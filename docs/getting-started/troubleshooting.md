# Troubleshooting

> **What this page is.** Fixes for the problems newcomers hit most: install,
> benchmark data, output paths, reference mismatches, and parallel-execution
> hiccups.
> **Who it is for.** Anyone whose run did not behave as the
> [Tutorial](tutorial.md) or [User Guide](user_guide.md) describes.
> **After reading**, you will be able to diagnose and resolve the common
> failures, and know which reference page to consult for the rest.
> **Prerequisites:** none. Terms used here are defined in the
> [Glossary](../reference/glossary.md).

Find your symptom in the table, then jump to the section.

| Symptom | Section |
|---|---|
| `gsk-run: command not found` | [gsk-run is not found](#gsk-run-is-not-found) |
| Benchmark data fails to load | [Benchmark data cannot be loaded](#benchmark-data-cannot-be-loaded) |
| Output path rejected | [Output root is rejected](#output-root-is-rejected) |
| Results land under `<suite>/<opt>/<suite>/` | [Output lands in a doubled suite path](#output-lands-in-a-doubled-suite-path) |
| Validation reports mismatches | [Reference comparison reports mismatches](#reference-comparison-reports-mismatches) |
| Parallel and serial disagree | [Parallel and serial results differ](#parallel-and-serial-results-differ) |
| `BrokenProcessPool` / worker dies | [A worker process dies or the pool breaks mid-run](#a-worker-process-dies-or-the-pool-breaks-mid-run) |
| Worker import errors (Windows) | [Worker import errors on Windows](#worker-import-errors-on-windows) |
| First run slow / Numba unavailable | [First run is slow or Numba is unavailable](#first-run-is-slow-or-numba-is-unavailable) |
| `gsk-stats` empty / `--stats` prints nothing | [Statistical analysis produces no output](#statistical-analysis-produces-no-output) |
| Review pack PDF missing curves | [The review pack skips curves](#the-review-pack-skips-curves) |

## `gsk-run` Is Not Found

The console commands appear only after the package is installed. Install it in
editable mode from the project root:

```powershell
python -m pip install -e ".[dev]"
```

Then reopen the shell if your environment does not refresh console scripts
automatically. As a fallback that needs no install, run `python run.py ...` from
the project root -- it adds `src/` to the import path and accepts the same flags
as `gsk-run`. The sibling scripts `gsk-list`,
`gsk-validate`, and `gsk-stats` also have `python -m gsk_family.cli.<name>`
equivalents (for example `python -m gsk_family.cli.validate ...`), but unlike
`python run.py` these need the package to be importable: run them after the
editable install completes, or set `PYTHONPATH=src` from the project root.

## Benchmark Data Cannot Be Loaded

The runner could not find the benchmark data files. Check that `data_root`
points at:

```text
benchmarks/cec_suite_python
```

When using YAML, prefer rooting paths to the current project:

```powershell
gsk-run --config configs/smoke.yml --root .
```

`--root .` rewrites relative `data_root`, `reference_root`, and `output_root`
inside the current project, which avoids stale absolute paths from another
machine.

## Output Root Is Rejected

This is a safety guard, not a bug. The runner refuses to write generated results
inside the imported reference tree:

```text
benchmarks/cec_reference_results
```

Point `output_root` at `results/` or another generated-output directory.
Keeping generated and reference evidence separate is intentional -- see
[Why reference tables are read-only](explainer.md#why-reference-tables-are-read-only).

## Output Lands In A Doubled Suite Path

The runner always appends `<optimizer>/<suite>/` to `output_root`. If you point
`output_root` at a directory that is *itself* a suite folder (for example
`.../my_results/cec2017`), the suite name is appended again and the results
land in a doubled `cec2017/<optimizer>/cec2017/` tree — which downstream
analysis then fails to find. Point `output_root` at the tree that **contains**
the suite folders instead:

```yaml
# correct  -> <output_root>/<optimizer>/cec2017/...
output_root: results/my_campaign
# WRONG    -> results/my_campaign/cec2017/<optimizer>/cec2017/...
# output_root: results/my_campaign/cec2017
```

If a doubled tree already exists, move the inner `<optimizer>/<suite>/` content
up to the intended `<root>/<optimizer>/<suite>/` location and delete the empty
shell before re-running analysis.

## Reference Comparison Reports Mismatches

First, check the budget. **Reduced-budget runs are valid smoke tests but are not
expected to reproduce full reference statistics** (see the
[Validation Report](../research/validation_report.md)). A `DEVIATES` verdict on a
reduced run usually means "too few evaluations", not "wrong".

If the budget is full, confirm you are comparing like with like: the same suite,
function ids, dimensions, optimizer id, and statistics basis on both sides. The
comparison rules and fields are in the
[Result Schema](../reference/result_schema.md).

## Parallel And Serial Results Differ

Parallel execution should use the **same seed schedule** as serial execution, so
matching runs should match. If they differ, verify that:

- `seed` is fixed;
- `seed_policy` is fixed;
- `overwrite` did not merge old and new rows;
- the same config file was used for both runs.

A clean way to compare is to run the same config once normally and once with
`--serial` (see the [User Guide](user_guide.md#forcing-a-serial-run)) and diff
the deterministic artifacts.

One known exception is thread count rather than seeding: `dt-gsk` at `D >= 50`
runs `prange` kernels whose floating-point reduction order follows the active
Numba thread count, and parallel runs auto-cap Numba threads while serial runs
keep the default. Pass `--numba-threads 1` to both runs to remove this
divergence source; for strict byte-identity, export the six thread-pinning
environment variables before Python starts and use `--serial` — see
[Determinism at D 50 and above](../development/dt_gsk_core_reference.md#determinism-at-d-50-and-above).

## A Worker Process Dies Or The Pool Breaks Mid-Run

The default backend runs each function on a pool of spawned worker processes. If
a worker dies (an intermittent JIT/spawn crash, or out-of-memory pressure), the
pool can raise `BrokenProcessPool`. The runner handles this automatically: it
tears the pool down and rebuilds it, retrying the affected function up to three
times. If failures persist, it runs that function on the reliable serial backend
and then rebuilds a fresh pool for the next function.

CEC suites use Numba/LLVM kernels, and CEC2017 composition functions `F21`-`F30`
can compile a large amount of LLVM code the first time they run in spawned
workers. The automatic worker count is intentionally small (2 workers on
machines with at least two logical cores, otherwise 1), and automatic CEC2017
composition cells retain an upper cap of 8 workers. This is meant to prevent
noisy `LLVM ERROR: out of memory` crashes in copied campaign commands. If you
explicitly pass `--workers N`, the runner treats that as your chosen
memory/speed tradeoff and records it in the metadata.

The runner never falls back to the thread backend, by design: the parallel
benchmark kernels can deadlock when called from many Python threads, which would
turn a recoverable crash into a hang.

If you keep hitting this, you can:

- re-run the campaign; already completed cells resume from `per_run.csv` as long
  as `--overwrite` is omitted;
- force serial execution with `--serial`;
- reduce memory pressure by lowering the worker count with `--workers N`.

## Worker Import Errors On Windows

The process backend uses the `spawn` start method, which re-imports the package
inside every worker process. If workers fail to start with import errors, run
from the project root so `gsk_family` is importable there. Install the package
in editable mode (or install the requirements) as described in the README, and
avoid placing run code where importing the module triggers side effects, since
the import runs once in each spawned worker.

## First Run Is Slow Or Numba Is Unavailable

The benchmark kernels are JIT-compiled by Numba on first use, so the first run
of a session pays a one-time compilation cost before the timed work begins. The
warmup step hides most of this, but the very first call is still slower than
later ones.

At startup the runner prints a Numba line reporting whether Numba is available,
its version, and the active thread count. If Numba is unavailable, the runner
refuses to run: the floating-point-regime gate raises `FPRegimeError` instead of
silently falling back to the pure-Python (NumPy) kernels, whose results are
deterministic but not bit-identical to the published fully-JIT runs. Reinstall
the requirements to restore a working Numba and re-run. Background on the JIT
and thread-capping is in [Performance](../research/performance.md); the gate
itself is documented in the
[FP Regime reference](../reference/fp_regime.md).

## Statistical Analysis Produces No Output

`gsk-stats` and the live `--stats` panel both read generated per-dimension
summary CSVs and the matching reference tables. If the report is empty or a run
prints `[stats] skipped statistical analysis ...`, check these in order:

- **The proposed optimizer's cells exist in some source.** `gsk-stats` reads
  the proposed method **reference-first** from
  `benchmarks/cec_reference_results/<suite>/<proposed>/<proposed>_<suite>_D<dim>.csv`,
  falling back to `results/_run_all/<proposed>/<suite>/summary/` only for cells
  the reference tree lacks. The default `dt-gsk` ships in the committed reference
  tree, so the panel builds out of the box. Empty output means *neither* source
  carries the proposed optimizer for the requested cells — for example a custom
  `--proposed` id you have not run yet, or a suite/dimension outside the committed
  set. Run that optimizer (or choose a covered cell) first.
- **The reference tree is present.** The comparison reads
  `benchmarks/cec_reference_results/<suite>/`; point `--reference-root` at it if
  it lives elsewhere.
- **Dimensions match.** `--dims 10,30,50,100` must name dimensions you actually
  ran. A dimension with no generated CSV is silently absent from the panel.
- **The live `--stats` flag deliberately skips the vanilla baseline.** By
  design it prints nothing for the vanilla `gsk` optimizer. Every suite is
  covered: fixed-dimension suites print one panel per dimension, and the
  native-dimension `cec2011` suite prints a single per-suite panel once its
  `<opt>_cec2011.csv` rollup is on disk. Add `--stats` to a different optimizer
  (for example `dt-gsk`) to see live output. This is expected behaviour, not a
  bug. See [Statistical Analysis](../research/statistical_analysis.md).

## The Review Pack Skips Curves

`python papers/scripts/generate_review_pack.py` reads checkpoint CSVs for all
seven algorithms. When a curve is unavailable it is **never fabricated**: the
plot cell is left empty and the missing entry is recorded in
`papers/DT-GSK-CEC2017-review_missing.log`. Open that log to see exactly which
`(algorithm, function, dimension)` curves are absent, then generate the missing
dt-gsk runs (comparator curves come from the committed
`benchmarks/cec_reference_results/<suite>/<alg>/gen_logs/` tree and should
already be present). See [papers/README.md](../../papers/README.md) for the
expected inputs.
