#!/usr/bin/env python3
"""Emit the GSK-family comparator parameter table (supplement).

Why this exists
---------------
``tab:panel`` states only "published constants, NP = 100 at every D". A reader
cannot check comparator fairness from that -- they would have to chase six
source papers. Both in-venue precedents publish their settings explicitly
(eGSK Table 3; ATMALS-GSK Table 3), so the omission is conspicuous. This table
closes it.

Provenance -- nothing here is hand-typed
----------------------------------------
Every value is READ from the shipped optimizer modules, not transcribed:

  * module-level constants (``KF_POOL``, ``SENIOR_P``, ``_KR`` ...) are
    imported and formatted directly;
  * runner-visible defaults (``_option_value(options, "kr", 0.9)``) are
    extracted from the module source by regex.

This matters because the frozen ``run_config.json`` records
``optimizer_options: {}`` for every comparator -- the campaign ran them on
their MODULE DEFAULTS, so the defaults *are* the settings of record, and the
evidence release does not restate them.

The script HARD-FAILS if a documented parameter can no longer be located,
rather than silently emitting a stale or partial row.

Writes deterministically:
    papers/generated/comparator_params.tex

It is written to ``papers/generated/`` and NOT to ``papers/tables/``:
both the DOCX builder and the parity gate treat ``tables/(T\d+|SA\d+)`` as
word_sources-backed GENERATED tables, and ``_flatten_inputs`` refuses to inline
anything under ``tables/``. A prose table placed there would demand a JSON it
cannot satisfy, and would be dropped from the DOCX. From ``generated/`` it is
inlined normally and checked as an authored table.

No ``word_sources`` JSON is emitted. That file would put the table under the
cross-format ``table_generated`` contract, which requires VALUE-only cells
(after stripping numerics a cell must leave no text residue). These cells are
configuration prose -- "NP = 100; Kf = 0.5; ..." -- so the labels would read as
residue and parity would fail by construction. Without the JSON the table is
verified as an AUTHORED table: a DOCX-vs-.tex text comparison, which is the
correct check for prose cells.

Usage::

    python papers/scripts/generate_comparator_params.py
"""
from __future__ import annotations

import importlib
import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PAPER_DIR = SCRIPT_DIR.parent
ROOT = PAPER_DIR.parent
SRC = ROOT / "src"
OPT_DIR = SRC / "gsk_family" / "optimizers"
TEX_PATH = PAPER_DIR / "generated" / "comparator_params.tex"

if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

# display name -> (module stem, citation key)
PANEL = [
    ("GSK", "gsk", "mohamed2020gaining"),
    ("AGSK", "agsk", "mohamed2020agsk"),
    ("APGSK", "apgsk", "apgsk2021"),
    ("FDB-AGSK", "fdb_agsk", "fdbagsk2023"),
    ("ATMALS-GSK", "atmals_gsk", "alfadli2025atmals"),
    ("eGSK", "egsk", "jawad2024egsk"),
]

# Parameters to surface per algorithm, in display order.
# Labels are PLAIN TEXT and UNDERSCORE-FREE on purpose:
#   * build_docx de-texes table cells, so a math label ($K_f$) would render
#     as 'K_f' in the DOCX and never match the word_sources JSON (parity);
#   * a bare '_' outside math is a LaTeX subscript and aborts the build,
#     so use 'NPinit', not 'NP_init'.
#   ("label", kind, key)  where kind is:
#     "opt"   -> _option_value(options, key, DEFAULT) default, read from source
#     "const" -> module-level constant, imported
#     "arange"-> np.arange(...) default of an _array_option, read from source
WANTED: dict[str, list[tuple[str, str, str]]] = {
    "gsk": [("NP", "opt", "np"), ("Kf", "opt", "kf"), ("Kr", "opt", "kr"),
            ("K", "opt", "k"), ("p", "opt", "p")],
    "agsk": [("NPinit", "opt", "np"), ("NPmin", "opt", "min_pop_size"),
             ("Kf pool", "const", "KF_POOL"), ("Kr pool", "const", "KR_POOL"),
             ("Kw init", "const", "INITIAL_KW"), ("p", "const", "SENIOR_P")],
    "apgsk": [("NPinit", "opt", "np"), ("NPmin", "opt", "min_pop_size"),
              ("Kf pool", "const", "KF_POOL"),
              ("Kf pool (neg.)", "const", "KF_POOL_NEGATIVE"),
              ("Kr pool", "const", "KR_POOL"), ("Kw init", "const", "INITIAL_KW"),
              ("p", "const", "SENIOR_P")],
    "fdb_agsk": [("NPinit", "opt", "np"), ("NPmin", "opt", "min_pop_size"),
                 ("FDB case", "opt", "fdb_case"), ("Kf pool", "const", "KF_POOL"),
                 ("Kr pool", "const", "KR_POOL"), ("p", "const", "SENIOR_P")],
    "atmals_gsk": [("NP", "opt", "np"), ("Kf pool", "arange", "kf_pool"),
                   ("Kr pool", "arange", "kr_pool"), ("K pool", "arange", "k_pool"),
                   ("p pool", "arange", "p_pool"),
                   ("PLS pool", "arange", "pls_pool")],
    "egsk": [("NP", "const", "_DEFAULT_NP"), ("Kf1, Kf2", "const", "_KF_INIT"),
             ("Kr", "const", "_KR"), ("K", "const", "_K"),
             ("p", "const", "_SENIOR_P"),
             ("late-stage frac.", "const", "_LATE_STAGE_FRAC"),
             ("IP budget frac.", "const", "_IP_FE_FRAC")],
}


def source_of(stem: str) -> str:
    p = OPT_DIR / f"{stem}.py"
    if not p.is_file():
        raise SystemExit(f"HARD FAIL - optimizer module missing: {p}")
    return p.read_text(encoding="utf-8")


def opt_default(src: str, key: str, stem: str) -> str:
    m = re.search(rf'_option_value\(\s*options,\s*"{re.escape(key)}"\s*,\s*([^),]+)\)', src)
    if not m:
        raise SystemExit(f"HARD FAIL - {stem}: no _option_value default for {key!r}")
    val = m.group(1).strip()
    if val == "np_default":          # AGSK-family alias for the "np" default
        return opt_default(src, "np", stem)
    if val.startswith("_"):          # resolves to a module constant
        c = re.search(rf"^{re.escape(val)}\s*=\s*([^\s#]+)", src, re.M)
        if c:
            return c.group(1).strip()
    return val


def arange_default(src: str, key: str, stem: str) -> str:
    m = re.search(
        rf'_array_option\(\s*options,\s*"{re.escape(key)}"\s*,\s*np\.arange\(([^)]+)\)',
        src)
    if not m:
        raise SystemExit(f"HARD FAIL - {stem}: no np.arange default for {key!r}")
    parts = [p.strip() for p in m.group(1).split(",")]
    if len(parts) != 3:
        raise SystemExit(f"HARD FAIL - {stem}: unexpected arange for {key!r}")
    import numpy as _np
    lo, hi, step = (float(p) for p in parts)
    grid = _np.arange(lo, hi, step)          # evaluate exactly as the optimizer does
    if grid.size == 0:
        raise SystemExit(f"HARD FAIL - {stem}: empty pool for {key!r}")
    # first:step:last -- the realised grid, not the epsilon-padded stop argument
    return f"{grid[0]:g}:{step:g}:{grid[-1]:g} ({grid.size} values)"


def fmt_const(value) -> str:
    try:
        import numpy as _np
        if isinstance(value, _np.ndarray):
            return "[" + ", ".join(f"{v:g}" for v in value.tolist()) + "]"
    except Exception:
        pass
    if isinstance(value, float):
        return f"{value:g}"
    return str(value)


def build_rows() -> list[list[str]]:
    rows: list[list[str]] = []
    for disp, stem, cite in PANEL:
        src = source_of(stem)
        mod = importlib.import_module(f"gsk_family.optimizers.{stem}")
        parts: list[str] = []
        for label, kind, key in WANTED[stem]:
            if kind == "opt":
                val = opt_default(src, key, stem)
            elif kind == "arange":
                val = arange_default(src, key, stem)
            else:
                if not hasattr(mod, key):
                    raise SystemExit(f"HARD FAIL - {stem}: constant {key!r} not found")
                val = fmt_const(getattr(mod, key))
            parts.append(f"{label} = {val}")
        # No \cite here: a \cite inside a generated tables/ file is never
        # flattened by build_docx, so the DOCX would silently lose the citation
        # and cross-format parity fails. The six references are cited in the
        # surrounding supplement prose instead, which IS processed.
        rows.append([disp, "; ".join(parts)])
    return rows


def write_tex(rows) -> None:
    lines = ["\\begin{tabular}{@{}l p{11.4cm}@{}}", "\\toprule",
             "\\textbf{Algorithm} & \\textbf{Parameter settings as run} \\\\",
             "\\midrule"]
    lines += [f"{a} & {p} \\\\" for a, p in rows]
    lines += ["\\bottomrule", "\\end{tabular}"]
    TEX_PATH.parent.mkdir(parents=True, exist_ok=True)
    TEX_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"  -> {TEX_PATH.name}  ({len(rows)} comparators)")


# Removed 2026-07-28: a write_json() emitting an SA05 word_sources payload, and
# the sha256_of() helper it alone used. It outlived its caller (the docstring
# explains why no JSON is emitted) and referenced a JSON_PATH constant that no
# longer existed, so calling it raised NameError instead of writing a table.


def main() -> None:
    rows = build_rows()
    if len(rows) != len(PANEL):
        raise SystemExit("HARD FAIL - comparator row count mismatch")
    write_tex(rows)
    # NOTE: deliberately no word_sources JSON -- see module docstring.
    for a, p in rows:
        print(f"     {a:12s} {p[:96]}")


if __name__ == "__main__":
    main()
