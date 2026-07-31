"""``parallel=False`` twins of the cec2020 kernels — same math, no launch tax.

WHY
---
Every ``@njit(parallel=True)`` call enters numba's threading runtime and pays a
fixed workqueue launch (~60 us) **regardless of batch size, even at
NUMBA_NUM_THREADS=1** — at one thread, ``parallel=True`` is literally
*serial + launch tax*. One ``problem.evaluate`` is several such launches
(transforms plus base function, plus composition weights on the hybrid and
composition functions), so the tax is paid repeatedly per evaluation.
Re-jitting the *same* ``py_func`` with ``parallel=False`` removes it without
touching a line of kernel arithmetic.

The twins are built from ``dispatcher.py_func`` and inherit each kernel's own
``targetoptions`` (notably its per-kernel ``fastmath`` policy) — the math is the
same source, compiled without the parallel transform.

NUMERICAL CONTRACT — MEASURED BIT-IDENTICAL (0 ULP), 2026-07-27
--------------------------------------------------------------
Divergence between a parallel kernel and its serial twin tracks ``fastmath``
and nothing else. That was established for cec2017 in
``cec2017/_numba_serial.py``: over 94,240 rows its ``fastmath=True`` kernels
reached 13 ULP while its single ``fastmath=False`` kernel was 100.00% bitwise.

This suite's ``_numba.py`` carries **no ``fastmath=True`` anywhere** — every
kernel decorator is ``@njit(cache=True, parallel=True, boundscheck=False,
nogil=True)`` — so the twins were predicted to be class (a) bit-identical
rather than cec2017's class (b). **That prediction has now been measured and
holds exactly**, through the production path
(``make_problem(..., serial_kernels=True)`` vs the default), so what is
verified is the path campaigns actually run — not the kernels in isolation:

| F | rows compared | max ULP | max relative |
|---|---|---|---|
| F1–F10 (each) | 2,352 | **0** | **0.0e+00** |
| **total** | **23,520** | **0** | **0.0e+00** |

Coverage per function: all four dimensions (5, 10, 15, 20) x {512 uniform
interior rows, the exact lower and upper bound vectors, the origin, and a
64-row cluster within 1e-12 of the lower bound} — i.e. the degenerate inputs
where a reassociated reduction would diverge first, not just interior noise.

Corroborating end-to-end evidence from the same date: all 32 registered
optimizers (24 family + 8 external) were run on this suite through both paths
and returned **identical** ``best_fitness`` and ``nfes`` — 0 failures,
0 mismatches.

Re-measure after any change to ``_numba.py``'s kernels or decorators; a single
``fastmath=True`` would move this suite from class (a) to class (b).

SCOPE
-----
Default is OFF. Opt in via ``make_problem(..., serial_kernels=True)``, which
routes through the suite-local flag in ``_kernel_mode.py``. Suite-local by
design: a cec2020 scope must never be able to route another suite's kernels.
The frozen evidence release was produced on the DEFAULT path, so leaving the
default untouched keeps every released number valid by construction.
"""

from __future__ import annotations

from typing import Any

from . import _numba as _nb

try:
    from numba import njit

    _HAVE_NUMBA = True
except Exception:  # pragma: no cover - exercised only without numba
    _HAVE_NUMBA = False


def _twin(dispatcher: Any) -> Any:
    """Re-jit ``dispatcher.py_func`` serially, inheriting its fastmath policy."""
    opts = dict(dispatcher.targetoptions)
    opts.pop("parallel", None)
    opts.pop("nopython", None)
    opts.pop("cache", None)
    # cache=False is mandatory: with cache=True numba silently reuses the
    # parallel build's artifact and the "twin" is not serial at all.
    return njit(cache=False, **opts)(dispatcher.py_func)


def __getattr__(name: str) -> Any:
    """Build each twin on first access, then cache it in module globals.

    Lazy by design: importing this module must stay free for the default
    (batch) path, which is every run that has not opted in. Once built, the
    twin is written into ``globals()`` so subsequent lookups never re-enter
    this hook.
    """
    if name.startswith("__"):
        raise AttributeError(name)
    disp = getattr(_nb, name, None)
    if disp is None or not hasattr(disp, "py_func"):
        raise AttributeError(f"{name!r} is not a compiled cec2020 kernel dispatcher")
    if not _HAVE_NUMBA:  # fail closed — never silently hand back the batch kernel
        raise RuntimeError(
            "serial kernels requested but numba is unavailable; refusing to fall "
            "back to a different FP path"
        )
    twin = _twin(disp)
    globals()[name] = twin
    return twin


def kernel_names() -> tuple[str, ...]:
    """Every cec2020 dispatcher that has a serial twin."""
    return tuple(
        n for n in dir(_nb)
        if not n.startswith("__") and hasattr(getattr(_nb, n), "py_func")
    )


def warmup() -> int:
    """Force-build every twin. Call once per worker at spawn.

    Returns the number of twins built. Roughly 0.25 s/kernel because
    ``cache=False`` is mandatory (see the module docstring) — pay it here,
    deliberately, rather than as a stall on the first evaluation of a cell.
    """
    n = 0
    for name in kernel_names():
        getattr(__import__(__name__, fromlist=["_"]), name)
        n += 1
    return n
