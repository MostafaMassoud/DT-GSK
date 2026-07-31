"""
Junior Gaining-Sharing Phase - Index Selection
==============================================

The Junior phase is the EXPLORATION component of the GSK algorithm.
It selects knowledge sources (R1, R2, R3) based on rank proximity,
encouraging individuals to learn from their immediate neighbors.

How It Works
------------
For each individual i in the population:

    Population sorted by fitness:

    Rank:     0      1      2     ...    N-2    N-1
            [best] [2nd]  [3rd]  ...   [2nd   [worst]
                                       worst]

    For individual i at rank r (middle of population):
    - R1 = neighbor at rank r-1 (better)
    - R2 = neighbor at rank r+1 (worse)
    - R3 = random individual (≠ i, R1, R2)

Special Cases
-------------
- Best individual (rank 0): Cannot look at rank -1, so uses R1=rank1, R2=rank2
- Worst individual (rank N-1): Cannot look at rank N, so uses R1=rank(N-3), R2=rank(N-2)

RNG Path Convergence
--------------------
Both the Numba and pure-Python paths consume the **same** random draws.  We
pre-draw a single ``(NP, MAX_R3_ATTEMPTS)`` integer pool in Python and pass it
to whichever kernel is active.  Each individual uses ``pool[i, 0]`` as its
initial R3 candidate; on conflict it walks to ``pool[i, 1]``, ``pool[i, 2]``,
... until either a non-conflicting candidate is found or attempts are
exhausted.  This eliminates the previous Numba LCG / Python RNG path
divergence.
"""

from __future__ import annotations

import numpy as np

# Numba-accelerated core (graceful fallback)
try:
    from ._numba_accel import junior_r1r2r3_core_fast as _jr_fast
except ImportError:
    _jr_fast = None

# Maximum number of dedup attempts per individual.  At pop sizes used by
# DT-GSK (NP <= 5*D), the chance that 32 successive uniform draws all
# collide with {i, R1, R2} is < (3/NP)^32 — essentially impossible.
MAX_R3_ATTEMPTS = 32


def gained_shared_junior_r1r2r3(
    ind_best: np.ndarray,
    rng: np.random.Generator,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Select knowledge source indices (R1, R2, R3) for the Junior phase.
    """
    if ind_best.dtype != np.int64:
        ind_best = ind_best.astype(np.int64)
    pop_size = ind_best.shape[0]

    # Pre-draw the unified R3 candidate pool consumed by BOTH paths.
    r3_pool = rng.integers(0, pop_size, size=(pop_size, MAX_R3_ATTEMPTS), dtype=np.int64)

    if _jr_fast is not None:
        return _jr_fast(ind_best, r3_pool)

    # Fallback: pure-Python path (uses the same r3_pool the Numba kernel would).
    idx = np.arange(pop_size, dtype=np.int64)
    rank_of = np.empty(pop_size, dtype=np.int64)
    rank_of[ind_best] = idx

    R1 = np.empty(pop_size, dtype=np.int64)
    R2 = np.empty(pop_size, dtype=np.int64)

    best_mask = (rank_of == 0)
    worst_mask = (rank_of == pop_size - 1)
    middle_mask = ~(best_mask | worst_mask)

    # No np.any() guards needed: for NP >= 4 (enforced invariant) all three
    # groups are guaranteed non-empty, and boolean-indexed assignment to an
    # all-False mask is a harmless no-op anyway.
    R1[best_mask] = ind_best[1]
    R2[best_mask] = ind_best[2]

    R1[worst_mask] = ind_best[pop_size - 3]
    R2[worst_mask] = ind_best[pop_size - 2]

    ranks = rank_of[middle_mask]
    R1[middle_mask] = ind_best[ranks - 1]
    R2[middle_mask] = ind_best[ranks + 1]

    R3 = r3_pool[:, 0].copy()
    for i in range(pop_size):
        attempt = 0
        while (R3[i] == i or R3[i] == R1[i] or R3[i] == R2[i]):
            attempt += 1
            if attempt >= MAX_R3_ATTEMPTS:
                # Fallback: scan linearly for any non-conflicting index.
                for cand in range(pop_size):
                    if cand != i and cand != R1[i] and cand != R2[i]:
                        R3[i] = cand
                        break
                break
            R3[i] = r3_pool[i, attempt]

    return R1, R2, R3
