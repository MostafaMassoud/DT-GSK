# Phase 7 exhibit validation report (task 12)

Verdict: **PASS** -- 0 mismatch(es); 4349 value-level comparisons.

Authoritative sources: the promoted benchmark export `benchmarks/cec_reference_results/_paper_tables/` (single source of truth; exported exclusively from the Phase 6 bundle, then promoted from results/paper_tables/ staging, per `provenance.json`), the bundle `papers/analysis/rel-2026-07-10-262fc16c9/`, and (for convergence, per pre-registration P2) `benchmarks/cec_reference_results/` gen_logs. Tolerance = display rounding only (generator formatting rules re-applied; string equality required). No `results/_run_all`, no `results/_ablation`, no rendered `.tex` used as a data source.

## Checks

| Check | Comparisons |
|---|---|
| T01.tex (head-to-head, CEC2011) | 220 |
| T02.tex (head-to-head, CEC17-D10) | 290 |
| T03.tex (head-to-head, CEC17-D30) | 290 |
| T04.tex (head-to-head, CEC17-D50) | 290 |
| T05.tex (head-to-head, CEC17-D100) | 290 |
| T06.tex (CEC2011 Wilcoxon summary) | 8 |
| T07.tex (family Mean+-SD, D10) | 406 |
| T08.tex (family Mean+-SD, D30) | 406 |
| T09.tex (family Mean+-SD, D50) | 406 |
| T10.tex (family Mean+-SD, D100) | 406 |
| T11.tex (head-to-head, CEC2013 D10) | 280 |
| T12.tex (head-to-head, CEC2013 D30) | 280 |
| T13.tex (head-to-head, CEC2013 D50) | 280 |
| T14.tex (CEC2013 Wilcoxon per-dim) | 24 |
| T15.tex (Wilcoxon+Holm+A12 family) | 168 |
| T16.tex (Friedman mean ranks) | 35 |
| T16_bca.tex (seeded BCa re-derivation) | 84 |
| Nemenyi CD diagrams D10/30/50/100 (PDF text vs bundle) | 32 |
| Rank charts (rank_trend/T16 cross-check + PDF text) | 70 |
| Convergence sample: 6 panels x 7 algorithms (endpoints vs recomputed checkpoint means + bundle) | 84 |

## Method notes

- T01--T05, T11--T13: every Best/Median/Worst/Mean/SD cell re-formatted from the staged CSV (`_fmt_sci` 2-dp scientific) and string-compared; `\bestval` bold-mean marker position re-derived and asserted.
- T07--T10: every Mean and SD cell compared (2 comparisons per table cell); bolded best-mean column re-derived.
- T14/T15/T16: generator formatting rules replicated exactly (4-dp p, 3-dp A12, 2-dp ranks, T14 mixed-format rule); T16 per-column best markers re-derived.
- T16_bca: full end-to-end re-derivation (bundle descriptive stats -> midrank Friedman ranks -> seeded BCa bootstrap, BASE_SEED=20260422, n_boot=10000) rendered to LaTeX and compared byte-for-byte with the published file; point estimates cross-checked against staged T16.csv at 2-dp display.
- Nemenyi: PDF text extracted (pypdf); the 7 rank value labels, rank-sorted algorithm ordering, CD scale-bar value, and N block count compared against the bundle friedman/nemenyi CSVs; CD recomputed (k=7, q_0.05=2.949); omnibus gate re-checked.
- Rank charts: bundle `rank_trend_cec2017.csv` cross-checked value-by-value against the four per-dimension friedman CSVs (exact) and staged `T16.csv` (<=5e-7, its 6-dp storage); `cec2011_ranks.pdf` / `friedman_gsk_family.pdf` numeric bar labels extracted and matched. `rank_vs_dim_cec2017.pdf` and `cec2017_mean_ranks.pdf` carry no numeric text labels; their data path is covered by the same source cross-checks (identical loader inputs), disclosed here rather than claimed as pixel checks.
- Convergence: 6 sampled panels (D30 F3/F10/F12/F26 = the frozen P5 main-text selection; D100 F1/F12) x 7 algorithms; full mean series recomputed independently (plain csv arithmetic) and compared to the plotting loader at rel_tol=1e-12, and endpoints compared to the bundle aggregated curves at their 7-significant-digit storage precision; n_runs asserted equal.

## Mismatches

(none)
