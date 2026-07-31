"""Statistics helpers for result summaries."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation

import numpy as np


@dataclass(frozen=True)
class SummaryStatistics:
    """CEC-style summary statistics over repeated runs."""

    best: float
    median: float
    mean: float
    worst: float
    sd: float


def sample_sd(values: np.ndarray) -> float:
    """Return sample standard deviation for result summaries."""
    arr = np.asarray(values, dtype=float).reshape(-1)
    if arr.size < 2:
        return 0.0
    return float(np.std(arr, ddof=1))


def summarize(values: np.ndarray) -> SummaryStatistics:
    """Return best, median, mean, worst, and sample SD."""
    arr = np.asarray(values, dtype=float).reshape(-1)
    if arr.size == 0:
        raise ValueError("Cannot summarize an empty value vector.")
    if not np.all(np.isfinite(arr)):
        raise ValueError("Cannot summarize non-finite values.")
    return SummaryStatistics(
        best=float(np.min(arr)),
        median=float(np.median(arr)),
        mean=float(np.mean(arr)),
        worst=float(np.max(arr)),
        sd=sample_sd(arr),
    )


def compute_error(
    best_fitness: float,
    optimum: float,
    target_error: float,
    *,
    absolute: bool = False,
) -> float:
    """Compute target-zeroed error against a known optimum."""
    if np.isnan(optimum):
        return float("nan")
    try:
        err_decimal = Decimal(str(best_fitness)) - Decimal(str(optimum))
    except InvalidOperation:
        err = float(best_fitness) - float(optimum)
    else:
        err = float(err_decimal)
    if absolute:
        err = abs(err)
    if not np.isnan(target_error) and err < float(target_error):
        return 0.0
    return err


def statistic_values(
    best_fitness: np.ndarray,
    *,
    optimum: float,
    target_error: float,
    statistics_basis: str,
    absolute_error: bool = False,
) -> np.ndarray:
    """Return values to summarize for raw-objective or error-based suites."""
    values = np.asarray(best_fitness, dtype=float).reshape(-1)
    if statistics_basis == "raw_objective":
        return values.copy()
    if statistics_basis != "error_vs_optimum":
        raise ValueError(f"Unknown statistics basis {statistics_basis!r}.")
    return np.array(
        [
            compute_error(v, optimum, target_error, absolute=absolute_error)
            for v in values
        ],
        dtype=float,
    )


def format_scientific(value: float, precision: int = 10) -> str:
    """Format a float for summary CSV output."""
    if np.isnan(value):
        return "NaN"
    if np.isposinf(value):
        return "Inf"
    if np.isneginf(value):
        return "-Inf"
    return f"{float(value):.{precision}E}"
