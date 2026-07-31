"""CEC2017 simple functions F1–F10 (shifted + rotated single base functions).

Each function applies shift_rotate(x, shift, rotation) → z, then calls
the base function on z and adds a bias = fid × 100.

Function mapping and special cases:
  F1:  bent_cigar     (standard shift+rotate)
  F2:  sum_diff_pow   (DEPRECATED — numerically unstable, excluded from competition)
  F3:  zakharov       (standard shift+rotate)
  F4:  rosenbrock     (standard shift+rotate)
  F5:  rastrigin      (standard shift+rotate)
  F6:  schaffer_F7    (SHIFT ONLY — C++ reads from y[] not z[], see below)
  F7:  bi_rastrigin   (custom shift/rotate logic, not via _get_defaults)
  F8:  step_rastrigin (C++ bug: step lost, reduces to plain rastrigin)
  F9:  levy           (standard shift+rotate)
  F10: schwefel       (standard shift+rotate)

C++ quirk — F6 (Schaffer F7):
  The compiled reference calls sr_func with s_flag=1, r_flag=1, which writes the shifted
  vector to global y[] and the rotated vector to global z[]. However,
  schaffer_F7_func then reads from y[] (shifted, NOT rotated). The rotation
  is computed but never used. We emulate this by passing only the shifted
  vector to basic.schaffer_F7.

C++ quirk — F8 (Step Rastrigin):
  The C++ applies a step modification to y[] (rounding values near integers),
  but sr_func is called AFTER step_rastrigin_func, overwriting y[] with the
  shift_rotate result. The step modification is lost. F8 reduces to plain
  rastrigin with F8's own shift/rotation data.

Valid dimensions: {2, 10, 20, 30, 50, 100} (F11-F19: no D=2 or D=20).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import numpy as np
from . import basic
from .transforms import rotations, rotations_T, shift_rotate, shifts


def _get_defaults(
    func_idx: int, N: int,
    shift: np.ndarray | None = None,
    rotation: np.ndarray | None = None,
) -> tuple[np.ndarray, np.ndarray, np.ndarray | None]:
    """Load default shift/rotation from packed data if not provided."""
    s = shift if shift is not None else shifts[func_idx]
    if rotation is not None:
        R = rotation
        R_T = None   # caller-supplied rotation — no pre-transposed version
    elif N in rotations and func_idx in rotations[N]:
        R = rotations[N][func_idx]
        R_T = rotations_T[N][func_idx]
    else:
        raise ValueError(
            f"No rotation data for func_idx={func_idx}, D={N}. "
            f"Available dims: {sorted(rotations.keys())}"
        )
    return s, R, R_T


def f1(
       x: np.ndarray,
       shift: np.ndarray | None = None,
       rotation: np.ndarray | None = None,
       *,
       strict_fp: bool = False,
) -> np.ndarray:
    """F1: Bent Cigar (shifted + rotated). Bias = 100."""
    s, R, R_T = _get_defaults(0, x.shape[1], shift, rotation)
    z = shift_rotate(x, s, R, rotation_T=R_T, strict=strict_fp)
    return basic.bent_cigar(z, strict=strict_fp) + 100.0


def f2(
       x: np.ndarray,
       shift: np.ndarray | None = None,
       rotation: np.ndarray | None = None,
) -> np.ndarray:
    """F2: Sum of Different Powers (DEPRECATED). Bias = 200."""
    s, R, R_T = _get_defaults(1, x.shape[1], shift, rotation)
    z = shift_rotate(x, s, R, rotation_T=R_T)
    return basic.sum_diff_pow(z) + 200.0


def f3(
       x: np.ndarray,
       shift: np.ndarray | None = None,
       rotation: np.ndarray | None = None,
) -> np.ndarray:
    """F3: Zakharov (shifted + rotated). Bias = 300."""
    s, R, R_T = _get_defaults(2, x.shape[1], shift, rotation)
    z = shift_rotate(x, s, R, rotation_T=R_T)
    return basic.zakharov(z) + 300.0


def f4(
       x: np.ndarray,
       shift: np.ndarray | None = None,
       rotation: np.ndarray | None = None,
) -> np.ndarray:
    """F4: Rosenbrock (shifted + rotated). Bias = 400."""
    s, R, R_T = _get_defaults(3, x.shape[1], shift, rotation)
    z = shift_rotate(x, s, R, rotation_T=R_T)
    return basic.rosenbrock(z) + 400.0


def f5(
       x: np.ndarray,
       shift: np.ndarray | None = None,
       rotation: np.ndarray | None = None,
) -> np.ndarray:
    """F5: Rastrigin (shifted + rotated). Bias = 500."""
    s, R, R_T = _get_defaults(4, x.shape[1], shift, rotation)
    z = shift_rotate(x, s, R, rotation_T=R_T)
    return basic.rastrigin(z) + 500.0


def f6(
       x: np.ndarray,
       shift: np.ndarray | None = None,
       rotation: np.ndarray | None = None,
) -> np.ndarray:
    """F6: Schaffer F7 (shifted ONLY — C++ uses y[] buffer, not z[]).

    The C++ computes si = sqrt(y[i]² + y[i+1]²) where y is the shifted
    (not rotated) vector. sr_func is called with s_flag=1, r_flag=1,
    but schaffer_F7_func reads from global y[] which holds the shifted values.
    Bias = 600.
    """
    s = shift if shift is not None else shifts[5]
    N = x.shape[1]
    # Shift only — no rotation applied (C++ quirk: reads y[] not z[])
    y = x - s[:N]
    return basic.schaffer_F7(y) + 600.0


def f7(
       x: np.ndarray,
       shift: np.ndarray | None = None,
       rotation: np.ndarray | None = None,
) -> np.ndarray:
    """F7: Bi-Rastrigin (custom shift/rotate). Bias = 700."""
    s = shift if shift is not None else shifts[6]
    N = x.shape[1]
    if rotation is not None:
        R = rotation
        R_T = None
    elif N in rotations and 6 in rotations[N]:
        R = rotations[N][6]
        R_T = rotations_T[N][6]
    else:
        raise ValueError(
            f"No rotation data for F7 (bi_rastrigin), D={N}. "
            f"Available dims: {sorted(rotations.keys())}"
        )
    return basic.bi_rastrigin(x, shift=s, rotation=R, apply_shift=True, rotation_T=R_T) + 700.0


def f8(
       x: np.ndarray,
       shift: np.ndarray | None = None,
       rotation: np.ndarray | None = None,
) -> np.ndarray:
    """F8: Step Rastrigin / Non-Continuous Rastrigin.

    compiled reference bug: step modification on y[] is overwritten by sr_func.
    This matches the C++ behavior (step lost → plain rastrigin with F8 data).
    Bias = 800.
    """
    s, R, R_T = _get_defaults(7, x.shape[1], shift, rotation)
    z = shift_rotate(x, s, R, rotation_T=R_T)
    return basic.step_rastrigin(z) + 800.0


def f9(
       x: np.ndarray,
       shift: np.ndarray | None = None,
       rotation: np.ndarray | None = None,
) -> np.ndarray:
    """F9: Levy (shifted + rotated). Bias = 900."""
    s, R, R_T = _get_defaults(8, x.shape[1], shift, rotation)
    z = shift_rotate(x, s, R, rotation_T=R_T)
    return basic.levy(z) + 900.0


def f10(
        x: np.ndarray,
        shift: np.ndarray | None = None,
        rotation: np.ndarray | None = None,
) -> np.ndarray:
    """F10: Schwefel (shifted + rotated). Bias = 1000."""
    s, R, R_T = _get_defaults(9, x.shape[1], shift, rotation)
    z = shift_rotate(x, s, R, rotation_T=R_T)
    return basic.schwefel(z) + 1000.0
