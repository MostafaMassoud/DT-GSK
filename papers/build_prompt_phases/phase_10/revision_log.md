# Phase 10 Revision Log (tasks 8-11: triage, resolve, rebuild)

**Date:** 2026-07-11 · **Inputs:** 6 reviews (`review_R{1..6}_*.md`) · **Baseline:** FROZEN Phase-9 build (34 pp PDF, 32 pp supplement) · **Evidence:** immutable release `rel-2026-07-10-262fc16c9`.

All edits are prose / method-description / presentation only. **No frozen number, equation, label, citation key, `% BIND` comment, claim scope, algorithm source, or evidence-bundle value was altered.** Ticket ledger: `papers/governance/revision_tickets.csv` (35 deduped tickets).

## Disposition summary

| Disposition | Count | Notes |
|---|---|---|
| FIXED | 17 | prose / method-description / one presentation-only table |
| DEFERRED (change-control) | 12 | new experiments, figure-asset regeneration, author-side items |
| REJECTED-INVALID (with evidence) | 3 | reviewer read a non-shipped draft, or no defect |
| RECORDED (journal_word, safe-to-leave) | 3 | minor Word cosmetics; current output correct |

Severity: 11 major, 23 minor, 1 editorial. No number-wrong ticket survived: R2 and R3 independently confirmed every headline number matches the release, so there were **no numeric corrections** — only two number-adjacent tickets (R6-T02, R5-5) were rejected as misreads.

---

## CRITICAL VERIFICATION FINDING (reframes R6-T01, R6-T02, R6-T03)

Three of R6's four major tickets quote a file, `papers/sections/supplementary_content.tex`, as "the supplement." **That file is an unbuilt orphan.** Verified:

- `supplementary.tex` (the only source compiled to `supplementary.pdf` by `build_supplementary.py`, and to `supplementary.docx` by `build_docx.py --supplementary`) does **not** `\input{sections/supplementary_content}` — it inlines its own S1–S5 content.
- `supplementary_content.tex` is referenced **only** by `generate_artifact_binding.py:159` (a binding source path), never by any compile.
- The **shipped** supplement titles the CEC2013 section *"CEC2013 Second Comparison Suite Detail"* and states *"it is not an independence argument of any kind"* (`supplementary.tex:361`, BIND PR-03); it has **no** "hold-out" language and **no** ablation (`supplementary.tex:947`: *"S6 — RESERVED (ablation study) … no heading, no text, and no exhibit in any released build"*).

Consequence: the "External Hold-Out" wording (R6-T02), the null 4-cell isolation (R6-T01), and the 6-config selection exposure (R6-T03) are all in the orphan draft, **not in any shipped artifact**. The shipped supplement is PR-03 compliant. See per-ticket entries below.

---

## FIXED (17)

Format: **issue (quoted)** → action · section · evidence · verification.

### Prose / method-description reconciliations

**R1-2 / R6-T07 (major, method_description)** — *"The 'not a sampling covariance' framing risks reading as a distinction without much difference … locate the genuine novelty in the discrete/decaying/signed/accepted-move-only framing."*
→ Added at first use in `proposed_algorithm.tex` §3.5: `$G$` is a *signed, decaying second-moment (co-movement) statistic over coordinate indices*, **covariance-like in construction**, and the terminal polish performs a **covariance-eigenbasis operation**; the novelty is relocated to the accepted-move-only / signed / decaying accumulation and discrete exploitation, with an explicit "records which coordinate indices co-move … not a recovered map of the objective's true variable interactions." `related_work.tex` §2.2 mirrored. · Evidence: MT-08/MT-09; `phase_04/novelty_scope.md`. · Verified: renders p.15/§2.2; no numbers touched.

**R1-4 (minor, prose)** — *"'2.48 of 7' … lacks the 'descriptive across-dimension aggregate, no cross-dimension test' qualifier."*
→ `main.tex` abstract: "(2.48 of 7) — an unweighted across-dimension mean, no cross-dimension test — placing first at three of four dimensions." · Evidence: RS-01 NARROWED permitted wording. · Verified: renders p.1; number unchanged; both `% BIND` lines preserved; **199 words ≤ 200** (word-count script).

**R1-6 (major, method_description)** — *"State … that the strong-baseline comparison is against a re-port … and that DT-GSK does not statistically separate from it."*
→ Confirmed already-compliant (no edit needed): the SLSQP-vs-`fmincon` port is disclosed in §4.1 Evidence discipline, the panel roster ("eGSK (Python port; SLSQP substitutes … `fmincon` (disclosed))"), §4.6 runtime, Limitation 4, and supplement S5; non-separation is in the abstract, §4.2.3 ("never Nemenyi-separable"), and Limitation 1. · Verified: grep of all superiority sentences — none implies an eGSK advantage.

**R1-7 (minor, prose)** — *"the single-environment reproducibility threat … and the self-authored-baseline issue … not framed as a scientific threat."*
→ `conclusions.tex` Limitations: added **Sixth** (single host/environment; run-time NumPy/SciPy behind eGSK's SLSQP uncaptured; single-thread byte-stability precondition) and **Seventh** (self-authored within-family panel as a scientific threat; self-init fairness). Count updated "Five → Seven." · Evidence: `comparability_audit.md`, `fp_environment_audit.md` E2, COI statement.

**R2-1 (major, method_description)** — *"does not state that zero-differences … are DISCARDED (zero_method='wilcox') nor whether p-values are exact or normal-approximation."*
→ `performance.tex` §4.1 Statistical protocol: zeros under the tie rule discarded before ranking (`zero_method='wilcox'`); p-values use the normal approximation with continuity correction (`scipy.stats`); effective post-zero n in the released R⁺/R⁻ workbooks. · Evidence: `phase6_run_analysis.py` L333/359/1879/1946. · Verified: renders p.19; **no p-value recomputed.**

**R2-2 (major, method_description)** — *"the A12 … is computed across the 29 per-function MEANS … distinct from the run-level A12 workbook."*
→ §4.1 protocol + Table 8 caption now state the tabulated A₁₂ is over the 29 per-function means (same unit as the across-function Wilcoxon), distinct from the run-level A₁₂ workbook, with the VD thresholds as descriptive labels. · Evidence: `phase6_run_analysis.py` L2233–2241; RS-08/T03. · Verified: caption + protocol render; numbers unchanged.

**R2-3 (minor, prose)** — *"the 24-cell tally aggregates four independent within-dimension Holm families … FWER controlled only within each dimension."*
→ §4.2.3 primary tally + §4.7 Discussion tally now state the 24-cell count aggregates four independent within-dimension Holm families (size 6) and is a descriptive tally, not a jointly FWER-controlled result.

**R2-4 (minor, method_description)** — *"BCa … resamples pre-computed midranks … unusual … a labeling/one-line-justification item."*
→ §4.2.3 BCa mention: intervals resample fixed per-function midranks, read descriptively (spread on the mean rank), not as a formal overlap test. Placed in the main text to avoid touching the frozen supplement.

**R2-5 (minor, prose)** — *"reads in the present tense as if the ablation is *in* the shipped supplement … Reword to make the deferral explicitly prospective."*
→ `proposed_algorithm.tex` §3.3 and `conclusions.tex` future work made prospective ("a follow-up supplement … no such component study is included in the present Supplementary Materials"). **Token discipline:** a first-pass wording used "ablation", which the governance guard `no_ablation_tokens_any_part` correctly rejected; reworded to "component study." · Verified: `validate_docx.py` ablation guard now PASS ("tokens … absent from all 33 parts").

**R2-6 (minor, prose)** — *"associating the D≥50 improvement with 'the interaction-structure memory' singles out one bundled change."*
→ §4.7 "By dimension": the D≥50 tier activates several subsystems together (ISM graph, subspace LS, eigenframe polish, raised population floor), so behaviour is associated with the bundled tier configuration, not an isolated component; per-component attribution deferred. · Evidence: within IN-02 permitted wording (reduces attribution; no causality). Also serves the residual valid kernel of R6-T01.

**R3-1 (minor, method_description)** — *"reads as if all optimizer kernels are numerically probed — a mild overstatement."*
→ §4.1: "probe hashes of the shared RNG, the DT-GSK kernels, and the suite evaluators (the comparator-specific update kernels are covered by the shared RNG and evaluator probes, not by a dedicated per-kernel hash)." · Evidence: `fp_environment_audit.md` §2.

**R3-2 (minor, prose)** — *"run-time NumPy/SciPy versions … not captured … material for eGSK … not disclosed as a limitation."* → folded into Limitation Sixth.

**R3-3 / R6-T08 (minor, prose)** — *"'repeat-identical' omits the precondition that byte-stability at D≥50 requires single-threaded Numba/BLAS."*
→ §4.1 states the single-thread precondition where the repeat-identical claim is made; `conclusions.tex` Sixth adds the parallel-speed-up cap. · Evidence: `implementation_correspondence.md` note 2.

### Presentation

**R4-T5 (minor, editorial)** — *"CEC2013 … has no main-text table or figure at all … 'CEC2013 overall #1' … should not be the only suite with zero in-text evidence."*
→ Added **Table 10** (`tab:friedman-cec2013`) to §4.4: 7 algorithms × D10/D30/D50 + Overall, best-per-column bold. Values transcribed from `friedman_ranks_cec2013_{overall,D10,D30,D50}.csv` and cross-checked cell-by-cell against the release (DT-GSK 2.41/3.38/2.61/2.80; eGSK D30 **3.07**). Caption: "second comparison suite … carries no independence claim" (PR-03). · Verified: renders as Table 10 p.26 (runtime auto-renumbered to Table 11); all `\ref` resolve; **cross-format parity table rows PASS (0 FAIL)**; extracted PDF cells equal the CSV values.

**R4-T7 (editorial)** — *"a single dense 199-word paragraph … split the mechanism sentence into two."*
→ Abstract mechanism block split into three sentences (memory; polish; scaffold + pipeline); operator list shortened to an em-dash apposition. Combined with R1-4; re-verified 199 words.

---

## DEFERRED — change-control required (12) · **OPEN MAJORS FLAGGED**

> **PROMINENT FLAG — the following MAJOR tickets are NOT resolved in this pass and require change-control (new experiments, figure-asset regeneration, or author decision) before they can close. They are honestly deferred, with the frozen algorithm and immutable evidence left intact.**

**R1-1 (MAJOR, analysis) — OPEN.** Promote a component ablation, or reframe as methodology-first. *Rationale:* the ablation is Phase-12 material (S6 placeholder; AB-01/02/03 deferred) = new analysis on immutable evidence. The paper already defers causality and now carries the R2-6 co-gating hedge, so the main text does not overstate; but the requested *demonstration* of the mechanism cannot be produced without reopening the evidence. → Phase 12.

**R1-5 / R6-T04 (MAJOR, missing_evidence) — OPEN (evidence).** Add an external L-SHADE/CMA-ES/structure-learning anchor. *Prose part FIXED* (Limitation Seventh states the absence as a scientific threat, not merely future work). *Evidence part deferred:* a new baseline requires new runs under the locked protocol = change-control.

**R4-T1, R4-T2 (MAJOR, editorial) — OPEN.** Figure E#↔Eq# misalignment (incl. the Fig. 4 caption/graphic contradiction) and Figure 1 raw BibTeX keys. *Rationale:* the four conceptual figures are **pre-rendered, checksum-bound PDF/PNG assets**; Figure 2 (architecture) is exported from a `.drawio` source not regenerable in this environment, so a partial regeneration would leave an inconsistent set. Outside the task's ".tex rendering-only" editorial scope; touching bound assets is change-control. **Turn-key remap recorded:** E4→Eq.5, E5→Eq.6, E7→Eq.8, E8→Eq.9, E9→Eq.10, E10→Eq.11, E11→Eq.12, E12→Eq.13; Fig. 1 keys → [22]/[23]/[24]. → figure-refresh pass.

**R6-T01 (MAJOR, analysis) — partially addressed; isolation DEFERRED.** The favorable-only framing is hedged via R2-6. The null isolation the ticket asks to point at is in the **unbuilt orphan** file, not the shipped supplement; a pointer to it would be a dangling reference. → the isolation result ships in Phase 12.

**R6-T03 (MAJOR, prose) — OPEN.** Surface the CEC2017 6-config selection exposure. *Rationale:* the shipped S5 contains no such disclosure (orphan-only); the shipped paper makes no "development suite" claim and is not itself overstating. Injecting an unsourced selection-exposure claim (unverifiable from the immutable bundle) is a new substantive claim = change-control. → surface in the Phase-12 tuning-protocol disclosure.

Minor deferrals: **R3-4** (persistent DOI/URL locator — author-side, AG-0006/R-0004; must not be fabricated), **R3-5** (re-stamp exhibits from a clean commit — repo hygiene; numbers unaffected), **R4-T3** (repo paths in figures — bound-asset re-render), **R4-T4** (SGSM alias in exhibits — bound-asset + `phase_03/notation_table.tex` re-render; the Abbreviations list already discloses the alias correctly), **R4-T6** (CD-diagram label vs graphic — bound-asset retitle; a caption-only change would desync from the baked graphic), **R6-T06** (shared-X₀ control run — new analysis; *prose caveat FIXED* in Limitation Seventh), **R6-T05** (D100 scaffold cell — *already-scoped in prose*; cell is Phase-12).

---

## REJECTED-INVALID (3, with evidence)

**R6-T02 (major, editorial).** "External Hold-Out" contradicts PR-03. **Invalid for the shipped artifact:** the strings exist only in the unbuilt orphan `supplementary_content.tex`; the shipped supplement uses "Second Comparison Suite Detail" and "not an independence argument of any kind." (Recommended separately: reconcile/remove the orphan draft under change-control.)

**R5-3 (minor, journal_word).** "Generic 'Picture' alt text." **Invalid / already handled:** `build_docx.py._pass_alt_text` sets `wp:docPr/@descr` on every figure; `validate_docx.py` reports `images_with_alt = 14/14`. The reviewer inspected `@name`, not the alt text.

**R5-5 (minor, journal_word).** "Extra DOCX table." **Not a defect:** the extra `w:tbl` is a layout table; parity validator PASS. After adding Table 10 this pass, PDF = 11 numbered tables, DOCX = 12 native (11 + 1 layout).

## RECORDED — safe-to-leave journal_word (3)

**R5-1** DOCX TOC vs PDF (author-side finalization, D-WORD-01; `updateFields=true`). **R5-2** IEEE citation-DB style stamp (IEEE numeric ≡ MDPI [n]; no MDPI `.xsl`; changing it risks breaking cached rendering). **R5-4** orphaned DOI rels in `footnotes.xml.rels` (cosmetic bloat; no content/validation impact). None modifies a number or the algorithm; each is a low-value/high-regression-risk generator tweak better handled in a build-tooling pass.

---

## Rebuild & verification

Env: `PYTHONIOENCODING=utf-8`, `SOURCE_DATE_EPOCH=1783641600`.

| Check | Result |
|---|---|
| `build_pdf.py` | OK → `papers/DT-GSK.pdf` (928,688 bytes) |
| Page count | **35 pp** (was 34; +1 from Table 10 + Limitations Sixth/Seventh + protocol sentences) |
| Undefined references / citations | **0** (`main.log`); no multiply-defined labels |
| PDF ablation scan (parity validator) | **PASS** (0) |
| `build_docx.py` (main) | OK → `papers/DT-GSK.docx` (3,061,644 bytes) |
| `validate_docx.py` | **`"ok": true`, 0 FAIL**; ablation guard **PASS**; native tables 12; images_with_alt 14/14; fields 274 balanced; markers_left 0 |
| `validate_cross_format_parity.py --doc main` | **exit 0, 275 rows, 0 FAIL** |

Supplement (`supplementary.pdf/.docx`) **not modified** — it was already PR-03 compliant; no supplement edit was warranted, so it remains byte-frozen. The DOCX finalize step fell back once to `DT-GSK.new.docx` (transient file lock) and was reconciled onto the canonical path (`os.replace`), then re-validated.

## Files touched (source; all prose/presentation)
`papers/main.tex` (abstract) · `papers/sections/performance.tex` (protocol, tallies, discussion, FP-probe, thread precondition, BCa note, Table 10) · `papers/sections/proposed_algorithm.tex` (co-movement clause, prospective deferral) · `papers/sections/related_work.tex` (covariance-like framing) · `papers/sections/conclusions.tex` (prospective deferral, Limitations Sixth/Seventh). Governance: `papers/governance/revision_tickets.csv`. Not touched: any `tables/T*.tex`, any figure asset, `phase_03/*`, `supplementary.tex`, the evidence bundle.
