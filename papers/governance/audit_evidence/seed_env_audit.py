"""Phase 2 Tasks 4-5: seed/pairing audit + FP/environment audit.

READ-ONLY over benchmarks/cec_reference_results/. Writes JSON summary to scratchpad only.
"""
from __future__ import annotations

import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(r"D:/AI/PhD-Projects/00-GSK-Family/02-GSK_Family_Python_v1.1")
EVID = ROOT / "benchmarks" / "cec_reference_results"
OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".") / "audit_out.json"

MAX_SAFE_SEED = 2_147_483_646

SUITES = {
    "cec2017": ["agsk", "apgsk", "atmals-gsk", "egsk", "fdb-agsk", "gsk", "dt-gsk"],
    "cec2011": ["agsk", "apgsk", "atmals-gsk", "egsk", "fdb-agsk", "gsk", "dt-gsk"],
    "cec2013": ["agsk", "apgsk", "atmals-gsk", "egsk", "fdb-agsk", "gsk", "dt-gsk"],
}
CONTEXT = {"cec2020": ["agsk"], "cec2013lsgo": ["decc-g", "mos"]}


def get_cec_seed(base_seed: int, dim: int, func: int, run: int) -> int:
    return (
        int(base_seed)
        + 1_000_003 * int(dim)
        + 1_000_033 * int(func)
        + 1_000_037 * int(run)
    ) % MAX_SAFE_SEED + 1


def load_schedule(path: Path):
    rows = []
    with open(path, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            rows.append((int(r["Dim"]), int(r["Function"]), int(r["Run"]), int(r["Seed"])))
    return rows


report = {"suites": {}, "env": {}, "cross_suite": {}, "context": {}, "file_mtimes_before": {}, "file_mtimes_after": {}}

# record mtimes of every file we will read, to prove read-only afterwards
files_to_watch = []
for suite, opts in SUITES.items():
    for opt in opts:
        base = EVID / suite / opt
        for name in ("seed_schedule.csv", "environment.json", "per_run.csv", "run_config.json"):
            p = base / name
            if p.exists():
                files_to_watch.append(p)
for p in files_to_watch:
    st = p.stat()
    report["file_mtimes_before"][str(p.relative_to(ROOT))] = (st.st_mtime_ns, st.st_size)

# ---------------- Task 4: seeds and pairing ----------------
schedule_maps = {}  # (suite, opt) -> {(dim,func,run): seed}
for suite, opts in SUITES.items():
    srep = {"optimizers": {}, "pairing": {}}
    for opt in opts:
        base = EVID / suite / opt
        sched_path = base / "seed_schedule.csv"
        env = json.load(open(base / "environment.json", encoding="utf-8"))
        runcfg_path = base / "run_config.json"
        runcfg = json.load(open(runcfg_path, encoding="utf-8")) if runcfg_path.exists() else {}
        base_seed = int(env.get("base_seed", 20240620))
        rows = load_schedule(sched_path)

        # deterministic mapping: duplicate keys
        keys = [(d, f, r) for d, f, r, _ in rows]
        dup_keys = len(keys) - len(set(keys))

        # full recompute of every row
        mismatches = []
        for d, f, r, s in rows:
            exp = get_cec_seed(base_seed, d, f, r)
            if exp != s:
                mismatches.append({"dim": d, "func": f, "run": r, "seed": s, "expected": exp})
                if len(mismatches) >= 10:
                    break
        n_mismatch = 0
        for d, f, r, s in rows:
            if get_cec_seed(base_seed, d, f, r) != s:
                n_mismatch += 1

        # seed uniqueness (global within schedule) and within-cell
        seeds = [s for _, _, _, s in rows]
        seed_dupes = len(seeds) - len(set(seeds))
        cell_runs = defaultdict(set)
        cell_dupe = 0
        for d, f, r, s in rows:
            if s in cell_runs[(d, f)]:
                cell_dupe += 1
            cell_runs[(d, f)].add(s)

        # coverage
        dims = sorted({d for d, _, _, _ in rows})
        funcs = sorted({f for _, f, _, _ in rows})
        runs = sorted({r for _, _, r, _ in rows})

        # per_run.csv cross-check
        per_run_path = base / "per_run.csv"
        pr_mismatch = 0
        pr_missing_in_sched = 0
        pr_rows = 0
        pr_first_mismatches = []
        smap = {(d, f, r): s for d, f, r, s in rows}
        pr_keys = set()
        with open(per_run_path, newline="", encoding="utf-8") as fh:
            for rec in csv.DictReader(fh):
                pr_rows += 1
                k = (int(rec["dimension"]), int(rec["function"]), int(rec["run"]))
                pr_keys.add(k)
                s = int(rec["seed"])
                if k not in smap:
                    pr_missing_in_sched += 1
                elif smap[k] != s:
                    pr_mismatch += 1
                    if len(pr_first_mismatches) < 5:
                        pr_first_mismatches.append({"key": k, "per_run_seed": s, "sched_seed": smap[k]})
        sched_not_in_pr = len(set(smap) - pr_keys)

        # run_config strides vs canonical
        stride_ok = (
            runcfg.get("stride_run") == 1000037
            and runcfg.get("dim_stride") == 1000003
            and runcfg.get("func_stride") == 1000033
        ) if runcfg else None

        srep["optimizers"][opt] = {
            "schedule_rows": len(rows),
            "dup_keys": dup_keys,
            "recompute_mismatches": n_mismatch,
            "first_mismatches": mismatches,
            "seed_value_duplicates_global": seed_dupes,
            "seed_value_duplicates_within_cell": cell_dupe,
            "dims": dims,
            "n_funcs": len(funcs),
            "funcs": funcs,
            "runs_min_max_n": [min(runs), max(runs), len(runs)],
            "base_seed": base_seed,
            "seed_policy_env": env.get("seed_policy", "")[:60],
            "run_config_seed_policy": runcfg.get("seed_policy"),
            "run_config_strides_ok": stride_ok,
            "per_run_rows": pr_rows,
            "per_run_seed_mismatches": pr_mismatch,
            "per_run_first_mismatches": pr_first_mismatches,
            "per_run_keys_missing_in_schedule": pr_missing_in_sched,
            "schedule_keys_missing_in_per_run": sched_not_in_pr,
        }
        schedule_maps[(suite, opt)] = smap

    # pairing: compare each optimizer's map to dt-gsk (and all-pairs identity)
    ref_opt = "dt-gsk"
    ref_map = schedule_maps[(suite, ref_opt)]
    pairing = {}
    for opt in opts:
        m = schedule_maps[(suite, opt)]
        same_keys = set(m) == set(ref_map)
        if same_keys:
            diff = sum(1 for k in ref_map if m[k] != ref_map[k])
        else:
            shared = set(m) & set(ref_map)
            diff = sum(1 for k in shared if m[k] != ref_map[k])
        pairing[opt] = {
            "same_key_set_as_ism_gsk": same_keys,
            "n_keys": len(m),
            "seed_differences_vs_ism_gsk": diff,
        }
    all_identical = all(
        schedule_maps[(suite, o)] == ref_map for o in opts
    )
    srep["pairing"] = pairing
    srep["all_seven_schedules_identical"] = all_identical
    report["suites"][suite] = srep

# cross-suite: overlap of (dim,func,run) keys between cec2013 and cec2017 (gsk as rep)
m17 = schedule_maps[("cec2017", "gsk")]
m13 = schedule_maps[("cec2013", "gsk")]
shared = set(m17) & set(m13)
same_seed = sum(1 for k in shared if m17[k] == m13[k])
report["cross_suite"]["cec2013_cec2017_shared_keys"] = len(shared)
report["cross_suite"]["cec2013_cec2017_same_seed"] = same_seed
m11 = schedule_maps[("cec2011", "gsk")]
shared11 = (set(m11) & set(m17)) | (set(m11) & set(m13))
report["cross_suite"]["cec2011_overlap_keys_with_2013_2017"] = len(shared11)
report["cross_suite"]["cec2011_same_seed_on_overlap"] = sum(
    1 for k in shared11 if m11.get(k) == m17.get(k, m13.get(k))
)

# ---------------- Task 5: environment / FP ----------------
env_fields = [
    "optimizer", "suite", "runs", "base_seed", "rand_generator",
    "initial_population_policy", "max_nfes_override", "statistics_basis",
    "benchmark_backend", "benchmark_fp_mode", "python_version", "cpu_cores",
    "computer", "platform", "git_commit", "timestamp", "runtime_seconds_total",
    "parallel_backend", "workers", "use_parallel", "warmup_enabled",
]
for suite, opts in SUITES.items():
    report["env"][suite] = {}
    for opt in opts:
        base = EVID / suite / opt
        env = json.load(open(base / "environment.json", encoding="utf-8"))
        e = {k: env.get(k) for k in env_fields}
        e["skipped_cells"] = env.get("skipped_cells")
        e["optimizer_notes"] = env.get("optimizer_notes")
        e["optimizer_options"] = env.get("optimizer_options")
        e["command"] = env.get("command")
        nr = env.get("numba_runtime", {}) or {}
        e["numba_version"] = nr.get("numba_version")
        e["suite_jit_enabled"] = nr.get("suite_jit_enabled")
        e["numba_threads_active"] = nr.get("numba_threads_active")
        fp = env.get("fp_regime", {}) or {}
        e["fp_suite"] = fp.get("suite")
        e["fp_jit_complete"] = fp.get("jit_complete")
        e["fp_numba_version"] = fp.get("numba_version")
        e["fp_llvmlite_version"] = fp.get("llvmlite_version")
        e["fp_probe_cell"] = fp.get("probe_cell")
        e["fp_probes"] = fp.get("probes")
        e["fp_sentinel"] = fp.get("sentinel")
        e["fp_kernel_flags"] = fp.get("kernel_flags")
        e["checkpoint_fractions_n"] = len(env.get("checkpoint_fractions", []) or [])
        e["dimensions_run"] = env.get("dimensions_run")
        e["functions_n"] = len(env.get("functions", []) or [])
        report["env"][suite][opt] = e

# sentinel consistency per suite
report["sentinel_check"] = {}
for suite in SUITES:
    sentinels = {opt: report["env"][suite][opt]["fp_sentinel"] for opt in SUITES[suite]}
    uniq = sorted(set(sentinels.values()), key=lambda x: (x is None, x))
    report["sentinel_check"][suite] = {
        "unique_sentinels": uniq,
        "consistent": len(uniq) == 1,
        "per_optimizer": sentinels,
    }
report["sentinel_check"]["cec2017_prefix_8bda40d8"] = (
    report["sentinel_check"]["cec2017"]["unique_sentinels"][0].startswith("8bda40d8")
    if report["sentinel_check"]["cec2017"]["unique_sentinels"] else False
)

# probe consistency per suite (threefry + suite probes must match across optimizers)
report["probe_check"] = {}
for suite in SUITES:
    probes = {opt: (report["env"][suite][opt]["fp_probes"] or {}) for opt in SUITES[suite]}
    tf = {opt: p.get("threefry") for opt, p in probes.items()}
    sp = {opt: p.get("suite") for opt, p in probes.items()}
    other = {opt: {k: v for k, v in p.items() if k not in ("threefry", "suite")} for opt, p in probes.items()}
    report["probe_check"][suite] = {
        "threefry_consistent": len(set(tf.values())) == 1,
        "suite_probe_consistent": len(set(sp.values())) == 1,
        "threefry": tf,
        "suite_probe": sp,
        "optimizer_specific_probes": other,
    }

# context suites: inventory only
for suite, opts in CONTEXT.items():
    report["context"][suite] = {}
    for opt in opts:
        base = EVID / suite / opt
        files = sorted(p.name for p in base.iterdir()) if base.exists() else []
        report["context"][suite][opt] = {
            "files": files,
            "has_environment_json": "environment.json" in files,
            "has_seed_schedule": "seed_schedule.csv" in files,
        }

# read-only proof
for p in files_to_watch:
    st = p.stat()
    report["file_mtimes_after"][str(p.relative_to(ROOT))] = (st.st_mtime_ns, st.st_size)
report["evidence_tree_untouched"] = report["file_mtimes_before"] == report["file_mtimes_after"]

OUT.parent.mkdir(parents=True, exist_ok=True)
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(report, f, indent=1, default=str)
print("WROTE", OUT)

# concise console summary
for suite in SUITES:
    s = report["suites"][suite]
    print(f"== {suite} == all7identical={s['all_seven_schedules_identical']}")
    for opt, o in s["optimizers"].items():
        print(
            f"  {opt:11s} rows={o['schedule_rows']:5d} dupkeys={o['dup_keys']} "
            f"recompute_mm={o['recompute_mismatches']} seed_dupes={o['seed_value_duplicates_global']} "
            f"pr_rows={o['per_run_rows']:5d} pr_mm={o['per_run_seed_mismatches']} "
            f"pr_extra={o['per_run_keys_missing_in_schedule']} sched_extra={o['schedule_keys_missing_in_per_run']} "
            f"strides_ok={o['run_config_strides_ok']}"
        )
    print("  sentinel consistent:", report["sentinel_check"][suite]["consistent"],
          report["sentinel_check"][suite]["unique_sentinels"][0][:16] if report["sentinel_check"][suite]["unique_sentinels"] else None)
    pc = report["probe_check"][suite]
    print("  probes: threefry_consistent=", pc["threefry_consistent"], " suite_probe_consistent=", pc["suite_probe_consistent"])
print("cec2017 prefix 8bda40d8:", report["sentinel_check"]["cec2017_prefix_8bda40d8"])
print("cross-suite 2013/2017 shared keys:", report["cross_suite"]["cec2013_cec2017_shared_keys"],
      "same seed:", report["cross_suite"]["cec2013_cec2017_same_seed"])
print("evidence tree untouched:", report["evidence_tree_untouched"])
