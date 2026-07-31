#!/usr/bin/env python3
# Copyright (c) 2026 Mostafa Masoud <moustafa.masoud@gmail.com>
"""Cross-check facts the submission states in more than one place (M-003, M-033).

WHY
---
Some facts are written down several times in different files: what the
supplement contains (main text back matter vs the supplement itself), and the
submission metadata (the Markdown cover letter vs the TeX one). Nothing links
those copies, so they agree only for as long as whoever edits one remembers the
others. Both tickets here are instances of exactly that decay:

  M-003  main text, conclusion and supplement disagreed on which studies the
         supplement contains.
  M-033  the Markdown and TeX cover letters were not the same document -- the
         Markdown still carried an unfilled "[submission date]" placeholder
         while the TeX was dated.

Both were fixed by hand. This gate exists so they cannot drift apart again.
It compares the copies against each other; it does not decide which is right.

CHECKS
------
1. SUPPLEMENT INVENTORY -- the section count claimed by main.tex's
   \\supplementary{} back matter must equal the sections that actually exist in
   supplementary.tex, and the claimed labels must be contiguous S1..SN.
2. COVER-LETTER PARITY -- title, date, corresponding author, GenAI tool and
   version, and the set of contribution-scope markers must match between
   cover_letter.md and cover_letter.tex.

Exit 0 = the copies agree.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PAPERS = ROOT / "papers"

MAIN = PAPERS / "main.tex"
SUPP = PAPERS / "supplementary.tex"
CL_MD = PAPERS / "cover_letter.md"
CL_TEX = PAPERS / "cover_letter.tex"

# Two independent concerns, deliberately not pooled.
#
#   DRIFT      copies of the same fact have diverged. This is the tickets'
#              subject and is always a defect in the tree.
#   READINESS  a field the AUTHOR must supply is still unfilled. Real and
#              blocking for submission, but not something tooling can resolve,
#              and pooling it with drift would leave the drift gate permanently
#              red -- which is how a gate stops being read.
#
# Exit 1 = drift, exit 2 = readiness only.
problems: list[str] = []
readiness: list[str] = []


def fail(msg: str) -> None:
    print(f"  FAIL  {msg}")
    problems.append(msg)


def needs_author(msg: str) -> None:
    print(f"  AUTHOR  {msg}")
    readiness.append(msg)


def ok(msg: str) -> None:
    print(f"  ok    {msg}")


def read(p: Path) -> str:
    return p.read_text(encoding="utf-8", errors="ignore")


def norm(s: str) -> str:
    """Comparison channel: markup stripped, dashes and spacing unified."""
    s = re.sub(r"\\(?:textbf|textit|emph|textsc|texttt|href)\{", "{", s)
    s = s.replace("\\&", "&").replace("\\_", "_").replace("\\%", "%")
    s = re.sub(r"[{}*_`]", "", s)
    s = s.replace("—", "-").replace("–", "-").replace("--", "-")
    s = re.sub(r"\\\\", " ", s)
    s = re.sub(r"\s+", " ", s)
    return s.strip().strip(".,;:").lower()


# --------------------------------------------------------------------------- #
def check_supplement_inventory() -> None:
    print("[1] supplement inventory: main-text claim vs the supplement itself")
    main = read(MAIN)
    supp = read(SUPP)

    actual = re.findall(r"(?m)^\\section\{([^}]*)\}", supp)
    n_actual = len(actual)

    m = re.search(r"\\supplementary\{", main)
    if not m:
        fail("main.tex has no \\supplementary{} back matter to check")
        return
    # take the balanced argument
    i, depth = m.end(), 1
    while i < len(main) and depth:
        depth += (main[i] == "{") - (main[i] == "}")
        i += 1
    claim = main[m.end():i - 1]

    labels = sorted({int(x) for x in re.findall(r"\(S(\d+)\)", claim)})
    if not labels:
        fail("main.tex \\supplementary{} names no (S<n>) sections")
        return

    if labels != list(range(1, len(labels) + 1)):
        fail(f"claimed supplement labels are not contiguous from S1: {labels}")
    else:
        ok(f"claimed labels contiguous S1..S{labels[-1]}")

    if labels[-1] != n_actual:
        fail(f"main.tex claims S1..S{labels[-1]} but supplementary.tex has "
             f"{n_actual} sections: {[t[:38] for t in actual]}")
    else:
        ok(f"claimed S1..S{labels[-1]} matches {n_actual} actual sections")

    # a range mention ("Sections S1--S6") must agree with the itemised labels
    for lo, hi in re.findall(r"S(\d+)\s*-+\s*S(\d+)", claim):
        if int(hi) != labels[-1] or int(lo) != labels[0]:
            fail(f"range 'S{lo}--S{hi}' disagrees with itemised labels "
                 f"S{labels[0]}..S{labels[-1]}")
        else:
            ok(f"range S{lo}--S{hi} agrees with the itemised labels")


# --------------------------------------------------------------------------- #
def _field(text: str, *patterns: str) -> str | None:
    for pat in patterns:
        m = re.search(pat, text, re.I)
        if m:
            return norm(m.group(1))
    return None


def check_cover_letters() -> None:
    print("\n[2] cover-letter parity: Markdown vs TeX")
    if not (CL_MD.is_file() and CL_TEX.is_file()):
        print("  SKIP  one or both cover letters absent")
        return
    md, tx = read(CL_MD), read(CL_TEX)

    fields = {
        "title": (
            [r"\*\*Manuscript:\*\*\s*\*([^*\n]+)\*"],
            [r"\\textbf\{Manuscript:\}\s*\\textit\{([^}]*)\}"],
        ),
        "date": (
            [r"\*\*Date:\*\*\s*([^\n]+)"],
            [r"(?m)^\s*(\d{1,2}\s+\w+\s+\d{4})\s*\\?\\?\s*$"],
        ),
        # The TeX writes the address inside \href{mailto:..}{..}, so the capture
        # must run to end of line; stopping at the first backslash compares a
        # name against an email and reports a difference that is not there.
        "corresponding": (
            [r"\*\*Corresponding author:\*\*\s*([^\n]+)"],
            [r"\\textbf\{Corresponding author:\}\s*([^\n]+)"],
        ),
    }
    for name, (md_pats, tx_pats) in fields.items():
        a, b = _field(md, *md_pats), _field(tx, *tx_pats)
        if a is None or b is None:
            fail(f"{name}: not found in {'markdown' if a is None else 'tex'}")
            continue
        # the corresponding-author line legitimately differs in shape (email
        # only vs name + email); require containment rather than equality
        agree = (a == b) or (name == "corresponding" and
                             (a in b or b in a or
                              bool(set(re.findall(r"[\w.]+@[\w.]+", a)) &
                                   set(re.findall(r"[\w.]+@[\w.]+", b)))))
        if agree:
            ok(f"{name} matches: {a[:60]}")
        else:
            fail(f"{name} differs:\n          md : {a[:80]}\n          tex: {b[:80]}")

    # Unfilled author fields must never ship, but only the author can fill them
    # (the suggested-reviewer block says so in its own comment).
    for label, text in (("markdown", md), ("tex", tx)):
        for m in re.findall(r"\[[^\]\n]*(?:author to fill|TBD|TODO|placeholder)"
                            r"[^\]\n]*\]", text, re.I):
            needs_author(f"{label} cover letter: unfilled field {m[:70]}")

    # GenAI tool + version, pinned by policy disclosure
    gen_md = re.search(r"\(([^)]*Claude[^)]*)\)", md)
    gen_tx = re.search(r"\(([^)]*Claude[^)]*)\)", tx)
    if gen_md and gen_tx:
        if norm(gen_md.group(1)) == norm(gen_tx.group(1)):
            ok(f"GenAI disclosure matches: {gen_md.group(1)}")
        else:
            fail(f"GenAI disclosure differs: md={gen_md.group(1)!r} "
                 f"tex={gen_tx.group(1)!r}")
    else:
        fail("GenAI disclosure missing from one or both cover letters")

    # contribution-scope markers
    c_md = set(re.findall(r"\bC([1-9])\b", md))
    c_tx = set(re.findall(r"\bC([1-9])\b", tx))
    if c_md == c_tx:
        ok(f"contribution-scope markers match: {sorted('C' + c for c in c_md)}")
    else:
        fail(f"contribution-scope markers differ: md={sorted(c_md)} tex={sorted(c_tx)}")


def main() -> int:
    argparse.ArgumentParser(description=__doc__.splitlines()[0],
                            formatter_class=argparse.RawDescriptionHelpFormatter
                            ).parse_args()
    print("[doc-consistency] cross-checking multiply-stated facts\n")
    check_supplement_inventory()
    check_cover_letters()

    if problems:
        print(f"\n[doc-consistency] DRIFT: {len(problems)} copy/copies disagree")
        for p in problems:
            print(f"  - {p.splitlines()[0]}")
        return 1

    print("\n[doc-consistency] OK - all cross-stated facts agree (no drift)")
    if readiness:
        print(f"\n[doc-consistency] {len(readiness)} field(s) await the AUTHOR "
              "-- blocking for submission, not resolvable by tooling:")
        for r in readiness:
            print(f"  - {r}")
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
