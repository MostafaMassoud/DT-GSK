"""CEC2013 entry point -- unified interface for all 28 benchmark functions.

Cross-reference: ``test_func.c`` (Jane Jing Liang, 27 Jan 2013) from the
CEC'2013 Special Session and Competition on Real-Parameter Single Objective
Optimization.  Python implementation verified line-by-line against the C
reference (R package ``cec2013``).

Usage::

    from benchmarks.cec_suite_python.cec2013 import cec2013_func

    x = np.random.uniform(-100, 100, (100, 10))
    fitness = cec2013_func(x, 1)           # F1: returns (100,) array
    fitness = cec2013_func(1, x)           # same -- auto-detects argument order
    fitness = cec2013_func(x[0], 1)        # single solution -> scalar

Function structure (28 functions)::

  F1-F5:   Unimodal  (shifted, optionally rotated)
  F6-F20:  Multimodal (shifted + rotated, various transforms)
  F21-F28: Composition (distance-weighted blend of base functions)

Optimal values: f*(F_i) skips 0 in the sequence:
  F1=-1400, F2=-1300, ..., F14=-100, F15=+100, F16=+200, ..., F28=+1400

Search domain: [-100, 100]^D for all functions
Valid dimensions: {2, 5, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100}
"""

from __future__ import annotations

import numpy as np

from .composition import f21, f22, f23, f24, f25, f26, f27, f28
from .simple import (
    f1, f2, f3, f4, f5, f6, f7, f8, f9, f10,
    f11, f12, f13, f14, f15, f16, f17, f18, f19, f20,
)
from .transforms import VALID_DIMS

__all__ = [
    "all_functions",
    "cec2013_func", "cec2013_test_func",
    "cec2013_bounds", "cec2013_fname", "cec2013_fopt",
    "f1", "f2", "f3", "f4", "f5", "f6", "f7", "f8", "f9", "f10",
    "f11", "f12", "f13", "f14", "f15", "f16", "f17", "f18", "f19", "f20",
    "f21", "f22", "f23", "f24", "f25", "f26", "f27", "f28",
]

all_functions = (
    f1, f2, f3, f4, f5, f6, f7, f8, f9, f10,
    f11, f12, f13, f14, f15, f16, f17, f18, f19, f20,
    f21, f22, f23, f24, f25, f26, f27, f28,
)

_FUNCTION_NAMES = [
    "Shifted Sphere",                             # F1
    "Rotated High Conditioned Elliptic",          # F2
    "Rotated Bent Cigar",                         # F3
    "Rotated Discus",                             # F4
    "Different Powers",                           # F5
    "Rotated Rosenbrock",                         # F6
    "Rotated Schaffer's F7",                      # F7
    "Rotated Ackley",                             # F8
    "Rotated Weierstrass",                        # F9
    "Rotated Griewank",                           # F10
    "Rastrigin",                                  # F11
    "Rotated Rastrigin",                          # F12
    "Non-continuous Rotated Rastrigin",           # F13
    "Schwefel",                                   # F14
    "Rotated Schwefel",                           # F15
    "Rotated Katsuura",                           # F16
    "Lunacek Bi-Rastrigin",                       # F17
    "Rotated Lunacek Bi-Rastrigin",               # F18
    "Expanded Griewank plus Rosenbrock",          # F19
    "Expanded Scaffer's F6",                      # F20
    "Composition 1",                              # F21
    "Composition 2",                              # F22
    "Composition 3",                              # F23
    "Composition 4",                              # F24
    "Composition 5",                              # F25
    "Composition 6",                              # F26
    "Composition 7",                              # F27
    "Composition 8",                              # F28
]

# f*(F_i): -1400 + 100*(i-1), but skipping f*=0 (F15 is +100, not 0)
_FOPT = [
    -1400, -1300, -1200, -1100, -1000,           # F1-F5
    -900, -800, -700, -600, -500,                 # F6-F10
    -400, -300, -200, -100, 100,                  # F11-F15
    200, 300, 400, 500, 600,                      # F16-F20
    700, 800, 900, 1000, 1100, 1200, 1300, 1400,  # F21-F28
]


def cec2013_func(arg1: object, arg2: object = None) -> np.ndarray | float:
    """Evaluate CEC2013 benchmark function.

    Supports both argument orders:
      cec2013_func(x, func_id)  -- population matrix first
      cec2013_func(func_id, x)  -- function ID first

    Parameters
    ----------
    x : array_like
        (M, N) population matrix or (N,) single solution.
        N must be in {2, 5, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100}.
    func_id : int
        Function number 1-28.

    Returns
    -------
    f : (M,) ndarray or float
        Fitness values.  Returns scalar float for single solution input.

    Raises
    ------
    TypeError
        If fewer than 2 arguments provided.
    ValueError
        If both arguments are scalars, or if D or func_id is out of range.
    """
    if arg2 is None:
        raise TypeError("cec2013_func requires two arguments: x and func_id")

    if np.isscalar(arg1) and np.isscalar(arg2):
        raise ValueError("One argument must be a population array")

    # Auto-detect argument order.
    #
    # Audit H-1: use ``np.ascontiguousarray`` (not ``np.asarray``) on the
    # population so every downstream Numba kernel receives a C-contiguous
    # ``float64`` view.  Without this, a non-contiguous view sliced from a
    # workspace buffer would force an implicit copy on every ``@njit``
    # call — ~10_000 × D times per run on the hot path.  Matches the
    # CEC2017 dispatcher.
    if isinstance(arg1, (int, np.integer)):
        func_id, x = int(arg1), np.ascontiguousarray(arg2, dtype=np.float64)
    elif isinstance(arg2, (int, np.integer)):
        x, func_id = np.ascontiguousarray(arg1, dtype=np.float64), int(arg2)
    else:
        # Audit AUDIT-05: validate that func_id is integer-valued before
        # truncating via int().  Without this, cec2013_func(x, 1.7)
        # silently evaluates F1 instead of raising.  Matches the CEC2011
        # dispatcher guard (lines 484-489).
        x = np.ascontiguousarray(arg1, dtype=np.float64)
        func_id_raw = np.asarray(arg2).flat[0]
        func_id = int(func_id_raw)
        if func_id != float(func_id_raw):
            raise ValueError(
                f"func_id must be integer-valued, got {func_id_raw}"
            )

    # Handle 1-D input (single solution)
    scalar_input = (x.ndim == 1)
    if scalar_input:
        x = x.reshape(1, -1)

    if x.ndim != 2:
        raise ValueError(f"x must be 1-D or 2-D, got {x.ndim}-D")

    # Audit CEC2017-L1 (shared across dispatchers): reject non-finite
    # inputs at the dispatcher layer so NaN / Inf never reaches the
    # per-function Numba kernels.  A single NaN would silently poison
    # every downstream Friedman-rank, mean, and Wilcoxon aggregation.
    if not np.all(np.isfinite(x)):
        bad = int(np.sum(~np.isfinite(x)))
        raise ValueError(
            f"cec2013_func(F{func_id}): input contains {bad} non-finite "
            f"entries (NaN / +Inf / -Inf).  This would silently poison "
            f"Friedman / Wilcoxon / mean aggregation downstream -- reject "
            f"the upstream sampler instead."
        )

    N = x.shape[1]
    if N not in VALID_DIMS:
        raise ValueError(
            f"CEC2013 requires D in {sorted(VALID_DIMS)}, got D={N}"
        )
    if func_id < 1 or func_id > 28:
        raise ValueError(f"func_id must be 1-28, got {func_id}")

    f = all_functions[func_id - 1](x)

    if scalar_input:
        return float(f[0])
    return f


def cec2013_bounds(
    dim: int | None = None,
) -> tuple[np.ndarray, np.ndarray] | tuple[float, float]:
    """Return bounds (lower, upper) = (-100, 100) for all CEC2013 functions.

    Parameters
    ----------
    dim : int or None
        If provided, returns (np.ndarray, np.ndarray) of length *dim*.
        If None, returns scalar tuple (-100.0, 100.0).
    """
    if dim is not None:
        return np.full(dim, -100.0), np.full(dim, 100.0)
    return -100.0, 100.0


def cec2013_fname(func_id: int) -> str:
    """Return the name of function F{func_id}.

    Parameters
    ----------
    func_id : int
        Function number 1-28.
    """
    if func_id < 1 or func_id > 28:
        raise ValueError(f"func_id must be 1-28, got {func_id}")
    return _FUNCTION_NAMES[func_id - 1]


def cec2013_fopt(func_id: int) -> float:
    """Return optimal value f* for function F{func_id}.

    Parameters
    ----------
    func_id : int
        Function number 1-28.
    """
    if func_id < 1 or func_id > 28:
        raise ValueError(f"func_id must be 1-28, got {func_id}")
    return float(_FOPT[func_id - 1])


# Alias for compatibility
cec2013_test_func = cec2013_func
