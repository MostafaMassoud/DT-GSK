"""Tests for the publication strict-source guard (PAPER_BUILD_PROMPT.md Section 2.3).

Strict mode (``GSK_STRICT_SOURCE=1`` or ``set_strict_source(True)``, threaded
from ``gsk-stats --strict-source``) must:

* refuse the ``results/_run_all`` reproduced fallback (loader and resolver);
* fail loudly when a requested cell is missing from the immutable evidence
  release instead of silently reading staging data;
* allow (and log) loads from ``benchmarks/cec_reference_results/``;
* leave default (non-strict) behaviour completely unchanged.
"""

from __future__ import annotations

import logging
from pathlib import Path

import pytest

from gsk_family.analysis import result_loader
from gsk_family.analysis.result_loader import (
    PROVENANCE_IMPORTED,
    PROVENANCE_REPRODUCED,
    STRICT_SOURCE_ENV,
    StrictSourceViolation,
    _reproduced_csv_path,
    clear_source_audit,
    get_source_audit,
    load_algorithm,
    load_reproduced,
    load_summary_csv,
    set_strict_source,
    strict_source_enabled,
)

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_BENCHMARKS = _PROJECT_ROOT / "benchmarks" / "cec_reference_results"


@pytest.fixture(autouse=True)
def _reset_strict_state(monkeypatch):
    """Isolate strict-mode global state (env var, override, audit log)."""
    monkeypatch.delenv(STRICT_SOURCE_ENV, raising=False)
    set_strict_source(None)
    clear_source_audit()
    yield
    set_strict_source(None)
    clear_source_audit()


def _write_staging_summary(root: Path, alg: str, suite_lower: str, dim: int) -> Path:
    """Create a minimal results/_run_all-style staging summary CSV fixture."""
    path = root / alg / suite_lower / "summary" / f"{alg}_{suite_lower}_D{dim}.csv"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "Function,Best,Median,Mean,Worst,SD\n1,0.0,0.0,0.0,0.0,0.0\n",
        encoding="utf-8",
    )
    return path


class TestModeSwitching:
    def test_default_is_non_strict(self):
        assert not strict_source_enabled()

    def test_env_var_enables_strict(self, monkeypatch):
        monkeypatch.setenv(STRICT_SOURCE_ENV, "1")
        assert strict_source_enabled()
        monkeypatch.setenv(STRICT_SOURCE_ENV, "0")
        assert not strict_source_enabled()

    def test_set_strict_source_overrides_env(self, monkeypatch):
        monkeypatch.setenv(STRICT_SOURCE_ENV, "0")
        set_strict_source(True)
        assert strict_source_enabled()
        set_strict_source(None)  # back to env
        assert not strict_source_enabled()


class TestStrictBlocksStagingFallback:
    """Strict mode blocks every route to results/_run_all staging data."""

    def test_load_algorithm_blocks_run_all_fallback(self, tmp_path, monkeypatch):
        # The staging fixture WOULD resolve in default mode (no such
        # algorithm exists in the reference tree) ...
        _write_staging_summary(tmp_path, "fake-alg", "cec2017", 10)
        r = load_algorithm("fake-alg", "CEC2017", 10, results_dir=tmp_path)
        assert r is not None and r.provenance == PROVENANCE_REPRODUCED

        # ... but strict mode refuses the fallback and fails loudly.
        monkeypatch.setenv(STRICT_SOURCE_ENV, "1")
        with pytest.raises(StrictSourceViolation) as exc:
            load_algorithm("fake-alg", "CEC2017", 10, results_dir=tmp_path)
        msg = str(exc.value)
        assert "strict-source" in msg
        assert "Section 2.3" in msg

    def test_load_reproduced_refuses_in_strict_mode(self, tmp_path, monkeypatch):
        _write_staging_summary(tmp_path, "gsk", "cec2017", 10)
        monkeypatch.setenv(STRICT_SOURCE_ENV, "1")
        with pytest.raises(StrictSourceViolation):
            load_reproduced("gsk", "CEC2017", 10, results_dir=tmp_path)

    def test_reproduced_resolver_refuses_in_strict_mode(self, tmp_path, monkeypatch):
        # Guards the family_report proposed-CSV fallback, which resolves via
        # this private helper rather than load_reproduced().
        _write_staging_summary(tmp_path, "dt-gsk", "cec2017", 30)
        monkeypatch.setenv(STRICT_SOURCE_ENV, "1")
        with pytest.raises(StrictSourceViolation):
            _reproduced_csv_path("dt-gsk", "CEC2017", 30, tmp_path)

    def test_open_chokepoint_refuses_non_reference_file(self, tmp_path, monkeypatch):
        csv_path = tmp_path / "outside.csv"
        csv_path.write_text(
            "Function,Best,Median,Mean,Worst,SD\n1,0,0,0,0,0\n", encoding="utf-8"
        )
        monkeypatch.setenv(STRICT_SOURCE_ENV, "1")
        with pytest.raises(StrictSourceViolation):
            load_summary_csv(csv_path)


class TestStrictAllowsReference:
    def test_reference_load_allowed_and_tagged(self, monkeypatch):
        if not (_BENCHMARKS / "cec2017" / "gsk").is_dir():
            pytest.skip("reference tree not available")
        monkeypatch.setenv(STRICT_SOURCE_ENV, "1")
        r = load_algorithm("gsk", "CEC2017", 10)
        assert r is not None
        assert r.provenance == PROVENANCE_IMPORTED
        assert Path(r.source_path).resolve().is_relative_to(_BENCHMARKS.resolve())

    def test_missing_reference_cell_fails_loudly(self, monkeypatch):
        monkeypatch.setenv(STRICT_SOURCE_ENV, "1")
        with pytest.raises(StrictSourceViolation) as exc:
            load_algorithm("no-such-optimizer", "CEC2017", 10)
        assert "missing from the" in str(exc.value)


class TestSourceAuditLog:
    def test_strict_load_records_opened_path(self, monkeypatch):
        if not (_BENCHMARKS / "cec2017" / "gsk").is_dir():
            pytest.skip("reference tree not available")
        monkeypatch.setenv(STRICT_SOURCE_ENV, "1")
        clear_source_audit()
        r = load_algorithm("gsk", "CEC2017", 10)
        audit = get_source_audit()
        assert len(audit) == 1
        assert audit[0]["path"] == str(Path(r.source_path).resolve())
        assert audit[0]["role"] == "summary_csv"

    def test_non_strict_load_is_logged_too(self):
        if not (_BENCHMARKS / "cec2017" / "gsk").is_dir():
            pytest.skip("reference tree not available")
        clear_source_audit()
        load_algorithm("gsk", "CEC2017", 10)
        assert len(get_source_audit()) == 1

    def test_module_logger_emits_opened_path(self, caplog):
        if not (_BENCHMARKS / "cec2017" / "gsk").is_dir():
            pytest.skip("reference tree not available")
        with caplog.at_level(logging.INFO, logger=result_loader.__name__):
            load_algorithm("gsk", "CEC2017", 10)
        assert "evidence source opened" in caplog.text


class TestDefaultBehaviourUnchanged:
    def test_non_strict_fallback_still_works(self, tmp_path):
        staged = _write_staging_summary(tmp_path, "fake-alg", "cec2017", 10)
        r = load_algorithm("fake-alg", "CEC2017", 10, results_dir=tmp_path)
        assert r is not None
        assert r.provenance == PROVENANCE_REPRODUCED
        assert Path(r.source_path) == staged

    def test_non_strict_missing_returns_none(self):
        assert load_algorithm("no-such-optimizer", "CEC2017", 10) is None


class TestStatsCliStrictSource:
    def test_cli_strict_source_runs_and_writes_source_audit(self, tmp_path):
        if not (_BENCHMARKS / "cec2011" / "dt-gsk").is_dir():
            pytest.skip("reference tree not available")
        from gsk_family.cli import stats as stats_cli

        out_dir = tmp_path / "out"
        empty_results = tmp_path / "empty_results"
        empty_results.mkdir()
        rc = stats_cli.main([
            "--suite", "CEC2011",
            "--no-figures",
            "--strict-source",
            "--results-root", str(empty_results),
            "--reference-root", str(_BENCHMARKS),
            "--out", str(out_dir),
        ])
        assert rc == 0
        audit_csv = out_dir / "source_use_audit.csv"
        assert audit_csv.is_file()
        lines = audit_csv.read_text(encoding="utf-8").strip().splitlines()
        assert lines[0] == "role,path"
        opened = [line.split(",", 1)[1] for line in lines[1:]]
        assert len(opened) >= 7  # proposed + 6 family comparators at minimum
        bench = str(_BENCHMARKS.resolve())
        assert all(p.startswith(bench) for p in opened)
        # strict mode must be restored after the CLI returns
        assert not strict_source_enabled()
