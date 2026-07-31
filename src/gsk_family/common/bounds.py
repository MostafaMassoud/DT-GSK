"""Boundary repair helpers."""

from __future__ import annotations

from typing import Any

import numpy as np

from gsk_family.common.numeric_compat import as_1d_bounds, ensure_2d_population


def gsk_bound_repair(trial: Any, parent: Any, lb: Any, ub: Any) -> np.ndarray:
    """Apply midpoint bound repair from the shared reference source ``boundConstraint``.

    Coordinates below ``lb`` become ``(parent + lb) / 2`` and coordinates
    above ``ub`` become ``(parent + ub) / 2``. Coordinates exactly on a bound
    are preserved because the reference uses strict ``<`` and ``>`` checks.
    """
    trial_arr = ensure_2d_population(trial)
    parent_arr = ensure_2d_population(parent, dim=trial_arr.shape[1])
    if parent_arr.shape != trial_arr.shape:
        raise ValueError(
            "parent and trial populations must have the same shape, got "
            f"{parent_arr.shape} and {trial_arr.shape}."
        )

    lower = as_1d_bounds(lb, dim=trial_arr.shape[1], name="lb")
    upper = as_1d_bounds(ub, dim=trial_arr.shape[1], name="ub")
    if np.any(lower > upper):
        raise ValueError("Lower bounds exceed upper bounds.")

    repaired = trial_arr.copy()
    lower_violation = repaired < lower
    upper_violation = repaired > upper
    repaired[lower_violation] = ((parent_arr + lower)[lower_violation]) / 2.0
    repaired[upper_violation] = ((parent_arr + upper)[upper_violation]) / 2.0
    return repaired
