#!/usr/bin/env python3
# Copyright (c) 2026 Mostafa Masoud <moustafa.masoud@gmail.com>
"""Deep structural validation of the Visio drawings and the OLE-embedded DOCX.

Why this exists
---------------
Phase D4 produced two generators -- ``build_visio_flowcharts.py`` (spec ->
``.vsdx``) and ``embed_visio_ole.py`` (DOCX + ``.vsdx`` -> editable OLE DOCX) --
and left acceptance resting on a manual test: open it in Word, double-click a
flowchart, confirm Visio loads it without offering to repair. That test needs
Microsoft Visio, which no CI or agent environment here has, so D4 sat open
indefinitely with nothing verifying it.

Most of what "Visio repairs the file" actually means is OPC structural damage:
a relationship pointing at a part that is not in the package, a part whose
extension no content type declares, a page referencing a missing page part, a
dangling ``r:id``. Those ARE checkable without Visio, and the shipped
``--check`` did not check them -- it verified only that five named parts exist
and that the XML parses.

This script closes that gap. It does not, and cannot, prove Visio renders the
drawing; it proves the package is not malformed in the ways that make Visio
refuse it. What remains after a clean run is a rendering question, not an
integrity one.

Checks, per .vsdx
-----------------
1. required OPC parts present; every XML part well-formed;
2. every relationship Target resolves to a real part (the dangling-target
   failure mode);
3. [Content_Types].xml covers every part, by Default extension or Override;
4. the Visio 2012/2013 main namespace is declared on document.xml;
5. every page in pages.xml resolves to a page part via its relationship;
6. shape and connector counts match the source spec.

Checks, for the OLE DOCX
------------------------
7. every <w:object> carries an OLE r:id that resolves to a relationship whose
   Target exists in the package;
8. each embedded .vsdx is byte-identical to its tracked source drawing;
9. each embedded .vsdx independently passes checks 1-5;
10. the preview image r:id resolves (so Word shows something without Visio);
11. the package declares a content type for the vsdx extension.

Exit 0 if every check passes, 1 otherwise.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

PAPERS = Path(__file__).resolve().parent.parent
CONCEPT = PAPERS / "figures" / "concept"
SPECS = CONCEPT / "flowchart_specs"
VNS = "http://schemas.microsoft.com/office/visio/2012/main"
R_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"

_problems: list[str] = []


def fail(msg: str) -> None:
    _problems.append(msg)
    print(f"  FAIL  {msg}")


def ok(msg: str) -> None:
    print(f"  ok    {msg}")


def _rels_for(names: set[str], part: str) -> str:
    """Path of the .rels part governing `part` ('' for the package root)."""
    if not part:
        return "_rels/.rels"
    p = Path(part)
    return f"{p.parent.as_posix()}/_rels/{p.name}.rels".lstrip("/")


def check_opc(z: zipfile.ZipFile, label: str, required: set[str]) -> bool:
    names = set(z.namelist())
    good = True

    missing = required - names
    if missing:
        fail(f"{label}: missing required part(s) {sorted(missing)}")
        good = False

    # every XML part parses
    for n in names:
        if n.endswith(".xml") or n.endswith(".rels"):
            try:
                ET.fromstring(z.read(n))
            except ET.ParseError as e:
                fail(f"{label}: {n} is not well-formed XML ({e})")
                good = False

    # every relationship target resolves
    for n in names:
        if not n.endswith(".rels"):
            continue
        base = Path(n).parent.parent.as_posix()
        base = "" if base == "." else base
        try:
            root = ET.fromstring(z.read(n))
        except ET.ParseError:
            continue
        for rel in root:
            tgt = rel.get("Target", "")
            mode = rel.get("TargetMode", "Internal")
            if mode == "External" or tgt.startswith(("http:", "https:")):
                continue
            resolved = tgt.lstrip("/") if tgt.startswith("/") else (
                f"{base}/{tgt}" if base else tgt)
            # normalise ../
            parts: list[str] = []
            for seg in resolved.split("/"):
                if seg == "..":
                    if parts:
                        parts.pop()
                elif seg not in ("", "."):
                    parts.append(seg)
            resolved = "/".join(parts)
            if resolved not in names:
                fail(f"{label}: {n} -> relationship {rel.get('Id')} targets "
                     f"'{tgt}' which is not in the package")
                good = False

    # content types cover every part
    if "[Content_Types].xml" in names:
        ct = ET.fromstring(z.read("[Content_Types].xml"))
        defaults = {e.get("Extension", "").lower()
                    for e in ct if e.tag.endswith("Default")}
        overrides = {e.get("PartName", "").lstrip("/")
                     for e in ct if e.tag.endswith("Override")}
        for n in names:
            if n == "[Content_Types].xml":
                continue
            ext = n.rsplit(".", 1)[-1].lower() if "." in n else ""
            if n not in overrides and ext not in defaults:
                fail(f"{label}: no content type declared for '{n}' "
                     f"(extension '{ext}')")
                good = False
    return good


def check_vsdx(path: Path, spec: Path | None = None) -> bool:
    label = path.name
    if not path.is_file():
        fail(f"{label}: file not found")
        return False
    with zipfile.ZipFile(path) as z:
        if z.testzip() is not None:
            fail(f"{label}: zip integrity failure")
            return False
        good = check_opc(z, label, {
            "[Content_Types].xml", "_rels/.rels", "visio/document.xml",
            "visio/pages/pages.xml", "visio/pages/page1.xml"})

        doc = ET.fromstring(z.read("visio/document.xml"))
        if not doc.tag.startswith(f"{{{VNS}}}"):
            fail(f"{label}: visio/document.xml is not in the Visio 2012 main "
                 f"namespace (root tag {doc.tag})")
            good = False

        # pages resolve
        pages = ET.fromstring(z.read("visio/pages/pages.xml"))
        prels_name = "visio/pages/_rels/pages.xml.rels"
        prels = {}
        if prels_name in z.namelist():
            for rel in ET.fromstring(z.read(prels_name)):
                prels[rel.get("Id")] = rel.get("Target")
        n_pages = 0
        for page in pages:
            n_pages += 1
            for child in page.iter():
                rid = child.get(f"{{{R_NS}}}id")
                if rid and rid not in prels:
                    fail(f"{label}: page references r:id {rid} with no "
                         f"relationship in pages.xml.rels")
                    good = False
        if n_pages == 0:
            fail(f"{label}: pages.xml declares no pages")
            good = False

        if spec and spec.is_file():
            s = json.loads(spec.read_text(encoding="utf-8"))
            want = len(s.get("nodes", [])) + len(s.get("edges", []))
            page1 = z.read("visio/pages/page1.xml").decode("utf-8")
            got = page1.count("<Shape ")
            if got != want:
                fail(f"{label}: page1 has {got} shapes, spec declares "
                     f"{want} (nodes+edges)")
                good = False
            else:
                ok(f"{label}: {got} shapes match spec ({spec.name})")
    if good:
        ok(f"{label}: OPC structure, relationships, content types and "
           f"namespace all valid")
    return good


def check_ole_docx(path: Path) -> bool:
    label = path.name
    if not path.is_file():
        print(f"  SKIP  {label} not present (build it with embed_visio_ole.py)")
        return True
    with zipfile.ZipFile(path) as z:
        names = set(z.namelist())
        if z.testzip() is not None:
            fail(f"{label}: zip integrity failure")
            return False
        good = check_opc(z, label, {"[Content_Types].xml", "_rels/.rels",
                                    "word/document.xml"})

        rels = {}
        rel_types = {}
        for rel in ET.fromstring(z.read("word/_rels/document.xml.rels")):
            rels[rel.get("Id")] = rel.get("Target")
            rel_types[rel.get("Id")] = rel.get("Type", "")

        # An OPC-package embed (.vsdx/.docx/.xlsx/.pptx) must be attached with
        # the `package` relationship type. Under `oleObject` Word expects a
        # legacy compound-file stream (.bin), cannot activate a zip, and falls
        # back to rendering the preview image only -- the object appears as a
        # static picture and double-click does nothing. That is precisely the
        # defect that failed the author acceptance test twice, and this
        # validator passed the broken package until this check was added.
        OPC_EXT = (".vsdx", ".docx", ".xlsx", ".pptx")
        for rid, tgt in rels.items():
            if tgt and tgt.lower().endswith(OPC_EXT):
                kind = rel_types.get(rid, "").rsplit("/", 1)[-1]
                if kind != "package":
                    fail(f"{label}: '{tgt}' is an OPC package but is attached "
                         f"with relationship type '{kind}' -- Word cannot "
                         f"activate it and will show the preview image only; "
                         f"it must be 'package'")
                    good = False

        doc = z.read("word/document.xml").decode("utf-8")
        objects = re.findall(r"<w:object\b.*?</w:object>", doc, re.S)
        if not objects:
            fail(f"{label}: no <w:object> OLE wrappers found")
            return False

        embedded = 0
        for obj in objects:
            for rid in re.findall(r'r:id="([^"]+)"', obj):
                tgt = rels.get(rid)
                if tgt is None:
                    fail(f"{label}: OLE r:id {rid} has no relationship")
                    good = False
                    continue
                full = f"word/{tgt.lstrip('/')}"
                if full not in names:
                    fail(f"{label}: r:id {rid} targets '{tgt}', absent from "
                         f"the package")
                    good = False
                elif full.endswith(".vsdx"):
                    embedded += 1
                    name = Path(full).stem.replace("visio_", "")
                    src = CONCEPT / f"flowchart_{name}.vsdx"
                    if src.is_file():
                        a = hashlib.sha256(z.read(full)).hexdigest()
                        b = hashlib.sha256(src.read_bytes()).hexdigest()
                        if a != b:
                            fail(f"{label}: embedded {full} differs from the "
                                 f"tracked {src.name}")
                            good = False
                        else:
                            ok(f"{label}: {full} is byte-identical to "
                               f"{src.name}")
            # preview image must resolve so Word shows something without Visio
            for rid in re.findall(r'r:embed="([^"]+)"', obj):
                if rid not in rels:
                    fail(f"{label}: preview image r:id {rid} has no "
                         f"relationship")
                    good = False

        ct = z.read("[Content_Types].xml").decode("utf-8")
        if "vsdx" not in ct.lower():
            fail(f"{label}: [Content_Types].xml declares no type for .vsdx")
            good = False

        if embedded == 0:
            fail(f"{label}: no .vsdx found among the OLE targets")
            good = False
        elif good:
            ok(f"{label}: {len(objects)} OLE object(s), {embedded} embedded "
               f"drawing(s), all relationships resolve")
    return good


def main() -> int:
    print("Visio drawings")
    for spec in sorted(SPECS.glob("*.json")):
        check_vsdx(CONCEPT / f"flowchart_{spec.stem}.vsdx", spec)
        # each embedded copy is validated again inside the DOCX below
    print("\nOLE-embedded DOCX")
    for cand in (PAPERS / "DT-GSK_visio.docx",):
        check_ole_docx(cand)
        if cand.is_file():
            with zipfile.ZipFile(cand) as z:
                for n in z.namelist():
                    if n.startswith("word/embeddings/") and n.endswith(".vsdx"):
                        tmp = Path(cand.parent / f"._chk_{Path(n).name}")
                        tmp.write_bytes(z.read(n))
                        try:
                            check_vsdx(tmp)
                        finally:
                            tmp.unlink(missing_ok=True)

    print()
    if _problems:
        print(f"FAIL: {len(_problems)} problem(s)")
        return 1
    print("PASS: every machine-checkable property holds.")
    print("NOTE: this proves the packages are not malformed in the ways that "
          "make Visio offer to repair a file. It does not prove Visio RENDERS "
          "the drawing as intended -- that remains a visual check, and it is "
          "not a submission dependency (the OLE DOCX is excluded from the "
          "package, C-001 5.4).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
