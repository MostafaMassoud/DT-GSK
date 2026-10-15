"""Per-suite function exclusions and default dimensions of the gsk-stats panel.

Only CEC2017 drops F2 (the benchmark maintainers withdrew it). Every other
suite keeps it: Amendment 1 Section A1.1 names the CEC2017 rule leaking into
another suite as a hazard. Synthetic trees only; the real-data pins against
the paper's frozen CEC2020 bundle live in
``tests/regression/test_gsk_stats_paper_panels.py``.
"""

from __future__ import annotations

import csv
import inspect
from pathlib import Path

from gsk_family.analysis.family_report import DEFAULT_EXCLUDED_FUNCS, analyze_family
from gsk_family.analysis.result_loader import SUITE_DIMS, SUITE_EXCLUDED_FUNCS
from gsk_family.analysis.statistical_tests import friedman_rank_test
from gsk_family.cli.stats import _parse_dims
from gsk_family.cli.stats import main as stats_main

# dt-gsk best, GSK middle, AGSK worst on every function.
_SCALE = {"dt-gsk": 1.0, "gsk": 2.0, "agsk": 3.0}


def _write(path: Path, means: dict[int, float]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["Function", "Best", "Median", "Mean", "Worst", "SD"])
        for func, mean in means.items():
            writer.writerow([func, mean, mean, mean, mean, 0.0])


def _ref_tree(root: Path, suite: str, dim: int, funcs: list[int]) -> Path:
    ref = root / "ref"
    for alg, scale in _SCALE.items():
        _write(ref / suite / alg / f"{alg}_{suite}_D{dim}.csv", {f: scale for f in funcs})
    return ref


class TestRegistries:
    def test_only_cec2017_excludes_f2(self):
        assert [s for s, ex in SUITE_EXCLUDED_FUNCS.items() if 2 in ex] == ["CEC2017"]

    def test_every_suite_with_dims_has_an_exclusion_entry(self):
        assert set(SUITE_DIMS) <= set(SUITE_EXCLUDED_FUNCS)

    def test_family_report_fallback_excludes_nothing(self):
        assert DEFAULT_EXCLUDED_FUNCS == ()

    def test_vendored_friedman_default_is_untouched(self):
        # papers/scripts/phase6b_run_analysis_newsuites.py reads this default
        # (Amendment 1 A1.1) and the frozen environment records cite it; the
        # fix lives in result_loader/family_report, never here.
        default = inspect.signature(friedman_rank_test).parameters["excluded"].default
        assert tuple(default) == (2,)

    def test_cli_default_dims(self):
        assert _parse_dims(None, "cec2020") == [5, 10, 15, 20]
        assert _parse_dims(None, "CEC2013LSGO") == [1000]
        assert _parse_dims("905", "cec2013lsgo") == [905]


class TestFamilyReportExclusions:
    def test_cec2020_keeps_f2(self, tmp_path):
        ref = _ref_tree(tmp_path, "cec2020", 10, [1, 2, 3, 4, 5])
        [r] = analyze_family("CEC2020", [10], reference_root=ref, results_root=tmp_path / "none")
        assert r.n_funcs == 5
        assert 2 in r.stat_result.friedman_gsk_family.func_ids

    def test_cec2013lsgo_keeps_f2_lowercase(self, tmp_path):
        ref = _ref_tree(tmp_path, "cec2013lsgo", 1000, [1, 2, 3])
        [r] = analyze_family("cec2013lsgo", [1000], reference_root=ref, results_root=tmp_path / "none")
        assert r.n_funcs == 3

    def test_cec2017_still_drops_f2(self, tmp_path):
        ref = _ref_tree(tmp_path, "cec2017", 10, [1, 2, 3, 4, 5])
        [r] = analyze_family("CEC2017", [10], reference_root=ref, results_root=tmp_path / "none")
        assert r.n_funcs == 4
        assert 2 not in r.stat_result.friedman_gsk_family.func_ids

    def test_unregistered_suite_drops_nothing(self, tmp_path):
        ref = _ref_tree(tmp_path, "cec2099", 10, [1, 2, 3])
        [r] = analyze_family("CEC2099", [10], reference_root=ref, results_root=tmp_path / "none")
        assert r.n_funcs == 3

    def test_explicit_excluded_funcs_still_wins(self, tmp_path):
        ref = _ref_tree(tmp_path, "cec2020", 10, [1, 2, 3, 4, 5])
        [r] = analyze_family(
            "CEC2020", [10], reference_root=ref, results_root=tmp_path / "none", excluded_funcs=(2,)
        )
        assert r.n_funcs == 4

    def test_under_three_functions_has_no_ranking(self, tmp_path):
        # friedman_rank_test returns positional placeholder ranks below N=3;
        # they must not be reported as a ranking (CEC2013LSGO D=905 has N=2).
        ref = _ref_tree(tmp_path, "cec2013lsgo", 905, [13, 14])
        [r] = analyze_family("CEC2013LSGO", [905], reference_root=ref, results_root=tmp_path / "none")
        assert r.mean_ranks is None
        assert r.n_funcs == 0
        # The text report must not carry the placeholder ranking either.
        text = r.stat_result.text
        assert r.stat_result.friedman_gsk_family is None
        assert "GSK-family Friedman ranking" not in text
        assert "Mean Rank" not in text
        assert "nearest peer" not in text
        assert "ahead of" not in text and "behind" not in text
        assert text.rstrip().endswith(
            "Friedman ranking omitted at D=905: only 2 common functions (at least 3 are needed)."
        )
        # The per-comparator Wilcoxon blocks do not use the ranking and stay.
        assert "Wilcoxon Signed-Rank Test: dt-gsk vs GSK (D=905)" in text
        assert "Per-function detail:" in text

    def test_one_common_function_report_file(self, tmp_path):
        ref = _ref_tree(tmp_path, "cec2017", 10, [1])
        out = tmp_path / "out"
        code = stats_main(["--suite", "cec2017", "--dims", "10", "--reference-root", str(ref),
                           "--results-root", str(tmp_path / "none"), "--out", str(out), "--no-figures"])
        assert code == 0
        report = (out / "cec2017_statistical_report.txt").read_text(encoding="utf-8")
        assert "Mean Rank" not in report and "ahead of" not in report
        assert "Friedman ranking omitted at D=10: only 1 common function (at least 3 are needed)." in report
        assert not (out / "cec2017_friedman_ranks.csv").exists()


def test_cli_names_ties_and_suppressed_panels(tmp_path, capsys):
    ref = tmp_path / "ref"
    for alg, s in {"dt-gsk": 1.0, "gsk": 1.0, "agsk": 3.0}.items():
        _write(ref / "cec2017" / alg / f"{alg}_cec2017_D10.csv", {f: s for f in [1, 3, 4]})
        _write(ref / "cec2017" / alg / f"{alg}_cec2017_D30.csv", {f: s for f in [1, 3]})
    assert stats_main(["--suite", "cec2017", "--dims", "10,30", "--reference-root", str(ref),
                       "--results-root", str(tmp_path / "none"), "--out", str(tmp_path / "out"),
                       "--no-figures"]) == 0
    out = capsys.readouterr().out
    assert "tied for best with dt-gsk: GSK" in out
    assert "D30: Friedman panel unavailable" in out


def test_cli_lists_suites_for_a_misspelled_suite(tmp_path, capsys):
    ref = _ref_tree(tmp_path, "cec2017", 10, [1, 3, 4])
    assert stats_main(["--suite", "cec2071", "--reference-root", str(ref), "--no-figures",
                       "--out", str(tmp_path / "out")]) == 1
    printed = capsys.readouterr().out
    assert "reference directory not found" in printed
    assert "suites found under" in printed and "cec2017" in printed


def _ranks(out: Path) -> dict[str, float]:
    with (out / "cec2017_friedman_ranks.csv").open(newline="", encoding="utf-8") as handle:
        return {row["Algorithm"]: float(row["MeanRank_D10"]) for row in csv.DictReader(handle)}


class TestDataSourcePrecedence:
    """Pins what cli/stats.py's docstring and the runbook say gsk-stats reads."""

    def test_reference_is_read_before_results(self, tmp_path):
        ref, res, funcs = tmp_path / "ref", tmp_path / "res", [1, 3, 4, 5, 6]
        _write(ref / "cec2017" / "gsk" / "gsk_cec2017_D10.csv", {f: 2.0 for f in funcs})
        _write(ref / "cec2017" / "agsk" / "agsk_cec2017_D10.csv", {f: 3.0 for f in funcs})
        _write(ref / "cec2017" / "dt-gsk" / "dt-gsk_cec2017_D10.csv", {f: 9.0 for f in funcs})
        _write(res / "dt-gsk" / "cec2017" / "summary" / "dt-gsk_cec2017_D10.csv", {f: 1.0 for f in funcs})
        _write(res / "apgsk" / "cec2017" / "summary" / "apgsk_cec2017_D10.csv", {f: 0.5 for f in funcs})
        out = tmp_path / "out"
        code = stats_main(["--suite", "CEC2017", "--dims", "10", "--results-root", str(res),
                           "--reference-root", str(ref), "--out", str(out), "--no-figures"])
        assert code == 0
        ranks = _ranks(out)
        assert ranks["dt-gsk"] == 3.0  # the committed panel's dt-gsk, not the local run
        assert "APGSK" not in ranks  # comparators never come from --results-root

    def test_results_are_a_fallback_for_a_missing_proposed_cell(self, tmp_path):
        ref, res, funcs = tmp_path / "ref", tmp_path / "res", [1, 3, 4, 5, 6]
        _write(ref / "cec2017" / "gsk" / "gsk_cec2017_D10.csv", {f: 2.0 for f in funcs})
        _write(ref / "cec2017" / "agsk" / "agsk_cec2017_D10.csv", {f: 3.0 for f in funcs})
        _write(res / "dt-gsk" / "cec2017" / "summary" / "dt-gsk_cec2017_D10.csv", {f: 1.0 for f in funcs})
        out = tmp_path / "out"
        code = stats_main(["--suite", "CEC2017", "--dims", "10", "--results-root", str(res),
                           "--reference-root", str(ref), "--out", str(out), "--no-figures"])
        assert code == 0
        assert _ranks(out)["dt-gsk"] == 1.0
