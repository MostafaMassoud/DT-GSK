# DT-GSK — Novelty Scope: Closest-Work Comparison, Non-Claims, Evidence Roles (Phase 4, tasks 5 + 9)

**Phase 4 deliverable (claim-freeze input to Gate 4).** Date: 2026-07-10.
Sources of record: `phase_03/contribution_matrix.md` (frozen novelty statement +
prohibited wordings), `papers/governance/evidence_cards/` (all comparison cells below
are bounded by the cited card's "supported uses" and "prohibited overextensions"),
`phase_04/terminology_glossary.md` (frozen names), `phase_04/contribution_matrix.md`
(accepted C1–C4).

**Comparison discipline (binding).** Closest-work comparisons are made ONLY along four
verified dimensions — **update trigger, evaluation cost, what is learned, how it is
exploited** — at the conceptual level supported by the evidence cards. No exhaustive or
universal novelty claim; no equivalence implied among support graph, covariance matrix,
decomposition, and eigenbasis; no performance numbers from the cited works beyond what
their cards permit.

---

## 1. Closest-work comparison

### 1.1 ISM (C1) vs differential grouping [omidvar2014dg]

| Dimension | Differential grouping (DG) | ISM (interaction-structure memory) |
|---|---|---|
| Update trigger | Offline grouping stage before optimization begins; pairwise forward-difference probes (Theorem 1) | Online, during the run: updated on every *accepted* move; decaying memory (λ = 0.95), confidence- and evidence-gated |
| Evaluation cost | Dedicated objective evaluations, O(n²/m) total (e.g. ~10^6 FEs for fully separable n = 1000) | **No extra objective evaluations** — learns from evaluations the run already made; compute-only cost per `phase_03/complexity_analysis.md` (never worded "free") |
| What is learned | Pairwise non-separability decisions (threshold ε on forward-difference disparity), yielding a variable partition | A weighted, signed coordinate-pair interaction graph (soft, decaying evidence — not a hard partition) |
| How exploited | Problem decomposition into cooperative-co-evolution subcomponents optimized round-robin / contribution-based | No decomposition: supplies linkage blocks to the GSK block crossover (D ≥ 50), a top-k-block subspace to local search, and the eigenbasis for the final polish |

Boundary: DG's evidence is CEC'2010 LSGO at n = 1000; DT-GSK makes **no LSGO claim**
(evidence tops out at D = 100). DG is cited as the structure-aware decomposition line
DT-GSK is positioned against, and as future-work direction — with DG's stated failure
modes (Rosenbrock-type overlap; region-dependent separability) acknowledged.

### 1.2 ISM (C1) vs covariance matrix adaptation [hansen2001cmaes]

| Dimension | CMA-ES | ISM |
|---|---|---|
| Update trigger | Every generation, from *selected* mutation steps plus evolution-path cumulation | Every *accepted* move, into a decaying pair graph; no evolution path, no sampling-distribution update |
| Evaluation cost | No extra objective evaluations, but ~n² evaluations of adaptation time for a significant shape change; O(n²) storage; eigendecomposition amortized (~every n/10 generations) | No extra objective evaluations; sparse graph updates; eigendecomposition only once, for the final polish basis (compute cost per `complexity_analysis.md`) |
| What is learned | Full mutation covariance (PCA of selected steps) — a complete sampling-distribution shape | A sparse signed coordinate-pair interaction graph — structure evidence, not a sampling distribution |
| How exploited | Reshapes every mutation the strategy samples (rotation + scaling of the search distribution) | Leaves GSK operator numerics unchanged; exploited discretely (block masks, local-search subspace) and once terminally (polish basis) |

Boundary: no claim that ISM confers CMA-style invariance (translation/rotation/
monotone-transform invariance belongs to CMA-ES per its card); no equivalence implied
between the ISM graph and a covariance matrix.

### 1.3 ISM (C1) vs eigenvector-based crossover [guo2015eig]

| Dimension | Eigenvector-based crossover (DE) | ISM |
|---|---|---|
| Update trigger | Every generation: covariance of the *current population* (no cumulative adaptation) | Accepted-move history with decay — a persistent memory, not an instantaneous population statistic |
| Evaluation cost | No extra objective evaluations; O(D³·Gmax) compute (measured overhead ≤ ~5.3% of function-call time per its card) | No extra objective evaluations; graph maintenance plus a single terminal eigendecomposition (per `complexity_analysis.md`) |
| What is learned | Eigenbasis of the population covariance (population geometry) | Signed pair-interaction evidence of moves that actually improved solutions |
| How exploited | Rotate–crossover–rotate-back with probability P, to make DE crossover rotationally invariant | In-axis block masks for the GSK crossover + local-search subspace + one-shot final-polish basis; **no rotational-invariance claim** for the main operator |

Boundary: guo2015eig is the representative structure-aware crossover line in DE;
DT-GSK's operators remain coordinate-frame GSK operators — the eigenbasis is used only
in the endgame polish (C2).

### 1.4 ACE + ARGP (C3) vs adaptive operator selection [fialho2010adaptive] and bandits [auer2002finite]

| Dimension | AOS / bandit prior art | ACE + ARGP |
|---|---|---|
| Update trigger | Per-decision reward updates; UCB index or restart-on-change (Page–Hinkley) policies | Per-generation EMA credit from acceptance events; at D ≥ 20 top/bottom acceptance memory; ARGP freezes arms on windowed-acceptance shortfall after warm-up |
| Evaluation cost | Framework-level (no objective cost of its own) | Same — control-plane only; no extra objective evaluations |
| What is learned | Arm-quality estimates for abstract operators (validated on artificial reward scenarios in fialho2010adaptive; stationary-regret theory in auer2002finite) | Arm quality of concrete (KF, KR, Kexp) GSK operator settings (arm 2 = GSK-pure), plus which arms are unproductive (ARGP) |
| How exploited | Selection probabilities / index maximization | Draw probabilities with a min-probability floor; ARGP concentrates draws on productive operators |

Boundary (binding, per both cards): these sources **ground** adaptive operator selection
as a dynamic exploration/exploitation problem; they are **not proof that the exact ACE
mechanism is inherited**. ACE is not claimed to be UCB1, D-MAB, PM, or AP; **no regret
bound transfers** to ACE (the theorems assume stationary rewards; an evolutionary run's
rewards drift).

### 1.5 Eigenframe final polish (C2) vs direct search [kolda2003directsearch, nelder1965simplex]

| Dimension | Compass/pattern search; Nelder–Mead | Eigenframe final polish |
|---|---|---|
| Update trigger | Iterative throughout its run: accept improving step or halve step (compass); reflect/expand/contract simplex (NM) | One-shot, in the final budget slice only, gated by the tier policy; fires at most once |
| Evaluation cost | Objective evaluations per trial step, run-length unbounded a priori | Objective evaluations charged through the strict budget path, hard-capped by the final slice; RNG-free (byte-identical whether it fires or not) |
| What is learned | Nothing carried in (coordinate directions fixed; simplex geometry adapts locally during the search) | Nothing learned by the polish itself — it *consumes* C1's learned basis (eigenbasis of the ISM signed interaction matrix; coordinate axes when no graph signal) |
| How exploited | General-purpose derivative-free local search | Deterministic endgame refinement along learned interaction directions |

Boundary (per the kolda2003directsearch card): comparison is conceptual only; **no
generating-set-search convergence guarantee is transferred** to the polish or to
DT-GSK; no equivalence between an eigenframe search and generating-set search is
implied. NM's documented failure modes motivate the capped, deterministic design — they
are not evidence about the polish.

## 2. Explicit non-claims (binding register)

1. **No new base operator.** The gaining-sharing junior/senior operator, Kexp schedule,
   and greedy selection are inherited unchanged [mohamed2020gaining]; contribution
   language is "control, budget, structure-memory, and polish layered on the GSK
   scaffold".
2. **No field-wide superiority claim.** All superiority wording is "within the GSK
   family panel" (7 algorithms); no claim against DE/ES/PSO fields or CEC competition
   winners [wolpert1997nfl grounds the refusal of universal claims].
3. **No theoretical convergence result.** No GSS convergence theory, no bandit regret
   bound, no CMA-ES invariance property is claimed for DT-GSK or any component.
4. **No LSGO claim.** Evidence tops out at D = 100; no claim at n = 1000-scale
   large-scale global optimization; DG-style decomposition remains future work.
5. **No structure-recovery claim.** ISM is not claimed to identify the true
   separability/interaction structure of the objective; it accumulates heuristic
   evidence from accepted moves.
6. **No rotational-invariance claim** for the GSK operators or the block crossover.
7. **No "free" wording** for ISM/polish without the qualifier "no extra *objective*
   evaluations" (compute cost per `complexity_analysis.md`).
8. **No NLPSR novelty claim** — tier-floored variant of the APGSK NLPSR schedule.
9. **No component-causality claim in the main text** — all component-contribution
   statements are `DEFERRED_TO_PHASE_12_SUPPLEMENT_ONLY`.
10. **CEC2013 is never called "independent", "holdout", or "validation" in the main
    text** — it is the "second comparison suite" (no development-history independence
    evidence on record). The phrase "hold-out" survives ONLY as the frozen name of the
    SGSM-overlay ablation *design* in the Phase-12 supplement.
11. **No pre-Phase-6 numbers.** The only permitted rank statements are the verified
    family-panel ranks (thesis §5.1), marked "to be re-derived in Phase 6 from release
    rel-2026-07-10-262fc16c9".

## 3. Evidence-role table (task 5)

| Evidence source | Role | Binding constraints |
|---|---|---|
| CEC2017 panel, release `rel-2026-07-10-262fc16c9` [awad2016problem] | **PRIMARY** | Headline rank + scalability claims; 29 functions (F1, F3–F30; F2 excluded), D ∈ {10, 30, 50, 100}, 51 runs, MaxFES 10^4·D; full statistics suite (Friedman/Iman–Davenport, Nemenyi CD, Wilcoxon + Holm, A12/Cliff's delta, BCa, win/tie/loss). All numbers bound in Phase 6. |
| CEC2011 panel, same release [das2011cec2011] | **SECONDARY (real-world)** | Real-world corroboration within the panel; 25 runs, MaxFES 150,000, native dimensions; error column NaN by design on problems without published optima — best_fitness authoritative. No headline claim rests on CEC2011 alone. |
| CEC2013 panel, same release [liang2013cec2013] | **SECOND COMPARISON SUITE** | Descriptive/secondary breadth check. NEVER "independent"/"holdout"/"validation" in main text (non-claim #10). |
| CEC2020 results (if referenced at all) | **CONTEXT-ONLY** | Not panel evidence; no claims; no allowed citation key exists — may not be cited in the manuscript. |
| CEC2013-LSGO / any large-scale suite | **CONTEXT-ONLY** | Not run; supports non-claim #4 (no LSGO claim); no allowed citation key — not citable. |
| Scaffold ablation (`results/_ablation/`, ACE/NLPSR/BSE/linkage/LS/archive toggles) + SGSM-overlay ablation (`full`/`no-adaptive`/`no-sgsm` on the CEC2013 hold-out design) | **SUPPLEMENT-ONLY, PHASE-12-ONLY** | `DEFERRED_TO_PHASE_12_SUPPLEMENT_ONLY`. No ablation subsection, number, or result in the main manuscript; exhibit IDs SA01–SA03 reserved. Staging ablation data is not citable until promoted to a release. |
| Phase 3 deterministic trace + complexity analysis + freeze manifest | **DESCRIPTIVE (method integrity)** | Supports C4 and method-section statements (budget-exact, monotone, repeat-identical; O(D²)/O(D³) amortized compute); not performance evidence. |
| Verified family-panel ranks in `docs/algorithms/dt-gsk.md` | **PLANNING-ONLY** | Quotable in planning artifacts only, always marked "to be re-derived in Phase 6 from release rel-2026-07-10-262fc16c9". |

Panel scope reminder: every role above is scoped to the 7-algorithm GSK-family panel
(GSK, AGSK, APGSK, FDB-AGSK, eGSK, ATMALS-GSK, DT-GSK); eGSK contributes committed
reference comparator data (solver-provenance note in `papers/governance/data_ledger.csv`).
