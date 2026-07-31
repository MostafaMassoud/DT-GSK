"""Compiled per-generation trial-construction kernel shared by the GSK family.

The GSK family builds each generation's trial population the same way: a junior
and a senior "gained" candidate per cell (each with a better/other branch),
midpoint bound repair, and a dimension mask gated by the junior probability and
KR. That work is pure element-wise float64 arithmetic, so it is compiled here
with Numba while the random draws stay in the caller (NumPy ``Generator``). The
compiled kernel reproduces the NumPy path bit-for-bit (no ``fastmath``), so the
optimizers' numeric results and RNG draw order are unchanged.
"""

from __future__ import annotations

from typing import Any

import numpy as np

try:  # pragma: no cover - exercised by both branches across environments
    from numba import njit

    HAS_NUMBA = True
except Exception:  # pragma: no cover - numba is a declared dependency
    HAS_NUMBA = False


def _gsk_build_trial_numpy(
    pop: np.ndarray,
    fitness: np.ndarray,
    rg1: np.ndarray,
    rg2: np.ndarray,
    rg3: np.ndarray,
    r1: np.ndarray,
    r2: np.ndarray,
    r3: np.ndarray,
    kf_junior: np.ndarray,
    kf_senior: np.ndarray,
    junior_prob: np.ndarray,
    rand_split: np.ndarray,
    rand_kr_junior: np.ndarray,
    rand_kr_senior: np.ndarray,
    kr: np.ndarray,
    lb: np.ndarray,
    ub: np.ndarray,
) -> np.ndarray:
    """Vectorized reference implementation (used when Numba is unavailable)."""
    gained_junior = np.zeros_like(pop)
    worse_j = fitness > fitness[rg3]
    other_j = ~worse_j
    kfj = kf_junior[:, np.newaxis]
    if np.any(worse_j):
        gained_junior[worse_j, :] = pop[worse_j, :] + kfj[worse_j] * (
            pop[rg1[worse_j], :] - pop[rg2[worse_j], :] + pop[rg3[worse_j], :] - pop[worse_j, :]
        )
    if np.any(other_j):
        gained_junior[other_j, :] = pop[other_j, :] + kfj[other_j] * (
            pop[rg1[other_j], :] - pop[rg2[other_j], :] + pop[other_j, :] - pop[rg3[other_j], :]
        )
    low_j = gained_junior < lb
    high_j = gained_junior > ub
    gained_junior[low_j] = ((pop + lb)[low_j]) / 2.0
    gained_junior[high_j] = ((pop + ub)[high_j]) / 2.0

    gained_senior = np.zeros_like(pop)
    worse_s = fitness > fitness[r2]
    other_s = ~worse_s
    kfs = kf_senior[:, np.newaxis]
    if np.any(worse_s):
        gained_senior[worse_s, :] = pop[worse_s, :] + kfs[worse_s] * (
            pop[r1[worse_s], :] - pop[worse_s, :] + pop[r2[worse_s], :] - pop[r3[worse_s], :]
        )
    if np.any(other_s):
        gained_senior[other_s, :] = pop[other_s, :] + kfs[other_s] * (
            pop[r1[other_s], :] - pop[r2[other_s], :] + pop[other_s, :] - pop[r3[other_s], :]
        )
    low_s = gained_senior < lb
    high_s = gained_senior > ub
    gained_senior[low_s] = ((pop + lb)[low_s]) / 2.0
    gained_senior[high_s] = ((pop + ub)[high_s]) / 2.0

    junior_mask = rand_split <= junior_prob[:, np.newaxis]
    senior_mask = ~junior_mask
    junior_mask &= rand_kr_junior <= kr[:, np.newaxis]
    senior_mask &= rand_kr_senior <= kr[:, np.newaxis]
    trial = pop.copy()
    trial[junior_mask] = gained_junior[junior_mask]
    trial[senior_mask] = gained_senior[senior_mask]
    return trial


def _gsk_build_trial_loop(
    pop: np.ndarray,
    fitness: np.ndarray,
    rg1: np.ndarray,
    rg2: np.ndarray,
    rg3: np.ndarray,
    r1: np.ndarray,
    r2: np.ndarray,
    r3: np.ndarray,
    kf_junior: np.ndarray,
    kf_senior: np.ndarray,
    junior_prob: np.ndarray,
    rand_split: np.ndarray,
    rand_kr_junior: np.ndarray,
    rand_kr_senior: np.ndarray,
    kr: np.ndarray,
    lb: np.ndarray,
    ub: np.ndarray,
) -> np.ndarray:
    """Scalar loop body; compiled with Numba when available."""
    n = pop.shape[0]
    d = pop.shape[1]
    trial = pop.copy()
    for i in range(n):
        worse_j = fitness[i] > fitness[rg3[i]]
        worse_s = fitness[i] > fitness[r2[i]]
        jp = junior_prob[i]
        kri = kr[i]
        kfj = kf_junior[i]
        kfs = kf_senior[i]
        a1 = rg1[i]
        b1 = rg2[i]
        c1 = rg3[i]
        a2 = r1[i]
        b2 = r2[i]
        c2 = r3[i]
        for j in range(d):
            pij = pop[i, j]
            if worse_j:
                gj = pij + kfj * (pop[a1, j] - pop[b1, j] + pop[c1, j] - pij)
            else:
                gj = pij + kfj * (pop[a1, j] - pop[b1, j] + pij - pop[c1, j])
            if gj < lb[j]:
                gj = (pij + lb[j]) / 2.0
            elif gj > ub[j]:
                gj = (pij + ub[j]) / 2.0
            if worse_s:
                gs = pij + kfs * (pop[a2, j] - pij + pop[b2, j] - pop[c2, j])
            else:
                gs = pij + kfs * (pop[a2, j] - pop[b2, j] + pij - pop[c2, j])
            if gs < lb[j]:
                gs = (pij + lb[j]) / 2.0
            elif gs > ub[j]:
                gs = (pij + ub[j]) / 2.0
            if rand_split[i, j] <= jp:
                if rand_kr_junior[i, j] <= kri:
                    trial[i, j] = gj
            else:
                if rand_kr_senior[i, j] <= kri:
                    trial[i, j] = gs
    return trial


if HAS_NUMBA:
    _gsk_build_trial_compiled = njit(cache=True, fastmath=False)(_gsk_build_trial_loop)
else:  # pragma: no cover - exercised only without numba
    _gsk_build_trial_compiled = _gsk_build_trial_numpy


def _as_f64_vector(value: Any, size: int) -> np.ndarray:
    """Return a contiguous float64 vector of length ``size`` for kernel input."""
    arr = np.asarray(value, dtype=np.float64)
    if arr.ndim == 0:
        return np.full(size, float(arr), dtype=np.float64)
    return np.ascontiguousarray(arr.reshape(-1), dtype=np.float64)


def gsk_build_trial(
    pop: np.ndarray,
    fitness: np.ndarray,
    rg1: np.ndarray,
    rg2: np.ndarray,
    rg3: np.ndarray,
    r1: np.ndarray,
    r2: np.ndarray,
    r3: np.ndarray,
    *,
    kf_junior: Any,
    kf_senior: Any,
    junior_prob: Any,
    rand_split: np.ndarray,
    rand_kr_junior: np.ndarray,
    rand_kr_senior: np.ndarray,
    kr: Any,
    lb: np.ndarray,
    ub: np.ndarray,
) -> np.ndarray:
    """Build one generation's trial population (compiled when Numba is available).

    ``kf_junior``/``kf_senior``/``junior_prob``/``kr`` accept either scalars or
    per-individual vectors; scalars are broadcast to one value per row. All
    random arrays are drawn by the caller so the RNG stream is unchanged.
    """
    n = int(pop.shape[0])
    population = np.ascontiguousarray(pop, dtype=np.float64)
    fitness_v = np.ascontiguousarray(np.asarray(fitness, dtype=np.float64).reshape(-1))
    return _gsk_build_trial_compiled(
        population,
        fitness_v,
        np.ascontiguousarray(np.asarray(rg1, dtype=np.int64).reshape(-1)),
        np.ascontiguousarray(np.asarray(rg2, dtype=np.int64).reshape(-1)),
        np.ascontiguousarray(np.asarray(rg3, dtype=np.int64).reshape(-1)),
        np.ascontiguousarray(np.asarray(r1, dtype=np.int64).reshape(-1)),
        np.ascontiguousarray(np.asarray(r2, dtype=np.int64).reshape(-1)),
        np.ascontiguousarray(np.asarray(r3, dtype=np.int64).reshape(-1)),
        _as_f64_vector(kf_junior, n),
        _as_f64_vector(kf_senior, n),
        _as_f64_vector(junior_prob, n),
        np.ascontiguousarray(rand_split, dtype=np.float64),
        np.ascontiguousarray(rand_kr_junior, dtype=np.float64),
        np.ascontiguousarray(rand_kr_senior, dtype=np.float64),
        _as_f64_vector(kr, n),
        np.ascontiguousarray(np.asarray(lb, dtype=np.float64).reshape(-1)),
        np.ascontiguousarray(np.asarray(ub, dtype=np.float64).reshape(-1)),
    )
