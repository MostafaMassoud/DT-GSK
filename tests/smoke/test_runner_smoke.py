from __future__ import annotations

import csv
import json
from pathlib import Path

import pytest

from gsk_family.runners.run_experiment import run_experiment


def _tiny_config(tmp_path: Path) -> dict[str, object]:
    return {
        "optimizers": ["gsk"],
        "suite": "sphere",
        "functions": [1],
        "dimensions": [4],
        "runs": 2,
        "seed": 20240620,
        "seed_policy": "unified",
        "rand_generator": "threefry",
        "max_evaluations": 80,
        "overwrite": True,
        "parallel": False,
        "data_root": str(tmp_path / "cec_suite_python"),
        "reference_root": str(tmp_path / "references"),
        "output_root": str(tmp_path / "results"),
        "optimizer_options": {"np": 20},
    }


def test_run_experiment_writes_result_schema(tmp_path: Path) -> None:
    summary = run_experiment(_tiny_config(tmp_path))

    assert len(summary.records) == 2
    root = tmp_path / "results" / "gsk" / "sphere"
    summary_dir = root / "summary"
    curves_dir = root / "curves"
    graphs_dir = curves_dir / "graphs"
    gen_logs_dir = root / "gen_logs"

    assert summary_dir.is_dir()
    assert curves_dir.is_dir()
    assert graphs_dir.is_dir()
    assert gen_logs_dir.is_dir()

    expected_files = [
        summary_dir / "per_run.csv",
        summary_dir / "seed_schedule.csv",
        summary_dir / "environment.json",
        summary_dir / "verification.json",
        summary_dir / "gsk_sphere_D4.csv",
    ]
    for path in expected_files:
        assert path.exists(), path
    assert (gen_logs_dir / "CheckpointErrors_gsk_F1_D4.csv").exists()
    assert len(list(curves_dir.glob("Figure_F1_D4_Run#*.csv"))) == 1

    with (summary_dir / "per_run.csv").open("r", newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 2
    assert {row["termination"] for row in rows} == {"max_evaluations"}
    assert {int(row["nfes"]) for row in rows} == {80}

    env = json.loads((summary_dir / "environment.json").read_text(encoding="utf-8"))
    assert env["initial_population_policy"] == "runner_supplied_X0"
    assert env["statistics_basis"] == "error_vs_optimum"
    assert env["generation_logs_enabled"] is True
    assert env["convergence_graphs_enabled"] is False
    assert env["console_log_enabled"] is True
    assert "numba_runtime" in env
    assert (summary_dir / "run_config.json").exists()
    assert (summary_dir / "phase0_protocol.json").exists()
    assert list(summary_dir.glob("gsk_D4_log_*.txt"))
    assert list(summary_dir.glob("gsk_D4_runs_log_*.txt"))


def test_run_experiment_logs_to_console_by_default(tmp_path: Path, capsys) -> None:
    config = _tiny_config(tmp_path)
    config["runs"] = 1

    run_experiment(config)

    stdout = capsys.readouterr().out
    assert "==================== run_all (SPHERE) ====================" in stdout
    assert "----- [1/1] GSK -----" in stdout
    assert "DETAILED CONFIGURATION" in stdout
    assert "Numba: " in stdout
    assert "| gsk - SPHERE - D=4" in stdout
    assert "|  F01   |" in stdout
    assert "[finalize] GSK" in stdout
    assert "PASS  GSK" in stdout
    assert "==================== done ====================" in stdout


def test_cec2011_console_uses_single_native_function_table(tmp_path: Path, capsys) -> None:
    config = _tiny_config(tmp_path)
    config.update(
        {
            "suite": "cec2011",
            "functions": [1, 2, 3],
            "dimensions": "native",
            "runs": 1,
            "max_evaluations": 40,
            "parallel": False,
        }
    )

    run_experiment(config)

    stdout = capsys.readouterr().out
    assert stdout.count("| gsk - CEC2011 - native dimensions") == 1
    assert "| gsk - CEC2011 - D=" not in stdout
    assert "|  Func  |     Best     |    Median    |     Mean     |    Worst     |      SD      |   Time/s    |" in stdout
    assert "|  F01   |" in stdout
    assert "|  F02   |" in stdout
    assert "|  F03   |" in stdout

    rollup_path = tmp_path / "results" / "gsk" / "cec2011" / "summary" / "gsk_cec2011.csv"
    with rollup_path.open("r", newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    assert [int(row["Function"]) for row in rows] == [1, 2, 3]


def test_run_experiment_quiet_disables_console_log(tmp_path: Path, capsys) -> None:
    config = _tiny_config(tmp_path)
    config["runs"] = 1
    config["console_log"] = False

    run_experiment(config)

    assert capsys.readouterr().out == ""


def test_run_experiment_writes_generation_logs_when_enabled(tmp_path: Path) -> None:
    config = _tiny_config(tmp_path)
    config["generation_logs"] = True

    run_experiment(config)

    log_path = (
        tmp_path
        / "results"
        / "gsk"
        / "sphere"
        / "gen_logs"
        / "CheckpointErrors_gsk_F1_D4.csv"
    )
    assert log_path.exists()


def test_run_experiment_does_not_write_convergence_graphs_by_default(tmp_path: Path) -> None:
    config = _tiny_config(tmp_path)

    run_experiment(config)

    root = tmp_path / "results" / "gsk" / "sphere"
    assert len(list((root / "curves").glob("Figure_F1_D4_Run#*.csv"))) == 1
    assert not list((root / "curves" / "graphs").glob("Figure_F1_D4.png"))
    env = json.loads((root / "summary" / "environment.json").read_text(encoding="utf-8"))
    assert env["convergence_graphs_enabled"] is False


def test_run_experiment_can_enable_convergence_graphs(tmp_path: Path) -> None:
    config = _tiny_config(tmp_path)
    config["convergence_graphs"] = True

    run_experiment(config)

    root = tmp_path / "results" / "gsk" / "sphere"
    assert len(list((root / "curves").glob("Figure_F1_D4_Run#*.csv"))) == 1
    assert list((root / "curves" / "graphs").glob("Figure_F1_D4.png"))
    env = json.loads((root / "summary" / "environment.json").read_text(encoding="utf-8"))
    assert env["convergence_graphs_enabled"] is True


def test_run_experiment_can_disable_convergence_graphs_from_explicit_true(tmp_path: Path) -> None:
    config = _tiny_config(tmp_path)
    config["convergence_graphs"] = True
    run_experiment(config)

    config["convergence_graphs"] = False

    run_experiment(config)

    root = tmp_path / "results" / "gsk" / "sphere"
    assert len(list((root / "curves").glob("Figure_F1_D4_Run#*.csv"))) == 1
    assert not list((root / "curves" / "graphs").glob("Figure_F1_D4.png"))
    env = json.loads((root / "summary" / "environment.json").read_text(encoding="utf-8"))
    assert env["convergence_graphs_enabled"] is False


def test_run_experiment_refuses_reference_output_root(tmp_path: Path) -> None:
    config = _tiny_config(tmp_path)
    config["output_root"] = config["reference_root"]

    with pytest.raises(ValueError, match="Refusing"):
        run_experiment(config)


def test_unified_seed_schedule_matches_for_future_optimizers(tmp_path: Path) -> None:
    config = _tiny_config(tmp_path)
    config["optimizers"] = ["gsk", "atmals-gsk"]
    config["runs"] = 1
    config["optimizer_options"] = {"np": 20, "protocol": "cec2017"}

    summary = run_experiment(config)

    assert len(summary.records) == 2
    assert not summary.skipped_cells

    def read_schedule(optimizer: str) -> list[dict[str, str]]:
        path = tmp_path / "results" / optimizer / "sphere" / "summary" / "seed_schedule.csv"
        with path.open("r", newline="", encoding="utf-8") as handle:
            return list(csv.DictReader(handle))

    assert read_schedule("gsk") == read_schedule("atmals-gsk")


def test_run_experiment_executes_agsk_optimizer(tmp_path: Path) -> None:
    config = _tiny_config(tmp_path)
    config["optimizers"] = ["agsk"]
    config["runs"] = 1
    config["optimizer_options"] = {"np_init": 20, "min_pop_size": 12}

    summary = run_experiment(config)

    assert len(summary.records) == 1
    assert not summary.skipped_cells
    record = summary.records[0]
    assert record.optimizer == "agsk"
    assert record.nfes <= 80
    assert (tmp_path / "results" / "agsk" / "sphere" / "summary" / "per_run.csv").exists()


def test_run_experiment_executes_apgsk_optimizer(tmp_path: Path) -> None:
    config = _tiny_config(tmp_path)
    config["optimizers"] = ["apgsk"]
    config["runs"] = 1
    config["optimizer_options"] = {"np_init": 20, "min_pop_size": 12}

    summary = run_experiment(config)

    assert len(summary.records) == 1
    assert not summary.skipped_cells
    record = summary.records[0]
    assert record.optimizer == "apgsk"
    assert record.nfes <= 80
    assert (tmp_path / "results" / "apgsk" / "sphere" / "summary" / "per_run.csv").exists()


def test_run_experiment_executes_fdb_agsk_optimizer(tmp_path: Path) -> None:
    config = _tiny_config(tmp_path)
    config["optimizers"] = ["fdb-agsk"]
    config["runs"] = 1
    config["optimizer_options"] = {"fdb_case": 1, "np_init": 20, "min_pop_size": 12}

    summary = run_experiment(config)

    assert len(summary.records) == 1
    assert not summary.skipped_cells
    record = summary.records[0]
    assert record.optimizer == "fdb-agsk"
    assert record.nfes <= 80
    assert (
        tmp_path / "results" / "fdb-agsk" / "sphere" / "summary" / "per_run.csv"
    ).exists()


def test_run_experiment_executes_atmals_gsk_optimizer(tmp_path: Path) -> None:
    config = _tiny_config(tmp_path)
    config["optimizers"] = ["atmals-gsk"]
    config["runs"] = 1
    config["optimizer_options"] = {"np": 20, "protocol": "cec2017"}

    summary = run_experiment(config)

    assert len(summary.records) == 1
    assert not summary.skipped_cells
    record = summary.records[0]
    assert record.optimizer == "atmals-gsk"
    assert record.nfes <= 80
    assert (
        tmp_path / "results" / "atmals-gsk" / "sphere" / "summary" / "per_run.csv"
    ).exists()
