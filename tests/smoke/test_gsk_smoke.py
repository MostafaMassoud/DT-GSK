from __future__ import annotations

import numpy as np

from gsk_family.benchmark_adapter.factory import make_problem
from gsk_family.benchmark_adapter.problem import BenchmarkProblem, as_population
from gsk_family.common.rng import RandomContext, create_fair_start
from gsk_family.optimizers.gsk import optimize
from gsk_family.types import OptimizerOptions, OptimizerResult


def _assert_result_contract(result: OptimizerResult, problem: BenchmarkProblem) -> None:
    assert result.optimizer == "gsk"
    assert result.suite == problem.suite
    assert result.func_id == problem.func_id
    assert result.dim == problem.dim
    assert result.seed >= 0
    assert result.best_x.shape == (problem.dim,)
    assert np.isfinite(result.best_fitness)
    assert result.nfes <= problem.max_nfes
    assert result.termination == "max_evaluations"
    assert result.runtime_seconds >= 0.0
    assert result.params["np"] > 0

    convergence = result.convergence
    assert convergence.nfes.shape == convergence.best_fitness.shape
    assert convergence.nfes.size >= 1
    assert np.all(np.diff(convergence.nfes) >= 0)
    assert np.all(np.diff(convergence.best_fitness) <= 0)
    assert convergence.nfes[-1] == result.nfes
    assert convergence.best_fitness[-1] == result.best_fitness


def test_gsk_sphere_smoke_and_result_contract() -> None:
    problem = make_problem("sphere", 1, dim=10, max_nfes_override=800)

    result = optimize(problem, OptimizerOptions(seed=42))

    _assert_result_contract(result, problem)
    assert result.nfes == problem.max_nfes
    assert result.error == result.best_fitness

    rng = RandomContext(99, "twister")
    random_pop = problem.lb + np.asarray(rng.random((200, problem.dim))) * (problem.ub - problem.lb)
    random_median = float(np.median(problem.evaluate(random_pop)))
    assert result.best_fitness < random_median

    reproduced = float(problem.evaluate(result.best_x.reshape(1, -1))[0])
    assert abs(reproduced - result.best_fitness) <= 1e-12 * max(1.0, abs(reproduced))


def test_gsk_same_seed_replays_trajectory() -> None:
    problem = make_problem("sphere", 1, dim=6, max_nfes_override=500)

    first = optimize(problem, {"seed": 77})
    second = optimize(problem, {"seed": 77})
    different = optimize(problem, {"seed": 78})

    assert second.best_fitness == first.best_fitness
    assert second.nfes == first.nfes
    np.testing.assert_array_equal(second.best_x, first.best_x)
    np.testing.assert_array_equal(second.convergence.nfes, first.convergence.nfes)
    np.testing.assert_array_equal(second.convergence.best_fitness, first.convergence.best_fitness)
    assert different.best_fitness != first.best_fitness


def test_gsk_fair_start_matches_internal_initialization_when_state_restored() -> None:
    problem = make_problem("sphere", 1, dim=5, max_nfes_override=300)
    fair = create_fair_start(55, "twister", 100, problem.dim, problem.lb, problem.ub)

    direct = optimize(problem, OptimizerOptions(seed=55))
    fair_started = optimize(
        problem,
        OptimizerOptions(
            seed=55,
            initial_population=fair.initial_population,
            rng_state_after_initialization=fair.rng_state_after_initialization,
        ),
    )

    assert fair_started.best_fitness == direct.best_fitness
    np.testing.assert_array_equal(fair_started.best_x, direct.best_x)
    np.testing.assert_array_equal(fair_started.convergence.nfes, direct.convergence.nfes)
    np.testing.assert_array_equal(
        fair_started.convergence.best_fitness,
        direct.convergence.best_fitness,
    )


def test_gsk_final_generation_is_fully_evaluated_but_nfes_is_clipped() -> None:
    calls: list[np.ndarray] = []

    def evaluate(population: np.ndarray) -> np.ndarray:
        pop = as_population(population, dim=3, suite="counting", func_id=1)
        calls.append(pop.copy())
        if len(calls) == 1:
            return np.arange(100.0, 110.0)
        return np.array([50.0, 49.0, 48.0, 47.0, 46.0, -1000.0, -1001.0, -1002.0, -1003.0, -1004.0])

    problem = BenchmarkProblem(
        suite="counting",
        func_id=1,
        dim=3,
        lb=np.full(3, -5.0),
        ub=np.full(3, 5.0),
        optimum=0.0,
        evaluate=evaluate,
        max_nfes=15,
        target_error=float("nan"),
        statistics_basis="raw_objective",
    )

    result = optimize(problem, {"seed": 12, "np": 10})

    assert [call.shape for call in calls] == [(10, 3), (10, 3)]
    assert result.nfes == 15
    np.testing.assert_array_equal(result.convergence.nfes, np.array([10, 15]))
    assert result.best_fitness == 46.0


def test_gsk_tiny_cec2017_run_uses_python_benchmark_adapter() -> None:
    problem = make_problem("cec2017", 1, dim=10, max_nfes_override=120)

    result = optimize(problem, {"seed": 5, "np": 20})

    _assert_result_contract(result, problem)
    assert result.nfes == 120
    assert np.isfinite(result.error)

