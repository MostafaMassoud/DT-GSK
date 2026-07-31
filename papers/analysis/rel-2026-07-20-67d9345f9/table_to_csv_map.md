# Exhibit -> authoritative CSV map (Phase 6, release rel-2026-07-20-67d9345f9)

| Planned exhibit | Authoritative machine-readable source |
|---|---|
| T01-SUM / T01-D10..D100 | cec2017/descriptive_stats_cec2017_D{10,30,50,100}.csv (+ W/T/L rows in primary_stats/statistical_results.csv, AN-DESC-2017-*) |
| T02 / T02-FULL-D10..D100 | cec2017/wilcoxon_holm_cec2017_D{10,30,50,100}.csv + cec2017/wilcoxon_run_cec2017_D{10,30,50,100}.csv |
| T03 / T03-FULL-D10..D100 | cec2017/effect_sizes_cec2017_D{10,30,50,100}.csv |
| T-BCA | cec2017/bca_ci_cec2017_D{10,30,50,100}.csv + cec2017/headline_bca.csv |
| T05 | cec2017/friedman_ranks_cec2017_D{10,30,50,100}.csv + cec2017/friedman_ranks_cec2017_overall.csv |
| F01-D10..D100 | cec2017/friedman_ranks_cec2017_D*.csv + cec2017/nemenyi_cd_cec2017_D*.csv (emitted only when omnibus significant) |
| F02-MAIN-D30/D100 | papers/build_prompt_phases/phase_05/curve_selection.csv + cec2017/curve_selection_cec2017_D{30,100}.csv + cec2017/convergence_checkpoints_cec2017_D{30,100}.csv |
| F02-SUP-CEC2017-D10..D100 | cec2017/convergence_checkpoints_cec2017_D*.csv |
| F02-SUP-CEC2011 | cec2011/convergence_checkpoints_cec2011.csv |
| F02-SUP-CEC2013-D30 | cec2013/convergence_checkpoints_cec2013_D30.csv |
| F03 | cec2017/rank_trend_cec2017.csv |
| F05-RANKBAR | cec2017/friedman_ranks_cec2017_D*.csv |
| T04 / F04-CEC2011 | cec2011/descriptive_stats_cec2011.csv + cec2011/friedman_ranks_cec2011.csv |
| T04-STATS | cec2011/wilcoxon_holm_cec2011.csv + cec2011/wilcoxon_run_cec2011.csv + cec2011/effect_sizes_cec2011.csv + cec2011/bca_ci_cec2011.csv |
| T06 / T06-FULL-D10..D50 | cec2013/friedman_ranks_cec2013_D{10,30,50}.csv + cec2013/friedman_ranks_cec2013_overall.csv + cec2013/descriptive_stats_cec2013_D{10,30,50}.csv |
| T-RUNTIME | cec2017/cost_cec2017.csv (comparability-qualified) |
| T-SENS | disclosed-unavailable (EG-006; evidence-gap row in primary_stats/statistical_results.csv) |
| F-TRACE / F-ADAPT | gated: no GenLog_* diagnostic release exists (source_resolution_map.csv); disclosed-unavailable |
| X-ABL-01..03 | DEFERRED_TO_PHASE_12_SUPPLEMENT_ONLY; results/_ablation quarantined; NOT computed in Phase 6 |
| AN-CLASS-2017 | cec2017/class_ranks_cec2017.csv (exploratory) |
| AN-ROB-2017-01..08 | cec2017/robustness/robustness_cec2017_r0{1..8}_*.csv |
| AN-EXP-BH-2017 | cec2017/wilcoxon_run_cec2017_D*_exploratory_bh.csv |
| T1-T16 legacy staging | results/paper_tables/T{1..16}.csv (exported from this bundle; provenance.json alongside) |
