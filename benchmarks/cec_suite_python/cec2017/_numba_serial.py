"""Serial (``parallel=False``) twins of the CEC2017 JIT kernels.

WHY THIS MODULE EXISTS
~~~~~~~~~~~~~~~~~~~~~~
Every kernel in ``_numba.py`` is compiled with ``parallel=True`` and enters
the numba parallel runtime on each call.  At the campaign setting
``numba_threads=1`` that launch is pure overhead: measured on the campaign
machine, a single-row ``rastrigin_nb`` call costs ~61 us through the parallel
build versus ~0.4 us through a ``parallel=False`` build of the *same*
``py_func`` — identical math, no fork/join.  Member-sequential optimizers
(toa, saro, moa-mother, ema) are required by their papers' asynchronous loop
structure (AMB-adjudicated) to issue ~3N single-row evaluations per
iteration, so the launch tax is >99% of their wall time.  These serial twins
remove it without touching algorithm behavior.

Routing is strictly opt-in via ``_kernel_mode.serial_kernel_scope()`` (see
that module's safety notes); problems built without the flag — including the
FP-regime sentinel probes — never reach this module.  Since 2026-07-17 the
campaign allowlist routes ALL 24 optimizers through these twins: gsk joined
via the deliberate refreeze, and odo/sgo-social/sns via the same-day
un-freeze after their archived batch-kernel result sets were deleted (see
the UN-FREEZE record in OPTIMIZER_PERFORMANCE_AUDIT.md).

CONSTRUCTION: PROGRAMMATIC RE-JIT, NOT COPIED SOURCE
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Each twin is ``njit(...)(<batch kernel>.py_func)`` with the batch kernel's own
flags minus ``parallel`` — the algorithm source stays single-copy in
``_numba.py`` (kernels are self-contained: none calls another jitted
function, so re-jitting the leaves is complete).  Flag parity is derived from
``dispatcher.targetoptions`` at import time, which automatically preserves
the per-kernel fastmath policy (the strict kernels and ``_cf_cal_nb`` stay
non-fastmath, everything else keeps ``fastmath=True``).  ``prange`` degrades
to ``range`` under ``parallel=False`` (numba-documented), preserving the
single-thread iteration order.

``cache=False`` IS LOAD-BEARING
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Re-jitting a ``py_func`` with ``cache=True`` SILENTLY LOADS THE BATCH
KERNEL'S ON-DISK CACHE ARTIFACT (verified empirically on this machine: the
"serial" dispatcher returned in ~61 us — the parallel binary — with no
warning; numba's cache index does not disambiguate the ``parallel`` flag for
a re-decorated ``py_func``).  With ``cache=False`` the true serial compile
(~0.25 s/kernel) happens once per process; :func:`warmup` pays it up front in
each worker so no benchmark cell absorbs the cost.

NUMERICAL CONTRACT (measured exhaustively, 2026-07-16)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The serial twins execute the same operations in the same single-thread order.
Non-fastmath kernels (the strict set and ``_cf_cal_nb``) are bit-identical by
construction — verified exactly (0 ULP over 18,600 rows/function in strict
mode).  Fastmath kernels may be vectorized differently by LLVM in the two
builds: over a 2.16M-row sweep (29 functions x D=10/30/50/100 x K=1/3/8/50),
95.68% of rows are bitwise identical (11/29 functions fully exact everywhere);
the divergent tail is largest in the long-accumulation hybrids F17/F20 and the
compositions embedding them (F29/F30), reaching a MAXIMUM OF 11 ULP at F29
D=100 — i.e. relative difference <= 2.5e-15 everywhere (values ~1e9), seven
orders below the 1e-8 target-error resolution.  Documented bar: relative
<= 3e-15 under fastmath; bit-identical under strict.  The parity sweep lives
in the verification record (OPTIMIZER_PERFORMANCE_AUDIT.md) and
tests/unit/test_serial_kernels.py enforces the bar.  Opted-in optimizers run
entirely on one kernel set for all their evaluations (no threshold, no mixed
builds within a run), and their provenance records it.
"""

from __future__ import annotations

import numpy as np

from . import _numba as _batch

HAS_NUMBA = _batch.HAS_NUMBA


def _serial_twin(dispatcher):
    """Re-jit a batch kernel's ``py_func`` with ``parallel=False``.

    Copies the batch dispatcher's target options (preserving the per-kernel
    fastmath/boundscheck/nogil policy), drops ``parallel`` and the implied
    ``nopython``, and forces ``cache=False`` (see module docstring — with
    ``cache=True`` numba silently reuses the parallel build's artifact).

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
    rastrigin_nb = _serial_twin(_batch.rastrigin_nb)
    zakharov_nb = _serial_twin(_batch.zakharov_nb)
    rosenbrock_nb = _serial_twin(_batch.rosenbrock_nb)
    bent_cigar_nb = _serial_twin(_batch.bent_cigar_nb)
    bent_cigar_strict_nb = _serial_twin(_batch.bent_cigar_strict_nb)
    levy_nb = _serial_twin(_batch.levy_nb)
    step_rastrigin_nb = _serial_twin(_batch.step_rastrigin_nb)
    schwefel_nb = _serial_twin(_batch.schwefel_nb)
    elliptic_nb = _serial_twin(_batch.elliptic_nb)
    discus_nb = _serial_twin(_batch.discus_nb)
    ackley_nb = _serial_twin(_batch.ackley_nb)
    weierstrass_nb = _serial_twin(_batch.weierstrass_nb)
    griewank_nb = _serial_twin(_batch.griewank_nb)
    katsuura_nb = _serial_twin(_batch.katsuura_nb)
    happycat_nb = _serial_twin(_batch.happycat_nb)
    hgbat_nb = _serial_twin(_batch.hgbat_nb)
    schaffer_F7_nb = _serial_twin(_batch.schaffer_F7_nb)
    bi_rastrigin_nb = _serial_twin(_batch.bi_rastrigin_nb)
    egpr_nb = _serial_twin(_batch.egpr_nb)
    esf6_nb = _serial_twin(_batch.esf6_nb)
    _shift_only_nb = _serial_twin(_batch._shift_only_nb)
    _shift_only_strict_nb = _serial_twin(_batch._shift_only_strict_nb)
    _shift_rotate_strict_nb = _serial_twin(_batch._shift_rotate_strict_nb)
    _cf_cal_nb = _serial_twin(_batch._cf_cal_nb)

    def shift_rotate_fast(x, shift, rotation, rotation_T=None):
        """Serial-kernel mirror of ``_numba.shift_rotate_fast``.

        Identical logic; only the shift kernel build differs.  The rotation
        GEMM is the same NumPy/BLAS call in both paths (bit-identical).
        """
        N = x.shape[1]
        y = _shift_only_nb(x, shift[:N], N)
        if rotation_T is not None:
            return y @ rotation_T
        if rotation is not None:
            return y @ rotation.T
        return y

    def shift_rotate_strict_fast(x, shift, rotation, rotation_T=None):
        """Serial-kernel mirror of ``_numba.shift_rotate_strict_fast``."""
        N = x.shape[1]
        if rotation_T is not None:
            return _shift_rotate_strict_nb(x, shift[:N], rotation_T)
        if rotation is not None:
            return _shift_rotate_strict_nb(x, shift[:N], np.ascontiguousarray(rotation.T))
        return _shift_only_strict_nb(x, shift[:N], N)

    cf_cal_fast = _cf_cal_nb

else:
    # Numba unavailable -- mirror _numba.py's fallback surface exactly.
    rastrigin_nb = None
    zakharov_nb = None
    rosenbrock_nb = None
    bent_cigar_nb = None
    bent_cigar_strict_nb = None
    levy_nb = None
    step_rastrigin_nb = None
    _shift_only_nb = None
    _shift_only_strict_nb = None
    _shift_rotate_strict_nb = None
    shift_rotate_fast = None
    shift_rotate_strict_fast = None
    schwefel_nb = None
    elliptic_nb = None
    discus_nb = None
    ackley_nb = None
    weierstrass_nb = None
    griewank_nb = None
    katsuura_nb = None
    happycat_nb = None
    hgbat_nb = None
    schaffer_F7_nb = None
    bi_rastrigin_nb = None
    egpr_nb = None
    esf6_nb = None
    _cf_cal_nb = None
    cf_cal_fast = None


def warmup() -> None:
    """Trigger compilation of all serial twins with small dummy inputs.

    Mirrors ``_numba.warmup()`` (same fixed ``default_rng(0xDEC0DE)`` payloads,
    audit C-02 determinism).  Because the twins are ``cache=False`` this pays
    the full ~0.25 s/kernel LLVM compile — call it once per worker process
    (the runner does so only when the campaign's serial-kernel allowlist is
    non-empty) so no benchmark cell absorbs compilation time.
    """
    if not HAS_NUMBA:
        return
    _warmup_rng = np.random.default_rng(0xDEC0DE)
    n, d = 4, 3
    xc = _warmup_rng.standard_normal((n, d))
    rastrigin_nb(xc)
    zakharov_nb(xc)
    rosenbrock_nb(xc)
    bent_cigar_nb(xc)
    bent_cigar_strict_nb(xc)
    levy_nb(xc)
    step_rastrigin_nb(xc)
    schwefel_nb(xc)
    elliptic_nb(xc)
    discus_nb(xc)
    ackley_nb(xc)
    weierstrass_nb(xc)
    griewank_nb(xc)
    katsuura_nb(xc)
    happycat_nb(xc)
    hgbat_nb(xc)
    schaffer_F7_nb(xc)
    egpr_nb(xc)
    esf6_nb(xc)
    sh = _warmup_rng.standard_normal(100)
    rot = np.eye(d)
    bi_rastrigin_nb(xc, sh[:d], rot, True)
    bi_rastrigin_nb(xc, sh[:d], None, False)
    _shift_only_nb(xc, sh[:d], d)
    _shift_only_strict_nb(xc, sh[:d], d)
    shift_rotate_strict_fast(xc, sh[:d], rot)
    cs = _warmup_rng.standard_normal((2, d))
    dl = np.array([1.0, 1.0])
    bi = np.array([0.0, 0.0])
    fv = _warmup_rng.standard_normal((2, n))
    _cf_cal_nb(xc, cs, dl, bi, fv)


__all__ = [
    "HAS_NUMBA",
    "rastrigin_nb",
    "zakharov_nb",
    "rosenbrock_nb",
    "bent_cigar_nb",
    "bent_cigar_strict_nb",
    "levy_nb",
    "step_rastrigin_nb",
    "schwefel_nb",
    "elliptic_nb",
    "discus_nb",
    "ackley_nb",
    "weierstrass_nb",
    "griewank_nb",
    "katsuura_nb",
    "happycat_nb",
    "hgbat_nb",
    "schaffer_F7_nb",
    "bi_rastrigin_nb",
    "egpr_nb",
    "esf6_nb",
    "shift_rotate_fast",
    "shift_rotate_strict_fast",
    "cf_cal_fast",
    "warmup",
]
