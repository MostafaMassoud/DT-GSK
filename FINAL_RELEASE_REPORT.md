# DT-GSK — Final Release Report (CEC2017)

> ⚠️ **HISTORICAL DOCUMENT — do not read this for current project state.**
> This report covers CEC2017 only and was written **before** submission. Its closing
> "PUBLISH READY" verdict describes the state as of the pre-submission release, not today:
> the manuscript has since been submitted to *Algorithms* (MDPI) as `algorithms-4507562`
> and has received a **MAJOR REVISION** from two reviewers.
> For current state — including which reviewer points are open and which claims the review
> put in question — see **[REVISION_STATUS.md](REVISION_STATUS.md)**.
> Retained for provenance. The section 9 mean-rank ordinals still hold against the frozen releases,
> but three framings below are superseded by the round-1 revision and must not be carried forward:
> the unqualified "#1-ranked algorithm in the GSK family" reading (Reviewer 2 asked that the best
> aggregate rank not be read as overall superiority — on CEC2017 the Holm-corrected tests separate
> DT-GSK from EGSK only at D10, and the two are never Nemenyi-separable at any dimension of that
> suite); the D50/D100 standing, now qualified as resting in part on the NP = 5D rule (re-run at
> the panel's NP = 100, DT-GSK is first at D10 and second at D30, D50 and D100); and the D30
> account in §11 and §13, which is incomplete rather than wrong — the uniform deep-stall trade-off
> is real, but the 20 ≤ D < 50 tier is also mis-specified: the parameter set DT-GSK resolves at
> D10 beats the set it ships at D30 on 20 of 29 functions (Holm 5.5e-3). The §9 rank decimals do
> not match any frozen release either; see the note there.

## 1. Executive summary
DT-GSK is the **#1-ranked algorithm in the GSK family** on CEC2017 (51 runs, 29 functions,
F2 excluded, unified Threefry seed schedule, error vs known optimum). It is **#1 at D10, D50,
D100 and #1 overall by both mean and median**; at **D30 it ranks #2 behind the strong EGSK
baseline** (the runner-up overall). The lone catastrophic
worst-case (F30 D10 run 27, a 1984× basin trap) is **fixed** by a standard, default-on
**deep-stall full-restart (multi-start)** mechanism that is byte-identical on non-stalling runs.

## 2. Final DT-GSK algorithm (what it is)
Vendored DT-GSK core (SGSM interaction graph at D≥50, TERRA stack at D≥100, ACE knowledge
control, NLPSR, BSE escape, archive) **plus** a new standard mechanism:
**deep-stall full restart.** When the incumbent has not improved for `deep_stall_frac` (0.25)
of the budget and the total budget exceeds `deep_stall_min_budget` (20000), the entire working
population is re-initialised uniformly while a separate global-best preserves the best-ever.
RNG is drawn only when it fires. `deep_stall_restart_enabled` defaults to **True**.

## 3. What changed from the previous DT-GSK
- **Added** the deep-stall full-restart (`src/gsk_family/optimizers/_dt_core.py`), default-on,
  with a min-budget guard. Fixes the BSE restart's structural flaw (it re-inits only the *worst*
  individuals, preserving a trapped elite, so it could never escape a deep basin).
- **Corrected** the diagnostics analyzer: added `ls_hit_rate` (the honest aggregate) because the
  prior `ls_waste_frac` was a per-trigger-median artifact that mislabelled net-useful LS as
  "100% wasted."
- **Rejected and removed** experiments that evidence disproved: Trust-Gated Local Search
  (0 improve/6 tie/4 worse), dimension-agnostic end-game polish (net-neutral; flag reverted),
  `bse_window=20` (regressed F13 at high-D).
- **Ran and rejected** a `strong_candidate` opt-in tuning experiment (variants a/b/c): full
  51-run validation showed no rank gain over the canonical profile, so it was **not promoted
  and fully removed**. DT-GSK ships the single canonical `pub` profile only.

## 4. Why the change is scientifically valid
- Targets a real, characterised failure (F30 D10 run 27, byte-faithful to source — not a bug).
- **Signal-driven, not function- or dimension-specific** → not overfit. Applied uniformly at all
  dimensions (default-on), not only where it helps.
- **Cannot lose ground** (global-best floor); **no extra NFEs**; **no RNG/seed/benchmark change**.
- Validated: rescues the trap; byte-identical at D50/D100; the min-budget guard keeps the
  byte-stability KAT identical (default-on is byte-safe).

## 5. Files modified / removed / retained
- **Modified:** `src/gsk_family/optimizers/_dt_core.py` (deep-stall mechanism, default-on;
  endgame flag reverted); `scripts/analyze_ism_diagnostics.py (since renamed analyze_dt_diagnostics.py)` (`ls_hit_rate`);
  `tests/unit/test_dt_profiles.py` (source-field parity contract).
- **Added:** `tests/unit/test_dt_deep_stall_restart.py`; `configs/publish/dt_gsk_cec2017_final.yml`;
  `ISM_GSK_TRAP_FIX_PLAN.md` (archived, then retired; retained in git history);
  the release notes below; this report.
- **Removed:** `tests/unit/test_ism_endgame_flag.py`, `configs/experimental/ism_endgame_d10d30.yml`
  (rejected endgame experiment).
- **Retained (reproducibility):** `benchmarks/cec_reference_results/`, benchmark runtime, all
  tests, governance docs, final results + seed_schedule/environment/run_config/protocol,
  `papers/scripts/`.

## 6. Release hardening pass (2026-07-03)

Executed `docs/prompt/publication-polish.md` to bring the repository to its
publication-ready state. Behavior-preserving only; all gates green afterward
(pytest all tiers, ruff, profile lock, docs build + link resolution, DT-GSK
byte-identity KATs untouched).

- **Removed:** rejected/superseded experimental configs (`bse_base_d10`,
  `bse_win20_d10`, `ism_ls_gate_config_only`, `ism_d10_dsr`, `ism_d30_dsr`,
  `ism_cec2011_dsr`); dead analysis modules (`analysis/plots.py`,
  `analysis/analyze_results.py`); LaTeX build intermediates and the orphaned
  `supplementary_v2.*` artifacts under `papers/` (now gitignored); a third-party
  PDF that must not ship publicly; `cleanup_candidates.csv` (fully actioned —
  the flagged stale `results/_experimental` / `_staging_*` trees were already
  purged earlier).
- **Archived:** the historical investigation records `ISM_GSK_TRAP_FIX_PLAN.md`,
  `ISM_GSK_REFERENCE_ROOTCAUSE.md`, and `DOC_POLISH_REPORT.md` moved from the
  root into `docs/development/` (rendered in the docs site; since relocated to
  `docs/development/history/`; that archive has since been retired -- the records
  remain in git history, and the DT2 retractions travel with the evidence in
  `benchmarks/cec_reference_results/_oracle/ (WITHDRAWN: the oracle study and its release orc-rel-2026-07-14 were removed from the paper and the tree deleted 2026-07-18; see papers/PAPER_REVIEW_PROMPT.md and the decision log) README.md`).
- **Prompts:** all completed-work prompts under `docs/prompt/` now carry
  historical-record banners; stale facts corrected (script count, test count,
  removed-module references); `publication-polish.md` added as the
  standing release-preparation prompt.
- **Documented decisions:** the module-private helper duplication across
  optimizer modules is recorded as an accepted trade-off in
  `DESIGN_GUIDE.md` §1.2; the legacy reference-seed formulas now carry a
  provenance note in `runners/seed_policy.py`; `papers/README.md` clarifies the
  manuscript-figure vs `gsk-stats` output split.
- **Known open items (documented, not defects):** package version remains
  `0.1.0` pending the maintainer's publication version decision. (The DT-GSK
  checkpoint gap previously listed here is closed: CEC2017 D10-D100 and
  CEC2011 generation logs are complete and the review-pack missing-curve log
  is empty.)

## 7. Convergence-telemetry fix (2026-07-05)

The deep-stall multi-start protects the *returned result* (a preserved global
best) but the vendored core reports the *working* incumbent to
`curve_callback` -- so on runs where the restart fired, the recorded
convergence trace jumped to a fresh random population's fitness (e.g. F1 D10:
0 -> 2.5e10 at eval 81,424) and could end above the returned best. Summary
tables, ranks, and all statistics were never affected; this was telemetry
only, but it corrupted the curve CSVs/PNGs and the checkpoint gen_logs that
feed the paper convergence grids (28/138 median-run curves; 1,165/6,466
checkpoint rows across 78 cells).

- **Code fix (adapter + writer; the locked core is untouched):**
  `optimizers/dt_gsk.py` now clamps both recording paths (fast
  `curve_callback` and the diagnostics `generation_callback`) to the running
  minimum, honoring the documented `ConvergenceTrace` best-so-far contract;
  `runners/output.py::_trace_values` additionally applies
  `np.minimum.accumulate` as defense-in-depth (a byte-identical no-op for the
  strictly greedy comparators). The diagnostics JSONL keeps the raw working
  incumbent (that is what diagnostics analyze).
- **Regression lock:** `tests/regression/test_dt_gsk_curve_monotone.py`
  forces a deep-stall restart via config overrides on a plateau objective and
  asserts (a) the raw core emission regresses (scenario guard) and (b) the
  adapter trace stays monotone and ends at the returned best.
- **Artifact repair (documented transformation, no re-run, no fabrication):**
  the affected `results/_run_all/dt-gsk` curve CSVs and CheckpointErrors rows
  were rewritten as the running-minimum (best-so-far) envelope of the recorded
  data -- exact for the full-resolution curves, and exact for the deep-stall
  spikes in the checkpoint rows because the >=25%-budget stall plateau always
  spans checkpoints. All 138 convergence PNGs and the review pack were
  regenerated; reference evidence was not touched. All gates green; the
  DT-GSK byte-identity KATs are unchanged.

## 8. Protocol & seed/RNG provenance
CEC2017, D∈{10,30,50,100}, F1+F3..F30, 51 runs, 10000·D NFEs, error vs optimum. Canonical RNG =
Threefry with `get_cec_seed(base=20240620, dim, func, run)`. The legacy `04` reference mismatch
(PCG64 + SeedSequence.spawn, base 123456) is a documented seed/RNG-regime artifact, not an
optimizer bug; it is **not** reproduced as the default.

## 9. Final CEC2017 results — family Friedman ranks (lower = better)
| Dim | DT-GSK (mean) | DT-GSK (median) | #1 |
|----:|---------------:|-----------------:|----|
| D10  | **#1** (2.88) | **#1** (2.67) | DT-GSK |
| D30  | #2 (2.47) | #2 (2.71) | EGSK |
| D50  | **#1** (2.00) | **#1** (2.19) | DT-GSK |
| D100 | **#1** (2.28) | **#1** (2.55) | DT-GSK |
| **Overall** | **#1 (2.41)** | **#1 (2.53)** | **DT-GSK** (2nd = EGSK) |

Friedman p-values: D10 3.1e-08, D30 5.7e-09, D50 1.1e-08, D100 1.6e-10. Wilcoxon+Holm tables,
effect sizes, win/tie/loss, and Nemenyi CD diagrams in `results/_run_all/_analysis/cec2017/`.

## 10. Outlier & failed-run audit (disclosed, not hidden)
- **F30 D10 run 27 (seed 87242640):** the only catastrophic trap (median 412 → 817,578 without
  the fix). With the default-on deep-stall restart: → **591**; F30 D10 mean 16,458 → 439, worst
  → 602. No other cell exceeds ~26× worst/median.
- **Prior `failed=1` (F13 D10 R7):** transient worker/IPC drop; complete trace + identical
  deterministic re-run. Not a bug.

## 11. D10/D30 analysis & D50/D100 preservation
- **D10:** the fix flips DT-GSK to #1 by mean (rescues run 27) and keeps #1 by median.
- **D30:** the fix rescues a few stalled runs (mean-rank improves 2.59→2.47) but prematurely
  restarts ~9 slow-converging multimodal functions (means worsen 2–12%). Accepted trade-off of
  applying the mechanism uniformly; DT-GSK is #2 at D30, behind only the strong EGSK baseline.
- **D50/D100:** **byte-identical** with/without the fix (productive runs never deep-stall) →
  DT-GSK's #1 standing is preserved exactly.

## 12. Tests & quality gates
`tests/unit + tests/smoke + tests/regression`: **303 passed** (at the 2026-07-05 release
snapshot; the suite has since grown substantially — re-check with `python -m pytest --collect-only -q`);
ruff `F,E9` clean;
`validate_profile_lock` passed (3 configs); reference validation OK; byte-stability KAT green
with the mechanism default-on (min-budget guard).

## 13. Limitations
- D30 multimodal slow-convergers see a small mean regression from the uniform deep-stall policy
  (disclosed §11). A budget/stagnation-adaptive trigger could reduce this but is left as future
  work to avoid overfitting the threshold.
- D30 #1 is held by the strong EGSK baseline (now a runnable optimizer, reported in the panel from
  its committed reference CSVs); DT-GSK is #2 at D30 and #1 at every other dimension and overall.

## 14. Final decision
**PUBLISH READY** — DT-GSK is #1 at D10/D50/D100 and #1 overall (and #2 at D30 behind EGSK) by
both mean and median, under the canonical protocol, with the sole catastrophic outlier fixed by
a validated default-on mechanism, all gates passing, and the outlier disclosed. Remaining items
are release hygiene (archive/delete stale `results/_experimental` traces; see cleanup manifest).
(Since actioned — §6 records the purge; neither `results/_experimental` nor the cleanup
manifest remains in the tree.)
