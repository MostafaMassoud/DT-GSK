"""Unit tests for scripts/build_stats_panel.py on synthetic summary trees."""

from __future__ import annotations

import csv
import importlib.util
import json
from pathlib import Path

import pytest

_SPEC = importlib.util.spec_from_file_location(
    "build_stats_panel",
    Path(__file__).resolve().parents[2] / "scripts" / "build_stats_panel.py",
)
_MOD = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_MOD)


def _write(path: Path, means: dict[int, float]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["Function", "Best", "Median", "Mean", "Worst", "SD"])
        for func, mean in means.items():
            writer.writerow([func, mean, mean, mean, mean, 0.0])


def _mean(path: Path, func: int) -> float:
    with path.open(newline="", encoding="utf-8") as handle:
        return next(float(r["Mean"]) for r in csv.DictReader(handle) if int(r["Function"]) == func)


def _trees(tmp_path: Path) -> tuple[Path, Path]:
    ref = tmp_path / "ref"
    for opt in ("gsk", "agsk", "dt-gsk"):
        for dim in (10, 30):
            _write(ref / "cec2017" / opt / f"{opt}_cec2017_D{dim}.csv", {1: 5.0, 3: 5.0, 4: 5.0})
    _write(ref / "cec2013" / "gsk" / "gsk_cec2013_D10.csv", {1: 7.0})  # another suite: never copied
    res = tmp_path / "my_results"
    _write(res / "dt-gsk" / "cec2017" / "summary" / "dt-gsk_cec2017_D10.csv", {1: 1.0, 3: 1.0, 4: 1.0})
    return ref, res


def test_own_file_replaces_committed_one_and_the_rest_is_kept(tmp_path, capsys):
    ref, res = _trees(tmp_path)
    out = tmp_path / "my_panel"
    assert _MOD.build_panel("CEC2017", res, ref, out) == 0
    panel = out / "cec2017"
    assert _mean(panel / "dt-gsk" / "dt-gsk_cec2017_D10.csv", 1) == 1.0  # yours
    assert _mean(panel / "dt-gsk" / "dt-gsk_cec2017_D30.csv", 1) == 5.0  # committed, not run by you
    assert _mean(panel / "gsk" / "gsk_cec2017_D10.csv", 1) == 5.0
    assert not (out / "cec2013").exists()
    printed = capsys.readouterr().out
    assert "dt-gsk/dt-gsk_cec2017_D10.csv" in printed
    assert "WARNING" not in printed


def test_partial_own_file_is_flagged(tmp_path, capsys):
    ref, res = _trees(tmp_path)
    _write(res / "gsk" / "cec2017" / "summary" / "gsk_cec2017_D30.csv", {1: 2.0})
    assert _MOD.build_panel("cec2017", res, ref, tmp_path / "my_panel") == 0
    assert "WARNING gsk_cec2017_D30.csv: your file has 1 of the 3 functions" in capsys.readouterr().out


def test_rebuild_replaces_its_own_panel_but_not_a_foreign_folder(tmp_path):
    ref, res = _trees(tmp_path)
    out = tmp_path / "my_panel"
    assert _MOD.build_panel("cec2017", res, ref, out) == 0
    assert _MOD.build_panel("cec2017", res, ref, out) == 0  # rebuilt in place
    foreign = tmp_path / "foreign"
    (foreign / "cec2017").mkdir(parents=True)
    (foreign / "cec2017" / "keep.txt").write_text("x", encoding="utf-8")
    assert _MOD.build_panel("cec2017", res, ref, foreign) == 1
    assert (foreign / "cec2017" / "keep.txt").is_file()


def test_missing_inputs_fail_loudly(tmp_path):
    ref, res = _trees(tmp_path)
    assert _MOD.build_panel("cec2017", tmp_path / "nothing", ref, tmp_path / "p") == 1
    assert _MOD.build_panel("cec2017", res, tmp_path / "no_bank", tmp_path / "p") == 1


def test_cec2011_rollup_name_is_recognised():
    assert _MOD.summary_name_matches("gsk_cec2011.csv", "gsk", "cec2011")
    assert not _MOD.summary_name_matches("gsk_cec2011_D30.csv", "gsk", "cec2011")  # gsk-stats reads the rollup only
    assert _MOD.summary_name_matches("gsk_cec2013_D10.csv", "gsk", "cec2013")
    assert not _MOD.summary_name_matches("gsk_cec2013.csv", "gsk", "cec2013")
    assert not _MOD.summary_name_matches("gsk_cec2013lsgo_D1000.csv", "gsk", "cec2013")
    assert not _MOD.summary_name_matches("per_run.csv", "gsk", "cec2013")


def test_reduced_run_is_flagged(tmp_path, capsys):
    ref, res = _trees(tmp_path)
    (ref / "cec2017" / "dt-gsk" / "run_config.json").write_text(
        json.dumps({"runs": 51, "max_nfes_override": 0}), encoding="utf-8"
    )
    (res / "dt-gsk" / "cec2017" / "summary" / "run_config.json").write_text(
        json.dumps({"runs": 5, "max_nfes_override": 2000}), encoding="utf-8"
    )
    assert _MOD.build_panel("cec2017", res, ref, tmp_path / "my_panel") == 0
    printed = capsys.readouterr().out
    assert "WARNING dt-gsk: your last run used a non-default budget (--max-evaluations 2000)" in printed
    assert "WARNING dt-gsk: your last run used 5 run(s) per function, the committed panel 51" in printed


def test_refuses_to_write_inside_the_committed_panel(tmp_path, capsys):
    ref, res = _trees(tmp_path)
    before = sorted(p.as_posix() for p in ref.rglob("*"))
    for out in (ref, ref / "_mine", ref / "cec2017"):
        assert _MOD.build_panel("cec2017", res, ref, out) == 1
    assert "refusing to write inside the committed panel" in capsys.readouterr().out
    assert sorted(p.as_posix() for p in ref.rglob("*")) == before


def test_misspelled_suite_is_rejected_by_the_parser(capsys):
    with pytest.raises(SystemExit):
        _MOD.main(["--suite", "lsgo"])
    assert "cec2013lsgo" in capsys.readouterr().err  # argparse lists the valid choices
