# Curve Selection Rule (BINDING) — Phase 5, Task 8

- **Status:** BINDING pre-registration for Phases 6-7. Formalizes phase_04/exhibit_plan.csv pre-registrations **P2** (convergence aggregation, CR-0001) and **P5** (main-text convergence selection rule, CR-0003 / PAPER_BUILD_PROMPT.md Section 6.7) into an executable procedure. Where P5 left a clause open ("any remaining stratum"), this document supplies the binding completion; nothing here contradicts P5.
- **Date:** 2026-07-10. **Evidence release:** rel-2026-07-10-262fc16c9 (`benchmarks/cec_reference_results/`, read-only). Staging `results/` (including `results/_ablation/`) is never citable and was not read.
- **Sources of record:** phase_04/exhibit_plan.csv (P1-P8); phase_04/thesis.md; papers/governance/seed_and_pairing_audit.md; papers/governance/benchmark_protocol_audit.md; papers/governance/phase2_anomaly_register.csv; phase_03/algorithm_freeze_manifest.json.
- **Scope:** governs exhibits F02-MAIN-D30 and F02-MAIN-D100 (main text) and, for alignment/aggregation/failure rules only, the supplement grids F02-SUP-CEC2017-D10/D30/D50/D100, F02-SUP-CEC2011, F02-SUP-CEC2013-D30 (supplement grids show ALL functions; no selection step applies to them).
- **Critical discipline:** this document was written WITHOUT computing, inspecting, or reporting any statistical outcome, rank, mean, or curve value. Only file existence, headers, and row counts of the release were read (feasibility verification, Section 8).

---

## 1. Data source and checkpoint alignment

### 1.1 Source of record for curves
Per P2, every convergence curve is computed from the release checkpoint logs:

```
benchmarks/cec_reference_results/<suite>/<opt>/gen_logs/CheckpointErrors_<opt>_F<f>_D<d>.csv
```

Verified schema (read-only): header `Run,Seed,E<fes_1>,...,E<fes_14>`, one row per run (51 rows for CEC2017). Each `E<fes>` column is the best error recorded at the checkpoint of `<fes>` function evaluations.

### 1.2 Checkpoint grid
The release grid is dimension-relative: 14 checkpoints at fixed fractions
`{1, 2, 3, 5, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100}%` of `MaxFES = 10^4 * D` (CEC2017). Verified against the release headers: D10 = `E1000..E100000`, D30 = `E3000..E300000`, D100 = `E10000..E1000000`.

### 1.3 Alignment policy (binding)
1. **Identical grid required.** All 7 panel algorithms (P1 order: gsk, agsk, apgsk, fdb-agsk, atmals-gsk, egsk, dt-gsk) must expose the identical checkpoint column set for a given (suite, f, d). Spot-verified identical for all 7 at CEC2017 F10/D30 (Section 8); Phase 6 MUST re-assert full-grid identity programmatically for every panel it renders, before aggregation.
2. **Grid mismatch disposition.** If any algorithm's file carries a different column set for a panel: use the **intersection** of checkpoint columns for ALL seven curves in that panel (so all curves stay on one common grid), disclose the mismatch in the panel caption and in `papers/governance/evidence_gap_register.md`. **Never interpolate, resample, or extrapolate** to a foreign grid.
3. **Missing/NaN cells inside a file.** Expected count is zero (release verification). If a cell is empty/NaN, the per-checkpoint mean at that checkpoint is computed over the available runs, the reduced n is disclosed in the caption, and the incident is logged in `evidence_gap_register.md`. **Never fill forward, impute, or interpolate.** No smoothing anywhere; no extension past termination (P2).
4. **x-axis.** Curves are plotted at the recorded checkpoint FES values (absolute FES or FES/MaxFES fraction, chosen once at render time and used for all panels in a grid); points are connected linearly between recorded checkpoints for display only — no claim is attached to inter-checkpoint behavior.

### 1.4 Fallback (P2, verbatim discipline)
The representative-run fallback (`curves/Figure_F<f>_D<d>_Run#<r>.csv`) is permitted ONLY when an algorithm's checkpoint logs are absent from the release for that (f, d), and must be caption-disclosed. Feasibility check (Section 8) found complete CheckpointErrors coverage (29 functions x 4 dimensions = 116 files per algorithm) for the spot-checked algorithms, so the fallback is expected to be unnecessary for CEC2017; the rule remains in force regardless.

## 2. Aggregation (P2, binding)

For each (suite, algorithm, f, d, checkpoint): the plotted value is the **arithmetic mean of the checkpoint error across ALL runs** (51 for CEC2017/CEC2013, 25 for CEC2011). Identical basis for all 7 curves in every panel — never a mix of mean-of-runs for some algorithms and single-run for others (absent the disclosed Section 1.4 fallback).

Pairing context: the unified seed schedule `get_cec_seed(20240620, dim, func, run)` gives identical seeds — and shared initial populations — across all 7 optimizers per (dim, func, run), verified in `papers/governance/seed_and_pairing_audit.md` (5,916/5,916 CEC2017 seed matches per algorithm, apgsk seeds re-verified from gen_logs). The per-checkpoint means for the 7 algorithms are therefore computed over the **same paired instance/run set**, which is what licenses visual comparison of the overlays.

**Zero handling / log floor (render-time, display-only):** stored aggregates are never modified. At render, the y-axis is log10; values at or below a display floor epsilon (chosen once at render time, documented in the figure note per P2) are drawn at the floor. The floor affects display only, never any stored or reported number.

## 3. Uncertainty (binding: none in main figures)

Main-text and supplement convergence panels show the 7 mean curves with **no uncertainty bands or error bars**. Rationale (pre-registered here):

1. **Readability:** each panel already overlays 7 curves distinguished by the fixed P3 Okabe-Ito color/linestyle map; adding 7 shaded bands (or per-checkpoint error bars on a log axis) produces heavy band overlap and makes the panels unreadable — the figure would no longer communicate the ordering it exists to show.
2. **Uncertainty is carried elsewhere, by pre-registration:** per-function SDs in T01-D10..D100, Wilcoxon+Holm outcomes in T02/T02-FULL, and A12/Cliff effect sizes with BCa 95% CIs in T03/T-BCA quantify run-level dispersion and pairwise reliability on the same release data.
3. **Completeness is carried by the supplement:** full per-function grids (F02-SUP-*) show every function, so the main-text selection hides nothing that the supplement does not expose.

Captions of the main-text grids must state that curves are per-checkpoint means over all runs and point to the SD/effect-size tables and supplement grids.

## 4. Failure rule (binding)

A missing algorithm curve (absent checkpoint logs AND absent fallback curve file) is a **caption-disclosed and register-disclosed absence** (`evidence_gap_register.md`): the panel is rendered with the remaining curves, the caption names the missing algorithm and the reason, and the absence is never fabricated, interpolated, borrowed from another dimension/suite, or silently dropped. Phase 7 validation asserts exactly seven series per panel OR a disclosed absence note (P7); a panel failing both checks blocks the gate.

Note: the known apgsk data constraint (per_run.csv covers D100 only at CEC2017; `phase2_anomaly_register.csv` / `benchmark_protocol_audit.md`) does **not** affect this plan: neither the selection strata (Section 5, summary CSVs only) nor the curve aggregation (Section 1, CheckpointErrors logs, which exist for apgsk at all four dimensions) reads `per_run.csv`.

## 5. Exact selection algorithm (P5, binding; executed in Phase 6)

### 5.0 Timing and information hygiene
- Executed in **Phase 6, BEFORE any convergence curve is rendered or viewed** and before any `gen_logs/CheckpointErrors_*` or `curves/*` file is opened for the featured panels. The Phase 6 executor must fill `papers/build_prompt_phases/phase_05/curve_selection.csv` (Section 6) and log the invocation FIRST; only then may generators run.
- **Permitted inputs (exhaustive):** the release per-function summary CSVs `benchmarks/cec_reference_results/cec2017/<opt>/<opt>_cec2017_D<d>.csv` (verified header `Function,Best,Median,Mean,Worst,SD`; 29 rows) for the 7 panel algorithms at d in {30, 100}. **Forbidden inputs:** any gen_log, curve file, per_run.csv, rendered figure, or anything under `results/`.
- Known limitation (carried from P5, must be restated in the register): repository figures were seen during the Phase 2 asset audit; the rule is nevertheless purely summary-statistic-driven and admits no discretionary choice.

### 5.1 Featured dimensions
`D30` (known-weak mid-D tier; the permitted Section 5.1 rank statement — #2 behind eGSK — is to be re-derived in Phase 6 from the release, not assumed) and `D100` (tier where the SGSM/polish subsystems are active per the pub-profile gating).

### 5.2 Strata (computed per featured dimension, from summary CSVs only)
For each function f in the 29 CEC2017 functions (F1, F3-F30) and each d in {30, 100}:

- Let `m_a(f,d)` = the `Mean` column value (mean final error over 51 runs) of algorithm a.
- **Difficulty score** `s(f,d)` = the **median over the 7 panel algorithms** of `m_a(f,d)` (panel-median mean final error; median of 7 values = 4th order statistic [david_order_statistics]).
- **Difficulty tercile:** sort the 29 functions ascending by the key `(s(f,d), f)` — the function-number component makes boundary ties deterministic. Positions 1-10 = `easy`, 11-20 = `moderate`, 21-29 = `hard`.
- **DT-GSK standing:** rank `m_ismgsk(f,d)` among the 7 values `{m_a(f,d)}`, ascending (rank 1 = lowest mean error), with **ties assigned the average rank** (fractional ranks permitted; exact-value ties, e.g. multiple algorithms at error 0, are expected on easy functions). Map: `strong` if rank <= 2, `comparable` if 2 < rank <= 5, `weak` if rank > 5.

### 5.3 Category partition (CEC2017 protocol; F2 excluded)
`unimodal` = {F1, F3}; `simple multimodal` = {F4..F10}; `hybrid` = {F11..F20}; `composition` = {F21..F30}.

### 5.4 Fill priority (total order; binding)
Positions 1-4 are P5 verbatim; positions 5-9 are the Phase-5 binding completion of P5's "any remaining stratum" clause, ordered by difficulty descending then standing (weak > comparable > strong), preserving P5's unfavorable-case-first intent:

1. (hard, weak)
2. (hard, comparable)
3. (moderate, comparable)
4. (easy, strong)
5. (hard, strong)
6. (moderate, weak)
7. (moderate, strong)
8. (easy, weak)
9. (easy, comparable)

### 5.5 Selection procedure (per featured dimension; deterministic)
```
selected[d] = {}                        # category -> function
for stratum in priority order 1..9:
    for f in functions of that stratum at dimension d, ascending function number:
        c = category(f)
        if c not in selected[d]:
            selected[d][c] = f
# terminates with all 4 categories filled: every function belongs to
# exactly one stratum, and every category is non-empty at every d
```
Ties are broken by **lowest function number** at every point where more than one function is eligible (P5 verbatim).

### 5.6 Joint constraint and deterministic repair
The 8 selected panels (4 at D30 + 4 at D100) must **jointly include >= 1 hard function and >= 1 DT-GSK-weak function** (Section 6.7 unfavorable-case requirement). After running 5.5 for both dimensions, check the constraint; it can only bind in degenerate stratum configurations, but the disposition is pre-specified:

1. If violated for BOTH hard and weak: seek a single substitution — candidates are (d, c, f) with f in stratum (hard, weak) at d, not currently selected; order candidates by (dimension ascending: 30 before 100, then function number ascending); replace `selected[d][c]` with the first candidate. If no (hard, weak) candidate exists anywhere, fall through to steps 2 then 3 as independent repairs.
2. If violated for hard only: candidates are (d, c, f) with f hard at d and not selected; order by (stratum priority restricted to hard: (hard,weak) > (hard,comparable) > (hard,strong), then dimension ascending, then function number ascending); replace `selected[d][c]` with the first candidate.
3. If violated for weak only: same construction with weak strata ordered (hard,weak) > (moderate,weak) > (easy,weak); the repair must not displace a slot introduced by step 2 — if the first candidate would, take the next candidate; if no other candidate exists, keep the step-2 slot and proceed to step 4 for the weak arm.
4. **Genuine unsatisfiability** (e.g. no DT-GSK-weak function exists at either featured dimension): select per the base rule, and disclose the fact in the main-grid caption AND `evidence_gap_register.md` ("no DT-GSK-weak function exists in the CEC2017 panel at D30/D100 under the pre-registered standing definition"). Such a fact — however favorable — is disclosed, never silently absorbed.

Every repair performed is recorded in `curve_selection.csv` via `selection_reason` = `constraint_repair_hard` / `constraint_repair_weak` / `constraint_repair_joint`.

### 5.7 Output contract
Phase 6 writes **all 58 rows** (2 dimensions x 29 functions) to `papers/build_prompt_phases/phase_05/curve_selection.csv` so the full strata are auditable:

| column | content |
|---|---|
| suite | `cec2017` |
| dimension | `30` or `100` |
| function | integer (1, 3-30) |
| category | `unimodal` / `simple_multimodal` / `hybrid` / `composition` |
| difficulty_tercile | `easy` / `moderate` / `hard` |
| ismgsk_standing | `strong` / `comparable` / `weak` |
| selection_reason | selected rows: `priority_<k>_(<tercile>,<standing>)` with k = position in Section 5.4, or a `constraint_repair_*` tag; all other rows: `not_selected` |
| selected_for_main | `TRUE` / `FALSE` (exactly 4 TRUE per dimension) |

Rendering (Phase 7) then consumes ONLY the 8 `selected_for_main = TRUE` rows for F02-MAIN-D30 / F02-MAIN-D100, with P3 styling and P1 legend order.

## 6. Reserved placeholder

`papers/build_prompt_phases/phase_05/curve_selection.csv` is created in this task with the header row ONLY (no data rows). Phase 6 fills it per Section 5.7. Any data row appearing in it before the Phase 6 selection run is a governance violation.

## 7. Other suites (supplement grids; no selection)

- **CEC2017 supplement** (F02-SUP-CEC2017-D10/D30/D50/D100): all 29 functions, Sections 1-4 apply unchanged.
- **CEC2011** (F02-SUP-CEC2011): all 22 problems at native dimensions, 25 runs, MaxFES = 150000; Sections 1-4 apply with the release CEC2011 checkpoint grid.
- **CEC2013** (F02-SUP-CEC2013-D30): D30 ONLY per P4 (Section 8.5 dimension-filename limitation); wording "second comparison suite", never "independent"/"holdout". Sections 1-4 apply.

## 8. Feasibility verification performed (read-only; no outcomes inspected)

Verified on 2026-07-10 against `benchmarks/cec_reference_results/cec2017/` (release rel-2026-07-10-262fc16c9); only file listings, headers, and row counts were read — no numeric column was aggregated, ranked, or compared:

1. Summary CSVs `<opt>_cec2017_D<d>.csv` exist for all 7 panel algorithms at D10/D30/D50/D100 with header `Function,Best,Median,Mean,Worst,SD` and 29 function rows -> the Section 5.2 strata are computable from pre-registered inputs.
2. `gen_logs/CheckpointErrors_<opt>_F10_D30.csv` headers are byte-identical across all 7 algorithms (`Run,Seed,E3000,...,E300000`; 14 checkpoints; 51 data rows each) -> the Section 1.3 identical-grid requirement is satisfiable; Phase 6 still re-asserts it for every rendered panel.
3. CheckpointErrors file counts: 116 per algorithm (29 functions x 4 dimensions) spot-checked for gsk, egsk, dt-gsk -> full curve coverage expected, including eGSK (panel data provenance per papers/governance/comparability_audit.md) and apgsk (whose per_run.csv D100-only limitation is irrelevant here, Section 4).
4. Checkpoint grids at D10/D30/D100 confirm the dimension-relative fraction pattern of Section 1.2.

## 9. Citations used

`david_order_statistics` (order-statistic definition of the panel median and tercile stratification). All other statistical machinery referenced (Wilcoxon/Holm/Friedman/effect sizes) lives in the companion Phase 5 statistical analysis plan, not in this document.
