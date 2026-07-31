# Benchmark protocol audit — part 2 (Phase 2, tasks 6–7: evaluator equivalence, MaxFES accounting)

- **Date:** 2026-07-10
- **Phase / tasks:** Phase 2 — Immutable empirical evidence, benchmark, and provenance audit; task 6 (evaluator equivalence) and task 7 (MaxFES and objective-call accounting).
- **Anchor commit:** `262fc16c91fbe5608a1a0b0c5df3cbcd009edc21` (HEAD verified identical at audit time).
- **Evidence tree (read-only):** `benchmarks/cec_reference_results/` — hashed and read only; never written, renamed, or touched.
- **Method evidence:** `papers/governance/audit_evidence/phase2_tasks678_audit.py` (audit script), `phase2_tasks678_audit.json` (machine output), `evaluator_hash_inventory.csv` (103-file SHA-256 inventory).
- **Coordination:** this file extends `benchmark_protocol_audit.md`; the Gate 2 merge folds these sections in. Comparator provenance (task 8) is in `comparability_audit.md`.
- **Quarantine compliance:** `results/` (including the live `results/_ablation/` campaign) was neither read nor interpreted (Section 6.10).

---

## Task 6 — Evaluator equivalence

### 6.1 Hash lock of benchmark data and evaluator code

All evaluator inputs and code were hashed (SHA-256) at the anchor commit: **103 files** across
`benchmarks/cec_suite_python/` (all five suites), `src/gsk_family/benchmark_adapter/`,
`src/gsk_family/optimizers/`, `src/gsk_family/runners/`, and `src/gsk_family/common/`.
Full inventory: `papers/governance/audit_evidence/evaluator_hash_inventory.csv`. Key anchors:

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| `benchmarks/cec_suite_python/cec2017/data.pkl` (shifts, shifts_cf, rotations, rotations_cf, shuffles, shuffles_cf) | 14,610,514 | `fe544853b079b1e7238e98c40c7c27748a94b62350d13f8a14808a7c4b8a4e15` |
| `benchmarks/cec_suite_python/cec2013/data.pkl` (rotations, shift_flat) | 3,090,796 | `1af80d77ad6f92bc06b8b7e29e7d5373475ce1d65b1315d97ed891bf3875ef5b` |
| `benchmarks/cec_suite_python/cec2013lsgo/data.pkl` | 1,252,477 | `1b79d4caa2b4a4a244bbbda115e833a09b4965091b664515314aea44810743dd` |
| `benchmarks/cec_suite_python/cec2020/data.pkl` | 4,707,969 | `3f160a73dd9c7b2981883c27bd8973bac48361a181e2ff503fc79ce0c3cdb3a0` |
| `benchmarks/cec_suite_python/cec2017/functions.py` | 9,552 | `d14429caf44a499679652d38cfef15730f81eb511f38b58b6433030df86a0e8f` |
| `benchmarks/cec_suite_python/cec2013/functions.py` | 8,770 | `e1764f86d81a1e437c640643162b7dba91e21388edb66ce7911165b4f06158b8` |
| `benchmarks/cec_suite_python/cec2011/functions.py` | 22,972 | `4145a538ea14ddc067fd5e72bf03beaa372382d3aef7046448406f153f901678` |
| `benchmarks/cec_suite_python/cec2011/_constants.py` (bounds/constants; CEC2011 has no data.pkl — data is in code) | 1,966 | `26c933c6a5c5f9b0500aae57a1a5cc4f140bcd645ef18de30e157471657241e2` |
| `src/gsk_family/benchmark_adapter/factory.py` (budget + problem construction) | 11,441 | `af612277d33a34f1a789a3de4d63c2b964ae4393a216b1520f5c5fe3d20dabc9` |
| `src/gsk_family/benchmark_adapter/protocol.py` (function sets, dims, F2 rule) | 4,922 | `b885617ec3ce612e2962aa9eb936d469f6e9c4a1bb6fe222e685bdffce9d11d0` |
| `src/gsk_family/runners/seed_policy.py` | 6,527 | `9513e0082bd66b48c9cf41b36f712e6a91405a23c419ac897e9bcb3b6ee66361` |
| `src/gsk_family/optimizers/_dt_subsystems/budget.py` (BudgetController) | 10,918 | `b1766ecf6d105c1e5fde77362a0e2d0f35631ee8cc264a430d187a1424316e57` |
| `src/gsk_family/optimizers/egsk.py` | 15,614 | `9d6a597eaaaccfc09e4707025f04d43576846e42aed612647dd6a8cacd0207d6` |
| `src/gsk_family/optimizers/dt_gsk.py` | 13,544 | `a274e0f83b4efd3c8f87c9f145bd662bcf26d1faa8616eea94e44a2b63f8dee3` |
| `src/gsk_family/optimizers/_dt_core.py` | 253,027 | `1ef815cee5d4c9c3a76f33bdf74b88775a4064bce3c2e5d3e71b4702d2a19bf6` |

**Code-identity across the run campaign (critical for equivalence).** The 21 panel cells record six
distinct producing commits in `environment.json` (`31c5a04c4`, `f94817cc4`, `20cfed0ac`,
`19f32fb83`, `7483cac2e`, `c35c26de7`, plus `2d72f6497` for four cec2013 cells). `git diff` between
every consecutive pair, restricted to `src/gsk_family/` and `benchmarks/cec_suite_python/`, is
**empty** — the evaluator, optimizer, and runner code is byte-identical across the whole campaign.
All optimizers therefore ran against identical benchmark data files and identical evaluator code
(single shared working-tree package; hashed above).

### 6.2 Suite-metadata cross-check against Phase 1 evidence cards

**CEC2013 vs `liang2013cec2013` (admissible, verified) — PASS.**

| Check | Card locator | Code/config | Result |
|---|---|---|---|
| 28 functions | Table I, PDF p. 5 | `protocol.py` function_ids 1..28 | PASS |
| f* = −1400:100:1400 (0 excluded) | Table I, PDF p. 5 | `cec2013_fopt`, all 28 checked | PASS (exact) |
| Search range [−100, 100]^D | Sec. 1.1, PDF p. 4 | `cec2013_bounds` | PASS |
| Official dims 10/30/50 | Sec. 2, PDF p. 35 | `protocol.py` default_dimensions (10,30,50); panel per_run dims {10,30,50} | PASS |
| 51 runs | PDF p. 35 | run_config `runs: 51`; per_run 4284 rows = 28×3×51 | PASS |
| MaxFES 10,000·D | PDF p. 35 | `factory.py` `10_000 * d`; per_run `nfes` | PASS |
| Error floor 1e-8, sub-floor as zero | PDF p. 35 | `target_error=1e-8`, `report_zero_tol=1e-8`, `compute_error` zeroing | PASS |
| Checkpoints (11 official points) | PDF p. 35 | runner checkpoint_fractions (14 points) are a strict superset of the official 11 | PASS (superset, disclosed) |
| Data for D up to 100 shipped; D100 not protocol-official | card Limitation | `VALID_DIMS` = {2,5,...,100}; **panel does not use CEC2013 D100** | PASS |

**CEC2011 vs `das2011cec2011` (admissible, verified) — PASS with one documented data deviation
and one reporting-protocol narrowing.**

- 22 instances (F1–F22) — PASS (`protocol.py` 1..22; per_run 550 rows = 22×25).
- 25 runs — PASS (run_config `runs: 25`).
- Budget 150,000 FEs — PASS (`factory.py` `150_000`; per_run `nfes` = 150000 for all 550 rows in
  every cell).
- Native dimensions — 21/22 match Table 1 (pp. 33–37). **Deviation D-CEC2011-F12:** vendored code
  implements F12 (DED instance 2) at **D = 240**, while das2011 Table 1 prints **D = 216**. The
  evidence card's own limitation anticipates this class of difference ("the authoritative
  dimension/bound values for DT-GSK experiments are the vendored benchmark code, not this PDF")
  — later toolbox revisions changed this instance. Manuscript obligation: state the vendored
  dimension (240) and disclose the deviation against the report locator; never present D=216
  as what was run. All seven optimizers ran the identical D=240 instance, so within-panel
  comparability is unaffected.
- Snapshot budgets: the official protocol asks for values at 50k/100k/150k FEs (Sec. 2, p. 40).
  The release's checkpoint fractions (0.01…1.0) do **not** include 1/3 and 2/3, so 50k/100k
  snapshots are unavailable; the panel endpoint is the final-budget (150k) value only. Narrow
  any protocol claim accordingly (final-FES reporting; snapshots not recorded).
- Raw-objective basis (no certified optima): `statistics_basis="raw_objective"`, adapter optimum
  NaN, per_run `error` column all-NaN by design in all 7 cells — consistent with the card
  (no f* table in the report).

**CEC2017 — definitional cross-check remains BLOCKED (EG-001).** `awad2016problem` is inadmissible
(wrong document in corpus). Consequently the CEC2017 evaluator/metadata check performed here is
**code-internal and protocol-anchor-based only**, not literature-anchored:

- 30 functions implemented; **F2 excluded from every default comparison** — verified in three
  independent layers: (i) `protocol.py` `default_function_ids=(1,)+tuple(range(3,31))` with the
  note "F2 is implemented but excluded from default comparisons"; (ii) every cec2017
  `run_config.json` records `exclude_funcs: 2` and a 29-function `funcs_to_run`; (iii) zero F2
  rows exist in any cec2017 `per_run.csv` (7/7 cells).
- Dimensions 10/30/50/100 enforced (`CEC2017_DIMS`, `validate_dimension`); bounds ±100 uniform at
  all four dims; `cec2017_fopt(i) = 100·i` for i = 1..30 (exact).
- data.pkl carries the expected CEC2017 structure (shifts/rotations/shuffles + composition `_cf`
  variants).
- These facts match the well-known CEC2017 convention, but per EG-001 the suite definition may
  only be cited via participant descriptions (`awad2017ensemble`, `brest2017single`) until the
  correct NTU report is supplied. **The definitional gap is not closed by this audit.**

**Dimension rules in code (all suites).** `factory.py` raises on any non-native CEC2011/CEC2013LSGO
dimension request and on any CEC2017/CEC2013/CEC2020 dimension outside the declared tuples;
`benchmark_backend` is locked to `python`; `benchmark_fp_mode` supports `default`/`strict` and all
21 panel cells ran `default` (uniform).

---

## Task 7 — MaxFES and objective-call accounting

### 7.1 Budget definition and override state

Single definition point `src/gsk_family/benchmark_adapter/factory.py::_max_nfes`:

- CEC2017: `10_000 * D` (100k/300k/500k/1M) — line 289;
- CEC2013: `10_000 * D` (100k/300k/500k) — line 218;
- CEC2011: `150_000` fixed — line 188;
- (context) CEC2013LSGO: 3,000,000; CEC2020: per-dim table — not used by the primary panel.

`max_nfes_override` semantics: `0`/`None` → suite default; positive → override; negative → error.
**All 21 panel cells record `max_nfes_override: 0` in both `run_config.json` and
`environment.json`** — suite-default budgets were active everywhere; no cell ran a reduced or
extended budget (`verification.json` `reduced_budget: false`, 21/21).

### 7.2 per_run `nfes` vs budget — machine check (PASS)

For every one of the 21 cells and every dimension, per_run `nfes` was compared with the expected
budget (machine output `phase2_tasks678_audit.json`, key `nfes_audit`):

- **Zero rows exceed budget** anywhere (0 of 33,132 panel rows).
- CEC2011: all 550 rows per cell are exactly 150,000 (`termination = max_evaluations`).
- CEC2017/CEC2013: all rows are exactly 10,000·D except protocol-compliant early stops:
  - `agsk` cec2017 D10 (351 of 1479 rows) and D30 (53) — `termination = target_error_reached`;
  - `agsk` cec2013 D10/D30/D50 (240/163/155) and `apgsk` cec2013 D10/D30/D50 (239/153/153) —
    same termination.
  - Early stop fires only when error ≤ 1e-8 (the CEC termination rule: "MaxFES reached or error
    below 1e-8", liang2013cec2013 PDF p. 35 for CEC2013). The reported error is already at the
    zero floor, so early stopping cannot bias final-error statistics; it only saves wall time.
    The remaining five optimizers are reference-faithful full-budget runners (no early-stop
    branch), which likewise cannot bias final error. **No per-algorithm budget difference exists**;
    only budget *usage* differs, in a protocol-compliant, non-biasing way. Recorded for
    the cost-analysis caveat: runtime comparisons on solved cells must note agsk/apgsk early
    termination.

### 7.3 DT-GSK: local-search and polish evaluations are counted (PASS)

`src/gsk_family/optimizers/dt_gsk.py` (module docstring, lines 12–13): "`BudgetController` is the
single evaluation cap, and `nfes_used` is reported as `OptimizerResult.nfes`." Verified in code:

- `_dt_core.py` line 2070 constructs the single `BudgetController(objective=objective,
  max_nfes=max_nfes)`; a repo-wide grep of `_dt_core.py` finds **no direct `objective(` call** —
  every evaluation site routes through `budget.eval_batch_strict/_safe/eval_one`:
  initialization (2103/2114), offspring (3319), Cauchy escape (3876), restart proposals (3954),
  **elite local search** (4245, 4363, and batch LS 4475 — additionally capped by
  `local_search_eval_cap` and `budget.remaining()`, lines 4048/4086/4210–4216/4337–4343),
  **final polish** (compass search receives the `budget` object itself, lines 4534–4548, capped by
  `min(budget.remaining(), final_polish_eval_cap)`), and DSR restart re-evaluations (4636–4639).
- `BudgetController._consume` raises typed `BudgetExhausted` on any over-budget call
  (budget.py lines 113–132); the strict path never calls the objective with more rows than remain.
- Panel confirmation: every dt-gsk per_run row reports `nfes` = exact budget, never above.

### 7.4 eGSK: SLSQP polish evaluations are counted (PASS)

`egsk.py::_egsk_ip_refine` (lines 149–212): the IP-refinement budget is
`ceil(2e-3 · MaxFES)` capped by `max_nfes − nfes`; **every SLSQP objective call (function and
finite-difference gradient evaluations alike) increments the counted `nfes`** via the counting
wrapper (`state["count"]`, raising an internal sentinel at the cap), mirroring the reference's
`details.funcCount` accounting. No RNG is drawn by the refine step.

### 7.5 Other family members

- `atmals-gsk`: its adaptive machinery (`atmals_helpers.py`) is reward/roulette parameter
  adaptation only — the optimizer has exactly two evaluation sites (initialization and the
  per-generation trial batch); no hidden local-search objective calls.
- `gsk`/`agsk`/`apgsk`/`fdb-agsk`: reference-faithful generation loops; counted
  `nfes += min(NP, max_nfes − nfes)` per batch (e.g., `gsk.py` lines 135–137, 191–199).
- **Boundary semantics note (corrected 2026-07-22; disclosed, no impact):** an earlier revision of
  this bullet asserted that "no truncated boundary generation occurs in any panel cell" because
  NP = 100 divides every panel budget. **That was false** — the divisibility argument holds only
  for the two fixed-NP ports. The actual position, established by source inspection, is:
  - **DT-GSK truncates before evaluating.** `BudgetController.eval_batch_strict` clips the
    candidate matrix to `n_eval = min(n, budget.remaining())` and calls the objective on the clipped
    matrix (`_dt_subsystems/budget.py` line 229), so dt-gsk never computes a row past the cap.
  - **The six comparator ports do not truncate — by design.** They are deliberate
    reference-faithful (MATLAB) ports: the terminal batch is evaluated in **full** and only the
    in-budget prefix is charged (`eval_batch_matlab` semantics; in the ports,
    `n_count = min(NP, max_nfes − nfes)` followed by `nfes += n_count`). This preserves the
    reference baselines' objective-call pattern and boundary fitness vectors.
  - **Which cells actually overrun.** `gsk` and `atmals-gsk` hold NP = 100 for the whole run and
    every panel budget is divisible by 100 (100k/300k/500k/1M/150k), so their terminal batch lands
    exactly on the cap. `agsk`, `apgsk` and `fdb-agsk` apply LPSR down to `min_pop_size = 12`, so
    the terminal NP generally does not divide the remaining budget; `egsk` runs its in-loop SLSQP
    refinement (`egsk.py::_egsk_ip_refine`, called at line 322), which adds a non-multiple-of-NP
    increment to `nfes` and likewise misaligns the terminal batch. The overrun is structurally
    bounded to a single generation: at most `NP - 1` rows on the one terminal batch, and exactly
    zero whenever the terminal `NP` divides the remaining budget.
  - **Counted budgets are unchanged: all seven optimizers are charged exactly MaxFES** (aside from
    the protocol-compliant `target_error_reached` early stops recorded in §7.2). The over-cap rows
    are computed but never charged, and §7.2 confirms 0 of 33,132 panel rows exceed budget; no
    optimizer buys a single counted evaluation of extra search.
  - **The discarded rows cannot enter the incumbent.** The best-so-far scan reads the counted
    prefix only (`_scan_best` / `_scan_best_with_index` slice `fitness[:n_count]`), and the
    `while nfes < max_nfes` loop exits immediately after the charge, so the survivor array those
    rows touch is never read again and they reach no reported field.
  - **Why the released panel is unaffected (machine-checked, ticket R-14).** The discarded rows are
    never read back (prefix-only scan) and the loop exits immediately after the charge, so no
    reported field — `best_fitness`, `error`, `nfes`, `best_x`, or either recorded curve — can
    depend on them. This is asserted directly, on all seven optimizers, by
    `tests/regression/test_budget_crossing_semantics.py`. With `MaxFES = 1050` chosen so that it is
    deliberately **not** a multiple of `NP = 100`, the terminal batch is truncated and the crossing
    is exercised: every optimizer is charged exactly 1050; `dt-gsk` evaluates exactly 1050 rows
    (strict pre-call truncation); the six reference-faithful ports evaluate 8–50 uncounted rows on
    the terminal batch (174 across the panel; 8 for the LPSR members `agsk`/`apgsk`/`fdb-agsk`,
    whose terminal `NP` has been reduced, and 50 for the fixed-`NP` members). Overwriting **every**
    one of those uncounted rows with `1e300` leaves `best_fitness`, `nfes` and `best_x`
    bit-identical for all seven. Never computing a row is strictly weaker than poisoning it, so a
    change to strict truncation would be a no-op on every reported value. The released panel is
    unaffected and no rerun is warranted.

### 7.6 Task 6–7 verdict

- Evaluator equivalence: **PASS** (single hashed evaluator package, code-identical campaign,
  metadata verified against the two admissible suite-definition cards; CEC2017 definitional
  citation remains blocked per EG-001; CEC2011 F12 D=240-vs-216 deviation documented).
- MaxFES: **PASS** (uniform suite-default budgets, no override, no over-budget row, LS/polish
  evaluations counted for dt-gsk and egsk, no per-algorithm budget difference).

### Anomalies raised or cross-referenced here

| ID | Anomaly | Severity | Disposition |
|---|---|---|---|
| P2-A1 | CEC2011 F12 implemented at D=240 vs das2011 Table 1 D=216 | minor (disclosure) | Manuscript states vendored dims; deviation disclosed against Table 1 locator; within-panel comparability unaffected (all optimizers identical instance) |
| P2-A2 | CEC2017 suite-definition literature anchor still BLOCKED (EG-001) | blocking for citation only | Unchanged; interim narrowing per EG-001 |
| P2-A3 | CEC2011 official 50k/100k snapshot budgets not among recorded checkpoints | minor (scope narrowing) | Report final-150k endpoint only; no snapshot claims |
| P2-A4 | agsk/apgsk early termination rows (target_error_reached) | none (protocol-compliant) | Note in cost-analysis captions |
| P2-A5 | `apgsk` cec2017 per_run/seed_schedule/environment contain only D100 (cell metadata overwritten by the 2026-07-08 D100 re-run; D10/30/50 per-run evidence lives in `gen_logs/CheckpointErrors_*.csv`) | **major** | See `comparability_audit.md` Section 5 (classification + two remediation paths) |
