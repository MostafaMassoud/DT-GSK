"""Regression lock: the dt-gsk convergence trace is best-so-far (monotone).

The deep-stall multi-start re-initializes the working population when the
incumbent stalls, and the vendored core reports the *working* incumbent to
``curve_callback`` -- so the raw emission can regress after a restart even
though the returned result (preserved global best) never loses ground. The
adapter must clamp the recorded ``ConvergenceTrace`` to the running minimum.

The plateau objective below makes the scenario deterministic: the initial
population scores 0.0 and every later evaluation scores 1.0, so the incumbent
can never improve, the deep-stall restart is guaranteed to fire (thresholds
lowered via config overrides), and the post-restart working incumbent is
strictly worse than the pre-restart best.
"""
from __future__ import annotations

import dataclasses

import numpy as np

from gsk_family.benchmark_adapter.problem import BenchmarkProblem
from gsk_family.optimizers._dt_core import dt_gsk_optimize
from gsk_family.optimizers._dt_profiles import build_pub_config
from gsk_family.optimizers.dt_gsk import optimize
from gsk_family.types import OptimizerOptions

_DIM = 10
_MAX_NFES = 4000
_INIT_EVALS = 5 * _DIM  # dt-gsk self-init population is np_init_mult * dim
_SEED = 20240620
_DEEP_STALL_OVERRIDES = {
    "deep_stall_min_budget": 1000,
    "deep_stall_frac": 0.05,
    "deep_stall_cooldown_frac": 0.02,
    "deep_stall_stop_frac": 0.99,
}


class _PlateauObjective:
    """Score the first ``n_zero`` evaluations 0.0 and every later one 1.0."""

    def __init__(self, n_zero: int) -> None:
        self._n_zero = int(n_zero)
        self._count = 0

    def __call__(self, population: np.ndarray) -> np.ndarray:
        rows = int(np.atleast_2d(population).shape[0])
        fitness = np.where(
            np.arange(self._count, self._count + rows) < self._n_zero, 0.0, 1.0
        )
        self._count += rows
        return fitness.astype(np.float64)


def _plateau_problem() -> BenchmarkProblem:
    ones = np.ones(_DIM, dtype=np.float64)
    return BenchmarkProblem(
        suite="sphere",
        func_id=1,
        dim=_DIM,
        lb=-100.0 * ones,
        ub=100.0 * ones,
        optimum=float("nan"),
        evaluate=_PlateauObjective(_INIT_EVALS),
        max_nfes=_MAX_NFES,
        target_error=float("nan"),
        statistics_basis="raw_objective",
        name="plateau",
    )


def test_deep_stall_fires_and_raw_core_emission_regresses() -> None:
    """Scenario guard: the raw core emission must rise after the restart.

    If this stops rising, the plateau scenario no longer triggers the
    deep-stall restart and the adapter assertion below proves nothing.
    """
    config = dataclasses.replace(
        build_pub_config(
            _DIM, seed=_SEED, max_nfes=_MAX_NFES, bounds=(-100.0, 100.0)
        ),
        **_DEEP_STALL_OVERRIDES,
    )
    raw: list[float] = []
    result = dt_gsk_optimize(
        objective=_PlateauObjective(_INIT_EVALS),
        config=config,
        curve_callback=lambda evals_used, best_f: raw.append(float(best_f)),
    )
    assert result.best_f == 0.0  # the preserved global best never loses ground
    assert min(raw) == 0.0
    assert max(np.diff(raw)) > 0.0  # the working incumbent regressed


def test_adapter_convergence_trace_is_monotone_across_deep_stall() -> None:
    """The recorded ConvergenceTrace must be best-so-far despite the restart."""
    result = optimize(
        _plateau_problem(),
        OptimizerOptions(seed=_SEED, values=dict(_DEEP_STALL_OVERRIDES)),
    )
    trace = result.convergence.best_fitness
    assert trace.size >= 2
    assert np.all(np.diff(trace) <= 0.0)
    assert trace[-1] == 0.0  # the curve ends at the returned best
    assert result.best_fitness == 0.0
