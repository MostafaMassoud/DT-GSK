from __future__ import annotations

import numpy as np

from gsk_family.common.reduction import gsk_reduction_survivors
from gsk_family.optimizers.agsk import (
    _improvement_credit,
    _reduce_population_after_generation,
    _select_parameter_slots,
    _target_population_size,
)


class _FixedDraws:
    """Small deterministic RNG stub for slot-selection boundary tests."""

    def __init__(self, draws: np.ndarray) -> None:
        self.draws = np.asarray(draws, dtype=np.float64)

    def random(self, size: int) -> np.ndarray:
        assert int(size) == self.draws.size
        return self.draws.copy()


def test_agsk_improvement_credit_matches_reference_floor_rule() -> None:
    parent = np.array([40.0, 20.0, 50.0, 25.0, 10.0, 30.0])
    child = np.array([35.0, 18.0, 51.0, 20.0, 10.0, 27.0])
    slots = np.array([0, 0, 1, 2, 2, 3])

    credit = _improvement_credit(parent, child, slots)

    np.testing.assert_allclose(
        credit,
        np.array([0.4166666667, 0.05, 0.3333333333, 0.2]),
        rtol=0.0,
        atol=1e-10,
    )
    assert float(np.sum(credit)) == 1.0


def test_agsk_parameter_slots_preserve_reference_boundaries() -> None:
    draws = np.array([0.0, 0.05, 0.85, 0.90, 0.95, 1.0, 1.1])
    slots = _select_parameter_slots(
        _FixedDraws(draws),  # type: ignore[arg-type]
        draws.size,
        np.array([0.85, 0.05, 0.05, 0.05]),
    )

    np.testing.assert_array_equal(slots, np.array([0, 0, 0, 1, 2, 3, 3]))


def test_agsk_improvement_credit_is_uniform_when_no_child_improves() -> None:
    parent = np.array([1.0, 2.0, 3.0, 4.0])
    child = np.array([1.0, 3.0, 5.0, 4.0])
    slots = np.array([0, 1, 2, 3])

    np.testing.assert_array_equal(
        _improvement_credit(parent, child, slots),
        np.full(4, 0.25),
    )


def test_agsk_population_plan_uses_compat_rounding() -> None:
    assert _target_population_size(0, 100, 20, 12) == 20
    assert _target_population_size(100, 100, 20, 12) == 12


def test_agsk_reduction_trims_population_and_k_in_survivor_order() -> None:
    popold = np.arange(16 * 2, dtype=float).reshape(16, 2)
    pop = popold + 100.0
    fitness = np.array(
        [5.0, 1.0, 1.0, 9.0, 3.0, 9.0, 2.0, 4.0, 8.0, 6.0, 7.0, 0.0, 2.0, 8.0, 10.0, 3.0]
    )
    k_vec = np.arange(16, dtype=float) + 0.5

    new_pop, new_fitness, new_k, new_size, survivors = (
        _reduce_population_after_generation(
            pop,
            fitness,
            k_vec,
            pop_size=16,
            max_pop_size=16,
            min_pop_size=12,
            nfes=100,
            max_nfes=100,
        )
    )

    expected = gsk_reduction_survivors(fitness, 4)
    assert new_size == 12
    np.testing.assert_array_equal(survivors, expected)
    np.testing.assert_array_equal(new_pop, pop[expected, :])
    np.testing.assert_array_equal(new_fitness, fitness[expected])
    np.testing.assert_array_equal(new_k, k_vec[expected])

    # W1.4: non-reducing call returns the SAME arrays and survivors=None
    same = _reduce_population_after_generation(
        new_pop, new_fitness, new_k,
        pop_size=12, max_pop_size=16, min_pop_size=12, nfes=0, max_nfes=100,
    )
    assert same[0] is new_pop and same[3] == 12 and same[4] is None
