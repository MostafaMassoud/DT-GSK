"""Cross-check apgsk cec2017 summary CSVs vs gen_logs final-checkpoint stats.

If Best/Median/Mean/Worst/SD recomputed from gen_logs' final checkpoint match
the summary files for D10/D30/D50 (the dims whose per_run.csv rows were lost),
the gen_logs are proven to belong to the same runs as the summaries.
Also: per_run.csv (D100) vs gen_logs D100 final errors.
Plus: dump remaining env fields needed for the reports. READ-ONLY.
"""
from __future__ import annotations

import csv
import json
import statistics
from pathlib import Path

ROOT = Path(r"D:/AI/PhD-Projects/00-GSK-Family/02-GSK_Family_Python_v1.1")
EVID = ROOT / "benchmarks" / "cec_reference_results"
AP = EVID / "cec2017" / "apgsk"

REPORT_ZERO_TOL = 1e-8  # from environment.json report_zero_tol


def load_summary(dim):
    rows = {}
    with open(AP / f"apgsk_cec2017_D{dim}.csv", newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            rows[int(r["Function"])] = {k: float(r[k]) for k in ("Best", "Median", "Mean", "Worst", "SD")}
    return rows


def genlog_final(dim, func):
    p = AP / "gen_logs" / f"CheckpointErrors_apgsk_F{func}_D{dim}.csv"
    vals = []
    with open(p, newline="", encoding="utf-8") as f:
        rd = csv.DictReader(f)
        last_col = rd.fieldnames[-1]
        for rec in rd:
            vals.append(float(rec[last_col]))
    return vals


def close(a, b, rtol=1e-6, atol=1e-9):
    return abs(a - b) <= max(atol, rtol * max(abs(a), abs(b)))


def floor_zero(v):
    return 0.0 if v < REPORT_ZERO_TOL else v


bad = []
checked = 0
for dim in (10, 30, 50, 100):
    summ = load_summary(dim)
    for func, s in summ.items():
        vals = sorted(genlog_final(dim, func))
        vals_floored = [floor_zero(v) for v in vals]
        stats = {
            "Best": vals_floored[0],
            "Median": statistics.median(vals_floored),
            "Mean": statistics.fmean(vals_floored),
            "Worst": vals_floored[-1],
            "SD": statistics.stdev(vals_floored),
        }
        for k in stats:
            checked += 1
            if not close(stats[k], s[k], rtol=1e-4, atol=1e-7):
                bad.append((dim, func, k, s[k], stats[k]))
print(f"summary-vs-genlogs: checked {checked} stats, mismatches: {len(bad)}")
for b in bad[:15]:
    print("  MISMATCH", b)

# per_run.csv (D100) vs gen_logs D100
pr = {}
with open(AP / "per_run.csv", newline="", encoding="utf-8") as f:
    for rec in csv.DictReader(f):
        pr[(int(rec["function"]), int(rec["run"]))] = float(rec["error"])
bad2 = 0
n2 = 0
for func in sorted({k[0] for k in pr}):
    vals = genlog_final(100, func)
    for i, v in enumerate(vals, start=1):
        n2 += 1
        if not close(pr[(func, i)], v, rtol=1e-9, atol=1e-12):
            bad2 += 1
print(f"per_run(D100)-vs-genlogs: {n2} rows, mismatches: {bad2}")

# remaining env fields
fields = ["statistics_basis", "initial_population_policy", "max_nfes_override",
          "report_zero_tol", "use_parallel", "parallel_backend", "warmup_enabled",
          "benchmark_backend_requested", "data_root", "output_dir"]
seen = {}
for suite in ("cec2017", "cec2011", "cec2013"):
    for opt in ("agsk", "apgsk", "atmals-gsk", "egsk", "fdb-agsk", "gsk", "dt-gsk"):
        env = json.load(open(EVID / suite / opt / "environment.json", encoding="utf-8"))
        for k in fields:
            seen.setdefault(k, {}).setdefault(str(env.get(k)), []).append(f"{suite}/{opt}")
for k, vals in seen.items():
    if len(vals) == 1:
        print(f"{k}: CONSTANT = {list(vals)[0][:100]}")
    else:
        print(f"{k}: {len(vals)} values")
        for v, cells in vals.items():
            print(f"   {v[:90]} <- {len(cells)}: {cells[:3]}{'...' if len(cells)>3 else ''}")

# full sentinels
for suite in ("cec2017", "cec2011", "cec2013"):
    env = json.load(open(EVID / suite / "gsk" / "environment.json", encoding="utf-8"))
    print(suite, "sentinel:", env["fp_regime"]["sentinel"])

# cec2011 native dims table
dims = {}
with open(EVID / "cec2011" / "gsk" / "seed_schedule.csv", newline="", encoding="utf-8") as f:
    for r in csv.DictReader(f):
        dims[int(r["Function"])] = int(r["Dim"])
print("cec2011 native dims:", dims)
dup_dim_funcs = {}
for f_, d_ in dims.items():
    dup_dim_funcs.setdefault(d_, []).append(f_)
print("cec2011 problems sharing a native dim:", {d: fs for d, fs in dup_dim_funcs.items() if len(fs) > 1})
