"""Regression: gsk-stats CEC2020 Friedman panels reproduce the paper's ranks.

The paper's frozen CEC2020 bundle ranks per-function MEANS with midranks, and
so does gsk-stats, so N and every mean rank must agree to the bundle's printed
precision. Wilcoxon p-values are NOT compared: the bundle uses exact sign-flip
enumeration after discarding |d| < 1e-8, while gsk-stats uses scipy
zero_method='zsplit', so they legitimately differ where ties exist.

CEC2013LSGO is not pinned here: the paper pools D=1000 and D=905 into one
15-function panel (phase6b), while gsk-stats ranks one dimension at a time.
"""

from __future__ import annotations

import csv
from pathlib import Path

import pytest

from gsk_family.analysis.family_report import analyze_family

_ROOT = Path(__file__).resolve().parents[2]
_REF = _ROOT / "benchmarks" / "cec_reference_results"
_CEC2020 = _ROOT / "papers" / "analysis" / "cec2020-rel-2026-07-29-5867abe1e" / "cec2020"


def _paper(path: Path) -> tuple[int, dict[str, float]]:
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    return int(rows[0]["n_blocks"]), {r["algorithm"]: float(r["mean_rank"]) for r in rows}


def _label(alg: str) -> str:
    return alg if alg == "dt-gsk" else alg.upper()


@pytest.mark.parametrize("dim", [5, 10, 15, 20])
def test_cec2020_friedman_panel_matches_frozen_bundle(tmp_path, dim):
    paper_csv = _CEC2020 / f"friedman_ranks_cec2020_{dim}.csv"
    if not paper_csv.is_file() or not (_REF / "cec2020").is_dir():
        pytest.skip("frozen bundle or evidence tree not present (code-only clone)")
    n_paper, ranks_paper = _paper(paper_csv)
    [r] = analyze_family("CEC2020", [dim], reference_root=_REF, results_root=tmp_path / "none")
    assert r.n_funcs == n_paper
    assert set(r.mean_ranks) == {_label(a) for a in ranks_paper}
    for alg, rank in ranks_paper.items():
        assert r.mean_ranks[_label(alg)] == pytest.approx(rank, rel=1e-6)
