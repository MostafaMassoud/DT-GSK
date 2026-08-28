#!/usr/bin/env python3
# Copyright (c) 2026 Mostafa Masoud <moustafa.masoud@gmail.com>
"""Promote the round-two E5 staging bundles into their own immutable release.

Journal round-1 major revision, second-round follow-up (pre-registration
Amendment A4, 2026-08-28): the dimension-boundary sensitivity experiment E5
was staged under ``results/_revision/e5_*`` by
``scripts/run_revision_experiments.py --only E5``. Per the governance rule
that evidence releases are additive and non-superseding and NEW FINDINGS GET
A NEW RELEASE ID, E5 is promoted into its own sibling tree rather than
amended into the round-one release::

    benchmarks/cec_reference_results/_revision2/<arm>/...
    benchmarks/cec_reference_results/_revision2/manifest.json

The fifth registered cell (boundary 20->31 at D=30) is NOT here: it is
identical by construction to E3's U-low arm at D=30 and is read from the
round-one release ``_revision/e3_uniform_low/`` (51 runs). The manifest
records that pairing.

Same promotion discipline as round one: never overwrite (re-running verifies
promoted bytes), hash before copy and re-hash after, read-only afterwards,
LF manifest with per-file SHA-256.

Usage::

    python papers/scripts/promote_revision2_experiments.py --dry-run
    python papers/scripts/promote_revision2_experiments.py
"""
from __future__ import annotations

import argparse
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
STAGING = REPO / "results" / "_revision"
DEST = REPO / "benchmarks" / "cec_reference_results" / "_revision2"
MANIFEST = DEST / "manifest.json"

E5_ARMS = ("e5_b20_lo_D10", "e5_b50_lo_D30", "e5_b50_hi_D50", "e5_b100_hi_D100")
EXPECTED_ROWS = 15 * 29     # one dimension, 15 runs, 29 scored functions


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def eligible(path: Path) -> bool:
    """summary/ files except per-session console logs; no curves/."""
    parts = path.relative_to(STAGING).parts
    if "curves" in parts:
        return False
    if "_log_" in path.name and path.suffix == ".txt":
        return False
    return True


def collect_arms() -> dict[str, Path]:
    arms: dict[str, Path] = {}
    for name in E5_ARMS:
        d = STAGING / name
        per = d / "dt-gsk" / "cec2017" / "summary" / "per_run.csv"
        if not per.is_file():
            print(f"SKIP absent arm {name}")
            continue
        with per.open(encoding="utf-8") as fh:
            rows = max(0, sum(1 for _ in fh) - 1)
        if rows < EXPECTED_ROWS:
            print(f"SKIP incomplete arm {name}: {rows}/{EXPECTED_ROWS} rows")
            continue
        if rows > EXPECTED_ROWS:
            raise SystemExit(f"ABORT: arm {name} has MORE rows than planned "
                             f"({rows} > {EXPECTED_ROWS}) -- investigate first")
        arms[name] = d
    return arms


def serialize(obj) -> bytes:
    return (json.dumps(obj, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    arms = collect_arms()
    if len(arms) != len(E5_ARMS):
        print(f"only {len(arms)}/{len(E5_ARMS)} arms complete; E5 promotes "
              "all-or-nothing (single registered campaign)")
        if not args.dry_run:
            return 1

    plan: list[tuple[Path, Path]] = []
    for arm, src_root in arms.items():
        for f in sorted(src_root.rglob("*")):
            if f.is_file() and eligible(f):
                plan.append((f, DEST / arm / f.relative_to(src_root)))
    for name in E5_ARMS:
        cfg = STAGING / "_configs" / f"{name}.yml"
        if cfg.is_file():
            plan.append((cfg, DEST / "_configs" / cfg.name))
    if (STAGING / "driver.log").is_file():
        plan.append((STAGING / "driver.log", DEST / "_provenance" / "driver.log"))

    already = [d for (_s, d) in plan if d.exists()]
    fresh = [(s, d) for (s, d) in plan if not d.exists()]
    print(f"arms: {', '.join(arms) or '(none)'}")
    print(f"plan: {len(plan)} files ({len(already)} already promoted, {len(fresh)} to copy)")
    if args.dry_run:
        for s, d in fresh[:8]:
            print(f"  {s.relative_to(REPO)} -> {d.relative_to(REPO)}")
        if len(fresh) > 8:
            print(f"  ... and {len(fresh) - 8} more")
        return 0

    for s, d in plan:
        if d.exists() and sha256(s) != sha256(d):
            print(f"ABORT: promoted file differs from staging: {d.relative_to(REPO)}")
            return 1

    for s, d in fresh:
        d.parent.mkdir(parents=True, exist_ok=True)
        src_hash = sha256(s)
        shutil.copy2(s, d)
        if sha256(d) != src_hash:
            print(f"ABORT: byte verification failed for {d.relative_to(REPO)}")
            return 1
        os.chmod(d, stat.S_IREAD | stat.S_IRGRP | stat.S_IROTH)

    files = []
    for f in sorted(DEST.rglob("*")):
        if f.is_file() and f != MANIFEST:
            files.append({"path": f.relative_to(DEST).as_posix(),
                          "sha256": sha256(f), "bytes": f.stat().st_size})

    head = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True,
                          text=True, check=True).stdout.strip()
    release_id = f"rev2-rel-2026-08-28-{head[:9]}"

    manifest = {
        "schema": "revision_evidence_manifest/v1",
        "release_id": release_id,
        "title": ("DT-GSK second-round revision experiment E5: dimension-boundary "
                  "sensitivity (four single-dimension profile-transplant cells)"),
        "generated_utc": _dt.datetime.now(_dt.timezone.utc)
                          .strftime("%Y-%m-%dT%H:%M:%S+00:00"),
        "git_head_at_promotion": head,
        "governance": ("Pre-registered as Amendment A4 (2026-08-28) in papers/"
                       "review_2026_08_24/revision_experiments_preregistration.md, "
                       "before any E5 run executed; canonical near-zero analysis "
                       "rule fixed by Amendments A5/A6."),
        "supersedes_release": None,
        "supersession_note": ("Non-superseding and additive. Pairs read-only with the "
                              "frozen primary release rel-2026-07-20-67d9345f9 (the "
                              "tiered reference restricted to the same first 15 runs "
                              "of the unified schedule) and with the round-one release "
                              "rev-rel-2026-08-26-dd42d37eb, whose e3_uniform_low arm "
                              "at D=30 IS the fifth registered E5 cell (boundary "
                              "20->31; 51 runs) and is deliberately not re-executed "
                              "or re-copied here."),
        "exclusions": ("curves/ (regenerable from the recorded seeds) and per-session "
                       "console logs (*_log_*.txt), following the round-one and "
                       "cec2020/lsgo release precedent."),
        "arms": sorted(arms),
        "reused_cell": {"boundary": "20->31 at D=30",
                        "source": "_revision/e3_uniform_low (rev-rel-2026-08-26-dd42d37eb)"},
        "totals": {"files": len(files), "bytes": sum(f["bytes"] for f in files)},
        "files": files,
    }

    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    if MANIFEST.exists():
        os.chmod(MANIFEST, stat.S_IWRITE | stat.S_IREAD)
    MANIFEST.write_bytes(serialize(manifest))
    os.chmod(MANIFEST, stat.S_IREAD | stat.S_IRGRP | stat.S_IROTH)
    print(f"promoted {len(fresh)} files; release {release_id}; "
          f"manifest lists {len(files)} files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
