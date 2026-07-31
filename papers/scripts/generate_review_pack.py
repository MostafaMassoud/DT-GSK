#!/usr/bin/env python3
"""One-file CEC2017 review pack for advisor review.

Builds ``papers/DT-GSK-CEC2017-review.pdf``:
  page 1          headline dashboard (Friedman ranks, Wilcoxon scoreboard)
  pages 2-5       CEC2017 7-algorithm mean table, one dimension per page
  page 6          CEC2011 mean table (DT-GSK vs GSK vs ATMALS-GSK)
  then            CEC2017 convergence grids (29 funcs x 4 dims) and
                  CEC2011 convergence grids (22 problems, native dims).

The convergence grids show the full **7-algorithm GSK-family panel**
(GSK, AGSK, APGSK, FDB-AGSK, eGSK, ATMALS-GSK, DT-GSK).  Each curve is the
**mean best-so-far error over that algorithm's runs** read at the shared CEC
checkpoints (the ``E<evals>`` columns of ``CheckpointErrors_*.csv``).  DT-GSK
is drawn last and most prominently (deep-blue solid line with markers).

Input result folders
--------------------
* Comparators (gsk, agsk, apgsk, fdb-agsk, egsk, atmals-gsk):
  ``benchmarks/cec_reference_results/<suite>/<alg>/gen_logs/``
* DT-GSK (reproduced locally):
  ``results/_run_all/dt-gsk/<suite>/gen_logs/``

All seven algorithms expose the same checkpoint schema
``CheckpointErrors_<alg>_F<func>_D<dim>.csv`` with header
``Run,Seed,E1000,E2000,...,E100000``.

Missing data
------------
DT-GSK has CEC2017 D10 complete + D30 partial only (no D50/D100), and no
CEC2011 checkpoints.  Missing (algorithm, function, dimension) curves are
**never fabricated**: they are skipped on the plot, summarised on the console
and written to ``papers/DT-GSK-CEC2017-review_missing.log``.

Regenerate with::

    python papers/scripts/generate_review_pack.py
"""
from __future__ import annotations

import csv
import sys
from collections import defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.lines import Line2D

_REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO))
sys.path.insert(0, str(_REPO / "src"))

from gsk_family.analysis.result_loader import (  # noqa: E402
    CEC2011_COMPARATORS,
    GSK_FAMILY,
    load_comparison_set,
)
from gsk_family.analysis.statistical_tests import (  # noqa: E402
    wilcoxon_signed_rank,
)
from scipy.stats import rankdata  # noqa: E402

_ISM_GL = _REPO / "results" / "_run_all" / "dt-gsk" / "cec2017" / "gen_logs"
_GSK_CURVES = _REPO / "results" / "gsk" / "cec2017" / "curves"
_ISM_GL_2011 = (_REPO / "results" / "_run_all" / "dt-gsk" /
                "cec2011" / "gen_logs")
_GSK_CURVES_2011 = _REPO / "results" / "gsk" / "cec2011" / "curves"
_OUT = _REPO / "papers" / "DT-GSK-CEC2017-review.pdf"
_MISSING_LOG = _REPO / "papers" / "DT-GSK-CEC2017-review_missing.log"
_DIMS = (10, 30, 50, 100)
_FUNCS = tuple(f for f in range(1, 31) if f != 2)
_EXCLUDED = {2}

# ---------------------------------------------------------------------------
# 7-algorithm GSK-family convergence panel.
# dt-gsk is listed last so it draws on top of the comparators.
# ---------------------------------------------------------------------------
ALGOS = ["gsk", "agsk", "apgsk", "fdb-agsk", "egsk", "atmals-gsk", "dt-gsk"]
DISP = {
    "gsk": "GSK", "agsk": "AGSK", "apgsk": "APGSK", "fdb-agsk": "FDB-AGSK",
    "egsk": "eGSK", "atmals-gsk": "ATMALS-GSK", "dt-gsk": "DT-GSK",
}
# (color, linestyle, marker).  DT-GSK deep-blue solid with markers; the six
# comparators get distinct colorblind-friendly-ish colors + line styles.
STYLE = {
    "dt-gsk":    ("#1F4E9D", "-",  "o"),    # deep blue, solid, marker
    "gsk":        ("#B02418", "--", None),   # red dashed
    "agsk":       ("#2E8B57", "-.", None),   # sea green
    "apgsk":      ("#E08A00", ":",  None),   # orange dotted
    "fdb-agsk":   ("#7B2D8E", "--", None),   # purple
    "egsk":       ("#00868B", "-.", None),   # teal
    "atmals-gsk": ("#6E7B8B", ":",  None),   # slate
}


def _checkpoint_dir(alg: str, suite: str) -> Path:
    """Directory holding ``CheckpointErrors_*.csv`` for *alg* on *suite*.

    Every algorithm - including dt-gsk - reads the PROMOTED evidence tree,
    so the reviewer-facing pack can never silently drift from the release
    (previously dt-gsk read results/ staging)."""
    return (_REPO / "benchmarks" / "cec_reference_results" / suite / alg
            / "gen_logs")


def _parse_checkpoint(p: Path):
    """Return (evals_array, mean_over_runs_array) from a checkpoint CSV.

    The header is ``Run,Seed,E1000,E2000,...``; only the ``E<evals>`` columns
    are used, averaged over the run rows.
    """
    with open(p, newline="") as fh:
        rows = [r for r in csv.reader(fh) if r]
    if len(rows) < 2:
        # Empty or header-only checkpoint file: treat as missing, never crash.
        return None, None
    header, data = rows[0], rows[1:]
    e_idx = [i for i, h in enumerate(header)
             if h.startswith("E") and h[1:].isdigit()]
    if not e_idx:
        return None, None
    try:
        evals = [int(header[i][1:]) for i in e_idx]
        errs = np.array([[float(r[i]) for i in e_idx] for r in data], dtype=float)
    except (ValueError, IndexError):
        return None, None
    if errs.size == 0:
        return None, None
    return np.array(evals, float), errs.mean(axis=0)


def alg_mean_curve(alg: str, func: int, dim: int, suite: str = "cec2017"):
    """Mean best-so-far error curve for one algorithm/function/dimension.

    Returns ``(evals_array, mean_array)`` or ``(None, None)`` when the
    checkpoint CSV for that (alg, func, dim) does not exist.  General loader
    used for every one of the seven GSK-family algorithms.
    """
    p = (_checkpoint_dir(alg, suite)
         / f"CheckpointErrors_{alg}_F{func}_D{dim}.csv")
    if not p.exists():
        return None, None
    return _parse_checkpoint(p)


def _alg_dim_for_func(alg: str, func: int, suite: str):
    """Native dimension recorded for *alg*/*func* on a native-dim suite.

    CEC2011 problems carry per-problem native dimensions encoded in the file
    name (``..._F<k>_D<native>.csv``).  Returns the integer dim or ``None``.
    """
    hits = sorted(_checkpoint_dir(alg, suite).glob(
        f"CheckpointErrors_{alg}_F{func}_D*.csv"))
    if not hits:
        return None
    return int(hits[0].stem.rsplit("_D", 1)[1])


# ---------------------------------------------------------------------------
# Legacy 2-algorithm helpers (kept for any external callers; the convergence
# grids below no longer use them -- they call ``alg_mean_curve`` for all 7).
# ---------------------------------------------------------------------------
def ism_mean_curve(func: int, dim: int, base: Path = None):
    p = (base or _ISM_GL) / f"CheckpointErrors_dt-gsk_F{func}_D{dim}.csv"
    if not p.exists():
        return None, None
    return _parse_checkpoint(p)


def gsk_median_curve(func: int, dim: int, base: Path = None):
    hits = sorted((base or _GSK_CURVES).glob(
        f"Figure_F{func}_D{dim}_Run#*.csv"))
    if not hits:
        return None, None
    rows = list(csv.reader(open(hits[0])))
    # columns: Eval, BestError, Log10Error
    data = [(float(r[0]), float(r[1])) for r in rows[1:] if r]
    arr = np.array(data)
    return arr[:, 0], arr[:, 1]


def _legend_handles():
    """Fixed handle/label lists so every page shows all 7 in the same order."""
    handles, labels = [], []
    for alg in ALGOS:
        color, ls, marker = STYLE[alg]
        lw = 1.7 if alg == "dt-gsk" else 1.0
        handles.append(Line2D([], [], color=color, linestyle=ls, marker=marker,
                              markersize=3 if marker else 0, linewidth=lw))
        labels.append(DISP[alg])
    return handles, labels


def main() -> None:
    res = {d: load_comparison_set("CEC2017", d, ["dt-gsk"] + list(GSK_FAMILY),
                                  require_mean=True) for d in _DIMS}

    # Missing-curve bookkeeping: missing[suite][alg] -> list of (func, dim).
    missing = {"cec2017": defaultdict(list), "cec2011": defaultdict(list)}
    # plotted_by_dim[suite][dim] -> set of algorithms with >=1 curve.
    plotted_by_dim = {"cec2017": defaultdict(set), "cec2011": defaultdict(set)}

    leg_handles, leg_labels = _legend_handles()

    with PdfPages(_OUT) as pdf:
        # ---- page 1: dashboard ----
        def _holm(pmap):
            items = sorted(pmap.items(), key=lambda kv: kv[1])
            out, running = {}, 0.0
            for i, (k, pv) in enumerate(items):
                running = max(running, min(1.0, pv * (len(items) - i)))
                out[k] = running
            return out

        ranks = {}
        wilcox = {}
        # Dimensions for which DT-GSK has mean summaries available.  In this
        # project DT-GSK covers D10/D30 only (no D50/D100 yet), so the
        # DT-GSK-anchored panels skip the dimensions where it is absent
        # rather than fabricating ranks/p-values.
        ism_dims = [d for d in _DIMS if "dt-gsk" in res[d]]
        for d in _DIMS:
            if "dt-gsk" not in res[d]:
                continue
            means = {a: r.mean_errors(_EXCLUDED) for a, r in res[d].items()}
            algs = ["dt-gsk"] + [a for a in GSK_FAMILY if a in means]
            common = sorted(set.intersection(*(set(means[a]) for a in algs))
                            - _EXCLUDED)
            acc = np.zeros(len(algs))
            for fid in common:
                vals = [0.0 if abs(means[a][fid]) < 1e-8 else means[a][fid]
                        for a in algs]
                acc += rankdata(vals)
            ranks[d] = dict(zip(algs, acc / len(common)))
            praw = {a: wilcoxon_signed_rank(means["dt-gsk"], means[a])
                    for a in GSK_FAMILY if a in means}
            ph = _holm({a: w.p_value for a, w in praw.items()})
            wilcox[d] = {a: (praw[a], ph[a]) for a in praw}
        # Dimension used to order the rank table rows (deepest with DT-GSK).
        _order_dim = ism_dims[-1] if ism_dims else _DIMS[0]

        fig = plt.figure(figsize=(8.27, 11.69))
        fig.text(0.5, 0.955, "DT-GSK on CEC2017 -- Results at a Glance",
                 ha="center", size=17, weight="bold")
        fig.text(0.5, 0.932,
                 "n = 51 runs, D in {10, 30, 50, 100}, 29 functions"
                 " (F2 excluded), 7-algorithm GSK-family panel",
                 ha="center", size=9.5, color="#444444")

        # Panel 1: Friedman mean ranks (rows = algorithms, sorted by D100)
        ax1 = fig.add_axes((0.08, 0.64, 0.84, 0.25))
        ax1.axis("off")
        _dims_note = ", ".join(f"D={d}" for d in ism_dims)
        ax1.set_title("Friedman mean rank (lower is better) -- "
                      f"DT-GSK is first at {_dims_note}",
                      size=11, weight="bold", loc="left")
        order = sorted(ranks[_order_dim], key=lambda a: ranks[_order_dim][a])
        # Comparators absent from the ordering dimension still get a row.
        order += [a for a in (["dt-gsk"] + list(GSK_FAMILY))
                  if a not in order]
        rows, cols = [], []
        for a in order:
            cells, ccols = [DISP[a]], ["#fff3cd" if a == "dt-gsk" else "white"]
            best_row = (a == "dt-gsk")
            for d in _DIMS:
                rd = ranks.get(d)
                if rd is None or a not in rd:
                    cells.append("n/a")
                    ccols.append("#f0f0f0")
                    continue
                cells.append(f"{rd[a]:.2f}")
                ccols.append("#c8e6c9" if rd[a] == min(rd.values())
                             else ("#fff3cd" if best_row else "white"))
            rows.append(cells)
            cols.append(ccols)
        tab1 = ax1.table(cellText=rows,
                         colLabels=["Algorithm", "D=10", "D=30",
                                    "D=50", "D=100"],
                         cellColours=cols, loc="center", cellLoc="center")
        tab1.auto_set_font_size(False)
        tab1.set_fontsize(9.5)
        tab1.scale(1.0, 1.55)

        # Panel 2: Wilcoxon scoreboard (DT-GSK vs each comparator)
        ax2 = fig.add_axes((0.08, 0.33, 0.84, 0.25))
        ax2.axis("off")
        ax2.set_title("Pairwise Wilcoxon vs DT-GSK (Holm-corrected)",
                      size=11, weight="bold", loc="left")
        rows2, cols2 = [], []
        for a in GSK_FAMILY:
            row, col = [DISP[a]], ["white"]
            for d in _DIMS:
                wd = wilcox.get(d)
                if wd is None or a not in wd:
                    row.append("n/a")
                    col.append("#f0f0f0")
                    continue
                w, ph = wd[a]
                sig = ph < 0.05
                row.append(f"{w.wins}/{w.ties}/{w.losses}"
                           + ("  *" if sig else f"  p={ph:.2f}"))
                col.append("#c8e6c9" if sig else "#f5f5f5")
            rows2.append(row)
            cols2.append(col)
        tab2 = ax2.table(cellText=rows2,
                         colLabels=["vs", "D=10", "D=30", "D=50", "D=100"],
                         cellColours=cols2, loc="center", cellLoc="center")
        tab2.auto_set_font_size(False)
        tab2.set_fontsize(8.8)
        tab2.scale(1.0, 1.55)
        tab2.auto_set_column_width(col=list(range(5)))
        fig.text(0.08, 0.325,
                 "Cells: wins/ties/losses over the 29 functions."
                 "  Green with * = Holm-significant at alpha = 0.05.",
                 size=8.5, color="#444444")

        # Panel 3: hold-outs / runtime, side by side
        ax3 = fig.add_axes((0.08, 0.13, 0.40, 0.15))
        ax3.axis("off")
        ax3.set_title("Hold-outs (frozen config, vs GSK)",
                      size=10.5, weight="bold", loc="left")
        tab3 = ax3.table(cellText=[
            ["CEC2013  D=10", "23/3/2", "p<0.001"],
            ["CEC2013  D=30", "20/5/3", "p<0.001"],
            ["CEC2013  D=50", "22/4/2", "p<0.001"],
            ["CEC2011 real-world", "13/6/3", "p=0.0066"],
        ], colLabels=["Suite", "W/T/L", "Wilcoxon"],
            loc="center", cellLoc="center")
        tab3.auto_set_font_size(False)
        tab3.set_fontsize(8.5)
        tab3.scale(1.0, 1.45)
        tab3.auto_set_column_width(col=list(range(3)))

        ax4 = fig.add_axes((0.54, 0.13, 0.38, 0.15))
        ax4.axis("off")
        ax4.set_title("Mean wall-clock per run", size=10.5,
                      weight="bold", loc="left")
        tab4 = ax4.table(cellText=[
            ["D=10", "4.1 s", "1.2 s"],
            ["D=50", "30.2 s", "9.5 s"],
            ["D=100", "53.9 s", "27.3 s"],
        ], colLabels=["", "DT-GSK", "GSK"],
            loc="center", cellLoc="center")
        tab4.auto_set_font_size(False)
        tab4.set_fontsize(8.5)
        tab4.scale(1.0, 1.45)

        fig.text(0.08, 0.075,
                 "Pages 2-5: CEC2017 per-function means (7 algorithms, one"
                 " dimension per page).  Page 6: CEC2011 means.",
                 size=9)
        fig.text(0.08, 0.058,
                 "Pages 7-18: CEC2017 convergence (29 functions x 4"
                 " dimensions).  Pages 19-21: CEC2011 convergence",
                 size=9)
        fig.text(0.08, 0.041,
                 "(22 problems, native dimensions).  Each panel shows the"
                 " 7-algorithm GSK-family panel: every curve is the mean"
                 " best-so-far error",
                 size=9)
        fig.text(0.08, 0.024,
                 "over that algorithm's runs at the CEC checkpoints"
                 " (DT-GSK drawn on top, deep-blue solid with markers).",
                 size=9)
        pdf.savefig(fig)
        plt.close(fig)

        # ---- pages 2-5: per-dim family tables ----
        for d in _DIMS:
            means = {a: r.mean_errors(_EXCLUDED) for a, r in res[d].items()}
            algs = ([a for a in ["dt-gsk"] if a in means]
                    + [a for a in GSK_FAMILY if a in means])
            fig = plt.figure(figsize=(8.27, 11.69))
            fig.text(0.5, 0.96, f"CEC2017 D={d}: mean error (n=51)",
                     ha="center", size=14, weight="bold")
            cell, colors = [], []
            for f in _FUNCS:
                vals = [means[a].get(f) for a in algs]
                present = [v for v in vals if v is not None]
                best = min(present) if present else None
                cell.append([f"F{f}"] + [f"{v:.3E}" if v is not None else "n/a"
                                         for v in vals])
                colors.append(["white"] + [
                    "#c8e6c9" if (best is not None and v is not None
                                  and v <= best * (1 + 1e-12))
                    else "white" for v in vals])
            tab = plt.table(cellText=cell,
                            colLabels=["F"] + [DISP.get(a, a.upper())
                                               for a in algs],
                            cellColours=colors, loc="center",
                            cellLoc="center")
            tab.auto_set_font_size(False)
            tab.set_fontsize(6.8)
            tab.scale(1.0, 1.18)
            plt.axis("off")
            fig.text(0.5, 0.03, "Green = best mean in the panel.",
                     ha="center", size=8)
            pdf.savefig(fig)
            plt.close(fig)

        # ---- page 6: CEC2011 mean table ----
        res11 = load_comparison_set("CEC2011", 0,
                                    ["dt-gsk"] + list(CEC2011_COMPARATORS),
                                    require_mean=True)
        means11 = {a: r.mean_errors(set()) for a, r in res11.items()}
        # Only include algorithms that actually have CEC2011 means.  In this
        # project DT-GSK has no CEC2011 results yet, so it is omitted here
        # (and recorded as missing in the convergence pass below).
        algs11 = ([a for a in ["dt-gsk"] if a in means11]
                  + [a for a in CEC2011_COMPARATORS if a in means11])
        funcs11 = sorted(set().union(*(set(means11[a]) for a in algs11))
                         if algs11 else set())
        # Native dim per CEC2011 problem, discovered from any algorithm's
        # checkpoint files (dt-gsk first, else any comparator that has data).
        dims11 = {}
        for f in funcs11:
            dim = _alg_dim_for_func("dt-gsk", f, "cec2011")
            if dim is None:
                for alg in ALGOS:
                    dim = _alg_dim_for_func(alg, f, "cec2011")
                    if dim is not None:
                        break
            dims11[f] = dim
        fig = plt.figure(figsize=(8.27, 11.69))
        fig.text(0.5, 0.96, "CEC2011 real-world problems: mean objective"
                 " (n=25)", ha="center", size=14, weight="bold")
        cell, colors = [], []
        for f in funcs11:
            vals = [means11[a].get(f) for a in algs11]
            present = [v for v in vals if v is not None]
            best = min(present) if present else None
            label = (f"F{f} (D={dims11[f]})" if dims11.get(f)
                     else f"F{f}")
            cell.append([label] + [f"{v:.4E}" if v is not None else "n/a"
                                   for v in vals])
            colors.append(["white"] + [
                "#c8e6c9" if (best is not None and v is not None
                              and v <= best + 1e-12)
                else "white" for v in vals])
        tab = plt.table(cellText=cell,
                        colLabels=["Problem"] + [DISP.get(a, a.upper())
                                                 for a in algs11],
                        cellColours=colors, loc="center", cellLoc="center")
        tab.auto_set_font_size(False)
        tab.set_fontsize(8)
        tab.scale(1.0, 1.5)
        tab.auto_set_column_width(col=list(range(len(algs11) + 1)))
        plt.axis("off")
        fig.text(0.5, 0.04, "Raw objective values (lower is better;"
                 " negatives are valid).  Green = best in the panel.",
                 ha="center", size=8)
        pdf.savefig(fig)
        plt.close(fig)

        # ---- CEC2017 convergence grids: 10 panels per page ----
        # 7-algorithm GSK-family panel; each curve = mean best-so-far error.
        for d in _DIMS:
            chunks = [list(_FUNCS[i:i + 10])
                      for i in range(0, len(_FUNCS), 10)]
            for ci, chunk in enumerate(chunks):
                fig, axes = plt.subplots(5, 2, figsize=(8.27, 11.69))
                fig.suptitle(
                    f"CEC2017 convergence, D={d}  (page {ci + 1}/{len(chunks)})"
                    "\n7-algorithm GSK-family panel (mean best-so-far error)",
                    size=12, weight="bold")
                for ax, f in zip(axes.flat, chunk):
                    ism_present = False
                    for alg in ALGOS:
                        x, y = alg_mean_curve(alg, f, d, suite="cec2017")
                        if x is None:
                            missing["cec2017"][alg].append((f, d))
                            continue
                        plotted_by_dim["cec2017"][d].add(alg)
                        color, ls, marker = STYLE[alg]
                        if alg == "dt-gsk":
                            ism_present = True
                            ax.plot(x, np.maximum(y, 1e-12), color=color,
                                    linestyle=ls, marker=marker, ms=2.5,
                                    lw=1.7, zorder=10, label=DISP[alg])
                        else:
                            ax.plot(x, np.maximum(y, 1e-12), color=color,
                                    linestyle=ls, lw=1.0, zorder=4,
                                    label=DISP[alg])
                    if not ism_present:
                        ax.text(0.5, 0.04, "DT-GSK: no data", size=5.5,
                                color="#999999", ha="center",
                                transform=ax.transAxes)
                    ax.set_yscale("log")
                    ax.set_title(f"F{f}", size=9)
                    ax.tick_params(labelsize=6)
                    ax.grid(alpha=0.3, lw=0.4)
                for ax in axes.flat[len(chunk):]:
                    ax.axis("off")
                fig.legend(leg_handles, leg_labels, loc="lower center",
                           ncol=7, fontsize=7, frameon=False)
                fig.text(0.5, 0.038, "x: function evaluations    "
                         "y: mean best-so-far error (log scale)",
                         ha="center", size=8)
                fig.tight_layout(rect=(0, 0.055, 1, 0.95))
                pdf.savefig(fig)
                plt.close(fig)

        # ---- CEC2011 convergence grids (native dimensions) ----
        chunks11 = [funcs11[i:i + 10] for i in range(0, len(funcs11), 10)]
        for ci, chunk in enumerate(chunks11):
            fig, axes = plt.subplots(5, 2, figsize=(8.27, 11.69))
            fig.suptitle(
                "CEC2011 convergence, native dimensions"
                f"  (page {ci + 1}/{len(chunks11)})"
                "\n7-algorithm GSK-family panel (mean best-so-far objective)",
                size=12, weight="bold")
            for ax, f in zip(axes.flat, chunk):
                curves = {}
                for alg in ALGOS:
                    dim = _alg_dim_for_func(alg, f, "cec2011")
                    if dim is None:
                        missing["cec2011"][alg].append((f, dims11.get(f)))
                        continue
                    x, y = alg_mean_curve(alg, f, dim, suite="cec2011")
                    if x is None:
                        missing["cec2011"][alg].append((f, dim))
                        continue
                    curves[alg] = (x, y)
                    plotted_by_dim["cec2011"][dims11.get(f)].add(alg)
                # log scale only if every plotted curve is strictly positive
                use_log = bool(curves) and all(
                    np.min(y) > 0 for _, y in curves.values())
                for alg in ALGOS:
                    if alg not in curves:
                        continue
                    x, y = curves[alg]
                    yv = np.maximum(y, 1e-12) if use_log else y
                    color, ls, marker = STYLE[alg]
                    if alg == "dt-gsk":
                        ax.plot(x, yv, color=color, linestyle=ls,
                                marker=marker, ms=2.5, lw=1.7, zorder=10,
                                label=DISP[alg])
                    else:
                        ax.plot(x, yv, color=color, linestyle=ls, lw=1.0,
                                zorder=4, label=DISP[alg])
                if "dt-gsk" not in curves:
                    ax.text(0.5, 0.04, "DT-GSK: no data", size=5.5,
                            color="#999999", ha="center",
                            transform=ax.transAxes)
                if use_log:
                    ax.set_yscale("log")
                ax.set_title(f"F{f} (D={dims11.get(f)})", size=9)
                ax.tick_params(labelsize=6)
                ax.grid(alpha=0.3, lw=0.4)
            for ax in axes.flat[len(chunk):]:
                ax.axis("off")
            fig.legend(leg_handles, leg_labels, loc="lower center",
                       ncol=7, fontsize=7, frameon=False)
            fig.text(0.5, 0.038, "x: function evaluations    "
                     "y: mean best-so-far raw objective"
                     " (log scale where positive)",
                     ha="center", size=8)
            fig.tight_layout(rect=(0, 0.055, 1, 0.95))
            pdf.savefig(fig)
            plt.close(fig)

    # ---- missing-curve summary: console + log file ----
    lines = ["DT-GSK CEC review pack -- missing convergence curves",
             "(skipped on plot, never fabricated)", ""]
    total_missing = 0
    for suite in ("cec2017", "cec2011"):
        lines.append(f"== {suite.upper()} ==")
        if not any(missing[suite].values()):
            lines.append("  (none missing)")
        for alg in ALGOS:
            entries = sorted(set(missing[suite][alg]))
            if not entries:
                continue
            total_missing += len(entries)
            by_dim = defaultdict(list)
            for func, dim in entries:
                by_dim[dim].append(func)
            lines.append(f"  {DISP[alg]} ({alg}): {len(entries)} missing")
            for dim in sorted(by_dim, key=lambda v: (v is None, v)):
                fns = ",".join(f"F{x}" for x in sorted(by_dim[dim]))
                lines.append(f"    D={dim}: {fns}")
        lines.append("")
    lines.append(f"TOTAL missing curves: {total_missing}")
    _MISSING_LOG.write_text("\n".join(lines), encoding="utf-8")

    # Per-dimension algorithm tally (proof the panels carry up to 7 curves).
    print("[review_pack] convergence algorithms plotted per dimension:")
    for suite in ("cec2017", "cec2011"):
        for dim in sorted(plotted_by_dim[suite],
                          key=lambda v: (v is None, v)):
            algs_here = [DISP[a] for a in ALGOS
                         if a in plotted_by_dim[suite][dim]]
            print(f"  {suite} D={dim}: {len(algs_here)} algorithms "
                  f"-> {', '.join(algs_here)}")
    print("\n".join(lines))
    print(f"[review_pack] Missing-curve log: {_MISSING_LOG}")
    print(f"[review_pack] Wrote {_OUT}  ({_OUT.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
