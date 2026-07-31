# Phase 5 — Pre-registered computational-cost analysis plan (task 11)

- **Date frozen:** 2026-07-10 (BEFORE any outcome inspection; no timing statistic has been
  computed or viewed from the evidence in preparing this plan — only schemas/headers were
  read for feasibility).
- **Phase / task:** Phase 5, task 11 (cost analysis plan feeding exhibit `T-RUNTIME`,
  claims C1;C4 per `phase_04/exhibit_plan.csv`).
- **Evidence release:** `rel-2026-07-10-262fc16c9` (`benchmarks/cec_reference_results/`,
  read-only; anchor commit `262fc16c91fbe5608a1a0b0c5df3cbcd009edc21`).
- **Governance sources read (cited by path):** `papers/governance/comparability_audit.md`;
  `papers/governance/fp_environment_audit.md`; `papers/governance/seed_and_pairing_audit.md`;
  `papers/governance/phase2_anomaly_register.csv`; `phase_03/complexity_analysis.md`;
  `phase_03/evaluation_accounting_report.md`.
- **Execution phase:** Phase 6, through the strict-source loader
  (`src/gsk_family/analysis/result_loader.py`: `set_strict_source` / `GSK_STRICT_SOURCE`).
  Output area: `papers/analysis/rel-2026-07-10-262fc16c9/<suite>/cost/`.
  All numeric cells are placeholders `<T-RUNTIME:*>` until Phase 6 binds them.

---

## 1. Data basis (feasibility verified read-only)

- **Per-run wall-clock exists in the release:** every class-A `per_run.csv` carries the
  column `runtime_seconds` (header verified in cec2017, cec2013, cec2011 cells; schema:
  `optimizer,suite,function,dimension,run,seed,best_fitness,error,nfes,termination,runtime_seconds`).
- **Repetitions available:** 51 runs per (function, dimension) for cec2017 (29 functions ×
  D10/30/50/100) and cec2013 (28 functions × D10/30/50); 25 runs per problem for cec2011
  (22 problems, native dimensions). Per `fp_environment_audit.md` §3, `skipped_cells = []`
  — no missing runs in any class-A cell.
- **KNOWN GAP (pre-specified disposition):** `cec2017/apgsk/per_run.csv` covers D100 only
  (1,479 rows; anomaly A2-004 in `papers/governance/phase2_anomaly_register.csv`;
  provisional class C per `comparability_audit.md` §3). The gen_logs fallback that
  recovers apgsk's D10/30/50 *endpoints* (`CheckpointErrors_apgsk_F*_D*.csv`, columns
  `Run,Seed,E<checkpoint>` — header verified) carries **no timing column**, so per-run
  wall-clock for apgsk at cec2017 D10/D30/D50 is **unrecoverable from the release**.
  Disposition: those three T-RUNTIME cells are marked **disclosed-unavailable** ("timing
  not recorded in release; A2-004") — never imputed, never borrowed from other dims, and
  unaffected by whichever Gate 2 option resolves P2-A5 (neither option restores historical
  timing; only reproduce-and-promote would create NEW timing under a new release id).
- **Class D context cells** (cec2020/agsk; cec2013lsgo/decc-g, mos) carry no timing, no
  environment metadata (`fp_environment_audit.md` §6) and are excluded from every cost
  exhibit per `comparability_audit.md` §3 (prohibited from any panel table).

## 2. Metrics (pre-registered)

### 2.1 Wall-clock per run (primary descriptive metric)

- Unit of observation: one run's `runtime_seconds`.
- Per-function summary: mean and sample SD across runs (median additionally recorded), per
  (optimizer, suite, function, dimension).
- Per-dimension aggregation: unweighted mean across functions of the per-function means
  (function-level aggregation; runs never pooled across functions — pseudoreplication
  rule). T-RUNTIME reports the per-dimension aggregate per optimizer, with per-function
  detail retained in the analysis output CSVs.

### 2.2 Budget-normalized wall-clock (fairness metric for early-stop cells)

- Motivation (pre-registered, from the anomaly register, not from outcomes): agsk and
  apgsk terminate early on `target_error_reached` in many runs (A2-001: 404 runs,
  cec2017/agsk; A2-029: 558 runs, cec2013/agsk; A2-032: 545 runs, cec2013/apgsk;
  protocol-legitimate, `nfes < MaxFES` by design). Raw wall-clock is therefore
  conditioned on evaluations actually spent.
- Metric: `seconds_per_1e4_evals = runtime_seconds / nfes × 10^4` per run, using the
  recorded `nfes` column; summarized exactly as in 2.1. Both raw and normalized values
  appear in the analysis outputs; T-RUNTIME states which is displayed and footnotes the
  early-stop counts.

### 2.3 Algorithmic overhead separated from objective cost

Two complementary treatments, both pre-registered — the release contains **no per-phase
timing breakdown** (`profile_enabled = false` in all 21 cells,
`fp_environment_audit.md` §3), so per-subsystem measured timing is impossible and is not
claimed:

1. **Analytic separation (authoritative):** transcribed from
   `phase_03/complexity_analysis.md` — per-generation overhead `O(NP·D)` (GSK core);
   dimension-gated SGSM refresh `O(D^2)` amortised to `O(D^2/5)`/gen; one-shot `O(D^3)`
   eigendecomposition; subspace LS `O(k·b)`, `b ≤ 20`; memory dominated by the `D×D`
   interaction matrix at D ≥ 50. Objective cost is `10^4·D · cost(f)` independent of
   overhead (MaxFES-exact accounting per `phase_03/evaluation_accounting_report.md`:
   single BudgetController cap, budget-safe exits, polish probes and restart
   re-evaluations charged). Wording guards from `complexity_analysis.md` are binding:
   SGSM/polish are `O(D^2)`/`O(D^3)` **compute** cost, explicitly amortised, never
   "free"; no claim of better overall complexity than GSK; low-D runs pay nothing for the
   tier-gated structures.
2. **Empirical paired-overhead proxy:** because all seven optimizers evaluate
   byte-identical objectives on identical (function, dimension, run) triples with
   identical seeds and shared X0 (`seed_and_pairing_audit.md` §4), the paired per-run
   difference/ratio `runtime(dt-gsk) − runtime(gsk)` (and vs each comparator) on triples
   where BOTH runs terminated at `max_evaluations` (equal `nfes`) isolates the
   algorithmic-overhead difference plus environment noise, since objective work is equal.
   Procedure: per (suite, function, dimension), paired mean difference and paired ratio of
   `runtime_seconds` restricted to equal-`nfes` pairs; the number of excluded (early-stop)
   pairs is reported per cell. Runs never pooled across functions.

### 2.4 Normalization: overhead as % of total runtime

- Definition (pre-registered): for each equal-`nfes` paired triple,
  `overhead_pct = (runtime_A − runtime_gsk) / runtime_A × 100` with A = dt-gsk (and,
  in the supplement detail, each other comparator), using gsk (the unmodified base
  algorithm, same shared kernel and RNG per `fp_environment_audit.md` §2) as the
  objective-plus-core baseline. Summarized per function then per dimension as in 2.1.
- Disclosed caveat (in prose AND caption): this is a *relative-to-base-algorithm* proxy,
  not a measured decomposition; negative values are possible (e.g., DT-GSK's NLPSR
  population shrinking reduces per-generation work) and are reported as-is.

## 3. Environment comparability rule (binding for prose AND captions)

1. **Within-release comparisons are environment-comparable with disclosed noise sources.**
   All 21 class-A cells ran on one host (`HUAWEI-MMASOUD`, Windows 10.0.26200, 22 logical
   cores, Python 3.10.11, numba 0.64.0/llvmlite 0.46.0, threefry RNG, python backend,
   `parallel_backend = process` with 15 workers, `numba_threads_active = 1` per worker) —
   `fp_environment_audit.md` §3. Mandatory disclosures wherever timing appears:
   (a) runs executed under 15-way process parallelism, so `runtime_seconds` includes
   co-scheduling/contention effects; CIs quantify run-to-run spread on this host, not
   cross-host validity; (b) the panel was a rolling campaign over 7 producer commits
   (2026-07-08 → 2026-07-10, `fp_environment_audit.md` §4) with proven code identity
   (empty diffs) and constant hardware/library stack, but uncontrolled background load;
   (c) numpy/scipy versions are unrecorded in the release (gap E2), qualifying absolute
   times.
2. **Values from incompatible environments are never compared without explicit
   qualification in prose AND captions.** Concretely: no timing from outside
   `rel-2026-07-10-262fc16c9` (published MATLAB runtimes, imported context tables,
   git-history fmincon-era artifacts, any other machine) may appear in T-RUNTIME or be
   ratio-ed/differenced against release timings. If a literature runtime is ever quoted in
   prose, it is a clearly-labeled citation with its own environment stated, never a panel
   column (cf. class-D discipline, `comparability_audit.md` §3).
3. **eGSK provenance (rule R-EGSK-1, `comparability_audit.md` §4):** all eGSK timing is
   the SciPy-SLSQP Python port's timing, and every cost exhibit names it
   "eGSK (Python port, SLSQP polish)". MATLAB-fmincon timing (a different solver AND a
   different runtime environment) must never be substituted, averaged, or displayed beside
   the port's values inside one exhibit; no numerical-equivalence claim between backends.
   The scipy version gap (E2, `fp_environment_audit.md` §5) is disclosed in the T-RUNTIME
   caption note for the eGSK row.
4. **Single-host limitation:** no independently-verified second-environment timing exists
   (`comparability_audit.md` §2 verification caveat); timing claims are scoped to this
   environment in the threats-to-validity prose.

## 4. Dimensions covered and repetitions (pre-registered exhibit scope)

| Suite | Dimensions in T-RUNTIME | Functions | Runs/cell | Timing availability |
|---|---|---|---|---|
| cec2017 | D10, D30, D50, D100 | 29 (F1, F3–F30) | 51 | 6/7 optimizers all dims; apgsk D100 only (D10/30/50 disclosed-unavailable, A2-004) |
| cec2013 | D10, D30, D50 | 28 | 51 | 7/7 optimizers, all dims |
| cec2011 | native problem dims (22 problems) | 22 | 25 | 7/7 optimizers; reported per problem or condensed (supplement detail) |

Main-text T-RUNTIME is the cec2017 table (per-dimension aggregates + overhead columns
per Section 2), consistent with its `exhibit_plan.csv` sourcing
(`phase_03/complexity_analysis.md` + release timing + `comparability_audit.md`);
cec2013/cec2011 cost tables go to the analysis outputs/supplement if page budget binds.

## 5. Confidence intervals

- **Where per-run timing exists (all class-A cells):** BCa bootstrap 95% CIs
  [efron1993introduction] via `src/gsk_family/analysis/statistics.py::bootstrap_bca_ci`,
  computed at two pre-registered levels:
  1. per-function mean `runtime_seconds` (resampling the 51/25 runs within a function);
  2. per-dimension aggregate (resampling functions, i.e., the per-function means, at the
     function level — consistent with the pseudoreplication rule), applied to both the
     raw metric (2.1) and the paired overhead metrics (2.3-2/2.4).
  Bootstrap parameters fixed now: 10,000 resamples, seed 20240620, percentile fallback
  disclosed if BCa degenerates (all-equal resamples).
- **Where per-run timing does not exist** (apgsk cec2017 D10/30/50; any context cell):
  **descriptive-only and disclosed** — the cell shows the unavailable marker; no CI, no
  imputation, no substitution from other dimensions.
- **No hypothesis tests on timing.** Cost analysis is descriptive + CI only (no p-values,
  so no multiplicity family is created; if any future revision adds tests, they must join
  the Phase 5 Holm framework — `robustness_plan.md` Section 0.1).

## 6. Execution and audit requirements (Phase 6 contract)

- One script `papers/scripts/generate_cost_analysis.py` (new; release-wired per
  exhibit_plan P7), reading exclusively through `result_loader.set_strict_source(True)`;
  source audit dumped as `cost_source_audit.json` next to outputs. `results/` staging
  (including `results/_ablation/`) is never read.
- Outputs per suite under `papers/analysis/rel-2026-07-10-262fc16c9/<suite>/cost/`:
  `runtime_per_function.csv`, `runtime_per_dimension.csv`, `overhead_paired.csv`,
  `runtime_digest.md`; T-RUNTIME LaTeX emitted with per-cell comparability footnotes.
- Every T-RUNTIME caption carries, verbatim commitments: the single-host/15-worker
  disclosure (Section 3.1), the eGSK port naming (Section 3.3), the apgsk unavailability
  note (Section 1), and the "ISM adds no extra objective evaluations; overhead is compute,
  not budget" framing sourced from `phase_03/evaluation_accounting_report.md` (verdict:
  MaxFES-exact single-cap accounting) and `phase_03/complexity_analysis.md` wording
  guards.

## 7. Citation keys used (all in `papers/governance/allowed_citation_keys.txt`)

`efron1993introduction` (BCa CIs). Complexity/accounting content cites internal frozen
artifacts by path (`phase_03/complexity_analysis.md`,
`phase_03/evaluation_accounting_report.md`), not literature keys.
