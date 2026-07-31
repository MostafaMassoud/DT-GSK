# Word-native (DrawingML) build plan for the conceptual figures — Phase 9 input

**Phase 7, task C.5 companion.** `fig_architecture.drawio` (this directory) is the
editable diagram source for `tab:architecture`. This file plans how the REMAINING
conceptual figures will be rebuilt **natively in Word** (DrawingML shapes / native
tables, not pasted rasters) at Phase 9, so every label stays editable and the
manuscript carries no screenshot content. All content is transcribed from the same
frozen sources as the rendered PDFs (`phase_03/algorithm_pseudocode.md`,
`phase_03/equation_registry.csv`, `phase_03/parameter_table.md`,
`phase_04/novelty_scope.md`, `phase_04/conceptual_figure_specs.md`); **no empirical
value appears in any of these figures**.

General DrawingML conventions (all figures):

- One drawing canvas (`<wpg:wgp>` group) per figure; rounded rectangles
  (`<a:prstGeom prst="roundRect">`) with 1 pt `#2C3E50` outlines.
- Fills follow the rendered palette: neutral `#E8E8E8` (inherited core), blue
  `#CFE1EE` (scaffold, all tiers), tan `#F5DCC4` (D≥50-gated), violet `#E3D1E8`
  (D≥100-gated), gray `#DCDCDC` (rails) — all grayscale-distinguishable.
- Control-flow connectors: straight/elbow `#34495E` with block arrowheads;
  data-flow connectors: `#A04000` (italic labels); gate badges: small white
  roundRects with `#7A4A00` bold text.
- Greek/math tokens (λ, κ_min, x^(1−x), NP(x)) as OMML inline math built in
  Phase 9 from the canonical Markdown (same pipeline as the notation table);
  never hand-authored ad hoc.
- Deterministic object names (`arch_core`, `sgsm_stage2_graph`, ...) so re-builds
  diff cleanly.

## tab:architecture (F-ARCH)

Built directly from `fig_architecture.drawio` (import or manual transcription):
same boxes, badges, rails, and edge set — see the .drawio file for authoritative
geometry, labels and colors. The RNG rail is a rotated text box on the left; the
BudgetController rail is a full-width box at the bottom; the deep-stall restart
edge is a dashed orthogonal connector re-entering at the top row, labeled
"restart branch: resample P from rngs.bse — re-enter loop (charged)".

## tab:sgsm-mechanism (F-SGSM-MECH)

- Three side-by-side stage panels (roundRect groups) titled "Stage 1 — learn
  from accepted moves", "Stage 2 — decaying signed pair graph (E10)",
  "Stage 3 — exploit ×3", plus a bottom timeline strip.
- Stage 1: three oval markers with green block-arrow deltas (accepted), one
  red dashed arrow with an "×" overlay (rejected — "rejected trials do not
  feed the graph"), caption text box "acceptance signal only — zero extra
  objective evaluations (compute cost per phase_03/complexity_analysis.md)".
- Stage 2: 8 circles labeled x1..x8 on a ring (abstract indices, didactic
  only); solid blue connectors = reinforcing pairs, dashed orange = opposing;
  one faint connector annotated "stale edges decay"; the E10 EMA formula as
  OMML; a threshold box "confidence gate: act only when conf ≥ κ_min".
- Stage 3: three stacked tan channel boxes ((i) linkage blocks → block
  crossover mask (E4); (ii) top-k blocks → subspace LS, "charged through
  BudgetController"; (iii) signed matrix → eigenbasis → final polish (E11),
  "one-shot, RNG-free, final budget slice; coordinate axes when no graph
  signal") with brown connectors fanning out of the gate box.
- Timeline strip: full-width bar 0 → MaxFES; "D≥50 activation gate" tick at 0;
  continuous-update band; hatched final slice labeled "polish fires once".

## tab:dim-gating (F-GATING)

- Built as a **native Word table** (not shapes): 11 rows (header + 10
  subsystem rows) × 5 columns (subsystem, D10, D30, D50, D100).
- ON cells: dark fill `#3D5A73`, white bold text carrying the frozen
  tier value (transcribed from `phase_03/parameter_table.md` — e.g. N_min,
  block size/mix, τ, r_rst/R_max, λ/κ_min, polish start, deep-stall frac);
  OFF cells: white fill, gray "OFF" text — filled-vs-empty survives grayscale.
- Two thick `#7A4A00` vertical borders before the D50 and D100 columns with
  the callouts "D ≥ 50: structure memory + polish activate" and
  "D ≥ 100: protective controllers activate" beneath the table.
- Footnote row: "single frozen configuration; no per-suite tuning
  (algorithm_freeze_manifest.json) — CEC2011 problems resolve to the tier of
  their native dimension".
- Binding rule carried over: any cell that cannot be transcribed verbatim
  from `phase_03/parameter_table.md` blocks the build and is escalated.

## tab:taxonomy (F-TAXONOMY)

- Built as a **native Word table**: 5 rows (header + 4 comparison dimensions)
  × 5 columns (dimension label; DG [omidvar2014dg]; CMA-ES [hansen2001cmaes];
  eigenvector-based crossover [guo2015eig]; ISM — this work, code alias SGSM).
- Header row dark `#3D5A73` with white bold text; ISM column highlighted
  `#F5DCC4` with a heavier outline; alternating row shading `#F4F7FA`.
- Cell text transcribed (condensed) from `phase_04/novelty_scope.md`
  Sections 1.1–1.3 only; footnote line: "conceptual positioning only,
  card-bounded; no equivalence implied among support graph, covariance
  matrix, decomposition, and eigenbasis; no performance statement; ISM
  compute cost per phase_03/complexity_analysis.md — never worded 'free'".

## fig:nlpsr-schedule (F-NLPSR)

- Remains a rendered analytic chart (matplotlib vector output of the frozen
  E5 closed form; `papers/scripts/generate_nlpsr_trajectory.py`). In Word it
  is embedded as the vector image (EMF/SVG conversion of
  `fig_nlpsr_schedule.pdf`) rather than rebuilt shape-by-shape — an analytic
  curve is not sensibly reproducible as DrawingML art. Caption states it is
  the analytic evaluation of E5 at the frozen tier floors (no empirical
  source).
