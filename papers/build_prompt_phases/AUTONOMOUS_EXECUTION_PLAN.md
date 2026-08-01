# Standing autonomous execution plan (user directive 2026-07-11)

> **What "autonomous" means here, and what it does not.** This file is a
> work-sequencing directive: it records the order in which the remaining
> production and review phases were to be executed, and the author's standing
> instruction to proceed through them without pausing for approval at every
> step.
>
> It concerns *sequencing and tooling*, not scientific judgement. Every phase it
> lists terminates in an author-gated freeze; every review it schedules produces
> a register of candidate findings that the authors then adjudicated (the
> registers, including refuted findings, are in `papers/governance/`); and no
> step in it authorizes generating a result, a claim, or a conclusion. The
> experimental campaigns it sequences were run by the deterministic pipeline
> from seeded, version-locked configurations, and every reported number derives
> from an immutable evidence release.
>
> The manuscript's *Use of Generative Artificial Intelligence* statement is the
> authoritative disclosure of AI involvement in this project. See also the
> README section "Internal Quality-Assurance Instruments".


**Directive:** continue autonomously through the remaining phases; after Phase 12,
apply `papers/PAPER_REVIEW_PROMPT.md` as a full adversarial review of the finished
paper and fix all issues autonomously.

## Sequence (each step gated on the previous freezing)
1. **Phase 10** — adversarial 6-reviewer review (RUNNING, task wfl2zo62s). On completion:
   apply fixes, close Gate 10, commit, freeze.
2. **Phase 11** — Primary manuscript finalization + pre-ablation freeze (Gate 11, the hard
   pre-ablation gate). Inline/workflow. Commit + freeze.
3. **Phase 12** — FINAL: promote the ablation campaign through Section 2.4 controlled
   validation (baseline D100 = repair slice per staging_inventory.md; byte-match verified),
   compute the supplement ablation exhibits, integrate supplement S6, final integrity audit,
   build the submission package. Commit + freeze.
4. **Apply PAPER_REVIEW_PROMPT.md** — run the full adversarial peer-review framework against
   the finished DT-GSK package (main + supplement + DOCX + cover letter). Produce the
   mandated review artifacts + issue register.
5. **Fix all issues** — resolve every critical/major/minor ticket the review raises
   (prose/editorial inline; analysis-level only via change-control without altering the
   frozen algorithm or fabricating; rebuild both formats; re-verify). Iterate until the
   review's gates pass.

## Hard invariants (unchanged)
- benchmarks/cec_reference_results/ read-only; results/ staging-only; no fabricated
  data/citations/numbers; frozen algorithm immutable; every number bound to release
  rel-2026-07-10-262fc16c9; commits end with the Co-Authored-By trailer.

## Author-side items that remain regardless (need the human)
- AG-0002 real ORCIDs; AG-0003/0004 funding + COI confirmation; final open-in-Word +
  Save-As-PDF check (D-WORD-01); the actual MDPI submission-account upload + APC.
