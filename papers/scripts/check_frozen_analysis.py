#!/usr/bin/env python3
"""Verify the frozen primary-release analysis outputs are byte-identical.

Everything the submitted manuscript says about CEC2017, CEC2011 and CEC2013 is
computed from `papers/analysis/rel-2026-07-20-67d9345f9/**`. Those files are the
provenance of the abstract's headline rank, the Friedman/Nemenyi exhibits and
the pairwise tables. Adding two suites means new analysis code runs in the same
process space as the old; the cheapest possible protection against a silent
regression is to hash the frozen tree once and re-check it after every phase.

    python papers/scripts/check_frozen_analysis.py            # verify (exit 1 on drift)
    python papers/scripts/check_frozen_analysis.py --mint     # (re)create the snapshot

The snapshot lives at papers/governance/frozen_analysis_manifest.json and is
itself committed, so drift is visible in review as well as at runtime.

A missing file is as much a failure as a changed one, and an unexpected NEW file
under the frozen tree is reported too: it means something wrote where nothing
should write.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FROZEN_REL_ID = "rel-2026-07-20-67d9345f9"
FROZEN_DIR = ROOT / "papers" / "analysis" / FROZEN_REL_ID
MANIFEST = ROOT / "papers" / "governance" / "frozen_analysis_manifest.json"


def _digest(path: Path) -> str:
    """Return the SHA-256 of one file."""
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _scan() -> dict[str, str]:
    """Hash every file under the frozen analysis tree, path-sorted."""
    if not FROZEN_DIR.is_dir():
        raise SystemExit(f"frozen analysis tree is missing: {FROZEN_DIR}")
    return {
        p.relative_to(FROZEN_DIR).as_posix(): _digest(p)
        for p in sorted(FROZEN_DIR.rglob("*"))
        if p.is_file()
    }


def mint() -> int:
    """Write the snapshot manifest from the current tree."""
    files = _scan()
    MANIFEST.write_text(
        json.dumps(
            {
                "release_id": FROZEN_REL_ID,
                "base_path": f"papers/analysis/{FROZEN_REL_ID}",
                "purpose": (
                    "Byte-identity guard. These outputs back every CEC2017, "
                    "CEC2011 and CEC2013 number in the submitted manuscript "
                    "and must not change while new suites are added."
                ),
                "file_count": len(files),
                "files": files,
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"minted {MANIFEST.relative_to(ROOT)} with {len(files)} files")
    return 0


def verify() -> int:
    """Compare the tree against the snapshot; return a process exit code."""
    if not MANIFEST.is_file():
        raise SystemExit(f"no snapshot to verify against: {MANIFEST} (run --mint)")
    expected = json.loads(MANIFEST.read_text(encoding="utf-8"))["files"]
    observed = _scan()

    changed = sorted(k for k in expected.keys() & observed.keys()
                     if expected[k] != observed[k])
    missing = sorted(expected.keys() - observed.keys())
    added = sorted(observed.keys() - expected.keys())

    if not (changed or missing or added):
        print(f"frozen analysis outputs unchanged: {len(expected)}/{len(expected)} "
              f"files byte-identical ({FROZEN_REL_ID})")
        return 0

    print(f"FROZEN ANALYSIS DRIFT under papers/analysis/{FROZEN_REL_ID}:")
    for label, items in (("changed", changed), ("missing", missing), ("added", added)):
        for item in items:
            print(f"- {label}: {item}")
    print(
        "\nThese files back the manuscript's published CEC2017/CEC2011/CEC2013 "
        "numbers. Do not re-mint the snapshot to make this pass -- find what "
        "wrote here, revert it, and re-check."
    )
    return 1


def main(argv: list[str] | None = None) -> int:
    """Entry point."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--mint", action="store_true",
                        help="(re)create the snapshot instead of verifying it")
    args = parser.parse_args(argv)
    return mint() if args.mint else verify()


if __name__ == "__main__":
    sys.exit(main())
