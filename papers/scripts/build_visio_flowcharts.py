#!/usr/bin/env python3
"""Generate a native Microsoft Visio (.vsdx) drawing from a flowchart spec.

Phase D4 (Tier V-A), step T2. Reads a flowchart_specs/*.json (the single source
of truth for a process flowchart) and emits a standalone, editable Visio 2013+
drawing: terminals (rounded), process / bold-outlined ISM-added rectangles, a
decision diamond, and arrowed connectors including the loop-back route. The
package is written with a DETERMINISTIC zip (fixed timestamps) so byte output is
a pure function of the spec + SOURCE_DATE_EPOCH.

NOTE: VSDX validity is verified STRUCTURALLY here (OPC parts present, XML
well-formed, zip integrity). Confirming that Microsoft Visio opens and edits it
without repair requires Visio, which is not in this environment -- that is the
author's manual acceptance test (see the plan, Phase D4).

Usage:
  python papers/scripts/build_visio_flowcharts.py papers/figures/concept/flowchart_specs/dtgsk.json
  python papers/scripts/build_visio_flowcharts.py <spec> --out <path.vsdx>
  python papers/scripts/build_visio_flowcharts.py <spec> --check   # structural self-test only
"""
from __future__ import annotations
import argparse
import datetime as _dt
import json
import os
import zipfile
from pathlib import Path
from xml.sax.saxutils import escape

VNS = "http://schemas.microsoft.com/office/visio/2012/main"
RNS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
PT = 1.0 / 72.0  # points -> inches


# --------------------------------------------------------------------------- #
# deterministic packaging
# --------------------------------------------------------------------------- #
def _zip_dt():
    raw = os.environ.get("SOURCE_DATE_EPOCH", "").strip()
    epoch = int(raw) if raw.isdigit() else 1783641600
    t = _dt.datetime.fromtimestamp(epoch, _dt.timezone.utc)
    return (max(t.year, 1980), t.month, t.day, t.hour, t.minute, t.second)


def write_vsdx(out_path, parts):
    zdt = _zip_dt()
    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for name, data in parts:
            info = zipfile.ZipInfo(filename=name, date_time=zdt)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 0
            info.external_attr = 0o600 << 16
            zf.writestr(info, data if isinstance(data, bytes) else data.encode("utf-8"),
                        compresslevel=6)


# --------------------------------------------------------------------------- #
# geometry helpers
# --------------------------------------------------------------------------- #
def _node_centers(spec):
    L = spec["layout"]
    out = {}
    for n in spec["nodes"]:
        out[n["id"]] = {
            "cx": L["spine_cx"] + n.get("dx", 0.0),
            "cy": L["top_y"] - n["level"] * L["pitch"],
            "w": spec["sizes"][n["type"]]["w"],
            "h": spec["sizes"][n["type"]]["h"],
            "type": n["type"],
            "text": n["text"],
        }
    return out


def _fmt(x):
    return f"{x:.4f}".rstrip("0").rstrip(".") if isinstance(x, float) else str(x)


# --------------------------------------------------------------------------- #
# shape XML
# --------------------------------------------------------------------------- #
def _cell(n, v, f=None):
    v = _fmt(v)
    return f'<Cell N="{n}" V="{v}"' + (f' F="{escape(f)}"' if f else "") + "/>"


def _rect_geom(w, h):
    p = [(0, 0), (w, 0), (w, h), (0, h), (0, 0)]
    rows = [f'<Row T="{"MoveTo" if i == 0 else "LineTo"}" IX="{i+1}">'
            f'<Cell N="X" V="{_fmt(x)}"/><Cell N="Y" V="{_fmt(y)}"/></Row>'
            for i, (x, y) in enumerate(p)]
    return ('<Section N="Geometry" IX="0"><Cell N="NoFill" V="0"/>'
            '<Cell N="NoLine" V="0"/>' + "".join(rows) + "</Section>")


def _diamond_geom(w, h):
    p = [(w / 2, 0), (w, h / 2), (w / 2, h), (0, h / 2), (w / 2, 0)]
    rows = [f'<Row T="{"MoveTo" if i == 0 else "LineTo"}" IX="{i+1}">'
            f'<Cell N="X" V="{_fmt(x)}"/><Cell N="Y" V="{_fmt(y)}"/></Row>'
            for i, (x, y) in enumerate(p)]
    return ('<Section N="Geometry" IX="0"><Cell N="NoFill" V="0"/>'
            '<Cell N="NoLine" V="0"/>' + "".join(rows) + "</Section>")


def _poly_geom(pts_local):
    rows = [f'<Row T="{"MoveTo" if i == 0 else "LineTo"}" IX="{i+1}">'
            f'<Cell N="X" V="{_fmt(x)}"/><Cell N="Y" V="{_fmt(y)}"/></Row>'
            for i, (x, y) in enumerate(pts_local)]
    return ('<Section N="Geometry" IX="0"><Cell N="NoFill" V="1"/>'
            '<Cell N="NoLine" V="0"/>' + "".join(rows) + "</Section>")


def _char_para(size_in):
    return (f'<Section N="Character"><Row IX="0"><Cell N="Size" V="{_fmt(size_in)}"/>'
            f'<Cell N="Color" V="#000000"/></Row></Section>'
            f'<Section N="Paragraph"><Row IX="0"><Cell N="HorzAlign" V="1"/></Row></Section>')


def _node_shape(sid, node, style):
    w, h, t = node["w"], node["h"], node["type"]
    lw = (style["ism_added_line_weight_pt"] if t == "ism_added"
          else style["line_weight_pt"]) * PT
    fs = (style["decision_font_pt"] if t == "decision" else style["font_pt"]) * PT
    cells = [
        _cell("PinX", node["cx"]), _cell("PinY", node["cy"]),
        _cell("Width", w), _cell("Height", h),
        _cell("LocPinX", w / 2, "Width*0.5"), _cell("LocPinY", h / 2, "Height*0.5"),
        _cell("Angle", 0.0),
        _cell("LineWeight", lw), _cell("LineColor", style["line_color"]),
        _cell("FillForegnd", style["fill_color"]),
        _cell("VerticalAlign", 1),
    ]
    if t == "terminal":
        cells.append(_cell("Rounding", min(h, w) * 0.5))
    geom = _diamond_geom(w, h) if t == "decision" else _rect_geom(w, h)
    return (f'<Shape ID="{sid}" Type="Shape" LineStyle="0" FillStyle="0" TextStyle="0">'
            + "".join(cells) + _char_para(fs) + geom
            + f'<Text>{escape(node["text"])}</Text></Shape>')


def _connector_shape(sid, pts, style, label=None):
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    minx, maxx, miny, maxy = min(xs), max(xs), min(ys), max(ys)
    w = max(maxx - minx, 1e-3)
    h = max(maxy - miny, 1e-3)
    cx, cy = (minx + maxx) / 2, (miny + maxy) / 2
    local = [(x - minx, y - miny) for x, y in pts]
    lw = style["line_weight_pt"] * PT
    cells = [
        _cell("PinX", cx), _cell("PinY", cy),
        _cell("Width", w), _cell("Height", h),
        _cell("LocPinX", w / 2, "Width*0.5"), _cell("LocPinY", h / 2, "Height*0.5"),
        _cell("Angle", 0.0), _cell("LineWeight", lw),
        _cell("LineColor", style["line_color"]),
        _cell("EndArrow", 4), _cell("EndArrowSize", 1),
        _cell("BeginX", pts[0][0]), _cell("BeginY", pts[0][1]),
        _cell("EndX", pts[-1][0]), _cell("EndY", pts[-1][1]),
    ]
    txt = f'<Text>{escape(label)}</Text>' if label else ""
    char = _char_para(style["decision_font_pt"] * PT) if label else ""
    return (f'<Shape ID="{sid}" Type="Shape" LineStyle="0" FillStyle="0" TextStyle="0">'
            + "".join(cells) + char + _poly_geom(local) + txt + "</Shape>")


def _build_shapes(spec):
    C = _node_centers(spec)
    style = spec["style"]
    L = spec["layout"]
    shapes, idmap, sid = [], {}, 1
    for n in spec["nodes"]:
        idmap[n["id"]] = sid
        shapes.append(_node_shape(sid, C[n["id"]], style))
        sid += 1
    for e in spec["edges"]:
        a, b = C[e["from"]], C[e["to"]]
        route = e.get("route")
        if route == "right_rail":                 # loop-back: right, up, left into b.east
            pts = [(a["cx"] + a["w"] / 2, a["cy"]),
                   (L["rail_x"], a["cy"]),
                   (L["rail_x"], b["cy"]),
                   (b["cx"] + b["w"] / 2, b["cy"])]
        elif route == "horizontal_left":          # A.west -> B.east (End sits left of decision)
            pts = [(a["cx"] - a["w"] / 2, a["cy"]), (b["cx"] + b["w"] / 2, b["cy"])]
        elif abs(a["cx"] - b["cx"]) < 1e-6:       # straight vertical A.bottom -> B.top
            pts = [(a["cx"], a["cy"] - a["h"] / 2), (b["cx"], b["cy"] + b["h"] / 2)]
        else:                                     # elbow: down, across, down (fork / join)
            a_bot, b_top = a["cy"] - a["h"] / 2, b["cy"] + b["h"] / 2
            mid_y = (a_bot + b_top) / 2
            pts = [(a["cx"], a_bot), (a["cx"], mid_y), (b["cx"], mid_y), (b["cx"], b_top)]
        shapes.append(_connector_shape(sid, pts, style, e.get("label")))
        sid += 1
    return shapes


# --------------------------------------------------------------------------- #
# package parts
# --------------------------------------------------------------------------- #
def _parts(spec):
    W, H = spec["layout"]["page_w"], spec["layout"]["page_h"]
    shapes = _build_shapes(spec)
    xml = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\r\n'

    content_types = xml + (
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="xml" ContentType="application/xml"/>'
        '<Override PartName="/visio/document.xml" ContentType="application/vnd.ms-visio.drawing.main+xml"/>'
        '<Override PartName="/visio/pages/pages.xml" ContentType="application/vnd.ms-visio.pages+xml"/>'
        '<Override PartName="/visio/pages/page1.xml" ContentType="application/vnd.ms-visio.page+xml"/>'
        '<Override PartName="/visio/windows.xml" ContentType="application/vnd.ms-visio.windows+xml"/>'
        '<Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>'
        '<Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>'
        '</Types>')

    root_rels = xml + (
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" Type="http://schemas.microsoft.com/visio/2010/relationships/document" Target="visio/document.xml"/>'
        '<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/>'
        '<Relationship Id="rId3" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>'
        '</Relationships>')

    document = xml + (
        f'<VisioDocument xmlns="{VNS}" xmlns:r="{RNS}" xml:space="preserve">'
        '<DocumentSettings TopPage="0" DefaultTextStyle="0" DefaultLineStyle="0" '
        'DefaultFillStyle="0" DefaultGuideStyle="0">'
        '<GlueSettings>9</GlueSettings><SnapSettings>65847</SnapSettings>'
        '<SnapExtensions>34</SnapExtensions><DynamicGridEnabled>1</DynamicGridEnabled>'
        '<ProtectStyles>0</ProtectStyles><ProtectShapes>0</ProtectShapes>'
        '<ProtectMasters>0</ProtectMasters><ProtectBkgnds>0</ProtectBkgnds></DocumentSettings>'
        '<Colors/><FaceNames><FaceName ID="1" Name="Calibri" '
        'UnicodeRanges="-536859905 -1073732485 9 0" CharSets="536871327 0" '
        'Panos="2 15 5 2 2 2 4 3 2 4" Flags="325"/></FaceNames><StyleSheets/>'
        '</VisioDocument>')

    document_rels = xml + (
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" Type="http://schemas.microsoft.com/visio/2010/relationships/pages" Target="pages/pages.xml"/>'
        '<Relationship Id="rId2" Type="http://schemas.microsoft.com/visio/2010/relationships/windows" Target="windows.xml"/>'
        '</Relationships>')

    pages = xml + (
        f'<Pages xmlns="{VNS}" xmlns:r="{RNS}" xml:space="preserve">'
        f'<Page ID="0" NameU="Page-1" Name="Page-1" ViewScale="-1" '
        f'ViewCenterX="{_fmt(W/2)}" ViewCenterY="{_fmt(H/2)}">'
        '<PageSheet LineStyle="0" FillStyle="0" TextStyle="0">'
        f'{_cell("PageWidth", W)}{_cell("PageHeight", H)}'
        f'{_cell("ShdwOffsetX", 0.125)}{_cell("ShdwOffsetY", -0.125)}'
        f'{_cell("PageScale", 1.0)}{_cell("DrawingScale", 1.0)}'
        f'{_cell("DrawingSizeType", 0)}{_cell("DrawingScaleType", 0)}'
        f'{_cell("InhibitSnap", 0)}{_cell("UIVisibility", 0)}</PageSheet>'
        '<Rel r:id="rId1"/></Page></Pages>')

    pages_rels = xml + (
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" Type="http://schemas.microsoft.com/visio/2010/relationships/page" Target="page1.xml"/>'
        '</Relationships>')

    page1 = xml + (
        f'<PageContents xmlns="{VNS}" xmlns:r="{RNS}" xml:space="preserve">'
        '<Shapes>' + "".join(shapes) + '</Shapes></PageContents>')

    windows = xml + (
        f'<Windows xmlns="{VNS}" xmlns:r="{RNS}" ClientWidth="1" ClientHeight="1"/>')

    core = xml + (
        '<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" '
        'xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" '
        'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">'
        f'<dc:title>{escape(spec.get("title", spec["name"]))}</dc:title>'
        '<dc:creator>DT-GSK build_visio_flowcharts.py</dc:creator>'
        '<cp:lastModifiedBy>DT-GSK build_visio_flowcharts.py</cp:lastModifiedBy>'
        '</cp:coreProperties>')

    app = xml + (
        '<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties" '
        'xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes">'
        '<Application>Microsoft Visio</Application><Company>DT-GSK</Company></Properties>')

    return [
        ("[Content_Types].xml", content_types),
        ("_rels/.rels", root_rels),
        ("docProps/app.xml", app),
        ("docProps/core.xml", core),
        ("visio/document.xml", document),
        ("visio/_rels/document.xml.rels", document_rels),
        ("visio/pages/pages.xml", pages),
        ("visio/pages/_rels/pages.xml.rels", pages_rels),
        ("visio/pages/page1.xml", page1),
        ("visio/windows.xml", windows),
    ]


def _check(parts):
    import xml.dom.minidom as minidom
    required = {"[Content_Types].xml", "_rels/.rels", "visio/document.xml",
                "visio/pages/pages.xml", "visio/pages/page1.xml"}
    names = {n for n, _ in parts}
    missing = required - names
    if missing:
        raise SystemExit(f"FAIL: missing parts {missing}")
    for n, d in parts:
        if n.endswith(".xml") or n.endswith(".rels"):
            minidom.parseString(d if isinstance(d, bytes) else d.encode("utf-8"))
    print(f"OK: {len(parts)} parts, all XML well-formed, required OPC parts present")


def build_vsdx(spec_path, out_path=None):
    """Generate a .vsdx from a spec JSON (importable). Returns the output Path.
    Raises on a structurally-invalid package."""
    spec = json.loads(Path(spec_path).read_text(encoding="utf-8"))
    parts = _parts(spec)
    _check(parts)
    out = (Path(out_path) if out_path
           else Path(spec_path).with_name(f"flowchart_{spec['name']}.vsdx"))
    write_vsdx(out, parts)
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("spec", help="flowchart spec JSON")
    ap.add_argument("--out", default=None, help="output .vsdx path")
    ap.add_argument("--check", action="store_true", help="structural self-test only; write nothing")
    args = ap.parse_args(argv)

    spec = json.loads(Path(args.spec).read_text(encoding="utf-8"))
    parts = _parts(spec)
    _check(parts)
    if args.check:
        return 0
    out = Path(args.out) if args.out else Path(args.spec).with_name(f"flowchart_{spec['name']}.vsdx")
    write_vsdx(out, parts)
    with zipfile.ZipFile(out) as zf:
        bad = zf.testzip()
    print(f"Wrote {out} ({out.stat().st_size} bytes); zip integrity: {'OK' if bad is None else bad}")
    print(f"  shapes: {len(spec['nodes'])} nodes + {len(spec['edges'])} connectors")
    print("  NOTE: open in Microsoft Visio to confirm it loads without repair (author acceptance test).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
