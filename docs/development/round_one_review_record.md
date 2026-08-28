# Round-one peer review — the public record

This is the **public** record of the round-one review of `algorithms-4507562` at *Algorithms*
(MDPI): what was asked, what was done about it, and what the evidence showed — including where it
went against the manuscript.

**What is deliberately not here, and why.** Both reviewers declined to sign. Their reports, the
point-by-point response letter (which quotes them), and the editorial correspondence are withheld
from this repository under **D-0049**; republishing an unsigned report is the journal's act at
acceptance, in the journal's own form, not the authors' act mid-revision. Everything below is the
project's own paraphrase of what was *asked*. No reviewer sentence, no report-form detail, no report
identifier and no attribution to any individual appears in this file, and none should be added.

The one companion document that **is** public is the
[pre-registration](../../papers/review_2026_08_24/revision_experiments_preregistration.md) — kept
public on purpose, because the claim that adverse-outcome wording was fixed *before* the outcomes
existed is uncheckable without it.

---

## Outcome

**Major revision**, two reviewers, submitted 1 August 2026. Ten points in total. The revision is
complete: all ten are answered, four of them by experiment — **32,451 runs**, promoted as the
non-superseding release `rev-rel-2026-08-26-dd42d37eb` and written up as Supplementary
**S9.1–S9.4** / Tables **A43–A46**.

## The ten points and what happened

| # | The ask (paraphrased) | Answer | Cost |
|---|---|---|---|
| R1.1 | An abstract sentence reads ungrammatically | Rewritten | text |
| R1.2 | "Adaptive control" misleads against its control-theory sense; retitle | Retitled across 20 files. A second suggestion was **declined with a stated reason** — tiering keys on dimension, resolved before the run, not on operator state | text |
| R1.3 / R2.2 | NP = 5D against the comparators' NP = 100 confounds the result; control for it | **Experiment E2.** Standing survives: first at D = 10, second at D = 30/50/100, top two everywhere. The difference is indistinguishable from zero at D = 10/30 and significant at D = 50/100, so those two rank claims are now qualified as resting in part on the population rule | 5,916 runs |
| R1.4 | The supplement reports a χ² omnibus where the main text uses Iman–Davenport | One convention throughout | 0 runs |
| R2.1 | No direct tiered-versus-uniform comparison | **Experiment E3.** Tiering is demonstrated at D = 10 and D = 50 — **and the result is mixed by design**: the low-dimension parameter set *beats* the shipped one at D = 30, so the 20 ≤ D < 50 tier is disclosed as mis-specified and contribution C2 is narrowed to where tiering was actually shown | 11,832 runs |
| R2.3 | Isolate the eigenframe: compare none / coordinate / eigenframe at one budget | **Experiment E1.** The polish beats no refinement at both active dimensions — **but the learned eigenbasis is beaten by plain coordinate axes at D = 50** and not separated at D = 100. Contribution C1 is therefore claimed basis-neutrally | 2,958 runs |
| R2.4 | ISM shows no standalone benefit; strengthen it or reduce its claimed importance | Reduced. The revision **strengthened the finding against it**: E1 moved ISM from a null to active harm in its terminal exploitation channel. It is positioned as a specified negative result, never as a performance driver | text |
| R2.5 | Do not read the best aggregate rank as overall superiority | The aggregate is labelled descriptive; non-separability is stated where the rank is claimed | text |
| R2.6 | The panel is GSK-family only, so wider competitiveness is not established | **Second limb taken deliberately**: no external algorithm enters any panel, table or claim, and every comparative claim is explicitly family-scoped. This required zero manuscript edits — the restriction already existed in six places | 0 runs |
| R2.7 | Thresholds and constants are fixed with no sensitivity analysis | **Experiment E4**, exploratory by registration and reported descriptively with no hypothesis test. Ordinals hold in 26 of 27 cells; the single flip is favourable and lands on the tier E3 independently identifies as mis-specified | 11,745 runs |

## Two submitted claims were falsified, and both were accepted into the paper

This is the part worth keeping. The experiments were pre-registered, **including the wording to be
used for each unfavourable outcome**, before any of them produced a result. Two came back against
the manuscript and both were carried:

- **The learned eigenbasis is harmful, not neutral.** Plain coordinate axes beat it at D = 50.
  Describing the mechanism as computing an eigenbasis remains correct; presenting that eigenbasis as
  a *benefit* does not, so C1 is now claimed basis-neutrally as a deterministic final polish. The
  polish itself survives — it still beats no refinement at both active dimensions.
- **The 20 ≤ D < 50 tier is mis-specified.** The D = 10 parameter set outperforms the shipped one at
  D = 30, which finally explains a weakness the submitted manuscript had already disclosed
  descriptively. C2 is narrowed to D = 10 and D = 50.

Neither is a defect awaiting repair. Any drift back toward the pre-revision story is treated as a
critical integrity defect, and the audit instrument says so in terms.

## Editorial obligations attached to the decision

The decision letter set a **short revision window** and a five-point check-list. Four of the five are
discharged or inapplicable: references are relevant, the point-by-point response exists, no reviewer
recommended a reference, and nothing was found impossible to address.

**The fifth is discharged on the repository side (2026-08-27/28).** The letter asks that revisions
be *highlighted in the manuscript* so editors and reviewers can see the changes. The project now
produces exactly that: a **latexdiff marked-up manuscript** (additions underlined, deletions struck
through, in place) *and* a **change register** listing all 93 changed passages as-submitted against
as-revised with the reviewer point each answers — both derived from the tagged diff, both
rebuildable from `papers/scripts/`. One rendering limit is disclosed in the response rather than
left to be discovered: latexdiff emits preamble changes as comments, so the retitle does not appear
as visible markup and is named in the letter instead. Whether the editors accept this treatment is
their call, but what is being sent is the thing the check-list asks for, not a substitute.

**A claim recorded here earlier was wrong and is withdrawn.** This paragraph used to say the
manuscript already highlights a few author-flagged passages, so a blanket pass would collide with
existing markup. **It does not.** Checked 2026-08-27 across `main.tex`, `supplementary.tex` and
all six section files: no `\hl`, no `soul`, no `colorbox`, no highlighting macro of any kind. The
only hits are the word "highlighted" in ordinary prose. There is no markup to collide with, so
the obstacle that reasoning rested on does not exist.

## Round-two addendum (2026-08-28)

Ahead of resubmission, a fifth pre-registered experiment was added: **E5, dimension-boundary
sensitivity** (pre-registration Amendment A4, filed before execution; 1,740 new runs promoted as
the additive release `rev2-rel-2026-08-28-203c78744`, with the fifth registered cell reused from
round one's E3). It answers the *threshold* half of the sensitivity request that the round-one
study E4 had answered only for constants. Result, adverse cells first: at D = 30 the shipped
middle profile is beaten from **both** neighbouring tiers; at D = 100 the 50 ≤ D < 100 set beats
the shipped upper profile on paired means while the family ordinal is unchanged; the boundaries
are insensitive at D = 10 and D = 50 — exactly where the narrowed contribution claims them.
Reported in Supplementary S9.5 / Table A47, limitations updated.

The same pass fixed a statistical-convention deviation the round-one analyzer carried (the
manuscript's stated 10⁻⁸ tie rule was not applied to E1–E3; Amendments A5–A6 record the
correction and its one decision-level consequence — the E1 D = 100 basis contrast is separated
under the stated rule), and retired the last pre-revision claim sites named by an external
second-round audit. Frozen state: pass-49 / tag v2.22.

## Where the rest lives

- **Current state, always:** [`REVISION_STATUS.md`](../../REVISION_STATUS.md) — §2 for the
  disposition table, §3 for what each phase applied.
- **Governance:** `papers/governance/decision_log.md` (D-0046 onward) and the change-request
  register.
- **Evidence:** release `rev-rel-2026-08-26-dd42d37eb`, with the analysis bundle self-manifested
  under `papers/analysis/`.
- **Audit instrument:** `papers/PAPER_REVIEW_PROMPT.md` §1.5.3-J carries all ten points with the
  verification each now requires, so a future review run verifies rather than re-raises them.
