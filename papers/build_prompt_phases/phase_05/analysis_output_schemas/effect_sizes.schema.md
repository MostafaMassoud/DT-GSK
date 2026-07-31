# effect_sizes — output schema (Phase 5 pre-registration)

**Filename pattern:** `effect_sizes_<suite>_D<dim>.csv`; cec2011: `effect_sizes_cec2011.csv`.

**One row per (function, comparator).** Run-level paired samples only (51/25 runs; dt-gsk vs comparator) [vargha2000critique]. Never pooled across functions. cec2011 uses `best_fitness` (A2-017).

| column | type | notes |
|---|---|---|
| suite | str | |
| dimension | int | native dim for cec2011 |
| function | int | |
| comparator | str | P1 order |
| n_runs | int | |
| a12 | float `%.6e` | Vargha–Delaney A12 (P(dt-gsk < comparator) orientation stated in file comment line) |
| cliffs_delta | float `%.6e` | = 2*a12 - 1 |
| magnitude | str | `negligible/small/medium/large` per vargha2000critique thresholds |
| availability | str | `ok` / `disclosed-unavailable` (apgsk cec2017 D10/D30/D50 — no function-level substitute for effect sizes) |

**Sort order:** function asc, comparator in P1 order.
**Precision:** floats `%.6e`; unavailable cells literal `n/a` (rows kept).
