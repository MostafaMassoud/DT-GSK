"""CEC2013 base functions with full transformation pipelines.

Cross-reference: ``test_func.c`` (Jane Jing Liang, 27 Jan 2013)
from the CEC'2013 competition R package ``cec2013``.

Each function takes ``(x, Os, M1, [M2,] r_flag)`` and returns raw fitness
*without* the CEC2013 bias offset.  Both :mod:`simple` (F1-F20) and
:mod:`composition` (F21-F28) call into these functions.

All functions accept batch input: *x* is ``(M, N)``, returns ``(M,)``.

C reference mapping
-------------------
Each Python function corresponds to a C function in ``test_func.c``:

=======================  ========================  ==============  ===========
Python function          C function                C lines         Pipeline
=======================  ========================  ==============  ===========
sphere_func              sphere_func               252-266         shift -> [R] -> sum(z^2)
ellips_func              ellips_func               268-283         shift -> R -> osz -> sum(lambda*z^2)
bent_cigar_func          bent_cigar_func           285-307         shift -> R1 -> asy -> R2 -> z0^2+1e6*sum(zi^2)
discus_func              discus_func               309-325         shift -> R -> osz -> 1e6*y0^2+sum(yi^2)
dif_powers_func          dif_powers_func           327-342         shift -> [R] -> sqrt(sum(|z|^exp))
rosenbrock_func          rosenbrock_func           345-371         shift -> x(2.048/100) -> [R] -> +1 -> Rosen
schaffer_F7_func         schaffer_F7_func          373-401         shift -> R1 -> asy -> cond -> R2 -> formula
ackley_func              ackley_func               403-434         shift -> R1 -> asy -> cond -> R2 -> Ackley
weierstrass_func         weierstrass_func          437-478         shift -> x(0.5/100) -> R1 -> asy -> cond -> R2 -> W
griewank_func            griewank_func             481-509         shift -> x6 -> [R] -> cond -> Griewank
rastrigin_func           rastrigin_func            511-551         shift -> x(5.12/100) -> R1 -> osz -> asy -> R2 -> cond -> R1 -> Rast
step_rastrigin_func      step_rastrigin_func       554-601         same + step quantisation after first R1
schwefel_func            schwefel_func             603-643         shift -> x10 -> [R] -> cond -> +420.97 -> Schwefel
katsuura_func            katsuura_func             645-685         shift -> x(5/100) -> R1 -> cond -> R2 -> product
bi_rastrigin_func        bi_rastrigin_func         687-749         shift -> x0.1 -> sign-flip -> R1 -> cond -> R2 -> two-funnel
grie_rosen_func          grie_rosen_func           752-785         shift -> x(5/100) -> [R discarded] -> +1 -> GR chain
escaffer6_func           escaffer6_func            788-818         shift -> R1 -> asy -> R2 -> circular SF6
=======================  ========================  ==============  ===========

Note: grie_rosen has a C bug at line 770 where ``z[i]=y[i]+1`` overwrites the
rotation result.  Python replicates this intentionally (rotation is a no-op).

Buffer semantics
----------------
The original C implementation reuses two global buffers ``y[]`` and ``z[]``
(declared ``extern`` at line 53 of ``test_func.c``).

:func:`asy_func <transforms.asy_func>` (C ``asyfunc``, line 1003) only
writes to the output buffer where the input > 0; otherwise the output
retains whatever was previously stored (the C ``xasy`` buffer is NOT
zeroed).  We match this by passing the previous buffer content via the
explicit ``prev_buf`` parameter.

For example, in bent_cigar (C lines 289-300)::

    shiftfunc(x, y, ...)   -> y = shifted
    rotatefunc(y, z, ...)  -> z = rotated
    asyfunc(z, y, ...)     -> y[i] = z[i]^exp  if z[i]>0
                              y[i] = y[i]       if z[i]<=0  (still shifted!)

Python equivalent::

    y = x - Os                       # shifted
    z = y @ M1.T                     # rotated
    y2 = asy_func(z, y, beta=0.5)   # reads z, falls back to y

Numba acceleration
------------------
When numba is available, raw formula evaluation dispatches to JIT-compiled
kernels from :mod:`._numba`.  The transformation pipeline (shift, rotate,
osz, asy, conditioning) is done in NumPy; only the innermost formula
loop is JIT-accelerated.  This provides significant speedup especially
for composition functions where the same formula is evaluated many times
with different shift/rotation data.

Constants
---------
C defines (line 15-18)::

    #define E  2.7182818284590452353602874713526625
    #define PI 3.1415926535897932384626433832795029

Both truncate to the same IEEE 754 double as ``np.e`` and ``np.pi``.
"""

from __future__ import annotations

import threading

import numpy as np

from .transforms import asy_func, conditioning, osz_func

PI = np.pi
TWO_PI = 2.0 * np.pi   # audit round-2: avoid recomputing 2*π per call
E = np.e

# ---------------------------------------------------------------------------
# Numba kernels (graceful fallback)
# ---------------------------------------------------------------------------
try:
    from ._numba import (
        ackley_core_nb as _ackley_nb,
        bent_cigar_core_nb as _bent_cigar_nb,
        bi_rastrigin_core_nb as _bi_rastrigin_nb,
        dif_powers_core_nb as _dif_powers_nb,
        discus_core_nb as _discus_nb,
        elliptic_core_nb as _elliptic_nb,
        escaffer6_core_nb as _escaffer6_nb,
        grie_rosen_core_nb as _grie_rosen_nb,
        griewank_core_nb as _griewank_nb,
        katsuura_core_nb as _katsuura_nb,
        rastrigin_core_nb as _rastrigin_nb,
        rosenbrock_core_nb as _rosenbrock_nb,
        schaffer_F7_core_nb as _schaffer_F7_nb,
        schwefel_core_nb as _schwefel_nb,
        sphere_nb as _sphere_nb,
        step_rastrigin_quant_nb as _step_rastrigin_quant_nb,
        weierstrass_core_nb as _weierstrass_nb,
    )
except ImportError:
    _sphere_nb = None
    _bent_cigar_nb = None
    _elliptic_nb = None
    _discus_nb = None
    _dif_powers_nb = None
    _rastrigin_nb = None
    _schwefel_nb = None
    _rosenbrock_nb = None
    _ackley_nb = None
    _weierstrass_nb = None
    _griewank_nb = None
    _escaffer6_nb = None
    _grie_rosen_nb = None
    _schaffer_F7_nb = None
    _katsuura_nb = None
    _bi_rastrigin_nb = None
    _step_rastrigin_quant_nb = None

# Serial (parallel=False) twins of the same kernels plus the thread-local flag
# that routes an opted-in optimizer's evaluations to them.  Motivated by
# member-sequential optimizers (toa/saro/moa-mother/ema), whose single-row
# dispatches pay the numba parallel-runtime launch on EVERY kernel of the
# CEC2013 transform pipeline at numba_threads=1 (~924 us per single-row
# evaluation versus ~10 us on the twins; see _numba_serial.py).  Outside a
# serial_kernel_scope() every call site below takes the batch-kernel branch
# unchanged (one thread-local read of overhead, no floating-point change), so
# flag-off problems and the FP-regime sentinel are untouched.
try:
    from . import _numba_serial as _ns
    from ._kernel_mode import serial_kernels_active as _serial_kernels_active
except ImportError:
    _ns = None

    def _serial_kernels_active() -> bool:
        """Fallback when the serial-kernel modules are unavailable."""
        return False


def _ensure_f64(x: np.ndarray) -> np.ndarray:
    """Return C-contiguous float64 view (zero-copy when already the right type).

    Required by all Numba kernels which expect ``float64[::1]`` contiguous
    arrays.  If *x* is already C-contiguous float64, ``np.ascontiguousarray``
    returns the same buffer (no copy).
    """
    return np.ascontiguousarray(x, dtype=np.float64)


# ---------------------------------------------------------------------------
# Per-dimension coefficient caches
# ---------------------------------------------------------------------------
# These avoid recomputing power-law coefficients on every call.
# Audit AUDIT-06: use a shared reentrant lock for thread safety under
# free-threaded CPython 3.13t (--disable-gil), mirroring the
# CEC2013LSGO ``_CACHE_LOCK`` pattern.  The fast read path stays
# lock-free; only the "not present" branch acquires the lock with a
# double-check inside.
_CACHE_LOCK = threading.RLock()
_elliptic_coeff_cache: dict[int, np.ndarray] = {}
_dif_powers_exp_cache: dict[int, np.ndarray] = {}
_griewank_sqrt_cache: dict[int, np.ndarray] = {}   # N -> sqrt(1+arange(N))
_katsuura_idx_cache: dict[int, np.ndarray] = {}     # N -> arange(1, N+1)

# M3: Precomputed coefficients for Weierstrass/Katsuura NumPy fallback paths.
# Same role as CEC2017's ``_WEIER_AK_FB`` etc. — avoids recomputing power
# sequences (a^k, b^k, 2^j) on every NFE when Numba is unavailable.
_WEIER_AK_FB = np.array([0.5 ** k for k in range(21)], dtype=np.float64)
_WEIER_BK_FB = np.array([3.0 ** k for k in range(21)], dtype=np.float64)
_WEIER_CORRECTION_FB = float(
    np.sum(_WEIER_AK_FB * np.cos(TWO_PI * _WEIER_BK_FB * 0.5))
)

_KATSUURA_POW2J_FB = np.array([2.0 ** (j + 1) for j in range(32)], dtype=np.float64)


def _get_elliptic_coeff(N: int) -> np.ndarray:
    """Return cached coefficient vector 10^(6*i/(N-1)) for elliptic function.

    Guard: N=1 returns [1.0] (single dim, exponent=0/(0)→0 by convention).
    CEC2013 always has N≥2 but guard prevents ZeroDivisionError if reused.
    """
    if N not in _elliptic_coeff_cache:
        with _CACHE_LOCK:
            if N not in _elliptic_coeff_cache:
                if N == 1:
                    _elliptic_coeff_cache[N] = np.ones(1, dtype=np.float64)
                else:
                    _elliptic_coeff_cache[N] = np.power(
                        10.0, 6.0 * np.arange(N, dtype=np.float64) / (N - 1),
                    )
    return _elliptic_coeff_cache[N]


def _get_dif_powers_exp(N: int) -> np.ndarray:
    """Return cached exponent vector 2 + 4*i//(N-1) for dif_powers function.

    Guard: N=1 returns [2.0] (base exponent only, no scaling).
    CEC2013 always has N≥2 but guard prevents ZeroDivisionError if reused.
    """
    if N not in _dif_powers_exp_cache:
        with _CACHE_LOCK:
            if N not in _dif_powers_exp_cache:
                if N == 1:
                    _dif_powers_exp_cache[N] = np.array([2.0])
                else:
                    idx = np.arange(N)
                    _dif_powers_exp_cache[N] = (2 + 4 * idx // (N - 1)).astype(
                        np.float64,
                    )
    return _dif_powers_exp_cache[N]


# ============================================================
# Unimodal (F1-F5)
# ============================================================

def sphere_func(
    x: np.ndarray, Os: np.ndarray, M1: np.ndarray, r_flag: int,
    *, M1_T: np.ndarray | None = None,
) -> np.ndarray:
    """Shifted Sphere (F1 base).  C: ``sphere_func``, lines 252-266.

    Pipeline: shift -> [rotate] -> sum(z_i^2).

    When r_flag=0, dispatches to fused Numba kernel that combines
    shift + sum in a single pass (avoids (M,N) intermediate).
    When r_flag=1, applies rotation in NumPy then sums.

    XS-01: *M1_T* is the pre-transposed C-contiguous rotation matrix.
    When provided, ``y @ M1_T`` replaces ``y @ M1.T`` on the NumPy path.
    """
    N = x.shape[1]
    if _sphere_nb is not None and not r_flag:
        # Fused shift + sum: no intermediate array needed
        kernel = _ns.sphere_nb if _serial_kernels_active() else _sphere_nb
        return kernel(_ensure_f64(x), _ensure_f64(Os), N)
    y = x - Os
    z = (y @ M1_T if M1_T is not None else y @ M1.T) if r_flag else y
    return np.einsum('ij,ij->i', z, z)


def ellips_func(
    x: np.ndarray, Os: np.ndarray, M1: np.ndarray, r_flag: int,
    *, M1_T: np.ndarray | None = None,
) -> np.ndarray:
    """Rotated High Conditioned Elliptic (F2 base).  C: lines 268-283.

    Pipeline: shift -> rotate -> osz -> sum(10^(6i/(N-1)) * y_i^2).

    C: ``pow(10.0, 6.0*i/(nx-1)) * y[i]*y[i]`` (line 281).
    Coefficient vector is cached per dimension to avoid recomputation.

    XS-01: *M1_T* is the pre-transposed C-contiguous rotation matrix.
    When provided, ``y @ M1_T`` replaces ``y @ M1.T`` on the NumPy path.
    """
    N = x.shape[1]
    y = x - Os
    z = (y @ M1_T if M1_T is not None else y @ M1.T) if r_flag else y
    # osz_func always returns a new array, so no defensive copy needed.
    y2 = osz_func(z)
    # Guard: N=1 → coefficient is 10^(0/0); by convention 1.0, so f = z^2.
    # Must be BEFORE Numba dispatch: elliptic_core_nb divides by float(N-1)=0.0 → NaN.
    if N == 1:
        return y2[:, 0] ** 2
    if _elliptic_nb is not None:
        kernel = _ns.elliptic_core_nb if _serial_kernels_active() else _elliptic_nb
        return kernel(_ensure_f64(y2), N)
    coeff = _get_elliptic_coeff(N)
    return np.einsum('ij,ij->i', coeff * y2, y2)


def bent_cigar_func(
    x: np.ndarray, Os: np.ndarray, M1: np.ndarray, M2: np.ndarray,
    r_flag: int,
    *, M1_T: np.ndarray | None = None, M2_T: np.ndarray | None = None,
) -> np.ndarray:
    """Rotated Bent Cigar (F3 base).  C: lines 285-307.

    Pipeline: shift -> rotate(M1) -> asy(beta=0.5) -> rotate(M2) ->
              z_0^2 + 10^6 * sum(z_i^2).

    Buffer semantics (C lines 289-300):
      ``shiftfunc(x,y,...) -> rotatefunc(y,z,Mr) -> asyfunc(z,y,0.5)``
      asy reads from z (rotated), writes to y; where z <= 0,
      y keeps the shifted (pre-rotation) values.

    C uses ``&Mr[nx*nx]`` for M2 (line 297); Python ``get_rotation(N, 1)``.

    XS-01: *M1_T* / *M2_T* are pre-transposed C-contiguous rotation matrices.
    """
    y = x - Os                                   # y = shifted
    z = ((y @ M1_T if M1_T is not None else y @ M1.T)
         if r_flag else y.copy())                # z = rotated
    y2 = asy_func(z, y, beta=0.5)               # asy: z->y (fallback->shifted y)
    z2 = ((y2 @ M2_T if M2_T is not None else y2 @ M2.T)
          if r_flag else y2)                     # second rotation
    # Note: Numba kernel (bent_cigar_core_nb) exists but einsum is faster
    # because the formula is trivially BLAS-reducible (weighted sum-of-squares).
    return z2[:, 0] ** 2 + 1e6 * np.einsum('ij,ij->i', z2[:, 1:], z2[:, 1:])


def discus_func(
    x: np.ndarray, Os: np.ndarray, M1: np.ndarray, r_flag: int,
    *, M1_T: np.ndarray | None = None,
) -> np.ndarray:
    """Rotated Discus (F4 base).  C: lines 309-325.

    Pipeline: shift -> rotate -> osz -> 10^6 * y_0^2 + sum(y_i^2).

    XS-01: *M1_T* is the pre-transposed C-contiguous rotation matrix.
    """
    N = x.shape[1]
    y = x - Os
    z = (y @ M1_T if M1_T is not None else y @ M1.T) if r_flag else y
    # osz_func always returns a new array, so no defensive copy needed.
    y2 = osz_func(z)
    if _discus_nb is not None:
        kernel = _ns.discus_core_nb if _serial_kernels_active() else _discus_nb
        return kernel(_ensure_f64(y2), N)
    return 1e6 * y2[:, 0] ** 2 + np.einsum('ij,ij->i', y2[:, 1:], y2[:, 1:])


def dif_powers_func(
    x: np.ndarray, Os: np.ndarray, M1: np.ndarray, r_flag: int,
    *, M1_T: np.ndarray | None = None,
) -> np.ndarray:
    """Different Powers (F5 base).  C: lines 327-342.

    Pipeline: shift -> [rotate] -> sqrt(sum(|z_i|^(2 + 4*i//(N-1)))).

    Note: C reference uses integer division ``4*i/(nx-1)`` (line 339) which
    truncates toward zero.  Python ``4 * idx // (N - 1)`` matches exactly
    for non-negative integers.  Exponent vector is cached per dimension.

    XS-01: *M1_T* is the pre-transposed C-contiguous rotation matrix.
    """
    N = x.shape[1]
    y = x - Os
    z = (y @ M1_T if M1_T is not None else y @ M1.T) if r_flag else y
    # Guard: N=1 → exponent is 2 + 0//0; by convention 2, so f = sqrt(z^2) = |z|.
    # Must be BEFORE Numba dispatch: dif_powers_core_nb does integer //0 → ZeroDivisionError.
    if N == 1:
        return np.abs(z[:, 0])
    if _dif_powers_nb is not None:
        kernel = _ns.dif_powers_core_nb if _serial_kernels_active() else _dif_powers_nb
        return kernel(_ensure_f64(z), N)
    exponents = _get_dif_powers_exp(N)
    return np.sqrt(np.sum(np.abs(z) ** exponents, axis=1))


# ============================================================
# Multimodal (F6-F20 bases)
# ============================================================

def rosenbrock_func(
    x: np.ndarray, Os: np.ndarray, M1: np.ndarray, r_flag: int,
    *, M1_T: np.ndarray | None = None,
) -> np.ndarray:
    """Rotated Rosenbrock (F6 base).  C: lines 345-371.

    Pipeline: shift -> shrink(2.048/100) -> rotate -> shift(+1) ->
              sum(100*(z_i^2 - z_{i+1})^2 + (z_i - 1)^2).

    Shrink factor: ``y[i]*2.048/100`` (C line 352).
    Origin shift:  ``z[i]=z[i]+1`` (C line 361) -- note this correctly uses
    z (post-rotation), unlike grie_rosen which has a C bug.

    XS-01: *M1_T* is the pre-transposed C-contiguous rotation matrix.
    """
    y = (x - Os) * (2.048 / 100.0)
    z = ((y @ M1_T if M1_T is not None else y @ M1.T) if r_flag else y) + 1.0
    if _rosenbrock_nb is not None:
        kernel = _ns.rosenbrock_core_nb if _serial_kernels_active() else _rosenbrock_nb
        return kernel(_ensure_f64(z))
    t1 = z[:, :-1] ** 2 - z[:, 1:]
    t2 = z[:, :-1] - 1.0
    return np.sum(100.0 * t1 ** 2 + t2 ** 2, axis=1)


def schaffer_F7_func(
    x: np.ndarray, Os: np.ndarray, M1: np.ndarray, M2: np.ndarray,
    r_flag: int,
    *, M1_T: np.ndarray | None = None, M2_T: np.ndarray | None = None,
) -> np.ndarray:
    """Rotated Schaffer's F7 (F7 base).  C: lines 373-401.

    Pipeline: shift -> rotate(M1) -> asy(beta=0.5) -> cond(alpha=10) ->
              rotate(M2) ->
              [1/(N-1) * sum(sqrt(s_i) + sqrt(s_i) * sin^2(50*s_i^0.2))]^2.

    C conditioning (line 384-385): ``z[i]=y[i]*pow(10.0,1.0*i/(nx-1)/2.0)``
    = cond(alpha=10).

    XS-01: *M1_T* / *M2_T* are pre-transposed C-contiguous rotation matrices.
    """
    N = x.shape[1]
    # Guard: N=1 → no consecutive pairs; C loop range(0..nx-2) doesn't execute.
    # Both Numba (0.0/0.0→NaN) and NumPy (int 0 divisor→ZeroDivisionError) fail.
    # Convention: empty sum → result = 0.
    if N == 1:
        return np.zeros(x.shape[0], dtype=np.float64)
    y = x - Os
    z = (y @ M1_T if M1_T is not None else y @ M1.T) if r_flag else y.copy()
    y2 = asy_func(z, y, beta=0.5)
    z2 = conditioning(y2, alpha=10.0)
    y3 = (z2 @ M2_T if M2_T is not None else z2 @ M2.T) if r_flag else z2
    if _schaffer_F7_nb is not None:
        kernel = _ns.schaffer_F7_core_nb if _serial_kernels_active() else _schaffer_F7_nb
        return kernel(_ensure_f64(y3))
    si = np.sqrt(y3[:, :-1] ** 2 + y3[:, 1:] ** 2)
    sqrt_si = np.sqrt(si)
    terms = sqrt_si + sqrt_si * np.sin(50.0 * si ** 0.2) ** 2
    return (np.sum(terms, axis=1) / (N - 1)) ** 2


def ackley_func(
    x: np.ndarray, Os: np.ndarray, M1: np.ndarray, M2: np.ndarray,
    r_flag: int,
    *, M1_T: np.ndarray | None = None, M2_T: np.ndarray | None = None,
) -> np.ndarray:
    """Rotated Ackley (F8 base).  C: lines 403-434.

    Pipeline: shift -> rotate(M1) -> asy(beta=0.5) -> cond(alpha=10) ->
              rotate(M2) -> Ackley formula.

    C formula (line 433): ``f[0] = E - 20.0*exp(sum1) - exp(sum2) + 20.0``
    Uses ``#define E 2.71828...`` which truncates to the same IEEE double
    as ``np.e``.

    XS-01: *M1_T* / *M2_T* are pre-transposed C-contiguous rotation matrices.
    """
    N = x.shape[1]
    y = x - Os
    z = (y @ M1_T if M1_T is not None else y @ M1.T) if r_flag else y.copy()
    y2 = asy_func(z, y, beta=0.5)
    z2 = conditioning(y2, alpha=10.0)
    y3 = (z2 @ M2_T if M2_T is not None else z2 @ M2.T) if r_flag else z2
    if _ackley_nb is not None:
        kernel = _ns.ackley_core_nb if _serial_kernels_active() else _ackley_nb
        return kernel(_ensure_f64(y3))
    s1 = np.einsum('ij,ij->i', y3, y3)
    s2 = np.sum(np.cos(TWO_PI * y3), axis=1)
    return E - 20.0 * np.exp(-0.2 * np.sqrt(s1 / N)) - np.exp(s2 / N) + 20.0


def weierstrass_func(
    x: np.ndarray, Os: np.ndarray, M1: np.ndarray, M2: np.ndarray,
    r_flag: int,
    *, M1_T: np.ndarray | None = None, M2_T: np.ndarray | None = None,
) -> np.ndarray:
    """Rotated Weierstrass (F9 base).  C: lines 437-478.

    Pipeline: shift -> shrink(0.5/100) -> rotate(M1) -> asy(beta=0.5) ->
              cond(alpha=10) -> rotate(M2) -> Weierstrass sum.

    C shrink: ``y[i]*0.5/100`` (line 445).  a=0.5, b=3.0, k_max=20.
    Correction: ``sum2`` in C is recomputed each dim but is independent of
    ``y[i]``, so ``f -= nx*sum2`` matches ``- N * correction``.

    XS-01: *M1_T* / *M2_T* are pre-transposed C-contiguous rotation matrices.
    """
    N = x.shape[1]
    y = (x - Os) * (0.5 / 100.0)
    z = (y @ M1_T if M1_T is not None else y @ M1.T) if r_flag else y.copy()
    y2 = asy_func(z, y, beta=0.5)
    z2 = conditioning(y2, alpha=10.0)
    y3 = (z2 @ M2_T if M2_T is not None else z2 @ M2.T) if r_flag else z2
    if _weierstrass_nb is not None:
        kernel = _ns.weierstrass_core_nb if _serial_kernels_active() else _weierstrass_nb
        return kernel(_ensure_f64(y3), N)
    # NumPy fallback (audit HIGH-PERF-01): accumulate inner k-sum into a
    # running (M,) buffer instead of forming an (M, N, 21) 3D temporary.
    # Identical numerics (sum over k is associative) and identical big-O
    # work, but peak memory drops from O(M*N*K) to O(M*N).
    # M3: use precomputed _WEIER_AK_FB/_WEIER_BK_FB/_WEIER_CORRECTION_FB.
    M = y3.shape[0]
    s = np.zeros(M, dtype=np.float64)
    y3_plus = y3 + 0.5
    for k in range(21):
        s += _WEIER_AK_FB[k] * np.sum(
            np.cos(TWO_PI * _WEIER_BK_FB[k] * y3_plus), axis=1
        )
    return s - N * _WEIER_CORRECTION_FB


def griewank_func(
    x: np.ndarray, Os: np.ndarray, M1: np.ndarray, r_flag: int,
    *, M1_T: np.ndarray | None = None,
) -> np.ndarray:
    """Rotated Griewank (F10 base).  C: lines 481-509.

    Pipeline: shift -> shrink(x6) -> rotate(M1) -> cond(alpha=100) ->
              Griewank formula.

    C shrink: ``y[i]*600.0/100.0`` (line 489).
    C conditioning: ``z[i]*pow(100.0,...)`` (line 498), alpha=100.
    C product term uses ``cos(z[i]/sqrt(1.0+i))`` (0-based i, line 506).

    XS-01: *M1_T* is the pre-transposed C-contiguous rotation matrix.
    """
    N = x.shape[1]
    y = (x - Os) * (600.0 / 100.0)
    z = (y @ M1_T if M1_T is not None else y @ M1.T) if r_flag else y
    z = conditioning(z, alpha=100.0)
    if _griewank_nb is not None:
        kernel = _ns.griewank_core_nb if _serial_kernels_active() else _griewank_nb
        return kernel(_ensure_f64(z))
    s = np.einsum('ij,ij->i', z, z) / 4000.0
    # Audit round-2: cache the per-dimension sqrt vector.
    d = _griewank_sqrt_cache.get(N)
    if d is None:
        with _CACHE_LOCK:
            d = _griewank_sqrt_cache.get(N)
            if d is None:
                d = np.sqrt(1.0 + np.arange(N, dtype=np.float64))
                _griewank_sqrt_cache[N] = d
    return 1.0 + s - np.prod(np.cos(z / d), axis=1)


def rastrigin_func(
    x: np.ndarray, Os: np.ndarray, M1: np.ndarray, M2: np.ndarray,
    r_flag: int,
    *, M1_T: np.ndarray | None = None, M2_T: np.ndarray | None = None,
) -> np.ndarray:
    """Rotated Rastrigin (F11/F12 base).  C: lines 511-551.

    Pipeline: shift -> shrink(5.12/100) -> rotate(M1) -> osz -> asy(beta=0.2)
              -> rotate(M2) -> cond(alpha=10) -> rotate(M1) -> Rastrigin.

    Uses M1 (``Mr``) for both the first rotation (C line 522) and the third
    rotation (C line 542).  M2 uses ``&Mr[nx*nx]`` (C line 531).

    asy buffer semantics (C lines 527-528):
      ``oszfunc(z, y, nx)`` -> osz reads z, writes y.
      ``asyfunc(y, z, nx, beta)`` -> asy reads y (osz output), writes z
      where y>0; where y<=0, z retains its rotated values from line 522.

    XS-01: *M1_T* / *M2_T* are pre-transposed C-contiguous rotation matrices.
    """
    y = (x - Os) * (5.12 / 100.0)
    z = (y @ M1_T if M1_T is not None else y @ M1.T) if r_flag else y.copy()
    y2 = osz_func(z)
    z2 = asy_func(y2, z, beta=0.2)
    y3 = (z2 @ M2_T if M2_T is not None else z2 @ M2.T) if r_flag else z2
    y3 = conditioning(y3, alpha=10.0)
    z3 = (y3 @ M1_T if M1_T is not None else y3 @ M1.T) if r_flag else y3
    if _rastrigin_nb is not None:
        kernel = _ns.rastrigin_core_nb if _serial_kernels_active() else _rastrigin_nb
        return kernel(_ensure_f64(z3))
    return np.sum(z3 ** 2 - 10.0 * np.cos(TWO_PI * z3) + 10.0, axis=1)


def step_rastrigin_func(
    x: np.ndarray, Os: np.ndarray, M1: np.ndarray, M2: np.ndarray,
    r_flag: int,
    *, M1_T: np.ndarray | None = None, M2_T: np.ndarray | None = None,
) -> np.ndarray:
    """Non-continuous Rotated Rastrigin (F13 base).  C: lines 554-601.

    Same as :func:`rastrigin_func` but with a step quantisation after the
    first rotation (C lines 570-574):
    ``if (fabs(z[i])>0.5) z[i]=floor(2*z[i]+0.5)/2;``

    When Numba is available, the quantisation step uses a JIT kernel to
    avoid the overhead of ``np.where`` + ``np.floor`` temporaries.

    XS-01: *M1_T* / *M2_T* are pre-transposed C-contiguous rotation matrices.
    """
    y = (x - Os) * (5.12 / 100.0)
    z = (y @ M1_T if M1_T is not None else y @ M1.T) if r_flag else y.copy()
    # Step quantisation (C lines 570-574)
    if _step_rastrigin_quant_nb is not None:
        quant = (
            _ns.step_rastrigin_quant_nb if _serial_kernels_active()
            else _step_rastrigin_quant_nb
        )
        z = quant(_ensure_f64(z))
    else:
        mask_step = np.abs(z) > 0.5
        z = np.where(mask_step, np.floor(2.0 * z + 0.5) / 2.0, z)
    y2 = osz_func(z)
    z2 = asy_func(y2, z, beta=0.2)
    y3 = (z2 @ M2_T if M2_T is not None else z2 @ M2.T) if r_flag else z2
    y3 = conditioning(y3, alpha=10.0)
    z3 = (y3 @ M1_T if M1_T is not None else y3 @ M1.T) if r_flag else y3
    if _rastrigin_nb is not None:
        kernel = _ns.rastrigin_core_nb if _serial_kernels_active() else _rastrigin_nb
        return kernel(_ensure_f64(z3))
    return np.sum(z3 ** 2 - 10.0 * np.cos(TWO_PI * z3) + 10.0, axis=1)


def schwefel_func(
    x: np.ndarray, Os: np.ndarray, M1: np.ndarray, r_flag: int,
    *, M1_T: np.ndarray | None = None,
) -> np.ndarray:
    """Schwefel (F14/F15 base).  C: lines 603-643.

    Pipeline: shift -> shrink(x10) -> [rotate] -> cond(alpha=10) ->
              shift(+420.97) -> Schwefel formula with boundary handling.

    C shrink: ``y[i]*=1000/100`` (line 611, integer division -> x10).
    C offset: ``z[i]=y[i]+4.209687462275036e+002`` (line 622).
    C constant: ``4.189828872724338e+002*nx`` (line 642).

    Three boundary cases (C lines 627-641):
      z > 500:  penalty + clipped sine term
      z < -500: penalty + clipped sine term (using |z|)
      else:     standard Schwefel formula

    XS-01: *M1_T* is the pre-transposed C-contiguous rotation matrix.
    """
    N = x.shape[1]
    y = (x - Os) * (1000.0 / 100.0)
    z = (y @ M1_T if M1_T is not None else y @ M1.T) if r_flag else y
    y2 = conditioning(z, alpha=10.0)
    z2 = y2 + 4.209687462275036e+002

    if _schwefel_nb is not None:
        kernel = _ns.schwefel_core_nb if _serial_kernels_active() else _schwefel_nb
        return kernel(_ensure_f64(z2), N)

    # NumPy fallback: vectorised boundary handling
    mask_pos = z2 > 500.0
    mask_neg = z2 < -500.0
    mask_mid = ~mask_pos & ~mask_neg
    f = np.zeros(x.shape[0], dtype=np.float64)

    mod_p = np.fmod(z2, 500.0)
    term_p = (500.0 - mod_p) * np.sin(np.sqrt(np.abs(500.0 - mod_p)))
    pen_p = ((z2 - 500.0) / 100.0) ** 2
    f += np.sum(np.where(mask_pos, -term_p + pen_p / N, 0.0), axis=1)

    mod_n = np.fmod(np.abs(z2), 500.0)
    term_n = (-500.0 + mod_n) * np.sin(np.sqrt(np.abs(500.0 - mod_n)))
    pen_n = ((z2 + 500.0) / 100.0) ** 2
    f += np.sum(np.where(mask_neg, -term_n + pen_n / N, 0.0), axis=1)

    f += np.sum(np.where(mask_mid, -z2 * np.sin(np.sqrt(np.abs(z2))), 0.0), axis=1)
    f += 4.189828872724338e+002 * N
    return f


def katsuura_func(
    x: np.ndarray, Os: np.ndarray, M1: np.ndarray, M2: np.ndarray,
    r_flag: int,
    *, M1_T: np.ndarray | None = None, M2_T: np.ndarray | None = None,
) -> np.ndarray:
    """Rotated Katsuura (F16 base).  C: lines 645-685.

    Pipeline: shift -> shrink(5/100) -> rotate(M1) -> cond(alpha=100) ->
              rotate(M2) -> product formula.

    C uses 1-based dimension index: ``(i+1)*temp`` (line 680).
    Inner sum: 32 iterations, j=1..32, ``pow(2.0,j)`` (C line 676).
    Product exponent: ``10.0/pow(nx,1.2)`` (C line 680).

    XS-01: *M1_T* / *M2_T* are pre-transposed C-contiguous rotation matrices.
    """
    N = x.shape[1]
    y = (x - Os) * (5.0 / 100.0)
    z = (y @ M1_T if M1_T is not None else y @ M1.T) if r_flag else y
    z = conditioning(z, alpha=100.0)
    y2 = (z @ M2_T if M2_T is not None else z @ M2.T) if r_flag else z
    if _katsuura_nb is not None:
        kernel = _ns.katsuura_core_nb if _serial_kernels_active() else _katsuura_nb
        return kernel(_ensure_f64(y2), N)
    # NumPy fallback (audit HIGH-PERF-02): accumulate inner j-sum into a
    # running (M, N) buffer instead of forming an (M, N, 32) 3D temporary.
    # Numerics are identical (sum over j is associative); peak memory drops
    # from O(M*N*K) to O(M*N).
    # M3: use precomputed ``_KATSUURA_POW2J_FB`` array.
    M = y2.shape[0]
    tmp3 = N ** 1.2
    temp = np.zeros((M, N), dtype=np.float64)
    for jv in range(32):
        pow2j = _KATSUURA_POW2J_FB[jv]
        v = pow2j * y2
        temp += np.abs(v - np.floor(v + 0.5)) / pow2j
    # Audit round-2: cache the per-dimension index vector.
    idx = _katsuura_idx_cache.get(N)
    if idx is None:
        with _CACHE_LOCK:
            idx = _katsuura_idx_cache.get(N)
            if idx is None:
                idx = np.arange(1, N + 1, dtype=np.float64)
                _katsuura_idx_cache[N] = idx
    factors = (1.0 + idx * temp) ** (10.0 / tmp3)
    tmp1 = 10.0 / N / N
    return np.prod(factors, axis=1) * tmp1 - tmp1


def bi_rastrigin_func(
    x: np.ndarray, Os: np.ndarray, M1: np.ndarray, M2: np.ndarray,
    r_flag: int,
    *, M1_T: np.ndarray | None = None, M2_T: np.ndarray | None = None,
) -> np.ndarray:
    """Lunacek Bi-Rastrigin (F17/F18 base).  C: lines 687-749.

    Pipeline: shift -> shrink(x0.1) -> sign-flip -> rotate(M1) ->
              cond(alpha=100) -> rotate(M2) -> two-funnel formula.

    C sign-flip (lines 702-707): ``tmpx[i]=2*y[i]; if(Os[i]<0) tmpx[i]*=-1``
    C two-funnel: ``min(sum((tmpx-mu0)^2), s*sum((tmpx-mu1)^2)+d*N) + 10*(N-sum(cos(2*pi*z)))``
    where s, mu1 depend on N (lines 693-694).

    XS-01: *M1_T* / *M2_T* are pre-transposed C-contiguous rotation matrices.
    """
    N = x.shape[1]
    mu0, d = 2.5, 1.0
    s = 1.0 - 1.0 / (2.0 * np.sqrt(N + 20.0) - 8.2)
    mu1 = -np.sqrt((mu0 * mu0 - d) / s)

    y = (x - Os) * 0.1
    tmpx = 2.0 * y                    # new array (no copy needed, * creates it)
    tmpx[:, Os < 0.0] *= -1.0        # sign-flip in-place

    z = tmpx.copy()                   # z = pre-mu0 values (for rotation)
    tmpx += mu0                       # in-place add (safe: z has own copy)

    y2 = (z @ M1_T if M1_T is not None else z @ M1.T) if r_flag else z
    y2 = conditioning(y2, alpha=100.0)
    z2 = (y2 @ M2_T if M2_T is not None else y2 @ M2.T) if r_flag else y2

    if _bi_rastrigin_nb is not None:
        kernel = (
            _ns.bi_rastrigin_core_nb if _serial_kernels_active() else _bi_rastrigin_nb
        )
        return kernel(
            _ensure_f64(tmpx), _ensure_f64(z2),
            mu0, mu1, s, d, N,
        )

    tmp1 = np.sum((tmpx - mu0) ** 2, axis=1)
    tmp2 = s * np.sum((tmpx - mu1) ** 2, axis=1) + d * N
    cos_sum = np.sum(np.cos(TWO_PI * z2), axis=1)
    return np.minimum(tmp1, tmp2) + 10.0 * (N - cos_sum)


def grie_rosen_func(
    x: np.ndarray, Os: np.ndarray, M1: np.ndarray, r_flag: int,
    *, M1_T: np.ndarray | None = None,
) -> np.ndarray:
    """Expanded Griewank plus Rosenbrock (F19 base).  C: lines 752-785.

    Pipeline: shift -> shrink(5/100) -> [rotate discarded] -> shift(+1) ->
              circular Rosenbrock -> Griewank chain.

    .. warning::

       **C reference bug deliberately reproduced.**  The reference C
       implementation contains a bug at line 770 of ``test_func.c``::

           z[i] = y[i] + 1.0;   /* should be z[i] = z[i] + 1.0 */

       The intended behaviour is to rotate ``y`` into ``z`` (when
       ``r_flag == 1``) and then add 1.  Instead, the rotation result is
       silently *overwritten* by ``y + 1``, so **the rotation matrix M1
       is effectively a no-op for F19** even when ``r_flag == 1``.
       Compare ``rosenbrock_func`` at C line 361 which correctly uses
       ``z[i] = z[i] + 1.0``.

       This Python port faithfully reproduces the bug because the
       published CEC2013 numbers depend on it.  **Do not "fix" this** --
       a literal-correct implementation would silently diverge from the
       reference benchmark and invalidate every reported result on F19.
       The ``M1`` parameter is therefore accepted but ignored, and the
       function passes ``r_flag`` only for signature symmetry with the
       other ``*_func`` callables.

    Parameters
    ----------
    x : (M, N)
        Population matrix.
    Os : (N,)
        Per-dimension shift vector.
    M1 : (N, N)
        Rotation matrix -- **ignored** (see warning above).
    r_flag : int
        Rotation flag -- **ignored** (see warning above).
    M1_T : (N, N) or None
        Pre-transposed rotation matrix -- **ignored** (see warning above).
        Accepted for signature symmetry with the other ``*_func`` callables.
    """
    y = (x - Os) * (5.0 / 100.0)
    # C bug at test_func.c:770 -- rotation result is overwritten by
    # z[i] = y[i] + 1 (not z[i] + 1), so the rotation is a no-op.  See
    # the docstring warning above; do not "fix" this.
    z = y + 1.0
    if _grie_rosen_nb is not None:
        kernel = _ns.grie_rosen_core_nb if _serial_kernels_active() else _grie_rosen_nb
        return kernel(_ensure_f64(z))
    t1 = z[:, :-1] ** 2 - z[:, 1:]
    t2 = z[:, :-1] - 1.0
    temp_main = 100.0 * t1 ** 2 + t2 ** 2
    f = np.sum(temp_main ** 2 / 4000.0 - np.cos(temp_main) + 1.0, axis=1)
    t1w = z[:, -1] ** 2 - z[:, 0]
    t2w = z[:, -1] - 1.0
    tw = 100.0 * t1w ** 2 + t2w ** 2
    f += tw ** 2 / 4000.0 - np.cos(tw) + 1.0
    return f


def escaffer6_func(
    x: np.ndarray, Os: np.ndarray, M1: np.ndarray, M2: np.ndarray,
    r_flag: int,
    *, M1_T: np.ndarray | None = None, M2_T: np.ndarray | None = None,
) -> np.ndarray:
    """Expanded Scaffer's F6 (F20 base).  C: lines 788-818.

    Pipeline: shift -> rotate(M1) -> asy(beta=0.5) -> rotate(M2) ->
              circular pairwise Scaffer F6 chain.

    Circular wrap: last pair is (z[N-1], z[0]) (C line 814-817).

    XS-01: *M1_T* / *M2_T* are pre-transposed C-contiguous rotation matrices.
    """
    y = x - Os
    z = (y @ M1_T if M1_T is not None else y @ M1.T) if r_flag else y.copy()
    y2 = asy_func(z, y, beta=0.5)
    z2 = (y2 @ M2_T if M2_T is not None else y2 @ M2.T) if r_flag else y2
    if _escaffer6_nb is not None:
        kernel = _ns.escaffer6_core_nb if _serial_kernels_active() else _escaffer6_nb
        return kernel(_ensure_f64(z2))
    z_i, z_ip1 = z2[:, :-1], z2[:, 1:]
    ss = z_i ** 2 + z_ip1 ** 2
    t1 = np.sin(np.sqrt(ss)) ** 2
    t2 = (1.0 + 0.001 * ss) ** 2
    f = np.sum(0.5 + (t1 - 0.5) / t2, axis=1)
    ss_w = z2[:, -1] ** 2 + z2[:, 0] ** 2
    t1w = np.sin(np.sqrt(ss_w)) ** 2
    t2w = (1.0 + 0.001 * ss_w) ** 2
    f += 0.5 + (t1w - 0.5) / t2w
    return f
