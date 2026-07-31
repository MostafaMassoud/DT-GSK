# BUG-RESUME-01 — resume mode truncates (and mis-computes) the per-dimension summary CSV

**Status: ✅ FIXED 2026-07-25 — CR-0012.** Was present for all 7 algorithms and all
5 suites. Fix verified RED-then-GREEN plus end-to-end against the real runner; full
suite 491 passed (was 488). See "Resolution" at the bottom.

⚠ **Any summary CSV previously produced BY A RESUME is suspect** and should be
regenerated from `per_run.csv`, which is authoritative and was never affected.
**Reported:** 2026-07-25, reproduced by the author in the sibling project
`05-Human-Inspired-Family_Python_v0.1` (shade-ils, cec2013lsgo).
**Severity:** HIGH — silent data corruption of a released artifact.
**Urgency here:** the dt-gsk CEC2013LSGO campaign currently sits at **100/375
runs**, so the next resume will trigger this.

## Symptom (as reported)

Resuming a config **without** `--overwrite` (so only missing runs dispatch) rewrites
`<alg>_<suite>_D<dim>.csv` with **only the functions it touched**. In the sibling
project a resume that filled 6 missing F8 runs left the D1000 summary containing a
single row (F8); F1–F7, F9–F12, F15 were dropped. `per_run.csv` still held all 375
runs and was used to regenerate the summaries by hand.

## Root cause in this project (verified in source)

`src/gsk_family/runners/run_experiment.py`:

| line | code | effect |
|---|---|---|
| 1353–1355 | `existing_rows = ... read_existing_per_run(...)`; `all_rows = list(existing_rows)` | **`per_run.csv` correctly merges** prior runs |
| 1356 | `artifacts: list[RunArtifact] = []` | starts **empty** |
| 1366–1371 | already-complete `key_seed` → `continue` | existing runs are **skipped, never reconstructed** as `RunArtifact` |
| 1630 | `artifacts.append(artifact)` | only **new** runs enter `artifacts` |
| 1678, 1756 | `write_summary_tables(dirs["summary"], optimizer, cfg.suite, artifacts)` | summary built from new runs only |

`src/gsk_family/runners/output.py:146` `write_summary_tables` groups `artifacts` by
`(dim, func)` and opens each `<alg>_<suite>_D<dim>.csv` with mode **`"w"`**
(truncate) — so untouched functions are erased. The `cec2011` rollup path
(`<alg>_cec2011.csv`) has the identical defect.

## ⚠ Second, worse face of the bug — NOT in the original report

Because `artifacts` holds only new runs, a **partially** resumed function is
summarised over the new runs alone. A resume that adds 6 runs to an F8 that already
had 19 writes Best/Median/Mean/Worst/SD computed from **6 runs, not 25** — a
plausible-looking but wrong row, rather than an obviously missing one. Function
truncation is visible; this is not.

## Fix (designed, not yet applied)

**Rebuild the summary from `per_run.csv`, which is authoritative and already
complete.** This closes both faces at once; merging on-disk summary rows would fix
only the first.

Value selection is exactly reproducible from the CSV — `stats.py:69`
`statistic_values` returns:
- `statistics_basis == "raw_objective"` → `best_fitness` unchanged;
- `statistics_basis == "error_vs_optimum"` → `compute_error(...)`, which is what the
  `error` column already stores.

and `per_run.csv` carries **both** columns
(`optimizer,suite,function,dimension,run,seed,best_fitness,error,nfes,termination,runtime_seconds`).

Implementation sketch:

1. Add to `output.py` a row-based writer, e.g.
   `write_summary_tables_from_rows(summary_dir, optimizer, suite, rows, statistics_basis)`:
   group rows by `(dimension, function)`, select `best_fitness` or `error` per
   basis, `summarize(...)`, write every function present — same header and
   `format_scientific` formatting as today.
2. Replace both `write_summary_tables(..., artifacts)` call sites with the
   row-based writer fed `all_rows`. Keep the streaming site (1678) so an
   interrupted campaign still refreshes the summary — it becomes *more* correct,
   not less, because `all_rows` includes prior runs.
3. Keep `write_summary_tables` (artifact-based) only if something else needs it;
   otherwise delete to prevent reintroduction.

## Regression test to add

`tests/regression/test_resume_summary_not_truncated.py`:
- seed a `per_run.csv` bank covering several functions at one dim, plus matching
  summary CSV;
- run a resume that dispatches **one** function;
- assert the summary CSV still lists **every** function present in `per_run.csv`;
- assert the resumed function's row equals the statistics over **all** its runs in
  `per_run.csv`, not just the new ones (this is the check that catches face 2).

## Cross-project note

The same defect exists in `05-Human-Inspired-Family_Python_v0.1`
(`src/human_inspired_family/runners/run_experiment.py`). Fixing it there is outside
this project's change scope — the author holds that decision.

---

## Resolution — CR-0012, 2026-07-25

**The originally-proposed fix was rejected after measurement.** "Always recompute
all functions from `per_run.csv`" (§Fix above, and the author's own preferred
option) turns out to perturb released numbers: `per_run.csv` stores `%.10e`-rounded
values while the artifact path summarises full float64, so a rebuild shifts
**Mean/SD in the 10th significant digit**. Measured on real dt-gsk LSGO data,
**5 of 20 fields differed** — e.g. F3 Mean `2.0522500209E+01` vs
`2.0522500208E+01`, F2 SD `3.1119309017E+02` vs `3.1119309016E+02`.
Best/Median/Worst always matched (rounding is monotonic, so selection is stable).

That drift never reaches manuscript precision (paper tables print ~3 significant
digits) but it **would break the file hash of every frozen summary it rewrote** —
unacceptable for cec2017/cec2011/cec2013.

### What was implemented instead — never perturb a number you did not recompute

Per cell, in order of preference:

1. **Untouched function** → its existing on-disk row is carried over
   **byte-for-byte** (`_read_existing_summary`). A resume cannot rewrite it.
2. **Fully covered by this session** → exact artifact computation, unchanged from
   before, at full float64 precision.
3. **Partially resumed** → summarised from the complete banked values
   (`bank_counts` / `bank_values`, derived from `per_run.csv` by `_bank_from_rows`,
   basis-aware: `best_fitness` for `raw_objective`, the precomputed `error` column
   otherwise). Accepts the 10th-digit drift because the alternative — statistics
   over an arbitrary subset — is far worse, and the earlier runs' full-precision
   values no longer exist.

The `"w"` truncation is gone: both the per-dimension tables and the CEC2011 rollup
now merge into whatever is already on disk.

### Verification

- **RED-then-GREEN.** On pre-fix code the new test reproduces the reported symptom
  verbatim: `resume dropped functions: kept [8], expected [1, 2, 3, 8, 15]`, plus
  `cec2011 rollup dropped functions`. All pass after.
- `tests/regression/test_resume_summary_not_truncated.py` — 3 tests: truncation,
  **subset statistics** (the invisible face), and the CEC2011 rollup.
- Full suite **491 passed** (was 488).
- **End-to-end against the real runner:** ran F1/F2/F3 × 2, then resumed touching
  only F2 (`runs: 3`, no `--overwrite`). Summary retained `['1','2','3']`;
  `per_run.csv` showed `{1: 2, 2: 3, 3: 2}`.

### Still open

The same defect exists in `05-Human-Inspired-Family_Python_v0.1`
(`src/human_inspired_family/runners/run_experiment.py` + its `output.py`). Porting
this fix there is outside this project's change scope — author's decision.
