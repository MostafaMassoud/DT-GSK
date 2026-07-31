# Copyright (c) 2026 Mostafa Masoud <moustafa.masoud@gmail.com>
"""Emit the CEC2013 six-comparator across-function Wilcoxon-Holm matrix (SE-046).

The manuscript states DT-GSK's CEC2013 standing but prints only the DT-GSK
versus GSK column (Table T14).  The full six-comparator pairwise matrix that
the standing actually rests on appeared in **neither** document -- a reader
could not check which of the six contrasts are significant and which are not.
The matrix is emitted here from the promoted release; **nothing is recomputed
and no optimizer is re-run**, the released
``wilcoxon_holm_cec2013_D{10,30,50}.csv`` files are read and typeset.

Columns are exactly those the released CSV supports: paired sample size after
the tie rule, the Wilcoxon statistic, raw and Holm-adjusted p, the matched-pairs
rank-biserial correlation, and the decision.  Win/tie/loss counts are **not**
emitted: no released CEC2013 artifact carries them, and they are not going to be
invented for a table.

Reads   papers/analysis/<release>/cec2013/wilcoxon_holm_cec2013_D{10,30,50}.csv
Writes  papers/tables/SA03.tex

Re-generate via::

    python papers/scripts/generate_cec2013_pairwise.py
"""
from __future__ import annotations

import csv
import hashlib
import json
import os
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
REL_ID = os.environ.get("GSK_REL_ID", "rel-2026-07-20-67d9345f9")
SRC_DIR = REPO / "papers" / "analysis" / REL_ID / "cec2013"
OUT = REPO / "papers" / "tables" / "SA03.tex"

DIMS = (10, 30, 50)
# P1 panel order, DT-GSK excluded (it is the reference of every contrast).
ORDER = ["gsk", "agsk", "apgsk", "fdb-agsk", "atmals-gsk", "egsk"]
DISPLAY = {
    "gsk": "GSK", "agsk": "AGSK", "apgsk": "APGSK",
    "fdb-agsk": "FDB-AGSK", "atmals-gsk": "ATMALS-GSK", "egsk": r"\egsk{}",
}
# Released `outcome` -> the decision symbol used throughout the paper.
DECISION = {"win": "$+$", "loss": "$-$", "tie": "$=$"}


def _load(dim: int) -> dict[str, dict[str, str]]:
    path = SRC_DIR / f"wilcoxon_holm_cec2013_D{dim}.csv"
    if not path.is_file():
        raise SystemExit(f"HARD FAIL: released source missing: {path}")
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        rows = [r for r in csv.DictReader(fh)
                if r.get("test_level") == "across_functions_funclevel"]
    by_comp = {r["comparator"]: r for r in rows}
    missing = [c for c in ORDER if c not in by_comp]
    if missing:
        raise SystemExit(
            f"HARD FAIL: D{dim} released matrix is missing comparators {missing}"
            f" -- the table is read from the release, never back-filled.")
    return by_comp


def _p(value: str) -> str:
    """Format a p-value; bound below 1e-4 rather than printing 0.0000."""
    x = float(value)
    return r"$<10^{-4}$" if x < 1e-4 else f"{x:.4f}"


def main() -> int:
    data = {d: _load(d) for d in DIMS}
    n_pairs = {r["n_pairs"] for d in DIMS for r in data[d].values()}
    if len(n_pairs) != 1:
        raise SystemExit(f"HARD FAIL: inconsistent n_pairs across cells: {n_pairs}")

    lines: list[str] = [r"\zebra", r"\begin{tabular}{l" + "rrrc" * len(DIMS) + "}",
                        r"\toprule"]
    head = " & ".join(rf"\multicolumn{{4}}{{c}}{{\textbf{{D{d}}}}}" for d in DIMS)
    lines.append(rf"\textbf{{Algorithm}} & {head} \\")
    sub = " & ".join([r"$p$ & $p_{\mathrm{Holm}}$ & $r$ & Dec."] * len(DIMS))
    lines.append(rf" & {sub} \\")
    lines.append(r"\midrule")

    for comp in ORDER:
        cells: list[str] = []
        for d in DIMS:
            r = data[d][comp]
            cells += [_p(r["p_raw"]), _p(r["p_holm"]),
                      f"{float(r['rank_biserial']):+.3f}",
                      DECISION[r["outcome"]]]
        lines.append(f"{DISPLAY[comp]} & " + " & ".join(cells) + r" \\")

    lines += [r"\bottomrule", r"\end{tabular}"]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    npairs = n_pairs.pop()
    print(f"wrote {OUT.relative_to(REPO)}  "
          f"({len(ORDER)} comparators x {len(DIMS)} dimensions, "
          f"n_pairs={npairs}, release {REL_ID})")

    # The DOCX path builds native w:tbl objects from these JSON sources, and
    # validate_cross_format_parity reads them to compare PDF against DOCX.  A
    # table added to the .tex without one here fails both.
    hdr = ["Algorithm"] + [f"{lab} (D{d})" for d in DIMS
                           for lab in ("p", "p_Holm", "r", "Dec.")]
    body = []
    for comp in ORDER:
        row = [DISPLAY[comp].replace(r"\egsk{}", "eGSK")]
        for d in DIMS:
            r = data[d][comp]
            pr, ph = float(r["p_raw"]), float(r["p_holm"])
            # Must mirror the .tex token-for-token: validate_cross_format_parity
            # derives each numeral in the LaTeX cell from this string, and
            # "$<10^{-4}$" yields the tokens 10 and -4.
            row += ["<10^-4" if pr < 1e-4 else f"{pr:.4f}",
                    "<10^-4" if ph < 1e-4 else f"{ph:.4f}",
                    f"{float(r['rank_biserial']):+.3f}",
                    {"win": "+", "loss": "-", "tie": "="}[r["outcome"]]]
        body.append(row)
    payload = {
        "table_id": "SA03",
        "manuscript_label": "tab:cec2013-pairwise",
        "caption_stub": ("Complete across-function Wilcoxon-Holm matrix on the CEC2013 "
                         "second comparison suite: DT-GSK against each of the six "
                         f"comparators at D in {{{', '.join(str(d) for d in DIMS)}}} "
                         f"(n = {npairs} paired per-function mean errors)."),
        "headers": [hdr],
        "rows": body,
        "notes": [f"read verbatim from the promoted release {REL_ID}; no value is "
                  "recomputed and no optimizer is re-run (SE-046)",
                  "win/tie/loss counts are not tabulated: no released CEC2013 "
                  "artifact records them"],
        "number_format": "as-is",
        "source": f"papers/analysis/{REL_ID}/cec2013/wilcoxon_holm_cec2013_D{{10,30,50}}.csv",
        "source_sha256": {f"D{d}": hashlib.sha256(
            (SRC_DIR / f"wilcoxon_holm_cec2013_D{d}.csv").read_bytes()).hexdigest()
            for d in DIMS},
    }
    wj = REPO / "papers" / "tables" / "word_sources" / "SA03.json"
    wj.parent.mkdir(parents=True, exist_ok=True)
    wj.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
                  encoding="utf-8")
    print(f"wrote {wj.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
