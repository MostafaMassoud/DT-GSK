"""Dimension-aware ``pub`` profile builder for the migrated DT-GSK optimizer.

This is a faithful port of the source project's ``profiles.py`` ``pub`` profile
together with the ``dt_gsk_``-prefix-strip mapping that the source's
``experiment._build_dt_gsk_config`` applied. It builds the exact per-dimension
``DTGSKConfig`` the source produces for the paper-facing ``pub`` profile, so the
migrated optimizer reproduces the source configuration (and therefore its
trajectory) bit-for-bit. Byte-identity is locked by
``tests/unit/test_dt_profiles.py`` against an oracle generated from the source.

Keys below are the source ``dt_gsk_*`` Config field names with the ``dt_gsk_``
prefix stripped, i.e. the ``DTGSKConfig`` field names.
"""

from __future__ import annotations

import dataclasses

import numpy as np

from gsk_family.optimizers._dt_core import DTGSKConfig

# Linkage block-size schedule (dim-keyed; passed wholesale, dim-independent).
_DEFAULT_BLOCK_SIZES: dict[int, int] = {
    1: 1, 5: 5, 6: 5, 7: 5, 10: 5, 12: 5, 13: 5, 15: 5, 20: 5,
    22: 5, 26: 5, 30: 5, 40: 5, 50: 10, 96: 10, 100: 10,
    120: 10, 126: 10, 140: 10, 240: 10,
}

# pub profile -- common fields (all dim tiers).
_PUB_COMMON: dict[str, object] = dict(
    ace_enabled=True,
    psr_enabled=True,
    argp_enabled=True,
    argp_window=30,
    argp_warmup_frac=0.15,
    force_nonzero_update=True,
    linkage_block_size_by_dim=_DEFAULT_BLOCK_SIZES,
    ace_learning_rate=0.10,
    ace_start_frac=0.05,
    ace_min_prob=0.05,
    bse_enabled=True,
    arch_enabled=True,
    ace_coverage_weighted=False,
    ace_coverage_exponent=2.0,
    ace_de_F=0.5,
    ace_de_CR=0.9,
)

_PUB_D_LT_20: dict[str, object] = dict(
    argp_threshold=0.02,
    linkage_block_refresh_period=20,
    bse_trigger_mode="stagnation",
    bse_signal_window=10,
    bse_acceptance_floor=0.10,
    bse_diversity_floor_frac=0.35,
    bse_cauchy_enabled=False,
    bse_cauchy_frac=0.10,
    bse_cauchy_scale=0.05,
    psr_schedule="nlpsr",
    ace_memory_mode="single",
    kr_min_dims=0,
    ace_de_entry=False,
    ace_de_init_prob=0.20,
    linkage_blockwise_enabled=True,
    linkage_min_dim=10,
    linkage_block_mix_prob=0.70,
    local_search_enabled=True,
    local_search_start_frac=0.80,
    local_search_eval_budget_frac=0.02,
    local_search_elite_count=2,
    local_search_step_scale=0.20,
)

_PUB_D_20_TO_49: dict[str, object] = dict(
    argp_threshold=0.02,
    linkage_block_refresh_period=20,
    psr_schedule="nlpsr",
    ace_memory_mode="top_bottom",
    kr_min_dims=20,
    ace_de_entry=True,
    ace_de_init_prob=0.10,
    linkage_blockwise_enabled=True,
    linkage_min_dim=10,
    linkage_block_mix_prob=0.40,
    bse_trigger_mode="triple",
    bse_cauchy_enabled=True,
    bse_cauchy_scale=0.04,
    local_search_enabled=True,
    local_search_start_frac=0.80,
    local_search_eval_budget_frac=0.01,
    local_search_elite_count=3,
    local_search_step_scale=0.20,
)

_PUB_D_GE_50: dict[str, object] = dict(
    n_min=25,
    psr_schedule="nlpsr",
    ace_memory_mode="top_bottom",
    kr_min_dims=40,
    ace_de_entry=True,
    ace_de_init_prob=0.20,
    linkage_blockwise_enabled=True,
    linkage_min_dim=30,
    linkage_block_mix_prob=0.70,
    linkage_block_refresh_period=10,
    bse_trigger_mode="triple",
    bse_cauchy_enabled=True,
    bse_cauchy_scale=0.04,
    argp_threshold=0.010,
    local_search_enabled=True,
    local_search_start_frac=0.70,
    local_search_eval_budget_frac=0.03,
    local_search_elite_count=5,
    local_search_step_scale=0.10,
)

_SGSM_D_GE_50_EXTRA: dict[str, object] = dict(
    interaction_graph_enabled=True,
    interaction_graph_min_dim=50,
    interaction_graph_decay=0.95,
    interaction_graph_lr=1.0,
    interaction_graph_refresh_period=5,
    interaction_graph_warmup_frac=0.10,
    interaction_graph_edge_floor=1e-4,
    interaction_block_min_size=2,
    interaction_block_max_size=10,
    interaction_confidence_min=0.55,
    interaction_linkage_confidence_min=0.55,
    interaction_ls_confidence_min=0.65,
    interaction_linkage_mix_prob=0.50,
    interaction_use_for_linkage=True,
    interaction_use_for_local_search=True,
    interaction_ls_top_blocks=3,
    interaction_ls_dim_cap=20,
    interaction_min_updates=10,
    interaction_min_refreshes=2,
    interaction_min_nontrivial_dims=4,
    interaction_post_restart_cooldown=5,
    interaction_restart_decay=0.50,
    interaction_de_update_weight=0.0,
    interaction_ls_update_weight=0.25,
)

_D_LT_20_ESCAPE_OVERRIDES: dict[str, object] = dict(
    bse_max_restarts=4,
    bse_restart_frac=0.30,
    bse_cauchy_enabled=True,
)

_D30_BEST_STATUS_OVERRIDES: dict[str, object] = dict(
    bse_restart_frac=0.30,
    p_senior=0.15,
)

_V0_SPLIT_BW10_OVERRIDES: dict[str, object] = dict(
    p_senior=0.05,
    p_senior_split_enabled=True,
    p_senior_bottom_wide=0.10,
)

_ADAPTIVE_QUADRUPLE: dict[str, object] = dict(
    interaction_confidence_adaptive=True,
    interaction_confidence_adaptive_window=30,
    interaction_confidence_adaptive_percentile=0.50,
    interaction_confidence_adaptive_floor=0.12,
    interaction_confidence_adaptive_min_samples=5,
)

_ADAPTIVE_STATIC_TRIPLE: dict[str, object] = dict(
    interaction_confidence_min=0.35,
    interaction_linkage_confidence_min=0.35,
    interaction_ls_confidence_min=0.45,
)

_D_GE_50_PROMOTED: dict[str, object] = dict(
    local_search_eval_budget_frac=0.05,
    bse_max_restarts=4,
    final_polish_enabled=True,
    final_polish_start_frac=0.96,
    final_polish_budget_frac=0.02,
    final_polish_step_frac=0.05,
)

_PUB_D_GE_100_EXTRA: dict[str, object] = dict(
    terra_enabled=True,
    budget_policy_enabled=True,
    basin_memory_enabled=True,
    sp_nlpsr_enabled=True,
    sp_nlpsr_min_subspace_samples=64,
    sp_nlpsr_release_tau=0.70,
    sp_nlpsr_extra_floor=0,
    ace_de_entry=False,
    interaction_update_period=10,
    interaction_update_max_samples=24,
    interaction_graph_refresh_period=20,
    interaction_probe_rate=0.05,
    interaction_lift_min_samples=24,
    local_search_method="coordinate",
    local_search_auto_subspace=False,
    local_search_eval_budget_frac=0.02,
    local_search_elite_count=2,
    local_search_period=2,
    local_search_post_ls_cooldown=3,
    bse_max_restarts=2,
    late_accept_clip_enabled=True,
    late_accept_clip_tau_floor=0.85,
    late_accept_clip_acc_high=0.30,
    late_accept_clip_log_drop_eps=-2.0,
    late_accept_clip_streak_k=5,
    late_accept_clip_strict_eps=1e-3,
    late_accept_clip_log_drop_ema_alpha=0.30,
    frozen_broaden_enabled=True,
    frozen_broaden_acc_floor=0.05,
    frozen_broaden_log_drop_eps=-3.0,
    frozen_broaden_streak_k=10,
    frozen_broaden_window_m=20,
    frozen_broaden_cooldown=10,
    frozen_broaden_factor=1.5,
    link_random_mix_enabled=True,
    link_random_mix_tau_floor=0.50,
    link_random_mix_negative_lift=-0.05,
    link_random_mix_severe_lift=-0.20,
    link_random_mix_strength=0.5,
    link_random_mix_window=20,
    link_random_mix_ema_alpha=0.20,
)

_DTGSK_FIELDS = frozenset(f.name for f in dataclasses.fields(DTGSKConfig))


def _pub_tier_extras(dim: int) -> dict[str, object]:
    """Return the tier-specific ``pub`` overrides for ``dim`` (merge order matters)."""
    if dim < 20:
        return {**_PUB_D_LT_20, **_D_LT_20_ESCAPE_OVERRIDES}
    if dim < 50:
        return {**_PUB_D_20_TO_49, **_D30_BEST_STATUS_OVERRIDES}
    tier: dict[str, object] = {
        **_PUB_D_GE_50,
        **_SGSM_D_GE_50_EXTRA,
        **_ADAPTIVE_STATIC_TRIPLE,
        **_ADAPTIVE_QUADRUPLE,
        **_V0_SPLIT_BW10_OVERRIDES,
        **_D_GE_50_PROMOTED,
    }
    if dim >= 100:
        tier.update(_PUB_D_GE_100_EXTRA)
    return tier


def pub_overrides(dim: int) -> dict[str, object]:
    """Return the full ``pub`` profile override mapping for ``dim``."""
    overrides = {**_PUB_COMMON, **_pub_tier_extras(int(dim))}
    return {k: v for k, v in overrides.items() if k in _DTGSK_FIELDS}


def build_pub_config(
    dim: int,
    *,
    seed: int,
    max_nfes: int,
    bounds: tuple[float, float] = (-100.0, 100.0),
    rand_generator: str = "threefry",
) -> DTGSKConfig:
    """Build the dimension-aware ``pub`` DTGSKConfig for one run.

    Reproduces the source ``Config -> apply_step2_profile -> _build_dt_gsk_config``
    chain for the ``pub`` profile: profile fields are applied by dimension tier,
    run-specific fields (dim, seed, max_nfes, bounds, generator) are set per call,
    and all other fields take the DTGSKConfig defaults.
    """
    overrides = pub_overrides(int(dim))
    # Preserve per-dimension bounds (e.g. CEC2011 real-world problems) as float
    # arrays; collapse uniform bounds to scalar floats so CEC2017/sphere configs
    # stay byte-identical to the source ``(lo, hi)`` form.
    if isinstance(bounds[0], (list, tuple, np.ndarray)):
        # JSON-serializable, immutable tuples (matches the source's CEC2011
        # ``get_cec2011_bounds`` tuple form); ``bounds_matrix`` wraps them in
        # ``np.asarray`` when building the (2, D) repair array.
        norm_bounds = (
            tuple(float(x) for x in np.asarray(bounds[0], dtype=np.float64).reshape(-1)),
            tuple(float(x) for x in np.asarray(bounds[1], dtype=np.float64).reshape(-1)),
        )
    else:
        norm_bounds = (float(bounds[0]), float(bounds[1]))
    return DTGSKConfig(
        dim=int(dim),
        seed=int(seed),
        max_nfes=int(max_nfes),
        bounds=norm_bounds,
        rand_generator=str(rand_generator),
        **overrides,
    )
