#!/usr/bin/env python3
"""ONE-command, RESUMABLE driver for the four reviewer-requested experiments.

Journal round-1 major revision of algorithms-4507562 (D-0047, CR-0023). Six of
the ten reviewer points closed without new runs; these are the four that did
not.

    E1  R2.3        refinement-basis contrast (coordinate arm)        2,958 runs
    E2  R1.3/R2.2   DT-GSK at the comparators' NP = 100               5,916 runs
    E3  R2.1        uniform vs tiered configuration (two arms)       11,832 runs
    E4  R2.7        parameter sensitivity (27 one-factor cells)      11,745 runs
                                                                    -----------
                                                                     32,451 runs

Run ``--dry-run`` for the authoritative per-leg breakdown; the plan is derived
from the profiles at runtime, so these totals are indicative, not a promise.
One E4 cell is skipped automatically because its perturbation would land on the
frozen value (interaction_update_period is already 1 at D=30).

Usage
-----
    python scripts/run_revision_experiments.py

That is the whole command. Leave it running; it is resumable, so if it is
interrupted -- Ctrl-C, a reboot, a power cut -- re-running the identical line
picks up from the first incomplete cell instead of repeating finished work.
Every leg writes ``overwrite: false``.

    python scripts/run_revision_experiments.py --status     # progress, no runs
    python scripts/run_revision_experiments.py --only E1,E2 # a subset
    python scripts/run_revision_experiments.py --workers 8  # fewer workers
    python scripts/run_revision_experiments.py --dry-run    # plan only

Progress is appended to ``results/_revision/driver.log`` as well as printed, so
a detached run can be followed with ``Get-Content -Wait`` / ``tail -f``.

Why E1 is driven differently
----------------------------
E1 needs the final polish to search along the coordinate axes while everything
else -- including ISM -- stays exactly as shipped. The core exposes that as the
keyword-only research hook ``research_oracle_basis``; the public adapter
deliberately does NOT forward it, and ``tests/regression/
test_dormant_mechanisms_unreachable.py`` exists to keep it unreachable from
every config, profile, CLI and adapter path. That test also pins the adapter's
source text, and ``dt_gsk.py`` is hash-gated by validate_provenance_claims, so
E1 cannot be expressed as a YAML config without breaking a gate.

The tripwire scans ``src/gsk_family`` only, and its docstring records that
making the hooks reachable "requires a new evidence release" -- which is
precisely what E1 is. So E1 runs from here, outside the shipped surface,
reusing the shipped seed schedule and output writers so its cells pair with the
frozen bank exactly. Nothing under ``src/`` is modified.

Outputs
-------
``results/_revision/<leg>/`` -- staging, never ``benchmarks/``. Promotion into
an evidence release is a separate, deliberate step.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import os
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SRC = REPO / "src"

SUITE = "cec2017"
BASE_SEED = 20240620

# --- real campaign -----------------------------------------------------------
OUT_ROOT = REPO / "results" / "_revision"
RUNS_FULL = 51          # panel convention, for E1-E3
RUNS_SENS = 15          # E4 is explicitly a "limited" study: fewer runs, all functions
DIMS_FULL = [10, 30, 50, 100]
DIMS_E1 = [50, 100]     # the overlay's ISM-active tiers
DIMS_E4 = [30, 100]
FUNCTIONS = "default"   # the 29 scored functions (F2 withdrawn)
MAX_EVALS = 0           # 0 = the suite's own protocol budget

# --- smoke mode (--smoke) ----------------------------------------------------
# Same code path, drastically reduced scope: proves every leg KIND actually
# executes and writes rows before anyone commits ~30 hours to the real thing.
# Writes to a SEPARATE root so it can never contaminate campaign results.
SMOKE_OUT_ROOT = REPO / "results" / "_revision_smoke"
SMOKE_RUNS = 2
SMOKE_FUNCTIONS = [1, 3]
SMOKE_DIMS_FULL = [10]
SMOKE_DIMS_E1 = [50]    # must stay >= 50: below that the polish and ISM are gated off,
                        # so a lower dimension would not exercise E1's mechanism at all
SMOKE_DIMS_E4 = [30]
SMOKE_MAX_EVALS = 3000

# Rebound by main() when --smoke is passed.
CFG_ROOT = OUT_ROOT / "_configs"
LOG = OUT_ROOT / "driver.log"

# E4: one factor at a time. (config field, low, high) around the frozen value.
# Integer-valued constants move to the nearest DIFFERENT integer, which is
# stated in the caption rather than silently rounded.
SENSITIVITY = [
    ("ace_learning_rate", 0.08, 0.12),
    ("argp_threshold", 0.016, 0.024),
    ("bse_restart_frac", 0.24, 0.36),
    ("n_min", None, None),                     # resolved per-dimension below
    ("local_search_eval_budget_frac", 0.008, 0.012),
    ("local_search_elite_count", None, None),  # integer, resolved below
    ("interaction_update_period", None, None), # integer, resolved below
]


def log(msg: str) -> None:
    stamp = _dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{stamp}] {msg}"
    print(line, flush=True)
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("a", encoding="utf-8") as fh:
        fh.write(line + "\n")


def pinned_env() -> dict[str, str]:
    """Single-thread the numeric stack; D>=50 byte-stability depends on it."""
    env = dict(os.environ)
    for var in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS",
                "NUMBA_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
        env[var] = "1"
    env["PYTHONPATH"] = str(SRC) + os.pathsep + env.get("PYTHONPATH", "")
    return env


def write_config(name: str, payload: dict) -> Path:
    import yaml
    CFG_ROOT.mkdir(parents=True, exist_ok=True)
    path = CFG_ROOT / f"{name}.yml"
    header = (
        "# GENERATED by scripts/run_revision_experiments.py -- do not hand-edit.\n"
        "# Regenerate by re-running that script; every override below is derived\n"
        "# programmatically from gsk_family.optimizers._dt_profiles, never typed.\n"
    )
    path.write_text(header + yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")
    return path


def base_config(optimizers: list[str], dims: list[int], runs: int,
                out: str, options: dict | None = None) -> dict:
    cfg = {
        "optimizers": optimizers,
        "suite": SUITE,
        "functions": FUNCTIONS,
        "dimensions": dims,
        "runs": runs,
        "seed": BASE_SEED,
        "seed_policy": "unified",
        "rand_generator": "threefry",
        "max_evaluations": MAX_EVALS,
        "overwrite": False,          # RESUMABLE. never flip this.
        "parallel": True,
        "parallel_backend": "process",
        "numba_threads": 1,
        "generation_logs": False,
        "convergence_graphs": False,
        "benchmark_fp_mode": "default",
        "benchmark_backend": "auto",
        "data_root": "benchmarks/cec_suite_python",
        "reference_root": "benchmarks/cec_reference_results",
        "output_root": out,
    }
    if options:
        cfg["optimizer_options"] = options
    return cfg


def build_plan(smoke: bool = False) -> list[dict]:
    """Return the ordered leg list. Cheapest P0 first; E1 unblocks a held edit.

    ``smoke`` shrinks the scope only -- every leg KIND still executes through the
    identical code path, so a green smoke run exercises what the real run does.
    """
    sys.path.insert(0, str(SRC))
    from gsk_family.optimizers._dt_profiles import build_pub_config, pub_overrides

    n_funcs = len(FUNCTIONS) if isinstance(FUNCTIONS, list) else 29
    rel = OUT_ROOT.relative_to(REPO).as_posix()
    legs: list[dict] = []

    # ---- E1 -- refinement-basis contrast (bespoke driver, see module docstring)
    legs.append({
        "id": "E1", "point": "R2.3", "kind": "oracle_basis",
        "desc": "coordinate-basis final polish at the shipped configuration",
        "dims": DIMS_E1, "runs": RUNS_FULL,
        "out": str(OUT_ROOT / "e1_basis_coordinate"),
        "runs_est": len(DIMS_E1) * RUNS_FULL * n_funcs,
    })

    # ---- E2 -- DT-GSK at the comparators' population size
    legs.append({
        "id": "E2", "point": "R1.3/R2.2", "kind": "config",
        "desc": "DT-GSK at NP = 100 (comparator value); NLPSR floor left at tier value",
        "config": base_config(["dt-gsk"], DIMS_FULL, RUNS_FULL,
                              f"{rel}/e2_np100", {"pop_size": 100}),
        "name": "e2_np100_cec2017",
        "runs_est": len(DIMS_FULL) * RUNS_FULL * n_funcs,
    })

    # ---- E3 -- uniform vs tiered. Two arms; the tiered arm is the frozen leg.
    for tier_d, arm in ((10, "low"), (100, "high")):
        ov = dict(pub_overrides(tier_d))
        legs.append({
            "id": f"E3-{arm}", "point": "R2.1", "kind": "config",
            "desc": f"tier-constant arm: the D={tier_d} parameter set applied at every D",
            "config": base_config(["dt-gsk"], DIMS_FULL, RUNS_FULL,
                                  f"{rel}/e3_uniform_{arm}", ov),
            "name": f"e3_uniform_{arm}_cec2017",
            "runs_est": len(DIMS_FULL) * RUNS_FULL * n_funcs,
        })

    # ---- E4 -- one-factor-at-a-time sensitivity
    frozen = {d: build_pub_config(d, seed=BASE_SEED, max_nfes=10_000 * d) for d in DIMS_E4}
    # In smoke, two cells are enough to prove the leg kind; the real run sweeps all.
    factors = SENSITIVITY[:1] if smoke else SENSITIVITY
    for field, lo, hi in factors:
        for d in DIMS_E4:
            cur = getattr(frozen[d], field)
            if lo is None:      # integer-valued: nearest different integer
                pair = [max(1, int(cur) - 1), int(cur) + 1]
            else:
                pair = [lo, hi]
            for level, value in zip(("lo", "hi"), pair):
                if value == cur:
                    continue
                tag = f"e4_{field}_{level}_D{d}"
                legs.append({
                    "id": f"E4:{field}:{level}:D{d}", "point": "R2.7", "kind": "config",
                    "desc": f"{field} {cur} -> {value} at D={d}",
                    "config": base_config(["dt-gsk"], [d], RUNS_SENS,
                                          f"{rel}/{tag}", {field: value}),
                    "name": tag,
                    "runs_est": RUNS_SENS * n_funcs,
                })
    return legs


def leg_done(leg: dict) -> tuple[int, int]:
    """(completed runs, expected runs) from the leg's per_run.csv files."""
    root = Path(leg.get("out") or leg["config"]["output_root"])
    if not root.is_absolute():
        root = REPO / root
    done = 0
    for per_run in root.rglob("per_run.csv"):
        with per_run.open(encoding="utf-8") as fh:
            done += max(0, sum(1 for _ in fh) - 1)
    return done, leg["runs_est"]


def run_config_leg(leg: dict, workers: int) -> int:
    path = write_config(leg["name"], leg["config"])
    cmd = [sys.executable, str(REPO / "run.py"), "--config", str(path),
           "--root", str(REPO), "--workers", str(workers)]
    log(f"    $ {' '.join(cmd[-6:])}")
    return subprocess.run(cmd, cwd=REPO, env=pinned_env()).returncode


def run_oracle_leg(leg: dict, workers: int) -> int:
    cmd = [sys.executable, str(REPO / "scripts" / "run_e1_basis_contrast.py"),
           "--workers", str(workers), "--output-root", leg["out"],
           "--dims", ",".join(str(d) for d in leg["dims"]),
           "--runs", str(leg["runs"])]
    if isinstance(FUNCTIONS, list):
        cmd += ["--functions", ",".join(str(f) for f in FUNCTIONS)]
    if MAX_EVALS:
        cmd += ["--max-evals", str(MAX_EVALS)]
    log(f"    $ run_e1_basis_contrast.py --workers {workers}")
    return subprocess.run(cmd, cwd=REPO, env=pinned_env()).returncode


def _enter_smoke_mode() -> None:
    """Rebind the scope globals so every leg runs tiny, into a separate root."""
    global OUT_ROOT, CFG_ROOT, LOG, RUNS_FULL, RUNS_SENS
    global DIMS_FULL, DIMS_E1, DIMS_E4, FUNCTIONS, MAX_EVALS
    OUT_ROOT = SMOKE_OUT_ROOT
    CFG_ROOT = OUT_ROOT / "_configs"
    LOG = OUT_ROOT / "driver.log"
    RUNS_FULL = RUNS_SENS = SMOKE_RUNS
    DIMS_FULL, DIMS_E1, DIMS_E4 = SMOKE_DIMS_FULL, SMOKE_DIMS_E1, SMOKE_DIMS_E4
    FUNCTIONS = list(SMOKE_FUNCTIONS)
    MAX_EVALS = SMOKE_MAX_EVALS


def verify_smoke(legs: list[dict]) -> int:
    """Assert every leg actually wrote the rows it promised. Returns exit code."""
    log("-" * 88)
    log("SMOKE VERIFICATION")
    bad = []
    for leg in legs:
        done, exp = leg_done(leg)
        ok = done >= exp
        log(f"  {'PASS' if ok else 'FAIL'}  {leg['id']:34} {done:>4}/{exp:<4} rows")
        if not ok:
            bad.append(leg["id"])
    log("-" * 88)
    if bad:
        log(f"SMOKE FAILED -- {len(bad)} leg(s) short: {', '.join(bad)}")
        log("Do NOT start the real campaign until this is green.")
        return 1
    log(f"SMOKE PASSED -- all {len(legs)} legs produced the expected rows.")
    log("The real campaign is safe to start:")
    log("    python scripts/run_revision_experiments.py")
    log(f"Smoke output is in {OUT_ROOT.relative_to(REPO).as_posix()}/ and is NOT campaign")
    log("evidence -- it uses a truncated budget. Delete it whenever you like.")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(
        description="One resumable command for the four revision experiments.")
    ap.add_argument("--workers", type=int, default=15,
                    help="parallel workers per leg (default: 15)")
    ap.add_argument("--only", default="",
                    help="comma-separated leg prefixes, e.g. E1,E2")
    ap.add_argument("--status", action="store_true", help="print progress and exit")
    ap.add_argument("--dry-run", action="store_true", help="print the plan and exit")
    ap.add_argument("--smoke", action="store_true",
                    help="tiny-scope rehearsal of every leg kind, into a SEPARATE "
                         "output root; minutes, not hours. Verifies each leg wrote rows.")
    args = ap.parse_args()

    if args.smoke:
        _enter_smoke_mode()

    legs = build_plan(smoke=args.smoke)
    if args.only:
        keep = tuple(s.strip().upper() for s in args.only.split(",") if s.strip())
        legs = [l for l in legs if l["id"].upper().startswith(keep)]
        if not legs:
            print(f"no legs match --only {args.only!r}")
            return 2

    total = sum(l["runs_est"] for l in legs)

    if args.status or args.dry_run:
        print(f"\n{'leg':28} {'point':10} {'done':>8} {'of':>8}  description")
        print("-" * 108)
        for leg in legs:
            done, exp = (leg_done(leg) if args.status else (0, leg["runs_est"]))
            print(f"{leg['id']:28} {leg['point']:10} {done:>8} {exp:>8}  {leg['desc'][:52]}")
        print("-" * 108)
        print(f"{'TOTAL':28} {'':10} {'':>8} {total:>8} runs across {len(legs)} legs\n")
        if args.dry_run:
            print("dry run: nothing executed.")
        return 0

    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    log("=" * 88)
    if args.smoke:
        log(f"SMOKE REHEARSAL: {len(legs)} legs, {total:,} runs, {args.workers} workers")
        log(f"functions {FUNCTIONS}, runs {SMOKE_RUNS}, budget {SMOKE_MAX_EVALS} evals")
        log(f"output -> {OUT_ROOT.relative_to(REPO).as_posix()}/ (NOT campaign evidence)")
    else:
        log(f"revision experiments: {len(legs)} legs, {total:,} runs, {args.workers} workers")
        log("resumable -- re-run this exact command after any interruption")
    log("=" * 88)

    started = time.time()
    failed: list[str] = []
    for i, leg in enumerate(legs, 1):
        done, exp = leg_done(leg)
        if done >= exp:
            log(f"[{i}/{len(legs)}] {leg['id']}: already complete ({done:,}/{exp:,}) -- skipping")
            continue
        log(f"[{i}/{len(legs)}] {leg['id']} ({leg['point']}) -- {leg['desc']}")
        log(f"    {done:,}/{exp:,} runs present; resuming")
        t0 = time.time()
        rc = (run_oracle_leg(leg, args.workers) if leg["kind"] == "oracle_basis"
              else run_config_leg(leg, args.workers))
        mins = (time.time() - t0) / 60
        if rc != 0:
            failed.append(leg["id"])
            log(f"    FAILED rc={rc} after {mins:.1f} min -- continuing to the next leg")
        else:
            now, _ = leg_done(leg)
            log(f"    done in {mins:.1f} min ({now:,}/{exp:,})")

    elapsed = time.time() - started
    log("=" * 88)
    log(f"finished in {elapsed/60:.1f} min" if args.smoke
        else f"finished in {elapsed/3600:.2f} h")
    if failed:
        log(f"LEGS THAT FAILED: {', '.join(failed)}")
        if not args.smoke:
            log("re-run the same command; completed cells are skipped.")

    if args.smoke:
        log("=" * 88)
        return verify_smoke(legs) or (1 if failed else 0)

    if not failed:
        log("all legs complete.")
    log(f"results staged under {OUT_ROOT.relative_to(REPO).as_posix()}/ "
        "-- promotion is a separate step.")
    log("=" * 88)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
