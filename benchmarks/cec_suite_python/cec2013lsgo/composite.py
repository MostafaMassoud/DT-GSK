"""CEC2013LSGO function implementations F1-F15.

Five evaluation categories, matching the C++ reference (Benchmarks.cpp)::

  F1-F3    Fully separable — shift + base function (no rotation)
  F4-F7    7 rotated groups + 700-dim separable remainder
  F8-F11   20 rotated groups, no separable remainder
  F12, F15 Fully non-separable — shift + base function on all 1000 dims
  F13-F14  20 overlapping groups (overlap=5, D=905)

All functions accept ``(M, D)`` → ``(M,)``.
Optimal value ``f* = 0`` for all functions.

Performance strategy
--------------------
**Full-D functions (F1-F3 / F12 / F15):**
    Fused ``shift+transform+evaluate`` Numba kernels eliminate the
    ``M×1000`` intermediate allocation entirely.

**Group functions (F4-F14):**
    When Numba is available, fused group kernels process *all* groups in
    a single ``@njit(parallel=True)`` call — no Python loop, no per-group
    fancy indexing, no per-group BLAS dispatch.  The ``prange(M)`` outer
    loop parallelises across solutions; the inner loop over groups is
    sequential per solution (cache-friendly access pattern).

    Fallback (no Numba): Python loop over groups with BLAS matmul.

**Separable remainder (F4-F7 only):**
    Dedicated fused ``sep_*_nb`` kernels read the 700-dim remainder
    directly from the population matrix via column indices — no
    ``M×700`` temporary allocation, no Python-level fancy indexing.
    Delivers 1.8-3.2× speedup over the previous approach of
    gathering ``x[:, sep_indices] - xopt_sep`` into a temporary
    and dispatching to the base function's fused kernel.

    Fallback (no Numba): Python-level gather + base function call.
"""

from __future__ import annotations

import numpy as np

from .basic import ackley, ackley_raw, elliptic, rastrigin, rosenbrock, schwefel_1_2, sphere
from .transforms import (
    OVERLAP,
    _ensure_f64,
    load_group_flat,
    load_group_info,
    load_xopt,
)

__all__ = [
    "f1", "f2", "f3", "f4", "f5", "f6", "f7", "f8", "f9", "f10",
    "f11", "f12", "f13", "f14", "f15",
]

# ---------------------------------------------------------------------------
# Numba kernel imports (graceful fallback)
# ---------------------------------------------------------------------------
try:
    from ._numba import (
        # Shifted full-D kernels (F1-F3 / F12 / F15)
        shifted_osz_asy_lam_ackley_nb as _shifted_ackley,
        shifted_osz_asy_lam_rastrigin_nb as _shifted_rastrigin,
        shifted_osz_asy_schwefel_nb as _shifted_schwefel,
        shifted_osz_elliptic_nb as _shifted_elliptic,
        shifted_rosenbrock_nb as _shifted_rosenbrock,
        # Fused group kernels (F4-F14)
        group_elliptic_nb as _group_elliptic,
        group_rastrigin_nb as _group_rastrigin,
        group_ackley_nb as _group_ackley,
        group_schwefel_nb as _group_schwefel,
        # Fused separable-remainder kernels (F4-F7)
        sep_osz_elliptic_nb as _sep_elliptic,
        sep_osz_asy_lam_rastrigin_nb as _sep_rastrigin,
        sep_osz_asy_lam_ackley_nb as _sep_ackley,
        sep_sphere_nb as _sep_sphere,
        # RAW-ackley twins (ackley_variant='raw' — F3/F6/F10 only)
        shifted_ackley_raw_nb as _shifted_ackley_raw,
        group_ackley_raw_nb as _group_ackley_raw,
        sep_ackley_raw_nb as _sep_ackley_raw,
    )
except ImportError:
    _shifted_elliptic = None
    _shifted_rastrigin = None
    _shifted_ackley = None
    _shifted_rosenbrock = None
    _shifted_schwefel = None
    _group_elliptic = None
    _group_rastrigin = None
    _group_ackley = None
    _group_schwefel = None
    _sep_elliptic = None
    _sep_rastrigin = None
    _sep_ackley = None
    _sep_sphere = None
    _shifted_ackley_raw = None
    _group_ackley_raw = None
    _sep_ackley_raw = None

# Serial (parallel=False) twins + the thread-local routing flag for opted-in
# optimizers (see _numba_serial.py / _kernel_mode.py — the LSGO mirror of the
# proven cec2017 design). At numba_threads=1 the parallel launch costs
# 60-90% of a single-row D=1000 evaluation; member-sequential optimizers gain
# 2.3-5x. Outside a serial_kernel_scope() every call site below takes the
# batch branch unchanged (one thread-local read, no FP change), so the
# FP-regime sentinel's default-path LSGO probe is untouched by construction.
try:
    from . import _numba_serial as _ns
    from ._kernel_mode import serial_kernels_active as _serial_kernels_active
    from ._kernel_mode import ackley_raw_active as _ackley_raw_active
except ImportError:
    _ns = None

    def _serial_kernels_active() -> bool:
        return False

    def _ackley_raw_active() -> bool:
        return False


# ============================================================
# Helper: Numba fused group evaluation
# ============================================================

def _eval_group_numba(x: np.ndarray, func_id: int, kernel,
                      overlap: int = 0) -> np.ndarray:
    """Evaluate group function via fused Numba kernel.

    Loads (or caches) the :class:`GroupInfoFlat` for *func_id* and
    dispatches to the given Numba *kernel*.  Returns ``(M,)`` weighted
    sum of per-group base function values.

    Parameters
    ----------
    x : (M, D) float64
    func_id : int
    kernel : njit function — one of the ``group_*_nb`` kernels.
    overlap : int — 0 for F8-F11, 5 for F13-F14.

    Raises
    ------
    ValueError
        If ``overlap`` does not match the function's expected value.
        Audit H-04 (lsgo): F4-F11 must use ``overlap=0`` and F13-F14
        must use ``overlap=5``; any other combination silently
        miscomputes group indexing without this guard.
    """
    if overlap != 0 and func_id not in (13, 14):
        raise ValueError(
            f"_eval_group_numba: F{func_id} requires overlap=0, got "
            f"overlap={overlap}.  Only F13/F14 use overlapping groups "
            f"(overlap=5)."
        )
    if overlap == 0 and func_id in (13, 14):
        raise ValueError(
            f"_eval_group_numba: F{func_id} is an overlapping function "
            f"and requires overlap=5, got overlap=0."
        )
    gf = load_group_flat(func_id, overlap)
    return kernel(
        _ensure_f64(x),
        gf.idx_flat, gf.xopt_flat, gf.rot_flat,
        gf.rot_offsets, gf.group_starts, gf.weights,
        gf.n_groups,
    )


# ============================================================
# Helper: NumPy fallback group evaluation (Python loop)
# ============================================================

def _validate_input(x: np.ndarray, func_id: int) -> None:
    """Common shape / dtype guard for the NumPy-fallback evaluators.

    The Numba-accelerated paths get the same checks via their kernel
    type signatures, but when Numba is missing the kernels are ``None``
    and we fall back to these Python helpers.  Validate here so a
    malformed call (1-D input, wrong dtype, empty population, etc.)
    fails with a meaningful message instead of an opaque KeyError or
    silent miscompute somewhere inside the per-group loop.
    """
    if x.ndim != 2:
        raise ValueError(
            f"_eval_groups_*: F{func_id} expects a 2-D (M, D) population "
            f"matrix, got {x.ndim}-D shape {x.shape}."
        )
    if x.shape[0] == 0:
        raise ValueError(
            f"_eval_groups_*: F{func_id} received an empty population "
            f"(M=0); the dispatcher requires at least one row."
        )
    if x.shape[1] == 0:
        raise ValueError(
            f"_eval_groups_*: F{func_id} received zero-dimensional input "
            f"(D=0); the dispatcher requires at least one column."
        )


def _eval_groups_with_sep(
    x: np.ndarray,
    func_id: int,
    group_func,
    sep_func,
) -> np.ndarray:
    """NumPy fallback: 7 groups + separable remainder (F4-F7).

    Python loop over groups, BLAS matmul for rotation, Numba (if
    available) for per-group base function.

    Audit M-03 (lsgo) — weighting asymmetry
    ---------------------------------------
    Per-group rotated contributions are multiplied by ``w[i]`` (loaded
    from ``F{id}-w`` in ``data.pkl``).  The 700-dimension separable
    remainder is added **unweighted** -- this matches the C++ reference
    (``Benchmarks::F4::compute`` ... ``F7::compute``) where the
    ``compute_*`` functions return ``sum(w[i] * func(z_i)) + func(z_sep)``.
    The asymmetry is intentional: the per-group weights compensate for
    the differing condition numbers / dynamic ranges of the rotated
    sub-blocks, but the separable remainder uses the natural scale of
    the base function and so needs no rescaling.

    The fast path inside ``f4`` / ``f5`` / ``f6`` / ``f7`` uses the
    same convention (``result = group_kernel(...) + sep_kernel(...)``),
    so both paths produce bit-identical numbers.
    """
    _validate_input(x, func_id)
    gi = load_group_info(func_id)
    result = np.zeros(x.shape[0], dtype=np.float64)
    for i in range(gi.n_groups):
        z_group = x[:, gi.group_indices[i]] - gi.xopt_groups[i]
        z_rot = z_group @ gi.rotation_matrices_T[i]
        result += gi.weights[i] * group_func(z_rot)
    if gi.sep_indices is not None:
        z_sep = x[:, gi.sep_indices] - gi.xopt_sep
        result += sep_func(z_sep)
    return result


def _eval_groups_no_sep(
    x: np.ndarray,
    func_id: int,
    group_func,
) -> np.ndarray:
    """NumPy fallback: 20 groups, no remainder (F8-F11)."""
    _validate_input(x, func_id)
    gi = load_group_info(func_id)
    result = np.zeros(x.shape[0], dtype=np.float64)
    for i in range(gi.n_groups):
        z_group = x[:, gi.group_indices[i]] - gi.xopt_groups[i]
        z_rot = z_group @ gi.rotation_matrices_T[i]
        result += gi.weights[i] * group_func(z_rot)
    return result


def _eval_groups_overlap(
    x: np.ndarray,
    func_id: int,
    group_func,
) -> np.ndarray:
    """NumPy fallback: 20 overlapping groups (F13-F14)."""
    _validate_input(x, func_id)
    gi = load_group_info(func_id, overlap=OVERLAP)
    result = np.zeros(x.shape[0], dtype=np.float64)
    for i in range(gi.n_groups):
        z_group = x[:, gi.group_indices[i]] - gi.xopt_groups[i]
        z_rot = z_group @ gi.rotation_matrices_T[i]
        result += gi.weights[i] * group_func(z_rot)
    return result


# ============================================================
# Category 1: Fully Separable (F1-F3)
#
# No rotation.  Shift only: z = x - xopt, then base function.
# Fused Numba kernels avoid the M×1000 intermediate allocation.
# ============================================================

def f1(x: np.ndarray) -> np.ndarray:
    """F1: Shifted Elliptic (D=1000, fully separable).

    T_osz → elliptic.  Unimodal, condition number ≈ 10^6.
    """
    xopt = load_xopt(1)
    if _shifted_elliptic is not None:
        kernel = _ns.shifted_osz_elliptic_nb if _serial_kernels_active() else _shifted_elliptic
        return kernel(_ensure_f64(x), xopt)
    return elliptic(x - xopt)


def f2(x: np.ndarray) -> np.ndarray:
    """F2: Shifted Rastrigin (D=1000, fully separable).

    T_osz → T_asy(0.2) → Λ(10) → rastrigin.  Multimodal.
    """
    xopt = load_xopt(2)
    if _shifted_rastrigin is not None:
        kernel = (
            _ns.shifted_osz_asy_lam_rastrigin_nb if _serial_kernels_active() else _shifted_rastrigin
        )
        return kernel(_ensure_f64(x), xopt)
    return rastrigin(x - xopt)


def f3(x: np.ndarray) -> np.ndarray:
    """F3: Shifted Ackley (D=1000, fully separable).

    Default: T_osz → T_asy(0.2) → Λ(10) → ackley (Molina's package, used by
    shade-ils).  Under ``ackley_raw_scope`` (``ackley_variant='raw'``): raw
    shifted ackley with no transform chain — the official CEC2013-LSGO
    ``benchmark_func.m`` form that LaTorre's MOS reference uses.  Multimodal.
    """
    xopt = load_xopt(3)
    if _shifted_ackley is not None:
        serial = _serial_kernels_active()
        if _ackley_raw_active():
            kernel = _ns.shifted_ackley_raw_nb if serial else _shifted_ackley_raw
        else:
            kernel = _ns.shifted_osz_asy_lam_ackley_nb if serial else _shifted_ackley
        return kernel(_ensure_f64(x), xopt)
    return (ackley_raw if _ackley_raw_active() else ackley)(x - xopt)


# ============================================================
# Category 2: 7 groups + 700 separable remainder (F4-F7)
#
# 7 rotated non-separable groups (weighted by w[i]) plus a
# 700-dim separable remainder evaluated with the same base
# function (except F7: groups=schwefel, remainder=sphere).
#
# Numba path: fused group kernel + fused sep kernel.
# Fallback: Python loop over groups with BLAS matmul.
# ============================================================

def f4(x: np.ndarray) -> np.ndarray:
    """F4: 7-group Rotated Elliptic + Sep Elliptic (D=1000).

    Numba path: fused group kernel + fused sep kernel, zero M×700
    temporaries.  Both kernels read directly from the population matrix.
    """
    if _group_elliptic is not None:
        serial = _serial_kernels_active()
        group_kernel = _ns.group_elliptic_nb if serial else _group_elliptic
        sep_kernel = _ns.sep_osz_elliptic_nb if serial else _sep_elliptic
        x_f64 = _ensure_f64(x)
        gf = load_group_flat(4)
        result = group_kernel(
            x_f64, gf.idx_flat, gf.xopt_flat, gf.rot_flat,
            gf.rot_offsets, gf.group_starts, gf.weights, gf.n_groups)
        if gf.sep_indices is not None:
            result += sep_kernel(x_f64, gf.sep_indices, gf.sep_xopt)
        return result
    return _eval_groups_with_sep(x, 4, elliptic, elliptic)


def f5(x: np.ndarray) -> np.ndarray:
    """F5: 7-group Rotated Rastrigin + Sep Rastrigin (D=1000).

    Numba path: fused group kernel + fused sep kernel.
    """
    if _group_rastrigin is not None:
        serial = _serial_kernels_active()
        group_kernel = _ns.group_rastrigin_nb if serial else _group_rastrigin
        sep_kernel = _ns.sep_osz_asy_lam_rastrigin_nb if serial else _sep_rastrigin
        x_f64 = _ensure_f64(x)
        gf = load_group_flat(5)
        result = group_kernel(
            x_f64, gf.idx_flat, gf.xopt_flat, gf.rot_flat,
            gf.rot_offsets, gf.group_starts, gf.weights, gf.n_groups)
        if gf.sep_indices is not None:
            result += sep_kernel(x_f64, gf.sep_indices, gf.sep_xopt)
        return result
    return _eval_groups_with_sep(x, 5, rastrigin, rastrigin)


def f6(x: np.ndarray) -> np.ndarray:
    """F6: 7-group Rotated Ackley + Sep Ackley (D=1000).

    Numba path: fused group kernel + fused sep kernel.
    """
    if _group_ackley is not None:
        serial = _serial_kernels_active()
        if _ackley_raw_active():
            group_kernel = _ns.group_ackley_raw_nb if serial else _group_ackley_raw
            sep_kernel = _ns.sep_ackley_raw_nb if serial else _sep_ackley_raw
        else:
            group_kernel = _ns.group_ackley_nb if serial else _group_ackley
            sep_kernel = _ns.sep_osz_asy_lam_ackley_nb if serial else _sep_ackley
        x_f64 = _ensure_f64(x)
        gf = load_group_flat(6)
        result = group_kernel(
            x_f64, gf.idx_flat, gf.xopt_flat, gf.rot_flat,
            gf.rot_offsets, gf.group_starts, gf.weights, gf.n_groups)
        if gf.sep_indices is not None:
            result += sep_kernel(x_f64, gf.sep_indices, gf.sep_xopt)
        return result
    base = ackley_raw if _ackley_raw_active() else ackley
    return _eval_groups_with_sep(x, 6, base, base)


def f7(x: np.ndarray) -> np.ndarray:
    """F7: 7-group Rotated Schwefel + Sep Sphere (D=1000).

    Note: separable remainder uses *sphere* (not schwefel).
    Numba path: fused group kernel + fused sep kernel.
    """
    if _group_schwefel is not None:
        serial = _serial_kernels_active()
        group_kernel = _ns.group_schwefel_nb if serial else _group_schwefel
        sep_kernel = _ns.sep_sphere_nb if serial else _sep_sphere
        x_f64 = _ensure_f64(x)
        gf = load_group_flat(7)
        result = group_kernel(
            x_f64, gf.idx_flat, gf.xopt_flat, gf.rot_flat,
            gf.rot_offsets, gf.group_starts, gf.weights, gf.n_groups)
        if gf.sep_indices is not None:
            result += sep_kernel(x_f64, gf.sep_indices, gf.sep_xopt)
        return result
    return _eval_groups_with_sep(x, 7, schwefel_1_2, sphere)


# ============================================================
# Category 3: 20 groups, no separable remainder (F8-F11)
#
# All 1000 dimensions are partitioned into 20 non-separable
# groups (sizes 25/50/100).  No separable remainder.
# ============================================================

def f8(x: np.ndarray) -> np.ndarray:
    """F8: 20-group Rotated Elliptic (D=1000)."""
    if _group_elliptic is not None:
        kernel = _ns.group_elliptic_nb if _serial_kernels_active() else _group_elliptic
        return _eval_group_numba(x, 8, kernel)
    return _eval_groups_no_sep(x, 8, elliptic)


def f9(x: np.ndarray) -> np.ndarray:
    """F9: 20-group Rotated Rastrigin (D=1000)."""
    if _group_rastrigin is not None:
        kernel = _ns.group_rastrigin_nb if _serial_kernels_active() else _group_rastrigin
        return _eval_group_numba(x, 9, kernel)
    return _eval_groups_no_sep(x, 9, rastrigin)


def f10(x: np.ndarray) -> np.ndarray:
    """F10: 20-group Rotated Ackley (D=1000).

    Default transformed (Molina/shade-ils); raw under ``ackley_raw_scope``
    (MOS's LaTorre/official reference).
    """
    if _group_ackley is not None:
        serial = _serial_kernels_active()
        if _ackley_raw_active():
            kernel = _ns.group_ackley_raw_nb if serial else _group_ackley_raw
        else:
            kernel = _ns.group_ackley_nb if serial else _group_ackley
        return _eval_group_numba(x, 10, kernel)
    base = ackley_raw if _ackley_raw_active() else ackley
    return _eval_groups_no_sep(x, 10, base)


def f11(x: np.ndarray) -> np.ndarray:
    """F11: 20-group Rotated Schwefel (D=1000)."""
    if _group_schwefel is not None:
        kernel = _ns.group_schwefel_nb if _serial_kernels_active() else _group_schwefel
        return _eval_group_numba(x, 11, kernel)
    return _eval_groups_no_sep(x, 11, schwefel_1_2)


# ============================================================
# Category 4: Fully Non-Separable (F12, F15)
#
# All 1000 dims shifted and evaluated with a single base
# function.  No rotation.  Fused Numba kernels handle the
# entire shift+transform+evaluate pipeline.
# ============================================================

def f12(x: np.ndarray) -> np.ndarray:
    """F12: Shifted Rosenbrock (D=1000, fully non-separable).

    No transforms (rosenbrock has no T_osz/T_asy/Lambda).

    Note: Rosenbrock's minimum is at ``z = 1`` (all ones), so the
    global optimum in decision space is at ``x* = xopt + 1``, not
    at ``xopt`` itself.  ``f(xopt) = N - 1 = 999`` (D=1000).
    This matches the C++ reference (``Benchmarks::rosenbrock``).

    The first call triggers the lazy C-01 baseline assertion
    (audit AUDIT-15) to verify ``f12(xopt) == 999`` without
    paying the JIT cost at bare import time.
    """
    _assert_f12_baseline()
    xopt = load_xopt(12)
    if _shifted_rosenbrock is not None:
        kernel = _ns.shifted_rosenbrock_nb if _serial_kernels_active() else _shifted_rosenbrock
        return kernel(_ensure_f64(x), xopt)
    return rosenbrock(x - xopt)


def f15(x: np.ndarray) -> np.ndarray:
    """F15: Shifted Schwefel 1.2 (D=1000, fully non-separable).

    T_osz → T_asy(0.2) → cumsum squared.  No Lambda.
    """
    xopt = load_xopt(15)
    if _shifted_schwefel is not None:
        kernel = (
            _ns.shifted_osz_asy_schwefel_nb if _serial_kernels_active() else _shifted_schwefel
        )
        return kernel(_ensure_f64(x), xopt)
    return schwefel_1_2(x - xopt)


# ============================================================
# Category 5: Overlapping Groups (F13-F14, D=905)
#
# 20 groups with overlap=5 between consecutive groups.
# Both use schwefel_1_2 as the base function.
#
# F13 (conforming): single global shift vector, groups index
#   into it via permutation — shared dims get same shift.
# F14 (conflicting): per-group independent shift vectors loaded
#   via readOvectorVec — shared dims get DIFFERENT shifts from
#   different groups, creating optimization conflicts.
# ============================================================

def f13(x: np.ndarray) -> np.ndarray:
    """F13: Overlapping Schwefel (conforming, D=905).

    20 groups, overlap=5.  Single shared shift vector.
    """
    if _group_schwefel is not None:
        kernel = _ns.group_schwefel_nb if _serial_kernels_active() else _group_schwefel
        return _eval_group_numba(x, 13, kernel, overlap=OVERLAP)
    return _eval_groups_overlap(x, 13, schwefel_1_2)


def f14(x: np.ndarray) -> np.ndarray:
    """F14: Overlapping Schwefel (conflicting, D=905).

    20 groups, overlap=5.  Per-group independent shift vectors.
    """
    if _group_schwefel is not None:
        kernel = _ns.group_schwefel_nb if _serial_kernels_active() else _group_schwefel
        return _eval_group_numba(x, 14, kernel, overlap=OVERLAP)
    return _eval_groups_overlap(x, 14, schwefel_1_2)


# ============================================================
# Audit C-01 (lsgo): F12 fidelity assertion.
#
# Rosenbrock has its global minimum at z=1 (all-ones), not z=0,
# so f12(xopt) = N - 1 = 999 (D=1000), NOT zero.  This is a
# common source of confusion: every other LSGO function has
# f(xopt) = 0, but F12 inherits Rosenbrock's intrinsic offset.
#
# We check this contract once on first use so any accidental
# change to the shift vector, the kernel, or the base function
# fails loudly rather than silently shipping wrong baselines.
# Cost: one (1, 1000) evaluation -- ~1 ms.
#
# Audit AUDIT-15: moved from module-scope call to a lazy
# once-flag pattern so bare ``import composite`` does not
# trigger Numba JIT compilation (~200 ms).  The assertion
# still runs before the first real evaluation.
# ============================================================
_f12_baseline_checked: bool = False


def _assert_f12_baseline() -> None:
    """Verify F12(xopt) == 999 (once, on first use)."""
    global _f12_baseline_checked
    if _f12_baseline_checked:
        return
    _f12_baseline_checked = True
    xopt = load_xopt(12)
    val = float(f12(xopt.reshape(1, -1))[0])
    expected = float(1000 - 1)  # Rosenbrock at z=1 → 0; at z=0 → N-1
    if not np.isclose(val, expected, rtol=0.0, atol=1e-9):
        raise RuntimeError(
            f"CEC2013LSGO F12 baseline assertion failed: "
            f"f12(xopt) = {val!r}, expected {expected!r} "
            f"(Rosenbrock minimum is at z=1, not z=0). "
            f"This indicates a corrupted shift vector, a broken "
            f"kernel, or a regression in the base function."
        )
