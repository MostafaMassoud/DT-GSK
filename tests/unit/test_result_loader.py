"""Tests for gsk_family.analysis.result_loader.

Ported from the source project's tests/test_result_loader.py and retargeted to
this project's ``results/_run_all/<optimizer>/<suite>/summary/`` reproduced
layout. Schema/parsing/dataclass tests use the committed reference tables under
``benchmarks/cec_reference_results/``.
"""

from pathlib import Path

import pytest

from gsk_family.analysis.result_loader import (
    GSK_FAMILY,
    PROVENANCE_IMPORTED,
    SUITE_DIMS,
    SUITE_EXCLUDED_FUNCS,
    FunctionStats,
    _parse_float,
    _parse_func_id,
    _reproduced_csv_path,
    common_func_ids,
    discover_reference_algorithms,
    load_comparison_set,
    load_reference,
    load_summary_csv,
    provenance_report,
)

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_BENCHMARKS = _PROJECT_ROOT / "benchmarks" / "cec_reference_results"


class TestParseFuncId:
    def test_numeric(self):
        assert _parse_func_id("1") == 1
        assert _parse_func_id("30") == 30

    def test_f_prefix(self):
        assert _parse_func_id("F1") == 1
        assert _parse_func_id("f5") == 5

    def test_whitespace(self):
        assert _parse_func_id("  F1  ") == 1


class TestParseFloat:
    def test_valid(self):
        assert _parse_float("1.23E+04") == 1.23e4
        assert _parse_float("0.00E+00") == 0.0

    def test_empty_and_na(self):
        assert _parse_float("") is None
        assert _parse_float("N/A") is None
        assert _parse_float("—") is None


class TestFunctionStats:
    def test_has_mean(self):
        assert FunctionStats(mean=1.23).has_mean()
        assert not FunctionStats(best=1.0).has_mean()

    def test_full_stats(self):
        assert FunctionStats(best=0.0, median=0.0, mean=0.0, worst=0.0, sd=0.0).has_full_stats()
        assert not FunctionStats(best=0.0, sd=0.0).has_full_stats()

    def test_mean_sd_str(self):
        fs = FunctionStats(mean=1.23e4, sd=5.67e2)
        assert "+/-" in fs.mean_sd_str()
        assert FunctionStats().mean_sd_str() == "N/A"


class TestLoadSchemaA:
    @pytest.fixture
    def gsk_d10(self):
        path = _BENCHMARKS / "cec2017" / "gsk" / "gsk_cec2017_D10.csv"
        if not path.exists():
            pytest.skip("GSK reference CSV not found")
        return load_summary_csv(path)

    def test_loads_all_functions(self, gsk_d10):
        assert len(gsk_d10) == 29  # CEC2017 with F2 already excluded from the CSV

    def test_f1_and_full_stats(self, gsk_d10):
        assert gsk_d10[1].best == 0.0
        for fid, fs in gsk_d10.items():
            assert fs.has_full_stats(), f"F{fid} missing full stats"

    def test_f2_excluded(self, gsk_d10):
        assert 2 not in gsk_d10


class TestHighLevelLoading:
    def test_load_reference_gsk(self):
        r = load_reference("gsk", "CEC2017", 10)
        if r is None:
            pytest.skip("GSK reference not found")
        assert r.algorithm == "gsk"
        assert r.provenance == PROVENANCE_IMPORTED
        assert len(r) == 29

    def test_load_reference_nonexistent(self):
        assert load_reference("fake-algorithm", "CEC2017", 10) is None

    def test_load_comparison_set(self):
        results = load_comparison_set("CEC2017", 10, ["gsk", "egsk", "fake-alg"])
        assert "gsk" in results
        assert "egsk" in results
        assert "fake-alg" not in results

    def test_discover_references(self):
        algs = discover_reference_algorithms("CEC2017")
        for expected in ("gsk", "egsk", "atmals-gsk", "agsk", "apgsk", "fdb-agsk"):
            assert expected in algs

    def test_mean_errors_excludes_f2(self):
        r = load_reference("gsk", "CEC2017", 10)
        if r is None:
            pytest.skip("No GSK data")
        means = r.mean_errors(excluded={2})
        assert 2 not in means and 1 in means
        assert len(means) == 29


class TestComparisonSets:
    def test_gsk_family_size(self):
        # gsk + agsk + apgsk + fdb-agsk + egsk + atmals-gsk
        assert len(GSK_FAMILY) == 6
        assert "atmals-gsk" in GSK_FAMILY

    def test_suite_dims(self):
        assert SUITE_DIMS["CEC2017"] == [10, 30, 50, 100]
        assert SUITE_DIMS["CEC2011"] == [0]

    def test_excluded_funcs(self):
        assert 2 in SUITE_EXCLUDED_FUNCS["CEC2017"]
        assert len(SUITE_EXCLUDED_FUNCS["CEC2011"]) == 0


class TestCommonFuncIds:
    def test_two_algorithms(self):
        results = load_comparison_set("CEC2017", 10, ["gsk", "egsk"])
        if len(results) < 2:
            pytest.skip("Need at least 2 algorithms")
        common = common_func_ids(results, excluded={2})
        assert 2 not in common and 1 in common
        assert len(common) >= 28

    def test_empty(self):
        assert common_func_ids({}) == []


class TestProvenanceReport:
    def test_report_format(self):
        results = load_comparison_set("CEC2017", 10, ["gsk", "egsk"])
        if not results:
            pytest.skip("No data available")
        report = provenance_report(results)
        assert "Algorithm" in report
        assert "imported_reference" in report


def _write_tiny_summary(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "Function,Best,Median,Mean,Worst,SD\n1,0.0,0.0,0.0,0.0,0.0\n",
        encoding="utf-8",
    )


class TestReproducedPathResolution:
    """Retargeted to the ``results/_run_all/<alg>/<suite>/summary/`` layout."""

    def test_run_all_suite_partitioned_layout_resolved(self, tmp_path):
        nested = tmp_path / "gsk" / "cec2017" / "summary" / "gsk_cec2017_D50.csv"
        _write_tiny_summary(nested)
        assert _reproduced_csv_path("gsk", "CEC2017", 50, tmp_path) == nested

    def test_dt_gsk_uses_same_flat_per_optimizer_layout(self, tmp_path):
        nested = tmp_path / "dt-gsk" / "cec2017" / "summary" / "dt-gsk_cec2017_D30.csv"
        _write_tiny_summary(nested)
        assert _reproduced_csv_path("dt-gsk", "CEC2017", 30, tmp_path) == nested

    def test_cec2011_uppercase_combined_summary_resolved(self, tmp_path):
        combined = tmp_path / "dt-gsk" / "cec2011" / "summary" / "dt-gsk_CEC2011.csv"
        _write_tiny_summary(combined)
        assert _reproduced_csv_path("dt-gsk", "CEC2011", 0, tmp_path) == combined

    def test_legacy_flat_fallback(self, tmp_path):
        flat = tmp_path / "gsk" / "summary" / "gsk_cec2017_D10.csv"
        _write_tiny_summary(flat)
        assert _reproduced_csv_path("gsk", "CEC2017", 10, tmp_path) == flat

    def test_missing_returns_none(self, tmp_path):
        assert _reproduced_csv_path("gsk", "CEC2017", 10, tmp_path) is None
