# bca_ci — output schema (Phase 5 pre-registration)

**Filename pattern:** `bca_ci_<suite>_D<dim>.csv`; cec2011: `bca_ci_cec2011.csv`.

**One row per (function, comparator):** BCa 95% CI of the paired mean difference (dt-gsk error minus comparator error; `best_fitness` for cec2011) over runs [efron1993introduction]. Deterministic bootstrap: `B=10000`, RNG = `default_rng(SeedSequence([20240620, <suite_ordinal>, <dimension>, <function>, <comparator_P1_index>]))` (strict_source_execution.md Sec. 5).

| column | type | notes |
|---|---|---|
| suite | str | |
| dimension | int | |
| function | int | |
| comparator | str | P1 order |
| n_runs | int | |
| mean_diff | float `%.6e` | paired mean difference (negative favors dt-gsk) |
| ci_low | float `%.6e` | BCa 2.5% |
| ci_high | float `%.6e` | BCa 97.5% |
| B | int | 10000 |
| seed_scheme | str | fixed literal `SS[20240620,suite,dim,func,cmpP1]` |
| availability | str | `ok` / `disclosed-unavailable` (apgsk cec2017 D10/D30/D50) |

**Sort order:** function asc, comparator in P1 order.
**Precision:** floats `%.6e`; unavailable cells literal `n/a` (rows kept).
