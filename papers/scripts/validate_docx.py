#!/usr/bin/env python3
"""Phase 9 OOXML package inspection (Appendix D.6 validator).

    python papers/scripts/validate_docx.py papers/DT-GSK.docx
    python papers/scripts/validate_docx.py papers/supplementary.docx
    python papers/scripts/validate_docx.py <docx> --json out.json

Checks (package unzipped to a temporary validation directory):

1.  package/schema sanity: every XML part well-formed; required parts
    present; [Content_Types].xml covers every part; relationship targets
    resolve (package, document, customXml); unique relationship Ids; every
    r:embed/r:id used by document.xml resolves; root element sanity; no
    XML-1.0-invalid control characters in text nodes (Word repair trigger);
2.  OMML: m:oMath / m:oMathPara counts; ZERO equation images (image count
    must equal the canonical-source \\includegraphics count and no media
    part may look like a rendered formula);
3.  native tables: w:tbl count vs the canonical-source expectation
    (table envs + standalone tabulars); w:tbl structural sanity
    (tblGrid/gridSpan consistency, non-empty rows/cells -- repair triggers);
4.  fields: SEQ/REF/CITATION/TOC counts, fldChar begin/separate/end stack
    balance, REF targets exist as bookmarks, cached results present,
    counts cross-checked against word/field_registry.csv;
5.  bookmarks: start/end id pairing, unique ids, unique names, name rules;
6.  images: every drawing carries alt text (wp:docPr/@descr), unique
    docPr ids (repair trigger);
7.  customXml bibliography store: b:Sources present + wired (itemProps,
    rels, content types, document relationship), entry count vs the frozen
    .aux citation count;
8.  settings: w:updateFields absent-or-false (self-contained, no update-on-open
    prompt); styles referenced by the document exist;
9.  no unresolved @@ build markers;
10. no-ablation scan over EVERY package part (visible text and attributes)
    + S6-placeholder rendering check.

Exit status 0 (all PASS) / 2 (any FAIL).  JSON report on stdout.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
import tempfile
import zipfile
from pathlib import Path

from lxml import etree

SCRIPTS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS_DIR))

from _validate_common import (  # noqa: E402
    B, CT, M, REL, REPO, W, WP,
    DOC_PAIRS, docx_fields, flatten_tex, parse_aux_bibcites,
    strip_tex_comments, tex_document_body,
)

R_NS = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"

REQUIRED_PARTS = [
    "[Content_Types].xml",
    "_rels/.rels",
    "word/document.xml",
    "word/styles.xml",
    "word/settings.xml",
    "docProps/core.xml",
    "docProps/app.xml",
]

ABLATION_TOKENS = ("ablation", "ablat", "phase_12_placeholder",
                   "do not release")

# XML 1.0 invalid control characters (Word repair trigger if present)
_BAD_CTRL = re.compile("[\x00-\x08\x0b\x0c\x0e-\x1f]")


class Report:
    def __init__(self, path: Path):
        self.data: dict = {"file": str(path), "ok": True,
                           "checks": [], "counts": {}, "warnings": []}

    def check(self, name: str, ok: bool, detail: str = ""):
        self.data["checks"].append(
            {"check": name, "status": "PASS" if ok else "FAIL",
             "detail": detail})
        if not ok:
            self.data["ok"] = False

    def warn(self, msg: str):
        self.data["warnings"].append(msg)

    def count(self, name: str, value):
        self.data["counts"][name] = value


def doc_kind_for(path: Path) -> str:
    return "supplementary" if "supplement" in path.name.lower() else "main"


# ---------------------------------------------------------------------------
# canonical-source expectations
# ---------------------------------------------------------------------------

def source_expectations(kind: str) -> dict[str, int]:
    spec = DOC_PAIRS[kind]
    body = tex_document_body(
        strip_tex_comments(flatten_tex(spec["tex"])))
    n_table_envs = len(re.findall(r"\\begin\{table\}", body))
    n_longtable = len(re.findall(r"\\begin\{longtable\}", body))
    # standalone tabulars (not inside a table env)
    tabulars = [m.start() for m in re.finditer(r"\\begin\{tabular\}", body)]
    table_spans = []
    for m in re.finditer(r"\\begin\{table\}", body):
        e = body.find(r"\end{table}", m.start())
        table_spans.append((m.start(), e))
    standalone = sum(1 for t in tabulars
                     if not any(s <= t <= e for s, e in table_spans))
    return {
        "figures": len(re.findall(r"\\includegraphics", body)),
        "tables": n_table_envs + n_longtable + standalone,
        "citations": len(parse_aux_bibcites(spec["aux"])),
    }


# ---------------------------------------------------------------------------
# individual validations
# ---------------------------------------------------------------------------

def validate(path: Path) -> Report:
    rep = Report(path)
    kind = doc_kind_for(path)
    expect = source_expectations(kind)

    with tempfile.TemporaryDirectory(prefix="docx_validate_") as tmp:
        tmpdir = Path(tmp)
        with zipfile.ZipFile(path) as zf:
            bad = zf.testzip()
            rep.check("zip_integrity", bad is None,
                      f"corrupt member: {bad}" if bad else "zip CRC ok")
            names = zf.namelist()
            zf.extractall(tmpdir)
        dupes = {n for n in names if names.count(n) > 1}
        rep.check("zip_unique_part_names", not dupes,
                  f"duplicated: {sorted(dupes)[:4]}" if dupes else
                  f"{len(names)} parts")

        parts: dict[str, bytes] = {
            n: (tmpdir / n).read_bytes() for n in names}

        # ---- 1. XML well-formedness + required parts -----------------------
        parse_fail = []
        xml_parts: dict[str, etree._Element] = {}
        for n, data in parts.items():
            if n.endswith((".xml", ".rels")):
                try:
                    xml_parts[n] = etree.fromstring(data)
                except etree.XMLSyntaxError as exc:
                    parse_fail.append(f"{n}: {exc}")
        rep.check("xml_well_formed", not parse_fail,
                  "; ".join(parse_fail[:3]) if parse_fail else
                  f"{len(xml_parts)} XML parts parsed")
        missing = [p for p in REQUIRED_PARTS if p not in parts]
        rep.check("required_parts", not missing, str(missing) if missing
                  else "all required parts present")
        if "word/document.xml" not in xml_parts:
            rep.check("document_xml", False, "word/document.xml unreadable")
            return rep
        doc = xml_parts["word/document.xml"]

        # ---- content types --------------------------------------------------
        ct = xml_parts["[Content_Types].xml"]
        defaults = {d.get("Extension", "").lower()
                    for d in ct.findall(CT + "Default")}
        overrides = {o.get("PartName") for o in ct.findall(CT + "Override")}
        uncovered = [n for n in parts
                     if "/" + n not in overrides
                     and n.rsplit(".", 1)[-1].lower() not in defaults]
        rep.check("content_types_cover_all_parts", not uncovered,
                  str(uncovered[:4]) if uncovered else
                  f"{len(defaults)} defaults + {len(overrides)} overrides")

        # ---- relationships --------------------------------------------------
        rel_issues = []
        doc_rel_ids: dict[str, str] = {}
        for rel_name, root in [(n, x) for n, x in xml_parts.items()
                               if n.endswith(".rels")]:
            base = rel_name.rsplit("_rels/", 1)[0]
            ids = []
            for r in root.findall(REL + "Relationship"):
                rid, target = r.get("Id"), r.get("Target", "")
                ids.append(rid)
                if rel_name == "word/_rels/document.xml.rels":
                    doc_rel_ids[rid] = target
                if r.get("TargetMode") == "External":
                    continue
                norm = _norm_target(base, target)
                if norm not in parts:
                    rel_issues.append(f"{rel_name}: {rid} -> {norm} missing")
            dup = {i for i in ids if ids.count(i) > 1}
            if dup:
                rel_issues.append(f"{rel_name}: duplicate Ids {sorted(dup)}")
        rep.check("relationship_targets_resolve", not rel_issues,
                  "; ".join(rel_issues[:3]) if rel_issues else
                  f"{sum(1 for n in xml_parts if n.endswith('.rels'))} rels parts clean")

        used_rids = set()
        for el_ in doc.iter():
            for attr, val in el_.attrib.items():
                if attr.startswith(R_NS):
                    used_rids.add(val)
        dangling = sorted(used_rids - set(doc_rel_ids))
        rep.check("document_rids_resolve", not dangling,
                  f"dangling r:id {dangling[:4]}" if dangling else
                  f"{len(used_rids)} r:id references resolve")

        # ---- root/body sanity ----------------------------------------------
        body = doc.find(W + "body")
        ok_root = doc.tag == W + "document" and body is not None
        sect = body.findall(W + "sectPr") if body is not None else []
        sect_ok = len(sect) <= 1 and (not sect or
                                      list(body)[-1].tag == W + "sectPr")
        rep.check("root_body_sectpr", ok_root and sect_ok,
                  "w:document/w:body present, sectPr terminal")

        # ---- invalid control chars ------------------------------------------
        bad_text = []
        for el_ in doc.iter():
            if el_.text and _BAD_CTRL.search(el_.text):
                bad_text.append(el_.tag)
        rep.check("no_invalid_control_chars", not bad_text,
                  f"{len(bad_text)} tainted nodes" if bad_text else
                  "text nodes clean")

        # ---- OMML ------------------------------------------------------------
        n_omath = sum(1 for _ in doc.iter(M + "oMath"))
        n_omathpara = sum(1 for _ in doc.iter(M + "oMathPara"))
        rep.count("m_oMath", n_omath)
        rep.count("m_oMathPara", n_omathpara)
        rep.check("omml_present", n_omath > 0,
                  f"{n_omath} m:oMath ({n_omathpara} m:oMathPara)")

        # ---- images / zero equation images ----------------------------------
        drawings = list(doc.iter(W + "drawing"))
        # OLE objects (Phase D4: Visio flowcharts embedded as w:object) are
        # legitimate figures too -- count them toward the canonical figure total.
        n_ole = sum(1 for _ in doc.iter(W + "object"))
        media = [n for n in parts if n.startswith("word/media/")]
        formula_like = [n for n in media
                        if re.search(r"(eq|formula|math|texmf)", Path(n).stem,
                                     re.IGNORECASE)]
        rep.count("images_embedded", len(drawings))
        rep.count("ole_objects", n_ole)
        rep.count("media_parts", len(media))
        rep.check("zero_equation_images",
                  len(drawings) + n_ole == expect["figures"] and not formula_like,
                  f"{len(drawings)} drawings + {n_ole} OLE vs {expect['figures']} "
                  f"canonical \\includegraphics; formula-named media: {formula_like}")
        no_alt = sum(1 for d in drawings
                     for pr in d.iter(WP + "docPr")
                     if not (pr.get("descr") or "").strip())
        rep.count("images_with_alt", len(drawings) - no_alt)
        rep.check("alt_text_on_every_image", no_alt == 0,
                  f"{len(drawings) - no_alt}/{len(drawings)} images carry descr")
        pr_ids = [pr.get("id") for d in drawings for pr in d.iter(WP + "docPr")]
        dup_pr = {i for i in pr_ids if pr_ids.count(i) > 1}
        rep.check("unique_drawing_docpr_ids", not dup_pr,
                  f"duplicate docPr ids {sorted(dup_pr)[:4]}" if dup_pr
                  else f"{len(pr_ids)} unique ids")

        # ---- tables -----------------------------------------------------------
        tbls = list(doc.iter(W + "tbl"))
        rep.count("w_tbl", len(tbls))
        rep.check("table_count_vs_source", len(tbls) == expect["tables"],
                  f"{len(tbls)} w:tbl vs {expect['tables']} canonical table "
                  "environments")
        tbl_issues = []
        for ti, tbl in enumerate(tbls):
            grid = tbl.find(W + "tblGrid")
            ncols_grid = len(grid.findall(W + "gridCol")) if grid is not None else 0
            for tr in tbl.findall(W + "tr"):
                tcs = tr.findall(W + "tc")
                if not tcs:
                    tbl_issues.append(f"tbl{ti}: row without cells")
                    continue
                span = 0
                for tc in tcs:
                    if tc.find(W + "p") is None and tc.find(W + "tbl") is None:
                        tbl_issues.append(f"tbl{ti}: cell without block")
                    tcpr = tc.find(W + "tcPr")
                    gs = tcpr.find(W + "gridSpan") if tcpr is not None else None
                    span += int(gs.get(W + "val")) if gs is not None else 1
                if grid is not None and span != ncols_grid:
                    tbl_issues.append(
                        f"tbl{ti}: row span {span} != grid {ncols_grid}")
        rep.check("table_structure_sane", not tbl_issues,
                  "; ".join(tbl_issues[:4]) if tbl_issues else
                  "tblGrid/gridSpan consistent, no empty rows/cells")

        # ---- fields -------------------------------------------------------------
        fldchars = [f.get(W + "fldCharType") for f in doc.iter(W + "fldChar")]
        depth, neg = 0, False
        for t in fldchars:
            if t == "begin":
                depth += 1
            elif t == "end":
                depth -= 1
                neg = neg or depth < 0
        rep.check("fldchar_balance", depth == 0 and not neg,
                  f"begin={fldchars.count('begin')} end={fldchars.count('end')}"
                  f" separate={fldchars.count('separate')}")
        fields = docx_fields(doc)
        by_kind: dict[str, int] = {}
        for f in fields:
            by_kind[f["type"]] = by_kind.get(f["type"], 0) + 1
        for k in ("SEQ", "REF", "CITATION", "TOC"):
            rep.count(f"field_{k}", by_kind.get(k, 0))
        rep.count("fields_total", len(fields))
        rep.check("toc_field_absent", by_kind.get("TOC", 0) == 0,
                  f"{by_kind.get('TOC', 0)} TOC fields "
                  f"(expected 0: DOCX matches the no-TOC PDF)")
        empty_cached = [f for f in fields
                        if f["type"] in ("SEQ", "REF", "CITATION")
                        and not f["cached"].strip()]
        rep.check("fields_have_cached_results", not empty_cached,
                  f"{len(empty_cached)} without cached result" if empty_cached
                  else "every SEQ/REF/CITATION carries a cached result")
        seq_names = {m.group(1) for f in fields if f["type"] == "SEQ"
                     for m in [re.match(r"SEQ (\w+)", f["instr"])] if m}
        rep.check("seq_names_expected",
                  seq_names <= {"Figure", "Table", "Algorithm", "Equation"},
                  f"SEQ names: {sorted(seq_names)}")

        # ---- bookmarks ------------------------------------------------------------
        starts = list(doc.iter(W + "bookmarkStart"))
        ends = list(doc.iter(W + "bookmarkEnd"))
        s_ids = [b.get(W + "id") for b in starts]
        e_ids = [b.get(W + "id") for b in ends]
        names = [b.get(W + "name") or "" for b in starts]
        rep.count("bookmarks", len(starts))
        rep.check("bookmark_pairing", sorted(s_ids) == sorted(e_ids),
                  f"{len(starts)} starts / {len(ends)} ends, ids paired"
                  if sorted(s_ids) == sorted(e_ids) else
                  f"unpaired ids: {sorted(set(s_ids) ^ set(e_ids))[:5]}")
        dup_ids = {i for i in s_ids if s_ids.count(i) > 1}
        dup_names = {n for n in names if names.count(n) > 1}
        rep.check("bookmark_ids_unique", not dup_ids,
                  str(sorted(dup_ids)[:5]) if dup_ids else "ids unique")
        rep.check("bookmark_names_unique", not dup_names,
                  str(sorted(dup_names)[:5]) if dup_names else "names unique")
        bad_names = [n for n in names
                     if not n or len(n) > 40
                     or not (n[0].isalpha() or n[0] == "_")
                     or not re.fullmatch(r"[A-Za-z0-9_]+", n)]
        rep.check("bookmark_names_word_legal", not bad_names,
                  str(bad_names[:5]) if bad_names else
                  "all names [A-Za-z0-9_], len<=40, letter-initial")

        # REF targets
        bookmark_names = set(names)
        missing_ref = sorted({
            m.group(1) for f in fields if f["type"] == "REF"
            for m in [re.match(r"REF (\S+)", f["instr"])] if m
            and m.group(1) not in bookmark_names})
        rep.check("ref_targets_exist", not missing_ref,
                  str(missing_ref[:5]) if missing_ref else
                  f"{by_kind.get('REF', 0)} REF fields all target bookmarks")

        # ---- field registry cross-check --------------------------------------------
        reg_path = REPO / "word" / "field_registry.csv"
        if reg_path.is_file():
            with open(reg_path, encoding="utf-8", newline="") as fh:
                reg = [r for r in csv.DictReader(fh)
                       if r.get("doc") == path.name]
            reg_counts = {}
            for r in reg:
                reg_counts[r["field_type"]] = reg_counts.get(r["field_type"], 0) + 1
            mism = [f"{k}: doc={by_kind.get(k, 0)} registry={reg_counts.get(k, 0)}"
                    for k in ("SEQ", "REF", "CITATION", "TOC")
                    if by_kind.get(k, 0) != reg_counts.get(k, 0)]
            rep.check("field_registry_agrees", not mism,
                      "; ".join(mism) if mism else
                      f"{len(reg)} registry rows match package inventory")
        else:
            rep.check("field_registry_agrees", False,
                      "word/field_registry.csv missing")

        # ---- customXml citation store ------------------------------------------------
        store_ok = "customXml/item1.xml" in xml_parts
        n_sources = 0
        if store_ok:
            src_root = xml_parts["customXml/item1.xml"]
            store_ok = src_root.tag == B + "Sources"
            n_sources = len(src_root.findall(B + "Source"))
        wiring = ("customXml/itemProps1.xml" in parts
                  and "customXml/_rels/item1.xml.rels" in parts
                  and "/customXml/itemProps1.xml" in overrides
                  and any(t.endswith("customXml/item1.xml")
                          or t == "../customXml/item1.xml"
                          for t in doc_rel_ids.values()))
        rep.count("citation_sources", n_sources)
        rep.check("citation_store_present_and_wired", store_ok and wiring,
                  f"b:Sources with {n_sources} entries; itemProps/rels/"
                  f"content-type/document-rel wiring {'ok' if wiring else 'BROKEN'}")
        rep.check("citation_store_count_vs_aux",
                  n_sources == expect["citations"],
                  f"{n_sources} sources vs {expect['citations']} cited keys "
                  "in frozen .aux")

        # ---- settings -------------------------------------------------------------------
        settings = xml_parts.get("word/settings.xml")
        upd = settings.find(W + "updateFields") if settings is not None else None
        # Self-contained DOCX: fields carry cached results and there is no TOC, so
        # update-on-open must be OFF (absent or val="false") to avoid Word's
        # "update the fields?" prompt.  (This inverts the original update-on-open
        # design, which shipped a TOC that Word rebuilt on open.)
        rep.check("no_update_fields_on_open",
                  upd is None or upd.get(W + "val") in ("false", "0"),
                  "w:updateFields=%s" % upd.get(W + "val") if upd is not None
                  else "w:updateFields absent")

        # ---- style references ------------------------------------------------------------
        styles = xml_parts.get("word/styles.xml")
        style_ids = {s.get(W + "styleId")
                     for s in styles.findall(W + "style")} if styles is not None else set()
        used_styles = {el_.get(W + "val")
                       for tag in ("pStyle", "rStyle", "tblStyle")
                       for el_ in doc.iter(W + tag)}
        missing_styles = sorted(s for s in used_styles if s and s not in style_ids)
        rep.check("referenced_styles_defined", not missing_styles,
                  str(missing_styles[:6]) if missing_styles else
                  f"{len(used_styles)} referenced style ids all defined")

        # ---- residues ----------------------------------------------------------------------
        xml_str = etree.tostring(doc, encoding="unicode")
        residues = re.findall(r"@@[A-Z]+(?:![^@!]*)*@@", xml_str)
        rep.count("markers_left", len(residues))
        rep.check("no_unresolved_markers", not residues,
                  str(residues[:3]) if residues else "0 @@ markers")

        # ---- ablation-token scan over every part (governance guard) --------------------------
        # Direction is fixed by correction_exception_protocol.md Sec.4: the shipped
        # MAIN must carry ZERO ablation content, but ablation prose is admissible in
        # the SUPPLEMENT build only (the reserved, now-filled Phase-12 S6 slot).  The
        # release-block tokens (the placeholder marker + any "do not release" flag)
        # must be absent from BOTH: after Phase 12 the S6 placeholder is replaced by
        # real content, and nothing may remain marked do-not-release.
        RELEASE_BLOCK_TOKENS = ("phase_12_placeholder", "do not release")
        active_tokens = (RELEASE_BLOCK_TOKENS if kind == "supplementary"
                         else ABLATION_TOKENS)
        hits = []
        for n, data in parts.items():
            if n.endswith((".xml", ".rels")):
                try:
                    text = data.decode("utf-8", errors="replace").lower()
                except Exception:
                    continue
                for tok in active_tokens:
                    if tok in text:
                        hits.append(f"{n}: '{tok}'")
        rep.check("no_ablation_tokens_any_part", not hits,
                  "; ".join(hits[:5]) if hits else
                  (f"tokens {active_tokens} absent from all {len(parts)} parts"
                   + (" (supplement: ablation prose admissible in S6; only "
                      "release-block tokens forbidden)"
                      if kind == "supplementary" else "")))
        # S6 rendering: the MAIN must NOT render an S6 section (its component-study
        # slot is empty); the post-Phase-12 SUPPLEMENT MUST render its S6 ablation
        # section.  Same scan, opposite expectation per doc kind.
        s6 = []
        for p in doc.iter(W + "p"):
            txt = "".join(t.text or "" for t in p.iter()
                          if t.tag in (W + "t", M + "t") and t.text)
            if re.match(r"\s*S6(\s|\.|:|$)", txt):
                s6.append(txt[:60])
        if kind == "supplementary":
            rep.check("s6_ablation_section_rendered", bool(s6),
                      str(s6[:3]) if s6 else
                      "EXPECTED a rendered S6 ablation section, found none")
        else:
            rep.check("s6_placeholder_not_rendered", not s6,
                      str(s6[:3]) if s6 else "no rendered S6 heading/paragraph")

        # ---- python-docx opens -----------------------------------------------------------------
        try:
            import docx
            docx.Document(str(path))
            rep.check("python_docx_opens", True, "docx.Document() ok")
        except Exception as exc:
            rep.check("python_docx_opens", False, str(exc))

    return rep


def _norm_target(base: str, target: str) -> str:
    import posixpath
    return posixpath.normpath(posixpath.join(base, target))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("docx", help="path to the .docx to validate")
    ap.add_argument("--json", help="also write the JSON report here")
    args = ap.parse_args(argv)
    path = Path(args.docx)
    if not path.is_file():
        # accepted alias per D.6 (papers/main.docx -> recorded mapping)
        if path.name == "main.docx":
            alt = path.with_name("DT-GSK.docx")
            if alt.is_file():
                print(f"note: {path} not present; validating recorded "
                      f"filename mapping {alt}", file=sys.stderr)
                path = alt
    if not path.is_file():
        print(f"error: {path} not found", file=sys.stderr)
        return 1
    rep = validate(path)
    out = json.dumps(rep.data, indent=2, ensure_ascii=False)
    print(out)
    if args.json:
        Path(args.json).write_text(out + "\n", encoding="utf-8")
    fails = [c for c in rep.data["checks"] if c["status"] == "FAIL"]
    print(f"\n{path.name}: {len(rep.data['checks']) - len(fails)} PASS / "
          f"{len(fails)} FAIL", file=sys.stderr)
    return 0 if rep.data["ok"] else 2


if __name__ == "__main__":
    sys.exit(main())
