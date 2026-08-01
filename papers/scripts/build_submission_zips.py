#!/usr/bin/env python3
"""Build the two ZIPs MDPI requires at submission, and prove the first one works.

Why this exists
---------------
The live *Algorithms* Instructions for Authors (retrieved 2026-08-01, closing
assumption A-0001) impose two packaging obligations that no record in this
repository carried:

  1. "Manuscripts prepared in LaTeX must be collated into one ZIP folder
     (including all source files and images, so that the Editorial Office can
     recompile the submitted PDF)."
  2. "File for Figures and Schemes must be provided during submission in a
     single zip archive and at a sufficiently high resolution (preferably no
     less than 600 dpi) in PNG, JPEG or TIFF formats."

Note that (1) contradicts the docstring of ``build_submission_bundle.py``,
which says code is not uploaded to the journal. That remains true of the
*evidence tree*; it is not true of the LaTeX *sources*.

What it does
------------
* ``DT-GSK-latex-source.zip`` -- every file ``main.tex`` actually needs:
  the class and its support files, the five section files, the seven
  ``phase_03`` inputs, the generated tables, ``references.bib``, the frozen
  ``main.bbl`` (so the Editorial Office does not need the bib chain), and every
  included figure. Dependencies are discovered by parsing, not hardcoded.

* ``DT-GSK-figures-600dpi.zip`` -- every included figure rasterised to PNG at
  600 dpi. The sources are vector PDFs, which MDPI does not list as an accepted
  figure format, so they are converted rather than shipped as-is.

VERIFICATION (the part that matters): the source ZIP is extracted into a clean
temporary directory with no access to this repository and recompiled there with
pdflatex. If it does not build, the script fails. A ZIP that "looks complete"
is worth nothing; a ZIP that compiles from scratch is the deliverable.

Outputs land in ``papers/submission/`` and are deliberately NOT added to the
freeze manifest: they are derived from the frozen sources, and hashing them
would mean a re-mint every time they are regenerated.
"""
from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

PAPERS = Path(__file__).resolve().parent.parent
OUT = PAPERS / "submission"
MAIN = "main.tex"

INPUT_RE = re.compile(r"\\(?:input|include)\{([^}]+)\}")
GRAPHIC_RE = re.compile(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}")
BIB_RE = re.compile(r"\\bibliography\{([^}]+)\}")


def resolve(rel: str, exts: tuple[str, ...]) -> Path | None:
    p = PAPERS / rel
    if p.is_file():
        return p
    for e in exts:
        if (q := p.with_suffix(e)).is_file():
            return q
        if (q := Path(str(p) + e)).is_file():
            return q
    return None


def collect() -> set[Path]:
    """Walk \\input/\\includegraphics transitively from main.tex."""
    needed: set[Path] = set()
    queue = [PAPERS / MAIN]
    seen: set[Path] = set()
    while queue:
        cur = queue.pop()
        if cur in seen or not cur.is_file():
            continue
        seen.add(cur)
        needed.add(cur)
        text = cur.read_text(encoding="utf-8", errors="replace")
        # strip comments so commented-out \input lines are not pulled in
        text = re.sub(r"(?<!\\)%.*", "", text)
        for rel in INPUT_RE.findall(text):
            if (t := resolve(rel, (".tex",))) is not None:
                queue.append(t)
        for rel in GRAPHIC_RE.findall(text):
            if (g := resolve(rel, (".pdf", ".png", ".jpg", ".jpeg", ".eps"))) is not None:
                needed.add(g)
        for rel in BIB_RE.findall(text):
            for name in rel.split(","):
                if (b := resolve(name.strip(), (".bib",))) is not None:
                    needed.add(b)
    # class + support files, and the frozen .bbl
    for extra in ("Definitions", "main.bbl"):
        p = PAPERS / extra
        if p.is_dir():
            needed.update(q for q in p.rglob("*") if q.is_file())
        elif p.is_file():
            needed.add(p)
    return needed


# Pinned so regenerating a ZIP whose contents are unchanged yields an identical
# archive. zipfile stamps each entry with the file's mtime by default, which
# would make every rebuild a spurious diff.
PINNED_DT = (2026, 7, 20, 0, 0, 0)


def _add(z: zipfile.ZipFile, path: Path, arcname: str) -> None:
    info = zipfile.ZipInfo(arcname, date_time=PINNED_DT)
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = 0o644 << 16
    z.writestr(info, path.read_bytes())


def build_source_zip(files: set[Path]) -> Path:
    OUT.mkdir(exist_ok=True)
    zp = OUT / "DT-GSK-latex-source.zip"
    with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted(files):
            _add(z, f, f.relative_to(PAPERS).as_posix())
    return zp


def verify_recompiles(zp: Path) -> None:
    """Extract to a clean dir with no repo access and rebuild there."""
    with tempfile.TemporaryDirectory(prefix="dtgsk_srczip_") as td:
        tmp = Path(td)
        with zipfile.ZipFile(zp) as z:
            z.extractall(tmp)
        env = dict(os.environ, SOURCE_DATE_EPOCH="1783468800",
                   FORCE_SOURCE_DATE="1", TEXINPUTS="")
        for i in range(3):
            r = subprocess.run(
                ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", MAIN],
                cwd=tmp, env=env, capture_output=True, text=True)
            if r.returncode != 0:
                log = (tmp / "main.log")
                tail = log.read_text(errors="replace")[-2500:] if log.is_file() else r.stdout[-2500:]
                errs = [l for l in tail.splitlines() if l.startswith("!")][:6]
                raise SystemExit(
                    "FAIL: the source ZIP does not recompile in a clean "
                    "directory (pass %d).\n%s" % (i + 1, "\n".join(errs) or tail[-800:]))
        pdf = tmp / "main.pdf"
        if not pdf.is_file():
            raise SystemExit("FAIL: clean rebuild produced no PDF")
        try:
            import fitz
            n = fitz.open(pdf).page_count
        except Exception:
            n = None
        ref = PAPERS / "DT-GSK.pdf"
        ref_n = None
        if ref.is_file():
            try:
                import fitz
                ref_n = fitz.open(ref).page_count
            except Exception:
                pass
        print("  clean-room rebuild OK: %s (%d pages%s)"
              % (pdf.name, n or -1,
                 "" if ref_n is None else ", shipped PDF has %d" % ref_n))
        if n and ref_n and n != ref_n:
            raise SystemExit("FAIL: clean rebuild is %d pages, shipped is %d"
                             % (n, ref_n))
        # Stronger than a page count: the Editorial Office should be able to
        # reproduce the exact PDF that was submitted.
        if ref.is_file():
            import hashlib
            a = hashlib.sha256(pdf.read_bytes()).hexdigest()
            b = hashlib.sha256(ref.read_bytes()).hexdigest()
            if a == b:
                print("  clean-room PDF is BYTE-IDENTICAL to the shipped "
                      "DT-GSK.pdf (%s)" % a[:16])
            else:
                print("  note: clean-room PDF differs byte-wise from the "
                      "shipped PDF (%s vs %s). Page count matches and it "
                      "compiles, which is what MDPI requires; byte-identity "
                      "additionally depends on the local TeX installation."
                      % (a[:16], b[:16]))


def build_figure_zip(files: set[Path], dpi: int = 600) -> Path:
    figs = sorted(f for f in files
                  if f.suffix.lower() in (".pdf", ".png", ".jpg", ".jpeg")
                  and "figures" in f.parts)
    if not figs:
        raise SystemExit("FAIL: no figures discovered")
    try:
        import fitz
    except ImportError:
        raise SystemExit("FAIL: PyMuPDF is required to rasterise figures")
    OUT.mkdir(exist_ok=True)
    zp = OUT / ("DT-GSK-figures-%ddpi.zip" % dpi)
    made = []
    with tempfile.TemporaryDirectory(prefix="dtgsk_figs_") as td:
        tmp = Path(td)
        for f in figs:
            if f.suffix.lower() == ".pdf":
                doc = fitz.open(f)
                pix = doc[0].get_pixmap(dpi=dpi)
                png = tmp / (f.stem + ".png")
                pix.save(png)
                made.append((png, pix.width, pix.height))
            else:
                dst = tmp / f.name
                shutil.copyfile(f, dst)
                made.append((dst, None, None))
        with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
            for p, _w, _h in sorted(made, key=lambda t: t[0].name):
                _add(z, p, p.name)
    for p, w, h in made:
        print("    %-42s %s" % (p.name, "%dx%d px" % (w, h) if w else "copied as-is"))
    return zp


def main() -> int:
    print("Discovering dependencies from %s ..." % MAIN)
    files = collect()
    tex = sum(1 for f in files if f.suffix == ".tex")
    gfx = sum(1 for f in files if "figures" in f.parts)
    print("  %d files (%d .tex, %d figures, plus class/bib support)"
          % (len(files), tex, gfx))

    print("Building the LaTeX source ZIP ...")
    zp = build_source_zip(files)
    print("  %s (%.1f MB)" % (zp.name, zp.stat().st_size / 1e6))

    print("Verifying it recompiles in a clean room ...")
    verify_recompiles(zp)

    print("Building the 600 dpi figure ZIP ...")
    fz = build_figure_zip(files)
    print("  %s (%.1f MB)" % (fz.name, fz.stat().st_size / 1e6))

    total = zp.stat().st_size + fz.stat().st_size
    print("\nBoth ZIPs total %.1f MB (MDPI's per-submission cap is 120 MB)."
          % (total / 1e6))
    return 0


if __name__ == "__main__":
    sys.exit(main())
