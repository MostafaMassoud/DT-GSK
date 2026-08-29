#!/usr/bin/env python3
"""One-command build for the Supplementary Material PDF.

Usage (from the repository root):

    python papers/scripts/build_supplementary.py
    python papers/scripts/build_supplementary.py --rebuild-bib

Default: two pdflatex passes over ``papers/supplementary.tex`` (the
bibliography is the committed ``papers/supplementary.bbl``, input
directly by the document because the MDPI class has no bibtex flow).

``--rebuild-bib``: regenerate ``supplementary.bbl`` first.  The MDPI
class never writes ``\\bibdata`` to the aux file, so this helper runs
one pdflatex pass, appends the ``\\bibdata{references}`` line to the
aux, runs bibtex, then finishes with two pdflatex passes.  Use only
when citations inside the supplementary content change.
"""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

_PAPER = Path(__file__).resolve().parents[1]
_TEX = "supplementary.tex"
_BS = chr(92)


def _pdflatex() -> str:
    exe = shutil.which("pdflatex")
    if not exe:
        sys.exit("[build_supplementary] pdflatex not found on PATH.")
    return exe


# Deterministic build epoch -- see build_pdf.py for why this is pinned in the
# script rather than left to the caller's shell.
SOURCE_DATE_EPOCH = "1783468800"


def _build_env() -> dict:
    """Environment with the deterministic epoch pinned."""
    return dict(os.environ, SOURCE_DATE_EPOCH=SOURCE_DATE_EPOCH,
                FORCE_SOURCE_DATE="1")


def _run_pass(exe: str) -> None:
    r = subprocess.run(
        [exe, "-interaction=nonstopmode", "-halt-on-error", _TEX],
        cwd=_PAPER, capture_output=True, text=True, env=_build_env(),
    )
    if r.returncode != 0:
        log = _PAPER / "supplementary.log"
        tail = log.read_text(encoding="utf-8", errors="replace")[-1200:] if log.exists() else r.stdout[-1200:]
        sys.exit(f"[build_supplementary] pdflatex failed.\n--- log tail ---\n{tail}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--rebuild-bib", action="store_true",
                    help="Regenerate supplementary.bbl via bibtex first.")
    args = ap.parse_args()
    exe = _pdflatex()

    if args.rebuild_bib:
        _run_pass(exe)
        aux = _PAPER / "supplementary.aux"
        text = aux.read_text(encoding="utf-8")
        if _BS + "bibdata" not in text:
            aux.write_text(
                text + _BS + "bibdata{references}\n", encoding="utf-8",
            )
        r = subprocess.run(["bibtex", "supplementary"], cwd=_PAPER, env=_build_env(),
                           capture_output=True, text=True)
        bbl = _PAPER / "supplementary.bbl"
        if not bbl.exists() or "bibitem" not in bbl.read_text(encoding="utf-8"):
            sys.exit("[build_supplementary] bibtex produced no entries:\n"
                     + r.stdout[-800:])
        print("[build_supplementary] supplementary.bbl regenerated")

    _run_pass(exe)
    _run_pass(exe)

    log = (_PAPER / "supplementary.log").read_text(encoding="utf-8",
                                                   errors="replace")
    if "There were undefined" in log:
        sys.exit("[build_supplementary] undefined references remain -- "
                 "inspect papers/supplementary.log")
    pdf = _PAPER / "supplementary.pdf"
    print(f"[build_supplementary] Wrote {pdf}  ({pdf.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
