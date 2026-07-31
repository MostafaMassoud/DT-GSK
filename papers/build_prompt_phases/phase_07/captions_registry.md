# Phase 7 caption registry (task 11) — self-contained captions for every main + supplement exhibit

Evidence release: **rel-2026-07-10-262fc16c9** (anchor commit `262fc16c9`); all
empirical values trace to `papers/analysis/rel-2026-07-10-262fc16c9/` and the
staging export `results/paper_tables/` (exported exclusively from that bundle,
`provenance.json`); convergence curves per pre-registration P2 from
`benchmarks/cec_reference_results/` gen_logs. Cross-reference:
`papers/governance/artifact_binding.csv` (one row per artifact, checksums).

Conventions used by every caption below (stated once, repeated per caption
where the journal requires standalone captions):

- **Suites / n**: CEC2017 = 29 functions (F1, F3–F30; F2 excluded per
  protocol), 51 runs, MaxFES = 10^4·D; CEC2013 = second comparison suite,
  28 functions, 51 runs; CEC2011 = 22 real-world problems at native
  dimensions, 25 runs, MaxFES = 150{,}000.
- **Metric**: CEC2017/CEC2013 use final error f(x)−f(x*) with the suite
  success floor (error < 1e−8 → 0); CEC2011 uses raw best objective value
  (negative optima possible on some problems).
- **Aggregation**: tables aggregate per-function over runs (best / median /
  worst / mean / SD); convergence curves are the per-checkpoint MEAN across
  all runs per algorithm (P2; identical basis for all seven curves; no
  smoothing, no interpolation).
- **Significance / uncertainty rules**: Wilcoxon signed-rank two-sided,
  Holm-corrected at family level, alpha = 0.05; win/tie/loss tie rule
  |Δ| < 1e−8; Vargha–Delaney A12 (> 0.5 favours DT-GSK); Friedman +
  Iman–Davenport omnibus at alpha = 0.05 with Nemenyi post-hoc
  (CD = q_{0.05}·sqrt(k(k+1)/6N), k = 7, q_{0.05} = 2.949); bootstrap BCa
  95% CIs (n_boot = 10{,}000, seeded, BASE_SEED = 20260422).
- **Panel** (P1 order everywhere): GSK, AGSK, APGSK, FDB-AGSK, ATMALS-GSK,
  eGSK, DT-GSK. All comparative wording is scoped *within the GSK-family
  panel*, never field-wide.

Mandated limitation notes (attached per exhibit below):

- **[APGSK-GAP]** APGSK CEC2017 per-run records cover D100 only (anomaly
  A2-004/P2-A5); run-level quantities vs APGSK at CEC2017 D10/D30/D50 are
  disclosed-unavailable and were never imputed — function-level tests on
  per-function means are the sole inferential basis vs APGSK at those
  dimensions; APGSK D10/30/50 summary/checkpoint evidence derives from
  gen_logs whose producing environment is unrecorded.
- **[RANK-ROBUSTNESS]** Rank-ordering claims are qualified by the
  pre-registered robustness battery: r01 (median re-ranking) changes
  adjacent ordinal positions at D10 (APGSK/eGSK swap) and D50
  (FDB-AGSK/ATMALS-GSK swap) and shifts W/T/L counts; r04 (disputed-cell
  exclusion, APGSK removed at D10–D50) changes the D30 ordering (GSK and
  FDB-AGSK swap ordinal positions 4/5). Mean-based ranks are reported as the
  pre-registered primary; neither variant changes DT-GSK's own headline
  positions (its ordinal is identical in every variant), but panel orderings
  between comparators are not fully robust
  (`cec2017/robustness/robustness_summary_cec2017.md`,
  `robustness_cec2017_r01/r04*.csv`).
- **[CEC2011-EGSK-LOSS]** On CEC2011, DT-GSK's across-problem Wilcoxon vs
  eGSK is a statistically significant LOSS (n = 22, Holm-corrected
  p = 4.2e−02) — mandatory disclosure on every CEC2011 outcome exhibit.
- **[CEC2013-D30-THIRD]** On the CEC2013 second comparison suite at D30,
  DT-GSK places THIRD by Friedman mean rank (3.38) behind eGSK (3.07) and
  ATMALS-GSK (3.34) (bundle `friedman_ranks_cec2013_D30.csv`) — mandatory
  disclosure on CEC2013 outcome exhibits.

---

## Main-text exhibits

### alg:dt-gsk — Algorithm 1 (ART-PSEUDOCODE)
**Caption.** DT-GSK top-level pseudocode: the canonical loop (steps 1–11)
around the unchanged GSK core, with dimension-tier gating (blockwise linkage
crossover at D ≥ 30/50, SGSM interaction-structure memory, subspace local
search and eigenframe polish at D ≥ 50, controllers at D ≥ 100), strict
budget accounting, and global-best return semantics (restart never loses
ground; returns (x_gb, f_gb)). Method definition only — no empirical
values. Source: frozen `phase_03/algorithm_pseudocode.md`.

### eq:junior-idx … eq:rng-substreams — Equations E1a–E12 (ART-EQUATIONS)
**Caption set.** Formal definitions transcribed verbatim from the frozen
equation registry (`phase_03/equation_registry.csv`): inherited GSK
operators (E1a, E1b, E2, E3, E7, E8), modified components (E4 linkage-block
crossover mask; E5 tier-floored NLPSR; E6 ACE bandit credit; E9 budget-safe
escape), and original components (E10 SGSM interaction-graph EMA, λ = 0.95;
E11 RNG-free eigenframe polish; E12 13-substream child seeding). Method
definitions only — no empirical values.

### tab:notation — Notation table (ART-NOTATION)
**Caption.** Symbols used throughout the paper, defined once before use.
Method artifact; no empirical values. Source: frozen
`phase_03/notation_table.md`.

### tab:parameters — Parameter table (ART-PARAMS)
**Caption.** The single frozen `pub`-profile configuration of DT-GSK,
tier-resolved over D ∈ {10, 30, 50, 100}; identical across all three suites
(no per-suite tuning). Hash-frozen in
`phase_03/algorithm_freeze_manifest.json`. Method artifact; no empirical
values.

### tab:architecture — DT-GSK architecture (FIG-ARCH)
**Caption.** Architecture of DT-GSK: eight scaffold subsystems composed
around the unchanged GSK core, with dimension-gate badges, the
global-best/deep-stall restart loop ("restart never loses ground"; returns
the global best), the 13-substream RNG rail (E12) and the BudgetController
rail. Authored conceptual art from the frozen phase 3/4 specifications —
contains no measured values.

### tab:sgsm-mechanism — SGSM mechanism (FIG-SGSM-MECH)
**Caption.** How accepted moves become exploitable structure at zero extra
objective evaluations: acceptance events update the SGSM interaction-graph
EMA (E10), whose confidence-gated blocks feed the linkage crossover mask
(E4), the subspace local search, and the eigenframe polish (E11). Didactic
illustration over abstract coordinate indices — no measured interaction
structure is shown.

### tab:dim-gating — Dimension-tier gating chart (FIG-GATING)
**Caption.** Subsystem activation by dimension tier (D10/D30/D50/D100) under
the frozen `pub` profile; filled = ON with the frozen tier value, empty =
OFF (grayscale-safe). Threshold callouts per the frozen parameter table;
configuration fact, not an empirical result.

### tab:taxonomy — Related-work positioning (FIG-TAXONOMY)
**Caption.** Structure-learning taxonomy positioning ISM against
differential-grouping and covariance/eigenbasis methods on four dimensions:
update trigger, evaluation cost, what is learned, and how it is exploited.
ISM updates from accepted moves at no extra objective evaluations (not
"free": bookkeeping cost is O(NP·D) per generation). Authored from
card-verified literature facts only.

### tab:cec2011 — CEC2011 results (TAB-T01)
**Caption.** CEC2011 real-world suite (22 problems, native dimensions,
25 runs, MaxFES = 150{,}000): best / median / worst / mean / SD of the final
raw objective value for GSK vs DT-GSK; best mean per problem in bold.
Values from release rel-2026-07-10-262fc16c9 (raw best-fitness basis;
negative optima occur on some problems). **[CEC2011-EGSK-LOSS]** Within the
7-algorithm family panel on this suite, DT-GSK significantly loses to eGSK
across problems (Wilcoxon, n = 22, Holm p = 4.2e−02); this table's
head-to-head columns show GSK vs DT-GSK only and must not be read as a
panel-wide best claim.

### tab:wilcoxon-holm — CEC2017 pairwise inference (TAB-T15)
**Caption.** DT-GSK vs each GSK-family comparator on CEC2017
(29 functions, 51 runs, per-function mean error): across-function Wilcoxon
signed-rank p and Holm-corrected p (family = 6 comparators per dimension,
alpha = 0.05), win/tie/loss counts (tie |Δ| < 1e−8), Vargha–Delaney A12
(> 0.5 favours DT-GSK), and the Holm decision, per dimension
D ∈ {10, 30, 50, 100}. Release rel-2026-07-10-262fc16c9. **[APGSK-GAP]**
The APGSK rows at D10/D30/D50 rest on function-level tests over
per-function means — the sole valid inferential basis there, since APGSK
per-run records exist only at D100.

### tab:friedman-cec2017 — CEC2017 Friedman mean ranks (TAB-T16)
**Caption.** Friedman mean ranks (lower is better) of the 7-algorithm
GSK-family panel on CEC2017 per dimension (29 per-function mean errors as
blocks, 51 runs each) plus the unweighted across-dimension mean ("Overall",
descriptive aggregate); omnibus Friedman + Iman–Davenport significant at
every dimension (p ≤ 2.6e−08). Best rank per column in bold. Release
rel-2026-07-10-262fc16c9. **[RANK-ROBUSTNESS]** **[APGSK-GAP]**

### fig:cd-d10 / fig:cd-d30 / fig:cd-d50 / fig:cd-d100 — Nemenyi CD diagrams (FIG-CD-D10..D100)
**Caption (one per dimension).** Nemenyi critical-difference diagram for the
CEC2017 GSK-family Friedman mean ranks at D = {10|30|50|100} (k = 7
algorithms, N = 29 functions, alpha = 0.05, CD = 1.67); emitted only because
the Friedman omnibus is significant at that dimension. Mean rank of each
algorithm shown at bar end; the scale bar marks one CD from the best rank.
Within-one-CD-of-best cohorts: D10 best DT-GSK {DT-GSK, AGSK, FDB-AGSK,
APGSK, eGSK}; D30 best eGSK {eGSK, DT-GSK}; D50 best DT-GSK {DT-GSK,
eGSK}; D100 best DT-GSK {DT-GSK, eGSK, ATMALS-GSK}. Release
rel-2026-07-10-262fc16c9. **[RANK-ROBUSTNESS]**; D10/D30/D50 additionally
**[APGSK-GAP]**.

### fig:rank-vs-dim — Rank vs dimension (FIG-RANK-VS-DIM)
**Caption.** Friedman mean rank vs problem dimension (CEC2017,
D ∈ {10, 30, 50, 100}; 29 functions, 51 runs per cell) for the 7-algorithm
GSK-family panel; fixed panel colours/linestyles (Okabe-Ito), DT-GSK solid
black. Lower is better. Release rel-2026-07-10-262fc16c9.
**[RANK-ROBUSTNESS]** **[APGSK-GAP]**

### fig:cec2017-ranks — Per-dimension rank bars (FIG-CEC2017-RANKS)
**Caption.** Friedman mean ranks per dimension (CEC2017, 29 functions,
51 runs), grouped by dimension in the fixed panel order; companion to
tab:friedman-cec2017. Lower is better. Release rel-2026-07-10-262fc16c9.
**[RANK-ROBUSTNESS]** **[APGSK-GAP]**

### fig:cec2011-ranks — CEC2011 rank bars (FIG-CEC2011-RANKS)
**Caption.** Friedman mean ranks over the 22 CEC2011 real-world problems
(25 runs each, raw best-fitness basis), sorted best-first; DT-GSK
highlighted. Lower is better. Release rel-2026-07-10-262fc16c9.
**[CEC2011-EGSK-LOSS]**

### fig:friedman_bar_gsk — Overall CEC2017 rank bars (FIG-FRIEDMAN-OVERALL)
**Caption.** Overall CEC2017 Friedman mean rank (unweighted mean of the four
per-dimension mean ranks; descriptive aggregate, no omnibus test attaches to
the aggregate itself), sorted best-first; DT-GSK highlighted. Release
rel-2026-07-10-262fc16c9. **[RANK-ROBUSTNESS]** **[APGSK-GAP]**

### fig:conv-cec2017-d30 — Main-text convergence, D30 (FIG-CONV-MAIN-D30)
**Caption.** Family-overlay convergence on CEC2017 at D = 30 for the four
functions pre-registered by rule P5 and frozen before rendering
(`phase_05/curve_selection.csv`): F3 (unimodal; easy/strong), F10 (simple
multimodal; hard/comparable), F12 (hybrid; hard/comparable), F26
(composition; hard/WEAK — the mandated unfavourable case). Each panel
overlays all 7 panel algorithms; every curve is the per-checkpoint mean
error across 51 runs (identical basis; no smoothing); log-error y-axis with
a display-only floor of 1e−14 for exact zeros (never enters any statistic);
one shared legend. D30 is DT-GSK's known-weak tier: rank #2 behind eGSK.
Release rel-2026-07-10-262fc16c9. **[APGSK-GAP]** (checkpoint evidence at
D30).

### fig:conv-cec2017-d100 — Main-text convergence, D100 (FIG-CONV-MAIN-D100)
**Caption.** Family-overlay convergence on CEC2017 at D = 100 (tier where
SGSM/polish subsystems are active) for the four P5-frozen functions: F1
(unimodal; easy/strong), F5 (simple multimodal; easy/strong), F12 (hybrid;
hard/comparable), F26 (composition; hard/comparable). Per-checkpoint mean
error across 51 runs per algorithm, 7-curve overlay, log-error y-axis
(display floor 1e−14), one shared legend. Release rel-2026-07-10-262fc16c9.

---

## Supplement exhibits

### tab:h2h_d10 / tab:h2h_d30 / tab:h2h_d50 / tab:h2h_d100 — CEC2017 head-to-head detail (TAB-T02..T05)
**Caption (one per dimension).** CEC2017 at D = {10|30|50|100}
(29 functions, 51 runs): best / median / worst / mean / SD of the final
error (success floor 1e−8) for GSK vs DT-GSK; best mean per function in
bold. Two-algorithm detail behind the family-panel exhibits — no panel-wide
claim. Release rel-2026-07-10-262fc16c9.

### tab:cec2011-stats — CEC2011 Wilcoxon summary (TAB-T06)
**Caption.** Across-problem Wilcoxon signed-rank summary, DT-GSK vs GSK on
CEC2011 (n = 22 problems, 25 runs each, per-problem mean of the raw best
objective): R+, R−, p, and win/tie/loss counts (tie |Δ| < 1e−8);
alpha = 0.05. Release rel-2026-07-10-262fc16c9. **[CEC2011-EGSK-LOSS]**
(panel-level context: the corresponding panel-wide tests include a
significant loss to eGSK).

### tab:cec2017-d10 / -d30 / -d50 / -d100 — Family Mean±SD (TAB-T07..T10)
**Caption (one per dimension).** CEC2017 at D = {10|30|50|100}: mean ± SD of
the final error over 51 runs for all 7 GSK-family algorithms on each of the
29 functions; best mean per function in bold. Release
rel-2026-07-10-262fc16c9. D10/D30/D50 tables: **[APGSK-GAP]** (APGSK cells
derive from gen_logs final-checkpoint columns; per-run file absent at these
dimensions).

### tab:cec2013-d10 / -d30 / -d50 — CEC2013 head-to-head detail (TAB-T11..T13)
**Caption (one per dimension).** CEC2013 second comparison suite at
D = {10|30|50} (28 functions, 51 runs): best / median / worst / mean / SD of
the final error for GSK vs DT-GSK; best mean per function in bold. CEC2013
is a second comparison suite — never an independent hold-out. Release
rel-2026-07-10-262fc16c9. D30 table: **[CEC2013-D30-THIRD]**.

### tab:cec2013_wilcoxon — CEC2013 Wilcoxon summary (TAB-T14)
**Caption.** Across-function Wilcoxon signed-rank summary, DT-GSK vs GSK on
CEC2013 per dimension (n = 28 functions, 51 runs, per-function mean error):
R+, R−, p, win/tie/loss (tie |Δ| < 1e−8), and decision at alpha = 0.05.
Release rel-2026-07-10-262fc16c9. **[CEC2013-D30-THIRD]** (panel-level
context at D30).

### tab:bca-ci — BCa CIs on Friedman mean ranks (TAB-T16-BCA)
**Caption.** 95% bootstrap BCa confidence intervals on the CEC2017 Friedman
mean ranks of tab:friedman-cec2017 (per dimension; 29 function-level
midranks resampled, n_boot = 10{,}000, seeded BASE_SEED = 20260422); point
estimates reproduce tab:friedman-cec2017 exactly at 2-decimal display.
Release rel-2026-07-10-262fc16c9. **[RANK-ROBUSTNESS]** **[APGSK-GAP]**
Note (registry): the Word-side source `word_sources/T16_bca.json` carries
the per-function paired-difference BCa companion (plan T-BCA,
`headline_bca.csv`) — a different table; Phase 9 cross-format consistency
must reconcile the two before Word export.

### fig:sconv-cec2017-d10 / -d30 / -d50 / -d100 — Complete CEC2017 convergence grids (FIG-CONV-SUP-2017-*)
**Caption (one per dimension; three sub-figures a/b/c: F1,F3–F10 /
F11–F20 / F21–F30).** Family-overlay convergence for all 29 CEC2017
functions at D = {10|30|50|100}: per-checkpoint mean error across 51 runs
per algorithm (identical basis for all 7 curves; no smoothing), fixed
Okabe-Ito style map, DT-GSK solid black, one shared legend per grid,
log-error y-axis with display-only floor 1e−14 for exact zeros. All panels
carry the full 7/7 series (`cec2017_missing.log`). Release
rel-2026-07-10-262fc16c9. D10/D30/D50 grids: **[APGSK-GAP]**.

### fig:sconv-cec2011 — Complete CEC2011 convergence grids (FIG-CONV-CEC2011-A/B/C)
**Caption (three sub-figures: P1–P8 / P9–P16 / P17–P22).** Family-overlay
convergence for all 22 CEC2011 real-world problems at native dimensions:
per-checkpoint mean of the raw best objective across 25 runs per algorithm,
7-curve overlay, one shared legend. Panels whose means are negative
(problems with negative optima) fall back to a linear y-axis with an
in-panel disclosure; all other panels use the log axis with display floor
1e−14. All panels carry 7/7 series (`cec2011_missing.log`). Release
rel-2026-07-10-262fc16c9. **[CEC2011-EGSK-LOSS]** (outcome context for this
suite).

### fig:sconv-cec2013-d30 — Complete CEC2013 convergence grids (FIG-CONV-CEC2013-D30-A/B/C/D)
**Caption (four sub-figures: F1–F8 / F9–F16 / F17–F24 / F25–F28).**
Family-overlay convergence for all 28 functions of the CEC2013 second
comparison suite at D = 30 (the only pre-registered CEC2013 convergence
dimension, P4): per-checkpoint mean error across 51 runs per algorithm,
7-curve overlay, log-error y-axis (display floor 1e−14), one shared legend.
All panels carry 7/7 series (`cec2013_missing.log`). Release
rel-2026-07-10-262fc16c9. **[CEC2013-D30-THIRD]**.

### fig:nlpsr-schedule — NLPSR analytic schedule (FIG-NLPSR)
**Caption.** Analytic trajectory of the tier-floored nonlinear population
size reduction schedule (E5) under the frozen `pub` profile for all four
tiers (NP0 = 5D; N_min = 12/12/25/25): population size vs consumed budget
fraction. Analytic evaluation of the frozen formula — no empirical result
values. Sources: `phase_03/equation_registry.csv` (E5),
`phase_03/parameter_table.md`.

---

## Exhibits NOT available in this release (disclosed, never fabricated)

- **fig:trace-sgsm, fig:adaptive-params** (plan F-TRACE / F-ADAPT):
  UNAVAILABLE — diagnostic-release-gated; no promoted GenLog release exists
  (EG-005, dated Phase 7 note). Generators not run.
- **tab:sensitivity (T21/T22)**: NOT GENERATED — no admissible sensitivity
  release (EG-006, dated Phase 7 note); committed legacy `T21.tex`/`T22.tex`
  are stale and excluded from binding.
- **Ablation exhibits (X-ABL-01..03)**: DEFERRED_TO_PHASE_12_SUPPLEMENT_ONLY
  (P6); no ablation artifact of any kind exists in this build.
- **tab:cec2013-summary (plan T06 Friedman-rank table)**: not produced in
  the Phase 7 table set (the regenerated set carries the CEC2013 descriptive
  and Wilcoxon exhibits T11–T14); the **[CEC2013-D30-THIRD]** disclosure is
  therefore attached to tab:cec2013-d30 and tab:cec2013_wilcoxon above and
  must accompany any future tab:cec2013-summary.
