#!/usr/bin/env python3
"""Post-hoc robustness of the primary CEC2017 conclusions (READ-ONLY, deterministic).

Supplement Section S2 sensitivity analysis. Two checks, both computed from the
frozen per-run CSVs of the evidence release (no new runs, nothing in the frozen
release modified):

  (1) Endpoint invariance -- recompute the Friedman mean ranks under a median
      endpoint and a log10-error endpoint (floored at 1e-8) and confirm
      DT-GSK's rank position is unchanged versus the pre-registered raw-error
      endpoint.
  (2) Exact inference -- replace the normal-approximation Wilcoxon signed-rank
      p-value with an exact sign-flip permutation of the signed-rank statistic
      (fixed seed) and confirm every Holm-adjusted alpha=0.05 pairwise decision
      is preserved.

The script first REPRODUCES the frozen primary Friedman ranks as a validation
gate, then writes two result CSVs under papers/analysis/posthoc_robustness/.

Usage:  python papers/scripts/posthoc_robustness_cec2017.py
"""
from __future__ import annotations
import numpy as np
import os
import pandas as pd
from pathlib import Path
from scipy.stats import wilcoxon, rankdata

ROOT = Path(__file__).resolve().parents[2]
REF = ROOT / "benchmarks/cec_reference_results/cec2017"
BUNDLE = ROOT / "papers/analysis" / os.environ.get(
    "GSK_REL_ID", "rel-2026-07-16-78f075cb0") / "cec2017"
OUT = ROOT / "papers/analysis/posthoc_robustness"
OPTS = ["gsk", "agsk", "apgsk", "fdb-agsk", "atmals-gsk", "egsk", "dt-gsk"]
DIMS = [10, 30, 50, 100]
FLOOR = 1e-8
SEED = 20240620
NPERM = 200_000


def load():
    frames = []
    for o in OPTS:
        df = pd.read_csv(REF / o / "per_run.csv")
        frames.append(df[["optimizer", "function", "dimension", "error"]])
    a = pd.concat(frames, ignore_index=True)
    a["optimizer"] = a["optimizer"].str.lower()
    return a


def endpoints(allr, dim):
    """mean_raw / median_raw come from the frozen descriptive_stats values the
    primary analysis itself ranks (so the mean-endpoint ranks reproduce the
    frozen Friedman ranks exactly, including D10 near-zero ties); mean_log10 is
    the genuinely-new scale-invariant endpoint computed from the per-run CSVs."""
    d = pd.read_csv(BUNDLE / f"descriptive_stats_cec2017_D{dim}.csv")
    d["algorithm"] = d.algorithm.str.lower()
    mean_ = d.pivot(index="function", columns="algorithm", values="mean")[OPTS]
    med_ = d.pivot(index="function", columns="algorithm", values="median")[OPTS]
    sub = allr[allr.dimension == dim]
    log_ = (sub.assign(le=np.log10(sub.error.clip(lower=FLOOR)))
               .groupby(["optimizer", "function"])["le"].mean().unstack("optimizer"))
    log_.columns = [c.lower() for c in log_.columns]
    log_ = log_[OPTS]
    return {"mean_raw": mean_, "median_raw": med_, "mean_log10": log_}


def friedman_ranks(M):
    R = np.apply_along_axis(rankdata, 1, M.values)
    return pd.Series(R.mean(axis=0), index=M.columns)


def perm_signed_rank_p(diff, rng):
    diff = np.asarray(diff, float)
    diff = diff[diff != 0]
    n = len(diff)
    if n == 0:
        return np.nan
    r = rankdata(np.abs(diff))
    T = np.sum(r * np.sign(diff))
    signs = rng.choice([-1.0, 1.0], size=(NPERM, n))
    null = (signs * r).sum(axis=1)
    return (1 + np.sum(np.abs(null) >= abs(T) - 1e-9)) / (NPERM + 1)


def holm(pvals):
    order = np.argsort(pvals)
    m = len(pvals)
    adj = np.empty(m)
    run = 0.0
    for i, idx in enumerate(order):
        run = max(run, (m - i) * pvals[idx])
        adj[idx] = min(run, 1.0)
    return adj


def main():
    allr = load()
    OUT.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(SEED)

    # ---- validation gate: reproduce frozen primary Friedman ranks ----
    print("VALIDATION GATE (endpoint=mean_raw vs frozen friedman_ranks):")
    for dim in DIMS:
        mr = friedman_ranks(endpoints(allr, dim)["mean_raw"])
        fr = pd.read_csv(BUNDLE / f"friedman_ranks_cec2017_D{dim}.csv").set_index("algorithm")["mean_rank"]
        d = (mr - fr.reindex(mr.index)).abs().max()
        print(f"  D{dim}: max|rank-frozen|={d:.2e}  {'OK' if d < 1e-6 else 'MISMATCH'}")

    # ---- (1) endpoint invariance ----
    erows = []
    for dim in DIMS:
        eps = endpoints(allr, dim)
        for name, M in eps.items():
            mr = friedman_ranks(M).sort_values()
            place = list(mr.index).index("dt-gsk") + 1
            erows.append({"dimension": dim, "endpoint": name,
                          "dt_gsk_mean_rank": round(float(mr["dt-gsk"]), 4),
                          "dt_gsk_place": place, "n_algorithms": len(OPTS)})
    edf = pd.DataFrame(erows)
    edf.to_csv(OUT / "posthoc_endpoint_ranks_cec2017.csv", index=False)

    # ---- (2) exact inference ----
    irows = []
    comps = [o for o in OPTS if o != "dt-gsk"]
    for dim in DIMS:
        M = endpoints(allr, dim)["mean_raw"]
        pn, pp = [], []
        for c in comps:
            _, p = wilcoxon(M["dt-gsk"].values, M[c].values,
                            correction=True, mode="approx", zero_method="wilcox")
            pn.append(p)
            pp.append(perm_signed_rank_p((M["dt-gsk"] - M[c]).values, rng))
        hn, hp = holm(np.array(pn)), holm(np.array(pp))
        for i, c in enumerate(comps):
            irows.append({"dimension": dim, "comparator": c,
                          "p_normal": pn[i], "p_permutation": pp[i],
                          "holm_normal": hn[i], "holm_permutation": hp[i],
                          "sig_normal": int(hn[i] < 0.05),
                          "sig_permutation": int(hp[i] < 0.05)})
    idf = pd.DataFrame(irows)
    idf.to_csv(OUT / "posthoc_inference_cec2017.csv", index=False)
    flips = int((idf.sig_normal != idf.sig_permutation).sum())

    print("\nENDPOINT INVARIANCE (DT-GSK place / 7 by dimension):")
    for dim in DIMS:
        pl = edf[edf.dimension == dim].set_index("endpoint")["dt_gsk_place"]
        print(f"  D{dim}: mean_raw={pl['mean_raw']}  median={pl['median_raw']}  log10={pl['mean_log10']}")
    print(f"\nEXACT INFERENCE: Holm alpha=0.05 decision changes (normal vs permutation) "
          f"= {flips} / {len(idf)}")
    print(f"Wrote {OUT/'posthoc_endpoint_ranks_cec2017.csv'}")
    print(f"Wrote {OUT/'posthoc_inference_cec2017.csv'}")


if __name__ == "__main__":
    main()
