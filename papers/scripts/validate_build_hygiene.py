#!/usr/bin/env python3
# Copyright (c) 2026 Mostafa Masoud <moustafa.masoud@gmail.com>
"""Build-hygiene gate for the DT-GSK manuscript (review tickets M-001, C-002/C-003).

Three checks, any of which fails the build:

1. UNRESOLVED REFERENCES -- scans the LaTeX logs for
   ``LaTeX Warning: Reference ... undefined`` / ``Citation ... undefined`` and for
   the rendered ``??`` marker. A manuscript that ships "Section ??" is not
   submittable, and the warning is easy to miss in thousands of log lines.

2. CONTROL CHARACTERS IN SOURCES -- scans the manuscript sources for
   non-printable bytes. This exists because of a real defect: a lone carriage
   return once replaced the ``\\r`` of ``\\ref``, so ``\\ref{sec:experiments}``
   rendered as the literal text "efsec:experiments" in the shipped PDF. A bare
   CR (one not part of a CRLF pair) is therefore a hard failure.

3. RETIRED CONTENT -- fails if deliberately removed material resurfaces
   (the oracle study and its release, the BLADE research line, the superseded
   S6.8 numbering, or the corrected NLPSR mis-attribution).

Usage::

    python papers/scripts/validate_build_hygiene.py            # all checks
    python papers/scripts/validate_build_hygiene.py --logs-only
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent          # papers/

SOURCES = [
    ROOT / "main.tex",
    ROOT / "supplementary.tex",
    ROOT / "cover_letter.tex",
    ROOT / "cover_letter.md",
    *sorted((ROOT / "sections").glob("*.tex")),
]
LOGS = [ROOT / "main.log", ROOT / "supplementary.log"]
# Overfull hboxes at or below this are cosmetic (sub-point) and ignored;
# anything larger clips visibly and fails the gate.
OVERFULL_TOL_PT = 2.0

# Deliberately retired material. Each entry: (label, compiled pattern).
# Matched case-insensitively against manuscript sources only -- never against
# the bibliography, where e.g. a title may legitimately contain a word.
RETIRED = [
    # "author-code oracle" is the D-0025 adopted-verbatim external-baselines
    # sentence (main.tex Data Availability; FINAL_PUBLICATION_PLAN.md 0.4 (c))
    # -- a validation-oracle usage unrelated to the removed oracle study, so it
    # is excluded by lookbehind rather than allowlisted by line number.
    ("removed oracle study", re.compile(r"(?<!author-code )\boracle\b", re.I)),
    ("oracle evidence release", re.compile(r"\borc-rel\b", re.I)),
    ("oracle lab code", re.compile(r"\bdt2_oracle\b", re.I)),
    ("removed BLADE research line", re.compile(r"\bBLADE\b")),
    ("superseded S6.8 numbering", re.compile(r"S6\.8\b")),
    ("corrected NLPSR mis-attribution", re.compile(r"AGSK/L-SHADE")),
]

# Control characters that must never appear: everything below 0x20 except
# TAB (09) and LF (0A). CR (0D) is allowed ONLY as part of a CRLF pair.
_BAD_CTRL = {b for b in range(0x20)} - {0x09, 0x0A, 0x0D}


def _fail(msg: str) -> None:
    print(f"  FAIL  {msg}")


def check_logs() -> int:
    """Undefined references/citations in the LaTeX logs."""
    problems = 0
    for log in LOGS:
        if not log.is_file():
            print(f"  SKIP  {log.name} not present")
            continue
        text = log.read_text(encoding="utf-8", errors="ignore")
        for pat, label in (
            (r"LaTeX Warning: Reference [^\n]*undefined", "undefined reference"),
            (r"LaTeX Warning: Citation [^\n]*undefined", "undefined citation"),
            (r"There were undefined references", "undefined references (summary)"),
        ):
            for m in re.findall(pat, text):
                _fail(f"{log.name}: {label}: {m.strip()[:110]}")
                problems += 1
        # Overfull hboxes wider than OVERFULL_TOL_PT clip content at the page
        # edge -- a real desk-reject risk (added after the 2026-07-23 panel
        # found a 219 pt overflow in supplementary.log that only main.log had
        # been checked against). Both logs are now gated.
        for m in re.findall(r"Overfull \\hbox \(([\d.]+)pt too wide\)", text):
            if float(m) > OVERFULL_TOL_PT:
                _fail(f"{log.name}: overfull hbox {m}pt (> {OVERFULL_TOL_PT}pt "
                      "tolerance) -- content clips at the page edge")
                problems += 1
    return problems


def check_rendered_pdfs() -> int:
    """The rendered '??' marker, if pdftotext output is available."""
    problems = 0
    import shutil
    import subprocess
    if not shutil.which("pdftotext"):
        print("  SKIP  pdftotext unavailable; '??' scan skipped")
        return 0
    for pdf in (ROOT / "DT-GSK.pdf", ROOT / "supplementary.pdf"):
        if not pdf.is_file():
            continue
        out = subprocess.run(["pdftotext", str(pdf), "-"],
                             capture_output=True, text=True, errors="ignore")
        n = out.stdout.count("??")
        if n:
            _fail(f"{pdf.name}: {n} occurrence(s) of the unresolved-reference marker '??'")
            problems += n
    return problems


def check_control_characters() -> int:
    """Non-printable bytes in the manuscript sources (the 'efsec' defect)."""
    problems = 0
    for src in SOURCES:
        if not src.is_file():
            continue
        data = src.read_bytes()
        for i, byte in enumerate(data):
            if byte in _BAD_CTRL:
                line = data[:i].count(b"\n") + 1
                _fail(f"{src.name}:{line}: control byte 0x{byte:02X}")
                problems += 1
            elif byte == 0x0D and (i + 1 >= len(data) or data[i + 1] != 0x0A):
                line = data[:i].count(b"\n") + 1
                _fail(f"{src.name}:{line}: lone CR (0x0D) not part of CRLF -- "
                      f"this is the defect that once turned \\ref into 'ef'")
                problems += 1
    return problems


def check_retired_content() -> int:
    """Deliberately removed material must not reappear."""
    problems = 0
    for src in SOURCES:
        if not src.is_file():
            continue
        for lineno, line in enumerate(src.read_text(encoding="utf-8",
                                                    errors="ignore").splitlines(), 1):
            stripped = line.lstrip()
            if stripped.startswith("%"):          # LaTeX comments may discuss history
                continue
            for label, pat in RETIRED:
                if pat.search(line):
                    _fail(f"{src.name}:{lineno}: retired content ({label}): "
                          f"{line.strip()[:90]}")
                    problems += 1
    return problems


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--logs-only", action="store_true",
                    help="run only the undefined-reference log scan (post-compile gate)")
    args = ap.parse_args()

    total = 0
    print("[build-hygiene] unresolved references")
    total += check_logs()
    total += check_rendered_pdfs()

    if not args.logs_only:
        print("[build-hygiene] control characters in sources")
        total += check_control_characters()
        print("[build-hygiene] retired content")
        total += check_retired_content()

    if total:
        print(f"\n[build-hygiene] FAILED with {total} problem(s)")
        return 1
    print("\n[build-hygiene] OK - no unresolved references, control characters, "
          "or retired content")
    return 0


if __name__ == "__main__":
    sys.exit(main())
