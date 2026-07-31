"""CEC2020 Numba-accelerated kernels.

This module holds every JIT kernel used exclusively by the CEC2020 benchmark
suite -- the 15 raw base-function kernels (no baked-in shrink, since CEC2020
applies shrink externally via :func:`shift_rotate`) plus the unified
shift+rotate transform.  It mirrors the architecture of
:mod:`benchmarks.cec_suite_python.cec2017._numba`,
:mod:`benchmarks.cec_suite_python.cec2013._numba`,
:mod:`benchmarks.cec_suite_python.cec2011._numba`, and
:mod:`benchmarks.cec_suite_python.cec2013lsgo._numba`: each suite owns its own
``_numba.py`` file so that it can be dropped in or out without touching the
optimizer's own acceleration layer in :mod:`gsk._numba_accel`.

Kernel table
~~~~~~~~~~~~
========================= =================================================
Kernel                    Purpose
========================= =================================================
bent_cigar_raw_nb         Bent cigar (raw, no baked-in shrink)
ellips_raw_nb             High-conditioned Elliptic
discus_raw_nb             Discus
rosenbrock_raw_nb         Rosenbrock with +1 origin shift
ackley_raw_nb             Ackley
rastrigin_raw_nb          Rastrigin
schwefel_raw_nb           Schwefel with boundary correction
griewank_raw_nb           Griewank
weierstrass_raw_nb        Weierstrass (k_max=20)
katsuura_raw_nb           Katsuura
happycat_raw_nb           HappyCat with -1 origin shift
hgbat_raw_nb              HGBat with -1 origin shift
grie_rosen_raw_nb         Griewank-Rosenbrock with +1 origin shift
escaffer6_raw_nb          Expanded Schaffer F6
schaffer_F7_raw_nb        Schaffer F7
_shift_rotate_2020_nb     internal: shift + shrink + optional rotate
shift_rotate_2020_fast    Python wrapper with type coercion
========================= =================================================

All kernels expect C-contiguous ``float64`` input.  Outer loops over the
population dimension (``M``) are parallelised with ``prange``; inner loops
over ``N`` are sequential since they accumulate into a single reduction.

The ``raw`` suffix indicates that no shrink rate is baked into the kernel
itself -- the caller is responsible for scaling input via
:func:`shift_rotate_2020_fast` (which takes a ``shrink`` parameter).  This
matches CEC2020's design where ``shift_rotate(x, Os, Mr, shrink, ...)`` is
the single point that turns ``[-100, 100]^D`` input into per-function
natural-domain values.

Decorator policy
~~~~~~~~~~~~~~~~
Every parallel kernel uses the DT-GSK reproducibility-first decorator::

    @njit(cache=True, parallel=True, boundscheck=False, nogil=True)

``fastmath=True`` is **intentionally absent** across this entire suite (audit
finding H1).  CEC2020 composition functions (F8-F10) blend per-component
basic-kernel outputs through ``cf_cal``, so any FMA contraction or
associative reordering inside a basic kernel propagates into the composition
result and breaks bit-for-bit reproducibility across CPU ISAs (AVX2 vs
AVX-512) and Numba/LLVM versions.  ``boundscheck=False`` and ``nogil=True``
are required to release the GIL inside ``ProcessPoolExecutor`` workers
without contention.
"""

from __future__ import annotations

import numpy as np

try:
    from numba import njit, prange  # type: ignore[import-untyped]
    HAS_NUMBA = True
except Exception:  # not just ImportError: llvmlite can raise OSError under memory pressure
    HAS_NUMBA = False

PI = np.pi

# Pre-computed Weierstrass coefficients (a=0.5, b=3.0, k_max=20) used by
# weierstrass_raw_nb as closure variables, avoiding per-call recomputation.
_WEIER_AK_20 = np.array([0.5 ** k for k in range(21)], dtype=np.float64)
_WEIER_BK_20 = np.array([3.0 ** k for k in range(21)], dtype=np.float64)
_WEIER_CORR_20 = float(np.sum(_WEIER_AK_20 * np.cos(2.0 * PI * _WEIER_BK_20 * 0.5)))


# ===========================================================================
# JIT kernels (single big if HAS_NUMBA: / else: block)
# ===========================================================================
if HAS_NUMBA:

    # ----- Raw base functions -----------------------------------------------

    @njit(cache=True, parallel=True, boundscheck=False, nogil=True)
    def bent_cigar_raw_nb(z):
        """Bent cigar function kernel (raw, no baked-in shrink).

        Parameters
        ----------
        z : ndarray, shape (M, N) -- pre-shifted/rotated population
        """
        M, N = z.shape
        out = np.empty(M)
        for i in prange(M):
            s = z[i, 0] * z[i, 0]
            for j in range(1, N):
                s += 1e6 * z[i, j] * z[i, j]
            out[i] = s
        return out

    @njit(cache=True, parallel=True, boundscheck=False, nogil=True)
    def ellips_raw_nb(z):
        """High-conditioned elliptic function kernel (raw).

        Parameters
        ----------
        z : ndarray, shape (M, N) -- pre-shifted/rotated population
        """
        M, N = z.shape
        out = np.empty(M)
        denom = max(N - 1, 1)
        for i in prange(M):
            s = 0.0
            for j in range(N):
                s += 10.0 ** (6.0 * j / denom) * z[i, j] * z[i, j]
            out[i] = s
        return out

    @njit(cache=True, parallel=True, boundscheck=False, nogil=True)
    def discus_raw_nb(z):
        """Discus function kernel (raw).

        Parameters
        ----------
        z : ndarray, shape (M, N) -- pre-shifted/rotated population
        """
        M, N = z.shape
        out = np.empty(M)
        for i in prange(M):
            s = 1e6 * z[i, 0] * z[i, 0]
            for j in range(1, N):
                s += z[i, j] * z[i, j]
            out[i] = s
        return out

    @njit(cache=True, parallel=True, boundscheck=False, nogil=True)
    def rosenbrock_raw_nb(z):
        """Rosenbrock function kernel (raw): z+1 origin shift, NO shrink.

        The caller has already applied any shrink via
        :func:`shift_rotate_2020_fast`.

        Parameters
        ----------
        z : ndarray, shape (M, N) -- pre-shifted/rotated population
        """
        M, N = z.shape
        out = np.empty(M)
        for i in prange(M):
            s = 0.0
            for j in range(N - 1):
                zj = z[i, j] + 1.0
                zj1 = z[i, j + 1] + 1.0
                t1 = zj * zj - zj1
                t2 = zj - 1.0
                s += 100.0 * t1 * t1 + t2 * t2
            out[i] = s
        return out

    @njit(cache=True, parallel=True, boundscheck=False, nogil=True)
    def ackley_raw_nb(z):
        """Ackley function kernel (raw).

        Parameters
        ----------
        z : ndarray, shape (M, N) -- pre-shifted/rotated population
        """
        M, N = z.shape
        out = np.empty(M)
        E_val = np.e
        for i in prange(M):
            s1 = 0.0
            s2 = 0.0
            for j in range(N):
                s1 += z[i, j] * z[i, j]
                s2 += np.cos(2.0 * PI * z[i, j])
            out[i] = E_val - 20.0 * np.exp(-0.2 * np.sqrt(s1 / N)) - np.exp(s2 / N) + 20.0
        return out

    @njit(cache=True, parallel=True, boundscheck=False, nogil=True)
    def rastrigin_raw_nb(z):
        """Rastrigin function kernel (raw).

        Parameters
        ----------
        z : ndarray, shape (M, N) -- pre-shifted/rotated population
        """
        M, N = z.shape
        out = np.empty(M)
        for i in prange(M):
            s = 0.0
            for j in range(N):
                s += z[i, j] * z[i, j] - 10.0 * np.cos(2.0 * PI * z[i, j]) + 10.0
            out[i] = s
        return out

    @njit(cache=True, parallel=True, boundscheck=False, nogil=True)
    def schwefel_raw_nb(z):
        """Schwefel function kernel (raw): z already scaled, add 4.209...e2.

        Parameters
        ----------
        z : ndarray, shape (M, N) -- pre-shifted/rotated population
        """
        M, N = z.shape
        out = np.empty(M)
        for i in prange(M):
            s = 0.0
            for j in range(N):
                zj = z[i, j] + 4.209687462275036e2
                if zj > 500.0:
                    mod = zj - 500.0 * np.floor(zj / 500.0)
                    t = 500.0 - mod
                    s += -t * np.sin(np.sqrt(np.abs(t))) + ((zj - 500.0) / 100.0) ** 2 / N
                elif zj < -500.0:
                    az = -zj
                    mod = az - 500.0 * np.floor(az / 500.0)
                    t = -500.0 + mod
                    s += -t * np.sin(np.sqrt(np.abs(500.0 - mod))) + ((zj + 500.0) / 100.0) ** 2 / N
                else:
                    s += -zj * np.sin(np.sqrt(np.abs(zj)))
            out[i] = s + 4.189828872724338e2 * N
        return out

    @njit(cache=True, parallel=True, boundscheck=False, nogil=True)
    def griewank_raw_nb(z):
        """Griewank function kernel (raw).

        Parameters
        ----------
        z : ndarray, shape (M, N) -- pre-shifted/rotated population
        """
        M, N = z.shape
        out = np.empty(M)
        # C20-2: precompute 1/sqrt(1+j) outside prange — reduces M*N
        # transcendental calls to just N.
        inv_sqrt_j = np.empty(N)
        for j in range(N):
            inv_sqrt_j[j] = 1.0 / np.sqrt(1.0 + j)
        for i in prange(M):
            s = 0.0
            p = 1.0
            for j in range(N):
                s += z[i, j] * z[i, j] / 4000.0
                p *= np.cos(z[i, j] * inv_sqrt_j[j])
            out[i] = 1.0 + s - p
        return out

    @njit(cache=True, parallel=True, boundscheck=False, nogil=True)
    def weierstrass_raw_nb(z):
        """Weierstrass function kernel (raw).

        Uses module-level pre-computed ``_WEIER_AK_20``, ``_WEIER_BK_20``,
        ``_WEIER_CORR_20`` to avoid recomputing 21-element arrays and
        correction on every call.

        Parameters
        ----------
        z : ndarray, shape (M, N) -- pre-shifted/rotated population
        """
        M, N = z.shape
        out = np.empty(M)
        k_max = 20
        ak = _WEIER_AK_20
        bk = _WEIER_BK_20
        correction = _WEIER_CORR_20
        for i in prange(M):
            s = 0.0
            for j in range(N):
                for k in range(k_max + 1):
                    s += ak[k] * np.cos(2.0 * PI * bk[k] * (z[i, j] + 0.5))
            out[i] = s - N * correction
        return out

    @njit(cache=True, parallel=True, boundscheck=False, nogil=True)
    def katsuura_raw_nb(z):
        """Katsuura function kernel (raw).

        Parameters
        ----------
        z : ndarray, shape (M, N) -- pre-shifted/rotated population
        """
        M, N = z.shape
        out = np.empty(M)
        tmp3 = N ** 1.2
        pow2j = np.empty(32)
        for j in range(32):
            pow2j[j] = 2.0 ** (j + 1)
        tmp1 = 10.0 / N / N
        for i in prange(M):
            prod_val = 1.0
            for j in range(N):
                temp = 0.0
                for k in range(32):
                    v = pow2j[k] * z[i, j]
                    temp += np.abs(v - np.floor(v + 0.5)) / pow2j[k]
                prod_val *= (1.0 + (j + 1) * temp) ** (10.0 / tmp3)
            out[i] = prod_val * tmp1 - tmp1
        return out

    @njit(cache=True, parallel=True, boundscheck=False, nogil=True)
    def happycat_raw_nb(z):
        """HappyCat function kernel (raw): z-1 origin shift.

        Parameters
        ----------
        z : ndarray, shape (M, N) -- pre-shifted/rotated population
        """
        M, N = z.shape
        out = np.empty(M)
        for i in prange(M):
            r2 = 0.0
            sz = 0.0
            for j in range(N):
                zj = z[i, j] - 1.0
                r2 += zj * zj
                sz += zj
            out[i] = np.abs(r2 - N) ** 0.25 + (0.5 * r2 + sz) / N + 0.5
        return out

    @njit(cache=True, parallel=True, boundscheck=False, nogil=True)
    def hgbat_raw_nb(z):
        """HGBat function kernel (raw): z-1 origin shift.

        Parameters
        ----------
        z : ndarray, shape (M, N) -- pre-shifted/rotated population
        """
        M, N = z.shape
        out = np.empty(M)
        for i in prange(M):
            r2 = 0.0
            sz = 0.0
            for j in range(N):
                zj = z[i, j] - 1.0
                r2 += zj * zj
                sz += zj
            out[i] = np.abs(r2 * r2 - sz * sz) ** 0.5 + (0.5 * r2 + sz) / N + 0.5
        return out

    @njit(cache=True, parallel=True, boundscheck=False, nogil=True)
    def grie_rosen_raw_nb(z):
        """Griewank-Rosenbrock function kernel (raw): z+1 origin shift.

        Parameters
        ----------
        z : ndarray, shape (M, N) -- pre-shifted/rotated population
        """
        M, N = z.shape
        out = np.empty(M)
        for i in prange(M):
            s = 0.0
            for j in range(N):
                zj = z[i, j] + 1.0
                zj1 = z[i, (j + 1) % N] + 1.0
                t1 = zj * zj - zj1
                t2 = zj - 1.0
                temp = 100.0 * t1 * t1 + t2 * t2
                s += temp * temp / 4000.0 - np.cos(temp) + 1.0
            out[i] = s
        return out

    @njit(cache=True, parallel=True, boundscheck=False, nogil=True)
    def escaffer6_raw_nb(z):
        """Expanded Schaffer F6 function kernel (raw).

        Parameters
        ----------
        z : ndarray, shape (M, N) -- pre-shifted/rotated population
        """
        M, N = z.shape
        out = np.empty(M)
        for i in prange(M):
            s = 0.0
            for j in range(N):
                ss = z[i, j] * z[i, j] + z[i, (j + 1) % N] * z[i, (j + 1) % N]
                t1 = np.sin(np.sqrt(ss)) ** 2
                t2 = (1.0 + 0.001 * ss) ** 2
                s += 0.5 + (t1 - 0.5) / t2
            out[i] = s
        return out

    @njit(cache=True, parallel=True, boundscheck=False, nogil=True)
    def schaffer_F7_raw_nb(z):
        """Schaffer F7 function kernel (raw). Avoids redundant sqrt computation.

        Parameters
        ----------
        z : ndarray, shape (M, N) -- pre-shifted/rotated population
        """
        M, N = z.shape
        out = np.empty(M)
        if N < 2:
            for i in range(M):
                out[i] = 0.0
            return out
        for i in prange(M):
            s = 0.0
            for j in range(N - 1):
                si = np.sqrt(z[i, j] * z[i, j] + z[i, j + 1] * z[i, j + 1])
                sqsi = np.sqrt(si)
                s += sqsi * (1.0 + np.sin(50.0 * si ** 0.2) ** 2)
            out[i] = (s / (N - 1)) ** 2
        return out

    # ----- Shift-rotate transform (with shrink + flags) ---------------------

    @njit(cache=True, parallel=True, boundscheck=False, nogil=True)
    def _shift_scale_2020_nb(x, Os, shrink, s_flag):
        """Shift-and-scale kernel with optional shrink factor.

        Parameters
        ----------
        x : ndarray, shape (M, N) -- input population
        Os : ndarray, shape (>=N,) -- shift vector
        shrink : float -- shrink multiplier applied after shift
        s_flag : int -- 1 to apply shift, 0 to skip
        """
        M, N = x.shape
        y = np.empty((M, N))
        if s_flag:
            for i in prange(M):
                for j in range(N):
                    y[i, j] = (x[i, j] - Os[j]) * shrink
        else:
            for i in prange(M):
                for j in range(N):
                    y[i, j] = x[i, j] * shrink
        return y

    @njit(cache=True, boundscheck=False, nogil=True)
    def _shift_rotate_2020_nb(x, Os, Mr, shrink, s_flag, r_flag):
        """Backward-compatible shift/rotate kernel used by warmup and parity tests."""
        y = _shift_scale_2020_nb(x, Os, shrink, s_flag)
        if r_flag:
            return y @ Mr.T
        return y

    def shift_rotate_2020_fast(x, Os, Mr, shrink, s_flag, r_flag, Mr_T=None):
        """Shift-rotate wrapper with type coercion.

        Parameters
        ----------
        x : ndarray -- input population
        Os : ndarray -- shift vector
        Mr : ndarray -- rotation matrix
        shrink : float -- shrink multiplier
        s_flag : int/bool -- apply shift flag
        r_flag : int/bool -- apply rotation flag
        """
        y = _shift_scale_2020_nb(
            np.ascontiguousarray(x, dtype=np.float64),
            np.ascontiguousarray(Os, dtype=np.float64),
            float(shrink), int(s_flag),
        )
        if int(r_flag):
            if Mr_T is not None:
                return y @ Mr_T
            return y @ Mr.T
        return y

    # ----- Composition weights (cf_cal) -------------------------------------
    #
    # Audit H-3: previously ``cec2020/composition.py`` imported
    # ``cf_cal_fast`` from ``gsk._numba_accel`` — a location that does
    # not export this symbol.  The import silently fell through to
    # ``_cf_cal_fast = None`` and CEC2020 composition (F8/F9/F10)
    # was running the pure-NumPy branch on every NFE.  This local
    # definition restores the fast path without creating a
    # ``gsk/`` → ``benchmarks/`` dependency inversion.
    #
    # NOTE: ``fastmath=False`` is deliberate and consistent with this
    # suite's whole-module policy — see the module docstring (audit
    # H-01).  CEC2020 composition blends per-component basic-kernel
    # outputs, so any FMA contraction or associative reordering inside
    # ``cf_cal`` would break bit-for-bit reproducibility across CPU
    # ISAs.  This is the direct analogue of the ``_cf_cal_nb`` exception
    # in ``cec2017/_numba.py``.
    @njit(cache=True, parallel=True, boundscheck=False, nogil=True)
    def _cf_cal_nb(x, comp_shifts, deltas, biases, fit_values):
        """Composition weight calculation for CEC composition functions.

        Computes Gaussian-weighted combination of K component function
        values for each of M individuals.  Outer loop over M is
        parallelised.

        Parameters
        ----------
        x : ndarray, shape (M, N) -- population matrix
        comp_shifts : ndarray, shape (K, >=N) -- per-component shift vectors
        deltas : ndarray, shape (K,) -- per-component spread parameters
        biases : ndarray, shape (K,) -- per-component bias offsets
        fit_values : ndarray, shape (K, M) -- pre-computed component fitness
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
    # Numba unavailable -- every export is None; callers fall back to
    # pure NumPy under ``if _NB_FN is None:``.
    bent_cigar_raw_nb = None
    ellips_raw_nb = None
    discus_raw_nb = None
    rosenbrock_raw_nb = None
    ackley_raw_nb = None
    rastrigin_raw_nb = None
    schwefel_raw_nb = None
    griewank_raw_nb = None
    weierstrass_raw_nb = None
    katsuura_raw_nb = None
    happycat_raw_nb = None
    hgbat_raw_nb = None
    grie_rosen_raw_nb = None
    escaffer6_raw_nb = None
    schaffer_F7_raw_nb = None
    _shift_rotate_2020_nb = None
    shift_rotate_2020_fast = None
    # Audit H-3: composition weight kernel also unavailable without numba.
    _cf_cal_nb = None
    cf_cal_fast = None


# ===========================================================================
# Warmup -- trigger JIT compilation of all cached kernels
# ===========================================================================
def warmup() -> None:
    """Trigger JIT compilation of all CEC2020 kernels with small dummy inputs.

    Called once per worker process from
    :func:`gsk.benchmark_factory.init_cec_worker` so that subsequent calls
    to any ``*_nb`` / ``*_fast`` function do not pay the compilation cost.
    Skipped gracefully when numba is not installed.

    The warmup payload is drawn from a **fixed** ``default_rng(0xDEC0DE)``
    instance (audit finding Pattern B) so the JIT specialisation input is
    bit-identical across runs.  See ``cec2017/_numba.py:warmup`` for the
    full rationale.
    """
    if not HAS_NUMBA:
        return
    _warmup_rng = np.random.default_rng(0xDEC0DE)
    n, d = 4, 3
    xc = _warmup_rng.standard_normal((n, d))
    bent_cigar_raw_nb(xc)
    ellips_raw_nb(xc)
    discus_raw_nb(xc)
    rosenbrock_raw_nb(xc)
    ackley_raw_nb(xc)
    rastrigin_raw_nb(xc)
    schwefel_raw_nb(xc)
    griewank_raw_nb(xc)
    weierstrass_raw_nb(xc)
    katsuura_raw_nb(xc)
    happycat_raw_nb(xc)
    hgbat_raw_nb(xc)
    grie_rosen_raw_nb(xc)
    escaffer6_raw_nb(xc)
    schaffer_F7_raw_nb(xc)
    sh = _warmup_rng.standard_normal(100)
    mr = np.eye(d, dtype=np.float64)
    _shift_rotate_2020_nb(xc, sh[:d], mr, 1.0, 1, 1)
    # Audit H-3: warm up the composition weight kernel so CEC2020
    # F8/F9/F10 don't pay compilation cost on the first generation.
    K = 3
    _warmup_shifts = _warmup_rng.standard_normal((K, d))
    _warmup_deltas = np.array([10.0, 20.0, 30.0], dtype=np.float64)
    _warmup_biases = np.array([0.0, 100.0, 200.0], dtype=np.float64)
    _warmup_fit = _warmup_rng.standard_normal((K, n))
    _cf_cal_nb(xc, _warmup_shifts, _warmup_deltas, _warmup_biases, _warmup_fit)


__all__ = [
    "HAS_NUMBA",
    "bent_cigar_raw_nb",
    "ellips_raw_nb",
    "discus_raw_nb",
    "rosenbrock_raw_nb",
    "ackley_raw_nb",
    "rastrigin_raw_nb",
    "schwefel_raw_nb",
    "griewank_raw_nb",
    "weierstrass_raw_nb",
    "katsuura_raw_nb",
    "happycat_raw_nb",
    "hgbat_raw_nb",
    "grie_rosen_raw_nb",
    "escaffer6_raw_nb",
    "schaffer_F7_raw_nb",
    "shift_rotate_2020_fast",
    "cf_cal_fast",
    "warmup",
]
