"""ATMALS-GSK local helper functions."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np

from gsk_family.common.numeric_compat import compat_round_int
from gsk_family.common.rng import RandomContext


def atmals_gaussmf(x: Any, sigma: float, center: float) -> np.ndarray:
    """Evaluate the Gaussian membership function used by ATMALS-GSK."""
    values = np.asarray(x, dtype=np.float64)
    sig = float(sigma)
    if sig == 0.0:
        raise ValueError("sigma must be non-zero.")
    return np.exp(-((values - float(center)) ** 2) / (2.0 * sig * sig))


def _atmals_reward_row(
    values: np.ndarray,
    value: float,
    mean_fit: float,
    mean_fit_new: float,
) -> np.ndarray:
    """Return the one-row ATMALS memory reward/penalty contribution."""
    vals = np.asarray(values, dtype=np.float64).reshape(-1)
    matches = np.where(np.abs(vals - float(value)) < np.finfo(float).eps)[0]
    if matches.size == 0:
        raise ValueError(f"value {value!r} is not present in the ATMALS pool.")
    center = float(matches[0] + 1)
    yy = atmals_gaussmf(vals, 0.05 * float(np.max(vals) - np.min(vals)), center)

    # Guard the reference denominator against an exactly-zero mean signal (a
    # fully-solved best half). For any non-zero mean_fit this is identical to the
    # reference abs(mean_fit), so reproduced results are unchanged.
    denom = max(abs(float(mean_fit)), float(np.finfo(float).eps))
    with np.errstate(divide="ignore", invalid="ignore", over="ignore"):
        if float(mean_fit_new) < float(mean_fit):
            reward_scale = np.exp(-(float(mean_fit_new) - float(mean_fit)) / denom)
            return np.multiply(yy, reward_scale, out=np.zeros_like(yy), where=yy > 0.0)
        if float(mean_fit_new) > float(mean_fit):
            return (1.0 - yy) * 0.1 * np.exp(
                -(float(mean_fit_new) - float(mean_fit)) / denom
            )
    return np.zeros_like(yy)


@dataclass
class AtmalsProbabilityMemory:
    """Compact ATMALS probability-memory state.

    The reference helper keeps every historical reward row and recomputes the
    weighted sum from scratch.  Because each old row keeps the same
    ``alpha**row_index`` weight forever, the optimizer only needs the current
    weighted sum and the next row index.
    """

    values: np.ndarray
    alpha: float
    weighted_sum: np.ndarray
    row_count: int

    @classmethod
    def create(cls, values: Any, alpha: float) -> "AtmalsProbabilityMemory":
        """Create a memory seeded with the reference all-ones first row."""
        vals = np.asarray(values, dtype=np.float64).reshape(-1).copy()
        if vals.size == 0:
            raise ValueError("ATMALS memory values must not be empty.")
        alpha_f = float(alpha)
        return cls(
            values=vals,
            alpha=alpha_f,
            weighted_sum=alpha_f * np.ones(vals.size, dtype=np.float64),
            row_count=1,
        )

    def update(self, value: float, mean_fit: float, mean_fit_new: float) -> np.ndarray:
        """Append one logical reward row and return the updated probabilities."""
        row = _atmals_reward_row(self.values, value, mean_fit, mean_fit_new)
        self.row_count += 1
        self.weighted_sum = self.weighted_sum + (self.alpha**self.row_count) * row
        return self.weighted_sum


def atmals_prob_update(
    p_old: Any,
    values: Any,
    value: float,
    mean_fit: float,
    mean_fit_new: float,
    alpha: float,
) -> tuple[np.ndarray, np.ndarray]:
    """Port of ATMALS ``ProbUpdate.m``."""
    history = np.asarray(p_old, dtype=np.float64)
    if history.ndim == 1:
        history = history.reshape(1, -1)
    vals = np.asarray(values, dtype=np.float64).reshape(-1)
    if history.shape[1] != vals.size:
        raise ValueError(
            f"p_old width must match values length {vals.size}, got {history.shape[1]}."
        )

    row = _atmals_reward_row(vals, value, mean_fit, mean_fit_new)

    updated = np.vstack([history, row])
    p_new = np.zeros(vals.size, dtype=np.float64)
    row_count = updated.shape[0]
    for i in range(1, row_count + 1):
        p_new = p_new + (float(alpha) ** (row_count - i + 1)) * updated[row_count - i, :]
    return p_new, updated


def atmals_roulette_select(probabilities: Any, rng: RandomContext) -> int:
    """Return a 0-based ATMALS roulette-selected pool index."""
    probs = np.asarray(probabilities, dtype=np.float64).reshape(-1)
    if probs.size == 0:
        raise ValueError("probabilities must not be empty.")
    total = float(np.sum(probs))
    if not np.isfinite(total) or total <= 0.0:
        raise ValueError("probabilities must have a positive finite sum.")
    normalized = probs / total
    threshold = float(rng.random())
    cumulative = np.cumsum(normalized)
    return min(int(np.searchsorted(cumulative, threshold, side="left")), probs.size - 1)


def atmals_power_roulette_select(probabilities: Any, exponent: float, rng: RandomContext) -> int:
    """Return a roulette-selected index for ``probabilities ** exponent``.

    ATMALS sharpens memory probabilities with a positive power before roulette
    selection. Scaling all weights by the same positive constant leaves the
    roulette distribution unchanged, so divide by the largest finite weight
    before exponentiation to avoid overflow on long CEC2011 runs.
    """
    probs = np.asarray(probabilities, dtype=np.float64).reshape(-1)
    if probs.size == 0:
        raise ValueError("probabilities must not be empty.")
    power = float(exponent)
    if not np.isfinite(power) or power < 0.0:
        raise ValueError("exponent must be a finite non-negative value.")
    if np.any(probs < 0.0):
        raise ValueError("probabilities must be non-negative.")
    if np.any(np.isposinf(probs)):
        return atmals_roulette_select(np.isposinf(probs).astype(np.float64), rng)
    if not np.all(np.isfinite(probs)):
        raise ValueError("probabilities must be finite or positive infinity.")
    max_prob = float(np.max(probs))
    if max_prob <= 0.0:
        raise ValueError("probabilities must have a positive finite sum.")
    with np.errstate(under="ignore"):
        weights = np.power(probs / max_prob, power)
    return atmals_roulette_select(weights, rng)


def atmals_senior_r1r2r3_cec2017(
    ind_best: Any,
    p: float,
    rng: RandomContext,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Port of the ATMALS CEC2017-local senior donor helper."""
    order = np.asarray(ind_best, dtype=np.int64).reshape(-1)
    pop_size = int(order.size)
    part_size = compat_round_int(float(p) * pop_size)
    if part_size <= 0 or pop_size - part_size <= part_size:
        raise ValueError(f"Invalid CEC2017 ATMALS senior partition for NP={pop_size}.")
    return (
        _sample_block(order[:part_size], pop_size, rng, name="R1"),
        _sample_block(order[part_size : pop_size - part_size], pop_size, rng, name="R2"),
        _sample_block(order[pop_size - part_size :], pop_size, rng, name="R3"),
    )


def atmals_senior_r1r2r3_cec2011(
    ind_best: Any,
    rng: RandomContext,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Port of the ATMALS CEC2011-local senior donor helper."""
    order = np.asarray(ind_best, dtype=np.int64).reshape(-1)
    pop_size = int(order.size)
    top_end = compat_round_int(pop_size * 0.1)
    mid_end = compat_round_int(pop_size * 0.9)
    if top_end <= 0 or mid_end <= top_end or mid_end >= pop_size:
        raise ValueError(f"Invalid CEC2011 ATMALS senior partition for NP={pop_size}.")
    return (
        _sample_block(order[:top_end], pop_size, rng, name="R1"),
        _sample_block(order[top_end:mid_end], pop_size, rng, name="R2"),
        _sample_block(order[mid_end:], pop_size, rng, name="R3"),
    )


def _sample_block(block: np.ndarray, pop_size: int, rng: RandomContext, *, name: str) -> np.ndarray:
    """Sample donor indices uniformly from a non-empty ATMALS donor block."""
    values = np.asarray(block, dtype=np.int64).reshape(-1)
    if values.size == 0:
        raise ValueError(f"{name} donor block is empty.")
    draws = np.floor(np.asarray(rng.random(pop_size)) * values.size).astype(np.int64)
    return values[draws]
