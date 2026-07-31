# Phase 7 - CR-0001 seven-curve family-overlay convergence: validation record

Task: extend the three per-suite convergence generators from two-series
(GSK vs DT-GSK) to the pre-registered 7-algorithm family overlay
(P1/P2/P3, phase_04/exhibit_plan.csv), render all grids, and validate
that every panel carries exactly 7 series or a disclosed absence.

## Empirical inputs (admissible per pre-registration P2)

- `benchmarks/cec_reference_results/<suite>/<alg>/gen_logs/CheckpointErrors_<alg>_F<k>_D<dim>.csv`
  for suites cec2017/cec2011/cec2013 and the P1 panel
  (gsk, agsk, apgsk, fdb-agsk, atmals-gsk, egsk, dt-gsk).
- P5 frozen main-text selection: `papers/build_prompt_phases/phase_05/curve_selection.csv`
  (read, never re-derived): D30 -> F3, F10, F12, F26; D100 -> F1, F5, F12, F26.
- No `results/_run_all`, no `results/_ablation`, no rendered `.tex`, no
  hand-typed values. The former representative-run GSK fallback
  (`curves/Figure_*.csv` interpolation) was REMOVED: checkpoint logs
  exist for all seven algorithms, so the P2 identical-basis mean applies
  panel-wide with no fallback path exercised.

## Tooling changes

- NEW `papers/scripts/_convergence_common.py` - shared P1 order, P2
  per-checkpoint mean-across-runs loader, P3 fixed color/linestyle map
  (Okabe-Ito; dt-gsk #000000 solid at 1.5x width drawn on top), shared
  single legend per grid, log-error y-axis with display-only floor
  1e-14 for exact zeros (documented in each companion log; never enters
  any statistic), disclosed linear-axis fallback for negative CEC2011
  objectives, PDF-primary + PNG(300 dpi) writer, deterministic
  missing-log writer.
- REWRITTEN `papers/scripts/generate_full_convergence.py` - 7-curve
  overlay; adds the two main-text 2x2 grids from the frozen P5 CSV
  (HARD FAIL if the CSV is absent or does not list exactly 4 functions
  per featured dimension) and extends supplement coverage from
  D{10,50} to all D{10,30,50,100}.
- REWRITTEN `papers/scripts/generate_cec2011_convergence.py` - 7-curve
  overlay, all 22 problems at native dims.
- REWRITTEN `papers/scripts/generate_cec2013_convergence.py` - 7-curve
  overlay, 28 functions, `--dimension 30` (P4: D30 only).
- `ruff check --fix` on all four scripts: All checks passed.

## Panel validation (from the generators' per-panel series bookkeeping,
## written to the companion `*_missing.log` files)

| Suite | Grids | Panels | Panels with 7/7 series | Disclosed absences |
|---|---|---|---|---|
| CEC2017 main D30 | main_cec2017_D30 | 4 (F3,F10,F12,F26) | 4 | 0 |
| CEC2017 main D100 | main_cec2017_D100 | 4 (F1,F5,F12,F26) | 4 | 0 |
| CEC2017 supplement D10 | all_funcs_D10_{a,b,c} | 29 | 29 | 0 |
| CEC2017 supplement D30 | all_funcs_D30_{a,b,c} | 29 | 29 | 0 |
| CEC2017 supplement D50 | all_funcs_D50_{a,b,c} | 29 | 29 | 0 |
| CEC2017 supplement D100 | all_funcs_D100_{a,b,c} | 29 | 29 | 0 |
| CEC2011 (native dims) | cec2011_{a,b,c} | 22 | 22 | 0 |
| CEC2013 D30 | cec2013_{a,b,c,d} | 28 | 28 | 0 |
| **Total** | 21 grid figures | **174** | **174** | **0** |

Every panel contains exactly 7 series; zero missing curves; the
missing-curve section of each companion log affirmatively records
"(none)". Companion logs (deterministic, no timestamps):

- `papers/figures/convergence/cec2017_missing.log`
- `papers/figures/convergence/cec2011_missing.log`
- `papers/figures/convergence/cec2013_missing.log`

Visual spot-checks (main_cec2017_D30.png, main_cec2017_D100.png,
cec2011_a.png) confirmed: 7 distinguishable series per panel in the P3
style map, one shared legend per grid in P1 order (GSK, AGSK, APGSK,
FDB-AGSK, ATMALS-GSK, eGSK, DT-GSK), log-error y-axis (F3-D30 shows
the documented 1e-14 display floor after DT-GSK reaches machine zero),
and the disclosed linear-axis fallback on the negative-objective
CEC2011 problems F2/F5/F6 (F10 likewise per data scan).

## Main-text grid files (per frozen curve_selection.csv)

- `fig:conv-cec2017-d30`:
  `papers/figures/convergence/main_cec2017_D30.pdf` (primary) /
  `main_cec2017_D30.png` (300 dpi alternate) - panels F3, F10, F12, F26.
- `fig:conv-cec2017-d100`:
  `papers/figures/convergence/main_cec2017_D100.pdf` (primary) /
  `main_cec2017_D100.png` (300 dpi alternate) - panels F1, F5, F12, F26.

## Caption metadata (for Phase 8 caption authoring)

- Aggregation: per-checkpoint arithmetic MEAN of best-so-far error
  across all runs per algorithm (CEC2017/CEC2013: n=51; CEC2011: n=25),
  identical basis for all 7 curves; no smoothing, no extrapolation.
- Log-error y-axis; display-only floor 1e-14 applied to exact-zero
  means (well below the 1e-8 CEC success threshold); floor is
  presentation-only and appears in no table or statistic.
- CEC2011 panels F2 (D=30), F5 (D=30), F6 (D=30), F10 (D=12) plot raw
  mean objective on a LINEAR axis (negative optima), disclosed by an
  in-panel note.
- F2 is excluded from CEC2017 per protocol (29 functions).

## Notes / dispositions local to this task

- Legacy two-series artifacts formerly emitted by these scripts were
  overwritten in place (all_funcs_D10_*, all_funcs_D50_*, cec2011_*,
  cec2013_* keep their filenames, now 7-curve). Pre-existing stale
  PNGs `papers/figures/convergence/F{01,04,15,22}_D{30,50}.png` are
  NOT outputs of the extended generators; they are superseded by the
  family-overlay grids and should not be cited by any Phase 8 caption.
- No ablation input touched; no `results/` staging input touched.
