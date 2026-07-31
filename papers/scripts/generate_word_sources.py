"""Emit Word-native semantic table sources (Phase 7, task C.4 / task 9).

For each staged manuscript table T1-T16 (plus the T16_bca BCa companion)
this script writes ``papers/tables/word_sources/<T>.json`` -- a SEMANTIC
(machine-readable, non-rendered) source from which Phase 9 builds native
Word tables. Cell values are transcribed VERBATIM from the admissible
staging CSVs; this script performs no arithmetic and types no result value.

Admissible inputs ONLY:
  * ``benchmarks/cec_reference_results/_paper_tables/T{1..16}.csv`` -- the
    promoted benchmark evidence (Phase 6 task 23 export from the controlled
    analysis bundle, promoted from results/paper_tables/ staging; see
    benchmarks/cec_reference_results/_paper_tables/provenance.json).
  * ``papers/analysis/rel-2026-07-10-262fc16c9/cec2017/headline_bca.csv``
    for T16_bca -- the registry-defined T-BCA union companion (bundle
    ``table_to_csv_map.md``; verified byte-equal to the concatenation of
    bca_ci_cec2017_D10..D100.csv). The legacy ``papers/tables/T16_bca.tex``
    (BCa CIs on Friedman mean ranks) is STALE and its generator
    (``generate_t16_bca.py``) reads inadmissible sources
    (``gsk_family.analysis.result_loader`` with a results/_run_all
    fallback); it is NOT used here.

Missing input => HARD FAIL (SystemExit), never a silent skip.

Determinism: fixed filenames, fixed key order, no timestamps; sha256 of each
source CSV is recorded in the JSON.

Usage::

    python papers/scripts/generate_word_sources.py
"""
from __future__ import annotations

import csv
import hashlib
import json
import os
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PAPER_DIR = SCRIPT_DIR.parent
PROJECT_ROOT = PAPER_DIR.parent

# Consumer input = the PROMOTED, frozen benchmark evidence (single source of
# truth), not the results/ staging that producers write.  Repointed from
# results/paper_tables -> benchmarks/cec_reference_results/_paper_tables.
STAGING = PROJECT_ROOT / "benchmarks" / "cec_reference_results" / "_paper_tables"
_REL_ID = os.environ.get("GSK_REL_ID", "rel-2026-07-16-78f075cb0")
BUNDLE = PAPER_DIR / "analysis" / _REL_ID
OUT_DIR = PAPER_DIR / "tables" / "word_sources"

RELEASE_NOTE = (
    "values transcribed verbatim from the Phase 6 export of release "
    f"{_REL_ID}; see "
    "benchmarks/cec_reference_results/_paper_tables/provenance.json"
)
PANEL_NOTE = (
    "panel order P1: gsk, agsk, apgsk, fdb-agsk, atmals-gsk, egsk, dt-gsk; "
    "all comparative wording scoped to the GSK-family panel"
)
TERMINOLOGY_NOTE = (
    "display names at Word build time MUST apply the frozen Phase 4 "
    "glossary: EGSK -> eGSK, FDBAGSK -> FDB-AGSK (headers/rows here are "
    "verbatim CSV identifiers, not display names)"
)

# table_id -> (source path, manuscript_label, caption_stub, number_format,
#              extra notes)
TABLES: dict[str, tuple[Path, str, str, str, list[str]]] = {
    "T1": (STAGING / "T1.csv", "Table 1",
           "CEC2011 real-world suite (22 problems, 25 runs, MaxFES=150000): "
           "GSK vs DT-GSK descriptive statistics (Best/Median/Mean/Worst/SD,"
           " best-fitness basis).",
           "%.6e", ["best_fitness basis (CEC2011 error undefined on problems "
                    "without published optima)"]),
    "T2": (STAGING / "T2.csv", "Table 2",
           "CEC2017 D=10 (29 functions, 51 runs): GSK vs DT-GSK "
           "head-to-head descriptive statistics.", "%.6e", []),
    "T3": (STAGING / "T3.csv", "Table 3",
           "CEC2017 D=30 (29 functions, 51 runs): GSK vs DT-GSK "
           "head-to-head descriptive statistics.", "%.6e", []),
    "T4": (STAGING / "T4.csv", "Table 4",
           "CEC2017 D=50 (29 functions, 51 runs): GSK vs DT-GSK "
           "head-to-head descriptive statistics.", "%.6e", []),
    "T5": (STAGING / "T5.csv", "Table 5",
           "CEC2017 D=100 (29 functions, 51 runs): GSK vs DT-GSK "
           "head-to-head descriptive statistics.", "%.6e", []),
    "T6": (STAGING / "T6.csv", "Table 6",
           "CEC2011 Wilcoxon signed-rank summary, DT-GSK vs GSK "
           "(R+/R-, p-value, win/tie/loss).", "as-is",
           ["R+ = rank sum favoring DT-GSK; ties |d|<1e-8 dropped"]),
    "T7": (STAGING / "T7.csv", "Table 7",
           "CEC2017 D=10: GSK-family panel Mean and SD per function "
           "(7 algorithms).", "%.6e", [PANEL_NOTE]),
    "T8": (STAGING / "T8.csv", "Table 8",
           "CEC2017 D=30: GSK-family panel Mean and SD per function "
           "(7 algorithms).", "%.6e", [PANEL_NOTE]),
    "T9": (STAGING / "T9.csv", "Table 9",
           "CEC2017 D=50: GSK-family panel Mean and SD per function "
           "(7 algorithms).", "%.6e", [PANEL_NOTE]),
    "T10": (STAGING / "T10.csv", "Table 10",
            "CEC2017 D=100: GSK-family panel Mean and SD per function "
            "(7 algorithms).", "%.6e", [PANEL_NOTE]),
    "T11": (STAGING / "T11.csv", "Table 11",
            "CEC2013 second comparison suite, D=10 (28 functions, 51 runs): "
            "GSK vs DT-GSK descriptive statistics.", "%.6e",
            ["CEC2013 is the second comparison suite (never worded "
             "independent/holdout/validation)"]),
    "T12": (STAGING / "T12.csv", "Table 12",
            "CEC2013 second comparison suite, D=30 (28 functions, 51 runs): "
            "GSK vs DT-GSK descriptive statistics.", "%.6e",
            ["CEC2013 is the second comparison suite (never worded "
             "independent/holdout/validation)"]),
    "T13": (STAGING / "T13.csv", "Table 13",
            "CEC2013 second comparison suite, D=50 (28 functions, 51 runs): "
            "GSK vs DT-GSK descriptive statistics.", "%.6e",
            ["CEC2013 is the second comparison suite (never worded "
             "independent/holdout/validation)"]),
    "T14": (STAGING / "T14.csv", "Table 14",
            "CEC2013 per-dimension Wilcoxon signed-rank summary, DT-GSK vs "
            "GSK (R+/R-, p-value, win/tie/loss; D=10/30/50).", "as-is",
            ["R+ favors DT-GSK; ties |d|<1e-8 dropped"]),
    "T15": (STAGING / "T15.csv", "Table 15",
            "CEC2017 pairwise Wilcoxon + Holm outcomes, DT-GSK vs each "
            "GSK-family comparator per dimension (p, Holm-adjusted p, "
            "win/tie/loss, A12, decision).", "as-is",
            [PANEL_NOTE, "A12 > 0.5 favors DT-GSK; ties |d|<1e-8 half"]),
    "T16": (STAGING / "T16.csv", "Table 16",
            "CEC2017 Friedman mean ranks per dimension and overall "
            "(GSK-family panel; overall = descriptive mean of per-dimension "
            "ranks, no test attached).", "as-is", [PANEL_NOTE]),
    "T16_bca": (BUNDLE / "cec2017" / "headline_bca.csv",
                "Table 16 (BCa companion)",
                "BCa 95% bootstrap confidence intervals on paired "
                "mean-error differences, DT-GSK vs each GSK-family "
                "comparator, CEC2017 per function and dimension (B=10000 "
                "where defined; degenerate and disclosed-unavailable cells "
                "carry availability flags).", "as-is",
                ["registry-defined T-BCA union companion (bundle "
                 "table_to_csv_map.md); byte-equal to the concatenation of "
                 "bca_ci_cec2017_D10..D100.csv",
                 "DISTINCT ESTIMAND, machine-readable companion only: this JSON "
                 "holds per-function BCa CIs on paired mean-error DIFFERENCES. "
                 "The tab:bca-ci table shown in BOTH the PDF and the DOCX is the "
                 "rank-stability version rendered from papers/tables/T16_bca.tex "
                 "(BCa CIs on Friedman mean ranks), which is current, reads the "
                 "promoted release, and drives both formats via build_docx's "
                 "frozen-tex path; this JSON is NOT the source of the rendered "
                 "tab:bca-ci table (STAT-001, corrected 2026-07-23)",
                 PANEL_NOTE]),
}


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def main() -> None:
    missing = [str(p) for p, *_ in TABLES.values() if not p.exists()]
    if missing:
        raise SystemExit(
            "HARD FAIL — admissible source CSV(s) missing (never skipped, "
            "never interpolated): " + "; ".join(missing))

    # Head-to-head tables: SIDE-BY-SIDE algorithm groups (2026-07-24 author
    # request -- Function | GSK {5 stats} | DT-GSK (Proposed) {5 stats}). The DOCX
    # source must match the .tex row-for-row so cross-format parity stays 1:1.
    H2H_IDS = {"T1", "T2", "T3", "T4", "T5", "T11", "T12", "T13"}
    # Source CSV order after Func: Best_GSK,Best_DT,Median_GSK,Median_DT,
    # Mean_GSK,Mean_DT,Worst_GSK,Worst_DT,SD_GSK,SD_DT (idx 0..9). Display order
    # Best/Median/Worst/Mean/SD -> GSK idx [0,2,6,4,8], DT-GSK idx [1,3,7,5,9].
    _GSK = [0, 2, 6, 4, 8]
    _DT = [1, 3, 7, 5, 9]

    def _to_sidebyside_rows(rows):
        out = []
        for r in rows[1:]:
            body = r[1:]
            if len(body) < 10:
                continue
            out.append([r[0]] + [body[i] for i in _GSK] + [body[i] for i in _DT])
        header = ["Function", "Best", "Median", "Worst", "Mean", "SD",
                  "Best", "Median", "Worst", "Mean", "SD"]
        return header, out

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for table_id, (src, label, caption, numfmt, extra) in TABLES.items():
        with src.open(newline="", encoding="utf-8") as fh:
            rows = list(csv.reader(fh))
        if not rows:
            raise SystemExit(f"HARD FAIL — empty source CSV: {src}")
        if table_id in H2H_IDS:
            h2h_header, h2h_rows = _to_sidebyside_rows(rows)
            rows = [h2h_header] + h2h_rows
        if table_id == "T14":
            # Display policy: p-values below 1e-4 are bounded, never raw
            # (performance.tex / SAP Sec. 4). The .tex generator bounds them
            # (R3-20); the DOCX source must carry the same parity token that
            # SA03's generator emits ("<10^-4"), or cross-format parity breaks.
            for row in rows[1:]:
                if row and row[0].strip() in ("p_value", "p_holm"):
                    for i, cell in enumerate(row[1:], start=1):
                        try:
                            if float(cell) < 1e-4:
                                row[i] = "<10^-4"
                        except ValueError:
                            pass
        payload = {
            "table_id": table_id,
            "manuscript_label": label,
            "caption_stub": caption,
            "headers": [rows[0]],
            "rows": rows[1:],
            "notes": [RELEASE_NOTE, TERMINOLOGY_NOTE, *extra],
            "number_format": numfmt,
            "source_csv": src.relative_to(PROJECT_ROOT).as_posix(),
            "source_sha256": sha256_of(src),
        }
        out = OUT_DIR / f"{table_id}.json"
        out.write_text(json.dumps(payload, indent=1, ensure_ascii=False)
                       + "\n", encoding="utf-8")
        print(f"wrote {out}  ({len(rows) - 1} data rows)")


if __name__ == "__main__":
    main()
