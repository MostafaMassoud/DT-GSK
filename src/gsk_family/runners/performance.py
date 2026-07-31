"""Benchmark warmup and profiling helpers."""

from __future__ import annotations

import importlib
import os
import time
from dataclasses import asdict, dataclass
from typing import Any

import numpy as np

from gsk_family.benchmark_adapter.factory import make_problem


@dataclass(frozen=True)
class BenchmarkWarmupRecord:
    """One benchmark warmup timing record."""

    suite: str
    function: int
    dimension: int
    seconds: float


def warm_benchmark_cells(
    suite: str,
    cells: list[tuple[int, int]],
    max_evaluations: int,
    benchmark_fp_mode: str = "default",
) -> list[BenchmarkWarmupRecord]:
    """Import/load/evaluate benchmark cells once to trigger data and JIT warmup."""
    records: list[BenchmarkWarmupRecord] = []
    seen: set[tuple[int, int]] = set()
    for function, dimension in cells:
        key = (int(function), int(dimension))
        if key in seen:
            continue
        seen.add(key)
        start = time.perf_counter()
        problem = make_problem(
            suite,
            function,
            dimension,
            max_evaluations,
            benchmark_fp_mode=benchmark_fp_mode,
        )
        probe = ((problem.lb + problem.ub) / 2.0).reshape(1, -1)
        values = problem.evaluate(probe)
        if np.asarray(values).reshape(-1).size != 1:
            raise ValueError(f"Warmup for {suite} F{function} D{dimension} returned bad shape.")
        records.append(
            BenchmarkWarmupRecord(
                suite=suite,
                function=int(function),
                dimension=int(problem.dim),
                seconds=float(time.perf_counter() - start),
            )
        )
    return records


def warmup_records_to_json(records: list[BenchmarkWarmupRecord]) -> list[dict[str, object]]:
    """Return JSON-serializable warmup records."""
    return [asdict(record) for record in records]


def _suite_numba_enabled(suite: str) -> bool | None:
    """Return whether a suite exposes an active ``_numba.HAS_NUMBA`` flag."""
    if suite == "sphere":
        return None
    try:
        module = importlib.import_module(f"benchmarks.cec_suite_python.{suite}._numba")
    except Exception:
        return False
    return bool(getattr(module, "HAS_NUMBA", False))


def configure_numba_runtime(
    *,
    suite: str,
    parallel: bool,
    workers: int,
    requested_threads: int = 0,
) -> dict[str, Any]:
    """Configure and report Numba runtime state for benchmark execution.

    The runner parallelizes independent runs with Python workers (processes by
    default, threads only for diagnostics). Many benchmark kernels also use
    Numba ``prange`` internally. Letting every external worker use the full
    Numba thread pool can oversubscribe the CPU badly, so auto mode caps Numba
    threads to roughly ``logical_cores / workers`` when external parallelism is
    enabled.
    """
    suite_jit = _suite_numba_enabled(suite)
    payload: dict[str, Any] = {
        "numba_available": False,
        "numba_version": None,
        "suite_jit_enabled": suite_jit,
        "numba_threads_before": None,
        "numba_threads_active": None,
        "numba_threads_requested": int(requested_threads),
        "numba_threads_mode": "unavailable",
        "numba_threading_layer": None,
    }
    try:
        import numba  # type: ignore[import-untyped]
    except Exception as exc:
        payload["numba_error"] = str(exc)
        return payload

    before = int(numba.get_num_threads())
    logical_cores = os.cpu_count() or before
    target = int(requested_threads)
    mode = "manual" if target > 0 else "default"
    if target <= 0 and parallel and workers > 1:
        target = max(1, int(logical_cores) // int(workers))
        mode = "auto_parallel_cap"
    if target <= 0:
        target = before
    try:
        numba.set_num_threads(int(target))
    except Exception as exc:
        payload["numba_error"] = str(exc)
        target = before

    payload.update(
        {
            "numba_available": True,
            "numba_version": getattr(numba, "__version__", None),
            "numba_threads_before": before,
            "numba_threads_active": int(numba.get_num_threads()),
            "numba_threads_requested": int(requested_threads),
            "numba_threads_mode": mode,
            "numba_threading_layer": getattr(numba.config, "THREADING_LAYER", None),
            "logical_cores": int(logical_cores),
        }
    )
    return payload


def format_numba_runtime_line(metadata: dict[str, Any]) -> str:
    """Return a compact console line describing the active Numba runtime."""
    if not metadata.get("numba_available"):
        error = metadata.get("numba_error")
        suffix = f" ({error})" if error else ""
        return f"Numba: unavailable{suffix}; benchmark JIT fallback is pure Python"
    suite_jit = metadata.get("suite_jit_enabled")
    suite_text = "n/a" if suite_jit is None else ("enabled" if suite_jit else "disabled")
    return (
        "Numba: available "
        f"v{metadata.get('numba_version')} | suite JIT={suite_text} | "
        f"threads={metadata.get('numba_threads_active')} "
        f"(mode={metadata.get('numba_threads_mode')}, before={metadata.get('numba_threads_before')})"
    )
