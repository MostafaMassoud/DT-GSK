"""Generate the NLPSR analytic schedule trajectory (fig:nlpsr-schedule).

ANALYTIC PLOT ONLY (exhibit F-NLPSR, phase_04/exhibit_plan.csv): a closed-form
evaluation of the frozen E5 schedule from
``phase_03/equation_registry.csv`` (row E5) at the tier floors of
``phase_03/parameter_table.md`` -- NO empirical source, no result file read,
no live run:

    NP(x) = NP_init + (N_min - NP_init) * x^(1-x),   x = t / MaxFES

Tier settings plotted (frozen ``pub`` profile): NP_init = 5D for
D in {10, 30, 50, 100}; N_min = 12 below D50 (bare floor) and 25 at D >= 50
(tier floor). The conventional linear LPSR schedule is shown for reference.

Outputs (deterministic filenames, vector PDF primary + PNG >= 200 dpi):
    papers/figures/concept/fig_nlpsr_schedule.pdf
    papers/figures/concept/fig_nlpsr_schedule.png
"""
from __future__ import annotations

from pathlib import Path

import numpy as np

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import _fig_style
    _fig_style.apply()
except ImportError as exc:  # pragma: no cover - only for local builds
    raise SystemExit(
        "matplotlib is required for paper figure regeneration; "
        f"install via `pip install matplotlib` ({exc})"
    )

OUT_DIR = Path(__file__).resolve().parents[1] / "figures" / "concept"
OUT_DIR.mkdir(parents=True, exist_ok=True)
OUT_PDF = OUT_DIR / "fig_nlpsr_schedule.pdf"
OUT_PNG = OUT_DIR / "fig_nlpsr_schedule.png"

# Frozen pub-profile tier settings (phase_03/parameter_table.md):
# NP_init = 5D; N_min = 12 bare (below D50), 25 at D >= 50.
TIERS = [
    (10, 50, 12, "#999999", "-"),
    (30, 150, 12, "#56B4E9", "-"),
    (50, 250, 25, "#E69F00", "-"),
    (100, 500, 25, "#000000", "-"),
]


def nlpsr(np0: int, npmin: int, x: np.ndarray) -> np.ndarray:
    # E5: NP(x) = NP_init + (N_min - NP_init) * x^(1-x)
    e = np.clip(1.0 - x, 0.0, 1.0)
    return np0 + (npmin - np0) * np.power(np.clip(x, 1e-12, 1.0), e)


def lpsr(np0: int, npmin: int, x: np.ndarray) -> np.ndarray:
    return np0 + (npmin - np0) * x


def main() -> None:
    x = np.linspace(0.0, 1.0, 401)

    fig, ax = plt.subplots(figsize=(6.2, 3.6))
    for dim, np0, npmin, color, style in TIERS:
        ax.plot(x, nlpsr(np0, npmin, x), style, color=color, linewidth=1.9,
                label=(f"$D={dim}$: $NP_{{\mathrm{{init}}}}$={np0}, "
                       f"$N_{{\\min}}$={npmin}"))
        # Audit 2026-07-23: the alpha-0.55 tinted references sat at ~20%
        # contrast and vanished against the dotted grid in greyscale -- the
        # NLPSR-vs-LPSR comparison is the figure's point.  One uniform dark
        # grey matches the legend proxy and reads at print size; the dotted
        # style stays the NLPSR/LPSR discriminator.
        ax.plot(x, lpsr(np0, npmin, x), ":", color="#5A5A5A", linewidth=1.3)
    # One legend proxy for the LPSR reference style.
    ax.plot([], [], ":", color="#5A5A5A", linewidth=1.3,
            label="linear LPSR reference (same endpoints)")

    ax.set_xlabel(r"Budget fraction $x = t/\mathrm{MaxFES}$")
    ax.set_ylabel(r"Population size $NP(x)$")
    ax.set_xlim(0.0, 1.0)
    ax.set_ylim(0, None)
    ax.grid(True)
    ax.legend(fontsize=8.5, loc="upper right", frameon=False)
    # No internal headline: the LaTeX caption describes the schedule.

    fig.tight_layout()
    fig.savefig(OUT_PDF, bbox_inches="tight", metadata={"CreationDate": None})
    fig.savefig(OUT_PNG, bbox_inches="tight", dpi=220)
    plt.close(fig)
    print(f"wrote {OUT_PDF}")
    print(f"wrote {OUT_PNG}")


if __name__ == "__main__":
    main()
