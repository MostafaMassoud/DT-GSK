from __future__ import annotations

import numpy as np
import pytest

from gsk_family.common.bounds import gsk_bound_repair


def test_gsk_bound_repair_uses_midpoints_for_strict_violations() -> None:
    lb = np.array([-5.0, -5.0])
    ub = np.array([5.0, 5.0])
    parent = np.array([[0.0, 0.0], [4.0, -4.0]])
    trial = np.array([[-7.0, 3.0], [12.0, -20.0]])

    repaired = gsk_bound_repair(trial, parent, lb, ub)

    expected = np.array([[-2.5, 3.0], [4.5, -4.5]])
    np.testing.assert_allclose(repaired, expected)


def test_gsk_bound_repair_preserves_on_bound_values_and_inputs() -> None:
    lb = np.array([-5.0, -5.0])
    ub = np.array([5.0, 5.0])
    parent = np.array([[0.0, 0.0], [4.0, -4.0]])
    trial = np.array([[-5.0, 5.0], [5.0, -5.0]])
    trial_before = trial.copy()
    parent_before = parent.copy()

    repaired = gsk_bound_repair(trial, parent, lb, ub)

    np.testing.assert_allclose(repaired, trial_before)
    np.testing.assert_allclose(trial, trial_before)
    np.testing.assert_allclose(parent, parent_before)


def test_gsk_bound_repair_broadcasts_vector_bounds() -> None:
    parent = np.array([[2.0, -2.0, 0.0]])
    trial = np.array([[10.0, -10.0, 0.25]])

    repaired = gsk_bound_repair(trial, parent, [-1.0, -3.0, 0.0], [5.0, 4.0, 1.0])

    np.testing.assert_allclose(repaired, np.array([[3.5, -2.5, 0.25]]))


def test_gsk_bound_repair_validates_shapes_and_bounds() -> None:
    with pytest.raises(ValueError, match="same shape"):
        gsk_bound_repair(np.zeros((2, 2)), np.zeros((1, 2)), [-1, -1], [1, 1])
    with pytest.raises(ValueError, match="Lower bounds"):
        gsk_bound_repair(np.zeros((1, 2)), np.zeros((1, 2)), [2, -1], [1, 1])
