#!/usr/bin/env python3
"""Regenerate the CEC2017 overlay contrasts JSONs with the FULL CEC2013 schema.

Round-3 review Finding B1: the CEC2017 contrasts JSONs promoted on 2026-07-13
used a reduced per-cell schema, missing the vargha_delaney_a12_full_vs_cell
block (and the Wilcoxon-variant / direction detail) the CEC2013 contrasts JSON
carries. This recomputes them to full parity from the released overlay runs
(the sanctioned strict source), then refreshes their manifest.json checksums.
Deterministic; overwrites the two CEC2017 contrasts files in place.
"""
from __future__ import annotations

import csv
import hashlib
import json
import os
import statistics
import sys
from pathlib import Path

import numpy as np
from scipy.stats import wilcoxon as scipy_wilcoxon

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import generate_ablation_matrix as gam                       # noqa: E402
from gsk_family.analysis.statistics import (                 # noqa: E402
    friedman_rank, wilcoxon_paired, holm_correction,
)

REPO = HERE.parents[1]
ABL = REPO / "benchmarks/cec_reference_results/_ablation"
OV = ABL / "overlay"
ANA = OV / "analysis"
MAN = ABL / "manifest.json"
SUITE = os.environ.get("GSK_OVL_SUITE", "cec2017")
DIMS = [int(d) for d in os.environ.get("GSK_OVL_DIMS", "50,100").split(",")]
CELLS = ["full", "no_sgsm", "no_adaptive", "no_finalpolish"]
FULL = "full"

MEANING = {
    "no_sgsm": "DIRECT SGSM contribution (the R1/R6 question)",
    "no_adaptive": "adaptive confidence-gate contribution",
    "no_finalpolish": "eigenframe final-polish contribution (AN-ABL-POLISH; bears on C2/MT-09)",
}
CELL_LABELS = {
    "full": "SGSM ON (full algorithm; interaction_graph_enabled=true)",
    "no_sgsm": "SGSM OFF (interaction_graph_enabled=false)",
    "no_adaptive": "adaptive confidence gate OFF (interaction_confidence_adaptive=false)",
    "no_finalpolish": "eigenframe final polish OFF (final_polish_enabled=false)",
}
WILCOXON_METHOD = ("gsk_family.analysis.statistics.wilcoxon_paired (normal approx "
                   "+ continuity correction, zeros dropped; frozen method used by "
                   "generate_ablation_matrix.py)")
FAMILY = "X-ABL-02 = {full vs no_sgsm, full vs no_adaptive, full vs no_finalpolish}"


def per_run_errors(cell: str, dim: int) -> dict[int, list[float]]:
    f = OV / cell / "dt-gsk" / SUITE / "summary" / "per_run.csv"
    out: dict[int, list[float]] = {}
    for r in csv.DictReader(open(f)):
        if int(r["dimension"]) == dim:
            out.setdefault(int(r["function"]), []).append(float(r["error"]))
    return out


def a12(a: list[float], b: list[float]) -> float:
    n = len(a) * len(b)
    s = sum((x < y) + 0.5 * (x == y) for x in a for y in b)
    return s / n


def build(dim: int) -> dict:
    means = gam._discover_cells(OV, SUITE, dim)           # {cell: {func: mean}}
    funcs = sorted(set.intersection(*(set(m) for m in means.values())))
    err = {c: per_run_errors(c, dim) for c in CELLS}
    data = {c: [means[c][f] for f in funcs] for c in CELLS}
    fried = friedman_rank(data)
    ranks = fried.avg_ranks
    ordering = sorted(CELLS, key=lambda c: ranks[c])
    disabled = [c for c in CELLS if c != FULL]
    full_vec = np.asarray(data[FULL], float)
    raw = {c: float(wilcoxon_paired(full_vec, np.asarray(data[c], float)).p_value)
           for c in disabled}
    holm = holm_correction([raw[c] for c in disabled], disabled)
    holm_p = {str(k["label"]): float(k["p_adjusted"]) for k in holm.comparisons}
    holm_sig = {str(k["label"]): bool(k["significant"]) for k in holm.comparisons}

    contrasts = {}
    for c in disabled:
        fmeans = [means[FULL][f] for f in funcs]
        cmeans = [means[c][f] for f in funcs]
        diffs = [fm - cm for fm, cm in zip(fmeans, cmeans)]
        n_nonzero = sum(1 for d in diffs if d != 0)
        wr = wilcoxon_paired(np.asarray(fmeans), np.asarray(cmeans))
        sw = scipy_wilcoxon(fmeans, cmeans, zero_method="wilcox")
        sz = scipy_wilcoxon(fmeans, cmeans, zero_method="zsplit")
        wins = sum(fm < cm for fm, cm in zip(fmeans, cmeans))
        ties = sum(fm == cm for fm, cm in zip(fmeans, cmeans))
        a12_pf = {str(f): a12(err[FULL][f], err[c][f]) for f in funcs}
        a12_vals = list(a12_pf.values())
        contrasts[c] = {
            "contrast": f"full vs {c}",
            "meaning": MEANING[c],
            "cell_label": CELL_LABELS[c],
            "n_funcs": len(funcs),
            "n_pairs_nonzero_diff": n_nonzero,
            "wilcoxon_repo": {
                "statistic": float(wr.statistic), "p_value": float(wr.p_value),
                "n_pairs": n_nonzero, "method": WILCOXON_METHOD},
            "wilcoxon_scipy_wilcox": {
                "statistic": float(sw.statistic), "p_value": float(sw.pvalue),
                "zero_method": "wilcox (drops zeros; matches repo)"},
            "wilcoxon_scipy_zsplit": {
                "statistic": float(sz.statistic), "p_value": float(sz.pvalue),
                "zero_method": "zsplit (preregistration text)"},
            "wtl_full_vs_cell": {
                "wins_full_better": wins, "ties": ties,
                "losses_full_worse": len(funcs) - wins - ties,
                "note": "win = full (component ON) has lower mean error than cell"},
            "direction": {
                "mean_diff_full_minus_cell": statistics.mean(diffs),
                "median_diff_full_minus_cell": statistics.median(diffs),
                "sign_convention": "negative => full better (component helps); positive => removing component helps",
                "full_mean_rank": float(ranks[FULL]), "cell_mean_rank": float(ranks[c]),
                "delta_rank_vs_full": float(ranks[c] - ranks[FULL]),
                "component_helps_directionally": bool(ranks[c] > ranks[FULL])},
            "vargha_delaney_a12_full_vs_cell": {
                "mean_a12": statistics.mean(a12_vals),
                "median_a12": statistics.median(a12_vals),
                "n_funcs_favor_full_gt_0.5": sum(1 for v in a12_vals if v > 0.5),
                "n_funcs_favor_cell_lt_0.5": sum(1 for v in a12_vals if v < 0.5),
                "per_function": {k: round(v, 4) for k, v in a12_pf.items()}},
            "holm": {
                "p_raw": raw[c], "p_holm": holm_p[c],
                "significant_at_0.05": holm_sig[c], "family": FAMILY},
        }

    return {
        "study": "X-ABL-02 SGSM-overlay ablation",
        "suite": SUITE, "dimension": dim,
        "runs": int(os.environ.get("GSK_OVL_RUNS", "51")), "n_funcs": len(funcs),
        "reference_cell": FULL, "base_seed": 20240620, "seed_policy": "unified",
        "sgsm_active_dim_note": ("CEC2017 interaction_graph_min_dim=50; D50 and D100 "
                                 "are the SGSM-active tiers for CEC2017 (D100 additionally "
                                 "runs the high-dimension controllers)."),
        "per_function_mean_source": "per_run.csv error column (authoritative).",
        "friedman_omnibus": {
            "chi2": float(fried.statistic), "p_value": float(fried.p_value),
            "n_problems": len(funcs), "n_algorithms": len(CELLS),
            "avg_ranks": {c: float(ranks[c]) for c in CELLS},
            "mean_rank_ordering_best_to_worst": ordering},
        "cell_labels": CELL_LABELS,
        "contrasts": contrasts,
    }


def main() -> int:
    for dim in DIMS:
        j = build(dim)
        p = ANA / f"overlay_contrasts_{SUITE}_D{dim}.json"
        try:
            p.chmod(0o644)
        except OSError:
            pass
        p.write_text(json.dumps(j, indent=2) + "\n", encoding="utf-8")
        a = j["contrasts"]["no_sgsm"]["vargha_delaney_a12_full_vs_cell"]["mean_a12"]
        print(f"  D{dim}: full schema written; no_sgsm mean_a12={a:.4f}, "
              f"Holm p={j['contrasts']['no_sgsm']['holm']['p_holm']:.4g}")

    # refresh the two contrasts entries' checksums in the manifest (LF, indent 1)
    if not MAN.is_file():
        print("  manifest.json absent - skipping checksum refresh (the "
              "finalization driver mints the manifest afterwards)")
        return 0
    # tolerate CRLF-materialized checkouts (core.autocrlf) and a trailing
    # newline: the file is re-serialized in canonical LF form below anyway
    raw = MAN.read_bytes().decode("utf-8").replace("\r\n", "\n")
    man = json.loads(raw)
    sha = lambda pp: hashlib.sha256(pp.read_bytes()).hexdigest()
    refreshed = []
    for f in man["files"]:
        disk = ABL / f["path"]
        if disk.is_file() and sha(disk) != f["sha256"]:
            f["sha256"] = sha(disk); f["size_bytes"] = disk.stat().st_size
            refreshed.append(f["path"])
    man["totals"] = {"files": len(man["files"]),
                     "bytes": sum(f["size_bytes"] for f in man["files"])}
    groups: dict = {}
    for f in man["files"]:
        g = groups.setdefault(f["group"], {"files": 0, "bytes": 0})
        g["files"] += 1; g["bytes"] += f["size_bytes"]
    man["groups"] = groups
    MAN.write_bytes(json.dumps(man, indent=1, ensure_ascii=False).encode("utf-8"))
    for p in (ANA / f"overlay_contrasts_{SUITE}_D50.json",
              ANA / f"overlay_contrasts_{SUITE}_D100.json"):
        try:
            p.chmod(0o444)
        except OSError:
            pass
    print(f"  manifest checksums refreshed for: {refreshed}")
    bad = [f["path"] for f in man["files"]
           if (ABL / f["path"]).is_file() and sha(ABL / f["path"]) != f["sha256"]]
    assert not bad, f"self-check FAILED: {bad[:3]}"
    print(f"  self-check OK: all {len(man['files'])} tracked checksums match disk")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
