# Copyright (c) 2026 Mostafa Masoud <moustafa.masoud@gmail.com>
"""Phase 7 task 11 -- create ``papers/governance/artifact_binding.csv``.

One row per Phase 7-produced exhibit (tables T01--T16 + T16_bca, all
convergence / Nemenyi / rank / conceptual figures, and the phase_03
method artifacts), using the PAPER_BUILD_PROMPT Section 3.8 schema::

    artifact_id,artifact_path,artifact_type,manuscript_label,
    generator_script,generator_command,source_paths,source_checksums,
    analysis_id,evidence_release_id,commit_sha,output_checksum,scope,
    latex_location,word_location,validation_status

``manuscript_label`` is seeded from
``papers/build_prompt_phases/phase_04/exhibit_plan.csv`` (label column);
exhibits with no exhibit-plan row (the legacy-numbered GSK-vs-DT-GSK
head-to-head detail tables T02--T05 and the CEC2013 Wilcoxon summary
T14, plus the legacy overall rank bar) keep their current manuscript
labels and are marked as such in ``artifact_id``.

Checksums are SHA-256.  Multi-file cells join ``name=hash`` entries
with ``;``.  Convergence-grid gen_log inputs (hundreds of files per
grid) are recorded as a deterministic aggregate: the SHA-256 of the
sorted ``relpath=sha256`` line list, with the file count disclosed.

Every referenced path must exist -- a missing input or output is a
HARD FAIL, never a silent skip.  Deterministic output: no timestamps.

Usage::

    python papers/scripts/generate_artifact_binding.py
"""
from __future__ import annotations

import csv
import json
import os
import hashlib
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PAPERS = SCRIPT_DIR.parent
ROOT = PAPERS.parent

# The convergence-panel partition lives with the renderer that produces the
# panels; import it so this registry cannot describe a layout that is no
# longer the one on disk.
sys.path.insert(0, str(SCRIPT_DIR))
import generate_full_convergence  # noqa: E402
def _default_release_id() -> str:
    """Resolve the promoted primary release rather than hardcoding one.

    The default was pinned to ``rel-2026-07-16-78f075cb0``, which has been
    superseded by ``rel-2026-07-20-67d9345f9`` since the C006 regeneration. A
    hardcoded default means every regeneration of this registry re-stamps the
    superseded id over rows whose ``source_paths`` already point at the current
    release -- which is how 16 rows came to contradict themselves. Read the
    promoted id from the manifest that owns it, and fall back to the historical
    literal only if that manifest cannot be read, so this stays runnable.
    """
    try:
        manifest = PAPERS / "governance" / "evidence_release_manifest.json"
        return json.loads(manifest.read_text(encoding="utf-8"))["release_id"]
    except Exception:
        return "rel-2026-07-16-78f075cb0"


RELEASE_ID = os.environ.get("GSK_REL_ID", _default_release_id())
BUNDLE = f"papers/analysis/{RELEASE_ID}"
REF = "benchmarks/cec_reference_results"
OUT = PAPERS / "governance" / "artifact_binding.csv"

ALGS = ["gsk", "agsk", "apgsk", "fdb-agsk", "atmals-gsk", "egsk", "dt-gsk"]

VALIDATION_REPORT = "papers/build_prompt_phases/phase_07/exhibit_validation_report.md"

COLUMNS = [
    "artifact_id", "artifact_path", "artifact_type", "manuscript_label",
    "generator_script", "generator_command", "source_paths",
    "source_checksums", "analysis_id", "evidence_release_id", "commit_sha",
    "output_checksum", "scope", "latex_location", "word_location",
    "validation_status",
]


def sha256(rel: str) -> str:
    p = ROOT / rel
    if not p.is_file():
        raise SystemExit(f"HARD FAIL: missing file for checksum: {p}")
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def checksum_cell(rels: list[str]) -> str:
    return ";".join(f"{Path(r).name}={sha256(r)}" for r in rels)


def aggregate_checksum(rels: list[str]) -> tuple[str, int]:
    lines = sorted(f"{r}={sha256(r)}" for r in rels)
    agg = hashlib.sha256("\n".join(lines).encode("utf-8")).hexdigest()
    return agg, len(lines)


def head_sha() -> str:
    out = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True,
        text=True, check=True)
    sha = out.stdout.strip()
    dirty = subprocess.run(
        ["git", "status", "--porcelain"], cwd=ROOT, capture_output=True,
        text=True, check=True).stdout.strip()
    return sha + ("-dirty" if dirty else "")


def gen_log_files(suite: str, funcs: list[int], dim: int | None) -> list[str]:
    """gen_log checkpoint files for a grid; CEC2011 resolves native dims."""
    rels: list[str] = []
    for alg in ALGS:
        for f in funcs:
            if dim is not None:
                rel = f"{REF}/{suite}/{alg}/gen_logs/CheckpointErrors_{alg}_F{f}_D{dim}.csv"
                if not (ROOT / rel).is_file():
                    raise SystemExit(f"HARD FAIL: missing gen_log {rel}")
                rels.append(rel)
            else:
                hits = sorted((ROOT / REF / suite / alg / "gen_logs").glob(
                    f"CheckpointErrors_{alg}_F{f}_D*.csv"))
                if not hits:
                    raise SystemExit(
                        f"HARD FAIL: no native-dim gen_log for {suite} "
                        f"{alg} F{f}")
                rels.append(str(hits[0].relative_to(ROOT)).replace("\\", "/"))
    return rels


def provenance_sources() -> dict[str, list[str]]:
    import json
    p = json.loads((ROOT / REF / "_paper_tables" / "provenance.json")
                   .read_text(encoding="utf-8"))
    return {k: v["sources"] for k, v in p["exports"].items()}


def main() -> None:
    commit = head_sha()
    prov = provenance_sources()
    rows: list[dict[str, str]] = []

    def add(artifact_id: str, paths: list[str], atype: str, label: str,
            gscript: str, gcmd: str, sources: list[str], src_cksum: str,
            analysis: str, scope: str, latex_loc: str, word_loc: str,
            status: str, release: str = RELEASE_ID) -> None:
        for p in paths:
            if not (ROOT / p).is_file():
                raise SystemExit(f"HARD FAIL: missing output artifact {p}")
        rows.append({
            "artifact_id": artifact_id,
            "artifact_path": ";".join(paths),
            "artifact_type": atype,
            "manuscript_label": label,
            "generator_script": gscript,
            "generator_command": gcmd,
            "source_paths": ";".join(sources),
            "source_checksums": src_cksum,
            "analysis_id": analysis,
            "evidence_release_id": release,
            "commit_sha": commit,
            "output_checksum": checksum_cell(paths),
            "scope": scope,
            "latex_location": latex_loc,
            "word_location": word_loc,
            "validation_status": status,
        })

    # ------------------------------------------------------------------
    # Tables T01--T16 (generate_latex_tables.py --skip-ablation)
    # ------------------------------------------------------------------
    tab_gen = "papers/scripts/generate_latex_tables.py"
    tab_cmd = "python papers/scripts/generate_latex_tables.py --skip-ablation"
    validated = ("validated-value-level (PASS, 0 mismatches; "
                 f"{VALIDATION_REPORT})")
    sup = "supplementary.tex"
    perf = "sections/performance.tex"

    # (T#, csv, label, plan-seeded?, analysis_id, scope, latex_location)
    table_spec = [
        (1, "T1.csv", "tab:cec2011", "T04",
         "descriptive-export (cec2011 best-fitness basis)", "main", sup),
        (2, "T2.csv", "tab:h2h_d10", "LEGACY", "AN-DESC-2017-D10",
         "supplement", sup),
        (3, "T3.csv", "tab:h2h_d30", "LEGACY", "AN-DESC-2017-D30",
         "supplement", sup),
        (4, "T4.csv", "tab:h2h_d50", "LEGACY", "AN-DESC-2017-D50",
         "supplement", sup),
        (5, "T5.csv", "tab:h2h_d100", "LEGACY", "AN-DESC-2017-D100",
         "supplement", sup),
        (6, "T6.csv", "tab:cec2011-stats", "T04-STATS",
         "AN-PW-2011-NATIVE", "supplement", f"{perf};{sup}"),
        (7, "T7.csv", "tab:cec2017-d10", "T01-D10", "AN-DESC-2017-D10",
         "supplement", sup),
        (8, "T8.csv", "tab:cec2017-d30", "T01-D30", "AN-DESC-2017-D30",
         "supplement", sup),
        (9, "T9.csv", "tab:cec2017-d50", "T01-D50", "AN-DESC-2017-D50",
         "supplement", sup),
        (10, "T10.csv", "tab:cec2017-d100", "T01-D100",
         "AN-DESC-2017-D100", "supplement", sup),
        (11, "T11.csv", "tab:cec2013-d10", "T06-FULL-D10",
         "descriptive-export (cec2013 D10)", "supplement", sup),
        (12, "T12.csv", "tab:cec2013-d30", "T06-FULL-D30",
         "descriptive-export (cec2013 D30)", "supplement", sup),
        (13, "T13.csv", "tab:cec2013-d50", "T06-FULL-D50",
         "descriptive-export (cec2013 D50)", "supplement", sup),
        (14, "T14.csv", "tab:cec2013_wilcoxon", "LEGACY",
         "AN-PW-2013-D10;AN-PW-2013-D30;AN-PW-2013-D50", "supplement", sup),
        (15, "T15.csv", "tab:wilcoxon-holm", "T02",
         "AN-PW-2017-D10;AN-PW-2017-D30;AN-PW-2017-D50;AN-PW-2017-D100",
         "main", perf),
        (16, "T16.csv", "tab:friedman-cec2017", "T05",
         "AN-OMNI-2017-D10;AN-OMNI-2017-D30;AN-OMNI-2017-D50;"
         "AN-OMNI-2017-D100;AN-RANKAGG-2017-OVERALL", "main", perf),
    ]
    for num, csv_name, label, plan, analysis, scope, loc in table_spec:
        staging = f"{REF}/_paper_tables/{csv_name}"
        srcs = [staging] + prov[csv_name]
        aid = f"TAB-T{num:02d}" + ("" if plan == "LEGACY"
                                   else f" (plan {plan})")
        add(aid, [f"papers/tables/T{num:02d}.tex"], "table", label,
            tab_gen, tab_cmd, srcs, checksum_cell(srcs), analysis, scope,
            loc, f"papers/tables/word_sources/T{num}.json", validated)

    # T16_bca (rewired generate_t16_bca.py; bundle descriptive stats)
    bca_srcs = [f"{BUNDLE}/cec2017/descriptive_stats_cec2017_D{d}.csv"
                for d in (10, 30, 50, 100)]
    add("TAB-T16-BCA (plan T-BCA)", ["papers/tables/T16_bca.tex"], "table",
        "tab:bca-ci",
        "papers/scripts/generate_t16_bca.py",
        "python papers/scripts/generate_t16_bca.py",
        bca_srcs, checksum_cell(bca_srcs),
        "rank-CI companion (midrank Friedman ranks + seeded BCa, "
        "BASE_SEED=20260422, n_boot=10000; distinct inspected analysis)",
        "supplement", perf, "papers/tables/word_sources/T16_bca.json",
        "validated-value-level (byte-identical seeded re-derivation; "
        f"point estimates == T16 at 2 dp; {VALIDATION_REPORT}); "
        "NOTE: word_sources/T16_bca.json carries the bundle T-BCA "
        "per-function companion (headline_bca.csv), not this rank-CI "
        "table -- Phase 9 must reconcile (cross_format_consistency)")

    # ------------------------------------------------------------------
    # Convergence grids (CR-0001 seven-curve family overlays)
    # ------------------------------------------------------------------
    conv_note = ("series-count-verified 7/7 in all panels "
                 "(papers/figures/convergence/{log}); sampled panels "
                 f"value-validated ({VALIDATION_REPORT})")
    sel = "papers/build_prompt_phases/phase_05/curve_selection.csv"
    full_gen = "papers/scripts/generate_full_convergence.py"
    full_cmd = "python papers/scripts/generate_full_convergence.py"

    def conv_row(aid: str, stem: str, label: str, suite: str,
                 funcs: list[int], dim: int | None, analysis: str,
                 gscript: str, gcmd: str, scope: str, latex_loc: str,
                 extra_sources: list[str] | None = None,
                 status: str | None = None,
                 log: str = "cec2017_missing.log") -> None:
        rels = gen_log_files(suite, funcs, dim)
        agg, n = aggregate_checksum(rels)
        pattern = (f"{REF}/{suite}/<alg>/gen_logs/CheckpointErrors_"
                   f"<alg>_F{{{','.join(map(str, funcs))}}}_"
                   f"D{dim if dim is not None else '<native>'}.csv "
                   f"(7 algs x {len(funcs)} funcs = {n} files)")
        srcs = ([*extra_sources] if extra_sources else []) + [pattern]
        cks = ((checksum_cell(extra_sources) + ";") if extra_sources
               else "") + f"aggregate-sha256({n} files)={agg}"
        add(aid, [f"papers/figures/convergence/{stem}.pdf",
                  f"papers/figures/convergence/{stem}.png"],
            "figure", label, gscript, gcmd, srcs, cks, analysis, scope,
            latex_loc, "pending-phase9 (Word figure embed)",
            status or conv_note.format(log=log))

    # Main-text grids (frozen P5 selection)
    add_main = [
        ("FIG-CONV-MAIN-D30 (plan F02-MAIN-D30)", "main_cec2017_D30",
         "fig:conv-cec2017-d30", 30, [3, 10, 12, 26],
         "validated-sample-endpoints (all 4 panels x 7 algorithms; "
         f"{VALIDATION_REPORT}); series-count 7/7 (cec2017_missing.log)"),
        ("FIG-CONV-MAIN-D100 (plan F02-MAIN-D100)", "main_cec2017_D100",
         "fig:conv-cec2017-d100", 100, [1, 5, 12, 26],
         "validated-sample-endpoints (F1,F12 panels x 7 algorithms; "
         f"{VALIDATION_REPORT}); series-count 7/7 (cec2017_missing.log)"),
    ]
    for aid, stem, label, dim, funcs, status in add_main:
        conv_row(aid, stem, label, "cec2017", funcs, dim,
                 f"AN-CONV-2017-D{dim} (P2/P5, CR-0001)", full_gen,
                 full_cmd, "main", "pending-phase8-rewire",
                 extra_sources=[sel], status=status)

    # Supplement grids, CEC2017 all functions x 4 dims.  The panel partition is
    # imported from the renderer rather than restated here: a local copy drifted
    # once already (the N-011 5x2 -> 4x2 relayout added panel 'd' and moved every
    # boundary, leaving this registry naming the wrong source files for all 12
    # rows and omitting 4 published panels entirely).
    groups_2017 = generate_full_convergence.PANEL_GROUPS
    for dim in (10, 30, 50, 100):
        for suffix, funcs in groups_2017:
            loc = perf if dim == 10 else "pending-phase8-rewire"
            conv_row(
                f"FIG-CONV-SUP-2017-D{dim}-{suffix.upper()} "
                f"(plan F02-SUP-CEC2017-D{dim})",
                f"all_funcs_D{dim}_{suffix}", f"fig:sconv-cec2017-d{dim}",
                "cec2017", funcs, dim, f"AN-CONV-2017-D{dim} (P2, CR-0001)",
                full_gen, full_cmd, "supplement", loc)

    # CEC2011 grids (native dims)
    groups_2011 = [("a", list(range(1, 9))), ("b", list(range(9, 17))),
                   ("c", list(range(17, 23)))]
    for suffix, funcs in groups_2011:
        conv_row(
            f"FIG-CONV-CEC2011-{suffix.upper()} (plan F02-SUP-CEC2011)",
            f"cec2011_{suffix}", "fig:sconv-cec2011", "cec2011", funcs,
            None, "AN-CONV-2011-NATIVE (P2, CR-0001)",
            "papers/scripts/generate_cec2011_convergence.py",
            "python papers/scripts/generate_cec2011_convergence.py",
            "supplement", sup, log="cec2011_missing.log")

    # CEC2013 grids (D30 only per P4)
    groups_2013 = [("a", list(range(1, 9))), ("b", list(range(9, 17))),
                   ("c", list(range(17, 25))), ("d", list(range(25, 29)))]
    for suffix, funcs in groups_2013:
        conv_row(
            f"FIG-CONV-CEC2013-D30-{suffix.upper()} "
            "(plan F02-SUP-CEC2013-D30)",
            f"cec2013_{suffix}", "fig:sconv-cec2013-d30", "cec2013", funcs,
            30, "AN-CONV-2013-D30 (P2, CR-0001)",
            "papers/scripts/generate_cec2013_convergence.py",
            "python papers/scripts/generate_cec2013_convergence.py "
            "--dimension 30",
            "supplement", "pending-phase8-rewire",
            log="cec2013_missing.log")

    # ------------------------------------------------------------------
    # Nemenyi CD diagrams
    # ------------------------------------------------------------------
    for dim in (10, 30, 50, 100):
        srcs = [f"{BUNDLE}/cec2017/friedman_ranks_cec2017_D{dim}.csv",
                f"{BUNDLE}/cec2017/nemenyi_cd_cec2017_D{dim}.csv"]
        add(f"FIG-CD-D{dim} (plan F01-D{dim})",
            [f"papers/figures/nemenyi/nemenyi_cd_cec2017_D{dim}.pdf",
             f"papers/figures/nemenyi/nemenyi_cd_cec2017_D{dim}.png"],
            "figure", f"fig:cd-d{dim}",
            "papers/scripts/generate_nemenyi_cd.py",
            "python papers/scripts/generate_nemenyi_cd.py",
            srcs, checksum_cell(srcs), f"AN-OMNI-2017-D{dim}",
            "main", "pending-phase8-rewire "
            "(supersedes figures/ranks/nemenyi_cd_d50.pdf)",
            "pending-phase9 (Word figure embed)",
            "validated-value-level (PDF text vs bundle ranks/CD; "
            f"omnibus gate re-checked; {VALIDATION_REPORT})")

    # ------------------------------------------------------------------
    # Rank charts
    # ------------------------------------------------------------------
    rank_gen = "papers/scripts/generate_rank_charts.py"
    rank_cmd = "python papers/scripts/generate_rank_charts.py"
    srcs = [f"{BUNDLE}/cec2017/rank_trend_cec2017.csv"]
    add("FIG-RANK-VS-DIM (plan F03)",
        ["papers/figures/ranks/rank_vs_dim_cec2017.pdf",
         "papers/figures/ranks/rank_vs_dim_cec2017.png"],
        "figure", "fig:rank-vs-dim", rank_gen, rank_cmd, srcs,
        checksum_cell(srcs), "AN-TREND-2017", "main",
        "pending-phase8-rewire", "pending-phase9 (Word figure embed)",
        "source-cross-validated (rank_trend == per-dim friedman CSVs, "
        f"exact; {VALIDATION_REPORT})")

    srcs = [f"{BUNDLE}/cec2017/friedman_ranks_cec2017_D{d}.csv"
            for d in (10, 30, 50, 100)]
    add("FIG-CEC2017-RANKS (plan F05-RANKBAR)",
        ["papers/figures/ranks/cec2017_mean_ranks.pdf",
         "papers/figures/ranks/cec2017_mean_ranks.png"],
        "figure", "fig:cec2017-ranks", rank_gen, rank_cmd, srcs,
        checksum_cell(srcs),
        "AN-OMNI-2017-D10;AN-OMNI-2017-D30;AN-OMNI-2017-D50;"
        "AN-OMNI-2017-D100", "main", "pending-phase8-rewire",
        "pending-phase9 (Word figure embed)",
        "source-cross-validated (friedman CSVs == rank_trend == staged "
        f"T16.csv; {VALIDATION_REPORT})")

    srcs = [f"{BUNDLE}/cec2011/friedman_ranks_cec2011.csv"]
    add("FIG-CEC2011-RANKS (plan F04-CEC2011)",
        ["papers/figures/ranks/cec2011_ranks.pdf",
         "papers/figures/ranks/cec2011_ranks.png"],
        "figure", "fig:cec2011-ranks", rank_gen, rank_cmd, srcs,
        checksum_cell(srcs), "AN-OMNI-2011-NATIVE", "main",
        "pending-phase8-rewire", "pending-phase9 (Word figure embed)",
        "validated-value-level (PDF bar labels vs bundle ranks; "
        f"{VALIDATION_REPORT})")

    srcs = [f"{REF}/_paper_tables/T16.csv"]
    add("FIG-FRIEDMAN-OVERALL (LEGACY fig:friedman_bar_gsk)",
        ["papers/figures/ranks/friedman_gsk_family.pdf",
         "papers/figures/ranks/friedman_gsk_family.png"],
        "figure", "fig:friedman_bar_gsk", rank_gen, rank_cmd, srcs,
        checksum_cell(srcs), "AN-RANKAGG-2017-OVERALL", "main", perf,
        "pending-phase9 (Word figure embed)",
        "validated-value-level (PDF bar labels vs staged T16 Overall; "
        f"{VALIDATION_REPORT})")

    # ------------------------------------------------------------------
    # Conceptual figures (authored; NO empirical values)
    # ------------------------------------------------------------------
    concept_word = "papers/figures/concept/sources/diagram_word_plan.md"
    qa = ("authored-visual-qa (spec conformance verified, "
          "papers/build_prompt_phases/phase_07/method_artifacts_report.md;"
          " no empirical values by design)")
    specs = "papers/build_prompt_phases/phase_04/conceptual_figure_specs.md"
    p3param = "papers/build_prompt_phases/phase_03/parameter_table.md"
    p3eq = "papers/build_prompt_phases/phase_03/equation_registry.csv"
    p3alg = "papers/build_prompt_phases/phase_03/algorithm_pseudocode.md"
    novelty = "papers/build_prompt_phases/phase_04/novelty_scope.md"
    # NLPSR is the ONLY remaining conceptual figure asset. The other four
    # (architecture, SGSM-mechanism, dim-gating, taxonomy) were converted to
    # native inline LaTeX/Word tables during the R2 Ticket-3 DOCX remediation
    # and their matplotlib PDFs were retired and un-tracked - so they are
    # recorded as table-native rows (no output file to hash), matching the
    # frozen governance record.
    concept_rows = [
        ("FIG-NLPSR (plan F-NLPSR)", "fig_nlpsr_schedule",
         "fig:nlpsr-schedule", "papers/scripts/generate_nlpsr_trajectory.py",
         [p3eq, p3param], "supplement", "pending-phase8-rewire (supersedes "
         "figures/traces/nlpsr_trajectory.pdf)"),
    ]
    for aid, stem, label, gscript, srcs, scope, loc in concept_rows:
        add(aid,
            [f"papers/figures/concept/{stem}.pdf",
             f"papers/figures/concept/{stem}.png"],
            "figure-conceptual", label, gscript,
            f"python {gscript}", srcs, checksum_cell(srcs),
            "n/a (authored conceptual art; analytic E5 only for F-NLPSR)",
            scope, loc, concept_word, qa,
            release="n/a (authored; no empirical source)")

    native_qa = ("native-table conversion (R2 Ticket 3): former matplotlib "
                 "asset retired and un-tracked; label renders as a native "
                 "LaTeX tabular / editable Word table; verified no "
                 "\\includegraphics of this artifact remains in the build")
    native_rows = [
        ("FIG-ARCH (plan F-ARCH)",
         "papers/sections/proposed_algorithm.tex (native LaTeX/Word table)",
         "fig:architecture", [specs, p3alg, p3param],
         "Section~3 Architecture Overview; \\label{fig:architecture} "
         "(native tabular, formerly matplotlib PDF)"),
        ("FIG-SGSM-MECH (plan F-SGSM-MECH)",
         "papers/sections/proposed_algorithm.tex (native LaTeX/Word table)",
         "fig:sgsm-mechanism", [specs, p3eq],
         "Section~3 Contribution~C1; \\label{fig:sgsm-mechanism} "
         "(native tabular, formerly matplotlib PDF)"),
        ("FIG-GATING (plan F-GATING)",
         "papers/sections/proposed_algorithm.tex (native LaTeX/Word table)",
         "fig:dim-gating", [specs, p3param, p3alg],
         "Section~3 Dimension Gating; \\label{fig:dim-gating} "
         "(native tabular, formerly matplotlib PDF)"),
        ("FIG-TAXONOMY (plan F-TAXONOMY)",
         "papers/sections/related_work.tex (native LaTeX/Word table)",
         "fig:taxonomy", [specs, novelty],
         "Section~2 Related Work; \\label{fig:taxonomy} "
         "(native tabular, formerly matplotlib PDF)"),
    ]
    for aid, apath, label, srcs, latex_loc in native_rows:
        rows.append({
            "artifact_id": aid,
            "artifact_path": apath,
            "artifact_type": "table-native (converted from figure-conceptual)",
            "manuscript_label": label,
            "generator_script": "n/a (authored inline as native table)",
            "generator_command": "n/a",
            "source_paths": ";".join(srcs),
            "source_checksums": checksum_cell(srcs),
            "analysis_id": ("n/a (authored conceptual art; analytic E5 only "
                            "for F-NLPSR)"),
            "evidence_release_id": "n/a (authored; no empirical source)",
            "commit_sha": commit,
            "output_checksum": "n/a (inline native table; no separate binary asset)",
            "scope": "main",
            "latex_location": latex_loc,
            "word_location": "native w:tbl in DOCX (build_docx.py pandoc tabular path)",
            "validation_status": native_qa,
        })

    # ------------------------------------------------------------------
    # Method artifacts (phase_03 canonical transcriptions)
    # ------------------------------------------------------------------
    p3 = "papers/build_prompt_phases/phase_03"
    # N-015 split the single notation key into a core table plus per-subsystem
    # tables (scaffold, ISM); the RNG substream key is authored inline in the
    # supplement.  All render from the one canonical notation_table.md, so they
    # share a single artifact row whose artifact_path lists every rendered file.
    notation_tex = [f"{p3}/notation_table.tex",
                    f"{p3}/notation_table_scaffold.tex",
                    f"{p3}/notation_table_ism.tex"]
    method_rows = [
        ("ART-NOTATION (plan T-NOTATION)", notation_tex,
         "table-authored", "tab:notation;tab:notation-scaffold;"
         "tab:notation-ism;tab:notation-rng", [f"{p3}/notation_table.md"]),
        ("ART-PSEUDOCODE (plan A1)", f"{p3}/algorithm_pseudocode.tex",
         "algorithm", "alg:dt-gsk", [f"{p3}/algorithm_pseudocode.md"]),
        ("ART-PARAMS (plan T-PARAMS)", f"{p3}/parameter_table.tex",
         "table-authored", "tab:parameters",
         [f"{p3}/parameter_table.md",
          f"{p3}/algorithm_freeze_manifest.json"]),
        ("ART-EQUATIONS (plan E1a-E12)", f"{p3}/equations.tex",
         "equation-set",
         "eq:junior-idx;eq:senior-idx;eq:kexp-schedule;eq:gsk-update;"
         "eq:kr-mask;eq:nlpsr;eq:ace-update;eq:midpoint-repair;"
         "eq:greedy-accept;eq:bse-cauchy;eq:sgsm-graph;eq:eigen-polish;"
         "eq:rng-substreams",
         [f"{p3}/equation_registry.csv"]),
    ]
    for aid, path, atype, label, srcs in method_rows:
        paths = path if isinstance(path, list) else [path]
        add(aid, paths, atype, label,
            "authored transcription (Phase 7 task C; no generator script)",
            "n/a", srcs, checksum_cell(srcs),
            "n/a (method definition; no empirical values)", "main",
            "pending-phase8-rewire", "pending-phase9 (Word native build)",
            "canonical-transcription-verified "
            "(papers/build_prompt_phases/phase_07/"
            "method_artifacts_report.md)",
            release="n/a (authored; no empirical source)")

    # ------------------------------------------------------------------
    # Write
    # ------------------------------------------------------------------
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS)
        w.writeheader()
        for r in rows:
            w.writerow(r)
    print(f"wrote {OUT} ({len(rows)} artifact rows)")


if __name__ == "__main__":
    sys.exit(main())
