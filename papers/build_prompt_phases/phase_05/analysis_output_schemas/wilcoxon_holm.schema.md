# wilcoxon_holm / wilcoxon_run — output schema (Phase 5 pre-registration)

**Filename patterns (per `strict_source_execution.md` Sec. 5):**
- Across-function function-level tests (family `wilcoxon_holm`): `wilcoxon_holm_<suite>_D<dim>.csv`; cec2011: `wilcoxon_holm_cec2011.csv`.
- Per-function run-level tests (family `wilcoxon_run`): `wilcoxon_run_<suite>_D<dim>.csv`; cec2011: `wilcoxon_run_cec2011.csv`.
- Exploratory duplicate (separately labeled, BH-adjusted, never mixed into primary) of the **run-level** files only: `wilcoxon_run_<suite>_D<dim>_exploratory_bh.csv` with identical columns except `p_holm` -> `p_bh` [benjamini1995controlling].

**Rows:** `wilcoxon_run` files carry the per-function run-level tests (`test_level=per_function_runlevel`, one row per function x comparator; paired by run per seed_and_pairing_audit.md); `wilcoxon_holm` files carry the across-function function-level tests (`test_level=across_functions_funclevel`, one row per comparator, `function=0`, on per-function means — the GSK-family convention) [wilcoxon1945individual; holm1979simple]. Identical column set for both families. Proposed side is always `dt-gsk`.

| column | type | notes |
|---|---|---|
| suite | str | |
| dimension | int | |
| function | int | `0` for the across-function row |
| comparator | str | P1 order; dt-gsk vs comparator |
| test_level | str | `per_function_runlevel` / `across_functions_funclevel` |
| n_pairs | int | 51/25 runs, or #functions for funclevel; `n/a` if unavailable |
| statistic | float `%.6e` | Wilcoxon signed-rank W |
| p_raw | float `%.6e` | |
| p_holm | float `%.6e` | Holm within family = (suite, dimension, comparator set, test_level) |
| outcome | str | `win`/`tie`/`loss` from dt-gsk's perspective at alpha=0.05 after Holm; `n/a` when unavailable |
| availability | str | `ok` or `disclosed-unavailable` (apgsk cec2017 D10/D30/D50 run-level rows; see source_resolution_map.csv) |

**Sort order:** function asc (`wilcoxon_holm` files carry only the `function=0` across-function rows), then comparator in P1 order, then test_level.
**Precision:** floats `%.6e`; unavailable cells literal `n/a` (rows kept, never dropped).
