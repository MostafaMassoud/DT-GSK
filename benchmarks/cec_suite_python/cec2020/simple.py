"""CEC2020 simple functions F1–F4 (shifted + rotated single base functions).

Each function receives pre-sliced shift (Os) and rotation (Mr) arrays from
the calling layer (functions.py), applies shift_rotate, then calls the
basic module function and adds a bias.

XS-01: all functions now accept an optional ``Mr_T`` keyword argument
(a C-contiguous pre-transposed rotation matrix) that is forwarded to
:func:`shift_rotate` for the NumPy fallback path.

Function mapping:
  F1: bent_cigar       shrink=1.0,        s_flag=1, r_flag=1, bias=100
  F2: schwefel         shrink=1000/100,   s_flag=1, r_flag=1, bias=1100
  F3: bi_rastrigin     custom logic,      s_flag=1, r_flag=1, bias=700
  F4: grie_rosen       shrink=5/100,      s_flag=0, r_flag=0, bias=1900

F1 and F2 delegate to basic module functions to maintain a single source
of truth for the mathematical formulas. F3 (Lunacek Bi-Rastrigin) and F4
(Griewank-Rosenbrock) have custom shift/rotate handling that differs from
the standard pattern:
  - F3: applies sign-flip based on shift vector direction, custom mu0/mu1 logic
  - F4: uses s_flag=0 (no shift) and r_flag=0 (no rotation) — the shrink
    scaling and +1 origin shift are applied manually

Valid dimensions: {2, 5, 10, 15, 20, 30, 50, 100}.
"""

from __future__ import annotations

import numpy as np

from . import basic
from .transforms import shift_rotate


# ---------- F1: Shifted and Rotated Bent Cigar (bias=100) ----------
def f1_bent_cigar(x: np.ndarray, Os: np.ndarray, Mr: np.ndarray,
                  *, Mr_T: np.ndarray | None = None) -> np.ndarray:
    """F1: Bent Cigar (shrink=1.0, s_flag=1, r_flag=1). Bias=100."""
    z = shift_rotate(x, Os, Mr, 1.0, 1, 1, Mr_T=Mr_T)
    return basic.bent_cigar(z) + 100.0


# ---------- F2: Shifted and Rotated Schwefel (bias=1100) ----------
def f2_schwefel(x: np.ndarray, Os: np.ndarray, Mr: np.ndarray,
                *, Mr_T: np.ndarray | None = None) -> np.ndarray:
    """F2: Schwefel (shrink=10.0, s_flag=1, r_flag=1). Bias=1100."""
    z = shift_rotate(x, Os, Mr, 1000.0 / 100.0, 1, 1, Mr_T=Mr_T)
    return basic.schwefel(z) + 1100.0


# ---------- F3: Shifted and Rotated Lunacek Bi-Rastrigin (bias=700) ----------
def f3_bi_rastrigin(x: np.ndarray, Os: np.ndarray, Mr: np.ndarray,
                    *, Mr_T: np.ndarray | None = None) -> np.ndarray:
    """Lunacek Bi-Rastrigin with s_flag=1, r_flag=1.

    Expects (M, D) batch input (the dispatcher handles 1D→2D reshaping).
    The dispatcher pre-slices ``Os`` to ``(D,)`` and ``Mr`` to ``(D, D)``,
    so the redundant ``[:D]`` / ``[:D, :D]`` re-slices have been removed.

    XS-01: *Mr_T* is the pre-transposed rotation matrix used for the
    ``z_val @ Mr.T`` cosine-term rotation when the Numba fast path is
    unavailable.
    """
    D = x.shape[1]

    mu0 = 2.5
    d_val = 1.0
    s = 1.0 - 1.0 / (2.0 * np.sqrt(D + 20.0) - 8.2)
    mu1 = -np.sqrt((mu0 * mu0 - d_val) / s)

    # shift
    y = x - Os
    # scale
    y = y * (10.0 / 100.0)
    # sign-flip
    tmpx = 2.0 * y
    sign = np.where(Os < 0.0, -1.0, 1.0)
    tmpx = tmpx * sign
    z_val = tmpx.copy()
    tmpx = tmpx + mu0

    # two sphere terms
    tmp1 = np.sum((tmpx - mu0) ** 2, axis=-1)
    tmp2 = np.sum((tmpx - mu1) ** 2, axis=-1) * s + d_val * D

    # rotate z_val for cosine term
    # XS-01: use pre-transposed matrix when available
    yr = z_val @ Mr_T if Mr_T is not None else z_val @ Mr.T
    cos_sum = np.sum(np.cos(2.0 * np.pi * yr), axis=-1)

    return np.minimum(tmp1, tmp2) + 10.0 * (D - cos_sum) + 700.0


# ---------- F4: Griewank-Rosenbrock (s_flag=0, r_flag=0, bias=1900) ----------
def f4_grie_rosen(x: np.ndarray, Os: np.ndarray, Mr: np.ndarray,
                  *, Mr_T: np.ndarray | None = None) -> np.ndarray:
    """grie_rosen_func called with s_flag=0, r_flag=0.

    shift_rotate with s_flag=0 skips shift (just scales by shrink=5/100),
    r_flag=0 skips rotation. basic.grie_rosen then applies +1 origin shift
    and the Griewank-of-Rosenbrock formula internally.
    """
    z = shift_rotate(x, Os, Mr, 5.0 / 100.0, 0, 0, Mr_T=Mr_T)
    return basic.grie_rosen(z) + 1900.0
