"""Byte-stability golden regression for dt-gsk.

These expected ``best_fitness`` values were validated BYTE-IDENTICAL against the
source DT-GSK project (01-Python/03-DT-GSK-v2.1) at seed=12345, max_nfes=3000
(source ``dt_gsk_optimize`` with the pub profile vs the migrated adapter). They
lock the migration's parity: any change to the vendored DT-GSK core, the RNG
substream layer, or the pub-profile config that alters the trajectory will fail
here.

Cells are D<=30 (below the D>=50 SGSM/parallel-kernel tier), so they are
deterministic regardless of thread settings.
"""
from __future__ import annotations

import pytest

from gsk_family.benchmark_adapter.factory import make_problem
from gsk_family.optimizers.dt_gsk import optimize
from gsk_family.types import OptimizerOptions

_SEED = 12345
_BUDGET = 3000

# (suite, func, dim, expected best_fitness)
_GOLDEN = [
    ("sphere", 1, 10, 0.2945738850554555),
    ("sphere", 1, 30, 761.956387784266),
    ("cec2017", 1, 10, 644728.3858160916),
    ("cec2017", 3, 30, 69409.92642761044),
]


@pytest.mark.parametrize(("suite", "func", "dim", "expected"), _GOLDEN)
def test_dt_gsk_byte_stable(suite: str, func: int, dim: int, expected: float) -> None:
    problem = make_problem(suite, func, dim=dim, max_nfes_override=_BUDGET)
    result = optimize(problem, OptimizerOptions(seed=_SEED, rand_generator="threefry"))
    assert result.best_fitness == expected, (
        f"{suite} F{func} D{dim}: got {result.best_fitness!r}, expected {expected!r} "
        "(byte-stability / source parity regression)"
    )
