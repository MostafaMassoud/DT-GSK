# Result Schema

> **What this is.** Every file `gsk-run` writes, where it goes, and what each
> column or field means — with annotated samples from a real run. **Who it is
> for.** Anyone reading, parsing, validating, or archiving results. **Prerequisites.**
> Knowing roughly what a campaign is (see [workflows.md](workflows.md)) and the
> terms in [the glossary](glossary.md). **After reading** you can locate any
> output, read its values, and reproduce its exact formatting. The runner that
> emits these files is described in [api.md](api.md).

`gsk-run` writes generated experiment output under one tree per optimizer and
suite:

```text
results/_run_all/<optimizer>/<suite>/
  summary/
    <optimizer>_<suite>_D<dim>.csv
    per_run.csv
    seed_schedule.csv
    environment.json
    run_config.json
    phase0_protocol.json
    <optimizer>_D<dim>_log_<timestamp>.txt
    <optimizer>_D<dim>_runs_log_<timestamp>.txt
    verification.json
  curves/
    Figure_F<func>_D<dim>_Run#<run>.csv
    graphs/
      Figure_F<func>_D<dim>.png
  gen_logs/
    CheckpointErrors_<optimizer>_F<func>_D<dim>.csv
```

Generated output must not be written into `benchmarks/cec_reference_results`.
The runner enforces this guard (`ensure_output_root_allowed`) before creating
any files.

### The committed reference layout (flat)

The imported reference panel under
`benchmarks/cec_reference_results/<suite>/<optimizer>/` carries the same
artifact family in a **flat** layout — there is no `summary/` subdirectory:

```text
benchmarks/cec_reference_results/<suite>/<optimizer>/
  <optimizer>_<suite>_D<dim>.csv        per-dimension summary tables
  <optimizer>_cec2011.csv               all-functions rollup (cec2011 only)
  per_run.csv
  environment.json
  run_config.json
  seed_schedule.csv
  verification.json
  phase0_protocol.json
  curves/                               per-run convergence CSVs
  gen_logs/                             CheckpointErrors_*.csv
```

Rendered `curves/graphs/` PNGs and the `*_log_*.txt` reports are not committed
(both are regenerable). This tree is the paper's single source of truth: the
analysis loader (`analysis.result_loader.load_algorithm`) reads it first and
treats `results/_run_all/` as a fallback.

### A note on number formatting (preserved exactly)

These precisions mirror the upstream reference implementation byte-for-byte and
are intentional; do not "normalize" them:

| File | Field(s) | Format |
| --- | --- | --- |
| `per_run.csv` | `best_fitness`, `error` | `%.10e` (lowercase e) |
| `per_run.csv` | `runtime_seconds` | `%.6f` |
| summary `*_D<dim>.csv` | all statistics | `%.10E` (uppercase E, via `format_scientific`) |
| `curves/*.csv` | `BestError`, `Log10Error` | `%.16e` |
| `gen_logs/*.csv` | `E<checkpoint>` values | `%.16g` |

## Summary Table

The headline result for one dimension: one row per function with the across-runs
statistics.

`summary/<optimizer>_<suite>_D<dim>.csv`

```text
Function,Best,Median,Mean,Worst,SD
```

`SD` is the **sample** standard deviation (`ddof=1`). Statistics summarize error
values for suites with a known optimum and raw objective values for
raw-objective suites (see [benchmark_protocol.md](benchmark_protocol.md)).

Annotated real rows (`agsk_cec2017_D30.csv`):

```text
Function,Best,Median,Mean,Worst,SD
1,0.0000000000E+00,0.0000000000E+00,0.0000000000E+00,0.0000000000E+00,0.0000000000E+00
3,0.0000000000E+00,1.9364414817E-04,1.2422655464E-02,2.5224968236E-01,4.6246973086E-02
```

- `Function` — the suite function id (note F2 is absent: it is excluded by default).
- `Best`/`Worst` — smallest/largest error across the runs for that function.
- `Median`/`Mean` — central tendency across runs.
- `SD` — spread across runs. F1 here solved to error `0` on every run, so all
  five statistics are `0`.

## Per-Run Table

The raw record: one row per individual run, before any aggregation.

`summary/per_run.csv`

```text
optimizer,suite,function,dimension,run,seed,best_fitness,error,nfes,termination,runtime_seconds
```

Annotated real row (`agsk/cec2017/summary/per_run.csv`):

```text
agsk,cec2017,1,10,1,32240721,1.0000000001e+02,0.0000000000e+00,50484,target_error_reached,0.347855
```

| Column | Value here | Meaning |
| --- | --- | --- |
| `optimizer` | `agsk` | Optimizer id. |
| `suite` | `cec2017` | Benchmark suite. |
| `function` | `1` | Function id. |
| `dimension` | `10` | Problem dimension D. |
| `run` | `1` | Run index (1-based). |
| `seed` | `32240721` | The deterministic seed used (a bare integer). |
| `best_fitness` | `1.0000000001e+02` | Raw objective of the best point. |
| `error` | `0.0000000000e+00` | Target-zeroed error vs the optimum; `NaN` for raw-objective suites. |
| `nfes` | `50484` | Evaluations spent. Optimizers stop at `max_nfes` unless the target error is reached earlier. |
| `termination` | `target_error_reached` | Stop reason: `target_error_reached` or `max_evaluations`. |
| `runtime_seconds` | `0.347855` | Wall-clock time for the run (the only session-specific column; all others reproduce bit-for-bit). |

Every column except `runtime_seconds` is a deterministic function of the seed
schedule and reproduces bit-for-bit, so a regenerated `per_run.csv` matches the
committed reference in every field but that one. `runtime_seconds` is machine-
and session-specific by nature.

## Seed Schedule

The reproducibility ledger: the seed assigned to every cell and run, before the
run executes.

`summary/seed_schedule.csv`

```text
Dim,Function,Run,Seed
```

Unified-mode seeds are optimizer-independent for matching
`(dimension, function, run)` cells — that is what makes a fair start fair. The
exact seed formula is in [seed_policy.md](seed_policy.md).

## Compatibility Metadata

Three JSON files record the resolved settings and the reproducibility contract:
`run_config.json`, `phase0_protocol.json`, and `environment.json`. All three
preserve their authored key order; only `verification.json` and `profile.json`
are written with keys sorted alphabetically (see below).

`summary/run_config.json` captures the resolved campaign settings, including
optimizer id (`alg_name`), suite id, base seed, seed policy, seed strides
(`stride_run`/`dim_stride`/`func_stride`), requested functions (`funcs`),
excluded functions (`exclude_funcs`), the functions actually run
(`funcs_to_run`), dimensions, run count, statistics basis, the parallel flag
(`use_parallel`), the benchmark floating-point mode (`benchmark_fp_mode`; see
[fp_regime.md](fp_regime.md)), and the resolved optimizer options. It also
records `benchmark_backend` (the actual backend used for that optimizer) and
`benchmark_backend_requested` (the config selector, normally `auto`). The
resolved optimizer parameters are appended per optimizer by
`_run_config_optimizer_params`: for `gsk` that is `pop_size`/`KF`/`KR`/`K`/`P`,
for `agsk`/`apgsk`/`fdb-agsk` it is `NP_init`/`min_pop_size`, and for **`dt-gsk`
it is only `profile` (default `pub`)** alongside the (usually empty)
`optimizer_options` mapping. DT-GSK's core hyperparameters
(`np_init_mult = 5`, `n_min`, `KF = 0.5`, `KR = 0.9`, `Kexp = 10.0`) come from
the frozen `pub` profile in `DTGSKConfig` (`_dt_core.py`) rather than being
echoed into `run_config.json`; likewise the default-on **deep-stall full
restart** (`deep_stall_restart_enabled = True`) and its other `deep_stall_*`
fields stay internal to `DTGSKConfig` unless explicitly overridden through
`optimizer_options`.

`summary/phase0_protocol.json` captures the protocol-level reproducibility
contract: base seed, run/function/dimension strides, seed schedule policy block,
generator label, initial-population policy, dimensions, functions run, and a
`smoke` flag that is `true` for reduced-budget or small (`runs < 25`) campaigns.

`summary/environment.json` additionally records an `fp_regime` block: the
JIT-availability flag of every numba kernel module, the numba/llvmlite
versions, and a numeric **sentinel** (SHA-256 over fixed, thread-invariant
kernel-probe outputs). Every process in a campaign is verified against this
sentinel before running (`gsk_family.runners.fp_regime`), so a campaign runs in
one floating-point regime by construction; two campaigns are FP-comparable at
run level exactly when their sentinels match. Background:
[Floating-Point Regime Verification](fp_regime.md).

`summary/<optimizer>_D<dim>_log_<timestamp>.txt` is the readable per-dimension
summary report. It mirrors the console table with the detailed configuration
block, the best/median/mean/worst/SD/time statistics, and any available imported
reference-comparison table.

`summary/<optimizer>_D<dim>_runs_log_<timestamp>.txt` is the detailed per-run
audit log. It lists every run for the dimension's function cells with run id,
seed, best fitness, error, NFEs, termination reason, and runtime.

## Curves

The convergence history of one representative run per function/dimension cell.

`curves/Figure_F<func>_D<dim>_Run#<run>.csv`

```text
Eval,BestError,Log10Error
```

- `Eval` — cumulative evaluation count at the checkpoint.
- `BestError` — best-so-far value in the suite's statistics basis (`%.16e`).
- `Log10Error` — `log10(BestError)`, left blank when `BestError <= 0` or is non-finite.

The selected run is the run whose final value is nearest the **median** final
value for that function/dimension cell. When `--convergence-graphs` or
`convergence_graphs: true` is set, a best-effort PNG of the same curve is
written to `curves/graphs/Figure_F<func>_D<dim>.png` (a headless backend;
skipped silently if plotting is unavailable). Without that opt-in, the runner
writes the median-run curve CSV files only.

## Generation Logs

A coarse error-vs-budget table at fixed checkpoints, for every run in a cell.

`gen_logs/CheckpointErrors_<optimizer>_F<func>_D<dim>.csv`

Generation logs are written by default so a completed campaign includes the same
checkpoint-log artifact family as the reference-style result package. Use
`generation_logs: false` in YAML or `--no-generation-logs` on the CLI only for
temporary runs where those checkpoint tables are not needed.

```text
Run,Seed,E<c1>,E<c2>,...
```

Checkpoint columns correspond to evaluation checkpoints, each computed as
`max(1, round(max_nfes * fraction))` over these fractions:

```text
[0.01, 0.02, 0.03, 0.05, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
```

## Verification

The validation verdict: how the generated means compared with the imported
reference table.

`summary/verification.json` records the generated-vs-reference comparison when a
matching reference summary table is available. It is written **with keys sorted
alphabetically**. A real file (`agsk/cec2017/summary/verification.json`):

```json
{
  "failures": [],
  "functions_checked": 116,
  "generated_dir": "results\\_run_all\\agsk\\cec2017",
  "hard_failures": 0,
  "missing_reference": 0,
  "optimizer": "agsk",
  "reduced_budget": false,
  "reference_root": "benchmarks\\cec_reference_results",
  "suite": "cec2017",
  "thresholds": {
    "gross_factor": 1000000.0,
    "negative_error_floor": -1e-06,
    "reference_trivial_floor": 1e-08
  },
  "verdict": "CONSISTENT",
  "win_tie_loss": [
    0,
    116,
    0
  ]
}
```

Here every function is a tie (`[0, 116, 0]`) because the promoted `agsk`
reference is verified against itself — the regenerated run reproduces the
committed table exactly. An optimizer sensitive to the benchmark-arithmetic
residual can instead record a few wins/losses (the committed `gsk` file, for
example, shows `[2, 113, 1]`). The `116` is the 29 scored functions across the
four dimensions (`29 * 4`).

| Field | Meaning |
| --- | --- |
| `verdict` | `DEVIATES` when there are hard failures; `NOT_VERIFIED` when no hard failure exists but not a single function could be compared because no reference rows exist (`functions_checked == 0` with `missing_reference > 0`); otherwise `CONSISTENT`. A suite without a committed reference bank (`cec2020`, `cec2013lsgo`, `sphere`) therefore reports `NOT_VERIFIED`, never a vacuous `CONSISTENT`. |
| `reason` | `"NO_REFERENCE"` accompanies a `NOT_VERIFIED` verdict; `null` otherwise. |
| `reduced_budget` | `true` when the run used a reduced budget or `runs < 25`. |
| `functions_checked` | Function rows with both a generated and a reference mean. |
| `hard_failures` | Count of hard failures (see below); drives the verdict. |
| `win_tie_loss` | Generated mean better / equal / worse than reference, as `[wins, ties, losses]`. |
| `missing_reference` | Generated rows with no matching reference mean (not a hard failure). |
| `thresholds` | The numeric thresholds applied. |
| `failures` | Per-finding detail records (empty when none). |
| `generated_dir`, `reference_root` | The two directories compared. |

Missing reference rows are reported but are not hard failures. Hard-failure
checks are: non-finite generated statistics, impossible negative errors for
known-optimum suites, and gross full-budget deviation from non-trivial reference
means (`generated mean > 1e6 * |reference mean|`). Reduced-budget runs suppress
the gross-deviation hard failure because short runs are expected to underperform
published full-budget tables.

Standalone comparison (re-writes this file beside the run):

```powershell
gsk-validate --compare results/_run_all/gsk/cec2017 benchmarks/cec_reference_results
```

## Profile

Optional diagnostic timing, written only when requested.

When `gsk-run` is called with `--profile` or config `profile: true`, it writes
`summary/profile.json` (keys sorted alphabetically). The file contains:

- parallel mode, backend, and worker count;
- benchmark backend requested/selected fields;
- tasks dispatched / completed / skipped or failed;
- benchmark warmup records when warmup is enabled;
- optimizer-reported runtime for each run.

Profile timings are diagnostic, not exact-replay artifacts.

## Statistical Analysis Outputs

`gsk-stats` does not write into a per-optimizer tree; it writes the cross-optimizer
comparison under a shared analysis root (suite lowercased):

```text
results/_run_all/_analysis/<suite>/
  <suite>_statistical_report.txt      concatenated per-dimension text report
  <suite>_friedman_ranks.csv          Friedman mean ranks per dimension
  <suite>_friedman_ranks.tex          Friedman mean-rank LaTeX table
  <suite>_wilcoxon_summary.tex        pairwise Wilcoxon + A12 + Holm LaTeX table
  figures/
    nemenyi_cd_<suite>_D<dim>.png     Nemenyi critical-difference diagram
    friedman_ranks_<suite>_D<dim>.png mean-rank bar chart
```

The panel compares the **proposed** `dt-gsk` against the six committed
GSK-family comparators (`gsk`, `agsk`, `apgsk`, `fdb-agsk`, `egsk`,
`atmals-gsk`). All seven columns — the proposed included — are loaded
reference-first from `benchmarks/cec_reference_results/<suite>/`; a locally
reproduced run under `results/_run_all/` is only a fallback for cells the
reference tree does not carry. The `.tex` and figure artifacts are written only when a Friedman panel
could be formed (enough comparators have data for that dimension); pass
`--no-figures` to skip the PNGs. Override the destination with `--out`. The full
method and a column-by-column reading of these files are in
[research/statistical_analysis.md](../research/statistical_analysis.md).

When a campaign is run with `gsk-run --stats`, an equivalent per-dimension
Wilcoxon + Friedman summary is streamed to the console live (and folded into the
per-dimension `*_log_<timestamp>.txt` report); it covers the adaptive optimizers
only and skips vanilla `gsk` and the native-dimension `cec2011` suite.
