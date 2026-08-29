# Statistical Analysis (GSK-family comparison)

> **What this page is.** The statistical-comparison suite that ranks the
> proposed optimizer against the GSK-family panel — Friedman ranks, Nemenyi
> critical difference, pairwise Wilcoxon, Holm correction, and effect sizes —
> and how to run it and read its output.
>
> **Who it is for.** Anyone producing or interpreting the family-comparison
> statistics, from a quick `gsk-stats` run to the paper's published panels.
>
> **What you will get.** What each test computes and why, where the input data
> comes from, `gsk-stats` usage and options, the output files, the paper
> review pack, and a map of the analysis modules.
>
> **Prerequisites.** The run workflow is in the
> [Researcher Handbook](researcher_handbook.md); hand-checkable arithmetic for
> the tests is in [Numerical Examples](numerical_examples.md). Terms are
> defined in [the glossary](../reference/glossary.md).

This project ships a paper-grade statistical-comparison suite for the proposed
optimizer (`dt-gsk` by default) against the GSK-family comparators. It was
migrated from the source DT-GSK project and retargeted to this repository's
committed reference tables (`benchmarks/cec_reference_results/`) with the
`results/_run_all/<optimizer>/<suite>/summary/` layout as a fallback. The suite
lives in `src/gsk_family/analysis/` and is driven by the `gsk-stats` console
script.

## What it computes

For each requested dimension the suite builds the **7-algorithm GSK-family
panel** — the proposed algorithm plus the six committed reference comparators
(`gsk`, `agsk`, `apgsk`, `fdb-agsk`, `egsk`, `atmals-gsk`) — over the common
benchmark functions, and reports the statistics below. The committed reference
tree carries the full 7-optimizer panel for three suites: **CEC2017**
(F1, F3–F30 — the withdrawn F2 is excluded — at D = 10/30/50/100, 51 runs),
**CEC2011** (22 real-world problems at their native per-function dimensions,
25 runs), and **CEC2013** (the second comparison suite: 28 functions at
D = 10/30/50, 51 runs, no exclusions).

- **Friedman ranking** — average rank per algorithm (lower is better) with the
  Friedman chi-squared p-value (`statistical_tests.friedman_rank_test`).
- **Nemenyi critical difference (CD)** — the two-tailed post-hoc threshold
  `CD = q_alpha * sqrt(k (k+1) / (6 N))` (Demsar 2006, Table 5), rendered as a
  Demsar-style CD diagram.
- **Pairwise Wilcoxon signed-rank tests** — proposed vs each comparator on the
  per-function mean errors, with R+/R-, win/tie/loss, two-sided p-value, the
  standardized effect size `r = Z / sqrt(n)`, and the function-level Cliff's δ.
- **Holm correction** — family-wise adjustment of the per-dimension comparator
  p-values, yielding the corrected decision (`+` / `=` / `-`).
- **Vargha-Delaney A12** — probability of superiority on the per-function mean
  errors (> 0.5 favours the proposed algorithm).

## Methodology in detail

Each test answers a different question; together they form the standard
non-parametric comparison protocol for stochastic optimizers (Demsar 2006).

### Friedman ranking and Nemenyi critical difference

Within each benchmark function the `k = 7` algorithms are ranked by mean error
(rank 1 = lowest error); each algorithm's ranks are then averaged across the `N`
functions. The Friedman chi-squared statistic tests the null hypothesis that all
mean ranks are equal.

Because the `1e-8` success floor collapses many distinct solver outcomes onto
exactly `0.0`, tied ranks are common — 9 of the 29 CEC2017 functions at D=10, for
instance. Tied rows shrink the rank variance and bias the raw chi-squared
*downwards* (making the uncorrected test conservative), so `friedman_rank` in
`analysis/statistics.py` also returns the **tie-corrected** statistic `chi2 / C`
with

```text
C = 1 - sum_i sum_g (t_ig^3 - t_ig) / ( N (k^3 - k) )
```

where `t_ig` is the size of the g-th tie group in function `i`. Since `C <= 1`
the correction can only *raise* significance, and it leaves the average ranks —
hence the ranking itself — untouched (`tie_correction`, `statistic_tie_corrected`
on the returned `FriedmanSummary`).

If the omnibus test rejects, the **Nemenyi** post-hoc gives the critical
difference

```text
CD = q_alpha * sqrt( k (k + 1) / (6 N) )
```

(Demsar 2006, Table 5 supplies `q_alpha`). Two algorithms differ significantly
only if their average ranks differ by more than `CD`; the CD diagram draws a bar
of that width so groups that are statistically indistinguishable are visibly
connected. A [worked three-algorithm ranking](numerical_examples.md#friedman-average-rank-by-hand)
shows the averaging by hand.

### Pairwise Wilcoxon signed-rank

The proposed algorithm is paired against each comparator **by function**, using
per-function mean errors, with the convention that a positive difference
`ref_mean - new_mean` means the proposed algorithm is better. The test reports
`R+`/`R-`, win/tie/loss, the two-sided p-value, and the standardized effect size
`r = Z / sqrt(n)`. To keep the effect size numerically consistent with the
p-value on the same line, `|Z|` is recovered by inverting the two-sided p-value
(so the continuity and ties corrections SciPy applies to the variance flow
through automatically), then signed from the rank sums — `R+ > R-` gives `r > 0`,
oriented so **positive `r` favours the proposed algorithm**. Ties use a
scale-aware band (an absolute floor plus a relative term) so sub-noise
differences on large-magnitude functions are not miscounted — see the
[win/tie/loss worked example](numerical_examples.md#pairwise-win-tie-loss-wilcoxon-framing).

### Holm correction

Running one Wilcoxon test per comparator inflates the family-wise error rate, so
the per-dimension comparator p-values are adjusted with **Holm's** sequentially
rejective procedure: sort the `m` raw p-values ascending, multiply the rank-`i`
value (0-indexed) by `(m - i)`, enforce monotonicity, and clip to 1.0. A
comparison is significant when its adjusted p-value is below `alpha` (default
`0.05`). The corrected per-comparator decision is rendered as `+` (proposed
wins), `=` (no significant difference), or `-` (proposed loses). The vendored core
also provides a Benjamini-Hochberg FDR variant for reference.

Worked example — three comparators with raw p-values `[0.004, 0.030, 0.045]`
(`m = 3`), following `holm_correction` in `analysis/statistics.py` exactly:

```text
sort ascending:   0.004 (i=0)   0.030 (i=1)   0.045 (i=2)
step multiplier:  x (3-0)=3     x (3-1)=2     x (3-2)=1
raw x mult:       0.012         0.060         0.045
enforce monotone: 0.012         0.060         max(0.045, 0.060) = 0.060
decision @0.05:   significant   not sig.      not sig.
```

The third comparator has raw `p = 0.045 < 0.05` yet ends **non-significant**:
Holm's monotonicity clamp lifts its adjusted value to the running maximum
(`0.060`). That is the point of a step-down correction — a later hypothesis
cannot be rejected once an earlier, smaller raw p-value has already failed, so
reading the *raw* 0.045 as a win would be exactly the error the correction
exists to prevent.

### Effect sizes

Significance says a difference is unlikely to be chance; **effect size** says how
large it is. The suite reports two:

- **Vargha-Delaney A12** — probability that a randomly chosen proposed-algorithm
  value is better (lower) than a comparator value. Magnitude thresholds follow
  Vargha & Delaney (2000): negligible `0.44-0.56`, small, medium, large
  (`A12 > 0.71` or `< 0.29`). `A12 > 0.5` favours the proposed algorithm.
- **Cliff's delta** — a per-function rank-based effect size reported alongside the
  Wilcoxon panel.

BCa (bias-corrected and accelerated) bootstrap confidence intervals are available
in the vendored core (`bootstrap_bca_ci`) for interval estimates on these
statistics.

### Published-panel statistics (the paper's tool of record)

`gsk-stats` is the live, interactive comparison tool. The **released** paper
tables under `papers/analysis/rel-2026-07-20-67d9345f9/` are produced by
`papers/scripts/phase6_run_analysis.py`, which builds on the same
`analysis/statistics.py` core and reports two further forms derived from it:

- **Iman-Davenport `F`** — the Friedman omnibus decision statistic, computed from
  the *tie-corrected* chi-squared (above) as `F = (N-1) * chi2 / (N*(k-1) - chi2)`
  and tested against `F(k-1, (k-1)(N-1))`. It replaces the raw chi-squared p-value
  as the reported omnibus decision; the columns `friedman_chi2`,
  `iman_davenport_F`, `tie_correction_C`, `n_tied_functions` (plus `*_uncorrected`
  companions) live in `friedman_ranks_<suite>[_D<dim>].csv`.
- **Matched-pairs rank-biserial `r`** — the paired Wilcoxon effect size
  `r = (R- - R+) / (R+ + R-)`, negated from the textbook `(R+ - R-)/(R+ + R-)` so
  that, on error differences (lower is better), **`r > 0` favours the proposed
  algorithm** — the same orientation as the `direction` field and the `A12 > 0.5`
  convention. It is carried in `wilcoxon_holm_<suite>[_D<dim>].csv` alongside
  `w_plus`, `w_minus`, the Holm-adjusted `p_holm`, and the `win`/`tie`/`loss`
  `outcome`.

These are reporting refinements over the same underlying tests, not a different
analysis: the tie correction leaves ranks untouched and the rank-biserial only
re-expresses the signed-rank sums, so no rank, sign, or decision changes as a
result of adopting them.

## Data sources

The committed reference panel is the paper's **single source of truth** for
every algorithm — the proposed method included:

- **Every** algorithm (proposed and comparators alike) is loaded
  **reference-first** from
  `benchmarks/cec_reference_results/<suite>/<optimizer>/`. Each optimizer
  directory uses a flat layout: `<opt>_<suite>_D<dim>.csv` per-dimension
  summaries (plus a `<opt>_cec2011.csv` rollup for CEC2011), `per_run.csv`,
  provenance files (`environment.json`, `run_config.json`, `seed_schedule.csv`,
  `verification.json`, `phase0_protocol.json`), and the `curves/` and
  `gen_logs/` convergence assets.
- A **locally reproduced run** under
  `results/_run_all/<optimizer>/<suite>/summary/` is used only as a **fallback**
  for cells the reference tree does not carry. The policy is implemented in
  `analysis/result_loader.py` (`load_algorithm`: reference first, reproduced
  fallback) and `analysis/family_report.py` (`analyze_family` resolves the
  proposed method's CSV the same way).

Two resolution caveats when working below the per-function summaries:

- The panel statistics themselves operate on **per-function mean errors** (one
  value per function), never on raw per-run values.
- `per_run.csv` gives full per-run (seed-level) resolution for **`dt-gsk`** on
  every panel suite and dimension; some comparators carry only **partial**
  per-run coverage (their per-dimension summary CSVs are the complete source).
  Seed-matched per-run analyses are therefore guaranteed only for the proposed
  method — comparator claims should stay at per-function summary resolution.

## Usage

```powershell
# CEC2017 family report for the default dimensions (10, 30, 50, 100)
gsk-stats --suite CEC2017

# Specific dimensions, no figures
gsk-stats --suite CEC2017 --dims 10,30 --no-figures

# CEC2011 (per-function native dimensions; uses the rollup summary)
gsk-stats --suite CEC2011

# CEC2013 (second comparison suite: 28 functions, D = 10/30/50)
gsk-stats --suite CEC2013 --dims 10,30,50
```

### During a run (`--stats`)

The experiment runner can also stream the per-dimension analysis live, matching
the reference project. Pass `--stats` to `gsk-run`/`run.py` and, after each
dimension completes, the runner prints the Wilcoxon signed-rank panel + the
GSK-family Friedman ranking + a compact TL;DR banner, plus a cross-dimension
summary at the end. It is opt-in (default off), skips vanilla `gsk`, and covers
both the fixed-dimension suites and the native-dimension `cec2011` rollup
(emitted once as a single per-suite panel after the rollup CSV lands):

```powershell
gsk-run --optimizer dt-gsk --suite cec2017 --dimension 10 --dimension 30 --stats
```

`gsk-stats` remains the way to produce the figures, CSV, and LaTeX artifacts
after a run; `--stats` is purely the live console/per-run report.

**Self-validation against a committed reference table.** The `--stats` path has a
generic self-validation hook: when it runs an optimizer that has *committed
reference results of its own* under
`benchmarks/cec_reference_results/<suite>/<optimizer>/`, those results are folded
into the panel as an extra `<OPT>-REF` comparator (a Wilcoxon comparison plus a
row in the Friedman ranking) **while retaining the comparisons with the other
GSK-family algorithms**. This hook is general and only fires when such a
self-reference table is present.

Because the committed reference tree now carries the full DT-GSK panel for
CEC2017, CEC2011, and CEC2013 (it is the paper's single source of truth — see
[Data sources](#data-sources)), this hook **does** fire when you re-run
`dt-gsk` with `--stats`: the freshly reproduced run is compared against the
committed reference DT-GSK as an `DT-GSK-REF` row. Read that row as a
**reproduction/self-consistency check** on your local run — not as a paper
result; the paper's DT-GSK numbers are the committed reference tables
themselves.

### `gsk-stats` options

Key options: `--proposed` (default `dt-gsk`), `--dims` (default: the suite's
standard set), `--results-root` (default `results/_run_all`), `--reference-root`
(default `benchmarks/cec_reference_results`), `--out`
(default `<results-root>/_analysis/<suite>`), `--alpha` (default `0.05`), and
`--no-figures`. Passing `--strict-source` switches to **publication mode**: the
loader refuses any empirical input outside the immutable evidence release
(`benchmarks/cec_reference_results/` — no `results/` fallback; a missing cell
fails loudly) and writes a `source_use_audit.csv` of every opened data file next
to the report. The command exits nonzero when the reference tree is missing, or
when the proposed optimizer has neither a committed reference table nor a
reproduced fallback run for the requested suite/dimensions.

## Outputs

Written to `results/_run_all/_analysis/<suite>/` by default:

- `<suite>_statistical_report.txt` — concatenated per-dimension text report
  (Wilcoxon tables + Friedman table + peer comparison).
- `<suite>_friedman_ranks.csv` — algorithms x dimensions of mean ranks plus an
  `Overall_MeanRank` column.
- `<suite>_friedman_ranks.tex`, `<suite>_wilcoxon_summary.tex` — LaTeX
  `tabular` fragments (best values wrapped in a `\bestval{...}` macro).
- `figures/nemenyi_cd_<suite>_D<dim>.png`,
  `figures/friedman_ranks_<suite>_D<dim>.png` — matplotlib (Agg) figures.

### Reading the output

A defensible claim combines all three layers — never read one in isolation:

1. **Friedman + Nemenyi CD** (`*_friedman_ranks.csv`, the CD PNG): where the
   proposed algorithm sits in the overall ranking, and which competitors it is
   *not* statistically separated from (connected on the CD bar).
2. **Per-comparator Wilcoxon + Holm** (the text report, `*_wilcoxon_summary.tex`):
   the head-to-head `+`/`=`/`-` verdict after family-wise correction, with
   win/tie/loss counts.
3. **Effect size** (A12 / Cliff's delta): how *large* a significant difference is,
   so a statistically significant but practically negligible gap is not oversold.

Report the corrected (Holm) decision, not the raw p-value, when summarizing
multiple comparators in one dimension.

### Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `gsk-stats` exits nonzero, "no … summaries found" | The reference tree lacks the proposed optimizer for that suite **and** no local fallback run exists. | The committed panel already covers `dt-gsk` on CEC2017/CEC2011/CEC2013; for another `--proposed <id>` or suite, run `gsk-run` first. |
| `gsk-stats` exits nonzero, "reference tree missing" | `--reference-root` points nowhere. | Point it at `benchmarks/cec_reference_results`. |
| A comparator column is blank | No committed reference table for that algorithm/dimension. | Expected for partial coverage; it is omitted, not fabricated. |
| Figures not produced | `--no-figures` was passed. | Re-run without `--no-figures`. |
| CEC2011 ranks look off | CEC2011 uses native per-function dimensions and the rollup summary. | Run `gsk-stats --suite CEC2011` (no `--dims`). |

## Paper review pack

For advisor review, the `papers/` tree ships a standalone PDF builder that
complements `gsk-stats`. Run it from the project root:

```powershell
python papers/scripts/generate_review_pack.py
```

It writes `papers/DT-GSK-CEC2017-review.pdf` (matplotlib `PdfPages`, no LaTeX
needed for the review pack): a headline dashboard (Friedman ranks + Holm-
corrected Wilcoxon scoreboard), 7-algorithm CEC2017/CEC2011 per-function mean
tables, and **7-algorithm GSK-family convergence grids** (GSK, AGSK, APGSK,
FDB-AGSK, eGSK, ATMALS-GSK, DT-GSK). Each convergence curve is the mean
best-so-far error over an algorithm's runs, read from the shared CEC checkpoint
CSVs under `benchmarks/cec_reference_results/<suite>/<alg>/gen_logs/`
(comparators) and `results/_run_all/dt-gsk/<suite>/gen_logs/` (dt-gsk).
Missing `(algorithm, function, dimension)` curves are **never fabricated**: they
are skipped on the plot and recorded in
`papers/DT-GSK-CEC2017-review_missing.log`. See
[`papers/README.md`](../../papers/README.md) for the full page layout.

## Module map

| Module | Role |
| --- | --- |
| `analysis/statistics.py` | Vendored pure-NumPy core: Wilcoxon, Friedman, Holm, Benjamini-Hochberg, Vargha-Delaney, win/tie/loss, BCa bootstrap. |
| `analysis/statistical_tests.py` | Vendored scipy-backed layer: `wilcoxon_signed_rank`, `friedman_rank_test`, the formatted text report, and the `run_statistical_analysis` orchestrator. |
| `analysis/result_loader.py` | Loads reference + reproduced summaries into normalized `AlgorithmResult` records (reference takes priority; a reproduced run is the fallback). |
| `analysis/project_policy.py` | Runnable-optimizer and reference-comparator policy (single source of truth for the family panel). |
| `analysis/family_report.py` | Ties loading -> tests -> Holm/A12 -> figures/LaTeX/CSV/text into one report. |
| `analysis/figures.py` | Nemenyi CD diagram and Friedman rank-chart renderers (matplotlib Agg). |
| `analysis/latex_tables.py` | LaTeX `tabular` fragments built directly from the structured results. |
| `cli/stats.py` | The `gsk-stats` entry point. |

The vendored `statistics.py` and `statistical_tests.py` carry the published
formulas verbatim; the loader, figures, LaTeX, report orchestrator, and CLI are
target-native so the suite reads this repository's on-disk layout.
