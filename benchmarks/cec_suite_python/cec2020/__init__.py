"""CEC2020 Benchmark Suite for Single-Objective Bound-Constrained Optimization.

10 test functions:
  F1:    Bent Cigar (unimodal)
  F2:    Schwefel (multimodal)
  F3:    Lunacek Bi-Rastrigin (multimodal)
  F4:    Griewank-Rosenbrock (multimodal, no shift/rotate)
  F5-F7: Hybrid functions
  F8-F10: Composition functions

Library suite (audit cross M-07)
--------------------------------
This suite is **library-only** in the DT-GSK project.  It is fully
importable and JIT-warmed by every worker process (see
``gsk.experiment._do_warmup`` and ``gsk.benchmark_factory.init_cec_worker``)
but it is **not** wired into ``SUITE_META``.  The standard ``run.py``
subcommands (``baseline``, ``step2``, ``cec2011``, ``cec2013``) do not
benchmark CEC2020.  It is reserved for the next-version **DT-GSK**
fork (the high-D / structure-aware layer above DT-GSK).

Numerical precision: this suite intentionally drops ``fastmath=True``
from its Numba kernels (audit H-01) so that the basic-kernel outputs
that compose into the F8-F10 composition functions are bit-stable
across CPU ISAs (no FMA / approximate-transcendental drift).

Usage:
  from benchmarks.cec_suite_python.cec2020 import cec2020_func
  f = cec2020_func(x, func_id)   # x: (M, D) or (D,), func_id: 1-10

Runner-parity dimensions are ``{5, 10, 15, 20}``.  Public F1 and F8 are
unavailable at D=5 and D=15 because the staged C++/MEX reference distribution
does not ship marker files for those cells.
"""

from .functions import (
    BIASES as BIASES,
)
from .functions import (
    cec20_func as cec20_func,
)
from .functions import (
    cec2020_bounds as cec2020_bounds,
)
from .functions import (
    cec2020_fname as cec2020_fname,
)
from .functions import (
    cec2020_fopt as cec2020_fopt,
)
from .functions import (
    cec2020_func as cec2020_func,
)
from .functions import (
    cec2020_test_func as cec2020_test_func,
)

__all__ = [
    "cec2020_func", "cec20_func", "cec2020_test_func",
    "cec2020_bounds", "cec2020_fopt", "cec2020_fname", "BIASES",
]
