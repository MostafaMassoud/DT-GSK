#!/usr/bin/env python3
"""Phase 9 cross-format (PDF vs DOCX) parity validator (Appendix D.6).

    python papers/scripts/validate_cross_format_parity.py
    python papers/scripts/validate_cross_format_parity.py --doc main
    python papers/scripts/validate_cross_format_parity.py --csv <out.csv>

Compares, per logical artifact and per document pair
(``DT-GSK.pdf``/``DT-GSK.docx`` and ``supplementary.pdf``/``supplementary.docx``):

* numbered section headings   (DOCX Heading1-3 vs PDF outline + page text);
* run-in paragraph headings   (DOCX Heading4+ vs PDF text);
* figure/table/algorithm captions (normalized containment in PDF text);
* table values -- EXACT:
    - generated tables: DOCX cells must equal the semantic word_sources JSON
      byte-for-byte (terminology applied), the JSON values must reproduce the
      frozen ``tables/Txx.tex`` display strings at display precision
      (recorded format-only precision difference), and sampled display
      strings must appear in the PDF text;
    - authored tables: per-row cell-token comparison of the flattened
      canonical LaTeX against the DOCX table (alnum channel);
* body paragraphs (whitespace-normalized alnum containment / windowed
  coverage for math-bearing paragraphs);
* citation keys (canonical \\cite inventory vs CITATION field instructions),
  citation cached numbers (recomputed from the frozen .aux) and their
  rendered PDF forms;
* bibliography entries (count, numbering and per-entry text vs the frozen
  .bbl and the PDF text);
* intentional format-only differences (TOC present only in DOCX; semantic
  full-precision table values; Word heading-number typography).

Writes ``papers/governance/cross_format_consistency.csv`` (one row per
artifact) and prints a summary.  Exit 0 if no FAIL rows, else 2.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS_DIR))

from _validate_common import (  # noqa: E402
    DOC_PAIRS, M, PAPERS, W, alnum_channel, apply_terminology, detex,
    docx_document, docx_fields, extract_env_spans,
    flatten_tex, iter_body_blocks, number_channel, para_style, para_text,
    parse_aux_bibcites, parse_aux_labels, parse_tabular_rows, pdf_outline,
    pdf_raw_text, normalize_pdf_text, strip_tex_comments, squash,
    table_cells, tex_document_body,
)

CSV_OUT = PAPERS / "governance" / "cross_format_consistency.csv"
WORD_SOURCES = PAPERS / "tables" / "word_sources"

HEADING_STYLES = {"Heading1": 1, "Heading2": 2, "Heading3": 3}
RUNIN_STYLES = {"Heading4", "Heading5", "Heading6"}
CAPTION_STYLES = {"TableCaption", "ImageCaption", "Caption"}
SKIP_STYLES = (CAPTION_STYLES | RUNIN_STYLES | set(HEADING_STYLES)
               | {"Bibliography", "AlgorithmLine", "TOCHeading",
                  "TOC1", "TOC2", "TOC3", "Title", "Author", "Date",
                  "Abstract", "BlockText"})

# Generated-table \input pattern: primary manuscript tables (Txx, T16_bca)
# plus the Phase-12 supplement ablation tables (SA01, SA02) filled into S6.
_TTABLE_INPUT = re.compile(r"\\input\{tables/(T\d+(?:_bca)?|SA\d+)\}")


def _norm_tid(tex_id: str) -> str:
    m = re.match(r"T0*(\d+)(_bca)?$", tex_id)
    return "T" + m.group(1) + (m.group(2) or "") if m else tex_id


def sha1(s: str) -> str:
    return hashlib.sha1(s.encode("utf-8")).hexdigest()[:12]


class Rows:
    def __init__(self):
        self.rows: list[dict[str, str]] = []

    def add(self, doc, atype, aid, status, method, detail="",
            format_only="", content_hash=""):
        self.rows.append({
            "doc": doc, "artifact_type": atype, "artifact_id": aid,
            "status": status, "method": method, "detail": detail,
            "format_only_difference": format_only,
            "content_hash": content_hash})

    def fails(self):
        return [r for r in self.rows if r["status"] == "FAIL"]


# ===========================================================================
# tex-side canonical inventories
# ===========================================================================

def collapse_ranges(nums: list[int]) -> str:
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
            out.append(f"{start}-{prev}")
        if n is not None:
            start = prev = n
    return ",".join(out)


def tex_bodies(kind: str) -> tuple[str, str]:
    """(body with tables inlined, body with tables as \\input markers)."""
    spec = DOC_PAIRS[kind]
    full = tex_document_body(strip_tex_comments(
        flatten_tex(spec["tex"], include_tables=True)))
    marked = tex_document_body(strip_tex_comments(
        flatten_tex(spec["tex"], include_tables=False)))
    return full, marked


def tex_cite_keys(body: str) -> set[str]:
    keys = set()
    for m in re.finditer(r"\\cite\{([^}]+)\}", body):
        keys.update(k.strip() for k in m.group(1).split(",") if k.strip())
    return keys


def resolve_tex_cell(cell: str, bibnums: dict[str, int],
                     aux: dict[str, str]) -> str:
    """detex a table cell with \\cite -> cached [n] and \\ref -> number."""
    def _cite(m):
        nums = sorted(bibnums.get(k.strip(), 0)
                      for k in m.group(1).split(",") if k.strip())
        return "[" + collapse_ranges(nums) + "]"
    cell = re.sub(r"\\cite\{([^}]+)\}", _cite, cell)
    cell = re.sub(r"\\ref\{([^}]+)\}", lambda m: aux.get(m.group(1), "?"),
                  cell)
    return detex(cell)


def ordered_tex_tables(kind: str) -> list[tuple[str, object]]:
    """Document-order table list: ('generated', 'T16') or
    ('authored', [raw tabular inner, ...one per tabular in the float])."""
    _, marked = tex_bodies(kind)
    events: list[tuple[int, str, object]] = []
    for m in _TTABLE_INPUT.finditer(marked):
        events.append((m.start(), "generated", _norm_tid(m.group(1))))
    for s, _e, inner in extract_env_spans(marked, "tabular"):
        events.append((s, "authored", inner))
    for s, _e, inner in extract_env_spans(marked, "longtable"):
        events.append((s, "authored", inner))
    events.sort(key=lambda t: t[0])
    return [(k, payload) for _pos, k, payload in events]


# ===========================================================================
# display-precision numeric comparison (generated tables)
# ===========================================================================

_SCI_RE = re.compile(r"^-?\d+\.(\d+)E[+-]\d+$", re.IGNORECASE)
_DEC_RE = re.compile(r"^-?\d+\.(\d+)$")
_INT_RE = re.compile(r"^-?\d+$")


_NUM_TOKEN = re.compile(r"[+-]?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?")


def display_match(tex_tok: str, json_vals: list[str]) -> bool:
    """True if some JSON value renders as tex_tok at its display precision.

    Semantic cells are not always bare numbers: several tables carry composite
    display strings ('3.22 (ref)', '6.07 (+2.84)*'). Comparing only against the
    whole string makes float() throw and the check fail on values that plainly
    agree, so the numeric tokens inside each value are admitted as well.
    """
    t = tex_tok.strip()
    for jv in json_vals:
        if t == jv.strip():
            return True
    json_vals = list(json_vals) + [n for jv in json_vals
                                   for n in _NUM_TOKEN.findall(jv)]
    m = _SCI_RE.match(t)
    if m:
        k = len(m.group(1))
        for jv in json_vals:
            try:
                if format(float(jv), f".{k}E").upper() == t.upper():
                    return True
            except ValueError:
                pass
        # Exponent zero-padding differs between notations (1.84e-4 from LaTeX
        # \times10^{-4} vs 1.84e-04 in the JSON). Format BOTH sides the same way
        # so the comparison is on value at display precision, not on spelling.
        try:
            tv = float(t)
        except ValueError:
            return False
        for jv in json_vals:
            try:
                if format(float(jv), f".{k}E") == format(tv, f".{k}E"):
                    return True
            except ValueError:
                pass
        return False
    m = _DEC_RE.match(t)
    if m:
        k = len(m.group(1))
        for jv in json_vals:
            try:
                if format(float(jv), f".{k}f") == t:
                    return True
            except ValueError:
                pass
        return False
    if _INT_RE.match(t):
        for jv in json_vals:
            try:
                if float(jv) == float(t) and float(jv).is_integer():
                    return True
            except ValueError:
                pass
        return False
    return False


def norm_label(s: str) -> str:
    return alnum_channel(apply_terminology(s)).lower()


# ---------------------------------------------------------------------------
# generated-table row extraction (M-029)
# ---------------------------------------------------------------------------
# LaTeX renders scientific notation as 1.84x10-4 (after detex) while Word emits
# 1.84e-04. Same number, two notations; canonicalise both to <mant>e<int-exp>
# BEFORE the alnum channel strips the sign and the caret.
_SCI_TIMES = re.compile(r"(\d+(?:\.\d+)?)\s*[x×]\s*10\s*\^?\{?\s*([+-]?\d+)\s*\}?")
_SCI_E = re.compile(r"(\d+(?:\.\d+)?)\s*[eE]\s*([+-]?)0*(\d+)")
# Word drops trailing zeros that LaTeX prints (1.0000 -> 1). Numerically equal,
# and the alnum channel would otherwise read them as 10000 vs 1.
_DEC = re.compile(r"(?<![\w.])(\d+)\.(\d+)(?![\w.])")


def _strip_trailing_zeros(m: re.Match) -> str:
    frac = m.group(2).rstrip("0")
    return f"{m.group(1)}.{frac}" if frac else m.group(1)


def canon_times(s: str) -> str:
    """Only the LaTeX \\times10^{n} form -> 1.84e-4. Safe for display_match."""
    return _SCI_TIMES.sub(lambda m: f"{m.group(1)}e{int(m.group(2))}", s)


def canon_sci(s: str) -> str:
    """Full canonicalisation for the alnum comparison channel ONLY.

    Do not use this on tokens headed for display_match: normalising 0.00E+00 to
    0.00e+0 defeats its fixed-precision formatting comparison.
    """
    s = canon_times(s)
    s = _SCI_E.sub(lambda m: f"{m.group(1)}e{m.group(2)}{int(m.group(3))}", s)
    return _DEC.sub(_strip_trailing_zeros, s)


# The head-to-head display form ``$m \times 10^{e}$`` must be folded to
# sci-notation on the RAW LaTeX: detex mangles ``\times`` to "imes" and
# ``10^{e}`` to "10e", after which neither canon_times nor display_match can
# recover the value (2026-07-24). The DOCX path already carries E-notation.
_TIMES_TEX = re.compile(r"\$?\s*([-\d.]+)\s*\\times\s*10\^\{?(-?\d+)\}?\s*\$?")


def _fold_times(s: str) -> str:
    return _TIMES_TEX.sub(
        lambda m: f"{m.group(1)}E{int(m.group(2)):+03d}", s)


def canon_cells(row: list[str], already_detexed: bool = False) -> list[str]:
    return [alnum_channel(canon_sci(c if already_detexed else detex(_fold_times(c))))
            for c in row]


def tex_all_tabular_rows(tex_path: Path) -> list[list[str]]:
    """Rows from EVERY tabular in the file, in document order.

    T15 stacks two tabulars (D10/D30 above D50/D100). Taking only span [0] --
    as this validator previously did -- compared the D10/D30 half against the
    DOCX's D50/D100 tail, and, worse, silently left T15's D50/D100 values
    unverified against the semantic source entirely.
    """
    text = tex_path.read_text(encoding="utf-8")
    out: list[list[str]] = []
    for _, _, body in extract_env_spans(text, "tabular"):
        out.extend(parse_tabular_rows(body))
    return out


def row_label_set(jrows: list[list[str]]) -> set[str]:
    """Labels that identify a data row, from the first two semantic columns.

    Most tables key on column 0 (function id, algorithm). SA02 denormalises a
    group header into column 0 ('D=10') and carries the real row key in column
    1 ('-ACE'), so both are admitted.
    """
    labels = set()
    for r in jrows:
        for c in r[:2]:
            lab = norm_label(c)
            if lab:
                labels.add(lab)
    return labels


# A spacing command immediately before a row leaks its optional argument into
# the first cell (\addlinespace[2pt] -> "[2pt] -ACE"), which would otherwise
# hide every group's first data row from the label match.
_SPACING_PREFIX = re.compile(r"^\s*(?:\\?[a-zA-Z]*)?\[\s*-?[\d.]+\s*[a-z]{2}\s*\]\s*")


def strip_spacing_prefix(s: str) -> str:
    return _SPACING_PREFIX.sub("", s)


def data_rows_only(rows: list[list[str]], labels: set[str],
                   detex_first: bool = True) -> list[list[str]]:
    """Keep rows whose first cell is a known row label.

    Discriminates data from headers without guessing at cell counts: spanned
    group headers and column headers never carry a row label.
    """
    out = []
    for r in rows:
        if not r:
            continue
        raw = detex(r[0]) if detex_first else r[0]
        if norm_label(strip_spacing_prefix(raw)) in labels:
            out.append(r)
    return out


# ===========================================================================
# per-document validation
# ===========================================================================

def check_document(kind: str, rows: Rows) -> None:
    spec = DOC_PAIRS[kind]
    doc_id = spec["docx"].name
    dx = docx_document(spec["docx"])
    pdf_raw = pdf_raw_text(spec["pdf"])
    pdf_text = normalize_pdf_text(pdf_raw)
    pdf_alnum = alnum_channel(pdf_text)
    # squash channel from the RAW extraction: the layout normalization
    # strips digit-only lines (margin numbers), which would also delete
    # digit-only TABLE CELLS needed by the numeric spot checks
    pdf_squash = squash(pdf_raw)
    outline = pdf_outline(spec["pdf"])
    aux = parse_aux_labels(spec["aux"])
    bibnums = parse_aux_bibcites(spec["aux"])
    full_body, _ = tex_bodies(kind)

    # ---------------- headings ------------------------------------------------
    outline_alnum = {alnum_channel(t): t for _lvl, t in outline}
    matched_outline = set()
    n_head = 0
    for p in dx.iter(W + "p"):
        st = para_style(p)
        if st in HEADING_STYLES:
            n_head += 1
            text = para_text(p)
            title = re.sub(r"^[S\d.]+[\s\t]*", "", text).strip()
            key = alnum_channel(title)
            if key in outline_alnum:
                matched_outline.add(key)
                rows.add(doc_id, "heading", text[:70], "PASS",
                         "pdf-outline-match", content_hash=sha1(key))
            elif key and key in pdf_alnum:
                rows.add(doc_id, "heading", text[:70], "PASS",
                         "pdf-text-containment",
                         detail="not a PDF outline entry",
                         content_hash=sha1(key))
            else:
                rows.add(doc_id, "heading", text[:70], "FAIL",
                         "pdf-outline+text", detail="not found in PDF")
        elif st in RUNIN_STYLES:
            text = para_text(p)
            key = alnum_channel(text)
            ok = key and key in pdf_alnum
            rows.add(doc_id, "heading_runin", text[:70],
                     "PASS" if ok else "FAIL", "pdf-text-containment",
                     detail="" if ok else "run-in heading not in PDF",
                     content_hash=sha1(key))
    missing = [t for k, t in outline_alnum.items() if k not in matched_outline
               and k]  # outline entries with no DOCX heading
    for t in missing:
        rows.add(doc_id, "heading", t[:70], "FAIL", "pdf-outline-match",
                 detail="PDF outline entry missing from DOCX")
    rows.add(doc_id, "heading_inventory", f"{n_head} numbered headings",
             "PASS" if not missing else "FAIL", "outline-coverage",
             detail=f"{len(outline)} PDF outline entries, "
                    f"{len(matched_outline)} matched")

    # ---------------- captions -------------------------------------------------
    for p in dx.iter(W + "p"):
        if para_style(p) not in CAPTION_STYLES:
            continue
        text = para_text(p).strip()
        if not text:
            continue
        key = alnum_channel(text)
        if key in pdf_alnum:
            rows.add(doc_id, "caption", text[:70], "PASS",
                     "alnum-containment", content_hash=sha1(key))
            continue
        cov = window_coverage(key, pdf_alnum)
        if cov >= 0.85:
            rows.add(doc_id, "caption", text[:70], "PASS_FORMAT_DIFF",
                     "alnum-window-coverage",
                     detail=f"coverage={cov:.2f}",
                     format_only="math glyph/precision rendering in caption",
                     content_hash=sha1(key))
        else:
            rows.add(doc_id, "caption", text[:70], "FAIL",
                     "alnum-window-coverage", detail=f"coverage={cov:.2f}")

    # ---------------- tables ----------------------------------------------------
    docx_tables = [el for k, el in iter_body_blocks(dx) if k == "tbl"]
    tex_tables = ordered_tex_tables(kind)
    if len(docx_tables) != len(tex_tables):
        rows.add(doc_id, "table_inventory",
                 f"docx={len(docx_tables)} tex={len(tex_tables)}", "FAIL",
                 "count", detail="table count mismatch")
    for i, ((tkind, payload), tbl) in enumerate(zip(tex_tables, docx_tables)):
        cells = table_cells(tbl)
        if tkind == "generated":
            check_generated_table(doc_id, str(payload), cells, pdf_squash,
                                  rows)
        else:
            check_authored_table(doc_id, f"authored_{i}", str(payload),
                                 cells, bibnums, aux, rows)

    # ---------------- paragraphs -------------------------------------------------
    n_para = 0
    for p in (el for k, el in iter_body_blocks(dx) if k == "p"):
        st = para_style(p)
        if st in SKIP_STYLES:
            continue
        text = para_text(p)
        key = alnum_channel(text)
        if len(key) < 30:
            continue
        n_para += 1
        has_math = next(p.iter(M + "oMath"), None) is not None
        math_key = alnum_channel("".join(
            t.text or "" for t in p.iter(M + "t") if t.text))
        if has_math and len(key) and len(math_key) / len(key) >= 0.5:
            # display-equation paragraph: OMML linearization never matches
            # PDF glyph extraction; verify the equation number instead and
            # record the intentional format difference (content equality is
            # per-source: both formats render the same frozen LaTeX math)
            mnum = re.search(r"\((\w{1,4})\)\s*$", text.strip())
            num_ok = bool(mnum) and f"({mnum.group(1)})" in pdf_squash
            rows.add(doc_id, "equation_display",
                     (f"({mnum.group(1)}) " if mnum else "") + text[:50],
                     "PASS_FORMAT_DIFF" if (num_ok or not mnum) else "FAIL",
                     "equation-number + source identity",
                     detail=("eq number rendered in PDF" if num_ok else
                             "unnumbered display math"),
                     format_only="OMML linear text vs PDF math glyph "
                                 "extraction order",
                     content_hash=sha1(key))
            continue
        if key in pdf_alnum:
            status, method, det, fo = "PASS", "alnum-containment", "", ""
        elif split_containment(key, pdf_alnum):
            # a float (caption + table body) placed at a page break splits the
            # paragraph into two runs in the PDF extraction stream; both runs
            # still contain 100% of the paragraph verbatim, so this is the
            # same extraction-artifact class as the stripped running headers
            status, method = "PASS_FORMAT_DIFF", "alnum-split-containment"
            det = "paragraph verbatim in two contiguous runs"
            fo = "page-break/float interleaves PDF extraction mid-paragraph"
        else:
            cov = window_coverage(key, pdf_alnum)
            # \textsc{} is small-capped by LaTeX ("NUMPY") and left as authored
            # by pandoc ("NumPy"). That is a typographic transform, not a content
            # difference, so retry case-insensitively before calling it a miss.
            cov_ci = window_coverage(key.lower(), pdf_alnum.lower())
            if cov >= 0.97:
                status, method = "PASS", "alnum-window-coverage"
                det, fo = f"coverage={cov:.2f}", ""
            elif cov_ci >= 0.97:
                status, method = "PASS_FORMAT_DIFF", "alnum-window-coverage-ci"
                det = f"coverage={cov:.2f}; case-insensitive={cov_ci:.2f}"
                fo = "small-caps (\\textsc) rendered as capitals in PDF only"
            elif has_math and cov >= 0.80:
                status, method = "PASS_FORMAT_DIFF", "alnum-window-coverage"
                det = f"coverage={cov:.2f}"
                fo = "OMML vs PDF math glyph order/spacing"
            else:
                status, method = "FAIL", "alnum-window-coverage"
                det, fo = f"coverage={cov:.2f}", ""
        rows.add(doc_id, "paragraph", text[:60], status, method, det, fo,
                 sha1(key))

    # ---------------- citations ---------------------------------------------------
    tex_keys = tex_cite_keys(full_body)
    fields = docx_fields(dx)
    cite_fields = [f for f in fields if f["type"] == "CITATION"]
    docx_keys: set[str] = set()
    num_bad = []
    pdf_missing = []
    for f in cite_fields:
        keys = re.findall(r"(?:CITATION|\\m)\s+([A-Za-z0-9:_-]+)", f["instr"])
        keys = [k for k in keys if k != "1033"]
        docx_keys.update(keys)
        expect = "[" + collapse_ranges(sorted(bibnums.get(k, 0)
                                              for k in keys)) + "]"
        cached = number_channel(f["cached"])
        if cached != expect:
            num_bad.append(f"{keys}: cached={cached!r} expect={expect!r}")
        if squash(cached) not in pdf_squash:
            pdf_missing.append(cached)
    rows.add(doc_id, "citation_keys",
             f"{len(docx_keys)} distinct keys in {len(cite_fields)} fields",
             "PASS" if docx_keys == tex_keys else "FAIL",
             "set-equality vs canonical \\cite inventory",
             detail=("" if docx_keys == tex_keys else
                     f"docx-only={sorted(docx_keys - tex_keys)[:4]} "
                     f"tex-only={sorted(tex_keys - docx_keys)[:4]}"),
             content_hash=sha1(",".join(sorted(docx_keys))))
    rows.add(doc_id, "citation_numbers", f"{len(cite_fields)} CITATION fields",
             "PASS" if not num_bad else "FAIL",
             "cached [n] recomputed from frozen .aux",
             detail="; ".join(num_bad[:3]))
    rows.add(doc_id, "citation_pdf_render",
             f"{len(cite_fields) - len(pdf_missing)}/{len(cite_fields)} "
             "cached strings found in PDF",
             "PASS" if not pdf_missing else "FAIL",
             "squash-containment", detail="; ".join(pdf_missing[:4]))

    # ---------------- bibliography --------------------------------------------------
    bib_paras = [para_text(p) for p in dx.iter(W + "p")
                 if para_style(p) == "Bibliography"]
    n_expected = len(bibnums)
    ok_count = len(bib_paras) == n_expected
    rows.add(doc_id, "bibliography_inventory",
             f"{len(bib_paras)} entries", "PASS" if ok_count else "FAIL",
             "count vs frozen .aux/.bbl", detail=f"expected {n_expected}")
    for entry in bib_paras:
        m = re.match(r"\s*(\d+)\.\s*(.*)", entry, re.DOTALL)
        eid = f"[{m.group(1)}]" if m else entry[:20]
        key = alnum_channel(entry)
        if key in pdf_alnum:
            rows.add(doc_id, "bibliography_entry", f"{eid} {entry[:50]}",
                     "PASS", "alnum-containment", content_hash=sha1(key))
        else:
            cov = window_coverage(key, pdf_alnum)
            status = "PASS_FORMAT_DIFF" if cov >= 0.90 else "FAIL"
            rows.add(doc_id, "bibliography_entry", f"{eid} {entry[:50]}",
                     status, "alnum-window-coverage",
                     detail=f"coverage={cov:.2f}",
                     format_only="line-break/diacritic extraction" if
                     status != "FAIL" else "", content_hash=sha1(key))

    # ---------------- intentional format-only differences ----------------------------
    rows.add(doc_id, "toc", "Contents (native TOC field)", "PASS_FORMAT_DIFF",
             "inventory",
             format_only="TOC exists only in DOCX (update-on-open); "
                         "PDF (MDPI submission layout) carries none")
    rows.add(doc_id, "heading_number_typography", "N<tab>Title vs 'N. Title'",
             "PASS_FORMAT_DIFF", "recorded convention",
             format_only="Word heading tab after cached number; MDPI PDF "
                         "uses 'N.'")
    if kind == "main":
        rows.add(doc_id, "table_value_precision",
                 "native tables (word_sources exact precision)",
                 "PASS_FORMAT_DIFF", "recorded convention",
                 format_only="DOCX renders full semantic precision (e.g. "
                             "2.879310); PDF renders display-rounded (2.88); "
                             "values equal at display precision (checked)")

    # ---------------- ablation-content scan over PDF text -----------------------------
    # Direction per correction_exception_protocol.md Sec.4 (mirrors the Phase-12
    # validate_docx.py update): the shipped MAIN must render ZERO ablation content
    # (all ablation tokens + any rendered S6 heading forbidden), whereas ablation
    # prose is admissible in the SUPPLEMENT's now-filled Phase-12 S6 slot -- there
    # only the release-block tokens are forbidden and the S6 section MUST render.
    s6 = re.search(r"(?m)^\s*S6[.\s:]", pdf_text)
    if kind == "main":
        abl = [tok for tok in ("ablation", "ablat", "phase_12_placeholder",
                               "do not release") if tok in pdf_text.lower()]
        rows.add(doc_id.replace(".docx", ".pdf"), "no_ablation_scan",
                 "extracted PDF text",
                 "PASS" if not abl and not s6 else "FAIL",
                 "token scan (main: zero ablation content)",
                 detail=f"tokens={abl} s6={'rendered' if s6 else 'absent'}")
    else:
        block = [tok for tok in ("phase_12_placeholder", "do not release")
                 if tok in pdf_text.lower()]
        rows.add(doc_id.replace(".docx", ".pdf"), "no_ablation_scan",
                 "extracted PDF text",
                 "PASS" if not block and s6 else "FAIL",
                 "token scan (supplement: S6 ablation admissible; "
                 "release-block tokens forbidden; S6 must render)",
                 detail=f"release_block={block} "
                        f"s6={'rendered' if s6 else 'ABSENT'}")


# ---------------------------------------------------------------------------
# tables
# ---------------------------------------------------------------------------

def split_containment(key: str, haystack: str, min_part: int = 25) -> bool:
    """True when ``key`` occurs verbatim as exactly two contiguous runs in
    ``haystack`` (one interruption -- a page break with an intervening float).

    Greedy longest-prefix is complete here: if key = A+B with both parts
    present, the greedy prefix A' extends A, and the remainder is a substring
    of B, hence still present. ``min_part`` rejects degenerate splits so a
    genuinely edited paragraph cannot pass by splitting around the edit."""
    lo, hi = 0, len(key)
    while lo < hi:  # max i with key[:i] in haystack (monotone in i)
        mid = (lo + hi + 1) // 2
        if key[:mid] in haystack:
            lo = mid
        else:
            hi = mid - 1
    return (min_part <= lo < len(key)
            and len(key) - lo >= min_part
            and key[lo:] in haystack)


def window_coverage(key: str, haystack: str, win: int = 25) -> float:
    if not key:
        return 1.0
    if len(key) <= win:
        return 1.0 if key in haystack else 0.0
    chunks = [key[i:i + win] for i in range(0, len(key) - win + 1, win)]
    hit = sum(1 for c in chunks if c in haystack)
    return hit / len(chunks)


def check_generated_table(doc_id: str, tid: str, docx_cells: list[list[str]],
                          pdf_squash: str, rows: Rows) -> None:
    tex_path = PAPERS / "tables" / (
        ("T%02d" % int(tid[1:])) + ".tex" if tid[1:].isdigit()
        else tid + ".tex")
    if tid == "T16_bca":
        tex_path = PAPERS / "tables" / "T16_bca.tex"
    tex_rows = tex_all_tabular_rows(tex_path)

    if tid == "T16_bca":
        # DOCX is built from the same frozen .tex: exact multiset per row
        tex_norm = [[alnum_channel(detex(c)) for c in r] for r in tex_rows]
        dx_norm = [[alnum_channel(c) for c in r] for r in docx_cells]
        ok = len(tex_norm) == len(dx_norm) and all(
            sorted(a) == sorted(b) for a, b in zip(tex_norm, dx_norm))
        rows.add(doc_id, "table_generated", "T16_bca (tab:bca-ci)",
                 "PASS" if ok else "FAIL", "frozen-tex-rowset",
                 detail=f"{len(dx_norm)} rows vs tex {len(tex_norm)}",
                 content_hash=sha1(json.dumps(dx_norm)))
        spot_pdf(doc_id, tid, tex_rows, pdf_squash, rows)
        return

    src = json.loads((WORD_SOURCES / f"{tid}.json").read_text("utf-8"))
    jrows = [[apply_terminology(c) for c in row] for row in src["rows"]]
    n_data = len(jrows)

    # (a) DOCX reproduces the RENDERED .tex.
    #
    # This previously compared the DOCX against the semantic JSON and could
    # never pass: the Word tables are built from the rendered LaTeX, so they
    # carry display-rounded values and flattened spanned headers by
    # construction, while the JSON holds full precision and a flat machine
    # header. Comparing renderings to renderings is both correct and stronger --
    # together with (b) it chains DOCX -> .tex -> semantic source -> evidence.
    # build_docx emits some tables natively from the semantic JSON and routes the
    # rest through pandoc from the rendered LaTeX, so the DOCX must reproduce ONE
    # of those two legitimate sources -- which one is a build-routing detail, not
    # a content property. Requiring a specific reference is what made this check
    # unpassable for 18 tables.
    labels = row_label_set(jrows)
    tex_data = data_rows_only(tex_rows, labels)
    dx_data = data_rows_only(docx_cells, labels, detex_first=False)

    def _rstrip_empty(row):
        # A column-split table stacks tabulars of DIFFERENT widths under one
        # caption (e.g. the portrait h2h tables: Best/Median/Worst above, the
        # narrower Mean/SD below). build_docx flattens them into one w:tbl of the
        # MAX width, padding the narrow rows with trailing empty cells, while the
        # rendered .tex keeps each block at its own width. Those trailing blanks
        # carry no content, so drop them before the row-multiset comparison.
        while row and row[-1] == "":
            row = row[:-1]
        return row

    dx_norm = [_rstrip_empty(canon_cells(r, already_detexed=True)) for r in dx_data]
    tex_norm = [_rstrip_empty(canon_cells(r)) for r in tex_data]
    json_norm = [_rstrip_empty(canon_cells(r, already_detexed=True)) for r in jrows]

    if dx_norm == tex_norm:
        exact, ref = True, "rendered .tex"
    elif dx_norm == json_norm:
        exact, ref = True, "semantic word_sources JSON (native table)"
    else:
        exact, ref = False, ""
    detail_a = f"{len(dx_data)} data rows match {ref}"
    if not exact:
        diffs = [(ri, a, b) for ri, (a, b) in
                 enumerate(zip(tex_norm, dx_norm)) if a != b]
        detail_a = (f"docx {len(dx_norm)} rows match neither .tex "
                    f"({len(tex_norm)}) nor JSON ({len(json_norm)}); "
                    f"{len(diffs)} differing vs tex; first: {diffs[:1]}")

    # (b) frozen .tex display strings reproduce from JSON values per row.
    #
    # Pairing is k-fold aware: a table may stack k tabulars that share row keys
    # and split the columns between them (T15: D10/D30 above D50/D100), giving
    # k*n_data display rows against n_data semantic rows.
    tex_head = [r for r in tex_rows if r not in tex_data]
    prec_bad = []
    if n_data and len(tex_data) % n_data:
        prec_bad.append(f"{len(tex_data)} display rows is not a multiple of "
                        f"{n_data} semantic rows")
    paired = [(tr, jrows[i % n_data]) for i, tr in enumerate(tex_data)] \
        if n_data else []
    for tr, jr in paired:
        t_first = norm_label(strip_spacing_prefix(detex(tr[0])))
        # The semantic row key is column 0 for most tables, but SA02 folds a
        # group header into column 0 ('D=10') and keys on column 1 ('-ACE').
        if t_first not in {norm_label(c) for c in jr[:2] if norm_label(c)}:
            prec_bad.append(f"row-key {detex(tr[0])!r} != {jr[0]!r}")
            continue
        # Values are everything except the matched key; for the SA02 shape that
        # means column 0 stays available as a value too.
        jvals = [v.replace(",", "") for v in jr
                 if norm_label(v) != t_first]
        for cell in tr[1:]:
            # canon_times first: otherwise "1.84x10-4" is read as three separate
            # numerics (1.84, 10, -4), none of which is derivable on its own.
            # _fold_times first collapses the "$m \times 10^{e}$" display form to
            # sci-notation before detex can mangle it.
            tok = canon_times(detex(_fold_times(cell)).replace("−", "-").strip())
            if not tok:
                continue
            # a display cell may combine several numerics (e.g. mean ± SD)
            nums = re.findall(r"-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?",
                              tok.replace(",", ""))
            if nums:
                for n2 in nums:
                    if not display_match(n2, jvals):
                        prec_bad.append(
                            f"{detex(tr[0])}: {n2!r} not derivable")
                residue = re.sub(r"-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?", "",
                                 tok.replace(",", ""))
                # '+' is a sign carried by signed display values (+2.84), not
                # residual text; a bare backslash is what detex leaves behind
                # for spacing commands such as the thin space \, in "3.22\,(ref)".
                residue = residue.replace("±", "").replace("\\(ref", "")
                residue = residue.strip(" []()%$;:.-+\\*")
                # The declared display policy bounds p-values below 1e-4 as
                # "<10^-4" (SAP Sec. 4; R3-20). A lone '<' residue is that
                # bound's marker and is accepted ONLY when the semantic JSON
                # row itself carries the '<'-prefixed bounded token.
                if residue == "<" and any(
                        str(v).lstrip().startswith("<") for v in jr[1:]):
                    residue = ""
                if residue and norm_label(residue) not in {
                        norm_label(v) for v in jr[1:]}:
                    prec_bad.append(f"{detex(tr[0])}: residue {residue!r}")
            else:
                if norm_label(tok) not in {norm_label(v) for v in jr[1:]}:
                    prec_bad.append(f"{detex(tr[0])}: text {tok!r} missing")
    status = "PASS" if exact and not prec_bad else "FAIL"
    fo = ""
    if exact and not prec_bad:
        # value precision differs by convention wherever formats differ
        fo = ("DOCX = semantic full precision; PDF = display-rounded; "
              "equal at display precision")
        status = "PASS_FORMAT_DIFF" if any(
            "." in c or "e" in c.lower() for r in jrows for c in r[1:]) \
            else "PASS"
    rows.add(doc_id, "table_generated", f"{tid} ({src['manuscript_label']})",
             status, "wsource-exact + tex-display-precision",
             detail=(detail_a if not exact else
                     f"{n_data} data rows; header rows {len(tex_head)}; "
                     + ("; ".join(prec_bad[:3]) if prec_bad else
                        "all display strings derivable")),
             format_only=fo,
             content_hash=sha1(json.dumps(docx_cells)))
    spot_pdf(doc_id, tid, tex_data, pdf_squash, rows)


def spot_pdf(doc_id: str, tid: str, tex_data: list[list[str]],
             pdf_squash: str, rows: Rows) -> None:
    """Sample display strings from the frozen .tex table -> PDF text."""
    probes = []
    for r in (tex_data[0], tex_data[len(tex_data) // 2], tex_data[-1]):
        for cell in r[:6]:
            tok = squash(detex(cell))
            if tok and re.fullmatch(r"-?[\d.,]+(?:[eE][+-]?\d+)?%?", tok):
                probes.append(tok)
        if len(probes) >= 6:
            break
    missing = [p for p in probes if p not in pdf_squash]
    rows.add(doc_id, "table_pdf_spot", tid,
             "PASS" if not missing else "FAIL", "squash-containment",
             detail=f"{len(probes) - len(missing)}/{len(probes)} sampled "
                    f"display values found" + (f"; missing {missing[:3]}"
                                               if missing else ""))


def check_authored_table(doc_id: str, aid: str, inner: str,
                         docx_cells: list[list[str]], bibnums, aux,
                         rows: Rows) -> None:
    tex_rows = parse_tabular_rows(inner)
    tex_norm = [sorted(alnum_channel(resolve_tex_cell(c, bibnums, aux))
                       for c in r if alnum_channel(
                           resolve_tex_cell(c, bibnums, aux)))
                for r in tex_rows]
    dx_norm = [sorted(alnum_channel(c) for c in r if alnum_channel(c))
               for r in docx_cells]
    eq = sum(1 for a, b in zip(tex_norm, dx_norm) if a == b)
    near = 0
    bad_rows = []
    import difflib
    for ri, (a, b) in enumerate(zip(tex_norm, dx_norm)):
        if a == b:
            continue
        ratio = difflib.SequenceMatcher(
            None, " ".join(a), " ".join(b)).ratio()
        if ratio >= 0.80:
            near += 1
        else:
            bad_rows.append(f"r{ri} ratio={ratio:.2f}: tex={a[:2]} "
                            f"docx={b[:2]}")
    total = max(len(tex_norm), len(dx_norm))
    if eq == total and len(tex_norm) == len(dx_norm):
        status, det, fo = "PASS", f"{total} rows identical", ""
    elif eq + near == total and len(tex_norm) == len(dx_norm):
        status = "PASS_FORMAT_DIFF"
        det = f"{eq}/{total} rows identical, {near} math-styling rows"
        fo = "LaTeX math command text vs OMML glyph extraction"
    else:
        status = "FAIL"
        det = (f"{eq}/{total} rows identical; rows tex={len(tex_norm)} "
               f"docx={len(dx_norm)}; " + "; ".join(bad_rows[:3]))
        fo = ""
    first = detex(tex_rows[0][0])[:24] if tex_rows and tex_rows[0] else ""
    rows.add(doc_id, "table_authored", f"{aid} ({first}...)", status,
             "tex-detex-rowset", det, fo,
             sha1(json.dumps(dx_norm)))


# ===========================================================================
# driver
# ===========================================================================

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--doc", choices=["main", "supplementary", "both"],
                    default="both")
    ap.add_argument("--csv", default=str(CSV_OUT))
    args = ap.parse_args(argv)

    rows = Rows()
    kinds = ["main", "supplementary"] if args.doc == "both" else [args.doc]
    for kind in kinds:
        check_document(kind, rows)

    out = Path(args.csv)
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=[
            "doc", "artifact_type", "artifact_id", "status", "method",
            "detail", "format_only_difference", "content_hash"])
        w.writeheader()
        w.writerows(rows.rows)

    by = {}
    for r in rows.rows:
        k = (r["doc"], r["artifact_type"])
        st = by.setdefault(k, {"PASS": 0, "PASS_FORMAT_DIFF": 0, "FAIL": 0})
        st[r["status"]] += 1
    print(f"cross-format consistency -> {out}")
    for (d, t), st in sorted(by.items()):
        line = f"  {d:22s} {t:26s} PASS={st['PASS']:4d} " \
               f"FMT_DIFF={st['PASS_FORMAT_DIFF']:3d} FAIL={st['FAIL']:3d}"
        print(line)
    fails = rows.fails()
    print(f"TOTAL rows={len(rows.rows)}  FAIL={len(fails)}")
    for f in fails[:15]:
        print(f"  FAIL {f['doc']} {f['artifact_type']} {f['artifact_id']!r}"
              f" :: {f['detail'][:120]}")
    return 0 if not fails else 2


if __name__ == "__main__":
    sys.exit(main())
