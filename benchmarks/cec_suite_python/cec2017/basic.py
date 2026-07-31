"""CEC2017 basic benchmark functions.

Cross-reference: ``cec17_func.cpp`` (Noor Awad, Sep 2016, updated 26 May 2017).
Python implementation verified line-by-line against the compiled reference
implementation (the original IEEE CEC 2017 reference distribution).

All functions take (M, N) batch input, return (M,).
Shrink rates are BAKED IN as the first operation (never passed externally).
No shift/rotate applied here — that's handled by the calling layer.

Shrink rates (matching C++ ``sr_func`` ``sh_rate`` argument):

  ============ ======= ============== ===================================
  Function     Rate    C++ line       Origin shift
  ============ ======= ============== ===================================
  bent_cigar   1.0     518            —
  zakharov     1.0     448            —
  rosenbrock   0.02048 557            +1.0 (z[i] += 1.0, line 558)
  rastrigin    0.0512  651            —
  schaffer_F7  1.0     573            —
  step_rast.   0.0512  669            — (step on y[] lost; see note)
  schwefel     10.0    683            +420.9687462275036 (line 687)
  elliptic     1.0     421            —
  discus       1.0     531            —
  ackley       1.0     590            —
  weierstrass  0.005   612            —
  griewank     6.0     636            —
  katsuura     0.05    714            —
  happycat     0.05    859            −1.0 (z[i] -= 1.0, line 865)
  hgbat        0.05    879            −1.0 (z[i] -= 1.0, line 885)
  egpr         0.05    813            +1.0 (z[0] += 1.0, line 815)
  escaffer6    1.0     836            —
  levy         1.0     466            — (natural min at z=1, NOT z=0)
  bi_rastrigin 0.1     753            — (custom shift/rotate pipeline)
  ============ ======= ============== ===================================

Note on shrink ordering:
  C++ applies shrink BEFORE rotation (inside ``sr_func``).
  Python applies shrink AFTER shift_rotate (inside each base function).
  These are equivalent because scalar × rotation = rotation × scalar
  (rotation is a linear operator, so ``α·(v @ R.T) = (α·v) @ R.T``).

When numba is available, the hot functions dispatch to JIT-compiled kernels
in this suite's ``_numba.py`` (19 kernels, all verified to agree with NumPy
paths).

Coercion policy
~~~~~~~~~~~~~~~
Every JIT entry point wraps its input in ``np.ascontiguousarray(x,
dtype=np.float64)`` before calling the kernel.  Audit M-1 flagged this
as redundant on the belief that ``cec2017/functions.py`` (the
dispatcher) already normalises the top-level population.  That's true
for the F1-F10 *simple* path, but **not** for F11-F30: the hybrid
layer in ``cec2017/hybrid.py`` calls ``transforms.shuffle_and_partition``,
which applies ``np.split`` along the column axis and returns
stride-only *views* (not copies).  Passing a non-contiguous view to a
Numba kernel would force a second layout specialisation (slower
strided access) and double the JIT warmup cost.  The per-function
``np.ascontiguousarray`` here is therefore **intentional** — it's a
no-op on the F1-F10 hot path (array is already C-contiguous and
``float64``) and a necessary copy on the F11-F30 path.  Do not
remove.
"""

from __future__ import annotations

import numpy as np

PI = np.pi
TWO_PI = 2.0 * PI
E = np.e

# Numba-accelerated kernels (graceful fallback).  The kernels live in this
# suite's own ``_numba.py`` module.
try:
    from ._numba import (
        rastrigin_nb as _rastrigin_nb,
        zakharov_nb as _zakharov_nb,
        rosenbrock_nb as _rosenbrock_nb,
        bent_cigar_nb as _bent_cigar_nb,
        bent_cigar_strict_nb as _bent_cigar_strict_nb,
        levy_nb as _levy_nb,
        step_rastrigin_nb as _step_rastrigin_nb,
        schwefel_nb as _schwefel_nb,
        elliptic_nb as _elliptic_nb,
        discus_nb as _discus_nb,
        ackley_nb as _ackley_nb,
        weierstrass_nb as _weierstrass_nb,
        griewank_nb as _griewank_nb,
        katsuura_nb as _katsuura_nb,
        happycat_nb as _happycat_nb,
        hgbat_nb as _hgbat_nb,
        schaffer_F7_nb as _schaffer_F7_nb,
        bi_rastrigin_nb as _bi_rastrigin_nb,
        egpr_nb as _egpr_nb,
        esf6_nb as _esf6_nb,
    )
except ImportError:
    _rastrigin_nb = None; _zakharov_nb = None; _rosenbrock_nb = None
    _bent_cigar_nb = None; _bent_cigar_strict_nb = None; _levy_nb = None; _step_rastrigin_nb = None
    _schwefel_nb = None; _elliptic_nb = None; _discus_nb = None
    _ackley_nb = None; _weierstrass_nb = None; _griewank_nb = None
    _katsuura_nb = None; _happycat_nb = None; _hgbat_nb = None
    _schaffer_F7_nb = None; _bi_rastrigin_nb = None
    _egpr_nb = None; _esf6_nb = None

# Serial (parallel=False) twins of the same kernels plus the thread-local flag
# that routes an opted-in optimizer's evaluations to them.  Originally motivated
# by member-sequential optimizers (toa/saro/moa-mother/ema), whose single-row
# dispatches pay ~60 us of parallel-runtime launch per kernel call at
# numba_threads=1; since the 2026-07-17 un-freeze the campaign allowlist
# routes ALL 24 optimizers here.  The twins run the same math in ~0.4 us (see
# _numba_serial.py).  Outside a serial_kernel_scope() every call site below
# takes the batch-kernel branch unchanged (one thread-local read of overhead,
# no floating-point change), so flag-off problems and the FP-regime
# sentinel are untouched.
try:
    from . import _numba_serial as _ns
    from ._kernel_mode import serial_kernels_active as _serial_kernels_active
except ImportError:
    _ns = None

    def _serial_kernels_active() -> bool:
        return False

# XS-02: Per-dimension coefficient caches for NumPy fallback paths.
# Avoids recomputing O(N) vectors on every NFE.  Thread-safe because
# dict reads are atomic in CPython and the worst-case duplicate write
# produces the same value.
_zakharov_coeff_cache: dict[int, np.ndarray] = {}   # N -> 0.5*arange(1,N+1)
_elliptic_coeff_cache: dict[int, np.ndarray] = {}   # N -> 10^(6*j/(N-1))
_griewank_coeff_cache: dict[int, np.ndarray] = {}   # N -> sqrt(1+arange(N))

# M1: Precomputed coefficients for Weierstrass/Katsuura NumPy fallback paths.
# Avoids recomputing power sequences (a^k, b^k, 2^j) on every NFE when Numba
# is unavailable.  The Numba kernels in ``_numba.py`` have their own module-
# level constants (``_WEIER_AK`` etc.); these are independent so the fallback
# works even when Numba is not installed.
_WEIER_AK_FB = np.array([0.5 ** k for k in range(21)], dtype=np.float64)
_WEIER_BK_FB = np.array([3.0 ** k for k in range(21)], dtype=np.float64)
_WEIER_OFFSETS_FB = PI * _WEIER_BK_FB                # π·b^k  (= 2π·b^k·0.5)
_WEIER_CORRECTION_FB = float(np.sum(_WEIER_AK_FB * np.cos(_WEIER_OFFSETS_FB)))

_KATSUURA_POW2J_FB = np.array([2.0 ** (j + 1) for j in range(32)], dtype=np.float64)


# ============================================================
# Unimodal
# ============================================================

def _bent_cigar_strict_numpy(x: np.ndarray) -> np.ndarray:
    """Strict fallback for Bent Cigar: fixed row-major, left-to-right sum."""
    arr = np.ascontiguousarray(x, dtype=np.float64)
    out = np.empty(arr.shape[0], dtype=np.float64)
    for i in range(arr.shape[0]):
        s = float(arr[i, 0] * arr[i, 0])
        for j in range(1, arr.shape[1]):
            s = s + float(1e6 * arr[i, j] * arr[i, j])
        out[i] = s
    return out


def bent_cigar(x: np.ndarray, *, strict: bool = False) -> np.ndarray:
    """F1 base. No shrink (rate=1.0). f = x0² + 1e6 * Σ(xi²)."""
    if strict:
        if _bent_cigar_strict_nb is not None:
            kernel = _ns.bent_cigar_strict_nb if _serial_kernels_active() else _bent_cigar_strict_nb
            return kernel(np.ascontiguousarray(x, dtype=np.float64))
        return _bent_cigar_strict_numpy(x)
    if _bent_cigar_nb is not None:
        kernel = _ns.bent_cigar_nb if _serial_kernels_active() else _bent_cigar_nb
        return kernel(np.ascontiguousarray(x, dtype=np.float64))
    # Audit CEC2017-M3: coerce to float64 so the NumPy fallback matches
    # the JIT path for float32 inputs (NEP 50 weak-typing preserves
    # float32 across `array * python_scalar`, which would break
    # Numba <-> NumPy bit parity).
    x = np.ascontiguousarray(x, dtype=np.float64)
    return x[:, 0] ** 2 + 1e6 * np.sum(x[:, 1:] ** 2, axis=1)


def sum_diff_pow(x: np.ndarray) -> np.ndarray:
    """F2 base (deprecated). No shrink. f = Σ|xi|^(i+1).

    .. deprecated:: 0.1.0
        Numerically unstable; excluded from CEC2017 competition results.
    """
    import warnings
    warnings.warn(
        "sum_diff_pow (F2) is deprecated and numerically unstable. "
        "It was excluded from CEC2017 competition results.",
        DeprecationWarning,
        stacklevel=2,
    )
    M, N = x.shape
    exponents = np.arange(1, N + 1, dtype=np.float64)  # 1-indexed: i+1
    return np.sum(np.abs(x) ** exponents, axis=1)


def zakharov(x: np.ndarray) -> np.ndarray:
    """F3 base. No shrink. f = Σxi² + (0.5*Σ(i+1)*xi)² + (0.5*Σ(i+1)*xi)⁴."""
    if _zakharov_nb is not None:
        kernel = _ns.zakharov_nb if _serial_kernels_active() else _zakharov_nb
        return kernel(np.ascontiguousarray(x, dtype=np.float64))
    x = np.ascontiguousarray(x, dtype=np.float64)  # CEC2017-M3 fallback coercion
    M, N = x.shape
    idx = _zakharov_coeff_cache.get(N)
    if idx is None:
        idx = 0.5 * np.arange(1, N + 1, dtype=np.float64)  # 0.5*(i+1)
        _zakharov_coeff_cache[N] = idx
    s1 = np.sum(x ** 2, axis=1)
    s2 = np.sum(idx * x, axis=1)
    return s1 + s2 ** 2 + s2 ** 4


# ============================================================
# Multimodal
# ============================================================

def rosenbrock(x: np.ndarray) -> np.ndarray:
    """Shrink 2.048/100 + origin shift +1."""
    if _rosenbrock_nb is not None:
        kernel = _ns.rosenbrock_nb if _serial_kernels_active() else _rosenbrock_nb
        return kernel(np.ascontiguousarray(x, dtype=np.float64))
    x = np.ascontiguousarray(x, dtype=np.float64)  # CEC2017-M3 fallback coercion
    x = 0.02048 * x + 1.0
    t1 = x[:, :-1] ** 2 - x[:, 1:]
    t2 = x[:, :-1] - 1.0
    return np.sum(100.0 * t1 ** 2 + t2 ** 2, axis=1)


def rastrigin(x: np.ndarray) -> np.ndarray:
    """Shrink 5.12/100."""
    if _rastrigin_nb is not None:
        kernel = _ns.rastrigin_nb if _serial_kernels_active() else _rastrigin_nb
        return kernel(np.ascontiguousarray(x, dtype=np.float64))
    x = np.ascontiguousarray(x, dtype=np.float64)  # CEC2017-M3 fallback coercion
    x = 0.0512 * x
    return np.sum(x ** 2 - 10.0 * np.cos(TWO_PI * x) + 10.0, axis=1)


def schaffer_F7(x: np.ndarray) -> np.ndarray:
    """Standalone Schaffer F7. No shrink (rate=1.0)."""
    if _schaffer_F7_nb is not None:
        kernel = _ns.schaffer_F7_nb if _serial_kernels_active() else _schaffer_F7_nb
        return kernel(np.ascontiguousarray(x, dtype=np.float64))
    x = np.ascontiguousarray(x, dtype=np.float64)  # CEC2017-M3 fallback coercion
    N = x.shape[1]
    if N < 2:
        return np.zeros(x.shape[0])
    # CEC17-B03: avoid intermediate si allocation. Compute sqrt_si and
    # si^0.2 directly from the raw sum-of-squares.
    _raw = x[:, :-1] ** 2 + x[:, 1:] ** 2          # (M, N-1)
    sqrt_si = _raw ** 0.25                           # (a²+b²)^0.25 = sqrt(sqrt(a²+b²)) = sqrt(si)
    terms = sqrt_si + sqrt_si * np.sin(50.0 * _raw ** 0.1) ** 2  # _raw^0.1 = si^0.2
    s = np.sum(terms, axis=1)
    return (s / (N - 1)) ** 2


# Alias used by the hybrid layer for identity checks
# (hybrid._hybrid_eval tests `func is basic.schaffer_F7_inner` to trigger
# the C++ buffer-bug emulation path). Mathematically identical to schaffer_F7.
schaffer_F7_inner = schaffer_F7


def bi_rastrigin(
                 x: np.ndarray,
                 shift: np.ndarray | None = None,
                 rotation: np.ndarray | None = None,
                 apply_shift: bool = True,
                 rotation_T: np.ndarray | None = None,
) -> np.ndarray:
    """Lunacek Bi-Rastrigin. Custom shift/rotate logic.

    Parameters
    ----------
    x : (M, N) raw input
    shift : (>=N,) shift vector (needed for sign-flip even when apply_shift=False)
    rotation : (N, N) or None
    apply_shift : bool — True for standalone, False for hybrid context

    Note
    ----
    Requires N >= 2. At N=1 the formula produces s < 0, making
    sqrt((mu0^2 - d)/s) undefined. N=1 is never reached through validated
    entry points (minimum benchmark dimension is D=10), but a direct call
    with N<2 is treated as a programming error and raises ValueError --
    silently substituting the sphere function would mask the misuse and
    poison downstream benchmark results.
    """
    M, N = x.shape
    if N < 2:
        raise ValueError(
            f"bi_rastrigin requires N >= 2 (got N={N}); the formula "
            f"sqrt((mu0^2 - d)/s) is undefined for N=1.  This function is "
            f"not callable on D=1 problems."
        )

    if _bi_rastrigin_nb is not None:
        s = shift if shift is not None else np.zeros(max(N, 1))
        r = rotation
        kernel = _ns.bi_rastrigin_nb if _serial_kernels_active() else _bi_rastrigin_nb
        return kernel(np.ascontiguousarray(x, dtype=np.float64),
                      np.ascontiguousarray(s[:N], dtype=np.float64),
                      r, bool(apply_shift))

    # CEC2017-M3 fallback coercion: make the NumPy path bit-parity
    # equivalent to the JIT path for float32 callers.  Both x and
    # shift/rotation must be coerced to float64 because NEP 50 weak-
    # typing would otherwise let a float32 x collapse the whole
    # arithmetic chain back to float32.
    x = np.ascontiguousarray(x, dtype=np.float64)
    if shift is not None:
        shift = np.ascontiguousarray(shift, dtype=np.float64)
    if rotation is not None:
        rotation = np.ascontiguousarray(rotation, dtype=np.float64)

    mu0 = 2.5
    d = 1.0
    s = 1.0 - 1.0 / (2.0 * np.sqrt(N + 20.0) - 8.2)
    mu1 = -np.sqrt((mu0 * mu0 - d) / s)

    if apply_shift and shift is not None:
        y = x - shift[:N]
    else:
        y = x.copy()

    # Shrink: 10/100 = 0.1
    y = y * 0.1

    # tmpx = 2*y, sign-flipped where shift < 0
    tmpx = 2.0 * y
    if shift is not None:
        sign_mask = shift[:N] < 0.0
        tmpx[:, sign_mask] *= -1.0

    # z for rotation = tmpx (before adding mu0)
    z = tmpx.copy()
    tmpx = tmpx + mu0

    # Two sums
    tmp1 = np.sum(z ** 2, axis=1)
    tmp2 = np.sum((tmpx - mu1) ** 2, axis=1)
    tmp2 = s * tmp2 + d * N

    # Rotation applied to z
    # XS-01: use pre-transposed C-contiguous rotation_T when available.
    if rotation is not None:
        zr = z @ rotation_T if rotation_T is not None else z @ rotation.T
    else:
        zr = z

    cos_sum = np.sum(np.cos(TWO_PI * zr), axis=1)
    f = np.minimum(tmp1, tmp2) + 10.0 * (N - cos_sum)
    return f


def step_rastrigin(x: np.ndarray) -> np.ndarray:
    """Step Rastrigin / Non-continuous Rastrigin.

    NOTE: In the compiled reference, step_rastrigin_func modifies y[] before sr_func,
    but sr_func overwrites y[] via shiftfunc. The step modification is LOST.
    F8 effectively reduces to plain rastrigin with different shift/rotation data.

    This implementation matches the compiled reference behavior (step lost).
    """
    if _step_rastrigin_nb is not None:
        kernel = _ns.step_rastrigin_nb if _serial_kernels_active() else _step_rastrigin_nb
        return kernel(np.ascontiguousarray(x, dtype=np.float64))
    x = np.ascontiguousarray(x, dtype=np.float64)  # CEC2017-M3 fallback coercion
    # Identical to rastrigin — step is lost in compiled reference
    x = 0.0512 * x
    return np.sum(x ** 2 - 10.0 * np.cos(TWO_PI * x) + 10.0, axis=1)


def schwefel(x: np.ndarray) -> np.ndarray:
    """Shrink 1000/100 = 10.0."""
    if _schwefel_nb is not None:
        kernel = _ns.schwefel_nb if _serial_kernels_active() else _schwefel_nb
        return kernel(np.ascontiguousarray(x, dtype=np.float64))
    x = np.ascontiguousarray(x, dtype=np.float64)  # CEC2017-M3 fallback coercion
    x = 10.0 * x
    M, N = x.shape
    x = x + 420.9687462275036

    # Three branches merged into a single np.sum to reduce intermediate
    # reductions and improve cache locality (audit round-2, finding 1).
    mask_pos = x > 500.0
    mask_neg = x < -500.0
    mask_mid = ~mask_pos & ~mask_neg

    # Branch 1: z > 500
    mod_pos = np.fmod(x, 500.0)
    term_pos = (500.0 - mod_pos) * np.sin(np.sqrt(np.abs(500.0 - mod_pos)))
    pen_pos = ((x - 500.0) / 100.0) ** 2

    # Branch 2: z < -500
    mod_neg = np.fmod(np.abs(x), 500.0)
    term_neg = (-500.0 + mod_neg) * np.sin(np.sqrt(np.abs(500.0 - mod_neg)))
    pen_neg = ((x + 500.0) / 100.0) ** 2

    # Single reduction over all three branches
    f = np.sum(
        np.where(mask_pos, -term_pos + pen_pos / N, 0.0)
        + np.where(mask_neg, -term_neg + pen_neg / N, 0.0)
        + np.where(mask_mid, -x * np.sin(np.sqrt(np.abs(x))), 0.0),
        axis=1,
    )

    f += 418.9828872724338 * N
    return f


def elliptic(x: np.ndarray) -> np.ndarray:
    """Ellipsoidal. No shrink (rate=1.0)."""
    if _elliptic_nb is not None:
        kernel = _ns.elliptic_nb if _serial_kernels_active() else _elliptic_nb
        return kernel(np.ascontiguousarray(x, dtype=np.float64))
    x = np.ascontiguousarray(x, dtype=np.float64)  # CEC2017-M3 fallback coercion
    M, N = x.shape
    if N == 1:
        return x[:, 0] ** 2
    coeff = _elliptic_coeff_cache.get(N)
    if coeff is None:
        exponents = 6.0 * np.arange(N, dtype=np.float64) / (N - 1)
        coeff = 10.0 ** exponents
        _elliptic_coeff_cache[N] = coeff
    return np.sum(coeff * x ** 2, axis=1)


def discus(x: np.ndarray) -> np.ndarray:
    """Discus. No shrink (rate=1.0)."""
    if _discus_nb is not None:
        kernel = _ns.discus_nb if _serial_kernels_active() else _discus_nb
        return kernel(np.ascontiguousarray(x, dtype=np.float64))
    x = np.ascontiguousarray(x, dtype=np.float64)  # CEC2017-M3 fallback coercion
    return 1e6 * x[:, 0] ** 2 + np.sum(x[:, 1:] ** 2, axis=1)


def ackley(x: np.ndarray) -> np.ndarray:
    """Ackley. No shrink (rate=1.0)."""
    if _ackley_nb is not None:
        kernel = _ns.ackley_nb if _serial_kernels_active() else _ackley_nb
        return kernel(np.ascontiguousarray(x, dtype=np.float64))
    x = np.ascontiguousarray(x, dtype=np.float64)  # CEC2017-M3 fallback coercion
    M, N = x.shape
    s1 = np.sum(x ** 2, axis=1)
    s2 = np.sum(np.cos(2.0 * PI * x), axis=1)
    return E - 20.0 * np.exp(-0.2 * np.sqrt(s1 / N)) - np.exp(s2 / N) + 20.0


def weierstrass(x: np.ndarray) -> np.ndarray:
    """Shrink 0.5/100 = 0.005.

    Audit fix (cross M-04): the previous broadcast formed an (M, N, 21)
    temporary that could spike to ~16 MB at M=N=100.  We accumulate the
    inner k-sum into a running (M,) buffer instead -- 21 small (M, N)
    intermediates rather than a single 3D temp.  Identical numerics
    (the sum over k is associative) and identical big-O work, but peak
    memory drops from O(M*N*K) to O(M*N).
    """
    if _weierstrass_nb is not None:
        kernel = _ns.weierstrass_nb if _serial_kernels_active() else _weierstrass_nb
        return kernel(np.ascontiguousarray(x, dtype=np.float64))
    x = np.ascontiguousarray(x, dtype=np.float64)  # CEC2017-M3 fallback coercion
    x = 0.005 * x
    M, N = x.shape
    s = np.zeros(M, dtype=np.float64)
    # M1: use precomputed coefficient arrays instead of recomputing a^k, b^k,
    # and π·b^k on every call.  CEC17-B05 offset trick is preserved.
    # B1: TWO_PI hoisted to module-level constant.
    for k in range(21):
        s += _WEIER_AK_FB[k] * np.sum(
            np.cos(TWO_PI * _WEIER_BK_FB[k] * x + _WEIER_OFFSETS_FB[k]),
            axis=1,
        )
    return s - N * _WEIER_CORRECTION_FB


def griewank(x: np.ndarray) -> np.ndarray:
    """Shrink 600/100 = 6.0."""
    if _griewank_nb is not None:
        kernel = _ns.griewank_nb if _serial_kernels_active() else _griewank_nb
        return kernel(np.ascontiguousarray(x, dtype=np.float64))
    x = np.ascontiguousarray(x, dtype=np.float64)  # CEC2017-M3 fallback coercion
    x = 6.0 * x
    M, N = x.shape
    s = np.sum(x ** 2, axis=1) / 4000.0
    d = _griewank_coeff_cache.get(N)
    if d is None:
        d = np.sqrt(1.0 + np.arange(N, dtype=np.float64))  # sqrt(1+i), i from 0
        _griewank_coeff_cache[N] = d
    p = np.prod(np.cos(x / d), axis=1)
    return 1.0 + s - p


def katsuura(x: np.ndarray) -> np.ndarray:
    """Shrink 5/100 = 0.05.

    Audit fix (cross M-04): the original broadcast formed an (M, N, 32)
    temp that could spike to ~25 MB at M=N=100.  The previous fix cut
    that to an (M, N) accumulator.  This version streams one column at a
    time and keeps only O(M) temporaries alive, preserving the exact
    arithmetic order of the inner j-sum for every dimension.
    """
    if _katsuura_nb is not None:
        kernel = _ns.katsuura_nb if _serial_kernels_active() else _katsuura_nb
        return kernel(np.ascontiguousarray(x, dtype=np.float64))
    x = np.ascontiguousarray(x, dtype=np.float64)  # CEC2017-M3 fallback coercion
    x = 0.05 * x
    M, N = x.shape
    tmp3 = N ** 1.2
    prod_val = np.ones(M, dtype=np.float64)
    temp_col = np.empty(M, dtype=np.float64)  # B2: empty — zeroed inside inner loop
    exponent = 10.0 / tmp3
    # M1: use precomputed ``_KATSUURA_POW2J_FB`` array instead of
    # recomputing ``2.0 ** jv`` on every inner iteration.
    for dim_idx in range(N):
        temp_col[:] = 0.0
        x_col = x[:, dim_idx]
        for jv in range(32):
            pow2j = _KATSUURA_POW2J_FB[jv]
            v = pow2j * x_col
            temp_col += np.abs(v - np.floor(v + 0.5)) / pow2j
        prod_val *= (1.0 + float(dim_idx + 1) * temp_col) ** exponent
    tmp1 = 10.0 / N / N
    return prod_val * tmp1 - tmp1


def happycat(x: np.ndarray) -> np.ndarray:
    """Shrink 5/100 = 0.05, then subtract 1."""
    if _happycat_nb is not None:
        kernel = _ns.happycat_nb if _serial_kernels_active() else _happycat_nb
        return kernel(np.ascontiguousarray(x, dtype=np.float64))
    x = np.ascontiguousarray(x, dtype=np.float64)  # CEC2017-M3 fallback coercion
    x = 0.05 * x - 1.0
    M, N = x.shape
    r2 = np.sum(x ** 2, axis=1)
    sum_z = np.sum(x, axis=1)
    return np.abs(r2 - N) ** 0.25 + (0.5 * r2 + sum_z) / N + 0.5


def hgbat(x: np.ndarray) -> np.ndarray:
    """Shrink 5/100 = 0.05, then subtract 1."""
    if _hgbat_nb is not None:
        kernel = _ns.hgbat_nb if _serial_kernels_active() else _hgbat_nb
        return kernel(np.ascontiguousarray(x, dtype=np.float64))
    x = np.ascontiguousarray(x, dtype=np.float64)  # CEC2017-M3 fallback coercion
    x = 0.05 * x - 1.0
    M, N = x.shape
    r2 = np.sum(x ** 2, axis=1)
    sum_z = np.sum(x, axis=1)
    return np.abs(r2 ** 2 - sum_z ** 2) ** 0.5 + (0.5 * r2 + sum_z) / N + 0.5


def expanded_griewanks_plus_rosenbrock(x: np.ndarray) -> np.ndarray:
    """Shrink 5/100 = 0.05, then add 1."""
    if _egpr_nb is not None:
        kernel = _ns.egpr_nb if _serial_kernels_active() else _egpr_nb
        return kernel(np.ascontiguousarray(x, dtype=np.float64))
    x = np.ascontiguousarray(x, dtype=np.float64)  # CEC2017-M3 fallback coercion
    x = 0.05 * x + 1.0
    M, N = x.shape
    # Rosenbrock pairs: (x_i, x_{i+1}) for i=0..N-2, then wrap (x_{N-1}, x_0)
    # Main pairs
    x_i = x[:, :-1]
    x_ip1 = x[:, 1:]
    tmp1 = x_i ** 2 - x_ip1
    tmp2 = x_i - 1.0
    temp_main = 100.0 * tmp1 ** 2 + tmp2 ** 2
    grie_main = temp_main ** 2 / 4000.0 - np.cos(temp_main) + 1.0
    # Sum main pairs FIRST
    f = np.sum(grie_main, axis=1)
    # Wrap-around pair: (x_{N-1}, x_0)
    tmp1_w = x[:, -1] ** 2 - x[:, 0]
    tmp2_w = x[:, -1] - 1.0
    temp_w = 100.0 * tmp1_w ** 2 + tmp2_w ** 2
    grie_w = temp_w ** 2 / 4000.0 - np.cos(temp_w) + 1.0
    # Add wrap ONCE
    f += grie_w
    return f


def expanded_schaffers_f6(x: np.ndarray) -> np.ndarray:
    """No shrink (rate=1.0)."""
    if _esf6_nb is not None:
        kernel = _ns.esf6_nb if _serial_kernels_active() else _esf6_nb
        return kernel(np.ascontiguousarray(x, dtype=np.float64))
    x = np.ascontiguousarray(x, dtype=np.float64)  # CEC2017-M3 fallback coercion
    M, N = x.shape
    # Main pairs
    x_i = x[:, :-1]
    x_ip1 = x[:, 1:]
    ss = x_i ** 2 + x_ip1 ** 2
    temp1 = np.sin(np.sqrt(ss)) ** 2
    temp2 = (1.0 + 0.001 * ss) ** 2
    main = 0.5 + (temp1 - 0.5) / temp2
    # Sum main FIRST
    f = np.sum(main, axis=1)
    # Wrap-around: (x_{N-1}, x_0)
    ss_w = x[:, -1] ** 2 + x[:, 0] ** 2
    temp1_w = np.sin(np.sqrt(ss_w)) ** 2
    temp2_w = (1.0 + 0.001 * ss_w) ** 2
    wrap = 0.5 + (temp1_w - 0.5) / temp2_w
    f += wrap
    return f


def levy(x: np.ndarray) -> np.ndarray:
    """Levy function. No shrink despite definition (C++ omits 5.12/100 scaling)."""
    if _levy_nb is not None:
        kernel = _ns.levy_nb if _serial_kernels_active() else _levy_nb
        return kernel(np.ascontiguousarray(x, dtype=np.float64))
    x = np.ascontiguousarray(x, dtype=np.float64)  # CEC2017-M3 fallback coercion
    M, N = x.shape
    w = 1.0 + (x - 1.0) / 4.0  # w = 1 + 0.25*(x-1)
    term1 = np.sin(PI * w[:, 0]) ** 2
    term3 = (w[:, -1] - 1.0) ** 2 * (1.0 + np.sin(2.0 * PI * w[:, -1]) ** 2)
    wi = w[:, :-1]
    inner = (wi - 1.0) ** 2 * (1.0 + 10.0 * np.sin(PI * wi + 1.0) ** 2)
    s = np.sum(inner, axis=1)
    return term1 + s + term3
