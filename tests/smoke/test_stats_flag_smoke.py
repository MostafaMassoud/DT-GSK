"""Smoke test for the runner's opt-in ``--stats`` per-dimension analysis.

Confirms that ``--stats`` streams the Wilcoxon + Friedman statistical-analysis
block during a run, and that omitting it leaves the default output unchanged.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _env() -> dict[str, str]:
    env = os.environ.copy()
    entries = [str(PROJECT_ROOT / "src"), str(PROJECT_ROOT)]
    existing = env.get("PYTHONPATH")
    if existing:
        entries.append(existing)
    env["PYTHONPATH"] = os.pathsep.join(entries)
    return env


def _run(tmp_path: Path, *extra: str):
    import subprocess

    return subprocess.run(
        [
            sys.executable, "-m", "gsk_family.cli.run",
            "--optimizer", "agsk", "--suite", "cec2017",
            "--dimension", "10", "--function", "1", "--function", "3",
            "--runs", "2", "--seed", "20240620", "--max-evaluations", "500",
            "--output-root", str(tmp_path / "results"), "--overwrite", *extra,
        ],
        cwd=PROJECT_ROOT, env=_env(), text=True, capture_output=True,
        timeout=300, check=False,
    )


def test_stats_flag_streams_analysis(tmp_path: Path) -> None:
    result = _run(tmp_path, "--stats")
    assert result.returncode == 0, result.stderr
    assert "STATISTICAL ANALYSIS -- D=10" in result.stdout
    assert "Wilcoxon Signed-Rank Test: agsk vs" in result.stdout
    # The run is validated against its own reference implementation (AGSK-REF)
    # in addition to the GSK-family comparators.
    assert "AGSK-REF" in result.stdout


def test_default_run_has_no_statistical_analysis(tmp_path: Path) -> None:
    result = _run(tmp_path)
    assert result.returncode == 0, result.stderr
    for marker in ("STATISTICAL ANALYSIS --", "Wilcoxon Signed-Rank Test", "Friedman ranking"):
        assert marker not in result.stdout, f"unexpected stats output: {marker!r}"
