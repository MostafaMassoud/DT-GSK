# Benchmark Protocol Audit — Phase 2, Tasks 1–3

| Field | Value |
|---|---|
| Phase / tasks | Phase 2 (Immutable empirical evidence, benchmark, and provenance audit), tasks 1–3 |
| Date | 2026-07-10 |
| Anchor commit | `262fc16c91fbe5608a1a0b0c5df3cbcd009edc21` (verified: `git rev-parse HEAD` matches; `benchmarks/cec_reference_results/` clean in `git status`) |
| Evidence tree | `benchmarks/cec_reference_results/` — treated strictly READ-ONLY; no file in the tree was written, renamed, or touched |
| Governing sections | Master prompt Phase 2 tasks 1–3; Sections 2.3 (CR-0003 immutability prohibitions), 2.4, 2.6, 3.8, 6.10 (staging quarantine) |
| Staging quarantine | `results/` (including the live `results/_ablation/` campaign) was neither read nor interpreted for this audit |
| Method | Machine validation CLI + custom batched CR-0003 scan (`cr0003_anomaly_scan.py`); every anomaly logged, classified, traced to source file, impact-evaluated; **nothing repaired** |

---

## 1. Task 1 — Evidence-tree layout audit

### 1.1 Root and suite layout

- Root entries: `README.md`, `cec2011/`, `cec2013/`, `cec2013lsgo/`, `cec2017/`, `cec2020/` — exactly the three primary suites plus the two context suites plus the tree README. No unexpected entries.
- **No doubled-suite directories**: a full recursive walk found zero directories matching `cec*` below the suite level (e.g. no `cec2017/cec2017/`).
- **No zero-byte files** anywhere in the tree.
- **No stray files** at suite level; every optimizer directory contains only the canonical file classes (no `MISSING_FILE` or extra-file anomalies were raised for any of the 21 primary cells).

### 1.2 Primary suites — per-optimizer file classes

All three primary suites contain exactly the seven optimizer directories
`agsk`, `apgsk`, `atmals-gsk`, `egsk`, `fdb-agsk`, `gsk`, `dt-gsk`, and each of
the 21 cells carries all required file classes:

| Class | cec2017 (×7) | cec2011 (×7) | cec2013 (×7) |
|---|---|---|---|
| Summary CSVs `<opt>_<suite>_D<dim>.csv` | 4 (D10/30/50/100) | 16 per-dim files + 1 rollup `<opt>_cec2011.csv` | 3 (D10/30/50) |
| `per_run.csv` | present | present | present |
| `seed_schedule.csv` | present | present | present |
| `environment.json` (incl. `fp_regime.sentinel`) | present | present | present |
| `run_config.json` | present | present | present |
| `verification.json` | present | present | present |
| `phase0_protocol.json` | present | present | present |
| `curves/` (convergence traces, 1 per func×dim) | 116 files | 22 files | 84 files |
| `gen_logs/` (`CheckpointErrors_<opt>_F<f>_D<d>.csv`) | 116 files | 22 files | 84 files |

All curve filenames match `Figure_F<f>_D<d>_Run#<r>.csv` and all gen-log
filenames match `CheckpointErrors_<opt>_F<f>_D<d>.csv`; the (func, dim) cell
sets of both directories exactly equal the protocol cell sets for every
optimizer (including `cec2017/apgsk`, whose `curves/` and `gen_logs/` cover all
four dimensions even though its `per_run.csv` does not — see anomaly A2-004).

### 1.3 Context suites (verified separately)

| Cell | Content | Raw classes |
|---|---|---|
| `cec2020/agsk` | `agsk_cec2020_D05.csv`, `_D10.csv`, `_D15.csv`, `_D20.csv` (10 functions each) | none (summary-only, as expected for imported context evidence) |
| `cec2013lsgo/decc-g` | `decc-g_cec2013lsgo.csv` (15 functions) | none (summary-only) |
| `cec2013lsgo/mos` | `mos_cec2013lsgo.csv` (15 functions) | none (summary-only) |

Context summaries use 3-significant-digit scientific notation (`%.3e`),
consistent within each file; primary summaries use 10-digit (`%.10E`). This is
a suite-scope difference of imported vs locally produced evidence, not a
mixed-precision defect inside any one table.

### 1.4 CSV census (reconciles machine validation)

| Class | Count |
|---|---|
| Summary CSVs (incl. context) | 174 |
| `per_run.csv` | 21 |
| `seed_schedule.csv` | 21 |
| `curves/*.csv` | 1554 |
| `gen_logs/*.csv` | 1554 |
| **Total** | **3324** (equals the machine-validation CSV count) |

---

## 2. Task 2 — Machine validation and CR-0003 anomaly scan

### 2.1 Machine validation CLI

```powershell
python -m gsk_family.cli.validate --references benchmarks/cec_reference_results
```

- Result: **PASS** (exit 0) — `reference root: benchmarks\cec_reference_results`, `csv files: 3324`.
- Complete verbatim output archived: `papers/governance/machine_validation_output.txt`.
- Scope note: in `--references` mode this CLI validates root existence and CSV
  presence only (`src/gsk_family/cli/validate.py`, lines 14–29). It performs
  none of the CR-0003 checks; those were executed by the custom scan below, as
  the master prompt requires.

### 2.2 CR-0003 custom anomaly taxonomy scan

Script: `papers/governance/cr0003_anomaly_scan.py` (read-only over the tree;
outputs to scratchpad/governance). Full output archived at
`papers/governance/cr0003_anomaly_scan_output.txt`; machine-readable register at
`papers/governance/phase2_anomaly_register.csv`; full JSON detail in the
scratchpad (`phase2_audit_report.json`).

Checks executed (every 21 primary cells + 3 context cells, all 3324 CSVs parsed):

1. **Duplicate records** — duplicate `(function, dimension, run)` keys in `per_run.csv` and `seed_schedule.csv`: **none found**.
2. **Duplicate seeds** — within-cell seed duplication across runs: **none**; cross-cell seed collisions inside each optimizer×suite: **0 in all 21 cells** (all seeds unique per suite×optimizer); `per_run` seed vs `seed_schedule` seed: **exact agreement** for every present key; gen-log `Seed` column vs schedule: exact agreement for every key present in the local schedule.
3. **Inconsistent run counts** — every present cell holds exactly runs 1..51 (cec2017/cec2013) or 1..25 (cec2011); gen-log files hold exactly 51/25 data rows each: **no violations**.
4. **Mixed numerical precision** — `per_run` `best_fitness`/`error` all `%.10e` (or `NaN`), `nfes` integer, `runtime_seconds` fixed-point; primary summaries all `%.10E`: **no deviations** in primary suites.
5. **Unexpected algorithm names** — `optimizer` and `suite` columns equal their directory names on every row of all 21 `per_run.csv` files: **no violations**.
6. **NaN/Inf** — no NaN/Inf in `best_fitness`, `nfes`, `runtime_seconds`, or any primary summary statistic. `error` is `NaN` on **all** cec2011 rows (by design — real-world problems carry no defined-optimum error; see A2-015..A2-027). One context file contains `N/A` tokens (A2-041).
7. **Out-of-protocol values** — `nfes` never exceeds MaxFES (10000·D for cec2017/cec2013; 150000 for cec2011); every `nfes < MaxFES` row carries `termination=target_error_reached` with `error ≤ 1e-8` (protocol-legitimate target stop, A2-001/A2-029/A2-032); no negative errors (not even above the `-1e-6` tolerance floor); no non-positive runtimes; all seeds within `[1, 2147483646]`; all function/dimension/run indices inside protocol ranges; termination values limited to `{max_evaluations, target_error_reached}`.
8. **Truncated convergence rows** — all gen-log rows are full-width with the final checkpoint column equal to MaxFES for the cell's dimension; curve files parse with strictly increasing `Eval`. The only irregular curve rows are a systematic writer convention — `Log10Error` left empty where `BestError ≤ 0` (log10 undefined) — not truncation (A2-002 group). 49 agsk/apgsk curve files end before MaxFES; each terminates exactly at a `BestError = 0` early-stop point (A2-003 group).
9. **Suite-internal FP sentinel consistency** (audit target only; full FP audit is task 5) — `fp_regime.sentinel` unique per suite across all 7 optimizers; cec2017 sentinel prefix `8bda40d8` matches the expected audit target; cec2011 `10fef059...`, cec2013 `16a3e309...` each internally consistent.
10. **verification.json** — verdict `CONSISTENT` with 0 hard failures in all 21 cells; cec2017/cec2011 checked 116/22 functions against imported references; cec2013 checked **0** (no external reference CSVs exist — vacuous verdict, A2-042..A2-048).

---

## 3. Task 3 — Expected-vs-actual coverage

Expected panel: cec2017 = 29 funcs (F2 excluded) × D10/30/50/100 × 51 runs;
cec2011 = 22 native-dimension problems × 25 runs; cec2013 = 28 funcs ×
D10/30/50 × 51 runs.

### 3.1 Per-optimizer row counts (`per_run.csv` and `seed_schedule.csv`)

| Suite | Optimizer | per_run rows (act/exp) | seed rows (act/exp) | cells (act/exp) | runs/cell complete |
|---|---|---|---|---|---|
| cec2017 | agsk | 5916/5916 | 5916/5916 | 116/116 | yes |
| cec2017 | **apgsk** | **1479/5916** | **1479/5916** | **29/116 (D100 only)** | yes (for D100) |
| cec2017 | atmals-gsk | 5916/5916 | 5916/5916 | 116/116 | yes |
| cec2017 | egsk | 5916/5916 | 5916/5916 | 116/116 | yes |
| cec2017 | fdb-agsk | 5916/5916 | 5916/5916 | 116/116 | yes |
| cec2017 | gsk | 5916/5916 | 5916/5916 | 116/116 | yes |
| cec2017 | dt-gsk | 5916/5916 | 5916/5916 | 116/116 | yes |
| cec2011 | all 7 | 550/550 each | 550/550 each | 22/22 each | yes |
| cec2013 | all 7 | 4284/4284 each | 4284/4284 each | 84/84 each | yes |

Panel totals: expected 75250 per-run rows; actual 70813 (deficit 4437 = the 87
missing apgsk cec2017 cells × 51 runs). Cross-check: termination counts
(69306 `max_evaluations` + 1507 `target_error_reached` = 70813) reconcile exactly.

### 3.2 Function sets, dimensions, and summaries

- cec2017 function set = {1, 3..30} (F2 excluded) in every cell, including apgsk's D100 subset; cec2013 = {1..28}; cec2011 = {1..22}.
- cec2011 native-dimension map identical across all 7 optimizers:
  `{1:6, 2:30, 3:1, 4:1, 5:30, 6:30, 7:20, 8:7, 9:126, 10:12, 11:120, 12:240, 13:6, 14:13, 15:15, 16:40, 17:140, 18:96, 19:96, 20:96, 21:26, 22:22}`.
- Summary CSVs: 29 rows per cec2017 dim file (all 4 dims present for **all seven** optimizers, apgsk included), 28 per cec2013 dim file, 22 in each cec2011 rollup; headers `Function,Best,Median,Mean,Worst,SD` everywhere.
- Curves and gen_logs: full (func×dim) coverage in all 21 cells (1554 + 1554 files).

### 3.3 Seed schedule cross-checks

- `seed_schedule.csv` and `per_run.csv` agree on every `(dim, func, run) → seed` mapping in all 21 cells.
- The schedules of all 7 optimizers are **identical** within cec2011 and cec2013 (unified cross-family schedule confirmed). Within cec2017 they are identical for 6 optimizers; apgsk's schedule is the D100-only subset of the family schedule (A2-005/A2-040).
- Spot-check of the documented formula `get_cec_seed(20240620, dim, func, run) % 2147483646 + 1` (`src/gsk_family/runners/seed_policy.py`): (10,1,1) → 32240721 and (6,1,1) → 28240709, both matching the stored schedules. Full formula validation over the complete schedule is Phase 2 task 4 (out of scope here).

### 3.4 Environment provenance snapshot (recorded for tasks 5/8)

Producer timestamps/commits from `environment.json` (recorded, not evaluated
here): cec2017 cells were produced 2026-07-08→09 at commits `f94817cc`,
`20cfed0a` (apgsk D100 rerun), `7483cac2`, `c35c26de`, `19f32fb8`, `31c5a04c`;
all cec2011 cells at `c35c26de` (2026-07-09); cec2013 cells at
`c35c26de`/`2d72f649` (2026-07-09→10). Mixed producer commits across the
campaign are a comparability question deferred to tasks 5 and 8. Full table in
`cr0003_anomaly_scan_output.txt` / `phase2_audit_report.json`.

---

## 4. Anomaly register (CR-0003)

Rules applied: every anomaly **logged, classified, traced, impact-evaluated;
none repaired**. The evidence tree was not modified. Severity: `hard` =
protocol/coverage defect requiring a phase-level decision; `soft` = tolerated
deviation, disclosed; `info` = by-design behaviour or observation recorded for
downstream tasks. Disposition for all 48 entries: **logged; not repaired**
(CR-0003 prohibits any in-place correction).

Totals: **5 hard, 5 soft, 38 info** (48 entries).

### 4.1 Root-cause group H1 — `cec2017/apgsk` partial D100 rerun (all 5 hard anomalies)

Anomalies A2-004, A2-005, A2-006, A2-007, A2-040 share one root cause:

- **Observation.** `per_run.csv`, `seed_schedule.csv`, `environment.json` and `run_config.json` in `benchmarks/cec_reference_results/cec2017/apgsk/` describe a **D100-only** campaign (`dimensions_run=[100]`, 51 runs, timestamp 2026-07-08T21:53:10, producer commit `20cfed0a`), while the same cell's summary CSVs (all 4 dims × 29 functions), `curves/` (116) and `gen_logs/` (116) cover the full four-dimension protocol.
- **Trace.** The file was last changed by commit `b251bbbb5` (2026-07-10, "Update ISM GSK Family"), an ancestor of the anchor commit; the working tree is clean, so the defect is **inside the frozen release**, not a local mutation. The D10/30/50 raw records were evidently overwritten when the D100 rerun wrote its outputs into the same cell before the release was committed.
- **Counter-evidence of original integrity.** The 4437 gen-log seeds for the 87 missing (func,dim) cells match the family unified schedule 4437/4437, and `verification.json` records `functions_checked=116, CONSISTENT` — i.e. the original full-panel apgsk runs existed, used unified seeding, and their summary-level results remain in the release.
- **Impact.**
  - Summary-level exhibits (Best/Median/Mean/Worst/SD tables) — **unaffected**; apgsk summaries are complete for all dims.
  - Per-run-based primary statistics (paired Wilcoxon, effect sizes, per-run win/tie/loss) for apgsk on cec2017 D10/D30/D50 — **not computable from `per_run.csv` of this release** (87 cells × 51 runs missing).
  - Environment/config provenance for the original apgsk D10/30/50 runs — lost from this cell (relevant to task 5).
  - Final per-run errors for the missing cells do exist in `gen_logs/CheckpointErrors_apgsk_F*_D{10,30,50}.csv` (final checkpoint column = MaxFES), and per-run seeds are recoverable from the family unified schedule; whether that derivation is admissible, or whether apgsk D10/30/50 must be re-run in staging and promoted via `scripts/promote_evidence.py` (Section 2.4), is a **phase-level decision requiring a change request — deliberately not performed by this audit**.
- **Gate 2 status: BLOCKER** for the planned paired primary analysis on cec2017 until dispositioned.

### 4.2 Soft anomalies

- **A2-003 / A2-009 / A2-031 / A2-034 — `TRUNCATED_CONVERGENCE (last_eval_ne_maxfes)`**, 34 curve files, agsk/apgsk only. Traced: every such curve terminates exactly at a `BestError = 0` point, matching the `target_error_reached` early-stop rule of these two optimizers; not data loss. Impact: convergence figures for these cells end at the stop point; disclose in figure captions (Section 6.7); also feeds the comparator-fairness/budget audit (tasks 7–8) since the other five optimizers always run to MaxFES.
- **A2-041 — `NAN_INF (N/A tokens)`**, `cec2020/agsk_cec2020_D05.csv`: functions F6 and F7 carry `N/A` for all five statistics (10 tokens). Traced to the imported AGSK context source not reporting these functions at D5. Impact: context-only; cec2020 is not part of the primary panel.

### 4.3 Informational entries

- **cec2011 `error=NaN` by design** (A2-015..A2-027, 550 rows × 7): the real-world suite has no defined-optimum error in `per_run.csv`; all cec2011 analyses must use `best_fitness`. The loader/statistics path already operates on fitness for cec2011.
- **Early stops** (A2-001, A2-029, A2-032): 1507 runs across agsk/apgsk reached `error ≤ 1e-8` and stopped early — protocol-legitimate; all other rows ran to exactly MaxFES.
- **Empty `Log10Error` writer convention** (A2-002 group, ~150 curve files): `Log10Error` empty where `BestError ≤ 0` (log10 undefined) — systematic, values intact; log-scale plots need a disclosed display floor.
- **Vacuous cec2013 verification** (A2-042..A2-048): no external reference CSVs exist for cec2013, so `verification.json` verdicts are vacuously `CONSISTENT`; evaluator equivalence for cec2013 rests on Phase 2 tasks 6 and 8.

### 4.4 Full register

| ID | Class | Sev. | Suite/Optimizer | Count | Description | Traced source | Impact |
|----|-------|------|-----------------|-------|-------------|---------------|--------|
| A2-001 | PROTOCOL_OBSERVATION | info | cec2017/agsk | 404 | target_error_reached early stops: 404 runs (protocol-legitimate stopping rule; nfes<MaxFES by design) | `benchmarks/cec_reference_results/cec2017/agsk/per_run.csv` | none; budget accounting per stopping rule |
| A2-002 | PROTOCOL_OBSERVATION | info | cec2017/agsk | 8 | 8 curve files leave Log10Error empty where BestError<=0 (log10 undefined); systematic writer convention | `benchmarks/cec_reference_results/cec2017/agsk/curves` | log-scale plots need a disclosed display floor (Section 6.7); values themselves intact |
| A2-003 | TRUNCATED_CONVERGENCE | soft | cec2017/agsk | 8 | curve issue last_eval_ne_maxfes: 8 files | `benchmarks/cec_reference_results/cec2017/agsk/curves` | trace ends before MaxFES (early-stop rule; each ends at BestError=0) |
| A2-004 | COVERAGE_MISMATCH | hard | cec2017/apgsk | 1 | per_run rows 1479/5916, cells 29/116; dims present=[100] | `benchmarks/cec_reference_results/cec2017/apgsk/per_run.csv` | per-run evidence absent for missing cells; paired per-run statistics not computable from per_run.csv for the missing dims |
| A2-005 | COVERAGE_MISMATCH | hard | cec2017/apgsk | 1 | seed_schedule rows 1479/5916 | `benchmarks/cec_reference_results/cec2017/apgsk/seed_schedule.csv` | seed schedule incomplete for this cell |
| A2-006 | METADATA_INCONSISTENT | hard | cec2017/apgsk | 1 | environment/run_config dims [100]/100 != protocol [10, 30, 50, 100]; env timestamp=2026-07-08T21:53:10 git=20cfed0a | `benchmarks/cec_reference_results/cec2017/apgsk` | cell metadata describes a partial rerun; environment/config provenance for the other dims is not present in this cell |
| A2-007 | COVERAGE_MISMATCH | hard | cec2017/apgsk | 4437 | gen_log run seeds for 4437 (dim,func,run) keys absent from this cell's seed_schedule; 4437/4437 match the family unified schedule | `benchmarks/cec_reference_results/cec2017/apgsk/gen_logs` | local schedule incomplete; original runs consistent with unified seeding |
| A2-008 | PROTOCOL_OBSERVATION | info | cec2017/apgsk | 5 | 5 curve files leave Log10Error empty where BestError<=0 (log10 undefined); systematic writer convention | `benchmarks/cec_reference_results/cec2017/apgsk/curves` | log-scale plots need a disclosed display floor (Section 6.7); values themselves intact |
| A2-009 | TRUNCATED_CONVERGENCE | soft | cec2017/apgsk | 5 | curve issue last_eval_ne_maxfes: 5 files | `benchmarks/cec_reference_results/cec2017/apgsk/curves` | trace ends before MaxFES (early-stop rule; each ends at BestError=0) |
| A2-010 | PROTOCOL_OBSERVATION | info | cec2017/atmals-gsk | 9 | 9 curve files leave Log10Error empty where BestError<=0 (log10 undefined); systematic writer convention | `benchmarks/cec_reference_results/cec2017/atmals-gsk/curves` | log-scale plots need a disclosed display floor (Section 6.7); values themselves intact |
| A2-011 | PROTOCOL_OBSERVATION | info | cec2017/egsk | 10 | 10 curve files leave Log10Error empty where BestError<=0 (log10 undefined); systematic writer convention | `benchmarks/cec_reference_results/cec2017/egsk/curves` | log-scale plots need a disclosed display floor (Section 6.7); values themselves intact |
| A2-012 | PROTOCOL_OBSERVATION | info | cec2017/fdb-agsk | 7 | 7 curve files leave Log10Error empty where BestError<=0 (log10 undefined); systematic writer convention | `benchmarks/cec_reference_results/cec2017/fdb-agsk/curves` | log-scale plots need a disclosed display floor (Section 6.7); values themselves intact |
| A2-013 | PROTOCOL_OBSERVATION | info | cec2017/gsk | 9 | 9 curve files leave Log10Error empty where BestError<=0 (log10 undefined); systematic writer convention | `benchmarks/cec_reference_results/cec2017/gsk/curves` | log-scale plots need a disclosed display floor (Section 6.7); values themselves intact |
| A2-014 | PROTOCOL_OBSERVATION | info | cec2017/dt-gsk | 12 | 12 curve files leave Log10Error empty where BestError<=0 (log10 undefined); systematic writer convention | `benchmarks/cec_reference_results/cec2017/dt-gsk/curves` | log-scale plots need a disclosed display floor (Section 6.7); values themselves intact |
| A2-015 | NAN_INF | info | cec2011/agsk | 550 | error=NaN on all 550 rows: real-world suite carries no defined-optimum error in per_run; by design | `benchmarks/cec_reference_results/cec2011/agsk/per_run.csv` | cec2011 analyses must use best_fitness, not error |
| A2-016 | PROTOCOL_OBSERVATION | info | cec2011/agsk | 5 | 5 curve files leave Log10Error empty where BestError<=0 (log10 undefined); systematic writer convention | `benchmarks/cec_reference_results/cec2011/agsk/curves` | log-scale plots need a disclosed display floor (Section 6.7); values themselves intact |
| A2-017 | NAN_INF | info | cec2011/apgsk | 550 | error=NaN on all 550 rows: real-world suite carries no defined-optimum error in per_run; by design | `benchmarks/cec_reference_results/cec2011/apgsk/per_run.csv` | cec2011 analyses must use best_fitness, not error |
| A2-018 | PROTOCOL_OBSERVATION | info | cec2011/apgsk | 5 | 5 curve files leave Log10Error empty where BestError<=0 (log10 undefined); systematic writer convention | `benchmarks/cec_reference_results/cec2011/apgsk/curves` | log-scale plots need a disclosed display floor (Section 6.7); values themselves intact |
| A2-019 | NAN_INF | info | cec2011/atmals-gsk | 550 | error=NaN on all 550 rows: real-world suite carries no defined-optimum error in per_run; by design | `benchmarks/cec_reference_results/cec2011/atmals-gsk/per_run.csv` | cec2011 analyses must use best_fitness, not error |
| A2-020 | PROTOCOL_OBSERVATION | info | cec2011/atmals-gsk | 5 | 5 curve files leave Log10Error empty where BestError<=0 (log10 undefined); systematic writer convention | `benchmarks/cec_reference_results/cec2011/atmals-gsk/curves` | log-scale plots need a disclosed display floor (Section 6.7); values themselves intact |
| A2-021 | NAN_INF | info | cec2011/egsk | 550 | error=NaN on all 550 rows: real-world suite carries no defined-optimum error in per_run; by design | `benchmarks/cec_reference_results/cec2011/egsk/per_run.csv` | cec2011 analyses must use best_fitness, not error |
| A2-022 | PROTOCOL_OBSERVATION | info | cec2011/egsk | 5 | 5 curve files leave Log10Error empty where BestError<=0 (log10 undefined); systematic writer convention | `benchmarks/cec_reference_results/cec2011/egsk/curves` | log-scale plots need a disclosed display floor (Section 6.7); values themselves intact |
| A2-023 | NAN_INF | info | cec2011/fdb-agsk | 550 | error=NaN on all 550 rows: real-world suite carries no defined-optimum error in per_run; by design | `benchmarks/cec_reference_results/cec2011/fdb-agsk/per_run.csv` | cec2011 analyses must use best_fitness, not error |
| A2-024 | PROTOCOL_OBSERVATION | info | cec2011/fdb-agsk | 5 | 5 curve files leave Log10Error empty where BestError<=0 (log10 undefined); systematic writer convention | `benchmarks/cec_reference_results/cec2011/fdb-agsk/curves` | log-scale plots need a disclosed display floor (Section 6.7); values themselves intact |
| A2-025 | NAN_INF | info | cec2011/gsk | 550 | error=NaN on all 550 rows: real-world suite carries no defined-optimum error in per_run; by design | `benchmarks/cec_reference_results/cec2011/gsk/per_run.csv` | cec2011 analyses must use best_fitness, not error |
| A2-026 | PROTOCOL_OBSERVATION | info | cec2011/gsk | 5 | 5 curve files leave Log10Error empty where BestError<=0 (log10 undefined); systematic writer convention | `benchmarks/cec_reference_results/cec2011/gsk/curves` | log-scale plots need a disclosed display floor (Section 6.7); values themselves intact |
| A2-027 | NAN_INF | info | cec2011/dt-gsk | 550 | error=NaN on all 550 rows: real-world suite carries no defined-optimum error in per_run; by design | `benchmarks/cec_reference_results/cec2011/dt-gsk/per_run.csv` | cec2011 analyses must use best_fitness, not error |
| A2-028 | PROTOCOL_OBSERVATION | info | cec2011/dt-gsk | 6 | 6 curve files leave Log10Error empty where BestError<=0 (log10 undefined); systematic writer convention | `benchmarks/cec_reference_results/cec2011/dt-gsk/curves` | log-scale plots need a disclosed display floor (Section 6.7); values themselves intact |
| A2-029 | PROTOCOL_OBSERVATION | info | cec2013/agsk | 558 | target_error_reached early stops: 558 runs (protocol-legitimate stopping rule; nfes<MaxFES by design) | `benchmarks/cec_reference_results/cec2013/agsk/per_run.csv` | none; budget accounting per stopping rule |
| A2-030 | PROTOCOL_OBSERVATION | info | cec2013/agsk | 11 | 11 curve files leave Log10Error empty where BestError<=0 (log10 undefined); systematic writer convention | `benchmarks/cec_reference_results/cec2013/agsk/curves` | log-scale plots need a disclosed display floor (Section 6.7); values themselves intact |
| A2-031 | TRUNCATED_CONVERGENCE | soft | cec2013/agsk | 11 | curve issue last_eval_ne_maxfes: 11 files | `benchmarks/cec_reference_results/cec2013/agsk/curves` | trace ends before MaxFES (early-stop rule; each ends at BestError=0) |
| A2-032 | PROTOCOL_OBSERVATION | info | cec2013/apgsk | 545 | target_error_reached early stops: 545 runs (protocol-legitimate stopping rule; nfes<MaxFES by design) | `benchmarks/cec_reference_results/cec2013/apgsk/per_run.csv` | none; budget accounting per stopping rule |
| A2-033 | PROTOCOL_OBSERVATION | info | cec2013/apgsk | 10 | 10 curve files leave Log10Error empty where BestError<=0 (log10 undefined); systematic writer convention | `benchmarks/cec_reference_results/cec2013/apgsk/curves` | log-scale plots need a disclosed display floor (Section 6.7); values themselves intact |
| A2-034 | TRUNCATED_CONVERGENCE | soft | cec2013/apgsk | 10 | curve issue last_eval_ne_maxfes: 10 files | `benchmarks/cec_reference_results/cec2013/apgsk/curves` | trace ends before MaxFES (early-stop rule; each ends at BestError=0) |
| A2-035 | PROTOCOL_OBSERVATION | info | cec2013/atmals-gsk | 8 | 8 curve files leave Log10Error empty where BestError<=0 (log10 undefined); systematic writer convention | `benchmarks/cec_reference_results/cec2013/atmals-gsk/curves` | log-scale plots need a disclosed display floor (Section 6.7); values themselves intact |
| A2-036 | PROTOCOL_OBSERVATION | info | cec2013/egsk | 6 | 6 curve files leave Log10Error empty where BestError<=0 (log10 undefined); systematic writer convention | `benchmarks/cec_reference_results/cec2013/egsk/curves` | log-scale plots need a disclosed display floor (Section 6.7); values themselves intact |
| A2-037 | PROTOCOL_OBSERVATION | info | cec2013/fdb-agsk | 11 | 11 curve files leave Log10Error empty where BestError<=0 (log10 undefined); systematic writer convention | `benchmarks/cec_reference_results/cec2013/fdb-agsk/curves` | log-scale plots need a disclosed display floor (Section 6.7); values themselves intact |
| A2-038 | PROTOCOL_OBSERVATION | info | cec2013/gsk | 6 | 6 curve files leave Log10Error empty where BestError<=0 (log10 undefined); systematic writer convention | `benchmarks/cec_reference_results/cec2013/gsk/curves` | log-scale plots need a disclosed display floor (Section 6.7); values themselves intact |
| A2-039 | PROTOCOL_OBSERVATION | info | cec2013/dt-gsk | 10 | 10 curve files leave Log10Error empty where BestError<=0 (log10 undefined); systematic writer convention | `benchmarks/cec_reference_results/cec2013/dt-gsk/curves` | log-scale plots need a disclosed display floor (Section 6.7); values themselves intact |
| A2-040 | DUPLICATE_SEED | hard | cec2017/apgsk | 1 | seed schedules differ across optimizers despite unified policy (apgsk carries the D100-only subset) | `benchmarks/cec_reference_results/cec2017/apgsk/seed_schedule.csv` | pairing assumption not demonstrable from this cell's schedule alone; gen_logs confirm unified seeding of the original runs |
| A2-041 | NAN_INF | soft | cec2020/agsk | 10 | non_numeric_token[N/A]: 10 (functions F6/F7 at D5 report N/A for all five statistics) | `benchmarks/cec_reference_results/cec2020/agsk/agsk_cec2020_D05.csv` | missing-value token in imported context summary; context-only, not in primary panel |
| A2-042 | VERIFICATION_VACUOUS | info | cec2013/agsk | 1 | verification checked 0 functions (missing_reference=84); verdict vacuously CONSISTENT | `benchmarks/cec_reference_results/cec2013/agsk/verification.json` | no external reference cross-check exists for this suite cell; equivalence relies on Phase 2 tasks 6 and 8 |
| A2-043 | VERIFICATION_VACUOUS | info | cec2013/apgsk | 1 | verification checked 0 functions (missing_reference=84); verdict vacuously CONSISTENT | `benchmarks/cec_reference_results/cec2013/apgsk/verification.json` | no external reference cross-check exists for this suite cell; equivalence relies on Phase 2 tasks 6 and 8 |
| A2-044 | VERIFICATION_VACUOUS | info | cec2013/atmals-gsk | 1 | verification checked 0 functions (missing_reference=84); verdict vacuously CONSISTENT | `benchmarks/cec_reference_results/cec2013/atmals-gsk/verification.json` | no external reference cross-check exists for this suite cell; equivalence relies on Phase 2 tasks 6 and 8 |
| A2-045 | VERIFICATION_VACUOUS | info | cec2013/egsk | 1 | verification checked 0 functions (missing_reference=84); verdict vacuously CONSISTENT | `benchmarks/cec_reference_results/cec2013/egsk/verification.json` | no external reference cross-check exists for this suite cell; equivalence relies on Phase 2 tasks 6 and 8 |
| A2-046 | VERIFICATION_VACUOUS | info | cec2013/fdb-agsk | 1 | verification checked 0 functions (missing_reference=84); verdict vacuously CONSISTENT | `benchmarks/cec_reference_results/cec2013/fdb-agsk/verification.json` | no external reference cross-check exists for this suite cell; equivalence relies on Phase 2 tasks 6 and 8 |
| A2-047 | VERIFICATION_VACUOUS | info | cec2013/gsk | 1 | verification checked 0 functions (missing_reference=84); verdict vacuously CONSISTENT | `benchmarks/cec_reference_results/cec2013/gsk/verification.json` | no external reference cross-check exists for this suite cell; equivalence relies on Phase 2 tasks 6 and 8 |
| A2-048 | VERIFICATION_VACUOUS | info | cec2013/dt-gsk | 1 | verification checked 0 functions (missing_reference=84); verdict vacuously CONSISTENT | `benchmarks/cec_reference_results/cec2013/dt-gsk/verification.json` | no external reference cross-check exists for this suite cell; equivalence relies on Phase 2 tasks 6 and 8 |

---

## 5. Gate 2 implications from tasks 1–3

1. **BLOCKER (change-request required): `cec2017/apgsk` per-run gap** (register group H1). Options for phase-level disposition, in evidentiary order: (a) re-run apgsk cec2017 D10/30/50 in staging with frozen code/seeds and promote via `scripts/promote_evidence.py` as a superseding release; or (b) pre-register a documented derivation of per-run final errors from the cell's `gen_logs` final-checkpoint column (all seeds verified against the family unified schedule). Neither action was taken by this audit.
2. Everything else in tasks 1–3 scope **passes**: layout canonical, no doubled suites, machine validation PASS, duplicates/NaN/Inf/precision/name/protocol-range checks clean, coverage exact in 20 of 21 primary cells and both context suites in expected scope.
3. Items handed to later Phase 2 tasks: full seed-formula validation (task 4); FP/environment audit over mixed producer commits (task 5); cec2013 evaluator equivalence without external references (task 6); early-stop budget accounting in the cost study (task 7); comparator provenance classes and cec2013 reference absence (task 8).

## 6. Artifacts produced by this audit

| Artifact | Path |
|---|---|
| This audit | `papers/governance/benchmark_protocol_audit.md` |
| Machine validation archive | `papers/governance/machine_validation_output.txt` |
| CR-0003 scan script | `papers/governance/cr0003_anomaly_scan.py` |
| CR-0003 scan full output | `papers/governance/cr0003_anomaly_scan_output.txt` |
| Machine-readable anomaly register | `papers/governance/phase2_anomaly_register.csv` |

Reproduction: `python -m gsk_family.cli.validate --references benchmarks/cec_reference_results`
then `python papers/governance/cr0003_anomaly_scan.py <output_dir>` from the repo root at the anchor commit.
