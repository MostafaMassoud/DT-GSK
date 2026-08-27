"""Repeat-identity regression for dt-gsk at D >= 50.

``tests/regression/test_dt_gsk_byte_stable.py`` pins golden ``best_fitness``
values, but its own docstring records that its cells are ``D<=30 (below the
D>=50 SGSM/parallel-kernel tier)``. So the tier where the interaction-structure
memory accumulates and the final polish consumes its eigenframe has never had a
determinism test. CR-0007 names that gap explicitly: the byte-stability KAT
"could not catch this because its cells are D<=30, below the tier where the
graph activates", which is how the C006 polish defect reached a release.

These cells run at D = 50 and D = 100 and assert the property the manuscript
actually claims for that tier -- runs are *repeat-identical* (Section 4,
"Runs are budget-exact and repeat-identical"). Both ``best_fitness`` and the
full ``best_x`` vector must reproduce bit-for-bit.

WHY THIS IS NOT A GOLDEN-VALUE TEST. At D >= 50 the polish basis is an
eigendecomposition of the memory's signed interaction matrix, so the *value*
depends on the BLAS/LAPACK reduction order and therefore on thread count: the
manuscript states that "byte-identical reproduction at D >= 50 requires
single-threaded numerical kernels (a fixed reduction order)", and one cell here
was observed to take three different values under one, eight and inherited
thread settings. Repeat-identity, by contrast, holds at *any* fixed thread
count, so it is portable across machines and CI configurations. **Do not add
expected constants to this file** -- they would encode one machine's LAPACK and
would fail everywhere else, which is precisely the brittleness the repeat form
avoids.

The activation guard below is load-bearing: without it a profile change that
gated the memory off at these dimensions would leave the test passing while
covering nothing -- the same way the D<=30 cells silently covered nothing.
"""
from __future__ import annotations

import numpy as np
import pytest

from gsk_family.benchmark_adapter.factory import make_problem
from gsk_family.optimizers._dt_profiles import pub_overrides
from gsk_family.optimizers.dt_gsk import optimize
from gsk_family.types import OptimizerOptions

_SEED = 12345
_BUDGET = 60_000

# cec2017 cells at the two dimensions where the memory and the polish are live.
# F7, F13 and F20 are among the functions whose cells were observed to diverge
# between optimizer builds, so they exercise the sensitive path rather than a
# quiet one.
_CELLS = [
    ("cec2017", 7, 50),
    ("cec2017", 13, 50),
    ("cec2017", 20, 50),
    ("cec2017", 13, 100),
    ("cec2017", 20, 100),
]


@pytest.mark.parametrize(("suite", "func", "dim"), _CELLS)
def test_high_dim_subsystems_are_active(suite: str, func: int, dim: int) -> None:
    """The cells must actually reach the tier under test."""
    cfg = pub_overrides(dim)
    assert cfg["interaction_graph_enabled"] is True, f"D{dim}: memory not enabled"
    assert dim >= cfg["interaction_graph_min_dim"], (
        f"D{dim}: below interaction_graph_min_dim={cfg['interaction_graph_min_dim']}; "
        "this cell would exercise none of the D>=50 path"
    )
    assert cfg["final_polish_enabled"] is True, f"D{dim}: final polish not enabled"


@pytest.mark.parametrize(("suite", "func", "dim"), _CELLS)
def test_dt_gsk_repeat_identical_high_dim(suite: str, func: int, dim: int) -> None:
    """Two runs of one cell must agree bit-for-bit, fitness and vector alike."""
    results = []
    for _ in range(2):
        problem = make_problem(suite, func, dim=dim, max_nfes_override=_BUDGET)
        results.append(optimize(problem, OptimizerOptions(seed=_SEED,
                                                          rand_generator="threefry")))
    first, second = results

    assert first.best_fitness == second.best_fitness, (
        f"{suite} F{func} D{dim}: best_fitness not repeat-identical -- "
        f"{first.best_fitness!r} vs {second.best_fitness!r}"
    )
    assert first.nfes == second.nfes, (
        f"{suite} F{func} D{dim}: nfes differ -- {first.nfes} vs {second.nfes}"
    )

    x1 = np.asarray(first.best_x, dtype=np.float64)
    x2 = np.asarray(second.best_x, dtype=np.float64)
    assert x1.shape == x2.shape == (dim,)
    assert x1.tobytes() == x2.tobytes(), (
        f"{suite} F{func} D{dim}: best_x not bit-identical in "
        f"{int((x1 != x2).sum())} of {dim} coordinates"
    )
