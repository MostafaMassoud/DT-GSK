#!/usr/bin/env python3
"""Shared OOXML primitives for the Phase 9 Word pipeline.

Used by ``build_docx.py`` (shim + post-processing build) and
``make_reference_docx.py`` (style template generator).  Everything here is
deliberately dependency-light: ``lxml`` when available, falling back to the
stdlib ``xml.etree`` API is *not* attempted -- lxml 6.x is a recorded part of
the Phase 9 toolchain.

Key services
------------
* WordprocessingML namespace table + ``qn()`` helper.
* Run/field/bookmark element factories (SEQ / REF / CITATION / TOC complex
  fields with cached results, per ECMA-376 ``w:fldChar`` semantics).
* Deterministic DOCX (re)zipping: fixed entry order, fixed timestamps from
  ``SOURCE_DATE_EPOCH``, fixed compression -- the Section 9.4 determinism
  contract normalizes docProps timestamps *and* zip metadata.
"""
from __future__ import annotations

import datetime as _dt
import os
import zipfile
from typing import Iterable

from lxml import etree

NSMAP = {
    "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
    "m": "http://schemas.openxmlformats.org/officeDocument/2006/math",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "wp": "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing",
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "pic": "http://schemas.openxmlformats.org/drawingml/2006/picture",
    "ct": "http://schemas.openxmlformats.org/package/2006/content-types",
    "rel": "http://schemas.openxmlformats.org/package/2006/relationships",
    "cp": "http://schemas.openxmlformats.org/package/2006/metadata/core-properties",
    "dc": "http://purl.org/dc/elements/1.1/",
    "dcterms": "http://purl.org/dc/terms/",
    "xsi": "http://www.w3.org/2001/XMLSchema-instance",
    "b": "http://schemas.openxmlformats.org/officeDocument/2006/bibliography",
    "ds": "http://schemas.openxmlformats.org/officeDocument/2006/customXml",
}

# Fixed fallback build epoch: 2026-07-10T00:00:00Z (evidence release date).
DEFAULT_SOURCE_DATE_EPOCH = 1783641600


def qn(tag: str) -> str:
    """``w:p`` -> ``{ns}p`` Clark notation."""
    prefix, local = tag.split(":", 1)
    return "{%s}%s" % (NSMAP[prefix], local)


def source_date_epoch() -> int:
    raw = os.environ.get("SOURCE_DATE_EPOCH", "").strip()
    if raw.isdigit():
        return int(raw)
    return DEFAULT_SOURCE_DATE_EPOCH


def epoch_iso8601(epoch: int | None = None) -> str:
    if epoch is None:
        epoch = source_date_epoch()
    return _dt.datetime.fromtimestamp(epoch, _dt.timezone.utc).strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )


def epoch_zip_datetime(epoch: int | None = None) -> tuple[int, int, int, int, int, int]:
    if epoch is None:
        epoch = source_date_epoch()
    t = _dt.datetime.fromtimestamp(epoch, _dt.timezone.utc)
    # zip stores local DOS time; clamp to >= 1980
    year = max(t.year, 1980)
    return (year, t.month, t.day, t.hour, t.minute, t.second)


# ---------------------------------------------------------------------------
# Element factories
# ---------------------------------------------------------------------------

def el(tag: str, attrib: dict[str, str] | None = None, text: str | None = None):
    e = etree.Element(qn(tag))
    for k, v in (attrib or {}).items():
        if ":" in k:
            e.set(qn(k), v)
        else:
            e.set(qn("w:" + k) if not k.startswith("{") else k, v)
    if text is not None:
        e.text = text
    return e


def make_run(text: str, *, bold: bool = False, italic: bool = False,
             rstyle: str | None = None, sz_half_pt: int | None = None):
    r = etree.Element(qn("w:r"))
    if bold or italic or rstyle or sz_half_pt:
        rpr = etree.SubElement(r, qn("w:rPr"))
        if rstyle:
            s = etree.SubElement(rpr, qn("w:rStyle"))
            s.set(qn("w:val"), rstyle)
        if bold:
            etree.SubElement(rpr, qn("w:b"))
        if italic:
            etree.SubElement(rpr, qn("w:i"))
        if sz_half_pt:
            sz = etree.SubElement(rpr, qn("w:sz"))
            sz.set(qn("w:val"), str(sz_half_pt))
    t = etree.SubElement(r, qn("w:t"))
    t.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
    t.text = text
    return r


def make_tab_run():
    r = etree.Element(qn("w:r"))
    etree.SubElement(r, qn("w:tab"))
    return r


def make_fldchar_run(fld_type: str):
    r = etree.Element(qn("w:r"))
    f = etree.SubElement(r, qn("w:fldChar"))
    f.set(qn("w:fldCharType"), fld_type)
    return r


def make_instr_run(instr: str):
    r = etree.Element(qn("w:r"))
    i = etree.SubElement(r, qn("w:instrText"))
    i.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
    i.text = instr
    return r


def make_field_runs(instr: str, cached_result: str | Iterable[etree._Element],
                    *, result_bold: bool = False) -> list[etree._Element]:
    """Complex field: begin / instrText / separate / cached result / end."""
    runs = [
        make_fldchar_run("begin"),
        make_instr_run(instr),
        make_fldchar_run("separate"),
    ]
    if isinstance(cached_result, str):
        runs.append(make_run(cached_result, bold=result_bold))
    else:
        runs.extend(cached_result)
    runs.append(make_fldchar_run("end"))
    return runs


def make_bookmark_pair(bm_id: int, name: str) -> tuple[etree._Element, etree._Element]:
    s = etree.Element(qn("w:bookmarkStart"))
    s.set(qn("w:id"), str(bm_id))
    s.set(qn("w:name"), name)
    e = etree.Element(qn("w:bookmarkEnd"))
    e.set(qn("w:id"), str(bm_id))
    return s, e


def sanitize_bookmark_name(label: str, prefix: str = "ref_") -> str:
    """Word bookmark names: letters/digits/underscore, start with a letter,
    <= 40 chars.  Stable across builds (pure function of the label)."""
    out = []
    for ch in label:
        out.append(ch if (ch.isalnum() and ord(ch) < 128) else "_")
    name = prefix + "".join(out)
    name = name.strip("_")
    if not name or not name[0].isalpha():
        name = "b" + name
    return name[:40]


# ---------------------------------------------------------------------------
# XML (de)serialisation
# ---------------------------------------------------------------------------

def parse_xml(data: bytes) -> etree._Element:
    return etree.fromstring(data)


def serialize_xml(root: etree._Element) -> bytes:
    return etree.tostring(root, xml_declaration=True, encoding="UTF-8",
                          standalone=True)


# ---------------------------------------------------------------------------
# Deterministic packaging
# ---------------------------------------------------------------------------

def stamp_core_props(core_xml: bytes, *, creator: str, title: str,
                     subject: str | None = None,
                     keywords: str | None = None) -> bytes:
    """Normalize docProps/core.xml timestamps + identity to fixed values."""
    root = parse_xml(core_xml)
    iso = epoch_iso8601()

    def _set(tag: str, text: str, w3cdtf: bool = False):
        node = root.find(qn(tag))
        if node is None:
            node = etree.SubElement(root, qn(tag))
        node.text = text
        if w3cdtf:
            node.set(qn("xsi:type"), "dcterms:W3CDTF")

    _set("dcterms:created", iso, w3cdtf=True)
    _set("dcterms:modified", iso, w3cdtf=True)
    _set("dc:creator", creator)
    _set("cp:lastModifiedBy", creator)
    _set("dc:title", title)
    if subject:
        _set("dc:subject", subject)
    if keywords:
        _set("cp:keywords", keywords)
    # revision fixed for determinism
    rev = root.find(qn("cp:revision"))
    if rev is not None:
        rev.text = "1"
    return serialize_xml(root)


def write_deterministic_zip(out_path: str | os.PathLike,
                            parts: list[tuple[str, bytes]]) -> None:
    """Write a docx zip with fixed metadata.

    ``parts`` order is preserved ([Content_Types].xml must come first);
    timestamps, permissions and compression are fixed so byte output is a
    pure function of ``parts`` + SOURCE_DATE_EPOCH.
    """
    zdt = epoch_zip_datetime()
    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for name, data in parts:
            info = zipfile.ZipInfo(filename=name, date_time=zdt)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 0  # fixed (MS-DOS) regardless of host OS
            info.external_attr = 0o600 << 16
            zf.writestr(info, data, compresslevel=6)


def read_zip_parts(path: str | os.PathLike) -> list[tuple[str, bytes]]:
    with zipfile.ZipFile(path) as zf:
        return [(i.filename, zf.read(i.filename)) for i in zf.infolist()]
