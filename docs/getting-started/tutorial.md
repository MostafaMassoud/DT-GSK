# Tutorial

> **What this page is.** A guided, copy-paste-able first run: from a clean
> checkout to a validated result, following the page top to bottom.
> **Who it is for.** First-time users who want to see the project work before
> reading reference material.
> **After completing it**, you will have installed the package, listed its
> capabilities, run a smoke experiment and a single CEC2017 cell, inspected the
> output files, validated against reference tables, run a five-optimizer smoke
> config, and produced a statistical comparison report.
> **Prerequisites:** Python 3.10–3.13 and the repository checked out. For the "why"
> behind the steps, read the [Explainer](explainer.md); for the full command
> reference, see the [User Guide](user_guide.md).

Each step is one block you can paste as-is. Commands use PowerShell but work the
same in other shells.

## 1. Install

Install in editable mode, then run the test suite to confirm the environment is
healthy.

```powershell
python -m pip install -e ".[dev]"
python -m pytest
```

A healthy test run ends with a `passed` summary line.

## 2. List capabilities

Confirm the package can see its optimizers, suites, and reference tables.

```powershell
gsk-list --optimizers --benchmarks --references benchmarks/cec_reference_results
```

Confirm that all seven panel optimizers (`gsk`, `agsk`, `apgsk`, `atmals-gsk`,
`fdb-agsk`, `dt-gsk`, `egsk`) are listed under `optimizers:`, that the six benchmark
suites (the five CEC suites plus `sphere`) appear under `benchmarks:` / `smoke problems:`, and that the
`references:` block reports a non-zero CSV count for each imported suite. The
proposed method is `dt-gsk`; `egsk` is now runnable too, though its statistical-panel
cells still come from the committed reference comparator data.

## 3. Run the smoke config

Run the smallest example — one optimizer, one CEC2017 cell, a tiny budget.

```powershell
gsk-run --config configs/smoke.yml --root .
```

`--root .` roots the config's relative paths under the current project. This
writes output below `results/`. The console prints a `run_all (CEC2017)` banner,
a detailed configuration block, a one-row summary table, and an
`[OK] Updated 1 function(s)` line. (A full sample of this output is in the
[User Guide](user_guide.md#the-quickest-smoke-run-yaml).)

## 4. Run one direct CEC2017 cell

Now run a single cell directly from CLI flags instead of a config file.

```powershell
gsk-run --optimizer gsk --suite cec2017 --dimension 10 --function 1 --runs 1 --seed 20240620 --max-evaluations 1000 --overwrite
```

The reduced budget (`--max-evaluations 1000`) keeps the tutorial quick;
`--overwrite` replaces any existing rows for this cell.

## 5. Inspect output

The results live under the optimizer/suite path:

```text
results/_run_all/gsk/cec2017/
```

Files worth opening first:

| File | What it holds |
|---|---|
| `summary/per_run.csv` | One row per individual run (seed, best fitness, error, NFEs, time). |
| `summary/gsk_cec2017_D10.csv` | Per-function statistics: Best, Median, Mean, Worst, SD. |
| `summary/seed_schedule.csv` | The `(Dim, Function, Run) -> Seed` schedule actually used. |
| `summary/environment.json` | Captured run environment. |
| `summary/verification.json` | Validation verdict (written after a compare). |
| `curves/Figure_F1_D10_Run#1.csv` | Best-so-far convergence trace (median run). |
| `curves/graphs/Figure_F1_D10.png` | Rendered convergence graph PNG; present only when `--convergence-graphs` / `convergence_graphs: true` is used. |
| `gen_logs/CheckpointErrors_gsk_F1_D10.csv` | Per-checkpoint error log. |

The full file list and exact CSV columns are in the
[Result Schema](../reference/result_schema.md).

## 6. Validate against references

Compare your generated tree against the imported reference tables.

```powershell
gsk-validate --compare results/_run_all/gsk/cec2017 benchmarks/cec_reference_results
```

It prints a `verdict:` line (`CONSISTENT` or `DEVIATES`) plus counts and a
win/tie/loss tally. For reduced-budget runs, use this to confirm schema and
reference alignment — full statistical reproduction requires full protocol
budgets (see the [Validation Report](../research/validation_report.md)).

## 7. Run several optimizers together

Run the shipped multi-optimizer smoke config on the simple `sphere` problem. It
runs five optimizers (`gsk`, `agsk`, `apgsk`, `atmals-gsk`, `fdb-agsk`) and also
enables warmup and profile metadata. It explicitly uses the lightweight thread
backend because this smoke job is a tiny non-CEC demonstration; normal benchmark
runs you start without those settings use the process backend by default, and
CEC campaigns should keep that default.

```powershell
gsk-run --config configs/all_optimizers_smoke.yml --root .
```

The console header counts the optimizers (`[1/5]`, `[2/5]`, ...). Afterwards,
inspect `summary/profile.json` in each generated optimizer run directory.

This shipped config omits `egsk` and the proposed `dt-gsk` to stay fast. To
run the full seven-optimizer family, name them on the CLI instead:

```powershell
gsk-run --optimizer gsk,agsk,apgsk,fdb-agsk,atmals-gsk,egsk,dt-gsk --suite sphere --function 1 --dimension 4 --runs 1 --max-evaluations 120 --root . --overwrite
```

## 8. Produce a statistical comparison

With runs on disk for the proposed optimizer, build the GSK-family statistical
report (Friedman ranks, Nemenyi critical-difference, pairwise Wilcoxon + Holm,
and effect sizes):

```powershell
gsk-stats --suite CEC2017 --dims 10
```

It writes a text report, a Friedman-rank CSV, LaTeX fragments, and CD/rank PNGs
under `results/_run_all/_analysis/cec2017/`. The panel compares the proposed
`dt-gsk` against the six reference comparators. (Use `--no-figures` to skip the
PNG figures; the text report, CSV, and LaTeX fragments are still written.) For a richer narrative, see
[Statistical Analysis](../research/statistical_analysis.md).

Tip: to watch the same analysis stream **live during a run**, add the opt-in
`--stats` flag to a `gsk-run` command on a non-baseline optimizer (it skips
vanilla `gsk`; fixed-dimension suites and the native-dimension `cec2011`
rollup are both supported):

```powershell
gsk-run --optimizer dt-gsk --suite cec2017 --dimension 10 --stats --root .
```

## 9. Build documentation

```powershell
python scripts/build_docs_html.py
```

This regenerates the browsable HTML twins under `docs/html/` from the Markdown
sources and package docstrings. Open `docs/html/index.html` to browse them.

## Where to go next

- Everyday commands explained: [User Guide](user_guide.md).
- Configure a real campaign in YAML: [Configuration](configuration.md).
- The proposed method in depth: [DT-GSK](../algorithms/dt-gsk.md).
- Build the advisor review PDF: `python papers/scripts/generate_review_pack.py`
  (see [papers/README.md](../../papers/README.md)).
- If a step failed: [Troubleshooting](troubleshooting.md).
