# Stage 9 — Statistical Validity and Uncertainty Audit

- **Seat:** `s9_statistics` (T3-STAT lead role R4)
- **Date:** 2026-07-22
- **Package audited:** git HEAD `45248eb31`; manuscript freeze anchor `abd2fa2f2`; evidence release `rel-2026-07-20-67d9345f9`; `papers/DT-GSK.pdf` (39 pp), `papers/supplementary.pdf` (61 pp), `papers/DT-GSK.docx`, `papers/supplementary.docx`.
- **Mode:** read-only. No manuscript, code, or evidence file was modified. All recomputation ran from
  `benchmarks/cec_reference_results/` (immutable release) and `papers/analysis/rel-2026-07-20-67d9345f9/`
  into a scratch directory outside the repository.
- **Gate under this stage:** `Gate I — Statistical Validity`.

---

## 0. Headline verdict

**Every headline number in the manuscript reproduces exactly from the immutable release.** I independently
re-derived, from the release summary CSVs and without using any manuscript or table file, all four CEC2017
Friedman mean-rank vectors, the CEC2013 and CEC2011 rank vectors, all 48 across-function Wilcoxon raw
p-values, all win/tie/loss triples, the tie-correction factors, the Nemenyi critical differences, the
global-Holm sensitivity, the class-rank matrix, the robustness-battery counts, the BCa rank intervals, the
ISM-isolation table, and the F26 convergence descriptives. **Zero numerical mismatches.** The recomputation
work is genuinely strong and the loss-visibility discipline (§10.7 "loss-visibility parity") is the best I
have seen in this manuscript family: every unfavorable cell is stated alongside its favorable partner.

**The defects are not in the numbers. They are in the printed specification of the statistics, in the
provenance/attribution of the p-values, and in the post-freeze governance of three analysis changes.**
Four of them would be caught by a competent Q1 statistics referee on a careful read:

1. the printed rank-biserial formula produces the **opposite sign** from the value tabulated, when the
   reader substitutes the `R+`/`R−` the released workbooks actually contain (**CONFIRMED, Major**);
2. the main text advertises an "`A12` effect sizes" **column that does not exist** in Table 14, and quotes
   four `A12` values that are bound to **no artifact** in the controlled analysis area (**CONFIRMED, Major**);
3. the Methods declare the **tie-corrected** Friedman/Iman–Davenport as the reported omnibus, but CEC2017 and
   CEC2013 print the **uncorrected** p-values while CEC2011 prints the **corrected** F and p — mixed sourcing
   inside one paper (**CONFIRMED, Major**);
4. the Methods justify the tie band with a **false property claim** — the across-function Wilcoxon
   signed-rank is *not* invariant to per-function scale, and the tie band *does* change its p-values
   (**CONFIRMED, Major**; I provide explicit counterexamples).

All four are text-and-label corrections. **None requires a rerun, a new evidence release, or any change to
the byte-locked optimizer core.** Findings 5–9 (Moderate) require either a register regeneration or a
scoping edit.

**Gate I disposition: FAIL (remediable without new evidence).** Not because a result is wrong, but because
§10.7 requires "a machine-readable row for every reported statistic", the printed effect-size definition to
be recomputable, and effect-size/interval attachment to headline claims — and those three are unmet.

---

## 1. Scope, method, and what I actually ran

### 1.1 Independent recomputation harness

All recomputation is from first principles against the immutable release, not against the analysis bundle:

- per-function means read from `benchmarks/cec_reference_results/<suite>/<alg>/<alg>_<suite>_D<d>.csv`
  (column `Mean`; CEC2011 from `<alg>_cec2011.csv`, best-fitness basis);
- Friedman ranks by `DataFrame.rank(axis=1, method="average")`, mean over blocks;
- tie correction `C = 1 − Σ_blocks Σ_groups (t³−t) / (N·k·(k²−1))`;
- Iman–Davenport `F = (N−1)χ²/(N(k−1)−χ²)`, `df = (k−1, (k−1)(N−1))`;
- Wilcoxon two-sided, zeros at `|d| < 1e-8` discarded, normal approximation with continuity correction,
  cross-checked against `scipy.stats.wilcoxon(method="approx"|"exact")` and against the in-repo
  `gsk_family.analysis.statistics.wilcoxon_paired`;
- Holm step-down implemented independently;
- A12 across functions as `[#(x<y) + 0.5·#(|x−y|≤1e-8)] / (n·m)` over the 29×29 pairs.

### 1.2 Governing artifacts read

| Artifact | Path | Note |
|---|---|---|
| Frozen SAP | `papers/build_prompt_phases/phase_05/statistical_analysis_plan.md` | **not** at the §10.1-bound path (ticket S9-15) |
| A.7 register | `papers/analysis/rel-2026-07-20-67d9345f9/primary_stats/statistical_results.csv` | 5,098 rows, 60 analysis-id groups |
| Robustness digests | `papers/analysis/rel-2026-07-20-67d9345f9/cec2017/robustness/*_digest.md` | r01–r08 |
| Ablation evidence | `benchmarks/cec_reference_results/_ablation/overlay/analysis/` | `abl-rel-2026-07-20` |
| Amendment registers | `papers/governance/decision_log.md`, `change_request_register.csv` | last entries D-0015 (2026-07-13), CR-0007 |

---

## 2. Statistical design checklist (per §Stage-9 template)

Completed for the three confirmatory analysis layers. `AN-PW-*` is the layer that carries the headline
pairwise claims; `AN-OMNI-*` the panel claims; `AN-EFF-*` / `AN-PWRUN-*` the supplement layer.

| Field | AN-OMNI-2017-D{10,30,50,100} | AN-PW-2017-D{10,30,50,100} | X-ABL-02 (ISM isolation) |
|---|---|---|---|
| research_question | RQ1 panel standing per dimension | RQ2 pairwise reliability | RQ-A2 ISM standalone effect |
| estimand | population mean rank of each algorithm over the task set | median of paired per-function mean-error differences | as AN-PW, over 4 overlay cells |
| endpoint | final error `f−f*`, floor `<1e-8 → 0` (CEC2011: raw best fitness) | same | same |
| observation_unit | one run (`per_run.csv` row) | one run | one run |
| experimental_unit | benchmark function | benchmark function | benchmark function |
| aggregation_before_testing | per-function mean over 51 runs | per-function mean over 51 runs | per-function mean over 51 runs |
| pairing_key | function identity (blocks) | function identity | function identity |
| independence_assumptions | functions independent within a dimension; dimensions never pooled | same | same |
| sample_size_or_task_count | N=29 (CEC2017), 28 (CEC2013), 22 (CEC2011); k=7 | n=29/28/22 paired functions, minus zero-differences | n=29 (CEC2017), 28 (CEC2013); k=4 |
| missing_data_rule | none required (summary CSVs complete) | APGSK D10–D50 run-level marked disclosed-unavailable, never imputed | n/a |
| failure_encoding | no failed runs in release; early stops are complete observations | same | same |
| test | Friedman + Iman–Davenport, tie-corrected | Wilcoxon signed-rank, two-sided | Wilcoxon signed-rank, two-sided |
| one_or_two_sided | two-sided | two-sided | two-sided |
| multiplicity_family | one family per (suite, dimension) | 6 comparators per (suite, dimension) | 3 contrasts per (suite, dimension) |
| correction | none (single omnibus per family) | Holm, m=6 | Holm, m=3 |
| effect_size | mean rank (descriptive) | matched-pairs rank-biserial `r` **(post-freeze substitution — S9-06)** | Friedman Δrank + mean A12 |
| effect_direction | lower rank better | `r > 0` favours DT-GSK **(printed formula gives the opposite sign — S9-01)** | Δrank > 0 = removal hurts |
| uncertainty_interval | descriptive BCa rank-stability (supplement) | **none — `DISCLOSED-UNAVAILABLE` in all 24 register rows (S9-07)** | **none (S9-08)** |
| resampling_unit | per-function midranks (rank CI); paired runs within function (paired-difference BCa) | n/a | n/a |
| RNG_seed | `20260422 + 7·dim + i` (rank CI); `SeedSequence([20240620, suite, dim, func, cmp])` (paired BCa) | n/a | `20240620` unified schedule |
| software_and_version | `statistics.friedman_rank` + `scipy.stats.f` (SciPy 1.15.3) | **`statistics.wilcoxon_paired` (pure NumPy), not `scipy.stats` as the paper states (S9-05)** | same |

---

## 3. Core statistical checks — findings

### 3.1 Estimand and unit of analysis — PASS with one reservation

Unit of analysis is the benchmark function, aggregation is the per-function mean over 51 runs, and run-level
observations never enter an across-function test. Pseudoreplication is correctly avoided and the plan states
the prohibition as binding (SAP §3). Pairing is genuine: seeds are optimizer-independent and audit-verified
(70,813 schedule rows, 0 mismatches), and the one exception (DT-GSK self-init) is disclosed in the protocol
table, the pairing paragraph, and the limitations. Dimensions are never pooled; the "Overall" column is
explicitly labelled a descriptive unweighted mean with no test attached, both in prose
(`performance.tex:325-329`) and in the register (`interpretation = "descriptive aggregation of per-dimension
ranks; no test attached"`). This is exactly what §10.7's "descriptive overall-rank versus pooled test"
disposition requires. **This is done correctly.**

Reservation: the across-function Wilcoxon ranks **absolute differences across functions of incommensurable
scale** (per-function mean errors range from `0` to `>1e4` within one dimension). See S9-04.

### 3.2 Pairing, ties, zeros — PASS on execution, FAIL on printed specification

`n_zero` is recorded per cell in `wilcoxon_holm_*.csv` and in the register `interpretation` field, and
zero-differences are discarded rather than split. I verified the zero counts reproduce
(e.g. CEC2017 D10 vs GSK: 4 zeros, n=25). `p = 0` never appears; `<0.0001` is used per the precision policy.
**But** the printed statement of *which* zero rule is used (`zero_method='wilcox'`, threshold `|Δ|<1e-8`)
describes `scipy` behaviour, whereas the code that produced the numbers drops only *exactly* zero
differences (`np.abs(d) > 0`, `statistics.py:339`). In this release the two coincide because the release
floors sub-`1e-8` values to exact zero (r02 digest: 0 of 71,400 per-run values in the open interval), but
the printed rule is not the executed rule.

### 3.3 Multiplicity — PASS

Holm is the primary correction within explicitly enumerated families of size 6, per (suite, dimension).
Benjamini–Hochberg appears only as a separately labelled exploratory family (`AN-EXP-BH-2017`, 696 rows) and
supports no claim. Raw and adjusted p are distinguished in every table. The 24-cell tally is explicitly
qualified as a descriptive across-dimension tally in **all three** places it appears (Section 4.2.3, Section
4.7, Conclusions) — this closes the classic "17 of 24" over-read and is done well. `AN-GHOLM-2017` supplies
the conservative global-Holm sensitivity (15/24 survive). All of this reproduces exactly.

### 3.4 Effect sizes and intervals — FAIL

- The tabulated effect size is the matched-pairs rank-biserial `r`. Its **printed defining formula is
  sign-inverted** relative to the released operands (S9-01).
- The main text still describes and quotes an **A12 column that no longer exists** (S9-02).
- **No headline pairwise claim carries an uncertainty interval.** All 24 `AN-PW-2017-*` register rows have
  `ci_low = ci_high = NaN` and `interpretation` containing `uncertainty interval DISCLOSED-UNAVAILABLE`
  (S9-07). The paired-difference BCa CIs exist per function in `headline_bca.csv` but are neither typeset nor
  attached to any across-function claim; the SAP's planned `T03`/`T-BCA` supplement tables were dropped.
- The only intervals in the manuscript are the BCa **rank-stability** intervals, which the paper itself
  (correctly and commendably) disclaims as descriptive rather than inferential.

### 3.5 Interpretation of non-significance — PARTIAL FAIL

The supplement is exemplary: *"absent a formal equivalence test, this evidence is consistent with zero rather
than establishing it"* and *"This is a failure to detect an effect under this design, not a demonstration that
none exists"* (`supplementary.tex:2113-2119`). **Neither caveat survives into the abstract or the
conclusions**, which upgrade the same non-result to *"a controlled negative result"* and *"a boundary on the
idea that structure can be learned cheaply"* (S9-08). No power, minimum-detectable-effect, or equivalence
analysis exists anywhere for a claim that appears in the abstract.

### 3.6 Robustness and reversals — PASS

Both diverging checks (r01 mean-vs-median, r04 disputed-cell exclusion) are disclosed in the main text with
their specific reversals, including the reversal that costs the paper something (median endpoint at D=100
makes first place an exact tie with eGSK). §10.7's "robustness-divergence disclosure" requirement is met. The
r05 counts (11 sig→n.s., 21 n.s.→sig) reproduce exactly from the digest. Minor issues at S9-11 and S9-13.

### 3.7 RNG, seeding, reproducibility of intervals — PASS

Two bootstrap seed constructions exist, but they are **pre-registered as distinct** in SAP §7 (paired-difference
BCa: `SeedSequence([20240620, suite, dim, func, cmp_index])`, B=10,000; rank-stability CI: `20260422 + 7·dim + i`,
n_boot=10,000). Both appear in the artifacts as declared, and the rank-CI seed is disclosed in the supplement
caption. This satisfies §10.7's "deterministic interval seeding" disposition — it is **not** the "two
contradictory seed constructions" defect that disposition targets.

---

## 4. Ticket register (§5.4 schema)

### S9-01 — Printed rank-biserial formula yields the opposite sign from the released workbook operands

```text
ticket_id: S9-01
review_stage: Stage 9 (Statistical validity)
reviewer_role: R4 / T3-STAT
severity: Major
priority: P1
confidence: Confirmed
issue_type: statistics
manuscript_location: papers/sections/performance.tex:212-213 and 228-231; rendered PDF p.26 (Statistical protocol);
  papers/tables/T15.tex (column r); papers/tables/T06.tex; papers/tables/T14.tex; DT-GSK.docx (same prose);
  papers/analysis/rel-2026-07-20-67d9345f9/primary_stats/statistical_results.csv (interpretation field, all AN-PW rows)
claim_id_or_artifact_id: RS-08 / TAB-T15 / TAB-T14 / TAB-T06 / AN-PW-2017-*, AN-PW-2013-*, AN-PW-2011-NATIVE
concise_issue: The manuscript prints r = (R+ - R-)/(R+ + R-) with "r > 0 favours DT-GSK", but the R+/R-
  carried by the released per-comparison workbooks are the reverse of the paper's labels, so a reader who
  substitutes them into the printed formula obtains the negated effect size for every cell. The released
  A.7 register states the formula and its operands in the same field and is self-contradictory.
exact_evidence_or_observation:
  papers/analysis/.../cec2017/wilcoxon_holm_cec2017_D10.csv, gsk row:
    w_plus=2.200000e+01, w_minus=3.030000e+02, rank_biserial=+8.646154e-01
    (22 - 303)/(22 + 303) = -0.8646, but the file and Table 14 both print +0.865.
  statistical_results.csv row AN-PW-2017-D10 (gsk), interpretation field, verbatim:
    "effect=matched-pairs rank-biserial r=(R+ - R-)/(R+ + R-) from w_plus=22.0,w_minus=303.0"
    with effect_size = 0.864615. The stated formula on the stated operands gives -0.864615.
  Direction of the underlying difference confirmed by independent recomputation: with d = mean(DT-GSK) -
    mean(comparator), sum of positive-difference ranks = 22 and negative = 303 at CEC2017 D10 vs GSK
    (DT-GSK better, W/T/L 22-4-3), i.e. w_plus is the DT-GSK-*worse* rank sum.
  The manuscript's own tables use the opposite labelling: T14 prints "R+ = 340, R- = 11" for CEC2013 D10 vs
    GSK where the released CSV has w_plus=11, w_minus=340; T06 prints "R+ 159 / R- 51" where the CEC2011 CSV
    has w_plus=51, w_minus=159.
root_cause: M-027 introduced rank_biserial with a sign chosen so that positive favours DT-GSK, but the
  emitted w_plus/w_minus columns kept the standard "positive difference" definition, and the formula string
  was copied into both the prose and the register without reconciling the two conventions. The manuscript
  never states the direction of the difference d, so R+ is undefined for the reader.
scientific_or_editorial_justification: An effect-size definition must be recomputable from the artifacts the
  paper points to. §10.6/§10.7 require the printed rule to be recomputed symbolically from the frozen source
  before acceptance; here the printed rule fails that test on the paper's own released operands.
impact_on_validity_or_acceptance: No reported value changes sign or magnitude, and every direction label
  ("+", "=", favours_dt-gsk) is correct. The defect is in the printed specification: a referee or reader
  reproducing the effect size gets -0.865 where the paper prints +0.865, which reads as a sign error in the
  authors' analysis. High probability of a reviewer comment; low probability of it surviving to print unnoticed.
required_correction: (a) Define the differencing direction explicitly in the Statistical protocol paragraph
  (e.g. "with d_i = e_i(comparator) - e_i(DT-GSK), so R+ is the rank sum of the functions on which DT-GSK is
  better"); OR print r = (R- - R+)/(R+ + R-) with the standard d = DT-GSK - comparator convention.
  (b) Make the released workbook column names match the paper's labels, or add a one-line header note in
  wilcoxon_holm_*.csv and in the register interpretation string stating that w_plus is the DT-GSK-worse rank
  sum. (c) Correct the interpretation string in statistical_results.csv so the printed formula and the printed
  operands are consistent.
acceptable_alternatives: Rename the workbook columns to w_dtgsk_better / w_dtgsk_worse and cite those names
  in the paper; this removes the ambiguity without touching any value.
additional_evidence_needed: none
dependencies: none (text + register-string change; regeneration of statistical_results.csv only if the
  interpretation string is fixed in-place rather than by an erratum note)
expected_improvement: the tabulated effect size becomes recomputable from the released artifacts.
post_revision_verification: For all 48 pairwise cells, assert
  sign(printed r) == sign(printed formula evaluated on the released w_plus/w_minus) and
  |printed r| == |(w_plus - w_minus)/(w_plus + w_minus)| to 1e-9.
status: open
```

### S9-02 — Main text describes and quotes an A12 column that Table 14 does not contain, and the quoted A12 values are bound to no released artifact

```text
ticket_id: S9-02
review_stage: Stage 9
reviewer_role: R4 / T3-STAT
severity: Major
priority: P1
confidence: Confirmed
issue_type: statistics / evidence
manuscript_location: papers/sections/performance.tex:361-373 and 405-426; rendered DT-GSK.pdf p.27
  (Section 4.2.3, both paragraphs surrounding Table 14); DT-GSK.docx carries the identical prose
claim_id_or_artifact_id: TAB-T15 / RS-08 / AN-PW-2017-*
concise_issue: The paragraph introducing Table 14 says the table reports "A12 effect sizes" and devotes two
  sentences to how "The A12 column" should be read; Table 14 has no A12 column (its effect-size column is r,
  the matched-pairs rank-biserial). The following paragraph then quotes four A12 values as if readable from
  the table. Those four values exist in no CSV under papers/analysis/rel-2026-07-20-67d9345f9/.
exact_evidence_or_observation:
  Rendered PDF, p.27: "Table 14 reports the across-function Wilcoxon tests with Holm correction, win/tie/loss
    counts, A12 effect sizes, and Holm decisions ... The A12 column is computed over the 29 per-function
    means, on the same unit as the Wilcoxon test ..."
  Rendered Table 14 header (same page): "p  pHolm  +  ≈  −  r  Dec." — no A12 column.
  Table 14 caption (same page): "... the matched-pairs rank-biserial effect size r (> 0 favors DT-GSK) ..."
  Rendered PDF, p.27: "with A12 of 0.490, 0.505, and 0.472" and "the largest effect is against APGSK at
    D = 100 (A12 = 0.712)".
  I recomputed these across-function A12 values independently and they are numerically correct
    (eGSK D30/D50/D100 = 0.4905 / 0.5054 / 0.4721; APGSK D100 = 0.7122), but a scan of every CSV under
    papers/analysis/rel-2026-07-20-67d9345f9/ finds a12 columns only in effect_sizes_*.csv, which hold the
    RUN-LEVEL per-function A12 (n_runs = 51) — a different statistic. The strings "0.712", "0.4905",
    "0.5054", "0.4721" appear in no file in the controlled analysis area.
  DOCX check: 'A12 effect sizes' present, 'A12 column is computed' present, 'matched-pairs rank-biserial'
    present — the same contradiction ships in Word.
root_cause: M-027 replaced the A12 column in T15 with r and dropped the across-function A12 from the emitted
  CSVs, but the two surrounding prose paragraphs (which were written for the pre-M-027 table) were not updated.
scientific_or_editorial_justification: §10.11 forbids reader-facing numbers that are not bound to an
  authoritative analysis output; §10.7 requires a machine-readable row for every reported statistic. A quoted
  effect size that is neither in the table it is attributed to nor in the release is unverifiable at the
  reader's end.
impact_on_validity_or_acceptance: The quoted values are correct, so no conclusion is wrong. But the reader is
  told to look at a column that is not there, and the numbers cited for the paper's most delicate cells (the
  three non-significant DT-GSK-vs-eGSK comparisons) cannot be located in the shipped evidence. This is a
  camera-ready credibility failure of the kind §5.5 calibrates as Major.
required_correction: Either (a) restore an across-function A12 column to Table 14 and emit it into
  wilcoxon_holm_*.csv + statistical_results.csv, or (b) rewrite both paragraphs to describe the r column, and
  either drop the A12 sentences or re-express the eGSK and APGSK statements in terms of r
  (r = -0.286, -0.002, -0.057 for eGSK at D30/50/100; r = +0.977 for APGSK at D100, the largest in the table).
  Option (b) is the cleaner fix and is consistent with the caption already shipped.
acceptable_alternatives: Keep the A12 sentences but move them to a footnote that states the values are
  derived quantities computed from the released per-function means, and add the four values to the register.
additional_evidence_needed: none
dependencies: coupled to S9-01 (same paragraph) and S9-06 (M-027 provenance)
expected_improvement: table and prose describe the same statistic; every quoted effect size is locatable.
post_revision_verification: grep the rendered PDF and DOCX for "A12" and confirm every occurrence in Section
  4.2.3 either names a column that exists in the rendered table or cites a released artifact by name.
status: open
```

### S9-03 — Reported omnibus p-values mix tie-corrected and uncorrected sources across suites, contradicting the Methods

```text
ticket_id: S9-03
review_stage: Stage 9
reviewer_role: R4 / T3-STAT
severity: Major
priority: P1
confidence: Confirmed
issue_type: statistics
manuscript_location: papers/sections/performance.tex:316-317 (CEC2017 "p <= 2.6e-8"), :338 (Table 13 caption),
  :529-531 (CEC2011 "F = 4.27, p = 6.0e-4"), :599 (Table 15 caption "p <= 2.3e-3"),
  :621-626 (CEC2013 per-dimension 3.3e-7 / 2.2e-3 / 9.2e-6); declaring sentence at :250-262
claim_id_or_artifact_id: AN-OMNI-2017-D10..D100, AN-OMNI-2013-D10..D50, AN-OMNI-2011-NATIVE
concise_issue: The Statistical protocol paragraph states "the Friedman statistic uses the tie-corrected rank
  variance that underlies the Iman-Davenport F". The CEC2011 omnibus is indeed quoted from the corrected
  columns; the CEC2017 and CEC2013 omnibus p-values are quoted from the *uncorrected* columns. One paper,
  two sources, with the Methods naming only one of them.
exact_evidence_or_observation:
  papers/analysis/.../cec2017/friedman_ranks_cec2017_D10.csv:
    p_value (corrected)      = 1.159690e-09   iman_davenport_F      = 10.25319
    p_value_uncorrected      = 2.576884e-08   ..._F_uncorrected     =  8.769128
    tie_correction_C = 0.889778, n_tied_functions = 9
  My independent recomputation reproduces both to 6 s.f. The manuscript's bound "p <= 2.6e-8" is the maximum
    of the four UNCORRECTED Iman-Davenport p-values (max = 2.577e-8 at D10). The corrected bound would be
    "p <= 1.2e-9".
  papers/analysis/.../cec2013/friedman_ranks_cec2013_D30.csv: p_value = 1.089721e-03 (corrected),
    p_value_uncorrected = 2.242258e-03. The manuscript prints "omnibus p = 2.2e-3" and the caption bound
    "p <= 2.3e-3" — both uncorrected. D10: prints 3.3e-7 (uncorrected 3.264e-7; corrected 5.322e-8).
    D50: prints 9.2e-6 (uncorrected 9.212e-6; corrected 2.909e-6).
  papers/analysis/.../cec2011/friedman_ranks_cec2011.csv: iman_davenport_F = 4.266899 (corrected;
    uncorrected 3.668834), p_value = 6.007858e-04 (uncorrected 2.160258e-03). The manuscript prints
    "F = 4.27, p = 6.0e-4" — CORRECTED.
  The A.7 register agrees with the corrected columns throughout (AN-OMNI-2017-D10 iman_davenport_F =
    10.253190, p_raw = 1.159690e-09), so the register and the manuscript disagree on CEC2017 and CEC2013.
root_cause: M-026 added the corrected columns and made them the register's primary, but the manuscript's
  CEC2017/CEC2013 omnibus sentences were written against the pre-M-026 (uncorrected) values and were not
  re-derived; CEC2011's sentence happened to be regenerated.
scientific_or_editorial_justification: §10.7 requires the frozen plan's omnibus decision criterion to be
  identified and the reported statistic to match it; the paper further makes the tie correction a
  methodological talking point ("The correction is material ..."), which makes quoting the uncorrected value
  in the same section self-refuting.
impact_on_validity_or_acceptance: No decision changes - all p are far below 0.05 under either form, and the
  paper's own sentence "every omnibus decision, rank, and effect direction reported here is identical under
  the corrected and uncorrected forms" is true. But the *reported statistic* is not the declared one, on two
  of three suites, and a referee who opens friedman_ranks_*.csv will see the mismatch immediately.
required_correction: Re-derive the CEC2017 and CEC2013 omnibus p bounds and per-dimension values from the
  `p_value` (corrected) column: CEC2017 becomes "p <= 1.2e-9"; CEC2013 becomes D10 5.3e-8, D30 1.1e-3,
  D50 2.9e-6, caption bound "p <= 1.1e-3". Alternatively, state explicitly in each location which form is
  quoted and why, and make that choice uniform across the three suites.
acceptable_alternatives: Report both forms in the Table 13/15 captions (the CSVs already carry both), as the
  paper already promises ("Both are released per panel ... so the correction can be checked directly").
additional_evidence_needed: none
dependencies: none (values already exist in the release)
expected_improvement: reported omnibus statistics match the declared method and the A.7 register.
post_revision_verification: For each of the 8 omnibus families, assert the printed p equals
  friedman_ranks_*.csv `p_value` (or `p_value_uncorrected`, if that is the declared choice) at the printed
  precision, with the same column used in all 8.
status: open
```

### S9-04 — The Methods justify the tie band with a false invariance property of the Wilcoxon signed-rank

```text
ticket_id: S9-04
review_stage: Stage 9
reviewer_role: R4 / T3-STAT
severity: Major
priority: P1
confidence: Confirmed
issue_type: statistics / method
manuscript_location: papers/sections/performance.tex:203-209 (Statistical protocol); rendered DT-GSK.pdf p.26.
  Stronger restatement in papers/supplementary.tex:1288-1292 (S5 tie-band sensitivity):
  "Every Holm decision, every Friedman rank, and every reported significance is computed from the tests
  themselves and is unaffected by the tie band, which enters only the descriptive counts."
claim_id_or_artifact_id: AN-PW-2017-*, AN-PW-2013-*, AN-PW-2011-NATIVE; AN-ROB-2017-02
concise_issue: The paper claims "the inferential Wilcoxon and Friedman tests are rank-based and hence
  invariant to per-function scale, so the band affects no significance decision." The Friedman test is
  scale-invariant (it ranks within blocks). The across-function Wilcoxon signed-rank is NOT: it ranks the
  ABSOLUTE DIFFERENCES ACROSS functions, so a pure change of one function's units changes its rank, the
  statistic, and the p-value. Separately, the tie band is the zero threshold of that same test, so it
  demonstrably changes n and p.
exact_evidence_or_observation:
  Scale-dependence, from the frozen per-function means (my recomputation, no reruns):
    CEC2017 D100 vs GSK   : p = 0.032298 -> 0.076212 after multiplying ONE function's errors by 1e6
                                        -> 0.044330 after multiplying a different function's errors by 1e-3
    CEC2017 D30  vs GSK   : p = 0.014747 -> 0.020427 / 0.015756 under the same two rescalings
    CEC2017 D50  vs ATMALS: p = 1.187e-4 -> 1.255e-5 after one function is rescaled by 1e-3
    (Rescaling a single function's objective by a constant is exactly the "different scales" concern the
     sentence is dismissing; note the D100-vs-GSK case crosses the raw 0.05 boundary.)
  Tie-band dependence, recomputing the same tests at floor 1e-6 instead of 1e-8:
    D10 vs GSK   : n 25->24, p 1.6524e-4 -> 1.9257e-4
    D10 vs ATMALS: n 25->24, p 9.0550e-3 -> 1.1453e-2
    D10 vs eGSK  : n 25->24, p 6.9824e-4 -> 7.8752e-4
    D30 vs eGSK  : n 27->26, p 0.198674  -> 0.195219
    D50 vs eGSK  : n 29->28, p 1.000000  -> 0.990920
    D50 vs ATMALS: n 29->28, p 1.1863e-4 -> 1.4978e-4
  (I confirmed no Holm DECISION flips at 1e-6, so the paper's operative conclusion survives; the stated
   REASON does not.)
root_cause: A correct property of the Friedman test was over-generalised to the Wilcoxon signed-rank, and the
  tie band's dual role (descriptive W/T/L threshold AND inferential zero threshold) was not separated.
scientific_or_editorial_justification: §4.6 requires rejecting language that overstates what a method
  guarantees; the sentence is used to retire a genuine limitation (cross-function commensurability of the
  signed-rank) rather than to disclose it. Demsar's own treatment flags commensurability as the standing
  caveat of the across-dataset Wilcoxon.
impact_on_validity_or_acceptance: No reported decision changes. But this is the single sentence a statistics
  referee is most likely to challenge, and it currently asserts a property the paper's own data refute. It
  also sits one paragraph above the sentence that (correctly) makes a point of tie correction, so the section
  reads as inattentive to exactly the issue it is claiming to have handled.
required_correction: Replace with an accurate two-part statement, e.g.: "The Friedman test ranks within
  functions and is therefore invariant to per-function scale. The across-function Wilcoxon ranks absolute
  differences across functions and is not scale-free; we retain it as the family convention and report the
  tie band's effect explicitly. Recomputing every across-function test at a 1e-6 floor changes individual
  p-values by at most X but leaves all 48 Holm decisions unchanged." Then correct the supplement sentence in
  the same way (the band enters the test through the zero rule, not only the descriptive counts), and add the
  1e-6 recomputation to the robustness digest so the claim is evidenced rather than asserted.
acceptable_alternatives: Add a sign-test or a per-function-standardised companion (e.g. the log10 endpoint
  already computed in the post-hoc section) as the scale-free check, and cite it here.
additional_evidence_needed: none (the recomputation is read-only from the frozen means; I have already run it)
dependencies: touches AN-ROB-2017-02, see S9-11
expected_improvement: the Methods state a property the evidence supports, and the commensurability caveat is
  disclosed instead of dismissed.
post_revision_verification: Confirm the revised sentence is consistent with a re-executed floor-sensitivity
  check reporting per-cell p at 1e-8 and 1e-6 and the count of decision changes (currently 0/48).
status: open
```

### S9-05 — Wilcoxon p-values are attributed to `scipy.stats` but produced by a bespoke pure-NumPy routine that disagrees with SciPy at the reported precision

```text
ticket_id: S9-05
review_stage: Stage 9
reviewer_role: R4 / T3-STAT
severity: Moderate
priority: P2
confidence: Confirmed
issue_type: reproducibility / statistics
manuscript_location: papers/sections/performance.tex:216-219 ("the reported p-values use the normal
  approximation with continuity correction (\texttt{scipy.stats})") and :250-253 ("Tests are computed with
  \texttt{scipy.stats} (SciPy 1.15.3); ... with \texttt{scipy.stats} supplying the F-distribution tail and
  the Wilcoxon and Nemenyi terms")
claim_id_or_artifact_id: AN-PW-2017-*, AN-PW-2013-*, AN-PW-2011-NATIVE, AN-PWRUN-*
concise_issue: The released Wilcoxon p-values are produced by src/gsk_family/analysis/statistics.py::
  wilcoxon_paired, a hand-written pure-NumPy implementation with its own rational-polynomial erf, not by
  scipy.stats.wilcoxon. Its outputs differ from SciPy's at the paper's declared 4-significant-figure
  reporting precision in at least 8 of the 24 CEC2017 cells.
exact_evidence_or_observation:
  src/gsk_family/analysis/statistics.py:304-397. Zeros dropped by `np.abs(d) > 0`; p from
    z = (W - n(n+1)/4 + 0.5) / sqrt(n(n+1)(2n+1)/24) with a local `_norm_cdf`/`_erf` approximation;
    no tie correction of the variance.
  Released p_raw == wilcoxon_paired output to full precision (24/24 cells). Comparison to
    scipy.stats.wilcoxon(zero_method='wilcox', correction=True, method='approx'), 4 s.f.:
      D10  gsk      released 1.653e-4  scipy 1.652e-4
      D10  eGSK     released 6.983e-4  scipy 6.982e-4
      D30  FDB-AGSK released 8.500e-4  scipy 8.499e-4
      D50  APGSK    released 5.775e-5  scipy 5.773e-5
      D50  ATMALS   released 1.187e-4  scipy 1.186e-4
      D100 AGSK     released 1.256e-5  scipy 1.255e-5
      D100 APGSK    released 4.564e-6  scipy 4.559e-6
      D100 FDB-AGSK released 2.255e-5  scipy 2.254e-5
  The gap is the erf approximation, not tie handling: I verified there are no ties among the non-zero |d| in
    any across-function cell, so SciPy's tie correction is a no-op here.
  Secondary defect in the same function: its docstring states "Uses the exact distribution for n <= 25 and
    normal approximation for n > 25". The code never computes an exact distribution. Cells with n <= 25
    exist (CEC2011: n = 20 for all six comparators; CEC2017 D10: n = 25 for four comparators).
  Frozen plan deviation: SAP Section 6a pre-registers "exact distribution where implementation permits, else
    normal approximation with tie correction". SciPy 1.15.3 permits the exact distribution at n = 20-29, and
    the approximation actually used is not tie-corrected. The A.7 register DOES record the executed method
    ("method=normal_approx_continuity(statistics.wilcoxon_paired)"), which satisfies the plan's recording
    requirement; the manuscript's attribution does not match it.
  Decision-relevance check (performed): recomputing all 48 across-function tests with
    scipy.stats.wilcoxon(method='exact') and re-running Holm changes ZERO decisions on CEC2017 (all four
    dimensions), CEC2013 (all three) and CEC2011. Closest margins: CEC2011 vs eGSK p_Holm 0.0424 -> 0.0320
    exact; CEC2011 vs FDB-AGSK 0.0424 -> 0.0320; CEC2017 D10 vs ATMALS 0.0362 -> 0.0295. All stay significant.
root_cause: The analysis pipeline uses an in-repo statistics module written to avoid a SciPy dependency; the
  Methods paragraph names the package that supplies the Friedman F tail and the Nemenyi q, and generalised it.
scientific_or_editorial_justification: Software-and-version is a mandatory register field (Appendix A.7) and
  a reproducibility claim. A reader following the stated method will not reproduce the released p at the
  stated precision.
impact_on_validity_or_acceptance: No decision, rank, direction or table entry changes. It is a provenance and
  reproducibility-statement defect, and the docstring/implementation mismatch is a latent trap for anyone
  reusing the module (it silently uses the normal approximation at n = 20, where the exact test is
  materially more accurate).
required_correction: (a) State in the Methods that the paired Wilcoxon p-values are computed by the released
  analysis package's own normal-approximation implementation, naming the module, and that SciPy supplies the
  Friedman F tail and Nemenyi q. (b) Fix the wilcoxon_paired docstring to describe what the code does.
  (c) Recommended, and cheap: report the exact-distribution p as a companion (n <= 29 everywhere) or state in
  the robustness paragraph that the exact test leaves all 48 Holm decisions unchanged - this converts a
  latent objection into a strength and closes the SAP Section 6a "exact where implementation permits" branch.
acceptable_alternatives: Regenerate the pairwise layer with scipy.stats.wilcoxon and reissue the affected
  CSVs; not recommended, since it would require a new analysis bundle for no inferential gain.
additional_evidence_needed: none
dependencies: (c) would extend the supplement's post-hoc robustness subsection, which already covers the
  CEC2017 sign-flip randomisation but NOT CEC2011 or CEC2013 (see S9-08 note)
expected_improvement: the stated software provenance matches the artifacts; the approximation choice is
  evidenced as decision-irrelevant on all three suites rather than only CEC2017.
post_revision_verification: Assert that the Methods name the module that produced each reported p, and that a
  script re-deriving p from the named module reproduces every released p_raw bit-for-bit.
status: open
```

### S9-06 — Three post-freeze statistical changes are unlogged in the SAP's designated amendment register, and one introduces an analysis family with no registry ID

```text
ticket_id: S9-06
review_stage: Stage 9
reviewer_role: R4 / T3-STAT
severity: Moderate
priority: P2
confidence: Confirmed
issue_type: statistics / reproducibility
manuscript_location: papers/sections/performance.tex:250-262 (tie-corrected Friedman as the reported method),
  :210-231 (rank-biserial as the tabulated effect size), :398-404 (global-Holm sensitivity);
  governance: papers/governance/decision_log.md (last entry D-0015, 2026-07-13),
  papers/governance/change_request_register.csv (last row CR-0007)
claim_id_or_artifact_id: AN-OMNI-2017-*, AN-PW-*, AN-GHOLM-2017
concise_issue: M-026 (tie-corrected Friedman becomes the reported omnibus), M-027 (rank-biserial replaces A12
  as the tabulated effect size for ALL cells) and M-028 (new global-Holm family AN-GHOLM-2017) were made on
  2026-07-18, after every affected outcome had been inspected. SAP Section 13 requires either a logged
  confirmatory amendment in papers/governance/decision_log.md with an explicit outcome-blindness statement,
  or demotion of the affected analyses to exploratory. Neither is present in the designated register, and
  AN-GHOLM-2017 has no Section 12 family ID, which SAP Section 13.3 itself calls a governance defect.
exact_evidence_or_observation:
  papers/governance/decision_log.md: last section header is "## D-0015 (2026-07-13)". No entry mentions
    M-026, M-027, M-028 or AN-GHOLM. A scan of every .md/.csv directly under papers/governance/ for the
    strings "M-026", "M-027", "M-028", "AN-GHOLM" returns no hit outside the remediation subfolder.
  The changes ARE documented, but only in papers/governance/remediation_2026_07_18/change_log.md:32-56 and
    decisions.md:19 - a folder the frozen plan does not name as the amendment register.
  papers/analysis/.../primary_stats/statistical_results.csv contains 24 rows with analysis_id
    "AN-GHOLM-2017" and 1 row "EG-006-T-SENS"; neither ID appears in SAP Section 12's registry table.
    (EG-006-T-SENS is a disclosed evidence-gap row and is benign; AN-GHOLM-2017 is a live analysis.)
  SAP Section 7 pre-registers A12 + Cliff's delta at RUN level within each function as the effect-size
    measures, with matched-pairs rank-biserial named ONLY as the fallback for the APGSK CEC2017 D10-D50 cells
    where per-run data was absent. The shipped Table 14 uses rank-biserial for all 24 cells.
  The manuscript labels the global-Holm analysis "As a sensitivity check", not "exploratory" or "post-hoc".
    (By contrast, the supplement's two genuinely post-hoc checks ARE labelled: "This subsection reports two
    post-hoc sensitivity checks - not part of the prespecified analysis plan", supplementary.tex:513-515.
    The same discipline was simply not applied to M-026/027/028.)
root_cause: The 2026-07-18 remediation created its own change log and did not back-propagate entries into the
  frozen plan's named register.
scientific_or_editorial_justification: The project's own frozen plan is the control that makes its
  confirmatory claims confirmatory. An unlogged post-outcome change to the reported omnibus statistic and to
  the primary tabulated effect size is precisely what Section 13 exists to catch.
impact_on_validity_or_acceptance: All three changes move in the conservative/corrective direction - the tie
  correction can only increase the statistic, the rank-biserial replaces an unpaired effect size with the
  aligned paired one, and the global Holm is strictly more conservative - so there is no outcome-shopping
  here and I do not allege any. The defect is procedural but material to the reproducibility narrative, and a
  referee who reads the SAP will ask why the plan's Section 12 registry does not contain a family the paper
  reports.
required_correction: (a) Add a dated decision_log.md entry (D-0016) recording M-026/M-027/M-028 with
  motivation, affected family IDs, the outcome-inspection status, and the explicit statement that no
  affected decision, rank or direction changed (which I have independently verified to be true).
  (b) Register AN-GHOLM-2017 as an amendment-added family with its definition (Holm across all 24 CEC2017
  pairwise hypotheses, m = 24), or relabel it "post-hoc sensitivity, not pre-registered" in the manuscript
  sentence at performance.tex:398.
  (c) Record in the same entry that the reported effect size for the primary pairwise table changed from the
  Section 7 measure to the rank-biserial, and why.
acceptable_alternatives: If outcome-blindness cannot be demonstrated (it cannot, for changes prompted by a
  review of the results), label the three analyses "confirmatory in method, adopted post-hoc" and state that
  every pre-freeze decision is unchanged - which is verifiable and true.
additional_evidence_needed: author statement of the inspection sequence for the decision_log entry
dependencies: S9-03 (which corrected/uncorrected form is reported) resolves alongside (a)
expected_improvement: the frozen plan and the shipped analysis describe the same set of families.
post_revision_verification: Re-run the Phase 6 orphan check - assert every analysis_id in
  statistical_results.csv resolves to a SAP Section 12 row or a dated amendment-log entry.
status: open
```

### S9-07 — No uncertainty interval is attached to any headline pairwise inference

```text
ticket_id: S9-07
review_stage: Stage 9
reviewer_role: R4 / T3-STAT
severity: Moderate
priority: P2
confidence: Confirmed
issue_type: statistics
manuscript_location: papers/tables/T15.tex (Table 14, 24 cells), T14.tex, T06.tex; register rows
  AN-PW-2017-D10/D30/D50/D100, AN-PW-2013-*, AN-PW-2011-NATIVE
claim_id_or_artifact_id: RS-08 / RS-09 / T03 / T-BCA
concise_issue: SAP Section 7 states as binding that "every planned significance claim and every headline
  comparative claim carries at least one effect size AND one uncertainty interval". All 48 across-function
  pairwise rows carry an effect size and no interval; the register marks the interval DISCLOSED-UNAVAILABLE
  for every one of them, and the planned T03 / T-BCA supplement tables were not typeset.
exact_evidence_or_observation:
  statistical_results.csv, all AN-PW-2017-* rows: ci_low = ci_high = NaN, ci_level empty, interpretation
    contains "uncertainty interval DISCLOSED-UNAVAILABLE" (24/24 cells; same for AN-PW-2013-* and
    AN-PW-2011-NATIVE).
  papers/sections/performance.tex:264-267: "The complete per-comparison workbooks ... are released with the
    reproducibility bundle (they accompany the analysis scripts and are not typeset in the supplement)."
  The shipped supplement (S1-S6) contains no T03 (run-level A12/Cliff) and no T-BCA (per-function paired
    BCa) table; the only intervals in either document are the BCa rank-stability intervals of Table A9,
    which the paper itself labels descriptive and not inferential.
  The data to close this exist: headline_bca.csv holds seeded B=10,000 BCa CIs on paired mean differences
    per (dim, function, comparator), and a bootstrap CI on the 29 paired function-level differences (or on
    the rank-biserial r) is directly computable from the same frozen means with no rerun.
root_cause: The interval was pre-registered at the per-function level (paired runs within a function) while
  the headline test is at the across-function level; no across-function interval was ever defined, and the
  planned per-function interval tables were dropped for page reasons.
scientific_or_editorial_justification: Section 9 requires confidence intervals attached to headline effects;
  Section 4.6 forbids suppressing uncertainty. "DISCLOSED-UNAVAILABLE" is the plan's term for data that does
  not exist - it is being used here for a quantity that is computable.
impact_on_validity_or_acceptance: The paper's inference is p-value-and-effect-size only at its headline
  level. For the delicate cells (eGSK at D30/50/100, GSK at D100) an interval would materially help the
  paper's own "not separable" framing; its absence invites the standard referee request.
required_correction: Add a bootstrap CI on the across-function effect (either on the matched-pairs r or on
  the median paired per-function difference), seeded with the already pre-registered entropy-list scheme,
  as an extra column of Table 14 or as a supplement table; and change the register's
  DISCLOSED-UNAVAILABLE string to the computed interval.
acceptable_alternatives: If no new column is wanted, typeset T-BCA (already generated) in the supplement and
  point Table 14 at it, and state explicitly in the Methods that the headline interval is at the
  per-function level.
additional_evidence_needed: none - read-only recomputation from the frozen per-function means
dependencies: S9-06 (any added analysis needs an amendment-log entry)
expected_improvement: closes the plan's binding attachment rule and removes a predictable referee request.
post_revision_verification: Assert every headline comparative claim resolves to a register row with non-null
  ci_low/ci_high/ci_level, or to an explicitly justified exemption.
status: open
```

### S9-08 — The abstract-level ISM null carries no interval, no equivalence test and no power statement, and the supplement's own caveat does not survive into the abstract or conclusions

```text
ticket_id: S9-08
review_stage: Stage 9
reviewer_role: R4 / T3-STAT
severity: Moderate
priority: P2
confidence: Confirmed
issue_type: statistics / claim-scope
manuscript_location: papers/main.tex:147-150 (abstract: "A direct isolation finds no detectable standalone
  benefit from the interaction-structure memory---a controlled negative result");
  papers/sections/conclusions.tex (Component-level evidence paragraph: "a boundary on the idea that structure
  can be learned cheaply"); supplement papers/supplementary.tex:1978-2062 (S6.5) and 2110-2122 (S6.6)
claim_id_or_artifact_id: X-ABL-02 / AN-ABL-SGSM-OVERLAY / AB-02
concise_issue: A non-significant result is promoted to a named finding in the abstract and conclusions
  ("controlled negative result", "a boundary on the idea") on the strength of three non-significant Holm
  p-values and three point A12 values, with no confidence interval on any of them, no equivalence or
  non-inferiority test, and no minimum-detectable-effect / power statement. The supplement's correct caveats
  are not carried up.
exact_evidence_or_observation:
  Supporting evidence in full (verified to reproduce exactly from
  benchmarks/cec_reference_results/_ablation/overlay/analysis/):
    CEC2017 D50 : Delta-rank +0.0517, Holm p 0.98270, mean A12 0.5065
    CEC2017 D100: Delta-rank +0.1552, Holm p 0.89677, mean A12 0.5031
    CEC2013 D50 : Delta-rank +0.1964, Holm p 0.64737, mean A12 0.4190
  No CI, SE, or interval accompanies any of these nine numbers in ism_isolation_effects_*.csv, in the
    overlay_contrasts_*.json, in the supplement table, or in the A.7 register (which has no rows for this
    family at all - see S9-09).
  The supplement DOES state the correct interpretation, at supplementary.tex:2113-2119: "though, absent a
    formal equivalence test, this evidence is consistent with zero rather than establishing it" and "This is
    a failure to detect an effect under this design, not a demonstration that none exists."
  Neither sentence, nor any equivalent, appears in the abstract or the conclusions.
  The conclusions' Limitations paragraph does carry a related caveat ("the standalone null is therefore 'no
    detectable benefit under this design' and not a demonstration that the memory was active and neutral"),
    but it is in the supplement's Limitations-in-full (S5), not in the main-text conclusions paragraph that
    states the finding.
root_cause: The narrowing of Section 10.9 permits the null to be advertised; the statistical qualification
  that must travel with it was left in the supplement.
scientific_or_editorial_justification: Section 4.6 forbids treating failure to reject as proof of
  equivalence; Section 9 requires power/precision/practical-detectability discussion. The narrowing at
  Section 10.9 permits disclosing the null - it does not relax the requirement to state it at the strength
  the evidence supports.
impact_on_validity_or_acceptance: The abstract wording ("no detectable standalone benefit") is defensible;
  "a controlled negative result" and "a boundary on the idea that structure can be learned cheaply" are not,
  without an interval or an equivalence margin. This is the one place in the paper where a non-significant
  result carries claim weight, so it is the one place a referee will demand the power analysis.
required_correction: (a) Attach an interval to the ISM contrast - a seeded bootstrap CI on the mean A12 or on
  the paired rank-biserial across the 29/28 functions is computable read-only from
  overlay_per_function_means_*.csv, no rerun. (b) State the minimum effect the design could have detected
  (n = 29 paired functions, Holm m = 3, alpha = 0.05, two-sided). (c) Carry one clause of the supplement's
  caveat into the conclusions sentence, e.g. "...a failure to detect a standalone benefit under this design
  at D <= 100, not a demonstration that none exists."
acceptable_alternatives: Soften "controlled negative result" to "a null result under this design" and
  "a boundary on the idea" to "no support, at these dimensions, for the idea", and keep the quantitative
  work in the supplement.
additional_evidence_needed: none (read-only recomputation from the promoted ablation release)
dependencies: coordinate with the ECB/T2-BENCH seat on Section 10.9 narrowing wording (I am NOT re-raising
  the advertised null as a Section 10.9 leak - the narrowing is explicit and I accept it)
expected_improvement: the strength of the abstract claim matches the strength of the evidence.
post_revision_verification: Assert the abstract and conclusions sentences about the ISM null each carry
  either an interval, a detectability statement, or an explicit "failure to detect, not demonstration of
  absence" qualifier.
status: open
```

### S9-09 — No A.7 register row exists for any supplement-reported ablation or post-hoc statistic, and two analysis directories sit outside the controlled analysis area

```text
ticket_id: S9-09
review_stage: Stage 9
reviewer_role: R4 / T3-STAT
severity: Moderate
priority: P2
confidence: Confirmed
issue_type: reproducibility / statistics
manuscript_location: papers/supplementary.tex Tables SA01, SA02, tab:ism-isolation, tab:ism-subset, and the
  post-hoc subsection at :511-556; register file
  papers/analysis/rel-2026-07-20-67d9345f9/primary_stats/statistical_results.csv
claim_id_or_artifact_id: AN-ABL-SCAFFOLD, AN-ABL-SGSM-OVERLAY, AN-ABL-POLISH, AN-ROB post-hoc
concise_issue: SAP Section 12 pre-registers three ablation families that "get rows in
  papers/analysis/<release>/primary_stats/statistical_results.csv". The register contains ZERO rows for any
  of them, though the supplement typesets their Friedman ranks, Wilcoxon/Holm p-values and A12 values -
  including the isolation null that the abstract carries. The two post-hoc supplement statistics likewise
  have no rows, and their source CSVs live outside the controlled analysis area.
exact_evidence_or_observation:
  Group counts over statistical_results.csv analysis_id (5,098 rows, 60 groups): no group name begins with
    "AN-ABL". Searching all three release bundles under papers/analysis/ for an ablation register returns
    nothing; the only statistical_results.csv files are the three primary ones.
  Supplement-reported statistics with no register row: SA01 (28 rank cells + deltas), SA02 (24 Wilcoxon/Holm
    contrasts), tab:ism-isolation (9 Delta-rank / 9 Holm p / 9 mean A12 + 3 Friedman omnibus p),
    tab:ism-subset (14 W/T/L triples + subset p-values), the endpoint-invariance table (12 ranks) and the
    sign-flip result (2e5 resamples, 0/24 decisions changed).
  Location: papers/analysis/posthoc_robustness/ and papers/analysis/ablation_overlay/ are NOT under a
    <release_id> directory, whereas Section 1.1 binds DERIVED_ANALYSIS_BUNDLE to papers/analysis/<release_id>/.
    (The underlying evidence for the ablation numbers IS in the promoted immutable release
    benchmarks/cec_reference_results/_ablation/, abl-rel-2026-07-20, which is correct.)
  I verified all nine ISM-isolation cells, the three overlay Friedman p-values, the three runtime-overhead
    percentages and the class-subset table reproduce exactly from the promoted ablation release, so this is a
    registration gap, not a numbers problem.
root_cause: The ablation pipeline emits its own JSON/CSV summaries and was never wired into the A.7 register
  emitter; the post-hoc checks were added at submission phase A1 and written to an ad-hoc directory.
scientific_or_editorial_justification: Section 10.7 and the Stage 9 deliverable both require "a
  machine-readable row for every reported statistic"; Section 10.3 requires publication analysis to resolve
  inside the controlled analysis area.
impact_on_validity_or_acceptance: Nothing reported is wrong or unbound to raw evidence, but a third of the
  paper's reported statistics are outside the machine-readable audit trail the project's own controls
  mandate. A reproducibility-focused referee (or the journal's data-availability check) will notice the
  asymmetry between the primary and supplement layers.
required_correction: Emit A.7-schema rows for the three ablation families and the two post-hoc analyses into
  a register file (either appended to the existing primary_stats register with the ablation release id in the
  evidence_release_id column, or a sibling ablation register), and relocate/alias
  papers/analysis/{posthoc_robustness,ablation_overlay}/ under a release-identified directory.
acceptable_alternatives: Record an explicit, justified exemption in the reproducibility manifest stating that
  supplement-only component statistics are registered in the ablation release's own artifacts
  (overlay_contrasts_*.json), and cite that file from the supplement captions.
additional_evidence_needed: none
dependencies: no rerun; register emission only
expected_improvement: complete machine-readable statistical audit trail.
post_revision_verification: Assert that every numeric statistic printed in supplement Sections S6.1-S6.6 and
  S2.4 resolves to exactly one register row.
status: open
```

### S9-10 — Ablation omnibus uses the plain Friedman chi-square, not the Iman–Davenport criterion the plan inherits

```text
ticket_id: S9-10
review_stage: Stage 9
reviewer_role: R4 / T3-STAT
severity: Minor
priority: P3
confidence: Confirmed
issue_type: statistics
manuscript_location: papers/supplementary.tex:1990-1993 ("the four cells differ overall (Friedman
  p = 2.4e-3, 5.2e-3, and 3.8e-3 ...)"); source
  benchmarks/cec_reference_results/_ablation/overlay/analysis/overlay_contrasts_*.json
claim_id_or_artifact_id: AN-ABL-SGSM-OVERLAY
concise_issue: SAP Section 5 makes the Iman-Davenport p the omnibus decision criterion and reports the
  tie-corrected statistic; SAP Section 12 states the ablation families "reuse the machinery of Sections 5-7
  unchanged". The overlay study reports the raw Friedman chi-square p with no Iman-Davenport refinement and
  no tie correction.
exact_evidence_or_observation:
  overlay_contrasts_cec2017_D50.json: "friedman_omnibus": {"chi2": 14.43103, "p_value": 0.00237346,
    "n_problems": 29, "n_algorithms": 4} - a chi-square-distribution p; no iman_davenport_F, no
    tie_correction_C field anywhere in the file. Same shape for D100 and CEC2013 D50.
  Contrast: the primary friedman_ranks_*.csv carry friedman_chi2, iman_davenport_F, tie_correction_C,
    n_tied_functions and the uncorrected companions.
root_cause: The ablation analysis path predates M-026 and was not brought onto the corrected statistics API.
scientific_or_editorial_justification: Consistency of the omnibus criterion across the paper's analyses;
  the plan explicitly binds the ablation families to the same machinery.
impact_on_validity_or_acceptance: No decision changes (all three omnibus p are well below 0.05 and the
  Iman-Davenport refinement is more powerful, so it can only strengthen them). Purely a consistency defect.
required_correction: Either recompute the three overlay omnibus statistics with the Iman-Davenport
  refinement and tie correction and report them, or state in the S6.5 Statistical Treatment paragraph that
  the ablation omnibus is the plain Friedman chi-square and why.
acceptable_alternatives: state the deviation in the supplement's Statistical Treatment paragraph.
additional_evidence_needed: none
dependencies: S9-09 (same regeneration pass)
expected_improvement: one omnibus criterion across the paper.
post_revision_verification: Assert the omnibus statistic name and correction state is identical in the
  primary and ablation register rows, or that a stated exemption exists.
status: open
```

### S9-11 — The pre-registered floor-sensitivity check could not be executed as written and the substitution is not disclosed in the manuscript

```text
ticket_id: S9-11
review_stage: Stage 9
reviewer_role: R4 / T3-STAT
severity: Minor
priority: P3
confidence: Confirmed
issue_type: statistics / evidence
manuscript_location: papers/sections/performance.tex:483-492 ("A prespecified robustness battery accompanies
  the release, and two of its checks diverge from the primary analysis")
claim_id_or_artifact_id: AN-ROB-2017-02
concise_issue: SAP Section 10 item 2 pre-registers "error-floor sensitivity (recompute ties/W/T/L at floor
  1e-6 vs 1e-8)". The digest records that the raw sub-floor values are unrecoverable from the release and
  that a surrogate was run instead. The manuscript reports only that two checks diverged; it does not
  disclose that one check could not be executed as pre-registered.
exact_evidence_or_observation:
  papers/analysis/.../cec2017/robustness/robustness_cec2017_r02_floor_sensitivity_digest.md, verbatim:
    "Branch B disclosure (pre-registered): raw sub-floor values are unrecoverable from the release
     (write-time flooring); the check is executed as the nearest admissible surrogate B1/B2 (tie handling at
     the floor; means <= 1e-8 snapped to 0 before ranking/W-T-L)."
    verdict: agree
  The manuscript's robustness paragraph mentions r01 and r04 by content and refers to "a prespecified
    robustness battery" without stating that r02's pre-registered form was infeasible.
root_cause: The release floors errors at write time, so the pre-registered comparison of two floors cannot be
  performed on raw values; branch B was correctly pre-specified and correctly executed and logged, but the
  disclosure stopped at the digest.
scientific_or_editorial_justification: Section 4.6 forbids suppressing exceptions; a pre-registered check
  that had to be substituted is exactly the kind of exception that belongs in the text.
impact_on_validity_or_acceptance: Low - the branch was pre-specified, the substitution is logged, and the
  verdict is "agree". It is a one-sentence disclosure gap.
required_correction: Add one clause to the robustness paragraph: "...; the pre-registered floor-sensitivity
  check was executed in its pre-specified surrogate form because the release floors sub-1e-8 errors at write
  time, and it agrees with the primary analysis."
acceptable_alternatives: state it in the supplement's tie-band subsection, which already discusses the floor.
additional_evidence_needed: none
dependencies: pairs naturally with S9-04's rewrite
expected_improvement: the robustness battery's actual execution status is visible to the reader.
post_revision_verification: Assert the manuscript states the execution branch for every robustness check
  whose digest records a substitution.
status: open
```

### S9-12 — Nemenyi CD is computed with the untied formula while the omnibus is tie-corrected, and the "within one CD of best" cohorts are knife-edge

```text
ticket_id: S9-12
review_stage: Stage 9
reviewer_role: R4 / T3-STAT
severity: Minor
priority: P3
confidence: Confirmed
issue_type: statistics
manuscript_location: papers/sections/performance.tex:442-474 (CD formula and Figure 4 caption cohorts)
claim_id_or_artifact_id: AN-OMNI-2017-* / FIG-CD-D10..D100 / RS-06
concise_issue: The same section that makes the Friedman tie correction a methodological point uses the
  standard untied Nemenyi CD, and the figure caption then states four crisp "within one CD of best" cohorts,
  two of whose boundaries turn on less than 0.09 rank units.
exact_evidence_or_observation:
  CD = q_0.05 * sqrt(k(k+1)/(6N)) = 2.949 * sqrt(56/174) = 1.672993 (matches nemenyi_cd_cec2017_D10.csv
    exactly); the formula assumes no ties in the block ranks, but D10 has 9 of 29 tied blocks
    (tie_correction_C = 0.8898) and D30 has 3.
  Cohort boundary arithmetic (my recomputation on unrounded mean ranks):
    D50 : best = DT-GSK 2.2069, threshold 3.8799; FDB-AGSK is 3.9655 - excluded by 0.086 rank units.
    D100: best = DT-GSK 2.3448, threshold 4.0178; GSK is 4.0345 - excluded by 0.017 rank units.
  All four cohorts as printed are arithmetically correct; the concern is that they are presented as
    partitions without noting how close two of the exclusions are.
root_cause: The CD generator predates M-026 and the caption was written from its output.
scientific_or_editorial_justification: The tie correction shrinks the effective rank variance, so the untied
  CD is CONSERVATIVE (wider than necessary). That direction protects every "not separable" statement the
  paper makes - so this is not a validity problem - but it makes the exclusions (which are separability
  assertions in the other direction) the ones that need care.
impact_on_validity_or_acceptance: Low. The paper's key CD claim (DT-GSK and eGSK never separable) is safe in
  both directions. The cohort sets read as firmer than a 0.017-rank-unit margin supports.
required_correction: Add a half-sentence to the Figure 4 caption noting that the CD uses the standard untied
  formula (conservative under the observed ties) and that the D100 and D50 cohort boundaries are within
  0.02 and 0.09 rank units respectively.
acceptable_alternatives: Report the cohort as an ordered rank list with the CD span drawn, and drop the set
  notation.
additional_evidence_needed: none
dependencies: none
expected_improvement: the post-hoc display's precision matches its resolution.
post_revision_verification: Assert the caption discloses the CD variance assumption and any cohort boundary
  narrower than 0.1 rank units.
status: open
```

### S9-13 — The unpaired-companion sentence silently shifts unit of analysis inside a paragraph about rank statements

```text
ticket_id: S9-13
review_stage: Stage 9
reviewer_role: R4 / T3-STAT
severity: Minor
priority: P3
confidence: Confirmed
issue_type: statistics / writing
manuscript_location: papers/sections/performance.tex:498-503 (Robustness of the rank statements paragraph)
claim_id_or_artifact_id: AN-ROB-2017-05
concise_issue: The sentence "An unpaired Mann-Whitney companion produces 11 paired-significant-to-unpaired-
  non-significant transitions and 21 transitions in the opposite direction" sits in a paragraph about
  across-function rank statements, but the 32 transitions are counted over the 696 RUN-LEVEL per-function
  tests, a different analysis layer. The unit is not stated.
exact_evidence_or_observation:
  robustness_cec2017_r05_unpaired_companion.csv has 696 rows = 29 functions x 6 comparators x 4 dimensions,
    columns p_paired_raw / p_unpaired_raw / transition. Value counts: none 664, ns_to_sig 21, sig_to_ns 11 -
    reproducing the manuscript's two numbers exactly.
  The paragraph's other content (median re-ranking, disputed-cell exclusion, ordinal positions) is all at
    the across-function/rank layer.
root_cause: r05 was defined at the run level in the plan (Section 10 item 5, "unpaired Mann-Whitney companion
  to selected per-function Wilcoxon results") and the sentence was folded into the nearest paragraph.
scientific_or_editorial_justification: Section 9 requires run-level variability not to be confused with
  across-function variability; the paper is otherwise scrupulous about this distinction, which makes the one
  unlabelled shift stand out.
impact_on_validity_or_acceptance: Low, but a careful reader will try to reconcile "11 and 21 transitions"
  with a 24-cell table and fail.
required_correction: Insert the unit: "...across the 696 run-level per-function tests, an unpaired
  Mann-Whitney companion produces 11 ... and 21 ...".
acceptable_alternatives: move the sentence to the supplement's post-hoc subsection.
additional_evidence_needed: none
dependencies: none
expected_improvement: unit of analysis explicit at every reported count.
post_revision_verification: Assert every reported count in the robustness paragraph names its denominator.
status: open
```

### S9-14 — A mathematically necessary invariance is presented as a robustness finding

```text
ticket_id: S9-14
review_stage: Stage 9
reviewer_role: R4 / T3-STAT
severity: Minor
priority: P3
confidence: Confirmed
issue_type: statistics / writing
manuscript_location: papers/sections/performance.tex:398-404 ("...and the count of significant losses
  remains zero under either correction")
claim_id_or_artifact_id: AN-GHOLM-2017
concise_issue: Holm over a larger family produces adjusted p-values that are pointwise >= those from Holm
  over a subfamily, so a comparison that was not a significant loss under the within-dimension correction
  cannot become one under the global correction. The sentence presents an arithmetic necessity as evidence.
exact_evidence_or_observation:
  global_holm_sensitivity_cec2017.csv: p_holm_global_m24 >= p_holm_within_dimension in all 24 rows
    (e.g. D10 ATMALS 0.036220 -> 0.081496; D30 GSK 0.029494 -> 0.117975).
  The genuinely informative parts of the same sentence - 15 of 24 survive, and exactly two cells drop out -
    are correct and reproduce exactly; only the "zero losses under either" clause is vacuous.
root_cause: M-028 phrasing.
scientific_or_editorial_justification: Section 4.6 - avoid presenting non-evidence as evidence.
impact_on_validity_or_acceptance: Editorial-to-Minor; a statistically literate referee will notice.
required_correction: Delete the clause, or reframe: "(no cell can become a significant loss under a stricter
  correction, so the zero-loss count is unchanged by construction)".
acceptable_alternatives: none needed.
additional_evidence_needed: none
dependencies: none
expected_improvement: removes a soft over-claim from an otherwise well-qualified paragraph.
post_revision_verification: text check.
status: open
```

### S9-15 — The frozen SAP is not at the path the governing profile binds, and still names a superseded release as its sole empirical source

```text
ticket_id: S9-15
review_stage: Stage 9
reviewer_role: R4 / T3-STAT
severity: Minor
priority: P3
confidence: Confirmed
issue_type: reproducibility / compliance
manuscript_location: governance only - papers/governance/ (absent file) vs
  papers/build_prompt_phases/phase_05/statistical_analysis_plan.md (actual)
claim_id_or_artifact_id: STATISTICAL_ANALYSIS_PLAN binding, PAPER_REVIEW_PROMPT.md Section 10.1
concise_issue: Section 10.1 binds STATISTICAL_ANALYSIS_PLAN to papers/governance/statistical_analysis_plan.md.
  No such file exists. The frozen plan lives under papers/build_prompt_phases/phase_05/ and still declares
  rel-2026-07-10-262fc16c9 as "Evidence release (sole empirical source)", two releases behind the shipped
  rel-2026-07-20-67d9345f9, with every internal path pointing at the 07-10 analysis bundle.
exact_evidence_or_observation:
  A filesystem search for *statistical_analysis_plan* returns exactly one hit:
    ./papers/build_prompt_phases/phase_05/statistical_analysis_plan.md
  That file, line 6: "**Evidence release (sole empirical source):** `rel-2026-07-10-262fc16c9`".
  Line 10 and Section 12 route every register row to
    papers/analysis/rel-2026-07-10-262fc16c9/primary_stats/statistical_results.csv.
  The shipped register is at papers/analysis/rel-2026-07-20-67d9345f9/primary_stats/statistical_results.csv.
root_cause: The plan was frozen against the first release and the release id was never re-pointed (correctly,
  since re-editing a frozen plan is itself a control violation), but no supersession note was added and no
  copy/alias was placed at the profile-bound governance path.
scientific_or_editorial_justification: Section 10.1 requires the review to validate the bound artifacts
  rather than hunt for them; a reviewer following the binding finds nothing.
impact_on_validity_or_acceptance: Administrative. The plan's substance is unaffected and CR-0006/CR-0007
  document the release progression elsewhere.
required_correction: Place the frozen plan (or a pointer file) at papers/governance/statistical_analysis_plan.md
  and add a dated supersession header recording that the frozen methods apply unchanged to
  rel-2026-07-16-78f075cb0 and rel-2026-07-20-67d9345f9, with the register path updated accordingly. Do not
  edit the frozen body.
acceptable_alternatives: record the actual path in project_configuration.md as the authoritative binding.
additional_evidence_needed: none
dependencies: S9-06 (the same supersession header is the natural home for the M-026/027/028 amendment note)
expected_improvement: the plan is discoverable at its bound path and its release scope is unambiguous.
post_revision_verification: Assert papers/governance/statistical_analysis_plan.md exists and its declared
  release id set includes the shipped release.
status: open
```

### S9-16 — Governing prompt Section 1.5 / Section 10.7 snapshot is stale relative to the shipped package (mandated staleness record)

```text
ticket_id: S9-16
review_stage: Stage 9
reviewer_role: R4 / T3-STAT
severity: Minor
priority: P3
confidence: Confirmed
issue_type: compliance
manuscript_location: papers/PAPER_REVIEW_PROMPT.md Section 1.5 (dated 2026-07-20) and Section 10.7 final
  bullet (RT-001)
claim_id_or_artifact_id: RT-001; Section 10.7 per-run-gap disposition
concise_issue: Recorded per the review instruction. Two statistics-relevant items in the prompt's own
  snapshot no longer describe the repository.
exact_evidence_or_observation:
  (a) Section 10.7 RT-001 states the runtime table "and its source (cost_cec2017.csv) are being brought into
      single-environment comparability by re-timing all six comparators on one idle machine
      (scripts/retime_comparators.py)" and instructs the review to treat the runtime cells as in-progress.
      The shipped manuscript resolved this the other way: papers/sections/performance.tex:738-784 tabulates
      DT-GSK's own wall-clock ONLY, states "The comparator timings were collected in a separate measurement
      session, so we do not tabulate a cross-algorithm wall-clock comparison and make no runtime-superiority
      claim", and the cost artifact stamps comparability=NOT-COMPARABLE-ACROSS-ALGORITHMS. There is no mixed
      two-session comparison left to certify. Under Section 1.4 precedence the repository governs.
  (b) Section 10.7's per-run-gap disposition (function-level fallback, run-level quantities
      disclosed-unavailable) is superseded for APGSK by CR-0006: the run-level records were recovered
      deterministically post-freeze, the manuscript discloses the recovery in a footnote
      (performance.tex:134-139) and conservatively retains the frozen function-level basis. The manuscript
      draws the recovery-versus-comparability line correctly in both directions - seed-deterministic
      quantities acknowledged as recovered, non-deterministic wall-clock kept out of any cross-algorithm
      comparison - so this control is satisfied, not violated.
root_cause: the prompt snapshot predates the 2026-07-21/22 remediation.
scientific_or_editorial_justification: Section 1.4 precedence; the review instruction requires recording it.
impact_on_validity_or_acceptance: none on the manuscript; affects the review record only.
required_correction: Refresh Section 1.5 and the Section 10.7 RT-001 bullet to the shipped state.
acceptable_alternatives: none
additional_evidence_needed: none
dependencies: none
expected_improvement: prompt and repository agree.
post_revision_verification: n/a (review-record item)
status: open
```

### S9-17 — The across-function A12 is an estimand with no clean interpretation, and is used for the paper's most delicate cells

```text
ticket_id: S9-17
review_stage: Stage 9
reviewer_role: R4 / T3-STAT
severity: Minor
priority: P3
confidence: Confirmed (computation) / Medium (severity judgement)
issue_type: statistics
manuscript_location: papers/sections/performance.tex:221-231 and 405-426
claim_id_or_artifact_id: RS-08 / AN-PW-2017-*
concise_issue: The A12 the paper quotes for the eGSK cells is computed over the 29x29 cross-product of
  per-function mean errors, i.e. it includes comparisons of DT-GSK on function i against the comparator on a
  DIFFERENT function j. That quantity is driven by the marginal distribution of error magnitudes across
  functions, not by per-function superiority, and it is not the A12 the frozen plan defines.
exact_evidence_or_observation:
  SAP Section 7 defines A12 as "the probability that a randomly chosen DT-GSK run achieves a strictly lower
    error ... than a randomly chosen comparator run ON THE SAME FUNCTION", ties counted half - a within-
    function, run-level quantity. The values quoted in the main text are the across-function analogue.
  I reproduced the quoted values by taking all 29x29 pairs of per-function means (0.4905, 0.5054, 0.4721,
    0.7122), confirming the estimand actually used.
  The paper does flag the statistic as "unpaired" and "distinct from the run-level A12", which is honest
    about the unit but not about the interpretive problem.
root_cause: The across-function A12 was introduced to give the across-function Wilcoxon a companion effect
  size on the same unit; the aligned companion (rank-biserial) later replaced it in the table but not in the
  prose (see S9-02).
scientific_or_editorial_justification: An effect size must have a stated estimand; "P(DT-GSK's mean on a
  random function < comparator's mean on an independently drawn random function)" is not a comparison of the
  algorithms on a task.
impact_on_validity_or_acceptance: The three eGSK values (0.490/0.505/0.472) are used to characterise the
  paper's most delicate non-significant cells as "negligible magnitudes"; the aligned paired r for the same
  cells (-0.286, -0.002, -0.057) tells a slightly different story at D30. Nothing is wrong, but the choice of
  statistic flatters the D30 cell.
required_correction: Resolve together with S9-02: report the matched-pairs r for these cells (it is the
  statistic actually tabulated), and if A12 is retained anywhere, state its estimand explicitly or move it to
  the run-level within-function form the plan defines.
acceptable_alternatives: keep the across-function A12 as an explicitly labelled descriptive summary of the
  two marginal error distributions, and never call it an effect size.
additional_evidence_needed: none
dependencies: S9-02
expected_improvement: every reported effect size has a stated, interpretable estimand.
post_revision_verification: Assert each effect size in the manuscript maps to a SAP Section 7 definition or a
  logged amendment.
status: open
```

### Advisory items (non-blocking)

- **A-1.** The r05 result is the *opposite* of its own pre-stated expectation: the digest says "Expected
  direction: unpaired less powerful under positive pairing correlation", yet 21 cells move n.s.→significant
  and only 11 move the other way. The manuscript reports both counts honestly but offers no interpretation.
  A reviewer may read it as evidence that the paired differences are not consistently positively correlated,
  which bears on the signed-rank symmetry assumption. One sentence of interpretation would pre-empt this.
- **A-2.** The signed-rank test's symmetry-of-paired-differences assumption is nowhere discussed. Across
  functions of heterogeneous scale it is implausible on its face. The post-hoc sign-flip randomisation
  (supplement S2.5) is the right robustness answer and already shows 0/24 decision changes — but it was run
  for **CEC2017 only**. The single Holm-significant *adverse* headline cell (CEC2011 vs eGSK, p_Holm = 0.042,
  n = 20) is in the family with the smallest n and no randomisation check. Extending the existing sign-flip
  script to CEC2011 and CEC2013 is read-only and cheap. (I ran the exact-Wilcoxon equivalent: 0 decision
  changes on all three suites, CEC2011 vs eGSK 0.0424 → 0.0320 exact. The paper would be strengthened by
  saying so.)
- **A-3.** `AN-OMNI-*` register rows for `nemenyi_critical_difference` carry an empty `interpretation` field
  and NaN `p_raw`; a one-line descriptor would complete the register.

---

## 5. Statistical-analysis register (Appendix A.7) — recomputation results

Full schema retained; long invariant fields abbreviated in the header note to keep the table readable. Every
`recomputed_value` below is from my own harness against the immutable release, not from the analysis bundle.

Common fields for all CEC2017 primary rows unless stated: `endpoint=final error (floor 1e-8→0)`;
`observation_unit=run`; `experimental_unit=function`; `aggregation_before_testing=per-function mean over 51 runs`;
`pairing_key=function identity`; `sample_size_or_task_count=29`; `missing_data_rule=none (summary CSVs complete)`;
`failure_encoding=no failed runs; early stop = complete observation`; `one_or_two_sided=two-sided`;
`RNG_seed=n/a (deterministic)`; `software_and_version=gsk_family.analysis.statistics + SciPy 1.15.3`;
`evidence_release=rel-2026-07-20-67d9345f9`.

```csv
analysis_id,estimand,test,multiplicity_family,correction,effect_size,effect_direction,uncertainty_interval,reported_value,recomputed_value,match_status,ticket_ids
AN-OMNI-2017-D10,population mean rank,friedman+iman-davenport,1 per (suite dim),none,mean rank,lower better,none,DT-GSK 2.88,2.879310,MATCH,
AN-OMNI-2017-D30,population mean rank,friedman+iman-davenport,1 per (suite dim),none,mean rank,lower better,none,DT-GSK 2.50,2.500000,MATCH,
AN-OMNI-2017-D50,population mean rank,friedman+iman-davenport,1 per (suite dim),none,mean rank,lower better,none,DT-GSK 2.21,2.206897,MATCH,
AN-OMNI-2017-D100,population mean rank,friedman+iman-davenport,1 per (suite dim),none,mean rank,lower better,none,DT-GSK 2.34,2.344828,MATCH,
AN-OMNI-2017-D30,population mean rank,friedman+iman-davenport,1 per (suite dim),none,mean rank,lower better,none,eGSK 2.29 (best),2.293103,MATCH,
AN-OMNI-2017-ALL,omnibus significance,iman-davenport,4 families,none,n/a,n/a,none,p <= 2.6e-8,"tie-corrected max 1.160e-9; UNcorrected max 2.577e-8",MISMATCH-vs-DECLARED-METHOD,S9-03
AN-OMNI-2017-D10,tie correction,friedman tie correction,n/a,n/a,C,n/a,none,C=0.890 over 9 of 29,0.889778 / 9,MATCH,
AN-OMNI-2017-D30,tie correction,friedman tie correction,n/a,n/a,C,n/a,none,C=0.979,0.979110,MATCH,
AN-OMNI-2017-D50/D100,tie correction,friedman tie correction,n/a,n/a,C,n/a,none,C=1 exactly; no ties,1.000000 / 0 tied blocks,MATCH,
AN-RANKAGG-2017-OVERALL,descriptive mean of 4 per-dim ranks,none (no test),n/a,none,mean rank,lower better,none,DT-GSK 2.48; eGSK 2.96,2.482759 / 2.961207,MATCH,
AN-PW-2017-D10,median paired per-function difference,wilcoxon signed-rank,6 comparators,holm m=6,rank-biserial,r>0 favours DT-GSK,DISCLOSED-UNAVAILABLE,"GSK p=0.0002 pH=0.0010 r=+0.865","p_raw=1.65295e-4 pH=9.9177e-4 r=+0.864615 (formula on released operands gives -0.864615)",MATCH-VALUE / FORMULA-SIGN-MISMATCH,S9-01;S9-07
AN-PW-2017-D10,as above,wilcoxon signed-rank,6 comparators,holm m=6,rank-biserial,r>0 favours DT-GSK,DISCLOSED-UNAVAILABLE,"ATMALS pH=0.0362; eGSK pH=0.0035","0.0362203 / 0.0034917",MATCH,S9-07
AN-PW-2017-D30,as above,wilcoxon signed-rank,6 comparators,holm m=6,rank-biserial,r>0 favours DT-GSK,DISCLOSED-UNAVAILABLE,"eGSK pH=0.199 r=-0.286",0.1986745 / -0.285714,MATCH,S9-07
AN-PW-2017-D50,as above,wilcoxon signed-rank,6 comparators,holm m=6,rank-biserial,r>0 favours DT-GSK,DISCLOSED-UNAVAILABLE,"eGSK pH=1.0 r=-0.002",1.000000 / -0.002299,MATCH,S9-07
AN-PW-2017-D100,as above,wilcoxon signed-rank,6 comparators,holm m=6,rank-biserial,r>0 favours DT-GSK,DISCLOSED-UNAVAILABLE,"GSK p=0.0323 pH=0.0646 (n.s.)",0.03229837 / 0.06459675,MATCH,S9-07
AN-PW-2017-D100,as above,wilcoxon signed-rank,6 comparators,holm m=6,rank-biserial,r>0 favours DT-GSK,DISCLOSED-UNAVAILABLE,"eGSK pH=0.795 r=-0.057",0.7952663 / -0.057471,MATCH,S9-07
AN-PW-2017-ALL,decision tally,wilcoxon+holm,4x6,holm m=6 within dim,n/a,n/a,none,"17 wins / 7 n.s. / 0 losses","17 / 7 / 0",MATCH,
AN-PW-2017-ALL,p reproducibility,wilcoxon normal approx,n/a,n/a,n/a,n/a,none,"p attributed to scipy.stats","8 of 24 cells differ from scipy at 4 s.f.",MISMATCH-ATTRIBUTION,S9-05
AN-PW-2017-ALL,exact-test sensitivity,wilcoxon exact,4x6,holm m=6,n/a,n/a,none,not reported,0 of 24 Holm decisions change under exact test,VERIFIED-ROBUST,A-2
AN-GHOLM-2017,global multiplicity sensitivity,wilcoxon+holm,24 hypotheses,holm m=24,n/a,n/a,none,"15 of 24 survive; ATMALS@D10 and GSK@D30 drop","15 survive; exactly those two",MATCH,S9-06;S9-14
(unregistered),across-function A12 on per-function means,none (descriptive),n/a,none,A12,A12>0.5 favours DT-GSK,none,"eGSK 0.490 / 0.505 / 0.472; APGSK D100 0.712","0.4905 / 0.5054 / 0.4721 / 0.7122",VALUE-MATCH / UNBOUND-TO-ARTIFACT,S9-02;S9-17
AN-DESC-2017-*,win/tie/loss vs GSK,none (descriptive),n/a,none,W/T/L,DT-GSK first,none,"22-4-3 / 19-2-8 / 22-0-7 / 20-0-9",identical,MATCH,
AN-DESC-2017-*,win/tie/loss vs eGSK,none (descriptive),n/a,none,W/T/L,DT-GSK first,none,"11-2-16 / 13-0-16 / 12-0-17",identical,MATCH,
AN-OMNI-2017-*,post-hoc separability,nemenyi CD,k=7 N=29,n/a,CD span,n/a,none,"CD=1.67 (q=2.949)",1.672993,MATCH,
AN-OMNI-2017-*,DT-GSK vs eGSK rank gaps,nemenyi CD,n/a,n/a,rank units,n/a,none,"1.36 / 0.21 / 0.41 / 0.34",1.3621 / 0.2069 / 0.4138 / 0.3448,MATCH,
AN-OMNI-2017-*,within-1-CD cohorts,nemenyi CD,n/a,n/a,set,n/a,none,"4 cohorts as captioned",all four verified; boundaries 0.017 and 0.086 rank units at D100/D50,MATCH / KNIFE-EDGE,S9-12
TAB-T16-BCA,rank stability,BCa bootstrap (descriptive),n/a,none,mean rank,lower better,"95% BCa, B=10000, seed 20260422","DT-GSK [2.29,3.43] [2.07,3.10] [1.86,2.69] [1.90,2.83]",identical,MATCH,
AN-TREND-2017,rank vs dimension,none (descriptive),n/a,none,mean rank,lower better,none,"2.88 2.50 2.21 2.34; non-monotone",identical,MATCH,
AN-CLASS-2017,per-class mean rank,none (exploratory descriptive),n/a,none,class mean rank,lower better,none,"hybrid 1.60/1.80/2.30; simple-mm 2.07/3.29/2.29/1.71; comp D10 3.70",all 14 quoted cells identical,MATCH,
AN-ROB-2017-01,mean vs median re-ranking,none (exploratory),n/a,none,ordinal + W/T/L,n/a,none,"21-4-4 -> 17-10-2 vs eGSK D10; APGSK/eGSK swap D10; FDB/ATMALS swap D50; D100 tie 2.59",digest identical,MATCH,
AN-ROB-2017-04,disputed-cell exclusion,none (exploratory),n/a,none,ordinal,n/a,none,"GSK/FDB-AGSK swap at D30",digest identical,MATCH,
AN-ROB-2017-05,paired vs unpaired,mann-whitney companion,identical families,holm,n/a,n/a,none,"11 sig->n.s.; 21 n.s.->sig; 0 sign reversals","11 / 21 / 0 over 696 run-level cells",MATCH / UNIT-UNSTATED,S9-13
AN-ROB-2017-02,floor sensitivity,surrogate branch B,n/a,n/a,n/a,n/a,none,"battery accompanies the release","pre-registered form infeasible; surrogate executed; not disclosed in main text",DISCLOSURE-GAP,S9-11
AN-OMNI-2011-NATIVE,population mean rank,friedman+iman-davenport (tie-corrected),1 family,none,mean rank,lower better,none,"F=4.27 p=6.0e-4; DT-GSK 3.36 eGSK 2.52","F=4.266899 p=6.0079e-4 (CORRECTED); 3.3636 / 2.5227",MATCH,
AN-PW-2011-NATIVE,median paired per-problem difference,wilcoxon signed-rank,6 comparators,holm m=6,rank-biserial,r>0 favours DT-GSK,DISCLOSED-UNAVAILABLE,"eGSK LOSS p=9.5e-3 pH=4.2e-2","9.46961e-3 / 4.2448e-2",MATCH,S9-07
AN-PW-2011-NATIVE,as above,wilcoxon signed-rank,6 comparators,holm m=6,rank-biserial,n/a,DISCLOSED-UNAVAILABLE,"AGSK pH=1.6e-2; FDB pH=4.2e-2; GSK/APGSK 0.137; ATMALS 0.323","0.015921 / 0.042448 / 0.137378 / 0.322509",MATCH,
AN-PW-2011-NATIVE,head-to-head vs GSK,wilcoxon signed-rank,6,holm m=6,W/T/L + rank sums,n/a,DISCLOSED-UNAVAILABLE,"13-2-7; R+=159 R-=51; p=4.6e-2 pH=0.137","13-2-7; workbook w_plus=51 w_minus=159 (labels transposed); 0.0457927 / 0.137378",MATCH-VALUE / LABEL-INVERSION,S9-01
AN-OMNI-2011-NATIVE,post-hoc separability,nemenyi CD,k=7 N=22,n/a,CD span,n/a,none,"CD=1.92; gap 0.84",1.92077 / 0.8409,MATCH,
AN-OMNI-2013-D10/D30/D50,population mean rank,friedman+iman-davenport,3 families,none,mean rank,lower better,none,"2.41 / 3.38 / 2.61; overall 2.80","2.4107 / 3.3750 / 2.6071 / 2.7976",MATCH,
AN-OMNI-2013-D10/D30/D50,omnibus p,iman-davenport,3 families,none,n/a,n/a,none,"3.3e-7 / 2.2e-3 / 9.2e-6; caption <=2.3e-3","UNcorrected 3.264e-7 / 2.242e-3 / 9.212e-6; corrected 5.32e-8 / 1.090e-3 / 2.909e-6",MISMATCH-vs-DECLARED-METHOD,S9-03
AN-PW-2013-D30,eGSK and ATMALS at D30,wilcoxon signed-rank,6,holm m=6,rank-biserial,n/a,DISCLOSED-UNAVAILABLE,"pH=0.748 each",0.7480821 both,MATCH,S9-07
AN-PW-2013-*,head-to-head vs GSK,wilcoxon signed-rank,6,holm m=6,W/T/L + rank sums,n/a,DISCLOSED-UNAVAILABLE,"pH 1.9e-4 / 3.1e-2 / 2.7e-3; 24-2-2 21-2-5 24-2-2; R+/R- 340/11 286/65 314/37","1.867e-4 / 3.1259e-2 / 2.741e-3; W/T/L identical; workbook w_plus 11/65/37 (transposed)",MATCH-VALUE / LABEL-INVERSION,S9-01
AN-COST-2017,DT-GSK per-run wall clock,none (descriptive),n/a,none,mean +/- SD,n/a,SD only,"4.93 / 13.04 / 23.30 / 41.59 s",cost_cec2017.csv dt-gsk rows,MATCH,
AN-DESC-2017-D30,F26 convergence descriptives,none (descriptive),n/a,none,mean/best/SD,n/a,none,"DT 1.16e3 / 9.85e2 / 7.5e1; ATMALS 1.32e3; GSK SD 2.7e2","1159.393 / 984.556 / 75.306 / 1322.564 / 269.262",MATCH,
AN-DESC-2017-D100,F26 comparator ordering,none (descriptive),n/a,none,mean,n/a,none,"DT 4.09e3 below ATMALS/FDB/AGSK/APGSK; above GSK 3.69e3 and eGSK 3.05e3",all seven means verified,MATCH,
X-ABL-02 (unregistered),ISM standalone effect,wilcoxon signed-rank,3 contrasts per cell,holm m=3,Friedman Delta-rank + mean A12,positive = removal hurts,NONE,"+0.05 p=0.983 A12=0.51; +0.16 p=0.897 A12=0.50; +0.20 p=0.647 A12=0.42","0.0517/0.98270/0.5065; 0.1552/0.89677/0.5031; 0.1964/0.64737/0.4190",MATCH / NO-REGISTER-ROW / NO-INTERVAL,S9-08;S9-09
X-ABL-02 (unregistered),final-polish effect,wilcoxon signed-rank,3 contrasts per cell,holm m=3,Delta-rank + mean A12,positive = removal hurts,NONE,"+1.14 p=0.002; +0.98 p=0.005; +1.18 p=0.002","1.1379/0.00183; 0.9828/0.005226; 1.1786/0.001727",MATCH,S9-09
X-ABL-02 (unregistered),overlay omnibus,friedman chi-square (NOT iman-davenport),n/a,none,n/a,n/a,none,"p=2.4e-3 / 5.2e-3 / 3.8e-3","0.0023735 / 0.0051971 / 0.0038404 (plain chi2, no tie correction)",MATCH / CRITERION-DEVIATION,S9-10
X-ABL-02 (unregistered),ISM wall-clock overhead,none (descriptive),n/a,none,percent,n/a,none,"+57.3% / +36.3% / +30.3%",identical,MATCH,S9-09
AN-ROB post-hoc (unregistered),endpoint invariance,none (post-hoc descriptive),n/a,none,mean rank,lower better,none,"raw/median/log10 ranks table; DT-GSK place unchanged",source outside controlled analysis area,NOT-REGISTERED,S9-09
AN-ROB post-hoc (unregistered),sign-flip randomisation,monte carlo sign flip (2e5),4x6,holm,n/a,n/a,none,"0 of 24 Holm decisions change",source outside controlled analysis area; CEC2017 only,NOT-REGISTERED / SCOPE-GAP,S9-09;A-2
```

---

## 6. Gate I determination and category score

| Item | Determination |
|---|---|
| Invalid units | **No.** Function-level unit, no pseudoreplication, dimensions never pooled. |
| Pseudoreplication | **No.** Run-level data never pooled across functions; the prohibition is stated and honoured. |
| Invalid pairing | **No.** Seed-schedule pairing audited (70,813 rows, 0 mismatches); the one asymmetry (DT-GSK self-init) is disclosed in four places. |
| Undisclosed multiplicity | **No.** Families enumerated; Holm primary; BH exploratory and separately labelled; global-Holm sensitivity supplied. |
| Incorrect p-values / effects / intervals | **Partly.** p-values are numerically correct but sourced from the wrong (uncorrected) column on two suites (S9-03) and attributed to the wrong package (S9-05); the printed effect-size formula is sign-inverted against the released operands (S9-01); no interval accompanies any headline pairwise claim (S9-07). |
| Outcome-driven test changes | **No evidence of any.** The three post-freeze changes (S9-06) all move conservatively and I verified none alters a decision, rank, or direction. The defect is that they are unlogged in the designated register, not that they were opportunistic. |
| Headline statistical claim that cannot be reproduced | **No.** Every headline number reproduced exactly. |

**Gate I — Statistical Validity: FAIL**, on the "incorrect p-values/effects/intervals" limb only, and
remediable entirely by text, caption, register-string and governance-log edits. **No rerun, no new evidence
release, and no change to the byte-locked optimizer core is required by any ticket in this audit.**

**Category score — Statistical rigour: 3 / 5 (adequate but vulnerable).** The underlying analysis is
methodologically sound, correctly unitised, honestly qualified, fully reproducible, and unusually good on
loss visibility. It scores 3 rather than 4 because the printed specification of two of its three reported
statistics (the effect-size formula and the omnibus p source) does not match what the artifacts contain, and
because the headline inferential layer ships without uncertainty intervals.

**Minimum path to clearing Gate I:** S9-01, S9-02, S9-03, S9-04 (all text/label; ~1 editing pass).
**Path to a 4:** additionally S9-05(c), S9-06, S9-07, S9-08 — i.e. name the real software, log the three
amendments, attach one bootstrap interval to the across-function effect, and carry the supplement's null
caveat into the abstract/conclusions.

---

## 7. Explicitly checked and found sound (recorded so other seats do not re-litigate)

- Descriptive overall-rank vs pooled test (§10.7): **correct** — the "Overall" row is labelled a descriptive
  unweighted mean in prose, caption and register, and no omnibus statistic is attached to it.
- Per-run-gap disposition (§10.7): **correct** — the function-level basis is retained, the post-freeze
  recovery is footnoted, nothing is imputed, and no claim is upgraded.
- Recovery-vs-comparability line (§10.7): **drawn correctly in both directions** — seed-deterministic
  recovery acknowledged; non-deterministic wall-clock kept out of any cross-algorithm comparison.
- Deterministic interval seeding (§10.7): **correct** — two seed constructions exist but both are
  pre-registered as distinct in SAP §7 and both appear as declared; this is not the "contradictory seed
  constructions" defect.
- Multiplicity-family hygiene (§10.7): **correct** — Holm primary within enumerated families; BH exploratory
  and separately labelled; family size stated everywhere.
- Robustness-divergence disclosure (§10.7): **correct** — both diverging checks, including the one that costs
  the paper a sole first place at D=100, are disclosed in the main text.
- Loss-visibility parity (§10.7): **correct and exemplary** — the CEC2011 eGSK Holm-significant loss, the
  three losing eGSK head-to-head records, the D=100 GSK non-significance, the CEC2013 D=30 third place and
  the D=10 composition-class weakness are all stated alongside the favourable cells, not after them.
- `p = 0` avoidance: **correct** — `<0.0001` bound used throughout.
- Failed runs: **none exist**; early-stopped runs are complete observations at their recorded endpoint, and
  this is disclosed.
- Ranks computed from unrounded values: **verified** — every rank I recomputed from full-precision means
  matches the released rank to 6 decimals.
- ISM null advertised in the abstract: **not re-raised as a §10.9 leak** (the §10.9 narrowing is explicit);
  my objection at S9-08 is solely about the statistical strength of the wording, which the narrowing
  expressly leaves in force.
