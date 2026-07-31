"""Fitness-Distance Balance score helpers for FDB-AGSK."""

from __future__ import annotations

from typing import Any

import numpy as np

from gsk_family.common.numeric_compat import ensure_2d_population, stable_argsort
from gsk_family.common.rng import RandomContext


def _fitness_vector(fitness: Any, *, expected_rows: int) -> np.ndarray:
    """Validate FDB fitness input as a one-dimensional vector."""
    values = np.asarray(fitness, dtype=np.float64).reshape(-1)
    if values.shape != (expected_rows,):
        raise ValueError(f"fitness must have shape ({expected_rows},), got {values.shape}.")
    return values


def _fdb_scores(population: Any, fitness: Any) -> tuple[np.ndarray, bool, bool]:
    """Compute normalized FDB scores and degeneracy flags."""
    pop = ensure_2d_population(population)
    fit = _fitness_vector(fitness, expected_rows=pop.shape[0])
    best_index = int(np.argmin(fit))
    best = pop[best_index, :]

    flat_fitness = bool(np.min(fit) == np.max(fit))
    roulette_degenerate = bool(np.sum(fit) >= np.inf or not (np.sum(best) < np.inf))
    if flat_fitness:
        return np.zeros(pop.shape[0], dtype=np.float64), True, roulette_degenerate

    distances = np.sum(np.abs(best - pop), axis=1, dtype=np.float64)
    min_fitness = float(np.min(fit))
    max_min_fitness = float(np.max(fit) - min_fitness)
    min_distance = float(np.min(distances))
    max_min_distance = float(np.max(distances) - min_distance)

    norm_fitness = 1.0 - ((fit - min_fitness) / max_min_fitness)
    norm_distances = (distances - min_distance) / max_min_distance
    return norm_fitness + norm_distances, False, roulette_degenerate


def fdb_score_best(population: Any, fitness: Any, rng: RandomContext) -> int:
    """Return the 0-based FDB best-score index."""
    scores, flat_fitness, _ = _fdb_scores(population, fitness)
    if flat_fitness:
        return int(rng.randi(scores.size)) - 1
    return int(np.argmax(scores))


def fdb_score_ranking(population: Any, fitness: Any, rng: RandomContext) -> np.ndarray:
    """Return 0-based indices sorted by descending FDB score."""
    scores, flat_fitness, _ = _fdb_scores(population, fitness)
    if flat_fitness:
        _ = rng.randi(scores.size)
        return np.array([], dtype=np.int64)
    return stable_argsort(scores, descending=True).astype(np.int64, copy=False)


def fdb_score_roulette(population: Any, fitness: Any, rng: RandomContext) -> int:
    """Return a 0-based roulette-wheel FDB index."""
    scores, flat_fitness, roulette_degenerate = _fdb_scores(population, fitness)
    if flat_fitness or roulette_degenerate:
        return int(rng.randi(scores.size)) - 1

    total = float(np.sum(scores))
    threshold = float(rng.random()) * total
    cumulative = np.cumsum(scores)
    index = int(np.searchsorted(cumulative, threshold, side="left"))
    return min(index, scores.size - 1)
