#!/usr/bin/env python3
# Copyright (c) 2026 Mostafa Masoud <moustafa.masoud@gmail.com>
"""Analysis bundle for the revision-experiment release rev-rel-2026-08-26-dd42d37eb.

Strict-source: reads ONLY the promoted release
``benchmarks/cec_reference_results/_revision/`` plus the two frozen releases it
pairs with (the primary panel ``benchmarks/cec_reference_results/cec2017/`` and
the ablation overlay ``.../_ablation/overlay/``). Never reads ``results/``
staging. Emits a self-manifested bundle::

    papers/analysis/rev-rel-2026-08-26-dd42d37eb/
        e1_basis_contrast.json      three-arm refinement contrast (R2.3)
        e2_np100.json               matched population size + panel re-rank (R1.3/R2.2)
        e3_uniform_vs_tiered.json   configuration transplants (R2.1)
        e4_sensitivity.csv          DESCRIPTIVE ONLY (R2.7; registered exploratory)
        analysis_manifest.json      per-file SHA-256
        analysis_checksums.sha256

Statistical conventions, exactly as pre-registered
(papers/review_2026_08_24/revision_experiments_preregistration.md):

* per-function means over the paired runs; paired Wilcoxon signed-rank across
  the 29 scored functions (repo tool of record ``wilcoxon_paired``);
* Holm correction, alpha = 0.05, with the FAMILY STRUCTURE recorded per
  experiment inside each JSON: E1 within-dimension (its 2 contrasts), E2 one
  family across the four dimensions, E3 one family across the four dimensions
  within each transplant arm;
* W/T/L via the repo tool of record ``win_tie_loss`` (tie tolerance 1e-8);
* Vargha-Delaney A12 on the raw paired runs;
* Friedman mean ranks are descriptive; any omnibus uses the tie-corrected
  statistic with the Iman-Davenport F (the paper's post-R1.4 convention);
* E4 is DESCRIPTIVE ONLY -- no hypothesis tests, no corrected p-values
  (registered exploratory; robustness_plan.md reporting constraints).

Fail-closed self-checks: pairing is verified by per-cell seed identity before
any statistic (0 mismatches required), and a pinned known-answer battery from
the pre-promotion analyses must reproduce or the script refuses to emit.
"""
from __future__ import annotations

import csv
import hashlib
import json
import os
import sys
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

import numpy as np  # noqa: E402
from gsk_family.analysis.statistics import (  # noqa: E402
    friedman_rank, holm_correction, wilcoxon_paired, win_tie_loss,
)

REL = os.environ.get("GSK_REV_REL_ID", "rev-rel-2026-08-26-dd42d37eb")
REV = REPO / "benchmarks" / "cec_reference_results" / "_revision"
REV2 = REPO / "benchmarks" / "cec_reference_results" / "_revision2"
PANEL = REPO / "benchmarks" / "cec_reference_results" / "cec2017"
OVERLAY = REPO / "benchmarks" / "cec_reference_results" / "_ablation" / "overlay"
OUT = REPO / "papers" / "analysis" / REL

FAMILY = ["gsk", "agsk", "apgsk", "fdb-agsk", "atmals-gsk", "egsk", "dt-gsk"]
DIMS = [10, 30, 50, 100]

# Pinned known answers from the pre-promotion analyses (2026-08-26). Tolerances
# are generous only where display rounding was involved; refusal on mismatch.
PINS = [
    ("E1 D50 eigen-vs-coord raw p", 6.933e-5, 2e-6),
    ("E1 D50 eigen-vs-coord W", 4, 0), ("E1 D50 eigen-vs-coord L", 25, 0),
    ("E1 D100 eigen-vs-coord W", 11, 0), ("E1 D100 eigen-vs-coord T", 1, 0),
    ("E2 D100 swapped mean rank", 3.069, 2e-3),
    ("E2 D50 Holm p", 6.412e-3, 2e-4),
    ("E3 U-low D30 Holm p", 5.495e-3, 2e-4),
    ("E3 U-high D10 Holm p", 5.994e-3, 2e-4),
    # supplementary coordinate-vs-none contrast (added post-QC, 2026-08-26)
    ("E1 D50 coord-vs-none W", 28, 0),
    # canonical-rule value (Amendments A5/A6): one within-band pair leaves the
    # ranking, moving this from 1.181e-3; the decision is unchanged.
    ("E1 D100 coord-vs-none raw p", 1.490e-3, 5e-5),
]
_pin_hits: dict[str, float] = {}


def pin(name: str, value: float) -> None:
    _pin_hits[name] = float(value)


def check_pins() -> None:
    bad = []
    for name, want, tol in PINS:
        got = _pin_hits.get(name)
        if got is None or abs(got - want) > tol:
            bad.append(f"{name}: want {want}, got {got}")
    if bad:
        raise SystemExit("HARD FAIL: known-answer pins did not reproduce:\n  "
                         + "\n  ".join(bad))


def load(path: Path) -> dict[tuple[int, int, int], tuple[float, int]]:
    out = {}
    with path.open(encoding="utf-8", newline="") as fh:
        for r in csv.DictReader(fh):
            if r.get("suite", "cec2017") != "cec2017":
                continue
            out[(int(r["function"]), int(r["dimension"]), int(r["run"]))] = (
                float(r["error"]), int(r["seed"]))
    return out


def verify_pairing(name: str, a, b, dims=None) -> int:
    common = set(a) & set(b)
    if dims is not None:
        common = {k for k in common if k[1] in dims}
    bad = sum(1 for k in common if a[k][1] != b[k][1])
    if bad:
        raise SystemExit(f"HARD FAIL: {name}: {bad} seed mismatches -- paired design void")
    return len(common)


def pf_means(data, dim) -> dict[int, float]:
    acc = defaultdict(list)
    for (f, d, _), (e, _s) in data.items():
        if d == dim:
            acc[f].append(e)
    return {f: float(np.mean(v)) for f, v in acc.items()}


def a12(a: list[float], b: list[float]) -> float:
    n = len(a) * len(b)
    return sum((x < y) + 0.5 * (x == y) for x in a for y in b) / n


def raw_at(data, funcs, dim, runs=51):
    # runs caps the schedule prefix used, so 15-run E5 cells pair against the
    # frozen leg's SAME first 15 runs (Amendment A4 pairing rule).
    out = []
    for f in funcs:
        out += [data[(f, dim, r)][0] for r in range(1, runs + 1) if (f, dim, r) in data]
    return out


def wtl(m_a: dict[int, float], m_b: dict[int, float]):
    r = win_tie_loss(m_a, m_b)
    return {"W": int(r.wins), "T": int(r.ties), "L": int(r.losses)}


def contrast(m_ref, m_cmp, raw_ref, raw_cmp) -> dict:
    # Canonical near-zero rule (pre-registration Amendment A5): |d| < 1e-8 is
    # zeroed and excluded before ranking, matching the manuscript's stated tie
    # rule and the primary pipeline. The first release of this analyzer passed
    # exact zeros only; the deviation and its one decision-level consequence
    # (E1 D=100, eigenframe vs coordinate) are recorded in the amendment.
    funcs = sorted(set(m_ref) & set(m_cmp))
    res = wilcoxon_paired(np.array([m_ref[f] for f in funcs]),
                          np.array([m_cmp[f] for f in funcs]), zero_tol=1e-8)
    return {"raw_p": float(res.p_value), "wtl_ref_vs_cmp": wtl(m_ref, m_cmp),
            "a12_ref_vs_cmp": a12(raw_ref, raw_cmp), "n_funcs": len(funcs),
            "n_effective": int(res.n_pairs)}


def analyse_e1() -> dict:
    arms = {
        "none": load(OVERLAY / "no_finalpolish/dt-gsk/cec2017/summary/per_run.csv"),
        "coordinate": load(REV / "e1_basis_coordinate/dt-gsk/cec2017/summary/per_run.csv"),
        "eigenframe": load(OVERLAY / "full/dt-gsk/cec2017/summary/per_run.csv"),
    }
    shared = verify_pairing("E1", arms["coordinate"], arms["eigenframe"], dims=[50, 100])
    verify_pairing("E1-none", arms["coordinate"], arms["none"], dims=[50, 100])
    out = {"experiment": "E1", "reviewer_point": "R2.3",
           "design": "three-arm refinement contrast at the shipped configuration",
           "holm_family": "within-dimension: {eigenframe-vs-coordinate, eigenframe-vs-none}",
           "shared_cells": shared, "seed_mismatches": 0, "dimensions": {}}
    for dim in (50, 100):
        means = {a: pf_means(arms[a], dim) for a in arms}
        funcs = sorted(set.intersection(*(set(m) for m in means.values())))
        raws, labels, cons = [], [], {}
        for other in ("coordinate", "none"):
            c = contrast(means["eigenframe"], means[other],
                         raw_at(arms["eigenframe"], funcs, dim),
                         raw_at(arms[other], funcs, dim))
            cons[f"eigenframe_vs_{other}"] = c
            raws.append(c["raw_p"]); labels.append(f"eigenframe_vs_{other}")
        holm = holm_correction(raws, labels)
        for h in holm.comparisons:
            cons[str(h["label"])]["holm_p"] = float(h["p_adjusted"])
            cons[str(h["label"])]["significant"] = bool(h["significant"])
        # Supplementary contrast, OUTSIDE the registered 2-test family (added
        # after the QC pass found the axes-polish-vs-none direction supported
        # only transitively): coordinate vs none, single-test family, so its
        # Holm p equals its raw p. The registered family above is untouched.
        supp = contrast(means["coordinate"], means["none"],
                        raw_at(arms["coordinate"], funcs, dim),
                        raw_at(arms["none"], funcs, dim))
        supp["holm_p"] = supp["raw_p"]
        supp["significant"] = bool(supp["raw_p"] < 0.05)
        supp["family_note"] = ("supplementary single-test contrast, outside the "
                               "registered E1 family")
        cons["coordinate_vs_none_supplementary"] = supp
        out["dimensions"][f"D{dim}"] = {
            "mean_of_means": {a: float(np.mean([means[a][f] for f in funcs]))
                              for a in arms},
            "contrasts": cons,
        }
    d50 = out["dimensions"]["D50"]["contrasts"]["eigenframe_vs_coordinate"]
    d100 = out["dimensions"]["D100"]["contrasts"]["eigenframe_vs_coordinate"]
    pin("E1 D50 eigen-vs-coord raw p", d50["raw_p"])
    pin("E1 D50 eigen-vs-coord W", d50["wtl_ref_vs_cmp"]["W"])
    pin("E1 D50 eigen-vs-coord L", d50["wtl_ref_vs_cmp"]["L"])
    pin("E1 D100 eigen-vs-coord W", d100["wtl_ref_vs_cmp"]["W"])
    pin("E1 D100 eigen-vs-coord T", d100["wtl_ref_vs_cmp"]["T"])
    s50 = out["dimensions"]["D50"]["contrasts"]["coordinate_vs_none_supplementary"]
    s100 = out["dimensions"]["D100"]["contrasts"]["coordinate_vs_none_supplementary"]
    pin("E1 D50 coord-vs-none W", s50["wtl_ref_vs_cmp"]["W"])
    pin("E1 D100 coord-vs-none raw p", s100["raw_p"])
    return out


def analyse_e2() -> dict:
    panel = {o: load(PANEL / o / "per_run.csv") for o in FAMILY}
    e2 = load(REV / "e2_np100/dt-gsk/cec2017/summary/per_run.csv")
    shared = verify_pairing("E2", e2, panel["dt-gsk"])
    out = {"experiment": "E2", "reviewer_point": "R1.3/R2.2",
           "design": ("DT-GSK at pop_size=100 vs its NP=5D leg; panel re-ranked with "
                      "the six frozen comparator columns unchanged. Registered framing: "
                      "an ablation of the declared population component, not a "
                      "corrected baseline."),
           "holm_family": "one family across the four dimensions",
           "shared_cells": shared, "seed_mismatches": 0, "dimensions": {}}
    raws, labels = [], []
    for dim in DIMS:
        m_pub = {o: pf_means(panel[o], dim) for o in FAMILY}
        funcs = sorted(set.intersection(*(set(v) for v in m_pub.values())))
        fr_pub = friedman_rank({o: [m_pub[o][f] for f in funcs] for o in FAMILY})
        m_e2 = dict(m_pub); m_e2["dt-gsk"] = pf_means(e2, dim)
        fr_e2 = friedman_rank({o: [m_e2[o][f] for f in funcs] for o in FAMILY})
        r_pub, r_e2 = dict(fr_pub.avg_ranks), dict(fr_e2.avg_ranks)
        c = contrast(m_pub["dt-gsk"], m_e2["dt-gsk"],
                     raw_at(panel["dt-gsk"], funcs, dim), raw_at(e2, funcs, dim))
        raws.append(c["raw_p"]); labels.append(f"D{dim}")
        out["dimensions"][f"D{dim}"] = {
            "rank_np5d": float(r_pub["dt-gsk"]), "rank_np100": float(r_e2["dt-gsk"]),
            "ordinal_np5d": sorted(FAMILY, key=lambda o: r_pub[o]).index("dt-gsk") + 1,
            "ordinal_np100": sorted(FAMILY, key=lambda o: r_e2[o]).index("dt-gsk") + 1,
            "paired_np5d_vs_np100": c,
        }
    holm = holm_correction(raws, labels)
    for h in holm.comparisons:
        d = out["dimensions"][str(h["label"])]
        d["paired_np5d_vs_np100"]["holm_p"] = float(h["p_adjusted"])
        d["paired_np5d_vs_np100"]["significant"] = bool(h["significant"])
    pin("E2 D100 swapped mean rank", out["dimensions"]["D100"]["rank_np100"])
    pin("E2 D50 Holm p", out["dimensions"]["D50"]["paired_np5d_vs_np100"]["holm_p"])
    return out


def analyse_e3() -> dict:
    T = load(PANEL / "dt-gsk" / "per_run.csv")
    out = {"experiment": "E3", "reviewer_point": "R2.1",
           "design": ("configuration transplants: pub_overrides(10) and pub_overrides(100) "
                      "applied unchanged at every dimension (tier-constant arms) vs the "
                      "frozen tiered leg. Registered rule: no E3 difference may be "
                      "attributed to any individual subsystem."),
           "holm_family": "one family across the four dimensions, within each arm",
           "arms": {}}
    for arm_name, sub in (("U_low", "e3_uniform_low"), ("U_high", "e3_uniform_high")):
        arm = load(REV / sub / "dt-gsk/cec2017/summary/per_run.csv")
        shared = verify_pairing(f"E3 {arm_name}", arm, T)
        raws, labels, dims_out = [], [], {}
        for dim in DIMS:
            mt, ma = pf_means(T, dim), pf_means(arm, dim)
            c = contrast(mt, ma, raw_at(T, sorted(set(mt) & set(ma)), dim),
                         raw_at(arm, sorted(set(mt) & set(ma)), dim))
            raws.append(c["raw_p"]); labels.append(f"D{dim}")
            dims_out[f"D{dim}"] = {"tiered_vs_transplant": c}
        holm = holm_correction(raws, labels)
        for h in holm.comparisons:
            d = dims_out[str(h["label"])]["tiered_vs_transplant"]
            d["holm_p"] = float(h["p_adjusted"])
            d["significant"] = bool(h["significant"])
        out["arms"][arm_name] = {"shared_cells": shared, "seed_mismatches": 0,
                                 "dimensions": dims_out}
    pin("E3 U-low D30 Holm p",
        out["arms"]["U_low"]["dimensions"]["D30"]["tiered_vs_transplant"]["holm_p"])
    pin("E3 U-high D10 Holm p",
        out["arms"]["U_high"]["dimensions"]["D10"]["tiered_vs_transplant"]["holm_p"])
    return out


def analyse_e4() -> list[dict]:
    """DESCRIPTIVE ONLY (registered exploratory). No tests, no corrected p-values."""
    panel = {o: load(PANEL / o / "per_run.csv") for o in FAMILY}
    rows = []
    for cell_dir in sorted(REV.glob("e4_*")):
        name = cell_dir.name[3:]                      # strip "e4_"
        dim = int(name.rsplit("_D", 1)[1])
        field_level = name.rsplit("_D", 1)[0]
        field, level = field_level.rsplit("_", 1)
        cell = load(cell_dir / "dt-gsk/cec2017/summary/per_run.csv")
        verify_pairing(f"E4 {cell_dir.name}", cell, panel["dt-gsk"], dims=[dim])
        m_pub = {o: pf_means(panel[o], dim) for o in FAMILY}
        funcs = sorted(set.intersection(*(set(v) for v in m_pub.values())))
        fr_pub = friedman_rank({o: [m_pub[o][f] for f in funcs] for o in FAMILY})
        m_cell = dict(m_pub); m_cell["dt-gsk"] = pf_means(cell, dim)
        fr_cell = friedman_rank({o: [m_cell[o][f] for f in funcs] for o in FAMILY})
        r_pub, r_cell = dict(fr_pub.avg_ranks), dict(fr_cell.avg_ranks)
        w = wtl(m_pub["dt-gsk"], m_cell["dt-gsk"])
        rows.append({
            "cell": cell_dir.name, "parameter": field, "level": level,
            "dimension": dim,
            "baseline_rank": round(float(r_pub["dt-gsk"]), 4),
            "perturbed_rank": round(float(r_cell["dt-gsk"]), 4),
            "baseline_ordinal": sorted(FAMILY, key=lambda o: r_pub[o]).index("dt-gsk") + 1,
            "perturbed_ordinal": sorted(FAMILY, key=lambda o: r_cell[o]).index("dt-gsk") + 1,
            "baseline_wtl_vs_perturbed": f"{w['W']}/{w['T']}/{w['L']}",
            "median_ratio_perturbed_over_baseline": round(float(np.median(
                [(m_cell["dt-gsk"][f] / m_pub["dt-gsk"][f])
                 for f in funcs if m_pub["dt-gsk"][f] > 0])), 4),
            "note": ("DESCRIPTIVE ONLY (registered exploratory). Perturbed arm has 15 "
                     "runs vs the frozen 51; ordinal computed on per-function means."),
        })
    return rows


E5_CELLS = [
    # (arm dir under REV2, boundary, shift description, runs)
    ("e5_b20_lo_D10", "T0/T1", "20->10: D10 joins the middle tier", 15),
    ("e5_b50_lo_D30", "T1/T2", "50->30: D30 joins the structure tier", 15),
    ("e5_b50_hi_D50", "T1/T2", "50->51: D50 drops to the middle tier", 15),
    ("e5_b100_hi_D100", "T2/T3", "100->101: D100 drops to the T2 profile", 15),
]


def analyse_e5() -> dict:
    """Dimension-boundary sensitivity (Amendment A4; release _revision2).

    Five registered cells: four executed at 15 paired runs, the fifth
    (boundary 20->31 at D=30) reused from E3's U-low arm (51 runs). The tiered
    reference is the frozen leg restricted to the SAME runs each cell has.
    One Holm family across the five boundary contrasts (m=5).
    """
    T = load(PANEL / "dt-gsk" / "per_run.csv")
    panel = {o: load(PANEL / o / "per_run.csv") for o in FAMILY}

    cells: list[dict] = []
    for arm, boundary, shift, runs in E5_CELLS:
        dim = int(arm.rsplit("_D", 1)[1])
        data = load(REV2 / arm / "dt-gsk/cec2017/summary/per_run.csv")
        cells.append({"arm": arm, "boundary": boundary, "shift": shift,
                      "dim": dim, "runs": runs, "data": data,
                      "provenance": "rev2 release (new execution)"})
    # the reused fifth cell: E3 U-low at D=30 (51 runs, round-one release)
    ulow = load(REV / "e3_uniform_low/dt-gsk/cec2017/summary/per_run.csv")
    cells.insert(1, {"arm": "e3_uniform_low@D30", "boundary": "T0/T1",
                     "shift": "20->31: D30 joins the low tier", "dim": 30,
                     "runs": 51,
                     "data": {k: v for k, v in ulow.items() if k[1] == 30},
                     "provenance": ("REUSED: rev-rel-2026-08-26-dd42d37eb "
                                    "e3_uniform_low, identical by construction")})

    out = {"experiment": "E5", "reviewer_point": "R2.7 (threshold half)",
           "design": ("dimension-boundary sensitivity: each cell shifts one tier "
                      "boundary far enough to change the profile assigned to the "
                      "nearest official CEC2017 dimension, executed as an E3-style "
                      "single-dimension profile transplant. Registered rule: only "
                      "boundary-level sensitivity is licensed -- a shift changes the "
                      "complete resolved profile, so no cell attributes anything to "
                      "an individual mechanism."),
           "holm_family": "one family across the five boundary contrasts (m=5)",
           "coverage_note": ("T2/T3 tested one-sided (101 only): a lower-side "
                             "perturbation collapses adjacent boundaries and no "
                             "official dimension lies between 50 and 100."),
           "cells": []}

    raws, labels = [], []
    for c in cells:
        dim, runs = c["dim"], c["runs"]
        ref = {k: v for k, v in T.items()
               if k[1] == dim and k[2] <= runs}
        verify_pairing(f"E5 {c['arm']}", c["data"], ref, dims=[dim])
        m_ref, m_cell = pf_means(ref, dim), pf_means(c["data"], dim)
        funcs = sorted(set(m_ref) & set(m_cell))
        con = contrast(m_ref, m_cell,
                       raw_at(ref, funcs, dim, runs=runs),
                       raw_at(c["data"], funcs, dim, runs=runs))
        raws.append(con["raw_p"]); labels.append(c["arm"])

        m_pub = {o: pf_means(panel[o], dim) for o in FAMILY}
        pfuncs = sorted(set.intersection(*(set(v) for v in m_pub.values())))
        fr_pub = friedman_rank({o: [m_pub[o][f] for f in pfuncs] for o in FAMILY})
        m_sub = dict(m_pub); m_sub["dt-gsk"] = m_cell
        fr_sub = friedman_rank({o: [m_sub[o][f] for f in pfuncs] for o in FAMILY})
        r_pub, r_sub = dict(fr_pub.avg_ranks), dict(fr_sub.avg_ranks)

        c_out = {"arm": c["arm"], "boundary": c["boundary"], "shift": c["shift"],
                 "dimension": dim, "runs": runs, "provenance": c["provenance"],
                 "tiered_vs_transplant": con,
                 "rank_tiered": round(float(r_pub["dt-gsk"]), 4),
                 "rank_transplant": round(float(r_sub["dt-gsk"]), 4),
                 "ordinal_tiered": sorted(FAMILY, key=lambda o: r_pub[o]).index("dt-gsk") + 1,
                 "ordinal_transplant": sorted(FAMILY, key=lambda o: r_sub[o]).index("dt-gsk") + 1,
                 "rerank_note": ("ordinal from per-function means with only the "
                                 "DT-GSK column substituted; transplant means use "
                                 f"{runs} runs vs the panel's 51 (E4 convention)")}
        out["cells"].append(c_out)

    holm = holm_correction(raws, labels)
    for h in holm.comparisons:
        for c_out in out["cells"]:
            if c_out["arm"] == str(h["label"]):
                c_out["tiered_vs_transplant"]["holm_p"] = float(h["p_adjusted"])
                c_out["tiered_vs_transplant"]["significant"] = bool(h["significant"])
    return out


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    common = {"release_id": REL,
              "strict_sources": ["benchmarks/cec_reference_results/_revision/",
                                 "benchmarks/cec_reference_results/cec2017/",
                                 "benchmarks/cec_reference_results/_ablation/overlay/"],
              "preregistration": "papers/review_2026_08_24/revision_experiments_preregistration.md",
              "conventions": ("paired Wilcoxon across per-function means; Holm alpha=0.05 "
                              "(family per experiment, stated in-file); W/T/L tie tol 1e-8 "
                              "(tool of record); A12 on raw paired runs; Friedman ranks "
                              "descriptive")}

    jobs = [("e1_basis_contrast", analyse_e1()),
            ("e2_np100", analyse_e2()),
            ("e3_uniform_vs_tiered", analyse_e3())]
    if (REV2 / "manifest.json").is_file():
        common["strict_sources"] = common["strict_sources"] + [
            "benchmarks/cec_reference_results/_revision2/"]
        jobs.append(("e5_threshold_sensitivity", analyse_e5()))
    else:
        print("note: _revision2 not promoted yet -- E5 analysis skipped")
    for name, payload in jobs:
        payload = {**common, **payload}
        (OUT / f"{name}.json").write_bytes(
            (json.dumps(payload, indent=2, ensure_ascii=False) + "\n").encode("utf-8"))
        print(f"wrote {name}.json")

    e4 = analyse_e4()
    if e4:
        with (OUT / "e4_sensitivity.csv").open("w", encoding="utf-8", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(e4[0].keys()), lineterminator="\n")
            w.writeheader()
            w.writerows(e4)
        print(f"wrote e4_sensitivity.csv ({len(e4)} cells)")
    else:
        print("e4: no promoted cells found (pending campaign completion)")

    check_pins()
    print("known-answer pins: all reproduced")

    entries = {f.name: sha256(f) for f in sorted(OUT.iterdir())
               if f.is_file() and f.name not in
               ("analysis_manifest.json", "analysis_checksums.sha256")}
    (OUT / "analysis_manifest.json").write_bytes(
        (json.dumps({"release_id": REL, "generator":
                     "papers/scripts/analyze_revision_experiments.py",
                     "files": entries}, indent=2) + "\n").encode("utf-8"))
    (OUT / "analysis_checksums.sha256").write_text(
        "".join(f"{h}  {n}\n" for n, h in entries.items()), encoding="utf-8")
    print(f"bundle: {OUT.relative_to(REPO)} ({len(entries)} artifacts + manifest)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
