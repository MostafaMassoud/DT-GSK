"""Generate the ATMALS-style multi-panel adaptive-parameter figure.

Mirrors ATMALS-GSK 2025 Figure 11 (Figure 3 of A07): a single PDF with
six sub-panels showing the evolution of the headline DT-GSK adaptive
parameters over the CEC2017 D=10 benchmark, averaged across all 29
functions (F2 excluded) and 51 runs.  At D=10 the SGSM overlay does
not activate (the paper restricts SGSM to D >= 50), so panel (f)
c(t) carries the "not recorded" fallback rather than a real curve --
consistent with the scaffold-isolation narrative at D=10.

Panels
------
(a) K_eff(t)    - effective population size (pop_size)
(b) K_f(t)      - expected knowledge factor under the ACE selection
                  distribution (dot product of ACE probabilities with
                  the default ACE pool KF values)
(c) K_r(t)      - expected knowledge ratio (same idea for KR)
(d) P(t)        - BSE triple-trigger activation rate (fraction of
                  runs with ``restart_triggered == True``
                  at the given generation)
(e) P_LS(t)     - Nelder-Mead LS activation rate
                  (``local_search_triggered`` fraction)

At D=10 the SGSM overlay is inactive (it activates only at D >= 50),
so a c(t) confidence panel is not drawn --- the figure uses a
5-panel layout with the bottom row (d,e) centred.

Static parameters (those that DT-GSK does not adapt at any step) are
drawn as a horizontal constant line with a dashed style and a note in
the caption so the visual grid stays complete.

Output
------
    papers/figures/traces/adaptive_params_all_D10.pdf

Re-generate via::

    python papers/scripts/generate_adaptive_params_panel.py
"""
from __future__ import annotations

import ast
import csv
import re
from pathlib import Path

import numpy as np

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
except ImportError as exc:  # pragma: no cover
    raise SystemExit(
        "matplotlib is required; install via `pip install matplotlib` "
        f"({exc})"
    )


_REPO = Path(__file__).resolve().parents[2]
_OUT = _REPO / "papers" / "figures" / "traces" / "adaptive_params_all_D10.pdf"
# Headline GenLogs: prefer the canonical suite-partitioned paper layout.
_BULK_DIR = _REPO / "results" / "dt-gsk" / "dt-gsk" / "cec2017" / "gen_logs"
_LOCKED_DIR = _REPO / "results" / "dt-gsk" / "pub-lock-sgsm-adaptive" / \
              "cec2017" / "gen_logs"
_GEN_LOG_DIR = _BULK_DIR if _BULK_DIR.is_dir() else _LOCKED_DIR

_DIM = 10
_FUNC_IDS = tuple(f for f in range(1, 31) if f != 2)  # F2 excluded

# Default ACE pool from gsk/dt_gsk.py (5 entries: KF, KR, Kexp).  When
# ``ace_de_entry`` is True (the headline enables it at D>=20) a 6th
# entry is appended for DE; we tag that entry with KF=KR=NaN so the
# probability mass on the DE entry contributes zero to the expected
# KF/KR average but is not double-counted as GSK KF=0 / KR=0.
_ACE_POOL: tuple[tuple[float, float, float], ...] = (
    (0.1, 0.2, 2.0),
    (1.0, 0.1, 15.0),
    (0.5, 0.9, 10.0),
    (1.0, 0.9, 5.0),
    (0.5, 0.9, 3.0),
)
_KF_VALUES = np.asarray([kf for kf, _, _ in _ACE_POOL], dtype=float)
_KR_VALUES = np.asarray([kr for _, kr, _ in _ACE_POOL], dtype=float)

# Downsample all run time-series onto a common grid so we can average.
_GRID_POINTS = 200

# Colours follow ATMALS-GSK 2025 Figure 11: red dash-dot for the
# vanilla-GSK reference and blue dash-dot for the adaptive proposal.
_TRACE_COLOR = "#1F4E9D"   # deep blue — DT-GSK adaptive trace
_GSK_COLOR = "#D62728"      # tab:red — vanilla GSK horizontal baseline
_STATIC_COLOR = "#888888"  # legacy grey used for static-fallback panels

# Vanilla GSK parameter values (see gsk/gsk.py docstring: NP=100, KF=0.5,
# KR=0.9, K=10).  BSE restarts, Nelder-Mead LS triggers, and SGSM
# interaction-graph confidence do not exist in vanilla GSK, so those
# panels have no GSK baseline.
_GSK_POP_SIZE = 100.0
_GSK_KF = 0.5
_GSK_KR = 0.9


def _parse_tuple(cell: str) -> tuple[float, ...]:
    """Parse a ``"(p1, p2, ...)"``-encoded cell."""
    if not cell or cell in ("None", "none"):
        return ()
    try:
        val = ast.literal_eval(cell)
    except (ValueError, SyntaxError):
        return ()
    try:
        return tuple(float(x) for x in val)
    except (TypeError, ValueError):
        return ()


def _parse_bool_int(cell: str) -> int:
    """Parse a boolean-ish cell (True/False/1/0) to 0/1."""
    if not cell:
        return 0
    s = cell.strip().lower()
    if s in ("true", "1", "t"):
        return 1
    if s in ("false", "0", "f", ""):
        return 0
    try:
        return int(float(s))
    except ValueError:
        return 0


def _load_run_series(path: Path) -> dict[str, np.ndarray] | None:
    """Extract the columns we need from one GenLog CSV.

    Returns dict with arrays: budget_frac, pop_size, ace_probs (2D),
    restart_triggered, local_search_triggered,
    interaction_graph_overall_confidence.
    """
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            budget_frac: list[float] = []
            pop_size: list[float] = []
            ace_probs_rows: list[tuple[float, ...]] = []
            restart: list[int] = []
            ls_trig: list[int] = []
            conf: list[float] = []
            for row in reader:
                try:
                    budget_frac.append(float(row.get("budget_frac", 0.0)))
                except ValueError:
                    budget_frac.append(0.0)
                try:
                    pop_size.append(float(row.get("pop_size", 0.0)))
                except ValueError:
                    pop_size.append(0.0)
                ace_probs_rows.append(_parse_tuple(row.get("ace_probs", "")))
                restart.append(_parse_bool_int(row.get("restart_triggered", "0")))
                ls_trig.append(_parse_bool_int(row.get("local_search_triggered", "0")))
                try:
                    conf.append(float(row.get("interaction_graph_overall_confidence", 0.0)))
                except ValueError:
                    conf.append(0.0)
    except OSError:
        return None

    if not budget_frac:
        return None

    # Coerce ACE probs (may be empty / different length per row).
    k = max((len(p) for p in ace_probs_rows), default=0)
    if k == 0:
        ace_arr = np.zeros((len(budget_frac), 1), dtype=float)
    else:
        ace_arr = np.full((len(budget_frac), k), np.nan, dtype=float)
        for i, p in enumerate(ace_probs_rows):
            if p:
                ace_arr[i, : len(p)] = p

    return {
        "budget_frac":    np.asarray(budget_frac, dtype=float),
        "pop_size":       np.asarray(pop_size, dtype=float),
        "ace_probs":      ace_arr,
        "restart":        np.asarray(restart, dtype=float),
        "ls_trig":        np.asarray(ls_trig, dtype=float),
        "conf":           np.asarray(conf, dtype=float),
    }


def _aggregate_run(
    series: dict[str, np.ndarray],
    x_grid: np.ndarray,
) -> dict[str, np.ndarray]:
    """Interpolate one run's series onto ``x_grid`` (budget fraction).

    Returns per-metric 1D arrays on the common grid.  For ACE-derived
    metrics we compute the expected K_f / K_r by dotting the probability
    vector with the default pool's KF / KR values (first 5 entries; any
    probability mass on a DE entry (index 5 if present) is treated as
    non-GSK and re-normalised out of the expectation for visualisation).

    For sparse events (BSE triple trigger, LS trigger) we accumulate
    per-run cumulative activation counts so the mean-across-runs gives
    the expected cumulative number of activations up to ``x_grid[t]``.

    For the SGSM confidence we drop gens where the graph has not been
    refreshed (c == 0.0 with zero refreshes) to avoid flat-lining the
    inter-refresh zeros pulling the mean to the floor.
    """
    bf = series["budget_frac"]
    # Clamp grid to actual coverage
    bf_min = float(bf.min())
    bf_max = float(bf.max())
    if bf_max <= bf_min:
        bf_max = bf_min + 1e-9

    def _interp(y: np.ndarray, *, fill_edge: bool = True) -> np.ndarray:
        mask = np.isfinite(y)
        if not np.any(mask):
            return np.full_like(x_grid, np.nan, dtype=float)
        if fill_edge:
            return np.interp(
                x_grid, bf[mask], y[mask],
                left=y[mask][0], right=y[mask][-1],
            )
        return np.interp(
            x_grid, bf[mask], y[mask],
            left=np.nan, right=np.nan,
        )

    pop = _interp(series["pop_size"])

    # Sparse events — aggregate as *cumulative activation count* per run
    # so the eventual cross-run mean is a smooth proxy for the
    # activation *rate* curve.
    restart_cum = np.cumsum(series["restart"].astype(float))
    ls_cum = np.cumsum(series["ls_trig"].astype(float))
    restart = _interp(restart_cum)
    ls = _interp(ls_cum)

    # SGSM confidence — only include rows where confidence > 0 (i.e.
    # where the graph has actually been refreshed). The zero rows are
    # "no update this generation" rather than "confidence dropped to 0".
    conf_raw = series["conf"]
    conf_masked = np.where(conf_raw > 0.0, conf_raw, np.nan)
    # Forward-fill: carry the last non-NaN value forward so the grid
    # interpolation sees a continuous series reflecting the most
    # recent refresh's confidence.
    last = np.nan
    conf_ff = np.empty_like(conf_masked)
    for i, v in enumerate(conf_masked):
        if np.isfinite(v):
            last = v
        conf_ff[i] = last
    conf = _interp(conf_ff, fill_edge=True)

    # Expected KF / KR from the ACE probability distribution.
    ace = series["ace_probs"]
    K = ace.shape[1]
    k_gsk = min(K, _KF_VALUES.shape[0])
    gsk_probs = ace[:, :k_gsk]
    sums = np.nansum(gsk_probs, axis=1, keepdims=True)
    sums = np.where(sums > 0.0, sums, np.nan)
    norm_probs = gsk_probs / sums
    kf_exp = np.nansum(norm_probs * _KF_VALUES[:k_gsk], axis=1)
    kr_exp = np.nansum(norm_probs * _KR_VALUES[:k_gsk], axis=1)

    kf = _interp(kf_exp)
    kr = _interp(kr_exp)

    return {
        "pop_size": pop,
        "kf":       kf,
        "kr":       kr,
        "restart":  restart,
        "ls":       ls,
        "conf":     conf,
    }


def _aggregate_all() -> dict[str, np.ndarray]:
    """Scan every GenLog for D=50 across F1..F30 (F2 excluded) and 51 runs.

    Returns dict keyed by metric name with arrays on the shared grid
    (averaged across all runs).
    """
    x_grid = np.linspace(0.0, 1.0, _GRID_POINTS)
    stacks: dict[str, list[np.ndarray]] = {
        k: [] for k in ("pop_size", "kf", "kr", "restart", "ls", "conf")
    }

    # Pattern: GenLog_{alg}_F<k>_D{_DIM}_Run<n>.csv — alg is either "dt-gsk"
    # (bulk runs) or "pub-lock-sgsm-adaptive" (SGSM-enabled trace run).
    pattern = re.compile(
        rf"GenLog_(?:dt-gsk|pub-lock-sgsm-adaptive)_F(\d+)_D{_DIM}_Run(\d+)\.csv"
    )

    n_loaded = 0
    # Broad glob: any GenLog_<alg>_F*_D{_DIM}_Run*.csv; re-filter against
    # the per-alg pattern below so non-DT-GSK runs (if any) are skipped.
    for path in sorted(_GEN_LOG_DIR.glob(f"GenLog_*_F*_D{_DIM}_Run*.csv")):
        m = pattern.match(path.name)
        if m is None:
            continue
        fid = int(m.group(1))
        if fid not in _FUNC_IDS:
            continue
        series = _load_run_series(path)
        if series is None:
            continue
        aggregated = _aggregate_run(series, x_grid)
        for key, arr in aggregated.items():
            stacks[key].append(arr)
        n_loaded += 1

    if n_loaded == 0:
        raise SystemExit(
            f"No D={_DIM} GenLog CSVs found under {_GEN_LOG_DIR}. "
            "Run the headline variant with --write-gen-logs first."
        )
    print(f"Loaded {n_loaded} GenLog files across {len(_FUNC_IDS)} functions.")

    means = {k: np.nanmean(np.vstack(v), axis=0) for k, v in stacks.items()}
    means["x_grid"] = x_grid
    means["n_loaded"] = n_loaded
    return means


def _plot_panel(
    ax,
    x: np.ndarray,
    y: np.ndarray,
    title: str,
    ylabel: str,
    *,
    gsk_baseline: float | None = None,
    is_static: bool = False,
    static_note: str = "",
) -> None:
    """Draw one ATMALS-Fig-11 parameter-trace subpanel.

    ``gsk_baseline`` is a scalar vanilla-GSK value drawn as a red
    dash-dot horizontal reference line (labelled "GSK" in the legend);
    pass ``None`` for panels with no GSK analogue (BSE, LS, SGSM).
    """
    if is_static:
        const = float(np.nanmean(y))
        ax.axhline(
            const, color=_STATIC_COLOR, linestyle="--", linewidth=1.2,
            label=f"static = {const:.3g}",
        )
        ax.text(0.5, 0.9, static_note, transform=ax.transAxes,
                ha="center", fontsize=7, color=_STATIC_COLOR)
    else:
        # Red dash-dot GSK reference line first (behind the DT-GSK trace).
        if gsk_baseline is not None:
            ax.axhline(
                gsk_baseline,
                color=_GSK_COLOR, linestyle="-.", linewidth=1.3,
                label="GSK",
            )
        ax.plot(
            x, y,
            color=_TRACE_COLOR, linewidth=1.4, linestyle="-.",
            label="DT-GSK",
        )
    ax.set_title(title, fontsize=10, fontweight="bold")
    ax.set_xlabel("NFE budget (fraction)", fontsize=8)
    ax.set_ylabel(ylabel, fontsize=8, fontstyle="italic")
    ax.tick_params(axis="both", labelsize=7)
    ax.grid(True, which="major", axis="y", linestyle=":", alpha=0.35)
    ax.set_axisbelow(True)
    # Per-subplot boxed legend at upper-right, matching ATMALS Fig 11.
    ax.legend(
        loc="upper right", frameon=True, fontsize=7,
        edgecolor="#333333", framealpha=0.95,
    )


def main() -> None:
    data = _aggregate_all()

    # 5-panel layout: top row (a,b,c) over 3 equal columns, bottom row
    # (d,e) centred — the former panel (f) c(t) SGSM confidence is
    # omitted because the SGSM overlay is inactive at D=10 (it
    # activates only at D >= 50).  The GridSpec uses a 6-column grid
    # so the two bottom panels (cols 1:3 and 3:5) sit symmetrically
    # under the three top panels (cols 0:2, 2:4, 4:6).
    from matplotlib import gridspec

    fig = plt.figure(figsize=(12.0, 5.8))
    gs = gridspec.GridSpec(2, 6, figure=fig)
    ax_a = fig.add_subplot(gs[0, 0:2])
    ax_b = fig.add_subplot(gs[0, 2:4])
    ax_c = fig.add_subplot(gs[0, 4:6])
    ax_d = fig.add_subplot(gs[1, 1:3])
    ax_e = fig.add_subplot(gs[1, 3:5])
    x = data["x_grid"]

    _plot_panel(
        ax_a, x, data["pop_size"],
        r"(a) $K_{eff}(t)$", r"$K_{eff}$",
        gsk_baseline=_GSK_POP_SIZE,
    )
    # K_f and K_r come from ACE expectation so they are genuinely
    # time-varying over the headline; vanilla GSK uses fixed KF=0.5,
    # KR=0.9 which we plot as horizontal red dash-dot baselines.
    _plot_panel(
        ax_b, x, data["kf"],
        r"(b) $K_F(t)$", r"$K_F$",
        gsk_baseline=_GSK_KF,
    )
    _plot_panel(
        ax_c, x, data["kr"],
        r"(c) $K_R(t)$", r"$K_R$",
        gsk_baseline=_GSK_KR,
    )
    # BSE restarts and LS triggers have no vanilla-GSK analogue —
    # ATMALS-style plots draw a red dash-dot at y=0 to show "GSK never
    # triggers" while the DT-GSK trace rises above it.
    _plot_panel(
        ax_d, x, data["restart"],
        r"(d) $P(t)$  BSE cumulative activations",
        r"$P$ (mean restarts / run)",
        gsk_baseline=0.0,
    )
    _plot_panel(
        ax_e, x, data["ls"],
        r"(e) $P_{LS}(t)$  LS cumulative activations",
        r"$P_{LS}$ (mean triggers / run)",
        gsk_baseline=0.0,
    )

    fig.suptitle(
        f"DT-GSK adaptive parameter traces  CEC2017 D={_DIM}  "
        f"(n={data['n_loaded']} run-function pairs)",
        fontsize=11, y=1.02,
    )
    _OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(_OUT, bbox_inches="tight")
    plt.close(fig)
    print(f"wrote {_OUT}")


if __name__ == "__main__":
    main()
