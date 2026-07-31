from __future__ import annotations

import numpy as np

from gsk_family.benchmark_adapter.factory import make_problem
from gsk_family.benchmark_adapter.problem import BenchmarkProblem, as_population
from gsk_family.common.rng import create_fair_start
from gsk_family.optimizers.atmals_gsk import optimize
from gsk_family.types import OptimizerOptions, OptimizerResult


def _atmals_options(seed: int, *, protocol: str = "cec2017", np_size: int = 20) -> dict[str, object]:
    return {"seed": seed, "protocol": protocol, "np": np_size}


def _assert_result_contract(
    result: OptimizerResult,
    problem: BenchmarkProblem,
    protocol: str,
) -> None:
    assert result.optimizer == "atmals-gsk"
    assert result.suite == problem.suite
    assert result.func_id == problem.func_id
    assert result.dim == problem.dim
    assert result.seed >= 0
    assert result.best_x.shape == (problem.dim,)
    assert np.isfinite(result.best_fitness)
    assert result.nfes <= problem.max_nfes
    assert result.termination == "max_evaluations"
    assert result.runtime_seconds >= 0.0
    assert result.params["protocol"] == protocol
    assert result.params["np"] >= 12
    assert result.params["nls"] >= 1

    convergence = result.convergence
    assert convergence.nfes.shape == convergence.best_fitness.shape
    assert convergence.nfes.size >= 1
    assert np.all(np.diff(convergence.nfes) >= 0)
    assert np.all(np.diff(convergence.best_fitness) <= 0)
    assert convergence.nfes[-1] == result.nfes
    assert convergence.best_fitness[-1] == result.best_fitness


def test_atmals_gsk_sphere_smoke_and_result_contract() -> None:
    problem = make_problem("sphere", 1, dim=8, max_nfes_override=400)

    result = optimize(problem, _atmals_options(42))

    _assert_result_contract(result, problem, "cec2017")
    assert result.nfes == problem.max_nfes

    reproduced = float(problem.evaluate(result.best_x.reshape(1, -1))[0])
    assert abs(reproduced - result.best_fitness) <= 1e-12 * max(1.0, abs(reproduced))


def test_atmals_gsk_same_seed_replays_trajectory() -> None:
    problem = make_problem("sphere", 1, dim=6, max_nfes_override=280)

    first = optimize(problem, _atmals_options(77))
    second = optimize(problem, _atmals_options(77))
    different = optimize(problem, _atmals_options(78))

    assert second.best_fitness == first.best_fitness
    assert second.nfes == first.nfes
    np.testing.assert_array_equal(second.best_x, first.best_x)
    np.testing.assert_array_equal(second.convergence.nfes, first.convergence.nfes)
    np.testing.assert_array_equal(second.convergence.best_fitness, first.convergence.best_fitness)
    assert different.best_fitness != first.best_fitness


def test_atmals_gsk_fair_start_matches_internal_initialization_when_state_restored() -> None:
    problem = make_problem("sphere", 1, dim=5, max_nfes_override=220)
    fair = create_fair_start(55, "twister", 20, problem.dim, problem.lb, problem.ub)

    direct = optimize(problem, _atmals_options(55))
    fair_started = optimize(
        problem,
        OptimizerOptions(
            seed=55,
            initial_population=fair.initial_population,
            rng_state_after_initialization=fair.rng_state_after_initialization,
            values={"protocol": "cec2017", "np": 20},
        ),
    )

    assert fair_started.best_fitness == direct.best_fitness
    np.testing.assert_array_equal(fair_started.best_x, direct.best_x)
    np.testing.assert_array_equal(fair_started.convergence.nfes, direct.convergence.nfes)
    np.testing.assert_array_equal(
        fair_started.convergence.best_fitness,
        direct.convergence.best_fitness,
    )


def test_atmals_gsk_budget_crossing_scans_only_budgeted_child_prefix() -> None:
    calls: list[np.ndarray] = []

    def evaluate(population: np.ndarray) -> np.ndarray:
        pop = as_population(population, dim=3, suite="counting", func_id=1)
        calls.append(pop.copy())
        if len(calls) == 1:
            return np.arange(100.0, 112.0)
        return np.array(
            [90.0, 91.0, 92.0, 93.0, 94.0, 95.0, -1000.0, -1001.0, -1002.0, -1003.0, -1004.0, -1005.0]
        )

    problem = BenchmarkProblem(
        suite="counting",
        func_id=1,
        dim=3,
        lb=np.full(3, -5.0),
        ub=np.full(3, 5.0),
        optimum=float("nan"),
        evaluate=evaluate,
        max_nfes=18,
        target_error=float("nan"),
        statistics_basis="raw_objective",
    )

    result = optimize(problem, _atmals_options(12, np_size=12))

    assert [call.shape for call in calls] == [(12, 3), (12, 3)]
    assert result.nfes == 18
    assert result.best_fitness == 90.0
    np.testing.assert_array_equal(result.convergence.nfes, np.array([12, 18]))
    np.testing.assert_array_equal(result.convergence.best_fitness, np.array([100.0, 90.0]))


def test_atmals_gsk_zeroes_final_error_without_early_target_stop() -> None:
    calls = 0

    def evaluate(population: np.ndarray) -> np.ndarray:
        nonlocal calls
        pop = as_population(population, dim=2, suite="target", func_id=1)
        calls += 1
        if calls == 1:
            return np.arange(10.0, 22.0)
        return np.zeros(pop.shape[0])

    problem = BenchmarkProblem(
        suite="target",
        func_id=1,
        dim=2,
        lb=np.full(2, -5.0),
        ub=np.full(2, 5.0),
        optimum=0.0,
        evaluate=evaluate,
        max_nfes=36,
        target_error=1e-8,
        statistics_basis="error_vs_optimum",
    )

    result = optimize(problem, _atmals_options(19, np_size=12))

    assert result.termination == "max_evaluations"
    assert result.error == 0.0
    assert result.nfes == 36


def test_atmals_gsk_cec2011_dim1_protocol_branch_runs() -> None:
    problem = make_problem("sphere", 1, dim=1, max_nfes_override=120)

    result = optimize(problem, _atmals_options(88, protocol="cec2011", np_size=20))

    _assert_result_contract(result, problem, "cec2011")
    assert result.nfes == 120
