#!/usr/bin/env python3
"""Gate ``reproducibility_manifest.json`` against disk and the freeze manifest.

Why this exists
---------------
``papers/governance/reproducibility_manifest.json`` records a sha256 and byte
count for each of the five shipped artifacts, plus the current freeze anchor.
Nothing read it, and it went silently stale three separate times:

* pass-41 through pass-45, carrying pass-41-era digests for eight passes;
* pass-53, where the refresh ran at the apply commit and the two
  main-manuscript artifacts were rebuilt afterwards -- so the file recorded
  superseded values while its own note asserted it had been verified;
* pass-54, the same way again, which is what motivated this script.

The failure mode is specific and repeatable: the manifest is refreshed EARLY in
a pass, then the artifacts are rebuilt LATE in the same pass. It is not caught
by ``check_manifest.py``, which reads the freeze manifest's ``files[]``, a
different record. A reader who hashes ``DT-GSK.pdf`` against this file -- which
is exactly what contribution C3 invites -- gets a mismatch on the flagship
artifact.

Run it AFTER every rebuild, alongside ``check_manifest.py``.

Usage
-----
    python papers/scripts/check_reproducibility_manifest.py

Exit code 0 when every recorded digest, byte count and anchor matches; 1
otherwise, naming each disagreement.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
GOV = ROOT / "papers" / "governance"
REPRO = GOV / "reproducibility_manifest.json"
FREEZE = GOV / "main_manuscript_freeze_manifest.json"


def main() -> int:
    """Compare the reproducibility manifest with disk and the freeze manifest."""
    repro = json.loads(REPRO.read_bytes().decode("utf-8"))
    freeze = json.loads(FREEZE.read_bytes().decode("utf-8"))
    problems: list[str] = []

    shipped = repro.get("shipped_artifacts", {})
    if not shipped:
        problems.append("shipped_artifacts is empty or missing")

    frozen = {e["path"]: e for e in freeze.get("files", [])}
    for rel, entry in sorted(shipped.items()):
        path = ROOT / rel
        if not path.is_file():
            problems.append(f"{rel}: recorded but absent from the tree")
            continue
        blob = path.read_bytes()
        sha = hashlib.sha256(blob).hexdigest()
        if sha != entry.get("sha256"):
            problems.append(
                f"{rel}: sha256 {entry.get('sha256', '')[:16]} recorded, "
                f"{sha[:16]} on disk"
            )
        if len(blob) != entry.get("bytes"):
            problems.append(
                f"{rel}: bytes {entry.get('bytes')} recorded, {len(blob)} on disk"
            )
        # The freeze manifest is the gated record; the two must not disagree.
        peer = frozen.get(rel)
        if peer and peer["sha256"] != entry.get("sha256"):
            problems.append(
                f"{rel}: disagrees with the freeze manifest's files[] digest"
            )

    anchor = freeze.get("anchor_commit")
    if repro.get("anchor_commit_current") != anchor:
        problems.append(
            f"anchor_commit_current is {repro.get('anchor_commit_current', '')[:9]}, "
            f"but the freeze anchor is {str(anchor)[:9]}"
        )

    n_repro = len([k for k in repro.get("evidence_release", {}) if k != "note"])
    n_freeze = len(freeze.get("evidence_release", {}))
    if n_repro != n_freeze:
        problems.append(
            f"evidence_release lists {n_repro} releases, the freeze manifest {n_freeze}"
        )

    if problems:
        print("[repro-manifest] FAIL")
        for p in problems:
            print(f"  - {p}")
        return 1
    print(
        f"[repro-manifest] OK - {len(shipped)} shipped artifacts match disk "
        f"and the freeze manifest; anchor {str(anchor)[:9]}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
