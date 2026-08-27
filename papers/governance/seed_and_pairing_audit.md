# Seed and Pairing Audit (Phase 2, Task 4)

- **Date:** 2026-07-10
- **Phase / task:** Phase 2 — Immutable empirical evidence, benchmark, and provenance audit; task 4 (seeds and pairing).
- **Anchor commit:** `262fc16c91fbe5608a1a0b0c5df3cbcd009edc21`
- **Evidence tree (read-only):** `benchmarks/cec_reference_results/`
- **Method evidence:** `papers/governance/audit_evidence/seed_env_audit.py`, `genlog_seed_check.py`, `apgsk_consistency.py`; machine outputs `audit_out.json`, `genlog_check_out.json`.
- **Read-only compliance:** mtime+size of every evidence file opened was snapshotted before and after the audit; all snapshots identical (`evidence_tree_untouched = true` in `audit_out.json`). No evidence file was written, renamed, or touched.

## 1. Canonical seed formula under audit

From `src/gsk_family/runners/seed_policy.py` (`get_cec_seed`), base seed 20240620:

```
seed = (20240620 + 1000003*dim + 1000033*func + 1000037*run) mod 2147483646 + 1
```

Every `run_config.json` in the panel records `seed_policy = "unified"` with strides `dim_stride=1000003`, `func_stride=1000033`, `stride_run=1000037` — all 21 cells match the module constants (`run_config_strides_ok = True` for 21/21). Every `environment.json` records `base_seed = 20240620` and `rand_generator = "threefry"`. No cell in the evidence release uses the legacy `reference` linear/product schedules; the `dt-gsk` unified-only rule is therefore consistent with the entire panel rather than a deviation.

## 2. Schedule recomputation (full recompute, exceeds the sample requirement)

The task required recomputation for a full-schedule sample (all cells for one function plus spot functions per suite and optimizer). Because the schedules are small, **every row of every `seed_schedule.csv` in all 21 (suite, optimizer) cells was recomputed** against the formula above.

| Suite | Optimizers | Rows per schedule | Recompute mismatches | Duplicate (dim,func,run) keys | Duplicate seed values |
|---|---|---|---|---|---|
| cec2017 | agsk, atmals-gsk, egsk, fdb-agsk, gsk, dt-gsk | 5,916 (4 dims × 29 funcs × 51 runs) | 0 | 0 | 0 |
| cec2017 | **apgsk** | **1,479 (D100 only — see anomaly A1)** | 0 | 0 | 0 |
| cec2011 | all 7 | 550 (22 problems × 25 runs) | 0 | 0 | 0 |
| cec2013 | all 7 | 4,284 (3 dims × 28 funcs × 51 runs) | 0 | 0 | 0 |

Total schedule rows recomputed and verified: **70,813; 0 mismatches.**

Function sets are identical across all 7 optimizers within each suite: cec2017 = F1, F3–F30 (F2 excluded, matching `run_config.json` `exclude_funcs: 2`); cec2011 = P1–P22 at native dimensions; cec2013 = F1–F28. Run indices are contiguous 1..51 (1..25 for cec2011).

### Uniqueness and deterministic mapping

- **Deterministic mapping:** no duplicate `(dim, func, run)` key in any schedule (each key maps to exactly one seed; recomputation confirms the mapping is the pure function above).
- **Injectivity in panel range:** no duplicate seed **value** within any schedule (0 collisions in all 21 cells). The linear form never exceeds ~3.1×10⁸ for panel arguments (max dim 240, func 30, run 51), far below the 2,147,483,646 modulus, so no wraparound occurs and the mapping is injective over the panel domain.
- **cec2011 native-dimension sharing:** several problems share a native dimension (P1/P13: D6; P2/P5/P6: D30; P3/P4: D1; P18/P19/P20: D96). The `func` term keeps their seeds distinct; verified empirically (0 duplicate seeds in the cec2011 schedules).

## 3. Cross-checks against per-run records

- **`per_run.csv` seed column:** for all 21 cells, every per-run row was joined to its schedule on `(dimension, function, run)`: 0 seed mismatches, 0 per-run keys missing from the schedule, 0 schedule keys missing from per-run (row counts equal schedule counts, including apgsk's truncated 1,479 — see A1).
- **`gen_logs/CheckpointErrors_*.csv` seed column:** these files embed `Run,Seed` per row.
  - apgsk/cec2017 **full sweep**: all 116 files (29 funcs × 4 dims), 5,916 rows — 0 mismatches vs the formula. This recovers and verifies the D10/D30/D50 seed coverage missing from the overwritten sidecars (A1).
  - Spot check for every other (suite, optimizer): first and last checkpoint file per dimension, 10,598 rows total — 0 mismatches.

## 4. Pairing validity per comparator

**Determination: pairing is VALID for every comparator pair among the 7 panel optimizers, on all three primary suites.** Basis:

1. **Identical problem instances.** All 21 cells use the same deterministic benchmark data (`data_root = benchmarks\cec_suite_python`, `benchmark_backend = python`); the per-suite FP `suite` probe hash is identical across all 7 optimizers within each suite (see `fp_environment_audit.md`), so run r of any two optimizers on (suite, func, dim) evaluates byte-identical objective functions. For CEC suites the instance does not depend on the seed, so instance identity holds even where seeds are examined.
2. **Optimizer-independent seed schedule.** Within each suite, all seven schedules are identical maps `(dim,func,run) -> seed` (0 seed differences vs the dt-gsk reference map on all shared keys; cec2011 and cec2013: full 7-way identity; cec2017: 6 full schedules identical, apgsk identical on its stored D100 subset and verified identical on D10/D30/D50 via gen_logs — A1).
3. **Common random numbers at initialization.** `initial_population_policy = runner_supplied_X0`; `run_config.json` states: "runner-generated shared X0 from get_cec_seed(base_seed,dim,func,run); post-initialization rng state restored inside optimizer". With identical seeds and the same `threefry` generator in all 21 cells, run r of every optimizer starts from the **same initial population** on the same instance.

Per-comparator table (vs `dt-gsk`; the schedule-identity result makes it hold for every pair):

| Comparator | cec2017 | cec2011 | cec2013 |
|---|---|---|---|
| gsk | PAIRED (identical seeds, 5,916/5,916) | PAIRED (550/550) | PAIRED (4,284/4,284) |
| agsk | PAIRED (5,916/5,916) | PAIRED | PAIRED |
| apgsk | PAIRED — seeds identical on all keys; per-run values for D10/D30/D50 available only via `gen_logs` (A1) | PAIRED | PAIRED |
| atmals-gsk | PAIRED (5,916/5,916) | PAIRED | PAIRED |
| egsk | PAIRED (5,916/5,916) | PAIRED | PAIRED |
| fdb-agsk | PAIRED (5,916/5,916) | PAIRED | PAIRED |

Context suites **cec2020** (agsk) and **cec2013lsgo** (decc-g, mos) carry no seed schedules, per-run files, or environment metadata (imported reference summaries). They are **outside the pairing framework**: no paired per-run statistic may be computed against them; context-only use.

## 5. Known properties (not defects)

- **Cross-suite seed sharing.** The formula contains no suite term, so cells sharing `(dim, func, run)` across suites share seeds: 4,131 keys are common to cec2013 and cec2017 schedules (all with equal seeds, verified), 75 keys overlap cec2011. Harmless: analyses are per-suite and the evaluators differ; recorded to preempt reviewer surprise at repeated seed values across suites.
- **F2 exclusion (cec2017)** is uniform across all seven optimizers in schedules, per-run files, and summaries; the environment `functions` list records the *requested* 1–30 range while `run_config.json` records the exclusion — the executed set is F1, F3–F30.

## 6. Anomaly A1 — cec2017/apgsk sidecar metadata truncated to D100

- **Observation.** `benchmarks/cec_reference_results/cec2017/apgsk/seed_schedule.csv` and `per_run.csv` contain only D100 rows (1,479); `environment.json` (`dimensions_requested = dimensions_run = [100]`, timestamp 2026-07-08T21:53:10, git commit `20cfed0a`) and `run_config.json` (`dims = 100`) describe only a D100 invocation. The exhibit-bearing files are complete: 4 summary CSVs (D10/D30/D50/D100, 29 functions each), 116 curve files, 116 `gen_logs` checkpoint files covering all four dimensions.
- **Classification.** Metadata-coverage defect: the apgsk cec2017 campaign was executed in (at least) two invocations and the final D100-only invocation **overwrote the single-file sidecars** (seed schedule, per-run, environment, run config) while per-(func,dim) artifacts from earlier invocations survived. Traced to the runner writing sidecars per invocation at a fixed path. No evidence of data corruption.
- **Impact evaluation (verified, read-only):**
  - Seeds for the missing D10/D30/D50 cells recomputed from `gen_logs` (Run,Seed columns): 5,916/5,916 rows match the unified formula → pairing for apgsk at those dimensions is intact and identical to the other six optimizers.
  - Summary CSVs vs `gen_logs` final checkpoint per-run values: Best/Median/Mean/Worst/SD recomputed for all 29 functions × 4 dims (580 statistics, with the documented `report_zero_tol = 1e-8` display floor) — **580/580 match**. The summaries and gen_logs therefore derive from the same runs.
  - Surviving `per_run.csv` (D100) vs `gen_logs` D100 final checkpoint: **1,479/1,479 exact matches**.
- **Consequence for analyses.** Any per-run paired statistic (e.g., Wilcoxon) that sources per-run values exclusively from `per_run.csv` will silently lack apgsk cec2017 D10/D30/D50. The admissible per-run source for that cell is `gen_logs/CheckpointErrors_apgsk_F<f>_D<dim>.csv` (final checkpoint column), now verified equivalent. This must be respected by the strict-source loader audit (task 10) and by Phase 5/6 statistics.
- **Resolution options (no silent repair; tree is immutable):**
  1. Register `gen_logs` as the sanctioned per-run source for apgsk/cec2017 D10/D30/D50 in the data ledger, with this audit as the equivalence evidence; or
  2. Re-run apgsk cec2017 in staging and promote a complete bundle as a new versioned release via `scripts/promote_evidence.py` (Section 2.4).
  Option 1 is sufficient for the primary study since seeds, pairing, and values are fully verified; option 2 is preferable if reviewers require uniform sidecar schemas.
- **Prohibited:** hand-writing the missing seed/per-run rows into the evidence tree.

## 7. Acceptance statement

- Seed formula verified by full recomputation over all 70,813 schedule rows plus 16,514 gen-log rows: 0 mismatches.
- Uniqueness and deterministic mapping: confirmed in every cell.
- Pairing: valid for all 21 optimizer pairs on cec2017, cec2011, cec2013 (identical instances, identical seeds, shared initial populations); context suites excluded from pairing by construction.
- One anomaly (A1) — logged, classified, traced, impact-evaluated above; no unexplained anomaly remains for task 4 scope.

---

## Erratum (2026-08-27) — the DT-GSK carve-out this audit does not state

Basis 3 and the Section 7 summary above assert common random numbers at
initialization "for all 21 optimizer pairs" without recording the one documented
exception. The provisioning claim is correct and is **not** what needs
qualifying: `run_experiment.py` really does supply a shared `X0` to every
optimizer including DT-GSK. The exception is in **consumption** — DT-GSK
self-initializes and does not consume the shared payload, which the manuscript
already records (Table 13 and Supplementary S5.1, "the single documented
exception is DT-GSK self-initialization").

**No manuscript edit follows**: the shipped sentences are already true at all
four rendered sites, and Supplementary S5.1 *is* the pairing record a reader can
check. This note exists so the governance audit is not read as contradicting
them. Appended rather than rewritten — the audit is a dated, anchor-stamped
record and its original text stands.
