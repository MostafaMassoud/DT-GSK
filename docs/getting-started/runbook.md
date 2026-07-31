# Runbook

> **What this page is.** A quick, copy-paste command reference for routine
> operation - the commands with only the context needed to choose the right one.
> **Who it is for.** Anyone who already knows the workflow and just wants the
> command to run.
> **Prerequisites.** The package installed (see [User Guide](user_guide.md)).
> **Want explanations?** Each command is explained step by step in the
> [User Guide](user_guide.md); for a guided first run, see the
> [Tutorial](tutorial.md).

Run every command from the project root (the directory that contains
`run.py`, `pyproject.toml`, and the `configs/` folder). On this machine that is:

```powershell
cd D:\AI\PhD-Projects\00-GSK-Family\02-GSK_Family_Python_v1.1
```

The canonical runner is `python run.py`, which prepends `src/` to the import
path so it works without installing the package. Once you have run
`python -m pip install -e ".[dev]"`, the console scripts `gsk-run`
(alias `gsk-family-run`), `gsk-list`, `gsk-validate`, and `gsk-stats` are
equivalent and shorter; this runbook mixes both forms. Commands use PowerShell
(the project's primary shell on Windows) but work the same in other shells.

## Command Picker

| I want to... | Jump to |
|---|---|
| Confirm the install works | [Verify The Environment](#verify-the-environment) |
| See which optimizers/suites/references exist | [List Runtime Assets](#list-runtime-assets) |
| Run the tiniest possible job | [Smoke Run](#smoke-run) |
| Reproduce one published cell | [Targeted Runs](#targeted-runs) |
| Run one optimizer on one CEC cell | [Single Optimizer Run](#single-optimizer-run) |
| Reproduce every paper artifact, in order | [Full Paper Pipeline](#full-paper-pipeline) |
| Run the full 7-optimizer CEC2017 sweep | [CEC2017 All Optimizers](#cec2017-all-optimizers) |
| Run another CEC suite end to end | [Other Full Sweeps](#other-full-sweeps) |
| Run the second comparison suite | [CEC2013 Family Panel](#cec2013-family-panel) |
| Run the large-scale (LSGO) suite, all 7 optimizers | [CEC2013-LSGO Family Panel](#cec2013-lsgo-family-panel) |
| Check a run against reference tables | [Validate Results](#validate-results) |
| Produce paper-grade Friedman/Wilcoxon stats | [Statistical Analysis](#statistical-analysis) |
| Isolate what each DT-GSK mechanism contributes | [DT-GSK Ablation](#dt-gsk-ablation) |
| Build the advisor review PDF | [Paper Review Pack](#paper-review-pack) |
| Recover from a crash mid-sweep | [Tight On Memory](#tight-on-memory) and the [Troubleshooting](troubleshooting.md#a-worker-process-dies-or-the-pool-breaks-mid-run) page |

## Verify The Environment

```powershell
python -m pip install -e ".[dev]"
python -m pytest -q
```

A healthy run ends with a `passed` summary line. If the console scripts are
later reported as "not found", reopen the shell or fall back to `python run.py`
(see [Troubleshooting](troubleshooting.md#gsk-run-is-not-found)).

## List Runtime Assets

```powershell
gsk-list --optimizers --benchmarks --references benchmarks/cec_reference_results
```

## Smoke Run

The fastest sanity check: one optimizer, the `sphere` smoke problem, a tiny
budget. It finishes in seconds and writes a complete (if trivial) output tree.

```powershell
python run.py --root . --optimizer gsk --suite sphere --function 1 --dimension 4 --runs 1 --max-evaluations 80 --overwrite
```

Or run the equivalent committed config, which targets one CEC2017 cell:

```powershell
gsk-run --config configs/smoke.yml --root .
```

## Single Optimizer Run

```powershell
python run.py --root . --optimizer agsk --suite cec2017 --dimension 10 --function 1 --runs 1 --seed 20240620 --max-evaluations 1000 --output-root results --overwrite
```

## Full Paper Pipeline

The complete data-to-PDF sequence, mirrored from the project-root
[runbook.md](../../runbook.md) (its "Full Paper Pipeline" section — the two are
kept consistent; the root runbook adds the per-stage variants). `--workers 15`
matches `configs/publish/`; drop to the safe baseline `2` if memory-constrained.
Dependency order: 1 data -> 3 stats -> 5/6 figures & tables -> 7 build; and
2 ablation -> 4 aggregate -> 6 table.

```powershell
# --- 1. Generate run data: the three benchmark campaigns ---
python run.py --root . --optimizer gsk,agsk,apgsk,fdb-agsk,atmals-gsk,egsk,dt-gsk --suite cec2017 --function 1:30 --dimension 10,30,50,100 --runs 51 --parallel --workers 15 --convergence-graphs --overwrite
python run.py --root . --optimizer gsk,agsk,apgsk,fdb-agsk,atmals-gsk,egsk,dt-gsk --suite cec2011 --function 1:22 --dimension native --runs 25 --parallel --workers 15 --convergence-graphs --overwrite
python run.py --root . --optimizer gsk,agsk,apgsk,fdb-agsk,atmals-gsk,egsk,dt-gsk --suite cec2013 --function 1:28 --dimension 10,30,50 --runs 51 --parallel --workers 15 --convergence-graphs --overwrite

# --- 2. DT-GSK scaffold ablation: CEC2017, all dimensions ---
python scripts/run_ablation.py --dimension 10,30,50,100 --runs 25 --workers 15

# --- 3. Statistical panels (per suite) ---
python -m gsk_family.cli.stats --suite CEC2017 --dims 10,30,50,100
python -m gsk_family.cli.stats --suite CEC2011
python -m gsk_family.cli.stats --suite CEC2013 --dims 10,30,50

# --- 4. Aggregate the ablation (per dimension) ---
python papers/scripts/generate_ablation_matrix.py --dimension 10
python papers/scripts/generate_ablation_matrix.py --dimension 30
python papers/scripts/generate_ablation_matrix.py --dimension 50
python papers/scripts/generate_ablation_matrix.py --dimension 100

# --- 5. Figures ---
python papers/scripts/generate_full_convergence.py
python papers/scripts/generate_cec2011_convergence.py
python papers/scripts/generate_cec2013_convergence.py --dimension 30
python papers/scripts/generate_nemenyi_cd.py
python papers/scripts/generate_rank_charts.py
python papers/scripts/generate_trace_figures.py
python papers/scripts/generate_nlpsr_trajectory.py
python papers/scripts/generate_adaptive_params_panel.py

# --- 6. Tables (read frozen, checked-in evidence: benchmarks/cec_reference_results/_paper_tables/
#     and papers/analysis/rel-2026-07-20-67d9345f9/ — not results/ staging) ---
python papers/scripts/generate_latex_tables.py
python papers/scripts/generate_t16_bca.py

# --- 7. Build the PDFs ---
python papers/scripts/build_pdf.py
python papers/scripts/build_supplementary.py
python papers/scripts/generate_review_pack.py

# --- 8. Quality gates ---
python -m pytest -q
python -m ruff check .
python scripts\validate_profile_lock.py --root .
python scripts\build_docs_html.py
```

## CEC2017 All Optimizers

Use a visible worker count in campaign commands. The safe baseline is
`--workers 2`; increase the number only when you know the machine has spare CPU
and memory and you are not running other heavy work. `--convergence-graphs`
opts in to rendered PNG plots; omit it when you only need the convergence CSV
files.

```powershell
python run.py --root . --optimizer gsk,agsk,apgsk,fdb-agsk,atmals-gsk,egsk,dt-gsk --suite cec2017 --function 1:30 --dimension 10,30,50,100 --runs 51 --parallel --workers 2 --convergence-graphs --overwrite
```

This runs all seven runnable optimizers. `egsk` executes via its scipy-SLSQP
port of the MATLAB reference, and its statistical-panel cells come from the
committed `scipy`-SLSQP port run (the comparator of record).
`--function 1:30` is an inclusive range; the CEC2017 *scored* set excludes the
withdrawn F2, so per-function tables and statistics cover F1 and F3-F30. Each
generated cell is one `(optimizer, suite, dimension, function)` group with 51
independent runs.

`--overwrite` recomputes matching cells. Omit it only when you intentionally
want to **resume**: without `--overwrite`, cells whose runs already exist in
`summary/per_run.csv` are skipped, so a sweep interrupted by a crash or reboot
picks up where it left off. With `--overwrite`, the runner rebuilds that
optimizer/suite `per_run.csv` from scratch: **all** previously recorded rows are
discarded, not just the cells named in the command — so when overwriting, name
the full cell set you want the tree to contain.

## Other Full Sweeps

```powershell
# CEC2020 - 10 functions, dims 5/10/15/20
python run.py --root . --optimizer gsk,agsk,apgsk,fdb-agsk,atmals-gsk,egsk,dt-gsk --suite cec2020 --function 1:10 --dimension 5,10,15,20 --runs 51 --parallel --workers 2 --convergence-graphs --overwrite

# CEC2013 - 28 functions, dims 10/30/50 (see the CEC2013 Family Panel section below)
python run.py --root . --optimizer gsk,agsk,apgsk,fdb-agsk,atmals-gsk,egsk,dt-gsk --suite cec2013 --function 1:28 --dimension 10,30,50 --runs 51 --parallel --workers 2 --convergence-graphs --overwrite

# CEC2011 - native per-problem dims. NOTE: --function defaults to F1 only, so you
# MUST pass --function 1:22 to run the whole suite (22 problems).
python run.py --root . --optimizer gsk,agsk,apgsk,fdb-agsk,atmals-gsk,egsk,dt-gsk --suite cec2011 --function 1:22 --dimension native --runs 25 --parallel --workers 2 --convergence-graphs --overwrite

# CEC2013-LSGO - 15 funcs, native D=1000 (F13-F14: D=905), 3,000,000 evals/run; VERY
# expensive. MUST use --dimension native (a fixed --dimension 1000 errors on F13/F14).
# Full 7-optimizer panel + cost/scheduling caveats: see "CEC2013-LSGO Family Panel" below.
python run.py --root . --optimizer gsk,agsk,apgsk,fdb-agsk,atmals-gsk,egsk,dt-gsk --suite cec2013lsgo --function 1:15 --dimension native --runs 25 --parallel --workers 2 --convergence-graphs --overwrite
```

## CEC2013 Family Panel

CEC2013 is the paper's **second comparison suite**: 28 functions, dims 10/30/50,
51 runs (the CEC2013 competition standard). Run the full 7-optimizer panel
(`egsk` runs via the scipy-SLSQP port; the statistical panel reads `egsk` from
the committed `scipy`-SLSQP port CSVs, the comparator of record):

```powershell
python run.py --root . --optimizer gsk,agsk,apgsk,fdb-agsk,atmals-gsk,egsk,dt-gsk --suite cec2013 --function 1:28 --dimension 10,30,50 --runs 51 --parallel --workers 2 --convergence-graphs --overwrite
```

Then build the CEC2013 family report (Friedman ranks, Nemenyi CD, pairwise
Wilcoxon/Holm, effect sizes) — comparators are read from
`benchmarks/cec_reference_results/cec2013/`:

```powershell
python -m gsk_family.cli.stats --suite CEC2013 --dims 10,30,50
```

CEC2013 convergence-curve grids (28 functions at a chosen dimension):

```powershell
python papers/scripts/generate_cec2013_convergence.py --dimension 30
```

## CEC2013-LSGO Family Panel

CEC2013-LSGO is the CEC-2013 **large-scale global optimization** suite: 15
functions at native dimensions — **D=1000** for F1–F12 and F15, **D=905** for the
overlapping-group functions F13–F14 — scored on **raw objective value** (no
optimum subtraction, like CEC2011), with a **3,000,000-evaluation** budget per
run. All seven optimizers run on it unchanged (`egsk` via the scipy-SLSQP port).
It is registered in code (`CEC_SUITES` in `benchmark_adapter/protocol.py`) but
carries **no committed reference-results tree**, so a fresh run populates
`results/_run_all/` and the panel reads from there — not from
`benchmarks/cec_reference_results/`.

> **Cost & scheduling — read first.** This is by far the heaviest sweep in the
> project: 7 optimizers × 15 functions × 25 runs × 3,000,000 evaluations at
> D≈1000. Run it on an **idle machine**, and **not** concurrently with any
> timing-critical campaign — competing for CPU contaminates wall-clock
> measurements. (The RT-001 comparator re-timing that this warning originally
> referenced is closed and must not be re-run.) D=1000 is memory-heavy, so tune
> `--workers` to your RAM (start low; see "Tight On Memory"). Always pass
> `--dimension native`: a fixed `--dimension 1000` errors on F13/F14 (native
> D=905).

Do a **bounded end-to-end check first** (2 functions, 1 run, reduced budget) to
confirm the pipeline in minutes before committing to the full multi-hour sweep:

```powershell
python run.py --root . --optimizer gsk,agsk,apgsk,fdb-agsk,atmals-gsk,egsk,dt-gsk --suite cec2013lsgo --function 1,12 --dimension native --runs 1 --max-evaluations 50000 --parallel --workers 2 --overwrite
```

Full 7-optimizer panel (native dims, full 3,000,000-evaluation budget, 25 runs). Use
`--workers 13`: the runner dispatches each function-cell's 25 runs as a barrier
(`ceil(25 / workers)` waves), so 13 is the knee that cuts 3 waves to 2 (~1.5x vs 12);
14-22 give the same 2 waves and >22 cannot help on a 22-core box. `--numba-threads 1`
keeps the batch kernel byte-stable at D>=50.

```powershell
python run.py --root . --optimizer gsk,agsk,apgsk,fdb-agsk,atmals-gsk,egsk,dt-gsk --suite cec2013lsgo --function 1:15 --dimension native --runs 25 --parallel --workers 13 --numba-threads 1 --convergence-graphs --overwrite
```

The 7-in-one command runs the optimizers **sequentially** (`[1/7]` -> `[7/7]`); the 13
workers parallelize the 25 runs *within* each function-cell, not the optimizers. To run
them **one at a time** instead -- cleaner failure isolation, and an early `gsk` result in
hand before the slow ones -- launch each as its own command (each writes to its own
`results/_run_all/<optimizer>/cec2013lsgo/`, so they never collide):

```powershell
python run.py --root . --optimizer gsk        --suite cec2013lsgo --function 1:15 --dimension native --runs 25 --parallel --workers 13 --numba-threads 1 --convergence-graphs --overwrite
python run.py --root . --optimizer agsk       --suite cec2013lsgo --function 1:15 --dimension native --runs 25 --parallel --workers 13 --numba-threads 1 --convergence-graphs --overwrite
python run.py --root . --optimizer apgsk      --suite cec2013lsgo --function 1:15 --dimension native --runs 25 --parallel --workers 13 --numba-threads 1 --convergence-graphs --overwrite
python run.py --root . --optimizer fdb-agsk   --suite cec2013lsgo --function 1:15 --dimension native --runs 25 --parallel --workers 13 --numba-threads 1 --convergence-graphs --overwrite
python run.py --root . --optimizer egsk       --suite cec2013lsgo --function 1:15 --dimension native --runs 25 --parallel --workers 13 --numba-threads 1 --convergence-graphs --overwrite
python run.py --root . --optimizer atmals-gsk --suite cec2013lsgo --function 1:15 --dimension native --runs 25 --parallel --workers 13 --numba-threads 1 --convergence-graphs --overwrite
python run.py --root . --optimizer dt-gsk     --suite cec2013lsgo --function 1:15 --dimension native --runs 25 --parallel --workers 13 --numba-threads 1 --convergence-graphs --overwrite
```

Rough per-optimizer wall time (from the measured relative cost): `gsk` ~2.5 h;
`agsk`/`apgsk`/`fdb-agsk`/`egsk` ~3-4 h each; `atmals-gsk` ~6 h (local search, ~2.4x gsk);
`dt-gsk` ~12 h (scaffold + structure memory + eigenframe polish, ~4.8x gsk). The
evaluation kernel is identical across all seven (numba batch, byte-stable at
`threads=1`) -- the spread is the optimizers' own subsystems, not the benchmark.

Output lands in `results/_run_all/<optimizer>/cec2013lsgo/summary/`. Then build the
raw-objective family report (Friedman ranks, pairwise Wilcoxon/Holm, effect sizes)
from those fresh results:

```powershell
python -m gsk_family.cli.stats --suite cec2013lsgo
```

## Config Launchers

```powershell
python scripts\run_all_cec2017.py
python scripts\run_all_cec2011.py
python scripts\run_all_cec2020.py
python scripts\run_all_cec2013.py
python scripts\run_all_cec2013lsgo.py
```

You can also drive campaigns directly from the YAML files in `configs/`:

```powershell
python run.py --root . --config configs/all_cec2017.yml
python run.py --root . --config configs/all_optimizers_smoke.yml
python run.py --root . --config configs/all_optimizers_cec2017_reduced.yml
```

## Tight On Memory

Run one optimizer at a time with the same safe worker baseline. Omit
`--overwrite` only when you intentionally want to resume.

```powershell
python run.py --root . --optimizer gsk --suite cec2017 --function 1:30 --dimension 10,30,50,100 --runs 51 --parallel --workers 2 --convergence-graphs --overwrite
python run.py --root . --optimizer agsk --suite cec2017 --function 1:30 --dimension 10,30,50,100 --runs 51 --parallel --workers 2 --convergence-graphs --overwrite
python run.py --root . --optimizer apgsk --suite cec2017 --function 1:30 --dimension 10,30,50,100 --runs 51 --parallel --workers 2 --convergence-graphs --overwrite
python run.py --root . --optimizer fdb-agsk --suite cec2017 --function 1:30 --dimension 10,30,50,100 --runs 51 --parallel --workers 2 --convergence-graphs --overwrite
python run.py --root . --optimizer atmals-gsk --suite cec2017 --function 1:30 --dimension 10,30,50,100 --runs 51 --parallel --workers 2 --convergence-graphs --overwrite
python run.py --root . --optimizer egsk --suite cec2017 --function 1:30 --dimension 10,30,50,100 --runs 51 --parallel --workers 2 --convergence-graphs --overwrite
python run.py --root . --optimizer dt-gsk --suite cec2017 --function 1:30 --dimension 10,30,50,100 --runs 51 --parallel --workers 2 --convergence-graphs --overwrite
```

Need more speed? Increase the worker count deliberately:

```powershell
python run.py --root . --optimizer gsk --suite cec2017 --function 1:30 --dimension 10,30,50,100 --runs 51 --parallel --workers 4 --convergence-graphs --overwrite
```

## Targeted Runs

```powershell
# One optimizer, one function, one dimension
python run.py --root . --optimizer agsk --suite cec2017 --function 5 --dimension 30 --runs 51 --parallel --workers 2 --convergence-graphs --overwrite

# Same run with reference seed policy
python run.py --root . --optimizer agsk --suite cec2017 --function 5 --dimension 30 --runs 51 --seed-policy reference --parallel --workers 2 --convergence-graphs --overwrite
```

`--seed-policy reference` reproduces the published per-optimizer seed labels for
a single cell (see the [Seed Policy reference](../reference/seed_policy.md));
the default `unified` policy is what every family campaign uses.

## Where Output Lands

Generated runs are written under one root, keyed by optimizer and suite:

```text
results/_run_all/<optimizer>/<suite>/
  summary/    # per_run.csv, per-dimension summary CSVs, seed_schedule.csv, environment.json, verification.json
  curves/     # median-run convergence CSVs (+ graphs/*.png when --convergence-graphs)
  gen_logs/   # CheckpointErrors_<alg>_F<k>_D<dim>.csv per-checkpoint logs
```

`gsk-stats` writes to `results/_run_all/_analysis/<suite>/`. The imported,
read-only reference evidence stays under `benchmarks/cec_reference_results/`;
the runner refuses to write generated output there. Exact filenames and CSV
columns are in the [Result Schema](../reference/result_schema.md).

## Validate Results

The first form audits that the reference tree is well formed; the second
compares a generated run tree against it and prints a `verdict:` line
(`CONSISTENT` / `DEVIATES`) plus counts and a win/tie/loss tally. The exit code
is non-zero on `DEVIATES` or when no comparable functions were found, so the
command is script-friendly. The equivalent console script is `gsk-validate`.

```powershell
python -m gsk_family.cli.validate --references benchmarks/cec_reference_results
python -m gsk_family.cli.validate --compare results/_run_all/gsk/cec2017 benchmarks/cec_reference_results
```

Reduced-budget runs will not reproduce full-budget reference statistics; read a
comparison on such a run as a schema/consistency check, not a benchmark claim
(see the [Validation Report](../research/validation_report.md)).

## Statistical Analysis

Produce the paper-grade GSK-family comparison (Friedman ranks, Nemenyi CD,
pairwise Wilcoxon/Holm, and effect sizes) for the proposed optimizer
(`dt-gsk` by default) against the committed reference comparators. Outputs
(text report, Friedman-rank CSV, LaTeX fragments, CD/rank PNGs) land under
`results/_run_all/_analysis/<suite>/`.

```powershell
gsk-stats --suite CEC2017 --dims 10,30,50,100
gsk-stats --suite CEC2011
gsk-stats --suite CEC2013 --dims 10,30,50
```

The 7-algorithm panel is the six reference comparators
(`gsk`, `agsk`, `apgsk`, `fdb-agsk`, `egsk`, `atmals-gsk`) plus the proposed
`dt-gsk`.

**Single source of truth.** All paper statistics — the proposed `dt-gsk`
included — are read from the committed reference panel
`benchmarks/cec_reference_results/<suite>/<optimizer>/` first; a locally
reproduced run under `results/_run_all/` is used only as a fallback for cells
the reference tree does not carry. The convergence-figure generators read
curves and gen_logs from the same reference tree.

Useful `gsk-stats` flags (all optional):

| Flag | Default | Effect |
|---|---|---|
| `--suite` | `CEC2017` | Suite to analyse (`CEC2017`, `CEC2011`, `CEC2013`). |
| `--dims` | suite standard set | Comma-separated dimensions, e.g. `10,30,50,100`. |
| `--proposed` | `dt-gsk` | Optimizer id anchoring the pairwise comparisons. |
| `--results-root` | `results/_run_all` | Reproduced-results root. |
| `--reference-root` | `benchmarks/cec_reference_results` | Reference-results root. |
| `--out` | `<results-root>/_analysis/<suite>` | Output directory. |
| `--alpha` | `0.05` | Significance level for Holm/Wilcoxon/Nemenyi. |
| `--no-figures` | off | Skip the matplotlib CD/rank PNGs (text + CSV + LaTeX only). |
| `--strict-source` | off | Publication mode: refuse any empirical input outside `benchmarks/cec_reference_results/` (no `results/` fallback; missing cells fail loudly) and write a `source_use_audit.csv` of every opened data file beside the report. |

Outputs (text report, Friedman-rank CSV, LaTeX fragments, and Nemenyi
critical-difference + rank PNGs) land under
`results/_run_all/_analysis/<suite>/` (lower-cased suite name).

To instead stream the per-dimension Wilcoxon + Friedman analysis **live during a
run**, add the opt-in `--stats` flag. It is off by default and, by design, skips
vanilla `gsk` (the baseline anchor); `cec2011` is supported via its single
per-suite rollup panel. Add it on any non-baseline optimizer:

```powershell
python run.py --root . --optimizer dt-gsk --suite cec2017 --dimension 10 --dimension 30 --stats
```

(`--dimension` may be repeated, comma-separated, or given as a `START:STOP`
range.) See [Statistical Analysis](../research/statistical_analysis.md) for the
methodology and how to read the tables.

## Paper Review Pack

Build the single-PDF advisor review pack from the reproduced DT-GSK run plus
the committed comparator checkpoints:

```powershell
python papers/scripts/generate_review_pack.py
```

This writes `papers/DT-GSK-CEC2017-review.pdf` (matplotlib `PdfPages`, no
LaTeX needed): a headline dashboard, 7-algorithm CEC2017/CEC2011 mean tables,
and 7-algorithm GSK-family convergence grids (GSK, AGSK, APGSK, FDB-AGSK,
eGSK, ATMALS-GSK, DT-GSK), reading checkpoint CSVs from
`benchmarks/cec_reference_results/<suite>/<alg>/gen_logs/` (comparators) and
`results/_run_all/dt-gsk/<suite>/gen_logs/` (dt-gsk). Missing curves are
never fabricated: they are skipped on the plot and listed in
`papers/DT-GSK-CEC2017-review_missing.log`. See
[papers/README.md](../../papers/README.md) for the full layout.

## DT-GSK Ablation

The scaffold ablation isolates each DT-GSK mechanism by toggling
`optimizer_options` flags (every mechanism defaults to `true` in the locked
profile, so a cell disables exactly one). Six mechanisms plus the baseline give
seven cells: ACE (`ace_enabled`), NLPSR (`psr_enabled`), BSE (`bse_enabled`),
linkage crossover (`linkage_blockwise_enabled`), coordinate endgame local search
(`local_search_enabled`; the locked `pub` profile runs the coordinate method,
not the subspace/Nelder-Mead variant), and the elite archive (`arch_enabled`).
**SGSM
(`interaction_graph_enabled`) stays off in every cell** — the SGSM overlay is
ablated separately (the CEC2013 hold-out design with `full` / `no-adaptive` /
`no-sgsm` cells).

```powershell
# inspect the per-cell configs without running
python scripts/run_ablation.py --dimension 30 --dry-run

# run the default cell set (baseline + one disable-one cell per mechanism), n=25
python scripts/run_ablation.py --dimension 30 --runs 25 --workers 2

# aggregate the cells you just ran -> results/ablation/ablation_matrix_rank_summary_cec2017_D30.csv
# (point --ablation-root at the fresh per-cell tree; run_ablation.py prints this exact
#  line on completion. Without it the script defaults to the promoted immutable release
#  benchmarks/cec_reference_results/_ablation/scaffold instead of your new run.)
python papers/scripts/generate_ablation_matrix.py --ablation-root results/_ablation --suite cec2017 --dimension 30

# render the scaffold-ablation supplement tables (SA01/SA02) -> papers/tables/SA01.tex, SA02.tex
# (reads the manifest-verified frozen release copy, not the fresh results/ablation/ aggregate)
python papers/scripts/generate_ablation_exhibits.py
```

Useful flags: `--suite {cec2017,cec2011,cec2013}` (cec2011 uses native dims),
`--mode {remove-one,add-one}`, `--dimension 10,30,50,100`, `--runs` (default
25), `--workers`, `--only <cells>`, `--dry-run`. Per-cell configs are written
to `configs/_ablation/<cell>.yml` and per-cell output lands under
`results/_ablation/<cell>/dt-gsk/<suite>/`. The full option surface and the
ATMALS-GSK-protocol variants are in the project-root
[runbook.md](../../runbook.md#dt-gsk-ablation-cec2017).

## DT-GSK Diagnostics

Opt-in per-generation telemetry for root-cause analysis. It is **default off** and
**observational** — enabling it never alters DT-GSK's RNG order, evaluations, or
result for a given seed (the core's `generation_callback` path draws no RNG and
evaluates no objective). Enable it through `optimizer_options.dt_diagnostics` in a
YAML config; the runner writes one JSONL trace per cell to
`<output_root>/dt-gsk/<suite>/diagnostics/DTTrace_<suite>_F<func>_D<dim>_R<run>_S<seed>.jsonl`.

```yaml
# configs/experimental/dt_diag.yml
optimizers: [dt-gsk]
suite: cec2017
functions: [4, 13, 19, 26, 30]
dimensions: [10, 30, 50, 100]
runs: 5
seed: 20240620
seed_policy: unified
rand_generator: threefry
parallel: true
workers: 2
generation_logs: true
convergence_graphs: false
overwrite: true
output_root: results/_experimental/dt_diag
optimizer_options:
  dt_diagnostics: true
  dt_diagnostics_include_all_fields: true
```

```powershell
python run.py --root . --config configs/experimental/dt_diag.yml
python scripts/analyze_dt_diagnostics.py `
  --input results/_experimental/dt_diag/dt-gsk/cec2017/diagnostics `
  --out   results/_experimental/dt_diag/dt-gsk/cec2017/diagnostics_analysis
```

The analyzer aggregates the traces into `diagnostics_summary.csv`,
`wrong_basin_candidates.csv`, and per-subsystem summaries (ACE entropy, linkage
reliability, diversity/population, local-search ROI, boundary hits). Wrong-basin
flagging is general across all functions/dimensions — never hard-coded to a single
function. The JSONL fields come straight from the core's `DTGSKGenerationLog`.

## Build HTML Documentation

```powershell
python scripts\build_docs_html.py
```

Open `docs/html/index.html` in a browser to browse the reference-style static
documentation site.

## Clean Generated Python Caches

Only remove generated caches inside the project root:

```powershell
Get-ChildItem -Path . -Recurse -Directory -Filter __pycache__ | Remove-Item -Recurse -Force
Get-ChildItem -Path . -Recurse -Directory -Filter .pytest_cache | Remove-Item -Recurse -Force
```

Do not remove imported reference evidence.

## Campaign Checklist

- Config file is committed or archived.
- `seed`, `seed_policy`, and `rand_generator` are explicit.
- `output_root` is not inside `benchmarks/cec_reference_results`.
- `output_root` points at the tree that *contains* the suite folders, never at
  a suite folder itself — the runner writes `<output_root>/<optimizer>/<suite>/`,
  so an `output_root` ending in a suite name creates a doubled
  `<suite>/<optimizer>/<suite>/` path (see
  [Troubleshooting](troubleshooting.md#output-lands-in-a-doubled-suite-path)).
- `--overwrite` is present only when recomputing is intended.
- Reduced budget is clearly labelled.
- `environment.json` and `verification.json` are kept with summaries.
