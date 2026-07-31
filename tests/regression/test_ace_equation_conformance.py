"""C-006 conformance: the printed ACE update (main-text Eq. 7) IS the frozen operator.

The reference below is transcribed from the *paper*, not from the implementation:

    d_m = sum_{i: s_i = m} ( f(x_i) - f(v_i) ),      S = sum_m d_m

    tau = d / S                                        if S > 0
        = (max(d_m,0))_m / sum_m' max(d_m',0)          if S < 0 and max_m d_m > 0
        = undefined                                    otherwise

    pi <- P( (1-c) pi + c P(tau) )   if tau defined,  else  P(pi)

    P(z) = argmin_{y_m >= pi_min, sum y = 1} || y - z ||_2

The code works in the opposite sign convention (omega_m = -d_m, s = -S), so the
test negates before calling it. Both the NumPy path and the Numba fast path are
checked, over every branch the operator can take.
"""
from __future__ import annotations

import math

import numpy as np
import pytest

from gsk_family.optimizers import _dt_core


# --------------------------------------------------------------------------- #
# Reference implementation, written from the printed equation only.
# --------------------------------------------------------------------------- #
def _project_reference(z: np.ndarray, pi_min: float) -> np.ndarray:
    """Euclidean projection onto {y : y_m >= pi_min, sum_m y_m = 1}."""
    z = np.asarray(z, dtype=np.float64).reshape(-1)
    n = z.size
    if pi_min * n >= 1.0:                       # floor consumes the simplex
        return np.full(n, 1.0 / n)
    # Shift by the floor and project onto the scaled simplex {a >= 0, sum a = s}.
    s = 1.0 - pi_min * n
    a = z - pi_min
    u = np.sort(a)[::-1]
    cssv = np.cumsum(u) - s
    idx = np.arange(1, n + 1)
    cond = u - cssv / idx > 0
    rho = int(np.nonzero(cond)[0][-1])
    theta = cssv[rho] / float(rho + 1)
    return np.maximum(a - theta, 0.0) + pi_min


def ace_update_reference(pi, d, *, c, pi_min):
    """Main-text Eq. (7), evaluated exactly as printed."""
    pi = np.asarray(pi, dtype=np.float64)
    d = np.asarray(d, dtype=np.float64)
    S = float(np.sum(d))

    tau = None
    if math.isfinite(S):
        if S > 0.0:
            tau = d / S
        elif S < 0.0 and float(np.max(d)) > 0.0:
            pos = np.maximum(d, 0.0)
            denom = float(np.sum(pos))
            if denom > 0.0 and math.isfinite(denom):
                tau = pos / denom

    if tau is None:
        return _project_reference(pi, pi_min)
    return _project_reference((1.0 - c) * pi + c * _project_reference(tau, pi_min), pi_min)


# --------------------------------------------------------------------------- #
# Branch coverage. `d` is the PAPER quantity; the code receives omega = -d.
# --------------------------------------------------------------------------- #
C = 0.10
PI_MIN = 0.05

CASES = {
    # S > 0  -> net improvement, full arm pool
    "net_improving_all": np.array([3.0, 1.0, 2.0, 0.5, 1.5]),
    "net_improving_mixed": np.array([5.0, -1.0, 2.0, -0.5, 0.25]),
    # S < 0 with at least one improving arm -> improved-subset credit
    "net_worsening_some_improved": np.array([1.0, -4.0, -3.0, 0.5, -2.0]),
    "net_worsening_one_improved": np.array([-2.0, -3.0, 0.25, -1.0, -4.0]),
    # S < 0, no arm improved -> hold
    "all_worsening": np.array([-1.0, -2.0, -3.0, -0.5, -1.5]),
    # S == 0 exactly -> hold (checked BEFORE the subset branch in the operator)
    "sum_exactly_zero": np.array([2.0, -2.0, 1.0, -1.0, 0.0]),
    "all_zero": np.zeros(5),
    # non-finite -> hold
    "non_finite": np.array([np.inf, 1.0, -1.0, 0.0, 2.0]),
    "nan_present": np.array([np.nan, 1.0, -1.0, 0.0, 2.0]),
}

PI_STARTS = {
    "frozen_init": np.array([0.05, 0.05, 0.45, 0.05, 0.40]),
    "uniform": np.full(5, 0.2),
    "at_floor": np.array([0.05, 0.05, 0.05, 0.05, 0.80]),
}


@pytest.mark.parametrize("case", sorted(CASES))
@pytest.mark.parametrize("start", sorted(PI_STARTS))
def test_printed_equation_matches_frozen_operator(case, start):
    """Eq. (7) reproduces _ace_update_probs on every branch."""
    d = CASES[case]
    pi = PI_STARTS[start]
    got = _dt_core._ace_update_probs(pi, -d, c=C, p_min=PI_MIN)
    want = ace_update_reference(pi, d, c=C, pi_min=PI_MIN)
    np.testing.assert_allclose(got, want, rtol=0, atol=1e-12,
                               err_msg=f"Eq.(7) diverges from the operator: {case}/{start}")


@pytest.mark.parametrize("case", sorted(CASES))
def test_single_arm_pool(case):
    """A one-arm pool degenerates to the constant vector under any branch."""
    d = CASES[case][:1]
    pi = np.array([1.0])
    got = _dt_core._ace_update_probs(pi, -d, c=C, p_min=PI_MIN)
    want = ace_update_reference(pi, d, c=C, pi_min=PI_MIN)
    np.testing.assert_allclose(got, want, rtol=0, atol=1e-12)


@pytest.mark.parametrize("case", sorted(CASES))
def test_numba_fast_path_agrees(case):
    """The Numba fast path must equal the NumPy path bit-for-bit in behaviour."""
    fast = getattr(_dt_core, "ace_update_full_fast", None)
    if fast is None:
        pytest.skip("Numba ACE kernel not available in this environment")
    d = CASES[case]
    pi = PI_STARTS["frozen_init"]
    got_fast = np.asarray(fast(pi.copy(), (-d).copy(), float(C), float(PI_MIN)))
    want = ace_update_reference(pi, d, c=C, pi_min=PI_MIN)
    np.testing.assert_allclose(got_fast, want, rtol=0, atol=1e-12,
                               err_msg=f"Numba ACE path diverges from Eq.(7): {case}")


@pytest.mark.parametrize("case", sorted(CASES))
@pytest.mark.parametrize("start", sorted(PI_STARTS))
def test_output_is_a_floored_probability_vector(case, start):
    """Whatever branch is taken, the result stays on the floored simplex."""
    out = _dt_core._ace_update_probs(PI_STARTS[start], -CASES[case], c=C, p_min=PI_MIN)
    assert np.all(out >= PI_MIN - 1e-12), "floor violated"
    assert math.isclose(float(np.sum(out)), 1.0, rel_tol=0, abs_tol=1e-10)


def test_hold_branches_do_not_move_an_already_valid_vector():
    """S == 0, no improving arm, and non-finite S all leave a valid pi in place."""
    pi = PI_STARTS["frozen_init"]
    for case in ("sum_exactly_zero", "all_zero", "all_worsening", "non_finite", "nan_present"):
        out = _dt_core._ace_update_probs(pi, -CASES[case], c=C, p_min=PI_MIN)
        np.testing.assert_allclose(out, pi, rtol=0, atol=1e-12,
                                   err_msg=f"{case} should hold pi, not move it")


def test_projection_is_the_euclidean_projection():
    """P(z) is the nearest floored-simplex point, not a floor-and-renormalize."""
    z = np.array([0.9, 0.02, 0.02, 0.03, 0.03])
    proj = _project_reference(z, PI_MIN)

    # The equation's P and the frozen helper are the same map.
    np.testing.assert_allclose(_dt_core._ace_project_probs(z, p_min=PI_MIN), proj,
                               rtol=0, atol=1e-12)

    # It is feasible: on the simplex and at or above the floor.
    assert np.all(proj >= PI_MIN - 1e-12)
    assert math.isclose(float(proj.sum()), 1.0, rel_tol=0, abs_tol=1e-12)

    # Floor-and-renormalize is a DIFFERENT map: renormalizing after flooring
    # pushes entries back under the floor, so it is not even feasible here.
    naive = np.maximum(z, PI_MIN)
    naive = naive / naive.sum()
    assert float(np.min(naive)) < PI_MIN - 1e-9, "naive variant should break the floor"
    assert not np.allclose(naive, proj)

    # Optimality: no feasible point is closer to z than the projection.
    rng = np.random.default_rng(0)
    for _ in range(400):
        y = _project_reference(proj + rng.normal(scale=0.05, size=proj.size), PI_MIN)
        assert np.linalg.norm(proj - z) <= np.linalg.norm(y - z) + 1e-12
