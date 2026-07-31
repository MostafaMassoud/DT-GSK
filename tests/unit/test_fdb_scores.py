from __future__ import annotations

import numpy as np

from gsk_family.common.rng import RandomContext
from gsk_family.optimizers.fdb_agsk import _fdb_junior_r1r2r3, _fdb_senior_r1r2r3
from gsk_family.optimizers.fdb_scores import (
    fdb_score_best,
    fdb_score_ranking,
    fdb_score_roulette,
)


def _example_population() -> tuple[np.ndarray, np.ndarray]:
    population = np.array(
        [
            [0.0, 0.0],
            [5.0, 0.0],
            [2.0, 0.0],
        ]
    )
    fitness = np.array([10.0, 14.0, 18.0])
    return population, fitness


def test_fdb_score_best_selects_fitness_distance_balance_argmax() -> None:
    population, fitness = _example_population()

    assert fdb_score_best(population, fitness, RandomContext(1, "twister")) == 1


def test_fdb_score_ranking_returns_descending_score_order() -> None:
    population, fitness = _example_population()

    np.testing.assert_array_equal(
        fdb_score_ranking(population, fitness, RandomContext(1, "twister")),
        np.array([1, 0, 2]),
    )


def test_fdb_score_roulette_uses_score_weighted_threshold() -> None:
    population, fitness = _example_population()
    expected_rng = RandomContext(9, "twister")
    threshold = float(expected_rng.random()) * 2.9
    expected = int(np.searchsorted(np.array([1.0, 2.5, 2.9]), threshold, side="left"))

    assert fdb_score_roulette(population, fitness, RandomContext(9, "twister")) == expected


def test_fdb_flat_fitness_degenerate_branches_match_reference_shape() -> None:
    population = np.arange(12.0).reshape(6, 2)
    fitness = np.ones(6)

    expected_rng = RandomContext(7, "twister")
    expected_index = int(expected_rng.randi(6)) - 1
    assert fdb_score_best(population, fitness, RandomContext(7, "twister")) == expected_index

    ranking = fdb_score_ranking(population, fitness, RandomContext(7, "twister"))
    np.testing.assert_array_equal(ranking, np.array([], dtype=np.int64))

    expected_rng = RandomContext(8, "twister")
    expected_index = int(expected_rng.randi(6)) - 1
    assert fdb_score_roulette(population, fitness, RandomContext(8, "twister")) == expected_index


def test_fdb_senior_case1_injects_fdb_index_as_r2() -> None:
    order = np.arange(20, dtype=np.int64)

    _, r2, _ = _fdb_senior_r1r2r3(order, 1, 7, RandomContext(12, "twister"))

    np.testing.assert_array_equal(r2, np.full(20, 7))


def test_fdb_senior_case2_uses_fdb_ranking_tail_for_r3() -> None:
    order = np.arange(20, dtype=np.int64)
    ranking = np.arange(19, -1, -1, dtype=np.int64)

    _, _, r3 = _fdb_senior_r1r2r3(order, 2, ranking, RandomContext(12, "twister"))

    assert set(r3.tolist()) <= {0}


def test_fdb_junior_case3_injects_rfdb_as_r2_and_repairs_r3_collisions() -> None:
    order = np.arange(12, dtype=np.int64)

    _, r2, r3 = _fdb_junior_r1r2r3(order, 3, 11, 4, RandomContext(14, "twister"))

    np.testing.assert_array_equal(r2, np.full(12, 4))
    idx = np.arange(12, dtype=np.int64)
    assert not np.any(r3 == idx)
    assert not np.any(r3 == r2)
