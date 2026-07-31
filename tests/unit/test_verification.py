from __future__ import annotations

import json
from pathlib import Path

from gsk_family.cli.validate import main as validate_main
from gsk_family.runners.verification import compare_generated_to_references, verify_run_directory


def _write_generated(
    root: Path,
    *,
    optimizer: str = "gsk",
    suite: str = "cec2017",
    dim: int = 10,
    row: str = "1,1,1,1,1,0\n",
    max_override: int = 0,
    runs: int = 25,
    basis: str = "error_vs_optimum",
) -> Path:
    run_dir = root / optimizer / suite
    summary = run_dir / "summary"
    summary.mkdir(parents=True)
    (summary / "environment.json").write_text(
        json.dumps(
            {
                "optimizer": optimizer,
                "suite": suite,
                "max_nfes_override": max_override,
                "runs": runs,
                "statistics_basis": basis,
            }
        ),
        encoding="utf-8",
    )
    (summary / f"{optimizer}_{suite}_D{dim}.csv").write_text(
        "Function,Best,Median,Mean,Worst,SD\n" + row,
        encoding="utf-8",
    )
    return run_dir


def _write_reference(
    root: Path,
    *,
    optimizer: str = "gsk",
    suite: str = "cec2017",
    dim: int = 10,
    row: str = "1,1,1,1,1,0\n",
) -> Path:
    ref_dir = root / suite / optimizer
    ref_dir.mkdir(parents=True)
    (ref_dir / f"{optimizer}_{suite}_D{dim}.csv").write_text(
        "Function,Best,Median,Mean,Worst,SD\n" + row,
        encoding="utf-8",
    )
    return root


def test_verification_missing_reference_yields_not_verified_no_reference(tmp_path: Path) -> None:
    """No reference row for any function => NOT_VERIFIED/NO_REFERENCE, never a
    vacuous CONSISTENT (the CEC2013LSGO banks shipped exactly that misleading
    verdict; deviation record D-8.1)."""
    run_dir = _write_generated(tmp_path / "results", row="F1,1,1,1,1,0\n")
    ref_root = tmp_path / "refs"

    result = compare_generated_to_references(run_dir, ref_root, reduced_budget=True)

    assert result.verdict == "NOT_VERIFIED"
    assert result.reason == "NO_REFERENCE"
    assert result.hard_failures == 0
    assert result.functions_checked == 0
    assert result.missing_reference == 1
    assert result.failures[0].kind == "missing_reference"
    # The reason must survive JSON serialization -- promotion and audit tooling
    # read the file, not the dataclass.
    assert result.to_json_dict()["reason"] == "NO_REFERENCE"


def test_verification_negative_error_floor_is_hard_failure(tmp_path: Path) -> None:
    run_dir = _write_generated(tmp_path / "results", row="1,-0.01,0,0,0,0\n")
    ref_root = _write_reference(tmp_path / "refs")

    result = compare_generated_to_references(run_dir, ref_root, reduced_budget=True)

    assert result.verdict == "DEVIATES"
    assert result.hard_failures == 1
    assert any(failure.kind == "negative_error_floor" for failure in result.failures)


def test_reduced_budget_suppresses_gross_deviation_hard_failure(tmp_path: Path) -> None:
    run_dir = _write_generated(tmp_path / "results", row="1,1e9,1e9,1e9,1e9,0\n", max_override=1000, runs=1)
    ref_root = _write_reference(tmp_path / "refs", row="1,1,1,1,1,0\n")

    reduced = compare_generated_to_references(run_dir, ref_root)
    full = compare_generated_to_references(run_dir, ref_root, reduced_budget=False)

    assert reduced.verdict == "CONSISTENT"
    assert reduced.win_tie_loss == (0, 0, 1)
    assert full.verdict == "DEVIATES"
    assert any(failure.kind == "gross_deviation" for failure in full.failures)


def test_verify_run_directory_writes_verification_json(tmp_path: Path) -> None:
    run_dir = _write_generated(tmp_path / "results", row="1,1,1,1,1,0\n")
    ref_root = _write_reference(tmp_path / "refs", row="F1,1,1,1,1,0\n")

    result = verify_run_directory(run_dir, ref_root, reduced_budget=False)

    payload = json.loads((run_dir / "summary" / "verification.json").read_text(encoding="utf-8"))
    assert result.verdict == "CONSISTENT"
    assert payload["verdict"] == "CONSISTENT"
    assert payload["functions_checked"] == 1
    assert payload["win_tie_loss"] == [0, 1, 0]


def test_validate_cli_compare_fails_when_no_functions_are_checked(
    tmp_path: Path,
    capsys,
) -> None:
    run_dir = _write_generated(tmp_path / "results", row="F1,1,1,1,1,0\n")
    ref_root = tmp_path / "refs"

    code = validate_main(["--compare", str(run_dir), str(ref_root), "--reduced"])

    captured = capsys.readouterr()
    assert code == 1
    assert "functions_checked: 0" in captured.out
    assert "validation is inconclusive" in captured.out


def test_validate_cli_default_references_are_checked(capsys) -> None:
    code = validate_main([])

    captured = capsys.readouterr()
    assert code == 0
    assert "reference root:" in captured.out
    assert "csv files:" in captured.out
