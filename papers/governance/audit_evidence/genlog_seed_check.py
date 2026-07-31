"""Verify per-run seeds embedded in gen_logs CheckpointErrors files.

1. apgsk/cec2017: ALL 116 files (recovers the D10/D30/D50 coverage lost from
   the overwritten seed_schedule.csv / per_run.csv).
2. Every other (suite, optimizer): spot-check one CheckpointErrors file per
   dimension (lowest and highest function) against the unified formula.
Also dump optimizer-specific fp probes across suites.
READ-ONLY.
"""
from __future__ import annotations

import csv
import json
import re
from pathlib import Path

ROOT = Path(r"D:/AI/PhD-Projects/00-GSK-Family/02-GSK_Family_Python_v1.1")
EVID = ROOT / "benchmarks" / "cec_reference_results"
MAX_SAFE_SEED = 2_147_483_646
BASE = 20240620

SUITES = {
    "cec2017": ["agsk", "apgsk", "atmals-gsk", "egsk", "fdb-agsk", "gsk", "dt-gsk"],
    "cec2011": ["agsk", "apgsk", "atmals-gsk", "egsk", "fdb-agsk", "gsk", "dt-gsk"],
    "cec2013": ["agsk", "apgsk", "atmals-gsk", "egsk", "fdb-agsk", "gsk", "dt-gsk"],
}

# cec2011 native dims per problem (from seed_schedule Dim column)
CEC2011_DIMS = {}
with open(EVID / "cec2011" / "gsk" / "seed_schedule.csv", newline="", encoding="utf-8") as f:
    for r in csv.DictReader(f):
        CEC2011_DIMS[int(r["Function"])] = int(r["Dim"])


def get_cec_seed(dim: int, func: int, run: int) -> int:
    return (BASE + 1_000_003 * dim + 1_000_033 * func + 1_000_037 * run) % MAX_SAFE_SEED + 1


PAT = re.compile(r"CheckpointErrors_.+_F(\d+)_D(\d+)\.csv$")
PAT_2011 = re.compile(r"CheckpointErrors_.+_F(\d+)\.csv$")


def check_file(path: Path, suite: str):
    m = PAT.match(path.name)
    if m:
        func, dim = int(m.group(1)), int(m.group(2))
    else:
        m2 = PAT_2011.match(path.name)
        if not m2:
            return None
        func = int(m2.group(1))
        dim = CEC2011_DIMS.get(func)
        if dim is None:
            return ("no_dim", path.name, 0, 0)
    bad = 0
    n = 0
    with open(path, newline="", encoding="utf-8") as f:
        for rec in csv.DictReader(f):
            n += 1
            run = int(rec["Run"])
            seed = int(rec["Seed"])
            if seed != get_cec_seed(dim, func, run):
                bad += 1
    return (path.name, func, dim, n, bad)


results = {}
# 1. apgsk cec2017 full sweep
apgsk_dir = EVID / "cec2017" / "apgsk" / "gen_logs"
files = sorted(apgsk_dir.glob("CheckpointErrors_*.csv"))
tot_rows = tot_bad = 0
per_dim_files = {}
for p in files:
    name, func, dim, n, bad = check_file(p, "cec2017")
    tot_rows += n
    tot_bad += bad
    per_dim_files.setdefault(dim, 0)
    per_dim_files[dim] += 1
results["apgsk_cec2017_full"] = {
    "files": len(files), "rows": tot_rows, "bad": tot_bad, "files_per_dim": per_dim_files,
}

# 2. spot check every other cell: first + last CheckpointErrors file per dim
spot = {}
for suite, opts in SUITES.items():
    for opt in opts:
        gl = EVID / suite / opt / "gen_logs"
        files = sorted(gl.glob("CheckpointErrors_*.csv"))
        by_dim = {}
        for p in files:
            m = PAT.match(p.name)
            if m:
                d = int(m.group(2))
            else:
                m2 = PAT_2011.match(p.name)
                d = 0 if not m2 else CEC2011_DIMS.get(int(m2.group(1)), -1)
            by_dim.setdefault(d, []).append(p)
        cell_bad = 0
        cell_rows = 0
        n_checked = 0
        for d, plist in sorted(by_dim.items()):
            for p in (plist[0], plist[-1]):
                r = check_file(p, suite)
                if r is None:
                    continue
                cell_rows += r[3]
                cell_bad += r[4]
                n_checked += 1
        spot[f"{suite}/{opt}"] = {
            "genlog_files_total": len(files), "checked": n_checked,
            "rows": cell_rows, "bad": cell_bad,
        }
results["spot_checks"] = spot

# 3. optimizer-specific fp probes across suites
probes = {}
for suite, opts in SUITES.items():
    for opt in opts:
        env = json.load(open(EVID / suite / opt / "environment.json", encoding="utf-8"))
        p = (env.get("fp_regime", {}) or {}).get("probes", {}) or {}
        for k, v in p.items():
            probes.setdefault(k, {}).setdefault(v, []).append(f"{suite}/{opt}")
results["probe_values"] = probes

out = Path(__file__).parent / "genlog_check_out.json"
with open(out, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=1)
print(json.dumps(results["apgsk_cec2017_full"], indent=1))
nbad = {k: v for k, v in spot.items() if v["bad"] or v["rows"] == 0}
print("spot cells with problems:", nbad if nbad else "NONE")
print("total spot rows checked:", sum(v["rows"] for v in spot.values()))
for k, vals in probes.items():
    print(f"probe {k}: {len(vals)} distinct value(s)")
    for v, cells in vals.items():
        print(f"   {v[:16]}... <- {len(cells)} cells: {cells[:4]}{'...' if len(cells)>4 else ''}")
