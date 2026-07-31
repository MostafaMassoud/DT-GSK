# DT-GSK — Canonical Pseudocode

**Phase 3 deliverable** (Phase 3 task 8; canonical source for `algorithm_pseudocode.tex`
and the Phase 7/9 method figure). Order and gating match `_dt_core.dt_gsk_optimize`
(`_dt_core.py:1974`) and the verified pipeline in `docs/algorithms/dt-gsk.md`. Symbols:
`notation_table.md`. Equation labels (E1–E12): `equation_registry.csv`. Dimension-gated
steps (D≥50, D≥100) are skipped when the `pub` tier does not enable them.

```text
ALGORITHM DT-GSK(f, D, [ℓ,u], MaxFES = 10^4·D, seed)
  cfg ← build_pub_config(D)                         # dimension-tiered pub profile
  rngs ← ThreefrySubstreams(seed)                   # 13 append-only substreams (E12)

  # ---- Initialisation ----
  NP ← NP_init ← 5·D
  P ← sample NP points uniformly in [ℓ,u]^D from rngs.init   # self-init (fair-start exception)
  F ← f(P)                                          # charged through BudgetController
  (x*, f*) ← best(P, F)
  (x_gb, f_gb) ← (x*, f*)                            # global-best shadow
  t ← NP;  nfes_at_best ← t

  while t < MaxFES do
    # 1. NLPSR population-size reduction                                (E5)
    NP_target ← round_half_up( NP_init + (N_min − NP_init)·x^(1−x) ),  x = t/MaxFES
    if psr_enabled and NP_target < NP: cull worst (NP − NP_target) rows

    # 2. ACE knowledge-source selection                                (E6)
    for each i: arm_i ← sample arm m ~ π  from rngs.ace                 # (KF,KR,Kexp)_i
    #    (ACE disabled → fixed (KF,KR,Kexp) with heterogeneous-Kexp fallback)

    # 3. Junior / senior gaining-sharing trial construction           (E1–E4)
    rank P by fitness;  D_jun ← D·(1−x)^Kexp                           # junior dim count (E2)
    (R1,R2,R3)_jun ← junior_indices(rank)                              # rank-neighbours (E1a)
    (R1,R2,R3)_sen ← senior_indices(rank, p)                           # top/mid/worst (E1b)
    U ← gaining_sharing_update(P, R1,R2,R3, KF, D_jun)                 # (E3)
    # 3b. crossover mask: per-coordinate KR, OR linkage block mask     (E4)
    if linkage_blockwise_enabled: mask ← block_mask(size_by_dim, mix_prob; SGSM blocks if D≥50)
    else: mask ← per-coordinate Bernoulli(KR)
    V ← where(mask, U, P)

    # 4. Bound repair + evaluate                                       (E7)
    V ← midpoint_repair(V, P, [ℓ,u])
    F_V ← f(V)                                        # charged; truncates if > remaining
    t ← t + |V|

    # 5. Elitist accept (greedy, no-worse; ties accepted)             (E8)
    for each i: if F_V[i] <= F[i]: (P[i],F[i]) ← (V[i],F_V[i]); record acceptance
    update EliteArchive A (distance-thresholded) if arch_enabled
    update ACE credit ω, π from acceptances (EMA, floor π_min)          (E6)
    if argp_enabled: soft-freeze ACE arms with windowed acceptance < τ_argp to π_min
                     (over W_argp=30 gens; recoverable — re-activate on recovery; ≥2 arms kept active)

    # 6. BSE budget-safe escape                                        (E9)
    if bse_enabled and StagnationDetector.triggers(window W):
        perturb worst r_rst·NP by Cauchy 𝒞(0,γ) from rngs.bse; seed some from A
        (bounded by R_max, disabled past bse_stop_frac)

    # 7. (D≥50) SGSM/ISM update + coordinate local search             (E10)
    if interaction_graph_enabled and D ≥ 50:
        G ← λ·G + η·outer(strictly-improving accepted deltas)   # η=1.0; zero extra evals
        if confidence(G) ≥ κ_min:
            supply linkage blocks to step 3b   # coordinate LS runs; top-k subspace LS implemented but not enabled

    # NOTE: the (D≥100) upper-tier controllers are CROSS-CUTTING, not a stage here.
    #   They act inline at earlier points, not as a block after the local search:
    #     - SP-NLPSR floor        -> inside population reduction (top of the generation)
    #     - A2 frozen-streak broaden, FC4 link random-mix -> inside trial construction
    #     - A1 late-accept clip, basin-memory write        -> inside acceptance
    #     - basin-novelty reseed                           -> inside the BSE escape
    #     - TERRA budget/ROI gate  -> gates the local search only (the escape
    #       hook exists but is runtime-dead: terra_escape_allowed is True in
    #       both branches; see _dt_core.py:3915-3927)
    #   (all enabled only when D ≥ 100; see _dt_profiles._PUB_D_GE_100_EXTRA)

    # 9. (D≥50) eigenframe final polish (one-shot, RNG-free)           (E11)
    if final_polish_enabled and x ≥ s_fp and not polished:
        V_dirs ← eigenbasis of SGSM signed matrix (coord axes if no signal)
        x* ← compass_search(x*, V_dirs, strict budget)  # probes charged; no RNG
        polished ← true

    # 10. Update global-best
    if best(P) < f_gb: (x_gb,f_gb) ← best(P);  nfes_at_best ← t

    # 11. Deep-stall full restart (default-on, global-best preserved)  (via ρ_ds)
    if deep_stall_restart_enabled
       and (t − nfes_at_best)/MaxFES ≥ deep_stall_frac
       and MaxFES ≥ deep_stall_min_budget
       and cooldown elapsed and x < deep_stall_stop_frac:
        P ← resample NP points uniformly in [ℓ,u]^D from rngs.bse; F ← f(P); t += NP
        reset stagnation window                       # x_gb,f_gb preserved ⇒ never lose ground
  end while

  return (x_gb, f_gb)         # global-best (substitutes working incumbent when better)
```

## Notes for the reader (reimplementability, Phase 3 acceptance criterion)
- **Return value is the global-best**, not the working incumbent — the deep-stall restart's
  correctness depends on this.
- **All `f(·)` calls are charged** through one `BudgetController`; the last batch truncates to
  the remaining budget (see `evaluation_accounting_report.md`).
- **Every stochastic step names its substream** (`rngs.init/ace/bse/...`); toggling a
  subsystem cannot disturb another's draw order (byte-stable ablation).
- **Dimension gating**: linkage (`pub` ON from D≥10 per tier; ISM-fed from D≥50), ISM + polish (D≥50),
  upper-tier controllers (D≥100). Below the tier, the guarded block is a no-op.
