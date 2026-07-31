#!/usr/bin/env python3
"""Build the paper-facing PDF (``DT-GSK.pdf``) from ``main.tex``.

The canonical LaTeX source must stay at ``papers/main.tex`` because the
MDPI LaTeX class expects that exact filename.  pdflatex consequently
produces ``papers/main.pdf``; this script drives the full four-pass
LaTeX + BibTeX compile and then renames the resulting PDF to the
paper-facing artefact ``papers/DT-GSK.pdf`` so that the PDF matches
the companion Word build (``DT-GSK.docx``).

Usage
-----
    python papers/scripts/build_pdf.py

The script cd's into ``paper/`` before invoking pdflatex, so every
``\\input{sections/...}`` / ``\\includegraphics{figures/...}`` path
resolves exactly the same way it does during a manual compile.

Behaviour
---------
* Runs ``pdflatex`` + ``bibtex`` + ``pdflatex`` * 2 in sequence.
* On success, moves ``main.pdf`` to ``DT-GSK.pdf``.
* If ``DT-GSK.pdf`` is locked (typical cause: open in a PDF viewer)
  the renamed artefact is written to ``DT-GSK.new.pdf`` so the build
  still produces output the user can diff.
* Auxiliary files (``main.aux``, ``main.bbl``, ``main.log``, ...) are
  left in place for incremental rebuilds; ``make clean`` sweeps them.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent  # .../paper/
MAIN_TEX = ROOT / "main.tex"
# pdflatex always writes the PDF using the .tex stem; we rename it
# after the build so the user-facing filename matches the paper title.
INTERMEDIATE_PDF = ROOT / "main.pdf"
OUT_PDF = ROOT / "DT-GSK.pdf"

# Full four-pass compile: first pdflatex seeds the .aux, bibtex reads
# the .aux to produce the .bbl, two more pdflatex passes incorporate
# the .bbl and resolve cross-references / table-of-contents entries.
_PDFLATEX_ARGS = ["-interaction=nonstopmode", "-halt-on-error", "main.tex"]


def _resolve_tool(name: str) -> str:
    """Return the best available path for a LaTeX build tool."""
    on_path = shutil.which(name)
    if on_path:
        return on_path
    raise FileNotFoundError(
        f"{name} not found on PATH.  Install a TeX distribution "
        f"(e.g. MiKTeX on Windows, TeX Live on Linux/macOS) so the "
        f"paper can be compiled."
    )


def _run(cmd: list[str], *, label: str) -> int:
    """Invoke ``cmd`` from ROOT and stream its exit code back."""
    print(f"[build_pdf] {label}: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=str(ROOT))
    return result.returncode


def _full_compile() -> int:
    """Run pdflatex + bibtex + pdflatex + pdflatex.

    Returns 0 on success, a non-zero exit code from the first failing
    tool otherwise.  We halt on the first hard error to avoid masking
    a pdflatex failure behind a successful bibtex that used stale .aux.
    """
    pdflatex = _resolve_tool("pdflatex")
    bibtex = _resolve_tool("bibtex")

    rc = _run([pdflatex, *_PDFLATEX_ARGS], label="pass 1")
    if rc != 0:
        return rc
    rc = _run([bibtex, "main"], label="bibtex")
    if rc != 0:
        return rc
    rc = _run([pdflatex, *_PDFLATEX_ARGS], label="pass 2")
    if rc != 0:
        return rc
    rc = _run([pdflatex, *_PDFLATEX_ARGS], label="pass 3")
    return rc


def _finalise(intermediate: Path, target: Path) -> Path:
    """Move ``intermediate`` onto ``target``, tolerating a locked target.

    If the target path cannot be written (typical cause: a PDF reader
    is holding a lock on the Windows file handle), fall back to a
    ``<target>.new.pdf`` sibling and warn the user.
    """
    try:
        os.replace(intermediate, target)
        return target
    except PermissionError:
        fallback = target.with_name(target.stem + ".new" + target.suffix)
        try:
            os.replace(intermediate, fallback)
        except OSError as exc:
            raise RuntimeError(
                f"could not finalise PDF path: {exc}"
            ) from exc
        print(
            f"[build_pdf] ! {target.name} is locked (open in a viewer?); "
            f"wrote {fallback.name} instead",
            file=sys.stderr,
        )
        return fallback


def main() -> int:
    if not MAIN_TEX.is_file():
        print(f"error: {MAIN_TEX} not found", file=sys.stderr)
        return 1

    rc = _full_compile()
    if rc != 0:
        print(
            f"[build_pdf] LaTeX compile failed with exit code {rc}. "
            "Inspect papers/main.log for details.",
            file=sys.stderr,
        )
        return rc

    if not INTERMEDIATE_PDF.is_file():
        print(
            f"[build_pdf] expected {INTERMEDIATE_PDF} after compile, "
            "but it does not exist",
            file=sys.stderr,
        )
        return 1

    final_path = _finalise(INTERMEDIATE_PDF, OUT_PDF)
    size = final_path.stat().st_size
    try:
        rel = final_path.relative_to(ROOT.parent)
    except ValueError:
        rel = final_path
    print(f"[build_pdf] Wrote {rel}  ({size:,} bytes)")

    # M-001 gate: a manuscript that ships "Section ??" is not submittable, and
    # the LaTeX warning that precedes it is trivial to lose among thousands of
    # log lines. Fail the build here instead of discovering it in review.
    gate = Path(__file__).with_name("validate_build_hygiene.py")
    if gate.is_file():
        rc = subprocess.run([sys.executable, "-X", "utf8", str(gate),
                             "--logs-only"]).returncode
        if rc != 0:
            print("[build_pdf] build-hygiene gate FAILED: unresolved references")
            return rc
    return 0


if __name__ == "__main__":
    sys.exit(main())
