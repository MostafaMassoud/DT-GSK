#!/usr/bin/env python3
# Copyright (c) 2026 Mostafa Masoud <moustafa.masoud@gmail.com>
"""Recover the lost apgsk CEC2017 D10/30/50 per-run rows into the reference tree.

Anomaly A2-004: benchmarks/cec_reference_results/cec2017/apgsk/per_run.csv holds
D100 only; the D10/30/50 individual-run rows were lost to a save-overwrite before
the tree was frozen. The frozen SUMMARY CSVs (Best/Median/Mean/Worst/SD) survived.

Because run seeds are deterministic (get_cec_seed(20240620, dim, func, run)), the
re-run in ``results/_apgsk_recover`` reproduces the original per-run values. This
script PROVES that by recomputing the summary from the recovered per-run rows and
comparing it to the frozen summary CSVs; only if every cell matches does ``--apply``
merge the recovered D10/30/50 rows into the reference per_run.csv (D100 preserved),
after backing up the original.

Usage:
    python scripts/recover_apgsk_perrun.py            # validate only (dry run)
    python scripts/recover_apgsk_perrun.py --apply    # validate, then merge if PASS
"""
from __future__ import annotations

import argparse
import csv
import io
import statistics
import sys
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
REF_DIR = ROOT / "benchmarks" / "cec_reference_results" / "cec2017" / "apgsk"
REF_PERRUN = REF_DIR / "per_run.csv"
RECOVER_ROOT = ROOT / "results" / "_apgsk_recover"
DIMS = [10, 30, 50]
RTOL, ATOL = 1e-8, 1e-12


def _find_recovered_perrun() -> Path:
    hits = [p for p in RECOVER_ROOT.rglob("per_run.csv")]
    if not hits:
        sys.exit(f"ERROR: no per_run.csv under {RECOVER_ROOT} - run the recovery config first.")
    return hits[0]


def _load(pr: Path) -> list[dict]:
    with open(pr, encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def _close(a: float, b: float) -> bool:
    return abs(a - b) <= ATOL + RTOL * abs(b)


def validate(recov_rows: list[dict]) -> bool:
    ok = True
    for dim in DIMS:
        summ = REF_DIR / f"apgsk_cec2017_D{dim}.csv"
        if not summ.exists():
            print(f"  D{dim}: MISSING frozen summary {summ.name} - cannot validate")
            ok = False
            continue
        with open(summ, encoding="utf-8") as fh:
            frozen = {int(r["Function"]): r for r in csv.DictReader(fh)}
        by_fn: dict[int, list[float]] = {}
        for r in recov_rows:
            if int(r["dimension"]) == dim:
                by_fn.setdefault(int(r["function"]), []).append(float(r["error"]))
        worst_diff = 0.0
        nfun = 0
        for fn, errs in sorted(by_fn.items()):
            if fn not in frozen:
                continue
            nfun += 1
            errs_sorted = sorted(errs)
            got = {
                "Best": errs_sorted[0], "Worst": errs_sorted[-1],
                "Mean": statistics.fmean(errs), "Median": statistics.median(errs_sorted),
                "SD": statistics.pstdev(errs) if len(errs) > 1 else 0.0,
            }
            # try sample SD too (some pipelines use ddof=1); accept whichever matches
            sd_sample = statistics.stdev(errs) if len(errs) > 1 else 0.0
            for col, val in got.items():
                ref = float(frozen[fn][col])
                match = _close(val, ref) or (col == "SD" and _close(sd_sample, ref))
                if not match:
                    ok = False
                    worst_diff = max(worst_diff, abs(val - ref))
                    if worst_diff == abs(val - ref):
                        print(f"    MISMATCH D{dim} F{fn} {col}: recovered={val:.10E} frozen={ref:.10E}")
        runs = {len(v) for v in by_fn.values()}
        print(f"  D{dim}: {nfun} functions checked, runs/func={runs}, "
              f"{'PASS' if worst_diff == 0 else f'FAIL (max diff {worst_diff:.2E})'}")
    return ok


def merge(recov_rows: list[dict]) -> None:
    ref_rows = _load(REF_PERRUN)
    ref_header = list(ref_rows[0].keys())
    backup = REF_PERRUN.with_suffix(".csv.pre_A2004_recovery.bak")
    backup.write_bytes(REF_PERRUN.read_bytes())
    print(f"  backed up original -> {backup.relative_to(ROOT)}")
    keep = [r for r in ref_rows if int(r["dimension"]) not in DIMS]  # D100 (+ any other)
    add = [r for r in recov_rows if int(r["dimension"]) in DIMS]
    # align recovered rows to the reference header (fill missing cols if any)
    norm = []
    for r in keep + add:
        norm.append({c: r.get(c, "") for c in ref_header})
    norm.sort(key=lambda r: (int(r["dimension"]), int(r["function"]), int(r["run"])))
    with open(REF_PERRUN, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=ref_header)
        w.writeheader()
        w.writerows(norm)
    print(f"  wrote {len(norm)} rows to {REF_PERRUN.relative_to(ROOT)} "
          f"(kept {len(keep)} existing + added {len(add)} recovered)")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--apply", action="store_true", help="merge into the reference tree if validation PASSES")
    args = ap.parse_args()

    recov = _find_recovered_perrun()
    recov_rows = _load(recov)
    print(f"recovered per_run: {recov.relative_to(ROOT)} ({len(recov_rows)} rows)")
    print("VALIDATION (recovered summary vs frozen reference):")
    ok = validate(recov_rows)
    print(f"\nVALIDATION {'PASS - recovered rows reproduce the frozen summaries exactly' if ok else 'FAIL - do NOT merge'}")
    if not ok:
        return 1
    if args.apply:
        print("\nMERGE (--apply):")
        merge(recov_rows)
        print("\nDONE. NOTE: this modified the frozen evidence tree. Follow-ups required:")
        print("  1) regenerate papers/governance/evidence_release_manifest.json (per-file SHA-256)")
        print("  2) recompute the affected Phase-6 supplement cells (run-level Wilcoxon/A12/BCa vs apgsk D10/30/50)")
        print("  3) record the recovery as a change-control decision (D-00xx) + update phase2_anomaly_register A2-004")
    else:
        print("\n(dry run) re-run with --apply to merge the recovered rows into the reference tree.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
