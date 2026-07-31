# CR-0006 — apgsk CEC2017 per-run recovery (A2-004 data-loss correction)

**Date:** 2026-07-11 · **Approver:** P1 · **Status:** APPROVED · **Decision:** `decision_log.md` D-0011

---

## 1. What changed and why

The apgsk CEC2017 D10/D30/D50 per-run data — lost from
`benchmarks/cec_reference_results/cec2017/apgsk/per_run.csv` and recorded as
**anomaly A2-004** (the file covered D100 only; run-level quantities vs apgsk at
the three lower dimensions were pre-registered *disclosed-unavailable*, never
imputed) — has been **restored to all four dimensions (1479 → 5916 rows)** by a
**validated deterministic recovery** (`scripts/recover_apgsk_perrun.py`).

**Admissibility proof:** the recovered D10/D30/D50 rows **reproduce the frozen
summary CSVs EXACTLY.** This makes the change a **completeness correction of lost
data**, not new experimental data. No benchmark was re-run; the frozen algorithm
and every other optimizer's data are immutable.

The SAP pre-registered exactly this contingency: `source_resolution_map.csv`
disposition (iv) and SAP Section 6b anticipate a *registered change request*
sanctioning a recovered apgsk per-run source as a **logged confirmatory
amendment** (SAP Section 13). CR-0006 is that amendment; validation is against
frozen summaries, not against any inspected outcome, so the confirmatory
character of the affected families is preserved.

## 2. Bounded blast radius (verified)

Reopens **Phase 6** (run-level recompute), **Phase 7** (exhibit regeneration),
and **Phase 11** (freeze/parity re-verification) **for apgsk run-level cells
only**. Phase 9 (Word/docx) is **not** reopened.

### Phase 6 — Stage 1 (analysis bundle)
- **31** files under `papers/analysis/rel-2026-07-10-262fc16c9/` changed:
  apgsk run-level `wilcoxon_run_cec2017_D{10,30,50}`, `effect_sizes_cec2017_D{10,30,50}`,
  `bca_ci_cec2017_D{10,30,50}` (29 apgsk rows each, `disclosed-unavailable` → real),
  `headline_bca.csv` (87 apgsk rows), `cost_cec2017.csv` (3 apgsk runtime rows),
  `wilcoxon_run_*_exploratory_bh` (29 each), robustness r02/r05/r06,
  `primary_stats/statistical_results.csv` (+87 apgsk BH rows; 745 apgsk data-cell
  changes), and provenance re-stamps (`commit_sha`, `git_head`, timestamps, dependent
  hashes).
- **0 non-apgsk data cells changed.** Byte-identical: all `friedman_ranks_*`,
  `descriptive_stats_*`, function-level `wilcoxon_holm_*`, `cross_check.json`,
  robustness r01/r03/**r04**/r07/r08, and every CEC2013/CEC2011 run-level file.
- Driver: static `APGSK_GAP_DIMS` skip → dynamic `per_run_absent()` presence gate;
  the r04 disputed-cell tuple (`APGSK_DISPUTED_DIMS`) deliberately kept **fixed**
  (pre-registered summary-means variant, not a data gate).

### Phase 7 — Stage 2 (exhibits) — this stage
- Re-ran the two release-wired generators with `PYTHONIOENCODING=utf-8` and
  `SOURCE_DATE_EPOCH` set:
  - `python papers/scripts/generate_latex_tables.py --skip-ablation`
  - `python papers/scripts/generate_t16_bca.py`
- **All 21 `papers/tables/*.tex` are byte-identical** (SHA-256 verified before/after;
  `git status` clean on `papers/tables/`). Reason: `generate_latex_tables.py` reads
  only `results/paper_tables/T*.csv` and `generate_t16_bca.py` reads only
  `descriptive_stats_cec2017_D*.csv` — **all byte-identical** sources.
- The exhibit_plan supplement "FULL" per-function run-level tables
  (`T02-FULL`/`T03-FULL`/`T-BCA` per-function) are **not built as separate `.tex`
  artifacts**; the run-level apgsk d.u.→real change lives entirely in the Stage-1
  analysis-bundle CSVs (their released data form) and does not propagate to any
  built LaTeX table.
- `results/paper_tables/T*.csv` + `provenance.json`: **unchanged** (no re-export
  needed).
- `papers/governance/artifact_binding.csv`: **no checksum change.** No bound
  exhibit's `source_paths` references any changed run-level file (only match is a
  `headline_bca` mention inside the T16-BCA note, not a source), and every regenerated
  `.tex` output is byte-identical.
- **Main manuscript: NOT touched.** The main-text effect-size table (T15,
  `tab:effect-sizes`) is across-function A12 on per-function *means* (summary-based)
  + function-level Wilcoxon/Holm → unaffected. The only main-text exhibit that carries
  apgsk run-level cells is the runtime/cost table (`sections/performance.tex`,
  `tab:runtime`); regenerating it and softening the outdated main-text gap prose are
  handed off to the manuscript-rebuild stage (Phase 9), out of CR-0006 Stage 2 scope.

### Phase 9 — hand-off (NOT reopened here)
- `papers/tables/word_sources/T16_bca.json` reads the recovered `headline_bca.csv`
  and would change on regeneration; a Word/PDF rebuild is a separate downstream stage.
  Recorded as a hand-off, not executed under this CR.

## 3. Dispositions marked RESOLVED (Stage 2)

Original pre-registration text **preserved**; RESOLVED annotations appended in
place (append-only governance).

| File | Change |
|---|---|
| `phase_05/analysis_registry.csv` | Binding APGSK-GAP header block gains a RESOLVED-CR-0006 note; 14 row-level markers on AN-DESC/AN-PWRUN/AN-EFF/AN-COST/AN-EXP-BH D10/D30/D50 dispositions (+ AN-PW rank-biserial cross-reference to now-available AN-EFF). |
| `phase_05/source_resolution_map.csv` | Binding APGSK-GAP header block gains a RESOLVED-CR-0006 note (disposition (iv) CR now filed); 11 row markers on T01-SUM/T02/T03/T-RUNTIME/T02-FULL-D{10,30,50}/T03-FULL-D{10,30,50}/T-BCA. T-SENS (EG-006 parametric-sweep gap) explicitly flagged as a **separate, still-open** gap — **not** touched. |
| `phase_05/statistical_analysis_plan.md` | Dated **CR-0006 confirmatory amendment** bullet (per Section 13) + 7 inline markers on the concrete cell-level d.u. dispositions. |
| `papers/governance/claims_evidence_matrix.csv` | RS-07, RS-08, RS-09, LM-04 gain a dated CR-0006 **evidence note** (apgsk run-level cells now computed). Permitted/blocked wording and `ACCEPTED_PHASE_6`/`READY` status **unchanged**; **no claim upgraded**. |

`evidence_gap_register.md` does **not** carry the apgsk per-run gap (A2-004 is an
anomaly, tracked in `phase2_anomaly_register.csv`/`data_ledger.csv`) — left untouched.

## 4. Change-control records (Stage 2)

| File | Change |
|---|---|
| `papers/governance/change_request_register.csv` | CR-0006 row appended (APPROVED, P1). |
| `papers/governance/decision_log.md` | Decision **D-0011** appended (recovery rationale, blast radius, no-upgrade). |
| `papers/governance/phase2_anomaly_register.csv` | **A2-004** `impact` cell annotated **RESOLVED-CR-0006**; siblings A2-005/A2-006/A2-007 (seed_schedule/env/gen-log provenance) explicitly noted as **not** covered and still open. |
| `papers/governance/evidence_release_manifest.json` | (Stage 1) apgsk per_run size/sha updated + ancestor byte rollups + dated `cr_0006_recovery_note`. |

## 5. No claim upgraded

Filling a disclosed-unavailable cell with its true measured value is a
**completeness correction**. Disclosure wording was left conservative; no claim's
permitted wording, blocked wording, or acceptance status was strengthened.

## 6. Integrity checks run

- Both LaTeX generators exit 0; all 21 `.tex` SHA-256 byte-identical before/after.
- `results/paper_tables/`, `papers/tables/`, `artifact_binding.csv`: `git status`
  clean (unchanged).
- All four edited registry/matrix CSVs re-parse with uniform column counts
  (analysis_registry 10×60; source_resolution_map 6×43; claims_evidence_matrix
  10×51; change_request_register 9×7).
- Disposition/claims patchers used exact anchors with asserted occurrence counts
  (fail-loud on mismatch); T-SENS non-apgsk d.u. deliberately excluded.
