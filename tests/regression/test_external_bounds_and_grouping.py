"""External-baseline defects found by the 2026-07-28 crossover audit.

Both defects were reported against the sibling project (05-Human-Inspired-Family)
and confirmed present in this repository's vendored/first-party copies. Neither
contaminated any committed artifact -- MOS ran only on CEC2013LSGO, whose boxes
are per-variable uniform, and DECC-G ran only at D=905/1000 -- but both were
reachable from committed configs. See decision_log D-0025.
"""

from __future__ import annotations

import numpy as np
import pytest

from benchmarks.cec_suite_python.cec2011 import cec2011_bounds
from gsk_family.optimizers.external import optimize_decc_g, optimize_mos
from gsk_family.optimizers.external._base import OptimizerOptions


class _BoxProbe:
    """Problem shim that records every evaluated point's box violations."""

    suite = "probe"
    func_id = 1
    statistics_basis = "raw_objective"
    optimum = float("nan")
    target_error = float("nan")
    notes = ""

    def __init__(self, lb, ub, max_nfes: int) -> None:
        self.lb = np.asarray(lb, dtype=np.float64)
        self.ub = np.asarray(ub, dtype=np.float64)
        self.dim = int(self.lb.size)
        self.max_nfes = int(max_nfes)
        self.violations = 0
        self.rows = 0

    def evaluate(self, pop):
        """Evaluate a population, counting rows that fall outside the box."""
        pop = np.atleast_2d(np.asarray(pop, dtype=np.float64))
        outside = ((self.lb - pop > 0) | (pop - self.ub > 0)).any(axis=1)
        self.violations += int(outside.sum())
        self.rows += int(pop.shape[0])
        return np.sum(pop * pop, axis=1)


def _run_mos(problem) -> None:
    try:
        optimize_mos(problem, OptimizerOptions(seed=20240620, rand_generator="threefry"))
    except AttributeError:
        # The shim intentionally omits result-builder fields; the search itself
        # has already run to budget by the time build_result is reached.
        pass


@pytest.mark.parametrize("func_id", [21, 17, 22, 15, 12])
def test_mos_respects_heterogeneous_bounds(func_id: int) -> None:
    """MOS must never evaluate outside the box on per-variable-varying bounds.

    Until 2026-07-28 MTS-LS1-Reduced received dim-0 scalars while the GA and
    Solis-Wets techniques received the lb/ub vectors, so its probes clipped
    against the wrong bounds. Measured before the fix on these five CEC2011
    problems: 6.96%-16.82% of evaluations outside the box, excursions up to
    1899 units, and a returned best_x that could itself be infeasible.
    """
    lb, ub = cec2011_bounds(func_id)
    probe = _BoxProbe(lb, ub, max_nfes=12_000)

    _run_mos(probe)

    assert probe.rows > 0, "probe recorded no evaluations"
    assert probe.violations == 0, (
        f"MOS evaluated {probe.violations}/{probe.rows} points outside the box on "
        f"CEC2011 F{func_id}"
    )


def test_mos_is_identity_on_uniform_bounds() -> None:
    """The fix must not perturb a uniform box, where the old code was correct.

    Every CEC2013LSGO function has per-variable-uniform bounds, so dim-0 scalars
    equalled the true per-dimension bounds and the promoted MOS bank is
    unaffected by the change.
    """
    lb, ub = cec2011_bounds(1)  # F1: 6 identical [-6.4, 6.35] variables
    assert np.all(lb == lb[0]) and np.all(ub == ub[0]), "fixture is not a uniform box"
    probe = _BoxProbe(lb, ub, max_nfes=8_000)

    _run_mos(probe)

    assert probe.violations == 0


class _Sphere:
    suite = "probe"
    func_id = 1
    statistics_basis = "raw_objective"
    optimum = float("nan")
    target_error = float("nan")
    notes = ""

    def __init__(self, dim: int) -> None:
        self.dim = dim
        self.lb = np.full(dim, -100.0)
        self.ub = np.full(dim, 100.0)
        self.max_nfes = 4_000

    def evaluate(self, pop):
        """Sphere objective."""
        return np.sum(np.atleast_2d(np.asarray(pop, dtype=np.float64)) ** 2, axis=1)


@pytest.mark.parametrize("dim", [5, 20, 100])
def test_decc_g_refuses_degenerate_grouping(dim: int) -> None:
    """At dim <= group_size the decomposition collapses to one subcomponent.

    Regrouping is then a no-op and the run is SaNSDE with adaptive weighting --
    a different algorithm wearing the DECC-G label. dim == 100 is included
    deliberately: with the default group_size of 100 it is degenerate too, so
    "below D=100" understates the affected range.
    """
    with pytest.raises(ValueError, match="degenerate"):
        optimize_decc_g(_Sphere(dim), OptimizerOptions(seed=1, rand_generator="threefry"))


def test_decc_g_allows_explicit_smaller_group_size() -> None:
    """The guard blocks accidents, not deliberate decomposed runs."""
    try:
        optimize_decc_g(
            _Sphere(20),
            OptimizerOptions(seed=1, rand_generator="threefry", values={"group_size": 5}),
        )
    except ValueError as exc:  # pragma: no cover - guard must not fire here
        pytest.fail(f"guard fired on a legitimate 4-subcomponent run: {exc}")
    except AttributeError:
        pass  # shim lacks result-builder fields; the run itself completed
