#!/usr/bin/env python3
# Copyright (c) 2026 Mostafa Masoud <moustafa.masoud@gmail.com>
"""Promote the revision-experiment staging bundles into the immutable evidence tree.

Journal round-1 major revision (CR-0023, D-0047): the four reviewer-requested
experiments were staged under ``results/_revision/`` by
``scripts/run_revision_experiments.py``. This tool promotes them into::

    benchmarks/cec_reference_results/_revision/<arm>/...
    benchmarks/cec_reference_results/_revision/manifest.json

following the flat, manifest-bound layout of the ``_ablation`` release (the
``_releases/`` per-release-copy layout of ``scripts/promote_evidence.py`` was
retired; see ``_index/BENCHMARK_EVIDENCE_INDEX.md``).

Scope and exclusions (cec2020/lsgo release precedent, recorded in-manifest):

* promoted: every ``summary/`` file EXCEPT per-session console logs
  (``*_log_*.txt``), plus the generated leg configs (``_configs/*.yml``) and
  the campaign driver log as provenance;
* excluded: ``curves/`` (one representative convergence CSV per (function,
  dimension); regenerable from recorded seeds) and the per-session console
  logs. Exclusions are named in the manifest, not silently dropped.

Guarantees, matching the project's promotion discipline:

* an existing release subtree is never overwritten (re-running against an
  existing ``_revision/`` tree verifies instead of re-copying);
* every staged file is hashed before copy, the copy is re-hashed and
  byte-verified, and promoted files are set read-only;
* the manifest is written LF, ``indent=2``, ``ensure_ascii=False``, with a
  trailing newline -- the canonical serialization the ``_ablation`` manifest
  uses -- and carries per-file SHA-256 + size plus a self-check summary.

E4 note: this tool promotes whatever complete arms exist. If the E4 legs are
present they are included under ``e4/<cell>/``; if the campaign is still
running, promote E1-E3 now and re-run this tool after completion -- it will
add ONLY the missing arms and append an amendment record, never touching
already-promoted bytes.

Usage::

    python papers/scripts/promote_revision_experiments.py --dry-run
    python papers/scripts/promote_revision_experiments.py
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
DEST = REPO / "benchmarks" / "cec_reference_results" / "_revision"
MANIFEST = DEST / "manifest.json"

RELEASE_ID = "rev-rel-2026-08-26-dd42d37eb"

EXCLUDE_NAME_PATTERNS = ("_log_",)          # per-session console logs
EXCLUDE_DIRS = ("curves", "gen_logs")


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def eligible(path: Path) -> bool:
    if any(part in EXCLUDE_DIRS for part in path.parts):
        return False
    if any(pat in path.name for pat in EXCLUDE_NAME_PATTERNS):
        return False
    return True


def expected_rows(arm: str) -> int:
    """Planned run count per arm: 29 scored functions x runs x dims."""
    if arm.startswith("e1"):
        return 2 * 51 * 29          # D in {50,100}
    if arm.startswith(("e2", "e3")):
        return 4 * 51 * 29          # D in {10,30,50,100}
    if arm.startswith("e4"):
        return 15 * 29              # one dimension, 15 runs
    raise SystemExit(f"unknown arm kind: {arm}")


def collect_arms() -> dict[str, Path]:
    """{arm-name: staging-dir} for every COMPLETE arm present in staging.

    Completeness gate: an arm whose per_run.csv row count is below the planned
    count is SKIPPED with a notice, never promoted partially. This makes the
    tool safe to run at any time, including while the campaign is in flight.
    """
    arms: dict[str, Path] = {}
    for d in sorted(STAGING.iterdir()):
        if not d.is_dir() or d.name.startswith("_"):
            continue
        per_runs = list(d.rglob("per_run.csv"))
        if not per_runs:
            continue
        rows = 0
        for p in per_runs:
            with p.open(encoding="utf-8") as fh:
                rows += max(0, sum(1 for _ in fh) - 1)
        want = expected_rows(d.name)
        if rows < want:
            print(f"SKIP incomplete arm {d.name}: {rows}/{want} rows")
            continue
        if rows > want:
            raise SystemExit(f"ABORT: arm {d.name} has MORE rows than planned "
                             f"({rows} > {want}) -- investigate before promoting")
        arms[d.name] = d
    return arms


def serialize(obj) -> bytes:
    return (json.dumps(obj, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    arms = collect_arms()
    if not arms:
        print("no complete arms in staging")
        return 1

    plan: list[tuple[Path, Path]] = []          # (staging file, dest file)
    for arm, src_root in arms.items():
        for f in sorted(src_root.rglob("*")):
            if f.is_file() and eligible(f):
                plan.append((f, DEST / arm / f.relative_to(src_root)))
    # provenance: leg configs + driver log
    for f in sorted((STAGING / "_configs").glob("*.yml")):
        plan.append((f, DEST / "_configs" / f.name))
    if (STAGING / "driver.log").is_file():
        plan.append((STAGING / "driver.log", DEST / "_provenance" / "driver.log"))

    already = [d for (_s, d) in plan if d.exists()]
    fresh = [(s, d) for (s, d) in plan if not d.exists()]
    print(f"arms: {', '.join(arms)}")
    print(f"plan: {len(plan)} files ({len(already)} already promoted, {len(fresh)} to copy)")
    if args.dry_run:
        for s, d in fresh[:10]:
            print(f"  {s.relative_to(REPO)} -> {d.relative_to(REPO)}")
        if len(fresh) > 10:
            print(f"  ... and {len(fresh) - 10} more")
        return 0

    # verify already-promoted bytes instead of overwriting
    for s, d in plan:
        if d.exists():
            if sha256(s) != sha256(d):
                print(f"ABORT: promoted file differs from staging: {d.relative_to(REPO)}")
                return 1

    copied = []
    for s, d in fresh:
        d.parent.mkdir(parents=True, exist_ok=True)
        src_hash = sha256(s)
        shutil.copy2(s, d)
        if sha256(d) != src_hash:
            print(f"ABORT: byte verification failed for {d.relative_to(REPO)}")
            return 1
        os.chmod(d, stat.S_IREAD | stat.S_IRGRP | stat.S_IROTH)
        copied.append((d, src_hash, d.stat().st_size))

    # (re)build the manifest over the full promoted tree
    files = []
    for f in sorted(DEST.rglob("*")):
        if f.is_file() and f != MANIFEST:
            files.append({
                "path": f.relative_to(DEST).as_posix(),
                "sha256": sha256(f),
                "bytes": f.stat().st_size,
            })

    head = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True,
                          text=True, check=True).stdout.strip()
    prior = None
    if MANIFEST.exists():
        prior = json.loads(MANIFEST.read_bytes().decode("utf-8"))

    manifest = {
        "schema": "revision_evidence_manifest/v1",
        "release_id": RELEASE_ID,
        "title": ("DT-GSK journal round-1 revision experiments (E1 refinement-basis "
                  "contrast, E2 matched population size, E3 uniform-vs-tiered, "
                  "E4 parameter sensitivity)"),
        "generated_utc": _dt.datetime.now(_dt.timezone.utc)
                          .strftime("%Y-%m-%dT%H:%M:%S+00:00"),
        "git_head_at_promotion": head,
        "governance": "CR-0023; D-0047; pre-registered in papers/review_2026_08_24/"
                      "revision_experiments_preregistration.md (signed 2026-08-25, "
                      "before any result existed)",
        "supersedes_release": None,
        "supersession_note": ("Non-superseding. Pairs read-only with the frozen primary "
                              "release rel-2026-07-20-67d9345f9 (panel columns, tiered "
                              "arm) and the frozen ablation release abl-rel-2026-07-20 "
                              "(overlay full / no_finalpolish arms for E1) via the "
                              "unified seed schedule; nothing in either is re-minted."),
        "exclusions": ("curves/ (one representative convergence CSV per (function, "
                       "dimension); regenerable from the recorded seeds) and "
                       "per-session console logs (*_log_*.txt) are excluded, following "
                       "the cec2020/lsgo release precedent."),
        "e4_status": ("included" if any(a.startswith("e4_") for a in arms)
                      else "pending campaign completion; added by amendment"),
        "arms": sorted(arms),
        "amendments": (prior or {}).get("amendments", []),
        "totals": {"files": len(files), "bytes": sum(f["bytes"] for f in files)},
        "files": files,
    }
    if prior is not None:
        manifest["amendments"] = list(prior.get("amendments", []))
        new_arms = sorted(set(arms) - set(prior.get("arms", [])))
        if new_arms:
            manifest["amendments"].append({
                "id": f"A{len(manifest['amendments']) + 1}",
                "date_utc": manifest["generated_utc"],
                "note": f"arms added after initial promotion: {', '.join(new_arms)}",
            })

    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    if MANIFEST.exists():
        os.chmod(MANIFEST, stat.S_IWRITE | stat.S_IREAD)
    MANIFEST.write_bytes(serialize(manifest))
    os.chmod(MANIFEST, stat.S_IREAD | stat.S_IRGRP | stat.S_IROTH)

    # self-check: every manifest entry matches disk
    bad = [e["path"] for e in files
           if sha256(DEST / e["path"]) != e["sha256"]]
    print(f"copied {len(copied)} files; manifest {len(files)} entries; "
          f"self-check {'OK -- all match disk' if not bad else f'FAILED: {bad[:5]}'}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
