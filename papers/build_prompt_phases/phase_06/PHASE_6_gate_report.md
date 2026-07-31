# Phase 6 — Primary Evidence Computation and Statistical Validation — Gate Report

- **Phase:** 6 (PAPER_BUILD_PROMPT.md lines 4102–4377)
- **Evidence release:** `rel-2026-07-10-262fc16c9` (sole empirical input; strict-source-proven)
- **Gate date:** 2026-07-11
- **Verdict:** **APPROVED — Phase 6 FROZEN**
- **Signatories:** P3 + P4 + P5 + P9 (framework Gate 6 quorum)

## 1. Source-only proof
- Driver: `papers/scripts/phase6_run_analysis.py` (ruff-clean, self-contained, deterministic).
- **1,239 audited file-opens** (847/224/168 per suite) — **100% under
  `benchmarks/cec_reference_results/`**; zero `results/` or `results/_ablation` inputs.
- **3 negative tests PASS**: staging reads raise `StrictSourceViolation` (results/_run_all,
  results/_ablation, `load_reproduced()`); audit unpolluted.
- Source pre-check: function counts 29/28/22 OK; per-run row counts match the ledger
  (apgsk cec2017 = 1,479 D100-only per anomaly A2-004, exactly as pre-dispositioned).

## 2. Analysis summary (all 56 non-ablation registry families computed)
- **Bundle:** 115 files / 129 manifest entries under `papers/analysis/rel-2026-07-10-262fc16c9/`
  (cec2017: 70, cec2013: 25, cec2011: 10, root: manifest/checksums/env/cross-check/
  `primary_stats/statistical_results.csv` with **4,987 rows** in the Section 7.14 schema).
- **T1–T16 staging exports** to `results/paper_tables/` (+ provenance.json) — the only
  permitted `results/` write; T21/T22 not exported (no admissible sensitivity release; EG-006).
- **Curve selection (outcome-blind, verified):** computed from summary CSVs before any curve
  data was opened (audit order proves it); 58 audit rows, exactly 8 main picks —
  D30: F3/F10/F12/F26 (F26 = hard+ISM-weak case), D100: F1/F5/F12/F26. QA independently
  recomputed all 58 rows: 0 mismatches.
- **PHASE_12_ONLY families untouched:** AN-ABL-* not computed; ablation staging never read.

## 3. Determinism result
- Full re-run vs snapshot: **108/108 machine-readable outputs byte-identical**; 5 files
  differ only in wall-clock timestamps (3 source_use_logs + the 2 checksum/manifest entries
  hashing them) — documented tolerance; **0 real differences**. Bundle restored byte-identical
  after the check (`phase_06/determinism_check.md`).
- All 129 manifest SHA-256 entries re-verified against the tree at gate time.

## 4. Cross-implementation verification
`cross_check.json`: **14/14 agree** — Friedman ranks/χ² exact vs direct formula, decisions
agree with `scipy.friedmanchisquare`; Holm exact; A12 exact; BCa agrees with an independent
scipy implementation (rtol 1e-5); Wilcoxon W exact vs scipy. Known tie-correction variants
documented; all α-decisions identical.

## 5. Re-derived headline results (the actual numbers)
| Suite | DT-GSK result (Friedman mean rank) |
|---|---|
| **CEC2017 overall** | **#1 of 7** (2.483; eGSK #2 at 2.961) |
| CEC2017 D10 | **#1** (2.879) — not pairwise-separable vs agsk/apgsk/fdb-agsk (p_holm=1.0) |
| CEC2017 D30 | **#2** behind eGSK (2.500 vs 2.293) — pre-registered limitation LM-01 **confirmed** |
| CEC2017 D50 | **#1** (2.207) |
| CEC2017 D100 | **#1** (2.345) |
| **CEC2011** | **#2** behind eGSK (3.364 vs 2.523) — Holm-**significant loss** vs eGSK (p_holm=4.24e-2) |
| **CEC2013 overall** | **#1** (2.798); per-dimension 1st/**3rd**/1st (D30 behind eGSK + ATMALS-GSK) |

**All six previously-stated rank claims confirmed** by re-derivation; nothing rested on
stale numbers.

## 6. Negative findings (fully disclosed — `phase_06/negative_findings.md`, 10 items)
Key items binding Phase 8 prose: CEC2011 Holm-significant loss to eGSK (the only significant
unfavorable headline cell); losing W/T/L vs eGSK at D50 (13-0-16) and D100 (12-0-17) despite
#1 Friedman ranks; ISM–eGSK never Nemenyi-separable at any dimension (CD=1.673); D10 #1 not
pairwise-significant vs three comparators; robustness **r01 (mean→median) and r04
(disputed-cell exclusion) DIVERGE** (orderings shift; ISM ordinals stable) — affected
main-text claims must carry the robustness qualification; CEC2013 D30 third place.

## 7. Claims matrix adjudication (task 21)
18 rows adjudicated: **16 ACCEPTED_PHASE_6, 2 NARROWED_PHASE_6** (RS-01 overall-row test
scope; IN-03 CEC2011 corroboration wording), **0 BLOCKED**; 0 PENDING remain. Orphan checks
clean both directions (claims ↔ registry ↔ outputs ↔ exhibits).

## 8. Adversarial QA (Gate 6)
**PASS — 0 critical, 0 major, 3 minor** (r05 unpaired-transitions narrative completeness —
fixed; CEC2013 D30 disclosure — added as item 10; timestamp-in-log design note — recorded
for any future driver revision). QA independently re-verified ranks, W/T/L, Nemenyi CD,
Holm families, curve selections, and the determinism/source sweeps.

## 9. Carry-forward for Phase 7
- **Legacy `papers/tables/*.tex` are STALE** vs this bundle — Phase 7 MUST regenerate every
  table from `results/paper_tables/` (T1–T16) / the authoritative bundle, never reuse
  committed .tex values.
- Convergence generators still REQUIRE the CR-0001 seven-curve family-overlay extension
  (pre-registration P7) before Phase 7 rendering.

## 10. Sign-off
- **P3:** APPROVED — critical statistics independently verified (14/14 cross-check + QA recompute).
- **P4:** APPROVED — denominators, pairing, and the apgsk disposition executed exactly as frozen.
- **P5:** APPROVED — source-use logs, hashes, commands, determinism all proven.
- **P9:** APPROVED — claim statuses reflect actual evidence; negative findings fully disclosed.

**Gate 6 APPROVED. Phase 6 FROZEN 2026-07-11.** Any later change to release, algorithm,
endpoint, or analysis plan invalidates affected outputs and claims.
