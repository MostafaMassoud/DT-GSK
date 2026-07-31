from __future__ import annotations

import math

import numpy as np
import pytest

from benchmarks.cec_suite_python.cec2011 import cec2011_bounds, cec2011_func
from benchmarks.cec_suite_python.cec2013 import cec2013_func
from benchmarks.cec_suite_python.cec2017 import cec2017_func
from benchmarks.cec_suite_python.cec2020 import cec2020_func
from gsk_family.benchmark_adapter.factory import make_problem
from gsk_family.benchmark_adapter.protocol import (
    STAT_ERROR,
    STAT_RAW,
    all_function_ids,
    default_dimensions,
    default_function_ids,
)


def _midpoint_population(lb: np.ndarray, ub: np.ndarray, rows: int = 2) -> np.ndarray:
    midpoint = (lb + ub) / 2.0
    return np.repeat(midpoint.reshape(1, -1), rows, axis=0)


@pytest.mark.parametrize(
    ("suite", "func_id", "dim"),
    [
        ("cec2011", 1, None),
        ("cec2013", 1, 10),
        ("cec2013lsgo", 1, None),
        ("cec2017", 1, 10),
        ("cec2020", 2, 5),
    ],
)
def test_make_problem_evaluates_population_for_each_suite(
    suite: str,
    func_id: int,
    dim: int | None,
) -> None:
    problem = make_problem(suite, func_id, dim)
    population = _midpoint_population(problem.lb, problem.ub)

    values = problem.evaluate(population)

    assert values.shape == (2,)
    assert values.dtype == np.float64
    assert np.all(np.isfinite(values))


def test_sphere_problem_evaluates_exactly() -> None:
    problem = make_problem("sphere", 1, 3, max_nfes_override=123)
    values = problem.evaluate(np.array([[1.0, 2.0, 3.0], [0.0, -1.0, 2.0]]))

    np.testing.assert_allclose(values, np.array([14.0, 5.0]))
    assert problem.max_nfes == 123
    assert problem.optimum == 0.0
    assert problem.statistics_basis == STAT_ERROR


def test_cec2017_default_functions_exclude_f2_but_explicit_f2_is_constructible() -> None:
    defaults = default_function_ids("cec2017")

    assert 1 in defaults
    assert 2 not in defaults
    assert 30 in defaults
    assert 2 in all_function_ids("cec2017")

    problem = make_problem("cec2017", 2, 10)
    assert problem.func_id == 2
    assert "F2" in problem.notes


def test_native_raw_objective_suites_use_nan_optimum_and_no_target() -> None:
    for suite in ("cec2011", "cec2013lsgo"):
        problem = make_problem(suite, 1)
        assert problem.statistics_basis == STAT_RAW
        assert math.isnan(problem.optimum)
        assert math.isnan(problem.target_error)


def test_known_optimum_suites_use_error_statistics() -> None:
    cases = [
        ("cec2013", 1, 10, -1400.0, 100_000),
        ("cec2017", 1, 10, 100.0, 100_000),
        ("cec2020", 2, 5, 1100.0, 50_000),
    ]
    for suite, func_id, dim, optimum, max_nfes in cases:
        problem = make_problem(suite, func_id, dim)
        assert problem.statistics_basis == STAT_ERROR
        assert problem.optimum == optimum
        assert problem.target_error == 1e-8
        assert problem.max_nfes == max_nfes


def test_cec2011_bounds_are_copied_into_mutable_problem_arrays() -> None:
    problem = make_problem("cec2011", 1)
    original_lb, _ = cec2011_bounds(1)
    before = float(original_lb[0])

    problem.lb[0] = before + 1.0

    after_lb, _ = cec2011_bounds(1)
    assert float(after_lb[0]) == before


def test_cec2011_f4_f6_match_reference_probe_values() -> None:
    """Guard CEC2011 F04-F06 quirks that strongly affect GSK reference parity."""
    f4_cases = [
        (np.array([2.5]), 29.042242154614943),
        (np.array([1.25]), 28.575033035532645),
        (np.array([3.75]), 65.153442205152444),
    ]
    for x, expected in f4_cases:
        assert cec2011_func(4, x) == pytest.approx(expected, rel=1e-12)

    degenerate = np.array([2.0, 2.0, np.pi / 2.0] + [0.0] * 27)
    assert cec2011_func(5, degenerate) == 0.0
    assert cec2011_func(6, degenerate) == 0.0

    q1 = np.array(
        [1.0, 1.0, np.pi / 4.0]
        + [
            -2.0,
            -2.0,
            -2.0,
            -2.125,
            -2.125,
            -2.125,
            -2.25,
            -2.25,
            -2.25,
            -2.375,
            -2.375,
            -2.375,
            -2.5,
            -2.5,
            -2.5,
            -2.625,
            -2.625,
            -2.625,
            -2.75,
            -2.75,
            -2.75,
            -2.875,
            -2.875,
            -2.875,
            -3.0,
            -3.0,
            -3.0,
        ]
    )
    assert cec2011_func(5, q1) == pytest.approx(21815.773883338115, rel=1e-12)
    assert cec2011_func(6, q1) == pytest.approx(13637.607037710848, rel=1e-12)


def test_cec2011_f2_f3_f10_match_reference_probe_values() -> None:
    """Guard the remaining CEC2011 C++ oracle mismatches found by review."""
    degenerate_atoms = np.array([2.0, 2.0, np.pi / 2.0] + [0.0] * 27)
    assert cec2011_func(2, degenerate_atoms) == 0.0

    f3_cases = [
        (np.array([0.75]), 1.7423862846074083e-05),
        (np.array([0.675]), 9.2569794790120125e-05),
        (np.array([0.825]), 1.4363455069064565e-05),
    ]
    for x, expected in f3_cases:
        assert cec2011_func(3, x) == pytest.approx(expected, rel=1e-12, abs=1e-15)

    f10_cases = [
        (np.array([0.6] * 6 + [0.0] * 6), -7.5468782284276479),
        (np.array([0.4] * 6 + [-90.0] * 6), 19.899046307521022),
        (np.array([0.8] * 6 + [90.0] * 6), 19.899046305090852),
    ]
    for x, expected in f10_cases:
        assert cec2011_func(10, x) == pytest.approx(expected, rel=1e-12)


def test_cec2017_d10_zero_vector_matches_cpp_oracle_all_functions() -> None:
    """Guard CEC2017 evaluator parity against the C++ fixed-vector oracle."""
    x = np.zeros(10)
    expected_by_function = {
        1: 29975432515.940056,
        2: 8.8696454249692198e17,
        3: 1343217.0396465289,
        4: 5901.6564530861406,
        5: 726.71456129591127,
        6: 741.77549410442828,
        7: 939.71632391343246,
        8: 946.64548085259537,
        9: 4306.1324978942675,
        10: 6138.3086251591922,
        11: 65027134.706558108,
        12: 5721203472.4570827,
        13: 2841537129.1318893,
        14: 2215435591.9727898,
        15: 769548252.85083985,
        16: 3437.7629457022122,
        17: 3283.0084570298259,
        18: 14468752711.761957,
        19: 12289135494.984451,
        20: 3152.3424399956784,
        21: 2828.6145683142258,
        22: 5302.4980403395475,
        23: 4335.9298845337862,
        24: 3392.2088309135484,
        25: 4820.812334105729,
        26: 5733.9190574778031,
        27: 5055.8926968404394,
        28: 4517.3352849663461,
        29: 48958.529822646604,
        30: 506077323.003654,
    }

    for func_id, expected in expected_by_function.items():
        if func_id == 2:
            with pytest.warns(DeprecationWarning):
                got = cec2017_func(func_id, x)
        else:
            got = cec2017_func(func_id, x)
        assert got == pytest.approx(expected, rel=1e-11)


def test_cec2013_d10_probe_values_match_cpp_regression_guard() -> None:
    """Guard representative CEC2013 values against the C++ self-regression CSV."""
    x = np.zeros(10)

    assert cec2013_func(1, x) == pytest.approx(17398.270025643684, rel=1e-12)
    assert cec2013_func(8, x) == pytest.approx(-678.0156101056773, rel=1e-9, abs=1e-9)


def test_cec2020_composition_zero_vector_matches_cpp_oracle() -> None:
    """Guard CEC2020 staged-MEX composition mapping for public F08-F10."""
    expected_cases = {
        (8, 10): 5302.4980403395475,
        (8, 20): 9739.3336536045426,
        (9, 5): 3423.9485214939136,
        (9, 10): 3392.2088309135484,
        (9, 15): 5135.182087612073,
        (9, 20): 4573.621648579414,
        (10, 5): 3403.6472298252447,
        (10, 10): 4820.812334105729,
        (10, 15): 6183.311445592753,
        (10, 20): 11401.184382526544,
    }

    for (func_id, dim), expected in expected_cases.items():
        assert cec2020_func(func_id, np.zeros(dim)) == pytest.approx(expected, rel=1e-12)


def test_cec2013lsgo_native_dimensions_are_function_specific() -> None:
    f1 = make_problem("cec2013lsgo", 1)
    f13 = make_problem("cec2013lsgo", 13)

    assert f1.dim == 1000
    assert f13.dim == 905
    assert default_dimensions("cec2013lsgo") == "native"


def test_validation_rejects_bad_suite_function_dimension_and_budget() -> None:
    with pytest.raises(ValueError, match="Unsupported suite"):
        make_problem("cec2099", 1, 10)
    with pytest.raises(ValueError, match="function id"):
        make_problem("cec2017", 31, 10)
    with pytest.raises(ValueError, match="requires D"):
        make_problem("cec2020", 1, 30)
    # F1@D5 and F8@D15 were oracle-validated and RESTORED on 2026-07-26
    # (tests/regression/test_cec2020_restored_cells.py); they must construct and
    # evaluate finitely rather than raise.
    assert np.isfinite(float(make_problem("cec2020", 1, 5).evaluate(np.zeros((1, 5)))[0]))
    assert np.isfinite(float(np.asarray(cec2020_func(8, np.zeros(15))).ravel()[0]))
    # The PROTOCOL exclusion is unaffected: F6/F7 are undefined at D=5
    # (Yue et al. 2019 SS2.1) and stay refused.
    with pytest.raises(ValueError, match="not defined at D=5"):
        make_problem("cec2020", 6, 5)
    with pytest.raises(ValueError, match="native D"):
        make_problem("cec2011", 1, 10)
    with pytest.raises(ValueError, match="max_nfes_override"):
        make_problem("cec2017", 1, 10, max_nfes_override=-1)


def test_evaluate_rejects_bad_population_shape_empty_and_nonfinite() -> None:
    problem = make_problem("cec2017", 1, 10)

    with pytest.raises(ValueError, match="2D population"):
        problem.evaluate(np.zeros(10))
    with pytest.raises(ValueError, match="empty population"):
        problem.evaluate(np.zeros((0, 10)))
    with pytest.raises(ValueError, match="requires D=10"):
        problem.evaluate(np.zeros((1, 9)))
    bad = np.zeros((1, 10))
    bad[0, 0] = np.nan
    with pytest.raises(ValueError, match="non-finite"):
        problem.evaluate(bad)


def test_cec2017_strict_fp_mode_evaluates_sensitive_function() -> None:
    problem = make_problem("cec2017", 1, 10, benchmark_fp_mode="strict")
    values = problem.evaluate(np.zeros((2, 10)))

    assert values.shape == (2,)
    assert np.all(np.isfinite(values))
    assert "Strict fixed-order" in problem.notes


def test_benchmark_fp_mode_rejects_unknown_value() -> None:
    with pytest.raises(ValueError, match="benchmark_fp_mode"):
        make_problem("cec2017", 1, 10, benchmark_fp_mode="wild")


def test_bounds_are_expected_shape_and_mutable_for_all_primary_cases() -> None:
    cases = [
        ("cec2011", 1, None),
        ("cec2013", 1, 10),
        ("cec2013lsgo", 13, None),
        ("cec2017", 1, 10),
        ("cec2020", 2, 5),
    ]
    for suite, func_id, dim in cases:
        problem = make_problem(suite, func_id, dim)
        assert problem.lb.shape == (problem.dim,)
        assert problem.ub.shape == (problem.dim,)
        assert np.all(problem.lb <= problem.ub)
        problem.lb[0] = problem.lb[0]
