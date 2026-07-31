# Paper / review pack

LaTeX sources, tables, figures and figure-generation scripts for the DT-GSK
paper and the advisor review pack.

## Paper build prompt

`PAPER_BUILD_PROMPT.md` is the master prompt for (re)building the manuscript.
It is split into phase files under `build_prompt_phases/` (`PHASE_0_audit.md`
through `PHASE_9_submission.md`) plus
`build_prompt_phases/ADDENDUM_R2_cec2013_and_ablation.md`, which covers the
CEC2013 comparison suite and the ablation study added for revision 2.

## Review pack: `DT-GSK-CEC2017-review.pdf`

`scripts/generate_review_pack.py` builds a single PDF for advisor review:

* page 1 — headline dashboard (Friedman mean ranks + Holm-corrected Wilcoxon
  scoreboard, DT-GSK vs each comparator);
* pages 2–5 — CEC2017 per-function mean tables, one dimension per page
  (7-algorithm GSK-family panel);
* page 6 — CEC2011 real-world mean table;
* remaining pages — **CEC2017 and CEC2011 convergence grids** showing the full
  **7-algorithm GSK-family panel**.

### Convergence curves

Every convergence panel plots, for each algorithm, the **mean best-so-far
error over that algorithm's runs**, read at the shared CEC checkpoints
(the `E<evals>` columns of `CheckpointErrors_*.csv`). One general loader
(`alg_mean_curve`) is used for all seven algorithms. DT-GSK is drawn last and
most prominently (deep-blue solid line with markers, on top of the
comparators). A single figure-level legend per page lists all seven variants
in a fixed order/colour so pages stay consistent even when a panel is missing
an algorithm.

### Supported algorithms

| ID            | Display name |
|---------------|--------------|
| `gsk`         | GSK          |
| `agsk`        | AGSK         |
| `apgsk`       | APGSK        |
| `fdb-agsk`    | FDB-AGSK     |
| `egsk`        | eGSK         |
| `atmals-gsk`  | ATMALS-GSK   |
| `dt-gsk`     | DT-GSK      |

### Expected input result folders

* **Comparators** (`gsk`, `agsk`, `apgsk`, `fdb-agsk`, `egsk`, `atmals-gsk`):
  `benchmarks/cec_reference_results/<suite>/<alg>/gen_logs/`
* **DT-GSK** (reproduced locally):
  `results/_run_all/dt-gsk/<suite>/gen_logs/`

where `<suite>` is `cec2017` or `cec2011`. All seven algorithms share the
checkpoint schema `CheckpointErrors_<alg>_F<func>_D<dim>.csv` with header
`Run,Seed,E1000,E2000,...,E100000`. CEC2011 problems carry per-problem native
dimensions encoded in the file name (`..._F<k>_D<native>.csv`); the loader
discovers the dimension from the file name.

### Output

* `papers/DT-GSK-CEC2017-review.pdf` — the review pack.
* `papers/DT-GSK-CEC2017-review_missing.log` — every missing
  `(algorithm, function, dimension)` convergence curve, grouped by
  algorithm/dimension.

### Missing data

Missing curves are **never fabricated**. When the checkpoint CSV for an
`(algorithm, function, dimension)` is absent, that curve is simply skipped on
the plot and recorded. A console summary is printed and the missing list is
written to `*_missing.log`. DT-GSK checkpoint coverage is now complete for
CEC2017 (D10/D30/D50/D100) and CEC2011, so every convergence page shows the
full 7-algorithm panel and the missing-curve log is empty.

### Regenerate

From the project root:

```bash
python papers/scripts/generate_review_pack.py
```

(The script inserts both the repo root and `src/` on `sys.path`, so no
`PYTHONPATH` is required; `PYTHONPATH=src` also works.)

## Manuscript convergence figures

Separate from the review pack, `scripts/` also renders the manuscript
convergence grids, one script per suite:

* `generate_full_convergence.py` — CEC2017;
* `generate_cec2011_convergence.py` — CEC2011 (native per-problem dimensions);
* `generate_cec2013_convergence.py` — CEC2013 (28 functions, four subfigures
  a–d).

All three read `curves/` and `gen_logs/` from the committed reference panel
`benchmarks/cec_reference_results/<suite>/<alg>/` — the single source of truth
for paper data — for the full 7-algorithm family panel.

## Ablation matrix and tables

Two generators turn `scripts/run_ablation.py` cell outputs into paper assets:

* `scripts/generate_ablation_matrix.py` — aggregates the per-cell results under
  `results/_ablation/` into
  `results/ablation/ablation_matrix_rank_summary_<suite>[_D<dim>].csv`
  (mean Friedman rank, delta vs the full scaffold, best-case counts, and
  full-vs-cell Wilcoxon with Holm correction); `--suite`, `--dimension`, and
  `--full-cell` select the cells.
* `scripts/generate_latex_tables.py` (`gen_ablation_table`) — renders one
  `papers/tables/ablation_<tag>.tex` per matrix CSV found under
  `results/ablation/`.

## Figure scripts vs `gsk-stats`

The `scripts/` generators here (e.g. `generate_rank_charts.py`,
`generate_nemenyi_cd.py`) render the **manuscript** figures — PDF output under
`papers/figures/` sized and styled for the LaTeX pages. They are deliberately
separate from `gsk-stats`, which writes the **analysis** PNGs under
`results/_run_all/_analysis/<suite>/figures/`. Same statistics, two canonical
outputs: one per deliverable.
