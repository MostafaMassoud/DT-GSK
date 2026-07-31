# Workflows

> **What this is.** The main paths data takes through the project: running a
> campaign from the CLI, running one optimizer from Python, validating output,
> and rebuilding the docs. **Who it is for.** Anyone who wants
> the big-picture flow before diving into a specific module. **Prerequisites.** A
> working install; the terms in [the glossary](glossary.md). **After reading**
> you will know which entry point to use for which job and have one worked
> end-to-end example. For the symbol-level API see [api.md](api.md); for the
> files produced see [result_schema.md](result_schema.md).

This document describes the main execution paths through the Python project.
Each path is sketched as a numbered flow; read the arrows top to bottom.

## CLI Experiment Workflow

The everyday path: `gsk-run` turns a request (YAML or flags) into a fixed,
reproducible set of runs and writes the full result tree.

```text
gsk-run
  -> parse YAML or direct CLI arguments
  -> ExperimentConfig                       (normalized, frozen request)
  -> resolve suite functions and dimensions (the run "cells")
  -> create deterministic seed schedule      (one seed per cell+run)
  -> create fair-start populations           (when using unified seeds)
  -> construct BenchmarkProblem cells
  -> call optimizer.optimize                 (process pool by default)
  -> write per-run rows, summaries, curves, logs, environment, profile
  -> optionally compare with reference tables (verification.json)
```

The same path is used by smoke tests and full benchmark campaigns; only the
budget and run count differ. The default backend is a **process** pool with an
automatic worker policy. Runbooks still show `--parallel --workers 2` explicitly
for full campaigns so copied commands are safe on shared machines.
Command-line flags and YAML keys are in the
[configuration guide](../getting-started/configuration.md).

## Python API Workflow

The focused path: call one optimizer directly, with no files written. Best for
tests and quick algorithm experiments.

```python
from gsk_family.benchmark_adapter.factory import make_problem
from gsk_family.optimizers.gsk import optimize
from gsk_family.types import OptimizerOptions

problem = make_problem("sphere", 1, dim=4, max_nfes_override=120)
result = optimize(problem, OptimizerOptions(seed=20240620))
```

Use the direct API when artifacts, fair starts, summaries, and validation are
not needed. Use the runner (next section) when they are. The result object's
fields are documented in
[python_optimizer_interface.md](python_optimizer_interface.md).

## Worked End-to-End Example

This runs a small but complete campaign through the runner, then validates it —
the same two commands a reviewer would use, just with a reduced budget so it
finishes in seconds.

```powershell
# 1. Run: gsk on cec2017, functions 1 and 3, D=10, 3 runs, reduced budget.
gsk-run --optimizer gsk --suite cec2017 --function 1,3 --dimension 10 --runs 3 --max-evaluations 2000

# 2. Inspect the tree that was written.
#    results/_run_all/gsk/cec2017/summary/  curves/  gen_logs/

# 3. Validate the generated summaries against the bundled references.
gsk-validate --compare results/_run_all/gsk/cec2017 benchmarks/cec_reference_results
```

What happens, step by step:

1. `gsk-run` builds an `ExperimentConfig`, resolves the cells
   `(F1, D10)` and `(F3, D10)`, and fixes a seed schedule.
2. Because the seed policy is `unified` (the default), it draws one shared
   initial population per cell so every optimizer would start identically.
3. It runs the 2 cells (`F1·D10` and `F3·D10`) at 3 runs each — `3 x 2 = 6`
   run tasks — which the runner dispatches; the process pool only engages when
   the task count exceeds the worker count, so for so few tasks the runner may
   stay in-process (see the "Parallel Workflow" note below). Either way it
   writes `per_run.csv`, the per-dimension summary CSV, median-run curve CSVs,
   optional convergence graph PNGs, checkpoint logs, `environment.json`, and
   `verification.json`.
4. `gsk-validate --compare` reloads the generated summaries, finds the matching
   reference rows, compares means, and (re)writes `verification.json` beside the
   run, printing a one-line `verdict`.

Because `--max-evaluations` is set, the run is flagged as reduced-budget, so the
validation step will not treat underperformance against full-budget reference
tables as a failure. Drop `--max-evaluations` and raise `--runs` for a full
campaign. The artifacts are detailed in [result_schema.md](result_schema.md).

## Validation Workflow

The audit path: compare a finished run to imported reference tables, or just
check that reference assets are present.

```text
gsk-validate --compare <generated-run-dir> <reference-root>
  -> load generated environment and summary CSV files
  -> find matching reference tables
  -> compare function-level summary statistics (means)
  -> write verification.json beside the generated run tree
  -> print verdict / functions_checked / hard_failures / win_tie_loss
```

`--verify` is an alias for `--compare`. With no `--compare`, `gsk-validate
--references <root>` simply reports how many comparator CSVs exist under a
reference root. Reduced-budget runs are marked so reference comparison does not
pretend to be full reference-replay evidence; force the interpretation with
`--reduced` or `--full`. The verdict values and thresholds are explained in
[result_schema.md](result_schema.md).

## Statistical Analysis Workflow

The comparison path: turn finished summary tables into the GSK-family
statistical verdict (ranks, significance, effect sizes, figures). Validation
(above) asks "does this run match its reference?"; analysis asks "how does the
proposed optimizer rank against the whole family?".

```text
gsk-stats --suite CEC2017 --dims 10,30,50,100
  -> load per-function means for all 7 panel optimizers, reference-first,
     from benchmarks/cec_reference_results/<suite>/
  -> fall back to results/_run_all/<opt>/<suite>/summary/ only for cells
     the reference tree does not carry
  -> per dimension: Friedman ranks over the 7-algorithm panel
  -> pairwise Wilcoxon signed-rank vs the proposed, with Holm correction
  -> Vargha-Delaney A12 effect sizes and win/tie/loss tallies
  -> write CSV/LaTeX tables + Nemenyi CD and rank-chart PNGs
  -> results/_run_all/_analysis/<suite>/
```

The proposed optimizer defaults to `dt-gsk`; the comparator panel is the six
reference optimizers (`gsk`, `agsk`, `apgsk`, `fdb-agsk`, `egsk`, `atmals-gsk`).
Every column — the proposed `dt-gsk` included — is read from the committed
reference panel first (`benchmarks/cec_reference_results/` is the paper's
single source of truth for all data and statistics); a locally reproduced run
under `results/_run_all/` is only a fallback for cells the reference tree does
not carry. A lighter version runs
live during a campaign when you pass `gsk-run --stats`: it streams the
per-dimension Wilcoxon + Friedman panel as each dimension finishes, skipping only
vanilla `gsk` (the native-dimension `cec2011` suite is supported and emits a
single per-suite rollup panel). The full method, options,
and output inventory are in
[research/statistical_analysis.md](../research/statistical_analysis.md).

## Ablation Workflow

The mechanism-attribution path: measure what each DT-GSK scaffold mechanism
contributes by re-running the optimizer with one mechanism disabled at a time.

```text
python scripts/run_ablation.py --suite cec2017 --dimension 30 --runs 25
  -> write one config per cell to configs/_ablation/<cell>.yml
  -> run 7 cells: baseline (full scaffold) + one cell per disabled mechanism
     (ACE, NLPSR, BSE, linkage crossover, Nelder-Mead local search, elite archive)
  -> results/_ablation/<cell>/dt-gsk/<suite>/

python papers/scripts/generate_ablation_matrix.py --suite cec2017
  -> aggregate the cells: mean Friedman rank, delta vs full, best-case counts,
     full-vs-cell Wilcoxon + Holm
  -> results/ablation/ablation_matrix_rank_summary_<suite>[_D<dim>].csv

python papers/scripts/generate_latex_tables.py
  -> render one papers/tables/ablation_<tag>.tex per matrix
```

`run_ablation.py` supports `--suite {cec2017,cec2011,cec2013}` (`cec2011` runs
at its native dimensions), `--mode {remove-one,add-one}`, `--dimension`
(comma-separated list), `--runs` (default 25), `--workers`, `--only` (subset of
cell names), and `--dry-run` (write configs and print the matrix without
running). SGSM (`interaction_graph_enabled`) is OFF in every cell, so the
matrix isolates the scaffold mechanisms; the SGSM overlay itself is measured
separately by a 4-cell direct-isolation design (full / no-sgsm / no-adaptive /
no-finalpolish) run on CEC2017 (D50, D100) and CEC2013 (D50) via
`scripts/run_overlay_ablation_51.py`.

## Paper Review-Pack Workflow

The publication path: regenerate the reviewer-facing convergence PDF from the
checkpoint logs a campaign already wrote.

```text
python papers/scripts/generate_review_pack.py
  -> read CheckpointErrors_<alg>_F<func>_D<dim>.csv for all 7 algorithms
  -> build 7-algorithm convergence grids per function/dimension
  -> render papers/DT-GSK-CEC2017-review.pdf via matplotlib PdfPages
  -> log any missing curves to papers/DT-GSK-CEC2017-review_missing.log
```

This pipeline needs no LaTeX: it draws straight to a PDF with matplotlib's
`PdfPages`. Missing `(algorithm, function, dimension)` curves are recorded in the
missing-log and never fabricated. The separate full paper (`papers/main.tex`) is
built with MiKTeX and is independent of this review pack.

The paper's convergence-figure generators
(`papers/scripts/generate_full_convergence.py`,
`generate_cec2011_convergence.py`, and `generate_cec2013_convergence.py`) read
their curves and checkpoint logs from the committed reference tree
`benchmarks/cec_reference_results/<suite>/<optimizer>/`.

## Parallel Workflow

The execution path: how independent runs are spread across cores deterministically.

Parallel mode is the default. After the seed schedule is fixed, independent run
tasks are dispatched to a process pool (`ProcessPoolExecutor` with a spawn
context). The automatic worker count is 2 on machines with at least two logical
cores, otherwise 1. Full campaign commands should keep
`--parallel --workers 2` visible, and users can increase `--workers N` only when
they want to spend more CPU and memory. Automatic CEC2017 composition cells
(`F21`-`F30`) retain an upper cap of 8 workers for memory safety. Each task
receives the same deterministic payload it would receive in serial mode, and
outputs are restored to serial order before writing, so artifacts are identical
regardless of backend.

For very small task counts the runner stays in-process (the spawn overhead would
not pay off). If a worker process dies, the runner tears the pool down, rebuilds
it, and retries a few times; after repeated failures it finishes the affected
cell on the **serial** backend rather than the thread backend (parallel Numba
kernels can deadlock under many Python threads). The optional `profile.json`
records worker count, warmup status, skipped cells, and per-run timing metadata.
See [research/performance.md](../research/performance.md) for tuning guidance.

## Documentation Workflow

Documentation is maintained in Markdown. Generated API HTML from the reference
source archive is not copied because it describes compiled reference-bridge
symbols. The Python replacement is `docs/reference/api.md`, the source
docstrings, and importable package metadata.

Regenerate the browsable HTML site from the Markdown sources and docstrings:

```text
python scripts\build_docs_html.py
  -> regenerate Markdown and API HTML pages
```

Run this after editing documentation Markdown or source docstrings so the
generated HTML under `docs/html/` stays in sync.
