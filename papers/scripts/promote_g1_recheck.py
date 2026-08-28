#!/usr/bin/env python3
# Copyright (c) 2026 Mostafa Masoud <moustafa.masoud@gmail.com>
"""Promote the D-0051 cross-build re-execution as a citable evidence release.

The diagnostic staged under ``results/_g1_recheck/`` answered D-0051: the five
CEC2017 D = 100 functions carrying the 26-cell archive/transplant divergence
(F7, F13, F14, F20, F30, plus F1 as an agreeing control) were re-executed
under the current build, threads pinned, 51 runs each. D-0051 recorded the
verdict but kept the run as staging, cited nowhere. Reopened by author
instruction (2026-08-28): promote it, so the Supplementary can state the
demonstrated resolution instead of an unresolved residual.

Fail-closed: the promotion FIRST re-derives the D-0051 verdict from the
staged bytes against the frozen archive and the round-one transplant arm --
zero seed mismatches; on every cell where the two frozen legs differ the
fresh run must equal the TRANSPLANT arm and never the archive; on every cell
where they agree it must equal both. Any deviation aborts the promotion.

Destination::

    benchmarks/cec_reference_results/_g1_recheck/<files>
    benchmarks/cec_reference_results/_g1_recheck/manifest.json

Exclusions per release precedent: curves/, gen_logs/, per-session console
logs. Promoted files are byte-verified and set read-only.
"""
from __future__ import annotations

import csv
import datetime as _dt
import hashlib
import json
import os
import shutil
import stat
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
STAGING = REPO / "results" / "_g1_recheck"
DEST = REPO / "benchmarks" / "cec_reference_results" / "_g1_recheck"
MANIFEST = DEST / "manifest.json"
ARCHIVE = REPO / "benchmarks" / "cec_reference_results" / "cec2017" / "dt-gsk" / "per_run.csv"
UHIGH = (REPO / "benchmarks" / "cec_reference_results" / "_revision" /
         "e3_uniform_high" / "dt-gsk" / "cec2017" / "summary" / "per_run.csv")
FRESH = STAGING / "dt-gsk" / "cec2017" / "summary" / "per_run.csv"


def load(path: Path) -> dict:
    out = {}
    with path.open(encoding="utf-8", newline="") as fh:
        for r in csv.DictReader(fh):
            if int(r["dimension"]) != 100:
                continue
            out[(int(r["function"]), int(r["run"]))] = (r["best_fitness"], int(r["seed"]))
    return out


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def verify() -> dict:
    fresh, arch, uh = load(FRESH), load(ARCHIVE), load(UHIGH)
    keys = sorted(fresh)
    if not keys:
        sys.exit("ABORT: no D=100 rows in staging")
    mism = [k for k in keys if not (fresh[k][1] == arch[k][1] == uh[k][1])]
    if mism:
        sys.exit(f"ABORT: {len(mism)} seed mismatches -- pairing void")
    diff_cells = [k for k in keys if arch[k][0] != uh[k][0]]
    agree_cells = [k for k in keys if arch[k][0] == uh[k][0]]
    bad = []
    for k in diff_cells:
        if fresh[k][0] != uh[k][0] or fresh[k][0] == arch[k][0]:
            bad.append(("diff-cell", k, fresh[k][0]))
    for k in agree_cells:
        if fresh[k][0] != uh[k][0]:
            bad.append(("agree-cell", k, fresh[k][0]))
    if bad:
        for b in bad[:5]:
            print("  VERDICT DEVIATION:", b)
        sys.exit("ABORT: staged bytes do not reproduce the D-0051 verdict")
    funcs = sorted({f for f, _ in keys})
    print(f"  verdict reproduced: {len(keys)} cells over F{funcs}; "
          f"{len(diff_cells)} divergent cells all equal the transplant arm and "
          f"never the archive; {len(agree_cells)} agreeing cells equal both; "
          f"0 seed mismatches")
    return {"cells": len(keys), "functions": funcs,
            "divergent_cells": len(diff_cells), "agreeing_cells": len(agree_cells)}


def eligible(p: Path) -> bool:
    parts = p.relative_to(STAGING).parts
    if "curves" in parts or "gen_logs" in parts:
        return False
    if "_log_" in p.name and p.suffix == ".txt":
        return False
    return True


def main() -> int:
    dry = "--dry-run" in sys.argv
    print("[1/3] fail-closed verdict verification")
    stats = verify()

    plan = [(f, DEST / f.relative_to(STAGING))
            for f in sorted(STAGING.rglob("*")) if f.is_file() and eligible(f)]
    fresh = [(s, d) for s, d in plan if not d.exists()]
    print(f"[2/3] plan: {len(plan)} files ({len(plan)-len(fresh)} already promoted)")
    if dry:
        for s, d in fresh[:6]:
            print("   ", s.relative_to(REPO), "->", d.relative_to(REPO))
        return 0
    for s, d in plan:
        if d.exists() and sha256(s) != sha256(d):
            sys.exit(f"ABORT: promoted file differs: {d.relative_to(REPO)}")
    for s, d in fresh:
        d.parent.mkdir(parents=True, exist_ok=True)
        h = sha256(s)
        shutil.copy2(s, d)
        if sha256(d) != h:
            sys.exit("ABORT: byte verification failed")
        os.chmod(d, stat.S_IREAD | stat.S_IRGRP | stat.S_IROTH)

    files = [{"path": f.relative_to(DEST).as_posix(), "sha256": sha256(f),
              "bytes": f.stat().st_size}
             for f in sorted(DEST.rglob("*")) if f.is_file() and f != MANIFEST]
    head = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True,
                          text=True, check=True).stdout.strip()
    release_id = f"g1-rel-2026-08-28-{head[:9]}"
    manifest = {
        "schema": "revision_evidence_manifest/v1",
        "release_id": release_id,
        "title": ("D-0051 cross-build identity re-execution: the divergent CEC2017 "
                  "D=100 cells re-run under the current build, threads pinned"),
        "generated_utc": _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+00:00"),
        "git_head_at_promotion": head,
        "governance": ("D-0051 (executed and independently replicated 2026-08-27, kept as "
                       "staging by decision); promotion reopened and ordered by the author "
                       "2026-08-28, recorded in D-0055. Verdict re-derived fail-closed at "
                       "promotion from the staged bytes."),
        "verdict": {
            **stats,
            "statement": ("On every cell where the archived leg and the round-one "
                          "transplant arm disagree, the current build reproduces the "
                          "transplant arm and never the archive; on every cell where "
                          "they agree it reproduces both. The residual is a build "
                          "difference, not a within-build instability."),
            "method_note": ("run_campaign-style single-thread pinning is load-bearing; "
                            "an unpinned re-run is meaningless at D=100."),
        },
        "supersedes_release": None,
        "supersession_note": ("Non-superseding and additive. Reads the frozen primary "
                              "release (archived leg) and rev-rel-2026-08-26-dd42d37eb "
                              "(transplant arm) without re-minting either."),
        "exclusions": "curves/, gen_logs/ and per-session console logs, per release precedent.",
        "totals": {"files": len(files), "bytes": sum(f["bytes"] for f in files)},
        "files": files,
    }
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    if MANIFEST.exists():
        os.chmod(MANIFEST, stat.S_IWRITE | stat.S_IREAD)
    MANIFEST.write_bytes((json.dumps(manifest, indent=2, ensure_ascii=False) + "\n").encode("utf-8"))
    os.chmod(MANIFEST, stat.S_IREAD | stat.S_IRGRP | stat.S_IROTH)
    print(f"[3/3] promoted {len(fresh)} files; release {release_id}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
