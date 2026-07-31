# Developer Guide

> **Orientation.** This is the day-to-day reference for working *inside* the
> Python package. It is for contributors who will edit code, run the test
> suite, and reason about how experiments execute. After reading it you can set
> up a local dev environment, find your way around the source tree, run the
> right test tier for a change, and understand how a run is parallelized. New to
> the project? Skim the [Code Reading Guide](code_reading_guide.md) first for a
> tour of the source, and keep the [glossary](../reference/glossary.md) and
> [module dependencies](../reference/module_dependencies.md) open for terms.
> When you are ready to submit work, follow the
> [Contributor Guide](contributor_guide.md).

## Local Setup

Install the package in editable mode with its development extras, then run the
tests once to confirm the checkout is healthy.

```powershell
python -m pip install -e ".[dev]"
python -m pytest
```

`-e` (editable) means your source edits take effect without reinstalling;
`[dev]` pulls in the test and lint tooling. The package uses a `src/` layout, so
importable code lives under `src/gsk_family/` and benchmark data is reached
through the separate `benchmarks` package. A green `python -m pytest` is the
baseline: if it fails on a fresh checkout, fix the environment before making
changes.

### Prerequisites and runtime stack

- **CPython 3.10–3.13.** `pyproject.toml` declares `requires-python =
  ">=3.10,<3.14"`, and CI exercises the full `3.10 / 3.11 / 3.12 / 3.13` matrix.
  `[tool.ruff]` pins `target-version = "py310"` as the language floor, so the
  optimizers use only 3.10-compatible syntax (`X | Y` unions,
  `from __future__ import annotations`).
- **Runtime dependencies** (declared in `pyproject.toml`, with pinned upper
  bounds): `numpy>=1.24,<2.4`, `scipy>=1.10,<1.16`, `pandas>=2.0,<2.4`,
  `matplotlib>=3.7,<3.11`, `PyYAML>=6.0,<7`, and `numba>=0.64,<0.66`. The `[dev]`
  extra adds `build>=1.0`, `mypy>=1.10,<2`, `pytest>=7.4,<10`, `ruff>=0.6,<1`,
  and `types-PyYAML>=6.0`. Numba's LLVM JIT compiles the heavy CEC2017
  composition kernels, which is why the parallel runner caps automatic workers
  (see the [worker model](#parallel-and-worker-model) below).
- The installed **console scripts** come from `[project.scripts]` in
  `pyproject.toml`: `gsk-run` (alias `gsk-family-run`), `gsk-list`,
  `gsk-validate`, and `gsk-stats`. The canonical, dependency-free runner is
  `python run.py`, which forwards to the same entry point as `gsk-run`.

### First-run sanity checks

After the test suite is green, confirm the registry and a tiny end-to-end run:

```powershell
gsk-list --optimizers --benchmarks --references benchmarks/cec_reference_results
gsk-run --config configs/smoke.yml --root .
```

`gsk-list` should report the seven runnable optimizers (`gsk`, `agsk`, `apgsk`,
`fdb-agsk`, `atmals-gsk`, `egsk`, `dt-gsk`) and the six suites (`sphere`, `cec2011`,
`cec2013`, `cec2013lsgo`, `cec2017`, `cec2020`). Generated output lands under
`results/_run_all/<optimizer>/<suite>/`; imported reference evidence under
`benchmarks/cec_reference_results/` is read-only and never written by a run.

## Development Principles

These are the standing rules that keep the port faithful and reproducible.
Follow them by default; document any deliberate exception (see the last bullet).

- Keep optimizer code dependent on `BenchmarkProblem`, not on suite internals.
- Keep runner behavior deterministic and testable.
- Prefer NumPy vector operations where they preserve reference behavior.
- Preserve reference rounding, sorting, and index conventions through helpers in
  `common/`.
- Keep generated output separate from imported reference evidence.
- Document any intentional deviation from reference behavior in
  `docs/research/validation_report.md`.

## Code Organization

The source tree is layered: shared types and the benchmark adapter sit at the
bottom, optimizers in the middle, and the runners/CLI on top. Each package has
one job.

```text
src/gsk_family/
  analysis/           summary statistics, statistical tests, plotting, LaTeX
  benchmark_adapter/  problem factory, protocol metadata, shape validation
  cli/                thin entry points (run, list, validate, stats)
  common/             reference-faithful rng, donors, bounds, population helpers
  optimizers/         the seven runnable optimizers (gsk + adaptive variants + egsk + dt-gsk)
  runners/            config, seed policy, experiment driver, output, parallel
  stats.py            error and statistics conventions
  types.py            shared dataclasses exchanged across layers
```

Dependencies flow downward only — follow the arrows in
[Module Dependencies](../reference/module_dependencies.md). The
[Code Reading Guide](code_reading_guide.md) walks these packages in reading
order.

### The vendored dt-gsk core (byte-identity rule)

`optimizers/_dt_core.py`, `_dt_subsystems/`, `_dt_rng.py` and `_dt_profiles.py` are
**vendored** and must not be edited for behavior. `dt_gsk.py` is the adapter onto the
optimizer contract, and is where anything the runner needs belongs.

**See the [DT-GSK Core Reference](dt_gsk_core_reference.md)** for the locked file list,
the six tests that hold the line, the dimension tiers, the determinism setup at
`D >= 50`, and the facts about DT-GSK that are most often got wrong.

## Documentation Requirements

Every module, class, function, and method in `src/gsk_family` should have a
docstring. Public behavior also needs Markdown coverage when it affects users,
experiments, output artifacts, reproducibility, or parity decisions.

Three documentation gates run as part of `python -m pytest`; treat them as part
of the local gate, not optional polish:

1. **Docstring-coverage gate** — `tests/unit/test_docstrings.py` walks every
   `*.py` under `src/gsk_family` with `ast` and fails if any module, class,
   function, or method lacks a docstring. The vendored `dt-gsk` core
   (`optimizers/_dt_core.py`, `optimizers/_dt_subsystems/*`) and the vendored
   `analysis/statistics.py` / `analysis/statistical_tests.py` are exempt, since
   they are byte-identical upstream copies (see the
   [vendored-core rule](#the-vendored-dt-gsk-core-byte-identity-rule)).
2. **Documentation-command gate** — `tests/smoke/test_documentation_commands.py`
   runs the commands quoted in the docs (`gsk-list`, `gsk-validate`, a direct
   `gsk_family.cli.run`, and the HTML generator) and also asserts that a fixed
   list of documentation paths resolves on disk via `test_documented_docs_exist`.
   **Renaming, moving, or deleting a listed doc breaks this gate.** If you must
   add a new doc, add its path to that list too — but prefer editing an existing
   file.
3. **Link-resolution gate** — `test_generated_html_local_links_resolve` in the
   same module fails if any local `href`/`src` in the generated `docs/html/`
   site points at a missing file. Every relative Markdown link must therefore
   resolve to a real file before you rebuild the HTML.

After editing any docstring or Markdown page, rebuild the HTML twins with
`python scripts/build_docs_html.py` so `docs/html/` stays in sync, then commit
the regenerated HTML alongside the source change.


## Testing

Pick the cheapest tier that covers your change, then run the full suite before
you push. Run all default tests with `python -m pytest`. The suite is organized
into tiers that mirror the `tests/` layout, fastest first:

- **Unit tests** (`tests/unit`): helper semantics, seed formulas, statistics,
  option parsing, RNG/numeric compatibility, the parallel helpers, the CLI, and
  verification. Representative files: `test_donors.py`, `test_bounds.py`,
  `test_population.py`, `test_reduction.py`, `test_numeric_compat.py`,
  `test_rng.py`, `test_seed_policy.py`, `test_config.py`, `test_cli_run.py`,
  `test_parallel.py`, `test_statistical_tests_friedman.py`,
  `test_dt_profiles.py`, and `test_dt_rng.py`. This tier also includes the
  docstring-coverage gate (`test_docstrings.py`).
- **Smoke tests** (`tests/smoke`): each optimizer and the runner executing on
  tiny budgets — `test_gsk_smoke.py`, `test_agsk_smoke.py`,
  `test_apgsk_smoke.py`, `test_fdb_agsk_smoke.py`, `test_atmals_gsk_smoke.py`,
  `test_dt_gsk_smoke.py`, `test_runner_smoke.py` — plus the `gsk-stats` CLI
  (`test_stats_cli_smoke.py`), the `--stats` run flag
  (`test_stats_flag_smoke.py`), and the documentation-command +
  link-resolution gates (`test_documentation_commands.py`).
- **Regression tests** (`tests/regression`): the validation ladder
  (`test_validation_ladder.py`) guarding reference-comparison and exact
  Python-replay behavior; the process-pool self-heal (`test_pool_self_heal.py`);
  the floating-point-regime sentinel (`test_fp_regime.py`); and four dt-gsk locks
  --- the byte-stability golden (`test_dt_gsk_byte_stable.py`), the best-so-far
  convergence contract (`test_dt_gsk_curve_monotone.py`), the interaction-graph
  backend parity (`test_dt_graph_backend_parity.py`), and the final-polish
  incumbent consistency (`test_dt_polish_incumbent_consistent.py`). The last two
  run at `D >= 50`, because the byte-stability golden cannot reach that tier ---
  see the [DT-GSK Core Reference](dt_gsk_core_reference.md).
- **Performance tests** (`tests/performance`): the parallel runner under a
  realistic task load (`test_parallel_runner.py`). This tier carries the `slow`
  marker: `-m "not slow"` skips it, `-m slow` runs only it.

A top-level import smoke test (`tests/test_imports.py`) also runs by default.
Run a focused tier by passing its directory, or a single file/test for tighter
loops:

```powershell
python -m pytest tests/unit
python -m pytest tests/smoke
python -m pytest tests/regression
python -m pytest tests/performance
python -m pytest tests/regression/test_dt_gsk_byte_stable.py -q
python -m pytest "tests/unit/test_seed_policy.py::test_unified_schedule" -q
```

A quick rule of thumb:

| Change you made | Tier(s) to run first |
| --- | --- |
| A helper or numeric formula in `common/` | `tests/unit` |
| An optimizer kernel or the runner | add `tests/smoke` |
| Anything touching reference parity / replay | `tests/regression` |
| The vendored dt-gsk core, RNG, or profile | `tests/regression/test_dt_gsk_byte_stable.py` + `tests/unit/test_dt_profiles.py` |
| The parallel/worker code | `tests/performance` |

Always run the whole suite (`python -m pytest`), the linter
(`python -m ruff check src tests scripts`), and the scoped type-check gate
(`python -m mypy src/gsk_family/cli src/gsk_family/runners src/gsk_family/common
--ignore-missing-imports --follow-imports=skip`) before opening a pull
request — that is the same gate the
[Contributor Guide](contributor_guide.md#contribution-workflow) spells out.

### Linting and type checking

The project lints with ruff, configured in `pyproject.toml`. `[tool.ruff]` sets
`target-version = "py310"` and `line-length = 120`; the deliberately tight rule
set lives under the nested `[tool.ruff.lint]` table as
`select = ["E9", "F"]` (pycodestyle syntax errors and pyflakes checks). Because
that selection is configured in the file, the local command needs no `--select`
flag — run it over the three source roots:

```powershell
python -m ruff check src tests scripts
```

Ruff is intentionally scoped to correctness-class rules so it never reformats or
fights the reference-faithful numeric code; style is enforced by review, not by
an autoformatter. (CI runs the equivalent whole-tree form
`python -m ruff check . --select F,E9`.)

A **scoped mypy gate** — configured in `[tool.mypy]` (`python_version = "3.10"`,
`ignore_missing_imports = true`, `follow_imports = "skip"`) — type-checks the
three actively-typed packages. Run the same command CI runs:

```powershell
python -m mypy src/gsk_family/cli src/gsk_family/runners src/gsk_family/common `
  --ignore-missing-imports --follow-imports=skip
```

The scope is deliberate: `cli`, `runners`, and `common` are held to a clean
type check, while the imported benchmark/optimizer kernels are left out to avoid
fighting NumPy 2.x shape-typing churn. A green run reports
`Success: no issues found`.

## Parallel and worker model

This section explains how one `gsk-run` invocation spreads its independent runs
across CPU cores. The runner has conservative defaults, and the runbooks keep
the worker count visible in full-campaign commands.

Experiment runs execute on a **process** pool: the runner builds a
`ProcessPoolExecutor` with a `spawn` start method (each worker is a fresh
process, so there is no shared interpreter state across cells). Automatic worker
count is `2` when at least two logical CPU cores are available, otherwise `1`
(`default_worker_count`, with `DEFAULT_WORKER_COUNT = 2` in
`runners/parallel.py`). Full campaign examples spell this out as
`--parallel --workers 2` so users can decide when to spend more CPU and memory.

`effective_worker_count` applies one safety cap: when the worker count is
**automatic**, the backend is `process`, the suite is `cec2017`, and the
function id is `>= 21` (the composition cells `F21`-`F30`), the count is clamped
to `DEFAULT_CEC_PROCESS_WORKER_CAP = 8`. These cells JIT-compile heavy
Numba/LLVM kernels inside each spawned worker; on typical workstation memory,
letting too many automatic workers compile them at once can exhaust LLVM memory.
An explicit `--workers N` is always respected verbatim — the cap only guards the
automatic policy. Pass `--workers N` to choose a different speed/memory tradeoff
explicitly.

If a spawned worker dies (an intermittent crash or out-of-memory), the runner
tears the pool down, rebuilds it, and retries the affected cell, up to three
rebuilds. After repeated failures it falls back to the **serial** backend for
that cell and rebuilds a fresh pool for the next one. It never falls back to the
thread backend, which would deadlock on the GIL-bound inner loops. Because each
run is an independent task keyed by `(optimizer, suite, dim, func, run)`, the
process pool is embarrassingly parallel and the per-cell retry never changes a
run's seed or result — only where it executes. The
[performance notes](../research/performance.md) discuss campaign-scale timing.

## Statistical Analysis Suite

Two distinct paths produce statistics; do not confuse them.

- **Live, in-run analysis (`--stats`).** The `gsk-run` / `run.py` runner accepts
  an opt-in `--stats` flag (default OFF). When set, it streams a Wilcoxon +
  Friedman panel live as a run progresses. Gating mirrors the reference runner
  via `_statistical_analysis_enabled` in `runners/run_experiment.py`, whose only
  hard exclusion is vanilla `gsk`: the panel runs for every **advanced**
  GSK-family optimizer. Fixed-dimension suites (e.g. `cec2017`) emit a
  per-dimension panel; the native-dimension `cec2011` is now supported too and
  emits a single per-suite rollup panel (its 22 problems have no per-dimension
  split), which became possible once the CEC2011 reference rollups were
  committed. Exercised by `tests/smoke/test_stats_flag_smoke.py`.
- **Post-hoc analysis suite (`gsk-stats`).** The standalone CLI in
  `cli/stats.py` (entry point `gsk-stats`) runs over a results tree and writes
  to `results/_run_all/_analysis/<suite>/` unless `--out` is given. Data policy:
  the loader (`analysis/result_loader.py::load_algorithm`, used by
  `analysis/family_report.py`) reads the committed reference panel under
  `benchmarks/cec_reference_results/` **first** and falls back to locally
  reproduced `results/_run_all/` only for cells the reference tree does not
  carry — so all paper statistics come from the single committed source of
  truth. Its engine
  under `src/gsk_family/analysis/` produces: Friedman mean ranks
  (`statistical_tests.py`), Nemenyi critical-difference diagrams and rank charts
  (`figures.py`), pairwise Wilcoxon signed-rank tests with Holm correction,
  Vargha-Delaney A12 / Cliff's delta effect sizes, win/tie/loss counts, BCa
  bootstrap intervals, and LaTeX table fragments (`latex_tables.py`). The
  7-algorithm GSK-family panel = the six reference comparators (`gsk`, `agsk`,
  `apgsk`, `fdb-agsk`, `egsk`, `atmals-gsk`) plus `dt-gsk`; `egsk`'s panel cells
  are reported from committed reference comparator data even though `egsk` is now
  also a runnable optimizer (`optimizers/egsk.py`). The
  CEC2017 scored set excludes `F2` (it scores `F1`, `F3`-`F30`), which the
  analysis loader encodes as `excluded=(2,)`. Smoke-tested by
  `tests/smoke/test_stats_cli_smoke.py`. See
  [Statistical Analysis](../research/statistical_analysis.md) for the
  methodology.

## Papers Review Pack

The `papers/` directory holds the manuscript and a reproducible review pack.
`python papers/scripts/generate_review_pack.py` builds
`papers/DT-GSK-CEC2017-review.pdf` directly with matplotlib `PdfPages` — **no
LaTeX is required** for the review pack (MiKTeX is only needed for the full
`papers/main.tex` paper). The pack draws 7-algorithm convergence grids (GSK,
AGSK, APGSK, FDB-AGSK, eGSK, ATMALS-GSK, DT-GSK) from
`CheckpointErrors_<alg>_F<k>_D<dim>.csv` files; any missing curve is logged to
`papers/DT-GSK-CEC2017-review_missing.log` and **never fabricated**. When you
change result schema or curve filenames, re-run the pack and check that log.

The review pack is one piece of a larger pipeline. The paper's convergence-figure
generators (`papers/scripts/generate_full_convergence.py`,
`generate_cec2011_convergence.py`, `generate_cec2013_convergence.py`) read their
curves and `gen_logs` from `benchmarks/cec_reference_results/`; the DT-GSK
scaffold ablation is driven by `scripts/run_ablation.py` and aggregated by
`papers/scripts/generate_ablation_matrix.py` +
`papers/scripts/generate_latex_tables.py`. The ordered stage list is the
"Full Paper Pipeline" section of the root `runbook.md`.
