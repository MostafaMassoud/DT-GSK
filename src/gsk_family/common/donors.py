"""Gaining-sharing donor index helpers."""

from __future__ import annotations

from typing import Any

import numpy as np

from gsk_family.common.numeric_compat import compat_round_int
from gsk_family.common.rng import RandomContext


def _as_zero_based_permutation(ind_best: Any, *, validate: bool = True) -> np.ndarray:
    """Validate and return a zero-based best-to-worst permutation."""
    order = np.asarray(ind_best, dtype=np.int64).reshape(-1)
    pop_size = int(order.size)
    if pop_size == 0:
        raise ValueError("ind_best must contain at least one index.")
    if validate and not np.array_equal(np.sort(order), np.arange(pop_size, dtype=np.int64)):
        raise ValueError("ind_best must be a 0-based permutation of 0..NP-1.")
    return order


def gained_shared_junior_r1r2r3(
    ind_best: Any,
    rng: RandomContext,
    *,
    max_iterations: int = 1000,
    validate: bool = True,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Port of ``Gained_Shared_Junior_R1R2R3.m`` with 0-based indices."""
    order = _as_zero_based_permutation(ind_best, validate=validate)
    pop_size = int(order.size)
    if pop_size < 4:
        raise ValueError("Junior donor helper requires NP >= 4.")

    idx: np.ndarray = np.arange(pop_size, dtype=np.int64)
    rank_of: np.ndarray = np.empty(pop_size, dtype=np.int64)
    rank_of[order] = idx

    r1: np.ndarray = np.empty(pop_size, dtype=np.int64)
    r2: np.ndarray = np.empty(pop_size, dtype=np.int64)

    best_mask = rank_of == 0
    worst_mask = rank_of == pop_size - 1
    middle_mask = ~(best_mask | worst_mask)

    r1[best_mask] = order[1]
    r2[best_mask] = order[2]
    r1[worst_mask] = order[pop_size - 3]
    r2[worst_mask] = order[pop_size - 2]

    middle_ranks = rank_of[middle_mask]
    r1[middle_mask] = order[middle_ranks - 1]
    r2[middle_mask] = order[middle_ranks + 1]

    r3 = np.floor(np.asarray(rng.random(pop_size)) * pop_size).astype(np.int64)
    for iteration in range(max_iterations + 1):
        collision = (r3 == idx) | (r3 == r1) | (r3 == r2)
        count = int(np.count_nonzero(collision))
        if count == 0:
            return r1, r2, r3
        if iteration >= max_iterations:
            raise RuntimeError("Cannot generate collision-free junior R3 donors.")
        r3[collision] = np.floor(np.asarray(rng.random(count)) * pop_size).astype(np.int64)

    raise AssertionError("Unreachable junior donor loop exit.")


def gained_shared_senior_r1r2r3(
    ind_best: Any,
    p: float,
    rng: RandomContext,
    *,
    validate: bool = True,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Port of ``Gained_Shared_Senior_R1R2R3.m`` with 0-based indices."""
    order = _as_zero_based_permutation(ind_best, validate=validate)
    pop_size = int(order.size)
    fraction = float(p)
    if not 0.0 < fraction < 0.5:
        raise ValueError(f"p must be in the open interval (0, 0.5), got {p}.")

    top_end = compat_round_int(pop_size * fraction)
    mid_end = compat_round_int(pop_size * (1.0 - fraction))
    if top_end <= 0 or mid_end <= top_end or mid_end >= pop_size:
        raise ValueError(
            "Senior donor partition contains an empty block: "
            f"NP={pop_size}, p={fraction}, top_end={top_end}, mid_end={mid_end}."
        )

    best_block = order[:top_end]
    middle_block = order[top_end:mid_end]
    worst_block = order[mid_end:]

    r1 = best_block[np.floor(np.asarray(rng.random(pop_size)) * best_block.size).astype(np.int64)]
    r2 = middle_block[
        np.floor(np.asarray(rng.random(pop_size)) * middle_block.size).astype(np.int64)
    ]
    r3 = worst_block[
        np.floor(np.asarray(rng.random(pop_size)) * worst_block.size).astype(np.int64)
    ]
    return r1.astype(np.int64, copy=False), r2.astype(np.int64, copy=False), r3.astype(
        np.int64, copy=False
    )
