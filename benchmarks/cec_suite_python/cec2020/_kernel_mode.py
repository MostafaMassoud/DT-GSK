"""Thread-local serial-kernel routing — **cec2020 suite only**.

Why per-suite: a scope must never be able to route a *different* suite's
kernels. Each suite that gets serial twins owns its own thread-local flag; this
mirrors ``cec2017/_kernel_mode.py`` and ``cec2020lsgo/_kernel_mode.py``.

Why thread-local rather than a module global: the runner's thread backend
(``--parallel-backend thread``) can run several problems concurrently in one
process; a global would let one problem's opt-in leak into another's kernels.

Default is OFF. Callers opt in via ``make_problem(..., serial_kernels=True)``,
which keeps the FP-regime integrity sentinel (``runners/fp_regime.py``, enforced
at every worker spawn) invariant **by construction** — the default path is
untouched, so no tolerance argument is ever needed for it, and the frozen
evidence release (produced on the default path) stays valid.
"""

from __future__ import annotations

import threading

_STATE = threading.local()


def serial_kernels_active() -> bool:
    """True iff the calling thread is inside a :class:`serial_kernel_scope`."""
    return getattr(_STATE, "serial", False)


class serial_kernel_scope:
    """Route cec2020 kernel calls to the ``parallel=False`` twins.

    ``__slots__`` keeps entry/exit at ~0.1 us; this sits on the per-evaluation
    path, so a plain class with a ``__dict__`` measurably erodes the win.
    Re-entrant and exception-safe: the previous flag is always restored.
    """

    __slots__ = ("_prev",)

    def __enter__(self) -> "serial_kernel_scope":
        self._prev = getattr(_STATE, "serial", False)
        _STATE.serial = True
        return self

    def __exit__(self, *exc: object) -> bool:
        _STATE.serial = self._prev
        return False


def set_serial_kernels(flag: bool) -> None:
    """Latch serial routing for the calling thread (process-pool workers).

    Used by problems constructed with ``serial_kernels=True`` so every
    ``evaluate`` call routes to the twins without paying scope entry per call.
    """
    _STATE.serial = bool(flag)
