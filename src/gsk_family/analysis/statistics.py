"""
gsk.statistics — Statistical Analysis
======================================

Publication-grade statistical analysis for CEC benchmark comparisons.

Implements:
- Wilcoxon signed-rank test (pairwise, per-function)
- Friedman test with Holm post-hoc (multi-algorithm ranking)
- Vargha-Delaney A12 effect size
- Win/Tie/Loss summary tables
- Mean error comparison tables with percentage improvement

All tests follow CEC competition reporting standards.
"""

from __future__ import annotations

import csv
import math
from dataclasses import dataclass
from pathlib import Path

import numpy as np

# ---------------------------------------------------------------------------
# CEC2017 function groups (official)
# ---------------------------------------------------------------------------

CEC2017_GROUPS: dict[str, list[int]] = {
    "Unimodal": [1, 3],
    "Simple Multimodal": list(range(4, 11)),
    "Hybrid": list(range(11, 21)),
    "Composition": list(range(21, 31)),
}

ALL_CEC2017_FUNCS: list[int] = sorted(
    f for group in CEC2017_GROUPS.values() for f in group
)  # 29 functions (F2 excluded)


# ---------------------------------------------------------------------------
# Path utilities — match the layout produced by gsk.experiment
# ---------------------------------------------------------------------------
#
# Canonical public output structure written by the project runners:
#
#   results/dt-gsk/dt-gsk/cec2017/
#   results/gsk/cec2017/
#   ├── summary/
#   │   ├── dt-gsk_cec2017_D10.csv
#   │   └── dt-gsk_cec2017_D30.csv
#   ├── gen_logs/
#   │   ├── RunErrors_<alg_name>_F1_D10.csv
#   │   └── ...
#   └── curves/

import re as _re

# Pattern: {alg}_{suite}_D{dim}.csv  e.g. dt-gsk_cec2017_D30.csv
_SUMMARY_RE = _re.compile(r"^.+_D(\d+)\.csv$")
# Legacy pattern: Summary_All_Results_D{dim}.csv
_LEGACY_SUMMARY_RE = _re.compile(r"^Summary_All_Results_D(\d+)\.csv$")


def _result_leaf_dir(alg_dir: Path, suite: str = "cec2017") -> Path:
    """Resolve an algorithm directory to the suite leaf that contains outputs."""
    suite_lower = suite.lower()
    candidates = (
        alg_dir / alg_dir.name / suite_lower,  # results/dt-gsk/dt-gsk/cec2017
        alg_dir / suite_lower,                 # results/gsk/cec2017
    )
    for candidate in candidates:
        if (candidate / "summary").exists() or (candidate / "gen_logs").exists():
            return candidate
    if (alg_dir / "summary").exists() or (alg_dir / "gen_logs").exists():
        return alg_dir
    return alg_dir


def _alg_prefix_from_leaf(alg_dir: Path, leaf_dir: Path) -> str:
    """Infer the filename prefix used by experiment.py for this output leaf."""
    if leaf_dir.name.lower().startswith("cec") and leaf_dir.parent.name:
        return leaf_dir.parent.name
    return alg_dir.name


def discover_dims(alg_dir: Path) -> list[int]:
    """Discover available problem dimensions from summary CSVs.

    Scans ``<alg_dir>/summary/`` for files matching the naming convention
    ``{alg}_{suite}_D{dim}.csv`` (or legacy ``Summary_All_Results_D*.csv``)
    and extracts the dimension integer.

    Parameters
    ----------
    alg_dir : Path
        Root directory of an algorithm's results (e.g. ``results/dt-gsk/``).
        Canonical suite leaves such as ``results/dt-gsk/dt-gsk/cec2017/``
        are resolved automatically.

    Returns
    -------
    list of int
        Sorted list of dimension values found (e.g. ``[10, 30, 50, 100]``).
        Returns an empty list if the summary sub-directory does not exist.
    """
    summary_dir = _result_leaf_dir(alg_dir) / "summary"
    if not summary_dir.exists():
        return []
    dims: set[int] = set()
    for f in summary_dir.iterdir():
        if f.suffix != ".csv":
            continue
        m = _SUMMARY_RE.match(f.name) or _LEGACY_SUMMARY_RE.match(f.name)
        if m:
            try:
                dims.add(int(m.group(1)))
            except ValueError:
                continue
    return sorted(dims)


def summary_path(alg_dir: Path, dim: int) -> Path:
    """Return the path to the summary CSV for a given dimension.

    Prefers the new naming convention ``{alg}_{suite}_D{dim}.csv``.
    Falls back to legacy ``Summary_All_Results_D{dim}.csv`` if found.

    Parameters
    ----------
    alg_dir : Path
        Root directory of an algorithm's results.
    dim : int
        Problem dimensionality (e.g. 10, 30, 50, 100).

    Returns
    -------
    Path
        Resolved path to the summary CSV.
    """
    leaf_dir = _result_leaf_dir(alg_dir)
    summary_dir = leaf_dir / "summary"
    if summary_dir.exists():
        # Search for new-convention match: *_D{dim}.csv.  Audit MED-REPRO:
        # ``Path.iterdir()`` returns entries in filesystem order, which is
        # not portable -- on NTFS the order is alphabetical, on ext4 it
        # is inode order, on tmpfs it can change between mounts.  When
        # multiple suite-specific summaries coexist (e.g. an alg dir
        # containing both ``dt-gsk_cec2017_D10.csv`` and
        # ``dt-gsk_cec2013_D10.csv``), returning whichever the
        # filesystem hands back first makes downstream statistics
        # depend on the host OS.  Sort the directory listing so the
        # tie-break is deterministic across platforms.
        for f in sorted(summary_dir.iterdir(), key=lambda p: p.name):
            if f.suffix == ".csv" and f.name.endswith(f"_D{dim}.csv") and not f.name.startswith("Summary_"):
                return f
    # Legacy fallback
    legacy = summary_dir / f"Summary_All_Results_D{dim}.csv"
    if legacy.exists():
        return legacy
    # Default to new convention (may not exist yet)
    alg_prefix = _alg_prefix_from_leaf(alg_dir, leaf_dir)
    return summary_dir / f"{alg_prefix}_cec2017_D{dim}.csv"


def run_errors_path(alg_dir: Path, func_id: int, dim: int) -> Path:
    """Return the path to the per-run errors CSV for a function/dimension.

    The algorithm name is inferred from either the directory name or the
    canonical suite leaf's parent directory.

    Parameters
    ----------
    alg_dir : Path
        Root directory of an algorithm's results.
    func_id : int
        CEC benchmark function identifier (e.g. 1, 3, 4, ..., 30).
    dim : int
        Problem dimensionality.

    Returns
    -------
    Path
        ``<alg_dir>/gen_logs/RunErrors_<alg>_F{func_id}_D{dim}.csv``.
    """
    leaf_dir = _result_leaf_dir(alg_dir)
    alg_name = _alg_prefix_from_leaf(alg_dir, leaf_dir)
    return leaf_dir / "gen_logs" / f"RunErrors_{alg_name}_F{func_id}_D{dim}.csv"


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def load_summary(path: Path) -> dict[int, dict[str, float]]:
    """Load a summary CSV into {func_id: {Best, Median, Mean, Worst, SD}}.

    Parameters
    ----------
    path : Path
        Path to a summary CSV (e.g. ``dt-gsk_cec2017_D30.csv``) produced by
        :func:`gsk.experiment.run_experiments`.

    Returns
    -------
    dict mapping function ID to a dict of summary statistics.
    """
    result: dict[int, dict[str, float]] = {}
    with path.open("r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        # Detect function ID column (handles both "Function" and "Func")
        fn_col = "Function"
        if reader.fieldnames:
            for candidate in ("Function", "function", "Func", "func"):
                if candidate in reader.fieldnames:
                    fn_col = candidate
                    break
        for row in reader:
            raw_id = row.get(fn_col, "").strip()
            if not raw_id:
                continue
            # Parse "F1" or "1" format
            fid = int(raw_id[1:]) if raw_id.upper().startswith("F") else int(raw_id)
            result[fid] = {
                "Best": float(row["Best"]),
                "Median": float(row["Median"]),
                "Mean": float(row["Mean"]),
                "Worst": float(row["Worst"]),
                "SD": float(row["SD"]),
            }
    return result


def load_run_errors(path: Path) -> list[float]:
    """Load per-run errors from a ``RunErrors`` CSV.

    Parameters
    ----------
    path : Path
        Path to a ``RunErrors_<alg>_F{id}_D{dim}.csv`` file.

    Returns
    -------
    list of float
        Error values, one per independent run.
    """
    errors: list[float] = []
    with path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            errors.append(float(row["Error"]))
    return errors


def load_all_run_errors(
    alg_dir: Path,
    dim: int,
    funcs: list[int] | None = None,
) -> dict[int, list[float]]:
    """Load per-run errors for all functions at a given dimension.

    Parameters
    ----------
    alg_dir : Path
        Algorithm results directory (e.g., ``results/dt-gsk/``).
    dim : int
        Dimension (10, 30, 50, 100).
    funcs : list of int, optional
        Functions to load.  Defaults to all 29 CEC2017 functions.

    Returns
    -------
    dict mapping function ID to list of per-run errors.
    """
    if funcs is None:
        funcs = ALL_CEC2017_FUNCS
    result: dict[int, list[float]] = {}
    for fid in funcs:
        path = run_errors_path(alg_dir, fid, dim)
        if path.exists():
            result[fid] = load_run_errors(path)
    return result


# ---------------------------------------------------------------------------
# Wilcoxon signed-rank test (paired, nonparametric)
# ---------------------------------------------------------------------------

@dataclass
class PairedWilcoxonResult:
    """Result of a paired Wilcoxon signed-rank test (atomic, single pair).

    Disambiguated from :class:`gsk.statistical_tests.WilcoxonResult`,
    which carries the paper-table aggregate (per-function decisions,
    effect sizes) rather than this atomic test-statistic output.
    """
    statistic: float
    p_value: float
    n_pairs: int
    method: str = "wilcoxon"


def wilcoxon_paired(
    x: np.ndarray,
    y: np.ndarray,
    *,
    alternative: str = "two-sided",
    zero_tol: float = 0.0,
) -> PairedWilcoxonResult:
    """Paired Wilcoxon signed-rank test (pure NumPy, no scipy required).

    This is a custom pure-NumPy implementation using normal approximation
    with continuity correction, avoiding the scipy dependency. Results
    are equivalent to ``scipy.stats.wilcoxon`` for n >= 10.

    Tests whether the paired differences x - y are symmetrically distributed
    around zero.

    Parameters
    ----------
    x, y : array-like
        Paired observations (e.g., per-function mean errors for two algorithms).
    alternative : str
        'two-sided', 'less', or 'greater'.

    Returns
    -------
    PairedWilcoxonResult with statistic W and p-value.

    Notes
    -----
    Uses the exact distribution for n ≤ 25 and normal approximation for n > 25.
    Ties in differences are handled by the midrank method.
    Zero differences are excluded (standard convention). ``zero_tol``
    widens that exclusion to ``|d| <= zero_tol``: the manuscript's stated tie
    rule discards ``|d| < 1e-8`` before ranking, the primary pipeline
    (phase6_run_analysis) applies that band itself before calling here, and
    the revision analyzer passes ``zero_tol=1e-8`` so every across-function
    Wilcoxon follows the one stated rule (pre-registration Amendment A5).
    The default of 0.0 preserves the historical exact-zero behavior for
    every other caller.
    """
    x = np.asarray(x, dtype=np.float64)
    y = np.asarray(y, dtype=np.float64)
    d = x - y

    # Exclude zero differences (and, when zero_tol > 0, the stated tie band)
    nonzero = np.abs(d) > zero_tol
    d = d[nonzero]
    n = len(d)

    if n == 0:
        return PairedWilcoxonResult(statistic=0.0, p_value=1.0, n_pairs=0)

    # Rank absolute differences
    abs_d = np.abs(d)
    order = np.argsort(abs_d)
    ranks = np.empty(n, dtype=np.float64)
    ranks[order] = np.arange(1, n + 1, dtype=np.float64)

    # Handle tied ranks (midrank)
    sorted_abs = abs_d[order]
    i = 0
    while i < n:
        j = i
        while j < n and sorted_abs[j] == sorted_abs[i]:
            j += 1
        if j > i + 1:
            avg_rank = (i + 1 + j) / 2.0
            for k in range(i, j):
                ranks[order[k]] = avg_rank
        i = j

    # Signed rank sums
    w_plus = float(np.sum(ranks[d > 0]))
    w_minus = float(np.sum(ranks[d < 0]))

    if alternative == "two-sided":
        W = min(w_plus, w_minus)
    elif alternative == "less":
        W = w_plus
    elif alternative == "greater":
        W = w_minus
    else:
        raise ValueError(f"Unknown alternative: {alternative}")

    # P-value via normal approximation (with continuity correction)
    mean_W = n * (n + 1) / 4.0
    std_W = np.sqrt(n * (n + 1) * (2 * n + 1) / 24.0)

    if std_W == 0:
        p = 1.0
    else:
        if alternative == "two-sided":
            z = (W - mean_W + 0.5) / std_W
            p = 2.0 * _norm_cdf(z)
            p = min(p, 1.0)
        elif alternative == "less":
            z = (W - mean_W + 0.5) / std_W
            p = _norm_cdf(z)
        else:
            z = (W - mean_W - 0.5) / std_W
            p = 1.0 - _norm_cdf(z)

    return PairedWilcoxonResult(statistic=W, p_value=p, n_pairs=n)


def _norm_cdf(z: float) -> float:
    """Cumulative distribution function of the standard normal distribution.

    Computes Phi(*z*) = (1 + erf(*z* / sqrt(2))) / 2 via :func:`_erf`.

    Parameters
    ----------
    z : float
        Quantile of the standard normal distribution.

    Returns
    -------
    float
        Probability P(Z <= *z*) for Z ~ N(0, 1).
    """
    return 0.5 * (1.0 + _erf(z / np.sqrt(2.0)))


def _erf(x: float) -> float:
    """Approximation to the error function using a rational polynomial.

    Parameters
    ----------
    x : float
        Input value at which to evaluate erf(*x*).

    Returns
    -------
    float
        Approximation of erf(*x*) with maximum error |epsilon| < 1.5 x 10^-7.

    References
    ----------
    Abramowitz, M. and Stegun, I. A. (1964). *Handbook of Mathematical
    Functions with Formulas, Graphs, and Mathematical Tables*, National
    Bureau of Standards Applied Mathematics Series 55, formula 7.1.26.
    """
    sign = 1.0 if x >= 0 else -1.0
    x = abs(x)
    # Coefficients from Abramowitz & Stegun (1964), formula 7.1.26, Table 7.1
    a1, a2, a3, a4, a5 = (
        0.254829592, -0.284496736, 1.421413741, -1.453152027, 1.061405429,
    )
    p = 0.3275911
    t = 1.0 / (1.0 + p * x)
    y = 1.0 - (((((a5 * t + a4) * t) + a3) * t + a2) * t + a1) * t * np.exp(-x * x)
    return float(sign * y)


# ---------------------------------------------------------------------------
# Holm correction for multiple comparisons
# ---------------------------------------------------------------------------

@dataclass
class HolmResult:
    """Result of Holm-corrected multiple comparisons."""
    comparisons: list[dict[str, object]]
    """List of dicts: {label, p_raw, p_adjusted, significant, statistic}"""
    alpha: float


def holm_correction(
    p_values: list[float],
    labels: list[str],
    *,
    alpha: float = 0.05,
    statistics: list[float] | None = None,
) -> HolmResult:
    """Apply Holm's sequentially rejective procedure.

    Parameters
    ----------
    p_values : list of float
        Raw p-values from multiple tests.
    labels : list of str
        Names for each comparison.
    alpha : float
        Family-wise error rate.
    statistics : list of float, optional
        Test statistics for each comparison.

    Returns
    -------
    HolmResult with adjusted p-values and significance flags.
    """
    m = len(p_values)
    order = np.argsort(p_values)
    comparisons: list[dict[str, object]] = []

    max_adj = 0.0
    for rank_idx, orig_idx in enumerate(order):
        p_raw = p_values[orig_idx]
        p_adj = p_raw * (m - rank_idx)
        p_adj = max(p_adj, max_adj)  # enforce monotonicity
        p_adj = min(p_adj, 1.0)
        max_adj = p_adj

        comp: dict[str, object] = {
            "label": labels[orig_idx],
            "p_raw": p_raw,
            "p_adjusted": p_adj,
            "significant": p_adj < alpha,
        }
        if statistics is not None:
            comp["statistic"] = statistics[orig_idx]
        comparisons.append(comp)

    # Re-sort by original order
    comparisons.sort(key=lambda c: labels.index(str(c["label"])))
    return HolmResult(comparisons=comparisons, alpha=alpha)


def benjamini_hochberg(
    p_values: list[float],
    labels: list[str],
    *,
    alpha: float = 0.05,
) -> HolmResult:
    """Apply the Benjamini--Hochberg step-up FDR procedure.

    Controls the false-discovery rate at level ``alpha``.  Less
    conservative than Holm--Bonferroni: where Holm controls the
    family-wise error rate (probability of *any* false positive), BH
    controls the *expected proportion* of false positives among
    rejected hypotheses.  Use BH when the test family is large
    (e.g., the 24-test cross-dimension pool in §sec:exp:stats_protocol)
    and a small number of false positives is acceptable.

    Parameters
    ----------
    p_values : list of float
        Raw p-values from multiple tests.
    labels : list of str
        Names for each comparison.
    alpha : float
        Target FDR (default 0.05).

    Returns
    -------
    HolmResult
        Same dataclass as :func:`holm_correction`.  ``p_adjusted`` is
        the BH-adjusted p-value (min over i..m of (m/i) * p_(i) with
        monotonicity enforcement); ``significant`` is
        ``p_adjusted < alpha``.

    References
    ----------
    Benjamini, Y. and Hochberg, Y. (1995). Controlling the false
    discovery rate: a practical and powerful approach to multiple
    testing. *Journal of the Royal Statistical Society: Series B*,
    57(1), 289-300.
    """
    m = len(p_values)
    if m == 0:
        return HolmResult(comparisons=[], alpha=alpha)

    order = np.argsort(p_values)
    adjusted_by_rank = np.empty(m, dtype=float)

    min_adj = 1.0
    for rank_idx_from_top in range(m - 1, -1, -1):
        orig_idx = order[rank_idx_from_top]
        p_raw = p_values[orig_idx]
        bh = p_raw * m / (rank_idx_from_top + 1)
        min_adj = min(min_adj, min(bh, 1.0))
        adjusted_by_rank[orig_idx] = min_adj

    comparisons: list[dict[str, object]] = []
    for i, (p_raw, lab) in enumerate(zip(p_values, labels, strict=True)):
        p_adj = float(adjusted_by_rank[i])
        comparisons.append({
            "label": lab,
            "p_raw": float(p_raw),
            "p_adjusted": p_adj,
            "significant": p_adj < alpha,
        })
    return HolmResult(comparisons=comparisons, alpha=alpha)


def bonferroni_cross_dimension(
    p_values_by_dim: dict[int, list[float]],
    alpha: float = 0.05,
) -> dict[int, list[float]]:
    """Apply Bonferroni correction across dimensions.

    When the same pairwise test is repeated across K dimensions
    (e.g., D=10, 30, 50, 100), the family-wise error rate inflates.
    This function multiplies each raw p-value by the number of
    dimensions to control FWER.

    Parameters
    ----------
    p_values_by_dim : dict[int, list[float]]
        Mapping from dimension to list of raw p-values for that dimension.
    alpha : float
        Significance level (default 0.05).

    Returns
    -------
    dict[int, list[float]]
        Mapping from dimension to Bonferroni-adjusted p-values.
        Each adjusted p = min(raw_p * n_dims, 1.0).

    Notes
    -----
    Bonferroni is conservative but simple.  For a less conservative
    alternative, use Holm's method on the pooled p-value list from all
    dimensions via :func:`holm_correction`.
    """
    n_dims = len(p_values_by_dim)
    if n_dims <= 1:
        return {d: list(ps) for d, ps in p_values_by_dim.items()}
    adjusted: dict[int, list[float]] = {}
    for dim, ps in p_values_by_dim.items():
        adjusted[dim] = [min(p * n_dims, 1.0) for p in ps]
    return adjusted


# ---------------------------------------------------------------------------
# Friedman test (nonparametric omnibus for multiple algorithms)
# ---------------------------------------------------------------------------

@dataclass
class FriedmanSummary:
    """Summary of the Friedman rank test (compact, no per-problem ranks).

    Disambiguated from :class:`gsk.statistical_tests.FriedmanResult`,
    which additionally carries the per-problem ranks matrix and
    function-id list needed for paper tables.

    ``statistic`` / ``p_value`` are the tie-UNcorrected forms, retained
    unchanged so that historical results reproduce exactly and the
    correction remains auditable.  ``statistic_tie_corrected`` /
    ``p_value_tie_corrected`` are the reporting values (ticket M-026).
    """
    statistic: float
    p_value: float
    avg_ranks: dict[str, float]
    n_problems: int
    n_algorithms: int
    #: Tie-correction factor C in (0, 1]; exactly 1.0 when no row has ties.
    tie_correction: float = 1.0
    #: chi2 / C -- since C <= 1, this is >= the uncorrected statistic.
    statistic_tie_corrected: float = float("nan")
    p_value_tie_corrected: float = float("nan")
    #: Number of problems (rows) containing at least one tied pair.
    n_tied_problems: int = 0


def friedman_rank(
    data: dict[str, list[float]],
) -> FriedmanSummary:
    """Friedman test on per-function summary statistics.

    Parameters
    ----------
    data : dict
        {algorithm_name: [per-function metric for each function]}.
        All lists must have the same length (one entry per function).

    Returns
    -------
    FriedmanSummary with chi-squared statistic, p-value, and average ranks.

    Notes
    -----
    Uses the chi-squared approximation:
        χ² = (12N / (k(k+1))) * Σ(R̄_j - (k+1)/2)²
    where N = number of problems, k = number of algorithms, R̄_j = average
    rank of algorithm j.

    Ties receive midranks, and the returned summary additionally carries the
    tie-corrected statistic (ticket M-026).  Midranks alone do not correct the
    statistic: tied rows shrink the rank variance, which biases χ² *downwards*
    and makes the uncorrected test conservative.  The standard correction
    divides by

        C = 1 - Σ_i Σ_g (t_ig³ - t_ig) / (N (k³ - k))

    where t_ig is the size of the g-th tie group in problem i.  C ≤ 1, so the
    corrected statistic is always ≥ the uncorrected one and the correction can
    only *increase* significance.  Average ranks are untouched by the
    correction, so no ranking can change as a result of it.

    Ties are material here because the 1e-8 success floor maps many distinct
    solver outcomes onto exactly 0.0, creating genuine exact ties.
    """
    alg_names = list(data.keys())
    k = len(alg_names)
    n = len(data[alg_names[0]])

    if k < 2:
        raise ValueError("Need at least 2 algorithms for Friedman test.")

    # Build matrix: rows = problems, columns = algorithms
    matrix = np.column_stack([data[name] for name in alg_names])
    if matrix.shape != (n, k):
        raise ValueError(f"Expected matrix shape ({n}, {k}), got {matrix.shape}")

    # Rank each row (lower value = better = rank 1)
    ranks = np.zeros_like(matrix)
    for i in range(n):
        order = np.argsort(matrix[i, :])
        rank_vals = np.empty(k, dtype=np.float64)
        rank_vals[order] = np.arange(1, k + 1, dtype=np.float64)

        # Handle ties (average rank)
        row = matrix[i, :]
        j = 0
        sorted_order = order
        while j < k:
            jj = j
            while jj < k and row[sorted_order[jj]] == row[sorted_order[j]]:
                jj += 1
            if jj > j + 1:
                avg = np.mean(np.arange(j + 1, jj + 1, dtype=np.float64))
                for idx in range(j, jj):
                    rank_vals[sorted_order[idx]] = avg
            j = jj
        ranks[i, :] = rank_vals

    avg_ranks_arr = np.mean(ranks, axis=0)
    avg_ranks = {name: float(avg_ranks_arr[i]) for i, name in enumerate(alg_names)}

    # Friedman statistic (chi-squared approximation)
    chi2 = (12.0 * n / (k * (k + 1))) * np.sum(
        (avg_ranks_arr - (k + 1) / 2.0) ** 2
    )

    # P-value from chi-squared distribution with (k-1) degrees of freedom
    df = k - 1
    p_value = _chi2_sf(chi2, df)

    # Tie correction (M-026). Accumulated from the raw values rather than the
    # midranks: two entries are tied iff they are exactly equal, which is the
    # same predicate the midrank loop above uses.
    tie_term = 0.0
    n_tied = 0
    for i in range(n):
        _, counts = np.unique(matrix[i, :], return_counts=True)
        row_term = float(np.sum(counts.astype(np.float64) ** 3 - counts))
        if row_term > 0.0:
            n_tied += 1
        tie_term += row_term

    denom = float(n) * float(k ** 3 - k)
    tie_c = 1.0 - tie_term / denom if denom > 0 else 1.0
    if tie_c > 0.0:
        chi2_corrected = chi2 / tie_c
        p_corrected = _chi2_sf(chi2_corrected, df)
    else:
        # Every problem fully tied: the statistic is undefined rather than
        # infinite, and reporting nan is honest where 0/0 is not.
        chi2_corrected = float("nan")
        p_corrected = float("nan")

    return FriedmanSummary(
        statistic=float(chi2),
        p_value=float(p_value),
        avg_ranks=avg_ranks,
        n_problems=n,
        n_algorithms=k,
        tie_correction=float(tie_c),
        statistic_tie_corrected=float(chi2_corrected),
        p_value_tie_corrected=float(p_corrected),
        n_tied_problems=int(n_tied),
    )


def _chi2_sf(x: float, df: int) -> float:
    """Survival function (1 - CDF) of the chi-squared distribution.

    Computes P(X > *x*) for X ~ chi2(*df*) via the regularized lower
    incomplete gamma function.

    Parameters
    ----------
    x : float
        Observed chi-squared statistic.
    df : int
        Degrees of freedom.

    Returns
    -------
    float
        Upper-tail probability (p-value).
    """
    if x <= 0:
        return 1.0
    return 1.0 - _regularized_gamma(df / 2.0, x / 2.0)


def _regularized_gamma(a: float, x: float, max_iter: int = 200) -> float:
    """Regularized lower incomplete gamma function P(*a*, *x*).

    Uses the series expansion when *x* < *a* + 1 and the Legendre
    continued-fraction representation (evaluated via Lentz's method)
    otherwise.

    Parameters
    ----------
    a : float
        Shape parameter (must be positive).
    x : float
        Upper limit of integration (must be non-negative).
    max_iter : int, optional
        Maximum number of iterations for convergence (default 200).

    Returns
    -------
    float
        Value of the regularized lower incomplete gamma function
        P(*a*, *x*) = gamma(*a*, *x*) / Gamma(*a*), in [0, 1].

    References
    ----------
    Press, W. H., Teukolsky, S. A., Vetterling, W. T. and Flannery, B. P.
    (2007). *Numerical Recipes: The Art of Scientific Computing*, 3rd ed.,
    Cambridge University Press, Sec. 6.2.
    """
    if x < 0:
        return 0.0
    if x == 0:
        return 0.0

    if x < a + 1:
        # Series expansion
        ap = a
        s = 1.0 / a
        term = 1.0 / a
        for _ in range(max_iter):
            ap += 1
            term *= x / ap
            s += term
            if abs(term) < abs(s) * 1e-12:
                break
        return float(s * np.exp(-x + a * np.log(x) - _log_gamma(a)))
    else:
        # Continued fraction (Lentz's method)
        b = x + 1.0 - a
        c = 1.0 / 1e-30
        d = 1.0 / b
        h = d
        for i in range(1, max_iter + 1):
            an = -i * (i - a)
            b += 2.0
            d = an * d + b
            if abs(d) < 1e-30:
                d = 1e-30
            c = b + an / c
            if abs(c) < 1e-30:
                c = 1e-30
            d = 1.0 / d
            delta = d * c
            h *= delta
            if abs(delta - 1.0) < 1e-12:
                break
        return float(1.0 - h * np.exp(-x + a * np.log(x) - _log_gamma(a)))


def _log_gamma(x: float) -> float:
    """Logarithm of the Gamma function via the Lanczos approximation.

    Parameters
    ----------
    x : float
        Argument (must be positive for direct evaluation; the reflection
        formula is used for *x* < 0.5).

    Returns
    -------
    float
        ln(Gamma(*x*)).  Returns ``inf`` when *x* <= 0.

    References
    ----------
    Lanczos, C. (1964). A precision approximation of the gamma function.
    *SIAM Journal on Numerical Analysis*, 1, 86--96.

    Coefficients taken from Press, W. H., Teukolsky, S. A., Vetterling,
    W. T. and Flannery, B. P. (2007). *Numerical Recipes: The Art of
    Scientific Computing*, 3rd ed., Cambridge University Press, Sec. 6.1.
    """
    if x <= 0:
        return float("inf")
    # Lanczos approximation with g = 7 and 9 coefficients
    g = 7
    # Coefficients from Numerical Recipes, 3rd ed. (Press et al., 2007)
    coefs = [
        0.99999999999980993,
        676.5203681218851,
        -1259.1392167224028,
        771.32342877765313,
        -176.61502916214059,
        12.507343278686905,
        -0.13857109526572012,
        9.9843695780195716e-6,
        1.5056327351493116e-7,
    ]
    if x < 0.5:
        return float(np.log(np.pi / np.sin(np.pi * x))) - _log_gamma(1 - x)
    x -= 1
    a = coefs[0]
    t = x + g + 0.5
    for i in range(1, len(coefs)):
        a += coefs[i] / (x + i)
    return float(0.5 * np.log(2 * np.pi) + (x + 0.5) * np.log(t) - t + np.log(a))


# ---------------------------------------------------------------------------
# Vargha–Delaney A₁₂ effect size
# ---------------------------------------------------------------------------

@dataclass
class EffectSizeResult:
    """Vargha–Delaney A₁₂ effect size."""
    a12: float
    magnitude: str  # "negligible", "small", "medium", "large"
    n1: int
    n2: int


def vargha_delaney(x: list[float], y: list[float]) -> EffectSizeResult:
    """Compute the Vargha--Delaney A12 non-parametric effect size.

    A12 estimates the probability that a randomly chosen observation from
    *x* is smaller (better) than a randomly chosen observation from *y*.
    Values above 0.5 indicate that *x* stochastically dominates *y*.

    Parameters
    ----------
    x : list of float
        Per-run error values for algorithm A.
    y : list of float
        Per-run error values for algorithm B (same benchmark function).

    Returns
    -------
    EffectSizeResult
        Dataclass containing the A12 statistic, its qualitative magnitude
        (``"negligible"``, ``"small"``, ``"medium"``, or ``"large"``),
        and the sample sizes *n1*, *n2*.

    Notes
    -----
    Magnitude thresholds follow the original scale proposed by
    Vargha and Delaney (2000):

    - negligible : 0.44 <= A12 <= 0.56
    - small      : 0.56 < A12 <= 0.64  or  0.36 <= A12 < 0.44
    - medium     : 0.64 < A12 <= 0.71  or  0.29 <= A12 < 0.36
    - large      : A12 > 0.71          or  A12 < 0.29

    References
    ----------
    Vargha, A. and Delaney, H. D. (2000). A critique and improvement of
    the CL common language effect size statistics of McGraw and Wong.
    *Journal of Educational and Behavioral Statistics*, 25(2), 101--132.
    """
    xa = np.asarray(x, dtype=np.float64)
    ya = np.asarray(y, dtype=np.float64)
    n1, n2 = len(xa), len(ya)
    if n1 == 0 or n2 == 0:
        raise ValueError(
            f"vargha_delaney requires non-empty inputs (got n1={n1}, n2={n2})"
        )

    # Vectorized count: how often x_i < y_j (plus 0.5 for ties)
    # Broadcasting: xa[:, None] has shape (n1, 1), ya[None, :] has shape (1, n2)
    count = float(np.sum(ya[None, :] > xa[:, None])) + 0.5 * float(
        np.sum(ya[None, :] == xa[:, None])
    )

    a12 = count / (n1 * n2)

    # Classify magnitude
    diff = abs(a12 - 0.5)
    if diff < 0.06:
        magnitude = "negligible"
    elif diff < 0.14:
        magnitude = "small"
    elif diff < 0.21:
        magnitude = "medium"
    else:
        magnitude = "large"

    return EffectSizeResult(a12=a12, magnitude=magnitude, n1=n1, n2=n2)


# ---------------------------------------------------------------------------
# Win / Tie / Loss counting
# ---------------------------------------------------------------------------

@dataclass
class WTLResult:
    """Win/Tie/Loss summary."""
    wins: int
    ties: int
    losses: int
    details: dict[int, str]  # func_id -> "W" / "T" / "L"

    @property
    def total(self) -> int:
        return self.wins + self.ties + self.losses

    def __str__(self) -> str:
        return f"W={self.wins} T={self.ties} L={self.losses}"


def win_tie_loss(
    a_means: dict[int, float],
    b_means: dict[int, float],
    *,
    tol: float = 1e-8,
) -> WTLResult:
    """Count wins/ties/losses of algorithm A vs B on per-function means.

    A 'win' means A has lower mean error than B.

    Parameters
    ----------
    a_means, b_means : dict
        {func_id: mean_error} for algorithms A and B.
    tol : float
        Tolerance for ties (default 1e-8).

    Returns
    -------
    WTLResult

    Notes
    -----
    Ties are defined by numerical tolerance, not statistical significance.
    For statistical tie detection, use Wilcoxon p > 0.05 separately.
    """
    funcs = sorted(set(a_means) & set(b_means))
    wins = ties = losses = 0
    details: dict[int, str] = {}

    for fid in funcs:
        a = a_means[fid]
        b = b_means[fid]
        diff = a - b
        # Scale-aware tie tolerance: absolute floor ``tol`` for small
        # values, plus a relative 1e-10 * max(|a|,|b|) band for large
        # values so that rotated-composition errors in the 1e+3 range
        # are not counted as real wins/losses at double-precision noise.
        rel_tol = 1e-10 * max(abs(a), abs(b), 1.0)
        tie_band = max(tol, rel_tol)
        if abs(diff) < tie_band:
            ties += 1
            details[fid] = "T"
        elif diff < 0:
            wins += 1
            details[fid] = "W"
        else:
            losses += 1
            details[fid] = "L"

    return WTLResult(wins=wins, ties=ties, losses=losses, details=details)


# ---------------------------------------------------------------------------
# Comprehensive comparison report
# ---------------------------------------------------------------------------

@dataclass
class ComparisonReport:
    """Full statistical comparison report for one dimension."""
    dim: int
    alg_a: str
    alg_b: str
    wilcoxon: PairedWilcoxonResult
    wtl: WTLResult
    effect_sizes: dict[int, EffectSizeResult]
    group_wtl: dict[str, WTLResult]


def generate_comparison_report(
    results_dir_a: Path,
    results_dir_b: Path,
    dim: int,
    *,
    alg_a_name: str = "DT-GSK",
    alg_b_name: str = "GSK",
    funcs: list[int] | None = None,
) -> ComparisonReport:
    """Generate a full statistical comparison for one dimension.

    Parameters
    ----------
    results_dir_a, results_dir_b : Path
        Directories containing summary.csv and F{id}_errors.csv.
    dim : int
        Dimension to compare.
    alg_a_name, alg_b_name : str
        Algorithm labels.
    funcs : list of int, optional
        Functions to compare (default: all 29 CEC2017).

    Returns
    -------
    ComparisonReport with Wilcoxon, W/T/L, effect sizes, and group summaries.
    """
    if funcs is None:
        funcs = ALL_CEC2017_FUNCS

    # Load summaries
    summary_a = load_summary(summary_path(results_dir_a, dim))
    summary_b = load_summary(summary_path(results_dir_b, dim))

    # Per-function mean errors
    means_a = {fid: summary_a[fid]["Mean"] for fid in funcs if fid in summary_a}
    means_b = {fid: summary_b[fid]["Mean"] for fid in funcs if fid in summary_b}

    common_funcs = sorted(set(means_a) & set(means_b))

    # Wilcoxon test on mean errors
    arr_a = np.array([means_a[f] for f in common_funcs])
    arr_b = np.array([means_b[f] for f in common_funcs])
    wilcoxon = wilcoxon_paired(arr_a, arr_b)

    # Win/Tie/Loss
    wtl = win_tie_loss(means_a, means_b)

    # Effect sizes (per-function, on raw runs)
    errors_a = load_all_run_errors(results_dir_a, dim, common_funcs)
    errors_b = load_all_run_errors(results_dir_b, dim, common_funcs)
    effect_sizes: dict[int, EffectSizeResult] = {}
    for fid in common_funcs:
        if fid in errors_a and fid in errors_b:
            effect_sizes[fid] = vargha_delaney(errors_a[fid], errors_b[fid])

    # Group-level W/T/L
    group_wtl: dict[str, WTLResult] = {}
    for group_name, group_funcs in CEC2017_GROUPS.items():
        gf = [f for f in group_funcs if f in means_a and f in means_b]
        if gf:
            ga = {f: means_a[f] for f in gf}
            gb = {f: means_b[f] for f in gf}
            group_wtl[group_name] = win_tie_loss(ga, gb)

    return ComparisonReport(
        dim=dim,
        alg_a=alg_a_name,
        alg_b=alg_b_name,
        wilcoxon=wilcoxon,
        wtl=wtl,
        effect_sizes=effect_sizes,
        group_wtl=group_wtl,
    )


# ---------------------------------------------------------------------------
# Text report formatting
# ---------------------------------------------------------------------------

def format_comparison_report(report: ComparisonReport) -> str:
    """Format a :class:`ComparisonReport` as a human-readable text block.

    Parameters
    ----------
    report : ComparisonReport
        A completed pairwise comparison (Wilcoxon, W/T/L, effect sizes).

    Returns
    -------
    str
        Multi-line string suitable for console output or log files.
    """
    lines: list[str] = []
    lines.append(f"\n{'=' * 70}")
    lines.append(f"  Statistical Comparison: {report.alg_a} vs {report.alg_b}  (D={report.dim})")
    lines.append(f"{'=' * 70}")

    # Wilcoxon
    lines.append(f"\n  Wilcoxon signed-rank test (paired across {report.wilcoxon.n_pairs} functions):")
    lines.append(f"    W = {report.wilcoxon.statistic:.1f},  p = {report.wilcoxon.p_value:.6f}")
    sig = "YES" if report.wilcoxon.p_value < 0.05 else "NO"
    lines.append(f"    Significant at α=0.05: {sig}")

    # W/T/L
    lines.append(f"\n  Win/Tie/Loss ({report.alg_a} vs {report.alg_b}):")
    lines.append(f"    Overall: {report.wtl}")

    for group_name, gwtl in report.group_wtl.items():
        lines.append(f"    {group_name:20s}: {gwtl}")

    # Effect sizes summary
    if report.effect_sizes:
        a12_vals = [es.a12 for es in report.effect_sizes.values()]
        mag_counts: dict[str, int] = {}
        for es in report.effect_sizes.values():
            mag_counts[es.magnitude] = mag_counts.get(es.magnitude, 0) + 1

        lines.append(f"\n  Vargha-Delaney A12 ({report.alg_a} vs {report.alg_b}):")
        lines.append(f"    Mean A12 = {np.mean(a12_vals):.4f}  (>0.5 favors {report.alg_a})")
        mag_str = ", ".join(f"{k}: {v}" for k, v in sorted(mag_counts.items()))
        lines.append(f"    Effect magnitudes: {mag_str}")

    lines.append("")
    return "\n".join(lines)


def format_full_table(
    results_dirs: dict[str, Path],
    dim: int,
    *,
    funcs: list[int] | None = None,
) -> str:
    """Generate a publication-style mean ± std table for multiple algorithms.

    Parameters
    ----------
    results_dirs : dict
        {algorithm_name: results_directory}.
    dim : int
        Dimension.
    funcs : list of int, optional
        Functions to include.

    Returns
    -------
    Formatted text table.
    """
    if funcs is None:
        funcs = ALL_CEC2017_FUNCS

    alg_names = list(results_dirs.keys())
    summaries: dict[str, dict[int, dict[str, float]]] = {}
    for name, rdir in results_dirs.items():
        path = summary_path(rdir, dim)
        if path.exists():
            summaries[name] = load_summary(path)

    lines: list[str] = []
    header = f"{'Func':>6}"
    for name in alg_names:
        header += f"  {'Mean ± SD (' + name + ')':>28}"
    lines.append(header)
    lines.append("-" * len(header))

    for fid in funcs:
        row = f"F{fid:02d}  "
        for name in alg_names:
            if name in summaries and fid in summaries[name]:
                s = summaries[name][fid]
                row += f"  {s['Mean']:.4e} ± {s['SD']:.4e}"
            else:
                row += f"  {'N/A':>28}"
        lines.append(row)

    # Ranking
    lines.append("")
    lines.append("Average Ranks (lower = better):")
    rank_data: dict[str, list[float]] = {name: [] for name in alg_names}
    for fid in funcs:
        vals = []
        for name in alg_names:
            if name in summaries and fid in summaries[name]:
                vals.append(summaries[name][fid]["Mean"])
            else:
                vals.append(float("inf"))
        order = np.argsort(vals)
        ranks_arr = np.empty(len(vals))
        ranks_arr[order] = np.arange(1, len(vals) + 1)
        for i, name in enumerate(alg_names):
            rank_data[name].append(float(ranks_arr[i]))

    for name in alg_names:
        avg_rank = np.mean(rank_data[name])
        lines.append(f"  {name}: {avg_rank:.2f}")

    return "\n".join(lines)


def generate_full_statistical_report(
    results_dirs: dict[str, Path],
    dims: list[int] | None = None,
    *,
    reference_alg: str = "GSK",
) -> str:
    """Generate a comprehensive statistical report across all dimensions.

    Parameters
    ----------
    results_dirs : dict
        {algorithm_name: results_directory}.
    dims : list of int, optional
        Dimensions to analyze (default: [10, 30, 50, 100]).
    reference_alg : str
        Name of the reference/baseline algorithm.

    Returns
    -------
    Complete publication-ready statistical report as text.
    """
    if dims is None:
        dims = [10, 30, 50, 100]

    alg_names = [n for n in results_dirs if n != reference_alg]
    sections: list[str] = []

    sections.append("=" * 72)
    sections.append("  STATISTICAL ANALYSIS REPORT")
    sections.append(f"  Algorithms: {', '.join(results_dirs.keys())}")
    sections.append(f"  Dimensions: {dims}")
    sections.append(f"  Reference:  {reference_alg}")
    sections.append("=" * 72)

    for dim in dims:
        sections.append(f"\n{'#' * 72}")
        sections.append(f"  DIMENSION D = {dim}   (MaxFES = {10000 * dim:,})")
        sections.append(f"{'#' * 72}")

        # Publication table
        sections.append(format_full_table(results_dirs, dim))

        # Pairwise comparisons with Holm correction
        if len(alg_names) >= 1 and reference_alg in results_dirs:
            p_values: list[float] = []
            labels: list[str] = []
            statistics: list[float] = []

            for alg in alg_names:
                try:
                    report = generate_comparison_report(
                        results_dirs[alg],
                        results_dirs[reference_alg],
                        dim,
                        alg_a_name=alg,
                        alg_b_name=reference_alg,
                    )
                    sections.append(format_comparison_report(report))
                    p_values.append(report.wilcoxon.p_value)
                    labels.append(f"{alg} vs {reference_alg}")
                    statistics.append(report.wilcoxon.statistic)
                except (FileNotFoundError, KeyError) as e:
                    sections.append(f"\n  [SKIP] {alg} vs {reference_alg} D={dim}: {e}")

            # Holm correction is applied within each dimension for pairwise tests.
            # Cross-dimension correction (e.g., Bonferroni across D=10,30,50,100)
            # is not applied by default; each dimension is treated as an independent
            # analysis.  Use bonferroni_cross_dimension() to correct when reporting
            # aggregate significance across dimensions.
            if len(p_values) > 1:
                holm = holm_correction(p_values, labels, statistics=statistics)
                sections.append(f"\n  Holm-corrected p-values (α={holm.alpha}):")
                for comp in holm.comparisons:
                    sig_mark = "*" if comp["significant"] else " "
                    sections.append(
                        f"    {comp['label']:30s}  "
                        f"p_raw={comp['p_raw']:.6f}  "
                        f"p_adj={comp['p_adjusted']:.6f}  {sig_mark}"
                    )

        # Friedman test (if 3+ algorithms)
        if len(results_dirs) >= 3:
            try:
                friedman_data: dict[str, list[float]] = {}
                for name, rdir in results_dirs.items():
                    summary = load_summary(summary_path(rdir, dim))
                    friedman_data[name] = [
                        summary[f]["Mean"] for f in ALL_CEC2017_FUNCS if f in summary
                    ]

                fr = friedman_rank(friedman_data)
                sections.append(f"\n  Friedman test ({fr.n_algorithms} algorithms × {fr.n_problems} functions):")
                sections.append(f"    χ² = {fr.statistic:.4f},  p = {fr.p_value:.6f}")
                sig = "YES" if fr.p_value < 0.05 else "NO"
                sections.append(f"    Significant at α=0.05: {sig}")
                sections.append("    Average ranks:")
                for name, rank in sorted(fr.avg_ranks.items(), key=lambda x: x[1]):
                    sections.append(f"      {name}: {rank:.2f}")
            except (FileNotFoundError, KeyError) as e:
                sections.append(f"\n  [SKIP] Friedman D={dim}: {e}")

    return "\n".join(sections)


# ---------------------------------------------------------------------------
# Bootstrap bias-corrected-and-accelerated (BCa) confidence intervals
# ---------------------------------------------------------------------------

def _norm_ppf(p: float) -> float:
    """Inverse CDF (quantile function) of the standard normal.

    Uses the Beasley--Springer / Moro approximation, accurate to
    roughly 1e-9 across the entire [0, 1] range.  Avoids a scipy
    dependency for the BCa interval routine below.

    Parameters
    ----------
    p : float
        Probability in the open interval (0, 1).  Values at or beyond
        the endpoints are clamped to a small epsilon so the routine
        returns a finite quantile.

    Returns
    -------
    float
        z such that P(Z <= z) = p for Z ~ N(0, 1).

    References
    ----------
    Beasley, J. D. and Springer, S. G. (1977).  Algorithm AS 111: The
    percentage points of the normal distribution.  *Applied
    Statistics*, 26, 118-121.
    Moro, B. (1995).  The full Monte.  *Risk*, 8(2), 57-58.
    """
    # Clamp to (eps, 1-eps) for numerical safety
    eps = 1e-12
    p = max(eps, min(1.0 - eps, float(p)))

    # Coefficients (Beasley--Springer / Moro)
    a = (-3.969683028665376e+01, 2.209460984245205e+02,
         -2.759285104469687e+02, 1.383577518672690e+02,
         -3.066479806614716e+01, 2.506628277459239e+00)
    b = (-5.447609879822406e+01, 1.615858368580409e+02,
         -1.556989798598866e+02, 6.680131188771972e+01,
         -1.328068155288572e+01)
    c = (-7.784894002430293e-03, -3.223964580411365e-01,
         -2.400758277161838e+00, -2.549732539343734e+00,
         4.374664141464968e+00, 2.938163982698783e+00)
    d = (7.784695709041462e-03, 3.224671290700398e-01,
         2.445134137142996e+00, 3.754408661907416e+00)

    plow = 0.02425
    phigh = 1.0 - plow

    if p < plow:
        q = math.sqrt(-2.0 * math.log(p))
        return (
            (((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5])
            / ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1.0)
        )
    if p <= phigh:
        q = p - 0.5
        r = q * q
        return (
            (((((a[0] * r + a[1]) * r + a[2]) * r + a[3]) * r + a[4]) * r + a[5]) * q
            / (((((b[0] * r + b[1]) * r + b[2]) * r + b[3]) * r + b[4]) * r + 1.0)
        )
    q = math.sqrt(-2.0 * math.log(1.0 - p))
    return -(
        (((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5])
        / ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1.0)
    )


def bootstrap_bca_ci(
    rank_samples,
    *,
    n_boot: int = 10000,
    alpha: float = 0.05,
    rng: np.random.Generator | None = None,
    statistic=None,
) -> tuple[float, float, float]:
    """Bias-corrected-and-accelerated bootstrap CI for a sample mean.

    Computes a ``(1 - alpha)`` BCa confidence interval on the mean of
    ``rank_samples`` by resampling with replacement ``n_boot`` times.
    This is the standard two-sided BCa bootstrap of Efron (1987).

    Parameters
    ----------
    rank_samples : array-like of float
        Observed sample (e.g. per-function ranks for one algorithm on
        one dimension).  Must contain at least two distinct values for
        the BCa acceleration term to be finite.
    n_boot : int, optional
        Number of bootstrap resamples (default 10 000).  The Efron and
        Tibshirani (1993) rule of thumb is ``n_boot >= 2000`` for a
        two-sided 95 % interval.
    alpha : float, optional
        Significance level; the returned interval covers the
        ``(1 - alpha)`` two-sided probability region (default 0.05
        for a 95 % interval).
    rng : numpy.random.Generator, required
        Seeded PRNG for reproducibility.  An explicit seeded generator
        must be passed; passing ``None`` raises ``ValueError`` so that
        callers cannot silently produce non-reproducible intervals by
        relying on implicit ``default_rng()`` entropy.
    statistic : callable, optional
        Summary statistic to apply on each resample.  Must accept a
        1-D ``np.ndarray`` and return a scalar.  Defaults to
        ``np.mean``.

    Returns
    -------
    tuple of (lo, hi, point)
        Lower and upper BCa endpoints together with the point estimate
        (``statistic`` applied to the original sample).

    Notes
    -----
    The accelerated percentile uses the jackknife formula
    ``a_hat = sum(u^3) / (6 * sum(u^2)^(3/2))`` where
    ``u_i = mean(x_{-i}) - mean(x_{-})``.  When the sample is fully
    degenerate (all values equal), ``a_hat`` is undefined and this
    function falls back to the standard percentile interval
    ``[theta_hat, theta_hat]``.

    References
    ----------
    Efron, B. (1987).  Better bootstrap confidence intervals.
    *Journal of the American Statistical Association*, 82(397),
    171-185.
    Efron, B. and Tibshirani, R. J. (1993).  *An Introduction to the
    Bootstrap*, Chapman and Hall / CRC Monographs on Statistics and
    Applied Probability 57.
    """
    x = np.asarray(rank_samples, dtype=np.float64).ravel()
    n = x.size
    if n == 0:
        raise ValueError("bootstrap_bca_ci: rank_samples is empty")

    stat = statistic if statistic is not None else np.mean
    theta_hat = float(stat(x))

    # Degenerate sample -> point interval
    if np.all(x == x[0]):
        return theta_hat, theta_hat, theta_hat

    if rng is None:
        raise ValueError(
            "bootstrap_bca_ci: an explicit np.random.Generator must be passed "
            "via rng=... for reproducibility; callers must seed their own RNG "
            "rather than relying on default_rng() entropy."
        )

    # Bootstrap resamples
    idx = rng.integers(0, n, size=(n_boot, n))
    boots = np.empty(n_boot, dtype=np.float64)
    for b in range(n_boot):
        boots[b] = float(stat(x[idx[b]]))
    boots.sort()

    # Bias-correction z0
    frac_below = float(np.mean(boots < theta_hat))
    frac_below = min(max(frac_below, 1e-9), 1.0 - 1e-9)
    z0 = _norm_ppf(frac_below)

    # Jackknife acceleration a_hat
    total = x.sum()
    # jackknife mean of the i-th leave-one-out sample = (total - x_i) / (n - 1)
    jack_means = (total - x) / (n - 1)
    jack_grand_mean = float(jack_means.mean())
    u = jack_grand_mean - jack_means  # sign per Efron (1987)
    num = float(np.sum(u ** 3))
    den = 6.0 * float(np.sum(u ** 2)) ** 1.5
    a_hat = num / den if den > 0 else 0.0

    # BCa percentile endpoints
    z_alpha_lo = _norm_ppf(alpha / 2.0)
    z_alpha_hi = _norm_ppf(1.0 - alpha / 2.0)

    def _alpha_adj(z_alpha: float) -> float:
        val = z0 + (z0 + z_alpha) / (1.0 - a_hat * (z0 + z_alpha))
        return _norm_cdf(val)

    alpha_lo = _alpha_adj(z_alpha_lo)
    alpha_hi = _alpha_adj(z_alpha_hi)

    # Clamp to [0, 1] just in case of round-off
    alpha_lo = float(min(max(alpha_lo, 0.0), 1.0))
    alpha_hi = float(min(max(alpha_hi, 0.0), 1.0))

    lo = float(np.quantile(boots, alpha_lo, method="linear"))
    hi = float(np.quantile(boots, alpha_hi, method="linear"))
    return lo, hi, theta_hat
