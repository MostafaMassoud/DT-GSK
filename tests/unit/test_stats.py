from __future__ import annotations

import math

import numpy as np
import pytest

from gsk_family.stats import (
    compute_error,
    format_scientific,
    sample_sd,
    statistic_values,
    summarize,
)


def test_sample_sd_uses_ddof_one_and_singleton_zero() -> None:
    assert sample_sd(np.array([1.0])) == 0.0
    assert sample_sd(np.array([1.0, 2.0, 3.0])) == pytest.approx(1.0)


def test_summarize_returns_cec_ordered_statistics() -> None:
    summary = summarize(np.array([3.0, 1.0, 2.0]))

    assert summary.best == 1.0
    assert summary.median == 2.0
    assert summary.mean == 2.0
    assert summary.worst == 3.0
    assert summary.sd == pytest.approx(1.0)


def test_summarize_rejects_empty_and_nonfinite() -> None:
    with pytest.raises(ValueError, match="empty"):
        summarize(np.array([]))
    with pytest.raises(ValueError, match="non-finite"):
        summarize(np.array([1.0, np.nan]))


def test_compute_error_target_zeroing_is_strict_less_than_target() -> None:
    assert compute_error(100.0 + 1e-9, 100.0, 1e-8) == 0.0
    assert compute_error(100.0 + 1e-8, 100.0, 1e-8) == pytest.approx(1e-8)
    assert compute_error(99.0, 100.0, 1e-8) == 0.0
    assert compute_error(99.0, 100.0, 1e-8, absolute=True) == 1.0
    assert math.isnan(compute_error(1.0, float("nan"), 1e-8))


def test_statistic_values_support_raw_and_error_basis() -> None:
    raw = statistic_values(np.array([10.0, 20.0]), optimum=float("nan"), target_error=float("nan"), statistics_basis="raw_objective")
    err = statistic_values(np.array([101.0, 102.0]), optimum=100.0, target_error=1e-8, statistics_basis="error_vs_optimum")

    np.testing.assert_allclose(raw, np.array([10.0, 20.0]))
    np.testing.assert_allclose(err, np.array([1.0, 2.0]))

    with pytest.raises(ValueError, match="Unknown"):
        statistic_values(np.array([1.0]), optimum=0.0, target_error=1e-8, statistics_basis="bad")


def test_format_scientific_handles_special_values() -> None:
    assert format_scientific(1.23, precision=2) == "1.23E+00"
    assert format_scientific(float("nan")) == "NaN"
    assert format_scientific(float("inf")) == "Inf"
    assert format_scientific(float("-inf")) == "-Inf"

