#!/usr/bin/env python3
"""Shared extraction/normalization helpers for the Phase 9 validators.

Used by ``validate_docx.py``, ``validate_cross_format_parity.py`` and
``validate_evidence_bindings.py``.  Read-only over the frozen canonical
sources -- nothing here writes into papers/ content.

Services
--------
* canonical .tex flattening (``\\input``/``\\include`` inlining) + comment
  stripping, WITHOUT touching the sources (pure string transforms);
* DOCX package reading + text extraction (``w:t`` + ``m:t`` in document
  order, per-paragraph structures, styles, tables, fields);
* PDF text extraction (PyMuPDF) with the submission-layout normalization
  (ligatures, margin line numbers, hyphenation, unicode minus);
* text normalization channels used by the parity/binding checks.
"""
from __future__ import annotations

import re
import zipfile
from pathlib import Path

from lxml import etree

PAPERS = Path(__file__).resolve().parent.parent      # .../papers
REPO = PAPERS.parent

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
M = "{http://schemas.openxmlformats.org/officeDocument/2006/math}"
WP = "{http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing}"
R = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"
B = "{http://schemas.openxmlformats.org/officeDocument/2006/bibliography}"
CT = "{http://schemas.openxmlformats.org/package/2006/content-types}"
REL = "{http://schemas.openxmlformats.org/package/2006/relationships}"

DOC_PAIRS = {
    "main": {
        "pdf": PAPERS / "DT-GSK.pdf",
        "docx": PAPERS / "DT-GSK.docx",
        "tex": PAPERS / "main.tex",
        "aux": PAPERS / "main.aux",
        "bbl": PAPERS / "main.bbl",
    },
    "supplementary": {
        "pdf": PAPERS / "supplementary.pdf",
        "docx": PAPERS / "supplementary.docx",
        "tex": PAPERS / "supplementary.tex",
        "aux": PAPERS / "supplementary.aux",
        "bbl": PAPERS / "supplementary.bbl",
    },
}

LIGATURES = {
    "ﬀ": "ff", "ﬁ": "fi", "ﬂ": "fl",
    "ﬃ": "ffi", "ﬄ": "ffl", "ﬅ": "st", "ﬆ": "st",
}

# Word display strings vs frozen CSV identifiers (build-time glossary)
TERMINOLOGY = [("FDBAGSK", "FDB-AGSK"), ("EGSK", "eGSK")]


# ===========================================================================
# canonical .tex access
# ===========================================================================

_INPUT_RE = re.compile(r"\\(?:input|include)\{([^}]+)\}")


def flatten_tex(path: Path, *, include_tables: bool = True,
                seen: set | None = None) -> str:
    """Inline every ``\\input``/``\\include`` (relative to papers/)."""
    seen = seen if seen is not None else set()
    txt = path.read_text(encoding="utf-8")
    out, pos = [], 0
    for m in _INPUT_RE.finditer(txt):
        out.append(txt[pos:m.start()])
        rel = m.group(1).strip().replace("\\", "/")
        if not include_tables and rel.startswith("tables/"):
            out.append(m.group(0))
            pos = m.end()
            continue
        p = PAPERS / rel
        if p.suffix.lower() != ".tex":
            p = p.with_suffix(".tex")
        key = str(p.resolve())
        if p.is_file() and key not in seen:
            seen.add(key)
            out.append(flatten_tex(p, include_tables=include_tables, seen=seen))
        pos = m.end()
    out.append(txt[pos:])
    return "".join(out)


_COMMENT_RE = re.compile(r"(?<!\\)%.*")


def strip_tex_comments(text: str) -> str:
    return _COMMENT_RE.sub("", text)


def tex_document_body(text: str) -> str:
    m = re.search(r"\\begin\{document\}(.*)\\end\{document\}", text, re.DOTALL)
    return m.group(1) if m else text


def find_balanced_close(text: str, open_idx: int) -> int:
    assert text[open_idx] == "{"
    depth, i, n = 0, open_idx, len(text)
    while i < n:
        c = text[i]
        if c == "\\" and i + 1 < n:
            i += 2
            continue
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return i
        i += 1
    raise ValueError("unbalanced braces at %d" % open_idx)


def parse_aux_labels(aux_path: Path) -> dict[str, str]:
    labels: dict[str, str] = {}
    txt = aux_path.read_text(encoding="utf-8", errors="replace")
    for m in re.finditer(r"\\newlabel\{([^}]+)\}\{\{([^{}]*)\}", txt):
        labels[m.group(1)] = m.group(2)
    return labels


def parse_aux_bibcites(aux_path: Path) -> dict[str, int]:
    cites: dict[str, int] = {}
    txt = aux_path.read_text(encoding="utf-8", errors="replace")
    for m in re.finditer(r"\\bibcite\{([^}]+)\}\{\{(\d+)\}", txt):
        cites[m.group(1)] = int(m.group(2))
    return cites


# ===========================================================================
# DOCX access
# ===========================================================================

def read_docx_parts(path: Path) -> dict[str, bytes]:
    with zipfile.ZipFile(path) as zf:
        return {i.filename: zf.read(i.filename) for i in zf.infolist()}


def docx_document(path_or_parts) -> etree._Element:
    if isinstance(path_or_parts, dict):
        data = path_or_parts["word/document.xml"]
    else:
        data = read_docx_parts(path_or_parts)["word/document.xml"]
    return etree.fromstring(data)


def para_style(p) -> str:
    ppr = p.find(W + "pPr")
    if ppr is None:
        return ""
    st = ppr.find(W + "pStyle")
    return (st.get(W + "val") or "") if st is not None else ""


def para_text(p, *, include_math: bool = True,
              include_instr: bool = False) -> str:
    """Visible text of a paragraph: ``w:t`` (+ ``m:t``), skipping field
    instruction text unless requested."""
    tags = {W + "t"}
    if include_math:
        tags.add(M + "t")
    if include_instr:
        tags.add(W + "instrText")
    out = []
    for el_ in p.iter():
        if el_.tag in tags and el_.text:
            out.append(el_.text)
    return "".join(out)


def iter_body_blocks(doc: etree._Element):
    """Yield ('p', element) / ('tbl', element) for direct + nested body flow
    in document order (paragraphs inside tables are NOT yielded again)."""
    body = doc.find(W + "body")
    for child in body:
        if child.tag == W + "p":
            yield "p", child
        elif child.tag == W + "tbl":
            yield "tbl", child


def table_cells(tbl) -> list[list[str]]:
    rows = []
    for tr in tbl.findall(W + "tr"):
        rows.append([para_text(tc) for tc in tr.findall(W + "tc")])
    return rows


def docx_full_text(doc: etree._Element) -> str:
    """All visible text (w:t + m:t) in document order, paragraphs separated
    by newlines.  Field instruction text is excluded (not rendered)."""
    parts = []
    for p in doc.iter(W + "p"):
        parts.append(para_text(p))
    return "\n".join(parts)


def docx_fields(doc: etree._Element) -> list[dict[str, str]]:
    """Complex fields in document order: instruction + cached result text."""
    fields = []
    stack: list[dict] = []
    for el_ in doc.iter():
        if el_.tag == W + "fldChar":
            t = el_.get(W + "fldCharType")
            if t == "begin":
                stack.append({"instr": "", "cached": "", "in_result": False})
            elif t == "separate" and stack:
                stack[-1]["in_result"] = True
            elif t == "end" and stack:
                f = stack.pop()
                instr = " ".join(f["instr"].split())
                kind = instr.split(" ", 1)[0] if instr else "?"
                fields.append({"type": kind, "instr": instr,
                               "cached": f["cached"]})
        elif el_.tag == W + "instrText" and stack and not stack[-1]["in_result"]:
            stack[-1]["instr"] += el_.text or ""
        elif el_.tag in (W + "t", M + "t") and stack and stack[-1]["in_result"]:
            stack[-1]["cached"] += el_.text or ""
    return fields


# ===========================================================================
# PDF access
# ===========================================================================

def pdf_raw_text(path: Path) -> str:
    import fitz
    doc = fitz.open(str(path))
    try:
        return "".join(page.get_text() for page in doc)
    finally:
        doc.close()


def pdf_outline(path: Path) -> list[tuple[int, str]]:
    import fitz
    doc = fitz.open(str(path))
    try:
        return [(lvl, title) for lvl, title, _pg in doc.get_toc()]
    finally:
        doc.close()


def normalize_pdf_text(text: str) -> str:
    """Submission-layout normalization: ligatures, margin line numbers,
    end-of-line hyphenation, unicode minus/dashes."""
    for k, v in LIGATURES.items():
        text = text.replace(k, v)
    # margin line numbers / bare page numbers are emitted as digit-only lines
    text = re.sub(r"(?m)^\d+\s*$", "", text)
    # MDPI submission running header/footer ("Version <date> submitted to
    # <journal>" / "<n> of <N>" / first-page footer) interleave at breaks
    text = re.sub(r"(?m)^Version .{0,60}submitted to[^\n]*$", "", text)
    text = re.sub(r"(?m)^\d+ of \d+\s*$", "", text)
    text = re.sub(r"(?m)^Submitted to [^\n]*$", "", text)
    text = re.sub(r"(?m)^www\.mdpi\.com[^\n]*$", "", text)
    # "pages 1 - 53" is the same running-footer class as "<n> of <N>"; it lands
    # mid-sentence at a page break and otherwise splits the paragraph window.
    text = re.sub(r"(?m)^pages \d+\s*[-–]\s*\d+\s*$", "", text)
    # rejoin hyphenated line breaks (LaTeX justification)
    text = re.sub(r"-\n(?=[a-z])", "", text)
    text = text.replace("−", "-").replace("–", "-")
    text = text.replace("—", "-").replace("­", "")
    return text


# ===========================================================================
# comparison channels
# ===========================================================================

_ALNUM_RE = re.compile(r"[0-9A-Za-z]+")


def alnum_channel(text: str) -> str:
    """ASCII-alphanumeric channel: robust to spacing, hyphenation, math
    glyph differences, punctuation and dash conventions."""
    for k, v in LIGATURES.items():
        text = text.replace(k, v)
    return "".join(_ALNUM_RE.findall(text))


def number_channel(text: str) -> str:
    """Channel for numeric-token searches: ligature+minus normalized,
    whitespace collapsed to single spaces."""
    for k, v in LIGATURES.items():
        text = text.replace(k, v)
    text = text.replace("−", "-").replace("–", "-")
    text = text.replace("—", "-")
    text = text.replace("×", "x")      # multiplication sign
    return " ".join(text.split())


def squash(text: str) -> str:
    """No-whitespace channel (for adjacency searches like 4.2x10-2)."""
    return re.sub(r"\s+", "", number_channel(text))


# ===========================================================================
# LaTeX -> text for cell/caption comparison
# ===========================================================================

_MACRO_MAP = {
    "\\dtgsk": "DT-GSK", "\\sgsm": "SGSM", "\\atmals": "ATMALS-GSK",
    "\\agsk": "AGSK", "\\apgsk": "APGSK", "\\fdbagsk": "FDB-AGSK",
    "\\egsk": "eGSK", "\\wmark": "+", "\\lmark": "-", "\\emark": "≈",
    "\\pm": "±", "\\approx": "≈", "\\times": "x",
    "\\%": "%", "\\&": "&", "\\_": "_", "\\#": "#",
    "\\dots": "...", "\\ldots": "...",
    # Named math operators render as their own literal text in BOTH formats
    # ("log_10 error"). Dropping them as unknown commands left detex with the
    # bare subscript ("10 error"), which no rendering ever shows.
    #
    # Deliberately limited to operators that appear in operator position.
    # \min/\max/\arg are NOT included: in this manuscript they occur as
    # subscripts inside symbol names (\pi_{\min}), where mapping them to
    # literal text changes the token grouping and breaks the notation table.
    "\\log": "log", "\\ln": "ln", "\\exp": "exp",
}


def detex(s: str) -> str:
    """Best-effort LaTeX -> plain text for table cells / captions.
    Content-preserving for prose + numbers; math commands reduced to their
    argument text; unknown commands dropped."""
    s = s.replace("~", " ")
    for k, v in _MACRO_MAP.items():
        s = s.replace(k + "{}", v).replace(k, v)
    # \multicolumn{n}{a}{X} -> X   \multirow{n}{a}{X} -> X
    for cmd in ("multicolumn", "multirow"):
        pat = re.compile(r"\\" + cmd + r"\{[^}]*\}\{[^}]*\}\{")
        while True:
            m = pat.search(s)
            if not m:
                break
            close = find_balanced_close(s, m.end() - 1)
            s = s[:m.start()] + s[m.end():close] + s[close + 1:]
    # argument-transparent wrappers
    for cmd in ("textbf", "textit", "texttt", "textsc", "emph", "mbox",
                "bestval", "text", "mathrm", "mathbf", "mathit", "textrm",
                "operatorname", "underline", "footnotesize", "small"):
        pat = re.compile(r"\\" + cmd + r"\s*\{")
        while True:
            m = pat.search(s)
            if not m:
                break
            close = find_balanced_close(s, m.end() - 1)
            s = s[:m.start()] + s[m.end():close] + s[close + 1:]
    s = re.sub(r"\$([^$]*)\$", r"\1", s)           # inline math -> content
    s = re.sub(r"\^\{([^}]*)\}", r"\1", s)         # sup/sub braces
    s = re.sub(r"_\{([^}]*)\}", r"\1", s)
    # operator names render as words in both formats (surrounding spaces
    # keep them from gluing onto a preceding \command name)
    s = re.sub(r"\\(exp|min|max|log|ln|arg|round|bmod|mod|sign|floor|ceil)"
               r"\b", r" \1 ", s)
    s = re.sub(r"\\[a-zA-Z]+\*?", " ", s)          # leftover commands
    # (do NOT consume a following [..] group: it is usually set notation
    # like "\in [0,1]", not an optional argument)
    s = s.replace("{", "").replace("}", "")
    s = s.replace("--", "-")
    return " ".join(s.split())


def parse_tabular_rows(inner: str) -> list[list[str]]:
    """Split a tabular/longtable body into rows of raw-LaTeX cells.

    ``inner`` is everything between ``\\begin{tabular}`` and
    ``\\end{tabular}`` and therefore STARTS with the optional ``[pos]`` and
    the mandatory ``{colspec}`` arguments -- both are stripped first.
    """
    i = 0
    while i < len(inner) and inner[i].isspace():
        i += 1
    if i < len(inner) and inner[i] == "[":
        close = inner.find("]", i)
        if close > 0:
            i = close + 1
    while i < len(inner) and inner[i].isspace():
        i += 1
    if i < len(inner) and inner[i] == "{":
        i = find_balanced_close(inner, i) + 1
    inner = inner[i:]
    inner = re.sub(r"\\(?:top|mid|bottom)rule", "", inner)
    inner = re.sub(r"\\cmidrule(?:\([^)]*\))?\{[^}]*\}", "", inner)
    inner = re.sub(r"\\hline", "", inner)
    rows = []
    for raw in inner.split("\\\\"):
        if not raw.strip():
            continue
        cells = [c.strip() for c in _split_cells(raw)]
        if any(c for c in cells):
            rows.append(cells)
    return rows


def _split_cells(row: str) -> list[str]:
    """Split on & except escaped \\&."""
    out, cur, i = [], [], 0
    while i < len(row):
        c = row[i]
        if c == "\\" and i + 1 < len(row):
            cur.append(row[i:i + 2])
            i += 2
            continue
        if c == "&":
            out.append("".join(cur))
            cur = []
        else:
            cur.append(c)
        i += 1
    out.append("".join(cur))
    return out


def extract_env_spans(text: str, env: str) -> list[tuple[int, int, str]]:
    spans = []
    begin, end = "\\begin{%s}" % env, "\\end{%s}" % env
    i = 0
    while True:
        s = text.find(begin, i)
        if s < 0:
            break
        e = text.find(end, s)
        if e < 0:
            break
        spans.append((s, e + len(end), text[s + len(begin):e]))
        i = e + len(end)
    return spans


def apply_terminology(s: str) -> str:
    for old, new in TERMINOLOGY:
        s = s.replace(old, new)
    return s
