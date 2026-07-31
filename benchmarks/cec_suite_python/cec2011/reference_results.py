"""Reference results for CEC2011 from published GSK paper.

Source: Mohamed, A.W., Hadi, A.A. & Mohamed, A.K.
        "Gaining-sharing knowledge based algorithm for solving optimization
        problems: a novel nature-inspired algorithm"
        International Journal of Machine Learning and Cybernetics 11, 1501-1529 (2020)
        Table 24 — Result of GSK on CEC2011
        25 independent runs, 150,000 NFEs, Pop=100
"""

from __future__ import annotations

import numpy as np

# fmt: off
# Columns: [func_id, best, median, mean, worst, sd]
GSK_CEC2011_RESULTS: dict[int, dict[str, float]] = {
    1:  {"best": 0.00e+00, "median": 1.85e-21, "mean": 3.28e+00, "worst": 1.49e+01, "sd": 5.21e+00},
    2:  {"best":-1.35e+01, "median":-1.14e+01, "mean":-1.13e+01, "worst":-9.25e+00, "sd": 1.03e+00},
    3:  {"best": 1.15e-05, "median": 1.15e-05, "mean": 1.15e-05, "worst": 1.15e-05, "sd": 9.12e-13},
    4:  {"best": 0.00e+00, "median": 0.00e+00, "mean": 0.00e+00, "worst": 0.00e+00, "sd": 0.00e+00},
    5:  {"best":-2.39e+01, "median":-2.08e+01, "mean":-2.06e+01, "worst":-1.87e+01, "sd": 1.21e+00},
    6:  {"best":-1.16e+01, "median":-6.85e+00, "mean":-6.94e+00, "worst": 0.00e+00, "sd": 2.48e+00},
    7:  {"best": 1.59e+00, "median": 1.78e+00, "mean": 1.78e+00, "worst": 1.97e+00, "sd": 1.08e-01},
    8:  {"best": 2.20e+02, "median": 2.20e+02, "mean": 2.20e+02, "worst": 2.20e+02, "sd": 0.00e+00},
    9:  {"best": 1.29e+03, "median": 2.07e+03, "mean": 2.11e+03, "worst": 3.09e+03, "sd": 5.02e+02},
    10: {"best":-2.18e+01, "median":-2.16e+01, "mean":-2.16e+01, "worst":-2.14e+01, "sd": 1.19e-01},
    11: {"best": 5.09e+04, "median": 5.24e+04, "mean": 5.24e+04, "worst": 5.39e+04, "sd": 6.88e+02},
    12: {"best": 1.07e+06, "median": 1.07e+06, "mean": 1.07e+06, "worst": 1.08e+06, "sd": 1.73e+03},
    13: {"best": 1.54e+04, "median": 1.54e+04, "mean": 1.54e+04, "worst": 1.55e+04, "sd": 2.44e+00},
    14: {"best": 1.82e+04, "median": 1.84e+04, "mean": 1.84e+04, "worst": 1.86e+04, "sd": 1.22e+02},
    15: {"best": 3.28e+04, "median": 3.28e+04, "mean": 3.28e+04, "worst": 3.28e+04, "sd": 1.55e+01},
    16: {"best": 1.32e+05, "median": 1.35e+05, "mean": 1.35e+05, "worst": 1.39e+05, "sd": 2.22e+03},
    17: {"best": 1.97e+06, "median": 2.03e+06, "mean": 2.09e+06, "worst": 2.36e+06, "sd": 1.20e+05},
    18: {"best": 1.17e+06, "median": 1.27e+06, "mean": 1.27e+06, "worst": 1.57e+06, "sd": 7.56e+04},
    19: {"best": 1.75e+06, "median": 2.03e+06, "mean": 2.00e+06, "worst": 2.25e+06, "sd": 1.36e+05},
    20: {"best": 1.12e+06, "median": 1.29e+06, "mean": 1.29e+06, "worst": 1.46e+06, "sd": 9.20e+04},
    21: {"best": 1.34e+01, "median": 1.61e+01, "mean": 1.70e+01, "worst": 2.49e+01, "sd": 3.11e+00},
    22: {"best": 8.61e+00, "median": 1.28e+01, "mean": 1.29e+01, "worst": 2.09e+01, "sd": 2.93e+00},
}
# fmt: on

# Experimental setup from the paper
GSK_CEC2011_SETUP: dict[str, object] = {
    "algorithm": "GSK",
    "source": "IJMLC 2020, Table 24",
    "runs": 25,
    "max_nfes": 150_000,
    "pop_size": 100,
    "num_functions": 22,
    "excluded_functions": (),  # all 22 tested
}


def get_gsk_reference(func_id: int) -> dict[str, float]:
    """Return published GSK results for a CEC2011 function.

    Parameters
    ----------
    func_id : int
        Function number (1-22).

    Returns
    -------
    dict[str, float]
        Keys: 'best', 'median', 'mean', 'worst', 'sd'.

    Raises
    ------
    ValueError
        If *func_id* is out of range.
    """
    if func_id not in GSK_CEC2011_RESULTS:
        raise ValueError(f"func_id must be 1-22, got {func_id}")
    return GSK_CEC2011_RESULTS[func_id]


def get_gsk_mean_vector() -> np.ndarray:
    """Return (22,) array of published GSK mean values for all functions."""
    return np.array([GSK_CEC2011_RESULTS[i]["mean"] for i in range(1, 23)])
