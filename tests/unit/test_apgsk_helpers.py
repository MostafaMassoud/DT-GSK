from __future__ import annotations

import numpy as np

from gsk_family.optimizers.apgsk import (
    KF_POOL,
    KF_POOL_NEGATIVE,
    _apgsk_kf_values,
    _stochastic_junior_dimension,
)


def test_apgsk_uses_positive_kf_pool_in_initial_phase() -> None:
    slots = np.array([0, 1, 2, 3])

    values, used_negative = _apgsk_kf_values(
        slots,
        adaptive_phase=False,
        adaptive_pool_draw=None,
        nfes=10,
        max_nfes=100,
    )

    assert used_negative is False
    np.testing.assert_array_equal(values, KF_POOL)


def test_apgsk_negative_kf_pool_requires_adaptive_rule_to_fail() -> None:
    slots = np.array([0, 1, 2, 3])

    values, used_negative = _apgsk_kf_values(
        slots,
        adaptive_phase=True,
        adaptive_pool_draw=0.2,
        nfes=60,
        max_nfes=100,
    )

    assert used_negative is True
    np.testing.assert_array_equal(values, KF_POOL_NEGATIVE)


def test_apgsk_positive_kf_pool_requires_draw_and_budget_progress() -> None:
    slots = np.array([0, 1, 2, 3])

    values, used_negative = _apgsk_kf_values(
        slots,
        adaptive_phase=True,
        adaptive_pool_draw=0.4,
        nfes=60,
        max_nfes=100,
    )

    assert used_negative is False
    np.testing.assert_array_equal(values, KF_POOL)

    values, used_negative = _apgsk_kf_values(
        slots,
        adaptive_phase=True,
        adaptive_pool_draw=0.4,
        nfes=40,
        max_nfes=100,
    )

    assert used_negative is True
    np.testing.assert_array_equal(values, KF_POOL_NEGATIVE)


def test_apgsk_stochastic_junior_dimension_uses_compat_rounding() -> None:
    assert _stochastic_junior_dimension(10, 64, 100, 0.7) == 6
    assert _stochastic_junior_dimension(10, 64, 100, 0.1) == 1
    assert _stochastic_junior_dimension(5, 50, 100, 0.6) == 4
    assert _stochastic_junior_dimension(5, 50, 100, 0.4) == 1
