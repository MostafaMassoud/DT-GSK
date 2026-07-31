# Claim-analysis binding report — Phase 5 validation walk

- **Date:** 2026-07-10. Pre-registration validation; performed BEFORE any outcome inspection (no statistic, rank, p-value, mean, or effect size was computed or viewed).
- **Inputs validated:**
  - `papers/build_prompt_phases/phase_05/statistical_analysis_plan.md` (SAP; authoritative method definitions, Sections 1–13)
  - `papers/build_prompt_phases/phase_05/analysis_registry.csv` (this phase's task 16 output; **59 rows**)
  - `papers/governance/claims_evidence_matrix.csv` (updated in place: 10th column `analysis_ids` appended to the header and to all **50** claim rows; all pre-existing cells byte-preserved)
  - `papers/build_prompt_phases/phase_04/exhibit_plan.csv` (71 exhibit rows; 42 empirical per `source_resolution_map.csv`; 26 non-empirical; 3 reserved Phase-12)
  - `papers/build_prompt_phases/phase_05/source_resolution_map.csv` (empirical-exhibit input classes and apgsk-gap dispositions)
- **Validation method:** programmatic cross-reference walk (csv parse of all four files; bidirectional consistency between registry `claim_ids`/`exhibit_ids` and matrix `analysis_ids`; existence checks of every referenced ID). Result: **0 cross-reference errors**.

## 1. Registry summary

59 pre-registered analysis rows, expanding every SAP Section 12 family per suite × dimension:

| Block | Rows |
|---|---|
| CEC2017: AN-DESC (4), AN-OMNI (4), AN-RANKAGG-OVERALL (1), AN-PW (4), AN-PWRUN (4), AN-EFF (4), AN-CONV (4), AN-TREND (1), AN-CLASS (1), AN-COST (1) | 28 |
| CEC2013: AN-OMNI (3), AN-RANKAGG-OVERALL (1), AN-PW (3), AN-PWRUN (3), AN-EFF (3), AN-CONV-D30 (1) | 14 |
| CEC2011: AN-OMNI, AN-PW, AN-PWRUN, AN-EFF, AN-CONV (all -NATIVE) | 5 |
| Robustness AN-ROB-2017-01…08 (SAP Sec. 10 checks 1–8, one row each) | 8 |
| Exploratory AN-EXP-BH-2017 (separate BH-FDR family; never headline) | 1 |
| PHASE_12_ONLY: AN-ABL-SCAFFOLD, AN-ABL-SGSM-OVERLAY, AN-ABL-POLISH (methods frozen; inputs = future promoted ablation release; `results/_ablation` quarantined) | 3 |
| **Total** | **59** |

Every row declares method, scope, input resolution (`summary_per_function` / `per_run` / `checkpoint_logs`), release source paths (relative to `benchmarks/cec_reference_results/`, rel-2026-07-10-262fc16c9), multiplicity family (Holm primary; BH only in the separately-labeled exploratory family — no mixed families), effect/interval machinery (A12 + Cliff's delta; BCa 95% CI, B=10,000, `SeedSequence(20240620, spawn_key)` per SAP Sec. 7), and output file under `papers/analysis/rel-2026-07-10-262fc16c9/<suite>/` plus `primary_stats/statistical_results.csv` rows keyed by `analysis_id`. The apgsk CEC2017 D10/D30/D50 per-run gap (anomaly A2-004) is carried disposition-by-disposition on every affected row: function-level AN-PW-2017-D10/D30/D50 is the sole valid inferential basis vs apgsk at those dimensions; run-level, effect-size, BCa, success-rate, and runtime quantities vs apgsk there are disclosed-unavailable, never imputed. Pairing declarations cite `papers/governance/seed_and_pairing_audit.md` (unified schedule `get_cec_seed(20240620, dim, func, run)`; 70,813 rows recomputed, 0 mismatches). CEC2011 rows use `best_fitness` (error NaN by design, A2-017).

## 2. Claim → analysis bindings (matrix `analysis_ids` column)

**23 of 50 claim rows carry at least one analysis_id.** Every planned numerical/statistical claim is bound to a compatible pre-registered analysis:

| Claim(s) | Bound analyses (rationale) |
|---|---|
| RS-01 | AN-OMNI-2017-D10/D30/D50/D100 + AN-RANKAGG-2017-OVERALL (overall row = descriptive mean of per-dimension Friedman ranks; no test) + AN-ROB-2017-01/-03/-04/-08 (stability disclosures attached to the headline) |
| RS-02…RS-05 | AN-OMNI-2017-D10 / -D30 / -D50 / -D100 respectively (one omnibus per dimension) |
| RS-06 | AN-OMNI-2017-D10…D100 (Nemenyi CD is the conditional post-hoc of each omnibus family) |
| RS-07 | AN-PW-2017-D10…D100 (function-level, GSK-family convention; sole basis vs apgsk at D10/D30/D50) + AN-PWRUN-2017-D10…D100 (run-level supplement) + AN-ROB-2017-05/-06 + AN-EXP-BH-2017 (exploratory companions, separately labeled, never headline) |
| RS-08 | AN-EFF-2017-D10…D100 (A12/Cliff) + AN-DESC-2017-D10…D100 (descriptive W/T/L tallies, tie rule 1e-8) + AN-ROB-2017-01/-02 |
| RS-09 | AN-EFF-2017-D10…D100 (BCa 95% CIs live in the same estimation family) |
| RS-10 | AN-OMNI/AN-PW/AN-PWRUN/AN-EFF-2011-NATIVE + AN-ROB-2017-07 |
| RS-11 | all 13 CEC2013 analysis rows + AN-ROB-2017-07 |
| IN-01 | AN-TREND-2017 (rank-vs-dimension; no extrapolation past D100) + AN-CLASS-2017 (exploratory per-class, RQ4 partial) + AN-OMNI-2017-D10/D100 (trend endpoints) |
| IN-02 | AN-CONV-2017-D50/D100 (descriptive convergence at the SGSM-active tiers) + AN-OMNI-2017-D50/D100 (the rank evidence cited in the claim) |
| IN-03 | AN-OMNI-2011-NATIVE + AN-PW-2011-NATIVE ("corroborate" wording only) |
| LM-01 | AN-OMNI-2017-D30 (the D30 rank re-derivation that the limitation binds to) |
| LM-04 | AN-COST-2017 (comparability-qualified runtime; no superiority claim) |
| LM-05 | AN-TREND-2017 (its no-extrapolation-beyond-D100 rule operationalizes the evidence ceiling) |
| CN-01 | AN-OMNI-2017-D10…D100 + AN-RANKAGG-2017-OVERALL + AN-OMNI-2011-NATIVE + AN-TREND-2017 (conclusion restates exactly these exhibit-bound results) |
| HL-01, CL-02 | AN-RANKAGG-2017-OVERALL (the single headline family-panel number both templates quote) |
| AB-01 / AB-02 / AB-03 | AN-ABL-SCAFFOLD / AN-ABL-SGSM-OVERLAY / AN-ABL-POLISH (PHASE_12_ONLY, supplement-only) |

Bidirectional consistency holds: every analysis_id on a matrix row back-references that claim in the registry's `claim_ids`, and vice versa (0 mismatches).

## 3. Claim rows with empty `analysis_ids` (27) — justification per row class

Empty bindings are confined to non-empirical claim types, as permitted:

- **BG-01…BG-06 (6, background):** literature/gap statements grounded in evidence cards and governance docs; no empirical analysis exists or is needed. BG-06 grounds the statistics *methodology* (citations), not any outcome.
- **MT-01…MT-11 (11, method):** method-prose design facts (operator inheritance, ACE/ARGP/NLPSR/BSE/ISM/polish/RNG/budget accounting) sourced to frozen phase_03 artifacts and code; the matrix's own blocked-wording rules already forbid effectiveness claims here (deferred to Phase 12, where AN-ABL-* apply via AB-01…03, which ARE bound).
- **PR-01…PR-06 (6, protocol):** protocol facts (suite definitions, budgets, run counts, 1e-8 convention, fair-start exception) verified by governance audits (`benchmark_protocol_audit.md`, `seed_and_pairing_audit.md`), not by statistical analyses. Per the task rule "protocol rows get none or AN-DESC," these take **none**: no protocol row states an outcome, and binding AN-DESC would wrongly imply the protocol depends on result descriptives.
- **LM-02 (limitation, design-fact):** subsystem gating to D≥50 is a frozen-configuration fact (`phase_03/parameter_table.md`), not an empirical finding; its Phase-6 exhibit cross-references arrive via the already-bound RS/IN rows. Not "limitation-empirical."
- **LM-03 (limitation, scope):** panel-scope restriction — a wording rule, not an empirical quantity.
- **CN-02 (conclusion, reproducibility):** artifact-backed design-fact conclusion (seeds, freeze manifest, release, RNG layer) with status READY; its evidence is governance artifacts and the Phase 3 deterministic trace, not any statistical analysis. No numerical placeholder appears in its template.
- **CL-01 (cover-letter, venue):** administrative/venue statement (risk R-0004, deferred); no empirical content.

Empirical limitation rows (LM-01, LM-04, LM-05) **are** bound. Every primary-result (RS-01…RS-11), every interpretation (IN-01…IN-03), every ablation row (AB-01…03), CN-01, HL-01, and CL-02 (the rows whose templates contain `<TXX:...>`/`<FXX:...>` numerical placeholders) carry at least one compatible analysis_id. **No planned numerical/statistical claim is left without a pre-registered analysis.**

## 4. Analysis orphan check (registry → claims/exhibits)

**Every one of the 59 registry analysis_ids appears on ≥ 1 claim or ≥ 1 exhibit. Orphans: none (0).** Rows bound via exhibits only (claim_ids empty by design, all descriptive): AN-CONV-2017-D10 (F02-SUP-CEC2017-D10), AN-CONV-2017-D30 (F02-MAIN-D30; F02-SUP-CEC2017-D30), AN-CONV-2013-D30 (F02-SUP-CEC2013-D30), AN-CONV-2011-NATIVE (F02-SUP-CEC2011). Rows bound via claims only (no dedicated exhibit exists in `exhibit_plan.csv`, all outputs land in the analysis bundle/supplement text): AN-PW-2013-*, AN-PWRUN-2013-*, AN-EFF-2013-* (all → RS-11), AN-CLASS-2017 (→ IN-01), AN-ROB-2017-01…08 (→ the headline claims they stress-test), AN-EXP-BH-2017 (→ RS-07, exploratory companion label only).

## 5. Exhibit coverage check (empirical exhibits → registry)

Of the **42** empirical exhibit rows in `source_resolution_map.csv`, **39 appear on ≥ 1 registry row** via `exhibit_ids`: T01-SUM, T05, F01-D10…D100, T02, T03, F02-MAIN-D30/D100, F03, F05-RANKBAR, T04, F04-CEC2011, T06, T-RUNTIME, T01-D10…D100, T02-FULL-D10…D100, T03-FULL-D10…D100, T-BCA, F02-SUP-CEC2017-D10…D100, F02-SUP-CEC2011, F02-SUP-CEC2013-D30, T04-STATS, T06-FULL-D10/D30/D50. (T06-FULL-* descriptive tables are transcriptions of the same summary CSVs consumed by AN-OMNI-2013-*, on whose rows they ride; T04/T04-STATS ride on the CEC2011 families; SAP defines no separate AN-DESC family for the secondary suites.)

**3 documented exceptions — intentionally on no registry row** because their pre-registered disposition (fixed in `source_resolution_map.csv` before any outcome inspection) is *unavailable-from-release*, i.e., no analysis can be pre-registered against inputs that do not exist in rel-2026-07-10-262fc16c9:

- **T-SENS** — "NONE RESOLVABLE": the release contains only the 7-algorithm panel runs, no parameter-sensitivity sweep. Disposition: disclosed-unavailable; `papers/governance/evidence_gap_register.md` entry; ships only if a future versioned release adds admissible sensitivity evidence.
- **F-TRACE / F-ADAPT** — GATED on a promoted `GenLog_*` diagnostic release that is absent from rel-2026-07-10-262fc16c9. Disposition per P7: marked unavailable in `evidence_gap_register.md` unless such a release exists before Phase 7; `results/` staging never admissible.

These are pre-registered evidence gaps, not binding orphans; any future analysis against a new release would enter via a logged confirmatory amendment (SAP Sec. 13), never silently.

The 3 RESERVED exhibits (X-ABL-01…03) are outside the empirical denominator but are nonetheless covered by the AN-ABL-* rows for Phase-12 traceability.

## 6. Verdict

- Registry: 59 rows, each with source, method, multiplicity family, effect/interval machinery, and output file. 0 duplicate IDs.
- Claims matrix: 50 rows preserved byte-wise + `analysis_ids` column; 23 rows bound; all 27 empty rows are non-empirical claim classes with per-class justification above.
- Orphan analyses: **0**. Unbound empirical exhibits: **0 defects** (3 pre-registered disclosed-unavailable/gated exceptions, dispositions already frozen upstream).
- No outcome was computed or inspected at any point in this validation.
