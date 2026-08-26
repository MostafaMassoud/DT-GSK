#!/usr/bin/env python3
"""Assemble the lightweight DT-GSK reproduction pack (COMP-001, convenience half).

WHAT THIS IS -- AND IS NOT
--------------------------
This pack is a *convenience download*. It is neither of the two authoritative
channels:

  1. JOURNAL SUBMISSION -- the five deliverables (main PDF/DOCX, supplement
     PDF/DOCX, cover letter; about 13 MB), PLUS the two ZIPs MDPI requires for
     a LaTeX submission: the collated source archive and the 600 dpi figure
     archive, both built by ``build_submission_zips.py``. They are uploaded
     through the journal's own system and the five deliverables are
     hash-recorded in ``papers/governance/submission_package_manifest.json``.
     The EVIDENCE TREE is not uploaded to the journal -- but the LaTeX sources
     are, and an earlier version of this note wrongly said otherwise. The live
     Instructions for Authors (retrieved 2026-08-01, A-0001) require LaTeX
     manuscripts to be "collated into one ZIP folder (including all source
     files and images, so that the Editorial Office can recompile the submitted
     PDF)".

  2. ARCHIVE OF RECORD -- the public repository at
     https://github.com/MostafaMassoud/DT-GSK (public since 2026-08-01, D-0044),
     including the full evidence tree (``curves/`` and all), bound to the
     immutable evidence release rel-2026-07-20-67d9345f9 and the two later
     suite releases by a SHA-256 manifest over every released file. That is
     what the Data Availability Statement cites and the copy to use to
     reproduce or audit the work. No Zenodo deposit and no repository DOI
     exist (D-0037 limbs still in force); the article DOI comes from the
     journal after acceptance.

This pack exists only so a reviewer can obtain the implementation, the frozen
configuration, the analysis bundle and the summary-level evidence without
cloning the full ~1.2 GB repository. Nothing here is authoritative; if this
pack and the archived release ever disagree, the release wins.

CONTENTS
--------
Everything needed to re-derive each reported NUMBER: the five deliverables, the
implementation, the hash-frozen configuration, the analysis bundle, the
governance manifests, the docs/runbook, and the summary-level evidence (per-run
records, per-suite CSVs, per-cell provenance manifests).

EXCLUDED, deliberately: ``curves/`` (~1117 MB) and ``gen_logs/`` (~35 MB) --
the per-generation convergence traces. They feed the convergence FIGURES only;
no table, statistic, rank, p-value or claim depends on them. Excluding them is
what keeps this a light download. They are present in full in the repository
and its archived release.

``SIZE_GUARD_BYTES`` below is a self-check that this stays "light" -- it is a
property of this pack, not a journal limit.

Output (written outside ``papers/`` so it cannot trip the build-hygiene
source scanners):

    dist/dtgsk_reproduction_pack.zip
    dist/dtgsk_reproduction_pack_manifest.json

Usage::

    python papers/scripts/build_submission_bundle.py
"""
from __future__ import annotations

import hashlib
import json
import zipfile
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parent.parent
OUT_DIR = ROOT / "dist"
ZIP_PATH = OUT_DIR / "dtgsk_reproduction_pack.zip"
MANIFEST_PATH = OUT_DIR / "dtgsk_reproduction_pack_manifest.json"

# Self-check that the pack stays a light download. NOT a journal limit.
SIZE_GUARD_BYTES = 120 * 1024 * 1024

# Directory names pruned wherever they occur (the bulk convergence traces).
PRUNE_DIRS = {"curves", "gen_logs", "__pycache__", ".pytest_cache", ".ipynb_checkpoints"}
PRUNE_SUFFIXES = {".pyc", ".pyo"}

# Individual files (relative to ROOT).
FILES = [
    "papers/DT-GSK.pdf",
    "papers/DT-GSK.docx",
    "papers/supplementary.pdf",
    "papers/supplementary.docx",
    "papers/cover_letter.pdf",
    "README.md",
    "LICENSE",
    "pyproject.toml",
    "run.py",
]

# Directory trees (relative to ROOT), pruned by PRUNE_DIRS.
TREES = [
    "src",
    "configs",
    "scripts",
    "tests",
    "docs",
    "papers/analysis",
    "papers/governance",
    "benchmarks/cec_reference_results",
]

README = """# DT-GSK reproduction pack (convenience copy)

This archive accompanies the manuscript "DT-GSK: Dimension-Tiered Adaptive
Configuration Selection and Deterministic Refinement for Gaining-Sharing
Knowledge Optimization".

Evidence release: rel-2026-07-20-67d9345f9  (ablation: abl-rel-2026-07-20)

## This is a convenience copy, not the archive of record

* The **journal submission** is the five deliverables only (main PDF/DOCX,
  supplement PDF/DOCX, cover letter). Code and evidence are not uploaded there.
* The **archive of record** is the project's full evidence tree, bound to the
  immutable evidence release `rel-2026-07-20-67d9345f9` (and the two later,
  non-superseding suite releases) by a SHA-256 manifest over every released
  file. It is supplied by the corresponding author on reasonable request, which
  is what the Data Availability Statement cites. This pack is a lighter subset
  of it; if the two ever disagree, **the full evidence tree wins.**

This pack exists only so the implementation and summary evidence can be
obtained without cloning the full (~1.2 GB) repository.

## What is here

* `papers/`      - the five deliverables, the derived analysis bundle, and the
                   governance manifests (including the SHA-256 freeze manifest
                   covering every tracked source and artifact).
* `src/`, `configs/`, `scripts/`, `run.py` - the implementation and the single
                   hash-frozen configuration.
* `tests/`       - the regression suite, including the byte-stability and
                   configuration-lock tests.
* `docs/`        - the runbook and the reproduction guides.
* `benchmarks/cec_reference_results/` - the SUMMARY-level frozen evidence:
                   per-run records, per-suite result CSVs, and the per-cell
                   environment/verification/protocol manifests.

## What is deliberately NOT here

`curves/` (~1117 MB) and `gen_logs/` (~35 MB) - the per-generation convergence
traces. They are inputs to the convergence FIGURES only: no table, statistic,
rank, p-value or reported claim depends on them. Omitting them is what keeps
this a light download; they are present in full in the repository and its
archived release.

Reproducing every reported NUMBER requires only what is in this archive;
reproducing the convergence figures additionally requires those traces.

## Reproducing

See `docs/getting-started/runbook.md` (routine commands) and
`docs/development/evidence_rerun_runbook.md` (procedure of record). Every
empirical value derives from the frozen release named above; reproduction means
re-deriving the analysis and artifacts from it, not re-optimizing.
"""


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def keep(path: Path) -> bool:
    if path.suffix in PRUNE_SUFFIXES:
        return False
    return not any(part in PRUNE_DIRS for part in path.parts)


def collect() -> list[Path]:
    out: list[Path] = []
    for rel in FILES:
        p = ROOT / rel
        if p.is_file():
            out.append(p)
        else:
            print(f"  NOTE: missing optional file {rel}")
    for rel in TREES:
        base = ROOT / rel
        if not base.is_dir():
            print(f"  NOTE: missing tree {rel}")
            continue
        for p in sorted(base.rglob("*")):
            if p.is_file() and keep(p.relative_to(ROOT)):
                out.append(p)
    seen, uniq = set(), []
    for p in sorted(out):
        if p not in seen:
            seen.add(p)
            uniq.append(p)
    return uniq


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    # Remove the pre-2026-07-24 name so the stale artifact cannot linger.
    for stale in ("dtgsk_submission_bundle.zip", "dtgsk_submission_bundle_manifest.json"):
        (OUT_DIR / stale).unlink(missing_ok=True)

    members = collect()
    raw = sum(p.stat().st_size for p in members)
    print(f"  {len(members)} files, {raw / 1024 / 1024:.1f} MB uncompressed")

    ZIP_PATH.unlink(missing_ok=True)
    zinfo_date = (1980, 1, 1, 0, 0, 0)  # fixed timestamp -> reproducible archive
    with zipfile.ZipFile(ZIP_PATH, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        zi = zipfile.ZipInfo("README_PACK.md", date_time=zinfo_date)
        zi.compress_type = zipfile.ZIP_DEFLATED
        zi.external_attr = 0o644 << 16
        z.writestr(zi, README)
        for p in members:
            zi = zipfile.ZipInfo(p.relative_to(ROOT).as_posix(), date_time=zinfo_date)
            zi.compress_type = zipfile.ZIP_DEFLATED
            zi.external_attr = 0o644 << 16
            z.writestr(zi, p.read_bytes())

    size = ZIP_PATH.stat().st_size
    print(f"  wrote {ZIP_PATH.relative_to(ROOT)}  {size / 1024 / 1024:.1f} MB")

    manifest = {
        "schema": "dtgsk_reproduction_pack/v1",
        "role": ("convenience reproduction pack -- NOT the journal submission "
                 "(five deliverables only) and NOT the archive of record (the "
                 "tagged, DOI-archived repository release)"),
        "evidence_release": "rel-2026-07-20-67d9345f9",
        "ablation_release": "abl-rel-2026-07-20",
        "size_guard_bytes": SIZE_GUARD_BYTES,
        "archive": ZIP_PATH.name,
        "archive_bytes": size,
        "archive_sha256": sha256(ZIP_PATH),
        "file_count": len(members) + 1,
        "uncompressed_bytes": raw,
        "excluded": {
            "directories": ["curves", "gen_logs"],
            "reason": ("per-generation convergence traces; inputs to the "
                       "convergence figures only -- no table, statistic, rank, "
                       "p-value or claim depends on them. Present in full in "
                       "the repository and its archived release."),
        },
        "authoritative_channels": {
            "journal_submission": ("five deliverables only; hashes in "
                                   "papers/governance/submission_package_manifest.json"),
            "archive_of_record": ("public repository https://github.com/MostafaMassoud/DT-GSK "
                                  "(full evidence tree bound to the immutable "
                                  "releases by SHA-256 manifest). No Zenodo "
                                  "deposit or repository DOI (D-0037/D-0044)"),
        },
    }
    MANIFEST_PATH.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"  wrote {MANIFEST_PATH.relative_to(ROOT)}")

    if size > SIZE_GUARD_BYTES:
        raise SystemExit(
            f"HARD FAIL - pack {size / 1024 / 1024:.1f} MB exceeds the "
            f"{SIZE_GUARD_BYTES / 1024 / 1024:.0f} MB light-download guard")
    print(f"  OK - within the {SIZE_GUARD_BYTES / 1024 / 1024:.0f} MB "
          f"light-download guard ({100 * size / SIZE_GUARD_BYTES:.1f}% used)")


if __name__ == "__main__":
    main()
