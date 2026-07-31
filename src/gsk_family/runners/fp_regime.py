"""Per-process floating-point regime canonicalization, verification, and sentinel.

Why this exists (see ``docs/reference/fp_regime.md`` for the full reference):

Every JIT kernel module in this project guards its ``import numba`` and
silently degrades to pure-NumPy fallbacks when that import fails.
numba/llvmlite imports can fail *transiently* under memory pressure
(``ImportError``/``OSError``/``AttributeError``), so a spawned campaign worker
can come up with some kernel modules JIT-compiled and others in NumPy
fallback. The fallback paths are numerically correct but not bit-identical to
the JIT kernels (fastmath reassociation), so such a worker runs in a second,
internally-deterministic floating-point regime: on chaotic cells it
deterministically selects different basins (verified witness: CEC2017 F20 D10
seed 54241459 finishes at error 3.1217325598e-01 with the ISM kernels in
fallback versus 0.0 fully JIT-compiled). Mixed-regime workers silently poison
paired cross-campaign comparisons while remaining invisible in summary
statistics.

This module turns the regime into an explicit, verified, recorded contract:

* :func:`canonical_fp_regime` deterministically imports every kernel module,
  launches a fixed warmup/probe kernel sequence, and returns a payload with
  each module's JIT flag plus a numeric sentinel (SHA-256 over probe outputs).
* :func:`ensure_canonical_fp_regime` fails closed: it raises
  :class:`FPRegimeError` when any kernel module is in NumPy fallback or when
  the computed sentinel does not match an expected (parent-process) sentinel.

The published DT-GSK reference results and the byte-stability golden values
correspond to the fully-JIT regime (all flags ``True``); the sentinel recorded
in ``environment.json`` makes that verifiable per campaign.

All probes are thread-count invariant (sequential kernels, or ``prange``
kernels whose iterations are per-element/per-row independent), so a worker
capped at one numba thread computes the same sentinel as the parent process
running with the full thread pool.
"""

from __future__ import annotations

import gc
import hashlib
import importlib
from typing import Any

import numpy as np

#: Seed for every deterministic probe input (matches the family base seed).
_PROBE_SEED = 20240620

#: Suite-independent kernel modules and their module-level JIT flags.
_CORE_KERNEL_MODULES: tuple[tuple[str, str], ...] = (
    ("gsk_family.common.reference_rng", "_HAVE_NUMBA"),
    ("gsk_family.common.threefry_rng", "_HAVE_NUMBA"),
    ("gsk_family.optimizers._kernels", "HAS_NUMBA"),
    ("gsk_family.optimizers._dt_subsystems._numba_accel", "HAS_NUMBA"),
)

#: Per-suite kernel modules and their module-level JIT flags.
_SUITE_KERNEL_MODULES: dict[str, tuple[str, str]] = {
    "cec2011": ("benchmarks.cec_suite_python.cec2011._numba", "HAS_NUMBA"),
    "cec2013": ("benchmarks.cec_suite_python.cec2013._numba", "HAS_NUMBA"),
    "cec2013lsgo": ("benchmarks.cec_suite_python.cec2013lsgo._numba", "HAS_NUMBA"),
    "cec2017": ("benchmarks.cec_suite_python.cec2017._numba", "HAS_NUMBA"),
    "cec2020": ("benchmarks.cec_suite_python.cec2020._numba", "HAS_NUMBA"),
}

#: Fixed per-suite probe cell ``(function, dimension)``; ``None`` = native dim.
#: cec2017 uses F20 D10 — the chaotic hybrid cell on which the regime split was
#: first observed and bit-exactly reproduced.
_SUITE_PROBE_CELLS: dict[str, tuple[int, int | None]] = {
    "sphere": (1, 10),
    "cec2011": (1, None),
    "cec2013": (1, 10),
    "cec2013lsgo": (1, None),
    "cec2017": (20, 10),
    "cec2020": (1, 10),
}

#: Per-process cache: suite -> canonical regime payload.
_REGIME_CACHE: dict[str, dict[str, Any]] = {}


class FPRegimeError(RuntimeError):
    """Raised when a process is not in the canonical (fully-JIT) FP regime."""


def _import_numba_with_retry(attempts: int = 3) -> tuple[Any | None, str | None]:
    """Import numba with retries; return ``(module_or_None, error_or_None)``.

    A failed ``import numba`` is removed from ``sys.modules`` by the
    interpreter, so a retry after ``gc.collect()`` can genuinely succeed when
    the first attempt failed under transient memory pressure.
    """
    error: str | None = None
    for _attempt in range(max(1, int(attempts))):
        try:
            import numba  # type: ignore[import-untyped]

            return numba, None
        except Exception as exc:  # numba/llvmlite can raise beyond ImportError
            error = f"{type(exc).__name__}: {exc}"
            gc.collect()
    return None, error


def _kernel_flag_report(suite: str) -> dict[str, bool | None]:
    """Import each kernel module for ``suite`` and read its JIT flag.

    Returns a mapping ``module_name -> flag`` where ``flag`` is the module's
    numba-availability boolean, or ``None`` when the module itself failed to
    import (recorded, not raised — the caller decides how loud to be).
    """
    modules = list(_CORE_KERNEL_MODULES)
    suite_entry = _SUITE_KERNEL_MODULES.get(suite)
    if suite_entry is not None:
        modules.append(suite_entry)
    report: dict[str, bool | None] = {}
    for module_name, flag_name in modules:
        try:
            module = importlib.import_module(module_name)
            report[module_name] = bool(getattr(module, flag_name))
        except Exception:
            report[module_name] = None
    return report


def _threefry_probe() -> np.ndarray:
    """Return 256 doubles from the shared Threefry stream (fixed seed).

    The pure-Python fallback of this generator is bit-identical to the JIT
    kernel by design, so this probe guards the stream itself (wrong values
    mean a broken generator, not merely a fallback).
    """
    from gsk_family.common.threefry_rng import ThreefryGenerator

    return np.asarray(ThreefryGenerator(_PROBE_SEED).random(256), dtype=np.float64)


def _dt_kernel_probe() -> bytes | None:
    """Exercise regime-sensitive ISM ``*_fast`` kernels on fixed inputs.

    Calls three fastmath kernels whose outputs are thread-count invariant
    (per-element repair, per-individual mutation, per-row distance) with
    Threefry-derived inputs and returns the concatenated result bytes.
    Returns ``None`` when the ISM acceleration module is in NumPy fallback
    (``*_fast`` exports are ``None``) — callers treat that as non-canonical.
    """
    from gsk_family.common.threefry_rng import ThreefryGenerator
    from gsk_family.optimizers._dt_subsystems import _numba_accel as accel

    if not getattr(accel, "HAS_NUMBA", False):
        return None
    gen = ThreefryGenerator(_PROBE_SEED)
    n, d = 8, 6
    pop = np.asarray(gen.random((n, d))) * 200.0 - 100.0
    vi = np.asarray(gen.random((n, d))) * 400.0 - 200.0
    lu = np.vstack((np.full(d, -100.0), np.full(d, 100.0)))
    accel.bound_constraint_fast(vi, pop, lu)

    fitness = np.asarray(gen.random(n), dtype=np.float64)
    kf = 0.5 + 0.5 * np.asarray(gen.random(n), dtype=np.float64)
    indices: list[np.ndarray] = [gen.permutation(n).astype(np.int64) for _ in range(6)]
    vi_junior: np.ndarray = np.empty((n, d), dtype=np.float64)
    vi_senior: np.ndarray = np.empty((n, d), dtype=np.float64)
    accel.build_junior_senior_fast(
        pop, fitness, kf, indices[0], indices[1], indices[2],
        indices[3], indices[4], indices[5], vi_junior, vi_senior,
    )

    inv_span = np.full(d, 1.0 / 200.0)
    dists = accel.archive_dists_fast(pop, n, pop[0], inv_span, 1.0 / np.sqrt(d))
    return b"".join(part.tobytes() for part in (vi, vi_junior, vi_senior, dists))


def _suite_probe(suite: str) -> np.ndarray | None:
    """Evaluate the suite's fixed probe cell on a fixed 8-point population.

    Routes through :func:`make_problem` so the probe exercises exactly the
    evaluation path campaigns use (including the suite's JIT kernels). Returns
    ``None`` for unknown suites.
    """
    cell = _SUITE_PROBE_CELLS.get(suite)
    if cell is None:
        return None
    from gsk_family.benchmark_adapter.factory import make_problem
    from gsk_family.common.threefry_rng import ThreefryGenerator

    func, dim = cell
    problem = make_problem(suite, func, dim)
    gen = ThreefryGenerator(_PROBE_SEED)
    u = np.asarray(gen.random((8, problem.dim)), dtype=np.float64)
    population = problem.lb + u * (problem.ub - problem.lb)
    return np.asarray(problem.evaluate(population), dtype=np.float64).reshape(-1)


def canonical_fp_regime(suite: str, *, use_cache: bool = True) -> dict[str, Any]:
    """Initialize this process's FP regime deterministically and fingerprint it.

    Runs a fixed sequence — numba import (with retry), kernel-module imports,
    Threefry probe, ISM kernel probe, suite probe — and returns a payload::

        {
          "suite": str,
          "jit_complete": bool,          # every kernel-module flag is True
          "kernel_flags": {module: bool | None, ...},
          "numba_import_error": str | None,
          "numba_version": str | None,
          "llvmlite_version": str | None,
          "probe_cell": [func, dim | None],
          "probes": {"threefry": sha256, "dt_kernels": sha256|None,
                      "suite": sha256 | None},
          "sentinel": str,               # sha256 over the probe digests
        }

    The sentinel hashes only numeric probe outputs, so two campaigns are
    FP-comparable exactly when their sentinels match. The payload is cached
    per process and suite (the regime cannot change after the kernel modules
    are imported, because each module freezes its fallback choice at import).
    """
    suite_key = str(suite).strip().lower()
    if use_cache and suite_key in _REGIME_CACHE:
        return _REGIME_CACHE[suite_key]

    numba_module, numba_error = _import_numba_with_retry()
    llvmlite_version: str | None = None
    if numba_module is not None:
        try:
            import llvmlite  # type: ignore[import-untyped]

            llvmlite_version = getattr(llvmlite, "__version__", None)
        except Exception:
            llvmlite_version = None

    kernel_flags = _kernel_flag_report(suite_key)

    threefry_values = _threefry_probe()
    dt_bytes = _dt_kernel_probe()
    suite_values = _suite_probe(suite_key)

    probes: dict[str, str | None] = {
        "threefry": hashlib.sha256(threefry_values.tobytes()).hexdigest(),
        "dt_kernels": hashlib.sha256(dt_bytes).hexdigest() if dt_bytes is not None else None,
        "suite": hashlib.sha256(suite_values.tobytes()).hexdigest() if suite_values is not None else None,
    }
    sentinel_text = "|".join(
        f"{name}:{digest if digest is not None else 'fallback'}"
        for name, digest in sorted(probes.items())
    )
    payload: dict[str, Any] = {
        "suite": suite_key,
        "jit_complete": all(flag is True for flag in kernel_flags.values()),
        "kernel_flags": kernel_flags,
        "numba_import_error": numba_error,
        "numba_version": getattr(numba_module, "__version__", None) if numba_module else None,
        "llvmlite_version": llvmlite_version,
        "probe_cell": list(_SUITE_PROBE_CELLS.get(suite_key, (None, None))),
        "probes": probes,
        "sentinel": hashlib.sha256(sentinel_text.encode("ascii")).hexdigest(),
    }
    if use_cache:
        _REGIME_CACHE[suite_key] = payload
    return payload


def ensure_canonical_fp_regime(
    suite: str,
    *,
    expected_sentinel: str | None = None,
) -> dict[str, Any]:
    """Verify this process is in the canonical fully-JIT FP regime.

    Raises :class:`FPRegimeError` when any kernel module is in NumPy fallback
    (silent regime-2; see the module docstring) or when ``expected_sentinel``
    is provided and does not match this process's sentinel. Returns the
    :func:`canonical_fp_regime` payload on success.
    """
    payload = canonical_fp_regime(suite)
    if not payload["jit_complete"]:
        degraded = sorted(
            name for name, flag in payload["kernel_flags"].items() if flag is not True
        )
        raise FPRegimeError(
            "Non-canonical floating-point regime: numba JIT is inactive in "
            f"{degraded} (numba_import_error={payload['numba_import_error']!r}). "
            "Results in this process would be deterministic but bit-different "
            "from the published fully-JIT regime (see "
            "docs/reference/fp_regime.md). "
            "Refusing to run rather than silently mixing FP regimes."
        )
    if expected_sentinel is not None and payload["sentinel"] != expected_sentinel:
        raise FPRegimeError(
            "FP-regime sentinel mismatch: this process computed "
            f"{payload['sentinel']} but the parent expected {expected_sentinel}. "
            "Probe digests: "
            f"{payload['probes']}. Refusing to run in a divergent FP regime."
        )
    return payload
