# DT-GSK Manuscript — Consolidated Q2 Review Report (Round 1)

**Date:** 2026-07-13 · **Target:** MDPI *Algorithms* (Q2) · **Method:** `PAPER_REVIEW_PROMPT.md` applied by six independent read-only expert panels (algorithm/claims, benchmark methodology, statistics/reproducibility, writing/exhibits, ethics/citations, production/code-fidelity), each calibrated to the post-A0–A4 status snapshot (§1.5) — verify-not-reopen resolved items; scope out known author-side gaps.

> This is **pass 1 of the requested five**. Findings are merged and de-duplicated across panels and severity-ranked. Every item was independently verified against the current build/evidence/code and is quoted to a location.

---

## 0. Executive summary & Q2 readiness verdict

**The science, statistics, honesty, and reproducibility are sound and were extensively *verified* (not merely read):** every headline number reconciles end-to-end; Friedman/Iman-Davenport/Nemenyi/Holm/BCa all recompute from committed artifacts; no pseudoreplication; equations and Algorithm 1 are internally correct; the ISM-null is disclosed consistently; code↔method spot-checks all match; the DOCX carries native OMML + native tables with 0 machine residue; the COI/citation discipline is strong.

**Verdict: NOT yet submission-ready, but close — no *critical* defect and no new experiments strictly required.** The gap to Q2-ready is **6 Major** items (all fixable by editing/rebuilding, not new science), a cluster of Minor/Editorial polish, and the known author-side administrative facts. Two of the Major/Minor items **correct assertions made earlier this session** (see §4).

| Severity | Count | Nature |
|---|---|---|
| Critical | 0 | — |
| Major | 6 | 3 DOCX/production, 1 disclosure/fairness, 1 GenAI-placement, 1 claim-attribution + 1 positioning |
| Medium | 3 | stale robustness count; unbounded self-init; eGSK-port comparability |
| Minor | 13 | 2 spec-constant errors, table legibility, bib hygiene, template compliance, effective-n |
| Editorial | 8 | stale title comment (×3-confirmed), column order, abstract scope, etc. |

---

## 1. MAJOR findings

**MAJ-1 — Four authored main-text tables collapse to unreadable 1×1 cells in the shipped DOCX.**
*Location:* `papers/DT-GSK.docx` `word/document.xml` w:tbl #1/#4/#6/#9; sources `related_work.tex:245` (taxonomy), `proposed_algorithm.tex:130` (architecture), `:222` (dim-gating), `:491` (sgsm-mechanism). *Description:* verified via lxml — each is `gridCols=1, rows=1` with all cell text concatenated into one blob; pandoc failed to parse the `p{width}` multi-line-cell tabulars. The PDF renders them correctly. *Impact:* the contribution-framing tables (ISM vs Differential-Grouping/CMA-ES/Eigenvector-DE; architecture/subsystem/activation) are garbled in the default Word submission and do not match the PDF. *Fix:* route these four through the existing native-table builder (semantic source + `@@NATIVETABLE@@`) or add a post-process guard rebuilding a collapsed w:tbl; add validator `authored_table_column_count_vs_source`. *Outcome:* four proper multi-row/col native tables matching the PDF. **Corrects the earlier "authored-table FAILs = tooling drift" claim (see §4).**

**MAJ-2 — Shipped main DOCX fails its own Appendix-D.6 validator (`validate_docx.py` → exit 2, 30 PASS/3 FAIL).**
*Location:* `papers/scripts/validate_docx.py` on `papers/DT-GSK.docx`. *Description:* (2a) `referenced_styles_defined: ['FigureTable']` — the 4 authored tables reference a `FigureTable` style defined nowhere (not in `styles.xml`/`reference.docx`), a **real dangling-style defect** (Word falls back to borderless); (2b) `table_count_vs_source 20 vs 16` — counter misses the 4 authored tabulars; (2c) `no_ablation_tokens` false-positive on the legit supplement pointer. *Impact:* the paper documents this validator as its QA gate, yet the shipped main DOCX fails it. *Fix:* rewrite `tblStyle FigureTable→Table` (or define it); fix `source_expectations()` to count authored tabulars; make the ablation scan signature-based. *Outcome:* exit 0. *Dependency:* 2a/2b resolve as a side-effect of MAJ-1.

**MAJ-3 — Triple-dangling "tuning-protocol disclosure → §S5" reference; undisclosed CEC2017 development-suite selection-bias at the headline.**
*Location:* `performance.tex:99`, `conclusions.tex:116`, `main.tex:230` all point to a "tuning-protocol disclosure in Supplement S5," but shipped S5 (Reproducibility Appendix) contains **no tuning protocol**. Internal records (`review_R6_domain.md:36`, `revision_tickets.csv` R6-T03) confirm CEC2017 was the development suite and six full-panel configs were compared before promotion — the multiple-testing exposure — a disclosure that "lives only in the unbuilt orphan file." *Impact:* the CEC2017 headline (best 2.48/7) is stated with no co-located selection-bias caveat and misdirects a reviewer to a non-existent disclosure — a fairness/train-on-test red flag. *Fix:* add a short tuning-protocol subsection to S5 (CEC2017 = dev suite; #configs compared; CEC2011/2013 untouched during selection); add a one-clause caveat beside the headline; repoint the 3 refs. *Outcome:* a hidden leakage exposure becomes a disclosed, bounded limitation; dangling refs resolved. *Highest-leverage single fix.*

**MAJ-4 — GenAI "how-used" description sits in back-matter, not Materials & Methods, contradicting the authors' own recorded MDPI requirement.**
*Location:* `main.tex:240-251` vs `administrative_gap_register.md:14` (AG-0007: "describe HOW used **in Materials and Methods**"). *Impact:* documented governance↔manuscript inconsistency on a mandatory MDPI ethics item; MDPI AI-integrity screening scrutinizes placement — desk-query risk. *Fix:* add one GenAI-use sentence into Methods (cross-referenced), or confirm the current *Algorithms* template accepts a dedicated back-matter section and update AG-0007. *Outcome:* placement matches recorded policy.

**MAJ-5 — The final-polish benefit is attributed to ISM's *learned eigenbasis*, which the isolation cannot support (and points the other way).**
*Location:* `proposed_algorithm.tex:539-541` ("its basis is learned…"); `supplementary.tex:1372-1374` ("only *the eigenframe* polish carries an isolated … effect"). *Description:* S6.5 shows `no_sgsm` (ISM off → polish falls back to coordinate axes) is **null** (Δrank +0.09, Holm 0.80/0.93), while `no_finalpolish` (whole polish removed) is **significant** (Holm 0.010/0.006). So the significant effect is "having a compass endgame at all"; the learned-basis-vs-axes contrast is the null row. The reframe was not fully propagated into the method/supplement. *Impact:* the paper's only significant added-value signal is over-attributed to the learned basis — a claim outrunning its own evidence. *Fix:* credit the deterministic RNG-free compass endgame; demote the learned eigenbasis to a design choice whose isolated advantage is unestablished at D≤100; change "only the eigenframe polish" → "only the final polish (basis-agnostic in these tests)." *Outcome:* C2 consistent with S6.5; stronger, not weaker, credibility.

**MAJ-6 — Positioning/desk-screening: named after a null mechanism + no statistically-established improvement over eGSK; the abstract does not signpost this.**
*Location:* Title/abstract `main.tex:90-151`; conclusions `:32-58`. *Description:* ISM (the namesake) is null in isolation; the headline 2.48/7 is an untested aggregate; DT-GSK and eGSK are never Nemenyi-separable and eGSK *wins* at D30 and on CEC2011 (Holm-significant). No statistically-demonstrated advance over the in-family best exists. *Impact:* the combination "null-named mechanism + no statistically-separable improvement" invites a fundamental "what is the demonstrated contribution?" screening query; the abstract sells the mechanism and the rank without signposting (a) non-separability and (b) the isolated-benefit question. *Fix:* raise the abstract's framing altitude to "novel accepted-move interaction-memory mechanism + a reproducible dimension-tiered family evaluation attaining statistically-tied family-competitive standing, with ISM's isolated benefit an open question at D≤100" — one forward-referencing clause; **do not change any number.** *Outcome:* reads as "novel mechanism + honest rigor," lowering desk-screen/reviewer-hostility risk. *Dependency:* coordinate with MAJ-5, MIN-abstract-scope.

---

## 2. MEDIUM findings

**MED-1 — `performance.tex:468` says "8" significant→non-significant transitions; the committed r05 artifact says "11".** Stale *pre-CR-0006* count (the 3 missing are the apgsk cells recovered post-freeze); the "expected power loss" framing also omits the 21 opposite-direction (`ns_to_sig`) transitions. Binding "0 sign reversals" conclusion unaffected. *Fix:* 8→11; report both directions; add a CR-0006 propagation check for every count predating the apgsk recovery.

**MED-2 — Self-initialization breaks the paired fair-start for DT-GSK at every dimension; disclosed but unbounded.** No comparator starts from DT-GSK's self-drawn 5·D population; no control run quantifies the effect, and D10 first place rests on only 3 Holm-significant wins. *Fix:* add one control cell (DT-GSK from shared X₀ at D10/D30) or explicitly scope the low-D claims.

**MED-3 — eGSK — the decisive rival — is a SciPy-SLSQP port whose accuracy comparability is disclosed but uncharacterized.** Direction of any bias is unbounded, and most headline nuances hinge on the DT-GSK↔eGSK relationship. *Fix:* a one-paragraph face-validity check of the port against a few published eGSK CEC2017 cells.

---

## 3. MINOR & EDITORIAL findings

**Minor**
- **MIN-1 [spec error]** `supplementary.tex:1055-1058` — S5.3 says BSE Cauchy escape "disabled for D<20"; frozen code **enables** it at D=10/15 (`_dt_profiles.py:145-149`), scale 0.05 (not 0.04). *Corrects an A1 statement (see §4).*
- **MIN-2 [spec error]** `supplementary.tex:1032` — S5.3 κ_min "0.45 at D≥50" is the **local-search** floor; the **linkage** floor is 0.35 (`_dt_profiles.py:170`), and the adaptive threshold (floor 0.12) takes over after warm-up. *Corrects an A1 statement (see §4).*
- **MIN-3** Four text-grid matrices are floated/captioned as **Figures** (taxonomy/architecture/dim-gating/sgsm) — reclassify as Tables (MDPI convention; same four as MAJ-1).
- **MIN-4** Table 4 (parameters) `\resizebox`'d to ~6pt — re-flow (split by tier / landscape) so type stays ≥ footnotesize.
- **MIN-5** Table 8/T15 (Wilcoxon-Holm, 29 columns) over-squeezed — split into D10/D30 and D50/D100, or move full detail to supplement.
- **MIN-6** T06 prints integer rank-sums/counts with 4 decimals ("159.0000") — format as integers (T14 already does).
- **MIN-7** Missing "Institutional Review Board Statement" + "Informed Consent Statement" back-matter — add "Not applicable."
- **MIN-8** Data-Availability + GenAI blocks are hand-built (full body font, period-not-colon) because the bundled `mdpi.cls` predates `\dataavailability`/IRB/consent macros — update to the current *Algorithms* class or reformat to 9pt "Label:". *(Root cause of MIN-7/MIN-8 and eases MAJ-4.)*
- **MIN-9** 17 bibliography entries are uncited in the build (phantom corpus vs. the governance "57"); 3 carry now-false comments (`david_order_statistics`, `jones1995fitness`, `yao1999evolutionary`) — prune or reintroduce; fix the 3 comments.
- **MIN-10** CRediT structurally incomplete — H.S.M.R. holds no role (AG-0001, author-side); must close before submission.
- **MIN-11** Self-citation/text-recycling exposure (A.W.M. co-authored 5/6 comparators) — run iThenticate pre-submission; add self-cites at any reused phrasing.
- **MIN-12** Effective n (25–27 after zero-difference discards) vs reported `n=29` in T15/wilcoxon_holm CSVs — add an `n_effective` column + T15 footnote.
- **MIN-13** D10 ISM-vs-eGSK is Holm-significant yet in the same Nemenyi band — add one sentence reconciling the focused Holm-6 (primary) vs all-pairs Nemenyi.

**Editorial**
- **ED-1 [×3-confirmed]** Stale "High-Dimensional" title in the `main.tex:2-3` source **comment** vs the reframed `\Title` — update the comment.
- **ED-2** Table 6 suite-column order (2017/2013/2011) differs from the paper's 2017/2011/2013 narrative order — reorder or note the grouping.
- **ED-3** Abstract `main.tex:125` "none learns" is an unscoped universal; body scopes to "cited" — scope the abstract to the surveyed corpus.
- **ED-4** Abstract describes ISM only beneficially (no null hint) — fold a half-clause into the MAJ-6 edit.
- **ED-5** Algorithm 1 omits the elite-archive update step that BSE reseeds from — add "…and update the elite archive."
- **ED-6** Provenance nits: `ablation_overlay_effects.py` hard-codes `SUITE="cec2017"` so the S6.5 CEC2013-D50 row isn't regenerable from the cited `papers/analysis/ablation_overlay/`; `overlay_contrasts_cec2013_D50.json` mislabels `zsplit` as pre-registration (used method is `wilcox`) — commit a CEC2013 CSV / repoint BIND; fix the label.
- **ED-7** Main-text "ablation" wording vs section header comments ("No ablation content") — reword pointers to "component study" (also clears validator 2c).
- **ED-8** Cosmetic bibkey/year mismatches (`fialho2010adaptive` = 2008/Da Costa; `jawad2024egsk` = 2025) — invisible under numeric style; optional.

---

## 4. Corrections to earlier-session claims (integrity)

The review caught defects that **contradict things asserted earlier this session** — recorded here honestly rather than defended:

1. **DOCX authored tables are NOT "just tooling drift."** During D4/A4 and in `PAPER_REVIEW_PROMPT.md §1.5.6` I characterized the `cross_format_consistency.csv` authored-table FAILs as "cross-format parity-check limitations, not content errors." **MAJ-1 verifies four of them are real structural collapses in the shipped DOCX.** (The `table_generated` precision/JSON-header FAILs ARE genuine tooling drift — that part stands.) → **§1.5.6 of the review prompt must be corrected**, and MAJ-1/MAJ-2 fixed.
2. **Two §S5.3 constants I wrote in A1 are wrong vs the frozen code** (MIN-1 BSE Cauchy D<20; MIN-2 κ_min 0.45→0.35) — despite A1 claiming "every value transcribed from the hash-frozen sources." My spot-check in A1 covered ACE arms and polish fractions but missed these two. → fix S5.3.

These corrections are the strongest evidence the multi-panel pass did its job.

---

## 5. Known author-side gaps (scoped out — not scientific defects)

DOI/ORCIDs/CRediT split/institutional emails/GenAI version-date/licenses/funding-COI confirmation (AG-0001..0007); cover-letter fill; opt-in Visio flowcharts unverified; EG-005 per-generation diagnostics unavailable. These block only the metadata gates (O and metadata-P), not the scientific gates.

---

## 6. Dependency clusters (fix-together groups)

- **C1 — DOCX authored tables:** MAJ-1 + MAJ-2(2a/2b) + MIN-3. One engineering fix (native-table + reclassify + style) closes all.
- **C2 — Selection-bias disclosure:** MAJ-3 (dangling refs + missing S5 subsection + headline caveat) — one fix.
- **C3 — ISM/polish framing:** MAJ-5 + MAJ-6 + ED-3 + ED-4 — one coordinated abstract/C2/supplement wording pass.
- **C4 — Back-matter/template:** MAJ-4 + MIN-7 + MIN-8 (root cause: outdated `mdpi.cls`).
- **C5 — Spec-constant accuracy:** MIN-1 + MIN-2 (§S5.3 vs code).
- **C6 — Ablation wording / validator 2c:** ED-7 + MAJ-2(2c).
- Independent singletons: MED-1, MED-2, MED-3, MIN-4/5/6/9/12/13, ED-1/2/5/6/8.

## 7. Recommended fix order (Round-1 roadmap)

1. **C1** (DOCX tables) → clears MAJ-1, MAJ-2(2a/2b), MIN-3 and makes the Word submission correct.
2. **C2** (tuning-protocol disclosure) → the highest-leverage credibility fix.
3. **C3** (ISM/polish framing) → aligns the last of the post-null wording.
4. **C4** (mdpi.cls / GenAI placement / IRB-consent) → MDPI template compliance.
5. **C5** (S5.3 constants) + **MED-1** (8→11) → evidence-accuracy.
6. Remaining Minor/Editorial as a copy-edit pass; MED-2/MED-3 are optional control-run/face-validity additions.
7. Author-side facts (§5) close the metadata gates.

**No new experiments are required to reach Q2-ready** (MED-2/MED-3 controls are optional strengtheners). With C1–C5 + MED-1 applied and the author facts supplied, the manuscript should clear a strong-Q2 bar.
