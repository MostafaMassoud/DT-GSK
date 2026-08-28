"""The canonical near-zero rule for across-function Wilcoxon tests.

Pre-registration Amendment A5 (2026-08-28): the manuscript states one tie rule
- differences with |d| < 1e-8 are discarded before ranking - and the primary
pipeline applies it, but the round-one revision analyzer passed exact zeros
only. ``wilcoxon_paired`` now takes ``zero_tol`` so both pipelines follow the
stated rule from one place. These tests pin the policy so it cannot silently
drift in either direction again.
"""
from __future__ import annotations

import numpy as np

from gsk_family.analysis.statistics import wilcoxon_paired


def test_default_keeps_exact_zero_behavior():
    """zero_tol=0 must reproduce the historical convention byte-for-byte:
    a sub-band difference is a nonzero difference and stays in the ranking."""
    x = np.array([1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0])
    y = x + np.array([5e-9] + [1.0] * 9)  # one sub-band pair, nine real ones
    res = wilcoxon_paired(x, y)
    assert res.n_pairs == 10


def test_band_excludes_sub_tolerance_pair():
    """Under the stated rule the 5e-9 pair is a tie and leaves the ranking."""
    x = np.array([1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0])
    y = x + np.array([5e-9] + [1.0] * 9)
    res = wilcoxon_paired(x, y, zero_tol=1e-8)
    assert res.n_pairs == 9


def test_band_keeps_large_magnitude_pair():
    """The band is absolute, not relative: a large-magnitude pair whose
    difference exceeds 1e-8 must never be swallowed by scale."""
    x = np.array([1e9, 2e9, 3e9, 4e9, 5e9, 6e9, 7e9, 8e9, 9e9, 1e10])
    y = x + 1.0
    res = wilcoxon_paired(x, y, zero_tol=1e-8)
    assert res.n_pairs == 10


def test_band_changes_only_membership_not_ranking():
    """With no sub-band pairs the two conventions must agree exactly."""
    rng = np.random.default_rng(20240620)
    x = rng.normal(size=29)
    y = x + rng.normal(loc=0.5, size=29)
    a = wilcoxon_paired(x, y)
    b = wilcoxon_paired(x, y, zero_tol=1e-8)
    assert a.n_pairs == b.n_pairs
    assert a.p_value == b.p_value


def test_all_pairs_inside_band_degenerates_to_p_one():
    """Every difference inside the band: the registered degenerate convention
    is n = 0 and p = 1, matching the released cross-check record."""
    x = np.zeros(12)
    y = x + 1e-9
    res = wilcoxon_paired(x, y, zero_tol=1e-8)
    assert res.n_pairs == 0
    assert res.p_value == 1.0
