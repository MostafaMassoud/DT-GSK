# convergence_checkpoints — output schema (Phase 5 pre-registration)

**Filename pattern:** `convergence_checkpoints_<suite>_D<dim>.csv`; cec2011: `convergence_checkpoints_cec2011.csv` (all 22 problems, native dims); cec2013 grids D30 only per P4.

**One row per (function, algorithm, checkpoint).** P2 aggregation: per-checkpoint MEAN error across all runs (51; 25 for cec2011), computed from `gen_logs/CheckpointErrors_<alg>_F<f>_D<d>.csv` (columns `Run,Seed,E<nfes>...`); identical basis for all 7 curves; no smoothing, no extrapolation past termination; raw values only — any log-scale display floor is applied at render time (Phase 7) and disclosed there, never stored here.

| column | type | notes |
|---|---|---|
| suite | str | |
| dimension | int | native dim for cec2011 |
| function | int | |
| algorithm | str | P1 order |
| checkpoint_nfes | int | from the `E<nfes>` column header of the source log |
| mean_error | float `%.6e` | mean across runs at this checkpoint |
| n_runs | int | runs aggregated (must equal 51/25; shortfall => `availability` flag, disclosed) |
| availability | str | `ok` / `disclosed-missing` (absent algorithm logs per P2 — logged, never fabricated/interpolated) |

**Sort order:** function asc, algorithm in P1 order, checkpoint_nfes asc.
**Precision:** floats `%.6e`; missing = literal `n/a`.
