# Benchmark Protocol

> **What this is.** The rules every benchmark suite follows: which functions and
> dimensions exist, how big the evaluation budget is, and how results are scored.
> **Who it is for.** Anyone choosing a suite to run, validating output, or adding
> a suite. **Prerequisites.** The terms in [the glossary](glossary.md) (function
> id, known optimum, budget). **After reading** you can pick a valid
> `(suite, function, dimension)` triple, predict its budget, and know whether its
> statistics are errors or raw objectives. The object that enforces these rules is
> `BenchmarkProblem` (see [api.md](api.md)).

All benchmark suites are accessed through the uniform `BenchmarkProblem`
contract, so an optimizer never imports a CEC module directly — it receives an
already-built problem. The metadata below comes from
`gsk_family.benchmark_adapter.protocol`.

## Supported Suites

```text
sphere
cec2011
cec2013
cec2013lsgo
cec2017
cec2020
```

`sphere` is a pure-Python smoke-test problem (used by tests and quick checks).
The CEC suites are provided by the bundled Python evaluator package:

- `benchmarks/cec_suite_python/`: Python/Numba evaluator used in normal `auto`
  mode.

The runner records both the requested backend (`auto` or `python`) and
the actual backend selected for each optimizer in `run_config.json`,
`phase0_protocol.json`, `environment.json`, and `profile.json` when profiling is
enabled.

## Function and Dimension Rules

Pick a function id from the suite's range and a dimension it allows. "Native"
means the dimension is fixed per function (you cannot choose it).

| Suite | Functions | Dimensions | Statistics |
| --- | --- | --- | --- |
| `sphere` | 1 | positive integer, default 10 | error vs optimum |
| `cec2011` | 1..22 | native per function | raw objective |
| `cec2013` | 1..28 | 10, 30, 50 (default; also accepts 2,5,10,20,30,40,50,60,70,80,90,100) | error vs optimum |
| `cec2013lsgo` | 1..15 | native per function | raw objective |
| `cec2017` | 1..30 | 10, 30, 50, 100 | error vs optimum |
| `cec2020` | 1..10 | 5, 10, 15, 20 | error vs optimum |

CEC2017 F2 is implemented but excluded from default comparisons because the
suite protocol marks it as non-default (its default function list is
`1, 3, 4, ..., 30`). Request it explicitly when needed, e.g.
`make_problem("cec2017", 2, dim=10)` or `--function 2` on the CLI.

The CEC2017 **scored set** is therefore the 29 functions `F1, F3-F30` evaluated
at `D = 10, 30, 50, 100`. F2 is widely reported as numerically unstable in high
dimension, so excluding it is standard CEC2017 practice and keeps the
statistical panel comparable to the published GSK-family tables. The
function-by-function equivalence of the Python evaluator against the C++
reference is documented in
[cec2017_cpp_python_equivalence_review.md](cec2017_cpp_python_equivalence_review.md)
(and the sibling per-suite review files).

`cec2013` is the paper's **second comparison suite**: the full 28 functions at
`D = 10, 30, 50` with 51 runs per cell, covered by the same 7-optimizer
reference panel as `cec2017` and `cec2011`.

## Evaluation Budgets

The budget is the maximum number of objective evaluations (`max_nfes`) per run.
Defaults:

- `sphere`: `10000 * D`
- `cec2011`: `150000`
- `cec2013`: `10000 * D`
- `cec2013lsgo`: `3000000`
- `cec2017`: `10000 * D`
- `cec2020`: `50000` for D5, `1000000` for D10, `3000000` for D15,
  `10000000` for D20

Use `max_nfes_override` in Python, or `--max-evaluations` / `max_evaluations`
from the runner, to create reduced-budget smoke or validation runs. An override
of `0` (or omitted) keeps the suite default.

Worked budgets for the dimension-scaled suites (`10000 * D`):

| Suite | D=10 | D=30 | D=50 | D=100 |
| --- | --- | --- | --- | --- |
| `cec2017` | 100000 | 300000 | 500000 | 1000000 |
| `cec2013` | 100000 | 300000 | 500000 | 1000000 |
| `sphere` | 100000 | 300000 | 500000 | 1000000 |

The native-dimension suites use fixed totals instead: `cec2011 = 150000` and
`cec2013lsgo = 3000000` per run, independent of the function's dimension. CEC2020
is the one suite whose budget is keyed to the chosen dimension rather than
`10000 * D` (see the per-dimension list above).

CEC2020 historically refused four cells — **F1 and F8 at D5 and D15** — via
`CEC2020_UNAVAILABLE_CELLS` (`benchmark_adapter/factory.py`) and
`_UNAVAILABLE_REFERENCE_CELLS` (`cec2020/functions.py`). Both sets are **empty
since 2026-07-26**; the history is kept here because the explanation went
through two corrections. The original docs said "missing shuffle marker files" —
loader-level true (the MEX-faithful loader opens a shuffle file for *every*
function as a per-dimension availability marker, and the official distribution
ships none for ids 1/22 at D5/D15) but math-level misleading, since only the
hybrids F5–F7 consume shuffle content. An interim correction here over-swung and
called the marker claim simply wrong. The complete account:

**RESTORED 2026-07-26.** The four cells were validated against the in-repo C++
oracle and the guard lifted. Method: the loader's missing files are pure
per-dimension availability MARKERS (the loader opens one for every function;
only hybrids consume the content), so the oracle was built with dummy markers
and its output proven bit-identical under two different marker contents.
Against it, F1/F8 at D5/D15 agreed with the Python suite to worst relative
error 1.258e-15 -- three orders inside the committed rel=1e-12 criterion --
with the already-trusted D10/D20 cells reproducing the same profile as
controls. The AGSK paper's own 5D tables always did include F1 and F8, so the
competition itself ran these cells. Pinned by
`tests/regression/test_cec2020_restored_cells.py`; the schedule now covers all
four dimensions, dropping only F6/F7 at D=5 (protocol-undefined).

Distinct from this, and permanent: **F6 and F7 are undefined at D5** by the
protocol itself (Yue et al. 2019 §2.1), enforced separately by
`CEC2020_PROTOCOL_EXCLUDED_CELLS`.

### Protocol Run Counts

The full campaign protocol uses **51 runs** per cell for `cec2017` and
`cec2013`, **25 runs** per cell for `cec2011` and `cec2013lsgo`, and **30 runs**
per cell for `cec2020` (Yue et al. 2019 §2.1, corroborated by the authors' own
`Adaptive_GSK_ALI.m`; corrected 2026-07-26 from an unsourced 25). The DT-GSK
ablation cells (`scripts/run_ablation.py`) default to 25 runs, the paper's
stated ablation design.

## Statistics Basis

Each suite reports either error-vs-optimum or raw objective values; this choice
decides what goes into the summary tables and curves. The classification is the
`ERROR_VS_OPTIMUM_SUITES` (`cec2013`, `cec2017`, `cec2020`) and
`RAW_OBJECTIVE_SUITES` (`cec2011`, `cec2013lsgo`) sets in
`benchmark_adapter.protocol`; `sphere` also reports error-vs-optimum as a
known-optimum smoke problem.

Suites with a known optimum report `error_vs_optimum`. For each run the error is
computed (in `gsk_family.stats.compute_error`) as the difference from the
optimum, then **floored to zero** once it falls below the suite's target:

```text
diff  = best_fitness - optimum
error = 0.0           if diff < target_error      (target_error is 1e-8 for the CEC suites)
        diff          otherwise
```

So a run that reaches the optimum within `1e-8` records an error of exactly `0`,
which is why solved functions show all-zero summary rows.

Raw-objective suites (`cec2011`, `cec2013lsgo`) report best objective values
directly, because the adapter exposes no unified optimum for them (their
`optimum` is `NaN` and `error` is reported as `NaN`).

### Worked walk-through — one CEC2017 cell

A concrete trace of the rules above for `cec2017`, function 5, D=30:

- Valid function? F5 is in `1..30` and is in the default list — yes.
- Valid dimension? D=30 is in `{10, 30, 50, 100}` — yes.
- Budget: `max_nfes = 10000 * 30 = 300000` evaluations per run.
- Statistics basis: `error_vs_optimum`, with `target_error = 1e-8`.
- A run ending at `best_fitness = optimum + 4.2e-9` records `error = 0.0`
  (below `1e-8`); a run ending at `optimum + 92.4` records `error = 92.4`.
- The summary row aggregates those per-run errors into Best/Median/Mean/Worst/SD.

Build the same problem in Python with
`make_problem("cec2017", 5, dim=30)`.

## Reference Comparisons

Imported reference evidence lives under:

```text
benchmarks/cec_reference_results/
```

Generated output lives under:

```text
results/_run_all/<optimizer>/<suite>/
```

Compare them with:

```powershell
gsk-validate --compare results/_run_all/gsk/cec2017 benchmarks/cec_reference_results
```

Reduced-budget runs are allowed to underperform full-budget references. The
verification step still checks for malformed values, impossible negative errors,
missing reference rows, and gross deviations when a full-budget comparison is
requested. The verdict and thresholds are detailed in
[result_schema.md](result_schema.md).

## Reference-Comparison Coverage

Reference summary tables under `benchmarks/cec_reference_results` carry the
full 7-optimizer GSK-family panel (`gsk`, `agsk`, `apgsk`, `fdb-agsk`,
`atmals-gsk`, `egsk`, `dt-gsk`) for **four** suites: `cec2017`, `cec2011`, and
`cec2013` (imported with the frozen primary release
`rel-2026-07-20-67d9345f9`), and `cec2013lsgo` (promoted 2026-07-28 from the
campaign staging banks as the separate, non-superseding release
`lsgo-rel-2026-07-28-ff1a046ef`; manifest
`papers/governance/evidence_release_manifest_cec2013lsgo.json`). The remaining
in-code suites (`cec2020` and `sphere`) ship **no** committed reference tables
yet — `cec2020`'s banks are promoted by the same tool
(`papers/scripts/promote_suite.py`) once its campaign passes the completeness
gate — so for those `gsk-validate --compare` finds no reference and reports
missing references rather than a consistency verdict.

## Benchmark Backend Policy

The default runner setting is `benchmark_backend=auto`. In that mode the runner
uses the Python/Numba evaluator. Selecting `benchmark_backend=python` records
the same evaluator choice explicitly; optimizer logic, seeds, fair starts,
evaluation budgets, summary schemas, and validation paths remain unchanged.

The related `benchmark_fp_mode` setting (`default`/`strict`, CLI
`--benchmark-fp-mode`) selects the CEC2017 evaluator's floating-point summation
order for the order-sensitive functions F1/F12/F13. It defaults to `default`
(the mode the committed references were produced under) and is a no-op for every
other suite. See [Floating-Point Regime Verification](fp_regime.md) for the full
contract.
