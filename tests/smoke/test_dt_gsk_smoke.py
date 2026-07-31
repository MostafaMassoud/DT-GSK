"""Smoke tests for the dt-gsk optimizer."""
from __future__ import annotations

import numpy as np

from gsk_family.benchmark_adapter.factory import make_problem
from gsk_family.optimizers.dt_gsk import optimize
from gsk_family.types import OptimizerOptions


def test_dt_gsk_sphere_runs() -> None:
    problem = make_problem("sphere", 1, dim=10, max_nfes_override=1500)
    result = optimize(problem, OptimizerOptions(seed=20240620, rand_generator="threefry"))
    assert result.optimizer == "dt-gsk"
    assert result.suite == "sphere"
    assert result.nfes <= 1500
    assert np.isfinite(result.best_fitness)
    assert result.best_x.shape == (10,)
    assert np.all((result.best_x >= problem.lb) & (result.best_x <= problem.ub))
    assert result.convergence.nfes.shape == result.convergence.best_fitness.shape
    assert result.convergence.nfes.size >= 1
    # best-so-far is non-increasing for minimization
    assert np.all(np.diff(result.convergence.best_fitness) <= 0.0)


def test_dt_gsk_deterministic() -> None:
    problem = make_problem("sphere", 1, dim=10, max_nfes_override=1500)
    a = optimize(problem, OptimizerOptions(seed=7))
    b = optimize(problem, OptimizerOptions(seed=7))
    assert a.best_fitness == b.best_fitness
    assert np.array_equal(a.best_x, b.best_x)
    assert a.nfes == b.nfes


def test_dt_gsk_accepts_dict_options() -> None:
    problem = make_problem("cec2017", 1, dim=10, max_nfes_override=1500)
    result = optimize(problem, {"seed": 42})
    assert result.optimizer == "dt-gsk"
    assert np.isfinite(result.best_fitness)


def test_dt_gsk_ignores_injected_fair_start() -> None:
    """dt-gsk self-inits its 5*D population; an injected X0 must be ignored."""
    problem = make_problem("sphere", 1, dim=10, max_nfes_override=1500)
    base = optimize(problem, OptimizerOptions(seed=99))
    opts = OptimizerOptions(seed=99)
    opts.initial_population = np.full((100, 10), 12345.0)
    opts.rng_state_after_initialization = {"junk": 1}
    injected = optimize(problem, opts)
    assert base.best_fitness == injected.best_fitness
    assert np.array_equal(base.best_x, injected.best_x)
