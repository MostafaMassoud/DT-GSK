from __future__ import annotations

import numpy as np
import pytest

from gsk_family.common.donors import (
    gained_shared_junior_r1r2r3,
    gained_shared_senior_r1r2r3,
)
from gsk_family.common.rng import RandomContext


def _manual_junior_r3(rng: RandomContext, r1: np.ndarray, r2: np.ndarray) -> np.ndarray:
    pop_size = r1.size
    idx = np.arange(pop_size)
    r3 = np.floor(np.asarray(rng.random(pop_size)) * pop_size).astype(np.int64)
    for _ in range(1001):
        collision = (r3 == idx) | (r3 == r1) | (r3 == r2)
        count = int(np.count_nonzero(collision))
        if count == 0:
            return r3
        r3[collision] = np.floor(np.asarray(rng.random(count)) * pop_size).astype(np.int64)
    raise AssertionError("manual junior R3 failed")


def test_junior_donors_use_rank_neighbors_for_sorted_order() -> None:
    pop_size = 30
    order = np.arange(pop_size)
    rng = RandomContext(21, "twister")

    r1, r2, r3 = gained_shared_junior_r1r2r3(order, rng)

    assert r1[0] == 1
    assert r2[0] == 2
    assert r1[-1] == pop_size - 3
    assert r2[-1] == pop_size - 2
    np.testing.assert_array_equal(r1[1:-1], np.arange(pop_size - 2))
    np.testing.assert_array_equal(r2[1:-1], np.arange(2, pop_size))
    idx = np.arange(pop_size)
    assert np.all((r3 != idx) & (r3 != r1) & (r3 != r2))


def test_junior_donors_use_rank_neighbors_for_permuted_order() -> None:
    pop_size = 30
    order = np.array([7, 2, 19, 4, 0, 9, 21, 1, 26, 3, 11, 5, 28, 13, 6, 14, 8, 15, 10, 16, 12, 17, 18, 20, 22, 23, 24, 25, 27, 29])
    rank_of = np.empty(pop_size, dtype=np.int64)
    rank_of[order] = np.arange(pop_size)

    r1, r2, _ = gained_shared_junior_r1r2r3(order, RandomContext(22, "twister"))

    for individual in range(pop_size):
        rank = rank_of[individual]
        if rank == 0:
            assert r1[individual] == order[1]
            assert r2[individual] == order[2]
        elif rank == pop_size - 1:
            assert r1[individual] == order[-3]
            assert r2[individual] == order[-2]
        else:
            assert r1[individual] == order[rank - 1]
            assert r2[individual] == order[rank + 1]


def test_junior_donors_preserve_r3_draw_order() -> None:
    order = np.array([3, 0, 4, 1, 5, 2])
    rng = RandomContext(123, "twister")
    manual_rng = RandomContext(123, "twister")

    r1, r2, r3 = gained_shared_junior_r1r2r3(order, rng)
    expected_r3 = _manual_junior_r3(manual_rng, r1, r2)

    np.testing.assert_array_equal(r3, expected_r3)
    np.testing.assert_allclose(rng.random(8), manual_rng.random(8))


def test_senior_donors_draw_from_reference_rank_blocks() -> None:
    pop_size = 100
    order = np.array(
        [42, 3, 75, 12, 99, 0, 54, 28, 61, 7, 83, 19, 45, 32, 90, 11, 68, 24, 36, 5,
         72, 14, 58, 29, 94, 1, 47, 31, 80, 17, 63, 22, 50, 39, 88, 9, 70, 26, 57, 16,
         97, 4, 66, 21, 53, 35, 85, 10, 74, 27, 60, 18, 49, 33, 91, 2, 69, 25, 56, 15,
         96, 6, 65, 20, 52, 34, 84, 13, 73, 30, 59, 23, 48, 37, 89, 8, 71, 40, 55, 41,
         98, 43, 64, 44, 51, 46, 82, 47, 76, 62, 67, 78, 79, 81, 86, 87, 92, 93, 95, 77]
    )
    order = np.array([*dict.fromkeys(order), *[i for i in range(pop_size) if i not in set(order)]])
    assert np.array_equal(np.sort(order), np.arange(pop_size))

    r1, r2, r3 = gained_shared_senior_r1r2r3(order, 0.1, RandomContext(31, "twister"))

    assert r1.shape == (pop_size,)
    assert r2.shape == (pop_size,)
    assert r3.shape == (pop_size,)
    assert np.all(np.isin(r1, order[:10]))
    assert np.all(np.isin(r2, order[10:90]))
    assert np.all(np.isin(r3, order[90:]))


def test_senior_donors_support_shrinking_population_edge() -> None:
    order = np.arange(12)

    r1, r2, r3 = gained_shared_senior_r1r2r3(order, 0.05, RandomContext(32, "twister"))

    np.testing.assert_array_equal(r1, np.zeros(12, dtype=np.int64))
    assert np.all(np.isin(r2, np.arange(1, 11)))
    np.testing.assert_array_equal(r3, np.full(12, 11, dtype=np.int64))


def test_senior_donors_preserve_draw_order() -> None:
    order = np.arange(20)
    rng = RandomContext(321, "twister")
    manual = RandomContext(321, "twister")

    r1, r2, r3 = gained_shared_senior_r1r2r3(order, 0.1, rng)
    best_block = order[:2]
    middle_block = order[2:18]
    worst_block = order[18:]
    expected_r1 = best_block[np.floor(np.asarray(manual.random(20)) * best_block.size).astype(np.int64)]
    expected_r2 = middle_block[np.floor(np.asarray(manual.random(20)) * middle_block.size).astype(np.int64)]
    expected_r3 = worst_block[np.floor(np.asarray(manual.random(20)) * worst_block.size).astype(np.int64)]

    np.testing.assert_array_equal(r1, expected_r1)
    np.testing.assert_array_equal(r2, expected_r2)
    np.testing.assert_array_equal(r3, expected_r3)
    np.testing.assert_allclose(rng.random(5), manual.random(5))


def test_donor_helpers_validate_reference_constraints() -> None:
    with pytest.raises(ValueError, match="permutation"):
        gained_shared_junior_r1r2r3([0, 1, 1, 3], RandomContext(1, "twister"))
    with pytest.raises(ValueError, match="NP >= 4"):
        gained_shared_junior_r1r2r3([0, 1, 2], RandomContext(1, "twister"))
    with pytest.raises(ValueError, match="empty block"):
        gained_shared_senior_r1r2r3(np.arange(8), 0.05, RandomContext(1, "twister"))

