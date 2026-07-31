# Copyright (c) 2026 Mostafa Masoud <moustafa.masoud@gmail.com>
"""Shared figure style for every generated exhibit (reader feedback 2026-07-23).

One design, applied by every generator, so the figures read as typeset parts
of the article rather than tool output:

* **Typeface matches the paper.**  The manuscript body is Palatino; figures
  now use Palatino Linotype (with graceful fallbacks) and STIX math instead
  of matplotlib's default DejaVu Sans -- the single strongest "generated
  chart" tell.
* **No in-figure headline titles.**  The LaTeX caption is the one place a
  figure is described; internal titles that duplicated captions are removed
  by the generators.  Small panel tags (``F3 (D=30)``, ``D = 10``) remain,
  in regular weight.
* **Quiet chrome.**  Left/bottom spines only, soft dark-grey, hairline solid
  grid (dotted grids fought the dotted GSK curve), outward ticks, frameless
  legends, thin refined hatching.

Deterministic: fonts subset-embed under ``pdf.fonttype 42``; no timestamps.
Usage: ``import _fig_style; _fig_style.apply()`` immediately after selecting
the Agg backend, BEFORE any figure is created.  Generator-specific keys
(e.g. ``savefig.bbox``) may be set after ``apply()``.
"""
from __future__ import annotations

import matplotlib

#: Palatino first (the manuscript face, present on the build host), then
#: metric-compatible fallbacks so a bare CI host still renders a serif.
FONT_STACK = [
    "Palatino Linotype", "Book Antiqua", "Palatino",
    "TeX Gyre Pagella", "DejaVu Serif",
]


def apply() -> None:
    matplotlib.rcParams.update({
        # -- typography ----------------------------------------------------
        "font.family": "serif",
        "font.serif": FONT_STACK,
        "mathtext.fontset": "stix",          # pairs acceptably with Palatino
        "font.size": 9,
        "axes.labelsize": 9.5,
        "axes.titlesize": 10,
        "axes.titleweight": "normal",        # panel tags, never headlines
        "figure.titleweight": "normal",
        # -- axes chrome ---------------------------------------------------
        "axes.edgecolor": "#444444",
        "axes.linewidth": 0.7,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "xtick.direction": "out",
        "ytick.direction": "out",
        "xtick.major.size": 3.0,
        "ytick.major.size": 3.0,
        "xtick.color": "#444444",
        "ytick.color": "#444444",
        "xtick.labelcolor": "#1A1A1A",
        "ytick.labelcolor": "#1A1A1A",
        # -- grid: hairline solid, well behind the data --------------------
        "grid.color": "#9C9C9C",
        "grid.linestyle": "-",
        "grid.linewidth": 0.5,
        "grid.alpha": 0.30,
        "axes.axisbelow": True,
        # -- legend / hatching --------------------------------------------
        "legend.frameon": False,
        "hatch.linewidth": 0.5,              # refined, not Excel-dense
        # -- output determinism -------------------------------------------
        "figure.dpi": 300,
        "savefig.dpi": 300,
        "pdf.fonttype": 42,
        "svg.fonttype": "none",
    })
