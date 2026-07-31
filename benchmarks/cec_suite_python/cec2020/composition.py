"""CEC2020 composition functions F8–F10.

Composition functions blend multiple base functions using distance-based weights.
Each component is independently shift+rotated using its own data from shifts_cf
and rotations_cf, then scaled by a lambda multiplier.

Weight formula (cf_cal, identical across all CEC suites):
  w_i = (1/‖x-shift_i‖) * exp(-‖x-shift_i‖² / (2*D*δ_i²))
  At x = shift_0: w_0 = INF → f(x) = bias_0 + fid_bias = fid_bias

Component specifications:
  F8 cf02 (3 comp): rastrigin(λ=1) + griewank(λ=10) + schwefel(λ=1)
                     δ=[10,20,30], bias=[0,100,200], final=+2200

  F9 cf04 (4 comp): ackley(λ=10) + ellips(λ=1e-6) + griewank(λ=10) + rastrigin(λ=1)
                     δ=[10,20,30,40], bias=[0,100,200,300], final=+2400

  F10 cf05 (5 comp): rastrigin(λ=10) + happycat(λ=1) + ackley(λ=10)
                      + discus(λ=1e-6) + rosenbrock(λ=1)
                      δ=[10,20,30,40,50], bias=[0,100,200,300,400], final=+2500

Lambda values normalize component outputs: 10000/divisor where divisor approximates
each function's typical magnitude. This prevents any single component from dominating
due to scale differences.

The _eval_component helper applies shift_rotate with the component's own shrink rate,
then evaluates the basic function. This is different from CEC2017/2022 where shrink
rates are baked into the basic functions.

Valid dimensions: {2, 5, 10, 15, 20, 30, 50, 100}.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from collections.abc import Callable

from . import basic
from .transforms import SHRINK_RATES, shift_rotate
from benchmarks.cec_suite_python.cec2017.composition import (
    f22 as _cec2017_cf02,
    f24 as _cec2017_cf04,
    f25 as _cec2017_cf05,
)

INF = 1.0e99

# Audit H-3: import cf_cal_fast from the per-suite kernel module
# (``cec2020/_numba.py``) instead of ``gsk._numba_accel``.  The old
# import path silently fell through to ``None`` — the gsk module
# does not export this symbol — so CEC2020 composition F8/F9/F10 was
# running the pure-NumPy branch on every NFE without anyone noticing.
# The per-suite kernel uses ``fastmath=False`` to preserve CEC2020's
# cross-ISA bit-stability policy (see ``cec2020/_numba.py`` module
# docstring, audit H-01/H-03).
try:
    from ._numba import cf_cal_fast as _cf_cal_fast
except ImportError:
    _cf_cal_fast = None

# C20-4: cache contiguous (K, D) shift slices per (func_id, D) pair.
import threading as _threading
_cf_shifts_c_cache: dict[tuple[int, int], np.ndarray] = {}
_cf_shifts_c_lock = _threading.RLock()


def _get_cf_shifts_c(func_id: int, Os_all: np.ndarray, D: int) -> np.ndarray:
    """Return a cached contiguous (K, D) shift slice for the given function."""
    key = (func_id, D)
    cached = _cf_shifts_c_cache.get(key)
    if cached is not None:
        return cached
    with _cf_shifts_c_lock:
        cached = _cf_shifts_c_cache.get(key)
        if cached is not None:
            return cached
        cached = np.ascontiguousarray(Os_all[:, :D], dtype=np.float64)
        _cf_shifts_c_cache[key] = cached
        return cached

# ---- Per-function constants (hoisted to avoid per-call allocation) ----
# Audit HIGH-PERF-04: previously these were Python lists, so every NFE
# paid for ``np.array(delta, ...)`` / ``np.array(bias, ...)`` allocations
# inside ``cf_cal``.  Storing them as immutable C-contiguous float64
# arrays at module load eliminates the per-call cast.
_F8_DELTA = np.array([10.0, 20.0, 30.0], dtype=np.float64)
_F8_BIAS = np.array([0.0, 100.0, 200.0], dtype=np.float64)
_F8_LAMBDAS = np.array([1.0, 1000.0 / 100.0, 1.0], dtype=np.float64)

_F9_DELTA = np.array([10.0, 20.0, 30.0, 40.0], dtype=np.float64)
_F9_BIAS = np.array([0.0, 100.0, 200.0, 300.0], dtype=np.float64)
_F9_LAMBDAS = np.array(
    [1000.0 / 100.0, 10000.0 / 1e10, 1000.0 / 100.0, 1.0], dtype=np.float64
)

_F10_DELTA = np.array([10.0, 20.0, 30.0, 40.0, 50.0], dtype=np.float64)
_F10_BIAS = np.array([0.0, 100.0, 200.0, 300.0, 400.0], dtype=np.float64)
_F10_LAMBDAS = np.array(
    [10000.0 / 1e3, 1000.0 / 1e3, 1000.0 / 100.0, 10000.0 / 1e10, 1.0],
    dtype=np.float64,
)

# Make the module-level arrays read-only so an accidental in-place mutation
# (e.g. `delta *= 2` inside an ill-behaved component) raises immediately.
for _arr in (
    _F8_DELTA, _F8_BIAS, _F8_LAMBDAS,
    _F9_DELTA, _F9_BIAS, _F9_LAMBDAS,
    _F10_DELTA, _F10_BIAS, _F10_LAMBDAS,
):
    _arr.flags.writeable = False
del _arr

# Function and shrink-rate lists (reference basic module and SHRINK_RATES dict)
_F8_FUNCS = [basic.rastrigin, basic.griewank, basic.schwefel]
_F8_SHRINKS = [SHRINK_RATES['rastrigin'], SHRINK_RATES['griewank'], SHRINK_RATES['schwefel']]

_F9_FUNCS = [basic.ackley, basic.ellips, basic.griewank, basic.rastrigin]
_F9_SHRINKS = [SHRINK_RATES['ackley'], SHRINK_RATES['ellips'],
               SHRINK_RATES['griewank'], SHRINK_RATES['rastrigin']]

_F10_FUNCS = [basic.rastrigin, basic.happycat, basic.ackley, basic.discus, basic.rosenbrock]
_F10_SHRINKS = [SHRINK_RATES['rastrigin'], SHRINK_RATES['happycat'], SHRINK_RATES['ackley'],
                SHRINK_RATES['discus'], SHRINK_RATES['rosenbrock']]


def _eval_component(
                    func: Callable[..., np.ndarray],
                    x: np.ndarray,
                    Os_i: np.ndarray,
                    Mr_i: np.ndarray,
                    shrink: float,
                    r_flag: int = 1,
                    Mr_T_i: np.ndarray | None = None,
) -> np.ndarray:
    """Evaluate a single composition component: shift_rotate then basic func.

    XS-01: *Mr_T_i* is the pre-transposed rotation matrix for this
    component, forwarded to :func:`shift_rotate` for the NumPy fallback.
    """
    z = shift_rotate(x, Os_i, Mr_i, shrink, 1, r_flag, Mr_T=Mr_T_i)
    return func(z)


def cf_cal(
    x: np.ndarray, Os_all: np.ndarray, delta: list[float] | np.ndarray,
    bias: list[float] | np.ndarray, fit: np.ndarray, cf_num: int,
) -> np.ndarray:
    """Composition weight calculation — mirrors C++ cf_cal exactly.

    The composition combines cf_num base functions, each evaluated at a different
    shift point. The weight for component i is:

      w_i = (1/dist_i) * exp(-dist_i² / (2*D*δ_i²))

    where dist_i = ‖x - shift_i‖ and δ_i (delta) controls spread. When x exactly
    equals shift_i, dist=0 → w=INF → that component dominates completely, giving
    f(x) = fit_i + bias_i. Since fit_i = basic_func(0) * λ_i = 0, this means
    f(shift_0) = bias_0 (typically 0), and the final result is bias_0 + fid_bias.

    Expects (M, D) batch input (the dispatcher handles 1D→2D reshaping).

    Parameters
    ----------
    x : ndarray (M, D) — raw (unshifted) input
    Os_all : ndarray (cf_num, >=D) — shift vectors for each component
    delta : list/array of length cf_num — spread parameters (σ values)
    bias : list/array of length cf_num — per-component bias offsets
    fit : ndarray (cf_num, M) — component fitness values
    cf_num : int — number of components

    Returns
    -------
    f : ndarray (M,) — weighted combination
    """
    M, D = x.shape

    # Audit HIGH-PERF-04: callers already pass float64 ndarrays from the
    # hoisted ``_F{8,9,10}_*`` module constants, so the previous
    # ``np.array(...)`` casts allocated three small arrays per NFE for
    # nothing.  Use ``np.asarray`` (no copy when already float64) and
    # only force contiguity / dtype when the inputs are not already
    # well formed.
    delta_arr = np.asarray(delta, dtype=np.float64)
    bias_arr = np.asarray(bias, dtype=np.float64)
    fit = np.asarray(fit, dtype=np.float64)

    if _cf_cal_fast is not None:
        # C20-4: Os_all is now pre-cached as contiguous by _get_cf_shifts_c;
        # delta_arr, bias_arr, fit are already float64 from np.asarray above.
        # B2: delta_arr, bias_arr are C-contiguous from module-level constants
        # via np.asarray (no-copy); fit is from np.zeros (always contiguous).
        # Only x needs the contiguity guard (comes from outside).
        return _cf_cal_fast(
            np.ascontiguousarray(x, dtype=np.float64),
            Os_all,
            delta_arr,
            bias_arr,
            fit,
        )

    # Add biases to fit values — vectorized over all K components at once.
    # bias is (K,), fit is (K, M); broadcasting adds bias per component row.
    fit = fit + bias_arr[:, np.newaxis]  # (K, M)

    # Compute squared Euclidean distances from each individual to each
    # component's shift vector.  Audit HIGH-PERF-03: previous version
    # built a (K, M, D) ``diff`` tensor (~80 MB at K=10, M=1000, D=100);
    # we now expand ``|x - s|^2 = |x|^2 - 2 x·s + |s|^2`` so the largest
    # temporary is (K, M).  Numerically equivalent for finite inputs.
    os_sliced = Os_all[:cf_num, :D]                                # (K, D)
    x_norm_sq = np.einsum('ij,ij->i', x, x)                        # (M,)
    cs_norm_sq = np.einsum('ij,ij->i', os_sliced, os_sliced)       # (K,)
    cross = os_sliced @ x.T                                        # (K, M)
    dist_sq = (
        x_norm_sq[np.newaxis, :]
        - 2.0 * cross
        + cs_norm_sq[:, np.newaxis]
    )                                                              # (K, M)
    # Floating-point cancellation can drop dist_sq slightly below zero
    # when x ≈ shift; clamp so the sqrt below is well defined.
    np.maximum(dist_sq, 0.0, out=dist_sq)

    # Weight formula: w_i = (1/dist_i) * exp(-dist_i² / (2*D*δ_i²))
    # Vectorized with np.where to handle dist==0 → INF.
    delta2 = (2.0 * D * delta_arr ** 2)[:, np.newaxis]            # (K, 1)
    nonzero = dist_sq != 0.0
    w = np.where(
        nonzero,
        (1.0 / np.sqrt(np.where(nonzero, dist_sq, 1.0)))
        * np.exp(-dist_sq / delta2),  # B1: delta2 always positive (from module-level constants)
        INF,
    )  # (K, M)

    w_sum = w.sum(axis=0)

    all_zero = w_sum == 0.0
    if np.any(all_zero):
        w[:, all_zero] = 1.0
        w_sum[all_zero] = cf_num

    # Weighted sum — fully vectorized dot over K components.
    return np.sum(w / w_sum * fit, axis=0)


# ---------- F8: cf02 (3 components, bias=2200) ----------
def f8_cf02(x: np.ndarray, Os_cf: np.ndarray, Mr_cf: np.ndarray, D: int,
            *, Mr_cf_T: np.ndarray | None = None) -> np.ndarray:
    """Composition 2: rastrigin + griewank(x10) + schwefel. Bias=2200.

    Expects (M, D) batch input (the dispatcher handles 1D→2D reshaping).
    """
    # Public CEC2020 F8 is staged-MEX internal id 22. The validated C++
    # port matches the CEC2017 F22 composition kernel when it is fed the
    # CEC2020 internal-id shift and rotation data. Reuse that audited path
    # rather than maintaining a second near-duplicate composition evaluator.
    return _cec2017_cf02(x, shift=Os_cf, rotation=Mr_cf)


# ---------- F9: cf04 (4 components, bias=2400) ----------
def f9_cf04(x: np.ndarray, Os_cf: np.ndarray, Mr_cf: np.ndarray, D: int,
            *, Mr_cf_T: np.ndarray | None = None) -> np.ndarray:
    """Composition 4: ackley(x10) + ellips(x1e-6) + griewank(x10) + rastrigin. Bias=2400.

    Expects (M, D) batch input (the dispatcher handles 1D→2D reshaping).
    """
    # Public CEC2020 F9 is staged-MEX internal id 24, equivalent to the
    # CEC2017 F24 composition kernel with CEC2020 data overrides.
    return _cec2017_cf04(x, shift=Os_cf, rotation=Mr_cf)


# ---------- F10: cf05 (5 components, bias=2500) ----------
def f10_cf05(x: np.ndarray, Os_cf: np.ndarray, Mr_cf: np.ndarray, D: int,
             *, Mr_cf_T: np.ndarray | None = None) -> np.ndarray:
    """Composition 5: rastrigin(x10) + happycat(x1) + ackley(x10)
    + discus(x1e-6) + rosenbrock. Bias=2500.

    Expects (M, D) batch input (the dispatcher handles 1D→2D reshaping).
    """
    # Public CEC2020 F10 is staged-MEX internal id 25, equivalent to the
    # CEC2017 F25 composition kernel with CEC2020 data overrides.
    return _cec2017_cf05(x, shift=Os_cf, rotation=Mr_cf)
