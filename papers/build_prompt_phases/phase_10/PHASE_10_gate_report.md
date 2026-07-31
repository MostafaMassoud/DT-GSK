# Phase 10 — Adversarial Review — Gate Report

- **Phase:** 10 (PAPER_BUILD_PROMPT.md lines 5207–5432)
- **Gate date:** 2026-07-11
- **Verdict:** **APPROVED — Phase 10 FROZEN** (Gate 10 pass=true; open_critical_major=0)
- **Signatories:** P1 + P3 + P5 + P6 + P7 + P8 + P9 (framework Gate 10 quorum)

## 1. Review outcome (6 hostile reviewers)
| Reviewer | Recommendation | Tickets |
|---|---|---|
| R1 scientific | major_revision | 4 major, 3 minor |
| R2 statistics | minor_revision | 2 major, 4 minor |
| R3 reproducibility | minor_revision | 2 major, 3 minor, 1 editorial |
| R4 editorial | minor_revision | 3 major, 3 minor, 1 editorial |
| R5 Word | minor_revision | 4 minor, 1 editorial |
| R6 domain (hostile) | major_revision | 4 major, 3 minor, 1 editorial |

The two `major_revision` verdicts rest on two structural critiques that are **real and
already-disclosed design boundaries**, not defects: (a) the 7-member panel is entirely
within the GSK family with no external (L-SHADE/CMA-ES/jSO) anchor; (b) the named central
mechanism's causal payoff is deferred to the Phase-12 supplement. Both are legitimately
handled by change-control, not silent edits.

## 2. Ticket disposition (35 deduped → `revision_tickets.csv`)
| Disposition | Count | Notes |
|---|---|---|
| **FIXED** | 17 | prose / method-description / one presentation table; **zero numbers, equations, labels, citations, `% BIND`, claim scopes, algorithm source, or bundle values changed** |
| **DEFERRED (change-control)** | 12 | new experiments (external baseline, main-text ablation), figure-asset regen, author-side items |
| **REJECTED-INVALID (with evidence)** | 3 | reviewers read the **unbuilt orphan** `sections/supplementary_content.tex` (not `\input` by the compiled `supplementary.tex`); shipped artifacts are compliant (no "hold-out" wording, no ablation, S6 reserved) |
| **RECORDED (safe Word cosmetics)** | 3 | current output correct |
| **Numeric corrections** | 0 | R2/R3 confirmed every number matches release `rel-2026-07-10-262fc16c9` |

### Fixed highlights
Abstract qualifier "unweighted across-dimension mean, no cross-dimension test" added
(199 ≤ 200 words); §3.5/§2.2 reframed ISM's interaction matrix as covariance-like with the
novelty relocated to the discrete/decaying/signed/accepted-move framing (answers R1/R6 on
the CMA-ES distinction); IN-02 hedged to "consistent with intended role … per-component
attribution deferred"; external-baseline and single-environment threats surfaced in the
main-text limitations.

## 3. Post-revision integrity (all pass)
Citations 40/40 in-build ⊆ 57-key pool, 0 undefined, usage-map symmetric; 15+ numbers
spot-checked all bind to the release (CEC2017 2.48/2.96; D30 2.50 vs eGSK 2.29; CD
1.672993; CEC2011 3.36/2.52; 24-cell 17W/7T/0L); no `results/` or absolute-path leak;
cross-format parity 275 rows / 0 FAIL; both formats + supplement ablation-clean (S6
unrendered); PDF 0 undefined refs, `validate_docx.py` ok.

## 4. Ablation correction-trigger register (Phase-12 guard)
`ablation_correction_triggers.md` records one-directional triggers: an unfavorable Phase-12
ablation result **narrows** the affected claim; a favorable result stays **supplement-only**
and may **never** back-port to upgrade an existing main claim (governance guard G0). This
keeps the deferral a genuine open question and prevents the ablation from retro-justifying
the paper.

## 5. Carry-forward to Phase 11 / pre-submission (DEFERRED, do NOT block content freeze)
- **R4-T1 (major)** — conceptual Figs 1–4 label equations with an `E#` scheme misaligned
  with the manuscript equation numbers; Fig. 4 caption/graphic contradiction. → controlled figure-refresh.
- **R4-T2 (major)** — Fig. 1 (taxonomy) header prints raw BibTeX keys
  (`[omidvar2014dg]`…) instead of rendered citations. → controlled figure-refresh.
- R4-T4/T6 (minor) — SGSM/ISM alias duplication in bound exhibits; Nemenyi charts are
  bar+band, not canonical Demšár diagrams. → figure-refresh.
- R1-3 (minor, author) — "High-Dimensional" title vs the D=100 ceiling.
- R3-4 (minor, author) — Data-Availability needs a persistent DOI/URL (do not fabricate).
- R3-5 (minor) — exhibit bindings stamped `commit_sha …-dirty`; resolved on commit.
- Cosmetic — Algorithm 1 float sits low on p11 (clean render; LaTeX float placement).

**These are scheduled for the post-Phase-12 "apply review + fix all issues" pass** per the
standing directive; the figure defects (R4-T1/T2) are the priority items there.

## 6. Sign-off
Gate 10 APPROVED, pass=true, 0 open critical/major. The manuscript is READY for the
Phase 11 pre-ablation freeze on integrity grounds. Every major ticket is FIXED (verified in
the shipped PDF), legitimately DEFERRED with rationale, or REJECTED-INVALID with evidence.

**Gate 10 APPROVED. Phase 10 FROZEN 2026-07-11.** Phase 11 (finalization + pre-ablation
freeze) unblocked.
