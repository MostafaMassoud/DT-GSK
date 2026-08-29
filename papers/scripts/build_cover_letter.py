#!/usr/bin/env python3
"""Build ``cover_letter.pdf`` from ``cover_letter.tex`` with the pinned epoch.

Why this exists
---------------
``cover_letter.pdf`` is ``files[10]`` of the freeze manifest and
``cover_letter.tex`` is one of its two hashed ``source_files``, yet until
pass-54 there was no builder for it: ``build_pdf.py`` and
``build_supplementary.py`` cover the manuscript and the supplement, and
``finalize_evidence.py`` P10 builds those two plus the two DOCX.  Anyone
rebuilding the cover letter therefore ran ``pdflatex`` by hand, which stamps a
wall-clock ``/CreationDate`` and produces a PDF that is not byte-reproducible.

That is the same defect pass-54 closed for the other two builders, on the one
document that ships to the editor -- and the one pass-42 already broke once by
editing the source, skipping the rebuild, and leaving a green gate on a stale
render.  ``check_manifest`` would flag the changed digest, but the natural
operator response is to re-mint the manifest, which silently records a
wall-clock PDF under a manifest asserting double-build identity.

Usage
-----
    python papers/scripts/build_cover_letter.py

The epoch is pinned here, not left to the caller's shell, for the same reason
it is pinned in ``build_pdf.py``.  Note that the DOCX epoch is a *different*
number (see ``_word_ooxml.py``); do not export either into a shared shell.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent  # .../papers/
TEX = ROOT / "cover_letter.tex"
OUT_PDF = ROOT / "cover_letter.pdf"

# Same epoch as the manuscript and the supplement (D:20260708000000Z).
SOURCE_DATE_EPOCH = "1783468800"

_PDFLATEX_ARGS = ["-interaction=nonstopmode", "-halt-on-error", "cover_letter.tex"]


def _resolve_tool(name: str) -> str:
    """Return the best available path for a LaTeX build tool."""
    found = shutil.which(name)
    if found:
        return found
    raise FileNotFoundError(
        f"{name} not found on PATH.  Install a TeX distribution "
        f"(e.g. MiKTeX on Windows, TeX Live on Linux/macOS)."
    )


def _build_env() -> dict[str, str]:
    """Environment with the deterministic epoch pinned."""
    return dict(os.environ, SOURCE_DATE_EPOCH=SOURCE_DATE_EPOCH,
                FORCE_SOURCE_DATE="1")


def _run(cmd: list[str], *, label: str) -> int:
    """Invoke ``cmd`` from ROOT and stream its exit code back."""
    print(f"[build_cover_letter] {label}: {' '.join(cmd)}")
    return subprocess.run(cmd, cwd=str(ROOT), env=_build_env()).returncode


def main() -> int:
    """Compile the cover letter twice and report the resulting size."""
    if not TEX.is_file():
        print(f"[build_cover_letter] missing source: {TEX}", file=sys.stderr)
        return 1
    pdflatex = _resolve_tool("pdflatex")
    # Two passes: the letter has no bibliography, but a second pass settles
    # any page-dependent reference before the digest is taken.
    for n in (1, 2):
        rc = _run([pdflatex, *_PDFLATEX_ARGS], label=f"pass {n}")
        if rc != 0:
            print(f"[build_cover_letter] pdflatex failed (exit {rc})", file=sys.stderr)
            return rc
    if not OUT_PDF.is_file():
        print("[build_cover_letter] no cover_letter.pdf produced", file=sys.stderr)
        return 1
    print(f"[build_cover_letter] Wrote {OUT_PDF}  ({OUT_PDF.stat().st_size:,} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
