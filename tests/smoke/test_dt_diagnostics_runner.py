"""Smoke test: DT-GSK diagnostics flow end-to-end through the runner.

With ``dt_diagnostics`` enabled, the runner injects the per-cell output
directory + run number and the adapter writes one JSONL trace under
``<output_root>/dt-gsk/<suite>/diagnostics/``.
"""

from __future__ import annotations

import json
from pathlib import Path

from gsk_family.runners.run_experiment import run_experiment


def test_runner_writes_diagnostics(tmp_path: Path) -> None:
    out = tmp_path / "results"
    run_experiment(
        {
            "optimizers": ["dt-gsk"],
            "suite": "sphere",
            "functions": [1],
            "dimensions": [4],
            "runs": 1,
            "seed": 20240620,
            "max_evaluations": 80,
            "parallel": False,
            "convergence_graphs": False,
            "output_root": str(out),
            "reference_root": str(tmp_path / "refs"),
            "optimizer_options": {"dt_diagnostics": True},
            "overwrite": True,
            "console_log": False,
        }
    )
    diag = out / "dt-gsk" / "sphere" / "diagnostics"
    files = list(diag.glob("*.jsonl"))
    assert files, f"expected a diagnostics jsonl under {diag}"
    assert files[0].name.startswith("DTTrace_sphere_F1_D4_R1_S")
    first = json.loads(files[0].read_text(encoding="utf-8").splitlines()[0])
    assert first["optimizer"] == "dt-gsk"
    assert first["suite"] == "sphere"
    assert first["function"] == 1 and first["dimension"] == 4 and first["run"] == 1


def test_runner_writes_no_diagnostics_by_default(tmp_path: Path) -> None:
    out = tmp_path / "results"
    run_experiment(
        {
            "optimizers": ["dt-gsk"],
            "suite": "sphere",
            "functions": [1],
            "dimensions": [4],
            "runs": 1,
            "seed": 20240620,
            "max_evaluations": 80,
            "parallel": False,
            "convergence_graphs": False,
            "output_root": str(out),
            "reference_root": str(tmp_path / "refs"),
            "overwrite": True,
            "console_log": False,
        }
    )
    assert not (out / "dt-gsk" / "sphere" / "diagnostics").exists()
