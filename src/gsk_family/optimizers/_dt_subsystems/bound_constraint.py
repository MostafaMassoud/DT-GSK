"""
Boundary Constraint Handling — L-SHADE Midpoint Repair
=======================================================

Repairs solutions that violate search bounds [-100, 100] using the
midpoint method from L-SHADE: x_repaired = (x_parent + x_bound) / 2.

This preserves the search direction while keeping solutions feasible.
Applied after every mutation step in both GSK and DT-GSK.

When numba is available, uses a JIT-compiled kernel (zero temp allocations).
Falls back to the numpy implementation otherwise.
"""

from __future__ import annotations

import numpy as np

# Try to import the numba-accelerated kernel
try:
    from ._numba_accel import bound_constraint_fast as _fast
except ImportError:
    _fast = None


def bound_constraint(
    vi: np.ndarray,
    pop: np.ndarray,
    lu: np.ndarray,
) -> None:
    """
    Repair out-of-bounds solutions using L-SHADE midpoint method.

    Modifies vi IN-PLACE.

    Parameters
    ----------
    vi : np.ndarray, shape (pop_size, dim)
        Mutant vectors to repair. Modified in-place.
    pop : np.ndarray, shape (pop_size, dim)
        Parent vectors (must already be feasible).
    lu : np.ndarray, shape (2, dim)
        Bounds: lu[0] = lower bounds, lu[1] = upper bounds.
    """
    if _fast is not None:
        _fast(vi, pop, lu)
        return

    # Audit PERF-MED-2: NumPy fallback rewritten to avoid the inline
    # ``np.broadcast_to(...)[mask]`` pattern.  ``np.where`` returns the
    # row / column indices of every violating cell, which lets us index
    # the (D,) bound vectors directly with ``cols`` and the (NP, D)
    # parent matrix with ``(rows, cols)``.  Both forms are correct, but
    # this one (a) avoids materialising the (NP, D) ``broadcast_to``
    # *view* twice (once for the lower repair, once for upper) and (b)
    # makes the shape contract obvious to a reader: ``lower[cols]`` and
    # ``pop[rows, cols]`` are both 1-D arrays of equal length, so the
    # midpoint formula is unambiguous.  This path is only exercised when
    # Numba is unavailable; the JIT kernel above remains the hot path.
    lower = lu[0]  # shape (D,)
    upper = lu[1]  # shape (D,)

    lower_violation = vi < lower
    if lower_violation.any():
        rows, cols = np.where(lower_violation)
        vi[rows, cols] = 0.5 * (pop[rows, cols] + lower[cols])

    upper_violation = vi > upper
    if upper_violation.any():
        rows, cols = np.where(upper_violation)
        vi[rows, cols] = 0.5 * (pop[rows, cols] + upper[cols])
