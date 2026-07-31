"""Generate DT-GSK adaptive-parameter trace figures for the paper.

Reads the per-generation CSV emitted by ``scripts/run_ism_gsk_variants.py
--write-gen-logs`` and produces two publication-quality PDFs:

  * Figure A (``ace_probability_F14_D10.pdf``):
      ACE entry selection probability evolution over generations.
      One line per pool entry.
  * Figure B (``accept_diversity_F14_D10.pdf``):
      Acceptance rate (solid, left axis) and diversity radius (dashed,
      right axis) over generations.

The canonical CSV for the headline variant on CEC 2017 F14 at D=10 lives
at:

    results/dt-gsk/dt-gsk/cec2017/gen_logs/GenLog_dt-gsk_F14_D10_Run1.csv

Regenerate via::

    python run.py --suite CEC2017 --runs 51 --alg dt-gsk --dims 10 --gen-logs
    python papers/scripts/generate_trace_figures.py

Both PDFs are 5.4 x 3.2 inches (single-column friendly), with a
colour-blind-safe palette (Paul Tol bright).
"""
from __future__ import annotations

import ast
import csv
from pathlib import Path

import numpy as np

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
except ImportError as exc:  # pragma: no cover - only for local builds
    raise SystemExit(
        "matplotlib is required for paper figure regeneration; "
        f"install via `pip install matplotlib` ({exc})"
    )


_REPO = Path(__file__).resolve().parents[2]
# Prefer the canonical suite-partitioned layout, then legacy locked/flat
# locations from older artifact snapshots.
_CANDIDATES = (
    _REPO / "results" / "dt-gsk" / "dt-gsk" / "cec2017"
          / "gen_logs" / "GenLog_dt-gsk_F14_D10_Run1.csv",
    _REPO / "results" / "dt-gsk" / "pub-lock-sgsm-adaptive" / "cec2017"
          / "gen_logs" / "GenLog_pub-lock-sgsm-adaptive_F14_D10_Run1.csv",
    _REPO / "results" / "dt-gsk" / "gen_logs"
          / "GenLog_dt-gsk_F14_D10_Run1.csv",
)
_CSV = next((p for p in _CANDIDATES if p.exists()), _CANDIDATES[-1])
_OUT_DIR = Path(__file__).resolve().parents[1] / "figures" / "traces"
_OUT_ACE = _OUT_DIR / "ace_probability_F14_D10.pdf"
_OUT_ACC = _OUT_DIR / "accept_diversity_F14_D10.pdf"

# Paul Tol "bright" qualitative palette (colour-blind-safe).
_TOL_BRIGHT = (
    "#4477AA",  # blue
    "#EE6677",  # red
    "#228833",  # green
    "#CCBB44",  # yellow
    "#66CCEE",  # cyan
    "#AA3377",  # purple
    "#BBBBBB",  # grey
)


def _parse_tuple(cell: str) -> tuple[float, ...]:
    """Parse a ``"(p1, p2, ...)"``-encoded cell via ast.literal_eval."""
    if not cell:
        return ()
    val = ast.literal_eval(cell)
    return tuple(float(x) for x in val)


def _load_series(path: Path) -> dict[str, np.ndarray]:
    """Read the needed columns out of the gen-log CSV.

    Returns a dict with keys ``gen``, ``acceptance_rate``,
    ``diversity_radius``, ``ace_probs`` (2-D, shape ``(T, K)``).
    """
    gens: list[int] = []
    acc: list[float] = []
    div: list[float] = []
    probs: list[tuple[float, ...]] = []

    with path.open("r", encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            gens.append(int(row["gen"]))
            acc.append(float(row["acceptance_rate"]))
            div.append(float(row["diversity_radius"]))
            probs.append(_parse_tuple(row["ace_probs"]))

    if not gens:
        raise SystemExit(f"gen-log CSV has no data rows: {path}")

    # Coerce the ragged probability tuples into a dense 2-D array.
    k = max(len(p) for p in probs)
    probs_arr = np.full((len(probs), k), np.nan, dtype=float)
    for i, p in enumerate(probs):
        probs_arr[i, : len(p)] = p

    return {
        "gen": np.asarray(gens, dtype=int),
        "acceptance_rate": np.asarray(acc, dtype=float),
        "diversity_radius": np.asarray(div, dtype=float),
        "ace_probs": probs_arr,
    }


def _plot_ace_probs(data: dict[str, np.ndarray], out: Path) -> None:
    gen = data["gen"]
    probs = data["ace_probs"]
    k = probs.shape[1]

    fig, ax = plt.subplots(figsize=(5.4, 3.2))

    for i in range(k):
        color = _TOL_BRIGHT[i % len(_TOL_BRIGHT)]
        ax.plot(
            gen,
            probs[:, i],
            color=color,
            linewidth=1.1,
            label=f"entry {i + 1}",
        )

    ax.set_xlabel("Generation", fontsize=10)
    ax.set_ylabel("ACE selection probability", fontsize=10)
    ax.set_xlim(gen.min(), gen.max())
    ax.set_ylim(0.0, 1.0)
    ax.grid(True, linestyle=":", alpha=0.4)
    ax.legend(
        fontsize=7,
        loc="upper right",
        frameon=False,
        ncol=2,
        handlelength=1.5,
        columnspacing=0.9,
    )
    ax.tick_params(axis="both", labelsize=9)

    fig.tight_layout()
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    print(f"wrote {out}")


def _plot_accept_diversity(data: dict[str, np.ndarray], out: Path) -> None:
    gen = data["gen"]
    acc = data["acceptance_rate"]
    div = data["diversity_radius"]

    fig, ax_left = plt.subplots(figsize=(5.4, 3.2))
    ax_right = ax_left.twinx()

    color_acc = _TOL_BRIGHT[0]  # blue
    color_div = _TOL_BRIGHT[1]  # red

    (line_acc,) = ax_left.plot(
        gen,
        acc,
        color=color_acc,
        linewidth=1.1,
        linestyle="-",
        label="acceptance rate",
    )
    (line_div,) = ax_right.plot(
        gen,
        div,
        color=color_div,
        linewidth=1.1,
        linestyle="--",
        label="diversity radius",
    )

    ax_left.set_xlabel("Generation", fontsize=10)
    ax_left.set_ylabel("Acceptance rate", color=color_acc, fontsize=10)
    ax_right.set_ylabel("Diversity radius", color=color_div, fontsize=10)
    ax_left.tick_params(axis="y", colors=color_acc, labelsize=9)
    ax_right.tick_params(axis="y", colors=color_div, labelsize=9)
    ax_left.tick_params(axis="x", labelsize=9)

    ax_left.set_xlim(gen.min(), gen.max())
    ax_left.set_ylim(0.0, 1.0)
    # Right axis: pad the top so the dashed trace does not hug the frame.
    div_top = float(np.nanmax(div)) if np.any(np.isfinite(div)) else 1.0
    if div_top <= 0.0:
        div_top = 1.0
    ax_right.set_ylim(0.0, div_top * 1.05)

    ax_left.grid(True, linestyle=":", alpha=0.4)

    # Combined legend on a single handle pool.
    lines = [line_acc, line_div]
    labels = [line.get_label() for line in lines]
    ax_left.legend(
        lines,
        labels,
        fontsize=7,
        loc="upper right",
        frameon=False,
        handlelength=2.2,
    )

    fig.tight_layout()
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    print(f"wrote {out}")


def main() -> None:
    if not _CSV.exists():
        raise SystemExit(
            f"gen-log CSV not found: {_CSV}\n"
            "Regenerate it via `python run.py --suite CEC2017 --runs 51 "
            "--alg dt-gsk --dims 10 --gen-logs`."
        )

    _OUT_DIR.mkdir(parents=True, exist_ok=True)
    data = _load_series(_CSV)
    print(
        f"loaded {_CSV.name}: {len(data['gen'])} generations "
        f"(first={int(data['gen'][0])}, last={int(data['gen'][-1])}), "
        f"{data['ace_probs'].shape[1]} ACE entries"
    )
    _plot_ace_probs(data, _OUT_ACE)
    _plot_accept_diversity(data, _OUT_ACC)


if __name__ == "__main__":
    main()
