#!/usr/bin/env python3
"""Generate ``word/reference.docx`` -- the pandoc style template (Phase 9).

The template is created programmatically: pandoc's built-in default
``reference.docx`` (obtained via ``pandoc --print-default-data-file``) is used
only as the *style-name skeleton* that the pandoc docx writer requires; every
visual property is then (re)stated in code with python-docx / lxml:

* A4 page, 2.0 cm side / 2.5 cm top-bottom margins (MDPI-like companion);
* serif body: Palatino Linotype 10 pt (named, NOT embedded -- no proprietary
  font embedding; Word falls back per its own font substitution table);
* Heading 1-3 (12/10.5/10 pt bold family), Title/Author/Abstract front matter;
* Caption styles (``Table Caption`` / ``Image Caption`` / ``Caption``) 9 pt,
  captions editable text;
* monospace code/algorithm styles (``Source Code``, ``Verbatim Char``, plus a
  dedicated ``Algorithm Line`` paragraph style used by the pseudocode block);
* ``Bibliography`` (References) style with hanging indent;
* table style ``Table`` with a shaded, bold header row (firstRow conditional
  formatting);
* TOC Heading / TOC 1-3 styles for the native TOC field.

Output is deterministically packaged (fixed zip metadata + docProps
timestamps from SOURCE_DATE_EPOCH; see ``_word_ooxml``).

Usage
-----
    python papers/scripts/make_reference_docx.py
"""
from __future__ import annotations

import io
import os
import shutil
import subprocess
import sys
from pathlib import Path

from docx import Document
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.shared import Cm, Pt
from lxml import etree

SCRIPTS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS_DIR))

from _word_ooxml import (  # noqa: E402
    qn,
    read_zip_parts,
    stamp_core_props,
    write_deterministic_zip,
)

REPO_ROOT = SCRIPTS_DIR.parent.parent  # repo root (papers/..)
OUT_PATH = REPO_ROOT / "word" / "reference.docx"

BODY_FONT = "Palatino Linotype"
MONO_FONT = "Consolas"

_PANDOC_USER_WIN = Path(
    os.environ.get("LOCALAPPDATA", r"C:\Users\moust\AppData\Local")
) / "Pandoc" / "pandoc.exe"


def _resolve_pandoc() -> str:
    on_path = shutil.which("pandoc")
    if on_path:
        return on_path
    if _PANDOC_USER_WIN.is_file():
        return str(_PANDOC_USER_WIN)
    raise FileNotFoundError("pandoc not found")


def _default_reference_bytes() -> bytes:
    out = subprocess.run(
        [_resolve_pandoc(), "--print-default-data-file", "reference.docx"],
        capture_output=True, check=True,
    )
    return out.stdout


def _font(style, name: str, size_pt: float | None = None, *, bold=None,
          italic=None, color=None):
    f = style.font
    f.name = name
    if size_pt is not None:
        f.size = Pt(size_pt)
    if bold is not None:
        f.bold = bold
    if italic is not None:
        f.italic = italic
    if color is not None:
        f.color.rgb = color
    # east-asian + complex-script bindings so Word does not substitute
    rpr = style.element.get_or_add_rPr()
    rfonts = rpr.find(qn("w:rFonts"))
    if rfonts is None:
        rfonts = etree.SubElement(rpr, qn("w:rFonts"))
    for attr in ("w:ascii", "w:hAnsi", "w:cs"):
        rfonts.set(qn(attr), name)


def _pf(style, *, before=None, after=None, line=None, keep_next=None,
        align=None, left_indent=None, hanging=None, space_exact=False):
    pf = style.paragraph_format
    if before is not None:
        pf.space_before = Pt(before)
    if after is not None:
        pf.space_after = Pt(after)
    if line is not None:
        pf.line_spacing = line
        pf.line_spacing_rule = WD_LINE_SPACING.MULTIPLE
    if keep_next is not None:
        pf.keep_with_next = keep_next
    if align is not None:
        pf.alignment = align
    if left_indent is not None:
        pf.left_indent = Cm(left_indent)
    if hanging is not None:
        pf.first_line_indent = Cm(-hanging)
    if space_exact:
        pf.widow_control = True


def _ensure_paragraph_style(doc, name: str, style_id: str | None = None):
    try:
        return doc.styles[name]
    except KeyError:
        st = doc.styles.add_style(name, WD_STYLE_TYPE.PARAGRAPH)
        if style_id:
            st.element.set(qn("w:styleId"), style_id)
        return st


def _style_table_header_shading(doc) -> None:
    """Give the pandoc ``Table`` table style a shaded bold header row."""
    styles_el = doc.styles.element
    tbl_style = None
    for st in styles_el.findall(qn("w:style")):
        if st.get(qn("w:styleId")) == "Table":
            tbl_style = st
            break
    if tbl_style is None:
        return
    # remove any prior firstRow conditional format, then add ours
    for prior in tbl_style.findall(qn("w:tblStylePr")):
        if prior.get(qn("w:type")) == "firstRow":
            tbl_style.remove(prior)
    xml = (
        '<w:tblStylePr xmlns:w="http://schemas.openxmlformats.org/'
        'wordprocessingml/2006/main" w:type="firstRow">'
        '<w:pPr><w:keepNext/><w:spacing w:before="20" w:after="20"/></w:pPr>'
        "<w:rPr><w:b/></w:rPr>"
        '<w:tcPr><w:shd w:val="clear" w:color="auto" w:fill="E7E6E6"/>'
        "<w:tcBorders>"
        '<w:top w:val="single" w:sz="8" w:space="0" w:color="000000"/>'
        '<w:bottom w:val="single" w:sz="4" w:space="0" w:color="000000"/>'
        "</w:tcBorders></w:tcPr>"
        "</w:tblStylePr>"
    )
    tbl_style.append(etree.fromstring(xml))


def build_reference_docx() -> bytes:
    base = _default_reference_bytes()
    doc = Document(io.BytesIO(base))

    # ---- page geometry: A4, MDPI-like companion margins ------------------
    sec = doc.sections[0]
    sec.page_width = Cm(21.0)
    sec.page_height = Cm(29.7)
    sec.left_margin = Cm(2.0)
    sec.right_margin = Cm(2.0)
    sec.top_margin = Cm(2.5)
    sec.bottom_margin = Cm(2.5)
    sec.header_distance = Cm(1.25)
    sec.footer_distance = Cm(1.25)

    styles = doc.styles

    # ---- body text --------------------------------------------------------
    # MDPI mdpi.cls: 10pt Palatino (mathpazo), justified body.
    normal = styles["Normal"]
    _font(normal, BODY_FONT, 10)
    _pf(normal, before=0, after=4, line=1.15, align=WD_ALIGN_PARAGRAPH.JUSTIFY)

    for nm in ("Body Text", "First Paragraph", "Compact"):
        try:
            st = styles[nm]
        except KeyError:
            continue
        _font(st, BODY_FONT, 10)
        if nm == "Compact":
            _pf(st, before=0, after=0, line=1.0)
        else:
            _pf(st, before=0, after=4, line=1.15,
                align=WD_ALIGN_PARAGRAPH.JUSTIFY)

    # ---- headings ---------------------------------------------------------
    # MDPI mdpi.cls exact: section 10pt BOLD, subsection 10pt ITALIC,
    # subsubsection 10pt regular, paragraph 10pt regular (all left-aligned /
    # raggedright). (size, bold, italic, space_before, space_after)
    heading_spec = {
        "Heading 1": (10, True, False, 12, 4),
        "Heading 2": (10, False, True, 10, 4),
        "Heading 3": (10, False, False, 8, 4),
        "Heading 4": (10, False, False, 8, 4),
    }
    for nm, (size, bold, italic, before, after) in heading_spec.items():
        try:
            st = styles[nm]
        except KeyError:
            continue
        _font(st, BODY_FONT, size, bold=bold, italic=italic)
        _pf(st, before=before, after=after, keep_next=True)
        # neutralize themed heading colour (pandoc default is blue-ish)
        rpr = st.element.get_or_add_rPr()
        for col in rpr.findall(qn("w:color")):
            rpr.remove(col)

    # ---- front matter -----------------------------------------------------
    for nm, size, bold, align in (
        ("Title", 18, True, WD_ALIGN_PARAGRAPH.LEFT),  # mdpi.cls \fontsize{18}
        ("Author", 11, True, WD_ALIGN_PARAGRAPH.LEFT),
        ("Date", 10, False, WD_ALIGN_PARAGRAPH.LEFT),
        ("Abstract Title", 10, True, WD_ALIGN_PARAGRAPH.LEFT),
        ("Abstract", 9.5, False, WD_ALIGN_PARAGRAPH.JUSTIFY),
    ):
        try:
            st = styles[nm]
        except KeyError:
            continue
        _font(st, BODY_FONT, size, bold=bold)
        _pf(st, align=align)

    # ---- captions (editable text; 9 pt; table captions keep-with-next) ----
    for nm in ("Caption", "Table Caption", "Image Caption"):
        try:
            st = styles[nm]
        except KeyError:
            st = _ensure_paragraph_style(doc, nm)
        _font(st, BODY_FONT, 9, bold=False, italic=False)
        _pf(st, before=6, after=6, keep_next=(nm != "Image Caption"),
            align=WD_ALIGN_PARAGRAPH.JUSTIFY)

    # ---- code / algorithm -------------------------------------------------
    for nm in ("Source Code",):
        try:
            st = styles[nm]
            _font(st, MONO_FONT, 9)
            _pf(st, before=0, after=0, line=1.0)
        except KeyError:
            pass
    try:
        st = styles["Verbatim Char"]
        _font(st, MONO_FONT, 9)
    except KeyError:
        pass
    alg = _ensure_paragraph_style(doc, "Algorithm Line", "AlgorithmLine")
    _font(alg, MONO_FONT, 9)
    _pf(alg, before=0, after=0, line=1.0)

    # ---- bibliography ------------------------------------------------------
    try:
        bib = styles["Bibliography"]
    except KeyError:
        bib = _ensure_paragraph_style(doc, "Bibliography")
    _font(bib, BODY_FONT, 9)
    _pf(bib, before=0, after=3, left_indent=0.75, hanging=0.75,
        align=WD_ALIGN_PARAGRAPH.JUSTIFY)

    # ---- TOC styles --------------------------------------------------------
    try:
        toch = styles["TOC Heading"]
    except KeyError:
        toch = _ensure_paragraph_style(doc, "TOC Heading", "TOCHeading")
    _font(toch, BODY_FONT, 12, bold=True)
    _pf(toch, before=12, after=6, keep_next=True)
    for i in (1, 2, 3):
        nm = f"toc {i}"
        try:
            st = styles[nm]
        except KeyError:
            st = _ensure_paragraph_style(doc, nm, f"TOC{i}")
        _font(st, BODY_FONT, 10 if i == 1 else 9.5)
        _pf(st, before=0, after=2, left_indent=0.5 * (i - 1))

    # ---- section-number character style (used on heading numbers) ---------
    try:
        styles["Section Number"]
    except KeyError:
        sn = doc.styles.add_style("Section Number", WD_STYLE_TYPE.CHARACTER)
        sn.element.set(qn("w:styleId"), "SectionNumber")

    _style_table_header_shading(doc)

    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()


def main() -> int:
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    raw = build_reference_docx()

    # deterministic re-package + docProps normalization
    parts = read_zip_parts(io.BytesIO(raw))
    fixed: list[tuple[str, bytes]] = []
    for name, data in parts:
        if name == "docProps/core.xml":
            data = stamp_core_props(
                data,
                creator="DT-GSK Phase 9 Word pipeline",
                title="DT-GSK Word reference template",
            )
        fixed.append((name, data))
    write_deterministic_zip(OUT_PATH, fixed)
    print(f"Wrote {OUT_PATH.relative_to(REPO_ROOT)}  "
          f"({OUT_PATH.stat().st_size:,} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
