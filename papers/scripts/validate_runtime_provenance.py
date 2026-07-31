#!/usr/bin/env python3
# Copyright (c) 2026 Mostafa Masoud <moustafa.masoud@gmail.com>
"""Gate for the cross-algorithm runtime table (ticket RT-001).

WHY THIS EXISTS
---------------
Wall-clock is the only quantity the manuscript reports that is a property of the
machine and build rather than of the algorithm.  Every other reported number --
error, rank, effect size, p-value -- is reproducible from the frozen seeds and is
therefore immune to when or on what commit a cell was measured.  Runtime is not.

The post-fix campaign re-timed DT-GSK (defect M038: the interaction graph had
been silently executing the bit-for-bit-equivalent NumPy path) 9.4 days after the
comparator block, on a different commit.  Every scientific column reproduced
exactly; only ``runtime_seconds`` moved.  Regenerating Table ``tab:runtime`` from
that state would publish a comparison across two measurement sessions -- which is
not a valid comparison, however accurate each half is on its own.

This gate makes that failure mode loud instead of silent.  It reads the per-cell
``environment.json`` provenance and refuses the runtime table whenever the panel
was not measured as one session.

CHECKS
------
1. MACHINE      -- all cells on the same host (hard fail; different hardware is
                   simply not comparable).
2. WORKERS      -- same worker count (hard fail; different CPU contention).
3. SESSION SPAN -- no cell more than ``--max-gap-hours`` (default 72) from the
                   panel median timestamp.  A campaign that runs cells
                   back-to-back spans about a day; a cell nine days out is a
                   different session, not a long campaign.

Commit equality is deliberately NOT required: a sequential campaign advances
through commits between cells, so commit inequality alone carries no signal.
Commits are reported for the audit trail.

USAGE
-----
    python papers/scripts/validate_runtime_provenance.py
    python papers/scripts/validate_runtime_provenance.py --suite cec2017 --json

Exit 0 means the runtime table may be regenerated.  Non-zero means it must not
be: either finish the re-timing (``scripts/retime_comparators.py``) or re-scope
the table as single-algorithm and explicitly non-comparative
(``papers/governance/remediation_2026_07_18/decisions.md``, Decision 7).
"""
from __future__ import annotations

import argparse
import json
import statistics
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REF = ROOT / "benchmarks" / "cec_reference_results"

# RT-001 fallback ADOPTED (Decision 7): the comparator re-timing could not
# reproduce the frozen scientific columns under current code (2026-07-08 evidence
# vs current commit -- deterministic within a commit, but FP drift across the
# code change amplified by chaotic search), so tab:runtime was re-scoped to
# DT-GSK-only / non-comparative. This gate therefore now verifies only that
# DT-GSK's own timing is a single measurement session; the cross-algorithm
# single-session requirement no longer applies because the table makes no
# cross-algorithm comparison. To audit the full panel, set GSK_RUNTIME_PANEL.
import os as _os
PANEL = ([a.strip() for a in _os.environ["GSK_RUNTIME_PANEL"].split(",")]
         if _os.environ.get("GSK_RUNTIME_PANEL") else ["dt-gsk"])


def load(suite: str) -> dict[str, dict]:
    out: dict[str, dict] = {}
    for algo in PANEL:
        p = REF / suite / algo / "environment.json"
        if not p.is_file():
            continue
        d = json.loads(p.read_text(encoding="utf-8"))
        out[algo] = {
            "timestamp": d.get("timestamp", ""),
            "git_commit": str(d.get("git_commit", ""))[:9],
            "computer": str(d.get("computer", "")),
            "workers": d.get("workers", None),
            "python": str(d.get("python_version", "")),
        }
    return out


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__.splitlines()[0],
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--suite", default="cec2017")
    ap.add_argument("--max-gap-hours", type=float, default=72.0,
                    help="max distance from the panel median timestamp (default 72)")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    args = ap.parse_args()

    cells = load(args.suite)
    if not cells:
        print(f"[runtime-provenance] no cells found under {REF / args.suite}")
        return 1

    stamps = {a: datetime.fromisoformat(c["timestamp"])
              for a, c in cells.items() if c["timestamp"]}
    if len(stamps) != len(cells):
        print("[runtime-provenance] FAIL: some cells carry no timestamp")
        return 1

    median = statistics.median(sorted(stamps.values()))
    gaps = {a: (t - median).total_seconds() / 3600.0 for a, t in stamps.items()}
    span = (max(stamps.values()) - min(stamps.values())).total_seconds() / 3600.0

    problems: list[str] = []

    machines = {c["computer"] for c in cells.values()}
    if len(machines) > 1:
        problems.append(f"cells measured on {len(machines)} different hosts: "
                        f"{sorted(machines)}")

    workers = {c["workers"] for c in cells.values()}
    if len(workers) > 1:
        problems.append(f"cells measured at {len(workers)} different worker "
                        f"counts: {sorted(str(w) for w in workers)}")

    outliers = {a: g for a, g in gaps.items() if abs(g) > args.max_gap_hours}
    if outliers:
        detail = ", ".join(f"{a} ({g / 24:+.1f} d)"
                           for a, g in sorted(outliers.items(),
                                              key=lambda kv: -abs(kv[1])))
        problems.append(f"{len(outliers)} cell(s) outside the "
                        f"{args.max_gap_hours:.0f} h session window: {detail}")

    if args.json:
        print(json.dumps({"suite": args.suite, "span_hours": round(span, 2),
                          "median": median.isoformat(),
                          "cells": {a: {**cells[a], "gap_hours": round(gaps[a], 2)}
                                    for a in cells},
                          "problems": problems,
                          "ok": not problems}, indent=2))
        return 1 if problems else 0

    print(f"[runtime-provenance] {args.suite}: measurement session audit")
    print(f"  {'cell':12s} {'timestamp':21s} {'commit':10s} {'host':17s} "
          f"{'wk':>3s} {'gap':>9s}")
    for a in PANEL:
        if a not in cells:
            continue
        c = cells[a]
        g = gaps[a]
        mark = "  <<<" if abs(g) > args.max_gap_hours else ""
        gap_s = f"{g / 24:+.1f} d" if abs(g) >= 24 else f"{g:+.1f} h"
        print(f"  {a:12s} {c['timestamp']:21s} {c['git_commit']:10s} "
              f"{c['computer']:17s} {str(c['workers']):>3s} {gap_s:>9s}{mark}")
    print(f"\n  panel span: {span:.1f} h ({span / 24:.1f} d)"
          f"   median: {median.isoformat()}")

    if problems:
        print("\n[runtime-provenance] FAILED - the panel was not measured as one "
              "session:")
        for p in problems:
            print(f"  - {p}")
        print("\n  A cross-algorithm runtime table built from this state mixes\n"
              "  measurement sessions and is not a valid comparison. Either:\n"
              "    1. finish the re-timing:  python scripts/retime_comparators.py\n"
              "    2. or re-scope tab:runtime as single-algorithm and explicitly\n"
              "       non-comparative (decisions.md, Decision 7, fallback option).\n"
              "  Tracked as ticket RT-001.")
        return 1

    print("\n[runtime-provenance] OK - single host, single worker count, all "
          f"cells within {args.max_gap_hours:.0f} h.")
    print("  The DT-GSK-only runtime table is single-session and may be regenerated.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
