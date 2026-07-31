"""CEC2013LSGO Numba-accelerated kernels.

Fused single-pass kernels that combine shift + transforms + evaluation
to eliminate intermediate array allocations at D=1000.

Kernel categories
-----------------
1. **Transform kernels** (3): standalone T_osz, T_asy, Lambda.
   Used by :mod:`.transforms` NumPy fallback path when basic functions
   are called on already-shifted/rotated input.

2. **Fused transform+evaluate cores** (6): T_osz+formula, T_osz+T_asy+Lambda+formula,
   plus sphere and rosenbrock (no transforms).
   Used by :mod:`.basic` on post-shift or post-rotation input.

3. **Shifted full-D kernels** (5): shift+transforms+formula in one pass.
   Used by :mod:`.composite` for F1-F3/F12/F15 — eliminates the
   ``M × 1000`` intermediate ``z = x - xopt`` allocation entirely.

4. **Fused group kernels** (4): shift+rotate+transforms+formula for ALL
   groups in a single call, with ``prange(M)`` outer parallelism.
   Used by :mod:`.composite` for F4-F14 — eliminates the Python loop
   over 7-20 groups, per-group fancy indexing, and per-group BLAS dispatch.
   Delivers 3-7× speedup for group functions at D≥905.

5. **Fused separable-remainder kernels** (4): shift+transforms+formula on
   indexed columns for the 700-dim separable remainder of F4-F7.
   Reads directly from the population matrix via column indices — no
   M×700 temporary allocation, no Python-level fancy indexing.
   Delivers 1.8-3.2× speedup for F4-F7.

Parallelization strategy
------------------------
All kernels use ``prange(M)`` as the outer parallel loop (across
solutions) and sequential inner loops (across dimensions/groups).
This creates cache-friendly row-major access patterns.  Scratch
buffers are allocated as ``(M, max_d)`` — each prange thread gets
its own row, ensuring thread safety without explicit locking.

All kernels expect C-contiguous float64 input (enforced by callers
via ``_ensure_f64``).

Decorator policy
~~~~~~~~~~~~~~~~
Most kernels use the project's canonical parallel decorator::

    @njit(cache=True, parallel=True, fastmath=True, boundscheck=False, nogil=True)

matching the per-suite ``_numba.py`` files for
CEC2017 and CEC2011.  (CEC2013 is deliberately stricter: it uses
``fastmath=False`` on **every** kernel, not just Category 4 reductions.
Do not assume the same policy applies when porting kernels between
CEC2013 and CEC2013LSGO.)  ``fastmath=True`` is safe for the standalone
transforms (Category 1), the fused transform+evaluate cores (Category 2),
the shifted full-D kernels (Category 3) and the separable-remainder
kernels (Category 5): each does a single reduction per individual with no
cross-component accumulation, matching the CEC2017 basic-kernel policy.

The **4 group kernels** in Category 4 (``group_elliptic_nb``,
``group_rastrigin_nb``, ``group_ackley_nb``, ``group_schwefel_nb``) are
the single exception — they drop ``fastmath=True`` because they
accumulate ``out[m] += weights[g] * (...)`` across groups, which is the
LSGO analogue of CEC2017's ``cf_cal`` composition-weight reduction.
Without that guard, LLVM would be free to fuse mul+add into FMA and
reorder associative ops across ``g``, producing last-ulp drift across
CPU ISAs (AVX2 vs AVX-512) and Numba/LLVM versions — and breaking
bit-for-bit reproducibility of the published F4-F14 benchmark numbers.
See audit finding H-2 and the comment block immediately above
``group_elliptic_nb``.

``boundscheck=False`` and ``nogil=True`` are required on every kernel
to release the GIL inside ``ProcessPoolExecutor`` workers without
contention.
"""

from __future__ import annotations

__all__ = [
    # Category 1: Standalone transforms
    "transform_osz_nb", "transform_asy_nb", "lambda_transform_nb",
    # Category 2: Fused transform+evaluate cores
    "fused_osz_elliptic_nb", "fused_osz_asy_lam_rastrigin_nb",
    "fused_osz_asy_lam_ackley_nb", "fused_osz_asy_schwefel_nb",
    "sphere_nb", "rosenbrock_nb",
    # Category 3: Shifted full-D kernels
    "shifted_osz_elliptic_nb", "shifted_osz_asy_lam_rastrigin_nb",
    "shifted_osz_asy_lam_ackley_nb", "shifted_rosenbrock_nb",
    "shifted_osz_asy_schwefel_nb",
    # Category 4: Fused group kernels
    "group_elliptic_nb", "group_rastrigin_nb",
    "group_ackley_nb", "group_schwefel_nb",
    # Category 5: Fused separable-remainder kernels
    "sep_osz_elliptic_nb", "sep_osz_asy_lam_rastrigin_nb",
    "sep_osz_asy_lam_ackley_nb", "sep_sphere_nb",
    # Category 6: RAW-ackley twins (ackley_variant='raw' — F3/F6/F10; MOS's
    # LaTorre/official reference, transforms dropped per benchmark_func.m)
    "shifted_ackley_raw_nb", "group_ackley_raw_nb", "sep_ackley_raw_nb",
    # Utilities
    "warmup", "HAS_NUMBA",
]

import math

import numpy as np

try:
    from numba import njit, prange
    HAS_NUMBA = True
except Exception:  # not just ImportError: llvmlite can raise OSError under memory pressure
    HAS_NUMBA = False

PI = np.pi
E_VAL = np.e

# =========================================================================

if HAS_NUMBA:

    # =================================================================
    # 1. Standalone transform kernels
    # =================================================================

    @njit(cache=True, parallel=True, fastmath=True, boundscheck=False, nogil=True)
    def transform_osz_nb(z):
        """Oscillation transform — ALL dimensions (LSGO-specific)."""
        M, N = z.shape
        out = np.empty_like(z)
        for m in prange(M):
            for i in range(N):
                xi = z[m, i]
                if xi != 0.0:
                    xx = math.log(abs(xi))
                    if xi > 0.0:
                        c1, c2, sx = 10.0, 7.9, 1.0
                    else:
                        c1, c2, sx = 5.5, 3.1, -1.0
                    out[m, i] = sx * math.exp(
                        xx + 0.049 * (math.sin(c1 * xx) + math.sin(c2 * xx))
                    )
                else:
                    out[m, i] = 0.0
        return out

    @njit(cache=True, parallel=True, fastmath=True, boundscheck=False, nogil=True)
    def transform_asy_nb(z, beta):
        """Asymmetry transform: z_i^(1+beta*i/(N-1)*sqrt(z_i)) for z_i > 0.

        Uses ``np.empty`` + explicit else branch instead of ``z.copy()``
        to eliminate the O(M*N) memcpy — single write-pass only.
        """
        M, N = z.shape
        out = np.empty_like(z)
        Nm1 = max(N - 1.0, 1.0)
        for m in prange(M):
            for i in range(N):
                xi = z[m, i]
                if xi > 0.0:
                    exp = 1.0 + beta * i / Nm1 * math.sqrt(xi)
                    out[m, i] = xi ** exp
                else:
                    out[m, i] = xi
        return out

    @njit(cache=True, parallel=True, fastmath=True, boundscheck=False, nogil=True)
    def lambda_transform_nb(z, alpha):
        """Ill-conditioning: z_i *= alpha^(0.5*i/(N-1))."""
        M, N = z.shape
        out = np.empty_like(z)
        Nm1 = max(float(N - 1), 1.0)
        # Precompute Lambda scaling — O(N) vs O(M*N) pow() calls
        _lc = np.empty(N, dtype=np.float64)
        for i in range(N):
            _lc[i] = alpha ** (0.5 * i / Nm1)
        for m in prange(M):
            for i in range(N):
                out[m, i] = z[m, i] * _lc[i]
        return out

    # =================================================================
    # 2. Fused transform+evaluate cores (post-shift/rotation input)
    # =================================================================

    @njit(cache=True, parallel=True, fastmath=True, boundscheck=False, nogil=True)
    def fused_osz_elliptic_nb(z):
        """T_osz + elliptic: single-pass, no intermediate arrays."""
        M, N = z.shape
        out = np.empty(M, dtype=np.float64)
        Nm1 = max(N - 1.0, 1.0)
        # Precompute elliptic coefficients — O(N) vs O(M·N) pow() calls
        _ec = np.empty(N, dtype=np.float64)
        for i in range(N):
            _ec[i] = 10.0 ** (6.0 * i / Nm1)
        for m in prange(M):
            s = 0.0
            for i in range(N):
                zi = z[m, i]
                # T_osz
                if zi != 0.0:
                    hat = math.log(abs(zi))
                    if zi > 0.0:
                        c1, c2, sx = 10.0, 7.9, 1.0
                    else:
                        c1, c2, sx = 5.5, 3.1, -1.0
                    zi = sx * math.exp(
                        hat + 0.049 * (math.sin(c1 * hat) + math.sin(c2 * hat))
                    )
                # elliptic
                s += _ec[i] * zi * zi
            out[m] = s
        return out

    @njit(cache=True, parallel=True, fastmath=True, boundscheck=False, nogil=True)
    def fused_osz_asy_lam_rastrigin_nb(z):
        """T_osz + T_asy(0.2) + Lambda(10) + rastrigin: single-pass."""
        M, N = z.shape
        out = np.empty(M, dtype=np.float64)
        Nm1 = max(N - 1.0, 1.0)
        beta = 0.2
        alpha = 10.0
        # Precompute Lambda scaling — O(N) vs O(M·N) pow() calls
        _lc = np.empty(N, dtype=np.float64)
        for i in range(N):
            _lc[i] = alpha ** (0.5 * i / Nm1)
        for m in prange(M):
            s = 0.0
            for i in range(N):
                zi = z[m, i]
                # T_osz
                if zi != 0.0:
                    hat = math.log(abs(zi))
                    if zi > 0.0:
                        c1, c2, sx = 10.0, 7.9, 1.0
                    else:
                        c1, c2, sx = 5.5, 3.1, -1.0
                    zi = sx * math.exp(
                        hat + 0.049 * (math.sin(c1 * hat) + math.sin(c2 * hat))
                    )
                # T_asy
                if zi > 0.0:
                    exp = 1.0 + beta * i / Nm1 * math.sqrt(zi)
                    zi = zi ** exp
                # Lambda
                zi *= _lc[i]
                # rastrigin
                s += zi * zi - 10.0 * math.cos(2.0 * PI * zi) + 10.0
            out[m] = s
        return out

    @njit(cache=True, parallel=True, fastmath=True, boundscheck=False, nogil=True)
    def fused_osz_asy_lam_ackley_nb(z):
        """T_osz + T_asy(0.2) + Lambda(10) + ackley: single-pass."""
        M, N = z.shape
        out = np.empty(M, dtype=np.float64)
        Nm1 = max(N - 1.0, 1.0)
        beta = 0.2
        alpha = 10.0
        # Precompute Lambda scaling — O(N) vs O(M·N) pow() calls
        _lc = np.empty(N, dtype=np.float64)
        for i in range(N):
            _lc[i] = alpha ** (0.5 * i / Nm1)
        for m in prange(M):
            s1 = 0.0
            s2 = 0.0
            for i in range(N):
                zi = z[m, i]
                # T_osz
                if zi != 0.0:
                    hat = math.log(abs(zi))
                    if zi > 0.0:
                        c1, c2, sx = 10.0, 7.9, 1.0
                    else:
                        c1, c2, sx = 5.5, 3.1, -1.0
                    zi = sx * math.exp(
                        hat + 0.049 * (math.sin(c1 * hat) + math.sin(c2 * hat))
                    )
                # T_asy
                if zi > 0.0:
                    exp = 1.0 + beta * i / Nm1 * math.sqrt(zi)
                    zi = zi ** exp
                # Lambda
                zi *= _lc[i]
                # ackley accumulators
                s1 += zi * zi
                s2 += math.cos(2.0 * PI * zi)
            out[m] = (
                -20.0 * math.exp(-0.2 * math.sqrt(s1 / N))
                - math.exp(s2 / N) + 20.0 + E_VAL
            )
        return out

    @njit(cache=True, parallel=True, fastmath=True, boundscheck=False, nogil=True)
    def fused_osz_asy_schwefel_nb(z):
        """T_osz + T_asy(0.2) + schwefel_1_2 (fused cumsum): single-pass."""
        M, N = z.shape
        out = np.empty(M, dtype=np.float64)
        Nm1 = max(N - 1.0, 1.0)
        beta = 0.2
        for m in prange(M):
            running = 0.0
            total = 0.0
            for i in range(N):
                zi = z[m, i]
                # T_osz
                if zi != 0.0:
                    hat = math.log(abs(zi))
                    if zi > 0.0:
                        c1, c2, sx = 10.0, 7.9, 1.0
                    else:
                        c1, c2, sx = 5.5, 3.1, -1.0
                    zi = sx * math.exp(
                        hat + 0.049 * (math.sin(c1 * hat) + math.sin(c2 * hat))
                    )
                # T_asy
                if zi > 0.0:
                    exp = 1.0 + beta * i / Nm1 * math.sqrt(zi)
                    zi = zi ** exp
                # schwefel fused cumsum
                running += zi
                total += running * running
            out[m] = total
        return out

    @njit(cache=True, parallel=True, fastmath=True, boundscheck=False, nogil=True)
    def sphere_nb(z):
        """Sphere: sum(z_i^2), no transforms."""
        M, N = z.shape
        out = np.empty(M, dtype=np.float64)
        for m in prange(M):
            s = 0.0
            for i in range(N):
                zi = z[m, i]
                s += zi * zi
            out[m] = s
        return out

    @njit(cache=True, parallel=True, fastmath=True, boundscheck=False, nogil=True)
    def rosenbrock_nb(z):
        """Rosenbrock: sum(100*(z_j^2 - z_{j+1})^2 + (z_j-1)^2), no transforms."""
        M, N = z.shape
        out = np.empty(M, dtype=np.float64)
        for m in prange(M):
            s = 0.0
            for i in range(N - 1):
                zi = z[m, i]
                zi1 = z[m, i + 1]
                t1 = zi * zi - zi1
                t2 = zi - 1.0
                s += 100.0 * t1 * t1 + t2 * t2
            out[m] = s
        return out

    # =================================================================
    # 3. Shifted full-D kernels (avoids M*1000 allocation)
    # =================================================================

    @njit(cache=True, parallel=True, fastmath=True, boundscheck=False, nogil=True)
    def shifted_osz_elliptic_nb(x, xopt):
        """F1: shift + T_osz + elliptic in one pass."""
        M, N = x.shape
        out = np.empty(M, dtype=np.float64)
        Nm1 = max(N - 1.0, 1.0)
        # Precompute elliptic coefficients — O(N) vs O(M·N) pow() calls
        _ec = np.empty(N, dtype=np.float64)
        for i in range(N):
            _ec[i] = 10.0 ** (6.0 * i / Nm1)
        for m in prange(M):
            s = 0.0
            for i in range(N):
                zi = x[m, i] - xopt[i]
                if zi != 0.0:
                    hat = math.log(abs(zi))
                    if zi > 0.0:
                        c1, c2, sx = 10.0, 7.9, 1.0
                    else:
                        c1, c2, sx = 5.5, 3.1, -1.0
                    zi = sx * math.exp(
                        hat + 0.049 * (math.sin(c1 * hat) + math.sin(c2 * hat))
                    )
                s += _ec[i] * zi * zi
            out[m] = s
        return out

    @njit(cache=True, parallel=True, fastmath=True, boundscheck=False, nogil=True)
    def shifted_osz_asy_lam_rastrigin_nb(x, xopt):
        """F2: shift + T_osz + T_asy(0.2) + Lambda(10) + rastrigin."""
        M, N = x.shape
        out = np.empty(M, dtype=np.float64)
        Nm1 = max(N - 1.0, 1.0)
        beta = 0.2
        alpha = 10.0
        # Precompute Lambda scaling — O(N) vs O(M·N) pow() calls
        _lc = np.empty(N, dtype=np.float64)
        for i in range(N):
            _lc[i] = alpha ** (0.5 * i / Nm1)
        for m in prange(M):
            s = 0.0
            for i in range(N):
                zi = x[m, i] - xopt[i]
                if zi != 0.0:
                    hat = math.log(abs(zi))
                    if zi > 0.0:
                        c1, c2, sx = 10.0, 7.9, 1.0
                    else:
                        c1, c2, sx = 5.5, 3.1, -1.0
                    zi = sx * math.exp(
                        hat + 0.049 * (math.sin(c1 * hat) + math.sin(c2 * hat))
                    )
                if zi > 0.0:
                    exp = 1.0 + beta * i / Nm1 * math.sqrt(zi)
                    zi = zi ** exp
                zi *= _lc[i]
                s += zi * zi - 10.0 * math.cos(2.0 * PI * zi) + 10.0
            out[m] = s
        return out

    @njit(cache=True, parallel=True, fastmath=True, boundscheck=False, nogil=True)
    def shifted_osz_asy_lam_ackley_nb(x, xopt):
        """F3: shift + T_osz + T_asy(0.2) + Lambda(10) + ackley."""
        M, N = x.shape
        out = np.empty(M, dtype=np.float64)
        Nm1 = max(N - 1.0, 1.0)
        beta = 0.2
        alpha = 10.0
        # Precompute Lambda scaling — O(N) vs O(M·N) pow() calls
        _lc = np.empty(N, dtype=np.float64)
        for i in range(N):
            _lc[i] = alpha ** (0.5 * i / Nm1)
        for m in prange(M):
            s1 = 0.0
            s2 = 0.0
            for i in range(N):
                zi = x[m, i] - xopt[i]
                if zi != 0.0:
                    hat = math.log(abs(zi))
                    if zi > 0.0:
                        c1, c2, sx = 10.0, 7.9, 1.0
                    else:
                        c1, c2, sx = 5.5, 3.1, -1.0
                    zi = sx * math.exp(
                        hat + 0.049 * (math.sin(c1 * hat) + math.sin(c2 * hat))
                    )
                if zi > 0.0:
                    exp = 1.0 + beta * i / Nm1 * math.sqrt(zi)
                    zi = zi ** exp
                zi *= _lc[i]
                s1 += zi * zi
                s2 += math.cos(2.0 * PI * zi)
            out[m] = (
                -20.0 * math.exp(-0.2 * math.sqrt(s1 / N))
                - math.exp(s2 / N) + 20.0 + E_VAL
            )
        return out

    @njit(cache=True, parallel=True, fastmath=True, boundscheck=False, nogil=True)
    def shifted_ackley_raw_nb(x, xopt):
        """F3 (RAW variant): shift + ackley with NO T_osz/T_asy/Lambda.

        The official CEC2013-LSGO ``benchmark_func.m`` comments the ackley
        transform chain out, and LaTorre's MOS competition reference uses this
        raw form (MOS's published F3=1.69e-12 is only reproducible here).
        Selected per optimizer via ``ackley_variant='raw'`` — see
        ``composite.py`` / ``_kernel_mode.ackley_raw_scope``.  The default
        suite path keeps the transformed twin (Molina's package, used by
        shade-ils).  Bitwise-parallel to the raw C++ ``Benchmarks::ackley_raw``.
        """
        M, N = x.shape
        out = np.empty(M, dtype=np.float64)
        for m in prange(M):
            s1 = 0.0
            s2 = 0.0
            for i in range(N):
                zi = x[m, i] - xopt[i]
                s1 += zi * zi
                s2 += math.cos(2.0 * PI * zi)
            out[m] = (
                -20.0 * math.exp(-0.2 * math.sqrt(s1 / N))
                - math.exp(s2 / N) + 20.0 + E_VAL
            )
        return out

    @njit(cache=True, parallel=True, fastmath=True, boundscheck=False, nogil=True)
    def shifted_rosenbrock_nb(x, xopt):
        """F12: shift + rosenbrock in one pass."""
        M, N = x.shape
        out = np.empty(M, dtype=np.float64)
        for m in prange(M):
            s = 0.0
            prev = x[m, 0] - xopt[0]
            for i in range(N - 1):
                curr = x[m, i + 1] - xopt[i + 1]
                t1 = prev * prev - curr
                t2 = prev - 1.0
                s += 100.0 * t1 * t1 + t2 * t2
                prev = curr
            out[m] = s
        return out

    @njit(cache=True, parallel=True, fastmath=True, boundscheck=False, nogil=True)
    def shifted_osz_asy_schwefel_nb(x, xopt):
        """F15: shift + T_osz + T_asy(0.2) + schwefel_1_2."""
        M, N = x.shape
        out = np.empty(M, dtype=np.float64)
        Nm1 = max(N - 1.0, 1.0)
        beta = 0.2
        for m in prange(M):
            running = 0.0
            total = 0.0
            for i in range(N):
                zi = x[m, i] - xopt[i]
                if zi != 0.0:
                    hat = math.log(abs(zi))
                    if zi > 0.0:
                        c1, c2, sx = 10.0, 7.9, 1.0
                    else:
                        c1, c2, sx = 5.5, 3.1, -1.0
                    zi = sx * math.exp(
                        hat + 0.049 * (math.sin(c1 * hat) + math.sin(c2 * hat))
                    )
                if zi > 0.0:
                    exp = 1.0 + beta * i / Nm1 * math.sqrt(zi)
                    zi = zi ** exp
                running += zi
                total += running * running
            out[m] = total
        return out

    # =================================================================
    # 4. Fused group kernels — eliminates Python loop over groups
    #
    # For partially-separable functions F4-F14, these kernels replace
    # the Python-level loop over groups with a single Numba call.
    #
    # Each kernel:
    #   prange(M) outer  →  parallel across solutions
    #   range(n_groups)  →  sequential: extract → shift → rotate → eval
    #
    # Data layout (pre-flattened for Numba compatibility):
    #   idx_flat     : (T,) int64 — concat 0-based column indices
    #   xopt_flat    : (T,) float64 — concat per-group shift values
    #   rot_flat     : (R,) float64 — concat row-major rotation matrices
    #   rot_offsets  : (n_groups+1,) int64 — cumsum of s_i^2
    #   group_starts : (n_groups+1,) int64 — cumsum of group sizes
    #   weights      : (n_groups,) float64 — per-group weights
    #
    # Gains: eliminates per-group fancy indexing + BLAS dispatch +
    # Numba call overhead.  For F8-F11 (20 groups × M=50), this
    # removes ~20 Python iterations per evaluation batch.
    # =================================================================

    # Audit H-2: the 4 ``group_*_nb`` kernels (F4-F7, F11, F13, F14) drop
    # ``fastmath=True`` because they accumulate ``out[m] += weights[g] *
    # (...)`` across groups inside a ``prange(m)`` loop.  With fastmath,
    # the LLVM backend is free to fuse mul+add into FMA and reorder
    # associative ops across ``g``, which would produce last-ulp drift
    # across CPU ISAs (AVX2 vs AVX-512) and Numba/LLVM versions.  This
    # mirrors the CEC2017 ``_cf_cal_nb`` policy (audit finding Pattern A
    # in ``cec2017/_numba.py``): reductions that combine per-component
    # contributions are the single exception to the project fastmath
    # rule, because they feed the published benchmark numbers.
    @njit(cache=True, parallel=True, boundscheck=False, nogil=True)
    def group_elliptic_nb(x, idx_flat, xopt_flat, rot_flat,
                          rot_offsets, group_starts, weights, n_groups):
        """Fused shift+rotate+T_osz+elliptic for all groups.

        Used by F4 (7 groups + sep elliptic) and F8 (20 groups).
        Inline rotation avoids BLAS dispatch overhead for small
        group sizes (25/50/100).

        Parameters
        ----------
        x            : (M, D) float64 — population matrix.
        idx_flat     : (T,) int64 — concatenated group column indices.
        xopt_flat    : (T,) float64 — concatenated group shift values.
        rot_flat     : (R,) float64 — concatenated row-major R matrices.
        rot_offsets  : (G+1,) int64 — cumsum of s_i^2 (rotation starts).
        group_starts : (G+1,) int64 — cumsum of group sizes (dim starts).
        weights      : (G,) float64 — per-group multiplicative weights.
        n_groups     : int — number of groups (G).

        Returns
        -------
        (M,) float64 — weighted sum of per-group elliptic values.
        """
        M = x.shape[0]
        out = np.zeros(M, dtype=np.float64)
        # Pre-compute max group size for scratch buffer allocation.
        max_d = 0
        for g in range(n_groups):
            d = group_starts[g + 1] - group_starts[g]
            if d > max_d:
                max_d = d
        # Per-solution scratch: thread-safe because prange(M) assigns
        # disjoint rows to different threads.
        z_buf = np.empty((M, max_d), dtype=np.float64)
        r_buf = np.empty((M, max_d), dtype=np.float64)
        # Precompute per-group elliptic coefficients — O(T) pow() calls
        # vs O(M*T) inside prange.  Indexed by group_starts offsets.
        T = group_starts[n_groups]
        _ec = np.empty(T, dtype=np.float64)
        for g in range(n_groups):
            gs_g = group_starts[g]
            d_g = group_starts[g + 1] - gs_g
            dm1_g = max(d_g - 1.0, 1.0)
            for i in range(d_g):
                _ec[gs_g + i] = 10.0 ** (6.0 * i / dm1_g)
        for m in prange(M):
            for g in range(n_groups):
                gs = group_starts[g]
                ge = group_starts[g + 1]
                d = ge - gs
                ro = rot_offsets[g]
                # --- Step 1: Extract + shift ---
                # z[j] = x[m, column_index_j] - shift_j
                for j in range(d):
                    z_buf[m, j] = x[m, idx_flat[gs + j]] - xopt_flat[gs + j]
                # --- Step 2: Rotate ---
                # r[i] = sum_j z[j] * R[i,j]  where R is row-major
                # Matches C++ multiply(vector, matrix, dim).
                for i in range(d):
                    acc = 0.0
                    for j in range(d):
                        acc += z_buf[m, j] * rot_flat[ro + i * d + j]
                    r_buf[m, i] = acc
                # --- Step 3: T_osz + elliptic ---
                s = 0.0
                for i in range(d):
                    zi = r_buf[m, i]
                    # T_osz (oscillation on every element)
                    if zi != 0.0:
                        hat = math.log(abs(zi))
                        if zi > 0.0:
                            c1v, c2v, sx = 10.0, 7.9, 1.0
                        else:
                            c1v, c2v, sx = 5.5, 3.1, -1.0
                        zi = sx * math.exp(
                            hat + 0.049 * (math.sin(c1v * hat)
                                           + math.sin(c2v * hat)))
                    s += _ec[gs + i] * zi * zi
                out[m] += weights[g] * s
        return out

    # Audit H-2: ``fastmath=False`` — see group_elliptic_nb rationale.
    @njit(cache=True, parallel=True, boundscheck=False, nogil=True)
    def group_rastrigin_nb(x, idx_flat, xopt_flat, rot_flat,
                           rot_offsets, group_starts, weights, n_groups):
        """Fused shift+rotate+T_osz+T_asy(0.2)+Lambda(10)+rastrigin.

        Used by F5 (7 groups + sep rastrigin) and F9 (20 groups).
        Transform chain: T_osz → T_asy(β=0.2) → Λ(α=10) → rastrigin.
        """
        M = x.shape[0]
        out = np.zeros(M, dtype=np.float64)
        beta = 0.2
        alpha = 10.0
        max_d = 0
        for g in range(n_groups):
            d = group_starts[g + 1] - group_starts[g]
            if d > max_d:
                max_d = d
        z_buf = np.empty((M, max_d), dtype=np.float64)
        r_buf = np.empty((M, max_d), dtype=np.float64)
        # Precompute per-group Lambda scaling — O(T) pow() vs O(M*T)
        T = group_starts[n_groups]
        _lc = np.empty(T, dtype=np.float64)
        for g in range(n_groups):
            gs_g = group_starts[g]
            d_g = group_starts[g + 1] - gs_g
            dm1_g = max(d_g - 1.0, 1.0)
            for i in range(d_g):
                _lc[gs_g + i] = alpha ** (0.5 * i / dm1_g)
        for m in prange(M):
            for g in range(n_groups):
                gs = group_starts[g]
                ge = group_starts[g + 1]
                d = ge - gs
                ro = rot_offsets[g]
                # Extract + shift
                for j in range(d):
                    z_buf[m, j] = x[m, idx_flat[gs + j]] - xopt_flat[gs + j]
                # Rotate
                for i in range(d):
                    acc = 0.0
                    for j in range(d):
                        acc += z_buf[m, j] * rot_flat[ro + i * d + j]
                    r_buf[m, i] = acc
                # T_osz + T_asy + Lambda + rastrigin (fused single pass)
                dm1 = max(d - 1.0, 1.0)
                s = 0.0
                for i in range(d):
                    zi = r_buf[m, i]
                    # T_osz
                    if zi != 0.0:
                        hat = math.log(abs(zi))
                        if zi > 0.0:
                            c1v, c2v, sx = 10.0, 7.9, 1.0
                        else:
                            c1v, c2v, sx = 5.5, 3.1, -1.0
                        zi = sx * math.exp(
                            hat + 0.049 * (math.sin(c1v * hat)
                                           + math.sin(c2v * hat)))
                    # T_asy(β=0.2)
                    if zi > 0.0:
                        zi = zi ** (1.0 + beta * i / dm1 * math.sqrt(zi))
                    # Lambda(10): precomputed scaling
                    zi *= _lc[gs + i]
                    # Rastrigin formula
                    s += zi * zi - 10.0 * math.cos(2.0 * PI * zi) + 10.0
                out[m] += weights[g] * s
        return out

    # Audit H-2: ``fastmath=False`` — see group_elliptic_nb rationale.
    @njit(cache=True, parallel=True, boundscheck=False, nogil=True)
    def group_ackley_nb(x, idx_flat, xopt_flat, rot_flat,
                        rot_offsets, group_starts, weights, n_groups):
        """Fused shift+rotate+T_osz+T_asy(0.2)+Lambda(10)+ackley.

        Used by F6 (7 groups + sep ackley) and F10 (20 groups).
        Transform chain: T_osz → T_asy(β=0.2) → Λ(α=10) → ackley.
        Two accumulators (s1=sum z², s2=sum cos) merged in final formula.
        """
        M = x.shape[0]
        out = np.zeros(M, dtype=np.float64)
        beta = 0.2
        alpha = 10.0
        max_d = 0
        for g in range(n_groups):
            d = group_starts[g + 1] - group_starts[g]
            if d > max_d:
                max_d = d
        z_buf = np.empty((M, max_d), dtype=np.float64)
        r_buf = np.empty((M, max_d), dtype=np.float64)
        # Precompute per-group Lambda scaling — O(T) pow() vs O(M*T)
        T = group_starts[n_groups]
        _lc = np.empty(T, dtype=np.float64)
        for g in range(n_groups):
            gs_g = group_starts[g]
            d_g = group_starts[g + 1] - gs_g
            dm1_g = max(d_g - 1.0, 1.0)
            for i in range(d_g):
                _lc[gs_g + i] = alpha ** (0.5 * i / dm1_g)
        for m in prange(M):
            for g in range(n_groups):
                gs = group_starts[g]
                ge = group_starts[g + 1]
                d = ge - gs
                ro = rot_offsets[g]
                for j in range(d):
                    z_buf[m, j] = x[m, idx_flat[gs + j]] - xopt_flat[gs + j]
                for i in range(d):
                    acc = 0.0
                    for j in range(d):
                        acc += z_buf[m, j] * rot_flat[ro + i * d + j]
                    r_buf[m, i] = acc
                # T_osz + T_asy + Lambda + ackley (dual accumulator)
                dm1 = max(d - 1.0, 1.0)
                s1 = 0.0  # sum of z_i^2
                s2 = 0.0  # sum of cos(2π z_i)
                for i in range(d):
                    zi = r_buf[m, i]
                    # T_osz
                    if zi != 0.0:
                        hat = math.log(abs(zi))
                        if zi > 0.0:
                            c1v, c2v, sx = 10.0, 7.9, 1.0
                        else:
                            c1v, c2v, sx = 5.5, 3.1, -1.0
                        zi = sx * math.exp(
                            hat + 0.049 * (math.sin(c1v * hat)
                                           + math.sin(c2v * hat)))
                    # T_asy(β=0.2)
                    if zi > 0.0:
                        zi = zi ** (1.0 + beta * i / dm1 * math.sqrt(zi))
                    # Lambda(10): precomputed scaling
                    zi *= _lc[gs + i]
                    # Ackley accumulators
                    s1 += zi * zi
                    s2 += math.cos(2.0 * PI * zi)
                # Ackley formula: -20*exp(-0.2*sqrt(s1/d)) - exp(s2/d) + 20 + e
                out[m] += weights[g] * (
                    -20.0 * math.exp(-0.2 * math.sqrt(s1 / d))
                    - math.exp(s2 / d) + 20.0 + E_VAL
                )
        return out

    # Audit H-2: ``fastmath=False`` — see group_elliptic_nb rationale.
    @njit(cache=True, parallel=True, boundscheck=False, nogil=True)
    def group_ackley_raw_nb(x, idx_flat, xopt_flat, rot_flat,
                            rot_offsets, group_starts, weights, n_groups):
        """Fused shift+rotate+ackley (RAW variant): NO T_osz/T_asy/Lambda.

        Raw-ackley twin of ``group_ackley_nb`` for F6/F10 under
        ``ackley_variant='raw'`` (MOS's LaTorre/official reference).  Only the
        per-coordinate transform chain is dropped; the shift+rotate and the
        Ackley accumulation are unchanged, so it stays bitwise-parallel to the
        raw C++ path.
        """
        M = x.shape[0]
        out = np.zeros(M, dtype=np.float64)
        max_d = 0
        for g in range(n_groups):
            d = group_starts[g + 1] - group_starts[g]
            if d > max_d:
                max_d = d
        z_buf = np.empty((M, max_d), dtype=np.float64)
        r_buf = np.empty((M, max_d), dtype=np.float64)
        for m in prange(M):
            for g in range(n_groups):
                gs = group_starts[g]
                ge = group_starts[g + 1]
                d = ge - gs
                ro = rot_offsets[g]
                for j in range(d):
                    z_buf[m, j] = x[m, idx_flat[gs + j]] - xopt_flat[gs + j]
                for i in range(d):
                    acc = 0.0
                    for j in range(d):
                        acc += z_buf[m, j] * rot_flat[ro + i * d + j]
                    r_buf[m, i] = acc
                s1 = 0.0  # sum of z_i^2
                s2 = 0.0  # sum of cos(2π z_i)
                for i in range(d):
                    zi = r_buf[m, i]
                    s1 += zi * zi
                    s2 += math.cos(2.0 * PI * zi)
                out[m] += weights[g] * (
                    -20.0 * math.exp(-0.2 * math.sqrt(s1 / d))
                    - math.exp(s2 / d) + 20.0 + E_VAL
                )
        return out

    # Audit H-2: ``fastmath=False`` — see group_elliptic_nb rationale.
    @njit(cache=True, parallel=True, boundscheck=False, nogil=True)
    def group_schwefel_nb(x, idx_flat, xopt_flat, rot_flat,
                          rot_offsets, group_starts, weights, n_groups):
        """Fused shift+rotate+T_osz+T_asy(0.2)+schwefel_1_2 (cumsum).

        Used by F7 (7 groups + sep sphere), F11 (20 groups),
        F13 (20 overlap groups, conforming), F14 (20 overlap, conflicting).

        IMPORTANT: schwefel_1_2 has NO Lambda transform — only T_osz + T_asy.
        The cumulative sum is inherently sequential per group, but prange(M)
        still parallelises across solutions.
        """
        M = x.shape[0]
        out = np.zeros(M, dtype=np.float64)
        beta = 0.2
        max_d = 0
        for g in range(n_groups):
            d = group_starts[g + 1] - group_starts[g]
            if d > max_d:
                max_d = d
        z_buf = np.empty((M, max_d), dtype=np.float64)
        r_buf = np.empty((M, max_d), dtype=np.float64)
        for m in prange(M):
            for g in range(n_groups):
                gs = group_starts[g]
                ge = group_starts[g + 1]
                d = ge - gs
                ro = rot_offsets[g]
                for j in range(d):
                    z_buf[m, j] = x[m, idx_flat[gs + j]] - xopt_flat[gs + j]
                for i in range(d):
                    acc = 0.0
                    for j in range(d):
                        acc += z_buf[m, j] * rot_flat[ro + i * d + j]
                    r_buf[m, i] = acc
                # T_osz + T_asy + schwefel cumsum (NO Lambda)
                dm1 = max(d - 1.0, 1.0)
                running = 0.0
                total = 0.0
                for i in range(d):
                    zi = r_buf[m, i]
                    # T_osz
                    if zi != 0.0:
                        hat = math.log(abs(zi))
                        if zi > 0.0:
                            c1v, c2v, sx = 10.0, 7.9, 1.0
                        else:
                            c1v, c2v, sx = 5.5, 3.1, -1.0
                        zi = sx * math.exp(
                            hat + 0.049 * (math.sin(c1v * hat)
                                           + math.sin(c2v * hat)))
                    # T_asy(β=0.2) — no Lambda for schwefel
                    if zi > 0.0:
                        zi = zi ** (1.0 + beta * i / dm1 * math.sqrt(zi))
                    # Schwefel fused cumsum: running += z; total += running^2
                    running += zi
                    total += running * running
                out[m] += weights[g] * total
        return out

    # =================================================================
    # 5. Fused separable-remainder kernels (F4-F7)
    #
    # The 700-dim separable remainder for F4-F7 was previously
    # evaluated via Python-level fancy indexing:
    #   z_sep = x[:, sep_indices] - xopt_sep   ← M×700 gather + alloc
    #   result += base_func(z_sep)              ← second kernel call
    #
    # These fused kernels eliminate both the M×700 temporary and the
    # extra Python→Numba dispatch by reading directly from the
    # population matrix via column indices.
    # =================================================================

    @njit(cache=True, parallel=True, fastmath=True, boundscheck=False, nogil=True)
    def sep_osz_elliptic_nb(x, indices, xopt_sep):
        """Separable remainder: shift + T_osz + elliptic on indexed columns.

        Used by F4 (700-dim separable elliptic remainder).
        Reads ``x[:, indices[i]]`` directly — no M×700 temporary.
        """
        M = x.shape[0]
        N = indices.shape[0]
        out = np.empty(M, dtype=np.float64)
        Nm1 = max(N - 1.0, 1.0)
        # Precompute elliptic coefficients — O(N) vs O(M·N) pow() calls
        _ec = np.empty(N, dtype=np.float64)
        for i in range(N):
            _ec[i] = 10.0 ** (6.0 * i / Nm1)
        for m in prange(M):
            s = 0.0
            for i in range(N):
                zi = x[m, indices[i]] - xopt_sep[i]
                # T_osz
                if zi != 0.0:
                    hat = math.log(abs(zi))
                    if zi > 0.0:
                        c1, c2, sx = 10.0, 7.9, 1.0
                    else:
                        c1, c2, sx = 5.5, 3.1, -1.0
                    zi = sx * math.exp(
                        hat + 0.049 * (math.sin(c1 * hat) + math.sin(c2 * hat)))
                s += _ec[i] * zi * zi
            out[m] = s
        return out

    @njit(cache=True, parallel=True, fastmath=True, boundscheck=False, nogil=True)
    def sep_osz_asy_lam_rastrigin_nb(x, indices, xopt_sep):
        """Separable remainder: shift + T_osz + T_asy(0.2) + Λ(10) + rastrigin.

        Used by F5 (700-dim separable rastrigin remainder).
        """
        M = x.shape[0]
        N = indices.shape[0]
        out = np.empty(M, dtype=np.float64)
        Nm1 = max(N - 1.0, 1.0)
        beta = 0.2
        alpha = 10.0
        # Precompute Lambda scaling — O(N) vs O(M·N) pow() calls
        _lc = np.empty(N, dtype=np.float64)
        for i in range(N):
            _lc[i] = alpha ** (0.5 * i / Nm1)
        for m in prange(M):
            s = 0.0
            for i in range(N):
                zi = x[m, indices[i]] - xopt_sep[i]
                if zi != 0.0:
                    hat = math.log(abs(zi))
                    if zi > 0.0:
                        c1, c2, sx = 10.0, 7.9, 1.0
                    else:
                        c1, c2, sx = 5.5, 3.1, -1.0
                    zi = sx * math.exp(
                        hat + 0.049 * (math.sin(c1 * hat) + math.sin(c2 * hat)))
                if zi > 0.0:
                    zi = zi ** (1.0 + beta * i / Nm1 * math.sqrt(zi))
                zi *= _lc[i]
                s += zi * zi - 10.0 * math.cos(2.0 * PI * zi) + 10.0
            out[m] = s
        return out

    @njit(cache=True, parallel=True, fastmath=True, boundscheck=False, nogil=True)
    def sep_osz_asy_lam_ackley_nb(x, indices, xopt_sep):
        """Separable remainder: shift + T_osz + T_asy(0.2) + Λ(10) + ackley.

        Used by F6 (700-dim separable ackley remainder).
        """
        M = x.shape[0]
        N = indices.shape[0]
        out = np.empty(M, dtype=np.float64)
        Nm1 = max(N - 1.0, 1.0)
        beta = 0.2
        alpha = 10.0
        # Precompute Lambda scaling — O(N) vs O(M·N) pow() calls
        _lc = np.empty(N, dtype=np.float64)
        for i in range(N):
            _lc[i] = alpha ** (0.5 * i / Nm1)
        for m in prange(M):
            s1 = 0.0
            s2 = 0.0
            for i in range(N):
                zi = x[m, indices[i]] - xopt_sep[i]
                if zi != 0.0:
                    hat = math.log(abs(zi))
                    if zi > 0.0:
                        c1, c2, sx = 10.0, 7.9, 1.0
                    else:
                        c1, c2, sx = 5.5, 3.1, -1.0
                    zi = sx * math.exp(
                        hat + 0.049 * (math.sin(c1 * hat) + math.sin(c2 * hat)))
                if zi > 0.0:
                    zi = zi ** (1.0 + beta * i / Nm1 * math.sqrt(zi))
                zi *= _lc[i]
                s1 += zi * zi
                s2 += math.cos(2.0 * PI * zi)
            out[m] = (
                -20.0 * math.exp(-0.2 * math.sqrt(s1 / N))
                - math.exp(s2 / N) + 20.0 + E_VAL
            )
        return out

    @njit(cache=True, parallel=True, fastmath=True, boundscheck=False, nogil=True)
    def sep_ackley_raw_nb(x, indices, xopt_sep):
        """Separable remainder (RAW variant): shift + ackley, NO transforms.

        Raw-ackley twin of ``sep_osz_asy_lam_ackley_nb`` for the F6 700-dim
        separable remainder under ``ackley_variant='raw'``.
        """
        M = x.shape[0]
        N = indices.shape[0]
        out = np.empty(M, dtype=np.float64)
        for m in prange(M):
            s1 = 0.0
            s2 = 0.0
            for i in range(N):
                zi = x[m, indices[i]] - xopt_sep[i]
                s1 += zi * zi
                s2 += math.cos(2.0 * PI * zi)
            out[m] = (
                -20.0 * math.exp(-0.2 * math.sqrt(s1 / N))
                - math.exp(s2 / N) + 20.0 + E_VAL
            )
        return out

    @njit(cache=True, parallel=True, fastmath=True, boundscheck=False, nogil=True)
    def sep_sphere_nb(x, indices, xopt_sep):
        """Separable remainder: shift + sphere on indexed columns.

        Used by F7 (700-dim separable sphere remainder).
        No transforms — just sum((x[idx] - xopt)^2).
        """
        M = x.shape[0]
        N = indices.shape[0]
        out = np.empty(M, dtype=np.float64)
        for m in prange(M):
            s = 0.0
            for i in range(N):
                zi = x[m, indices[i]] - xopt_sep[i]
                s += zi * zi
            out[m] = s
        return out

else:
    # Numba unavailable -- every export is None; callers fall back to
    # pure NumPy under ``if _NB_FN is None:``.
    transform_osz_nb = None
    transform_asy_nb = None
    lambda_transform_nb = None
    fused_osz_elliptic_nb = None
    fused_osz_asy_lam_rastrigin_nb = None
    fused_osz_asy_lam_ackley_nb = None
    fused_osz_asy_schwefel_nb = None
    sphere_nb = None
    rosenbrock_nb = None
    shifted_osz_elliptic_nb = None
    shifted_osz_asy_lam_rastrigin_nb = None
    shifted_osz_asy_lam_ackley_nb = None
    shifted_rosenbrock_nb = None
    shifted_osz_asy_schwefel_nb = None
    group_elliptic_nb = None
    group_rastrigin_nb = None
    group_ackley_nb = None
    group_schwefel_nb = None
    sep_osz_elliptic_nb = None
    sep_osz_asy_lam_rastrigin_nb = None
    sep_osz_asy_lam_ackley_nb = None
    sep_sphere_nb = None
    shifted_ackley_raw_nb = None
    group_ackley_raw_nb = None
    sep_ackley_raw_nb = None


# ===========================================================================
# Warmup -- trigger JIT compilation of all cached kernels
# ===========================================================================
def warmup() -> None:
    """Pre-compile all cached CEC2013LSGO kernels with tiny inputs.

    Retained pre-compilation utility (no runner call sites in this project:
    the campaign runner warms each worker by evaluating a probe cell instead
    — ``warm_benchmark_cells`` in ``gsk_family.runners.performance``)
    so JIT cost is paid
    before the first benchmark generation runs.  Uses deterministic
    non-zero input (arange-based) so warmup is reproducible and avoids
    the global ``np.random`` RNG.  Skipped gracefully when numba is not
    installed.
    """
    if not HAS_NUMBA:
        return
    n, d = 2, 5
    # Deterministic non-zero data — exercises all transform branches
    xc = np.ascontiguousarray(
        np.arange(n * d, dtype=np.float64).reshape(n, d) * 0.1 - 0.25,
    )
    xopt = np.zeros(d, dtype=np.float64)
    # 1. Standalone transforms
    transform_osz_nb(xc)
    transform_asy_nb(xc, 0.2)
    lambda_transform_nb(xc, 10.0)
    # 2. Fused transform+evaluate cores
    fused_osz_elliptic_nb(xc)
    fused_osz_asy_lam_rastrigin_nb(xc)
    fused_osz_asy_lam_ackley_nb(xc)
    fused_osz_asy_schwefel_nb(xc)
    sphere_nb(xc)
    rosenbrock_nb(xc)
    # 3. Shifted full-D kernels
    shifted_osz_elliptic_nb(xc, xopt)
    shifted_osz_asy_lam_rastrigin_nb(xc, xopt)
    shifted_osz_asy_lam_ackley_nb(xc, xopt)
    shifted_rosenbrock_nb(xc, xopt)
    shifted_osz_asy_schwefel_nb(xc, xopt)
    # 4. Fused group kernels (1 group of 5 dims)
    idx = np.arange(d, dtype=np.int64)
    rot = np.eye(d, dtype=np.float64).ravel().copy()
    ro = np.array([0, d * d], dtype=np.int64)
    gs = np.array([0, d], dtype=np.int64)
    wt = np.ones(1, dtype=np.float64)
    group_elliptic_nb(xc, idx, xopt, rot, ro, gs, wt, 1)
    group_rastrigin_nb(xc, idx, xopt, rot, ro, gs, wt, 1)
    group_ackley_nb(xc, idx, xopt, rot, ro, gs, wt, 1)
    group_schwefel_nb(xc, idx, xopt, rot, ro, gs, wt, 1)
    # 5. Fused separable-remainder kernels
    sep_osz_elliptic_nb(xc, idx, xopt)
    sep_osz_asy_lam_rastrigin_nb(xc, idx, xopt)
    sep_osz_asy_lam_ackley_nb(xc, idx, xopt)
    sep_sphere_nb(xc, idx, xopt)
