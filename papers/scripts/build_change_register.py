"""Build the change register: every changed manuscript passage, as submitted
against as revised, with the reviewer point it answers.

This is the companion to the marked-up manuscript built by
``build_change_marked_pdf.py``. The marked-up PDF is what MDPI check-list item
(II) literally asks for -- changes shown in place. The register is what makes
those changes *navigable*: grouped by file, each with the reviewer point it
answers, so an editor can read it beside the point-by-point response letter.

Scope is the manuscript a reviewer actually reads: ``main.tex``, the five
section files, and ``supplementary.tex``. Deliberately excluded:

* ``*_pandoc.tex`` -- generated mirrors for the DOCX build. Including them
  would list every change twice.
* ``papers/tables/SA0*.tex`` -- generated from the analysis bundle.
* ``cover_letter.tex`` and ``DT-GSK-plain-summary.tex`` -- not the manuscript.

That scope is exactly the "75 hunks across 7 files" the submission kit cites.

Reviewer-point attribution is keyword-based and deliberately conservative: a
hunk is attributed only when the keyword evidence is unambiguous, and
everything else is labelled "Editorial / consistency" rather than guessed at.
The document says so on its own front page, because a register that goes to an
editor must not overstate how it was built.

    python papers/scripts/build_change_register.py
    python papers/scripts/build_change_register.py --base v2.13 --new v2.21
"""
from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EPOCH = "1783468800"
DEFAULT_BASE = "v2.13"

# The manuscript a reviewer reads, in reading order.
FILES = [
    "papers/main.tex",
    "papers/sections/introduction.tex",
    "papers/sections/related_work.tex",
    "papers/sections/proposed_algorithm.tex",
    "papers/sections/performance.tex",
    "papers/sections/conclusions.tex",
    "papers/supplementary.tex",
]

# Attribution rules. Each entry is (label, description, case-insensitive
# substrings); a hunk matches when any substring appears in the text it added or
# removed. A passage may answer more than one point and is attributed to all it
# matches: forcing one label made the result depend on rule order, which sent
# the aggregate-rank disclosure at main.tex:163 to "Editorial" because an
# earlier rule claimed it first.
RULES = [
    ("R2.3", "Eigenframe isolation -- C1 claimed basis-neutrally",
     ["eigenframe", "eigenbasis", "basis-neutral", "coordinate axes", "s9.1",
      "learned basis", "three-arm"]),
    # S9.2 is Matched Population Size and S9.3 is Tiered Versus Tier-Constant.
    # These two keys were transposed in the first version of this file, which
    # attributed each experiment's passages to the other reviewer's point.
    ("R2.1", "Tiered versus uniform -- C2 narrowed to where tiering was shown",
     ["s9.3", "mis-specified", "misspecified", "uniform parameter", "tiering is",
      "tier-constant", "low-dimension parameter set"]),
    ("R1.3 / R2.2", "Population rule NP = 5D against the comparators' NP = 100",
     ["np = 100", "np=100", "population rule", "matched population", "s9.2",
      "matched np", "$np$"]),
    ("R2.7", "Sensitivity of thresholds and constants",
     ["s9.4", "sensitivity analys", "knife-edge", "ordinal"]),
    ("R1.2", "Retitle -- adaptive control renamed",
     ["adaptive control", "adaptive configuration", "configuration-and-budget",
      "control-and-budget"]),
    ("R1.4", "One omnibus convention throughout",
     ["iman", "imandavenport", "omnibus", "chi-squared", "$\\chi^2$"]),
    ("R2.4", "ISM positioned as a specified negative result",
     ["interaction-structure memory", "ism "]),
    ("R2.5", "Aggregate rank labelled descriptive, not superiority",
     ["overall superiority", "aggregate rank", "rank aggregate", "non-separab",
      "separate it from", "descriptive"]),
    ("R2.6", "Panel is GSK-family only; comparative claims family-scoped",
     ["family-scoped", "external algorithm", "gsk family", "family only"]),
    ("R1.1", "Abstract sentence rewritten for grammar",
     ["adapt control to a single", "adapt control at one"]),
]
UNCLASSIFIED = ("Editorial", "Consistency, wording, or cross-reference upkeep")


def sh(cmd, **kw):
    return subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True,
                          errors="replace", **kw)


S9_ORDER = [
    ("sec:supp:rev:basis", "S9.1", "Refinement Basis"),
    ("sec:supp:rev:np", "S9.2", "Matched Population Size"),
    ("sec:supp:rev:tiering", "S9.3", "Tiered Versus Tier-Constant"),
    ("sec:supp:rev:sensitivity", "S9.4", "Parameter Sensitivity"),
]


def verify_s9_mapping(ref):
    """Abort if the S9 subsection order at ``ref`` contradicts the S9.x
    numbers RULES assumes. An S9.2/S9.3 transposition shipped once in this
    script's rules; the mapping is a checkable fact, so check it instead of
    trusting memory."""
    res = sh(["git", "show", ref + ":papers/supplementary.tex"])
    if res.returncode != 0:
        sys.exit("S9 mapping check: cannot read papers/supplementary.tex at %s" % ref)
    # anchor on the DEFINITION site: a bare find() would hit the first
    # cross-reference to the label, which scrambles the order test
    pos = [(res.stdout.find("\label{" + label + "}"), label, num, title)
           for label, num, title in S9_ORDER]
    missing = [l for p, l, _n, _t in pos if p < 0]
    if missing:
        sys.exit("S9 mapping check: label(s) %s absent at %s -- RULES may be stale" % (missing, ref))
    if [p for p, *_ in pos] != sorted(p for p, *_ in pos):
        sys.exit("S9 mapping check: subsection order at %s contradicts the S9.x "
                 "numbers in RULES -- fix RULES before building" % ref)
    for p, label, num, title in pos:
        window = res.stdout[max(0, p - 200):p]
        if title.lower() not in window.lower():
            sys.exit("S9 mapping check: %s (%s) does not carry the title %r at %s"
                     % (label, num, title, ref))
    print("  S9 mapping verified at %s: S9.1=basis, S9.2=matched NP, "
          "S9.3=tiering, S9.4=sensitivity" % ref)


def hunks_for(base: str, new: str, path: str):
    """Yield (old_start, context, removed_lines, added_lines) per hunk."""
    res = sh(["git", "diff", "-U0", base, new, "--", path])
    if res.returncode != 0:
        sys.exit("git diff failed for %s: %s" % (path, res.stderr[:400]))
    header = re.compile(r"^@@ -(\d+)(?:,\d+)? \+\d+(?:,\d+)? @@ ?(.*)$")
    cur = None
    for line in res.stdout.split("\n"):
        m = header.match(line)
        if m:
            if cur:
                yield cur
            cur = (int(m.group(1)), m.group(2).strip(), [], [])
            continue
        if cur is None or line.startswith("\\"):
            continue
        if line.startswith("-") and not line.startswith("---"):
            cur[2].append(line[1:])
        elif line.startswith("+") and not line.startswith("+++"):
            cur[3].append(line[1:])
    if cur:
        yield cur


def classify(removed, added):
    """Every point a passage matches, not just the first. Returns [(label, desc)]."""
    blob = ("\n".join(removed) + "\n" + "\n".join(added)).lower()
    hits = [(label, desc) for label, desc, keys in RULES
            if any(k in blob for k in keys)]
    return hits or [UNCLASSIFIED]


def listing(lines, empty_note):
    """Render source lines through listings, which needs no escaping."""
    if not lines or not any(s.strip() for s in lines):
        return "\\textit{%s}\n\n" % empty_note
    body = "\n".join(lines)
    # listings delimits on the literal end tag only; nothing else can break it.
    body = body.replace("\\end{lstlisting}", "\\end {lstlisting}")
    return "\\begin{lstlisting}\n%s\n\\end{lstlisting}\n" % body


def build_tex(base, new, per_file, counts, total):
    out = []
    A = out.append
    A(r"\documentclass[10pt,a4paper]{article}")
    A(r"\usepackage[margin=2cm]{geometry}")
    A(r"\usepackage{listings}")
    A(r"\usepackage{xcolor}")
    A(r"\usepackage{longtable}")
    A(r"\usepackage{parskip}")
    A(r"\usepackage[hidelinks]{hyperref}")
    A(r"\definecolor{oldbg}{rgb}{0.97,0.93,0.93}")
    A(r"\definecolor{newbg}{rgb}{0.92,0.96,0.92}")
    A(r"\lstset{basicstyle=\ttfamily\scriptsize,breaklines=true,"
      r"breakatwhitespace=false,columns=fullflexible,keepspaces=true,"
      r"xleftmargin=6pt,frame=none,literate={\ }{{\ }}1}")
    A(r"\setlength{\parskip}{4pt}")
    A(r"\title{\vspace{-1.5cm}Change register\\[2pt]"
      r"\large DT-GSK, manuscript \texttt{algorithms-4507562}}")
    A(r"\author{Round-one major revision, \emph{Algorithms} (MDPI)}")
    A(r"\date{Diff of \texttt{%s} (as submitted) against \texttt{%s} (as revised)}"
      % (tex_escape(base), tex_escape(new)))
    A(r"\begin{document}")
    A(r"\maketitle")
    A(r"\thispagestyle{empty}")

    A(r"\section*{What this document is}")
    A("This register lists every changed passage of the manuscript, each given "
      "as it was submitted and as it now reads. It is the companion to the "
      "marked-up manuscript, which shows the same changes in place; this "
      "document exists to make them navigable next to the point-by-point "
      "response letter.")

    A(r"\section*{Scope}")
    A("The manuscript a reviewer reads: \\texttt{main.tex}, the five section "
      "files, and \\texttt{supplementary.tex}. Generated artefacts are "
      "excluded --- the \\texttt{\\_pandoc} mirrors used to build the Word "
      "twins, and the \\texttt{SA0*} table files generated from the analysis "
      "bundle --- because they restate changes already listed here. The cover "
      "letter and the plain-language summary are separate documents and are "
      "not manuscript text.")

    A(r"\section*{How the reviewer column was derived, and its limits}")
    A("Attribution is keyword-based and deliberately conservative. A passage "
      "is attributed to a reviewer point only where the evidence is "
      "unambiguous. Everything else is labelled \\textbf{Editorial}, which "
      "means \\emph{not classified}, not \\emph{unimportant}: consistency "
      "edits following a substantive change are labelled that way, and so is "
      "any passage whose wording did not make its own provenance explicit. "
      "The authoritative account of what each reviewer point asked and how it "
      "was answered is the point-by-point response letter, not this column. "
      "A passage that answers two points is listed under both.")

    A(r"\section*{Summary}")
    A(r"\begin{longtable}{@{}llr@{}}")
    A(r"\textbf{Point} & \textbf{Subject} & \textbf{Passages}\\ \hline")
    A(r"\endhead")
    for label, desc, n in counts:
        A(r"%s & %s & %d\\" % (tex_escape(label), tex_escape(desc), n))
    A(r"\end{longtable}")
    A(r"\noindent\textbf{%d changed passages in total.} The column above sums to "
      r"%d because a passage that answers two points is counted under both; it "
      r"is a count of attributions, not of passages, and the two do not agree."
      % (total, sum(c[2] for c in counts)))

    for path, entries in per_file:
        if not entries:
            continue
        A(r"\clearpage")
        A(r"\section*{\texttt{%s}}" % tex_escape(path))
        A("%d changed passage%s." % (len(entries), "" if len(entries) == 1 else "s"))
        for idx, (line_no, context, removed, added, label, _desc) in enumerate(entries, 1):
            A(r"\subsection*{%d. Line %d \hfill \normalfont\small Answers: \textbf{%s}}"
              % (idx, line_no, tex_escape(label)))
            if context:
                A(r"{\small\itshape Context: %s}" % tex_escape(context[:150]))
            A(r"\noindent\textbf{As submitted}")
            A(listing(removed, "Not present in the submitted version (this passage is new)."))
            A(r"\noindent\textbf{As revised}")
            A(listing(added, "Removed in revision (this passage no longer appears)."))
    A(r"\end{document}")
    return "\n".join(out) + "\n"


def tex_escape(s: str) -> str:
    for a, b in (("\\", r"\textbackslash{}"), ("&", r"\&"), ("%", r"\%"),
                 ("$", r"\$"), ("#", r"\#"), ("_", r"\_"), ("{", r"\{"),
                 ("}", r"\}"), ("~", r"\textasciitilde{}"),
                 ("^", r"\textasciicircum{}")):
        s = s.replace(a, b)
    return s


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--base", default=DEFAULT_BASE)
    ap.add_argument("--new", default="HEAD")
    ap.add_argument("--out", default=str(ROOT / "papers" / "submission" / "DT-GSK-change-register.pdf"))
    ap.add_argument("--keep", action="store_true")
    args = ap.parse_args()

    verify_s9_mapping(args.new)

    per_file, tally = [], {}
    total = 0
    for path in FILES:
        entries = []
        for line_no, context, removed, added in hunks_for(args.base, args.new, path):
            hits = classify(removed, added)
            label = ", ".join(h[0] for h in hits)
            entries.append((line_no, context, removed, added, label, hits[0][1]))
            for lab, desc in hits:
                tally[lab] = (desc, tally.get(lab, (desc, 0))[1] + 1)
            total += 1
        per_file.append((path, entries))
        print("  %-42s %2d passages" % (path, len(entries)))
    print("  %-42s %2d total" % ("", total))
    if not total:
        sys.exit("no changes between %s and %s -- nothing to register" % (args.base, args.new))

    order = [r[0] for r in RULES] + [UNCLASSIFIED[0]]
    counts = [(k, tally[k][0], tally[k][1]) for k in order if k in tally]

    work = Path(tempfile.mkdtemp(prefix="dtgsk-register-"))
    try:
        tex = work / "register.tex"
        tex.write_text(build_tex(args.base, args.new, per_file, counts, total), encoding="utf-8")
        env = dict(os.environ, SOURCE_DATE_EPOCH=EPOCH, FORCE_SOURCE_DATE="1")
        cmd = ["pdflatex", "-interaction=nonstopmode", "register.tex"]
        for i in (1, 2):
            r = subprocess.run(cmd, cwd=str(work), env=env,
                               capture_output=True, text=True, errors="replace")
            if not (work / "register.pdf").is_file():
                sys.stderr.write(r.stdout[-3000:] + "\n")
                sys.exit("pdflatex pass %d produced no PDF" % i)
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(work / "register.pdf", out)
        pages = len(re.findall(rb"/Type\s*/Page[^s]", out.read_bytes()))
        print("  -> %s (%d pages, %d bytes)" % (out, pages, out.stat().st_size))
        return 0
    finally:
        if args.keep:
            print("     scratch kept at %s" % work)
        else:
            shutil.rmtree(work, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main())
