#!/usr/bin/env python3
"""Phase 9 evidence-binding number verification (Appendix D.6).

    python papers/scripts/validate_evidence_bindings.py
    python papers/scripts/validate_evidence_bindings.py --sample 30
    python papers/scripts/validate_evidence_bindings.py --csv <out.csv>

Every ``% BIND:``-carrying statement in the FROZEN canonical LaTeX sources
binds rendered numbers to promoted evidence.  This validator extracts every
numeric token from the visible text those BIND comments annotate and checks
the token appears identically in BOTH rendered formats:

* main-paper BINDs  (``main.tex`` + ``sections/*.tex``)
      -> ``papers/DT-GSK.pdf``      (PyMuPDF text extraction)
      -> ``papers/DT-GSK.docx``     (w:t + m:t document text)
* supplement BINDs (``supplementary.tex``)
      -> ``papers/supplementary.pdf`` / ``papers/supplementary.docx``

Context rule: an inline BIND annotates its own code line plus up to two
preceding visible lines of the same paragraph; a standalone BIND comment
line annotates up to six preceding visible lines (stop at a blank line /
environment boundary).  ``\\cite``/``\\ref``/``\\label`` arguments and the
BIND comment itself never contribute tokens.

Token kinds: scientific (1.23E+04), powers of ten (4.2 x 10^-2, 10^-8),
decimals (2.29), comma-grouped integers (150,000), plain integers.
Verification runs on whitespace-squashed, ligature/uni-minus-normalized
channels of each format.

A deterministic sample (default 30, spread over both documents, preferring
the most distinctive tokens) is reported in detail for the manual
word_validation_report.md record.  Full results ->
``papers/build_prompt_phases/phase_09/evidence_binding_verification.csv``.

Exit 0 when every extracted number is found in both formats, else 2.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import re
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS_DIR))

from _validate_common import (  # noqa: E402
    DOC_PAIRS, PAPERS, docx_document, docx_full_text, number_channel,
    pdf_raw_text, squash,
)

CSV_OUT = (PAPERS / "build_prompt_phases" / "phase_09" /
           "evidence_binding_verification.csv")

BIND_RE = re.compile(r"%\s*BIND\b[:]?\s*(.*)$")

STOP_LINE = re.compile(
    r"^\s*(\\(sub)*section|\\paragraph|\\begin\{(figure|table|equation|"
    r"algorithm)|\\end\{(figure|table|equation|algorithm)|\\caption)")


def find_comment_split(line: str) -> tuple[str, str]:
    """(code, comment) at the first unescaped %."""
    i = 0
    while i < len(line):
        if line[i] == "\\":
            i += 2
            continue
        if line[i] == "%":
            return line[:i], line[i:]
        i += 1
    return line, ""


def main_source_files() -> list[Path]:
    files = [PAPERS / "main.tex"]
    txt = (PAPERS / "main.tex").read_text(encoding="utf-8")
    for m in re.finditer(r"\\(?:input|include)\{([^}]+)\}", txt):
        rel = m.group(1).strip().replace("\\", "/")
        if rel.startswith("tables/"):
            continue
        p = PAPERS / rel
        if p.suffix.lower() != ".tex":
            p = p.with_suffix(".tex")
        if p.is_file():
            files.append(p)
    return files


def collect_bind_contexts(path: Path) -> list[dict]:
    """[{file, line, bind_ids, context}] for every % BIND in the file."""
    out = []
    lines = path.read_text(encoding="utf-8").splitlines()
    codes = [find_comment_split(ln)[0] for ln in lines]
    for idx, ln in enumerate(lines):
        code, comment = find_comment_split(ln)
        m = BIND_RE.search(comment)
        if not m:
            continue
        inline = bool(code.strip())
        budget = 2 if inline else 6
        ctx = [code] if inline else []
        j = idx - 1
        while j >= 0 and budget > 0:
            cj = codes[j]
            if not cj.strip():
                break                      # paragraph boundary
            if STOP_LINE.match(cj):
                ctx.insert(0, cj)          # keep boundary line, then stop
                break
            ctx.insert(0, cj)
            budget -= 1
            j -= 1
        out.append({"file": str(path.relative_to(PAPERS)),
                    "line": idx + 1,
                    "bind_ids": m.group(1).strip()[:80],
                    "context": "\n".join(ctx)})
    return out


# ---------------------------------------------------------------------------
# numeric token extraction
# ---------------------------------------------------------------------------

_STRIP_ARGS = re.compile(
    r"\\(?:cite|ref|eqref|label|input|include|url|href|texttt|mbox)"
    r"\{[^}]*\}")

TOKEN_PATTERNS = [
    # mantissa x 10^{exp}
    ("pow10", re.compile(
        r"(\d+(?:\.\d+)?)\s*\\(?:times|cdot)\s*10\^\{(-?\d+)\}")),
    # bare 10^{exp}
    ("pow10", re.compile(r"()10\^\{(-?\d+)\}")),
    ("sci", re.compile(r"(?<![\w.])(\d+(?:\.\d+)?[eE][+-]?\d+)(?![\w.])")),
    ("group_int", re.compile(r"(?<![\w.])(\d{1,3}(?:,\d{3})+)(?![\w.])")),
    ("decimal", re.compile(r"(?<![\w.])(\d+\.\d+)(?![\w.])")),
    ("int", re.compile(r"(?<![\w.,])(\d+)(?![\w.,])")),
]


def extract_tokens(context: str) -> list[tuple[str, str]]:
    """[(kind, token)] -- pow10 tokens encoded as 'mant^exp'."""
    text = _STRIP_ARGS.sub(" ", context)
    text = text.replace("{,}", ",")
    text = re.sub(r"\\%", "%", text)
    tokens: list[tuple[str, str]] = []
    consumed: list[tuple[int, int]] = []

    def free(a: int, b: int) -> bool:
        return all(b <= s or a >= e for s, e in consumed)

    for kind, pat in TOKEN_PATTERNS:
        for m in pat.finditer(text):
            if not free(m.start(), m.end()):
                continue
            consumed.append((m.start(), m.end()))
            if kind == "pow10":
                mant, exp = m.group(1), m.group(2)
                tokens.append((kind, f"{mant}^{exp}"))
            else:
                tok = m.group(1)
                if kind == "int" and len(tok) > 1 and tok[0] == "0":
                    continue        # zero-padded ids, not display numbers
                tokens.append((kind, tok))
    return tokens


# ---------------------------------------------------------------------------
# verification against rendered channels
# ---------------------------------------------------------------------------

def token_found(kind: str, token: str, spaced: str, squashed: str) -> bool:
    """The SPACED channel keeps word/cell separators (strict boundaries);
    the SQUASHED channel catches values wrapped across spans, with slightly
    relaxed boundaries (adjacent table cells concatenate there)."""
    if kind == "pow10":
        mant, exp = token.split("^")
        exp_pat = re.escape(exp.replace("−", "-"))
        if mant:
            pat = (re.escape(mant) + r"[x·*]?10" + exp_pat +
                   r"(?![0-9])")
            spaced_pat = (re.escape(mant) + r"\s*[x·*×]?\s*10\s*" +
                          exp_pat + r"(?![0-9])")
        else:
            pat = r"(?<![0-9.])10" + exp_pat + r"(?![0-9])"
            spaced_pat = r"(?<![0-9.])10\s*" + exp_pat + r"(?![0-9])"
        # pow10 checks BOTH channels, like every kind below it. The squashed
        # channel alone is not sufficient: adjacent table cells concatenate
        # there, so a neighbouring cell's leading digit lands directly on the
        # exponent and the trailing-digit guard rejects an otherwise exact
        # match ("1.8x10-11" followed by "4.3x10-10" squashes to
        # "1.8x10-114.3x10-10"). The spaced channel keeps the cell separator,
        # so the same guard is safe there and still blocks a truncated
        # exponent (10^-11 must not match inside 10^-110). Whitespace
        # tolerance is needed because pdf extraction emits "1.8 x 10-11"
        # where the docx emits "1.8x10-11".
        return (re.search(spaced_pat, spaced) is not None
                or re.search(pat, squashed) is not None)
    if kind == "sci":
        pat = re.escape(token) + r"(?![0-9])"
        return (re.search(pat, spaced, re.IGNORECASE) is not None
                or re.search(pat, squashed, re.IGNORECASE) is not None)
    if kind == "group_int":
        for hay in (spaced, squashed):
            if re.search(re.escape(token) + r"(?![0-9])", hay):
                return True
            # some renderings drop the thousands separator
            if re.search(re.escape(token.replace(",", "")) + r"(?![0-9])",
                         hay):
                return True
        return False
    # decimal / int
    strict = r"(?<![0-9.])" + re.escape(token) + r"(?![0-9])"
    if re.search(strict, spaced):
        return True
    relaxed = (r"(?<![0-9])(?<![0-9]\.)" + re.escape(token) + r"(?![0-9])")
    return re.search(relaxed, squashed) is not None


def stable_rank(row: dict) -> tuple:
    score = {"pow10": 5, "sci": 4, "decimal": 3, "group_int": 3}.get(
        row["kind"], 2 if len(row["token"]) >= 3 else 1)
    h = hashlib.sha1(
        f"{row['file']}:{row['line']}:{row['token']}".encode()).hexdigest()
    return (-score, h)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--sample", type=int, default=30)
    ap.add_argument("--csv", default=str(CSV_OUT))
    args = ap.parse_args(argv)

    channels = {}
    for kind, spec in DOC_PAIRS.items():
        pdf_txt = pdf_raw_text(spec["pdf"])
        docx_txt = docx_full_text(docx_document(spec["docx"]))
        channels[kind] = {
            "pdf": (number_channel(pdf_txt), squash(pdf_txt)),
            "docx": (number_channel(docx_txt), squash(docx_txt)),
        }

    sources = {"main": main_source_files(),
               "supplementary": [PAPERS / "supplementary.tex"]}

    rows: list[dict] = []
    n_binds = 0
    for doc_kind, files in sources.items():
        for f in files:
            for ctx in collect_bind_contexts(f):
                n_binds += 1
                for tkind, tok in extract_tokens(ctx["context"]):
                    in_pdf = token_found(tkind, tok,
                                         *channels[doc_kind]["pdf"])
                    in_docx = token_found(tkind, tok,
                                          *channels[doc_kind]["docx"])
                    rows.append({
                        "doc": doc_kind, "file": ctx["file"],
                        "line": ctx["line"], "bind_ids": ctx["bind_ids"],
                        "kind": tkind, "token": tok,
                        "found_pdf": "yes" if in_pdf else "NO",
                        "found_docx": "yes" if in_docx else "NO",
                        "status": "PASS" if (in_pdf and in_docx) else "FAIL",
                        "sampled": "",
                    })

    # deterministic detail sample: round-robin over token kinds (then most
    # distinctive within each kind) so all number classes are represented
    seen: set[tuple[str, str]] = set()
    ranked_by_kind: dict[str, list[dict]] = {}
    for row in sorted(rows, key=stable_rank):
        key = (row["file"], row["token"])
        if key in seen:
            continue
        seen.add(key)
        ranked_by_kind.setdefault(row["kind"], []).append(row)
    sample: list[dict] = []
    kind_cycle = ["pow10", "sci", "decimal", "group_int", "int"]
    while len(sample) < args.sample and any(ranked_by_kind.values()):
        for k in kind_cycle:
            if ranked_by_kind.get(k):
                sample.append(ranked_by_kind[k].pop(0))
                if len(sample) >= args.sample:
                    break
    for row in sample:
        row["sampled"] = "yes"

    out = Path(args.csv)
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=[
            "doc", "file", "line", "bind_ids", "kind", "token",
            "found_pdf", "found_docx", "status", "sampled"])
        w.writeheader()
        w.writerows(rows)

    fails = [r for r in rows if r["status"] == "FAIL"]
    print(f"BIND comments scanned : {n_binds}")
    print(f"numeric tokens checked: {len(rows)}")
    print(f"found in both formats : {len(rows) - len(fails)}")
    print(f"FAIL                  : {len(fails)}")
    print(f"full record -> {out}")
    print(f"\nDeterministic {len(sample)}-token verification sample:")
    for r in sample:
        print(f"  [{r['status']}] {r['doc']:13s} {r['file']}:{r['line']:<4} "
              f"{r['kind']:9s} {r['token']:>14s}  pdf={r['found_pdf']:3s} "
              f"docx={r['found_docx']:3s}  ({r['bind_ids'][:40]})")
    for r in fails[:20]:
        print(f"  FAIL {r['file']}:{r['line']} {r['kind']} {r['token']!r} "
              f"pdf={r['found_pdf']} docx={r['found_docx']}")
    return 0 if not fails else 2


if __name__ == "__main__":
    sys.exit(main())
