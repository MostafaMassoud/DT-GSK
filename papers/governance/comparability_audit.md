# Comparability audit — comparator fairness and provenance (Phase 2, task 8)

- **Date:** 2026-07-10
- **Phase / task:** Phase 2 — Immutable empirical evidence, benchmark, and provenance audit; task 8 (comparator provenance, Section 6.3 A–D classification, egsk solver provenance).
- **Anchor commit:** `262fc16c91fbe5608a1a0b0c5df3cbcd009edc21` (HEAD verified identical at audit time).
- **Evidence tree (read-only):** `benchmarks/cec_reference_results/` — hashed and read only.
- **Method evidence:** `papers/governance/audit_evidence/phase2_tasks678_audit.py` / `phase2_tasks678_audit.json`; `evaluator_hash_inventory.csv`; git-history provenance commands recorded in the machine output and below.
- **Companions:** MaxFES/evaluator evidence in `benchmark_protocol_audit_part2.md`; FP/environment in `fp_environment_audit.md`; seeds/pairing detail in `seed_and_pairing_audit.md`; per-cell inventory in `data_ledger.csv` (this file supplies the A–D values its `comparability_status` column points to).
- **Quarantine compliance:** `results/` (including the live `results/_ablation/` campaign) was neither read nor interpreted (Section 6.10).

---

## 1. Section 6.3 fairness checklist — evidence per criterion (primary panel)

Primary panel = 7 optimizers (`gsk`, `agsk`, `apgsk`, `fdb-agsk`, `atmals-gsk`, `egsk`, `dt-gsk`)
× {cec2017 D10/30/50/100 × 29 funcs × 51 runs; cec2013 D10/30/50 × 28 funcs × 51 runs;
cec2011 22 native-dim problems × 25 runs}.

| Criterion | Evidence | Status |
|---|---|---|
| Identical objective definitions and benchmark data | Single hashed evaluator package (`cec_suite_python`, 103-file SHA-256 inventory); `git diff` across all seven producing commits (`31c5a04c4` → `2d72f6497`) restricted to `src/gsk_family/` + `benchmarks/cec_suite_python/` is **empty** | PASS |
| Identical function sets and dimensions | cec2017: 29 funcs (F2 excluded) × D10/30/50/100 in 7/7 per_run files; cec2013: 28 × D10/30/50 in 7/7; cec2011: 22 native-dim instances in 7/7 | PASS (apgsk-cec2017 per_run metadata gap: Section 5) |
| Identical / demonstrably equivalent budgets | 10,000·D (cec2017/cec2013), 150,000 (cec2011); `max_nfes_override: 0` in 21/21 cells; zero over-budget rows | PASS |
| Matching endpoint/error definitions and floors | `statistics_basis` uniform per suite (error_vs_optimum for cec2017/cec2013; raw_objective for cec2011); `report_zero_tol = 1e-8` uniform; `compute_error` floor identical | PASS |
| Compatible run and seed designs | Unified optimizer-independent formula `get_cec_seed(20240620, dim, func, run)`; `seed_schedule.csv` SHA-256 identical across all 7 optimizers for cec2013 and cec2011; cec2017 identical for 6/7, apgsk file is the exact D100 subset of the common schedule; spot-check of per_run seeds vs formula: all match | PASS (apgsk caveat, Section 5) |
| Valid pairing for planned paired tests | Pairing key suite × function × dimension × run with identical seeds and shared runner-generated X0 per key (`initial_population_policy: runner_supplied_X0`) | PASS for 6/7 × cec2017 and 7/7 × cec2013/cec2011; apgsk cec2017 D10/30/50 pairing recoverable from `gen_logs` (seeds verified against the unified formula) |
| Comparable initialization, boundary handling, failure policy | Initialization: identical shared X0 per (dim,func,run) drawn by the runner. Boundary handling: each optimizer keeps its reference-faithful repair rule (inherent to comparing published algorithms; disclosed, not unified). Failure policy: `skipped_cells: []`, no failed runs, non-finite fitness rejected by adapter contract | PASS (boundary-handling heterogeneity disclosed) |
| Transparent parameter-tuning effort | Baselines run their reference-implementation constants (`optimizer_options: {}`). NOTE (CR-0023, 2026-08-25): the resulting NP = 100 is a panel normalization traceable to eGSK's published CEC2017 panel, NOT each comparator's own published rule (AGSK specifies 20D, APGSK 200D, FDB-AGSK 40n); the earlier wording \"pop_size 100 where applicable\" implied the latter. DT-GSK runs NP = 5D. The asymmetry is disclosed in the main text and is the subject of reviewer point R1.3/R2.2; it was not a controlled variable.; dt-gsk runs the frozen `pub` profile (`run_config.profile: "pub"`), a byte-locked faithful port of the paper-facing configuration (`_dt_profiles.py`, locked by `tests/unit/test_dt_profiles.py`); no opt-in candidate profile (`ism_profile` A/B/C) appears in any panel run_config | PASS |
| Objective-call accounting incl. local search | dt-gsk BudgetController single cap (all LS/polish/escape/restart evals counted); egsk SLSQP refine calls counted into nfes; atmals-gsk has no hidden LS evals — see `benchmark_protocol_audit_part2.md` §7.3–7.5 | PASS |
| Algorithm version and implementation provenance | Per-cell `environment.json` records command, git commit, host, timestamp; code-identity across commits proven | PASS |
| Imported vs locally produced vs independently verified | See Section 2 | Recorded |

## 2. Origin classification: imported vs locally produced

**All 21 primary-panel cells are LOCALLY PRODUCED** by the Python runner on host
`HUAWEI-MMASOUD`, Python 3.10.11, Windows, threefry RNG, python backend
(`environment.json` `command: "python run.py --root . --optimizer <opt> --suite <suite> …"`,
`output_dir: results\_run_all\<opt>\<suite>`, later curated into the evidence tree; commit
`b251bbbb5` carries the per_run/metadata refresh, 2026-07-10).

| Suite | Producing commits (environment.json) | Run window | Cells |
|---|---|---|---|
| cec2017 | `31c5a04c4` (gsk), `f94817cc4` (agsk), `20cfed0ac` (apgsk D100 re-run), `19f32fb83` (fdb-agsk), `7483cac2e` (atmals-gsk), `c35c26de7` (egsk, dt-gsk) | 2026-07-08 12:24 → 2026-07-09 14:45 | 7 |
| cec2011 | `c35c26de7` (all seven) | 2026-07-09 15:27 → 20:36 | 7 |
| cec2013 | `c35c26de7` (gsk, agsk, apgsk), `2d72f6497` (fdb-agsk, atmals-gsk, egsk, dt-gsk) | 2026-07-09 21:14 → 2026-07-10 08:20 | 7 |

Code-identity across all these commits was verified (empty diffs over `src/` and the evaluator
package), so the rolling campaign is equivalent to a single-commit campaign for fairness purposes.

**Summary-table provenance (numeric verification).** Every committed per-dimension summary CSV was
recomputed from its cell's `per_run.csv` (error basis for cec2017/cec2013; raw best-fitness basis
for cec2011; identical Best/Median/Mean/Worst/sample-SD conventions as `stats.py::summarize`):

- **100% agreement on Best, Median, Mean, Worst** for every function in every cell (0 mismatches).
- SD agrees except for 83 isolated SD entries (cec2011 rollup rows duplicate their per-dim rows in
  this count) with relative deviations ≤ 1.7e-3 (median ~2e-9; two apgsk-cec2013 F28 entries show
  SD ≈ 1.8e-12/8.8e-12 vs recomputed 0 — absolute deviation ≤ 9e-12) — exactly the round-trip
  artifact of recomputing a sample SD from per_run values stored at 11 significant digits
  (`%.10e`), amplified by cancellation where SD ≪ mean. **No summary value has independent
  provenance from the per-run records** — summaries are derived tables of the same runs.
- `apgsk` cec2017 D10/30/50 summaries (per_run absent for those dims) were instead verified
  against `gen_logs/CheckpointErrors_apgsk_F*_D{10,30,50}.csv` final-checkpoint columns:
  **435/435 statistics match exactly** (29 funcs × 5 stats × 3 dims).
- Older aggregate tables committed 2026-06-27 → 2026-07-03 (the tree's earlier "imported reference"
  era) were superseded by commit `b251bbbb5`; where retained unchanged (e.g., cec2011 summaries,
  apgsk cec2017 summaries), the fresh 2026-07 runs reproduced them, confirming deterministic
  reproduction under the unified seed schedule (verification.json all-tie or near-tie verdicts).

**Verification status.** `verification.json` verdicts are CONSISTENT in 21/21 cells. Caveat: for
cec2013 the comparison is **vacuous** (`functions_checked: 0`, `missing_reference: 84` — no prior
reference tables exist for that suite), so cec2013 cells are locally produced *without* an
external cross-check baseline; their integrity rests on the machine validation, seed/budget
audits, and summary-consistency checks above. No cell is "independently verified" in the
Section 6.3 sense (all runs from one host/environment); this is a disclosed limitation, not a
defect.

**Context cells are IMPORTED, summary-only:** `cec2020/agsk` (4 aggregate tables),
`cec2013lsgo/decc-g`, `cec2013lsgo/mos` (1 aggregate table each). No per_run.csv,
no environment.json, no run_config.json, no seed schedule — published aggregate values curated
into the tree (per the tree README's citation-practice rules).

## 3. A–D classification (Section 6.3) — one status per comparison cell

Granularity matches `data_ledger.csv` (algorithm × suite × dimension); its
`comparability_status = pending-task8` values resolve to the table below.

### Class A — directly comparable, same frozen protocol, complete per-run evidence

| Cells | Count |
|---|---|
| cec2017 × D10/30/50/100 × {gsk, agsk, fdb-agsk, atmals-gsk, egsk, dt-gsk} | 24 |
| cec2017 × D100 × apgsk | 1 |
| cec2013 × D10/30/50 × all seven optimizers | 21 |
| cec2011 × all native dims × all seven optimizers | 7 × 16-dim panel (112 ledger rows) |

Rationale: locally produced under one frozen protocol (identical evaluator hashes, code-identical
commits, unified seeds, shared X0, identical budgets/floors, complete per-run records), verified
run counts, no failures. egsk carries the mandatory solver-substitution disclosure of Section 4
(class A within the panel definition "egsk = the Python SLSQP port").

### Provisional class C — pending Gate 2 decision (upgrade path to A defined)

| Cells | Count |
|---|---|
| cec2017 × D10/30/50 × apgsk | 3 |

Defect (anomaly P2-A5): the canonical `per_run.csv`, `seed_schedule.csv`, `run_config.json`, and
`environment.json` in `cec2017/apgsk/` describe only the 2026-07-08 **D100 re-run** (dims [100],
1479 rows); the four-dimension metadata was overwritten when the cell was refreshed. The D10/30/50
evidence content **is present and verified** inside the same immutable cell — `gen_logs/`
checkpoint logs carry per-run `Run,Seed,…,E<final>` rows for all 29 × 51 runs per dim; their seeds
match the unified formula exactly and their final errors reproduce the committed summaries
435/435 — but the producing environment/commit for those dims is unrecorded in-cell
(logs+summaries date to the 2026-06-27 curation).

Fail-closed default: **C (descriptively comparable)** until Gate 2 chooses one of:

1. **Designate-source decision:** formally designate `gen_logs/CheckpointErrors_apgsk_F*_D{10,30,50}.csv`
   final-checkpoint columns as the authoritative per-run source for these three cells (data is
   complete, immutable, seed-verified, summary-consistent; pairing key fully recoverable) and record
   an `assumption_register.csv` entry for the unrecorded producing environment; then reclassify **A**
   with disclosure; or
2. **Reproduce-and-promote:** re-run apgsk cec2017 D10/30/50 with the frozen code (deterministic
   byte-reproduction was already demonstrated by the D100 re-run and by verification all-tie
   verdicts) and promote via `scripts/promote_evidence.py` into a new release subtree; classify **A**
   with clean metadata.

Until then, apgsk may appear at cec2017 D10/30/50 only in clearly-labeled descriptive contexts,
not in the planned paired primary inference at those dims (loaders reading `per_run.csv` alone
would silently drop these cells — an additional reason to resolve before Phase 6).

### Class D — non-comparable; excluded from formal comparison (context-only)

| Cells | Count |
|---|---|
| cec2020 × agsk (D5/10/15/20 aggregate tables) | 4 |
| cec2013lsgo × decc-g, mos (aggregate tables) | 2 |

Rationale: imported aggregate-only values with no per-run records, no in-repo protocol metadata,
different budgets (CEC2020 per-dim budgets; LSGO 3M), and **no protocol-matched counterpart cell
in the release** (no family member was run on cec2020/cec2013lsgo in this release) — there is no
valid formal comparison for them to enter. Permitted use: background/context sentences citing the
published sources with budget caveats (cf. EG-002/EG-012 discipline); prohibited: any appearance
in a panel table, rank, test, or effect-size computation.

### Class B — none

No cell qualifies as "immutable imported evidence with verified protocol": the context imports
lack verifiable protocol metadata, and everything else is locally produced.

## 4. eGSK solver provenance (EG-011) — verified determination

**Published mechanism:** eGSK's late-stage refinement is a sequential-quadratic-programming
(SQP) polish per `jawad2024egsk` (Sect. 3.2.3); the concrete solver, MATLAB `fmincon`
(Optimization Toolbox), comes from the family's vendored reference implementation
(`egsk_ip_refine.m`, see `egsk.py` docstring), not from the article — the published PDF never
names fmincon (corrected 2026-07-31, round-3 CITE-REP-01).

**Local implementation:** `src/gsk_family/optimizers/egsk.py` substitutes
`scipy.optimize.minimize(method="SLSQP")` (module docstring lines 16–22; `_egsk_ip_refine` lines
156–212; result params record `"ip_solver": "scipy-SLSQP"` and the note "statistical-equivalence
port"). The GSK population core is byte-faithful (shared kernel + Threefry); only the polish
solver differs.

**Which provenance produced the committed cec-panel cells — VERIFIED: the SciPy-SLSQP port, for
all three suites.**

- `environment.json` in `cec2017/egsk`, `cec2013/egsk`, `cec2011/egsk`: local `run.py` commands,
  commits `c35c26de7`/`2d72f6497`, timestamps 2026-07-09/10, python backend, unified seeds.
- The committed egsk summary tables are numerically exact aggregations of the committed SLSQP-port
  `per_run.csv` (100% Best/Median/Mean/Worst; SD round-trip artifacts only) — they are not the
  historical fmincon tables.
- Git history: fmincon-era egsk aggregate tables existed at commits `296c36036` (2026-06-27),
  `a9facf8a1` (2026-07-02), `d18b1d0b0` (2026-07-03) and **differ numerically** from the current
  tables (e.g., cec2017 D10 F5/F7/F8 rows); they were superseded at `b251bbbb5` (2026-07-10).
  **No fmincon-derived egsk value remains anywhere in the working-tree evidence.** (This also
  falsifies the earlier planning note that "the panel still uses fmincon reference CSVs" —
  stale as of the 2026-07-09 refresh; flagged for `instruction_precedence.md`/`asset_map.md`
  under task 11.)

**Binding no-mixing rule (recorded for Phases 6–10):**

> R-EGSK-1. Within any single exhibit (table, figure, statistical test, rank set, or effect-size
> computation), egsk values MUST come exclusively from the SciPy-SLSQP port cells of the selected
> evidence release. MATLAB-fmincon-derived egsk values — whether from git history, the published
> paper's tables, or any external CSV — MUST NOT be substituted for, averaged with, or displayed
> beside the port's values inside one exhibit. Published fmincon numbers may appear only as
> clearly-labeled literature citations in prose/related-work context, never as a panel column.
> No numerical-equivalence claim between the two backends is permitted (EG-011 narrow
> disposition); the manuscript's panel description must disclose the substitution.

The panel comparison is therefore a comparison against "eGSK (Python port, SLSQP polish)" — the
methods section must name it as such.

## 5. Anomalies and Gate 2 decision items

| ID | Item | Severity | Owner/next |
|---|---|---|---|
| P2-A5 | apgsk cec2017 cell metadata covers D100 only; D10/30/50 per-run evidence lives in gen_logs with unrecorded producing environment | **major — Gate 2 decision required** (designate-source vs reproduce-and-promote; provisional class C at D10/30/50) | Gate 2 / P4, P5 |
| P2-A6 | `benchmarks/cec_reference_results/README.md` still describes the tree as imported published tables for 5 optimizers — stale vs the current 7-optimizer locally-produced panel; misleading provenance documentation | minor (administrative; evidence unaffected) | change-request pipeline (doc fix; never hand-edit evidence) |
| P2-A7 | cec2013 verification.json verdicts vacuous (0 functions checked, 84 missing references) | minor (disclosed) | note in evidence_readiness_report |
| P2-A8 | Rolling multi-commit campaign (6 commits) rather than a single frozen commit | resolved (empty code diffs proven) | recorded here |
| P2-A9 | Stale planning memory "panel still uses fmincon reference CSVs" falsified by this audit | minor | task 11 instruction_precedence/asset_map updates |
| — | No independently-verified (second-environment) cell exists; all runs single host | disclosed limitation | threats-to-validity prose |

**Bottom line for Gate 2:** 158 of 161 primary-panel ledger cells classify A now; 3 (apgsk
cec2017 D10/30/50) are provisional C with two defined upgrade paths; 6 context cells are D
(context-only, excluded from formal comparison); egsk provenance is uniquely determined as the
SciPy-SLSQP port with rule R-EGSK-1 binding all exhibits.
