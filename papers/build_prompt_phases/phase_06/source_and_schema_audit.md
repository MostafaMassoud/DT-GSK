# Phase 6 — Source-use audit and schema-conformance audit (task 19)

- **Date:** 2026-07-10. **Auditor:** Phase 6 validation pass (read-only; no analysis output modified).
- **Bundle audited:** `papers/analysis/rel-2026-07-10-262fc16c9/` (release rel-2026-07-10-262fc16c9, anchor commit `262fc16c91fbe5608a1a0b0c5df3cbcd009edc21`).
- **Binding references:** `phase_05/statistical_analysis_plan.md`, `phase_05/analysis_registry.csv`, `phase_05/analysis_output_schemas/*.schema.md`, `phase_05/strict_source_execution.md` (Sec. 5 naming/sorting/precision), `phase_05/curve_selection_rule.md`, `phase_05/robustness_plan.md`, `phase_05/source_resolution_map.csv`, PAPER_BUILD_PROMPT Sec. 7.14.
- **Audit tooling:** standalone read-only script (scratchpad `audit_task19.py`), Python + numpy; every CSV parsed with the csv module; reconstruction census reads release `per_run.csv` files directly.

## Verdict summary

| Category | Checks | PASS | FAIL | Verdict |
|---|---|---|---|---|
| Source audit (strict-source provenance) | 18 | 18 | 0 | **PASS** |
| Schema conformance | 727 | 727 | 0 | **PASS** |
| Denominators (function/run counts) | 122 | 122 | 0 | **PASS** |
| Raw-to-summary reconstruction | 6 | 5 | 1 | **PASS (with 1 disclosed storage-precision exception, 0 substantive discrepancies)** |
| **Total** | **873** | **872** | **1** | |

**Overall: PASS.** All empirical inputs trace exclusively to `benchmarks/cec_reference_results/`; zero `results/` or `results/_ablation/` inputs anywhere; every emitted CSV conforms to its pre-registered schema family (columns, sort order, `%.6e` float format, `n/a` literals, status columns for disclosed-unavailable cells, range constraints); all denominators are exactly 29/28/22 functions and 51/51/25 runs; raw-to-summary reconstruction agrees at 1e-9 relative for 1435/1467 cells with the remaining 32 bounded by the release files' own storage rounding (max scaled discrepancy 2.7e-07, all below the %.6e reporting precision; 0 substantive discrepancies). No confirmatory amendment required; no deviation from the frozen plan was found in the bundle.

## Category 1 — Source audit — **PASS**

Inputs parsed: `cec2017/source_use_log.json` (847 opened paths), `cec2013/source_use_log.json` (224), `cec2011/source_use_log.json` (168) — 1,239 opened-path records total — plus the 8 robustness `*_source_audit.json` companions and the top-level `source_precheck.json`. No `analysis_source_use.log` exists in the bundle (the JSON logs are the artifact of record per strict_source_execution.md Sec. 2). `primary_stats/statistical_results.csv` `source_paths` columns were also swept for forbidden prefixes. The `results/paper_tables/` export area is a WRITE target of Phase 6 task 23, not an input; it does not appear in any opened-path record.

| Check | Result | Detail |
|---|---|---|
| source_use_log.json present per suite | PASS | found 3: ['papers\\analysis\\rel-2026-07-10-262fc16c9\\cec2011\\source_use_log.json', 'papers\\analysis\\rel-2026-07-10-262fc16c9\\cec2013\\source_use_log.json', 'papers\\analysis\\rel-2026-07-10-262fc16c9\\cec2017\\source_use_log.json'] |
| cec2011: strict_source flag | PASS | strict_source=True, status=ok |
| cec2011: status ok | PASS | status=ok |
| cec2011: release/anchor | PASS | release=rel-2026-07-10-262fc16c9, anchor=262fc16c91fbe5608a1a0b0c5df3cbcd009edc21 |
| cec2013: strict_source flag | PASS | strict_source=True, status=ok |
| cec2013: status ok | PASS | status=ok |
| cec2013: release/anchor | PASS | release=rel-2026-07-10-262fc16c9, anchor=262fc16c91fbe5608a1a0b0c5df3cbcd009edc21 |
| cec2017: strict_source flag | PASS | strict_source=True, status=ok |
| cec2017: status ok | PASS | status=ok |
| cec2017: release/anchor | PASS | release=rel-2026-07-10-262fc16c9, anchor=262fc16c91fbe5608a1a0b0c5df3cbcd009edc21 |
| all opened paths under benchmarks/cec_reference_results | PASS | 1239 opened paths across 3 suite logs; outside-release=0 |
| zero results/ or _ablation/ inputs | PASS | paths containing results/ or _ablation/: 0 |
| roles from fixed vocabulary | PASS | non-vocabulary roles: none |
| robustness *_source_audit.json inputs under release | PASS | 8 audit files, 0 opened paths, outside-release=0 |
| robustness audits: new_opens all under release (or empty with cache note referring to the verified suite log) | PASS | all 8 files record new_opens=[] with note 'inputs otherwise served from the in-process cache of audited release reads; full log in cec2017/source_use_log.json' (that suite log verified above: 847/847 paths under the release) |
| no additional analysis_source_use.log present | PASS | only source_use_log.json + robustness *_source_audit.json exist |
| source_precheck.json references only release paths | PASS | top-level precheck inspected |
| primary_stats\statistical_results.csv: source_paths release-relative, zero results/ | PASS | 4987 rows; violations=0 |

## Category 2 — Schema conformance — **PASS**

Every CSV under the bundle was checked against its family schema: the 7 schema docs in `analysis_output_schemas/` (descriptive_stats, friedman_ranks, wilcoxon_holm/wilcoxon_run, effect_sizes, bca_ci, convergence_checkpoints, curve_selection) plus the plan-governed families (cost = SAP Sec. 9, rank_trend = SAP Sec. 12, class_ranks = SAP Sec. 11, nemenyi_cd = SAP Sec. 5 conditional companion, robustness = robustness_plan.md Secs. 1.0/3-4, statistical_results = PAPER_BUILD_PROMPT Sec. 7.14). Checked per file: exact column set and order; fixed sort (suite, dimension asc, function asc, algorithm/comparator in P1 order gsk, agsk, apgsk, fdb-agsk, atmals-gsk, egsk, dt-gsk); float format C-locale `%.6e`; integers plain; missing cells literal `n/a`; p-values stored unrounded in (0,1] (the 1e-4 display floor is render-time only per SAP precision policy — files verifiably carry unrounded p < 1e-4 values, and no CSV contains a floored `< 1.0e-4` string); Holm/BH adjusted >= raw; status/availability columns present with closed vocabulary; apgsk CEC2017 D10/D30/D50 run-level cells emitted as disclosed-unavailable rows (never dropped, never imputed); ranks in [1,7]; A12 in [0,1]; Cliff's delta = 2*A12-1 in [-1,1]; BCa B=10000 with the literal seed-scheme tag; no timestamps inside any output CSV; closed filename vocabulary.

Two pre-registered filename exceptions outside the `<family>_<suite>[_D<dim>][_<qualifier>].csv` pattern, both accounted for: `primary_stats/statistical_results.csv` (mandated by PAPER_BUILD_PROMPT Sec. 7.14 / SAP Sec. 12) and `cec2017/headline_bca.csv` (verified byte-equal to the concatenation of `bca_ci_cec2017_D10..D100.csv`; the registry-defined T-BCA union companion). Neither introduces new numbers.

<details><summary>All 727 schema checks (click to expand)</summary>

| Check | Result | Detail |
|---|---|---|
| cec2017\descriptive_stats_cec2017_D10.csv: columns | PASS | 10 columns exact |
| cec2017\descriptive_stats_cec2017_D10.csv: float format %.6e (n/a allowed) | PASS | violations=0 |
| cec2017\descriptive_stats_cec2017_D10.csv: integer columns plain ints | PASS | violations=0 |
| cec2017\descriptive_stats_cec2017_D10.csv: suite column constant | PASS | values=['cec2017'] |
| cec2017\descriptive_stats_cec2017_D10.csv: dimension column constant | PASS | values=['10'] |
| cec2017\descriptive_stats_cec2017_D10.csv: sort order | PASS | function asc, algorithm P1 |
| cec2017\descriptive_stats_cec2017_D10.csv: source_path release-relative and resolvable | PASS | violations=0 (paths resolve under benchmarks/cec_reference_results/) |
| cec2017\friedman_ranks_cec2017_D10.csv: columns | PASS | 8 columns exact |
| cec2017\friedman_ranks_cec2017_D10.csv: float format %.6e (n/a allowed) | PASS | violations=0 |
| cec2017\friedman_ranks_cec2017_D10.csv: integer columns plain ints | PASS | violations=0 |
| cec2017\friedman_ranks_cec2017_D10.csv: suite column constant | PASS | values=['cec2017'] |
| cec2017\friedman_ranks_cec2017_D10.csv: dimension column constant | PASS | values=['10'] |
| cec2017\friedman_ranks_cec2017_D10.csv: 7 rows P1 order | PASS | algs=['gsk', 'agsk', 'apgsk', 'fdb-agsk', 'atmals-gsk', 'egsk', 'dt-gsk'] |
| cec2017\friedman_ranks_cec2017_D10.csv: mean_rank in [1,7] | PASS | range [2.8793,5.5172] |
| cec2017\friedman_ranks_cec2017_D10.csv: sum(mean_rank)=k(k+1)/2=28 (within %.6e storage rounding) | PASS | sum=27.999999 |
| cec2017\friedman_ranks_cec2017_D10.csv: p_value in [0,1], repeated per row | PASS | p=2.576884e-08 |
| cec2017\friedman_ranks_cec2017_D10.csv: dimension=10 | PASS | dimension values=['10'] |
| cec2017\nemenyi_cd_cec2017_D10.csv: columns | PASS | 8 columns exact |
| cec2017\nemenyi_cd_cec2017_D10.csv: float format %.6e (n/a allowed) | PASS | violations=0 |
| cec2017\nemenyi_cd_cec2017_D10.csv: integer columns plain ints | PASS | violations=0 |
| cec2017\nemenyi_cd_cec2017_D10.csv: suite column constant | PASS | values=['cec2017'] |
| cec2017\nemenyi_cd_cec2017_D10.csv: dimension column constant | PASS | values=['10'] |
| cec2017\nemenyi_cd_cec2017_D10.csv: 7 rows P1 order | PASS | algs=['gsk', 'agsk', 'apgsk', 'fdb-agsk', 'atmals-gsk', 'egsk', 'dt-gsk'] |
| cec2017\nemenyi_cd_cec2017_D10.csv: k=7 | PASS | k column |
| cec2017\nemenyi_cd_cec2017_D10.csv: mean_rank in [1,7] | PASS | range [2.8793,5.5172] |
| cec2017\nemenyi_cd_cec2017_D10.csv: conditional emission (omnibus p<0.05) | PASS | Iman-Davenport p=2.576884e-08 |
| cec2017\nemenyi_cd_cec2017_D10.csv: mean_rank matches friedman file | PASS | cross-file consistency |
| cec2017\wilcoxon_holm_cec2017_D10.csv: columns | PASS | 11 columns exact |
| cec2017\wilcoxon_holm_cec2017_D10.csv: float format %.6e (n/a allowed) | PASS | violations=0 |
| cec2017\wilcoxon_holm_cec2017_D10.csv: integer columns plain ints | PASS | violations=0 |
| cec2017\wilcoxon_holm_cec2017_D10.csv: suite column constant | PASS | values=['cec2017'] |
| cec2017\wilcoxon_holm_cec2017_D10.csv: dimension column constant | PASS | values=['10'] |
| cec2017\wilcoxon_holm_cec2017_D10.csv: test_level | PASS | values=['across_functions_funclevel'] |
| cec2017\wilcoxon_holm_cec2017_D10.csv: 6 comparator rows, function=0 | PASS | 6 rows |
| cec2017\wilcoxon_holm_cec2017_D10.csv: comparator P1 order | PASS | ['gsk', 'agsk', 'apgsk', 'fdb-agsk', 'atmals-gsk', 'egsk'] |
| cec2017\wilcoxon_holm_cec2017_D10.csv: p_raw in (0,1], never 0 | PASS | violations=0; 0 rows carry unrounded p<1e-4 (floor is render-time only) |
| cec2017\wilcoxon_holm_cec2017_D10.csv: p_holm >= p_raw | PASS | violations=0 |
| cec2017\wilcoxon_holm_cec2017_D10.csv: outcome vocabulary | PASS | values=['tie', 'win'] |
| cec2017\wilcoxon_holm_cec2017_D10.csv: availability vocabulary | PASS | values=['ok'] |
| cec2017\wilcoxon_run_cec2017_D10.csv: columns | PASS | 11 columns exact |
| cec2017\wilcoxon_run_cec2017_D10.csv: float format %.6e (n/a allowed) | PASS | violations=0 |
| cec2017\wilcoxon_run_cec2017_D10.csv: integer columns plain ints | PASS | violations=0 |
| cec2017\wilcoxon_run_cec2017_D10.csv: suite column constant | PASS | values=['cec2017'] |
| cec2017\wilcoxon_run_cec2017_D10.csv: dimension column constant | PASS | values=['10'] |
| cec2017\wilcoxon_run_cec2017_D10.csv: test_level | PASS | values=['per_function_runlevel'] |
| cec2017\wilcoxon_run_cec2017_D10.csv: sort order | PASS | function asc, comparator P1 |
| cec2017\wilcoxon_run_cec2017_D10.csv: p_raw in (0,1], never 0 | PASS | violations=0; 75 rows carry unrounded p<1e-4 (floor is render-time only) |
| cec2017\wilcoxon_run_cec2017_D10.csv: p_holm >= p_raw | PASS | violations=0 |
| cec2017\wilcoxon_run_cec2017_D10.csv: outcome vocabulary | PASS | values=['loss', 'n/a', 'tie', 'win'] |
| cec2017\wilcoxon_run_cec2017_D10.csv: availability vocabulary | PASS | values=['disclosed-unavailable', 'ok'] |
| cec2017\wilcoxon_run_cec2017_D10.csv: apgsk rows disclosed-unavailable (A2-004) | PASS | 29 apgsk rows present, all n/a cells with status column |
| cec2017\wilcoxon_run_cec2017_D10_exploratory_bh.csv: columns | PASS | 11 columns exact |
| cec2017\wilcoxon_run_cec2017_D10_exploratory_bh.csv: float format %.6e (n/a allowed) | PASS | violations=0 |
| cec2017\wilcoxon_run_cec2017_D10_exploratory_bh.csv: integer columns plain ints | PASS | violations=0 |
| cec2017\wilcoxon_run_cec2017_D10_exploratory_bh.csv: suite column constant | PASS | values=['cec2017'] |
| cec2017\wilcoxon_run_cec2017_D10_exploratory_bh.csv: dimension column constant | PASS | values=['10'] |
| cec2017\wilcoxon_run_cec2017_D10_exploratory_bh.csv: test_level | PASS | values=['per_function_runlevel'] |
| cec2017\wilcoxon_run_cec2017_D10_exploratory_bh.csv: sort order | PASS | function asc, comparator P1 |
| cec2017\wilcoxon_run_cec2017_D10_exploratory_bh.csv: p_raw in (0,1], never 0 | PASS | violations=0; 75 rows carry unrounded p<1e-4 (floor is render-time only) |
| cec2017\wilcoxon_run_cec2017_D10_exploratory_bh.csv: p_bh >= p_raw | PASS | violations=0 |
| cec2017\wilcoxon_run_cec2017_D10_exploratory_bh.csv: outcome vocabulary | PASS | values=['loss', 'n/a', 'tie', 'win'] |
| cec2017\wilcoxon_run_cec2017_D10_exploratory_bh.csv: availability vocabulary | PASS | values=['disclosed-unavailable', 'ok'] |
| cec2017\wilcoxon_run_cec2017_D10_exploratory_bh.csv: apgsk rows disclosed-unavailable (A2-004) | PASS | 29 apgsk rows present, all n/a cells with status column |
| cec2017\effect_sizes_cec2017_D10.csv: columns | PASS | 9 columns exact |
| cec2017\effect_sizes_cec2017_D10.csv: float format %.6e (n/a allowed) | PASS | violations=0 |
| cec2017\effect_sizes_cec2017_D10.csv: integer columns plain ints | PASS | violations=0 |
| cec2017\effect_sizes_cec2017_D10.csv: suite column constant | PASS | values=['cec2017'] |
| cec2017\effect_sizes_cec2017_D10.csv: dimension column constant | PASS | values=['10'] |
| cec2017\effect_sizes_cec2017_D10.csv: sort order | PASS | function asc, comparator P1 |
| cec2017\effect_sizes_cec2017_D10.csv: a12 in [0,1] | PASS | violations=0 |
| cec2017\effect_sizes_cec2017_D10.csv: cliffs_delta=2*a12-1 in [-1,1] | PASS | violations=0 |
| cec2017\effect_sizes_cec2017_D10.csv: magnitude vocabulary | PASS | violations=0 |
| cec2017\effect_sizes_cec2017_D10.csv: apgsk disclosed-unavailable | PASS | 29 apgsk rows, n/a cells kept |
| cec2017\bca_ci_cec2017_D10.csv: columns | PASS | 11 columns exact |
| cec2017\bca_ci_cec2017_D10.csv: float format %.6e (n/a allowed) | PASS | violations=0 |
| cec2017\bca_ci_cec2017_D10.csv: integer columns plain ints | PASS | violations=0 |
| cec2017\bca_ci_cec2017_D10.csv: suite column constant | PASS | values=['cec2017'] |
| cec2017\bca_ci_cec2017_D10.csv: dimension column constant | PASS | values=['10'] |
| cec2017\bca_ci_cec2017_D10.csv: sort order | PASS | function asc, comparator P1 |
| cec2017\bca_ci_cec2017_D10.csv: B=10000 on ok rows | PASS | violations=0 |
| cec2017\bca_ci_cec2017_D10.csv: ci_low<=ci_high on ok rows | PASS | violations=0 |
| cec2017\bca_ci_cec2017_D10.csv: seed_scheme literal | PASS | violations=0 |
| cec2017\bca_ci_cec2017_D10.csv: availability vocabulary | PASS | values=['disclosed-unavailable', 'no CI (degenerate cell)', 'ok'] |
| cec2017\bca_ci_cec2017_D10.csv: apgsk disclosed-unavailable | PASS | 29 apgsk rows |
| cec2017\convergence_checkpoints_cec2017_D10.csv: columns | PASS | 8 columns exact |
| cec2017\convergence_checkpoints_cec2017_D10.csv: float format %.6e (n/a allowed) | PASS | violations=0 |
| cec2017\convergence_checkpoints_cec2017_D10.csv: integer columns plain ints | PASS | violations=0 |
| cec2017\convergence_checkpoints_cec2017_D10.csv: suite column constant | PASS | values=['cec2017'] |
| cec2017\convergence_checkpoints_cec2017_D10.csv: dimension column constant | PASS | values=['10'] |
| cec2017\convergence_checkpoints_cec2017_D10.csv: sort order | PASS | function asc, algorithm P1, checkpoint_nfes asc |
| cec2017\convergence_checkpoints_cec2017_D10.csv: availability vocabulary | PASS | values=['ok'] |
| cec2017\descriptive_stats_cec2017_D30.csv: columns | PASS | 10 columns exact |
| cec2017\descriptive_stats_cec2017_D30.csv: float format %.6e (n/a allowed) | PASS | violations=0 |
| cec2017\descriptive_stats_cec2017_D30.csv: integer columns plain ints | PASS | violations=0 |
| cec2017\descriptive_stats_cec2017_D30.csv: suite column constant | PASS | values=['cec2017'] |
| cec2017\descriptive_stats_cec2017_D30.csv: dimension column constant | PASS | values=['30'] |
| cec2017\descriptive_stats_cec2017_D30.csv: sort order | PASS | function asc, algorithm P1 |
| cec2017\descriptive_stats_cec2017_D30.csv: source_path release-relative and resolvable | PASS | violations=0 (paths resolve under benchmarks/cec_reference_results/) |
| cec2017\friedman_ranks_cec2017_D30.csv: columns | PASS | 8 columns exact |
| cec2017\friedman_ranks_cec2017_D30.csv: float format %.6e (n/a allowed) | PASS | violations=0 |
| cec2017\friedman_ranks_cec2017_D30.csv: integer columns plain ints | PASS | violations=0 |
| cec2017\friedman_ranks_cec2017_D30.csv: suite column constant | PASS | values=['cec2017'] |
| cec2017\friedman_ranks_cec2017_D30.csv: dimension column constant | PASS | values=['30'] |
| cec2017\friedman_ranks_cec2017_D30.csv: 7 rows P1 order | PASS | algs=['gsk', 'agsk', 'apgsk', 'fdb-agsk', 'atmals-gsk', 'egsk', 'dt-gsk'] |
| cec2017\friedman_ranks_cec2017_D30.csv: mean_rank in [1,7] | PASS | range [2.2931,5.4138] |
| cec2017\friedman_ranks_cec2017_D30.csv: sum(mean_rank)=k(k+1)/2=28 (within %.6e storage rounding) | PASS | sum=27.999999 |
| cec2017\friedman_ranks_cec2017_D30.csv: p_value in [0,1], repeated per row | PASS | p=1.151976e-10 |
| cec2017\friedman_ranks_cec2017_D30.csv: dimension=30 | PASS | dimension values=['30'] |
| cec2017\nemenyi_cd_cec2017_D30.csv: columns | PASS | 8 columns exact |
| cec2017\nemenyi_cd_cec2017_D30.csv: float format %.6e (n/a allowed) | PASS | violations=0 |
| cec2017\nemenyi_cd_cec2017_D30.csv: integer columns plain ints | PASS | violations=0 |
| cec2017\nemenyi_cd_cec2017_D30.csv: suite column constant | PASS | values=['cec2017'] |
| cec2017\nemenyi_cd_cec2017_D30.csv: dimension column constant | PASS | values=['30'] |
| cec2017\nemenyi_cd_cec2017_D30.csv: 7 rows P1 order | PASS | algs=['gsk', 'agsk', 'apgsk', 'fdb-agsk', 'atmals-gsk', 'egsk', 'dt-gsk'] |
| cec2017\nemenyi_cd_cec2017_D30.csv: k=7 | PASS | k column |
| cec2017\nemenyi_cd_cec2017_D30.csv: mean_rank in [1,7] | PASS | range [2.2931,5.4138] |
| cec2017\nemenyi_cd_cec2017_D30.csv: conditional emission (omnibus p<0.05) | PASS | Iman-Davenport p=1.151976e-10 |
| cec2017\nemenyi_cd_cec2017_D30.csv: mean_rank matches friedman file | PASS | cross-file consistency |
| cec2017\wilcoxon_holm_cec2017_D30.csv: columns | PASS | 11 columns exact |
| cec2017\wilcoxon_holm_cec2017_D30.csv: float format %.6e (n/a allowed) | PASS | violations=0 |
| cec2017\wilcoxon_holm_cec2017_D30.csv: integer columns plain ints | PASS | violations=0 |
| cec2017\wilcoxon_holm_cec2017_D30.csv: suite column constant | PASS | values=['cec2017'] |
| cec2017\wilcoxon_holm_cec2017_D30.csv: dimension column constant | PASS | values=['30'] |
| cec2017\wilcoxon_holm_cec2017_D30.csv: test_level | PASS | values=['across_functions_funclevel'] |
| cec2017\wilcoxon_holm_cec2017_D30.csv: 6 comparator rows, function=0 | PASS | 6 rows |
| cec2017\wilcoxon_holm_cec2017_D30.csv: comparator P1 order | PASS | ['gsk', 'agsk', 'apgsk', 'fdb-agsk', 'atmals-gsk', 'egsk'] |
| cec2017\wilcoxon_holm_cec2017_D30.csv: p_raw in (0,1], never 0 | PASS | violations=0; 0 rows carry unrounded p<1e-4 (floor is render-time only) |
| cec2017\wilcoxon_holm_cec2017_D30.csv: p_holm >= p_raw | PASS | violations=0 |
| cec2017\wilcoxon_holm_cec2017_D30.csv: outcome vocabulary | PASS | values=['tie', 'win'] |
| cec2017\wilcoxon_holm_cec2017_D30.csv: availability vocabulary | PASS | values=['ok'] |
| cec2017\wilcoxon_run_cec2017_D30.csv: columns | PASS | 11 columns exact |
| cec2017\wilcoxon_run_cec2017_D30.csv: float format %.6e (n/a allowed) | PASS | violations=0 |
| cec2017\wilcoxon_run_cec2017_D30.csv: integer columns plain ints | PASS | violations=0 |
| cec2017\wilcoxon_run_cec2017_D30.csv: suite column constant | PASS | values=['cec2017'] |
| cec2017\wilcoxon_run_cec2017_D30.csv: dimension column constant | PASS | values=['30'] |
| cec2017\wilcoxon_run_cec2017_D30.csv: test_level | PASS | values=['per_function_runlevel'] |
| cec2017\wilcoxon_run_cec2017_D30.csv: sort order | PASS | function asc, comparator P1 |
| cec2017\wilcoxon_run_cec2017_D30.csv: p_raw in (0,1], never 0 | PASS | violations=0; 81 rows carry unrounded p<1e-4 (floor is render-time only) |
| cec2017\wilcoxon_run_cec2017_D30.csv: p_holm >= p_raw | PASS | violations=0 |
| cec2017\wilcoxon_run_cec2017_D30.csv: outcome vocabulary | PASS | values=['loss', 'n/a', 'tie', 'win'] |
| cec2017\wilcoxon_run_cec2017_D30.csv: availability vocabulary | PASS | values=['disclosed-unavailable', 'ok'] |
| cec2017\wilcoxon_run_cec2017_D30.csv: apgsk rows disclosed-unavailable (A2-004) | PASS | 29 apgsk rows present, all n/a cells with status column |
| cec2017\wilcoxon_run_cec2017_D30_exploratory_bh.csv: columns | PASS | 11 columns exact |
| cec2017\wilcoxon_run_cec2017_D30_exploratory_bh.csv: float format %.6e (n/a allowed) | PASS | violations=0 |
| cec2017\wilcoxon_run_cec2017_D30_exploratory_bh.csv: integer columns plain ints | PASS | violations=0 |
| cec2017\wilcoxon_run_cec2017_D30_exploratory_bh.csv: suite column constant | PASS | values=['cec2017'] |
| cec2017\wilcoxon_run_cec2017_D30_exploratory_bh.csv: dimension column constant | PASS | values=['30'] |
| cec2017\wilcoxon_run_cec2017_D30_exploratory_bh.csv: test_level | PASS | values=['per_function_runlevel'] |
| cec2017\wilcoxon_run_cec2017_D30_exploratory_bh.csv: sort order | PASS | function asc, comparator P1 |
| cec2017\wilcoxon_run_cec2017_D30_exploratory_bh.csv: p_raw in (0,1], never 0 | PASS | violations=0; 81 rows carry unrounded p<1e-4 (floor is render-time only) |
| cec2017\wilcoxon_run_cec2017_D30_exploratory_bh.csv: p_bh >= p_raw | PASS | violations=0 |
| cec2017\wilcoxon_run_cec2017_D30_exploratory_bh.csv: outcome vocabulary | PASS | values=['loss', 'n/a', 'tie', 'win'] |
| cec2017\wilcoxon_run_cec2017_D30_exploratory_bh.csv: availability vocabulary | PASS | values=['disclosed-unavailable', 'ok'] |
| cec2017\wilcoxon_run_cec2017_D30_exploratory_bh.csv: apgsk rows disclosed-unavailable (A2-004) | PASS | 29 apgsk rows present, all n/a cells with status column |
| cec2017\effect_sizes_cec2017_D30.csv: columns | PASS | 9 columns exact |
| cec2017\effect_sizes_cec2017_D30.csv: float format %.6e (n/a allowed) | PASS | violations=0 |
| cec2017\effect_sizes_cec2017_D30.csv: integer columns plain ints | PASS | violations=0 |
| cec2017\effect_sizes_cec2017_D30.csv: suite column constant | PASS | values=['cec2017'] |
| cec2017\effect_sizes_cec2017_D30.csv: dimension column constant | PASS | values=['30'] |
| cec2017\effect_sizes_cec2017_D30.csv: sort order | PASS | function asc, comparator P1 |
| cec2017\effect_sizes_cec2017_D30.csv: a12 in [0,1] | PASS | violations=0 |
| cec2017\effect_sizes_cec2017_D30.csv: cliffs_delta=2*a12-1 in [-1,1] | PASS | violations=0 |
| cec2017\effect_sizes_cec2017_D30.csv: magnitude vocabulary | PASS | violations=0 |
| cec2017\effect_sizes_cec2017_D30.csv: apgsk disclosed-unavailable | PASS | 29 apgsk rows, n/a cells kept |
| cec2017\bca_ci_cec2017_D30.csv: columns | PASS | 11 columns exact |
| cec2017\bca_ci_cec2017_D30.csv: float format %.6e (n/a allowed) | PASS | violations=0 |
| cec2017\bca_ci_cec2017_D30.csv: integer columns plain ints | PASS | violations=0 |
| cec2017\bca_ci_cec2017_D30.csv: suite column constant | PASS | values=['cec2017'] |
| cec2017\bca_ci_cec2017_D30.csv: dimension column constant | PASS | values=['30'] |
| cec2017\bca_ci_cec2017_D30.csv: sort order | PASS | function asc, comparator P1 |
| cec2017\bca_ci_cec2017_D30.csv: B=10000 on ok rows | PASS | violations=0 |
| cec2017\bca_ci_cec2017_D30.csv: ci_low<=ci_high on ok rows | PASS | violations=0 |
| cec2017\bca_ci_cec2017_D30.csv: seed_scheme literal | PASS | violations=0 |
| cec2017\bca_ci_cec2017_D30.csv: availability vocabulary | PASS | values=['disclosed-unavailable', 'no CI (degenerate cell)', 'ok'] |
| cec2017\bca_ci_cec2017_D30.csv: apgsk disclosed-unavailable | PASS | 29 apgsk rows |
| cec2017\convergence_checkpoints_cec2017_D30.csv: columns | PASS | 8 columns exact |
| cec2017\convergence_checkpoints_cec2017_D30.csv: float format %.6e (n/a allowed) | PASS | violations=0 |
| cec2017\convergence_checkpoints_cec2017_D30.csv: integer columns plain ints | PASS | violations=0 |
| cec2017\convergence_checkpoints_cec2017_D30.csv: suite column constant | PASS | values=['cec2017'] |
| cec2017\convergence_checkpoints_cec2017_D30.csv: dimension column constant | PASS | values=['30'] |
| cec2017\convergence_checkpoints_cec2017_D30.csv: sort order | PASS | function asc, algorithm P1, checkpoint_nfes asc |
| cec2017\convergence_checkpoints_cec2017_D30.csv: availability vocabulary | PASS | values=['ok'] |
| cec2017\descriptive_stats_cec2017_D50.csv: columns | PASS | 10 columns exact |
| cec2017\descriptive_stats_cec2017_D50.csv: float format %.6e (n/a allowed) | PASS | violations=0 |
| cec2017\descriptive_stats_cec2017_D50.csv: integer columns plain ints | PASS | violations=0 |
| cec2017\descriptive_stats_cec2017_D50.csv: suite column constant | PASS | values=['cec2017'] |
| cec2017\descriptive_stats_cec2017_D50.csv: dimension column constant | PASS | values=['50'] |
| cec2017\descriptive_stats_cec2017_D50.csv: sort order | PASS | function asc, algorithm P1 |
| cec2017\descriptive_stats_cec2017_D50.csv: source_path release-relative and resolvable | PASS | violations=0 (paths resolve under benchmarks/cec_reference_results/) |
| cec2017\friedman_ranks_cec2017_D50.csv: columns | PASS | 8 columns exact |
| cec2017\friedman_ranks_cec2017_D50.csv: float format %.6e (n/a allowed) | PASS | violations=0 |
| cec2017\friedman_ranks_cec2017_D50.csv: integer columns plain ints | PASS | violations=0 |
| cec2017\friedman_ranks_cec2017_D50.csv: suite column constant | PASS | values=['cec2017'] |
| cec2017\friedman_ranks_cec2017_D50.csv: dimension column constant | PASS | values=['50'] |
| cec2017\friedman_ranks_cec2017_D50.csv: 7 rows P1 order | PASS | algs=['gsk', 'agsk', 'apgsk', 'fdb-agsk', 'atmals-gsk', 'egsk', 'dt-gsk'] |
| cec2017\friedman_ranks_cec2017_D50.csv: mean_rank in [1,7] | PASS | range [2.2069,5.3448] |
| cec2017\friedman_ranks_cec2017_D50.csv: sum(mean_rank)=k(k+1)/2=28 (within %.6e storage rounding) | PASS | sum=28.000001 |
| cec2017\friedman_ranks_cec2017_D50.csv: p_value in [0,1], repeated per row | PASS | p=6.763147e-11 |
| cec2017\friedman_ranks_cec2017_D50.csv: dimension=50 | PASS | dimension values=['50'] |
| cec2017\nemenyi_cd_cec2017_D50.csv: columns | PASS | 8 columns exact |
| cec2017\nemenyi_cd_cec2017_D50.csv: float format %.6e (n/a allowed) | PASS | violations=0 |
| cec2017\nemenyi_cd_cec2017_D50.csv: integer columns plain ints | PASS | violations=0 |
| cec2017\nemenyi_cd_cec2017_D50.csv: suite column constant | PASS | values=['cec2017'] |
| cec2017\nemenyi_cd_cec2017_D50.csv: dimension column constant | PASS | values=['50'] |
| cec2017\nemenyi_cd_cec2017_D50.csv: 7 rows P1 order | PASS | algs=['gsk', 'agsk', 'apgsk', 'fdb-agsk', 'atmals-gsk', 'egsk', 'dt-gsk'] |
| cec2017\nemenyi_cd_cec2017_D50.csv: k=7 | PASS | k column |
| cec2017\nemenyi_cd_cec2017_D50.csv: mean_rank in [1,7] | PASS | range [2.2069,5.3448] |
| cec2017\nemenyi_cd_cec2017_D50.csv: conditional emission (omnibus p<0.05) | PASS | Iman-Davenport p=6.763147e-11 |
| cec2017\nemenyi_cd_cec2017_D50.csv: mean_rank matches friedman file | PASS | cross-file consistency |
| cec2017\wilcoxon_holm_cec2017_D50.csv: columns | PASS | 11 columns exact |
| cec2017\wilcoxon_holm_cec2017_D50.csv: float format %.6e (n/a allowed) | PASS | violations=0 |
| cec2017\wilcoxon_holm_cec2017_D50.csv: integer columns plain ints | PASS | violations=0 |
| cec2017\wilcoxon_holm_cec2017_D50.csv: suite column constant | PASS | values=['cec2017'] |
| cec2017\wilcoxon_holm_cec2017_D50.csv: dimension column constant | PASS | values=['50'] |
| cec2017\wilcoxon_holm_cec2017_D50.csv: test_level | PASS | values=['across_functions_funclevel'] |
| cec2017\wilcoxon_holm_cec2017_D50.csv: 6 comparator rows, function=0 | PASS | 6 rows |
| cec2017\wilcoxon_holm_cec2017_D50.csv: comparator P1 order | PASS | ['gsk', 'agsk', 'apgsk', 'fdb-agsk', 'atmals-gsk', 'egsk'] |
| cec2017\wilcoxon_holm_cec2017_D50.csv: p_raw in (0,1], never 0 | PASS | violations=0; 1 rows carry unrounded p<1e-4 (floor is render-time only) |
| cec2017\wilcoxon_holm_cec2017_D50.csv: p_holm >= p_raw | PASS | violations=0 |
| cec2017\wilcoxon_holm_cec2017_D50.csv: outcome vocabulary | PASS | values=['tie', 'win'] |
| cec2017\wilcoxon_holm_cec2017_D50.csv: availability vocabulary | PASS | values=['ok'] |
| cec2017\wilcoxon_run_cec2017_D50.csv: columns | PASS | 11 columns exact |
| cec2017\wilcoxon_run_cec2017_D50.csv: float format %.6e (n/a allowed) | PASS | violations=0 |
| cec2017\wilcoxon_run_cec2017_D50.csv: integer columns plain ints | PASS | violations=0 |
| cec2017\wilcoxon_run_cec2017_D50.csv: suite column constant | PASS | values=['cec2017'] |
| cec2017\wilcoxon_run_cec2017_D50.csv: dimension column constant | PASS | values=['50'] |
| cec2017\wilcoxon_run_cec2017_D50.csv: test_level | PASS | values=['per_function_runlevel'] |
| cec2017\wilcoxon_run_cec2017_D50.csv: sort order | PASS | function asc, comparator P1 |
| cec2017\wilcoxon_run_cec2017_D50.csv: p_raw in (0,1], never 0 | PASS | violations=0; 103 rows carry unrounded p<1e-4 (floor is render-time only) |
| cec2017\wilcoxon_run_cec2017_D50.csv: p_holm >= p_raw | PASS | violations=0 |
| cec2017\wilcoxon_run_cec2017_D50.csv: outcome vocabulary | PASS | values=['loss', 'n/a', 'tie', 'win'] |
| cec2017\wilcoxon_run_cec2017_D50.csv: availability vocabulary | PASS | values=['disclosed-unavailable', 'ok'] |
| cec2017\wilcoxon_run_cec2017_D50.csv: apgsk rows disclosed-unavailable (A2-004) | PASS | 29 apgsk rows present, all n/a cells with status column |
| cec2017\wilcoxon_run_cec2017_D50_exploratory_bh.csv: columns | PASS | 11 columns exact |
| cec2017\wilcoxon_run_cec2017_D50_exploratory_bh.csv: float format %.6e (n/a allowed) | PASS | violations=0 |
| cec2017\wilcoxon_run_cec2017_D50_exploratory_bh.csv: integer columns plain ints | PASS | violations=0 |
| cec2017\wilcoxon_run_cec2017_D50_exploratory_bh.csv: suite column constant | PASS | values=['cec2017'] |
| cec2017\wilcoxon_run_cec2017_D50_exploratory_bh.csv: dimension column constant | PASS | values=['50'] |
| cec2017\wilcoxon_run_cec2017_D50_exploratory_bh.csv: test_level | PASS | values=['per_function_runlevel'] |
| cec2017\wilcoxon_run_cec2017_D50_exploratory_bh.csv: sort order | PASS | function asc, comparator P1 |
| cec2017\wilcoxon_run_cec2017_D50_exploratory_bh.csv: p_raw in (0,1], never 0 | PASS | violations=0; 103 rows carry unrounded p<1e-4 (floor is render-time only) |
| cec2017\wilcoxon_run_cec2017_D50_exploratory_bh.csv: p_bh >= p_raw | PASS | violations=0 |
| cec2017\wilcoxon_run_cec2017_D50_exploratory_bh.csv: outcome vocabulary | PASS | values=['loss', 'n/a', 'tie', 'win'] |
| cec2017\wilcoxon_run_cec2017_D50_exploratory_bh.csv: availability vocabulary | PASS | values=['disclosed-unavailable', 'ok'] |
| cec2017\wilcoxon_run_cec2017_D50_exploratory_bh.csv: apgsk rows disclosed-unavailable (A2-004) | PASS | 29 apgsk rows present, all n/a cells with status column |
| cec2017\effect_sizes_cec2017_D50.csv: columns | PASS | 9 columns exact |
| cec2017\effect_sizes_cec2017_D50.csv: float format %.6e (n/a allowed) | PASS | violations=0 |
| cec2017\effect_sizes_cec2017_D50.csv: integer columns plain ints | PASS | violations=0 |
| cec2017\effect_sizes_cec2017_D50.csv: suite column constant | PASS | values=['cec2017'] |
| cec2017\effect_sizes_cec2017_D50.csv: dimension column constant | PASS | values=['50'] |
| cec2017\effect_sizes_cec2017_D50.csv: sort order | PASS | function asc, comparator P1 |
| cec2017\effect_sizes_cec2017_D50.csv: a12 in [0,1] | PASS | violations=0 |
| cec2017\effect_sizes_cec2017_D50.csv: cliffs_delta=2*a12-1 in [-1,1] | PASS | violations=0 |
| cec2017\effect_sizes_cec2017_D50.csv: magnitude vocabulary | PASS | violations=0 |
| cec2017\effect_sizes_cec2017_D50.csv: apgsk disclosed-unavailable | PASS | 29 apgsk rows, n/a cells kept |
| cec2017\bca_ci_cec2017_D50.csv: columns | PASS | 11 columns exact |
| cec2017\bca_ci_cec2017_D50.csv: float format %.6e (n/a allowed) | PASS | violations=0 |
| cec2017\bca_ci_cec2017_D50.csv: integer columns plain ints | PASS | violations=0 |
| cec2017\bca_ci_cec2017_D50.csv: suite column constant | PASS | values=['cec2017'] |
| cec2017\bca_ci_cec2017_D50.csv: dimension column constant | PASS | values=['50'] |
| cec2017\bca_ci_cec2017_D50.csv: sort order | PASS | function asc, comparator P1 |
| cec2017\bca_ci_cec2017_D50.csv: B=10000 on ok rows | PASS | violations=0 |
| cec2017\bca_ci_cec2017_D50.csv: ci_low<=ci_high on ok rows | PASS | violations=0 |
| cec2017\bca_ci_cec2017_D50.csv: seed_scheme literal | PASS | violations=0 |
| cec2017\bca_ci_cec2017_D50.csv: availability vocabulary | PASS | values=['disclosed-unavailable', 'ok'] |
| cec2017\bca_ci_cec2017_D50.csv: apgsk disclosed-unavailable | PASS | 29 apgsk rows |
| cec2017\convergence_checkpoints_cec2017_D50.csv: columns | PASS | 8 columns exact |
| cec2017\convergence_checkpoints_cec2017_D50.csv: float format %.6e (n/a allowed) | PASS | violations=0 |
| cec2017\convergence_checkpoints_cec2017_D50.csv: integer columns plain ints | PASS | violations=0 |
| cec2017\convergence_checkpoints_cec2017_D50.csv: suite column constant | PASS | values=['cec2017'] |
| cec2017\convergence_checkpoints_cec2017_D50.csv: dimension column constant | PASS | values=['50'] |
| cec2017\convergence_checkpoints_cec2017_D50.csv: sort order | PASS | function asc, algorithm P1, checkpoint_nfes asc |
| cec2017\convergence_checkpoints_cec2017_D50.csv: availability vocabulary | PASS | values=['ok'] |
| cec2017\descriptive_stats_cec2017_D100.csv: columns | PASS | 10 columns exact |
| cec2017\descriptive_stats_cec2017_D100.csv: float format %.6e (n/a allowed) | PASS | violations=0 |
| cec2017\descriptive_stats_cec2017_D100.csv: integer columns plain ints | PASS | violations=0 |
| cec2017\descriptive_stats_cec2017_D100.csv: suite column constant | PASS | values=['cec2017'] |
| cec2017\descriptive_stats_cec2017_D100.csv: dimension column constant | PASS | values=['100'] |
| cec2017\descriptive_stats_cec2017_D100.csv: sort order | PASS | function asc, algorithm P1 |
| cec2017\descriptive_stats_cec2017_D100.csv: source_path release-relative and resolvable | PASS | violations=0 (paths resolve under benchmarks/cec_reference_results/) |
| cec2017\friedman_ranks_cec2017_D100.csv: columns | PASS | 8 columns exact |
| cec2017\friedman_ranks_cec2017_D100.csv: float format %.6e (n/a allowed) | PASS | violations=0 |
| cec2017\friedman_ranks_cec2017_D100.csv: integer columns plain ints | PASS | violations=0 |
| cec2017\friedman_ranks_cec2017_D100.csv: suite column constant | PASS | values=['cec2017'] |
| cec2017\friedman_ranks_cec2017_D100.csv: dimension column constant | PASS | values=['100'] |
| cec2017\friedman_ranks_cec2017_D100.csv: 7 rows P1 order | PASS | algs=['gsk', 'agsk', 'apgsk', 'fdb-agsk', 'atmals-gsk', 'egsk', 'dt-gsk'] |
| cec2017\friedman_ranks_cec2017_D100.csv: mean_rank in [1,7] | PASS | range [2.3448,5.8966] |
| cec2017\friedman_ranks_cec2017_D100.csv: sum(mean_rank)=k(k+1)/2=28 (within %.6e storage rounding) | PASS | sum=28.000000 |
| cec2017\friedman_ranks_cec2017_D100.csv: p_value in [0,1], repeated per row | PASS | p=1.424078e-12 |
| cec2017\friedman_ranks_cec2017_D100.csv: dimension=100 | PASS | dimension values=['100'] |
| cec2017\nemenyi_cd_cec2017_D100.csv: columns | PASS | 8 columns exact |
| cec2017\nemenyi_cd_cec2017_D100.csv: float format %.6e (n/a allowed) | PASS | violations=0 |
| cec2017\nemenyi_cd_cec2017_D100.csv: integer columns plain ints | PASS | violations=0 |
| cec2017\nemenyi_cd_cec2017_D100.csv: suite column constant | PASS | values=['cec2017'] |
| cec2017\nemenyi_cd_cec2017_D100.csv: dimension column constant | PASS | values=['100'] |
| cec2017\nemenyi_cd_cec2017_D100.csv: 7 rows P1 order | PASS | algs=['gsk', 'agsk', 'apgsk', 'fdb-agsk', 'atmals-gsk', 'egsk', 'dt-gsk'] |
| cec2017\nemenyi_cd_cec2017_D100.csv: k=7 | PASS | k column |
| cec2017\nemenyi_cd_cec2017_D100.csv: mean_rank in [1,7] | PASS | range [2.3448,5.8966] |
| cec2017\nemenyi_cd_cec2017_D100.csv: conditional emission (omnibus p<0.05) | PASS | Iman-Davenport p=1.424078e-12 |
| cec2017\nemenyi_cd_cec2017_D100.csv: mean_rank matches friedman file | PASS | cross-file consistency |
| cec2017\wilcoxon_holm_cec2017_D100.csv: columns | PASS | 11 columns exact |
| cec2017\wilcoxon_holm_cec2017_D100.csv: float format %.6e (n/a allowed) | PASS | violations=0 |
| cec2017\wilcoxon_holm_cec2017_D100.csv: integer columns plain ints | PASS | violations=0 |
| cec2017\wilcoxon_holm_cec2017_D100.csv: suite column constant | PASS | values=['cec2017'] |
| cec2017\wilcoxon_holm_cec2017_D100.csv: dimension column constant | PASS | values=['100'] |
| cec2017\wilcoxon_holm_cec2017_D100.csv: test_level | PASS | values=['across_functions_funclevel'] |
| cec2017\wilcoxon_holm_cec2017_D100.csv: 6 comparator rows, function=0 | PASS | 6 rows |
| cec2017\wilcoxon_holm_cec2017_D100.csv: comparator P1 order | PASS | ['gsk', 'agsk', 'apgsk', 'fdb-agsk', 'atmals-gsk', 'egsk'] |
| cec2017\wilcoxon_holm_cec2017_D100.csv: p_raw in (0,1], never 0 | PASS | violations=0; 3 rows carry unrounded p<1e-4 (floor is render-time only) |
| cec2017\wilcoxon_holm_cec2017_D100.csv: p_holm >= p_raw | PASS | violations=0 |
| cec2017\wilcoxon_holm_cec2017_D100.csv: outcome vocabulary | PASS | values=['tie', 'win'] |
| cec2017\wilcoxon_holm_cec2017_D100.csv: availability vocabulary | PASS | values=['ok'] |
| cec2017\wilcoxon_run_cec2017_D100.csv: columns | PASS | 11 columns exact |
| cec2017\wilcoxon_run_cec2017_D100.csv: float format %.6e (n/a allowed) | PASS | violations=0 |
| cec2017\wilcoxon_run_cec2017_D100.csv: integer columns plain ints | PASS | violations=0 |
| cec2017\wilcoxon_run_cec2017_D100.csv: suite column constant | PASS | values=['cec2017'] |
| cec2017\wilcoxon_run_cec2017_D100.csv: dimension column constant | PASS | values=['100'] |
| cec2017\wilcoxon_run_cec2017_D100.csv: test_level | PASS | values=['per_function_runlevel'] |
| cec2017\wilcoxon_run_cec2017_D100.csv: sort order | PASS | function asc, comparator P1 |
| cec2017\wilcoxon_run_cec2017_D100.csv: p_raw in (0,1], never 0 | PASS | violations=0; 126 rows carry unrounded p<1e-4 (floor is render-time only) |
| cec2017\wilcoxon_run_cec2017_D100.csv: p_holm >= p_raw | PASS | violations=0 |
| cec2017\wilcoxon_run_cec2017_D100.csv: outcome vocabulary | PASS | values=['loss', 'tie', 'win'] |
| cec2017\wilcoxon_run_cec2017_D100.csv: availability vocabulary | PASS | values=['ok'] |
| cec2017\wilcoxon_run_cec2017_D100_exploratory_bh.csv: columns | PASS | 11 columns exact |
| cec2017\wilcoxon_run_cec2017_D100_exploratory_bh.csv: float format %.6e (n/a allowed) | PASS | violations=0 |
| cec2017\wilcoxon_run_cec2017_D100_exploratory_bh.csv: integer columns plain ints | PASS | violations=0 |
| cec2017\wilcoxon_run_cec2017_D100_exploratory_bh.csv: suite column constant | PASS | values=['cec2017'] |
| cec2017\wilcoxon_run_cec2017_D100_exploratory_bh.csv: dimension column constant | PASS | values=['100'] |
| cec2017\wilcoxon_run_cec2017_D100_exploratory_bh.csv: test_level | PASS | values=['per_function_runlevel'] |
| cec2017\wilcoxon_run_cec2017_D100_exploratory_bh.csv: sort order | PASS | function asc, comparator P1 |
| cec2017\wilcoxon_run_cec2017_D100_exploratory_bh.csv: p_raw in (0,1], never 0 | PASS | violations=0; 126 rows carry unrounded p<1e-4 (floor is render-time only) |
| cec2017\wilcoxon_run_cec2017_D100_exploratory_bh.csv: p_bh >= p_raw | PASS | violations=0 |
| cec2017\wilcoxon_run_cec2017_D100_exploratory_bh.csv: outcome vocabulary | PASS | values=['loss', 'tie', 'win'] |
| cec2017\wilcoxon_run_cec2017_D100_exploratory_bh.csv: availability vocabulary | PASS | values=['ok'] |
| cec2017\effect_sizes_cec2017_D100.csv: columns | PASS | 9 columns exact |
| cec2017\effect_sizes_cec2017_D100.csv: float format %.6e (n/a allowed) | PASS | violations=0 |
| cec2017\effect_sizes_cec2017_D100.csv: integer columns plain ints | PASS | violations=0 |
| cec2017\effect_sizes_cec2017_D100.csv: suite column constant | PASS | values=['cec2017'] |
| cec2017\effect_sizes_cec2017_D100.csv: dimension column constant | PASS | values=['100'] |
| cec2017\effect_sizes_cec2017_D100.csv: sort order | PASS | function asc, comparator P1 |
| cec2017\effect_sizes_cec2017_D100.csv: a12 in [0,1] | PASS | violations=0 |
| cec2017\effect_sizes_cec2017_D100.csv: cliffs_delta=2*a12-1 in [-1,1] | PASS | violations=0 |
| cec2017\effect_sizes_cec2017_D100.csv: magnitude vocabulary | PASS | violations=0 |
| cec2017\bca_ci_cec2017_D100.csv: columns | PASS | 11 columns exact |
| cec2017\bca_ci_cec2017_D100.csv: float format %.6e (n/a allowed) | PASS | violations=0 |
| cec2017\bca_ci_cec2017_D100.csv: integer columns plain ints | PASS | violations=0 |
| cec2017\bca_ci_cec2017_D100.csv: suite column constant | PASS | values=['cec2017'] |
| cec2017\bca_ci_cec2017_D100.csv: dimension column constant | PASS | values=['100'] |
| cec2017\bca_ci_cec2017_D100.csv: sort order | PASS | function asc, comparator P1 |
| cec2017\bca_ci_cec2017_D100.csv: B=10000 on ok rows | PASS | violations=0 |
| cec2017\bca_ci_cec2017_D100.csv: ci_low<=ci_high on ok rows | PASS | violations=0 |
| cec2017\bca_ci_cec2017_D100.csv: seed_scheme literal | PASS | violations=0 |
| cec2017\bca_ci_cec2017_D100.csv: availability vocabulary | PASS | values=['ok'] |
| cec2017\convergence_checkpoints_cec2017_D100.csv: columns | PASS | 8 columns exact |
| cec2017\convergence_checkpoints_cec2017_D100.csv: float format %.6e (n/a allowed) | PASS | violations=0 |
| cec2017\convergence_checkpoints_cec2017_D100.csv: integer columns plain ints | PASS | violations=0 |
| cec2017\convergence_checkpoints_cec2017_D100.csv: suite column constant | PASS | values=['cec2017'] |
| cec2017\convergence_checkpoints_cec2017_D100.csv: dimension column constant | PASS | values=['100'] |
| cec2017\convergence_checkpoints_cec2017_D100.csv: sort order | PASS | function asc, algorithm P1, checkpoint_nfes asc |
| cec2017\convergence_checkpoints_cec2017_D100.csv: availability vocabulary | PASS | values=['ok'] |
| cec2017\friedman_ranks_cec2017_overall.csv: columns | PASS | 3 columns exact |
| cec2017\friedman_ranks_cec2017_overall.csv: float format %.6e (n/a allowed) | PASS | violations=0 |
| cec2017\friedman_ranks_cec2017_overall.csv: suite column constant | PASS | values=['cec2017'] |
| cec2017\friedman_ranks_cec2017_overall.csv: 7 rows P1 order | PASS | algs=['gsk', 'agsk', 'apgsk', 'fdb-agsk', 'atmals-gsk', 'egsk', 'dt-gsk'] |
| cec2017\friedman_ranks_cec2017_overall.csv: mean_rank in [1,7] | PASS | range [2.4828,5.0560] |
| cec2017\friedman_ranks_cec2017_overall.csv: no pooled test columns | PASS | 3-column descriptive form, no chi2/F/p |
| cec2013\descriptive_stats_cec2013_D10.csv: columns | PASS | 10 columns exact |
| cec2013\descriptive_stats_cec2013_D10.csv: float format %.6e (n/a allowed) | PASS | violations=0 |
| cec2013\descriptive_stats_cec2013_D10.csv: integer columns plain ints | PASS | violations=0 |
| cec2013\descriptive_stats_cec2013_D10.csv: suite column constant | PASS | values=['cec2013'] |
| cec2013\descriptive_stats_cec2013_D10.csv: dimension column constant | PASS | values=['10'] |
| cec2013\descriptive_stats_cec2013_D10.csv: sort order | PASS | function asc, algorithm P1 |
| cec2013\descriptive_stats_cec2013_D10.csv: source_path release-relative and resolvable | PASS | violations=0 (paths resolve under benchmarks/cec_reference_results/) |
| cec2013\friedman_ranks_cec2013_D10.csv: columns | PASS | 8 columns exact |
| cec2013\friedman_ranks_cec2013_D10.csv: float format %.6e (n/a allowed) | PASS | violations=0 |
| cec2013\friedman_ranks_cec2013_D10.csv: integer columns plain ints | PASS | violations=0 |
| cec2013\friedman_ranks_cec2013_D10.csv: suite column constant | PASS | values=['cec2013'] |
| cec2013\friedman_ranks_cec2013_D10.csv: dimension column constant | PASS | values=['10'] |
| cec2013\friedman_ranks_cec2013_D10.csv: 7 rows P1 order | PASS | algs=['gsk', 'agsk', 'apgsk', 'fdb-agsk', 'atmals-gsk', 'egsk', 'dt-gsk'] |
| cec2013\friedman_ranks_cec2013_D10.csv: mean_rank in [1,7] | PASS | range [2.4107,5.8750] |
| cec2013\friedman_ranks_cec2013_D10.csv: sum(mean_rank)=k(k+1)/2=28 (within %.6e storage rounding) | PASS | sum=28.000000 |
| cec2013\friedman_ranks_cec2013_D10.csv: p_value in [0,1], repeated per row | PASS | p=3.264004e-07 |
| cec2013\friedman_ranks_cec2013_D10.csv: dimension=10 | PASS | dimension values=['10'] |
| cec2013\nemenyi_cd_cec2013_D10.csv: columns | PASS | 8 columns exact |
| cec2013\nemenyi_cd_cec2013_D10.csv: float format %.6e (n/a allowed) | PASS | violations=0 |
| cec2013\nemenyi_cd_cec2013_D10.csv: integer columns plain ints | PASS | violations=0 |
| cec2013\nemenyi_cd_cec2013_D10.csv: suite column constant | PASS | values=['cec2013'] |
| cec2013\nemenyi_cd_cec2013_D10.csv: dimension column constant | PASS | values=['10'] |
| cec2013\nemenyi_cd_cec2013_D10.csv: 7 rows P1 order | PASS | algs=['gsk', 'agsk', 'apgsk', 'fdb-agsk', 'atmals-gsk', 'egsk', 'dt-gsk'] |
| cec2013\nemenyi_cd_cec2013_D10.csv: k=7 | PASS | k column |
| cec2013\nemenyi_cd_cec2013_D10.csv: mean_rank in [1,7] | PASS | range [2.4107,5.8750] |
| cec2013\nemenyi_cd_cec2013_D10.csv: conditional emission (omnibus p<0.05) | PASS | Iman-Davenport p=3.264004e-07 |
| cec2013\nemenyi_cd_cec2013_D10.csv: mean_rank matches friedman file | PASS | cross-file consistency |
| cec2013\wilcoxon_holm_cec2013_D10.csv: columns | PASS | 11 columns exact |
| cec2013\wilcoxon_holm_cec2013_D10.csv: float format %.6e (n/a allowed) | PASS | violations=0 |
| cec2013\wilcoxon_holm_cec2013_D10.csv: integer columns plain ints | PASS | violations=0 |
| cec2013\wilcoxon_holm_cec2013_D10.csv: suite column constant | PASS | values=['cec2013'] |
| cec2013\wilcoxon_holm_cec2013_D10.csv: dimension column constant | PASS | values=['10'] |
| cec2013\wilcoxon_holm_cec2013_D10.csv: test_level | PASS | values=['across_functions_funclevel'] |
| cec2013\wilcoxon_holm_cec2013_D10.csv: 6 comparator rows, function=0 | PASS | 6 rows |
| cec2013\wilcoxon_holm_cec2013_D10.csv: comparator P1 order | PASS | ['gsk', 'agsk', 'apgsk', 'fdb-agsk', 'atmals-gsk', 'egsk'] |
| cec2013\wilcoxon_holm_cec2013_D10.csv: p_raw in (0,1], never 0 | PASS | violations=0; 1 rows carry unrounded p<1e-4 (floor is render-time only) |
| cec2013\wilcoxon_holm_cec2013_D10.csv: p_holm >= p_raw | PASS | violations=0 |
| cec2013\wilcoxon_holm_cec2013_D10.csv: outcome vocabulary | PASS | values=['tie', 'win'] |
| cec2013\wilcoxon_holm_cec2013_D10.csv: availability vocabulary | PASS | values=['ok'] |
| cec2013\wilcoxon_run_cec2013_D10.csv: columns | PASS | 11 columns exact |
| cec2013\wilcoxon_run_cec2013_D10.csv: float format %.6e (n/a allowed) | PASS | violations=0 |
| cec2013\wilcoxon_run_cec2013_D10.csv: integer columns plain ints | PASS | violations=0 |
| cec2013\wilcoxon_run_cec2013_D10.csv: suite column constant | PASS | values=['cec2013'] |
| cec2013\wilcoxon_run_cec2013_D10.csv: dimension column constant | PASS | values=['10'] |
| cec2013\wilcoxon_run_cec2013_D10.csv: test_level | PASS | values=['per_function_runlevel'] |
| cec2013\wilcoxon_run_cec2013_D10.csv: sort order | PASS | function asc, comparator P1 |
| cec2013\wilcoxon_run_cec2013_D10.csv: p_raw in (0,1], never 0 | PASS | violations=0; 100 rows carry unrounded p<1e-4 (floor is render-time only) |
| cec2013\wilcoxon_run_cec2013_D10.csv: p_holm >= p_raw | PASS | violations=0 |
| cec2013\wilcoxon_run_cec2013_D10.csv: outcome vocabulary | PASS | values=['loss', 'tie', 'win'] |
| cec2013\wilcoxon_run_cec2013_D10.csv: availability vocabulary | PASS | values=['ok'] |
| cec2013\effect_sizes_cec2013_D10.csv: columns | PASS | 9 columns exact |
| cec2013\effect_sizes_cec2013_D10.csv: float format %.6e (n/a allowed) | PASS | violations=0 |
| cec2013\effect_sizes_cec2013_D10.csv: integer columns plain ints | PASS | violations=0 |
| cec2013\effect_sizes_cec2013_D10.csv: suite column constant | PASS | values=['cec2013'] |
| cec2013\effect_sizes_cec2013_D10.csv: dimension column constant | PASS | values=['10'] |
| cec2013\effect_sizes_cec2013_D10.csv: sort order | PASS | function asc, comparator P1 |
| cec2013\effect_sizes_cec2013_D10.csv: a12 in [0,1] | PASS | violations=0 |
| cec2013\effect_sizes_cec2013_D10.csv: cliffs_delta=2*a12-1 in [-1,1] | PASS | violations=0 |
| cec2013\effect_sizes_cec2013_D10.csv: magnitude vocabulary | PASS | violations=0 |
| cec2013\bca_ci_cec2013_D10.csv: columns | PASS | 11 columns exact |
| cec2013\bca_ci_cec2013_D10.csv: float format %.6e (n/a allowed) | PASS | violations=0 |
| cec2013\bca_ci_cec2013_D10.csv: integer columns plain ints | PASS | violations=0 |
| cec2013\bca_ci_cec2013_D10.csv: suite column constant | PASS | values=['cec2013'] |
| cec2013\bca_ci_cec2013_D10.csv: dimension column constant | PASS | values=['10'] |
| cec2013\bca_ci_cec2013_D10.csv: sort order | PASS | function asc, comparator P1 |
| cec2013\bca_ci_cec2013_D10.csv: B=10000 on ok rows | PASS | violations=0 |
| cec2013\bca_ci_cec2013_D10.csv: ci_low<=ci_high on ok rows | PASS | violations=0 |
| cec2013\bca_ci_cec2013_D10.csv: seed_scheme literal | PASS | violations=0 |
| cec2013\bca_ci_cec2013_D10.csv: availability vocabulary | PASS | values=['no CI (degenerate cell)', 'ok'] |
| cec2013\descriptive_stats_cec2013_D30.csv: columns | PASS | 10 columns exact |
| cec2013\descriptive_stats_cec2013_D30.csv: float format %.6e (n/a allowed) | PASS | violations=0 |
| cec2013\descriptive_stats_cec2013_D30.csv: integer columns plain ints | PASS | violations=0 |
| cec2013\descriptive_stats_cec2013_D30.csv: suite column constant | PASS | values=['cec2013'] |
| cec2013\descriptive_stats_cec2013_D30.csv: dimension column constant | PASS | values=['30'] |
| cec2013\descriptive_stats_cec2013_D30.csv: sort order | PASS | function asc, algorithm P1 |
| cec2013\descriptive_stats_cec2013_D30.csv: source_path release-relative and resolvable | PASS | violations=0 (paths resolve under benchmarks/cec_reference_results/) |
| cec2013\friedman_ranks_cec2013_D30.csv: columns | PASS | 8 columns exact |
| cec2013\friedman_ranks_cec2013_D30.csv: float format %.6e (n/a allowed) | PASS | violations=0 |
| cec2013\friedman_ranks_cec2013_D30.csv: integer columns plain ints | PASS | violations=0 |
| cec2013\friedman_ranks_cec2013_D30.csv: suite column constant | PASS | values=['cec2013'] |
| cec2013\friedman_ranks_cec2013_D30.csv: dimension column constant | PASS | values=['30'] |
| cec2013\friedman_ranks_cec2013_D30.csv: 7 rows P1 order | PASS | algs=['gsk', 'agsk', 'apgsk', 'fdb-agsk', 'atmals-gsk', 'egsk', 'dt-gsk'] |
| cec2013\friedman_ranks_cec2013_D30.csv: mean_rank in [1,7] | PASS | range [3.0714,4.9821] |
| cec2013\friedman_ranks_cec2013_D30.csv: sum(mean_rank)=k(k+1)/2=28 (within %.6e storage rounding) | PASS | sum=28.000001 |
| cec2013\friedman_ranks_cec2013_D30.csv: p_value in [0,1], repeated per row | PASS | p=2.242258e-03 |
| cec2013\friedman_ranks_cec2013_D30.csv: dimension=30 | PASS | dimension values=['30'] |
| cec2013\nemenyi_cd_cec2013_D30.csv: columns | PASS | 8 columns exact |
| cec2013\nemenyi_cd_cec2013_D30.csv: float format %.6e (n/a allowed) | PASS | violations=0 |
| cec2013\nemenyi_cd_cec2013_D30.csv: integer columns plain ints | PASS | violations=0 |
| cec2013\nemenyi_cd_cec2013_D30.csv: suite column constant | PASS | values=['cec2013'] |
| cec2013\nemenyi_cd_cec2013_D30.csv: dimension column constant | PASS | values=['30'] |
| cec2013\nemenyi_cd_cec2013_D30.csv: 7 rows P1 order | PASS | algs=['gsk', 'agsk', 'apgsk', 'fdb-agsk', 'atmals-gsk', 'egsk', 'dt-gsk'] |
| cec2013\nemenyi_cd_cec2013_D30.csv: k=7 | PASS | k column |
| cec2013\nemenyi_cd_cec2013_D30.csv: mean_rank in [1,7] | PASS | range [3.0714,4.9821] |
| cec2013\nemenyi_cd_cec2013_D30.csv: conditional emission (omnibus p<0.05) | PASS | Iman-Davenport p=2.242258e-03 |
| cec2013\nemenyi_cd_cec2013_D30.csv: mean_rank matches friedman file | PASS | cross-file consistency |
| cec2013\wilcoxon_holm_cec2013_D30.csv: columns | PASS | 11 columns exact |
| cec2013\wilcoxon_holm_cec2013_D30.csv: float format %.6e (n/a allowed) | PASS | violations=0 |
| cec2013\wilcoxon_holm_cec2013_D30.csv: integer columns plain ints | PASS | violations=0 |
| cec2013\wilcoxon_holm_cec2013_D30.csv: suite column constant | PASS | values=['cec2013'] |
| cec2013\wilcoxon_holm_cec2013_D30.csv: dimension column constant | PASS | values=['30'] |
| cec2013\wilcoxon_holm_cec2013_D30.csv: test_level | PASS | values=['across_functions_funclevel'] |
| cec2013\wilcoxon_holm_cec2013_D30.csv: 6 comparator rows, function=0 | PASS | 6 rows |
| cec2013\wilcoxon_holm_cec2013_D30.csv: comparator P1 order | PASS | ['gsk', 'agsk', 'apgsk', 'fdb-agsk', 'atmals-gsk', 'egsk'] |
| cec2013\wilcoxon_holm_cec2013_D30.csv: p_raw in (0,1], never 0 | PASS | violations=0; 0 rows carry unrounded p<1e-4 (floor is render-time only) |
| cec2013\wilcoxon_holm_cec2013_D30.csv: p_holm >= p_raw | PASS | violations=0 |
| cec2013\wilcoxon_holm_cec2013_D30.csv: outcome vocabulary | PASS | values=['tie', 'win'] |
| cec2013\wilcoxon_holm_cec2013_D30.csv: availability vocabulary | PASS | values=['ok'] |
| cec2013\wilcoxon_run_cec2013_D30.csv: columns | PASS | 11 columns exact |
| cec2013\wilcoxon_run_cec2013_D30.csv: float format %.6e (n/a allowed) | PASS | violations=0 |
| cec2013\wilcoxon_run_cec2013_D30.csv: integer columns plain ints | PASS | violations=0 |
| cec2013\wilcoxon_run_cec2013_D30.csv: suite column constant | PASS | values=['cec2013'] |
| cec2013\wilcoxon_run_cec2013_D30.csv: dimension column constant | PASS | values=['30'] |
| cec2013\wilcoxon_run_cec2013_D30.csv: test_level | PASS | values=['per_function_runlevel'] |
| cec2013\wilcoxon_run_cec2013_D30.csv: sort order | PASS | function asc, comparator P1 |
| cec2013\wilcoxon_run_cec2013_D30.csv: p_raw in (0,1], never 0 | PASS | violations=0; 110 rows carry unrounded p<1e-4 (floor is render-time only) |
| cec2013\wilcoxon_run_cec2013_D30.csv: p_holm >= p_raw | PASS | violations=0 |
| cec2013\wilcoxon_run_cec2013_D30.csv: outcome vocabulary | PASS | values=['loss', 'tie', 'win'] |
| cec2013\wilcoxon_run_cec2013_D30.csv: availability vocabulary | PASS | values=['ok'] |
| cec2013\effect_sizes_cec2013_D30.csv: columns | PASS | 9 columns exact |
| cec2013\effect_sizes_cec2013_D30.csv: float format %.6e (n/a allowed) | PASS | violations=0 |
| cec2013\effect_sizes_cec2013_D30.csv: integer columns plain ints | PASS | violations=0 |
| cec2013\effect_sizes_cec2013_D30.csv: suite column constant | PASS | values=['cec2013'] |
| cec2013\effect_sizes_cec2013_D30.csv: dimension column constant | PASS | values=['30'] |
| cec2013\effect_sizes_cec2013_D30.csv: sort order | PASS | function asc, comparator P1 |
| cec2013\effect_sizes_cec2013_D30.csv: a12 in [0,1] | PASS | violations=0 |
| cec2013\effect_sizes_cec2013_D30.csv: cliffs_delta=2*a12-1 in [-1,1] | PASS | violations=0 |
| cec2013\effect_sizes_cec2013_D30.csv: magnitude vocabulary | PASS | violations=0 |
| cec2013\bca_ci_cec2013_D30.csv: columns | PASS | 11 columns exact |
| cec2013\bca_ci_cec2013_D30.csv: float format %.6e (n/a allowed) | PASS | violations=0 |
| cec2013\bca_ci_cec2013_D30.csv: integer columns plain ints | PASS | violations=0 |
| cec2013\bca_ci_cec2013_D30.csv: suite column constant | PASS | values=['cec2013'] |
| cec2013\bca_ci_cec2013_D30.csv: dimension column constant | PASS | values=['30'] |
| cec2013\bca_ci_cec2013_D30.csv: sort order | PASS | function asc, comparator P1 |
| cec2013\bca_ci_cec2013_D30.csv: B=10000 on ok rows | PASS | violations=0 |
| cec2013\bca_ci_cec2013_D30.csv: ci_low<=ci_high on ok rows | PASS | violations=0 |
| cec2013\bca_ci_cec2013_D30.csv: seed_scheme literal | PASS | violations=0 |
| cec2013\bca_ci_cec2013_D30.csv: availability vocabulary | PASS | values=['no CI (degenerate cell)', 'ok'] |
| cec2013\convergence_checkpoints_cec2013_D30.csv: columns | PASS | 8 columns exact |
| cec2013\convergence_checkpoints_cec2013_D30.csv: float format %.6e (n/a allowed) | PASS | violations=0 |
| cec2013\convergence_checkpoints_cec2013_D30.csv: integer columns plain ints | PASS | violations=0 |
| cec2013\convergence_checkpoints_cec2013_D30.csv: suite column constant | PASS | values=['cec2013'] |
| cec2013\convergence_checkpoints_cec2013_D30.csv: dimension column constant | PASS | values=['30'] |
| cec2013\convergence_checkpoints_cec2013_D30.csv: sort order | PASS | function asc, algorithm P1, checkpoint_nfes asc |
| cec2013\convergence_checkpoints_cec2013_D30.csv: availability vocabulary | PASS | values=['ok'] |
| cec2013\descriptive_stats_cec2013_D50.csv: columns | PASS | 10 columns exact |
| cec2013\descriptive_stats_cec2013_D50.csv: float format %.6e (n/a allowed) | PASS | violations=0 |
| cec2013\descriptive_stats_cec2013_D50.csv: integer columns plain ints | PASS | violations=0 |
| cec2013\descriptive_stats_cec2013_D50.csv: suite column constant | PASS | values=['cec2013'] |
| cec2013\descriptive_stats_cec2013_D50.csv: dimension column constant | PASS | values=['50'] |
| cec2013\descriptive_stats_cec2013_D50.csv: sort order | PASS | function asc, algorithm P1 |
| cec2013\descriptive_stats_cec2013_D50.csv: source_path release-relative and resolvable | PASS | violations=0 (paths resolve under benchmarks/cec_reference_results/) |
| cec2013\friedman_ranks_cec2013_D50.csv: columns | PASS | 8 columns exact |
| cec2013\friedman_ranks_cec2013_D50.csv: float format %.6e (n/a allowed) | PASS | violations=0 |
| cec2013\friedman_ranks_cec2013_D50.csv: integer columns plain ints | PASS | violations=0 |
| cec2013\friedman_ranks_cec2013_D50.csv: suite column constant | PASS | values=['cec2013'] |
| cec2013\friedman_ranks_cec2013_D50.csv: dimension column constant | PASS | values=['50'] |
| cec2013\friedman_ranks_cec2013_D50.csv: 7 rows P1 order | PASS | algs=['gsk', 'agsk', 'apgsk', 'fdb-agsk', 'atmals-gsk', 'egsk', 'dt-gsk'] |
| cec2013\friedman_ranks_cec2013_D50.csv: mean_rank in [1,7] | PASS | range [2.6071,5.1607] |
| cec2013\friedman_ranks_cec2013_D50.csv: sum(mean_rank)=k(k+1)/2=28 (within %.6e storage rounding) | PASS | sum=27.999999 |
| cec2013\friedman_ranks_cec2013_D50.csv: p_value in [0,1], repeated per row | PASS | p=9.212405e-06 |
| cec2013\friedman_ranks_cec2013_D50.csv: dimension=50 | PASS | dimension values=['50'] |
| cec2013\nemenyi_cd_cec2013_D50.csv: columns | PASS | 8 columns exact |
| cec2013\nemenyi_cd_cec2013_D50.csv: float format %.6e (n/a allowed) | PASS | violations=0 |
| cec2013\nemenyi_cd_cec2013_D50.csv: integer columns plain ints | PASS | violations=0 |
| cec2013\nemenyi_cd_cec2013_D50.csv: suite column constant | PASS | values=['cec2013'] |
| cec2013\nemenyi_cd_cec2013_D50.csv: dimension column constant | PASS | values=['50'] |
| cec2013\nemenyi_cd_cec2013_D50.csv: 7 rows P1 order | PASS | algs=['gsk', 'agsk', 'apgsk', 'fdb-agsk', 'atmals-gsk', 'egsk', 'dt-gsk'] |
| cec2013\nemenyi_cd_cec2013_D50.csv: k=7 | PASS | k column |
| cec2013\nemenyi_cd_cec2013_D50.csv: mean_rank in [1,7] | PASS | range [2.6071,5.1607] |
| cec2013\nemenyi_cd_cec2013_D50.csv: conditional emission (omnibus p<0.05) | PASS | Iman-Davenport p=9.212405e-06 |
| cec2013\nemenyi_cd_cec2013_D50.csv: mean_rank matches friedman file | PASS | cross-file consistency |
| cec2013\wilcoxon_holm_cec2013_D50.csv: columns | PASS | 11 columns exact |
| cec2013\wilcoxon_holm_cec2013_D50.csv: float format %.6e (n/a allowed) | PASS | violations=0 |
| cec2013\wilcoxon_holm_cec2013_D50.csv: integer columns plain ints | PASS | violations=0 |
| cec2013\wilcoxon_holm_cec2013_D50.csv: suite column constant | PASS | values=['cec2013'] |
| cec2013\wilcoxon_holm_cec2013_D50.csv: dimension column constant | PASS | values=['50'] |
| cec2013\wilcoxon_holm_cec2013_D50.csv: test_level | PASS | values=['across_functions_funclevel'] |
| cec2013\wilcoxon_holm_cec2013_D50.csv: 6 comparator rows, function=0 | PASS | 6 rows |
| cec2013\wilcoxon_holm_cec2013_D50.csv: comparator P1 order | PASS | ['gsk', 'agsk', 'apgsk', 'fdb-agsk', 'atmals-gsk', 'egsk'] |
| cec2013\wilcoxon_holm_cec2013_D50.csv: p_raw in (0,1], never 0 | PASS | violations=0; 0 rows carry unrounded p<1e-4 (floor is render-time only) |
| cec2013\wilcoxon_holm_cec2013_D50.csv: p_holm >= p_raw | PASS | violations=0 |
| cec2013\wilcoxon_holm_cec2013_D50.csv: outcome vocabulary | PASS | values=['tie', 'win'] |
| cec2013\wilcoxon_holm_cec2013_D50.csv: availability vocabulary | PASS | values=['ok'] |
| cec2013\wilcoxon_run_cec2013_D50.csv: columns | PASS | 11 columns exact |
| cec2013\wilcoxon_run_cec2013_D50.csv: float format %.6e (n/a allowed) | PASS | violations=0 |
| cec2013\wilcoxon_run_cec2013_D50.csv: integer columns plain ints | PASS | violations=0 |
| cec2013\wilcoxon_run_cec2013_D50.csv: suite column constant | PASS | values=['cec2013'] |
| cec2013\wilcoxon_run_cec2013_D50.csv: dimension column constant | PASS | values=['50'] |
| cec2013\wilcoxon_run_cec2013_D50.csv: test_level | PASS | values=['per_function_runlevel'] |
| cec2013\wilcoxon_run_cec2013_D50.csv: sort order | PASS | function asc, comparator P1 |
| cec2013\wilcoxon_run_cec2013_D50.csv: p_raw in (0,1], never 0 | PASS | violations=0; 113 rows carry unrounded p<1e-4 (floor is render-time only) |
| cec2013\wilcoxon_run_cec2013_D50.csv: p_holm >= p_raw | PASS | violations=0 |
| cec2013\wilcoxon_run_cec2013_D50.csv: outcome vocabulary | PASS | values=['loss', 'tie', 'win'] |
| cec2013\wilcoxon_run_cec2013_D50.csv: availability vocabulary | PASS | values=['ok'] |
| cec2013\effect_sizes_cec2013_D50.csv: columns | PASS | 9 columns exact |
| cec2013\effect_sizes_cec2013_D50.csv: float format %.6e (n/a allowed) | PASS | violations=0 |
| cec2013\effect_sizes_cec2013_D50.csv: integer columns plain ints | PASS | violations=0 |
| cec2013\effect_sizes_cec2013_D50.csv: suite column constant | PASS | values=['cec2013'] |
| cec2013\effect_sizes_cec2013_D50.csv: dimension column constant | PASS | values=['50'] |
| cec2013\effect_sizes_cec2013_D50.csv: sort order | PASS | function asc, comparator P1 |
| cec2013\effect_sizes_cec2013_D50.csv: a12 in [0,1] | PASS | violations=0 |
| cec2013\effect_sizes_cec2013_D50.csv: cliffs_delta=2*a12-1 in [-1,1] | PASS | violations=0 |
| cec2013\effect_sizes_cec2013_D50.csv: magnitude vocabulary | PASS | violations=0 |
| cec2013\bca_ci_cec2013_D50.csv: columns | PASS | 11 columns exact |
| cec2013\bca_ci_cec2013_D50.csv: float format %.6e (n/a allowed) | PASS | violations=0 |
| cec2013\bca_ci_cec2013_D50.csv: integer columns plain ints | PASS | violations=0 |
| cec2013\bca_ci_cec2013_D50.csv: suite column constant | PASS | values=['cec2013'] |
| cec2013\bca_ci_cec2013_D50.csv: dimension column constant | PASS | values=['50'] |
| cec2013\bca_ci_cec2013_D50.csv: sort order | PASS | function asc, comparator P1 |
| cec2013\bca_ci_cec2013_D50.csv: B=10000 on ok rows | PASS | violations=0 |
| cec2013\bca_ci_cec2013_D50.csv: ci_low<=ci_high on ok rows | PASS | violations=0 |
| cec2013\bca_ci_cec2013_D50.csv: seed_scheme literal | PASS | violations=0 |
| cec2013\bca_ci_cec2013_D50.csv: availability vocabulary | PASS | values=['no CI (degenerate cell)', 'ok'] |
| cec2013\friedman_ranks_cec2013_overall.csv: columns | PASS | 3 columns exact |
| cec2013\friedman_ranks_cec2013_overall.csv: float format %.6e (n/a allowed) | PASS | violations=0 |
| cec2013\friedman_ranks_cec2013_overall.csv: suite column constant | PASS | values=['cec2013'] |
| cec2013\friedman_ranks_cec2013_overall.csv: 7 rows P1 order | PASS | algs=['gsk', 'agsk', 'apgsk', 'fdb-agsk', 'atmals-gsk', 'egsk', 'dt-gsk'] |
| cec2013\friedman_ranks_cec2013_overall.csv: mean_rank in [1,7] | PASS | range [2.7976,5.3393] |
| cec2013\friedman_ranks_cec2013_overall.csv: no pooled test columns | PASS | 3-column descriptive form, no chi2/F/p |
| cec2011\descriptive_stats_cec2011.csv: columns | PASS | 10 columns exact |
| cec2011\descriptive_stats_cec2011.csv: float format %.6e (n/a allowed) | PASS | violations=0 |
| cec2011\descriptive_stats_cec2011.csv: integer columns plain ints | PASS | violations=0 |
| cec2011\descriptive_stats_cec2011.csv: suite column constant | PASS | values=['cec2011'] |
| cec2011\descriptive_stats_cec2011.csv: sort order | PASS | function asc, algorithm P1 |
| cec2011\descriptive_stats_cec2011.csv: source_path release-relative and resolvable | PASS | violations=0 (paths resolve under benchmarks/cec_reference_results/) |
| cec2011\friedman_ranks_cec2011.csv: columns | PASS | 8 columns exact |
| cec2011\friedman_ranks_cec2011.csv: float format %.6e (n/a allowed) | PASS | violations=0 |
| cec2011\friedman_ranks_cec2011.csv: integer columns plain ints | PASS | violations=0 |
| cec2011\friedman_ranks_cec2011.csv: suite column constant | PASS | values=['cec2011'] |
| cec2011\friedman_ranks_cec2011.csv: 7 rows P1 order | PASS | algs=['gsk', 'agsk', 'apgsk', 'fdb-agsk', 'atmals-gsk', 'egsk', 'dt-gsk'] |
| cec2011\friedman_ranks_cec2011.csv: mean_rank in [1,7] | PASS | range [2.5227,4.7500] |
| cec2011\friedman_ranks_cec2011.csv: sum(mean_rank)=k(k+1)/2=28 (within %.6e storage rounding) | PASS | sum=28.000000 |
| cec2011\friedman_ranks_cec2011.csv: p_value in [0,1], repeated per row | PASS | p=2.160258e-03 |
| cec2011\friedman_ranks_cec2011.csv: dimension=0 | PASS | dimension values=['0'] |
| cec2011\nemenyi_cd_cec2011.csv: columns | PASS | 8 columns exact |
| cec2011\nemenyi_cd_cec2011.csv: float format %.6e (n/a allowed) | PASS | violations=0 |
| cec2011\nemenyi_cd_cec2011.csv: integer columns plain ints | PASS | violations=0 |
| cec2011\nemenyi_cd_cec2011.csv: suite column constant | PASS | values=['cec2011'] |
| cec2011\nemenyi_cd_cec2011.csv: 7 rows P1 order | PASS | algs=['gsk', 'agsk', 'apgsk', 'fdb-agsk', 'atmals-gsk', 'egsk', 'dt-gsk'] |
| cec2011\nemenyi_cd_cec2011.csv: k=7 | PASS | k column |
| cec2011\nemenyi_cd_cec2011.csv: mean_rank in [1,7] | PASS | range [2.5227,4.7500] |
| cec2011\nemenyi_cd_cec2011.csv: conditional emission (omnibus p<0.05) | PASS | Iman-Davenport p=2.160258e-03 |
| cec2011\nemenyi_cd_cec2011.csv: mean_rank matches friedman file | PASS | cross-file consistency |
| cec2011\wilcoxon_holm_cec2011.csv: columns | PASS | 11 columns exact |
| cec2011\wilcoxon_holm_cec2011.csv: float format %.6e (n/a allowed) | PASS | violations=0 |
| cec2011\wilcoxon_holm_cec2011.csv: integer columns plain ints | PASS | violations=0 |
| cec2011\wilcoxon_holm_cec2011.csv: suite column constant | PASS | values=['cec2011'] |
| cec2011\wilcoxon_holm_cec2011.csv: test_level | PASS | values=['across_functions_funclevel'] |
| cec2011\wilcoxon_holm_cec2011.csv: 6 comparator rows, function=0 | PASS | 6 rows |
| cec2011\wilcoxon_holm_cec2011.csv: comparator P1 order | PASS | ['gsk', 'agsk', 'apgsk', 'fdb-agsk', 'atmals-gsk', 'egsk'] |
| cec2011\wilcoxon_holm_cec2011.csv: p_raw in (0,1], never 0 | PASS | violations=0; 0 rows carry unrounded p<1e-4 (floor is render-time only) |
| cec2011\wilcoxon_holm_cec2011.csv: p_holm >= p_raw | PASS | violations=0 |
| cec2011\wilcoxon_holm_cec2011.csv: outcome vocabulary | PASS | values=['loss', 'tie', 'win'] |
| cec2011\wilcoxon_holm_cec2011.csv: availability vocabulary | PASS | values=['ok'] |
| cec2011\wilcoxon_run_cec2011.csv: columns | PASS | 11 columns exact |
| cec2011\wilcoxon_run_cec2011.csv: float format %.6e (n/a allowed) | PASS | violations=0 |
| cec2011\wilcoxon_run_cec2011.csv: integer columns plain ints | PASS | violations=0 |
| cec2011\wilcoxon_run_cec2011.csv: suite column constant | PASS | values=['cec2011'] |
| cec2011\wilcoxon_run_cec2011.csv: test_level | PASS | values=['per_function_runlevel'] |
| cec2011\wilcoxon_run_cec2011.csv: sort order | PASS | function asc, comparator P1 |
| cec2011\wilcoxon_run_cec2011.csv: p_raw in (0,1], never 0 | PASS | violations=0; 45 rows carry unrounded p<1e-4 (floor is render-time only) |
| cec2011\wilcoxon_run_cec2011.csv: p_holm >= p_raw | PASS | violations=0 |
| cec2011\wilcoxon_run_cec2011.csv: outcome vocabulary | PASS | values=['loss', 'tie', 'win'] |
| cec2011\wilcoxon_run_cec2011.csv: availability vocabulary | PASS | values=['ok'] |
| cec2011\effect_sizes_cec2011.csv: columns | PASS | 9 columns exact |
| cec2011\effect_sizes_cec2011.csv: float format %.6e (n/a allowed) | PASS | violations=0 |
| cec2011\effect_sizes_cec2011.csv: integer columns plain ints | PASS | violations=0 |
| cec2011\effect_sizes_cec2011.csv: suite column constant | PASS | values=['cec2011'] |
| cec2011\effect_sizes_cec2011.csv: sort order | PASS | function asc, comparator P1 |
| cec2011\effect_sizes_cec2011.csv: a12 in [0,1] | PASS | violations=0 |
| cec2011\effect_sizes_cec2011.csv: cliffs_delta=2*a12-1 in [-1,1] | PASS | violations=0 |
| cec2011\effect_sizes_cec2011.csv: magnitude vocabulary | PASS | violations=0 |
| cec2011\bca_ci_cec2011.csv: columns | PASS | 11 columns exact |
| cec2011\bca_ci_cec2011.csv: float format %.6e (n/a allowed) | PASS | violations=0 |
| cec2011\bca_ci_cec2011.csv: integer columns plain ints | PASS | violations=0 |
| cec2011\bca_ci_cec2011.csv: suite column constant | PASS | values=['cec2011'] |
| cec2011\bca_ci_cec2011.csv: sort order | PASS | function asc, comparator P1 |
| cec2011\bca_ci_cec2011.csv: B=10000 on ok rows | PASS | violations=0 |
| cec2011\bca_ci_cec2011.csv: ci_low<=ci_high on ok rows | PASS | violations=0 |
| cec2011\bca_ci_cec2011.csv: seed_scheme literal | PASS | violations=0 |
| cec2011\bca_ci_cec2011.csv: availability vocabulary | PASS | values=['no CI (degenerate cell)', 'ok'] |
| cec2011\convergence_checkpoints_cec2011.csv: columns | PASS | 8 columns exact |
| cec2011\convergence_checkpoints_cec2011.csv: float format %.6e (n/a allowed) | PASS | violations=0 |
| cec2011\convergence_checkpoints_cec2011.csv: integer columns plain ints | PASS | violations=0 |
| cec2011\convergence_checkpoints_cec2011.csv: suite column constant | PASS | values=['cec2011'] |
| cec2011\convergence_checkpoints_cec2011.csv: sort order | PASS | function asc, algorithm P1, checkpoint_nfes asc |
| cec2011\convergence_checkpoints_cec2011.csv: availability vocabulary | PASS | values=['ok'] |
| exploratory BH files: cec2017 run-level only, 4 files | PASS | ['wilcoxon_run_cec2017_D100_exploratory_bh.csv', 'wilcoxon_run_cec2017_D10_exploratory_bh.csv', 'wilcoxon_run_cec2017_D30_exploratory_bh.csv', 'wilcoxon_run_cec2017_D50_exploratory_bh.csv'] |
| no exploratory BH outside cec2017 | PASS | found=[] |
| cec2013 convergence grids: D30 only (P4) | PASS | ['convergence_checkpoints_cec2013_D30.csv'] |
| cec2017\curve_selection_cec2017_D30.csv: columns (exactly 8, no 9th) | PASS | ['suite', 'dimension', 'function', 'category', 'difficulty_tercile', 'ismgsk_standing', 'selection_reason', 'selected_for_main'] |
| cec2017\curve_selection_cec2017_D30.csv: 29 rows | PASS | 29 rows |
| cec2017\curve_selection_cec2017_D30.csv: sort dimension asc, function asc | PASS | sorted |
| cec2017\curve_selection_cec2017_D30.csv: exactly 4 selected_for_main=TRUE | PASS | 4 TRUE |
| cec2017\curve_selection_cec2017_D30.csv: vocabulary (category/tercile/standing/flag) | PASS | violations=0 |
| cec2017\curve_selection_cec2017_D30.csv: one selected per category | PASS | selected categories=['composition', 'hybrid', 'simple_multimodal', 'unimodal'] |
| cec2017\curve_selection_cec2017_D30.csv: selection_reason consistent with flag | PASS | violations=0 |
| cec2017\curve_selection_cec2017_D100.csv: columns (exactly 8, no 9th) | PASS | ['suite', 'dimension', 'function', 'category', 'difficulty_tercile', 'ismgsk_standing', 'selection_reason', 'selected_for_main'] |
| cec2017\curve_selection_cec2017_D100.csv: 29 rows | PASS | 29 rows |
| cec2017\curve_selection_cec2017_D100.csv: sort dimension asc, function asc | PASS | sorted |
| cec2017\curve_selection_cec2017_D100.csv: exactly 4 selected_for_main=TRUE | PASS | 4 TRUE |
| cec2017\curve_selection_cec2017_D100.csv: vocabulary (category/tercile/standing/flag) | PASS | violations=0 |
| cec2017\curve_selection_cec2017_D100.csv: one selected per category | PASS | selected categories=['composition', 'hybrid', 'simple_multimodal', 'unimodal'] |
| cec2017\curve_selection_cec2017_D100.csv: selection_reason consistent with flag | PASS | violations=0 |
| curve_selection joint constraint: >=1 hard and >=1 weak among 8 selected | PASS | selected strata=[('easy', 'strong'), ('hard', 'comparable'), ('hard', 'comparable'), ('hard', 'weak'), ('easy', 'strong'), ('easy', 'strong'), ('hard', 'comparable'), ('hard', 'comparable')] |
| phase_05/curve_selection.csv: 58 data rows under 8-col header | PASS | header ok=True, 58 rows |
| phase_05/curve_selection.csv: exactly 8 TRUE | PASS | 8 TRUE |
| phase_05 curve_selection.csv rows == D30+D100 emissions | PASS | byte-level row comparison |
| cec2017\cost_cec2017.csv: columns (SAP Sec.9 family; no schema doc) | PASS | ['suite', 'dimension', 'algorithm', 'n_runs', 'mean_runtime_seconds', 'sd_runtime_seconds', 'comparability', 'availability'] |
| cec2017\cost_cec2017.csv: float format on ok rows | PASS | violations=0 |
| cec2017\cost_cec2017.csv: apgsk cec2017 D10/30/50 disclosed-unavailable | PASS | 3 rows |
| cec2017\cost_cec2017.csv: sort (suite, dimension asc, algorithm P1) | PASS | 56 rows |
| cec2017\rank_trend_cec2017.csv: columns (SAP Sec.12 family; no schema doc) | PASS | ['suite', 'dimension', 'algorithm', 'mean_rank', 'ordinal_position'] |
| cec2017\rank_trend_cec2017.csv: 28 rows (4 dims x 7 algs) | PASS | 28 |
| cec2017\rank_trend_cec2017.csv: ranks in [1,7], ordinal in [1,7] | PASS | range check |
| cec2017\rank_trend_cec2017.csv: mean_rank matches AN-OMNI friedman files (no recompute) | PASS | cross-file consistency all 4 dims |
| cec2017\class_ranks_cec2017.csv: columns (SAP Sec.11 family; no schema doc) | PASS | ['suite', 'dimension', 'category', 'n_functions', 'algorithm', 'mean_rank', 'ism_wins', 'ism_ties', 'ism_losses'] |
| cec2017\class_ranks_cec2017.csv: 112 rows (4 dims x 4 cats x 7 algs) | PASS | 112 |
| cec2017\class_ranks_cec2017.csv: verified category sizes (2/7/10/10) | PASS | violations=0 |
| cec2017\class_ranks_cec2017.csv: mean_rank in [1,7] | PASS | range |
| cec2017\class_ranks_cec2017.csv: W+T+L = n_functions (n/a only on dt-gsk self rows) | PASS | violations=0; n/a rows=16 (all dt-gsk=True) |
| cec2017\headline_bca.csv: equals union of bca_ci_cec2017_D10..D100 | PASS | 696 rows vs 696 expected (registry-defined T-BCA union) |
| robustness family: 8 pre-registered check files present | PASS | ['robustness_cec2017_r01_mean_vs_median.csv', 'robustness_cec2017_r02_floor_sensitivity.csv', 'robustness_cec2017_r03_lofo_friedman.csv', 'robustness_cec2017_r04_disputed_cell_exclusion.csv', 'robustness_cec2017_r05_unpaired_companion.csv', 'robustness_cec2017_r06_holm_vs_bh.csv', 'robustness_cec2017_r07_secondary_suite_effect.csv', 'robustness_cec2017_r08_overall_aggregation_variants.csv'] |
| cec2017\robustness\robustness_cec2017_r01_mean_vs_median.csv: non-integer numeric cells use %.6e | PASS | violations=0 |
| cec2017\robustness\robustness_cec2017_r01_mean_vs_median.csv: non-empty with header | PASS | 52 data rows, 12 columns |
| cec2017\robustness\robustness_cec2017_r01_mean_vs_median.csv: verdict vocabulary (Agree/Diverge per robustness_plan.md Sec.0.2; R7 qualitative wording per SAP Sec.10 item 7) | PASS | values=['agree', 'diverge'] |
| cec2017\robustness\robustness_cec2017_r01_mean_vs_median.csv: digest + source_audit companions present | PASS | robustness_plan.md Sec.3 companions |
| cec2017\robustness\robustness_cec2017_r02_floor_sensitivity.csv: non-integer numeric cells use %.6e | PASS | violations=0 |
| cec2017\robustness\robustness_cec2017_r02_floor_sensitivity.csv: non-empty with header | PASS | 53 data rows, 12 columns |
| cec2017\robustness\robustness_cec2017_r02_floor_sensitivity.csv: R1 branch-B scan record present | PASS | scan row verdict='count_in_(0,1e-8)=0/66963;branch=B' |
| cec2017\robustness\robustness_cec2017_r02_floor_sensitivity.csv: verdict vocabulary (Agree/Diverge per robustness_plan.md Sec.0.2; R7 qualitative wording per SAP Sec.10 item 7) | PASS | values=['agree'] |
| cec2017\robustness\robustness_cec2017_r02_floor_sensitivity.csv: digest + source_audit companions present | PASS | robustness_plan.md Sec.3 companions |
| cec2017\robustness\robustness_cec2017_r03_lofo_friedman.csv: non-integer numeric cells use %.6e | PASS | violations=0 |
| cec2017\robustness\robustness_cec2017_r03_lofo_friedman.csv: non-empty with header | PASS | 28 data rows, 9 columns |
| cec2017\robustness\robustness_cec2017_r03_lofo_friedman.csv: verdict vocabulary (Agree/Diverge per robustness_plan.md Sec.0.2; R7 qualitative wording per SAP Sec.10 item 7) | PASS | values=['agree', 'diverge'] |
| cec2017\robustness\robustness_cec2017_r03_lofo_friedman.csv: digest + source_audit companions present | PASS | robustness_plan.md Sec.3 companions |
| cec2017\robustness\robustness_cec2017_r04_disputed_cell_exclusion.csv: non-integer numeric cells use %.6e | PASS | violations=0 |
| cec2017\robustness\robustness_cec2017_r04_disputed_cell_exclusion.csv: non-empty with header | PASS | 49 data rows, 10 columns |
| cec2017\robustness\robustness_cec2017_r04_disputed_cell_exclusion.csv: verdict vocabulary (Agree/Diverge per robustness_plan.md Sec.0.2; R7 qualitative wording per SAP Sec.10 item 7) | PASS | values=['agree', 'diverge'] |
| cec2017\robustness\robustness_cec2017_r04_disputed_cell_exclusion.csv: digest + source_audit companions present | PASS | robustness_plan.md Sec.3 companions |
| cec2017\robustness\robustness_cec2017_r05_unpaired_companion.csv: non-integer numeric cells use %.6e | PASS | violations=0 |
| cec2017\robustness\robustness_cec2017_r05_unpaired_companion.csv: non-empty with header | PASS | 609 data rows, 11 columns |
| cec2017\robustness\robustness_cec2017_r05_unpaired_companion.csv: digest + source_audit companions present | PASS | robustness_plan.md Sec.3 companions |
| cec2017\robustness\robustness_cec2017_r06_holm_vs_bh.csv: non-integer numeric cells use %.6e | PASS | violations=0 |
| cec2017\robustness\robustness_cec2017_r06_holm_vs_bh.csv: non-empty with header | PASS | 24 data rows, 9 columns |
| cec2017\robustness\robustness_cec2017_r06_holm_vs_bh.csv: digest + source_audit companions present | PASS | robustness_plan.md Sec.3 companions |
| cec2017\robustness\robustness_cec2017_r07_secondary_suite_effect.csv: non-integer numeric cells use %.6e | PASS | violations=0 |
| cec2017\robustness\robustness_cec2017_r07_secondary_suite_effect.csv: non-empty with header | PASS | 7 data rows, 8 columns |
| cec2017\robustness\robustness_cec2017_r07_secondary_suite_effect.csv: verdict vocabulary (Agree/Diverge per robustness_plan.md Sec.0.2; R7 qualitative wording per SAP Sec.10 item 7) | PASS | values=['diverge', 'qualitatively-consistent'] |
| cec2017\robustness\robustness_cec2017_r07_secondary_suite_effect.csv: digest + source_audit companions present | PASS | robustness_plan.md Sec.3 companions |
| cec2017\robustness\robustness_cec2017_r08_overall_aggregation_variants.csv: non-integer numeric cells use %.6e | PASS | violations=0 |
| cec2017\robustness\robustness_cec2017_r08_overall_aggregation_variants.csv: non-empty with header | PASS | 7 data rows, 10 columns |
| cec2017\robustness\robustness_cec2017_r08_overall_aggregation_variants.csv: verdict vocabulary (Agree/Diverge per robustness_plan.md Sec.0.2; R7 qualitative wording per SAP Sec.10 item 7) | PASS | values=['agree'] |
| cec2017\robustness\robustness_cec2017_r08_overall_aggregation_variants.csv: digest + source_audit companions present | PASS | robustness_plan.md Sec.3 companions |
| primary_stats\statistical_results.csv: 31-column Section 7.14 schema | PASS | 31 columns |
| primary_stats\statistical_results.csv: evidence_release_id constant | PASS | values=['rel-2026-07-10-262fc16c9'] |
| primary_stats\statistical_results.csv: analysis_id coverage | PASS | 57 distinct analysis_ids over 4987 rows |
| primary_stats\statistical_results.csv: p_raw in (0,1] where numeric | PASS | violations=0 |
| closed naming vocabulary (strict_source_execution.md Sec.5) | PASS | all CSVs match <family>_<suite>[_D<dim>][_<qualifier>].csv; exceptions noted: primary_stats/statistical_results.csv (Sec.7.14), cec2017/headline_bca.csv (registry T-BCA union); off-pattern=[] |
| no timestamps inside output CSVs | PASS | hits=[] |

</details>

## Category 3 — Denominators — **PASS**

CEC2017 files carry exactly 29 functions (F1, F3-F30) at each of D10/D30/D50/D100; CEC2013 exactly 28 functions (F1-F28, no F2 exclusion) at D10/D30/D50; CEC2011 exactly 22 problems at native dimensions. Run counts: n_runs / n_pairs = 51 (CEC2017), 51 (CEC2013), 25 (CEC2011) on every `ok` row; Friedman n_blocks = 29/28/22; convergence n_runs = 51/25 at every checkpoint row.

<details><summary>All 122 denominator checks (click to expand)</summary>

| Check | Result | Detail |
|---|---|---|
| cec2017\descriptive_stats_cec2017_D10.csv: function set | PASS | 29 functions (expected 29) |
| cec2017\descriptive_stats_cec2017_D10.csv: row count | PASS | 203 rows (expected 203) |
| cec2017\friedman_ranks_cec2017_D10.csv: n_blocks | PASS | n_blocks=['29'] (expected 29) |
| cec2017\nemenyi_cd_cec2017_D10.csv: n_blocks | PASS | n_blocks=['29'] |
| cec2017\wilcoxon_holm_cec2017_D10.csv: n_pairs<= 29 functions (zero-diffs discarded) | PASS | violations=0 |
| cec2017\wilcoxon_run_cec2017_D10.csv: rows = 29 functions x 6 comparators | PASS | 174 rows |
| cec2017\wilcoxon_run_cec2017_D10.csv: function set | PASS | 29 functions |
| cec2017\wilcoxon_run_cec2017_D10.csv: n_pairs=51 on ok rows | PASS | violations=0 |
| cec2017\wilcoxon_run_cec2017_D10_exploratory_bh.csv: rows = 29 functions x 6 comparators | PASS | 174 rows |
| cec2017\wilcoxon_run_cec2017_D10_exploratory_bh.csv: function set | PASS | 29 functions |
| cec2017\wilcoxon_run_cec2017_D10_exploratory_bh.csv: n_pairs=51 on ok rows | PASS | violations=0 |
| cec2017\effect_sizes_cec2017_D10.csv: rows = 29 x 6 | PASS | 174 rows |
| cec2017\effect_sizes_cec2017_D10.csv: n_runs=51 on ok rows | PASS | values=['51'] |
| cec2017\bca_ci_cec2017_D10.csv: rows = 29 x 6 | PASS | 174 rows |
| cec2017\bca_ci_cec2017_D10.csv: n_runs=51 on ok rows | PASS | values=['51'] |
| cec2017\convergence_checkpoints_cec2017_D10.csv: function set | PASS | 29 functions |
| cec2017\convergence_checkpoints_cec2017_D10.csv: n_runs=51 on ok rows | PASS | violations=0 of 2842 rows |
| cec2017\descriptive_stats_cec2017_D30.csv: function set | PASS | 29 functions (expected 29) |
| cec2017\descriptive_stats_cec2017_D30.csv: row count | PASS | 203 rows (expected 203) |
| cec2017\friedman_ranks_cec2017_D30.csv: n_blocks | PASS | n_blocks=['29'] (expected 29) |
| cec2017\nemenyi_cd_cec2017_D30.csv: n_blocks | PASS | n_blocks=['29'] |
| cec2017\wilcoxon_holm_cec2017_D30.csv: n_pairs<= 29 functions (zero-diffs discarded) | PASS | violations=0 |
| cec2017\wilcoxon_run_cec2017_D30.csv: rows = 29 functions x 6 comparators | PASS | 174 rows |
| cec2017\wilcoxon_run_cec2017_D30.csv: function set | PASS | 29 functions |
| cec2017\wilcoxon_run_cec2017_D30.csv: n_pairs=51 on ok rows | PASS | violations=0 |
| cec2017\wilcoxon_run_cec2017_D30_exploratory_bh.csv: rows = 29 functions x 6 comparators | PASS | 174 rows |
| cec2017\wilcoxon_run_cec2017_D30_exploratory_bh.csv: function set | PASS | 29 functions |
| cec2017\wilcoxon_run_cec2017_D30_exploratory_bh.csv: n_pairs=51 on ok rows | PASS | violations=0 |
| cec2017\effect_sizes_cec2017_D30.csv: rows = 29 x 6 | PASS | 174 rows |
| cec2017\effect_sizes_cec2017_D30.csv: n_runs=51 on ok rows | PASS | values=['51'] |
| cec2017\bca_ci_cec2017_D30.csv: rows = 29 x 6 | PASS | 174 rows |
| cec2017\bca_ci_cec2017_D30.csv: n_runs=51 on ok rows | PASS | values=['51'] |
| cec2017\convergence_checkpoints_cec2017_D30.csv: function set | PASS | 29 functions |
| cec2017\convergence_checkpoints_cec2017_D30.csv: n_runs=51 on ok rows | PASS | violations=0 of 2842 rows |
| cec2017\descriptive_stats_cec2017_D50.csv: function set | PASS | 29 functions (expected 29) |
| cec2017\descriptive_stats_cec2017_D50.csv: row count | PASS | 203 rows (expected 203) |
| cec2017\friedman_ranks_cec2017_D50.csv: n_blocks | PASS | n_blocks=['29'] (expected 29) |
| cec2017\nemenyi_cd_cec2017_D50.csv: n_blocks | PASS | n_blocks=['29'] |
| cec2017\wilcoxon_holm_cec2017_D50.csv: n_pairs<= 29 functions (zero-diffs discarded) | PASS | violations=0 |
| cec2017\wilcoxon_run_cec2017_D50.csv: rows = 29 functions x 6 comparators | PASS | 174 rows |
| cec2017\wilcoxon_run_cec2017_D50.csv: function set | PASS | 29 functions |
| cec2017\wilcoxon_run_cec2017_D50.csv: n_pairs=51 on ok rows | PASS | violations=0 |
| cec2017\wilcoxon_run_cec2017_D50_exploratory_bh.csv: rows = 29 functions x 6 comparators | PASS | 174 rows |
| cec2017\wilcoxon_run_cec2017_D50_exploratory_bh.csv: function set | PASS | 29 functions |
| cec2017\wilcoxon_run_cec2017_D50_exploratory_bh.csv: n_pairs=51 on ok rows | PASS | violations=0 |
| cec2017\effect_sizes_cec2017_D50.csv: rows = 29 x 6 | PASS | 174 rows |
| cec2017\effect_sizes_cec2017_D50.csv: n_runs=51 on ok rows | PASS | values=['51'] |
| cec2017\bca_ci_cec2017_D50.csv: rows = 29 x 6 | PASS | 174 rows |
| cec2017\bca_ci_cec2017_D50.csv: n_runs=51 on ok rows | PASS | values=['51'] |
| cec2017\convergence_checkpoints_cec2017_D50.csv: function set | PASS | 29 functions |
| cec2017\convergence_checkpoints_cec2017_D50.csv: n_runs=51 on ok rows | PASS | violations=0 of 2842 rows |
| cec2017\descriptive_stats_cec2017_D100.csv: function set | PASS | 29 functions (expected 29) |
| cec2017\descriptive_stats_cec2017_D100.csv: row count | PASS | 203 rows (expected 203) |
| cec2017\friedman_ranks_cec2017_D100.csv: n_blocks | PASS | n_blocks=['29'] (expected 29) |
| cec2017\nemenyi_cd_cec2017_D100.csv: n_blocks | PASS | n_blocks=['29'] |
| cec2017\wilcoxon_holm_cec2017_D100.csv: n_pairs<= 29 functions (zero-diffs discarded) | PASS | violations=0 |
| cec2017\wilcoxon_run_cec2017_D100.csv: rows = 29 functions x 6 comparators | PASS | 174 rows |
| cec2017\wilcoxon_run_cec2017_D100.csv: function set | PASS | 29 functions |
| cec2017\wilcoxon_run_cec2017_D100.csv: n_pairs=51 on ok rows | PASS | violations=0 |
| cec2017\wilcoxon_run_cec2017_D100_exploratory_bh.csv: rows = 29 functions x 6 comparators | PASS | 174 rows |
| cec2017\wilcoxon_run_cec2017_D100_exploratory_bh.csv: function set | PASS | 29 functions |
| cec2017\wilcoxon_run_cec2017_D100_exploratory_bh.csv: n_pairs=51 on ok rows | PASS | violations=0 |
| cec2017\effect_sizes_cec2017_D100.csv: rows = 29 x 6 | PASS | 174 rows |
| cec2017\effect_sizes_cec2017_D100.csv: n_runs=51 on ok rows | PASS | values=['51'] |
| cec2017\bca_ci_cec2017_D100.csv: rows = 29 x 6 | PASS | 174 rows |
| cec2017\bca_ci_cec2017_D100.csv: n_runs=51 on ok rows | PASS | values=['51'] |
| cec2017\convergence_checkpoints_cec2017_D100.csv: function set | PASS | 29 functions |
| cec2017\convergence_checkpoints_cec2017_D100.csv: n_runs=51 on ok rows | PASS | violations=0 of 2842 rows |
| cec2013\descriptive_stats_cec2013_D10.csv: function set | PASS | 28 functions (expected 28) |
| cec2013\descriptive_stats_cec2013_D10.csv: row count | PASS | 196 rows (expected 196) |
| cec2013\friedman_ranks_cec2013_D10.csv: n_blocks | PASS | n_blocks=['28'] (expected 28) |
| cec2013\nemenyi_cd_cec2013_D10.csv: n_blocks | PASS | n_blocks=['28'] |
| cec2013\wilcoxon_holm_cec2013_D10.csv: n_pairs<= 28 functions (zero-diffs discarded) | PASS | violations=0 |
| cec2013\wilcoxon_run_cec2013_D10.csv: rows = 28 functions x 6 comparators | PASS | 168 rows |
| cec2013\wilcoxon_run_cec2013_D10.csv: function set | PASS | 28 functions |
| cec2013\wilcoxon_run_cec2013_D10.csv: n_pairs=51 on ok rows | PASS | violations=0 |
| cec2013\effect_sizes_cec2013_D10.csv: rows = 28 x 6 | PASS | 168 rows |
| cec2013\effect_sizes_cec2013_D10.csv: n_runs=51 on ok rows | PASS | values=['51'] |
| cec2013\bca_ci_cec2013_D10.csv: rows = 28 x 6 | PASS | 168 rows |
| cec2013\bca_ci_cec2013_D10.csv: n_runs=51 on ok rows | PASS | values=['51'] |
| cec2013\descriptive_stats_cec2013_D30.csv: function set | PASS | 28 functions (expected 28) |
| cec2013\descriptive_stats_cec2013_D30.csv: row count | PASS | 196 rows (expected 196) |
| cec2013\friedman_ranks_cec2013_D30.csv: n_blocks | PASS | n_blocks=['28'] (expected 28) |
| cec2013\nemenyi_cd_cec2013_D30.csv: n_blocks | PASS | n_blocks=['28'] |
| cec2013\wilcoxon_holm_cec2013_D30.csv: n_pairs<= 28 functions (zero-diffs discarded) | PASS | violations=0 |
| cec2013\wilcoxon_run_cec2013_D30.csv: rows = 28 functions x 6 comparators | PASS | 168 rows |
| cec2013\wilcoxon_run_cec2013_D30.csv: function set | PASS | 28 functions |
| cec2013\wilcoxon_run_cec2013_D30.csv: n_pairs=51 on ok rows | PASS | violations=0 |
| cec2013\effect_sizes_cec2013_D30.csv: rows = 28 x 6 | PASS | 168 rows |
| cec2013\effect_sizes_cec2013_D30.csv: n_runs=51 on ok rows | PASS | values=['51'] |
| cec2013\bca_ci_cec2013_D30.csv: rows = 28 x 6 | PASS | 168 rows |
| cec2013\bca_ci_cec2013_D30.csv: n_runs=51 on ok rows | PASS | values=['51'] |
| cec2013\convergence_checkpoints_cec2013_D30.csv: function set | PASS | 28 functions |
| cec2013\convergence_checkpoints_cec2013_D30.csv: n_runs=51 on ok rows | PASS | violations=0 of 2744 rows |
| cec2013\descriptive_stats_cec2013_D50.csv: function set | PASS | 28 functions (expected 28) |
| cec2013\descriptive_stats_cec2013_D50.csv: row count | PASS | 196 rows (expected 196) |
| cec2013\friedman_ranks_cec2013_D50.csv: n_blocks | PASS | n_blocks=['28'] (expected 28) |
| cec2013\nemenyi_cd_cec2013_D50.csv: n_blocks | PASS | n_blocks=['28'] |
| cec2013\wilcoxon_holm_cec2013_D50.csv: n_pairs<= 28 functions (zero-diffs discarded) | PASS | violations=0 |
| cec2013\wilcoxon_run_cec2013_D50.csv: rows = 28 functions x 6 comparators | PASS | 168 rows |
| cec2013\wilcoxon_run_cec2013_D50.csv: function set | PASS | 28 functions |
| cec2013\wilcoxon_run_cec2013_D50.csv: n_pairs=51 on ok rows | PASS | violations=0 |
| cec2013\effect_sizes_cec2013_D50.csv: rows = 28 x 6 | PASS | 168 rows |
| cec2013\effect_sizes_cec2013_D50.csv: n_runs=51 on ok rows | PASS | values=['51'] |
| cec2013\bca_ci_cec2013_D50.csv: rows = 28 x 6 | PASS | 168 rows |
| cec2013\bca_ci_cec2013_D50.csv: n_runs=51 on ok rows | PASS | values=['51'] |
| cec2011\descriptive_stats_cec2011.csv: function set | PASS | 22 functions (expected 22) |
| cec2011\descriptive_stats_cec2011.csv: row count | PASS | 154 rows (expected 154) |
| cec2011\friedman_ranks_cec2011.csv: n_blocks | PASS | n_blocks=['22'] (expected 22) |
| cec2011\nemenyi_cd_cec2011.csv: n_blocks | PASS | n_blocks=['22'] |
| cec2011\wilcoxon_holm_cec2011.csv: n_pairs<= 22 functions (zero-diffs discarded) | PASS | violations=0 |
| cec2011\wilcoxon_run_cec2011.csv: rows = 22 functions x 6 comparators | PASS | 132 rows |
| cec2011\wilcoxon_run_cec2011.csv: function set | PASS | 22 functions |
| cec2011\wilcoxon_run_cec2011.csv: n_pairs=25 on ok rows | PASS | violations=0 |
| cec2011\effect_sizes_cec2011.csv: rows = 22 x 6 | PASS | 132 rows |
| cec2011\effect_sizes_cec2011.csv: n_runs=25 on ok rows | PASS | values=['25'] |
| cec2011\bca_ci_cec2011.csv: rows = 22 x 6 | PASS | 132 rows |
| cec2011\bca_ci_cec2011.csv: n_runs=25 on ok rows | PASS | values=['25'] |
| cec2011\convergence_checkpoints_cec2011.csv: function set | PASS | 22 functions |
| cec2011\convergence_checkpoints_cec2011.csv: n_runs=25 on ok rows | PASS | violations=0 of 2156 rows |
| cec2017\curve_selection_cec2017_D30.csv: function set = 29 cec2017 funcs | PASS | 29 functions |
| cec2017\curve_selection_cec2017_D100.csv: function set = 29 cec2017 funcs | PASS | 29 functions |

</details>

## Category 4 — Raw-to-summary reconstruction — **PASS (with 1 disclosed storage-precision exception, 0 substantive discrepancies)**

Protocol: 5 cells drawn with `numpy.random.default_rng(20240620)` from the population of (algorithm, suite, dimension, function) cells with per-run evidence (apgsk CEC2017 D10/D30/D50 excluded by the pre-registered disposition). For each cell, mean and SD were recomputed from the release `per_run.csv` (`error`; `best_fitness` for CEC2011) and compared to `descriptive_stats_*` at 1e-9 relative tolerance on the %.6e-rounded basis (the summary files store 6 significant decimals). SD ddof selected by best match and reported per cell (release summaries use ddof=1, sample SD, in all sampled cells).

| # | Cell | n | mean recomputed | mean reported | SD recomputed | SD reported | rel.err mean | rel.err SD | Result |
|---|---|---|---|---|---|---|---|---|---|
| 1 | apgsk cec2013 D10 F9 | 51 | 4.556558688e+00 | 4.556559000e+00 | 8.243355201e-01 | 8.243355000e-01 | 0.000e+00 | 0.000e+00 | PASS |
| 2 | atmals-gsk cec2017 D10 F26 | 51 | 3.000000000e+02 | 3.000000000e+02 | 0.000000000e+00 | 2.479051000e-13 | 0.000e+00 | 1.000e+00 | FAIL (strict) — explained, see below |
| 3 | dt-gsk cec2013 D10 F5 | 51 | 0.000000000e+00 | 0.000000000e+00 | 0.000000000e+00 | 0.000000000e+00 | 0.000e+00 | 0.000e+00 | PASS |
| 4 | dt-gsk cec2017 D30 F17 | 51 | 4.929638193e+01 | 4.929638000e+01 | 2.907333942e+01 | 2.907334000e+01 | 0.000e+00 | 0.000e+00 | PASS |
| 5 | apgsk cec2013 D30 F3 | 51 | 7.014264764e+06 | 7.014265000e+06 | 1.370829035e+07 | 1.370829000e+07 | 0.000e+00 | 0.000e+00 | PASS |

**Explained exception (cell 2, atmals-gsk cec2017 D10 F26):** the mean matches exactly (3.000000e+02). The reported SD (2.479051e-13) lies below the 11-significant-digit storage resolution of `per_run.csv` at |mean| = 3.0e+02 — all 51 stored error values are textually identical (`3.0000000000e+02`), so the recomputed SD is 0. The absolute discrepancy is 2.479e-13, i.e. 8.3e-16 relative to the mean (machine-epsilon scale). This is a storage-precision property of the release files themselves (summary computed from full-precision in-memory values before per-run serialization), not a Phase 6 defect and not a data-integrity failure. The strict-tolerance verdict for the cell is recorded as FAIL and disclosed here; the mean check passes.

### Supplementary census (beyond the 5-cell mandate)

To bound the finding, ALL 1467 cells with per-run evidence were reconstructed (mean + SD, ddof=1, %.6e-rounded basis):

- **1435 / 1467 cells pass at 1e-9 relative** on both mean and SD.
- **32 cells** show last-digit discrepancies, every one bounded by the release files' own storage/rounding granularity (max scaled discrepancy 2.7e-07 relative to the cell's largest per-run magnitude; the release summary CSVs' Worst column shows 6-significant-digit rounding, e.g. apgsk cec2013 D50 F11 Worst `1.1702600000E-08` vs per_run `1.1702582015e-08` — the mean discrepancy in that cell is exactly that rounding difference / 51). All are below the %.6e reporting precision of every Phase 6 output.
- **0 substantive discrepancies.**

<details><summary>The 32 storage-precision-bounded cells (click to expand)</summary>

- gsk cec2017 D10 F26: mean 3.000000e+02 vs 3.000000e+02, sd 0.000000e+00 vs 2.287903e-13, scaled discrepancy 7.6e-16
- gsk cec2017 D10 F28: mean 3.000000e+02 vs 3.000000e+02, sd 0.000000e+00 vs 1.399318e-13, scaled discrepancy 4.7e-16
- gsk cec2017 D30 F22: mean 1.000000e+02 vs 1.000000e+02, sd 0.000000e+00 vs 2.541797e-13, scaled discrepancy 2.5e-15
- atmals-gsk cec2017 D10 F26: mean 3.000000e+02 vs 3.000000e+02, sd 0.000000e+00 vs 2.479051e-13, scaled discrepancy 8.3e-16
- atmals-gsk cec2017 D30 F22: mean 1.000000e+02 vs 1.000000e+02, sd 0.000000e+00 vs 4.916052e-13, scaled discrepancy 4.9e-15
- egsk cec2017 D10 F26: mean 3.000000e+02 vs 3.000000e+02, sd 0.000000e+00 vs 1.750187e-13, scaled discrepancy 5.8e-16
- egsk cec2017 D30 F22: mean 1.000000e+02 vs 1.000000e+02, sd 0.000000e+00 vs 6.091337e-13, scaled discrepancy 6.1e-15
- dt-gsk cec2017 D30 F22: mean 1.000000e+02 vs 1.000000e+02, sd 0.000000e+00 vs 6.431601e-13, scaled discrepancy 6.4e-15
- gsk cec2013 D10 F28: mean 3.000000e+02 vs 3.000000e+02, sd 0.000000e+00 vs 1.189645e-13, scaled discrepancy 4.0e-16
- gsk cec2013 D30 F28: mean 3.000000e+02 vs 3.000000e+02, sd 0.000000e+00 vs 2.275157e-13, scaled discrepancy 7.6e-16
- agsk cec2013 D30 F17: mean 3.043375e+01 vs 3.043375e+01, sd 3.384624e-06 vs 3.384259e-06, scaled discrepancy 4.5e-08
- agsk cec2013 D30 F26: mean 2.000163e+02 vs 2.000163e+02, sd 8.157996e-03 vs 8.157997e-03, scaled discrepancy 1.4e-07
- agsk cec2013 D30 F28: mean 3.000000e+02 vs 3.000000e+02, sd 0.000000e+00 vs 3.145450e-13, scaled discrepancy 1.0e-15
- agsk cec2013 D50 F28: mean 4.000000e+02 vs 4.000000e+02, sd 0.000000e+00 vs 4.590612e-13, scaled discrepancy 1.1e-15
- apgsk cec2013 D30 F28: mean 3.000000e+02 vs 3.000000e+02, sd 0.000000e+00 vs 1.771801e-12, scaled discrepancy 5.9e-15
- apgsk cec2013 D50 F11: mean 2.294624e-10 vs 2.294627e-10, sd 1.638689e-09 vs 1.638692e-09, scaled discrepancy 2.3e-07
- apgsk cec2013 D50 F28: mean 4.000000e+02 vs 4.000000e+02, sd 0.000000e+00 vs 8.841705e-12, scaled discrepancy 2.2e-14
- fdb-agsk cec2013 D30 F28: mean 3.000000e+02 vs 3.000000e+02, sd 0.000000e+00 vs 3.090526e-13, scaled discrepancy 1.0e-15
- fdb-agsk cec2013 D50 F26: mean 2.002111e+02 vs 2.002111e+02, sd 9.286598e-02 vs 9.286597e-02, scaled discrepancy 2.0e-07
- fdb-agsk cec2013 D50 F28: mean 4.000000e+02 vs 4.000000e+02, sd 0.000000e+00 vs 3.344596e-13, scaled discrepancy 8.4e-16
- atmals-gsk cec2013 D30 F28: mean 3.000000e+02 vs 3.000000e+02, sd 0.000000e+00 vs 3.337827e-13, scaled discrepancy 1.1e-15
- egsk cec2013 D50 F28: mean 4.000000e+02 vs 4.000000e+02, sd 3.040253e-08 vs 3.048865e-08, scaled discrepancy 1.5e-11
- gsk cec2011 F3: mean 1.151489e-05 vs 1.151489e-05, sd 1.728999e-21 vs 1.403819e-19, scaled discrepancy 5.1e-08
- agsk cec2011 F3: mean 1.151489e-05 vs 1.151489e-05, sd 1.728999e-21 vs 1.557194e-19, scaled discrepancy 5.1e-08
- agsk cec2011 F13: mean 1.544431e+04 vs 1.544431e+04, sd 2.275840e-01 vs 2.275841e-01, scaled discrepancy 2.7e-07
- apgsk cec2011 F3: mean 1.151489e-05 vs 1.151489e-05, sd 1.728999e-21 vs 1.927665e-19, scaled discrepancy 5.1e-08
- fdb-agsk cec2011 F3: mean 1.151489e-05 vs 1.151489e-05, sd 1.728999e-21 vs 1.491343e-19, scaled discrepancy 5.1e-08
- fdb-agsk cec2011 F13: mean 1.544474e+04 vs 1.544474e+04, sd 6.390487e-01 vs 6.390485e-01, scaled discrepancy 3.6e-08
- atmals-gsk cec2011 F3: mean 1.151489e-05 vs 1.151489e-05, sd 1.728999e-21 vs 1.195147e-19, scaled discrepancy 5.1e-08
- atmals-gsk cec2011 F13: mean 1.544419e+04 vs 1.544419e+04, sd 6.002341e-05 vs 6.012590e-05, scaled discrepancy 2.3e-07
- egsk cec2011 F3: mean 1.151489e-05 vs 1.151489e-05, sd 1.728999e-21 vs 1.408000e-19, scaled discrepancy 5.1e-08
- dt-gsk cec2011 F3: mean 1.151489e-05 vs 1.151489e-05, sd 1.728999e-21 vs 1.023490e-18, scaled discrepancy 5.1e-08

</details>

## Deviations

None. No confirmatory amendment is required by this audit. Two observations recorded for completeness (neither is a deviation): (i) the bundle contains the pre-registered-exception filenames `primary_stats/statistical_results.csv` and `cec2017/headline_bca.csv` (both plan-mandated, verified above); (ii) the release-internal per_run-vs-summary last-digit rounding described in Category 4 is a property of release rel-2026-07-10-262fc16c9 itself, predating Phase 6, and does not affect any reported number at %.6e precision or any rank-based statistic.
