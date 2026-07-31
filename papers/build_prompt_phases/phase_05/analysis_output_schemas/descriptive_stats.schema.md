# descriptive_stats — output schema (Phase 5 pre-registration)

**Filename pattern:** `descriptive_stats_<suite>_D<dim>.csv`; cec2011: `descriptive_stats_cec2011.csv`.

**One row per (function, algorithm)** — transcription of the release per-function summary CSVs (`<alg>_<suite>_D<dim>.csv` / `<alg>_cec2011.csv`), normalized through `load_summary_csv()` (schema variants A/B/C auto-detected). No recomputation from runs; this family is the single descriptive source for T01-*/T04/T06-* exhibits.

| column | type | notes |
|---|---|---|
| suite | str | |
| dimension | int | native dim for cec2011 |
| function | int | cec2017 excludes F2 (protocol); cec2013 has no exclusion |
| algorithm | str | P1 order |
| best | float `%.6e` | |
| median | float `%.6e` | |
| mean | float `%.6e` | |
| worst | float `%.6e` | |
| sd | float `%.6e` | |
| source_path | str | release-relative path of the summary CSV read |

**Sort order:** function asc, algorithm in P1 order (`gsk, agsk, apgsk, fdb-agsk, atmals-gsk, egsk, dt-gsk`).
**Precision:** floats `%.6e`; missing stats literal `n/a` (never fabricated).
