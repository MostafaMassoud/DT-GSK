"""LaTeX table fragments for the GSK-family statistical comparison.

Builds ``\\input{}``-ready ``tabular`` fragments directly from the structured
Friedman / Wilcoxon results rather than from intermediate CSVs, so the tables
never drift from the computed statistics. Two tables are produced:

* :func:`friedman_ranks_latex` — algorithms (rows) x dimensions (columns) of
  mean Friedman ranks, with the best (lowest) rank per column bolded and an
  ``Overall`` column averaging across dimensions.
* :func:`wilcoxon_summary_latex` — the proposed algorithm versus each
  comparator per dimension: raw and Holm-adjusted p-values, win/tie/loss
  counts, Vargha-Delaney A12, and the Holm-corrected decision.

Best values are wrapped in a ``\\bestval{...}`` macro (define it in the paper
preamble, e.g. ``\\newcommand{\\bestval}[1]{\\textbf{#1}}``).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence


@dataclass(frozen=True)
class WilcoxonRow:
    """One proposed-vs-comparator Wilcoxon outcome for a single dimension.

    Attributes
    ----------
    comparator : str
        Comparator algorithm label (e.g. ``"GSK"``).
    p_value : float
        Raw two-sided Wilcoxon signed-rank p-value.
    p_holm : float
        Holm-adjusted p-value across the comparator family for this dimension.
    plus, ties, minus : int
        Win / tie / loss counts (functions where the proposed algorithm is
        better / tied / worse).
    a12 : float
        Vargha-Delaney probability of superiority (>0.5 favours the proposed
        algorithm) computed over the per-function mean errors.
    decision : str
        Holm-corrected decision: ``'+'`` (proposed better), ``'-'`` (comparator
        better), or ``'='`` (no significant difference).
    """

    comparator: str
    p_value: float
    p_holm: float
    plus: int
    ties: int
    minus: int
    a12: float
    decision: str


def _bestval(text: str) -> str:
    """Wrap *text* in the ``\\bestval{...}`` highlight macro."""
    return f"\\bestval{{{text}}}"


def _fmt_rank(value: float) -> str:
    """Format a mean rank to two decimals."""
    return f"{value:.2f}"


def _fmt_p(value: float) -> str:
    """Format a p-value to four decimals, or scientific notation when tiny."""
    if value != value:  # NaN
        return "---"
    if 0.0 < value < 1e-4:
        return f"{value:.1E}"
    return f"{value:.4f}"


def friedman_ranks_latex(
    mean_ranks_by_dim: Mapping[int, Mapping[str, float]],
    *,
    proposed: str = "dt-gsk",
) -> str:
    """Return a LaTeX ``tabular`` of mean Friedman ranks (algorithms x dimensions).

    Parameters
    ----------
    mean_ranks_by_dim : Mapping[int, Mapping[str, float]]
        ``{dim: {algorithm: mean_rank}}``. Dimensions are emitted in ascending
        order; algorithms are ordered by their overall (cross-dimension) mean
        rank, best first.
    proposed : str
        Proposed-algorithm label (retained for API symmetry; ranking order is
        purely by mean rank).

    Returns
    -------
    str
        A ``tabular`` fragment terminated by a newline.
    """
    dims = sorted(mean_ranks_by_dim)
    algorithms = {alg for ranks in mean_ranks_by_dim.values() for alg in ranks}

    overall: dict[str, float] = {}
    for alg in algorithms:
        present = [mean_ranks_by_dim[d][alg] for d in dims if alg in mean_ranks_by_dim[d]]
        overall[alg] = sum(present) / len(present) if present else float("nan")
    ordered_algs = sorted(algorithms, key=lambda a: overall[a])

    # Best (minimum) rank per dimension column and overall, for bolding.
    best_by_dim = {
        d: min(mean_ranks_by_dim[d].values()) for d in dims if mean_ranks_by_dim[d]
    }
    best_overall = min(overall.values()) if overall else float("nan")

    col_spec = "l" + "r" * (len(dims) + 1)
    lines = [f"\\begin{{tabular}}{{{col_spec}}}", "\\toprule"]
    header = ["\\textbf{Algorithm}"] + [f"\\textbf{{D{d}}}" for d in dims] + ["\\textbf{Overall}"]
    lines.append(" & ".join(header) + " \\\\")
    lines.append("\\midrule")

    for alg in ordered_algs:
        cells = [alg]
        for d in dims:
            if alg in mean_ranks_by_dim[d]:
                val = mean_ranks_by_dim[d][alg]
                text = _fmt_rank(val)
                cells.append(_bestval(text) if val == best_by_dim.get(d) else text)
            else:
                cells.append("---")
        ov = overall[alg]
        ov_text = _fmt_rank(ov) if ov == ov else "---"
        cells.append(_bestval(ov_text) if ov == best_overall else ov_text)
        lines.append(" & ".join(cells) + " \\\\")

    lines.append("\\bottomrule")
    lines.append("\\end{tabular}")
    return "\n".join(lines) + "\n"


def wilcoxon_summary_latex(
    rows_by_dim: Mapping[int, Sequence[WilcoxonRow]],
    *,
    proposed: str = "dt-gsk",
) -> str:
    """Return a LaTeX ``tabular`` summarising Wilcoxon results per dimension.

    Each dimension contributes seven columns: ``p``, ``p_Holm``, ``+``, ``=``,
    ``-``, ``A12``, ``Dec.``. Comparator rows are emitted in the order they
    appear in the first dimension's sequence.

    Parameters
    ----------
    rows_by_dim : Mapping[int, Sequence[WilcoxonRow]]
        ``{dim: [WilcoxonRow, ...]}``.
    proposed : str
        Proposed-algorithm label, used only in the table comment header.

    Returns
    -------
    str
        A ``tabular`` fragment terminated by a newline.
    """
    dims = sorted(rows_by_dim)
    # Comparator order from the first populated dimension.
    comparators: list[str] = []
    for d in dims:
        if rows_by_dim[d]:
            comparators = [r.comparator for r in rows_by_dim[d]]
            break
    indexed = {d: {r.comparator: r for r in rows_by_dim[d]} for d in dims}

    n_dims = len(dims)
    lines = [f"% Wilcoxon signed-rank: {proposed} vs GSK-family comparators"]
    lines.append("\\begin{tabular}{l" + "rrcccrc" * n_dims + "}")
    lines.append("\\toprule")
    dim_header = " & ".join(f"\\multicolumn{{7}}{{c}}{{\\textbf{{D{d}}}}}" for d in dims)
    lines.append(f"\\textbf{{Comparator}} & {dim_header} \\\\")
    sub = " & ".join(
        "$p$ & $p_{\\text{Holm}}$ & $+$ & $=$ & $-$ & $A_{12}$ & Dec."
        for _ in dims
    )
    lines.append(f" & {sub} \\\\")
    lines.append("\\midrule")

    for comp in comparators:
        cells = [comp]
        for d in dims:
            row = indexed[d].get(comp)
            if row is None:
                cells.extend(["---"] * 7)
                continue
            cells.extend([
                _fmt_p(row.p_value),
                _fmt_p(row.p_holm),
                str(row.plus),
                str(row.ties),
                str(row.minus),
                f"{row.a12:.3f}",
                row.decision,
            ])
        lines.append(" & ".join(cells) + " \\\\")

    lines.append("\\bottomrule")
    lines.append("\\end{tabular}")
    return "\n".join(lines) + "\n"
