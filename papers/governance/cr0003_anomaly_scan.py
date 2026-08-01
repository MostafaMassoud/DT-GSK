"""Phase 2 Tasks 1-3 audit: evidence-tree layout, CR-0003 anomaly taxonomy, coverage.

READ-ONLY over benchmarks/cec_reference_results/. All outputs written to scratchpad.
Anchor commit expected: 262fc16c91fbe5608a1a0b0c5df3cbcd009edc21.
"""
from __future__ import annotations

import csv
import json
import math
import os
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REF = ROOT / "benchmarks" / "cec_reference_results"
OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
OUT.mkdir(parents=True, exist_ok=True)

PRIMARY_SUITES = ["cec2017", "cec2011", "cec2013"]
CONTEXT_SUITES = {"cec2020": ["agsk"], "cec2013lsgo": ["decc-g", "mos"]}
OPTIMIZERS = ["agsk", "apgsk", "atmals-gsk", "egsk", "fdb-agsk", "gsk", "dt-gsk"]

PROTO = {
    "cec2017": {
        "funcs": [1] + list(range(3, 31)),
        "dims": [10, 30, 50, 100],
        "runs": 51,
        "maxfes": lambda d: 10000 * d,
    },
    "cec2013": {
        "funcs": list(range(1, 29)),
        "dims": [10, 30, 50],
        "runs": 51,
        "maxfes": lambda d: 10000 * d,
    },
    "cec2011": {
        "funcs": list(range(1, 23)),
        "dims": None,  # native dims derived from data, cross-checked across optimizers
        "runs": 25,
        "maxfes": lambda d: 150000,
    },
}

REQUIRED_FILES = [
    "per_run.csv",
    "environment.json",
    "run_config.json",
    "seed_schedule.csv",
    "verification.json",
    "phase0_protocol.json",
]
REQUIRED_DIRS = ["curves", "gen_logs"]

PER_RUN_HEADER = [
    "optimizer", "suite", "function", "dimension", "run", "seed",
    "best_fitness", "error", "nfes", "termination", "runtime_seconds",
]
SEED_HEADER = ["Dim", "Function", "Run", "Seed"]
SUMMARY_HEADER = ["Function", "Best", "Median", "Mean", "Worst", "SD"]
CURVE_HEADER = ["Eval", "BestError", "Log10Error"]

RE_SCI10_LOWER = re.compile(r"^-?\d\.\d{10}e[+-]\d{2,3}$")
RE_SCI10_UPPER = re.compile(r"^-?\d\.\d{10}E[+-]\d{2,3}$")
RE_INT = re.compile(r"^\d+$")
RE_RUNTIME = re.compile(r"^\d+\.\d+$")
SEED_MIN, SEED_MAX = 1, 2147483646
NEG_ERROR_FLOOR = -1e-06  # matches verification.json negative_error_floor

anomalies: list[dict] = []


def add_anomaly(aclass, severity, suite, optimizer, source, description, count=1, impact=""):
    anomalies.append({
        "anomaly_id": f"A2-{len(anomalies) + 1:03d}",
        "class": aclass,
        "severity": severity,
        "suite": suite,
        "optimizer": optimizer,
        "source_file": source,
        "description": description,
        "count": count,
        "impact": impact,
    })


def read_csv_rows(path: Path):
    with open(path, "r", newline="", encoding="utf-8-sig") as fh:
        return list(csv.reader(fh))


report = {"layout": {}, "coverage": {}, "validation": {}, "notes": []}

# ---------------------------------------------------------------- layout ----
print("=" * 78)
print("[1] EVIDENCE-TREE LAYOUT AUDIT")
print("=" * 78)

root_entries = sorted(p.name for p in REF.iterdir())
expected_root = sorted(PRIMARY_SUITES + list(CONTEXT_SUITES) + ["README.md"])
print(f"root entries: {root_entries}")
if root_entries != expected_root:
    extra = set(root_entries) - set(expected_root)
    missing = set(expected_root) - set(root_entries)
    add_anomaly("LAYOUT_UNEXPECTED", "hard", "-", "-", str(REF),
                f"root entries mismatch: extra={sorted(extra)} missing={sorted(missing)}",
                impact="tree scope differs from frozen expectation")
report["layout"]["root_entries"] = root_entries

# doubled-suite directories: any dir named cec* below the suite level
doubled = []
for dirpath, dirnames, _ in os.walk(REF):
    rel = Path(dirpath).relative_to(REF)
    depth = len(rel.parts)
    for d in dirnames:
        if re.match(r"^cec\d", d, re.IGNORECASE) and depth >= 1:
            doubled.append(str(rel / d))
print(f"doubled-suite directories: {doubled or 'NONE'}")
if doubled:
    add_anomaly("LAYOUT_UNEXPECTED", "hard", "-", "-", str(REF),
                f"doubled-suite directories found: {doubled}",
                count=len(doubled), impact="ambiguous evidence resolution")
report["layout"]["doubled_suite_dirs"] = doubled

# zero-byte files anywhere
zero_byte = [str(p.relative_to(REF)) for p in REF.rglob("*") if p.is_file() and p.stat().st_size == 0]
print(f"zero-byte files: {zero_byte or 'NONE'}")
for z in zero_byte:
    add_anomaly("EMPTY_FILE", "hard", "-", "-", z, "zero-byte file", impact="unreadable evidence")

# per-optimizer layout for primary suites
layout_table = {}
for suite in PRIMARY_SUITES:
    sdir = REF / suite
    opt_dirs = sorted(p.name for p in sdir.iterdir() if p.is_dir())
    if opt_dirs != OPTIMIZERS:
        add_anomaly("LAYOUT_UNEXPECTED", "hard", suite, "-", str(sdir),
                    f"optimizer dirs {opt_dirs} != expected {OPTIMIZERS}",
                    impact="panel incomplete or polluted")
    stray_files = sorted(p.name for p in sdir.iterdir() if p.is_file())
    if stray_files:
        add_anomaly("LAYOUT_UNEXPECTED", "soft", suite, "-", str(sdir),
                    f"stray files at suite level: {stray_files}", count=len(stray_files),
                    impact="unexpected non-optimizer content")
    for opt in opt_dirs:
        odir = sdir / opt
        files = sorted(p.name for p in odir.iterdir() if p.is_file())
        dirs = sorted(p.name for p in odir.iterdir() if p.is_dir())
        entry = {"files": len(files), "dirs": dirs}
        # required file classes
        missing = [f for f in REQUIRED_FILES if f not in files]
        if missing:
            add_anomaly("MISSING_FILE", "hard", suite, opt, str(odir),
                        f"missing required files: {missing}", count=len(missing),
                        impact="cell cannot be validated")
        if dirs != REQUIRED_DIRS:
            add_anomaly("LAYOUT_UNEXPECTED", "hard", suite, opt, str(odir),
                        f"subdirs {dirs} != expected {REQUIRED_DIRS}",
                        impact="missing curve/checkpoint evidence or extra dirs")
        # summary files
        proto = PROTO[suite]
        if suite == "cec2011":
            rollup = f"{opt}_{suite}.csv"
            dim_files = sorted(f for f in files if re.match(rf"^{re.escape(opt)}_{suite}_D\d+\.csv$", f))
            expected_summary = [rollup]
            entry["summary_files"] = ([rollup] if rollup in files else []) + dim_files
            if rollup not in files:
                add_anomaly("MISSING_FILE", "hard", suite, opt, str(odir),
                            f"missing rollup summary {rollup}", impact="suite summary missing")
        else:
            expected_summary = [f"{opt}_{suite}_D{d}.csv" for d in proto["dims"]]
            missing_sum = [f for f in expected_summary if f not in files]
            entry["summary_files"] = [f for f in expected_summary if f in files]
            if missing_sum:
                add_anomaly("MISSING_FILE", "hard", suite, opt, str(odir),
                            f"missing summary files: {missing_sum}", count=len(missing_sum),
                            impact="dimension summary missing")
        # unexpected extras
        known = set(REQUIRED_FILES) | set(entry.get("summary_files", []))
        if suite == "cec2011":
            known |= {f for f in files if re.match(rf"^{re.escape(opt)}_{suite}(_D\d+)?\.csv$", f)}
        extras = [f for f in files if f not in known]
        if extras:
            add_anomaly("LAYOUT_UNEXPECTED", "soft", suite, opt, str(odir),
                        f"unexpected extra files: {extras}", count=len(extras),
                        impact="non-canonical content in evidence tree")
        # curves / gen_logs counts and naming
        n_cells_expected = None
        if suite != "cec2011":
            n_cells_expected = len(proto["funcs"]) * len(proto["dims"])
        curves = sorted((odir / "curves").glob("*.csv")) if (odir / "curves").is_dir() else []
        genlogs = sorted((odir / "gen_logs").glob("*.csv")) if (odir / "gen_logs").is_dir() else []
        entry["curves"] = len(curves)
        entry["gen_logs"] = len(genlogs)
        layout_table[(suite, opt)] = entry
print(f"{'suite':<10}{'optimizer':<12}{'files':>6}{'curves':>8}{'gen_logs':>10}  summary_files")
for (suite, opt), e in layout_table.items():
    print(f"{suite:<10}{opt:<12}{e['files']:>6}{e['curves']:>8}{e['gen_logs']:>10}  {len(e.get('summary_files', []))}")
report["layout"]["primary"] = {f"{s}/{o}": e for (s, o), e in layout_table.items()}

# context suites
print("\ncontext suites:")
ctx_report = {}
for suite, opts in CONTEXT_SUITES.items():
    sdir = REF / suite
    actual_opts = sorted(p.name for p in sdir.iterdir() if p.is_dir())
    if actual_opts != sorted(opts):
        add_anomaly("LAYOUT_UNEXPECTED", "hard", suite, "-", str(sdir),
                    f"context optimizer dirs {actual_opts} != expected {sorted(opts)}",
                    impact="context scope drift")
    for opt in actual_opts:
        odir = sdir / opt
        files = sorted(p.name for p in odir.iterdir())
        ctx_report[f"{suite}/{opt}"] = files
        print(f"  {suite}/{opt}: {files}")
        raw_classes = [f for f in REQUIRED_FILES if f in files]
        if raw_classes:
            add_anomaly("LAYOUT_UNEXPECTED", "info", suite, opt, str(odir),
                        f"context cell unexpectedly carries raw classes: {raw_classes}",
                        impact="none; more evidence than expected")
report["layout"]["context"] = ctx_report

# CSV census
all_csv = list(REF.rglob("*.csv"))
census = Counter()
for p in all_csv:
    rel = p.relative_to(REF).parts
    if len(rel) >= 3 and rel[2] in ("curves", "gen_logs"):
        census[rel[2]] += 1
    elif p.name in ("per_run.csv", "seed_schedule.csv"):
        census[p.name] += 1
    else:
        census["summary"] += 1
print(f"\ncsv census: total={len(all_csv)} breakdown={dict(census)}")
report["layout"]["csv_census"] = {"total": len(all_csv), **dict(census)}

# ------------------------------------------------------- coverage + CR-0003 ----
print("\n" + "=" * 78)
print("[2] COVERAGE + CR-0003 ANOMALY TAXONOMY (primary suites)")
print("=" * 78)

TERMINATIONS = Counter()
coverage = {}
suite_seed_schedules = {}  # suite -> {opt: frozenset((dim,func,run,seed))}
suite_family_maps = {}     # suite -> first complete ss_map {(dim,func,run): seed}
cec2011_dim_maps = {}      # opt -> {func: dim}
env_provenance = {}        # suite/opt -> {timestamp, git_commit, dims_run}
PROTO_ENV_DIMS = {
    "cec2017": [10, 30, 50, 100],
    "cec2013": [10, 30, 50],
    "cec2011": [1, 6, 7, 12, 13, 15, 20, 22, 26, 30, 40, 96, 120, 126, 140, 240],
}

for suite in PRIMARY_SUITES:
    proto = PROTO[suite]
    funcs_expected = set(proto["funcs"])
    runs_expected = proto["runs"]
    dims_expected = set(proto["dims"]) if proto["dims"] else None
    n_cells = (len(funcs_expected) * len(dims_expected)) if dims_expected else len(funcs_expected)
    rows_expected = n_cells * runs_expected
    suite_seed_schedules[suite] = {}

    for opt in OPTIMIZERS:
        odir = REF / suite / opt
        tag = f"{suite}/{opt}"

        # ---- per_run.csv ----
        pr_path = odir / "per_run.csv"
        rows = read_csv_rows(pr_path)
        header, data = rows[0], rows[1:]
        if header != PER_RUN_HEADER:
            add_anomaly("CORRUPT_FILE", "hard", suite, opt, str(pr_path),
                        f"per_run header {header} != expected", impact="schema drift")
        key_counter = Counter()
        cell_runs = defaultdict(set)
        cell_seeds = defaultdict(list)
        seen_seeds_by_cell = {}
        per_run_seed_map = {}
        bad_fields = 0
        nan_error_rows = 0
        nan_other = 0
        inf_rows = 0
        early_stops = 0
        prec_bad = Counter()
        oop = Counter()
        func_dims = defaultdict(set)
        for i, r in enumerate(data, start=2):
            if len(r) != len(PER_RUN_HEADER):
                bad_fields += 1
                continue
            o, s, f_, d_, run_, seed_, bf, err, nfes, term, rt = r
            if o != opt:
                add_anomaly("UNEXPECTED_ALGORITHM_NAME", "hard", suite, opt, f"{pr_path}:{i}",
                            f"optimizer column '{o}' != directory '{opt}'",
                            impact="record attribution broken")
            if s != suite:
                add_anomaly("UNEXPECTED_ALGORITHM_NAME", "hard", suite, opt, f"{pr_path}:{i}",
                            f"suite column '{s}' != suite dir '{suite}'",
                            impact="record attribution broken")
            f, d, run, seed = int(f_), int(d_), int(run_), int(seed_)
            key = (f, d, run)
            key_counter[key] += 1
            cell_runs[(f, d)].add(run)
            cell_seeds[(f, d)].append(seed)
            per_run_seed_map[(d, f, run)] = seed
            func_dims[f].add(d)
            # precision / format
            if not (RE_SCI10_LOWER.match(bf) or bf == "NaN"):
                prec_bad["best_fitness"] += 1
            if not (RE_SCI10_LOWER.match(err) or err == "NaN"):
                prec_bad["error"] += 1
            if not RE_INT.match(nfes):
                prec_bad["nfes"] += 1
            if not RE_RUNTIME.match(rt):
                prec_bad["runtime_seconds"] += 1
            # NaN / Inf
            bfv = float(bf)
            errv = float(err)
            rtv = float(rt)
            if math.isnan(errv):
                nan_error_rows += 1
            if math.isnan(bfv) or math.isnan(rtv):
                nan_other += 1
            if math.isinf(bfv) or math.isinf(errv) or math.isinf(rtv):
                inf_rows += 1
            # out-of-protocol
            mf = proto["maxfes"](d)
            nfesv = int(nfes)
            if nfesv > mf:
                oop["nfes_gt_maxfes"] += 1
            elif nfesv != mf and term == "max_evaluations":
                oop["nfes_lt_maxfes_at_max_evaluations_termination"] += 1
            if term not in ("max_evaluations", "target_error_reached"):
                oop["unexpected_termination_value"] += 1
            if term == "target_error_reached":
                early_stops += 1
                if not math.isnan(errv) and errv > 1e-08:
                    oop["target_termination_but_error_above_1e-8"] += 1
            if not math.isnan(errv):
                if errv < NEG_ERROR_FLOOR:
                    oop["error_below_floor"] += 1
                elif errv < 0:
                    oop["error_slightly_negative"] += 1
            if rtv <= 0 or math.isnan(rtv) or math.isinf(rtv):
                oop["runtime_nonpositive"] += 1
            if not (SEED_MIN <= seed <= SEED_MAX):
                oop["seed_out_of_range"] += 1
            if f not in funcs_expected:
                oop["function_out_of_protocol"] += 1
            if dims_expected is not None and d not in dims_expected:
                oop["dimension_out_of_protocol"] += 1
            if not (1 <= run <= runs_expected):
                oop["run_index_out_of_protocol"] += 1
            TERMINATIONS[term] += 1
        if bad_fields:
            add_anomaly("TRUNCATED_ROW", "hard", suite, opt, str(pr_path),
                        f"{bad_fields} per_run rows with wrong field count",
                        count=bad_fields, impact="records unusable")
        # duplicates
        dups = {k: c for k, c in key_counter.items() if c > 1}
        if dups:
            add_anomaly("DUPLICATE_RECORD", "hard", suite, opt, str(pr_path),
                        f"duplicate (func,dim,run) keys, e.g. {list(dups)[:5]}",
                        count=len(dups), impact="double counting in statistics")
        dup_seed_cells = {c: [s for s, n in Counter(v).items() if n > 1]
                          for c, v in cell_seeds.items() if len(set(v)) != len(v)}
        if dup_seed_cells:
            add_anomaly("DUPLICATE_SEED", "hard", suite, opt, str(pr_path),
                        f"duplicate seeds inside cells: {list(dup_seed_cells.items())[:5]}",
                        count=len(dup_seed_cells), impact="runs not independent")
        # cross-cell seed collisions (informational)
        all_seeds = [s for v in cell_seeds.values() for s in v]
        cross_collisions = len(all_seeds) - len(set(all_seeds))
        # inconsistent run counts
        bad_cells = {c: sorted(v) for c, v in cell_runs.items()
                     if v != set(range(1, runs_expected + 1))}
        if bad_cells:
            add_anomaly("INCONSISTENT_RUN_COUNT", "hard", suite, opt, str(pr_path),
                        f"cells without exactly runs 1..{runs_expected}: {list(bad_cells)[:5]}",
                        count=len(bad_cells), impact="unbalanced panel cell")
        # function/dimension set
        funcs_actual = set(f for f, _ in cell_runs)
        if funcs_actual != funcs_expected:
            add_anomaly("COVERAGE_MISMATCH", "hard", suite, opt, str(pr_path),
                        f"function set mismatch: missing={sorted(funcs_expected - funcs_actual)} "
                        f"extra={sorted(funcs_actual - funcs_expected)}",
                        impact="panel coverage broken")
        dims_actual = sorted({d for _, d in cell_runs})
        if len(data) != rows_expected or len(cell_runs) != n_cells:
            add_anomaly("COVERAGE_MISMATCH", "hard", suite, opt, str(pr_path),
                        f"per_run rows {len(data)}/{rows_expected}, cells {len(cell_runs)}/{n_cells}; "
                        f"dims present={dims_actual}",
                        impact="per-run evidence absent for missing cells; paired per-run statistics "
                               "not computable from per_run.csv for the missing dims")
        if early_stops:
            add_anomaly("PROTOCOL_OBSERVATION", "info", suite, opt, str(pr_path),
                        f"target_error_reached early stops: {early_stops} runs "
                        f"(protocol-legitimate stopping rule; nfes<MaxFES by design)",
                        count=early_stops, impact="none; budget accounting per stopping rule")
        if suite == "cec2011":
            multi_dim = {f: sorted(v) for f, v in func_dims.items() if len(v) != 1}
            if multi_dim:
                add_anomaly("COVERAGE_MISMATCH", "hard", suite, opt, str(pr_path),
                            f"cec2011 problems with multiple dims: {multi_dim}",
                            impact="native-dimension rule violated")
            cec2011_dim_maps[opt] = {f: sorted(v)[0] for f, v in func_dims.items()}
        if prec_bad:
            add_anomaly("MIXED_PRECISION", "soft", suite, opt, str(pr_path),
                        f"non-canonical numeric formatting: {dict(prec_bad)}",
                        count=sum(prec_bad.values()),
                        impact="format drift; values still parseable")
        if nan_other:
            add_anomaly("NAN_INF", "hard", suite, opt, str(pr_path),
                        f"NaN in best_fitness/runtime: {nan_other} rows",
                        count=nan_other, impact="records unusable")
        if inf_rows:
            add_anomaly("NAN_INF", "hard", suite, opt, str(pr_path),
                        f"Inf values: {inf_rows} rows", count=inf_rows,
                        impact="records unusable")
        if nan_error_rows and suite != "cec2011":
            add_anomaly("NAN_INF", "hard", suite, opt, str(pr_path),
                        f"NaN error on optimum-referenced suite: {nan_error_rows} rows",
                        count=nan_error_rows, impact="error metric broken")
        if nan_error_rows and suite == "cec2011":
            add_anomaly("NAN_INF", "info", suite, opt, str(pr_path),
                        f"error=NaN on all {nan_error_rows} rows: real-world suite carries no "
                        f"defined-optimum error in per_run; by design",
                        count=nan_error_rows,
                        impact="cec2011 analyses must use best_fitness, not error")
        for k, c in oop.items():
            sev = "soft" if k in ("nfes_ne_maxfes", "error_slightly_negative") else "hard"
            add_anomaly("OUT_OF_PROTOCOL_VALUE", sev, suite, opt, str(pr_path),
                        f"{k}: {c} rows", count=c,
                        impact="protocol deviation" if sev == "hard" else "within tolerance floor")

        # ---- seed_schedule.csv ----
        ss_path = odir / "seed_schedule.csv"
        ss_rows = read_csv_rows(ss_path)
        if ss_rows[0] != SEED_HEADER:
            add_anomaly("CORRUPT_FILE", "hard", suite, opt, str(ss_path),
                        f"seed_schedule header {ss_rows[0]} != expected", impact="schema drift")
        ss_data = ss_rows[1:]
        ss_map = {}
        ss_dup = 0
        for r in ss_data:
            k = (int(r[0]), int(r[1]), int(r[2]))
            if k in ss_map:
                ss_dup += 1
            ss_map[k] = int(r[3])
        if ss_dup:
            add_anomaly("DUPLICATE_RECORD", "hard", suite, opt, str(ss_path),
                        f"{ss_dup} duplicate (dim,func,run) keys in seed_schedule",
                        count=ss_dup, impact="ambiguous seed assignment")
        # cross-check per_run vs schedule
        mismatch = sum(1 for k, v in per_run_seed_map.items() if ss_map.get(k) != v)
        missing_in_ss = sum(1 for k in per_run_seed_map if k not in ss_map)
        extra_in_ss = sum(1 for k in ss_map if k not in per_run_seed_map)
        if mismatch or missing_in_ss or extra_in_ss:
            add_anomaly("DUPLICATE_SEED", "hard", suite, opt, str(ss_path),
                        f"per_run/seed_schedule disagreement: mismatch={mismatch} "
                        f"missing_in_schedule={missing_in_ss} extra_in_schedule={extra_in_ss}",
                        impact="seed provenance broken")
        if len(ss_data) != rows_expected:
            add_anomaly("COVERAGE_MISMATCH", "hard", suite, opt, str(ss_path),
                        f"seed_schedule rows {len(ss_data)}/{rows_expected}",
                        impact="seed schedule incomplete for this cell")
        suite_seed_schedules[suite][opt] = frozenset((k[0], k[1], k[2], v) for k, v in ss_map.items())
        if suite not in suite_family_maps and len(ss_map) == rows_expected:
            suite_family_maps[suite] = ss_map

        # ---- environment.json / run_config.json metadata consistency ----
        env = json.load(open(odir / "environment.json"))
        rc = json.load(open(odir / "run_config.json"))
        env_dims = env.get("dimensions_run") or []
        rc_dims = rc.get("dims")
        rc_dims_list = rc_dims if isinstance(rc_dims, list) else [rc_dims]
        env_provenance[tag] = {"timestamp": env.get("timestamp"),
                               "git_commit": str(env.get("git_commit"))[:8],
                               "dims_run": env_dims}
        if sorted(env_dims) != PROTO_ENV_DIMS[suite] or sorted(rc_dims_list) != PROTO_ENV_DIMS[suite]:
            add_anomaly("METADATA_INCONSISTENT", "hard", suite, opt, str(odir),
                        f"environment/run_config dims {env_dims}/{rc_dims} != protocol "
                        f"{PROTO_ENV_DIMS[suite]}; env timestamp={env.get('timestamp')} "
                        f"git={str(env.get('git_commit'))[:8]}",
                        impact="cell metadata describes a partial rerun; environment/config "
                               "provenance for the other dims is not present in this cell")

        # ---- summary CSVs ----
        summary_issue = Counter()
        for sf in layout_table[(suite, opt)].get("summary_files", []):
            sp = odir / sf
            srows = read_csv_rows(sp)
            if srows[0] != SUMMARY_HEADER:
                add_anomaly("CORRUPT_FILE", "hard", suite, opt, str(sp),
                            f"summary header {srows[0]} != expected", impact="schema drift")
                continue
            n = len(srows) - 1
            m = re.match(rf"^{re.escape(opt)}_{suite}(?:_D(\d+))?\.csv$", sf)
            dim_tag = m.group(1)
            if suite == "cec2011":
                exp_n = 22 if dim_tag is None else None
            else:
                exp_n = len(proto["funcs"])
            if exp_n is not None and n != exp_n:
                add_anomaly("COVERAGE_MISMATCH", "hard", suite, opt, str(sp),
                            f"summary rows {n} != expected {exp_n}", impact="summary incomplete")
            for r in srows[1:]:
                if len(r) != 6:
                    summary_issue["ragged"] += 1
                    continue
                for v in r[1:]:
                    if not (RE_SCI10_UPPER.match(v) or v == "NaN"):
                        summary_issue["precision"] += 1
                    try:
                        fv = float(v)
                    except ValueError:
                        summary_issue["non_numeric"] += 1
                        continue
                    if math.isnan(fv) or math.isinf(fv):
                        summary_issue["nan_inf"] += 1
        if summary_issue.get("ragged"):
            add_anomaly("TRUNCATED_ROW", "hard", suite, opt, str(odir),
                        f"ragged summary rows: {summary_issue['ragged']}",
                        count=summary_issue["ragged"], impact="summary unusable")
        if summary_issue.get("precision"):
            add_anomaly("MIXED_PRECISION", "soft", suite, opt, str(odir),
                        f"summary precision deviations: {summary_issue['precision']}",
                        count=summary_issue["precision"], impact="format drift")
        if summary_issue.get("nan_inf"):
            add_anomaly("NAN_INF", "hard", suite, opt, str(odir),
                        f"NaN/Inf in summary stats: {summary_issue['nan_inf']}",
                        count=summary_issue["nan_inf"], impact="summary stat broken")

        # ---- gen_logs (checkpoint / truncated-convergence check) ----
        gl_dir = odir / "gen_logs"
        gl_files = sorted(gl_dir.glob("*.csv"))
        gl_cells = set()
        gl_trunc = 0
        gl_short = []
        gl_seed_mismatch = 0
        gl_seed_missing = 0
        gl_family_match = 0
        for g in gl_files:
            m = re.match(rf"^CheckpointErrors_{re.escape(opt)}_F(\d+)_D(\d+)\.csv$", g.name)
            if not m:
                add_anomaly("LAYOUT_UNEXPECTED", "soft", suite, opt, str(g),
                            "gen_log filename does not match canonical pattern",
                            impact="naming drift")
                continue
            f, d = int(m.group(1)), int(m.group(2))
            gl_cells.add((f, d))
            grows = read_csv_rows(g)
            gh = grows[0]
            if gh[:2] != ["Run", "Seed"] or not all(c.startswith("E") for c in gh[2:]):
                add_anomaly("CORRUPT_FILE", "hard", suite, opt, str(g),
                            f"gen_log header unexpected: {gh[:4]}...", impact="schema drift")
                continue
            last_cp = int(gh[-1][1:])
            if last_cp != proto["maxfes"](d):
                add_anomaly("OUT_OF_PROTOCOL_VALUE", "hard", suite, opt, str(g),
                            f"last checkpoint E{last_cp} != MaxFES {proto['maxfes'](d)}",
                            impact="budget mismatch")
            if len(grows) - 1 != runs_expected:
                gl_short.append((g.name, len(grows) - 1))
            for r in grows[1:]:
                if len(r) != len(gh) or any(v.strip() == "" for v in r):
                    gl_trunc += 1
                    continue
                k = (d, f, int(r[0]))
                sv = int(r[1])
                if k in ss_map:
                    if ss_map[k] != sv:
                        gl_seed_mismatch += 1
                else:
                    gl_seed_missing += 1
                    if suite_family_maps.get(suite, {}).get(k) == sv:
                        gl_family_match += 1
        if gl_short:
            add_anomaly("INCONSISTENT_RUN_COUNT", "hard", suite, opt, str(gl_dir),
                        f"gen_logs with wrong run rows (expected {runs_expected}): {gl_short[:5]}",
                        count=len(gl_short), impact="checkpoint evidence incomplete")
        if gl_trunc:
            add_anomaly("TRUNCATED_CONVERGENCE", "hard", suite, opt, str(gl_dir),
                        f"truncated/empty-field checkpoint rows: {gl_trunc}",
                        count=gl_trunc, impact="convergence evidence incomplete")
        if gl_seed_mismatch:
            add_anomaly("DUPLICATE_SEED", "hard", suite, opt, str(gl_dir),
                        f"gen_log seeds disagreeing with seed_schedule: {gl_seed_mismatch}",
                        count=gl_seed_mismatch, impact="seed provenance broken")
        if gl_seed_missing:
            add_anomaly("COVERAGE_MISMATCH", "hard", suite, opt, str(gl_dir),
                        f"gen_log run seeds for {gl_seed_missing} (dim,func,run) keys absent from "
                        f"this cell's seed_schedule; {gl_family_match}/{gl_seed_missing} match the "
                        f"family unified schedule",
                        count=gl_seed_missing,
                        impact="local schedule incomplete; original runs consistent with unified seeding")
        exp_cells = set((f, d) for f in funcs_expected
                        for d in (proto["dims"] or [cec2011_dim_maps.get(opt, {}).get(f)]))
        exp_cells = {(f, d) for f, d in exp_cells if d is not None}
        if gl_cells != exp_cells:
            add_anomaly("COVERAGE_MISMATCH", "hard", suite, opt, str(gl_dir),
                        f"gen_log cells: missing={sorted(exp_cells - gl_cells)[:5]} "
                        f"extra={sorted(gl_cells - exp_cells)[:5]}",
                        impact="checkpoint coverage incomplete")

        # ---- curves (representative convergence traces) ----
        cv_dir = odir / "curves"
        cv_files = sorted(cv_dir.glob("*.csv"))
        cv_cells = set()
        cv_issues = Counter()
        for c in cv_files:
            m = re.match(r"^Figure_F(\d+)_D(\d+)_Run#(\d+)\.csv$", c.name)
            if not m:
                add_anomaly("LAYOUT_UNEXPECTED", "soft", suite, opt, str(c),
                            "curve filename does not match canonical pattern",
                            impact="naming drift")
                continue
            f, d, run = int(m.group(1)), int(m.group(2)), int(m.group(3))
            if (f, d) in cv_cells:
                cv_issues["duplicate_cell"] += 1
            cv_cells.add((f, d))
            if not (1 <= run <= runs_expected):
                cv_issues["run_out_of_range"] += 1
            crows = read_csv_rows(c)
            if not crows or crows[0] != CURVE_HEADER:
                cv_issues["bad_header"] += 1
                continue
            if len(crows) < 2:
                cv_issues["no_data"] += 1
                continue
            prev = -1
            ragged = False
            uses_empty_log10 = False
            for r in crows[1:]:
                if len(r) != 3:
                    ragged = True
                    break
                ev, be, lg = r
                if ev.strip() == "" or be.strip() == "":
                    ragged = True
                    break
                if lg.strip() == "":
                    # writer convention: Log10Error left empty when BestError <= 0
                    try:
                        bev = float(be)
                    except ValueError:
                        ragged = True
                        break
                    if bev <= 0:
                        uses_empty_log10 = True
                    else:
                        ragged = True
                        break
                e = int(float(ev))
                if e <= prev:
                    cv_issues["non_monotonic_eval"] += 1
                    break
                prev = e
            if ragged:
                cv_issues["ragged_rows"] += 1
                continue
            if uses_empty_log10:
                cv_issues["empty_log10_when_besterror_le_0"] += 1
            if prev != proto["maxfes"](d):
                cv_issues["last_eval_ne_maxfes"] += 1
        for k, cnt in cv_issues.items():
            if k == "empty_log10_when_besterror_le_0":
                add_anomaly("PROTOCOL_OBSERVATION", "info", suite, opt, str(cv_dir),
                            f"{cnt} curve files leave Log10Error empty where BestError<=0 "
                            f"(log10 undefined); systematic writer convention",
                            count=cnt,
                            impact="log-scale plots need a disclosed display floor (Section 6.7); "
                                   "values themselves intact")
                continue
            sev = "soft" if k == "last_eval_ne_maxfes" else "hard"
            add_anomaly("TRUNCATED_CONVERGENCE", sev, suite, opt, str(cv_dir),
                        f"curve issue {k}: {cnt} files", count=cnt,
                        impact="convergence trace truncated" if sev == "hard"
                        else "trace ends before MaxFES (early-stop or checkpoint policy)")
        if cv_cells != exp_cells:
            add_anomaly("COVERAGE_MISMATCH", "hard", suite, opt, str(cv_dir),
                        f"curve cells: missing={sorted(exp_cells - cv_cells)[:5]} "
                        f"extra={sorted(cv_cells - exp_cells)[:5]}",
                        impact="figure coverage incomplete")

        coverage[tag] = {
            "per_run_rows_expected": rows_expected,
            "per_run_rows_actual": len(data),
            "seed_rows_expected": rows_expected,
            "seed_rows_actual": len(ss_data),
            "cells_expected": n_cells,
            "cells_actual": len(cell_runs),
            "runs_per_cell_ok": not bad_cells,
            "cross_cell_seed_collisions": cross_collisions,
            "nan_error_rows": nan_error_rows,
        }
        print(f"{tag:<22} per_run {len(data)}/{rows_expected}  seeds {len(ss_data)}/{rows_expected}  "
              f"cells {len(cell_runs)}/{n_cells}  runs_ok={not bad_cells}  "
              f"xcell_seed_coll={cross_collisions}  nan_err={nan_error_rows}")

# cec2011 native dim map consistency across optimizers
ref_map = cec2011_dim_maps[OPTIMIZERS[0]]
for opt, m in cec2011_dim_maps.items():
    if m != ref_map:
        add_anomaly("COVERAGE_MISMATCH", "hard", "cec2011", opt, "per_run.csv",
                    f"native dim map differs from {OPTIMIZERS[0]}",
                    impact="cross-optimizer comparability broken")
print(f"\ncec2011 native dim map (consistent across all 7 optimizers): {ref_map}")
report["coverage"] = coverage
report["coverage_cec2011_dim_map"] = ref_map

# unified seed schedule across optimizers (pairing precondition; informational here)
for suite in PRIMARY_SUITES:
    scheds = suite_seed_schedules[suite]
    base = scheds[OPTIMIZERS[0]]
    diff_opts = [o for o, s in scheds.items() if s != base]
    if diff_opts:
        add_anomaly("DUPLICATE_SEED", "hard", suite, ",".join(diff_opts), "seed_schedule.csv",
                    "seed schedules differ across optimizers despite unified policy",
                    impact="pairing assumption broken")
    print(f"{suite}: seed schedules identical across 7 optimizers = {not diff_opts}")
    report["validation"][f"{suite}_unified_schedule"] = not diff_opts

print(f"\ntermination values observed: {dict(TERMINATIONS)}")
report["validation"]["termination_values"] = dict(TERMINATIONS)

# ---------------------------------------------------- context-suite scan ----
print("\ncontext-suite content scan:")
for suite, opts in CONTEXT_SUITES.items():
    for opt in opts:
        for p in sorted((REF / suite / opt).glob("*.csv")):
            rows = read_csv_rows(p)
            n = len(rows) - 1
            issues = Counter()
            if rows[0] != SUMMARY_HEADER:
                issues["bad_header"] += 1
            for r in rows[1:]:
                if len(r) != 6:
                    issues["ragged"] += 1
                    continue
                for v in r[1:]:
                    try:
                        fv = float(v)
                    except ValueError:
                        issues[f"non_numeric_token[{v}]"] += 1
                        continue
                    if math.isnan(fv) or math.isinf(fv):
                        issues["nan_inf"] += 1
            print(f"  {suite}/{opt}/{p.name}: rows={n} issues={dict(issues) or 'none'}")
            for k, cnt in issues.items():
                if k == "bad_header":
                    cls, sev, imp = "CORRUPT_FILE", "hard", "context summary defective"
                elif k == "ragged":
                    cls, sev, imp = "TRUNCATED_ROW", "hard", "context summary defective"
                elif k.startswith("non_numeric"):
                    cls, sev = "NAN_INF", "soft"
                    imp = "missing-value token in imported context summary; context-only, not in primary panel"
                else:
                    cls, sev, imp = "NAN_INF", "hard", "context summary defective"
                add_anomaly(cls, sev, suite, opt, str(p), f"{k}: {cnt}", count=cnt, impact=imp)

# --------------------------------------------------- verification.json ----
print("\nverification.json verdicts:")
ver_table = {}
for suite in PRIMARY_SUITES:
    for opt in OPTIMIZERS:
        vp = REF / suite / opt / "verification.json"
        v = json.load(open(vp))
        ver_table[f"{suite}/{opt}"] = {
            "verdict": v.get("verdict"),
            "functions_checked": v.get("functions_checked"),
            "hard_failures": v.get("hard_failures"),
            "missing_reference": v.get("missing_reference"),
        }
        print(f"  {suite}/{opt}: {v.get('verdict')} checked={v.get('functions_checked')} "
              f"hard_failures={v.get('hard_failures')} missing_ref={v.get('missing_reference')}")
        if v.get("verdict") != "CONSISTENT" or v.get("hard_failures", 0) != 0:
            add_anomaly("OUT_OF_PROTOCOL_VALUE", "hard", suite, opt, str(vp),
                        f"verification verdict {v.get('verdict')}, hard_failures={v.get('hard_failures')}",
                        impact="cell failed its own release verification")
        if v.get("functions_checked", 0) == 0:
            add_anomaly("VERIFICATION_VACUOUS", "info", suite, opt, str(vp),
                        f"verification checked 0 functions (missing_reference="
                        f"{v.get('missing_reference')}); verdict vacuously CONSISTENT",
                        impact="no external reference cross-check exists for this suite cell; "
                               "equivalence relies on Phase 2 tasks 6 and 8")
report["validation"]["verification_json"] = ver_table

# fp sentinel audit-target check (light; full FP audit is Phase 2 task 5)
def find_sentinel(obj):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == "sentinel" and isinstance(v, str):
                return v
            r = find_sentinel(v)
            if r:
                return r
    return None

print("\nfp_regime sentinel (audit target only):")
sentinels = defaultdict(set)
for suite in PRIMARY_SUITES:
    for opt in OPTIMIZERS:
        env = json.load(open(REF / suite / opt / "environment.json"))
        s = find_sentinel(env.get("fp_regime", {}))
        sentinels[suite].add(s)
for suite, vals in sentinels.items():
    ok = len(vals) == 1 and None not in vals
    v0 = next(iter(vals)) if vals else None
    prefix_ok = (suite != "cec2017") or (v0 or "").startswith("8bda40d8")
    print(f"  {suite}: unique={ok} value_prefix={(v0 or 'MISSING')[:16]} cec2017_prefix_ok={prefix_ok}")
    if not ok:
        add_anomaly("OUT_OF_PROTOCOL_VALUE", "hard", suite, "-", "environment.json",
                    f"fp sentinel not suite-consistent: {sorted(str(x)[:16] for x in vals)}",
                    impact="mixed FP regimes inside one suite")
    if suite == "cec2017" and not prefix_ok:
        add_anomaly("OUT_OF_PROTOCOL_VALUE", "soft", suite, "-", "environment.json",
                    f"cec2017 sentinel prefix {(v0 or '')[:8]} != expected 8bda40d8",
                    impact="audit-target mismatch; full FP audit in task 5")
    report["validation"][f"{suite}_sentinel_prefix"] = (v0 or "")[:16]

# ------------------------------------------------------------- register ----
print("\n" + "=" * 78)
print("[3] ANOMALY REGISTER")
print("=" * 78)
if not anomalies:
    print("NO ANOMALIES DETECTED under the CR-0003 taxonomy.")
for a in anomalies:
    print(f"{a['anomaly_id']} [{a['severity'].upper():<4}] {a['class']:<26} "
          f"{a['suite']}/{a['optimizer']}: {a['description']} (n={a['count']})")

hard_n = sum(1 for a in anomalies if a["severity"] == "hard")
soft_n = sum(1 for a in anomalies if a["severity"] == "soft")
info_n = sum(1 for a in anomalies if a["severity"] == "info")
print(f"\nTOTALS: hard={hard_n} soft={soft_n} info={info_n}")
report["anomalies"] = anomalies
report["anomaly_totals"] = {"hard": hard_n, "soft": soft_n, "info": info_n}
report["env_provenance"] = env_provenance

with open(OUT / "phase2_audit_report.json", "w", encoding="utf-8") as fh:
    json.dump(report, fh, indent=1, default=str)
with open(OUT / "phase2_anomaly_register.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=["anomaly_id", "class", "severity", "suite", "optimizer",
                                       "source_file", "description", "count", "impact"])
    w.writeheader()
    w.writerows(anomalies)
print(f"\nwrote {OUT / 'phase2_audit_report.json'} and {OUT / 'phase2_anomaly_register.csv'}")
