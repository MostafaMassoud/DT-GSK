"""CEC2011 Real-World Optimization Benchmark Suite (22 problems)."""

from .functions import (
    NUM_FUNCTIONS as NUM_FUNCTIONS,
    all_functions as all_functions,
    cec2011_bounds as cec2011_bounds,
    cec2011_dim as cec2011_dim,
    cec2011_fname as cec2011_fname,
    cec2011_fopt as cec2011_fopt,
    cec2011_func as cec2011_func,
)

__all__ = [
    "NUM_FUNCTIONS",
    "all_functions",
    "cec2011_func",
    "cec2011_bounds",
    "cec2011_fname",
    "cec2011_fopt",
    "cec2011_dim",
]
