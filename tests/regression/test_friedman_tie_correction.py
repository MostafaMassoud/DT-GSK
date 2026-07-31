"""M-026: the Friedman statistic is tie-corrected, and the correction is inert
where it should be.

Why this matters here specifically: the 1e-8 success floor maps many distinct
solver outcomes onto exactly 0.0, so exact ties are common rather than
pathological.  Midranks alone do not fix this -- tied rows shrink the rank
variance, biasing chi2 downwards and making the uncorrected test conservative.

The correction divides by

    C = 1 - sum_i sum_g (t_ig^3 - t_ig) / ( N (k^3 - k) )

Two guarantees follow from C <= 1 and are asserted below, because they are what
license the claim that no published conclusion can change direction:

  * the corrected statistic is >= the uncorrected one, so the correction can
    only ever *increase* significance; and
  * average ranks are computed before the correction and are untouched by it,
    so no ranking can move as a result of applying it.

``scipy.stats.friedmanchisquare`` applies the same correction and is used as an
independent oracle -- the implementation here is checked against it rather than
against a restatement of its own formula.
"""
from __future__ import annotations

import numpy as np
import pytest

from gsk_family.analysis.statistics import friedman_rank

sps = pytest.importorskip("scipy.stats", reason="scipy is the independent oracle")


# --------------------------------------------------------------------------- #
# helpers
# --------------------------------------------------------------------------- #
def as_data(matrix: np.ndarray) -> dict[str, list[float]]:
    """[n_problems, k] matrix -> the {algorithm: per-problem values} form."""
    return {f"alg{j}": list(matrix[:, j]) for j in range(matrix.shape[1])}


def floored(matrix: np.ndarray, floor_frac: float, rng) -> np.ndarray:
    """Emulate the 1e-8 success floor: a fraction of entries collapse to 0.0."""
    mask = rng.random(matrix.shape) < floor_frac
    out = matrix.copy()
    out[mask] = 0.0
    return out


# --------------------------------------------------------------------------- #
# 1. inertness: no ties => the correction must be exactly the identity
# --------------------------------------------------------------------------- #
def test_no_ties_correction_is_exactly_identity():
    rng = np.random.default_rng(11)
    m = rng.random((15, 5))          # continuous draws: ties have measure zero
    r = friedman_rank(as_data(m))

    assert r.n_tied_problems == 0
    assert r.tie_correction == 1.0                      # exact, not approximate
    assert r.statistic_tie_corrected == r.statistic     # bit-for-bit
    assert r.p_value_tie_corrected == r.p_value


# --------------------------------------------------------------------------- #
# 2. the correction fires when ties are present, in the right direction
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("floor_frac", [0.15, 0.35, 0.60])
def test_ties_increase_the_statistic_and_never_decrease_significance(floor_frac):
    rng = np.random.default_rng(23)
    m = floored(rng.random((29, 7)), floor_frac, rng)   # 29 functions x 7 algs
    r = friedman_rank(as_data(m))

    assert r.n_tied_problems > 0
    assert 0.0 < r.tie_correction < 1.0
    assert r.statistic_tie_corrected > r.statistic
    # C <= 1 => chi2/C >= chi2 => the p-value can only shrink.
    assert r.p_value_tie_corrected <= r.p_value


# --------------------------------------------------------------------------- #
# 3. independent oracle: agreement with scipy across tie regimes
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("seed", range(12))
@pytest.mark.parametrize("floor_frac", [0.0, 0.25, 0.5])
def test_matches_scipy_friedmanchisquare(seed, floor_frac):
    rng = np.random.default_rng(1000 + seed)
    m = rng.random((20, 4))
    if floor_frac:
        m = floored(m, floor_frac, rng)

    r = friedman_rank(as_data(m))
    ref = sps.friedmanchisquare(*[m[:, j] for j in range(m.shape[1])])

    assert r.statistic_tie_corrected == pytest.approx(ref.statistic, rel=1e-12)
    assert r.p_value_tie_corrected == pytest.approx(ref.pvalue, rel=1e-9)


# --------------------------------------------------------------------------- #
# 4. the guarantee that makes the correction safe to adopt post-hoc
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("seed", range(6))
def test_average_ranks_are_invariant_under_the_correction(seed):
    """No ranking can move because the correction rescales the statistic only."""
    rng = np.random.default_rng(500 + seed)
    m = floored(rng.random((29, 7)), 0.4, rng)
    data = as_data(m)

    r = friedman_rank(data)

    # ranks recomputed from the same midrank convention, independent of chi2
    expected = np.vstack([sps.rankdata(row, method="average") for row in m])
    for j, name in enumerate(data):
        assert r.avg_ranks[name] == pytest.approx(float(expected[:, j].mean()),
                                                  rel=1e-12)
    # and the correction factor plays no part in producing them
    assert r.tie_correction < 1.0


# --------------------------------------------------------------------------- #
# 5. backward compatibility: the uncorrected fields are unchanged
# --------------------------------------------------------------------------- #
def test_uncorrected_fields_retain_the_historical_formula():
    """Published results must keep reproducing from `statistic`/`p_value`."""
    rng = np.random.default_rng(97)
    m = floored(rng.random((29, 7)), 0.3, rng)
    r = friedman_rank(as_data(m))

    n, k = m.shape
    ranks = np.vstack([sps.rankdata(row, method="average") for row in m])
    avg = ranks.mean(axis=0)
    chi2_plain = (12.0 * n / (k * (k + 1))) * np.sum((avg - (k + 1) / 2.0) ** 2)

    assert r.statistic == pytest.approx(float(chi2_plain), rel=1e-12)
    assert r.statistic != r.statistic_tie_corrected      # correction did apply


# --------------------------------------------------------------------------- #
# 6. degenerate input: honest nan rather than inf or a crash
# --------------------------------------------------------------------------- #
def test_fully_tied_matrix_yields_nan_not_infinity():
    """Every row fully tied => C == 0 => the statistic is undefined, not huge."""
    m = np.ones((10, 4))
    r = friedman_rank(as_data(m))

    assert r.tie_correction == 0.0
    assert np.isnan(r.statistic_tie_corrected)
    assert np.isnan(r.p_value_tie_corrected)
    assert r.statistic == pytest.approx(0.0, abs=1e-12)  # uncorrected is well defined


def test_single_tie_group_correction_matches_closed_form():
    """C is checked against a hand-computed value, not the implementation."""
    # 3 problems, k=4. Exactly one problem has a single tie group of size 2.
    m = np.array([
        [1.0, 2.0, 3.0, 4.0],
        [1.0, 1.0, 3.0, 4.0],   # one tie group, t=2 -> t^3 - t = 6
        [4.0, 3.0, 2.0, 1.0],
    ])
    n, k = m.shape
    expected_c = 1.0 - 6.0 / (n * (k ** 3 - k))          # 1 - 6/(3*60) = 0.9666...

    r = friedman_rank(as_data(m))

    assert r.n_tied_problems == 1
    assert r.tie_correction == pytest.approx(expected_c, rel=1e-15)
    assert r.statistic_tie_corrected == pytest.approx(r.statistic / expected_c,
                                                      rel=1e-15)
