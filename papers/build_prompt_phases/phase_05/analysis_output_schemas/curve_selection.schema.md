# curve_selection — output schema (Phase 5 pre-registration)

**Authoritative column contract:** `papers/build_prompt_phases/phase_05/curve_selection_rule.md` Section 5.7. This schema restates it; on any discrepancy, Sec. 5.7 governs.

**Files:** the canonical audit record is `papers/build_prompt_phases/phase_05/curve_selection.csv` — **ALL 58 rows** (2 featured dimensions × 29 functions), written by Phase 6 BEFORE any curve is rendered or viewed (P5 ordering guarantee; the file is the auditable record that selection preceded viewing). The analysis-area emission follows the `strict_source_execution.md` Sec. 5 naming pattern: `curve_selection_cec2017_D30.csv` and `curve_selection_cec2017_D100.csv` (29 rows each; identical columns; jointly the same 58 audit rows).

**Row counts (binding):** 58 audit rows total; **exactly 8 rows with `selected_for_main = TRUE`** (4 per featured dimension, one per category); every other row `FALSE`.

**Columns (exactly these 8; per curve_selection_rule.md Sec. 5.7):**

| column | content |
|---|---|
| suite | `cec2017` |
| dimension | `30` or `100` |
| function | integer (1, 3–30) |
| category | `unimodal` / `simple_multimodal` / `hybrid` / `composition` |
| difficulty_tercile | `easy` / `moderate` / `hard` |
| ismgsk_standing | `strong` / `comparable` / `weak` |
| selection_reason | selected rows: `priority_<k>_(<tercile>,<standing>)` with k = position in curve_selection_rule.md Sec. 5.4, or a `constraint_repair_*` tag; all other rows: `not_selected` |
| selected_for_main | `TRUE` / `FALSE` (exactly 4 `TRUE` per dimension) |

No 9th column is permitted (no `panel_median_error` or other auxiliary column — curve_selection_rule.md Sec. 5.7 enumerates exactly these 8; the panel-median difficulty score of Sec. 5.2 is an intermediate quantity, not an emitted column).

**Joint constraint:** across the 8 selected panels, >= 1 `hard` and >= 1 DT-GSK-`weak` function (curve_selection_rule.md Sec. 5.6 repair rules; genuine unsatisfiability is disclosed, never silently absorbed); verified by Phase 6 assertion, recorded in run_manifest.json.
**Sort order:** dimension asc, then function asc.
**Header check:** the header row of `papers/build_prompt_phases/phase_05/curve_selection.csv` matches these 8 columns exactly (verified 2026-07-10).
