"""Serial (``parallel=False``) twins of the CEC2013-LSGO JIT kernels.

Suite mirror of ``cec2017/_numba_serial.py`` — read that module's docstring
for the full rationale.  In short: every kernel in ``_numba.py`` is compiled
``parallel=True`` and pays a fixed parallel-runtime launch per call at
``numba_threads=1``.  At D=1000 the launch is still 60-90 % of a single-row
evaluation (measured: F1 kernel-direct 158 vs 64 us at K=1; F4's two launches
375 vs 48 us), so member-sequential optimizers lose 2.3-5x of their wall time
to it, and even full-population dispatchers gain 1.1-1.7x under campaign
contention.  These twins are produced by re-jitting the SAME ``py_func`` with
``parallel`` dropped — flag parity (including the four deliberately
``fastmath=False`` group kernels, audit H-2) is derived from each dispatcher's
``targetoptions``, so the group kernels' twins are bit-identical by
construction and the fastmath twins carry the project's documented
rel<=3e-15 contract (measured bitwise on this hardware, F1/F4/F11 x K=100).

``cache=False`` IS LOAD-BEARING: re-jitting a ``py_func`` with ``cache=True``
silently loads the batch (parallel) on-disk artifact (verified on cec2017 and
re-verified for this suite).  The one-time compile (~0.25 s/kernel) is paid by
:func:`warmup` in each worker process.

Routing is strictly opt-in via ``_kernel_mode.serial_kernel_scope()``; the
FP-regime sentinel probes LSGO F1 through the DEFAULT path and is untouched
by construction.
"""

from __future__ import annotations

import numpy as np

from . import _numba as _batch

HAS_NUMBA = _batch.HAS_NUMBA


def _serial_twin(dispatcher):
    """Re-jit a batch kernel's ``py_func`` with ``parallel=False``.

    Copies the batch dispatcher's target options (preserving the per-kernel
    fastmath policy — the four group kernels stay non-fastmath), drops
    ``parallel`` and the implied ``nopython``, and forces ``cache=False``
    (see module docstring).

    Args:
        dispatcher: A compiled dispatcher from ``_numba.py``.

    Returns:
        The serial dispatcher over the same ``py_func``.
    """
    from numba import njit

    options = dict(dispatcher.targetoptions)
    options.pop("parallel", None)
    options.pop("nopython", None)
    options.pop("cache", None)
    return njit(cache=False, **options)(dispatcher.py_func)


if HAS_NUMBA:
    # Cat 1 — standalone transforms (fallback support; twinned for surface parity).
    transform_osz_nb = _serial_twin(_batch.transform_osz_nb)
    transform_asy_nb = _serial_twin(_batch.transform_asy_nb)
    lambda_transform_nb = _serial_twin(_batch.lambda_transform_nb)
    # Cat 2 — fused transform+eval cores (basic.py surface).
    fused_osz_elliptic_nb = _serial_twin(_batch.fused_osz_elliptic_nb)
    fused_osz_asy_lam_rastrigin_nb = _serial_twin(_batch.fused_osz_asy_lam_rastrigin_nb)
    fused_osz_asy_lam_ackley_nb = _serial_twin(_batch.fused_osz_asy_lam_ackley_nb)
    fused_osz_asy_schwefel_nb = _serial_twin(_batch.fused_osz_asy_schwefel_nb)
    sphere_nb = _serial_twin(_batch.sphere_nb)
    rosenbrock_nb = _serial_twin(_batch.rosenbrock_nb)
    # Cat 3 — shifted full-D kernels (hot path: F1-F3, F12, F15).
    shifted_osz_elliptic_nb = _serial_twin(_batch.shifted_osz_elliptic_nb)
    shifted_osz_asy_lam_rastrigin_nb = _serial_twin(_batch.shifted_osz_asy_lam_rastrigin_nb)
    shifted_osz_asy_lam_ackley_nb = _serial_twin(_batch.shifted_osz_asy_lam_ackley_nb)
    shifted_rosenbrock_nb = _serial_twin(_batch.shifted_rosenbrock_nb)
    shifted_osz_asy_schwefel_nb = _serial_twin(_batch.shifted_osz_asy_schwefel_nb)
    # Cat 4 — fused group kernels (hot path: F4-F11, F13, F14; fastmath=False).
    group_elliptic_nb = _serial_twin(_batch.group_elliptic_nb)
    group_rastrigin_nb = _serial_twin(_batch.group_rastrigin_nb)
    group_ackley_nb = _serial_twin(_batch.group_ackley_nb)
    group_schwefel_nb = _serial_twin(_batch.group_schwefel_nb)
    # Cat 5 — fused separable-remainder kernels (hot path: F4-F7).
    sep_osz_elliptic_nb = _serial_twin(_batch.sep_osz_elliptic_nb)
    sep_osz_asy_lam_rastrigin_nb = _serial_twin(_batch.sep_osz_asy_lam_rastrigin_nb)
    sep_osz_asy_lam_ackley_nb = _serial_twin(_batch.sep_osz_asy_lam_ackley_nb)
    sep_sphere_nb = _serial_twin(_batch.sep_sphere_nb)
    # Cat 6 — RAW-ackley twins (ackley_variant='raw'; F3/F6/F10, MOS reference).
    shifted_ackley_raw_nb = _serial_twin(_batch.shifted_ackley_raw_nb)
    group_ackley_raw_nb = _serial_twin(_batch.group_ackley_raw_nb)
    sep_ackley_raw_nb = _serial_twin(_batch.sep_ackley_raw_nb)
else:
    transform_osz_nb = None
    transform_asy_nb = None
    lambda_transform_nb = None
    fused_osz_elliptic_nb = None
    fused_osz_asy_lam_rastrigin_nb = None
    fused_osz_asy_lam_ackley_nb = None
    fused_osz_asy_schwefel_nb = None
    sphere_nb = None
    rosenbrock_nb = None
    shifted_osz_elliptic_nb = None
    shifted_osz_asy_lam_rastrigin_nb = None
    shifted_osz_asy_lam_ackley_nb = None
    shifted_rosenbrock_nb = None
    shifted_osz_asy_schwefel_nb = None
    group_elliptic_nb = None
    group_rastrigin_nb = None
    group_ackley_nb = None
    group_schwefel_nb = None
    sep_osz_elliptic_nb = None
    sep_osz_asy_lam_rastrigin_nb = None
    sep_osz_asy_lam_ackley_nb = None
    sep_sphere_nb = None
    shifted_ackley_raw_nb = None
    group_ackley_raw_nb = None
    sep_ackley_raw_nb = None


def warmup() -> None:
    """Trigger compilation of all serial twins with the batch warmup payloads.

    Mirrors ``_numba.warmup()`` exactly (same deterministic arange inputs).
    ``cache=False`` twins pay the full LLVM compile here (~0.25 s/kernel),
    once per worker process — the runner calls this only when the campaign's
    serial-kernel allowlist is non-empty for this suite.

    Covers the three RAW-ackley twins as well (``shifted_ackley_raw_nb``,
    ``group_ackley_raw_nb``, ``sep_ackley_raw_nb``).  They are exported by
    ``__all__`` but were never called here, so their ``.signatures`` stayed
    empty and ~0.28 s of LLVM landed in MOS's first F3/F6/F10 cell.

    NOTE: the payloads below are WRITABLE, while the suite's real data blobs
    are frozen read-only (``transforms.py:131,647-655``).  Numba types those as
    distinct arrays, so this helper cannot by itself prevent a recompile in the
    first timed cell — the runner warms through the real cells instead (see
    ``runners/run_experiment.py:_warm_serial_kernel_cells``) and falls back
    here only if that sweep warms nothing.
    """
    if not HAS_NUMBA:
        return
    n, d = 2, 5
    xc = np.ascontiguousarray(
        np.arange(n * d, dtype=np.float64).reshape(n, d) * 0.1 - 0.25,
    )
    xopt = np.zeros(d, dtype=np.float64)
    transform_osz_nb(xc)
    transform_asy_nb(xc, 0.2)
    lambda_transform_nb(xc, 10.0)
    fused_osz_elliptic_nb(xc)
    fused_osz_asy_lam_rastrigin_nb(xc)
    fused_osz_asy_lam_ackley_nb(xc)
    fused_osz_asy_schwefel_nb(xc)
    sphere_nb(xc)
    rosenbrock_nb(xc)
    shifted_osz_elliptic_nb(xc, xopt)
    shifted_osz_asy_lam_rastrigin_nb(xc, xopt)
    shifted_osz_asy_lam_ackley_nb(xc, xopt)
    shifted_rosenbrock_nb(xc, xopt)
    shifted_osz_asy_schwefel_nb(xc, xopt)
    idx = np.arange(d, dtype=np.int64)
    rot = np.eye(d, dtype=np.float64).ravel().copy()
    ro = np.array([0, d * d], dtype=np.int64)
    gs = np.array([0, d], dtype=np.int64)
    wt = np.ones(1, dtype=np.float64)
    group_elliptic_nb(xc, idx, xopt, rot, ro, gs, wt, 1)
    group_rastrigin_nb(xc, idx, xopt, rot, ro, gs, wt, 1)
    group_ackley_nb(xc, idx, xopt, rot, ro, gs, wt, 1)
    group_schwefel_nb(xc, idx, xopt, rot, ro, gs, wt, 1)
    sep_osz_elliptic_nb(xc, idx, xopt)
    sep_osz_asy_lam_rastrigin_nb(xc, idx, xopt)
    sep_osz_asy_lam_ackley_nb(xc, idx, xopt)
    sep_sphere_nb(xc, idx, xopt)
    # RAW-ackley twins (ackley_variant='raw'; F3/F6/F10, MOS reference).
    shifted_ackley_raw_nb(xc, xopt)
    group_ackley_raw_nb(xc, idx, xopt, rot, ro, gs, wt, 1)
    sep_ackley_raw_nb(xc, idx, xopt)


__all__ = [
    "HAS_NUMBA",
    "transform_osz_nb",
    "transform_asy_nb",
    "lambda_transform_nb",
    "fused_osz_elliptic_nb",
    "fused_osz_asy_lam_rastrigin_nb",
    "fused_osz_asy_lam_ackley_nb",
    "fused_osz_asy_schwefel_nb",
    "sphere_nb",
    "rosenbrock_nb",
    "shifted_osz_elliptic_nb",
    "shifted_osz_asy_lam_rastrigin_nb",
    "shifted_osz_asy_lam_ackley_nb",
    "shifted_rosenbrock_nb",
    "shifted_osz_asy_schwefel_nb",
    "group_elliptic_nb",
    "group_rastrigin_nb",
    "group_ackley_nb",
    "group_schwefel_nb",
    "sep_osz_elliptic_nb",
    "sep_osz_asy_lam_rastrigin_nb",
    "sep_osz_asy_lam_ackley_nb",
    "sep_sphere_nb",
    "shifted_ackley_raw_nb",
    "group_ackley_raw_nb",
    "sep_ackley_raw_nb",
    "warmup",
]
