# Python Optimizer Interface

> **What this is.** The contract every optimizer follows, with a runnable
> snippet for each implemented optimizer. **Who it is for.** Anyone
> calling an optimizer directly (tests, experiments) or writing a new one.
> **Prerequisites.** A working install and the terms in [the glossary](glossary.md)
> (`BenchmarkProblem`, fair start, convergence trace). **After reading** you can
> build a problem, run any optimizer, read its result, and know what a new
> optimizer must provide. For the importable symbol map see
> [api.md](api.md); for the campaign runner see [workflows.md](workflows.md).

The public optimizer interface is intentionally small. Every optimizer depends
on just three types — `BenchmarkProblem` (what to solve), `OptimizerOptions`
(how to start), and `OptimizerResult` (what came back). The two steps below —
build a problem, then call `optimize` — are the whole interface.

## Problem Construction

A `BenchmarkProblem` packages a suite function with its bounds, budget, optimum,
and a vectorized evaluator. Build one with `make_problem`.

```python
from gsk_family.benchmark_adapter.factory import make_problem

problem = make_problem("cec2017", 1, dim=10, max_nfes_override=1000)
```

`make_problem` validates the suite, function id, dimension, bounds, known
optimum metadata, and evaluation budget. The returned object exposes:

```python
problem.suite
problem.func_id
problem.dim
problem.lb
problem.ub
problem.optimum
problem.max_nfes
problem.target_error
problem.statistics_basis
problem.evaluate(population)
```

`population` must be a two-dimensional `float64`-compatible array with shape
`(n_candidates, problem.dim)`. The evaluator returns a one-dimensional fitness
vector with one value per candidate. The full table of suites, function ids,
dimensions, and budgets accepted by `make_problem` is in
[benchmark_protocol.md](benchmark_protocol.md).

## Running Implemented Optimizers

Each call below is complete: build a problem (above), then call that optimizer's
`optimize`. The `values` dictionary carries the options that are specific to one
optimizer; the keys shown are the ones that optimizer actually reads. Baseline
GSK:

```python
from gsk_family.optimizers.gsk import optimize
from gsk_family.types import OptimizerOptions

result = optimize(problem, OptimizerOptions(seed=20240620, rand_generator="threefry"))
```

Adaptive GSK:

```python
from gsk_family.optimizers.agsk import optimize

result = optimize(
    problem,
    OptimizerOptions(
        seed=20240620,
        rand_generator="threefry",
        values={"np_init": 100, "min_pop_size": 12},
    ),
)
```

Adaptive-parameters GSK:

```python
from gsk_family.optimizers.apgsk import optimize

result = optimize(
    problem,
    OptimizerOptions(
        seed=20240620,
        rand_generator="threefry",
        values={"np_init": 100, "min_pop_size": 12},
    ),
)
```

Fitness-Distance Balance AGSK:

```python
from gsk_family.optimizers.fdb_agsk import optimize

result = optimize(
    problem,
    OptimizerOptions(
        seed=20240620,
        rand_generator="threefry",
        values={"fdb_case": 1, "np_init": 100, "min_pop_size": 12},
    ),
)
```

ATMALS-GSK:

```python
from gsk_family.optimizers.atmals_gsk import optimize

result = optimize(
    problem,
    OptimizerOptions(
        seed=20240620,
        rand_generator="threefry",
        values={"protocol": "cec2017", "np": 100},
    ),
)
```

Enhanced GSK (`egsk`, a faithful MATLAB port; its interior-point refinement
uses `scipy.optimize.minimize(method="SLSQP")` in place of MATLAB `fmincon`):

```python
from gsk_family.optimizers.egsk import optimize

result = optimize(
    problem,
    OptimizerOptions(
        seed=20240620,
        rand_generator="threefry",
        values={"np": 100},
    ),
)
```

DT-GSK (the project's proposed Dimension-Tiered GSK method; the
interaction-structure memory is one supporting mechanism inside it):

```python
from gsk_family.optimizers.dt_gsk import optimize

result = optimize(problem, OptimizerOptions(seed=20240620, rand_generator="threefry"))
```

DT-GSK needs no required `values`: it applies a dimension-aware `pub` profile
automatically from `problem.dim`. The profile builder
(`gsk_family.optimizers._dt_profiles.build_pub_config`) picks one of four
dimension tiers via `pub_overrides(dim)` — `D<20`, `20-49`, `50-99`, `>=100` —
and merges those tier overrides over the common `DTGSKConfig` defaults (defined
in `gsk_family.optimizers._dt_core`). Advanced users may override individual
`DTGSKConfig` fields through `options.values`, e.g.
`OptimizerOptions(seed=..., values={"np_init_mult": 6})`.

Unlike the other optimizers, DT-GSK self-inits its own population from the
unified `threefry(seed)` stream and intentionally ignores the runner-supplied
fair-start population — a documented fair-start exception intrinsic to the
algorithm; it never uses a different seed. The initial size is
`np_init_mult * D` with `np_init_mult` defaulting to `5` (so `5*D`), and the
population is reduced toward the NLPSR floor `n_min` (the `DTGSKConfig` default
is `12`; the D>=50 tiers raise it to `25`) as the budget is spent.
The exact seeding contract (it is in `seed_policy.UNIFIED_ONLY_OPTIMIZERS`, so it
uses the shared `get_cec_seed` seed under every policy) is in
[seed_policy.md](seed_policy.md).

The result is an `OptimizerResult`:

```python
result.optimizer
result.suite
result.func_id
result.dim
result.seed
result.best_x
result.best_fitness
result.error
result.nfes
result.termination
result.convergence.nfes
result.convergence.best_fitness
result.runtime_seconds
result.params
```

What each result field means:

| Field | Meaning |
| --- | --- |
| `optimizer`, `suite`, `func_id`, `dim`, `seed` | Identity of the run (echoed back from the problem and options). |
| `best_x` | Best decision vector found, inside `problem.lb`/`problem.ub`. |
| `best_fitness` | Raw objective value of `best_x`. |
| `error` | Target-zeroed error vs the known optimum; `NaN` for raw-objective suites. |
| `nfes` | Benchmark evaluations actually spent. Optimizers stop at `problem.max_nfes` unless the target error is reached earlier. |
| `termination` | Why the run stopped: `target_error_reached` or `max_evaluations`. |
| `convergence.nfes`, `convergence.best_fitness` | Paired arrays for the convergence trace. |
| `runtime_seconds` | Wall-clock time for this run. |
| `params` | Resolved optimizer parameters such as population size, factors, adaptive settings, and local-search settings for optimizers that support them. |

`result.convergence.best_fitness` is best-so-far and therefore non-increasing
for minimization problems.

## Optimizer Options

`OptimizerOptions` fields:

- `seed`: deterministic integer seed for this run.
- `rand_generator`: reference-facing RNG label such as `threefry` or `twister`.
- `initial_population`: optional fair-start population supplied by the runner.
- `rng_state_after_initialization`: optional state captured immediately after
  fair-start creation.
- `values`: optimizer-specific options.

All implemented optimizers also accept a plain dictionary for convenience:

```python
result = optimize(problem, {"seed": 77, "np": 20})
result = optimize(problem, {"seed": 77, "np_init": 20, "min_pop_size": 12})
result = optimize(problem, {"seed": 77, "fdb_case": 3, "np_init": 20})
result = optimize(problem, {"seed": 77, "protocol": "cec2011", "np": 20})
result = optimize(problem, {"seed": 77, "values": {"np_init_mult": 6}})  # dt-gsk: override one DTGSKConfig field
```

For new optimizers, prefer accepting `OptimizerOptions` and reading custom
parameters from `options.values`.

## Fair Starts

The runner uses the unified seed policy to create the same initial population
for every optimizer in a matching `(dimension, function, run)` cell. It passes
that population and the restored post-initialization RNG state to the optimizer.

This preserves fair cross-optimizer comparisons while still allowing each
optimizer to continue drawing random values after initialization.

## New Optimizer Checklist

When adding another GSK-family optimizer:

- expose `optimize(problem: BenchmarkProblem, options: OptimizerOptions)`;
- keep all candidate vectors inside `problem.lb` and `problem.ub`;
- count benchmark evaluations through `problem.evaluate`;
- stop at `problem.max_nfes`;
- return an `OptimizerResult` with a valid best-so-far convergence trace;
- add the optimizer function to `OPTIMIZER_FUNCTIONS` in
  `src/gsk_family/runners/run_experiment.py`;
- register the optimizer id in `RUNNABLE_OPTIMIZERS` in
  `src/gsk_family/analysis/project_policy.py` so the statistical-analysis layer
  recognizes it (and add it to `REFERENCE_COMPARATORS` there only if it also
  ships committed reference statistics);
- add smoke, fair-start/replay, and runner tests.

The full step-by-step procedure, including suite registration, is in the
[extension guide](../development/extension_guide.md).
