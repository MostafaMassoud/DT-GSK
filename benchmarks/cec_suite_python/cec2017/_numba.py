"""CEC2017 Numba-accelerated kernels.

This module holds every JIT kernel used exclusively by the CEC2017 benchmark
suite -- the 19 base-function kernels (plus the strict fixed-order twins
backing ``benchmark_fp_mode='strict'``), the shift/rotate transforms, and
the composition weight calculator.  It mirrors the architecture of
:mod:`benchmarks.cec_suite_python.cec2013._numba` and
:mod:`benchmarks.cec_suite_python.cec2011._numba`: each suite owns its own
``_numba.py`` file so that it can be dropped in or out without touching the
optimizers' own code under ``src/gsk_family/optimizers/``.

Kernel table
~~~~~~~~~~~~
========================= =================================================
Kernel                    Purpose
========================= =================================================
rastrigin_nb              Rastrigin with 0.0512 shrink
zakharov_nb               Zakharov
rosenbrock_nb             Rosenbrock with 0.02048 shrink + origin shift
bent_cigar_nb             Bent cigar
levy_nb                   Levy
step_rastrigin_nb         Step Rastrigin with 0.0512 shrink
schwefel_nb               Schwefel with boundary correction
elliptic_nb               High-conditioned Elliptic
discus_nb                 Discus
ackley_nb                 Ackley
weierstrass_nb            Weierstrass with 0.005 shrink
griewank_nb               Griewank with 6.0 shrink
katsuura_nb               Katsuura with 0.05 shrink
happycat_nb               HappyCat with 0.05 shrink and -1 shift
hgbat_nb                  HGBat with 0.05 shrink and -1 shift
schaffer_F7_nb            Schaffer F7
bi_rastrigin_nb           Lunacek Bi-Rastrigin (takes shift/rotation)
egpr_nb                   Expanded Griewank plus Rosenbrock (F11)
esf6_nb                   Expanded Schaffer F6 (F12)
_shift_only_nb            helper: subtract shift vector per row
shift_rotate_fast         Python wrapper for shift+rotate transform
bent_cigar_strict_nb      Bent cigar, fixed-order/non-fastmath (strict FP)
_shift_only_strict_nb     helper: shift subtract, strict FP twin
_shift_rotate_strict_nb   shift+rotate, strict FP twin
shift_rotate_strict_fast  Python wrapper for the strict transform
_cf_cal_nb / cf_cal_fast  distance-weighted composition weights
========================= =================================================

All kernels expect C-contiguous ``float64`` input.  Outer loops over the
population dimension (``M``) are parallelised with ``prange``; inner loops
over ``N`` are sequential since they accumulate into a single reduction.

Decorator policy
~~~~~~~~~~~~~~~~
Every parallel kernel uses the project's canonical decorator::

    @njit(cache=True, parallel=True, fastmath=True, boundscheck=False, nogil=True)

inherited from the ancestor project's ``gsk/_numba_accel.py``.
``fastmath=True`` is safe for the basic
function kernels: each one does straight arithmetic over finite ``float64``
populations and never touches NaN/Inf semantics, and the parallelisation
slices the population by row so there is no cross-thread reduction.

Four kernels drop ``fastmath``.  The composition weight kernel
``_cf_cal_nb`` (audit finding Pattern A) does so to keep the published
composition-function numbers (F21-F30) bit-for-bit reproducible across
CPU ISAs and Numba/LLVM versions -- see the comment block immediately
above ``_cf_cal_nb`` for the full rationale.  The strict fixed-order
kernels ``bent_cigar_strict_nb``, ``_shift_only_strict_nb`` and
``_shift_rotate_strict_nb`` (backing ``benchmark_fp_mode='strict'`` via
``transforms.py``/``basic.py``) do so to guarantee a fixed left-to-right
evaluation order.

``boundscheck=False`` and ``nogil=True`` are required on every kernel to
release the GIL inside ``ProcessPoolExecutor`` workers without contention.
"""

from __future__ import annotations

import numpy as np

try:
    from numba import njit, prange  # type: ignore[import-untyped]
    HAS_NUMBA = True
except Exception:  # not just ImportError: llvmlite can raise OSError under memory pressure
    HAS_NUMBA = False

PI = np.pi

# ---------------------------------------------------------------------------
# AUDIT-31: precomputed constant arrays for weierstrass_nb / katsuura_nb.
#
# These arrays are invariant across calls (pure functions of fixed
# parameters a=0.5, b=3, k_max=20 for Weierstrass; 32 powers of 2 for
# Katsuura).  Hoisting them to module level avoids recomputing ~53 float64
# values per kernel invocation and lets Numba embed them as compile-time
# constants in the LLVM IR.  Thread-safe: the arrays are computed once at
# import time and are read-only thereafter.
# ---------------------------------------------------------------------------
_WEIER_K_MAX = 20
_WEIER_AK = np.array([0.5 ** k for k in range(_WEIER_K_MAX + 1)], dtype=np.float64)
_WEIER_BK = np.array([3.0 ** k for k in range(_WEIER_K_MAX + 1)], dtype=np.float64)
_WEIER_CORRECTION = float(np.sum(_WEIER_AK * np.cos(2.0 * PI * _WEIER_BK * 0.5)))

_KATSUURA_POW2J = np.array([2.0 ** (j + 1) for j in range(32)], dtype=np.float64)


# ===========================================================================
# JIT kernels (single big if HAS_NUMBA: / else: block)
# ===========================================================================
if HAS_NUMBA:

    # ----- Base functions 1: rastrigin / zakharov / rosenbrock --------------

    @njit(cache=True, parallel=True, fastmath=True, boundscheck=False, nogil=True)
    def rastrigin_nb(x):
        """Rastrigin function with baked-in 0.0512 shrink factor.

        Parameters
        ----------
        x : ndarray, shape (M, N) -- population matrix
        """
        M, N = x.shape
        out = np.empty(M)
        for i in prange(M):
            s = 0.0
            for j in range(N):
                xj = 0.0512 * x[i, j]
                s += xj * xj - 10.0 * np.cos(2.0 * PI * xj) + 10.0
            out[i] = s
        return out

    @njit(cache=True, parallel=True, fastmath=True, boundscheck=False, nogil=True)
    def zakharov_nb(x):
        """Zakharov function.

        Parameters
        ----------
        x : ndarray, shape (M, N) -- population matrix
        """
        M, N = x.shape
        out = np.empty(M)
        for i in prange(M):
            s1 = 0.0
            s2 = 0.0
            for j in range(N):
                s1 += x[i, j] * x[i, j]
                s2 += 0.5 * (j + 1) * x[i, j]
            out[i] = s1 + s2 * s2 + s2 * s2 * s2 * s2
        return out

    @njit(cache=True, parallel=True, fastmath=True, boundscheck=False, nogil=True)
    def rosenbrock_nb(x):
        """Rosenbrock function with baked-in 0.02048 shrink and +1 shift.

        Parameters
        ----------
        x : ndarray, shape (M, N) -- population matrix
        """
        M, N = x.shape
        out = np.empty(M)
        for i in prange(M):
            s = 0.0
            for j in range(N - 1):
                xj = 0.02048 * x[i, j] + 1.0
                xj1 = 0.02048 * x[i, j + 1] + 1.0
                t1 = xj * xj - xj1
                t2 = xj - 1.0
                s += 100.0 * t1 * t1 + t2 * t2
            out[i] = s
        return out

    @njit(cache=True, parallel=True, fastmath=True, boundscheck=False, nogil=True)
    def bent_cigar_nb(x):
        """Bent Cigar function.

        Parameters
        ----------
        x : ndarray, shape (M, N) -- population matrix
        """
        M, N = x.shape
        out = np.empty(M)
        for i in prange(M):
            s = x[i, 0] * x[i, 0]
            for j in range(1, N):
                s += 1e6 * x[i, j] * x[i, j]
            out[i] = s
        return out

    @njit(cache=True, parallel=True, boundscheck=False, nogil=True)
    def bent_cigar_strict_nb(x):
        """Bent Cigar with fixed left-to-right summation and no fastmath."""
        M, N = x.shape
        out = np.empty(M)
        for i in prange(M):
            s = x[i, 0] * x[i, 0]
            for j in range(1, N):
                s = s + 1e6 * x[i, j] * x[i, j]
            out[i] = s
        return out

    @njit(cache=True, parallel=True, fastmath=True, boundscheck=False, nogil=True)
    def levy_nb(x):
        """Levy function.

        Parameters
        ----------
        x : ndarray, shape (M, N) -- population matrix
        """
        M, N = x.shape
        out = np.empty(M)
        for i in prange(M):
            w0 = 1.0 + (x[i, 0] - 1.0) * 0.25
            s = np.sin(PI * w0) ** 2
            for j in range(N - 1):
                wj = 1.0 + (x[i, j] - 1.0) * 0.25
                s += (wj - 1.0) ** 2 * (1.0 + 10.0 * np.sin(PI * wj + 1.0) ** 2)
            wn = 1.0 + (x[i, N - 1] - 1.0) * 0.25
            s += (wn - 1.0) ** 2 * (1.0 + np.sin(2.0 * PI * wn) ** 2)
            out[i] = s
        return out

    @njit(cache=True, parallel=True, fastmath=True, boundscheck=False, nogil=True)
    def step_rastrigin_nb(x):
        """Step Rastrigin function with baked-in 0.0512 shrink factor.

        Parameters
        ----------
        x : ndarray, shape (M, N) -- population matrix
        """
        M, N = x.shape
        out = np.empty(M)
        for i in prange(M):
            s = 0.0
            for j in range(N):
                xj = 0.0512 * x[i, j]
                s += xj * xj - 10.0 * np.cos(2.0 * PI * xj) + 10.0
            out[i] = s
        return out

    # ----- shift_rotate (helper + Python wrapper) ---------------------------

    @njit(cache=True, parallel=True, fastmath=True, boundscheck=False, nogil=True)
    def _shift_only_nb(x, shift, N):
        """Subtract shift vector from each row of x.

        Parameters
        ----------
        x : ndarray, shape (M, >=N) -- input matrix
        shift : ndarray, shape (>=N,) -- shift vector
        N : int -- number of dimensions to process
        """
        M = x.shape[0]
        out = np.empty((M, N), dtype=np.float64)
        for i in prange(M):
            for j in range(N):
                out[i, j] = x[i, j] - shift[j]
        return out

    @njit(cache=True, parallel=True, boundscheck=False, nogil=True)
    def _shift_only_strict_nb(x, shift, N):
        """Subtract shift vector with no fastmath for strict trace mode."""
        M = x.shape[0]
        out = np.empty((M, N), dtype=np.float64)
        for i in prange(M):
            for j in range(N):
                out[i, j] = x[i, j] - shift[j]
        return out

    @njit(cache=True, parallel=True, boundscheck=False, nogil=True)
    def _shift_rotate_strict_nb(x, shift, rotation_T):
        """Shift and rotate with the same explicit inner-loop order every time."""
        M = x.shape[0]
        N = x.shape[1]
        out = np.empty((M, N), dtype=np.float64)
        for i in prange(M):
            for k in range(N):
                s = 0.0
                for j in range(N):
                    s = s + (x[i, j] - shift[j]) * rotation_T[j, k]
                out[i, k] = s
        return out

    def shift_rotate_fast(x, shift, rotation, rotation_T=None):
        """Apply shift (and optional rotation) to a population matrix.

        Parameters
        ----------
        x : ndarray, shape (M, D) -- population
        shift : ndarray -- shift vector (at least D elements)
        rotation : ndarray or None -- rotation matrix (D, D), or None to skip
        """
        N = x.shape[1]
        y = _shift_only_nb(x, shift[:N], N)
        if rotation_T is not None:
            return y @ rotation_T
        if rotation is not None:
            return y @ rotation.T
        return y

    def shift_rotate_strict_fast(x, shift, rotation, rotation_T=None):
        """Apply shift/rotation without BLAS or fastmath for parity tracing."""
        N = x.shape[1]
        if rotation_T is not None:
            return _shift_rotate_strict_nb(x, shift[:N], rotation_T)
        if rotation is not None:
            return _shift_rotate_strict_nb(x, shift[:N], np.ascontiguousarray(rotation.T))
        return _shift_only_strict_nb(x, shift[:N], N)

    # ----- Base functions 2: schwefel / elliptic / discus / ackley ----------

    @njit(cache=True, parallel=True, fastmath=True, boundscheck=False, nogil=True)
    def schwefel_nb(x):
        """Schwefel function with baked-in scaling and boundary correction.

        Parameters
        ----------
        x : ndarray, shape (M, N) -- population matrix
        """
        M, N = x.shape
        out = np.empty(M)
        for i in prange(M):
            s = 0.0
            for j in range(N):
                z = 10.0 * x[i, j] + 420.9687462275036
                if z > 500.0:
                    mod = z - 500.0 * np.floor(z / 500.0)  # fmod
                    t = 500.0 - mod
                    s += -t * np.sin(np.sqrt(np.abs(t))) + ((z - 500.0) / 100.0) ** 2 / N
                elif z < -500.0:
                    az = -z
                    mod = az - 500.0 * np.floor(az / 500.0)
                    t = -500.0 + mod
                    s += -t * np.sin(np.sqrt(np.abs(500.0 - mod))) + ((z + 500.0) / 100.0) ** 2 / N
                else:
                    s += -z * np.sin(np.sqrt(np.abs(z)))
            out[i] = s + 418.9828872724338 * N
        return out

    @njit(cache=True, parallel=True, fastmath=True, boundscheck=False, nogil=True)
    def elliptic_nb(x):
        """High-conditioned Elliptic function.

        Parameters
        ----------
        x : ndarray, shape (M, N) -- population matrix
        """
        M, N = x.shape
        out = np.empty(M)
        # Pre-compute coefficient array once outside prange
        _ec = np.empty(N)
        denom = max(N - 1, 1)
        for j in range(N):
            _ec[j] = 10.0 ** (6.0 * j / denom)
        for i in prange(M):
            s = 0.0
            for j in range(N):
                s += _ec[j] * x[i, j] * x[i, j]
            out[i] = s
        return out

    @njit(cache=True, parallel=True, fastmath=True, boundscheck=False, nogil=True)
    def discus_nb(x):
        """Discus function (1e6 weight on first variable).

        Parameters
        ----------
        x : ndarray, shape (M, N) -- population matrix
        """
        M, N = x.shape
        out = np.empty(M)
        for i in prange(M):
            s = 1e6 * x[i, 0] * x[i, 0]
            for j in range(1, N):
                s += x[i, j] * x[i, j]
            out[i] = s
        return out

    @njit(cache=True, parallel=True, fastmath=True, boundscheck=False, nogil=True)
    def ackley_nb(x):
        """Ackley function.

        Parameters
        ----------
        x : ndarray, shape (M, N) -- population matrix
        """
        M, N = x.shape
        out = np.empty(M)
        E_val = np.e
        for i in prange(M):
            s1 = 0.0
            s2 = 0.0
            for j in range(N):
                s1 += x[i, j] * x[i, j]
                s2 += np.cos(2.0 * PI * x[i, j])
            out[i] = E_val - 20.0 * np.exp(-0.2 * np.sqrt(s1 / N)) - np.exp(s2 / N) + 20.0
        return out

    # ----- Base functions 3: weierstrass / griewank / katsuura --------------

    @njit(cache=True, parallel=True, fastmath=True, boundscheck=False, nogil=True)
    def weierstrass_nb(x):
        """Weierstrass function with baked-in 0.005 shrink.

        Uses module-level precomputed ``_WEIER_AK``, ``_WEIER_BK``, and
        ``_WEIER_CORRECTION`` (AUDIT-31) to avoid recomputing 21-element
        coefficient arrays and the correction sum on every call.

        Parameters
        ----------
        x : ndarray, shape (M, N) -- population matrix
        """
        M, N = x.shape
        out = np.empty(M)
        ak = _WEIER_AK
        bk = _WEIER_BK
        correction = _WEIER_CORRECTION
        k_max = _WEIER_K_MAX
        for i in prange(M):
            s = 0.0
            for j in range(N):
                xj = 0.005 * x[i, j]
                for k in range(k_max + 1):
                    s += ak[k] * np.cos(2.0 * PI * bk[k] * (xj + 0.5))
            out[i] = s - N * correction
        return out

    @njit(cache=True, parallel=True, fastmath=True, boundscheck=False, nogil=True)
    def griewank_nb(x):
        """Griewank function with baked-in 6.0 shrink.

        Parameters
        ----------
        x : ndarray, shape (M, N) -- population matrix
        """
        M, N = x.shape
        out = np.empty(M)
        # Pre-compute inverse sqrt divisors once outside prange
        inv_sqrt_j = np.empty(N)
        for j in range(N):
            inv_sqrt_j[j] = 1.0 / np.sqrt(1.0 + j)
        for i in prange(M):
            s = 0.0
            p = 1.0
            for j in range(N):
                xj = 6.0 * x[i, j]
                s += xj * xj / 4000.0
                p *= np.cos(xj * inv_sqrt_j[j])
            out[i] = 1.0 + s - p
        return out

    @njit(cache=True, parallel=True, fastmath=True, boundscheck=False, nogil=True)
    def katsuura_nb(x):
        """Katsuura function with baked-in 0.05 shrink.

        Uses module-level precomputed ``_KATSUURA_POW2J`` (AUDIT-31) to
        avoid recomputing the 32-element powers-of-2 array on every call.

        Parameters
        ----------
        x : ndarray, shape (M, N) -- population matrix
        """
        M, N = x.shape
        out = np.empty(M)
        tmp3 = N ** 1.2
        pow2j = _KATSUURA_POW2J
        tmp1 = 10.0 / N / N
        for i in prange(M):
            prod_val = 1.0
            for j in range(N):
                xj = 0.05 * x[i, j]
                temp = 0.0
                for k in range(32):
                    v = pow2j[k] * xj
                    temp += np.abs(v - np.floor(v + 0.5)) / pow2j[k]
                prod_val *= (1.0 + (j + 1) * temp) ** (10.0 / tmp3)
            out[i] = prod_val * tmp1 - tmp1
        return out

    # ----- Base functions 4: happycat / hgbat / schaffer_F7 -----------------

    @njit(cache=True, parallel=True, fastmath=True, boundscheck=False, nogil=True)
    def happycat_nb(x):
        """HappyCat function with baked-in 0.05 shrink and -1 shift.

        Parameters
        ----------
        x : ndarray, shape (M, N) -- population matrix
        """
        M, N = x.shape
        out = np.empty(M)
        for i in prange(M):
            r2 = 0.0
            sz = 0.0
            for j in range(N):
                xj = 0.05 * x[i, j] - 1.0
                r2 += xj * xj
                sz += xj
            out[i] = np.abs(r2 - N) ** 0.25 + (0.5 * r2 + sz) / N + 0.5
        return out

    @njit(cache=True, parallel=True, fastmath=True, boundscheck=False, nogil=True)
    def hgbat_nb(x):
        """HGBat function with baked-in 0.05 shrink and -1 shift.

        Parameters
        ----------
        x : ndarray, shape (M, N) -- population matrix
        """
        M, N = x.shape
        out = np.empty(M)
        for i in prange(M):
            r2 = 0.0
            sz = 0.0
            for j in range(N):
                xj = 0.05 * x[i, j] - 1.0
                r2 += xj * xj
                sz += xj
            out[i] = np.abs(r2 * r2 - sz * sz) ** 0.5 + (0.5 * r2 + sz) / N + 0.5
        return out

    @njit(cache=True, parallel=True, fastmath=True, boundscheck=False, nogil=True)
    def schaffer_F7_nb(x):
        """Schaffer F7 function. Eliminates redundant sqrt computation.

        Parameters
        ----------
        x : ndarray, shape (M, N) -- population matrix
        """
        M, N = x.shape
        out = np.empty(M)
        if N < 2:
            for i in range(M):
                out[i] = 0.0
            return out
        for i in prange(M):
            s = 0.0
            for j in range(N - 1):
                si = np.sqrt(x[i, j] * x[i, j] + x[i, j + 1] * x[i, j + 1])
                sqsi = np.sqrt(si)
                s += sqsi * (1.0 + np.sin(50.0 * si ** 0.2) ** 2)
            out[i] = (s / (N - 1)) ** 2
        return out

    # ----- Base functions 5: bi_rastrigin / egpr / esf6 ---------------------

    @njit(cache=True, parallel=True, fastmath=True, boundscheck=False, nogil=True)
    def bi_rastrigin_nb(x, shift, rotation, apply_shift):
        """Lunacek Bi-Rastrigin with custom shift/rotate.

        Two-peak Rastrigin variant for composition functions.  The outer
        loop over M is parallelised; the matrix multiply (z @ rotation.T)
        is done collectively before the parallel reduction loop.

        Parameters
        ----------
        x : ndarray, shape (M, N) -- population matrix
        shift : ndarray, shape (>=N,) -- shift vector
        rotation : ndarray, shape (N, N) or None -- rotation matrix
        apply_shift : bool -- whether to subtract shift from x
        """
        M, N = x.shape
        # AUDIT-26: N<2 guard.  The Bi-Rastrigin formula contains
        # ``s = 1 - 1/(2*sqrt(N+20) - 8.2)``; at N=1 ``s`` is still
        # positive (~0.908) but ``mu0^2 - d = 5.25`` makes ``mu1``
        # imaginary only when ``s < 0`` (which never happens).  The real
        # issue is that the *NumPy* path in ``basic.py:bi_rastrigin``
        # raises ``ValueError`` for N<2, so the two paths diverge:
        #   - NumPy path: raises ValueError (strict)
        #   - Numba path: falls back to sphere (lenient)
        # A ``@njit`` kernel cannot raise Python exceptions, so we keep
        # the sphere fallback here.  This divergence is acceptable because
        # N<2 never occurs through validated entry points (minimum CEC
        # benchmark dimension is D=10).
        if N < 2:
            out = np.empty(M)
            for i in range(M):
                s = 0.0
                for j in range(N):
                    s += x[i, j] * x[i, j]
                out[i] = s
            return out
        mu0 = 2.5
        d = 1.0
        s_param = 1.0 - 1.0 / (2.0 * np.sqrt(N + 20.0) - 8.2)
        mu1 = -np.sqrt((mu0 * mu0 - d) / s_param)
        out = np.empty(M)
        # Build y and tmpx
        y = np.empty((M, N))
        tmpx = np.empty((M, N))
        z = np.empty((M, N))
        for i in prange(M):
            for j in range(N):
                if apply_shift:
                    y[i, j] = (x[i, j] - shift[j]) * 0.1
                else:
                    y[i, j] = x[i, j] * 0.1
                val = 2.0 * y[i, j]
                if shift[j] < 0.0:
                    val = -val
                z[i, j] = val
                tmpx[i, j] = val + mu0
        # Rotate z
        if rotation is not None:
            zr = z @ rotation.T
        else:
            zr = z
        for i in prange(M):
            tmp1 = 0.0
            tmp2 = 0.0
            cos_sum = 0.0
            for j in range(N):
                tmp1 += (tmpx[i, j] - mu0) ** 2
                tmp2 += (tmpx[i, j] - mu1) ** 2
                cos_sum += np.cos(2.0 * PI * zr[i, j])
            tmp2 = s_param * tmp2 + d * N
            out[i] = min(tmp1, tmp2) + 10.0 * (N - cos_sum)
        return out

    @njit(cache=True, parallel=True, fastmath=True, boundscheck=False, nogil=True)
    def egpr_nb(x):
        """Expanded Griewank plus Rosenbrock function (F11 in CEC2017).

        Parameters
        ----------
        x : ndarray, shape (M, N) -- population matrix
        """
        M, N = x.shape
        out = np.empty(M)
        for i in prange(M):
            s = 0.0
            for j in range(N):
                xj = 0.05 * x[i, j] + 1.0
                xj1 = 0.05 * x[i, (j + 1) % N] + 1.0
                t1 = xj * xj - xj1
                t2 = xj - 1.0
                temp = 100.0 * t1 * t1 + t2 * t2
                s += temp * temp / 4000.0 - np.cos(temp) + 1.0
            out[i] = s
        return out

    @njit(cache=True, parallel=True, fastmath=True, boundscheck=False, nogil=True)
    def esf6_nb(x):
        """Expanded Schaffer F6 function (F12 in CEC2017).

        Parameters
        ----------
        x : ndarray, shape (M, N) -- population matrix
        """
        M, N = x.shape
        out = np.empty(M)
        for i in prange(M):
            s = 0.0
            for j in range(N):
                ss = x[i, j] * x[i, j] + x[i, (j + 1) % N] * x[i, (j + 1) % N]
                t1 = np.sin(np.sqrt(ss)) ** 2
                t2 = (1.0 + 0.001 * ss) ** 2
                s += 0.5 + (t1 - 0.5) / t2
            out[i] = s
        return out

    # ----- Composition weights (cf_cal) -------------------------------------

    # NOTE: ``fastmath=False`` is intentional here.  This kernel feeds the
    # composition functions (F21-F30), which are the published benchmark
    # numbers.  Dropping ``fastmath`` guarantees bit-for-bit reproducibility
    # across CPU ISAs (AVX2 vs AVX-512) and across LLVM versions, because the
    # backend is no longer allowed to fuse mul+add into FMA, reorder
    # associative ops, or substitute approximate ``sqrt`` / ``exp``.  The
    # outer ``prange(M)`` parallelism is safe -- each iteration of i writes
    # to disjoint slices ``w[:, i]`` / ``out[i]`` and there is no
    # cross-thread reduction, so the result is independent of
    # ``NUMBA_NUM_THREADS``.
    @njit(cache=True, parallel=True, boundscheck=False, nogil=True)
    def _cf_cal_nb(x, comp_shifts, deltas, biases, fit_values):
        """Composition weight calculation for CEC composition functions.

        Computes Gaussian-weighted combination of K component function values
        for each of M individuals.  Outer loop over M is parallelised.

        Parameters
        ----------
        x : ndarray, shape (M, N) -- population matrix
        comp_shifts : ndarray, shape (K, >=N) -- per-component shift vectors
        deltas : ndarray, shape (K,) -- per-component spread parameters
        biases : ndarray, shape (K,) -- per-component bias offsets
        fit_values : ndarray, shape (K, M) -- pre-computed component fitness values
        """
        M = x.shape[0]
        N = x.shape[1]
        K = deltas.shape[0]
        INF_VAL = 1.0e99
        w = np.zeros((K, M))
        for i in prange(M):
            for k in range(K):
                dist_sq = 0.0
                for j in range(N):
                    d = x[i, j] - comp_shifts[k, j]
                    dist_sq += d * d
                if dist_sq != 0.0:
                    w[k, i] = (1.0 / np.sqrt(dist_sq)) * np.exp(
                        -dist_sq / (2.0 * N * deltas[k] * deltas[k])
                    )
                else:
                    w[k, i] = INF_VAL
        # Normalize + weighted sum
        out = np.zeros(M)
        for i in prange(M):
            w_sum = 0.0
            for k in range(K):
                w_sum += w[k, i]
            if w_sum == 0.0:
                for k in range(K):
                    w[k, i] = 1.0
                w_sum = float(K)
            s = 0.0
            for k in range(K):
                s += (w[k, i] / w_sum) * (fit_values[k, i] + biases[k])
            out[i] = s
        return out

    cf_cal_fast = _cf_cal_nb

else:
    # Numba unavailable -- every export is None; callers must provide a
    # pure-NumPy fallback under ``if _NB_FN is None:``.
    rastrigin_nb = None
    zakharov_nb = None
    rosenbrock_nb = None
    bent_cigar_nb = None
    bent_cigar_strict_nb = None
    levy_nb = None
    step_rastrigin_nb = None
    _shift_only_nb = None
    _shift_only_strict_nb = None
    _shift_rotate_strict_nb = None
    shift_rotate_fast = None
    shift_rotate_strict_fast = None
    schwefel_nb = None
    elliptic_nb = None
    discus_nb = None
    ackley_nb = None
    weierstrass_nb = None
    griewank_nb = None
    katsuura_nb = None
    happycat_nb = None
    hgbat_nb = None
    schaffer_F7_nb = None
    bi_rastrigin_nb = None
    egpr_nb = None
    esf6_nb = None
    _cf_cal_nb = None
    cf_cal_fast = None


# ===========================================================================
# Warmup -- trigger JIT compilation of all cached kernels
# ===========================================================================
def warmup() -> None:
    """Trigger JIT compilation of all CEC2017 kernels with small dummy inputs.

    Retained pre-compilation utility (no runner call sites in this project:
    the campaign runner warms each worker by evaluating a probe cell instead
    — ``warm_benchmark_cells`` in ``gsk_family.runners.performance``,
    invoked from ``run_experiment._init_process_worker``).  Calling it ensures
    subsequent calls to any ``*_nb`` / ``*_fast`` function do not pay the
    compilation cost.  Skipped gracefully when numba is not installed.

    The warmup payloads are drawn from a **fixed** ``default_rng(0xDEC0DE)``
    instance (audit finding C-02) so the JIT specialisation input is
    bit-identical across runs.  Using the unseeded global ``np.random``
    here would change the bytes the LLVM type-resolver sees on the very
    first compile, even though it does not affect any subsequent benchmark
    evaluation.  Determinism nonetheless costs nothing here -- the warmup
    arrays are never used by callers.
    """
    if not HAS_NUMBA:
        return
    _warmup_rng = np.random.default_rng(0xDEC0DE)
    n, d = 4, 3
    xc = _warmup_rng.standard_normal((n, d))
    rastrigin_nb(xc)
    zakharov_nb(xc)
    rosenbrock_nb(xc)
    bent_cigar_nb(xc)
    bent_cigar_strict_nb(xc)
    levy_nb(xc)
    step_rastrigin_nb(xc)
    schwefel_nb(xc)
    elliptic_nb(xc)
    discus_nb(xc)
    ackley_nb(xc)
    weierstrass_nb(xc)
    griewank_nb(xc)
    katsuura_nb(xc)
    happycat_nb(xc)
    hgbat_nb(xc)
    schaffer_F7_nb(xc)
    egpr_nb(xc)
    esf6_nb(xc)
    sh = _warmup_rng.standard_normal(100)
    rot = np.eye(d)
    bi_rastrigin_nb(xc, sh[:d], rot, True)
    bi_rastrigin_nb(xc, sh[:d], None, False)
    _shift_only_nb(xc, sh[:d], d)
    _shift_only_strict_nb(xc, sh[:d], d)
    shift_rotate_strict_fast(xc, sh[:d], rot)
    cs = _warmup_rng.standard_normal((2, d))
    dl = np.array([1.0, 1.0])
    bi = np.array([0.0, 0.0])
    fv = _warmup_rng.standard_normal((2, n))
    _cf_cal_nb(xc, cs, dl, bi, fv)


__all__ = [
    "HAS_NUMBA",
    "rastrigin_nb",
    "zakharov_nb",
    "rosenbrock_nb",
    "bent_cigar_nb",
    "bent_cigar_strict_nb",
    "levy_nb",
    "step_rastrigin_nb",
    "schwefel_nb",
    "elliptic_nb",
    "discus_nb",
    "ackley_nb",
    "weierstrass_nb",
    "griewank_nb",
    "katsuura_nb",
    "happycat_nb",
    "hgbat_nb",
    "schaffer_F7_nb",
    "bi_rastrigin_nb",
    "egpr_nb",
    "esf6_nb",
    "shift_rotate_fast",
    "shift_rotate_strict_fast",
    "cf_cal_fast",
    "warmup",
]
