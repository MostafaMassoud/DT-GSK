# User Guide

> **What this page is.** The everyday command reference for running the GSK
> family project from Python: install, inspect, run, validate, and find your
> results.
> **Who it is for.** Anyone who has the repository checked out and wants to use
> it — no prior knowledge of the algorithms required.
> **After reading**, you will be able to install the package, run a smoke
> experiment, run a single benchmark cell, validate output against reference
> tables, and locate every file the runner writes.
> **Prerequisites:** Python 3.10–3.13 and the repository checked out. New to the
> concepts? Read the [Explainer](explainer.md) first. Want a guided first run?
> Use the [Tutorial](tutorial.md). For a bare command list, see the
> [Runbook](runbook.md).

This guide covers normal Python use. The upstream reference runtime, CMake, and
any compiled bridge are **not** part of the normal Python workflow and are not
needed here.

A note on commands: examples use PowerShell, which is the project's primary
shell on Windows. They work the same in other shells. The canonical entry point
is `python run.py`, which adds `src/` to the import path; once the package is
installed (next section) the console commands `gsk-run`, `gsk-list`, and
`gsk-validate` are equivalent and shorter.

## Install

Install the package in editable mode (so code edits take effect immediately),
then run the tests to confirm the environment is healthy. Run both from the
project root.

```powershell
python -m pip install -e ".[dev]"
```

```powershell
python -m pytest
```

A healthy run ends with a `passed` summary line. If `gsk-run` is later reported
as "not found", see [Troubleshooting](troubleshooting.md#gsk-run-is-not-found).

## Inspect available assets

Before running anything, list what the package offers — optimizers, benchmark
suites, and how many imported reference tables are present.

```powershell
gsk-list --optimizers --benchmarks --references benchmarks/cec_reference_results
```

What you'll see (shape, not exact counts):

```text
optimizers:
  gsk
  agsk
  apgsk
  atmals-gsk
  egsk
  fdb-agsk
  dt-gsk
benchmarks:
  cec2011
  cec2013
  cec2013lsgo
  cec2017
  cec2020
smoke problems:
  sphere
references:
  cec2011: 441 csv files
  cec2013: 1211 csv files
  cec2017: 1666 csv files
```

The `references:` block lists only the suites that carry committed reference
evidence — currently `cec2011`, `cec2013`, and `cec2017`, the three suites the
statistical panel actually reads. Underscore-prefixed companion releases under
the reference root (`_ablation`, `_paper_tables`) are intentionally skipped, and
the per-suite counts grow as more evidence is promoted, so treat them as a
present/absent signal rather than exact figures.

Six of the seven **runnable** optimizers (the seventh, `egsk`, is described below):

| Id | Name | Notes |
|---|---|---|
| `gsk` | Baseline Gaining-Sharing Knowledge | The unadapted reference algorithm; the live `--stats` panel uses it as the baseline anchor and skips it. |
| `agsk` | Adaptive GSK | Adaptive parameter pools + linear population-size reduction (LPSR). |
| `apgsk` | Adaptive-parameters GSK | Adaptive `kf`/`kr` pools with probability-matching. |
| `atmals-gsk` | GSK with adaptive memory and local search | Optional local-search refinement; reads a `protocol` option. |
| `fdb-agsk` | AGSK with fitness-distance-balance donor selection | FDB donor selection on top of AGSK. |
| `dt-gsk` | Dimension-Tiered Gaining-Sharing Knowledge | **This project's proposed method**; dimension-aware "pub" profile with adaptive configuration selection, nonlinear population reduction, an interaction-structure memory, and a default-on deep-stall full restart. On CEC2017 (51 runs, 29 scored functions, F2 excluded) it attains the best **descriptive** family mean rank — first at D10/D50/D100, second at D30 behind the strong `egsk` baseline — with Holm-corrected separation from `egsk` only at D10, and the D50/D100 first places resting in part on the NP = 5D population rule. See [DT-GSK](../algorithms/dt-gsk.md). |

A seventh family member, `egsk`, is now a runnable optimizer too
(`gsk-run --optimizer egsk` works); it is a faithful MATLAB port whose only
deviation is the interior-point refinement (`scipy.optimize.minimize` with
`method="SLSQP"` in place of MATLAB `fmincon`), validated as statistically
equivalent to the MATLAB `fmincon` reference. The 7-algorithm statistical panel
and review pack report `egsk`'s cells from the committed `scipy`-SLSQP port run
(the comparator of record).

The benchmark suites are `cec2017`, `cec2011`, `cec2020`, `cec2013`,
`cec2013lsgo`, and the simple `sphere` smoke problem. See the
[Benchmark Protocol](../reference/benchmark_protocol.md) for each suite's
dimensions, function counts, and evaluation budgets. For CEC2017 the scored set
excludes the withdrawn F2 (functions F1 and F3-F30) across D=10/30/50/100.

## Run an experiment

There are two ways to run: a **YAML config** (preferred for repeatable
campaigns) or **direct CLI flags** (handy for a one-off cell). Both build the
same in-memory `ExperimentConfig`. Every run uses the **process** backend in
parallel by default; you never need to pass `--parallel` or `--workers` for a
normal run. (The bundled smoke and validation configs are the exception —
`configs/smoke.yml` turns parallelism off entirely, and the other demonstration
configs pin the lightweight `thread` backend with two workers for small,
deterministic gate runs.)

### The quickest smoke run (YAML)

```powershell
gsk-run --config configs/smoke.yml --root .
```

`--root .` rewrites the config's relative paths (`output_root`,
`reference_root`, `data_root`) under the current project root, so a config can
move between machines. `configs/smoke.yml` runs one optimizer on one CEC2017
cell at a tiny budget.

What you'll see (abridged — one optimizer, one function):

```text
==================== run_all (CEC2017) ====================
suite=cec2017  functions=[1]  dims=10  runs=1  seed_policy=unified  rng=threefry  fp=default  backend=auto->python  parallel=0

----- [1/1] GSK -----
Numba: available v0.xx | suite JIT=enabled | threads=... (mode=..., before=...)

========================================================================
DETAILED CONFIGURATION
========================================================================
optimizer       : gsk
suite           : CEC2017
funcs_to_run    : [1]
...
========================================================================

+----------------------------------------------------------+
| gsk - CEC2017 - D=10                                      |
+----------------------------------------------------------+
| 1 functions x 1 runs | Budget: 1,000 NFEs                |
...
+--------+--------------+--------------+--------------+--------------+--------------+-------------+
|  Func  |     Best     |    Median    |     Mean     |    Worst     |      SD      |   Time/s    |
+--------+--------------+--------------+--------------+--------------+--------------+-------------+
|  F01   |   ...e+00    |   ...e+00    |   ...e+00    |   ...e+00    |   ...e+00    |      ...s   |
+--------+--------------+--------------+--------------+--------------+--------------+-------------+

[OK] Updated 1 function(s); wrote 1 new run(s)
```

(`parallel=0` appears here because `configs/smoke.yml` sets `parallel: false`
for a deterministic single-thread smoke; the default for runs you start without
that line is parallel.)

### A direct single-cell run

```powershell
gsk-run --optimizer gsk --suite cec2017 --dimension 10 --function 1 --runs 1 --seed 20240620 --max-evaluations 1000 --overwrite
```

`--max-evaluations 1000` is a deliberately small budget so the run finishes
quickly; `--overwrite` replaces any existing rows for the same cell. Output
lands under the default `results/_run_all` tree described in
[Output locations](#output-locations). Each flag
maps to a config field — see [Configuration](configuration.md) for the full
list and the YAML equivalents.

### Run all optimizers at once

```powershell
gsk-run --config configs/all_optimizers_smoke.yml --root .
```

This config runs five optimizers (`gsk`, `agsk`, `apgsk`, `atmals-gsk`,
`fdb-agsk`) on the `sphere` smoke problem and adds warmup and profile metadata.
It is parallel, and (being a tiny demonstration config) it sets the lightweight
`thread` backend with two workers rather than the process default. The console
header shows `----- [1/5] GSK -----`, `----- [2/5] AGSK -----`, and so on.

This shipped smoke config deliberately omits `egsk` and the proposed `dt-gsk`
to stay fast; to exercise the full seven-optimizer family, name them explicitly
on the CLI, for example
`gsk-run --optimizer gsk,agsk,apgsk,fdb-agsk,atmals-gsk,egsk,dt-gsk --suite cec2017 ...`
(see the [Runbook](runbook.md#cec2017-all-optimizers) for the full-sweep form).

Console progress logging is on by default. A long CEC campaign prints the
campaign banner, each optimizer's dispatch and detailed configuration, the
per-function summary table, finalization progress bars while reports and
metadata are written, and a final summary. Pass `--quiet` only when an automated
pipeline should suppress progress output.

### Forcing a serial run

For step-through debugging or a strict single-thread reproducibility check, turn
parallelism off:

```powershell
gsk-run --config configs/all_optimizers_smoke.yml --root . --serial
```

## Validate results

Validation compares a generated run tree against the imported reference tables
and prints a verdict.

```powershell
gsk-validate --compare results/_run_all/gsk/cec2017 benchmarks/cec_reference_results
```

What you'll see:

```text
verdict: CONSISTENT
functions_checked: ...
hard_failures: 0
missing_reference: ...
win_tie_loss: .../.../...
```

The exit code is non-zero when the verdict is `DEVIATES` or when no comparable
functions were found, which makes the command usable in scripts.

**Reduced-budget runs will not reproduce full-budget reference statistics.** Read
their comparison as a consistency and schema check, not a paper-quality
benchmark claim. The fields above and the comparison rules are documented in the
[Result Schema](../reference/result_schema.md) and
[Benchmark Protocol](../reference/benchmark_protocol.md).

## Statistical analysis

`gsk-stats` builds the paper-grade GSK-family comparison: Friedman ranks,
Nemenyi critical-difference, pairwise Wilcoxon + Holm correction,
Vargha-Delaney A12 effect sizes, win/tie/loss, LaTeX tables, and CD/rank
PNGs (BCa bootstrap intervals come from the separate papers pipeline under
`papers/scripts/`, not this command). It works out of the box from the
committed reference panel; generated runs are only needed for cells the
reference tree does not carry.

```powershell
gsk-stats --suite CEC2017 --dims 10,30,50,100
gsk-stats --suite CEC2011
gsk-stats --suite CEC2013 --dims 10,30,50
```

CEC2013 (28 functions, dims 10/30/50, 51 runs) is the second comparison suite
alongside CEC2017; CEC2011 (22 real-world problems, native dims, 25 runs)
completes the trio. The 7-algorithm panel compares the six reference comparators
(`gsk`, `agsk`, `apgsk`, `fdb-agsk`, `egsk`, `atmals-gsk`) against the proposed
`dt-gsk` (override with `--proposed`). Every algorithm — the proposed `dt-gsk`
included — is read **reference-first** from
`benchmarks/cec_reference_results/<suite>/<optimizer>/`; a locally reproduced
run under `results/_run_all/` is only a fallback for cells the reference tree
lacks. Outputs land under
`results/_run_all/_analysis/<suite>/`. Add `--no-figures` to skip the PNGs, or
`--alpha 0.01` to tighten the significance level. See
[Statistical Analysis](../research/statistical_analysis.md) for the full method.

To watch the per-dimension Wilcoxon + Friedman analysis stream **live during a
run**, add the opt-in `--stats` flag (off by default; the live panel skips the
`gsk` baseline; the native-dimension `cec2011` suite emits a single per-suite
panel instead of per-dimension ones):

```powershell
gsk-run --optimizer dt-gsk --suite cec2017 --dimension 10 --dimension 30 --stats
```

## Paper review pack

To assemble the single-PDF advisor review pack from a reproduced DT-GSK run
plus the committed comparator checkpoints:

```powershell
python papers/scripts/generate_review_pack.py
```

This writes `papers/DT-GSK-CEC2017-review.pdf` using matplotlib `PdfPages` (no
LaTeX required): a headline dashboard, 7-algorithm mean tables, and 7-algorithm
convergence grids (GSK, AGSK, APGSK, FDB-AGSK, eGSK, ATMALS-GSK, DT-GSK).
Missing curves are never fabricated — they are skipped on the plot and listed in
`papers/DT-GSK-CEC2017-review_missing.log`. See
[papers/README.md](../../papers/README.md) for the full layout.

## Output locations

Generated results are written under one root, keyed by optimizer and suite:

```text
results/_run_all/<optimizer>/<suite>/
  summary/
  curves/
  gen_logs/
```

| Folder | Holds |
|---|---|
| `summary/` | Per-run table, per-dimension summary CSVs, seed schedule, environment/config JSON, validation verdict, text logs. |
| `curves/` | One convergence-trace CSV per (function, dimension) cell (the median run), plus rendered `graphs/*.png` when `--convergence-graphs` / `convergence_graphs: true` is used. |
| `gen_logs/` | Per-checkpoint generation-log CSVs (`CheckpointErrors_*`). |

Imported reference evidence stays read-only here:

```text
benchmarks/cec_reference_results/
```

The runner refuses to write generated output into the imported reference tree.
For the exact filenames and CSV columns, see the
[Result Schema](../reference/result_schema.md).

## Documentation artifacts

Build the browsable HTML documentation:

```powershell
python scripts\build_docs_html.py
```
