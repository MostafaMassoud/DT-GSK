"""CEC2013LSGO base mathematical functions.

Six base functions with embedded transforms, all vectorised ``(M, N) → (M,)``.

The LSGO transforms (T_osz on **ALL** dims, T_asy, Lambda) are applied
*inside* each base function, matching the C++ reference source
(``Benchmarks.cpp``).  This differs from CEC2013 standard, where T_osz
only touches the first and last elements.

Transform chains (per function)
-------------------------------
=========== ============================== ================
Function    Transform chain                C++ reference
=========== ============================== ================
elliptic    T_osz → evaluate               ``Benchmarks::elliptic``
rastrigin   T_osz → T_asy(0.2) → Λ(10) →  ``Benchmarks::rastrigin``
ackley      T_osz → T_asy(0.2) → Λ(10) →  ``Benchmarks::ackley``
schwefel12  T_osz → T_asy(0.2) → evaluate  ``Benchmarks::schwefel``
sphere      (none)                         ``Benchmarks::sphere``
rosenbrock  (none)                         ``Benchmarks::rosenbrock``
=========== ============================== ================

Numba acceleration
------------------
When Numba is available, fused single-pass ``@njit(parallel=True)`` kernels
handle the entire transform+evaluate pipeline in one loop, eliminating
intermediate ``(M, N)`` allocations.  Falls back to pure NumPy with
separate :func:`~.transforms.transform_osz` / :func:`~.transforms.transform_asy` /
:func:`~.transforms.lambda_transform` calls otherwise.
"""

from __future__ import annotations

import threading

import numpy as np

from .transforms import (
    _ensure_f64,
    lambda_transform,
    transform_asy,
    transform_osz,
)

__all__ = [
    "elliptic", "rastrigin", "ackley", "ackley_raw",
    "schwefel_1_2", "sphere", "rosenbrock",
]

PI = np.pi
E = np.e

# Thread-safe elliptic coefficient cache (double-check locking pattern
# matching CEC2013 ``_cond_scale_cache`` and CEC2013LSGO transforms).
_LSGO_CACHE_LOCK = threading.RLock()
_elliptic_coeff_cache: dict[int, np.ndarray] = {}


def _get_elliptic_coeff(N: int) -> np.ndarray:
    """Return cached 1e6^(i/max(N-1,1)) coefficient vector."""
    if N not in _elliptic_coeff_cache:
        with _LSGO_CACHE_LOCK:
            if N not in _elliptic_coeff_cache:
                _elliptic_coeff_cache[N] = np.power(
                    1e6, np.arange(N, dtype=np.float64) / max(N - 1, 1),
                )
    return _elliptic_coeff_cache[N]


# ---------------------------------------------------------------------------
# Numba fused kernels (graceful fallback)
# ---------------------------------------------------------------------------
try:
    from ._numba import (
        fused_osz_asy_lam_ackley_nb as _fused_ackley_nb,
        fused_osz_asy_lam_rastrigin_nb as _fused_rastrigin_nb,
        fused_osz_asy_schwefel_nb as _fused_schwefel_nb,
        fused_osz_elliptic_nb as _fused_elliptic_nb,
        rosenbrock_nb as _rosenbrock_nb,
        sphere_nb as _sphere_nb,
    )
except ImportError:
    _fused_elliptic_nb = None
    _fused_rastrigin_nb = None
    _fused_ackley_nb = None
    _fused_schwefel_nb = None
    _sphere_nb = None
    _rosenbrock_nb = None


# ============================================================
# Base functions
# ============================================================

def elliptic(z: np.ndarray) -> np.ndarray:
    r"""High-conditioned elliptic function with oscillation transform.

    .. math::
        f(\mathbf{z}) = \sum_{i=0}^{N-1} 10^{6i/(N-1)} \cdot \hat{z}_i^2

    where :math:`\hat{\mathbf{z}} = T_\text{osz}(\mathbf{z})`.

    The exponential coefficient spacing creates a condition number of
    :math:`10^6`, making the function highly ill-conditioned.  The T_osz
    transform adds a weak sinusoidal perturbation to break symmetry.

    **C++ reference**: ``Benchmarks::elliptic`` in ``Benchmarks.cpp``.
    Called by F1 (full-D), F4 (7 groups + sep), F8 (20 groups).

    Parameters
    ----------
    z : (M, N) float64
        Shifted (and optionally rotated) input.  For full-D functions
        (F1), ``z = x - xopt``.  For group functions (F4/F8), ``z``
        is already group-extracted, shifted, and rotated.

    Returns
    -------
    (M,) float64
        Fitness values.  ``f(0) = 0`` (global minimum).
    """
    if _fused_elliptic_nb is not None:
        return _fused_elliptic_nb(_ensure_f64(z))
    # NumPy fallback
    z_t = transform_osz(z)
    N = z_t.shape[1]
    coeff = _get_elliptic_coeff(N)
    return np.sum(coeff * z_t ** 2, axis=1)


def rastrigin(z: np.ndarray) -> np.ndarray:
    r"""Rastrigin function with full LSGO transform chain.

    .. math::
        f(\mathbf{z}) = \sum_{i=0}^{N-1}
            \bigl[\hat{z}_i^2 - 10\cos(2\pi\hat{z}_i) + 10\bigr]

    where :math:`\hat{\mathbf{z}} = \Lambda(10) \circ T_\text{asy}(0.2)
    \circ T_\text{osz}(\mathbf{z})`.

    Highly multimodal: approximately :math:`10^N` local minima arranged
    on a regular lattice.  The three-stage transform chain breaks the
    lattice regularity and creates asymmetry + ill-conditioning.

    **C++ reference**: ``Benchmarks::rastrigin`` in ``Benchmarks.cpp``.
    Called by F2 (full-D), F5 (7 groups + sep), F9 (20 groups).

    Parameters
    ----------
    z : (M, N) float64
        Shifted (and optionally rotated) input.

    Returns
    -------
    (M,) float64
        Fitness values.  ``f(0) = 0`` (global minimum).
    """
    if _fused_rastrigin_nb is not None:
        return _fused_rastrigin_nb(_ensure_f64(z))
    # NumPy fallback
    z_t = transform_osz(z)
    z_t = transform_asy(z_t, 0.2)
    z_t = lambda_transform(z_t, 10.0)
    return np.sum(z_t ** 2 - 10.0 * np.cos(2.0 * PI * z_t) + 10.0, axis=1)


def ackley(z: np.ndarray) -> np.ndarray:
    r"""Ackley function with full LSGO transform chain.

    .. math::
        f(\mathbf{z}) = -20\exp\!\left(-0.2\sqrt{\tfrac{1}{N}
            \sum_{i}\hat{z}_i^2}\right)
            - \exp\!\left(\tfrac{1}{N}\sum_{i}\cos(2\pi\hat{z}_i)\right)
            + 20 + e

    where :math:`\hat{\mathbf{z}} = \Lambda(10) \circ T_\text{asy}(0.2)
    \circ T_\text{osz}(\mathbf{z})`.

    Multimodal with a nearly flat outer region and a deep global basin.
    The exponential terms create a funnel that narrows sharply near the
    optimum.  Two accumulators (sum-of-squares and sum-of-cosines) are
    combined in the final formula.

    **C++ reference**: ``Benchmarks::ackley`` in ``Benchmarks.cpp``.
    Called by F3 (full-D), F6 (7 groups + sep), F10 (20 groups).

    Parameters
    ----------
    z : (M, N) float64
        Shifted (and optionally rotated) input.

    Returns
    -------
    (M,) float64
        Fitness values.  ``f(0) = 0`` (global minimum).
    """
    if _fused_ackley_nb is not None:
        return _fused_ackley_nb(_ensure_f64(z))
    # NumPy fallback
    z_t = transform_osz(z)
    z_t = transform_asy(z_t, 0.2)
    z_t = lambda_transform(z_t, 10.0)
    N = z_t.shape[1]
    s1 = np.sum(z_t ** 2, axis=1)
    s2 = np.sum(np.cos(2.0 * PI * z_t), axis=1)
    return -20.0 * np.exp(-0.2 * np.sqrt(s1 / N)) - np.exp(s2 / N) + 20.0 + E


def ackley_raw(z: np.ndarray) -> np.ndarray:
    r"""Ackley function WITHOUT the LSGO transform chain (``ackley_variant='raw'``).

    Identical to :func:`ackley` except the ``T_osz`` → ``T_asy(0.2)`` →
    ``Λ(10)`` chain is omitted, matching the official CEC2013-LSGO
    ``benchmark_func.m`` (which comments those three lines out for ackley) and
    LaTorre's MOS competition reference.  Used by F3/F6/F10 only when an
    optimizer opts into the raw variant (see :mod:`.composite` /
    :mod:`._kernel_mode`); the default suite path keeps the transformed
    :func:`ackley` (Molina's package, used by shade-ils).

    Parameters
    ----------
    z : (M, N) float64
        Shifted (and optionally rotated) input.

    Returns
    -------
    (M,) float64
        Fitness values.  ``f(0) = 0``.
    """
    N = z.shape[1]
    s1 = np.sum(z ** 2, axis=1)
    s2 = np.sum(np.cos(2.0 * PI * z), axis=1)
    return -20.0 * np.exp(-0.2 * np.sqrt(s1 / N)) - np.exp(s2 / N) + 20.0 + E


def schwefel_1_2(z: np.ndarray) -> np.ndarray:
    r"""Schwefel's Problem 1.2 with oscillation and asymmetry transforms.

    .. math::
        f(\mathbf{z}) = \sum_{i=0}^{N-1}
            \left(\sum_{j=0}^{i} \hat{z}_j\right)^{\!2}

    where :math:`\hat{\mathbf{z}} = T_\text{asy}(0.2) \circ
    T_\text{osz}(\mathbf{z})`.

    **No Lambda transform** — unlike rastrigin/ackley, schwefel_1_2 does
    not apply ill-conditioning scaling.  The cumulative sum creates full
    variable interaction: every dimension depends on all preceding ones,
    making this inherently non-separable.

    Implemented as ``cumsum → square → sum``, equivalent to the C++
    nested double loop but with O(N) complexity instead of O(N²).

    **C++ reference**: ``Benchmarks::schwefel`` in ``Benchmarks.cpp``.
    Called by F15 (full-D), F7 groups, F11 (20 groups), F13-F14 (overlap).

    Parameters
    ----------
    z : (M, N) float64
        Shifted (and optionally rotated) input.

    Returns
    -------
    (M,) float64
        Fitness values.  ``f(0) = 0`` (global minimum).
    """
    if _fused_schwefel_nb is not None:
        return _fused_schwefel_nb(_ensure_f64(z))
    # NumPy fallback
    z_t = transform_osz(z)
    z_t = transform_asy(z_t, 0.2)
    cs = np.cumsum(z_t, axis=1)
    return np.sum(cs ** 2, axis=1)


def sphere(z: np.ndarray) -> np.ndarray:
    r"""Sphere function — simplest benchmark, no transforms.

    .. math::
        f(\mathbf{z}) = \sum_{i=0}^{N-1} z_i^2

    No transforms applied (no T_osz, T_asy, or Lambda).  Unimodal,
    separable, and isotropic.  Used only as the separable remainder
    function for F7 (7-group Schwefel + sep sphere).

    **C++ reference**: ``Benchmarks::sphere`` in ``Benchmarks.cpp``.

    Parameters
    ----------
    z : (M, N) float64
        Shifted input (``z = x[sep_indices] - xopt[sep_indices]``).

    Returns
    -------
    (M,) float64
        Fitness values.  ``f(0) = 0`` (global minimum).
    """
    if _sphere_nb is not None:
        return _sphere_nb(_ensure_f64(z))
    return np.sum(z ** 2, axis=1)


def rosenbrock(z: np.ndarray) -> np.ndarray:
    r"""Rosenbrock (banana/valley) function — no transforms.

    .. math::
        f(\mathbf{z}) = \sum_{i=0}^{N-2}
            \bigl[100(z_i^2 - z_{i+1})^2 + (z_i - 1)^2\bigr]

    No transforms applied.  The global minimum is at :math:`\mathbf{z} = \mathbf{1}`
    (all ones), **not** at the origin.  For shifted LSGO usage (F12),
    the shift vector is set such that ``xopt`` maps to the Rosenbrock
    minimum, so ``f(xopt) = 999`` (the raw Rosenbrock minimum of 0 plus
    the F12 bias of 999).

    The narrow, curved valley from the origin to :math:`\mathbf{1}` makes
    this non-separable and difficult for gradient-free optimizers despite
    being unimodal (in 2-D/3-D; weakly multimodal for large N).

    **C++ reference**: ``Benchmarks::rosenbrock`` in ``Benchmarks.cpp``.
    Called by F12 (full-D, fully non-separable).

    Parameters
    ----------
    z : (M, N) float64
        Shifted input (``z = x - xopt``).

    Returns
    -------
    (M,) float64
        Fitness values.  ``f(1, 1, ..., 1) = 0`` (global minimum).
    """
    if _rosenbrock_nb is not None:
        return _rosenbrock_nb(_ensure_f64(z))
    t1 = z[:, :-1] ** 2 - z[:, 1:]
    t2 = z[:, :-1] - 1.0
    return np.sum(100.0 * t1 ** 2 + t2 ** 2, axis=1)
