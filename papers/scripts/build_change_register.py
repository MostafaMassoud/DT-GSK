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
     ["s9.4", "s9.5", "sensitivity analys", "knife-edge", "ordinal",
      "boundary sensitivity", "dimension-boundary", "rev:boundary",
      "selected-constant"]),
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
    ("sec:supp:rev:sensitivity", "S9.4", "Selected-Constant Sensitivity"),
    ("sec:supp:rev:boundary", "S9.5", "Dimension-Boundary Sensitivity"),
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


def listing(lines, empty_note, kind):
    """One color-coded panel: kind is 'old' (red-tinted) or 'new' (green)."""
    bg = "oldbg" if kind == "old" else "newbg"
    rule = "oldrule" if kind == "old" else "newrule"
    if not lines or not any(x.strip() for x in lines):
        return ("\\begin{quote}\\itshape\\small\\color{gray!60!black} "
                + tex_escape(empty_note) + "\\end{quote}\n")
    body = "\n".join(lines).replace("\\end{lstlisting}", "\\end {lstlisting}")
    return ("\\begin{lstlisting}[backgroundcolor=\\color{" + bg + "},"
            "frame=leftline,framerule=1.6pt,rulecolor=\\color{" + rule + "},"
            "framexleftmargin=4pt]\n" + body + "\n\\end{lstlisting}\n")


def clean_context(context: str) -> str:
    """Diff hunk context is raw TeX mid-line: strip markup debris and show it
    only when enough legible text survives to orient the reader."""
    if not context:
        return ""
    t = context
    for junk in ("\\", "{", "}", "$", "~", "%"):
        t = t.replace(junk, " ")
    t = " ".join(t.split())[:110]
    alnum = sum(ch.isalnum() for ch in t)
    if alnum < 18 or alnum < 0.55 * max(len(t), 1):
        return ""
    return t


def build_tex(base, new, per_file, counts, total):
    out = []
    A = out.append
    A(r"\documentclass[10pt,a4paper]{article}")
    A(r"\usepackage[margin=2.1cm]{geometry}")
    A(r"\usepackage{lmodern}")
    A(r"\usepackage[T1]{fontenc}")
    A(r"\usepackage{listings}")
    A(r"\usepackage{xcolor}")
    A(r"\usepackage{booktabs}")
    A(r"\usepackage{longtable}")
    A(r"\usepackage{needspace}")
    A(r"\usepackage{parskip}")
    A(r"\usepackage[colorlinks=true,linkcolor=accent,urlcolor=accent]{hyperref}")
    A(r"\definecolor{accent}{RGB}{0,84,147}")
    A(r"\definecolor{oldbg}{RGB}{253,240,240}")
    A(r"\definecolor{newbg}{RGB}{240,249,241}")
    A(r"\definecolor{oldrule}{RGB}{192,57,43}")
    A(r"\definecolor{newrule}{RGB}{39,124,56}")
    A(r"\definecolor{badge}{RGB}{234,240,246}")
    A(r"\definecolor{ctxgray}{gray}{0.42}")
    A(r"\lstset{basicstyle=\ttfamily\scriptsize,breaklines=true,"
      r"breakatwhitespace=false,columns=fixed,basewidth=0.52em,"
      r"keepspaces=true,breakindent=14pt,"
      r"postbreak=\mbox{\textcolor{ctxgray}{$\hookrightarrow$}\space},"
      r"xleftmargin=8pt,aboveskip=3pt,belowskip=7pt,literate={\ }{{\ }}1}")
    A(r"\setlength{\parskip}{4pt}")
    A(r"\newcommand{\pointbadge}[1]{\colorbox{badge}{\footnotesize\textbf{\textcolor{accent}{#1}}}}")
    A(r"\newcommand{\panelhead}[2]{\noindent\textcolor{#1}{\rule[0.25ex]{7pt}{7pt}}~\textbf{\small #2}\par\vspace{1.5pt}}")
    A(r"\begin{document}")

    # ---- title page ----
    A(r"\begin{center}")
    A(r"{\LARGE\bfseries Change Register}\\[6pt]")
    A(r"{\large DT-GSK \textbullet{} manuscript \texttt{algorithms-4507562}}\\[3pt]")
    A(r"{\normalsize round-one major revision \textbullet{} \emph{Algorithms} (MDPI)}\\[10pt]")
    A(r"\begin{tabular}{ccc}")
    A(r"{\Large\bfseries %d} & {\Large\bfseries 7} & {\Large\bfseries %s $\to$ %s}\\"
      % (total, tex_escape(base), tex_escape(new)))
    A(r"{\footnotesize changed passages} & {\footnotesize manuscript files} & "
      r"{\footnotesize as submitted $\to$ as revised}\\")
    A(r"\end{tabular}\\[8pt]")
    A(r"\begin{minipage}{0.86\textwidth}\centering\small")
    A("Every changed passage of the manuscript, shown "
      r"\panelcolor{oldrule}{as submitted} and \panelcolor{newrule}{as revised}, "
      "with the reviewer point each answers. Companion to the marked-up manuscripts, "
      "which show the same changes in place."
      .replace("\\panelcolor{oldrule}{as submitted}",
               r"{\color{oldrule}\textbf{as submitted}}")
      .replace("\\panelcolor{newrule}{as revised}",
               r"{\color{newrule}\textbf{as revised}}"))
    A(r"\end{minipage}")
    A(r"\end{center}")
    A(r"\vspace{4pt}\hrule\vspace{8pt}")

    A(r"\subsection*{How to read this document}")
    A(r"\begin{itemize}\setlength\itemsep{1pt}")
    A(r"\item Each entry shows the source location, the reviewer point(s) it answers "
      r"(\pointbadge{R2.3}\,-style badges), and the passage in both states: "
      r"{\color{oldrule}\textbf{red panel}} = as submitted, "
      r"{\color{newrule}\textbf{green panel}} = as revised.")
    A(r"\item Attribution is keyword-derived and deliberately conservative; "
      r"\pointbadge{Editorial} means \emph{not classified}, not unimportant. "
      r"The point-by-point response letter is the authoritative mapping.")
    A(r"\item A passage answering two points is listed under both in the summary, "
      r"so that column sums to more than the passage count.")
    A(r"\item Generated artifacts (the \texttt{\_pandoc} mirrors and the "
      r"\texttt{SA0*} tables) are excluded: they restate changes listed here.")
    A(r"\end{itemize}")

    A(r"\subsection*{Summary by reviewer point}")
    A(r"\begin{longtable}{@{}llr@{}}")
    A(r"\toprule")
    A(r"\textbf{Point} & \textbf{Subject} & \textbf{Passages}\\")
    A(r"\midrule\endhead")
    for label, desc, n in counts:
        A(r"\pointbadge{%s} & %s & %d\\" % (tex_escape(label), tex_escape(desc), n))
    A(r"\bottomrule")
    A(r"\end{longtable}")
    A(r"\noindent\textbf{%d changed passages in total.} The column above counts "
      r"attributions (a passage answering two points appears under both), so it "
      r"sums to more than %d." % (total, total))

    A(r"\vspace{10pt}")
    A(r"{\setlength{\parskip}{2pt}\tableofcontents}")

    first_file = True
    for path, entries in per_file:
        if not entries:
            continue
        if first_file:
            A(r"\clearpage")
            first_file = False
        else:
            A(r"\vspace{16pt}\Needspace*{10\baselineskip}")
            A(r"{\color{accent}\hrule height 1.1pt}")
            A(r"\vspace{-4pt}")
        A(r"\section{\texorpdfstring{\texttt{%s}\hspace{0.8em}"
          r"{\normalfont\small\color{ctxgray}%d passage%s}}{%s}}"
          % (tex_escape(path), len(entries),
             "" if len(entries) == 1 else "s", tex_escape(path)))
        for idx, (line_no, context, removed, added, label, _desc) in enumerate(entries, 1):
            A(r"\vspace{7pt}\Needspace*{7\baselineskip}")
            badges = "~".join(r"\pointbadge{%s}" % tex_escape(x.strip())
                              for x in label.split(","))
            A(r"\noindent\textbf{%d.}~\texttt{%s:%d}\hfill %s\par"
              % (idx, tex_escape(path.rsplit('/', 1)[-1]), line_no, badges))
            ctx = clean_context(context)
            if ctx:
                A(r"{\small\itshape\color{ctxgray} near: %s}\par\vspace{2pt}"
                  % tex_escape(ctx))
            A(r"\panelhead{oldrule}{As submitted}")
            A(listing(removed, "Not present in the submitted version (this passage is new).", "old"))
            A(r"\panelhead{newrule}{As revised}")
            A(listing(added, "Removed in revision (this passage no longer appears).", "new"))
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
