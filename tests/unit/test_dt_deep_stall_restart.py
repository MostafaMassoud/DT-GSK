"""Contract for the deep-stall full-restart (catastrophic-trap fix), now default-ON.

The mechanism performs a true multi-start (full population re-init) when the
incumbent is frozen for a large fraction of the budget, with a global-best that
survives the restart. It is a standard DT-GSK mechanism (``deep_stall_restart_enabled``
defaults to True). It must rescue the known CEC2017 F30 D10 run-27 basin trap, be
inert on non-stalling runs, stay within budget, and -- via the min-budget guard --
leave tiny budgets byte-identical so the byte-stability KAT is unaffected.
"""
from __future__ import annotations

from gsk_family.benchmark_adapter.factory import make_problem
from gsk_family.optimizers.dt_gsk import optimize
from gsk_family.types import OptimizerOptions

# F30 D10 run 27 (unified base 20240620): the lone 1984x catastrophic basin trap.
_TRAP_SEED = 87242640


def _run(func, dim, seed, budget, enabled=None):
    problem = make_problem("cec2017", func, dim=dim, max_nfes_override=budget)
    values = {} if enabled is None else {"deep_stall_restart_enabled": enabled}
    return optimize(problem, OptimizerOptions(seed=seed, rand_generator="threefry", values=values))


class TestDeepStallRestart:
    def test_default_is_on_and_rescues_trap(self):
        # Default behaviour (mechanism on) must rescue the trap; explicit-off reproduces it.
        on = _run(30, 10, _TRAP_SEED, 100000)               # default -> on
        off = _run(30, 10, _TRAP_SEED, 100000, enabled=False)
        assert off.error > 1e4          # the catastrophic trap, mechanism disabled
        assert on.error < 1e3           # rescued by default
        assert on.nfes <= 100000        # no extra evaluations

    def test_inert_on_non_stalling_run(self):
        # A healthy run never deep-stalls -> on == off byte-for-byte.
        on = _run(4, 10, 1004, 30000)
        off = _run(4, 10, 1004, 30000, enabled=False)
        assert on.best_fitness == off.best_fitness

    def test_min_budget_guard_keeps_tiny_budgets_inert(self):
        # Below deep_stall_min_budget (20000) the restart never fires, so on == off
        # -- this is what keeps the 3000-NFE byte-stability KAT identical default-on.
        for seed in (1001, 1002):
            on = _run(13, 10, seed, 3000)
            off = _run(13, 10, seed, 3000, enabled=False)
            assert on.best_fitness == off.best_fitness
