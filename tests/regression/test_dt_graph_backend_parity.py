"""Backend-parity regression for the DT-GSK interaction graph.

The interaction graph ships compiled (numba) kernels alongside NumPy reference
implementations and selects between them with a guarded import. Two properties
must hold, and neither was covered before:

1. The compiled kernels must actually be *bound*. A wrong import path silently
   selects the NumPy fallback -- which is exactly what happened in the released
   evidence (the graph imported ``gsk_family._numba_accel``, which does not
   exist, instead of the sibling ``._numba_accel``). Nothing failed; the runs
   were merely slower.

2. Both backends must produce bit-identical trajectories. The kernels are
   compiled ``fastmath=False`` with no thread-parallel reduction precisely so
   that their arithmetic matches the NumPy path exactly.

``tests/regression/test_dt_gsk_byte_stable.py`` cannot cover either property:
its cells are D<=30, *below* the D>=50 tier at which the interaction graph
activates, so it never calls these kernels at all. These tests run at D>=50.
"""
from __future__ import annotations

import numpy as np
import pytest

from gsk_family.benchmark_adapter.factory import make_problem
from gsk_family.optimizers import dt_gsk
from gsk_family.optimizers._dt_subsystems import interaction_graph as ig
from gsk_family.types import OptimizerOptions

_KERNELS = (
    "ig_scatter_add_fast",
    "ig_symmetrise_nonneg_fast",
    "ig_symmetrise_signed_fast",
    "ig_symmetrise_inplace_fast",
    "ig_apply_decay_fast",
    "ig_build_adj_topk_fast",
)

# Skip only when numba is genuinely absent. If numba IS installed, an unbound
# kernel is a defect and must FAIL -- keying the skip off "kernels are None"
# would skip precisely the broken-import case these tests exist to catch.
try:  # pragma: no cover - environment probe
    import numba  # noqa: F401

    _HAS_NUMBA = True
except ImportError:  # pragma: no cover - environment probe
    _HAS_NUMBA = False

_requires_numba = pytest.mark.skipif(not _HAS_NUMBA, reason="numba is not installed")

_SEED = 12345
_BUDGET = 20000

# D>=50 cells: the SGSM tier, where the interaction graph is active.
_CELLS = [("cec2017", 3, 50), ("cec2017", 5, 50)]


@_requires_numba
def test_interaction_graph_kernels_are_bound() -> None:
    """Fail if the compiled interaction-graph kernels are not importable.

    Guards the import path itself: a typo selects the NumPy fallback silently.
    """
    for name in _KERNELS:
        assert getattr(ig, name, None) is not None, (
            f"{name} is None: the interaction graph fell back to NumPy. "
            "Check the import in interaction_graph.py -- it must be the "
            "relative 'from ._numba_accel import ...'."
        )


def _run_with_backend(suite: str, func: int, dim: int, *, numba: bool) -> float:
    """Optimize one cell with the compiled kernels bound or forced off."""
    saved = {name: getattr(ig, name) for name in _KERNELS}
    try:
        if not numba:
            for name in _KERNELS:
                setattr(ig, name, None)
        problem = make_problem(suite, func, dim=dim, max_nfes_override=_BUDGET)
        result = dt_gsk.optimize(problem, OptimizerOptions(seed=_SEED, rand_generator="threefry"))
        return float(result.best_fitness)
    finally:
        for name, value in saved.items():
            setattr(ig, name, value)


@_requires_numba
@pytest.mark.parametrize(("suite", "func", "dim"), _CELLS)
def test_graph_backends_are_bit_identical(suite: str, func: int, dim: int) -> None:
    """The compiled and NumPy interaction-graph paths must agree bit-for-bit.

    Locks the property that let the released (NumPy-path) evidence stay valid
    after the import was corrected: the backend changes wall-clock, never a
    reported number.
    """
    for name in _KERNELS:
        assert getattr(ig, name, None) is not None, (
            f"{name} is unbound, so both arms would run NumPy and this "
            "comparison would be vacuous."
        )
    fast = _run_with_backend(suite, func, dim, numba=True)
    slow = _run_with_backend(suite, func, dim, numba=False)
    assert fast == slow, (
        f"{suite} F{func} D{dim}: compiled backend gave {fast!r}, NumPy gave {slow!r}. "
        "The interaction-graph kernels must be numerically identical to the NumPy "
        "reference (fastmath=False, no parallel reduction); a difference means the "
        "backend now changes scientific results, not just speed."
    )
    assert np.isfinite(fast)
