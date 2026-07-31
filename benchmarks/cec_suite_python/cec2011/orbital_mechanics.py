"""Orbital mechanics library for CEC2011 F21/F22 (MGA-DSM trajectories).

Pure Python/NumPy port of ESA's ``mga_dsm.m`` (Dario Izzo, ESA/ACT, 2007).
Provides the Multiple Gravity Assist with Deep Space Manoeuvres solver
used by the Messenger (F21) and Cassini-2 (F22) benchmark problems.

Reference
---------
Izzo, D., "Global optimization and space pruning for spacecraft trajectory
design", in *Spacecraft Trajectory Optimization* (Conway Ed.), Cambridge
University Press, 2009.
"""

from __future__ import annotations

import math

import numpy as np

from ._constants import NAN_PENALTY

# JIT kernels live in this suite's own ``_numba.py`` -- mirroring the
# CEC2013/CEC2017 layout.  Each name is either the JIT'd
# function or ``None`` when numba is unavailable; the pure-Python
# fallbacks defined below take over when the import returns ``None``.
from ._numba import (
    _E2M as _E2M_nb,
    _M2E as _M2E_nb,
    _ni2E as _ni2E_nb,
    _tofabn as _tofabn_nb,
    _vers as _vers_nb,
    _vett as _vett_nb,
    _x2tof as _x2tof_nb,
)

# ---------------------------------------------------------------------------
# Physical constants  (must match reference mga_dsm.m exactly)
# ---------------------------------------------------------------------------

# Gravitational parameters [km^3/s^2]  — used in mga_dsm main solver
_MU_PLANET = np.array([
    22321.0,              # 1 Mercury
    324860.0,             # 2 Venus
    398601.19,            # 3 Earth
    42828.3,              # 4 Mars
    126.7e6,              # 5 Jupiter
    37.93951970883e6,     # 6 Saturn
])

_MU_SUN = 1.32712428e+11  # main solver

# Planetary radii [km]
_RPL = np.array([
    2440.0,   # Mercury
    6052.0,   # Venus
    6378.0,   # Earth
    3397.0,   # Mars
    71492.0,  # Jupiter
    60330.0,  # Saturn
])
_MU_PLANET.flags.writeable = False
_RPL.flags.writeable = False

# Constants for pleph_an (ephemeris)
_MU_SUN_PLEPH = 1.327124400180000e+11
_RAD = math.pi / 180.0
_KM = 1.495978706910000e+08   # 1 AU in km

# Constant for conversion() (slightly different value — match reference exactly)
_MU_SUN_CONV = 1.327124280000000e+11


# ===================================================================
# Low-level vector / anomaly helpers
# ===================================================================

def _vett_py(r1: np.ndarray, r2: np.ndarray) -> np.ndarray:
    """Cross product returning shape (3,) -- pure-Python fallback."""
    return np.array([
        r1[1] * r2[2] - r1[2] * r2[1],
        r1[2] * r2[0] - r1[0] * r2[2],
        r1[0] * r2[1] - r1[1] * r2[0],
    ])


def _vers_py(V: np.ndarray) -> np.ndarray:
    """Unit vector -- pure-Python fallback."""
    return V / math.sqrt(float(V @ V))


_vett = _vett_nb if _vett_nb is not None else _vett_py
_vers = _vers_nb if _vers_nb is not None else _vers_py


def _ni2E_py(ni: float, e: float) -> float:
    """True anomaly -> eccentric anomaly -- pure-Python fallback."""
    if e < 1.0:
        return 2.0 * math.atan(math.sqrt((1.0 - e) / (1.0 + e)) * math.tan(ni / 2.0))
    else:
        return 2.0 * math.atan(math.sqrt((e - 1.0) / (e + 1.0)) * math.tan(ni / 2.0))


def _M2E_py(M: float, e: float) -> float:
    """Mean anomaly -> eccentric anomaly via Newton iteration -- fallback."""
    E = M + e * math.cos(M)
    for _ in range(100):
        Enew = E - (E - e * math.sin(E) - M) / (1.0 - e * math.cos(E))
        if abs(E - Enew) < 1e-10:
            return Enew
        E = Enew
    return E


def _E2M_py(E: float, e: float) -> float:
    """Eccentric anomaly -> mean anomaly -- pure-Python fallback."""
    if e < 1.0:
        return E - e * math.sin(E)
    else:
        return e * math.tan(E) - math.log(math.tan(E / 2.0 + math.pi / 4.0))


_ni2E = _ni2E_nb if _ni2E_nb is not None else _ni2E_py
_M2E = _M2E_nb if _M2E_nb is not None else _M2E_py
_E2M = _E2M_nb if _E2M_nb is not None else _E2M_py


# ===================================================================
# Keplerian ↔ Cartesian conversions
# ===================================================================

def _IC2par(r0: np.ndarray, v0: np.ndarray, mu: float) -> np.ndarray:
    """Cartesian (r0, v0) → 6 Keplerian elements [a, e, i, OM, om, EA]."""
    k = np.array([0.0, 0.0, 1.0])
    h = _vett(r0, v0)
    h_norm = np.linalg.norm(h)         # audit round-2: cache norm(h)
    p = float(h @ h) / mu
    n = _vett(k, h)
    n = n / np.linalg.norm(n)
    R0 = np.linalg.norm(r0)
    evett = _vett(v0, h) / mu - r0 / R0
    e2 = float(evett @ evett)

    E = np.zeros(6)
    E[0] = p / (1.0 - e2)             # a
    E[1] = math.sqrt(e2)              # e
    e = E[1]
    E[2] = math.acos(np.clip(h[2] / h_norm, -1.0, 1.0))  # i

    # Argument of periapsis
    cos_om = np.clip(float(n @ evett) / max(e, 1e-30), -1.0, 1.0)
    E[4] = math.acos(cos_om)
    if evett[2] < 0.0:
        E[4] = 2.0 * math.pi - E[4]

    # RAAN
    E[3] = math.acos(np.clip(n[0], -1.0, 1.0))
    if n[1] < 0.0:
        E[3] = 2.0 * math.pi - E[3]

    # True anomaly → eccentric anomaly
    cos_ni = np.clip(float(evett @ r0) / max(e * R0, 1e-30), -1.0, 1.0)
    ni = math.acos(cos_ni)
    if float(r0 @ v0) < 0.0:
        ni = 2.0 * math.pi - ni
    E[5] = _ni2E(ni, e)

    return E


def _par2IC(E: np.ndarray, mu: float) -> tuple[np.ndarray, np.ndarray]:
    """Keplerian elements → Cartesian (r, v).  Handles elliptic + hyperbolic."""
    a = E[0]
    e = E[1]
    i = E[2]
    omg = E[3]
    omp = E[4]
    EA = E[5]

    if e < 1.0:
        b = a * math.sqrt(1.0 - e * e)
        n = math.sqrt(mu / (a * a * a))
        xper = a * (math.cos(EA) - e)
        yper = b * math.sin(EA)
        denom = 1.0 - e * math.cos(EA)
        xdotper = -(a * n * math.sin(EA)) / denom
        ydotper = (b * n * math.cos(EA)) / denom
    else:
        b = -a * math.sqrt(e * e - 1.0)
        n = math.sqrt(-mu / (a * a * a))
        tanEA = math.tan(EA)
        cosEA = math.cos(EA)
        half_arg = math.tan(EA / 2.0 + math.pi / 4.0)
        dNdzeta = e * (1.0 + tanEA * tanEA) - (0.5 + 0.5 * half_arg * half_arg) / half_arg
        xper = a / cosEA - a * e
        yper = b * tanEA
        xdotper = a * tanEA / cosEA * n / dNdzeta
        ydotper = b / (cosEA * cosEA) * n / dNdzeta

    # Perifocal → ECI rotation matrix
    ci, si = math.cos(i), math.sin(i)
    co, so = math.cos(omg), math.sin(omg)
    cp, sp = math.cos(omp), math.sin(omp)

    R = np.array([
        [co * cp - so * sp * ci, -co * sp - so * cp * ci,  so * si],
        [so * cp + co * sp * ci, -so * sp + co * cp * ci, -co * si],
        [sp * si,                 cp * si,                  ci     ],
    ])

    r0 = R @ np.array([xper, yper, 0.0])
    v0 = R @ np.array([xdotper, ydotper, 0.0])
    return r0, v0


def _conversion(E: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Keplerian → Cartesian for ephemeris (always elliptic, uses _MU_SUN_CONV)."""
    a = E[0]
    e = E[1]
    i = E[2]
    omg = E[3]
    omp = E[4]
    EA = E[5]

    b = a * math.sqrt(1.0 - e * e)
    n = math.sqrt(_MU_SUN_CONV / (a * a * a))

    xper = a * (math.cos(EA) - e)
    yper = b * math.sin(EA)
    denom = 1.0 - e * math.cos(EA)
    xdotper = -(a * n * math.sin(EA)) / denom
    ydotper = (b * n * math.cos(EA)) / denom

    ci, si = math.cos(i), math.sin(i)
    co, so = math.cos(omg), math.sin(omg)
    cp, sp = math.cos(omp), math.sin(omp)

    R = np.array([
        [co * cp - so * sp * ci, -co * sp - so * cp * ci,  so * si],
        [so * cp + co * sp * ci, -so * sp + co * cp * ci, -co * si],
        [sp * si,                 cp * si,                  ci     ],
    ])

    r = R @ np.array([xper, yper, 0.0])
    v = R @ np.array([xdotper, ydotper, 0.0])
    return r, v


# ===================================================================
# Kepler propagation
# ===================================================================

# Audit quick-win (CEC2011 F21/F22): ``_propagateKEP`` is called twice per
# leg per NFE and used to allocate ``np.eye(3)`` (and, on the low-inclination
# branch, a second constant 3x3) on every call.  Both matrices are
# compile-time constants — hoist them to frozen module-level arrays.  The
# function only reads them (``DD @ r0``, ``DD.T @ r``); writeable=False
# makes any future in-place write fail loudly instead of corrupting shared
# state.
_KEP_EYE3 = np.eye(3)
_KEP_EYE3.flags.writeable = False
_KEP_DD_LOW_INC = np.array([[1.0, 0.0, 0.0],
                            [0.0, 0.0, 1.0],
                            [0.0, -1.0, 0.0]])
_KEP_DD_LOW_INC.flags.writeable = False


def _propagateKEP(
    r0: np.ndarray, v0: np.ndarray, t: float, mu: float,
) -> tuple[np.ndarray, np.ndarray]:
    """Analytical Keplerian propagation for time *t* (seconds)."""
    DD = _KEP_EYE3
    h = _vett(r0, v0)
    ih = h / np.linalg.norm(h)

    # Low-inclination guard (match reference abs threshold)
    if abs(abs(ih[2]) - 1.0) < 1e-3:
        DD = _KEP_DD_LOW_INC
        r0 = DD @ r0
        v0 = DD @ v0

    E = _IC2par(r0, v0, mu)
    M0 = _E2M(E[5], E[1])

    a = E[0]
    if E[1] < 1.0:
        M = M0 + math.sqrt(mu / (a * a * a)) * t
    else:
        M = M0 + math.sqrt(-mu / (a * a * a)) * t

    E[5] = _M2E(M, E[1])
    r, v = _par2IC(E, mu)

    r = DD.T @ r
    v = DD.T @ v
    return r, v


# ===================================================================
# Analytical planetary ephemeris
# ===================================================================

def _pleph_an(mjd2000: float, planet: int) -> tuple[np.ndarray, np.ndarray]:
    """Analytical planetary ephemeris for planets 1-9.

    Returns position [km] and velocity [km/s] in ecliptic J2000.
    """
    T = (mjd2000 + 36525.0) / 36525.0
    TT = T * T
    TTT = T * TT

    E = np.zeros(6)

    if planet == 1:  # Mercury
        E[0] = 0.38709860
        E[1] = 0.205614210 + 0.000020460 * T - 0.000000030 * TT
        E[2] = 7.002880555555555560 + 1.86083333333333333e-3 * T - 1.83333333333333333e-5 * TT
        E[3] = 4.71459444444444444e+1 + 1.185208333333333330 * T + 1.73888888888888889e-4 * TT
        E[4] = 2.87537527777777778e+1 + 3.70280555555555556e-1 * T + 1.20833333333333333e-4 * TT
        XM = 1.49472515288888889e+5 + 6.38888888888888889e-6 * T
        E[5] = 1.02279380555555556e2 + XM * T

    elif planet == 2:  # Venus
        E[0] = 0.72333160
        E[1] = 0.006820690 - 0.000047740 * T + 0.0000000910 * TT
        E[2] = 3.393630555555555560 + 1.00583333333333333e-3 * T - 9.72222222222222222e-7 * TT
        E[3] = 7.57796472222222222e+1 + 8.9985e-1 * T + 4.1e-4 * TT
        E[4] = 5.43841861111111111e+1 + 5.08186111111111111e-1 * T - 1.38638888888888889e-3 * TT
        XM = 5.8517803875e+4 + 1.28605555555555556e-3 * T
        E[5] = 2.12603219444444444e2 + XM * T

    elif planet == 3:  # Earth
        E[0] = 1.000000230
        E[1] = 0.016751040 - 0.000041800 * T - 0.0000001260 * TT
        E[2] = 0.0
        E[3] = 0.0
        E[4] = 1.01220833333333333e+2 + 1.7191750 * T + 4.52777777777777778e-4 * TT + 3.33333333333333333e-6 * TTT
        XM = 3.599904975e+4 - 1.50277777777777778e-4 * T - 3.33333333333333333e-6 * TT
        E[5] = 3.58475844444444444e2 + XM * T

    elif planet == 4:  # Mars
        E[0] = 1.5236883990
        E[1] = 0.093312900 + 0.0000920640 * T - 0.0000000770 * TT
        E[2] = 1.850333333333333330 - 6.75e-4 * T + 1.26111111111111111e-5 * TT
        E[3] = 4.87864416666666667e+1 + 7.70991666666666667e-1 * T - 1.38888888888888889e-6 * TT - 5.33333333333333333e-6 * TTT
        E[4] = 2.85431761111111111e+2 + 1.069766666666666670 * T + 1.3125e-4 * TT + 4.13888888888888889e-6 * TTT
        XM = 1.91398585e+4 + 1.80805555555555556e-4 * T + 1.19444444444444444e-6 * TT
        E[5] = 3.19529425e2 + XM * T

    elif planet == 5:  # Jupiter
        E[0] = 5.2025610
        E[1] = 0.048334750 + 0.000164180 * T - 0.00000046760 * TT - 0.00000000170 * TTT
        E[2] = 1.308736111111111110 - 5.69611111111111111e-3 * T + 3.88888888888888889e-6 * TT
        E[3] = 9.94433861111111111e+1 + 1.010530 * T + 3.52222222222222222e-4 * TT - 8.51111111111111111e-6 * TTT
        E[4] = 2.73277541666666667e+2 + 5.99431666666666667e-1 * T + 7.0405e-4 * TT + 5.07777777777777778e-6 * TTT
        XM = 3.03469202388888889e+3 - 7.21588888888888889e-4 * T + 1.78444444444444444e-6 * TT
        E[5] = 2.25328327777777778e2 + XM * T

    elif planet == 6:  # Saturn
        E[0] = 9.5547470
        E[1] = 0.055892320 - 0.00034550 * T - 0.0000007280 * TT + 0.000000000740 * TTT
        E[2] = 2.492519444444444440 - 3.91888888888888889e-3 * T - 1.54888888888888889e-5 * TT + 4.44444444444444444e-8 * TTT
        E[3] = 1.12790388888888889e+2 + 8.73195138888888889e-1 * T - 1.52180555555555556e-4 * TT - 5.30555555555555556e-6 * TTT
        E[4] = 3.38307772222222222e+2 + 1.085220694444444440 * T + 9.78541666666666667e-4 * TT + 9.91666666666666667e-6 * TTT
        XM = 1.22155146777777778e+3 - 5.01819444444444444e-4 * T - 5.19444444444444444e-6 * TT
        E[5] = 1.75466216666666667e2 + XM * T

    elif planet == 7:  # Uranus
        E[0] = 19.218140
        E[1] = 0.04634440 - 0.000026580 * T + 0.0000000770 * TT
        E[2] = 7.72463888888888889e-1 + 6.25277777777777778e-4 * T + 3.95e-5 * TT
        E[3] = 7.34770972222222222e+1 + 4.98667777777777778e-1 * T + 1.31166666666666667e-3 * TT
        E[4] = 9.80715527777777778e+1 + 9.85765e-1 * T - 1.07447222222222222e-3 * TT - 6.05555555555555556e-7 * TTT
        XM = 4.28379113055555556e+2 + 7.88444444444444444e-5 * T + 1.11111111111111111e-9 * TT
        E[5] = 7.26488194444444444e1 + XM * T

    elif planet == 8:  # Neptune
        E[0] = 30.109570
        E[1] = 0.008997040 + 0.0000063300 * T - 0.0000000020 * TT
        E[2] = 1.779241666666666670 - 9.54361111111111111e-3 * T - 9.11111111111111111e-6 * TT
        E[3] = 1.30681358333333333e+2 + 1.0989350 * T + 2.49866666666666667e-4 * TT - 4.71777777777777778e-6 * TTT
        E[4] = 2.76045966666666667e+2 + 3.25639444444444444e-1 * T + 1.4095e-4 * TT + 4.11333333333333333e-6 * TTT
        XM = 2.18461339722222222e+2 - 7.03333333333333333e-5 * T
        E[5] = 3.77306694444444444e1 + XM * T

    elif planet == 9:  # Pluto (5th-order fit, valid 2000-2100)
        T = mjd2000 / 36525.0
        TT = T * T
        TTT = TT * T
        TTTT = TTT * T
        TTTTT = TTTT * T
        E[0] = 39.34041961252520 + 4.33305138120726 * T - 22.93749932403733 * TT + 48.76336720791873 * TTT - 45.52494862462379 * TTTT + 15.55134951783384 * TTTTT
        E[1] = 0.24617365396517 + 0.09198001742190 * T - 0.57262288991447 * TT + 1.39163022881098 * TTT - 1.46948451587683 * TTTT + 0.56164158721620 * TTTTT
        E[2] = 17.16690003784702 - 0.49770248790479 * T + 2.73751901890829 * TT - 6.26973695197547 * TTT + 6.36276927397430 * TTTT - 2.37006911673031 * TTTTT
        E[3] = 110.222019291707 + 1.551579150048 * T - 9.701771291171 * TT + 25.730756810615 * TTT - 30.140401383522 * TTTT + 12.796598193159 * TTTTT
        E[4] = 113.368933916592 + 9.436835192183 * T - 35.762300003726 * TT + 48.966118351549 * TTT - 19.384576636609 * TTTT - 3.362714022614 * TTTTT
        E[5] = 15.17008631634665 + 137.023166578486 * T + 28.362805871736 * TT - 29.677368415909 * TTT - 3.585159909117 * TTTT + 13.406844652829 * TTTTT
    else:
        raise ValueError(f"planet must be 1-9, got {planet}")

    # AU → km, degrees → radians
    E[0] *= _KM
    for idx in range(2, 6):
        E[idx] *= _RAD
    E[5] = E[5] % (2.0 * math.pi)

    # Mean anomaly → eccentric anomaly
    E[5] = _M2E(E[5], E[1])

    r, v = _conversion(E)
    return r, v


# ===================================================================
# Lambert solver
# ===================================================================

def _tofabn_py(sigma: float, alfa: float, beta: float, N: int) -> float:
    """Lambert TOF -- pure-Python fallback."""
    if sigma > 0.0:
        return sigma * math.sqrt(sigma) * (
            (alfa - math.sin(alfa)) - (beta - math.sin(beta)) + N * 2.0 * math.pi
        )
    else:
        return -sigma * math.sqrt(-sigma) * (
            (math.sinh(alfa) - alfa) - (math.sinh(beta) - beta)
        )


def _x2tof_py(x: float, s: float, c: float, lw: int, N: int) -> float:
    """Lambert: x parameter -> TOF -- pure-Python fallback."""
    am = s / 2.0
    a = am / (1.0 - x * x)
    if x < 1.0:
        beta = 2.0 * math.asin(math.sqrt((s - c) / (2.0 * a)))
        if lw:
            beta = -beta
        alfa = 2.0 * math.acos(np.clip(x, -1.0, 1.0))
    else:
        alfa = 2.0 * math.acosh(x)
        beta = 2.0 * math.asinh(math.sqrt((s - c) / (-2.0 * a)))
        if lw:
            beta = -beta
    return _tofabn(a, alfa, beta, N)


_tofabn = _tofabn_nb if _tofabn_nb is not None else _tofabn_py
_x2tof = _x2tof_nb if _x2tof_nb is not None else _x2tof_py


# Audit quick-win (CEC2011 F21/F22): shared NaN sentinel for the four
# ``_lambertI`` failure paths (exception guard, t<=0, and the two secant
# non-convergence guards), which each allocated a fresh
# ``np.array([nan, nan, nan])`` per hit.  Every consumer only *reads* the
# returned vectors (``norm(v_out - v_in)`` and column-copy into
# ``v_sc_pl_in``) — verified against both call sites in ``_mga_dsm_core``
# — so a single frozen constant is safe; writeable=False enforces it.
_LAMBERT_NAN3 = np.array([np.nan, np.nan, np.nan])
_LAMBERT_NAN3.flags.writeable = False


def _lambertI(
    r1: np.ndarray,
    r2: np.ndarray,
    t: float,
    mu: float,
    lw: int,
    N: int = 0,
    branch: str = "r",
) -> tuple[np.ndarray, np.ndarray]:
    """Solve Lambert's boundary value problem.

    Returns (v1, v2) velocity vectors at departure/arrival [same units as mu, r].

    Audit CRIT-06: any ``ValueError`` from ``math.log`` / ``math.sqrt`` /
    ``math.acos`` / ``math.acosh`` (raised on degenerate or ill-posed
    geometries that the input bounds technically allow) is converted into
    the same ``(NaN, NaN)`` sentinel that the convergence-failure path
    uses.  ``mga_dsm`` then converts the propagated NaN sum into the
    standard CEC2011 infeasibility penalty (``NAN_PENALTY = 1e30``) at
    the function boundary.
    """
    try:
        return _lambertI_core(r1, r2, t, mu, lw, N, branch)
    except (ValueError, ZeroDivisionError, FloatingPointError):
        return _LAMBERT_NAN3, _LAMBERT_NAN3


def _lambertI_core(
    r1: np.ndarray,
    r2: np.ndarray,
    t: float,
    mu: float,
    lw: int,
    N: int,
    branch: str,
) -> tuple[np.ndarray, np.ndarray]:
    """Inner core of :func:`_lambertI` -- raises on math-domain errors."""
    if t <= 0.0:
        return _LAMBERT_NAN3, _LAMBERT_NAN3

    tol = 1e-11

    # Non-dimensional units
    R = np.linalg.norm(r1)
    V = math.sqrt(mu / R)
    T = R / V

    r1n = r1 / R
    r2n = r2 / R
    tn = t / T

    # Geometry
    r2mod = np.linalg.norm(r2n)
    cos_theta = np.clip(float(r1n @ r2n) / r2mod, -1.0, 1.0)
    theta = math.acos(cos_theta)
    if lw:
        theta = 2.0 * math.pi - theta

    c = math.sqrt(1.0 + r2mod * r2mod - 2.0 * r2mod * math.cos(theta))
    s = (1.0 + r2mod + c) / 2.0
    am = s / 2.0
    lam = math.sqrt(r2mod) * math.cos(theta / 2.0) / s

    # Secant iteration to find x
    if N == 0:
        inn1 = -0.5233
        inn2 = 0.5233
        x1 = math.log(1.0 + inn1)
        x2 = math.log(1.0 + inn2)
        y1 = math.log(_x2tof(inn1, s, c, lw, N)) - math.log(tn)
        y2 = math.log(_x2tof(inn2, s, c, lw, N)) - math.log(tn)

        converged = False
        for _ in range(60):
            if y1 == y2:
                break  # secant degenerate
            xnew = (x1 * y2 - y1 * x2) / (y2 - y1)
            ynew = math.log(_x2tof(math.exp(xnew) - 1.0, s, c, lw, N)) - math.log(tn)
            x1, y1 = x2, y2
            x2, y2 = xnew, ynew
            if abs(x1 - xnew) < tol:
                converged = True
                break
        if not converged:
            # Loop exhausted 60 iterations or hit a degenerate secant
            # without reaching tolerance.  Signal infeasibility via the
            # same NaN convention used at the t<=0 guard above instead
            # of returning a stale ``xnew`` (silent garbage).
            return _LAMBERT_NAN3, _LAMBERT_NAN3
        x = math.exp(xnew) - 1.0
    else:
        if branch == "l":
            inn1, inn2 = -0.5234, -0.2234
        else:
            inn1, inn2 = 0.7234, 0.5234
        x1 = math.tan(inn1 * math.pi / 2.0)
        x2 = math.tan(inn2 * math.pi / 2.0)
        y1 = _x2tof(inn1, s, c, lw, N) - tn
        y2 = _x2tof(inn2, s, c, lw, N) - tn

        converged = False
        for _ in range(60):
            if y1 == y2:
                break  # secant degenerate
            xnew = (x1 * y2 - y1 * x2) / (y2 - y1)
            ynew = _x2tof(math.atan(xnew) * 2.0 / math.pi, s, c, lw, N) - tn
            x1, y1 = x2, y2
            x2, y2 = xnew, ynew
            if abs(x1 - xnew) < tol:
                converged = True
                break
        if not converged:
            # Same convergence guard as the N==0 branch above.
            return _LAMBERT_NAN3, _LAMBERT_NAN3
        x = math.atan(xnew) * 2.0 / math.pi

    # Recover conic from x
    a = am / (1.0 - x * x)

    if x < 1.0:  # ellipse
        beta = 2.0 * math.asin(math.sqrt((s - c) / (2.0 * a)))
        if lw:
            beta = -beta
        alfa = 2.0 * math.acos(np.clip(x, -1.0, 1.0))
        psi = (alfa - beta) / 2.0
        eta2 = 2.0 * a * math.sin(psi) ** 2 / s
        eta = math.sqrt(eta2)
    else:  # hyperbola
        beta = 2.0 * math.asinh(math.sqrt((c - s) / (2.0 * a)))
        if lw:
            beta = -beta
        alfa = 2.0 * math.acosh(x)
        psi = (alfa - beta) / 2.0
        eta2 = -2.0 * a * math.sinh(psi) ** 2 / s
        eta = math.sqrt(eta2)

    p = r2mod / am / eta2 * math.sin(theta / 2.0) ** 2
    sigma1 = (1.0 / eta / math.sqrt(am)) * (2.0 * lam * am - (lam + x * eta))

    ih = _vers(_vett(r1n, r2n))
    if lw:
        ih = -ih

    vr1 = sigma1
    vt1 = math.sqrt(p)
    v1 = vr1 * r1n + vt1 * _vett(ih, r1n)

    vt2 = vt1 / r2mod
    vr2 = -vr1 + (vt1 - vt2) / math.tan(theta / 2.0)
    v2 = vr2 * r2n / r2mod + vt2 * _vett(ih, r2n / r2mod)

    # Re-dimensionalise
    v1 = v1 * V
    v2 = v2 * V

    return v1, v2


# ===================================================================
# MGA-DSM main solver
# ===================================================================

def mga_dsm(
    t: np.ndarray,
    sequence: np.ndarray | list[int],
    objective_type: str,
    rp_target: float = 0.0,
    e_target: float = 0.0,
) -> float:
    """Multiple Gravity Assist with Deep Space Manoeuvres trajectory solver.

    Parameters
    ----------
    t : ndarray
        Decision vector.
    sequence : array-like of int
        Planet sequence (1=Mercury .. 6=Saturn).
    objective_type : str
        ``"orbit insertion"``, ``"total DV rndv"``, or ``"rndv"``.
    rp_target, e_target : float
        Target orbit parameters (only for ``"orbit insertion"``).

    Returns
    -------
    float
        Total delta-V cost (km/s).  Returns the CEC2011 infeasibility
        penalty (``NAN_PENALTY = 1e30``) when the trajectory is
        ill-posed: convergence failures in the Lambert solver, math-
        domain errors in any orbital subroutine, or any non-finite
        intermediate value all funnel through the same penalty so the
        optimizer never observes ``NaN`` (audit CRIT-06).
    """
    try:
        return _mga_dsm_core(t, sequence, objective_type, rp_target, e_target)
    except (ValueError, ZeroDivisionError, FloatingPointError,
            np.linalg.LinAlgError):
        return NAN_PENALTY


def _mga_dsm_core(
    t: np.ndarray,
    sequence: np.ndarray | list[int],
    objective_type: str,
    rp_target: float,
    e_target: float,
) -> float:
    """Inner core of :func:`mga_dsm` -- raises on math-domain errors."""
    sequence = np.asarray(sequence, dtype=int)
    N = len(sequence)
    seq = np.abs(sequence)

    # ── Parse decision vector ──
    tdep = t[0]
    VINF = t[1]
    udir = t[2]
    vdir = t[3]

    tof = np.zeros(N - 1)
    alpha = np.zeros(N - 1)
    for i in range(N - 1):
        tof[i] = t[i + 4]
        alpha[i] = t[N + i + 3]

    rp_non_dim = np.zeros(N - 2)
    gamma = np.zeros(N - 2)
    for i in range(N - 2):
        rp_non_dim[i] = t[i + 2 * N + 2]
        gamma[i] = t[3 * N + i]

    # ── Planetary positions & velocities ──
    r = np.zeros((3, N))
    v = np.zeros((3, N))
    muvec = np.zeros(N)

    T_epoch = tdep
    for i in range(N):
        r[:, i], v[:, i] = _pleph_an(T_epoch, int(seq[i]))
        muvec[i] = _MU_PLANET[seq[i] - 1]
        if i < N - 1:
            T_epoch += tof[i]

    # Dimensional flyby radii
    rp = np.zeros(N - 2)
    for i in range(N - 2):
        rp[i] = rp_non_dim[i] * _RPL[seq[i + 1] - 1]

    # ── FIRST LEG (P1 → DSM1 → P2) ──
    vtemp = _vett(r[:, 0], v[:, 0])
    iP1 = v[:, 0] / np.linalg.norm(v[:, 0])
    zP1 = vtemp / np.linalg.norm(vtemp)
    # Use _vett (matches the rest of this solver) instead of np.cross.
    # np.cross would bypass the JIT kernel and round differently from
    # the other 6 cross products in this function, breaking F21/F22
    # determinism between the Numba and pure-Python paths.
    jP1 = _vett(zP1, iP1)

    theta_dep = 2.0 * math.pi * udir
    phi_dep = math.acos(2.0 * vdir - 1.0) - math.pi / 2.0

    vinf = VINF * (
        math.cos(theta_dep) * math.cos(phi_dep) * iP1
        + math.sin(theta_dep) * math.cos(phi_dep) * jP1
        + math.sin(phi_dep) * zP1
    )

    v_sc_pl_out = np.zeros((3, N))
    v_sc_pl_in = np.zeros((3, N))

    v_sc_pl_in[:, 0] = v[:, 0]
    v_sc_pl_out[:, 0] = v[:, 0] + vinf

    # Propagate to DSM1
    tDSM1 = alpha[0] * tof[0]
    rd1, v_sc_dsm_in1 = _propagateKEP(
        r[:, 0], v_sc_pl_out[:, 0], tDSM1 * 86400.0, _MU_SUN
    )

    # Lambert from DSM1 → P2
    lw_vec = _vett(rd1, r[:, 1])
    lw = 0 if lw_vec[2] >= 0.0 else 1

    v_sc_dsm_out1, v_sc_pl_in_2 = _lambertI(
        rd1, r[:, 1], tof[0] * (1.0 - alpha[0]) * 86400.0, _MU_SUN, lw
    )
    v_sc_pl_in[:, 1] = v_sc_pl_in_2

    DV = np.zeros(N)
    DV[0] = np.linalg.norm(v_sc_dsm_out1 - v_sc_dsm_in1)

    # ── INTERMEDIATE LEGS ──
    for i in range(N - 2):
        v_rel_in = v_sc_pl_in[:, i + 1] - v[:, i + 1]
        e_flyby = 1.0 + rp[i] / muvec[i + 1] * float(v_rel_in @ v_rel_in)
        beta_rot = 2.0 * math.asin(np.clip(1.0 / e_flyby, -1.0, 1.0))

        v_rel_in_norm = np.linalg.norm(v_rel_in)  # audit round-2: cache
        ix = v_rel_in / v_rel_in_norm
        iy = _vett(ix, v[:, i + 1] / np.linalg.norm(v[:, i + 1]))
        iy = iy / np.linalg.norm(iy)
        iz = _vett(ix, iy)

        iVout = (
            math.cos(beta_rot) * ix
            + math.cos(gamma[i]) * math.sin(beta_rot) * iy
            + math.sin(gamma[i]) * math.sin(beta_rot) * iz
        )
        v_rel_out = v_rel_in_norm * iVout
        v_sc_pl_out[:, i + 1] = v[:, i + 1] + v_rel_out

        # Propagate to DSM
        tDSM_i = alpha[i + 1] * tof[i + 1]
        rd_i, v_sc_dsm_in_i = _propagateKEP(
            r[:, i + 1], v_sc_pl_out[:, i + 1], tDSM_i * 86400.0, _MU_SUN
        )

        # Lambert from DSM → next planet
        lw_vec = _vett(rd_i, r[:, i + 2])
        lw = 0 if lw_vec[2] >= 0.0 else 1

        v_sc_dsm_out_i, v_sc_pl_in_next = _lambertI(
            rd_i, r[:, i + 2], tof[i + 1] * (1.0 - alpha[i + 1]) * 86400.0,
            _MU_SUN, lw,
        )
        v_sc_pl_in[:, i + 2] = v_sc_pl_in_next
        DV[i + 1] = np.linalg.norm(v_sc_dsm_out_i - v_sc_dsm_in_i)

    # ── FINAL BLOCK ──
    DVrel = np.linalg.norm(v[:, N - 1] - v_sc_pl_in[:, N - 1])

    if objective_type == "orbit insertion":
        DVper = math.sqrt(DVrel ** 2 + 2.0 * muvec[N - 1] / rp_target)
        DVper2 = math.sqrt(
            2.0 * muvec[N - 1] / rp_target
            - muvec[N - 1] / rp_target * (1.0 - e_target)
        )
        DVarr = abs(DVper - DVper2)
    elif objective_type in ("total DV orbit insertion",):
        DVper = math.sqrt(DVrel ** 2 + 2.0 * muvec[N - 1] / rp_target)
        DVper2 = math.sqrt(
            2.0 * muvec[N - 1] / rp_target
            - muvec[N - 1] / rp_target * (1.0 - e_target)
        )
        DVarr = abs(DVper - DVper2)
    elif objective_type in ("rndv", "total DV rndv"):
        DVarr = DVrel
    else:
        DVarr = DVrel

    DV[N - 1] = DVarr

    # ── Objective ──
    if objective_type in ("total DV orbit insertion", "total DV rndv"):
        result = float(np.sum(DV) + VINF)
    else:
        result = float(np.sum(DV))

    # Audit CRIT-06: Lambert non-convergence (and other ill-conditioned
    # geometries) leak NaN into ``DV`` via the ``_lambertI`` sentinel
    # return.  Convert any non-finite total to the standard CEC2011
    # infeasibility penalty so the optimizer's selection step never
    # has to compare NaN to a finite value -- otherwise NaN propagates
    # through the elite archive and ACE reward updates and silently
    # corrupts the run.
    if not math.isfinite(result):
        return NAN_PENALTY
    return result
