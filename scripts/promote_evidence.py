#!/usr/bin/env python3
# Copyright (c) 2026 Mostafa Masoud <moustafa.masoud@gmail.com>
"""Promote an accepted staging bundle into the immutable evidence tree.

Implements the scripted ingestion step of the controlled staging-to-evidence
promotion process (``papers/PAPER_BUILD_PROMPT.md`` Section 2.4): staging
outputs under ``results/`` never enter the paper directly -- they are promoted
through this tool into a **new versioned subtree** of the evidence root::

    <dest>/_releases/<release-id>/<suite>/<optimizer>/...      (promoted copy)
    <dest>/_releases/<release-id>/<suite>/<optimizer>_promotion_manifest.json

Design guarantees:

* the flat live layout ``<dest>/<suite>/<optimizer>/`` is **never** written --
  promotion only creates the versioned ``_releases/<release-id>/`` subtree;
* an existing release subtree is never overwritten (corrections require a new
  release id plus an explicit supersession record);
* every staged file is hashed (SHA-256) before the copy, the promoted copy is
  re-hashed and byte-verified against staging, and the promoted files are set
  read-only (``attrib +R`` equivalent via ``os.chmod``);
* the promotion manifest (per-file SHA-256 + size, creation record, byte
  verification result) is written beside the promoted subtree so the promoted
  directory remains a byte-identical mirror of the accepted staging bundle.

Examples
--------
    # inspect the promotion plan without writing anything
    python scripts/promote_evidence.py --staging results/_ablation/baseline/dt-gsk \\
        --suite cec2017 --optimizer dt-gsk --release-id rel-2026-07-15-abc123 --dry-run

    # promote into the default evidence root
    python scripts/promote_evidence.py --staging results/_ablation/baseline/dt-gsk \\
        --suite cec2017 --optimizer dt-gsk --release-id rel-2026-07-15-abc123

    # promote into an alternate destination (e.g. a scratch dest for tool tests)
    python scripts/promote_evidence.py --staging <bundle> --suite cec2011 --optimizer gsk \\
        --release-id rel-test-0001 --dest <temp-dir>
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import stat
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
_DEFAULT_DEST = _REPO / "benchmarks" / "cec_reference_results"

# suite / optimizer / release-id must each be a single, safe path component.
_COMPONENT_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")

MANIFEST_SCHEMA = "promotion_manifest/v1"


def _sha256(path: Path) -> str:
    """Return the SHA-256 hex digest of *path* (streamed)."""
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _git_head() -> str:
    """Best-effort current commit hash for the creation record."""
    try:
        out = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=_REPO, capture_output=True, text=True, timeout=30,
        )
        return out.stdout.strip() if out.returncode == 0 else "unavailable"
    except OSError:
        return "unavailable"


def _collect_staging(staging: Path) -> list[dict]:
    """Hash every file in the staging bundle (sorted, relative POSIX paths)."""
    entries: list[dict] = []
    for p in sorted(q for q in staging.rglob("*") if q.is_file()):
        rel = p.relative_to(staging).as_posix()
        entries.append({
            "path": rel,
            "size_bytes": p.stat().st_size,
            "sha256": _sha256(p),
        })
    return entries


def _set_read_only(path: Path) -> None:
    """Mark *path* read-only (on Windows this sets the +R file attribute)."""
    os.chmod(path, stat.S_IREAD | stat.S_IRGRP | stat.S_IROTH)


def main(argv: list[str] | None = None) -> int:
    """Run the promotion. Returns 0 on success, nonzero on any failure."""
    parser = argparse.ArgumentParser(
        description=(
            "Promote an accepted staging bundle into a new versioned subtree "
            "under the immutable evidence root (Section 2.4)."
        ),
    )
    parser.add_argument("--staging", required=True, help="Accepted staging bundle directory.")
    parser.add_argument("--suite", required=True, help="Benchmark suite id (e.g. cec2017).")
    parser.add_argument("--optimizer", required=True, help="Optimizer id (e.g. dt-gsk).")
    parser.add_argument("--release-id", required=True, help="Immutable release identifier for this promotion.")
    parser.add_argument(
        "--dest",
        default=str(_DEFAULT_DEST),
        help=f"Evidence root to promote into (default: {_DEFAULT_DEST}).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Hash and validate only; print the promotion plan and write nothing.",
    )
    args = parser.parse_args(argv)

    staging = Path(args.staging).resolve()
    dest = Path(args.dest).resolve()

    for label, value in (("suite", args.suite), ("optimizer", args.optimizer), ("release-id", args.release_id)):
        if not _COMPONENT_RE.match(value):
            print(f"ERROR: --{label} '{value}' is not a safe single path component.")
            return 2

    if not staging.is_dir():
        print(f"ERROR: staging directory not found: {staging}")
        return 2

    release_root = dest / "_releases" / args.release_id
    target = release_root / args.suite / args.optimizer
    manifest_path = release_root / args.suite / f"{args.optimizer}_promotion_manifest.json"

    if target.exists() or manifest_path.exists():
        print(f"ERROR: release subtree already exists and is immutable: {target}")
        print("Existing immutable evidence is never overwritten; promote under a NEW release id")
        print("and record an explicit supersession (Section 2.4).")
        return 2
    if staging == target or target.is_relative_to(staging) or staging.is_relative_to(dest):
        print("ERROR: staging bundle and promotion target overlap; refusing self-copy.")
        return 2

    files = _collect_staging(staging)
    if not files:
        print(f"ERROR: staging bundle is empty: {staging}")
        return 2
    total_bytes = sum(f["size_bytes"] for f in files)

    print(f"promotion plan: {len(files)} file(s), {total_bytes} bytes")
    print(f"  staging : {staging}")
    print(f"  target  : {target}")
    print(f"  manifest: {manifest_path}")
    print("  live flat layout untouched: promotion writes only under "
          f"{dest / '_releases' / args.release_id}")

    if args.dry_run:
        print("dry run: nothing written.")
        return 0

    # Copy the accepted bundle into the versioned subtree.
    for entry in files:
        src = staging / entry["path"]
        dst = target / entry["path"]
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)

    # Byte-verify the promoted copy against the accepted staging bundle.
    mismatches: list[str] = []
    for entry in files:
        dst = target / entry["path"]
        if dst.stat().st_size != entry["size_bytes"] or _sha256(dst) != entry["sha256"]:
            mismatches.append(entry["path"])
    if mismatches:
        print(f"ERROR: byte verification FAILED for {len(mismatches)} file(s):")
        for rel in mismatches:
            print(f"  {rel}")
        print("Promoted copy left in place for forensic inspection; do NOT use this release.")
        return 1

    # Make the promoted release read-only (attrib +R equivalent).
    for entry in files:
        _set_read_only(target / entry["path"])

    manifest = {
        "schema": MANIFEST_SCHEMA,
        "release_id": args.release_id,
        "suite": args.suite,
        "optimizer": args.optimizer,
        "staging_root": str(staging),
        "dest_root": str(dest),
        "promoted_subtree": str(target),
        "creation_record": {
            "created_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "tool": "scripts/promote_evidence.py",
            "git_head": _git_head(),
            "process": "PAPER_BUILD_PROMPT.md Section 2.4 controlled staging-to-evidence promotion",
        },
        "verification": {
            "byte_verified": True,
            "files_verified": len(files),
            "mismatches": 0,
            "read_only_applied": True,
        },
        "totals": {"files": len(files), "bytes": total_bytes},
        "files": files,
    }
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, indent=1), encoding="utf-8")
    _set_read_only(manifest_path)

    print(f"promoted {len(files)} file(s); byte verification PASSED; files set read-only.")
    print(f"manifest written: {manifest_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
