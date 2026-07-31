"""Smoke tests for the gsk-stats CLI (gsk_family.cli.stats).

Runs the report end-to-end against a tiny synthetic results/reference tree and
checks the exit codes and that artifacts are written.
"""

from __future__ import annotations

import csv
from pathlib import Path

from gsk_family.cli.stats import main

_FUNCS = [1, 3, 4, 5, 6]


def _write_summary(path: Path, mean: float) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["Function", "Best", "Median", "Mean", "Worst", "SD"])
        for func in _FUNCS:
            writer.writerow([func, mean, mean, mean, mean, 0.0])


def _build_tree(tmp_path: Path) -> tuple[Path, Path]:
    results_root = tmp_path / "results" / "_run_all"
    reference_root = tmp_path / "benchmarks" / "cec_reference_results"
    _write_summary(
        results_root / "dt-gsk" / "cec2017" / "summary" / "dt-gsk_cec2017_D10.csv", 1.0
    )
    _write_summary(reference_root / "cec2017" / "gsk" / "gsk_cec2017_D10.csv", 2.0)
    _write_summary(reference_root / "cec2017" / "agsk" / "agsk_cec2017_D10.csv", 3.0)
    return results_root, reference_root


def test_cli_runs_and_writes_artifacts(tmp_path):
    results_root, reference_root = _build_tree(tmp_path)
    out_dir = tmp_path / "out"
    code = main([
        "--suite", "CEC2017", "--dims", "10",
        "--results-root", str(results_root),
        "--reference-root", str(reference_root),
        "--out", str(out_dir),
        "--no-figures",
    ])
    assert code == 0
    assert (out_dir / "cec2017_statistical_report.txt").is_file()
    assert (out_dir / "cec2017_friedman_ranks.csv").is_file()
    assert (out_dir / "cec2017_friedman_ranks.tex").is_file()


def test_cli_missing_reference_returns_1(tmp_path):
    results_root, _ = _build_tree(tmp_path)
    code = main([
        "--suite", "CEC2017", "--dims", "10",
        "--results-root", str(results_root),
        "--reference-root", str(tmp_path / "does-not-exist"),
        "--out", str(tmp_path / "out"),
        "--no-figures",
    ])
    assert code == 1


def test_cli_no_reproduced_data_returns_1(tmp_path):
    _, reference_root = _build_tree(tmp_path)
    empty_results = tmp_path / "empty_results"
    empty_results.mkdir()
    code = main([
        "--suite", "CEC2017", "--dims", "10",
        "--results-root", str(empty_results),
        "--reference-root", str(reference_root),
        "--out", str(tmp_path / "out"),
        "--no-figures",
    ])
    assert code == 1
