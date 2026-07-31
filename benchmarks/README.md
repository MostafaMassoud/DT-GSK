# Benchmarks

All CEC-related artifacts live here.

```text
cec_reference_results/  frozen reference panel: per-optimizer summaries, per-run
                        tables, convergence curves, gen_logs, and provenance files
cec_suite_python/       Python/Numba CEC benchmark evaluators used by run.py
```

Do not place CEC input files or CEC benchmark source under the root `data`
folder, under `src`, or under `src/benchmark/cec*`. Python runtime evaluators
and packaged CEC data live in `benchmarks/cec_suite_python`.

Do not add Python code, Python wrappers, or generated Cython bindings under
`benchmarks`.

## Reference panel (`cec_reference_results`)

`cec_reference_results` is the **single source of truth for all paper data and
statistics**: analysis and figure/table generation load it first, and locally
reproduced `../results/_run_all/` output is only a fallback for cells the
reference tree does not carry (see
`src/gsk_family/analysis/result_loader.py::load_algorithm`).

Layout is flat per optimizer — `cec_reference_results/<suite>/<optimizer>/`
directly contains:

```text
<opt>_<suite>_D<dim>.csv   per-dimension summary tables
<opt>_cec2011.csv          rollup (CEC2011 only)
per_run.csv                per-run final values
environment.json           run environment + FP-regime sentinel
run_config.json            resolved experiment config
seed_schedule.csv          deterministic seed schedule
verification.json          verification record
phase0_protocol.json       protocol snapshot
curves/                    per-run convergence CSVs (Figure_F<f>_D<d>_Run#<r>.csv)
gen_logs/                  checkpoint tables (CheckpointErrors_<opt>_F<f>_D<d>.csv)
```

Coverage: the **full 7-optimizer panel** (`gsk`, `agsk`, `apgsk`, `fdb-agsk`,
`atmals-gsk`, `egsk`, `dt-gsk`) exists for **cec2017, cec2011, and cec2013**.


The tree holds CSV/JSON data only: rendered convergence PNGs and `*_log_*.txt`
run logs were deleted because they are regenerable from `curves/` and
`gen_logs/` (e.g. via `scripts/plot_convergence_from_curves.py` and the
`papers/scripts/generate_*_convergence.py` figure scripts).

Treat everything under `cec_reference_results` as **read-only**. Fresh runs go
under `../results`; a run enters the reference archive only through an explicit
curation step with documented provenance.

## Researcher mental model

| Folder | Contains | Mutability |
|---|---|---|
| `cec_suite_python/<suite>` | Python/Numba benchmark evaluator package | Runtime evaluator used by the optimizer runner. |
| `cec_reference_results` | Frozen per-optimizer reference panel: summary tables, `per_run.csv`, provenance files, `curves/`, `gen_logs/` | Read-only single source of truth for paper data, comparison, verification, and convergence-graph generation. |
| `../results` | Generated experiment outputs | Append/resume only; do not use as input reference data. |

Example: if `run_all_cec2017` reports a result discrepancy, first inspect
`../results/<optimizer>/cec2017/summary/environment.json` and
`seed_schedule.csv`. Do not edit `cec_reference_results` to make the comparison
look better; its aggregate tables and curated convergence assets are the
baseline evidence being tested against. Fresh run outputs still belong under
`../results`, not under `benchmarks`, unless a future curation step explicitly
promotes them into the reference archive with documented provenance.
