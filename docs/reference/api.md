# API Reference

> **What this is.** A map of the public Python API: the importable types,
> functions, and console commands you can call directly from your own code.
> **Who it is for.** Anyone scripting the package, writing tests, or building on
> top of the optimizers and runner. **Prerequisites.** A working install (see
> the [user guide](../getting-started/user_guide.md)) and the vocabulary in
> [the glossary](glossary.md). **After reading** you will know which module each
> symbol lives in and have a runnable snippet for every major area.

This documents the active Python API. Every symbol below is importable from
Python. Normal execution uses the Python/Numba benchmark evaluator through
`BenchmarkProblem.evaluate`, not through optimizer imports.

How to read the tables: each row is `symbol` — one-line purpose. Import paths
are the module headings above each group. For deeper, task-oriented usage see
the [Python optimizer interface](python_optimizer_interface.md) and
[workflows](workflows.md).

## Public Data Types

These dataclasses are the shared contracts that flow between the benchmark
adapter, the optimizers, and the result writers. They live in
`gsk_family.types`.

| Symbol | Purpose |
| --- | --- |
| `OptimizerOptions` | Input options for one optimizer run: `seed`, RNG label, optional fair-start population, optional restored RNG state, and optimizer-specific `values`. |
| `ConvergenceTrace` | Two parallel arrays: evaluation counts (`nfes`) and best-so-far objective values (`best_fitness`). |
| `OptimizerResult` | Canonical optimizer return object (best point, error, evaluation count, convergence trace, timing, resolved parameters). |
| `RunRecord` | One normalized per-run row, consumed by the result writers that emit `per_run.csv`. |

The shape contract for evaluation lives in `gsk_family.benchmark_adapter.problem`:

| Symbol | Purpose |
| --- | --- |
| `BenchmarkProblem` | Frozen problem object: suite, function id, dimension, bounds, optimum, budget, statistics basis, and a vectorized `evaluate`. |
| `as_population` | Validate a candidate array is 2-D, finite, `float64`, and shaped `(n_candidates, dim)`. |
| `as_fitness_vector` | Validate an evaluator return value is a 1-D vector with one entry per candidate. |

```python
from gsk_family.types import OptimizerOptions

# A minimal options object: seed is the only required field.
options = OptimizerOptions(seed=20240620, rand_generator="threefry")
```

Field note: `OptimizerOptions.rand_generator` defaults to `"twister"` on the
dataclass itself, but the runner passes `"threefry"` (its own default) on every
campaign. See [seed_policy.md](seed_policy.md) for what these labels select.

## Benchmark API

Build and describe benchmark problems without importing any CEC module directly.

`gsk_family.benchmark_adapter.factory`

| Symbol | Purpose |
| --- | --- |
| `make_problem(suite, func_id, dim=None, max_nfes_override=0)` | Construct a validated `BenchmarkProblem`. `max_nfes_override` of `0`/`None` keeps the suite default budget. |

`gsk_family.benchmark_adapter.protocol`

| Symbol | Purpose |
| --- | --- |
| `suite_protocol(suite)` | Return the `SuiteProtocol` metadata record for a suite. |
| `default_function_ids(suite)` | Functions run by default (CEC2017 omits F2). |
| `all_function_ids(suite)` | Every implemented function id for the suite. |
| `default_dimensions(suite)` | Default dimensions, or the string `"native"` for per-function dimensions. |
| `validate_function_id(suite, func_id)` | Validate and normalize a function id. |
| `validate_dimension(suite, dim, valid)` | Validate a fixed-dimension suite dimension against an allowed tuple. |

```python
from gsk_family.benchmark_adapter.factory import make_problem

problem = make_problem("cec2017", 1, dim=10)   # full default budget (10000 * D)
fitness = problem.evaluate(problem.lb.reshape(1, -1))  # one candidate at the lower bound
print(problem.max_nfes, problem.statistics_basis)      # 100000 error_vs_optimum
```

The full list of suites, function ranges, dimensions, and budgets is in
[benchmark_protocol.md](benchmark_protocol.md).

## Optimizer API

Each optimizer module exposes a single entry point with the same signature:

```python
optimize(problem: BenchmarkProblem, options: OptimizerOptions | dict) -> OptimizerResult
```

Optimizer modules (the canonical ids are in `gsk_family.optimizers.OPTIMIZER_IDS`):

- `gsk_family.optimizers.gsk`
- `gsk_family.optimizers.agsk`
- `gsk_family.optimizers.apgsk`
- `gsk_family.optimizers.atmals_gsk`
- `gsk_family.optimizers.fdb_agsk`
- `gsk_family.optimizers.egsk`
- `gsk_family.optimizers.dt_gsk`

Internal helper modules (used by the optimizers; not called directly to run one):

- `gsk_family.optimizers._kernels` — shared Numba-compiled per-generation trial kernel (`gsk_build_trial`); imported by every optimizer except `dt_gsk`, and reproduces the NumPy path bit-for-bit (no `fastmath`).
- `gsk_family.optimizers.fdb_scores` — Fitness-Distance-Balance score helpers.
- `gsk_family.optimizers.atmals_helpers` — ATMALS memory and local-search helpers.
- `gsk_family.optimizers._dt_profiles` — DT-GSK dimension-tier `pub` config builder.
- `gsk_family.optimizers._dt_rng` — DT-GSK named-substream RNG layer.
- `gsk_family.optimizers._dt_core` — DT-GSK core driver (`DTGSKConfig`, `dt_gsk_optimize`).
- `gsk_family.optimizers._dt_subsystems` — DT-GSK subsystems package (vendored byte-for-byte).

```python
from gsk_family.optimizers.gsk import optimize
from gsk_family.types import OptimizerOptions

result = optimize(problem, OptimizerOptions(seed=20240620, rand_generator="threefry"))
print(result.best_fitness, result.error, result.nfes, result.termination)
```

Per-optimizer option keys (for example `fdb_case`, `protocol`, `np_init`)
and dictionary-style calls are documented in
[python_optimizer_interface.md](python_optimizer_interface.md). The mathematics
of each optimizer is in the [algorithm guides](../algorithms/gsk.md).

## Runner API

The runner expands a campaign into cells, fixes the seed schedule, runs every
cell, and writes the result tree. Use it whenever artifacts, fair starts,
summaries, or validation matter.

`gsk_family.runners.config`

| Symbol | Purpose |
| --- | --- |
| `ExperimentConfig` | Frozen, fully normalized campaign request (optimizers, suite, functions, dimensions, runs, seeds, parallel settings, output roots, optimizer options). |
| `config_from_mapping(mapping)` | Validate a YAML-like mapping into an `ExperimentConfig`; rejects unknown keys. |
| `load_config(path)` | Read a YAML file into an `ExperimentConfig`. |

`gsk_family.runners.run_experiment`

| Symbol | Purpose |
| --- | --- |
| `run_experiment(config=None, **kwargs)` | Execute a campaign and return an `ExperimentRunSummary`. Accepts an `ExperimentConfig`, a mapping, or bare keyword arguments. |
| `ExperimentRunSummary` | Result object with fields `output_dirs`, `records`, `skipped_cells`, `skipped_completed`, and `runtime_seconds_total`. |
| `OPTIMIZER_FUNCTIONS` | Mapping from optimizer id to its `optimize` function; a new optimizer is registered here. |

```python
from gsk_family.runners.run_experiment import run_experiment

# A small, self-contained smoke campaign. Defaults: process backend,
# conservative automatic workers, unified seed policy.
summary = run_experiment(
    optimizers="gsk",
    suite="sphere",
    functions=[1],
    dimensions=[4],
    runs=2,
    max_evaluations=500,
)
print(summary.output_dirs[0])          # results/_run_all/gsk/sphere
print(len(summary.records))            # 2 completed RunRecords
```

`gsk_family.runners.seed_policy`

| Symbol | Purpose |
| --- | --- |
| `make_seed_schedule` | Build a deterministic list of `SeedScheduleRow` for the requested cells. |
| `verify_unified_seed_schedule` | Audit that every optimizer shares identical seeds for matching `(dim, function, run)` cells. |
| `seed_for_run` | Normalize a policy and derive the single integer seed for one run. |

`gsk_family.runners.output`

| Symbol | Purpose |
| --- | --- |
| `ensure_output_dirs` | Create the `summary/`, `curves/`, `curves/graphs/`, `gen_logs/` tree and return the paths. |
| `write_per_run` | Write `per_run.csv`. |
| `write_summary_tables` | Write the per-dimension CEC-style summary CSVs. |
| `write_curves_and_logs` | Write the median-run convergence curve, optional checkpoint logs, and optional best-effort PNG. |
| `write_environment` | Write `environment.json`, preserving the caller's key order. |
| `write_profile` | Write the optional `profile.json` timing metadata. |

`gsk_family.runners.verification`

| Symbol | Purpose |
| --- | --- |
| `verify_run_directory` | Compare a run directory to references and write `verification.json`. |
| `compare_generated_to_references` | Return a `VerificationResult` without writing a file. |
| `write_verification_json` | Serialize a `VerificationResult` to disk. |

The exact files these writers emit, and an annotated sample of each, are in
[result_schema.md](result_schema.md).

## Statistics API

Summary statistics and error formatting. These define the numbers that land in
the summary tables.

`gsk_family.stats`

| Symbol | Purpose |
| --- | --- |
| `sample_sd` | Sample standard deviation (`ddof=1`); returns `0.0` for fewer than two values. |
| `summarize` | Return best, median, mean, worst, and sample SD as a `SummaryStatistics` record. |
| `compute_error` | Target-zeroed error against a known optimum; returns `0.0` once error drops below `target_error`, and `NaN` when the optimum is `NaN`. |
| `statistic_values` | Map best-fitness values to error or raw-objective values per the suite's statistics basis. |
| `format_scientific` | Format a float for CSV output; default precision is 10 (`%.10E`), with `NaN`/`Inf`/`-Inf` spelled out. |

```python
import numpy as np
from gsk_family.stats import summarize, format_scientific

stats = summarize(np.array([1.0e-3, 4.0e-3, 2.0e-3]))
print(stats.mean, stats.sd)                 # 0.0023333... 1.5275...e-03
print(format_scientific(stats.mean))        # 2.3333333333E-03
```

The standard-deviation convention (sample, `ddof=1`) is used everywhere a
summary SD is reported. See the worked statistics example in
[research/numerical_examples.md](../research/numerical_examples.md).

## Statistical Analysis Package

`gsk_family.stats` (above) produces the per-run summary numbers. The separate
`gsk_family.analysis` package consumes finished summaries and builds the
paper-grade cross-optimizer comparison: a 7-algorithm GSK-family panel of the
six reference comparators (`gsk`, `agsk`, `apgsk`, `fdb-agsk`, `egsk`,
`atmals-gsk`) plus the proposed `dt-gsk`. Per-function mean errors for every
panel member — the proposed included — are loaded **reference-first** from the
committed tables under `benchmarks/cec_reference_results/<suite>/` (the paper's
single source of truth); a locally reproduced run under
`results/_run_all/<opt>/<suite>/summary/` is only a fallback for cells the
reference tree does not carry (`analysis.result_loader.load_algorithm`).

`gsk_family.analysis.family_report` — the orchestrator the `gsk-stats` CLI calls.

| Symbol | Purpose |
| --- | --- |
| `generate_family_report(suite, dims, out_dir, ...)` | End-to-end driver: load summaries, run the tests, write CSV/LaTeX/PNG artifacts; returns `(dim_results, written_paths)`. |
| `analyze_family(...)` | Build the per-dimension `DimResult` records (mean ranks, Wilcoxon rows, effect sizes) without writing files. |
| `write_report(...)` | Serialize a completed analysis to the output tree. |
| `DEFAULT_PROPOSED` | The proposed optimizer id anchoring every comparison (`"dt-gsk"`). |
| `DimResult` | One dimension's analysis bundle (function count, mean ranks, Friedman result, Holm-corrected pairwise rows). |

`gsk_family.analysis.statistics` — the dependency-light test kernel.

| Symbol | Purpose |
| --- | --- |
| `wilcoxon_paired` | Paired Wilcoxon signed-rank test over per-function errors (R+, R-, p-value). |
| `friedman_rank` | Friedman test with mean ranks across the algorithm panel. |
| `holm_correction`, `benjamini_hochberg`, `bonferroni_cross_dimension` | Multiple-comparison p-value adjustments (Holm is the default for the family panel). |
| `vargha_delaney` | Vargha-Delaney A12 probability-of-superiority effect size. |
| `win_tie_loss` | Per-function win/tie/loss tally between two optimizers. |
| `bootstrap_bca_ci` | Bias-corrected-and-accelerated (BCa) bootstrap confidence interval for a sample mean (Efron 1987). |

`gsk_family.analysis.figures` — Demsar-style figure rendering.

| Symbol | Purpose |
| --- | --- |
| `nemenyi_critical_difference(k, n_funcs, q_alpha=None)` | Nemenyi post-hoc critical difference for `k` algorithms over `n_funcs` problems. |
| `render_cd_diagram(...)` | Draw the critical-difference (CD) diagram PNG. |
| `render_rank_chart(...)` | Draw the mean-rank bar chart PNG. |

`gsk_family.analysis.latex_tables` — LaTeX table fragments.

| Symbol | Purpose |
| --- | --- |
| `friedman_ranks_latex(...)` | Friedman mean-rank LaTeX table. |
| `wilcoxon_summary_latex(...)` | Pairwise Wilcoxon + A12 + Holm-decision LaTeX table. |

Outputs land in `results/_run_all/_analysis/<suite>/` (suite lowercased) unless
the CLI is given `--out`. The narrative walkthrough, including the live `--stats`
mode and the `papers/` review pack, is in
[research/statistical_analysis.md](../research/statistical_analysis.md).

## Common Helpers

Reference-compatible numerical helpers shared by the optimizers. They live under
`gsk_family.common`. You rarely call these directly, but they define the exact
arithmetic that keeps results consistent with the upstream source.

| Symbol | Purpose |
| --- | --- |
| `bounds.gsk_bound_repair` | GSK midpoint bound repair: pull an out-of-range coordinate to `(parent + breached_bound) / 2`. |
| `donors.gained_shared_junior_r1r2r3` | Junior-phase donor index selection (fitness-rank neighbours plus a random peer). |
| `donors.gained_shared_senior_r1r2r3` | Senior-phase donor index selection (top / middle / bottom partitions). |
| `numeric_compat.compat_round`, `compat_fix`, stable-sort helpers, index-conversion helpers | Reference-matching rounding, truncation, deterministic sorting, and 1-based/0-based index conversion. |
| `population.gsk_init_population`, `gsk_initial_population_from_options`, `gsk_restore_rng_after_initialization` | Build an initial population, accept a runner-supplied fair start, and restore the post-initialization RNG state. |
| `reduction.gsk_reduction_survivors` | Indices kept after a population-size reduction step. |
| `rng.RandomContext`, `create_fair_start`, generator-normalization helpers | RNG wrapper, fair-start construction, and reference RNG label handling. |

```python
import numpy as np
from gsk_family.common.bounds import gsk_bound_repair

lb, ub = np.zeros(3), np.full(3, 10.0)
parent = np.array([[2.0, 8.0, 5.0]])
trial  = np.array([[-4.0, 12.0, 5.0]])      # first two breach the bounds
print(gsk_bound_repair(trial, parent, lb, ub))   # [[1. 9. 5.]] midpoints toward the bound
```

## CLI Entry Points

Configured in `pyproject.toml` under `[project.scripts]`:

| Command | Target | Purpose |
| --- | --- | --- |
| `gsk-list` | `gsk_family.cli.list:main` | List optimizers, suites, and reference inventory. |
| `gsk-run` | `gsk_family.cli.run:main` | Run a campaign from a YAML config or direct flags. |
| `gsk-validate` | `gsk_family.cli.validate:main` | Inspect references, or compare a generated run with `--compare RUN_DIR REFERENCE_ROOT`. |
| `gsk-stats` | `gsk_family.cli.stats:main` | Run the GSK-family statistical comparison (Friedman/Wilcoxon/Holm, tables, figures); see [Statistical Analysis](../research/statistical_analysis.md). |

The alias `gsk-family-run` also maps to `gsk_family.cli.run:main`. The canonical
launcher `python run.py` adds `src/` to `sys.path` and forwards to `gsk-run`.
Command-line usage, flags, and copy-pasteable examples are in the
[runbook](../getting-started/runbook.md) and
[configuration guide](../getting-started/configuration.md).

`gsk-stats` drives the [Statistical Analysis package](#statistical-analysis-package)
from the command line:

```powershell
# Full CEC2017 family report for the standard dimensions, with figures.
gsk-stats --suite CEC2017 --dims 10,30,50,100

# A single dimension, tables only (skip matplotlib).
gsk-stats --suite CEC2017 --dims 30 --no-figures
```

Key `gsk-stats` flags: `--suite` (default `CEC2017`), `--dims` (default the
suite's standard set), `--proposed` (default `dt-gsk`), `--results-root`
(default `results/_run_all`), `--reference-root` (default
`benchmarks/cec_reference_results`), `--out` (default
`<results-root>/_analysis/<suite>`), `--alpha` (default `0.05`), and
`--no-figures`. It returns exit code `0` on success and `1` when no
proposed-optimizer summaries can be loaded (from the reference tree or a
reproduced run).

The `gsk-run` runner also exposes a `--stats` flag (opt-in, default off): it
streams the per-dimension Wilcoxon + Friedman panel live during a campaign. The
live pass runs for every optimizer except vanilla `gsk` (gated by
`_statistical_analysis_enabled` in `runners/run_experiment.py`); the
native-dimension `cec2011` suite is supported too and emits a single per-suite
rollup panel instead of per-dimension panels. See [workflows.md](workflows.md)
and [research/statistical_analysis.md](../research/statistical_analysis.md).
