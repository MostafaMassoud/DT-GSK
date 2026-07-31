"""Deterministic parallel task helpers for experiment runs."""

from __future__ import annotations

import os
import time
import traceback as _traceback
from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait
from dataclasses import dataclass
from typing import Any, Callable


DEFAULT_WORKER_COUNT = 2
DEFAULT_CEC_PROCESS_WORKER_CAP = 8


@dataclass(frozen=True)
class RunTask:
    """One independent optimizer/suite/function/dimension/run task."""

    optimizer: str
    function: int
    dimension: int
    run: int
    seed: int


@dataclass(frozen=True)
class RunTaskOutcome:
    """Task result or captured exception."""

    task: RunTask
    result: Any | None = None
    error: BaseException | None = None
    # Full traceback text for ``error``. For process-pool tasks the remote
    # (worker-side) traceback is preferred when the executor attached one;
    # without this, a failed campaign records only ``str(error)``, which for
    # e.g. MemoryError is the empty string.
    traceback_text: str | None = None


def _format_error_traceback(exc: BaseException) -> str:
    """Best-available traceback for a task exception (remote first)."""
    cause = exc.__cause__
    if cause is not None and type(cause).__name__ == "_RemoteTraceback":
        return str(cause)
    return "".join(_traceback.format_exception(type(exc), exc, exc.__traceback__))


ProgressCallback = Callable[[int, int, RunTask, RunTaskOutcome], None]
HeartbeatCallback = Callable[[int, int], None]


def default_worker_count(logical_cores: int | None = None) -> int:
    """Return the default deterministic parallel worker count.

    The project default is intentionally conservative: use two workers when at
    least two logical CPU cores are available, otherwise use one worker. Larger
    campaigns should increase concurrency explicitly with ``--workers N`` after
    checking that the machine has enough CPU and memory headroom.
    """
    cores = os.cpu_count() if logical_cores is None else int(logical_cores)
    if cores is None or cores <= 0:
        cores = 1
    return max(1, min(DEFAULT_WORKER_COUNT, cores))


def effective_worker_count(
    workers: int,
    *,
    suite: str,
    function: int | None = None,
    parallel: bool,
    parallel_backend: str,
    workers_auto: bool,
) -> int:
    """Return the effective worker count for an experiment run.

    ``default_worker_count`` keeps automatic runs small. A small set of CEC2017
    composition cells JIT-compile heavy Numba/LLVM kernels inside spawned worker
    processes; on typical workstation memory, letting too many automatic workers
    compile those cells at once can exhaust LLVM memory. Explicit ``--workers``
    values are respected, but automatic CEC2017 composition cells are capped to
    a conservative memory-safe count.
    """
    count = max(1, int(workers))
    if (
        parallel
        and str(parallel_backend).lower() == "process"
        and bool(workers_auto)
        and str(suite).lower() == "cec2017"
        and function is not None
        and int(function) >= 21
    ):
        return min(count, DEFAULT_CEC_PROCESS_WORKER_CAP)
    return count


def _collect_future_outcomes(
    tasks: list[RunTask],
    submit: Callable[[RunTask], Any],
    *,
    progress: ProgressCallback | None,
    heartbeat: HeartbeatCallback | None,
    heartbeat_seconds: float,
) -> list[RunTaskOutcome]:
    """Submit each task via ``submit`` and collect outcomes in submission order."""
    total = len(tasks)
    indexed: dict[Any, tuple[int, RunTask]] = {}
    outcomes_by_index: dict[int, RunTaskOutcome] = {}
    for index, task in enumerate(tasks):
        future = submit(task)
        indexed[future] = (index, task)
    pending = set(indexed)
    heartbeat_interval = max(0.001, float(heartbeat_seconds))
    next_heartbeat = time.perf_counter() + heartbeat_interval
    completed = 0
    while pending:
        timeout = None
        if heartbeat is not None:
            timeout = max(0.0, next_heartbeat - time.perf_counter())
        done, pending = wait(pending, timeout=timeout, return_when=FIRST_COMPLETED)
        if not done:
            if heartbeat is not None:
                heartbeat(completed, total)
            next_heartbeat = time.perf_counter() + heartbeat_interval
            continue
        for future in done:
            completed += 1
            index, task = indexed[future]
            try:
                outcome = RunTaskOutcome(task=task, result=future.result())
            except BaseException as exc:
                outcome = RunTaskOutcome(
                    task=task, error=exc, traceback_text=_format_error_traceback(exc)
                )
            outcomes_by_index[index] = outcome
            if progress is not None:
                progress(completed, total, task, outcome)
    return [outcomes_by_index[index] for index in range(len(tasks))]


def execute_run_tasks(
    tasks: list[RunTask],
    runner: Callable[[RunTask], Any],
    *,
    parallel: bool,
    workers: int,
    progress: ProgressCallback | None = None,
    heartbeat: HeartbeatCallback | None = None,
    heartbeat_seconds: float = 30.0,
    executor: Any | None = None,
    process_fn: Callable[[RunTask], Any] | None = None,
) -> list[RunTaskOutcome]:
    """Execute tasks deterministically, preserving input order in the result.

    When ``executor`` and ``process_fn`` are provided (the process backend), tasks
    are submitted to that shared, caller-owned pool. Otherwise a local thread pool
    is used, and trivial cases (serial, single worker, or single task) run inline.
    """
    total = len(tasks)
    if not parallel or workers <= 1 or len(tasks) <= 1:
        outcomes: list[RunTaskOutcome] = []
        for completed, task in enumerate(tasks, start=1):
            try:
                outcome = RunTaskOutcome(task=task, result=runner(task))
            except BaseException as exc:
                outcome = RunTaskOutcome(
                    task=task, error=exc, traceback_text=_format_error_traceback(exc)
                )
            outcomes.append(outcome)
            if progress is not None:
                progress(completed, total, task, outcome)
        return outcomes

    if executor is not None and process_fn is not None:
        return _collect_future_outcomes(
            tasks,
            lambda task: executor.submit(process_fn, task),
            progress=progress,
            heartbeat=heartbeat,
            heartbeat_seconds=heartbeat_seconds,
        )

    with ThreadPoolExecutor(max_workers=int(workers)) as pool:
        return _collect_future_outcomes(
            tasks,
            lambda task: pool.submit(runner, task),
            progress=progress,
            heartbeat=heartbeat,
            heartbeat_seconds=heartbeat_seconds,
        )
