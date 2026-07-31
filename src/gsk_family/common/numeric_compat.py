"""Numeric compatibility helpers shared by optimizer kernels.

The functions in this module centralize small numeric conventions that must be
applied consistently across optimizers: half-away-from-zero rounding,
toward-zero truncation, stable ordering, population shape validation, bounds
normalization, and explicit one-based/zero-based index conversion. Keeping
those rules here prevents each optimizer from reimplementing the same policy in
slightly different ways.
"""

from __future__ import annotations

from typing import Any

import numpy as np


def compat_round(x: Any) -> np.ndarray | float:
    """Round halves away from zero for reference-compatible schedules.

    NumPy's ``round`` uses bankers rounding for halves. GSK schedules and rank
    partitions need the half-away-from-zero convention instead.
    """
    arr = np.asarray(x, dtype=np.float64)
    rounded = np.sign(arr) * np.floor(np.abs(arr) + 0.5)
    if rounded.ndim == 0:
        return float(rounded)
    return rounded


def compat_round_int(x: Any) -> np.ndarray | int:
    """Return half-away-from-zero rounded values as integers."""
    rounded = np.asarray(compat_round(x), dtype=np.int64)
    if rounded.ndim == 0:
        return int(rounded)
    return rounded


def compat_fix(x: Any) -> np.ndarray | float:
    """Round toward zero for generation-count compatibility."""
    fixed = np.trunc(np.asarray(x, dtype=np.float64))
    if fixed.ndim == 0:
        return float(fixed)
    return fixed


def compat_fix_int(x: Any) -> np.ndarray | int:
    """Return toward-zero truncated values as integers."""
    fixed = np.asarray(compat_fix(x), dtype=np.int64)
    if fixed.ndim == 0:
        return int(fixed)
    return fixed


def stable_argsort(values: Any, *, descending: bool = False) -> np.ndarray:
    """Return a stable argsort, preserving deterministic tie order."""
    arr = np.asarray(values)
    if descending:
        return np.argsort(-arr, kind="stable")
    return np.argsort(arr, kind="stable")


def stable_sort(values: Any, *, descending: bool = False) -> np.ndarray:
    """Return stable-sorted values."""
    arr = np.asarray(values)
    return arr[stable_argsort(arr, descending=descending)]


def ensure_2d_population(population: Any, *, dim: int | None = None) -> np.ndarray:
    """Normalize a population matrix while preserving row-candidate convention."""
    pop = np.ascontiguousarray(population, dtype=np.float64)
    if pop.ndim != 2:
        raise ValueError(f"Population must be 2D with rows as candidates, got {pop.ndim}D.")
    if pop.shape[0] == 0:
        raise ValueError("Population must contain at least one candidate row.")
    if dim is not None and pop.shape[1] != dim:
        raise ValueError(f"Population requires D={dim}, got D={pop.shape[1]}.")
    return pop


def as_1d_bounds(bounds: Any, *, dim: int, name: str) -> np.ndarray:
    """Return a finite 1D bounds vector of length ``dim``."""
    arr = np.asarray(bounds, dtype=np.float64)
    if arr.ndim == 0:
        arr = np.full(dim, float(arr), dtype=np.float64)
    arr = arr.reshape(-1)
    if arr.shape != (dim,):
        raise ValueError(f"{name} must have shape ({dim},), got {arr.shape}.")
    if not np.all(np.isfinite(arr)):
        raise ValueError(f"{name} contains non-finite values.")
    return arr.copy()


def one_based_to_zero_based(index: Any) -> np.ndarray | int:
    """Convert one-based reference indices to Python zero-based indices."""
    arr = np.asarray(index, dtype=np.int64) - 1
    if np.any(arr < 0):
        raise ValueError("One-based indices must be >= 1.")
    if arr.ndim == 0:
        return int(arr)
    return arr


def zero_based_to_one_based(index: Any) -> np.ndarray | int:
    """Convert Python zero-based indices to one-based reference indices."""
    arr = np.asarray(index, dtype=np.int64)
    if np.any(arr < 0):
        raise ValueError("Python indices must be >= 0.")
    converted = arr + 1
    if converted.ndim == 0:
        return int(converted)
    return converted
