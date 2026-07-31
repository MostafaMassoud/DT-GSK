# Copyright (c) 2026 Mostafa Masoud <moustafa.masoud@gmail.com>
"""Phase 7 task 12 -- value-level exhibit validation.

Compares EVERY numeric cell of the regenerated ``papers/tables/T01.tex``
.. ``T16.tex`` and ``T16_bca.tex`` against the authoritative CSVs
(the promoted benchmark export
``benchmarks/cec_reference_results/_paper_tables/`` -- itself exported
exclusively from the frozen Phase 6 bundle
``papers/analysis/rel-2026-07-10-262fc16c9/`` per its ``provenance.json``,
then promoted from results/paper_tables/ staging -- and, for T16_bca, the
bundle descriptive stats directly).  Tolerance is display rounding ONLY:
the validator
re-applies the generators' exact formatting rules to the CSV values and
requires string equality with the .tex cells.

Figure data is sample-validated:

* Nemenyi CD diagrams (all 4 dims): numeric text extracted from the
  published PDFs (mean-rank value labels, CD scale-bar label, N) is
  compared against the bundle ``friedman_ranks_cec2017_D<dim>.csv`` /
  ``nemenyi_cd_cec2017_D<dim>.csv``; omnibus gate re-checked.
* Rank charts: ``rank_trend_cec2017.csv`` cross-checked value-by-value
  against the per-dimension friedman CSVs and staging ``T16.csv``;
  numeric bar labels extracted from ``cec2011_ranks.pdf`` and
  ``friedman_gsk_family.pdf`` compared to their sources.
* Convergence (6 sampled panels >= the required 3): per-checkpoint mean
  series endpoints recomputed INDEPENDENTLY (plain csv + arithmetic,
  no reuse of the plotting loader's numpy path) from
  ``benchmarks/cec_reference_results/cec2017/<alg>/gen_logs/`` and
  compared (a) exactly against the plotting loader
  (``_convergence_common.load_mean_curve``) and (b) against the bundle
  ``convergence_checkpoints_cec2017_D<dim>.csv`` at display precision.

T16_bca is additionally re-derived end-to-end (same BASE_SEED BCa
scheme) and the regenerated LaTeX must equal the published file
byte-for-byte.

Output: ``exhibit_validation_report.md`` next to this script.  Every
mismatch is listed; a missing input is a hard failure, never a silent
skip.  Exit code 0 only when zero unexplained mismatches remain.

Usage::

    python papers/build_prompt_phases/phase_07/validate_exhibits.py
"""
from __future__ import annotations

import csv
import math
import re
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJECT_ROOT = HERE.parents[2]
PAPERS = PROJECT_ROOT / "papers"
TABLES = PAPERS / "tables"
# Consumer input = the PROMOTED, frozen benchmark evidence (single source of
# truth), not the results/ staging that producers write.  Repointed from
# results/paper_tables -> benchmarks/cec_reference_results/_paper_tables.
STAGING = PROJECT_ROOT / "benchmarks" / "cec_reference_results" / "_paper_tables"
RELEASE_ID = os.environ.get("GSK_REL_ID", "rel-2026-07-16-78f075cb0")
BUNDLE = PAPERS / "analysis" / RELEASE_ID
REFERENCE_ROOT = PROJECT_ROOT / "benchmarks" / "cec_reference_results"

sys.path.insert(0, str(PAPERS / "scripts"))

REPORT = HERE / "exhibit_validation_report.md"

mismatches: list[str] = []
sections: list[str] = []
cells_checked = 0


def fail(msg: str) -> None:
    mismatches.append(msg)


def require(path: Path) -> Path:
    if not path.is_file():
        raise SystemExit(f"HARD FAIL: required input missing: {path}")
    return path


# ---------------------------------------------------------------------------
# Generator display-formatting rules (replicated verbatim from
# papers/scripts/generate_latex_tables.py so the tolerance is exactly
# "display rounding").
# ---------------------------------------------------------------------------
def fmt_sci(val_str: str) -> str:
    val_str = val_str.strip()
    if not val_str or val_str == "nan":
        return "---"
    try:
        val = float(val_str)
    except ValueError:
        return val_str
    if val == 0.0:
        return "0.00E+00"
    return f"{val:.2E}"


def strip_best(cell: str) -> tuple[str, bool]:
    cell = cell.strip()
    m = re.fullmatch(r"\\bestval\{(.*)\}", cell)
    if m:
        return m.group(1), True
    return cell, False


def read_csv_rows(path: Path) -> list[list[str]]:
    with require(path).open(newline="", encoding="utf-8") as f:
        return list(csv.reader(f))


def tex_data_rows(path: Path) -> list[list[str]]:
    """Data rows (between \\midrule and \\bottomrule) of a tabular .tex."""
    lines = require(path).read_text(encoding="utf-8").splitlines()
    try:
        i0 = lines.index("\\midrule") + 1
        i1 = lines.index("\\bottomrule")
    except ValueError:
        raise SystemExit(f"HARD FAIL: cannot locate tabular body in {path}")
    rows = []
    for ln in lines[i0:i1]:
        ln = ln.strip()
        if not ln:
            continue
        if ln.endswith("\\\\"):
            ln = ln[:-2].strip()
        rows.append([c.strip() for c in ln.split(" & ")])
    return rows


# ---------------------------------------------------------------------------
# T1--T5, T11--T13: head-to-head tables
# ---------------------------------------------------------------------------
DISPLAY_PERM = [0, 1, 2, 3, 6, 7, 4, 5, 8, 9]


def check_h2h(csv_name: str, tex_name: str) -> int:
    global cells_checked
    n = 0
    data = read_csv_rows(STAGING / csv_name)[1:]
    trows = tex_data_rows(TABLES / tex_name)
    csv_rows = [r for r in data if len(r) >= 11]
    if len(trows) != len(csv_rows):
        fail(f"{tex_name}: row count {len(trows)} != CSV data rows "
             f"{len(csv_rows)}")
        return 0
    for crow, trow in zip(csv_rows, trows):
        func = crow[0]
        if trow[0] != func:
            fail(f"{tex_name} {func}: row label '{trow[0]}' != '{func}'")
        src = [fmt_sci(c) for c in crow[1:11]]
        expected = [src[i] for i in DISPLAY_PERM]
        # replicate _bold_best_in_row on display indices [6, 7]
        best_idx, best_val = None, None
        for idx in (6, 7):
            try:
                v = float(expected[idx])
            except ValueError:
                continue
            if best_val is None or v < best_val:
                best_val, best_idx = v, idx
        got = trow[1:]
        if len(got) != 10:
            fail(f"{tex_name} {func}: {len(got)} cells (expected 10)")
            continue
        for j, cell in enumerate(got):
            plain, bolded = strip_best(cell)
            n += 1
            if plain != expected[j]:
                fail(f"{tex_name} {func} col{j}: tex '{plain}' != "
                     f"csv-formatted '{expected[j]}'")
            if bolded != (j == best_idx):
                fail(f"{tex_name} {func} col{j}: bestval marker "
                     f"{'present' if bolded else 'absent'}, expected "
                     f"{'present' if j == best_idx else 'absent'}")
    cells_checked += n
    return n


# ---------------------------------------------------------------------------
# T6: CEC2011 Wilcoxon summary
# ---------------------------------------------------------------------------
def check_t6() -> int:
    global cells_checked
    n = 0
    rows = read_csv_rows(STAGING / "T6.csv")[1:]
    trows = tex_data_rows(TABLES / "T06.tex")
    exp = []
    for r in rows:
        if len(r) < 2:
            continue
        metric = r[0].replace("_", " ").replace("(", "$").replace(")", "$")
        try:
            v = f"{float(r[1]):.4f}"
        except ValueError:
            v = r[1]
        exp.append((metric, v))
    if len(trows) != len(exp):
        fail(f"T06.tex: row count {len(trows)} != {len(exp)}")
        return 0
    for (em, ev), trow in zip(exp, trows):
        n += 1
        if trow[0] != em or trow[1] != ev:
            fail(f"T06.tex '{em}': tex {trow} != expected ({em!r}, {ev!r})")
    cells_checked += n
    return n


# ---------------------------------------------------------------------------
# T7--T10: GSK-family Mean+-SD tables
# ---------------------------------------------------------------------------
def check_family(csv_name: str, tex_name: str) -> int:
    global cells_checked
    n = 0
    rows = read_csv_rows(STAGING / csv_name)
    header, data = rows[0], rows[1:]
    n_alg = (len(header) - 1) // 2
    trows = tex_data_rows(TABLES / tex_name)
    csv_rows = [r for r in data if len(r) >= 1 + 2 * n_alg]
    if len(trows) != len(csv_rows):
        fail(f"{tex_name}: row count {len(trows)} != {len(csv_rows)}")
        return 0
    for crow, trow in zip(csv_rows, trows):
        func = crow[0]
        if trow[0] != func:
            fail(f"{tex_name} {func}: row label '{trow[0]}'")
        mean_vals = []
        expected = []
        for i in range(n_alg):
            m_raw, s_raw = crow[1 + 2 * i], crow[2 + 2 * i]
            expected.append(f"{fmt_sci(m_raw)}$\\pm${fmt_sci(s_raw)}")
            try:
                mean_vals.append(float(m_raw))
            except ValueError:
                mean_vals.append(float("inf"))
        best_idx = min(range(n_alg), key=lambda k: mean_vals[k])
        got = trow[1:]
        if len(got) != n_alg:
            fail(f"{tex_name} {func}: {len(got)} cells (expected {n_alg})")
            continue
        for j, cell in enumerate(got):
            plain, bolded = strip_best(cell)
            n += 2  # mean and sd both checked
            if plain != expected[j]:
                fail(f"{tex_name} {func} col{j}: '{plain}' != "
                     f"'{expected[j]}'")
            if bolded != (j == best_idx):
                fail(f"{tex_name} {func} col{j}: bestval marker wrong")
    cells_checked += n
    return n


# ---------------------------------------------------------------------------
# T14: CEC2013 per-dim Wilcoxon summary
# ---------------------------------------------------------------------------
def _fmt_t14(val: str) -> str:
    val = val.strip()
    if not val or val == "N/A":
        return "---"
    try:
        fv = float(val)
    except ValueError:
        return val
    if val.replace(".", "", 1).isdigit() and "." not in val:
        return val
    if abs(fv) < 1e-3 or abs(fv) >= 1e4:
        return f"{fv:.2E}"
    return f"{fv:.4f}".rstrip("0").rstrip(".")


def _fmt_t14_metric(m: str) -> str:
    # Must mirror gen_wilcoxon_cec2013._fmt_metric in
    # papers/scripts/generate_latex_tables.py exactly.
    m = m.strip()
    m = m.replace("R+", "$R^+$").replace("R-", "$R^-$")
    m = m.replace("p_value", "$p$-value")
    m = m.replace("p_holm", "$p_{\\text{Holm}}$")
    m = m.replace("(+)", " (+)").replace("(=)", " ($\\approx$)")
    m = m.replace("(-)", " ($-$)")
    return m


def check_t14() -> int:
    global cells_checked
    n = 0
    rows = read_csv_rows(STAGING / "T14.csv")
    data = [r for r in rows[1:] if r]
    trows = tex_data_rows(TABLES / "T14.tex")
    if len(trows) != len(data):
        fail(f"T14.tex: row count {len(trows)} != {len(data)}")
        return 0
    for crow, trow in zip(data, trows):
        exp = [_fmt_t14_metric(crow[0])] + [_fmt_t14(v) for v in crow[1:]]
        if trow != exp:
            fail(f"T14.tex row '{crow[0]}': tex {trow} != expected {exp}")
        n += len(exp) - 1
    cells_checked += n
    return n


# ---------------------------------------------------------------------------
# T15: Wilcoxon+Holm+A12 GSK-family summary
# ---------------------------------------------------------------------------
_DISPLAY_ALG = {"EGSK": "eGSK", "FDBAGSK": "FDB-AGSK"}


def check_t15() -> int:
    global cells_checked
    n = 0
    rows = read_csv_rows(STAGING / "T15.csv")
    header, data = rows[0], rows[1:]
    dims = []
    for col in header[1:]:
        d = col.split("_")[0]
        if d not in dims:
            dims.append(d)
    trows = tex_data_rows(TABLES / "T15.tex")
    if len(trows) != len(data):
        fail(f"T15.tex: row count {len(trows)} != {len(data)}")
        return 0
    for crow, trow in zip(data, trows):
        alg = _DISPLAY_ALG.get(crow[0].strip(), crow[0].strip())
        exp = [alg]
        for i in range(len(dims)):
            base = 1 + i * 7
            p, ph, w, t, ls, a12, dec = crow[base:base + 7]
            try:
                p = f"{float(p):.4f}"
            except ValueError:
                pass
            try:
                ph = f"{float(ph):.4f}"
            except ValueError:
                pass
            try:
                a12 = f"{float(a12):.3f}"
            except ValueError:
                pass
            exp.extend([p, ph, w, t, ls, a12, dec])
        if trow != exp:
            for j, (g, e) in enumerate(zip(trow, exp)):
                if g != e:
                    fail(f"T15.tex {alg} col{j}: '{g}' != '{e}'")
        n += len(exp) - 1
    cells_checked += n
    return n


# ---------------------------------------------------------------------------
# T16: Friedman mean ranks
# ---------------------------------------------------------------------------
def check_t16() -> int:
    global cells_checked
    n = 0
    rows = read_csv_rows(STAGING / "T16.csv")
    header, data = rows[0], rows[1:]
    n_cols = len(header) - 1
    col_vals: list[list[float]] = [[] for _ in range(n_cols)]
    for row in data:
        for j in range(n_cols):
            try:
                col_vals[j].append(float(row[1 + j]))
            except (ValueError, IndexError):
                col_vals[j].append(float("inf"))
    col_bests = [min(v) for v in col_vals]
    trows = tex_data_rows(TABLES / "T16.tex")
    if len(trows) != len(data):
        fail(f"T16.tex: row count {len(trows)} != {len(data)}")
        return 0
    for ridx, (crow, trow) in enumerate(zip(data, trows)):
        alg = _DISPLAY_ALG.get(crow[0].strip(), crow[0].strip())
        if trow[0] != alg:
            fail(f"T16.tex row {ridx}: label '{trow[0]}' != '{alg}'")
        for j in range(n_cols):
            val = float(crow[1 + j])
            exp = f"{val:.2f}"
            plain, bolded = strip_best(trow[1 + j])
            n += 1
            if plain != exp:
                fail(f"T16.tex {alg} col{j}: '{plain}' != '{exp}'")
            if bolded != (val == col_bests[j]):
                fail(f"T16.tex {alg} col{j}: bestval marker wrong")
    cells_checked += n
    return n


# ---------------------------------------------------------------------------
# T16_bca: full re-derivation (same seeded BCa scheme) + byte comparison
# ---------------------------------------------------------------------------
def check_t16_bca() -> int:
    global cells_checked
    import generate_t16_bca as t16b  # papers/scripts (sys.path above)

    all_results = {d: t16b._compute_bca_for_dim(d) for d in t16b.DIMS}
    regenerated = t16b._render_tex(all_results)
    published = require(TABLES / "T16_bca.tex").read_text(encoding="utf-8")
    n = 3 * len(t16b.DIMS) * len(t16b.ALGS)  # mean, lo, hi per cell
    if regenerated != published:
        fail("T16_bca.tex: byte-level regeneration mismatch (published "
             "file differs from seeded BCa re-derivation)")
    # cross-check point estimates vs staged T16.csv at 2-dp display
    t16_rows = read_csv_rows(STAGING / "T16.csv")
    header = t16_rows[0]
    dim_col = {int(c.split("_")[0][1:]): i + 1
               for i, c in enumerate(header[1:]) if c != "Overall_MeanRank"}
    tag_to_disp = {"GSK": "GSK", "AGSK": "AGSK", "APGSK": "APGSK",
                   "FDBAGSK": r"\fdbagsk{}", "ATMALS-GSK": "ATMALS-GSK",
                   "EGSK": r"\egsk{}", "DT-GSK": "DT-GSK"}
    for row in t16_rows[1:]:
        disp = tag_to_disp.get(row[0].strip())
        if disp is None:
            continue
        for d, ci in dim_col.items():
            theta = all_results[d][disp][0]
            cells_here = f"{theta:.2f}"
            staged = f"{float(row[ci]):.2f}"
            if cells_here != staged:
                fail(f"T16_bca vs T16.csv: {row[0]} D{d} point estimate "
                     f"{cells_here} != staged mean rank {staged}")
    cells_checked_local = n
    globals()["cells_checked"] += cells_checked_local
    return n


# ---------------------------------------------------------------------------
# Figures -- Nemenyi CD diagrams
# ---------------------------------------------------------------------------
def _pdf_text(path: Path) -> str:
    import pypdf
    return pypdf.PdfReader(str(require(path))).pages[0].extract_text()


def check_nemenyi() -> int:
    n = 0
    for dim in (10, 30, 50, 100):
        ranks: dict[str, float] = {}
        n_blocks = p_value = None
        disp = {"gsk": "GSK", "agsk": "AGSK", "apgsk": "APGSK",
                "fdb-agsk": "FDB-AGSK", "atmals-gsk": "ATMALS-GSK",
                "egsk": "eGSK", "dt-gsk": "DT-GSK"}
        rows = read_csv_rows(
            BUNDLE / "cec2017" / f"friedman_ranks_cec2017_D{dim}.csv")
        hdr = rows[0]
        for r in rows[1:]:
            rec = dict(zip(hdr, r))
            ranks[disp[rec["algorithm"].strip()]] = float(rec["mean_rank"])
            n_blocks = int(rec["n_blocks"])
            p_value = float(rec["p_value"])
        cd_rows = read_csv_rows(
            BUNDLE / "cec2017" / f"nemenyi_cd_cec2017_D{dim}.csv")
        cd_hdr = cd_rows[0]
        cds = {float(dict(zip(cd_hdr, r))["critical_difference"])
               for r in cd_rows[1:]}
        assert len(cds) == 1
        cd = cds.pop()
        if p_value >= 0.05:
            fail(f"nemenyi D{dim}: emitted despite non-significant omnibus "
                 f"p={p_value}")
        # recompute CD (k=7, q=2.949) as in the generator
        cd_re = 2.949 * math.sqrt(7 * 8 / (6.0 * n_blocks))
        if not math.isclose(cd_re, cd, rel_tol=1e-6, abs_tol=1e-9):
            fail(f"nemenyi D{dim}: recomputed CD {cd_re} != bundle {cd}")
        text = _pdf_text(
            PAPERS / "figures" / "nemenyi" / f"nemenyi_cd_cec2017_D{dim}.pdf")
        for lbl, v in ranks.items():
            n += 1
            if f"{v:.2f}" not in text:
                fail(f"nemenyi D{dim}: rank value {v:.2f} ({lbl}) not in PDF")
            if lbl not in text:
                fail(f"nemenyi D{dim}: label {lbl} not in PDF")
        n += 1
        if f"CD = {cd:.2f}" not in text:
            fail(f"nemenyi D{dim}: 'CD = {cd:.2f}' not found in PDF")
        if f"N = {n_blocks}" not in text.replace("N = ", "N = "):
            # title renders as $N = 29$; extraction gives 'N = 29'
            if f"N = {n_blocks}" not in text:
                fail(f"nemenyi D{dim}: N={n_blocks} not found in PDF title")
        # rank ordering: labels sorted by rank must appear in that order
        order = [lbl for lbl, _ in sorted(ranks.items(), key=lambda kv: kv[1])]
        pos = [text.find(lbl) for lbl in order]
        # DT-GSK contains 'GSK' etc.; use line-based order instead
        lines = [ln.strip() for ln in text.splitlines()]
        line_idx = []
        for lbl in order:
            try:
                line_idx.append(lines.index(lbl))
            except ValueError:
                line_idx.append(-1)
        if -1 in line_idx or line_idx != sorted(line_idx):
            fail(f"nemenyi D{dim}: label ordering in PDF "
                 f"{list(zip(order, line_idx))} not rank-sorted")
        _ = pos
    globals()["cells_checked"] += n
    return n


# ---------------------------------------------------------------------------
# Figures -- rank charts
# ---------------------------------------------------------------------------
def check_rank_charts() -> int:
    n = 0
    algs = ["gsk", "agsk", "apgsk", "fdb-agsk", "atmals-gsk", "egsk",
            "dt-gsk"]
    # rank_trend vs per-dim friedman CSVs (exact)
    trend: dict[tuple[str, int], float] = {}
    rows = read_csv_rows(BUNDLE / "cec2017" / "rank_trend_cec2017.csv")
    hdr = rows[0]
    for r in rows[1:]:
        rec = dict(zip(hdr, r))
        trend[(rec["algorithm"].strip(), int(rec["dimension"]))] = float(
            rec["mean_rank"])
    for dim in (10, 30, 50, 100):
        rows = read_csv_rows(
            BUNDLE / "cec2017" / f"friedman_ranks_cec2017_D{dim}.csv")
        hdr = rows[0]
        for r in rows[1:]:
            rec = dict(zip(hdr, r))
            a = rec["algorithm"].strip()
            n += 1
            if trend[(a, dim)] != float(rec["mean_rank"]):
                fail(f"rank_trend vs friedman D{dim} {a}: "
                     f"{trend[(a, dim)]} != {rec['mean_rank']}")
    # staging T16.csv vs friedman CSVs (T16.csv stores 6-dp fixed)
    t16 = read_csv_rows(STAGING / "T16.csv")
    hdr = t16[0]
    tag_to_key = {"GSK": "gsk", "AGSK": "agsk", "APGSK": "apgsk",
                  "FDBAGSK": "fdb-agsk", "ATMALS-GSK": "atmals-gsk",
                  "EGSK": "egsk", "DT-GSK": "dt-gsk"}
    for row in t16[1:]:
        key = tag_to_key[row[0].strip()]
        for i, col in enumerate(hdr[1:], start=1):
            if col == "Overall_MeanRank":
                continue
            dim = int(col.split("_")[0][1:])
            n += 1
            if abs(float(row[i]) - trend[(key, dim)]) > 5e-7:
                fail(f"T16.csv {row[0]} {col}: {row[i]} != bundle "
                     f"{trend[(key, dim)]}")
    # cec2011_ranks.pdf bar labels vs bundle
    rows = read_csv_rows(BUNDLE / "cec2011" / "friedman_ranks_cec2011.csv")
    hdr = rows[0]
    r2011 = {dict(zip(hdr, r))["algorithm"].strip():
             float(dict(zip(hdr, r))["mean_rank"]) for r in rows[1:]}
    text = _pdf_text(PAPERS / "figures" / "ranks" / "cec2011_ranks.pdf")
    for a in algs:
        n += 1
        if f"{r2011[a]:.2f}" not in text:
            fail(f"cec2011_ranks.pdf: value {r2011[a]:.2f} ({a}) not found")
    # friedman_gsk_family.pdf bar labels vs staging T16 Overall
    text = _pdf_text(
        PAPERS / "figures" / "ranks" / "friedman_gsk_family.pdf")
    oi = hdr_index = t16[0].index("Overall_MeanRank")
    _ = hdr_index
    for row in t16[1:]:
        n += 1
        if f"{float(row[oi]):.2f}" not in text:
            fail(f"friedman_gsk_family.pdf: Overall {float(row[oi]):.2f} "
                 f"({row[0]}) not found")
    globals()["cells_checked"] += n
    return n


# ---------------------------------------------------------------------------
# Figures -- convergence panel sample (>= 3 panels)
# ---------------------------------------------------------------------------
SAMPLE_PANELS = [(30, 3), (30, 10), (30, 12), (30, 26), (100, 1), (100, 12)]


def _independent_mean_curve(alg: str, func: int, dim: int):
    """Recompute the P2 per-checkpoint mean with plain csv arithmetic."""
    path = (REFERENCE_ROOT / "cec2017" / alg / "gen_logs"
            / f"CheckpointErrors_{alg}_F{func}_D{dim}.csv")
    with require(path).open("r", encoding="utf-8-sig", newline="") as fh:
        rows = [r for r in csv.reader(fh) if r]
    header, data = rows[0], rows[1:]
    cols = [(i, int(h[1:])) for i, h in enumerate(header)
            if h.startswith("E") and h[1:].isdigit()]
    evals = [b for _, b in cols]
    means = []
    for i, _ in cols:
        vals = [float(r[i]) for r in data]
        means.append(sum(vals) / len(vals))
    return evals, means, len(data)


def check_convergence_sample() -> int:
    from _convergence_common import PANEL_ORDER, load_mean_curve

    n = 0
    # bundle authoritative aggregated curves
    bundle_curves: dict[tuple[int, int, str], dict[int, float]] = {}
    bundle_nruns: dict[tuple[int, int, str], int] = {}
    for dim in {d for d, _ in SAMPLE_PANELS}:
        rows = read_csv_rows(
            BUNDLE / "cec2017" / f"convergence_checkpoints_cec2017_D{dim}.csv")
        hdr = rows[0]
        for r in rows[1:]:
            rec = dict(zip(hdr, r))
            key = (dim, int(rec["function"]), rec["algorithm"].strip())
            bundle_curves.setdefault(key, {})[int(rec["checkpoint_nfes"])] = \
                float(rec["mean_error"])
            bundle_nruns[key] = int(rec["n_runs"])
    for dim, func in SAMPLE_PANELS:
        for alg in PANEL_ORDER:
            evals_i, means_i, n_runs = _independent_mean_curve(alg, func, dim)
            loaded = load_mean_curve("cec2017", alg, func, dim)
            if loaded is None:
                fail(f"convergence F{func} D{dim} {alg}: loader returned "
                     "None but checkpoint file exists")
                continue
            evals_l, means_l = loaded
            if list(evals_l) != [float(e) for e in evals_i]:
                fail(f"convergence F{func} D{dim} {alg}: checkpoint grids "
                     "differ between loader and independent recompute")
                continue
            # endpoint (and full series) comparison, loader vs independent
            n += 1
            for e, mi, ml in zip(evals_i, means_i, means_l):
                if not math.isclose(mi, float(ml), rel_tol=1e-12,
                                    abs_tol=1e-300):
                    fail(f"convergence F{func} D{dim} {alg} E{e}: loader "
                         f"{float(ml)!r} != independent {mi!r}")
                    break
            # endpoint vs bundle (bundle stores %e with 6 decimals)
            key = (dim, func, alg)
            bc = bundle_curves.get(key)
            if not bc:
                fail(f"convergence F{func} D{dim} {alg}: no bundle curve")
                continue
            end_e = evals_i[-1]
            n += 1
            if end_e not in bc:
                fail(f"convergence F{func} D{dim} {alg}: final checkpoint "
                     f"E{end_e} absent from bundle")
            else:
                b = bc[end_e]
                mine = means_i[-1]
                ok = (mine == b == 0.0) or math.isclose(
                    mine, b, rel_tol=5e-7, abs_tol=5e-13)
                if not ok:
                    fail(f"convergence F{func} D{dim} {alg}: endpoint "
                         f"{mine!r} != bundle {b!r}")
            if bundle_nruns[key] != n_runs:
                fail(f"convergence F{func} D{dim} {alg}: n_runs {n_runs} "
                     f"!= bundle {bundle_nruns[key]}")
    globals()["cells_checked"] += n
    return n


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> int:
    results: list[tuple[str, int]] = []

    for i, d in [(1, "2011"), (2, "17-D10"), (3, "17-D30"), (4, "17-D50"),
                 (5, "17-D100")]:
        results.append((f"T{i:02d}.tex (head-to-head, CEC{d})",
                        check_h2h(f"T{i}.csv", f"T{i:02d}.tex")))
    results.append(("T06.tex (CEC2011 Wilcoxon summary)", check_t6()))
    for i, d in [(7, 10), (8, 30), (9, 50), (10, 100)]:
        results.append((f"T{i:02d}.tex (family Mean+-SD, D{d})",
                        check_family(f"T{i}.csv", f"T{i:02d}.tex")))
    for i, d in [(11, 10), (12, 30), (13, 50)]:
        results.append((f"T{i:02d}.tex (head-to-head, CEC2013 D{d})",
                        check_h2h(f"T{i}.csv", f"T{i:02d}.tex")))
    results.append(("T14.tex (CEC2013 Wilcoxon per-dim)", check_t14()))
    results.append(("T15.tex (Wilcoxon+Holm+A12 family)", check_t15()))
    results.append(("T16.tex (Friedman mean ranks)", check_t16()))
    results.append(("T16_bca.tex (seeded BCa re-derivation)",
                    check_t16_bca()))
    results.append(("Nemenyi CD diagrams D10/30/50/100 (PDF text vs bundle)",
                    check_nemenyi()))
    results.append(("Rank charts (rank_trend/T16 cross-check + PDF text)",
                    check_rank_charts()))
    results.append(("Convergence sample: 6 panels x 7 algorithms "
                    "(endpoints vs recomputed checkpoint means + bundle)",
                    check_convergence_sample()))

    verdict = "PASS" if not mismatches else "FAIL"
    lines = [
        "# Phase 7 exhibit validation report (task 12)",
        "",
        f"Verdict: **{verdict}** -- {len(mismatches)} mismatch(es); "
        f"{cells_checked} value-level comparisons.",
        "",
        "Authoritative sources: the promoted benchmark export "
        "`benchmarks/cec_reference_results/_paper_tables/` (single source of "
        "truth; exported exclusively from the Phase 6 bundle, then promoted "
        f"from results/paper_tables/ staging, per `provenance.json`), the bundle "
        f"`papers/analysis/{RELEASE_ID}/`, and (for convergence, per "
        "pre-registration P2) `benchmarks/cec_reference_results/` "
        "gen_logs. Tolerance = display rounding only (generator formatting "
        "rules re-applied; string equality required). No `results/_run_all`,"
        " no `results/_ablation`, no rendered `.tex` used as a data source.",
        "",
        "## Checks",
        "",
        "| Check | Comparisons |",
        "|---|---|",
    ]
    for name, cnt in results:
        lines.append(f"| {name} | {cnt} |")
    lines += [
        "",
        "## Method notes",
        "",
        "- T01--T05, T11--T13: every Best/Median/Worst/Mean/SD cell "
        "re-formatted from the staged CSV (`_fmt_sci` 2-dp scientific) and "
        "string-compared; `\\bestval` bold-mean marker position re-derived "
        "and asserted.",
        "- T07--T10: every Mean and SD cell compared (2 comparisons per "
        "table cell); bolded best-mean column re-derived.",
        "- T14/T15/T16: generator formatting rules replicated exactly "
        "(4-dp p, 3-dp A12, 2-dp ranks, T14 mixed-format rule); T16 "
        "per-column best markers re-derived.",
        "- T16_bca: full end-to-end re-derivation (bundle descriptive "
        "stats -> midrank Friedman ranks -> seeded BCa bootstrap, "
        "BASE_SEED=20260422, n_boot=10000) rendered to LaTeX and compared "
        "byte-for-byte with the published file; point estimates "
        "cross-checked against staged T16.csv at 2-dp display.",
        "- Nemenyi: PDF text extracted (pypdf); the 7 rank value labels, "
        "rank-sorted algorithm ordering, CD scale-bar value, and N block "
        "count compared against the bundle friedman/nemenyi CSVs; CD "
        "recomputed (k=7, q_0.05=2.949); omnibus gate re-checked.",
        "- Rank charts: bundle `rank_trend_cec2017.csv` cross-checked "
        "value-by-value against the four per-dimension friedman CSVs "
        "(exact) and staged `T16.csv` (<=5e-7, its 6-dp storage); "
        "`cec2011_ranks.pdf` / `friedman_gsk_family.pdf` numeric bar "
        "labels extracted and matched. `rank_vs_dim_cec2017.pdf` and "
        "`cec2017_mean_ranks.pdf` carry no numeric text labels; their "
        "data path is covered by the same source cross-checks (identical "
        "loader inputs), disclosed here rather than claimed as pixel "
        "checks.",
        "- Convergence: 6 sampled panels (D30 F3/F10/F12/F26 = the frozen "
        "P5 main-text selection; D100 F1/F12) x 7 algorithms; full mean "
        "series recomputed independently (plain csv arithmetic) and "
        "compared to the plotting loader at rel_tol=1e-12, and endpoints "
        "compared to the bundle aggregated curves at their 7-significant-"
        "digit storage precision; n_runs asserted equal.",
        "",
        "## Mismatches",
        "",
    ]
    if mismatches:
        lines += [f"- {m}" for m in mismatches]
    else:
        lines.append("(none)")
    lines.append("")
    REPORT.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {REPORT}")
    print(f"verdict: {verdict}; {cells_checked} comparisons; "
          f"{len(mismatches)} mismatches")
    for m in mismatches:
        print(" MISMATCH:", m)
    return 0 if not mismatches else 1


if __name__ == "__main__":
    sys.exit(main())
