"""Tests for run_statistical_analysis extra_comparators (reference-self validation).

When ``--stats`` runs an optimizer that has committed reference results (e.g. the
reference DT-GSK under ``benchmarks/cec_reference_results/<suite>/dt-gsk/``),
those results are folded into the panel as a ``<OPT>-REF`` comparator so the
current run is validated directly against the reference implementation while the
GSK-family comparisons are retained.
"""

from pathlib import Path

import pytest

from gsk_family.analysis.statistical_tests import HAS_SCIPY, run_statistical_analysis

_BENCH = Path(__file__).resolve().parents[2] / "benchmarks" / "cec_reference_results" / "cec2017"
_DT_REF = _BENCH / "dt-gsk" / "dt-gsk_cec2017_D10.csv"

_BENCH_2011 = Path(__file__).resolve().parents[2] / "benchmarks" / "cec_reference_results" / "cec2011"
# The committed CEC2011 DT-GSK rollup uses an uppercase suite in its filename
# (dt-gsk_CEC2011.csv) -- resolve case-insensitively so the test is robust on
# case-sensitive filesystems.
_DT_REF_2011 = next(
    iter(sorted(_BENCH_2011.glob("dt-gsk/dt-gsk_[cC][eE][cC]2011.csv"))),
    _BENCH_2011 / "dt-gsk" / "dt-gsk_cec2011.csv",
)


@pytest.mark.skipif(not HAS_SCIPY, reason="scipy required")
@pytest.mark.skipif(not _DT_REF.exists(), reason="reference DT-GSK data not present")
class TestExtraComparators:
    def test_reference_self_folded_into_both_panels(self):
        # Use the reference DT-GSK as the "current run" AND the extra comparator:
        # identical data must validate to zero difference (all ties).
        res = run_statistical_analysis(
            _DT_REF, _BENCH, "cec2017", 10, "dt-gsk",
            extra_comparators={"DT-GSK-REF": _DT_REF},
        )
        assert "DT-GSK-REF" in res.wilcoxon_results
        assert res.friedman_gsk_family is not None
        assert "DT-GSK-REF" in res.friedman_gsk_family.mean_ranks
        # GSK-family comparisons are retained alongside the validation comparator.
        assert "GSK" in res.wilcoxon_results

        w = res.wilcoxon_results["DT-GSK-REF"]
        assert w.wins == 0 and w.losses == 0  # identical -> no wins/losses
        assert w.decision == "="

    def test_absent_without_extra(self):
        res = run_statistical_analysis(_DT_REF, _BENCH, "cec2017", 10, "dt-gsk")
        assert "DT-GSK-REF" not in res.wilcoxon_results
        # the GSK-family panel still builds
        assert res.friedman_gsk_family is not None

    def test_missing_extra_csv_skipped(self):
        res = run_statistical_analysis(
            _DT_REF, _BENCH, "cec2017", 10, "dt-gsk",
            extra_comparators={"DT-GSK-REF": _BENCH / "dt-gsk" / "does_not_exist.csv"},
        )
        assert "DT-GSK-REF" not in res.wilcoxon_results


@pytest.mark.skipif(not HAS_SCIPY, reason="scipy required")
@pytest.mark.skipif(not _DT_REF_2011.exists(), reason="reference CEC2011 data not present")
class TestCec2011Comparators:
    """CEC2011 uses native per-problem dims, so comparators are single rollups
    (``<alg>_cec2011.csv``, 22 problems) rather than per-dimension CSVs. The
    panel must still discover the 6 GSK-family comparators, fold in the
    reference-self DT-GSK-REF validator, and never exclude F2.
    """

    def test_native_rollup_panels_and_self_ties(self):
        # Use the reference DT-GSK rollup as both the "current run" and the
        # extra comparator: identical data must validate to all ties, and the
        # six GSK-family comparators must load from their cec2011 rollups.
        res = run_statistical_analysis(
            _DT_REF_2011, _BENCH_2011, "cec2011", 0, "dt-gsk",
            excluded_funcs=(),
            extra_comparators={"DT-GSK-REF": _DT_REF_2011},
        )
        # All six GSK-family comparators discovered from <alg>_cec2011.csv.
        for ref in ("GSK", "AGSK", "APGSK", "FDB-AGSK", "EGSK", "ATMALS-GSK"):
            assert ref in res.wilcoxon_results, ref
        # Reference-self validator folded into both panels.
        assert "DT-GSK-REF" in res.wilcoxon_results
        assert res.friedman_gsk_family is not None
        assert "DT-GSK-REF" in res.friedman_gsk_family.mean_ranks
        # F2 (Lennard-Jones) is a legitimate problem -- all 22 compared.
        assert len(res.friedman_gsk_family.func_ids) == 22

        w = res.wilcoxon_results["DT-GSK-REF"]
        assert w.wins == 0 and w.losses == 0  # identical -> no wins/losses
        assert w.ties == 22
        assert w.decision == "="
