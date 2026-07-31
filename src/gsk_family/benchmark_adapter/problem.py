"""Problem contracts for optimizer-facing benchmark evaluation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import numpy as np


EvaluateFn = Callable[[np.ndarray], np.ndarray]


@dataclass(frozen=True)
class BenchmarkProblem:
    """Uniform optimizer-facing problem contract."""

    suite: str
    func_id: int
    dim: int
    lb: np.ndarray
    ub: np.ndarray
    optimum: float
    evaluate: EvaluateFn
    max_nfes: int
    target_error: float
    statistics_basis: str
    name: str = ""
    native_dim: int | None = None
    notes: str = ""

    def __post_init__(self) -> None:
        """Validate immutable problem metadata at construction time."""
        lb = np.asarray(self.lb, dtype=np.float64)
        ub = np.asarray(self.ub, dtype=np.float64)
        if lb.shape != (self.dim,) or ub.shape != (self.dim,):
            raise ValueError(
                f"Bounds for {self.suite} F{self.func_id} must have shape "
                f"({self.dim},), got {lb.shape} and {ub.shape}."
            )
        if np.any(lb > ub):
            raise ValueError(f"Lower bounds exceed upper bounds for {self.suite} F{self.func_id}.")

        object.__setattr__(self, "lb", lb.copy())
        object.__setattr__(self, "ub", ub.copy())


def as_population(
    population: np.ndarray,
    *,
    dim: int,
    suite: str,
    func_id: int,
    check_finite: bool = True,
) -> np.ndarray:
    """Return a validated 2D, C-contiguous, float64 population matrix.

    ``check_finite=False`` skips only the non-finite scan, for callers that hand
    ``pop`` straight to a suite dispatcher which repeats that exact scan (T2,
    2026-07-25). Measured at NP=100/D=1000: the scan is 18.42 us of
    ``as_population``'s 18.60 us -- 99 % of the cost, and a full pass over 1e5
    doubles -- so performing it twice per generation cost ~1.1 s per LSGO run
    (4-10 %). The shape/dtype/emptiness checks are ALWAYS performed; only the
    duplicate pass is elided, and only where a second scan is guaranteed.
    Default stays ``True`` so every other caller is unchanged.
    """
    pop = np.ascontiguousarray(population, dtype=np.float64)
    if pop.ndim != 2:
        raise ValueError(
            f"{suite} F{func_id} evaluate expects a 2D population matrix, "
            f"got {pop.ndim}D."
        )
    if pop.shape[0] == 0:
        raise ValueError(f"{suite} F{func_id} evaluate received an empty population.")
    if pop.shape[1] != dim:
        raise ValueError(f"{suite} F{func_id} requires D={dim}, got D={pop.shape[1]}.")
    if check_finite and not np.all(np.isfinite(pop)):
        bad = int(np.sum(~np.isfinite(pop)))
        raise ValueError(f"{suite} F{func_id} population contains {bad} non-finite values.")
    return pop


def as_fitness_vector(values: object, *, expected_rows: int, suite: str, func_id: int) -> np.ndarray:
    """Normalize benchmark return values to a 1D float64 vector."""
    fitness = np.asarray(values, dtype=np.float64)
    if fitness.ndim == 0:
        fitness = fitness.reshape(1)
    else:
        fitness = fitness.reshape(-1)
    if fitness.shape != (expected_rows,):
        raise ValueError(
            f"{suite} F{func_id} returned fitness shape {fitness.shape}; "
            f"expected ({expected_rows},)."
        )
    return fitness
