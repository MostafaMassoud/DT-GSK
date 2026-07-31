"""CEC2013 simple functions F1-F20 (shifted/rotated single base functions).

Cross-reference: ``test_func.c`` switch statement (lines 131-244),
dispatching ``case 1`` through ``case 20`` with per-function ``r_flag``
and bias offsets.

Each function loads default shift/rotation data and adds the CEC2013 bias.

Data indexing
~~~~~~~~~~~~~
All simple functions use:
  - Shift vector 0: ``OShift[0*nx]`` -> ``get_shift(N, 0)``
  - Rotation M1:    ``Mr[0*nx*nx]``  -> ``get_rotation(N, 0)``
  - Rotation M2:    ``Mr[1*nx*nx]``  -> ``get_rotation(N, 1)``

r_flag per function (from the C switch statement)::

  ====  =============  ======  ========================
  F#    base function  r_flag  rotations used
  ====  =============  ======  ========================
  F1    sphere         0       none
  F2    elliptic       1       M1
  F3    bent_cigar     1       M1 + M2
  F4    discus         1       M1
  F5    dif_powers     0       none
  F6    rosenbrock     1       M1
  F7    schaffer_F7    1       M1 + M2
  F8    ackley         1       M1 + M2
  F9    weierstrass    1       M1 + M2
  F10   griewank       1       M1
  F11   rastrigin      0       none (osz/asy/cond only)
  F12   rastrigin      1       M1 + M2 + M1 (3 rotations)
  F13   step_rastrigin 1       M1 + M2 + M1 (3 rotations)
  F14   schwefel       0       none
  F15   schwefel       1       M1
  F16   katsuura       1       M1 + M2
  F17   bi_rastrigin   0       none (sign-flip/cond only)
  F18   bi_rastrigin   1       M1 + M2
  F19   grie_rosen     1       M1 (but C bug discards it)
  F20   escaffer6      1       M1 + M2
  ====  =============  ======  ========================

Optimal values: f*(F_i) = -1400 + 100*(i-1), skipping 0.
  F1=-1400, F2=-1300, ..., F14=-100, F15=+100, ..., F20=+600.
"""

from __future__ import annotations

import threading

import numpy as np

from . import basic
from .transforms import get_rotation, get_rotation_T, get_shift


# Audit LOW (CEC2013): cache the per-dim ``(shift, M1, M2, M1_T, M2_T)``
# tuple so the F1..F20 hot path stops paying for dict lookups + tuple
# construction on every NFE.  ``get_shift`` / ``get_rotation`` /
# ``get_rotation_T`` are already cached in ``transforms.py``, so this is a
# second-level micro-cache that collapses the lookups into one.  Bounded
# at <= |VALID_DIMS| (12 entries), never invalidated, deterministic per-key.
# Audit AUDIT-06: use a reentrant lock for thread safety under
# free-threaded CPython 3.13t (--disable-gil).
_CACHE_LOCK = threading.RLock()
_defaults_cache: dict[
    int,
    tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray],
] = {}


def _defaults(
    N: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Return (shift_0, M1, M2, M1_T, M2_T) for simple functions.

    All simple functions F1-F20 use the same data indices:
      - shift vector index 0
      - rotation matrix indices 0 (M1) and 1 (M2)

    XS-01: *M1_T* and *M2_T* are the pre-transposed C-contiguous rotation
    matrices from :func:`get_rotation_T`, provided so downstream
    ``y @ M1_T`` uses a C-contiguous right operand for optimal BLAS.

    The transforms module caches the underlying arrays, and the
    ``_defaults_cache`` above caches the assembled tuple so each dim
    pays the lookup cost exactly once per process.
    """
    cached = _defaults_cache.get(N)
    if cached is None:
        with _CACHE_LOCK:
            cached = _defaults_cache.get(N)
            if cached is None:
                cached = (
                    get_shift(N, 0),
                    get_rotation(N, 0),
                    get_rotation(N, 1),
                    get_rotation_T(N, 0),
                    get_rotation_T(N, 1),
                )
                _defaults_cache[N] = cached
    return cached


# ============================================================
# Unimodal: F1-F5
# ============================================================

def f1(x: np.ndarray) -> np.ndarray:
    """F1: Shifted Sphere.  f* = -1400.

    C: case 1 (line 132), r_flag=0.
    """
    Os, M1, _, M1_T, _ = _defaults(x.shape[1])
    return basic.sphere_func(x, Os, M1, r_flag=0, M1_T=M1_T) + (-1400.0)


def f2(x: np.ndarray) -> np.ndarray:
    """F2: Rotated High Conditioned Elliptic.  f* = -1300.

    C: case 2 (line 138), r_flag=1.
    """
    Os, M1, _, M1_T, _ = _defaults(x.shape[1])
    return basic.ellips_func(x, Os, M1, r_flag=1, M1_T=M1_T) + (-1300.0)


def f3(x: np.ndarray) -> np.ndarray:
    """F3: Rotated Bent Cigar.  f* = -1200.

    C: case 3 (line 142), r_flag=1.  Uses both M1 and M2.
    """
    Os, M1, M2, M1_T, M2_T = _defaults(x.shape[1])
    return basic.bent_cigar_func(
        x, Os, M1, M2, r_flag=1, M1_T=M1_T, M2_T=M2_T,
    ) + (-1200.0)


def f4(x: np.ndarray) -> np.ndarray:
    """F4: Rotated Discus.  f* = -1100.

    C: case 4 (line 146), r_flag=1.
    """
    Os, M1, _, M1_T, _ = _defaults(x.shape[1])
    return basic.discus_func(x, Os, M1, r_flag=1, M1_T=M1_T) + (-1100.0)


def f5(x: np.ndarray) -> np.ndarray:
    """F5: Different Powers.  f* = -1000.

    C: case 5 (line 150), r_flag=0.
    """
    Os, M1, _, M1_T, _ = _defaults(x.shape[1])
    return basic.dif_powers_func(x, Os, M1, r_flag=0, M1_T=M1_T) + (-1000.0)


# ============================================================
# Multimodal: F6-F20
# ============================================================

def f6(x: np.ndarray) -> np.ndarray:
    """F6: Rotated Rosenbrock.  f* = -900.

    C: case 6 (line 155), r_flag=1.
    """
    Os, M1, _, M1_T, _ = _defaults(x.shape[1])
    return basic.rosenbrock_func(x, Os, M1, r_flag=1, M1_T=M1_T) + (-900.0)


def f7(x: np.ndarray) -> np.ndarray:
    """F7: Rotated Schaffer's F7.  f* = -800.

    C: case 7 (line 159), r_flag=1.  Uses M1 + M2.
    """
    Os, M1, M2, M1_T, M2_T = _defaults(x.shape[1])
    return basic.schaffer_F7_func(
        x, Os, M1, M2, r_flag=1, M1_T=M1_T, M2_T=M2_T,
    ) + (-800.0)


def f8(x: np.ndarray) -> np.ndarray:
    """F8: Rotated Ackley.  f* = -700.

    C: case 8 (line 163), r_flag=1.  Uses M1 + M2.
    """
    Os, M1, M2, M1_T, M2_T = _defaults(x.shape[1])
    return basic.ackley_func(
        x, Os, M1, M2, r_flag=1, M1_T=M1_T, M2_T=M2_T,
    ) + (-700.0)


def f9(x: np.ndarray) -> np.ndarray:
    """F9: Rotated Weierstrass.  f* = -600.

    C: case 9 (line 167), r_flag=1.  Uses M1 + M2.
    """
    Os, M1, M2, M1_T, M2_T = _defaults(x.shape[1])
    return basic.weierstrass_func(
        x, Os, M1, M2, r_flag=1, M1_T=M1_T, M2_T=M2_T,
    ) + (-600.0)


def f10(x: np.ndarray) -> np.ndarray:
    """F10: Rotated Griewank.  f* = -500.

    C: case 10 (line 172), r_flag=1.
    """
    Os, M1, _, M1_T, _ = _defaults(x.shape[1])
    return basic.griewank_func(x, Os, M1, r_flag=1, M1_T=M1_T) + (-500.0)


def f11(x: np.ndarray) -> np.ndarray:
    """F11: Rastrigin (non-rotated).  f* = -400.

    C: case 11 (line 176), r_flag=0.
    Even with r_flag=0, the pipeline still applies osz/asy/conditioning.
    """
    Os, M1, M2, M1_T, M2_T = _defaults(x.shape[1])
    return basic.rastrigin_func(
        x, Os, M1, M2, r_flag=0, M1_T=M1_T, M2_T=M2_T,
    ) + (-400.0)


def f12(x: np.ndarray) -> np.ndarray:
    """F12: Rotated Rastrigin.  f* = -300.

    C: case 12 (line 180), r_flag=1.  Uses 3 rotations: M1, M2, M1.
    """
    Os, M1, M2, M1_T, M2_T = _defaults(x.shape[1])
    return basic.rastrigin_func(
        x, Os, M1, M2, r_flag=1, M1_T=M1_T, M2_T=M2_T,
    ) + (-300.0)


def f13(x: np.ndarray) -> np.ndarray:
    """F13: Non-continuous Rotated Rastrigin.  f* = -200.

    C: case 13 (line 184), r_flag=1.  Same as F12 with step quantisation.
    """
    Os, M1, M2, M1_T, M2_T = _defaults(x.shape[1])
    return basic.step_rastrigin_func(
        x, Os, M1, M2, r_flag=1, M1_T=M1_T, M2_T=M2_T,
    ) + (-200.0)


def f14(x: np.ndarray) -> np.ndarray:
    """F14: Schwefel (non-rotated).  f* = -100.

    C: case 14 (line 189), r_flag=0.
    """
    Os, M1, _, M1_T, _ = _defaults(x.shape[1])
    return basic.schwefel_func(x, Os, M1, r_flag=0, M1_T=M1_T) + (-100.0)


def f15(x: np.ndarray) -> np.ndarray:
    """F15: Rotated Schwefel.  f* = 100.

    C: case 15 (line 193), r_flag=1.
    Note: f* skips 0 in the CEC2013 sequence.
    """
    Os, M1, _, M1_T, _ = _defaults(x.shape[1])
    return basic.schwefel_func(x, Os, M1, r_flag=1, M1_T=M1_T) + 100.0


def f16(x: np.ndarray) -> np.ndarray:
    """F16: Rotated Katsuura.  f* = 200.

    C: case 16 (line 197), r_flag=1.  Uses M1 + M2.
    """
    Os, M1, M2, M1_T, M2_T = _defaults(x.shape[1])
    return basic.katsuura_func(
        x, Os, M1, M2, r_flag=1, M1_T=M1_T, M2_T=M2_T,
    ) + 200.0


def f17(x: np.ndarray) -> np.ndarray:
    """F17: Lunacek Bi-Rastrigin (non-rotated).  f* = 300.

    C: case 17 (line 201), r_flag=0.
    """
    Os, M1, M2, M1_T, M2_T = _defaults(x.shape[1])
    return basic.bi_rastrigin_func(
        x, Os, M1, M2, r_flag=0, M1_T=M1_T, M2_T=M2_T,
    ) + 300.0


def f18(x: np.ndarray) -> np.ndarray:
    """F18: Rotated Lunacek Bi-Rastrigin.  f* = 400.

    C: case 18 (line 205), r_flag=1.  Uses M1 + M2.
    """
    Os, M1, M2, M1_T, M2_T = _defaults(x.shape[1])
    return basic.bi_rastrigin_func(
        x, Os, M1, M2, r_flag=1, M1_T=M1_T, M2_T=M2_T,
    ) + 400.0


def f19(x: np.ndarray) -> np.ndarray:
    """F19: Expanded Griewank plus Rosenbrock.  f* = 500.

    C: case 19 (line 209), r_flag=1.
    Note: Due to C bug (line 770), the rotation is effectively a no-op.
    """
    Os, M1, _, _, _ = _defaults(x.shape[1])
    return basic.grie_rosen_func(x, Os, M1, r_flag=1) + 500.0


def f20(x: np.ndarray) -> np.ndarray:
    """F20: Expanded Scaffer's F6.  f* = 600.

    C: case 20 (line 213), r_flag=1.  Uses M1 + M2.
    """
    Os, M1, M2, M1_T, M2_T = _defaults(x.shape[1])
    return basic.escaffer6_func(
        x, Os, M1, M2, r_flag=1, M1_T=M1_T, M2_T=M2_T,
    ) + 600.0
