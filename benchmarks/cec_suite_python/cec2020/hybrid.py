"""CEC2020 hybrid functions F5–F7.

Pipeline: shift_rotate(shrink=1.0) → shuffle → partition → Σ sub-functions + bias.

Unlike CEC2017/2022 where shrink rates are baked into basic functions, CEC2020
applies shrink rates EXTERNALLY via the _apply() helper. This is because CEC2020
basic functions expect pre-scaled input (matching the C++ pattern where sr_func
handles scaling). The SHRINK_RATES dict in transforms.py is the single source
of truth for these rates.

Function composition:
  F5 hf01: schwefel(0.3) + rastrigin(0.3) + ellips(0.4)     bias=1700, oddball_first=True
  F6 hf06: escaffer6(0.2) + hgbat(0.2) + rosenbrock(0.3) + schwefel(0.3)  bias=1600
  F7 hf05: escaffer6(0.1) + hgbat(0.2) + rosenbrock(0.2)
           + schwefel(0.2) + ellips(0.3)  bias=2100, oddball_first=True

oddball_first: CEC2020 F5/F7 use a different partition scheme where the FIRST
group gets the remainder (D - Σceil(others)) instead of the last. This matches
the C++ which computes G_nx[0] = D - sum(G_nx[1:]) for these functions.

Valid dimensions: {5, 10, 15, 20, 30, 50, 100} (no D=2: hybrids need partitions).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from collections.abc import Callable

from . import basic
from .transforms import SHRINK_RATES, shift_rotate, shuffle_and_partition

# Audit LOW (CEC2020): hoist the per-function ``SHRINK_RATES[name]`` dict
# lookups to module-level constants.  Each F5..F7 hybrid otherwise pays
# 3..5 string-keyed dict lookups per NFE call (10000*D NFEs per run);
# binding them once at import time collapses all of that into a closure
# read on the local scope.
_SR_SCHWEFEL   = SHRINK_RATES['schwefel']
_SR_RASTRIGIN  = SHRINK_RATES['rastrigin']
_SR_ELLIPS     = SHRINK_RATES['ellips']
_SR_ESCAFFER6  = SHRINK_RATES['escaffer6']
_SR_HGBAT      = SHRINK_RATES['hgbat']
_SR_ROSENBROCK = SHRINK_RATES['rosenbrock']

# Pre-bound partition specs (the literal lists were rebuilt on every NFE).
_F5_GP = [0.3, 0.3, 0.4]
_F6_GP = [0.2, 0.2, 0.3, 0.3]
_F7_GP = [0.1, 0.2, 0.2, 0.2, 0.3]


def _apply(func: Callable[..., np.ndarray], part: np.ndarray, shrink: float) -> np.ndarray:
    """Apply sub-function: scale partition by shrink, then compute.

    Empty partitions (0 columns) can occur at small D with oddball_first=True
    (e.g., F7 at D=5: escaffer6 gets 0 columns). Return zeros in that case.
    """
    if part.shape[-1] == 0:
        return np.zeros(part.shape[0])
    z = part * shrink
    return func(z)


def _escaffer6_empty_guard(z_before_shuffle: np.ndarray) -> np.ndarray:
    """Return the C++ guard-slot term for F7/D5's zero-width first slice."""
    s2 = z_before_shuffle[:, 0] ** 2
    t1 = np.sin(np.sqrt(s2)) ** 2
    t2 = (1.0 + 0.001 * s2) ** 2
    return 0.5 + (t1 - 0.5) / t2


# ---------- F5: hf01 (bias=1700) ----------
def f5_hf01(x: np.ndarray, Os: np.ndarray, Mr: np.ndarray, SS: np.ndarray,
            *, Mr_T: np.ndarray | None = None) -> np.ndarray:
    """Hybrid 1: schwefel(0.3) + rastrigin(0.3) + ellips(0.4). Bias=1700."""
    z = shift_rotate(x, Os, Mr, 1.0, 1, 1, Mr_T=Mr_T)
    parts = shuffle_and_partition(z, SS, _F5_GP, oddball_first=True)

    f = (_apply(basic.schwefel, parts[0], _SR_SCHWEFEL)
         + _apply(basic.rastrigin, parts[1], _SR_RASTRIGIN)
         + _apply(basic.ellips, parts[2], _SR_ELLIPS))
    return f + 1700.0


# ---------- F6: hf06 (bias=1600) ----------
def f6_hf06(x: np.ndarray, Os: np.ndarray, Mr: np.ndarray, SS: np.ndarray,
            *, Mr_T: np.ndarray | None = None) -> np.ndarray:
    """Hybrid 6: escaffer6(0.2) + hgbat(0.2) + rosenbrock(0.3) + schwefel(0.3). Bias=1600."""
    z = shift_rotate(x, Os, Mr, 1.0, 1, 1, Mr_T=Mr_T)
    parts = shuffle_and_partition(z, SS, _F6_GP, oddball_first=False)

    f = (_apply(basic.escaffer6, parts[0], _SR_ESCAFFER6)
         + _apply(basic.hgbat, parts[1], _SR_HGBAT)
         + _apply(basic.rosenbrock, parts[2], _SR_ROSENBROCK)
         + _apply(basic.schwefel, parts[3], _SR_SCHWEFEL))
    return f + 1600.0


# ---------- F7: hf05 (bias=2100) ----------
def f7_hf05(x: np.ndarray, Os: np.ndarray, Mr: np.ndarray, SS: np.ndarray,
            *, Mr_T: np.ndarray | None = None) -> np.ndarray:
    """Hybrid 5: escaffer6(0.1) + hgbat(0.2) + rosenbrock(0.2)
    + schwefel(0.2) + ellips(0.3). Bias=2100."""
    z = shift_rotate(x, Os, Mr, 1.0, 1, 1, Mr_T=Mr_T)
    parts = shuffle_and_partition(z, SS, _F7_GP, oddball_first=True)
    escaffer6_value = (
        _escaffer6_empty_guard(z)
        if parts[0].shape[-1] == 0
        else _apply(basic.escaffer6, parts[0], _SR_ESCAFFER6)
    )

    f = (escaffer6_value
         + _apply(basic.hgbat, parts[1], _SR_HGBAT)
         + _apply(basic.rosenbrock, parts[2], _SR_ROSENBROCK)
         + _apply(basic.schwefel, parts[3], _SR_SCHWEFEL)
         + _apply(basic.ellips, parts[4], _SR_ELLIPS))
    return f + 2100.0
