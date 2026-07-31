"""A zero-new-runs resume must not rewrite a bank's production provenance.

environment.json records the git commit, statistics basis and wall time of the
invocation that actually produced runs. Before 2026-07-28 the finalize block
rewrote it unconditionally, so re-invoking the same command over a completed
bank replaced the production commit with resume-time HEAD, nulled
``statistics_basis`` (``artifacts`` is empty on a full skip), and recorded the
no-op's wall time -- and a null statistics_basis silently disables the
known-optimum hard checks in later verification passes. Discovered while
auditing the stopped CEC2020 campaign (production_deviation_record.md D-8.5).

verification.json, by contrast, is DERIVED metadata and is deliberately still
rewritten on resume -- that is the sanctioned regeneration path for banks whose
verdict predates the NOT_VERIFIED/NO_REFERENCE fix (D-8.1).
"""

from __future__ import annotations

import json
from pathlib import Path

from gsk_family.cli.run import main


def _invoke(root: Path, out: Path) -> int:
    return main(
        [
            "--root", str(root),
            "--optimizer", "gsk",
            "--suite", "sphere",
            "--functions", "1",
            "--dimensions", "5",
            "--runs", "2",
            "--max-evaluations", "300",
            "--seed", "20240620",
            "--seed-policy", "unified",
            "--rand-generator", "threefry",
            "--serial",
            "--no-convergence-graphs",
            "--output-root", str(out),
        ]
    )


def test_zero_new_runs_resume_preserves_environment_json(tmp_path: Path) -> None:
    out = tmp_path / "results"
    project_root = Path(__file__).resolve().parents[2]

    assert _invoke(project_root, out) == 0
    summary = out / "gsk" / "sphere" / "summary"
    env_path = summary / "environment.json"
    per_run_path = summary / "per_run.csv"
    assert env_path.is_file() and per_run_path.is_file()

    env_bytes = env_path.read_bytes()
    per_run_bytes = per_run_path.read_bytes()
    env = json.loads(env_bytes)
    # The production record must be intact to begin with.
    assert env["statistics_basis"] == "error_vs_optimum"

    # Second, identical invocation: every (function, dim, run, seed) is banked,
    # so zero tasks dispatch and the finalize block runs with artifacts == [].
    assert _invoke(project_root, out) == 0

    assert env_path.read_bytes() == env_bytes, (
        "zero-new-runs resume rewrote environment.json -- production provenance "
        "(git_commit / statistics_basis / runtime) must survive a resume"
    )
    assert per_run_path.read_bytes() == per_run_bytes

    # And the derived verification verdict is honest for a reference-less suite.
    verification = json.loads((summary / "verification.json").read_text(encoding="utf-8"))
    assert verification["verdict"] == "NOT_VERIFIED"
    assert verification["reason"] == "NO_REFERENCE"
