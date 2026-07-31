#!/usr/bin/env python3
"""Effect sizes + compute cost for the ISM-overlay isolation (READ-ONLY).

Complements generate_ablation_matrix.py (which emits Friedman rank / paired
Wilcoxon / Holm) with the two quantities Supplement Table A17 also reports:
Vargha-Delaney A12 (full vs each single-toggle cell, per-function, averaged over
the raw paired runs) and the ISM compute overhead (full vs no_sgsm mean per-run
wall time). Deterministic; reads the promoted overlay evidence and writes one
CSV under papers/analysis/ablation_overlay/.

Usage: python papers/scripts/ablation_overlay_effects.py
"""
from __future__ import annotations
import csv
import statistics
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OV = ROOT / "benchmarks/cec_reference_results/_ablation/overlay"
OUT = ROOT / "papers/analysis/ablation_overlay"
SUITE = os.environ.get("GSK_OVL_SUITE", "cec2017")
DIMS = [int(d) for d in os.environ.get("GSK_OVL_DIMS", "50,100").split(",")]
CELLS = ["no_sgsm", "no_adaptive", "no_finalpolish"]


def _per_run(cell, dim, col):
    f = OV / cell / "dt-gsk" / SUITE / "summary" / "per_run.csv"
    out = {}
    for r in csv.DictReader(open(f)):
        if int(r["dimension"]) == dim:
            out.setdefault(int(r["function"]), []).append(float(r[col]))
    return out


def a12(a, b):
    """P(a<b) + 0.5 P(a==b): prob a random 'a' error beats a random 'b' error.
    a = full runs, b = cell runs; >0.5 => full (ISM on) better (lower error)."""
    n = len(a) * len(b)
    s = sum((x < y) + 0.5 * (x == y) for x in a for y in b)
    return s / n


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    out_path = OUT / f"ism_isolation_effects_{SUITE}.csv"
    rows = []
    for dim in DIMS:
        full_err = _per_run("full", dim, "error")
        full_rt = statistics.mean(v for vs in _per_run("full", dim, "runtime_seconds").values() for v in vs)
        for cell in CELLS:
            cell_err = _per_run(cell, dim, "error")
            a12_vals = [a12(full_err[fn], cell_err[fn]) for fn in full_err]
            overhead = ""
            if cell == "no_sgsm":
                cell_rt = statistics.mean(v for vs in _per_run(cell, dim, "runtime_seconds").values() for v in vs)
                overhead = f"{100 * (full_rt / cell_rt - 1):+.1f}"
            rows.append({"suite": SUITE, "dimension": dim, "cell": cell,
                         "n_funcs": len(a12_vals),
                         "mean_a12": round(statistics.mean(a12_vals), 4),
                         "ism_runtime_overhead_pct": overhead})
    with out_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    for r in rows:
        oh = f" | ISM overhead {r['ism_runtime_overhead_pct']}%" if r["ism_runtime_overhead_pct"] else ""
        print(f"  D{r['dimension']} full vs {r['cell']:15s}: mean A12={r['mean_a12']}{oh}")
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
