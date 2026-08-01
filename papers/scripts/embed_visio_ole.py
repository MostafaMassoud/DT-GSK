#!/usr/bin/env python3
"""Embed native Visio (.vsdx) flowcharts into a DOCX as editable OLE objects.

Phase D4 (Tier V-A), step T3. Takes an already-built DOCX whose flowcharts are
raster-PNG pictures and, for each flowchart, replaces the picture <w:drawing>
with a <w:object> OLE wrapper: the .vsdx is embedded under word/embeddings/, the
existing PNG is kept as the in-document preview (so the DOCX still displays
without Visio), and double-clicking the object in Word opens it in Visio. The
.vsdx is extractable directly from the package (word/embeddings/*.vsdx).

Flowcharts are matched to their DOCX image part by CONTENT HASH of the preview
PNG (robust to relationship-id changes). Output is written with the same
deterministic zip as the DOCX build, so byte output is reproducible.

SAFETY: writes a SEPARATE output file (default *_visio.docx); the input DOCX is
untouched. STRUCTURAL validity is checked here; whether Word displays the
preview and Visio opens the object on double-click is the author's manual test.

Usage:
  python papers/scripts/embed_visio_ole.py papers/DT-GSK.docx \
      --flowchart gsk --flowchart dtgsk --out papers/DT-GSK_visio.docx
"""
from __future__ import annotations
import argparse
import hashlib
import re
from pathlib import Path

from _word_ooxml import read_zip_parts, write_deterministic_zip  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
CONCEPT = ROOT / "papers/figures/concept"
# A .vsdx is an OPC PACKAGE (a zip), not a legacy OLE compound-file stream.
#
# This was the defect behind the failed author acceptance test ("the OLE
# flowcharts showed as static images in Word", 2026-07-13, retested and still
# failing 2026-08-01). The embed used the `oleObject` relationship type, under
# which Word expects a legacy compound-file stream (.bin); handed a zip instead
# it cannot activate the object and silently falls back to rendering only the
# preview image -- which is exactly "it is treated as an image".
#
# Modern Office formats (.vsdx/.docx/.xlsx/.pptx) must be attached with the
# `package` relationship type. The <o:OLEObject> markup was always correct
# (Type="Embed", ProgID="Visio.Drawing.15", DrawAspect="Content"); only the
# relationship type was wrong.
OLE_REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/package"
VSDX_CT = "application/vnd.ms-visio.drawing"
EMU_PER_IN = 914400.0


def _sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def _find_media_for(parts, preview_png: bytes):
    want = _sha(preview_png)
    for name, data in parts:
        if name.startswith("word/media/") and _sha(data) == want:
            return name
    return None


def _next_rids(rels_xml: str, k: int):
    nums = [int(m) for m in re.findall(r'Id="rId(\d+)"', rels_xml)]
    start = (max(nums) if nums else 0) + 1
    return [f"rId{start + i}" for i in range(k)]


# Canonical Word picture-frame shapetype for OLE previews. Word recognizes an
# object as an editable OLE (not a static image) only when the preview v:shape
# references this shapetype and carries o:ole. Defined once per document.
_T75 = (
    '<v:shapetype id="_x0000_t75" coordsize="21600,21600" o:spt="75" '
    'o:preferrelative="t" path="m@4@5l@4@11@9@11@9@5xe" filled="f" stroked="f">'
    '<v:stroke joinstyle="miter"/><v:formulas>'
    '<v:f eqn="if lineDrawn pixelLineWidth 0"/><v:f eqn="sum @0 1 0"/>'
    '<v:f eqn="sum 0 0 @1"/><v:f eqn="prod @2 1 2"/>'
    '<v:f eqn="prod @3 21600 pixelWidth"/><v:f eqn="prod @3 21600 pixelHeight"/>'
    '<v:f eqn="sum @0 0 1"/><v:f eqn="prod @6 1 2"/>'
    '<v:f eqn="prod @7 21600 pixelWidth"/><v:f eqn="sum @8 21600 0"/>'
    '<v:f eqn="prod @7 21600 pixelHeight"/><v:f eqn="sum @10 21600 0"/>'
    '</v:formulas><v:path o:extrusionok="f" gradientshapeok="t" o:connecttype="rect"/>'
    '<o:lock v:ext="edit" aspectratio="t"/></v:shapetype>'
)


def _object_xml(shapeid, objid, img_rid, ole_rid, cx_emu, cy_emu, with_shapetype=False):
    dxa = round(cx_emu * 1440 / EMU_PER_IN)
    dya = round(cy_emu * 1440 / EMU_PER_IN)
    w_pt = cx_emu / 12700.0
    h_pt = cy_emu / 12700.0
    return (
        f'<w:object w:dxaOrig="{dxa}" w:dyaOrig="{dya}">'
        f'{_T75 if with_shapetype else ""}'
        f'<v:shape id="{shapeid}" type="#_x0000_t75" '
        f'style="width:{w_pt:.1f}pt;height:{h_pt:.1f}pt" o:ole="">'
        f'<v:imagedata r:id="{img_rid}" o:title=""/></v:shape>'
        f'<o:OLEObject Type="Embed" ProgID="Visio.Drawing.15" ShapeID="{shapeid}" '
        f'DrawAspect="Content" ObjectID="{objid}" r:id="{ole_rid}"/></w:object>'
    )


def _replace_drawing(doc: str, img_rid: str, object_xml: str):
    """Replace the <w:drawing>..</w:drawing> that uses r:embed="img_rid"."""
    marker = f'r:embed="{img_rid}"'
    i = doc.find(marker)
    if i < 0:
        raise SystemExit(f"FAIL: no drawing uses {marker}")
    start = doc.rfind("<w:drawing", 0, i)
    end = doc.find("</w:drawing>", i)
    if start < 0 or end < 0:
        raise SystemExit(f"FAIL: could not bound <w:drawing> for {img_rid}")
    end += len("</w:drawing>")
    # capture extent for sizing
    m = re.search(r'<wp:extent cx="(\d+)" cy="(\d+)"', doc[start:end])
    cx, cy = (int(m.group(1)), int(m.group(2))) if m else (2743200, 2743200)
    return doc[:start] + object_xml + doc[end:], cx, cy


def embed_ole(docx_in, names, docx_out):
    """Embed flowchart_<name>.vsdx into docx_in as editable OLE objects and write
    docx_out (deterministic). Importable from the DOCX build. Returns a list of
    per-flowchart info dicts. Raises SystemExit on any unmet expectation."""
    parts = read_zip_parts(docx_in)
    idx = {n: k for k, (n, _) in enumerate(parts)}
    doc = parts[idx["word/document.xml"]][1].decode("utf-8")
    rels = parts[idx["word/_rels/document.xml.rels"]][1].decode("utf-8")
    ct = parts[idx["[Content_Types].xml"]][1].decode("utf-8")

    new_parts, new_rels, new_overrides, info = [], [], [], []
    ole_rids = _next_rids(rels, len(names))
    for i, (n, ole_rid) in enumerate(zip(names, ole_rids)):
        png = (CONCEPT / f"fig_{n}_flowchart.docx.png").read_bytes()
        vsdx = (CONCEPT / f"flowchart_{n}.vsdx").read_bytes()
        media = _find_media_for(parts, png)
        if media is None:
            raise SystemExit(f"FAIL: no DOCX image matches fig_{n}_flowchart.docx.png")
        rel_target = media.split("word/", 1)[1]                 # media/rIdNN.png
        mm = re.search(r'Id="(rId\d+)"[^>]*Target="' + re.escape(rel_target) + '"', rels) \
            or re.search(r'Target="' + re.escape(rel_target) + r'"[^>]*Id="(rId\d+)"', rels)
        if not mm:
            raise SystemExit(f"FAIL: no relationship targets {rel_target}")
        img_rid = mm.group(1)
        emb = f"word/embeddings/visio_{n}.vsdx"
        shapeid, objid = f"_x0000_i{1026 + i}", f"_{1600000000 + i}"
        obj = _object_xml(shapeid, objid, img_rid, ole_rid, 0, 0, with_shapetype=True)
        doc, cx, cy = _replace_drawing(doc, img_rid, obj)
        doc = doc.replace(
            obj, _object_xml(shapeid, objid, img_rid, ole_rid, cx, cy, with_shapetype=True), 1)
        new_parts.append((emb, vsdx))
        new_rels.append(f'<Relationship Id="{ole_rid}" Type="{OLE_REL}" '
                        f'Target="embeddings/visio_{n}.vsdx"/>')
        new_overrides.append(f'<Override PartName="/{emb}" ContentType="{VSDX_CT}"/>')
        info.append({"name": n, "media": media, "img_rid": img_rid, "emb": emb,
                     "bytes": len(vsdx), "extent": (cx, cy), "ole_rid": ole_rid})

    rels = rels.replace("</Relationships>", "".join(new_rels) + "</Relationships>")
    ct = ct.replace("</Types>", "".join(new_overrides) + "</Types>")
    parts[idx["word/document.xml"]] = ("word/document.xml", doc.encode("utf-8"))
    parts[idx["word/_rels/document.xml.rels"]] = ("word/_rels/document.xml.rels", rels.encode("utf-8"))
    parts[idx["[Content_Types].xml"]] = ("[Content_Types].xml", ct.encode("utf-8"))
    parts.extend(new_parts)
    write_deterministic_zip(docx_out, parts)
    return info


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("docx", help="input DOCX (built with PNG flowcharts)")
    ap.add_argument("--flowchart", action="append", default=[],
                    help="flowchart name (repeat); expects fig_<name>_flowchart.docx.png "
                         "and flowchart_<name>.vsdx in papers/figures/concept/")
    ap.add_argument("--out", default=None, help="output DOCX (default *_visio.docx)")
    args = ap.parse_args(argv)
    names = args.flowchart or ["gsk", "dtgsk"]
    out = Path(args.out) if args.out else Path(args.docx).with_name(Path(args.docx).stem + "_visio.docx")
    for d in embed_ole(args.docx, names, out):
        print(f"  {d['name']}: {d['media']} (rid {d['img_rid']}) -> OLE {d['emb']} "
              f"({d['bytes']} B), extent {d['extent'][0]}x{d['extent'][1]} EMU, ole rel {d['ole_rid']}")
    print(f"Wrote {out} ({Path(out).stat().st_size} bytes)")
    print("  NOTE: open in Microsoft Word; double-click a flowchart -> it should open in Visio "
          "(author acceptance test). Extract with: word/embeddings/visio_<name>.vsdx")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
