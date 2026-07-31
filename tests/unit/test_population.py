from __future__ import annotations

import numpy as np
import pytest

from gsk_family.common.population import (
    gsk_init_population,
    gsk_initial_population_from_options,
    gsk_restore_rng_after_initialization,
    infer_dimension,
)
from gsk_family.common.rng import RandomContext, create_fair_start
from gsk_family.types import OptimizerOptions


def test_gsk_init_population_uses_one_population_sized_draw() -> None:
    rng = RandomContext(11, "twister")
    manual = RandomContext(11, "twister")
    lb = np.array([-3.0, 2.0])
    ub = np.array([7.0, 6.0])

    pop = gsk_init_population(rng, 4, lb, ub)
    expected = lb + np.asarray(manual.random((4, 2))) * (ub - lb)

    np.testing.assert_allclose(pop, expected)
    np.testing.assert_allclose(rng.random(5), manual.random(5))
    assert pop.shape == (4, 2)
    assert np.all(pop >= lb)
    assert np.all(pop <= ub)


def test_gsk_initial_population_from_options_uses_prefix_copy() -> None:
    rng = RandomContext(7, "twister")
    x0 = np.arange(20.0).reshape(5, 4)
    options = {"initial_population": x0}

    pop = gsk_initial_population_from_options(options, rng, 3, -3.0, 7.0, dim=4)

    np.testing.assert_allclose(pop, x0[:3, :])
    pop[0, 0] = -999.0
    assert x0[0, 0] == 0.0


def test_gsk_initial_population_from_options_draws_when_x0_missing() -> None:
    rng = RandomContext(8, "twister")
    manual = RandomContext(8, "twister")
    options = OptimizerOptions(seed=8)

    pop = gsk_initial_population_from_options(options, rng, 2, [-1.0, -2.0], [1.0, 2.0])
    expected = np.array([-1.0, -2.0]) + np.asarray(manual.random((2, 2))) * np.array([2.0, 4.0])

    np.testing.assert_allclose(pop, expected)
    np.testing.assert_allclose(rng.random(3), manual.random(3))


def test_gsk_restore_rng_after_initialization_requires_matching_x0() -> None:
    fair = create_fair_start(101, "twister", 5, 4, -3.0, 7.0)
    options = OptimizerOptions(
        seed=101,
        initial_population=fair.initial_population,
        rng_state_after_initialization=fair.rng_state_after_initialization,
    )
    rng = RandomContext(101, "twister")
    comparison = RandomContext(101, "twister")
    comparison.restore_state(fair.rng_state_after_initialization)

    pop = gsk_initial_population_from_options(options, rng, 3, -3.0, 7.0, dim=4)
    gsk_restore_rng_after_initialization(options, rng)

    np.testing.assert_allclose(pop, fair.initial_population[:3, :])
    np.testing.assert_allclose(rng.random(6), comparison.random(6))

    no_x0_rng = RandomContext(101, "twister")
    no_x0_options = OptimizerOptions(
        seed=101,
        rng_state_after_initialization=fair.rng_state_after_initialization,
    )
    gsk_restore_rng_after_initialization(no_x0_options, no_x0_rng)
    baseline = RandomContext(101, "twister")
    np.testing.assert_allclose(no_x0_rng.random(4), baseline.random(4))


def test_gsk_initial_population_from_options_validates_shape() -> None:
    rng = RandomContext(1, "twister")
    with pytest.raises(ValueError, match="at least 4 rows"):
        gsk_initial_population_from_options({"initial_population": np.zeros((3, 2))}, rng, 4, -1, 1, dim=2)
    with pytest.raises(ValueError, match="D=3"):
        gsk_initial_population_from_options({"initial_population": np.zeros((4, 2))}, rng, 4, -1, 1, dim=3)


def test_infer_dimension_rejects_inconsistent_inputs() -> None:
    with pytest.raises(ValueError, match="Inconsistent"):
        infer_dimension([0.0, 0.0], [1.0, 1.0, 1.0])

