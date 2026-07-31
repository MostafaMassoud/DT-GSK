"""Unit tests for gsk_family.analysis.statistics (vendored from the source project).

Validates the family-wide statistical functions (Wilcoxon, Friedman, Holm,
Vargha-Delaney A12, win/tie/loss) against hand-computed examples. Ported
verbatim from the source's tests/test_statistics.py with the import rewired to
the target's analysis package.
"""

import numpy as np
import pytest

from gsk_family.analysis.statistics import (
    friedman_rank,
    holm_correction,
    vargha_delaney,
    wilcoxon_paired,
    win_tie_loss,
)


class TestWilcoxonPaired:
    def test_identical(self):
        x = np.array([1.0, 2.0, 3.0])
        r = wilcoxon_paired(x, x)
        assert r.p_value == 1.0
        assert r.n_pairs == 0

    def test_clear_difference(self):
        x = np.array([1.0, 2.0, 3.0, 4.0, 5.0, 6.0])
        y = np.array([10.0, 20.0, 30.0, 40.0, 50.0, 60.0])
        r = wilcoxon_paired(x, y)
        assert r.p_value < 0.05
        assert r.n_pairs == 6

    def test_literature_review_example(self):
        err_a = np.array([11.0, 12.0, 13.0, 14.0, 15.0, 16.0])
        err_b = np.array([10.0, 10.0, 10.0, 10.0, 10.0, 10.0])
        r = wilcoxon_paired(err_a, err_b)
        assert r.n_pairs == 6
        assert r.p_value < 0.10

    def test_symmetric_no_difference(self):
        x = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        y = np.array([2.0, 1.0, 4.0, 3.0, 5.5])
        r = wilcoxon_paired(x, y)
        assert r.p_value > 0.2


class TestHolmCorrection:
    def test_single(self):
        r = holm_correction([0.03], ["A vs B"])
        assert len(r.comparisons) == 1
        assert r.comparisons[0]["p_adjusted"] == pytest.approx(0.03)
        assert r.comparisons[0]["significant"] is True

    def test_multiple(self):
        r = holm_correction([0.01, 0.04, 0.03], ["A", "B", "C"])
        for c in r.comparisons:
            if c["label"] == "A":
                assert c["p_adjusted"] == pytest.approx(0.03)
                assert c["significant"] is True
            elif c["label"] == "C":
                assert c["p_adjusted"] == pytest.approx(0.06)
                assert c["significant"] is False
            elif c["label"] == "B":
                assert c["p_adjusted"] == pytest.approx(0.06)
                assert c["significant"] is False

    def test_all_significant(self):
        r = holm_correction([0.001, 0.002], ["A", "B"])
        assert all(c["significant"] for c in r.comparisons)


class TestFriedmanRank:
    def test_identical_algorithms(self):
        data = {"A": [1.0, 2.0, 3.0], "B": [1.0, 2.0, 3.0], "C": [1.0, 2.0, 3.0]}
        r = friedman_rank(data)
        assert r.p_value > 0.9
        for _name, rank in r.avg_ranks.items():
            assert rank == pytest.approx(2.0)

    def test_clear_ranking(self):
        data = {
            "A": [1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
            "B": [5.0, 5.0, 5.0, 5.0, 5.0, 5.0],
            "C": [10.0, 10.0, 10.0, 10.0, 10.0, 10.0],
        }
        r = friedman_rank(data)
        assert r.p_value < 0.05
        assert r.avg_ranks["A"] < r.avg_ranks["B"] < r.avg_ranks["C"]
        assert r.avg_ranks["A"] == 1.0
        assert r.avg_ranks["C"] == 3.0

    def test_returns_correct_counts(self):
        data = {"X": [1.0, 2.0, 3.0], "Y": [2.0, 1.0, 4.0]}
        r = friedman_rank(data)
        assert r.n_problems == 3
        assert r.n_algorithms == 2


class TestVarghaDelaney:
    def test_identical(self):
        r = vargha_delaney([1.0, 2.0, 3.0], [1.0, 2.0, 3.0])
        assert r.a12 == pytest.approx(0.5)
        assert r.magnitude == "negligible"

    def test_x_always_better(self):
        r = vargha_delaney([1.0, 2.0, 3.0], [10.0, 20.0, 30.0])
        assert r.a12 == pytest.approx(1.0)
        assert r.magnitude == "large"

    def test_x_always_worse(self):
        r = vargha_delaney([10.0, 20.0, 30.0], [1.0, 2.0, 3.0])
        assert r.a12 == pytest.approx(0.0)
        assert r.magnitude == "large"

    def test_empty_input_raises(self):
        with pytest.raises(ValueError, match="non-empty"):
            vargha_delaney([], [1.0, 2.0])
        with pytest.raises(ValueError, match="non-empty"):
            vargha_delaney([1.0], [])


class TestWinTieLoss:
    def test_all_wins(self):
        a = {1: 1.0, 2: 2.0, 3: 3.0}
        b = {1: 10.0, 2: 20.0, 3: 30.0}
        r = win_tie_loss(a, b)
        assert r.wins == 3 and r.ties == 0 and r.losses == 0

    def test_mixed(self):
        a = {1: 1.0, 2: 20.0, 3: 3.0}
        b = {1: 10.0, 2: 2.0, 3: 3.0}
        r = win_tie_loss(a, b)
        assert r.wins == 1 and r.ties == 1 and r.losses == 1

    def test_tolerance(self):
        a = {1: 1e-10, 2: 5e-9}
        b = {1: 2e-10, 2: 3e-9}
        r = win_tie_loss(a, b, tol=1e-8)
        assert r.ties == 2
