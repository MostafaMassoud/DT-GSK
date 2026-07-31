# Extension Guide

> **Orientation.** This page shows how to *add* to the package: a new optimizer,
> a benchmark suite, an output artifact, or a CLI command. It is for contributors
> extending capability rather than fixing existing code. After reading it you can
> create each kind of component, register it in the right place, and know which
> tests and docs to add. It assumes you have read the
> [Developer Guide](developer_guide.md) and the
> [Code Reading Guide](code_reading_guide.md); follow the
> [Contributor Guide](contributor_guide.md) when you submit. The optimizer
> contract is specified in the
> [Python Optimizer Interface](../reference/python_optimizer_interface.md), and
> shared terms are in the [glossary](../reference/glossary.md).

Each section below is a self-contained recipe. Do the numbered steps in order;
the registration step (where the new component becomes visible to the runner or
CLI) is the one that is easy to forget.

## Add An Optimizer

An optimizer is a single module exposing one `optimize(problem, options)`
function and returning an `OptimizerResult`. The numbered contract below is the
same one `optimizers/gsk.py` follows; the skeleton after it is a compiling
starting point.

1. Create `src/gsk_family/optimizers/<name>.py`.
2. Expose `optimize(problem, options)`.
3. Accept `OptimizerOptions` and plain dictionaries.
4. Read custom options from `options.values` or from the top-level dict.
5. Evaluate candidates only through `problem.evaluate`.
6. Keep candidates inside `problem.lb` and `problem.ub`.
7. Stop at `problem.max_nfes`.
8. Return `OptimizerResult`.
9. Register the optimizer in `OPTIMIZER_FUNCTIONS` in
   `src/gsk_family/runners/run_experiment.py`.
10. Add smoke, fair-start/replay, and runner tests.
11. Add an algorithm page under `docs/algorithms/`.

### Skeleton

The `optimize` contract is the same one the baseline GSK optimizer follows. The
stub below compiles against `gsk_family.types` and shows the option-reading and
`OptimizerResult` construction patterns from `optimizers/gsk.py`. Fill the loop
with the real search and keep every field name as written.

```python
"""Example optimizer."""

from __future__ import annotations

import time
from typing import Any

import numpy as np

from gsk_family.benchmark_adapter.problem import BenchmarkProblem
from gsk_family.stats import compute_error
from gsk_family.types import ConvergenceTrace, OptimizerOptions, OptimizerResult

_MISSING = object()


def _option_value(options: Any, name: str, default: Any = _MISSING) -> Any:
    """Read an option from object, dict, or nested values mapping."""
    if options is None:
        if default is _MISSING:
            raise ValueError(f"options.{name} is required.")
        return default
    if isinstance(options, dict):
        value = options.get(name, _MISSING)
        values = options.get("values", {})
    else:
        value = getattr(options, name, _MISSING)
        values = getattr(options, "values", {})
    if (value is _MISSING or value is None) and isinstance(values, dict):
        value = values.get(name, _MISSING)
    if value is _MISSING or value is None:
        if default is _MISSING:
            raise ValueError(f"options.{name} is required.")
        return default
    return value


def optimize(
    problem: BenchmarkProblem,
    options: OptimizerOptions | dict[str, Any],
) -> OptimizerResult:
    """Run the example optimizer and return one `OptimizerResult`."""
    seed = int(_option_value(options, "seed"))
    np_size = int(_option_value(options, "np", 100))

    start = time.perf_counter()
    dim = int(problem.dim)
    max_nfes = int(problem.max_nfes)

    nfes = 0
    best_fitness = float("1e300")
    best_x = np.zeros(dim, dtype=np.float64)
    conv_nfes: list[int] = []
    conv_best: list[float] = []

    # Search loop: draw candidates inside problem.lb/problem.ub, evaluate only
    # through problem.evaluate, update best_x/best_fitness, and stop at max_nfes.
    while nfes < max_nfes:
        candidates = np.random.default_rng(seed + nfes).uniform(
            problem.lb, problem.ub, size=(np_size, dim)
        )
        fitness = np.asarray(problem.evaluate(candidates), dtype=np.float64).reshape(-1)
        n_count = min(np_size, max_nfes - nfes)
        idx = int(np.argmin(fitness[:n_count]))
        if float(fitness[idx]) < best_fitness:
            best_fitness = float(fitness[idx])
            best_x = candidates[idx, :].copy()
        nfes += n_count
        conv_nfes.append(int(nfes))
        conv_best.append(float(best_fitness))

    error = compute_error(
        best_fitness, float(problem.optimum), float(problem.target_error)
    )

    return OptimizerResult(
        optimizer="example",
        suite=problem.suite,
        func_id=int(problem.func_id),
        dim=dim,
        seed=seed,
        best_x=best_x,
        best_fitness=float(best_fitness),
        error=float(error),
        nfes=int(nfes),
        termination="max_evaluations",
        convergence=ConvergenceTrace(
            nfes=np.asarray(conv_nfes, dtype=np.int64),
            best_fitness=np.asarray(conv_best, dtype=np.float64),
        ),
        runtime_seconds=float(time.perf_counter() - start),
        params={"np": np_size},
        notes="",
    )
```

Register it (step 9) by adding the name and its `optimize` function to the
`OPTIMIZER_FUNCTIONS` dict in `runners/run_experiment.py`, keeping the existing
imported alias style:

```python
OPTIMIZER_FUNCTIONS = {
    "agsk": optimize_agsk,
    "apgsk": optimize_apgsk,
    "atmals-gsk": optimize_atmals_gsk,
    "egsk": optimize_egsk,
    "example": optimize_example,  # add the new optimizer here
    "fdb-agsk": optimize_fdb_agsk,
    "gsk": optimize_gsk,
    "dt-gsk": optimize_dt_gsk,
}
```

Also add the id to the `OPTIMIZER_IDS` tuple in
`src/gsk_family/optimizers/__init__.py` so `gsk-list` and config validation see
it. If the optimizer needs a fixed seed/RNG policy regardless of the run's
`seed_policy`, register it in `runners/seed_policy.py` as well (for example by
adding the id to `UNIFIED_ONLY_OPTIMIZERS`, which forces `threefry` + the shared
`get_cec_seed` schedule under every policy — this is exactly what `dt-gsk`
does).

To recap, a new optimizer has **three** registration points, all of which the
worked `dt-gsk` example below touches:

1. `OPTIMIZER_FUNCTIONS` in `runners/run_experiment.py` (name -> `optimize`).
2. `OPTIMIZER_IDS` in `optimizers/__init__.py` (so `gsk-list` and config
   validation accept the id).
3. *(optional)* `runners/seed_policy.py` (only if it needs a fixed seed/RNG
   policy).

Then add tests in the matching tiers — a smoke test under `tests/smoke/`
(model it on `tests/smoke/test_gsk_smoke.py`), any fair-start/replay coverage,
and a runner test — and an algorithm page under `docs/algorithms/<name>.md`
linked from `docs/index.md`. The new module must satisfy the docstring gate
(`tests/unit/test_docstrings.py`): give the module, `optimize`, and every helper
a docstring unless the module is a byte-identical vendored copy.

### Worked example: dt-gsk

`dt-gsk` — this project's proposed Dimension-Tiered Gaining-Sharing Knowledge — is a real
optimizer added through exactly the steps above, and is a good template when your
optimizer needs its own configuration and RNG layers:

- the `optimize(problem, options)` adapter lives in
  `optimizers/dt_gsk.py` (it applies the dimension-aware "pub" profile
  automatically by `problem.dim`);
- the per-dimension-tier config builder is in `optimizers/_dt_profiles.py`;
- the named-substream RNG layer is in `optimizers/_dt_rng.py`, with the core
  driver and subsystems under `optimizers/_dt_core.py` and
  `optimizers/_dt_subsystems/`;
- it is registered in `OPTIMIZER_IDS` (`optimizers/__init__.py`) and
  `OPTIMIZER_FUNCTIONS` (`runners/run_experiment.py`), and is listed in
  `UNIFIED_ONLY_OPTIMIZERS` in `runners/seed_policy.py` so it always uses the
  unified shared seed with `threefry` under every seed policy;
- it self-initializes a `np_init_mult * D` population (always `5*D`;
  `np_init_mult` is never overridden at any dimension) rather than consuming the
  runner's fair-start `initial_population`; the adapter records this as
  `notes="self-init (fair-start exception)"`;
- it ships a **default-on deep-stall full restart** (multi-start): when the
  incumbent has been frozen for `>= deep_stall_frac` of the budget the entire
  working population is re-initialised uniformly while a separate global-best
  preserves the best-ever, so a restart can never lose ground. The fields live in
  `DTGSKConfig` (`optimizers/_dt_core.py`): `deep_stall_restart_enabled=True`,
  `deep_stall_frac=0.25`, `deep_stall_cooldown_frac=0.15`, `deep_stall_stop_frac=0.9`,
  `deep_stall_min_budget=20000`. It is a **standard** mechanism, not an
  `experimental_*` flag, and draws RNG only when it fires — non-stalling and
  tiny-budget runs (below `deep_stall_min_budget`) stay byte-identical, which is
  why the byte-stability golden is unaffected.

Two distinct kinds of "locked" apply here, and it is worth keeping them apart.
The whole `dt-gsk` set — `dt_gsk.py`, `_dt_profiles.py`, `_dt_rng.py`,
`_dt_core.py`, and `_dt_subsystems/` — is **behavior-frozen** (hash-locked in
`algorithm_freeze_manifest.json`) and guarded by
`tests/regression/test_dt_gsk_byte_stable.py` (exact `best_fitness` at
`seed=12345`, `max_nfes=3000`, `pub` profile) and `tests/unit/test_dt_profiles.py`.
The **docstring-gate exemption** is narrower: only the two byte-identical
upstream copies — `_dt_core.py` and everything under `_dt_subsystems/` — are
exempt (`_is_vendored_ism` in `tests/unit/test_docstrings.py`). The adapter
`dt_gsk.py` and the project-authored `_dt_profiles.py` / `_dt_rng.py` carry full
docstrings and **are** checked by the gate. A brand-new optimizer you author is
neither frozen nor exempt — give it full docstrings. Use `dt-gsk` as a
structural template for layering (adapter + profile + RNG + core), not as a
license to skip the docstring or test requirements.

## Add A Benchmark Suite

A suite is described by its metadata (dimensions, function count, budget) and a
factory that builds each `BenchmarkProblem`. Add both, then make sure shapes are
normalized so optimizers see a consistent problem object. See the
[Benchmark Protocol](../reference/benchmark_protocol.md) for the metadata fields.

1. Add a `SuiteProtocol` entry to the `SUITE_PROTOCOLS` map in
   `benchmark_adapter/protocol.py`, and list the new id in `SUPPORTED_SUITES`
   (and `CEC_SUITES` if it is a CEC suite). A `SuiteProtocol` carries
   `suite`, `function_ids`, `default_function_ids`, `default_dimensions`,
   `statistics_basis`, `target_error`, and `notes`. Two fields encode the
   conventions the runner and analysis layers gate on:
   - **Statistics basis.** Set `statistics_basis` to `STAT_RAW` (raw objectives,
     as `cec2011`/`cec2013lsgo` do) or `STAT_ERROR` (error-vs-optimum, as
     `cec2013`/`cec2017`/`cec2020` do); the same basis is stamped onto each
     `BenchmarkProblem` in `factory.py`. Keep the module-level membership sets
     `RAW_OBJECTIVE_SUITES` / `ERROR_VS_OPTIMUM_SUITES` in sync with that choice.
   - **Native dimension.** Set `default_dimensions="native"` for a
     per-function-dimension suite (like `cec2011`); `is_native_dimension_suite()`
     then reports `True`. Otherwise give an explicit dimension tuple such as
     `(10, 30, 50, 100)`.
2. Add problem construction to `benchmark_adapter/factory.py` so `make_problem`
   builds your `BenchmarkProblem` (follow the existing `_sphere_problem` /
   per-suite branches; honor `max_nfes_override`).
3. Normalize population and fitness shapes through
   `benchmark_adapter/problem.py`.
4. Add a benchmark README under `benchmarks/cec_suite_python/<suite>/` if data is
   packaged.
5. Add or update documentation, fixtures, and validation evidence for the suite
   before exposing it through the runner.
6. Add adapter tests (model on `tests/unit/test_benchmark_adapter.py`) for
   bounds, dimensions, function ids, and backend selection.

Two existing protocol conventions to respect: the **CEC2017 scored set excludes
F2** (it covers `F1`, `F3`-`F30`), and `cec2011` is native-dimension, so its
live `--stats` panel is a single per-suite rollup rather than a per-dimension
one (the panel is skipped only for vanilla `gsk`, never by suite). Keep any new
suite's metadata consistent with how the analysis loader and the runner gate on
these properties.

## Add An Output Artifact

An artifact is a file the runner writes per experiment (for example a CSV or a
JSON summary). Add the writer, document its schema, and test by parsing it back.
Existing artifacts and their byte-format conventions are in the
[Result Schema](../reference/result_schema.md).

1. Add writer logic to `runners/output.py`.
2. Add schema documentation to `docs/reference/result_schema.md`.
3. Add tests that parse the artifact rather than only checking file existence.
4. Keep generated output below `results/` by default.

## Add A CLI Command

A CLI command is a thin module wired to a console entry point. The existing
commands (`gsk-run`, `gsk-list`, `gsk-validate`, `gsk-stats`) live in
`src/gsk_family/cli/` and delegate all real work to the lower layers -- follow
that pattern.

1. Create a module in `src/gsk_family/cli/` that exposes a `main(argv=None) -> int`
   function (the existing `list.py`, `run.py`, `validate.py`, and `stats.py`
   modules all follow this signature).
2. Add an entry to `[project.scripts]` in `pyproject.toml`, mapping the script
   name to `gsk_family.cli.<module>:main`. For reference, the current entries
   are:

   ```toml
   [project.scripts]
   gsk-list = "gsk_family.cli.list:main"
   gsk-run = "gsk_family.cli.run:main"
   gsk-family-run = "gsk_family.cli.run:main"
   gsk-validate = "gsk_family.cli.validate:main"
   gsk-stats = "gsk_family.cli.stats:main"
   ```

3. Keep CLI modules thin; business logic belongs in `runners`, `analysis`, or
   `benchmark_adapter`. (`gsk-stats`, for example, is a thin wrapper over the
   `analysis/` statistical suite.)
4. Add smoke tests (model on `tests/smoke/test_stats_cli_smoke.py`) and update
   the [runbook](../getting-started/runbook.md). If you quote the new command in
   any doc, the documentation-command gate
   (`tests/smoke/test_documentation_commands.py`) will execute it — keep the
   quoted invocation runnable.

