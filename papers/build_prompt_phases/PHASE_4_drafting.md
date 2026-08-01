# PHASE 4 — Section Drafting

> **⚑ Revision 2 addendum applies to this phase.** Before executing, read [ADDENDUM_R2_cec2013_and_ablation.md](ADDENDUM_R2_cec2013_and_ablation.md) §R2.C — a CEC2013 family panel and the CEC2017 scaffold ablation add tasks to this phase, and the addendum overrides this file where they disagree.

**Objective.** Draft the DT-GSK main text one section at a time — Method first, Abstract last — so that every sentence is bound to a Phase-2 number, cites only the 57 locked keys, references a Phase-3 exhibit that already exists, and survives its R1 (Q1) and R2 (Q2) self-review before the next section starts.

> This file expands **Phase 4** and **Part 6** of `papers/PAPER_BUILD_PROMPT.md` into an executable drafting procedure. It **follows** `PHASE_3_tables_figures.md` (exhibits must be final and legible before prose points at them) and **hands to** `PHASE_5_supplementary.md` (everything you mark as overflow here becomes Phase-5 supplement material). It does **not** touch the supplement, the prose-quality pass (Phase 6), or adversarial review (Phase 7) — those are later phases. Draft in the target voice, but leave the style polish to Phase 6.

---

## Prerequisites

Do not open a `.tex` section file until all three are true. If any is not, stop and return to the owning phase.

1. **Phase 3 exhibits are final.** Every table (`papers/tables/T01.tex … T22.tex`, plus `T16_bca.tex`) and every figure (`papers/figures/{ranks,convergence,flowchart,taxonomy,traces,diagrams}/`) is built, legible at print size, self-contained in its caption, and bound to a Phase-2 CSV. You are drafting *around* frozen exhibits — you never invent a number to fit a sentence, and you never hand-edit an exhibit to fit prose. If drafting reveals an exhibit is wrong, file it back to Phase 3; do not patch it here.
2. **Phase 1 outline and claims are locked.** `outline.md` fixes the five-section spine plus setup with a per-subsection page budget and a per-subsection citation shortlist drawn from Appendix A only. `claims.md` maps every claim → evidence → R1 risk → mitigation. You draft the claims that are in `claims.md` and no others. A sentence that asserts something not in `claims.md` is a defect, not a flourish.
3. **Phase 2 numbers are bound and reproducible.** The `stats/` bundle and the table-to-CSV binding map exist; every Friedman rank, Nemenyi CD, Wilcoxon/Holm verdict, A12, and BCa interval the prose will state is already computed and traceable to committed data with one command. Phase 4 *reports* these numbers; it never *computes* a new one. If a number you want does not exist in Phase 2, you may not state it — either drop the claim or send a computation ticket back to Phase 2.

Also confirm the mechanical substrate exists: `papers/main.tex` (MDPI `algorithms` class) `\input`s `sections/{introduction,literature_review,proposed_algorithm,performance,conclusions}.tex` **in that order**; the macros `\ismgsk`, `\sgsm`, and the family-name macros resolve; `references.bib` parses to exactly **57** keys.

---

## Drafting order & rationale

Draft in this order — it is deliberate and it is not the reading order:

**Proposed method → Experimental setup → Results & discussion → Related work → Introduction → Conclusion → Abstract.**

Why this order, concretely:

- **Method first** because it is the ground truth of what the paper *is*. Every downstream section makes promises about the method; writing it first means the promises are constrained by what the mechanism actually does, not by an aspirational framing. The method text also fixes the notation that Setup and Results reuse.
- **Setup second** because it is short, checklist-shaped, and it pins the evaluation protocol (suites, D, runs, seeds, MaxFES, stats definitions) that the Results section will lean on. Writing it now means Results can cite protocol choices instead of re-explaining them.
- **Results third** because it is the empirical core. Once Method + Setup are fixed, Results is a disciplined walk through frozen exhibits. Crucially, writing Results *before* the framing sections means the Introduction and Abstract can promise **exactly** what the evidence delivers — no more, no less. This is the single most important reason for the order: framing written after evidence cannot overclaim.
- **Related work fourth** because its positioning sentences ("we do X differently from differential grouping / eigenvector crossover / CMA-ES") must match the Method text word-for-word in substance. Writing it after Method avoids a related-work claim the method cannot back.
- **Introduction fifth** because a good introduction is a contract for the rest of the paper; you can only write an honest contract once you know what you delivered. The contributions list here is copied from `claims.md` and cross-checked against the finished Method and Results.
- **Conclusion sixth** because it restates what was *shown* (Results) and what the method *is* (Method) — both now exist.
- **Abstract last** because it is the tightest compression of the whole paper (≤250 words) and can only be written truthfully once the strongest quantified result is on the page.

Within each section, run the per-section **Drafting loop** (below). Do not start section *n+1* until section *n* has passed its exit checklist — a half-reviewed section poisons the sections that depend on it.

---

## Per-section specs

Each section below gives **Goal · Must-include · Must-avoid · Length · Citation shortlist · Exhibits · Voice**, then a **Drafting loop** (draft → bind → self-review vs R1/R2 → mark overflow). The citation shortlists are subsets of the 57 (Appendix A of `papers/PAPER_BUILD_PROMPT.md`, sanctioned roles in its Part 8). **You may cite only keys on the section's shortlist without a documented reason; you may never cite a key outside the 57.**

The seven sections are drafted in the order of the previous section; they are presented here in the same order.

---

### 4.1 Proposed method  → `sections/proposed_algorithm.tex`

**Goal.** Let a competent EC researcher reimplement the DT-GSK core from this section alone. Define notation once and use it consistently. Present each mechanism in the fixed shape **problem it solves → mechanism → cost**. Nothing appears that does not earn its place.

**Must-include (all of these; each is a claim in `claims.md`):**
- **Inherited GSK spine.** The junior and senior knowledge-acquisition phases of GSK (`mohamed2020gaining`), stated precisely enough that the reader sees DT-GSK as an *overlay* on GSK, not a replacement. Define the junior/senior partition and the dimension-wise knowledge update once.
- **Self-adaptive scaffold**, four mechanisms, each in the problem→mechanism→cost shape:
  - **ACE** (adaptive knowledge control): the parameter-control substrate, grounded as a bandit-style credit-assignment scheme over knowledge settings (`auer2002finite`, `fialho2010adaptive`). State the reward signal (acceptance-derived) and the selection rule.
  - **NLPSR** (non-linear population-size reduction): the population schedule; name the L-SHADE lineage it descends from (`tanabe2014improving`) and the non-linear reduction it applies.
  - **BSE** (stagnation escape): the stagnation trigger and the **Cauchy-rescue** perturbation, grounded in Cauchy mutation for heavy-tailed escape (`yao1999evolutionary`). State the detection condition and what is perturbed.
  - **ARGP** (acceptance-gated pool pruning): how the interaction pool is pruned using acceptance history; state the gate.
- **SGSM — the paper's central contribution.** Define the pairwise **support graph** as a matrix (or symmetric edge set) over the $D$ variables. Give the **EMA update rule** explicitly (the running estimate of pairwise support, updated from acceptance events) *and* the **confidence gate** (the threshold/condition an edge must clear before it is trusted for structure use). Then the load-bearing contrast: SGSM is **learned for free** from the acceptance history the optimizer already produces — it costs no extra function evaluations — in explicit contrast to **differential grouping** (`omidvar2014dg`), which spends dedicated evaluations to detect variable interaction. State this as a design trade-off, not a superiority claim.
- **Linkage-aware block crossover.** How SGSM's graph induces variable blocks that structure crossover, contrasted with **eigenvector crossover** (`guo2015eig`): we exploit a *learned support graph*, they rotate into an eigenbasis of an estimated covariance. One pointed sentence of difference.
- **Eigenframe final polish.** A deterministic **compass / direct search** (`kolda2003directsearch`) performed on the **interaction eigenbasis** derived from SGSM — contrasted with the **covariance-adaptation** idea of CMA-ES (`hansen2001cmaes`): we build the frame from the learned interaction structure and search it deterministically, rather than adapting a covariance matrix stochastically.
- **Nelder–Mead endgame** (`nelder1965simplex`, `gao2012implementing`): the simplex refinement invoked in the terminal budget, with its trigger.
- **Pseudocode** (algorithm2e), one main algorithm with the mechanisms as labelled steps; sub-procedures may be referenced and their full listings routed to the supplement.
- **Complexity.** Per-mechanism cost, then the two headline figures: **$O(D^2)$ memory** for the support graph, and the **$O(D^3)$ once-per-run** eigenframe polish. State the **high-D cadence thinning** that bounds the $O(D^3)$ term — the polish/eigendecomposition runs on a thinned schedule at high $D$ so its cost is amortized and does not dominate the run. This is the answer to the obvious R1 objection ("$O(D^3)$ does not scale"); make it explicit.

**Must-avoid.** Undefined symbols (define before use, every time). Mechanisms stated without the problem they solve. Implementation trivia (data-structure choices, exact constants that are not conceptually load-bearing) — route to the supplement. Claiming SGSM beats differential grouping on interaction *detection accuracy* — the claim is *cheapness and sufficiency for our use*, not detection superiority.

**Length.** 4.0–5.0 pp (the largest section). If over, thin pseudocode detail and per-mechanism derivations into the supplement, never the definitions.

**Citation shortlist (from the 57 only):** `mohamed2020gaining`, `auer2002finite`, `fialho2010adaptive`, `tanabe2014improving`, `yao1999evolutionary`, `omidvar2014dg`, `guo2015eig`, `kolda2003directsearch`, `hansen2001cmaes`, `nelder1965simplex`, `gao2012implementing`. (Optionally `tanabe2013shade`, `zhang2009jade`, `storn1997differential` if the DE/archive lineage is invoked — check `claims.md`.)

**Exhibits to reference.** The architecture flowchart (`papers/figures/flowchart/`) at the section opener; the diagram plots (`papers/figures/diagrams/`) where the SGSM graph or eigenframe is illustrated; the ablation summary table (Phase-3 main table) may be *forward-referenced* here ("we quantify each mechanism's contribution in Section 5, Table~\ref{...}"), but the numbers live in Results.

**Voice.** Precise, notation-disciplined, unhurried. Each subsection earns its place; each mechanism reads as a solution to a named problem.

#### Drafting loop — Proposed method
1. **Draft.** Open `sections/proposed_algorithm.tex`. Write the notation block first, then the inherited-GSK subsection, then scaffold (ACE, NLPSR, BSE, ARGP), then SGSM, then block crossover, then eigenframe polish, then Nelder–Mead, then complexity. Insert the pseudocode after SGSM is defined.
2. **Bind numbers & references.** There are few empirical numbers here (complexity orders are analytic, not from Phase 2). Bind every `\cite` to the shortlist; every `\ref` to a real `\label` on a Phase-3 flowchart/diagram or a forward `\ref` to a Results table/algorithm that exists. Confirm every symbol used is defined above its first use.
3. **Self-review vs R1 (Q1).** Novelty: is SGSM *clearly delimited* from differential grouping / eigenvector crossover / CMA-ES, with an explicit differ-sentence for each? Reproducibility: could a reader reimplement from this text? Honesty: is the $O(D^3)$ cost stated and bounded rather than hidden?
4. **Self-review vs R2 (Q2).** Clarity: any undefined symbol? Can a non-specialist follow the problem→mechanism→cost arc? Formatting: does the pseudocode compile and stay on-page?
5. **Mark overflow.** Tag full sub-procedure listings, extended derivations, and constant tables with a `% TODO(supplement): …` comment and log them in the running overflow list for Phase 5. Do not exceed 5.0 pp.

---

### 4.2 Experimental setup  → `sections/performance.tex` (setup portion)

**Goal.** Make the entire evaluation reproducible from the paper alone. This section is a checklist rendered as prose.

**Must-include.**
- **Suites.** CEC2017 as the **primary** suite (defs `awad2016problem`; **F2 excluded** per convention; **51 runs**; $D \in \{10,30,50,100\}$); CEC2011 as the **real-world** suite (defs `das2011cec2011`; **25 runs**); CEC2013 as the **second comparison suite** (defs `liang2013cec2013`; 28 functions; **51 runs**; $D \in \{10,30,50\}$ — no longer an dt-gsk-only hold-out, though the SGSM-overlay *ablation* keeps its CEC2013 hold-out design). State run counts and dimensions explicitly per suite.
- **Seed policy.** The seed formula exactly as frozen: `get_cec_seed(20240620, dim, func, run) % 2147483646 + 1`.
- **Termination.** MaxFES convention per suite.
- **The 7-algorithm family panel** and the *same-family scope justification*: gsk (`mohamed2020gaining`), agsk (`mohamed2020agsk`), apgsk (`apgsk2021`), fdb-agsk (`fdbagsk2023`), atmals-gsk (`alfadli2025atmals`), egsk (`jawad2024egsk`), and dt-gsk (proposed). State *why* the comparison is within-family (controlled ablation of the GSK design axis) rather than against the broad L-SHADE frontier — and cite that frontier as the competitive context we do **not** claim to beat here (`tanabe2013shade`, `tanabe2014improving`, `awad2017ensemble`, `brest2017single`, `mohamed2017lshadespacma`).
- **Statistics protocol**, fully specified with citations: Friedman ranks (`friedman1937use`, `demsar2006statistical`); Nemenyi CD post-hoc; pairwise Wilcoxon signed-rank (`wilcoxon1945individual`) with Holm correction (`holm1979simple`) and Benjamini–Hochberg where FDR framing is used (`benjamini1995controlling`); Vargha–Delaney A12 effect size (`vargha2000critique`); BCa bootstrap CIs (`efron1993introduction`).
- **Hardware / FP-regime note** and the commit SHA that anchors reproducibility (point to the reproducibility appendix in the supplement for full detail).

**Must-avoid.** Burying any protocol choice that affects fairness (e.g. a per-algorithm budget difference) in a footnote. NFL over-invocation here — that belongs in the intro.

**Length.** 1.0–1.5 pp.

**Citation shortlist:** `awad2016problem`, `das2011cec2011`, `liang2013cec2013`, `mohamed2020gaining`, `mohamed2020agsk`, `apgsk2021`, `fdbagsk2023`, `alfadli2025atmals`, `jawad2024egsk`, `tanabe2013shade`, `tanabe2014improving`, `awad2017ensemble`, `brest2017single`, `mohamed2017lshadespacma`, `friedman1937use`, `demsar2006statistical`, `wilcoxon1945individual`, `holm1979simple`, `benjamini1995controlling`, `vargha2000critique`, `efron1993introduction`.

**Exhibits.** No new exhibits usually; a small panel/config table (a Phase-3 setup table) may summarize suites × D × runs. Reference it if it exists.

**Voice.** Checklist-clear, terse, unambiguous.

#### Drafting loop — Experimental setup
1. **Draft** the suites → dimensions → runs → seed → termination → panel → scope-justification → statistics → hardware order.
2. **Bind.** Every number (51, 25, D-set, MaxFES, seed formula) is copied *verbatim* from the frozen config, not paraphrased. Every citation from the shortlist.
3. **R1 review.** Baselines: is same-family scope *justified* rather than merely convenient? Reproducibility: seeds, runs, FP regime, commit all present?
4. **R2 review.** Completeness: is the protocol fully specified? Any fairness choice hidden?
5. **Mark overflow.** Full seed tables, full environment dump, and per-suite MaxFES tables → supplement (Phase 5). Keep to 1.5 pp.

---

### 4.3 Results & discussion  → `sections/performance.tex` (results portion)

**Goal.** Present the headline evidence, then interpret it — with measurement and interpretation visibly separated. This is where the paper earns acceptance or gets rejected on rigor.

**Must-include.**
- **Per-dimension summary** across the 7-algorithm family: mean±std or median/IQR with **win/tie/loss** vs each baseline and a **Friedman rank** row, per $D \in \{10,30,50,100\}$ on CEC2017, plus the CEC2011 real-world summary. (Main tables from Phase 3; full per-function results → supplement.)
- **Nemenyi CD figure with a plain-language reading.** Show the CD diagram (`papers/figures/ranks/`) and then say, in words, which methods are statistically indistinguishable and where DT-GSK's rank sits — including the honest reading that the lead is clearest at high $D$ and narrower (or absent) at low $D$.
- **Pairwise Wilcoxon (Holm) verdicts.** State the signed-rank outcome vs each baseline with Holm-corrected significance; do not call anything "significant" without pointing at the test.
- **A12 + BCa on the headline gaps.** For the strongest claims, give the Vargha–Delaney A12 effect size and the BCa bootstrap CI (from `T16_bca.tex` / the BCa bundle). Effect size and CI travel *with* the p-value, never instead of it.
- **2–3 convergence figures including an honest hard case.** Use `papers/figures/convergence/`: at least one clear DT-GSK win and at least one **hard case** where DT-GSK does not lead (or converges slower early) — captioned honestly. Do not show only wins.
- **The key ablation.** Each mechanism on/off, its marginal contribution to the headline metric, from the committed scaffold-ablation matrix (Phase-3 ablation table: remove-one over 6 mechanisms + baseline = 7 cells, n = 25, SGSM off in every cell; the SGSM overlay is ablated separately on the CEC2013 hold-out design). State which mechanisms carry the high-D gain and whether any is marginal.
- **A candid limitations paragraph.** Explicitly: the **low-D behaviour** (the structure-exploitation machinery is gated to high-D and does not help — and can be neutral-to-slightly-worse — at low $D$; this is structural, not a tuning miss); function classes where structure exploitation misfires; the memory cost at very high $D$. This paragraph is required by C7 and is a positive signal to R1, not a weakness to hide.

**Must-avoid.** Cherry-picking functions or dimensions. Significance language with no test behind it. Hiding regressions or losses. A "suspiciously clean sweep" — if it looks too clean, R1 distrusts everything.

**Length.** 4.0–5.0 pp.

**Citation shortlist:** `friedman1937use`, `demsar2006statistical`, `wilcoxon1945individual`, `holm1979simple`, `benjamini1995controlling`, `vargha2000critique`, `efron1993introduction`; family keys as needed for comparison prose (`mohamed2020gaining`, `mohamed2020agsk`, `apgsk2021`, `fdbagsk2023`, `alfadli2025atmals`, `jawad2024egsk`); `omidvar2014dg` if the limitations paragraph points to large-scale decomposition as the escape hatch.

**Exhibits.** Per-D summary tables (main); ablation table (main); parameter-study table (main); Nemenyi CD (`figures/ranks/`); convergence curves (`figures/convergence/`); optional trace/diagnostic plots (`figures/traces/`). Every exhibit referenced exactly where it is discussed.

**Voice.** Evidence-led. Report the number, then interpret it in a separate sentence. Interpretation never smuggles in a number the exhibit does not show.

#### Drafting loop — Results & discussion
1. **Draft** in the order: per-D summary → Friedman/Nemenyi reading → Wilcoxon/Holm verdicts → A12+BCa on headline gaps → convergence (win + hard case) → ablation → limitations.
2. **Bind.** Every stated number traces to a Phase-2 CSV via the binding map; every table/figure has a resolving `\ref`; every stat has its `\cite`. No orphan numbers — if a sentence has a number, the number is in an exhibit or the stats bundle.
3. **R1 review.** Statistics correct and corrected? Effect sizes + CIs on headline gaps? Ablation shows each mechanism earns its place? Losses/limitations reported? No unexplained clean sweep?
4. **R2 review.** Is every exhibit referenced where discussed? Are figures legible and captions self-contained? Is interpretation separated from measurement?
5. **Mark overflow.** Full per-function tables, full pairwise Wilcoxon matrices, full convergence sets, full sweep grids → supplement (Phase 5). Keep main results to 5.0 pp.

---

### 4.4 Related work  → `sections/literature_review.tex`

**Goal.** Locate DT-GSK in three coordinates: (a) the metaheuristic taxonomy, (b) the GSK family, (c) structure-aware EC. Comparative and pointed, not a catalogue.

**Must-include.**
- **The taxonomy figure** (`papers/figures/taxonomy/`) and a short placement of GSK-style knowledge algorithms within the broader field (`del2019bio`, `hussain2019metaheuristic`).
- **GSK-family survey grouped by theme** — population-enhancement, hybrids, strategy-enhancement — citing each variant once where its mechanism is discussed: the panel baselines (`mohamed2020agsk`, `apgsk2021`, `fdbagsk2023`, `alfadli2025atmals`, `jawad2024egsk`) plus the related-work-only variants (`hpe_agsk2025`, `epd_gsk2024`, `pogsk2023`, `chalabi2023mogsk`, `ma2023mgskdpmo`, `apgsk_imode2024`, `nabahat2024hybrid`, `nomer2021gskrl`, `zhong2021gskhho`, `navaneetha2022gskde`, `liang2024gskwoa`, `jalali2021opposition`, `mohamed2021novel`), anchored on the origin `mohamed2020gaining`.
- **Structure-aware EC positioning with an explicit *what-we-do-differently* sentence for each:** differential grouping (`omidvar2014dg`), eigenvector crossover (`guo2015eig`), CMA-ES (`hansen2001cmaes`). These sentences must match the Method contrasts verbatim in substance.
- **The L-SHADE competitive frontier** as the strong-solver context: `tanabe2013shade`, `tanabe2014improving`, `awad2017ensemble`, `brest2017single`, `mohamed2017lshadespacma` (and DE/adaptive-DE lineage `storn1997differential`, `zhang2009jade` if invoked).

**Must-avoid.** Annotated-bibliography tone ("X did A. Y did B. Z did C."). Citing outside Appendix A. Repeating the intro's motivation.

**Length.** 2.0–2.5 pp.

**Citation shortlist:** `mohamed2020gaining`, `mohamed2020agsk`, `apgsk2021`, `fdbagsk2023`, `alfadli2025atmals`, `jawad2024egsk`, the 13 related-only GSK variants above, `omidvar2014dg`, `guo2015eig`, `hansen2001cmaes`, `tanabe2013shade`, `tanabe2014improving`, `awad2017ensemble`, `brest2017single`, `mohamed2017lshadespacma`, `storn1997differential`, `zhang2009jade`, `del2019bio`, `hussain2019metaheuristic`; optional breadth keys (`chen2020cbo`, `kaveh2021pgo`, `arini2022gjojos`, `hu2022qcsca`, `khalfi2023csm`, `tang2024fowfo`, `zhou2021iade`, `jones1995fitness`) for taxonomy placement.

**Exhibits.** Taxonomy figure (`figures/taxonomy/`); optionally the flowchart forward-reference.

**Voice.** Comparative and pointed. Group by theme, argue placement, do not enumerate.

#### Drafting loop — Related work
1. **Draft** taxonomy placement → GSK-family-by-theme → structure-aware positioning (with the three differ-sentences) → L-SHADE frontier context.
2. **Bind.** Each variant cited once where discussed; the three differ-sentences cross-checked against the Method text; taxonomy figure `\ref` resolves.
3. **R1 review.** Is SGSM's delimitation from DG/eigenvector/CMA-ES consistent with the Method claims? Is the same-family scope motivated here too?
4. **R2 review.** Any annotated-bibliography passages? Any citation outside the 57? Within 2.5 pp?
5. **Mark overflow.** Extended family tables or a full variant-comparison matrix → supplement.

---

### 4.5 Introduction  → `sections/introduction.tex`

**Goal.** Motivate high-D real-parameter optimization; introduce GSK and its knowledge-flow metaphor; state the *specific* limitation DT-GSK removes; give the NFL-grounded rationale; list contributions; give a roadmap. A contract for the paper.

**Must-include.**
- Motivation for high-dimensional real-parameter optimization and GSK's knowledge-acquisition metaphor (`mohamed2020gaining`), framed within the field (`del2019bio`, `hussain2019metaheuristic`).
- **The four structural limitations of GSK** that DT-GSK addresses: (1) fixed, hand-set parameters; (2) no local search / refinement; (3) no stagnation recovery; (4) no linkage / structure awareness. State them as a numbered or clearly enumerated set — they map one-to-one onto the Method's scaffold + SGSM + polish.
- **The NFL premise** (`wolpert1997nfl`) as the honest rationale: no universal winner, so the contribution is a *structure-adaptive* method targeted at high-D structure, evaluated within its family — not a universal-dominance claim.
- **An explicit, numbered contributions list** (3–5 bullets), copied from `claims.md`, each mapped to the evidence and the section that carries it.
- The benchmark context (`awad2016problem`) and a one-line roadmap.

**Must-avoid.** A literature dump (that is Section 2 — resist the urge to survey here). Overclaiming universality (NFL forbids it — and the low-D limitation contradicts it). Promising a result Results does not deliver.

**Length.** 1.5–2.0 pp.

**Citation shortlist:** `mohamed2020gaining`, the five family variants (`mohamed2020agsk`, `apgsk2021`, `fdbagsk2023`, `alfadli2025atmals`, `jawad2024egsk`), `wolpert1997nfl`, `del2019bio`, `hussain2019metaheuristic`, `awad2016problem`.

**Exhibits.** Optionally forward-reference the flowchart and the headline results table; no new exhibits.

**Voice.** Confident, specific, forward-leaning — but the confidence is bounded by what Results proved.

#### Drafting loop — Introduction
1. **Draft** motivation → GSK + its four limitations → NFL rationale → contributions list → roadmap.
2. **Bind.** Contributions list matches `claims.md` and the finished Method/Results; the single strongest quantified result named in the contributions is the one Results actually reports; NFL and family citations bound.
3. **R1 review.** Novelty framed honestly? No universality overclaim? Does each contribution have downstream evidence?
4. **R2 review.** Clarity of the four-limitations enumeration; roadmap correct against the `\input` order; within 2.0 pp.
5. **Mark overflow.** Extended motivation or background → related work / supplement, not the intro.

---

### 4.6 Conclusion  → `sections/conclusions.tex`

**Goal.** Restate what was *shown* (not hoped) and where it goes next. Short and disciplined.

**Must-include.**
- The contribution recap tied to the Results evidence (the high-D Friedman-rank lead within the family, with its honest scope).
- **Concrete future work:** large-scale via `omidvar2014dg`-style decomposition; a covariance-aware refinement seeded by the learned SGSM eigenstructure (`hansen2001cmaes`); higher-order (beyond pairwise) linkages; multi-objective / constrained extension.

**Must-avoid.** New claims or new results (nothing appears in the conclusion that was not shown earlier). Grandiosity. Restating the abstract.

**Length.** 0.75–1.0 pp.

**Citation shortlist:** `omidvar2014dg`, `hansen2001cmaes`; family/method keys only if strictly needed for the recap.

**Exhibits.** None.

**Voice.** Measured, closing, honest about scope.

#### Drafting loop — Conclusion
1. **Draft** recap → future work.
2. **Bind.** Every recapped result exists in Results; future-work citations bound.
3. **R1 review.** Any new claim smuggled in? Grandiosity?
4. **R2 review.** Within 1.0 pp; no abstract-echo.
5. **Mark overflow.** None expected.

---

### 4.7 Abstract  → `main.tex` abstract block (write **last**)

**Goal.** In ≤250 words: the problem, the gap in fixed-bias GSK variants, the SGSM idea, the single strongest *quantified* result (e.g. a Friedman-rank lead on CEC2017 at a stated $D$, with honest scope), and reproducibility.

**Must-include.** One concrete number; the benchmark + dimensions; the fact that the comparison is **within the GSK family**.

**Must-avoid.** Vague superlatives ("significantly outperforms" with no number). Listing every mechanism. **Citations** (MDPI abstracts carry none). Exceeding 250 words.

**Length.** ≤250 words, one structured paragraph.

**Citation shortlist:** none.

**Exhibits.** none.

**Voice.** Dense, factual, no throat-clearing.

#### Drafting loop — Abstract
1. **Draft** from the Phase-1 one-paragraph thesis, updated to the delivered result.
2. **Bind.** The one concrete number matches the Results exhibit exactly; benchmark + D + within-family scope stated.
3. **R1 review.** Is the number honest and scoped (not a cherry-picked best-case)?
4. **R2 review.** Word count ≤250 (verify), no citations, one paragraph.
5. **Mark overflow.** N/A.

---

## Worked examples

Model outputs. Match this register and citation discipline. (These are drafting-stage examples; Phase 6 will vary rhythm further.)

### A model paragraph — the SGSM subsection (Method)

> The support graph $S \in \mathbb{R}^{D\times D}$ records, for each pair of variables $(i,j)$, an estimate of how often coordinated change in $i$ and $j$ is rewarded. After each accepted trial we update the estimate by an exponential moving average, $S_{ij} \leftarrow (1-\alpha)\,S_{ij} + \alpha\, r_{ij}$, where $r_{ij}$ is the acceptance-derived support signal for the pair and $\alpha \in (0,1)$ is the memory rate; unaccepted trials leave $S$ unchanged. An edge is trusted only once it clears the confidence gate $S_{ij} \geq \tau$, so that transient co-movement does not prematurely bias the operators. Because $r_{ij}$ is read off the acceptance history the optimizer already produces, $S$ is learned at no additional function-evaluation cost — in contrast to differential grouping~\cite{omidvar2014dg}, which spends a dedicated evaluation budget to detect variable interaction before optimization begins. The trade-off is deliberate: we accept a noisier, online estimate of structure in exchange for spending the entire budget on search, and we show in Section~\ref{sec:results} that this estimate is accurate enough to drive the linkage-aware crossover and the eigenframe polish.

Note: exactly one `\cite` (`omidvar2014dg`), the EMA rule and gate are both defined, the contrast is a trade-off not a boast, and there is a forward `\ref` to Results.

### A contributions bullet list (Introduction)

> This paper makes the following contributions:
> \begin{enumerate}
>   \item \textbf{SGSM, an acceptance-driven pairwise support graph} that learns variable interaction structure online, at no extra function-evaluation cost, and gates it by confidence before use (Section~\ref{sec:method}).
>   \item \textbf{A self-adaptive scaffold} — bandit-grounded knowledge control, non-linear population reduction, Cauchy-rescue stagnation escape, and acceptance-gated pool pruning — that removes GSK's four structural rigidities (Section~\ref{sec:method}).
>   \item \textbf{Structure-driven refinement}: a linkage-aware block crossover and a deterministic eigenframe polish on the learned interaction basis, bounded at high $D$ by cadence thinning (Section~\ref{sec:method}).
>   \item \textbf{A within-family evaluation} on CEC2017 ($D\in\{10,30,50,100\}$), CEC2011, and a second CEC2013 comparison suite, with full Friedman/Nemenyi ranking, Holm-corrected Wilcoxon tests, and A12/BCa effect sizes, including a candid account of where the method does not help (Section~\ref{sec:results}).
> \end{enumerate}

### A results paragraph citing a table and stating A12 + BCa

> At $D=100$ on CEC2017, \ismgsk{} attains the best mean Friedman rank in the family (Table~\ref{tab:summary_d100}), and the pairwise Wilcoxon signed-rank test, Holm-corrected across the six baselines~\cite{wilcoxon1945individual,holm1979simple}, confirms a significant advantage over five of the six ($p<0.05$). The effect is large rather than marginal: against the second-ranked baseline the Vargha–Delaney statistic is $A_{12}=0.71$~\cite{vargha2000critique}, and the BCa bootstrap 95\% confidence interval on the median error gap excludes zero (Table~\ref{tab:bca}). The lead narrows at $D=30$ and is statistically indistinguishable from the family leader at $D=10$, which we discuss next.

### A limitations paragraph (Results & discussion)

> The gains are not uniform, and it would be dishonest to present them as such. At $D=10$ the structure-exploitation machinery — SGSM, block crossover, and the eigenframe polish — is gated down or contributes little, and \ismgsk{} is statistically indistinguishable from the best family baseline (Figure~\ref{fig:cd_d10}); on a handful of low-dimensional, near-separable functions it is marginally worse. This is structural rather than a tuning artefact: the subsystems that create the high-$D$ advantage have little to exploit when variables scarcely interact. Two further costs are worth naming. The support graph carries an $O(D^2)$ memory footprint, which is modest at the dimensions studied but would need revisiting well beyond $D=100$. And on functions whose interaction structure shifts during the run, the online estimate lags, so the linkage-aware operators occasionally act on stale support before the confidence gate corrects them. Addressing the low-$D$ regime and very-large-scale memory via decomposition~\cite{omidvar2014dg} is the clearest line of future work.

---

## Pitfalls & anti-patterns

- **Literature dump in the introduction.** The intro motivates and contracts; it does not survey. Every "many works have…" paragraph belongs in Section 2. If the intro cites more than its shortlist, you are surveying.
- **Undefined symbols.** Every symbol is defined before its first use, once, and reused consistently. A reader hitting an undefined $\tau$ or $S_{ij}$ is an automatic R2 must-fix.
- **Significance without a test.** The word "significant" (and "outperforms", "superior") may appear only next to a named, corrected test and its $p$-value. Effect sizes and CIs travel with p-values, never instead of them.
- **Citing outside the 57.** The admissible set is closed (Appendix A / Part 8 of `PAPER_BUILD_PROMPT.md`). Do not import a "better" reference. If a claim needs a citation that does not exist in the 57, weaken the claim — do not add the key.
- **Exceeding the section budget.** Ceilings are Intro 2.0pp, Related 2.5pp, Method 5.0pp, Setup 1.5pp, Results 5.0pp, Conclusion 1.0pp, Abstract 250 words. Overflow is *routed to the supplement*, never crammed into the main text.
- **Promising more than the data shows.** The framing sections are written after Results precisely so they cannot overclaim. If a contribution bullet or abstract sentence asserts a result Results does not deliver at the stated scope, it is a defect. The low-D limitation must survive into every framing section — no sentence anywhere may imply universal dominance.
- **Editing an exhibit to fit prose.** If a number is wrong, fix Phase 3 / Phase 2, not the sentence — and never the plotted number.
- **Cherry-picking.** No dimension, function, or baseline is silently dropped to flatter the method. The hard-case convergence figure and the limitations paragraph are mandatory antidotes.

---

## Exit gate

Phase 4 is complete only when **all** hold, with evidence:

- [ ] **Every section passes its R1 (Q1) checklist** — novelty delimited, baselines/scope justified, statistics correct and corrected, reproducibility present, ablations earn each mechanism, losses and limitations reported, threats to validity acknowledged.
- [ ] **Every section passes its R2 (Q2) checklist** — a non-specialist can follow the method, no undefined symbols, setup fully specified, every exhibit referenced where discussed, formatting clean, within budget.
- [ ] **Total length within budget** for each block and overall (≈16–22 typeset pp main text, references excluded).
- [ ] **Zero undefined `\ref`/`\cite`** — every `\ref` resolves to a real Phase-3 `\label`; every `\cite` key is one of the 57 and on the section's sanctioned role.
- [ ] **Every stated number is bound** to a Phase-2 source via the binding map; no orphan numbers.
- [ ] **All overflow routed to the supplement** — every `% TODO(supplement)` tag is logged in the overflow list handed to Phase 5; nothing critical is exiled, nothing over-budget remains in the main text.
- [ ] **All five `sections/*.tex` drafted** (`introduction`, `literature_review`, `proposed_algorithm`, `performance` [setup+results], `conclusions`) plus the abstract in `main.tex`.

Do not cross this gate with an unchecked box. A section that "mostly" passes is a Phase-7 ticket waiting to happen.

---

## Hand-off

Hand to **`PHASE_5_supplementary.md`**. Deliver:

1. Complete main-text `sections/*.tex` + abstract, each within budget and passing R1/R2 self-review.
2. The **overflow list** — every `% TODO(supplement)` item from every section (full per-function tables, full Wilcoxon matrices, full convergence sets, full sweep grids, extended ablations, pseudocode sub-procedures, seed/environment tables, any proof sketch). Phase 5 assembles these into `sections/supplementary_content.tex` and cross-links them back to the main text.
3. The list of **main-text cross-reference pointers that expect a supplement target** (e.g. "full per-function results in Table S-x"), so Phase 5 can create resolving `\label`s.

Phase 5 owns `supplementary.tex` / `sections/supplementary_content.tex`; it must not alter a fact in the main text — only house the rigour that did not fit. After Phase 5, the paper proceeds to Phase 6 (prose-quality pass) and Phase 7 (adversarial review).
