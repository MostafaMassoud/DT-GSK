"""Unit tests for gsk_family.analysis.figures.

Covers the Nemenyi critical-difference formula, the proposed-algorithm
highlight predicate, and that both renderers write a non-empty figure file.
"""

from __future__ import annotations

import math

import pytest

from gsk_family.analysis.figures import (
    Q_ALPHA_005_TABLE,
    is_proposed,
    nemenyi_critical_difference,
    render_cd_diagram,
    render_rank_chart,
)

_RANKS = {
    "dt-gsk": 2.07,
    "AGSK": 3.02,
    "GSK": 5.45,
    "EGSK": 4.24,
    "APGSK": 3.53,
    "FDB-AGSK": 3.41,
    "ATMALS-GSK": 5.21,
}


class TestNemenyiCD:
    def test_known_value_k7_n29(self):
        cd = nemenyi_critical_difference(7, 29)
        expected = Q_ALPHA_005_TABLE[7] * math.sqrt(7 * 8 / (6 * 29))
        assert cd == pytest.approx(expected)
        assert cd == pytest.approx(1.6730, abs=1e-3)

    def test_explicit_q_alpha_overrides_table(self):
        cd = nemenyi_critical_difference(7, 29, q_alpha=3.0)
        assert cd == pytest.approx(3.0 * math.sqrt(7 * 8 / (6 * 29)))

    def test_too_few_algorithms_raises(self):
        with pytest.raises(ValueError, match="at least 2"):
            nemenyi_critical_difference(1, 29)

    def test_unknown_k_raises(self):
        with pytest.raises(ValueError, match="No tabulated"):
            nemenyi_critical_difference(99, 29)


class TestIsProposed:
    def test_hyphen_and_case_insensitive(self):
        assert is_proposed("DT-GSK", "dt-gsk")
        assert is_proposed("dt_gsk", "dt-gsk")
        assert is_proposed("DTGSK", "dt-gsk")

    def test_rejects_comparators(self):
        assert not is_proposed("GSK", "dt-gsk")
        assert not is_proposed("AGSK", "dt-gsk")


class TestRenderers:
    def test_cd_diagram_writes_file(self, tmp_path):
        out = tmp_path / "cd.png"
        cd = render_cd_diagram(_RANKS, n_funcs=29, out_path=out, suite="CEC2017", dim=10)
        assert out.is_file()
        assert out.stat().st_size > 0
        assert cd == pytest.approx(nemenyi_critical_difference(7, 29))

    def test_rank_chart_writes_file(self, tmp_path):
        out = tmp_path / "ranks.png"
        render_rank_chart(_RANKS, out_path=out, title="Test")
        assert out.is_file()
        assert out.stat().st_size > 0
