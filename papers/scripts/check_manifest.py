#!/usr/bin/env python3
"""Read-only freeze-manifest recompute gate.

Recomputes the SHA-256 of every file tracked in the main manuscript freeze
manifest and reports how many still match the recorded digest.  Pure read-only:
no writes, no network.  Exit code 0 iff every tracked file matches.

Usage
-----
    python papers/scripts/check_manifest.py
    python papers/scripts/check_manifest.py --manifest <path>
    python papers/scripts/check_manifest.py --manifest <path> --manifest <path2> --strict-inventory

Prints e.g. ``12/12 match  []`` on success, or the list of mismatched paths.

``--manifest`` is repeatable. Each manifest's files are byte-checked against its
own declared base exactly as before; the strict-inventory direction then treats
the UNION of all supplied manifests as the listing for each shared evidence
root. This exists because the evidence tree legitimately holds more than one
release (the frozen primary plus the per-suite releases minted later): checked
against any single manifest, the other release's files would all read as
unlisted, so a single-manifest strict inventory can only ever work for a
single-release tree.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

# Repo root = two levels up from papers/scripts/check_manifest.py
_ROOT = Path(__file__).resolve().parents[2]
_DEFAULT_MANIFEST = "papers/governance/main_manuscript_freeze_manifest.json"


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _check_one_manifest(manifest_path: Path) -> tuple[dict, list[str], int, int]:
    """Byte-check one manifest's files against its own declared base.

    Returns ``(manifest, bad, n_ok, n_files, details)`` where ``bad`` carries
    the missing/mismatched/byte-stale findings exactly as historically
    reported and ``details`` maps each finding kind to its list for printing.
    """
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    files = manifest["files"]

    # Manifests come in two shapes: the main-manuscript manifest stores
    # repo-relative paths and declares no root, while the evidence-release
    # manifests store paths relative to their ``evidence_root``. Resolving the
    # latter against the repo root made every tracked file look missing and the
    # gate print "0/3403 match" -- which read as catastrophic corruption when it
    # was only a wrong base directory. Pick the base from the manifest itself.
    _root_field = manifest.get("evidence_root")
    _base = (_ROOT / _root_field).resolve() if _root_field else _ROOT

    mismatched: list[str] = []
    missing: list[str] = []
    byte_stale: list[str] = []
    bad_paths: set[str] = set()
    for entry in files:
        rel = entry["path"]
        target = (_base / rel).resolve()
        if not target.exists():
            missing.append(rel)
            bad_paths.add(rel)
            continue
        if _sha256(target) != entry["sha256"]:
            mismatched.append(rel)
            bad_paths.add(rel)
        # A recorded ``bytes`` count that disagrees with the file on disk is a
        # defect: it means a surgical re-mint updated the hash but not the size
        # (REPRO-001, 2026-07-23). A hash match with a byte mismatch is
        # impossible for the same file, so this only fires on a stale record.
        if "bytes" in entry and target.stat().st_size != int(entry["bytes"]):
            byte_stale.append(f"{rel} (disk {target.stat().st_size} != recorded {entry['bytes']})")
            bad_paths.add(rel)

    bad = missing + mismatched + byte_stale
    # Count DISTINCT bad files: a file failing both the hash and the byte check
    # is one bad file, not two. The historical count subtracted per finding, so
    # one doubly-bad file out of 15 printed "13/15" (and a doubly-bad file out
    # of 1 printed "-1/1"). Exit-code semantics are unchanged.
    n_ok = len(files) - len(bad_paths)
    details = {"missing": missing, "changed": mismatched, "byte-stale": byte_stale}
    return manifest, bad, n_ok, len(files), details


def _check_sources(manifest: dict) -> tuple[list[str], int, int]:
    """Byte-check the optional ``source_files`` list.

    The freeze manifest hashes RENDERS (``cover_letter.pdf``,
    ``supplementary.pdf``/``.docx``) but historically did not hash the
    ``.tex`` they are built from, while ``main.tex`` *was* hashed. That
    asymmetry has a failure mode, and it fired in pass-42: editing
    ``cover_letter.tex`` without rebuilding left ``cover_letter.pdf`` matching
    its recorded digest, so the gate stayed green while the shipped letter --
    which goes to the editor -- still carried a phrasing the paper had
    retracted. Nothing in the output changed, so nothing prompted a rebuild.

    ``source_files`` closes that blind spot without touching ``files``: the
    tracked-file count and its ``N/N match`` line are unchanged, so every
    recorded "15/15" stays true, and a source edited without a rebuild now
    shows up as a source mismatch instead of as silence.
    """
    entries = manifest.get("source_files") or []
    bad: list[str] = []
    for entry in entries:
        rel = entry["path"]
        target = (_ROOT / rel).resolve()
        if not target.exists():
            bad.append(f"{rel} (missing)")
            continue
        if _sha256(target) != entry["sha256"]:
            bad.append(rel)
        elif "bytes" in entry and target.stat().st_size != int(entry["bytes"]):
            bad.append(f"{rel} (disk {target.stat().st_size} != recorded {entry['bytes']})")
    return bad, len(entries) - len(bad), len(entries)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--manifest", action="append", dest="manifests",
                    help="path to a manifest JSON (repo-relative); repeatable -- "
                         "strict inventory then checks disk against the UNION")
    ap.add_argument(
        "--strict-inventory",
        action="store_true",
        help="also FAIL when an evidence tree holds files no supplied manifest "
             "lists (disk -> manifest direction); unlisted files are always reported.",
    )
    args = ap.parse_args(argv)
    manifest_names = args.manifests or [_DEFAULT_MANIFEST]

    all_bad: list[str] = []
    #: evidence_root -> union of listed absolute paths across supplied manifests
    listed_by_root: dict[Path, set[Path]] = {}
    prefix_names = len(manifest_names) > 1
    for name in manifest_names:
        manifest_path = (_ROOT / name).resolve()
        manifest, bad, n_ok, n_files, details = _check_one_manifest(manifest_path)
        label = f"{Path(name).name}: " if prefix_names else ""
        print(f"{label}{n_ok}/{n_files} match  {bad if bad else '[]'}")
        for kind, items in details.items():
            if items:
                print(f"  {kind} : {items}")
        all_bad.extend(bad)
        src_bad, src_ok, src_n = _check_sources(manifest)
        if src_n:
            print(f"{label}sources {src_ok}/{src_n} match  {src_bad if src_bad else '[]'}")
            all_bad.extend(f"source: {s}" for s in src_bad)
        # Commit-field resolvability. Pass-55's mint recorded a published_commit
        # whose tail was invented while expanding an abbreviation, and nothing
        # read the field, so the gate stayed green over a SHA that resolves to
        # nothing. Every recorded commit field must name a real object.
        for fld in ("anchor_commit", "published_commit"):
            sha = manifest.get(fld)
            if not sha:
                continue
            rc = subprocess.run(
                ["git", "cat-file", "-e", str(sha) + "^{commit}"],
                cwd=_ROOT, capture_output=True,
            ).returncode
            if rc != 0:
                print(f"{label}{fld} DOES NOT RESOLVE: {sha}")
                all_bad.append(f"{fld}: {sha} unresolvable")
        root_field = manifest.get("evidence_root")
        if root_field:
            evidence_root = (_ROOT / root_field).resolve()
            listed_by_root.setdefault(evidence_root, set()).update(
                (evidence_root / e["path"]).resolve() for e in manifest["files"]
            )

    # ---- disk -> manifest direction (the blind spot) -----------------------
    # The per-manifest loop only walks manifest -> disk, so a file PRESENT on
    # disk but ABSENT from every manifest is structurally invisible: the counts
    # still read "N/N match" no matter how many extras exist. That is how three
    # unlisted files (BENCHMARK_EVIDENCE_INDEX.md and the mos/ and decc-g/ LSGO
    # baseline tables) sat in benchmarks/cec_reference_results while the gate
    # stayed green. It matters because finalize_evidence.py P6 walks every
    # NON-underscore directory under the evidence root, so an unlisted file
    # outside an underscore-prefixed tree is silently absorbed into the primary
    # release at the next mint, changing its contents and file count with no
    # record. The listing is the UNION of every supplied manifest sharing the
    # root: the tree legitimately holds multiple releases (frozen primary plus
    # the per-suite mints), and no single manifest can vouch for all of them.
    # Reported always; fails the run only under --strict-inventory.
    unlisted: list[str] = []
    for evidence_root, listed in listed_by_root.items():
        if not evidence_root.is_dir():
            continue
        for p in evidence_root.rglob("*"):
            if not p.is_file():
                continue
            rel_parts = p.resolve().relative_to(evidence_root).parts
            if rel_parts and rel_parts[0].startswith("_"):
                continue  # separate immutable release, has its own manifest
            if p.resolve() not in listed:
                unlisted.append(str(p.resolve().relative_to(evidence_root)))

    if unlisted:
        which = "these manifests" if prefix_names else "this manifest"
        print(f"  UNLISTED on disk ({len(unlisted)}), not in {which}:")
        for u in sorted(unlisted):
            print(f"    {u}")
        if args.strict_inventory:
            all_bad = all_bad + [f"unlisted: {u}" for u in unlisted]
    return 0 if not all_bad else 1


if __name__ == "__main__":
    sys.exit(main())
