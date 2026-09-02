"""Bundle the Supplementary Materials LaTeX sources into one ZIP.

Written for the editorial office's 2026-09-02 request for the supplement in
editable form. It mirrors ``build_submission_zips.py`` (same discovery,
pinned timestamps, clean-room recompile check) but touches a DIFFERENT output
file: that script unconditionally overwrites the two TRACKED zips of the
submitted package, which must not be rewritten after submission.

Dependencies are discovered by parsing ``supplementary.tex``, never
hardcoded, so a source that grows a new input or figure cannot silently ship
an incomplete archive. Pass-64 removed the supplement's citation apparatus,
so no ``.bib`` or ``.bbl`` belongs here; the script asserts that rather than
assuming it.

Output: papers/submission/DT-GSK-supplement-latex-source.zip
"""
from __future__ import annotations

import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

PAPERS = Path(__file__).resolve().parents[1]
ROOT = PAPERS.parent
OUT = PAPERS / "submission" / "DT-GSK-supplement-latex-source.zip"
MAIN = PAPERS / "supplementary.tex"
PDF = PAPERS / "supplementary.pdf"

# Pinned so an unchanged rebuild yields an identical archive; zipfile would
# otherwise stamp each entry with the file's mtime.
PINNED_DT = (2026, 7, 20, 0, 0, 0)
PDF_EPOCH = "1783468800"

# The class needs these regardless of what the body references.
CLASS_FILES = [
    "Definitions/mdpi.cls",
    "Definitions/journalnames.tex",
    "Definitions/logo-mdpi.eps",
    "Definitions/logo-mdpi-eps-converted-to.pdf",
    "Definitions/mdpi.bst",
]

INPUT_RE = re.compile(r"\\input\{([^{}]+)\}")
GRAPHIC_RE = re.compile(r"\\includegraphics(?:\[[^\]]*\])?\{([^{}]+)\}")
COMMENT_RE = re.compile(r"(?<!\\)%.*$", re.MULTILINE)


def resolve(rel: str, exts: tuple[str, ...]) -> Path:
    """Resolve an extensionless LaTeX reference the way TeX does."""
    direct = PAPERS / rel
    if direct.is_file():
        return direct
    for ext in exts:
        cand = PAPERS / (rel + ext)
        if cand.is_file():
            return cand
    sys.exit(f"[supplement-zip] unresolved reference: {rel}")


def collect() -> list[Path]:
    body = COMMENT_RE.sub("", MAIN.read_text(encoding="utf-8"))

    if "\\bibliography{" in body or "\\cite{" in body:
        sys.exit("[supplement-zip] the supplement carries citation apparatus "
                 "again; pass-64 removed it. Re-check before shipping.")

    files = {MAIN, PDF}
    for rel in CLASS_FILES:
        p = PAPERS / rel
        if not p.is_file():
            sys.exit(f"[supplement-zip] missing class file: {rel}")
        files.add(p)

    inputs = sorted(set(INPUT_RE.findall(body)))
    graphics = sorted(set(GRAPHIC_RE.findall(body)))
    for rel in inputs:
        files.add(resolve(rel, (".tex",)))
    for rel in graphics:
        files.add(resolve(rel, (".pdf", ".png", ".jpg", ".jpeg", ".eps")))

    print(f"[supplement-zip] {len(inputs)} inputs, {len(graphics)} figures, "
          f"{len(CLASS_FILES)} class files")
    return sorted(files)


def write_zip(files: list[Path]) -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as z:
        for f in files:
            info = zipfile.ZipInfo(str(f.relative_to(PAPERS)).replace("\\", "/"),
                                   date_time=PINNED_DT)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            z.writestr(info, f.read_bytes())
    print(f"[supplement-zip] wrote {OUT.relative_to(ROOT)} "
          f"({OUT.stat().st_size:,} bytes, {len(files)} members)")


def verify_recompiles() -> None:
    """Extract into a clean directory with TEXINPUTS emptied, so nothing can
    reach back into the repository, and prove the archive builds on its own."""
    with tempfile.TemporaryDirectory(prefix="dtgsk_suppzip_") as tmp:
        work = Path(tmp)
        with zipfile.ZipFile(OUT) as z:
            z.extractall(work)
        env = {"SOURCE_DATE_EPOCH": PDF_EPOCH, "FORCE_SOURCE_DATE": "1",
               "TEXINPUTS": "", "PATH": __import__("os").environ["PATH"]}
        for i in (1, 2, 3):
            r = subprocess.run(
                ["pdflatex", "-interaction=nonstopmode", "-halt-on-error",
                 "supplementary.tex"],
                cwd=work, env=env, capture_output=True, text=True)
            if r.returncode != 0:
                log = (work / "supplementary.log")
                bangs = [ln for ln in log.read_text(errors="replace").splitlines()
                         if ln.startswith("!")][:6] if log.is_file() else []
                sys.exit("[supplement-zip] clean-room pass %d FAILED:\n%s"
                         % (i, "\n".join(bangs) or r.stdout[-800:]))
        built = work / "supplementary.pdf"
        if not built.is_file():
            sys.exit("[supplement-zip] clean-room build produced no PDF")

        def pages(p: Path) -> int:
            return p.read_bytes().count(b"/Type /Page\n") or \
                len(re.findall(rb"/Type\s*/Page[^s]", p.read_bytes()))

        got, want = pages(built), pages(PDF)
        if got != want:
            sys.exit(f"[supplement-zip] clean-room PDF has {got} pages, "
                     f"the shipped one has {want}")
        print(f"[supplement-zip] clean-room recompile OK: 3 passes, "
              f"{got} pages, matches the shipped supplement")


if __name__ == "__main__":
    if not shutil.which("pdflatex"):
        sys.exit("[supplement-zip] pdflatex not on PATH")
    write_zip(collect())
    verify_recompiles()
