# -*- coding: utf-8 -*-
"""Phase 4 / M-026: tie-corrected Friedman + Iman-Davenport, re-analysis only.

Reads the FROZEN per-function means from the promoted analysis bundle, reproduces
the published (uncorrected) statistic as a control, then applies the standard tie
correction and reports whether ANY decision at alpha=0.05 changes.

    C          = 1 - sum_i sum_g (t^3 - t) / ( N (k^3 - k) )
    chi2_corr  = chi2_uncorr / C            (C <= 1  =>  chi2_corr >= chi2_uncorr)
    F_ID       = (N-1) chi2 / ( N(k-1) - chi2 ),  df=(k-1, (k-1)(N-1))
"""
import csv, math
from collections import defaultdict
from pathlib import Path
import numpy as np
from scipy import stats as sps

B = (Path(__file__).resolve().parents[3] / "papers" / "analysis"
     / "rel-2026-07-16-78f075cb0")
ALPHA = 0.05

def load_matrix(desc_csv):
    """-> (algs, matrix[n_functions, k]) of per-function mean error."""
    by_fn = defaultdict(dict)
    for r in csv.DictReader(desc_csv.open(encoding="utf-8")):
        try:
            by_fn[r["function"]][r["algorithm"]] = float(r["mean"])
        except (KeyError, ValueError):
            continue
    fns = sorted(by_fn, key=lambda x: int(x) if x.isdigit() else x)
    algs = sorted({a for v in by_fn.values() for a in v})
    rows = [[by_fn[f][a] for a in algs] for f in fns if all(a in by_fn[f] for a in algs)]
    return algs, np.asarray(rows, dtype=float)

def friedman(matrix):
    n, k = matrix.shape
    ranks = np.vstack([sps.rankdata(row, method="average") for row in matrix])
    avg = ranks.mean(axis=0)
    chi2 = (12.0 * n / (k * (k + 1))) * np.sum((avg - (k + 1) / 2.0) ** 2)
    # tie correction
    tie_term = 0.0
    for row in matrix:
        _, counts = np.unique(row, return_counts=True)
        tie_term += float(np.sum(counts ** 3 - counts))
    C = 1.0 - tie_term / (n * (k ** 3 - k))
    chi2_c = chi2 / C if C > 0 else float("nan")
    def idf(x):
        den = n * (k - 1) - x
        if den <= 0: return float("inf"), 0.0
        f = (n - 1) * x / den
        return f, float(sps.f.sf(f, k - 1, (k - 1) * (n - 1)))
    f_u, p_fu = idf(chi2)
    f_c, p_fc = idf(chi2_c)
    return dict(n=n, k=k, avg=avg, C=C, tie_term=tie_term,
                chi2=chi2, p_chi2=float(sps.chi2.sf(chi2, k - 1)),
                chi2_c=chi2_c, p_chi2_c=float(sps.chi2.sf(chi2_c, k - 1)),
                f=f_u, p_f=p_fu, f_c=f_c, p_f_c=p_fc)

def published(fr_csv):
    for r in csv.DictReader(fr_csv.open(encoding="utf-8")):
        return float(r["friedman_chi2"]), float(r["iman_davenport_F"]), float(r["p_value"])
    return None

PANELS = []
for d in (10, 30, 50, 100):
    PANELS.append((f"CEC2017 D{d}", B/"cec2017"/f"descriptive_stats_cec2017_D{d}.csv",
                   B/"cec2017"/f"friedman_ranks_cec2017_D{d}.csv"))
for d in (10, 30, 50):
    PANELS.append((f"CEC2013 D{d}", B/"cec2013"/f"descriptive_stats_cec2013_D{d}.csv",
                   B/"cec2013"/f"friedman_ranks_cec2013_D{d}.csv"))
PANELS.append(("CEC2011", B/"cec2011"/"descriptive_stats_cec2011.csv",
               B/"cec2011"/"friedman_ranks_cec2011.csv"))

print(f"{'panel':14s} {'N':>3s} {'k':>2s} {'C':>8s} {'chi2_unc':>10s} {'chi2_tie':>10s} "
      f"{'p_unc':>10s} {'p_tie':>10s}  decision")
print("-" * 92)
flips, checked = [], 0
for name, desc, fr in PANELS:
    if not desc.exists():
        print(f"{name:14s}  -- descriptive stats not found: {desc.name}")
        continue
    algs, M = load_matrix(desc)
    if M.size == 0:
        print(f"{name:14s}  -- empty matrix"); continue
    r = friedman(M)
    checked += 1
    pub = published(fr) if fr.exists() else None
    ctrl = ""
    if pub:
        ok = math.isclose(r["chi2"], pub[0], rel_tol=1e-6)
        ctrl = "control-OK" if ok else f"CONTROL-MISMATCH(pub={pub[0]:.6g})"
    dec_u = "sig" if r["p_f"] < ALPHA else "ns"
    dec_c = "sig" if r["p_f_c"] < ALPHA else "ns"
    flag = "" if dec_u == dec_c else "  <<< DECISION FLIP"
    if dec_u != dec_c:
        flips.append((name, dec_u, dec_c))
    print(f"{name:14s} {r['n']:3d} {r['k']:2d} {r['C']:8.6f} {r['chi2']:10.4f} "
          f"{r['chi2_c']:10.4f} {r['p_f']:10.3e} {r['p_f_c']:10.3e}  {dec_u}->{dec_c} {ctrl}{flag}")

print("-" * 92)
print(f"panels checked: {checked}   decision flips at alpha={ALPHA}: {len(flips)}")
if flips:
    print("  !!! STOP CONDITION: ", flips)
else:
    print("  No significance flip. Mean ranks are unchanged by construction")
    print("  (tie correction rescales the statistic only), so no rank or sign can flip.")
