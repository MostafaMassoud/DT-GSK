# Phase 6 claims update report (tasks 21-22)

Inputs: `papers/analysis/rel-2026-07-10-262fc16c9/` (Phase 6 bundle; 129 output files,
4987 rows in `primary_stats/statistical_results.csv`), pre-registration
`papers/build_prompt_phases/phase_05/` (registry 59 families). Matrix updated in place:
`papers/governance/claims_evidence_matrix.csv` (validated post-edit: 50 data rows x 10
columns; header intact).

## 1. Rank-verification verdict (special-attention items): ALL CONFIRMED

Re-derived from `friedman_ranks_*` files of the release bundle:

| Previously stated | Re-derived (Phase 6) | Verdict |
|---|---|---|
| #1 overall CEC2017 (mean + median) | Overall mean-of-ranks 2.482759 vs eGSK 2.961207 -> first of 7. Median-endpoint check (r01): DT-GSK per-dimension ordinals unchanged (1/2/1/1); pooled block-Friedman variant (r08): agree | CONFIRMED |
| #1 at D10 | 2.879310, best of 7 (agsk 3.051724 second) | CONFIRMED |
| #2 at D30 behind eGSK (LM-01) | DT-GSK 2.500000 vs eGSK 2.293103 -> second of 7 | CONFIRMED |
| #1 at D50 | 2.206897, best of 7 (egsk 2.620690 second) | CONFIRMED |
| #1 at D100 | 2.344828, best of 7 (egsk 2.689655 second) | CONFIRMED |
| CEC2011 #2 | 3.363636, second of 7 behind eGSK 2.522727 | CONFIRMED |

No rank claim required NARROWED/BLOCKED treatment on rank-mismatch grounds. All four
per-dimension CEC2017 omnibus tests and the CEC2011 omnibus are Iman-Davenport
significant (p = 2.576884e-08 / 1.151976e-10 / 6.763147e-11 / 1.424078e-12 /
2.160258e-03). CEC2013 (context): DT-GSK overall mean rank 2.797619, best of 7.

## 2. Status changes (18 rows updated: 17 PENDING_PHASE_6 + 1 VERIFIED_PLANNING_REDERIVE_PHASE_6)

- ACCEPTED_PHASE_6: 16 - RS-02, RS-03, RS-04, RS-05, RS-06, RS-07, RS-08, RS-09,
  RS-10, RS-11, IN-01, IN-02, LM-01, CN-01, HL-01, CL-02.
- NARROWED_PHASE_6: 2 - RS-01, IN-03 (narrowed wording appended to permitted_wording).
- BLOCKED_PHASE_6: 0.

Narrowing rationale:
- RS-01: the overall row is a descriptive unweighted mean of per-dimension Friedman
  mean ranks with NO cross-dimension test; the template's "(Iman-Davenport corrected)"
  applies only to the per-dimension omnibuses. Narrowed wording makes this explicit;
  blocked_wording extended to forbid describing the overall row itself as tested.
- IN-03: CEC2011 "corroborate" narrowed to within-family competitiveness (second of 7)
  because the Holm-corrected Wilcoxon vs eGSK on CEC2011 is a significant LOSS
  (p_holm = 4.244817e-02); CEC2011 does not corroborate first place.

Acceptance annotations (not narrowings) appended to permitted_wording of RS-10 (must
disclose the eGSK deficit alongside the #2 placement) and LM-01 (re-derived numbers
recorded); blocked_wording of IN-01 extended (trend not monotone) and IN-02 extended
(no head-to-head-dominance-over-eGSK wording at D50/D100: W/T/L 13-0-16 / 12-0-17,
pairwise ties).

Rows left untouched: 28 READY, 3 DEFERRED_TO_PHASE_12_SUPPLEMENT_ONLY (AB-01..03),
1 BLOCKED_ON_R-0004 (CL-01).

## 3. Orphan checks: CLEAN

- Every claim analysis_id exists in the 59-family registry: PASS (0 unknown ids).
- Every referenced non-ablation family has rows in statistical_results.csv: PASS
  (56/56 computed families present; the 3 AN-ABL-* families are PHASE_12_ONLY by
  pre-registration and correctly absent; extra disclosed-unavailable row
  EG-006-T-SENS present by design).
- Every registry non-ablation output file exists with >=1 data row: PASS (no
  header-only CSVs anywhere in the bundle; brace-pattern entries such as
  `wilcoxon_run_cec2017_D{10,30,50,100}_exploratory_bh.csv` verified file-by-file,
  175 lines each).
- Every planned-exhibit empirical source in table_to_csv_map.md exists: PASS
  (incl. headline_bca.csv 697 lines, rank_trend 29, class_ranks 113, cost 57,
  curve_selection D30/D100 30 lines each, nemenyi files all dims, T1-T16 staging
  exports + provenance.json). T-SENS and F-TRACE/F-ADAPT are mapped as
  disclosed-unavailable by design - not orphans.
- Curve-selection blindness artifact: phase_05/curve_selection.csv filled (58 audit
  rows, exactly 8 selected_for_main=TRUE).

## 4. Negative findings

Recorded in full in `papers/build_prompt_phases/phase_06/negative_findings.md`
(9 items): D30 second place (confirmed); CEC2011 Holm-significant loss to eGSK (the
single significant unfavorable headline cell); losing W/T/L records vs eGSK at
D50/D100 despite #1 ranks; DT-GSK vs eGSK never Nemenyi-separable at any CEC2017
dimension (CD = 1.672993); weak D10 pairwise separation (ties vs agsk/apgsk/fdb-agsk);
D100 vs GSK tie after Holm (p_holm = 6.118680e-02); r01 and r04 robustness DIVERGE
verdicts (DT-GSK ordinals stable, comparator orderings/W-T-L unstable) and r05's
8 significant->n.s. unpaired transitions; disclosed-unavailable inventory (apgsk A2-004,
EG-006, F-TRACE/F-ADAPT, CEC2011 NaN-by-design); non-monotone dimension trend.

## 5. Deviations and execution notes

- No confirmatory amendments were needed; the frozen plan was executable as written.
- Execution note: during this task the bundle was concurrently regenerated by
  `papers/scripts/phase6_run_analysis.py` (completed successfully: "PHASE 6 DRIVER
  COMPLETE", 129 outputs, strict-source negative tests PASS, audited opens 1239 all
  under benchmarks/cec_reference_results/). All values quoted above were re-verified
  against the post-regeneration bundle and are identical to the pre-regeneration
  values (deterministic pipeline).
- Matrix edits confined to the three permitted columns (permitted_wording,
  blocked_wording, status); claim templates, evidence_ids, citation_keys, risk and
  analysis_ids untouched; CSV shape preserved (10 cols x 50 data rows).
