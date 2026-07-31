# Robustness summary - cec2017 (Phase 6 bound values)

| Check | Suite | Variant compared | Primary conclusion element | Verdict |
|---|---|---|---|---|
| r01_mean_vs_median | cec2017 | median re-ranking | ordinal rank positions + W/T/L (C-a) | diverge |
| r02_floor_sensitivity | cec2017 | branch B (B1 vs B2) | ranks + W/T/L at the protocol floor | agree |
| r03_lofo_friedman | cec2017 | 29 LOFO replicates per dimension | DT-GSK ordinal position (C-a) | agree |
| r04_disputed_cell_exclusion | cec2017 | apgsk V1/V2 + eGSK exclusion | descriptive rank aggregates (C-a) | diverge |
| r05_unpaired_companion | cec2017 | unpaired Mann-Whitney U | per-function Holm decision triples (C-b) | agree |
| r06_holm_vs_bh | cec2017 | Benjamini-Hochberg q=0.05 (AN-EXP-BH-2017) | decision counts per (dim, comparator) | n/a (exploratory) |
| r07_secondary_suite_effect | cec2017 | with vs without secondary suites | qualitative cross-suite ordering of DT-GSK | qualitatively-consistent |
| r08_overall_aggregation_variants | cec2017 | pooled block-Friedman | overall ordinal positions (C-a) | agree |
