"""Gate: the built Python package must never swallow the evidence bank.

``pyproject.toml`` requests ``benchmarks*`` packages with
``include-package-data = true`` and a package-data glob over
``benchmarks/cec_reference_results/**``. Today's setuptools resolves that to a
small wheel (the reference-results tree is not importable package data), but
that outcome is behavioral, not declared -- a future setuptools could start
honoring the glob and silently produce a ~1.2 GB wheel carrying the frozen
evidence bank, and an sdist could sweep in withheld or acquired material if
ignore rules drift.

This gate builds the sdist and wheel into a temporary directory and fails if
either artifact:

* contains any file from the frozen evidence bank
  (``benchmarks/cec_reference_results/``) other than markdown documentation;
* contains anything from ``papers/``, ``reference_papers/``, ``results/``,
  or a reviewer/withheld filename pattern;
* exceeds a hard size or member-count bound far above the known-good build
  (wheel ~7 MB / ~150 members, sdist ~7.5 MB / ~400 members at pass-59).

Run it from the repository root::

    python scripts/check_package_contents.py

Exit code 0 means both artifacts are clean. The build runs with
``--no-isolation`` (uses the installed setuptools) and takes a few seconds.
"""
from __future__ import annotations

import re
import subprocess
import sys
import tarfile
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Hard ceilings, far above the known-good pass-59 build but far below any
# evidence-bank accident (the bank alone is ~1.2 GB across ~6,000 CSVs).
MAX_MEMBERS = 2000
MAX_UNCOMPRESSED_BYTES = 60 * 1024 * 1024  # 60 MB

FORBIDDEN = re.compile(
    r"(benchmarks/cec_reference_results/.+\.(?!md$)[a-z0-9]+$)"
    r"|(^|/)papers/"
    r"|(^|/)reference_papers/"
    r"|(^|/)results/"
    r"|(^|/)paper-revisions/"
    r"|reviewer"
    r"|PRIVATE_OPS"
    r"|AUTHOR_DATA_HANDOFF"
    r"|review_2026_08_24",
    re.IGNORECASE,
)


def wheel_members(path: Path) -> list[tuple[str, int]]:
    with zipfile.ZipFile(path) as z:
        return [(i.filename, i.file_size) for i in z.infolist()]


def sdist_members(path: Path) -> list[tuple[str, int]]:
    with tarfile.open(path, "r:gz") as t:
        return [(m.name, m.size) for m in t.getmembers() if m.isfile()]


def check(kind: str, members: list[tuple[str, int]]) -> list[str]:
    problems = []
    total = sum(size for _, size in members)
    if len(members) > MAX_MEMBERS:
        problems.append(f"{kind}: {len(members)} members exceeds bound {MAX_MEMBERS}")
    if total > MAX_UNCOMPRESSED_BYTES:
        problems.append(
            f"{kind}: {total:,} uncompressed bytes exceeds bound "
            f"{MAX_UNCOMPRESSED_BYTES:,}"
        )
    bad = [name for name, _ in members if FORBIDDEN.search(name)]
    for name in bad[:20]:
        problems.append(f"{kind}: forbidden member {name}")
    if len(bad) > 20:
        problems.append(f"{kind}: ... and {len(bad) - 20} more forbidden members")
    print(f"[package-contents] {kind}: {len(members)} members, "
          f"{total:,} bytes uncompressed, {len(bad)} forbidden")
    return problems


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        # Build from a pristine `git archive` export, never in the working
        # tree: an in-tree build stages the sdist inside the repository and
        # regenerates gsk_family.egg-info there, and BOTH leak state -- a
        # failed run leaves read-only staging copies that every later sdist
        # re-tars, and a stale egg-info SOURCES.txt re-includes files the
        # current config no longer selects (both observed 2026-08-29). The
        # export also tests exactly what a clone of the public repo gets.
        src = Path(tmp) / "src"
        src.mkdir()
        tar_path = Path(tmp) / "tree.tar"
        with open(tar_path, "wb") as fh:
            proc = subprocess.run(["git", "archive", "HEAD"], cwd=ROOT,
                                  stdout=fh, stderr=subprocess.PIPE, text=False)
        if proc.returncode != 0:
            print("[package-contents] FAILED - git archive error:")
            print(proc.stderr.decode(errors="replace")[-2000:])
            return 1
        with tarfile.open(tar_path) as t:
            t.extractall(src)
        proc = subprocess.run(
            [sys.executable, "-m", "build", "--no-isolation", "--outdir", tmp,
             str(src)],
            capture_output=True, text=True,
        )
        if proc.returncode != 0:
            print("[package-contents] FAILED - build error:")
            print(proc.stdout[-2000:])
            print(proc.stderr[-2000:])
            return 1
        out = Path(tmp)
        wheels = sorted(out.glob("*.whl"))
        sdists = sorted(out.glob("*.tar.gz"))
        if not wheels or not sdists:
            print(f"[package-contents] FAILED - expected one wheel and one "
                  f"sdist, found {len(wheels)} / {len(sdists)}")
            return 1
        problems = check("wheel", wheel_members(wheels[0]))
        problems += check("sdist", sdist_members(sdists[0]))
    if problems:
        print(f"[package-contents] FAILED with {len(problems)} problem(s)")
        for p in problems:
            print("  -", p)
        return 1
    print("[package-contents] OK - built artifacts stay within bounds and "
          "carry no evidence-bank, papers/, or withheld material")
    return 0


if __name__ == "__main__":
    sys.exit(main())
