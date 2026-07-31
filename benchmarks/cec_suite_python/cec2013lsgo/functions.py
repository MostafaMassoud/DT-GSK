"""CEC2013LSGO entry point — unified interface for all 15 benchmark functions.

Usage::

    from benchmarks.cec_suite_python.cec2013lsgo import cec2013lsgo_func

    x = np.random.uniform(-100, 100, (50, 1000))
    fitness = cec2013lsgo_func(x, 1)          # F1: returns (50,) array
    fitness = cec2013lsgo_func(1, x)          # same — auto-detects argument order
    fitness = cec2013lsgo_func(x[0], 1)       # single solution → scalar

Function structure (15 functions)::

  F1-F3:    Fully separable (Elliptic, Rastrigin, Ackley)           D=1000
  F4-F7:    Partially separable, 7 groups + separable remainder     D=1000
  F8-F11:   Partially separable, 20 groups, no remainder            D=1000
  F12:      Fully non-separable (Rosenbrock)                        D=1000
  F13-F14:  Overlapping groups (conforming / conflicting)           D=905
  F15:      Fully non-separable (Schwefel 1.2)                      D=1000

Optimal value: f* = 0 for all functions, **except F12 (Shifted Rosenbrock)
where f(xopt) = N - 1 = 999** -- Rosenbrock's minimum is at z = 1
(all-ones), not z = 0.  See ``cec2013lsgo_fopt`` and
``composite._assert_f12_baseline`` (audit C-01 lsgo).
Search domain: varies per function (see :func:`cec2013lsgo_bounds`).
Dimension: D=1000 for F1-F12/F15; D=905 for F13-F14 (20 groups, overlap=5).

Provenance of numerical data (audit L-1 lsgo)
---------------------------------------------
The CEC2013LSGO suite is assembled from **two different reference
sources**, and the choice is documented by
:data:`CEC2013LSGO_BOUNDS_PROVENANCE` below:

* **Shift / permutation / rotation / group-size / weight data**
  (``data.pkl``) is built via :mod:`.make_data_pkl` from the C++
  reference ``cdatafiles/*.txt`` (75 raw files → 1.25 MB blob).  The
  pickle is SHA-256-verified at import time in
  :mod:`.transforms`.

* **Search-domain bounds** (:data:`_BOUNDS` below) follow the CEC2013
  LSGO technical report, *not* the C++ reference, for F9/F10/F11.
  The C++ reference ships bounds that were cross-pasted between these
  three functions (a well-known upstream bug), so using it would
  produce a domain that no published LSGO result was measured on.
  F1-F8/F12-F15 happen to agree between the two sources, so this
  divergence only matters for three functions.

If you port new CEC2013LSGO baselines from a paper, make sure they
were measured with the tech-report bounds -- otherwise the reported
fitness is not comparable to this suite.  See the inline annotations
at ``_BOUNDS[9/10/11]`` for the exact C++-reference bounds that
would be produced by the "wrong" path.
"""

from __future__ import annotations

import numpy as np

from .composite import (
    f1, f2, f3, f4, f5, f6, f7, f8, f9, f10,
    f11, f12, f13, f14, f15,
)
from .transforms import DIMENSION, DIMENSION_OVERLAP

__all__ = [
    "NUM_FUNCTIONS",
    "CEC2013LSGO_BOUNDS_PROVENANCE",
    "all_functions",
    "cec2013lsgo_func", "cec2013lsgo_test_func",
    "cec2013lsgo_bounds", "cec2013lsgo_fopt", "cec2013lsgo_fname",
    "cec2013lsgo_dim",
    "f1", "f2", "f3", "f4", "f5", "f6", "f7", "f8", "f9", "f10",
    "f11", "f12", "f13", "f14", "f15",
]

NUM_FUNCTIONS = 15

all_functions = (
    f1, f2, f3, f4, f5, f6, f7, f8, f9, f10,
    f11, f12, f13, f14, f15,
)

_FUNCTION_NAMES = [
    "Shifted Elliptic",                                          # F1
    "Shifted Rastrigin",                                         # F2
    "Shifted Ackley",                                            # F3
    "7-group Shifted+Rotated Elliptic with Sep Elliptic",        # F4
    "7-group Shifted+Rotated Rastrigin with Sep Rastrigin",      # F5
    "7-group Shifted+Rotated Ackley with Sep Ackley",            # F6
    "7-group Shifted+Rotated Schwefel with Sep Sphere",          # F7
    "20-group Shifted+Rotated Elliptic",                         # F8
    "20-group Shifted+Rotated Rastrigin",                        # F9
    "20-group Shifted+Rotated Ackley",                           # F10
    "20-group Shifted+Rotated Schwefel",                         # F11
    "Shifted Rosenbrock",                                        # F12
    "Overlapping Shifted+Rotated Schwefel (Conforming)",         # F13
    "Overlapping Shifted+Rotated Schwefel (Conflicting)",        # F14
    "Shifted Schwefel 1.2",                                      # F15
]

# ---------------------------------------------------------------------------
# Search-domain bounds (provenance: CEC2013 LSGO tech report)
# ---------------------------------------------------------------------------
# Audit L-1 lsgo: make the "where did these bounds come from?" answer
# first-class.  The suite uses the CEC2013 LSGO tech-report bounds
# everywhere, NOT the C++ reference.  They agree on 12 of 15 functions,
# but F9/F10/F11 are cross-pasted in the C++ ref and we intentionally
# diverge (see module docstring and the per-entry annotations below).
CEC2013LSGO_BOUNDS_PROVENANCE: str = "cec2013_lsgo_tech_report"

# Bounds per function: (lower, upper)
_BOUNDS = {
    1: (-100.0, 100.0),
    2: (-5.0, 5.0),
    3: (-32.0, 32.0),
    4: (-100.0, 100.0),
    5: (-5.0, 5.0),
    6: (-32.0, 32.0),
    7: (-100.0, 100.0),
    8: (-100.0, 100.0),
    9: (-5.0, 5.0),       # tech report: [-5,5]; C++ ref has bug ([-100,100])
    10: (-32.0, 32.0),    # tech report: [-32,32]; C++ ref has bug ([-5,5])
    11: (-100.0, 100.0),  # tech report: [-100,100]; C++ ref has bug ([-32,32])
    12: (-100.0, 100.0),
    13: (-100.0, 100.0),
    14: (-100.0, 100.0),
    15: (-100.0, 100.0),
}


def cec2013lsgo_func(arg1: object, arg2: object = None) -> np.ndarray | float:
    """Evaluate CEC2013LSGO benchmark function.

    Supports both argument orders:
      cec2013lsgo_func(x, func_id)  — population matrix first
      cec2013lsgo_func(func_id, x)  — function ID first

    Parameters
    ----------
    x : array_like — (M, D) population or (D,) single solution
    func_id : int — function number 1-15

    Returns
    -------
    f : (M,) array or float (for single solution input)
    """
    if arg2 is None:
        raise TypeError("cec2013lsgo_func requires two arguments: x and func_id")

    if np.isscalar(arg1) and np.isscalar(arg2):
        raise ValueError("One argument must be a population array")

    # Auto-detect argument order.
    #
    # Audit H-1: use ``np.ascontiguousarray`` (not ``np.asarray``) on the
    # population so every downstream Numba kernel receives a C-contiguous
    # ``float64`` view.  Without this, a non-contiguous view sliced from a
    # workspace buffer would force an implicit copy on every ``@njit``
    # call — the LSGO hot path runs at D=1000 where the copy cost is
    # measurable.  Matches the CEC2017 dispatcher.
    if isinstance(arg1, (int, np.integer)):
        func_id, x = int(arg1), np.ascontiguousarray(arg2, dtype=np.float64)
    elif isinstance(arg2, (int, np.integer)):
        x, func_id = np.ascontiguousarray(arg1, dtype=np.float64), int(arg2)
    else:
        # Fallback: both are array-like — treat arg2 as func_id.
        # Validate that it looks like an integer to catch misuse early.
        a2 = np.asarray(arg2)
        fid_val = float(a2.flat[0])
        if fid_val != int(fid_val):
            raise ValueError(
                f"func_id must be an integer, got {fid_val}. "
                "Pass func_id as int, not float."
            )
        x = np.ascontiguousarray(arg1, dtype=np.float64)
        func_id = int(fid_val)

    # Handle 1-D input
    scalar_input = (x.ndim == 1)
    if scalar_input:
        x = x.reshape(1, -1)

    if x.ndim != 2:
        raise ValueError(f"x must be 1-D or 2-D, got {x.ndim}-D")

    # Audit CEC2017-L1 (shared across dispatchers): reject non-finite
    # inputs before they reach any per-function Numba kernel.  A single
    # NaN would silently poison every downstream Friedman-rank, mean,
    # and Wilcoxon aggregation.  At D=1000 this check costs ~1 us per
    # individual -- negligible on top of the ~50 us LSGO hot-path.
    if not np.all(np.isfinite(x)):
        bad = int(np.sum(~np.isfinite(x)))
        raise ValueError(
            f"cec2013lsgo_func(F{func_id}): input contains {bad} non-finite "
            f"entries (NaN / +Inf / -Inf).  This would silently poison "
            f"Friedman / Wilcoxon / mean aggregation downstream -- reject "
            f"the upstream sampler instead."
        )

    if func_id < 1 or func_id > NUM_FUNCTIONS:
        raise ValueError(f"func_id must be 1-{NUM_FUNCTIONS}, got {func_id}")

    expected_dim = cec2013lsgo_dim(func_id)
    N = x.shape[1]
    if N != expected_dim:
        raise ValueError(
            f"CEC2013LSGO F{func_id} requires D={expected_dim}, got D={N}"
        )

    f = all_functions[func_id - 1](x)

    if scalar_input:
        return float(f[0])
    return f


def cec2013lsgo_dim(func_id: int) -> int:
    """Return the dimensionality for function F{func_id}.

    F13 and F14 (overlapping groups) have D=905; all others have D=1000.
    """
    if func_id < 1 or func_id > NUM_FUNCTIONS:
        raise ValueError(f"func_id must be 1-{NUM_FUNCTIONS}, got {func_id}")
    return DIMENSION_OVERLAP if func_id in (13, 14) else DIMENSION


def cec2013lsgo_bounds(
    func_id: int, dim: int | None = None,
) -> tuple[np.ndarray, np.ndarray] | tuple[float, float]:
    """Return bounds (lower, upper) for function *func_id*.

    Parameters
    ----------
    func_id : int — function number 1-15.
    dim : int, optional — if given, return (dim,) arrays.
    """
    if func_id < 1 or func_id > NUM_FUNCTIONS:
        raise ValueError(f"func_id must be 1-{NUM_FUNCTIONS}, got {func_id}")
    lo, hi = _BOUNDS[func_id]
    if dim is not None:
        return np.full(dim, lo), np.full(dim, hi)
    return lo, hi


def cec2013lsgo_fname(func_id: int) -> str:
    """Return the name of function F{func_id}."""
    if func_id < 1 or func_id > NUM_FUNCTIONS:
        raise ValueError(f"func_id must be 1-{NUM_FUNCTIONS}, got {func_id}")
    return _FUNCTION_NAMES[func_id - 1]


def cec2013lsgo_fopt(func_id: int) -> float:
    """Return optimal value f* for function F{func_id}.

    All functions have ``f* = 0`` **except F12** (Shifted Rosenbrock) where
    ``f(xopt) = N - 1 = 999``.  Rosenbrock's minimum is at z = 1 (all-ones),
    not z = 0, so the shifted-and-translated F12 sits at 999, not 0.  This
    is enforced at module-import time by ``composite._assert_f12_baseline``
    (audit C-01 lsgo) and the module docstring.
    """
    if func_id < 1 or func_id > NUM_FUNCTIONS:
        raise ValueError(f"func_id must be 1-{NUM_FUNCTIONS}, got {func_id}")
    if func_id == 12:
        return 999.0
    return 0.0


# Alias
cec2013lsgo_test_func = cec2013lsgo_func
