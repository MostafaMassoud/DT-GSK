"""Thread-local selection between the batch and serial CEC2013-LSGO kernel sets.

Suite-local mirror of ``cec2017/_kernel_mode.py`` (see that module's full
rationale).  The LSGO JIT kernels in ``_numba.py`` are compiled
``parallel=True`` and pay a fixed parallel-runtime launch cost per call at
``numba_threads=1`` (measured ~45-135 us/launch idle, up to ~300 us under
campaign contention) — at D=1000 that launch is still 60-90 % of a single-row
evaluation, so member-sequential optimizers (toa, saro, moa-mother, ema) lose
2.3-5x of their wall time to it.  ``_numba_serial.py`` provides
``parallel=False`` twins; this module holds the thread-local switch the
benchmark factory flips around an opted-in problem's evaluations.

A deliberately SEPARATE flag from cec2017's: per-suite flags mean a cec2017
serial scope can never route LSGO kernels (and vice versa), and no cec2017
file is touched while its campaign is mid-flight.

Safety properties (identical to the cec2017 design, adversarially verified
there): default off — threads that never enter the scope run the exact bytes
they always did (the FP-regime sentinel probes LSGO F1 through the default
path and is untouched by construction); thread-local, never leaking across
worker threads; re-entrant with exception-safe restore.
"""

from __future__ import annotations

import threading

_STATE = threading.local()


def serial_kernels_active() -> bool:
    """Return True while the current thread is inside an LSGO serial scope.

    Consulted by the kernel call sites in ``composite.py``; outside any scope
    this is False and the batch (``parallel=True``) kernels are used unchanged.
    """
    return getattr(_STATE, "serial", False)


class serial_kernel_scope:
    """Route this thread's LSGO kernel calls to the serial twins.

    Entered by the benchmark factory around the pre-resolved per-function
    target for problems constructed with ``serial_kernels=True`` (opt-in per
    optimizer via the campaign config allowlist).  Restores the previous state
    on exit, so nesting and exceptions are safe.  ``__slots__`` class rather
    than ``@contextmanager`` for the same hot-path reason as the cec2017
    original (~0.1 us vs ~0.7 us per enter/exit).
    """

    __slots__ = ("_previous",)

    def __enter__(self) -> None:
        self._previous = getattr(_STATE, "serial", False)
        _STATE.serial = True

    def __exit__(self, exc_type: object, exc_value: object, traceback: object) -> None:
        _STATE.serial = self._previous


def ackley_raw_active() -> bool:
    """Return True while the current thread is inside a raw-ackley scope.

    Consulted by the F3/F6/F10 call sites in ``composite.py``.  When True the
    RAW ackley kernels (no ``T_osz``/``T_asy``/``Lambda``) are used — the
    official CEC2013-LSGO ``benchmark_func.m`` form that LaTorre's MOS
    reference was measured on.  Outside any scope this is False and the default
    TRANSFORMED ackley (Molina's package, used by shade-ils) is used unchanged.
    Composes orthogonally with :func:`serial_kernels_active` — the raw kernels
    have their own serial twins.
    """
    return getattr(_STATE, "ackley_raw", False)


class ackley_raw_scope:
    """Route this thread's F3/F6/F10 ackley calls to the RAW (untransformed) twins.

    Entered by the benchmark factory around the pre-resolved per-function
    target for problems constructed with ``ackley_variant='raw'`` (opt-in per
    optimizer via the campaign config ``raw_ackley_optimizers`` allowlist).
    Restores the previous state on exit, so nesting inside a
    ``serial_kernel_scope`` and exceptions are both safe.  ``__slots__`` class
    for the same hot-path reason as the serial scope.
    """

    __slots__ = ("_previous",)

    def __enter__(self) -> None:
        self._previous = getattr(_STATE, "ackley_raw", False)
        _STATE.ackley_raw = True

    def __exit__(self, exc_type: object, exc_value: object, traceback: object) -> None:
        _STATE.ackley_raw = self._previous
