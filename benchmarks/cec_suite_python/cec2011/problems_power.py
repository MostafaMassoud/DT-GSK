"""CEC2011 power system problems: F9 (energy brokerage) and F11-F17 (ELD).

F9:  Large-Scale Energy Brokerage (IEEE 30-bus, D=126)
F11: Dynamic Economic Load Dispatch, 5-unit 24h  (D=120)
F12: Dynamic Economic Load Dispatch, 10-unit 24h (D=240)
F13: Static Economic Load Dispatch, 6-unit   (D=6)
F14: Static Economic Load Dispatch, 13-unit  (D=13)
F15: Static Economic Load Dispatch, 15-unit  (D=15)
F16: Static Economic Load Dispatch, 40-unit  (D=40)
F17: Static Economic Load Dispatch, 140-unit (D=140)

All data is embedded inline, matching the original CEC2011 reference sources.

Penalty formula convention
--------------------------
All ELD functions use the reference ``abs(a-b)-(a-b)`` pattern for penalty
computation, which equals ``2 * max(b-a, 0)``.  This is preserved verbatim
for benchmark fidelity rather than using the equivalent NumPy formulation.

Shared helpers: ``_capacity_penalty``, ``_ramp_penalty``, ``_poz_penalty``
factor out the common penalty patterns used by F13-F17.

Dynamic ELD (F11, F12) use Fortran-order reshape ``x.reshape((N, 24), order='F').T``
to match the reference column-major ``reshape(x, N, 24)'`` convention.  Consecutive elements in
``x`` cycle through units (not hours), matching the ``np.tile(Pmin, 24)`` bounds.

Known reference-source quirk (F17)
-----------------------------------
The reference ``fn_ELD_140.m`` has a missing ``sum()`` on the lower-bound capacity
penalty term, causing the upper-bound violation scalar to broadcast across all
140 units.  This Python port reproduces the bug for benchmark compatibility.
See ``f17_static_eld_140unit()`` for the explicit broadcast computation.

Reference
---------
Suganthan, P.N. et al., "Problem Definitions and Evaluation Criteria for the
CEC 2011 Special Session on Real-Parameter Optimization", 2011.

Reference source files
  fn_DED_5.m        (F11, dynamic 5-unit)
  fn_DED_10.m       (F12, dynamic 10-unit)
  fn_ELD_6.m        (F13, static 6-unit)
  fn_ELD_13.m       (F14, static 13-unit)
  fn_ELD_15.m       (F15, static 15-unit)
  fn_ELD_40.m       (F16, static 40-unit)
  fn_ELD_140.m      (F17, static 140-unit)
  fn_IEEE_30_bus.m  (F9, energy brokerage)
"""

from __future__ import annotations

import numpy as np

# =========================================================================== #
#  Shared helpers for Economic Load Dispatch problems
# =========================================================================== #


def _capacity_penalty(x: np.ndarray, Pmin: np.ndarray, Pmax: np.ndarray) -> float:
    """Capacity-limits penalty matching reference: sum(|x-Pmin|-(x-Pmin)) + sum(|Pmax-x|-(Pmax-x)).

    Equivalent to 2*sum(max(Pmin-x, 0)) + 2*sum(max(x-Pmax, 0)).

    Algebra (per generator i)
    -------------------------
    The reference ELD scripts express each one-sided ReLU using ``|a| - a``::

        |a| - a == 0          if a >= 0
        |a| - a == -2*a       if a < 0

    so for the lower bound (with a = x_i - Pmin_i)::

        |x_i - Pmin_i| - (x_i - Pmin_i)
            == 0                    if x_i >= Pmin_i
            == 2 * (Pmin_i - x_i)   if x_i <  Pmin_i
            == 2 * max(Pmin_i - x_i, 0)    -- one-sided ReLU x 2

    and symmetrically for the upper bound (with a = Pmax_i - x_i)::

        |Pmax_i - x_i| - (Pmax_i - x_i)
            == 2 * max(x_i - Pmax_i, 0)

    Summing over all generators yields the total capacity violation
    multiplied by 2 -- the factor-of-2 is intentional (it doubles the
    penalty weight relative to a plain ReLU sum) and matches the original
    reference source. **Do not** simplify away the ``|a| - a`` form: F17 in
    particular relies on the bug-compatible broadcast variant of this
    expression (see ``f17_static_eld_140unit``).

    Parameters
    ----------
    x : ndarray, shape (N,)
        Generator outputs.
    Pmin : ndarray, shape (N,)
        Minimum capacity limits.
    Pmax : ndarray, shape (N,)
        Maximum capacity limits.

    Returns
    -------
    penalty : float
        Total capacity violation (already multiplied by 2 from the
        ``|a| - a`` rewrite).
    """
    return float(
        np.sum(np.abs(x - Pmin) - (x - Pmin))
        + np.sum(np.abs(Pmax - x) - (Pmax - x))
    )


def _ramp_penalty(
    x: np.ndarray,
    down_ramp_limit: np.ndarray,
    up_ramp_limit: np.ndarray,
) -> float:
    """Ramp-rate penalty: same formula as capacity but with ramp-adjusted limits.

    Parameters
    ----------
    x : ndarray, shape (N,)
        Generator outputs.
    down_ramp_limit : ndarray, shape (N,)
        Lower ramp-adjusted limits.
    up_ramp_limit : ndarray, shape (N,)
        Upper ramp-adjusted limits.

    Returns
    -------
    penalty : float
        Total ramp-rate violation.
    """
    return float(
        np.sum(np.abs(x - down_ramp_limit) - (x - down_ramp_limit))
        + np.sum(np.abs(up_ramp_limit - x) - (up_ramp_limit - x))
    )


def _poz_penalty(
    x: np.ndarray,
    poz_lower: np.ndarray,
    poz_upper: np.ndarray,
) -> float:
    """Prohibited Operating Zone penalty.

    For each unit and each zone, if the output falls strictly inside
    [lower, upper], the penalty is min(x - lower, upper - x).

    Parameters
    ----------
    x : ndarray, shape (N,)
        Generator outputs.
    poz_lower : ndarray, shape (n_zones, N)
        Lower bounds of prohibited zones.
    poz_upper : ndarray, shape (n_zones, N)
        Upper bounds of prohibited zones.

    Returns
    -------
    penalty : float
        Total POZ violation.
    """
    n_zones = poz_lower.shape[0]
    pen = 0.0
    for z in range(n_zones):
        inside = (poz_lower[z] < x) & (x < poz_upper[z])
        if np.any(inside):
            pen += float(np.sum(
                np.minimum(x[inside] - poz_lower[z, inside],
                           poz_upper[z, inside] - x[inside])
            ))
    return pen


# =========================================================================== #
#  F9: Large-Scale Energy Brokerage (IEEE 30-bus)
#
#  Pre-computed constants: Ybus inversion, PTDF tensor, reference rates, and
#  bilateral transactions are all independent of the decision vector x.
#  Computing them once at module level eliminates ~25 ms per evaluation.
#
#  Audit M-3 note: do **not** lazify this block.  A typical CEC2011 run on
#  F9 performs 150_000 NFEs; moving the 25 ms PTDF build into the hot path
#  would cost ~3 750 s per run (at D=126 the inversion alone dominates),
#  while the eager build cost is a one-off ~50 ms charged to ``import
#  benchmarks.cec_suite_python.cec2011.problems_power`` — already warmed on the
#  worker-pool background thread (see ``gsk/experiment.py::_do_warmup``).
#  The audit originally flagged this block as worker-startup-tail latency;
#  the trade-off analysis says eager is correct by ~75 000×.
# =========================================================================== #

# IEEE 30-bus system data (MW / baseMVA=100)
_F09_bus_Pg = np.array([
    165.9, 49.1, 0, 0, 21.6, 0, 0, 22.8, 0, 0,
    12.4, 0, 11.6, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
]) / 100.0
_F09_bus_Pd = np.array([
    0, 21.7, 2.4, 7.6, 94.2, 0, 22.8, 30.0, 0, 5.8,
    0, 11.2, 0, 6.2, 8.2, 3.5, 9.0, 3.2, 9.5, 2.2,
    17.5, 0, 3.2, 8.7, 0, 3.5, 0, 0, 2.4, 10.6,
]) / 100.0

_F09_g_idx = np.where(_F09_bus_Pg > 0)[0]   # 6 generator buses
_F09_d_idx = np.where(_F09_bus_Pd > 0)[0]   # 21 load buses
_F09_Pg = _F09_bus_Pg[_F09_g_idx]
_F09_Pd = _F09_bus_Pd[_F09_d_idx]
_F09_ng = len(_F09_Pg)   # 6
_F09_nd = len(_F09_Pd)   # 21

# Bilateral Transaction (50 MW case)
_F09_BT = np.zeros((_F09_ng, _F09_nd))
_F09_BT[0, 3] = 5.0
_F09_BT[0, 4] = 10.0
_F09_BT[0, 5] = 5.0
_F09_BT[1, 2] = 5.0
_F09_BT[2, 20] = 2.5
_F09_BT[3, 20] = 2.5
_F09_BT[3, 15] = 15.0
_F09_BT[4, 11] = 2.5
_F09_BT[5, 7] = 2.5
_F09_BT /= 100.0

_F09_BT_row_sum = np.sum(_F09_BT, axis=1)   # (ng,)
_F09_BT_col_sum = np.sum(_F09_BT, axis=0)   # (nd,)

# IEEE 30-bus line data (41 lines)
_F09_na = np.array([
    1, 1, 2, 3, 2, 2, 4, 7, 6, 6,
    6, 6, 11, 9, 4, 13, 12, 12, 12, 14,
    16, 15, 18, 20, 10, 10, 10, 10, 22, 15,
    22, 23, 25, 25, 27, 28, 27, 27, 29, 8, 6,
])
_F09_nb = np.array([
    2, 3, 4, 4, 5, 6, 6, 5, 7, 8,
    9, 10, 9, 10, 12, 12, 14, 15, 16, 15,
    17, 18, 19, 19, 20, 17, 21, 22, 21, 23,
    24, 24, 24, 26, 25, 27, 29, 30, 30, 28, 28,
])
_F09_linedata_x = np.array([
    0.0575, 0.1652, 0.1737, 0.0379, 0.1983,
    0.1763, 0.0414, 0.1160, 0.0820, 0.0420,
    0.2080, 0.5560, 0.2080, 0.1100, 0.2560,
    0.1400, 0.2559, 0.1304, 0.1987, 0.1997,
    0.1923, 0.2185, 0.1292, 0.0680, 0.2090,
    0.0845, 0.0749, 0.1499, 0.0236, 0.2020,
    0.1790, 0.2700, 0.3292, 0.3800, 0.2087,
    0.3960, 0.4153, 0.6027, 0.4533, 0.2000, 0.0599,
])

# Ybus (imaginary), invert, reactance matrix — all constant
_F09_n_bus = 30
_F09_YI = 1.0 / _F09_linedata_x
_F09_YIbus = np.zeros((_F09_n_bus, _F09_n_bus))
for _k in range(len(_F09_na)):
    _ni = _F09_na[_k] - 1
    _mi = _F09_nb[_k] - 1
    _F09_YIbus[_ni, _ni] += _F09_YI[_k]
    _F09_YIbus[_ni, _mi] -= _F09_YI[_k]
    _F09_YIbus[_mi, _ni] -= _F09_YI[_k]
    _F09_YIbus[_mi, _mi] += _F09_YI[_k]
_F09_X = np.zeros((_F09_n_bus, _F09_n_bus))
_F09_X[1:, 1:] = np.linalg.inv(_F09_YIbus[1:, 1:])

# Vectorised PTDF tensor: (ng, nd, n_lines)
# PTDF[i,j,k] = (X[na[k]-1, g[i]] - X[nb[k]-1, g[i]]
#               - X[na[k]-1, d[j]] + X[nb[k]-1, d[j]]) / linedata_x[k]
_F09_Xg_na = _F09_X[_F09_na - 1][:, _F09_g_idx].T   # (ng, n_lines)
_F09_Xg_nb = _F09_X[_F09_nb - 1][:, _F09_g_idx].T   # (ng, n_lines)
_F09_Xd_na = _F09_X[_F09_na - 1][:, _F09_d_idx].T   # (nd, n_lines)
_F09_Xd_nb = _F09_X[_F09_nb - 1][:, _F09_d_idx].T   # (nd, n_lines)
_F09_PTDF = (
    (_F09_Xg_na[:, None, :] - _F09_Xg_nb[:, None, :])
    - (_F09_Xd_na[None, :, :] - _F09_Xd_nb[None, :, :])
) / _F09_linedata_x[None, None, :]

# Rate references
_F09_Rg = np.array([32.7290, 32.1122, 30.3532, 33.6474, 64.1156, 66.8729])
_F09_Rd = np.array([
    7.5449, 10.7964, 10.9944, 11.0402, 11.7990, 15.3803,
    42.6800, 41.4551, 73.1939, 57.0430, 45.5920, 43.6553,
    61.8002, 59.6409, 57.0279, 51.0749, 67.1070, 60.6623,
    198.6744, 178.9956, 199.9483,
])
_F09_FC = 100.0 * _F09_linedata_x / np.sum(_F09_linedata_x)
_F09_pg = _F09_Pg - _F09_BT_row_sum   # available poolco gen
_F09_pd = _F09_Pd - _F09_BT_col_sum   # available poolco demand

# ----------------------------------------------------------------------
# Audit CEC2011-M1: freeze every F09 module-level constant.
#
# Extends the M-2 pattern (cec2011_bounds return arrays are read-only)
# to the Energy-Brokerage problem's per-module tables.  These arrays
# are eagerly computed at import time, cached for the lifetime of the
# worker, and read on every one of the 150_000 NFEs per CEC2011 run.
# Any in-place mutation downstream would silently corrupt every
# subsequent evaluation in the same worker.  Flipping ``writeable`` off
# turns that class of bug into an immediate ``ValueError`` at the
# mutation site, and adds ~0 ns to the read-only hot path.
# ----------------------------------------------------------------------
for _arr in (
    _F09_bus_Pg, _F09_bus_Pd,
    _F09_g_idx, _F09_d_idx,
    _F09_Pg, _F09_Pd,
    _F09_BT, _F09_BT_row_sum, _F09_BT_col_sum,
    _F09_na, _F09_nb, _F09_linedata_x,
    _F09_YI, _F09_YIbus, _F09_X,
    _F09_Xg_na, _F09_Xg_nb, _F09_Xd_na, _F09_Xd_nb,
    _F09_PTDF,
    _F09_Rg, _F09_Rd, _F09_FC,
    _F09_pg, _F09_pd,
):
    _arr.flags.writeable = False

# Clean up loop variables from module scope
del _k, _ni, _mi, _arr


def f09_energy_brokerage(x: np.ndarray) -> float:
    """F9: Large-Scale Energy Brokerage (IEEE 30-bus).  D=126.

    Minimises rate deviation in a poolco-based electricity market on the
    IEEE 30-bus system with bilateral transactions.

    Parameters
    ----------
    x : ndarray, shape (126,)
        Poolco transaction matrix entries (6 generators x 21 loads),
        flattened row-major.

    Returns
    -------
    cost : float
        Objective = rate_deviation + 50 * Kp * constraint_penalty.
    """
    GD = x.reshape(_F09_ng, _F09_nd)

    # Vectorised line flows: flows[k] = sum_{i,j} |PTDF[i,j,k]*GD[i,j]|
    #                                            + |PTDF[i,j,k]*BT[i,j]|
    flows = np.sum(
        np.abs(_F09_PTDF * GD[:, :, None])
        + np.abs(_F09_PTDF * _F09_BT[:, :, None]),
        axis=(0, 1),
    )
    cost_line = _F09_FC / np.maximum(flows, 1e-20)

    # Vectorised line usage cost: cost_l[i,j] = sum_k |cost_line[k]*PTDF[i,j,k]|
    cost_l = np.sum(np.abs(cost_line[None, None, :] * _F09_PTDF), axis=2)

    # Rate deviations (vectorised over generators / loads)
    cost_gen = np.sum(GD * cost_l, axis=1)     # (ng,)
    rate_ebe1 = float(np.sum((cost_gen / _F09_pg - _F09_Rg) ** 2))

    cost_load = np.sum(GD * cost_l, axis=0)    # (nd,)
    rate_ebe2 = float(np.sum((cost_load / _F09_pd - _F09_Rd) ** 2))

    # Constraint violations
    Pg_x = np.sum(GD, axis=1) + _F09_BT_row_sum
    Pd_x = np.sum(GD, axis=0) + _F09_BT_col_sum
    PENALTY = 100.0 * np.sum(np.abs(Pg_x - _F09_Pg)) \
        + 100.0 * np.sum(np.abs(Pd_x - _F09_Pd))

    return float(rate_ebe1 + rate_ebe2 + 50.0 * 100.0 * PENALTY)


# =========================================================================== #
#  F11: Dynamic Economic Load Dispatch -- 5-unit 24h
# =========================================================================== #

# 5-unit coefficient data
# Data1: [Pmin, Pmax, a, b, c, e, f]
_DED5_DATA1 = np.array([
    [10,  75,  0.0080, 2.0, 25,  100, 0.042],
    [20,  125, 0.0030, 1.8, 60,  140, 0.040],
    [30,  175, 0.0012, 2.1, 100, 160, 0.038],
    [40,  250, 0.0010, 2.0, 120, 180, 0.037],
    [50,  300, 0.0015, 1.8, 40,  200, 0.035],
])

# Data2: [Po, UR, DR, Zone1min, Zone1max, Zone2min, Zone2max]
_DED5_DATA2 = np.array([
    [np.nan, 30, 30, 10, 10, 10, 10],
    [np.nan, 30, 30, 20, 20, 20, 20],
    [np.nan, 40, 40, 30, 30, 30, 30],
    [np.nan, 50, 50, 40, 40, 40, 40],
    [np.nan, 50, 50, 50, 50, 50, 50],
])

# Loss coefficients (5x5)
_DED5_B1 = np.array([
    [0.000049, 0.000014, 0.000015, 0.000015, 0.000020],
    [0.000014, 0.000045, 0.000016, 0.000020, 0.000018],
    [0.000015, 0.000016, 0.000039, 0.000010, 0.000012],
    [0.000015, 0.000020, 0.000010, 0.000040, 0.000014],
    [0.000020, 0.000018, 0.000012, 0.000014, 0.000035],
])

_DED5_DEMAND = np.array([
    410, 435, 475, 530, 558, 608, 626, 654, 690, 704,
    720, 740, 704, 690, 654, 580, 558, 608, 654, 704,
    680, 605, 527, 463,
], dtype=np.float64)

# Audit MED-PERF (CEC2011): hoist per-column slices that the F11 hot path
# would otherwise rebuild on every NFE.  CEC2011's budget is 150_000
# evaluations per run, so the seven ``_DED5_DATA1[:, k]`` view operations
# inside the body added up to ~1M view objects per run for nothing -- the
# columns are pure functions of the static problem definition.  Hoist
# them, mark the rest of the per-call setup as constants too, and freeze
# the writeable flag so a buggy caller cannot mutate the master tables.
_DED5_PMIN = _DED5_DATA1[:, 0]
_DED5_PMAX = _DED5_DATA1[:, 1]
_DED5_A = _DED5_DATA1[:, 2]
_DED5_B = _DED5_DATA1[:, 3]
_DED5_C = _DED5_DATA1[:, 4]
_DED5_E = _DED5_DATA1[:, 5]
_DED5_F = _DED5_DATA1[:, 6]
_DED5_UP_RAMP = _DED5_DATA2[:, 1]
_DED5_DOWN_RAMP = _DED5_DATA2[:, 2]
# POZ: Data2 columns 3..end, transposed to (rows_of_zones, units) -> (4, 5)
_DED5_POZ_ALL = _DED5_DATA2[:, 3:].T
_DED5_POZ_LOWER = _DED5_POZ_ALL[0::2, :]  # (2, 5)
_DED5_POZ_UPPER = _DED5_POZ_ALL[1::2, :]  # (2, 5)
_DED5_NUM_POZ = _DED5_POZ_LOWER.shape[0]

for _arr in (
    _DED5_DATA1, _DED5_DATA2, _DED5_B1, _DED5_DEMAND,
    _DED5_PMIN, _DED5_PMAX, _DED5_A, _DED5_B, _DED5_C, _DED5_E, _DED5_F,
    _DED5_UP_RAMP, _DED5_DOWN_RAMP,
    _DED5_POZ_ALL, _DED5_POZ_LOWER, _DED5_POZ_UPPER,
):
    _arr.flags.writeable = False
del _arr


def f11_dynamic_eld_5unit(x: np.ndarray) -> float:
    """F11: Dynamic Economic Load Dispatch, 5-unit 24h.  D=120.

    Minimises total generation cost over a 24-hour horizon for 5 thermal
    units, subject to power balance, capacity, ramp-rate, and prohibited
    operating zone constraints.

    Parameters
    ----------
    x : ndarray, shape (120,)
        Generation schedule, reshaped as ``(5, 24).T`` -> (24, 5).

    Returns
    -------
    cost : float
        Total cost + penalty.
    """
    No_of_Units = 5
    No_of_Load_Hours = 24

    # Reference: reshape(x, 5, 24)' — column-major fill then transpose.
    # Must use order='F' to match the reference column-major layout, so that
    # consecutive x elements cycle through units (not hours).
    # Bounds np.tile(Pmin, 24) assume this convention: x[k] → unit k%5.
    Input_Gen = x.reshape(No_of_Units, No_of_Load_Hours, order='F').T

    # Audit MED-PERF (CEC2011): consume the module-level hoisted views from
    # _DED5_DATA1 / _DED5_DATA2 instead of slicing on every NFE.
    Pmin = _DED5_PMIN
    Pmax = _DED5_PMAX
    a = _DED5_A
    b = _DED5_B
    c = _DED5_C
    e = _DED5_E
    f = _DED5_F

    Up_Ramp = _DED5_UP_RAMP
    Down_Ramp = _DED5_DOWN_RAMP

    POZ_Lower = _DED5_POZ_LOWER  # (2, 5)
    POZ_Upper = _DED5_POZ_UPPER  # (2, 5)
    No_of_POZ_Limits = _DED5_NUM_POZ * 2

    B1 = _DED5_B1

    # --- Vectorised over all 24 hours simultaneously ---

    # Power loss for each hour: PL[j] = xj @ B1 @ xj (B2=0)
    # einsum 'hi,ij,hj->h' computes quadratic form per row
    PL = np.einsum('hi,ij,hj->h', Input_Gen, B1, Input_Gen)
    PL = np.round(PL * 10000.0) / 10000.0

    # Balance penalty: |demand + PL - sum_of_gen|
    total_balance_pen = float(np.sum(np.abs(
        _DED5_DEMAND + PL - np.sum(Input_Gen, axis=1)
    )))

    # Capacity penalty (vectorised): 2 * sum(max(Pmin-x,0) + max(x-Pmax,0))
    cap_lo = np.maximum(0.0, Pmin[None, :] - Input_Gen)   # (24, 5)
    cap_hi = np.maximum(0.0, Input_Gen - Pmax[None, :])
    total_cap_pen = 2.0 * float(np.sum(cap_lo + cap_hi))

    # Ramp penalty (hours 1..23): previous gen = Input_Gen[j-1]
    prev = Input_Gen[:-1, :]   # (23, 5)
    curr = Input_Gen[1:, :]    # (23, 5)
    url = np.minimum(Pmax[None, :], prev + Up_Ramp[None, :])
    drl = np.maximum(Pmin[None, :], prev - Down_Ramp[None, :])
    ramp_lo = np.maximum(0.0, drl - curr)
    ramp_hi = np.maximum(0.0, curr - url)
    total_ramp_pen = 2.0 * float(np.sum(ramp_lo + ramp_hi))

    # POZ penalty (all hours, all zones)
    total_poz_pen = 0.0
    for z in range(No_of_POZ_Limits // 2):
        lo_z = POZ_Lower[z, :]    # (5,)
        hi_z = POZ_Upper[z, :]    # (5,)
        inside = (Input_Gen > lo_z[None, :]) & (Input_Gen < hi_z[None, :])
        if np.any(inside):
            total_poz_pen += float(np.sum(np.minimum(
                Input_Gen[inside] - np.broadcast_to(lo_z, Input_Gen.shape)[inside],
                np.broadcast_to(hi_z, Input_Gen.shape)[inside] - Input_Gen[inside],
            )))

    # Cost (vectorised with valve-point effect)
    costs = (a[None, :] * Input_Gen**2 + b[None, :] * Input_Gen + c[None, :]
             + np.abs(e[None, :] * np.sin(f[None, :] * (Pmin[None, :] - Input_Gen))))
    total_cost = float(np.sum(costs))

    total_penalty = (
        1e3 * total_balance_pen
        + 1e3 * total_cap_pen
        + 1e5 * total_ramp_pen
        + 1e5 * total_poz_pen
    )
    return float(total_cost + total_penalty)


# =========================================================================== #
#  F12: Dynamic Economic Load Dispatch -- 10-unit 24h
# =========================================================================== #

# 10-unit coefficient data
# Data1: [Pmin, Pmax, a, b, c, e, f]
_DED10_DATA1 = np.array([
    [150, 470, 0.00043, 21.60, 958.20, 450, 0.041],
    [135, 460, 0.00063, 21.05, 1313.6, 600, 0.036],
    [73,  340, 0.00039, 20.81, 604.97, 320, 0.028],
    [60,  300, 0.00070, 23.90, 471.60, 260, 0.052],
    [73,  243, 0.00079, 21.62, 480.29, 280, 0.063],
    [57,  160, 0.00056, 17.87, 601.75, 310, 0.048],
    [20,  130, 0.00211, 16.51, 502.7,  300, 0.086],
    [47,  120, 0.0048,  23.23, 639.40, 340, 0.082],
    [20,  80,  0.10908, 19.58, 455.60, 270, 0.098],
    [55,  55,  0.00951, 22.54, 692.4,  380, 0.094],
])

# Data2: [Po, UR, DR] -- no POZ zones for 10-unit
_DED10_DATA2 = np.array([
    [np.nan, 80, 80],
    [np.nan, 80, 80],
    [np.nan, 80, 80],
    [np.nan, 50, 50],
    [np.nan, 50, 50],
    [np.nan, 50, 50],
    [np.nan, 30, 30],
    [np.nan, 30, 30],
    [np.nan, 30, 30],
    [np.nan, 30, 30],
])

_DED10_DEMAND = np.array([
    1036, 1110, 1258, 1406, 1480, 1628, 1702, 1776, 1924, 2072,
    2146, 2220, 2072, 1924, 1776, 1554, 1480, 1628, 1776, 2072,
    1924, 1628, 1332, 1184,
], dtype=np.float64)

# Audit MED-PERF (CEC2011): hoist per-column slices that the F12 hot path
# would otherwise rebuild on every NFE.  Same rationale as F11 above --
# CEC2011's 150_000-NFE budget multiplied by seven slice operations per
# call adds up to ~1M wasted view allocations per run.
_DED10_PMIN = _DED10_DATA1[:, 0]
_DED10_PMAX = _DED10_DATA1[:, 1]
_DED10_A = _DED10_DATA1[:, 2]
_DED10_B = _DED10_DATA1[:, 3]
_DED10_C = _DED10_DATA1[:, 4]
_DED10_E = _DED10_DATA1[:, 5]
_DED10_F = _DED10_DATA1[:, 6]
_DED10_UP_RAMP = _DED10_DATA2[:, 1]
_DED10_DOWN_RAMP = _DED10_DATA2[:, 2]

for _arr in (
    _DED10_DATA1, _DED10_DATA2, _DED10_DEMAND,
    _DED10_PMIN, _DED10_PMAX, _DED10_A, _DED10_B, _DED10_C, _DED10_E, _DED10_F,
    _DED10_UP_RAMP, _DED10_DOWN_RAMP,
):
    _arr.flags.writeable = False
del _arr


def f12_dynamic_eld_10unit(x: np.ndarray) -> float:
    """F12: Dynamic Economic Load Dispatch, 10-unit 24h.  D=240.

    Minimises total generation cost over a 24-hour horizon for 10 thermal
    units, subject to power balance, capacity, and ramp-rate constraints.
    No POZ zones in the 10-unit formulation.

    Parameters
    ----------
    x : ndarray, shape (240,)
        Generation schedule, reshaped as ``(10, 24).T`` -> (24, 10).

    Returns
    -------
    cost : float
        Total cost + penalty.
    """
    No_of_Units = 10
    No_of_Load_Hours = 24

    # Reference: reshape(x, 10, 24)' — column-major fill then transpose.
    # Must use order='F' to match the reference column-major layout, so that
    # consecutive x elements cycle through units (not hours).
    # Bounds np.tile(Pmin, 24) assume this convention: x[k] → unit k%10.
    Input_Gen = x.reshape(No_of_Units, No_of_Load_Hours, order='F').T

    # Audit MED-PERF (CEC2011): consume the module-level hoisted views from
    # _DED10_DATA1 / _DED10_DATA2 instead of slicing on every NFE.
    Pmin = _DED10_PMIN
    Pmax = _DED10_PMAX
    a = _DED10_A
    b_coeff = _DED10_B
    c = _DED10_C
    e = _DED10_E
    f = _DED10_F

    Up_Ramp = _DED10_UP_RAMP
    Down_Ramp = _DED10_DOWN_RAMP

    # No POZ zones -- Data2 has only 3 columns, so Data2(:,4:end)' is empty
    # Reference: Prohibited_Operating_Zones_POZ = Data2(:,4:end)' -> (0, 10)
    # No_of_POZ_Limits = 0, so POZ_Penalty is always 0

    # --- Vectorised over all 24 hours simultaneously ---
    # B1=0, B2=0 => Power_Loss=0 for all hours

    # Balance penalty: |demand - sum_of_gen|
    total_balance_pen = float(np.sum(np.abs(
        _DED10_DEMAND - np.sum(Input_Gen, axis=1)
    )))

    # Capacity penalty (vectorised)
    cap_lo = np.maximum(0.0, Pmin[None, :] - Input_Gen)
    cap_hi = np.maximum(0.0, Input_Gen - Pmax[None, :])
    total_cap_pen = 2.0 * float(np.sum(cap_lo + cap_hi))

    # Ramp penalty (hours 1..23)
    prev = Input_Gen[:-1, :]
    curr = Input_Gen[1:, :]
    url = np.minimum(Pmax[None, :], prev + Up_Ramp[None, :])
    drl = np.maximum(Pmin[None, :], prev - Down_Ramp[None, :])
    ramp_lo = np.maximum(0.0, drl - curr)
    ramp_hi = np.maximum(0.0, curr - url)
    total_ramp_pen = 2.0 * float(np.sum(ramp_lo + ramp_hi))

    # No POZ zones for 10-unit formulation
    total_poz_pen = 0.0

    # Cost (vectorised with valve-point effect)
    costs = (a[None, :] * Input_Gen**2 + b_coeff[None, :] * Input_Gen + c[None, :]
             + np.abs(e[None, :] * np.sin(f[None, :] * (Pmin[None, :] - Input_Gen))))
    total_cost = float(np.sum(costs))

    # Note: ramp uses 1e3 (not 1e5) for 10-unit, matching reference
    total_penalty = (
        1e3 * total_balance_pen
        + 1e3 * total_cap_pen
        + 1e3 * total_ramp_pen
        + 1e5 * total_poz_pen
    )
    return float(total_cost + total_penalty)


# =========================================================================== #
#  F13: Static Economic Load Dispatch -- 6-unit
# =========================================================================== #

# Data1: [Pmin, Pmax, a, b, c]
_ELD6_DATA1 = np.array([
    [100, 500, 0.0070, 7.0,  240],
    [50,  200, 0.0095, 10.0, 200],
    [80,  300, 0.0090, 8.5,  220],
    [50,  150, 0.0090, 11.0, 200],
    [50,  200, 0.0080, 10.5, 220],
    [50,  120, 0.0075, 12.0, 190],
])

# Data2: [Po, UR, DR, Zone1min, Zone1max, Zone2min, Zone2max]
_ELD6_DATA2 = np.array([
    [440, 80,  120, 210, 240, 350, 380],
    [170, 50,  90,  90,  110, 140, 160],
    [200, 65,  100, 150, 170, 210, 240],
    [150, 50,  90,  80,  90,  110, 120],
    [190, 50,  90,  90,  110, 140, 150],
    [150, 50,  90,  75,  85,  100, 105],
])

# Loss coefficients (6x6)
_ELD6_B1 = np.array([
    [1.7,  1.2,  0.7, -0.1, -0.5, -0.2],
    [1.2,  1.4,  0.9,  0.1, -0.6, -0.1],
    [0.7,  0.9,  3.1,  0.0, -1.0, -0.6],
    [-0.1, 0.1,  0.0,  0.24, -0.6, -0.8],
    [-0.5, -0.6, -0.1, -0.6, 12.9, -0.2],
    [0.2,  -0.1, -0.6, -0.8, -0.2, 15.0],
]) * 1e-5

_ELD6_B2 = np.array([-0.3908, -0.1297, 0.7047, 0.0591, 0.2161, -0.6635]) * 1e-5
_ELD6_B3 = 0.0056e-2


# Pre-computed constants for F13 (avoids rebuilding on every evaluation).
_ELD6_Pmin = _ELD6_DATA1[:, 0]
_ELD6_Pmax = _ELD6_DATA1[:, 1]
_ELD6_a = _ELD6_DATA1[:, 2]
_ELD6_b = _ELD6_DATA1[:, 3]
_ELD6_c = _ELD6_DATA1[:, 4]

_ELD6_Up_Ramp_Limit = np.minimum(_ELD6_Pmax, _ELD6_DATA2[:, 0] + _ELD6_DATA2[:, 1])
_ELD6_Down_Ramp_Limit = np.maximum(_ELD6_Pmin, _ELD6_DATA2[:, 0] - _ELD6_DATA2[:, 2])

# POZ: Data2 columns 3..end -> (4, 6) -> lower=(2,6), upper=(2,6)
_ELD6_POZ_all = _ELD6_DATA2[:, 3:].T  # (4, 6)
_ELD6_POZ_Lower = _ELD6_POZ_all[0::2, :]  # (2, 6)
_ELD6_POZ_Upper = _ELD6_POZ_all[1::2, :]  # (2, 6)

for _arr in (
    _ELD6_DATA1, _ELD6_DATA2, _ELD6_B1, _ELD6_B2,
    _ELD6_Pmin, _ELD6_Pmax, _ELD6_a, _ELD6_b, _ELD6_c,
    _ELD6_Up_Ramp_Limit, _ELD6_Down_Ramp_Limit,
    _ELD6_POZ_all, _ELD6_POZ_Lower, _ELD6_POZ_Upper,
):
    _arr.flags.writeable = False
del _arr


def f13_static_eld_6unit(x: np.ndarray) -> float:
    """F13: Static Economic Load Dispatch, 6-unit.  D=6.

    Minimises fuel cost for 6 thermal generators subject to power balance,
    capacity, ramp-rate, and prohibited operating zone constraints.
    No valve-point effect.

    Parameters
    ----------
    x : ndarray, shape (6,)
        Generator outputs in MW.

    Returns
    -------
    cost : float
        Total cost + penalty.
    """
    # Power loss (rounded to 4 decimals)
    Power_Loss = float(x @ _ELD6_B1 @ x + _ELD6_B2 @ x + _ELD6_B3)
    Power_Loss = np.round(Power_Loss * 10000.0) / 10000.0

    # Power balance penalty
    balance_pen = abs(1263.0 + Power_Loss - np.sum(x))

    # Capacity penalty
    cap_pen = _capacity_penalty(x, _ELD6_Pmin, _ELD6_Pmax)

    # Ramp penalty
    ramp_pen = _ramp_penalty(x, _ELD6_Down_Ramp_Limit, _ELD6_Up_Ramp_Limit)

    # POZ penalty
    poz_pen = _poz_penalty(x, _ELD6_POZ_Lower, _ELD6_POZ_Upper)

    total_penalty = (
        1e3 * balance_pen
        + 1e3 * cap_pen
        + 1e5 * ramp_pen
        + 1e5 * poz_pen
    )

    # Cost (no valve-point effect)
    cost = float(np.sum(_ELD6_a * x**2 + _ELD6_b * x + _ELD6_c))

    return float(cost + total_penalty)


# =========================================================================== #
#  F14: Static Economic Load Dispatch -- 13-unit
# =========================================================================== #

# Data1: [Pmin, Pmax, a, b, c, e, f]
_ELD13_DATA1 = np.array([
    [0,  680, 0.00028, 8.1,  550, 300, 0.035],
    [0,  360, 0.00056, 8.1,  309, 200, 0.042],
    [0,  360, 0.00056, 8.1,  307, 200, 0.042],
    [60, 180, 0.00324, 7.74, 240, 150, 0.063],
    [60, 180, 0.00324, 7.74, 240, 150, 0.063],
    [60, 180, 0.00324, 7.74, 240, 150, 0.063],
    [60, 180, 0.00324, 7.74, 240, 150, 0.063],
    [60, 180, 0.00324, 7.74, 240, 150, 0.063],
    [60, 180, 0.00324, 7.74, 240, 150, 0.063],
    [40, 120, 0.00284, 8.6,  126, 100, 0.084],
    [40, 120, 0.00284, 8.6,  126, 100, 0.084],
    [55, 120, 0.00284, 8.6,  126, 100, 0.084],
    [55, 120, 0.00284, 8.6,  126, 100, 0.084],
])

# Audit MED-PERF (CEC2011): hoist per-column slices for F14, same rationale
# as F11/F12 above.  150_000 NFE/run × 7 slice operations = ~1M wasted view
# allocations per run.
_ELD13_PMIN = _ELD13_DATA1[:, 0]
_ELD13_PMAX = _ELD13_DATA1[:, 1]
_ELD13_A = _ELD13_DATA1[:, 2]
_ELD13_B = _ELD13_DATA1[:, 3]
_ELD13_C = _ELD13_DATA1[:, 4]
_ELD13_E = _ELD13_DATA1[:, 5]
_ELD13_F = _ELD13_DATA1[:, 6]

for _arr in (
    _ELD13_DATA1,
    _ELD13_PMIN, _ELD13_PMAX, _ELD13_A, _ELD13_B, _ELD13_C, _ELD13_E, _ELD13_F,
):
    _arr.flags.writeable = False
del _arr


def f14_static_eld_13unit(x: np.ndarray) -> float:
    """F14: Static Economic Load Dispatch, 13-unit.  D=13.

    Minimises fuel cost with valve-point effect for 13 thermal generators.
    No transmission losses (B1=0), no ramp limits, no POZ.

    Parameters
    ----------
    x : ndarray, shape (13,)
        Generator outputs in MW.

    Returns
    -------
    cost : float
        Total cost + penalty.
    """
    Power_Demand = 1800.0

    # Audit MED-PERF (CEC2011): consume the module-level hoisted views from
    # _ELD13_DATA1 instead of slicing on every NFE.
    Pmin = _ELD13_PMIN
    Pmax = _ELD13_PMAX
    a = _ELD13_A
    b = _ELD13_B
    c = _ELD13_C
    e = _ELD13_E
    f = _ELD13_F

    # No losses -- reference defines B1=zeros(13,13), B2=zeros(1,13), B3=0,
    # computes x*B1*x'+B2*x'+B3 = 0, then rounds.  Skipped for performance.
    Power_Loss = 0.0

    # Power balance penalty
    balance_pen = abs(Power_Demand + Power_Loss - np.sum(x))

    # Capacity penalty
    cap_pen = _capacity_penalty(x, Pmin, Pmax)

    total_penalty = 1e5 * balance_pen + 1e3 * cap_pen

    # Cost (with valve-point effect)
    cost = float(np.sum(
        a * x**2 + b * x + c + np.abs(e * np.sin(f * (Pmin - x)))
    ))

    return float(cost + total_penalty)


# =========================================================================== #
#  F15: Static Economic Load Dispatch -- 15-unit
# =========================================================================== #

# Data1: [Pmin, Pmax, a, b, c]
_ELD15_DATA1 = np.array([
    [150, 455, 0.000299, 10.1, 671],
    [150, 455, 0.000183, 10.2, 574],
    [20,  130, 0.001126, 8.8,  374],
    [20,  130, 0.001126, 8.8,  374],
    [150, 470, 0.000205, 10.4, 461],
    [135, 460, 0.000301, 10.1, 630],
    [135, 465, 0.000364, 9.8,  548],
    [60,  300, 0.000338, 11.2, 227],
    [25,  162, 0.000807, 11.2, 173],
    [25,  160, 0.001203, 10.7, 175],
    [20,  80,  0.003586, 10.2, 186],
    [20,  80,  0.005513, 9.9,  230],
    [25,  85,  0.000371, 13.1, 225],
    [15,  55,  0.001929, 12.1, 309],
    [15,  55,  0.004447, 12.4, 323],
])

# Data2: [Po, UR, DR, Zone1min, Zone1max, Zone2min, Zone2max, Zone3min, Zone3max]
_ELD15_DATA2 = np.array([
    [400, 80,  120, 150, 150, 150, 150, 150, 150],
    [300, 80,  120, 185, 255, 305, 335, 420, 450],
    [105, 130, 130, 20,  20,  20,  20,  20,  20],
    [100, 130, 130, 20,  20,  20,  20,  20,  20],
    [90,  80,  120, 180, 200, 305, 335, 390, 420],
    [400, 80,  120, 230, 255, 365, 395, 430, 455],
    [350, 80,  120, 135, 135, 135, 135, 135, 135],
    [95,  65,  100, 60,  60,  60,  60,  60,  60],
    [105, 60,  100, 25,  25,  25,  25,  25,  25],
    [110, 60,  100, 25,  25,  25,  25,  25,  25],
    [60,  80,  80,  20,  20,  20,  20,  20,  20],
    [40,  80,  80,  30,  40,  55,  65,  20,  20],
    [30,  80,  80,  25,  25,  25,  25,  25,  25],
    [20,  55,  55,  15,  15,  15,  15,  15,  15],
    [20,  55,  55,  15,  15,  15,  15,  15,  15],
])

# Loss coefficients (15x15)
_ELD15_B1 = np.array([
    [1.4,  1.2,  0.7,  -0.1, -0.3, -0.1, -0.1, -0.1, -0.3, -0.5, -0.3, -0.2, 0.4,   0.3,   -0.1],
    [1.2,  1.5,  1.3,   0.0, -0.5, -0.2,  0.0,  0.1, -0.2, -0.4, -0.4,  0.0, 0.4,   1.0,   -0.2],
    [0.7,  1.3,  7.6,  -0.1, -1.3, -0.9, -0.1,  0.0, -0.8, -1.2, -1.7,  0.0, -2.6, 11.1,   -2.8],
    [-0.1, 0.0, -0.1,   3.4, -0.7, -0.4,  1.1,  5.0,  2.9,  3.2, -1.1,  0.0, 0.1,   0.1,   -2.6],
    [-0.3, -0.5, -1.3, -0.7,  9.0,  1.4, -0.3, -1.2, -1.0, -1.3, 0.7,  -0.2, -0.2, -2.4,   -0.3],
    [-0.1, -0.2, -0.9, -0.4,  1.4,  1.6,  0.0, -0.6, -0.5, -0.8, 1.1,  -0.1, -0.2, -1.7,    0.3],
    [-0.1, 0.0,  -0.1,  1.1, -0.3,  0.0,  1.5,  1.7,  1.5,  0.9, -0.5,  0.7, 0.0,  -0.2,   -0.8],
    [-0.1, 0.1,   0.0,  5.0, -1.2, -0.6,  1.7, 16.8,  8.2,  7.9, -2.3, -3.6, 0.1,   0.5,   -7.8],
    [-0.3, -0.2, -0.8,  2.9, -1.0, -0.5,  1.5,  8.2, 12.9, 11.6, -2.1, -2.5, 0.7,  -1.2,   -7.2],
    [-0.5, -0.4, -1.2,  3.2, -1.3, -0.8,  0.9,  7.9, 11.6, 20.0, -2.7, -3.4, 0.9,  -1.1,   -8.8],
    [-0.3, -0.4, -1.7, -1.1,  0.7,  1.1, -0.5, -2.3, -2.1, -2.7, 14.0,  0.1, 0.4,  -3.8,   16.8],
    [-0.2, 0.0,   0.0,  0.0, -0.2, -0.1,  0.7, -3.6, -2.5, -3.4, 0.1,   5.4, -0.1, -0.4,    2.8],
    [0.4,  0.4,  -2.6,  0.1, -0.2, -0.2,  0.0,  0.1,  0.7,  0.9, 0.4,  -0.1, 10.3, -10.1,   2.8],
    [0.3,  1.0,  11.1,  0.1, -2.4, -1.7, -0.2,  0.5, -1.2, -1.1, -3.8, -0.4, -10.1, 57.8,  -9.4],
    [-0.1, -0.2, -2.8, -2.6, -0.3,  0.3, -0.8, -7.8, -7.2, -8.8, 16.8,  2.8, 2.8,  -9.4,  128.3],
]) * 1e-5

_ELD15_B2 = np.array([
    -0.1, -0.2, 2.8, -0.1, 0.1, -0.3, -0.2, -0.2, 0.6, 3.9,
    -1.7, 0.0, -3.2, 6.7, -6.4,
]) * 1e-5

_ELD15_B3 = 0.0055e-2


# Pre-computed constants for F15 (avoids rebuilding on every evaluation).
_ELD15_Pmin = _ELD15_DATA1[:, 0]
_ELD15_Pmax = _ELD15_DATA1[:, 1]
_ELD15_a = _ELD15_DATA1[:, 2]
_ELD15_b = _ELD15_DATA1[:, 3]
_ELD15_c = _ELD15_DATA1[:, 4]

_ELD15_Up_Ramp_Limit = np.minimum(
    _ELD15_Pmax, _ELD15_DATA2[:, 0] + _ELD15_DATA2[:, 1]
)
_ELD15_Down_Ramp_Limit = np.maximum(
    _ELD15_Pmin, _ELD15_DATA2[:, 0] - _ELD15_DATA2[:, 2]
)

# POZ: Data2 columns 3..end -> (6, 15) -> lower=(3,15), upper=(3,15)
_ELD15_POZ_all = _ELD15_DATA2[:, 3:].T  # (6, 15)
_ELD15_POZ_Lower = _ELD15_POZ_all[0::2, :]  # (3, 15)
_ELD15_POZ_Upper = _ELD15_POZ_all[1::2, :]  # (3, 15)

for _arr in (
    _ELD15_DATA1, _ELD15_DATA2, _ELD15_B1, _ELD15_B2,
    _ELD15_Pmin, _ELD15_Pmax, _ELD15_a, _ELD15_b, _ELD15_c,
    _ELD15_Up_Ramp_Limit, _ELD15_Down_Ramp_Limit,
    _ELD15_POZ_all, _ELD15_POZ_Lower, _ELD15_POZ_Upper,
):
    _arr.flags.writeable = False
del _arr


def f15_static_eld_15unit(x: np.ndarray) -> float:
    """F15: Static Economic Load Dispatch, 15-unit.  D=15.

    Minimises fuel cost for 15 thermal generators with transmission losses,
    ramp-rate limits, and prohibited operating zones.
    No valve-point effect.

    Parameters
    ----------
    x : ndarray, shape (15,)
        Generator outputs in MW.

    Returns
    -------
    cost : float
        Total cost + penalty.
    """
    # Power loss (rounded to 4 decimals)
    Power_Loss = float(x @ _ELD15_B1 @ x + _ELD15_B2 @ x + _ELD15_B3)
    Power_Loss = np.round(Power_Loss * 10000.0) / 10000.0

    # Power balance penalty
    balance_pen = abs(2630.0 + Power_Loss - np.sum(x))

    # Capacity penalty
    cap_pen = _capacity_penalty(x, _ELD15_Pmin, _ELD15_Pmax)

    # Ramp penalty
    ramp_pen = _ramp_penalty(x, _ELD15_Down_Ramp_Limit, _ELD15_Up_Ramp_Limit)

    # POZ penalty
    poz_pen = _poz_penalty(x, _ELD15_POZ_Lower, _ELD15_POZ_Upper)

    total_penalty = (
        1e3 * balance_pen
        + 1e3 * cap_pen
        + 1e5 * ramp_pen
        + 1e5 * poz_pen
    )

    # Cost (no valve-point effect)
    cost = float(np.sum(_ELD15_a * x**2 + _ELD15_b * x + _ELD15_c))

    return float(cost + total_penalty)


# =========================================================================== #
#  F16: Static Economic Load Dispatch -- 40-unit
# =========================================================================== #

# Data1: [Pmin, Pmax, a, b, c, e, f]
_ELD40_DATA1 = np.array([
    [36,  114, 0.0069,  6.73, 94.705,  100, 0.084],
    [36,  114, 0.0069,  6.73, 94.705,  100, 0.084],
    [60,  120, 0.02028, 7.07, 309.54,  100, 0.084],
    [80,  190, 0.00942, 8.18, 369.03,  150, 0.063],
    [47,  97,  0.0114,  5.35, 148.89,  120, 0.077],
    [68,  140, 0.01142, 8.05, 222.33,  100, 0.084],
    [110, 300, 0.00357, 8.03, 287.71,  200, 0.042],
    [135, 300, 0.00492, 6.99, 391.98,  200, 0.042],
    [135, 300, 0.00573, 6.6,  455.76,  200, 0.042],
    [130, 300, 0.00605, 12.9, 722.82,  200, 0.042],
    [94,  375, 0.00515, 12.9, 635.2,   200, 0.042],
    [94,  375, 0.00569, 12.8, 654.69,  200, 0.042],
    [125, 500, 0.00421, 12.5, 913.4,   300, 0.035],
    [125, 500, 0.00752, 8.84, 1760.4,  300, 0.035],
    [125, 500, 0.00708, 9.15, 1728.3,  300, 0.035],
    [125, 500, 0.00708, 9.15, 1728.3,  300, 0.035],
    [220, 500, 0.00313, 7.97, 647.85,  300, 0.035],
    [220, 500, 0.00313, 7.95, 649.69,  300, 0.035],
    [242, 550, 0.00313, 7.97, 647.83,  300, 0.035],
    [242, 550, 0.00313, 7.97, 647.81,  300, 0.035],
    [254, 550, 0.00298, 6.63, 785.96,  300, 0.035],
    [254, 550, 0.00298, 6.63, 785.96,  300, 0.035],
    [254, 550, 0.00284, 6.66, 794.53,  300, 0.035],
    [254, 550, 0.00284, 6.66, 794.53,  300, 0.035],
    [254, 550, 0.00277, 7.1,  801.32,  300, 0.035],
    [254, 550, 0.00277, 7.1,  801.32,  300, 0.035],
    [10,  150, 0.52124, 3.33, 1055.1,  120, 0.077],
    [10,  150, 0.52124, 3.33, 1055.1,  120, 0.077],
    [10,  150, 0.52124, 3.33, 1055.1,  120, 0.077],
    [47,  97,  0.0114,  5.35, 148.89,  120, 0.077],
    [60,  190, 0.0016,  6.43, 222.92,  150, 0.063],
    [60,  190, 0.0016,  6.43, 222.92,  150, 0.063],
    [60,  190, 0.0016,  6.43, 222.92,  150, 0.063],
    [90,  200, 0.0001,  8.95, 107.87,  200, 0.042],
    [90,  200, 0.0001,  8.62, 116.58,  200, 0.042],
    [90,  200, 0.0001,  8.62, 116.58,  200, 0.042],
    [25,  110, 0.0161,  5.88, 307.45,  80,  0.098],
    [25,  110, 0.0161,  5.88, 307.45,  80,  0.098],
    [25,  110, 0.0161,  5.88, 307.45,  80,  0.098],
    [242, 550, 0.00313, 7.97, 647.83,  300, 0.035],
])

# Audit MED-PERF (CEC2011): hoist per-column slices for F16, same rationale
# as F11/F12/F14 above.  150_000 NFE/run × 7 slice operations = ~1M wasted
# view allocations per run.
_ELD40_PMIN = _ELD40_DATA1[:, 0]
_ELD40_PMAX = _ELD40_DATA1[:, 1]
_ELD40_A = _ELD40_DATA1[:, 2]
_ELD40_B = _ELD40_DATA1[:, 3]
_ELD40_C = _ELD40_DATA1[:, 4]
_ELD40_E = _ELD40_DATA1[:, 5]
_ELD40_F = _ELD40_DATA1[:, 6]

for _arr in (
    _ELD40_DATA1,
    _ELD40_PMIN, _ELD40_PMAX, _ELD40_A, _ELD40_B, _ELD40_C, _ELD40_E, _ELD40_F,
):
    _arr.flags.writeable = False
del _arr


def f16_static_eld_40unit(x: np.ndarray) -> float:
    """F16: Static Economic Load Dispatch, 40-unit.  D=40.

    Minimises fuel cost with valve-point effect for 40 thermal generators.
    No transmission losses (B1=0), no ramp limits, no POZ.

    Parameters
    ----------
    x : ndarray, shape (40,)
        Generator outputs in MW.

    Returns
    -------
    cost : float
        Total cost + penalty.
    """
    Power_Demand = 10500.0

    # Audit MED-PERF (CEC2011): consume the module-level hoisted views from
    # _ELD40_DATA1 instead of slicing on every NFE.
    Pmin = _ELD40_PMIN
    Pmax = _ELD40_PMAX
    a = _ELD40_A
    b = _ELD40_B
    c = _ELD40_C
    e = _ELD40_E
    f = _ELD40_F

    # No losses -- reference defines B1=zeros(40,40), B2=zeros(1,40), B3=0,
    # computes x*B1*x'+B2*x'+B3 = 0, then rounds.  Skipped for performance.
    Power_Loss = 0.0

    # Power balance penalty
    balance_pen = abs(Power_Demand + Power_Loss - np.sum(x))

    # Capacity penalty
    cap_pen = _capacity_penalty(x, Pmin, Pmax)

    total_penalty = 1e5 * balance_pen + 1e3 * cap_pen

    # Cost (with valve-point effect)
    cost = float(np.sum(
        a * x**2 + b * x + c + np.abs(e * np.sin(f * (Pmin - x)))
    ))

    return float(cost + total_penalty)


# =========================================================================== #
#  F17: Static Economic Load Dispatch -- 140-unit
# =========================================================================== #

# Data1: [Pmin, Pmax, c, b, a] -- NOTE: reference column order is [Pmin, Pmax, c, b, a]
_ELD140_DATA1 = np.array([
    [71,  119,  1220.645,  61.242,  0.032888],
    [120, 189,  1315.118,  41.095,  0.00828],
    [125, 190,  874.288,   46.31,   0.003849],
    [125, 190,  874.288,   46.31,   0.003849],
    [90,  190,  1976.469,  54.242,  0.042468],
    [90,  190,  1338.087,  61.215,  0.014992],
    [280, 490,  1818.299,  11.791,  0.007039],
    [280, 490,  1133.978,  15.055,  0.003079],
    [260, 496,  1320.636,  13.226,  0.005063],
    [260, 496,  1320.636,  13.226,  0.005063],
    [260, 496,  1320.636,  13.226,  0.005063],
    [260, 496,  1106.539,  14.498,  0.003552],
    [260, 506,  1176.504,  14.651,  0.003901],
    [260, 509,  1176.504,  14.651,  0.003901],
    [260, 506,  1176.504,  14.651,  0.003901],
    [260, 505,  1176.504,  14.651,  0.003901],
    [260, 506,  1017.406,  15.669,  0.002393],
    [260, 506,  1017.406,  15.669,  0.002393],
    [260, 505,  1229.131,  14.656,  0.003684],
    [260, 505,  1229.131,  14.656,  0.003684],
    [260, 505,  1229.131,  14.656,  0.003684],
    [260, 505,  1229.131,  14.656,  0.003684],
    [260, 505,  1267.894,  14.378,  0.004004],
    [260, 505,  1229.131,  14.656,  0.003684],
    [280, 537,  975.926,   16.261,  0.001619],
    [280, 537,  1532.093,  13.362,  0.005093],
    [280, 549,  641.989,   17.203,  0.000993],
    [280, 549,  641.989,   17.203,  0.000993],
    [260, 501,  911.533,   15.274,  0.002473],
    [260, 501,  910.533,   15.212,  0.002547],
    [260, 506,  1074.81,   15.033,  0.003542],
    [260, 506,  1074.81,   15.033,  0.003542],
    [260, 506,  1074.81,   15.033,  0.003542],
    [260, 506,  1074.81,   15.033,  0.003542],
    [260, 500,  1278.46,   13.992,  0.003132],
    [260, 500,  861.742,   15.679,  0.001323],
    [120, 241,  408.834,   16.542,  0.00295],
    [120, 241,  408.834,   16.542,  0.00295],
    [423, 774,  1288.815,  16.518,  0.000991],
    [423, 769,  1436.251,  15.815,  0.001581],
    [3,   19,   699.988,   75.464,  0.90236],
    [3,   28,   134.544,   129.544, 0.110295],
    [160, 250,  3427.912,  56.613,  0.024493],
    [160, 250,  3751.772,  54.451,  0.029156],
    [160, 250,  3918.78,   54.736,  0.024667],
    [160, 250,  3379.58,   58.034,  0.016517],
    [160, 250,  3345.296,  55.981,  0.026584],
    [160, 250,  3138.754,  61.52,   0.00754],
    [160, 250,  3453.05,   58.635,  0.01643],
    [160, 250,  5119.3,    44.647,  0.045934],
    [165, 504,  1898.415,  71.584,  0.000044],
    [165, 504,  1898.415,  71.584,  0.000044],
    [165, 504,  1898.415,  71.584,  0.000044],
    [165, 504,  1898.415,  71.584,  0.000044],
    [180, 471,  2473.39,   85.12,   0.002528],
    [180, 561,  2781.705,  87.682,  0.000131],
    [103, 341,  5515.508,  69.532,  0.010372],
    [198, 617,  3478.3,    78.339,  0.007627],
    [100, 312,  6240.909,  58.172,  0.012464],
    [153, 471,  9960.11,   46.636,  0.039441],
    [163, 500,  3671.997,  76.947,  0.007278],
    [95,  302,  1837.383,  80.761,  0.000044],
    [160, 511,  3108.395,  70.136,  0.000044],
    [160, 511,  3108.395,  70.136,  0.000044],
    [196, 490,  7095.484,  49.84,   0.018827],
    [196, 490,  3392.732,  65.404,  0.010852],
    [196, 490,  7095.484,  49.84,   0.018827],
    [196, 490,  7095.484,  49.84,   0.018827],
    [130, 432,  4288.32,   66.465,  0.03456],
    [130, 432,  13813.001, 22.941,  0.08154],
    [137, 455,  4435.493,  64.314,  0.023534],
    [137, 455,  9750.75,   45.017,  0.035475],
    [195, 541,  1042.366,  70.644,  0.000915],
    [175, 536,  1159.895,  70.959,  0.000044],
    [175, 540,  1159.895,  70.959,  0.000044],
    [175, 538,  1303.99,   70.302,  0.001307],
    [175, 540,  1156.193,  70.662,  0.000392],
    [330, 574,  2118.968,  71.101,  0.000087],
    [160, 531,  779.519,   37.854,  0.000521],
    [160, 531,  829.888,   37.768,  0.000498],
    [200, 542,  2333.69,   67.983,  0.001046],
    [56,  132,  2028.954,  77.838,  0.13205],
    [115, 245,  4412.017,  63.671,  0.096968],
    [115, 245,  2982.219,  79.458,  0.054868],
    [115, 245,  2982.219,  79.458,  0.054868],
    [207, 307,  3174.939,  93.966,  0.014382],
    [207, 307,  3218.359,  94.723,  0.013161],
    [175, 345,  3723.822,  66.919,  0.016033],
    [175, 345,  3551.405,  68.185,  0.013653],
    [175, 345,  4332.615,  60.821,  0.028148],
    [175, 345,  3493.739,  68.551,  0.01347],
    [360, 580,  226.799,   2.842,   0.000064],
    [415, 645,  382.932,   2.946,   0.000252],
    [795, 984,  156.987,   3.096,   0.000022],
    [795, 978,  154.484,   3.04,    0.000022],
    [578, 682,  332.834,   1.709,   0.000203],
    [615, 720,  326.599,   1.668,   0.000198],
    [612, 718,  345.306,   1.789,   0.000215],
    [612, 720,  350.372,   1.815,   0.000218],
    [758, 964,  370.377,   2.726,   0.000193],
    [755, 958,  367.067,   2.732,   0.000197],
    [750, 1007, 124.875,   2.651,   0.000324],
    [750, 1006, 130.785,   2.798,   0.000344],
    [713, 1013, 878.746,   1.595,   0.00069],
    [718, 1020, 827.959,   1.503,   0.00065],
    [791, 954,  432.007,   2.425,   0.000233],
    [786, 952,  445.606,   2.499,   0.000239],
    [795, 1006, 467.223,   2.674,   0.000261],
    [795, 1013, 475.94,    2.692,   0.000259],
    [795, 1021, 899.462,   1.633,   0.000707],
    [795, 1015, 1000.367,  1.816,   0.000786],
    [94,  203,  1269.132,  89.83,   0.014355],
    [94,  203,  1269.132,  89.83,   0.014355],
    [94,  203,  1269.132,  89.83,   0.014355],
    [244, 379,  4965.124,  64.125,  0.030266],
    [244, 379,  4965.124,  64.125,  0.030266],
    [244, 379,  4965.124,  64.125,  0.030266],
    [95,  190,  2243.185,  76.129,  0.024027],
    [95,  189,  2290.381,  81.805,  0.00158],
    [116, 194,  1681.533,  81.14,   0.022095],
    [175, 321,  6743.302,  46.665,  0.07681],
    [2,   19,   394.398,   78.412,  0.953443],
    [4,   59,   1243.165,  112.088, 0.000044],
    [15,  83,   1454.74,   90.871,  0.072468],
    [9,   53,   1011.051,  97.116,  0.000448],
    [12,  37,   909.269,   83.244,  0.599112],
    [10,  34,   689.378,   95.665,  0.244706],
    [112, 373,  1443.792,  91.202,  0.000042],
    [4,   20,   535.553,   104.501, 0.085145],
    [5,   38,   617.734,   83.015,  0.524718],
    [5,   19,   90.966,    127.795, 0.176515],
    [50,  98,   974.447,   77.929,  0.063414],
    [5,   10,   263.81,    92.779,  2.740485],
    [42,  74,   1335.594,  80.95,   0.112438],
    [42,  74,   1033.871,  89.073,  0.041529],
    [41,  105,  1391.325,  161.288, 0.000911],
    [17,  51,   4477.11,   161.829, 0.005245],
    [7,   19,   57.794,    84.972,  0.234787],
    [7,   19,   57.794,    84.972,  0.234787],
    [26,  40,   1258.437,  16.087,  1.111878],
])

# Data2: [Po, UR, DR]
_ELD140_DATA2 = np.array([
    [98.4,   30,   120],
    [134,    30,   120],
    [141.5,  60,   60],
    [183.3,  60,   60],
    [125,    150,  150],
    [91.3,   150,  150],
    [401.1,  180,  300],
    [329.5,  180,  300],
    [386.1,  300,  510],
    [427.3,  300,  510],
    [412.2,  300,  510],
    [370.1,  300,  510],
    [301.8,  600,  600],
    [368,    600,  600],
    [301.9,  600,  600],
    [476.4,  600,  600],
    [283.1,  600,  600],
    [414.1,  600,  600],
    [328,    600,  600],
    [389.4,  600,  600],
    [354.7,  600,  600],
    [262,    600,  600],
    [461.5,  600,  600],
    [371.6,  600,  600],
    [462.6,  300,  300],
    [379.2,  300,  300],
    [530.8,  360,  360],
    [391.9,  360,  360],
    [480.1,  180,  180],
    [319,    180,  180],
    [329.5,  600,  600],
    [333.8,  600,  600],
    [390,    600,  600],
    [432,    600,  600],
    [402,    660,  660],
    [428,    900,  900],
    [178.4,  180,  180],
    [194.1,  180,  180],
    [474,    600,  600],
    [609.8,  600,  600],
    [17.8,   210,  210],
    [6.9,    366,  366],
    [224.3,  702,  702],
    [210,    702,  702],
    [212,    702,  702],
    [200.8,  702,  702],
    [220,    702,  702],
    [232.9,  702,  702],
    [168,    702,  702],
    [208.4,  702,  702],
    [443.9,  1350, 1350],
    [426.0,  1350, 1350],
    [434.1,  1350, 1350],
    [402.5,  1350, 1350],
    [357.4,  1350, 1350],
    [423,    720,  720],
    [220,    720,  720],
    [369.4,  2700, 2700],
    [273.5,  1500, 1500],
    [336,    1656, 1656],
    [432,    2160, 2160],
    [220,    900,  900],
    [410.6,  1200, 1200],
    [422.7,  1200, 1200],
    [351,    1014, 1014],
    [296,    1014, 1014],
    [411.1,  1014, 1014],
    [263.2,  1014, 1014],
    [370.3,  1350, 1350],
    [418.7,  1350, 1350],
    [409.6,  1350, 1350],
    [412,    1350, 1350],
    [423.2,  780,  780],
    [428,    1650, 1650],
    [436,    1650, 1650],
    [428,    1650, 1650],
    [425,    1650, 1650],
    [497.2,  1620, 1620],
    [510,    1482, 1482],
    [470,    1482, 1482],
    [464.1,  1668, 1668],
    [118.1,  120,  120],
    [141.3,  180,  180],
    [132,    120,  180],
    [135,    120,  180],
    [252,    120,  180],
    [221,    120,  180],
    [245.9,  318,  318],
    [247.9,  318,  318],
    [183.6,  318,  318],
    [288,    318,  318],
    [557.4,  18,   18],
    [529.5,  18,   18],
    [800.8,  36,   36],
    [801.5,  36,   36],
    [582.7,  138,  204],
    [680.7,  144,  216],
    [670.7,  144,  216],
    [651.7,  144,  216],
    [921,    48,   48],
    [916.8,  48,   48],
    [911.9,  36,   54],
    [898,    36,   54],
    [905,    30,   30],
    [846.5,  30,   30],
    [850.9,  30,   30],
    [843.7,  30,   30],
    [841.4,  36,   36],
    [835.7,  36,   36],
    [828.8,  36,   36],
    [846,    36,   36],
    [179,    120,  120],
    [120.8,  120,  120],
    [121,    120,  120],
    [317.4,  480,  480],
    [318.4,  480,  480],
    [335.8,  480,  480],
    [151,    240,  240],
    [129.5,  240,  240],
    [130,    120,  120],
    [218.9,  180,  180],
    [5.4,    90,   90],
    [45,     90,   90],
    [20,     300,  300],
    [16.3,   162,  162],
    [20,     114,  114],
    [22.1,   120,  120],
    [125,    1080, 1080],
    [10,     60,   60],
    [13,     66,   66],
    [7.5,    12,   6],
    [53.2,   300,  300],
    [6.4,    6,    6],
    [69.1,   60,   60],
    [49.9,   60,   60],
    [91,     528,  528],
    [41,     300,  300],
    [13.7,   18,   30],
    [7.4,    18,   30],
    [28.6,   72,   120],
])

# Valve-point effect: [unit_no (1-based), e, f] -- only 12 units
_ELD140_DATA3 = np.array([
    [5,   700,  0.080],
    [10,  600,  0.055],
    [15,  800,  0.060],
    [22,  600,  0.050],
    [33,  600,  0.043],
    [40,  600,  0.043],
    [52,  1100, 0.043],
    [70,  1200, 0.030],
    [72,  1000, 0.050],
    [84,  1000, 0.050],
    [119, 600,  0.070],
    [121, 1200, 0.043],
])

# POZ data: [unit_no (1-based), Zone1min, Zone1max, Zone2min, Zone2max, Zone3min, Zone3max]
_ELD140_DATA4 = np.array([
    [8,   250, 280, 305, 335, 420, 450],
    [32,  220, 250, 320, 350, 390, 420],
    [74,  230, 255, 365, 395, 430, 455],
    [136, 50,  75,  85,  95,  0,   0],
])


# Pre-computed constants for F17 (avoids rebuilding on every evaluation).
# These are all derived from the static DATA tables and never change.
_ELD140_Pmin = _ELD140_DATA1[:, 0]
_ELD140_Pmax = _ELD140_DATA1[:, 1]
# Reference column order: [Pmin, Pmax, c, b, a]
_ELD140_c_coeff = _ELD140_DATA1[:, 2]
_ELD140_b_coeff = _ELD140_DATA1[:, 3]
_ELD140_a_coeff = _ELD140_DATA1[:, 4]

# Valve-point e, f coefficients (12 of 140 units have nonzero values)
_ELD140_e_coeff = np.zeros(140)
_ELD140_f_coeff = np.zeros(140)
for _row in _ELD140_DATA3:
    _ELD140_e_coeff[int(_row[0]) - 1] = _row[1]
    _ELD140_f_coeff[int(_row[0]) - 1] = _row[2]

# Ramp limits (constant -- depend on static Initial_Gen from Data2)
_ELD140_Up_Ramp_Limit = np.minimum(
    _ELD140_Pmax, _ELD140_DATA2[:, 0] + _ELD140_DATA2[:, 1]
)
_ELD140_Down_Ramp_Limit = np.maximum(
    _ELD140_Pmin, _ELD140_DATA2[:, 0] - _ELD140_DATA2[:, 2]
)

# POZ arrays: only 4 of 140 units have nonzero zones
_ELD140_POZ_zones = np.zeros((140, 6))
for _row in _ELD140_DATA4:
    _ELD140_POZ_zones[int(_row[0]) - 1, :] = _row[1:]
_ELD140_POZ_all = _ELD140_POZ_zones.T  # (6, 140)
_ELD140_POZ_Lower = _ELD140_POZ_all[0::2, :]  # (3, 140)
_ELD140_POZ_Upper = _ELD140_POZ_all[1::2, :]  # (3, 140)

del _row  # clean up loop variable

for _arr in (
    _ELD140_DATA1, _ELD140_DATA2, _ELD140_DATA3, _ELD140_DATA4,
    _ELD140_Pmin, _ELD140_Pmax, _ELD140_c_coeff, _ELD140_b_coeff, _ELD140_a_coeff,
    _ELD140_e_coeff, _ELD140_f_coeff,
    _ELD140_Up_Ramp_Limit, _ELD140_Down_Ramp_Limit,
    _ELD140_POZ_zones, _ELD140_POZ_all, _ELD140_POZ_Lower, _ELD140_POZ_Upper,
):
    _arr.flags.writeable = False
del _arr


def f17_static_eld_140unit(x: np.ndarray) -> float:
    """F17: Static Economic Load Dispatch, 140-unit.  D=140.

    Minimises fuel cost with valve-point effect (12 units) for 140
    thermal generators, subject to power balance, capacity, ramp-rate,
    and prohibited operating zone constraints.
    No transmission losses (B1=0).

    Parameters
    ----------
    x : ndarray, shape (140,)
        Generator outputs in MW.

    Returns
    -------
    cost : float
        Total cost + penalty.
    """
    Pmin = _ELD140_Pmin
    Pmax = _ELD140_Pmax

    # No losses -- reference defines B1=zeros(140,140), skipped for performance.
    # Power balance penalty
    balance_pen = abs(49342.0 - np.sum(x))

    # Capacity penalty — reference F17 has a typo that omits `sum` on the
    # lower-bound term:
    #   Capacity_Limits_Penalty = (abs(x-Pmin)-(x-Pmin)) + sum(abs(Pmax-x)-(Pmax-x));
    # The first term is a vector (140,), the second is a scalar.  Adding
    # them broadcasts the scalar, so sum(CLP) = sum(lower_vec) + 140 * upper_scalar.
    # This differs from all other ELD functions which sum both terms.
    # We reproduce the reference behaviour exactly for benchmark fidelity.
    _lower_vec = np.abs(x - Pmin) - (x - Pmin)            # (140,) element-wise
    _upper_scalar = float(np.sum(np.abs(Pmax - x) - (Pmax - x)))  # scalar (summed)
    cap_pen = float(np.sum(_lower_vec + _upper_scalar))    # broadcast: sum(lower) + 140*upper

    # Ramp penalty -- reference F17: element-wise, then 1e7*sum(...)
    ramp_pen = _ramp_penalty(x, _ELD140_Down_Ramp_Limit, _ELD140_Up_Ramp_Limit)

    # POZ penalty
    poz_pen = _poz_penalty(x, _ELD140_POZ_Lower, _ELD140_POZ_Upper)

    total_penalty = (
        1e7 * balance_pen
        + 1e5 * cap_pen
        + 1e7 * ramp_pen
        + 1e5 * poz_pen
    )

    # Cost (with valve-point for selected units)
    cost = float(np.sum(
        _ELD140_a_coeff * x**2 + _ELD140_b_coeff * x + _ELD140_c_coeff
        + np.abs(_ELD140_e_coeff * np.sin(_ELD140_f_coeff * (Pmin - x)))
    ))

    return float(cost + total_penalty)
