# friedman_ranks — output schema (Phase 5 pre-registration)

**Filename pattern:** `friedman_ranks_<suite>_D<dim>.csv` (per dimension; carries the per-dimension Friedman test) and `friedman_ranks_<suite>_overall.csv` (DESCRIPTIVE cross-dimension aggregate; see below — no pooled test). cec2011: `friedman_ranks_cec2011.csv` only (22 problem blocks, native dims).

**One row per algorithm** (7 rows, P1 order). Function-level aggregation only: blocks are per-function mean errors from release summary CSVs [friedman1937use; demsar2006statistical].

## Per-dimension files (`friedman_ranks_<suite>_D<dim>.csv`; `friedman_ranks_cec2011.csv`)

| column | type | notes |
|---|---|---|
| suite | str | `cec2017` / `cec2013` / `cec2011` |
| dimension | int | file's dimension; `0` = cec2011 native aggregate |
| n_blocks | int | functions entering the test (29 / 28 / 22) |
| algorithm | str | canonical id, P1 order |
| mean_rank | float `%.6e` | Friedman mean rank (lower = better) |
| friedman_chi2 | float `%.6e` | test statistic (repeated per row for self-containment) |
| iman_davenport_F | float `%.6e` | Iman–Davenport corrected statistic |
| p_value | float `%.6e` | Iman–Davenport p-value |

## Overall file (`friedman_ranks_<suite>_overall.csv`) — descriptive only (SAP Sec. 5 authoritative)

The overall row is a **DESCRIPTIVE aggregation, not a test**: `mean_rank` = the unweighted arithmetic **mean of the per-dimension Friedman mean ranks** (4 dimensions for cec2017; 3 for cec2013), labeled "descriptive aggregation of per-dimension ranks; no test attached" in the T05/T06 table note. **NO pooled cross-dimension test is computed, attached, or reported for this file — there is no omnibus across dimensions, ever.** Columns (exactly these):

| column | type | notes |
|---|---|---|
| suite | str | `cec2017` / `cec2013` |
| algorithm | str | canonical id, P1 order |
| mean_rank | float `%.6e` | mean of the per-dimension Friedman mean ranks (descriptive; lower = better) |

The `friedman_chi2` / `iman_davenport_F` / `p_value` columns are **removed** from the overall file — they never carry a pooled statistic (if a downstream tool structurally requires the fixed 8-column set, those cells are written as the literal `NA`; the pre-registered emission is the 3-column form above). The pooled (function,dimension)-block Friedman appears ONLY as robustness check AN-ROB-2017-08/R7 output under the robustness file naming (`robustness_<suite>_r08_overall_aggregation_variants.csv`), never as the T05 overall row.

**Sort order:** suite, dimension asc (per-dimension files), algorithm in P1 order (`gsk, agsk, apgsk, fdb-agsk, atmals-gsk, egsk, dt-gsk`).
**Precision:** all floats C-locale `%.6e`. Missing = literal `n/a`.
