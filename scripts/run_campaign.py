#!/usr/bin/env python3
# Copyright (c) 2026 Mostafa Masoud <moustafa.masoud@gmail.com>
"""ONE-command, RESUMABLE driver for the whole post-fix evidence campaign.

Runs everything still missing, in order, and never overwrites completed work:

    1. primary cec2017   run.py  --function 1:30 --dimension 10,30,50,100  (51 runs)
    2. primary cec2013   run.py  --function 1:28 --dimension 10,30,50      (51 runs)
    3. primary cec2011   run.py  --function 1:22 --dimension native        (25 runs)
    4. scaffold ablation scripts/run_ablation.py       (7 cells x 4 dims x 51)
    5. overlay isolation scripts/run_overlay_ablation_51.py (4 cells x 2 suites)
    6. telemetry pass    run.py --dt-diagnostics (scoped: F1,4,17,23 x D30,100 x 3)
                         + scripts/analyze_dt_diagnostics.py   [--skip-telemetry]
    7. finalization      papers/scripts/finalize_evidence.py (--dry-run, then full)

Resume model (safe to re-run any number of times):
  * Every unit is checked for completeness FIRST (per_run row counts, summary
    files, curve/gen_log inventories - the same contract finalize_evidence.py
    P0 enforces). Complete units are skipped entirely.
  * Incomplete units re-launch WITHOUT --overwrite: the runner reads the
    existing per_run.csv, skips every already-completed (function, dim, run,
    seed) task, and computes only the missing ones - partial staging is
    continued, never discarded.
  * Ablation/overlay re-launch only the incomplete cells (--only ...).
  * The finalizer keeps its own phase checkpoints (results/_finalize/state.json).

Do NOT start this while another run.py / run_ablation.py process is still
writing to the same staging directories.

Usage::

    python scripts/run_campaign.py --status      # show what is done / missing
    python scripts/run_campaign.py               # run everything missing
    python scripts/run_campaign.py --workers 15
    python scripts/run_campaign.py --skip-finalize
"""
from __future__ import annotations

import argparse
import csv
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

STAGE_RUNALL = ROOT / "results" / "_run_all" / "dt-gsk"
STAGE_SCAFFOLD = ROOT / "results" / "_ablation"
STAGE_OV17 = ROOT / "results" / "_ablation_sgsm_cec2017_51"
STAGE_OV13 = ROOT / "results" / "_ablation_sgsm_51"

PROV_FILES = ["environment.json", "phase0_protocol.json", "run_config.json",
              "seed_schedule.csv", "verification.json"]
SCAFFOLD_CELLS = ["baseline", "no_ace", "no_arch", "no_bse",
                  "no_linkage", "no_localsearch", "no_psr"]
OVERLAY_CELLS = ["full", "no_sgsm", "no_adaptive", "no_finalpolish"]

CEC2011_DIMS = [1, 6, 7, 12, 13, 15, 20, 22, 26, 30, 40, 96, 120, 126, 140, 240]

# (suite, funcs, runs, dims, function selector, dimension selector, curves)
PRIMARY = [
    ("cec2017", 29, 51, [10, 30, 50, 100], "1:30", "10,30,50,100", 116),
    ("cec2013", 28, 51, [10, 30, 50], "1:28", "10,30,50", 84),
    ("cec2011", 22, 25, None, "1:22", "native", 22),
]

# --------------------------------------------------------------------------- #
# Per-generation telemetry pass (adaptation diagnostics for the paper figures)
# --------------------------------------------------------------------------- #
# The frozen gen_logs hold only checkpoint ERRORS, so they cannot show how the
# controllers behave over a run. DT-GSK's opt-in per-generation telemetry does:
# ACE operator credit/entropy, module activity, the REALIZED population
# schedule, tier activation, restart and local-search events.
#
# Scoped deliberately. Measured cost is ~5 MB per cell at D=10 in the compact
# field set (~21 MB with every field), and cost scales with the budget, so
# telemetry over the full 5,916-cell DT-GSK CEC2017 grid would run to tens of
# gigabytes. The adaptation figures need trajectories for a few representative
# functions at the two tiers that actually differ -- not the whole grid:
#     F1  unimodal | F4  multimodal | F17 hybrid | F23 composition
#     D=30   mid tier   -- structure memory and eigenframe polish gated OFF
#     D=100  upper tier -- structure memory, polish and upper-tier controllers ON
# Three runs per cell so a median run can be chosen for plotting.
#
# Written to its OWN output root: the frozen primary staging is never touched,
# and because the telemetry callback is observational (it draws no RNG and
# evaluates no objective) these runs reproduce the primary numbers for the same
# seeds. Raw traces are regenerable; the small summary CSVs are the durable
# product.
STAGE_TELEMETRY = ROOT / "results" / "_telemetry"
TELEMETRY_FUNCS = "1,4,17,23"
TELEMETRY_DIMS = "30,100"
TELEMETRY_RUNS = 3
TELEMETRY_CELLS = 4 * 2 * TELEMETRY_RUNS          # funcs x dims x runs
TELEMETRY_DIAG = STAGE_TELEMETRY / "dt-gsk" / "cec2017" / "diagnostics"
TELEMETRY_ANALYSIS = STAGE_TELEMETRY / "dt-gsk" / "cec2017" / "diagnostics_analysis"


# --------------------------------------------------------------------------- #
# completeness checks (mirror finalize_evidence.py P0)
# --------------------------------------------------------------------------- #
def per_run_dim_counts(p: Path) -> dict[int, int]:
    out: dict[int, int] = {}
    with p.open(encoding="utf-8", newline="") as fh:
        for r in csv.DictReader(fh):
            d = int(r["dimension"])
            out[d] = out.get(d, 0) + 1
    return out


def _n_csv(d: Path) -> int:
    return len(list(d.glob("*.csv"))) if d.is_dir() else 0


def _bundle_missing(src: Path, summaries: list[str], per_dim: dict[int, int] | int,
                    curves: int | None, genlogs: int | None) -> list[str]:
    """Return the reasons a staged bundle is incomplete ([] = complete)."""
    why: list[str] = []
    s = src / "summary"
    if not s.is_dir():
        return [f"missing {s.relative_to(ROOT)}"]
    for name in summaries + PROV_FILES + ["per_run.csv"]:
        if not (s / name).is_file():
            why.append(f"missing summary/{name}")
    pr = s / "per_run.csv"
    if pr.is_file():
        got = per_run_dim_counts(pr)
        if isinstance(per_dim, dict):
            for d, want in per_dim.items():
                if got.get(d, 0) != want:
                    why.append(f"per_run D{d}: {got.get(d, 0)}/{want} rows")
        else:
            total = sum(got.values())
            if total != per_dim:
                why.append(f"per_run: {total}/{per_dim} rows")
    if curves is not None and _n_csv(src / "curves") != curves:
        why.append(f"curves: {_n_csv(src / 'curves')}/{curves}")
    if genlogs is not None and _n_csv(src / "gen_logs") != genlogs:
        why.append(f"gen_logs: {_n_csv(src / 'gen_logs')}/{genlogs}")
    return why


def primary_missing(suite: str, funcs: int, runs: int, dims: list[int] | None,
                    curves: int) -> list[str]:
    if suite == "cec2011":
        summaries = (["dt-gsk_cec2011.csv"]
                     + [f"dt-gsk_cec2011_D{d}.csv" for d in CEC2011_DIMS])
        per_dim: dict[int, int] | int = funcs * runs      # total only (native dims)
    else:
        summaries = [f"dt-gsk_{suite}_D{d}.csv" for d in dims or []]
        per_dim = {d: funcs * runs for d in dims or []}
    return _bundle_missing(STAGE_RUNALL / suite, summaries, per_dim,
                           curves, curves)


def scaffold_missing(cell: str) -> list[str]:
    src = STAGE_SCAFFOLD / cell / "dt-gsk" / "cec2017"
    return _bundle_missing(
        src, [f"dt-gsk_cec2017_D{d}.csv" for d in (10, 30, 50, 100)],
        {d: 29 * 51 for d in (10, 30, 50, 100)}, 116, None)


def overlay_missing(cell: str) -> list[str]:
    why = []
    src = STAGE_OV17 / cell / "dt-gsk" / "cec2017"
    why += [f"cec2017 {w}" for w in _bundle_missing(
        src, ["dt-gsk_cec2017_D50.csv", "dt-gsk_cec2017_D100.csv"],
        {50: 29 * 51, 100: 29 * 51}, 58, None)]
    src = STAGE_OV13 / cell / "dt-gsk" / "cec2013"
    why += [f"cec2013 {w}" for w in _bundle_missing(
        src, ["dt-gsk_cec2013_D50.csv"], {50: 28 * 51}, 28, None)]
    return why


# --------------------------------------------------------------------------- #
# execution
# --------------------------------------------------------------------------- #
def pinned_env() -> dict:
    env = os.environ.copy()
    for k in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS",
              "VECLIB_MAXIMUM_THREADS", "NUMEXPR_NUM_THREADS",
              "NUMBA_NUM_THREADS"):
        env[k] = "1"
    env["PYTHONIOENCODING"] = "utf-8"
    return env


def run(cmd: list[str]) -> None:
    """Run a child with live output; abort the campaign on failure."""
    print(f"\n>>> {' '.join(cmd)}", flush=True)
    rc = subprocess.run([sys.executable, *cmd], cwd=str(ROOT),
                        env=pinned_env()).returncode
    if rc != 0:
        raise SystemExit(f"campaign step failed (exit {rc}): {' '.join(cmd)} "
                         "- fix the cause and re-run this script; completed "
                         "work is skipped automatically.")


def telemetry_missing() -> list[str]:
    """Missing pieces of the per-generation telemetry pass (traces + analysis)."""
    why: list[str] = []
    traces = len(list(TELEMETRY_DIAG.glob("DTTrace_*.jsonl"))) if TELEMETRY_DIAG.is_dir() else 0
    if traces < TELEMETRY_CELLS:
        why.append(f"traces {traces}/{TELEMETRY_CELLS}")
    if not (TELEMETRY_ANALYSIS / "diagnostics_summary.csv").is_file():
        why.append("diagnostics_summary.csv missing")
    return why


def telemetry_cmd(workers: int) -> list[str]:
    """Scoped DT-GSK run with per-generation telemetry on, to its own root."""
    return ["run.py", "--root", ".", "--optimizer", "dt-gsk",
            "--suite", "cec2017", "--function", TELEMETRY_FUNCS,
            "--dimension", TELEMETRY_DIMS, "--runs", str(TELEMETRY_RUNS),
            "--workers", str(workers),
            "--seed", "20240620", "--seed-policy", "unified",
            "--rand-generator", "threefry", "--benchmark-fp-mode", "default",
            "--benchmark-backend", "auto",
            "--output-root", STAGE_TELEMETRY.relative_to(ROOT).as_posix(),
            "--no-convergence-graphs", "--dt-diagnostics"]


def telemetry_analysis_cmd() -> list[str]:
    return ["scripts/analyze_dt_diagnostics.py",
            "--input", TELEMETRY_DIAG.relative_to(ROOT).as_posix(),
            "--out", TELEMETRY_ANALYSIS.relative_to(ROOT).as_posix()]


def primary_cmd(suite: str, runs: int, fsel: str, dsel: str, workers: int) -> list[str]:
    return ["run.py", "--root", ".", "--optimizer", "dt-gsk",
            "--suite", suite, "--function", fsel, "--dimension", dsel,
            "--runs", str(runs), "--workers", str(workers),
            "--seed", "20240620", "--seed-policy", "unified",
            "--rand-generator", "threefry", "--benchmark-fp-mode", "default",
            "--benchmark-backend", "auto", "--convergence-graphs"]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--workers", type=int, default=15,
                    help="parallel workers for every runner (default: 15)")
    ap.add_argument("--status", action="store_true",
                    help="print the completeness table and exit")
    ap.add_argument("--skip-finalize", action="store_true",
                    help="run the campaign only; do not chain "
                         "finalize_evidence.py at the end")
    ap.add_argument("--skip-telemetry", action="store_true",
                    help="skip the scoped per-generation telemetry pass "
                         "(adaptation diagnostics for the paper figures)")
    args = ap.parse_args()

    # ---- assess ----
    plan: list[tuple[str, list[str]]] = []   # (label, why-incomplete)
    for suite, funcs, runs, dims, fsel, dsel, curves in PRIMARY:
        plan.append((f"primary {suite}",
                     primary_missing(suite, funcs, runs, dims, curves)))
    scaffold_todo = {c: scaffold_missing(c) for c in SCAFFOLD_CELLS}
    overlay_todo = {c: overlay_missing(c) for c in OVERLAY_CELLS}

    print("=== campaign status ===")
    for label, why in plan:
        print(f"  {label:18s} {'COMPLETE' if not why else 'incomplete: ' + '; '.join(why[:3])}")
    for c in SCAFFOLD_CELLS:
        why = scaffold_todo[c]
        print(f"  scaffold/{c:14s} {'COMPLETE' if not why else 'incomplete: ' + '; '.join(why[:3])}")
    for c in OVERLAY_CELLS:
        why = overlay_todo[c]
        print(f"  overlay/{c:15s} {'COMPLETE' if not why else 'incomplete: ' + '; '.join(why[:3])}")
    telemetry_todo = telemetry_missing()
    print(f"  {'telemetry':18s} "
          f"{'SKIPPED (--skip-telemetry)' if args.skip_telemetry else ('COMPLETE' if not telemetry_todo else 'incomplete: ' + '; '.join(telemetry_todo[:3]))}")
    if args.status:
        return 0

    # ---- run what is missing (resume: never --overwrite) ----
    for (label, why), (suite, funcs, runs, dims, fsel, dsel, curves) in zip(plan, PRIMARY):
        if not why:
            print(f"[skip] {label} already complete")
            continue
        run(primary_cmd(suite, runs, fsel, dsel, args.workers))

    cells = [c for c in SCAFFOLD_CELLS if scaffold_todo[c]]
    if cells:
        run(["scripts/run_ablation.py", "--dimension", "10,30,50,100",
             "--runs", "51", "--workers", str(args.workers),
             "--only", ",".join(cells)])
    else:
        print("[skip] scaffold ablation already complete (7/7 cells)")

    cells = [c for c in OVERLAY_CELLS if overlay_todo[c]]
    if cells:
        run(["scripts/run_overlay_ablation_51.py",
             "--workers", str(args.workers), "--only", ",".join(cells)])
    else:
        print("[skip] overlay isolation already complete (4/4 cells)")

    # ---- per-generation telemetry (adaptation diagnostics for the figures) ----
    # Own output root, so this can never disturb the frozen primary staging.
    if args.skip_telemetry:
        print("[skip] telemetry pass disabled (--skip-telemetry)")
    elif telemetry_todo:
        run(telemetry_cmd(args.workers))
        run(telemetry_analysis_cmd())
        still = telemetry_missing()
        if still:
            raise SystemExit(
                "telemetry pass finished but is still incomplete: "
                + "; ".join(still))
    else:
        print(f"[skip] telemetry already complete ({TELEMETRY_CELLS}/{TELEMETRY_CELLS} cells)")

    # ---- re-verify everything before finalizing ----
    incomplete = []
    for suite, funcs, runs, dims, fsel, dsel, curves in PRIMARY:
        incomplete += [f"primary {suite}: {w}"
                       for w in primary_missing(suite, funcs, runs, dims, curves)]
    incomplete += [f"scaffold/{c}: {w}" for c in SCAFFOLD_CELLS
                   for w in scaffold_missing(c)]
    incomplete += [f"overlay/{c}: {w}" for c in OVERLAY_CELLS
                   for w in overlay_missing(c)]
    if incomplete:
        print("\nCampaign steps finished but staging is STILL incomplete:")
        for w in incomplete[:20]:
            print(f"  - {w}")
        raise SystemExit(2)
    print("\nAll campaign staging COMPLETE.")

    if args.skip_finalize:
        print("(--skip-finalize given: run "
              "'python papers/scripts/finalize_evidence.py' when ready)")
        return 0
    run(["papers/scripts/finalize_evidence.py", "--dry-run"])
    run(["papers/scripts/finalize_evidence.py"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
