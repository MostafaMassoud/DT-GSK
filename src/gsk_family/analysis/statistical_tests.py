"""
Statistical Analysis for DT-GSK Benchmark Comparison
====================================================

Implements nonparametric tests used in the eGSK and ATMALS-GSK theses
for fair, publication-grade comparison of optimisation algorithms.

Tests Implemented
-----------------
1. **Wilcoxon Signed-Rank Test** (pairwise, per dimension)
   - Compares two algorithms using mean errors paired by function
   - Reports R+, R-, p-value, win/tie/loss counts, and decision
   - Significance level alpha = 0.05

2. **Friedman Test** (multi-algorithm ranking, per dimension)
   - Ranks all algorithms per function by mean error
   - Reports mean rank per algorithm, overall rank, and p-value
   - Lower rank = better performance

Both theses use these tests on CEC 2017 mean errors across 29 functions
(excluding F2), with 51 independent runs per function.

Usage Example
-------------
    from gsk_family.statistical_tests import run_statistical_analysis
    from pathlib import Path

    report = run_statistical_analysis(
        new_summary_csv=Path(
            "results/dt-gsk/dt-gsk/cec2017/summary/dt-gsk_cec2017_D10.csv"
        ),
        ref_base_dir=Path("benchmarks/cec_reference_results/cec2017"),
        suite="CEC2017",
        dim=10,
        new_label="dt-gsk",
    )
    print(report)

Notes
-----
- Requires ``scipy>=1.10`` for ``scipy.stats.wilcoxon`` and
  ``scipy.stats.friedmanchisquare``.  Falls back gracefully with
  a warning message when scipy is not installed.
- All p-values use two-sided tests with ``zero_method='zsplit'``.
"""

from __future__ import annotations

import csv
import warnings
from collections.abc import Sequence
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

from .project_policy import REFERENCE_COMPARATORS
from .result_loader import audit_source_open

try:
    from scipy import stats as sp_stats
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False


def _load_means(csv_path: Path, excluded: Sequence[int] = (2,)) -> dict[int, float]:
    """Load function-to-mean-error mapping from a summary CSV.

    Parameters
    ----------
    csv_path : Path
        Path to summary CSV.  Accepts two header variants:
        - ``Function`` column with ``F1`` prefix or numeric IDs
        - ``Func`` column with numeric IDs
    excluded : sequence of int, default=(2,)
        Function IDs to skip (e.g., CEC2017 F2 is unstable).

    Returns
    -------
    dict[int, float]
        Mapping of function_id to mean error value.

    Notes
    -----
    Rows with empty or missing Mean values are silently skipped.
    """
    result: dict[int, float] = {}
    # Strict-source chokepoint (publication analyses, Section 2.3): log every
    # opened summary CSV; in strict mode refuse paths outside the immutable
    # evidence release.
    audit_source_open(csv_path, role="stats_means_csv")
    with csv_path.open("r", newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        # Detect function ID column (Schema A: "Function", Schema B: "Func")
        fn_col = None
        if reader.fieldnames:
            for candidate in ("Function", "function", "Func", "func"):
                if candidate in reader.fieldnames:
                    fn_col = candidate
                    break
        if fn_col is None:
            return result
        for row in reader:
            raw_id = row.get(fn_col, "").strip()
            if not raw_id:
                continue
            # Parse "F1" or "1" format
            if raw_id.upper().startswith("F"):
                fid = int(raw_id[1:])
            else:
                fid = int(raw_id)
            if fid in excluded:
                continue
            mean_str = row.get("Mean", "").strip()
            if not mean_str:
                continue
            result[fid] = float(mean_str)
    return result


def _simple_rankdata(arr: np.ndarray) -> np.ndarray:
    """Fallback rank computation when scipy is unavailable."""
    order = np.argsort(arr)
    ranks = np.empty_like(arr, dtype=np.float64)
    ranks[order] = np.arange(1, len(arr) + 1, dtype=np.float64)
    return ranks


# ============================================================================
# Result Dataclasses
# ============================================================================

@dataclass(frozen=True)
class WilcoxonResult:
    """Result of a Wilcoxon signed-rank test between two algorithms.

    Attributes
    ----------
    funcs : list[int]
        Common function IDs compared.
    n_pairs : int
        Number of non-tied pairs used in the test.
    R_plus : float
        Sum of positive ranks (new algorithm is better).
    R_minus : float
        Sum of negative ranks (reference algorithm is better).
    p_value : float
        Two-sided p-value from the Wilcoxon test.
    wins : int
        Number of functions where new algorithm has lower mean error.
    ties : int
        Number of functions with no significant difference.
    losses : int
        Number of functions where reference algorithm is better.
    decision : str
        Overall decision: '+' (new better), '-' (ref better), '=' (no diff).
    per_func : list[tuple]
        Per-function detail: (func_id, new_mean, ref_mean, sign).
    r_effect : float
        Standardised Wilcoxon effect size r = Z / sqrt(n_pairs).
        Sign follows the direction: positive = new better, negative = ref better.
        Magnitude interpretation (Cohen): |r|<0.1 negligible, 0.1-0.3 small,
        0.3-0.5 medium, >=0.5 large.  NaN when n_pairs < 2.
    cliffs_delta : float
        Cliff's delta non-parametric effect size in [-1, 1], computed from
        the per-function win/loss counts as
        (wins - losses) / (wins + losses + ties).  Each pair counts once
        across the suite (e.g. 29 paired CEC2017 functions → 29 outcomes),
        so this is a function-level effect size, distinct from the
        per-run A_12 reported elsewhere.  Positive = new better,
        negative = ref better.  Magnitude interpretation (Romano):
        |d|<0.147 negligible, 0.147-0.33 small, 0.33-0.474 medium,
        >=0.474 large.
    """
    funcs: list
    n_pairs: int
    R_plus: float
    R_minus: float
    p_value: float
    wins: int
    ties: int
    losses: int
    decision: str
    per_func: list
    r_effect: float = float("nan")
    cliffs_delta: float = 0.0


@dataclass(frozen=True)
class FriedmanResult:
    """Result of a Friedman ranking test across multiple algorithms.

    Attributes
    ----------
    alg_names : list[str]
        Algorithm names in input order.
    func_ids : list[int]
        Common function IDs used for ranking.
    ranks_matrix : np.ndarray
        Per-function ranks, shape (n_funcs, n_algs).
    mean_ranks : dict[str, float]
        Mean rank per algorithm (lower is better).
    overall_order : list[tuple[str, float]]
        Algorithms sorted by mean rank (best first).
    p_value : float
        p-value from the Friedman chi-squared test.
    """
    alg_names: list
    func_ids: list
    ranks_matrix: np.ndarray
    mean_ranks: dict
    overall_order: list
    p_value: float


# Canonical GSK-family algorithm names (case-insensitive comparators carried
# in `benchmarks/cec_reference_results/cec2017/` plus the new DT-GSK label). Used
# to build the 7-algo "GSK-family" Friedman panel (6 comparators + DT-GSK).
# The paper scope is GSK-family-only, so this is also the full comparator set;
# keep this list aligned with CLAUDE.md "publication scope covers the GSK
# family (6 comparators)".
_GSK_FAMILY_REF_NAMES: frozenset[str] = frozenset(
    alg.upper() for alg in REFERENCE_COMPARATORS
)


@dataclass(frozen=True)
class StatAnalysisResult:
    """Bundle of per-dim statistical-analysis outputs.

    Attributes
    ----------
    dim : int
        Problem dimension this result was computed for.
    new_label : str
        Display label for the new algorithm (e.g. ``dt-gsk``).
    text : str
        Full formatted report (Wilcoxon tables + Friedman table +
        per-dim peer comparison) -- printed verbatim by the runner.
    friedman_gsk_family : FriedmanResult | None
        7-algo Friedman result restricted to DT-GSK + the GSK-family
        comparators.  ``None`` if no GSK-family references were found.
        (The paper scope is GSK-family-only; this is the sole Friedman
        panel.)
    wilcoxon_results : dict[str, WilcoxonResult]
        Per-comparator Wilcoxon results keyed by reference label
        (e.g. ``"GSK"``, ``"AGSK"``).  Insertion-ordered to match the
        comparator iteration order used when building the full text
        report (priority refs first, then alphabetical).  Empty dict
        if no Wilcoxon panel ran.

    Notes
    -----
    ``__str__`` returns ``text`` so existing call-sites that do
    ``log.info(stat_report)`` keep working; new code accesses the
    structured Friedman + Wilcoxon fields for the per-dim TL;DR
    banner and cross-dim aggregation.
    """
    dim: int
    new_label: str
    text: str
    friedman_gsk_family: "FriedmanResult | None"
    wilcoxon_results: dict = field(default_factory=dict)

    def __str__(self) -> str:
        return self.text


# ============================================================================
# Wilcoxon Signed-Rank Test
# ============================================================================

def wilcoxon_signed_rank(
    new_means: dict[int, float],
    ref_means: dict[int, float],
    alpha: float = 0.05,
    zero_tol: float = 1e-8,
) -> WilcoxonResult:
    """Perform the Wilcoxon signed-rank test between two algorithms.

    Paired by function: (new_mean_Fi, ref_mean_Fi).
    Positive difference = new algorithm is BETTER (lower error).

    Parameters
    ----------
    new_means : dict[int, float]
        Function-to-mean-error mapping for the new algorithm.
    ref_means : dict[int, float]
        Function-to-mean-error mapping for the reference algorithm.
    alpha : float, default=0.05
        Significance level for the two-sided test.
    zero_tol : float, default=1e-8
        Values below this are treated as zero before comparison.

    Returns
    -------
    WilcoxonResult
        Dataclass with R_plus, R_minus, p_value, wins, ties, losses,
        decision, and per_func detail.

    Notes
    -----
    Uses ``scipy.stats.wilcoxon`` with ``zero_method='zsplit'`` for
    handling tied pairs, matching the methodology in the eGSK thesis.
    """
    common = sorted(set(new_means) & set(ref_means))

    per_func = []
    wins = ties = losses = 0

    for fid in common:
        n = new_means[fid]
        r = ref_means[fid]
        if abs(n) < zero_tol:
            n = 0.0
        if abs(r) < zero_tol:
            r = 0.0

        diff = r - n  # positive = new is better
        # Scale-aware tie tolerance: absolute floor ``zero_tol`` for small
        # values, and a relative 1e-10 * max(|n|,|r|) band for large values.
        # Without the relative band a 1e+3 vs 1e+3 + 1e-7 gap on a hybrid
        # function would be counted as a real win/loss even though it is
        # below both IEEE-754 and objective-function numerical noise.
        rel_tol = 1e-10 * max(abs(n), abs(r), 1.0)
        tie_band = max(zero_tol, rel_tol)
        if abs(diff) < tie_band:
            sign = "="
            ties += 1
        elif diff > 0:
            sign = "+"
            wins += 1
        else:
            sign = "-"
            losses += 1
        per_func.append((fid, n, r, sign))

    new_arr = np.array([new_means[f] for f in common], dtype=np.float64)
    ref_arr = np.array([ref_means[f] for f in common], dtype=np.float64)
    diffs = ref_arr - new_arr

    abs_diffs = np.abs(diffs)
    nonzero = abs_diffs > zero_tol
    n_pairs = int(nonzero.sum())

    R_plus = 0.0
    R_minus = 0.0
    p_value = 1.0

    if n_pairs >= 2:
        nz_abs = abs_diffs[nonzero]
        nz_sign = diffs[nonzero]
        ranks = sp_stats.rankdata(nz_abs) if HAS_SCIPY else _simple_rankdata(nz_abs)

        R_plus = float(np.sum(ranks[nz_sign > 0]))
        R_minus = float(np.sum(ranks[nz_sign < 0]))

        if HAS_SCIPY:
            try:
                # Use the exact permutation distribution when the sample
                # is small enough (n_pairs < 25) for the asymptotic
                # approximation to be unreliable; scipy's heuristic only
                # kicks in at n_pairs < 25, so we request it explicitly
                # here and fall back to the default (``"auto"``) for
                # larger samples.  This also matches the footnote in the
                # per-dim Holm block of Section 4.
                method = "exact" if n_pairs < 25 else "auto"
                _, p_value = sp_stats.wilcoxon(
                    new_arr, ref_arr,
                    zero_method="zsplit",
                    alternative="two-sided",
                    method=method,
                )
                p_value = float(p_value)
            except (TypeError, ValueError):
                # ``method=`` was introduced in SciPy 1.9; on older
                # installations retry without it.
                try:
                    _, p_value = sp_stats.wilcoxon(
                        new_arr, ref_arr,
                        zero_method="zsplit",
                        alternative="two-sided",
                    )
                    p_value = float(p_value)
                except ValueError:
                    p_value = 1.0
        else:
            p_value = float("nan")

    if p_value < alpha:
        decision = "+" if R_plus > R_minus else "-"
    else:
        decision = "="

    # Effect sizes.
    #
    # r = Z / sqrt(n_pairs) for the Wilcoxon signed-rank test.  We derive
    # |Z| by inverting the SciPy two-sided p-value, which internally
    # applies both the continuity (+/-0.5) and the ties correction to
    # sigma_w.  Doing it this way guarantees that the magnitude of r is
    # numerically consistent with the p-value reported on the same line:
    # small p_value <=> large |r|, with no possibility of the two
    # disagreeing in a tie-heavy sample (strict Q1 reviewers flagged the
    # earlier uncorrected formula as inconsistent in tied regimes).
    #
    # The sign of r is taken from the Wilcoxon rank-sum comparison
    # (R_plus > R_minus means the first argument is better, i.e. positive
    # improvement, i.e. r > 0) because the p-value itself is two-sided
    # and has no sign.  When R_plus == R_minus we report r = 0.
    r_effect = float("nan")
    if n_pairs >= 2:
        if HAS_SCIPY and np.isfinite(p_value) and 0.0 < p_value < 1.0:
            z_abs = float(sp_stats.norm.isf(p_value / 2.0))
            if R_plus > R_minus:
                z_sign = 1.0
            elif R_plus < R_minus:
                z_sign = -1.0
            else:
                z_sign = 0.0
            z_stat = z_sign * z_abs
            r_effect = float(z_stat / np.sqrt(n_pairs))
        else:
            # SciPy unavailable or p_value at a boundary (0 / 1 / nan).
            # Fall back to the uncorrected normal approximation.  At
            # p=1 (no effect) we correctly get r=0; at p very close to
            # 0 the uncorrected and corrected Z differ by at most the
            # continuity offset 0.5/sigma_w, which is negligible
            # compared to the reported |Z| in that regime.
            mu_w = n_pairs * (n_pairs + 1) / 4.0
            sigma_w = np.sqrt(n_pairs * (n_pairs + 1) * (2 * n_pairs + 1) / 24.0)
            if sigma_w > 0:
                z_stat = (R_plus - mu_w) / sigma_w
                r_effect = float(z_stat / np.sqrt(n_pairs))

    # Cliff's delta on paired function-level outcomes.
    n_total = wins + ties + losses
    cliffs_delta = 0.0 if n_total == 0 else float(wins - losses) / float(n_total)

    return WilcoxonResult(
        funcs=common,
        n_pairs=n_pairs,
        R_plus=R_plus,
        R_minus=R_minus,
        p_value=p_value,
        wins=wins,
        ties=ties,
        losses=losses,
        decision=decision,
        per_func=per_func,
        r_effect=r_effect,
        cliffs_delta=cliffs_delta,
    )


# ============================================================================
# Friedman Test
# ============================================================================

def friedman_rank_test(
    alg_means: dict[str, dict[int, float]],
    excluded: Sequence[int] = (2,),
    zero_tol: float = 1e-8,
) -> FriedmanResult:
    """Perform the Friedman test to rank multiple algorithms.

    Ranks per function (lower error = lower rank = better), then
    averages across all functions for an overall ranking.

    Parameters
    ----------
    alg_means : dict[str, dict[int, float]]
        Algorithm name -> {function_id: mean_error} mapping.
    excluded : sequence of int, default=(2,)
        Function IDs to exclude from ranking.
    zero_tol : float, default=1e-8
        Values below this are treated as zero.

    Returns
    -------
    FriedmanResult
        Dataclass with alg_names, func_ids, ranks_matrix,
        mean_ranks, overall_order, and p_value.

    Notes
    -----
    Uses ``scipy.stats.friedmanchisquare`` for the chi-squared
    statistic.  Requires at least 3 functions and 3 algorithms;
    the p-value falls back to 1.0 (and no warning is emitted) when
    fewer than 3 algorithms are available — ranks are still returned.
    """
    alg_names = list(alg_means.keys())
    n_algs = len(alg_names)

    if n_algs < 2:
        return FriedmanResult(
            alg_names=alg_names, func_ids=[],
            ranks_matrix=np.empty((0, 0)),
            mean_ranks={a: 1.0 for a in alg_names},
            overall_order=[(a, 1.0) for a in alg_names],
            p_value=1.0,
        )

    common_funcs = None
    for name in alg_names:
        fids = set(alg_means[name].keys()) - set(excluded)
        common_funcs = fids if common_funcs is None else (common_funcs & fids)

    func_ids = sorted(common_funcs) if common_funcs else []
    n_funcs = len(func_ids)

    if n_funcs < 3:
        mean_ranks = {a: float(i + 1) for i, a in enumerate(alg_names)}
        return FriedmanResult(
            alg_names=alg_names, func_ids=func_ids,
            ranks_matrix=np.empty((0, n_algs)),
            mean_ranks=mean_ranks,
            overall_order=sorted(mean_ranks.items(), key=lambda x: x[1]),
            p_value=1.0,
        )

    err_matrix = np.zeros((n_funcs, n_algs), dtype=np.float64)
    for j, name in enumerate(alg_names):
        for i, fid in enumerate(func_ids):
            val = alg_means[name].get(fid, float("inf"))
            if abs(val) < zero_tol:
                val = 0.0
            err_matrix[i, j] = val

    ranks_matrix = np.zeros_like(err_matrix)
    for i in range(n_funcs):
        ranks_matrix[i, :] = (
            sp_stats.rankdata(err_matrix[i, :]) if HAS_SCIPY
            else _simple_rankdata(err_matrix[i, :])
        )

    mean_ranks_arr = np.mean(ranks_matrix, axis=0)
    mean_ranks = {alg_names[j]: float(mean_ranks_arr[j]) for j in range(n_algs)}
    overall_order = sorted(mean_ranks.items(), key=lambda x: x[1])

    p_value = 1.0
    if HAS_SCIPY and n_funcs >= 3 and n_algs >= 3:
        try:
            columns = [err_matrix[:, j] for j in range(n_algs)]
            with warnings.catch_warnings():
                warnings.simplefilter("error", RuntimeWarning)
                _, p_value = sp_stats.friedmanchisquare(*columns)
            p_value = float(p_value)
        except (ValueError, RuntimeWarning) as err:
            warnings.warn(
                f"friedmanchisquare raised {type(err).__name__}: {err!s}. "
                "Returning p_value=NaN; caller should treat the Friedman "
                "p-value as undefined for this cell.",
                RuntimeWarning,
                stacklevel=2,
            )
            p_value = float("nan")

    return FriedmanResult(
        alg_names=alg_names, func_ids=func_ids,
        ranks_matrix=ranks_matrix, mean_ranks=mean_ranks,
        overall_order=overall_order, p_value=p_value,
    )


# ============================================================================
# Formatted Output
# ============================================================================

def format_wilcoxon_table(result: WilcoxonResult, new_label: str, ref_label: str, dim: int) -> str:
    """Format Wilcoxon result matching eGSK Table 4.11 / ATMALS-GSK Table 4.17."""
    lines: list[str] = []

    lines.append("")
    lines.append("+" + "=" * 78 + "+")
    title = f"Wilcoxon Signed-Rank Test: {new_label} vs {ref_label} (D={dim})"
    lines.append(f"|{title:^78}|")
    lines.append("+" + "=" * 78 + "+")
    lines.append("  Significance level alpha = 0.05")
    lines.append(f"  + = {new_label} better | - = {ref_label} better | = = no significant difference")
    lines.append("")

    lines.append("  +" + "-" * 10 + "+" + "-" * 10 + "+" + "-" * 12 + "+" + "-" * 6 + "+" + "-" * 6 + "+" + "-" * 6 + "+" + "-" * 8 + "+")
    lines.append(
        f"  |{'R+':^10}|{'R-':^10}|{'p Value':^12}|"
        f"{'  +  ':^6}|{'  =  ':^6}|{'  -  ':^6}|{' Dec. ':^8}|"
    )
    lines.append("  +" + "-" * 10 + "+" + "-" * 10 + "+" + "-" * 12 + "+" + "-" * 6 + "+" + "-" * 6 + "+" + "-" * 6 + "+" + "-" * 8 + "+")

    p_str = f"{result.p_value:.4f}" if not np.isnan(result.p_value) else "N/A"

    lines.append(
        f"  |{result.R_plus:^10.0f}|{result.R_minus:^10.0f}|{p_str:^12}|"
        f"{result.wins:^6}|{result.ties:^6}|{result.losses:^6}|{result.decision:^8}|"
    )
    lines.append("  +" + "-" * 10 + "+" + "-" * 10 + "+" + "-" * 12 + "+" + "-" * 6 + "+" + "-" * 6 + "+" + "-" * 6 + "+" + "-" * 8 + "+")

    # Per-function detail
    lines.append("")
    lines.append("  Per-function detail:")
    lines.append("  +" + "-" * 6 + "+" + "-" * 14 + "+" + "-" * 14 + "+" + "-" * 6 + "+")
    lines.append(f"  |{'Func':^6}|{new_label:^14}|{ref_label:^14}|{'Sign':^6}|")
    lines.append("  +" + "-" * 6 + "+" + "-" * 14 + "+" + "-" * 14 + "+" + "-" * 6 + "+")

    for fid, n_mean, r_mean, sign in result.per_func:
        n_s = f"{n_mean:.3e}" if n_mean > 1e-8 else "0.00E+00"
        r_s = f"{r_mean:.3e}" if r_mean > 1e-8 else "0.00E+00"
        lines.append(f"  |{'F' + str(fid).zfill(2):^6}|{n_s:^14}|{r_s:^14}|{sign:^6}|")

    lines.append("  +" + "-" * 6 + "+" + "-" * 14 + "+" + "-" * 14 + "+" + "-" * 6 + "+")

    total = result.wins + result.ties + result.losses
    if total > 0:
        pct = 100.0 * result.wins / total
        lines.append("")
        lines.append(
            f"  Success ratio: {result.wins}/{total} = {pct:.1f}%  "
            f"(+ {result.wins}, = {result.ties}, - {result.losses})"
        )
    lines.append("")
    return "\n".join(lines)


def format_friedman_table(
    result: FriedmanResult,
    dim: int,
    panel_label: str | None = None,
) -> str:
    """Format Friedman result matching eGSK Table 4.12 / ATMALS-GSK Table 4.20.

    Parameters
    ----------
    result : FriedmanResult
        The Friedman ranking to render.
    dim : int
        Problem dimension (appears in the title).
    panel_label : str | None
        Optional panel name (e.g. ``"GSK-family Friedman ranking"``).
        When provided, the panel name and ``D=<dim>`` are shown together
        in a single 78-char-wide title box -- avoiding the doubly-boxed
        look of an outer section header wrapping a smaller default
        Friedman box.
    """
    lines: list[str] = []
    overall = result.overall_order
    p_val = result.p_value

    if panel_label is not None:
        title = f"{panel_label} -- D={dim}"
        bar = "=" * 78
        lines.append("")
        lines.append("+" + bar + "+")
        lines.append(f"|{title:^78}|")
        lines.append("+" + bar + "+")
    else:
        lines.append("")
        lines.append("+" + "=" * 56 + "+")
        title = f"Friedman Test Ranking (D={dim})"
        lines.append(f"|{title:^56}|")
        lines.append("+" + "=" * 56 + "+")

    lines.append(f"  Functions compared: {len(result.func_ids)}")
    lines.append("")

    lines.append("  +" + "-" * 22 + "+" + "-" * 14 + "+" + "-" * 14 + "+")
    lines.append(f"  |{'Algorithm':^22}|{'Mean Rank':^14}|{'Overall Rank':^14}|")
    lines.append("  +" + "-" * 22 + "+" + "-" * 14 + "+" + "-" * 14 + "+")

    for rank_pos, (name, mean_rank) in enumerate(overall, 1):
        lines.append(f"  |{name:^22}|{mean_rank:^14.2f}|{rank_pos:^14}|")

    lines.append("  +" + "-" * 22 + "+" + "-" * 14 + "+" + "-" * 14 + "+")

    p_str = f"{p_val:.2e}" if (not np.isnan(p_val) and p_val > 0) else "N/A"
    sig = "YES (reject H0)" if (not np.isnan(p_val) and p_val < 0.05) else "NO"
    lines.append(f"  p-value: {p_str}    Significant (alpha=0.05): {sig}")

    if not np.isnan(p_val) and p_val < 0.05:
        winner = overall[0][0]
        lines.append(f"  --> {winner} achieves the best (lowest) mean rank.")
    lines.append("")

    return "\n".join(lines)


# ============================================================================
# High-Level Runner
# ============================================================================

def format_per_dim_peer_comparison(
    friedman: FriedmanResult,
    new_label: str,
    dim: int,
    *,
    panel_label: str = "GSK family",
) -> str:
    """Format the single-row "DT-GSK position vs nearest peer" table.

    The "nearest peer" is the algorithm immediately adjacent to the new
    algorithm in the supplied ranking: the rank-above peer when the new
    algorithm is not #1, otherwise the rank-below peer.  The delta
    column is ``mean(peer) - mean(new)`` -- positive when DT-GSK is
    ahead of its nearest peer, negative when behind.

    ``panel_label`` is rendered in the title (e.g. ``"GSK family"`` for
    the 7-algo panel) so the helper can label the peer-comparison block.
    """
    overall = friedman.overall_order
    if not overall:
        return ""
    # Locate DT-GSK in the overall_order list.
    idx = next((i for i, (n, _) in enumerate(overall) if n == new_label), -1)
    if idx < 0:
        return ""

    rank = idx + 1
    new_mean = overall[idx][1]
    if idx == 0:
        peer_idx = 1 if len(overall) > 1 else 0
        relation = "ahead of"
    else:
        peer_idx = idx - 1
        relation = "behind"
    if peer_idx == idx:
        return ""
    peer_name, peer_mean = overall[peer_idx]
    delta = peer_mean - new_mean  # positive => new is better than peer

    W_DIM, W_LABEL, W_RANK, W_PEER, W_DELTA = 6, 24, 14, 24, 12
    INNER = W_DIM + W_LABEL + W_RANK + W_PEER + W_DELTA + 4
    BAR_W = max(78, INNER + 2)
    rule = "  +" + "+".join("-" * w for w in (W_DIM, W_LABEL, W_RANK, W_PEER, W_DELTA)) + "+"

    lines: list[str] = []
    lines.append("")
    lines.append("+" + "=" * BAR_W + "+")
    title = f"Per-dimension DT-GSK position vs nearest peer ({panel_label}) -- D={dim}"
    lines.append(f"|{title:^{BAR_W}}|")
    lines.append("+" + "=" * BAR_W + "+")
    lines.append(rule)
    lines.append(
        f"  |{'Dim':^{W_DIM}}|{'DT-GSK label':^{W_LABEL}}|{'Rank':^{W_RANK}}|"
        f"{'Nearest peer':^{W_PEER}}|{'Delta-rank':^{W_DELTA}}|"
    )
    lines.append(rule)
    lines.append(
        f"  |{dim:^{W_DIM}}|{new_label:^{W_LABEL}}|"
        f"{f'#{rank} ({new_mean:.2f})':^{W_RANK}}|"
        f"{peer_name:^{W_PEER}}|{delta:^+{W_DELTA}.2f}|"
    )
    lines.append(rule)
    lines.append(f"  DT-GSK is {relation} {peer_name} by {abs(delta):.2f} mean-rank units.")
    lines.append("")
    return "\n".join(lines)


def format_cross_dim_summary(
    results: Sequence["StatAnalysisResult"],
    new_label: str,
    suite: str = "CEC2017",
) -> str:
    """Build the end-of-all-dimensions summary block.

    Two back-to-back tables, one row per dim (GSK-family-only scope):
      1. GSK-family Friedman ranking (7-algo) - DT-GSK rank + delta to #2
      2. Per-dim DT-GSK position vs nearest peer (GSK family)

    The ``suite`` argument controls only the title labels — the ranking
    rows themselves come from the per-dim ``StatAnalysisResult`` objects
    the caller supplies.

    Returns the empty string when ``results`` is empty, OR when none of
    the per-dim results carries a non-empty Friedman panel (e.g. CEC2013
    with only the ``gsk`` reference available -- a 2-algorithm Friedman
    is degenerate, and emitting an all-dashes table just adds noise to
    the suite log).  In that case the per-dim Wilcoxon vs GSK panels
    remain the only statistical output for the suite.
    """
    if not results:
        return ""
    has_any_friedman = any(
        (r.friedman_gsk_family is not None and r.friedman_gsk_family.overall_order)
        for r in results
    )
    if not has_any_friedman:
        return ""
    suite_label = str(suite).upper()

    # Column widths chosen so algorithm names plus a "(+/-X.XX)" suffix
    # never overflow (the widest peer cell carries a name + delta suffix).
    # Title bar spans the same total interior width as the row separator
    # below it.
    W_DIM, W_RANK, W_MEAN, W_PEER, W_WINNER = 6, 8, 12, 32, 32
    INNER = W_DIM + W_RANK + W_MEAN + W_PEER + W_WINNER + 4  # 4 inner '|'
    BAR_W = max(78, INNER + 2)

    def _row_for(friedman: "FriedmanResult | None") -> tuple[str, str, str, str]:
        if friedman is None or not friedman.overall_order:
            return ("--", "--", "--", "--")
        order = friedman.overall_order
        idx = next((i for i, (n, _) in enumerate(order) if n == new_label), -1)
        if idx < 0:
            return ("--", "--", "--", "--")
        rank = f"#{idx + 1}"
        new_mean = f"{order[idx][1]:.2f}"
        winner_name, winner_mean = order[0]
        if idx == 0:
            peer_idx = 1 if len(order) > 1 else 0
        else:
            peer_idx = idx - 1
        if peer_idx == idx:
            peer = "--"
        else:
            peer_name, peer_mean = order[peer_idx]
            delta = peer_mean - order[idx][1]
            peer = f"{peer_name} ({delta:+.2f})"
        return (rank, new_mean, peer, f"{winner_name} ({winner_mean:.2f})")

    def _ruled(*widths: int) -> str:
        return "  +" + "+".join("-" * w for w in widths) + "+"

    PEER_W = W_PEER
    DELTA_W = 12

    def _peer_rows(getter) -> list[str]:
        rows: list[str] = []
        for r in results:
            friedman = getter(r)
            if friedman is None or not friedman.overall_order:
                rows.append(
                    f"  |{r.dim:^{W_DIM}}|{'--':^{W_RANK}}|{'--':^{PEER_W}}|{'--':^{DELTA_W}}|"
                )
                continue
            order = friedman.overall_order
            idx = next((i for i, (n, _) in enumerate(order) if n == new_label), -1)
            if idx < 0:
                rows.append(
                    f"  |{r.dim:^{W_DIM}}|{'--':^{W_RANK}}|{'--':^{PEER_W}}|{'--':^{DELTA_W}}|"
                )
                continue
            rank = f"#{idx + 1}"
            peer_idx = (1 if len(order) > 1 else 0) if idx == 0 else idx - 1
            if peer_idx == idx:
                rows.append(
                    f"  |{r.dim:^{W_DIM}}|{rank:^{W_RANK}}|{'--':^{PEER_W}}|{'--':^{DELTA_W}}|"
                )
                continue
            peer_name, peer_mean = order[peer_idx]
            delta = peer_mean - order[idx][1]
            rows.append(
                f"  |{r.dim:^{W_DIM}}|{rank:^{W_RANK}}|{peer_name:^{PEER_W}}|{delta:^+{DELTA_W}.2f}|"
            )
        return rows

    parts: list[str] = []
    parts.append("")
    parts.append("#" * BAR_W)
    parts.append(f"  CROSS-DIMENSION STATISTICAL SUMMARY -- {new_label}")
    parts.append("#" * BAR_W)

    # Output order matches the per-dim block (GSK-family-only scope):
    #   1. GSK-family Friedman ranking (7-algo)
    #   2. Per-dim peer (GSK family)

    # 1. GSK-family Friedman ranking (7-algo) per dim
    parts.append("")
    parts.append("+" + "=" * BAR_W + "+")
    parts.append(f"|{f'GSK-family Friedman ranking ({suite_label})':^{BAR_W}}|")
    parts.append("+" + "=" * BAR_W + "+")
    parts.append(_ruled(W_DIM, W_RANK, W_MEAN, W_PEER, W_WINNER))
    parts.append(
        f"  |{'Dim':^{W_DIM}}|{'Rank':^{W_RANK}}|{'Mean rank':^{W_MEAN}}|"
        f"{'Nearest peer (delta)':^{W_PEER}}|{'#1 (mean rank)':^{W_WINNER}}|"
    )
    parts.append(_ruled(W_DIM, W_RANK, W_MEAN, W_PEER, W_WINNER))
    for r in results:
        rank, mean, peer, winner = _row_for(r.friedman_gsk_family)
        parts.append(
            f"  |{r.dim:^{W_DIM}}|{rank:^{W_RANK}}|{mean:^{W_MEAN}}|"
            f"{peer:^{W_PEER}}|{winner:^{W_WINNER}}|"
        )
    parts.append(_ruled(W_DIM, W_RANK, W_MEAN, W_PEER, W_WINNER))

    # 2. Per-dim peer comparison (GSK family)
    parts.append("")
    parts.append("+" + "=" * BAR_W + "+")
    parts.append(f"|{'Per-dimension DT-GSK position vs nearest peer (GSK family)':^{BAR_W}}|")
    parts.append("+" + "=" * BAR_W + "+")
    parts.append(_ruled(W_DIM, W_RANK, PEER_W, DELTA_W))
    parts.append(
        f"  |{'Dim':^{W_DIM}}|{'Rank':^{W_RANK}}|"
        f"{'Nearest peer':^{PEER_W}}|{'Delta-rank':^{DELTA_W}}|"
    )
    parts.append(_ruled(W_DIM, W_RANK, PEER_W, DELTA_W))
    parts.extend(_peer_rows(lambda r: r.friedman_gsk_family))
    parts.append(_ruled(W_DIM, W_RANK, PEER_W, DELTA_W))
    parts.append("")

    return "\n".join(parts)


def format_per_dim_tldr(
    result: "StatAnalysisResult",
    suite: str = "CEC2017",
    log_path: str | None = None,
) -> str:
    """Per-dim TL;DR banner with compact Wilcoxon + Friedman headlines.

    Designed to be the LAST thing printed for each dim so the headline
    decisions survive in console scrollback even when the next dim
    immediately starts streaming its own ~700-line Wilcoxon panel.
    Shows the COMPACT Wilcoxon decision table (one row per comparator)
    plus a one-line GSK-family Friedman headline -- the FULL ranking
    table is already emitted earlier in the same dim block by
    ``run_statistical_analysis``, so this banner intentionally avoids
    duplicating it.

    Output structure (~20 lines):
      - Banner header
      - Wilcoxon Signed-Rank decision table (one row per comparator)
      - GSK-family Friedman headline (rank + p-value, no full table)
      - Path to the per-dim log file (if given)

    Returns the empty string when the Friedman panel is None
    (e.g. no references found, or vanilla GSK parity run).
    """
    if result.friedman_gsk_family is None:
        return ""

    BAR_W = 78
    label = result.new_label
    suite_label = str(suite).upper()

    def _headline(friedman: "FriedmanResult | None", title: str) -> list[str]:
        lines: list[str] = []
        lines.append("")
        lines.append(f"  {title}")
        if friedman is None or not friedman.overall_order:
            lines.append("    (panel not built -- no references found)")
            return lines
        order = friedman.overall_order
        sig = "*" if friedman.p_value < 0.05 else "ns"
        idx = next((i for i, (n, _) in enumerate(order) if n == label), -1)
        winner_name, winner_mean = order[0]
        if idx >= 0:
            mean = order[idx][1]
            lines.append(
                f"    {label} #{idx + 1} of {len(order)}  "
                f"(mean rank {mean:.2f})  "
                f"p={friedman.p_value:.2e}  alpha=0.05  {sig}"
            )
        else:
            lines.append(
                f"    {label} not in panel  "
                f"p={friedman.p_value:.2e}  alpha=0.05  {sig}"
            )
        lines.append(
            f"    #1 = {winner_name} (mean rank {winner_mean:.2f})"
        )
        return lines

    parts: list[str] = []
    parts.append("")
    parts.append("+" + "=" * BAR_W + "+")
    title = f"KEY RESULTS  ({suite_label}, D={result.dim}) -- {label}"
    parts.append(f"|{title:^{BAR_W}}|")
    parts.append("+" + "=" * BAR_W + "+")
    parts.extend(_wilcoxon_summary_table(result))
    parts.extend(_headline(result.friedman_gsk_family, "GSK-family Friedman headline:"))
    if log_path:
        parts.append("")
        parts.append("  Full per-dim Wilcoxon + Friedman log:")
        parts.append(f"    {log_path}")
    parts.append("+" + "=" * BAR_W + "+")
    parts.append("")
    return "\n".join(parts)


def _wilcoxon_summary_table(result: "StatAnalysisResult") -> list[str]:
    """Compact one-row-per-comparator Wilcoxon summary table.

    Used inside ``format_per_dim_tldr`` so the banner shows the full
    Wilcoxon panel decisions for all comparators in ~16 lines (vs the
    ~700-line per-comparator tables emitted earlier in the same dim
    block).  Each row carries R+, R-, p-value, +/=/- counts, and
    overall decision -- enough for the reader to see who beat whom
    without scrolling up.

    Returns an empty list when ``result.wilcoxon_results`` is empty.
    """
    wsr_dict = getattr(result, "wilcoxon_results", None) or {}
    if not wsr_dict:
        return []
    W_REF, W_RPM, W_P, W_CNT, W_DEC = 22, 8, 12, 4, 8
    rule = (
        "  +" + "-" * W_REF + "+" + "-" * W_RPM + "+" + "-" * W_RPM + "+"
        + "-" * W_P + "+" + "-" * W_CNT + "+" + "-" * W_CNT + "+" + "-" * W_CNT
        + "+" + "-" * W_DEC + "+"
    )
    lines: list[str] = []
    lines.append("")
    lines.append(f"  Wilcoxon Signed-Rank vs {len(wsr_dict)} comparators:")
    lines.append(rule)
    lines.append(
        f"  |{'Comparator':^{W_REF}}|{'R+':^{W_RPM}}|{'R-':^{W_RPM}}|"
        f"{'p-value':^{W_P}}|{'+':^{W_CNT}}|{'=':^{W_CNT}}|{'-':^{W_CNT}}|"
        f"{'Dec.':^{W_DEC}}|"
    )
    lines.append(rule)
    for ref_label, wsr in wsr_dict.items():
        lines.append(
            f"  |{ref_label:^{W_REF}}|{int(wsr.R_plus):^{W_RPM}}|"
            f"{int(wsr.R_minus):^{W_RPM}}|"
            f"{f'{wsr.p_value:.4f}':^{W_P}}|"
            f"{wsr.wins:^{W_CNT}}|{wsr.ties:^{W_CNT}}|{wsr.losses:^{W_CNT}}|"
            f"{wsr.decision:^{W_DEC}}|"
        )
    lines.append(rule)
    return lines


def _resolve_comparator_csv(ref_dir: Path, ref_alg: str, suite: str, dim: int) -> Path | None:
    """Resolve the comparator summary CSV for one reference algorithm.

    The file layout is suite-dependent:

    - ``cec2011`` uses NATIVE per-problem dimensions, so each algorithm has a
      single rollup ``<alg>_cec2011.csv`` (22 problems) rather than a family of
      per-dimension ``<alg>_cec2011_D<dim>.csv`` files.  Windows is
      case-insensitive, but the committed reference for DT-GSK happens to be
      ``dt-gsk_CEC2011.csv`` (uppercase suite); other repos may differ, so we
      try the lowercase rollup, then a case-insensitive ``CEC2011`` fallback,
      then a final glob so the lookup is robust on case-sensitive filesystems.
    - all other suites (e.g. ``cec2017``) keep the existing per-dimension
      ``<alg>_<suite>_D<dim>.csv`` layout with a ``D{dim:02d}`` fallback.

    Returns the first existing path, or ``None`` when no comparator file is
    found for this algorithm.
    """
    if suite.lower() == "cec2011":
        candidates = [
            ref_dir / f"{ref_alg}_cec2011.csv",
            ref_dir / f"{ref_alg}_CEC2011.csv",
        ]
        for candidate in candidates:
            if candidate.exists():
                return candidate
        # Case-insensitive filesystem fallback: match any-case "cec2011" rollup.
        for candidate in sorted(ref_dir.glob(f"{ref_alg}_[cC][eE][cC]2011.csv")):
            if candidate.exists():
                return candidate
        return None

    ref_csv = ref_dir / f"{ref_alg}_{suite.lower()}_D{dim}.csv"
    if not ref_csv.exists():
        ref_csv = ref_dir / f"{ref_alg}_{suite.lower()}_D{dim:02d}.csv"
    return ref_csv if ref_csv.exists() else None


def run_statistical_analysis(
    new_summary_csv: Path,
    ref_base_dir: Path,
    suite: str,
    dim: int,
    new_label: str = "dt-gsk",
    excluded_funcs: Sequence[int] = (2,),
    zero_tol: float = 1e-8,
    extra_comparators: "dict[str, Path] | None" = None,
) -> StatAnalysisResult:
    """Run both Wilcoxon and Friedman tests against the GSK-family references.

    Parameters
    ----------
    extra_comparators : dict[str, Path], optional
        Additional ``{label: summary_csv}`` comparators to fold into the panel
        beyond the discovered GSK-family references -- e.g. the reference
        DT-GSK results from the official reference implementation, passed so the
        proposed run can be validated directly against its reference while the
        GSK-family comparisons are retained.  Each is added to the Wilcoxon
        panel (proposed vs comparator) and to the Friedman ranking.  Missing or
        empty CSVs are skipped.

    Returns
    -------
    StatAnalysisResult
        Bundle with formatted text plus the GSK-family ``FriedmanResult``
        (which also includes any ``extra_comparators``) so the runner can build
        a cross-dim summary at the end of the run.  ``str(result)`` yields the
        formatted text -- existing ``log.info(result)`` callers keep working
        unchanged.
    """
    if not HAS_SCIPY:
        return StatAnalysisResult(
            dim=dim, new_label=new_label,
            text=("\n[WARNING] scipy not installed -- statistical tests skipped.\n"
                  "  Install with: pip install scipy\n"),
            friedman_gsk_family=None,
        )

    new_means = _load_means(new_summary_csv, excluded=excluded_funcs)
    if not new_means:
        return StatAnalysisResult(
            dim=dim, new_label=new_label,
            text="\n[INFO] No results to run statistical tests on.\n",
            friedman_gsk_family=None,
        )

    if not ref_base_dir.is_dir():
        return StatAnalysisResult(
            dim=dim, new_label=new_label,
            text=f"\n[INFO] No reference directory at {ref_base_dir}\n",
            friedman_gsk_family=None,
        )

    ref_algs = sorted(p.name for p in ref_base_dir.iterdir() if p.is_dir())

    # Paper scope: GSK family only.  Restrict the discovered reference
    # directories to the canonical GSK-family comparators so the Wilcoxon
    # and Friedman panels never pick up a stray non-GSK directory.
    ref_algs = [a for a in ref_algs if a.upper() in _GSK_FAMILY_REF_NAMES]

    priority = ["gsk", "egsk", "atmals-gsk"]
    ordered = [a for a in priority if a in ref_algs]
    ordered += [a for a in ref_algs if a not in priority]

    all_alg_means: dict[str, dict[int, float]] = {new_label: new_means}
    wilcoxon_results: dict[str, WilcoxonResult] = {}

    parts: list[str] = []
    parts.append("")
    parts.append("*" * 80)
    parts.append(f"  STATISTICAL ANALYSIS -- D={dim}")
    parts.append("*" * 80)

    # Wilcoxon tests
    for ref_alg in ordered:
        ref_dir = ref_base_dir / ref_alg
        ref_csv = _resolve_comparator_csv(ref_dir, ref_alg, suite, dim)
        if ref_csv is None:
            continue
        try:
            ref_means = _load_means(ref_csv, excluded=excluded_funcs)
        except (ValueError, KeyError):
            continue
        if not ref_means:
            continue

        ref_label = ref_alg.upper()
        all_alg_means[ref_label] = ref_means

        wsr = wilcoxon_signed_rank(new_means=new_means, ref_means=ref_means, zero_tol=zero_tol)
        wilcoxon_results[ref_label] = wsr
        parts.append(format_wilcoxon_table(wsr, new_label, ref_label, dim))

    # Extra comparators (e.g. the reference DT-GSK results) -- folded into both
    # the Wilcoxon panel and the Friedman ranking for direct validation.
    extra_labels: set[str] = set()
    for label, csv_path in (extra_comparators or {}).items():
        csv_path = Path(csv_path)
        if not csv_path.exists():
            continue
        try:
            ref_means = _load_means(csv_path, excluded=excluded_funcs)
        except (ValueError, KeyError):
            continue
        if not ref_means:
            continue
        all_alg_means[label] = ref_means
        extra_labels.add(label)
        wsr = wilcoxon_signed_rank(new_means=new_means, ref_means=ref_means, zero_tol=zero_tol)
        wilcoxon_results[label] = wsr
        parts.append(format_wilcoxon_table(wsr, new_label, label, dim))

    friedman_gsk_family: FriedmanResult | None = None

    # Paper scope is GSK-family only, so there is a single Friedman panel.
    # Output order:
    #   1. GSK-family Friedman ranking (7-algo: 6 comparators + DT-GSK)
    #   2. Per-dim DT-GSK position vs nearest peer (GSK family)
    gsk_family_means = {
        name: means for name, means in all_alg_means.items()
        if name == new_label or name.upper() in _GSK_FAMILY_REF_NAMES
        or name in extra_labels
    }
    if len(gsk_family_means) >= 3:
        friedman_gsk_family = friedman_rank_test(
            alg_means=gsk_family_means, excluded=excluded_funcs, zero_tol=zero_tol,
        )
        parts.append(format_friedman_table(
            friedman_gsk_family, dim,
            panel_label=f"GSK-family Friedman ranking ({suite.upper()})",
        ))
        # 2. Peer comparison within the GSK-family panel
        parts.append(format_per_dim_peer_comparison(
            friedman_gsk_family, new_label, dim,
            panel_label="GSK family",
        ))

    return StatAnalysisResult(
        dim=dim, new_label=new_label,
        text="\n".join(parts),
        friedman_gsk_family=friedman_gsk_family,
        wilcoxon_results=wilcoxon_results,
    )
