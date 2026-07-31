"""CEC2011 entry point — unified interface for all 22 real-world benchmark problems.

Usage::

    from benchmarks.cec_suite_python.cec2011 import cec2011_func

    x = np.random.uniform(0, 1, (50, 6))
    fitness = cec2011_func(x, 1)           # F1: returns (50,) array
    fitness = cec2011_func(1, x)           # same — auto-detects argument order
    fitness = cec2011_func(x[0], 1)        # single solution -> scalar

Function structure (22 real-world problems):
  F1:      Parameter Estimation for FM Sound Waves (D=6)
  F2:      Lennard-Jones Potential (D=30)
  F3:      Bifunctional Catalyst Blend Control (D=1)
  F4:      Stirred Tank Reactor Control (D=1)
  F5-F6:   Tersoff Potential (D=30)
  F7:      Spread Spectrum Radar Polyphase (D=20)
  F8:      Transmission Network Expansion Planning (D=7)
  F9:      Large Scale Energy Brokerage (D=126)
  F10:     Circular Antenna Array Design (D=12)
  F11-F12: Dynamic Economic Load Dispatch (D=120, D=240)
  F13-F17: Static Economic Load Dispatch (D=6..140)
  F18-F20: Hydrothermal Scheduling (D=96)
  F21:     Messenger Spacecraft Trajectory (D=26)
  F22:     Cassini-Huygens Spacecraft Trajectory (D=22)

Optimal values: f*(F_i) = 0.0 for all functions (real-world, no known bias).
Search domains: variable per function (see ``cec2011_bounds``).

Note: CEC2011 problems are NOT vectorizable — the dispatcher loops over rows
and evaluates each solution individually.

Special handling:
  Objective NaN results are converted to 0.0, matching the original
  reference wrapper behaviour.
"""

from __future__ import annotations

import math

import numpy as np

from .problems_antenna import f10_antenna_array
from .problems_basic import (
    f01_fm_sound,
    f02_lennard_jones,
    f03_bifunctional_catalyst as f03_catalyst_blend,
    f04_stirred_tank,
    f05_tersoff_sib as f05_tersoff_si_b,
    f06_tersoff_sic as f06_tersoff_si_c,
    f07_spread_spectrum as f07_radar_polyphase,
    f08_tnep as f08_transmission_network,
)
from .problems_hydrothermal import (
    f18_hydrothermal_case1,
    f19_hydrothermal_case2,
    f20_hydrothermal_case3,
)
from .problems_power import (
    f09_energy_brokerage,
    f11_dynamic_eld_5unit,
    f12_dynamic_eld_10unit,
    f13_static_eld_6unit,
    f14_static_eld_13unit,
    f15_static_eld_15unit,
    f16_static_eld_40unit,
    f17_static_eld_140unit,
)
from .problems_spacecraft import (
    f21_messenger,
    f22_cassini_huygens,
)

__all__ = [
    "NUM_FUNCTIONS",
    "all_functions",
    "cec2011_func",
    "cec2011_bounds",
    "cec2011_fname",
    "cec2011_fopt",
    "cec2011_dim",
]

NUM_FUNCTIONS = 22

all_functions: tuple = (
    f01_fm_sound,
    f02_lennard_jones,
    f03_catalyst_blend,
    f04_stirred_tank,
    f05_tersoff_si_b,
    f06_tersoff_si_c,
    f07_radar_polyphase,
    f08_transmission_network,
    f09_energy_brokerage,
    f10_antenna_array,
    f11_dynamic_eld_5unit,
    f12_dynamic_eld_10unit,
    f13_static_eld_6unit,
    f14_static_eld_13unit,
    f15_static_eld_15unit,
    f16_static_eld_40unit,
    f17_static_eld_140unit,
    f18_hydrothermal_case1,
    f19_hydrothermal_case2,
    f20_hydrothermal_case3,
    f21_messenger,
    f22_cassini_huygens,
)

# --------------------------------------------------------------------------- #
#   Function metadata
# --------------------------------------------------------------------------- #

_FUNCTION_NAMES: list[str] = [
    "Parameter Estimation for FM Sound Waves",   # F1
    "Lennard-Jones Potential",                    # F2
    "Bifunctional Catalyst Blend Control",        # F3
    "Stirred Tank Reactor Control",               # F4
    "Tersoff Potential Si(B)",                    # F5
    "Tersoff Potential Si(C)",                    # F6
    "Spread Spectrum Radar Polyphase",            # F7
    "Transmission Network Expansion Planning",    # F8
    "Large Scale Energy Brokerage",               # F9
    "Circular Antenna Array Design",              # F10
    "Dynamic ELD 5-Unit 24h",                     # F11
    "Dynamic ELD 10-Unit 24h",                    # F12
    "Static ELD 6-Unit",                          # F13
    "Static ELD 13-Unit",                         # F14
    "Static ELD 15-Unit",                         # F15
    "Static ELD 40-Unit",                         # F16
    "Static ELD 140-Unit",                        # F17
    "Hydrothermal Scheduling Case 1",             # F18
    "Hydrothermal Scheduling Case 2",             # F19
    "Hydrothermal Scheduling Case 3",             # F20
    "Messenger Spacecraft Trajectory",            # F21
    "Cassini-Huygens Spacecraft Trajectory",      # F22
]

_FUNCTION_DIMS: list[int] = [
    6,    # F1
    30,   # F2
    1,    # F3
    1,    # F4
    30,   # F5
    30,   # F6
    20,   # F7
    7,    # F8
    126,  # F9
    12,   # F10
    120,  # F11
    240,  # F12
    6,    # F13
    13,   # F14
    15,   # F15
    40,   # F16
    140,  # F17
    96,   # F18
    96,   # F19
    96,   # F20
    26,   # F21
    22,   # F22
]

# The CEC2011 reference wrapper maps objective NaN to zero for every problem.
_NAN_TO_ZERO_FUNCS = frozenset(range(1, 23))

# --------------------------------------------------------------------------- #
#   Bounds data
# --------------------------------------------------------------------------- #

# F17: 140-unit static ELD bounds from reference data
_F17_BOUNDS = np.array([
    [71, 119], [120, 189], [125, 190], [125, 190], [90, 190], [90, 190],
    [280, 490], [280, 490], [260, 496], [260, 496], [260, 496], [260, 496],
    [260, 506], [260, 509], [260, 506], [260, 505], [260, 506], [260, 506],
    [260, 505], [260, 505], [260, 505], [260, 505], [260, 505], [260, 505],
    [280, 537], [280, 537], [280, 549], [280, 549], [260, 501], [260, 501],
    [260, 506], [260, 506], [260, 506], [260, 506], [260, 500], [260, 500],
    [120, 241], [120, 241], [423, 774], [423, 769], [3, 19], [3, 28],
    [160, 250], [160, 250], [160, 250], [160, 250], [160, 250], [160, 250],
    [160, 250], [160, 250], [165, 504], [165, 504], [165, 504], [165, 504],
    [180, 471], [180, 561], [103, 341], [198, 617], [100, 312], [153, 471],
    [163, 500], [95, 302], [160, 511], [160, 511], [196, 490], [196, 490],
    [196, 490], [196, 490], [130, 432], [130, 432], [137, 455], [137, 455],
    [195, 541], [175, 536], [175, 540], [175, 538], [175, 540], [330, 574],
    [160, 531], [160, 531], [200, 542], [56, 132], [115, 245], [115, 245],
    [115, 245], [207, 307], [207, 307], [175, 345], [175, 345], [175, 345],
    [175, 345], [360, 580], [415, 645], [795, 984], [795, 978], [578, 682],
    [615, 720], [612, 718], [612, 720], [758, 964], [755, 958], [750, 1007],
    [750, 1006], [713, 1013], [718, 1020], [791, 954], [786, 952], [795, 1006],
    [795, 1013], [795, 1021], [795, 1015], [94, 203], [94, 203], [94, 203],
    [244, 379], [244, 379], [244, 379], [95, 190], [95, 189], [116, 194],
    [175, 321], [2, 19], [4, 59], [15, 83], [9, 53], [12, 37], [10, 34],
    [112, 373], [4, 20], [5, 38], [5, 19], [50, 98], [5, 10], [42, 74],
    [42, 74], [41, 105], [17, 51], [7, 19], [7, 19], [26, 40],
], dtype=np.float64)


def _compute_f09_bounds() -> tuple[np.ndarray, np.ndarray]:
    """Compute IEEE 30-bus energy brokerage bounds (D=126).

    Derives variable bounds from generator capacities and load demands
    in the IEEE 30-bus system, minus bilateral transaction commitments.

    Returns
    -------
    xmin : ndarray, shape (126,)
        Lower bounds (all zeros).
    xmax : ndarray, shape (126,)
        Upper bounds per poolco transaction variable.
    """
    Pg_raw = np.array([
        165.9, 49.1, 0, 0, 21.6, 0, 0, 22.8, 0, 0,
        12.4, 0, 11.6, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    ]) / 100.0
    Pd_raw = np.array([
        0, 21.7, 2.4, 7.6, 94.2, 0, 22.8, 30.0, 0, 5.8,
        0, 11.2, 0, 6.2, 8.2, 3.5, 9.0, 3.2, 9.5, 2.2,
        17.5, 0, 3.2, 8.7, 0, 3.5, 0, 0, 2.4, 10.6,
    ]) / 100.0

    Pg = Pg_raw[Pg_raw > 0]   # 6 generators
    Pd = Pd_raw[Pd_raw > 0]   # 21 loads

    # Bilateral transaction matrix (6 generators x 21 loads)
    BT = np.zeros((6, 21))
    BT[0, 3] = 5.0
    BT[0, 4] = 10.0
    BT[0, 5] = 5.0
    BT[1, 2] = 5.0
    BT[2, 20] = 2.5
    BT[3, 20] = 2.5
    BT[3, 15] = 15.0
    BT[4, 11] = 2.5
    BT[5, 7] = 2.5
    BT /= 100.0

    xmin = np.zeros(126)
    xmax = np.zeros(126)
    c = 0
    for i in range(6):
        for j in range(21):
            xmax[c] = min(Pg[i] - BT[i, j], Pd[j] - BT[i, j])
            c += 1
    return xmin, xmax


# Pre-compute F9 bounds at import time
_F09_XMIN, _F09_XMAX = _compute_f09_bounds()
_F09_XMIN.flags.writeable = False
_F09_XMAX.flags.writeable = False


def _build_bounds(func_id: int) -> tuple[np.ndarray, np.ndarray]:
    """Build (xmin, xmax) arrays for a given problem.

    Parameters
    ----------
    func_id : int
        Function number, 1-22.

    Returns
    -------
    xmin : ndarray, shape (D,)
        Lower bounds.
    xmax : ndarray, shape (D,)
        Upper bounds.
    """
    if func_id == 1:
        # D=6, [-6.4, 6.35]
        D = 6
        return np.full(D, -6.4), np.full(D, 6.35)

    if func_id in (2, 5, 6):
        # D=30, mixed bounds for Lennard-Jones / Tersoff
        D = 30
        xmin = np.zeros(D)
        xmax = np.zeros(D)
        # j=0,1 (reference j=1,2): [0, 4]
        xmin[0] = 0.0
        xmax[0] = 4.0
        xmin[1] = 0.0
        xmax[1] = 4.0
        # j=2 (reference j=3): [0, pi]
        xmin[2] = 0.0
        xmax[2] = math.pi
        # j>=3 (reference j>=4): [-4-floor((j-4)/3)/4, 4+floor((j-4)/3)/4]
        # Reference uses 1-based j, so j_ref = j_python + 1
        for j in range(3, D):
            j_ref = j + 1
            offset = math.floor((j_ref - 4) / 3) / 4.0
            xmin[j] = -4.0 - offset
            xmax[j] = 4.0 + offset
        return xmin, xmax

    if func_id == 3:
        # D=1, [0.6, 0.9]
        return np.array([0.6]), np.array([0.9])

    if func_id == 4:
        # D=1, [0, 5]
        return np.array([0.0]), np.array([5.0])

    if func_id == 7:
        # D=20, [0, 2*pi]
        D = 20
        return np.zeros(D), np.full(D, 2.0 * math.pi)

    if func_id == 8:
        # D=7, [0, 15]
        D = 7
        return np.zeros(D), np.full(D, 15.0)

    if func_id == 9:
        # D=126, dynamic bounds from IEEE 30-bus data
        return _F09_XMIN.copy(), _F09_XMAX.copy()

    if func_id == 10:
        # D=12, j<=6: [0.2, 1.0], j>6: [-180, 180]
        # (0-indexed: j<6 -> [0.2,1.0], j>=6 -> [-180,180])
        D = 12
        xmin = np.empty(D)
        xmax = np.empty(D)
        xmin[:6] = 0.2
        xmax[:6] = 1.0
        xmin[6:] = -180.0
        xmax[6:] = 180.0
        return xmin, xmax

    if func_id == 11:
        # D=120, 5 units x 24h
        Pmin = np.array([10.0, 20.0, 30.0, 40.0, 50.0])
        Pmax = np.array([75.0, 125.0, 175.0, 250.0, 300.0])
        xmin = np.tile(Pmin, 24)
        xmax = np.tile(Pmax, 24)
        return xmin, xmax

    if func_id == 12:
        # D=240, 10 units x 24h
        Pmin = np.array([150.0, 135.0, 73.0, 60.0, 73.0,
                         57.0, 20.0, 47.0, 20.0, 55.0])
        Pmax = np.array([470.0, 460.0, 340.0, 300.0, 243.0,
                         160.0, 130.0, 120.0, 80.0, 55.0])
        xmin = np.tile(Pmin, 24)
        xmax = np.tile(Pmax, 24)
        return xmin, xmax

    if func_id == 13:
        # D=6
        bounds = np.array([
            [100, 500], [50, 200], [80, 300],
            [50, 150], [50, 200], [50, 120],
        ], dtype=np.float64)
        return bounds[:, 0].copy(), bounds[:, 1].copy()

    if func_id == 14:
        # D=13
        bounds = np.array([
            [0, 680], [0, 360], [0, 360], [60, 180], [60, 180],
            [60, 180], [60, 180], [60, 180], [60, 180],
            [40, 120], [40, 120], [55, 120], [55, 120],
        ], dtype=np.float64)
        return bounds[:, 0].copy(), bounds[:, 1].copy()

    if func_id == 15:
        # D=15
        bounds = np.array([
            [150, 455], [150, 455], [20, 130], [20, 130], [150, 470],
            [135, 460], [135, 465], [60, 300], [25, 162], [25, 160],
            [20, 80], [20, 80], [25, 85], [15, 55], [15, 55],
        ], dtype=np.float64)
        return bounds[:, 0].copy(), bounds[:, 1].copy()

    if func_id == 16:
        # D=40
        bounds = np.array([
            [36, 114], [36, 114], [60, 120], [80, 190], [47, 97],
            [68, 140], [110, 300], [135, 300], [135, 300], [130, 300],
            [94, 375], [94, 375], [125, 500], [125, 500], [125, 500],
            [125, 500], [220, 500], [220, 500], [242, 550], [242, 550],
            [254, 550], [254, 550], [254, 550], [254, 550], [254, 550],
            [254, 550], [10, 150], [10, 150], [10, 150], [47, 97],
            [60, 190], [60, 190], [60, 190], [90, 200], [90, 200],
            [90, 200], [25, 110], [25, 110], [25, 110], [242, 550],
        ], dtype=np.float64)
        return bounds[:, 0].copy(), bounds[:, 1].copy()

    if func_id == 17:
        # D=140
        return _F17_BOUNDS[:, 0].copy(), _F17_BOUNDS[:, 1].copy()

    if func_id in (18, 19, 20):
        # D=96, 4 reservoirs x 24h
        Qmin = np.array([5.0, 6.0, 10.0, 13.0])
        Qmax = np.array([15.0, 15.0, 30.0, 25.0])
        xmin = np.tile(Qmin, 24)
        xmax = np.tile(Qmax, 24)
        return xmin, xmax

    if func_id == 21:
        # D=26, Messenger spacecraft trajectory
        xmin = np.array([
            1900.0, 2.5, 0.0, 0.0, 100.0, 100.0, 100.0, 100.0, 100.0,
            100.0, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 1.1, 1.1,
            1.05, 1.05, 1.05, -math.pi, -math.pi, -math.pi, -math.pi,
            -math.pi,
        ])
        xmax = np.array([
            2300.0, 4.05, 1.0, 1.0, 500.0, 500.0, 500.0, 500.0, 500.0,
            600.0, 0.99, 0.99, 0.99, 0.99, 0.99, 0.99, 6.0, 6.0,
            6.0, 6.0, 6.0, math.pi, math.pi, math.pi, math.pi,
            math.pi,
        ])
        return xmin, xmax

    if func_id == 22:
        # D=22, Cassini-Huygens spacecraft trajectory
        xmin = np.array([
            -1000.0, 3.0, 0.0, 0.0, 100.0, 100.0, 30.0, 400.0, 400.0,
            0.01, 0.01, 0.01, 0.01, 0.01, 1.05, 1.05, 1.15, 1.7,
            -math.pi, -math.pi, -math.pi, -math.pi,
        ])
        xmax = np.array([
            0.0, 5.0, 1.0, 1.0, 400.0, 500.0, 300.0, 1600.0, 2200.0,
            0.9, 0.9, 0.9, 0.9, 0.9, 6.0, 6.0, 6.5, 291.0,
            math.pi, math.pi, math.pi, math.pi,
        ])
        return xmin, xmax

    raise ValueError(f"func_id must be 1-{NUM_FUNCTIONS}, got {func_id}")


# --------------------------------------------------------------------------- #
#   Public API
# --------------------------------------------------------------------------- #

def cec2011_func(arg1: object, arg2: object = None) -> np.ndarray | float:
    """Evaluate CEC2011 real-world benchmark problem.

    Supports both argument orders:
      cec2011_func(x, func_id)  -- population matrix first
      cec2011_func(func_id, x)  -- function ID first

    CEC2011 problems are NOT vectorizable, so this dispatcher loops over
    rows and evaluates each solution individually.  NaN results from
    F5/F6 (Tersoff potential) are converted to 0.0 to match the reference.

    Parameters
    ----------
    arg1 : int or array_like
        Either a function ID (1-22) or a population array.
    arg2 : int or array_like
        The other argument (whichever ``arg1`` is not).

    Returns
    -------
    f : ndarray, shape (M,) or float
        Fitness values.  Scalar for single-solution input.
    """
    if arg2 is None:
        raise TypeError("cec2011_func requires two arguments: x and func_id")

    # Both scalars -> neither is a population
    if np.isscalar(arg1) and np.isscalar(arg2):
        raise ValueError("One argument must be a population array")

    # Auto-detect argument order.
    #
    # Audit H-1: use ``np.ascontiguousarray`` (not ``np.asarray``) on the
    # population so every downstream kernel receives a C-contiguous
    # ``float64`` view.  CEC2011 is dominated by Python-level per-row
    # problem solvers (orbital mechanics, ED, RK45) where layout matters
    # less than on CEC2017/LSGO, but we standardise across all four
    # dispatchers so callers see a single documented contract.
    if isinstance(arg1, (int, np.integer)):
        func_id, x = int(arg1), np.ascontiguousarray(arg2, dtype=np.float64)
    elif isinstance(arg2, (int, np.integer)):
        x, func_id = np.ascontiguousarray(arg1, dtype=np.float64), int(arg2)
    else:
        # Both arrays -- assume (x, func_id) where func_id might be array-like
        x = np.ascontiguousarray(arg1, dtype=np.float64)
        func_id_raw = np.asarray(arg2).flat[0]
        func_id = int(func_id_raw)
        if func_id != float(func_id_raw):
            raise ValueError(
                f"func_id must be integer-valued, got {func_id_raw}"
            )

    if func_id < 1 or func_id > NUM_FUNCTIONS:
        raise ValueError(
            f"func_id must be 1-{NUM_FUNCTIONS}, got {func_id}"
        )

    # Handle 1-D input
    scalar_input = x.ndim == 1
    if scalar_input:
        x = x.reshape(1, -1)

    if x.ndim != 2:
        raise ValueError(f"x must be 1-D or 2-D, got {x.ndim}-D")

    # Audit AUDIT-21: reject empty populations before entering the
    # per-row evaluation loop.  An M=0 population is never valid --
    # every upstream caller guarantees M >= 1, so this is a defensive
    # guard against silent shape propagation bugs.
    if x.shape[0] == 0:
        raise ValueError("cec2011_func: empty population (M=0)")

    # Audit AUDIT-01: reject non-finite inputs at the dispatcher so
    # NaN / Inf never reaches the per-row Python-level evaluators
    # (orbital mechanics, ED, RK45, etc.).  Matches the existing
    # CEC2017 / CEC2013 dispatcher guard (audit CEC2017-L1).
    if not np.all(np.isfinite(x)):
        bad = int(np.sum(~np.isfinite(x)))
        raise ValueError(
            f"cec2011_func(F{func_id}): input contains {bad} non-finite "
            f"entries (NaN / +Inf / -Inf).  This would silently poison "
            f"Friedman / Wilcoxon / mean aggregation downstream -- reject "
            f"the upstream sampler instead."
        )

    M, D = x.shape
    expected_dim = _FUNCTION_DIMS[func_id - 1]
    if D != expected_dim:
        raise ValueError(
            f"F{func_id} requires D={expected_dim}, got D={D}"
        )

    evaluator = all_functions[func_id - 1]
    nan_to_zero = func_id in _NAN_TO_ZERO_FUNCS

    # CEC2011 problems are NOT vectorizable — loop over rows.
    # Suppress overflow / invalid / divide warnings from real-world
    # functions (ODE stiffness, Tersoff exponents, antenna log10, etc.).
    f = np.empty(M, dtype=np.float64)
    with np.errstate(over="ignore", invalid="ignore", divide="ignore"):
        for i in range(M):
            val = evaluator(x[i])
            if nan_to_zero and np.isnan(val):
                val = 0.0
            f[i] = val

    if scalar_input:
        return float(f[0])
    return f


# Audit M-2: bounds are immutable per function id, so cache them once and
# freeze the arrays at first request.  ``_build_bounds`` contains several
# non-trivial paths (F2/5/6 offset arithmetic, F9 PTDF-derived bounds,
# F13-F22 parameter lookups) that were previously re-executed on every
# ``cec2011_bounds`` call — cheap in isolation, but the optimizer calls the
# getter inside its boundary-repair loop so the per-call allocation was
# showing up in F20/F21 profiles.  Using ``dict.get`` keeps the fast path
# lock-free without needing an ``__init__`` sentinel.  Freezing the arrays
# (``writeable=False``) also protects callers from accidentally mutating
# cached state — F9's PTDF-derived bounds in particular are expensive to
# rebuild.
_BOUNDS_CACHE: dict[int, tuple[np.ndarray, np.ndarray]] = {}


def cec2011_bounds(func_id: int) -> tuple[np.ndarray, np.ndarray]:
    """Return (xmin, xmax) bound arrays for function ``func_id``.

    Each CEC2011 problem has its own domain and dimensionality.  The
    returned arrays are **frozen** (``writeable=False``) — callers that
    need to mutate a copy should use ``arr.copy()`` explicitly.

    Parameters
    ----------
    func_id : int
        Function number, 1-22.

    Returns
    -------
    xmin : ndarray, shape (D,)
        Lower bounds (read-only).
    xmax : ndarray, shape (D,)
        Upper bounds (read-only).
    """
    if func_id < 1 or func_id > NUM_FUNCTIONS:
        raise ValueError(
            f"func_id must be 1-{NUM_FUNCTIONS}, got {func_id}"
        )
    cached = _BOUNDS_CACHE.get(func_id)
    if cached is not None:
        return cached
    xmin, xmax = _build_bounds(func_id)
    xmin.flags.writeable = False
    xmax.flags.writeable = False
    cached = (xmin, xmax)
    _BOUNDS_CACHE[func_id] = cached
    return cached


def cec2011_fname(func_id: int) -> str:
    """Return the human-readable name for function ``func_id``.

    Parameters
    ----------
    func_id : int
        Function number, 1-22.

    Returns
    -------
    name : str
        Problem name.
    """
    if func_id < 1 or func_id > NUM_FUNCTIONS:
        raise ValueError(
            f"func_id must be 1-{NUM_FUNCTIONS}, got {func_id}"
        )
    return _FUNCTION_NAMES[func_id - 1]


def cec2011_fopt(func_id: int) -> float:
    """Return the optimal (bias) value for function ``func_id``.

    All CEC2011 real-world problems return 0.0 since the true global
    optima are unknown.

    Parameters
    ----------
    func_id : int
        Function number, 1-22.

    Returns
    -------
    fopt : float
        Always 0.0.
    """
    if func_id < 1 or func_id > NUM_FUNCTIONS:
        raise ValueError(
            f"func_id must be 1-{NUM_FUNCTIONS}, got {func_id}"
        )
    return 0.0


def cec2011_dim(func_id: int) -> int:
    """Return the fixed dimensionality for function ``func_id``.

    Parameters
    ----------
    func_id : int
        Function number, 1-22.

    Returns
    -------
    dim : int
        Problem dimensionality.
    """
    if func_id < 1 or func_id > NUM_FUNCTIONS:
        raise ValueError(
            f"func_id must be 1-{NUM_FUNCTIONS}, got {func_id}"
        )
    return _FUNCTION_DIMS[func_id - 1]
