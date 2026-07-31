# FP and Environment Audit (Phase 2, Task 5)

- **Date:** 2026-07-10
- **Phase / task:** Phase 2 — Immutable empirical evidence, benchmark, and provenance audit; task 5 (FP and environment).
- **Anchor commit:** `262fc16c91fbe5608a1a0b0c5df3cbcd009edc21`
- **Evidence tree (read-only):** `benchmarks/cec_reference_results/`
- **Method evidence:** `papers/governance/audit_evidence/seed_env_audit.py`, `genlog_seed_check.py`, `apgsk_consistency.py`; machine outputs `audit_out.json`, `genlog_check_out.json`.
- **Scope:** every `environment.json` in the release was read — 21 files (7 optimizers × {cec2017, cec2011, cec2013}). Context suites carry no environment metadata (Section 6).
- **Read-only compliance:** mtime+size snapshots of all opened evidence files identical before and after the audit (`evidence_tree_untouched = true`).

## 1. FP sentinel — suite-internal consistency (PASS)

`fp_regime.sentinel` is identical across all seven optimizers within each suite:

| Suite | Sentinel (full) | Consistent 7/7 |
|---|---|---|
| cec2017 | `8bda40d80d1671fe6571a56195b1d0679208c20f8cb2ae14c24b56f469c15bdb` | yes |
| cec2011 | `10fef05901ee77631e8f6bbaf838b9836db88bf2669f2cbbcafb00fd82e41822` | yes |
| cec2013 | `16a3e3095b606c5bab5f56fe52e6849ccde461a71f37929366d059ae7d72309e` | yes |

**Audit target:** the expected cec2017 prefix `8bda40d8...` is confirmed (treated strictly as an audit target, not as ground truth).

## 2. FP probes and kernel state

`fp_regime.probes` decomposes the sentinel into named numerical probes:

| Probe | Distinct values across all 21 cells | Value (prefix) |
|---|---|---|
| `threefry` (RNG stream) | 1 | `be8ec1bb394ec405...` — identical in all 21 cells (cross-suite RNG bit-identity) |
| `ism_kernels` | 1 | `b468e920990d8fab...` — identical in all 21 cells |
| `suite` (evaluator) | 3 (one per suite; 7/7 identical within each suite) | cec2017 `9d0adb66ea456ff2...`, cec2011 `f1d8c8a7422a90df...`, cec2013 `d2d9b94da8a6cad4...` |

- `fp_regime.jit_complete = true` in all 21 cells; `numba_import_error = null`.
- `kernel_flags` all true in every cell for: `gsk_family.common.reference_rng`, `gsk_family.common.threefry_rng`, `gsk_family.optimizers._kernels`, `gsk_family.optimizers._dt_subsystems._numba_accel`, plus the suite-appropriate `benchmarks.cec_suite_python.<suite>._numba` (correct suite module in each cell; no cross-suite flag leakage).
- `probe_cell` is suite-appropriate: cec2017 `[20, 10]`, cec2011 `[1, null]` (native-dim problem), cec2013 `[1, 10]` — consistent within each suite.
- **Residual limitation:** the probe set covers the shared RNG, the ISM kernels, and the suite evaluator. Comparator-specific optimizer kernels (gsk/agsk/apgsk/fdb-agsk/atmals-gsk/egsk update rules) are JIT-flag-covered but have no dedicated numerical probe; their numerical identity across producer commits rests on the shared-kernel probes plus code history, not on a direct hash.

## 3. Hardware, libraries, and runner configuration (constant across all 21 cells)

| Field | Value |
|---|---|
| computer | `HUAWEI-MMASOUD` |
| platform | `Windows-10-10.0.26200-SP0` |
| cpu_cores (logical) | 22 |
| python_version | 3.10.11 |
| numba / llvmlite | 0.64.0 / 0.46.0 |
| benchmark_backend | `python` (requested `auto`, resolved to python + numba JIT) |
| benchmark_fp_mode | `default` |
| rand_generator | `threefry` |
| base_seed / seed_policy | 20240620 / `unified` |
| initial_population_policy | `runner_supplied_X0` |
| max_nfes_override | 0 |
| report_zero_tol | 1e-08 |
| parallel_backend / workers | `process` / 15 (of 22 cores; `numba_threads_active = 1` per worker) |
| warmup_enabled / profile_enabled | false / false |
| checkpoint_fractions | 14 fractions, 0.01 → 1.0, identical in all cells |
| data_root | `benchmarks\cec_suite_python` |
| runs | 51 (cec2017, cec2013), 25 (cec2011) |

`statistics_basis` differs **by suite, uniformly across optimizers**: `error_vs_optimum` (cec2017, cec2013) vs `raw_objective` (cec2011 — real-world problems without published optima; explains the NaN `error` column in cec2011 `per_run.csv`). This is a protocol property, not an inconsistency.

`output_dir` in every cell points at `results\_run_all\<optimizer>\<suite>`: the evidence was produced in staging and then vendored into `benchmarks/cec_reference_results/` — consistent with the Section 2.4 staging→evidence model (the vendoring predates the named promotion tool, which task 10 builds).

## 4. Provenance variation register (git commits and timestamps)

The panel was produced as a rolling campaign, 2026-07-08 12:24 → 2026-07-10 08:20, across **7 distinct producer commits**. Hardware/library stack constant throughout (Section 3); FP probes (Section 2) demonstrate bit-identical RNG, ISM kernels, and suite evaluators across the commit drift.

| Suite | Optimizer | git_commit | timestamp |
|---|---|---|---|
| cec2017 | gsk | `31c5a04c` | 2026-07-08T12:24:02 |
| cec2017 | agsk | `f94817cc` | 2026-07-08T16:44:22 |
| cec2017 | apgsk | `20cfed0a` | 2026-07-08T21:53:10 (D100-only re-run; see anomaly A1 in `seed_and_pairing_audit.md`) |
| cec2017 | fdb-agsk | `19f32fb8` | 2026-07-09T02:36:00 |
| cec2017 | atmals-gsk | `7483cac2` | 2026-07-09T06:20:39 |
| cec2017 | egsk | `c35c26de` | 2026-07-09T09:56:08 |
| cec2017 | dt-gsk | `c35c26de` | 2026-07-09T14:45:09 |
| cec2011 | gsk | `c35c26de` | 2026-07-09T15:27:34 |
| cec2011 | agsk | `c35c26de` | 2026-07-09T16:07:38 |
| cec2011 | apgsk | `c35c26de` | 2026-07-09T16:53:15 |
| cec2011 | fdb-agsk | `c35c26de` | 2026-07-09T17:37:07 |
| cec2011 | atmals-gsk | `c35c26de` | 2026-07-09T18:19:39 |
| cec2011 | dt-gsk | `c35c26de` | 2026-07-09T19:07:44 |
| cec2011 | egsk | `c35c26de` | 2026-07-09T20:36:48 |
| cec2013 | gsk | `c35c26de` | 2026-07-09T21:14:03 |
| cec2013 | agsk | `c35c26de` | 2026-07-09T22:52:04 |
| cec2013 | apgsk | `c35c26de` | 2026-07-10T01:02:01 |
| cec2013 | fdb-agsk | `2d72f649` | 2026-07-10T03:04:05 |
| cec2013 | atmals-gsk | `2d72f649` | 2026-07-10T04:27:18 |
| cec2013 | egsk | `2d72f649` | 2026-07-10T05:48:19 |
| cec2013 | dt-gsk | `2d72f649` | 2026-07-10T08:20:31 |

- No `environment.json` records the anchor commit `262fc16c` — expected: the anchor identifies the audit/build state; the producer commits above are the run provenance and must be carried into the data ledger (`commit_sha` column).
- `skipped_cells = []` and `optimizer_notes = []` in all 21 cells.
- Recorded commands are uniform: `python run.py --root . --optimizer <opt> --suite <suite> --runs <51|25> --seed 20240620 --seed-policy unified --rand-generator threefry --benchmark-fp-mode default --benchmark-backend auto --convergence-graphs`.

## 5. Solver provenance — gap for egsk (FINDING)

- `environment.json` records `python_version`, `numba`, and `llvmlite` versions, but **no numpy or scipy version** in any cell.
- egsk's local search substitutes SciPy SLSQP for MATLAB `fmincon` (project decision record). Its cells record empty `optimizer_options` and `optimizer_notes`, so **the exact SciPy version used by the evidence runs is not captured inside the release**.
- Consequences:
  1. The task 8 rule "verify egsk solver provenance and prevent SciPy/MATLAB substitution inside one exhibit" can rely on the *design* provenance (all vendored egsk panel cells are Python/SciPy runs; the MATLAB/fmincon reference CSVs live outside this panel), but the *version* provenance must be recovered from the producer commits' lockfile/`pip freeze` and recorded in the data ledger / reproducibility manifest — it cannot be read from the evidence tree.
  2. Recommendation (forward-looking, non-blocking): extend the runner's environment capture with numpy/scipy versions before any future promotion; do not modify existing releases.
- The same gap applies to numpy for all optimizers; impact is lower because the FP probes directly hash the numerical outputs of the shared kernels.

## 6. Context suites (imported, outside the FP framework)

| Suite | Cell | Files | environment.json | seed/per-run |
|---|---|---|---|---|
| cec2020 | agsk | `agsk_cec2020_D05/D10/D15/D20.csv` | absent | absent |
| cec2013lsgo | decc-g | `decc-g_cec2013lsgo.csv` | absent | absent |
| cec2013lsgo | mos | `mos_cec2013lsgo.csv` | absent | absent |

These are imported reference summaries (literature-derived), with no sentinel, seed, or environment metadata. They are non-poolable with the locally produced panel and admissible only as context exhibits with imported-source labeling (comparator classification is task 8 scope).

## 7. Anomalies and dispositions

| ID | Anomaly | Classification | Disposition |
|---|---|---|---|
| E1 | cec2017/apgsk `environment.json` + `run_config.json` describe only the final D100 invocation (`dimensions_run = [100]`); environment metadata for the D10/D30/D50 invocations was overwritten | metadata-coverage defect (same root cause as seed/pairing anomaly A1) | Impact bounded: FP sentinel of the surviving file matches the suite (so the D100 re-run ran under the audited regime); the earlier invocations' sentinels are unrecoverable from the tree, but their outputs' consistency is demonstrated via the gen-log/summary equivalence checks in `seed_and_pairing_audit.md` §6. Carry into data ledger as reduced environment provenance for apgsk/cec2017 D10–D50; options: accept with this note, or re-promote a complete bundle. No in-place repair. |
| E2 | numpy/scipy versions unrecorded in all `environment.json` (Section 5); scipy version material for egsk solver provenance | provenance gap | Recover from producer-commit lockfiles into ledger/manifest; extend capture for future promotions. |
| E3 | Producer `git_commit` varies across cells (7 commits) and never equals the anchor commit | expected variation, documented | Record per-cell commit in data ledger; FP probes evidence numerical stability across the drift (with the Section 2 residual limitation on optimizer-specific kernels). |

## 8. Acceptance statement

- All 21 `environment.json` files read and tabulated; suite-internal sentinel consistency **PASS** (7/7 per suite).
- Expected cec2017 sentinel prefix `8bda40d8` **confirmed** as an audit target.
- Hardware, library, and runner configuration constant across the panel; all variation (commits, timestamps, apgsk metadata truncation) is enumerated above with dispositions.
- No unexplained anomaly remains in task 5 scope; E1/E2 require ledger entries (tasks 8–9) and a resolution decision before Gate 2.
