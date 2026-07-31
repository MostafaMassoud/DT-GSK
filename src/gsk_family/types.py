"""Shared result and option types."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np


@dataclass
class OptimizerOptions:
    """Common optimizer options."""

    seed: int
    rand_generator: str = "twister"
    initial_population: np.ndarray | None = None
    rng_state_after_initialization: dict[str, Any] | None = None
    values: dict[str, Any] = field(default_factory=dict)


@dataclass
class ConvergenceTrace:
    """Best-so-far values over evaluations."""

    nfes: np.ndarray
    best_fitness: np.ndarray


@dataclass
class OptimizerResult:
    """Common optimizer result shape."""

    optimizer: str
    suite: str
    func_id: int
    dim: int
    seed: int
    best_x: np.ndarray
    best_fitness: float
    error: float
    nfes: int
    termination: str
    convergence: ConvergenceTrace
    runtime_seconds: float
    params: dict[str, Any] = field(default_factory=dict)
    notes: str = ""


@dataclass
class RunRecord:
    """One row of the per-run output table."""

    optimizer: str
    suite: str
    function: int
    dimension: int
    run: int
    seed: int
    best_fitness: float
    error: float
    nfes: int
    termination: str
    runtime_seconds: float
