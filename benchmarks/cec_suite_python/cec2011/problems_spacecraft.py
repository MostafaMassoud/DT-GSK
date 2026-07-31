"""CEC2011 F21--F22 -- Spacecraft Trajectory Optimisation (MGA-DSM).

F21 (Messenger) and F22 (Cassini-Huygens) minimise the total delta-V of
interplanetary trajectories using Multiple Gravity Assist with Deep Space
Maneuvers (MGA-DSM).

Reference
---------
Suganthan, P.N. et al., "Problem Definitions and Evaluation Criteria for the
CEC 2011 Special Session on Real-Parameter Optimization", 2011.

Reference source files: mga_dsm.m (shared solver), messenger_full.m, cassini2.m.
"""

from __future__ import annotations

import numpy as np

from .orbital_mechanics import mga_dsm

# Audit quick-win (CEC2011 F21/F22): the planet sequences are constant, but
# passing them as Python lists made ``_mga_dsm_core`` re-run
# ``np.asarray(sequence, dtype=int)`` (a fresh list->array conversion) on
# every NFE.  Pre-convert once here with the *same* constructor and dtype
# the per-call conversion produced (C-contiguous ``np.int_``, i.e. int64),
# so the solver-side ``np.asarray`` becomes a no-op returning this object.
# The solver only reads the sequence (len / abs / indexing), never writes;
# the arrays are frozen to make any future in-place write fail loudly.
_F21_SEQUENCE = np.asarray([3, 2, 2, 1, 1, 1, 1], dtype=int)
_F21_SEQUENCE.flags.writeable = False
_F22_SEQUENCE = np.asarray([3, 2, 2, 3, 5, 6], dtype=int)
_F22_SEQUENCE.flags.writeable = False


def f21_messenger(x: np.ndarray) -> float:
    """F21: Messenger Spacecraft Trajectory Optimisation.  D=26.

    Minimises total delta-V for a multi-gravity-assist trajectory
    (Earth--Venus--Venus--Mercury--Mercury--Mercury--Mercury insertion).

    Parameters
    ----------
    x : ndarray, shape (26,)
        Decision variables:

        - ``x[0]``:     departure epoch (MJD2000), [1900, 2300]
        - ``x[1]``:     escape velocity magnitude, [2.5, 4.05] km/s
        - ``x[2:4]``:   velocity direction parameters, [0, 1]
        - ``x[4:10]``:  time-of-flight per leg, [100, 500--600] days
        - ``x[10:16]``: DSM fraction, [0.01, 0.99]
        - ``x[16:21]``: flyby radii, [1.05--1.1, 6] planetary radii
        - ``x[21:26]``: flyby rotation angles, [-pi, pi] rad

    Returns
    -------
    float
        Total delta-V in km/s.
    """
    return mga_dsm(
        x,
        sequence=_F21_SEQUENCE,
        objective_type="orbit insertion",
        rp_target=2640.0,
        e_target=0.704,
    )


def f22_cassini_huygens(x: np.ndarray) -> float:
    """F22: Cassini-Huygens Spacecraft Trajectory Optimisation.  D=22.

    Minimises total delta-V for an Earth--Venus--Venus--Earth--Jupiter--Saturn
    transfer trajectory.

    Parameters
    ----------
    x : ndarray, shape (22,)
        Decision variables:

        - ``x[0]``:     departure epoch (MJD2000), [-1000, 0]
        - ``x[1]``:     escape velocity, [3, 5] km/s
        - ``x[2:4]``:   direction parameters, [0, 1]
        - ``x[4:8]``:   time-of-flight per leg, [100--500, 400--2200] days
        - ``x[8:12]``:  DSM fractions, [0.01, 0.9]
        - ``x[12:16]``: flyby radii, [1.05--1.7, 6.5--291] planetary radii
        - ``x[16:22]``: rotation angles, [-pi, pi] rad

    Returns
    -------
    float
        Total delta-V in km/s.
    """
    return mga_dsm(
        x,
        sequence=_F22_SEQUENCE,
        objective_type="total DV rndv",
    )
