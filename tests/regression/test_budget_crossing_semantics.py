# Copyright (c) 2026 Mostafa Masoud <moustafa.masoud@gmail.com>
"""Ticket R-14 -- machine-check the panel's budget-crossing semantics.

WHY THIS EXISTS
---------------
An external review observed that several comparator ports compute objective
rows past ``MaxFES`` and concluded the released panel might be contaminated.
The observation is correct; the conclusion is not.  DT-GSK clips the terminal
batch before evaluating (``BudgetController.eval_batch_strict``), while the six
comparator ports are deliberate MATLAB-faithful reimplementations that evaluate
the terminal batch in full and charge only its in-budget prefix
(``eval_batch_matlab`` semantics).

That argument used to rest on source inspection alone.  These tests turn it into
evidence, so the governance audit cites a check rather than a reading:

1. ``test_counted_budget_never_exceeds_maxfes`` -- no optimizer is ever *charged*
   more than ``MaxFES``, and any uncounted overrun is bounded to a single
   terminal generation (``< NP`` rows).
2. ``test_over_cap_rows_are_inert`` -- poisoning every row computed past the cap
   with ``1e300`` leaves ``best_fitness``, ``nfes`` and ``best_x`` bit-identical.
   Truncating those rows (never computing them) is strictly weaker than
   poisoning them, so a "strict truncation" fix would be a no-op on every
   reported value.  This is the property that makes a rerun unnecessary.

The budget is deliberately NOT a multiple of the default population, so the
terminal batch is truncated and the crossing is exercised in about a second --
no campaign-scale run is needed to reproduce it.
"""
from __future__ import annotations

import importlib

import numpy as np
import pytest

from gsk_family.benchmark_adapter.problem import BenchmarkProblem
from gsk_family.types import OptimizerResult

_DIM = 10
_NP = 100
# 1050 = 10 full batches of 100 + a terminal batch charged 50 of 100.
_MAX_NFES = 1050
_SEED = 20240620
_POISON = 1e300

# module -> optimizer id.  dt-gsk is the strict one; the rest are the ports.
_PANEL = [
    ("gsk_family.optimizers.gsk", "gsk"),
    ("gsk_family.optimizers.agsk", "agsk"),
    ("gsk_family.optimizers.apgsk", "apgsk"),
    ("gsk_family.optimizers.fdb_agsk", "fdb-agsk"),
    ("gsk_family.optimizers.atmals_gsk", "atmals-gsk"),
    ("gsk_family.optimizers.egsk", "egsk"),
    ("gsk_family.optimizers.dt_gsk", "dt-gsk"),
]


def _sphere(x: np.ndarray) -> np.ndarray:
    return np.sum(np.asarray(x, dtype=np.float64) ** 2, axis=1)


class _CountingObjective:
    """Record how many rows the optimizer actually asks the objective to score."""

    def __init__(self) -> None:
        self.rows = 0
        self.batches: list[int] = []

    def __call__(self, population: np.ndarray) -> np.ndarray:
        pop = np.atleast_2d(population)
        self.rows += int(pop.shape[0])
        self.batches.append(int(pop.shape[0]))
        return _sphere(pop)


class _PoisonPastCapObjective:
    """Return ``1e300`` for every row evaluated after the counted cap is reached."""

    def __init__(self, max_nfes: int) -> None:
        self.max_nfes = int(max_nfes)
        self.seen = 0
        self.poisoned = 0

    def __call__(self, population: np.ndarray) -> np.ndarray:
        pop = np.atleast_2d(population)
        out = _sphere(pop)
        n = int(pop.shape[0])
        start, self.seen = self.seen, self.seen + n
        if self.seen > self.max_nfes:
            first_bad = max(0, self.max_nfes - start)
            self.poisoned += n - first_bad
            out = out.copy()
            out[first_bad:] = _POISON
        return out


def _problem(evaluate) -> BenchmarkProblem:
    ones = np.ones(_DIM, dtype=np.float64)
    return BenchmarkProblem(
        suite="sphere",
        func_id=1,
        dim=_DIM,
        lb=-100.0 * ones,
        ub=100.0 * ones,
        optimum=0.0,
        evaluate=evaluate,
        max_nfes=_MAX_NFES,
        target_error=float("nan"),   # NaN => never early-stop; consume the budget
        statistics_basis="raw_objective",
        name="budget-crossing-probe",
    )


def _run(module: str, evaluate) -> OptimizerResult:
    optimize = importlib.import_module(module).optimize
    return optimize(_problem(evaluate), {"seed": _SEED, "np": _NP})


@pytest.mark.parametrize("module,opt_id", _PANEL, ids=[o for _, o in _PANEL])
def test_counted_budget_never_exceeds_maxfes(module: str, opt_id: str) -> None:
    counter = _CountingObjective()
    result = _run(module, counter)

    # The charge is what the protocol equalises across the panel.
    assert result.nfes <= _MAX_NFES, (
        f"{opt_id}: charged {result.nfes} > MaxFES {_MAX_NFES}")

    # Any uncounted overrun is confined to one terminal generation.
    overrun = counter.rows - int(result.nfes)
    assert overrun >= 0, f"{opt_id}: evaluated fewer rows ({counter.rows}) than charged"
    assert overrun < max(_NP, max(counter.batches or [1])), (
        f"{opt_id}: overrun {overrun} exceeds a single terminal batch")


@pytest.mark.parametrize("module,opt_id", _PANEL, ids=[o for _, o in _PANEL])
def test_over_cap_rows_are_inert(module: str, opt_id: str) -> None:
    """Poisoning the past-cap rows must not move a single reported value."""
    clean = _run(module, _CountingObjective())
    poison = _PoisonPastCapObjective(_MAX_NFES)
    dirty = _run(module, poison)

    assert repr(dirty.best_fitness) == repr(clean.best_fitness), (
        f"{opt_id}: best_fitness moved when past-cap rows were poisoned "
        f"({clean.best_fitness!r} -> {dirty.best_fitness!r})")
    assert int(dirty.nfes) == int(clean.nfes), f"{opt_id}: nfes moved"
    np.testing.assert_array_equal(
        np.asarray(dirty.best_x, dtype=np.float64),
        np.asarray(clean.best_x, dtype=np.float64),
        err_msg=f"{opt_id}: best_x moved when past-cap rows were poisoned")
    assert dirty.best_fitness < _POISON, f"{opt_id}: a poisoned row became the incumbent"
