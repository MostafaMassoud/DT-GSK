# PHASE 6 — Prose-Quality Pass

*(**Renamed 2026-08-01** from `PHASE_6_humanization.md`. The old file name carried the revoked framing described below into every directory listing of this repository, where a reader sees it before opening anything, so the file now carries its corrected title instead. Git history preserves the original name and every prior revision; the rename is recorded in `papers/governance/decision_log.md` (D-0033) and in the precedence register, and no substantive content changed at the rename.)*

> ## SUPERSEDED — RETAINED AS HISTORICAL RECORD. DO NOT APPLY AS WRITTEN.
>
> **The detector-oriented framing in this file was formally revoked by this
> project's own governance before submission.** Two passages — the objective
> below ("so the text lacks the statistical fingerprints of machine
> generation") and the note further down that good prose "happens to evade
> naive AI-text classifiers" — are recorded as **OBSOLETE / SUPERSEDED** in
> [`papers/governance/instruction_precedence.md`](../governance/instruction_precedence.md)
> (conflict **C-07**, and precedence row **S-10**).
>
> They are superseded by `papers/PAPER_BUILD_PROMPT.md` §0.3, which is binding:
> **"Wording intended to evade AI-text detectors is prohibited. The writing goal
> is genuine academic clarity, specificity, and integrity."** The same
> prohibition is restated at PAPER_BUILD_PROMPT.md:6648 ("a prose-quality audit,
> not an attempt to evade authorship detection") and :7196, and the review
> instrument's §18.4 forbids recommending detector-gaming edits at all. **No
> phase of this project targeted, measured, or optimized a detector score.**
>
> **What remains usable here** is the craft guidance — prefer specific to
> generic phrasing, delete hollow connectives, never pad, never add fake
> hedging, never fabricate — read as writing-quality examples only, stripped of
> the detector motive. The integrity note immediately below is the operative
> constraint and was never relaxed: this is a style pass over *already frozen*
> content that may not change any number, citation, claim, or scope qualifier.
>
> The file is kept rather than deleted because it is part of the audit trail:
> the governance records key their supersession ruling to this document by
> quotation, under both its current and its former name. Banner added
> 2026-08-01; the file was renamed the same day (see the note above the
> banner).

**Objective (superseded wording — see banner).** Make the DT-GSK manuscript read
as expert-human prose — varied rhythm, concrete paper-specific detail, honest
local hedging — while changing not one fact, number, citation, or claim.

> **INTEGRITY NOTE (read first, non-negotiable).** This phase is a **style pass
> over true content**. You may re-order words, split or merge sentences, delete
> hollow connectives, and rewrite generic phrasing into specific phrasing. You
> may **not** change any number, any citation key, any reported win/tie/loss, any
> statistical verdict, any effect size, any dimension, run count, or scope
> qualifier. If a "nicer" sentence would require a fact you cannot verify from the
> bound data, keep the duller true sentence. **Integrity (constraints C1, C2, C6,
> C7) outranks style, always.** When in doubt, restyle less.

This file expands `papers/PAPER_BUILD_PROMPT.md` **Phase 6** and **Part 7** into
an operational, per-paragraph checklist plus worked rewrites. It follows
`PHASE_5_supplementary.md` (full main text + supplement drafted and all numbers
bound to committed data) and hands to `PHASE_7_review.md` (adversarial review).
The manuscript lives in `papers/sections/*.tex`
(`introduction.tex`, `literature_review.tex`, `proposed_algorithm.tex`,
`performance.tex`, `conclusions.tex`) and `papers/sections/supplementary_content.tex`.
The admissible citation set is the 57 locked keys in Appendix A of
`papers/PAPER_BUILD_PROMPT.md`; do not introduce, rename, or drop any key here.

---

## Prerequisites

Do not start Phase 6 until all of the following hold:

1. **Draft complete.** Every main-text section and the supplement are fully
   drafted prose (not outline, not TODO stubs). Phase 5's exit gate has passed:
   no critical result lives only in the supplement, and every main↔supplement
   cross-link resolves.
2. **Numbers bound.** Every table, figure, and in-text number traces to committed
   data plus a commit SHA (constraint C2). Phase 6 must never be the step that
   introduces a number — it can only restyle sentences around numbers that are
   already correct and locked.
3. **Citations closed.** Every `\cite{...}` key is one of the 57; every key is
   actually used; zero undefined references (constraint C1). Phase 6 does not add
   or remove citations; it only changes surrounding wording.
4. **A frozen baseline.** Tag or stash the pre-pass tex so the integrity
   diff in Task 6.6 has a clean "before" to compare against. Recommended:
   `git tag phase6-baseline` before the first edit, or work on a dedicated branch.

If any prerequisite is unmet, return to the owning phase. Restyling an unbound
draft risks laundering an unverified number into publishable-looking prose — the
worst possible failure mode for this project.

---

## What this pass is and is NOT

**Legitimate (do this).** Write genuinely well. Expert human technical prose has
a texture: sentence lengths vary hard, paragraphs are lumpy, claims are anchored
to specific measurements, and the author admits friction where friction exists.
The target is genuine academic clarity, specificity, and integrity. It is not a
detector score, and no detector score was ever targeted, measured, or optimized
in this project.

> *Superseded sentence, removed 2026-08-01 and recorded here for the audit
> trail:* the original text continued "When you write that way, the text also
> happens to evade naive AI-text classifiers — not because you gamed them, but
> because it no longer carries their tells." That framing is revoked by
> `PAPER_BUILD_PROMPT.md` §0.3 and logged as conflict **C-07** in
> `papers/governance/instruction_precedence.md`. The original wording remains in
> git history.

**Illegitimate (never do this).**

- **Fabrication.** Inventing a number, a mechanism behaviour, or a citation to
  make a sentence land. A vivid false sentence is a retraction risk; a plain true
  one is publishable.
- **Fake uncertainty.** Adding hedges to sound human ("results may vary,"
  "arguably") where the data is actually firm. Hedge only where the evidence is
  genuinely limited, and say exactly how (Task 6.4).
- **Synonym-swapping over robotic structure.** Replacing "leverage" with
  "utilize" while leaving a four-tricolon paragraph with uniform 22-word
  sentences intact. That defeats a keyword filter and fails a human reader. The
  structure is the tell; fix the structure.
- **Padding.** Adding throat-clearing, restatement, or filler to "sound
  academic." Concision reads human when the content is specific. Length is not
  humanity.

The test for every edit: *does this make the prose more true-and-specific, or am
I just decorating?* Only the former is in scope.

---

## Tasks

Work **section by section, paragraph by paragraph**. Do not batch-edit across the
whole manuscript in one sweep; the point is per-paragraph judgement. Suggested
order: `proposed_algorithm.tex` and `performance.tex` first (densest, most
tell-prone), then `introduction.tex` and `literature_review.tex`, then
`conclusions.tex`, then the supplement.

### 6.1 Tell-scan every paragraph → flagged-spans list

Read each paragraph once, hunting only for machine tells and banned vocabulary.
Produce a running flagged-spans list (a scratch file under the session scratchpad
is fine; do not commit it into the paper). For each flag record: file, section,
approximate line, the offending span, and the tell category. Categories to scan
for, from Part 7.1:

- **Uniform sentence rhythm.** A run of sentences all within a few words of the
  same length, or all opening with the subject. Mark any paragraph where three or
  more consecutive sentences share a length band and an opening pattern.
- **Compulsive tricolons.** The "X, Y, and Z" triple used more than once in a
  paragraph, or as the default shape for every list. Flag every tricolon so you
  can later keep the good ones and break the reflexive ones.
- **Hollow connectives.** Sentence-initial *Moreover, Furthermore, Additionally,
  Importantly, Notably, Overall,* and the phrase *It is worth noting that* —
  flag each and mark whether it carries logical weight or is empty scaffolding.
- **Signposting overload.** More than one "First/Second/Third" ladder per
  section; "As mentioned above / As discussed / In this section we will."
- **Empty intensifiers.** *significantly, substantially, dramatically, markedly,
  considerably* — flag every instance not immediately backed by a number or a
  named statistical test.
- **Abstract-noun-for-verb.** "performs an optimization of," "provides an
  improvement in," "achieves a reduction of," "conducts an evaluation of."
- **Symmetric paragraph shapes.** Sections where every paragraph is 4–5 sentences
  of similar length. Flag the section, not a span.
- **Banned vocabulary (hard stop — zero tolerance).** Search the tex for every
  item below and flag all hits. These are near-certain machine tells in this
  register and must be absent at the exit gate:

  > delve, tapestry, realm, **leverage** (as a verb), **robust** (in any
  > non-statistical sense), showcase, underscore, pivotal, testament to,
  > seamless, holistic, cutting-edge, paradigm shift, in the ever-evolving,
  > it is worth noting that, a myriad of, plays a crucial role, pave the way,
  > shed light on.

  Notes on the two context-sensitive ones: **"robust"** is permitted *only* in
  its precise statistical sense (e.g. "robust to the choice of \(\gamma\)" backed
  by a sensitivity result, or "a robust estimator"); everywhere else ("robust
  performance," "robust algorithm") it is banned — say what you actually mean
  ("stable across the 30 functions," "low run-to-run variance"). **"landscape"**
  is permitted only as the literal *fitness landscape*; "the optimization
  landscape," "the research landscape" are banned.

Do a mechanical grep pass to catch the fixed strings, then a human read for the
structural tells a grep cannot see (rhythm, symmetry, empty connectives in
context). The output of 6.1 is the flagged-spans list that drives 6.2–6.3.

### 6.2 Rhythm & structure rewrite

Work the flagged-spans list. For each flag:

- **Vary length hard.** After a long, clause-rich sentence, write a short one —
  six to nine words. Not as a gimmick every time, but often enough that no
  paragraph reads metronomic. A results paragraph that explains a mechanism over
  30 words, then lands the verdict in "The gain vanishes at \(D=10\).", reads
  human. Aim for genuine variance, not an alternating pattern (an alternating
  long/short/long/short is itself a rhythm).
- **Vary openings.** Not every sentence starts with the grammatical subject.
  Open sometimes with a subordinate clause ("Because the support graph is EMA-
  smoothed, ..."), sometimes with a prepositional anchor ("At \(D=100\), ..."),
  sometimes with the plain subject. Do not manufacture inversions that hurt
  clarity.
- **Break reflexive tricolons.** Keep a tricolon when the three items are genuinely
  parallel and you want the cadence. Break it otherwise: split into a pair plus a
  follow-on sentence, drop the weakest member into a subordinate clause, or expand
  one member because it deserves more than a list slot. One deliberate tricolon
  per few paragraphs; not three per paragraph.
- **Cut hollow connectives.** Delete an empty *Moreover/Furthermore/Additionally*
  outright — the logical relation is usually already clear from content, and if
  it is not, name the actual relation ("This matters because...", "The exception
  is..."). Keep a connective only when it does real work (genuine contrast,
  genuine consequence).
- **De-signpost.** Trust the section headings and the reader. Delete "In this
  section we will" openers; delete "As mentioned above" back-references unless the
  cross-reference is load-bearing (then use a real `\ref`/`\cref`). Keep at most
  one ordinal ladder per section.
- **Verb up abstract nouns.** "performs an optimization of the rotated Rastrigin"
  → "optimizes the rotated Rastrigin." Shorter, more direct, less mechanical.
- **Break paragraph symmetry.** Let some paragraphs be two sentences and some be
  eight. Merge two thin, related paragraphs; split one that carries two ideas.

Constraint reminder: none of these edits may touch a number, a `\cite`, a table
value, or a claim's truth value. If breaking a tricolon would strand a fact,
re-house the fact, do not drop it.

### 6.3 Specificity injection (the highest-leverage task)

Genericness is the master tell (Part 7.3). Wherever the tell-scan or your read
finds a sentence that could appear in *any* metaheuristic paper, replace the
generic phrasing with something that could only be about **DT-GSK, this
benchmark panel, these results**. Concrete levers, drawn from the actual method
and evaluation:

- **Name the mechanism, not "the algorithm."** Instead of "the method adapts its
  parameters," name the substrate: the ACE knowledge-control layer, NLPSR
  population reduction, the SGSM support graph with its EMA update and confidence
  gate, blended survival/exploration (BSE) with the Cauchy rescue
  (`yao1999evolutionary`), ARGP, the linkage-aware block crossover, the eigenframe
  final polish, or the Nelder–Mead endgame
  (`nelder1965simplex`, `gao2012implementing`).
- **Name the function, class, and dimension.** Not "on difficult functions" but
  "on the rotated multimodal cases (F4–F10) at \(D=50\)." Use the correct domain
  idiom precisely: *basin, separability, rotation, stagnation, elite archive,
  linkage/interaction structure*. A rotated function destroys coordinate
  separability — say that, and say why it stresses a structure-blind operator.
- **Attach the number that is already bound.** Not "a notable improvement" but the
  specific bound gap with its scope, e.g. the exemplar in Part 7.2: "the F10 D50
  gap of 1.69× (three trials)." Report effect sizes with their test:
  \(A_{12}\) (`vargha2000critique`) for pairwise magnitude, BCa intervals
  (`efron1993introduction`) for the headline gaps, Friedman rank
  (`friedman1937use`) with the Nemenyi CD reading (`demsar2006statistical`),
  Holm-corrected Wilcoxon (`wilcoxon1945individual`, `holm1979simple`) for
  pairwise verdicts. **Only cite the number already in the bound tables — do not
  compute a fresh one here.**
- **Say the mechanism's cost, not "efficiently."** The method is not "efficient";
  it is \(O(D^2)\) in memory and \(O(D^3)\) for the once-per-run eigenframe polish,
  bounded at high \(D\) by cadence-thinning. Specifics of cost read expert;
  "efficient" reads generated.
- **Contrast against the named alternative.** The SGSM learns interaction
  structure "for free" during search — contrast explicitly with differential
  grouping's dedicated probing budget (`omidvar2014dg`) and with eigenvector
  crossover (`guo2015eig`). "Unlike prior work" is generic; naming the prior work
  and the exact difference is specific.

Every specificity edit must remain true to the bound data. Inject detail you can
point to in a committed table or in `proposed_algorithm.tex`; never invent a
plausible-sounding figure.

### 6.4 Local hedging & one honest limitation per results subsection

Generators smooth over friction; humans admit it precisely. In `performance.tex`,
**let exactly one honest limitation breathe per results subsection** — stated
locally, with its scope, not as a blanket disclaimer.

- **Local and earned.** "We did not test beyond \(D=100\)" beats "results may not
  generalize." "The low-\(D\) advantage is smaller and, at \(D=10\), the family
  is statistically tied on [N] of the [M] functions" beats "performance varies by
  dimension." Tie every hedge to the specific evidence (a real count, a real
  dimension, a real function class) — placeholders here stand for numbers you must
  read from the bound tables, never guess.
- **Draw on the project's known honest limitations** (already established; do not
  overstate or understate them): the low-\(D\) behaviour is structural, not a
  local-search-budget artifact — the interaction-structure subsystems are gated to
  high \(D\) by design, so at low \(D\) DT-GSK behaves closer to the base GSK
  operators (`mohamed2020gaining`); the \(O(D^2)\) memory cost matters at very
  high \(D\); structure exploitation can misfire on functions where the assumed
  interaction structure is absent or misleading (e.g. fully separable cases where
  the block crossover buys nothing).
- **Do not over-hedge.** One limitation per subsection, said once, cleanly. Do not
  hedge a firm result into mush. If a result is strong and the test backs it, state
  it plainly and move on. The candour is calibrated, not reflexive.
- **Keep it consistent with C7.** Losses and limitations are reported candidly
  elsewhere already; Phase 6 only sharpens the *wording* of those admissions, it
  does not add new losses or soften real ones.

### 6.5 Three-sentence test sweep

Final structural sweep. Slide a three-sentence window through every section. For
each window ask: *could these three consecutive sentences sit unchanged in a
generic optimization paper?* If yes, rewrite them to be about this method, these
results, this benchmark — using the 6.3 levers. Pay special attention to the
usual generic hotspots:

- Introduction motivation ("Optimization problems are ubiquitous...") — replace
  with the specific high-\(D\) real-parameter framing and the *specific* GSK
  limitation DT-GSK removes (fixed, structure-blind operators).
- Related-work transitions and the "gap" paragraph — make the gap concrete to the
  GSK family and to structure-aware EC, not generic.
- Results topic sentences and the conclusion recap — anchor to bound numbers and
  named mechanisms, not to "our approach demonstrates strong performance."

The window catches what per-flag editing misses: three individually-fine
sentences that together say nothing specific. Rewrite until no such triple
survives in any section (this is also the exit-gate criterion).

### 6.6 Integrity diff (mandatory gate before hand-off)

Confirm the entire pass was **style-only**. Procedure:

1. **Generate the diff.** From the repo root, diff each edited tex against the
   frozen baseline, e.g. `git diff phase6-baseline -- papers/sections/`. Review
   every hunk.
2. **Number invariance.** For every hunk, confirm no numeral, unit, dimension,
   run count, p-value, effect-size value, or table cell changed. Fast check:
   extract all numeric tokens from before and after each file and diff those sets
   — they must be identical. Any numeric delta is a defect; revert it.
3. **Citation invariance.** Confirm the multiset of `\cite`/`\citep`/`\citet`
   keys is unchanged per file (same keys, same count). No key added, removed, or
   swapped. Re-run the Phase 8 / constraint-C1 citation check to be sure the set
   is still ⊆ the 57 and all still used.
4. **Claim invariance.** Read each hunk for meaning drift: a restyled sentence
   must assert the same thing (same subject, same verdict, same scope, same
   hedge strength where the hedge reflects real evidence). "Outperforms on most
   functions" must not become "outperforms on all"; a tie must not become a win.
5. **Cross-reference integrity.** Confirm no `\ref`/`\cref`/`\label` was broken by
   a merge/split, and that main↔supplement pointers still resolve (Phase 5's
   invariant).
6. **Record.** Note in the revision log that Phase 6 diffs were reviewed and are
   style-only (this feeds constraint C6/Part 7 on the compliance checklist).

If any check fails, fix the specific hunk and re-diff. The pass is not complete
until the integrity diff is clean.

---

## Worked rewrites

Illustrative BEFORE→AFTER pairs on DT-GSK-flavoured sentences. **Every AFTER is
factually neutral or placeholdered** (`[X.XX]`, `[N]`, `[D]`) so no fabricated
number is implied — in the real edit you bind the placeholder to the committed
value, never invent it. These show the *style* transformation only.

### Rewrite 1 — Tricolon-heavy sentence, broken

**BEFORE**
> DT-GSK leverages the SGSM support graph, exploits linkage structure, and
> showcases robust performance across separable, partially-separable, and fully
> non-separable functions, underscoring its holistic design.

Tells: banned *leverages/showcases/robust/underscoring/holistic*; two stacked
tricolons; abstract and generic.

**AFTER**
> DT-GSK reads interaction structure from the SGSM support graph and uses it to
> group linked variables for block crossover. The payoff is largest on the
> partially-separable and rotated functions, where coordinate-wise operators
> waste moves; on fully separable cases the block crossover buys little.

### Rewrite 2 — Hollow-connective opener, cut

**BEFORE**
> Moreover, it is worth noting that the proposed method plays a crucial role in
> significantly improving convergence, and furthermore paves the way for future
> extensions.

Tells: *Moreover / it is worth noting that / plays a crucial role / paves the way*;
*significantly* with no number; empty forward-looking filler.

**AFTER**
> Convergence improves too: on the rotated multimodal cases the median error at
> the FES budget drops by [X.XX]× relative to the base GSK operators. Whether the
> same holds under a covariance-aware refinement is open — we have not built one.

### Rewrite 3 — Generic results sentence made specific (with A12 / BCa)

**BEFORE**
> Our approach demonstrates substantially superior performance over the baselines,
> confirming its effectiveness on the benchmark.

Tells: generic (fits any paper); *substantially* unbacked; "effectiveness on the
benchmark" says nothing; fails the three-sentence test alone.

**AFTER**
> Against APGSK on F10 at \(D=50\), DT-GSK wins the headline gap of [X.XX]×, with
> \(A_{12}=[0.XX]\) (`vargha2000critique`) and a BCa 95\% interval of
> \([{[lo]},\,{[hi]}]\) excluding 1 (`efron1993introduction`). The Holm-corrected
> Wilcoxon verdict (`wilcoxon1945individual`, `holm1979simple`) agrees.

### Rewrite 4 — Over-hedged sentence, localised

**BEFORE**
> Results may vary depending on the problem, and performance could potentially be
> influenced by various factors in certain settings.

Tell: blanket fake uncertainty that admits nothing checkable.

**AFTER**
> The advantage is dimension-dependent. At \(D=10\) the family is statistically
> tied on [N] of the [M] functions, because DT-GSK's structure-learning
> subsystems are gated to high \(D\) and contribute little in low dimension.

### Rewrite 5 — Uniform rhythm, varied; abstract noun verbed

**BEFORE**
> The algorithm performs an adaptation of its parameters through the ACE
> mechanism. The algorithm performs a reduction of the population through NLPSR.
> The algorithm performs a final polish through the eigenframe procedure.

Tells: three near-identical openings and lengths; abstract-noun-for-verb in each.

**AFTER**
> ACE adapts the knowledge-control parameters online; NLPSR shrinks the
> population on the usual linear schedule. The eigenframe polish comes last — one
> \(O(D^3)\) pass on the interaction eigenbasis, run on a thinned cadence at high
> \(D\) so its cost stays bounded.

### Rewrite 6 — Generic contribution claim made specific vs. named prior work

**BEFORE**
> Unlike existing methods, our method leverages problem structure in a robust and
> seamless manner, representing a paradigm shift in the field.

Tells: banned *leverages/robust/seamless/paradigm shift*; "unlike existing
methods" without naming them; grandiosity.

**AFTER**
> Differential grouping spends a dedicated probing budget to recover variable
> interactions before search begins (`omidvar2014dg`). The SGSM instead
> accumulates the same signal for free from move outcomes during search, gated by
> a confidence threshold before it is trusted — closer in spirit to eigenvector
> crossover (`guo2015eig`) but acting on a learned support graph rather than a
> covariance eigenbasis.

---

## Pitfalls & anti-patterns

- **Changing a number while restyling.** The cardinal sin. Splitting a sentence or
  moving a clause must never nudge "1.69×" to "1.7×", "\(D=100\)" to "\(D=50\)", or
  "[N] of [M]" to a rounder pair. The integrity diff (6.6) exists to catch this;
  do not rely on it — be careful at edit time.
- **Deleting a needed citation.** Merging two sentences can orphan a `\cite`.
  Every claim that needed support before still needs it after. Never drop a key to
  make a sentence flow; re-house it.
- **Over-casual register.** Improving prose quality is not colloquializing. No contractions in
  formal claims, no "basically," no jokes, no rhetorical questions as filler. The
  target is a strong human *technical* author: precise, occasionally dry, never
  chatty. Varied rhythm ≠ casual tone.
- **Introducing ambiguity.** A shorter sentence that loses the referent of "it,"
  or a broken tricolon that drops a scope qualifier, trades one tell for a defect.
  Clarity outranks rhythm. If the varied version is ambiguous, keep it clear.
- **Detector-driven synonym spam.** Swapping banned words for near-synonyms while
  leaving robotic structure (uniform rhythm, symmetric paragraphs, empty
  connectives) is the classic failure. It may move a classifier score and will
  still read generated. Fix structure and specificity, not just vocabulary.
- **Manufacturing the rhythm as a pattern.** A rigid long/short/long/short
  alternation is itself a machine rhythm. Aim for genuine, uneven variance.
- **Hedging a firm result into mush** or, conversely, deleting a real limitation
  to make the paper look cleaner (violates C7). Calibrate: firm where the evidence
  is firm, hedged exactly where it is thin.
- **Editing tables/figures/algorithm environments.** Phase 6 touches prose. Do not
  restyle inside `tabular`, `algorithm2e`, captions-that-are-really-data, or
  equation environments beyond trivial surrounding text — and never their content.

---

## Exit gate

Phase 6 is complete only when **all** of the following hold:

- [ ] **Three-sentence test passes everywhere.** No three consecutive sentences in
      any section (`introduction`, `literature_review`, `proposed_algorithm`,
      `performance`, `conclusions`, supplement) could sit unchanged in a generic
      optimization paper.
- [ ] **Banned vocabulary absent.** A grep for every banned term returns nothing
      except the two context-licensed exceptions used correctly ("robust" in its
      statistical sense only; "landscape" only as the literal fitness landscape).
- [ ] **Rhythm varied.** No paragraph is metronomic; sentence lengths and openings
      vary; paragraph shapes are lumpy; reflexive tricolons broken; hollow
      connectives and signposting overload removed.
- [ ] **Specificity dense.** Generic phrasing replaced with named mechanisms,
      named functions/classes/dimensions, and bound numbers with their tests.
- [ ] **One honest limitation per results subsection**, stated locally and tied to
      real evidence; no blanket fake uncertainty.
- [ ] **Integrity diff clean (6.6).** Numeric-token set unchanged per file;
      citation multiset unchanged and still ⊆ the 57; no claim/scope drift; all
      `\ref`/`\cref`/cross-links intact. Recorded in the revision log as style-only
      (satisfies C6/Part 7).

Any unchecked box sends you back to the relevant task. Integrity boxes are
blocking regardless of how good the prose reads.

---

## Hand-off

On a clean exit gate, hand to **`PHASE_7_review.md`** (adversarial review &
revision loop). Phase 7's A1 pass re-reads the manuscript for the prose
defects listed above and must find none; its R1 (Q1) and R2 (Q2) referee
passes then attack novelty, baselines, statistics, reproducibility, and clarity.

> *Superseded wording, replaced 2026-08-01 and recorded here for the audit
> trail:* the sentence above originally read "Phase 7's A1 / AI-text-adversary
> pass reads only for machine-generation tells and must find none." This is the
> **third** detector-oriented passage in this file, revoked on the same ground
> as the two struck above — `PAPER_BUILD_PROMPT.md` §0.3 and conflict **C-07**.
> It survived that strike because the precedence register had recorded the
> quotation against `PHASE_7_review.md` line 461, where it has never appeared
> (checked against the full history with `git log -S`); the register's
> misattribution is corrected at the same date, so the record and the file now
> agree. As with the other two, the framing is revoked but the sentence is
> preserved here rather than deleted.
Carry forward: the frozen `phase6-baseline` tag (so any Phase 7 prose fix can be
integrity-checked the same way) and the note that Phase 6 diffs were confirmed
style-only. If Phase 7 revisions touch prose, re-apply this file's tell-scan and
integrity-diff to the changed spans before re-closing the C6 gate.
