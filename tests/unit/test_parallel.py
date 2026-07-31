from __future__ import annotations

import time

from gsk_family.runners.parallel import RunTask, execute_run_tasks


def test_parallel_executor_emits_heartbeat_while_tasks_are_running() -> None:
    tasks = [
        RunTask(optimizer="gsk", function=1, dimension=10, run=1, seed=101),
        RunTask(optimizer="gsk", function=1, dimension=10, run=2, seed=102),
    ]
    heartbeats: list[tuple[int, int]] = []

    def runner(task: RunTask) -> int:
        time.sleep(0.10)
        return task.run

    outcomes = execute_run_tasks(
        tasks,
        runner,
        parallel=True,
        workers=2,
        heartbeat=lambda completed, total: heartbeats.append((completed, total)),
        heartbeat_seconds=0.01,
    )

    assert heartbeats
    assert all(total == 2 for _completed, total in heartbeats)
    assert [outcome.result for outcome in outcomes] == [1, 2]
