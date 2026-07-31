# Phase 8 — Evidence-First Main-Manuscript and Pre-Ablation Supplement Drafting — Gate Report

- **Phase:** 8 (PAPER_BUILD_PROMPT.md lines 4654–4897)
- **Gate date:** 2026-07-11
- **Verdict:** **APPROVED — Phase 8 FROZEN**
- **Signatories:** P2 + P3 + P4 + P6 + P9 (framework Gate 8 quorum)

## 1. The manuscript
**Title:** *An Interaction-Structure Memory for High-Dimensional Gaining-Sharing
Knowledge Optimization* — MDPI Algorithms class; canonical source `papers/main.tex` +
five section files (introduction, related_work, proposed_algorithm, performance,
conclusions) + `papers/supplementary.tex`.

| Measure | Value | Rule |
|---|---|---|
| **main.pdf** | **34 pages total; B1 = 31 main-text pages** (back matter 31–32, refs 32–34) | 28–34 band, ≤34 hard cap — **PASS, no valve needed** |
| **supplementary.pdf** | 32 pages | — |
| **Abstract** | **exactly 200 words** (was 222; trimmed at gate, bound number + all three disclosures intact) | ≤200 — PASS |
| Prose | ~10.1k words across sections (per-section budgets hit within ±10%) | outline budgets |

## 2. Evidence discipline (audited, not asserted)
- **Number binding:** every empirical sentence carries a `% BIND:` comment;
  `audit_manuscript.py` scan: **zero unbound numbers, zero forbidden-claim binds**;
  QA spot-checked 40+ numbers against the bundle/tables — all exact.
- **Citations:** `citation_usage_map.csv` (153 rows; 110 in released build) —
  **0 failures**; all keys ⊆ the 57 admissible, role-map-compliant.
- **Paragraph evidence:** `paragraph_evidence_audit.csv` (274 rows) — every scientific
  paragraph claim-anchored; only ACCEPTED/NARROWED/READY rows asserted; NARROWED
  wording used verbatim (RS-01, IN-03).
- **Mandated loss disclosures — ALL present in prose** (QA-verified): CEC2011
  Holm-significant loss vs eGSK (also in the abstract); W/T/L 11-2-16/13-0-16/12-0-17
  vs eGSK stated in the same paragraph as the #1 ranks; Nemenyi non-separability
  (CD=1.67); D30 #2; CEC2013 D30 third place; apgsk per-run gap; self-init exception;
  r01/r04/r05 robustness qualification; D10 weak separation.
- **No ablation:** scan clean; S6 = unreleased placeholder comment only; single
  neutral supplement pointer in §3.3.
- **AG-0007 GenAI disclosure:** present (dedicated back-matter block + Acknowledgments
  tool/version statement); placement question routed to Phase 9 (minor).
- Legacy defects eliminated: duplicate `\label{sec:alg:complexity}`, the prohibited
  "Theoretical Properties" subsection, fabricated SGSM/ACE expansions, stale
  `tab:panel` duplicate, wrong APGSK citation.

## 3. Build record
Six assembly fixes (package swap algorithm2e→algorithm+algpseudocode, label
de-duplication, T16-BCA scope correction, parameter-table resize wrap at the input
site — frozen artifact untouched); both PDFs rebuild cleanly from scratch with zero
unresolved references (`build_record.md`).

## 4. Adversarial QA and resolution
1 major + 3 minor: ~~abstract 222 words~~ → **rewritten to exactly 200** (recompiled,
34 pages unchanged); ~~supplement stale title~~ → fixed during QA;
~~liang2024gskwoa overextension~~ → reworded to junior-phase-only claim;
AG-0007 back-matter placement → **Phase 9 hand-off** (confirm MDPI placement or fold
one sentence into §4.1). Zero unfixed findings.

## 5. Hand-offs to Phase 9
- AG-0007 placement confirmation; T16_bca tex-vs-word-source reconciliation (Phase 7
  carry-forward); figure word_locations; DOCX parity page check (page_budget §7);
  R-0004 cover-letter rewrite gate remains.

## 6. Sign-off
- **P2:** APPROVED — method prose faithful to the frozen canon; boundaries C1–C4 marked.
- **P3:** APPROVED — setup/results/statistical wording matches the SAP + actual outputs.
- **P4:** APPROVED — protocol/provenance statements exact (release, seeds, pairing, gaps).
- **P6:** APPROVED — losses visible, calibrated non-promotional prose, abstract scoped.
- **P9:** APPROVED — paragraph sampling traced to claims/cards; no unsupported novelty.

**Gate 8 APPROVED. Phase 8 FROZEN 2026-07-11.** Subsequent changes only through review
tickets preserving evidence bindings. Phase 9 (dual-format production) unblocked.
