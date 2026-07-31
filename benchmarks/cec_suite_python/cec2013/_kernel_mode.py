"""Thread-local selection between the batch and serial CEC2013 kernel sets.

Suite mirror of ``cec2017/_kernel_mode.py`` — read that module's docstring for
the full design rationale.  The CEC2013 formula kernels in ``_numba.py`` are
compiled ``parallel=True`` and pay a fixed parallel-runtime launch cost per
kernel call regardless of batch size.  CEC2013 evaluates a *pipeline* of
kernels per function (conditioning + one or more formula cores, and up to
5 components x 2-3 kernels for the F21-F28 compositions), so the launch tax is
multiplied: measured on this machine a single-row CEC2013 evaluation costs
~924 us through the batch build versus ~10 us through the serial twins.
Member-sequential optimizers (toa, saro, moa-mother, ema) are required by their
papers' asynchronous loop structure to issue ~3N single-row evaluations per
iteration, so >99% of their wall time is launch overhead, not objective math.

``_numba_serial.py`` provides ``parallel=False`` twins of the same kernels.
This module holds the switch that routes a *single thread's* kernel calls to
those twins: the benchmark factory wraps an opted-in problem's evaluate call in
:func:`serial_kernel_scope`, and the per-kernel call sites in ``basic.py`` /
``transforms.py`` / ``composition.py`` consult :func:`serial_kernels_active`.

Safety properties:

- Default off.  A thread that never enters the scope executes the exact same
  code path (one extra thread-local read per kernel call, no floating-point
  change), so flag-off problems and the FP-regime sentinel probes are
  byte-identical by construction.
- Thread-local, not global: a scope entered by one thread can never leak into
  concurrently running evaluations on other threads (relevant for the
  ``thread`` parallel backend; the ``process`` backend isolates naturally).
- Re-entrant: nested scopes restore the previous state on exit.
- Stronger numerical contract than CEC2017's: no CEC2013 kernel carries
  ``fastmath=True`` (audit finding M-03, see ``_numba.py``), so every serial
  twin is bit-identical to its batch kernel — verified exhaustively over the
  28 functions x D in {10, 30, 50}.

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
    """Route this thread's CEC2013 kernel calls to the serial twins.

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
        """Enter the scope, remembering the thread's previous routing state."""
        self._previous = getattr(_STATE, "serial", False)
        _STATE.serial = True

    def __exit__(self, exc_type: object, exc_value: object, traceback: object) -> None:
        """Restore the routing state captured on entry (exception-safe)."""
        _STATE.serial = self._previous
