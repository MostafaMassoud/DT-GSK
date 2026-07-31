# DT-GSK — Contribution Matrix (inherited / modified / original)

**Phase 3 deliverable** (PAPER_BUILD_PROMPT.md Phase 3, task 2). Classifies every
mechanism in the *executed* DT-GSK method as **inherited**, **modified**, or
**original** relative to the closest approved literature, with the exact
difference and the code location. Evidence anchors: `docs/algorithms/dt-gsk.md`
(byte-stability-locked spec), the source modules cited per row, and the evidence
cards under `papers/governance/evidence_cards/`.

> Scope note. "Executed method" = the `pub` profile resolved by
> `_dt_profiles.build_pub_config(dim)` — the single shipped, paper-facing
> configuration. Dataclass defaults in `_dt_core.ISMGSKConfig` are the *bare*
> fallback; the tier-resolved `pub` values are what runs. Novelty claims below
> are scoped to what the `pub` profile actually enables at each dimension tier.

## Legend
- **INH** inherited unchanged from a cited method.
- **MOD** inherited in concept but materially modified (the modification is stated).
- **ORI** original to DT-GSK (no direct antecedent in the cited corpus at this specificity).

| # | Mechanism | Class | Closest approved antecedent | Exact difference / novelty | Code anchor |
|---|---|---|---|---|---|
| 1 | Junior/senior gaining-sharing operator | **INH** | GSK (mohamed2020gaining) | Rank-neighbour junior (R1=r−1, R2=r+1, R3=random≠{i,R1,R2}); senior top/mid/worst partition by `p`. Numerics unchanged. | `gained_shared_junior.py:56`, `gained_shared_senior.py:59` |
| 2 | Junior→senior dimension schedule (`Kexp`) | **INH** | GSK (mohamed2020gaining) | Standard `(1−nfes/MaxFES)^Kexp` junior-dimension decay; `Kexp` default 10. | `_dt_core.py` (Kexp path), `ISMGSKConfig.Kexp:171` |
| 3 | Greedy elitist selection (no-worse, <=) | **INH/MOD** | GSK (mohamed2020gaining) | Child replaces parent iff no worse (<=; ties accepted); vector-update numerics unchanged. | `_dt_core.dt_gsk_optimize:1974` (accept step) |
| 4 | Midpoint (L-SHADE) bound repair | **INH** | tanabe2014improving (L-SHADE) | Out-of-bounds component repaired to midpoint of parent and violated bound. | `bound_constraint.py:1` |
| 5 | Nonlinear population-size reduction (NLPSR) | **MOD** | APGSK NLPSR (apgsk2021); population-size-reduction lineage L-SHADE LPSR (tanabe2014improving) | Same `x^(1−x)` concave shape, but starts from dimension-scaled `NP=5·D` and bottoms at a **tier-specific floor** `n_min` (25 at D≥50) rather than a fixed minimum; worst-drop cull each gen. | `_dt_core._psr_target_size:790`, `_numba_accel._psr_target_nb:909` |
| 6 | ACE — bandit control of `(KF,KR,Kexp)` | **MOD** | AGSK adaptive parameter pools (mohamed2020agsk); APGSK (mohamed2021novel); EMA credit ~ SHADE memory (tanabe2013shade) | AGSK adapts KF/KR from a fixed pool by success history; ACE is an **EMA-credit multi-armed bandit over a 5-arm `(KF,KR,Kexp)` operator pool** (arm 2 = GSK-pure) with a min-probability floor and, at D≥20, top/bottom acceptance memory + optional DE arm. Operator-level (not just parameter-level) adaptation. | `_ace_update_probs:1193`, `_ace_sample_indices:1163`, `ace_pool:202` |
| 7 | ARGP — acceptance-rate gated pool pruning | **ORI** | (adaptive-operator pruning generally; no direct GSK-family antecedent) | Freezes ACE arms whose windowed acceptance falls below a tier threshold after a warm-up; concentrates draws on productive operators. | `_argp_update_memory_probs:1261`, `_argp_update_memory_probs_guarded:1304` |
| 8 | Linkage-aware block crossover | **MOD** | GSK per-coordinate KR mask (mohamed2020gaining); linkage/grouping ideas (omidvar2014dg) | Replaces the per-coordinate KR mask, for ~70% of the population, with a **block mask over arbitrary (non-contiguous) index subsets** — blocks are chunks of a random coordinate permutation (block size 5<D50, 10≥D50), periodically refreshed; at D≥50 the block structure is supplied by the SGSM graph. | `_make_linkage_groups:908`, `_build_phase4_masks:926`, `_resolve_linkage_block_size:839` |
| 9 | BSE — budget-safe escape | **MOD** | Restart/stagnation escape (jade/shade lineage; storn1997differential Cauchy) | Triple-trigger stagnation detector (acceptance / diversity / signal floors) firing a Cauchy rescue + archive-seeded partial restart, **hard-capped by `bse_max_restarts` and `bse_stop_frac`** so it can never overshoot MaxFES. | `StagnationDetector:1813`, `cauchy_like:1412`, `EliteArchive:1640` |
| 10 | Diversity archive (distance-filtered) | **MOD** | External archive (JADE zhang2009jade; SHADE tanabe2013shade) | Distance-filtered diversity archive (`|A|~1.5·NPinit`, cap 200, normalized-L2 threshold; no fitness admission) used to seed BSE restarts. | `EliteArchive:1640`, `arch_*` fields `:298` |
| 11 | SGSM/ISM — interaction-structure memory | **ORI** | (variable-interaction learning e.g. omidvar2014dg differ in mechanism & cost) | **Zero-extra-evaluation** decaying (`0.95`) coordinate-pair interaction graph learned from *accepted* moves; confidence- and evidence-gated; supplies linkage blocks and a top-k-block subspace to local search. Learns structure only from moves the run already made. | `interaction_graph.py:1` (862 lines) |
| 12 | Eigenframe final polish | **ORI** | Pattern/compass search (kolda2003directsearch; nelder1965simplex) | One-shot **RNG-free deterministic compass search on the eigenbasis of the SGSM signed interaction matrix**, in the final budget slice; coordinate axes when no graph signal. Consumes budget via the strict path, draws no RNG (byte-identical whether it fires or not). | `_final_polish_basis:1882`, `_final_polish_compass:1907` |
| 13 | Deep-stall full restart (multi-start) | **MOD** | Restart metaheuristics (generic); distinct from BSE | Default-ON full re-init of the **working** population on a deep stall (frozen ≥`deep_stall_frac`=0.25 of budget), with a **preserved global-best** so a restart can never lose ground and can escape a basin BSE structurally cannot. `deep_stall_min_budget`=20000 keeps tiny budgets inert (byte-safe). | `deep_stall_*` fields `:444`, restart block in `dt_gsk_optimize` |
| 14 | D≥100 controllers (A1/A2/FC4, basin memory, SP-NLPSR, TERRA) | **ORI** | (high-D EC protections generally) | Late-budget A1 accept-clip, A2 frozen-streak broaden, FC4 linkage random-mix, basin memory, SP-NLPSR subspace floor, TERRA budget policy — all D≥100-gated, default no-op below. | `_dt_core` late-controller block, `basin_memory.py:1`, `budget_policy.py:1` |
| 15 | 13-substream append-only RNG layer | **ORI** | Counter-based RNG (threefry; salmon2011parallel-style) | Prefix-locked 13-named-substream layer child-seeded from one run seed; toggling any subsystem cannot disturb others' draw order — the mechanism that makes byte-stable ablation possible. | `_dt_rng.py:1` |
| 16 | Self-init (fair-start exception) | **MOD** | family fair-start `X0` protocol | Draws its own `5·D` initial population from `threefry(seed)` (same stream as fair-start) and ignores the runner's `X0`; documented exception, still deterministic. | `dt_gsk.py:166` |

## Summary counts
- **Inherited (INH):** 4 — the GSK operator core, dimension schedule, greedy selection, bound repair.
- **Modified (MOD):** 6 — NLPSR, ACE, linkage crossover, BSE, elite archive, deep-stall restart, self-init (6–7 depending on self-init classing).
- **Original (ORI):** 5–6 — ARGP, SGSM/ISM, eigenframe polish, D≥100 controllers, 13-substream RNG layer.

## Novelty statement (evidence-bounded, for Phase 4 claim freeze)
DT-GSK's **primary original contribution** is the pair **SGSM/ISM interaction-structure
memory (11) + eigenframe final polish (12)** — learning accepted-move geometry at
**zero extra objective evaluations** and exploiting it for both crossover linkage and a
deterministic end-of-run polish. Its **secondary contributions** are the operator-level
**ACE bandit + ARGP pruning (6,7)** and the **dimension-tiered budget/escape stack**
(NLPSR floor, triple-trigger budget-safe BSE, global-best-preserving deep-stall restart).
No claim of a *new operator* is made — the gaining-sharing operator itself is inherited
unchanged (rows 1–3). Claims must be phrased as *control, budget, structure-memory, and
polish* contributions layered on the GSK scaffold, never as a new base operator.

## Prohibited wordings (QA — Section-3 checkpoints)
- Do **not** call SGSM/eigenframe polish "free" without the qualifier "no extra *objective*
  evaluations" (they do have compute cost — see `complexity_analysis.md`).
- Do **not** describe the gaining-sharing operator as novel.
- Do **not** claim NLPSR is new — it is a tier-floored variant of the APGSK NLPSR schedule.
