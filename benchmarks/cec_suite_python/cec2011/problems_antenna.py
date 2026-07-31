"""CEC2011 F10 -- Circular Antenna Array Design (D=12).

Optimises excitation amplitudes (6) and phases (6) of a 12-element circular
antenna array to minimise side-lobe level (SLL) while controlling beamwidth,
null placement, and maximum-gain direction.

Reference
---------
Suganthan, P.N. et al., "Problem Definitions and Evaluation Criteria for the
CEC 2011 Special Session on Real-Parameter Optimization", 2011.
"""

from __future__ import annotations

import numpy as np

_PI = 3.141592654  # match reference precision

# Audit MED-PERF-01 (CEC2011): hoist deterministic constants used by every
# F10 call so the inner sweep stops paying for ``np.linspace``, the
# degrees-to-radians conversion, and ``np.sin(trap_phi - PI/2)`` on every
# evaluation.  Each value below is a pure function of the F10 problem
# definition (D=12, 300-point sweep, 50-point trapezoidal grid).
_PI_OVER_180: float = _PI / 180.0
_F10_NUM1: int = 300
_F10_PHI_ARR_DEG: np.ndarray = np.linspace(0.0, 360.0, _F10_NUM1)
_F10_PHI_ARR_RAD: np.ndarray = _F10_PHI_ARR_DEG * _PI_OVER_180
_F10_N1: int = 50
_F10_TRAP_PHI: np.ndarray = np.linspace(0.0, 2.0 * _PI, _F10_N1 + 1)
_F10_TRAP_SIN: np.ndarray = np.sin(_F10_TRAP_PHI - _PI / 2.0)
_F10_H: float = (2.0 * _PI) / _F10_N1
for _arr in (_F10_PHI_ARR_DEG, _F10_PHI_ARR_RAD, _F10_TRAP_PHI, _F10_TRAP_SIN):
    _arr.flags.writeable = False
del _arr


def _array_factor_batch(
    x1: np.ndarray,
    phi_arr: np.ndarray,
    phi_desired: float,
    distance: float,
    dim: int,
) -> np.ndarray:
    """Compute array factor magnitude at multiple angles simultaneously.

    Parameters
    ----------
    x1 : ndarray, shape (dim,)
        Antenna element weights: first half are amplitudes, second half
        are phases (in degrees).
    phi_arr : ndarray, shape (N,)
        Observation angles in radians.
    phi_desired : float
        Desired beam direction in degrees.
    distance : float
        Inter-element spacing in wavelengths.
    dim : int
        Total number of design variables.

    Returns
    -------
    af : ndarray, shape (N,)
        Magnitude of the array factor at each angle.
    """
    half = dim // 2
    phi_des_rad = phi_desired * _PI_OVER_180

    # Element indices 0..dim-1
    i1 = np.arange(dim)
    delphi = 2.0 * _PI * i1 / dim                        # (dim,)

    # shi[n, el] for all angles and elements at once
    shi = (
        np.cos(phi_arr[:, None] - delphi[None, :])
        - np.cos(phi_des_rad - delphi[None, :])
    ) * dim * distance                                    # (N, dim)

    # Symmetric array: amplitudes mirror, phases negate across halfpoint.
    #   i1 < half:  amp = x1[i1],     phase = +x1[half + i1] * PI/180
    #   i1 >= half: amp = x1[i1-half], phase = -x1[half + (i1-half)] * PI/180
    amps = np.empty(dim)
    phases = np.empty(dim)
    amps[:half] = x1[:half]
    amps[half:] = x1[:half]
    phases[:half] = x1[half:] * _PI_OVER_180
    phases[half:] = -x1[half:] * _PI_OVER_180

    arg = shi + phases[None, :]                            # (N, dim)
    y_re = np.dot(np.cos(arg), amps)                       # (N,)
    y_im = np.dot(np.sin(arg), amps)                       # (N,)

    return np.sqrt(y_re * y_re + y_im * y_im)


def _array_factor_scalar(x1: np.ndarray, phi: float) -> float:
    """Reference-order scalar ``array_factorcir`` used for sensitive ties."""
    dim = 12
    half = dim // 2
    y_re = 0.0
    y_im = 0.0
    phi_des_rad = 180.0 * _PI_OVER_180

    for i1 in range(1, half + 1):
        delphi = (2.0 * _PI) * float(i1 - 1) / 12.0
        shi = np.cos(phi - delphi) - np.cos(phi_des_rad - delphi)
        shi = (shi * 12.0) * 0.5
        y_re += x1[i1 - 1] * np.cos(shi + x1[half + i1 - 1] * _PI_OVER_180)

    for i1 in range(half + 1, dim + 1):
        delphi = (2.0 * _PI) * float(i1 - 1) / 12.0
        shi = np.cos(phi - delphi) - np.cos(phi_des_rad - delphi)
        shi = (shi * 12.0) * 0.5
        y_re += x1[i1 - half - 1] * np.cos(shi - x1[i1 - 1] * _PI_OVER_180)

    for i1 in range(1, half + 1):
        delphi = (2.0 * _PI) * float(i1 - 1) / 12.0
        shi = np.cos(phi - delphi) - np.cos(phi_des_rad - delphi)
        shi = (shi * 12.0) * 0.5
        y_im += x1[i1 - 1] * np.sin(shi + x1[half + i1 - 1] * _PI_OVER_180)

    for i1 in range(half + 1, dim + 1):
        delphi = (2.0 * _PI) * float(i1 - 1) / 12.0
        shi = np.cos(phi - delphi) - np.cos(phi_des_rad - delphi)
        shi = (shi * 12.0) * 0.5
        y_im += x1[i1 - half - 1] * np.sin(shi - x1[i1 - 1] * _PI_OVER_180)

    return float(np.sqrt(y_re * y_re + y_im * y_im))


def f10_antenna_array(x: np.ndarray) -> float:
    """F10: Circular Antenna Array Design.  D=12 (6 amplitudes + 6 phases).

    Minimises a composite objective combining side-lobe level (SLL),
    beamwidth, null depth, and beam-pointing error.

    Parameters
    ----------
    x : ndarray, shape (12,)
        Design vector -- x[0:6] are excitation amplitudes in [0.2, 1.0],
        x[6:12] are excitation phases in [-180, 180] degrees.

    Returns
    -------
    cost : float
        Composite objective value (lower is better).
    """
    null = np.array([50.0, 120.0])
    phi_desired = 180.0
    distance = 0.5
    dim = len(x)

    # ------------------------------------------------------------------
    # Sweep array factor over 0-360 degrees (vectorised).  Audit
    # MED-PERF-01: ``phi_arr_deg`` / ``phi_arr_rad`` are deterministic
    # constants of the F10 problem and live at module scope so each
    # evaluation skips the linspace + degrees-to-radians conversion.
    # ------------------------------------------------------------------
    num1 = _F10_NUM1
    phi_arr_deg = _F10_PHI_ARR_DEG
    phi_arr_rad = _F10_PHI_ARR_RAD
    yax = _array_factor_batch(x, phi_arr_rad, phi_desired, distance, dim)
    # The reference evaluates endpoints with scalar summation.  For symmetric
    # designs this decides whether 360 degrees is counted as a side lobe.
    yax[0] = _array_factor_scalar(x, float(phi_arr_rad[0]))
    yax[-1] = _array_factor_scalar(x, float(phi_arr_rad[-1]))
    phi_ref = int(np.argmax(yax))
    maxi = yax[phi_ref]
    phizero = phi_arr_deg[phi_ref]

    # ------------------------------------------------------------------
    # Detect side-lobes (local maxima)
    # ------------------------------------------------------------------
    sidelobes: list[float] = []
    if yax[0] > yax[-1] and yax[0] > yax[1]:
        sidelobes.append(float(yax[0]))
    if yax[-1] > yax[0] and yax[-1] > yax[-2]:
        sidelobes.append(float(yax[-1]))
    for i in range(1, num1 - 1):
        if yax[i] > yax[i + 1] and yax[i] > yax[i - 1]:
            sidelobes.append(float(yax[i]))
    sidelobes.sort(reverse=True)

    # Guard: the reference also crashes if <2 sidelobes (degenerate pattern).
    # Return worst-case SLL (0 dB) to keep the optimizer running.
    if len(sidelobes) < 2:
        y = 1.0
    else:
        y = sidelobes[1] / maxi  # SLL ratio (second highest / max)
    # Guard: y should be in (0, 1] for valid SLL. Clamp to avoid log10
    # domain errors from numerical noise (y slightly > 1 or y ≤ 0).
    y = min(max(y, 1e-30), 1.0)
    sllreturn = 20.0 * np.log10(y)

    # ------------------------------------------------------------------
    # Beamwidth (first-null beamwidth)
    # ------------------------------------------------------------------
    upper_bound = 180.0
    lower_bound = 180.0
    for i in range(1, num1 // 2):
        if phi_ref + i > num1 - 2:
            upper_bound = 180.0
            break
        if (
            yax[phi_ref + i] < yax[phi_ref + i - 1]
            and yax[phi_ref + i] < yax[phi_ref + i + 1]
        ):
            upper_bound = phi_arr_deg[phi_ref + i] - phi_arr_deg[phi_ref]
            break
    for i in range(1, num1 // 2):
        if phi_ref - i < 1:
            lower_bound = 180.0
            break
        if (
            yax[phi_ref - i] < yax[phi_ref - i - 1]
            and yax[phi_ref - i] < yax[phi_ref - i + 1]
        ):
            lower_bound = phi_arr_deg[phi_ref] - phi_arr_deg[phi_ref - i]
            break
    bwfn = upper_bound + lower_bound

    # ------------------------------------------------------------------
    # Null control.  The angles are passed raw as radians in the reference.
    # ------------------------------------------------------------------
    y1 = (
        _array_factor_scalar(x, float(null[0])) / maxi
        + _array_factor_scalar(x, float(null[1])) / maxi
    )

    # ------------------------------------------------------------------
    # Directivity via trapezoidal integration (vectorised).  Audit
    # MED-PERF-01: the ``trap_phi`` grid, the ``sin(trap_phi - PI/2)``
    # weights, and the integration step ``h`` are pure constants of the
    # 50-point quadrature and live at module scope so each evaluation
    # only pays for the array-factor sweep itself.
    # ------------------------------------------------------------------
    N1 = _F10_N1  # noqa: F841 - retained for reference-equation parity.
    trap_phi = _F10_TRAP_PHI
    trap_af = _array_factor_batch(x, trap_phi, phi_desired, distance, dim)
    trap_vals = np.abs(trap_af * trap_af * _F10_TRAP_SIN)
    h = _F10_H
    uavg = (h / 2.0) * (trap_vals[0] + trap_vals[-1] + 2.0 * np.sum(trap_vals[1:-1]))  # noqa: F841
    # y2 = abs(2*PI*maxi^2 / uavg)  — directivity, kept for reference compatibility

    y3 = abs(phizero - phi_desired)
    if y3 < 5.0:
        y3 = 0.0

    # ------------------------------------------------------------------
    # Composite cost
    # ------------------------------------------------------------------
    result = 0.0
    if bwfn > 80.0:
        result += abs(bwfn - 80.0)
    result = sllreturn + result + y1 + y3

    return float(result)
