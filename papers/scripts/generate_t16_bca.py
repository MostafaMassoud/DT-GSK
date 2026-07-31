"""Generate the ``T16_bca.tex`` BCa confidence-interval companion to T16.

T16 reports the per-dimension Friedman mean rank for each GSK-family
algorithm on CEC2017 (29 functions, F2 excluded).  This companion table
reports the 95 % bootstrap bias-corrected-and-accelerated (BCa) CI on
those mean ranks, via ``n_boot = 10 000`` resamples of the 29
function-level ranks for each (algorithm, dimension) cell.

The BCa routine lives in :func:`gsk_family.analysis.statistics.bootstrap_bca_ci`.

Phase 7 evidence lock: per-function mean errors are read EXCLUSIVELY
from the frozen Phase 6 analysis bundle
``papers/analysis/rel-2026-07-10-262fc16c9/cec2017/descriptive_stats_cec2017_D<dim>.csv``
(the same authoritative source that produced the staged T16 export).
No ``results/`` staging path and no ``benchmarks/`` summary path is
read.  A missing bundle file is a hard failure, never a silent skip.

The rank-CI scheme (per-function midrank Friedman ranks + seeded BCa
bootstrap with ``BASE_SEED``) is a distinct inspected analysis and is
kept unchanged.

Output: ``papers/tables/T16_bca.tex`` (``longtable``-free plain
``tabular`` so it can be included under ``\\input{tables/T16_bca}``).

Usage::

    python papers/scripts/generate_t16_bca.py
"""
from __future__ import annotations

import csv
import os
import sys
from pathlib import Path

import numpy as np

SCRIPT_DIR = Path(__file__).resolve().parent
PAPER_DIR = SCRIPT_DIR.parent
PROJECT_ROOT = PAPER_DIR.parent
# The package lives under src/ (src-layout); fall back to it when the
# project is not pip-installed in the current environment.
_SRC = PROJECT_ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from gsk_family.analysis.statistics import bootstrap_bca_ci  # noqa: E402

# Frozen Phase 6 analysis bundle (sole admissible empirical input).
# SE-046: this defaulted to rel-2026-07-16-78f075cb0, a SUPERSEDED release, while the
# manuscript ships rel-2026-07-20-67d9345f9.  Re-pointed 2026-07-22 after verifying that
# both releases reproduce the shipped T16_bca.tex byte-identically -- the CEC2017
# per-function mean errors, and therefore the midranks, are unchanged between them, so
# no printed value moves as a result of this change.
RELEASE_ID = os.environ.get("GSK_REL_ID", "rel-2026-07-20-67d9345f9")
BUNDLE_DIR = PAPER_DIR / "analysis" / RELEASE_ID / "cec2017"

OUT_TEX = PAPER_DIR / "tables" / "T16_bca.tex"
# SE-046: these rank intervals existed ONLY inside the typeset table -- no CSV and no
# machine-readable row anywhere, so a reader could not check them without retyping the
# LaTeX.  Note the released bca_ci_*.csv files hold a DIFFERENT estimand: BCa intervals
# on per-function mean DIFFERENCES, not on Friedman mean ranks.
OUT_CSV = PAPER_DIR / "analysis" / RELEASE_ID / "cec2017" / "bca_rank_ci_cec2017.csv"

DIMS = [10, 30, 50, 100]

# P1 panel order (pre-registered, binding): six comparators then DT-GSK.
ALGS = ["gsk", "agsk", "apgsk", "fdb-agsk", "atmals-gsk", "egsk", "dt-gsk"]

# CEC2017 exclusion protocol: F2 is excluded (29 functions remain).
EXCLUDED_FUNCS = {2}

# Paper-facing display labels (Phase 4 terminology glossary: eGSK
# capitalization per CR-0003; FDB-AGSK hyphenated).
DISPLAY_NAME = {
    "dt-gsk": "DT-GSK",
    "gsk": "GSK",
    "agsk": "AGSK",
    "apgsk": "APGSK",
    "fdb-agsk": r"\fdbagsk{}",
    "egsk": r"\egsk{}",
    "atmals-gsk": "ATMALS-GSK",
}

# Deterministic PRNG seed so the camera-ready numbers are reproducible.
BASE_SEED = 20260422


def _load_mean_errors(dim: int) -> tuple[list[int], dict[str, dict[int, float]]]:
    """Load per-function mean errors from the frozen analysis bundle.

    Returns
    -------
    (funcs, means) where ``funcs`` is the sorted list of function IDs
    common to all P1 panel algorithms (F2 excluded) and ``means`` maps
    algorithm -> {function -> mean error}.
    """
    path = BUNDLE_DIR / f"descriptive_stats_cec2017_D{dim}.csv"
    if not path.is_file():
        raise SystemExit(
            f"HARD FAIL: required Phase 6 bundle input missing: {path}. "
            "T16_bca may only be generated from the frozen analysis "
            f"bundle {RELEASE_ID}; no fallback source is admissible."
        )
    means: dict[str, dict[int, float]] = {a: {} for a in ALGS}
    with path.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            alg = row["algorithm"].strip()
            if alg not in means:
                continue
            func = int(row["function"])
            if func in EXCLUDED_FUNCS:
                continue
            means[alg][func] = float(row["mean"])

    missing = [a for a in ALGS if not means[a]]
    if missing:
        raise SystemExit(
            f"HARD FAIL: bundle file {path} has no rows for panel "
            f"algorithm(s) {missing}; refusing to emit a partial T16_bca."
        )
    common = set.intersection(*(set(means[a]) for a in ALGS))
    if not common:
        raise SystemExit(
            f"HARD FAIL: no common function IDs across the panel in {path}."
        )
    return sorted(common), means


def _per_function_ranks(matrix: np.ndarray) -> np.ndarray:
    """Rank each row of ``matrix`` (lower = better), with midrank ties.

    Parameters
    ----------
    matrix : np.ndarray of shape (n_funcs, n_algs)
        Mean errors per function, per algorithm.

    Returns
    -------
    np.ndarray of the same shape
        Per-function ranks (1 = best).  Tied cells receive the average
        of the tied rank positions.
    """
    n, k = matrix.shape
    ranks = np.empty_like(matrix, dtype=np.float64)
    for i in range(n):
        row = matrix[i]
        order = np.argsort(row)
        rvals = np.empty(k, dtype=np.float64)
        rvals[order] = np.arange(1, k + 1, dtype=np.float64)
        j = 0
        while j < k:
            jj = j
            while jj < k and row[order[jj]] == row[order[j]]:
                jj += 1
            if jj > j + 1:
                avg = float(np.mean(np.arange(j + 1, jj + 1)))
                for idx in range(j, jj):
                    rvals[order[idx]] = avg
            j = jj
        ranks[i] = rvals
    return ranks


def _compute_bca_for_dim(dim: int) -> dict[str, tuple[float, float, float]]:
    """Compute BCa 95 % CIs on Friedman mean ranks for one dimension.

    Returns
    -------
    dict mapping algorithm display name -> (mean_rank, ci_lo, ci_hi)
    """
    funcs, means = _load_mean_errors(dim)

    matrix = np.array(
        [[means[a][f] for a in ALGS] for f in funcs],
        dtype=np.float64,
    )
    ranks = _per_function_ranks(matrix)

    out: dict[str, tuple[float, float, float]] = {}
    for i, alg in enumerate(ALGS):
        rng = np.random.default_rng(BASE_SEED + dim * 7 + i)
        lo, hi, theta = bootstrap_bca_ci(
            ranks[:, i], n_boot=10000, alpha=0.05, rng=rng,
        )
        out[DISPLAY_NAME[alg]] = (float(theta), float(lo), float(hi))
    return out


def _render_tex(all_results: dict[int, dict[str, tuple[float, float, float]]]) -> str:
    """Render the companion as a plain LaTeX ``tabular``.

    Columns: Algorithm | D=10 mean [lo, hi] | D=30 mean [lo, hi] | ...
    """
    # Keep the row order stable across dims (P1 panel order)
    display_rows = [DISPLAY_NAME[a] for a in ALGS]

    # Headers
    header_top = (
        "\\textbf{Algorithm} & "
        + " & ".join(f"\\textbf{{D{d}}}" for d in DIMS)
        + " \\\\"
    )

    lines: list[str] = []
    col_spec = "l" + "c" * len(DIMS)
    lines.append("\\begin{tabular}{" + col_spec + "}")
    lines.append("\\toprule")
    lines.append(header_top)
    lines.append(
        "            & "
        + " & ".join("Mean [95\\% BCa CI]" for _ in DIMS)
        + " \\\\"
    )
    lines.append("\\midrule")

    for alg_label in display_rows:
        cells: list[str] = [alg_label]
        for d in DIMS:
            cell = all_results.get(d, {}).get(alg_label)
            if cell is None:
                cells.append("N/A")
                continue
            mean, lo, hi = cell
            cells.append(f"{mean:.2f} [{lo:.2f}, {hi:.2f}]")
        lines.append(" & ".join(cells) + " \\\\")

    lines.append("\\bottomrule")
    lines.append("\\end{tabular}")
    return "\n".join(lines) + "\n"


def main() -> None:
    all_results: dict[int, dict[str, tuple[float, float, float]]] = {}
    for d in DIMS:
        res = _compute_bca_for_dim(d)
        all_results[d] = res
        print(f"D={d}: {len(res)} algorithms")

    tex = _render_tex(all_results)
    OUT_TEX.parent.mkdir(parents=True, exist_ok=True)
    OUT_TEX.write_text(tex, encoding="utf-8")
    print(f"\nwrote {OUT_TEX}")

    # SE-046: the same numbers, machine-readable.  Written alongside the release's
    # other analysis CSVs so it is discoverable where a reader would look for it.
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUT_CSV.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh, lineterminator="\n")
        writer.writerow(["suite", "dimension", "algorithm", "mean_rank",
                         "ci_low", "ci_high", "n_functions", "B", "alpha",
                         "seed_scheme", "estimand", "release_id"])
        for d in DIMS:
            for alg in ALGS:
                theta, lo, hi = all_results[d][DISPLAY_NAME[alg]]
                writer.writerow(["cec2017", d, alg, f"{theta:.6f}",
                                 f"{lo:.6f}", f"{hi:.6f}", 29, 10000, 0.05,
                                 f"default_rng({BASE_SEED} + dim*7 + p1_index)",
                                 "friedman_mean_rank", RELEASE_ID])
    print(f"wrote {OUT_CSV}  ({len(DIMS) * len(ALGS)} rows)")


if __name__ == "__main__":
    main()
