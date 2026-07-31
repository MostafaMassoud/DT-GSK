#!/usr/bin/env python3
# Copyright (c) 2026 Mostafa Masoud <moustafa.masoud@gmail.com>
"""Re-time the six comparator algorithms on CEC2017 for runtime comparability.

WHY THIS EXISTS
---------------
The post-fix campaign re-ran DT-GSK with the interaction graph's compiled
kernels active (defect M038: an earlier release silently executed the
bit-for-bit-equivalent NumPy reference path).  Every scientific quantity was
reproduced byte-for-byte -- ``error``, ``best_fitness``, ``seed``, ``nfes``,
``termination`` are identical across all 5,916 rows -- but ``runtime_seconds``
fell substantially (D100: 69.04 -> 41.59 s, -39.8%).

The comparators were NOT re-run.  Table~\\ref{tab:runtime} in the manuscript
would therefore mix two measurement sessions: today's DT-GSK timings against
the original campaign's comparator timings.  Wall-clock is the one reported
quantity that is a property of the machine and build rather than of the
algorithm, so a mixed-provenance runtime table is not a valid comparison.

This script restores a single-environment comparison by re-timing the six
comparators on the same workstation.  Because the runners are deterministic,
this is a PURE TIMING REFRESH: the verify stage asserts that every scientific
column is reproduced exactly, and fails loudly if it is not.

SCOPE
-----
CEC2017 only -- that is the suite Table~\\ref{tab:runtime} reports.  CEC2013 and
CEC2011 carry no cross-algorithm runtime table (CEC2011 is cited only as a
panel-wide span, which this script's ``--suite cec2011`` mode can refresh later
if that sentence is retained).

COST (measured, from the existing evidence)
-------------------------------------------
    dt-gsk (already done)     34.0 core-hours
    6 comparators             227.7 core-hours   ~15-25 h wall-clock @ 15 workers

OPERATIONAL REQUIREMENT -- READ THIS
------------------------------------
Timing runs must not compete for CPU.  If the ablation/overlay campaign (or any
other load) is running concurrently, the measurements are contaminated and the
comparison is invalid *again* -- a full day spent for nothing.  The preflight
check below refuses to start when it detects an active campaign; override only
if you are certain the machine is otherwise idle.

USAGE
-----
    # 1. preflight only -- confirm the machine is quiet and show the plan
    python scripts/retime_comparators.py --status

    # 2. the run itself (long; consider a detached terminal)
    python scripts/retime_comparators.py --workers 15

    # 3. verify determinism + report timing deltas (also run automatically)
    python scripts/retime_comparators.py --verify-only

Nothing is promoted into ``benchmarks/cec_reference_results`` by this script.
Promotion is a separate, deliberate step taken only after the verify stage
reports GREEN.
"""
from __future__ import annotations

import argparse
import csv
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STAGE = ROOT / "results" / "_run_all"
REF = ROOT / "benchmarks" / "cec_reference_results"

COMPARATORS = ["gsk", "agsk", "apgsk", "fdb-agsk", "atmals-gsk", "egsk"]

# Mirrors run_campaign.PRIMARY for cec2017 exactly; the runtime table is
# CEC2017-only, so that is the default scope.
SUITE_SPEC = {
    "cec2017": dict(fsel="1:30", dsel="10,30,50,100", runs=51, curves=116),
    "cec2011": dict(fsel="1:22", dsel="native", runs=25, curves=22),
}

# Columns that MUST reproduce exactly. runtime_seconds is deliberately absent:
# it is the quantity we are re-measuring.
SCIENTIFIC_COLS = ["optimizer", "suite", "function", "dimension", "run",
                   "seed", "best_fitness", "error", "nfes", "termination"]

# Directories whose recent activity means a campaign is live.
CAMPAIGN_STAGES = ["_ablation", "_ablation_sgsm_cec2017_51", "_ablation_sgsm_51"]
IDLE_WINDOW_S = 600  # a write in the last 10 min == "campaign is running"


# --------------------------------------------------------------------------- #
# environment
# --------------------------------------------------------------------------- #
def pinned_env() -> dict:
    """Single-threaded numeric stack -- identical to run_campaign.pinned_env.

    Timing comparability depends on this: the original campaign measured every
    cell with one thread per worker, so the refresh must too.
    """
    env = os.environ.copy()
    for k in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS",
              "VECLIB_MAXIMUM_THREADS", "NUMEXPR_NUM_THREADS",
              "NUMBA_NUM_THREADS"):
        env[k] = "1"
    env["PYTHONIOENCODING"] = "utf-8"
    return env


# --------------------------------------------------------------------------- #
# preflight
# --------------------------------------------------------------------------- #
def active_campaigns() -> list[str]:
    """Staging trees written to within IDLE_WINDOW_S -- i.e. a live campaign."""
    now = time.time()
    hot = []
    for name in CAMPAIGN_STAGES:
        d = ROOT / "results" / name
        if not d.is_dir():
            continue
        newest = 0.0
        for p in d.rglob("*"):
            if p.is_file():
                newest = max(newest, p.stat().st_mtime)
        if newest and (now - newest) < IDLE_WINDOW_S:
            hot.append(f"{name} (last write {int(now - newest)}s ago)")
    return hot


def preflight(force: bool, inspect_only: bool = False) -> int:
    """Report machine quietness. Non-zero means 'do not start a timing run'."""
    print("=== preflight ===")
    hot = active_campaigns()
    if not hot:
        print("  IDLE  no campaign staging tree written in the last "
              f"{IDLE_WINDOW_S // 60} min")
        return 0

    print("  BUSY  a campaign appears to be running:")
    for h in hot:
        print(f"          - {h}")
    print("\n  Timing measurements taken while other work competes for CPU are")
    print("  contaminated, and the resulting table is not a valid comparison.")
    print("  Wait for the ablation/overlay campaign to finish, then re-run.")
    if inspect_only:
        print("\n  (--status: showing the plan anyway; nothing will be run.)")
    elif force:
        print("\n  --force given; proceeding despite detected activity.")
        return 0
    else:
        print("\n  Refusing to start. Pass --force only if the machine is idle.")
    return 1


# --------------------------------------------------------------------------- #
# run
# --------------------------------------------------------------------------- #
def cmd_for(algo: str, suite: str, workers: int) -> list[str]:
    """Byte-for-byte the campaign's primary_cmd, with the optimizer swapped."""
    spec = SUITE_SPEC[suite]
    return ["run.py", "--root", ".", "--optimizer", algo,
            "--suite", suite, "--function", spec["fsel"],
            "--dimension", spec["dsel"],
            "--runs", str(spec["runs"]), "--workers", str(workers),
            "--seed", "20240620", "--seed-policy", "unified",
            "--rand-generator", "threefry", "--benchmark-fp-mode", "default",
            "--benchmark-backend", "auto", "--convergence-graphs"]


def per_run_path(base: Path) -> Path:
    """Resolve per_run.csv under a cell dir, tolerating the summary/ layout.

    A fresh ``run.py`` writes ``<cell>/summary/per_run.csv`` (see
    run_experiment.py); promotion flattens that to ``<cell>/per_run.csv`` under
    benchmarks/cec_reference_results. So the staged side is nested and the
    reference side is flat. Mirror runners/verification.py: prefer summary/ when
    it exists, else the flat path. Without this the verify stage would look for
    the flat staged path, find nothing, and fail every comparator after a full
    run had in fact staged correctly under summary/.
    """
    nested = base / "summary" / "per_run.csv"
    return nested if nested.is_file() else base / "per_run.csv"


def already_complete(algo: str, suite: str) -> bool:
    """Staged cell has the full per_run.csv row count for this suite."""
    p = per_run_path(STAGE / algo / suite)
    if not p.is_file():
        return False
    ref = per_run_path(REF / suite / algo)
    if not ref.is_file():
        return False
    with p.open(encoding="utf-8", newline="") as fh:
        n = sum(1 for _ in csv.DictReader(fh))
    with ref.open(encoding="utf-8", newline="") as fh:
        want = sum(1 for _ in csv.DictReader(fh))
    return n == want


def do_run(algos: list[str], suite: str, workers: int) -> int:
    for i, algo in enumerate(algos, 1):
        if already_complete(algo, suite):
            print(f"\n[skip] {algo}/{suite} already staged and complete")
            continue
        cmd = cmd_for(algo, suite, workers)
        print(f"\n>>> [{i}/{len(algos)}] {' '.join(cmd)}", flush=True)
        t0 = time.time()
        rc = subprocess.run([sys.executable, *cmd], cwd=str(ROOT),
                            env=pinned_env()).returncode
        dt = time.time() - t0
        if rc != 0:
            print(f"\nFAILED: {algo}/{suite} exited {rc} after {dt / 60:.1f} min.")
            print("Completed algorithms are skipped on re-run; fix and re-invoke.")
            return rc
        print(f"[done] {algo}/{suite} in {dt / 3600:.2f} h")
    return 0


# --------------------------------------------------------------------------- #
# verify -- the gate that makes this a *pure timing refresh*
# --------------------------------------------------------------------------- #
def _rows(p: Path) -> list[dict]:
    with p.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def verify(algos: list[str], suite: str) -> int:
    """Assert every scientific column reproduces; report runtime deltas only."""
    print(f"\n=== verify: determinism + timing delta ({suite}) ===")
    problems = 0
    compared = 0
    missing: list[str] = []
    print(f"  {'algorithm':12s} {'rows':>6s}  {'sci-cols':>9s}   "
          f"{'old s/run':>9s} {'new s/run':>9s} {'delta':>8s}")
    for algo in algos:
        new_p = per_run_path(STAGE / algo / suite)
        old_p = per_run_path(REF / suite / algo)
        if not new_p.is_file():
            print(f"  {algo:12s} {'--':>6s}  not staged yet")
            missing.append(algo)
            continue
        compared += 1
        new, old = _rows(new_p), _rows(old_p)
        if len(new) != len(old):
            print(f"  {algo:12s} {len(new):6d}  ROW-COUNT MISMATCH "
                  f"(reference has {len(old)})")
            problems += 1
            continue

        # key on the run identity so ordering differences cannot mask a defect
        def key(r):
            return (r["function"], r["dimension"], r["run"])
        old_by = {key(r): r for r in old}
        mismatched = []
        for r in new:
            o = old_by.get(key(r))
            if o is None:
                mismatched.append((key(r), "missing in reference"))
                continue
            for c in SCIENTIFIC_COLS:
                if r.get(c) != o.get(c):
                    mismatched.append((key(r), f"{c}: {o.get(c)} -> {r.get(c)}"))

        old_rt = sum(float(r["runtime_seconds"]) for r in old) / len(old)
        new_rt = sum(float(r["runtime_seconds"]) for r in new) / len(new)
        pct = (new_rt - old_rt) / old_rt * 100 if old_rt else 0.0
        verdict = "identical" if not mismatched else f"{len(mismatched)} DIFF"
        print(f"  {algo:12s} {len(new):6d}  {verdict:>9s}   "
              f"{old_rt:9.2f} {new_rt:9.2f} {pct:+7.1f}%")
        if mismatched:
            problems += len(mismatched)
            for k, why in mismatched[:5]:
                print(f"      f{k[0]} D{k[1]} run{k[2]}: {why}")
            if len(mismatched) > 5:
                print(f"      ... and {len(mismatched) - 5} more")

    if problems:
        print(f"\n  FAILED: {problems} scientific-column difference(s).")
        print("  This is NOT a pure timing refresh -- do not promote. A change in")
        print("  error/best_fitness/nfes means the run is not reproducing the")
        print("  frozen evidence, which is a correctness defect, not a timing one.")
        return 1

    # A green verdict must never be reported over an empty comparison: "nothing
    # was checked" and "everything checked out" are different states, and only
    # the second one licenses promotion.
    if missing:
        print(f"\n  INCOMPLETE: {len(missing)} of {len(algos)} comparator(s) not "
              f"staged ({', '.join(missing)}).")
        print("  A runtime table needs every panel row measured in the same")
        print("  session; a partial refresh reintroduces the mixed provenance")
        print("  this run exists to remove. Not a pass -- finish the run first.")
        return 1

    print(f"\n  OK - all {compared} comparator(s) reproduced every scientific "
          "column exactly;")
    print("  only runtime_seconds differs. Safe to promote as a timing refresh.")
    return 0


# --------------------------------------------------------------------------- #
def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__.splitlines()[0],
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--workers", type=int, default=15)
    ap.add_argument("--suite", default="cec2017", choices=sorted(SUITE_SPEC))
    ap.add_argument("--algorithms", default=",".join(COMPARATORS),
                    help="comma-separated optimizer ids to re-time")
    ap.add_argument("--status", action="store_true",
                    help="preflight + plan only; run nothing")
    ap.add_argument("--verify-only", action="store_true",
                    help="skip the run; compare staged results to the reference")
    ap.add_argument("--force", action="store_true",
                    help="start even if a campaign appears to be running")
    args = ap.parse_args()

    algos = [a.strip() for a in args.algorithms.split(",") if a.strip()]

    if args.verify_only:
        return verify(algos, args.suite)

    # --status is an inspection mode: report the preflight verdict but still
    # show the plan, so the campaign that is currently blocking the run can be
    # inspected without waiting for it to finish.
    rc = preflight(args.force, inspect_only=args.status)
    if rc and not args.status:
        return rc

    print(f"\n=== plan: re-time {len(algos)} comparators on {args.suite} ===")
    spec = SUITE_SPEC[args.suite]
    for a in algos:
        state = "staged/complete" if already_complete(a, args.suite) else "to run"
        print(f"  {a:12s} {spec['runs']} runs x functions {spec['fsel']} "
              f"x D {spec['dsel']}   [{state}]")
    print(f"  workers={args.workers}, single-threaded numeric stack (pinned)")
    print(f"  staging -> results/_run_all/<algo>/{args.suite}/summary/per_run.csv")
    print("  reference is NOT modified; promotion is a separate step")
    if args.status:
        return 0

    t0 = time.time()
    rc = do_run(algos, args.suite, args.workers)
    if rc:
        return rc
    print(f"\n=== all comparators staged in {(time.time() - t0) / 3600:.2f} h ===")
    return verify(algos, args.suite)


if __name__ == "__main__":
    sys.exit(main())
