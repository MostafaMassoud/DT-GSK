# PHASE 1 — Scope, Contributions, Outline & Budget Lock

> **Objective (one sentence).** Freeze the paper's scientific message, its 3–5
> evidence-backed contributions, its section outline with per-subsection page
> budgets and citation shortlists, and its target journal — so that not a single
> `.tex` token is drafted until the message and shape are locked.

This file **expands Phase 1** of `papers/PAPER_BUILD_PROMPT.md` (the master
prompt; Part 5 › "PHASE 1 — Scope, contributions, outline, budget lock", and
Part 3 §3.4 for the budget). It **follows `PHASE_0_audit.md`** (which delivers
the asset map, data ledger, and evidence-readiness note) and **hands to
`PHASE_2_data_stats.md`** (which turns located runs into the exact statistics
this phase promises the paper will report).

Nothing here executes code, computes a statistic, or edits a manuscript /
results file. Phase 1 produces three planning artifacts only:
`outline.md`, `claims.md`, `decisions.md`. Prose and numbers come later.

Method under construction: **DT-GSK** — an adaptive Interaction-Structure
Memory (SGSM) overlay for high-dimensional Gaining–Sharing Knowledge
optimization. Family panel (7 algorithms): `gsk`, `agsk`
(`mohamed2020agsk`), `apgsk` (`apgsk2021`), `fdb-agsk` (`fdbagsk2023`),
`atmals-gsk` (`alfadli2025atmals`), `egsk` (`jawad2024egsk`), and the proposed
**dt-gsk**.

---

## Prerequisites

Phase 1 may not begin until the **Phase 0 exit gate is green**. Confirm each
before proceeding; if any is red, return to Phase 0.

- [ ] **Asset map complete.** Every file in `papers/` classified keep /
  rewrite / regenerate; every `tables/T01..T22.tex` (+ `T16_bca.tex`) mapped to
  the result file it renders; every figure PDF in
  `figures/{convergence,diagrams,flowchart,ranks,taxonomy,traces}/` mapped to
  its generator script and source CSV(s).
- [ ] **Data ledger complete.** One row per reported cell-group with columns
  `optimizer, suite, dimension, n_runs, seed_policy, source_path, commit_sha,
  table_or_figure` (Appendix D.1 schema). Every panel cell for the 7-algorithm
  family × {CEC2017, CEC2011, CEC2013} × D is either **located** (path + SHA) or
  carries an explicit **regeneration ticket**. (The committed reference panel
  under `benchmarks/cec_reference_results/` already carries the full 7-panel for
  all three suites — expect *located* rows, not tickets.)
- [ ] **Gaps ticketed, not papered over.** Each missing cell has a decision:
  regenerate (via the existing `scripts/run_all_*.py` runners) or rescope the
  claim. No unexplained holes.
- [ ] **Reproducibility anchor recorded.** FP-regime sentinel confirmed in
  `environment.json`; profile lock passing; the single **commit SHA** that all
  "reproducible from" claims will cite is written down.
- [ ] **Citation set snapshotted.** The **57 admissible keys** (master prompt
  Appendix A) dumped and the bib confirmed to parse. Phase 1 cites nothing
  outside this set.

If Phase 0 left any cell as "assumed present but unverified," treat it as a gap
here: **a contribution cannot rest on a cell that is not in the ledger.**

---

## Inputs

Phase 1 consumes only planning artifacts, not raw data:

1. **The evidence-readiness note** (Phase 0 deliverable) — the one-page listing
   of what evidence exists, what is missing, and the plan per gap. This is the
   *ground truth* for what any contribution or claim may assert.
2. **The data ledger** (`data_ledger.csv` from Phase 0) — the per-cell
   provenance table. Every bullet, thesis number, and claim-row in Phase 1 must
   point at a ledger row (or its regeneration ticket).
3. **The master prompt** (`papers/PAPER_BUILD_PROMPT.md`) — the constitution
   (Part 2), the theme/budget analysis (Part 3), the per-section writing specs
   (Part 6), the citation-usage map (Part 8), and the 57-key set (Appendix A).

You do **not** re-open raw `results/**` CSVs in Phase 1. If a number you want
is not already summarized in the ledger, it is not yet admissible — flag it for
Phase 2, do not go compute it here.

---

## Tasks

Work the five sub-tasks in order. Each ends by writing to one of the three
artifacts (`outline.md`, `claims.md`, `decisions.md`). Adopt the **P1 (PI /
lead author)** hat throughout — P1 owns the thesis, the contribution list, and
scope-creep control (master prompt Part 1.2).

### 1.1 — Contribution list (3–5 bullets, each proven by evidence)

**Rule (hard).** No evidence → cut. A contribution bullet that cannot name the
exact ledger row(s) that prove it and the exact section that carries it is not a
contribution; it is a hope. Delete it or move it to future work.

**Micro-steps.**
1. Draft 5–7 *candidate* contributions from the method spine (master prompt
   §3.2): the SGSM interaction memory, the eigenframe polish, the self-adaptive
   scaffold (ACE / NLPSR / BSE / ARGP), and the family-controlled evaluation.
2. For each candidate, fill the template below. If the "Evidence" slot cannot be
   filled from the Phase-0 ledger, strike the candidate now.
3. Rank survivors by strength of evidence × novelty. Keep the **top 3–5**. More
   than five dilutes; fewer than three under-sells a genuine method.
4. Assign each survivor to **exactly one** carrying section (the section where
   its evidence is presented, not merely mentioned).
5. Sanity-check against the honesty clause (master prompt C7 / N4): a
   contribution phrased as a universal win ("outperforms all baselines on every
   function") will be cut by R1 on sight. Phrase every empirical claim with its
   **scope**.

**Decision criteria for keeping a bullet.**
- **Provable:** points at ≥1 ledger row (located, or ticketed-for-Phase-2).
- **Novel-within-scope:** distinguishable from the nearest prior art named in
  the citation map (SGSM vs `omidvar2014dg`; block crossover vs `guo2015eig`;
  eigenframe polish vs `hansen2001cmaes`).
- **Load-bearing:** removing it would not leave a duplicate of another bullet.
- **Honest:** carries its scope; no implied universality.

**Fill-in template (one per contribution).**
```
C#. <one-sentence claim, with scope>
    Kind:      [conceptual | algorithmic | empirical | reproducibility]
    Evidence:  <ledger row(s): optimizer × suite × D × table/figure id>
               <or: regeneration ticket #NN from Phase 0>
    Carried in: <exact section — §Method / §Results / §Setup ...>
    Nearest prior art & delta: <cite key> — <what we do differently>
    Risk if challenged: <one line; expanded in the claim table, task 1.5>
```

**Two–three worked example bullets (DT-GSK specific).** These are *shapes*;
final wording waits on Phase 2 numbers.

```
C1. SGSM — an interaction-structure memory learned "for free" from the
    algorithm's own acceptance history — turns structure-blind GSK into a
    structure-aware optimizer at negligible extra evaluation cost.
    Kind:      conceptual + algorithmic
    Evidence:  ablation panel (SGSM on/off) — ledger rows for dt-gsk vs
               dt-gsk[-sgsm], CEC2017, D∈{50,100}, ablation summary table.
    Carried in: §Proposed method (mechanism) + §Results (ablation delta)
    Nearest prior art & delta: omidvar2014dg — differential grouping spends a
               dedicated evaluation budget to detect linkage; SGSM spends none,
               reusing acceptance events already produced by the search.
    Risk if challenged: "is the support graph actually used, or decorative?"
                        -> ablation shows the marginal contribution.

C2. Within a controlled 7-member GSK family evaluated identically, DT-GSK
    attains the best mean Friedman rank overall and at D∈{10,50,100} on CEC2017,
    with D30 the single honest exception (2nd, behind eGSK).
    Kind:      empirical
    Evidence:  Friedman-rank rows per D, CEC2017 (51 runs, F2 excluded),
               summary tables T## + Nemenyi CD figure (figures/ranks/).
    Carried in: §Results (per-dimension summary + CD figure)
    Nearest prior art & delta: the five family variants (mohamed2020agsk,
               apgsk2021, fdbagsk2023, alfadli2025atmals, jawad2024egsk) —
               same suite, same runs, same seeds; the comparison isolates the
               overlay rather than confounding it with a different base.
    Risk if challenged: "same-family scope is convenient, not fair"
                        -> Setup justifies scope; the D30 loss is reported, not
                           hidden, which reads as candour not cherry-picking.

C3. An eigenframe final polish — a deterministic direct search on the learned
    interaction eigenbasis — converts SGSM's structural estimate into end-of-run
    accuracy without a covariance-adaptation budget.
    Kind:      algorithmic
    Evidence:  ablation (polish on/off) + convergence traces (figures/traces/,
               figures/convergence/) showing the endgame delta on rotated
               functions.
    Carried in: §Proposed method + §Results (ablation + one convergence case)
    Nearest prior art & delta: hansen2001cmaes — CMA-ES *adapts* a covariance
               online at cost; the polish *reuses* SGSM's eigenframe once, via
               a compass/direct search (kolda2003directsearch).
    Risk if challenged: "why not just run CMA-ES?" -> positioning + cost
                        argument in Method; scope is the GSK family.
```

A candid fourth candidate — **the self-adaptive scaffold** (ACE knowledge
control grounded in `auer2002finite` / `fialho2010adaptive`, NLPSR population
reduction lineage `tanabe2014improving`, BSE stagnation escape with Cauchy
rescue `yao1999evolutionary`, ARGP acceptance-gated pruning) — is a legitimate
C4 *only if* the ablation isolates its marginal contribution. The scaffold-ablation
tooling is implemented (`scripts/run_ablation.py`: remove-one over 6 mechanisms +
baseline = 7 cells, n = 25 by design, SGSM off in every cell; matrix via
`papers/scripts/generate_ablation_matrix.py`). If Phase 0 shows the cells are not
yet run, either ticket them for Phase 2 or fold the scaffold into the Method as
engineering context rather than a headline contribution.

Write the surviving 3–5 bullets to **`claims.md`** (top block) and mirror the
one-liners into `outline.md`'s Introduction stub.

### 1.2 — One-paragraph thesis (the abstract skeleton)

Write a single paragraph that is the abstract's load-bearing skeleton (the real
abstract is drafted last, in Phase 4, and must stay ≤250 words — master prompt
§6.1). It must move: **problem → gap → idea → single strongest quantified
result (with honest scope) → reproducibility.** One concrete number only; no
citations in the abstract itself.

**Template with slots.**
```
High-dimensional real-parameter optimization <PROBLEM: why hard — scaling,
non-separability, rotation>. Gaining–Sharing Knowledge (GSK) variants improve
the base method but share a <GAP: fixed, structure-blind operators — they do
not learn which variables interact>. We propose DT-GSK, which <IDEA: adds
SGSM, an interaction-structure memory learned for free from acceptance history,
feeding linkage-aware crossover and an eigenframe polish>. Across a controlled
seven-member GSK family evaluated identically on CEC2017 (<N> runs, D up to
100), DT-GSK <RESULT: single strongest quantified claim, e.g. best mean
Friedman rank overall and at D∈{10,50,100}>, with <SCOPE: the honest exception —
D30, where it places second>. <REPRO: all runs regenerate from a fixed seed
formula and a pinned commit; code and data are released>.
```

**Decision criteria for the "single strongest result" slot.**
- It must be one number/claim the ledger already supports (or Phase 2 will
  produce from a ticketed cell) — not an aspiration.
- Prefer a **rank-based** headline (Friedman) over a single function's gap: a
  rank summarizes the whole panel and resists cherry-picking objections.
- It must be stated with its scope in the *same sentence*. The D30 second-place
  result is an asset here — naming it is what makes the win credible (per the
  family-best memo: DT-GSK is #1 overall + D10/D50/D100, #2 at D30 behind eGSK;
  absolute D30 gains do not convert to rank gains, so do not over-promise D30).

Write the thesis paragraph to **`outline.md`** (top) and note the chosen
headline number as a claim row in `claims.md`.

### 1.3 — Lock the outline (5-section spine + experimental-setup section)

Lock to the existing spine already wired in `main.tex`
(`\input` order: introduction → literature_review → proposed_algorithm →
performance → conclusions) plus an explicit **experimental-setup** section.
Assign each subsection a page budget drawn **only** from master prompt §3.4, and
a citation shortlist drawn **only** from the 57 keys (Appendix A). Treat budgets
as *ceilings*; under-budget is fine, over-budget means content migrates to the
supplement (C3/C4), never illegible shrinking.

**Budget ceilings (MDPI Algorithms, single-column; from §3.4).**

| Section | Ceiling | Notes |
|---|---|---|
| Title + abstract + keywords | ≤250-word abstract | one structured paragraph |
| 1. Introduction | 1.5–2.0 pp | motivation, gap, contributions, roadmap |
| 2. Related work | 2.0–2.5 pp | taxonomy + GSK family + structure-aware EC |
| 3. Proposed method | 4.0–5.0 pp | notation, pseudocode, complexity |
| 4. Experimental setup | 1.0–1.5 pp | suites, D, runs, seeds, stats defined |
| 5. Results & discussion | 4.0–5.0 pp | summaries, Nemenyi, convergence, ablation, limits |
| 6. Conclusion | 0.75–1.0 pp | recap + honest future work |
| **Main total** | **≈16–22 pp** | excluding references |
| Supplement | unbounded | everything in C4 |

**Outline skeleton with per-section citation shortlists** (place holders `≈`
show intra-section page split; sum ≤ the ceiling above). Cite only from these
shortlists when drafting; a citation not on a section's shortlist needs P1
sign-off (master prompt Part 8).

```
§1 Introduction  (1.5–2.0 pp)
   1.1 Motivation: high-D real-parameter optimization      ≈0.4 pp
       shortlist: del2019bio, hussain2019metaheuristic, awad2016problem
   1.2 GSK & the knowledge-flow metaphor; its 4 limitations ≈0.5 pp
       (fixed params · no local search · no stagnation recovery · no linkage)
       shortlist: mohamed2020gaining, + the five family variants
                  (mohamed2020agsk, apgsk2021, fdbagsk2023,
                   alfadli2025atmals, jawad2024egsk)
   1.3 NFL-grounded thesis + numbered contributions          ≈0.5 pp
       shortlist: wolpert1997nfl
   1.4 Roadmap                                               ≈0.2 pp
       shortlist: (none)

§2 Related work  (2.0–2.5 pp)
   2.1 Metaheuristic taxonomy (positioning)                  ≈0.6 pp
       shortlist: del2019bio, hussain2019metaheuristic, storn1997differential,
                  chen2020cbo, kaveh2021pgo, arini2022gjojos, hu2022qcsca,
                  khalfi2023csm, tang2024fowfo, zhou2021iade
   2.2 The GSK family, grouped by theme                      ≈0.9 pp
       shortlist: mohamed2020agsk, apgsk2021, fdbagsk2023, alfadli2025atmals,
                  jawad2024egsk, hpe_agsk2025, epd_gsk2024, pogsk2023,
                  chalabi2023mogsk, ma2023mgskdpmo, apgsk_imode2024,
                  nabahat2024hybrid, nomer2021gskrl, zhong2021gskhho,
                  navaneetha2022gskde, liang2024gskwoa, jalali2021opposition,
                  mohamed2021novel
   2.3 Structure-aware EC + the L-SHADE frontier             ≈0.7 pp
       shortlist: omidvar2014dg, guo2015eig, hansen2001cmaes,
                  zhang2009jade, tanabe2013shade, tanabe2014improving,
                  mohamed2017lshadespacma, awad2017ensemble, brest2017single

§3 Proposed method  (4.0–5.0 pp)
   3.1 Notation + inherited GSK junior/senior operators      ≈0.6 pp
       shortlist: mohamed2020gaining
   3.2 Self-adaptive scaffold (ACE, NLPSR, BSE, ARGP)        ≈1.0 pp
       shortlist: auer2002finite, fialho2010adaptive, tanabe2014improving,
                  yao1999evolutionary
   3.3 SGSM interaction-structure memory (the named contribution) ≈1.2 pp
       shortlist: omidvar2014dg, jones1995fitness
   3.4 Linkage-aware block crossover                         ≈0.6 pp
       shortlist: guo2015eig
   3.5 Eigenframe polish + Nelder–Mead endgame               ≈0.7 pp
       shortlist: kolda2003directsearch, hansen2001cmaes,
                  nelder1965simplex, gao2012implementing
   3.6 Complexity: O(D^2) memory, O(D^3) once-per-run polish, cadence-thinning ≈0.4 pp
       shortlist: (none new)

§4 Experimental setup  (1.0–1.5 pp)
   4.1 Suites, dimensions, run counts, termination           ≈0.6 pp
       shortlist: awad2016problem, das2011cec2011, liang2013cec2013
   4.2 The 7-algorithm family panel + why same-family scope  ≈0.3 pp
       shortlist: mohamed2020gaining + the five variants
   4.3 Statistics protocol + seed/FP-regime note             ≈0.4 pp
       shortlist: friedman1937use, demsar2006statistical,
                  wilcoxon1945individual, holm1979simple,
                  benjamini1995controlling, vargha2000critique,
                  efron1993introduction

§5 Results & discussion  (4.0–5.0 pp)
   5.1 Per-dimension summary tables (win/tie/loss + Friedman) ≈1.2 pp
   5.2 Nemenyi CD figure + plain reading                      ≈0.7 pp
       shortlist: friedman1937use, demsar2006statistical
   5.3 Pairwise Wilcoxon (Holm) + A12 + BCa on headline gaps  ≈0.8 pp
       shortlist: wilcoxon1945individual, holm1979simple,
                  benjamini1995controlling, vargha2000critique,
                  efron1993introduction
   5.4 Convergence: 2–3 cases incl. one honest hard case      ≈0.7 pp
   5.5 Ablation: each mechanism's marginal contribution       ≈0.7 pp
       shortlist: omidvar2014dg, guo2015eig, kolda2003directsearch
   5.6 Limitations (low-D behaviour, misfire classes, memory) ≈0.4 pp
       shortlist: (none new)

§6 Conclusion  (0.75–1.0 pp)
   recap tied to evidence + honest future work
   shortlist: omidvar2014dg (large-scale decomposition),
              hansen2001cmaes (covariance-aware refinement)

Supplement (unbounded): full per-function tables all D; full pairwise Wilcoxon
   matrices; all convergence curves; hyperparameter sweeps; FP-regime /
   reproducibility appendix; extended ablations; proof sketch
   (david_order_statistics if an order-statistics argument is used).
```

**Micro-steps.**
1. Copy the skeleton into `outline.md`; adjust intra-section page splits so each
   section sums ≤ its ceiling and the main total lands ≈16–22 pp.
2. For every subsection, confirm each shortlisted key exists in the 57-set and
   is used in its **sanctioned role** (master prompt Part 8). Delete any key you
   cannot justify in that role.
3. Cross-check: every surviving contribution (task 1.1) maps to at least one
   subsection here, and every heavy exhibit (summary tables, CD figure,
   convergence, ablation) has a home subsection.
4. Note per-section which Phase-0 ledger rows / Phase-2 tickets feed it, so
   Phase 4 drafting can bind numbers without re-deriving provenance.

### 1.4 — Target-journal decision

**Default: MDPI *Algorithms*** — the `algorithms` class is already wired into
`main.tex` and it is a legitimate Q1/Q2 venue for this topic. No hard page cap;
we self-impose the §3.4 budget above.

**Fallback: IEEE TEC** — hard **14 double-column pages** for a regular paper;
over-length penalized. Choosing it tightens the budget and migrates all full
per-function tables, all but one CD figure, and the reproducibility appendix to
the supplement.

**Decision procedure.**
1. Default to MDPI *Algorithms* unless a concrete reason to retarget exists.
2. Reasons that make it *genuinely ambiguous* (and only these): the PI has
   signalled a prestige/impact-factor requirement TEC meets and Algorithms does
   not; a co-author/institution mandate; a target special issue at either venue;
   an explicit page-count constraint that changes the split.
3. **Ask the human at most ONCE**, and only if genuinely ambiguous — the choice
   changes budget + template, so it is P1's to confirm (master prompt 0.7, 1.4).
   Phrase it as a single closed question: *"Default target is MDPI Algorithms
   (class already wired, ≈16–22 pp). Switch to IEEE TEC (hard 14 double-column
   pp, more to supplement)? Y/N."* Do not ask about mechanical matters.
4. If no ambiguity, do **not** ask — record the default and move on.

Record the decision, its date, and its one-line rationale in **`decisions.md`**
(see schema in Worked examples). This log also captures the P1 contribution
sign-off (task 1.1 gate) and the target confirmation.

### 1.5 — Claim table (claim → evidence → risk → mitigation)

Enumerate **every** claim the paper will make — not only the headline
contributions, but every empirical assertion, positioning claim, and
reproducibility statement. For each, record the evidence, the likely **R1
objection** (the adversarial Q1 reviewer; master prompt Part 1.2 / Part 9), and
the mitigation already planned. A claim with no mitigation for a plausible R1
objection is a claim to soften or cut *now*, before drafting.

**Table schema (write to `claims.md`).**
```
| ID | Claim (with scope) | Evidence (ledger row / ticket / figure id) |
     R1 objection (risk) | Mitigation | Carried in |
```

**Three worked rows.**
```
| CL1 | DT-GSK attains best mean Friedman rank overall and at D{10,50,100}
        on CEC2017; 2nd at D30. | Friedman-rank rows per D, summary tables T##
        + CD figure (figures/ranks/), 51 runs, F2 excluded.
      | "Ranks can flip under a different post-hoc / tie-handling." 
      | Report Nemenyi CD *and* pairwise Wilcoxon(Holm); state N and tie rule;
        show the D30 loss openly. | §5.1–5.3 |

| CL2 | SGSM is learned for free (no dedicated evaluation budget), unlike
        differential grouping. | Complexity analysis §3.6 + evaluation-count
        accounting; ablation shows contribution without extra FES.
      | "For-free is a design claim; where is the accounting?" (cf omidvar2014dg)
      | Give explicit FES accounting in Method; ablation isolates SGSM's delta
        at equal budget. | §3.3, §3.6, §5.5 |

| CL3 | All headline numbers regenerate from a fixed seed formula and one commit.
      | Seed policy get_cec_seed(20240620, dim, func, run); FP-regime sentinel
        in environment.json; pinned commit SHA (Phase 0). 
      | "Reproducibility asserted but not demonstrated." 
      | Reproducibility appendix (supplement) with formula, sentinel, commit,
        and per-exhibit regeneration script names. | §4.3 + supplement |
```

**Micro-steps.**
1. Seed the table from the contribution bullets (1.1) and the thesis (1.2), then
   sweep the outline (1.3) for every additional claim each section will make.
2. Rate each risk (H/M/L). Any **H** with no concrete mitigation is escalated to
   P1: soften the claim's scope, add a planned exhibit, or cut it.
3. Ensure every claim's evidence is a real ledger row or a Phase-0 ticket —
   never "to be found later without a ticket."
4. Confirm mitigations reference exhibits/sections that exist in the outline; if
   a mitigation needs a table/figure not yet planned, add it to the outline
   (respecting budget) or downgrade the claim.

---

## Worked examples

**A filled contribution bullet with its evidence pointer.**
```
C1. SGSM turns structure-blind GSK into a structure-aware optimizer using an
    interaction memory learned for free from acceptance history — at negligible
    extra evaluation cost.
    Kind:      conceptual + algorithmic
    Evidence:  ledger rows dt-gsk vs dt-gsk[-sgsm], CEC2017 D{50,100},
                ablation summary table (Phase-0 map -> tables/T## ; if the
                on/off cells are not yet present, Phase-0 ticket #07).
    Carried in: §3.3 (mechanism) and §5.5 (marginal contribution)
    Nearest prior art & delta: omidvar2014dg — spends a detection budget; SGSM
                spends none (reuses acceptance events).
    Risk if challenged: "decorative graph" -> ablation delta (see CL under 1.5).
```

**A claim-table row.**
```
| CL7 | The eigenframe polish improves end-of-run accuracy on rotated functions
        without a covariance-adaptation budget. | Ablation polish on/off +
        convergence trace (figures/traces/, figures/convergence/) on a rotated
        F-case. | "Why not CMA-ES?" (hansen2001cmaes) | Method gives the
        cost argument (one O(D^3) polish vs online adaptation); scope is the
        GSK family; convergence case shown honestly. | §3.5, §5.4–5.5 |
```

**An outline fragment with budgets.**
```
§5 Results & discussion  (ceiling 4.0–5.0 pp)
   5.1 Per-dimension summary tables (win/tie/loss + Friedman rank row)  ≈1.2 pp
       exhibits: summary table per D {10,30,50,100}; source = Phase-2 stats bundle
   5.2 Nemenyi CD figure + one-paragraph plain reading                  ≈0.7 pp
       shortlist: friedman1937use, demsar2006statistical ; fig = figures/ranks/
   5.6 Limitations (low-D behaviour incl. D30 2nd place; misfire classes;
       O(D^2) memory at very high D)                                    ≈0.4 pp
```

---

## Pitfalls & anti-patterns

- **Scope creep.** Adding a sixth "nice" contribution, a second suite as a
  co-headline, or a new mechanism to explain. Phase 1 *narrows*. If it is not on
  the frozen contribution list, it is context or future work.
- **Contribution bullets without evidence.** The single most common failure. A
  bullet whose "Evidence" slot is empty or hand-wavy ("shown to be effective")
  must be cut or ticketed. No ledger row, no bullet.
- **Promising what the data cannot deliver.** Do not let the thesis or abstract
  claim a D30 win, a universal sweep, or a cross-suite dominance the ledger does
  not support. DT-GSK is #1 overall and at D{10,50,100} but **2nd at D30** — the
  honest scope is the credible scope. Over-promising here poisons every later
  phase and hands R1 an easy rejection.
- **Citing outside the 57.** Any key not in Appendix A is inadmissible. If a
  subsection "needs" an outside citation, rewrite the sentence to rest on an
  admissible key or move the claim to future work — never import a reference.
- **Citing a key outside its sanctioned role.** Even an admissible key used for
  the wrong purpose (decorative citing) fails C1. Match Part 8's role map.
- **Budget denial.** Writing an outline whose sections sum past ≈22 pp and
  planning to "trim later." Fix the budget now; over-budget content is a
  supplement-migration decision, not a shrink-the-figures decision.
- **Deferring the journal decision indefinitely, or asking more than once.**
  Default to MDPI Algorithms; ask the human exactly once and only if genuinely
  ambiguous; then record it and stop revisiting.

---

## Exit gate

Phase 1 is complete only when **all** hold, each with evidence in the artifacts:

- [ ] **PI (P1) has signed the contribution list** — sign-off line recorded in
  `decisions.md` with date.
- [ ] **Every contribution maps to evidence** — each bullet in `claims.md`
  names ≥1 located ledger row or a Phase-0 regeneration ticket; zero
  evidence-free bullets remain.
- [ ] **Outline fits the budget** — sections in `outline.md` sum to ≈16–22 pp
  (or ≤14 double-column pp if IEEE TEC was chosen); every subsection has a page
  ceiling and a citation shortlist drawn only from the 57.
- [ ] **Every claim has evidence + risk + mitigation** — `claims.md` table
  complete; no High-risk claim without a concrete mitigation or a scope
  reduction.
- [ ] **Target journal chosen and recorded** — `decisions.md` states the venue,
  date, and one-line rationale (and, if the human was asked, their answer).
- [ ] **Citation lockdown holds** — no key outside Appendix A appears in any
  shortlist; each shortlisted key is in its sanctioned role.

**Evidence artifacts produced by this phase:**
- `outline.md` — the locked spine with per-subsection page budgets, citation
  shortlists, and the thesis paragraph.
- `claims.md` — the contribution list plus the full claim → evidence → risk →
  mitigation table.
- `decisions.md` — the journal decision, the PI contribution sign-off, and any
  single human question asked (with the answer).

---

## Hand-off

Phase 1 hands to **`PHASE_2_data_stats.md`** (master prompt Part 5 › "PHASE 2 —
Data consolidation & statistical computation"). Phase 2 consumes:

- the **claim table** — every headline number and effect-size claim it lists
  becomes a statistic Phase 2 must produce from committed data (Friedman ranks
  per D; Nemenyi CD; pairwise Wilcoxon with Holm / BH; A12; BCa CIs; ablation
  deltas);
- the **Phase-0 regeneration tickets** referenced by contributions/claims —
  Phase 2 regenerates those panel cells first (honouring run counts: CEC2017 51
  runs, CEC2011 25 runs, CEC2013 51 runs; the seed formula; the FP regime);
- the **outline's exhibit list** — Phase 2's source-of-truth CSV per table must
  cover exactly the exhibits the outline plans, no more.

Phase 2's exit gate (every statistic reproducible from committed data with one
command; no orphan numbers) is what makes the Phase-1 claims *true* rather than
merely *promised*. Do not begin Phase 2 until this phase's exit gate is green.
