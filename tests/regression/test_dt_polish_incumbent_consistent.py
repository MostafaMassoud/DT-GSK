"""Regression: the final polish must receive a self-consistent incumbent (C006).

``_final_polish_compass(x0, f0, ...)`` trusts ``f0`` without re-evaluating ``x0``.
Before the fix, the core refreshed ``best_idx``/``best_f`` mid-generation (e.g. after a
local-search improvement) while ``best_x`` was only re-materialised from the population
at the END of the generation. The polish could therefore be entered with a stale vector
paired with a newer incumbent's fitness, and would search around one point while judging
probes against another point's value.

Reported results were never corrupted -- the write-back requires a strict improvement and
a protected global best is restored at return -- but the polish, the one component with an
isolated significant effect, was measured in a handicapped form.

This test pins the invariant directly: at polish entry, ``f(x0) == f0``.
"""
from __future__ import annotations

import math

import numpy as np
import pytest

from gsk_family.benchmark_adapter.factory import make_problem
from gsk_family.optimizers import _dt_core
from gsk_family.optimizers._dt_profiles import build_pub_config

# The polish is gated to D >= 50 in the publication profile; below that it never fires.
_CELLS = [("cec2017", 3, 50), ("cec2017", 5, 50)]
_SEED = 12345
_BUDGET = 30000


@pytest.mark.parametrize(("suite", "func", "dim"), _CELLS)
def test_polish_entry_incumbent_is_consistent(
    suite: str, func: int, dim: int, monkeypatch: pytest.MonkeyPatch
) -> None:
    """f0 handed to the compass must be the true objective value of x0."""
    problem = make_problem(suite, func, dim=dim)
    calls: list[tuple[np.ndarray, float]] = []
    real_compass = _dt_core._final_polish_compass

    def spy(x0: np.ndarray, f0: float, **kwargs: object):
        """Record the (x0, f0) pair the core passes into the compass."""
        calls.append((np.array(x0, dtype=np.float64, copy=True), float(f0)))
        return real_compass(x0, f0, **kwargs)  # type: ignore[arg-type]

    monkeypatch.setattr(_dt_core, "_final_polish_compass", spy)

    def evaluate_one(x: np.ndarray) -> float:
        """Objective value of a single point (the core evaluates in batches)."""
        return float(np.asarray(problem.evaluate(np.atleast_2d(x))).ravel()[0])

    config = build_pub_config(dim, seed=_SEED, max_nfes=_BUDGET)
    assert config.final_polish_enabled, f"polish must be active at D={dim} for this test"

    _dt_core.dt_gsk_optimize(objective=problem.evaluate, config=config)

    assert calls, "the final polish never fired; the test cell is not exercising it"
    for x0, f0 in calls:
        actual = evaluate_one(x0)
        # Compare with a relative tolerance, not for equality: the core's stored
        # fitness comes from the batched benchmark kernel while this re-evaluation
        # passes a single row, and the two differ in the last few ULPs (the known
        # batch-vs-single reduction-order residual). A genuinely stale incumbent is
        # a DIFFERENT point and disagrees by orders of magnitude, not by 1e-16.
        assert math.isclose(actual, f0, rel_tol=1e-9, abs_tol=1e-12), (
            f"polish entered with an inconsistent incumbent: f(x0)={actual!r} but "
            f"f0={f0!r}. The vector and its fitness refer to different individuals "
            "(C006): re-materialise best_idx/best_f/best_x atomically before polishing."
        )
