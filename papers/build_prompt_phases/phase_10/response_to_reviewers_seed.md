# Response to Reviewers — SEED (Phase 10)

*Author-facing draft. Point-by-point seed for the rebuttal letter; edit tone and add author sign-off. Line/section pointers are to the revised build (`DT-GSK.pdf`, 35 pp). Numbers, algorithm, and evidence release are unchanged from the frozen build; all changes are prose/presentation. Items marked **[CHANGE-CONTROL]** need an author decision before the letter is finalized.*

We thank all six reviewers. Several noted that the manuscript's scope discipline, evidence provenance, and disclosure of unfavourable cells are "exemplary" / "close to a model"; we have preserved that discipline and confined every change to clarification, method description, and one presentation-only table. **No reported number was changed** — R2 and R3 independently confirmed every headline figure matches the release, and our own re-check found no numeric error.

---

## Reviewer 1 (Scientific)

- **R1-1 (importance rests on a deferred mechanism).** We agree the algorithmic-gain claim for ISM/polish is held to the Phase-12 component study, and we have made the main text state this without over-attribution: the Discussion now notes that the D≥50 tier activates several subsystems together, so high-dimension behaviour is associated with the bundled tier configuration rather than any isolated component (§4.7). We have **not** promoted an ablation into the main text, because doing so would require new analysis outside the frozen evidence release; the component study remains the Phase-12 deliverable. **[CHANGE-CONTROL: confirm the methodology/reproducibility-first framing is acceptable vs. promoting the ablation.]**
- **R1-2 (mechanistic distinction from CMA-ES/covariance).** Agreed and adopted. §3.5 now states outright that the accepted-move interaction matrix is *covariance-like* and that the eigenframe polish performs a *covariance-eigenbasis operation*, and relocates the novelty to the signed/decaying/accepted-move-only accumulation and the discrete exploitation rather than to the learned object being of a new type. §2.2 was aligned.
- **R1-3 (title "High-Dimensional").** **[CHANGE-CONTROL]** We take the point that the field reserves "high-dimensional" for n≈1000. The body already bounds the term (explicit D=100 ceiling, no LSGO claim, LM-05). Because the title propagates into the cover letter and metadata, we defer the wording to the authors; a softened option (e.g., scoping to the tested range) is recorded.
- **R1-4 (abstract qualifier).** Adopted: the abstract now marks 2.48/7 as "an unweighted across-dimension mean, no cross-dimension test."
- **R1-5 (no external baseline).** We have added this as an explicit **limitation** (not merely future work): the panel is entirely within-family and self-authored, and no external L-SHADE/CMA-ES/structure-learning anchor calibrates it against the field (Limitation 7). **[CHANGE-CONTROL: adding an external anchor requires a new run campaign under the locked protocol.]**
- **R1-6 (eGSK is a re-port; not separable).** These facts were already disclosed; we confirm they appear prominently (Evidence discipline §4.1, panel roster, runtime, Limitation 4, supplement S5) and that non-separation is stated in the abstract and §4.2.3. No headline implies an eGSK advantage.
- **R1-7 (missing limitations).** Added Limitation 6 (single host/environment; run-time SciPy behind eGSK uncaptured; single-thread precondition) and Limitation 7 (self-authored panel as a scientific threat; self-init fairness).

## Reviewer 2 (Statistics)

- **R2-1 (Wilcoxon zero-handling / approximation).** Added to §4.1: zeros under the |Δ|<1e-8 rule are discarded before ranking (`zero_method='wilcox'`), and p-values use the normal approximation with continuity correction (`scipy.stats`); effective post-zero n are in the released R⁺/R⁻ workbooks. No p-value recomputed.
- **R2-2 (Table 8 A12 basis).** Added to §4.1 and the Table 8 caption: the tabulated A₁₂ is computed over the 29 per-function means (the same unit as the across-function Wilcoxon) and is distinct from the run-level A₁₂ in the effect-size workbook; the 0.56/0.64/0.71 thresholds are descriptive labels here.
- **R2-3 (24-cell tally / Holm families).** The tally in §4.2.3 and §4.7 now states it aggregates four independent within-dimension Holm families (size 6) and is descriptive, not jointly FWER-controlled.
- **R2-4 (BCa on midranks).** §4.2.3 now notes the BCa resamples fixed per-function midranks and is read descriptively, not as a formal overlap test.
- **R2-5 (forward-reference tense).** Both pointers are now explicitly prospective and note that no component study is in the present supplement.
- **R2-6 (soft-attribution confound).** Addressed jointly with R1-1 by the D≥50 co-gating clause in §4.7.

## Reviewer 3 (Reproducibility)

- **R3-1 (FP-probe wording).** Corrected in §4.1 to scope the numerical probes to the shared RNG, the DT-GSK kernels, and the suite evaluators, and to note the comparator kernels carry no dedicated per-kernel hash.
- **R3-2 / R3-3 (environment & thread pinning).** Added: the single-thread byte-stability precondition at D≥50 (§4.1) and, in Limitation 6, the uncaptured run-time NumPy/SciPy versions behind eGSK's SLSQP and the parallel-speed-up cap.
- **R3-4 (persistent locator).** **[CHANGE-CONTROL / author-side]** The DOI/Zenodo/repository URL is an author-side submission item (AG-0006/R-0004); we will insert it at submission and have not fabricated one.
- **R3-5 (`-dirty` generation commit).** **[CHANGE-CONTROL / repo hygiene]** Outputs are checksum-pinned to the immutable release, so the numbers are locked; we will re-stamp the exhibit generators from a clean commit in a governance pass. No reported number is affected.

## Reviewer 4 (Editorial)

- **R4-T5 (CEC2013 has no in-text exhibit).** Adopted: a compact CEC2013 panel Friedman-rank table (7 algorithms × D10/D30/D50 + Overall) is now Table 10, surfacing the released numbers under the "second comparison suite / no independence claim" framing.
- **R4-T7 (dense abstract).** The mechanism sentence is split into three; the operator list is a shorter apposition. (Length re-verified ≤ 200 words.)
- **R4-T1, T2, T3, T4, T6 (figure internals).** **[CHANGE-CONTROL: figure-refresh pass]** We agree with all of these (E#↔Eq# mismatch incl. the Fig. 4 caption/graphic contradiction; Fig. 1 BibTeX keys; leaked repo paths; the SGSM alias in exhibits; the CD-diagram label vs. graphic). The four conceptual figures are pre-rendered, checksum-bound assets — one is exported from a `.drawio` source — so they must be regenerated together in a controlled figure pass to stay consistent; a turn-key equation remap and the key/label fixes are recorded in the revision log. The Abbreviations list already discloses "SGSM" correctly as an unexpanded code alias.

## Reviewer 5 (Word)

- **R5-3 (alt text).** The Word build already writes descriptive alt text (`wp:docPr/@descr`) on all 14 figures (validator: `images_with_alt = 14/14`); the generic string the reviewer saw is the display `@name`. No change required.
- **R5-5 (extra table).** The extra native table is a layout table; cross-format parity passes. (After adding Table 10: 11 numbered tables, 12 native `w:tbl`.)
- **R5-1 (TOC), R5-2 (IEEE style stamp), R5-4 (orphaned DOI rels).** All minor and currently correct; the TOC is refreshed on open (`updateFields=true`) and is part of the reserved author-side Word finalization, the IEEE numeric style equals MDPI `[n]`, and the orphaned relationships are cosmetic. We will address these in a build-tooling pass rather than risk the validated deterministic Word build.

## Reviewer 6 (Domain)

- **R6-T07 (loaded terminology).** Addressed with R1-2: §3.5 now states the graph records co-movement over coordinate *indices*, not recovered objective linkage.
- **R6-T08 (single-thread determinism).** Addressed with R3-3.
- **R6-T06 (self-init fairness).** Added as a caveat in Limitation 7. **[CHANGE-CONTROL: a shared-X₀ control run is new analysis.]**
- **R6-T05 (NLPSR).** The manuscript makes no empirical NLPSR-superiority claim and already scopes the tier-floor rationale to high dimension; the substantiating D100 cell is Phase-12 material.
- **R6-T02 (CEC2013 "External Hold-Out").** We believe this rests on a **non-shipped draft file** (`sections/supplementary_content.tex`), which is not compiled into the released supplement. The **shipped** supplement titles the section "CEC2013 Second Comparison Suite Detail" and states it "is not an independence argument of any kind" (PR-03), with no hold-out language. We will remove/reconcile the stale draft to prevent confusion. *[If the reviewer was given the draft file, we apologise for the ambiguity and confirm the released supplement is compliant.]*
- **R6-T01 (central primitive credited while its isolation is null).** The null 4-cell isolation the review cites is in the same non-shipped draft; the released supplement contains no ablation (S6 is a reserved Phase-12 slot) and the main text makes no component-causality claim. We have nonetheless removed any single-mechanism reading of the D≥50 gains (co-gating clause, §4.7). The direct component isolation will be reported, in full and with its inconclusive cells, in the Phase-12 supplement. **[CHANGE-CONTROL]**
- **R6-T03 (CEC2017 selection exposure).** **[CHANGE-CONTROL]** The 6-config exposure disclosure is likewise in the non-shipped draft; the released paper states only that a single frozen `pub` profile is used with no per-suite tuning, and makes no "development suite" claim. We will surface the selection-exposure accounting alongside the Phase-12 tuning-protocol disclosure.

---

### Summary of manuscript changes
Abstract rewritten for readability + aggregate qualifier; §3.5/§2.2 covariance-like framing; §4.1 Wilcoxon zero-handling, A₁₂ basis, FP-probe scope, single-thread precondition; §4.2.3 Holm-family + BCa notes; §4.4 new CEC2013 Table 10; §4.7 D≥50 co-gating clause; Conclusions Limitations 6–7 and prospective-supplement wording. Rebuilt PDF (35 pp) and DOCX pass all validators (0 undefined refs; DOCX `ok:true`; cross-format parity 0 FAIL).
