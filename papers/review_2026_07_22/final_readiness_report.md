# DT-GSK — Final Readiness Report

**Stage 19 consensus and Stage 20 verification plan · Supervising Editor · Editorial Coordination Board**

---

## 12.1 Review metadata and scope

```text
review_id                : DTGSK-REVIEW-2026-07-22
review_date              : 2026-07-22
project_title            : DT-GSK: Dimension-Tiered Adaptive Control and Deterministic Refinement
                           for Gaining-Sharing Knowledge Optimization
manuscript_version       : git HEAD 45248eb31af7b01567c251f2a5da4f36e92d6030
                           (post-remediation R-01..R-14; freeze manifest declares anchor abd2fa2f25c8)
target_journal           : Algorithms (MDPI)
target_article_type      : Article
target_quartile_status   : Q2 (MDPI Algorithms; Q1 claimed only as an aspiration — see 12.16)
materials_reviewed       : DT-GSK.pdf (39 pp), supplementary.pdf (61 pp), cover_letter.pdf (2 pp),
                           DT-GSK.docx, supplementary.docx, all LaTeX sources, papers/governance/**,
                           papers/analysis/rel-2026-07-20-67d9345f9/**,
                           benchmarks/cec_reference_results/** (evidence release
                           rel-2026-07-20-67d9345f9, anchor 67d9345f9502a9a584e645fa8948f60a61d70e29),
                           papers/scripts/**, the byte-locked optimizer core, and eleven seat artifacts
                           under papers/review_2026_07_22/
materials_missing        : papers/governance/statistical_analysis_plan.md and exhibit_plan.csv do not
                           exist at their section 10.1 bound paths (they are under
                           build_prompt_phases/phase_05 and phase_04); the external-gate mapping is
                           absent from the tree; the MDPI Algorithms instructions page returned
                           HTTP 403 to this panel (verified_online = FALSE)
governing_protocol       : papers/PAPER_REVIEW_PROMPT.md — universal workflow, section 9 Module A,
                           and the section 10 DT-GSK evidence-locked profile
scientific_scope         : Seven-method GSK-family panel (gsk, agsk, apgsk, fdb-agsk, atmals-gsk,
                           egsk, dt-gsk) on CEC2017 D10/D30/D50/D100 (51 runs, F2 excluded),
                           CEC2013 D10/D30/D50 (51 runs), CEC2011 (25 runs). External non-GSK
                           baselines are OUT OF SCOPE by section 1.5.4 directive.
review_limitations       : (i) The governing prompt's own section 1.5 snapshot is dated 2026-07-20 and
                           predates the R-01..R-14 remediation; per section 1.4 the repository state
                           governs and the staleness is recorded as SE-050. (ii) Journal-instruction
                           verification is administratively BLOCKED (HTTP 403). (iii) No rerun, no new
                           evidence release, and no change to the byte-locked optimizer core was
                           permitted or performed; every finding below is correctable by text,
                           exhibit regeneration, or governance-record edit.
```

---

## 12.2 Executive editorial verdict

**Internal disposition: `D2 — MAJOR PRE-SUBMISSION REVISION`. Weighted readiness score 64.60/100. Not submission-ready today; realistically two to three weeks of text-only work from a defensible Q2 submission. No scientific blocker was found by any of the eleven seats, and none by me.**

The paper claims three contributions: a deterministic, RNG-free eigenframe final polish executed once in the terminal budget slice (C1); a dimension-tiered adaptive scaffold of bandit-style operator selection, tier-floored population reduction, stagnation escape and deep-stall restart (C2); and the evaluation-integrity infrastructure that makes the study checkable (C3). A supporting interaction-structure memory is deliberately reported as a controlled negative result.

**The strongest verified contribution is C1 combined with the evidence discipline behind it.** Four seats independently recomputed every headline number from the frozen release — the CEC2017 per-dimension ranks 2.88/2.50/2.21/2.34 and the 2.48 aggregate, the 17-7-0 Holm tally, the 15-of-24 global-Holm sensitivity, the CEC2013 2.80 and CEC2011 3.36, every Nemenyi gap against CD 1.673, every BCa interval, every F26 cell — with **zero numerical mismatches**. Method review recomputed all thirteen displayed equations symbolically against the byte-locked source and found **no equation wrong**. Evidence review reconciled 3,403/3,403 release checksums over 712 MB with zero mismatches and a 70,813-row seed audit. The paper's loss visibility is genuinely exemplary: the abstract itself carries the second place at D=30, the Holm-significant CEC2011 loss to eGSK, and the fact that the nearest comparator is never Nemenyi-separable. That is rarer in this literature than the result being claimed.

**The central scientific weakness is framing, not validity.** The organising question and the stated gap are both ISM-shaped, and the ISM result is the null. The contribution the paper calls original (ARGP, inside C2) is a pre-specified exclusion from every ablation. The mechanism with the largest measured effect — the coordinate/compass endgame, close to classical direct search — is claimed by no bullet. A reviewer asking "what is the thesis?" currently gets pointed at the paper's own negative result (SE-030, SE-015).

**The strongest likely rejection reason is different from the weakness, and it is mechanical.** Table 14 prints a rank-biserial `r` column while four prose passages describe "the $A_{12}$ column" and quote four A12 values that appear in no exhibit and in no released CSV; one paragraph designates two different statistics as "the tabulated effect size" within itself (SE-001). Alongside it: the fairness sentence "All seven optimizers are held to exactly the same MaxFES charge" is falsified by 1,845 runs in the shipped data (SE-002, which I counted myself), and the proposed method's own legend label runs 32 points off the page edge in both main-text convergence figures (SE-005, which I measured myself). Each of these is checkable by a reviewer in under a minute, and each is text or regeneration only.

**Does the current evidence support the thesis?** Yes, in the scope the paper claims. Nothing in this review changes a reported number, invalidates a statistical inference, or touches the byte-locked core. Two findings genuinely constrain interpretation rather than presentation: the undisclosed 5× population-size asymmetry at D=100, where the headline lives (SE-008), and the complete absence — undisclosed — of parameter-sensitivity evidence for a contribution that *is* a parameter schedule (SE-016). Neither makes the result false; both leave the paper unable to answer the obvious question.

**Amount of revision required:** 17 Major, 19 Moderate, 14 Minor tickets. Every one is text, exhibit regeneration, or governance-record work. Zero require a rerun, a new evidence release, or a core change. Exactly one requires new work of any kind, and it is an author attestation at zero compute (SE-014, the selection-exposure count).

**Q1 or Q2 after correction?** **Q2-ready is realistic and well within reach.** Q1 is not, and should not be pursued in this cycle: the headline suite is development-exposed, the closest comparator is never Nemenyi-separable, the strongest measured effect belongs to a deterministic endgame close to classical direct search, and the panel is deliberately intra-family. Those are structural properties of the study, not defects — but they are what separates Q2 from Q1 here.

---

## 12.3 Submission-readiness dashboard

| Category | Score /5 | Weight | Weighted | Gate | Crit/Major | Status | Evidence summary |
|---|---:|---:|---:|---|---:|---|---|
| Journal fit and scientific significance | 4.00 | 8 | 6.40 | B, D | 0 | PASS (cond.) | In-scope algorithmic contribution; framing and cover-letter scoping deductions |
| Novelty and contribution boundary | 3.00 | 12 | 7.20 | D | 2 | REVISION | C1 sound; C2's originality claim untested; C3 is infrastructure; novelty scope stated three ways |
| Theory, method, or algorithmic correctness | 4.00 | 14 | 11.20 | F | 1 | PASS (cond.) | All 13 equations recomputed symbolically — none wrong; three ISM parameters unspecified |
| Experimental or study design | 3.00 | 14 | 8.40 | H | 4 | REVISION | Three fairness statements falsifiable from the shipped release; selection exposure unbounded |
| Statistical validity | 3.00 | 14 | 8.40 | I | 2 | FAIL | Zero numerical errors in ~200 recomputed quantities; defects are in the printed spec and governance |
| Evidence and citation integrity | 4.00 | 8 | 6.40 | E, G | 0 | PASS (cond.) | 3,403/3,403 checksums; 57/57 sources; one omitted author; stale governance bindings |
| Results, discussion, and limitations | 3.00 | 8 | 4.80 | J | 4 | REVISION | Headline numbers exact; effect-size referent, omitted determinism scope, false APGSK claim |
| Robustness, sensitivity, and ablation logic | 3.00 | 6 | 3.60 | K | 2 | REVISION | Ablation sound where run; zero parameter sensitivity, undisclosed; ARGP never isolated |
| Reproducibility and open-science readiness | 2.00 | 7 | 2.80 | L | 2 | FAIL | Freeze envelope 15/15 only on the author's disk (10/15 at HEAD, 7/15 at the declared anchor) |
| Writing, exhibits, and presentation | 3.00 | 5 | 3.00 | M, N | 3 | M FAIL / N PASS (cond.) | Zero AI tells; but 25/25 convergence figures clip the proposed method's own label |
| Ethics, journal compliance, and production package | 3.00 | 4 | 2.40 | O, P | 2 | O FAIL / P BLOCKED | Strong integrity posture; GenAI declaration over-claims; Word geometry off; 403 on instructions |
| **TOTAL** | — | **100** | **64.60** | — | **17** | — | — |

**Readiness band: `Major pre-submission revision`.** Weighted score 64.60 against the 82 Q2 threshold; three core scientific categories (novelty, experimental design, statistical validity) sit at 3.00 against the 4.00 Q2 floor; 17 Major tickets are open.

> **Hard gates override the score (section 11).** Even were the weighted score above 82, Gates I, L, M and O are FAIL and Gate P is BLOCKED, so no readiness classification above `Major pre-submission revision` is available.

---

## 12.4 Gate report

| gate | status | evidence | blocking_tickets | minimum_action_to_pass | reviewer_signoff |
|---|---|---|---|---|---|
| **Stage 0 decision** | **PASS** | One authoritative manuscript state exists and is readable; `check_manifest` 15/15 against the working tree; `validate_provenance_claims` OK; `validate_cross_format_parity` 579 rows / 0 FAIL; `validate_document_consistency` OK; `validate_build_hygiene` OK — all re-run read-only by SE. No three-way source↔PDF↔Word desync. Four open P1 items carried forward. | — | — | s0-1_preflight; SE |
| **A — Package integrity** | **FAIL** | SE hashed all 15 pinned files three ways: working tree 15/15, HEAD `45248eb31` **10/15**, declared anchor `abd2fa2f25c8` **7/15**. Five files (proposed_algorithm.tex, claims_evidence_matrix.csv, citation_usage_map.csv, artifact_binding.csv, references.bib) match neither committed blob — `core.autocrlf=true` with no `.gitattributes`. Three more (performance.tex, DT-GSK.pdf, DT-GSK.docx) changed at HEAD after the anchor was stamped; the manifest's own `freeze_statement` records the amendment. Section 10.1 additionally requires every build-gate row to carry pass evidence; the Phase-12 row carries no page count. | SE-003, SE-004, SE-018, SE-022, SE-040 | Re-stamp `anchor_commit` to the commit holding the pinned bytes, add `.gitattributes`, land a stamping commit, and demonstrate 15/15 from a clean `git archive` extraction outside the author's working tree. | SE (measured directly) |
| **B — Desk review** | **PASS (conditional)** | No unresolved likely desk-rejection defect. The page and word budgets are self-imposed, not journal rules — `phase_04/page_budget.md` records "No hard journal page limit found" for MDPI *Algorithms*, and 12,000 words is MDPI's contact-the-office threshold, not a rejection threshold. | SE-018 (cond.), SE-029 | Record the measured B1/B2 at the gate and either waive the cap with a change request or migrate material to the supplement. | s2-4_desk_significance; SE |
| **C — Claim integrity** | **FAIL** | Four substantive claims are unsupported or misscoped as printed: the effect-size referent (SE-001), the MaxFES-equality assertion (SE-002, 1,845 counterexamples counted by SE), the APGSK availability claim (SE-017), and the unscoped determinism property (SE-009). Claim-level recomputation was otherwise exact across ~200 quantities. | SE-001, SE-002, SE-009, SE-017, SE-021, SE-047 | Correct all four; re-run the claim audit against the revised text. | s3_claims; SE |
| **D — Contribution merit** | **PASS (conditional)** | Defensible significance for MDPI *Algorithms* at Q2. C1 is the only added mechanism with an isolated Holm-significant effect. Conditional on the C2 originality boundary and the thesis framing. | SE-015, SE-024, SE-030 | Narrow C2 so its originality claim does not rest solely on an untested element; state the novelty boundary at one scope; re-frame the organising question onto the supported evidence. | s2-4_desk_significance; SE |
| **E — Literature/citation integrity** | **PASS (conditional)** | 57 bib entries : 57 local PDFs; 40 cited = 40 in `main.bbl`; exact PDF↔DOCX bibliography parity; no `\nocite`; 117 citation occurrences recounted = 117 usage-map rows; no fabricated or unverifiable reference; no patchwriting; ten load-bearing related-work claims re-verified against source PDFs, nine reproducing exactly. | SE-023, SE-024, SE-025, SE-034 | Add the omitted fourth author to `liang2013cec2013`; correct the GSK-RL characterisation; backfill the `awad2016problem` role-map row and banner the superseded audit report; fix the dead DOI. | s5_literature; SE |
| **F — Method/theory** | **PASS (conditional)** | All 13 displayed equations recomputed symbolically against the byte-locked source — none wrong. All four freeze SHA-256s independently re-verified as matching the working tree. The R1-canonical SGSM EMA defect (`G←λG+ηΣ`) is genuinely fixed at `interaction_graph.py:201/:344`. Single `BudgetController`, no direct objective call, MaxFES-exact by construction. No convergence claim smuggled. | SE-012, SE-027 | Publish the three missing ISM parameters; restate the linkage channel as a 0.5 mixture; complete the R-01/R-02 propagation. | s6_method; SE |
| **G — Evidence integrity** | **PASS (conditional)** | 3,403/3,403 release checksums (712 MB, 0 mismatch); 130/130 analysis-bundle; 59/59 exhibit source+output checksums; 1,239 source opens with 0 outside the release; exact row counts with F2 excluded; 0 duplicate seeds; 0 NaN/Inf; seeds identical across all seven optimizers on every pairing key; the printed seed formula re-derived over 32,250 rows exactly; threefry in all 36 cells. | SE-009, SE-022, SE-040 | Disclose the cross-commit determinism result; re-point the stale governance bindings. | s7-12_evidence_repro; SE |
| **H — Study design/fairness** | **FAIL** | Design answers the panel-scoped question and the seven-method panel is intact, but three fairness statements are falsifiable from the shipped release. SE independently verified two of the three: 1,845 `target_error_reached` runs (agsk 404+558, apgsk 338+545, min charged nfes 44,497/1,000,000) and a flat NP=100 for all six comparators at every dimension against DT-GSK's 5·D. | SE-002, SE-008, SE-011, SE-014 | Correct the MaxFES sentence; state the executed NP for all seven; extend the eGSK disclosure to performance; quantify the selection exposure. | s8_design_fairness; SE |
| **I — Statistical validity** | **FAIL** | Every Friedman rank vector, all 48 across-function Wilcoxon p-values, all W/T/L triples, tie-correction factors, Nemenyi CDs, global-Holm sensitivity, BCa intervals, class ranks and robustness counts recomputed from the frozen release with **zero numerical mismatches**. All defects are in the printed specification, provenance, or governance. | SE-001, SE-007, SE-019, SE-020, SE-042, SE-046 | Settle the effect-size referent; print the corrected omnibus column on all three suites; correct the scale-invariance claim; log the post-outcome changes and backfill the A.7 register rows. | s9_statistics; SE |
| **J — Result integrity** | **FAIL** | All headline numbers re-derived exactly; loss visibility on CEC2017/CEC2011 exemplary. Fails on the effect-size referent rendering in the results narrative, the mixed omnibus columns, an undisclosed cross-commit determinism finding, a false APGSK existence claim, and an unlabelled post-hoc class result in the Conclusions. | SE-001, SE-007, SE-009, SE-017, SE-028 | As for Gates C and I; add the exploratory label to the class analysis. | s10-11_results_robust; SE |
| **K — Robustness/attribution** | **FAIL** | Ablation design is sound where it runs (51-run scaffold remove-one at four dimensions, promoted immutable release, negative results retained). Fails because zero parameter-sensitivity evidence exists and is disclosed nowhere, and because ARGP — the sole element claimed as original — is a pre-specified exclusion from every ablation. | SE-015, SE-016 | Disclose the sensitivity absence as a limitation; correct "each scaffold subsystem"; narrow C2. | s10-11_results_robust; SE |
| **L — Reproducibility** | **FAIL** | The evidence is intact and fully checksummed; the published route to it is not. Freeze envelope 15/15 only against the author's working tree (SE-measured: 10/15 at HEAD, 7/15 at the declared anchor). `reproducibility_manifest.json` records `anchor_commit 262fc16c9…` — two evidence releases behind the shipped `rel-2026-07-20-67d9345f9` (SE-verified directly). The `runbook.md` cited by the Data Availability statement omits the sole producer of the analysis bundle, the DOCX build, `check_manifest` and every validator. | SE-003, SE-004, SE-022, SE-033, SE-040 | Re-point the manifest, rewrite the runbook so it actually reproduces the shipped artifacts, and demonstrate a clean-room `check_manifest` 15/15. | s7-12_evidence_repro; SE |
| **M — Exhibit integrity** | **FAIL** | SE measured with `pdfplumber` across all 25 convergence figures: **every one** places legend glyphs outside the media box. On the 443.88 pt canvas, `GSK` starts at x0 = −1.75 and `DT-GSK` spans 442.45→476.24 — only 1.43 pt of the proposed method's own label is on the page. This includes `main_cec2017_D30.pdf` (Figure 6) and `main_cec2017_D100.pdf` (Figure 7). Figure 4 renders in-figure text at 4.18–5.23 pt against 8.9 pt body text. Supplement Table A19 overflows by 218.99 pt and loses its Notes column. | SE-005, SE-006, SE-013, SE-026, SE-039, SE-045 | Regenerate all 25 convergence figures with a wrapped legend and `bbox_inches='tight'`; rescale Figure 4 to ≥8 pt at final size; re-typeset Table A19 to zero overfull boxes; add an automated off-canvas assertion to the build hygiene gate. | s13_exhibits; SE |
| **N — Writing/authorship integrity** | **PASS (conditional)** | Zero occurrences of the canonical AI tells (Moreover / Furthermore / Additionally / Notably / It is worth noting / delve / leverage / crucial role / paves the way / comprehensive / remarkably) across the entire package. No claims-strengthening, no detector-evasion editing. A distinct human voice with measurable tics. | SE-036 | Complete the R-13 de-packing beyond the two paragraphs it touched; remove the transparency framing while keeping every disclosure; settle on one name for the C1 mechanism. | s15_writing; SE |
| **O — Ethics/publication integrity** | **FAIL** | No AI author; no retracted reference (51 DOIs queried, 0 retractions/corrections/EoCs); no fabricated administrative value; no redistributed third-party PDF; self-citation 15.8–17.5 % and structurally forced, doubly disclosed, used adversely as often as favourably; adverse results advertised in both abstract and cover letter. Fails on one item: the GenAI declaration asserts the implementation was produced "independently of any AI system" while 231 of 384 project commits — including `af7efc534`, which modifies `_dt_core.py` and forced the regeneration behind the shipped release — carry `Co-Authored-By: Claude`. SE verified both figures directly. | SE-010, SE-034, SE-035, SE-049 | Narrow the declaration to what is accurate and verifiable; name every model version; extend `validate_document_consistency.py` beyond the cover letter to the three manuscript loci. | s16_ethics_ai; SE |
| **P — Journal/production compliance** | **BLOCKED** | 0 undefined refs/citations; 0 overfull boxes in the main PDF; all fonts embedded; correct metadata and bookmarks; vector PDF figures; 0 tracked changes, comments or hidden text; 0 rasterised equations or tables; 17/26 native `w:tbl`; 753/640 native OMML with 0 literal `&`; abstract ≤200 words in the rendered PDF; all MDPI declarations present. BLOCKED (not FAIL) on the journal-instruction axis: `mdpi.com/journal/algorithms/instructions` returned **HTTP 403** on 2026-07-22, so `verified_online = FALSE` persists from Phase 4. | SE-006, SE-031, SE-032, SE-048 (+ administrative 403) | Re-attempt instruction verification from an unblocked network and record the result; align the Word page geometry or record the deviation; regenerate `word_validation_report.md`; fix Table A19. | s17_journal_production; SE |
| **Q — Post-revision verification** | **NOT YET RUN** | Stage 20 plan issued; see `revision_roadmap.md` and `post_revision_verification.csv`. | all open Major | All 17 Major tickets closed with evidence, every affected artifact regenerated and validated, and no regression. | SE |

---

## 12.5 Verified strengths

These are demonstrably supported and should be protected through revision — several are stronger than the paper currently claims.

1. **Arithmetic integrity is complete.** Four seats independently recomputed every headline quantity from `rel-2026-07-20-67d9345f9` — CEC2017 ranks 2.88/2.50/2.21/2.34 → 2.48; the 17-7-0 Holm tally; the 15-of-24 global-Holm sensitivity with both named non-survivors; CEC2013 2.41/3.38/2.61 → 2.80; CEC2011 F=4.27; every Nemenyi gap against CD 1.673; every BCa interval and the eGSK overlap pattern; every class-rank cell; the r01/r04/r05 robustness figures including the exact D100 median tie at 2.59 and 0 sign reversals; every F26 descriptive value. **Zero mismatches.** For a manuscript of this size that is unusual, and it is the foundation everything else rests on.
2. **The method's printed specification is correct where it matters most.** All thirteen displayed equations were recomputed symbolically against the byte-locked source. The specific defect this profile exists to catch — the SGSM interaction-graph EMA — is genuinely fixed and verified: `interaction_graph.py:201` `matrix*=decay` and `:344` `matrix+=lr*agg` match the printed `G←λG+ηΣ`. Section 10.6's exemplar failure is absent.
3. **Loss visibility is exemplary and should be advertised as such.** The abstract itself carries the second place at D=30, the Holm-significant CEC2011 loss to eGSK, and the non-separability of the nearest comparator. The cover letter reports the ISM isolation as a controlled negative result. Very few papers in this literature put their adverse cells in the abstract. This is the package's strongest differentiator for *Algorithms*, which values reproducible and honestly bounded algorithmic work.
4. **Evidence immutability is real, not asserted.** 3,403/3,403 release checksums over 712 MB with zero mismatches; 130/130 analysis-bundle; 59/59 exhibit checksums; 1,239 source opens with zero outside the release; a 70,813-row seed audit reconciling exactly; the printed seed formula re-derived over 32,250 rows; threefry in all 36 cells; zero duplicate seeds and zero NaN/Inf. The evidence lock of section 10.3 holds.
5. **The section 10.9 prohibition holds in the direction that matters.** No favourable component result leaks into the main text — notably the Holm-significant final-polish effect stays supplementary. Three seats checked this independently. The advertised null is permitted by the narrowing and is not a leak.
6. **Comparator fairness holds structurally even where it is under-described.** Seeds are identical across all seven optimizers on every pairing key; `nfes` never exceeds MaxFES anywhere; 6/7 CEC2017 schedules are byte-identical; the evaluator FP probe hash and `workers:15` are identical across all 21 cells; the eGSK polish is budget-capped and fully charged; convergence panels aggregate from complete `gen_logs` with 0 ragged or blank files across 400.
7. **The conflict-of-interest declaration is exactly accurate.** Five of six comparators are Mohamed-co-authored and FDB-AGSK is third-party — checked against the sources. Self-citation at 7/40 references and 41/117 occurrences is structurally forced by an intra-family study, doubly disclosed, and used adversely as often as favourably.
8. **The prose is human.** Zero canonical AI tells across the whole package; no claims-strengthening; no detector-evasion editing. The de-formulaic pass succeeded and should not be re-litigated.

---

## 12.6 Top ten rejection risks

Ranked by combined probability and impact. Reviewer wording is written as it would plausibly appear in a report.

| # | Risk | Likely reviewer/editor wording | Probability | Mitigation |
|---|---|---|---|---|
| 1 | **Effect-size column does not exist** (SE-001) | "Section 4.2.3 discusses 'the $A_{12}$ column' of Table 14 at length and quotes four values from it. Table 14 has no such column, and I cannot locate these numbers in the supplied data. The same paragraph calls two different statistics 'the tabulated effect size'." | **Very high** — one glance at the table | Settle the referent; delete or relocate the four quotations; consolidate the duplicated definition. Text-only. |
| 2 | **Budget-fairness claim contradicted by the authors' own data** (SE-002) | "The paper states all seven optimizers receive exactly the same MaxFES charge. Sorting the supplied `per_run.csv` on `termination` shows 1,845 AGSK/APGSK runs stopping early, one at 44,497 of 1,000,000." | **High** — the data ships with the paper | State the asymmetry and the floor argument that makes it harmless. Text-only. |
| 3 | **Population-size asymmetry at the headline dimension** (SE-008) | "DT-GSK runs NP=5·D (500 at D=100) while every comparator runs NP=100 at all dimensions. The panel table attributes 'published reference constants' that specify 20·D, 200·D and 40·D. How much of the D=100 result is the population schedule?" | **High** — visible in the released configs | Disclose the executed configuration; name the confound in the limitations; optionally run a published-NP sensitivity cell (Q1 work). |
| 4 | **Proposed method's curve is unlabelled** (SE-005) | "In Figures 6 and 7 the legend is cut off at both edges; I cannot tell which curve is DT-GSK." | **High** — the reader hits it on p.28 | Regenerate all 25 figures with a wrapped legend and tight bounding box; add an automated off-canvas assertion. |
| 5 | **The paper's question is the one it answers negatively** (SE-030, SE-015) | "The introduction frames the work around learning interaction structure; Section 4 reports that the structure memory has no detectable standalone benefit. What, then, is the thesis? And the one element claimed as original is excluded from every ablation." | **Medium-high** — a thoughtful referee | Re-frame around dimension-tiered control and the deterministic endgame; narrow C2; state the ARGP exclusion plainly. |
| 6 | **Undisclosed selection multiplicity on the development suite** (SE-014, SE-016) | "The configuration was selected on CEC2017, on which the headline rank is reported. 'Several candidate configurations' is not a number, and no parameter sensitivity is reported at all." | **Medium-high** | Attest the count, cells and criterion (zero compute); disclose the sensitivity absence. |
| 7 | **Reproducibility route does not work** (SE-004, SE-003) | "I followed the runbook named in the Data Availability statement. It cites a superseded release, omits the analysis-bundle generator entirely, and its ablation run count does not match the paper." | **Medium** — only a reviewer who tries | Rewrite the runbook and re-point the manifest; demonstrate a clean end-to-end rebuild. |
| 8 | **Declared statistic is not the reported statistic** (SE-007) | "Section 4.1 declares the tie-corrected Iman–Davenport statistic, but the CEC2017 and CEC2013 p-values are the uncorrected ones while CEC2011 is corrected. Which was used?" | **Medium** — a statistically careful referee | Print the corrected column on all three suites; fix the caption bound. |
| 9 | **GenAI declaration is falsifiable from the public repository** (SE-010) | "The declaration states the implementation was produced independently of any AI system. The linked repository shows AI co-authorship trailers on 231 of 384 commits, including one that modifies the optimizer core and triggered the evidence regeneration." | **Low-medium** probability, **high** impact if raised | Narrow the declaration to what is accurate; name every model version. Cheapest fix in the package. |
| 10 | **Same-family panel over-read** (section 10.5) | "All comparisons are intra-family. The paper says so, but the abstract's framing invites a broader reading." | **Medium** | The manuscript already scopes every comparative claim to the panel and makes no field-wide claim; keep it that way through revision. External baselines are out of scope for this cycle by directive — see residual risk R7. |

---

## 12.7 Critical and major issue register

**Zero Critical. Seventeen Major, ordered by dependency and priority.** Full schema in `issue_register.csv`.

| ID | Sev/Pri | Gate | Issue | Fix class |
|---|---|---|---|---|
| SE-003 | Major P1 | A, L | Freeze anchor does not contain the pinned bytes; manifest reproduces only on the author's disk (SE-measured: 15/15 worktree, 10/15 HEAD, 7/15 anchor) | governance + re-freeze |
| SE-004 | Major P1 | L | `reproducibility_manifest.json` two releases stale; `runbook.md` does not reproduce the paper | governance |
| SE-002 | Major P1 | C, H | "All seven optimizers held to exactly the same MaxFES charge" false — 1,845 early-stopped runs | text |
| SE-008 | Major P1 | H | Comparator NP undisclosed; "published reference constants" false; 5x asymmetry at D=100 | text |
| SE-009 | Major P1 | G, H, J | Cross-commit determinism failure (3,772 diffs) invisible to the reader | text |
| SE-011 | Major P1 | H | eGSK solver substitution bounded only for runtime, not performance | text |
| SE-012 | Major P1 | F | Three shipped ISM parameters in no specification surface; linkage channel overstated ~2x | text |
| SE-001 | Major P1 | C, I, J, M | A12 column does not exist; paragraph self-contradicts on the tabulated statistic | text (+ optional exhibit) |
| SE-007 | Major P1 | I, J | Omnibus p-values mix corrected and uncorrected columns across suites | text |
| SE-017 | Major P2 | C, J | APGSK per-run data declared unavailable after it was recovered — false existence claim | text |
| SE-005 | Major P1 | M | Legend off-canvas in 25/25 convergence figures incl. both main-text figures; DT-GSK label lost | figure regeneration |
| SE-006 | Major P1 | M, P | Supplement Table A19 overflows 218.99 pt; Notes column lost from the PDF, present in the DOCX | typesetting |
| SE-013 | Major P2 | M | Figure 4 in-figure text at 4.2–5.2 pt; CD bar renders at four physical lengths | figure regeneration |
| SE-010 | Major P1 | O | GenAI declaration asserts AI-independence of the implementation; contradicted by public commit metadata | text |
| SE-014 | Major P2 | I | Selection exposure disclosed without a count, cells, or criterion | author attestation (0 compute) |
| SE-015 | Major P2 | D, K | ARGP — sole C2 originality claim — untested; "each scaffold subsystem" false | text |
| SE-016 | Major P2 | K | Zero parameter-sensitivity evidence, undisclosed | text |

**Dependency note.** SE-030 (thesis framing, Moderate) is not Major but must be **decided first**: SE-015, SE-021 and SE-036 all polish prose that SE-030 may re-frame. Stage 20's rule — *do not polish prose around a claim that may later be removed* — binds here.

---

## 12.8 Full issue register

`papers/review_2026_07_22/issue_register.csv` — 56 consolidated tickets in the section 5.4 mandatory schema, with two added columns (`source_seat_tickets`, `se_adjudication`) recording provenance and every contradiction resolution.

**Composition:** 0 Critical · 17 Major · 19 Moderate · 14 Minor/Editorial · 6 Rejected. Status: 50 open · 5 accepted_risk · 1 resolved.

**De-duplication:** roughly 200 seat findings consolidated. The largest merges are SE-001 (nine seat tickets across seven seats), SE-050 (fifteen), SE-045 (fourteen), SE-022 (eleven).

### Contradictions between seats, resolved

| Contradiction | Resolution |
|---|---|
| Freeze-anchor magnitude: s0-1 "11/15 at anchor" vs s7-12 "10/15 from `git archive HEAD`" | **SE measured directly; both are partially right.** Working tree 15/15; HEAD 10/15 (matches s7-12 exactly); declared anchor **7/15**. s0-1's 11/15 was computed on line-ending-normalised content, not raw bytes. SE's figures govern (SE-003). |
| Page budget B1: s0-1 "34, or 35 under a stricter reading" vs s2-4 "35–36" vs s17 "35 or 36" | **SE adjudicates B1 = 35** (39 pp total; references pp.38–39; back matter pp.36–37). The cap is breached by one page. |
| Severity of the page/word cap breach: s2-4 and s17 framed it as near-desk-reject; s0-1 as a section 10.14 record failure | **s0-1's framing is correct.** The cap is *self-imposed*; MDPI *Algorithms* publishes no hard page limit, and 12,000 words is a contact-the-office threshold, not a rejection threshold. Downgraded Major to **Moderate** and re-scoped onto the missing gate measurement (SE-018). |
| R-09 residue severity: s8 Major P2 vs s3 Minor | **s3 is correct.** The shipped `cover_letter.pdf` (built from `.tex`) is correctly narrowed; only the non-shipped `.md` retains the old wording. Downgraded to **Minor** (SE-037). |
| s13's claim that DT-GSK "loses its label entirely" in the convergence legends | **UPHELD and escalated.** SE initially doubted it — all seven labels are present in the PDF *text layer*. Positional measurement with `pdfplumber` proved the seat right: `DT-GSK` spans x0=442.45 to x1=476.24 on a 443.88 pt page. Scope is wider than reported: **25/25 figures, including both main-text figures** (SE-005). |
| s16 rating the GenAI declaration Critical P0 vs the other seats not raising it at all | **Real defect, wrong severity.** SE reproduced the evidence exactly (231/384 commits; the `af7efc534` trailer verified). Downgraded to **Major P1**: no scientific claim, number or result is affected, and no misconduct is established — a Claude Code trailer stamps every commit made through the tool. It remains a hard Gate O blocker (SE-010). |
| s9 rating the rank-biserial sign convention Major vs s3 and s10-11 rating it Minor | **Minor.** The paper is internally consistent with its own stated direction; the defect is that the released workbook's operand *labels* are not aligned to it (SE-042). |
| s16 counting six author-metadata items toward a Gate O BLOCK vs s15 recording them as advisory | **s15 is correct.** Section 1.5.4 is normative and explicit: raise no ticket, fail no gate on submission metadata. Rejected as findings (SE-R01, SE-R02, and the locator half of SE-033); carried on the upload checklist only. |
| s9's Gate I FAIL vs s10-11's "arithmetic integrity is not the problem" | **Not a contradiction — both hold, and together they characterise the package.** Zero numerical errors across roughly 200 recomputed quantities *and* Gate I fails, because every defect is in the printed specification, provenance, or governance rather than in a number. |

---

## 12.9 Claim audit and claims ceiling

### High-visibility claims and verified status

| Claim | Locus | Verdict |
|---|---|---|
| Best overall CEC2017 Friedman mean rank in the panel (2.48; eGSK 2.96) | Abstract, cover letter | **Supported and exact.** Descriptive mean of four per-dimension ranks, correctly framed as descriptive. The cover letter must carry the abstract's qualifiers (SE-029). |
| Second at D=30; Holm-significant CEC2011 loss to eGSK; never Nemenyi-separable | Abstract | **Supported.** The CEC2013 leg of "never Nemenyi-separable" is true but typeset nowhere — scope it or add the exhibit (SE-043). |
| CEC2013 overall first place (2.80) | Section 4 | **Supported**, but rests on 3/6 and 1/6 significant pairwise cells; the matrix appears in neither document (SE-046). |
| ISM isolation finds no detectable standalone benefit | Abstract, introduction, Section 4, conclusions, cover letter | **Supported as a failure to detect.** Overstated where framed as "a boundary on the idea" or "answers in the negative" (SE-021). *Not* a section 10.9 leak — the narrowing permits it. |
| Budget-fair: all seven charged exactly MaxFES | Section 4.1 | **UNSUPPORTED as printed** (SE-002). The counted charge never exceeds MaxFES; the equality claim is false. |
| Runs are budget-exact and repeat-identical | Section 4.1 | **Over-scoped** (SE-009). True for DT-GSK single-threaded; comparator re-execution measured 3,772 scientific-column diffs. |
| Verified bit-identical under strict truncation for all seven optimizers | Section 4.1 | **Over-generalised** (SE-047). Rests on one synthetic cell; the stronger structural warrant (the counted-prefix invariant) is unstated. |
| Comparators ran published reference constants | Table 3 | **UNSUPPORTED** (SE-008). All six ran NP=100 at every dimension. |
| Every empirical value derives from a single immutable release | Section 4.1 | **Supported** (1,239 source opens, 0 outside the release), but contradicted by the supplement's "distinct, immutable ablation release" wording (SE-046). |
| Remove-one study examines each scaffold subsystem | Section 3 | **UNSUPPORTED** (SE-015). Three of six mechanisms are pre-specified exclusions. |
| APGSK run-level companion analyses unavailable at D<=50 | Section 4 | **FALSE existence claim** (SE-017). 29 rows exist, all `availability=ok`. |
| No AI system contributed to design, execution or analysis; implementation produced independently of any AI | Back matter, Section 4.1, cover letter | **The first half is supportable; the second is falsifiable** (SE-010). |

**Claims requiring new evidence: none.** Every correction is text, exhibit regeneration, or a zero-compute attestation.

**Claims to remove: none from the abstract or conclusions.** Four require narrowing — budget fairness, determinism scope, the ISM null's strength, and the effect-size referent.

**Claims to move to the supplement: none.** The section 10.9 direction of travel is already correct, and the narrowing is symmetric: a favourable component result may not be back-ported either.

**Strongest defensible abstract statement, after correction:**

> Within a seven-algorithm GSK-family panel evaluated under a single frozen protocol, DT-GSK attains the best overall CEC2017 Friedman mean rank (2.48, the unweighted mean of four per-dimension ranks; eGSK second at 2.96), places second at *D*=30, loses significantly to eGSK on CEC2011 under Holm correction, and is never separable from the nearest comparator by the Nemenyi critical difference. CEC2017 was the development suite on which the configuration was selected; CEC2013 and CEC2011 are corroborative. A direct isolation of the interaction-structure memory finds no detectable standalone benefit at its active tiers. All comparative claims are scoped to this panel; no field-wide claim is made.

That statement is fully supported by the frozen release today, and it is the ceiling.

---

## 12.10 Scientific review by stage

**Stages 0–1 (package, requirements).** One authoritative readable state; all shipped gates green — SE re-ran `check_manifest` (15/15), `validate_provenance_claims` (OK), `validate_cross_format_parity` (579 rows, 0 FAIL), `validate_document_consistency` (OK), `validate_build_hygiene` (OK). `requirements_compliance_matrix.csv`: 57 rows — **24 met / 18 partially met / 8 unmet / 6 n-a / 1 blocked**. Gate A fails on freeze traceability, not on package readability.

**Stages 2 and 4 (desk screening, significance).** Fit is good for MDPI *Algorithms*. Disposition: editorial revision before review. No scientific blocker; every finding text-correctable.

**Stage 3 (claims).** 72 claims audited, 16 tickets. Four require narrowing, none requires removal, and all three suggested evidence additions are read-only.

**Stage 5 (literature).** 57 bib entries to 57 local PDFs; 40/40 cited; 117/117 occurrences mapped; no fabricated reference, no material mis-citation, no patchwriting. One omitted author, one adverse competitor mischaracterisation, and the section 10.2 controls enforced by no validator.

**Stage 6 (method and theory).** All 13 displayed equations recomputed symbolically; none wrong. Evaluation accounting sound. Three ISM parameters unpublished; R-01 and R-02 propagation incomplete.

**Stages 7–12 (evidence, reproducibility).** Gate G passes on recomputation; Gate L fails on the published route. The distinction matters and should be stated plainly to the authors: the evidence is sound, the instructions for reaching it are not.

**Stage 8 (design, fairness).** Comparator classification: GSK **A**, ATMALS-GSK **A**, AGSK **B**, APGSK **B**, FDB-AGSK **B**, eGSK **B**. None is class C or D; none must be excluded from formal claims; four require a declared deviation the manuscript does not currently declare.

**Stage 9 (statistics).** Roughly 200 quantities recomputed, zero mismatches. Every defect is specification, provenance, or governance.

**Stages 10–11 (results, robustness).** Headline arithmetic exact; loss visibility exemplary. Robustness fails on the sensitivity absence and the ARGP exclusion.

**Stage 13 (exhibits).** 56 artifacts audited. Gate M fails on measured legibility and off-canvas rendering, not on data accuracy — all 124+22+28 convergence panels carry 7/7 series with no interpolation and no undisclosed absence.

**Stage 14 (sections).** Aggregate section score 3.56/5. Critical section findings map to Gates C, J and N per the section 12.4 note.

**Stage 15 (writing).** Gate N conditional pass. The headline finding is negative in the right direction: zero canonical AI tells across the package.

**Stage 16 (ethics, AI disclosure).** One real defect (SE-010); several out-of-scope items rejected. No AI author, no retracted reference, no fabricated administrative value.

**Stage 17 (production).** Gate P blocked administratively; four production findings, of which Table A19 is a genuine content divergence.

### Domain modules activated

**Section 9 Module A — evolutionary computation, metaheuristics, stochastic optimization** is the only applicable module and was activated in full. Findings: budget accounting is sound by construction but the fairness *claim* over-reaches (SE-002); the population-size asymmetry is undisclosed (SE-008); comparator provenance is misstated (SE-008, SE-011); the seven-method panel is intact and correctly scoped to the family, satisfying section 10.5; convergence aggregation is uniform and complete; and no convergence guarantee is claimed or smuggled anywhere in the method.

### Section 10 profile compliance

| Control | Status |
|---|---|
| 10.1 Governing-source and governance-artifact audit | **PARTIALLY MET** — matrix produced; bindings stale or unresolvable (SE-022, SE-025); two bound paths do not exist (SE-050) |
| 10.2 Closed-corpus literature boundary | **PARTIALLY MET** — boundary holds; role map holed at the highest-traffic key; no validator enforces it (SE-025) |
| 10.3 Empirical evidence lock | **MET** for the lock (3,403/3,403 checksums; 1,239 opens, 0 outside); **UNMET** for the determinism contract (SE-004) |
| 10.4 Seven-method panel and protocol scope | **PARTIALLY MET** — panel intact and verified; MaxFES and NP descriptions inaccurate (SE-002, SE-008) |
| 10.5 Same-family claim boundary | **MET** — every comparative claim panel-scoped; no field-wide claim |
| 10.6 Method and implementation correspondence | **PARTIALLY MET** — exemplar defect absent, all equations correct; three parameters unpublished (SE-012) |
| 10.7 Statistics profile and advanced dispositions | **PARTIALLY MET** — descriptive overall-rank framing, per-run-gap and pairing dispositions all correct; recovery-versus-comparability half-applied (SE-017); register rows missing (SE-020) |
| 10.8 Convergence profile | **PARTIALLY MET** — aggregation uniform, 7/7 series everywhere, adverse case visible; legends clipped (SE-005) |
| 10.9 Main-manuscript ablation prohibition | **MET** — no favourable component result leaks; the advertised null is permitted by the narrowing; overstatement ticketed separately at SE-021 |
| 10.10 Final ablation profile | **PARTIALLY MET** — protocol sound; ARGP, polish and restart excluded, and the main text misdescribes the coverage (SE-015) |
| 10.11 Exhibit and source-binding profile | **PARTIALLY MET** — no hand-edited number, no exhibit sourcing another; binding registry has gaps (SE-022) |
| 10.12 Dual-format profile | **PARTIALLY MET** — 0 rasterised tables or equations, native OMML, parity 579/0; geometry mismatch and one real content divergence (SE-031, SE-006) |
| 10.13 DT-GSK hard rejection risks | **3 of 14 live** — bundle-without-thesis (SE-030), eGSK provenance and solver (SE-011), missing overhead analysis (SE-044) |
| 10.14 Page-limit hard rule | **UNMET** — no page-count row for the shipped build; B1=35 against a self-imposed cap of 34 (SE-018) |
| 10.15 Presentation conventions and exemplar parity | **MET** — `jawad2024egsk` metadata correct; no prose labels eGSK by year; no mechanical copying of the exemplars |
| 10.17 Human-authored presentation | **PARTIALLY MET** — prose passes cleanly (Gate N); pseudocode collides with the number gutter and figures clip (SE-005, SE-026) |

---

## 12.11 Missing experiments and analyses

Classified with the controlled vocabulary of section 12.11 and Appendix A.5. Full register: `missing_experiment_register.csv` (Stage 8).

**`essential_before_submission` — one item, zero compute**

- **MX-04 · Selection-exposure attestation** (SE-014). *Minimum valid design:* an author statement of how many full-panel candidate configurations were evaluated, on which cells, and by what criterion the shipped profile was chosen. *Claim it supports:* bounds optimistic-selection bias on the CEC2017 headline. *Cost:* none — it is recollection, not computation.

**`recommended_for_q1` — two items**

- **MX-01 · eGSK solver sensitivity** (SE-011). *Design:* re-run eGSK on a subset of cells with the SLSQP polish disabled or capped differently, to bound how much of eGSK's standing is the substitution. *Supports or refutes:* whether the DT-GSK-versus-eGSK comparison is class A or class B.
- **MX-02 · Published-NP sensitivity** (SE-008). *Design:* re-run AGSK, APGSK and FDB-AGSK at their published NP (20·D, 200·D, 40·D) on CEC2017 D=100. *Supports or refutes:* whether the D=100 standing survives removal of the population asymmetry. **This is the single most valuable additional experiment in the package**, and the one a Q1 referee is most likely to demand.

**`useful_for_q2` — three items**

- MX-03, parameter sensitivity on the tier constants (SE-016); MX-05, an ARGP isolation cell (SE-015); MX-07, comparator wall-clock on one idle machine (SE-044).

**`optional_or_out_of_scope` — one item**

- **MX-06 · External non-GSK baseline panel.** Recorded with **no ticket and no gate consequence** per section 1.5.4. See residual risk R7 — this is a scope decision of *this review cycle*, not a prediction that external referees will accept it.

**Nothing on this list is required to make the current claims true.** What is required before submission is *disclosure*, which is text-only and fully compatible with the no-rerun, no-new-release, byte-locked-core constraints.

---

## 12.12 Independent reviewer reports

The eight simulated seats (EIC, AE, R1–R6) are recorded un-harmonised in `independent_reviewer_reports.md`, with five disagreements deliberately preserved. Specialist-role pre-consensus findings are in the seat artifacts named below. **Consensus recommendation across the eight simulated seats was `Minor revision` with external review justified; the Supervising Editor's consolidated disposition is `D2 — Major pre-submission revision`.**

The divergence is deliberate and worth stating plainly. The reviewer-simulation seat is modelling *what external referees would say about the paper as a scientific contribution*, and on that axis the paper is in good shape — the numbers are right, the honesty is real, the method is correct. The Supervising Editor is judging *whether the package should be uploaded today*, and it should not: seventeen Major tickets are open, four of them checkable by a referee in under a minute, and three hard gates (I, L, M) plus Gate O fail. Both judgements are correct at their own altitude. If every Major ticket is closed, I expect the external outcome to land at minor revision, which is what the simulation predicts.

| Seat / role | Lead stage | Disposition | Artifact |
|---|---|---|---|
| Preflight (Stage 0/Gate A) | 0–1 | Stage 0 PASS, Gate A PASS with 4 open P1 (SE now sets Gate A **FAIL** on measured freeze traceability) | `review_configuration.md`, `requirements_compliance_matrix.csv` |
| EIC / desk | 2, 4 | Editorial revision before review | `desk_screening_report.md` |
| RI (claims) | 3 | 16 tickets; no claim removal required | `claim_audit.csv` |
| RI (literature) | 5 | Gate E pass with conditions | `citation_and_literature_audit.md` |
| R-method | 6 | Gate F conditional pass; 4/5 | `method_and_theory_audit.md` |
| REP (evidence, reproducibility) | 7–12 | Gate G PASS, Gate L FAIL | `evidence_and_reproducibility_audit.md` |
| R-design | 8 | Gate H pass with required corrections; 3/5 | `experimental_design_audit.md`, `missing_experiment_register.csv` |
| R-stats | 9 | Gate I FAIL; 3/5 | `statistical_audit.md` |
| R-results | 10–11 | Gates J and K conditional FAIL | `results_integrity_audit.md` |
| VIZ (exhibits) | 13 | Gate M FAIL | `exhibit_audit.csv` |
| R-sections | 14 | Major revision; 3.56/5 | `section_review.md` |
| RW (writing) | 15 | Gate N pass with required corrections; 4/5 | `writing_integrity_audit.md` |
| JCO (ethics, AI) | 16 | Gate O FAIL (SE downgrades the Critical to Major) | `ethics_and_compliance_audit.md`, `ai_disclosure_audit.md` |
| PROD-PDF / PROD-WORD | 17 | Gate P BLOCKED | `journal_compliance_matrix.csv`, `pdf_build_report.md`, `word_validation_report.md`, `cross_format_consistency_report.md` |
| EIC, AE, R1–R6 simulation | 18 | Minor revision | `independent_reviewer_reports.md`, `predicted_reviewer_questions.md` |

### Preserved disagreements not resolved by consensus

1. **Severity of the page and word budget.** s2-4 and s17 read it as a near-desk-reject; s0-1 and SE read it as a governance-record failure against a self-imposed cap. SE's reading governs; the dissent is recorded because if MDPI *Algorithms* has in fact adopted a hard limit since Phase 4 (unverifiable — HTTP 403), s2-4's reading becomes correct.
2. **Whether the GenAI declaration is Critical.** s16 says yes; SE says Major. Both agree it is a hard Gate O blocker; the disagreement is only about whether the word "Critical" is proportionate to a wording defect with no scientific consequence.
3. **Whether the advertised ISM null is over-exposed.** s18's AE seat counts six main-text plus two cover-letter sites and calls it a scope excess; SE holds it is permitted by the section 10.9 narrowing and ticketed only where overstated (SE-021).
4. **Whether the NP asymmetry is a fairness defect or a disclosure defect.** s10-11 leans toward the former; s8 and SE toward the latter — DT-GSK's population schedule is contribution C2, so running it is not unfair; not saying so is.
5. **Whether `cover_letter.md` matters.** s8 Major, s3 Minor. SE sides with s3.

---

## 12.13 Predicted reviewer questions and response preparation

48 questions are prepared in `predicted_reviewer_questions.md` (25 mandated, 16 manuscript-specific, 7 ready-answer, with a response-letter priority ordering). The twelve most likely, with what constitutes a convincing response:

| # | Question | Convincing response |
|---|---|---|
| 1 | Where is the A12 column you discuss at length? | Correct the referent (SE-001). There is no defence; this must be fixed in the manuscript, not argued in the letter. |
| 2 | Your data shows 1,845 runs stopping below MaxFES. How is the budget equal? | State the count and the floor argument: the stop fires at the 1e-8 reporting floor, so the recorded error is already at the floor and no statistic moves (SE-002). |
| 3 | DT-GSK runs 5·D and every comparator runs 100. Is the D=100 result a population effect? | Disclose the configuration; state that the schedule is contribution C2; concede that no published-NP sensitivity was run and that the question is open (SE-008). Do **not** claim it was controlled. |
| 4 | Which curve is DT-GSK in Figures 6 and 7? | Regenerate the figures (SE-005). |
| 5 | Section 4.1 declares the tie-corrected statistic; the p-values are uncorrected. Which? | Print the corrected column on all three suites (SE-007). |
| 6 | How many configurations did you try before choosing this one? | Attest the count, cells and criterion (SE-014). An honest number, however large, is stronger than "several". |
| 7 | Your central mechanism shows no benefit. What is the paper's thesis? | Re-frame around dimension-tiered control and the deterministic endgame; present the null as a bounded negative result within that frame (SE-030). |
| 8 | Is the eGSK comparison fair given the solver substitution? | Extend the disclosure to performance and classify the comparison as class B (SE-011). Optionally run MX-01. |
| 9 | I followed your runbook and could not reproduce the paper. | Rewrite the runbook and demonstrate a clean end-to-end rebuild (SE-004). |
| 10 | Why is there no sensitivity analysis for a parameter-schedule contribution? | Disclose the absence as a limitation (SE-016); optionally run MX-03. |
| 11 | Why no comparison against L-SHADE or CMA-ES? | State the intra-family scoping as a deliberate design choice with the reason (controlled family-internal attribution), and point at the existing limitation. This answer is *weaker* than the others — see residual risk R7. |
| 12 | Your declaration says no AI touched the implementation, but your repository says otherwise. | Fix the declaration before submission (SE-010). This question must never be asked. |

---

## 12.14 Writing and language report

**Overall clarity: strong.** Full analysis in `writing_integrity_audit.md` — prose profile, three frequency tables, terminology list, five coherence issues, sixteen tickets, twenty-two worked revisions, twelve generic sentences to cut, a style-only checklist, and the authorship note.

**Recurring formulaic patterns:** the canonical AI tells are **absent** — zero occurrences of *Moreover, Furthermore, Additionally, Notably, It is worth noting, delve, leverage, crucial role, paves the way, comprehensive, remarkably* across the entire package. What remains is a human voice with tics: 98 sentences over 55 words (longest 106), 35 with two or more semicolons, 18 announce-scaffold openers, and roughly 16 transparency meta-clauses ("discussed rather than skipped", "disclosed up front", "labeled honestly", "transparently" twice in a two-page cover letter).

**Terminology problems:** the titular C1 mechanism has **nine** reader-facing names; the title's "Deterministic Refinement" and the abstract's "eigenframe refinement" never recur in the body, which says "eigenframe final polish" thirteen times. The headline null alternates between "no **detectable**" (3×) and "no **significant**" (5×) standalone benefit, both forms inside `main.tex` and both inside the cover letter.

**Highest-impact revisions:** consolidate the rank-biserial definition, stated **twice inside one paragraph** (`performance.tex:209-213` and `:227-231`); de-pack the 106-word sentence; unify the C1 mechanism name to the title's term; remove the transparency framing while keeping every disclosure intact.

**Generic or promotional phrasing to remove:** the transparency meta-clauses above; "a boundary we believe is itself informative"; "To our knowledge" attached to a self-measured fact in the cover letter.

**Passages needing factual verification before rewriting — do not touch until the ticket is decided:** the entire effect-size paragraph (SE-001), the omnibus sentences (SE-007), the budget-fairness sentence (SE-002), the determinism sentences (SE-009), and the "Eleven limitations" count (SE-028). Style editing over an undecided claim is how numbers drift.

**Style-only rules:** American English throughout — four British strays (`characterise` ×2, `behaviour`, `favourable`) propagate into both `*_pandoc.tex` DOCX sources; one caption sentence repeats across sixteen supplement captions; abstract is 201 tokens against its own ≤200 constraint, enforced by no validator.

**Authorship and tool-disclosure note.** No AI author appears anywhere, and none should. The GenAI declaration is present, correctly placed at all four required loci, and MDPI-policy-shaped — but its absolute exclusion clause over-reaches and must be narrowed (SE-010). Every writing change in this review is **de-cluttering for authorship quality, never detector evasion** (section 15.5). s15 found no detector-evasion editing and no claims-strengthening, and SE explicitly endorses s15's guard against the opposite error: legitimately formal, information-dense scientific writing is **not** a defect, and a false "this reads as AI" flag on sound expert prose is itself a review error.

---

## 12.15 Revision roadmap

Full dependency-aware plan with Appendix A.8 schema in `revision_roadmap.md`; ticket-by-ticket recheck and regression plan in `post_revision_verification.csv`. Grouped as section 12.15 requires:

1. **Scientific blockers** — W01 freeze envelope and reproducibility route (SE-003, SE-004); W02 protocol-disclosure paragraph (SE-002, SE-008, SE-009, SE-011); W03 GenAI declaration (SE-010).
2. **Analysis and experiment work** — W04 selection-exposure attestation (SE-014, zero compute); W05 statistical governance backfill (SE-020, SE-046). No rerun; no new release.
3. **Claim and interpretation corrections** — W06 thesis-framing decision (SE-030) **first**; then W07 effect-size referent and omnibus columns (SE-001, SE-007, SE-019, SE-042); W08 claim narrowing (SE-015, SE-016, SE-017, SE-021, SE-028, SE-047).
4. **Exhibit regeneration** — W09 convergence figures (SE-005); W10 Figure 4 (SE-013); W11 Table A19 (SE-006); W12 exhibit consistency cluster (SE-026, SE-039, SE-045).
5. **Structural revision** — W13 sections, limitations, supplement listing (SE-028, SE-039); W14 page and word budget (SE-018).
6. **Language revision** — W15 (SE-036, SE-029) — **strictly after** W06–W08.
7. **Journal and production work** — W16 Word geometry and validators (SE-031, SE-032); W17 citations and DOIs (SE-023, SE-024, SE-025, SE-034); W18 class and metadata (SE-048); W19 governance hygiene (SE-022, SE-035, SE-037, SE-038, SE-040, SE-041, SE-049, SE-050).
8. **Final validation** — W20 full rebuild, all gates, clean-room `check_manifest`, Gate Q.

---

## 12.16 Final internal recommendation

### `D2 — MAJOR PRE-SUBMISSION REVISION`

**Present readiness.** Not submission-ready. Weighted readiness score **64.60/100**. Seventeen Major tickets open, zero Critical. Gates A, C, H, I, J, K, L, M and O FAIL; Gate P BLOCKED administratively; Gates B, D, E, F, G, N pass conditionally. Section 11.1 is decisive on its own terms: an open Major ticket forbids a submission-ready classification, and there are seventeen.

**Expected readiness after the specified corrections.** **`D4 — Q2-READY CANDIDATE`.** Closing all seventeen Major and the nineteen Moderate tickets should lift the categories to approximately: journal fit 4.5, novelty 3.5, method 4.5, design 4.0, statistics 4.5, evidence 4.5, results 4.5, robustness 3.5, reproducibility 4.5, writing/exhibits 4.5, ethics/production 4.5 — a weighted score near **83**, above the 82 Q2 threshold. Novelty and robustness would remain at 3.5, below the 4.0 core floor, so **a strict reading leaves the package at `Minor pre-submission revision` rather than a clean Q2-ready classification unless C2 is genuinely re-scoped (SE-015) and the sensitivity absence is either filled by MX-03 or accepted as a disclosed boundary.** I recommend the disclosure route and the honest 3.5: this is a solid Q2 paper, and claiming otherwise is the very failure mode the package was built to avoid.

**Is the target journal appropriate?** **Yes.** MDPI *Algorithms* is a good fit: an algorithmic contribution with a fully specified mechanism, a reproducible artifact chain, and panel-scoped empirical evidence. Nothing in this review suggests a venue change. If the authors want a higher-impact venue, the required work is MX-02 and an external panel — a different research cycle, not a revision.

**Is a Q1 or Q2 claim justified?** Q2 is justified as an achievable outcome. **Q1 is an aspiration only** and should not be pursued in this cycle. Section 11.3 requires "evidence breadth and depth proportionate to the claims" and "no weak or missing load-bearing analysis"; the development-exposed headline suite, the never-separable nearest comparator, the intra-family panel, and the untested ARGP each independently prevent that finding today.

**Residual uncertainties.**

- **R1.** Whether MDPI *Algorithms* has adopted a hard page or word limit since Phase 4. Unverifiable here (HTTP 403). If it has, SE-018 escalates to Major.
- **R2.** Whether the public repository is in fact public and whether its name matches the availability statement. SE could not verify from this environment; the wording defect (SE-033) stands regardless.
- **R3.** Whether the D=100 standing survives the population asymmetry. Unresolvable without MX-02. The paper can disclose it but cannot currently rebut it, and a determined referee may insist.
- **R4.** Whether the four A12 values were computed on the unit the prose states. Four seats recomputed them correctly from per-function means, so this is low-probability, but the value has no released row to check against until SE-001 is closed.
- **R5.** Whether the freeze can be made reproducible without disturbing the 15/15 property the package advertises. The `.gitattributes` fix is straightforward but will change hashes; SE-003 must be the **last** work item.
- **R6.** Whether the ARGP and deep-stall restart contribute at all. Never isolated; the paper will assert nothing about them after SE-015, which is the correct posture but leaves C2 thinner than written.
- **R7.** **The external-baseline scope decision.** Section 1.5.4 removed this from the review, and every seat complied. That directive binds *this panel*; it does not bind external referees. A referee at any venue may ask why a 2026 optimization paper compares only within one algorithm family, and the honest answer — controlled family-internal attribution — is a real answer but not a complete one. The authors should expect the question and should not be surprised that this review did not prepare them for it.

**Exact conditions for changing the decision.**

- **To `D3 — Minor pre-submission revision`:** all seventeen Major tickets closed with verification evidence, Gates A, C, H, I, J, K, L, M and O returned to PASS, and a clean-room `check_manifest` at 15/15.
- **To `D4 — Q2-READY CANDIDATE`:** the above, plus all nineteen Moderate tickets closed or formally accepted as risk under section 11.2 (documented reason, visible residual risk, EIC and specialist agreement, and any required qualification present in the manuscript), plus Gate P unblocked by a successful journal-instruction verification.
- **To `D6 — SCIENTIFICALLY READY, ADMINISTRATIVELY BLOCKED`:** if every scientific gate passes but the journal-instruction verification remains 403 and the author-side metadata (e-mail, ORCIDs, archive locator) is still outstanding at the point of decision.
- **Downgrade to `D1`** only if a rerun ever becomes necessary — nothing in this review requires one, and no finding here approaches that threshold.

---

## 12.17 Post-revision verification checklist

Ticket-linked and rerunnable. Full machine-readable form in `post_revision_verification.csv`. **Gate Q passes only when every row below is green.**

| # | Check | Command or method | Pass criterion | Tickets |
|---|---|---|---|---|
| 1 | Clean-room freeze | `git archive <new-anchor>` into an empty dir, then `check_manifest.py` | 15/15 **outside** the author's working tree | SE-003 |
| 2 | Reproducibility route | Execute the corrected `runbook.md` end to end from the release | Produced PDF matches `papers/DT-GSK.pdf`; manifest hashes equal shipped | SE-004 |
| 3 | Effect-size referent | Count `A_{12}` occurrences in `performance.tex` against A12 objects printed in `T15.tex` | Equal; every quoted statistic resolves to a released CSV column | SE-001 |
| 4 | Omnibus columns | Assert each printed omnibus p equals the **corrected** column of the released `statistical_results.csv` | All three suites match to printed precision | SE-007 |
| 5 | Budget census | Re-run the `termination` census over every `per_run.csv` | Printed count equals 1,845; the sentence renders in PDF and DOCX | SE-002 |
| 6 | Panel configuration | Assert Table 3's NP values equal every released `run_config.json` | Exact match for all seven | SE-008 |
| 7 | Figure canvas | For every figure PDF assert `min(x0) >= 0` and `max(x1) <= page_width` over all extracted words | Zero off-canvas glyphs in all 25 convergence figures | SE-005 |
| 8 | Figure legibility | Measure minimum glyph height in Figure 4 at final embedded scale | ≥ 8 pt | SE-013 |
| 9 | Supplement overflow | `grep -c Overfull papers/supplementary.log` | 0; all seven Table A19 Notes cells present on p.48 | SE-006 |
| 10 | GenAI declaration | Confirm revised wording at all four loci; extend `validate_document_consistency.py` past the cover letter | Renders in PDF and DOCX; validator covers all four | SE-010 |
| 11 | Determinism scope | grep every determinism sentence | Each scoped to DT-GSK; the comparator disclosure renders | SE-009 |
| 12 | APGSK availability | Assert every availability assertion matches the released `availability` flags | No false existence claim; runtime still correctly unavailable | SE-017 |
| 13 | Ablation coverage | grep "each scaffold subsystem" | Zero hits; the three exclusions stated in the main text | SE-015 |
| 14 | Selection exposure | Confirm the attested count, cells and criterion render | Present in supplement and echoed in main text | SE-014 |
| 15 | Sensitivity disclosure | Confirm the limitation sentence renders in both formats | Present | SE-016 |
| 16 | ISM parameters | Assert every `build_pub_config` parameter appears in the supplement specification table | Complete; linkage prose states the 0.5 mixture | SE-012 |
| 17 | Page and word budget | Re-measure B1 and B2 on the final build; assert a page-count row exists for it | Row present; cap met or formally waived | SE-018 |
| 18 | Bibliography | Diff every bib author list against its source PDF title page; re-query every printed DOI | Zero mismatches; all DOIs resolve | SE-023, SE-034 |
| 19 | Cross-format | `validate_cross_format_parity.py` with content-comparing equation and TOC rows | 0 FAIL, no unconditional PASS rows | SE-031 |
| 20 | Regression sweep | Re-run the section 10.9 leak test; re-read abstract, conclusions, highlights and cover letter | No favourable component result in the main text; no new unsupported claim | all |
| 21 | Number drift | Diff every numeric token in the manuscript before and after the language pass | Zero changes | SE-036 |
| 22 | Full gate suite | `check_manifest`, `validate_provenance_claims`, `validate_cross_format_parity`, `validate_document_consistency`, `validate_build_hygiene`, `validate_evidence_bindings`, `validate_docx` | All green, with the new assertions from rows 3, 4 and 7 added | all |

**Do not mark any ticket resolved because text changed.** Section 5.4 is explicit: close it only when the row above passes.
