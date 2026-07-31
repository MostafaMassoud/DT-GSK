# Phase 4 Task 1 — Journal Decision Record

- **Date**: 2026-07-10
- **Decision**: The target journal is **FROZEN as MDPI *Algorithms***.
- **Decision-log anchor**: D-0010 (`papers/governance/decision_log.md`); configuration anchor: `papers/governance/project_configuration.md` Section 4.

## 1. Basis

1. **Repository-wired default (framework Phase 4 task 1)**: the manuscript is already wired to MDPI *Algorithms* — `papers/Definitions/mdpi.cls` is vendored, and `papers/main.tex` line 5 reads `\documentclass[algorithms,article,submit,moreauthors,pdftex]{Definitions/mdpi}` (journal option `algorithms`, type `article`).
2. **Explicit user decision, 2026-07-10**: "use the current plan's target and flag R-0004 for later" — i.e., keep the repository-wired target; do not switch venues now.

## 2. R-0004 disposition — DEFERRED, not resolved

- **The conflict**: `papers/cover_letter.md`/`.tex`/`.pdf` address Elsevier *Swarm and Evolutionary Computation*, which contradicts the repository-wired MDPI *Algorithms* template (risk register R-0004; `instruction_precedence.md` C-08).
- **Disposition**: **DEFERRED by user decision 2026-07-10.** This record does NOT resolve the conflict and does NOT touch the cover-letter files. The risk stays open and owned by the finalization phases (Phase 9 rendering / Phase 11 packaging), which MUST NOT render or package the stale cover letter as-is.

## 3. Consequences (binding on later phases)

1. **Cover letter rewrite gate**: if MDPI *Algorithms* is confirmed at re-verification, the cover letter MUST be rewritten for MDPI *Algorithms* before submission (or the venue decision revisited by the author via a new change request). Blocking at Phase 9/11.
2. **Page-limit binding**: per the requirements record (`journal_requirements.md`, Section 2), no strict journal page limit was found for MDPI *Algorithms* (MDPI general guidance: contact the Editorial Office below 3,000 or above 12,000 words). Under the framework Section 1.5 hard page-limit rule, the enforceable limit therefore binds to the **SELF-IMPOSED budget in `page_budget.md`** (main manuscript approximately 16–22 typeset pages excluding references; overflow resolved only by migration to the Supplementary Materials, never by shrinking below legibility). Compliance is measured from the compiled PDF at the Phase 8 draft gate, Phase 9 build, and Phase 11 packaging.
3. **Online re-verification gate**: the official instructions page could not be fetched on 2026-07-10 (HTTP 403; `journal_requirements.md` records verified_online=false). All journal-specific rules (length cap, peer-review model, template currency, APC, declaration blocks) MUST be re-verified against the live page before submission; discrepancies are handled via change request, not silent edits.
4. **Supplement routing unchanged**: extended tables, full curves, reproducibility detail, and the ablation study (Phase-12, supplement-only) remain in the Supplementary Materials — consistent with both the MDPI supplement policy (as far as verifiable) and the framework's no-ablation-in-main rule.

## 4. Alternatives considered

- **(a) Switch to Swarm and Evolutionary Computation** (match the cover letter) — REJECTED: the framework default binds to the repository-wired template, and the user chose the current plan's target.
- **(b) Resolve the cover-letter conflict now** — REJECTED: the user explicitly deferred R-0004.
