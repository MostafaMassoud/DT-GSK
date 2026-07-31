# PHASE 3 — Tables & Figures

> **⚑ Revision 2 addendum applies to this phase.** Before executing, read [ADDENDUM_R2_cec2013_and_ablation.md](ADDENDUM_R2_cec2013_and_ablation.md) §R2.C — a CEC2013 family panel and the CEC2017 scaffold ablation add tasks to this phase, and the addendum overrides this file where they disagree.

> **Objective.** Turn the Phase-2 statistics bundle and source-of-truth CSVs into
> legible, self-contained, budget-aware exhibits — the main-text tables and the
> six figure families — with every number bound to committed data and never
> hand-typed.

This file expands **Phase 3** of `papers/PAPER_BUILD_PROMPT.md` (Part 5, "PHASE 3
— Tables & figures", and the C4 main/supplement split). It **follows**
`PHASE_2_data_stats.md` (which produced the `stats/` bundle and the
table→CSV binding map) and **hands to** `PHASE_4_drafting.md` (which references
these exhibits with `\ref`/`\cite`). Do **not** run optimizers, recompute
statistics, or edit `sections/*.tex` here — Phase 3 only builds and binds
exhibits from already-committed numbers.

Repo root (all commands assume this cwd; Windows PowerShell or Bash, `python`):

```
D:\AI\PhD-Projects\00-GSK-Family\02-GSK_Family_Python_v1.1
```

---

## Prerequisites

Do not start until **every** box below is checked (they are Phase-2 exit-gate
deliverables — confirm, do not re-derive):

- [ ] The Phase-2 **`stats/` bundle** exists and is committed. It was produced by
  the family-report pipeline (`gsk-stats`, i.e. `gsk_family.cli.stats:main`,
  wrapping `gsk_family.analysis.family_report.generate_family_report`). Its
  default output directory is `results/_run_all/_analysis/<suite>/` unless
  `--out` was passed. It contains, per suite:
  - `cec2017_statistical_report.txt` — concatenated per-dimension text report;
  - `cec2017_friedman_ranks.csv` — the Friedman mean-rank table (source of truth
    for the rank row/column and the CD figure);
  - `cec2017_friedman_ranks.tex` — `\input`-ready `tabular` (algorithms × dims,
    best-per-column already wrapped in `\bestval{}`);
  - `cec2017_wilcoxon_summary.tex` — `\input`-ready `tabular` (per dimension:
    `p`, `p_Holm`, `+`, `=`, `-`, `A12`, `Dec.`);
  - `figures/nemenyi_cd_cec2017_D{10,30,50,100}.png` and
    `figures/friedman_ranks_cec2017_D{…}.png`.
- [ ] The **table→CSV binding map** from Phase 2 is complete: every `tables/T*.tex`
  slot the paper will use names the exact source-of-truth CSV that supplies each
  cell. Phase 3 renders from those CSVs and re-uses that map as its checklist.
- [ ] The **commit SHA** anchoring all headline numbers is recorded (Part 2, C2).
  Every exhibit regenerated here must trace to that SHA.
- [ ] No Phase-0 provenance gap is still open for any exhibit Phase 3 will emit.

If any box is unchecked, stop and return to Phase 2. Building an exhibit on an
unverified number violates C2 and will be rejected downstream.

---

## Inputs

Read-only unless the task says "write". Never edit a number in any of these by
hand.

- **Source-of-truth CSVs** (Phase-2 binding map): the per-table CSV that supplies
  each cell. For the GSK-family panel these derive **reference-first** from
  `benchmarks/cec_reference_results/<suite>/<optimizer>/` (READ-ONLY committed
  panel — all seven optimizers including the proposed method; flat layout; never
  edit; SHA-256 auditable), with `results/_run_all/<optimizer>/<suite>/summary/`
  as the fallback only for cells the reference tree lacks
  (`result_loader.load_algorithm` enforces this order).
- **Stats bundle**: `results/_run_all/_analysis/<suite>/` (or the Phase-2 `--out`
  location) — the `.tex` fragments, `.csv`, and `figures/*.png` listed above.
- **Convergence curve CSVs** (committed, one median-run curve per cell):
  `benchmarks/cec_reference_results/<suite>/<optimizer>/curves/Figure_F<f>_D<d>_Run#<n>.csv`
  (fallback: `results/_run_all/<optimizer>/<suite>/curves/`) with columns
  `Eval, BestError, Log10Error`. The paper generators
  (`papers/scripts/generate_full_convergence.py`, `generate_cec2011_convergence.py`,
  `generate_cec2013_convergence.py`) read curves/gen_logs from the reference tree.
- **Existing manuscript exhibits** (classify keep/regenerate against the Phase-0
  asset map before touching):
  - `papers/tables/T01.tex … T16.tex`, `T16_bca.tex`, `T21.tex`, `T22.tex`
    (LaTeX `tabular` fragments, `\input`-ed inside `table` floats in
    `sections/*.tex`);
  - `papers/figures/ranks/` (`nemenyi_cd_d50.pdf`, `friedman_gsk_family.pdf`);
  - `papers/figures/convergence/` (per-cell PNGs and `all_funcs_*` / `cec2011_*`
    multi-panel PDFs);
  - `papers/figures/flowchart/` (`dt_gsk_flowchart.pdf` + preview PNG);
  - `papers/figures/taxonomy/` (`metaheuristic_tree.pdf` + preview PNG);
  - `papers/figures/traces/` (`ace_probability_F14_D10.pdf`,
    `adaptive_params_all_D10.pdf`, `nlpsr_trajectory.pdf`,
    `accept_diversity_F14_D10.pdf`);
  - `papers/figures/diagrams/` (`.gitkeep` — currently empty).
- **Macros already defined in `papers/main.tex`** (lines ~40–50; do not
  redefine): `\ismgsk \sgsm \atmals \agsk \apgsk \fdbagsk \egsk`, and the
  exhibit macros `\bestval{#1}` (→ `\textbf`), `\wmark` (→ `+`), `\lmark` (→
  `-`), `\emark` (→ `≈`).

**Conventions to honour throughout** (Part 4.4 + C4):

- 7-algorithm panel, fixed order: `gsk, agsk, apgsk, fdb-agsk, atmals-gsk, egsk,
  dt-gsk`.
- CEC2017 is primary, D ∈ {10, 30, 50, 100}, **F2 excluded** → **N = 29**
  functions per Friedman panel (`DEFAULT_EXCLUDED_FUNCS = (2,)`; matches the
  F1,F3…F30 rows in `tables/T05.tex`). CEC2013 is the second comparison suite
  (28 functions, D ∈ {10, 30, 50}). Run counts: CEC2017 = 51, CEC2011 = 25,
  CEC2013 = 51.
- The Nemenyi CD figure lives in `papers/figures/ranks/`.
- Citations restricted to the **57 locked keys**. Statistics keys usable in
  captions: `friedman1937use`, `demsar2006statistical` (Friedman + Nemenyi CD),
  `wilcoxon1945individual`, `holm1979simple`, `benjamini1995controlling`,
  `vargha2000critique` (A12), `efron1993introduction` (BCa).

---

## Tasks

Work through 3.1 → 3.5 in order. Each micro-step names the exact command and the
exact file it writes. Regenerate; do not transcribe.

### 3.1 Main-text tables

The main text carries **three** tables (C4): one **per-dimension summary**, one
**ablation summary**, one **parameter-study summary**. Keep everything else in
the supplement (3.2). Every cell traces to a Phase-2 CSV.

**3.1.1 Regenerate the LaTeX fragments from committed data.** The family-report
CLI emits the Friedman-rank and Wilcoxon-summary fragments straight from the
structured statistics (via `gsk_family.analysis.latex_tables`), so they can never
drift from the numbers. Run it for the primary suite:

```bash
python -m gsk_family.cli.stats \
  --suite CEC2017 --dims 10,30,50,100 \
  --proposed dt-gsk \
  --out results/_run_all/_analysis/cec2017
# equivalent console entry point (pyproject [project.scripts]):
# gsk-stats --suite CEC2017 --dims 10,30,50,100
```

This (re)writes into the `--out` directory:
`cec2017_friedman_ranks.tex`, `cec2017_wilcoxon_summary.tex`,
`cec2017_friedman_ranks.csv`, `cec2017_statistical_report.txt`, and
`figures/nemenyi_cd_cec2017_D*.png` + `figures/friedman_ranks_cec2017_D*.png`.
Pass `--no-figures` if you only want the `.tex`/`.csv` refresh.

> **What `latex_tables.py` guarantees.** `friedman_ranks_latex()` orders
> algorithms by overall mean rank (best first), bolds the minimum rank per
> dimension column and the overall column with `\bestval{}`, and appends an
> `Overall` column. `wilcoxon_summary_latex()` emits, per dimension, the seven
> columns `p / p_Holm / + / = / - / A12 / Dec.` with the Holm-corrected decision
> already resolved to `+` / `-` / `=`. Both are bare `tabular` fragments (no
> float, no caption) — exactly the shape the existing `tables/T*.tex` slots use.

**3.1.2 Bind the fragments into the `tables/T*.tex` slots.** For each main-text
table, confirm the target `T*.tex` slot in the Phase-0 asset map, then bind the
generated fragment to it. Two acceptable binding styles (pick one per slot and be
consistent):

- **Direct input** — point the `table` float at the generated fragment path (only
  if that path is inside the committed tree), or
- **Copy-in** — overwrite the `tables/T*.tex` fragment with the freshly generated
  fragment's bytes.

Never edit the copied bytes afterward. The float, caption, and label live in the
`sections/*.tex` file that `\input`s the slot; the numbers live only in the
fragment. Existing wiring pattern to match (from
`sections/supplementary_content.tex`):

```latex
\begin{table}[htbp]
  \caption{...}\label{tab:...}
  \centering
  \resizebox{\textwidth}{!}{\input{tables/T09}}
\end{table}
```

**3.1.3 Assemble the per-dimension summary table.** This composite exhibit is the
main-text headline table. Per algorithm (rows, in panel order) it reports, for
each dimension:

- central tendency + spread — **mean ± std** (or **median / IQR** if the
  distribution is skewed; pick one convention and state it in the caption);
- **win / tie / loss vs. each baseline** — take the `+ / = / -` counts directly
  from `cec2017_wilcoxon_summary.tex` (proposed vs. each comparator; do not
  recount);
- a **Friedman-rank row** — take the mean ranks from
  `cec2017_friedman_ranks.csv` / `cec2017_friedman_ranks.tex`.

Best-in-row uses `\bestval{}`; significance vs. the relevant baseline uses
`\wmark` (proposed better), `\lmark` (proposed worse), `\emark` (no significant
difference), reading the Holm-corrected `Dec.` column. Keep the numeric cells
identical to the source CSVs — the only additions are the macros. See the worked
skeleton in the *Worked examples* section.

**3.1.4 Ablation summary table.** One row per scaffold-ablation cell — the
remove-one design of `scripts/run_ablation.py`: **6 mechanisms + baseline =
7 cells** (ACE, NLPSR, BSE, linkage-aware crossover, Nelder–Mead endgame,
elite archive; SGSM is off in every cell; ARGP / eigenframe final-polish /
deep-stall restart are commented-out extras). Columns: mean Friedman rank,
Δ vs the full (baseline) cell, best-case count, and the full-vs-cell
Holm-corrected Wilcoxon verdict. Source every value from the committed matrix
`results/ablation/ablation_matrix_rank_summary_<suite>[_D<dim>].csv` named in
the Phase-2 binding map; the rendered fragment is
`papers/tables/ablation_<tag>.tex`, emitted by `gen_ablation_table()` in
`papers/scripts/generate_latex_tables.py` — never hand-typed. Bold the
full-scaffold (baseline) row or the best delta with `\bestval{}`. Report
regressions honestly (C7): a mechanism that *hurts* on some D must show its
positive delta, not be hidden. (The SGSM overlay is ablated separately via the
CEC2013 hold-out design — do not conflate the two.)

**3.1.5 Parameter-study summary table.** Condense the hyperparameter sweep to the
main-text-worthy rows only (the swept parameter, the values tried, the best
setting, and the metric at that setting) from the committed sweep-grid CSV. The
**full grid** goes to the supplement (3.2). Bold the selected operating point
with `\bestval{}`.

**3.1.6 Keep numbers bound to CSVs.** For every main-text table, record in the
binding map: `T*.tex slot → source CSV → generator command → commit SHA`. This is
the artifact the Phase 8 data-binding check (`PAPER_BUILD_PROMPT.md` Appendix D.3)
re-runs. A cell whose value is not reproducible by re-running the named command
is a defect.

### 3.2 Supplementary tables

Everything not in the three main tables (C4). Naming: caption as **"Table S-x"**
(supplement numbering), `\label{tab:...}` in `sections/supplementary_content.tex`.
These are already partly wired — regenerate their fragments, do not re-invent the
floats.

**3.2.1 Full per-function results per dimension.** For every D, the per-function
Best / Median / Worst / Mean / SD table (proposed vs. each comparator). Confirmed
existing slots: `tables/T02.tex` (D10), `T03.tex` (D30), `T04.tex` (D50),
`T05.tex` (D100) for the `\ismgsk` vs. GSK head-to-head, and `T07.tex` (D10),
`T08.tex` (D30), `T09.tex` (D50), … for the wider GSK-family comparison. Each is
a `tabular` fragment with `\bestval{}` on the best Mean per function
(F1, F3, …, F30 — 29 rows, F2 excluded). Regenerate every cell from the
source-of-truth summary CSVs named in the binding map; keep the F-row ordering and
the panel column order fixed.

**3.2.2 Full pairwise Wilcoxon matrices.** The complete per-dimension matrices
(every algorithm vs. every algorithm, not just proposed-vs-comparator), with raw
and Holm-adjusted p-values (`holm1979simple`; use the Benjamini–Hochberg variant
only where the prose frames results as FDR, `benjamini1995controlling`). The
proposed-vs-family summary (`cec2017_wilcoxon_summary.tex`) is the main-text
condensation; the full matrix is supplement-only. Confirmed slot `tables/T06.tex`
holds the CEC2011 Wilcoxon table; map the remaining matrices to their slots via
the Phase-0 asset map.

**3.2.3 Full sweep grids.** The complete hyperparameter grid behind the 3.1.5
summary, and any extended ablation grid behind 3.1.4. One fragment per grid;
`\bestval{}` on the selected point.

**3.2.4 Naming/labeling discipline.** Every supplementary table's caption begins
"Table S-x"; every `\label` is unique and referenced at least once from the
supplement body (3.2 exhibits may be referenced from the main text via a
"full results in Table S-x" pointer, which Phase 5 wires). No orphan tables.

### 3.3 Figures

Six families live under `papers/figures/`. Main text gets the Nemenyi CD figure +
2–3 convergence curves + the method/related-work diagrams; the rest go to the
supplement.

**3.3.1 Nemenyi critical-difference diagram (main; `figures/ranks/`).** Produced
by `gsk_family.analysis.figures.render_cd_diagram()` from the same
`{algorithm: mean_rank}` mapping the Friedman table uses, so the CD figure and the
rank table are guaranteed consistent (`friedman1937use`, `demsar2006statistical`).
The `gsk-stats` run in 3.1.1 already emits PNGs
(`figures/nemenyi_cd_cec2017_D*.png`) into the stats bundle. For **print quality**
the main-text figure must be a PDF in `papers/figures/ranks/`; `render_cd_diagram`
infers the format from the output suffix, so render a vector copy directly. Choose
the dimension that best states the thesis (a committed example already exists:
`figures/ranks/nemenyi_cd_d50.pdf`). Minimal driver reading the committed
mean-rank CSV:

```bash
python - <<'PY'
import csv
from pathlib import Path
from gsk_family.analysis.figures import render_cd_diagram

# Read committed Friedman mean ranks (source of truth) for the chosen D.
csv_path = Path("results/_run_all/_analysis/cec2017/cec2017_friedman_ranks.csv")
DIM = 50            # dimension whose CD panel goes to the main text
N_FUNCS = 29        # CEC2017 with F2 excluded
ranks = {}
with csv_path.open(newline="", encoding="utf-8") as fh:
    for row in csv.DictReader(fh):
        ranks[row["algorithm"]] = float(row[f"D{DIM}"])   # column key per the CSV header

render_cd_diagram(
    ranks, n_funcs=N_FUNCS,
    out_path="papers/figures/ranks/nemenyi_cd_d50.pdf",
    suite="CEC2017", dim=DIM, proposed="dt-gsk",
)
PY
```

> Confirm the CSV's column header names before wiring (`D10`/`D30`/… vs a
> `dim` column) against the actual `cec2017_friedman_ranks.csv`; the loop key must
> match. The proposed algorithm is drawn in the deep-blue accent (`#1F4E9D`); all
> comparators in slate grey (`#6E7B8B`) — a two-colour, colour-blind-safe scheme
> where hue is redundant with position (best rank on top).

The companion mean-rank bar chart (`figures/ranks/friedman_gsk_family.pdf`) comes
from `render_rank_chart()` the same way if the paper uses it.

**3.3.2 Convergence curves (2–3 in main; rest to supplement).** Regenerate PNGs
from the committed per-run curve CSVs — **no optimizer re-run**. The multi-panel
paper figures come from the dedicated generators, which read curves/gen_logs
from `benchmarks/cec_reference_results/`:
`papers/scripts/generate_full_convergence.py` (CEC2017 grids),
`generate_cec2011_convergence.py`, `generate_cec2013_convergence.py` (28
functions, 4 subfigures a–d). For single-cell renders:

```bash
python scripts/plot_convergence_from_curves.py \
  --root benchmarks/cec_reference_results/cec2017/dt-gsk \
         benchmarks/cec_reference_results/cec2017/apgsk
```

This writes one PNG per cell to `<root>/curves/graphs/Figure_F<f>_D<d>.png`
(a derived render artifact — the underlying reference CSVs are never edited)
(x-axis = Evaluations, y-axis = "Best error" for CEC2017 / "Best fitness" for
CEC2011, title = "`<optimizer> <suite> F<f> D<d>`", single median-run line per
cell). Select the main-text cells deliberately (C4, Part 6.6):

- **one clear win** — a cell where DT-GSK's curve separates cleanly (e.g. an
  F-D cell with a large mean-error gap in the per-function table);
- **one honest hard case** — a cell where DT-GSK ties or loses (the limitations
  paragraph must have a figure to point at; hiding it violates C7);
- optionally a third that illustrates a specific mechanism (e.g. late-run polish).

Copy the chosen PNGs into `papers/figures/convergence/` under the existing naming
(`F<f>_D<d>.png`, e.g. the committed `F15_D50.png`, `F04_D30.png`). The committed
multi-panel PDFs (`all_funcs_D*_*.pdf`, `cec2011_*.pdf`) are supplement exhibits
already wired in `sections/supplementary_content.tex`; regenerate them only if
their upstream CSVs changed. **All remaining per-cell curves go to the
supplement.**

> The committed script plots a **single median-run series per cell** (one line).
> It does not overlay the 7-algorithm panel. If the main-text convergence figure
> is meant to overlay algorithms, that overlay is a pre-existing committed
> multi-panel PDF, not an output of this script — do not fabricate an overlay the
> script cannot produce; use the committed PDF or select single-series panels.

**3.3.3 Architecture flowchart & taxonomy.** These support the method and
related-work sections and are static, committed vector art:

- `papers/figures/flowchart/dt_gsk_flowchart.pdf` — the DT-GSK architecture /
  control-flow diagram (junior/senior GSK phases → ACE → NLPSR → BSE → ARGP →
  SGSM → linkage-aware crossover → eigenframe polish → Nelder–Mead endgame).
- `papers/figures/taxonomy/metaheuristic_tree.pdf` — the metaheuristic taxonomy
  locating the GSK family (for related work).

Neither is data-driven, so there is no CSV to bind; verify they are current
against the method description and leave them otherwise untouched. Keep the
`_preview.png` companions in sync if the PDFs change.

**3.3.4 Trace / diagnostic plots (`figures/traces/`, `figures/diagrams/`).**
Committed diagnostics — `ace_probability_F14_D10.pdf` (ACE operator-selection
probabilities), `adaptive_params_all_D10.pdf` (adaptive-parameter trajectories),
`nlpsr_trajectory.pdf` (population-size schedule), `accept_diversity_F14_D10.pdf`
(acceptance/diversity). Each must trace to a committed diagnostic CSV named in the
binding map. `figures/diagrams/` is currently empty (`.gitkeep`); add a diagram
here only if a section calls for one, and only if it is bound to committed data or
is static schematic art. Any trace plot used in the main text counts against the
page budget — default these to the supplement unless a specific claim needs one.

### 3.4 Legibility pass

Apply to **every** exhibit (main and supplement). This is the R2 gate.

- **Axes.** Every axis labelled, with units where they exist. Convergence:
  x = "Evaluations" (state MaxFES budget in the caption), y = "Best error"
  (CEC2017) / "Best fitness" (CEC2011); use a log scale for error and label it as
  log. CD figure: x = "Mean Friedman rank (lower is better)".
- **Fonts.** Legible at final print size. Do not rely on `\resizebox` shrinking a
  wide table into unreadability (see Pitfalls). Figure tick/label fonts must
  survive single-column MDPI width.
- **Colour.** Colour-blind-safe only. The rank/CD palette (deep blue + slate
  grey) already satisfies this and keeps hue redundant with position. For any
  multi-series figure, distinguish series by **line style / marker as well as
  colour**, never colour alone.
- **Captions.** Every caption is **standalone**: it states the suite, dimension,
  run count (n = 51 for CEC2017/CEC2013, n = 25 for CEC2011), what "best" means,
  what the marks (`\wmark/\lmark/\emark`)
  denote, and the statistical test with its citation where relevant. A reader must
  understand the exhibit without the body text (Part 6, R2 rubric 9.2).

### 3.5 Regenerate everything from committed CSVs

- **Never hand-edit a plotted or tabulated number.** Every table cell and figure
  point is emitted by a named script from a committed CSV (C2). If a number is
  wrong, fix the CSV upstream (Phase 2) and re-run the generator — do not patch
  the `.tex`/figure.
- **Re-run order for a full refresh:**
  1. `python -m gsk_family.cli.stats --suite CEC2017 --dims 10,30,50,100` (tables
     + CD/rank figures into the stats bundle);
  2. the CD-PDF driver in 3.3.1 (vector copy into `figures/ranks/`);
  3. the convergence generators (`papers/scripts/generate_full_convergence.py`,
     `generate_cec2011_convergence.py`, `generate_cec2013_convergence.py`, all
     reading `benchmarks/cec_reference_results/`; or
     `python scripts/plot_convergence_from_curves.py --root …` for single cells),
     then copy the selected cells into `figures/convergence/`;
  4. copy the regenerated `.tex` fragments into their `tables/T*.tex` slots.
- **Verify a figure matches its CSV.** Spot-check: the CD figure's top algorithm
  and its printed rank value must equal the minimum-rank row of
  `cec2017_friedman_ranks.csv`; a convergence curve's final y-value must equal the
  last `BestError` row of its `Figure_F<f>_D<d>_Run#<n>.csv`. For a table, re-run
  the generator into a scratch dir and `diff` against the committed fragment — a
  clean diff proves the binding.

```bash
# Binding self-check: regenerate to scratch and diff against the committed fragment.
python -m gsk_family.cli.stats --suite CEC2017 --dims 10,30,50,100 \
  --no-figures --out "$TMPDIR/stats_check"
diff -u results/_run_all/_analysis/cec2017/cec2017_friedman_ranks.tex \
        "$TMPDIR/stats_check/cec2017_friedman_ranks.tex"   # expect no differences
```

(On PowerShell, use the scratchpad dir for `--out` and `Compare-Object`/`git diff
--no-index` in place of `diff`.)

---

## Worked examples

### A. Convergence PNG from committed curves (no re-run)

```bash
# Render every committed cell for two optimizers; then hand-pick main-text cells.
python scripts/plot_convergence_from_curves.py \
  --root benchmarks/cec_reference_results/cec2017/dt-gsk \
         benchmarks/cec_reference_results/cec2017/apgsk
# -> benchmarks/cec_reference_results/cec2017/dt-gsk/curves/graphs/Figure_F*_D*.png
# -> benchmarks/cec_reference_results/cec2017/apgsk/curves/graphs/Figure_F*_D*.png
# (derived render artifacts; the reference CSVs themselves are never edited)
# Copy the chosen win + hard-case cells into papers/figures/convergence/
# under the existing F<f>_D<d>.png naming (e.g. F18_D50.png win, F16_D30.png hard case).
```

### B. Main-text per-dimension summary — booktabs skeleton

`tables/T<slot>.tex` fragment (numbers copied verbatim from the source CSVs;
only the macros are added). `\bestval` bolds best-in-row; `\wmark/\lmark/\emark`
read the Holm-corrected decision vs. the reference method:

```latex
\begin{tabular}{l r r r r}
\toprule
\textbf{Algorithm} & \textbf{D10} & \textbf{D30} & \textbf{D50} & \textbf{D100} \\
\midrule
\gsk         & 5.83\,\lmark & 6.10\,\lmark & 6.21\,\lmark & 6.34\,\lmark \\
\agsk        & 4.02\,\lmark & 3.88\,\lmark & 3.95\,\lmark & 4.10\,\lmark \\
\apgsk       & 3.41\,\lmark & 3.20\,\lmark & 3.05\,\emark & 3.12\,\lmark \\
\fdbagsk     & 4.55\,\lmark & 4.31\,\lmark & 4.40\,\lmark & 4.28\,\lmark \\
\atmals      & 3.10\,\emark & 3.02\,\lmark & 2.98\,\lmark & 2.90\,\lmark \\
\egsk        & 3.28\,\lmark & \bestval{2.41} & 2.86\,\emark & 2.71\,\lmark \\
\ismgsk      & \bestval{2.81} & 2.58 & \bestval{2.55} & \bestval{2.45} \\
\midrule
\multicolumn{5}{l}{\footnotesize Mean Friedman rank (lower is better); \bestval{best} per column.}\\
\multicolumn{5}{l}{\footnotesize vs.\ \ismgsk: \wmark\ better, \lmark\ worse, \emark\ n.s.\ (Wilcoxon, Holm-corrected).}\\
\bottomrule
\end{tabular}
```

> The numeric values above are **placeholders for shape only** — the real
> fragment is the byte-for-byte output of `friedman_ranks_latex()` from
> `cec2017_friedman_ranks.csv`, plus the marks from
> `cec2017_wilcoxon_summary.tex`. Never type ranks by hand.

### C. Self-contained caption

```latex
\begin{figure}[htbp]
  \centering
  \includegraphics[width=0.78\textwidth,keepaspectratio]{figures/ranks/nemenyi_cd_d50.pdf}
  \caption{Nemenyi critical-difference diagram for the seven-member GSK family on
  CEC~2017 at $D = 50$ ($N = 29$ functions, F2 excluded; $n = 51$ runs each;
  $\alpha = 0.05$). Bars give the mean Friedman rank (lower is better);
  \ismgsk{} is highlighted. Algorithms whose ranks differ by less than the
  critical difference (CD bar, top) are statistically indistinguishable
  \citep{friedman1937use,demsar2006statistical}.}
  \label{fig:cd_d50}
\end{figure}
```

---

## Pitfalls & anti-patterns

- **Shrinking a figure/table to hit the page budget until it is illegible.** A
  `\resizebox{\textwidth}{!}{…}` that crushes a 7-column-per-dimension Wilcoxon
  table below print legibility is a **design smell, not a solution** (C3). The
  fix is to migrate the exhibit to the supplement (C4), not shrink it. The main
  text carries the *condensed* summary; the full grid lives in "Table S-x".
- **Hand-editing a number.** Typing or "correcting" a value in a `.tex` fragment
  or re-drawing a curve point breaks the C2 binding and will fail the Phase-8
  data-binding check. Fix upstream, regenerate.
- **Unreferenced exhibits.** A table or figure never `\ref`-ed from the text is an
  R2 must-fix. Every exhibit is referenced exactly where it is discussed (Phase-4
  concern, but Phase 3 must not create exhibits no section will use).
- **Colour-only encoding.** Distinguishing series by hue alone fails colour-blind
  readers. Use position (CD/rank charts already do) or line-style + marker for
  multi-series plots.
- **Captions that need the body text.** A caption that omits the suite,
  dimension, run count, or the meaning of its marks forces the reader back into
  the prose — an R2 clarity failure. Make every caption self-contained (3.4).
- **Cherry-picked convergence set.** Showing only wins violates C7. The main-text
  set must include at least one honest hard case.
- **Silent panel/order drift.** Re-ordering the 7-algorithm panel or dropping/
  adding a function between a table and its figure desynchronises the CD figure
  from the rank table. Keep panel order and the N = 29 function set fixed across
  every exhibit.

---

## Exit gate

Do not cross into Phase 4 until **all** hold, each with evidence:

- [ ] **Standalone readability.** R2 can read every exhibit — main and supplement
  — without the body text: axes labelled with units, print-legible fonts,
  colour-blind-safe encoding, self-contained caption stating suite / D / n /
  "best" / marks / test.
- [ ] **Referenceability.** Every exhibit has a unique `\label`; nothing is
  created that no section will `\ref` (main-text exhibits are referenced where
  discussed; supplementary "Table S-x" / figures are pointed to from the main
  text or the supplement body).
- [ ] **Every number bound to a CSV.** Each table cell and figure point
  regenerates from a committed CSV via a named command; the binding map records
  `slot → CSV → command → commit SHA`; the 3.5 regenerate-and-diff check is clean.
- [ ] **Main/supplement split honoured (C4).** Main text = one per-dimension
  summary + ablation summary + parameter-study summary + Nemenyi CD figure + 2–3
  convergence curves (incl. an honest hard case) + the method/taxonomy diagrams.
  Everything else (full per-function tables all D, full pairwise Wilcoxon
  matrices, full sweep grids, all remaining convergence curves) is in the
  supplement. No exhibit critical to the conclusion is supplement-only.
- [ ] **Citations closed.** Every caption citation is within the 57 locked keys
  (statistics: `friedman1937use`, `demsar2006statistical`,
  `wilcoxon1945individual`, `holm1979simple`, `benjamini1995controlling`,
  `vargha2000critique`, `efron1993introduction`).

---

## Hand-off

Phase 3 delivers the final `papers/tables/*.tex` and `papers/figures/**`
exhibits, each bound to Phase-2 data and each regenerable by a named command.
Hand to **`PHASE_4_drafting.md`**, which drafts `sections/*.tex` (Method → Setup →
Results → Related work → Introduction → Conclusion → Abstract) and inserts the
`\ref`/`\cite` that place these exhibits exactly where they are discussed. Give
Phase 4: (1) the updated table→CSV→command→SHA binding map, (2) the list of
main-text vs. supplementary exhibit labels, and (3) the chosen convergence cells
(the win + the honest hard case) so the Results narrative promises exactly what
the figures show.
