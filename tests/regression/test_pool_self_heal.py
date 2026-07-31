"""Regression: the process-pool self-heal path completes with correct results.

The runner's per-cell loop (``run_experiment``) treats a ``BrokenProcessPool``
(a spawned worker dying — intermittent Numba/spawn crash or OOM) as recoverable:
it tears the pool down and rebuilds it up to ``max_pool_rebuilds`` (3) times,
and if the pool is still unstable it runs that cell on the reliable **serial**
backend before rebuilding a fresh pool for the next cell. It deliberately never
falls back to the thread backend (parallel Numba kernels can deadlock across many
Python threads). That self-heal is a real robustness guarantee.

These tests inject the fault at the ``execute_run_tasks`` boundary — no real
worker crashes, no timing dependence — and assert that:

1. a transient break recovers on a pool rebuild (no serial fallback needed), and
2. a persistent break exhausts the rebuild budget and falls back to serial,

and that in **both** cases the campaign still completes with per-cell results
byte-identical to a pure-serial run. ``ProcessPoolExecutor`` is replaced by a
no-op stand-in so no real processes are spawned; the mocked ``execute_run_tasks``
runs the real optimizer through the passed ``runner`` for the recovering/serial
paths, so the numeric results are genuine.
"""
from __future__ import annotations

from concurrent.futures.process import BrokenProcessPool
from pathlib import Path
from unittest.mock import patch

import gsk_family.runners.run_experiment as rex
from gsk_family.runners.parallel import RunTaskOutcome

#: The runner's rebuild budget before it falls back to the serial backend.
_MAX_POOL_REBUILDS = 3


class _FakePool:
    """Stand-in for ``ProcessPoolExecutor`` that never spawns a process.

    ``execute_run_tasks`` is mocked in these tests, so the pool object is only
    ever created, resized, and shut down — never submitted to. It just needs to
    be a non-``None`` object exposing ``shutdown``.
    """

    def __init__(self, *args: object, **kwargs: object) -> None:
        """Accept and ignore the real executor's constructor arguments."""

    def shutdown(self, *args: object, **kwargs: object) -> None:
        """No-op teardown."""


def _config(output_root: Path, *, parallel: bool) -> dict[str, object]:
    """Return a tiny deterministic gsk/sphere process-backend campaign config."""
    return {
        "optimizers": ["gsk"],
        "suite": "sphere",
        "functions": [1],
        "dimensions": [4],
        "runs": 5,
        "seed": 20240620,
        "seed_policy": "unified",
        "rand_generator": "threefry",
        "max_evaluations": 80,
        "overwrite": True,
        "parallel": parallel,
        "parallel_backend": "process",
        "workers": 2,
        "data_root": str(output_root.parent / "cec_suite_python"),
        "reference_root": str(output_root.parent / "references"),
        "output_root": str(output_root),
        "optimizer_options": {"np": 20},
    }


def _make_fake_execute(break_process_calls: int) -> tuple[object, dict[str, int]]:
    """Return a fake ``execute_run_tasks`` plus a call-counter state dict.

    The fake distinguishes the two backends by the ``executor`` argument:
    a non-``None`` executor is a process-pool call, ``None`` is the serial
    fallback. The first ``break_process_calls`` process calls return
    ``BrokenProcessPool`` outcomes (simulating a dead worker); any later process
    call and every serial call run the real optimizer through ``runner`` so the
    results are genuine.
    """
    state = {"process": 0, "serial": 0}

    def fake(cell_tasks, runner, *, parallel, workers, progress, executor, process_fn):  # type: ignore[no-untyped-def]
        """Injected ``execute_run_tasks`` replacement."""
        if executor is not None:
            state["process"] += 1
            if state["process"] <= break_process_calls:
                return [
                    RunTaskOutcome(task=task, error=BrokenProcessPool("injected worker death"))
                    for task in cell_tasks
                ]
            return [RunTaskOutcome(task=task, result=runner(task)) for task in cell_tasks]
        state["serial"] += 1
        return [RunTaskOutcome(task=task, result=runner(task)) for task in cell_tasks]

    return fake, state


def _summary_bytes(root: Path) -> bytes:
    """Return the raw per-dimension summary CSV for the gsk/sphere run."""
    return (root / "gsk" / "sphere" / "summary" / "gsk_sphere_D4.csv").read_bytes()


def _run_with_injected_faults(output_root: Path, break_process_calls: int) -> dict[str, int]:
    """Run the process-backend campaign with a mocked pool boundary; return call counts."""
    fake, state = _make_fake_execute(break_process_calls)
    with patch.object(rex, "ProcessPoolExecutor", _FakePool), patch.object(
        rex, "execute_run_tasks", side_effect=fake
    ):
        rex.run_experiment(_config(output_root, parallel=True))
    return state


def test_transient_break_recovers_on_pool_rebuild(tmp_path: Path) -> None:
    """Two broken attempts then a healthy rebuild completes the cell in-pool."""
    serial_ref = tmp_path / "serial_ref"
    rex.run_experiment(_config(serial_ref, parallel=False))

    faulted = tmp_path / "faulted"
    state = _run_with_injected_faults(faulted, break_process_calls=2)

    # initial attempt + 2 rebuilds break; the 3rd (still within budget) recovers.
    assert state["process"] == 3
    assert state["serial"] == 0  # recovered before exhausting the rebuild budget
    assert _summary_bytes(faulted) == _summary_bytes(serial_ref)


def test_persistent_break_falls_back_to_serial(tmp_path: Path) -> None:
    """A pool that never recovers exhausts the rebuild budget and runs serial."""
    serial_ref = tmp_path / "serial_ref"
    rex.run_experiment(_config(serial_ref, parallel=False))

    faulted = tmp_path / "faulted"
    state = _run_with_injected_faults(faulted, break_process_calls=1000)

    # initial attempt + max_pool_rebuilds rebuilds all break, then serial fallback.
    assert state["process"] == _MAX_POOL_REBUILDS + 1
    assert state["serial"] == 1
    # the cell still completes with results byte-identical to a pure-serial run.
    assert _summary_bytes(faulted) == _summary_bytes(serial_ref)
