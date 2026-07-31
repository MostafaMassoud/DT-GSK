"""Serial (``parallel=False``) twins of the CEC2013 JIT kernels.

WHY THIS MODULE EXISTS
~~~~~~~~~~~~~~~~~~~~~~
Suite mirror of ``cec2017/_numba_serial.py`` — read that module's docstring
for the full rationale.  Nineteen of the twenty-one kernels in ``_numba.py``
are compiled ``parallel=True`` and enter the numba parallel runtime on each
call.  At the campaign setting ``numba_threads=1`` that launch is pure
overhead, and CEC2013 pays it *repeatedly per evaluation*: unlike CEC2017
(one formula kernel per simple function), a CEC2013 function runs a pipeline
— ``conditioning_nb`` plus a formula core for the simple functions, and up to
five components x two or three kernels for the F21-F28 compositions.  Measured
on the campaign machine, a single-row CEC2013 evaluation costs ~924 us through
the batch build versus ~10 us through these twins: identical math, no
fork/join.  Member-sequential optimizers (toa, saro, moa-mother, ema) are
required by their papers' asynchronous loop structure (AMB-adjudicated) to
issue ~3N single-row evaluations per iteration, so the launch tax is >99% of
their wall time.  These serial twins remove it without touching algorithm
behavior.

Routing is strictly opt-in via ``_kernel_mode.serial_kernel_scope()`` (see that
module's safety notes); problems built without the flag — including the
FP-regime sentinel probes — never reach this module.

CONSTRUCTION: PROGRAMMATIC RE-JIT, NOT COPIED SOURCE
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Each twin is ``njit(...)(<batch kernel>.py_func)`` with the batch kernel's own
flags minus ``parallel`` — the algorithm source stays single-copy in
``_numba.py`` (kernels are self-contained: none calls another jitted function,
so re-jitting the leaves is complete).  Flag parity is derived from
``dispatcher.targetoptions`` at import time, which automatically preserves the
per-kernel ``boundscheck``/``nogil`` policy.  ``prange`` degrades to ``range``
under ``parallel=False`` (numba-documented), preserving the single-thread
iteration order.

DEVIATION FROM THE CEC2017 TEMPLATE: ALREADY-SERIAL KERNELS PASS THROUGH
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Every CEC2017 kernel is ``parallel=True``, so every twin there is a re-jit.
Two CEC2013 kernels — ``osz_func_nb`` and ``asy_func_nb`` — are declared
``parallel``-free on purpose (their per-row work is too small to amortise
prange; see ``_numba.py``'s decorator policy).  For those, :func:`_serial_twin`
returns the batch dispatcher itself: it already *is* the serial build, so
re-jitting would only discard its ``cache=True`` on-disk artifact and pay a
pointless ~0.25 s compile per worker.  Parity for those two kernels is
therefore bit-identical by object identity, and the ``transforms.py`` call
sites for ``osz_func`` / ``asy_func`` deliberately skip the mode check (a
branch that could only ever select the same object) to keep the hot path free
of dead thread-local reads.

``cache=False`` IS LOAD-BEARING
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Re-jitting a ``py_func`` with ``cache=True`` SILENTLY LOADS THE BATCH KERNEL'S
ON-DISK CACHE ARTIFACT (verified empirically on cec2017 and re-verified for
this suite: the "serial" dispatcher returned the parallel binary's timing with
no warning; numba's cache index does not disambiguate the ``parallel`` flag for
a re-decorated ``py_func``).  With ``cache=False`` the true serial compile
(~0.25 s/kernel) happens once per process; :func:`warmup` pays it up front in
each worker so no benchmark cell absorbs the cost.

NUMERICAL CONTRACT (measured exhaustively, 2026-07-26)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
STRICTER THAN CEC2017's.  ``fastmath=True`` is intentionally absent across the
whole CEC2013 suite (audit finding M-03 — see ``_numba.py``), so LLVM may not
fuse mul+add into FMA, reorder associative reductions, or substitute
approximate transcendentals in *either* build.  The serial twins therefore
execute the same operations in the same single-thread order with the same
rounding, and are **bit-identical by construction** — verified exactly (0 ULP,
0.0 relative difference) over all 28 functions x D in {10, 30, 50} x 256 rows.
There is no fastmath tail here and no 3e-15 allowance: any nonzero ULP
difference on this suite is a regression.  ``tests/unit/test_serial_kernels.py``
enforces the bar.  Opted-in optimizers run entirely on one kernel set for all
their evaluations (no threshold, no mixed builds within a run), and their
provenance records it.
"""

from __future__ import annotations

import numpy as np

from . import _numba as _batch

HAS_NUMBA = _batch.HAS_NUMBA


def _serial_twin(dispatcher):
    """Re-jit a batch kernel's ``py_func`` with ``parallel=False``.

    Copies the batch dispatcher's target options (preserving the per-kernel
    boundscheck/nogil policy), drops ``parallel`` and the implied ``nopython``,
    and forces ``cache=False`` (see module docstring — with ``cache=True``
    numba silently reuses the parallel build's artifact).

    A dispatcher that was never built with ``parallel=True`` is returned
    unchanged: it already is its own serial twin (``osz_func_nb`` /
    ``asy_func_nb``), and re-jitting would throw away its cached artifact for
    a byte-for-byte identical binary.

    Args:
        dispatcher: A compiled dispatcher from ``_numba.py``.

    Returns:
        The serial dispatcher over the same ``py_func``.
    """
    from numba import njit

    options = dict(dispatcher.targetoptions)
    if not options.get("parallel", False):
        return dispatcher
    options.pop("parallel", None)
    options.pop("nopython", None)
    options.pop("cache", None)
    return njit(cache=False, **options)(dispatcher.py_func)


if HAS_NUMBA:
    # ----- Transform kernels ------------------------------------------------
    # osz/asy are already parallel-free: pass-through (see module docstring).
    osz_func_nb = _serial_twin(_batch.osz_func_nb)
    asy_func_nb = _serial_twin(_batch.asy_func_nb)
    conditioning_nb = _serial_twin(_batch.conditioning_nb)
    # ----- Base function kernels -------------------------------------------
    sphere_nb = _serial_twin(_batch.sphere_nb)
    elliptic_core_nb = _serial_twin(_batch.elliptic_core_nb)
    bent_cigar_core_nb = _serial_twin(_batch.bent_cigar_core_nb)
    discus_core_nb = _serial_twin(_batch.discus_core_nb)
    dif_powers_core_nb = _serial_twin(_batch.dif_powers_core_nb)
    rastrigin_core_nb = _serial_twin(_batch.rastrigin_core_nb)
    schwefel_core_nb = _serial_twin(_batch.schwefel_core_nb)
    rosenbrock_core_nb = _serial_twin(_batch.rosenbrock_core_nb)
    ackley_core_nb = _serial_twin(_batch.ackley_core_nb)
    weierstrass_core_nb = _serial_twin(_batch.weierstrass_core_nb)
    griewank_core_nb = _serial_twin(_batch.griewank_core_nb)
    escaffer6_core_nb = _serial_twin(_batch.escaffer6_core_nb)
    grie_rosen_core_nb = _serial_twin(_batch.grie_rosen_core_nb)
    schaffer_F7_core_nb = _serial_twin(_batch.schaffer_F7_core_nb)
    katsuura_core_nb = _serial_twin(_batch.katsuura_core_nb)
    bi_rastrigin_core_nb = _serial_twin(_batch.bi_rastrigin_core_nb)
    step_rastrigin_quant_nb = _serial_twin(_batch.step_rastrigin_quant_nb)
    # ----- Composition weight kernel ---------------------------------------
    cf_cal_nb = _serial_twin(_batch.cf_cal_nb)

else:
    # Numba unavailable -- mirror _numba.py's fallback surface exactly.
    osz_func_nb = None
    asy_func_nb = None
    conditioning_nb = None
    sphere_nb = None
    bent_cigar_core_nb = None
    elliptic_core_nb = None
    discus_core_nb = None
    dif_powers_core_nb = None
    rastrigin_core_nb = None
    schwefel_core_nb = None
    rosenbrock_core_nb = None
    ackley_core_nb = None
    weierstrass_core_nb = None
    griewank_core_nb = None
    escaffer6_core_nb = None
    grie_rosen_core_nb = None
    schaffer_F7_core_nb = None
    katsuura_core_nb = None
    bi_rastrigin_core_nb = None
    step_rastrigin_quant_nb = None
    cf_cal_nb = None


def warmup() -> None:
    """Trigger compilation of all serial twins with small dummy inputs.

    Mirrors ``_numba.warmup()`` (same fixed ``default_rng(0xDEC0DE)`` payloads
    and the same 2x3 shapes, audit Pattern B determinism).  Because the twins
    are ``cache=False`` this pays the full ~0.25 s/kernel LLVM compile — call
    it once per worker process (the runner does so only when the campaign's
    serial-kernel allowlist is non-empty) so no benchmark cell absorbs
    compilation time.
    """
    if not HAS_NUMBA:
        return
    _warmup_rng = np.random.default_rng(0xDEC0DE)
    n, d = 2, 3
    xc = np.ascontiguousarray(_warmup_rng.standard_normal((n, d)), dtype=np.float64)
    Os = np.zeros(d)
    prev = xc.copy()
    # Transform kernels
    osz_func_nb(xc)
    asy_func_nb(xc, prev, 0.5)
    conditioning_nb(xc, 10.0)
    # Core formula kernels
    sphere_nb(xc, Os, d)
    rastrigin_core_nb(xc)
    schwefel_core_nb(xc, d)
    rosenbrock_core_nb(xc)
    ackley_core_nb(xc)
    weierstrass_core_nb(xc, d)
    griewank_core_nb(xc)
    escaffer6_core_nb(xc)
    grie_rosen_core_nb(xc)
    schaffer_F7_core_nb(xc)
    katsuura_core_nb(xc, d)
    bent_cigar_core_nb(xc, d)
    elliptic_core_nb(xc, d)
    discus_core_nb(xc, d)
    dif_powers_core_nb(xc, d)
    bi_rastrigin_core_nb(xc, xc, 2.5, -1.0, 0.9, 1.0, d)
    step_rastrigin_quant_nb(xc)
    # Composition weight kernel
    shifts_K = np.zeros((2, d))
    deltas = np.ones(2)
    biases = np.zeros(2)
    fit = np.zeros((2, n))
    cf_cal_nb(xc, shifts_K, deltas, biases, fit)


__all__ = [
    "HAS_NUMBA",
    "osz_func_nb",
    "asy_func_nb",
    "conditioning_nb",
    "sphere_nb",
    "bent_cigar_core_nb",
    "elliptic_core_nb",
    "discus_core_nb",
    "dif_powers_core_nb",
    "rastrigin_core_nb",
    "schwefel_core_nb",
    "rosenbrock_core_nb",
    "ackley_core_nb",
    "weierstrass_core_nb",
    "griewank_core_nb",
    "escaffer6_core_nb",
    "grie_rosen_core_nb",
    "schaffer_F7_core_nb",
    "katsuura_core_nb",
    "bi_rastrigin_core_nb",
    "step_rastrigin_quant_nb",
    "cf_cal_nb",
    "warmup",
]
