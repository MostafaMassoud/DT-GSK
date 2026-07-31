from __future__ import annotations

import warnings

import numpy as np

from gsk_family.common.rng import RandomContext
from gsk_family.optimizers.atmals_helpers import (
    AtmalsProbabilityMemory,
    atmals_gaussmf,
    atmals_power_roulette_select,
    atmals_prob_update,
    atmals_roulette_select,
    atmals_senior_r1r2r3_cec2011,
    atmals_senior_r1r2r3_cec2017,
)


def test_atmals_gaussmf_matches_formula() -> None:
    x = np.array([0.0, 1.0, 2.0])

    result = atmals_gaussmf(x, 2.0, 1.0)

    np.testing.assert_allclose(result, np.exp(-((x - 1.0) ** 2) / 8.0))


def test_atmals_prob_update_preserves_oldest_row_largest_alpha_weight() -> None:
    values = np.array([1.0, 1.1, 1.2])
    old = np.ones((1, 3))
    alpha = 0.98

    p_new, p_old = atmals_prob_update(old, values, 1.0, 100.0, 90.0, alpha)

    yy = atmals_gaussmf(values, 0.05 * (np.max(values) - np.min(values)), 1.0)
    reward = yy * np.exp(0.1)
    expected = (alpha**2) * reward + alpha * np.ones(3)
    np.testing.assert_allclose(p_new, expected)
    assert p_old.shape == (2, 3)


def test_atmals_prob_update_appends_zero_reward_when_signal_ties() -> None:
    values = np.array([1.0, 1.1, 1.2])

    p_new, p_old = atmals_prob_update(np.ones((1, 3)), values, 1.0, 50.0, 50.0, 0.98)

    np.testing.assert_allclose(p_old[-1], np.zeros(3))
    np.testing.assert_allclose(p_new, 0.98 * np.ones(3))


def test_atmals_prob_update_avoids_nan_when_improvement_scale_overflows() -> None:
    values = np.arange(0.2, 0.8000001, 0.1)

    p_new, p_old = atmals_prob_update(
        np.ones((1, values.size)),
        values,
        0.5,
        1e-6,
        -1.0,
        0.98,
    )

    assert not np.any(np.isnan(p_old[-1]))
    assert not np.any(np.isnan(p_new))


def test_atmals_compact_probability_memory_matches_reference_update() -> None:
    values = np.array([0.8, 0.9, 1.0, 1.1])
    alpha = 0.98
    history = np.ones((1, values.size))
    memory = AtmalsProbabilityMemory.create(values, alpha)

    steps = [
        (1.0, 100.0, 90.0),
        (0.9, 90.0, 95.0),
        (1.1, 95.0, 95.0),
        (0.8, 95.0, 50.0),
    ]
    for value, mean_fit, mean_fit_new in steps:
        expected, history = atmals_prob_update(
            history,
            values,
            value,
            mean_fit,
            mean_fit_new,
            alpha,
        )
        actual = memory.update(value, mean_fit, mean_fit_new)
        np.testing.assert_allclose(actual, expected, rtol=1e-14, atol=1e-14)

    assert memory.row_count == history.shape[0]


def test_atmals_roulette_select_uses_cumulative_threshold() -> None:
    rng = RandomContext(6, "twister")
    expected_rng = RandomContext(6, "twister")
    draw = float(expected_rng.random())
    expected = int(np.searchsorted(np.array([0.2, 0.5, 1.0]), draw, side="left"))

    assert atmals_roulette_select(np.array([2.0, 3.0, 5.0]), rng) == expected


def test_atmals_power_roulette_select_matches_direct_power_when_finite() -> None:
    probs = np.array([2.0, 3.0, 5.0])
    rng = RandomContext(6, "twister")
    expected_rng = RandomContext(6, "twister")
    powered = probs**3.0
    cumulative = np.cumsum(powered / np.sum(powered))
    expected = int(np.searchsorted(cumulative, float(expected_rng.random()), side="left"))

    assert atmals_power_roulette_select(probs, 3.0, rng) == expected


def test_atmals_power_roulette_select_avoids_overflow() -> None:
    probs = np.array([1e200, 1e199, 1e198])
    rng = RandomContext(6, "twister")
    expected_rng = RandomContext(6, "twister")
    scaled_powered = np.array([1.0, 0.1, 0.01]) ** 3.0
    cumulative = np.cumsum(scaled_powered / np.sum(scaled_powered))
    expected = int(np.searchsorted(cumulative, float(expected_rng.random()), side="left"))

    with warnings.catch_warnings(record=True) as captured:
        warnings.simplefilter("always")
        actual = atmals_power_roulette_select(probs, 3.0, rng)

    assert captured == []
    assert actual == expected


def test_atmals_senior_partitions_are_protocol_local() -> None:
    order = np.arange(15, dtype=np.int64)

    _, _, r3_2017 = atmals_senior_r1r2r3_cec2017(order, 0.1, RandomContext(3, "twister"))
    _, _, r3_2011 = atmals_senior_r1r2r3_cec2011(order, RandomContext(3, "twister"))

    assert set(r3_2017.tolist()) <= {13, 14}
    assert set(r3_2011.tolist()) <= {14}
