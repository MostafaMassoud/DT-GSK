"""EGSK (Enhanced GSK) optimizer: smoke, registry, determinism, parity sanity."""
from __future__ import annotations

import numpy as np

from gsk_family.benchmark_adapter.factory import make_problem
from gsk_family.optimizers import OPTIMIZER_IDS
from gsk_family.optimizers.egsk import optimize
from gsk_family.types import OptimizerOptions


def _run(suite, func, dim, budget, seed):
    problem = make_problem(suite, func, dim=dim, max_nfes_override=budget)
    return optimize(problem, OptimizerOptions(seed=seed, rand_generator="threefry"))


def test_smoke_oracle_sphere():
    # MATLAB test_egsk_smoke oracle: sphere F1 D10 must converge well below 1e-2.
    r = _run("sphere", 1, 10, 10000, 777)
    assert r.best_fitness < 1e-2
    assert r.error == 0.0
    assert r.nfes <= 10000
    assert r.optimizer == "egsk"


def test_solves_easy_cec2017():
    # With the SQP IP-refine, EGSK polishes the easy CEC2017 cells to the optimum.
    for func in (1, 3):
        r = _run("cec2017", func, 10, 100000, 12345)
        assert r.error == 0.0
        assert np.all(np.isfinite(r.best_x))


def test_runs_within_budget_and_finite():
    r = _run("cec2017", 7, 10, 100000, 12345)
    assert r.nfes <= 100000 + r.params["ip_fe"]   # IP-refine may add up to ip_fe evals
    assert np.isfinite(r.best_fitness)
    assert r.termination == "max_evaluations"
    assert r.params["ip_solver"] == "scipy-SLSQP"


def test_deterministic():
    a = _run("cec2017", 7, 10, 50000, 999)
    b = _run("cec2017", 7, 10, 50000, 999)
    assert a.best_fitness == b.best_fitness
    assert np.array_equal(a.best_x, b.best_x)


def test_registered_runnable():
    assert "egsk" in OPTIMIZER_IDS
    from gsk_family.analysis.project_policy import RUNNABLE_OPTIMIZERS, REFERENCE_COMPARATORS
    assert "egsk" in RUNNABLE_OPTIMIZERS         # now executable
    assert "egsk" in REFERENCE_COMPARATORS       # still a panel comparator
    from gsk_family.runners.run_experiment import OPTIMIZER_FUNCTIONS
    assert OPTIMIZER_FUNCTIONS["egsk"] is optimize


def test_statistical_sanity_vs_reference():
    # On functions the reference solves to 0, the port must too (a robust,
    # tolerance-free agreement check that does not depend on fmincon vs SLSQP).
    from gsk_family.runners.seed_policy import get_cec_seed
    for func in (1, 3, 11):
        errs = [
            _run("cec2017", func, 10, 100000, get_cec_seed(20240620, 10, func, run)).error
            for run in range(1, 4)
        ]
        assert max(errs) == 0.0
