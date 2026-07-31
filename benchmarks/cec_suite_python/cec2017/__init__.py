"""CEC2017 Benchmark Suite for Single-Objective Optimization (30 functions)."""

from .functions import (
    all_functions as all_functions,
    cec17_func as cec17_func,
    cec2017_bounds as cec2017_bounds,
    cec2017_f_name as cec2017_f_name,
    cec2017_fname as cec2017_fname,
    cec2017_fopt as cec2017_fopt,
    cec2017_func as cec2017_func,
    cec2017_test_func as cec2017_test_func,
)

__all__ = [
    "cec2017_func", "cec2017_test_func", "cec17_func",
    "cec2017_bounds", "cec2017_fopt", "cec2017_fname", "cec2017_f_name",
    "all_functions",
]
