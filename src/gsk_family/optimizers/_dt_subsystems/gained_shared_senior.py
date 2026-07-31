"""
Senior Gaining-Sharing Phase - Index Selection
==============================================

The Senior phase is the EXPLOITATION component of the GSK algorithm.
It selects knowledge sources (R1, R2, R3) from stratified population groups,
guiding individuals toward better regions of the search space.

How It Works
------------
The population is divided into three groups by fitness:

    ┌─────────────┬─────────────────────────┬─────────────┐
    │   Top 10%   │       Middle 80%        │  Bottom 10% │
    │   (Elite)   │    (Average performers) │   (Worst)   │
    │             │                         │             │
    │  R1 source  │       R2 source         │  R3 source  │
    └─────────────┴─────────────────────────┴─────────────┘

For each individual i:
- R1 = random from top 10% (elite guidance)
- R2 = random from middle 80% (reference point)
- R3 = random from bottom 10% (contrast/diversity)

Purpose in GSK
--------------
The Senior phase promotes EXPLOITATION by:
1. R1 from elites pulls individuals toward best solutions
2. R2 from middle provides stable reference direction
3. R3 from worst indicates regions to avoid

Group Boundary Calculation
--------------------------
For population size N:
- best_end = round(0.1 × N)    → Top group: indices [0, best_end)
- mid_end = round(0.9 × N)     → Middle group: indices [best_end, mid_end)
                                → Worst group: indices [mid_end, N)

Note: Uses "round away from zero" for ties (e.g., 0.5 → 1, not banker's rounding).
"""

from __future__ import annotations

import math

import numpy as np

# Numba-accelerated core (graceful fallback)
try:
    from ._numba_accel import senior_r1r2r3_fast as _sr_fast
except ImportError:
    _sr_fast = None


def _round_away_from_zero(x: float) -> int:
    return int(math.copysign(math.floor(abs(x) + 0.5), x))


def gained_shared_senior_r1r2r3_from_rands(
    ind_best: np.ndarray,
    r1_rand: np.ndarray,
    r2_rand: np.ndarray,
    r3_rand: np.ndarray,
    p: float,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Select knowledge source indices (R1, R2, R3) using **pre-drawn** rands.

    Identical numerics to :func:`gained_shared_senior_r1r2r3` for the
    same ``(ind_best, p)`` and the same drawn arrays — this helper just
    skips the ``rng.random(pop_size)`` step so the caller can reuse the
    same uniform sample for two different ``p`` values without consuming
    additional RNG state.

    The v0 split-senior path (``p_senior_split_enabled``, locked-headline
    at ``D >= 50``) uses this to dispatch a single set of draws across
    two effective ``p_senior`` scalars (top / bottom) and merge by mask.
    """
    if ind_best.dtype != np.int64:
        ind_best = ind_best.astype(np.int64)
    pop_size = ind_best.shape[0]

    if not (0.0 < p < 0.5):
        raise ValueError(
            f"p must be strictly in (0, 0.5) so the best/middle/worst groups "
            f"(each of size round(p*NP)) partition the population without "
            f"overlap; got {p!r}"
        )

    if _sr_fast is not None:
        return _sr_fast(ind_best, r1_rand, r2_rand, r3_rand, p)

    # Fallback: original numpy path
    n_grp = _round_away_from_zero(p * pop_size)
    if n_grp < 1:
        n_grp = 1
    if 2 * n_grp >= pop_size:
        n_grp = max(1, (pop_size - 1) // 2)

    best_group = ind_best[:n_grp]
    middle_group = ind_best[n_grp : pop_size - n_grp]
    worst_group = ind_best[pop_size - n_grp :]

    len_best = len(best_group)
    len_middle = len(middle_group)
    len_worst = len(worst_group)

    if len_best == 0 or len_middle == 0 or len_worst == 0:
        raise ValueError(
            f"Empty group detected with pop_size={pop_size}: "
            f"best={len_best}, middle={len_middle}, worst={len_worst}"
        )

    r1_idx = np.ceil(r1_rand * len_best).astype(np.int64) - 1
    r2_idx = np.ceil(r2_rand * len_middle).astype(np.int64) - 1
    r3_idx = np.ceil(r3_rand * len_worst).astype(np.int64) - 1

    if __debug__:
        if r1_idx.min() < 0 or r1_idx.max() >= len_best:
            raise ValueError("Out-of-range R1 indices generated")
        if r2_idx.min() < 0 or r2_idx.max() >= len_middle:
            raise ValueError("Out-of-range R2 indices generated")
        if r3_idx.min() < 0 or r3_idx.max() >= len_worst:
            raise ValueError("Out-of-range R3 indices generated")

    R1 = best_group[r1_idx]
    R2 = middle_group[r2_idx]
    R3 = worst_group[r3_idx]

    return R1, R2, R3


def gained_shared_senior_r1r2r3(
    ind_best: np.ndarray,
    rng: np.random.Generator,
    *,
    p: float = 0.1,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Select knowledge source indices (R1, R2, R3) for the Senior phase.
    """
    pop_size = ind_best.shape[0]
    r1_rand = rng.random(pop_size)
    r2_rand = rng.random(pop_size)
    r3_rand = rng.random(pop_size)
    return gained_shared_senior_r1r2r3_from_rands(ind_best, r1_rand, r2_rand, r3_rand, p)
