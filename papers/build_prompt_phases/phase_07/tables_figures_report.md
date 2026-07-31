# Phase 7 — Tables & Statistical Figures Report (Task B)

Run date: 2026-07-11. Evidence lock: Phase 6 bundle
`papers/analysis/rel-2026-07-10-262fc16c9/` + staging export
`results/paper_tables/` (sole admissible `results/` input; exported
exclusively from the bundle per `results/paper_tables/provenance.json`).
No `results/_run_all`, no `results/_ablation`, no rendered `.tex` was read
as a data source. Zero hand-typed result values.

## 1. Ablation suppression assertion — PASSED

- `generate_latex_tables.py` scans only
  `results/ablation/ablation_matrix_rank_summary*.csv`.
- Asserted before generation: `results/ablation/` does not exist; **0**
  `ablation_matrix_rank_summary*.csv` files anywhere under `results/`
  (checked recursively, including `results/_ablation/`).
- Tooling (named): added `--skip-ablation` flag to
  `papers/scripts/generate_latex_tables.py`; the Phase 7 run used it, so
  the ablation branch never executed. **No ablation .tex produced.**

## 2. Tables regenerated (papers/tables/)

Generator: `python papers/scripts/generate_latex_tables.py --skip-ablation`
(input verified: `results/paper_tables/` only; the script hard-fails if
that directory is absent). Shapes = data rows x value columns of the
emitted `tabular` (excluding the label column).

| Table | File | Input | Shape | Content |
|---|---|---|---|---|
| T1  | T01.tex | T1.csv  | 22 x 10 | CEC2011 head-to-head GSK vs DT-GSK (Best/Median/Worst/Mean/SD) |
| T2  | T02.tex | T2.csv  | 29 x 10 | CEC2017 D10 head-to-head |
| T3  | T03.tex | T3.csv  | 29 x 10 | CEC2017 D30 head-to-head |
| T4  | T04.tex | T4.csv  | 29 x 10 | CEC2017 D50 head-to-head |
| T5  | T05.tex | T5.csv  | 29 x 10 | CEC2017 D100 head-to-head |
| T6  | T06.tex | T6.csv  | 8 x 1   | CEC2011 Wilcoxon summary |
| T7  | T07.tex | T7.csv  | 29 x 7  | GSK-family Mean+-SD, CEC2017 D10 |
| T8  | T08.tex | T8.csv  | 29 x 7  | GSK-family Mean+-SD, CEC2017 D30 |
| T9  | T09.tex | T9.csv  | 29 x 7  | GSK-family Mean+-SD, CEC2017 D50 |
| T10 | T10.tex | T10.csv | 29 x 7  | GSK-family Mean+-SD, CEC2017 D100 |
| T11 | T11.tex | T11.csv | 28 x 10 | CEC2013 D10 head-to-head |
| T12 | T12.tex | T12.csv | 28 x 10 | CEC2013 D30 head-to-head |
| T13 | T13.tex | T13.csv | 28 x 10 | CEC2013 D50 head-to-head |
| T14 | T14.tex | T14.csv | 8 x 3   | CEC2013 per-dim Wilcoxon summary |
| T15 | T15.tex | T15.csv | 6 x 28  | Wilcoxon+Holm+A12 GSK-family, 4 dims x 7 cols |
| T16 | T16.tex | T16.csv | 7 x 5   | Friedman mean ranks D10/D30/D50/D100 + Overall |
| T16_bca | T16_bca.tex | bundle `cec2017/descriptive_stats_cec2017_D{10,30,50,100}.csv` | 7 x 4 | BCa 95% CIs on Friedman mean ranks |

Terminology normalization applied at render time (Phase 4 glossary,
binding): `EGSK -> eGSK` (CR-0003), `FDBAGSK -> FDB-AGSK`.

`generate_t16_bca.py` (rewired, named tooling): now reads per-function mean
errors EXCLUSIVELY from the bundle `descriptive_stats_cec2017_D<dim>.csv`
(previously: `gsk_family.analysis.result_loader`, i.e.
`benchmarks/cec_reference_results/` with `results/_run_all` fallback —
inadmissible under the Phase 7 lock). The distinct inspected BASE_SEED
(20260422) rank-CI bootstrap scheme (midrank per-function Friedman ranks,
n_boot=10000, BCa 95%) is kept; rows reordered to the pre-registered P1
panel order; F2 excluded; missing bundle input = hard fail.
Cross-consistency check: T16_bca point estimates reproduce T16's mean
ranks exactly at 2-decimal display (e.g. DT-GSK D50 2.21, eGSK D30 2.29).

## 3. Nemenyi CD diagrams (papers/figures/nemenyi/)

`papers/scripts/generate_nemenyi_cd.py` REWIRED (named tooling): reads
UNROUNDED mean ranks from bundle
`cec2017/friedman_ranks_cec2017_D<dim>.csv` (never T16.tex; the old
.tex-parsing path was removed); recomputed CD is cross-checked against the
bundle's `nemenyi_cd_cec2017_D<dim>.csv` (hard fail on mismatch — all four
matched, CD = 1.6730, k=7, N=29, q_0.05=2.949); a CD diagram is emitted
only when the bundle's Friedman omnibus p < 0.05 (post-hoc gate).

| Dim | Omnibus p | Emitted | Files |
|---|---|---|---|
| D10  | 2.577e-08 | yes | nemenyi_cd_cec2017_D10.pdf / .png |
| D30  | 1.152e-10 | yes | nemenyi_cd_cec2017_D30.pdf / .png |
| D50  | 6.763e-11 | yes | nemenyi_cd_cec2017_D50.pdf / .png |
| D100 | 1.424e-12 | yes | nemenyi_cd_cec2017_D100.pdf / .png |

All four omnibus tests significant, so all four diagrams emitted
(8 files). Within-one-CD-of-best cohorts (from stdout): D10 best DT-GSK
{DT-GSK, AGSK, FDB-AGSK, APGSK, eGSK}; D30 best eGSK {eGSK, DT-GSK};
D50 best DT-GSK {DT-GSK, eGSK}; D100 best DT-GSK {DT-GSK, eGSK,
ATMALS-GSK}.

## 4. Rank charts (papers/figures/ranks/)

`papers/scripts/generate_rank_charts.py` REWIRED (named tooling) to the
bundle; hard-fails on any missing input or missing panel algorithm.

| Figure label | Files | Input |
|---|---|---|
| fig:rank-vs-dim | rank_vs_dim_cec2017.pdf / .png | bundle `cec2017/rank_trend_cec2017.csv` (7 lines, P1 legend order, P3 color/linestyle map, dt-gsk solid black 1.5x) |
| fig:cec2017-ranks | cec2017_mean_ranks.pdf / .png | bundle `cec2017/friedman_ranks_cec2017_D{10,30,50,100}.csv` (grouped bars, P1 order, P3 colors, one shared legend) |
| fig:cec2011-ranks | cec2011_ranks.pdf / .png | bundle `cec2011/friedman_ranks_cec2011.csv` (sorted barh, 22 problems) |
| fig:friedman_bar_gsk (legacy overall) | friedman_gsk_family.pdf / .png | staging `results/paper_tables/T16.csv` Overall_MeanRank (admissible staging export) |

8 files produced. Legacy `papers/figures/ranks/nemenyi_cd_d50.pdf` is
superseded (see table_dispositions.md) and was not regenerated.

## 5. Determinism & output contract

- All PDFs written with `metadata={"CreationDate": None}`; verified 0
  occurrences of `CreationDate` in every produced PDF. Fixed filenames, no
  timestamps in artifact content.
- PNG alternates at 300 dpi (>= 200 dpi contract).
- Figure labels use glossary display names (eGSK, FDB-AGSK, ATMALS-GSK).

## 6. Dispositions (see table_dispositions.md)

- T21/T22: NOT-GENERATED (EG-006, no admissible sensitivity release);
  `generate_parametric_tables.py` NOT run; its output destination verified
  already fixed (`papers/tables/`). Stale legacy T21.tex/T22.tex flagged.
- T17–T20: do-not-create rule recorded.
- generate_trace_figures.py / generate_adaptive_params_panel.py: NOT run
  (diagnostic-release-gated; no promoted GenLog release exists).
- Ablation: suppressed; assertion passed; no ablation artifact of any kind.

## 7. Tooling changes (all pass `ruff check`)

1. `papers/scripts/generate_latex_tables.py`: added `--skip-ablation`
   argparse flag; added display-name normalization (EGSK->eGSK,
   FDBAGSK->FDB-AGSK) for T7–T10 headers and T15/T16 row labels.
2. `papers/scripts/generate_t16_bca.py`: input rewired to the Phase 6
   bundle descriptive stats; P1 row order; hard-fail on missing input;
   BASE_SEED BCa scheme unchanged.
3. `papers/scripts/generate_nemenyi_cd.py`: full rewrite of the input and
   loop layer — bundle friedman CSVs (unrounded ranks), omnibus gate,
   bundle-CD cross-check, 4 dims, PDF+PNG, deterministic metadata; render
   style preserved.
4. `papers/scripts/generate_rank_charts.py`: rewired to bundle; added
   fig:rank-vs-dim, fig:cec2017-ranks, fig:cec2011-ranks generators with
   P1/P3 pre-registered styling; PDF+PNG, deterministic metadata; legacy
   overall chart kept on staging T16.csv.
