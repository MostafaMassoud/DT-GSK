"""
gsk.dt_gsk - DT-GSK optimizer core.

This module implements the paper-facing DT-GSK optimizer.  The core is a
dimension-aware GSK scaffold with ACE, NLPSR/LPSR, BSE, ARGP,
linkage-aware crossover, a diversity archive, and a coordinate local
search.  At D>=50 the `dt_gsk` variant can activate the deterministic
interaction-structure memory (ISM) defined in `gsk.interaction_graph`.
At D>=100 the same single variant enables the high-dimensional budget and
late-stagnation controllers wired through `scripts/run_dt_gsk_variants.py`.

The main loop implements the GSK evolutionary framework with seven core
components plus auxiliary safeguards:

Core components:
1. ACE (Adaptive Control of Evolution):
   Multi-armed bandit selects from a pool of 5 (KF, KR, Kexp) parameter entries
   each generation. EMA-based probability learning from per-entry fitness deltas.
   Population is split into top/bottom halves with separate probability vectors.

2. NLPSR (Nonlinear Population Size Reduction):
   NP = NP_init + (N_min - NP_init) * x^(1-x) where x = evals/max_evals.
   More aggressive than LPSR early (71% reduction by 50% budget), gentler late.
   LPSR (linear) is also available: NP = NP_init + (N_min - NP_init) * x.

3. ARGP (Acceptance-Rate Gated Pool Pruning):
   Tracks rolling acceptance rate per ACE entry. After warmup (15% budget),
   freezes entries whose acceptance rate drops below 2%. Probability mass
   from frozen entries redistributes to survivors.

4. Linkage Crossover:
   Groups dimensions into blocks of size 5 (10 at D=100). ~70% of population
   uses block-level crossover, ~30% uses per-dimension. Preserves variable
   correlations created by rotation matrices in CEC benchmark functions.

5. BSE (Budget-Safe Escape):
   Triple-trigger stagnation detection with Cauchy perturbation and
   archive-seeded restart for diversity recovery.

6. Archive:
   Distance-threshold diversity archive for diversity preservation and BSE seeding.

7. Local Search:
   Coordinate local search (the ISM-block subspace variant is implemented but not enabled in the frozen configuration).

Auxiliary features:
- DE/rand/1 (injected via ACE pool)
- Module Gate (per-ACE-entry BSE control)
- KR Floor (minimum knowledge rate)
- Force Nonzero Update (null mutation guard)
- Dimension-Aware Profiles (three-tier auto-configuration)

Key Classes
-----------
- DTGSKConfig:        All hyperparameters for a single DT-GSK run
- DTGSKResult:        Optimization result (best_x, best_f, nfes_used)
- DTGSKGenerationLog: Per-generation diagnostics with paper-package telemetry

Entry Point
-----------
    dt_gsk_optimize(func, config, ...) -> DTGSKResult

Default CEC budget: 10000*D function evaluations.  Default initial
population: 5*D, subject to the active profile and PSR floor.
"""

from __future__ import annotations

import math
import warnings
from collections import deque
from collections.abc import Callable
from dataclasses import asdict, dataclass
import time

import numpy as np

from gsk_family.optimizers._dt_subsystems.bound_constraint import bound_constraint
from gsk_family.optimizers._dt_subsystems.budget import BudgetController
from gsk_family.optimizers._dt_subsystems.gained_shared_junior import gained_shared_junior_r1r2r3
from gsk_family.optimizers._dt_subsystems.gained_shared_senior import (
    gained_shared_senior_r1r2r3,
    gained_shared_senior_r1r2r3_from_rands,
)
from gsk_family.optimizers._dt_rng import RNGStreams
from gsk_family.optimizers._dt_subsystems._dt_provenance import current_git_commit, stable_hash
from gsk_family.optimizers._dt_subsystems.interaction_graph import (
    InteractionGraphState,
    ig_adaptive_threshold,
    ig_apply_restart_decay,
    ig_build_local_search_basis,
    ig_expand_blocks_with_singletons,
    ig_extract_blocks,
    ig_init,
    ig_ready,
    ig_select_local_search_dims,
    ig_stats,
    ig_update_from_accepted,
)
from gsk_family.optimizers._dt_subsystems.budget_policy import LinkageReliabilityState, PredictedValueGate, SPNlpsrState, dimension_scaled_n_min
from gsk_family.optimizers._dt_subsystems.basin_memory import BasinMemory

# Numba-accelerated hot paths (graceful fallback if unavailable)
from gsk_family.optimizers._dt_subsystems._numba_accel import (
    HAS_NUMBA,
    population_radius_fast,
    ace_project_probs_fast,
    archive_dists_fast,
    archive_consider_fast,
    archive_consider_batch_fast,
    build_junior_senior_fast,
    build_junior_senior_with_repair_fast,
    build_masks_scalar_fast,
    build_masks_scalar_rows_fast,
    build_masks_blockwise_fast,
    ace_sample_fast,
    ace_update_full_fast,
    psr_target_fast,
    dim_coverage_fast,
    ace_bincount_fused_fast,
    count_true_fast,
    compose_trial_fast,
    warmup as _numba_warmup,
)

_NUMBA_WARMED = False

# =============================================================================
# Config
# =============================================================================


def _round_half_up(x: float) -> int:
    """Round-half-up for non-negative x (deterministic, avoids banker's rounding)."""
    return int(np.floor(float(x) + 0.5))


@dataclass(frozen=True)
class DTGSKConfig:
    """Configuration for a single DT-GSK optimization run."""

    # Problem
    dim: int = 10
    bounds: tuple[float, float] = (-100.0, 100.0)
    max_nfes: int | None = None
    seed: int = 0
    rand_generator: str = "threefry"

    # Population sizing
    # - NPinit = 5 * D
    # - Nmin  = 12 for NLPSR
    pop_size: int | None = None           # If None, uses np_init_mult * dim
    np_init_mult: int = 5
    psr_enabled: bool = True
    psr_schedule: str = "lpsr"
    psr_alpha: float = 1.0
    n_min: int = 12
    # Init-stage basin-coverage oversampling (April 2026 D=30 F4 probe).
    # When k > 1, sample k*NP candidates at gen 0, evaluate them, retain
    # the best NP. Cost: (k-1)*NP additional FE at gen 0. Default k=1
    # is byte-identical to the locked headline.
    init_oversample: int = 1
    # Init-stage sampling strategy (April 2026 D=30 F4 diversity probe).
    # "uniform" (default) is byte-identical to the locked headline;
    # "lhs" uses scipy.stats.qmc.LatinHypercube to stratify each variable
    # across the population, seeded deterministically from rngs.init.
    init_method: str = "uniform"

    # Core GSK parameters (used as fallback when ACE is disabled)
    KF: float = 0.5
    KR: float = 0.9
    Kexp: float = 10.0

    # Senior selection fraction p (Table 11)
    p_senior: float = 0.05

    # Senior-GSK adaptive split (locked-headline at D >= 50).  See
    # ``_variant_dt_gsk`` in scripts/run_dt_gsk_variants.py for tier
    # resolution.  OFF for D < 50; byte-identical to bare GSK senior.
    p_senior_split_enabled: bool = False
    p_senior_bottom_wide: float = 0.15

    # Linkage-aware crossover
    linkage_blockwise_enabled: bool = False
    linkage_min_dim: int = 30
    linkage_block_size_by_dim: dict[int, int] | None = None
    linkage_block_mix_prob: float = 0.70
    linkage_block_refresh_period: int = 20
    # B.8: fail-closed toggle for unmapped dims (see gsk/config.py comment).
    strict_profile_dims: bool = False
    # DT2 significance program (docs/development/dt2/): when True, emit shadow
    # reward-per-eval diagnostics for learned vs random blockwise-linkage rows.
    # Observation-only -- reads already-computed improvement arrays, draws no RNG
    # and mutates no optimizer state, so the trajectory is byte-identical to pub
    # (guarded by the trajectory-identity regression test). Default off; the pub
    # profile never sets it.
    research_dt2_shadow: bool = False

    # Module toggles
    ace_enabled: bool = True
    bse_enabled: bool = True
    arch_enabled: bool = True

    # --- ACE (Adaptive Control of Evolution) ---
    # Each pool entry is (KF, KR, Kexp).  ACE controls all three per-individual.
    # Entry 2 is the "GSK-pure" config: exact baseline GSK defaults.
    # Entry 4 extends exploration time (low Kexp) with GSK step/crossover.
    # On unimodal functions ACE learns to concentrate on GSK-pure;
    # on multimodal it distributes across exploratory configs.
    ace_pool: tuple[tuple[float, float, float], ...] = (
        (0.1, 0.2, 2.0),       # 0: Cautious explorer
        (1.0, 0.1, 15.0),      # 1: Dimension-selective bold
        (0.5, 0.9, 10.0),      # 2: ★ GSK-pure (exact baseline defaults)
        (1.0, 0.9, 5.0),       # 3: Aggressive wide
        (0.5, 0.9, 3.0),       # 4: Extended-exploration GSK
    )
    ace_init_probs: tuple[float, ...] = (0.05, 0.05, 0.45, 0.05, 0.40)
    ace_learning_rate: float = 0.10
    ace_start_frac: float = 0.05
    ace_min_prob: float = 0.05
    ace_memory_mode: str = "single"

    # Coverage-weighted ACE feedback (experimental, off by default).
    # Scales omega by fraction of dims updated. Tested: insufficient
    # effect due to bandit rich-get-richer dynamics.
    ace_coverage_weighted: bool = False
    ace_coverage_exponent: float = 2.0

    # ARGP: Acceptance-Rate Gated Pool Pruning.
    # Freezes ACE entries whose rolling acceptance rate drops below
    # threshold. At D=10 nothing gets pruned; at D>=30 low-performing
    # entries are removed, improving FE efficiency.
    argp_enabled: bool = False
    argp_window: int = 30           # rolling window (generations)
    argp_threshold: float = 0.02    # freeze if acceptance < 2%
    argp_warmup_frac: float = 0.15  # don't prune before 15% of budget
    argp_preserve_split_memory: bool = False
    argp_threshold_top: float | None = None
    argp_threshold_bottom: float | None = None
    argp_freeze_scope: str = "shared"  # shared | per_half
    argp_confirm_windows: int = 1      # low-acceptance windows before freeze
    argp_max_frozen_frac: float = 1.0  # cap frozen entries per memory
    argp_soft_freeze_prob: float = 0.0 # 0 => use ace_min_prob

    # KR floor: minimum fraction of dimensions updated per individual.
    # Computed as max(KR_pool, kr_min_dims / D).
    # At D=10 with kr_min_dims=20: floor=2.0→clamped to KR_pool (no effect).
    # At D=30: floor=0.67 (entries 0,1 now update 20+ dims instead of 3-6).
    # At D=100: floor=0.20 (same as entry 0's native KR).
    # Set kr_min_dims=0 to disable.
    kr_min_dims: int = 0

    # DE entry: adds a DE/rand/1 operator as an extra ACE pool entry.
    # ACE learns when GSK entries vs DE entry works best per function.
    # DE inherently updates all dimensions, solving the D>=30 coverage
    # problem without changing the GSK operator itself.
    ace_de_entry: bool = False
    ace_de_F: float = 0.5           # DE mutation scale factor
    ace_de_CR: float = 0.9          # DE binomial crossover rate
    ace_de_init_prob: float = 0.20  # initial ACE probability for DE entry
    ace_de_policy_mode: str = "static"  # static | state
    ace_de_policy_acceptance_floor: float = 0.08
    ace_de_policy_diversity_cap: float = 0.25
    ace_de_policy_stagnation_gens: int = 12

    # --- Per-entry module gating ---
    # When True, individuals drawn from that pool entry are subject to
    # BSE restarts.  When the total ACE probability mass on module-active
    # entries drops below ace_module_gate_thresh, BSE restarts are
    # suppressed population-wide.
    # Entry 2 (GSK-pure) has modules OFF so the algorithm can self-select
    # pure GSK convergence on easy/unimodal landscapes.
    ace_pool_modules: tuple[bool, ...] = (True, True, False, True, True)
    ace_module_gate_thresh: float = 0.30
    ace_module_gate_mode: str = "static"  # static | hysteresis
    ace_module_gate_low: float = 0.20
    ace_module_gate_high: float = 0.35

    # --- Heterogeneous Kexp (fallback when ACE is disabled) ---
    # When ACE is enabled, Kexp is controlled per-individual from the pool.
    # These settings only apply when ace_enabled=False.
    kexp_hetero_enabled: bool = True
    kexp_small_prob: float = 0.20
    kexp_small_range: tuple[float, float] = (1.0, 5.0)
    kexp_large_range: tuple[float, float] = (5.0, 20.0)

    # --- BSE (budget-safe escape; Table 11) ---
    bse_window: int = 50                    # W steps
    bse_epsilon: float = 1e-8               # ϵ (scale-aware)
    bse_restart_frac: float = 0.10          # rrst (reduced from 0.20)
    bse_max_restarts: int = 2
    bse_cooldown_frac: float = 0.05         # Δcool as fraction of MaxFEs
    bse_stop_frac: float = 0.95
    bse_freeze_elites: bool = True
    bse_freeze_frac: float = 0.05
    bse_archive_inject_prob: float = 0.50   # probability to seed from archive
    bse_jitter_scale: float = 0.10          # jitter as fraction of range
    bse_trigger_mode: str = "stagnation"    # stagnation | triple
    bse_signal_window: int = 10             # rolling window for acceptance/diversity signals
    bse_acceptance_floor: float = 0.10      # mean acceptance-rate floor for trigger-based escape
    bse_diversity_floor_frac: float = 0.35  # relative floor vs initial population radius
    bse_cauchy_enabled: bool = False        # targeted heavy-tail perturbation on escape signal
    bse_cauchy_frac: float = 0.10           # worst-fraction to perturb when triggered
    bse_cauchy_scale: float = 0.05          # perturbation scale as fraction of range

    # --- Archive (distance-thresholded; Table 11) ---
    arch_size_mult: float = 1.5             # |A| ~ mult * NPinit
    arch_dist_thresh: float = 0.05          # normalized L2 distance threshold
    arch_max_size: int | None = 200

    # --- Tiny endgame local search ---
    local_search_enabled: bool = False
    local_search_method: str = "coordinate"  # "coordinate", "nelder_mead", or "subspace_nm"
    local_search_start_frac: float = 0.95
    local_search_eval_budget_frac: float = 0.005
    local_search_elite_count: int = 2
    local_search_period: int = 1
    local_search_step_scale: float = 0.25
    local_search_min_step_frac: float = 0.001
    local_search_subspace_dim: int = 0  # 0 = auto (min(10, D//3))
    local_search_trigger_mode: str = "time"  # time | time_and_event
    local_search_stagnation_window: int = 12
    local_search_acceptance_floor: float = 0.08
    local_search_diversity_cap: float = 0.20
    local_search_score_threshold: int = 3
    local_search_coherence_window: int = 5
    local_search_coherence_min: float = 0.65
    local_search_post_restart_cooldown: int = 8
    local_search_post_ls_cooldown: int = 6

    # --- Success-Graph Structural Memory (SGSM overlay, non-RL) ---
    interaction_graph_enabled: bool = False
    interaction_graph_min_dim: int = 50
    interaction_graph_decay: float = 0.95
    interaction_graph_lr: float = 1.0
    interaction_graph_refresh_period: int = 5
    interaction_graph_warmup_frac: float = 0.10
    interaction_graph_edge_floor: float = 1e-4
    interaction_block_min_size: int = 2
    interaction_block_max_size: int = 10
    interaction_confidence_min: float = 0.55
    interaction_linkage_confidence_min: float | None = None
    interaction_ls_confidence_min: float | None = None
    interaction_linkage_mix_prob: float = 0.50
    interaction_use_for_linkage: bool = False
    interaction_use_for_local_search: bool = False
    interaction_ls_top_blocks: int = 3
    interaction_ls_dim_cap: int = 20
    interaction_min_updates: int = 10
    interaction_min_refreshes: int = 2
    interaction_min_nontrivial_dims: int = 4
    interaction_post_restart_cooldown: int = 5
    interaction_restart_decay: float = 0.50
    interaction_de_update_weight: float = 0.0
    interaction_ls_update_weight: float = 0.25
    # Runtime-safe SGSM update thinning. Defaults preserve the original every-generation update path.
    interaction_update_period: int = 1
    interaction_update_max_samples: int = 0
    # Adaptive confidence gate. Default OFF; when enabled, the linkage and LS
    # gate thresholds become the ``percentile``-quantile of the last
    # ``window`` recorded overall-confidence refreshes, clipped below by
    # ``floor``. Static ``confidence_min`` / ``*_confidence_min`` fields are
    # used only during the first ``min_samples`` refreshes (warm-up).
    interaction_confidence_adaptive: bool = False
    interaction_confidence_adaptive_window: int = 50
    interaction_confidence_adaptive_percentile: float = 0.50
    interaction_confidence_adaptive_floor: float = 0.10
    interaction_confidence_adaptive_min_samples: int = 5
    # v2 absolute-quality safeguard. When >0, reverts the gate to the static
    # threshold whenever the rolling-median confidence is below this value.
    interaction_confidence_adaptive_absolute_min: float = 0.0

    # --- TERRA-GSK prototype controls (default OFF) ---
    terra_enabled: bool = False
    budget_policy_enabled: bool = False
    budget_policy_min_evals_frac: float = 0.01
    sp_nlpsr_enabled: bool = False
    sp_nlpsr_min_subspace_samples: int = 2_147_483_647
    sp_nlpsr_release_tau: float = 1.0
    sp_nlpsr_extra_floor: int = 0
    interaction_lift_alpha: float = 1.0
    interaction_lift_lcb_z: float = 1.64
    interaction_lift_threshold: float = 0.0
    interaction_lift_min_samples: int = 12
    interaction_probe_rate: float = 0.10
    basin_memory_enabled: bool = False
    basin_memory_max_size: int = 64
    basin_memory_min_distance: float = 0.05
    basin_restart_pool_mult: int = 4
    local_search_auto_subspace: bool = False

    # --- No-null-update guarantee (engineering safeguard) ---
    force_nonzero_update: bool = True

    # ========================================================================
    # V4 — Late-budget controller scalars (D >= 100 only; default OFF/no-op).
    # All defaults reproduce the locked ``dt_gsk`` D >= 100 anchor
    # byte-for-byte (they are also in ``_ALGORITHM_EXCLUDE_KEYS``).
    #
    # ========================================================================
    # A1 — late_tau_acceptance_clip.
    late_accept_clip_enabled: bool = False
    late_accept_clip_tau_floor: float = 1.0
    late_accept_clip_acc_high: float = 1.0
    late_accept_clip_log_drop_eps: float = 0.0
    late_accept_clip_streak_k: int = 0
    late_accept_clip_strict_eps: float = 0.0
    late_accept_clip_log_drop_ema_alpha: float = 0.0
    # A2 — frozen_streak_broaden.
    frozen_broaden_enabled: bool = False
    frozen_broaden_acc_floor: float = 0.0
    frozen_broaden_log_drop_eps: float = 0.0
    frozen_broaden_streak_k: int = 0
    frozen_broaden_window_m: int = 0
    frozen_broaden_cooldown: int = 0
    frozen_broaden_factor: float = 1.0
    # FC4 — linkage_random_mix_late.
    link_random_mix_enabled: bool = False
    link_random_mix_tau_floor: float = 1.0
    link_random_mix_negative_lift: float = 0.0
    link_random_mix_severe_lift: float = 0.0
    link_random_mix_strength: float = 0.0
    link_random_mix_window: int = 0
    link_random_mix_ema_alpha: float = 0.0

    # Eigenframe final polish (opt-in; default OFF
    # keeps runs byte-identical).  From ``final_polish_start_frac`` of
    # the budget onward the incumbent best is refined once by a
    # deterministic compass search whose direction set is the eigenbasis
    # of the SGSM signed interaction matrix (coordinate axes when no
    # graph signal exists).  Consumes at most
    # ``final_polish_budget_frac`` of ``max_nfes`` through the strict
    # budget path and uses NO random draws, so RNG streams are
    # untouched whether the mechanism fires or not.
    final_polish_enabled: bool = False
    final_polish_start_frac: float = 0.985
    final_polish_budget_frac: float = 1.0
    final_polish_step_frac: float = 0.02
    final_polish_min_step_frac: float = 1e-12

    # Deep-stall full restart (multi-start) -- a standard DT-GSK mechanism.
    # When the incumbent has not improved for ``deep_stall_frac`` of the budget,
    # the WORKING population is fully re-initialised while a separate global-best
    # preserves the best-ever -- so a restart can never lose ground and CAN escape
    # a basin the BSE restart cannot (BSE structurally keeps the trapped elite).
    # Fires only on deep stalls, so productive runs (especially high-D, which stay
    # productive via SGSM/TERRA) never trigger it; RNG is drawn only when it fires.
    # Default-ON: it rescues catastrophic basin traps (e.g. CEC2017 F30 D10) and
    # is byte-identical on non-stalling runs. The ``deep_stall_min_budget`` guard
    # keeps tiny budgets (e.g. the 3000-NFE byte-stability KAT) inert, so
    # default-on is byte-safe; all real CEC runs (>= 10000*D) are far above it.
    deep_stall_restart_enabled: bool = True
    deep_stall_frac: float = 0.25
    deep_stall_cooldown_frac: float = 0.15
    deep_stall_stop_frac: float = 0.9
    deep_stall_min_budget: int = 20000

    def resolved_max_nfes(self) -> int:
        if self.max_nfes is None:
            return 10000 * int(self.dim)
        return int(self.max_nfes)

    def resolved_pop_size_init(self) -> int:
        if self.pop_size is not None:
            return int(self.pop_size)
        return int(self.np_init_mult) * int(self.dim)

    def bounds_matrix(self) -> np.ndarray:
        """Return bounds as ``(2, D)`` array.

        Supports both scalar bounds ``(lo, hi)`` and per-dimension bounds
        ``(lb_sequence, ub_sequence)`` for suites like CEC2011 where each
        dimension has different limits.
        """
        b0 = self.bounds[0]
        if isinstance(b0, (list, tuple, np.ndarray)):
            # Per-dimension bounds: bounds = (lb_array, ub_array)
            return np.vstack([
                np.asarray(self.bounds[0], dtype=np.float64),
                np.asarray(self.bounds[1], dtype=np.float64),
            ])
        lo, hi = float(b0), float(self.bounds[1])
        return np.vstack([
            np.full(int(self.dim), lo, dtype=np.float64),
            np.full(int(self.dim), hi, dtype=np.float64),
        ])


@dataclass(slots=True)
class DTGSKGenerationLog:
    """Per-generation diagnostics for DT-GSK.

    Each field answers a specific analysis question:
    - Core:      Where are we in the budget? How fast?
    - Fitness:   Is the population improving? How spread is it?
    - Accept:    Are offspring being accepted? How big are improvements?
    - Diversity: Is the population collapsing?
    - Linkage:   Does block crossover outperform per-dim crossover?
    - ACE:       Which pool entries are working? How much do they improve?
    - ARGP:      Which entries got pruned? When?
    - Coverage:  How many dimensions are updated per individual?
    """

    # --- Core ---
    gen: int                            # generation number (1-based)
    evals_used: int                     # cumulative function evaluations
    budget_frac: float                  # evals_used / max_nfes (0.0 → 1.0)
    pop_size: int                       # current population size (after NLPSR)
    generation_runtime_sec: float       # wall-clock seconds for this gen
    generation_evals_used: int          # total FEs consumed this generation
    generation_runtime_per_eval_sec: float  # generation_runtime_sec / generation_evals_used

    # --- Fitness (population health) ---
    best_fitness: float                 # best individual in population
    worst_fitness: float                # worst individual in population
    median_fitness: float               # median fitness
    mean_fitness: float                 # mean fitness
    fitness_std: float                  # std dev of fitness
    fitness_range: float                # worst - best (population spread)
    best_f_init: float                  # best fitness after initialization (constant)
    cumulative_improvement: float       # best_f_init - best_fitness (total progress so far)

    # --- Acceptance (operator effectiveness) ---
    offspring_evaluated: int            # offspring evaluated this gen
    accepted_offspring: int             # offspring that beat parent
    acceptance_rate: float              # accepted / evaluated
    best_improvement: float             # max(0, best_before_gen - best_after_gen)
    normalized_best_improvement: float  # best_improvement / (|best_before| + eps)
    mean_accepted_improvement: float    # mean(f_old - f_new) for accepted offspring
    max_accepted_improvement: float     # largest single improvement this gen
    stagnation_gens: int                # consecutive gens without best-fitness improvement

    # --- Diversity ---
    diversity_radius: float             # population radius (mean dist to centroid)
    diversity_ratio: float              # diversity_radius / initial_diversity (1.0 = init)

    # --- Linkage crossover ---
    linkage_active: bool                # is blockwise crossover active?
    linkage_block_size: int             # block size used (0 if inactive)
    linkage_group_count: int            # number of random linkage groups this gen
    linkage_rows: int                   # rows using blockwise crossover
    linkage_accepted: int               # accepted from linkage rows
    linkage_total: int                  # total linkage rows evaluated
    linkage_acc_rate: float             # linkage_accepted / linkage_total
    perdim_accepted: int                # accepted from per-dim rows
    perdim_total: int                   # total per-dim rows evaluated
    perdim_acc_rate: float              # perdim_accepted / perdim_total

    # --- ACE (per-entry analysis) ---
    ace_probs: tuple[float, ...]        # current probability per pool entry
    ace_top_probs: tuple[float, ...]    # top-half ACE probabilities (when top_bottom mode)
    ace_bottom_probs: tuple[float, ...] # bottom-half ACE probabilities (when top_bottom mode)
    ace_sample_counts: tuple[int, ...]  # individuals assigned to each entry
    ace_success_counts: tuple[int, ...] # successful individuals per entry
    ace_reward_sums: tuple[float, ...]  # total relative reward per entry
    ace_entry_acc_rate: tuple[float, ...]    # per-entry acceptance rate
    ace_entry_mean_reward: tuple[float, ...] # per-entry mean relative reward
    ace_entropy: float                  # Shannon entropy of active ACE memory
    ace_top_entropy: float              # entropy of top-half ACE memory
    ace_bottom_entropy: float           # entropy of bottom-half ACE memory
    module_prob_mass: float             # ACE probability mass on module-active entries
    modules_active: bool                # population-wide BSE gate after ACE masking
    de_sample_count: int                # individuals sampled from the DE ACE entry
    de_policy_active: bool              # whether DE override was active this gen

    # --- ARGP / escape / archive ---
    argp_frozen_entries: tuple[int, ...]   # indices of frozen pool entries
    argp_frozen_top_entries: tuple[int, ...]    # top-half frozen entries (per-half mode)
    argp_frozen_bottom_entries: tuple[int, ...] # bottom-half frozen entries (per-half mode)
    argp_rolling_acc: tuple[float, ...]    # rolling acceptance rate per entry
    argp_rolling_acc_top: tuple[float, ...] # rolling acceptance rate for top-half memory
    argp_rolling_acc_bottom: tuple[float, ...] # rolling acceptance rate for bottom-half memory
    restarts_done: int                     # cumulative restarts performed so far
    restart_triggered: bool                # whether a BSE restart fired this gen
    restart_cause: str                     # none | stagnation | triple | cauchy+restart
    archive_size: int                      # current archive cardinality
    archive_insertions: int                # archive updates performed this gen
    archive_samples_used: int              # archive-guided restart seeds this gen

    # --- Coverage ---
    mean_dim_coverage: float            # mean fraction of dims updated per individual

    # --- Local search telemetry ---
    local_search_triggered: bool        # whether LS ran this gen
    local_search_trigger_score: int     # event score for time_and_event mode
    local_search_trigger_reason: str    # concise trigger explanation
    local_search_basis_source: str      # displacements | variance | skip | none
    local_search_subspace_dim: int       # resolved subspace dim used this gen (0 if not used)
    local_search_elite_count_used: int   # elites targeted by LS this gen
    local_search_displacement_coherence: float  # coherence score in [0, 1]
    local_search_evals_used: int        # local-search FEs consumed this gen
    local_search_improvements: int      # number of elites improved this gen
    local_search_best_delta: float      # best elite improvement from LS this gen
    local_search_roi: float             # best_delta / evals_used (0 if evals_used=0)

    # --- Success-Graph Structural Memory telemetry ---
    interaction_graph_active: bool      # whether SGSM was enabled for this run/dim
    interaction_graph_density: float    # normalized off-diagonal density
    interaction_graph_block_count: int  # number of learned blocks
    interaction_graph_mean_block_confidence: float  # average internal confidence
    interaction_graph_nontrivial_dim_fraction: float  # fraction of dims in non-singleton blocks
    interaction_graph_orphan_dim_fraction: float  # dims not covered by non-singleton learned blocks
    interaction_graph_overall_confidence: float  # overall weighted block confidence
    interaction_graph_refresh_count: int  # number of block refreshes seen so far
    interaction_linkage_rows_learned: int  # linkage rows driven by learned blocks this gen
    interaction_linkage_rows_random: int  # blockwise linkage rows still using random blocks this gen
    interaction_updates_from_de: int  # accepted DE moves used for SGSM updates this gen
    interaction_updates_from_ls: int  # successful LS moves fed back into SGSM this gen
    interaction_ls_blocks_used: tuple[int, ...]  # block ids used by LS this gen
    interaction_linkage_threshold: float  # SGSM admit threshold tau_t this gen (adaptive percentile or static)
    interaction_linkage_mix_base: float  # SGSM mix base prob (config interaction_linkage_mix_prob)
    interaction_linkage_mix_eff: float  # SGSM effective mix prob this gen

    # --- Operator / diagnostic telemetry ---
    # Passive observers — fields below record what the locked-headline did
    # this gen.  All take their default-off values (0 / False) when the
    # corresponding mechanism is not engaged so the CSV stays well-formed.
    rescue_owner: int                      # 0=NONE, 1=BSE, 2=CAUCHY, 3=SR-WIDE (unified per-gen owner; BSE>CAUCHY>SR-WIDE>NONE)
    cauchy_triggered: bool                 # whether the BSE-internal Cauchy perturbation fired this gen
    bottom_widen_active: bool              # whether the bottom-half senior cone was widened this gen (v0-split path)
    junior_dominant_success_count: int     # accepted offspring with more junior than senior components in the trial mask
    senior_dominant_success_count: int     # accepted offspring with at-least-as-many senior than junior components in the trial mask
    # Per-segment SGSM learned/random acceptance breakdown (round-2 telemetry).
    # Exact row-attributed counts (uses `_build_phase4_masks` returned row
    # indices, not the first-N-rows approximation in `linkage_accepted`).
    linkage_learned_rows: int              # rows assigned to the SGSM learned-block path this gen (0 when SGSM not admitted)
    linkage_random_rows: int               # rows assigned to the random-block path this gen (== blockwise_rows when SGSM not admitted)
    linkage_learned_accepted: int          # accepted offspring from learned-block rows this gen
    linkage_random_accepted: int           # accepted offspring from random-block rows this gen
    # Boundary-repair telemetry.  The L-SHADE midpoint rule is
    # detected by exact equality with `0.5 * (pop + bound)` post-repair;
    # both the Numba fast path and the Python fallback compute bit-
    # identical scalars, so the test catches every repaired component.
    boundary_repairs_junior: int           # components in vi_junior that were repaired this gen
    boundary_repairs_senior: int           # components in vi_senior that were repaired this gen
    boundary_hit_rate: float               # (jun + sen) / (2 * NP * D) — fraction of trial components hit the bound
    # Prospective reward + intent-quality of failures.
    # `delayed_reward_lag10` is the cumulative best-f improvement over the past
    # 10 generations (window of 11 samples); zero until the window has filled.
    # `failure_alignment_*` measure cosine similarity between failed-trial
    # displacements (parent->trial) and the direction parent->current-best;
    # positive alignment fraction is the share of failures that had the right
    # intent but wrong magnitude.
    delayed_reward_lag10: float            # cumulative best-f drop over the last 10 gens
    failure_alignment_mean: float          # mean cosine alignment of failed trials with parent->best
    failure_alignment_pos_frac: float      # fraction of failed trials with positive alignment

    # --- TERRA-GSK controller telemetry ---
    terra_trust_clip_rate: float           # retained telemetry column; pinned at 0.0 since the TR-GSK governor was removed (v4.1-paper-freeze)
    terra_ls_allowed: bool                 # budget/PTR gate allowed local search this gen
    terra_escape_allowed: bool             # budget/PTR gate allowed BSE/BMNP escape this gen
    terra_linkage_lift: float              # learned-vs-random linkage acceptance lift
    terra_linkage_lcb: float               # lower confidence bound for linkage lift
    terra_linkage_reliable: bool           # SRI admit decision
    terra_basin_memory_size: int           # number of basin descriptors retained
    terra_basin_novelty_fires: int         # cumulative count of BMNP novelty-restart branch hits

    # --- Control / reproducibility ---
    run_seed: int                       # exact run seed for this trajectory
    run_config_hash: str                # stable run-level config hash
    git_commit: str                     # git revision if available, else "unknown"
    stop_reason: str | None = None      # "budget_exhausted" or None
    # --- DT2 shadow reward diagnostics (research_dt2_shadow only; 0.0 in pub) ---
    linkage_learned_reward_sum: float = 0.0  # sum of positive improvement over learned-block rows this gen
    linkage_random_reward_sum: float = 0.0   # sum of positive improvement over random-block rows this gen


@dataclass
class DTGSKResult:
    """Final result of a DT-GSK optimization run."""

    best_x: np.ndarray
    best_f: float
    nfes_used: int
    max_nfes: int
    stop_reason: str
    restarts_done: int


# =============================================================================
# RNG streams (determinism across toggles)
# =============================================================================
#
# RNGStreams is now defined in gsk.rng — re-imported above. It provides thirteen
# independent named threefry substreams derived from a single integer seed
# via counter-offset child seeding, so toggling any module ON/OFF
# cannot perturb the draws consumed by any other module.


# =============================================================================
# ACE helpers (probability learning and pool sampling)
# =============================================================================


def _ace_project_probs(p: np.ndarray, *, p_min: float) -> np.ndarray:
    """Project a vector to the probability simplex with a per-entry lower bound."""
    if ace_project_probs_fast is not None:
        return ace_project_probs_fast(p, p_min)

    v = np.asarray(p, dtype=np.float64).reshape(-1)
    n = int(v.size)
    if n <= 0:
        raise ValueError("p must be non-empty")

    p_min = float(p_min)
    if p_min < 0.0:
        p_min = 0.0

    # If the floor consumes the whole simplex, fall back to uniform.
    if p_min * n >= 1.0:
        return np.full(n, 1.0 / float(n), dtype=np.float64)

    s = 1.0 - p_min * n
    a = v - p_min

    # Standard Euclidean projection onto simplex {x>=0, sum x = s}.
    # References: Wang & Carreira-Perpinan (2013), "Projection onto the probability simplex".
    u = np.sort(a)[::-1]
    cssv = np.cumsum(u)

    rho = -1
    for j in range(n):
        t = (cssv[j] - s) / float(j + 1)
        if u[j] - t > 0:
            rho = j

    if rho == -1:
        # All entries are <= 0 after shift; distribute mass uniformly.
        x = np.full(n, s / float(n), dtype=np.float64)
    else:
        theta = (cssv[rho] - s) / float(rho + 1)
        x = np.maximum(a - theta, 0.0)

    out = x + p_min

    # Final renormalization for numerical safety.
    tot = float(np.sum(out))
    if not math.isfinite(tot) or tot <= 0.0:
        out[:] = 1.0 / float(n)
    else:
        out /= tot

    # Ensure the floor (allow tiny negative due to float error).
    if p_min > 0.0:
        out = np.maximum(out, p_min)
        out /= float(np.sum(out))

    return out


def _normalise_ace_memory_mode(mode: str) -> str:
    """Return the canonical ACE memory mode key.

    Supported modes:
      - ``single``: one global ACE probability memory (single shared memory)
      - ``top_bottom``: independent memories for top-half and bottom-half
        cohorts (dual-memory ACE)
    """

    key = str(mode).strip().lower().replace("-", "_").replace(" ", "_")
    aliases = {
        "single": "single",
        "global": "single",
        "one": "single",
        "top_bottom": "top_bottom",
        "topbottom": "top_bottom",
        "dual": "top_bottom",
        "dual_top_bottom": "top_bottom",
    }
    if key not in aliases:
        raise ValueError(
            "ace_memory_mode must be one of {'single', 'top_bottom'} "
            f"(got {mode!r})"
        )
    return aliases[key]


def _normalise_psr_schedule(mode: str) -> str:
    """Return the canonical population-reduction schedule key."""

    key = str(mode).strip().lower().replace("-", "_").replace(" ", "_")
    aliases = {
        "lpsr": "lpsr",
        "linear": "lpsr",
        "lin": "lpsr",
        "power": "power",
        "pow": "power",
        "nonlinear": "power",
        "curve": "power",
        "nlpsr": "nlpsr",
        "nl": "nlpsr",
    }
    if key not in aliases:
        raise ValueError(
            "psr_schedule must be one of {'lpsr', 'power', 'nlpsr'} "
            f"(got {mode!r})"
        )
    return aliases[key]


def _psr_target_size(*, n_init: int, n_min: int, nfes_used: int, max_nfes: int, schedule: str, alpha: float, schedule_code: int | None = None) -> int:
    """Return the target population size under the configured PSR schedule."""
    # I1: resolve schedule code first; defer schedule_key string lookup until
    # the fallback path actually needs it (numba hot path never does).
    if schedule_code is not None:
        code = schedule_code
    else:
        schedule_key_pre = _normalise_psr_schedule(schedule)
        code = {"lpsr": 0, "nlpsr": 1, "power": 2}[schedule_key_pre]
    alpha_f = float(alpha)
    if not math.isfinite(alpha_f) or alpha_f <= 0.0:
        raise ValueError(f"psr_alpha must be > 0 (got {alpha!r})")

    if psr_target_fast is not None:
        return int(psr_target_fast(int(n_init), int(n_min), int(nfes_used), int(max_nfes), code, alpha_f))

    schedule_key = ("lpsr", "nlpsr", "power")[code]
    n_init_i = int(n_init)
    n_min_i = int(n_min)
    max_nfes_i = int(max_nfes)
    if max_nfes_i <= 0:
        return max(n_min_i, n_init_i)

    frac_used = max(0.0, min(1.0, float(nfes_used) / float(max_nfes_i)))
    # S2: schedule_key and alpha_f already validated above (line 739-742).
    # Removed redundant second call to _normalise_psr_schedule and alpha_f
    # re-validation that was here before.

    if schedule_key == "lpsr":
        desired = float(n_min_i - n_init_i) / float(max_nfes_i) * float(nfes_used) + float(n_init_i)
    elif schedule_key == "nlpsr":
        # NLPSR: nonlinear x^(1-x) population size reduction.
        # NP = NP_init + (NP_min - NP_init) * x^(1-x)
        # At x=0: 0^1=0 → NP=NP_init.  At x=1: 1^0=1 → NP=NP_min.
        if frac_used <= 0.0:
            nl_ratio = 0.0
        elif frac_used >= 1.0:
            nl_ratio = 1.0
        else:
            nl_ratio = frac_used ** (1.0 - frac_used)
        desired = float(n_init_i) + float(n_min_i - n_init_i) * nl_ratio
    else:
        # power schedule
        desired = float(n_min_i) + float(n_init_i - n_min_i) * (1.0 - (frac_used ** alpha_f))

    return int(_round_half_up(desired))



def _resolve_linkage_block_size(
    *,
    dim: int,
    block_size_by_dim: dict[int, int] | None,
    strict: bool = False,
) -> int:
    """Return the configured linkage block size for the current dimension.

    When ``dim`` is not an exact key in ``block_size_by_dim``, fall back to the
    nearest configured dimension ``k <= dim`` (step-function interpolation) and
    emit a :class:`UserWarning` so the caller knows the block size was inferred.
    Previously unmapped dims silently returned ``1``, which disabled linkage
    entirely via the ``linkage_block_size > 1`` gate at the call site — a
    subtle silent-disable bug for any experiment at an arbitrary dim (e.g.,
    D=40, 60, 75, 200, 600) where the profile's intent was linkage on.

    Returns ``1`` only when the mapping is empty, absent, or no configured
    key is ``<=`` to ``dim`` (e.g., D=3 against a dict keyed at 5+).  In that
    residual case the ``linkage_min_dim`` gate typically blocks linkage too.

    When ``strict`` is True (B.8), unmapped dims raise ``ValueError`` instead
    of warning.  This is how paper/benchmark drivers opt into fail-closed
    behavior so that running at an off-profile dim cannot silently produce
    interpolated results.
    """

    if not block_size_by_dim:
        return 1
    d = int(dim)
    if d in block_size_by_dim:
        size = int(block_size_by_dim[d])
        if size < 1:
            raise ValueError(f"linkage block size must be >= 1 for dim {dim}; got {size!r}")
        return size
    # Step-function fallback: use the largest configured key k <= d.
    lower_keys = [k for k in block_size_by_dim if k <= d]
    if not lower_keys:
        if strict:
            raise ValueError(
                f"linkage_block_size_by_dim has no entry for dim={d} and no "
                f"configured key is <= {d}; mapped keys are "
                f"{sorted(block_size_by_dim.keys())!r}. Add dim={d} to the "
                "profile or disable dt_gsk_strict_profile_dims."
            )
        return 1
    nearest = max(lower_keys)
    size = int(block_size_by_dim[nearest])
    if size < 1:
        raise ValueError(
            f"linkage block size must be >= 1 for interpolated dim {dim} "
            f"(nearest key {nearest}); got {size!r}"
        )
    if strict:
        raise ValueError(
            f"linkage_block_size_by_dim has no entry for dim={d}; "
            f"nearest configured key is {nearest} (block_size={size}). "
            "Strict mode is on (dt_gsk_strict_profile_dims=True); "
            f"add dim={d} to the profile before running here."
        )
    warnings.warn(
        f"linkage_block_size_by_dim has no entry for dim={d}; "
        f"falling back to block_size={size} from nearest configured dim={nearest}. "
        f"Add dim={d} to linkage_block_size_by_dim to suppress this warning.",
        UserWarning,
        stacklevel=2,
    )
    return size


def _make_linkage_groups(*, dim: int, block_size: int, rng: np.random.Generator) -> list[np.ndarray]:
    """Create a random partition of dimensions into linkage blocks."""

    d = int(dim)
    b = int(block_size)
    if d <= 0:
        raise ValueError(f"dim must be positive (got {dim!r})")
    if b <= 1 or b >= d:
        return [np.arange(d, dtype=np.int64)] if b >= d else [np.arange(i, min(i + 1, d), dtype=np.int64) for i in range(d)]

    dims = np.asarray(rng.permutation(d), dtype=np.int64)

    groups: list[np.ndarray] = []
    for start in range(0, d, b):
        groups.append(np.sort(dims[start : min(start + b, d)]))
    return groups


def _build_phase4_masks(
    *,
    rng_core: np.random.Generator,
    rng_link: np.random.Generator,
    NP: int,
    D: int,
    p_junior_i: np.ndarray,
    KR_i: np.ndarray,
    linkage_active: bool,
    linkage_groups: list[np.ndarray] | None,
    linkage_mix_prob: float,
    linkage_groups_secondary: list[np.ndarray] | None = None,
    linkage_primary_row_prob: float = 1.0,
    _dj_buf: np.ndarray | None = None,
    _ds_buf: np.ndarray | None = None,
    _link_flat: np.ndarray | None = None,
    _link_offsets: np.ndarray | None = None,
    _link_flat_secondary: np.ndarray | None = None,
    _link_offsets_secondary: np.ndarray | None = None,
) -> tuple[np.ndarray, np.ndarray, int, int, np.ndarray, np.ndarray]:
    """Build junior/senior crossover masks with optional mixed blockwise linkage.

    Returns
    -------
    D_J, D_S, n_blockwise_rows, n_primary_rows, primary_rows, secondary_rows
        Boolean junior/senior masks, the total number of blockwise rows, the
        subset count driven by ``linkage_groups`` (the primary group set), and
        two int64 row-index arrays naming exactly which population rows were
        assigned to the primary (learned) and secondary (random) blockwise
        paths this gen.  When linkage is inactive both index arrays are empty.
        The row-index arrays support per-segment telemetry — they let the
        caller compute per-segment acceptance breakdowns without re-drawing
        from ``rng_link``.
    """

    # Fast path: callers typically pass contiguous float64 (NP,) arrays.
    # Skip ``np.asarray`` + ``reshape`` when shape and dtype already match.
    _NP = int(NP)
    if (
        isinstance(p_junior_i, np.ndarray)
        and p_junior_i.dtype == np.float64
        and p_junior_i.shape == (_NP,)
    ):
        p_jun = p_junior_i
    else:
        p_jun = np.asarray(p_junior_i, dtype=np.float64).reshape(_NP)
    if (
        isinstance(KR_i, np.ndarray)
        and KR_i.dtype == np.float64
        and KR_i.shape == (_NP,)
    ):
        kr = KR_i
    else:
        kr = np.asarray(KR_i, dtype=np.float64).reshape(_NP)

    if not linkage_active or not linkage_groups or int(D) < 1:
        # W2.1 (2026-07-25, author-authorized _rng_3buf realization): ONE fused
        # flat draw replaces three separate (N, D) draws. Bit-identical BY
        # CONSTRUCTION: a shaped draw (N, D) is _draw(N*D) followed by
        # reshape(D, N).swapaxes -- element [i, j] is the stream double at
        # start + j*N + i -- and _draw is concatenation-consistent
        # (_draw(a) then _draw(b) consumes exactly the stream positions of
        # _draw(a+b): Threefry doubles are a pure function of block index with
        # the reservoir carrying partial-block tails; so segment k of the fused
        # draw occupies exactly draw k's absolute positions, the identical
        # reshape maps every element to the same 8 bytes, and the generator's
        # end state (counter + unconsumed tail) is unchanged). The views below
        # have the same F-order layout the shaped draws returned, so downstream
        # numba kernels see identical arrays. Removes 2 Python->kernel draw
        # dispatches and 2 allocations per generation.
        _n3 = NP * D
        _flat3 = rng_core.random(3 * _n3)
        rands_j = _flat3[:_n3].reshape(D, NP).T
        rands_jg = _flat3[_n3:2 * _n3].reshape(D, NP).T
        rands_sg = _flat3[2 * _n3:].reshape(D, NP).T
        if build_masks_scalar_fast is not None:
            if _dj_buf is not None and _ds_buf is not None:
                D_J = _dj_buf[:NP, :D]
                D_S = _ds_buf[:NP, :D]
                D_J[:] = False
                D_S[:] = False
            else:
                D_J = np.zeros((NP, D), dtype=np.bool_)
                D_S = np.zeros((NP, D), dtype=np.bool_)
            build_masks_scalar_fast(rands_j, rands_jg, rands_sg,
                                     p_jun, kr, NP, D, D_J, D_S)
        else:
            D_J_base = np.less_equal(rands_j, p_jun.reshape(NP, 1))
            J_gate = np.less_equal(rands_jg, kr.reshape(NP, 1))
            S_gate = np.less_equal(rands_sg, kr.reshape(NP, 1))
            D_J = np.logical_and(D_J_base, J_gate)
            D_S = np.logical_and(~D_J_base, S_gate)
        _empty_idx = np.empty((0,), dtype=np.int64)
        return D_J, D_S, 0, 0, _empty_idx, _empty_idx

    mix = float(linkage_mix_prob)
    if not math.isfinite(mix) or mix < 0.0 or mix > 1.0:
        raise ValueError(f"linkage_block_mix_prob must be in [0, 1] (got {linkage_mix_prob!r})")

    primary_row_prob = float(linkage_primary_row_prob)
    if not math.isfinite(primary_row_prob) or primary_row_prob < 0.0 or primary_row_prob > 1.0:
        raise ValueError(f"linkage_primary_row_prob must be in [0, 1] (got {linkage_primary_row_prob!r})")

    if mix <= 0.0:
        return _build_phase4_masks(
            rng_core=rng_core,
            rng_link=rng_link,
            NP=NP,
            D=D,
            p_junior_i=p_jun,
            KR_i=kr,
            linkage_active=False,
            linkage_groups=None,
            linkage_mix_prob=0.0,
            _dj_buf=_dj_buf,
            _ds_buf=_ds_buf,
        )

    if mix >= 1.0:
        block_rows = np.ones((NP,), dtype=bool)
    else:
        block_rows = rng_link.random(NP) <= mix

    if _dj_buf is not None and _ds_buf is not None:
        D_J = _dj_buf[:NP, :D]
        D_S = _ds_buf[:NP, :D]
        D_J[:] = False
        D_S[:] = False
    else:
        D_J = np.zeros((NP, D), dtype=bool)
        D_S = np.zeros((NP, D), dtype=bool)

    scalar_rows = ~block_rows
    if np.any(scalar_rows):
        rows = np.nonzero(scalar_rows)[0]
        n_scalar = int(rows.size)
        # W2.1: fused flat draw -- same by-construction argument as the
        # linkage-off branch above (segment k == shaped draw k, bit-for-bit).
        _n3 = n_scalar * D
        _flat3 = rng_core.random(3 * _n3)
        rands_j = _flat3[:_n3].reshape(D, n_scalar).T
        rands_jg = _flat3[_n3:2 * _n3].reshape(D, n_scalar).T
        rands_sg = _flat3[2 * _n3:].reshape(D, n_scalar).T
        if build_masks_scalar_rows_fast is not None:
            build_masks_scalar_rows_fast(
                rands_j,
                rands_jg,
                rands_sg,
                p_jun,
                kr,
                rows,
                n_scalar,
                D,
                D_J,
                D_S,
            )
        else:
            D_J_base_sub = rands_j <= p_jun[rows].reshape(n_scalar, 1)
            J_gate_sub = rands_jg <= kr[rows].reshape(n_scalar, 1)
            S_gate_sub = rands_sg <= kr[rows].reshape(n_scalar, 1)
            D_J[rows, :] = np.logical_and(D_J_base_sub, J_gate_sub)
            D_S[rows, :] = np.logical_and(~D_J_base_sub, S_gate_sub)

    def _flatten_groups(groups: list[np.ndarray], flat: np.ndarray | None, offsets: np.ndarray | None) -> tuple[np.ndarray, np.ndarray]:
        if flat is not None and offsets is not None:
            return flat, offsets
        n_groups = len(groups)
        group_sizes = np.empty(n_groups, dtype=np.int64)
        for g in range(n_groups):
            group_sizes[g] = int(groups[g].size)
        group_offsets = np.empty(n_groups + 1, dtype=np.int64)
        group_offsets[0] = 0
        if n_groups > 0:
            np.cumsum(group_sizes, out=group_offsets[1:])
            total = int(group_offsets[-1])
            groups_flat = np.empty(total, dtype=np.int64)
            for g in range(n_groups):
                s = int(group_offsets[g])
                e = int(group_offsets[g + 1])
                groups_flat[s:e] = groups[g]
        else:
            groups_flat = np.empty((0,), dtype=np.int64)
        return groups_flat, group_offsets

    def _apply_blockwise_rows(rows: np.ndarray, groups: list[np.ndarray], *, flat: np.ndarray | None, offsets: np.ndarray | None) -> None:
        if rows.size == 0 or not groups:
            return
        n_block = int(rows.size)
        n_groups = len(groups)
        rands_block_jun = rng_link.random((n_block, n_groups))
        rands_block_gate = rng_link.random((n_block, n_groups))
        p_jun_block = p_jun[rows]
        kr_block = kr[rows]
        if build_masks_blockwise_fast is not None:
            groups_flat, group_offsets = _flatten_groups(groups, flat, offsets)
            build_masks_blockwise_fast(
                rands_block_jun,
                rands_block_gate,
                p_jun_block,
                kr_block,
                rows,
                groups_flat,
                group_offsets,
                D_J,
                D_S,
            )
        else:
            block_jun = rands_block_jun <= p_jun_block.reshape(n_block, 1)
            block_gate = rands_block_gate <= kr_block.reshape(n_block, 1)
            block_sen = np.logical_not(block_jun)
            for g, dims in enumerate(groups):
                take_j = np.logical_and(block_jun[:, g], block_gate[:, g])
                if np.any(take_j):
                    D_J[rows[take_j][:, None], dims.reshape(1, -1)] = True
                take_s = np.logical_and(block_sen[:, g], block_gate[:, g])
                if np.any(take_s):
                    D_S[rows[take_s][:, None], dims.reshape(1, -1)] = True

    n_blockwise_rows = int(np.sum(block_rows))
    n_primary_rows = 0
    primary_rows = np.empty((0,), dtype=np.int64)
    secondary_rows = np.empty((0,), dtype=np.int64)
    if n_blockwise_rows > 0:
        block_row_idx = np.asarray(np.nonzero(block_rows)[0], dtype=np.int64)
        if linkage_groups_secondary and primary_row_prob < 1.0:
            primary_mask = rng_link.random(n_blockwise_rows) <= primary_row_prob
            primary_rows = block_row_idx[primary_mask]
            secondary_rows = block_row_idx[~primary_mask]
        else:
            primary_rows = block_row_idx
            secondary_rows = np.empty((0,), dtype=np.int64)
        n_primary_rows = int(primary_rows.size)
        _apply_blockwise_rows(primary_rows, linkage_groups, flat=_link_flat, offsets=_link_offsets)
        if secondary_rows.size > 0 and linkage_groups_secondary:
            _apply_blockwise_rows(secondary_rows, linkage_groups_secondary, flat=_link_flat_secondary, offsets=_link_offsets_secondary)

    return D_J, D_S, n_blockwise_rows, n_primary_rows, primary_rows, secondary_rows

def _ace_sample_indices(rng: np.random.Generator, probs: np.ndarray, *, n: int) -> np.ndarray:
    """Roulette-wheel sampling from a probability vector."""
    # I3: skip asarray when probs is already a 1-D float64 ndarray (typical
    # hot-path caller). Compute n once.
    if not (isinstance(probs, np.ndarray) and probs.dtype == np.float64 and probs.ndim == 1):
        probs = np.asarray(probs, dtype=np.float64)
        if probs.ndim != 1:
            raise ValueError("probs must be 1D")
    if probs.size == 0:
        raise ValueError("probs must be non-empty")
    n_i = int(n)
    if n_i <= 0:
        return np.zeros((0,), dtype=np.int64)

    u = rng.random(n_i)

    if ace_sample_fast is not None:
        return ace_sample_fast(probs, u)

    # CDF
    cdf = np.cumsum(probs)
    cdf[-1] = 1.0

    # Match the Numba fast path's left-closed bin semantics so an exact
    # CDF-boundary draw lands in the same ACE entry on both paths.
    idx = np.searchsorted(cdf, u, side="left").astype(np.int64)
    idx = np.clip(idx, 0, probs.size - 1)
    return idx


def _ace_update_probs(
    Kw: np.ndarray,
    omega: np.ndarray,
    *,
    c: float,
    p_min: float,
) -> np.ndarray:
    """Update ACE probabilities using EMA-based adaptation with
    per-entry fitness-delta signals and probability floor.

    The spec reports:

      ω_ps = sum_i ( f(x_new_i) - f(x_old_i) )
      Δ_ps = max(p_min, ω_ps / sum_ps ω_ps)
      Kw_{g+1} = (1-c) Kw_g + c Δ

    Notes
    -----
    - For minimization, improvements make (f_new - f_old) negative.
      If most settings improve, sum(ω) is negative and the ratio remains
      positive.
    - If sum(ω) is 0 or non-finite, we skip the update (deterministic).
    """

    Kw = np.asarray(Kw, dtype=np.float64).copy()
    omega = np.asarray(omega, dtype=np.float64)

    if Kw.ndim != 1 or omega.ndim != 1 or Kw.size != omega.size:
        raise ValueError("Kw and omega must be 1D vectors of the same length")

    if ace_update_full_fast is not None:
        return ace_update_full_fast(Kw, omega, float(c), float(p_min))

    s = float(np.sum(omega))
    if not math.isfinite(s) or s == 0.0:
        return _ace_project_probs(Kw, p_min=float(p_min))

    # When sum(omega) > 0 the population worsened overall.  The ratio
    # omega_ps / sum(omega) is then *inverted*: settings that worsened most
    # get the largest positive ratios while settings that improved get
    # negative ratios (floored to p_min).  This rewards the worst settings
    # and punishes the best — the opposite of what we want.
    #
    # NEW-004 refinement: instead of skipping entirely when s >= 0, extract
    # the subset of settings that actually improved (omega < 0) and compute
    # the target from that subset alone.  This lets ACE continue adapting
    # even on hard problems where improvements are sparse.
    if s >= 0.0:
        improved = omega < 0.0
        if not np.any(improved):
            # No setting improved at all — nothing to learn from.
            return _ace_project_probs(Kw, p_min=float(p_min))
        # Zero out non-improved settings and compute target from improved only.
        omega_imp = np.where(improved, omega, 0.0)
        s_imp = float(np.sum(omega_imp))
        if s_imp == 0.0 or not math.isfinite(s_imp):
            return _ace_project_probs(Kw, p_min=float(p_min))
        target = omega_imp / s_imp
    else:
        target = omega / s
    # Floor + renormalize.
    target = _ace_project_probs(target, p_min=float(p_min))

    Kw = (1.0 - float(c)) * Kw + float(c) * target
    Kw = _ace_project_probs(Kw, p_min=float(p_min))
    return Kw


def _argp_update_memory_probs(
    probs: np.ndarray,
    frozen_mask: np.ndarray,
    rolling_acc: np.ndarray,
    total_samp: np.ndarray,
    *,
    threshold: float,
    p_min: float,
    min_active: int = 2,
) -> tuple[np.ndarray, np.ndarray]:
    """Freeze/unfreeze one ACE memory and redistribute mass.

    This helper powers the split-memory ARGP path. It intentionally does not
    alter the legacy shared-memory path so feature-off behavior remains exactly
    as before.
    """
    probs = np.asarray(probs, dtype=np.float64).copy()
    frozen = np.asarray(frozen_mask, dtype=bool).copy()
    rolling = np.asarray(rolling_acc, dtype=np.float64).reshape(-1)
    samp = np.asarray(total_samp, dtype=np.float64).reshape(-1)
    if probs.ndim != 1 or frozen.ndim != 1 or probs.shape != frozen.shape:
        raise ValueError("probs and frozen_mask must be 1D vectors of equal length")
    if rolling.shape != probs.shape or samp.shape != probs.shape:
        raise ValueError("rolling_acc and total_samp must match probs shape")

    n_unfrozen = int(np.sum(~frozen))
    for k in range(int(probs.size)):
        if frozen[k]:
            continue
        if n_unfrozen <= int(min_active):
            break
        if rolling[k] < float(threshold):
            frozen[k] = True
            n_unfrozen -= 1

    for k in range(int(probs.size)):
        if frozen[k] and samp[k] > 0.0 and rolling[k] >= float(threshold):
            frozen[k] = False

    probs = _argp_redistribute_probs(probs, frozen, p_min=float(p_min))
    return probs, frozen


def _argp_update_memory_probs_guarded(
    probs: np.ndarray,
    frozen_mask: np.ndarray,
    rolling_acc: np.ndarray,
    total_samp: np.ndarray,
    low_streak: np.ndarray,
    *,
    threshold: float,
    p_min: float,
    min_active: int = 2,
    confirm_windows: int = 1,
    max_frozen_frac: float = 1.0,
    frozen_prob_floor: float | None = None,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Guarded split-memory ARGP update.

    This path is opt-in. It keeps the legacy immediate-freeze helper unchanged
    and adds three conservative controls for exploratory screens:
    confirmation windows, a per-memory frozen-count cap, and a soft-freeze
    probability floor above ``p_min``.
    """
    probs = np.asarray(probs, dtype=np.float64).copy()
    frozen = np.asarray(frozen_mask, dtype=bool).copy()
    rolling = np.asarray(rolling_acc, dtype=np.float64).reshape(-1)
    samp = np.asarray(total_samp, dtype=np.float64).reshape(-1)
    streak = np.asarray(low_streak, dtype=np.int64).copy().reshape(-1)
    if probs.ndim != 1 or frozen.ndim != 1 or probs.shape != frozen.shape:
        raise ValueError("probs and frozen_mask must be 1D vectors of equal length")
    if rolling.shape != probs.shape or samp.shape != probs.shape or streak.shape != probs.shape:
        raise ValueError("rolling_acc, total_samp, and low_streak must match probs shape")

    n = int(probs.size)
    min_active_i = max(1, int(min_active))
    confirm_i = max(1, int(confirm_windows))
    max_frac = max(0.0, min(1.0, float(max_frozen_frac)))
    if max_frac >= 1.0:
        max_frozen = max(0, n - min_active_i)
    else:
        max_frozen = min(max(0, int(math.floor(max_frac * n))), max(0, n - min_active_i))

    n_unfrozen = int(np.sum(~frozen))
    n_frozen = int(np.sum(frozen))
    for k in range(n):
        if frozen[k]:
            continue
        if samp[k] > 0.0 and rolling[k] < float(threshold):
            streak[k] += 1
        else:
            streak[k] = 0
        if n_unfrozen <= min_active_i or n_frozen >= max_frozen:
            continue
        if streak[k] >= confirm_i:
            frozen[k] = True
            streak[k] = 0
            n_unfrozen -= 1
            n_frozen += 1

    for k in range(n):
        if frozen[k] and samp[k] > 0.0 and rolling[k] >= float(threshold):
            frozen[k] = False
            streak[k] = 0

    floor = float(p_min) if frozen_prob_floor is None else max(float(p_min), float(frozen_prob_floor))
    probs = _argp_redistribute_probs(probs, frozen, p_min=float(p_min), frozen_prob_floor=floor)
    return probs, frozen, streak


# Public wrappers for unit tests

def ace_sample_indices(rng: np.random.Generator, probs: np.ndarray, n: int) -> np.ndarray:
    return _ace_sample_indices(rng, probs, n=n)


def ace_update_probs(Kw_P: np.ndarray, omega: np.ndarray, *, c: float, p_min: float) -> np.ndarray:
    return _ace_update_probs(Kw_P, omega, c=c, p_min=p_min)


# =============================================================================
# Diversity metric (Rad(X)) and heavy-tail noise
# =============================================================================


def population_radius(pop: np.ndarray, span: np.ndarray) -> float:
    """Compute Rad(X) ≈ mean_i ||x_i - x̄||_2 / ||span||_2."""
    if population_radius_fast is not None:
        return population_radius_fast(pop, span)
    pop = np.asarray(pop, dtype=np.float64)
    if pop.ndim != 2:
        raise ValueError("pop must be 2D")
    if pop.shape[0] <= 1:
        return 0.0

    span = np.asarray(span, dtype=np.float64)
    denom = float(np.linalg.norm(span))
    if denom <= 0.0 or not math.isfinite(denom):
        return 0.0

    mu = np.mean(pop, axis=0)
    d = pop - mu
    dist = np.linalg.norm(d, axis=1)
    rad = float(np.mean(dist) / denom)

    # Numeric safety: clamp to [0, 1].
    if not math.isfinite(rad):
        return 0.0
    return max(0.0, min(1.0, rad))


def cauchy_like(rng: np.random.Generator, n: int, d: int) -> np.ndarray:
    """Generate Cauchy-like heavy-tail noise using inverse-CDF tan(pi(u-0.5))."""
    if n <= 0 or d <= 0:
        return np.zeros((max(0, n), max(0, d)), dtype=np.float64)
    u = rng.random((int(n), int(d)))
    # Avoid exactly 0 or 1 to prevent inf; PCG64 produces [0, 1) in practice,
    # but clamp defensively.
    u = np.clip(u, 1e-15, 1.0 - 1e-15)
    return np.tan(np.pi * (u - 0.5))


def _normalise_local_search_start_frac(x: float) -> float:
    """Clamp local-search start fraction to [0, 1]."""
    x = float(x)
    if not math.isfinite(x):
        raise ValueError("local_search_start_frac must be finite")
    return max(0.0, min(1.0, x))


def _normalise_local_search_trigger_mode(mode: str) -> str:
    """Return canonical local-search trigger mode."""
    key = str(mode).strip().lower().replace("-", "_").replace(" ", "_")
    aliases = {
        "time": "time",
        "schedule": "time",
        "scheduled": "time",
        "time_and_event": "time_and_event",
        "event": "time_and_event",
        "event_driven": "time_and_event",
        "time_event": "time_and_event",
    }
    if key not in aliases:
        raise ValueError(
            "local_search_trigger_mode must be one of {'time', 'time_and_event'} "
            f"(got {mode!r})"
        )
    return aliases[key]


def _normalise_local_search_method(method: str) -> str:
    """Return canonical local-search method and fail fast on typos."""
    key = str(method).strip().lower().replace("-", "_").replace(" ", "_")
    aliases = {
        "coordinate": "coordinate",
        "coord": "coordinate",
        "nelder_mead": "nelder_mead",
        "nelder": "nelder_mead",
        "nm": "nelder_mead",
        "subspace_nm": "subspace_nm",
        "subspace": "subspace_nm",
        "subspace_nelder_mead": "subspace_nm",
        "snm": "subspace_nm",
    }
    if key not in aliases:
        raise ValueError(
            "local_search_method must be one of {'coordinate', 'nelder_mead', 'subspace_nm'} "
            f"(got {method!r})"
        )
    return aliases[key]


def _normalise_local_search_score_threshold(x: int) -> int:
    """Validate event-trigger threshold for the four LS trigger signals."""
    value = int(x)
    if value < 1 or value > 4:
        raise ValueError(
            f"local_search_score_threshold must be in [1, 4] because the trigger has 4 signals (got {x!r})"
        )
    return value


def _normalise_ace_module_gate_mode(mode: str) -> str:
    key = str(mode).strip().lower().replace("-", "_").replace(" ", "_")
    aliases = {"static": "static", "fixed": "static", "hysteresis": "hysteresis"}
    if key not in aliases:
        raise ValueError(
            "ace_module_gate_mode must be one of {'static', 'hysteresis'} "
            f"(got {mode!r})"
        )
    return aliases[key]


def _normalise_ace_de_policy_mode(mode: str) -> str:
    key = str(mode).strip().lower().replace("-", "_").replace(" ", "_")
    aliases = {"static": "static", "fixed": "static", "state": "state", "stateful": "state"}
    if key not in aliases:
        raise ValueError(
            "ace_de_policy_mode must be one of {'static', 'state'} "
            f"(got {mode!r})"
        )
    return aliases[key]


def _normalise_argp_freeze_scope(scope: str) -> str:
    key = str(scope).strip().lower().replace("-", "_").replace(" ", "_")
    aliases = {"shared": "shared", "global": "shared", "per_half": "per_half", "perhalf": "per_half"}
    if key not in aliases:
        raise ValueError(
            "argp_freeze_scope must be one of {'shared', 'per_half'} "
            f"(got {scope!r})"
        )
    return aliases[key]


def _validate_unit_interval(name: str, x: float) -> float:
    value = float(x)
    if not math.isfinite(value) or value < 0.0 or value > 1.0:
        raise ValueError(f"{name} must be finite and in [0, 1] (got {x!r})")
    return value


def _validate_hysteresis_bounds(*, low: float, high: float) -> tuple[float, float]:
    low_f = _validate_unit_interval("ace_module_gate_low", low)
    high_f = _validate_unit_interval("ace_module_gate_high", high)
    if low_f > high_f:
        raise ValueError(
            f"ace_module_gate_low must be <= ace_module_gate_high (got {low!r} > {high!r})"
        )
    return low_f, high_f


def _entropy_prob(p: np.ndarray) -> float:
    """Return Shannon entropy of a probability vector."""
    q = np.asarray(p, dtype=np.float64).reshape(-1)
    if q.size == 0:
        return 0.0
    q = q[q > 0.0]
    if q.size == 0:
        return 0.0
    return float(-np.sum(q * np.log(q)))


def _displacement_coherence(displacements: list[np.ndarray], *, window: int) -> float:
    """Return a structure score in [0, 1] from recent successful displacements.

    Uses the explained-energy ratio of the first singular direction, which is
    robust to sign flips (unlike a simple vector mean). A value near 1 means
    recent successful steps align strongly with a single local subspace.
    """
    if not displacements:
        return 0.0
    w = max(1, int(window))
    n = min(len(displacements), w)
    if n < 2:
        return 0.0
    mat = np.asarray(displacements[-n:], dtype=np.float64)
    if mat.ndim != 2 or mat.shape[0] < 2:
        return 0.0
    try:
        _u, s, _vt = np.linalg.svd(mat, full_matrices=False)
    except np.linalg.LinAlgError:
        return 0.0
    if s.size == 0:
        return 0.0
    energy = float(np.sum(s * s))
    if energy <= 0.0 or not math.isfinite(energy):
        return 0.0
    return max(0.0, min(1.0, float((s[0] * s[0]) / energy)))


def _argp_redistribute_probs(
    probs: np.ndarray,
    frozen_mask: np.ndarray,
    *,
    p_min: float,
    frozen_prob_floor: float | None = None,
) -> np.ndarray:
    """Redistribute ACE probabilities while pinning frozen entries to a floor.

    This helper is used only in the split-memory ARGP path. The legacy shared
    path intentionally keeps its original inline implementation to preserve
    bit-level feature-off behavior.
    """
    out = np.asarray(probs, dtype=np.float64).copy()
    frozen = np.asarray(frozen_mask, dtype=bool).reshape(-1)
    if out.ndim != 1 or frozen.shape != out.shape:
        raise ValueError("probs and frozen_mask must be 1D with the same shape")
    if not np.any(frozen):
        return _ace_project_probs(out, p_min=p_min)

    n = int(out.size)
    p_floor = max(0.0, float(p_min))
    frozen_floor = p_floor if frozen_prob_floor is None else max(p_floor, float(frozen_prob_floor))
    if p_floor * n >= 1.0:
        return np.full(n, 1.0 / float(n), dtype=np.float64)

    n_frozen = int(np.sum(frozen))
    unfrozen = ~frozen
    n_unfrozen = int(np.sum(unfrozen))
    if frozen_floor <= p_floor + 1e-15:
        remaining = 1.0 - float(n_frozen) * p_floor
        out[frozen] = p_floor
        if remaining <= 0.0 or not np.any(unfrozen):
            return np.full(n, 1.0 / float(n), dtype=np.float64)

        unfrozen_sum = float(np.sum(out[unfrozen]))
        if unfrozen_sum > 0.0 and math.isfinite(unfrozen_sum):
            out[unfrozen] *= remaining / unfrozen_sum
        else:
            out[unfrozen] = remaining / float(np.sum(unfrozen))
        return _ace_project_probs(out, p_min=p_floor)

    min_mass = (float(n_frozen) * frozen_floor) + (float(n_unfrozen) * p_floor)
    if min_mass > 1.0:
        return np.full(n, 1.0 / float(n), dtype=np.float64)

    remaining = 1.0 - float(n_frozen) * frozen_floor
    out[frozen] = frozen_floor
    if remaining <= 0.0 or not np.any(unfrozen):
        return np.full(n, 1.0 / float(n), dtype=np.float64)

    unfrozen_floor = p_floor / remaining if remaining > 0.0 else 0.0
    out[unfrozen] = _ace_project_probs(out[unfrozen], p_min=unfrozen_floor) * remaining

    # Repair tiny floating-point residuals without touching frozen entries.
    residual = 1.0 - float(np.sum(out))
    if abs(residual) > 1e-14 and np.any(unfrozen):
        unfrozen_idx = np.flatnonzero(unfrozen)
        out[unfrozen_idx[int(np.argmax(out[unfrozen]))]] += residual
    return out


# =============================================================================
# Archive (distance-thresholded diverse elites)
# =============================================================================


@dataclass
class EliteArchive:
    """Distance-thresholded archive of diverse elite solutions.

    The archive stores a bounded collection of high-quality solutions that are
    *spread out* across the search space.  It serves two purposes:

    1. **Restart seeding (BSE):** When the optimizer stagnates, new points are
       generated near archived solutions rather than purely at random, giving
       the restart a head-start in promising regions.

    2. **Diversity preservation:** The distance threshold prevents the archive
       from collapsing to a single basin.  When the archive is full, the
       NEW-002 diversity-based pruning removes the *closest* pair rather than
       the worst-fitness entry, maximising spatial coverage.

    Distance metric:
        Normalized L2: d(a,b) = ||diag(1/span) · (a-b)|| / sqrt(D)
        This makes the threshold scale-invariant across dimensions and bounds.

    Lifecycle:
        1. Created at optimizer init with ``EliteArchive.create(...)``.
        2. ``consider(x, f)`` is called after every accepted improvement.
        3. ``sample(rng)`` is called by BSE when generating restart points.

    Key parameters (from DTGSKConfig):
        arch_size_mult (default 5.0):   |A| = round(mult × NP_init)
        arch_dist_thresh (default 0.05): Minimum normalized distance to add.

    Implementation note:
        Archive vectors are stored in a pre-allocated (max_size, D) numpy
        array.  All distance computations are fully vectorized — no Python
        loops over archive entries.
    """

    dim: int
    max_size: int
    dist_thresh: float

    _inv_span: np.ndarray     # (D,) precomputed 1/span (0 where span==0)
    _inv_sqrt_d: float        # 1/sqrt(D) precomputed
    _xs: np.ndarray           # (max_size, D) pre-allocated storage
    _fs: np.ndarray           # (max_size,) fitness values
    _n: int                   # current number of entries

    @classmethod
    def create(
        cls,
        *,
        dim: int,
        span: np.ndarray,
        max_size: int,
        dist_thresh: float,
    ) -> EliteArchive:
        span = np.asarray(span, dtype=np.float64)
        safe_span = np.where(span > 0.0, span, 1.0)
        inv_span = np.where(span > 0.0, 1.0 / safe_span, 0.0)
        cap = max(1, int(max_size))
        return cls(
            dim=int(dim),
            max_size=cap,
            dist_thresh=float(dist_thresh),
            _inv_span=inv_span,
            _inv_sqrt_d=1.0 / np.sqrt(float(dim)) if dim > 0 else 1.0,
            _xs=np.empty((cap, int(dim)), dtype=np.float64),
            _fs=np.full((cap,), np.inf, dtype=np.float64),
            _n=0,
        )

    def __len__(self) -> int:
        return self._n

    def _dists_to(self, x: np.ndarray) -> np.ndarray:
        """Vectorized normalized L2 distances from *x* to all archive entries."""
        if self._n == 0:
            return np.empty((0,), dtype=np.float64)
        if archive_dists_fast is not None:
            return archive_dists_fast(self._xs, self._n, x,
                                      self._inv_span, self._inv_sqrt_d)
        diff = (self._xs[:self._n, :] - x) * self._inv_span
        return np.asarray(np.sqrt(np.sum(diff * diff, axis=1)) * self._inv_sqrt_d, dtype=np.float64)

    def consider(self, x: np.ndarray, f: float) -> bool:
        """Consider adding (x,f) if far enough from existing archive."""
        if self.max_size <= 0:
            return False
        x = np.asarray(x, dtype=np.float64).ravel()
        f = float(f)
        if not math.isfinite(f):
            return False

        if archive_consider_fast is not None:
            changed, new_n = archive_consider_fast(
                self._xs, self._fs, self._n, self.max_size,
                x, f, self._inv_span, self._inv_sqrt_d, self.dist_thresh)
            self._n = int(new_n)
            return bool(changed)

        # Distance-thresholding (vectorized).
        if self._n > 0:
            dists = self._dists_to(x)
            if np.any(dists < self.dist_thresh):
                return False

        # Append.
        if self._n < self.max_size:
            self._xs[self._n, :] = x
            self._fs[self._n] = f
            self._n += 1
            return True

        # Archive full → NEW-002 diversity-based pruning:
        # Temporarily add to end, find closest pair involving the new
        # point, remove the other member of that pair.
        #
        # Since we already computed dists above (or archive was empty),
        # just find closest existing entry to the new point.
        dists = self._dists_to(x)
        j = int(np.argmin(dists))
        # Replace the closest entry with the new point.
        self._xs[j, :] = x
        self._fs[j] = f
        return True

    def consider_batch(self, X: np.ndarray, F: np.ndarray) -> int:
        """H7: batched ``consider`` over a (K, D) candidate matrix.

        Each row is processed sequentially against the live archive,
        preserving the same semantics as a Python ``for`` loop of
        :meth:`consider` calls but eliminating per-call boundary overhead
        when the JIT fast path is available.

        Returns the number of insertions made.
        """
        if self.max_size <= 0:
            return 0
        if X.size == 0:
            return 0
        X = np.ascontiguousarray(X, dtype=np.float64)
        F = np.ascontiguousarray(F, dtype=np.float64).ravel()
        if X.ndim != 2 or X.shape[1] != self.dim:
            raise ValueError(f"consider_batch expects (K, {self.dim}), got {X.shape}")
        if F.shape[0] != X.shape[0]:
            raise ValueError("consider_batch X/F row mismatch")

        if archive_consider_batch_fast is not None:
            n_inserted, new_n = archive_consider_batch_fast(
                self._xs, self._fs, self._n, self.max_size,
                X, F, self._inv_span, self._inv_sqrt_d, self.dist_thresh,
            )
            self._n = int(new_n)
            return int(n_inserted)

        # Pure-Python fallback — sequential consider().
        inserted = 0
        for k in range(X.shape[0]):
            if self.consider(X[k, :], float(F[k])):
                inserted += 1
        return inserted

    def sample(self, rng: np.random.Generator) -> tuple[np.ndarray, float] | None:
        """Sample one archive element uniformly."""
        if self._n == 0:
            return None
        j = int(rng.integers(0, self._n))
        return self._xs[j, :].copy(), float(self._fs[j])


# =============================================================================
# Stagnation detector (BSE)
# =============================================================================


@dataclass
class StagnationDetector:
    """Sliding-window stagnation detector for the BSE (Budget-Safe Escape) module.

    Monitors the best-so-far fitness over the last W generations.  If the
    improvement over the window is less than epsilon (relative to the older
    value), the detector fires and BSE may trigger a partial restart.

    How it works:
        Window stores the last W+1 best_f values.  Each generation,
        ``push(best_f)`` appends the current best.  ``triggered()`` returns
        True when:
            |old - new| / max(|old|, 1) < epsilon

    This is a *relative* stagnation test — it adapts to the scale of the
    objective function.

    Key parameters (from DTGSKConfig):
        bse_window (default 50):   W — number of generations to look back.
        bse_epsilon (default 1e-8): Minimum relative improvement.
    """

    W: int               # Window size (generations)
    eps: float           # Relative improvement threshold
    buf: deque[float]    # Circular buffer of best_f values

    @classmethod
    def create(cls, *, W: int, eps: float) -> StagnationDetector:
        W = int(W)
        if W < 1:
            W = 1
        return cls(W=W, eps=float(eps), buf=deque(maxlen=W + 1))

    def reset(self) -> None:
        self.buf.clear()

    def push(self, best_f: float) -> None:
        self.buf.append(float(best_f))

    def triggered(self) -> bool:
        # I2: maxlen is always set in from_eps (W + 1, W >= 1), so skip None
        # check. buf stores floats from push(); self.eps is float. `<` returns
        # bool directly — drop redundant conversions.
        buf = self.buf
        if len(buf) < buf.maxlen:
            return False
        old = buf[0]
        new = buf[-1]
        if not (math.isfinite(old) and math.isfinite(new)):
            return False
        # Relative stagnation: if the *relative* improvement over the window is
        # smaller than eps, we consider the search stagnated.
        #
        # NOTE:
        # - We use the older value as the reference scale (as stated in the
        #   docstring): denom = max(|old|, 1).
        # - Best-so-far should be non-increasing under greedy selection, but we
        #   still guard against negative improvements.
        # Clamp negative improvements (numerical noise / non-monotone best) to
        # zero so the test remains well-defined.
        improvement = max(0.0, old - new) if old > new else 0.0
        denom = abs(old) if abs(old) > 1.0 else 1.0
        return (improvement / denom) < self.eps


# =============================================================================
# P3 final polish (opt-in eigenframe compass search on the incumbent best)
# =============================================================================


def _final_polish_basis(interaction_state, dim: int) -> tuple[np.ndarray, str]:
    """Direction set for the final polish.

    Preferred: eigenvectors of the symmetrised SGSM signed interaction
    matrix ordered by descending absolute eigenvalue — the learned
    coordinate frame of co-improving directions.  Falls back to the
    coordinate axes when no graph signal exists (D below the SGSM tier,
    empty matrix, or a degenerate decomposition).  Deterministic: eigh
    plus a stable sort; no RNG.
    """
    if interaction_state is not None:
        try:
            signed = np.asarray(interaction_state.signed_matrix, dtype=np.float64)
            if signed.shape == (dim, dim) and np.any(signed):
                sym = 0.5 * (signed + signed.T)
                eigvals, eigvecs = np.linalg.eigh(sym)
                order = np.argsort(-np.abs(eigvals), kind="stable")
                basis = np.ascontiguousarray(eigvecs[:, order].T)
                if np.all(np.isfinite(basis)):
                    return basis, "sgsm_eig"
        except np.linalg.LinAlgError:
            pass
    return np.eye(dim, dtype=np.float64), "axes"


def _final_polish_compass(
    x0: np.ndarray,
    f0: float,
    *,
    basis: np.ndarray,
    lower: np.ndarray,
    upper: np.ndarray,
    span: np.ndarray,
    budget,
    max_evals: int,
    step_frac: float,
    min_step_frac: float,
) -> tuple[np.ndarray, float, int]:
    """Deterministic compass search along ``basis`` rows from ``x0``.

    Probes +/- step along one direction per iteration (one strict-budget
    batch of two evaluations), rides a successful direction with a 1.3x
    step growth, advances on failure, and halves the step after a full
    unsuccessful sweep.  Stops on the eval cap, budget exhaustion, or
    step underflow.  Uses NO random draws.
    """
    x = np.array(x0, dtype=np.float64, copy=True)
    f_best = float(f0)
    n_dir = int(basis.shape[0])
    span_max = float(np.max(span)) if span.size else 1.0
    step = float(step_frac) * span_max
    min_step = float(min_step_frac) * span_max
    step_cap = 0.5 * span_max
    used = 0
    dir_idx = 0
    fails = 0
    cand = np.empty((2, x.shape[0]), dtype=np.float64)
    while (
        n_dir > 0
        and used < int(max_evals)
        and not budget.exhausted()
        and step >= min_step
    ):
        direction = basis[dir_idx % n_dir]
        cand[0] = x + step * direction
        cand[1] = x - step * direction
        np.clip(cand, lower, upper, out=cand)
        take = min(2, int(max_evals) - used)
        y, n_eval = budget.eval_batch_strict(cand[:take])
        used += int(n_eval)
        if n_eval <= 0:
            break
        j = int(np.argmin(y[:n_eval]))
        if float(y[j]) < f_best:
            f_best = float(y[j])
            x[:] = cand[j]
            step = min(step * 1.3, step_cap)
            fails = 0
        else:
            dir_idx += 1
            fails += 1
            if fails >= n_dir:
                step *= 0.5
                fails = 0
    return x, f_best, used


# =============================================================================
# Main optimizer
# =============================================================================


def dt_gsk_optimize(
    *,
    objective: Callable[[np.ndarray], np.ndarray],
    config: DTGSKConfig,
    return_history: bool = False,
    generation_callback: Callable[[DTGSKGenerationLog], None] | None = None,
    curve_callback: Callable[[int, float], None] | None = None,
    research_oracle_blocks: list | None = None,
    research_oracle_basis: np.ndarray | None = None,
    research_state_sink: dict | None = None,
    research_shadow_estimator: dict | None = None,
) -> DTGSKResult | tuple[DTGSKResult, np.ndarray]:
    """Run DT-GSK on an objective function (minimization).

    Executes the full DT-GSK loop (ACE, PSR, BSE, linkage crossover)
    for up to ``10000 * D`` function evaluations and returns the best
    solution found.

    .. note::
        The default configuration has several modules disabled (e.g., local
        search, triple-BSE). For competitive performance, apply a dimension-
        aware profile via ``apply_step2_profile()`` before calling this
        function. See ``profiles.py`` for available profiles.

    Parameters
    ----------
    objective : callable
        Batch objective function with signature ``(M, D) -> (M,)``.
        Accepts a 2-D array of *M* candidate solutions and returns a
        1-D array of fitness values (lower is better).
    config : DTGSKConfig
        Hyperparameters for this run (dimension, bounds, seed, module
        toggles, ACE pool, PSR schedule, etc.).
    return_history : bool, optional
        If ``True``, return ``(result, history)`` where *history* is a
        ``(G, D)`` array of per-generation best vectors.  Default is
        ``False``.
    generation_callback : callable or None, optional
        Called with a `DTGSKGenerationLog` after every generation for
        live diagnostics.  Default is ``None``.
    curve_callback : callable or None, optional
        MEM-1 fast-path: a lightweight callback ``fn(evals_used, best_f)``
        for convergence-curve collection only.  When *generation_callback*
        is ``None`` and *curve_callback* is provided, the per-generation
        telemetry assembly (``ig_stats`` + the ~340-line ``DTGSKGenerationLog``
        construction + failure-alignment / ACE-entropy / argp tuples) is
        skipped; only the two curve scalars are emitted.  The values passed
        are identical to ``gl.evals_used`` / ``gl.best_fitness`` on the full
        path (``int(budget.nfes_used)`` / ``float(best_f)``).  The live FC4
        lift-EMA controller state (the only fitness-affecting quantity in the
        telemetry block) is still updated above the skip point, so a
        curve-only run is byte-identical to the same run under the full
        callback.  If *generation_callback* is set it takes precedence and
        this is ignored.  Default is ``None``.

    Returns
    -------
    DTGSKResult or tuple[DTGSKResult, numpy.ndarray]
        If *return_history* is ``False``, a `DTGSKResult` with fields
        ``best_x``, ``best_f``, ``nfes_used``, ``max_nfes``,
        ``stop_reason``, and ``restarts_done``.  Otherwise a 2-tuple
        ``(result, history)``.

    Raises
    ------
    ValueError
        If ``config.dim`` is not positive or ``pop_size`` is less than 4.

    Examples
    --------
    >>> from gsk_family.dt_gsk import dt_gsk_optimize, DTGSKConfig
    >>> cfg = DTGSKConfig(dim=10, seed=42)
    >>> result = dt_gsk_optimize(objective=my_func, config=cfg)
    >>> result.best_f  # best fitness found
    """

    # Ensure Numba kernels are JIT-compiled on first call (amortized).
    global _NUMBA_WARMED
    if not _NUMBA_WARMED and HAS_NUMBA:
        _numba_warmup()
        _NUMBA_WARMED = True

    D = int(config.dim)
    if D <= 0:
        raise ValueError("dim must be positive")

    max_nfes = int(config.resolved_max_nfes())
    rngs = RNGStreams.from_seed(int(config.seed), generator=config.rand_generator)

    lu = config.bounds_matrix()
    lower = lu[0, :]
    upper = lu[1, :]
    span = upper - lower
    inv_sqrt_d = 1.0 / np.sqrt(float(D))

    NP_init = int(config.resolved_pop_size_init())
    if NP_init < 4:
        raise ValueError("pop_size must be at least 4")

    # Budgeted objective wrapper
    budget = BudgetController(objective=objective, max_nfes=max_nfes)

    # -----------------------------------------------------------------
    # Initialization
    # -----------------------------------------------------------------
    NP = int(NP_init)
    _init_oversample = int(getattr(config, "init_oversample", 1) or 1)
    _init_method = str(getattr(config, "init_method", "uniform") or "uniform").lower()

    def _sample_unit(n: int) -> np.ndarray:
        """Return shape ``(n, D)`` array of samples in ``[0, 1)``.

        The default ``uniform`` path consumes one ``rngs.init.random``
        draw of width ``n*D`` so it is byte-identical to the pre-LHS
        code path.  The ``lhs`` path uses ``scipy.stats.qmc`` seeded
        deterministically from one ``rngs.init.integers`` draw.  Note
        that the ``lhs`` branch DOES alter the RNG draw pattern vs
        ``uniform``, so it is gated and NOT used by the locked headline.
        """
        if _init_method == "lhs":
            from scipy.stats import qmc
            seed_val = int(rngs.init.integers(0, 2**31 - 1))
            sampler = qmc.LatinHypercube(d=int(D), seed=seed_val)
            return sampler.random(n=int(n))
        return rngs.init.random((int(n), int(D)))

    if _init_oversample > 1:
        # Oversampled init for basin-coverage: sample k*NP candidates,
        # evaluate them all, retain the best NP. RNG draw width changes
        # vs the default path, so this branch is gated and NOT used
        # by the locked headline (k=1 default).
        NP_over = NP * _init_oversample
        pop = lower + _sample_unit(NP_over) * span
        fitness, n0 = budget.eval_batch_strict(pop)
        pop = pop[:n0, :]
        fitness = np.asarray(fitness, dtype=np.float64)
        keep_n = min(NP, pop.shape[0])
        if keep_n > 0:
            order = np.argsort(fitness, kind="stable")[:keep_n]
            pop = pop[order, :]
            fitness = fitness[order]
        NP = int(pop.shape[0])
    else:
        pop = lower + _sample_unit(NP) * span
        fitness, n0 = budget.eval_batch_strict(pop)
        pop = pop[:n0, :]
        fitness = np.asarray(fitness, dtype=np.float64)
        NP = int(pop.shape[0])

    if NP == 0:
        # Budget too small to evaluate even one point.
        best_x = np.zeros((D,), dtype=np.float64)
        return DTGSKResult(
            best_x=best_x,
            best_f=float("inf"),
            nfes_used=int(budget.nfes_used),
            max_nfes=int(max_nfes),
            stop_reason="budget_exhausted",
            restarts_done=0,
        )

    best_idx = int(np.argmin(fitness))
    best_f = float(fitness[best_idx])
    best_x = pop[best_idx, :].copy()
    best_f_init = float(best_f)  # constant for cumulative_improvement tracking

    # Deep-stall full-restart bookkeeping (experimental; inert when disabled).
    # ``global_best_*`` shadows the best-ever so a full population re-init can
    # never lose ground; ``_dsr_nfes_at_best`` marks the last incumbent
    # improvement for the budget-proportional stall test.
    _dsr_enabled = bool(config.deep_stall_restart_enabled)
    _dsr_min_budget = int(config.deep_stall_min_budget)
    global_best_f = float(best_f)
    global_best_x = best_x.copy()
    _dsr_nfes_at_best = int(budget.nfes_used)
    _dsr_last_restart_nfes = -1

    # -----------------------------------------------------------------
    # Per-individual Kexp
    # When ACE is enabled, Kexp comes from the pool each generation.
    # When ACE is disabled, use the one-time heterogeneous init.
    # -----------------------------------------------------------------
    if not config.ace_enabled and config.kexp_hetero_enabled:
        u = rngs.kexp.random(NP)
        small = u < float(config.kexp_small_prob)

        lo_s, hi_s = map(float, config.kexp_small_range)
        lo_l, hi_l = map(float, config.kexp_large_range)

        kexp = np.empty((NP,), dtype=np.float64)
        if np.any(small):
            u_s = rngs.kexp.random(int(np.sum(small)))
            kexp[small] = lo_s + u_s * (hi_s - lo_s)
        if np.any(~small):
            u_l = rngs.kexp.random(int(np.sum(~small)))
            kexp[~small] = lo_l + u_l * (hi_l - lo_l)
    else:
        kexp = np.full((NP,), float(config.Kexp), dtype=np.float64)

    # -----------------------------------------------------------------
    # ACE state
    # -----------------------------------------------------------------
    pool = np.asarray(config.ace_pool, dtype=np.float64)
    if pool.ndim != 2 or pool.shape[1] != 3:
        raise ValueError("ace_pool must be a sequence of (KF, KR, Kexp) triples")

    # DE entry: append a virtual pool row for DE/rand/1 operator.
    # The pool values (KF=de_F, KR=de_CR, Kexp=0) are stored for
    # telemetry but the actual DE operator ignores junior/senior.
    de_entry_idx: int = -1  # -1 = disabled

    if config.ace_de_entry:
        de_row = np.array([[config.ace_de_F, config.ace_de_CR, 0.0]])
        pool = np.vstack([pool, de_row])
        de_entry_idx = int(pool.shape[0] - 1)

    M = int(pool.shape[0])
    ace_memory_mode = _normalise_ace_memory_mode(config.ace_memory_mode)
    psr_schedule = _normalise_psr_schedule(config.psr_schedule)
    _psr_code = {"lpsr": 0, "nlpsr": 1, "power": 2}[psr_schedule]
    # Top-bottom ACE: maintain separate probability vectors for the
    # better-ranked half (top) and worse-ranked half (bottom) of the
    # population.  Rationale: top individuals have already found productive
    # parameter settings, so their ACE distribution should reinforce those
    # entries; bottom individuals need more exploratory settings, so their
    # distribution should drift independently.  This prevents the global
    # ACE distribution from averaging out exploitation and exploration
    # signals.  Enabled via ace_memory_mode="top_bottom" (profiles: D>=20).
    dual_ace_top_bottom = bool(config.ace_enabled and ace_memory_mode == "top_bottom")

    linkage_block_size = _resolve_linkage_block_size(
        dim=D,
        block_size_by_dim=(dict(config.linkage_block_size_by_dim) if config.linkage_block_size_by_dim else None),
        strict=bool(getattr(config, "strict_profile_dims", False)),
    )
    linkage_min_dim = int(config.linkage_min_dim)
    linkage_mix_prob = float(config.linkage_block_mix_prob)
    if not math.isfinite(linkage_mix_prob) or linkage_mix_prob < 0.0 or linkage_mix_prob > 1.0:
        raise ValueError(
            f"linkage_block_mix_prob must be in [0, 1] (got {config.linkage_block_mix_prob!r})"
        )
    linkage_refresh_period = int(config.linkage_block_refresh_period)
    # NOTE: block_refresh_period is fixed at 20 generations regardless of
    # population size.  As NLPSR shrinks the population, each refresh
    # cycle builds blocks from fewer individuals, reducing co-success
    # signal quality.  Consider scaling refresh_period inversely with NP
    # if learned linkage accuracy degrades at late stages.
    if linkage_refresh_period < 1:
        raise ValueError(
            f"linkage_block_refresh_period must be >= 1 (got {config.linkage_block_refresh_period!r})"
        )
    linkage_blockwise_enabled = bool(
        config.linkage_blockwise_enabled and D >= linkage_min_dim and linkage_block_size > 1
    )
    # LINK: cached flat arrays for JIT dispatch; rebuilt on refresh.
    _link_flat: np.ndarray | None = None
    _link_offsets: np.ndarray | None = None
    linkage_random_groups: list[np.ndarray] | None = None

    # Per-entry module mask: True = this entry participates in BSE.
    _pool_modules = list(config.ace_pool_modules)
    if config.ace_de_entry:
        _pool_modules.append(False)  # DE entry doesn't participate in BSE
    if len(_pool_modules) != M:
        raise ValueError(f"ace_pool_modules (len={len(_pool_modules)}) must match pool size {M}")
    pool_modules = np.asarray(_pool_modules, dtype=bool)  # shape (M,)

    _init_probs = list(config.ace_init_probs)
    if config.ace_de_entry:
        # Rescale existing probs to make room for DE entry
        de_p = float(config.ace_de_init_prob)
        scale = 1.0 - de_p
        _init_probs = [p * scale for p in _init_probs]
        _init_probs.append(de_p)
    Kw_P = np.asarray(_init_probs, dtype=np.float64)
    if Kw_P.shape != (M,):
        raise ValueError(f"ace_init_probs (len={Kw_P.shape[0]}) must match pool size {M}")
    Kw_P = _ace_project_probs(Kw_P, p_min=float(config.ace_min_prob))
    # S4: only copy Kw_P into top/bottom when dual mode is active;
    # in single mode, both references point to the same array (read-only
    # in the non-dual path; overwritten next gen anyway).
    if dual_ace_top_bottom:
        Kw_P_top = Kw_P.copy()
        Kw_P_bottom = Kw_P.copy()
    else:
        Kw_P_top = Kw_P
        Kw_P_bottom = Kw_P

    # -----------------------------------------------------------------
    # Archive state
    # -----------------------------------------------------------------
    archive: EliteArchive | None = None
    if config.arch_enabled:
        if config.arch_max_size is not None:
            max_size = int(config.arch_max_size)
        else:
            max_size = int(_round_half_up(float(config.arch_size_mult) * float(NP_init)))
        archive = EliteArchive.create(
            dim=D,
            span=span,
            max_size=max(0, max_size),
            dist_thresh=float(config.arch_dist_thresh),
        )
        # Seed archive with the initial best.
        archive.consider(best_x, best_f)

    init_div_rad = population_radius(pop, span)

    # -----------------------------------------------------------------
    # BSE / escape state
    # -----------------------------------------------------------------
    restarts_done = 0
    basin_novelty_fires = 0
    cooldown_until_nfes = 0
    stagnation = StagnationDetector.create(W=int(config.bse_window), eps=float(config.bse_epsilon))
    stagnation.push(best_f)
    signal_window = max(1, int(config.bse_signal_window))
    acceptance_hist: deque[float] = deque(maxlen=signal_window)
    diversity_hist: deque[float] = deque(maxlen=signal_window)
    diversity_hist.append(float(init_div_rad))
    # Telemetry: sliding window of best_f for the gen-log delayed-reward
    # field (cumulative best-f improvement over a fixed lag).  Lag of 10
    # gens matches the BSE signal window default; written to gen logs as
    # `delayed_reward_lag10` for offline diagnostic analysis.
    _DELAYED_REWARD_LAG = 10
    _best_f_window: deque[float] = deque(maxlen=_DELAYED_REWARD_LAG + 1)
    _best_f_window.append(float(best_f))
    bse_trigger_mode = str(config.bse_trigger_mode).strip().lower()
    if bse_trigger_mode not in {"stagnation", "triple"}:
        raise ValueError("bse_trigger_mode must be 'stagnation' or 'triple'")
    bse_diversity_floor = max(0.0, float(config.bse_diversity_floor_frac) * float(init_div_rad))

    # -----------------------------------------------------------------
    # Tiny endgame local-search state
    # -----------------------------------------------------------------
    local_search_enabled = bool(config.local_search_enabled)
    local_search_method = _normalise_local_search_method(config.local_search_method)
    local_search_start_frac = _normalise_local_search_start_frac(config.local_search_start_frac)
    local_search_trigger_mode = _normalise_local_search_trigger_mode(
        config.local_search_trigger_mode
    )
    local_search_eval_cap = int(np.floor(float(config.local_search_eval_budget_frac) * float(max_nfes)))
    if local_search_enabled and float(config.local_search_eval_budget_frac) > 0.0:
        local_search_eval_cap = max(1, local_search_eval_cap)
    else:
        local_search_eval_cap = 0
    local_search_elite_count = max(1, int(config.local_search_elite_count))
    local_search_period = max(1, int(config.local_search_period))
    local_search_step_scale = max(0.0, float(config.local_search_step_scale))
    local_search_min_step = np.maximum(0.0, float(config.local_search_min_step_frac)) * span
    local_search_evals_total = 0

    # P3 final polish resolution (default OFF -> zero behavioural effect).
    final_polish_enabled = bool(config.final_polish_enabled)
    final_polish_start_frac = float(config.final_polish_start_frac)
    final_polish_eval_cap = (
        int(np.floor(float(config.final_polish_budget_frac) * float(max_nfes)))
        if final_polish_enabled
        else 0
    )
    final_polish_done = False
    local_search_coord_cursor = 0
    local_search_stagnation_window = max(1, int(config.local_search_stagnation_window))
    local_search_acceptance_floor = _validate_unit_interval("local_search_acceptance_floor", config.local_search_acceptance_floor)
    local_search_diversity_cap = _validate_unit_interval("local_search_diversity_cap", config.local_search_diversity_cap)
    local_search_score_threshold = _normalise_local_search_score_threshold(config.local_search_score_threshold)
    local_search_coherence_window = max(1, int(config.local_search_coherence_window))
    local_search_coherence_min = _validate_unit_interval("local_search_coherence_min", config.local_search_coherence_min)
    local_search_post_restart_cooldown = max(0, int(config.local_search_post_restart_cooldown))
    local_search_post_ls_cooldown = max(0, int(config.local_search_post_ls_cooldown))
    local_search_block_until_gen = 0
    local_search_restart_block_until_gen = 0

    # Success-Graph Structural Memory (SGSM) state.
    interaction_graph_enabled = bool(config.interaction_graph_enabled) and int(D) >= int(config.interaction_graph_min_dim)
    interaction_graph_refresh_period = max(1, int(config.interaction_graph_refresh_period))
    interaction_graph_warmup_frac = _validate_unit_interval("interaction_graph_warmup_frac", config.interaction_graph_warmup_frac)
    interaction_graph_decay = _validate_unit_interval("interaction_graph_decay", config.interaction_graph_decay)
    interaction_graph_lr = max(0.0, float(config.interaction_graph_lr))
    interaction_graph_edge_floor = max(0.0, float(config.interaction_graph_edge_floor))
    interaction_block_min_size = max(2, int(config.interaction_block_min_size))
    interaction_block_max_size = max(interaction_block_min_size, int(config.interaction_block_max_size))
    interaction_confidence_min = _validate_unit_interval("interaction_confidence_min", config.interaction_confidence_min)
    interaction_linkage_confidence_min = (
        interaction_confidence_min
        if config.interaction_linkage_confidence_min is None
        else _validate_unit_interval("interaction_linkage_confidence_min", config.interaction_linkage_confidence_min)
    )
    interaction_ls_confidence_min = (
        interaction_confidence_min
        if config.interaction_ls_confidence_min is None
        else _validate_unit_interval("interaction_ls_confidence_min", config.interaction_ls_confidence_min)
    )
    # Adaptive-gate parameters. When disabled (default) the effective gate
    # threshold equals the static floors above. When enabled, ``ig_adaptive_threshold``
    # returns the ``percentile``-quantile of the most recent ``window`` confidences
    # recorded in state.confidence_history (clipped below by ``floor`` and with
    # a static warm-up of ``min_samples`` refreshes).
    interaction_confidence_adaptive = bool(getattr(config, "interaction_confidence_adaptive", False))
    interaction_confidence_adaptive_window = max(1, int(getattr(config, "interaction_confidence_adaptive_window", 50)))
    interaction_confidence_adaptive_percentile = _validate_unit_interval(
        "interaction_confidence_adaptive_percentile",
        float(getattr(config, "interaction_confidence_adaptive_percentile", 0.50)),
    )
    interaction_confidence_adaptive_floor = _validate_unit_interval(
        "interaction_confidence_adaptive_floor",
        float(getattr(config, "interaction_confidence_adaptive_floor", 0.10)),
    )
    interaction_confidence_adaptive_min_samples = max(
        1, int(getattr(config, "interaction_confidence_adaptive_min_samples", 5))
    )
    interaction_confidence_adaptive_absolute_min = _validate_unit_interval(
        "interaction_confidence_adaptive_absolute_min",
        float(getattr(config, "interaction_confidence_adaptive_absolute_min", 0.0)),
    )
    interaction_linkage_mix_prob = _validate_unit_interval("interaction_linkage_mix_prob", config.interaction_linkage_mix_prob)
    interaction_use_for_linkage = bool(config.interaction_use_for_linkage) and interaction_graph_enabled
    interaction_use_for_local_search = bool(config.interaction_use_for_local_search) and interaction_graph_enabled
    interaction_ls_top_blocks = max(1, int(config.interaction_ls_top_blocks))
    interaction_ls_dim_cap = max(1, min(int(config.interaction_ls_dim_cap), int(D)))
    interaction_min_updates = max(1, int(config.interaction_min_updates))
    interaction_min_refreshes = max(1, int(config.interaction_min_refreshes))
    interaction_min_nontrivial_dims = max(2, int(config.interaction_min_nontrivial_dims))
    interaction_post_restart_cooldown = max(0, int(config.interaction_post_restart_cooldown))
    interaction_restart_decay = _validate_unit_interval("interaction_restart_decay", config.interaction_restart_decay)
    interaction_de_update_weight = max(0.0, float(config.interaction_de_update_weight))
    interaction_ls_update_weight = max(0.0, float(config.interaction_ls_update_weight))
    interaction_update_period = max(1, int(getattr(config, "interaction_update_period", 1)))
    interaction_update_max_samples = max(0, int(getattr(config, "interaction_update_max_samples", 0)))
    interaction_state: InteractionGraphState | None = ig_init(D) if interaction_graph_enabled else None
    interaction_learned_groups: list[np.ndarray] | None = None
    interaction_linkage_rows_learned = 0
    interaction_linkage_rows_random = 0
    interaction_updates_from_de = 0
    interaction_updates_from_ls = 0
    interaction_ls_blocks_used: tuple[int, ...] = tuple()
    interaction_block_until_gen = 0

    # TERRA-GSK state (all default-off; no effect unless enabled).
    # IMPORTANT: each sub-flag is honored independently so that a single-
    # component toggle (e.g. flipping ``sp_nlpsr_enabled`` alone) actually
    # enables/disables only the named module. ``terra_enabled`` is purely a
    # label; the variant builder is responsible for setting each sub-flag to
    # its desired value. A previous implementation OR'd each sub-flag with
    # ``terra_enabled``, which silently forced every component on whenever
    # TERRA was active and made independent component control impossible.
    budget_policy_enabled = bool(getattr(config, "budget_policy_enabled", False))
    sp_nlpsr_enabled = bool(getattr(config, "sp_nlpsr_enabled", False))
    basin_memory_enabled = bool(getattr(config, "basin_memory_enabled", False))
    local_search_auto_subspace = bool(getattr(config, "local_search_auto_subspace", False))
    linkage_reliability_state: LinkageReliabilityState | None = None
    # predicted-value gate.  When enabled, the
    # subspace-admission rule is replaced by a phase-conditional
    # predicted-improvement threshold.  When disabled, the gate is a
    # strict pass-through to the bare LCB admission, preserving
    # locked-headline byte stability.
    predicted_value_gate: PredictedValueGate | None = None
    # Sample-Protected NLPSR floor governor.  When enabled,
    # NLPSR's NP target is clamped to dimension_scaled_n_min(D) +
    # extra_floor while subspace decisions are below
    # min_subspace_samples and budget_frac is below release_tau.  The
    # legacy sp_nlpsr_enabled clamp at the NLPSR call site is replaced
    # by sp_nlpsr_state.clamp().
    sp_nlpsr_state: SPNlpsrState | None = None
    if sp_nlpsr_enabled:
        sp_nlpsr_state = SPNlpsrState.create(
            enabled=True,
            dim=int(D),
            min_subspace_samples=int(getattr(config, "sp_nlpsr_min_subspace_samples", 64)),
            release_tau=float(getattr(config, "sp_nlpsr_release_tau", 0.70)),
            extra_floor=int(getattr(config, "sp_nlpsr_extra_floor", 0)),
        )
    basin_memory: BasinMemory | None = None
    if basin_memory_enabled:
        basin_memory = BasinMemory(
            max_size=int(getattr(config, "basin_memory_max_size", 64)),
            min_distance=float(getattr(config, "basin_memory_min_distance", 0.05)),
        )
        basin_memory.add(best_x, best_f, span, improved=True)
    terra_trust_clip_rate = 0.0
    terra_ls_allowed = True
    terra_escape_allowed = True

    # Subspace NM: track successful displacement vectors for PCA
    _subspace_dim = int(config.local_search_subspace_dim)
    if _subspace_dim <= 0:
        _subspace_dim = min(10, max(3, D // 3))  # auto: 3..10
    _subspace_dim = min(_subspace_dim, D)  # can't exceed D
    _disp_buf_max = max(50, 3 * _subspace_dim)  # rolling buffer size
    _disp_buf: list[np.ndarray] = []  # successful displacement vectors
    _track_disp_vectors = (
        (_ls_code := {"subspace_nm": 0, "nelder_mead": 1}.get(local_search_method, -1)) == 0
        or local_search_trigger_mode == "time_and_event"
        or bool(local_search_auto_subspace)
    )

    history: list[float] | None = [] if return_history else None

    div_rad = population_radius(pop, span)  # initial value for first log
    linkage_groups: list[np.ndarray] | None = None
    linkage_group_count = 0

    # S10: integer code for local-search method to skip per-gen string comparisons
    # computed above together with _track_disp_vectors.

    # -----------------------------------------------------------------
    # ARGP: Acceptance-Rate Gated Pool Pruning state
    # -----------------------------------------------------------------
    argp_frozen = np.zeros(M, dtype=bool)        # True = entry permanently frozen
    argp_ring_succ = np.zeros((config.argp_window, M), dtype=np.int64)
    argp_ring_samp = np.zeros((config.argp_window, M), dtype=np.int64)
    argp_ring_idx = 0                            # current slot in ring buffer
    argp_rolling_acc = np.zeros(M, dtype=np.float64)
    argp_frozen_top = np.zeros(M, dtype=bool)
    argp_frozen_bottom = np.zeros(M, dtype=bool)
    argp_ring_succ_top = np.zeros((config.argp_window, M), dtype=np.int64)
    argp_ring_samp_top = np.zeros((config.argp_window, M), dtype=np.int64)
    argp_ring_succ_bottom = np.zeros((config.argp_window, M), dtype=np.int64)
    argp_ring_samp_bottom = np.zeros((config.argp_window, M), dtype=np.int64)
    argp_rolling_acc_top = np.zeros(M, dtype=np.float64)
    argp_rolling_acc_bottom = np.zeros(M, dtype=np.float64)
    argp_low_streak_top = np.zeros(M, dtype=np.int64)
    argp_low_streak_bottom = np.zeros(M, dtype=np.int64)

    # Scipy minimize: import once, guard call sites on availability.
    _sp_minimize = None
    try:
        from scipy.optimize import minimize as _sp_minimize
    except ImportError:
        pass

    # Stable per-run telemetry identifiers.
    _run_seed = int(config.seed)
    # research_dt2_shadow is a diagnostics-only flag (DT2 program); exclude it
    # from the scientific config identity so enabling shadow diagnostics never
    # changes the pub config hash (numbers are byte-identical regardless).
    _run_config_hash = stable_hash(
        {k: v for k, v in asdict(config).items() if k != "research_dt2_shadow"}
    )
    _git_commit = current_git_commit()
    # DT2 Sprint-1 oracle injection (research only; both default None -> the
    # adapter never passes them, so pub is byte-identical). When supplied, the
    # exact ground-truth blocks / basis are forced through the existing learned
    # linkage and eigenframe-polish consumers, giving the oracle upper bound.
    _research_oracle_blocks = (
        [np.asarray(g, dtype=np.int64) for g in research_oracle_blocks]
        if research_oracle_blocks is not None else None
    )
    _research_oracle_basis = (
        np.ascontiguousarray(research_oracle_basis, dtype=np.float64)
        if research_oracle_basis is not None else None
    )

    # -----------------------------------------------------------------
    # Main loop
    # -----------------------------------------------------------------
    gen = 0
    stagnation_gens_counter = 0
    _ui_buf = np.empty((NP_init, D), dtype=np.float64)  # pre-allocated trial buffer
    # Pre-allocate junior/senior mutation buffers ONCE at NP_init capacity so the
    # main loop can reuse them as ``_vi_jun_buf[:NP, :]`` views every generation.
    # Without pre-allocation we would allocate-and-free 2 x (NP, D) float64 arrays
    # per generation, which dominates per-generation Python overhead at high D
    # and triggers heavy GC pressure during long runs.  The slice ``[:NP, :]`` is
    # C-contiguous from offset 0, so all Numba kernels (which infer NP from
    # ``arr.shape[0]``) work unchanged.
    _vi_jun_buf = np.empty((NP_init, D), dtype=np.float64)
    _vi_sen_buf = np.empty((NP_init, D), dtype=np.float64)
    _fitness_old_buf = np.empty(NP_init, dtype=np.float64)  # pre-allocated fitness snapshot
    _rank_pos_buf = np.empty((NP_init,), dtype=np.int64)
    _s_idx_buf = np.empty((NP_init,), dtype=np.int64)
    _KF_buf = np.empty((NP_init,), dtype=np.float64)
    _KR_buf = np.empty((NP_init,), dtype=np.float64)
    _rewards_buf = np.zeros((NP_init,), dtype=np.float64)
    _child_fit_buf = np.empty(NP_init, dtype=np.float64)   # B14: pre-allocated
    _dj_buf = np.zeros((NP_init, D), dtype=np.bool_)      # B03: pre-allocated mask
    _ds_buf = np.zeros((NP_init, D), dtype=np.bool_)      # B03: pre-allocated mask
    _arange_int_buf = np.arange(NP_init, dtype=np.int64)    # S2: reusable int arange
    _arange_float_buf = np.arange(NP_init, dtype=np.float64) # S6: reusable float arange
    _dim_upd_buf = np.empty((NP_init, D), dtype=np.bool_)   # S3: logical_or output
    _p_junior_buf = np.empty(NP_init, dtype=np.float64)      # S5: p_junior_i buffer
    _de_rows_buf = np.zeros((NP_init,), dtype=np.bool_)      # B19: pre-allocated DE-used mask
    # S5: cache config booleans (frozen dataclass — never change)
    _cfg_ace_enabled = bool(config.ace_enabled)
    _cfg_psr_enabled = bool(config.psr_enabled)
    _cfg_bse_enabled = bool(config.bse_enabled)
    _cfg_argp_enabled = bool(config.argp_enabled)
    _cfg_research_dt2_shadow = bool(config.research_dt2_shadow)  # DT2 shadow diagnostics
    # S3: sentinel empty arrays for ACE-disabled path
    _ace_empty_int = np.zeros((0,), dtype=np.int64)
    _ace_empty_float = np.zeros((0,), dtype=np.float64)
    _cfg_argp_threshold = float(config.argp_threshold)            # S7
    _cfg_n_min = int(config.n_min)
    _cfg_psr_alpha = float(config.psr_alpha)
    _cfg_p_senior = float(config.p_senior)
    _cfg_p_senior_split_enabled = bool(config.p_senior_split_enabled)
    _cfg_p_senior_bottom_wide = float(config.p_senior_bottom_wide)
    _cfg_KF = float(config.KF)
    _cfg_KR = float(config.KR)
    _cfg_kr_min_dims = int(config.kr_min_dims)
    _cfg_ace_module_gate_thresh = _validate_unit_interval("ace_module_gate_thresh", config.ace_module_gate_thresh)
    _cfg_ace_module_gate_mode = _normalise_ace_module_gate_mode(config.ace_module_gate_mode)
    _cfg_ace_module_gate_low, _cfg_ace_module_gate_high = _validate_hysteresis_bounds(
        low=config.ace_module_gate_low,
        high=config.ace_module_gate_high,
    )
    _cfg_force_nonzero_update = bool(config.force_nonzero_update)
    # ----------------------------------------------------------------------
    # V4 -- late-budget controllers (D >= 100 only).  All defaults collapse
    # to byte-identical V3-locked behaviour.  See PHASE3/PHASE4_DESIGN.md.
    # ----------------------------------------------------------------------
    # A1 -- late_tau_acceptance_clip
    _cfg_v4_a1_enabled = bool(config.late_accept_clip_enabled)
    _cfg_v4_a1_tau_floor = float(config.late_accept_clip_tau_floor)
    _cfg_v4_a1_acc_high = float(config.late_accept_clip_acc_high)
    _cfg_v4_a1_log_drop_eps = float(config.late_accept_clip_log_drop_eps)
    _cfg_v4_a1_streak_k = int(config.late_accept_clip_streak_k)
    _cfg_v4_a1_strict_eps = float(config.late_accept_clip_strict_eps)
    _cfg_v4_a1_logdrop_alpha = float(config.late_accept_clip_log_drop_ema_alpha)
    # A2 -- frozen_streak_broaden
    _cfg_v4_a2_enabled = bool(config.frozen_broaden_enabled)
    _cfg_v4_a2_acc_floor = float(config.frozen_broaden_acc_floor)
    _cfg_v4_a2_log_drop_eps = float(config.frozen_broaden_log_drop_eps)
    _cfg_v4_a2_streak_k = int(config.frozen_broaden_streak_k)
    _cfg_v4_a2_window_m = int(config.frozen_broaden_window_m)
    _cfg_v4_a2_cooldown = int(config.frozen_broaden_cooldown)
    _cfg_v4_a2_factor = float(config.frozen_broaden_factor)
    # FC4 -- linkage_random_mix_late
    _cfg_v4_fc4_enabled = bool(config.link_random_mix_enabled)
    _cfg_v4_fc4_tau_floor = float(config.link_random_mix_tau_floor)
    _cfg_v4_fc4_negative_lift = float(config.link_random_mix_negative_lift)
    _cfg_v4_fc4_severe_lift = float(config.link_random_mix_severe_lift)
    _cfg_v4_fc4_strength = float(config.link_random_mix_strength)
    _cfg_v4_fc4_window = int(config.link_random_mix_window)
    _cfg_v4_fc4_ema_alpha = float(config.link_random_mix_ema_alpha)
    # V4 runtime state.  All initial values produce no-op behaviour.
    _v4_log_drop_ema: float = 0.0      # A1+A2: |log10(prev_best - best + eps)|; init 0 ⇒ first gen never gates
    _v4_logdrop_streak: int = 0        # A1: gens with low log_drop AND high acc
    _v4_frozen_streak: int = 0         # A2: gens with low acc AND low log_drop
    _v4_a2_window_remaining: int = 0   # A2: KR-broaden gens left
    _v4_a2_cooldown_remaining: int = 0 # A2: cooldown gens left
    _v4_link_lift_ema: float = 0.0     # FC4: rolling (learned_acc - random_acc)
    _v4_prev_best_f: float = float(best_f)  # for log_drop computation
    _cfg_ace_de_F = float(config.ace_de_F)
    _cfg_ace_de_CR = float(config.ace_de_CR)
    _cfg_ace_de_policy_mode = _normalise_ace_de_policy_mode(config.ace_de_policy_mode)
    _cfg_ace_de_policy_acceptance_floor = _validate_unit_interval("ace_de_policy_acceptance_floor", config.ace_de_policy_acceptance_floor)
    _cfg_ace_de_policy_diversity_cap = _validate_unit_interval("ace_de_policy_diversity_cap", config.ace_de_policy_diversity_cap)
    _cfg_ace_de_policy_stagnation_gens = int(config.ace_de_policy_stagnation_gens)
    # Per-individual F/CR scratch buffers + previous fitness for SHADE update.
    _cfg_ace_start_frac = float(config.ace_start_frac)
    _cfg_ace_coverage_weighted = bool(config.ace_coverage_weighted)
    # W2.4 (2026-07-25): coverage_i feeds ONLY (a) the ACE coverage weight
    # (config-off in every shipped profile) and (b) the mean_dim_coverage
    # telemetry field, whose GenStats are consumed solely by
    # generation_callback (verified: the callback call is inner-guarded;
    # curve_callback takes (evals, best_f) only). When neither consumer
    # exists the O(NP*D) coverage kernel is pure waste.
    _need_coverage = _cfg_ace_coverage_weighted or (generation_callback is not None)
    _cfg_ace_coverage_exponent = float(config.ace_coverage_exponent)
    _cfg_ace_learning_rate = float(config.ace_learning_rate)
    _cfg_ace_min_prob = float(config.ace_min_prob)
    _cfg_argp_window = int(config.argp_window)
    _cfg_argp_preserve_split_memory = bool(config.argp_preserve_split_memory)
    _cfg_argp_threshold_top = (
        float(config.argp_threshold_top)
        if config.argp_threshold_top is not None else float(config.argp_threshold)
    )
    _cfg_argp_threshold_bottom = (
        float(config.argp_threshold_bottom)
        if config.argp_threshold_bottom is not None else float(config.argp_threshold)
    )
    _cfg_argp_freeze_scope = _normalise_argp_freeze_scope(config.argp_freeze_scope)
    _cfg_argp_confirm_windows = max(1, int(config.argp_confirm_windows))
    _cfg_argp_max_frozen_frac = max(0.0, min(1.0, float(config.argp_max_frozen_frac)))
    _cfg_argp_soft_freeze_prob = float(config.argp_soft_freeze_prob)
    _cfg_argp_frozen_prob_floor = (
        max(_cfg_ace_min_prob, _cfg_argp_soft_freeze_prob)
        if _cfg_argp_soft_freeze_prob > 0.0
        else _cfg_ace_min_prob
    )
    _cfg_argp_guarded_split = bool(
        _cfg_argp_confirm_windows > 1
        or _cfg_argp_max_frozen_frac < 1.0
        or _cfg_argp_frozen_prob_floor > (_cfg_ace_min_prob + 1e-15)
    )
    _cfg_Kexp = float(config.Kexp)
    # Resolve the pool entry closest to the baseline GSK control tuple so DE
    # policy remapping does not assume a hard-coded arm index.
    _gsk_pure_arm_idx = -1
    _pure_target = np.array([_cfg_KF, _cfg_KR, _cfg_Kexp], dtype=np.float64)
    _cand_mask = np.ones(M, dtype=bool)
    if 0 <= de_entry_idx < M:
        _cand_mask[de_entry_idx] = False
    _cand_idx = np.flatnonzero(_cand_mask)
    if _cand_idx.size > 0:
        _cand_pool = pool[_cand_idx, :]
        _exact = np.all(np.isclose(_cand_pool, _pure_target[np.newaxis, :], atol=1e-12, rtol=1e-12), axis=1)
        if np.any(_exact):
            _gsk_pure_arm_idx = int(_cand_idx[np.flatnonzero(_exact)[0]])
        else:
            _dist = np.linalg.norm(_cand_pool - _pure_target[np.newaxis, :], axis=1)
            _gsk_pure_arm_idx = int(_cand_idx[int(np.argmin(_dist))])
    _cfg_bse_acceptance_floor = float(config.bse_acceptance_floor)
    _cfg_bse_max_restarts = int(config.bse_max_restarts)
    _cfg_bse_stop_frac = float(config.bse_stop_frac)
    _cfg_bse_freeze_elites = bool(config.bse_freeze_elites)
    _cfg_bse_freeze_frac = float(config.bse_freeze_frac)
    _cfg_bse_cauchy_enabled = bool(config.bse_cauchy_enabled)
    _cfg_bse_cauchy_frac = float(config.bse_cauchy_frac)
    _cfg_bse_cauchy_scale = float(config.bse_cauchy_scale)
    _cfg_bse_restart_frac = float(config.bse_restart_frac)
    _cfg_bse_archive_inject_prob = float(config.bse_archive_inject_prob)
    _cfg_bse_jitter_scale = float(config.bse_jitter_scale)
    _cfg_bse_cooldown_frac = float(config.bse_cooldown_frac)
    _cfg_argp_warmup_frac = float(config.argp_warmup_frac)
    _module_gate_hysteresis = (_cfg_ace_module_gate_mode == "hysteresis")
    _module_gate_state = True
    _bse_triple = (bse_trigger_mode == "triple")  # S10: cache string compare as bool
    # FE2-3: hoist the loop-invariant interaction_probe_rate clamp out of the hot
    # loop (it is reassigned nowhere in the loop body).  Reused at the two in-loop
    # sites below (SRI probe gate + FC4 primary-row prob); bit-identical scalar.
    _probe_rate_clamped = max(0.0, min(1.0, float(getattr(config, "interaction_probe_rate", 0.10))))
    while not budget.exhausted():
        gen += 1
        if generation_callback is not None or curve_callback is not None:
            # B18: only time when a callback consumes the telemetry block.
            # MEM-1: bound for the curve-only path too (the block below is now
            # entered for either callback); the value is unused on the
            # curve-only branch but must exist before ``generation_runtime``.
            gen_t0 = time.perf_counter()
        evals_used_before_gen = int(budget.nfes_used)
        best_before_gen = float(best_f)
        archive_insertions = 0
        archive_samples_used = 0
        low_acceptance_triggered = False
        low_diversity_triggered = False
        escape_triggered = False
        signal_acceptance_mean = 0.0
        signal_diversity_mean = float(div_rad)
        cauchy_triggered = False
        n_cauchy_perturbed = 0
        local_search_active = False
        local_search_evals_used_gen = 0
        local_search_improvements = 0
        local_search_best_delta = 0.0
        local_search_basis_source = "none"
        local_search_trigger_score = 0
        local_search_trigger_reason = "none"
        local_search_disp_coherence = 0.0
        local_search_subspace_dim_used = 0
        local_search_elite_count_used = 0
        interaction_linkage_rows_learned = 0
        interaction_linkage_rows_random = 0
        interaction_updates_from_de = 0
        interaction_updates_from_ls = 0
        interaction_ls_blocks_used = tuple()
        de_policy_active = (de_entry_idx >= 0)
        de_used_rows = _de_rows_buf[:NP]
        de_used_rows[:] = False
        restart_cause = "none"

        # Budget fraction used
        frac_used = (budget.nfes_used / float(max_nfes)) if max_nfes > 0 else 1.0
        frac_used = max(0.0, min(1.0, frac_used))
        progress = 1.0 - frac_used

        # --------------------------------------------------------------
        # (A) Population size reduction (decoupled, nonlinear)
        # --------------------------------------------------------------
        _psr_culled = False  # B06: track whether PSR sorted+culled
        if _cfg_psr_enabled:
            Ninit = int(NP_init)
            Nmin = _cfg_n_min
            if sp_nlpsr_enabled:
                # SP-NLPSR floor governor.  Clamps Nmin to
                # dimension_scaled_n_min(D)+extra_floor while the
                # subspace-decision count is below min_subspace_samples
                # AND budget_frac < release_tau (default tau=0.70 = PTR
                # refine boundary).  Releases automatically once either
                # gate is reached, allowing standard L-SHADE shrinkage.
                if sp_nlpsr_state is not None:
                    Nmin = int(sp_nlpsr_state.clamp(int(Nmin), budget_frac=float(frac_used)))
                else:
                    # Defensive fallback when the legacy flag is on but
                    # the state somehow was not constructed: keep the
                    # always-on floor at dimension_scaled_n_min(D).
                    Nmin = max(int(Nmin), int(dimension_scaled_n_min(D)))
            if Nmin < 4:
                Nmin = 4
            if Nmin > Ninit:
                Nmin = Ninit

            NP_desired = _psr_target_size(
                n_init=Ninit,
                n_min=Nmin,
                nfes_used=int(budget.nfes_used),
                max_nfes=int(max_nfes),
                schedule=psr_schedule,
                alpha=_cfg_psr_alpha,
                schedule_code=_psr_code,
            )
            NP_desired = max(Nmin, min(NP_desired, NP))

            if NP_desired < NP:
                ind_best = np.argsort(fitness, kind="mergesort")
                keep = ind_best[:NP_desired]
                pop = pop[keep, :]
                fitness = fitness[keep]
                kexp = kexp[keep]
                NP = int(NP_desired)
                _psr_culled = True  # B06: fitness is now sorted ascending

        # --------------------------------------------------------------
        # Diversity metric (Rad(X)) for logging and BSE triggers
        # --------------------------------------------------------------
        div_rad = population_radius(pop, span)

        # --------------------------------------------------------------
        # Sort and pick sources (deterministic sort)
        # B06: skip argsort when PSR already sorted fitness this generation
        # --------------------------------------------------------------
        if _psr_culled:
            ind_best = _arange_int_buf[:NP]
        else:
            ind_best = np.argsort(fitness, kind="mergesort")
        rank_pos = _rank_pos_buf[:NP]
        rank_pos[ind_best] = _arange_int_buf[:NP]
        top_half_cut = max(1, (NP + 1) // 2)
        top_half_mask = rank_pos < top_half_cut
        bottom_half_mask = ~top_half_mask
        top_frac_current = (float(top_half_cut) / float(NP)) if NP > 0 else 0.5
        bottom_frac_current = 1.0 - top_frac_current
        Rg1, Rg2, Rg3 = gained_shared_junior_r1r2r3(ind_best, rngs.core)
        # ----------------------------------------------------------------
        # Senior-GSK adaptive split (locked headline at D >= 50).
        #
        # When ``p_senior_split_enabled`` is OFF (D < 50): byte-identical
        # to the bare GSK senior selection -- a single call with the base
        # p_senior.
        #
        # When ON (D >= 50): as long as the rolling acceptance signal is
        # hot (mean over the last signal_window generations is ABOVE the
        # floor), we still run the byte-identical single call.  When the
        # signal cools (mean <= bse_acceptance_floor), we run two senior
        # selections -- the base p_senior for the top-half-by-fitness
        # mask, and the wider ``p_senior_bottom_wide`` for the bottom-
        # half mask -- and merge.  This keeps the elite direction sharp
        # on unimodal basins (F1/F9/F12 at D=100) while letting the
        # laggers explore a wider senior cone when stuck.  The trigger
        # uses ``acceptance_hist`` *before* the current generation's
        # value is pushed (line ~2990), so the signal observed here is
        # the previous generation's mean -- consistent with how
        # ``de_policy_active`` consumes it below.
        # ----------------------------------------------------------------
        if (
            _cfg_p_senior_split_enabled
            and len(acceptance_hist) >= signal_window
        ):
            _split_prev_acc_mean = sum(acceptance_hist) / len(acceptance_hist)
            _split_signal_widen = bool(
                _split_prev_acc_mean <= _cfg_bse_acceptance_floor
            )
        else:
            _split_signal_widen = False
        _split_widen_now = bool(_split_signal_widen)
        _v4_p_senior_eff = _cfg_p_senior
        _v4_p_senior_bottom_wide_eff = _cfg_p_senior_bottom_wide
        if _split_widen_now:
            # Single random triplet, dispatched to two p-values via
            # _from_rands. Keeps RNG draw count equal to the disabled
            # path (3 draws/gen) so v0-split toggling does not drift
            # the rngs.core stream.
            _r1_rand = rngs.core.random(NP)
            _r2_rand = rngs.core.random(NP)
            _r3_rand = rngs.core.random(NP)
            _R1_top, _R2_top, _R3_top = gained_shared_senior_r1r2r3_from_rands(
                ind_best, _r1_rand, _r2_rand, _r3_rand, _v4_p_senior_eff,
            )
            _R1_bot, _R2_bot, _R3_bot = gained_shared_senior_r1r2r3_from_rands(
                ind_best, _r1_rand, _r2_rand, _r3_rand, _v4_p_senior_bottom_wide_eff,
            )
            R1 = np.where(top_half_mask, _R1_top, _R1_bot)
            R2 = np.where(top_half_mask, _R2_top, _R2_bot)
            R3 = np.where(top_half_mask, _R3_top, _R3_bot)
        else:
            R1, R2, R3 = gained_shared_senior_r1r2r3(
                ind_best, rngs.core, p=_v4_p_senior_eff,
            )

        # --------------------------------------------------------------
        # ACE per-individual parameter selection
        #
        # IMPORTANT (NEW): ACE sampling must happen *before* we compute
        # the junior experience mask (D_junior_i), because Kexp is part of
        # the ACE pool.  If we compute D_junior_i first, Kexp lags by one
        # generation (the previous generation's sampled Kexp is used).
        # --------------------------------------------------------------
        if _cfg_ace_enabled:
            if dual_ace_top_bottom:
                s_idx = _s_idx_buf[:NP]
                # H3: count_true_fast over top_half_mask, bottom is the
                # complement so it follows by subtraction.
                if count_true_fast is not None:
                    n_top = int(count_true_fast(top_half_mask))
                else:
                    n_top = int(np.sum(top_half_mask))
                n_bottom = int(NP) - n_top
                if n_top > 0:
                    s_idx[top_half_mask] = _ace_sample_indices(rngs.ace, Kw_P_top, n=n_top)
                if n_bottom > 0:
                    s_idx[bottom_half_mask] = _ace_sample_indices(rngs.ace, Kw_P_bottom, n=n_bottom)
                Kw_P = (top_frac_current * Kw_P_top) + (bottom_frac_current * Kw_P_bottom)
            else:
                s_idx = _ace_sample_indices(rngs.ace, Kw_P, n=NP)
                # S4: skip unnecessary copies in single-ACE mode.
                Kw_P_top = Kw_P
                Kw_P_bottom = Kw_P

            if de_entry_idx >= 0 and _cfg_ace_de_policy_mode == "state":
                _prev_acc_mean = (sum(acceptance_hist) / len(acceptance_hist)) if acceptance_hist else 1.0
                _div_ratio_now = float(div_rad) / max(1e-30, float(init_div_rad))
                de_policy_active = bool(
                    frac_used <= 0.35
                    or stagnation_gens_counter >= _cfg_ace_de_policy_stagnation_gens
                    or _prev_acc_mean <= _cfg_ace_de_policy_acceptance_floor
                    or _div_ratio_now <= _cfg_ace_de_policy_diversity_cap
                )
                if not de_policy_active and _gsk_pure_arm_idx >= 0:
                    s_idx[s_idx == de_entry_idx] = _gsk_pure_arm_idx

            KF_i = pool[s_idx, 0]
            KR_i = pool[s_idx, 1]
            # Per-individual Kexp from pool column 2.
            kexp = pool[s_idx, 2]

            # KR floor: ensure every individual updates at least kr_min_dims.
            if _cfg_kr_min_dims > 0:
                kr_floor = min(1.0, float(_cfg_kr_min_dims) / float(D))
                KR_i = np.maximum(KR_i, kr_floor)
        else:
            s_idx = _s_idx_buf[:NP]; s_idx[:] = 0
            KF_i = _KF_buf[:NP]; KF_i[:] = _cfg_KF
            KR_i = _KR_buf[:NP]; KR_i[:] = _cfg_KR

        # A2 -- frozen_streak_broaden.  When V4 has opened an
        # active broaden window (set in EOG when frozen streak hits K),
        # scale every KR_i by ``factor`` and clip to [0, 1].  This is a
        # parallel path to the (removed) PTR clip (which was OFF in V3-locked).
        # Default (factor=1.0 OR window=0) collapses to no-op.
        if _v4_a2_window_remaining > 0 and _cfg_v4_a2_factor != 1.0:
            KR_i = np.clip(KR_i * _cfg_v4_a2_factor, 0.0, 1.0)

        # --------------------------------------------------------------
        # Experience masks (budget-driven)
        # --------------------------------------------------------------
        D_junior_i = np.ceil(float(D) * np.power(progress, kexp)).astype(np.int64)
        np.clip(D_junior_i, 0, D, out=D_junior_i)

        p_junior_i = _p_junior_buf[:NP]
        np.divide(D_junior_i, float(D), out=p_junior_i)

        linkage_blockwise_active = bool(linkage_blockwise_enabled)
        linkage_mix_prob_eff = float(linkage_mix_prob)
        if interaction_confidence_adaptive and interaction_state is not None:
            _linkage_gate_thr = ig_adaptive_threshold(
                interaction_state,
                static_threshold=interaction_linkage_confidence_min,
                percentile=interaction_confidence_adaptive_percentile,
                floor=interaction_confidence_adaptive_floor,
                min_samples=interaction_confidence_adaptive_min_samples,
                window=interaction_confidence_adaptive_window,
                absolute_min=interaction_confidence_adaptive_absolute_min,
            )
        else:
            _linkage_gate_thr = interaction_linkage_confidence_min
        interaction_linkage_ready = bool(
            interaction_use_for_linkage
            and interaction_state is not None
            and int(gen) >= int(interaction_block_until_gen)
            and ig_ready(
                interaction_state,
                confidence_min=_linkage_gate_thr,
                min_updates=interaction_min_updates,
                min_refreshes=interaction_min_refreshes,
                min_nontrivial_dims=interaction_min_nontrivial_dims,
            )
        )
        _sri_probe_active = False
        if interaction_linkage_ready and linkage_reliability_state is not None:
            # when enabled, route the admission decision
            # through the predicted-value gate; falls back to the bare
            # LCB admission when the gate is disabled or absent.
            _sri_legacy_admit = bool(linkage_reliability_state.admit())
            if predicted_value_gate is not None:
                _sri_acc = (sum(acceptance_hist) / len(acceptance_hist)) if acceptance_hist else 0.0
                _sri_admit = predicted_value_gate.admit(
                    lcb_lift=float(linkage_reliability_state.last_lift),
                    budget_frac=float(frac_used),
                    acceptance_per_eval=float(_sri_acc),
                    phase_code=0,
                    legacy_admission=_sri_legacy_admit,
                )
            else:
                _sri_admit = _sri_legacy_admit
            if not _sri_admit:
                _probe_rate = _probe_rate_clamped  # FE2-3: hoisted loop-invariant
                _sri_probe_active = bool(_probe_rate > 0.0 and rngs.control.random() < _probe_rate)
                interaction_linkage_ready = bool(_sri_probe_active)
        if _research_oracle_blocks is not None:
            # Oracle injection: force the exact ground-truth blocks through the
            # learned-linkage path every generation, bypassing graph readiness.
            interaction_learned_groups = _research_oracle_blocks
            interaction_linkage_ready = True
        linkage_groups_secondary: list[np.ndarray] | None = None
        linkage_primary_row_prob = 1.0
        _link_flat_secondary = None
        _link_offsets_secondary = None
        if linkage_blockwise_active:
            if linkage_random_groups is None or gen == 1 or ((gen - 1) % linkage_refresh_period == 0):
                linkage_random_groups = _make_linkage_groups(
                    dim=D, block_size=linkage_block_size, rng=rngs.link)
            linkage_groups = linkage_random_groups
            if interaction_linkage_ready and interaction_learned_groups:
                linkage_groups = [np.asarray(g, dtype=np.int64) for g in interaction_learned_groups]
                linkage_groups_secondary = linkage_random_groups
                # every generation that commits to
                # learned linkage groups counts as one subspace decision.
                if sp_nlpsr_state is not None:
                    sp_nlpsr_state.record_subspace_decision(1)
                linkage_primary_row_prob = (
                    _probe_rate_clamped  # FE2-3: hoisted loop-invariant
                    if _sri_probe_active else float(interaction_linkage_mix_prob)
                )
                # FC4 -- linkage_random_mix_late.  When the
                # rolling EMA of (learned_acc - random_acc) is negative,
                # the learned linkage is anti-helpful; mix in or fully
                # fall back to the random secondary groups by lowering
                # the primary-row prob.  Default (severe=0, negative=0,
                # strength=0) collapses to no-op.
                if (
                    _cfg_v4_fc4_enabled
                    and frac_used >= _cfg_v4_fc4_tau_floor
                    and not _sri_probe_active
                ):
                    if _v4_link_lift_ema <= _cfg_v4_fc4_severe_lift and _cfg_v4_fc4_severe_lift < 0.0:
                        linkage_primary_row_prob = 0.0
                    elif _v4_link_lift_ema <= _cfg_v4_fc4_negative_lift and _cfg_v4_fc4_strength > 0.0:
                        linkage_primary_row_prob = max(
                            0.0,
                            linkage_primary_row_prob * (1.0 - _cfg_v4_fc4_strength),
                        )
            linkage_group_count = len(linkage_groups) if linkage_groups is not None else 0
            _n_groups = linkage_group_count
            _g_sizes = np.array([int(g.size) for g in linkage_groups], dtype=np.int64) if linkage_groups else np.zeros((0,), dtype=np.int64)
            _link_offsets = np.empty(_n_groups + 1, dtype=np.int64)
            _link_offsets[0] = 0
            if _n_groups > 0:
                np.cumsum(_g_sizes, out=_link_offsets[1:])
                _total = int(_link_offsets[-1])
                _link_flat = np.empty(_total, dtype=np.int64)
                for _gi in range(_n_groups):
                    _link_flat[int(_link_offsets[_gi]):int(_link_offsets[_gi + 1])] = linkage_groups[_gi]
            else:
                _link_flat = None
            if linkage_groups_secondary:
                _n_groups2 = len(linkage_groups_secondary)
                _g_sizes2 = np.array([int(g.size) for g in linkage_groups_secondary], dtype=np.int64)
                _link_offsets_secondary = np.empty(_n_groups2 + 1, dtype=np.int64)
                _link_offsets_secondary[0] = 0
                np.cumsum(_g_sizes2, out=_link_offsets_secondary[1:])
                _total2 = int(_link_offsets_secondary[-1])
                _link_flat_secondary = np.empty(_total2, dtype=np.int64)
                for _gi in range(_n_groups2):
                    _link_flat_secondary[int(_link_offsets_secondary[_gi]):int(_link_offsets_secondary[_gi + 1])] = linkage_groups_secondary[_gi]
            if _n_groups == 0:
                linkage_blockwise_active = False
                _link_offsets = None
                _link_flat = None
                _link_offsets_secondary = None
                _link_flat_secondary = None
        else:
            linkage_groups = None
            linkage_group_count = 0
            _link_flat = None
            _link_offsets = None

        # Population-wide module gate: when ACE concentrates probability on
        # module-inactive entries (GSK-pure), BSE restarts are suppressed.
        if _cfg_ace_enabled:
            if dual_ace_top_bottom:
                module_prob_mass = float(
                    top_frac_current * np.sum(Kw_P_top[pool_modules])
                    + bottom_frac_current * np.sum(Kw_P_bottom[pool_modules])
                )
            else:
                module_prob_mass = float(np.sum(Kw_P[pool_modules]))
            if _module_gate_hysteresis:
                if _module_gate_state:
                    _module_gate_state = bool(module_prob_mass >= _cfg_ace_module_gate_low)
                else:
                    _module_gate_state = bool(module_prob_mass >= _cfg_ace_module_gate_high)
                pop_modules_active = bool(_module_gate_state)
            else:
                pop_modules_active = module_prob_mass >= _cfg_ace_module_gate_thresh
        else:
            module_prob_mass = 1.0
            pop_modules_active = True

        # S1: single reshape after all KF_i modifiers
        KF_col = KF_i.reshape(NP, 1)

        # --------------------------------------------------------------
        # Build junior/senior trial vectors (baseline formulas) and apply
        # L-SHADE midpoint bound repair in a single fused JIT pass (H2).
        # The fallback path runs the legacy three-phase Python sequence.
        # --------------------------------------------------------------
        # Reuse the pre-allocated NP_init-sized buffers; the [:NP, :] slice
        # is a C-contiguous view from offset 0, so the Numba kernels and the
        # NumPy fallback both see a (NP, D) array exactly as before.  This
        # eliminates 2 × NP × D × 8 B of np.empty + GC churn per generation.
        vi_junior = _vi_jun_buf[:NP, :]
        vi_senior = _vi_sen_buf[:NP, :]

        if build_junior_senior_with_repair_fast is not None:
            build_junior_senior_with_repair_fast(
                pop, fitness, KF_i,
                Rg1, Rg2, Rg3, R1, R2, R3,
                lu[0], lu[1],
                vi_junior, vi_senior,
            )
        elif build_junior_senior_fast is not None:
            build_junior_senior_fast(pop, fitness, KF_i,
                                      Rg1, Rg2, Rg3, R1, R2, R3,
                                      vi_junior, vi_senior)
            bound_constraint(vi_junior, pop, lu)
            bound_constraint(vi_senior, pop, lu)
        else:
            worse_mask = fitness > fitness[Rg3]
            better_mask = ~worse_mask

            # S6: skip redundant np.any guards — fancy indexing on
            # all-False masks is a zero-cost no-op.
            m = worse_mask
            vi_junior[m, :] = (
                pop[m, :]
                + KF_col[m, :] * (
                    pop[Rg1[m], :] - pop[Rg2[m], :] + pop[Rg3[m], :] - pop[m, :]
                )
            )
            m = better_mask
            vi_junior[m, :] = (
                pop[m, :]
                + KF_col[m, :] * (
                    pop[Rg1[m], :] - pop[Rg2[m], :] + pop[m, :] - pop[Rg3[m], :]
                )
            )

            worse_mask2 = fitness > fitness[R2]
            better_mask2 = ~worse_mask2

            m = worse_mask2
            vi_senior[m, :] = (
                pop[m, :]
                + KF_col[m, :] * (
                    pop[R1[m], :] - pop[R3[m], :] + pop[R2[m], :] - pop[m, :]
                )
            )
            m = better_mask2
            vi_senior[m, :] = (
                pop[m, :]
                + KF_col[m, :] * (
                    pop[R1[m], :] - pop[R3[m], :] + pop[m, :] - pop[R2[m], :]
                )
            )
            bound_constraint(vi_junior, pop, lu)
            bound_constraint(vi_senior, pop, lu)

        # Telemetry: boundary-repair detection for gen logs.
        # Detect L-SHADE midpoint repairs by exact equality with the
        # repair formula `0.5 * (pop + bound)`.  Both the Numba fast path
        # (`_build_junior_senior_with_repair_nb`) and the Python fallback
        # (`bound_constraint`) compute the same bit-identical scalar, so
        # exact equality detects every repair without false negatives.
        # False positives are only possible if a non-repaired component
        # happens to land exactly on the midpoint by numerical
        # coincidence — vanishingly unlikely in continuous float64.
        # Cost per gen: 4 (NP, D) bool buffers + 2 (NP, D) float buffers.
        #
        # (perf): this block is pure telemetry — its sole consumers
        # are the ``boundary_repairs_*`` gen-log fields inside the
        # ``generation_callback is not None`` gate below (~L4979).  When
        # no callback is registered (the production n=51 sweep), the work
        # is 100% wasted, so we gate it behind the SAME condition.  The
        # gate is applied IN PLACE here (before the pop replacement) so
        # ``_bd_pop = pop[:NP, :]`` still reads the *pre-replacement*
        # population, preserving the exact telemetry values.
        if generation_callback is not None:
            _bd_lo = lu[0]
            _bd_hi = lu[1]
            _bd_pop = pop[:NP, :]
            _bd_mid_lo = 0.5 * (_bd_pop + _bd_lo)
            _bd_mid_hi = 0.5 * (_bd_pop + _bd_hi)
            _boundary_repairs_jun = int(
                np.sum((vi_junior == _bd_mid_lo) | (vi_junior == _bd_mid_hi))
            )
            _boundary_repairs_sen = int(
                np.sum((vi_senior == _bd_mid_lo) | (vi_senior == _bd_mid_hi))
            )
            _boundary_total = int(2 * NP * D) if (NP > 0 and D > 0) else 0
            _boundary_hit_rate = (
                float(_boundary_repairs_jun + _boundary_repairs_sen)
                / float(_boundary_total)
                if _boundary_total > 0 else 0.0
            )

        # --------------------------------------------------------------
        # Crossover masks + KR gating
        # Linkage-aware crossover optionally replaces per-dimension Bernoulli masks with
        # blockwise linkage masks on a configurable fraction of rows.
        # --------------------------------------------------------------
        D_J, D_S, linkage_blockwise_rows, linkage_primary_rows, _link_primary_idx, _link_secondary_idx = _build_phase4_masks(
            rng_core=rngs.core,
            rng_link=rngs.link,
            NP=NP,
            D=D,
            p_junior_i=p_junior_i,
            KR_i=KR_i,
            linkage_active=linkage_blockwise_active,
            linkage_groups=linkage_groups,
            linkage_mix_prob=linkage_mix_prob_eff,
            linkage_groups_secondary=linkage_groups_secondary,
            linkage_primary_row_prob=linkage_primary_row_prob,
            _dj_buf=_dj_buf,
            _ds_buf=_ds_buf,
            _link_flat=_link_flat,
            _link_offsets=_link_offsets,
            _link_flat_secondary=_link_flat_secondary,
            _link_offsets_secondary=_link_offsets_secondary,
        )

        if interaction_linkage_ready and linkage_groups_secondary is not None:
            interaction_linkage_rows_learned = int(linkage_primary_rows)
            interaction_linkage_rows_random = int(linkage_blockwise_rows - linkage_primary_rows)
        elif interaction_linkage_ready:
            interaction_linkage_rows_learned = int(linkage_blockwise_rows)

        ui = _ui_buf[:NP, :]
        # W2.2 (2026-07-25): fused selection kernel replaces the full copy plus
        # two boolean fancy-index gather/scatter pairs (bit-identical for every
        # mask combination -- senior wins overlaps exactly as the sequential
        # writes did; pure selection, no arithmetic). 80% of assembly cost at
        # D=1000 per microbench. Fallback preserves the original sequence.
        if compose_trial_fast is not None:
            compose_trial_fast(pop, vi_junior, vi_senior, D_J, D_S, ui)
        else:
            np.copyto(ui, pop)
            ui[D_J] = vi_junior[D_J]
            ui[D_S] = vi_senior[D_S]

        # --------------------------------------------------------------
        # No-null-update guarantee (optional)
        # --------------------------------------------------------------
        if _cfg_force_nonzero_update:
            any_update = np.any(D_J, axis=1) | np.any(D_S, axis=1)
            missing = ~any_update
            if np.any(missing):
                idx_missing = np.nonzero(missing)[0]
                n_miss = int(idx_missing.size)

                j = rngs.core.integers(0, D, size=n_miss)  # S11: integers() returns int64

                u_phase = rngs.core.random(n_miss)
                use_junior = u_phase <= p_junior_i[idx_missing]

                rows = idx_missing
                cols = j

                if np.any(use_junior):
                    rj = rows[use_junior]
                    cj = cols[use_junior]
                    ui[rj, cj] = vi_junior[rj, cj]
                    D_J[rj, cj] = True

                if np.any(~use_junior):
                    rs = rows[~use_junior]
                    cs = cols[~use_junior]
                    ui[rs, cs] = vi_senior[rs, cs]
                    D_S[rs, cs] = True

        # Note: bound_constraint(ui) is NOT needed here — vi_junior and
        # vi_senior are already bounded (lines above), pop is always
        # bounded, and the DE path handles its own boundary repair.

        # Per-individual dimension coverage: fraction of dims updated.
        # W2.3 (2026-07-25): the logical_or into _dim_upd_buf was DEAD when the
        # numba kernel is active (the kernel reads D_J/D_S directly; the mask's
        # only reader is the numpy fallback) -- moved inside that fallback.
        # W2.4: the whole computation is skipped when no consumer exists
        # (coverage_i = None; the DE write and the telemetry mean are guarded).
        if _need_coverage:
            if dim_coverage_fast is not None:
                coverage_i = dim_coverage_fast(D_J, D_S, NP, D)
            else:
                dim_updated_mask = _dim_upd_buf[:NP, :]
                np.logical_or(D_J, D_S, out=dim_updated_mask)
                coverage_i = np.sum(dim_updated_mask, axis=1).astype(np.float64) / float(D)  # (NP,)
        else:
            coverage_i = None

        # --------------------------------------------------------------
        # DE/rand/1 operator for individuals sampled from DE entry.
        # Overwrites their ui rows with DE trial vectors. This operator
        # inherently updates all D dimensions (via binomial crossover
        # with CR≈0.9), solving the dimensional coverage problem.
        # --------------------------------------------------------------
        if de_entry_idx >= 0 and _cfg_ace_enabled and de_policy_active:
            de_mask = (s_idx == de_entry_idx)
            n_de = int(np.sum(de_mask))
            if n_de > 0:
                de_indices = np.nonzero(de_mask)[0]
                de_used_rows[de_indices] = True

                de_F = _cfg_ace_de_F  # scalar
                de_CR = _cfg_ace_de_CR

                # fully vectorized DE/rand/1 — replaces the per-individual
                # Python loop.  Donor selection uses an argpartition-on-uniform
                # -keys trick that yields uniformly random *ordered* triples
                # (statistically equivalent to ``rng.choice(replace=False)``)
                # while masking self via +inf so that the chosen indices are
                # all distinct from ``ii``.
                #
                # H6b: switched from full ``argsort`` to ``argpartition`` so
                # the per-row cost drops from O(NP log NP) to O(NP).  We then
                # sort just the 3 partitioned elements to recover the ordered
                # triple — the result is bit-identical to the old argsort path
                # because the underlying float keys are unique.
                inv_D = 1.0 / float(D)
                keys = rngs.de.random((n_de, NP))
                keys[_arange_int_buf[:n_de], de_indices] = np.inf
                if NP > 3:
                    part = np.argpartition(keys, 3, axis=1)[:, :3]
                    part_keys = np.take_along_axis(keys, part, axis=1)
                    order = np.argsort(part_keys, axis=1, kind="stable")
                    donors = np.take_along_axis(part, order, axis=1)
                else:
                    # Population too small to partition; fall back to sort.
                    donors = np.argsort(keys, axis=1, kind="stable")[:, :3]
                r1 = donors[:, 0]
                r2 = donors[:, 1]
                r3 = donors[:, 2]

                # DE/rand/1 mutation, batched (n_de, D). Per-individual F
                # broadcasts as (n_de,1) when shade_memory is active.
                mutants = pop[r1, :] + de_F * (pop[r2, :] - pop[r3, :])

                # Binomial crossover masks with forced-update dimension.
                # Per-individual CR threshold supported via column broadcast.
                cr_masks = rngs.de.random((n_de, D)) < de_CR
                forced_dims = rngs.de.integers(0, D, size=n_de)
                cr_masks[_arange_int_buf[:n_de], forced_dims] = True

                # DE: merge mutation + boundary repair into a single
                # extract → mutate → repair → write-back cycle.
                ui_de = ui[de_indices]
                np.copyto(ui_de, mutants, where=cr_masks)

                # Coverage update — vectorized count of True per row
                if coverage_i is not None:   # W2.4: skipped with the kernel
                    coverage_i[de_indices] = cr_masks.sum(axis=1).astype(np.float64) * inv_D

                # Midpoint boundary repair (same as GSK trials) for fairness
                bound_constraint(ui_de, pop[de_indices], lu)
                ui[de_indices] = ui_de

        # TR-GSK trust-region displacement governor removed in
        # v4.1-paper-freeze (runtime-dead: trust_enabled was always
        # False).  The clip-rate telemetry stays pinned at 0.0.
        terra_trust_clip_rate = 0.0

        # --------------------------------------------------------------
        # Evaluate + selection
        # --------------------------------------------------------------
        fitness_old = _fitness_old_buf[:NP]
        np.copyto(fitness_old, fitness)

        child_fit_eval, n_child = budget.eval_batch_safe(ui)
        child_fit = _child_fit_buf[:NP]
        child_fit[:] = np.inf
        if n_child > 0:
            child_fit[:n_child] = np.asarray(child_fit_eval, dtype=np.float64)

        improved = child_fit <= fitness
        improved[n_child:] = False

        # A1 -- late_tau_acceptance_clip.
        # When D >= 100 V4 variants enable A1 AND we are in late-budget tau
        # AND prior rolling acceptance was high AND the log-drop EMA was
        # below eps for ``streak_k`` consecutive gens, tighten the elitist
        # acceptance to require strict relative improvement of at least
        # ``strict_eps * |fitness|``.  This is a MASK tightening only --
        # no RNG, no sort, no FE change.  Default (streak_k=0) collapses.
        if (
            _cfg_v4_a1_enabled
            and _cfg_v4_a1_streak_k > 0
            and _v4_logdrop_streak >= _cfg_v4_a1_streak_k
            and frac_used >= _cfg_v4_a1_tau_floor
            and _cfg_v4_a1_strict_eps > 0.0
        ):
            _v4_a1_prev_acc = (sum(acceptance_hist) / len(acceptance_hist)) if acceptance_hist else 0.0
            if _v4_a1_prev_acc >= _cfg_v4_a1_acc_high:
                _v4_a1_thresh = fitness - _cfg_v4_a1_strict_eps * np.abs(fitness)
                improved = child_fit < _v4_a1_thresh
                improved[n_child:] = False

        # H3: scalar JIT popcount over the bool array, ~2-4x faster than
        # numpy's reduction for the typical NP<=200 case.
        if count_true_fast is not None:
            accepted = int(count_true_fast(improved))
        else:
            accepted = int(np.sum(improved))

        # S1: compute the improved-index array ONCE and reuse it in all
        # downstream blocks (NM-track, archive, relative-rewards).
        idx_imp = np.nonzero(improved)[0] if accepted > 0 else np.empty(0, dtype=np.intp)

        # S6: cache improvement deltas for relative-rewards and generation log.
        if accepted > 0:
            _imp_deltas = fitness_old[idx_imp] - child_fit[idx_imp]
            _imp_deltas_pos = np.maximum(_imp_deltas, 0.0)
        else:
            _imp_deltas = np.empty(0, dtype=np.float64)
            _imp_deltas_pos = _imp_deltas


        accepted_displacements = np.empty((0, D), dtype=np.float64)
        accepted_sgsm_weights = np.empty((0,), dtype=np.float64)
        # W2.6 (2026-07-25): the gather's ONLY consumers are the subspace-NM
        # displacement buffer (_track_disp_vectors) and the SGSM update
        # (interaction_state is not None); the DT2 shadow computes its own
        # displacements. Below D50 (interaction_state None) and with coordinate
        # LS this O(K*D) gather had no observer.
        if accepted > 0 and (interaction_state is not None or _track_disp_vectors):
            accepted_displacements = ui[idx_imp, :] - pop[idx_imp, :]  # before replacement

        # DT2 shadow estimator (research; default None -> pub byte-identical).
        # Accumulate accepted (M+) and rejected (M-) co-movement + a range-normalized
        # variant, for offline contrastive fidelity screening (H3 self-confirmation).
        # Pure reads of ui/pop/improved/span before replacement; no RNG, no state
        # mutation, so the trajectory is unchanged.
        if research_shadow_estimator is not None:
            _se = research_shadow_estimator
            if "Mplus" not in _se:
                for _k in ("Mplus", "Mminus", "Mrange", "Cplus", "Cminus"):
                    _se[_k] = np.zeros((D, D), dtype=np.float64)
                _se["nplus"] = 0
                _se["nminus"] = 0
            _seAcc = np.abs(ui[improved, :] - pop[improved, :])
            _seRej = np.abs(ui[~improved, :] - pop[~improved, :])
            if _seAcc.shape[0]:
                _se["Mplus"] += _seAcc.T @ _seAcc
                _seB = (_seAcc > 0.0).astype(np.float64)
                _se["Cplus"] += _seB.T @ _seB
                _seN = _seAcc / span
                _se["Mrange"] += _seN.T @ _seN
                _se["nplus"] += int(_seAcc.shape[0])
            if _seRej.shape[0]:
                _se["Mminus"] += _seRej.T @ _seRej
                _seRb = (_seRej > 0.0).astype(np.float64)
                _se["Cminus"] += _seRb.T @ _seRb
                _se["nminus"] += int(_seRej.shape[0])

        if accepted > 0:

            # Track successful displacements for subspace NM
            if _track_disp_vectors:
                for _disp in accepted_displacements:
                    _dnorm = float(np.linalg.norm(_disp))
                    if _dnorm > 1e-15:
                        _disp_buf.append(_disp / _dnorm)  # unit direction
                        if len(_disp_buf) > _disp_buf_max:
                            _disp_buf.pop(0)

            if interaction_state is not None:
                accepted_sgsm_weights = np.ones((accepted_displacements.shape[0],), dtype=np.float64)
                accepted_from_de = de_used_rows[idx_imp] if idx_imp.size > 0 else np.zeros((0,), dtype=bool)
                if accepted_from_de.size > 0:
                    accepted_sgsm_weights[accepted_from_de] = interaction_de_update_weight
                    interaction_updates_from_de = int(np.sum(np.logical_and(accepted_from_de, accepted_sgsm_weights > 0.0)))

            pop[improved, :] = ui[improved, :]
            fitness[improved] = child_fit[improved]

            # Archive update on accepted solutions (H7: batched).
            if archive is not None and idx_imp.size > 0:
                archive_insertions += archive.consider_batch(pop[idx_imp], fitness[idx_imp])
            if basin_memory is not None and idx_imp.size > 0:
                # Descriptor memory is updated from accepted basins only; it is
                # never used as a DE difference donor.
                _best_accept_idx = idx_imp[int(np.argmin(fitness[idx_imp]))]
                basin_memory.add(pop[_best_accept_idx], float(fitness[_best_accept_idx]), span, improved=True)

        if linkage_reliability_state is not None:
            if linkage_groups_secondary is not None:
                _sri_learned_idx = _link_primary_idx
                _sri_random_idx = _link_secondary_idx
            else:
                _sri_learned_idx = np.empty((0,), dtype=np.int64)
                _sri_random_idx = _link_primary_idx
            linkage_reliability_state.update(
                learned_success=(int(np.sum(improved[_sri_learned_idx])) if _sri_learned_idx.size > 0 else 0),
                learned_total=int(_sri_learned_idx.size),
                random_success=(int(np.sum(improved[_sri_random_idx])) if _sri_random_idx.size > 0 else 0),
                random_total=int(_sri_random_idx.size),
            )
            linkage_reliability_state.refresh()

        if interaction_state is not None:
            frac_used_after_update = (budget.nfes_used / float(max_nfes)) if max_nfes > 0 else 1.0
            if frac_used_after_update >= interaction_graph_warmup_frac:
                _do_sgsm_update = (int(gen) % int(interaction_update_period) == 0)
                _disp_sgsm = accepted_displacements
                _imp_sgsm = _imp_deltas_pos
                _w_sgsm = accepted_sgsm_weights if accepted_sgsm_weights.size > 0 else None
                if _do_sgsm_update and interaction_update_max_samples > 0 and _imp_sgsm.size > interaction_update_max_samples:
                    # Deterministic top-improvement thinning keeps high-D SGSM runtime bounded
                    # without consuming RNG or extra objective calls.
                    _ord_sgsm = np.argsort(-_imp_sgsm, kind="mergesort")[:interaction_update_max_samples]
                    _disp_sgsm = _disp_sgsm[_ord_sgsm, :]
                    _imp_sgsm = _imp_sgsm[_ord_sgsm]
                    if _w_sgsm is not None:
                        _w_sgsm = _w_sgsm[_ord_sgsm]
                if not _do_sgsm_update:
                    # Preserve passive decay between structural updates.
                    _disp_sgsm = np.empty((0, D), dtype=np.float64)
                    _imp_sgsm = np.empty((0,), dtype=np.float64)
                    _w_sgsm = None
                ig_update_from_accepted(
                    interaction_state,
                    displacements=_disp_sgsm,
                    improvements=_imp_sgsm,
                    decay=interaction_graph_decay,
                    lr=interaction_graph_lr,
                    sample_weights=_w_sgsm,
                )
                _v4_eff_refresh_period = interaction_graph_refresh_period
                _v4_eff_block_max_size = interaction_block_max_size
                _v4_should_refresh = bool(
                    interaction_state.updates > 0 and (
                        not interaction_state.blocks
                        or (gen % _v4_eff_refresh_period == 0)
                    )
                )
                if _v4_should_refresh:
                    ig_extract_blocks(
                        interaction_state,
                        edge_floor=interaction_graph_edge_floor,
                        min_block_size=interaction_block_min_size,
                        max_block_size=_v4_eff_block_max_size,
                        gen=int(gen),
                    )
                    interaction_learned_groups = ig_expand_blocks_with_singletons(interaction_state, dim=D) if interaction_state.blocks else None

        relative_rewards = _rewards_buf[:NP]; relative_rewards[:] = 0.0
        if accepted > 0:
            denom = np.abs(fitness_old[idx_imp]) + 1e-12
            relative_rewards[idx_imp] = np.maximum(
                0.0,
                _imp_deltas / denom,
            )

        if _cfg_ace_enabled:
            # H1: collapse 9 separate bincount passes into one fused JIT pass
            # over (s_idx, improved, top_half_mask, bottom_half_mask, rewards).
            # Bit-identical to the bincount path because the iteration order
            # over ``s_idx`` is the same — float accumulation respects index
            # order, so the seed-locked main loop is unaffected.
            if ace_bincount_fused_fast is not None:
                (
                    ace_sample_counts_arr,
                    ace_success_counts_arr,
                    ace_reward_sums_arr,
                    ace_sample_counts_top_arr,
                    ace_sample_counts_bottom_arr,
                    ace_success_counts_top_arr,
                    ace_success_counts_bottom_arr,
                    _ace_reward_sums_top_arr,
                    _ace_reward_sums_bottom_arr,
                ) = ace_bincount_fused_fast(
                    s_idx.astype(np.int64, copy=False),
                    improved,
                    top_half_mask,
                    bottom_half_mask,
                    relative_rewards,
                    M,
                )
            else:
                ace_sample_counts_arr = np.bincount(s_idx, minlength=M).astype(np.int64)
                ace_success_counts_arr = np.bincount(s_idx[idx_imp], minlength=M).astype(np.int64)
                ace_reward_sums_arr = np.bincount(s_idx, weights=relative_rewards, minlength=M)
                ace_sample_counts_top_arr = np.bincount(s_idx[top_half_mask], minlength=M).astype(np.int64)
                ace_sample_counts_bottom_arr = np.bincount(s_idx[bottom_half_mask], minlength=M).astype(np.int64)
                ace_success_counts_top_arr = np.bincount(
                    s_idx[idx_imp[top_half_mask[idx_imp]]],
                    minlength=M,
                ).astype(np.int64)
                ace_success_counts_bottom_arr = np.bincount(
                    s_idx[idx_imp[bottom_half_mask[idx_imp]]],
                    minlength=M,
                ).astype(np.int64)
                _ace_reward_sums_top_arr = np.bincount(
                    s_idx[top_half_mask],
                    weights=relative_rewards[top_half_mask],
                    minlength=M,
                )
                _ace_reward_sums_bottom_arr = np.bincount(
                    s_idx[bottom_half_mask],
                    weights=relative_rewards[bottom_half_mask],
                    minlength=M,
                )
        else:
            ace_sample_counts_arr = _ace_empty_int
            ace_sample_counts_top_arr = _ace_empty_int
            ace_sample_counts_bottom_arr = _ace_empty_int
            ace_success_counts_arr = _ace_empty_int
            ace_success_counts_top_arr = _ace_empty_int
            ace_success_counts_bottom_arr = _ace_empty_int
            ace_reward_sums_arr = _ace_empty_float

        # Update best from current population.
        best_idx = int(np.argmin(fitness))
        best_f = float(fitness[best_idx])

        # --------------------------------------------------------------
        # V4 -- end-of-generation state update (A1/A2 streaks + EMAs).
        # Pure read-only of best_f / acceptance_hist; produces no RNG, no
        # sort, no FE.  When all V4 toggles are False, the streaks update
        # but no downstream code reads them ⇒ byte-identical V3-locked.
        # --------------------------------------------------------------
        # log_drop = max(0, log10(prev_best - best + eps_tiny)) -- larger
        # = better progress.  When prev_best == best, log_drop = log10(eps)
        # which is very negative ⇒ "no progress" signal.  We track an EMA
        # using late_accept_clip alpha; alpha=0 means no EMA (raw value).
        _v4_eps_tiny = 1e-30
        _v4_drop_raw = max(0.0, _v4_prev_best_f - best_f)
        _v4_log_drop_now = math.log10(_v4_drop_raw + _v4_eps_tiny)
        _v4_alpha = _cfg_v4_a1_logdrop_alpha
        if _v4_alpha > 0.0:
            _v4_log_drop_ema = (1.0 - _v4_alpha) * _v4_log_drop_ema + _v4_alpha * _v4_log_drop_now
        else:
            _v4_log_drop_ema = _v4_log_drop_now
        _v4_prev_best_f = best_f
        # A1 streak: gens with low log_drop AND high acceptance.
        _v4_acc_now = (sum(acceptance_hist) / len(acceptance_hist)) if acceptance_hist else 0.0
        if (
            _v4_log_drop_ema < _cfg_v4_a1_log_drop_eps
            and _v4_acc_now >= _cfg_v4_a1_acc_high
        ):
            _v4_logdrop_streak += 1
        else:
            _v4_logdrop_streak = 0
        # A2 streak: gens with low acceptance AND low log_drop (frozen).
        if (
            _v4_log_drop_ema < _cfg_v4_a2_log_drop_eps
            and _v4_acc_now < _cfg_v4_a2_acc_floor
        ):
            _v4_frozen_streak += 1
        else:
            _v4_frozen_streak = 0
        # A2 cooldown / window decrements.
        if _v4_a2_window_remaining > 0:
            _v4_a2_window_remaining -= 1
        if _v4_a2_cooldown_remaining > 0:
            _v4_a2_cooldown_remaining -= 1
        # A2 trigger: frozen streak met, not in cooldown, no active window.
        if (
            _cfg_v4_a2_enabled
            and _cfg_v4_a2_streak_k > 0
            and _cfg_v4_a2_window_m > 0
            and _cfg_v4_a2_factor != 1.0
            and _v4_frozen_streak >= _cfg_v4_a2_streak_k
            and _v4_a2_cooldown_remaining == 0
            and _v4_a2_window_remaining == 0
        ):
            _v4_a2_window_remaining = _cfg_v4_a2_window_m
            _v4_a2_cooldown_remaining = _cfg_v4_a2_window_m + _cfg_v4_a2_cooldown
            _v4_frozen_streak = 0
        # --------------------------------------------------------------
        # ACE probability update (after ace_start_frac budget)
        # --------------------------------------------------------------
        if _cfg_ace_enabled:
            frac_used_after = (budget.nfes_used / float(max_nfes)) if max_nfes > 0 else 1.0
            if frac_used_after >= _cfg_ace_start_frac and n_child > 0:
                # Eq. (7): omega per setting is sum( f_new - f_old ) over individuals
                delta = child_fit[:n_child] - fitness_old[:n_child]

                # Coverage-weighted feedback: scale each individual's delta
                # by the fraction of dimensions it actually updated.
                # This prevents low-KR entries from accumulating inflated
                # reward from easy-to-accept baby-step improvements.
                #
                # CRITICAL: Only weight IMPROVEMENTS (delta < 0), not worsenings.
                # Weighting worsenings amplifies the noise from high-KR entries
                # (many worsening trials × large weight), drowning the signal.
                if _cfg_ace_coverage_weighted:
                    cov_weight = np.power(coverage_i[:n_child], _cfg_ace_coverage_exponent)
                    improved_mask = delta < 0.0
                    # Improvements: weight by coverage^exp (low-KR discounted)
                    # Worsenings: zero them out so they don't pollute the signal
                    delta = np.where(improved_mask, delta * cov_weight, 0.0)
                if dual_ace_top_bottom:
                    top_eval_mask = top_half_mask[:n_child]
                    bottom_eval_mask = bottom_half_mask[:n_child]
                    if np.any(top_eval_mask):
                        omega_top = np.bincount(
                            s_idx[:n_child][top_eval_mask],
                            weights=delta[top_eval_mask],
                            minlength=M,
                        ).astype(np.float64)
                        Kw_P_top = _ace_update_probs(
                            Kw_P_top,
                            omega_top,
                            c=_cfg_ace_learning_rate,
                            p_min=_cfg_ace_min_prob,
                        )
                    if np.any(bottom_eval_mask):
                        omega_bottom = np.bincount(
                            s_idx[:n_child][bottom_eval_mask],
                            weights=delta[bottom_eval_mask],
                            minlength=M,
                        ).astype(np.float64)
                        Kw_P_bottom = _ace_update_probs(
                            Kw_P_bottom,
                            omega_bottom,
                            c=_cfg_ace_learning_rate,
                            p_min=_cfg_ace_min_prob,
                        )
                    Kw_P = (top_frac_current * Kw_P_top) + (bottom_frac_current * Kw_P_bottom)
                    Kw_P = _ace_project_probs(Kw_P, p_min=_cfg_ace_min_prob)
                else:
                    omega = np.bincount(
                        s_idx[:n_child],
                        weights=delta,
                        minlength=M,
                    ).astype(np.float64)
                    Kw_P = _ace_update_probs(
                        Kw_P,
                        omega,
                        c=_cfg_ace_learning_rate,
                        p_min=_cfg_ace_min_prob,
                    )
                    # S4: skip unnecessary copies in single-ACE mode.
                    Kw_P_top = Kw_P
                    Kw_P_bottom = Kw_P

        # --------------------------------------------------------------
        # ARGP: Acceptance-Rate Gated Pool Pruning
        # Track per-entry rolling acceptance rate and freeze entries
        # whose rate drops below threshold after warmup.
        # --------------------------------------------------------------
        if _cfg_argp_enabled and _cfg_ace_enabled:
            # Update ring buffer with this generation's per-entry stats
            argp_ring_succ[argp_ring_idx, :] = ace_success_counts_arr[:M]
            argp_ring_samp[argp_ring_idx, :] = ace_sample_counts_arr[:M]
            argp_ring_succ_top[argp_ring_idx, :] = ace_success_counts_top_arr[:M]
            argp_ring_samp_top[argp_ring_idx, :] = ace_sample_counts_top_arr[:M]
            argp_ring_succ_bottom[argp_ring_idx, :] = ace_success_counts_bottom_arr[:M]
            argp_ring_samp_bottom[argp_ring_idx, :] = ace_sample_counts_bottom_arr[:M]
            argp_ring_idx = (argp_ring_idx + 1) % _cfg_argp_window

            # Compute rolling acceptance rate per entry
            total_succ = argp_ring_succ.sum(axis=0).astype(np.float64)
            total_samp = argp_ring_samp.sum(axis=0).astype(np.float64)
            safe_samp = np.maximum(total_samp, 1.0)  # avoid 0/0 warning
            argp_rolling_acc = np.where(
                total_samp > 0,
                total_succ / safe_samp,
                0.0,
            )
            total_succ_top = argp_ring_succ_top.sum(axis=0).astype(np.float64)
            total_samp_top = argp_ring_samp_top.sum(axis=0).astype(np.float64)
            safe_samp_top = np.maximum(total_samp_top, 1.0)
            argp_rolling_acc_top = np.where(
                total_samp_top > 0,
                total_succ_top / safe_samp_top,
                0.0,
            )
            total_succ_bottom = argp_ring_succ_bottom.sum(axis=0).astype(np.float64)
            total_samp_bottom = argp_ring_samp_bottom.sum(axis=0).astype(np.float64)
            safe_samp_bottom = np.maximum(total_samp_bottom, 1.0)
            argp_rolling_acc_bottom = np.where(
                total_samp_bottom > 0,
                total_succ_bottom / safe_samp_bottom,
                0.0,
            )

            # Apply pruning after warmup
            frac_now = (budget.nfes_used / float(max_nfes)) if max_nfes > 0 else 1.0
            if frac_now >= _cfg_argp_warmup_frac:
                if dual_ace_top_bottom and _cfg_argp_preserve_split_memory and _cfg_argp_freeze_scope == "per_half":
                    if _cfg_argp_guarded_split:
                        Kw_P_top, argp_frozen_top, argp_low_streak_top = _argp_update_memory_probs_guarded(
                            Kw_P_top,
                            argp_frozen_top,
                            argp_rolling_acc_top,
                            total_samp_top,
                            argp_low_streak_top,
                            threshold=_cfg_argp_threshold_top,
                            p_min=_cfg_ace_min_prob,
                            min_active=2,
                            confirm_windows=_cfg_argp_confirm_windows,
                            max_frozen_frac=_cfg_argp_max_frozen_frac,
                            frozen_prob_floor=_cfg_argp_frozen_prob_floor,
                        )
                        Kw_P_bottom, argp_frozen_bottom, argp_low_streak_bottom = _argp_update_memory_probs_guarded(
                            Kw_P_bottom,
                            argp_frozen_bottom,
                            argp_rolling_acc_bottom,
                            total_samp_bottom,
                            argp_low_streak_bottom,
                            threshold=_cfg_argp_threshold_bottom,
                            p_min=_cfg_ace_min_prob,
                            min_active=2,
                            confirm_windows=_cfg_argp_confirm_windows,
                            max_frozen_frac=_cfg_argp_max_frozen_frac,
                            frozen_prob_floor=_cfg_argp_frozen_prob_floor,
                        )
                    else:
                        Kw_P_top, argp_frozen_top = _argp_update_memory_probs(
                            Kw_P_top,
                            argp_frozen_top,
                            argp_rolling_acc_top,
                            total_samp_top,
                            threshold=_cfg_argp_threshold_top,
                            p_min=_cfg_ace_min_prob,
                            min_active=2,
                        )
                        Kw_P_bottom, argp_frozen_bottom = _argp_update_memory_probs(
                            Kw_P_bottom,
                            argp_frozen_bottom,
                            argp_rolling_acc_bottom,
                            total_samp_bottom,
                            threshold=_cfg_argp_threshold_bottom,
                            p_min=_cfg_ace_min_prob,
                            min_active=2,
                        )
                    argp_frozen = np.logical_or(argp_frozen_top, argp_frozen_bottom)
                    Kw_P = (top_frac_current * Kw_P_top) + (bottom_frac_current * Kw_P_bottom)
                    Kw_P = _ace_project_probs(Kw_P, p_min=_cfg_ace_min_prob)
                else:
                    p_min = _cfg_ace_min_prob
                    n_unfrozen = int(np.sum(~argp_frozen))

                    for k in range(M):
                        if argp_frozen[k]:
                            continue
                        if n_unfrozen <= 2:
                            # Keep at least 2 active entries
                            break
                        if argp_rolling_acc[k] < _cfg_argp_threshold:
                            argp_frozen[k] = True
                            n_unfrozen -= 1

                    # ── ARGP recovery: unfreeze entries that have recovered ──
                    for k in range(M):
                        if argp_frozen[k] and total_samp[k] > 0:
                            if argp_rolling_acc[k] >= _cfg_argp_threshold:
                                argp_frozen[k] = False

                    # Redistribute: frozen entries get p_min, rest share remainder
                    if np.any(argp_frozen):
                        n_frozen = int(np.sum(argp_frozen))
                        frozen_mass = n_frozen * p_min
                        remaining_mass = 1.0 - frozen_mass
                        unfrozen_mask = ~argp_frozen

                        if remaining_mass > 0 and np.any(unfrozen_mask):
                            # Scale unfrozen probs to fill remaining mass
                            unfrozen_sum = float(np.sum(Kw_P[unfrozen_mask]))
                            if unfrozen_sum > 0:
                                scale = remaining_mass / unfrozen_sum
                                Kw_P[unfrozen_mask] *= scale
                            else:
                                # Uniform among unfrozen
                                Kw_P[unfrozen_mask] = remaining_mass / np.sum(unfrozen_mask)
                            Kw_P[argp_frozen] = p_min

                        # S4: skip unnecessary copies in single-ACE mode.
                        Kw_P_top = Kw_P
                        Kw_P_bottom = Kw_P

                    argp_frozen_top[:] = argp_frozen
                    argp_frozen_bottom[:] = argp_frozen
                    argp_rolling_acc_top[:] = argp_rolling_acc
                    argp_rolling_acc_bottom[:] = argp_rolling_acc

        # --------------------------------------------------------------
        # Escape signals + budget-safe partial restart
        # --------------------------------------------------------------
        acceptance_now = (float(accepted) / float(n_child)) if n_child > 0 else 0.0
        acceptance_hist.append(float(acceptance_now))
        diversity_hist.append(float(div_rad))
        # S3: pure-Python mean for small deques — zero allocation.
        signal_acceptance_mean = sum(acceptance_hist) / len(acceptance_hist) if acceptance_hist else 0.0
        signal_diversity_mean = sum(diversity_hist) / len(diversity_hist) if diversity_hist else 0.0

        stagnation.push(best_f)
        stagnation_triggered = stagnation.triggered()

        _bse_acc_floor = _cfg_bse_acceptance_floor
        _bse_div_floor = float(bse_diversity_floor)

        low_acceptance_triggered = (
            len(acceptance_hist) >= signal_window
            and signal_acceptance_mean <= _bse_acc_floor
        )
        low_diversity_triggered = signal_diversity_mean <= _bse_div_floor

        if _bse_triple:
            escape_triggered = (
                bool(stagnation_triggered)
                and bool(low_acceptance_triggered)
                and bool(low_diversity_triggered)
            )
        else:
            escape_triggered = bool(stagnation_triggered)

        restart_triggered = False
        if budget_policy_enabled:
            # PTR is removed (runtime-dead), so the BAPC heat/exploration-debt
            # gate is gone.  Fall back to a PTR-free schedule: allow late-phase
            # local search (tau >= 0.70) and never block BSE escapes downstream
            # of BSE's own conditions.  This reproduces the prior runtime
            # behaviour exactly, because ``ptr_enabled`` was always False so the
            # heat-driven branch never executed.
            _tau = (float(budget.nfes_used) / float(max_nfes)) if max_nfes > 0 else 1.0
            terra_escape_allowed = True
            terra_ls_allowed = bool(_tau >= 0.70)
        else:
            terra_escape_allowed = True
            terra_ls_allowed = True

        if _cfg_bse_enabled and pop_modules_active:
            frac_used_after = (budget.nfes_used / float(max_nfes)) if max_nfes > 0 else 1.0
            can_escape = (
                restarts_done < _cfg_bse_max_restarts
                and frac_used_after < _cfg_bse_stop_frac
                and int(budget.nfes_used) >= int(cooldown_until_nfes)
                and escape_triggered
                and (terra_escape_allowed or not budget_policy_enabled)
            )
            if can_escape:
                best_before_escape = float(best_f)
                rank = np.argsort(fitness, kind="mergesort")

                if _cfg_bse_freeze_elites:
                    n_freeze = max(1, _round_half_up(_cfg_bse_freeze_frac * float(NP)))
                    n_freeze = min(n_freeze, NP - 1)
                else:
                    n_freeze = 0

                restart_pool = rank[n_freeze:]

                if (
                    restart_pool.size > 0
                    and _cfg_bse_cauchy_enabled
                ):
                    n_cauchy = max(1, _round_half_up(_cfg_bse_cauchy_frac * float(NP)))
                    n_cauchy = min(n_cauchy, int(restart_pool.size), int(budget.remaining()))
                    if n_cauchy > 0:
                        idx_cauchy = restart_pool[-n_cauchy:]
                        X_cauchy = pop[idx_cauchy, :].copy()
                        z = cauchy_like(rngs.div, n_cauchy, D)
                        X_cauchy += (_cfg_bse_cauchy_scale * inv_sqrt_d * span) * z
                        bound_constraint(X_cauchy, pop[idx_cauchy, :], lu)
                        y_cauchy, n_eval_c = budget.eval_batch_safe(X_cauchy)
                        y_cauchy = np.asarray(y_cauchy, dtype=np.float64)
                        if n_eval_c > 0:
                            y_old = fitness[idx_cauchy[:n_eval_c]]
                            use_cauchy = y_cauchy[:n_eval_c] <= y_old
                            if np.any(use_cauchy):
                                sel = idx_cauchy[:n_eval_c][use_cauchy]
                                pop[sel, :] = X_cauchy[:n_eval_c, :][use_cauchy, :]
                                fitness[sel] = y_cauchy[:n_eval_c][use_cauchy]
                                if archive is not None:
                                    archive_insertions += archive.consider_batch(pop[sel], fitness[sel])
                            cauchy_triggered = True
                            n_cauchy_perturbed = int(n_eval_c)
                            best_idx = int(np.argmin(fitness))
                            best_f = float(fitness[best_idx])
                            if best_f < best_before_escape:
                                stagnation.reset()
                                stagnation.push(best_f)
                                escape_triggered = False

                if (
                    escape_triggered
                    and restart_pool.size > 0
                ):
                    n_restart = max(1, _round_half_up(_cfg_bse_restart_frac * float(NP)))
                    n_restart = min(n_restart, int(restart_pool.size), NP)
                    idx_restart = restart_pool[-n_restart:]

                    rem = int(budget.remaining())
                    n_restart_actual = min(n_restart, rem)
                    if n_restart_actual > 0:
                        idx_restart = idx_restart[:n_restart_actual]

                        X_new = np.empty((n_restart_actual, D), dtype=np.float64)
                        use_arch = np.zeros((n_restart_actual,), dtype=bool)
                        if archive is not None and len(archive) > 0:
                            u = rngs.bse.random(n_restart_actual)
                            use_arch = u < _cfg_bse_archive_inject_prob

                        if np.any(use_arch) and archive is not None:
                            idxs = np.nonzero(use_arch)[0]
                            for _, j in enumerate(idxs):
                                sample = archive.sample(rngs.arch)
                                if sample is None:
                                    use_arch[j] = False
                                    continue
                                archive_samples_used += 1
                                x0, _f0 = sample
                                jitter = (rngs.bse.random(D) - 0.5) * 2.0
                                X_new[j, :] = x0 + (_cfg_bse_jitter_scale * inv_sqrt_d * span) * jitter

                        if np.any(~use_arch):
                            idxs = np.nonzero(~use_arch)[0]
                            if basin_memory is not None and len(basin_memory) > 0:
                                # TERRA BMNP: choose restart candidates by basin novelty
                                # from an unevaluated candidate pool.  This uses no extra
                                # function evaluations and does not create archive-difference
                                # donors; it only changes where restart replacements are sampled.
                                # Use a distinct local name so we do not shadow the outer
                                # ACE ``pool`` (which is the (M, 3) Kw / KR / Kexp tuple table).
                                _basin_pool_n = max(int(idxs.size), int(idxs.size) * int(max(1, int(config.basin_restart_pool_mult))))
                                _basin_pool = lower + rngs.basin.random((_basin_pool_n, D)) * span
                                # when failure tracking is on,
                                # compute a PTR-phase-coupled failure weight so
                                # the anti-restart-trap pressure is strongest in
                                # the escape phase and routine elsewhere.  When
                                # the flag is off, fall back to the pre-Phase-5
                                # 0.05 hard-coded weight (byte-stable default).
                                _bmnp_fw = 0.05
                                novelty = basin_memory.novelty_scores(_basin_pool, span, failure_weight=_bmnp_fw)
                                chosen = np.argsort(novelty, kind="mergesort")[-int(idxs.size):]
                                X_new[idxs, :] = _basin_pool[chosen, :]
                                basin_novelty_fires += 1
                            else:
                                X_new[idxs, :] = lower + rngs.bse.random((int(idxs.size), D)) * span

                        bound_constraint(X_new, pop[idx_restart, :], lu)

                        y_new, n_eval = budget.eval_batch_safe(X_new)
                        y_new = np.asarray(y_new, dtype=np.float64)

                        if n_eval > 0:
                            pop[idx_restart[:n_eval], :] = X_new[:n_eval, :]
                            fitness[idx_restart[:n_eval]] = y_new[:n_eval]

                            if archive is not None:
                                _restart_sel = idx_restart[:n_eval]
                                archive_insertions += archive.consider_batch(pop[_restart_sel], fitness[_restart_sel])
                            if basin_memory is not None and n_eval > 0:
                                _best_restart_local = int(np.argmin(y_new[:n_eval]))
                                # when failure tracking is enabled,
                                # mark the restart record as ``improved`` only if the
                                # local-best of the restart batch actually beat the
                                # pre-restart best.  Without this the ``failures``
                                # field never accumulates and the BMNP novelty
                                # weight has no signal to act on.  When the flag
                                # is off we keep the pre-Phase-5 default of
                                # ``improved=True`` for byte-stability.
                                _bmnp_improved = True
                                basin_memory.add(
                                    X_new[_best_restart_local],
                                    float(y_new[_best_restart_local]),
                                    span,
                                    improved=_bmnp_improved,
                                )

                            restarts_done += 1
                            restart_triggered = True
                            if cauchy_triggered:
                                restart_cause = "cauchy+restart"
                            else:
                                restart_cause = "triple" if _bse_triple else "stagnation"

                            cool = int(_round_half_up(_cfg_bse_cooldown_frac * float(max_nfes)))
                            cooldown_until_nfes = int(budget.nfes_used) + max(0, cool)
                            local_search_restart_block_until_gen = max(
                                local_search_restart_block_until_gen,
                                int(gen) + local_search_post_restart_cooldown,
                            )

                            stagnation.reset()
                            best_idx = int(np.argmin(fitness))
                            best_f = float(fitness[best_idx])
                            stagnation.push(best_f)

        if restart_triggered or n_cauchy_perturbed > 0:
            div_rad = population_radius(pop, span)
            if diversity_hist:
                diversity_hist[-1] = float(div_rad)
            if interaction_state is not None:
                ig_apply_restart_decay(interaction_state, factor=interaction_restart_decay)
                interaction_block_until_gen = max(
                    int(interaction_block_until_gen),
                    int(gen) + int(interaction_post_restart_cooldown),
                )
                if interaction_state.updates > 0:
                    ig_extract_blocks(
                        interaction_state,
                        edge_floor=interaction_graph_edge_floor,
                        min_block_size=interaction_block_min_size,
                        max_block_size=interaction_block_max_size,
                        gen=int(gen),
                    )
                    interaction_learned_groups = ig_expand_blocks_with_singletons(interaction_state, dim=D) if interaction_state.blocks else None

        # --------------------------------------------------------------
        # Tiny endgame local search
        # --------------------------------------------------------------
        interaction_ls_displacements: list[np.ndarray] = []
        interaction_ls_improvements_vals: list[float] = []
        if local_search_enabled and local_search_eval_cap > 0:
            frac_used_after_escape = (budget.nfes_used / float(max_nfes)) if max_nfes > 0 else 1.0
            div_ratio_now = float(div_rad) / max(1e-30, float(init_div_rad))
            local_search_disp_coherence = (
                _displacement_coherence(_disp_buf, window=local_search_coherence_window)
                if _track_disp_vectors else 0.0
            )
            _ls_reasons: list[str] = []
            if stagnation_gens_counter >= local_search_stagnation_window:
                local_search_trigger_score += 1
                _ls_reasons.append("stagnation")
            if signal_acceptance_mean <= local_search_acceptance_floor:
                local_search_trigger_score += 1
                _ls_reasons.append("accept")
            if div_ratio_now <= local_search_diversity_cap:
                local_search_trigger_score += 1
                _ls_reasons.append("diversity")
            if local_search_disp_coherence >= local_search_coherence_min:
                local_search_trigger_score += 1
                _ls_reasons.append("coherence")

            _ls_time_gate = frac_used_after_escape >= local_search_start_frac
            _ls_budget_gate = local_search_evals_total < local_search_eval_cap and int(budget.remaining()) > 0
            _ls_period_gate = (gen % local_search_period == 0)
            _ls_restart_gate = int(gen) >= int(local_search_restart_block_until_gen)
            _ls_cooldown_gate = int(gen) >= int(local_search_block_until_gen)
            _ls_event_gate = (
                local_search_trigger_mode == "time"
                or local_search_trigger_score >= local_search_score_threshold
            )
            can_local_search = (
                _ls_time_gate
                and _ls_budget_gate
                and _ls_period_gate
                and _ls_restart_gate
                and _ls_cooldown_gate
                and _ls_event_gate
                and (terra_ls_allowed or not budget_policy_enabled)
                and NP > 0
            )
            if local_search_trigger_mode == "time":
                local_search_trigger_reason = "time"
            elif _ls_reasons:
                local_search_trigger_reason = "+".join(_ls_reasons)
            else:
                local_search_trigger_reason = f"score<{local_search_score_threshold}"
            if not _ls_restart_gate:
                local_search_trigger_reason = "restart_cooldown"
            elif not _ls_cooldown_gate:
                local_search_trigger_reason = "ls_cooldown"
            elif not _ls_time_gate:
                local_search_trigger_reason = "time_gate"
            elif not _ls_period_gate:
                local_search_trigger_reason = "period_gate"
            elif not _ls_budget_gate:
                local_search_trigger_reason = "budget_gate"
            elif budget_policy_enabled and not terra_ls_allowed:
                local_search_trigger_reason = "terra_roi_gate"
            if can_local_search:
                local_search_active = True
                ls_budget_rem = min(int(budget.remaining()), int(local_search_eval_cap - local_search_evals_total))

                _ls_code_gen = _ls_code
                if local_search_auto_subspace:
                    # when enabled, route the
                    # local-search auto-subspace admission through the
                    # predicted-value gate; falls back to the bare LCB
                    # admission when the gate is disabled or absent.
                    if linkage_reliability_state is None:
                        _sri_ls_admit = False
                    else:
                        _sri_ls_legacy = bool(linkage_reliability_state.admit())
                        if predicted_value_gate is not None:
                            _sri_ls_acc = (sum(acceptance_hist) / len(acceptance_hist)) if acceptance_hist else 0.0
                            _sri_ls_admit = bool(predicted_value_gate.admit(
                                lcb_lift=float(linkage_reliability_state.last_lift),
                                budget_frac=float(frac_used),
                                acceptance_per_eval=float(_sri_ls_acc),
                                phase_code=0,
                                legacy_admission=_sri_ls_legacy,
                            ))
                        else:
                            _sri_ls_admit = _sri_ls_legacy
                    _sri_ls_ok = (
                        linkage_reliability_state is None
                        or _sri_ls_admit
                        or (interaction_state is not None and interaction_state.refresh_count >= interaction_min_refreshes)
                    )
                    if interaction_state is not None and interaction_use_for_local_search and _sri_ls_ok:
                        _ls_code_gen = 0

                if ls_budget_rem > 0 and _ls_code_gen == 0:  # subspace_nm
                    # ----- Subspace Nelder-Mead (structure-aware) -----
                    # Run NM in a low-dimensional subspace defined by recent
                    # successful displacement vectors. The basis window is tied
                    # to the same recent-history horizon used by the coherence
                    # trigger so the trigger and geometry model describe the
                    # same local regime.
                    elite_count = min(int(local_search_elite_count), int(NP))
                    elite_idx = np.argsort(fitness, kind="mergesort")[:elite_count]
                    remaining_elites = elite_count
                    local_search_elite_count_used = elite_count
                    lower = lu[0]
                    upper = lu[1]
                    k = int(_subspace_dim)
                    _ls_archive_idx: list[int] = []
                    coord_scale = np.std(pop, axis=0, dtype=np.float64)
                    coord_scale = np.maximum(coord_scale, 1e-10)
                    basis_window = max(int(k), int(local_search_coherence_window))
                    _disp_recent = (
                        np.asarray(_disp_buf[-min(len(_disp_buf), basis_window):], dtype=np.float64)
                        if len(_disp_buf) > 0 else None
                    )
                    basis = None

                    if interaction_confidence_adaptive and interaction_state is not None:
                        _ls_gate_thr = ig_adaptive_threshold(
                            interaction_state,
                            static_threshold=interaction_ls_confidence_min,
                            percentile=interaction_confidence_adaptive_percentile,
                            floor=interaction_confidence_adaptive_floor,
                            min_samples=interaction_confidence_adaptive_min_samples,
                            window=interaction_confidence_adaptive_window,
                            absolute_min=interaction_confidence_adaptive_absolute_min,
                        )
                    else:
                        _ls_gate_thr = interaction_ls_confidence_min
                    if (
                        interaction_use_for_local_search
                        and interaction_state is not None
                        and int(gen) >= int(interaction_block_until_gen)
                        and ig_ready(
                            interaction_state,
                            confidence_min=_ls_gate_thr,
                            min_updates=interaction_min_updates,
                            min_refreshes=interaction_min_refreshes,
                            min_nontrivial_dims=interaction_min_nontrivial_dims,
                        )
                    ):
                        _ls_dims, _ls_blocks, _ls_scores = ig_select_local_search_dims(
                            interaction_state,
                            recent_displacements=_disp_recent,
                            top_blocks=interaction_ls_top_blocks,
                            dim_cap=min(int(interaction_ls_dim_cap), int(_subspace_dim)),
                        )
                        if _ls_dims.size > 0:
                            k = min(int(_ls_dims.size), int(_subspace_dim), int(interaction_ls_dim_cap))
                            basis, local_search_basis_source = ig_build_local_search_basis(
                                interaction_state,
                                dims=_ls_dims,
                                recent_displacements=_disp_recent,
                                k=k,
                            )
                            if basis.size > 0:
                                k = int(basis.shape[0])
                                interaction_ls_blocks_used = tuple(int(v) for v in _ls_blocks.tolist())

                    local_search_subspace_dim_used = int(k)

                    # Build subspace basis from the same recent-history regime
                    # inspected by the coherence trigger, rather than the full
                    # displacement buffer.
                    if basis is None and _disp_recent is not None and _disp_recent.shape[0] >= k:
                        try:
                            _U, _S, _Vt = np.linalg.svd(_disp_recent, full_matrices=False)
                            basis = _Vt[:k, :]  # (k, D) — top-k right singular vectors
                            local_search_basis_source = "displacements"
                        except np.linalg.LinAlgError:
                            basis = None

                    # Fallback: use coordinate directions with highest population variance.
                    # M8: stable sort so the picked basis dims are deterministic on ties.
                    if basis is None:
                        top_dims = np.argsort(-coord_scale, kind="stable")[:k]
                        basis = np.zeros((k, D), dtype=np.float64)
                        basis[_arange_int_buf[:k], top_dims] = 1.0
                        local_search_basis_source = "variance"

                    # Scale for subspace simplex / fallback coordinate search.
                    sub_scale = np.linalg.norm(basis[:k] * coord_scale[np.newaxis, :], axis=1) * local_search_step_scale
                    sub_scale = np.maximum(sub_scale, 1e-10)

                    for idx in elite_idx:
                        idx = int(idx)
                        if local_search_evals_total >= local_search_eval_cap or int(budget.remaining()) <= 0:
                            break
                        per_elite_budget = max(1, (local_search_eval_cap - local_search_evals_total) // max(1, remaining_elites))
                        remaining_elites -= 1
                        x0 = pop[idx, :].copy()
                        f0 = float(fitness[idx])
                        maxfev = min(per_elite_budget, int(budget.remaining()),
                                     int(local_search_eval_cap - local_search_evals_total))
                        if maxfev < 2:
                            break

                        # Project to subspace coordinates: alpha = basis @ (x - x0)
                        alpha0 = np.zeros(k, dtype=np.float64)

                        _nm_evals = [0]
                        _nm_best_f = [f0]
                        _nm_best_x = [x0.copy()]
                        _nm_best_alpha = [alpha0.copy()]

                        def _snm_obj(
                            alpha,
                            *,
                            x0=x0,
                            basis=basis,
                            lower=lower,
                            upper=upper,
                            _nm_evals=_nm_evals,
                            _nm_best_f=_nm_best_f,
                            _nm_best_x=_nm_best_x,
                            _nm_best_alpha=_nm_best_alpha,
                        ):
                            # Map subspace coords back to full space
                            x_full = x0 + alpha @ basis  # (k,) @ (k, D) → (D,)
                            x_full = np.clip(x_full, lower, upper)
                            x_2d = x_full.reshape(1, -1)
                            y, n = budget.eval_batch_safe(x_2d)
                            if n == 0:
                                return float(_nm_best_f[0])
                            _nm_evals[0] += int(n)
                            yf = float(y[0])
                            if yf < _nm_best_f[0]:
                                _nm_best_f[0] = yf
                                _nm_best_x[0] = x_full.copy()
                                _nm_best_alpha[0] = np.asarray(alpha, dtype=np.float64).copy()
                            return yf

                        if _sp_minimize is not None and maxfev >= k + 2:
                            init_simplex = np.empty((k + 1, k), dtype=np.float64)
                            init_simplex[0] = alpha0
                            init_simplex[1:] = alpha0
                            _diag_k = _arange_int_buf[:k]
                            init_simplex[_diag_k + 1, _diag_k] += sub_scale

                            _sp_minimize(
                                _snm_obj, alpha0, method='Nelder-Mead',
                                options={
                                    'maxfev': maxfev,
                                    'initial_simplex': init_simplex,
                                    'xatol': 1e-10,
                                    'fatol': 1e-10,
                                    'adaptive': True,
                                },
                            )
                        else:
                            # Deterministic fallback when SciPy is unavailable
                            # (or when the remaining per-elite budget is too
                            # small for a simplex step): projected coordinate
                            # search in the learned subspace.
                            alpha_best = alpha0.copy()
                            step = sub_scale.copy()
                            evals_left = int(maxfev)
                            while evals_left > 0:
                                fallback_improved = False
                                for j in range(k):
                                    for sign in (1.0, -1.0):
                                        if evals_left <= 0:
                                            break
                                        alpha_try = alpha_best.copy()
                                        alpha_try[j] += sign * step[j]
                                        yf = _snm_obj(alpha_try)
                                        evals_left -= 1
                                        if yf < _nm_best_f[0]:
                                            alpha_best = _nm_best_alpha[0].copy()
                                            fallback_improved = True
                                    if evals_left <= 0:
                                        break
                                if fallback_improved:
                                    continue
                                step *= 0.5
                                if float(np.max(step)) <= 1e-10:
                                    break

                        n_used = _nm_evals[0]
                        local_search_evals_total += n_used
                        local_search_evals_used_gen += n_used

                        if _nm_best_f[0] < f0:
                            pop[idx, :] = _nm_best_x[0]
                            fitness[idx] = _nm_best_f[0]
                            local_search_improvements += 1
                            local_search_best_delta = max(local_search_best_delta, f0 - _nm_best_f[0])
                            interaction_ls_displacements.append(_nm_best_x[0] - x0)
                            interaction_ls_improvements_vals.append(float(f0 - _nm_best_f[0]))
                            _ls_archive_idx.append(idx)

                    if archive is not None and _ls_archive_idx:
                        _ls_idx = np.asarray(_ls_archive_idx, dtype=np.intp)
                        archive_insertions += int(archive.consider_batch(pop[_ls_idx], fitness[_ls_idx]))

                    if local_search_improvements > 0:
                        best_idx = int(np.argmin(fitness))
                        best_f = float(fitness[best_idx])
                        stagnation.reset()
                        stagnation.push(best_f)

                elif ls_budget_rem > 0 and _ls_code_gen == 1:  # nelder_mead
                    # ----- Nelder-Mead local search (rotation-aware) -----
                    elite_count = min(int(local_search_elite_count), int(NP))
                    local_search_elite_count_used = elite_count
                    elite_idx = np.argsort(fitness, kind="mergesort")[:elite_count]
                    remaining_elites = elite_count
                    lower = lu[0]
                    upper = lu[1]
                    _ls_archive_idx: list[int] = []

                    for idx in elite_idx:
                        idx = int(idx)
                        if local_search_evals_total >= local_search_eval_cap or int(budget.remaining()) <= 0:
                            break
                        per_elite_budget = max(1, (local_search_eval_cap - local_search_evals_total) // max(1, remaining_elites))
                        remaining_elites -= 1
                        x0 = pop[idx, :].copy()
                        f0 = float(fitness[idx])
                        maxfev = min(per_elite_budget, int(budget.remaining()),
                                     int(local_search_eval_cap - local_search_evals_total))
                        if maxfev < D + 2:
                            break  # not enough budget for even one NM iteration

                        # Wrap objective through budget system
                        _nm_evals = [0]
                        _nm_best_f = [f0]
                        _nm_best_x = [x0.copy()]

                        def _nm_obj(
                            x_1d,
                            *,
                            lower=lower,
                            upper=upper,
                            _nm_evals=_nm_evals,
                            _nm_best_f=_nm_best_f,
                            _nm_best_x=_nm_best_x,
                        ):
                            x_c = np.clip(x_1d, lower, upper).reshape(1, -1)
                            y, n = budget.eval_batch_safe(x_c)
                            if n == 0:
                                return float(_nm_best_f[0])
                            _nm_evals[0] += int(n)
                            yf = float(y[0])
                            if yf < _nm_best_f[0]:
                                _nm_best_f[0] = yf
                                _nm_best_x[0] = x_c[0].copy()
                            return yf

                        if _sp_minimize is not None:
                            # Initial simplex: elite + small perturbations
                            # S5: vectorised simplex construction (tile + diagonal
                            # scatter + single clip) — matches subspace-NM path.
                            coord_scale = np.std(pop, axis=0, dtype=np.float64)
                            coord_scale = np.maximum(coord_scale, 1e-10)
                            init_simplex = np.empty((D + 1, D), dtype=np.float64)
                            init_simplex[0] = x0
                            init_simplex[1:] = x0
                            _diag_d = _arange_int_buf[:D]
                            init_simplex[_diag_d + 1, _diag_d] += local_search_step_scale * coord_scale
                            np.clip(init_simplex[1:], lower, upper, out=init_simplex[1:])

                            _sp_minimize(
                                _nm_obj, x0, method='Nelder-Mead',
                                options={
                                    'maxfev': maxfev,
                                    'initial_simplex': init_simplex,
                                    'xatol': 1e-10,
                                    'fatol': 1e-10,
                                    'adaptive': True,
                                },
                            )
                        else:
                            # Fallback: scipy not installed, do coordinate LS
                            coord_scale = np.std(pop, axis=0, dtype=np.float64)
                            coord_scale = np.maximum(coord_scale, 1e-10)
                            for _ in range(min(maxfev, D)):
                                j = int(rngs.core.integers(0, D))
                                delta = local_search_step_scale * coord_scale[j]
                                for sign in [1.0, -1.0]:
                                    xt = x0.copy()
                                    xt[j] += sign * delta
                                    _nm_obj(xt)

                        n_used = _nm_evals[0]
                        local_search_evals_total += n_used
                        local_search_evals_used_gen += n_used

                        if _nm_best_f[0] < f0:
                            pop[idx, :] = _nm_best_x[0]
                            fitness[idx] = _nm_best_f[0]
                            local_search_improvements += 1
                            local_search_best_delta = max(local_search_best_delta, f0 - _nm_best_f[0])
                            interaction_ls_displacements.append(_nm_best_x[0] - x0)
                            interaction_ls_improvements_vals.append(float(f0 - _nm_best_f[0]))
                            _ls_archive_idx.append(idx)

                    if archive is not None and _ls_archive_idx:
                        _ls_idx = np.asarray(_ls_archive_idx, dtype=np.intp)
                        archive_insertions += int(archive.consider_batch(pop[_ls_idx], fitness[_ls_idx]))

                    if local_search_improvements > 0:
                        best_idx = int(np.argmin(fitness))
                        best_f = float(fitness[best_idx])
                        stagnation.reset()
                        stagnation.push(best_f)

                elif ls_budget_rem > 0 and local_search_step_scale > 0.0:
                    # ----- Coordinate-wise local search (original) -----
                    elite_count = min(int(local_search_elite_count), int(NP))
                    local_search_elite_count_used = elite_count
                    elite_idx = np.argsort(fitness, kind="mergesort")[:elite_count]
                    coord_scale = np.std(pop, axis=0, dtype=np.float64)
                    coord_scale = np.maximum(coord_scale, local_search_min_step)
                    coord_order = np.argsort(-coord_scale, kind="mergesort")
                    window_den = max(1e-12, 1.0 - float(local_search_start_frac))
                    window_progress = max(0.0, min(1.0, (frac_used_after_escape - float(local_search_start_frac)) / window_den))
                    step_decay = max(0.25, 1.0 - (0.75 * window_progress))

                    proposals: list[np.ndarray] = []
                    parents_ls: list[np.ndarray] = []
                    proposal_meta: list[tuple[int, float]] = []
                    _ls_archive_idx: list[int] = []

                    for elite_offset, idx in enumerate(elite_idx):
                        if len(proposals) >= ls_budget_rem:
                            break
                        coord = int(coord_order[(local_search_coord_cursor + elite_offset) % D])
                        delta = float(local_search_step_scale) * float(coord_scale[coord]) * float(step_decay)
                        if not math.isfinite(delta) or delta <= 0.0:
                            continue
                        x0 = pop[int(idx), :].copy()
                        x_plus = x0.copy()
                        x_plus[coord] += delta
                        proposals.append(x_plus)
                        parents_ls.append(x0)
                        proposal_meta.append((int(idx), float(fitness[int(idx)])))

                        if len(proposals) >= ls_budget_rem:
                            break

                        x_minus = x0.copy()
                        x_minus[coord] -= delta
                        proposals.append(x_minus)
                        parents_ls.append(x0)
                        proposal_meta.append((int(idx), float(fitness[int(idx)])))

                    if proposals:
                        X_ls = np.vstack(proposals)
                        X_ls_parent = np.vstack(parents_ls)
                        bound_constraint(X_ls, X_ls_parent, lu)
                        y_ls, n_eval_ls = budget.eval_batch_safe(X_ls)
                        y_ls = np.asarray(y_ls, dtype=np.float64)
                        local_search_evals_total += int(n_eval_ls)
                        local_search_evals_used_gen = int(n_eval_ls)
                        ls_best_by_idx: dict[int, tuple[float, np.ndarray]] = {}

                        for pos in range(int(n_eval_ls)):
                            idx, f_old = proposal_meta[pos]
                            y_new = float(y_ls[pos])
                            if y_new <= float(f_old):
                                prev = ls_best_by_idx.get(idx)
                                if prev is None or y_new < float(prev[0]):
                                    ls_best_by_idx[idx] = (y_new, X_ls[pos, :].copy())

                        for idx, (y_new, x_new) in ls_best_by_idx.items():
                            old_val = float(fitness[idx])
                            if y_new <= old_val:
                                x_old = pop[idx, :].copy()
                                pop[idx, :] = x_new
                                fitness[idx] = y_new
                                local_search_improvements += 1
                                local_search_best_delta = max(local_search_best_delta, max(0.0, old_val - y_new))
                                interaction_ls_displacements.append(x_new - x_old)
                                interaction_ls_improvements_vals.append(float(max(0.0, old_val - y_new)))
                                _ls_archive_idx.append(int(idx))

                        if archive is not None and _ls_archive_idx:
                            _ls_idx = np.asarray(_ls_archive_idx, dtype=np.intp)
                            archive_insertions += int(archive.consider_batch(pop[_ls_idx], fitness[_ls_idx]))

                        if local_search_improvements > 0:
                            best_idx = int(np.argmin(fitness))
                            best_f = float(fitness[best_idx])
                            stagnation.reset()
                            stagnation.push(best_f)

                        local_search_coord_cursor = (local_search_coord_cursor + elite_count) % max(1, D)

                if local_search_active:
                    if _ls_code_gen == 0 and local_search_basis_source == "none":
                        local_search_basis_source = "skip"
                    if local_search_evals_used_gen > 0:
                        local_search_block_until_gen = max(
                            local_search_block_until_gen,
                            int(gen) + local_search_post_ls_cooldown,
                        )

        # --------------------------------------------------------------
        # P3 final polish: one-shot unconditional refinement of the
        # incumbent best in the closing budget slice (opt-in).
        # --------------------------------------------------------------
        if (
            final_polish_enabled
            and not final_polish_done
            and max_nfes > 0
            and (budget.nfes_used / float(max_nfes)) >= final_polish_start_frac
            and not budget.exhausted()
        ):
            final_polish_done = True
            _fp_budget = min(int(budget.remaining()), int(final_polish_eval_cap))
            if _fp_budget > 0:
                # C006: re-materialise the incumbent ATOMICALLY before polishing.
                # ``best_idx``/``best_f`` are refreshed mid-generation (e.g. after a
                # local-search improvement), but ``best_x`` is only rebuilt from the
                # population at the end of the generation (the "S4" materialisation).
                # Entering the compass with that pairing hands it a stale vector
                # carrying a NEWER incumbent's fitness: ``_final_polish_compass``
                # trusts ``f0`` without re-evaluating ``x0``, so it would search the
                # neighbourhood of one point while judging probes against another
                # point's (better) value -- rejecting useful candidates and spending
                # its one-shot budget in the wrong place. Results were never corrupted
                # (the write-back below still requires a strict improvement, and the
                # protected global best is restored at return), but the polish was
                # measured in a handicapped form. Rebuild all three from ``fitness``
                # so the vector and its value refer to the same individual.
                best_idx = int(np.argmin(fitness))
                best_f = float(fitness[best_idx])
                best_x = pop[best_idx, :].copy()
                if _research_oracle_basis is not None:
                    _fp_basis, _fp_src = _research_oracle_basis, "oracle"
                else:
                    _fp_basis, _fp_src = _final_polish_basis(interaction_state, D)
                _fp_x, _fp_f, _fp_used = _final_polish_compass(
                    best_x,
                    float(best_f),
                    basis=_fp_basis,
                    lower=lower,
                    upper=upper,
                    span=span,
                    budget=budget,
                    max_evals=_fp_budget,
                    step_frac=float(config.final_polish_step_frac),
                    min_step_frac=float(config.final_polish_min_step_frac),
                )
                if _fp_f < float(best_f):
                    # Write the polished incumbent back into the best
                    # individual's slot: ``best_f`` is recomputed from the
                    # population each generation, so the gain must live in
                    # ``pop`` to persist (acceptance is elitist; the slot
                    # only ever improves).
                    _fp_best_idx = int(np.argmin(fitness))
                    pop[_fp_best_idx] = _fp_x
                    fitness[_fp_best_idx] = _fp_f
                    best_x = _fp_x.copy()
                    best_f = float(_fp_f)

        if (
            interaction_state is not None
            and interaction_ls_update_weight > 0.0
            and interaction_ls_displacements
            and ((budget.nfes_used / float(max_nfes)) if max_nfes > 0 else 1.0) >= interaction_graph_warmup_frac
        ):
            _ls_disp_arr = np.asarray(interaction_ls_displacements, dtype=np.float64)
            _ls_imp_arr = np.asarray(interaction_ls_improvements_vals, dtype=np.float64)
            _ls_weights = np.full((_ls_disp_arr.shape[0],), float(interaction_ls_update_weight), dtype=np.float64)
            ig_update_from_accepted(
                interaction_state,
                displacements=_ls_disp_arr,
                improvements=_ls_imp_arr,
                decay=1.0,
                lr=interaction_graph_lr,
                sample_weights=_ls_weights,
            )
            interaction_updates_from_ls = int(_ls_disp_arr.shape[0])
            if interaction_state.updates > 0:
                ig_extract_blocks(
                    interaction_state,
                    edge_floor=interaction_graph_edge_floor,
                    min_block_size=interaction_block_min_size,
                    max_block_size=interaction_block_max_size,
                    gen=int(gen),
                )
                interaction_learned_groups = ig_expand_blocks_with_singletons(interaction_state, dim=D) if interaction_state.blocks else None

        # S4: single best_x materialization after all modifiers
        best_x = pop[best_idx, :].copy()

        # --------------------------------------------------------------
        # Per-generation history (best-so-far)
        # --------------------------------------------------------------
        if history is not None:
            history.append(float(best_f))

        # --------------------------------------------------------------
        # Stagnation counter (must run unconditionally — used by BSE)
        # --------------------------------------------------------------
        best_improvement = max(0.0, best_before_gen - best_f)
        if best_improvement > 0.0:
            stagnation_gens_counter = 0
        else:
            stagnation_gens_counter += 1

        # --------------------------------------------------------------
        # Deep-stall full restart (standard mechanism, default-ON; RNG only when
        # it fires, and the deep_stall_min_budget guard keeps tiny budgets inert).
        # Track the global best so a full re-init cannot lose ground, then, if the
        # incumbent has been frozen for a large fraction of the budget, abandon
        # the working population and re-initialise it uniformly (a true
        # multi-start). The BSE restart cannot escape a deep trap because it
        # always preserves the best individual -- which, in a trap, IS the trapped
        # solution; a full re-init removes that bad attractor.
        if best_f < global_best_f:
            global_best_f = float(best_f)
            global_best_x = best_x.copy()
            _dsr_nfes_at_best = int(budget.nfes_used)
        if _dsr_enabled and max_nfes >= _dsr_min_budget:
            _dsr_stall = (budget.nfes_used - _dsr_nfes_at_best) / float(max_nfes)
            _dsr_cool_ok = (
                _dsr_last_restart_nfes < 0
                or (budget.nfes_used - _dsr_last_restart_nfes)
                >= config.deep_stall_cooldown_frac * max_nfes
            )
            _dsr_phase_ok = (
                budget.nfes_used / float(max_nfes)
            ) < config.deep_stall_stop_frac
            if (
                _dsr_stall >= config.deep_stall_frac
                and _dsr_cool_ok
                and _dsr_phase_ok
                and budget.remaining() > 0
            ):
                _dsr_n = min(int(pop.shape[0]), int(budget.remaining()))
                if _dsr_n > 0:
                    _dsr_X = lower + rngs.bse.random((_dsr_n, D)) * span
                    _dsr_y, _dsr_ne = budget.eval_batch_safe(_dsr_X)
                    _dsr_y = np.asarray(_dsr_y, dtype=np.float64)
                    if _dsr_ne > 0:
                        pop[:_dsr_ne, :] = _dsr_X[:_dsr_ne, :]
                        fitness[:_dsr_ne] = _dsr_y[:_dsr_ne]
                        stagnation.reset()
                        best_idx = int(np.argmin(fitness))
                        best_f = float(fitness[best_idx])
                        best_x = pop[best_idx, :].copy()
                        stagnation.push(best_f)
                        stagnation_gens_counter = 0
                        # Restart the stall window from "now" so it does not
                        # immediately re-fire while the fresh search descends.
                        _dsr_nfes_at_best = int(budget.nfes_used)
                        _dsr_last_restart_nfes = int(budget.nfes_used)

        # --------------------------------------------------------------
        # Generation log
        # --------------------------------------------------------------
        # S0-4 (DT2): the learned/random linkage attribution and the FC4
        # lift-EMA update -- the SOLE fitness-affecting state in this region
        # (``_v4_link_lift_ema``, read back by FC4 at ~L3009) -- now run
        # UNCONDITIONALLY, so the trajectory no longer depends on telemetry
        # presence.  Previously nested in the gen-log callback block; the shipped
        # adapter always passes a callback so pub is byte-identical, but a
        # callback-less core call diverged at D>=100 (the EMA went stale).  The
        # FC4 read happens earlier in the generation, so running the update here
        # keeps it AFTER that read -- intra-generation ordering, and pub, are
        # unchanged.  The per-segment attribution uses the exact row-index arrays
        # from `_build_phase4_masks` (primary==learned / secondary==random when
        # SGSM is admitted; primary==random fallback otherwise), masked by the
        # per-row `improved` flag.
        if linkage_groups_secondary is not None:
            _learned_idx_log = _link_primary_idx
            _random_idx_log = _link_secondary_idx
        else:
            _learned_idx_log = np.empty((0,), dtype=np.int64)
            _random_idx_log = _link_primary_idx
        _link_learned_rows = int(_learned_idx_log.size)
        _link_random_rows = int(_random_idx_log.size)
        _link_learned_accepted = (
            int(np.sum(improved[_learned_idx_log]))
            if _link_learned_rows > 0 else 0
        )
        _link_random_accepted = (
            int(np.sum(improved[_random_idx_log]))
            if _link_random_rows > 0 else 0
        )
        # DT2 shadow diagnostics (S0-3): summed positive improvement per path
        # (reward magnitude, not just acceptance). Observation-only -- gated on
        # the research flag; no RNG, no state mutation. `_imp_deltas` is ordered
        # by the improving rows np.nonzero(improved)[0], so scatter the reward to
        # per-row positions and sum over the exact learned/random row arrays.
        _link_learned_reward_sum = 0.0
        _link_random_reward_sum = 0.0
        if _cfg_research_dt2_shadow:
            _s0_idx_imp = np.nonzero(improved)[0]
            _s0_row_reward = np.zeros(improved.shape[0], dtype=np.float64)
            if _s0_idx_imp.size:
                _s0_row_reward[_s0_idx_imp] = np.maximum(_imp_deltas, 0.0)
            if _link_learned_rows > 0:
                _link_learned_reward_sum = float(_s0_row_reward[_learned_idx_log].sum())
            if _link_random_rows > 0:
                _link_random_reward_sum = float(_s0_row_reward[_random_idx_log].sum())
        # FC4 lift EMA update: only when BOTH learned and random rows are present
        # (linkage_groups_secondary is not None and both partitions non-empty).
        # Default ema_alpha=0 collapses the EMA to a no-op.
        if (
            _cfg_v4_fc4_enabled
            and _cfg_v4_fc4_ema_alpha > 0.0
            and _link_learned_rows > 0
            and _link_random_rows > 0
        ):
            _v4_fc4_learned_acc = _link_learned_accepted / float(_link_learned_rows)
            _v4_fc4_random_acc = _link_random_accepted / float(_link_random_rows)
            _v4_fc4_lift_now = _v4_fc4_learned_acc - _v4_fc4_random_acc
            _v4_link_lift_ema = (
                (1.0 - _cfg_v4_fc4_ema_alpha) * _v4_link_lift_ema
                + _cfg_v4_fc4_ema_alpha * _v4_fc4_lift_now
            )

        # MEM-1: the telemetry block below is entered for BOTH the full gen-log
        # callback and the lightweight curve-only callback.  It carries NO
        # fitness-affecting state (that moved above); the reductions feed only the
        # DTGSKGenerationLog constructor and are relocated below the curve-only
        # ``continue`` (their inputs -- fitness[:NP], _imp_deltas, improved,
        # n_child, linkage_blockwise_rows -- are not reassigned to the constructor).
        if generation_callback is not None or curve_callback is not None:
            stop_note = "budget_exhausted" if budget.exhausted() else None
            generation_runtime = time.perf_counter() - gen_t0
            generation_evals_used = int(budget.nfes_used) - int(evals_used_before_gen)
            generation_runtime_per_eval = (
                float(generation_runtime) / float(generation_evals_used)
                if generation_evals_used > 0 else 0.0
            )
            denom_best = abs(best_before_gen) + 1e-12
            _ace_enabled = _cfg_ace_enabled

            # MEM-1 curve-only fast path.  The FC4 lift-EMA (the sole
            # fitness-affecting state in this block) has now been updated, so
            # for a curve-only run we emit the two convergence scalars and skip
            # the entire telemetry tail below (rescue/jun-sen counters,
            # failure-alignment cosine, ACE/argp tuples, ``ig_stats``, and the
            # ~130-line ``DTGSKGenerationLog`` construction).  ``int(budget.
            # nfes_used)`` / ``float(best_f)`` are exactly the ``evals_used`` /
            # ``best_fitness`` fields the full path would emit.  This block is
            # the last statement in the generation loop body, so ``continue``
            # simply advances to the next ``while`` iteration.
            if generation_callback is None:
                curve_callback(int(budget.nfes_used), float(best_f))
                continue

            # TEL2-1: relocated from above the curve-only ``continue``.  These
            # reductions feed ONLY the DTGSKGenerationLog constructor below, so
            # they are pure waste on the curve path and are computed here, on the
            # gen-log path only.  Bit-identical to the old in-place computation:
            # none of the inputs are reassigned between the ``continue`` above and
            # the constructor below.
            # Population fitness statistics
            _fit_slice = fitness[:NP]
            _worst_f = float(np.max(_fit_slice))
            _median_f = float(np.median(_fit_slice))
            _mean_f = float(np.mean(_fit_slice))
            _std_f = float(np.std(_fit_slice))

            # Accepted improvement statistics
            _mean_acc_imp = 0.0
            _max_acc_imp = 0.0
            if accepted > 0:
                _mean_acc_imp = float(np.mean(_imp_deltas))
                _max_acc_imp = float(np.max(_imp_deltas))

            # Linkage vs per-dim acceptance split
            _link_rows = min(int(linkage_blockwise_rows), n_child)
            _link_accepted = int(np.sum(improved[:_link_rows])) if _link_rows > 0 else 0
            _perdim_total = max(0, n_child - _link_rows)
            _perdim_accepted = int(np.sum(improved[_link_rows:n_child])) if _perdim_total > 0 else 0
            _link_acc_rate = float(_link_accepted) / max(1, _link_rows)
            _perdim_acc_rate = float(_perdim_accepted) / max(1, _perdim_total)

            # Operator/rescue-owner telemetry (no behaviour change; passive observers).
            # Rescue owner priority: BSE > CAUCHY > SR-WIDE > NONE.  BSE and Cauchy
            # may co-occur in the same gen (Cauchy fires inside the escape branch
            # before BSE restart) but BSE is the heavier rescue and owns the slot
            # when both fired.  SR-WIDE captures the bottom-half senior cone
            # widening from the v0-split path.
            if bool(restart_triggered):
                _rescue_owner_code = 1  # BSE
            elif bool(cauchy_triggered):
                _rescue_owner_code = 2  # CAUCHY (resolved escape, BSE skipped)
            elif bool(_split_widen_now):
                _rescue_owner_code = 3  # SR-WIDE
            else:
                _rescue_owner_code = 0  # NONE
            _bottom_widen_active = bool(_split_widen_now)
            # Junior/senior trial-dominance success split.  D_J and D_S are the
            # per-component selection masks for the junior and senior trials
            # respectively (built by `_build_phase4_masks`).  A row is "junior-
            # dominant" when more components were taken from the junior trial
            # than from the senior trial; ties go to senior to mirror the GSK
            # convention that senior knowledge is the higher-quality cone.
            if int(n_child) > 0 and improved.size >= int(n_child):
                _dj_count = D_J[:int(n_child), :].sum(axis=1)
                _ds_count = D_S[:int(n_child), :].sum(axis=1)
                _jun_dom = _dj_count > _ds_count
                _sen_dom = ~_jun_dom
                _improved_n = improved[:int(n_child)]
                _jun_dom_succ = int(np.sum(np.logical_and(_improved_n, _jun_dom)))
                _sen_dom_succ = int(np.sum(np.logical_and(_improved_n, _sen_dom)))
            else:
                _jun_dom_succ = 0
                _sen_dom_succ = 0

            # Telemetry: delayed-reward and failure-alignment fields for gen logs.
            #
            # `delayed_reward_lag10` is the cumulative best-f drop across a
            # sliding window of length `_DELAYED_REWARD_LAG + 1`, smoothing
            # single-gen noise to expose sustained progress in offline
            # diagnostic analysis.  Reports 0.0 until the window has filled.
            #
            # `failure_alignment_*` measure whether failed-trial displacements
            # had the right "intent" — cosine alignment with the direction
            # from parent to the current best.  Positive alignment means the
            # failed trial pointed in roughly the right direction but landed
            # in a worse spot (right intent, wrong magnitude); negative means
            # uncoordinated search.  Failed rows aren't replaced, so
            # `pop[failed_idx]` is still the parent post-acceptance.
            _best_f_window.append(float(best_f))
            if len(_best_f_window) >= _DELAYED_REWARD_LAG + 1:
                _delayed_reward_lag10 = float(_best_f_window[0] - _best_f_window[-1])
            else:
                _delayed_reward_lag10 = 0.0
            if int(n_child) > 0 and improved.size >= int(n_child):
                _failed_n_mask = ~improved[:int(n_child)]
                _n_failed_log = int(np.sum(_failed_n_mask))
                if _n_failed_log > 0:
                    _failed_idx_arr = np.nonzero(_failed_n_mask)[0]
                    _disp_fail = ui[_failed_idx_arr, :] - pop[_failed_idx_arr, :]
                    _to_best_fail = pop[best_idx, :] - pop[_failed_idx_arr, :]
                    _disp_norm_fail = np.linalg.norm(_disp_fail, axis=1) + 1e-30
                    _to_best_norm_fail = np.linalg.norm(_to_best_fail, axis=1) + 1e-30
                    _cos_fail = (
                        np.sum(_disp_fail * _to_best_fail, axis=1)
                        / (_disp_norm_fail * _to_best_norm_fail)
                    )
                    _failure_alignment_mean = float(np.mean(_cos_fail))
                    _failure_alignment_pos_frac = float(np.mean(_cos_fail > 0))
                else:
                    _failure_alignment_mean = 0.0
                    _failure_alignment_pos_frac = 0.0
            else:
                _failure_alignment_mean = 0.0
                _failure_alignment_pos_frac = 0.0

            # Per-entry acceptance rate and mean reward
            _ace_count_size = int(ace_sample_counts_arr.size)
            if _ace_count_size > 0:
                _ace_probs = tuple(Kw_P.tolist()) if _ace_enabled else tuple()
                _ace_top_probs = (
                    tuple(Kw_P_top.tolist())
                    if dual_ace_top_bottom and _ace_enabled else tuple()
                )
                _ace_bottom_probs = (
                    tuple(Kw_P_bottom.tolist())
                    if dual_ace_top_bottom and _ace_enabled else tuple()
                )
                _ace_sample_counts = tuple(ace_sample_counts_arr.tolist())
                _ace_success_counts = tuple(ace_success_counts_arr.tolist())
                _ace_reward_sums = tuple(ace_reward_sums_arr.tolist())
                _ace_denom = np.maximum(
                    ace_sample_counts_arr.astype(np.float64, copy=False), 1.0
                )
                _entry_acc = tuple(
                    (
                        ace_success_counts_arr.astype(np.float64, copy=False) / _ace_denom
                    ).tolist()
                )
                _entry_mean_rew = tuple((ace_reward_sums_arr / _ace_denom).tolist())
                _ace_entropy = _entropy_prob(Kw_P) if _ace_enabled else 0.0
                _ace_top_entropy = _entropy_prob(Kw_P_top) if _ace_enabled else 0.0
                _ace_bottom_entropy = _entropy_prob(Kw_P_bottom) if _ace_enabled else 0.0
            else:
                _ace_probs = tuple()
                _ace_top_probs = tuple()
                _ace_bottom_probs = tuple()
                _ace_sample_counts = tuple()
                _ace_success_counts = tuple()
                _ace_reward_sums = tuple()
                _entry_acc = (0.0,)
                _entry_mean_rew = (0.0,)
                _ace_entropy = 0.0
                _ace_top_entropy = 0.0
                _ace_bottom_entropy = 0.0

            # Diversity ratio (relative to init)
            _div_ratio = float(div_rad) / max(1e-30, float(init_div_rad))
            _de_sample_count = (
                int(ace_sample_counts_arr[de_entry_idx])
                if _ace_enabled and 0 <= de_entry_idx < _ace_count_size
                else 0
            )
            _argp_frozen_entries = tuple(np.flatnonzero(argp_frozen).tolist())
            _argp_frozen_top_entries = tuple(np.flatnonzero(argp_frozen_top).tolist())
            _argp_frozen_bottom_entries = tuple(np.flatnonzero(argp_frozen_bottom).tolist())
            _argp_rolling_acc = tuple(argp_rolling_acc.tolist())
            _argp_rolling_acc_top = tuple(argp_rolling_acc_top.tolist())
            _argp_rolling_acc_bottom = tuple(argp_rolling_acc_bottom.tolist())
            _archive_size = len(archive) if archive is not None else 0
            _mean_dim_coverage = (
                float(coverage_i.mean()) if coverage_i is not None else 0.0
            )  # W2.4: placeholder only reachable when stats are discarded
            _ls_roi = (
                float(local_search_best_delta) / float(local_search_evals_used_gen)
                if local_search_evals_used_gen > 0 else 0.0
            )
            if interaction_state is not None:
                _ig_stats = ig_stats(interaction_state)
                _ig_active = True
                _ig_density = float(_ig_stats.density)
                _ig_block_count = int(_ig_stats.block_count)
                _ig_mean_block_conf = float(_ig_stats.mean_block_confidence)
                _ig_nontrivial_dim_frac = float(_ig_stats.nontrivial_dim_fraction)
                _ig_orphan_dim_frac = float(_ig_stats.orphan_dim_fraction)
                _ig_overall_conf = float(interaction_state.overall_confidence)
                _ig_refresh_count = int(_ig_stats.refresh_count)
            else:
                _ig_active = False
                _ig_density = 0.0
                _ig_block_count = 0
                _ig_mean_block_conf = 0.0
                _ig_nontrivial_dim_frac = 0.0
                _ig_orphan_dim_frac = 1.0
                _ig_overall_conf = 0.0
                _ig_refresh_count = 0

            generation_callback(
                DTGSKGenerationLog(
                    gen=int(gen),
                    evals_used=int(budget.nfes_used),
                    budget_frac=float(budget.nfes_used) / float(max_nfes),
                    pop_size=int(NP),
                    generation_runtime_sec=float(generation_runtime),
                    generation_evals_used=int(generation_evals_used),
                    generation_runtime_per_eval_sec=float(generation_runtime_per_eval),
                    best_fitness=float(best_f),
                    worst_fitness=_worst_f,
                    median_fitness=_median_f,
                    mean_fitness=_mean_f,
                    fitness_std=_std_f,
                    fitness_range=_worst_f - float(best_f),
                    best_f_init=float(best_f_init),
                    cumulative_improvement=float(best_f_init - best_f),
                    offspring_evaluated=int(n_child),
                    accepted_offspring=int(accepted),
                    acceptance_rate=(float(accepted) / float(n_child) if n_child > 0 else 0.0),
                    best_improvement=float(best_improvement),
                    normalized_best_improvement=float(best_improvement / denom_best),
                    mean_accepted_improvement=_mean_acc_imp,
                    max_accepted_improvement=_max_acc_imp,
                    stagnation_gens=stagnation_gens_counter,
                    diversity_radius=float(div_rad),
                    diversity_ratio=_div_ratio,
                    linkage_active=bool(linkage_blockwise_active),
                    linkage_block_size=(int(linkage_block_size) if linkage_blockwise_active else 0),
                    linkage_group_count=int(linkage_group_count),
                    linkage_rows=int(linkage_blockwise_rows),
                    linkage_accepted=_link_accepted,
                    linkage_total=_link_rows,
                    linkage_acc_rate=_link_acc_rate,
                    perdim_accepted=_perdim_accepted,
                    perdim_total=_perdim_total,
                    perdim_acc_rate=_perdim_acc_rate,
                    ace_probs=_ace_probs,
                    ace_top_probs=_ace_top_probs,
                    ace_bottom_probs=_ace_bottom_probs,
                    ace_sample_counts=_ace_sample_counts,
                    ace_success_counts=_ace_success_counts,
                    ace_reward_sums=_ace_reward_sums,
                    ace_entry_acc_rate=_entry_acc,
                    ace_entry_mean_reward=_entry_mean_rew,
                    ace_entropy=float(_ace_entropy),
                    ace_top_entropy=float(_ace_top_entropy),
                    ace_bottom_entropy=float(_ace_bottom_entropy),
                    module_prob_mass=float(module_prob_mass),
                    modules_active=bool(pop_modules_active),
                    de_sample_count=_de_sample_count,
                    de_policy_active=bool(de_policy_active),
                    argp_frozen_entries=_argp_frozen_entries,
                    argp_frozen_top_entries=_argp_frozen_top_entries,
                    argp_frozen_bottom_entries=_argp_frozen_bottom_entries,
                    argp_rolling_acc=_argp_rolling_acc,
                    argp_rolling_acc_top=_argp_rolling_acc_top,
                    argp_rolling_acc_bottom=_argp_rolling_acc_bottom,
                    restarts_done=int(restarts_done),
                    restart_triggered=bool(restart_triggered),
                    restart_cause=str(restart_cause),
                    archive_size=_archive_size,
                    archive_insertions=int(archive_insertions),
                    archive_samples_used=int(archive_samples_used),
                    mean_dim_coverage=_mean_dim_coverage,
                    local_search_triggered=bool(local_search_active),
                    local_search_trigger_score=int(local_search_trigger_score),
                    local_search_trigger_reason=str(local_search_trigger_reason),
                    local_search_basis_source=str(local_search_basis_source),
                    local_search_subspace_dim=int(local_search_subspace_dim_used),
                    local_search_elite_count_used=int(local_search_elite_count_used),
                    local_search_displacement_coherence=float(local_search_disp_coherence),
                    local_search_evals_used=int(local_search_evals_used_gen),
                    local_search_improvements=int(local_search_improvements),
                    local_search_best_delta=float(local_search_best_delta),
                    local_search_roi=float(_ls_roi),
                    interaction_graph_active=bool(_ig_active),
                    interaction_graph_density=float(_ig_density),
                    interaction_graph_block_count=int(_ig_block_count),
                    interaction_graph_mean_block_confidence=float(_ig_mean_block_conf),
                    interaction_graph_nontrivial_dim_fraction=float(_ig_nontrivial_dim_frac),
                    interaction_graph_orphan_dim_fraction=float(_ig_orphan_dim_frac),
                    interaction_graph_overall_confidence=float(_ig_overall_conf),
                    interaction_graph_refresh_count=int(_ig_refresh_count),
                    interaction_linkage_rows_learned=int(interaction_linkage_rows_learned),
                    interaction_linkage_rows_random=int(interaction_linkage_rows_random),
                    interaction_updates_from_de=int(interaction_updates_from_de),
                    interaction_updates_from_ls=int(interaction_updates_from_ls),
                    interaction_ls_blocks_used=tuple(int(v) for v in interaction_ls_blocks_used),
                    interaction_linkage_threshold=float(_linkage_gate_thr),
                    interaction_linkage_mix_base=float(interaction_linkage_mix_prob),
                    interaction_linkage_mix_eff=float(linkage_primary_row_prob),
                    rescue_owner=int(_rescue_owner_code),
                    cauchy_triggered=bool(cauchy_triggered),
                    bottom_widen_active=bool(_bottom_widen_active),
                    junior_dominant_success_count=int(_jun_dom_succ),
                    senior_dominant_success_count=int(_sen_dom_succ),
                    linkage_learned_rows=int(_link_learned_rows),
                    linkage_random_rows=int(_link_random_rows),
                    linkage_learned_accepted=int(_link_learned_accepted),
                    linkage_random_accepted=int(_link_random_accepted),
                    linkage_learned_reward_sum=float(_link_learned_reward_sum),
                    linkage_random_reward_sum=float(_link_random_reward_sum),
                    boundary_repairs_junior=int(_boundary_repairs_jun),
                    boundary_repairs_senior=int(_boundary_repairs_sen),
                    boundary_hit_rate=float(_boundary_hit_rate),
                    delayed_reward_lag10=float(_delayed_reward_lag10),
                    failure_alignment_mean=float(_failure_alignment_mean),
                    failure_alignment_pos_frac=float(_failure_alignment_pos_frac),
                    terra_trust_clip_rate=float(terra_trust_clip_rate),
                    terra_ls_allowed=bool(terra_ls_allowed),
                    terra_escape_allowed=bool(terra_escape_allowed),
                    terra_linkage_lift=(float(linkage_reliability_state.last_lift) if linkage_reliability_state is not None else 0.0),
                    terra_linkage_lcb=(float(linkage_reliability_state.last_lcb) if linkage_reliability_state is not None else 0.0),
                    terra_linkage_reliable=(bool(linkage_reliability_state.admit()) if linkage_reliability_state is not None else False),
                    terra_basin_memory_size=(int(len(basin_memory)) if basin_memory is not None else 0),
                    terra_basin_novelty_fires=int(basin_novelty_fires),
                    run_seed=int(_run_seed),
                    run_config_hash=str(_run_config_hash),
                    git_commit=str(_git_commit),
                    stop_reason=stop_note,
                )
            )

    # Deep-stall multi-start: report the global best-ever, which a full restart
    # preserves even when the working-population incumbent is currently worse.
    if _dsr_enabled and global_best_f < best_f:
        best_f = float(global_best_f)
        best_x = global_best_x

    # DT2 research: expose the final interaction-state (learned graph + blocks)
    # for fidelity diagnostics. Default None -> no effect; adapter never passes it.
    if research_state_sink is not None:
        research_state_sink["interaction_state"] = interaction_state

    res = DTGSKResult(
        best_x=best_x,
        best_f=float(best_f),
        nfes_used=int(budget.nfes_used),
        max_nfes=int(max_nfes),
        stop_reason="budget_exhausted",
        restarts_done=int(restarts_done),
    )

    if history is not None:
        return res, np.asarray(history, dtype=np.float64)
    return res
