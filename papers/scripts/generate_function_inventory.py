#!/usr/bin/env python3
"""Emit the CEC2017 scored-function inventory (supplement table SA04).

A reader-orientation table: for each of the 29 SCORED CEC2017 functions, its
class in the suite taxonomy and its known optimal value. The supplement's
function-class analysis (S6.6) reasons about these classes, but until now the
paper never listed which function belongs to which class -- this closes that
gap (eGSK Table 2 / ATMALS-GSK carry the equivalent inventory).

Provenance: the taxonomy and the optimum rule come from the benchmark suite
itself (``benchmarks/cec_suite_python/cec2017/functions.py``), not from a
secondary source:

  * classes  -- Unimodal F1-F3, Simple multimodal F4-F10, Hybrid F11-F20,
                Composition F21-F30 (the CEC2017 technical-report taxonomy).
  * optimum  -- f*(F_i) = i x 100, checked against the suite's own
                ``cec2017_fopt`` when that entry point is importable.

F2 is EXCLUDED under the adopted protocol (documented instability), uniformly
in every panel cell, so it is absent from the 29 rows and is stated in the
caption instead.

Writes, deterministically (fixed order, no timestamps):
    papers/tables/SA04.tex
    papers/tables/word_sources/SA04.json

Usage::

    python papers/scripts/generate_function_inventory.py
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PAPER_DIR = SCRIPT_DIR.parent
ROOT = PAPER_DIR.parent
TEX_PATH = PAPER_DIR / "tables" / "SA04.tex"
JSON_PATH = PAPER_DIR / "tables" / "word_sources" / "SA04.json"
SUITE_DEF = ROOT / "benchmarks" / "cec_suite_python" / "cec2017" / "functions.py"

EXCLUDED = {2}          # F2: documented instability, excluded by protocol
N_FUNCS = 30

# CEC2017 technical-report taxonomy (also how the suite modules are split:
# simple.py F1-F10, hybrid.py F11-F20, composition.py F21-F30 -- the report
# further separates the unimodal head F1-F3 from the multimodal tail F4-F10).
CLASSES = [
    (1, 3, "Unimodal"),
    (4, 10, "Simple multimodal"),
    (11, 20, "Hybrid"),
    (21, 30, "Composition"),
]


def function_class(fid: int) -> str:
    for lo, hi, name in CLASSES:
        if lo <= fid <= hi:
            return name
    raise ValueError(f"F{fid} outside the CEC2017 range")


def suite_fopt(fid: int) -> float:
    """Optimum for F<fid>, preferring the suite's own entry point."""
    documented = fid * 100.0
    try:
        sys.path.insert(0, str(ROOT / "benchmarks" / "cec_suite_python"))
        from cec2017.functions import cec2017_fopt  # type: ignore
    except Exception:
        return documented
    got = float(cec2017_fopt(fid))
    if abs(got - documented) > 1e-9:
        raise SystemExit(
            f"HARD FAIL - suite cec2017_fopt(F{fid})={got} disagrees with the "
            f"documented i x 100 rule ({documented}); inspect before shipping")
    return got


def sha256_of(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else ""


def build_rows() -> list[list[str]]:
    rows: list[list[str]] = []
    for fid in range(1, N_FUNCS + 1):
        if fid in EXCLUDED:
            continue
        rows.append([f"F{fid}", function_class(fid), f"{int(suite_fopt(fid))}"])
    return rows


def write_tex(rows: list[list[str]]) -> None:
    lines = ["\\zebra",
             "\\begin{tabular}{llr}",
             "\\toprule",
             "\\textbf{Function} & \\textbf{Class} & \\textbf{$f^{*}$} \\\\",
             "\\midrule"]
    lines += [f"{f} & {cls} & {opt} \\\\" for f, cls, opt in rows]
    lines += ["\\bottomrule", "\\end{tabular}"]
    TEX_PATH.parent.mkdir(parents=True, exist_ok=True)
    TEX_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"  -> {TEX_PATH.name}  ({len(rows)} functions)")


def write_json(rows: list[list[str]]) -> None:
    payload = {
        "table_id": "SA04",
        "manuscript_label": "Table SA04",
        "caption_stub": ("CEC2017 scored-function inventory: class in the suite "
                         "taxonomy and known optimal value f* for each of the 29 "
                         "scored functions (F2 excluded by protocol)."),
        "headers": [["Function", "Class", "f*"]],
        "rows": rows,
        "notes": [
            "taxonomy and optimum rule read from the benchmark suite definition "
            "(benchmarks/cec_suite_python/cec2017/functions.py), not a secondary source",
            "f*(F_i) = i x 100; cross-checked against the suite's cec2017_fopt "
            "entry point when importable",
            "F2 is excluded under the adopted CEC2017 protocol (documented "
            "instability), uniformly in every panel cell",
        ],
        "number_format": "as-is",
        "source": SUITE_DEF.relative_to(ROOT).as_posix(),
        "source_sha256": sha256_of(SUITE_DEF),
    }
    JSON_PATH.parent.mkdir(parents=True, exist_ok=True)
    JSON_PATH.write_text(json.dumps(payload, indent=1, ensure_ascii=False) + "\n",
                         encoding="utf-8")
    print(f"  -> {JSON_PATH.name}")


def main() -> None:
    if not SUITE_DEF.is_file():
        raise SystemExit(f"HARD FAIL - suite definition missing: {SUITE_DEF}")
    rows = build_rows()
    if len(rows) != N_FUNCS - len(EXCLUDED):
        raise SystemExit(
            f"HARD FAIL - expected {N_FUNCS - len(EXCLUDED)} scored functions, "
            f"built {len(rows)}")
    write_tex(rows)
    write_json(rows)


if __name__ == "__main__":
    main()
