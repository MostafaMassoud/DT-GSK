"""CEC2011 F18--F20 -- Hydrothermal Economic Load Dispatch (D=96).

Three variants of the hydrothermal scheduling problem with 4 hydro reservoirs
and 1 thermal unit over a 24-hour horizon.  The decision vector encodes the
discharge rates of the 4 hydro units across 24 time periods (4 x 24 = 96).

Case 1 (F18): base case, no prohibited operating zones (POZ), no valve-point
Case 2 (F19): with POZ penalty
Case 3 (F20): POZ defined but multiplied by 0, valve-point cost commented out
              in the reference source -- effectively identical to Case 1

Decision vector layout
----------------------
x[0..95] are discharge rates, reshaped with Fortran (column-major) order into
a (4, 24) matrix: ``q = x.reshape((4, 24), order='F')``.
  - q[i, j] = discharge rate of hydro unit i during hour j
  - Column 0 = all 4 units at hour 0; Column 1 = all 4 units at hour 1; etc.

System topology
---------------
4 hydro reservoirs in cascade (upstream → downstream):
  Unit 0: no upstream,       Delay = 2h
  Unit 1: no upstream,       Delay = 3h
  Unit 2: 2 upstreams (0,1), Delay = 4h   (receives delayed water from 0 and 1)
  Unit 3: 1 upstream (2),    Delay = 0h   (receives delayed water from 2)

Upstream delay indexing: ``src_hour = j - _DELAY_TIME[k]`` where k is the
upstream unit index.  This matches the reference ``All_Discharges(k, j+MaxDelay-Delay_Time(k))``.

Known reference-source quirks preserved for benchmark fidelity
----------------------------------------------
1. ``Capacity_Limits_Penalty_H`` is counted TWICE in ``All_Penalty`` (original bug).
2. ``Capacity_Limits_Penalty_T`` (thermal) is computed but NOT included in
   ``All_Penalty`` (original omission).
3. ``Spillage = 0`` for all hours/units (no spillage modelled).

Reference
---------
Suganthan, P.N. et al., "Problem Definitions and Evaluation Criteria for the
CEC 2011 Special Session on Real-Parameter Optimization", 2011.

Reference source files
  fn_HT_ELD_Case_1.m  (124 lines, base case)
  fn_HT_ELD_Case_2.m  (138 lines, with POZ)
  fn_HT_ELD_Case_3.m  (POZ x 0, valve-point off)
"""

from __future__ import annotations

import numpy as np

# =========================================================================== #
#   Shared constants for all three HT-ELD cases
# =========================================================================== #

_NO_LOAD_HOURS = 24
_NO_UNITS = 4  # 4 hydro units (+ 1 thermal unit, implicit)

_POWER_DEMAND = np.array(
    [1370, 1390, 1360, 1290, 1290, 1410, 1650, 2000, 2240, 2320,
     2230, 2310, 2230, 2200, 2130, 2070, 2130, 2140, 2240, 2280,
     2240, 2120, 1850, 1590],
    dtype=np.float64,
)

# Hydro generation coefficients: c1*v^2 + c2*q^2 + c3*v*q + c4*v + c5*q + c6
_C_COEFFICIENTS = np.array(
    [[-0.0042, -0.42, 0.030, 0.90, 10.0, -50],
     [-0.0040, -0.30, 0.015, 1.14,  9.5, -70],
     [-0.0016, -0.30, 0.014, 0.55,  5.5, -40],
     [-0.0030, -0.31, 0.027, 1.44, 14.0, -90]],
    dtype=np.float64,
)

# Inflow rates: (4, 24) -- one row per hydro unit, one column per hour
_INFLOW_RATE = np.array(
    [[10, 9, 8, 7, 6, 7, 8, 9, 10, 11, 12, 10,
      11, 12, 11, 10, 9, 8, 7, 6, 7, 8, 9, 10],
     [8, 8, 9, 9, 8, 7, 6, 7, 8, 9, 9, 8,
      8, 9, 9, 8, 7, 6, 7, 8, 9, 9, 8, 8],
     [8.1, 8.2, 4, 2, 3, 4, 3, 2, 1, 1, 1, 2,
      4, 3, 3, 2, 2, 2, 1, 1, 2, 2, 1, 0],
     [2.8, 2.4, 1.6, 0, 0, 0, 0, 0, 0, 0, 0, 0,
      0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]],
    dtype=np.float64,
)

_PTMIN, _PTMAX = 500.0, 2500.0

_PHMIN = np.array([0.0, 0.0, 0.0, 0.0], dtype=np.float64)
_PHMAX = np.array([500.0, 500.0, 500.0, 500.0], dtype=np.float64)

_DELAY_TIME = np.array([2, 3, 4, 0], dtype=np.int64)
_NO_UPSTREAMS = np.array([0, 0, 2, 1], dtype=np.int64)

_VMIN = np.array([80.0, 60.0, 100.0, 70.0], dtype=np.float64)
_VMAX = np.array([150.0, 120.0, 240.0, 160.0], dtype=np.float64)
_V_INITIAL = np.array([100.0, 80.0, 170.0, 120.0], dtype=np.float64)
_V_FINAL = np.array([120.0, 70.0, 170.0, 140.0], dtype=np.float64)

_QMIN = np.array([5.0, 6.0, 10.0, 13.0], dtype=np.float64)
_QMAX = np.array([15.0, 15.0, 30.0, 25.0], dtype=np.float64)

# POZ boundaries (lower, upper) per unit -- used by Case 2 and Case 3
_POZ_LOWER = np.array([8.0, 7.0, 22.0, 16.0], dtype=np.float64)
_POZ_UPPER = np.array([9.0, 8.0, 27.0, 18.0], dtype=np.float64)

# Thermal cost coefficients:  a + b*Pt + c*Pt^2
_THERMAL_A = 5000.0
_THERMAL_B = 19.2
_THERMAL_C = 0.002

# Audit LOW (CEC2011): hoist (4, 1) column views used by every HT-ELD call.
# Each view is lightweight, but ``_ht_eld_core`` builds eight of them on every
# NFE -- with CEC2011's 150_000 NFE budget that's ~1.2M throw-away ``ndarray``
# objects per run.  Pre-shape them once and freeze with the rest of the
# constants below.
_PHMIN_COL = _PHMIN[:, None]
_PHMAX_COL = _PHMAX[:, None]
_QMIN_COL = _QMIN[:, None]
_QMAX_COL = _QMAX[:, None]
_VMIN_COL = _VMIN[:, None]
_VMAX_COL = _VMAX[:, None]
_POZ_LOWER_COL = _POZ_LOWER[:, None]
_POZ_UPPER_COL = _POZ_UPPER[:, None]
_V_INITIAL_COL = _V_INITIAL[:, None]

# Audit LOW (CEC2011): freeze module-level constants so a wayward in-place
# mutation in any caller cannot silently corrupt the next benchmark call.
# Mirrors the existing freeze pattern in problems_antenna.py / problems_power.py.
for _arr in (
    _POWER_DEMAND,
    _C_COEFFICIENTS,
    _INFLOW_RATE,
    _PHMIN, _PHMAX,
    _DELAY_TIME, _NO_UPSTREAMS,
    _VMIN, _VMAX, _V_INITIAL, _V_FINAL,
    _QMIN, _QMAX,
    _POZ_LOWER, _POZ_UPPER,
    _PHMIN_COL, _PHMAX_COL, _QMIN_COL, _QMAX_COL,
    _VMIN_COL, _VMAX_COL, _POZ_LOWER_COL, _POZ_UPPER_COL,
    _V_INITIAL_COL,
):
    _arr.flags.writeable = False
del _arr


# =========================================================================== #
#   Core computation (shared by all three cases)
# =========================================================================== #

def _ht_eld_core(
    x: np.ndarray,
    use_poz: bool,
    poz_multiplier: float,
) -> float:
    """Evaluate hydrothermal economic load dispatch objective + penalty.

    Parameters
    ----------
    x : ndarray, shape (96,)
        Discharge rates reshaped to (4, 24) -- 4 hydro units x 24 hours.
    use_poz : bool
        Whether to compute the prohibited operating zone penalty.
    poz_multiplier : float
        Coefficient multiplying the POZ penalty term (1e5 for Case 2,
        0 for Case 3).

    Returns
    -------
    float
        Total cost including constraint-violation penalties.
    """
    # ------------------------------------------------------------------ #
    #  Reshape decision vector into discharge matrix (4 units x 24 hours)
    # ------------------------------------------------------------------ #
    # Reference: reshape(Input_Vector, No_of_Units, No_of_Load_Hours)
    # NumPy reshape with 'F' (Fortran/column-major) order matches the reference
    q = x.reshape((_NO_UNITS, _NO_LOAD_HOURS), order='F')

    # ------------------------------------------------------------------ #
    #  Water balance: compute storage volumes (fully vectorized)
    # ------------------------------------------------------------------ #
    # V(i, j+1) = V(i,j) + upstream_carry(i,j) - q(i,j) + inflow(i,j)
    # spillage = 0 in all three reference cases.
    #
    # Key insight: upstream_carry depends only on q (decision variable),
    # not on v (state).  So we precompute the entire (4, 24) upstream
    # matrix via delayed-slicing, then express v as a cumulative sum:
    #   v[:, 1:] = V_INITIAL + cumsum(upstream - q + inflow, axis=1)
    # This eliminates the 24-iteration Python loop entirely.
    upstream = np.zeros((_NO_UNITS, _NO_LOAD_HOURS), dtype=np.float64)
    for i in range(_NO_UNITS):
        n_up = _NO_UPSTREAMS[i]
        if n_up > 0:
            for k in range(i - n_up, i):
                delay = _DELAY_TIME[k]
                # q[k, j - delay] for j >= delay, else 0
                if delay < _NO_LOAD_HOURS:
                    upstream[i, delay:] += q[k, :_NO_LOAD_HOURS - delay]

    # delta[:, j] = net volume change at hour j
    delta = upstream - q + _INFLOW_RATE  # (4, 24)

    v = np.empty((_NO_UNITS, _NO_LOAD_HOURS + 1), dtype=np.float64)
    v[:, 0] = _V_INITIAL
    v[:, 1:] = _V_INITIAL_COL + np.cumsum(delta, axis=1)

    # ------------------------------------------------------------------ #
    #  Hydro power generation
    # ------------------------------------------------------------------ #
    # Ph(i,j) = c1*v^2 + c2*q^2 + c3*v*q + c4*v + c5*q + c6
    # Reference: v = Storage_Volume(:,j+1)' — uses END-of-hour volumes
    # (after water balance update), not start-of-hour.
    v_hour = v[:, 1:_NO_LOAD_HOURS + 1]  # (4, 24) — end-of-hour volumes
    c = _C_COEFFICIENTS

    ph = (
        c[:, 0:1] * v_hour**2
        + c[:, 1:2] * q**2
        + c[:, 2:3] * v_hour * q
        + c[:, 3:4] * v_hour
        + c[:, 4:5] * q
        + c[:, 5:6]
    )
    ph = np.maximum(ph, 0.0)  # Ph = max(Ph, 0)

    # ------------------------------------------------------------------ #
    #  Thermal generation and total cost
    # ------------------------------------------------------------------ #
    pt = _POWER_DEMAND - ph.sum(axis=0)  # (24,)
    cost = np.sum(_THERMAL_A + _THERMAL_B * pt + _THERMAL_C * pt**2)

    # ------------------------------------------------------------------ #
    #  Penalty: power balance violation
    # ------------------------------------------------------------------ #
    # Balance penalty = sum of |demand - (sum_Ph + Pt)| over hours
    # Since Pt = demand - sum_Ph, balance is always 0 by construction.
    # The reference still computes it; keep for fidelity.
    balance_penalty = np.sum(
        np.abs(_POWER_DEMAND - (ph.sum(axis=0) + pt))
    )

    # ------------------------------------------------------------------ #
    #  Penalty: hydro capacity limits
    #  Reference: sum(abs(Ph-PHmin)-(Ph-PHmin)) + sum(abs(PHmax-Ph)-(PHmax-Ph))
    #  which equals 2*sum(max(PHmin-Ph,0)) + 2*sum(max(Ph-PHmax,0))
    # ------------------------------------------------------------------ #
    cap_h_penalty = float(
        np.sum(np.abs(ph - _PHMIN_COL) - (ph - _PHMIN_COL))
        + np.sum(np.abs(_PHMAX_COL - ph) - (_PHMAX_COL - ph))
    )

    # ------------------------------------------------------------------ #
    #  Penalty: thermal capacity limits (computed but NOT used in
    #  All_Penalty — matches the reference which also computes but omits it)
    # ------------------------------------------------------------------ #
    cap_t_penalty = float(  # noqa: F841 - computed but omitted by the reference equation.
        np.sum(np.abs(pt - _PTMIN) - (pt - _PTMIN))
        + np.sum(np.abs(_PTMAX - pt) - (_PTMAX - pt))
    )

    # ------------------------------------------------------------------ #
    #  Penalty: discharge limits
    #  Reference: sum(abs(q-Qmin)-(q-Qmin)) + sum(abs(Qmax-q)-(Qmax-q))
    # ------------------------------------------------------------------ #
    discharge_penalty = float(
        np.sum(np.abs(q - _QMIN_COL) - (q - _QMIN_COL))
        + np.sum(np.abs(_QMAX_COL - q) - (_QMAX_COL - q))
    )

    # ------------------------------------------------------------------ #
    #  Penalty: storage volume limits
    #  Reference: sum(abs(v-Vmin)-(v-Vmin)) + sum(abs(Vmax-v)-(Vmax-v))
    # ------------------------------------------------------------------ #
    v_check = v[:, 1:]  # volumes at end of each hour (4, 24)
    storage_penalty = float(
        np.sum(np.abs(v_check - _VMIN_COL) - (v_check - _VMIN_COL))
        + np.sum(np.abs(_VMAX_COL - v_check) - (_VMAX_COL - v_check))
    )

    # ------------------------------------------------------------------ #
    #  Penalty: prohibited operating zones (vectorised)
    #  Reference: if POZ_Lower(i) < q(i,j) < POZ_Upper(i),
    #          penalty += min(q-lower, upper-q)
    # ------------------------------------------------------------------ #
    poz_penalty = 0.0
    if use_poz:
        # _POZ_LOWER_COL / _POZ_UPPER_COL are pre-shaped (4, 1) views frozen
        # at module load -- broadcast over 24 hours without re-allocating.
        inside = (_POZ_LOWER_COL < q) & (q < _POZ_UPPER_COL)  # (4, 24) boolean
        if np.any(inside):
            # Use broadcast_to instead of repeat to avoid copying (4,1)→(4,24).
            lo_bc = np.broadcast_to(_POZ_LOWER_COL, q.shape)
            hi_bc = np.broadcast_to(_POZ_UPPER_COL, q.shape)
            poz_penalty = float(np.sum(
                np.minimum(q[inside] - lo_bc[inside],
                           hi_bc[inside] - q[inside])
            ))

    # ------------------------------------------------------------------ #
    #  Penalty: reservoir boundary conditions (initial & final volume)
    # ------------------------------------------------------------------ #
    # Reference: 1e6 * (|V(:,1) - V_Initial| + |V(:,end) - V_Final|)
    reservoir_penalty = 1e6 * (
        np.sum(np.abs(v[:, 0] - _V_INITIAL))
        + np.sum(np.abs(v[:, _NO_LOAD_HOURS] - _V_FINAL))
    )

    # ------------------------------------------------------------------ #
    #  Aggregate penalty
    # ------------------------------------------------------------------ #
    # Reference (all three cases):
    #   All_Penalty = 1e4*balance + 1e4*cap_H + 1e4*cap_H
    #                 + 1e4*discharge + 1e5*storage + poz_mult*POZ
    #
    # NOTE: cap_H is counted TWICE in the reference code -- this is a quirk
    #       in the original reference that we reproduce exactly.
    all_penalty = (
        1e4 * balance_penalty
        + 1e4 * cap_h_penalty       # first cap_H term
        + 1e4 * cap_h_penalty       # second cap_H term (reference-source quirk preserved for benchmark fidelity)
        + 1e4 * discharge_penalty
        + 1e5 * storage_penalty
        + poz_multiplier * poz_penalty
    )

    return cost + all_penalty + reservoir_penalty


# =========================================================================== #
#   Public API
# =========================================================================== #

def f18_hydrothermal_case1(x: np.ndarray) -> float:
    """F18: Hydrothermal Scheduling -- Case 1 (no POZ, no valve-point).

    Minimises thermal generation cost subject to water-balance, capacity,
    discharge, and storage-volume constraints.  The 96-element decision
    vector encodes discharge rates for 4 hydro units over 24 hours.

    Parameters
    ----------
    x : ndarray, shape (96,)
        Discharge rates: reshaped internally to (4, 24).

    Returns
    -------
    float
        Total cost including constraint-violation penalties.
    """
    return _ht_eld_core(x, use_poz=False, poz_multiplier=0.0)


def f19_hydrothermal_case2(x: np.ndarray) -> float:
    """F19: Hydrothermal Scheduling -- Case 2 (with POZ, no valve-point).

    Same as Case 1 but adds a prohibited operating zone penalty for each
    hydro unit.  Discharges inside the zone [lower, upper] incur an
    additional cost proportional to the distance to the nearest boundary.

    Parameters
    ----------
    x : ndarray, shape (96,)
        Discharge rates: reshaped internally to (4, 24).

    Returns
    -------
    float
        Total cost including constraint-violation and POZ penalties.
    """
    return _ht_eld_core(x, use_poz=True, poz_multiplier=1e5)


def f20_hydrothermal_case3(x: np.ndarray) -> float:
    """F20: Hydrothermal Scheduling -- Case 3 (POZ x 0, valve-point off).

    POZ zones are defined but multiplied by 0 in the penalty formula.
    Valve-point loading effect is described in the problem title but
    commented out in the original reference code -- the cost formula is
    identical to Case 1.

    Parameters
    ----------
    x : ndarray, shape (96,)
        Discharge rates: reshaped internally to (4, 24).

    Returns
    -------
    float
        Total cost including constraint-violation penalties.
    """
    return _ht_eld_core(x, use_poz=True, poz_multiplier=0.0)
