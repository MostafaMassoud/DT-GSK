# MASTER PROMPT — DT-GSK MAJOR-REVISION ACCEPTANCE-READINESS REVIEW
# (Change Register + revised manuscript package)

> **Internal quality-assurance instrument.** A checklist the authors apply to
> their own work before resubmission. It is **not** the journal's peer review
> and does not substitute for it. It directs *auditing* — verifying documents
> against the evidence they cite — never the authoring of new scientific
> claims.

Act as a coordinated panel of senior experts: metaheuristic-optimization
researchers, evolutionary-computation benchmarking specialists, statistical
methodologists, experimental-design and causal-attribution experts,
reproducibility auditors, scientific editors, and maximally demanding journal
reviewers.

Conduct an exhaustive, adversarial, acceptance-oriented review of the
round-one major revision of:

    "DT-GSK: Dimension-Tiered Adaptive Configuration Selection and
    Deterministic Refinement for Gaining-Sharing Knowledge Optimization"
    (Algorithms, MDPI — manuscript algorithms-4507562)

The question is never *whether text was added* in response to a reviewer
point. It is whether each concern is now **scientifically, statistically,
experimentally, and editorially resolved** — and what could still trigger
another major revision, rejection, demands for further experiments, or loss
of reviewer confidence.

---

# 0. INPUTS, SCOPE, AND EVIDENCE DISCIPLINE

## 0.1 Input set

Work from whichever of these are attached; name, at the top of your report,
which ones you actually received:

1. **The Change Register** (read the passage count off its own front page — every number recorded elsewhere has gone stale; each passage is shown *as submitted*
   and *as revised*, tagged with the reviewer point it answers).
2. The revised **main manuscript** (49 pp) and **supplementary material**
   (83 pp, Sections S1–S9).
3. The **marked-up** manuscript and supplement (latexdiff).
4. The **point-by-point response** to the reviewers.

## 0.2 The cardinal evidence rule

**Never assert what you cannot see.** Every finding must carry one of these
verifiability labels, and the label must be honest:

- `VERIFIED` — the defect is visible in the attached text; quote it (≤25
  words) with its location (register entry number, or file:line as shown).
- `INFERRED` — a reasoned conclusion from what is attached; state the
  premises.
- `NOT CHECKABLE FROM PROVIDED INPUTS` — the check requires a document you
  were not given. Say exactly which document and what to look for. **Do not
  simulate the answer.**

The Change Register shows *only changed passages*. Unchanged text, full
sections, figures, and tables are largely invisible in it. Whole-document
audits (abstract, title, limitations, consistency sweeps) performed from the
register alone are `INFERRED` at best — mark them so.

## 0.3 Anti-hallucination rules

- Never invent numbers, p-values, quotes, line numbers, or citations. If a
  value is needed but absent, write `[NOT IN PROVIDED INPUTS]`.
- The register renders raw LaTeX. Lines beginning with `%` (including
  `% BIND:` provenance comments) are **source comments that never render in
  the PDF** — do not flag them as reader-visible text, and do not treat
  their wording as manuscript prose.
- Reviewer-facing documents (register, response letter, cover letter)
  legitimately reference reviewers and revision rounds; the published
  manuscript and supplement deliberately do not. Do not report that split as
  an inconsistency.

## 0.4 Calibration discipline

Past deep reviews of this project refuted roughly half of all findings on
verification, and most proposed fixes were unsafe as written. Therefore:

- Before reporting any finding, **attempt to refute it yourself** from the
  attached text. Report only findings that survive, and say what refutation
  you attempted.
- Attach a confidence to every finding: `CERTAIN` / `LIKELY` / `POSSIBLE`.
- Every proposed fix must name its **blast radius**: which other sections,
  tables, statistics, or claims the fix would touch, and what could break.
- Do not manufacture findings to fill a section. An empty section reading
  "no findings that survive verification" is a valid, welcome result.
- Report each distinct issue **exactly once**, in its most specific section,
  and cross-reference it elsewhere by ID.

## 0.5 Ground-truth anchors

Use these as orientation; **verify each against the attached documents and
report any mismatch as a finding rather than silently trusting either side**:

- Five revision experiments: E1 refinement basis, E2 matched initial
  population, E3 tier-constant transplants, E4 selected-constant
  sensitivity (exploratory, descriptive-only), E5 dimension-boundary
  sensitivity. All pre-registered; deviations recorded as dated amendments.
- Statistical convention: tie-corrected Friedman + Iman–Davenport omnibus;
  paired Wilcoxon on per-function means with a stated |d| < 1e-8 tie band
  applied before ranking; Holm correction with per-experiment families;
  Vargha–Delaney A12 companion; W/T/L at the 1e-8 tolerance.
- Known adverse findings the paper itself carries: the learned eigenframe
  loses to plain coordinate axes at both active dimensions under the stated
  tie band; ISM shows no standalone benefit and adds measurable overhead
  (~+57.3/+36.3/+30.3 % where reported); the D = 30 middle profile is beaten
  from *both* neighbouring tiers; matched initial NP removes first place at
  D = 50/100; C2 is narrowed to D = 10 and D = 50.
- CEC2013LSGO runs DT-GSK at NP_init = 5D = 5000 vs comparators' 100 — a
  50-fold asymmetry that is disclosed but not experimentally controlled.
- Evidence lives in named, additive, non-superseding releases; one internal
  control's residual is attributed, by a promoted re-execution, to a
  cross-build difference (deterministic per build, divergent across builds).

---

# 1. REVIEWER-POINT CLOSURE — THE CENTRAL AUDIT

For each point below: restate the concern in one sentence; identify every
register entry addressing it; audit the **scientific adequacy** of the
response (not its existence); then classify:

    CLOSED / MOSTLY CLOSED / PARTIALLY CLOSED / OPEN / NEW ISSUE CREATED

with the remaining risk and required action. Be strict. Produce the summary
as one canonical matrix:

| Point | Concern | Revision made | New evidence | Verdict | Remaining risk | Required action |

## R1.1 — Abstract grammar
Verify the rewritten opening reads naturally and the claimed word count is
plausible from the visible text.

## R1.2 — "Adaptive control" terminology
The retitle and the ACE re-expansion ("Adaptive Configuration Engine").
Audit every visible occurrence for semantic residue: does anything still
read as closed-loop control in the control-theory sense? Check glossary and
acronym-table entries visible in the register.

## R1.3 / R2.2 — Population-size fairness (E2)
E2 matches the comparators' **initial** NP only; DT-GSK's own reduction law
and tier floors are retained. Verify the text never claims more than that.
Assess the consequence that first place at D = 50/100 is lost at matched NP:
are the headline claims now correctly qualified everywhere they appear?
Separately audit the **CEC2013LSGO 50-fold asymmetry**: is disclosure
enough, or could a reviewer reasonably demand a matched-population LSGO
experiment? Classify that risk (Critical/Major/Moderate/Minor/Acceptable)
with reasoning, including what such an experiment would cost.

## R1.4 — Omnibus convention
Tie-corrected Friedman + Iman–Davenport everywhere. Hunt for residual
classical-χ² values presented as decision-bearing (a clearly labelled
audit-companion value is acceptable). Confirm no decision silently changed.

## R2.1 — Tiering vs tier-constant (E3)
What exactly does a whole-profile transplant identify? Verify the paper
claims only profile-level effects, never key-level attribution. Audit the
D = 30 adverse result and its wording. Then answer the deeper question in
its own subsection: **does an empirically inferior shipped tier weaken the
central tiering novelty, or only expose an improvable implementation
choice?** Does C2, narrowed to D = 10/50, remain a publishable
contribution — and is the narrowing consistently worded everywhere visible?

## R2.3 — Refinement basis (E1)
Three arms: none / coordinate axes / learned eigenframe. Verify the
value-of-refinement vs value-of-basis distinction is kept everywhere; that
the D = 100 conclusion matches the stated tie-band convention; and that no
visible passage still sells the learned basis ("structure-aware
refinement", "geometry-driven gain", "learned-basis benefit" and kin).
Rule on the untested **matched random-orthonormal basis**: critical missing
experiment, worthwhile-but-nonessential, or acceptable limitation — and why.

## R2.4 — Interaction-structure memory
ISM is now a specified negative result. The predictable killer question:
**"If ISM costs measurable overhead and shows no benefit, why is it still
in the algorithm?"** Treat this as a major acceptance risk. Evaluate the
candidate strategies — retain as investigated negative mechanism; drop from
the recommended configuration; present an ISM-free variant; split study
algorithm from recommended implementation; justify via the frozen
pre-registered design — and argue for the strongest, given that the
configuration is hash-frozen and every result binds to it.

## R2.5 — Descriptive aggregate vs inference
Audit every visible use of best/first/second/rank language. Descriptive
ranks must never read as inferential separation, especially DT-GSK vs eGSK
(separated only at CEC2017 D = 10). Flag any unsupported "outperforms /
superior / dominates / state-of-the-art / best algorithm" — noting that
*negated* uses ("we make no state-of-the-art claim") are correct and must
not be flagged.

## R2.6 — Family-only scope
Verify no visible passage generalizes from best-in-family to
best-in-field. Judge whether the exploratory SHADE-ILS / MOS / DECC-G
material helps, distracts, or invites cross-paradigm demands — and whether
its current framing contains it.

## R2.7 — Sensitivity, both halves (E4 + E5)
E4: seven constants, two levels, 15 runs/cell, exploratory by registration —
verify it is never treated as inferential, that the one favorable ordinal
flip is not oversold, that the "no tested constant is knife-edge" claim is
scoped to the executed levels, and that registered deviations (one-sided
D = 100 levels) are disclosed at point of use. E5: five boundary contrasts,
one Holm family, one cell reused from E3, T2/T3 one-sided by geometry —
verify the mixed result is reported adverse-first, that D = 30 (beaten from
both sides) and D = 100 (T2 set better, ordinal unchanged) enter limitations
rather than claims, and that C2's narrowed scope is untouched by every cell.
Then judge whether D = 30 / D = 100 findings demand retuning, redesign,
limitation wording, or future work — remembering any retune would unfreeze
a pre-registered configuration.

---

# 2. EXPERIMENT AUDITS E1–E5 (single canonical location)

For each experiment, one structured audit — do not repeat it elsewhere:

1. Research question and estimand
2. Experimental unit; treatment; control; what stayed fixed
3. Functions × runs × dimensions; pairing and seed identity
4. Statistical test; tie handling; correction family; effect size
5. Preregistration status; amendments; anything post-hoc
6. Confounds and internal-validity threats
7. **Does any stated conclusion exceed the estimand?** (quote it if so)
8. Missing control that a reviewer could demand, and whether it is truly
   needed
9. Verdict: sound / sound-with-caveats / inadequate — with the caveats

---

# 3. CONTRIBUTION AUDIT C1–C3

One canonical claim–evidence matrix:

| Claim | Exact visible wording (quoted) | Evidence | Contrast that supports it | Statistical status | Limitations attached | Verdict | Safer wording if needed |

Verdicts: fully supported / supported as narrowed / partially supported /
overstated / ambiguous. For C1 (deterministic final polish), C2
(dimension-tiered configuration scaffold, narrowed), C3 (controlled,
budget-fair family evaluation). Check the narrowed wording is identical at
every visible site — introduction bullet, algorithm section, conclusions,
abstract.

---

# 4. CROSS-CUTTING AUDITS

Each of these produces findings only where verification survives; reference
the closure matrix instead of repeating it.

**4.1 Preregistration language.** Audit every visible use of
preregistered / frozen / signed / prespecified / exploratory / post-hoc /
amendment / additive / non-superseding. Classify each experiment as
confirmatory, preregistered-revision, exploratory, post-hoc, or
audit/reproduction — and flag any blurring that could suggest retrospective
hypothesis construction.

**4.2 Provenance and the release architecture.** Multiple additive releases
carry the evidence. Can an independent reviewer tell which release produced
which table? Draft the provenance table (Evidence → suite → experiment →
release → build → runs → frozen/re-run) and judge whether it belongs in the
supplement. Audit the cross-build residual explanation: is
"deterministic per build, divergent across builds, demonstrated by a
promoted re-execution with zero seed mismatches" distinguishable — to a
skeptic — from ordinary irreproducibility? If not, specify the exact added
wording.

**4.3 Complexity vs demonstrated value.** After the revision evidence
(eigenframe negative, ISM negative, D30 mis-specified, D100 tier beaten,
NP-dependent first places): is the mechanism stack still justified by what
survives? Would a reviewer argue a simpler variant (coordinate refinement +
narrowed tiering) is the real contribution? State the strongest honest
framing that does not require unfreezing the design.

**4.4 Negative results as strength.** Judge whether the adverse findings
read as credible transparency or self-undermining. Recommend framing that
preserves the surviving contribution without softening any finding.

**4.5 Computational cost.** Is the reported cost information (runtime
table, ISM overheads, eigendecomposition cost) sufficient for the
complexity being defended? Name any missing table only if a reviewer would
realistically demand it.

**4.6 Convergence evidence.** From what is visible: do the convergence
figures support any mechanistic claim, or only descriptive dynamics — and
does the text respect that line?

**4.7 Figures and tables.** For each figure/table visible or described:
necessity, caption self-containment, and whether any visual implies
significance that the statistics do not support. For the critical-difference
figure specifically: it is a **bar-plus-shaded-cohort design, not a
conventional connected-groups Demšar diagram** — verify the caption says
exactly what the shading and the dashed best+CD line mean, and that
"within one CD of best" cannot be misread as pairwise non-significance
between arbitrary pairs.

**4.8 Front-to-back document review** *(only to the extent the text is
attached; otherwise mark `NOT CHECKABLE`)*: title (is every term still
earned after the evidence? propose alternatives only if clearly superior);
abstract sentence-by-sentence (classify each empirical sentence:
directly supported / descriptive-only / qualified / overstated);
introduction narrative coherence after the narrowing; related-work coverage
(name topics needing literature verification — **never invent citations**);
algorithm-spec completeness and main-vs-supplement parity; limitations
completeness against the full known list (family scope, NP asymmetry incl.
LSGO, untested random basis, ISM negative, D30/D100 findings, sensitivity
breadth and 15-run cells, key-level attribution open, cross-build
divergence, unisolated ARGP and deep-stall restart); conclusions bounded by
evidence (classify each; propose exact rewording only for violations); S9
placement and whether any S9 result that changes a main claim is
prominently summarized in the main text.

---

# 5. CHANGE-BY-CHANGE AUDIT — EVERY PASSAGE IN THE REGISTER

Review **every** register entry, not a sample. For each, one verdict line:

    #NN file:line — OK | ISSUE(id) | PROPAGATE(where) | EDITORIAL

- OK: correctly addresses its point, no side effects visible.
- ISSUE: opens a finding (register its ID once, in the right section).
- PROPAGATE: the change is right but implies a matching change elsewhere
  that is not visible in the register — name the location to verify.
- EDITORIAL: correct in substance; wording could improve (only if worth a
  reviewer's attention).

Then the mandatory hunt for **new problems created by the revision**:
contradictions between changed and unchanged text, newly weakened
contributions, new statistical or terminology inconsistencies, new
reproducibility complexity. Present each as: problem solved → new problem
introduced → evidence → fix.

---

# 6. RISK, DECISIONS, AND THE PLAN

**6.1 Acceptance-risk register** (canonical; everything else references it):

| ID | Risk | Severity (CRITICAL/MAJOR/MODERATE/MINOR) | P(reviewer notices) (VH/H/M/L) | Consequence (reject / major rev / minor rev / clarification / editorial) | Required fix | Confidence |

**6.2 Experiment decision matrix.** For each candidate — matched
random-orthonormal basis; ISM-free variant; matched-NP CEC2013LSGO; D = 30
retune; D = 100 upper-tier retune; wider sensitivity; ARGP ablation;
deep-stall-restart ablation; cross-paradigm comparison; efficiency scaling —
classify: REQUIRED BEFORE RESUBMISSION / STRONGLY RECOMMENDED / USEFUL BUT
OPTIONAL / NOT NEEDED, each with a one-line justification **and an
approximate run cost**. Recommending an experiment is a claim that its
absence materially threatens acceptance — hold that bar. Do not recommend
experiments whose answer existing evidence already contains.

**6.3 Simulated reviews.** Four independent reports — A: algorithm/novelty;
B: experimental design/benchmarking; C: statistics/reproducibility; D:
maximally skeptical senior reviewer — each with assessment, strengths,
major concerns, minor concerns, recommendation
(Accept / Minor / Major / Reject). Then the overlap synthesis: which
concerns appear in ≥2 reviews (these are the real threats).

**6.4 Editor simulation.** As handling editor: decision + reasoning + the
exact, finite list of changes that would move the paper to ACCEPT.

**6.5 Prioritized plan.** P0 acceptance-critical → P1 major scientific →
P2 reviewer-proofing → P3 presentation → P4 optional. Every item: location;
problem; why a reviewer cares; exact change; evidence required; blast
radius; verification method. No generic advice ("improve clarity") — only
executable instructions.

**6.6 Final checklist.** Reviewer points closed; claims ≤ evidence;
statistics convention uniform; fairness disclosed (incl. LSGO); negative
findings integrated; terminology consistent; figures/tables sound;
provenance traceable; preregistration language precise; limitations
complete; conclusions bounded; no unsupported superiority language; no
family-to-global drift; no residual eigenframe-benefit language; no hidden
NP issue; no sensitivity overclaim. Mark each: PASS / FAIL(id) / NEEDS
VERIFICATION(where).

---

# 7. REQUIRED OUTPUT STRUCTURE

1. **Inputs received** (which documents; what was therefore checkable)
2. **Executive assessment** (≤1 page) + likely editorial decision
3. **Top 10 acceptance threats** (IDs into the risk register)
4. Reviewer-point closure matrix (§1)
5. Experiment audits E1–E5 (§2)
6. Contribution matrix C1–C3 (§3)
7. Cross-cutting audits (§4, only sections with surviving findings in
   full; others as "no surviving findings")
8. Change-by-change verdict list, all ~92 (§5) + new-problems section
9. Acceptance-risk register (§6.1)
10. Experiment decision matrix (§6.2)
11. Simulated reviewers A–D + overlap synthesis (§6.3)
12. Editor decision + path to ACCEPT (§6.4)
13. Prioritized implementation plan P0–P4 (§6.5)
14. Final checklist (§6.6)
15. **Refuted-findings appendix** — findings you raised and then refuted
    yourself, with the refutation (this calibrates the rest of the report)

---

# 8. QUALITY BAR AND CRITICAL RULES

- Document-specific, evidence-pinned, adversarial, exhaustive, actionable.
- Every finding: location + quote + label (`VERIFIED`/`INFERRED`/`NOT
  CHECKABLE`) + confidence + consequence + exact fix + blast radius.
- Never hide or soften unfavorable evidence to please a reviewer; the
  strategy is the opposite — the paper becomes hard to reject because every
  claim is accurately bounded, directly supported, statistically
  defensible, experimentally fair, and transparent.
- The goal in one line:

      maximum scientific defensibility
              +
      maximum reviewer confidence
              +
      minimum unresolved acceptance risk.
