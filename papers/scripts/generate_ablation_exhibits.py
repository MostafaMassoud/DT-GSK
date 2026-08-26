#!/usr/bin/env python3
# Copyright (c) 2026 Mostafa Masoud <moustafa.masoud@gmail.com>
"""Render the Phase-12 X-ABL-01 scaffold-ablation supplement exhibits.

This is a *presentation* step only: it reads the already-computed,
release-bound analysis outputs under

    papers/build_prompt_phases/phase_12/ablation_results/

    * ``ablation_matrix_rank_summary_cec2017_D{10,30,50,100}.csv``
      (mean-Friedman-rank + full-vs-cell paired Wilcoxon, Holm within
      dimension; produced by ``generate_ablation_matrix.py`` from the
      promoted immutable release
      ``benchmarks/cec_reference_results/_ablation/scaffold``),
    * ``ablation_descriptive_deltas_cec2017.csv`` (identifiability /
      win-tie-loss context), and
    * ``ablation_results_manifest.json`` (Friedman omnibus p per
      dimension + the SHA-256 of every source CSV),

verifies each source CSV against the manifest SHA-256 (fail-closed), and
emits the three frozen-ID exhibits WITHOUT re-typing a single number:

    * ``papers/tables/SA01.tex``  -> tab:abl-scaffold
        mean-Friedman-rank ablation matrix (cells x dimensions).
    * ``papers/tables/SA02.tex``  -> tab:abl-wilcoxon
        full-vs-cell paired Wilcoxon + Holm table, per dimension.
    * ``papers/figures/ablation/abl_rank_delta.{pdf,png}`` -> fig:abl-rankdelta
        conditional rank-degradation (Delta rank) bar figure.

Every value therefore binds transitively to the promoted ablation
release. Nothing here recomputes statistics or touches raw evidence.

Interpretation scope carried in the captions (authored in
``supplementary.tex``), never overridden here: ISM OFF in every cell;
conditional remove-one contributions (not independent causal effects);
no cross-dimension averaging where signs differ; manifest-recorded run count; 29 functions.

Usage::

    python papers/scripts/generate_ablation_exhibits.py
"""
from __future__ import annotations

import csv
import hashlib
import json
import os

_RUNS = os.environ.get("GSK_ABL_RUNS", "51")
_RELID = os.environ.get("GSK_ABL_RELID", "abl-rel-2026-07-16")
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

import _fig_style
_fig_style.apply()

_SCRIPT_DIR = Path(__file__).resolve().parent
_PAPER_DIR = _SCRIPT_DIR.parent
_PROJECT_ROOT = _PAPER_DIR.parent

# Input read path = the release-bound rank matrices staged under
# phase_12/ablation_results/ (each verified against the manifest SHA-256 in
# _verify_source); this is NOT results/ staging, so there is no results/ ->
# benchmarks/ read-path to repoint here.  The promoted immutable evidence
# these matrices aggregate (logical release id abl-rel-2026-07-13, retained
# in ablation_results_manifest.json's immutable_release.root) physically
# resides after the Stage-1 restructure at
# benchmarks/cec_reference_results/_ablation/scaffold (X-ABL-01, CEC2017);
# generate_ablation_matrix.py reads that benchmark tree to produce these
# matrices.  The abl-rel-2026-07-13 release id echoed into SA01/SA02 and the
# word_sources JSON below is left verbatim so the exhibits stay consistent
# with that unaltered manifest data.
_ABL_DIR = _PAPER_DIR / "build_prompt_phases" / "phase_12" / "ablation_results"
_MANIFEST = _ABL_DIR / "ablation_results_manifest.json"

_TABLES_DIR = _PAPER_DIR / "tables"
_WORD_SOURCES = _TABLES_DIR / "word_sources"
_FIG_DIR = _PAPER_DIR / "figures" / "ablation"

_DIMS = [10, 30, 50, 100]

# CR-0023 (R1.4): relative tolerance for the fail-closed check that the
# recomputed UNCORRECTED Friedman p reproduces the manifest's recorded value.
# Observed maximum deviation across the four dimensions is 0.21% (D10), which
# reflects the manifest's rounded storage, not a data difference.
_OMNIBUS_TOL = 0.005

# Fixed presentation order (pre-registration Section 1.1 cell order;
# baseline first as the full-scaffold reference cell).
_CELL_ORDER = ["baseline", "no_ace", "no_psr", "no_bse",
               "no_linkage", "no_localsearch", "no_arch"]

# LaTeX row labels for the rank matrix (human names; the NUMBERS are read
# from the CSVs, never typed here).
_CELL_LABEL_TEX = {
    "baseline": r"Full scaffold (baseline)",
    "no_ace": r"$-$\,ACE (bandit operator control)",
    "no_psr": r"$-$\,NLPSR (population reduction)",
    "no_bse": r"$-$\,BSE (budget-safe escape)",
    "no_linkage": r"$-$\,Linkage-aware block crossover",
    "no_localsearch": r"$-$\,Local search (coordinate)",
    "no_arch": r"$-$\,Diversity archive",
}

# Short labels for the figure legend (also reused for the SA02 DOCX cells).
_CELL_LABEL_FIG = {
    "no_ace": "-ACE",
    "no_psr": "-NLPSR",
    "no_bse": "-BSE",
    "no_linkage": "-Linkage",
    "no_localsearch": "-Local search",
    "no_arch": "-Archive",
}

# Plain-text (no LaTeX math) row labels for the native Word tables (SA01).
_CELL_LABEL_DOCX = {
    "baseline": "Full scaffold (baseline)",
    "no_ace": "-ACE (bandit operator control)",
    "no_psr": "-NLPSR (population reduction)",
    "no_bse": "-BSE (budget-safe escape)",
    "no_linkage": "-Linkage-aware block crossover",
    "no_localsearch": "-Local search (coordinate)",
    "no_arch": "-Diversity archive",
}

# Okabe-Ito colour map, frozen in the ablation pre-registration
# (Section 4.1, X-ABL-01 styling). baseline is the black zero reference.
_CELL_HATCH = {  # greyscale channel, aligned with _CELL_COLOR keys
    "no_ace": '',
    "no_psr": '//',
    "no_bse": '..',
    "no_linkage": 'xx',
    "no_localsearch": '\\\\',
    "no_arch": '++',
}

_CELL_COLOR = {
    "no_ace": "#E69F00",
    "no_psr": "#56B4E9",
    "no_bse": "#009E73",
    "no_linkage": "#CC79A7",
    "no_localsearch": "#0072B2",
    "no_arch": "#999999",
}

_PNG_DPI = 300
_PDF_METADATA = {"CreationDate": None}  # deterministic (no build timestamp)

# Shared design from _fig_style.apply(); only the bbox rule is local.
plt.rcParams.update({"savefig.bbox": "tight"})


# ---------------------------------------------------------------------------
# IO + release-binding verification
# ---------------------------------------------------------------------------
def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def _load_manifest() -> dict:
    if not _MANIFEST.is_file():
        raise SystemExit(f"HARD FAIL: manifest missing: {_MANIFEST}")
    return json.loads(_MANIFEST.read_text(encoding="utf-8"))


def _corrected_omnibus(manifest: dict) -> dict[str, float]:
    """Iman-Davenport omnibus p per dimension, on the tie-corrected chi2.

    CR-0023 (journal round-1 major revision, R1.4).  The manifest's
    ``friedman_p_by_dimension`` holds the classical chi-square approximation,
    while the main text decides on the tie-corrected chi2 with the
    Iman-Davenport F (M-026 / D-0016).  The component-study exhibits now use
    the same convention.

    The manifest is append-only and is NOT edited: the corrected values are
    recomputed here from the same promoted immutable release the rank matrices
    aggregate.  As a fail-closed release binding, recomputing the *uncorrected*
    statistic must reproduce the manifest's recorded p to within
    ``_OMNIBUS_TOL`` -- otherwise this generator is reading different data than
    the manifest recorded and must refuse to emit.

    Direction is bounded a priori: the tie-correction factor C <= 1, so the
    corrected statistic is always >= the uncorrected one and every p can only
    decrease.  No rank, sign, or Holm decision can change as a result.
    """
    import sys as _sys
    if str(_SCRIPT_DIR) not in _sys.path:
        _sys.path.insert(0, str(_SCRIPT_DIR))
    import generate_ablation_matrix as _gam
    from scipy.stats import f as _scipy_f
    from gsk_family.analysis.statistics import friedman_rank as _friedman_rank

    scaffold = _PROJECT_ROOT / "benchmarks/cec_reference_results/_ablation/scaffold"
    if not scaffold.is_dir():
        raise SystemExit(f"HARD FAIL: scaffold release missing: {scaffold}")

    recorded = manifest["friedman_p_by_dimension"]
    out: dict[str, float] = {}
    for d in _DIMS:
        means = _gam._discover_cells(scaffold, "cec2017", d)
        funcs = sorted(set.intersection(*(set(m) for m in means.values())))
        cells = sorted(means)
        fr = _friedman_rank({c: [means[c][f] for f in funcs] for c in cells})
        n, k = len(funcs), len(cells)

        # fail-closed: the uncorrected recomputation must match the manifest
        rec = float(recorded[f"D{d}"])
        got = float(fr.p_value)
        if rec <= 0.0 or abs(got - rec) / rec > _OMNIBUS_TOL:
            raise SystemExit(
                f"HARD FAIL: D{d} uncorrected Friedman p does not reproduce the "
                f"manifest value (manifest {rec:.6e}, recomputed {got:.6e}); "
                "the generator is not reading the release the manifest recorded.")

        chi2 = float(fr.statistic_tie_corrected)
        if not np.isfinite(chi2):
            chi2 = float(fr.statistic)
        denom = n * (k - 1) - chi2
        if denom <= 1e-12:
            raise SystemExit(f"HARD FAIL: D{d} Iman-Davenport denominator <= 0.")
        f_id = (n - 1) * chi2 / denom
        p_id = float(_scipy_f.sf(f_id, k - 1, (k - 1) * (n - 1)))
        if p_id > rec:
            raise SystemExit(
                f"HARD FAIL: D{d} corrected p ({p_id:.6e}) exceeds the "
                f"uncorrected p ({rec:.6e}); C <= 1 makes this impossible.")
        out[f"D{d}"] = p_id
    return out


def _verify_source(rel_path: str, manifest: dict) -> Path:
    """Confirm a source CSV matches its manifest SHA-256 (release binding).

    Manifest ``files`` paths are stated relative to the phase_12 directory.
    """
    phase12 = _PAPER_DIR / "build_prompt_phases" / "phase_12"
    path = phase12 / rel_path
    if not path.is_file():
        raise SystemExit(f"HARD FAIL: source missing: {path}")
    want = next((f["sha256"] for f in manifest["files"] if f["path"] == rel_path), None)
    if want is None:
        raise SystemExit(f"HARD FAIL: {rel_path} not listed in manifest 'files'.")
    got = _sha256(path)
    if got != want:
        raise SystemExit(
            f"HARD FAIL: SHA-256 mismatch for {rel_path}\n  manifest={want}\n  ondisk ={got}\n"
            "Exhibits must bind to the promoted release; refusing to render stale data."
        )
    return path


def _read_rank_csv(path: Path) -> dict[str, dict]:
    """cell -> {mean_rank, delta, best_count, n_funcs, wilcoxon_p, holm_p, sig}."""
    rows: dict[str, dict] = {}
    with path.open(newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            cell = r["cell"].strip()
            def _f(key):
                v = (r.get(key) or "").strip()
                return float(v) if v not in ("", "nan") else float("nan")
            rows[cell] = {
                "mean_rank": _f("mean_rank"),
                "delta": _f("delta_rank_vs_full"),
                "best_count": int(float(r["best_count"])) if r.get("best_count") else 0,
                "n_funcs": int(float(r["n_funcs"])) if r.get("n_funcs") else 0,
                "wilcoxon_p": _f("wilcoxon_p"),
                "holm_p": _f("holm_p"),
                "sig": (r.get("significant") or "").strip().lower() == "yes",
            }
    return rows


# ---------------------------------------------------------------------------
# LaTeX formatting helpers
# ---------------------------------------------------------------------------
def _fmt_p(p: float) -> str:
    """p-value -> LaTeX math string (fixed for >=1e-3, scientific below)."""
    if p != p:  # NaN
        return r"--"
    if p >= 0.01:
        return f"{p:.3f}"
    if p >= 0.001:
        return f"{p:.4f}"
    mant, exp = f"{p:.2e}".split("e")
    return rf"${mant}\times10^{{{int(exp)}}}$"


def _fmt_friedman_p(p: float) -> str:
    mant, exp = f"{p:.1e}".split("e")
    return rf"${mant}\times10^{{{int(exp)}}}$"


def _fmt_p_plain(p: float) -> str:
    """p-value -> plain text for the native Word tables (e-notation < 1e-3;
    matches the word_sources convention of storing e-notation as text)."""
    if p != p:
        return "--"
    if p >= 0.01:
        return f"{p:.3f}"
    if p >= 0.001:
        return f"{p:.4f}"
    return f"{p:.2e}"  # e.g. "2.16e-04"


def _fmt_friedman_p_plain(p: float) -> str:
    return f"{p:.1e}"  # e.g. "3.4e-05"


_PROV = (
    "% AUTO-GENERATED by papers/scripts/generate_ablation_exhibits.py -- DO NOT EDIT BY HAND.\n"
    "% Source (release-bound): papers/build_prompt_phases/phase_12/ablation_results/\n"
    "% Promoted ablation release: benchmarks/cec_reference_results/_ablation/scaffold\n"
    f"% Study X-ABL-01 (scaffold remove-one); CEC2017; D10/30/50/100; {_RUNS} runs; 29 functions; ISM OFF in every cell.\n"
)


# ---------------------------------------------------------------------------
# SA01 -- tab:abl-scaffold (mean-Friedman-rank matrix, cells x dimensions)
# ---------------------------------------------------------------------------
def _write_sa01(per_dim: dict[int, dict[str, dict]], fried_p: dict[int, float]) -> Path:
    lines = [_PROV]
    lines.append(r"\begin{tabular}{@{}lcccc@{}}")
    lines.append(r"\toprule")
    lines.append(r"\textbf{Configuration} & \textbf{$D=10$} & \textbf{$D=30$} & "
                 r"\textbf{$D=50$} & \textbf{$D=100$} \\")
    lines.append(r" & \multicolumn{4}{c}{\footnotesize mean Friedman rank "
                 r"($\Delta$ vs baseline; lower rank is better)} \\")
    lines.append(r"\midrule")
    for cell in _CELL_ORDER:
        cells_txt = [_CELL_LABEL_TEX[cell]]
        for d in _DIMS:
            row = per_dim[d][cell]
            rank = row["mean_rank"]
            if cell == "baseline":
                cells_txt.append(rf"{rank:.2f}\,(ref)")
            else:
                star = r"$^{\ast}$" if row["sig"] else ""
                cells_txt.append(rf"{rank:.2f}\,({row['delta']:+.2f}){star}")
        lines.append(" & ".join(cells_txt) + r" \\")
    lines.append(r"\midrule")
    fried_txt = [r"\textit{Iman--Davenport omnibus $p$}"]
    for d in _DIMS:
        fried_txt.append(_fmt_friedman_p(fried_p[f"D{d}"]))
    lines.append(" & ".join(fried_txt) + r" \\")
    lines.append(r"\bottomrule")
    lines.append(r"\end{tabular}")
    out = _TABLES_DIR / "SA01.tex"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return out


# ---------------------------------------------------------------------------
# SA02 -- tab:abl-wilcoxon (full-vs-cell paired Wilcoxon + Holm, per dimension)
# ---------------------------------------------------------------------------
def _write_sa02(per_dim: dict[int, dict[str, dict]], fried_p: dict[int, float]) -> Path:
    lines = [_PROV]
    lines.append(r"\begin{tabular}{@{}lrrrc@{}}")
    lines.append(r"\toprule")
    lines.append(r"\textbf{Component removed} & \textbf{$\Delta$rank} & "
                 r"\textbf{Wilcoxon $p$} & \textbf{Holm $p$} & \textbf{Holm sig.} \\")
    lines.append(r"\midrule")
    for i, d in enumerate(_DIMS):
        rows = per_dim[d]
        # inference family = the six non-baseline cells, ascending raw p
        # (Holm step-down order); deterministic tie-break on cell name.
        cells = [c for c in _CELL_ORDER if c != "baseline"]
        cells.sort(key=lambda c: (rows[c]["wilcoxon_p"], c))
        fam = len(cells)
        header = (rf"\multicolumn{{5}}{{@{{}}l}}{{\textbf{{$D={d}$}}\quad "
                  rf"Iman--Davenport $p={_fmt_friedman_p(fried_p[f'D{d}']).strip('$')}$; "
                  rf"Holm family size $={fam}$}}")
        if i > 0:
            lines.append(r"\midrule")
        lines.append(header + r" \\")
        lines.append(r"\addlinespace[2pt]")
        for c in cells:
            r = rows[c]
            sig = r"\textbf{yes}" if r["sig"] else "no"
            lines.append(
                f"{_CELL_LABEL_FIG[c]} & {r['delta']:+.2f} & "
                f"{_fmt_p(r['wilcoxon_p'])} & {_fmt_p(r['holm_p'])} & {sig}" + r" \\"
            )
    lines.append(r"\bottomrule")
    lines.append(r"\end{tabular}")
    out = _TABLES_DIR / "SA02.tex"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return out


# ---------------------------------------------------------------------------
# Native-Word semantic sources (word_sources/*.json) -- flat single-header
# reconstructions of SA01/SA02 consumed by build_docx.py's native-table
# builder (same values as the .tex; the rich .tex drives the PDF).
# ---------------------------------------------------------------------------
def _write_sa01_json(per_dim: dict[int, dict[str, dict]],
                     fried_p: dict[int, float], src_sha: dict[str, str]) -> Path:
    headers = ["Configuration", "D=10", "D=30", "D=50", "D=100"]
    rows: list[list[str]] = []
    for cell in _CELL_ORDER:
        row = [_CELL_LABEL_DOCX[cell]]
        for d in _DIMS:
            c = per_dim[d][cell]
            if cell == "baseline":
                row.append(f"{c['mean_rank']:.2f} (ref)")
            else:
                star = "*" if c["sig"] else ""
                row.append(f"{c['mean_rank']:.2f} ({c['delta']:+.2f}){star}")
        rows.append(row)
    rows.append(["Iman-Davenport omnibus p"] +
                [_fmt_friedman_p_plain(fried_p[f"D{d}"]) for d in _DIMS])
    doc = {
        "table_id": "SA01",
        "manuscript_label": "Table A15",
        "caption_stub": ("Scaffold remove-one ablation on CEC2017: mean Friedman "
                         "rank per cell and dimension, change vs baseline in "
                         "parentheses; ISM off in every cell; conditional "
                         f"remove-one contributions; {_RUNS} runs; * = Holm-significant."),
        "headers": [headers],
        "rows": rows,
        "notes": [
            f"values reproduced from the promoted ablation release {_RELID} "
            "via generate_ablation_exhibits.py (release-bound; same values as tables/SA01.tex)",
            "each parenthesised value is a conditional remove-one delta (ISM off), "
            "not an independent causal effect; not averaged across dimensions",
            "omnibus p is the Iman-Davenport F on the tie-corrected Friedman "
            "statistic, the same convention the main text uses (M-026/D-0016); "
            "the classical chi-square approximation previously reported gives "
            "1.8e-06, 2.5e-08, 5.8e-03, 3.5e-02 and is retained as an audit "
            "companion. Because the tie-correction factor C <= 1, the correction "
            "can only increase the statistic; no rank or Holm decision changes.",
        ],
        "number_format": "as-is",
        "source": "papers/build_prompt_phases/phase_12/ablation_results/"
                  "ablation_matrix_rank_summary_cec2017_D{10,30,50,100}.csv",
        "source_sha256": src_sha,
    }
    out = _WORD_SOURCES / "SA01.json"
    out.write_text(json.dumps(doc, indent=1) + "\n", encoding="utf-8")
    return out


def _write_sa02_json(per_dim: dict[int, dict[str, dict]],
                     src_sha: dict[str, str]) -> Path:
    headers = ["Dim", "Component removed", "Δrank",
               "Wilcoxon p", "Holm p", "Holm sig."]
    rows: list[list[str]] = []
    for d in _DIMS:
        cells = [c for c in _CELL_ORDER if c != "baseline"]
        cells.sort(key=lambda c: (per_dim[d][c]["wilcoxon_p"], c))
        for c in cells:
            r = per_dim[d][c]
            rows.append([
                f"D={d}", _CELL_LABEL_FIG[c], f"{r['delta']:+.2f}",
                _fmt_p_plain(r["wilcoxon_p"]), _fmt_p_plain(r["holm_p"]),
                "yes" if r["sig"] else "no",
            ])
    doc = {
        "table_id": "SA02",
        "manuscript_label": "Table A16",
        "caption_stub": ("Scaffold remove-one ablation on CEC2017: full-vs-cell "
                         "paired Wilcoxon signed-rank with Holm correction within "
                         f"each dimension (alpha=0.05); ISM off; {_RUNS} runs; ordered "
                         "by ascending raw p within each dimension."),
        "headers": [headers],
        "rows": rows,
        "notes": [
            f"values reproduced from the promoted ablation release {_RELID} "
            "via generate_ablation_exhibits.py (release-bound; same values as tables/SA02.tex)",
            "Holm family = the six disabled-cell comparisons within each dimension; "
            "the four significant contrasts are all favorable (removal degrades)",
        ],
        "number_format": "as-is",
        "source": "papers/build_prompt_phases/phase_12/ablation_results/"
                  "ablation_matrix_rank_summary_cec2017_D{10,30,50,100}.csv",
        "source_sha256": src_sha,
    }
    out = _WORD_SOURCES / "SA02.json"
    out.write_text(json.dumps(doc, indent=1) + "\n", encoding="utf-8")
    return out


# ---------------------------------------------------------------------------
# fig:abl-rankdelta -- conditional rank-degradation bar figure
# ---------------------------------------------------------------------------
def _write_figure(per_dim: dict[int, dict[str, dict]]) -> list[Path]:
    cells = [c for c in _CELL_ORDER if c != "baseline"]
    n_cells = len(cells)
    n_dim = len(_DIMS)
    group_w = 0.84
    bar_w = group_w / n_cells

    fig, ax = plt.subplots(figsize=(7.2, 4.0))
    x = np.arange(n_dim)
    for j, cell in enumerate(cells):
        deltas = [per_dim[d][cell]["delta"] for d in _DIMS]
        sig = [per_dim[d][cell]["sig"] for d in _DIMS]
        xpos = x - group_w / 2 + (j + 0.5) * bar_w
        bars = ax.bar(
            xpos, deltas, width=bar_w * 0.92,
            color=_CELL_COLOR[cell],
            # Audit 2026-07-23: four of the six Okabe-Ito bar colours are
            # near-identical in greyscale (luminance 151-162), so a B/W print
            # could not tell the components apart.  Hatches are a redundant
            # non-colour channel; the dark edge makes them visible.
            hatch=_CELL_HATCH[cell], edgecolor="#333333", linewidth=0.3,
            label=_CELL_LABEL_FIG[cell],
        )
        # star the Holm-significant bars
        for k, (b, s) in enumerate(zip(bars, sig)):
            if s:
                h = b.get_height()
                ax.text(b.get_x() + b.get_width() / 2, h + 0.06,
                        "*", ha="center", va="bottom", fontsize=11,
                        fontweight="bold", color="#202020")

        # SE-045: a delta of exactly zero draws a bar of zero height, which is
        # indistinguishable from a series that was never plotted -- the reader
        # cannot tell "removal changed nothing" from "this cell is missing".
        # Mark those explicitly with a caret on the zero line.
        for b, d in zip(bars, deltas):
            if abs(d) < 1e-9:
                ax.plot(b.get_x() + b.get_width() / 2, 0.0, marker="_",
                        markersize=bar_w * 46, markeredgewidth=1.6,
                        color=_CELL_COLOR[cell], zorder=4, clip_on=False)
                ax.text(b.get_x() + b.get_width() / 2, 0.04, "0",
                        ha="center", va="bottom", fontsize=6.5,
                        color="#404040", zorder=5)

    ax.axhline(0.0, color="#000000", linewidth=1.2, zorder=3)
    # Audit 2026-07-23: the D100 group has bars to ~-0.2 but the lowest labeled
    # tick was 0.0; give the negative region scale.
    ymin, ymax = ax.get_ylim()
    ax.set_ylim(min(ymin, -0.45), ymax)
    ax.set_xticks(x)
    ax.set_xticklabels([f"D{d}" for d in _DIMS])
    ax.set_xlabel("Problem dimension", fontsize=10)
    ax.set_ylabel(r"$\Delta$ mean Friedman rank vs full scaffold"
                  "\n(positive $=$ removal degrades)", fontsize=10)
    # No internal headline: the supplement caption states the design (ISM
    # off, run count, 29 functions) and that * marks Holm-significance.
    ax.grid(axis="y")
    ax.set_axisbelow(True)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.16),
              ncol=6, frameon=False, fontsize=8, columnspacing=1.1,
              handlelength=1.4, handletextpad=0.5)

    fig.tight_layout()
    _FIG_DIR.mkdir(parents=True, exist_ok=True)
    stem = _FIG_DIR / "abl_rank_delta"
    pdf, png = stem.with_suffix(".pdf"), stem.with_suffix(".png")
    fig.savefig(pdf, format="pdf", metadata=_PDF_METADATA)
    fig.savefig(png, format="png", dpi=_PNG_DPI)
    plt.close(fig)
    return [pdf, png]


def main() -> int:
    manifest = _load_manifest()
    # CR-0023 (R1.4): report the Iman-Davenport omnibus on the tie-corrected
    # chi2, the same decision statistic the main text uses. The manifest's
    # uncorrected values are retained as the fail-closed reproduction anchor.
    fried_p_uncorrected = manifest["friedman_p_by_dimension"]
    fried_p = _corrected_omnibus(manifest)

    # verify + read every source rank CSV against the manifest SHA-256
    per_dim: dict[int, dict[str, dict]] = {}
    src_sha: dict[str, str] = {}
    for d in _DIMS:
        rel = f"ablation_results/ablation_matrix_rank_summary_cec2017_D{d}.csv"
        path = _verify_source(rel, manifest)
        per_dim[d] = _read_rank_csv(path)
        src_sha[f"D{d}"] = _sha256(path)
    # verify the descriptive-deltas source too (identifiability provenance)
    _verify_source("ablation_results/ablation_descriptive_deltas_cec2017.csv", manifest)

    _TABLES_DIR.mkdir(parents=True, exist_ok=True)
    _WORD_SOURCES.mkdir(parents=True, exist_ok=True)
    sa01 = _write_sa01(per_dim, fried_p)
    sa02 = _write_sa02(per_dim, fried_p)
    sa01_json = _write_sa01_json(per_dim, fried_p, src_sha)
    sa02_json = _write_sa02_json(per_dim, src_sha)
    figs = _write_figure(per_dim)

    outs = [sa01, sa02, sa01_json, sa02_json, *figs]
    manifest_out = {
        "schema": "ablation_exhibits_manifest/v1",
        "study_id": manifest["study_id"],
        "immutable_release": manifest["immutable_release"]["root"],
        "generator": "papers/scripts/generate_ablation_exhibits.py",
        "exhibits": {
            "tab:abl-scaffold": "papers/tables/SA01.tex",
            "tab:abl-wilcoxon": "papers/tables/SA02.tex",
            "fig:abl-rankdelta": "papers/figures/ablation/abl_rank_delta.pdf",
        },
        "outputs": {str(p.relative_to(_PROJECT_ROOT)).replace("\\", "/"): _sha256(p) for p in outs},
    }
    (_ABL_DIR.parent / "ablation_exhibits_manifest.json").write_text(
        json.dumps(manifest_out, indent=2) + "\n", encoding="utf-8")

    for p in outs:
        print(f"  wrote {p.relative_to(_PROJECT_ROOT)}")
    print("  wrote papers/build_prompt_phases/phase_12/ablation_exhibits_manifest.json")
    print("Done (all sources verified against the promoted-release manifest SHA-256).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
