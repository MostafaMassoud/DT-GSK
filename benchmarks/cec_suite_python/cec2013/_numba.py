"""CEC2013 Numba-accelerated kernels.

Cross-reference: each kernel corresponds to the inner formula loop of a C
function in ``test_func.c``.  The transform pipeline (shift, rotate) is
handled in NumPy by :mod:`.basic`; only the hot formula loops are JIT'd.

Kernel table
~~~~~~~~~~~~
========================= ===================== =========  ============================
Kernel                    C function            C lines    Formula
========================= ===================== =========  ============================
osz_func_nb               oszfunc               1013-1044  first/last dim oscillation
asy_func_nb               asyfunc               1003-1011  buffer-reuse asymmetry
conditioning_nb           (inline)              e.g. 384   x_i *= alpha^(i/(2(N-1)))
sphere_nb                 sphere_func           252-266    fused shift + sum(z^2)
elliptic_core_nb          ellips_func           279-283    sum(10^(6i/(N-1)) * z^2)
bent_cigar_core_nb        bent_cigar_func       302-306    z0^2 + 10^6*sum(zi^2)
discus_core_nb            discus_func           321-325    10^6*z0^2 + sum(zi^2)
dif_powers_core_nb        dif_powers_func       337-342    sqrt(sum(|z|^(2+4i//(N-1))))
rastrigin_core_nb         rastrigin_func        547-551    sum(z^2-10cos(2*pi*z)+10)
schwefel_core_nb          schwefel_func         624-643    boundary-handling Schwefel
rosenbrock_core_nb        rosenbrock_func       364-370    sum(100(z^2-z')^2+(z-1)^2)
ackley_core_nb            ackley_func           424-433    E-20exp(...)-exp(...)+20
weierstrass_core_nb       weierstrass_func      462-477    sum(a^k*cos(2pi*b^k*(y+0.5)))-N*corr
griewank_core_nb          griewank_func         501-508    1+s/4000-prod(cos(z/sqrt(1+j)))
escaffer6_core_nb         escaffer6_func        806-817    circular Scaffer F6
grie_rosen_core_nb        grie_rosen_func       773-784    circular Griewank-Rosenbrock
schaffer_F7_core_nb       schaffer_F7_func      392-400    [sum(sqrt(s)+sqrt(s)*sin^2(50*s^0.2))/(N-1)]^2
katsuura_core_nb          katsuura_func         670-683    prod(1+(j+1)*temp)^(10/N^1.2)*c-c
bi_rastrigin_core_nb      bi_rastrigin_func     731-749    min(s1,s2)+10(N-sum(cos(2pi*z)))
step_rastrigin_quant_nb   step_rastrigin_func   570-574    |z|>0.5 quantisation
cf_cal_nb                 cf_cal                1047-1085  distance-weighted composition
========================= ===================== =========  ============================

Parallelization strategy
~~~~~~~~~~~~~~~~~~~~~~~~
- Outer loop over M (population members) uses ``prange`` for multi-core.
- Inner loops over N (dimensions) or K (composition components) are
  sequential since they accumulate into a single value.
- Constants (ak, bk, pow2k, scale vectors, correction terms) are
  **pre-computed once** before the ``prange`` block to avoid redundant
  computation inside the hot loop.

All kernels expect C-contiguous float64 input.

Decorator policy
~~~~~~~~~~~~~~~~
Every parallel kernel uses the project's reproducibility-first decorator::

    @njit(cache=True, parallel=True, boundscheck=False, nogil=True)

Scalar kernels (``osz_func_nb`` and ``asy_func_nb``) drop ``parallel=True``
because the per-row work is too small to amortise the prange overhead, but
they still use the same ``boundscheck / nogil`` flags.

``fastmath=True`` is **intentionally absent** across this entire suite (audit
finding M-03).  Allowing the LLVM backend to fuse mul+add into FMA, reorder
associative reductions, or substitute approximate transcendentals would
break bit-for-bit reproducibility across CPU ISAs (AVX2 vs AVX-512) and
across Numba/LLVM versions.  The ~5-10 % performance gain is not worth the
loss of cross-host determinism for a published benchmark suite.

.. note::

   This is deliberately stricter than the five-category fastmath policy
   documented in ``benchmarks/cec_suite_python/cec2013lsgo/_numba.py``
   (Kernel categories / Decorator policy).  CEC2013LSGO follows the
   5-category policy (only Category 4 reductions drop ``fastmath``).  When
   porting kernels between CEC2013 and CEC2013LSGO, do not assume the same
   policy applies -- check the per-suite ``_numba.py`` module docstring.
"""

from __future__ import annotations

import numpy as np

try:
    from numba import njit, prange  # type: ignore[import-untyped]
    HAS_NUMBA = True
except Exception:  # not just ImportError: llvmlite can raise OSError under memory pressure
    HAS_NUMBA = False

PI = np.pi
E_VAL = np.e

# Composition "infinite weight" sentinel.  This is a Numba-side mirror of
# ``transforms.INF`` (the single source of truth in this suite).  It must be
# kept in sync; the assertion at the bottom of this module verifies they
# agree at import time.  Defined as a module-level constant so it can be
# captured by ``@njit`` closures (Numba cannot import Python module
# attributes from inside a JIT'd function).
INF_VAL: float = 1.0e99

# Pre-computed Weierstrass coefficients (a=0.5, b=3.0, k_max=20) used by
# weierstrass_core_nb as closure variables, avoiding per-call recomputation.
_WEIER_AK_13 = np.array([0.5 ** k for k in range(21)], dtype=np.float64)
_WEIER_BK_13 = np.array([3.0 ** k for k in range(21)], dtype=np.float64)
_WEIER_CORR_13 = float(np.sum(_WEIER_AK_13 * np.cos(2.0 * PI * _WEIER_BK_13 * 0.5)))

# =========================================================================
# Transform kernels
# =========================================================================

if HAS_NUMBA:

    @njit(cache=True, boundscheck=False, nogil=True)
    def osz_func_nb(x):
        """Oscillation transform -- first and last dimensions only.

        C reference: ``oszfunc`` (lines 1013-1044).
        Applies a smooth oscillation distortion to the first and last
        dimensions of each population member.  Middle dimensions pass
        through unchanged.

        The transform is::

            if x > 0:  c1, c2, sx = 10.0, 7.9, +1.0
            if x < 0:  c1, c2, sx = 5.5,  3.1, -1.0
            out = sx * exp(xx + 0.049*(sin(c1*xx) + sin(c2*xx)))

        where ``xx = log(|x|)``.

        Not parallelised: only 2 dimensions are processed per row,
        so the overhead of prange exceeds the work per item.
        """
        M, N = x.shape
        out = x.copy()
        # C loop: for (j=0; j<nx; j+=max(1,nx-1)) processes j=0 and j=N-1.
        # When N=1, only j=0 is processed (step=max(1,0)=1, loop ends).
        # We replicate this with max(1, N-1) step to avoid Numba type issues.
        step = max(1, N - 1)
        for dim_idx in range(0, N, step):
            for i in range(M):
                xi = x[i, dim_idx]
                if xi != 0.0:
                    xx = np.log(abs(xi))
                    if xi > 0.0:
                        c1, c2, sx = 10.0, 7.9, 1.0
                    else:
                        c1, c2, sx = 5.5, 3.1, -1.0
                    out[i, dim_idx] = sx * np.exp(
                        xx + 0.049 * (np.sin(c1 * xx) + np.sin(c2 * xx))
                    )
                else:
                    out[i, dim_idx] = 0.0
        return out

    @njit(cache=True, boundscheck=False, nogil=True)
    def asy_func_nb(x_in, prev_buf, beta):
        """Asymmetry transform with buffer-reuse semantics.

        C reference: ``asyfunc`` (lines 1003-1011).
        For elements where x_in > 0, computes::

            out[i,j] = x_in[i,j] ^ (1 + beta * j/(N-1) * sqrt(x_in[i,j]))

        For elements where x_in <= 0, retains the value from prev_buf
        (matching the C behaviour where the output buffer ``y[]`` is not
        cleared before the asy transform).

        Not parallelised: data-dependent branching on every element makes
        prange overhead dominate for typical population sizes.
        """
        M, N = x_in.shape
        out = prev_buf.copy()
        Nm1 = N - 1.0
        for i in range(M):
            for j in range(N):
                xij = x_in[i, j]
                if xij > 0.0:
                    exp = 1.0 + beta * j / Nm1 * np.sqrt(xij)
                    out[i, j] = xij ** exp
        return out

    @njit(cache=True, parallel=True, boundscheck=False, nogil=True)
    def conditioning_nb(x, alpha):
        """Ill-conditioning: x_i *= alpha^(i / (2*(N-1))).

        C reference: inline scaling e.g. ``z[i]*=pow(10.0,1.0*i/(nx-1)/2.0)``
        (line 384-385 for Schaffer F7).

        Pre-computes the scale vector ``alpha^(j/(2*(N-1)))`` once, then
        applies it across all M population members in parallel.
        """
        M, N = x.shape
        out = np.empty_like(x)
        Nm1 = float(N - 1)
        # Pre-compute scale vector (avoids recomputing pow per element)
        scale = np.empty(N)
        for j in range(N):
            scale[j] = alpha ** (j / Nm1 / 2.0)
        for i in prange(M):
            for j in range(N):
                out[i, j] = x[i, j] * scale[j]
        return out

    # =====================================================================
    # Base function kernels
    # =====================================================================

    @njit(cache=True, parallel=True, boundscheck=False, nogil=True)
    def sphere_nb(x, Os, N):
        """Sphere: shift + sum(z^2).

        C reference: ``sphere_func`` (lines 252-266).
        Fused shift-and-sum avoids creating an (M,N) intermediate.
        """
        M = x.shape[0]
        out = np.empty(M)
        for i in prange(M):
            s = 0.0
            for j in range(N):
                zj = x[i, j] - Os[j]
                s += zj * zj
            out[i] = s
        return out

    @njit(cache=True, parallel=True, boundscheck=False, nogil=True)
    def elliptic_core_nb(z, N):
        """Elliptic: sum(10^(6*i/(N-1)) * z_i^2).

        C reference: ``ellips_func`` (lines 279-283).
        Pre-computes the coefficient vector ``10^(6*i/(N-1))`` once.
        """
        M = z.shape[0]
        out = np.empty(M)
        Nm1 = float(N - 1)
        # Pre-compute coefficients
        coeff = np.empty(N)
        for j in range(N):
            coeff[j] = 10.0 ** (6.0 * j / Nm1)
        for i in prange(M):
            s = 0.0
            for j in range(N):
                s += coeff[j] * z[i, j] * z[i, j]
            out[i] = s
        return out

    @njit(cache=True, parallel=True, boundscheck=False, nogil=True)
    def bent_cigar_core_nb(z, N):
        """Bent Cigar: z_0^2 + 10^6 * sum(z_i^2, i=1..N-1).

        C reference: ``bent_cigar_func`` (lines 302-306).
        Note: the 10^6 multiplier is applied to EACH z_i^2 individually
        (C: ``pow(10.0,6.0)*z[i]*z[i]``), not factored out.
        Mathematically identical: z0^2 + 1e6*(z1^2+...+zN-1^2).
        """
        M = z.shape[0]
        out = np.empty(M)
        for i in prange(M):
            s = z[i, 0] * z[i, 0]
            for j in range(1, N):
                s += 1e6 * z[i, j] * z[i, j]
            out[i] = s
        return out

    @njit(cache=True, parallel=True, boundscheck=False, nogil=True)
    def discus_core_nb(z, N):
        """Discus: 10^6 * z_0^2 + sum(z_i^2, i=1..N-1).

        C reference: ``discus_func`` (lines 321-325).
        """
        M = z.shape[0]
        out = np.empty(M)
        for i in prange(M):
            s = 1e6 * z[i, 0] * z[i, 0]
            for j in range(1, N):
                s += z[i, j] * z[i, j]
            out[i] = s
        return out

    @njit(cache=True, parallel=True, boundscheck=False, nogil=True)
    def dif_powers_core_nb(z, N):
        """Different Powers: sqrt(sum(|z_i|^(2 + 4*i//(N-1)))).

        C reference: ``dif_powers_func`` (lines 337-342).
        Uses integer division ``4*i/(N-1)`` matching C truncation.
        Pre-computes the exponent vector.

        Audit CRIT-04: ``Nm1 = max(N - 1, 1)`` guards against the
        N==1 degenerate case (CEC2013 never calls this with N==1, but
        the kernel must remain safe for any caller -- a divide-by-zero
        in a Numba ``njit`` body is silent UB, not a Python exception).
        """
        M = z.shape[0]
        out = np.empty(M)
        Nm1 = N - 1 if N > 1 else 1
        # Pre-compute exponents (integer arithmetic matching C)
        exponents = np.empty(N)
        for j in range(N):
            exponents[j] = float(2 + (4 * j) // Nm1)
        for i in prange(M):
            s = 0.0
            for j in range(N):
                s += abs(z[i, j]) ** exponents[j]
            out[i] = np.sqrt(s)
        return out

    @njit(cache=True, parallel=True, boundscheck=False, nogil=True)
    def rastrigin_core_nb(z):
        """Rastrigin raw formula: sum(z^2 - 10*cos(2*pi*z) + 10).

        C reference: ``rastrigin_func`` (lines 547-551).
        Applied on pre-transformed z (after shift, shrink, osz, asy,
        conditioning, and up to 3 rotations).
        """
        M, N = z.shape
        out = np.empty(M)
        for i in prange(M):
            s = 0.0
            for j in range(N):
                zj = z[i, j]
                s += zj * zj - 10.0 * np.cos(2.0 * PI * zj) + 10.0
            out[i] = s
        return out

    @njit(cache=True, parallel=True, boundscheck=False, nogil=True)
    def schwefel_core_nb(z, N):
        """Schwefel raw formula with boundary handling.

        C reference: ``schwefel_func`` (lines 624-643).
        Three cases per dimension:
          z > 500:  penalty + clipped sine (using fmod(z, 500))
          z < -500: penalty + clipped sine (using fmod(|z|, 500))
          else:     -z * sin(sqrt(|z|))
        Final offset: 418.9828... * N.
        """
        M = z.shape[0]
        out = np.empty(M)
        for i in prange(M):
            f_val = 0.0
            for j in range(N):
                zj = z[i, j]
                if zj > 500.0:
                    mod_p = zj - 500.0 * np.floor(zj / 500.0)
                    term = 500.0 - mod_p
                    f_val -= term * np.sin(np.sqrt(abs(term)))
                    pen = (zj - 500.0) / 100.0
                    f_val += pen * pen / N
                elif zj < -500.0:
                    az = abs(zj)
                    mod_n = az - 500.0 * np.floor(az / 500.0)
                    term = -500.0 + mod_n
                    f_val -= term * np.sin(np.sqrt(abs(500.0 - mod_n)))
                    pen = (zj + 500.0) / 100.0
                    f_val += pen * pen / N
                else:
                    f_val -= zj * np.sin(np.sqrt(abs(zj)))
            out[i] = f_val + 4.189828872724338e+002 * N
        return out

    @njit(cache=True, parallel=True, boundscheck=False, nogil=True)
    def rosenbrock_core_nb(z):
        """Rosenbrock: sum(100*(z_i^2 - z_{i+1})^2 + (z_i - 1)^2).

        C reference: ``rosenbrock_func`` (lines 364-370).
        Applied on pre-transformed z (already shifted by +1).
        """
        M, N = z.shape
        out = np.empty(M)
        for i in prange(M):
            s = 0.0
            for j in range(N - 1):
                t1 = z[i, j] * z[i, j] - z[i, j + 1]
                t2 = z[i, j] - 1.0
                s += 100.0 * t1 * t1 + t2 * t2
            out[i] = s
        return out

    @njit(cache=True, parallel=True, boundscheck=False, nogil=True)
    def ackley_core_nb(y):
        """Ackley: E - 20*exp(-0.2*sqrt(s1/N)) - exp(s2/N) + 20.

        C reference: ``ackley_func`` (lines 424-433).
        Uses ``E = 2.7182818284590452...`` (same IEEE double as np.e).
        """
        M, N = y.shape
        out = np.empty(M)
        for i in prange(M):
            s1 = 0.0
            s2 = 0.0
            for j in range(N):
                yj = y[i, j]
                s1 += yj * yj
                s2 += np.cos(2.0 * PI * yj)
            out[i] = E_VAL - 20.0 * np.exp(-0.2 * np.sqrt(s1 / N)) - np.exp(s2 / N) + 20.0
        return out

    @njit(cache=True, parallel=True, boundscheck=False, nogil=True)
    def weierstrass_core_nb(y, N):
        """Weierstrass: sum_j sum_k a^k*cos(2*pi*b^k*(y_j+0.5)) - N*correction.

        C reference: ``weierstrass_func`` (lines 462-477).
        a=0.5, b=3.0, k_max=20.  Uses module-level pre-computed
        ``_WEIER_AK_13``, ``_WEIER_BK_13``, ``_WEIER_CORR_13`` to
        avoid recomputing 21-element arrays and correction on every call.
        """
        M = y.shape[0]
        k_max = 20
        ak = _WEIER_AK_13
        bk = _WEIER_BK_13
        correction = _WEIER_CORR_13

        out = np.empty(M)
        for i in prange(M):
            s = 0.0
            for j in range(N):
                yj = y[i, j]
                for k in range(k_max + 1):
                    s += ak[k] * np.cos(2.0 * PI * bk[k] * (yj + 0.5))
            out[i] = s - N * correction
        return out

    @njit(cache=True, parallel=True, boundscheck=False, nogil=True)
    def griewank_core_nb(z):
        """Griewank: 1 + s/4000 - prod(cos(z_j / sqrt(1+j))).

        C reference: ``griewank_func`` (lines 501-508).
        Uses 0-based index j: ``cos(z[j] / sqrt(1.0 + j))``.
        Pre-computes ``1/sqrt(1+j)`` to avoid recomputing in the hot loop.
        """
        M, N = z.shape
        out = np.empty(M)
        # Pre-compute inverse sqrt divisors
        inv_sqrt = np.empty(N)
        for j in range(N):
            inv_sqrt[j] = 1.0 / np.sqrt(1.0 + j)
        for i in prange(M):
            s = 0.0
            p = 1.0
            for j in range(N):
                zj = z[i, j]
                s += zj * zj
                p *= np.cos(zj * inv_sqrt[j])
            out[i] = 1.0 + s / 4000.0 - p
        return out

    @njit(cache=True, parallel=True, boundscheck=False, nogil=True)
    def escaffer6_core_nb(z):
        """Expanded Scaffer F6 with circular wrap.

        C reference: ``escaffer6_func`` (lines 806-817).
        Circular pairwise sum: pairs (z_j, z_{j+1}) for j=0..N-2,
        plus the wrap-around pair (z_{N-1}, z_0).
        """
        M, N = z.shape
        out = np.empty(M)
        for i in prange(M):
            f_val = 0.0
            for j in range(N - 1):
                ss = z[i, j] ** 2 + z[i, j + 1] ** 2
                t1 = np.sin(np.sqrt(ss)) ** 2
                t2 = (1.0 + 0.001 * ss) ** 2
                f_val += 0.5 + (t1 - 0.5) / t2
            # Circular wrap: last pair (z[N-1], z[0])
            ss = z[i, N - 1] ** 2 + z[i, 0] ** 2
            t1 = np.sin(np.sqrt(ss)) ** 2
            t2 = (1.0 + 0.001 * ss) ** 2
            f_val += 0.5 + (t1 - 0.5) / t2
            out[i] = f_val
        return out

    @njit(cache=True, parallel=True, boundscheck=False, nogil=True)
    def grie_rosen_core_nb(z):
        """Expanded Griewank-Rosenbrock with circular wrap.

        C reference: ``grie_rosen_func`` (lines 773-784).
        Circular chain: for each consecutive pair, compute Rosenbrock term
        ``temp = 100*(z_j^2 - z_{j+1})^2 + (z_j - 1)^2``, then apply
        Griewank: ``temp^2/4000 - cos(temp) + 1``.  Includes wrap-around.
        """
        M, N = z.shape
        out = np.empty(M)
        for i in prange(M):
            f_val = 0.0
            for j in range(N - 1):
                t1 = z[i, j] ** 2 - z[i, j + 1]
                t2 = z[i, j] - 1.0
                temp = 100.0 * t1 * t1 + t2 * t2
                f_val += temp * temp / 4000.0 - np.cos(temp) + 1.0
            # Circular wrap: (z[N-1], z[0])
            t1 = z[i, N - 1] ** 2 - z[i, 0]
            t2 = z[i, N - 1] - 1.0
            temp = 100.0 * t1 * t1 + t2 * t2
            f_val += temp * temp / 4000.0 - np.cos(temp) + 1.0
            out[i] = f_val
        return out

    @njit(cache=True, parallel=True, boundscheck=False, nogil=True)
    def schaffer_F7_core_nb(y):
        """Schaffer F7: [sum(sqrt(s) + sqrt(s)*sin^2(50*s^0.2)) / (N-1)]^2.

        C reference: ``schaffer_F7_func`` (lines 392-400).
        Consecutive-pair formula using ``s = sqrt(y_j^2 + y_{j+1}^2)``.
        """
        M, N = y.shape
        out = np.empty(M)
        Nm1 = float(N - 1)
        for i in prange(M):
            s = 0.0
            for j in range(N - 1):
                si = np.sqrt(y[i, j] ** 2 + y[i, j + 1] ** 2)
                s += np.sqrt(si) + np.sqrt(si) * np.sin(50.0 * si ** 0.2) ** 2
            out[i] = (s / Nm1) ** 2
        return out

    @njit(cache=True, parallel=True, boundscheck=False, nogil=True)
    def katsuura_core_nb(y, N):
        """Katsuura product formula.

        C reference: ``katsuura_func`` (lines 670-683).
        Inner sum over k=1..32 with ``2^k`` powers.
        Pre-computes ``pow2k = 2.0^k`` array to avoid redundant
        exponentiation in the innermost loop.
        """
        M = y.shape[0]
        tmp3 = N ** 1.2
        # Pre-compute powers of 2 (was recomputed per inner iteration)
        pow2k = np.empty(32)
        inv_pow2k = np.empty(32)
        for k in range(32):
            pow2k[k] = 2.0 ** (k + 1)
            inv_pow2k[k] = 1.0 / pow2k[k]
        tmp1 = 10.0 / N / N  # Hoisted outside prange (constant)
        out = np.empty(M)
        for i in prange(M):
            prod_val = 1.0
            for j in range(N):
                temp = 0.0
                yij = y[i, j]
                for k in range(32):
                    tmp2 = pow2k[k] * yij
                    temp += abs(tmp2 - np.floor(tmp2 + 0.5)) * inv_pow2k[k]
                prod_val *= (1.0 + (j + 1) * temp) ** (10.0 / tmp3)
            out[i] = prod_val * tmp1 - tmp1
        return out

    @njit(cache=True, parallel=True, boundscheck=False, nogil=True)
    def bi_rastrigin_core_nb(tmpx, z2, mu0, mu1, s, d, N):
        """Lunacek Bi-Rastrigin two-funnel formula.

        C reference: ``bi_rastrigin_func`` (lines 731-749).
        Computes::

            min(sum((tmpx-mu0)^2), s*sum((tmpx-mu1)^2) + d*N)
            + 10*(N - sum(cos(2*pi*z2)))

        where tmpx has already been sign-flipped and shifted by +mu0,
        and z2 has been rotated + conditioned.
        """
        M = tmpx.shape[0]
        out = np.empty(M)
        for i in prange(M):
            s1 = 0.0
            s2 = 0.0
            cos_sum = 0.0
            for j in range(N):
                diff0 = tmpx[i, j] - mu0
                diff1 = tmpx[i, j] - mu1
                s1 += diff0 * diff0
                s2 += diff1 * diff1
                cos_sum += np.cos(2.0 * PI * z2[i, j])
            tmp2 = s * s2 + d * N
            out[i] = min(s1, tmp2) + 10.0 * (N - cos_sum)
        return out

    @njit(cache=True, parallel=True, boundscheck=False, nogil=True)
    def step_rastrigin_quant_nb(z):
        """Step quantisation for Non-continuous Rotated Rastrigin (F13).

        C reference: ``step_rastrigin_func`` (lines 570-574)::

            if (fabs(z[i]) > 0.5)
                z[i] = floor(2*z[i] + 0.5) / 2;

        Applies the quantisation in-place semantics but returns a new array.
        """
        M, N = z.shape
        out = np.empty_like(z)
        for i in prange(M):
            for j in range(N):
                zj = z[i, j]
                if abs(zj) > 0.5:
                    out[i, j] = np.floor(2.0 * zj + 0.5) / 2.0
                else:
                    out[i, j] = zj
        return out

    # =====================================================================
    # Composition weight calculation
    # =====================================================================

    @njit(cache=True, parallel=True, boundscheck=False, nogil=True)
    def cf_cal_nb(x, comp_shifts_N, deltas, biases, fit_values):
        """Composition weight calculation -- matches C ``cf_cal`` exactly.

        C reference: ``cf_cal`` (lines 1047-1085).
        Distance-weighted blending of K component fitness values.

        Parameters
        ----------
        x : (M, N)
            Population matrix.
        comp_shifts_N : (K, N)
            Shift vectors already sliced to N columns.
        deltas : (K,)
            Sigma (spread) values per component.
        biases : (K,)
            Per-component bias offsets.
        fit_values : (K, M)
            Raw fitness from each component evaluation.

        Weight formula per component k::

            w_k = (1/sqrt(dist_sq)) * exp(-dist_sq / (2*N*delta_k^2))
            w_k = INF  when dist_sq == 0  (x at component optimum)

        Returns ``sum((w_k / sum_w) * (fit_k + bias_k))``.
        """
        M, N = x.shape
        K = deltas.shape[0]
        out = np.empty(M)

        for i in prange(M):
            w = np.empty(K)
            w_max = 0.0
            w_sum = 0.0

            for k in range(K):
                dist_sq = 0.0
                for j in range(N):
                    d = x[i, j] - comp_shifts_N[k, j]
                    dist_sq += d * d
                if dist_sq != 0.0:
                    w[k] = (1.0 / np.sqrt(dist_sq)) * np.exp(
                        -dist_sq / (2.0 * N * deltas[k] * deltas[k])
                    )
                else:
                    w[k] = INF_VAL
                if w[k] > w_max:
                    w_max = w[k]

            for k in range(K):
                w_sum += w[k]

            if w_max == 0.0:
                for k in range(K):
                    w[k] = 1.0
                w_sum = float(K)

            s = 0.0
            for k in range(K):
                s += (w[k] / w_sum) * (fit_values[k, i] + biases[k])
            out[i] = s

        return out

else:
    # Numba unavailable -- every export is None; callers fall back to
    # pure NumPy under ``if _NB_FN is None:``.
    osz_func_nb = None
    asy_func_nb = None
    conditioning_nb = None
    sphere_nb = None
    bent_cigar_core_nb = None
    elliptic_core_nb = None
    discus_core_nb = None
    dif_powers_core_nb = None
    rastrigin_core_nb = None
    schwefel_core_nb = None
    rosenbrock_core_nb = None
    ackley_core_nb = None
    weierstrass_core_nb = None
    griewank_core_nb = None
    escaffer6_core_nb = None
    grie_rosen_core_nb = None
    schaffer_F7_core_nb = None
    katsuura_core_nb = None
    bi_rastrigin_core_nb = None
    step_rastrigin_quant_nb = None
    cf_cal_nb = None


# ===========================================================================
# Warmup -- trigger JIT compilation of all cached kernels
# ===========================================================================
def warmup() -> None:
    """Trigger JIT compilation of all CEC2013 kernels with tiny inputs.

    Retained pre-compilation utility (no runner call sites in this project:
    the campaign runner warms each worker by evaluating a probe cell instead
    — ``warm_benchmark_cells`` in ``gsk_family.runners.performance``).
    Calling it ensures subsequent calls
    to any ``*_nb`` function do not pay the compilation cost.  Uses minimal
    array sizes (2 rows, 3 columns) to minimise compilation overhead while
    ensuring all code paths are cached.  Skipped gracefully when numba is
    not installed.

    The warmup payload is drawn from a **fixed** ``default_rng(0xDEC0DE)``
    instance (audit finding Pattern B) so the JIT specialisation input is
    bit-identical across runs.  See ``cec2017/_numba.py:warmup`` for the
    full rationale -- determinism is free here.
    """
    if not HAS_NUMBA:
        return
    _warmup_rng = np.random.default_rng(0xDEC0DE)
    n, d = 2, 3
    xc = np.ascontiguousarray(_warmup_rng.standard_normal((n, d)), dtype=np.float64)
    Os = np.zeros(d)
    prev = xc.copy()
    # Transform kernels
    osz_func_nb(xc)
    asy_func_nb(xc, prev, 0.5)
    conditioning_nb(xc, 10.0)
    # Core formula kernels
    sphere_nb(xc, Os, d)
    rastrigin_core_nb(xc)
    schwefel_core_nb(xc, d)
    rosenbrock_core_nb(xc)
    ackley_core_nb(xc)
    weierstrass_core_nb(xc, d)
    griewank_core_nb(xc)
    escaffer6_core_nb(xc)
    grie_rosen_core_nb(xc)
    schaffer_F7_core_nb(xc)
    katsuura_core_nb(xc, d)
    bent_cigar_core_nb(xc, d)
    elliptic_core_nb(xc, d)
    discus_core_nb(xc, d)
    dif_powers_core_nb(xc, d)
    bi_rastrigin_core_nb(xc, xc, 2.5, -1.0, 0.9, 1.0, d)
    step_rastrigin_quant_nb(xc)
    # Composition weight kernel
    shifts_K = np.zeros((2, d))
    deltas = np.ones(2)
    biases = np.zeros(2)
    fit = np.zeros((2, n))
    cf_cal_nb(xc, shifts_K, deltas, biases, fit)


# ---------------------------------------------------------------------------
# Cross-module sanity check for the composition INF sentinel.
#
# ``transforms.INF`` is the single source of truth for this suite (see
# ``transforms.py``).  ``INF_VAL`` above is a Numba-side mirror that has to
# be a module-level Python float so it can be captured by ``@njit`` closures
# (Numba cannot import Python attributes from inside a JIT'd function).
# This assertion catches accidental drift between the two if either is
# edited in isolation.
# ---------------------------------------------------------------------------
from .transforms import INF as _TRANSFORMS_INF  # noqa: E402

if INF_VAL != _TRANSFORMS_INF:
    raise RuntimeError(
        f"cec2013._numba.INF_VAL ({INF_VAL!r}) != cec2013.transforms.INF "
        f"({_TRANSFORMS_INF!r}) -- both must agree to keep composition "
        f"weights bit-identical between the Numba and NumPy paths."
    )

del _TRANSFORMS_INF


__all__ = [
    "HAS_NUMBA",
    "INF_VAL",
    "osz_func_nb",
    "asy_func_nb",
    "conditioning_nb",
    "sphere_nb",
    "bent_cigar_core_nb",
    "elliptic_core_nb",
    "discus_core_nb",
    "dif_powers_core_nb",
    "rastrigin_core_nb",
    "schwefel_core_nb",
    "rosenbrock_core_nb",
    "ackley_core_nb",
    "weierstrass_core_nb",
    "griewank_core_nb",
    "escaffer6_core_nb",
    "grie_rosen_core_nb",
    "schaffer_F7_core_nb",
    "katsuura_core_nb",
    "bi_rastrigin_core_nb",
    "step_rastrigin_quant_nb",
    "cf_cal_nb",
    "warmup",
]
