"""Thread-local selection between the batch and serial CEC2017 kernel sets.

The CEC2017 JIT kernels in ``_numba.py`` are compiled ``parallel=True`` and
pay a fixed parallel-runtime launch cost (~60 us per kernel launch at
``numba_threads=1``) regardless of batch size.  That cost is invisible for
full-population dispatches (one launch amortized over N rows) but dominates
member-sequential optimizers (toa, saro, moa-mother, ema), whose paper-mandated
asynchronous loops issue ~3N single-row evaluations per iteration: >99% of
their wall time is launch overhead, not objective math.

``_numba_serial.py`` provides ``parallel=False`` twins of the same kernels
(~0.4 us for a single row — the same math without the launch).  This module
holds the switch that routes a *single thread's* kernel calls to those twins:
the benchmark factory wraps an opted-in problem's evaluate call in
:func:`serial_kernel_scope`, and the per-kernel call sites in ``basic.py`` /
``transforms.py`` / ``composition.py`` consult :func:`serial_kernels_active`.

Safety properties:

- Default off.  A thread that never enters the scope executes the exact same
  code path (one extra thread-local read per kernel call, no floating-point
  change), so flag-off problems and the FP-regime sentinel probes are
  byte-identical by construction.  (Historical: odo/sgo-social/sns were held
  on the batch path to protect their archived result sets until 2026-07-17,
  when those archives were deleted and the trio was un-frozen onto the serial
  path — gsk had been deliberately refrozen onto it earlier the same day.
  All 24 optimizers now route through the serial twins in the campaign
  configs; see the UN-FREEZE record in OPTIMIZER_PERFORMANCE_AUDIT.md.)
- Thread-local, not global: a scope entered by one thread can never leak into
  concurrently running evaluations on other threads (relevant for the
  ``thread`` parallel backend; the ``process`` backend isolates naturally).
- Re-entrant: nested scopes restore the previous state on exit.

CAVEAT (do not violate): the kernel call sites consult this thread-local flag,
not the evaluating problem's own ``serial_kernels`` attribute.  The scope is
opened only around a single problem's dispatcher call, so under the runner
architecture no *other* problem's evaluation can ever nest inside it.  If
future code ever evaluates one BenchmarkProblem from within another problem's
objective, the inner (flag-off) problem would silently cross onto the serial
kernel set for that call — add per-problem routing before introducing any
such nesting.
"""

from __future__ import annotations

import threading

_STATE = threading.local()


def serial_kernels_active() -> bool:
    """Return True while the current thread is inside a serial-kernel scope.

    Consulted by the per-kernel call sites; outside any scope this is False
    and the batch (``parallel=True``) kernels are used unchanged.
    """
    return getattr(_STATE, "serial", False)


class serial_kernel_scope:
    """Route this thread's CEC2017 kernel calls to the serial twins.

    Entered by the benchmark factory around the pre-resolved per-function
    target for problems constructed with ``serial_kernels=True`` (opt-in per
    optimizer via the campaign config allowlist).  Restores the previous state
    on exit, so nesting and exceptions are safe.

    Implemented as a ``__slots__`` class rather than ``@contextmanager``: the
    scope wraps every objective evaluation on the hot path, and the plain
    enter/exit protocol costs ~0.1 us versus ~0.7 us for the generator-based
    one — identical thread-local flag semantics.
    """

    __slots__ = ("_previous",)

    def __enter__(self) -> None:
        self._previous = getattr(_STATE, "serial", False)
        _STATE.serial = True

    def __exit__(self, exc_type: object, exc_value: object, traceback: object) -> None:
        _STATE.serial = self._previous
