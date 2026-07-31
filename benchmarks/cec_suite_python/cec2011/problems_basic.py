"""CEC2011 basic benchmark functions F1--F8 (from bench_func.m).

Real-world and scientific optimization problems from the CEC2011 competition.
Unlike the CEC2017/2020 suites, these functions operate on single solutions
(1-D arrays), not batched (M, D) populations, and each has a fixed or
problem-specific dimensionality.

Functions
---------
f01_fm_sound         FM sound wave parameter estimation (D=6)
f02_lennard_jones    Lennard-Jones potential (D=30, 10 atoms x 3 coords)
f03_bifunctional_catalyst  Bifunctional catalyst blend ODE control (D=1)
f04_stirred_tank     Non-linear stirred tank reactor ODE control (D=1)
f05_tersoff_sib      Tersoff potential Si(B) (D=30, 10 atoms x 3 coords)
f06_tersoff_sic      Tersoff potential Si(C) (D=30, 10 atoms x 3 coords)
f07_spread_spectrum  Spread spectrum radar polyphase (D=20)
f08_tnep             Transmission network expansion planning (D=7)

References
----------
B. B. Saha and S. Das, "Problem Definitions and Evaluation Criteria for
CEC 2011 Competition on Testing Evolutionary Algorithms on Real World
Optimization Problems," Jadavpur University, 2010.
"""

from __future__ import annotations

import numpy as np

# ---------------------------------------------------------------------------
# Numba-accelerated inner loops for F5/F6 (Tersoff) and F7 (Spread Spectrum)
#
# The JIT kernels live in this suite's own ``_numba.py`` module --
# see the CEC2013/CEC2017 layout.  When numba is unavailable
# the imports return ``None`` and the per-function pure-Python fallbacks
# below are used.
# ---------------------------------------------------------------------------

from ._constants import NAN_PENALTY
from ._numba import (
    _bifunctional_catalyst_nb,
    _spread_spectrum_nb,
    _stirred_tank_nb,
    _tersoff_inner_nb,
)


# ---------------------------------------------------------------------------
# F1: Parameter Estimation for FM Sound Waves
# ---------------------------------------------------------------------------

def f01_fm_sound(x: np.ndarray) -> float:
    """F1: Parameter estimation for frequency-modulated sound waves.

    Parameters
    ----------
    x : np.ndarray
        Decision vector of length 6.  Bounds: [-6.4, 6.35].

    Returns
    -------
    float
        Sum of squared residuals between candidate and target FM signals
        evaluated at 101 equally-spaced time steps.
    """
    # Audit MED-PERF-01: ``theta``, ``t``, and the target FM signal are
    # constant across every NFE — they were previously rebuilt 150,000
    # times per run for an objective whose intrinsic work is one
    # broadcast multiply.  Module-level constants
    # ``_F01_THETA``, ``_F01_THETA_T``, ``_F01_TARGET`` are precomputed
    # below.
    theta_t = _F01_THETA_T
    y_t = x[0] * np.sin(
        x[1] * theta_t
        + x[2] * np.sin(x[3] * theta_t + x[4] * np.sin(x[5] * theta_t))
    )
    return float(np.sum((y_t - _F01_TARGET) ** 2))


# Audit MED-PERF-01: precomputed F01 constants.  Defined after the
# function so the docstring/signature stay at the top of the file.
_F01_THETA: float = 2.0 * np.pi / 100.0
_F01_THETA_T: np.ndarray = _F01_THETA * np.arange(101, dtype=np.float64)
_F01_TARGET: np.ndarray = np.sin(
    5.0 * _F01_THETA_T
    - 1.5 * np.sin(4.8 * _F01_THETA_T + 2.0 * np.sin(4.9 * _F01_THETA_T))
)
_F01_TARGET.flags.writeable = False
_F01_THETA_T.flags.writeable = False


# ---------------------------------------------------------------------------
# F2: Lennard-Jones Potential
# ---------------------------------------------------------------------------

def f02_lennard_jones(x: np.ndarray) -> float:
    """F2: Lennard-Jones potential energy minimisation.

    The decision vector encodes 3-D Cartesian coordinates for *n* atoms
    packed as ``[x1, y1, z1, x2, y2, z2, ...]``.

    Parameters
    ----------
    x : np.ndarray
        Decision vector of length ``3 * n_atoms`` (default D=30 for 10
        atoms).  Bounds are dimension-dependent; see ``define_boundaries.m``.

    Returns
    -------
    float
        Lennard-Jones pair-potential energy.  Lower is better; the global
        minimum for 10 atoms is approximately -12.712.

    Notes
    -----
    The original reference source uses ``a(i,j)=1`` and ``b(i,j)=2`` for
    all pairs, giving ``V = sum 1/r^12 - 2/r^6``.  Coincident atoms are
    deliberately not guarded: ``Inf - Inf`` becomes ``NaN``, and the
    CEC2011 wrapper maps final ``NaN`` objectives to ``0.0``.
    """
    n = len(x) // 3
    atoms = x.reshape(n, 3)

    # Pairwise distance matrix — upper triangle only (i < j)
    # Using broadcasting: diff[i,j] = atoms[i] - atoms[j]
    diff = atoms[:, np.newaxis, :] - atoms[np.newaxis, :, :]  # (n, n, 3)
    dist = np.sqrt(np.sum(diff ** 2, axis=2))                 # (n, n)

    # Extract upper-triangle distances (i < j).  Do not clamp zero distances:
    # the reference relies on the resulting NaN and maps it to 0.0 later.
    ii, jj = np.triu_indices(n, k=1)
    rij = dist[ii, jj]

    with np.errstate(divide="ignore", invalid="ignore"):
        r6 = rij ** 6
        r12 = r6 ** 2
        return float(np.sum(1.0 / r12 - 2.0 / r6))


# ---------------------------------------------------------------------------
# F3: Bifunctional Catalyst Blend Optimal Control
# ---------------------------------------------------------------------------

# Coefficient matrix from c_bifunc_data.mat (10 x 4).
# Each row i gives polynomial coefficients for rate constant k_i(u):
#   k_i = c[i,0] + c[i,1]*u + c[i,2]*u^2 + c[i,3]*u^3
_BIFUNC_COEFFS = np.array([
    [ 0.002918487, -0.008045787,  0.006749947, -0.001416647],
    [ 9.509977,    -35.00994,     42.83329,    -17.33333   ],
    [26.82093,     -95.56079,    113.0398,     -44.29997   ],
    [208.7241,    -719.8052,     827.7466,    -316.6655    ],
    [ 1.350005,     -6.850027,    12.16671,     -6.666689  ],
    [ 0.01921995,   -0.0794532,    0.110566,    -0.05033333],
    [ 0.1323596,    -0.469255,     0.5539323,   -0.2166664 ],
    [ 7.339981,    -25.27328,     29.93329,    -11.99999   ],
    [-0.3950534,     1.679353,    -1.777829,     0.4974987 ],
    [-0.0000250466,  0.01005854,  -0.01986696,   0.00983347],
], dtype=np.float64)
_BIFUNC_COEFFS.flags.writeable = False


def f03_bifunctional_catalyst(x: np.ndarray) -> float:
    """F3: Bifunctional catalyst blend optimal control (ODE problem).

    A 7-state ODE system is integrated over [0, 0.78] with initial
    conditions y(0) = [1, 0, 0, 0, 0, 0, 0].  The objective is the
    final value of the last state variable, scaled by 1e3.

    Parameters
    ----------
    x : np.ndarray
        Decision vector of length 1.  Bounds: [0.6, 0.9].

    Returns
    -------
    float
        ``y_7(t_final) * 1000``, where y_7 is the last ODE state.

    Notes
    -----
    Requires ``scipy.integrate.solve_ivp``.  The relative tolerance is
    set to 1e-1 to match the reference ``odeset('RelTol', 1e-1)``.

    Reproducibility caveat
    ----------------------
    SciPy's RK45 integrator is an *adaptive* solver: the step sizes it
    chooses depend on intermediate floating-point comparisons against
    the tolerance, which can vary in the last bit across BLAS/LAPACK
    versions, platform compilers, and CPU ISAs.  Therefore the value
    returned for a *given* ``u`` may differ by O(rtol) -- here ~10% --
    between machines, even with identical seeds.  This matches the
    behaviour of the reference ``ode45`` solver and is a property of the
    benchmark problem itself, not a bug in this implementation.  Do
    *not* tighten ``rtol`` to "fix" reproducibility -- it would diverge
    from the published F3/F4 numbers.
    """
    u = float(x[0])
    if _bifunctional_catalyst_nb is not None:
        return float(_bifunctional_catalyst_nb(u, _BIFUNC_COEFFS))

    # Audit quick-win (CEC2011 F3): the scipy import is only needed by this
    # pure-Python fallback, but it used to execute BEFORE the JIT check —
    # paying a sys.modules dict lookup + attribute fetch on every NFE of the
    # always-taken Numba path (~13% of F3 cost).  Import it lazily here so
    # the JIT path never touches it.
    from scipy.integrate import solve_ivp

    ml = np.array([1.0, u, u ** 2, u ** 3])
    k = _BIFUNC_COEFFS @ ml  # 10 rate constants

    def ode_fn(t: float, y: np.ndarray) -> np.ndarray:
        dy = np.zeros(7)
        dy[0] = -k[0] * y[0]
        dy[1] = k[0] * y[0] - (k[1] + k[2]) * y[1] + k[3] * y[4]
        dy[2] = k[1] * y[1]
        dy[3] = -k[5] * y[3] + k[4] * y[4]
        dy[4] = (k[2] * y[1] + k[5] * y[3]
                 - (k[3] + k[4] + k[7] + k[8]) * y[4]
                 + k[6] * y[5] + k[9] * y[6])
        dy[5] = k[7] * y[4] - k[6] * y[5]
        dy[6] = k[8] * y[4] - k[9] * y[6]
        return dy

    y0 = np.array([1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
    sol = solve_ivp(ode_fn, [0.0, 0.78], y0, method='RK45', rtol=1e-1)
    if not sol.success:
        return NAN_PENALTY  # integration failure → large penalty (CRIT-07)
    # Reference: f = Y(end, end) * 1e3  (last time-step, last state variable)
    return float(sol.y[-1, -1] * 1e3)


# ---------------------------------------------------------------------------
# F4: Stirred Tank Reactor Optimal Control
# ---------------------------------------------------------------------------

def f04_stirred_tank(x: np.ndarray) -> float:
    """F4: Optimal control of a non-linear stirred tank reactor (ODE).

    A 2-state ODE system is integrated over [0, 0.78].  The cost
    functional sums per-time-step state norms plus a control penalty.

    Parameters
    ----------
    x : np.ndarray
        Decision vector of length 1.  Bounds: [0, 5].

    Returns
    -------
    float
        ``sum_t (y1(t)^2 + y2(t)^2 + 0.1 * u^2)`` over all solver
        time-steps.

    Notes
    -----
    Requires ``scipy.integrate.solve_ivp``.  Relative tolerance is 1e-1
    to match the original reference source.

    Reproducibility caveat
    ----------------------
    Same caveat as F3 (``f03_bifunctional_catalyst``): the RK45
    integrator's adaptive step sizes are not guaranteed to be
    bit-identical across machines.  The returned cost may differ by
    O(rtol) -- here ~10% -- between platforms.  This is a property of
    the benchmark problem definition (matching the reference ``ode45``) and
    cannot be made deterministic without changing the published
    numbers.
    """
    u = float(x[0])
    if _stirred_tank_nb is not None:
        return float(_stirred_tank_nb(u))

    # Audit quick-win (CEC2011 F4): same as F3 — keep the scipy import off
    # the always-taken JIT path; only the pure-Python fallback needs it.
    from scipy.integrate import solve_ivp

    def ode_fn(t: float, y: np.ndarray) -> np.ndarray:
        dy = np.zeros(2)
        with np.errstate(over="ignore", invalid="ignore"):
            # Keep the unclamped exponential so fallback behavior follows the
            # reference problem definition when the Numba path is unavailable.
            exp_arg = 25.0 * y[0] / (y[0] + 2.0)
            exp_term = np.exp(exp_arg)
            dy[0] = -(2.0 + u) * (y[0] + 0.25) + (y[1] + 0.5) * exp_term
            dy[1] = 0.5 - y[1] - (y[1] + 0.5) * exp_term
        return dy

    y0 = np.array([0.09, 0.09])
    sol = solve_ivp(ode_fn, [0.0, 0.78], y0, method="RK45", rtol=1e-1, atol=1e-6)
    if not sol.success:
        return NAN_PENALTY  # integration failure → large penalty (CRIT-07)
    # Reference: f = sum(sum(Y.^2, 2) + 0.1*u*u)
    # Y has shape (nsteps, 2) — sum squared states per step, add control cost
    Y = sol.y.T  # (n_steps, 2)
    return float(np.sum(np.sum(Y ** 2, axis=1) + 0.1 * u * u))


# ---------------------------------------------------------------------------
# F5 / F6 helper: Tersoff potential (shared logic, different parameters)
# ---------------------------------------------------------------------------

def _tersoff_potential(
    x: np.ndarray,
    R1: float, R2: float,
    A: float, B: float,
    lam1: float, lam2: float, lam3: float,
    c: float, d: float,
    n1: float, gamma: float, h: float,
) -> float:
    """Compute Tersoff inter-atomic potential energy.

    Parameters
    ----------
    x : np.ndarray
        Flat coordinate vector of length ``3 * n_atoms``.
    R1, R2 : float
        Cutoff function parameters (centre and half-width).
    A, B : float
        Repulsive / attractive pre-exponential factors.
    lam1, lam2, lam3 : float
        Exponential decay constants.
    c, d : float
        Angular function parameters.
    n1 : float
        Bond-order exponent.
    gamma : float
        Bond-order prefactor.
    h : float
        Angular function equilibrium cosine.

    Returns
    -------
    float
        Total Tersoff potential energy.

    Notes
    -----
    The cosine-of-angle calculation uses ``rd3**3`` (cubed, not squared)
    and the three-body exponential uses ``lam3**3``.  These match the
    the reference ``bench_func.m`` source exactly and must NOT be "corrected".

    Complexity
    ----------
    The three-body bond-order accumulation is **O(NP^3)** in the number
    of atoms (triple loop ``i, j, k``).  For F5 and F6 the inputs are
    fixed at ``NP = 10`` atoms (``len(x) == 30``), so this is bounded at
    ~1000 inner-loop iterations per call -- fast enough that it does not
    show up in profiles, but the cubic scaling means a future caller
    that increases ``NP`` will see super-linear cost growth.  Stay
    inside the published bounds ([0, 5] in 30 dims) and do **not** use
    this function as a generic Tersoff calculator -- it is a benchmark
    *problem* tied to a specific atom count, not a physics library.
    """
    NP = len(x) // 3
    atoms = x.reshape(NP, 3)

    # --- Pairwise distances (vectorised) ---
    diff = atoms[:, None, :] - atoms[None, :, :]   # (NP, NP, 3)
    r = np.sqrt(np.sum(diff * diff, axis=2))        # (NP, NP)

    # --- Cutoff function (vectorised) ---
    fcr = np.where(
        r < (R1 - R2), 1.0,
        np.where(
            r > (R1 + R2), 0.0,
            0.5 - 0.5 * np.sin(np.pi / 2.0 * (r - R1) / R2),
        ),
    )

    # --- Repulsive / attractive pair terms ---
    VRr = A * np.exp(-lam1 * r)
    VAr = B * np.exp(-lam2 * r)

    # --- Three-body bond-order and energy accumulation ---
    if _tersoff_inner_nb is not None:
        return float(_tersoff_inner_nb(
            atoms, r, fcr, VRr, VAr,
            lam3, c, d, n1, gamma, h, NP,
        ))

    # Pure-Python fallback (suppress overflow/invalid warnings).
    E = np.zeros(NP)
    with np.errstate(over="ignore", invalid="ignore"):
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
                    # NOTE: rd3**3 (cubed!) matches reference bench_func.m exactly.
                    denom = 2.0 * rd1 * rd2
                    if abs(denom) < 1e-30:
                        continue  # degenerate geometry — skip
                    ctheta = (rd1 ** 2 + rd2 ** 2 - rd3 ** 3) / denom
                    G = (1.0 + c ** 2 / d ** 2
                         - c ** 2 / (d ** 2 + (h - ctheta) ** 2))
                    # NOTE: lam3**3 matches reference bench_func.m exactly.
                    zeta += fcr[i, kk] * G * np.exp(
                        lam3 ** 3 * (r[i, j] - r[i, kk]) ** 3
                    )

                gn = gamma * zeta
                abs_gn = abs(gn)
                if abs_gn < 1e-30:
                    Bij = 1.0
                elif n1 * np.log(abs_gn) > 700.0:
                    Bij = 0.0
                else:
                    Bij = (1.0 + abs_gn ** n1) ** (-0.5 / n1)

                E[i] += fcr[i, j] * (VRr[i, j] - Bij * VAr[i, j]) / 2.0

    return float(np.sum(E))


# ---------------------------------------------------------------------------
# F5: Tersoff Potential Si(B)
# ---------------------------------------------------------------------------

def f05_tersoff_sib(x: np.ndarray) -> float:
    """F5: Tersoff potential for model Si(B).

    Parameters
    ----------
    x : np.ndarray
        Decision vector of length 30 (10 atoms x 3 coordinates).
        Bounds are dimension-dependent; see ``define_boundaries.m``.

    Returns
    -------
    float
        Total Tersoff potential energy for the Si(B) parameter set.
    """
    return _tersoff_potential(
        x,
        R1=3.0, R2=0.2,
        A=3.2647e3, B=9.5373e1,
        lam1=3.2394, lam2=1.3258, lam3=1.3258,
        c=4.8381, d=2.0417,
        n1=22.956, gamma=0.33675, h=0.0,
    )


# ---------------------------------------------------------------------------
# F6: Tersoff Potential Si(C)
# ---------------------------------------------------------------------------

def f06_tersoff_sic(x: np.ndarray) -> float:
    """F6: Tersoff potential for model Si(C).

    Parameters
    ----------
    x : np.ndarray
        Decision vector of length 30 (10 atoms x 3 coordinates).
        Bounds are dimension-dependent; see ``define_boundaries.m``.

    Returns
    -------
    float
        Total Tersoff potential energy for the Si(C) parameter set.
    """
    return _tersoff_potential(
        x,
        R1=2.85, R2=0.15,
        A=1.8308e3, B=4.7118e2,
        lam1=2.4799, lam2=1.7322, lam3=1.7322,
        c=1.0039e5, d=1.6218e1,
        n1=7.8734e-1, gamma=1.0999e-6, h=-5.9826e-1,
    )


# ---------------------------------------------------------------------------
# F7: Spread Spectrum Radar Polyphase Code Design
# ---------------------------------------------------------------------------

def f07_spread_spectrum(x: np.ndarray) -> float:
    """F7: Spread spectrum radar polyphase code design.

    Parameters
    ----------
    x : np.ndarray
        Decision vector of length up to 20.  Bounds: [0, 2*pi].

    Returns
    -------
    float
        Maximum sidelobe level of the aperiodic autocorrelation function.

    Notes
    -----
    Translated from a triple-nested loop in ``bench_func.m`` (case 7).
    The outer loop iterates over odd and even indices of the
    autocorrelation vector ``hsum`` of length ``2*(2D-1)``, and the
    objective is ``max(hsum)``.
    """
    d = len(x)

    if _spread_spectrum_nb is not None:
        return float(_spread_spectrum_nb(x, d))

    # Pure-Python fallback
    var = 2 * d - 1
    hsum = np.zeros(2 * var)

    for kk in range(1, 2 * var + 1):  # 1-based index matching the reference
        if kk % 2 != 0:  # odd
            i = (kk + 1) // 2
            s = 0.0
            for j in range(i, d + 1):  # j = i .. d (1-based)
                summ = 0.0
                for i1 in range(abs(2 * i - j - 1) + 1, j + 1):  # 1-based
                    summ += x[i1 - 1]  # convert to 0-based
                s += np.cos(summ)
            hsum[kk - 1] = s
        else:  # even
            i = kk // 2
            s = 0.0
            for j in range(i + 1, d + 1):  # j = i+1 .. d (1-based)
                summ = 0.0
                for i1 in range(abs(2 * i - j) + 1, j + 1):  # 1-based
                    summ += x[i1 - 1]
                s += np.cos(summ)
            hsum[kk - 1] = s + 0.5

    return float(np.max(hsum))


# ---------------------------------------------------------------------------
# F8: Transmission Network Expansion Planning (TNEP)
# ---------------------------------------------------------------------------

# 6-bus system data from data6Bus.m
# Columns: [No, from, to, X, num_line, Pijmax, cost, overloads]
_LINEDATA_BASE = np.array([
    [1, 1, 2, 0.4,  1, 1.0,  np.inf, 1],
    [2, 1, 4, 0.6,  1, 0.8,  np.inf, 0],
    [3, 1, 5, 0.2,  1, 1.0,  np.inf, 0],
    [4, 2, 3, 0.2,  1, 1.0,  np.inf, 0],
    [5, 2, 4, 0.4,  1, 1.0,  np.inf, 1],
    [6, 3, 5, 0.2,  1, 1.0,  20.0,   1],
    [7, 6, 2, 0.3,  1, 1.0,  30.0,   1],
], dtype=np.float64)
_LINEDATA_BASE.flags.writeable = False

_CANDIDATE = np.array([
    [ 1, 1, 2, 0.40, 1, 1.00, 40, 1],
    [ 2, 1, 3, 0.38, 1, 1.00, 38, 1],
    [ 3, 1, 4, 0.60, 1, 0.80, 60, 0],
    [ 4, 1, 5, 0.20, 1, 1.00, 20, 0],
    [ 5, 1, 6, 0.68, 1, 0.70, 68, 0],
    [ 6, 2, 3, 0.20, 1, 1.00, 20, 0],
    [ 7, 2, 4, 0.40, 1, 1.00, 40, 1],
    [ 8, 2, 5, 0.31, 1, 1.00, 31, 1],
    [ 9, 6, 2, 0.30, 1, 1.00, 30, 1],
    [10, 3, 4, 0.69, 1, 0.82, 59, 1],
    [11, 3, 5, 0.20, 1, 1.00, 20, 1],
    [12, 6, 3, 0.48, 0, 1.00, 48, 0],
    [13, 4, 5, 0.63, 0, 0.75, 63, 0],
    [14, 4, 6, 0.30, 0, 1.00, 30, 0],
    [15, 5, 6, 0.61, 0, 0.78, 61, 0],
], dtype=np.float64)
_CANDIDATE.flags.writeable = False

_PGEN = np.array([0.5, 0.0, 1.65, 0.0, 0.0, 5.45], dtype=np.float64)
_PGEN.flags.writeable = False
_PLOAD = np.array([0.8, 2.4, 0.4, 1.6, 2.4, 0.0], dtype=np.float64)
_PLOAD.flags.writeable = False

# Audit quick-win (CEC2011 F8): memoization table for ``f08_tnep``.
#
# Key insight: the objective is a *deterministic function of
# sw = clip(ceil(x), 1, 15) ONLY* — the real-valued inputs enter the
# computation exclusively through that integer quantisation, so any two
# real vectors with the same ceil produce bit-identical outputs.
# Empirical proof (re-verified 2026-07-17 in this session, and previously
# by the performance audit): 1000 random pairs (x1, x2) with x1 uniform in
# [0, 15]^7 and x2 = ceil(x1) - u, u ~ U(1e-9, 1-1e-9) — i.e. different
# reals, same ceil — gave 0 bitwise mismatches in f08(x1) vs f08(x2), and
# repeat evaluations of the same x were bit-identical (the computation has
# no RNG, no adaptive solver; only ``np.linalg.inv`` of a matrix built
# purely from sw-selected table rows).
#
# The dict is bounded: the reachable key space is 15^7 (~1.7e8) but a
# 150k-NFE run touches only a tiny, heavily-repeated subset.  Once the cap
# is hit we simply stop inserting (no eviction) — lookups of cached keys
# stay O(1) and uncached keys fall through to the full computation, which
# is always bit-identical to the cached value anyway.
_F08_MEMO: dict[bytes, float] = {}
_F08_MEMO_MAX = 65536  # 56-byte keys + float values → a few MB worst case


def f08_tnep(x: np.ndarray) -> float:
    """F8: Transmission Network Expansion Planning (6-bus system).

    Selects candidate transmission lines (indexed by ``ceil(x)``) to add
    to a base network, then evaluates investment cost plus constraint
    violation penalties via DC power flow.

    Parameters
    ----------
    x : np.ndarray
        Decision vector of length 7.  Bounds: [0, 15].  Each element
        is ceiled to an integer index into the candidate line table.

    Returns
    -------
    float
        Total cost = investment cost of added lines + 30 + penalties
        for line overloads and duplicate candidate selections.
    """
    sw = np.ceil(x).astype(int)
    # Clamp indices to valid candidate range [1, 15]
    sw = np.clip(sw, 1, len(_CANDIDATE))

    # Memo lookup — the result depends on ``sw`` only (see _F08_MEMO above
    # for the key insight + empirical bit-identity proof).  The cached
    # float is returned verbatim, so hits are bitwise indistinguishable
    # from recomputation.
    memo_key = sw.tobytes()
    cached = _F08_MEMO.get(memo_key)
    if cached is not None:
        return cached

    n1_orig = len(_LINEDATA_BASE)

    # Build augmented line data: base lines + selected candidates
    # Reference: Linedata(n1+k,:) = Candidate(sw1(k),:)
    # Audit LOW (CEC2011): replace per-element list comprehension with a
    # single fancy-index lookup -- NumPy already handles ``int`` arrays as
    # row selectors, so the list-comp is pure overhead.
    selected = _CANDIDATE[sw - 1]
    Linedata = np.vstack([_LINEDATA_BASE, selected])

    n = len(_PGEN)  # 6 buses
    B = np.zeros((n, n))
    Nline = len(Linedata)
    Xline = Linedata[:, 3]  # reactance column (0-based col 3)

    for C in range(Nline):
        bline = 1.0 / Xline[C]
        k_bus = int(Linedata[C, 1]) - 1  # convert to 0-based
        m_bus = int(Linedata[C, 2]) - 1
        B[k_bus, m_bus] -= bline
        B[m_bus, k_bus] = B[k_bus, m_bus]
        B[k_bus, k_bus] += bline
        B[m_bus, m_bus] += bline

    # Reference: B(1,1) = 10000000  (make bus 1 the reference / slack bus)
    B[0, 0] = 10000000.0
    try:
        X = np.linalg.inv(B)
    except np.linalg.LinAlgError:
        # Singular network → large penalty (CRIT-07).  Also a pure
        # function of ``sw`` (B is built solely from sw-selected rows),
        # so it is memoised like the regular result.
        if len(_F08_MEMO) < _F08_MEMO_MAX:
            _F08_MEMO[memo_key] = NAN_PENALTY
        return NAN_PENALTY
    delP = _PGEN - _PLOAD
    delta = X @ delP

    # Compute line power flows
    pij = np.zeros(Nline)
    for k in range(Nline):
        i_bus = int(Linedata[k, 1]) - 1
        j_bus = int(Linedata[k, 2]) - 1
        pij[k] = (delta[i_bus] - delta[j_bus]) / Xline[k]

    # Investment cost: sum of costs of added lines + 30
    f = float(np.sum(Linedata[n1_orig:, 6])) + 30.0

    # Penalty for line overloads
    pen = 0.0
    for i in range(Nline):
        overload = abs(pij[i]) - Linedata[i, 5]
        if overload > 0.0:
            pen += 5000.0 * overload

    # Penalty for selecting the same candidate line more than 3 times
    for i in range(1, len(_CANDIDATE) + 1):
        count = int(np.sum(sw == i))
        if count > 3:
            pen += 1000.0

    result = float(f + pen)
    if len(_F08_MEMO) < _F08_MEMO_MAX:
        _F08_MEMO[memo_key] = result
    return result
