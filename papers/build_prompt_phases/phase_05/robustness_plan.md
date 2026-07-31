# Phase 5 — Pre-registered robustness plan (tasks 12 + 10)

- **Date frozen:** 2026-07-10 (BEFORE any outcome inspection; no statistic, rank, p-value,
  or mean has been computed or viewed from the evidence in preparing this plan).
- **Phase / tasks:** Phase 5, task 12 (robustness checks) and task 10 (parameter-sensitivity
  treatment).
- **Evidence release:** `rel-2026-07-10-262fc16c9` (`benchmarks/cec_reference_results/`,
  read-only; anchor commit `262fc16c91fbe5608a1a0b0c5df3cbcd009edc21`).
- **Frozen inputs honored:** `phase_04/exhibit_plan.csv` pre-registrations P1–P8;
  `phase_04/thesis.md`; `papers/governance/claims_evidence_matrix.csv` (50 rows);
  `phase_03/algorithm_freeze_manifest.json`.
- **Governance sources read (cited by path):** `papers/governance/comparability_audit.md`;
  `papers/governance/fp_environment_audit.md`; `papers/governance/seed_and_pairing_audit.md`;
  `papers/governance/phase2_anomaly_register.csv`; `papers/governance/evidence_gap_register.md`
  (EG-006); `phase_03/complexity_analysis.md`; `phase_03/evaluation_accounting_report.md`.
- **Execution phase:** all checks below are EXECUTED IN PHASE 6, after the primary analyses,
  through the strict-source loader (`src/gsk_family/analysis/result_loader.py`:
  `set_strict_source` / `GSK_STRICT_SOURCE`, `audit_source_open`), reading ONLY the release.
  `results/` staging (including `results/_ablation/`) is quarantined and never read.
- **Output area:** `papers/analysis/rel-2026-07-10-262fc16c9/<suite>/robustness/`.
- **Tooling (verified present):** `src/gsk_family/analysis/statistics.py`
  (`wilcoxon_paired`, `holm_correction`, `benjamini_hochberg`, `friedman_rank`,
  `vargha_delaney`, `win_tie_loss`, `bootstrap_bca_ci`),
  `src/gsk_family/analysis/statistical_tests.py` (`wilcoxon_signed_rank`,
  `friedman_rank_test`), `src/gsk_family/cli/stats.py` (`gsk-stats`).

---

## 0. Global rules binding every check

### 0.1 Endpoint and aggregation conventions (identical to primary analyses)

- **Endpoint:** final `error` per run for cec2017/cec2013 (`error_vs_optimum` basis);
  final `best_fitness` per run for cec2011 (`raw_objective` basis; `error` is NaN by
  design — anomaly register rows A2-015…A2-027). Never mix bases.
- **Pseudoreplication rule:** across-function claims use function-level aggregation
  (Friedman over functions on per-function summary statistics [friedman1937use;
  demsar2006statistical]; Wilcoxon across functions on per-function means as the
  GSK-family convention [wilcoxon1945individual]). Run-level data support per-function
  pairwise tests and effect sizes where per-run evidence exists; runs are NEVER pooled
  across functions as if independent.
- **Multiplicity:** Holm is the primary correction [holm1979simple]. Benjamini–Hochberg
  appears ONLY in check R6 as a separately-labeled exploratory recomputation
  [benjamini1995controlling]. No mixed families.
- **Pairing basis:** the unified seed schedule
  `get_cec_seed(20240620, dim, func, run)` gives identical seeds and shared runner-supplied
  X0 across all seven optimizers per (dim, func, run) — verified by full recomputation of
  70,813 schedule rows with 0 mismatches in `papers/governance/seed_and_pairing_audit.md`
  (§2–§4: pairing VALID for every comparator pair on all three primary suites).
- **Panel and naming:** 7 algorithms in P1 order (gsk, agsk, apgsk, fdb-agsk, atmals-gsk,
  egsk, dt-gsk); all wording scoped "within the GSK family panel"; eGSK per
  `phase_04/terminology_glossary.md` and rule R-EGSK-1
  (`papers/governance/comparability_audit.md` §4): only SciPy-SLSQP-port values, named as
  the Python port. CEC2013 is the "second comparison suite" (never independent/holdout);
  CEC2011 is the secondary real-world suite.

### 0.2 Primary-conclusion set (what a "divergence" is measured against)

The primary analyses (Phase 6, per `phase_04/exhibit_plan.csv` T01/T02/T03/T05/T06/F01/F03)
produce, per suite:

- C-a. DT-GSK's Friedman ordinal rank position per dimension and overall (T05/T06/F03).
- C-b. The Holm-corrected per-comparator per-dimension pairwise decision triples
  better/tie/worse per function, and their W/T/L counts (T02, T02-FULL-*).
- C-c. Effect-size direction categories per comparator per dimension (T03).
- C-d. Any Section-5.1-style rank statement admitted into the main text (e.g., the P5
  pre-registered "#2 behind eGSK at D30" statement, to be re-derived in Phase 6).

**Divergence (uniform definition):** a robustness variant CHANGES any element of the
primary-conclusion set — an ordinal rank position changes; a Holm-significant pairwise
decision flips category (better↔tie, tie↔worse, better↔worse); or a main-text rank
statement no longer holds under the variant.

**Uniform decision rule for reporting (binding, never silent):**

1. **Agreement** → one row in the supplement robustness summary table (Section 4 template)
   stating agreement; main text unchanged.
2. **Divergence** → (i) full variant result reported in the supplement with the primary
   result side by side; (ii) the affected main-text claim is QUALIFIED in prose (explicit
   sentence naming the check and the direction of the divergence) and its
   `claims_evidence_matrix.csv` row gains a qualifier note in Phase 6; (iii) if the
   divergence touches a headline claim (C1–C4 bindings in `exhibit_plan.csv`), a change
   request is filed per `papers/governance/change_request_register.csv` before Gate 6.
3. Silent omission of a divergent variant is PROHIBITED in all cases.

### 0.3 Pre-specified disposition of the apgsk cec2017 aux-provenance cells

Known data constraint (anomaly register A2-004…A2-007; `comparability_audit.md` §3
provisional class C; `seed_and_pairing_audit.md` A1): `cec2017/apgsk/per_run.csv` covers
D100 ONLY (1,479 rows). Run-level analyses vs apgsk at CEC2017 D10/D30/D50 are NOT
available from `per_run.csv`.

Pre-specified disposition (fixed now, not discovered later):

- **Primary analyses:** apgsk at cec2017 D10/D30/D50 enters function-level analyses only
  (Friedman over per-function summary statistics from the committed summary CSVs, verified
  435/435 against gen_logs final checkpoints per `comparability_audit.md` §2). All
  per-run-dependent quantities for those three cells (paired Wilcoxon, A12/Cliff effect
  sizes, BCa CIs) are marked **disclosed-unavailable** in the exhibits, with a footnote
  citing A2-004 — unless Gate 2 adopts the designate-source option, in which case check R3
  variant (ii) governs.
- apgsk cec2017 D100 and all apgsk cec2013/cec2011 cells are class A and fully in scope.

---

## 1. Task 12 — Pre-registered robustness checks R1–R7

Every check states purpose, exact procedure, and its decision rule (which is the Section
0.2 uniform rule unless narrowed). All numeric fields in the outputs are placeholders
`<RXX:field>` until Phase 6 binds them.

### 1.0 Registry crosswalk — AN-ROB-2017-01..08 ↔ R-checks (binding)

This plan's procedure definitions are AUTHORITATIVE for the Phase 6 robustness battery
(`statistical_analysis_plan.md` Sec. 10 defers here). The pre-registered registry IDs
(`analysis_registry.csv`, following the SAP Sec. 10 enumeration order) map to the
R-checks as stated below; IDs 01..07 distribute over R1–R7 in the SAP's order
(01→R2, 02→R1, 03→R4, 04→R3, 05→R5, 06→R6, 07→R7 cross-suite facet), and
AN-ROB-2017-08 is assigned to R7's pooled block-Friedman vs
mean-of-per-dimension-ranks comparison (the 8th mapping target). Output CSV filenames
follow `strict_source_execution.md` Sec. 5 (`robustness_<suite>_<check-tag>.csv`,
emitted under `<suite>/robustness/`):

| Registry ID (SAP Sec. 10 item) | R-check | Procedure of record | Output file (cec2017 shown) |
|---|---|---|---|
| AN-ROB-2017-01 (item 1: mean vs median) | **R2** | Section R2 (mean vs median re-ranking) | `robustness_cec2017_r01_mean_vs_median.csv` |
| AN-ROB-2017-02 (item 2: error-floor sensitivity) | **R1** | Section R1 — R1's feasibility-aware branch-A/branch-B definition is the SINGLE definition of the floor-sensitivity check; the SAP Sec. 10 wording ("floor 1e-6 vs 1e-8") defers to R1 | `robustness_cec2017_r02_floor_sensitivity.csv` |
| AN-ROB-2017-03 (item 3: LOFO Friedman) | **R4** | Section R4 (leave-one-function-out influence) | `robustness_cec2017_r03_lofo_friedman.csv` |
| AN-ROB-2017-04 (item 4: disputed-cell exclusion) | **R3** | Section R3 (apgsk aux-provenance V1/V2/V3) | `robustness_cec2017_r04_disputed_cell_exclusion.csv` |
| AN-ROB-2017-05 (item 5: paired vs unpaired) | **R5** | Section R5 (unpaired Mann–Whitney companion) | `robustness_cec2017_r05_unpaired_companion.csv` |
| AN-ROB-2017-06 (item 6: Holm vs BH) | **R6** | Section R6 (correction-family check) | `robustness_cec2017_r06_holm_vs_bh.csv` |
| AN-ROB-2017-07 (item 7: secondary-suite inclusion/exclusion) | **R7** (cross-suite scope facet) | Section R7 executed per suite (cec2017 AND cec2013, per the Section 4 template rows) with the suites' overall orderings reported side by side — this side-by-side IS the pre-registered answer to the secondary-suite inclusion/exclusion question (qualitative conclusions with vs without the second comparison suite) | `robustness_cec2017_r07_secondary_suite_effect.csv` |
| AN-ROB-2017-08 (item 8: overall-aggregation variants) | **R7** (pooled-Friedman comparison — the 8th mapping target) | Section R7's pooled (function,dimension)-block Friedman vs the primary descriptive mean-of-per-dimension-ranks aggregation; the pooled block-Friedman appears ONLY here, under the robustness file naming, never as the T05/T06 overall row | `robustness_cec2017_r08_overall_aggregation_variants.csv` |

Floor sensitivity therefore has exactly ONE definition in this build: R1's
feasibility-aware procedure below.

### R1 — Error-floor sensitivity (1e-8 vs no floor)

- **Purpose:** show that conclusions do not depend on the protocol's zero-reporting floor
  (`report_zero_tol = 1e-08`, uniform in all 21 cells per `comparability_audit.md` §1 and
  `run_config.json`).
- **Known constraint (pre-registered, verified read-only):** the floor is applied at
  WRITE time — a feasibility scan of sampled `per_run.csv` files (cec2017/dt-gsk,
  cec2017/gsk, cec2013/agsk) found 0 stored error values in the open interval (0, 1e-8).
  If this holds release-wide, the "no floor" raw values are NOT reconstructible from the
  release, and the check must be executed in its degraded form (branch B). This is decided
  by procedure, not by outcome inspection.
- **Exact procedure (Phase 6):**
  1. Scan every per-run error value in all cec2017/cec2013 class-A cells for values in
     (0, 1e-8). Record the count in the robustness log.
  2. **Branch A (count > 0):** run the full primary analysis pipeline twice — variant
     A1 = errors floored at 1e-8 (values < 1e-8 → 0, the protocol convention); variant
     A2 = raw stored values, no floor. Compare the primary-conclusion set.
  3. **Branch B (count = 0; floor baked in at write time):** the "no floor" variant is
     disclosed as unavailable-by-construction, and the check is executed as its nearest
     admissible surrogate: **tie-handling sensitivity at the floor** — variant B1 =
     primary treatment (exact zeros are legitimate ties; Wilcoxon zero-difference handling
     as implemented in `statistics.py::wilcoxon_paired`); variant B2 = all per-run values
     ≤ 1e-8 treated as exactly equal at the floor for W/T/L, ranking, and test purposes
     (which they already are numerically) PLUS per-function Friedman recomputed with
     mid-rank ties at zero. The supplement discloses that B1/B2 bound the floor's possible
     influence given write-time flooring.
  4. cec2011 is out of scope for R1 (`raw_objective` basis; no floor concept — A2-015).
- **Decision rule:** Section 0.2 uniform rule. Additionally, under branch B the supplement
  MUST carry the sentence that raw sub-floor values are unrecoverable from the release
  (disclosed limitation, not a defect).

### R2 — Summary statistic: mean vs median re-ranking

- **Purpose:** guard the rank claims against skew/outlier dependence of the per-function
  mean (51 runs, heavy-tailed error distributions are common).
- **Exact procedure:** for each suite × dimension, recompute (i) per-function panel ranks
  and Friedman mean ranks [friedman1937use] and (ii) W/T/L counts, using the per-function
  MEDIAN final error (cec2011: median best_fitness) instead of the mean. Medians come from
  the same per-run records (or the committed summary CSVs' Median column, which Phase 2
  verified to be exact aggregations of per_run — `comparability_audit.md` §2, 100%
  Best/Median/Mean/Worst agreement). The apgsk cec2017 D10/30/50 cells use the summary-CSV
  Median column (function-level; consistent with Section 0.3).
- **Decision rule:** Section 0.2 uniform rule, evaluated on C-a and C-d (rank positions
  and rank statements). Pairwise Holm decisions (C-b) are NOT recomputed under R2 — the
  Wilcoxon signed-rank statistic is already rank-based within functions; only the
  across-function ranking basis changes.

### R3 — Disputed/anomalous cells: apgsk aux-provenance handling

- **Purpose:** show that the panel conclusions are not carried by the disposition chosen
  for the three provisional-class-C apgsk cells (Section 0.3).
- **Exact procedure:** for cec2017 D10/D30/D50, run three variants of the function-level
  analyses (Friedman mean ranks + rank positions):
  - V1 (primary): apgsk included via committed summary statistics (Section 0.3).
  - V2 (exclusion): apgsk dropped entirely at those dimensions → 6-algorithm Friedman;
    ranks rescaled to the 6-panel.
  - V3 (conditional; ONLY if Gate 2 adopts the designate-source option of
    `comparability_audit.md` §3 / `seed_and_pairing_audit.md` §6 option 1): per-run values
    for apgsk taken from `gen_logs/CheckpointErrors_apgsk_F*_D{10,30,50}.csv` final
    checkpoint columns (seed-verified 5,916/5,916; summary-consistent 435/435), and the
    per-run pairwise analyses (Wilcoxon+Holm, A12, BCa) rerun WITH apgsk included.
    If Gate 2 instead chooses reproduce-and-promote, V3 is executed against the new
    release subtree and labeled with the new release id.
- **Decision rule:** Section 0.2 uniform rule, with one narrowing: differences between V1
  and V2 that consist ONLY of the mechanical rank rescaling from a 7- to 6-algorithm panel
  (all pairwise orderings preserved) count as agreement. Any ordering change or main-text
  rank-statement failure is a divergence. V3-vs-V1 divergences additionally trigger a note
  in `papers/governance/assumption_register.csv` (unrecorded producing environment).

### R4 — Influence analysis: leave-one-function-out Friedman rank stability

- **Purpose:** detect whether any single benchmark function drives a rank position
  (protection against "one-function wins").
- **Exact procedure:** for each suite × dimension (cec2017 D10/30/50/100 over 29 functions;
  cec2013 D10/30/50 over 28; cec2011 over 22 problems): recompute the Friedman mean ranks
  and ordinal positions N times, omitting one function per repetition (LOFO). Record, per
  algorithm: min/max mean rank over the N recomputations, and every omission that changes
  any ordinal position (which function, which algorithms swap). Same computation applied
  to the overall aggregation of check R7.
- **Decision rule:** a divergence is any LOFO recomputation that changes DT-GSK's ordinal
  position or invalidates a main-text rank statement (C-a, C-d). The influential
  function(s) are named in the supplement, and the affected claim is qualified as
  "sensitive to function F<k>". Positional changes among comparators that do not involve
  DT-GSK or a stated claim are tabulated in the supplement but do not trigger
  qualification.

### R5 — Pairing: paired vs unpaired Wilcoxon agreement

- **Purpose:** demonstrate that conclusions do not hinge on the common-random-numbers
  pairing assumption (valid per `seed_and_pairing_audit.md` §4, but reviewers may ask).
- **Exact procedure:** wherever per-run evidence exists for both sides (all class-A cells;
  apgsk cec2017 D10/30/50 excluded per Section 0.3 unless R3-V3 applies): for each
  (comparator, suite, dimension, function), compute both
  - primary: paired Wilcoxon signed-rank on the 51 (25 for cec2011) per-run endpoint
    pairs [wilcoxon1945individual] (`statistics.py::wilcoxon_paired`), Holm within the
    R6-defined family; and
  - variant: unpaired two-sample rank test (Wilcoxon rank-sum / Mann–Whitney U,
    two-sided) on the same endpoints, Holm within the identically-partitioned family.
    Implementation note: no rank-sum routine exists in `src/gsk_family/analysis/`; the
    Phase 6 script uses `scipy.stats.mannwhitneyu` and is wired through the strict-source
    loader; the script and invocation are recorded in the analysis output area.
  Compare the per-function decision triples and the aggregated W/T/L counts.
- **Decision rule:** Section 0.2 uniform rule on C-b. Expected direction is pre-stated:
  unpaired tests are less powerful under positive pairing correlation, so
  significant→non-significant transitions in the variant are reported but qualify a claim
  ONLY if the main text relied on that specific rejection; any sign REVERSAL
  (better↔worse) is always a divergence and always qualifies.

### R6 — Correction family: Holm (primary) vs Benjamini–Hochberg (exploratory)

- **Purpose:** disclose the dependence of decision counts on the multiplicity procedure.
- **Family definition (pre-registered, identical for both procedures):** one family = the
  set of per-function p-values for one (comparator, suite, dimension) pair
  (m = 29, 28, or 22). This matches the T02/T02-FULL granularity. Families are never
  merged across comparators, dimensions, or suites; the Friedman post-hoc rank comparisons
  in F01 use the Nemenyi procedure [demsar2006statistical] and form no part of these
  families.
- **Exact procedure:** recompute every T02 decision with Benjamini–Hochberg at q = 0.05
  (`statistics.py::benjamini_hochberg`) [benjamini1995controlling] on exactly the same
  p-values and family partition as the Holm primary [holm1979simple]. Output a
  SEPARATELY-LABELED supplement table ("exploratory — BH, not used for any claim") with
  side-by-side Holm/BH decision counts and a list of decisions that differ.
- **Decision rule (narrowed):** BH-vs-Holm differences are EXPECTED (BH is less
  conservative) and are NOT divergences per se. Binding rules: (i) no main-text claim may
  rest on a BH-only rejection — main claims rest on Holm only; (ii) the BH table is never
  mixed into a Holm exhibit; (iii) if BH removes a rejection that Holm makes (possible
  only via the differing family error metric — flagged if observed), that is reported as
  an anomaly in the supplement. No qualification of main claims arises from R6 by
  construction.

### R7 — Dimension aggregation: overall-rank stability vs per-dimension

- **Purpose:** show that any "overall" rank statement (T05 "+ overall" column; F03 trend)
  is not an artifact of the aggregation scheme.
- **Pre-registered primary aggregation (the T05/T06 overall row, per the SAP Sec. 5):**
  the DESCRIPTIVE unweighted arithmetic mean of the per-dimension Friedman mean ranks
  (each dimension contributes equally regardless of function count) — no pooled
  cross-dimension test is attached to the overall row, ever.
- **Exact procedure (this check only):** recompute the overall ordering under the
  variant aggregation = pooled block-Friedman over the union of function × dimension
  blocks (cec2017: N = 29 × 4 = 116 blocks; cec2013: 28 × 3 = 84; cec2011 has native
  dimensions and no overall-across-dimension aggregation — per-suite only). The pooled
  (function,dimension)-block Friedman is computed and reported ONLY as this check's
  output (AN-ROB-2017-08, `robustness_<suite>_r08_overall_aggregation_variants.csv`),
  never as the T05/T06 overall row. Also tabulate the per-dimension ordinal positions
  next to both overall orderings.
- **Decision rule:** divergence if (i) any algorithm's overall ordinal position differs
  between the two aggregations, or (ii) an overall main-text position is contradicted in
  one or more individual dimensions without the main text saying so. Consequence of (ii):
  the main text must state the per-dimension positions explicitly (e.g., the P5-recorded
  known-weak D30 tier) rather than the overall position alone.

---

## 2. Task 10 — Parameter-sensitivity treatment (exploratory ONLY)

### 2.1 Status of evidence (verified read-only, 2026-07-10)

- The release contains NO parametric-sweep evidence: `benchmarks/cec_reference_results/`
  holds only `README.md`, `cec2011`, `cec2013`, `cec2013lsgo`, `cec2017`, `cec2020`
  (no `parametric/` subtree; no files matching `*sens*`).
- This is the standing gap **EG-006** (`papers/governance/evidence_gap_register.md`,
  "Parametric-sweep validated release for T21/T22"), which records the historical study as
  "n = 3 sensitivity evidence" (master Section 4.4) and disposition "additional experiment
  … otherwise omit".
- Consequently the exhibit `T-SENS` (`phase_04/exhibit_plan.csv`) resolves, as of this
  pre-registration, to its evidence-gap branch: **marked unavailable, citing EG-006**,
  unless a validated parametric release is promoted (via `scripts/promote_evidence.py`
  into `benchmarks/cec_reference_results/parametric/<release_id>/`) before Phase 7
  assembly. `results/` staging is NEVER read as a fallback (quarantine, Section 6.10).

### 2.2 Binding rules if (and only if) a parametric release is promoted

1. **Exploratory only.** Every sensitivity exhibit is labeled "exploratory" in its title
   AND caption; content is descriptive (levels, ranges, observed spread) — no hypothesis
   tests, no corrected p-values, and no promotion of any sensitivity observation into a
   main-text performance claim.
2. **n = 3 limitation stated.** The caption and the accompanying prose MUST state the
   n = 3 evidence depth recorded in EG-006 verbatim as a limitation (far below the
   51-run/25-run panel standard), and that no distributional inference is supportable at
   that depth.
3. **Grid/range provenance.** The parameter grid, ranges, seeds, and configuration
   selection rule are transcribed verbatim from the promoted release's own metadata
   (run_config/environment files); if the promoted bundle lacks any of these, the missing
   item is disclosed in-caption and the affected axis is dropped, never reconstructed from
   memory or staging.
4. **Never mixed with ablation.** Sensitivity material shares no table, figure, section,
   or family with ablation material. Ablation remains X-ABL-01..03,
   DEFERRED_TO_PHASE_12_SUPPLEMENT_ONLY per pre-registration P6; the frozen `pub` profile
   (`phase_03/algorithm_freeze_manifest.json`) is the only configuration appearing in any
   primary exhibit (`comparability_audit.md` §1: no opt-in `ism_profile` candidate appears
   in any panel run_config).
5. **Never converted to component causality.** Prohibited wording: "component X
   contributes/causes/is responsible for …". Permitted wording: "performance varies
   with / is insensitive to parameter θ within the explored range". Any causal-sounding
   sentence about subsystems is out of scope for sensitivity evidence by definition
   (thesis.md Section 7 discipline).
6. **Placement:** supplement only (`T-SENS` destination), never main text.

### 2.3 If no promoted parametric release exists at Phase 7

`T-SENS` carries the unavailable marker and cites EG-006; the limitations section of the
manuscript states that parameter-sensitivity evidence is not part of the evidence release
and that the frozen single configuration (pub profile, zero per-suite tuning) is itself
the robustness posture being claimed (C4 wording via `claims_evidence_matrix.csv`).

---

## 3. Execution and audit requirements (Phase 6 contract)

- Each check R1–R7 is executed by a script under `papers/scripts/` (new scripts allowed;
  named `robustness_r<k>_*.py`), reading exclusively through
  `result_loader.set_strict_source(True)`; the source audit
  (`result_loader.get_source_audit()`) is dumped alongside each output as
  `<check>_source_audit.json`. Any strict-source violation aborts the check.
- Bootstrap or resampling inside any check uses a fixed, recorded seed: 20240620
  (base-seed reuse; recorded per output file).
- Outputs: one CSV + one Markdown digest per check per suite under
  `papers/analysis/rel-2026-07-10-262fc16c9/<suite>/robustness/`, plus the consolidated
  supplement table of Section 4. CSV filenames follow `strict_source_execution.md`
  Sec. 5: `robustness_<suite>_<check-tag>.csv` with the check tags fixed in the
  Section 1.0 crosswalk.
- No check result may be inspected before the corresponding primary analysis is complete
  and its placeholder values bound (protects the primary/robustness ordering).

## 4. Supplement robustness summary table (template)

One row per check × suite (values bound in Phase 6; placeholders shown):

| Check | Suite | Variant compared | Primary conclusion element | Variant outcome | Agree/Diverge | Action taken |
|---|---|---|---|---|---|---|
| R1 | cec2017 | floor 1e-8 vs `<R1:branch>` | `<R1:element>` | `<R1:variant_outcome>` | `<R1:verdict>` | `<R1:action>` |
| R2 | cec2017 | mean vs median ranking | `<R2:element>` | `<R2:variant_outcome>` | `<R2:verdict>` | `<R2:action>` |
| R3 | cec2017 | apgsk V1/V2(/V3) | `<R3:element>` | `<R3:variant_outcome>` | `<R3:verdict>` | `<R3:action>` |
| R4 | all | LOFO Friedman | `<R4:element>` | `<R4:variant_outcome>` | `<R4:verdict>` | `<R4:action>` |
| R5 | all class-A | paired vs unpaired | `<R5:element>` | `<R5:variant_outcome>` | `<R5:verdict>` | `<R5:action>` |
| R6 | all | Holm vs BH (exploratory) | `<R6:element>` | `<R6:variant_outcome>` | n/a (exploratory) | `<R6:action>` |
| R7 | cec2017, cec2013 | block-Friedman vs mean-of-ranks | `<R7:element>` | `<R7:variant_outcome>` | `<R7:verdict>` | `<R7:action>` |

(cec2013 and cec2011 rows expand identically; cec2011 omits R1 and R7 as specified.)

## 5. Citation keys used (all in `papers/governance/allowed_citation_keys.txt`)

`friedman1937use`, `demsar2006statistical`, `wilcoxon1945individual`, `holm1979simple`,
`benjamini1995controlling`, `vargha2000critique`, `efron1993introduction`.
