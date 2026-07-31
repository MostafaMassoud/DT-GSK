"""CEC2011 Numba-accelerated kernels.

Cross-reference: each kernel corresponds to an inner loop in either
:mod:`.problems_basic` (ODE45 F3/F4, Tersoff F5/F6, Spread Spectrum F7) or
:mod:`.orbital_mechanics` (MGA-DSM trajectory primitives for F21/F22).

Layout
~~~~~~
This module mirrors the per-suite ``_numba.py`` pattern used by CEC2013:
every JIT'd kernel for the CEC2011 problems lives here and the
suite source files import them via ``from ._numba import ...``.  JIT cost is
paid before the first timed generation by the runner's per-worker probe-cell
warmup (``warm_benchmark_cells`` in ``gsk_family.runners.performance``,
invoked from ``run_experiment._init_process_worker``); the module-level
:func:`warmup` remains available for ad-hoc pre-compilation.

Kernel table
~~~~~~~~~~~~
========================= ===================================================
Kernel                    Source / purpose
========================= ===================================================
_bifunctional_rhs_nb      Bifunctional catalyst ODE right-hand side (F3 inner)
_bifunctional_catalyst_nb ODE45 bifunctional catalyst objective (F3)
_stirred_tank_nb          ODE45 stirred tank reactor objective (F4)
_tersoff_inner_nb         Triple-loop Tersoff potential energy (F5/F6 inner)
_spread_spectrum_nb       Spread spectrum radar polyphase autocorrelation (F7)
_vett                     3-vector cross product (orbital_mechanics primitive)
_vers                     3-vector unit-norm (orbital_mechanics primitive)
_ni2E                     True anomaly -> eccentric anomaly
_M2E                      Mean anomaly -> eccentric anomaly (Newton iteration)
_E2M                      Eccentric anomaly -> mean anomaly
_tofabn                   Lambert solver: time-of-flight from a, beta, N
_x2tof                    Lambert solver: x parameter -> time of flight
========================= ===================================================

When numba is unavailable every export is set to ``None``; callers must
provide a pure-Python fallback under ``if _NB_FN is None:``.  This matches
the symmetric ``if _HAS_NUMBA / else`` style that ``problems_basic.py`` and
``orbital_mechanics.py`` had pre-refactor.

Decorator policy
~~~~~~~~~~~~~~~~
Every kernel here is scalar (per-row Tersoff, single-array spread spectrum,
3-vector orbital primitives) so none of them parallelise across a population
dimension.  The canonical reproducibility-first scalar decorator is::

    @njit(cache=True, fastmath=True, boundscheck=False, nogil=True)

``boundscheck=False`` and ``nogil=True`` are required to release the GIL
inside ``ProcessPoolExecutor`` workers without contention.  ``fastmath=True``
is applied only to the kernels where it is safe for the numerical content
(Newton-Kepler iteration, sin/cos/sqrt/exp arithmetic).

**Exception (do NOT add fastmath to these):** the four ODE45 (F3/F4) and Tersoff
(F5/F6) kernels intentionally OMIT ``fastmath=True`` and use the plain
``@njit(cache=True, boundscheck=False, nogil=True)`` decorator — their stiff-ODE
integration and many-body potential summations are sensitive to fastmath's
reassociation/reciprocal approximations, so adding fastmath would change the
F3-F6 reference numerics. 8 of the 12 kernels use fastmath; these 4 do not.
"""

from __future__ import annotations

import math

import numpy as np

try:
    from numba import njit  # type: ignore[import-untyped]
    HAS_NUMBA = True
except Exception:  # not just ImportError: llvmlite can raise OSError under memory pressure
    HAS_NUMBA = False


# ===========================================================================
# Tersoff potential inner triple loop (F5/F6)
# ===========================================================================

if HAS_NUMBA:

    @njit(cache=True, boundscheck=False, nogil=True)
    def _bifunctional_rhs_nb(s, k, out):
        out[0] = -k[0] * s[0]
        out[1] = k[0] * s[0] - (k[1] + k[2]) * s[1] + k[3] * s[4]
        out[2] = k[1] * s[1]
        out[3] = -k[5] * s[3] + k[4] * s[4]
        out[4] = (k[2] * s[1] + k[5] * s[3]
                  - (k[3] + k[4] + k[7] + k[8]) * s[4]
                  + k[6] * s[5] + k[9] * s[6])
        out[5] = k[7] * s[4] - k[6] * s[5]
        out[6] = k[8] * s[4] - k[9] * s[6]

    @njit(cache=True, boundscheck=False, nogil=True)
    def _bifunctional_catalyst_nb(u, coeffs):
        """MATLAB-ode45-compatible scalar F3 objective used by CEC2011."""
        k_pow = 1.0 / 5.0
        b11 = 1.0 / 5.0
        b21 = 3.0 / 40.0
        b22 = 9.0 / 40.0
        b31 = 44.0 / 45.0
        b32 = -56.0 / 15.0
        b33 = 32.0 / 9.0
        b41 = 19372.0 / 6561.0
        b42 = -25360.0 / 2187.0
        b43 = 64448.0 / 6561.0
        b44 = -212.0 / 729.0
        b51 = 9017.0 / 3168.0
        b52 = -355.0 / 33.0
        b53 = 46732.0 / 5247.0
        b54 = 49.0 / 176.0
        b55 = -5103.0 / 18656.0
        b61 = 35.0 / 384.0
        b63 = 500.0 / 1113.0
        b64 = 125.0 / 192.0
        b65 = -2187.0 / 6784.0
        b66 = 11.0 / 84.0
        e1 = 71.0 / 57600.0
        e3 = -71.0 / 16695.0
        e4 = 71.0 / 1920.0
        e5 = -17253.0 / 339200.0
        e6 = 22.0 / 525.0
        e7 = -1.0 / 40.0

        t0 = 0.0
        tfinal = 0.78
        rtol = 1.0e-1
        atol = 1.0e-6
        eps_double = 2.220446049250313e-16
        htspan = abs(tfinal - t0)
        threshold = atol / rtol
        safehmax = 16.0 * eps_double * max(abs(t0), abs(tfinal))
        userhmax = max(0.1 * abs(tfinal - t0), safehmax)

        u2 = u * u
        u3 = u2 * u
        k = np.empty(10)
        for i in range(10):
            k[i] = ((coeffs[i, 0] * 1.0 + coeffs[i, 1] * u) + coeffs[i, 2] * u2) + coeffs[i, 3] * u3

        t = t0
        y = np.empty(7)
        y[0] = 1.0
        y[1] = 0.0
        y[2] = 0.0
        y[3] = 0.0
        y[4] = 0.0
        y[5] = 0.0
        y[6] = 0.0

        f1 = np.empty(7)
        f2 = np.empty(7)
        f3 = np.empty(7)
        f4 = np.empty(7)
        f5 = np.empty(7)
        f6 = np.empty(7)
        f7 = np.empty(7)
        y2 = np.empty(7)
        y3 = np.empty(7)
        y4 = np.empty(7)
        y5 = np.empty(7)
        y6 = np.empty(7)
        ynew = np.empty(7)

        _bifunctional_rhs_nb(y, k, f1)

        tinystep = 16.0 * np.nextafter(t, np.inf) if t == 0.0 else 16.0 * (np.nextafter(abs(t), np.inf) - abs(t))
        hmin = max(tinystep, 0.0)
        hmax = max(tinystep, userhmax)
        absh = min(hmax, htspan)
        rh = 0.0
        for i in range(7):
            w = abs(f1[i] / max(abs(y[i]), threshold))
            if w > rh:
                rh = w
        rh /= 0.8 * rtol ** k_pow
        if absh * rh > 1.0:
            absh = 1.0 / rh
        absh = max(absh, hmin)

        done = False
        guard = 0
        while not done:
            guard += 1
            if guard > 10000:
                return np.nan
            tinystep = 16.0 * np.nextafter(t, np.inf) if t == 0.0 else 16.0 * (np.nextafter(abs(t), np.inf) - abs(t))
            hmin = max(tinystep, 0.0)
            hmax = max(tinystep, userhmax)
            absh = min(hmax, max(hmin, absh))
            h = absh
            if 1.1 * absh >= abs(tfinal - t):
                h = tfinal - t
                absh = abs(h)
                done = True

            nofailed = True
            err = 0.0
            tnew = t
            while True:
                for i in range(7):
                    y2[i] = y[i] + h * (b11 * f1[i])
                _bifunctional_rhs_nb(y2, k, f2)
                for i in range(7):
                    y3[i] = y[i] + h * (b21 * f1[i] + b22 * f2[i])
                _bifunctional_rhs_nb(y3, k, f3)
                for i in range(7):
                    y4[i] = y[i] + h * ((b31 * f1[i] + b32 * f2[i]) + b33 * f3[i])
                _bifunctional_rhs_nb(y4, k, f4)
                for i in range(7):
                    y5[i] = y[i] + h * (((b41 * f1[i] + b42 * f2[i]) + b43 * f3[i]) + b44 * f4[i])
                _bifunctional_rhs_nb(y5, k, f5)
                for i in range(7):
                    y6[i] = y[i] + h * ((((b51 * f1[i] + b52 * f2[i]) + b53 * f3[i]) + b54 * f4[i]) + b55 * f5[i])
                _bifunctional_rhs_nb(y6, k, f6)

                tnew = t + h
                if done:
                    tnew = tfinal
                h = tnew - t

                for i in range(7):
                    ynew[i] = y[i] + h * ((((b61 * f1[i] + b63 * f3[i]) + b64 * f4[i]) + b65 * f5[i]) + b66 * f6[i])
                _bifunctional_rhs_nb(ynew, k, f7)

                scaled = 0.0
                for i in range(7):
                    fe = ((((f1[i] * e1 + f3[i] * e3) + f4[i] * e4) + f5[i] * e5) + f6[i] * e6) + f7[i] * e7
                    denom = max(max(abs(y[i]), abs(ynew[i])), threshold)
                    w = abs(fe / denom)
                    if w > scaled:
                        scaled = w
                err = absh * scaled

                if err > rtol:
                    if absh <= hmin:
                        return np.nan
                    if nofailed:
                        nofailed = False
                        absh = max(hmin, absh * max(0.1, 0.8 * (rtol / err) ** k_pow))
                    else:
                        absh = max(hmin, 0.5 * absh)
                    h = absh
                    done = False
                else:
                    break

            if done:
                return ynew[6] * 1.0e3

            if nofailed:
                temp = 1.25 * (err / rtol) ** k_pow
                if temp > 0.2:
                    absh = absh / temp
                else:
                    absh = 5.0 * absh

            t = tnew
            for i in range(7):
                y[i] = ynew[i]
                f1[i] = f7[i]

        return y[6] * 1.0e3

    @njit(cache=True, boundscheck=False, nogil=True)
    def _stirred_tank_nb(u):
        """MATLAB-ode45-compatible scalar F4 objective used by CEC2011."""
        k_pow = 1.0 / 5.0
        b11 = 1.0 / 5.0
        b21 = 3.0 / 40.0
        b22 = 9.0 / 40.0
        b31 = 44.0 / 45.0
        b32 = -56.0 / 15.0
        b33 = 32.0 / 9.0
        b41 = 19372.0 / 6561.0
        b42 = -25360.0 / 2187.0
        b43 = 64448.0 / 6561.0
        b44 = -212.0 / 729.0
        b51 = 9017.0 / 3168.0
        b52 = -355.0 / 33.0
        b53 = 46732.0 / 5247.0
        b54 = 49.0 / 176.0
        b55 = -5103.0 / 18656.0
        b61 = 35.0 / 384.0
        b63 = 500.0 / 1113.0
        b64 = 125.0 / 192.0
        b65 = -2187.0 / 6784.0
        b66 = 11.0 / 84.0
        e1 = 71.0 / 57600.0
        e3 = -71.0 / 16695.0
        e4 = 71.0 / 1920.0
        e5 = -17253.0 / 339200.0
        e6 = 22.0 / 525.0
        e7 = -1.0 / 40.0
        bi12 = -183.0 / 64.0
        bi13 = 37.0 / 12.0
        bi14 = -145.0 / 128.0
        bi32 = 1500.0 / 371.0
        bi33 = -1000.0 / 159.0
        bi34 = 1000.0 / 371.0
        bi42 = -125.0 / 32.0
        bi43 = 125.0 / 12.0
        bi44 = -375.0 / 64.0
        bi52 = 9477.0 / 3392.0
        bi53 = -729.0 / 106.0
        bi54 = 25515.0 / 6784.0
        bi62 = -11.0 / 7.0
        bi63 = 11.0 / 3.0
        bi64 = -55.0 / 28.0
        bi72 = 3.0 / 2.0
        bi73 = -4.0
        bi74 = 5.0 / 2.0

        t0 = 0.0
        tfinal = 0.78
        rtol = 1.0e-1
        atol = 1.0e-6
        eps_double = 2.220446049250313e-16
        htspan = abs(tfinal - t0)
        threshold = atol / rtol
        safehmax = 16.0 * eps_double * max(abs(t0), abs(tfinal))
        userhmax = max(0.1 * abs(tfinal - t0), safehmax)

        t = t0
        y0 = 0.09
        y1 = 0.09
        q = (0.1 * u) * u
        total = y0 * y0 + y1 * y1 + q

        exp_term = np.exp(25.0 * y0 / (y0 + 2.0))
        f1_0 = -(2.0 + u) * (y0 + 0.25) + (y1 + 0.5) * exp_term
        f1_1 = (0.5 - y1) - (y1 + 0.5) * exp_term

        tinystep = 16.0 * np.nextafter(t, np.inf) if t == 0.0 else 16.0 * (np.nextafter(abs(t), np.inf) - abs(t))
        hmin = max(tinystep, 0.0)
        hmax = max(tinystep, userhmax)
        absh = min(hmax, htspan)
        rh = 0.0
        w = abs(f1_0 / max(abs(y0), threshold))
        if w > rh:
            rh = w
        w = abs(f1_1 / max(abs(y1), threshold))
        if w > rh:
            rh = w
        rh /= 0.8 * rtol ** k_pow
        if absh * rh > 1.0:
            absh = 1.0 / rh
        absh = max(absh, hmin)

        done = False
        guard = 0
        while not done:
            guard += 1
            if guard > 10000:
                return np.nan
            tinystep = 16.0 * np.nextafter(t, np.inf) if t == 0.0 else 16.0 * (np.nextafter(abs(t), np.inf) - abs(t))
            hmin = max(tinystep, 0.0)
            hmax = max(tinystep, userhmax)
            absh = min(hmax, max(hmin, absh))
            h = absh
            if 1.1 * absh >= abs(tfinal - t):
                h = tfinal - t
                absh = abs(h)
                done = True

            nofailed = True
            err = 0.0
            tnew = t
            while True:
                y2_0 = y0 + h * (b11 * f1_0)
                y2_1 = y1 + h * (b11 * f1_1)
                exp_term = np.exp(25.0 * y2_0 / (y2_0 + 2.0))
                f2_0 = -(2.0 + u) * (y2_0 + 0.25) + (y2_1 + 0.5) * exp_term
                f2_1 = (0.5 - y2_1) - (y2_1 + 0.5) * exp_term

                y3_0 = y0 + h * (b21 * f1_0 + b22 * f2_0)
                y3_1 = y1 + h * (b21 * f1_1 + b22 * f2_1)
                exp_term = np.exp(25.0 * y3_0 / (y3_0 + 2.0))
                f3_0 = -(2.0 + u) * (y3_0 + 0.25) + (y3_1 + 0.5) * exp_term
                f3_1 = (0.5 - y3_1) - (y3_1 + 0.5) * exp_term

                y4_0 = y0 + h * ((b31 * f1_0 + b32 * f2_0) + b33 * f3_0)
                y4_1 = y1 + h * ((b31 * f1_1 + b32 * f2_1) + b33 * f3_1)
                exp_term = np.exp(25.0 * y4_0 / (y4_0 + 2.0))
                f4_0 = -(2.0 + u) * (y4_0 + 0.25) + (y4_1 + 0.5) * exp_term
                f4_1 = (0.5 - y4_1) - (y4_1 + 0.5) * exp_term

                y5_0 = y0 + h * (((b41 * f1_0 + b42 * f2_0) + b43 * f3_0) + b44 * f4_0)
                y5_1 = y1 + h * (((b41 * f1_1 + b42 * f2_1) + b43 * f3_1) + b44 * f4_1)
                exp_term = np.exp(25.0 * y5_0 / (y5_0 + 2.0))
                f5_0 = -(2.0 + u) * (y5_0 + 0.25) + (y5_1 + 0.5) * exp_term
                f5_1 = (0.5 - y5_1) - (y5_1 + 0.5) * exp_term

                y6_0 = y0 + h * ((((b51 * f1_0 + b52 * f2_0) + b53 * f3_0) + b54 * f4_0) + b55 * f5_0)
                y6_1 = y1 + h * ((((b51 * f1_1 + b52 * f2_1) + b53 * f3_1) + b54 * f4_1) + b55 * f5_1)
                exp_term = np.exp(25.0 * y6_0 / (y6_0 + 2.0))
                f6_0 = -(2.0 + u) * (y6_0 + 0.25) + (y6_1 + 0.5) * exp_term
                f6_1 = (0.5 - y6_1) - (y6_1 + 0.5) * exp_term

                tnew = t + h
                if done:
                    tnew = tfinal
                h = tnew - t

                ynew_0 = y0 + h * ((((b61 * f1_0 + b63 * f3_0) + b64 * f4_0) + b65 * f5_0) + b66 * f6_0)
                ynew_1 = y1 + h * ((((b61 * f1_1 + b63 * f3_1) + b64 * f4_1) + b65 * f5_1) + b66 * f6_1)
                exp_term = np.exp(25.0 * ynew_0 / (ynew_0 + 2.0))
                f7_0 = -(2.0 + u) * (ynew_0 + 0.25) + (ynew_1 + 0.5) * exp_term
                f7_1 = (0.5 - ynew_1) - (ynew_1 + 0.5) * exp_term

                fe0 = ((((f1_0 * e1 + f3_0 * e3) + f4_0 * e4) + f5_0 * e5) + f6_0 * e6) + f7_0 * e7
                fe1 = ((((f1_1 * e1 + f3_1 * e3) + f4_1 * e4) + f5_1 * e5) + f6_1 * e6) + f7_1 * e7
                denom0 = max(max(abs(y0), abs(ynew_0)), threshold)
                denom1 = max(max(abs(y1), abs(ynew_1)), threshold)
                scaled = 0.0
                w = abs(fe0 / denom0)
                if w > scaled:
                    scaled = w
                w = abs(fe1 / denom1)
                if w > scaled:
                    scaled = w
                err = absh * scaled

                if err > rtol:
                    if absh <= hmin:
                        return np.nan
                    if nofailed:
                        nofailed = False
                        absh = max(hmin, absh * max(0.1, 0.8 * (rtol / err) ** k_pow))
                    else:
                        absh = max(hmin, 0.5 * absh)
                    h = absh
                    done = False
                else:
                    break

            for kk in range(1, 4):
                s = kk / 4.0
                s2 = s * s
                bs1 = s + s2 * (bi12 + s * (bi13 + bi14 * s))
                bs3 = s2 * (bi32 + s * (bi33 + bi34 * s))
                bs4 = s2 * (bi42 + s * (bi43 + bi44 * s))
                bs5 = s2 * (bi52 + s * (bi53 + bi54 * s))
                bs6 = s2 * (bi62 + s * (bi63 + bi64 * s))
                bs7 = s2 * (bi72 + s * (bi73 + bi74 * s))
                yi0 = y0 + h * (((((f1_0 * bs1 + f3_0 * bs3) + f4_0 * bs4) + f5_0 * bs5) + f6_0 * bs6) + f7_0 * bs7)
                yi1 = y1 + h * (((((f1_1 * bs1 + f3_1 * bs3) + f4_1 * bs4) + f5_1 * bs5) + f6_1 * bs6) + f7_1 * bs7)
                total += yi0 * yi0 + yi1 * yi1 + q
            total += ynew_0 * ynew_0 + ynew_1 * ynew_1 + q

            if done:
                break
            if nofailed:
                temp = 1.25 * (err / rtol) ** k_pow
                if temp > 0.2:
                    absh = absh / temp
                else:
                    absh = 5.0 * absh
            t = tnew
            y0 = ynew_0
            y1 = ynew_1
            f1_0 = f7_0
            f1_1 = f7_1

        return total

    @njit(cache=True, boundscheck=False, nogil=True)
    def _tersoff_inner_nb(
        atoms, r, fcr, VRr, VAr,
        lam3, c, d, n1, gamma, h, NP,
    ):
        """Numba-JIT inner triple loop of Tersoff potential.

        Cross-reference: ``problems_basic._tersoff_potential`` Python
        fallback (lines 388-425).  Computes the three-body bond-order
        ``Bij`` and accumulates pair energies into ``E``.

        Audit M-4 ***DO NOT "CORRECT"*** warning
        ----------------------------------------
        The law-of-cosines denominator uses ``rd3 ** 3`` (cubed, not
        squared) and the three-body exponential uses ``lam3 ** 3``.
        Both are reference-exact quirks from the CEC2011 reference
        ``bench_func.m`` case 5/6.  A physically-correct Tersoff
        implementation would write ``rd3 ** 2`` and ``lam3`` (linear),
        but changing either here breaks CEC2011 F5/F6 bit-reproducibility
        against every published baseline and against the Python fallback
        in ``problems_basic._tersoff_potential``.  See docstring of that
        function and inline comment near line 373 for the historical
        rationale.  If you *really* need a correct Tersoff potential,
        build it in a separate module -- these CEC kernels are benchmark
        *problems*, not a physics library.
        """
        E = np.zeros(NP)
        c2 = c * c
        d2 = d * d
        for i in range(NP):
            for j in range(NP):
                if i == j:
                    continue
                zeta = 0.0
                for kk in range(NP):
                    if kk == i or kk == j:
                        continue
                    rd1 = r[i, kk]
                    rd2 = r[i, j]
                    rd3 = r[kk, j]
                    denom = 2.0 * rd1 * rd2
                    # Audit M-4: rd3**3 and lam3**3 are reference-exact.  Do
                    # not change to rd3**2 / lam3 -- see kernel docstring.
                    if denom == 0.0:
                        ctheta = np.nan
                    else:
                        ctheta = (rd1 ** 2 + rd2 ** 2 - rd3 ** 3) / denom
                    G = 1.0 + c2 / d2 - c2 / (d2 + (h - ctheta) ** 2)
                    zeta += fcr[i, kk] * G * np.exp(lam3 ** 3 * (r[i, j] - r[i, kk]) ** 3)

                gn = gamma * zeta
                Bij = (1.0 + gn ** n1) ** (-0.5 / n1)

                E[i] += fcr[i, j] * (VRr[i, j] - Bij * VAr[i, j]) / 2.0
        return np.sum(E)

    # =======================================================================
    # Spread spectrum radar polyphase code (F7)
    # =======================================================================

    @njit(cache=True, fastmath=True, boundscheck=False, nogil=True)
    def _spread_spectrum_nb(x, d):
        """Numba-JIT triple-nested loop of F7 spread spectrum.

        Cross-reference: ``bench_func.m`` case 7.  Computes the
        autocorrelation magnitudes for both odd and even indices and
        returns the maximum sidelobe level.
        """
        var = 2 * d - 1
        hsum = np.zeros(2 * var)

        for kk in range(1, 2 * var + 1):
            if kk % 2 != 0:  # odd
                i = (kk + 1) // 2
                s = 0.0
                for j in range(i, d + 1):
                    summ = 0.0
                    lo = abs(2 * i - j - 1) + 1
                    for i1 in range(lo, j + 1):
                        summ += x[i1 - 1]
                    s += np.cos(summ)
                hsum[kk - 1] = s
            else:  # even
                i = kk // 2
                s = 0.0
                for j in range(i + 1, d + 1):
                    summ = 0.0
                    lo = abs(2 * i - j) + 1
                    for i1 in range(lo, j + 1):
                        summ += x[i1 - 1]
                    s += np.cos(summ)
                hsum[kk - 1] = s + 0.5
        return np.max(hsum)

    # =======================================================================
    # Orbital-mechanics primitives (vector helpers)
    # =======================================================================

    @njit(cache=True, fastmath=True, boundscheck=False, nogil=True)
    def _vett(r1, r2):
        """Cross product returning shape (3,)."""
        out = np.empty(3)
        out[0] = r1[1] * r2[2] - r1[2] * r2[1]
        out[1] = r1[2] * r2[0] - r1[0] * r2[2]
        out[2] = r1[0] * r2[1] - r1[1] * r2[0]
        return out

    @njit(cache=True, fastmath=True, boundscheck=False, nogil=True)
    def _vers(V):
        """Unit vector."""
        n = math.sqrt(V[0] * V[0] + V[1] * V[1] + V[2] * V[2])
        out = np.empty(3)
        out[0] = V[0] / n
        out[1] = V[1] / n
        out[2] = V[2] / n
        return out

    # =======================================================================
    # Anomaly conversions (Kepler problem)
    # =======================================================================

    @njit(cache=True, fastmath=True, boundscheck=False, nogil=True)
    def _ni2E(ni, e):
        """True anomaly -> eccentric anomaly."""
        if e < 1.0:
            return 2.0 * math.atan(math.sqrt((1.0 - e) / (1.0 + e)) * math.tan(ni / 2.0))
        else:
            return 2.0 * math.atan(math.sqrt((e - 1.0) / (e + 1.0)) * math.tan(ni / 2.0))

    @njit(cache=True, fastmath=True, boundscheck=False, nogil=True)
    def _M2E(M, e):
        """Mean anomaly -> eccentric anomaly via 100-iteration Newton solve."""
        E = M + e * math.cos(M)
        for _ in range(100):
            Enew = E - (E - e * math.sin(E) - M) / (1.0 - e * math.cos(E))
            if abs(E - Enew) < 1e-10:
                return Enew
            E = Enew
        return E

    @njit(cache=True, fastmath=True, boundscheck=False, nogil=True)
    def _E2M(E, e):
        """Eccentric anomaly -> mean anomaly (handles elliptic + hyperbolic)."""
        if e < 1.0:
            return E - e * math.sin(E)
        else:
            return e * math.tan(E) - math.log(math.tan(E / 2.0 + math.pi / 4.0))

    # =======================================================================
    # Lambert solver helpers
    # =======================================================================

    @njit(cache=True, fastmath=True, boundscheck=False, nogil=True)
    def _tofabn(sigma, alfa, beta, N):
        """Lambert TOF from a, beta and revolution count N."""
        if sigma > 0.0:
            return sigma * math.sqrt(sigma) * (
                (alfa - math.sin(alfa)) - (beta - math.sin(beta)) + N * 2.0 * math.pi
            )
        else:
            return -sigma * math.sqrt(-sigma) * (
                (math.sinh(alfa) - alfa) - (math.sinh(beta) - beta)
            )

    @njit(cache=True, fastmath=True, boundscheck=False, nogil=True)
    def _x2tof(x, s, c, lw, N):
        """Lambert: x parameter -> time of flight."""
        am = s / 2.0
        a = am / (1.0 - x * x)
        if x < 1.0:
            beta = 2.0 * math.asin(math.sqrt((s - c) / (2.0 * a)))
            if lw:
                beta = -beta
            xc = min(max(x, -1.0), 1.0)
            alfa = 2.0 * math.acos(xc)
        else:
            alfa = 2.0 * math.acosh(x)
            beta = 2.0 * math.asinh(math.sqrt((s - c) / (-2.0 * a)))
            if lw:
                beta = -beta
        return _tofabn(a, alfa, beta, N)

else:
    # Numba unavailable -- every export is None; callers fall back to
    # pure Python under ``if _NB_FN is None:``.
    _bifunctional_catalyst_nb = None
    _stirred_tank_nb = None
    _tersoff_inner_nb = None
    _spread_spectrum_nb = None
    _vett = None
    _vers = None
    _ni2E = None
    _M2E = None
    _E2M = None
    _tofabn = None
    _x2tof = None


# ===========================================================================
# Warmup -- trigger JIT compilation of all cached kernels
# ===========================================================================
def warmup() -> None:
    """Trigger JIT compilation of all CEC2011 kernels with tiny inputs.

    Retained pre-compilation utility (no runner call sites in this project:
    the campaign runner warms each worker by evaluating a probe cell instead
    — ``warm_benchmark_cells`` in ``gsk_family.runners.performance``)
    so JIT cost is paid
    before the first benchmark generation runs.  Uses minimal array
    sizes (3-atom Tersoff, length-4 spread spectrum) to keep
    compilation overhead low while ensuring all code paths are cached.
    Skipped gracefully when numba is not installed.
    """
    if not HAS_NUMBA:
        return
    coeffs = np.zeros((10, 4))
    coeffs.flags.writeable = False
    _bifunctional_catalyst_nb(0.75, coeffs)
    _stirred_tank_nb(1.0)

    # ----- Tersoff inner triple loop -----
    NP = 3
    atoms = np.zeros((NP, 3))
    atoms[1, 0] = 1.0
    atoms[2, 0] = 0.5
    atoms[2, 1] = 1.0
    diff = atoms[:, None, :] - atoms[None, :, :]
    r = np.sqrt(np.sum(diff * diff, axis=2))
    fcr = np.ones((NP, NP))
    VRr = np.ones((NP, NP))
    VAr = np.ones((NP, NP))
    _tersoff_inner_nb(
        atoms, r, fcr, VRr, VAr,
        1.0, 1.0, 1.0, 1.0, 1.0, 0.0, NP,
    )

    # ----- Spread spectrum -----
    x_ss = np.full(4, 1.0)
    _spread_spectrum_nb(x_ss, 4)

    # ----- Orbital primitives -----
    v1 = np.array([1.0, 0.0, 0.0])
    v2 = np.array([0.0, 1.0, 0.0])
    _vett(v1, v2)
    _vers(v1)
    _ni2E(0.5, 0.1)
    _M2E(0.5, 0.1)
    _E2M(0.5, 0.1)
    _tofabn(0.5, 0.4, 0.3, 0)
    _x2tof(0.1, 1.0, 0.5, 0, 0)


__all__ = [
    "HAS_NUMBA",
    "_bifunctional_catalyst_nb",
    "_stirred_tank_nb",
    "_tersoff_inner_nb",
    "_spread_spectrum_nb",
    "_vett",
    "_vers",
    "_ni2E",
    "_M2E",
    "_E2M",
    "_tofabn",
    "_x2tof",
    "warmup",
]
