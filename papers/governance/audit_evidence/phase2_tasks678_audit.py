"""Phase 2 tasks 6-8 audit: evaluator hashes, suite metadata cross-check,
MaxFES accounting, summary-vs-per_run provenance, seed-schedule identity.

Read-only over benchmarks/cec_reference_results. Outputs JSON + CSV into the
scratchpad; governance markdown is written separately by the agent.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
import pickle
import sys
from pathlib import Path

ROOT = Path(r"D:/AI/PhD-Projects/00-GSK-Family/02-GSK_Family_Python_v1.1")
SCRATCH = Path(r"C:\Users\moust\AppData\Local\Temp\claude\D--AI-PhD-Projects-00-GSK-Family-02-GSK-Family-Python-v1-1\936aad4c-083b-4d56-9c2a-2238bd8a85b8\scratchpad")
REF = ROOT / "benchmarks" / "cec_reference_results"
SUITE_PY = ROOT / "benchmarks" / "cec_suite_python"

sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

OPTS = ["gsk", "agsk", "apgsk", "fdb-agsk", "atmals-gsk", "egsk", "dt-gsk"]
PANEL = [("cec2017", OPTS), ("cec2013", OPTS), ("cec2011", OPTS)]
CONTEXT = [("cec2020", ["agsk"]), ("cec2013lsgo", ["decc-g", "mos"])]

out: dict = {}


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


# ---------------------------------------------------------------- 1. hashes
hash_rows = []
def add_hashes(base: Path, rel_prefix: str, exts=None, skip_dirs=("__pycache__",)):
    for p in sorted(base.rglob("*")):
        if p.is_dir():
            continue
        if any(sd in p.parts for sd in skip_dirs):
            continue
        if p.suffix in (".pyc", ".html"):
            continue
        if exts and p.suffix not in exts:
            continue
        rel = p.relative_to(ROOT).as_posix()
        hash_rows.append({
            "path": rel,
            "bytes": p.stat().st_size,
            "sha256": sha256_file(p),
            "class": ("data" if p.suffix in (".pkl", ".mat", ".txt", ".csv") else "code"),
            "group": rel_prefix,
        })

for suite_dir in ["cec2011", "cec2013", "cec2013lsgo", "cec2017", "cec2020"]:
    add_hashes(SUITE_PY / suite_dir, f"suite:{suite_dir}")
add_hashes(SUITE_PY, "suite:root", exts={".py", ".md"}, skip_dirs=("__pycache__", "cec2011", "cec2013", "cec2013lsgo", "cec2017", "cec2020"))
add_hashes(ROOT / "src/gsk_family/benchmark_adapter", "adapter")
add_hashes(ROOT / "src/gsk_family/optimizers", "optimizers")
add_hashes(ROOT / "src/gsk_family/runners", "runners")
add_hashes(ROOT / "src/gsk_family/common", "common")

with (SCRATCH / "evaluator_hash_inventory.csv").open("w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["group", "path", "class", "bytes", "sha256"])
    w.writeheader()
    for r in hash_rows:
        w.writerow(r)
out["n_hashed_files"] = len(hash_rows)

# ------------------------------------------------- 2. suite metadata checks
meta: dict = {}

# cec2017
from benchmarks.cec_suite_python.cec2017 import cec2017_bounds, cec2017_fopt  # noqa: E402
m17 = {"dims_checked": {}, "fopt_rule_100i": True, "fopt": {}}
for d in (10, 30, 50, 100):
    lb, ub = cec2017_bounds(d)
    import numpy as np
    lb = np.asarray(lb); ub = np.asarray(ub)
    m17["dims_checked"][d] = {
        "lb_uniform": float(lb.min()) if lb.ndim else float(lb),
        "ub_uniform": float(ub.max()) if ub.ndim else float(ub),
    }
for fid in range(1, 31):
    fo = float(cec2017_fopt(fid))
    m17["fopt"][fid] = fo
    if fo != 100.0 * fid:
        m17["fopt_rule_100i"] = False
with (SUITE_PY / "cec2017" / "data.pkl").open("rb") as f:
    d17 = pickle.load(f)
m17["data_pkl_keys"] = sorted(d17.keys())[:20] if isinstance(d17, dict) else str(type(d17))
m17["data_pkl_n_keys"] = len(d17) if isinstance(d17, dict) else None
meta["cec2017"] = m17

# cec2013
from benchmarks.cec_suite_python.cec2013 import cec2013_bounds, cec2013_fopt  # noqa: E402
from benchmarks.cec_suite_python.cec2013.transforms import VALID_DIMS as C13_DIMS  # noqa: E402
m13 = {"valid_dims": sorted(int(x) for x in C13_DIMS), "fopt": {}, "fopt_rule": True}
expected13 = [v for v in range(-1400, 1500, 100) if v != 0]
for i, fid in enumerate(range(1, 29)):
    fo = float(cec2013_fopt(fid))
    m13["fopt"][fid] = fo
    if fo != float(expected13[i]):
        m13["fopt_rule"] = False
lb, ub = cec2013_bounds(30)
m13["bounds_D30"] = [float(np.min(lb)), float(np.max(ub))]
with (SUITE_PY / "cec2013" / "data.pkl").open("rb") as f:
    d13 = pickle.load(f)
m13["data_pkl_n_keys"] = len(d13) if isinstance(d13, dict) else None
m13["data_pkl_keys_sample"] = sorted(d13.keys())[:12] if isinstance(d13, dict) else str(type(d13))
meta["cec2013"] = m13

# cec2011
from benchmarks.cec_suite_python.cec2011 import cec2011_bounds, cec2011_dim, cec2011_fname  # noqa: E402
card_dims = {1: 6, 2: 30, 3: 1, 4: 1, 5: 30, 6: 30, 7: 20, 8: 7, 9: 126, 10: 12,
             11: 120, 12: 216, 13: 6, 14: 13, 15: 15, 16: 40, 17: 140, 18: 96,
             19: 96, 20: 96, 21: 26, 22: 22}
m11 = {"functions": {}, "dim_mismatches_vs_das2011_table1": []}
for fid in range(1, 23):
    dd = int(cec2011_dim(fid))
    lo, hi = cec2011_bounds(fid)
    lo = np.asarray(lo, dtype=float); hi = np.asarray(hi, dtype=float)
    m11["functions"][fid] = {"name": str(cec2011_fname(fid)), "dim": dd,
                             "lb_min": float(lo.min()), "ub_max": float(hi.max())}
    if dd != card_dims[fid]:
        m11["dim_mismatches_vs_das2011_table1"].append(
            {"func": fid, "code_dim": dd, "das2011_table1_dim": card_dims[fid]})
meta["cec2011"] = m11
out["suite_metadata"] = meta

# ------------------------------------------------- 3+4. per-cell audits
EXPECTED_BUDGET = {"cec2017": lambda d: 10000 * d, "cec2013": lambda d: 10000 * d,
                   "cec2011": lambda d: 150000}
cells = []
for suite, opts in PANEL:
    for opt in opts:
        cell = REF / suite / opt
        rc = json.loads((cell / "run_config.json").read_text(encoding="utf-8"))
        env = json.loads((cell / "environment.json").read_text(encoding="utf-8"))
        ver = json.loads((cell / "verification.json").read_text(encoding="utf-8"))
        rec = {
            "suite": suite, "optimizer": opt,
            "max_nfes_override_runconfig": rc.get("max_nfes_override"),
            "max_nfes_override_env": env.get("max_nfes_override"),
            "profile": rc.get("profile"),
            "pop_size": rc.get("pop_size"),
            "optimizer_options": rc.get("optimizer_options"),
            "exclude_funcs": rc.get("exclude_funcs"),
            "statistics_basis": rc.get("statistics_basis"),
            "env_git_commit": env.get("git_commit"),
            "env_timestamp": env.get("timestamp"),
            "env_command": env.get("command"),
            "env_output_dir": env.get("output_dir"),
            "env_computer": env.get("computer"),
            "env_fp_sentinel": (env.get("fp_regime") or {}).get("sentinel"),
            "ver_verdict": ver.get("verdict"),
            "ver_generated_dir": ver.get("generated_dir"),
            "ver_functions_checked": ver.get("functions_checked"),
            "ver_wtl": ver.get("win_tie_loss"),
            "ver_reduced_budget": ver.get("reduced_budget"),
        }
        # per_run
        rows = list(csv.DictReader((cell / "per_run.csv").open(encoding="utf-8")))
        rec["per_run_rows"] = len(rows)
        by_dim: dict[int, list[dict]] = {}
        funcs_seen = set()
        for r in rows:
            by_dim.setdefault(int(r["dimension"]), []).append(r)
            funcs_seen.add(int(r["function"]))
        rec["per_run_dims"] = sorted(by_dim)
        rec["per_run_funcs_n"] = len(funcs_seen)
        rec["per_run_has_F2"] = (2 in funcs_seen) if suite == "cec2017" else None
        nfes_audit = {}
        for d, rws in sorted(by_dim.items()):
            budget = EXPECTED_BUDGET[suite](d)
            nf = [int(r["nfes"]) for r in rws]
            terms = sorted({r["termination"] for r in rws})
            nfes_audit[d] = {
                "expected": budget, "min": min(nf), "max": max(nf),
                "n_over": sum(1 for v in nf if v > budget),
                "n_under": sum(1 for v in nf if v < budget),
                "n_exact": sum(1 for v in nf if v == budget),
                "terminations": terms, "n_runs_rows": len(rws),
            }
        rec["nfes_audit"] = nfes_audit
        # error NaN policy
        if suite == "cec2011":
            rec["error_all_nan"] = all(r["error"].lower() == "nan" for r in rows)
        else:
            rec["error_nan_count"] = sum(1 for r in rows if r["error"].lower() == "nan")

        # summary vs per_run recomputation
        summary_check = {}
        def stats_from(vals):
            a = np.asarray(vals, dtype=float)
            sd = float(np.std(a, ddof=1)) if a.size >= 2 else 0.0
            return {"Best": float(a.min()), "Median": float(np.median(a)),
                    "Mean": float(a.mean()), "Worst": float(a.max()), "SD": sd}
        def close(a, b):
            if math.isnan(a) or math.isnan(b):
                return math.isnan(a) and math.isnan(b)
            return math.isclose(a, b, rel_tol=5e-10, abs_tol=1e-12)

        basis_col = "best_fitness" if suite == "cec2011" else "error"
        if suite == "cec2011":
            # rollup file over all functions
            roll = cell / f"{opt}_{suite}.csv"
            files = {"rollup": roll} if roll.exists() else {}
            for d in rec["per_run_dims"]:
                p = cell / f"{opt}_{suite}_D{d}.csv"
                if p.exists():
                    files[f"D{d}"] = p
            # group per function (native dims)
            byf: dict[int, list[float]] = {}
            for r in rows:
                byf.setdefault(int(r["function"]), []).append(float(r[basis_col]))
            for label, p in files.items():
                mism = []
                n_cmp = 0
                for sr in csv.DictReader(p.open(encoding="utf-8")):
                    fid = int(str(sr["Function"]).lstrip("Ff"))
                    if fid not in byf:
                        mism.append({"func": fid, "issue": "no per_run rows"})
                        continue
                    st = stats_from(byf[fid])
                    for k in ("Best", "Median", "Mean", "Worst", "SD"):
                        n_cmp += 1
                        if not close(st[k], float(sr[k])):
                            mism.append({"func": fid, "stat": k,
                                         "summary": float(sr[k]), "recomputed": st[k]})
                summary_check[label] = {"n_compared": n_cmp, "n_mismatch": len(mism),
                                        "mismatches": mism[:8]}
        else:
            for d in (10, 30, 50, 100):
                p = cell / f"{opt}_{suite}_D{d}.csv"
                if not p.exists():
                    continue
                byf = {}
                for r in by_dim.get(d, []):
                    byf.setdefault(int(r["function"]), []).append(float(r[basis_col]))
                mism = []
                n_cmp = 0
                n_missing = 0
                for sr in csv.DictReader(p.open(encoding="utf-8")):
                    fid = int(str(sr["Function"]).lstrip("Ff"))
                    if fid not in byf:
                        n_missing += 1
                        continue
                    st = stats_from(byf[fid])
                    for k in ("Best", "Median", "Mean", "Worst", "SD"):
                        n_cmp += 1
                        if not close(st[k], float(sr[k])):
                            mism.append({"func": fid, "stat": k,
                                         "summary": float(sr[k]), "recomputed": st[k]})
                summary_check[f"D{d}"] = {"n_compared": n_cmp, "n_mismatch": len(mism),
                                          "n_funcs_no_per_run": n_missing,
                                          "mismatches": mism[:8]}
        rec["summary_vs_per_run"] = summary_check

        # seed schedule hash
        rec["seed_schedule_sha256"] = sha256_file(cell / "seed_schedule.csv")
        cells.append(rec)

out["panel_cells"] = cells

# apgsk cec2017: recompute D10/30/50 from gen_logs final checkpoint
apgsk_cell = REF / "cec2017" / "apgsk"
apgsk_extra = {}
for d in (10, 30, 50):
    p = apgsk_cell / f"apgsk_cec2017_D{d}.csv"
    mism = []
    n_cmp = 0
    for sr in csv.DictReader(p.open(encoding="utf-8")):
        fid = int(str(sr["Function"]).lstrip("Ff"))
        gl = apgsk_cell / "gen_logs" / f"CheckpointErrors_apgsk_F{fid}_D{d}.csv"
        if not gl.exists():
            mism.append({"func": fid, "issue": "no gen_log"})
            continue
        finals = []
        for rr in csv.DictReader(gl.open(encoding="utf-8")):
            keys = [k for k in rr.keys() if k.startswith("E")]
            last = sorted(keys, key=lambda k: int(k[1:]))[-1]
            finals.append(float(rr[last]))
        a = np.asarray(finals, dtype=float)
        # display floor 1e-8 -> 0 may already be applied in logs; compare raw
        st = {"Best": float(a.min()), "Median": float(np.median(a)),
              "Mean": float(a.mean()), "Worst": float(a.max()),
              "SD": float(np.std(a, ddof=1)) if a.size >= 2 else 0.0,
              "n_runs": int(a.size)}
        for k in ("Best", "Median", "Mean", "Worst", "SD"):
            n_cmp += 1
            if not math.isclose(st[k], float(sr[k]), rel_tol=5e-10, abs_tol=1e-12):
                mism.append({"func": fid, "stat": k, "summary": float(sr[k]),
                             "from_genlog": st[k]})
    apgsk_extra[f"D{d}"] = {"n_compared": n_cmp, "n_mismatch": len(mism),
                            "mismatches": mism[:10]}
out["apgsk_cec2017_genlog_check"] = apgsk_extra

# ------------------------------------------------- 5. seed formula + identity
from gsk_family.runners.seed_policy import get_cec_seed  # noqa: E402
seed_checks = []
for suite, opts in PANEL:
    hashes = {}
    for opt in opts:
        cell = REF / suite / opt
        hashes[opt] = sha256_file(cell / "seed_schedule.csv")
    seed_checks.append({"suite": suite, "schedule_hashes": hashes,
                        "all_identical": len(set(hashes.values())) == 1})
# spot check formula against per_run rows
spot = []
for suite in ("cec2017", "cec2013", "cec2011"):
    cell = REF / suite / "dt-gsk"
    rows = list(csv.DictReader((cell / "per_run.csv").open(encoding="utf-8")))
    step = max(1, len(rows) // 25)
    ok = True
    n = 0
    for r in rows[::step]:
        n += 1
        expect = get_cec_seed(20240620, int(r["dimension"]), int(r["function"]), int(r["run"]))
        if int(r["seed"]) != int(expect):
            ok = False
            spot.append({"suite": suite, "row": r, "expected": int(expect)})
    spot.append({"suite": suite, "sampled": n, "all_match": ok})
out["seed_schedule_identity"] = seed_checks
out["seed_formula_spot_checks"] = spot

# ------------------------------------------------- 6. context cells
ctx = []
for suite, opts in CONTEXT:
    for opt in opts:
        cell = REF / suite / opt
        files = sorted(p.name for p in cell.iterdir())
        ctx.append({
            "suite": suite, "optimizer": opt, "files": files,
            "has_per_run": (cell / "per_run.csv").exists(),
            "has_environment": (cell / "environment.json").exists(),
            "has_run_config": (cell / "run_config.json").exists(),
            "has_seed_schedule": (cell / "seed_schedule.csv").exists(),
        })
out["context_cells"] = ctx

# egsk solver provenance markers
import gsk_family.optimizers.egsk as egsk_mod  # noqa: E402
egsk_src = Path(egsk_mod.__file__).read_text(encoding="utf-8")
out["egsk_solver_markers"] = {
    "uses_scipy_slsqp": "SLSQP" in egsk_src,
    "mentions_fmincon_reference": "fmincon" in egsk_src,
    "egsk_py_sha256": sha256_file(Path(egsk_mod.__file__)),
}

(SCRATCH / "phase2_tasks678_audit.json").write_text(
    json.dumps(out, indent=1, default=str), encoding="utf-8")
print("WROTE", SCRATCH / "phase2_tasks678_audit.json")
print("hash rows:", len(hash_rows))
print("cec2011 dim mismatches:", m11["dim_mismatches_vs_das2011_table1"])
print("cec2017 fopt rule 100*i:", m17["fopt_rule_100i"], "| cec2013 fopt rule:", m13["fopt_rule"])
for c in cells:
    sv = {k: (v["n_mismatch"], v.get("n_funcs_no_per_run", 0)) for k, v in c["summary_vs_per_run"].items()}
    over = {d: a["n_over"] for d, a in c["nfes_audit"].items()}
    print(f"{c['suite']:8s} {c['optimizer']:11s} rows={c['per_run_rows']:5d} dims={c['per_run_dims']} "
          f"F2={c['per_run_has_F2']} over={over} sum_mism={sv} verd={c['ver_verdict']}")
print("apgsk genlog check:", {k: (v["n_compared"], v["n_mismatch"]) for k, v in apgsk_extra.items()})
print("seed identity:", [(s["suite"], s["all_identical"]) for s in seed_checks])
print("spot:", [s for s in spot if "all_match" in s])
