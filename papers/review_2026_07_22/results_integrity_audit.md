# Results-integrity, interpretation, and robustness audit — Stages 10 & 11

**Seat:** `s10-11_results_robust` (Stage 10 — results integrity, interpretation, internal
consistency; Stage 11 — robustness, sensitivity, ablation, alternative explanations)
**Governing prompt:** `papers/PAPER_REVIEW_PROMPT.md` §§1934–2081 (mandate), 1104–1148 (ticket
schema), 3160–3522 (DT-GSK evidence-locked profile), 3977–3997 (prohibited shortcuts)
**Package reviewed (verified in-repo, not from the prompt snapshot):** git HEAD
`45248eb31af7b01567c251f2a5da4f36e92d6030`; evidence release
`rel-2026-07-20-67d9345f9`; ablation release `abl-rel-2026-07-20`;
`papers/DT-GSK.pdf` / `papers/supplementary.pdf` / `papers/cover_letter.pdf` rebuilt 2026-07-22 17:48–17:49
**Date:** 2026-07-22 — read-only pass. No manuscript, code, or evidence file was modified.

---

## 0. Executive summary

Every headline number I re-derived from the released analysis CSVs **reproduces exactly**: the
CEC2017 Friedman mean ranks (2.88 / 2.50 / 2.21 / 2.34, overall 2.48), the 17-wins/7-ties/0-losses
Holm tally, the 15-of-24 global-Holm sensitivity, the CEC2011 loss to eGSK
(p_Holm = 4.2×10⁻²), the CEC2013 panel (2.41 / 3.38 / 2.61, overall 2.80), the class ranks, the
BCa rank intervals, the F26 descriptive cells, the runtime cells, and every robustness figure
quoted in §4.3.3. **Arithmetic integrity is not the problem.**

The problems are of three kinds:

1. **Two confirmed reader-facing defects in how the statistics are described** — a single paragraph
   of the statistical-protocol section states *both* that the headline table's effect size is the
   rank-biserial *r* **and** that it is A₁₂ (R2-S10-01), and the Friedman omnibus p-values printed
   for CEC2017 and CEC2013 are the **superseded pre-tie-correction values** while CEC2011 uses the
   corrected ones (R2-S10-02). Both survived every gate because the package's evidence-binding
   validator only checks PDF↔DOCX token *presence*, never CSV values (R2-S10-12).
2. **Two Stage-11 gaps that a Q1 reviewer will attack**: an entirely undisclosed
   population-size asymmetry (DT-GSK NP_init = 5·D vs a fixed NP = 100 for all six comparators —
   500 vs 100 at D = 100, exactly where the high-dimensional story lives, R2-S11-03), and the total
   absence of any parameter/hyperparameter sensitivity evidence for a method whose contribution is
   a *tiered parameter schedule*, with the absence itself undisclosed (R2-S11-04).
3. **One hidden adverse outcome**: a 22-hour, 51-run controlled re-execution on 2026-07-21 proved
   the six comparators' *scientific* columns are **not reproducible across producer commits**
   (3,772 differing rows; ATMALS-GSK ≈31 %, eGSK ≈29 % of runs). This is recorded only in the
   remediation ledger; the manuscript's sentence on exactly this topic still offers the opposite
   reassurance (R2-S10-05).

**Gate J (Result Integrity): CONDITIONAL FAIL** — on R2-S10-01, R2-S10-02 and R2-S10-05
(irreconcilable numeric/descriptive inconsistency in the headline inferential table; statistics
printed from a superseded release; an adverse reproducibility outcome not visible to the reader).
All three are text-only fixes; none requires a rerun or a new release.

**Gate K (Robustness & Mechanism Attribution): CONDITIONAL FAIL** — on R2-S11-03 and R2-S11-04
(a first-order alternative explanation for the central dimension-resolved result is neither
disclosed nor bounded; no parameter-sensitivity evidence exists and its absence is not stated).
The central *conclusion* is **stable** under every robustness variant actually run — DT-GSK's own
ordinals 1/2/1/1 are invariant across r01–r08, the endpoint variants, and the sign-flip
randomisation (0/24 decision changes). The failure is one of *attribution and disclosure*, not of
conclusion stability.

**Confirmation of the 2026-07-21/22 remediation (R-01…R-14).** I re-verified the items that touch
my stages. **R-05** (budget-crossing) is correctly closed: `tests/regression/test_budget_crossing_semantics.py`
exists and the disclosure at `papers/sections/performance.tex:164–178` is accurate. **R-06**
(release identity) is correctly closed: `validate_provenance_claims.py` exits 0 and the supplement
states the current release. **R-07** is correctly closed (gate green). **R-08** is correctly
closed — the abstract lists exactly C1–C3 and the ISM null is not counted as a fourth contribution.
**R-09** is correctly closed — the cover letter's byte-stability claim is narrowed to DT-GSK.
I found **no** residual oracle/§S6.7-study reference anywhere in the manuscript. One earlier ticket,
**M-027, was closed incompletely** — see R2-S10-01.

**Prompt staleness confirmed and recorded** — see R2-PROMPT-23.

---

## 1. What I verified as CORRECT (evidence, so the panel does not re-check it)

All values below were recomputed from `papers/analysis/rel-2026-07-20-67d9345f9/**` with pandas and
compared against the rendered PDF text.

| Manuscript statement | Source | Verdict |
|---|---|---|
| CEC2017 Friedman means 2.88/2.50/2.21/2.34, eGSK 2.29/2.62/2.69 | `friedman_ranks_cec2017_D*.csv` | CONFIRMED |
| Overall 2.48 (DT-GSK) / 2.96 (eGSK); = unweighted mean of the four | `friedman_ranks_cec2017_overall.csv`; (2.879310+2.500000+2.206897+2.344828)/4 = 2.482759 | CONFIRMED |
| 17 wins / 7 ties / 0 losses across 24 Holm cells | `wilcoxon_holm_cec2017_D{10,30,50,100}.csv` outcome column (3+5+5+4 wins) | CONFIRMED |
| Global-Holm sensitivity: 15 of 24 survive; the two lost are ATMALS-GSK@D10 and GSK@D30 | `global_holm_sensitivity_cec2017.csv` (`survives_global_holm`) | CONFIRMED |
| eGSK cells p_Holm 0.0035 / 0.199 / 1.0 / 0.795 | same | CONFIRMED |
| GSK@D100 p_raw 0.0323, p_Holm 0.0646 despite 20-0-9 | same; T15 | CONFIRMED |
| Rank gaps vs eGSK 1.36 / 0.21 / 0.41 / 0.34; CD = 1.673 | `nemenyi_cd_cec2017_D*.csv` (`critical_difference` = 1.672993) | CONFIRMED |
| "never Nemenyi-separable" also holds on CEC2011 (0.84 < 1.92) and CEC2013 (1.46/0.30/0.68 < 1.703) | `nemenyi_cd_cec2011.csv`, `nemenyi_cd_cec2013_D*.csv` | CONFIRMED |
| CEC2011: 3.36 vs 2.52; loss p_raw 9.5×10⁻³, p_Holm 4.2×10⁻²; GSK head-to-head 13-2-7, R⁺=159, R⁻=51 | `friedman_ranks_cec2011.csv`, `wilcoxon_holm_cec2011.csv`, `tables/T06.tex` | CONFIRMED |
| CEC2013 panel table (all 28 cells) and the 1st/3rd/1st profile | `friedman_ranks_cec2013_*.csv` | CONFIRMED |
| CEC2013 vs GSK: p_Holm 1.9e-4/3.1e-2/2.7e-3; W/T/L 24-2-2, 21-2-5, 24-2-2; R⁺/R⁻ 340/11, 286/65, 314/37 | `wilcoxon_holm_cec2013_D*.csv`, `tables/T14.tex` | CONFIRMED |
| Class ranks (hybrid 1.60/1.80/2.30; simple multimodal 2.07/3.29/2.29/1.71; composition 3.70/2.85/2.50/2.90) | `class_ranks_cec2017.csv` | CONFIRMED |
| BCa rank intervals [2.29,3.43] [2.07,3.10] [1.86,2.69] [1.90,2.83]; overlap with eGSK at D30/50/100 only | `tables/T16_bca.tex` | CONFIRMED |
| r01 median re-ranking: 21-4-4 → 17-10-2 vs eGSK@D10; APGSK/eGSK swap@D10; FDB/ATMALS swap@D50; D100 exact tie at 2.59 | `robustness_cec2017_r01_mean_vs_median.csv` | CONFIRMED |
| r04: GSK/FDB-AGSK ordinal swap at D30 under APGSK exclusion | `robustness_cec2017_r04_disputed_cell_exclusion.csv` rows 7/10 | CONFIRMED |
| r05: 11 paired-sig→unpaired-non-sig, 21 the other way, 0 sign reversals | `robustness_cec2017_r05_unpaired_companion.csv` cross-tab (7+4; 8+13; 0) | CONFIRMED |
| "two of its checks diverge" | `robustness_summary_cec2017.md` (r01, r04 = diverge) | CONFIRMED |
| Tie-correction C = 0.890 (9 tied functions) @D10, 0.979 @D30, 1.0 @D50/D100 | `friedman_ranks_cec2017_D*.csv` | CONFIRMED |
| F26@D30: 1.16e3 mean, 9.85e2 best, SD 7.5e1 smallest (next GSK 2.7e2), all comparator bests 2.00–3.00e2, only ATMALS higher at 1.32e3 | `descriptive_stats_cec2017_D30.csv` F26 rows | CONFIRMED |
| F26@D100: 4.09e3 below 4 comparators, above GSK 3.69e3 and eGSK 3.05e3 | `descriptive_stats_cec2017_D100.csv` | CONFIRMED |
| Runtime 4.93/13.04/23.30/41.59 s ±0.83/2.69/5.23/13.95; CEC2013 4.45–34.26; CEC2011 80.64 | `cost_cec2017.csv` | CONFIRMED |
| Convergence panel selection (D30 F3/F10/F12/F26 incl. the hard/weak case; D100 F1/F5/F12/F26) | `curve_selection_cec2017_D{30,100}.csv` | CONFIRMED (but see R2-S11-17) |
| Seed audit 70,813 rows / 0 mismatches | `papers/governance/seed_and_pairing_audit.md:31` | CONFIRMED |
| Convergence checkpoints: 7/7 algorithms, n_runs = 51, availability ok | `convergence_checkpoints_cec2017_D*.csv` | CONFIRMED |
| A₁₂ values 0.490 / 0.505 / 0.472 / 0.712 quoted in §4.3.3 | recomputed from `descriptive_stats_cec2017_D*.csv` → 0.4905 / 0.5054 / 0.4721 / 0.7122 | CONFIRMED (arithmetic); see R2-S10-01 for the labelling defect |

**Loss visibility on the primary suite is exemplary.** Every unfavourable CEC2017 cell I could find
in the release is stated in the main text *alongside* the favourable one: the losing eGSK
head-to-heads at D≥30, the non-significant D10 cells, the GSK@D100 non-significance, the
non-monotone rank trend, the composition-class weakness at D10, the r01/r04 divergences, and the
never-separable Nemenyi outcome. That is materially better than the norm for this literature and
should be preserved verbatim in revision.

---

## 2. Contradiction matrix

Authoritative version in **bold**.

| # | Locus A | Locus B | Nature | Authoritative | Ticket |
|---|---|---|---|---|---|
| 1 | `performance.tex:209–216` "the tabulated effect size is the matched-pairs rank-biserial correlation *r*" | `performance.tex:221–231` "The tabulated A₁₂ is computed over the 29 per-function mean errors"; `:361–363` "…win/tie/loss counts, **A₁₂ effect sizes**, and Holm decisions"; `:365–366` "The **A₁₂ column** is…" | Same paragraph/section asserts two different measures occupy the same table column | **`tables/T15.tex` — the column is `r` (rank-biserial)** | R2-S10-01 |
| 2 | `performance.tex:317,338` "p ≤ 2.6×10⁻⁸" (CEC2017); `:599` "p ≤ 2.3×10⁻³"; `:623,625,626` 3.3e-7 / 2.2e-3 / 9.2e-6 (CEC2013) | `performance.tex:196–263` "the Friedman statistic uses the tie-corrected rank variance that underlies the Iman–Davenport F"; `:530` CEC2011 F = 4.27, p = 6.0×10⁻⁴ (corrected) | Two suites print the **uncorrected** column, one prints the **corrected** column | **`friedman_ranks_*.csv` `p_value` (corrected)** | R2-S10-02 |
| 3 | `performance.tex:126–139` "only its run-level companion analyses **are** unavailable at those dimensions" | its own footnote: "subsequently recovered after the analysis freeze"; `supplementary.tex:214–218`, all three S1 captions (past tense, "recovered post-freeze") | Present-tense existence claim vs recovered state | **the supplement / footnote** | R2-S10-13 |
| 4 | `conclusions.tex:91–93` "A breakdown by function class shows this null holds even on the hybrid and composition functions" (no label); `introduction.tex:135` "the function-class analysis reveals no systematic advantage…" | `supplementary.tex:2063–2069` "we ask *post hoc* (**this analysis was not pre-registered**)"; caption "Exploratory; not part of the pre-registered isolation" | Exploratory result promoted to Conclusions/Introduction without its label; the D50-hybrid favourable lean (win-rate 0.70) that the supplement discloses is dropped | **the supplement + `phase_05/statistical_analysis_plan.md` §11** | R2-S10-06 |
| 5 | `performance.tex:288–303` and `:790–798` present per-class mean ranks with no exploratory label and no class-size caveat (unimodal n = 2) | `phase_05/statistical_analysis_plan.md:190` "pre-specified here as **exploratory and descriptive** … small class sizes acknowledged in captions"; §12 registry: AN-CLASS-2017 class = *exploratory* | Frozen SAP requirement not met in the manuscript | **the frozen SAP** | R2-S10-07 |
| 6 | `cover_letter.tex:55` — "best overall CEC2017 Friedman mean rank … (2.48 …)" with no adverse qualification | `main.tex:143–146` abstract states the D30 second place, the CEC2011 Holm-significant loss, and the non-separability | Cover letter omits every qualification the abstract carries | **the abstract** | R2-S10-09 |
| 7 | `conclusions.tex:66` "**Eleven** limitations" | `supplementary.tex:1179–1263` enumerates First…Eighth + one unnumbered block (9); `claims_evidence_matrix.csv` has LM-01…LM-05 (5) | Unsourced count | **the supplement enumeration** | R2-S10-15 |
| 8 | `performance.tex:753, 768–769` "…the isolated compute cost of the interaction-structure memory … (Section S6.7)" | Rendered supplement: **S6.5** = *ISM-Overlay Isolation* (primary locus, +57.3/+36.3/+30.3 %); **S6.7** = *Implementation Caveats* | Pointer resolves (S6.7 restates the figures) but targets the wrong section | **S6.5** | R2-S10-21 |
| 9 | `performance.tex:147–158` "their numerical identity across producer commits rests on the shared-kernel probes and code history" | `remediation_2026_07_18/decisions.md` Decision 7 amendment (2026-07-21): 3,772 scientific-column differences on a controlled re-run | Reassurance contradicted by direct evidence | **the 2026-07-21 experiment** | R2-S10-05 |
| 10 | `supplementary.tex:1231–1236` the self-init asymmetry "is most consequential at low dimension" | `_dt_core.py:151–152, 462–465` NP_init = 5·D vs `benchmarks/cec_reference_results/cec2017/*/run_config.json` `pop_size`/`NP_init` = **100** for all six comparators at every D | The largest mismatch (5×, in DT-GSK's favour) is at **D = 100**, not low D | **the run configs** | R2-S11-03 |
| 11 | `PAPER_REVIEW_PROMPT.md` §1.5 "73/80 fully closed … seven … remain open"; §10.7 RT-001 "IN PROGRESS … being brought into single-environment comparability by re-timing all six comparators" | `remediation_2026_07_18/ticket_status.csv` = 80/80 (70 closed_verified + 10 superseded_with_evidence); RT-001 closed via **Option 3 (DT-GSK-only fallback)** after Option 2 failed | Prompt snapshot predates the repo | **the repo** (§1.4 precedence) | R2-PROMPT-23 |

No contradiction was found between the abstract, introduction C1–C3, the conclusions, and the cover
letter on the *content* of the three contributions; on the ranks, W/T/L records, and p-values the
abstract, body, tables and conclusions agree with each other and with the CSVs.

---

## 3. Tickets

### R2-S10-01 — The headline inferential table's effect size is specified two contradictory ways in the rendered paper

```text
ticket_id: R2-S10-01
review_stage: 10
reviewer_role: R1 (T1-OPT) with T3-STAT
severity: Major
priority: P1
confidence: Confirmed
issue_type: statistics
manuscript_location: papers/sections/performance.tex:209-216, 221-231, 361-363, 365-368, 405-411, 426
  (rendered: DT-GSK.pdf §4.1 "Statistical protocol" and §4.2.3 "Statistical Analysis"; Table 14)
claim_id_or_artifact_id: TAB-T15 / AN-PW-2017-D10..D100
concise_issue: One paragraph of the statistical protocol states that Table 14's effect-size column
  is the matched-pairs rank-biserial r AND, nine lines later, that it is A12; §4.2.3 then twice
  calls it "the A12 column" and quotes four A12 values that are not in the table.
exact_evidence_or_observation:
  performance.tex:211-213 "because the across-function test is a matched-pairs Wilcoxon, the
    tabulated effect size is the matched-pairs rank-biserial correlation r = (R+ - R-)/(R+ + R-)"
  performance.tex:221-222 "The tabulated $A_{12}$ is computed over the 29 per-function mean errors"
  performance.tex:361-363 "Table~\ref{tab:wilcoxon-holm} reports ... win/tie/loss counts,
    $A_{12}$ effect sizes, and Holm decisions"
  performance.tex:365-366 "The $A_{12}$ column is computed over the 29 per-function means"
  papers/tables/T15.tex:5 and :22 -> column header is `$r$`; values +0.865 ... -0.057
  Rendered PDF (pdftotext -layout DT-GSK.pdf): line 1395 "the tabulated effect size is the
    matched-pairs rank-biserial correlation r"; line 1401 "The tabulated A12 is computed over the
    29 per-function mean"; line 1517 "The A12 column is computed over the 29 per-function means";
    Table 14 header renders "r Dec." in all four dimension blocks.
  Ticket M-027 (papers/governance/remediation_2026_07_18/ticket_status.csv:52) records the intended
    swap: "Table 8 shows the signed matched-pairs rank-biserial in place of A12 ... Prose and
    caption updated". The caption WAS updated; four prose sentences were NOT.
root_cause: M-027 swapped the table column (A12 -> r) and rewrote the caption, but the two
  §4.1 sentences and the two §4.2.3 sentences that describe the same column were left at their
  pre-swap wording; the paragraph now contains both the new and the superseded description.
scientific_or_editorial_justification: §10.7 requires the effect-size definition and direction to
  be verifiable and the frozen plan to name which measure is reported. A reader cannot determine
  which effect size the paper's central inferential exhibit carries, and cannot locate the
  "A12 column" the text tells them to read. The two measures also disagree in sign at D50
  (r = -0.002 favours eGSK; A12 = 0.505 favours DT-GSK), so the ambiguity is not cosmetic.
impact_on_validity_or_acceptance: No reported number is wrong, but a Q1 statistics reviewer who
  cross-reads §4.1, §4.2.3 and Table 14 will conclude the statistical reporting was not
  proof-read; combined with R2-S10-02 this is the strongest single rejection lever in the package.
required_correction: (a) Delete the superseded half of the §4.1 paragraph (performance.tex:221-231)
  and keep one statement: the tabulated effect size is the matched-pairs rank-biserial r; A12 is
  retained as an unpaired descriptive companion in the released workbooks. (b) In §4.2.3 replace
  "A12 effect sizes" with "matched-pairs rank-biserial effect sizes r" and rewrite the
  "The A12 column ..." sentence to describe r. (c) Either drop the four across-function A12 values
  (0.490, 0.505, 0.472, 0.712) or keep them explicitly labelled as a companion statistic computed
  over the 29 per-function means and NOT shown in Table 14 (see R2-S10-19 for their provenance).
acceptable_alternatives: Restore an A12 column to T15 (rejected by M-027 on width grounds) — then
  the caption must change back instead.
additional_evidence_needed: none.
dependencies: R2-S10-19 (machine-readable row for the four quoted A12 values).
expected_improvement: The paper's central table becomes self-describing; Gate J unblocks.
post_revision_verification: grep the rendered PDF and DOCX for "A_{12} column" / "A12 effect
  sizes" -> 0 hits; confirm Table 14 caption and the §4.1 sentence name the same measure;
  re-run validate_evidence_bindings.py and validate_cross_format_parity.py.
status: open
```

### R2-S10-02 — CEC2017 and CEC2013 omnibus p-values are the superseded pre-tie-correction values; CEC2011 uses the corrected ones

```text
ticket_id: R2-S10-02
review_stage: 10
reviewer_role: R1 / T3-STAT
severity: Major
priority: P1
confidence: Confirmed
issue_type: statistics
manuscript_location: papers/sections/performance.tex:317, 338 (CEC2017 body + Table 13 caption);
  :599 (Table 15 caption), :623, :625, :626 (CEC2013 body). Rendered in DT-GSK.pdf and DT-GSK.docx.
claim_id_or_artifact_id: AN-OMNI-2017-D10..D100; AN-OMNI-2013-D10/D30/D50
concise_issue: The manuscript prints the tie-UNCORRECTED Friedman/Iman-Davenport p-values for
  CEC2017 and CEC2013 while stating in §4.1 that the reported statistic is tie-corrected, and while
  printing the tie-CORRECTED statistic for CEC2011 — three suites, two different columns.
exact_evidence_or_observation:
  Released rel-2026-07-20-67d9345f9 (both columns are shipped per panel):
    cec2017 D10  p_value = 1.159690e-09   p_value_uncorrected = 2.576884e-08
    cec2017 D30  5.760225e-11             1.151976e-10
    cec2017 D50  6.763147e-11             6.763147e-11
    cec2017 D100 1.424078e-12             1.424078e-12
    cec2013 D10  5.321814e-08             3.264004e-07
    cec2013 D30  1.089721e-03             2.242258e-03
    cec2013 D50  2.908506e-06             9.212405e-06
    cec2011      p 6.01e-04, F 4.266899   (uncorrected: 2.160258e-03, F 3.668834)
  Manuscript: CEC2017 "p <= 2.6 x 10^-8"  == 2.576884e-08 == the D10 UNCORRECTED value
    (the corrected bound is 1.2 x 10^-9).
  Manuscript: CEC2013 "p = 3.3 x 10^-7 / 2.2 x 10^-3 / 9.2 x 10^-6" == exactly the three
    UNCORRECTED values (corrected: 5.3e-8 / 1.1e-3 / 2.9e-6).
  Manuscript: CEC2011 "F = 4.27, p = 6.0 x 10^-4" == the CORRECTED values.
  Provenance proof: the CEC2017/CEC2013 numbers are byte-identical to the SUPERSEDED releases
    rel-2026-07-16-78f075cb0 and rel-2026-07-10-262fc16c9, whose single `p_value` column predates
    the M-026 tie correction (verified by reading those bundles).
  §4.1 (performance.tex:250-253) states: "the Friedman statistic uses the tie-corrected rank
    variance that underlies the Iman-Davenport F".
  The CEC2013 caption bound "p <= 2.3 x 10^-3" matches NEITHER column (uncorrected max rounds to
    2.2e-3; corrected max is 1.09e-3).
root_cause: M-026 added the tie correction and the analysis was regenerated, but the prose
  p-values were carried over from the pre-M-026 release; only the CEC2011 numbers were refreshed.
scientific_or_editorial_justification: §10.3 (every empirical input resolves under the selected
  release; no silent fallback to prior tables) and §10.7 (a machine-readable row for every reported
  statistic). A reported statistic that comes from a superseded release, in a paper whose entire
  contribution C3 is evidence-lock discipline, is a self-inflicted wound.
impact_on_validity_or_acceptance: No decision changes — every omnibus is significant under both
  columns, and the manuscript already says so. But the specific numbers printed are not the
  release's primary values, the paper is internally inconsistent about which column it reports,
  and the CEC2013 caption bound is unsourced.
required_correction: Replace with the corrected column throughout, and make the bounds match:
  CEC2017 "p <= 1.2 x 10^-9" (both occurrences); CEC2013 body "p = 5.3 x 10^-8 / 1.1 x 10^-3 /
  2.9 x 10^-6" and caption "p <= 1.1 x 10^-3". Alternatively keep the uncorrected values but state
  explicitly, in §4.1 and both captions, that the printed omnibus p is the uncorrected form (this
  contradicts the current §4.1 sentence and is the weaker option).
acceptable_alternatives: Print both, as the released CSVs do.
additional_evidence_needed: none — both columns ship in every friedman_ranks_*.csv.
dependencies: R2-S10-12 (the gate that should have caught this).
expected_improvement: Every printed statistic resolves to the declared release's primary column.
post_revision_verification: For each of the 7 panels, assert the rendered p equals
  `p_value` (not `p_value_uncorrected`) at the printed precision; extend
  validate_evidence_bindings.py per R2-S10-12 so the check is mechanical.
status: open
```

### R2-S11-03 — Undisclosed 5× population-size asymmetry: an unexcluded alternative explanation for the high-dimensional result

```text
ticket_id: R2-S11-03
review_stage: 11
reviewer_role: R3 (T2-BENCH) with T1-OPT
severity: Major
priority: P1
confidence: Confirmed
issue_type: experimental-design
manuscript_location: papers/sections/performance.tex:98-125 (panel/pairing/seed-paired start);
  papers/build_prompt_phases/phase_03/parameter_table.tex:28 (NP_init = 5D);
  papers/sections/proposed_algorithm.tex:677-704 (Table tab:panel, "published reference constants");
  papers/supplementary.tex:1231-1236 (the asymmetry limitation)
claim_id_or_artifact_id: PR-06; LM-03; RS-01 (the headline dimension-resolved standing)
concise_issue: DT-GSK runs NP_init = 5*D (50 / 150 / 250 / 500 at D = 10/30/50/100) while all six
  comparators run a FIXED population of 100 at every dimension. The manuscript prints DT-GSK's 5D
  but never the comparators' 100, so the reader cannot see that at D = 100 DT-GSK starts with a
  5x larger population — precisely the tier that carries the "first at three of four dimensions"
  and "high-dimensional" narrative. No analysis bounds this confound.
exact_evidence_or_observation:
  src/gsk_family/optimizers/_dt_core.py:151-152 "pop_size: int | None = None  # If None, uses
    np_init_mult * dim" ; "np_init_mult: int = 5" ; :462-465 resolved_pop_size_init() returns
    np_init_mult * dim.
  benchmarks/cec_reference_results/cec2017/<alg>/run_config.json (the frozen evidence itself):
    gsk        pop_size = 100
    agsk       NP_init  = 100, min_pop_size = 12
    apgsk      NP_init  = 100, min_pop_size = 12
    fdb-agsk   NP_init  = 100, min_pop_size = 12
    atmals-gsk pop_size = 100
    egsk       pop_size = 100
    dt-gsk     (profile "pub" -> NP_init = 5D, N_min = 25 at D>=50 / 12 below)
  A repo-wide grep of papers/**/*.tex for the comparator population size returns nothing: the only
  NP stated anywhere in the manuscript or supplement is DT-GSK's own 5D
  (parameter_table.tex:28, notation_table.tex:43, proposed_algorithm.tex:339/354/367/399/759).
  supplementary.tex:1231-1236 asserts the initialization asymmetry "is most consequential at low
  dimension, where DT-GSK runs essentially the scaffold" — but at D = 10 DT-GSK has HALF the
  comparators' population (50 vs 100), and at D = 100 it has FIVE TIMES (500 vs 100).
root_cause: Each algorithm runs its own published/frozen configuration (a defensible protocol),
  but the resulting population-size asymmetry was never surfaced to the reader or bounded.
scientific_or_editorial_justification: §10.13 lists "mechanism explanations based only on final
  performance" and "invalid pairing" as hard rejection risks; Stage 11 requires alternative
  explanations to be excluded or named. Population size is the single most influential control
  parameter in DE/GSK-class algorithms at high dimension. "DT-GSK wins at D >= 50 because it
  scales its population with D while the comparators do not" is a complete, competing explanation
  for the headline pattern that the paper attributes to its dimension-tiered design. It is also
  partially conceded already: the Discussion (performance.tex:820-823) names "the raised population
  floor" as one of the D>=50 co-activating subsystems, but the raised FLOOR (N_min 12 -> 25) is a
  second-order effect next to the 5x initial-population difference, which is never mentioned.
impact_on_validity_or_acceptance: This is the objection I would expect a benchmarking-methodology
  reviewer to lead with. It does not invalidate any number, but it materially weakens the causal
  reading of the dimension-tiered thesis unless disclosed and argued.
required_correction: NO RERUN REQUIRED. (1) State the comparators' population setting explicitly
  in Table tab:panel (add a "population" column: 100 fixed for the six; 5D -> tier floor for
  DT-GSK) or in the "Panel, pairing, and seed-paired start" paragraph. (2) Correct the supplement's
  claim about where the asymmetry bites: the mismatch is against DT-GSK at D = 10 and in its favour
  at D >= 30, largest at D = 100. (3) Add one sentence to the limitations naming
  dimension-scaled-vs-fixed population as a competing explanation for the upper-tier standing that
  this study does not separate from the tiered control itself.
acceptable_alternatives: A matched-NP sensitivity cell (DT-GSK at NP_init = 100, or comparators at
  5D) on CEC2017 D100 would settle it empirically — but that is a new experiment and is explicitly
  out of scope under the no-rerun constraint. Disclosure is the required minimum.
additional_evidence_needed: none for the disclosure fix.
dependencies: none.
expected_improvement: Converts an unstated confound into a disclosed, bounded scope limit.
post_revision_verification: Confirm the comparator NP appears in the rendered main text; confirm
  the supplement no longer claims the asymmetry is worst at low dimension; confirm the limitation
  names the competing explanation.
status: open
```

### R2-S11-04 — No parameter/hyperparameter sensitivity evidence exists, and the absence is not disclosed

```text
ticket_id: R2-S11-04
review_stage: 11
reviewer_role: R3 (T2-BENCH) with T3-STAT
severity: Major
priority: P1
confidence: Confirmed
issue_type: experimental-design
manuscript_location: absent throughout — papers/main.tex, papers/sections/*.tex,
  papers/supplementary.tex (S5.4 "Limitations in Full", supplementary.tex:1171-1263)
claim_id_or_artifact_id: EG-006 / T-SENS; C2 (dimension-tiered adaptive scaffold)
concise_issue: The manuscript contains no parameter-sensitivity analysis of any kind, and does not
  tell the reader that none exists. Every "sensitivity" in the paper is an ANALYSIS-choice check
  (global Holm, tie band, endpoint), not a parameter check.
exact_evidence_or_observation:
  grep -in "sensitiv" over sections/*.tex, supplementary.tex, main.tex, cover_letter.tex returns
  exactly six hits, all analysis-choice: performance.tex:398/404 (global Holm),
  supplementary.tex:513/519 (post-hoc endpoint + sign-flip), :1265/:1286 (tie-band).
  papers/analysis/rel-2026-07-20-67d9345f9/table_to_csv_map.md:
    "T-SENS | disclosed-unavailable (EG-006; evidence-gap row in primary_stats/statistical_results.csv)"
  papers/governance/evidence_gap_register.md:145-174 (EG-006): "Desired claim: Parameter-sensitivity
    tables T21/T22 ... Why it matters: Sensitivity evidence pre-empts reviewer questions on
    parameter robustness ... Phase 7 resolution note (2026-07-11): the **omit** branch is exercised.
    No admissible parametric-sensitivity release exists ... the parameter-sensitivity tables
    T21/T22 (T-SENS) remain **unavailable**."
  The frozen configuration it would test is large and tier-dependent: NP_init = 5D, N_min = 12/25,
  p_senior 0.05/0.15/0.10, the tier boundaries D<20 / 20-49 / 50-99 / >=100 themselves, and the
  per-subsystem constants of supplementary Table tab:parameters-detail (ACE/ARGP windows, BSE caps,
  ISM decay/confidence 0.12/edge floor 1e-4, archive 1.5*NP_init cap 200, ...).
  Supplementary S5.3 (:1154-1157) states these values "were set against CEC2017 at the reported
  budget and run count" — i.e. selected on the suite that supplies the headline.
root_cause: EG-006 was closed by the "omit" branch (no sweep artifacts, no sweep runner); the
  omission was recorded in governance but never surfaced to the reader.
scientific_or_editorial_justification: Stage 11 requires "sensitivity to hyperparameters or
  thresholds" and forbids substituting ablation for sensitivity (§ "Sensitivity-versus-ablation
  distinction"). The paper's titular mechanism is a DIMENSION-TIERED parameter schedule; the tier
  boundaries and tier-resolved values are the contribution. Presenting them as a frozen artefact
  with no stability evidence, while also disclosing that they were selected on the headline suite,
  leaves the central design choice entirely unevidenced. Stage 10 additionally requires that
  "failed" outcomes be visible — an abandoned planned study is one.
impact_on_validity_or_acceptance: High reviewer-question probability. The honest reading is that
  the tiered schedule is a design proposal validated only end-to-end on its development suite.
required_correction: NO RERUN REQUIRED. Add an explicit limitation (main-text Limitations outline
  and supplement S5.4): "No parameter-sensitivity study accompanies this release: the tier
  boundaries and the tier-resolved constants were fixed once on the development suite and are
  reported as a frozen configuration, not as tuned optima; their stability under perturbation is
  untested and is left to future work." Mirror one clause in §4.1 where the frozen configuration
  is introduced.
acceptable_alternatives: A small, honestly-scoped sensitivity study (e.g. NP_init multiplier in
  {3,5,8} and the D>=50 tier boundary in {40,50,60} on CEC2017 D50/D100) would be the strong
  answer, but it is a new experiment and out of scope this cycle. Disclosure is the minimum.
additional_evidence_needed: none for the disclosure fix.
dependencies: interacts with R2-S11-03 (NP_init is one of the untested parameters).
expected_improvement: Removes a silent gap and pre-empts the most predictable reviewer request.
post_revision_verification: Confirm the limitation appears in both the main-text outline and S5.4
  and that it names parameter sensitivity explicitly.
status: open
```

### R2-S10-05 — Adverse post-freeze reproducibility outcome is invisible to the reader, and the manuscript's sentence on the same topic now reads as an unsupported reassurance

```text
ticket_id: R2-S10-05
review_stage: 10
reviewer_role: R1 / R4, with T4-SOFT
severity: Major
priority: P1
confidence: Confirmed
issue_type: reproducibility
manuscript_location: papers/sections/performance.tex:147-158 ("Environment and determinism");
  papers/supplementary.tex:1216-1223 (limitation "Sixth"); papers/main.tex:227-251 (Data Availability)
claim_id_or_artifact_id: CN-02; MT-11; LM-04
concise_issue: A controlled 51-run re-execution of all six comparators on 2026-07-21 established
  that the released comparator evidence is NOT bit-reproducible under the current code (3,772
  differing scientific-column rows; ATMALS-GSK ~31%, eGSK ~29% of runs). The manuscript does not
  disclose this, and its one sentence on comparator numerical identity across producer commits
  still presents "code history" as the basis for believing identity holds.
exact_evidence_or_observation:
  papers/governance/remediation_2026_07_18/decisions.md, "Amendment (2026-07-21) — Option 2
  attempted and failed": "It **failed the determinism gate**: the re-timed comparators did not
  reproduce the frozen scientific columns — **3,772 differences** across the six, from ~1 ULP
  (`gsk`, 88 diffs, D100 only) to large chaos-amplified shifts in the scipy/local-search members
  (`atmals-gsk` 1,832 diffs ~31% of runs, `egsk` 1,733 ~29%). Root cause: the comparator frozen
  evidence is from **2026-07-08 (commit `31c5a04c4`)** and is not bit-reproducible under the
  current code (`dc924dc48`)... a fresh re-run at the current commit reproduced tonight's re-run
  **30/30** ... while differing from the 2026-07-08 evidence only where the code drifted."
  Same text mirrored in remediation_2026_07_18/ticket_status.csv, ticket RT-001 (closed 2026-07-21).
  Denominator: 6 x 5,916 rows = 35,496; 3,772 differ (~10.6% overall).
  Manuscript, performance.tex:155-158: "The comparator-specific update kernels are \emph{not}
  covered by a numerical probe: their JIT state is recorded, but their numerical identity across
  producer commits rests on the shared-kernel probes and code history rather than on a direct hash."
  Nothing anywhere in the main text or supplement reports the failed re-execution.
root_cause: RT-001 was correctly re-scoped (Decision 7 Option 3) and its RUNTIME consequence was
  reconciled in the paper, but the incidental scientific-reproducibility finding it produced was
  never carried into the manuscript.
scientific_or_editorial_justification: Stage 10 requires "negative, null, failed, and adverse
  outcomes are visible". §10.7's recovery-versus-comparability disposition requires post-freeze
  facts of this kind to be disclosed rather than absorbed. Contribution C3 is
  "a controlled, reproducible family evaluation"; the affected comparator is eGSK — the one that
  carries the study's single Holm-significant loss, the D30 second place, and the never-separable
  finding. A reviewer who later reruns the harness and cannot reproduce the eGSK cells, having been
  told identity "rests on ... code history", will read the omission unfavourably.
impact_on_validity_or_acceptance: NO reported number changes — the frozen release remains the
  authoritative record and every statistic derives from it. The defect is disclosure, plus one
  sentence that the new evidence contradicts.
required_correction: NO RERUN REQUIRED — the experiment already exists. (1) Replace the
  performance.tex:155-158 sentence with the fact: e.g. "The comparator update kernels carry no
  numerical probe. A post-freeze re-execution of all six comparators under a later commit
  reproduced their scientific columns only approximately (3,772 of 35,496 CEC2017 rows differ;
  worst for the SciPy/local-search members at ~29-31% of runs), confirming that comparator cells
  are reproducible within a commit but not across producer commits; the frozen release is
  therefore the authoritative record for every reported comparator number." (2) Add the
  corresponding clause to supplement limitation "Sixth". (3) Confirm the Data Availability wording
  stays scoped to the ANALYSIS pipeline re-deriving statistics from the released per-run CSVs
  (it currently does — do not weaken it, and do not extend it to optimizer re-execution).
acceptable_alternatives: none — the finding exists and must be visible.
additional_evidence_needed: the retime run's diff artefact should be retained/cited (Decision 7
  amendment is sufficient as the governance citation).
dependencies: none.
expected_improvement: The determinism story becomes precise and defensible instead of reassuring.
post_revision_verification: Confirm the rendered main text states the cross-commit
  non-reproducibility with its scope; confirm no sentence anywhere asserts comparator numerical
  identity across commits.
status: open
```

### R2-S10-06 — A post-hoc, non-preregistered subset result is stated as a finding in the Conclusions and Introduction without its exploratory label, and its one favourable exception is dropped

```text
ticket_id: R2-S10-06
review_stage: 10
reviewer_role: R1 with T3-STAT
severity: Moderate
priority: P1
confidence: Confirmed
issue_type: statistics
manuscript_location: papers/sections/conclusions.tex:91-93; papers/sections/introduction.tex:135
claim_id_or_artifact_id: Path-1 subset (Supplement S6.6)
concise_issue: The Conclusions and Introduction assert the function-class breakdown of the ISM null
  as an established finding; the supplement labels the same analysis post hoc and not
  pre-registered, and discloses a favourable D50-hybrid lean that the main text omits.
exact_evidence_or_observation:
  conclusions.tex:91-93 "A breakdown by function class shows this null holds even on the hybrid
    and composition functions, so the aggregate null is not explained by the separable-problem
    subset." — no exploratory qualifier.
  introduction.tex:135 "the function-class analysis reveals no systematic advantage on the hybrid
    or composition categories (Supplementary Materials, Sections~S6.5 and S6.6)." — same.
  supplementary.tex:2065-2069 "we ask \emph{post hoc} (this analysis was not pre-registered)";
    table caption (:2085-2086) "Exploratory; not part of the pre-registered isolation."
  supplementary.tex:2107-2112 "The only favourable lean is on the $D=50$ hybrids (win-rate $0.70$,
    median per-function $\log_{10}$-error gain $+0.026$), and it reverses at $D=100$."
  phase_05/statistical_analysis_plan.md:190 pre-specifies class analysis as "exploratory and
    descriptive ... never converted to mechanism/causality wording".
root_cause: A supplement-only exploratory analysis was summarised upward without carrying its
  label or its exception.
scientific_or_editorial_justification: Stage 10 requires that "primary and exploratory findings are
  separated" and that "subgroup or class analyses are pre-specified or labeled exploratory". Note
  this is NOT a §10.9 leak question — the ISM null is deliberately advertised under the narrowing —
  it is a labelling and completeness question about a post-hoc subgroup analysis.
impact_on_validity_or_acceptance: A reviewer who reads S6.6 after the Conclusions will see an
  exploratory result presented confirmatorily and one directional exception dropped.
required_correction: In both loci, add "an exploratory, post-hoc breakdown" (or equivalent) and
  soften "shows this null holds" to "does not reveal a class where the memory helps (the only
  favourable lean, the D=50 hybrids, reverses at D=100)". Keep the existing "not a demonstration
  that none exists" framing.
acceptable_alternatives: Drop the class breakdown from the Conclusions/Introduction entirely and
  leave it in S6.6.
additional_evidence_needed: none.
dependencies: R2-S10-07 (same labelling class).
expected_improvement: Exploratory/confirmatory boundary restored in the two most-read sections.
post_revision_verification: Confirm both sentences carry the exploratory label and the D50-hybrid
  exception; confirm no causal wording was introduced.
status: open
```

### R2-S10-07 — The CEC2017 function-class analysis appears in the main text without the exploratory label and class-size caveat the frozen analysis plan mandates

```text
ticket_id: R2-S10-07
review_stage: 10
reviewer_role: R1 with T3-STAT
severity: Moderate
priority: P1
confidence: Confirmed
issue_type: statistics
manuscript_location: papers/sections/performance.tex:288-303 (§4.2.1) and :790-798 (§4.7 "By function class")
claim_id_or_artifact_id: AN-CLASS-2017
concise_issue: The per-class mean ranks are presented as ordinary results; the frozen SAP
  pre-specifies them as exploratory and descriptive with class sizes acknowledged, and the released
  artifact records them as exploratory. Neither label appears in the manuscript.
exact_evidence_or_observation:
  phase_05/statistical_analysis_plan.md:190 (§11 "Function-class analysis (exploratory; RQ4 partial)"):
    "pre-specified here as **exploratory and descriptive** (per-class mean ranks and W/T/L only;
    no per-class inference, avoiding micro-family multiplicity); small class sizes acknowledged in
    captions; never converted to mechanism/causality wording"
  phase_05/statistical_analysis_plan.md:210 registry: "AN-CLASS-2017 | Exploratory per-class
    descriptive ranks/W/T/L on verified CEC2017 categories | exploratory"
  primary_stats/statistical_results.csv, AN-CLASS-2017 rows: test = "none (exploratory descriptive;
    no per-class inference)"; interpretation = "exploratory; W/T/L vs dt-gsk=..."
  table_to_csv_map.md: "AN-CLASS-2017 | cec2017/class_ranks_cec2017.csv (exploratory)"
  performance.tex:288-303 and :790-798: no "exploratory", no class-size note. Class sizes are
  n = 2 (unimodal), 7, 10, 10 — the unimodal class is a 7-way tie at 4.000 at D10 and is silently
  omitted from the narrative.
  The analysis is prose-only (no exhibit), so the SAP's "acknowledged in captions" cannot be
  satisfied as written.
root_cause: The exploratory status lives in the plan and the CSV but was not carried into the prose.
scientific_or_editorial_justification: Stage 10 explicitly checks that class analyses are
  pre-specified or labelled exploratory; §10.7 requires the frozen plan's dispositions to hold.
impact_on_validity_or_acceptance: Moderate. The Discussion already hedges ("stated here as
  plausibility, not as a measured component contribution"), which limits the damage.
required_correction: Add one clause at the head of the §4.2.1 class paragraph: "A pre-specified
  exploratory, descriptive class breakdown (no per-class inference; classes of 2/7/10/10
  functions) shows ...", and repeat the "exploratory" qualifier once in §4.7.
acceptable_alternatives: Promote the class ranks to a small labelled table so the SAP's caption
  requirement is literally satisfiable.
additional_evidence_needed: none.
dependencies: R2-S10-06.
expected_improvement: The frozen plan and the manuscript agree on the analysis's status.
post_revision_verification: grep the rendered PDF for "exploratory" within the class paragraphs.
status: open
```

### R2-S10-08 — CEC2013 loss-visibility gap: the suite's "first place" cells rest on 3-of-6 and 1-of-6 significant pairwise tests, and the six-comparator matrix appears nowhere

```text
ticket_id: R2-S10-08
review_stage: 10
reviewer_role: R1 with T3-STAT
severity: Moderate
priority: P2
confidence: Confirmed
issue_type: evidence
manuscript_location: papers/sections/performance.tex:621-646 (§4.4); papers/supplementary.tex:391-453 (S2.3)
claim_id_or_artifact_id: AN-PW-2013-D10/D30/D50; AN-RANKAGG-2013-OVERALL
concise_issue: The CEC2013 section reports the favourable rank ordering and the DT-GSK-vs-GSK
  head-to-heads, and discloses the D30 third place, but never states that at D10 only three of six
  and at D50 only ONE of six pairwise Holm tests are significant. The six-comparator CEC2013
  Wilcoxon-Holm matrix is in neither the main text nor the supplement.
exact_evidence_or_observation:
  wilcoxon_holm_cec2013_D10.csv p_holm: gsk 0.000187 (win), agsk 0.2409, apgsk 0.2409,
    fdb-agsk 0.2409, atmals-gsk 0.001727 (win), egsk 0.001727 (win)  -> 3 of 6 significant.
  wilcoxon_holm_cec2013_D50.csv p_holm: gsk 0.002741 (win), agsk 0.0617, apgsk 0.0617,
    fdb-agsk 0.0617, atmals-gsk 0.2680, egsk 0.4349                  -> 1 of 6 significant.
  Manuscript, performance.tex:621-626: "at $D = 10$, DT-GSK leads with mean rank 2.41 ...;
    at $D = 50$ it leads again with 2.61" — no pairwise-significance qualification.
  Supplement S2.3 typesets only T14 (DT-GSK vs GSK). S2.1 states the panel-wide six-comparator
  inference "is in the main paper" — true for CEC2017, false for CEC2013.
  Contrast with CEC2011, where all six pairwise outcomes ARE given (performance.tex:542-548).
root_cause: CEC2013 is a "second comparison suite", so its detail was thinned; the thinning removed
  the unfavourable-cell visibility rather than only the bulk.
scientific_or_editorial_justification: §10.7 loss-visibility parity — "Every unfavorable
  inferential cell material to a headline ... must be stated alongside — not after — the favorable
  cells it qualifies." The CEC2013 overall first place (2.80) is quoted in the Conclusions and is
  one of the two suites on which the "best on two of three suites" statement rests.
impact_on_validity_or_acceptance: Moderate. The paper's own standard (applied rigorously to
  CEC2017 and CEC2011) is not met on CEC2013.
required_correction: Add one sentence to §4.4: "The CEC2013 first places are rank-based: of the six
  Holm-corrected pairwise tests, three are significant at D = 10 (GSK, ATMALS-GSK, eGSK) and one at
  D = 50 (GSK); the remaining cells show no significant difference." Optionally add the
  six-comparator CEC2013 matrix to S2.3, matching the CEC2017 treatment.
acceptable_alternatives: State the counts only, without the table.
additional_evidence_needed: none — the CSVs exist.
dependencies: none.
expected_improvement: Loss-visibility parity across all three suites.
post_revision_verification: Confirm the rendered §4.4 states the significant-cell counts at D10 and D50.
status: open
```

### R2-S10-09 — The cover letter states the headline rank with none of the adverse qualifications the abstract carries

```text
ticket_id: R2-S10-09
review_stage: 10
reviewer_role: R1 / ECB
severity: Moderate
priority: P2
confidence: Confirmed
issue_type: claim-scope
manuscript_location: papers/cover_letter.tex:55 (rendered cover_letter.pdf p.1)
claim_id_or_artifact_id: RS-01 NARROWED; RS-10; LM-01
concise_issue: The cover letter's opening claim — best overall CEC2017 Friedman mean rank, 2.48,
  eGSK second at 2.96 — is stated without the D = 30 second place, the CEC2011 second place with
  its Holm-significant loss, or the never-Nemenyi-separable finding, all of which the abstract
  states in the adjacent sentence.
exact_evidence_or_observation:
  cover_letter.tex:55 "To our knowledge, DT-GSK attains the best overall CEC2017 Friedman mean rank
    on the seven-algorithm GSK-family panel (2.48 ... eGSK is second at 2.96), evaluated under a
    release-locked protocol..." — the letter's only qualifications concern the ISM null and the
    within-family scope; no comparative loss is mentioned anywhere in the 2-page letter.
  main.tex:143-146 (abstract) "It is second behind eGSK at $D = 30$ and on CEC2011 (a
    Holm-significant loss), and the two are never Nemenyi-separable."
  Stage 10's contradiction matrix explicitly includes the cover letter.
root_cause: The letter was written to sell the contribution and inherited the headline without the
  bound the abstract applies to it.
scientific_or_editorial_justification: §10.7 loss-visibility parity and §4.6 honest interpretation.
  An editor triaging on the cover letter alone receives a materially less-qualified claim than the
  paper makes. The letter is otherwise commendably transparent (it volunteers the ISM null and the
  unresolved basis question), which makes the asymmetry more conspicuous, not less.
impact_on_validity_or_acceptance: Editorial-trust risk rather than scientific error.
required_correction: Add one clause after the rank claim: "— second at D = 30 and, on the
  real-world CEC2011 suite, second behind eGSK with a Holm-significant deficit; the two are never
  separable by the Nemenyi critical difference."
acceptable_alternatives: none material.
additional_evidence_needed: none.
dependencies: none.
expected_improvement: Cover letter, abstract and body state the same bounded claim.
post_revision_verification: Diff the letter's headline sentence against the abstract's qualification set.
status: open
```

### R2-S10-10 — The BCa rank-stability intervals have no released CSV or machine-readable row; their generator defaults to a superseded release and uses a second, differently-constructed seed scheme

```text
ticket_id: R2-S10-10
review_stage: 10
reviewer_role: R1 / T3-STAT
severity: Moderate
priority: P2
confidence: Confirmed
issue_type: reproducibility
manuscript_location: papers/sections/performance.tex:429-440 (four DT-GSK intervals quoted);
  papers/supplementary.tex:455-509 (Table tab:bca-ci, 28 intervals); papers/tables/T16_bca.tex
claim_id_or_artifact_id: TAB-T16-BCA
concise_issue: The rank-stability intervals are reported in both documents but are not in the
  released analysis bundle: no CSV holds them, statistical_results.csv has no row for them, and the
  exhibit map points T-BCA at a different quantity (per-function mean-difference CIs).
exact_evidence_or_observation:
  papers/analysis/rel-2026-07-20-67d9345f9/table_to_csv_map.md:
    "T-BCA | cec2017/bca_ci_cec2017_D{10,30,50,100}.csv + cec2017/headline_bca.csv"
    — those files hold per-(function, comparator) mean-difference CIs (columns suite, dimension,
    function, comparator, n_runs, mean_diff, ci_low, ci_high, B, seed_scheme, availability),
    NOT per-(algorithm, dimension) rank CIs.
  primary_stats/statistical_results.csv: 1,250 rows carry a CI; ALL belong to AN-EFF-2017/2013/2011
    (unit_of_analysis = run, resampling_unit = "paired runs within function",
    seed = SeedSequence([20240620, suite, dim, func, comparator])). A search for
    ci_low in [2.28,2.30] and ci_high in [3.42,3.44] (the printed DT-GSK D10 interval) returns 0 rows.
  papers/scripts/generate_t16_bca.py:50  RELEASE_ID = os.environ.get("GSK_REL_ID",
    "rel-2026-07-16-78f075cb0")   <- SUPERSEDED release as the default
  same file, docstring lines 11-14 names a THIRD release ("rel-2026-07-10-262fc16c9") as the
    "sole admissible" source.
  same file:76 BASE_SEED = 20260422 ; :172 rng = np.random.default_rng(BASE_SEED + dim*7 + i)
    — an ad-hoc integer seed, versus the entropy-list SeedSequence construction used for every
    other bootstrap in the release.
  Mitigating fact I verified: descriptive_stats_cec2017_D*.csv are BYTE-IDENTICAL between
    rel-2026-07-16-78f075cb0 and rel-2026-07-20-67d9345f9 (sha256 db7e7c46.., 833d870c..,
    d1e47ba7.., b4a9c54f..), so the printed intervals are numerically unaffected by the stale default.
root_cause: T16_bca is generated outside phase6_run_analysis.py and was never wired into the
  release's CSV/registry emission.
scientific_or_editorial_justification: §10.7 requires "a machine-readable row for every reported
  statistic (Appendix A.7 schema)" and warns specifically about "two contradictory seed
  constructions in the frozen artifacts". §10.11 requires table generators to read only the
  controlled analysis area recorded in project_configuration.md.
impact_on_validity_or_acceptance: The intervals are correct as printed but are the one class of
  reported statistic a reader cannot re-derive from the release without re-running a script whose
  default points elsewhere.
required_correction: (1) Emit the 28 rank-stability intervals as a CSV in the release directory and
  as AN-RANKCI-2017 rows in statistical_results.csv (n_resamples = 10000, resampling_unit =
  "per-function midranks within dimension", seed scheme recorded verbatim). (2) Correct
  table_to_csv_map.md's T-BCA entry to point at that file. (3) Set the generator's default
  RELEASE_ID to rel-2026-07-20-67d9345f9 and fix its docstring. (4) Document the two seed
  constructions and why they differ, or unify on the SeedSequence form.
acceptable_alternatives: If no new file may be added to the frozen release, record the intervals
  and their seed scheme in the supplement's reproducibility appendix (S5.10) instead.
additional_evidence_needed: none.
dependencies: R2-S10-24 (same stale-default pattern in six other scripts).
expected_improvement: Every reported statistic resolves to a machine-readable row.
post_revision_verification: Re-run generate_t16_bca.py with no environment override and confirm it
  reads the current release and reproduces T16_bca.tex byte-identically.
status: open
```

### R2-S11-11 — Component-claim-to-design gap: the only scaffold element claimed as original (ARGP) is a pre-specified exclusion from every ablation design

```text
ticket_id: R2-S11-11
review_stage: 11
reviewer_role: R3 (T2-BENCH) with T1-OPT
severity: Moderate
priority: P2
confidence: Confirmed
issue_type: experimental-design
manuscript_location: papers/sections/introduction.tex:101-112 (contribution C2);
  papers/supplementary.tex:1843-1848 and :1963-1976 (S6.1 exclusions, S6.4 bounds)
claim_id_or_artifact_id: MT-02..MT-07 (C2); X-ABL-01
concise_issue: C2 highlights ARGP as the one mechanism the authors "did not find ... among the
  surveyed GSK variants", yet ARGP, the final polish, and the deep-stall restart are pre-specified
  exclusions from the scaffold remove-one matrix, so ARGP has no direct component evidence in any
  design in the package.
exact_evidence_or_observation:
  introduction.tex:110-112 "ACE, NLPSR, BSE, the archive, and the restart modify cited antecedents;
    we did not find ARGP's acceptance-rate-gated arm-freezing rule among the surveyed GSK variants."
  supplementary.tex:1843-1848 "Three further frozen flags are prespecified exclusions from this
    matrix --- the ARGP pool-pruning control, the ISM-dependent final polish ..., and the deep-stall
    restart ... --- and no contribution of any sign is claimed for those three from this scaffold matrix."
  supplementary.tex:1969-1971 (S6.4 (iv)) repeats the bound.
  The ISM-overlay design (S6.5) toggles only ISM, the adaptive confidence gate, and the final polish
    — ARGP is absent there too.
root_cause: The ablation matrix was scoped to six toggles for statistical-family reasons; ARGP was
  excluded on dependency grounds, but the contribution bullet still foregrounds it.
scientific_or_editorial_justification: Stage 11's component-claim-to-design matrix: the design here
  is "no direct component evidence" for ARGP, which supports no utility claim of any kind. C2 as
  written is a NOVELTY claim, not an efficacy claim, so it is defensible — but the asymmetry
  (the one element singled out as new is the one with no evidence) is exactly what a
  benchmarking reviewer probes, and §10.13 lists "ablation design that cannot identify SGSM or
  dependent mechanisms" as a rejection risk.
impact_on_validity_or_acceptance: Moderate; fully mitigable by wording.
required_correction: In C2, immediately after the ARGP sentence, add the scope bound already stated
  in the supplement: "ARGP, the final polish, and the deep-stall restart are pre-specified
  exclusions from the supplementary component matrix; ARGP is offered as a design element, not as
  an evidenced contributor." (No new experiment; this is a disclosure alignment.)
acceptable_alternatives: Move the ARGP novelty statement out of the contribution bullet into the
  method section.
additional_evidence_needed: none.
dependencies: none.
expected_improvement: The contribution bullet's evidential status matches the ablation design.
post_revision_verification: Confirm C2 carries the exclusion bound in the rendered PDF.
status: open
```

### R2-S10-12 — The package's evidence-binding gate cannot detect a stale statistic; it checks PDF↔DOCX token presence only

```text
ticket_id: R2-S10-12
review_stage: 10
reviewer_role: R4 / T4-SOFT
severity: Moderate
priority: P2
confidence: Confirmed
issue_type: production
manuscript_location: papers/scripts/validate_evidence_bindings.py:1-36
claim_id_or_artifact_id: Gate infrastructure behind every "% BIND:" annotation
concise_issue: The validator that the package treats as the number-integrity gate verifies only
  that each BIND-annotated numeric token appears in BOTH rendered formats. It never opens the
  released analysis CSVs, so any number that is internally consistent across PDF and DOCX passes
  even when it contradicts the declared release.
exact_evidence_or_observation:
  validate_evidence_bindings.py docstring: "This validator extracts every numeric token from the
    visible text those BIND comments annotate and checks the token appears identically in BOTH
    rendered formats ... Exit 0 when every extracted number is found in both formats, else 2."
  Run on the current package: "BIND comments scanned : 321 / numeric tokens checked: 825 /
    found in both formats : 825 / FAIL : 0".
  The stale omnibus p-values of R2-S10-02 are among the 825 tokens and PASS.
root_cause: The gate's contract is cross-format parity, not source fidelity; no other gate closes
  the loop to the CSVs.
scientific_or_editorial_justification: §10.3/§10.11 require exhibits and prose to be regenerated
  from authoritative analysis outputs. Without a source-resolving check, that requirement is
  enforced only by hand.
impact_on_validity_or_acceptance: Process risk. It is the proximate cause of R2-S10-02 surviving
  three convergence rounds.
required_correction: Extend the validator (or add a companion) so that each BIND whose annotation
  names an analysis ID or a release CSV resolves the annotated token against that CSV at the
  printed precision, failing on mismatch. At minimum, add a targeted check for the seven Friedman
  panels' p-values and the T15/T16/T14/T06 cells.
acceptable_alternatives: A one-off manual reconciliation table checked into governance, plus a
  documented statement that the automated gate does not cover source fidelity.
additional_evidence_needed: none.
dependencies: R2-S10-02.
expected_improvement: Stale-statistic class of defect becomes mechanically detectable.
post_revision_verification: Prove the extended check RED on the current (pre-fix) p-values and
  GREEN after R2-S10-02 is applied.
status: open
```

### R2-S10-13 — Present-tense APGSK unavailability claim contradicted by its own footnote

```text
ticket_id: R2-S10-13
review_stage: 10
reviewer_role: R1 / T3-STAT
severity: Minor
priority: P2
confidence: Confirmed
issue_type: evidence
manuscript_location: papers/sections/performance.tex:126-139
claim_id_or_artifact_id: APGSK-GAP
concise_issue: "only its run-level companion analyses are unavailable at those dimensions"
  (present tense) is immediately contradicted by the attached footnote, which records the
  post-freeze recovery.
exact_evidence_or_observation:
  performance.tex:133-134 "...only its run-level companion analyses are unavailable at those
    dimensions." followed by the footnote "These run-level records were subsequently recovered
    after the analysis freeze ... they reproduce the frozen APGSK summaries exactly."
  Every other locus is correctly past-tense: performance.tex:368-372 ("were missing at analysis
    freeze and recovered only afterwards"); supplementary.tex:214-218 and the three S1 captions
    ("recovered post-freeze, values unchanged; never imputed").
root_cause: One sentence not updated when the recovery disclosure was added.
scientific_or_editorial_justification: §10.7 recovery-versus-comparability disposition: statements
  that recovered seed-deterministic quantities "are disclosed-unavailable" are false existence
  claims. The adjacent footnote is the sanctioned disclosure, which is why this is Minor and not
  Major — but the sentence itself should not need the footnote to be true.
impact_on_validity_or_acceptance: Low.
required_correction: "...only its run-level companion analyses were unavailable at those dimensions
  when the analysis was frozen." (one-word tense change plus clause).
acceptable_alternatives: none needed.
additional_evidence_needed: none.
dependencies: none.
expected_improvement: Removes a self-contradicting sentence/footnote pair.
post_revision_verification: grep the rendered main text for "are unavailable" near APGSK -> 0 hits.
status: open
```

### R2-S10-14 — Unmeasured decomposition of DT-GSK's wall-clock into subsystem bookkeeping

```text
ticket_id: R2-S10-14
review_stage: 10 / 11
reviewer_role: R3
severity: Minor
priority: P2
confidence: Confirmed
issue_type: claim-scope
manuscript_location: papers/sections/performance.tex:747-751
claim_id_or_artifact_id: AN-COST-2017; MT-08
concise_issue: The runtime paragraph attributes DT-GSK's absolute per-run cost to "the bookkeeping
  cost of its scaffold and structure-memory subsystems on top of the unchanged GSK core", but the
  same subsection states that comparator timings are not comparable and are not tabulated — so no
  GSK reference time is admissible, and the decomposition is asserted rather than measured.
exact_evidence_or_observation:
  performance.tex:747-750 "DT-GSK's per-run time scales with dimension, from 4.93~s at $D = 10$ to
    41.59~s at $D = 100$ --- the bookkeeping cost of its scaffold and structure-memory subsystems
    on top of the unchanged GSK core."
  performance.tex:741-744 "The comparator timings were collected in a separate measurement session,
    so we do not tabulate a cross-algorithm wall-clock comparison".
  The only measured subsystem cost in the package is the ISM overhead (+57.3/+36.3/+30.3 %,
    supplement S6.5/S6.7); no scaffold-level timing decomposition exists (supplement limitation
    "Eighth" concedes: "the evidence-bearing runs carry no component-level evaluation ledger").
root_cause: Interpretive gloss inherited from the pre-Decision-7 comparative framing.
scientific_or_editorial_justification: §4.6 — do not describe association as measurement. The
  paper is otherwise scrupulous here.
impact_on_validity_or_acceptance: Low.
required_correction: "...41.59 s at D = 100. The added cost is bookkeeping rather than extra
  objective evaluations (Section 3); its decomposition across subsystems is not measured here,
  and only the interaction-structure memory's isolated share is quantified (Supplementary Material)."
acceptable_alternatives: none needed.
additional_evidence_needed: none.
dependencies: none.
expected_improvement: Claim matches the measurement.
post_revision_verification: Confirm the rendered sentence no longer attributes the total to named subsystems.
status: open
```

### R2-S10-15 — "Eleven limitations" is not traceable to any enumeration

```text
ticket_id: R2-S10-15
review_stage: 10
reviewer_role: R1
severity: Minor
priority: P2
confidence: Confirmed
issue_type: writing
manuscript_location: papers/sections/conclusions.tex:66; papers/supplementary.tex:1179-1263 (S5.4)
claim_id_or_artifact_id: LM-01..LM-05
concise_issue: The Conclusions assert a specific count that neither the supplement's enumeration
  nor the claims matrix supports.
exact_evidence_or_observation:
  conclusions.tex:66 "Eleven limitations bound these findings, stated in full with their numeric
    evidence in the Supplementary Material, Section~S5."
  supplementary.tex S5.4 enumerates First, Second, Third, Fourth, Fifth, Sixth, Seventh, Eighth,
    then an unnumbered "Beyond these, the statistical scope is itself bounded" — 9 blocks (the
    "Eighth" block itself contains three attribution gaps, and "Seventh" contains two items, so the
    count depends entirely on the partition chosen).
  papers/governance/claims_evidence_matrix.csv contains LM-01..LM-05 only (5 limitation claims).
  The supplement also asserts the S5.4 text is "the wording of the conclusions ... moved rather
  than rewritten", which is inconsistent with the Conclusions carrying a count the moved text does
  not use.
root_cause: A hand-maintained count that drifted from the enumeration.
scientific_or_editorial_justification: Stage 10 — every reported quantity, including a count, must
  map to a source.
impact_on_validity_or_acceptance: Low, but trivially checkable by a reviewer.
required_correction: Either number the supplement's limitations explicitly 1..11 to match, or
  replace "Eleven limitations" with "Several limitations" / "The limitations".
acceptable_alternatives: none.
additional_evidence_needed: none.
dependencies: none.
expected_improvement: Count is either sourced or removed.
post_revision_verification: If a number is kept, count the supplement's numbered items and assert equality.
status: open
```

### R2-S11-17 — The featured D = 100 convergence panel shows no adverse case although one exists at that dimension

```text
ticket_id: R2-S11-17
review_stage: 11
reviewer_role: R3 / T5-WRITE
severity: Minor
priority: P3
confidence: Confirmed
issue_type: exhibit
manuscript_location: papers/sections/performance.tex:721-732 (Figure fig:conv-cec2017-d100 caption)
claim_id_or_artifact_id: AN-CONV-2017-D100
concise_issue: §10.8 requires "one difficult or adverse case must be visible". The D = 30 panel
  satisfies this (F26, hard/weak, explicitly flagged). The D = 100 panel's four functions are
  easy/strong, easy/strong, hard/comparable, hard/comparable — no adverse case — even though F28 is
  classified weak at D = 100. The caption does not say so.
exact_evidence_or_observation:
  curve_selection_cec2017_D100.csv: F1 easy/strong (selected), F5 easy/strong (selected),
    F12 hard/comparable (selected), F26 hard/comparable (selected);
    F28 composition / easy / **weak** — not_selected.
  curve_selection_cec2017_D30.csv: F26 hard/**weak** — "priority_1_(hard,weak)", selected.
  performance.tex:724-730 (D100 caption) lists the four functions with no note that the panel
    contains no unfavourable case at this dimension.
root_cause: The selection rule is prespecified and outcome-blind (correctly, and I verified it is
  followed exactly); at D = 100 the rule's priority ordering happened to select no weak cell.
scientific_or_editorial_justification: The rule's integrity is not in question; the reader's view
  is. The paper explicitly advertises the D = 30 panel as "deliberately includ[ing] an unfavorable
  case", which invites the inference that both featured panels do.
impact_on_validity_or_acceptance: Low — the complete per-function grids are in S3.
required_correction: Add one clause to the D = 100 caption: "the prespecified rule selects no
  DT-GSK-weak function at this dimension (F28 is the only weak cell at D = 100 and appears in the
  complete grid, Supplementary Material S3)."
acceptable_alternatives: none needed.
additional_evidence_needed: none.
dependencies: none.
expected_improvement: The adverse-case guarantee is stated per panel rather than implied.
post_revision_verification: Confirm the caption clause and that F28@D100 appears in the S3 grid.
status: open
```

### R2-S10-18 — Two robustness observations not carried into the manuscript's summary

```text
ticket_id: R2-S10-18
review_stage: 11
reviewer_role: R3 / T3-STAT
severity: Minor
priority: P3
confidence: Confirmed
issue_type: statistics
manuscript_location: papers/sections/performance.tex:483-508 ("Robustness of the rank statements")
claim_id_or_artifact_id: AN-ROB-2017-03 (LOFO); AN-ROB-2017-04 variant v2b
concise_issue: (a) The manuscript says "two of its checks diverge" and attributes comparator-order
  instability to r01/r04 only; leave-one-function-out (r03) also flips comparator ordinals at two
  dimensions. (b) The r04 battery contains a second, undisclosed variant (eGSK excluded) under
  which DT-GSK becomes first at D = 30 — a favourable divergence, likewise unreported.
exact_evidence_or_observation:
  robustness_cec2017_r03_lofo_friedman.csv, verdict = "diverge": gsk@D30 and fdb-agsk@D30
    (ordinal_change_omissions "F5;F7;F8;F10;F11;F14;F21;F23;F25"); gsk@D50 and agsk@D50
    (11-12 omissions each). DT-GSK's own ordinal is stable at every dimension ("none").
  robustness_summary_cec2017.md scores r03 "agree" because its criterion is DT-GSK's ordinal only,
    which is why the manuscript's "two diverge" count is defensible as written.
  robustness_cec2017_r04_disputed_cell_exclusion.csv rows 28-34 (variant v2b_egsk_excluded, D30):
    dt-gsk mean_rank_variant 1.913793, ordinal_variant 1 (from ordinal 2 in the primary).
  The manuscript reports only the apgsk-excluded variant of r04.
root_cause: Summary criteria are DT-GSK-centric; the manuscript inherits them.
scientific_or_editorial_justification: §10.7 robustness-divergence disclosure. Neither omission
  favours the paper improperly — (b) is favourable to DT-GSK and its omission is conservative —
  but "panel orderings between comparators are not fully robust" should cite all three checks.
impact_on_validity_or_acceptance: Low.
required_correction: Extend the sentence to "...three of its checks (median re-ranking,
  disputed-cell exclusion, and leave-one-function-out) move comparator orderings, while DT-GSK's
  own ordinals are invariant in every variant", or state explicitly that the divergence count is
  scored on DT-GSK's ordinal position.
acceptable_alternatives: Add one line noting the eGSK-excluded variant and its (favourable) result,
  for completeness.
additional_evidence_needed: none.
dependencies: none.
expected_improvement: The robustness summary matches the released battery.
status: open
```

### R2-S10-19 — Released `statistical_results.csv` prints a rank-biserial formula whose operands yield the opposite sign, and its `w_plus`/`w_minus` are transposed relative to the paper's R⁺/R⁻

```text
ticket_id: R2-S10-19
review_stage: 10
reviewer_role: R1 / T3-STAT
severity: Minor
priority: P2
confidence: Confirmed
issue_type: reproducibility
manuscript_location: papers/analysis/rel-2026-07-20-67d9345f9/primary_stats/statistical_results.csv
  (interpretation column, all AN-PW-* function-level rows); cross-read with
  papers/sections/performance.tex:211-213 and papers/tables/T06.tex, T14.tex
claim_id_or_artifact_id: AN-PW-2017/2013/2011 (function-level rows)
concise_issue: The machine-readable record annotates each effect size as
  "r=(R+ - R-)/(R+ + R-) from w_plus=..,w_minus=.." but the printed operands give the NEGATIVE of
  the recorded value; and the CSV's w_plus/w_minus are the transpose of the paper's R+/R-.
exact_evidence_or_observation:
  statistical_results.csv row AN-PW-2017-D10 / dt-gsk vs gsk: effect_size = 0.864615,
    interpretation = "...effect=matched-pairs rank-biserial r=(R+ - R-)/(R+ + R-) from
    w_plus=22.0,w_minus=303.0..." -> (22-303)/325 = -0.865, not +0.865.
  wilcoxon_holm_cec2011.csv, gsk row: rank_biserial = +0.514286 with w_plus = 51, w_minus = 159;
    the manuscript (performance.tex:551-552) reports "R+ = 159 vs R- = 51", i.e. the paper's R+
    equals the CSV's w_minus. T06.tex and T14.tex follow the paper's (correct, DT-GSK-favouring)
    convention.
  The manuscript is INTERNALLY consistent: with R+ defined as the rank sum favouring DT-GSK,
    (159-51)/210 = +0.514 matches. Only the released artifact's annotation is wrong.
  Governance corroboration (ticket_status.csv, M-027): "SIGN BUG CAUGHT AND FIXED BY THE
    ACCEPTANCE CHECK: the raw statistic is negative for a DT-GSK win ... The statistic is now
    oriented at source" — the orientation was fixed in the value but not in the annotation string.
root_cause: The interpretation string was templated from the pre-orientation formula.
scientific_or_editorial_justification: §10.7 Appendix A.7 — the machine-readable row must be
  self-consistent; a reviewer reconciling the paper's R+/R- against the CSV's w_plus/w_minus will
  find them transposed and the printed formula false.
impact_on_validity_or_acceptance: No manuscript number is affected. This is an evidence-artifact
  hygiene defect that will cost reviewer time.
required_correction: Rename the CSV columns to their meaning (e.g. w_favor_comparator /
  w_favor_dtgsk) or correct the interpretation template to
  "r = (w_minus - w_plus)/(w_plus + w_minus), oriented so r > 0 favours DT-GSK", and add one line
  to the supplement's reproducibility appendix mapping the paper's R+/R- onto the CSV columns.
acceptable_alternatives: Document the mapping in table_to_csv_map.md only.
additional_evidence_needed: none.
dependencies: R2-S10-01.
expected_improvement: The released statistics package becomes self-verifying.
status: open
```

### R2-S10-20 — Supplement Table T06 renders integer counts with four decimals and uses labels inconsistent with its sibling table

```text
ticket_id: R2-S10-20
review_stage: 10
reviewer_role: T5-WRITE
severity: Editorial
priority: P3
confidence: Confirmed
issue_type: exhibit
manuscript_location: papers/tables/T06.tex (rendered: supplementary.pdf, Table in S2.2)
claim_id_or_artifact_id: TAB-T06
concise_issue: Rank sums and win/tie/loss counts — integers — print as 159.0000, 51.0000, 13.0000,
  2.0000, 7.0000; the sibling table T14 prints the same quantities as integers with proper labels.
exact_evidence_or_observation:
  papers/tables/T06.tex: "R+ & 159.0000", "R- & 51.0000", "Wins$+$ & 13.0000", "Ties$=$ & 2.0000",
    "Losses$-$ & 7.0000"; confirmed in the rendered PDF (pdftotext supplementary.pdf, lines 404-408).
  papers/tables/T14.tex uses "$R^+$ & 340", "Wins (+) & 24", "Ties ($\approx$) & 2".
root_cause: T06 is emitted by a generic float formatter; T14 by the typed one.
scientific_or_editorial_justification: §10.17.4 — reader-facing surfaces must not read as machine
  output; §10.11 exhibit consistency.
impact_on_validity_or_acceptance: Cosmetic, but it is on the page a reviewer checking the CEC2011
  head-to-head will read.
required_correction: Regenerate T06 with integer formatting and T14's label typography.
acceptable_alternatives: none.
additional_evidence_needed: none.
dependencies: none.
expected_improvement: Exhibit parity between the two Wilcoxon summary tables.
post_revision_verification: grep the rendered supplement for "\.0000" -> 0 hits.
status: open
```

### R2-S10-21 — Main-text pointer to the ISM compute cost targets S6.7 rather than S6.5

```text
ticket_id: R2-S10-21
review_stage: 10
reviewer_role: R1
severity: Minor
priority: P2
confidence: Confirmed
issue_type: writing
manuscript_location: papers/sections/performance.tex:752-754 and :767-769 (Table tab:runtime caption)
claim_id_or_artifact_id: X-ABL-02
concise_issue: Both main-text pointers for "the isolated compute cost of the interaction-structure
  memory" name Supplementary Section S6.7, which is "Implementation Caveats: Two Corrected Defects
  and Their Evidence Trail". The primary locus for the overhead figures is S6.5.
exact_evidence_or_observation:
  Rendered supplement numbering (pdftotext supplementary.pdf): S6.5 "ISM-Overlay Isolation: Direct
    Component Study"; S6.6 "Conditional-Benefit Analysis by Function Class (Post-Hoc)";
    S6.7 "Implementation Caveats: Two Corrected Defects and Their Evidence Trail".
  supplementary.tex:2038-2042 (S6.5) is where +57.3 % / +36.3 % / +30.3 % are reported as the
    component result; S6.7 (:2149-2153) restates them as provenance for the backend fix.
  The pointer therefore RESOLVES (S6.7 does print the numbers) — it is mis-targeted, not dangling.
  I confirmed there is NO residual reference to the removed oracle study anywhere in the
  manuscript (grep for oracle / headroom / "upper bound" over all .tex -> 0 hits), so this is not
  the §1.5.0-B(d) dangling-reference class.
root_cause: Section numbering shifted when the former S6.7 was deleted; the pointers were not retargeted.
scientific_or_editorial_justification: §10.11 traceability; a reader following the pointer lands on
  a provenance note rather than the component study.
impact_on_validity_or_acceptance: Low.
required_correction: Retarget both pointers to S6.5 (and, if the backend provenance is also
  intended, cite "S6.5, with the measurement provenance in S6.7").
acceptable_alternatives: none.
additional_evidence_needed: none.
dependencies: none.
expected_improvement: Cross-references resolve to the intended content.
status: open
```

### R2-S10-22 — `negative_findings.md`, cited as a `% BIND:` evidence target twelve times, is still bound to a superseded release and carries stale values

```text
ticket_id: R2-S10-22
review_stage: 10
reviewer_role: R4
severity: Minor
priority: P2
confidence: Confirmed
issue_type: evidence
manuscript_location: papers/build_prompt_phases/phase_06/negative_findings.md (cited from
  performance.tex:140, 324, 412, 416, 421, 457, 481, 492, 847 and conclusions.tex:50, 58)
claim_id_or_artifact_id: negative_findings items 1-10
concise_issue: The adverse-findings register that the manuscript's BIND comments point at is bound
  to rel-2026-07-10-262fc16c9 and its numbers no longer match the current release; the manuscript
  itself correctly quotes the CURRENT values, so the prose is right and its cited evidence is stale.
exact_evidence_or_observation:
  negative_findings.md:3 "Release: rel-2026-07-10-262fc16c9."
  Item 6: "p_raw = 3.059340e-02, p_holm = 6.118680e-02" vs current release 0.032298 / 0.064597
    (manuscript prints 0.0323 / 0.0646 — the CURRENT values).
  Item 7: "8 significant -> non-significant transitions ... 18 new significances" vs current
    release 11 and 21 (manuscript prints 11 and 21 — the CURRENT values).
root_cause: The register was written at Phase 6 and not regenerated after the M-026/M-038 re-mints.
scientific_or_editorial_justification: §10.3 source-use logs must prove the evidence boundary; a
  BIND target that disagrees with the release it is supposed to evidence breaks the audit chain.
impact_on_validity_or_acceptance: Low for the reader (the manuscript is correct); material for an
  auditor following the BIND comments.
required_correction: Regenerate negative_findings.md against rel-2026-07-20-67d9345f9, or stamp it
  "historical (rel-2026-07-10); superseded values re-derived in the current release" and repoint
  the BIND comments at the release CSVs.
acceptable_alternatives: none.
additional_evidence_needed: none.
dependencies: none.
expected_improvement: Every BIND target resolves to the declared release.
status: open
```

### R2-S10-24 — Seven shipped generators default to the superseded release id; the recorded reproduction command does not reproduce the declared bundle

```text
ticket_id: R2-S10-24
review_stage: 10 (reported here; primary owner Stage 12)
reviewer_role: R4 / T4-SOFT
severity: Minor
priority: P2
confidence: Confirmed
issue_type: reproducibility
manuscript_location: papers/scripts/*.py; papers/analysis/rel-2026-07-20-67d9345f9/analysis_manifest.json
claim_id_or_artifact_id: CN-02
concise_issue: The manifest's own reproduction command carries no environment override, while the
  script it names defaults to the superseded release; running the documented command reproduces the
  wrong bundle.
exact_evidence_or_observation:
  analysis_manifest.json: "release_id": "rel-2026-07-20-67d9345f9",
    "command": "python papers/scripts/phase6_run_analysis.py"
  statistical_results.csv `command` column (all 5,098 rows): "python papers/scripts/phase6_run_analysis.py"
  papers/scripts/phase6_run_analysis.py:74  REL_ID = os.environ.get("GSK_REL_ID", "rel-2026-07-16-78f075cb0")
  Same stale default in generate_artifact_binding.py:50, generate_nemenyi_cd.py:56,
    generate_rank_charts.py:39, generate_t16_bca.py:50, generate_word_sources.py:48;
    generate_ablation_exhibits.py:50 defaults to "abl-rel-2026-07-16" while the supplement cites
    abl-rel-2026-07-20; finalize_evidence.py:103 OLD_REL_ID = "rel-2026-07-10-262fc16c9".
root_cause: Deliberate design (env overrides with historical defaults), but the recorded command
  omits the override.
scientific_or_editorial_justification: §10.11 requires generators to read only the controlled
  analysis area recorded in project_configuration.md.
impact_on_validity_or_acceptance: Low for the reported numbers; material for an external reproducer.
required_correction: Either bump the defaults to rel-2026-07-20-67d9345f9 / abl-rel-2026-07-20, or
  record the command as "GSK_REL_ID=rel-2026-07-20-67d9345f9 python papers/scripts/phase6_run_analysis.py"
  in analysis_manifest.json, statistical_results.csv and the runbook.
acceptable_alternatives: A README note in the release directory.
additional_evidence_needed: none.
dependencies: R2-S10-10.
expected_improvement: The recorded command reproduces the declared bundle.
status: open
```

### R2-S10-25 — §10.1 binds `STATISTICAL_ANALYSIS_PLAN` to a path that does not exist

```text
ticket_id: R2-S10-25
review_stage: 10 (flagged for the Stage 0/3 seats)
reviewer_role: R4
severity: Minor
priority: P2
confidence: Confirmed
issue_type: compliance
manuscript_location: papers/governance/ (missing file)
claim_id_or_artifact_id: §10.1 binding table
concise_issue: The profile binds the frozen analysis plan to
  papers/governance/statistical_analysis_plan.md; that file does not exist. The actual frozen plan
  is papers/build_prompt_phases/phase_05/statistical_analysis_plan.md.
exact_evidence_or_observation:
  `find papers -iname "*statistical_analysis_plan*"` -> papers/build_prompt_phases/phase_05/statistical_analysis_plan.md only.
  PAPER_REVIEW_PROMPT.md:3177 binds STATISTICAL_ANALYSIS_PLAN to `papers/governance/statistical_analysis_plan.md`.
root_cause: Binding table records the intended governance location, not the build location.
scientific_or_editorial_justification: §10.1 requires these bindings to resolve to existing artifacts.
impact_on_validity_or_acceptance: Low — the plan exists and I audited against it (see R2-S10-07) —
  but the binding as written fails.
required_correction: Copy/symlink the plan into papers/governance/, or correct the binding table.
acceptable_alternatives: Record the actual path in project_configuration.md.
additional_evidence_needed: none.
dependencies: none.
expected_improvement: Every §10.1 binding resolves.
status: open
```

### R2-PROMPT-23 — Governing-prompt staleness (recorded per the review directive)

```text
ticket_id: R2-PROMPT-23
review_stage: 10/11 (meta)
reviewer_role: R4
severity: Moderate
priority: P2
confidence: Confirmed
issue_type: compliance
manuscript_location: papers/PAPER_REVIEW_PROMPT.md §1.5 (lines 118-602) and §10.7 final bullet (line 3299)
claim_id_or_artifact_id: prompt snapshot
concise_issue: The prompt's embedded status snapshot predates the 2026-07-21/22 remediation and
  contradicts the repo on the ledger state and on RT-001's disposition; §1.4 precedence makes the
  repo authoritative.
exact_evidence_or_observation:
  §1.5 (line 118 ff.): "the 80-ticket remediation ledger ... stands at **73/80 fully closed** ...
    and **seven** terminal / machine-gated / author-gated tickets remain open (RT-001 the live
    runtime blocker; C-008 -> C-001 the terminal freeze+commit; N-009 / N-021 / M-007 / E-012 ...)".
  Repo: papers/governance/remediation_2026_07_18/ticket_status.csv = 80 rows, lifecycle_status
    counts {closed_verified: 70, superseded_with_evidence: 10}; RT-001, C-001, C-008, N-009,
    N-021, M-007 and E-012 are ALL closed_verified (RT-001 closed_utc 2026-07-21).
  §10.7 final bullet (line 3299): "the runtime table (tab:runtime) and its source (cost_cec2017.csv)
    are being brought into single-environment comparability by re-timing all six comparators
    (scripts/retime_comparators.py) ... the current table mixes two measurement sessions and is
    provisionally frozen ... The review MUST treat the current runtime cells as in-progress".
  Repo: RT-001 was closed by the OPPOSITE remedy — Decision 7 Option 3, "DT-GSK-only fallback",
    after the Option-2 re-timing failed its determinism gate (see R2-S10-05). The shipped
    tab:runtime (performance.tex:759-784) contains DT-GSK rows only and explicitly makes no
    cross-algorithm comparison, so it no longer "mixes two measurement sessions".
  §1.5 also states the abstract is "~178 words" post-oracle-removal; the current abstract
    (main.tex:127-153) should be re-counted by the venue seat rather than taken from the snapshot.
root_cause: The snapshot is dated 2026-07-20 and was not regenerated after the R-01..R-14 pass.
scientific_or_editorial_justification: §1.4 precedence — current project state outranks the
  embedded snapshot. Reviewers following §10.7's RT-001 instruction would look for an in-progress
  mixed-provenance runtime table that no longer exists, and would mis-score Gate A on ledger state.
impact_on_validity_or_acceptance: Review-process risk only.
required_correction: Regenerate §1.5 and the §10.7 RT-001 bullet from
  remediation_2026_07_18/ticket_status.csv and decisions.md (Decision 7 amendment) before the next
  cycle; record that the runtime table is FINAL and DT-GSK-only, and that Option 2 failed.
acceptable_alternatives: A dated errata block at the head of §1.5.
additional_evidence_needed: none.
dependencies: R2-S10-05.
expected_improvement: The governing prompt stops contradicting the artifact it governs.
status: open
```

---

## 4. Robustness matrix (Stage 11 required output)

| Robustness axis | Evidence in package | Result | Disclosed in manuscript? |
|---|---|---|---|
| Alternative central tendency (median endpoint) | `r01_mean_vs_median.csv`; supplement S2.5 endpoint table | DT-GSK ordinals 1/2/1/1 unchanged; D100 becomes an exact tie at 2.59; two comparator swaps; W/T/L shift materially | **Yes**, in main text and supplement |
| Alternative transformation (log₁₀ endpoint, floored) | `posthoc_robustness/posthoc_endpoint_ranks_cec2017.csv` | DT-GSK first/second/first/first, unchanged | Yes (supplement S2.5) |
| Numerical floor sensitivity | `r02_floor_sensitivity.csv` | agree | Not named in main text (acceptable — no divergence) |
| Tie-band sensitivity (relative band ρ = 1 %, 5 %) | supplement S5.5 | Two eGSK cells change direction of the descriptive count at ρ = 5 %; no inference affected | **Yes**, and read against the paper's own interest |
| Missing-data / failed-run encoding | APGSK per-run gap; disclosed-unavailable, never imputed; post-freeze recovery footnoted | No imputation found; function-level basis retained | Yes (but see R2-S10-13) |
| Exclusion of disputed cells | `r04` (APGSK-excluded; eGSK-excluded) | APGSK variant: GSK/FDB-AGSK swap at D30; eGSK variant: DT-GSK first at D30 | APGSK variant yes; eGSK variant **no** (R2-S10-18) |
| Leave-one-function-out | `r03_lofo_friedman.csv` | DT-GSK ordinal stable at all four dimensions; four comparator rows diverge | Partially (R2-S10-18) |
| Alternative multiplicity family | `global_holm_sensitivity_cec2017.csv` (m = 24) | 15 of 24 survive; 0 losses under either family | **Yes**, in main text |
| BH exploratory companion | `r06_holm_vs_bh.csv`, `wilcoxon_run_*_exploratory_bh.csv` | Separately labelled, never headline — SAP-compliant | Yes, as exploratory |
| Alternative model spec (unpaired Mann–Whitney) | `r05_unpaired_companion.csv` | 11 / 21 transitions, **0 sign reversals** | **Yes**, with the honest note that dropping pairing *increases* significances |
| Randomization inference (sign-flip, 2×10⁵) | supplement S2.5 | 0 of 24 Holm decisions change | Yes |
| Aggregation variant (pooled block Friedman) | `r08_overall_aggregation_variants.csv` | Identical mean ranks and ordinals to the descriptive mean | Not cited (correctly — the paper does not pool) |
| Cross-suite consistency | `r07_secondary_suite_effect.csv` | qualitatively consistent | Yes |
| Different seeds / splits | Single frozen seed schedule (51 runs per cell) — no seed-family variation | n/a | Not claimed |
| **Hyperparameter / threshold sensitivity** | **NONE — EG-006 closed by the "omit" branch** | **absent** | **No — R2-S11-04** |
| Computational environment / precision | Single host; single-thread precondition for D ≥ 50 byte-identity | Disclosed as limitation "Sixth" | Yes; but the cross-commit comparator finding is **not** (R2-S10-05) |
| **Does the headline conclusion reverse under any reasonable choice?** | — | **No.** DT-GSK's own ordinals are invariant across every executed variant; the D100 first place degrades to a shared first under the median endpoint, which the paper states. | Yes |

**Conclusion-stability statement.** *The evidence directly supports* the claim that, within the
seven-algorithm GSK-family panel and under the frozen protocol, DT-GSK holds the best descriptive
across-dimension Friedman rank aggregate on CEC2017 and CEC2013 and is second on CEC2011, and that
this ordering does not reverse under any robustness variant executed. *The evidence supports this
conclusion only for* the three tested suites, the four tested dimensions, the stated budgets, and
the specific comparator configurations used — and the study's design **does not separate** the
tiered control mechanism from the dimension-scaled population it is bundled with (R2-S11-03).

---

## 5. Component-claim-to-design matrix (Stage 11 required output)

| Component claim | Design used | What it can support | What it cannot establish | Manuscript's claim scope | Verdict |
|---|---|---|---|---|---|
| ISM (interaction-structure memory) | Direct on/off overlay, 4 cells, 51 runs, CEC2017 D50/D100 + CEC2013 D50, Holm over 3 contrasts | Effect of the specific toggle with all else held constant | Broader mechanism explanation; equivalence to zero | Reported as a **controlled negative result**; "failure to detect ... not a demonstration that none exists" | **Correct.** Exemplary scoping. |
| ISM conditional benefit by class | Post-hoc subset of the same overlay | Exploratory hypothesis generation | Any confirmatory statement | Supplement labels it post hoc; Conclusions/Intro do not | **Defect — R2-S10-06** |
| Final polish (eigenframe compass endgame) | Remove-one within the overlay design (whole phase) | Conditional necessity of the phase | Whether the *learned eigenbasis* beats coordinate/random axes | Explicitly bounded in C1 and limitation "Eighth"; result kept supplementary per §10.9 | **Correct**, and the §10.9 confinement is respected |
| ACE, NLPSR, BSE, linkage, local search, archive | Scaffold remove-one, 7 cells, ISM off, 51 runs, CEC2017 D10–D100 | Conditional (ISM-off) remove-one contribution within the full configuration | Independent causal effect; additivity; ISM-on behaviour | Supplement states all four bounds explicitly and never averages across dimensions | **Correct** |
| ARGP (the only element claimed as not-found-elsewhere) | **None** — pre-specified exclusion from both matrices | Nothing | Any utility claim | C2 names it as novel without the exclusion bound | **Defect — R2-S11-11** |
| Deep-stall restart | **None** — pre-specified exclusion (overlaps BSE) | Nothing | Any utility claim | Bounded in S6.1/S6.4; not foregrounded in C2 | Acceptable |
| Dimension tiering itself (the titular mechanism) | **No direct evidence** — no tier-boundary variation, no matched-NP contrast, no parameter sensitivity | Nothing beyond end-to-end performance | That tiering, rather than the bundled population schedule, produces the D ≥ 50 standing | Discussion attributes D ≥ 50 behaviour to "the bundled tier configuration rather than ... any isolated component" — correctly hedged — but does not name the population confound | **Defect — R2-S11-03, R2-S11-04** |

**Unsupported mechanism claims found: none.** The manuscript's mechanism language is consistently
"consistent with", "plausibility", "not claimed", "bundled tier configuration". §10.9's confinement
of the favourable final-polish result to the supplement is respected; I found **no** favourable
component result in the main text, abstract, highlights, conclusion, or cover letter. The advertised
ISM null appears in the abstract (one sentence), the introduction (§ supporting-component
paragraph), the Discussion (performance.tex:826-829) and the Conclusions — the two latter loci go
beyond the "one abstract sentence plus the introduction paragraph" brevity the §10.9 narrowing
describes, but per the explicit reviewer directive I do **not** raise the advertised null as a leak;
none of the four sentences asserts a proven or favourable ISM effect, which is the condition the
directive says would make it a defect.

**Sensitivity and interaction gaps.** (i) No parameter sensitivity at all (R2-S11-04).
(ii) No factorial or targeted interaction analysis: the D ≥ 50 tier co-activates ISM, the eigenframe
polish, the raised population floor, and (per R2-S11-03) a 5× initial population, and no design
separates them. The manuscript says so in the Discussion — correctly — but the co-activation list
omits the population-size term.

---

## 6. Prioritized additional studies (Stage 11 required output)

Ranked by decision-relevance. Only #1 is achievable within the no-rerun constraint; #2–#4 are
recorded as the design a future cycle should run, with the decision each would settle.

1. **(Text-only, this cycle.)** Disclose the comparator population setting, the parameter-sensitivity
   absence, and the cross-commit comparator non-reproducibility. Settles R2-S11-03 (partially),
   R2-S11-04 and R2-S10-05 without a single new run.
2. **Matched-population contrast at the decisive tier.** DT-GSK at NP_init = 100 (comparator
   setting) vs NP_init = 5·D, CEC2017 D = 50 and D = 100, 51 paired runs, same seed schedule.
   *Decision it settles:* whether the upper-tier standing survives population matching — i.e.
   whether the dimension-tiered thesis or the population schedule carries the result. This is the
   single highest-value experiment in the whole programme.
3. **Tier-boundary sensitivity.** The D ≥ 50 gate at {40, 50, 60} and NP_init multiplier at
   {3, 5, 8}, CEC2017 D = 50 only, 51 runs, one factor at a time. *Decision it settles:* whether the
   titular tier boundary is a knife-edge or a plateau — the minimum evidence a reviewer will accept
   for a "dimension-tiered" contribution.
4. **Learned-basis isolation.** Eigenframe polish on (a) the ISM eigenbasis, (b) coordinate axes,
   (c) a matched random orthonormal basis, D = 50/100, 51 runs. *Decision it settles:* the question
   C1 and limitation "Eighth" both leave explicitly open. The package already concedes this gap, so
   this study converts a stated unknown into a result rather than closing a defect.

---

## 7. Gate assessment

| Gate | Verdict | Basis |
|---|---|---|
| **J — Result Integrity** | **CONDITIONAL FAIL** | R2-S10-01 (irreconcilable description of the headline table's effect size, reader-facing in both formats); R2-S10-02 (statistics printed from a superseded release, mixed across suites, contradicting the stated method); R2-S10-05 (adverse reproducibility outcome not visible). No selective reporting, no misleading aggregation, and no interpretation exceeding the evidence was found; all three blockers are text-only. |
| **K — Robustness & Mechanism Attribution** | **CONDITIONAL FAIL** | R2-S11-03 (a first-order alternative explanation for the dimension-resolved headline is neither disclosed nor bounded) and R2-S11-04 (no parameter-sensitivity evidence and no disclosure of its absence). The central conclusion is **stable**, component designs are honestly bounded, and the §10.9/§10.10 placement rules are respected — the failure is attribution and disclosure, not instability. |

Both gates clear on disclosure edits alone. **No rerun, no new evidence release, and no change to
the byte-locked optimizer core is required by any ticket in this report.**

---

## 8. Category scores (§6.1)

| Category | Score | Evidence |
|---|---|---|
| Results integrity / accuracy of reported numbers | **4** | Every headline number re-derived exactly; two stale/contradictory *descriptions* (R2-S10-01, R2-S10-02) rather than wrong values. |
| Internal consistency (abstract ↔ body ↔ tables ↔ supplement ↔ cover letter) | **3** | Eleven contradictions in §2, one of them inside a single paragraph; the cover letter drops the abstract's qualifications. |
| Loss and adverse-outcome visibility | **3** | Exemplary on CEC2017 and CEC2011; a real gap on CEC2013 (R2-S10-08) and one hidden adverse reproducibility outcome (R2-S10-05). |
| Interpretation discipline / claim scoping | **4** | Consistently calibrated language; no causal over-reach; two labelling lapses on exploratory results. |
| Robustness and sensitivity | **3** | A genuinely strong, pre-registered eight-check battery with divergences disclosed — but zero parameter sensitivity and no disclosure of that (R2-S11-04). |
| Ablation adequacy and mechanism attribution | **4** | Designs are correct and honestly bounded; the ARGP evidence gap and the unnamed population confound cost the fifth point. |
| Alternative-explanation exclusion | **2** | The population-size asymmetry (R2-S11-03) is a complete competing explanation for the central pattern and is neither stated nor bounded. |

---

## 9. Method note

Read-only throughout. Numbers were recomputed with pandas/numpy directly from
`papers/analysis/rel-2026-07-20-67d9345f9/**`; rendered text was extracted with
`pdftotext -layout` from `papers/DT-GSK.pdf`, `papers/supplementary.pdf` and
`papers/cover_letter.pdf` (all rebuilt 2026-07-22 17:48–17:49). The across-function A₁₂ values were
independently re-derived from `descriptive_stats_cec2017_D*.csv`. Three shipped read-only gates were
executed and all three pass: `validate_document_consistency.py` (OK),
`validate_evidence_bindings.py` (321 BINDs, 825 tokens, 0 FAIL — see R2-S10-12 for what that does
*not* cover), `validate_provenance_claims.py` (OK, exit 0). Configuration facts were read from
`src/gsk_family/optimizers/_dt_core.py`, `papers/build_prompt_phases/phase_03/parameter_table.tex`,
and the frozen `run_config.json` of each panel algorithm under
`benchmarks/cec_reference_results/cec2017/`. No file outside this report was written.
