# Analysis Package

The analysis package contains post-run helpers. It does not execute optimizers.

## Files

| File | Purpose |
|---|---|
| `statistics.py` | Summary and rank statistics over loaded results. |
| `statistical_tests.py` | Friedman, Wilcoxon, Holm, and Nemenyi significance tests. |
| `result_loader.py` | Load per-run and summary result tables into memory, reference first (see below). |
| `project_policy.py` | Suite/dimension/function-exclusion policy for the family report. |
| `family_report.py` | Assemble the cross-optimizer GSK-family comparison report. |
| `figures.py` | Render analysis PNG figures. |
| `latex_tables.py` | Emit LaTeX comparison tables. |

## Loading policy: reference first

`result_loader.load_algorithm` (used by `family_report.py`) resolves each
`(algorithm, suite, dimension)` cell against the committed reference panel
`benchmarks/cec_reference_results/` **first** — for every algorithm, the
proposed method included. Locally reproduced output under `results/_run_all/`
is only a fallback for cells the reference tree does not carry. Every loaded
result carries a provenance tag (`imported_reference`, `reproduced_locally`,
`derived_summary`, or `unavailable`).

Use runner verification for machine-readable validation and these analysis
helpers for research reports or notebooks.

