from __future__ import annotations

import numpy as np
import pytest

from gsk_family.common.reduction import gsk_reduction_survivors


def test_gsk_reduction_survivors_keeps_best_rows_in_original_order() -> None:
    fitness = np.array([3.0, 1.0, 2.0, 5.0, 4.0])

    survivors = gsk_reduction_survivors(fitness, 2)

    np.testing.assert_array_equal(survivors, np.array([0, 1, 2]))


def test_gsk_reduction_survivors_removes_highest_original_ties_first() -> None:
    fitness = np.array([1.0, 5.0, 5.0, 2.0])

    survivors = gsk_reduction_survivors(fitness, 2)

    np.testing.assert_array_equal(survivors, np.array([0, 3]))


def test_gsk_reduction_survivors_handles_zero_and_all_removals() -> None:
    fitness = np.array([4.0, 3.0, 2.0])

    np.testing.assert_array_equal(gsk_reduction_survivors(fitness, 0), np.array([0, 1, 2]))
    np.testing.assert_array_equal(gsk_reduction_survivors(fitness, 3), np.array([], dtype=np.int64))


def test_gsk_reduction_survivors_validates_inputs() -> None:
    with pytest.raises(ValueError, match="non-negative"):
        gsk_reduction_survivors([1.0, 2.0], -1)
    with pytest.raises(ValueError, match="cannot exceed"):
        gsk_reduction_survivors([1.0, 2.0], 3)
    with pytest.raises(ValueError, match="non-finite"):
        gsk_reduction_survivors([1.0, np.nan], 1)

