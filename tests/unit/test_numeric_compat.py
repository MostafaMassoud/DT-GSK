from __future__ import annotations

import numpy as np
import pytest

from gsk_family.common.numeric_compat import (
    ensure_2d_population,
    compat_fix,
    compat_fix_int,
    compat_round,
    compat_round_int,
    one_based_to_zero_based,
    stable_argsort,
    stable_sort,
    zero_based_to_one_based,
)


def test_compat_round_halves_away_from_zero() -> None:
    values = np.array([-2.5, -1.5, -0.5, -0.49, 0.49, 0.5, 1.5, 2.5])

    rounded = compat_round(values)

    np.testing.assert_array_equal(rounded, np.array([-3.0, -2.0, -1.0, -0.0, 0.0, 1.0, 2.0, 3.0]))
    assert compat_round_int(2.5) == 3
    assert compat_round_int(-2.5) == -3


def test_compat_fix_rounds_toward_zero() -> None:
    values = np.array([-2.9, -1.1, 0.0, 1.1, 2.9])

    fixed = compat_fix(values)

    np.testing.assert_array_equal(fixed, np.array([-2.0, -1.0, 0.0, 1.0, 2.0]))
    assert compat_fix_int(-2.9) == -2


def test_stable_sort_and_argsort_preserve_tie_order() -> None:
    values = np.array([3.0, 1.0, 2.0, 1.0, 3.0])

    np.testing.assert_array_equal(stable_argsort(values), np.array([1, 3, 2, 0, 4]))
    np.testing.assert_array_equal(stable_argsort(values, descending=True), np.array([0, 4, 2, 1, 3]))
    np.testing.assert_array_equal(stable_sort(values), np.array([1.0, 1.0, 2.0, 3.0, 3.0]))


def test_index_conversion_helpers() -> None:
    np.testing.assert_array_equal(one_based_to_zero_based([1, 2, 5]), np.array([0, 1, 4]))
    np.testing.assert_array_equal(zero_based_to_one_based([0, 1, 4]), np.array([1, 2, 5]))
    assert one_based_to_zero_based(3) == 2
    assert zero_based_to_one_based(2) == 3

    with pytest.raises(ValueError, match=">= 1"):
        one_based_to_zero_based(0)
    with pytest.raises(ValueError, match=">= 0"):
        zero_based_to_one_based(-1)


def test_ensure_2d_population_validates_row_candidate_shape() -> None:
    pop = ensure_2d_population([[1, 2], [3, 4]], dim=2)
    assert pop.shape == (2, 2)
    assert pop.dtype == np.float64

    with pytest.raises(ValueError, match="2D"):
        ensure_2d_population([1, 2], dim=2)
    with pytest.raises(ValueError, match="at least one"):
        ensure_2d_population(np.zeros((0, 2)), dim=2)
    with pytest.raises(ValueError, match="D=3"):
        ensure_2d_population(np.zeros((1, 2)), dim=3)

