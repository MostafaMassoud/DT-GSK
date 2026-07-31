"""Regression tests for gsk_family.analysis.statistical_tests.friedman_rank_test.

Ported from the source project; verifies the degenerate-input path (all-constant
columns -> p=NaN + RuntimeWarning), healthy ranking, and the small-N skip.
"""

from __future__ import annotations

import math
import warnings

import pytest

from gsk_family.analysis.statistical_tests import friedman_rank_test


class TestFriedmanDegenerate:
    def test_all_constant_returns_nan_and_emits_warning(self):
        alg_means = {
            "A": {i: 1.0 for i in range(1, 15)},
            "B": {i: 1.0 for i in range(1, 15)},
            "C": {i: 1.0 for i in range(1, 15)},
        }
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            result = friedman_rank_test(alg_means)

        assert math.isnan(result.p_value), "degenerate input must yield NaN"
        rt_warnings = [w for w in caught if issubclass(w.category, RuntimeWarning)]
        assert rt_warnings, "expected a RuntimeWarning surface for NaN fallback"
        assert "friedmanchisquare" in str(rt_warnings[0].message)

    def test_clear_ranking_still_significant(self):
        alg_means = {
            "A": {i: float(i) for i in range(1, 15)},
            "B": {i: float(i) + 5.0 for i in range(1, 15)},
            "C": {i: float(i) + 10.0 for i in range(1, 15)},
        }
        result = friedman_rank_test(alg_means)
        assert not math.isnan(result.p_value)
        assert result.p_value < 0.05
        names_sorted = [name for name, _ in result.overall_order]
        assert names_sorted == ["A", "B", "C"]


class TestFriedmanSmallN:
    def test_fewer_than_three_functions_keeps_default_pvalue(self):
        alg_means = {
            "A": {1: 1.0, 2: 2.0},
            "B": {1: 1.5, 2: 2.5},
            "C": {1: 1.2, 2: 2.2},
        }
        result = friedman_rank_test(alg_means)
        assert result.p_value == pytest.approx(1.0)
