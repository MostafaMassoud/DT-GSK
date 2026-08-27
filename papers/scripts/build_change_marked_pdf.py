"""Build the change-marked manuscript that MDPI check-list item (II) asks for.

Item (II) of the round-one decision letter says: "Highlight any revisions to the
manuscript, so editors and reviewers can see any changes made."  The submission
kit previously answered that with a change register -- a companion document
listing changed passages -- because latexdiff was believed unusable here.  It is
usable: MiKTeX ships ``latexdiff.exe`` as a shim whose Perl script was never
installed, and the *standalone* variant ``latexdiff-so`` bundles Algorithm::Diff
and runs as installed.  Use ``latexdiff-so``; plain ``latexdiff`` will fail on a
missing Algorithm::Diff unless that CPAN module is installed separately.

Requires the ``ulem`` LaTeX package (latexdiff's strikeout markup).  If MiKTeX
cannot reach a repository, register one per invocation:

    mpm --repository=<mirror>/systems/win32/miktex/tm/packages/ --install=ulem

Nothing in the frozen tree is touched: both sides are exported with ``git
archive`` into a scratch directory and the compile happens there.  The output is
derived and is NOT committed, matching how the change register is handled.

    python papers/scripts/build_change_marked_pdf.py
    python papers/scripts/build_change_marked_pdf.py --base v2.13 --new v2.21
"""
from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EPOCH = "1783468800"          # the PDF epoch; see runbook.md step 7
DEFAULT_BASE = "v2.13"        # the state actually submitted to Algorithms


def run(cmd, cwd, label, env=None):
    res = subprocess.run(cmd, cwd=str(cwd), env=env,
                         capture_output=True, text=True, errors="replace")
    if res.returncode != 0:
        sys.stderr.write("[%s] exit %d\n%s\n" % (label, res.returncode, res.stdout[-3000:]))
    return res.returncode


def export(ref: str, dest: Path) -> None:
    dest.mkdir(parents=True, exist_ok=True)
    archive = subprocess.run(["git", "archive", ref, "papers/"], cwd=str(ROOT),
                             capture_output=True)
    if archive.returncode != 0:
        sys.exit("git archive %s failed: %s" % (ref, archive.stderr.decode(errors="replace")))
    tar = subprocess.run(["tar", "-x", "-C", str(dest)], input=archive.stdout,
                         capture_output=True)
    if tar.returncode != 0:
        sys.exit("tar extract failed for %s" % ref)


def page_count(pdf: Path) -> int:
    return len(re.findall(rb"/Type\s*/Page[^s]", pdf.read_bytes()))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--base", default=DEFAULT_BASE, help="submitted state (default %s)" % DEFAULT_BASE)
    ap.add_argument("--new", default="HEAD", help="revised state (default HEAD)")
    ap.add_argument("--out", default=str(ROOT / "papers" / "submission" / "DT-GSK-changes-marked.pdf"))
    ap.add_argument("--keep", action="store_true", help="keep the scratch build tree")
    args = ap.parse_args()

    if shutil.which("latexdiff-so") is None:
        sys.exit("latexdiff-so not on PATH. Plain 'latexdiff' is not a substitute here: "
                 "the MiKTeX shim needs Algorithm::Diff, which latexdiff-so bundles.")

    work = Path(tempfile.mkdtemp(prefix="dtgsk-marked-"))
    try:
        print("[1/4] exporting %s and %s" % (args.base, args.new))
        export(args.base, work / "old")
        export(args.new, work / "new")

        print("[2/4] latexdiff-so --flatten")
        diff = subprocess.run(
            ["latexdiff-so", "--flatten", "old/papers/main.tex", "new/papers/main.tex"],
            cwd=str(work), capture_output=True, text=True, errors="replace")
        if diff.returncode != 0 or not diff.stdout.strip():
            sys.stderr.write(diff.stderr[-3000:] + "\n")
            sys.exit("latexdiff-so produced no output")
        # The MDPI class wants the job named main; the flattened diff replaces it.
        target = work / "new" / "papers"
        (target / "main.tex").write_text(diff.stdout, encoding="utf-8")

        marks = {m: diff.stdout.count("\\" + m) for m in ("DIFaddbegin", "DIFdelbegin")}
        print("      %d added blocks, %d deleted blocks" % (marks["DIFaddbegin"], marks["DIFdelbegin"]))
        if not any(marks.values()):
            sys.exit("no change markup produced -- the two refs may be identical")

        print("[3/4] pdflatex x1, bibtex, pdflatex x2")
        import os
        env = dict(os.environ, SOURCE_DATE_EPOCH=EPOCH, FORCE_SOURCE_DATE="1")
        pdflatex = ["pdflatex", "-interaction=nonstopmode", "main.tex"]
        if run(pdflatex, target, "pdflatex pass 1", env):
            sys.exit("pass 1 failed. A missing .sty is the usual cause; see the docstring.")
        run(["bibtex", "main"], target, "bibtex", env)
        run(pdflatex, target, "pdflatex pass 2", env)
        run(pdflatex, target, "pdflatex pass 3", env)

        built = target / "main.pdf"
        if not built.is_file():
            sys.exit("no PDF produced")

        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(built, out)
        print("[4/4] %s" % out)
        print("      %d pages, %d bytes" % (page_count(out), out.stat().st_size))
        print("      diff: %s..%s" % (args.base, args.new))
        return 0
    finally:
        if args.keep:
            print("      scratch kept at %s" % work)
        else:
            shutil.rmtree(work, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main())
