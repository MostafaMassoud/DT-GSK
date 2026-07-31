# Phase 8 — Task 15: Writing-Quality Pass — Drafting Decisions

Date: 2026-07-11. Agent: Phase 8 writing-quality agent (task 15).
Scope read: all five compiled sections (`papers/sections/{introduction,
related_work,proposed_algorithm,performance,conclusions}.tex`) plus
`papers/supplementary.tex`, calibrated against
`papers/governance/presentation_conventions.md` (esp. Dims 2, 17, 22 and
Global weakness 2, the eGSK duplicate-paragraph failure).
Legacy non-compiled files (`literature_review.tex`,
`supplementary_content.tex`) were not touched (not part of either
compiled document).

Invariants verified after editing: every `% BIND:` comment count
unchanged (9/34/41/78/18/83 per file), every `\cite` count unchanged
(8/43/21/12/1/9), all labels, numbers, and claim wordings byte-identical
except where noted below (no number, citation, label, or claim-scope
word was altered anywhere). Both documents recompiled to fixpoint at
unchanged page counts (main 34 pp / supplement 32 pp; no reference
warnings).

## Word counts (comment-stripped, `%`-tails removed)

| File | Before | After | Δ |
|---|---|---|---|
| sections/introduction.tex | 953 | 953 | 0 |
| sections/related_work.tex | 1925 | 1924 | −1 |
| sections/proposed_algorithm.tex | 3291 | 3281 | −10 |
| sections/performance.tex | 4548 | 4541 | −7 |
| sections/conclusions.tex | 756 | 756 | 0 |
| supplementary.tex | 4418 | 4418 | 0 |

All outline word budgets remain satisfied (deltas are negative or zero).

## Per-section decisions

### introduction.tex — NO EDITS
Assessed and deliberately left intact. The "is met by" anaphora in
paragraph 2 is functional parallel structure (weakness→subsystem
mapping), not repetition. C1–C4 bullets are verbatim-scoped from the
contribution matrix — untouchable. The closing roadmap ("The remainder
of the paper is organized as follows.") is the Dim-2-mandated roadmap in
standard MDPI register; kept, and the duplicate stem in Section 4 was
removed there instead (see performance.tex).

### related_work.tex (−1 word)
1. Grammar: dangling preposition removed — "carry no learned structure
   in~\cite{kolda2003directsearch,nelder1965simplex}" → "carry no
   learned structure~\cite{...}" (§2.2; citation preserved in place).
2. Spelling: "catalogue" → "catalog" (§2 opener), aligning to the
   manuscript's dominant American forms (the file itself uses
   organized/randomized/synthesis-ize forms 8×).

### proposed_algorithm.tex (−10 words)
1. Duplicate-pattern kill (Global weakness 2): the ARGP subsection
   (§3.3.2) repeated verbatim the appositive "--- original at this
   specificity within the cited corpus ---" already stated 40 lines
   above in the scaffold overview (§3.3, honest MOD/ORI labeling
   sentence). Second instance cut; §3.3.2 now opens "ARGP resolves
   this:". The originality fact and its exact frozen wording survive
   once in this section (and once in the C3 bullet, a different
   section) — no scope change.
2. "The section marks..." → "This section marks..." (§3 opener;
   register).
3. Spelling standardization to American (the manuscript majority and
   the other five files): initialisation → initialization (worked-
   example table body cell — table is section-authored, not a frozen
   phase_03 artifact; caption untouched), re-initialises/-ised/-isation
   → -izes/-ized/-ization (3×), amortised → amortized (2×), minimiser
   → minimizer, randomising → randomizing, self-initialises →
   self-initializes, neighbours → neighbors. Frozen phase_03 `\input`
   artifacts were NOT touched.

### performance.tex (−7 words)
1. Boilerplate opener cut: "This section is organized as follows."
   deleted; the orientation paragraph now leads directly with
   "Section~\ref{sec:exp:settings} discloses the full protocol: ...".
   Removes the near-verbatim stem shared with the introduction's
   roadmap (Dim-2 requires an orientation paragraph, which remains —
   only the filler frame sentence is gone).
2. Terminology collision defused: "The secondary suite is CEC2011"
   → "The real-world suite is CEC2011" (§4.1). "Secondary suite" is
   not in the frozen glossary and risks reader confusion with the
   frozen term "second comparison suite" (= CEC2013). CEC2011's frozen
   designation is "real-world suite"; facts (22 problems, native
   dimensions, 25 runs, MaxFES) unchanged.
3. Robustness of cross-references: four hardcoded "Section~3" in prose
   replaced with "Section~\ref{sec:algorithm}" (environment paragraph,
   convergence discussion, runtime paragraph, class-discussion
   paragraph). A fifth occurrence inside a % comment left as-is.
4. Consistency: one stray "seven-algorithm panel" (§4.2.2) aligned to
   the file's dominant "7-algorithm" (used 7× elsewhere in the file and
   in every frozen caption).

### conclusions.tex — NO EDITS
Assessed and left intact. The four Dim-21 movements are present, the
headed limitations paragraph is properly parallel ("First...Fifth"),
and the "motivates...motivates" pair in future work is deliberate
anaphora anchoring each item to a mechanism. Numbers paraphrase rather
than repeat Section 4 sentences, as required.

### supplementary.tex (0 words net)
1. Spelling: "colour/linestyle" → "color/linestyle" (S3 prose;
   captions untouched).
No other edits: the heavy caption repetition across the 19 convergence
grids is by design (registry-frozen self-contained captions,
Dimension 20/16 conventions) and is out of bounds for this pass.

## Deliberate non-edits (assessed, kept, with reasons)

- All MT-01/BG-03 frozen wordings ("leaves the gaining-sharing operator
  core unchanged and layers control, budget, structure-memory, and
  polish"; "none learns --- or exploits --- the interaction structure
  of the moves the run has already accepted") recur across sections by
  governance design; not repetition to kill.
- The three suite subsections opening with the same "Within the GSK
  family panel, \ismgsk{} ..." stem: this is the Dim-2 mandated
  identical internal rhythm plus mandatory scoping phrase; kept.
- Intro's two "seven-algorithm GSK-family panel" instances kept: one
  sits inside the verbatim-scoped C4 bullet (untouchable), and editing
  only the other would create intra-section drift.
- All registry-frozen captions, tables/T*.tex inputs, and phase_03
  frozen artifacts: byte-untouched.

## Flagged but left (for Phase 9 / report)

1. **Cross-document accuracy risk, performance.tex §4.2.1 (first
   sentence):** "The complete per-function five-statistic tables
   (best/median/mean/worst/SD over 51 runs) for \ismgsk{} and all six
   comparators at every dimension are provided in Supplementary
   Material, Section~S1". Supplement S1 actually carries mean±SD
   7-algorithm panel tables (T07–T10); the five-statistic detail lives
   in S2 and covers \ismgsk{} vs GSK only (T02–T05). Fixing this
   changes the factual description of the exhibits, which exceeds a
   writing-quality mandate — left for the Phase 9 cross-consistency
   audit (Dim 22 pass (i)). Also note the five-statistic order here
   (best/median/mean/worst/SD) differs from the S2/T01 caption order
   (best/median/worst/mean/SD).
2. **supplementary.tex S2.1:** the cross-document pointer "(Table
   \texttt{tab:wilcoxon-holm})" cites a main-paper label literally in
   typewriter font; once main-document exhibit numbering is final,
   Phase 9 should replace it with "Table N of the main paper". Left
   because frozen-label referencing is the current binding rule.
3. **conclusions.tex "Beyond these" sentence** (statistical-scope
   paragraph after the five limitations): dense triple-clause sentence;
   readable but at the outer edge of register. Left because it packs
   three mandated disclosures (block sizes, APGSK gap, no per-suite
   tuning) whose separation would add words against a met budget.
