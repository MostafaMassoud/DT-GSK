# Benchmark Mapping

> **What this is.** A translation table from the upstream reference benchmark
> framework to its Python equivalents in this project. **Who it is for.** Readers
> familiar with the original source who want to find "where did X go?", and
> maintainers tracing provenance. **Prerequisites.** None beyond the
> [glossary](glossary.md). **After reading** you can map any reference-source
> concept (problem construction, bounds, budget, optimum, comparison) to the
> Python symbol or path that replaces it. For the rules those symbols enforce see
> [benchmark_protocol.md](benchmark_protocol.md); for the function-by-function
> numerical equivalence of the Python evaluators against the C++ reference, see
> the per-suite `cec*_cpp_python_equivalence_review.md` pages in this folder.

This document maps the Python benchmark framework to the reference benchmark
implementation that was used as reference-source evidence. Bare `.m` filenames
below name original source files; the Python column is what you call now.

## Source Evidence

The source archive supplied:

- reference runners and optimizer implementations;
- compiled reference-bridge benchmark code;
- CEC input data;
- reference result tables, convergence curves, and logs;
- benchmark README files and protocol notes.

The Python project keeps imported benchmark evidence and live evaluator assets
under two directories:

```text
benchmarks/cec_reference_results/     (reference tables, used for validation)
benchmarks/cec_suite_python/          (Python/Numba benchmark evaluator/data)
```

## Python Runtime Mapping

Each reference concept on the left is replaced by the Python symbol or path on
the right.

| Reference-source concept | Python equivalent |
|---|---|
| Python benchmark evaluator | `benchmarks/cec_suite_python` Python/Numba benchmark package |
| Reference problem builder | `gsk_family.benchmark_adapter.factory.make_problem` |
| CEC suite metadata | `gsk_family.benchmark_adapter.protocol` (`suite_protocol`, function/dimension rules) |
| Bounds structures | `BenchmarkProblem.lb` and `BenchmarkProblem.ub` |
| Function-evaluation budget | `BenchmarkProblem.max_nfes` |
| Known optimum | `BenchmarkProblem.optimum` |
| Objective calls | `BenchmarkProblem.evaluate(population)` |
| Summary tables | `results/_run_all/<optimizer>/<suite>/summary/*.csv` |
| Reference comparisons (validation) | `gsk_family.runners.verification` |
| Reference comparisons (statistics) | `gsk_family.analysis.family_report` (`gsk-stats`) |

## Suite Coverage

| Suite | Python status | Notes |
|---|---|---|
| `sphere` | Implemented | Smoke-only deterministic minimization problem. |
| `cec2011` | Implemented | Native-dimension constrained / engineering-style problems through the Python adapter. |
| `cec2013` | Implemented | Packaged benchmark data and suite metadata. |
| `cec2013lsgo` | Implemented | Native-dimension large-scale global optimization suite. |
| `cec2017` | Implemented | Excludes F2 by default, as in common CEC2017 practice. |
| `cec2020` | Implemented | Uses packaged data and protocol metadata. |

## Shape Contract

The reference source passed loosely typed matrices; the Python adapter pins the
shapes down and validates them. Optimizers pass a two-dimensional population:

```text
(n_candidates, dimension)
```

The adapter returns a one-dimensional fitness vector:

```text
(n_candidates,)
```

This contract replaces the looser reference-source matrix conventions with
explicit validation (`as_population` / `as_fitness_vector`) while preserving the
same candidate-row semantics.

## Worked Mapping — one objective call

To evaluate one candidate for `cec2017` F1 at D=10:

- Reference source: call the suite's objective with a candidate matrix and the
  function number, via the compiled bridge.
- Python default path: build the problem with `make_problem("cec2017", 1, dim=10)`, then call
  `problem.evaluate(x)` where `x` has shape `(1, 10)`. The adapter validates the
  shape, dispatches to the bundled `cec_suite_python` data, and returns a `(1,)`
  vector.
The budget (`problem.max_nfes`), bounds (`problem.lb`/`problem.ub`), and optimum
(`problem.optimum`) that the reference source carried in separate structures are
all attributes of the single `BenchmarkProblem` object.

## Reference Table Use

Reference tables are used for validation, not as active runtime input. The
Python benchmark runtime evaluates objectives directly; validation compares
generated summary statistics to imported reference statistics after a run (see
[result_schema.md](result_schema.md) for the verdict format).

Committed reference tables currently exist for three suites only — `cec2017`,
`cec2013`, and `cec2011`, each carrying the full 7-optimizer GSK-family panel.
`cec2020`, `cec2013lsgo`, and `sphere` are implemented in code (the "Implemented"
rows above are code coverage, not reference coverage) but ship no reference
tables, so validation has nothing to compare against for them.

The same imported reference tables under `benchmarks/cec_reference_results/`
serve a second consumer: the statistical-analysis layer
(`gsk_family.analysis`, driven by `gsk-stats`) reads them as the family
comparison panel — every column, the proposed optimizer included, is loaded
reference-first, with locally reproduced runs as the fallback. So a reference
CSV can play two roles — a validation baseline for `gsk-validate` and a panel
column for the family Friedman/Wilcoxon report — without ever being fed to an
optimizer at runtime.
