"""CEC2017 entry point — unified interface for all 30 benchmark functions.

Usage::

    from benchmarks import cec2017_func

    x = np.random.uniform(-100, 100, (100, 10))
    fitness = cec2017_func(x, 1)           # F1: returns (100,) array
    fitness = cec2017_func(1, x)           # same — auto-detects argument order
    fitness = cec2017_func(x[0], 1)        # single solution → scalar

Function structure (30 functions):
  F1-F10:  Simple (shifted + rotated single base function)
  F11-F20: Hybrid (shift+rotate → shuffle → partition → sum)
  F21-F30: Composition (distance-weighted blend)

Optimal values: f*(F_i) = i × 100 (e.g., f*(F1) = 100, f*(F30) = 3000)
Search domain:  [-100, 100]^N for all functions

Special functions:
  F2: Sum of Different Powers — DEPRECATED, numerically unstable,
      excluded from CEC2017 competition results. Emits DeprecationWarning.

C++ quirks faithfully emulated:
  - F6 (Schaffer F7): shift-only, no rotation (C++ reads from y[] buffer)
  - F8 (Step Rastrigin): step modification lost (C++ sr_func overwrites y[])
  - F14, F20 (Schaffer F7 in hybrid): reads full shuffled buffer instead of partition

Dimensions per function type:
  F1-F10 (simple):         D ∈ {2, 10, 20, 30, 50, 100}
  F11-F19 (hybrid):        D ∈ {10, 30, 50, 100}
  F20 (hybrid 10):         D ∈ {10, 20, 30, 50, 100}
  F21-F28 (composition):   D ∈ {2, 10, 20, 30, 50, 100}
  F29-F30 (comp-hybrid):   D ∈ {10, 30, 50, 100}

Additional utilities:
  cec2017_fname(fid) → human-readable name (e.g., "Bent Cigar")
  cec2017_fopt(fid)  → optimal value (fid × 100.0)
  cec2017_bounds(dim) → (-100, 100) bounds

Aliases: cec17_func, cec2017_test_func (backward compatibility).
"""

from __future__ import annotations

import numpy as np

from .composition import f21, f22, f23, f24, f25, f26, f27, f28, f29, f30
from .hybrid import f11, f12, f13, f14, f15, f16, f17, f18, f19, f20
from .simple import f1, f2, f3, f4, f5, f6, f7, f8, f9, f10

__all__ = [
    "all_functions",
    "cec2017_func", "cec17_func", "cec2017_test_func",
    "cec2017_bounds", "cec2017_fname", "cec2017_f_name", "cec2017_fopt",
    "f1", "f2", "f3", "f4", "f5", "f6", "f7", "f8", "f9", "f10",
    "f11", "f12", "f13", "f14", "f15", "f16", "f17", "f18", "f19", "f20",
    "f21", "f22", "f23", "f24", "f25", "f26", "f27", "f28", "f29", "f30",
]

all_functions = (
    f1, f2, f3, f4, f5, f6, f7, f8, f9, f10,
    f11, f12, f13, f14, f15, f16, f17, f18, f19, f20,
    f21, f22, f23, f24, f25, f26, f27, f28, f29, f30,
)

_FP_MODES = {"default", "strict"}
_STRICT_FP_FUNCTIONS = {1, 12, 13}

# Valid dimensions per function type
_SIMPLE_COMP_DIMS = {2, 10, 20, 30, 50, 100}
_HYBRID_DIMS = {10, 20, 30, 50, 100}  # F20 supports D=20
_HYBRID_NO20_DIMS = {10, 30, 50, 100}  # F11-F19
_COMP_HYBRID_DIMS = {10, 30, 50, 100}  # F29-F30

_FUNCTION_NAMES = [
    "Bent Cigar",                          # F1
    "Sum of Different Powers (deprecated)", # F2
    "Zakharov",                            # F3
    "Rosenbrock",                          # F4
    "Rastrigin",                           # F5
    "Schaffer F7",                         # F6
    "Bi-Rastrigin (Lunacek)",              # F7
    "Step Rastrigin",                      # F8
    "Levy",                                # F9
    "Schwefel",                            # F10
    "Hybrid 1",                            # F11
    "Hybrid 2",                            # F12
    "Hybrid 3",                            # F13
    "Hybrid 4",                            # F14
    "Hybrid 5",                            # F15
    "Hybrid 6",                            # F16
    "Hybrid 7",                            # F17
    "Hybrid 8",                            # F18
    "Hybrid 9",                            # F19
    "Hybrid 10",                           # F20
    "Composition 1",                       # F21
    "Composition 2",                       # F22
    "Composition 3",                       # F23
    "Composition 4",                       # F24
    "Composition 5",                       # F25
    "Composition 6",                       # F26
    "Composition 7",                       # F27
    "Composition 8",                       # F28
    "Composition 9 (hybrid)",              # F29
    "Composition 10 (hybrid)",             # F30
]


def _validate_dim(func_id: int, N: int) -> None:
    """Check dimension validity for the given function."""
    if 1 <= func_id <= 10 or 21 <= func_id <= 28:
        valid = _SIMPLE_COMP_DIMS
    elif 11 <= func_id <= 19:
        valid = _HYBRID_NO20_DIMS
    elif func_id == 20:
        valid = _HYBRID_DIMS
    elif 29 <= func_id <= 30:
        valid = _COMP_HYBRID_DIMS
    else:
        raise ValueError(f"func_id must be 1-30, got {func_id}")

    if N not in valid:
        raise ValueError(f"F{func_id} requires D in {sorted(valid)}, got D={N}")


def cec2017_func(
    arg1: object,
    arg2: object = None,
    *,
    fp_mode: str = "default",
) -> np.ndarray | float:
    """Evaluate CEC2017 benchmark function.

    Supports both argument orders:
      cec2017_func(x, func_id)  — population matrix first
      cec2017_func(func_id, x)  — function ID first

    Parameters
    ----------
    x : array_like — (M, N) population or (N,) single solution
    func_id : int — function number 1-30

    Returns
    -------
    f : (M,) array or float (for single solution input)
    """
    mode = str(fp_mode).strip().lower()
    if mode not in _FP_MODES:
        raise ValueError(f"fp_mode must be one of {sorted(_FP_MODES)}, got {fp_mode!r}.")

    if arg2 is None:
        raise TypeError("cec2017_func requires two arguments: x and func_id")

    # Both scalars → neither is a population
    if np.isscalar(arg1) and np.isscalar(arg2):
        raise ValueError("One argument must be a population array")

    # Auto-detect argument order.  Audit PERF-LOW-1: use
    # ``np.ascontiguousarray`` here so the entire dispatcher hands a
    # C-contiguous, float64 view down to every per-function kernel.  The
    # underlying basic / hybrid / composition routines all assume a
    # contiguous (M, D) layout for their Numba kernels and rotation
    # GEMMs; without this guarantee, callers passing a non-contiguous
    # slice (e.g. ``population[start:stop, :]`` from a Fortran-ordered
    # buffer) would force every kernel to silently materialise a copy on
    # entry — once per NFE, on the hot path.  ``np.ascontiguousarray`` is
    # a free no-op when the input is already C-contiguous + float64, so
    # there is no penalty for the common harness case.
    if isinstance(arg1, (int, np.integer)):
        func_id, x = int(arg1), np.ascontiguousarray(arg2, dtype=np.float64)
    elif isinstance(arg2, (int, np.integer)):
        x, func_id = np.ascontiguousarray(arg1, dtype=np.float64), int(arg2)
    else:
        # Both arrays — assume (x, func_id) where func_id might be scalar array
        x = np.ascontiguousarray(arg1, dtype=np.float64)
        func_id = int(np.asarray(arg2).flat[0])

    # Handle 1-D input
    scalar_input = (x.ndim == 1)
    if scalar_input:
        x = x.reshape(1, -1)

    if x.ndim != 2:
        raise ValueError(f"x must be 1-D or 2-D, got {x.ndim}-D")

    # Audit CEC2017-L1: reject non-finite inputs at the dispatcher so
    # NaN / Inf never reaches the per-function Numba kernels.  A single
    # NaN would silently poison every Friedman-rank, mean, and Wilcoxon
    # sample downstream -- the Friedman critical-difference plot simply
    # collapses because NaN participates in rank propagation as a
    # non-comparable value.  Fail fast here with a clear diagnostic.
    if not np.all(np.isfinite(x)):
        bad = int(np.sum(~np.isfinite(x)))
        raise ValueError(
            f"cec2017_func(F{func_id}): input contains {bad} non-finite "
            f"entries (NaN / +Inf / -Inf).  This would silently poison "
            f"Friedman / Wilcoxon / mean aggregation downstream -- reject "
            f"the upstream sampler instead."
        )

    N = x.shape[1]
    _validate_dim(func_id, N)

    if mode == "strict" and func_id in _STRICT_FP_FUNCTIONS:
        if func_id == 1:
            f = f1(x, strict_fp=True)
        elif func_id == 12:
            f = f12(x, strict_fp=True)
        else:
            f = f13(x, strict_fp=True)
    else:
        f = all_functions[func_id - 1](x)

    if scalar_input:
        return float(f[0])
    return f


def cec2017_bounds(dim: int | None = None) -> tuple[np.ndarray, np.ndarray] | tuple[float, float]:
    """Return bounds (lower, upper) = (-100, 100) for all CEC2017 functions."""
    if dim is not None:
        return np.full(dim, -100.0), np.full(dim, 100.0)
    return -100.0, 100.0


def cec2017_fname(func_id: int) -> str:
    """Return the name of function F{func_id}."""
    if func_id < 1 or func_id > 30:
        raise ValueError(f"func_id must be 1-30, got {func_id}")
    return _FUNCTION_NAMES[func_id - 1]


# Backward-compatible alias
cec2017_f_name = cec2017_fname


def cec2017_fopt(func_id: int) -> float:
    """Return optimal value F* = func_id × 100."""
    if func_id < 1 or func_id > 30:
        raise ValueError(f"func_id must be 1-30, got {func_id}")
    return func_id * 100.0


# Aliases
cec17_func = cec2017_func
cec2017_test_func = cec2017_func
