#!/usr/bin/env python3
"""Generate LaTeX table fragments from DT-GSK paper CSV results.

Reads the GSK-family paper table CSVs from the promoted benchmark evidence
(benchmarks/cec_reference_results/_paper_tables/) and writes .tex files to
papers/tables/ for direct \\input{} in the paper.

The scaffold-ablation supplement tables (SA01/SA02) and figure are NOT produced
here: they are emitted by ``papers/scripts/generate_ablation_exhibits.py`` from
the manifest-verified frozen copy under
``papers/build_prompt_phases/phase_12/ablation_results/``.  This script therefore
reads only the promoted benchmark evidence and never touches results/ staging.

Usage:
    python papers/scripts/generate_latex_tables.py
"""

from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path

# Resolve project root (two levels up from this script)
SCRIPT_DIR = Path(__file__).resolve().parent
PAPER_DIR = SCRIPT_DIR.parent
PROJECT_ROOT = PAPER_DIR.parent
# Consumer input = the PROMOTED, frozen benchmark evidence (single source of
# truth), not the results/ staging that producers write.  Repointed from
# results/paper_tables -> benchmarks/cec_reference_results/_paper_tables.
RESULTS_DIR = PROJECT_ROOT / "benchmarks" / "cec_reference_results" / "_paper_tables"
# Audit B.5: the previous hardcoded worktree fallback path pointed at a
# developer-specific Windows location that only existed on one machine and
# silently masked missing inputs when run elsewhere.  Require the inputs
# to live at the canonical path and fail loudly otherwise.
if not RESULTS_DIR.exists():
    raise FileNotFoundError(
        f"Paper table CSV directory not found: {RESULTS_DIR}. "
        "Run the experiment pipeline (see RUNBOOK.md) and promote it "
        "(scripts/promote_evidence.py) to populate "
        "benchmarks/cec_reference_results/_paper_tables/ before invoking "
        "this script."
    )
TABLES_DIR = PAPER_DIR / "tables"

# Phase 4 terminology glossary (binding): "eGSK" capitalization (CR-0003)
# and "FDB-AGSK" hyphenation.  The staging CSV headers/rows carry the
# machine tags EGSK / FDBAGSK; normalize them for display only.
_DISPLAY_ALG = {
    "EGSK": "eGSK",
    "FDBAGSK": "FDB-AGSK",
}


def _alg_label(name: str) -> str:
    """Return the paper-facing display label for an algorithm tag."""
    return _DISPLAY_ALG.get(name.strip(), name.strip())


def _fmt_sci(val_str: str) -> str:
    """Format a scientific-notation string for LaTeX."""
    val_str = val_str.strip()
    if not val_str or val_str == "nan" or val_str == "":
        return "---"
    try:
        val = float(val_str)
    except ValueError:
        return val_str
    if val == 0.0:
        return "\\bestval{0.00E+00}" if False else "0.00E+00"
    # Format in scientific notation
    s = f"{val:.2E}"
    return s


def _fmt_times(val_str: str) -> str:
    """Format a value as ``$m \\times 10^{e}$`` (the head-to-head display style,
    matching the standard CEC comparison-table look). Exact zeros render as
    ``0.00``; exponent-0 values render as the bare mantissa (e.g. ``8.20``)."""
    val_str = val_str.strip()
    if not val_str or val_str == "nan":
        return "---"
    try:
        val = float(val_str)
    except ValueError:
        return val_str
    if val == 0.0:
        return "0.00"
    m, e = f"{val:.2E}".split("E")
    e = int(e)
    return m if e == 0 else f"${m} \\times 10^{{{e}}}$"


def _bold_cell(cell: str) -> str:
    """Bold a formatted display cell. A math cell (``$...$``) must be bolded
    with ``\\boldsymbol`` INSIDE the math delimiters -- a text-mode ``\\textbf``
    wrapped around ``$...$`` does NOT bold the math (amsmath, loaded by the MDPI
    class, provides ``\\boldsymbol``). Plain numeric cells keep ``\\textbf``.
    The cross-format parity gate strips both forms (``detex`` handles
    ``\\boldsymbol``; ``build_docx._clean_tex_cell`` strips it too)."""
    if cell.startswith("$") and cell.endswith("$"):
        return "$\\boldsymbol{" + cell[1:-1] + "}$"
    return f"\\textbf{{{cell}}}"


def _bold_best_in_row(cells: list[str], indices: list[int],
                       lower_is_better: bool = True) -> list[str]:
    """Bold the best value among selected column indices."""
    best_idx = None
    best_val = None
    for idx in indices:
        try:
            v = float(cells[idx])
        except (ValueError, IndexError):
            continue
        if best_val is None or (lower_is_better and v < best_val) or \
                (not lower_is_better and v > best_val):
            best_val = v
            best_idx = idx
    result = list(cells)
    if best_idx is not None:
        result[best_idx] = f"\\bestval{{{result[best_idx]}}}"
    return result


def _read_csv(name: str) -> list[list[str]]:
    """Read a CSV file, return list of rows (each row is list of strings)."""
    path = RESULTS_DIR / name
    if not path.exists():
        print(f"  WARNING: {path} not found, skipping.")
        return []
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.reader(f))


def _write_tex(name: str, content: str) -> None:
    """Write a .tex file to papers/tables/.

    Prepends the preamble-defined ``\\zebra`` helper so each data table gets
    eye-friendly light alternate-row shading in the PDF (harmless to pandoc,
    which drops the unknown macro and keeps the native Word table)."""
    path = TABLES_DIR / name
    path.write_text("\\zebra\n" + content, encoding="utf-8")
    print(f"  -> {path.name}")


# =====================================================================
# Table generators
# =====================================================================

def gen_h2h_table(csv_name: str, tex_name: str) -> None:
    """Generate head-to-head table (T1--T5): Best/Median/Worst/Mean/SD.

    Source CSV columns (after Func): Best_GSK, Best_ISM, Median_GSK, Median_ISM,
    Mean_GSK, Mean_ISM, Worst_GSK, Worst_ISM, SD_GSK, SD_ISM (indices 0..9).
    Display order per review protocol: Best, Median, Worst, Mean, SD --- so
    Worst (source idx 6,7) is placed before Mean (source idx 4,5).
    """
    rows = _read_csv(csv_name)
    if not rows:
        return
    data = rows[1:]

    # SIDE-BY-SIDE algorithm groups (2026-07-24 author request: match the standard
    # CEC comparison-table look). Function | GSK {Best Median Worst Mean SD} |
    # DT-GSK (Proposed) {Best Median Worst Mean SD} -- 11 columns, the proposed
    # method flagged in its group header, values in E-notation (e.g. 6.40E+02,
    # the same format as the panel tables T07-T10 and the Wilcoxon/Friedman
    # tables -- author request 2026-07-24), best Mean per function in bold.
    # Source cell indices after Func: Best 0,1 | Median 2,3 |
    # Mean 4,5 | Worst 6,7 | SD 8,9 (GSK, DT-GSK). Display order Best/Median/Worst/
    # Mean/SD -> GSK idx [0,2,6,4,8], DT-GSK idx [1,3,7,5,9].
    gsk_idx = [0, 2, 6, 4, 8]
    dt_idx = [1, 3, 7, 5, 9]

    lines = ["\\begin{tabular}{l" + "r" * 10 + "}", "\\toprule"]
    lines.append("\\textbf{Function} & \\multicolumn{5}{c}{\\textbf{GSK}}"
                 " & \\multicolumn{5}{c}{\\textbf{DT-GSK (Proposed)}} \\\\")
    lines.append("\\cmidrule(lr){2-6} \\cmidrule(lr){7-11}")
    stat = " & \\textbf{Best} & \\textbf{Median} & \\textbf{Worst} & \\textbf{Mean} & \\textbf{SD}"
    lines.append("" + stat + stat + " \\\\")
    lines.append("\\midrule")
    for row in data:
        if len(row) < 11:
            continue
        body = row[1:]
        g_cells = [_fmt_sci(body[i]) for i in gsk_idx]
        d_cells = [_fmt_sci(body[i]) for i in dt_idx]
        try:                                    # bold the better (smaller) Mean
            if float(body[4]) <= float(body[5]):
                g_cells[3] = _bold_cell(g_cells[3])
            else:
                d_cells[3] = _bold_cell(d_cells[3])
        except ValueError:
            pass
        lines.append(f"{row[0]} & " + " & ".join(g_cells + d_cells) + " \\\\")
    lines += ["\\bottomrule", "\\end{tabular}"]
    _write_tex(tex_name, "\n".join(lines) + "\n")


def gen_comparison_table(csv_name: str, tex_name: str) -> None:
    """Generate multi-algorithm Mean±SD table (T7--T10, GSK-family)."""
    rows = _read_csv(csv_name)
    if not rows:
        return
    header = rows[0]
    data = rows[1:]

    # Extract algorithm names from header: Alg_Mean, Alg_SD pairs
    alg_names = []
    for i in range(1, len(header), 2):
        name = _alg_label(header[i].replace("_Mean", ""))
        alg_names.append(name)
    n_alg = len(alg_names)

    lines = []
    col_spec = "l" + "r" * n_alg
    lines.append(f"\\begin{{tabular}}{{{col_spec}}}")
    lines.append("\\toprule")
    alg_header = " & ".join(f"\\textbf{{{a}}}" for a in alg_names)
    lines.append(f"\\textbf{{Func.}} & {alg_header} \\\\")
    lines.append("\\midrule")

    for row in data:
        if len(row) < 1 + 2 * n_alg:
            continue
        func = row[0]
        # Build Mean±SD cells
        cells = []
        mean_vals = []
        for i in range(n_alg):
            mean_str = row[1 + 2 * i]
            sd_str = row[2 + 2 * i]
            mean_f = _fmt_sci(mean_str)
            sd_f = _fmt_sci(sd_str)
            cells.append(f"{mean_f}$\\pm${sd_f}")
            try:
                mean_vals.append(float(mean_str))
            except ValueError:
                mean_vals.append(float("inf"))

        # Bold best mean
        best_idx = min(range(n_alg), key=lambda k: mean_vals[k])
        cells[best_idx] = f"\\bestval{{{cells[best_idx]}}}"

        lines.append(f"{func} & " + " & ".join(cells) + " \\\\")

    lines.append("\\bottomrule")
    lines.append("\\end{tabular}")
    _write_tex(tex_name, "\n".join(lines) + "\n")


def gen_wilcoxon_summary_table(csv_name: str, tex_name: str) -> None:
    """Generate Wilcoxon summary table (T15, GSK-family per-dim).

    CSV column layout per dim (7 cols):
        p, p_holm, W (+), T (approx), L (-), A12, Dec.

    The ``Dec`` column uses a Holm-corrected decision at family size
    equal to the number of comparators in the CSV (6 GSK-family
    comparators), and ``A12`` is the Vargha--Delaney
    probability-of-superiority (DT-GSK vs comparator) on per-function
    mean errors (>0.5 favours DT-GSK).  R+ / R- were dropped from the
    published table to keep it within \\textwidth after adding p_holm
    and A12.
    """
    rows = _read_csv(csv_name)
    if not rows:
        return
    header = rows[0]
    data = rows[1:]

    # Columns: Algorithm, D10_p, D10_p_holm, D10_W, D10_T, D10_L,
    # D10_A12, D10_Dec, D30_..., etc.
    dims = []
    for col in header[1:]:
        dim_part = col.split("_")[0]
        if dim_part not in dims:
            dims.append(dim_part)

    def _fmt_dim_cells(row: list[str], dim_indices: list[int]) -> list[str]:
        """Format the 7 rendered cells for each requested dimension index.

        M-027: the CSV carries 8 columns per dimension (both effect sizes); the
        table renders 7. The PAIRED rank-biserial r is shown because it is the
        effect size aligned with the Wilcoxon signed-rank test in the same row;
        the unpaired A12 stays in the workbook as a labelled companion. Swapping
        rather than adding keeps the rendered width unchanged -- this table
        already gave up R+/R- to fit \\textwidth.
        """
        cells: list[str] = []
        for i in dim_indices:
            base = 1 + i * 8
            if base + 8 <= len(row):
                p_val = row[base]
                p_holm = row[base + 1]
                wins = row[base + 2]
                ties = row[base + 3]
                losses = row[base + 4]
                rb = row[base + 6]          # base + 5 is A12 (workbook only)
                dec = row[base + 7]
                # SAP: p-values below 1e-4 render as a bound, never as 0.0000.
                try:
                    pv = float(p_val)
                    p_f = "$<$0.0001" if 0.0 <= pv < 1e-4 else f"{pv:.4f}"
                except ValueError:
                    p_f = p_val
                try:
                    phv = float(p_holm)
                    ph_f = "$<$0.0001" if 0.0 <= phv < 1e-4 else f"{phv:.4f}"
                except ValueError:
                    ph_f = p_holm
                try:
                    # signed: r > 0 favours the proposed algorithm
                    rb_f = f"{float(rb):+.3f}"
                except ValueError:
                    rb_f = rb
                cells.extend([p_f, ph_f, wins, ties, losses, rb_f, dec])
            else:
                cells.extend(["---"] * 7)
        return cells

    def _emit_part(dim_indices: list[int]) -> list[str]:
        """Emit one portrait-width tabular covering the given dimensions."""
        part_dims = [dims[i] for i in dim_indices]
        lines = []
        # 7 rendered columns per dim: p, p_holm, +/=/-, r, Dec.
        lines.append("\\begin{tabular}{l" + "rrcccrc" * len(part_dims) + "}")
        lines.append("\\toprule")
        dim_header = " & ".join(
            f"\\multicolumn{{7}}{{c}}{{\\textbf{{{d}}}}}" for d in part_dims
        )
        lines.append(f"\\textbf{{Algorithm}} & {dim_header} \\\\")
        sub = " & ".join(
            "$p$ & $p_{\\mathrm{Holm}}$ & $+$ & $\\approx$ & $-$ & $r$ & Dec."
            for _ in part_dims
        )
        lines.append(f" & {sub} \\\\")
        lines.append("\\midrule")
        for row in data:
            alg = _alg_label(row[0])
            cells = _fmt_dim_cells(row, dim_indices)
            lines.append(f"{alg} & " + " & ".join(cells) + " \\\\")
        lines.append("\\bottomrule")
        lines.append("\\end{tabular}")
        return lines

    # Two stacked portrait parts (D10+D30 above, D50+D100 below) replace the
    # former single 29-column sideways tabular, so the table shares the
    # portrait/footnotesize/zebra layout of every other table in the paper.
    # One \input, one caption/label, one semantic word-source (T15.json).
    first = _emit_part(list(range(0, min(2, len(dims)))))
    lines = list(first)
    if len(dims) > 2:
        lines.append("")
        lines.append("\\vspace{6pt}")
        lines.append("")
        lines.append("\\zebra")
        lines.extend(_emit_part(list(range(2, len(dims)))))
    _write_tex(tex_name, "\n".join(lines) + "\n")


def gen_friedman_table(csv_name: str, tex_name: str) -> None:
    """Generate Friedman ranking table (T16, GSK-family per-dim)."""
    rows = _read_csv(csv_name)
    if not rows:
        return
    header = rows[0]
    data = rows[1:]

    # Columns: Algorithm, D10_MeanRank, D30_MeanRank, ..., Overall_MeanRank
    rank_cols = header[1:]

    lines = []
    n_cols = len(rank_cols)
    col_spec = "l" + "r" * n_cols
    lines.append(f"\\begin{{tabular}}{{{col_spec}}}")
    lines.append("\\toprule")
    # CR-009: compact dimension headers ("10" not "D100") so the D100 cell
    # never wraps in the DOCX column; the caption states the columns are
    # problem dimension D (with the overall mean).
    def _hdr(col: str) -> str:
        label = col.replace('_MeanRank', '').replace('_', ' ')
        m = re.fullmatch(r"D(\d+)", label.strip())
        return m.group(1) if m else label

    col_headers = " & ".join(f"\\textbf{{{_hdr(c)}}}" for c in rank_cols)
    lines.append(f"\\textbf{{Algorithm}} & {col_headers} \\\\")
    lines.append("\\midrule")

    # Find best (lowest) rank per column
    col_vals: list[list[float]] = [[] for _ in range(n_cols)]
    for row in data:
        for j in range(n_cols):
            try:
                col_vals[j].append(float(row[1 + j]))
            except (ValueError, IndexError):
                col_vals[j].append(float("inf"))
    col_bests = [min(vals) if vals else float("inf") for vals in col_vals]

    for row_idx, row in enumerate(data):
        alg = _alg_label(row[0])
        cells = []
        for j in range(n_cols):
            try:
                val = float(row[1 + j])
                cell = f"{val:.2f}"
                if val == col_bests[j]:
                    cell = f"\\bestval{{{cell}}}"
            except (ValueError, IndexError):
                cell = "---"
            cells.append(cell)
        lines.append(f"{alg} & " + " & ".join(cells) + " \\\\")

    lines.append("\\bottomrule")
    lines.append("\\end{tabular}")
    _write_tex(tex_name, "\n".join(lines) + "\n")


def gen_wilcoxon_cec2011(csv_name: str, tex_name: str) -> None:
    """Generate CEC2011 Wilcoxon table (T6) - simple summary format."""
    rows = _read_csv(csv_name)
    if not rows:
        return
    # Format: Metric, Value
    lines = []
    lines.append("\\begin{tabular}{lr}")
    lines.append("\\toprule")
    lines.append("\\textbf{Metric} & \\textbf{Value} \\\\")
    lines.append("\\midrule")
    for row in rows[1:]:
        if len(row) >= 2:
            metric = row[0].replace("_", " ").replace("(", "$").replace(")", "$")
            val = row[1]
            # SE-026: rank sums and win/tie/loss counts are integers; printing
            # them as 159.0000 misreads as a measured quantity. Integers render
            # as integers, non-integers keep four decimals (matching T14).
            try:
                fv = float(val)
                val_f = f"{int(round(fv))}" if fv == int(fv) else f"{fv:.4f}"
            except ValueError:
                val_f = val
            lines.append(f"{metric} & {val_f} \\\\")
    lines.append("\\bottomrule")
    lines.append("\\end{tabular}")
    _write_tex(tex_name, "\n".join(lines) + "\n")


def gen_wilcoxon_cec2013(csv_name: str, tex_name: str) -> None:
    """Generate the CEC2013 per-dim Wilcoxon summary table (T14).

    CSV schema: Metric, D10, D30, D50 (rows: R+/R-/p_value/Wins(+)/
    Ties(=)/Losses(-)/Decision).
    """
    rows = _read_csv(csv_name)
    if not rows:
        return
    header = rows[0]
    data = rows[1:]

    dim_cols = header[1:]
    n_dims = len(dim_cols)

    lines: list[str] = []
    lines.append("\\begin{tabular}{l" + "r" * n_dims + "}")
    lines.append("\\toprule")
    dim_header = " & ".join(f"\\textbf{{{d}}}" for d in dim_cols)
    lines.append(f"\\textbf{{Metric}} & {dim_header} \\\\")
    lines.append("\\midrule")

    def _fmt_metric(m: str) -> str:
        # Replace parentheses with math mode, escape underscore.
        m = m.strip()
        m = m.replace("R+", "$R^+$").replace("R-", "$R^-$")
        m = m.replace("p_value", "$p$-value")
        m = m.replace("p_holm", "$p_{\\mathrm{Holm}}$")
        m = m.replace("(+)", " (+)").replace("(=)", " ($\\approx$)")
        m = m.replace("(-)", " ($-$)")
        return m

    for row in data:
        if not row:
            continue
        metric = _fmt_metric(row[0])
        # Display policy (performance.tex / SAP Sec. 4): p-values below 1e-4
        # are reported as bounded, never as a raw scientific figure. SA03
        # already bounds the identical test; T14 must match (R3-20).
        is_p_row = row[0].strip() in ("p_value", "p_holm")
        cells: list[str] = []
        for val in row[1:]:
            val = val.strip()
            if not val or val == "N/A":
                cells.append("---")
                continue
            try:
                fv = float(val)
                if is_p_row and fv < 1e-4:
                    cells.append("$<10^{-4}$")
                # Keep decisions and integers unformatted when no decimals.
                elif val.replace(".", "", 1).isdigit() and "." not in val:
                    cells.append(val)
                elif abs(fv) < 1e-3 or abs(fv) >= 1e4:
                    cells.append(f"{fv:.2E}")
                else:
                    cells.append(f"{fv:.4f}".rstrip("0").rstrip("."))
            except ValueError:
                cells.append(val)
        lines.append(f"{metric} & " + " & ".join(cells) + " \\\\")

    lines.append("\\bottomrule")
    lines.append("\\end{tabular}")
    _write_tex(tex_name, "\n".join(lines) + "\n")


# =====================================================================
# Main
# =====================================================================

def main() -> None:
    # parse_args() gives --help/-h and rejects stray arguments; this script has
    # no options (scaffold-ablation exhibits are produced by
    # generate_ablation_exhibits.py, so there is nothing to toggle here).
    argparse.ArgumentParser(description=__doc__).parse_args()

    TABLES_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Reading CSVs from: {RESULTS_DIR}")
    print(f"Writing .tex to:   {TABLES_DIR}")
    print()

    # T1: CEC2011 head-to-head
    print("T1: CEC2011 head-to-head")
    gen_h2h_table("T1.csv", "T01.tex")

    # T2-T5: CEC2017 head-to-head D=10/30/50/100
    for i, d in enumerate([10, 30, 50, 100], start=2):
        print(f"T{i}: CEC2017 D={d} head-to-head")
        gen_h2h_table(f"T{i}.csv", f"T{i:02d}.tex")

    # T6: CEC2011 Wilcoxon
    print("T6: CEC2011 Wilcoxon")
    gen_wilcoxon_cec2011("T6.csv", "T06.tex")

    # T7-T10: GSK-family comparison D=10/30/50/100
    for i, d in enumerate([10, 30, 50, 100], start=7):
        print(f"T{i}: GSK-family D={d}")
        gen_comparison_table(f"T{i}.csv", f"T{i:02d}.tex")

    # T11-T13: CEC2013 head-to-head D=10/30/50 (extended study)
    for i, d in enumerate([10, 30, 50], start=11):
        print(f"T{i}: CEC2013 D={d} head-to-head (extended study)")
        gen_h2h_table(f"T{i}.csv", f"T{i:02d}.tex")

    # T14: CEC2013 per-dim Wilcoxon summary
    print("T14: CEC2013 Wilcoxon (extended study)")
    gen_wilcoxon_cec2013("T14.csv", "T14.tex")

    # T15: Wilcoxon GSK-family
    print("T15: Wilcoxon GSK-family")
    gen_wilcoxon_summary_table("T15.csv", "T15.tex")

    # T16: Friedman GSK-family
    print("T16: Friedman GSK-family")
    gen_friedman_table("T16.csv", "T16.tex")

    # Scaffold-ablation supplement tables (SA01/SA02) and figure are emitted by
    # generate_ablation_exhibits.py from the manifest-verified frozen copy under
    # papers/build_prompt_phases/phase_12/ablation_results/ -- not here.

    print("\nDone.")


if __name__ == "__main__":
    main()
