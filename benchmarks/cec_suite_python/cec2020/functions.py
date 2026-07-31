"""CEC2020 entry point — unified interface for all 10 benchmark functions.

Usage::

    from benchmarks import cec2020_func

    x = np.random.uniform(-100, 100, (100, 10))
    fitness = cec2020_func(x, 1)           # F1: returns (100,) array
    fitness = cec2020_func(1, x)           # same — auto-detects argument order
    fitness = cec2020_func(x[0], 1)        # single solution → scalar

Function structure:
  F1:    Bent Cigar (unimodal, shifted+rotated)
  F2:    Schwefel (multimodal, shifted+rotated)
  F3:    Lunacek Bi-Rastrigin (multimodal, custom shift/rotate)
  F4:    Griewank-Rosenbrock (multimodal, NO shift/rotate: s_flag=0, r_flag=0)
  F5-F7: Hybrid functions (shift+rotate → shuffle → partition → sum)
  F8-F10: Composition functions (distance-weighted blend)

Optimal values (biases):
  F1:100, F2:1100, F3:700, F4:1900, F5:1700, F6:1600,
  F7:2100, F8:2200, F9:2400, F10:2500

CEC2020-specific design differences from CEC2017:
  - Shrink rates are applied externally (not baked into basic functions)
  - Simple functions receive pre-sliced shift/rotation from this dispatcher
  - Composition functions use the cf_cal weight scheme (identical formula)
  - Fewer functions (10 vs 30) but supports more dimensions

Search domain: [-100, 100]^D for all functions.
Runner-parity dimensions: {5, 10, 15, 20}, matching the staged CEC2020
C++/MEX protocol.

Two independent reasons refuse a cell, and they must not be conflated:

* **Protocol.** F6 and F7 are undefined at D=5. Yue, Price, Suganthan et al.,
  Technical Report 201911, §2.1: "For F1-F5 and F8-F10 D = 5, 10, 15, 20; for F6
  and F7, D = 10, 15, 20." Permanent; enforced by
  ``CEC2020_PROTOCOL_EXCLUDED_CELLS`` in the adapter.
* **Validation.** F1 and F8 at D=5 and D=15 are refused because the staged
  C++/MEX protocol produced no ground truth for them — see
  ``_UNAVAILABLE_REFERENCE_CELLS`` below. The Python computes them; nothing has
  checked the result. Closable by generating the missing oracle values.

An earlier revision of this docstring blamed "missing shuffle marker files".
That was wrong: shuffle data is consumed **only** by the hybrids F5-F7
(``shuffles[D][func_id - 5]``), F1 is unimodal and F8 is a composition, and no
CEC2020 distribution ships ``shuffle_data_22`` at any dimension — verified
against the in-repo MATLAB tree and an independent third-party distribution. The
shift and rotation inputs these cells need are present and finite at every
dimension.
"""

from __future__ import annotations

import numpy as np

from .composition import f8_cf02, f9_cf04, f10_cf05
from .hybrid import f5_hf01, f6_hf06, f7_hf05
from .simple import f1_bent_cigar, f2_schwefel, f3_bi_rastrigin, f4_grie_rosen
from .transforms import (
    rotations, rotations_cf, rotations_cf_T, rotations_T, shifts, shifts_cf,
    shuffles,
)

_VALID_DIMS = {5, 10, 15, 20}
_VALID_DIMS_SIMPLE = _VALID_DIMS
_VALID_DIMS_HYBRID = _VALID_DIMS
#: EMPTY since 2026-07-26. Previously {(1,5),(1,15),(8,5),(8,15)}: those cells
#: had no C++/MEX ground truth because the official distribution ships no
#: shuffle availability-marker files for ids 1/22 at D5/D15 (the loader opens
#: one for EVERY function; only hybrids consume it). Validated against the
#: in-repo C++ oracle at worst rel 1.258e-15 vs the committed 1e-12 criterion;
#: see tests/regression/test_cec2020_restored_cells.py for the pins and the
#: full account. The AGSK paper's 5D tables always did include F1 and F8.
_UNAVAILABLE_REFERENCE_CELLS: frozenset[tuple[int, int]] = frozenset()

# Bias (f*) for each function — tuple to prevent accidental mutation
BIASES: tuple[int, ...] = (100, 1100, 700, 1900, 1700, 1600, 2100, 2200, 2400, 2500)


def cec2020_func(arg1: object, arg2: object = None) -> np.ndarray | float:
    """Evaluate CEC2020 benchmark function.

    Supports both argument orders:
      cec2020_func(x, func_id)   -- population first
      cec2020_func(func_id, x)   -- function ID first

    Parameters
    ----------
    x : ndarray, shape (M, D) or (D,) -- population of M solutions
    func_id : int -- function number, 1-10

    Returns
    -------
    f : ndarray, shape (M,) or scalar -- fitness values
    """
    if arg2 is None:
        raise TypeError("cec2020_func requires two arguments: x and func_id")

    # Both scalars → neither is a population
    if np.isscalar(arg1) and np.isscalar(arg2):
        raise ValueError("One argument must be a population array")

    # Auto-detect argument order.
    #
    # Audit H-1: use ``np.ascontiguousarray`` (not ``np.asarray``) on the
    # population so every downstream Numba kernel receives a C-contiguous
    # ``float64`` view.  Without this, a non-contiguous view sliced from a
    # workspace buffer would force an implicit copy on every ``@njit``
    # call — ~10_000 × D times per run on the hot path.  Matches the
    # CEC2017 dispatcher and the ``_ascf64`` canonical normaliser
    # documented in ``cec2020/transforms.py``.
    if isinstance(arg1, (int, np.integer)):
        func_id, x = int(arg1), np.ascontiguousarray(arg2, dtype=np.float64)
    elif isinstance(arg2, (int, np.integer)):
        x, func_id = np.ascontiguousarray(arg1, dtype=np.float64), int(arg2)
    else:
        # Both arrays — assume (x, func_id) where func_id might be array-like
        x = np.ascontiguousarray(arg1, dtype=np.float64)
        func_id = int(np.asarray(arg2).flat[0])

    if func_id < 1 or func_id > 10:
        raise ValueError(f"func_id must be 1-10, got {func_id}")

    single = x.ndim == 1
    if single:
        x = x[None, :]
    if x.ndim != 2:
        raise ValueError(f"x must be 1-D or 2-D, got {x.ndim}-D")

    M, D = x.shape

    # Reject empty populations rather than silently returning ``np.empty(0)``
    # -- the optimizer never asks for zero evaluations, so a (0, D) input is
    # always a programming error and should fail loudly.
    if M == 0:
        raise ValueError(
            "cec2020_func received an empty population (M=0); "
            "the dispatcher requires at least one row in x."
        )
    if D == 0:
        raise ValueError(
            "cec2020_func received zero-dimensional input (D=0); "
            "the dispatcher requires at least one column in x."
        )

    # Audit CEC2017-L1 (shared across dispatchers): reject non-finite
    # inputs before they reach any per-function Numba kernel.  A single
    # NaN would silently poison every downstream Friedman-rank, mean,
    # and Wilcoxon aggregation.
    if not np.all(np.isfinite(x)):
        bad = int(np.sum(~np.isfinite(x)))
        raise ValueError(
            f"cec2020_func(F{func_id}): input contains {bad} non-finite "
            f"entries (NaN / +Inf / -Inf).  This would silently poison "
            f"Friedman / Wilcoxon / mean aggregation downstream -- reject "
            f"the upstream sampler instead."
        )

    if func_id in (5, 6, 7):
        if D not in _VALID_DIMS_HYBRID:
            raise ValueError(f"F{func_id} requires D in {sorted(_VALID_DIMS_HYBRID)}, got D={D}")
    else:
        if D not in _VALID_DIMS:
            raise ValueError(f"F{func_id} requires D in {sorted(_VALID_DIMS)}, got D={D}")
    if (func_id, D) in _UNAVAILABLE_REFERENCE_CELLS:
        raise ValueError(
            f"CEC2020 F{func_id} D={D} is unavailable in the reference data "
            "distribution; the staged C++/MEX protocol has no ground truth "
            "for this cell."
        )

    if func_id <= 4:
        # Simple functions: F1-F4 (bias included in each function)
        idx = func_id - 1
        Os = shifts[idx, :D]
        Mr = rotations[D][idx, :D, :D]
        Mr_T = rotations_T[D][idx, :D, :D]

        if func_id == 1:
            f = f1_bent_cigar(x, Os, Mr, Mr_T=Mr_T)
        elif func_id == 2:
            f = f2_schwefel(x, Os, Mr, Mr_T=Mr_T)
        elif func_id == 3:
            f = f3_bi_rastrigin(x, Os, Mr, Mr_T=Mr_T)
        else:
            f = f4_grie_rosen(x, Os, Mr, Mr_T=Mr_T)

    elif func_id <= 7:
        # Hybrid functions: F5-F7 (bias included in each function)
        idx = func_id - 1
        Os = shifts[idx, :D]
        Mr = rotations[D][idx, :D, :D]
        Mr_T = rotations_T[D][idx, :D, :D]
        SS = shuffles[D][func_id - 5]

        if func_id == 5:
            f = f5_hf01(x, Os, Mr, SS, Mr_T=Mr_T)
        elif func_id == 6:
            f = f6_hf06(x, Os, Mr, SS, Mr_T=Mr_T)
        else:
            f = f7_hf05(x, Os, Mr, SS, Mr_T=Mr_T)

    else:
        # Composition functions: F8-F10 (bias included in each function)
        cf_idx = func_id - 8
        Os_cf = shifts_cf[cf_idx, :, :D]
        Mr_cf = rotations_cf[D][cf_idx]
        Mr_cf_T = rotations_cf_T[D][cf_idx]

        if func_id == 8:
            f = f8_cf02(x, Os_cf, Mr_cf, D, Mr_cf_T=Mr_cf_T)
        elif func_id == 9:
            f = f9_cf04(x, Os_cf, Mr_cf, D, Mr_cf_T=Mr_cf_T)
        else:
            f = f10_cf05(x, Os_cf, Mr_cf, D, Mr_cf_T=Mr_cf_T)

    return float(f[0]) if single else f


# Aliases
cec20_func = cec2020_func
cec2020_test_func = cec2020_func


def cec2020_bounds(dim: int | None = None) -> tuple[np.ndarray, np.ndarray] | tuple[float, float]:
    """Return bounds (-100, 100) for all CEC2020 functions."""
    if dim is not None:
        return np.full(dim, -100.0), np.full(dim, 100.0)
    return -100.0, 100.0


def cec2020_fopt(func_id: int) -> float:
    """Return optimal value f* for function func_id (1-10)."""
    if func_id < 1 or func_id > 10:
        raise ValueError(f"func_id must be 1-10, got {func_id}")
    return float(BIASES[func_id - 1])


_FUNCTION_NAMES = [
    "Bent Cigar",                  # F1
    "Schwefel",                    # F2
    "Lunacek Bi-Rastrigin",        # F3
    "Griewank-Rosenbrock",         # F4
    "Hybrid 1 (hf01)",             # F5
    "Hybrid 6 (hf06)",             # F6
    "Hybrid 5 (hf05)",             # F7
    "Composition 2 (cf02)",        # F8
    "Composition 4 (cf04)",        # F9
    "Composition 5 (cf05)",        # F10
]


def cec2020_fname(func_id: int) -> str:
    """Return the name of function F{func_id}."""
    if func_id < 1 or func_id > 10:
        raise ValueError(f"func_id must be 1-10, got {func_id}")
    return _FUNCTION_NAMES[func_id - 1]
