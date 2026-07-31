"""CEC2013LSGO Benchmark Suite for Large-Scale Global Optimization.

15 benchmark functions (D=1000, except F13-F14 with D=905) from:

    X. Li, K. Tang, M.N. Omidvar, Z. Yang, K. Qin (2013).
    "Benchmark Functions for the CEC'2013 Special Session and
    Competition on Large-Scale Global Optimization."

Evaluation budget: 3,000,000 function evaluations per run (flat,
including the D=905 functions F13-F14).
Optimal value: f* = 0 for all functions, **except F12 (Shifted
Rosenbrock) where f(xopt) = N - 1 = 999** -- Rosenbrock's minimum
is at z = 1 (all-ones), not z = 0.  This is enforced lazily on
first use of F12 by ``composite._assert_f12_baseline`` (audit
C-01 lsgo, AUDIT-15).

Campaign suite (audit cross M-07, superseded: was library-only pre-rename)
--------------------------------------------------------------------------
This suite is a campaign suite in this project: it backs the
``family_cec2013lsgo.yml`` / ``baselines_cec2013lsgo.yml`` large-scale
campaigns (10 algorithms complete at 375/375 runs as of 2026-07-27; the
suite is not yet part of the paper's scored panel). Problems are served by
``gsk_family.benchmark_adapter.factory.make_problem`` and JIT
kernels are warmed per spawned worker by
``gsk_family.runners.run_experiment._init_process_worker`` when
an LSGO run is selected.

Data integrity: ``data.pkl`` is verified by SHA-256 at module import
(see :func:`transforms.verify_data_integrity`); rotation matrices are
checked for orthogonality at first use (audit M-02 lsgo).
"""

from __future__ import annotations

from .functions import (
    NUM_FUNCTIONS as NUM_FUNCTIONS,
    all_functions as all_functions,
    cec2013lsgo_bounds as cec2013lsgo_bounds,
    cec2013lsgo_dim as cec2013lsgo_dim,
    cec2013lsgo_fname as cec2013lsgo_fname,
    cec2013lsgo_fopt as cec2013lsgo_fopt,
    cec2013lsgo_func as cec2013lsgo_func,
    cec2013lsgo_test_func as cec2013lsgo_test_func,
)
from .transforms import (
    GroupInfo as GroupInfo,
    GroupInfoFlat as GroupInfoFlat,
    clear_caches as clear_caches,
    load_group_flat as load_group_flat,
    load_group_info as load_group_info,
    verify_data_integrity as verify_data_integrity,
)

# Audit API-LOW-1: re-export the LSGO group-info accessors so callers
# don't have to dig into ``benchmarks.cec_suite_python.cec2013lsgo.transforms``
# directly.  ``GroupInfo`` / ``GroupInfoFlat`` are the named-tuple
# return types of ``load_group_info`` / ``load_group_flat``; downstream
# downstream code (the structure-aware layer that actually consumes
# these groupings) needs both to type-check its decompositions.  The
# main convenience surface (``cec2013lsgo_func`` etc.) stays the same.
__all__ = [
    "NUM_FUNCTIONS",
    "cec2013lsgo_func", "cec2013lsgo_test_func",
    "cec2013lsgo_bounds", "cec2013lsgo_fopt", "cec2013lsgo_fname",
    "cec2013lsgo_dim",
    "all_functions",
    "clear_caches", "verify_data_integrity",
    # Group-info accessors for structure-aware downstream consumers
    "GroupInfo", "GroupInfoFlat",
    "load_group_info", "load_group_flat",
]
