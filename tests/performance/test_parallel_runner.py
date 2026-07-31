from __future__ import annotations

import json
from pathlib import Path

import pytest

from gsk_family.runners.run_experiment import run_experiment


def _config(output_root: Path, *, parallel: bool, backend: str = "thread") -> dict[str, object]:
    return {
        "optimizers": ["gsk"],
        "suite": "sphere",
        "functions": [1],
        "dimensions": [4],
        "runs": 3,
        "seed": 20240620,
        "seed_policy": "unified",
        "rand_generator": "threefry",
        "max_evaluations": 80,
        "overwrite": True,
        "parallel": parallel,
        "parallel_backend": backend,
        "workers": 2,
        "warmup": True,
        "profile": True,
        "generation_logs": True,
        "convergence_graphs": True,
        "data_root": str(output_root.parent / "cec_suite_python"),
        "reference_root": str(output_root.parent / "references"),
        "output_root": str(output_root),
        "optimizer_options": {"np": 20},
    }


@pytest.mark.slow
@pytest.mark.parametrize("backend", ["thread", "process"])
def test_parallel_runner_matches_serial_numeric_artifacts(tmp_path: Path, backend: str) -> None:
    serial_root = tmp_path / "serial"
    parallel_root = tmp_path / "parallel"

    run_experiment(_config(serial_root, parallel=False))
    run_experiment(_config(parallel_root, parallel=True, backend=backend))

    serial = serial_root / "gsk" / "sphere"
    parallel = parallel_root / "gsk" / "sphere"
    deterministic_files = [
        Path("summary") / "gsk_sphere_D4.csv",
        Path("summary") / "seed_schedule.csv",
        Path("gen_logs") / "CheckpointErrors_gsk_F1_D4.csv",
    ]
    for relative in deterministic_files:
        assert (serial / relative).read_bytes() == (parallel / relative).read_bytes()

    serial_curves = sorted((serial / "curves").glob("Figure_F1_D4_Run#*.csv"))
    parallel_curves = sorted((parallel / "curves").glob("Figure_F1_D4_Run#*.csv"))
    assert [path.name for path in serial_curves] == [path.name for path in parallel_curves]
    assert serial_curves[0].read_bytes() == parallel_curves[0].read_bytes()

    profile = json.loads((parallel / "summary" / "profile.json").read_text(encoding="utf-8"))
    assert profile["parallel"] is True
    assert profile["parallel_backend"] == backend
    assert profile["workers"] == 2
    assert profile["tasks_dispatched"] == 3
    assert profile["tasks_completed"] == 3
    assert profile["benchmark_warmup_seconds_total"] >= 0.0
    assert profile["benchmark_warmup"][0]["suite"] == "sphere"
    assert profile["warmup_scope"] == "selected"
    assert profile["generation_logs_enabled"] is True
    assert profile["convergence_graphs_enabled"] is True

    environment = json.loads((parallel / "summary" / "environment.json").read_text(encoding="utf-8"))
    assert environment["use_parallel"] is True
    assert environment["parallel_backend"] == backend
    assert environment["workers"] == 2
    assert environment["warmup_enabled"] is True
    assert environment["warmup_scope"] == "selected"
    assert environment["profile_enabled"] is True
    assert environment["generation_logs_enabled"] is True
    assert environment["convergence_graphs_enabled"] is True
