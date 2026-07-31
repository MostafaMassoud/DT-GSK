"""CEC2013 Benchmark Suite for Single-Objective Optimization (28 functions)."""

from .functions import (
    all_functions as all_functions,
    cec2013_bounds as cec2013_bounds,
    cec2013_fname as cec2013_fname,
    cec2013_fopt as cec2013_fopt,
    cec2013_func as cec2013_func,
    cec2013_test_func as cec2013_test_func,
)

__all__ = [
    "cec2013_func", "cec2013_test_func",
    "cec2013_bounds", "cec2013_fopt", "cec2013_fname",
    "all_functions",
]
