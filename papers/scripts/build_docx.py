#!/usr/bin/env python3
"""Build the Microsoft Word companions of the DT-GSK paper (Phase 9).

Two documents are produced from the FROZEN Phase-8 LaTeX sources (which are
never modified):

    python papers/scripts/build_docx.py                 -> papers/DT-GSK.docx
    python papers/scripts/build_docx.py --supplementary -> papers/supplementary.docx

Pipeline (per document)
-----------------------
1.  A pandoc-friendly *shim* copy of the canonical .tex is materialised
    (``main_pandoc.tex`` / ``supplementary_pandoc.tex``): MDPI front matter is
    re-expressed for a plain ``article`` preamble, ``\\input`` files are
    inlined, and constructs pandoc cannot model (algorithm floats, generated
    data tables, ``\\cite``/``\\ref``, the bibliography) are replaced by
    inert text **markers** that survive conversion.
2.  pandoc 3.9 converts the shim to DOCX with ``--reference-doc
    word/reference.docx`` (all math -> native OMML; no citeproc).
3.  An OOXML post-processing stage (zipfile + lxml) rewrites the package:
    * caption markers  -> editable captions with native ``SEQ`` fields
      (Figure/Table/Algorithm/Equation) + stable bookmarks,
    * ``@@REF!..@@``   -> ``REF`` fields with cached PDF-identical numbers
      (numbers parsed from the frozen ``main.aux``/``supplementary.aux``),
    * ``@@CITE!..@@``  -> native ``CITATION`` fields (cached ``[n]`` text
      matching the MDPI numbering from the frozen ``.bbl``) backed by a
      customXml ``b:Sources`` bibliography store built from
      ``papers/references.bib`` filtered to cited keys,
    * ``@@NATIVETABLE!Txx@@`` -> native ``w:tbl`` built from the semantic
      sources ``papers/tables/word_sources/*.json`` (exact values/precision;
      terminology notes applied: EGSK->eGSK, FDBAGSK->FDB-AGSK; header row
      carries the ``w:tblHeader`` accessibility property),
    * ``tab:bca-ci`` cross-format reconciliation: the DOCX table renders the
      SAME rank-CI content as the frozen ``papers/tables/T16_bca.tex`` (the
      per-function BCa companion in ``T16_bca.json`` stays supplement-only
      data and is NOT typeset -- matching the PDF),
    * no table of contents (the MDPI article PDF renders none, so the DOCX
      omits it too; ``w:updateFields`` is forced false so the DOCX opens
      self-contained on any machine with no update-on-open prompt),
    * alt text (``wp:docPr/@descr``) on every image from its registry-derived
      caption,
    * SOURCE_DATE_EPOCH docProps + zip normalization for determinism.
4.  Every SEQ/REF/CITATION/TOC field is appended to
    ``word/field_registry.csv``.

The canonical LaTeX sources remain untouched; the shim files are overwritten
on every run.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import re
import shutil
import subprocess
import sys
import uuid
from pathlib import Path

from lxml import etree

SCRIPTS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS_DIR))

from _word_ooxml import (  # noqa: E402
    NSMAP,
    make_bookmark_pair,
    make_field_runs,
    make_fldchar_run,
    make_run,
    make_tab_run,
    parse_xml,
    qn,
    read_zip_parts,
    sanitize_bookmark_name,
    serialize_xml,
    stamp_core_props,
    write_deterministic_zip,
)

ROOT = Path(__file__).resolve().parent.parent          # .../papers/
REPO_ROOT = ROOT.parent
WORD_DIR = REPO_ROOT / "word"
FIGURES_DIR = ROOT / "figures"
WORD_SOURCES = ROOT / "tables" / "word_sources"
GOVERNANCE = ROOT / "governance"

GS_DPI = 220

# Phase-4 frozen glossary applied to Word display strings (word_sources notes)
TERMINOLOGY = [("FDBAGSK", "FDB-AGSK"), ("EGSK", "eGSK")]

# CR-0005 / decision D-0009 (2026-07-10) un-blocked awad2016problem; the
# word_citation_tag_map.csv admissibility row predates that change request and
# is stale.  Recorded as a build deviation in the Phase 9 word build report.
CITATION_BLOCK_OVERRIDES = {"awad2016problem": "CR-0005/D-0009 approved"}

DOC_SPECS = {
    "main": {
        "tex": ROOT / "main.tex",
        "shim": ROOT / "main_pandoc.tex",
        "out": ROOT / "DT-GSK.docx",
        "aux": ROOT / "main.aux",
        "bbl": ROOT / "main.bbl",
        "table_prefix": "",     # SEQ Table cached values are plain integers
        "figure_prefix": "",
        "title": "DT-GSK: Dimension-Tiered Adaptive Control and Deterministic Refinement "
                 "for Gaining-Sharing Knowledge Optimization",
        "authors": "Mostafa Elsayed Masoud; Heba Sayed Mohamed Roshdy; "
                   "Ali Wagdy Mohamed",
        "subject": "Dimension-tiered adaptive control and deterministic refinement for "
                   "Gaining-Sharing Knowledge (DT-GSK) optimization",
        "keywords": "metaheuristic optimization; gaining-sharing knowledge; "
                    "dimension-tiered adaptive control; deterministic final refinement; adaptive operator selection; interaction-structure memory; "
                    "population-size reduction; "
                    "CEC benchmark suites; nonparametric statistical comparison; "
                    "reproducibility",
    },
    "supplementary": {
        "tex": ROOT / "supplementary.tex",
        "shim": ROOT / "supplementary_pandoc.tex",
        "out": ROOT / "supplementary.docx",
        "aux": ROOT / "supplementary.aux",
        "bbl": ROOT / "supplementary.bbl",
        "table_prefix": "A",    # supplement exhibits: Tables A1.., Figures B1..
        "figure_prefix": "B",
        "title": "Supplementary Material for: DT-GSK: Dimension-Tiered Adaptive Control "
                 "and Deterministic Refinement for Gaining-Sharing Knowledge Optimization",
        "authors": "Mostafa Elsayed Masoud; Heba Sayed Mohamed Roshdy; "
                   "Ali Wagdy Mohamed",
        "subject": "Supplementary Material: dimension-tiered adaptive control and "
                   "deterministic refinement for Gaining-Sharing Knowledge (DT-GSK) optimization",
        "keywords": "metaheuristic optimization; gaining-sharing knowledge; "
                    "dimension-tiered adaptive control; deterministic final refinement; adaptive operator selection; interaction-structure memory; "
                    "population-size reduction; "
                    "CEC benchmark suites; nonparametric statistical comparison; "
                    "reproducibility",
    },
}

_PANDOC_USER_WIN = Path(
    os.environ.get("LOCALAPPDATA", r"C:\Users\moust\AppData\Local")
) / "Pandoc" / "pandoc.exe"
_GS_USER_WIN = Path(r"C:\Program Files\gs\gs10.06.0\bin\gswin64c.exe")

MARKER_RE = re.compile(r"@@([A-Z]+)((?:![^@!]+)*)@@")


def _marker(tag: str, *payloads: str) -> str:
    """Build an ``@@TAG!p1!p2@@`` marker, LaTeX-escaping underscores."""
    body = "".join("!" + p for p in payloads)
    return ("@@" + tag + body + "@@").replace("_", r"\_")


# ===========================================================================
# tool resolution
# ===========================================================================

def _resolve_pandoc() -> str:
    on_path = shutil.which("pandoc")
    if on_path:
        return on_path
    if _PANDOC_USER_WIN.is_file():
        return str(_PANDOC_USER_WIN)
    raise FileNotFoundError(
        "pandoc not found.  Install with:  "
        "winget install --id JohnMacFarlane.Pandoc --scope user")


def _resolve_ghostscript() -> str | None:
    for candidate in ("gswin64c", "gswin64c.exe", "gs"):
        p = shutil.which(candidate)
        if p:
            return p
    if _GS_USER_WIN.is_file():
        return str(_GS_USER_WIN)
    return None


# ===========================================================================
# generic LaTeX utilities
# ===========================================================================

def _find_balanced_close(text: str, open_idx: int) -> int:
    assert text[open_idx] == "{"
    depth = 0
    i = open_idx
    n = len(text)
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
    raise ValueError(f"unbalanced braces starting at index {open_idx}")


def _extract_block(text: str, command: str) -> tuple[str | None, int, int]:
    pattern = re.compile(r"\\" + re.escape(command) + r"\s*\{")
    m = pattern.search(text)
    if not m:
        return None, -1, -1
    open_idx = m.end() - 1
    close_idx = _find_balanced_close(text, open_idx)
    return text[open_idx + 1:close_idx], m.start(), close_idx + 1


def _extract_all_envs(text: str, env: str) -> list[tuple[int, int, str]]:
    """Return (start, end, inner) spans of every ``\\begin{env}..\\end{env}``."""
    spans = []
    begin = "\\begin{%s}" % env
    end = "\\end{%s}" % env
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


def _strip_trailing_pct(s: str) -> str:
    out = []
    for line in s.splitlines():
        stripped = line.rstrip()
        if stripped.endswith("%") and not stripped.endswith("\\%"):
            stripped = stripped[:-1]
        out.append(stripped)
    return "\n".join(out).strip()


def _tidy_author(author_raw: str) -> str:
    s = _strip_trailing_pct(author_raw)
    # Keep the affiliation superscripts (the old re.sub stripped them, so a
    # DOCX reader could not map the three authors to the three numbered
    # affiliations -- R3-11). A trailing correspondence star is folded INTO
    # the math ("$^{1,}$*" -> "$^{1,*}$") so pandoc round-trips one clean
    # superscript run per author.
    s = re.sub(r"\$\^\{([^}]*?),?\}\$\s*\*", r"$^{\1,*}$", s)
    # Keep "A, B and C" as ONE author string. Emitting LaTeX \and here makes
    # pandoc treat the names as separate author entries and render them on
    # separate lines, unlike the PDF's single author line (FM-01).
    return s.strip()


def _flatten_inputs(text: str, seen: set[Path] | None = None) -> str:
    """Inline ``\\input``/``\\include`` except the generated ``tables/`` files
    (those are replaced by native-table markers later)."""
    if seen is None:
        seen = set()
    pattern = re.compile(r"\\(?:input|include)\{([^}]+)\}")

    def _sub(m: re.Match[str]) -> str:
        rel = m.group(1).strip()
        if rel.replace("\\", "/").startswith("tables/"):
            return m.group(0)
        candidate = ROOT / rel
        if candidate.suffix.lower() != ".tex":
            candidate = candidate.with_suffix(".tex")
        candidate = candidate.resolve()
        if not candidate.is_file():
            return f"% [build_docx] missing input: {rel}\n"
        if candidate in seen:
            return f"% [build_docx] cyclic input skipped: {rel}\n"
        seen.add(candidate)
        try:
            nested = candidate.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            nested = candidate.read_text(encoding="latin-1")
        return ("\n% >>>> " + rel + " <<<<\n" + _flatten_inputs(nested, seen)
                + "\n% <<<< end " + rel + " >>>>\n")

    return pattern.sub(_sub, text)


# ===========================================================================
# figure rasterisation
# ===========================================================================

def _pdf_to_png(pdf_path: Path, gs_exe: str) -> Path | None:
    png_path = pdf_path.with_suffix(".docx.png")
    if png_path.exists() and png_path.stat().st_mtime >= pdf_path.stat().st_mtime:
        return png_path
    cmd = [gs_exe, "-dNOPAUSE", "-dBATCH", "-dQUIET", "-sDEVICE=png16m",
           f"-r{GS_DPI}", "-dUseTrimBox", f"-sOutputFile={png_path}",
           str(pdf_path)]
    result = subprocess.run(cmd, capture_output=True)
    if result.returncode != 0:
        print(f"  ! Ghostscript failed on {pdf_path.name}", file=sys.stderr)
        return None
    return png_path


def _rasterise_figures(body: str) -> str:
    """Rewrite every ``\\includegraphics`` to a Word-renderable PNG.

    Resolution order per graphic stem: sibling ``.png`` written by the figure
    generator, else Ghostscript raster of the ``.pdf``.  Word-hostile size
    options (``height=..\\textheight``, ``keepaspectratio``) are dropped;
    ``width=`` fractions are kept for pandoc.
    """
    gs = _resolve_ghostscript()
    pattern = re.compile(r"\\includegraphics(\[[^\]]*\])?\{([^}]+)\}")

    def _resolve(stem: str) -> str | None:
        rel = stem[:-4] if stem.lower().endswith(".pdf") else stem
        png = ROOT / (rel + ".png")
        if png.is_file():
            return rel + ".png"
        pdf = ROOT / (rel + ".pdf")
        if pdf.is_file() and gs:
            out = _pdf_to_png(pdf.resolve(), gs)
            if out is not None:
                return str(out.relative_to(ROOT)).replace("\\", "/")
        return None

    n = 0

    def _sub(m: re.Match[str]) -> str:
        nonlocal n
        opts, stem = m.group(1) or "", m.group(2)
        target = _resolve(stem)
        if target is None:
            return m.group(0)
        n += 1
        keep = []
        for opt in opts.strip("[]").split(","):
            opt = opt.strip()
            if opt.startswith("width="):
                keep.append(opt)
        optstr = ("[" + ",".join(keep) + "]") if keep else ""
        return f"\\includegraphics{optstr}{{{target}}}"

    out = pattern.sub(_sub, body)
    if n:
        print(f"  Resolved {n} figures to PNG for Word")
    return out


# ===========================================================================
# shim transformations
# ===========================================================================

_PHASE8_GROUP_LINE = re.compile(
    r"^\s*(\\begingroup\s*$"
    r"|\\endgroup\s*$"
    r"|\\let\\phviii"
    r"|\\newsavebox\{\\phviii"
    r"|\\renewenvironment\{(?:table|tabular)\}"
    r"|\{\\begin\{lrbox\}"
    r"|\{\\phviii)")


def strip_phase8_groups(body: str) -> str:
    """Remove the Phase-8 presentation-group hack lines (lrbox/[H] wrappers)
    around the frozen notation/parameter table inputs; content is unchanged."""
    out = []
    for line in body.splitlines():
        if _PHASE8_GROUP_LINE.match(line):
            continue
        out.append(line)
    return "\n".join(out)


_COMMENT_RE = re.compile(r"(?<!\\)%.*$", re.MULTILINE)


def strip_comments(body: str) -> str:
    """Drop LaTeX comment text so no later regex pass can be fooled by
    commented-out markup (e.g. ``% ... \\resizebox ...`` build notes).

    pandoc drops comments anyway; this only protects the shim transforms.
    """
    return _COMMENT_RE.sub("", body)


def strip_misc_lines(body: str) -> str:
    out = []
    skip = re.compile(
        r"^\s*(\\renewcommand\{\\the(section|subsection|table|figure)\}"
        r"|\\setcounter\{section\}"
        r"|\\tablesize\{[^}]*\}"
        r"|\\centering\s*$"
        r"|\\reftitle\{[^}]*\}"
        r"|\\externalbibliography\{[^}]*\})")
    for line in body.splitlines():
        if skip.match(line):
            continue
        out.append(line)
    return "\n".join(out)


def strip_resizebox(body: str) -> str:
    """Unwrap ``\\resizebox{..}{..}{CONTENT}`` (balanced, any nesting)."""
    out = []
    i = 0
    while True:
        j = body.find("\\resizebox", i)
        if j < 0:
            out.append(body[i:])
            break
        out.append(body[i:j])
        k = body.find("{", j)
        k2 = _find_balanced_close(body, k)          # width arg
        k3 = body.find("{", k2 + 1)
        k4 = _find_balanced_close(body, k3)         # height arg
        k5 = body.find("{", k4 + 1)
        k6 = _find_balanced_close(body, k5)         # content
        out.append(body[k5 + 1:k6])
        i = k6 + 1
    return "".join(out)


_TTABLE_INPUT = re.compile(r"\\input\{tables/(T\d+(?:_bca)?|SA\d+)\}")


def _normalize_table_id(tex_id: str) -> str:
    """``tables/T01.tex`` binds to ``word_sources/T1.json`` (leading zeros)."""
    m = re.match(r"T0*(\d+)(_bca)?$", tex_id)
    if not m:
        return tex_id
    return "T" + m.group(1) + (m.group(2) or "")


def replace_generated_table_envs(body: str) -> str:
    """``table`` envs whose payload is a generated ``tables/Txx.tex`` become
    caption-marker + native-table-marker paragraphs (pandoc never sees the
    tabulars; post-processing builds native w:tbl from the semantic JSON)."""
    spans = _extract_all_envs(body, "table")
    if not spans:
        return body
    pieces = []
    last = 0
    for start, end, _inner in spans:
        seg = body[start:end]
        m = _TTABLE_INPUT.search(seg)
        if not m:
            continue
        table_id = _normalize_table_id(m.group(1))
        cap, _cs, _ce = _extract_block(seg, "caption")
        lab = re.search(r"\\label\{([^}]+)\}", seg)
        label = lab.group(1) if lab else "-"
        cap_text = _strip_trailing_pct(cap or "")
        replacement = (
            "\n\n" + _marker("TABLECAP", label, table_id) + " " + cap_text +
            "\n\n" + _marker("NATIVETABLE", table_id) + "\n\n")
        pieces.append(body[last:start])
        pieces.append(replacement)
        last = end
    pieces.append(body[last:])
    return "".join(pieces)


def convert_algorithm_envs(body: str) -> str:
    """Convert ``algorithm``+``algorithmic`` floats into caption-marker +
    numbered pseudocode-line paragraphs (inline math preserved -> OMML)."""
    spans = _extract_all_envs(body, "algorithm")
    if not spans:
        return body
    out = []
    last = 0
    for start, end, inner in spans:
        cap, _cs, _ce = _extract_block(inner, "caption")
        lab = re.search(r"\\label\{([^}]+)\}", inner)
        label = lab.group(1) if lab else "-"
        algm = re.search(r"\\begin\{algorithmic\}(?:\[\d+\])?(.*?)"
                         r"\\end\{algorithmic\}", inner, re.DOTALL)
        code = algm.group(1) if algm else ""
        lines = _algorithmic_to_lines(code)
        block = ["\n\n" + _marker("ALGCAP", label) + " " +
                 _strip_trailing_pct(cap or "") + "\n"]
        for num, indent, text in lines:
            block.append("\n" + _marker("ALGLINE",
                         str(num) if num is not None else "-", str(indent)) +
                         " " + text + "\n")
        block.append("\n")
        out.append(body[last:start])
        out.append("".join(block))
        last = end
    out.append(body[last:])
    return "".join(out)


def _replace_comments(stmt: str) -> str:
    """``\\Comment{X}`` -> trailing ``triangleright X`` note (balanced)."""
    out = []
    i = 0
    while True:
        j = stmt.find("\\Comment", i)
        if j < 0:
            out.append(stmt[i:])
            break
        out.append(stmt[i:j])
        k = stmt.find("{", j)
        k2 = _find_balanced_close(stmt, k)
        out.append("\\ \\ $\\triangleright$~" + stmt[k + 1:k2])
        i = k2 + 1
    return "".join(out)


def _expand_braced(s: str, macro: str, fn) -> str:
    """Replace every ``macro{...}`` (balanced braces) with ``fn(inner)``."""
    out = []
    i = 0
    needle = macro + "{"
    while True:
        j = s.find(needle, i)
        if j < 0:
            out.append(s[i:])
            break
        out.append(s[i:j])
        k = j + len(macro)          # index of the opening brace
        k2 = _find_balanced_close(s, k)
        out.append(fn(s[k + 1:k2]))
        i = k2 + 1
    return "".join(out)


def _algorithmic_to_lines(code: str) -> list[tuple[object, int, str]]:
    """Tokenize an ``algorithmic`` body into ``(number|None, indent, latex)``
    lines.  ``\\Require``/``\\Ensure``/``\\Statex`` render unnumbered (mirroring
    the PDF); the pseudocode float's rendering helpers ``\\cont``/``\\tier`` and
    the right-aligned ``\\hfill`` notes are expanded so no raw macro leaks into
    Word."""
    code = re.sub(r"(?m)^\s*%.*$", "", code)
    # expand the float-local rendering helpers into portable constructs
    code = _expand_braced(code, "\\cont", lambda x: " \\Statex " + x)
    code = _expand_braced(code, "\\tier", lambda d: "[$D\\ge " + d.strip() + "$] ")
    code = _expand_braced(code, "\\hfill", lambda x: "  " + x)   # note -> inline
    code = code.replace("\\footnotesize", "").replace("\\enspace", " ")
    # \Statex must precede \State in the alternation, else \State matches the
    # \Statex prefix and leaves a stray "x" numbered as a bogus statement.
    parts = re.split(
        r"(\\Statex|\\State|\\EndWhile|\\While|\\Return|\\Require|\\Ensure)", code)
    lines: list[tuple[object, int, str]] = []
    indent = 0
    num = 0
    i = 1
    while i < len(parts):
        tok = parts[i]
        rest = parts[i + 1] if i + 1 < len(parts) else ""
        rest = " ".join(rest.split()).strip()
        rest = _replace_comments(rest)
        if tok == "\\Require":
            lines.append((None, indent, "\\textbf{Require:}  " + rest))
        elif tok == "\\Ensure":
            lines.append((None, indent, "\\textbf{Ensure:}  " + rest))
        elif tok == "\\Statex":
            if rest:
                lines.append((None, indent + 1, rest))
        elif tok == "\\While":
            cond, rest_after = rest, ""
            if rest.startswith("{"):
                close = _find_balanced_close(rest, 0)
                cond = rest[1:close]
                rest_after = rest[close + 1:].strip()
            num += 1
            line = "\\textbf{while} " + cond + " \\textbf{do}"
            if rest_after:
                line += " " + rest_after
            lines.append((num, indent, line))
            indent += 1
        elif tok == "\\EndWhile":
            indent = max(0, indent - 1)
            num += 1
            line = "\\textbf{end while}"
            if rest:
                line += " " + rest
            lines.append((num, indent, line))
        elif tok == "\\Return":
            num += 1
            lines.append((num, indent, "\\textbf{return} " + rest))
        else:  # \State
            if not rest:
                i += 2
                continue
            extra = 0
            while rest.startswith("\\quad"):
                extra += 1
                rest = rest[len("\\quad"):].strip()
            num += 1
            lines.append((num, indent + extra, rest))
        i += 2
    return lines


def convert_equation_envs(body: str) -> str:
    pattern = re.compile(
        r"\\begin\{equation\}\s*(?:\\label\{([^}]+)\})?(.*?)\\end\{equation\}",
        re.DOTALL)

    def _sub(m: re.Match[str]) -> str:
        label = m.group(1) or "-"
        eq_body = m.group(2).strip()
        return ("\n\\[\n" + eq_body + "\n\\]\n\n" +
                _marker("EQNUM", label) + "\n")

    return pattern.sub(_sub, body)


def inject_caption_markers(body: str) -> str:
    """Prefix a FIGCAP/TABLECAP marker inside every remaining figure/table
    caption so post-processing can number it and bookmark it."""
    for env, tag in (("figure", "FIGCAP"), ("table", "TABLECAP")):
        spans = _extract_all_envs(body, env)
        rebuilt = []
        last = 0
        for start, end, _inner in spans:
            seg = body[start:end]
            lab = re.search(r"\\label\{([^}]+)\}", seg)
            label = lab.group(1) if lab else "-"
            m = re.search(r"(\\caption(?:\[[^\]]*\])?\{)", seg)
            if m:
                seg = (seg[:m.end()] + _marker(tag, label) + " " +
                       seg[m.end():])
            rebuilt.append(body[last:start])
            rebuilt.append(seg)
            last = end
        rebuilt.append(body[last:])
        body = "".join(rebuilt)
    return body


def number_section_headings(body: str, aux_labels: dict[str, str],
                            supplement: bool) -> str:
    """Insert SECNUM markers carrying the PDF-identical section numbers."""
    counters = [0, 0, 0]
    lines = body.splitlines()
    out = []
    pat = re.compile(r"^(\s*)\\(section|subsection|subsubsection)(\*?)\{")
    for idx, line in enumerate(lines):
        m = pat.match(line)
        if not m or m.group(3) == "*":
            out.append(line)
            continue
        level = {"section": 0, "subsection": 1, "subsubsection": 2}[m.group(2)]
        counters[level] += 1
        for deeper in range(level + 1, 3):
            counters[deeper] = 0
        num = ".".join(str(c) for c in counters[:level + 1])
        if supplement:
            num = "S" + num
        # prefer the frozen aux number when the heading is labelled
        lab = re.search(r"\\label\{([^}]+)\}", line)
        label = lab.group(1) if lab else "-"
        if label != "-" and label in aux_labels:
            num = aux_labels[label]
        # MDPI headings carry a terminal period after the number ("2.1.").
        disp = num if num.endswith(".") else num + "."
        insert_at = m.end()
        out.append(line[:insert_at] + _marker("SECNUM", label, disp) + " " +
                   line[insert_at:])
    return "\n".join(out)


def replace_refs(body: str) -> str:
    return re.sub(r"\\ref\{([^}]+)\}",
                  lambda m: _marker("REF", m.group(1)), body)


def replace_cites(body: str) -> str:
    def _sub(m: re.Match[str]) -> str:
        keys = [k.strip() for k in m.group(1).split(",") if k.strip()]
        return _marker("CITE", ",".join(keys))
    return re.sub(r"\\cite\{([^}]+)\}", _sub, body)


# ---------------------------------------------------------------------------
# bibliography (.bbl -> shim paragraphs)
# ---------------------------------------------------------------------------

def parse_bbl(bbl_path: Path) -> list[tuple[str, str]]:
    """Return ``[(key, entry-latex)]`` in .bbl (citation-number) order."""
    txt = bbl_path.read_text(encoding="utf-8", errors="replace")
    body_m = re.search(r"\\begin\{thebibliography\}.*?\n(.*)\\end\{thebibliography\}",
                       txt, re.DOTALL)
    if not body_m:
        return []
    body = body_m.group(1)
    entries = []
    for chunk in re.split(r"(?=\\bibitem)", body):
        chunk = chunk.strip()
        if not chunk.startswith("\\bibitem"):
            continue
        i = len("\\bibitem")
        if chunk[i] == "[":
            depth = 0
            while i < len(chunk):
                if chunk[i] == "[":
                    depth += 1
                elif chunk[i] == "]":
                    depth -= 1
                    if depth == 0:
                        i += 1
                        break
                elif chunk[i] == "{":       # brace group inside optional arg
                    i = _find_balanced_close(chunk, i)
                i += 1
        assert chunk[i] == "{", chunk[:80]
        close = _find_balanced_close(chunk, i)
        key = chunk[i + 1:close]
        entry = chunk[close + 1:].strip()
        entries.append((key, _clean_bbl_entry(entry)))
    return entries


def _clean_bbl_entry(entry: str) -> str:
    entry = re.sub(r"(?m)^\s*%.*$", "", entry)
    entry = entry.replace("\\newblock", " ")
    entry = re.sub(r"\\natexlab\{([^}]*)\}", r"\1", entry)
    entry = entry.replace("\\changeurlcolor{black}", "")
    entry = re.sub(r"\\detokenize\{([^}]*)\}", r"\1", entry)
    entry = re.sub(r"\{\\em\s+", r"\\emph{", entry)
    entry = re.sub(r"\{\\bf\s+", r"\\textbf{", entry)
    entry = re.sub(r"\\penalty\d+", "", entry)
    entry = re.sub(r"\s+", " ", entry).strip()
    return entry


def build_references_block(bbl_path: Path) -> str:
    entries = parse_bbl(bbl_path)
    parts = ["\n\\section*{References}\n"]
    for n, (key, latex) in enumerate(entries, start=1):
        parts.append("\n" + _marker("BIBENT", key, str(n)) + " " + latex + "\n")
    parts.append("\n")
    return "".join(parts)


def replace_bibliography(body: str, bbl_path: Path) -> str:
    # lambda replacement -> group escapes are NOT processed, keep verbatim
    return re.sub(r"\\bibliography\{references\}",
                  lambda m: build_references_block(bbl_path),
                  body, count=1)


# ---------------------------------------------------------------------------
# back matter (main document)
# ---------------------------------------------------------------------------

BACK_MATTER_MACROS = [
    ("supplementary", "Supplementary Materials"),
    ("authorcontributions", "Author Contributions"),
    ("funding", "Funding"),
    ("acknowledgments", "Acknowledgments"),
    ("conflictsofinterest", "Conflicts of Interest"),
    ("abbreviations", "Abbreviations"),
]


def expand_back_matter(body: str) -> str:
    for macro, heading in BACK_MATTER_MACROS:
        while True:
            content, s, e = _extract_block(body, macro)
            if content is None:
                break
            body = (body[:s] + "\n\\section*{" + heading + "}\n\n" +
                    _strip_trailing_pct(content) + "\n" + body[e:])
    return body


# ===========================================================================
# shim assembly
# ===========================================================================

HEADER = r"""\documentclass[10pt,a4paper]{article}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{amsmath}
\usepackage{amssymb}
\usepackage{bm}
\usepackage{graphicx}
\usepackage{booktabs}
\usepackage{longtable}
\usepackage{array}
\usepackage{hyperref}

% -------- custom macros (kept in sync with main.tex) --------
\newcommand{\dtgsk}{DT-GSK}
\newcommand{\sgsm}{SGSM}
\newcommand{\atmals}{ATMALS-GSK}
\newcommand{\agsk}{AGSK}
\newcommand{\apgsk}{APGSK}
\newcommand{\fdbagsk}{FDB-AGSK}
\newcommand{\egsk}{eGSK}
\newcommand{\bestval}[1]{\textbf{#1}}
\newcommand{\wmark}{\ensuremath{+}}
\newcommand{\lmark}{\ensuremath{-}}
\newcommand{\emark}{\ensuremath{\approx}}
\newcommand{\argmin}{\operatorname{arg\,min}}
\newcommand{\argmax}{\operatorname{arg\,max}}
\newcommand{\tablesize}[1]{}
\newcommand{\reftitle}[1]{}
\newcommand{\externalbibliography}[1]{}

"""

FOOTER = "\n\\end{document}\n"


def build_shim(doc_kind: str) -> str:
    spec = DOC_SPECS[doc_kind]
    src = spec["tex"].read_text(encoding="utf-8")
    supplement = doc_kind == "supplementary"

    title_raw, _, _ = _extract_block(src, "Title")
    author_raw, _, _ = _extract_block(src, "Author")
    abstract_raw, _, _ = _extract_block(src, "abstract")
    keyword_raw, _, _ = _extract_block(src, "keyword")
    address_raw, _, _ = _extract_block(src, "address")
    corres_raw, _, _ = _extract_block(src, "corres")

    title = _strip_trailing_pct(title_raw or "").replace("\n", " ")
    author = _tidy_author(author_raw or "")
    abstract = _strip_trailing_pct(abstract_raw or "")
    keyword = _strip_trailing_pct(keyword_raw or "")
    address = _strip_trailing_pct(address_raw or "")
    corres = _strip_trailing_pct(corres_raw or "")

    body_match = re.search(r"\\begin\{document\}(.*?)\\end\{document\}",
                           src, re.DOTALL)
    if not body_match:
        raise RuntimeError(f"no document body in {spec['tex'].name}")
    body = body_match.group(1).strip()

    aux_labels = parse_aux_labels(spec["aux"])

    body = _flatten_inputs(body)
    # Word has no page rotation; render sidewaystable (rotating pkg, PDF-only) as a
    # normal captioned table so pandoc emits its caption/label bookmark target.
    body = re.sub(r"\\begin\{sidewaystable\}(\[[^\]]*\])?", r"\\begin{table}[H]", body)
    body = body.replace(r"\end{sidewaystable}", r"\end{table}")
    body = strip_comments(body)
    body = strip_phase8_groups(body)
    body = strip_misc_lines(body)
    # Bold run-in labels: pandoc drops a \quad/\enspace that follows a bold
    # run, fusing e.g. "Data Availability Statement.The DT-GSK ..." in the
    # DOCX (R3-12). Convert to a plain interword space before conversion.
    body = re.sub(r"(\\textbf\{[^{}]*\})\\(?:quad|enspace)[ \t]*(?=\S)", r"\1 ", body)
    body = replace_generated_table_envs(body)
    body = convert_algorithm_envs(body)
    body = convert_equation_envs(body)
    body = inject_caption_markers(body)
    body = number_section_headings(body, aux_labels, supplement)
    if doc_kind == "main":
        body = expand_back_matter(body)
    body = replace_refs(body)
    body = replace_cites(body)
    body = replace_bibliography(body, spec["bbl"])
    body = strip_resizebox(body)
    body = _rasterise_figures(body)

    # Front matter. The PDF's title page is typeset by the MDPI class
    # (Definitions/mdpi.cls), which owns the "Article" type label, the logo, the
    # affiliation numbering and their order; this shim is plain `article`, so
    # that layout has to be approximated here.
    #   * \date{} is EMPTY on purpose -- deleting the line entirely would let
    #     LaTeX fall back to \today, which would make the DOCX non-reproducible.
    #     The PDF carries no date on the title page either.
    #   * The article-type label mirrors the PDF's "Article" line above the
    #     title (MDPI article type).
    parts = [HEADER,
             f"\\title{{{title}}}\n",
             f"\\author{{{author}}}\n",
             "\\date{}\n\n",
             "\\begin{document}\n",
             "\\noindent\\textit{Article}\n\n",
             "\\maketitle\n\n"]
    if address or corres:
        parts.append("\\begin{center}\\footnotesize\n")
        if address:
            parts.append(address + "\\\\\n")
        if corres:
            # Mirror the PDF's "* Correspondence:" marker so the DOCX ties
            # the starred author to the correspondence line (R3-11).
            parts.append("* " + corres + "\n")
        parts.append("\\end{center}\n\n")
    if abstract:
        parts.append("\\begin{abstract}\n" + abstract + "\n\\end{abstract}\n\n")
    if keyword:
        # A plain interword space: pandoc drops \enspace after a bold run,
        # which fused "Keywords:" to the first keyword in the DOCX (R3-12).
        parts.append("\\noindent\\textbf{Keywords:} " + keyword + "\n\n")
    parts.append(body.strip())
    parts.append(FOOTER)
    return "".join(parts)


# ===========================================================================
# frozen numbering + citation metadata
# ===========================================================================

def parse_aux_labels(aux_path: Path) -> dict[str, str]:
    labels: dict[str, str] = {}
    if not aux_path.is_file():
        print(f"  ! {aux_path.name} missing; cached numbers degrade",
              file=sys.stderr)
        return labels
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


def load_tag_map() -> dict[str, dict[str, str]]:
    path = GOVERNANCE / "word_citation_tag_map.csv"
    out: dict[str, dict[str, str]] = {}
    with open(path, encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            out[row["citation_key"]] = row
    return out


# ===========================================================================
# references.bib -> b:Sources store
# ===========================================================================

def parse_bibtex(path: Path) -> dict[str, dict[str, str]]:
    txt = path.read_text(encoding="utf-8", errors="replace")
    entries: dict[str, dict[str, str]] = {}
    for m in re.finditer(r"@(\w+)\s*\{\s*([^,\s]+)\s*,", txt):
        etype, key = m.group(1).lower(), m.group(2)
        start = m.end()
        depth = 1
        i = txt.find("{", m.start())
        i += 1
        while i < len(txt) and depth > 0:
            if txt[i] == "{":
                depth += 1
            elif txt[i] == "}":
                depth -= 1
            i += 1
        body = txt[start:i - 1]
        fields = {"__type__": etype}
        for fm in re.finditer(r"(\w+)\s*=\s*", body):
            name = fm.group(1).lower()
            j = fm.end()
            if j >= len(body):
                continue
            if body[j] == "{":
                k = _find_balanced_close(body, j)
                val = body[j + 1:k]
            elif body[j] == '"':
                k = body.find('"', j + 1)
                val = body[j + 1:k]
            else:
                k = body.find(",", j)
                if k < 0:
                    k = len(body)
                val = body[j:k]
            fields[name] = " ".join(val.split())
        entries[key] = fields
    return entries


def _delatex(s: str) -> str:
    s = re.sub(r"\\[a-zA-Z]+\{([^{}]*)\}", r"\1", s)
    s = s.replace("{", "").replace("}", "")
    s = s.replace("~", " ").replace("\\&", "&").replace("--", "-")
    s = s.replace("\\i", "i").replace('\\"', "").replace("\\'", "")
    s = s.replace("\\v", "").replace("\\c", "").replace("\\", "")
    return " ".join(s.split())


# Inline-math command names -> Unicode, for recovering authored-table cells that
# carry `$...$` fragments (e.g. $D{\ge}100$, $\lambda{=}0.95$, $\kappa_{\min}$).
# Keyed by the bare command name so tokenization is exact (\ge never matches the
# leading bytes of \gets).
_MATH_SYM_NAMES = {
    "geq": "≥", "ge": "≥", "leq": "≤", "le": "≤",
    "rightarrow": "→", "mapsto": "→", "to": "→", "gets": "←",
    "leftarrow": "←", "Rightarrow": "⇒", "neq": "≠",
    "times": "×", "cdot": "·", "pm": "±", "odot": "⊙",
    "approx": "≈", "infty": "∞", "ell": "ℓ", "propto": "∝",
    "nabla": "∇", "Delta": "Δ", "delta": "δ", "top": "⊤",
    "lambda": "λ", "kappa": "κ", "sigma": "σ", "Sigma": "Σ",
    "mu": "μ", "alpha": "α", "beta": "β", "omega": "ω",
    "rho": "ρ", "tau": "τ", "pi": "π", "sum": "∑",
    "theta": "θ", "gamma": "γ", "eta": "η", "zeta": "ζ",
    "phi": "φ", "varphi": "φ", "varepsilon": "ε", "epsilon": "ε",
    "bullet": "•", "circ": "∘", "star": "⋆", "oplus": "⊕", "otimes": "⊗",
    "leftrightarrow": "↔", "Leftrightarrow": "⇔", "langle": "⟨", "rangle": "⟩",
}
_STYLING_CMDS = frozenset((
    "textbf", "textit", "textrm", "textsc", "texttt", "emph", "mathrm",
    "mathbf", "mathit", "mathsf", "mathcal", "mathnormal", "operatorname",
    "text", "boldmath", "ensuremath", "mbox", "textnormal"))


def _cell_delatex(s: str, ref_resolver=None,
                  flatten_subscripts: bool = True) -> str:
    """LaTeX -> readable Unicode for a recovered authored-table cell, handling
    cross-references (\\ref/\\eqref), inline math ($...$), spacing braces
    ($D{<}20$), subscripts ($N_{\\min}$) and styling wrappers (\\textbf{...})."""

    def _ref(m):                                         # \ref{eq:x} -> number
        cmd, label = m.group(1), m.group(2)
        num = ref_resolver(label) if ref_resolver else "??"
        return f"({num})" if cmd == "eqref" else num
    s = re.sub(r"\\(ref|eqref|cref|Cref)\{([^{}]*)\}", _ref, s)
    s = re.sub(r"\\[,;:!>]", " ", s)                     # thin/med math spaces
    # Park an ESCAPED literal underscore (config keys such as no\_sgsm) behind
    # a sentinel, so the math-subscript flattening at the end cannot eat it.
    s = s.replace("\\_", "\x00")
    for a, b in (("\\%", "%"), ("\\&", "&"), ("\\#", "#"),
                 ("\\{", "{"), ("\\}", "}"), ("\\$", "$"), ("\\ ", " ")):
        s = s.replace(a, b)                              # escaped literals

    def _cmd(m):                                         # exact command tokenize
        name, sp = m.group(1), m.group(2)
        if name in _MATH_SYM_NAMES:
            return _MATH_SYM_NAMES[name]
        if name in _STYLING_CMDS:
            return ""                                    # drop styling, keep arg
        # pandoc glues a symbol command to the next word when it stringifies
        # math (\Delta + "rank" -> "\Deltarank"): peel the longest known symbol
        # prefix and KEEP the real space that followed it.
        for k in sorted(_MATH_SYM_NAMES, key=len, reverse=True):
            if len(name) > len(k) and name.startswith(k):
                return _MATH_SYM_NAMES[k] + name[len(k):] + sp
        return name                                      # \min -> min, etc.
    s = re.sub(r"\\([a-zA-Z]+)( ?)", _cmd, s)            # swallow one trailing sp
    s = s.replace("\\", "").replace("$", "")             # strip math delimiters
    s = s.replace("{", "").replace("}", "")
    # Every "_" still standing is a math subscript (the literals are parked in
    # the sentinel): flatten it the way the PDF typesets it -- G_{\mathrm{abs}}
    # -> Gabs, \kappa_{\min} -> κmin, G_\bullet -> G• -- then restore literals.
    # Callers whose input already had its escapes resolved (pandoc-mirrored
    # attribute text) pass flatten_subscripts=False, so a literal underscore in
    # a filename such as algorithm_freeze_manifest.json is never eaten.
    if flatten_subscripts:
        s = s.replace("_", "")
    s = s.replace("\x00", "_")
    s = s.replace("~", " ").replace("---", "—").replace("--", "–")
    return " ".join(s.split())


def build_sources_xml(cited_keys: list[str], bib: dict[str, dict[str, str]],
                      tag_map: dict[str, dict[str, str]]) -> bytes:
    B = NSMAP["b"]
    root = etree.Element("{%s}Sources" % B, nsmap={"b": B})
    root.set("SelectedStyle", "\\IEEE2006OfficeOnline.xsl")
    root.set("StyleName", "IEEE")
    for key in cited_keys:
        fields = bib.get(key)
        if fields is None:
            print(f"  ! bib entry missing for cited key {key}", file=sys.stderr)
            continue
        row = tag_map.get(key, {})
        admissible = row.get("admissible", "yes") == "yes" or \
            key in CITATION_BLOCK_OVERRIDES
        if not admissible:
            print(f"  ! citation source for {key} blocked by tag map; skipped",
                  file=sys.stderr)
            continue
        src = etree.SubElement(root, "{%s}Source" % B)

        def _add(tag: str, text: str):
            e = etree.SubElement(src, "{%s}%s" % (B, tag))
            e.text = text

        _add("Tag", row.get("word_tag", key))
        _add("SourceType", row.get("word_source_type") or {
            "article": "JournalArticle",
            "inproceedings": "ConferenceProceedings",
            "techreport": "Report",
            "book": "Book",
            "misc": "Misc",
        }.get(fields.get("__type__", "misc"), "Misc"))
        guid = uuid.uuid5(uuid.NAMESPACE_URL, "dt-gsk-bib:" + key)
        _add("Guid", "{%s}" % str(guid).upper())
        authors = fields.get("author", "")
        if authors:
            a1 = etree.SubElement(src, "{%s}Author" % B)
            a2 = etree.SubElement(a1, "{%s}Author" % B)
            nl = etree.SubElement(a2, "{%s}NameList" % B)
            for person in re.split(r"\s+and\s+", authors):
                person = _delatex(person)
                if not person:
                    continue
                p = etree.SubElement(nl, "{%s}Person" % B)
                if "," in person:
                    last, first = [x.strip() for x in person.split(",", 1)]
                else:
                    bits = person.rsplit(" ", 1)
                    first = bits[0] if len(bits) > 1 else ""
                    last = bits[-1]
                e = etree.SubElement(p, "{%s}Last" % B)
                e.text = last
                if first:
                    e = etree.SubElement(p, "{%s}First" % B)
                    e.text = first
        if fields.get("title"):
            _add("Title", _delatex(fields["title"]))
        if fields.get("year"):
            _add("Year", _delatex(fields["year"]))
        if fields.get("journal"):
            _add("JournalName", _delatex(fields["journal"]))
        if fields.get("booktitle"):
            _add("ConferenceName", _delatex(fields["booktitle"]))
        pub = fields.get("publisher") or fields.get("institution")
        if pub:
            _add("Publisher", _delatex(pub))
        if fields.get("address"):
            _add("City", _delatex(fields["address"]))
        if fields.get("volume"):
            _add("Volume", _delatex(fields["volume"]))
        if fields.get("number"):
            _add("Issue", _delatex(fields["number"]))
        if fields.get("pages"):
            _add("Pages", _delatex(fields["pages"]))
        if fields.get("url"):
            _add("URL", _delatex(fields["url"]))
        elif fields.get("doi"):
            _add("URL", "https://doi.org/" + _delatex(fields["doi"]))
    return serialize_xml(root)


ITEM_PROPS_XML = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
    '<ds:datastoreItem ds:itemID="{18AB57C6-4C09-45D4-A252-1B7A78A47AEA}" '
    'xmlns:ds="http://schemas.openxmlformats.org/officeDocument/2006/customXml">'
    '<ds:schemaRefs><ds:schemaRef ds:uri='
    '"http://schemas.openxmlformats.org/officeDocument/2006/bibliography"/>'
    "</ds:schemaRefs></ds:datastoreItem>"
).encode()

ITEM_RELS_XML = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
    '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
    '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/'
    'officeDocument/2006/relationships/customXmlProps" Target="itemProps1.xml"/>'
    "</Relationships>"
).encode()


# ===========================================================================
# native table construction
# ===========================================================================

def apply_terminology(s: str) -> str:
    for old, new in TERMINOLOGY:
        s = s.replace(old, new)
    return s


def _float_or_none(s: str) -> float | None:
    try:
        return float(s)
    except (TypeError, ValueError):
        return None


def compute_bold_mask(table_id: str, headers: list[str],
                      rows: list[list[str]]) -> set[tuple[int, int]]:
    """Reproduce the frozen .tex 'best value in bold' convention from the
    semantic values (first-minimum tie rule, matching the generator)."""
    bold: set[tuple[int, int]] = set()
    pair_tables = {"T1", "T2", "T3", "T4", "T5", "T11", "T12", "T13"}
    family_tables = {"T7", "T8", "T9", "T10"}
    if table_id in pair_tables:
        try:
            g = headers.index("Mean_GSK")
            i = headers.index("Mean_ISM")
        except ValueError:
            return bold
        for r, row in enumerate(rows):
            a, b = _float_or_none(row[g]), _float_or_none(row[i])
            if a is None or b is None:
                continue
            bold.add((r, g if a <= b else i))
    elif table_id in family_tables:
        idxs = [c for c, h in enumerate(headers) if h.endswith("_Mean")]
        for r, row in enumerate(rows):
            vals = [(c, _float_or_none(row[c])) for c in idxs]
            vals = [(c, v) for c, v in vals if v is not None]
            if not vals:
                continue
            best = min(vals, key=lambda cv: cv[1])
            bold.add((r, best[0]))
    elif table_id == "T16":
        for c in range(1, len(headers)):
            vals = [(r, _float_or_none(row[c])) for r, row in enumerate(rows)]
            vals = [(r, v) for r, v in vals if v is not None]
            if not vals:
                continue
            best = min(vals, key=lambda rv: rv[1])
            bold.add((best[0], c))
    return bold


def load_word_source(table_id: str) -> dict:
    return json.loads((WORD_SOURCES / f"{table_id}.json")
                      .read_text(encoding="utf-8"))


def parse_t16_bca_tex() -> tuple[list[list[str]], list[list[str]]]:
    """Parse the frozen rank-CI table (papers/tables/T16_bca.tex).

    Returns (header_rows, data_rows) of display strings -- the DOCX renders
    the SAME content as the .tex per the Phase 9 reconciliation.
    """
    txt = (ROOT / "tables" / "T16_bca.tex").read_text(encoding="utf-8")
    inner = re.search(r"\\begin\{tabular\}\{[^}]*\}(.*)\\end\{tabular\}",
                      txt, re.DOTALL).group(1)
    inner = re.sub(r"\\(top|mid|bottom)rule", "", inner)

    def _clean(cell: str) -> str:
        cell = cell.strip()
        cell = cell.replace("\\fdbagsk{}", "FDB-AGSK")
        cell = cell.replace("\\egsk{}", "eGSK")
        cell = cell.replace("\\dtgsk{}", "DT-GSK")
        cell = re.sub(r"\\textbf\{([^}]*)\}", r"\1", cell)
        cell = cell.replace("\\%", "%").replace("$", "")
        cell = " ".join(cell.split())
        return cell

    rows = []
    for raw_row in inner.split("\\\\"):
        if not raw_row.strip():
            continue
        rows.append([_clean(c) for c in raw_row.split("&")])
    header_rows, data_rows = rows[:2], rows[2:]
    return header_rows, data_rows


# --- Generic frozen results-table (.tex) parser -----------------------------
# Renders the DOCX numeric tables from the SAME frozen display .tex the PDF
# uses (grouped headers flattened to combined labels; 2-3 sig figs; mean+-SD;
# \bestval -> bold), instead of the raw word_sources/*.json DataFrame dump.
_RESULTS_TEX_IDS = {"T1", "T2", "T3", "T4", "T5", "T6", "T7", "T8", "T9", "T10",
                    "T11", "T12", "T13", "T14", "T15", "T16"}
_TEX_CELL_MACROS = {r"\dtgsk{}": "DT-GSK", r"\egsk{}": "eGSK", r"\agsk{}": "AGSK",
                    r"\apgsk{}": "APGSK", r"\fdbagsk{}": "FDB-AGSK",
                    r"\atmals{}": "ATMALS-GSK",
                    r"\wmark": "+", r"\emark": "≈", r"\lmark": "−"}


def _tex_filename_for(table_id: str) -> str:
    m = re.match(r"T(\d+)$", table_id)
    return f"T{int(m.group(1)):02d}.tex" if m else table_id + ".tex"


def _clean_tex_cell(cell: str, bold_flag: list) -> str:
    c = cell.strip()
    if r"\bestval{" in c:
        bold_flag[0] = True
        c = re.sub(r"\\bestval\{(.*?)\}", r"\1", c)
    c = re.sub(r"\\textbf\{(.*?)\}", r"\1", c)
    # Convert the head-to-head display form ``$m \times 10^{e}$`` to standard
    # sci-notation ``mE+0e`` before the generic macro strip (which would else
    # mangle it to "m 10 e"). The DOCX shows E-notation for these cells while the
    # PDF shows the x10 form; the parity gate canonicalizes both to the same
    # value (2026-07-24).
    c = re.sub(r"([-\d.]+)\s*\\times\s*10\^\{?(-?\d+)\}?",
               lambda m: f"{m.group(1)}E{int(m.group(2)):+03d}", c)
    c = c.replace(r"$\pm$", "±").replace(r"\pm", "±")
    c = c.replace(r"$\approx$", "≈").replace(r"\approx", "≈")
    for k, v in _TEX_CELL_MACROS.items():
        c = c.replace(k, v)
    c = c.replace(r"\mathrm", "").replace(r"\text", "").replace(r"\,", " ")
    c = re.sub(r"\^\{?\\ast\}?", "*", c)
    c = re.sub(r"\^\{([^}]*)\}", r"\1", c)
    c = re.sub(r"\^(\S)", r"\1", c)
    c = re.sub(r"_\{([^}]*)\}", r"\1", c)
    c = re.sub(r"_(\w)", r"\1", c)
    c = c.replace("$", "").replace(r"\%", "%").replace("~", " ")
    c = c.replace("{", "").replace("}", "")
    c = re.sub(r"\\[a-zA-Z]+", " ", c)
    c = re.sub(r"^(-?\d+)\.0+$", r"\1", c)
    return " ".join(c.split())


def _expand_multicol_row(cells: list) -> list:
    # A \multicolumn{n}{}{label} becomes the label in its first cell + (n-1)
    # blanks, so an appended stacked-tabular group header (e.g. T15's D50/D100)
    # reads as one left-aligned group label per span instead of the label
    # repeated n times across the row.
    out = []
    for c in cells:
        m = re.search(r"\\multicolumn\{(\d+)\}\{[^}]*\}\{(.*)\}", c.strip(), re.DOTALL)
        if m:
            out.extend([m.group(2)] + [""] * (int(m.group(1)) - 1))
        else:
            out.append(c)
    return out


def parse_frozen_table_tex(table_id: str):
    """Parse ``tables/<Txx>.tex`` -> (header_rows, data_rows, bold_mask).

    A .tex that stacks several ``tabular`` blocks under one caption (e.g. T15's
    D10/D30 and D50/D100 sub-tables) is flattened into ONE DOCX table: the first
    block supplies the grouped header and its data rows; every later block's rows
    (its dimension sub-header included, multicolumn expanded) are appended as data
    so the DOCX carries the SAME cells as the PDF (Round-2 review F4)."""
    txt = (ROOT / "tables" / _tex_filename_for(table_id)).read_text(encoding="utf-8")
    # Drop \cmidrule / \cline rules -- they carry no cells but, lacking a
    # trailing "\\", would otherwise attach to the next header cell (the
    # side-by-side h2h group rules, 2026-07-24).
    txt = re.sub(r"\\cmidrule(?:\([^)]*\))?\{[^}]*\}", "", txt)
    txt = re.sub(r"\\cline\{[^}]*\}", "", txt)
    tabulars = re.findall(r"\\begin\{tabular\}\{[^}]*\}(.*?)\\end\{tabular\}",
                          txt, re.DOTALL)
    inner = tabulars[0]
    parts = re.split(r"\\midrule", inner, maxsplit=1)
    head_src = parts[0].replace(r"\toprule", "")
    data_src = re.sub(r"\\(bottomrule|midrule)", "",
                      parts[1] if len(parts) > 1 else "")

    def _rows(src):
        return [r.split("&") for r in src.split("\\\\") if r.strip()]

    def _rowspan(r):
        n = 0
        for c in r:
            m = re.search(r"\\multicolumn\{(\d+)\}", c)
            n += int(m.group(1)) if m else 1
        return n

    hraw = _rows(head_src)
    draw = _rows(data_src)
    for extra in tabulars[1:]:                       # stacked sub-tables (e.g. T15)
        extra = re.sub(r"\\(top|mid|bottom)rule", "", extra)
        draw += _rows(extra)
    ncol = max([_rowspan(r) for r in hraw] + [_rowspan(r) for r in draw], default=0)
    # Preserve \multicolumn groups as (text, colspan) so the DOCX renders the
    # SAME two-tier grouped header as the PDF (D10/D30/D50/D100, Best/Median/...)
    # instead of flattening them into one combined label row.
    header_spans = []
    for r in hraw:
        cells, tot = [], 0
        for c in r:
            m = re.search(r"\\multicolumn\{(\d+)\}\{[^}]*\}\{(.*)\}",
                          c.strip(), re.DOTALL)
            if m:
                span, txt_ = int(m.group(1)), _clean_tex_cell(m.group(2), [False])
            else:
                span, txt_ = 1, _clean_tex_cell(c, [False])
            cells.append((txt_, span))
            tot += span
        if tot < ncol:
            cells.append(("", ncol - tot))
        header_spans.append(cells)
    data_rows, bold = [], set()
    for ri, raw in enumerate(draw):
        raw = _expand_multicol_row(raw)              # expand D50/D100 sub-header groups
        row = []
        for ci, cell in enumerate(raw):
            bf = [False]
            row.append(_clean_tex_cell(cell, bf))
            if bf[0]:
                bold.add((ri, ci))
        data_rows.append(row)
    return header_spans, data_rows, bold


def _normalize_header_spans(header):
    """Return the header as a list of rows of ``(text, colspan)``.

    Accepts either flat rows of strings (each cell colspan 1) -- as produced by
    ``parse_t16_bca_tex`` and the word_sources path -- or rows already made of
    ``(text, colspan)`` tuples from :func:`parse_frozen_table_tex`."""
    out = []
    for row in header:
        if row and isinstance(row[0], tuple):
            out.append([(str(t), int(s)) for (t, s) in row])
        else:
            out.append([(str(c), 1) for c in row])
    return out


def _table_font_halfpt(ncols: int) -> int:
    # Step the font down as the column count rises so the whole table fits the
    # page width on one line per cell -- the DOCX analogue of the PDF's
    # \resizebox{\textwidth}{!}{...} shrink-to-fit.
    if ncols <= 6:
        return 18   # 9 pt
    if ncols <= 11:
        return 16   # 8 pt
    if ncols <= 15:
        return 14   # 7 pt
    if ncols <= 20:
        return 12   # 6 pt
    if ncols <= 24:
        return 11   # 5.5 pt
    return 10       # 5 pt (very wide, e.g. the 28-column Wilcoxon-Holm table)


# Page geometry of word/reference.docx (A4 portrait): text width =
# pgSz.w (11906) - pgMar.left (1134) - pgMar.right (1134).
_PORTRAIT_TEXT_TWIPS = 9638
# Cell inset (left/right), reduced from Word's ~108-twip default so dense
# numeric tables reclaim width instead of wrapping every cell.
_TBL_CELL_MARGIN = 28


def _longest_token(s: str) -> int:
    """Longest whitespace-delimited token -- the unit that cannot wrap
    (numbers like ``<0.0001`` are single tokens; multi-word headers wrap)."""
    toks = str(s).split()
    return max((len(t) for t in toks), default=1)


def _col_char_weights(header_rows, data_rows, ncols: int) -> list[int]:
    w = [1] * ncols
    for row in list(header_rows) + list(data_rows):
        for c in range(min(len(row), ncols)):
            w[c] = max(w[c], _longest_token(row[c]))
    return w


def _scale_widths_to_fit(widths: list[float], available: int,
                         min_col: int) -> list[int]:
    """If the content-natural widths sum to more than ``available``, shrink them
    proportionally (keeping a per-column floor) so the table fits the page;
    otherwise leave them content-sized (do not stretch to full width)."""
    total = sum(widths)
    if total <= available:
        return [max(1, int(round(w))) for w in widths]
    ws = [max(float(min_col), available * w / total) for w in widths]
    over = sum(ws) - available
    if over > 0:
        flex = [(i, ws[i] - min_col) for i in range(len(ws)) if ws[i] > min_col]
        fs = sum(f for _, f in flex)
        if fs > 0:
            for i, f in flex:
                ws[i] -= over * (f / fs)
    return [max(1, int(round(x))) for x in ws]


def build_native_table(table_id: str) -> tuple[etree._Element, str, int, int]:
    """Return (w:tbl element, caption_stub, n_rows, n_cols)."""
    if table_id == "T16_bca":
        header_rows, data_rows = parse_t16_bca_tex()
        caption = ("BCa 95% CI companion to the CEC2017 Friedman mean ranks "
                   "(rank-CI table; frozen T16_bca.tex content)")
        bold_mask: set[tuple[int, int]] = set()
    elif (table_id in _RESULTS_TEX_IDS
          and (ROOT / "tables" / _tex_filename_for(table_id)).exists()):
        # Render the SAME formatted display the PDF uses (frozen .tex), not the
        # raw word_sources DataFrame dump.
        header_rows, data_rows, bold_mask = parse_frozen_table_tex(table_id)
        caption = load_word_source(table_id).get("caption_stub", "")
    else:
        src = load_word_source(table_id)
        headers = [apply_terminology(h) for h in src["headers"][0]]
        data_rows = [[apply_terminology(c) for c in row] for row in src["rows"]]
        header_rows = [headers]
        bold_mask = compute_bold_mask(table_id, src["headers"][0], src["rows"])
        caption = src.get("caption_stub", "")

    header_spans = _normalize_header_spans(header_rows)
    ncols = max([sum(s for _, s in hr) for hr in header_spans]
                + [len(r) for r in data_rows], default=0)
    # Per-column header text for width weighting: expand a span onto its first
    # underlying column so a wide group label does not inflate every column.
    _flat_headers = []
    for hr in header_spans:
        exp = []
        for _t, _s in hr:
            exp.append(_t)
            exp.extend([""] * (_s - 1))
        _flat_headers.append(exp)
    weights = _col_char_weights(_flat_headers, data_rows, ncols)
    # Size columns to their content (longest unbreakable token) and pick the
    # largest font whose content-natural width still fits the page text width,
    # stepping down as needed -- the DOCX analogue of the PDF's
    # \resizebox{\textwidth}{!}{...}.  Content-sized tables are NOT stretched to
    # full width (so a narrow table like the Friedman-rank table stays compact,
    # matching its un-resized PDF rendering), while a very wide table (the
    # 29-column Wilcoxon-Holm table) shrinks to fit instead of wrapping.
    sz = _table_font_halfpt(ncols)
    while sz > 8:
        _glyph = int(round(5.5 * sz))  # ~0.55 em/glyph (twips); sz is half-pt
        if sum(w * _glyph + 2 * _TBL_CELL_MARGIN
               for w in weights) <= _PORTRAIT_TEXT_TWIPS:
            break
        sz -= 2
    glyph = int(round(5.5 * sz))
    natural = [w * glyph + 2 * _TBL_CELL_MARGIN for w in weights]
    col_w = _scale_widths_to_fit(natural, _PORTRAIT_TEXT_TWIPS,
                                 2 * _TBL_CELL_MARGIN + 2 * glyph)
    total_w = sum(col_w)

    tbl = etree.Element(qn("w:tbl"))
    tblpr = etree.SubElement(tbl, qn("w:tblPr"))
    e = etree.SubElement(tblpr, qn("w:tblStyle"))
    e.set(qn("w:val"), "Table")
    e = etree.SubElement(tblpr, qn("w:tblW"))
    e.set(qn("w:w"), str(total_w))
    e.set(qn("w:type"), "dxa")
    lay = etree.SubElement(tblpr, qn("w:tblLayout"))
    lay.set(qn("w:type"), "fixed")
    cm = etree.SubElement(tblpr, qn("w:tblCellMar"))
    for _side in ("left", "right"):
        _m = etree.SubElement(cm, qn("w:" + _side))
        _m.set(qn("w:w"), str(_TBL_CELL_MARGIN))
        _m.set(qn("w:type"), "dxa")
    for _side in ("top", "bottom"):
        _m = etree.SubElement(cm, qn("w:" + _side))
        _m.set(qn("w:w"), "0")
        _m.set(qn("w:type"), "dxa")
    _cap = _clean_tex_cell(caption or table_id, [False]) or table_id
    cap = etree.SubElement(tblpr, qn("w:tblCaption"))
    cap.set(qn("w:val"), _cap[:250])
    desc = etree.SubElement(tblpr, qn("w:tblDescription"))
    desc.set(qn("w:val"), _cap[:500])
    look = etree.SubElement(tblpr, qn("w:tblLook"))
    look.set(qn("w:val"), "04A0")
    look.set(qn("w:firstRow"), "1")
    look.set(qn("w:lastRow"), "0")
    look.set(qn("w:firstColumn"), "0")
    look.set(qn("w:lastColumn"), "0")
    look.set(qn("w:noHBand"), "0")
    look.set(qn("w:noVBand"), "1")
    grid = etree.SubElement(tbl, qn("w:tblGrid"))
    for cw in col_w:
        gc = etree.SubElement(grid, qn("w:gridCol"))
        gc.set(qn("w:w"), str(cw))

    def _mkrow(cells: list[str], *, header: bool,
               bold_cells: set[int] = frozenset()):
        tr = etree.SubElement(tbl, qn("w:tr"))
        trpr = etree.SubElement(tr, qn("w:trPr"))
        etree.SubElement(trpr, qn("w:cantSplit"))
        if header:
            etree.SubElement(trpr, qn("w:tblHeader"))
        padded = list(cells) + [""] * (ncols - len(cells))
        for c, text in enumerate(padded):
            tc = etree.SubElement(tr, qn("w:tc"))
            tcpr = etree.SubElement(tc, qn("w:tcPr"))
            tcw = etree.SubElement(tcpr, qn("w:tcW"))
            tcw.set(qn("w:w"), str(col_w[c] if c < len(col_w)
                                   else min(col_w, default=500)))
            tcw.set(qn("w:type"), "dxa")
            if header:
                shd = etree.SubElement(tcpr, qn("w:shd"))
                shd.set(qn("w:val"), "clear")
                shd.set(qn("w:color"), "auto")
                shd.set(qn("w:fill"), "E7E6E6")
            p = etree.SubElement(tc, qn("w:p"))
            ppr = etree.SubElement(p, qn("w:pPr"))
            st = etree.SubElement(ppr, qn("w:pStyle"))
            st.set(qn("w:val"), "Compact")
            jc = etree.SubElement(ppr, qn("w:jc"))
            jc.set(qn("w:val"), "left" if c == 0 else "center")
            run = make_run(text, bold=header or (c in bold_cells),
                           sz_half_pt=sz)
            p.append(run)
        return tr

    def _mk_header_row(spanrow):
        tr = etree.SubElement(tbl, qn("w:tr"))
        trpr = etree.SubElement(tr, qn("w:trPr"))
        etree.SubElement(trpr, qn("w:cantSplit"))
        etree.SubElement(trpr, qn("w:tblHeader"))
        ci = 0
        for text, span in spanrow:
            tc = etree.SubElement(tr, qn("w:tc"))
            tcpr = etree.SubElement(tc, qn("w:tcPr"))
            w = (sum(col_w[ci:ci + span]) if ci < len(col_w)
                 else 2 * _TBL_CELL_MARGIN)
            tcw = etree.SubElement(tcpr, qn("w:tcW"))
            tcw.set(qn("w:w"), str(w))
            tcw.set(qn("w:type"), "dxa")
            if span > 1:
                gs = etree.SubElement(tcpr, qn("w:gridSpan"))
                gs.set(qn("w:val"), str(span))
            shd = etree.SubElement(tcpr, qn("w:shd"))
            shd.set(qn("w:val"), "clear")
            shd.set(qn("w:color"), "auto")
            shd.set(qn("w:fill"), "E7E6E6")
            p = etree.SubElement(tc, qn("w:p"))
            ppr = etree.SubElement(p, qn("w:pPr"))
            stp = etree.SubElement(ppr, qn("w:pStyle"))
            stp.set(qn("w:val"), "Compact")
            jc = etree.SubElement(ppr, qn("w:jc"))
            jc.set(qn("w:val"), "left" if ci == 0 else "center")
            p.append(make_run(text, bold=True, sz_half_pt=sz))
            ci += span
        return tr

    for hr in header_spans:
        _mk_header_row(hr)
    for r, row in enumerate(data_rows):
        _mkrow(row, header=False,
               bold_cells={c for (rr, c) in bold_mask if rr == r})
    return tbl, caption, len(data_rows), ncols


# --- authored figure-table recovery (Round-1 review MAJ-1/MAJ-2) -------------
# Four expository main-text tables are hand-written `\begin{tabular}{p{..}..}`
# grids inside `figure` floats with multi-line `\\` cells; pandoc cannot parse
# them and emits a single 1x1 cell (all text concatenated) carrying a dangling
# "FigureTable" style. We detect those collapsed tables and rebuild them as
# native multi-column w:tbl from the frozen source tabular.

def _split_top_level(s: str, sep: str) -> list[str]:
    """Split s on sep at brace-depth 0 and outside $...$ math."""
    out, buf, depth, math = [], [], 0, False
    i = 0
    while i < len(s):
        ch = s[i]
        if ch == "\\" and i + 1 < len(s):        # escaped token: keep the pair
            buf.append(s[i:i + 2]); i += 2; continue
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
        elif ch == "$":
            math = not math
        if ch == sep and depth == 0 and not math:
            out.append("".join(buf)); buf = []
        else:
            buf.append(ch)
        i += 1
    out.append("".join(buf))
    return out


def _extract_authored_tabular(src_text: str, label: str, ref_resolver=None):
    """Return (header_row, data_rows, ncols) for the tabular of the figure
    carrying \\label{label}, or None. ref_resolver maps a cross-reference
    label to its number (for \\ref/\\eqref inside cells)."""
    li = src_text.find("\\label{" + label + "}")
    if li < 0:
        return None
    end = src_text.rfind("\\end{tabular}", 0, li)
    beg = src_text.rfind("\\begin{tabular}", 0, end)
    if beg < 0 or end < 0:
        return None
    block = src_text[beg:end]
    # Skip "\begin{tabular}", any optional [pos] arg, then the BALANCED
    # {column spec} -- which itself contains nested braces, e.g. p{2.85cm}.
    j = block.find("\\begin{tabular}") + len("\\begin{tabular}")
    while j < len(block) and block[j] in " \t\r\n":
        j += 1
    if j < len(block) and block[j] == "[":            # optional [t]/[b] positioning
        j = block.find("]", j) + 1
        while j < len(block) and block[j] in " \t\r\n":
            j += 1
    if j < len(block) and block[j] == "{":
        depth = 0
        while j < len(block):
            if block[j] == "{":
                depth += 1
            elif block[j] == "}":
                depth -= 1
                if depth == 0:
                    j += 1
                    break
            j += 1
    inner = block[j:]
    for tok in ("\\toprule", "\\midrule", "\\bottomrule", "\\zebra"):
        inner = inner.replace(tok, "")
    rows = []
    for raw in re.split(r"\\\\", inner):
        if not raw.strip():
            continue
        cells = [_cell_delatex(c.strip(), ref_resolver)
                 for c in _split_top_level(raw, "&")]
        if any(cells):
            rows.append(cells)
    if len(rows) < 2:
        return None
    ncols = max(len(r) for r in rows)
    return rows[0], rows[1:], ncols


def _simple_native_tbl(header_row, data_rows, ncols):
    """A bordered, autofit native w:tbl (style 'Table') for a recovered
    authored table -- adequate for expository grids without the tuned
    width machinery of build_native_table."""
    tbl = etree.Element(qn("w:tbl"))
    tblpr = etree.SubElement(tbl, qn("w:tblPr"))
    etree.SubElement(tblpr, qn("w:tblStyle")).set(qn("w:val"), "Table")
    w = etree.SubElement(tblpr, qn("w:tblW")); w.set(qn("w:w"), "5000"); w.set(qn("w:type"), "pct")
    etree.SubElement(tblpr, qn("w:tblLayout")).set(qn("w:type"), "autofit")
    borders = etree.SubElement(tblpr, qn("w:tblBorders"))
    for side in ("top", "left", "bottom", "right", "insideH", "insideV"):
        b = etree.SubElement(borders, qn("w:" + side))
        b.set(qn("w:val"), "single"); b.set(qn("w:sz"), "4")
        b.set(qn("w:space"), "0"); b.set(qn("w:color"), "auto")
    grid = etree.SubElement(tbl, qn("w:tblGrid"))
    for _ in range(ncols):
        etree.SubElement(grid, qn("w:gridCol")).set(qn("w:w"), str(_PORTRAIT_TEXT_TWIPS // ncols))

    def _row(cells, header):
        tr = etree.SubElement(tbl, qn("w:tr"))
        trpr = etree.SubElement(tr, qn("w:trPr"))
        etree.SubElement(trpr, qn("w:cantSplit"))
        if header:
            etree.SubElement(trpr, qn("w:tblHeader"))
        padded = (list(cells) + [""] * ncols)[:ncols]
        for c, text in enumerate(padded):
            tc = etree.SubElement(tr, qn("w:tc"))
            tcpr = etree.SubElement(tc, qn("w:tcPr"))
            tcw = etree.SubElement(tcpr, qn("w:tcW"))
            tcw.set(qn("w:w"), str(5000 // ncols)); tcw.set(qn("w:type"), "pct")
            if header:
                shd = etree.SubElement(tcpr, qn("w:shd"))
                shd.set(qn("w:val"), "clear"); shd.set(qn("w:color"), "auto")
                shd.set(qn("w:fill"), "E7E6E6")
            p = etree.SubElement(tc, qn("w:p"))
            ppr = etree.SubElement(p, qn("w:pPr"))
            etree.SubElement(ppr, qn("w:pStyle")).set(qn("w:val"), "Compact")
            p.append(make_run(text, bold=header, sz_half_pt=16))
        return tr

    _row(header_row, True)
    for row in data_rows:
        _row(row, False)
    return tbl


# ===========================================================================
# OOXML post-processing
# ===========================================================================

class PostProcessor:
    def __init__(self, docx_path: Path, doc_kind: str):
        self.doc_kind = doc_kind
        self.spec = DOC_SPECS[doc_kind]
        self.parts = dict(read_zip_parts(docx_path))
        self.part_order = [name for name, _ in read_zip_parts(docx_path)]
        self.doc = parse_xml(self.parts["word/document.xml"])
        self.body = self.doc.find(qn("w:body"))
        self.aux = parse_aux_labels(self.spec["aux"])
        self.bibnums = parse_aux_bibcites(self.spec["aux"])
        self.registry: list[dict[str, str]] = []
        self._bm_next = self._max_bookmark_id() + 1
        self.counts = {"SEQ": 0, "REF": 0, "CITATION": 0, "TOC": 0,
                       "tables_native": 0, "bookmarks_added": 0,
                       "images_alt": 0}

    # -- helpers ----------------------------------------------------------
    def _max_bookmark_id(self) -> int:
        mx = 0
        for bm in self.doc.iter(qn("w:bookmarkStart")):
            try:
                mx = max(mx, int(bm.get(qn("w:id"))))
            except (TypeError, ValueError):
                pass
        return mx

    def _new_bm_id(self) -> int:
        i = self._bm_next
        self._bm_next += 1
        return i

    @staticmethod
    def _para_text(p) -> str:
        return "".join(t.text or "" for t in p.iter(qn("w:t")))

    def _log(self, ftype: str, fid: str, target: str, cached: str,
             location: str):
        self.registry.append({
            "doc": self.spec["out"].name,
            "field_type": ftype,
            "field_id": fid,
            "target": target,
            "cached_result": cached,
            "location": location,
        })

    def _seq_field(self, seq_name: str, cached: str, bold: bool):
        self.counts["SEQ"] += 1
        return make_field_runs(f" SEQ {seq_name} \\* ARABIC ", cached,
                               result_bold=bold)

    def _num_for(self, label: str) -> str:
        return self.aux.get(label, "??")

    # -- marker resolution --------------------------------------------------
    def process(self) -> None:
        self._pass_paragraph_markers()
        self._pass_inline_markers()
        self._clean_marker_attributes()
        self._rename_pandoc_bookmarks()
        self._pass_alt_text()
        self._rebuild_collapsed_authored_tables()
        self._protect_table_rows()
        # Landscape wide-table sections are DISABLED (2026-07-24 author request:
        # every page portrait). The wide tables now split into stacked halves in
        # the PDF and render portrait at the column-count-stepped font here, so no
        # rotated section (and none of the blank pages the section breaks caused)
        # is emitted. self._landscape_wide_tables() is retained but not called.
        self._add_page_numbers()
        self._affiliations_before_abstract()
        self._hoist_article_label()
        self._fix_math_alignment_markers()
        # No table of contents: the MDPI article PDF renders none, so the DOCX
        # omits it too for format parity with the PDF. (A native TOC field used
        # to be inserted here via self._insert_toc(); removed per the
        # "DOCX must match the PDF" requirement. The method is retained but
        # unused in case a future TOC-bearing target is added.)
        self._settings_update_fields()
        self._set_hyperlink_style()
        self._bind_figure_captions()
        self._install_citation_store()
        residues = self.parts_document_residue()
        if residues:
            raise RuntimeError(f"unresolved markers remain: {residues[:5]}")

    def _hoist_article_label(self) -> None:
        """Move the MDPI article-type label above the title block.

        The shim emits ``\\textit{Article}`` before ``\\maketitle``, but pandoc
        builds the title block from document METADATA and hoists it to the top,
        so a body paragraph written before ``\\maketitle`` still lands after the
        title and abstract. Relocating it here puts it where the MDPI class puts
        it in the PDF (first line of the title page). Main document only --
        the supplement has no article-type label.
        """
        if self.doc_kind != "main":
            return
        for para in self.body.findall(qn("w:p")):
            text = "".join(node.text or "" for node in para.iter(qn("w:t")))
            if text.strip() == "Article":
                self.body.remove(para)
                self.body.insert(0, para)
                return

    def _affiliations_before_abstract(self) -> None:
        """Place the affiliation/correspondence block above the abstract.

        Pandoc treats ``abstract`` as document METADATA and hoists it to the top
        of the body, so the centred affiliation block emitted after
        ``\\maketitle`` ends up BELOW the abstract -- the reverse of the MDPI
        class layout in the PDF (FM-02). Move those paragraphs back above the
        abstract heading. Main document only.
        """
        if self.doc_kind != "main":
            return
        paras = self.body.findall(qn("w:p"))

        def text_of(p) -> str:
            return "".join(n.text or "" for n in p.iter(qn("w:t"))).strip()

        abstract_idx = next(
            (i for i, p in enumerate(paras) if text_of(p).lower() == "abstract"), None)
        if abstract_idx is None:
            return
        # Affiliation block = the numbered-affiliation paragraph plus the
        # correspondence line, both of which sit AFTER the abstract when pandoc
        # has hoisted it.
        movers = [p for p in paras[abstract_idx:]
                  if ("Operations Research Department" in text_of(p)
                      or text_of(p).startswith("* Correspondence"))]
        if not movers:
            return
        anchor = paras[abstract_idx]
        for para in movers:
            self.body.remove(para)
        for offset, para in enumerate(movers):
            self.body.insert(list(self.body).index(anchor) + offset, para)

    def _add_page_numbers(self) -> None:
        """Add a centered page-number footer to every section (2026-07-24
        author request: match the PDF, which numbers every page). Mirrors the
        part/content-type/relationship wiring of :meth:`_install_citation_store`.
        """
        footer_xml = (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\r\n'
            '<w:ftr xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" '
            'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
            '<w:p><w:pPr><w:jc w:val="center"/></w:pPr>'
            '<w:r><w:fldChar w:fldCharType="begin"/></w:r>'
            '<w:r><w:instrText xml:space="preserve"> PAGE </w:instrText></w:r>'
            '<w:r><w:fldChar w:fldCharType="separate"/></w:r>'
            '<w:r><w:t>1</w:t></w:r>'
            '<w:r><w:fldChar w:fldCharType="end"/></w:r>'
            '</w:p></w:ftr>'
        ).encode("utf-8")
        self.parts["word/footer1.xml"] = footer_xml
        if "word/footer1.xml" not in self.part_order:
            self.part_order.append("word/footer1.xml")

        # content type override
        ct = parse_xml(self.parts["[Content_Types].xml"])
        CT = NSMAP["ct"]
        if not any(o.get("PartName") == "/word/footer1.xml"
                   for o in ct.findall("{%s}Override" % CT)):
            o = etree.SubElement(ct, "{%s}Override" % CT)
            o.set("PartName", "/word/footer1.xml")
            o.set("ContentType", "application/vnd.openxmlformats-officedocument."
                                 "wordprocessingml.footer+xml")
        self.parts["[Content_Types].xml"] = serialize_xml(ct)

        # document relationship -> the footer part
        rels = parse_xml(self.parts["word/_rels/document.xml.rels"])
        REL = NSMAP["rel"]
        existing = {r.get("Id") for r in rels.findall("{%s}Relationship" % REL)}
        rid = "rId8001"
        i = 1
        while rid in existing:
            i += 1
            rid = f"rId800{i}"
        r = etree.SubElement(rels, "{%s}Relationship" % REL)
        r.set("Id", rid)
        r.set("Type", "http://schemas.openxmlformats.org/officeDocument/2006/"
                      "relationships/footer")
        r.set("Target", "footer1.xml")
        self.parts["word/_rels/document.xml.rels"] = serialize_xml(rels)

        # reference the footer from every sectPr (footerReference must be the
        # first child group of CT_SectPr, before pgSz/pgMar).
        r_ns = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
        n = 0
        for sectpr in self.doc.iter(qn("w:sectPr")):
            if sectpr.find(qn("w:footerReference")) is not None:
                continue
            ref = etree.Element(qn("w:footerReference"))
            ref.set(qn("w:type"), "default")
            ref.set("{%s}id" % r_ns, rid)
            sectpr.insert(0, ref)
            n += 1
        return None

    def _landscape_wide_tables(self, min_cols: int = 8) -> None:
        """CR/WORD-001: put each wide table on a true Word landscape page.

        CR-007 rotated the wide per-function tables in the PDF (pdflscape sets
        /Rotate), but pandoc drops that env, so in the DOCX those 8-to-15-column
        tables stayed portrait at ~4-5 pt.  Word changes page orientation only
        at a SECTION boundary, so a table is made landscape by bracketing it
        with two paragraph-level ``w:sectPr`` breaks: a portrait one before its
        caption (ending the preceding portrait section) and a landscape one
        after the table (which governs the section the table now sits in).  The
        immediately-preceding caption paragraph is pulled into the landscape
        section so the caption stays with its table.  The body-final sectPr
        keeps the rest of the document portrait.
        """
        import copy
        body_sectpr = self.body.find(qn("w:sectPr"))
        if body_sectpr is None:
            return

        def _sectpr(landscape: bool):
            sp = copy.deepcopy(body_sectpr)
            for tag in ("w:headerReference", "w:footerReference"):
                for el in sp.findall(qn(tag)):
                    sp.remove(el)
            # An attribute-only <w:pgSz> is a childless lxml element and thus
            # FALSY, so `A or B` would always append a SECOND pgSz -- two pgSz
            # in one sectPr is schema-invalid (CT_SectPr maxOccurs=1) and strict
            # consumers (python-docx) then honour the first, portrait one and
            # see no landscape.  Mutate the single inherited pgSz in place.
            pgsz = sp.find(qn("w:pgSz"))
            if pgsz is None:
                pgsz = etree.SubElement(sp, qn("w:pgSz"))
            pgmar = sp.find(qn("w:pgMar"))
            if landscape:
                pgsz.set(qn("w:w"), "16838"); pgsz.set(qn("w:h"), "11906")
                pgsz.set(qn("w:orient"), "landscape")
                if pgmar is not None:  # rotate the margins with the page
                    t, b = pgmar.get(qn("w:top")), pgmar.get(qn("w:bottom"))
                    l, r = pgmar.get(qn("w:left")), pgmar.get(qn("w:right"))
                    pgmar.set(qn("w:top"), r or "1134"); pgmar.set(qn("w:bottom"), l or "1134")
                    pgmar.set(qn("w:left"), b or "1417"); pgmar.set(qn("w:right"), t or "1417")
            else:
                pgsz.set(qn("w:w"), "11906"); pgsz.set(qn("w:h"), "16838")
                pgsz.attrib.pop(qn("w:orient"), None)
            return sp

        def _sectpr_para(landscape: bool):
            p = etree.Element(qn("w:p"))
            ppr = etree.SubElement(p, qn("w:pPr"))
            ppr.append(_sectpr(landscape))
            return p

        def _is_caption(p) -> bool:
            if p is None or p.tag != qn("w:p"):
                return False
            st = p.find(qn("w:pPr"))
            st = st.find(qn("w:pStyle")) if st is not None else None
            val = st.get(qn("w:val")) if st is not None else ""
            return "aption" in val or val.startswith("Table")

        wrapped = 0
        for tbl in list(self.body.findall(qn("w:tbl"))):
            grid = tbl.find(qn("w:tblGrid"))
            ncols = len(grid.findall(qn("w:gridCol"))) if grid is not None else 0
            if ncols < min_cols:
                continue
            start = tbl
            prev = tbl.getprevious()
            if _is_caption(prev):
                start = prev
            body = tbl.getparent()
            body.insert(list(body).index(start), _sectpr_para(False))
            body.insert(list(body).index(tbl) + 1, _sectpr_para(True))
            wrapped += 1
        print(f"  wide tables set to landscape Word sections: {wrapped} "
              f"(>= {min_cols} cols; WORD-001)")

    def _protect_table_rows(self) -> None:
        """CR-010: stop dense pandoc-built tables from splitting rows across a
        page break and losing their column headers on the continuation page.

        The native w:tbl builder already sets w:cantSplit / w:tblHeader on its
        rows, but the wide per-function tables reach the DOCX via pandoc's
        LaTeX->tabular conversion, which sets neither.  This pass gives EVERY
        row a w:cantSplit (a row's cells stay together on one page) and marks
        each table's first row w:tblHeader (it repeats atop every continuation
        page).  Both are inserted at the top of w:trPr per the OOXML schema's
        ordering; rows that already carry the property are left untouched.
        """
        rows_fixed = headers_fixed = 0
        for tbl in self.doc.iter(qn("w:tbl")):
            first_row = True
            for tr in tbl.findall(qn("w:tr")):
                trpr = tr.find(qn("w:trPr"))
                if trpr is None:
                    trpr = etree.Element(qn("w:trPr"))
                    tr.insert(0, trpr)
                if trpr.find(qn("w:cantSplit")) is None:
                    trpr.insert(0, etree.Element(qn("w:cantSplit")))
                    rows_fixed += 1
                if first_row and trpr.find(qn("w:tblHeader")) is None:
                    # after cantSplit, before other props
                    idx = 1 if trpr.find(qn("w:cantSplit")) is not None else 0
                    trpr.insert(idx, etree.Element(qn("w:tblHeader")))
                    headers_fixed += 1
                first_row = False
        print(f"  table rows protected: +{rows_fixed} cantSplit, "
              f"+{headers_fixed} repeat-header (CR-010)")

    def _clean_marker_attributes(self) -> None:
        """pandoc mirrors caption text into attributes (w:tblCaption etc.);
        resolve marker tokens inside attribute values to plain text."""

        def _resolve(m: re.Match[str]) -> str:
            tag = m.group(1)
            payload = [s for s in m.group(2).split("!") if s]
            if tag == "REF" and payload:
                return self._num_for(payload[0])
            if tag == "CITE" and payload:
                nums = sorted(self.bibnums.get(k, 0)
                              for k in payload[0].split(",") if k)
                return "[" + _collapse_ranges(nums) + "]"
            return ""

        for el_ in self.doc.iter():
            # w:tblCaption / wp:docPr carry the accessibility text a screen
            # reader announces and Word shows in its Alt Text pane; pandoc
            # mirrors the RAW caption there, so de-TeX it to match the visible
            # caption instead of leaking markup (\pm, \times, _{...}).
            captionish = el_.tag.endswith("}tblCaption") or el_.tag.endswith("}docPr")
            for attr, value in list(el_.attrib.items()):
                if "@@" in value:
                    value = MARKER_RE.sub(_resolve, value).strip()
                    el_.set(attr, value)
                # pandoc drops the $...$ delimiters when mirroring a caption, so
                # markup can arrive with NO backslash ("m_{ij}") -- trigger on the
                # sub/superscript braces too. flatten_subscripts=False because
                # these escapes are already resolved here: a literal "_" in this
                # text is a filename (algorithm_freeze_manifest.json), not a
                # subscript, and must survive.
                if captionish and any(t in value for t in ("\\", "_{", "^{", "$")):
                    el_.set(attr, _cell_delatex(value, flatten_subscripts=False))

    def _rebuild_collapsed_authored_tables(self) -> None:
        """Round-1 review MAJ-1/MAJ-2: four expository main-text tables are
        authored ``figure``-wrapped ``tabular`` grids that pandoc collapses into
        a single 1x1 cell (all text concatenated) carrying a dangling
        ``FigureTable`` style. Detect those (by that style) and swap in a native
        multi-column ``w:tbl`` rebuilt from the frozen source tabular, so the
        DOCX matches the PDF."""
        if self.doc_kind != "main":
            return
        specs = [
            (ROOT / "sections" / "related_work.tex", "fig:taxonomy"),
            (ROOT / "sections" / "proposed_algorithm.tex", "fig:architecture"),
            (ROOT / "sections" / "proposed_algorithm.tex", "fig:dim-gating"),
            (ROOT / "sections" / "proposed_algorithm.tex", "fig:sgsm-mechanism"),
        ]
        collapsed = [t for t in self.doc.iter(qn("w:tbl"))
                     if any(s.get(qn("w:val")) == "FigureTable"
                            for s in t.iter(qn("w:tblStyle")))]
        if not collapsed:
            # Expected state since N-010: the four exhibits are `table` floats,
            # not `figure`-wrapped tabulars, so pandoc emits them as native
            # multi-column tables and there is nothing to rebuild. This whole
            # routine was a workaround for the figure wrapping; it is retained
            # only so a regression back to figure floats is still repaired.
            print("  authored tables: 0 collapsed grids "
                  "(N-010: now native table floats, no recovery needed)")
            return
        if len(collapsed) != len(specs):
            raise RuntimeError(
                f"authored-table recovery: found {len(collapsed)} FigureTable "
                f"tables, expected 0 (native table floats) or {len(specs)} "
                f"(legacy figure-wrapped) -- source layout changed")
        removed: dict[tuple[str, str], int] = {}    # (field_type, target)->count
        for tbl, (path, label) in zip(collapsed, specs):
            # The collapsed cell carries resolved REF fields for the cell's
            # equation cross-references; the rebuilt cell renders them as plain
            # resolved numbers, so tally those fields to prune their registry
            # rows (keeps the field-registry vs package cross-check in balance).
            for instr in tbl.iter(qn("w:instrText")):
                code = " ".join((instr.text or "").split())
                for kind in ("REF", "CITATION", "SEQ"):
                    if code.startswith(kind + " "):
                        tgt = code.split()[1]
                        removed[(kind, tgt)] = removed.get((kind, tgt), 0) + 1
                        break
            parsed = _extract_authored_tabular(
                path.read_text(encoding="utf-8"), label, self._num_for)
            if parsed is None:
                raise RuntimeError(
                    f"authored-table recovery: cannot parse {label} in {path.name}")
            header_row, data_rows, ncols = parsed
            new = _simple_native_tbl(header_row, data_rows, ncols)
            tbl.getparent().replace(tbl, new)
        # Prune the registry rows for the fields just replaced (match by
        # field_type + target, up to the tallied count), and correct the
        # running counters, so the emitted field_registry.csv agrees with the
        # final package inventory.
        n_removed = dict(removed)
        kept = []
        for row in self.registry:
            key = (row["field_type"], row.get("target", ""))
            if removed.get(key, 0) > 0:
                removed[key] -= 1
                continue
            kept.append(row)
        self.registry = kept
        for (kind, _t), n in n_removed.items():
            if kind in self.counts:
                self.counts[kind] -= n
        self.counts["tables_native"] += len(collapsed)
        print(f"  authored tables: recovered {len(collapsed)} collapsed "
              f"FigureTable grids as native multi-column tables "
              f"(pruned {sum(n_removed.values())} in-cell ref fields)")

    def parts_document_residue(self) -> list[str]:
        xml = etree.tostring(self.doc, encoding="unicode")
        return re.findall(r"@@[A-Z]+(?:![^@!]*)*@@", xml)

    # ---- paragraph-level markers ------------------------------------------
    def _pass_paragraph_markers(self) -> None:
        for p in list(self.body.iter(qn("w:p"))):
            text = self._para_text(p)
            m = MARKER_RE.match(text.strip())
            if not m:
                continue
            tag = m.group(1)
            payload = [s for s in m.group(2).split("!") if s][0:]
            if tag == "NATIVETABLE":
                self._replace_with_native_table(p, payload[0])
            elif tag in ("TABLECAP", "FIGCAP", "ALGCAP"):
                self._decorate_caption(p, tag, payload)
            elif tag == "ALGLINE":
                self._style_algorithm_line(p, payload)
            elif tag == "EQNUM":
                self._number_equation(p, payload[0])
            elif tag == "BIBENT":
                self._style_bib_entry(p, payload)
            elif tag == "SECNUM":
                self._number_heading(p, payload)

    def _strip_marker_from_para(self, p) -> None:
        """Remove the leading marker token from the paragraph's runs."""
        for r in p.iter(qn("w:r")):
            t = r.find(qn("w:t"))
            if t is None or not t.text:
                continue
            if "@@" in t.text:
                t.text = MARKER_RE.sub("", t.text, count=1)
                if not t.text.strip():
                    # drop the empty run and one following space-only run
                    parent = r.getparent()
                    nxt = r.getnext()
                    parent.remove(r)
                    if nxt is not None and nxt.tag == qn("w:r"):
                        nt = nxt.find(qn("w:t"))
                        if nt is not None and (nt.text or "") == " ":
                            parent.remove(nxt)
                return

    def _set_pstyle(self, p, style_id: str) -> None:
        ppr = p.find(qn("w:pPr"))
        if ppr is None:
            ppr = etree.Element(qn("w:pPr"))
            p.insert(0, ppr)
        st = ppr.find(qn("w:pStyle"))
        if st is None:
            st = etree.Element(qn("w:pStyle"))
            ppr.insert(0, st)
        st.set(qn("w:val"), style_id)

    def _first_run_anchor(self, p):
        """Index at which content runs start (after pPr)."""
        for i, child in enumerate(p):
            if child.tag != qn("w:pPr"):
                return i
        return len(p)

    def _decorate_caption(self, p, tag: str, payload: list[str]) -> None:
        label = payload[0]
        kind = {"TABLECAP": ("Table", "Table", self.spec["table_prefix"],
                             "TableCaption"),
                "FIGCAP": ("Figure", "Figure", self.spec["figure_prefix"],
                           "ImageCaption"),
                "ALGCAP": ("Algorithm", "Algorithm", "", "TableCaption")}[tag]
        word, seq_name, letter, style = kind
        self._strip_marker_from_para(p)
        self._set_pstyle(p, style)
        num = self._num_for(label) if label != "-" else "?"
        digits = num[len(letter):] if letter and num.startswith(letter) else num
        runs: list = [make_run(f"{word} ", bold=True)]
        bm_name = None
        if label != "-":
            bm_name = sanitize_bookmark_name(label)
            bid = self._new_bm_id()
            s, e = make_bookmark_pair(bid, bm_name)
            runs.append(s)
            self.counts["bookmarks_added"] += 1
        if letter:
            runs.append(make_run(letter, bold=True))
        runs.extend(self._seq_field(seq_name, digits, bold=True))
        if label != "-":
            runs.append(e)
        runs.append(make_run(". ", bold=True))
        at = self._first_run_anchor(p)
        for r in reversed(runs):
            p.insert(at, r)
        self._log("SEQ", f"SEQ_{seq_name}_{num}", f"SEQ {seq_name}",
                  digits, f"{label} caption")
        if bm_name:
            self._log("BOOKMARK", bm_name, label, num, f"{label} caption")

    def _style_algorithm_line(self, p, payload: list[str]) -> None:
        n, indent = payload[0], int(payload[1]) if len(payload) > 1 else 0
        self._strip_marker_from_para(p)
        self._set_pstyle(p, "AlgorithmLine")
        num_prefix = f"{int(n):>2}: " if n not in ("-", "") else " " * 4
        prefix = num_prefix + " " * (4 * indent)
        p.insert(self._first_run_anchor(p), make_run(prefix))

    def _fix_math_alignment_markers(self) -> int:
        """Replace literal ``&`` math runs left behind by the LaTeX->OMML step.

        ``aligned`` and ``cases`` use ``&`` as an alignment/column marker. A
        plain ``m:oMath`` has no alignment point, so the converter emits the
        marker as an ordinary run and Word renders it as visible text -- Eq. (4)
        shipped as ``junior: u_i &= x_i + ...`` (ticket R-03).

        A single space is the right substitution for both shapes present here:
        ``u_i &= x`` becomes ``u_i  = x``, and in ``cases`` ``value & condition``
        keeps the two sides apart.  Deleting the run outright would be wrong --
        it concatenates the sides of every ``cases`` row.
        """
        n = 0
        for t in self.body.iter(qn("m:t")):
            if (t.text or "").strip() == "&":
                t.text = " "
                n += 1
        if n:
            print(f"[build_docx] math: replaced {n} literal '&' alignment "
                  f"marker(s) with a space (R-03)")
        return n

    def _number_equation(self, p, label: str) -> None:
        prev = p.getprevious()
        # find preceding paragraph containing display math
        while prev is not None and next(prev.iter(qn("m:oMath")), None) is None:
            prev = prev.getprevious()
        if prev is None:
            p.getparent().remove(p)
            return
        # unwrap oMathPara -> inline oMath
        for para_math in list(prev.iter(qn("m:oMathPara"))):
            parent = para_math.getparent()
            idx = list(parent).index(para_math)
            for om in reversed(list(para_math.findall(qn("m:oMath")))):
                parent.insert(idx, om)
            parent.remove(para_math)
        ppr = prev.find(qn("w:pPr"))
        if ppr is None:
            ppr = etree.Element(qn("w:pPr"))
            prev.insert(0, ppr)
        tabs = etree.SubElement(ppr, qn("w:tabs"))
        for pos, kind in ((4819, "center"), (9638, "right")):
            tab = etree.SubElement(tabs, qn("w:tab"))
            tab.set(qn("w:val"), kind)
            tab.set(qn("w:pos"), str(pos))
        # layout: [tab] math [tab] (n)
        first_math = prev.find(qn("m:oMath"))
        if first_math is None:
            first_math = next(prev.iter(qn("m:oMath")))
            while first_math.getparent() is not prev:
                first_math = first_math.getparent()
        idx = list(prev).index(first_math)
        prev.insert(idx, make_tab_run())
        num = self._num_for(label) if label != "-" else "?"
        tail: list = [make_tab_run(), make_run("(")]
        bm_name = None
        if label != "-":
            bm_name = sanitize_bookmark_name(label)
            bid = self._new_bm_id()
            s, e = make_bookmark_pair(bid, bm_name)
            tail.append(s)
            tail.extend(self._seq_field("Equation", num, bold=False))
            tail.append(e)
            self.counts["bookmarks_added"] += 1
        else:
            tail.extend(self._seq_field("Equation", num, bold=False))
        tail.append(make_run(")"))
        for r in tail:
            prev.append(r)
        self._log("SEQ", f"SEQ_Equation_{num}", "SEQ Equation", num,
                  f"{label} display equation")
        if bm_name:
            self._log("BOOKMARK", bm_name, label, num, f"{label} equation")
        p.getparent().remove(p)

    def _style_bib_entry(self, p, payload: list[str]) -> None:
        n = payload[1]
        self._strip_marker_from_para(p)
        self._set_pstyle(p, "Bibliography")
        p.insert(self._first_run_anchor(p), make_run(f"{n}. "))

    def _number_heading(self, p, payload: list[str]) -> None:
        label, num = payload[0], payload[1]
        self._strip_marker_from_para(p)
        runs: list = []
        bm_name = None
        if label != "-":
            bm_name = sanitize_bookmark_name(label)
            bid = self._new_bm_id()
            s, e = make_bookmark_pair(bid, bm_name)
            runs = [s, make_run(num), e, make_tab_run()]
            self.counts["bookmarks_added"] += 1
        else:
            runs = [make_run(num), make_tab_run()]
        at = self._first_run_anchor(p)
        for r in reversed(runs):
            p.insert(at, r)
        if bm_name:
            self._log("BOOKMARK", bm_name, label, num, "section heading")

    def _replace_with_native_table(self, p, table_id: str) -> None:
        tbl, _caption, nrows, ncols = build_native_table(table_id)
        parent = p.getparent()
        parent.insert(list(parent).index(p), tbl)
        parent.remove(p)
        self.counts["tables_native"] += 1
        self._log("NATIVETABLE", f"TBL_{table_id}",
                  f"word_sources/{table_id}.json"
                  if table_id != "T16_bca" else "tables/T16_bca.tex",
                  f"{nrows}x{ncols}", "native w:tbl")

    # ---- inline markers -----------------------------------------------------
    def _pass_inline_markers(self) -> None:
        for r in list(self.doc.iter(qn("w:r"))):
            t = r.find(qn("w:t"))
            if t is None or not t.text or "@@" not in t.text:
                continue
            self._split_marker_run(r, t)

    def _split_marker_run(self, run, t) -> None:
        text = t.text
        parent = run.getparent()
        idx = list(parent).index(run)
        rpr = run.find(qn("w:rPr"))
        new_elems: list = []
        pos = 0
        for m in MARKER_RE.finditer(text):
            if m.start() > pos:
                new_elems.append(self._text_run(text[pos:m.start()], rpr))
            tag = m.group(1)
            payload = [s for s in m.group(2).split("!") if s]
            if tag == "REF":
                new_elems.extend(self._ref_field_runs(payload[0]))
            elif tag == "CITE":
                new_elems.extend(self._cite_field_runs(payload[0]))
            else:
                # unknown inline marker: keep visible for debugging
                new_elems.append(self._text_run(m.group(0), rpr))
            pos = m.end()
        if pos < len(text):
            new_elems.append(self._text_run(text[pos:], rpr))
        for el_ in reversed(new_elems):
            parent.insert(idx, el_)
        parent.remove(run)

    @staticmethod
    def _text_run(text: str, rpr) -> etree._Element:
        r = etree.Element(qn("w:r"))
        if rpr is not None:
            r.append(etree.fromstring(etree.tostring(rpr)))
        t = etree.SubElement(r, qn("w:t"))
        t.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
        t.text = text
        return r

    def _ref_field_runs(self, label: str) -> list:
        bm = sanitize_bookmark_name(label)
        cached = self._num_for(label)
        self.counts["REF"] += 1
        self._log("REF", f"REF_{bm}_{self.counts['REF']:03d}", bm, cached,
                  f"cross-reference to {label}")
        return make_field_runs(f" REF {bm} \\h ", cached)

    def _cite_field_runs(self, keys_csv: str) -> list:
        keys = [k for k in keys_csv.split(",") if k]
        nums = sorted(self.bibnums.get(k, 0) for k in keys)
        cached = "[" + _collapse_ranges(nums) + "]"
        instr = " CITATION " + keys[0] + " \\l 1033 "
        for k in keys[1:]:
            instr += "\\m " + k + " "
        self.counts["CITATION"] += 1
        self._log("CITATION", f"CIT_{self.counts['CITATION']:03d}",
                  ";".join(keys), cached, "in-text citation")
        return make_field_runs(instr, cached)

    # ---- pandoc bookmark normalization --------------------------------------
    _LEGAL_BOOKMARK = re.compile(r"[A-Za-z_][A-Za-z0-9_]{0,39}$")

    def _rename_pandoc_bookmarks(self) -> None:
        """Rename every pandoc-generated bookmark whose name is not
        Word-legal (letters/digits/underscore, letter-initial, <= 40 chars);
        e.g. heading anchors like ``limitations.`` (Phase 9 validator fix)."""
        seen: dict[str, int] = {}
        for bm in self.doc.iter(qn("w:bookmarkStart")):
            name = bm.get(qn("w:name")) or ""
            if self._LEGAL_BOOKMARK.fullmatch(name):
                continue
            new = sanitize_bookmark_name(name, prefix="lbl_")
            if new in seen:
                seen[new] += 1
                new = (new[:36] + f"_{seen[new]}")
            else:
                seen[new] = 0
            bm.set(qn("w:name"), new)

    # ---- alt text ------------------------------------------------------------
    def _pass_alt_text(self) -> None:
        paras = list(self.body.iter(qn("w:p")))
        for i, p in enumerate(paras):
            drawings = list(p.iter(qn("w:drawing")))
            if not drawings:
                continue
            alt = ""
            for j in (i + 1, i + 2):
                if j < len(paras):
                    style = self._para_style(paras[j])
                    if style in ("ImageCaption", "TableCaption", "Caption"):
                        alt = self._para_text(paras[j])
                        break
            if not alt:
                alt = "Figure from the DT-GSK manuscript (see caption in text)."
            for d in drawings:
                for doc_pr in d.iter(qn("wp:docPr")):
                    doc_pr.set("descr", alt[:512])
                    self.counts["images_alt"] += 1

    @staticmethod
    def _para_style(p) -> str:
        ppr = p.find(qn("w:pPr"))
        if ppr is None:
            return ""
        st = ppr.find(qn("w:pStyle"))
        return st.get(qn("w:val")) if st is not None else ""

    # ---- TOC -----------------------------------------------------------------
    def _style_id_by_name(self, wanted: str, fallback: str) -> str:
        styles = parse_xml(self.parts["word/styles.xml"])
        for st in styles.findall(qn("w:style")):
            nm = st.find(qn("w:name"))
            if nm is not None and (nm.get(qn("w:val")) or "").lower() == wanted.lower():
                return st.get(qn("w:styleId"))
        return fallback

    def _insert_toc(self) -> None:
        anchor = None
        for p in self.body.iter(qn("w:p")):
            if self._para_text(p).strip().startswith("Keywords:"):
                anchor = p
                break
        if anchor is None:
            anchor = next(iter(self.body.iter(qn("w:p"))))
        entries = []
        for p in self.body.iter(qn("w:p")):
            style = self._para_style(p)
            if style in ("Heading1", "Heading2", "Heading3"):
                lvl = int(style[-1])
                txt = self._para_text(p).strip()
                if txt:
                    entries.append((lvl, txt))
        toc_heading_id = self._style_id_by_name("TOC Heading", "TOCHeading")
        toc_ids = {i: self._style_id_by_name(f"toc {i}", f"TOC{i}")
                   for i in (1, 2, 3)}
        heading = etree.Element(qn("w:p"))
        ppr = etree.SubElement(heading, qn("w:pPr"))
        st = etree.SubElement(ppr, qn("w:pStyle"))
        st.set(qn("w:val"), toc_heading_id)
        heading.append(make_run("Contents"))
        paras = [heading]
        instr = ' TOC \\o "1-3" \\h \\z \\u '
        for k, (lvl, txt) in enumerate(entries):
            p = etree.Element(qn("w:p"))
            ppr = etree.SubElement(p, qn("w:pPr"))
            st = etree.SubElement(ppr, qn("w:pStyle"))
            st.set(qn("w:val"), toc_ids[lvl])
            if k == 0:
                p.append(make_fldchar_run("begin"))
                r = etree.SubElement(p, qn("w:r"))
                it = etree.SubElement(r, qn("w:instrText"))
                it.set("{http://www.w3.org/XML/1998/namespace}space",
                       "preserve")
                it.text = instr
                p.append(make_fldchar_run("separate"))
            p.append(make_run(txt.replace("\t", " ")))
            if k == len(entries) - 1:
                p.append(make_fldchar_run("end"))
            paras.append(p)
        parent = anchor.getparent()
        at = list(parent).index(anchor) + 1
        for p in reversed(paras):
            parent.insert(at, p)
        self.counts["TOC"] += 1
        self._log("TOC", "TOC_1", 'TOC \\o "1-3"', f"{len(entries)} entries",
                  "after keywords block")

    # ---- settings / customXml -------------------------------------------------
    def _bind_figure_captions(self) -> None:
        # Keep a figure with its caption and a table caption with its table so
        # Word never orphans a caption onto the next page (audit G-015/G-016).
        keepnext = {"CaptionedFigure", "TableCaption"}
        keeplines = {"CaptionedFigure", "ImageCaption", "TableCaption"}
        ppr_tag, pstyle_tag = qn("w:pPr"), qn("w:pStyle")
        for p in self.body.iter(qn("w:p")):
            ppr = p.find(ppr_tag)
            if ppr is None:
                continue
            pstyle = ppr.find(pstyle_tag)
            name = pstyle.get(qn("w:val")) if pstyle is not None else None
            if name is None:
                continue
            idx = list(ppr).index(pstyle) + 1
            if name in keepnext and ppr.find(qn("w:keepNext")) is None:
                ppr.insert(idx, etree.Element(qn("w:keepNext")))
                idx += 1
            if name in keeplines and ppr.find(qn("w:keepLines")) is None:
                ppr.insert(idx, etree.Element(qn("w:keepLines")))

    def _set_hyperlink_style(self) -> None:
        # Match the PDF's hyperref link colour (MDPI blue #0875B7) and drop the
        # underline, on every Hyperlink/FollowedHyperlink character style.
        styles = parse_xml(self.parts["word/styles.xml"])
        for st in styles.findall(qn("w:style")):
            sid = (st.get(qn("w:styleId")) or "").lower()
            nm = st.find(qn("w:name"))
            name = ((nm.get(qn("w:val")) if nm is not None else "") or "").lower()
            if "hyperlink" not in sid and "hyperlink" not in name:
                continue
            rpr = st.find(qn("w:rPr"))
            if rpr is None:
                rpr = etree.SubElement(st, qn("w:rPr"))
            col = rpr.find(qn("w:color"))
            if col is None:
                col = etree.SubElement(rpr, qn("w:color"))
            col.set(qn("w:val"), "0875B7")
            # drop any theme reference so the literal MDPI blue is used, not the
            # document theme's accent colour.
            for attr in ("w:themeColor", "w:themeTint", "w:themeShade"):
                col.attrib.pop(qn(attr), None)
            for u in rpr.findall(qn("w:u")):
                rpr.remove(u)
        self.parts["word/styles.xml"] = serialize_xml(styles)

    def _settings_update_fields(self) -> None:
        # The DOCX must open self-contained on any machine WITHOUT Word's
        # prompt "This document contains fields that may refer to other files.
        # Do you want to update the fields in this document?" -- that prompt is
        # raised by a <w:updateFields w:val="true"/> setting.  Every SEQ, REF,
        # and CITATION field is emitted with its computed cached result (and the
        # document carries no TOC), so no update-on-open is needed; forcing the
        # flag to "false" (and overriding any inherited "true") suppresses the
        # prompt while leaving the document fully readable.
        settings = parse_xml(self.parts["word/settings.xml"])
        existing = settings.find(qn("w:updateFields"))
        if existing is not None:
            existing.set(qn("w:val"), "false")
        else:
            upd = etree.Element(qn("w:updateFields"))
            upd.set(qn("w:val"), "false")
            anchors = [qn("w:hdrShapeDefaults"), qn("w:footnotePr"),
                       qn("w:endnotePr"), qn("w:compat"), qn("w:docVars"),
                       qn("w:rsids"),
                       "{http://schemas.openxmlformats.org/officeDocument/2006/math}mathPr",
                       qn("w:themeFontLang"), qn("w:clrSchemeMapping"),
                       qn("w:decimalSymbol"), qn("w:listSeparator")]
            inserted = False
            for a in anchors:
                node = settings.find(a)
                if node is not None:
                    node.addprevious(upd)
                    inserted = True
                    break
            if not inserted:
                settings.append(upd)
        self.parts["word/settings.xml"] = serialize_xml(settings)

    def _install_citation_store(self) -> None:
        cited = [k for k, _ in sorted(self.bibnums.items(),
                                      key=lambda kv: kv[1])]
        bib = parse_bibtex(ROOT / "references.bib")
        tag_map = load_tag_map()
        sources = build_sources_xml(cited, bib, tag_map)
        self.parts["customXml/item1.xml"] = sources
        self.parts["customXml/itemProps1.xml"] = ITEM_PROPS_XML
        self.parts["customXml/_rels/item1.xml.rels"] = ITEM_RELS_XML
        for name in ("customXml/item1.xml", "customXml/itemProps1.xml",
                     "customXml/_rels/item1.xml.rels"):
            if name not in self.part_order:
                self.part_order.append(name)
        # content types
        ct = parse_xml(self.parts["[Content_Types].xml"])
        CT = NSMAP["ct"]
        have_xml_default = any(
            d.get("Extension") == "xml"
            for d in ct.findall("{%s}Default" % CT))
        if not have_xml_default:
            d = etree.SubElement(ct, "{%s}Default" % CT)
            d.set("Extension", "xml")
            d.set("ContentType", "application/xml")
        if not any(o.get("PartName") == "/customXml/itemProps1.xml"
                   for o in ct.findall("{%s}Override" % CT)):
            o = etree.SubElement(ct, "{%s}Override" % CT)
            o.set("PartName", "/customXml/itemProps1.xml")
            o.set("ContentType",
                  "application/vnd.openxmlformats-officedocument."
                  "customXmlProperties+xml")
        self.parts["[Content_Types].xml"] = serialize_xml(ct)
        # document relationship
        rels = parse_xml(self.parts["word/_rels/document.xml.rels"])
        REL = NSMAP["rel"]
        existing = {r.get("Id") for r in rels.findall("{%s}Relationship" % REL)}
        rid = "rId9001"
        i = 1
        while rid in existing:
            i += 1
            rid = f"rId900{i}"
        r = etree.SubElement(rels, "{%s}Relationship" % REL)
        r.set("Id", rid)
        r.set("Type", "http://schemas.openxmlformats.org/officeDocument/2006/"
                      "relationships/customXml")
        r.set("Target", "../customXml/item1.xml")
        self.parts["word/_rels/document.xml.rels"] = serialize_xml(rels)

    # ---- finalize ---------------------------------------------------------
    def save(self, out_path: Path) -> None:
        self.parts["word/document.xml"] = serialize_xml(self.doc)
        core = self.parts.get("docProps/core.xml")
        if core:
            self.parts["docProps/core.xml"] = stamp_core_props(
                core, creator=self.spec.get("authors", "DT-GSK authors"),
                title=self.spec["title"],
                subject=self.spec.get("subject"),
                keywords=self.spec.get("keywords"))
        ordered = [(n, self.parts[n]) for n in self.part_order
                   if n in self.parts]
        write_deterministic_zip(out_path, ordered)


def _collapse_ranges(nums: list[int]) -> str:
    """MDPI-style collapsed citation list: 1,2  /  7-10 (en dash)."""
    if not nums:
        return "?"
    out = []
    start = prev = nums[0]
    for n in nums[1:] + [None]:
        if n is not None and n == prev + 1:
            prev = n
            continue
        if start == prev:
            out.append(str(start))
        elif prev == start + 1:
            out.append(f"{start},{prev}")
        else:
            out.append(f"{start}–{prev}")
        if n is not None:
            start = prev = n
    return ",".join(out)


# ===========================================================================
# package validation (documented Word-open fallback)
# ===========================================================================

def validate_package(path: Path) -> dict[str, object]:
    report: dict[str, object] = {"file": str(path), "ok": True, "issues": []}
    parts = dict(read_zip_parts(path))
    # 1. all XML parts parse
    for name, data in parts.items():
        if name.endswith((".xml", ".rels")):
            try:
                parse_xml(data)
            except etree.XMLSyntaxError as exc:
                report["ok"] = False
                report["issues"].append(f"XML parse failure in {name}: {exc}")
    doc = parse_xml(parts["word/document.xml"])
    # 2. relationship targets exist
    rels = parse_xml(parts["word/_rels/document.xml.rels"])
    for r in rels.findall("{%s}Relationship" % NSMAP["rel"]):
        target = r.get("Target")
        if r.get("TargetMode") == "External":
            continue
        norm = os.path.normpath(os.path.join("word", target)).replace("\\", "/")
        if norm not in parts:
            report["ok"] = False
            report["issues"].append(f"missing relationship target {norm}")
    # 3. bookmark balance + uniqueness
    starts = [b.get(qn("w:name")) for b in doc.iter(qn("w:bookmarkStart"))]
    ends = list(doc.iter(qn("w:bookmarkEnd")))
    if len(starts) != len(ends):
        report["ok"] = False
        report["issues"].append(
            f"bookmarkStart/End mismatch {len(starts)}/{len(ends)}")
    dupes = {s for s in starts if starts.count(s) > 1}
    if dupes:
        report["ok"] = False
        report["issues"].append(f"duplicate bookmark names: {sorted(dupes)[:5]}")
    # 4. field char balance
    fldchars = [f.get(qn("w:fldCharType")) for f in doc.iter(qn("w:fldChar"))]
    if fldchars.count("begin") != fldchars.count("end"):
        report["ok"] = False
        report["issues"].append("unbalanced fldChar begin/end")
    # 4b. every REF field targets an existing bookmark
    bookmark_names = set(starts)
    for instr in doc.iter(qn("w:instrText")):
        m = re.match(r"\s*REF\s+(\S+)", instr.text or "")
        if m and m.group(1) not in bookmark_names:
            report["ok"] = False
            report["issues"].append(f"REF target missing: {m.group(1)}")
    # 5. content types cover all parts
    ct = parse_xml(parts["[Content_Types].xml"])
    defaults = {d.get("Extension").lower()
                for d in ct.findall("{%s}Default" % NSMAP["ct"])}
    overrides = {o.get("PartName") for o in ct.findall("{%s}Override" % NSMAP["ct"])}
    for name in parts:
        ext = name.rsplit(".", 1)[-1].lower()
        if ("/" + name) not in overrides and ext not in defaults:
            report["ok"] = False
            report["issues"].append(f"no content type for {name}")
    # 6. counts
    xml = etree.tostring(doc, encoding="unicode")
    report["counts"] = {
        "oMath": xml.count("<m:oMath>") + xml.count("<m:oMath "),
        "tables": xml.count("<w:tbl>"),
        "drawings": xml.count("<w:drawing>"),
        "bookmarks": len(starts),
        "fields_begin": fldchars.count("begin"),
        "SEQ": xml.count(" SEQ "),
        "REF": xml.count(" REF "),
        "CITATION": xml.count(" CITATION "),
        "TOC": xml.count(" TOC "),
        "markers_left": len(re.findall(r"@@[A-Z]+", xml)),
    }
    # 7. python-docx can open it
    try:
        import docx  # noqa: F401
        docx.Document(str(path))
    except Exception as exc:   # pragma: no cover - defensive
        report["ok"] = False
        report["issues"].append(f"python-docx open failed: {exc}")
    return report


# ===========================================================================
# field registry
# ===========================================================================

def write_field_registry(rows: list[dict[str, str]], doc_name: str) -> Path:
    path = WORD_DIR / "field_registry.csv"
    existing: list[dict[str, str]] = []
    if path.is_file():
        with open(path, encoding="utf-8", newline="") as fh:
            existing = [r for r in csv.DictReader(fh)
                        if r.get("doc") != doc_name]
    fieldnames = ["doc", "field_type", "field_id", "target",
                  "cached_result", "location"]
    all_rows = existing + rows
    all_rows.sort(key=lambda r: (r["doc"], r["field_type"], r["field_id"]))
    WORD_DIR.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fieldnames)
        w.writeheader()
        for r in all_rows:
            w.writerow({k: r.get(k, "") for k in fieldnames})
    return path


# ===========================================================================
# driver
# ===========================================================================

def build(doc_kind: str) -> int:
    spec = DOC_SPECS[doc_kind]
    if not spec["tex"].is_file():
        print(f"error: {spec['tex']} not found", file=sys.stderr)
        return 1
    reference = WORD_DIR / "reference.docx"
    if not reference.is_file():
        print("word/reference.docx missing -- generating via "
              "make_reference_docx.py")
        subprocess.run([sys.executable,
                        str(SCRIPTS_DIR / "make_reference_docx.py")],
                       check=True)

    pandoc = _resolve_pandoc()
    shim = build_shim(doc_kind)
    spec["shim"].write_text(shim, encoding="utf-8")
    print(f"Wrote pandoc shim -> {spec['shim'].relative_to(REPO_ROOT)}  "
          f"({len(shim):,} chars)")

    tmp_docx = spec["out"].with_suffix(".new.docx")
    if tmp_docx.exists():
        tmp_docx.unlink()
    cmd = [pandoc, spec["shim"].name, "-o", tmp_docx.name,
           "--from=latex", "--to=docx",
           f"--reference-doc={reference}",
           "--resource-path=."]
    print("Running:", " ".join(cmd))
    result = subprocess.run(cmd, cwd=str(ROOT))
    if result.returncode != 0:
        print(f"pandoc exited with status {result.returncode}", file=sys.stderr)
        return result.returncode

    pp = PostProcessor(tmp_docx, doc_kind)
    pp.process()
    pp.save(tmp_docx)

    final_path = spec["out"]
    try:
        os.replace(tmp_docx, final_path)
    except PermissionError:
        final_path = spec["out"].with_name(spec["out"].stem + ".new.docx")
        print(f"  ! {spec['out'].name} locked; kept {final_path.name}",
              file=sys.stderr)

    # Phase D4 (OPT-IN, pending author Visio confirmation): embed the process
    # flowcharts as native Visio OLE objects (double-click-to-edit + extractable
    # from word/embeddings/) instead of raster pictures. Enabled only when
    # VISIO_OLE_FLOWCHARTS is set, so the default (frozen submission) DOCX keeps
    # the known-good PNG flowcharts until the Word/Visio round-trip is confirmed.
    if doc_kind == "main" and os.environ.get("VISIO_OLE_FLOWCHARTS"):
        specs_dir = ROOT / "figures" / "concept" / "flowchart_specs"
        if specs_dir.is_dir():
            from build_visio_flowcharts import build_vsdx
            from embed_visio_ole import embed_ole
            concept = ROOT / "figures" / "concept"
            for _fc in ("gsk", "dtgsk"):
                build_vsdx(specs_dir / f"{_fc}.json", concept / f"flowchart_{_fc}.vsdx")
            embed_ole(final_path, ["gsk", "dtgsk"], final_path)
            print("  visio flowcharts: embedded gsk + dtgsk as editable OLE objects")

    reg_path = write_field_registry(pp.registry, spec["out"].name)
    report = validate_package(final_path)
    print(f"Wrote {final_path.relative_to(REPO_ROOT)}  "
          f"({final_path.stat().st_size:,} bytes)")
    print("  post-process counts:", pp.counts)
    print("  validation:", "OK" if report["ok"] else "FAILED",
          "|", report["counts"])
    if report["issues"]:
        for issue in report["issues"]:
            print("   -", issue)
    print(f"  field registry -> {reg_path.relative_to(REPO_ROOT)}")
    return 0 if report["ok"] else 2


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--supplementary", action="store_true",
                    help="build papers/supplementary.docx instead of the "
                         "main manuscript")
    ap.add_argument("--validate-only", metavar="DOCX",
                    help="run package validation on an existing .docx")
    args = ap.parse_args(argv)
    if args.validate_only:
        report = validate_package(Path(args.validate_only))
        print(json.dumps(report, indent=2))
        return 0 if report["ok"] else 2
    return build("supplementary" if args.supplementary else "main")


if __name__ == "__main__":
    sys.exit(main())
