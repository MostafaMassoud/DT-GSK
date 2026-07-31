# Statistical Analysis Plan (SAP) — DT-GSK family-panel paper

- **Phase / tasks:** Phase 5, tasks 1–7 and 9 (pre-registration; frozen BEFORE any outcome inspection).
- **Date frozen:** 2026-07-10.
- **CR-0006 confirmatory amendment (2026-07-11) — logged per Section 13:** the apgsk CEC2017 D10/D30/D50 per-run gap (anomaly A2-004), disposed here as *disclosed-unavailable*, is **RESOLVED**. `cec2017/apgsk/per_run.csv` was restored to all four dimensions (5916 rows) by a validated deterministic recovery (`scripts/recover_apgsk_perrun.py`); the recovered D10/D30/D50 rows reproduce the frozen summary CSVs **exactly**. Consequently the apgsk run-level cells at those dimensions (AN-DESC success/failure rates, AN-PWRUN, AN-EFF A12/Cliff + BCa, AN-COST runtime, AN-EXP-BH) are now **computed** rather than disclosed-unavailable. This is a **completeness correction only**: the frozen summary CSVs, primary Friedman ranks, and function-level Wilcoxon/Holm are byte-unchanged; the pre-registered function-level basis (Section 6a, AN-PW-2017-D10/D30/D50) remains valid; the pre-registered summary-means robustness variant (Section 10 item 4 / AN-ROB-2017-04, disputed-cell exclusion) is deliberately kept fixed; **no claim is upgraded** and no outcome-dependent template changed. See `papers/governance/decision_log.md` D-0011, `change_request_register.csv` CR-0006, and `phase2_anomaly_register.csv` A2-004 (status RESOLVED-CR-0006). The individual disposition sentences below are annotated `[RESOLVED CR-0006 2026-07-11]` in place; original pre-registration text is preserved for the audit record.
- **Evidence release (sole empirical source):** `rel-2026-07-10-262fc16c9` (`benchmarks/cec_reference_results/`, read-only). Staging `results/` and `results/_ablation/` are never citable and were not opened for this plan.
- **Binding upstream artifacts honored:** `papers/build_prompt_phases/phase_04/exhibit_plan.csv` pre-registrations P1–P8; `papers/governance/claims_evidence_matrix.csv` (50 rows); `papers/build_prompt_phases/phase_04/thesis.md`; `papers/build_prompt_phases/phase_03/algorithm_freeze_manifest.json`; `papers/governance/seed_and_pairing_audit.md`; `papers/governance/phase2_anomaly_register.csv`; `papers/governance/data_ledger.csv`; `papers/PAPER_BUILD_PROMPT.md` Section 7.
- **Outcome-blindness declaration:** no statistical outcome, rank, p-value, mean, or effect size was computed, inspected, or reported while writing this plan. Feasibility checks were limited to schemas/headers (e.g., `benchmarks/cec_reference_results/cec2017/dt-gsk/per_run.csv` header: `optimizer,suite,function,dimension,run,seed,best_fitness,error,nfes,termination,runtime_seconds`) and governance audit files. The already-verified planning ranks quoted in `phase_04/terminology_glossary.md` and `docs/algorithms/dt-gsk.md` are planning-only and are always marked "to be re-derived in Phase 6 from release rel-2026-07-10-262fc16c9"; no template in this plan presupposes them.
- **Panel (P1 order, fixed everywhere):** gsk, agsk, apgsk, fdb-agsk, atmals-gsk, egsk (written **eGSK** in prose per the CR-0003 capitalization rule in `phase_04/terminology_glossary.md`), dt-gsk. All comparative wording is scoped "within the GSK family panel"; never field-wide (LM-03, BG-05 [wolpert1997nfl]).
- **Tooling of record (verified to exist by reading):** `src/gsk_family/analysis/result_loader.py` (strict-source guard `GSK_STRICT_SOURCE` / `set_strict_source`, threaded from `gsk-stats --strict-source`), `src/gsk_family/analysis/statistics.py`, `src/gsk_family/analysis/statistical_tests.py`, `src/gsk_family/cli/stats.py`, `papers/scripts/generate_latex_tables.py`, `papers/scripts/generate_t16_bca.py`, `papers/scripts/generate_nemenyi_cd.py`, `papers/scripts/generate_rank_charts.py`. All publication analyses run in strict reference-only mode and write to the controlled analysis area `papers/analysis/rel-2026-07-10-262fc16c9/<suite>/` (PAPER_BUILD_PROMPT Section 7.13). Every reported statistic gets a machine-readable row in `papers/analysis/rel-2026-07-10-262fc16c9/primary_stats/statistical_results.csv` per the Section 7.14 schema, keyed by the analysis-family IDs defined in Section 12 below.

Statistical-method evidence cards cited throughout (all in `papers/governance/allowed_citation_keys.txt`; cards in `papers/governance/evidence_cards/`): `friedman1937use`, `demsar2006statistical`, `wilcoxon1945individual`, `holm1979simple`, `benjamini1995controlling`, `vargha2000critique`, `efron1993introduction`, `david_order_statistics`.

---

## 1. Research questions (task 1)

Adopted/refined from `papers/PAPER_BUILD_PROMPT.md` Section 7.1 (RQ block at line 1526 ff.). Classification: **primary** (headline, confirmatory), **secondary** (supporting, confirmatory), **descriptive** (no inference), **exploratory** (labeled, never headline).

| RQ | Question (refined) | Class | Analysis families (Section 12) | Claim rows served |
|---|---|---|---|---|
| RQ1 | Within the 7-algorithm GSK-family panel, how does frozen DT-GSK compare on CEC2017 at each dimension D ∈ {10, 30, 50, 100}? | **Primary** | AN-DESC-2017-*, AN-OMNI-2017-*, AN-RANKAGG-2017-OVERALL | RS-01…RS-06, T01, T05, F01, F05 |
| RQ2 | Are observed pairwise differences (DT-GSK vs each comparator) statistically reliable under the declared unit of analysis and multiplicity family? | **Primary** | AN-PW-2017-*, AN-PWRUN-2017-* | RS-07, T02 |
| RQ3 | Are statistically reliable differences practically meaningful (effect sizes with uncertainty intervals)? | **Primary** | AN-EFF-2017-* | RS-08, RS-09, T03, T-BCA |
| RQ4 | How does the panel result vary across dimensions, functions, and verified CEC2017 function classes? | **Secondary** (dimension trend descriptive; function-class strictly exploratory) | AN-TREND-2017, AN-CLASS-2017 | IN-01, F03 |
| RQ5 | What convergence behavior is visible under the pre-specified curve-selection rule (P5)? | **Descriptive** | AN-CONV-* | IN-02, F02 |
| RQ6 | Do the CEC2011 (secondary real-world) and CEC2013 (second comparison suite) results support, qualify, or contradict the primary CEC2017 result? | **Secondary** | AN-OMNI-2011-NATIVE, AN-PW-2011-NATIVE, AN-EFF-2011-NATIVE, AN-OMNI-2013-*, AN-PW-2013-*, AN-EFF-2013-* | RS-10, RS-11, IN-03, T04, T06 |
| RQ7 | What wall-time cost accompanies DT-GSK, based on admissible runtime evidence (`per_run.csv` `runtime_seconds`)? Memory is answered analytically via `phase_03/complexity_analysis.md` plus an `evidence_gap_register.md` entry (no validated measurement harness exists in the release). | **Descriptive** | AN-COST-2017 | T-RUNTIME, LM-04 |
| RQ8 | How sensitive are conclusions to reasonable analysis choices (robustness checks of Section 10)? | **Exploratory** | AN-ROB-2017, AN-EXP-BH-2017 | robustness disclosures |

**Supplement-only ablation questions — pre-registered now, answered PHASE_12_ONLY** (claims AB-01…AB-03; exhibit rows X-ABL-01…03; P6; `DEFERRED_TO_PHASE_12_SUPPLEMENT_ONLY`; no ablation number, table, or component-causality statement may enter the main manuscript; staging `results/_ablation/` is quarantined and not citable until promoted to a release):

| RQ | Question | Class | Family |
|---|---|---|---|
| RQ-A1 | Which adaptive-scaffold components (ACE/NLPSR/BSE/archive/linkage/local search) contribute, under byte-stable single-toggle cells? (ARGP, final polish, and deep-stall restart are pre-registered exclusions/overlay cells per ablation_preregistration.md) | **PHASE_12_ONLY** | AN-ABL-SCAFFOLD |
| RQ-A2 | Does the interaction-structure memory contribute at D ≥ 50 (full / no-adaptive / no-sgsm cells on the CEC2013 "hold-out" ablation design — "hold-out" used ONLY as this design's frozen name)? | **PHASE_12_ONLY** | AN-ABL-SGSM-OVERLAY |
| RQ-A3 | What is the effect of the `final_polish_enabled` toggle — `full` vs the pre-registered fourth SGSM-overlay cell `no_finalpolish` (ablation_preregistration.md Sec. 2) — under Wilcoxon/Holm? | **PHASE_12_ONLY** | AN-ABL-POLISH |

Ablation families reuse the machinery of Sections 5–7 unchanged (same tests, same multiplicity discipline, same tie rule), applied to a future promoted ablation release; their pre-registration here fixes the methods so Phase 12 cannot tune them to outcomes.

Evidence cards for this section: `friedman1937use`, `demsar2006statistical` (methodology grounding per claim BG-06).

---

## 2. Primary endpoint and estimand conventions (task 2)

- **Primary endpoint:** final objective error `error = f(x_best) − f_optimum` exactly as recorded in the release (`per_run.csv` column `error`; summary CSVs carry the matching five-statistic set). The release applies the suite convention error < 1e-8 → 0 (`report_zero_tol = 1e-8`, verified in `papers/governance/benchmark_protocol_audit.md`; claim PR-05 [awad2016problem]). This floor is a protocol reporting convention, never presented as an accuracy achievement.
- **CEC2011 exception (by design):** the `error` column is NaN on all rows because problems lack published optima (anomaly register rows A2-015…A2-027; claim PR-02 [das2011cec2011]). The CEC2011 endpoint is therefore **`best_fitness`** (raw objective value, lower better); every CEC2011 statistic in this plan substitutes best_fitness for error. This NaN is a design property, not missing data.
- **Transformation:** none for any test or rank. Log10 scaling is display-only (convergence plots and any log-scaled table columns), with the render-time floor disclosed per P2 and the Log10Error-empty-cell writer convention (anomaly rows A2-002 etc.). No smoothing, no extrapolation.
- **Central tendency:** mean of the endpoint over runs within a (function, dimension, algorithm) cell — 51 runs on CEC2017 and CEC2013, 25 runs on CEC2011 (claim PR-04). This per-function mean is the primary ranking statistic (CR-0003) and the input to all across-function tests (Section 5, 6).
- **Dispersion:** standard deviation over the same runs (as stored in the release summary CSVs, verified value-identical to gen_logs final checkpoints in `seed_and_pairing_audit.md` Section 6, 580/580).
- **Ranking direction:** lower is better, everywhere.
- **Success threshold (descriptive only):** the protocol 1e-8 target defines per-cell success/failure rates where per-run evidence exists (Section 4); never an inferential endpoint.
- **Failure/missing encoding — disclose, never impute:** no run-level failures/timeouts exist in the release (termination is `max_evaluations` or the protocol-legitimate `target_error_reached` early stop, anomaly rows A2-001/A2-029/A2-032; early-stopped runs are complete observations at their recorded endpoint). The single missing-evidence case is **apgsk CEC2017 D10/D30/D50 per-run data** (anomaly rows A2-004…A2-007; `data_ledger.csv` rows marked `blocked-pending-recovery-or-new-release`): per_run.csv covers D100 only. Disposition pre-specified in Sections 6–7; those cells are never imputed, interpolated, or silently dropped — every affected exhibit cell is marked **disclosed-unavailable** with a footnote citing the anomaly register.
- **Primary analysis family structure:** primary = CEC2017 per-(dimension) families; secondary = CEC2011 (one native-dimension family) and CEC2013 per-(dimension) families; exploratory = Section 10/11 items. No family ever mixes suites or dimensions.

Evidence cards: `friedman1937use` (rank basis), `demsar2006statistical` (comparison design); protocol claims PR-01…PR-06 [awad2016problem; das2011cec2011; liang2013cec2013].

---

## 3. Units, estimands, pairing, and pseudoreplication (task 3)

For every analysis family the following declarations hold (repeated per-family in Section 12 registry rows):

- **Observation unit:** one run of one algorithm on one (suite, function, dimension) cell — a `per_run.csv` row (or, for apgsk CEC2017 D100-excluded dims, no admissible observation unit exists; see disposition).
- **Experimental unit for across-function claims:** the benchmark **function** (task). CEC2017: 29 tasks per dimension (F1, F3–F30; F2 excluded per protocol, PR-01). CEC2013: 28 tasks per dimension. CEC2011: 22 tasks (problems, native dimensions).
- **Task unit:** (function, dimension) within a suite; CEC2011 task unit is the problem at its native dimension.
- **Aggregation before across-function testing:** per-function mean over runs (Section 2). Run-level data enter tests ONLY within a single function (per-function pairwise tests and effect sizes, Sections 6–7).
- **Pairing key:** the unified optimizer-independent seed schedule `get_cec_seed(20240620, dim, func, run)` = `(20240620 + 1000003*dim + 1000033*func + 1000037*run) mod 2147483646 + 1`, verified by full recomputation of all 70,813 schedule rows with 0 mismatches, 0 duplicate keys, injective over the panel domain, with shared runner-generated X0 (`papers/governance/seed_and_pairing_audit.md` Sections 1–4). Pairing is VALID for every comparator pair on all three suites; run r of any two panel algorithms on a (suite, func, dim) cell shares seed, instance, and initial population (documented exception: DT-GSK self-init draws its own 5·D initial population from the same fair-start stream — disclosed per PR-06). For across-function tests the pairing key is the function identity (identical function sets across all 7 optimizers, verified in the same audit).
- **Independence assumptions:** runs within a cell are independent given distinct seeds; functions within a suite×dimension are treated as independent tasks for Friedman/Wilcoxon purposes (standard benchmark-practice assumption, BG-06 [demsar2006statistical; friedman1937use]); dimensions are NEVER pooled (Section 5).
- **Pseudoreplication prohibition (binding):** across-function claims use function-level aggregation only — Friedman over functions on per-function summary statistics; Wilcoxon across functions on per-function means (the GSK-family convention). Run-level observations may support per-function pairwise tests and effect sizes where per-run evidence exists for BOTH algorithms, and are **never pooled across functions as if independent**. Run-level and function-level variability answer different questions and are never mixed within one claim (PAPER_BUILD_PROMPT Section 7.3).
- **Sidedness:** all Wilcoxon tests two-sided (conservative; direction is then read from the signed statistic/effect size). Rationale: the plan must not presuppose DT-GSK superiority in any cell (see D30 limitation LM-01).

Evidence cards: `wilcoxon1945individual`, `friedman1937use`, `demsar2006statistical`.

---

## 4. Descriptive reporting (task 4)

- **Five-statistic set** per (function × dimension × algorithm) cell: **best, median, mean, worst, SD** — exactly the release summary-CSV schema (audit-verified against gen_logs, 580/580 for apgsk; available for all 7×(suite,dim) cells including apgsk CEC2017 D10/D30/D50, whose summary CSVs are complete). Where per-run evidence exists, run count, success rate and failure count against the 1e-8 protocol target are additionally retained in the analysis bundle (CR-0003); for apgsk CEC2017 D10/D30/D50 these per-run-derived descriptive quantities are disclosed-unavailable. [RESOLVED CR-0006 2026-07-11: apgsk per-run recovered; cell now computed]
- **Precision policy:** display = scientific notation, 4 significant figures; ranks to 2 decimals; p-values reported to 4 significant figures and **bounded below at 1e-4** (report "< 1.0e-4"; never "p = 0"). All ranks, tests, and tie decisions computed on unrounded values; rounding applied only at render time; the formatting policy stored with the analysis bundle.
- **Numerical tie rule:** two values tie iff |delta| < 1e-8 (aligned with the protocol zero floor). Applied to per-function mean comparisons for win/tie/loss and to paired differences (a paired difference with |d| < 1e-8 is a zero-difference).
- **Win/tie/loss basis (T01):** per-function **mean** errors (best_fitness for CEC2011), DT-GSK vs each comparator, tie rule above, denominator = full function set of the suite×dimension (29/28/22). These W/T/L counts are descriptive; statistical significance is never inferred from them. A second, separately-labeled count — "significantly better / no significant difference / significantly worse after Holm" — is defined by the inferential tests of Section 6 (T02) and is the only count from which significance language may be drawn.
- **Table ordering:** P1 panel order (gsk, agsk, apgsk, fdb-agsk, atmals-gsk, eGSK, dt-gsk) in every table and legend; per-suite function order F1, F3–F30 (CEC2017), F1–F28 (CEC2013), P1–P22 (CEC2011).

Evidence cards: `david_order_statistics` (order-statistic descriptives: best/median/worst), `demsar2006statistical` (reporting practice).

---

## 5. Omnibus comparison (task 5)

- **Test:** Friedman test [friedman1937use] over functions, per **suite × dimension**, on per-function mean errors (best_fitness for CEC2011), k = 7 algorithms. Task counts: **29** (CEC2017, each of D10/D30/D50/D100), **28** (CEC2013, each of D10/D30/D50), **22** (CEC2011, single native-dimension family).
- **Refinement (pre-registered):** the Iman–Davenport F-distribution correction is computed and reported alongside the Friedman chi-square (statistic, df, N, p per the precision policy). The Iman–Davenport p-value is the omnibus decision criterion at **alpha = 0.05** per family.
- **Nemenyi CD display condition:** a critical-difference diagram [demsar2006statistical] (F01-D10…F01-D100) is rendered for a suite×dimension ONLY when its omnibus is significant at alpha = 0.05; otherwise the exhibit cell states "omnibus not significant; CD diagram omitted by pre-registration". Pairs inside a common CD band are reported as not statistically separable (RS-06); narrative claims follow formal inference, never visual rank order alone.
- **NO cross-dimension pooling:** there is no omnibus test across dimensions, ever. The **overall-rank row** of T05 is a purely **descriptive aggregation** — the unweighted arithmetic mean of the four per-dimension Friedman mean ranks (CEC2017) or three (CEC2013) — labeled "descriptive aggregation of per-dimension ranks; no test attached" in the table note. RS-01's "overall" placeholder binds to this descriptive row.
- **apgsk note:** all omnibus analyses use per-function means from summary CSVs, which are complete for apgsk at all four CEC2017 dimensions; the omnibus families are therefore unaffected by anomaly A2-004.

Analysis families: AN-OMNI-2017-D10/D30/D50/D100, AN-OMNI-2013-D10/D30/D50, AN-OMNI-2011-NATIVE; descriptive rows AN-RANKAGG-2017-OVERALL, AN-RANKAGG-2013-OVERALL.

Evidence cards: `friedman1937use`, `demsar2006statistical`.

---

## 6. Pairwise family and multiplicity (task 6)

Two pre-registered pairwise layers, never mixed within a claim:

**6a. Primary pairwise layer — across functions (the GSK-family convention).**
- DT-GSK vs each of the 6 comparators, per suite × dimension.
- Test: Wilcoxon signed-rank [wilcoxon1945individual] **across functions on per-function mean errors** (n = 29 / 28 / 22 paired functions; pairing key = function identity). Two-sided; zero-differences (|d| < 1e-8) discarded per the classical Wilcoxon zero-method (`scipy` `zero_method='wilcox'`; exact distribution where implementation permits, else normal approximation with tie correction — the method actually used is recorded per test in `statistical_results.csv`).
- Multiplicity: **Holm** [holm1979simple] within each (suite, dimension) family, **m = 6** hypotheses (the 6 comparators). Alpha = 0.05 family-wise. Raw p, Holm-adjusted p, statistic, direction, n, and tie/zero counts all reported.
- **apgsk CEC2017 D10/D30/D50 disposition (pre-specified, binding):** because the release's `per_run.csv` for apgsk/cec2017 covers D100 only (anomaly A2-004; `data_ledger.csv` rows `blocked-pending-recovery-or-new-release`), this function-level test on per-function means (computable from the complete summary CSVs) is **the only valid inferential basis vs apgsk at CEC2017 D10/D30/D50**. It is pre-registered here as exactly that, so the main-text pairwise conclusion vs apgsk at those dimensions rests on AN-PW-2017-D10/D30/D50 and never on run-level quantities.

**6b. Supplement pairwise layer — run-level, per function.**
- Per-function Wilcoxon signed-rank on the 51 (25 for CEC2011) paired run errors, pairing key = run index under the unified seed schedule (audit-verified identical seeds per (dim, func, run)). Computed ONLY where per-run evidence exists for BOTH algorithms.
- Multiplicity: Holm within each (suite, dimension, comparator) family across its functions (m = 29 / 28 / 22). These feed the supplement matrices T02-FULL-* and the T02 "significantly better / n.s. / significantly worse after Holm" counts. Alpha = 0.05.
- **apgsk exclusion:** AN-PWRUN-2017-D10/D30/D50 exclude the apgsk column entirely; the matrix cell block is rendered "disclosed-unavailable (per-run evidence absent from release; anomaly A2-004)". [RESOLVED CR-0006 2026-07-11: apgsk per-run recovered; cell now computed] AN-PWRUN-2017-D100 includes apgsk (per_run.csv complete there, 1,479/1,479 audit-verified). Any future use of `gen_logs` final checkpoints as a sanctioned per-run source for those cells (resolution option 1 of `seed_and_pairing_audit.md` Section 6) would be a **logged confirmatory amendment** under Section 13, not a silent change.
- **Benjamini–Hochberg** [benjamini1995controlling] appears ONLY in the separately-labeled exploratory family AN-EXP-BH-2017 (same tests, BH-FDR at q = 0.05, clearly captioned "exploratory FDR analysis; separate family; not comparable to Holm results"). Holm and BH results are never mixed inside one claim; no headline uses BH.

Evidence cards: `wilcoxon1945individual`, `holm1979simple`, `benjamini1995controlling`.

---

## 7. Effect sizes and uncertainty intervals (task 7)

- **Measures:** Vargha–Delaney A12 [vargha2000critique] and Cliff's delta (= 2·A12 − 1), computed at **run level within each function** where per-run evidence exists for both algorithms (51 vs 51 runs; 25 vs 25 on CEC2011).
- **Direction definition (explicit, binding):** A12 is the probability that a randomly chosen DT-GSK run achieves a **strictly lower error** (better) than a randomly chosen comparator run on the same function, ties counted half: A12 = [#(x_ism < x_comp) + 0.5·#(ties, |d| < 1e-8)] / (n_ism·n_comp). **A12 > 0.5 favors DT-GSK**; delta > 0 favors DT-GSK. Magnitude labels follow vargha2000critique thresholds (|A12 − 0.5|: ≥ 0.06 small, ≥ 0.14 medium, ≥ 0.21 large), stated in every caption that uses them; no ad-hoc labels.
- **Interval:** BCa bootstrap [efron1993introduction] **95% CI on the paired mean-error difference** (mean over runs of `error_ism − error_comp`, paired by run via the unified seed schedule), per (suite, dimension, function, comparator).
  - **Resampling unit:** paired runs within a function (resample the 51/25 paired differences with replacement); the hierarchy never crosses functions — runs are never bootstrapped to support an across-function claim (that claim class is served by Section 6a).
  - **B = 10,000 resamples; confidence level 95%; deterministic analysis RNG per the AUTHORITATIVE fully-explicit entropy-list construction of `strict_source_execution.md` Sec. 5, quoted verbatim:** "per-cell RNG = `numpy.random.default_rng(numpy.random.SeedSequence([20240620, <suite_ordinal>, <dimension>, <function>, <comparator_P1_index>]))` with `suite_ordinal` in `{2017, 2013, 2011}` and `comparator_P1_index` the 0-based P1 position — one independent, reproducible stream per (suite, dim, function, comparator); resampling order fixed by iterating cells in the file sort order." This analysis seed is distinct from the experiment run-seed base (same integer by design for auditability; roles never confused). Recorded per PAPER_BUILD_PROMPT Section 7.7: the existing `papers/scripts/generate_t16_bca.py` was inspected and uses `BASE_SEED = 20260422` with per-cell `np.random.default_rng(20260422 + dim*7 + i)` for a different statistic (bootstrap CIs on mean ranks across functions, n_boot = 10,000); that rank-CI machinery, if used, keeps its inspected scheme and is reported as its own descriptive companion — it is not the paired-difference BCa defined here. The paired-difference BCa implementation extends the release-wired generator per P7 and records its exact seed derivation in `statistical_results.csv`.
  - **Failure handling (pre-specified):** degenerate cells (all paired differences identical, zero variance, or BCa acceleration/bias terms undefined) report the point estimate plus the disclosure "no CI (degenerate cell)"; never a fabricated interval, never percentile-fallback without labeling (if a percentile fallback is ever used it is labeled "percentile (BCa degenerate)").
- **Attachment rule (binding):** every planned significance claim and every headline comparative claim carries at least one effect size AND one uncertainty interval (RS-08/RS-09; T03 condensed in main, T03-FULL-*/T-BCA in supplement).
- **apgsk CEC2017 D10/D30/D50:** A12, Cliff's delta, and BCa CIs are per-run-dependent and therefore **disclosed-unavailable** for these cells (anomaly A2-004) [RESOLVED CR-0006 2026-07-11: apgsk per-run recovered; cell now computed]; the T03/T-BCA apgsk columns at those dimensions carry the disclosure footnote. **Pre-specified effect-size attachment for the DT-GSK-vs-apgsk column at CEC2017 D10/D30/D50 (per-run data absent):** the attached effect size is the **matched-pairs rank-biserial correlation**, computed from the same across-function Wilcoxon signed-rank on per-function means already pre-registered in Section 6a (AN-PW-2017-D10/D30/D50) — it requires no per-run data, and rank-biserial is sanctioned by CR-0003/Section 7.7; the accompanying uncertainty interval for those cells is **DISCLOSED-UNAVAILABLE** (never imputed). [CR-0006 2026-07-11: run-level A12/Cliff + BCa vs apgsk now available via AN-EFF-2017-D10/D30/D50; the function-level rank-biserial basis is unchanged] apgsk D100 cells are computed normally.

Analysis families: AN-EFF-2017-D10/D30/D50/D100, AN-EFF-2013-D10/D30/D50, AN-EFF-2011-NATIVE.

Evidence cards: `vargha2000critique`, `efron1993introduction`, `david_order_statistics` (rank/order basis of A12).

---

## 8. Convergence analysis (descriptive; RQ5)

- Aggregation per P2 (binding): per-checkpoint **mean error across all runs** per algorithm from `gen_logs/CheckpointErrors_<opt>_F<f>_D<d>.csv`; identical basis for all 7 curves in every panel; representative-run fallback only on caption-disclosed absence; missing algorithm disclosed, never fabricated; display-only log floor; no smoothing; no extrapolation past termination (early-stop truncation per anomaly rows A2-003/A2-009 disclosed at render).
- Styling per P3 (Okabe–Ito map, fixed); panel order per P1.
- **Main-text selection per P5 (pre-registered before any figure is viewed):** featured dimensions D30 and D100; 4 CEC2017 functions per featured dimension, one per suite category, strata (difficulty terciles of panel-median final error; DT-GSK standing by per-function mean-error rank) computed in Phase 6 from release summary CSVs only, before rendering; fill priority (hard,weak) > (hard,comparable) > (moderate,comparable) > (easy,strong) > remainder; ties to lowest function number; the 8 panels jointly include ≥ 1 hard and ≥ 1 DT-GSK-weak case. Selections recorded in `curve_selection.csv` before rendering.
- No inferential statistics are attached to convergence curves; descriptive shape statements only, separated from mechanism explanation (IN-02 wording constraints).

Analysis families: AN-CONV-2017-D10/D30/D50/D100 (supplement full grids; main-text picks at D30/D100 per P5), AN-CONV-2011-NATIVE, AN-CONV-2013-D30 (D30 only per P4).

Evidence cards: none required (descriptive); protocol basis PR-04.

---

## 9. Cost analysis (descriptive; RQ7)

- Wall-time metric: `runtime_seconds` from release `per_run.csv`, summarized per (suite, dimension, algorithm) as mean ± SD over runs; DT-GSK's no-extra-objective-evaluation property is stated with its compute-cost citation (`phase_03/complexity_analysis.md`; MT-08 wording rule).
- Comparability qualifications per `papers/governance/comparability_audit.md` and LM-04: eGSK reference provenance limits cross-implementation runtime comparability; **no runtime-superiority claim** is made; per-cell comparability status disclosed in T-RUNTIME.
- apgsk CEC2017 D10/D30/D50 runtime cells: disclosed-unavailable (per-run evidence absent). [RESOLVED CR-0006 2026-07-11: apgsk per-run recovered; cell now computed]
- Memory: analytic derivation only (`complexity_analysis.md`) + `evidence_gap_register.md` entry; no measured-memory claim.

Analysis family: AN-COST-2017 (CEC2011/CEC2013 runtime summarized in the same family's supplement rows).

---

## 10. Robustness checks (exploratory; RQ8)

Pre-specified checks, each labeled exploratory, run per suite×dimension where evidence permits, reported as stable/unstable statements only:

1. mean vs median per-function summary for ranks and W/T/L;
2. error-floor sensitivity (recompute ties/W/T/L at floor 1e-6 vs 1e-8; display floor variants for log plots);
3. leave-one-function-out Friedman mean ranks (function influence);
4. exclusion of disputed comparator cells (apgsk CEC2017 non-D100 columns; eGSK provenance-qualified cells) from descriptive rank aggregates;
5. pairing-assumption check: unpaired Mann–Whitney companion to selected per-function Wilcoxon results (labeling only; Holm families unchanged);
6. correction-family definition check: Holm vs BH (AN-EXP-BH-2017), never mixed into headlines;
7. secondary-suite inclusion/exclusion effect on qualitative conclusions;
8. dimension-aggregation variants of the descriptive overall row (mean vs median of per-dimension ranks).

Robustness procedure definitions: robustness_plan.md is authoritative; the AN-ROB-2017-01..08 IDs map per its crosswalk table.

Binding rule: a headline conclusion that reverses under any of these reasonable choices MUST be reported as unstable (PAPER_BUILD_PROMPT Section 7.11).

Analysis family: AN-ROB-2017 (checks enumerated AN-ROB-2017-01…08).

Evidence cards: `benjamini1995controlling` (check 6), `wilcoxon1945individual` (check 5).

---

## 11. Function-class analysis (exploratory; RQ4 partial)

Permitted only with class labels verified from the approved suite source (CEC2017 categories: unimodal F1/F3; simple multimodal F4–F10; hybrid F11–F20; composition F21–F30 per [awad2016problem], the same verified partition P5 already uses); pre-specified here as **exploratory and descriptive** (per-class mean ranks and W/T/L only; no per-class inference, avoiding micro-family multiplicity); small class sizes acknowledged in captions; never converted to mechanism/causality wording ("works because of" is blocked).

Analysis family: AN-CLASS-2017.

---

## 12. Analysis-family registry (pre-registered IDs)

Every family below gets rows in `papers/analysis/rel-2026-07-10-262fc16c9/primary_stats/statistical_results.csv` (Section 7.14 schema) with `analysis_id` = family ID; alpha = 0.05 throughout; endpoint per Section 2; units per Section 3.

| Family ID | Definition (test; unit; n; multiplicity) | Class |
|---|---|---|
| AN-DESC-2017-D10/D30/D50/D100 | Five-statistic descriptives + W/T/L on per-function means; 29 functions; no test | descriptive |
| AN-OMNI-2017-D10/D30/D50/D100 | Friedman + Iman–Davenport over 29 functions on per-function mean errors, k=7; Nemenyi CD only if significant | primary |
| AN-RANKAGG-2017-OVERALL | Descriptive mean of the 4 per-dimension Friedman mean ranks; no test | descriptive |
| AN-PW-2017-D10/D30/D50/D100 | Wilcoxon signed-rank across 29 functions on per-function means, DT-GSK vs each comparator; Holm m=6 per dimension; sole valid basis vs apgsk at D10/D30/D50 | primary |
| AN-PWRUN-2017-D10/D30/D50/D100 | Per-function run-level Wilcoxon (51 paired runs, seed-schedule pairing); Holm across 29 functions per (dim, comparator); apgsk excluded at D10/D30/D50 (disclosed-unavailable) [RESOLVED CR-0006 2026-07-11: apgsk per-run recovered; cell now computed] | primary (supplement detail) |
| AN-EFF-2017-D10/D30/D50/D100 | A12 + Cliff's delta at run level per function; BCa 95% CI on paired mean differences (B=10,000; seed scheme Section 7); apgsk cells disclosed-unavailable except D100 [RESOLVED CR-0006 2026-07-11: apgsk per-run recovered; cell now computed] | primary |
| AN-CONV-2017-D10/D30/D50/D100 | Descriptive per-checkpoint mean-across-runs convergence overlays (P2/P3); main-text picks per P5 at D30/D100 | descriptive |
| AN-TREND-2017 | Descriptive Friedman-mean-rank vs dimension trend (F03); no test; no extrapolation beyond D100 | secondary (descriptive) |
| AN-CLASS-2017 | Exploratory per-class descriptive ranks/W/T/L on verified CEC2017 categories | exploratory |
| AN-COST-2017 | Descriptive runtime_seconds summaries + analytic memory; comparability-qualified; no superiority claim | descriptive |
| AN-OMNI-2013-D10/D30/D50 | Friedman + Iman–Davenport over 28 functions, k=7; CD condition as above | secondary |
| AN-RANKAGG-2013-OVERALL | Descriptive mean of the 3 per-dimension Friedman mean ranks; no test | descriptive |
| AN-PW-2013-D10/D30/D50 | Wilcoxon across 28 functions on per-function means; Holm m=6 per dimension | secondary |
| AN-PWRUN-2013-D10/D30/D50 | Per-function run-level Wilcoxon (51 runs); Holm across 28 functions per (dim, comparator) | secondary (supplement) |
| AN-EFF-2013-D10/D30/D50 | A12/Cliff + BCa as Section 7 | secondary |
| AN-CONV-2013-D30 | Descriptive convergence grids, D30 only (P4) | descriptive |
| AN-OMNI-2011-NATIVE | Friedman + Iman–Davenport over 22 problems on per-problem mean best_fitness, k=7 | secondary |
| AN-PW-2011-NATIVE | Wilcoxon across 22 problems on per-problem mean best_fitness; Holm m=6 | secondary |
| AN-PWRUN-2011-NATIVE | Per-problem run-level Wilcoxon (25 paired runs); Holm across 22 problems per comparator | secondary (supplement) |
| AN-EFF-2011-NATIVE | A12/Cliff + BCa on best_fitness paired differences (25 runs) | secondary |
| AN-CONV-2011-NATIVE | Descriptive convergence grids, 22 problems, native dims | descriptive |
| AN-ROB-2017 (checks -01…-08) | Section 10 robustness battery | exploratory |
| AN-EXP-BH-2017 | BH-FDR relabeling of AN-PWRUN-2017-*; separate family; never headline | exploratory |
| AN-ABL-SCAFFOLD | Scaffold-toggle cells vs full; Section 6/7 machinery; future promoted ablation release only | PHASE_12_ONLY |
| AN-ABL-SGSM-OVERLAY | full/no-adaptive/no-sgsm cells on the CEC2013 "hold-out"-named ablation design | PHASE_12_ONLY |
| AN-ABL-POLISH | final_polish_enabled toggle: full vs no_finalpolish (fourth SGSM-overlay cell, ablation_preregistration.md Sec. 2) under Wilcoxon/Holm | PHASE_12_ONLY |

**Suite roles (task 9, per `phase_04/novelty_scope.md` Section 3 evidence-role table):** CEC2017 = PRIMARY; CEC2011 = SECONDARY (real-world corroboration; no headline rests on it alone; "corroborate", never "validate"); CEC2013 = **second comparison suite** — never "independent", "holdout", or "validation" in main text ("hold-out" survives only as the frozen name of the Phase-12 SGSM-overlay ablation design); CEC2020 / CEC2013-LSGO = context-only, outside the pairing framework (`seed_and_pairing_audit.md` Section 4), no claims, not citable.

---

## 13. Change control (binding; Phase 5 exit criteria)

This SAP is frozen as of the date above, before any outcome inspection. After freeze:

1. **Confirmatory amendment:** any change that preserves outcome-blindness (made before the affected outcome is inspected, motivated by data-availability or tooling facts, e.g., sanctioning `gen_logs` final checkpoints as the apgsk per-run source per audit resolution option 1) must be logged in `papers/governance/decision_log.md` with date, motivation, affected family IDs, and an explicit statement that no affected outcome had been viewed. The amended analysis remains confirmatory.
2. **Exploratory deviation:** any change made after the affected outcome has been inspected (or that cannot demonstrate outcome-blindness) demotes every affected analysis to **exploratory**; it must be labeled as such in every exhibit and never supports a headline or significance claim.
3. No unlogged change of endpoint, aggregation, family definition, multiplicity procedure, tie rule, seed scheme, or suite role is permitted. The Phase 6 orphan check audits `statistical_results.csv` against this registry; any analysis appearing there without a Section 12 family ID (or amendment log entry) is a governance defect.
