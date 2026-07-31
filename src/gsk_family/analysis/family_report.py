"""GSK-family statistical report orchestration.

Ties the data layer (:mod:`gsk_family.analysis.result_loader`), the vendored
statistical core (:mod:`gsk_family.analysis.statistical_tests`), the effect-size
and multiple-comparison helpers (:mod:`gsk_family.analysis.statistics`), and the
publication figure/table generators into a single paper-grade report for the
proposed algorithm (``dt-gsk`` by default) versus the GSK-family comparators.

For each requested dimension it builds the 7-algorithm Friedman panel (the
proposed algorithm plus the committed GSK-family reference comparators) and the
pairwise Wilcoxon signed-rank tests, applies a per-dimension Holm correction
across the comparator family, and emits:

* a concatenated text report (``<suite>_statistical_report.txt``),
* a Friedman mean-rank CSV (``<suite>_friedman_ranks.csv``),
* LaTeX fragments for the rank and Wilcoxon-summary tables, and
* per-dimension Nemenyi critical-difference and rank-chart figures.

All algorithms — the proposed method included — are read from the committed
reference panel (``benchmarks/cec_reference_results/<suite>/<optimizer>/``)
first; a locally reproduced run under
``results/_run_all/<proposed>/<suite>/summary/`` is used only as a fallback
for cells the reference tree does not carry.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass, field
from pathlib import Path
from typing import Sequence

from . import result_loader
from .latex_tables import WilcoxonRow, friedman_ranks_latex, wilcoxon_summary_latex
from .statistics import holm_correction, vargha_delaney
from .statistical_tests import StatAnalysisResult, run_statistical_analysis

DEFAULT_RESULTS_ROOT = Path("results/_run_all")
DEFAULT_REFERENCE_ROOT = Path("benchmarks/cec_reference_results")
DEFAULT_PROPOSED = "dt-gsk"
DEFAULT_EXCLUDED_FUNCS: tuple[int, ...] = (2,)


@dataclass
class DimResult:
    """Per-dimension analysis bundle.

    Attributes
    ----------
    dim : int
        Problem dimension.
    stat_result : StatAnalysisResult
        Full vendored result (text report + Friedman panel + Wilcoxon dict).
    mean_ranks : dict[str, float] | None
        ``{algorithm: mean_rank}`` from the Friedman panel, or ``None`` when the
        panel could not be built (fewer than three algorithms with data).
    n_funcs : int
        Number of benchmark functions used for the Friedman ranking.
    wilcoxon_rows : list[WilcoxonRow]
        Holm-corrected per-comparator rows for the LaTeX summary table.
    """

    dim: int
    stat_result: StatAnalysisResult
    mean_ranks: dict[str, float] | None
    n_funcs: int
    wilcoxon_rows: list[WilcoxonRow] = field(default_factory=list)


def _holm_rows(stat_result: StatAnalysisResult, alpha: float = 0.05) -> list[WilcoxonRow]:
    """Build Holm-corrected :class:`WilcoxonRow` entries from a stat result."""
    wilcoxon = stat_result.wilcoxon_results
    if not wilcoxon:
        return []

    labels = list(wilcoxon)
    p_values = [wilcoxon[label].p_value for label in labels]
    holm = holm_correction(p_values, labels, alpha=alpha)
    adjusted = {c["label"]: c for c in holm.comparisons}

    rows: list[WilcoxonRow] = []
    for label in labels:
        result = wilcoxon[label]
        corrected = adjusted.get(label, {})
        p_holm = float(corrected.get("p_adjusted", result.p_value))
        significant = bool(corrected.get("significant", False))
        if significant:
            decision = "+" if result.R_plus >= result.R_minus else "-"
        else:
            decision = "="

        if result.per_func:
            new_vec = [t[1] for t in result.per_func]
            ref_vec = [t[2] for t in result.per_func]
            a12 = vargha_delaney(new_vec, ref_vec).a12
        else:
            a12 = float("nan")

        rows.append(
            WilcoxonRow(
                comparator=label,
                p_value=result.p_value,
                p_holm=p_holm,
                plus=result.wins,
                ties=result.ties,
                minus=result.losses,
                a12=a12,
                decision=decision,
            )
        )
    return rows


def analyze_family(
    suite: str,
    dims: Sequence[int],
    *,
    results_root: Path | None = None,
    reference_root: Path | None = None,
    proposed: str = DEFAULT_PROPOSED,
    excluded_funcs: Sequence[int] | None = None,
    alpha: float = 0.05,
) -> list[DimResult]:
    """Run the family statistical analysis for each dimension.

    Parameters
    ----------
    suite : str
        Benchmark suite (e.g. ``"CEC2017"``).
    dims : sequence of int
        Dimensions to analyse.
    results_root : Path, optional
        Root containing the reproduced ``<optimizer>/<suite>/summary`` trees;
        defaults to ``results/_run_all``.
    reference_root : Path, optional
        Root of the committed reference tables; defaults to
        ``benchmarks/cec_reference_results``.
    proposed : str
        Proposed-algorithm id whose reproduced run anchors the comparison.
    excluded_funcs : sequence of int, optional
        Function IDs to drop. When ``None`` (default) the exclusion is resolved
        per suite from ``result_loader.SUITE_EXCLUDED_FUNCS`` (CEC2017 drops F2;
        CEC2011/CEC2013 drop nothing).
    alpha : float
        Significance level for the Holm correction.

    Returns
    -------
    list[DimResult]
        One entry per dimension that had a reproduced proposed-algorithm summary
        with at least one function; dimensions without data are skipped.
    """
    results_root = Path(results_root) if results_root is not None else DEFAULT_RESULTS_ROOT
    reference_root = Path(reference_root) if reference_root is not None else DEFAULT_REFERENCE_ROOT
    ref_base_dir = reference_root / suite.lower()
    if excluded_funcs is None:
        excluded_funcs = tuple(
            sorted(result_loader.SUITE_EXCLUDED_FUNCS.get(suite.upper(), DEFAULT_EXCLUDED_FUNCS))
        )

    out: list[DimResult] = []
    for dim in dims:
        # The paper's data source of truth is the committed reference panel
        # (benchmarks/cec_reference_results/<suite>/<proposed>/). Load the
        # proposed method from there first -- same source as the comparators --
        # and fall back to a locally reproduced run only if the reference tree
        # lacks this cell.
        new_csv = result_loader._reference_csv_path(proposed, suite, dim, reference_root)
        if new_csv is None:
            new_csv = result_loader._reproduced_csv_path(proposed, suite, dim, results_root)
        if new_csv is None:
            continue
        stat_result = run_statistical_analysis(
            new_csv, ref_base_dir, suite, dim, proposed,
            excluded_funcs=tuple(excluded_funcs),
        )
        friedman = stat_result.friedman_gsk_family
        mean_ranks = dict(friedman.mean_ranks) if friedman is not None else None
        n_funcs = len(friedman.func_ids) if friedman is not None else 0
        rows = _holm_rows(stat_result, alpha=alpha)
        out.append(
            DimResult(
                dim=dim,
                stat_result=stat_result,
                mean_ranks=mean_ranks,
                n_funcs=n_funcs,
                wilcoxon_rows=rows,
            )
        )
    return out


def _write_friedman_csv(path: Path, dim_results: list[DimResult]) -> None:
    """Write the Algorithm x dimension mean-rank CSV (with an Overall column)."""
    dims = [r.dim for r in dim_results if r.mean_ranks]
    algs: list[str] = []
    for r in dim_results:
        if not r.mean_ranks:
            continue
        for alg in r.mean_ranks:
            if alg not in algs:
                algs.append(alg)

    ranks_by_dim = {r.dim: r.mean_ranks for r in dim_results if r.mean_ranks}
    overall: dict[str, float] = {}
    for alg in algs:
        present = [ranks_by_dim[d][alg] for d in dims if alg in ranks_by_dim[d]]
        overall[alg] = sum(present) / len(present) if present else float("nan")
    ordered = sorted(algs, key=lambda a: overall[a])

    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["Algorithm"] + [f"MeanRank_D{d}" for d in dims] + ["Overall_MeanRank"])
        for alg in ordered:
            row = [alg]
            for d in dims:
                val = ranks_by_dim[d].get(alg)
                row.append(f"{val:.4f}" if val is not None else "N/A")
            ov = overall[alg]
            row.append(f"{ov:.4f}" if ov == ov else "N/A")
            writer.writerow(row)


def write_report(
    dim_results: list[DimResult],
    out_dir: Path,
    suite: str,
    *,
    proposed: str = DEFAULT_PROPOSED,
    make_figures: bool = True,
) -> list[Path]:
    """Write text, CSV, LaTeX, and figure artifacts for a family analysis.

    Parameters
    ----------
    dim_results : list[DimResult]
        Output of :func:`analyze_family`.
    out_dir : Path
        Destination directory (created if absent).
    suite : str
        Benchmark suite label used in file names and titles.
    proposed : str
        Proposed-algorithm label used for figure highlighting.
    make_figures : bool
        When True, render per-dimension Nemenyi CD diagrams and rank charts.

    Returns
    -------
    list[Path]
        All written artifact paths, in creation order.
    """
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    suite_lower = suite.lower()
    written: list[Path] = []

    # 1. Text report (concatenated per-dimension blocks).
    text_path = out_dir / f"{suite_lower}_statistical_report.txt"
    text_path.write_text(
        "\n".join(r.stat_result.text for r in dim_results) + "\n",
        encoding="utf-8",
    )
    written.append(text_path)

    # 2. Friedman mean-rank CSV.
    if any(r.mean_ranks for r in dim_results):
        csv_path = out_dir / f"{suite_lower}_friedman_ranks.csv"
        _write_friedman_csv(csv_path, dim_results)
        written.append(csv_path)

        # 3. LaTeX fragments.
        ranks_by_dim = {r.dim: r.mean_ranks for r in dim_results if r.mean_ranks}
        ranks_tex = out_dir / f"{suite_lower}_friedman_ranks.tex"
        ranks_tex.write_text(friedman_ranks_latex(ranks_by_dim, proposed=proposed), encoding="utf-8")
        written.append(ranks_tex)

        rows_by_dim = {r.dim: r.wilcoxon_rows for r in dim_results if r.wilcoxon_rows}
        if rows_by_dim:
            wil_tex = out_dir / f"{suite_lower}_wilcoxon_summary.tex"
            wil_tex.write_text(wilcoxon_summary_latex(rows_by_dim, proposed=proposed), encoding="utf-8")
            written.append(wil_tex)

    # 4. Figures (lazy matplotlib import so pure-stats runs stay light).
    if make_figures and any(r.mean_ranks for r in dim_results):
        from . import figures

        fig_dir = out_dir / "figures"
        for r in dim_results:
            if not r.mean_ranks:
                continue
            cd_path = fig_dir / f"nemenyi_cd_{suite_lower}_D{r.dim}.png"
            figures.render_cd_diagram(
                r.mean_ranks, n_funcs=r.n_funcs, out_path=cd_path,
                suite=suite, dim=r.dim, proposed=proposed,
            )
            written.append(cd_path)

            rank_path = fig_dir / f"friedman_ranks_{suite_lower}_D{r.dim}.png"
            figures.render_rank_chart(
                r.mean_ranks, out_path=rank_path,
                title=f"Friedman Mean Ranks ({suite}, D={r.dim})",
                proposed=proposed,
            )
            written.append(rank_path)

    return written


def generate_family_report(
    suite: str,
    dims: Sequence[int],
    out_dir: Path,
    *,
    results_root: Path | None = None,
    reference_root: Path | None = None,
    proposed: str = DEFAULT_PROPOSED,
    excluded_funcs: Sequence[int] | None = None,
    make_figures: bool = True,
    alpha: float = 0.05,
) -> tuple[list[DimResult], list[Path]]:
    """Run :func:`analyze_family` then :func:`write_report` and return both.

    Returns
    -------
    tuple[list[DimResult], list[Path]]
        The per-dimension results and the written artifact paths.
    """
    dim_results = analyze_family(
        suite, dims,
        results_root=results_root, reference_root=reference_root,
        proposed=proposed, excluded_funcs=excluded_funcs, alpha=alpha,
    )
    written = write_report(
        dim_results, out_dir, suite, proposed=proposed, make_figures=make_figures,
    )
    return dim_results, written
