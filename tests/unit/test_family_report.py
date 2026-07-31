"""Unit tests for gsk_family.analysis.family_report.

Builds a tiny synthetic results/reference tree in a tmp dir and verifies the
orchestrator computes the Friedman panel + Holm-corrected Wilcoxon rows and
writes the expected text/CSV/LaTeX artifacts.
"""

from __future__ import annotations

import csv
from pathlib import Path

from gsk_family.analysis.family_report import analyze_family, write_report

# Five functions (CEC2017 F2 excluded); dt-gsk is uniformly best, GSK middle,
# AGSK worst — so Friedman ranks are 1 / 2 / 3 respectively.
_FUNCS = [1, 3, 4, 5, 6]
_MEANS = {
    "dt-gsk": {f: 1.0 for f in _FUNCS},
    "gsk": {f: 2.0 for f in _FUNCS},
    "agsk": {f: 3.0 for f in _FUNCS},
}


def _write_summary(path: Path, means: dict[int, float]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["Function", "Best", "Median", "Mean", "Worst", "SD"])
        for func, mean in means.items():
            writer.writerow([func, mean, mean, mean, mean, 0.0])


def _build_tree(tmp_path: Path) -> tuple[Path, Path]:
    results_root = tmp_path / "results" / "_run_all"
    reference_root = tmp_path / "benchmarks" / "cec_reference_results"
    _write_summary(
        results_root / "dt-gsk" / "cec2017" / "summary" / "dt-gsk_cec2017_D10.csv",
        _MEANS["dt-gsk"],
    )
    for alg in ("gsk", "agsk"):
        _write_summary(
            reference_root / "cec2017" / alg / f"{alg}_cec2017_D10.csv",
            _MEANS[alg],
        )
    return results_root, reference_root


class TestAnalyzeFamily:
    def test_builds_panel_and_rows(self, tmp_path):
        results_root, reference_root = _build_tree(tmp_path)
        results = analyze_family(
            "CEC2017", [10],
            results_root=results_root, reference_root=reference_root,
        )
        assert len(results) == 1
        dim_result = results[0]
        assert dim_result.dim == 10
        assert dim_result.n_funcs == 5
        assert dim_result.mean_ranks is not None
        ranks = dim_result.mean_ranks
        assert set(ranks) == {"dt-gsk", "GSK", "AGSK"}
        # dt-gsk uniformly best -> mean rank 1.0, strictly below comparators.
        assert ranks["dt-gsk"] == min(ranks.values())
        assert ranks["dt-gsk"] < ranks["GSK"] < ranks["AGSK"]
        # Two comparators -> two Wilcoxon rows with finite A12.
        comparators = {row.comparator for row in dim_result.wilcoxon_rows}
        assert comparators == {"GSK", "AGSK"}
        for row in dim_result.wilcoxon_rows:
            assert 0.0 <= row.a12 <= 1.0

    def test_missing_dimension_skipped(self, tmp_path):
        results_root, reference_root = _build_tree(tmp_path)
        results = analyze_family(
            "CEC2017", [10, 30],  # only D10 exists on disk
            results_root=results_root, reference_root=reference_root,
        )
        assert [r.dim for r in results] == [10]


class TestWriteReport:
    def test_writes_text_csv_latex(self, tmp_path):
        results_root, reference_root = _build_tree(tmp_path)
        results = analyze_family(
            "CEC2017", [10],
            results_root=results_root, reference_root=reference_root,
        )
        out_dir = tmp_path / "out"
        written = write_report(results, out_dir, "CEC2017", make_figures=False)

        names = {p.name for p in written}
        assert "cec2017_statistical_report.txt" in names
        assert "cec2017_friedman_ranks.csv" in names
        assert "cec2017_friedman_ranks.tex" in names
        assert "cec2017_wilcoxon_summary.tex" in names
        for path in written:
            assert path.is_file() and path.stat().st_size > 0

        csv_text = (out_dir / "cec2017_friedman_ranks.csv").read_text(encoding="utf-8")
        assert "Overall_MeanRank" in csv_text
        # dt-gsk is best -> first data row.
        rows = [ln for ln in csv_text.splitlines() if ln and not ln.startswith("Algorithm")]
        assert rows[0].startswith("dt-gsk")

    def test_figures_written_when_enabled(self, tmp_path):
        results_root, reference_root = _build_tree(tmp_path)
        results = analyze_family(
            "CEC2017", [10],
            results_root=results_root, reference_root=reference_root,
        )
        out_dir = tmp_path / "out"
        written = write_report(results, out_dir, "CEC2017", make_figures=True)
        pngs = [p for p in written if p.suffix == ".png"]
        assert len(pngs) == 2
        for png in pngs:
            assert png.is_file() and png.stat().st_size > 0
