# DT-GSK Final Ablation Pre-Registration — **PHASE_12_ONLY**

**Status marker: PHASE_12_ONLY. Every section of this document is PHASE_12_ONLY.
Nothing in this document may be executed, aggregated, rendered, or interpreted
before the signed Phase 11 gate and an all-green `phase12_entry_certificate.md`.**

- **Phase / task:** Phase 5, task 17 (PAPER_BUILD_PROMPT.md §Phase 5, task 17) —
  pre-register the final ablation plan at design level only.
- **Date frozen:** 2026-07-10.
- **Primary evidence release in force:** `rel-2026-07-10-262fc16c9`
  (`benchmarks/cec_reference_results/`, read-only). The ablation will produce a
  **separate, new** immutable release (§5).
- **Design sources (all read-only, no outcome inspected):**
  `papers/build_prompt_phases/phase_03/ablation_toggle_audit.md` (verified toggle
  semantics), `scripts/run_ablation.py` (cell generator, design reading only),
  `papers/build_prompt_phases/phase_04/exhibit_plan.csv` rows X-ABL-01..03 and
  pre-registrations P2/P3, `papers/governance/seed_and_pairing_audit.md`,
  `papers/build_prompt_phases/phase_04/terminology_glossary.md`,
  `src/gsk_family/optimizers/_dt_core.py` / `_dt_profiles.py` (toggle scope),
  `src/gsk_family/analysis/statistics.py` and `statistical_tests.py`,
  `papers/scripts/generate_ablation_matrix.py`,
  `papers/build_prompt_phases/phase_03/complexity_analysis.md`.
- **Attestation (no-inspection):** no statistical outcome, rank, p-value, mean,
  or curve from any ablation cell was computed, read, or viewed in preparing this
  document. `results/_ablation/` (staging) is quarantined and was not opened.
  Feasibility checks were limited to schemas/headers of the primary release
  (e.g. `per_run.csv` header:
  `optimizer,suite,function,dimension,run,seed,best_fitness,error,nfes,termination,runtime_seconds`)
  and to source code.
- **Destination discipline:** all ablation exhibits are
  `supplement-phase12` / `DEFERRED_TO_PHASE_12_SUPPLEMENT_ONLY` (exhibit_plan.csv
  P6; thesis.md §7; PAPER_BUILD_PROMPT §1.3). Reserved labels: `tab:abl-scaffold`
  (X-ABL-01), `tab:abl-sgsm-overlay` (X-ABL-02), `tab:abl-wilcoxon` (X-ABL-03).
  No ablation number, rank, p-value, effect size, overhead value, or component-
  causality claim may enter the main manuscript.

---

## 1. X-ABL-01 — Scaffold remove-one ablation — **PHASE_12_ONLY**

**Design: remove-one from the full frozen scaffold; SGSM held OFF in every cell.**

### 1.1 Cells (7)

| Cell | `optimizer_options` override (on top of frozen `pub` profile + `interaction_graph_enabled: false`) | Component removed |
|---|---|---|
| `baseline` | *(none)* | — full scaffold, SGSM off |
| `no_ace` | `ace_enabled: false` | ACE knowledge control |
| `no_psr` | `psr_enabled: false` | NLPSR population reduction |
| `no_bse` | `bse_enabled: false` | Budget-Safe Escape |
| `no_linkage` | `linkage_blockwise_enabled: false` | Linkage-aware crossover |
| `no_localsearch` | `local_search_enabled: false` | Nelder–Mead endgame local search |
| `no_arch` | `arch_enabled: false` | Elite archive |

Cell generator: `scripts/run_ablation.py --mode remove-one` (writes per-cell YAML
to `configs/_ablation/`, runs via `gsk_family.cli.run`). SGSM is disabled in every
cell by the generator's `_SGSM_OFF = {"interaction_graph_enabled": false}`
(`run_ablation.py:52`); this scope MUST be verified from every generated config at
the §5 dry-run and MUST be stated in every table, caption, and interpretation:
**this study cannot establish SGSM's effect.**

### 1.2 Protocol constants (identical across all 7 cells)

- Suite: **CEC2017**, function set F1, F3–F30 (29 functions; F2 excluded per protocol).
- Dimensions: **D = 10, 30, 50, 100**.
- Runs: **25 per (cell, function, dimension)** (ablation protocol per
  PAPER_BUILD_PROMPT §12.3; disclosed as distinct from the primary panel's 51 runs).
- Budget: MaxFES = 10^4·D; identical failure policy, evaluator, environment, and
  FP regime across cells; objective-call equality is a validity requirement, not a finding.
- Seeds: base seed **20240620**, `seed_policy: unified`, `rand_generator: threefry`
  — `get_cec_seed(20240620, dim, func, run)`, the exact formula verified over
  70,813 schedule rows with 0 mismatches in
  `papers/governance/seed_and_pairing_audit.md`. Because the schedule contains no
  cell/algorithm term, **all 7 cells share identical seeds and identical
  runner-supplied initial populations per (dim, func, run)** — full-vs-cell
  contrasts are paired by construction (common random numbers), same basis as the
  panel pairing audit.
- Total runs: 7 cells × 4 dims × 29 functions × 25 runs = **20,300 runs**.

### 1.3 Mandatory disclosures (from `phase_03/ablation_toggle_audit.md`)

The two documented couplings MUST appear in the supplement write-up verbatim in
substance:

1. **arch → BSE seed source:** `arch_enabled: false` also removes BSE's
   archive-injection seed source (`bse_archive_inject_prob`); BSE still fires its
   Cauchy rescue. The `no_arch` delta is therefore the archive **plus** its role
   as BSE's restart seed pool — a real algorithmic dependency, not a toggle leak.
2. **BSE vs deep-stall distinctness:** `bse_enabled: false` does **not** disable
   the separate deep-stall restart (`deep_stall_restart_enabled`). A "no escape"
   reading of `no_bse` is incomplete; the deep-stall multi-start remains active in
   that cell.

### 1.4 Per-dimension baseline-ON check (binding rule)

Before any disable delta is claimed at dimension d, the resolved frozen `pub`
profile MUST be checked (from the cell `run_config.json` / effective-options echo
at the §5 dry-run) to confirm the mechanism was **ON in `baseline` at d** (e.g.
`local_search_enabled` and SGSM-dependent polish are only ON at D ≥ 50;
`linkage_blockwise_enabled` is tier-gated). If a mechanism is OFF in the baseline
at d, the (cell, d) contrast is a **null contrast**: it is excluded from the Holm
family at that dimension (§3.2), reported as "not identifiable at D=d (mechanism
inactive in baseline)", and never counted as evidence of a zero contribution.

### 1.5 Pre-registered exclusions (PAPER_BUILD_PROMPT §12.3 justification record)

Three additional flags are active in the frozen profile but are **excluded** from
the remove-one cell set, with these pre-registered justifications (toggle audit
finding 3; §12.3 admissibility clause):

- `argp_enabled` (`no_argp`): minor pool-pruning control parameterizing ACE's
  pool rather than a distinct mechanism; low marginal information per compute.
- `final_polish_enabled` (`no_finalpolish`): SGSM-dependent (eigenframe basis from
  the interaction graph); its contribution belongs to the SGSM-overlay design
  (§2), per the explicit §12.3 clause admitting this exclusion when recorded here.
- `deep_stall_restart_enabled` (`no_deepstall`): overlaps BSE as a stagnation
  response; a remove-one delta conditional on BSE-on is confounded, and the joint
  BSE×deep-stall factorial is out of pre-registered scope.

These exclusions are reportable **scope limits of the remove-one matrix**: the
X-ABL-01 write-up may not claim any contribution (positive, negative, or null)
for the three excluded mechanisms from the scaffold matrix alone. The
`final_polish_enabled` contribution is identified instead by the §2.1
`no_finalpolish` overlay cell (analysis family AN-ABL-POLISH); ARGP and
deep-stall restart remain untested (no contribution claims of any sign).

### 1.6 Interpretation boundary

Every X-ABL-01 delta is a **conditional remove-one contribution** (PAPER_BUILD_PROMPT
§12.2 estimand 1): the effect of disabling one component conditional on all other
scaffold components enabled and SGSM off. It is never reported as an independent
causal effect, never averaged across dimensions when sign or magnitude differs
materially, and never generalized beyond CEC2017 / the tested dimensions.

---

## 2. X-ABL-02 — SGSM-overlay ablation (CEC2013 hold-out design) — **PHASE_12_ONLY**

**Terminology rule (binding):** "hold-out" is used here strictly as the frozen
name of this ablation's *experimental design* per
`phase_04/terminology_glossary.md` (which permits the phrase only in this
supplement-only, Phase-12-only context, per `docs/algorithms/dt-gsk.md:473-474`
and the toggle audit). It is **not** a suite-level independence claim; CEC2013
remains the "second comparison suite" everywhere else.

### 2.1 Cells (4) — exact toggle composition (defined before execution, per §12.4)

| Cell | `optimizer_options` (on top of frozen `pub` profile; **no** `_SGSM_OFF` merge) | Meaning |
|---|---|---|
| `full` | *(none)* | frozen profile: SGSM on (`interaction_graph_enabled: true` at D ≥ `interaction_graph_min_dim` = 50), adaptive confidence gate on (`interaction_confidence_adaptive: true` per profile) |
| `no_adaptive` | `interaction_confidence_adaptive: false` **(this single toggle only)** | SGSM on, but the adaptive confidence gate is replaced by the frozen static thresholds (`interaction_confidence_min` and its `*_confidence_min` derivatives) |
| `no_sgsm` | `interaction_graph_enabled: false` **(this single toggle only)** | entire SGSM overlay off |
| `no_finalpolish` | `final_polish_enabled: false` **(this single toggle only)** | final polish off on top of the frozen `pub` profile; SGSM overlay and every other subsystem at frozen settings |

**Pre-registered rationale for the fourth cell:** the final polish is
SGSM-dependent — its eigenbasis derives from the interaction matrix
(`_dt_core._final_polish_basis`) — so its toggle belongs to the SGSM-overlay
cell family, not to the SGSM-off scaffold matrix (§1.5 exclusion, unchanged).
**AN-ABL-POLISH = `full` vs `no_finalpolish`** under the §3 Wilcoxon/Holm
machinery (§3.2), with the same suite, dimensions, runs, seeds, and budget as
the other overlay cells (§2.2). Without this cell AN-ABL-POLISH would be
unexecutable. **PHASE_12_ONLY.**

Tooling disposition (pre-registered, per §12.4): `scripts/run_ablation.py` cannot
emit SGSM-on cells (it merges `_SGSM_OFF` into every generated config). The four
cell YAMLs above are therefore **hand-authored frozen configs** executed via
`python run.py --config <cell>.yml`, with `generation_logs: true` (§4.1), the §1.2
seed/budget constants, and per-cell isolated output roots. Extending
`run_ablation.py` with an SGSM-overlay mode is the permitted alternative only if
the change is itself recorded as a pre-registered tooling change before execution.

### 2.2 Protocol

- Suite: **CEC2013** (28 functions, F1–F28), named explicitly per §12.4.
- Dimensions: **D = 50 and D = 100** (both in the evaluator's `VALID_DIMS`,
  `benchmarks/cec_suite_python/cec2013/transforms.py:92`). SGSM activates only at
  `interaction_graph_min_dim = 50` (`_dt_core.py:325`, profile `:120`), so D < 50
  contrasts compare identical algorithms and are **excluded from inference**.
  D100 on CEC2013 has no panel-release precedent; it is admissible here because
  every cell is an DT-GSK variant (no cross-algorithm panel comparability is
  consumed) — disclosed in the write-up.
- Runs: 25; seeds/budget/environment as §1.2. Total: 4 × 2 × 28 × 25 = **5,600 runs**.
- The `no_finalpolish` contrast is identifiable at both overlay dimensions:
  final polish is ON in `full` at D ≥ 50 per the frozen `pub` profile gating
  (§1.4 baseline-ON check; re-verified per cell at the §5 dry-run).
- Optional identity control (validation-only, drop-first under compute
  constraint): `full` vs `no_sgsm` at D30 is expected byte-identical (SGSM
  inactive); it may be replaced by config-level verification at the §5 dry-run.
  Never an inferential cell.

### 2.3 Mandatory disclosures

1. `no_sgsm` removes the **whole overlay and its consumers**: SGSM-fed linkage
   blocks, the LS-subspace steering, and the eigenframe source of the final
   polish (which falls back to its documented non-SGSM basis per
   `_dt_core._final_polish_basis`). The `no_sgsm` delta is the **joint overlay
   contribution**, never "the graph alone".
2. `no_adaptive` isolates only the adaptive confidence gate **conditional on SGSM
   on**; static thresholds remain at their frozen values (no retuning).
3. `no_finalpolish` removes ONLY the final polish stage; the rest of the SGSM
   overlay (graph maintenance, linkage feed, LS-subspace steering) remains
   active — the delta is the polish stage conditional on SGSM on, never an
   overlay-wide effect.
4. Whether CEC2013 was involved in development is not established; no independence
   or confirmation-suite wording is permitted (§2 header rule).
5. The direct SGSM comparison MUST report **both performance and overhead** (§4.2),
   per PAPER_BUILD_PROMPT §12.4.

Estimand: **direct SGSM overlay contribution** (§12.2 estimand 4), conditional on
the remaining frozen algorithm held constant.

---

## 3. X-ABL-03 — Statistical family — **PHASE_12_ONLY**

All inference reads exclusively from the promoted ablation release (§5), through
the strict-source guard (`GSK_STRICT_SOURCE` / `set_strict_source`,
`src/gsk_family/analysis/result_loader.py`). α = 0.05, two-sided, everywhere.

### 3.1 Units and pseudoreplication (binding)

- **Across-function inference is function-level:** the observation unit is the
  per-function summary statistic (mean final error over the 25 runs) per
  (cell, function, dimension). Run-level values are never pooled across functions
  as if independent.
- **Run-level data supports per-function pairwise effects only** (§3.4), which is
  valid here because every ablation cell is freshly run with `per_run.csv`
  (schema verified; §Attestation). The primary-panel apgsk per-run gap does not
  apply: no cross-algorithm panel data enters the ablation analyses.
- Pairing basis: identical unified seed schedule across cells per
  (dim, func, run) (§1.2; `papers/governance/seed_and_pairing_audit.md`).

### 3.2 Primary inferential family: full-vs-cell Wilcoxon + Holm, per dimension

- For each study and each dimension d, compare the reference cell (`baseline` for
  X-ABL-01; `full` for X-ABL-02) against every other cell with the **paired
  Wilcoxon signed-rank test across functions** on per-function mean final error
  (GSK-family convention; `zero_method='zsplit'` as implemented in
  `src/gsk_family/analysis/statistical_tests.py` and
  `gsk_family.analysis.statistics.wilcoxon_paired` used by
  `papers/scripts/generate_ablation_matrix.py`). [wilcoxon1945individual]
- **Holm correction within each (study, dimension) family** [holm1979simple]:
  - X-ABL-01 family at d: one comparison per mechanism cell whose mechanism is
    baseline-ON at d (§1.4) — family size ≤ 6, fixed by the dry-run profile
    resolution **before** any outcome is seen.
  - X-ABL-02 family at d: 3 comparisons (`full` vs `no_adaptive`, `full` vs
    `no_sgsm`, `full` vs `no_finalpolish`); the `full` vs `no_finalpolish`
    comparison carries the pre-registered analysis family **AN-ABL-POLISH**
    (§2.1 fourth cell).
  - No cross-dimension pooling; no cross-study pooling; no mixed families.
- **Benjamini–Hochberg** [benjamini1995controlling] is permitted ONLY as a
  separately-labeled exploratory table, never mixed with the Holm family, and only
  if retained by the frozen statistical_analysis_plan.md.

### 3.3 Rank structure: mean-Friedman-rank matrix, per dimension

- Per (study, dimension): Friedman ranks of all cells over the common function
  set (7 cells for X-ABL-01; 4 for X-ABL-02), reported as the mean-Friedman-rank
  matrix with the Friedman chi-square omnibus [friedman1937use;
  demsar2006statistical], computed by
  `papers/scripts/generate_ablation_matrix.py` (`friedman_rank`).
- Output schema (existing, frozen): `cell, label, disabled_flag, mean_rank,
  n_funcs, wilcoxon_p, holm_p, significant` — one row per cell, files
  `ablation_matrix_rank_summary_cec2017_D{10,30,50,100}.csv` (X-ABL-01) and the
  aggregator extended/wrapped (without touching raw evidence) to
  `ablation_overlay_rank_summary_cec2013_D{50,100}.csv` (X-ABL-02).
- The rank matrix is descriptive ordering evidence; the §3.2 Wilcoxon/Holm family
  carries the inferential weight.

### 3.4 Effect sizes and intervals (where per-run exists — here: all cells)

- **Per-function Vargha–Delaney A12** [vargha2000critique] reference-vs-cell over
  the 25 paired runs, per (cell, function, dimension)
  (`gsk_family.analysis.statistics.vargha_delaney`, `statistics.py:868`), with
  direction and the standard magnitude bands; reported per function, summarized
  per dimension by the median across functions (descriptive only).
- **Seeded BCa bootstrap CIs** [efron1993introduction] on the per-function mean
  error difference (reference − cell), resampling unit = run within function,
  `bootstrap_bca_ci` (`statistics.py:1396`) with `n_boot = 10,000`, 95% two-sided,
  `rng = numpy.random.default_rng(20240620)` (the function rejects unseeded use).
- Effects/intervals file schema (pre-registered):
  `ablation_effects_<study>_<suite>_D<dim>.csv` with columns
  `cell, function, n_runs, mean_diff, bca_lo, bca_hi, a12, a12_magnitude`.
- Every significance statement in the supplement carries its effect size and CI.

### 3.5 Interpretation discipline (PAPER_BUILD_PROMPT §12.12)

Each component discussion states: design (remove-one / direct / add-one /
cumulative / interaction), conditioning configuration, suite/dims/functions/
runs/seeds/budget, test + effect + interval, cost impact, convergence timing,
negative or inconsistent effects, and identifiability limits (§1.3, §2.3).
Prohibited: SGSM claims from the SGSM-off scaffold matrix; independent causality
from remove-one; universal benefit from one suite/dimension; ignoring overhead or
adverse effects; averaging sign-changing effects; modifying the algorithm in
response to any result.

Method citations restricted to `papers/governance/allowed_citation_keys.txt`:
friedman1937use, demsar2006statistical, wilcoxon1945individual, holm1979simple,
benjamini1995controlling, vargha2000critique, efron1993introduction (order
statistics, if needed for best-case counts: david_order_statistics).

---

## 4. Overhead, convergence, and sensitivity requirements — **PHASE_12_ONLY**

### 4.1 Convergence (reuses the P2/P3 pre-registered design)

- **Aggregation = P2 verbatim** (exhibit_plan.csv): per-checkpoint MEAN error
  across all runs per cell from `gen_logs/CheckpointErrors_*.csv`; identical basis
  for every curve in a panel; representative-run fallback
  (`curves/Figure_*.csv`) only when checkpoint logs are absent, caption-disclosed;
  missing cells disclosed, never fabricated/interpolated/silently dropped; no
  smoothing; no extrapolation past termination; display-only log floor documented
  at render time.
- **Styling = P3 discipline adapted to cells** (Okabe-Ito colorblind-safe,
  grayscale-distinguishable, fixed map, reference cell black solid 1.5×), frozen
  here before any rendering:
  - X-ABL-01: `baseline` #000000 solid (1.5×); `no_ace` #E69F00 dashed; `no_psr`
    #56B4E9 dash-dot; `no_bse` #009E73 densely-dashed; `no_linkage` #CC79A7
    long-dash; `no_localsearch` #0072B2 dash-dot-dot; `no_arch` #999999 dotted.
  - X-ABL-02: `full` #000000 solid (1.5×); `no_adaptive` #E69F00 dashed;
    `no_sgsm` #56B4E9 dash-dot; `no_finalpolish` #009E73 densely-dashed.
- **Feasibility requirement (pre-registered, binding):**
  `run_ablation.py._cell_config` currently writes `generation_logs: false` and
  `convergence_graphs: false` into every cell config — such cells emit **no**
  `CheckpointErrors_*.csv`. The Phase 12 campaign configs MUST set
  `generation_logs: true` (recorded as a pre-registered configuration amendment
  at the §5 dry-run). If the quarantined staging campaign is promoted as-is and
  its cells lack checkpoint logs, the convergence sub-analysis for those cells is
  marked **disclosed-unavailable** in `evidence_gap_register.md` (or a targeted
  convergence-only campaign is executed as a new promoted release); convergence
  is never reconstructed from summary files.

### 4.2 Overhead (governed by the Phase 5 cost plan)

- Rules of record: `papers/build_prompt_phases/phase_05/cost_analysis_plan.md`
  (Phase 5 task 11). The ablation reports overhead **deltas** under those rules:
  - Metric: `runtime_seconds` from each cell's `per_run.csv` (column verified in
    the release schema); objective-call accounting via `nfes` — **objective-call
    equality across cells is a validity gate** (§12.9), not a result.
  - Delta definition: per (cell, function, dimension), mean runtime over runs;
    overhead ratio = cell / reference; per-dimension summary = median ratio
    across functions with a seeded BCa CI (§3.4 machinery) on the per-function
    ratio set.
  - Algorithmic overhead is separated from objective-evaluation cost per
    `phase_03/complexity_analysis.md`; environment disclosed from each cell's
    `environment.json`.
  - Memory overhead only if the optional pre-freeze peak-memory harness
    (PAPER_BUILD_PROMPT §6.9) was built before the analysis freeze; otherwise the
    memory gap remains a documented `evidence_gap_register.md` entry — no
    instrumentation may be added in Phase 12 (frozen hashes).
- Output schema (pre-registered): `ablation_overhead_<study>_<suite>_D<dim>.csv`
  with columns `cell, function, n_runs, mean_runtime_s, runtime_ratio_vs_ref`
  plus a per-dimension summary row set `cell, median_ratio, bca_lo, bca_hi`.
- The X-ABL-02 write-up MUST pair performance and overhead (§12.4).

### 4.3 Sensitivity of ablation conclusions (exploratory-labeled, no code changes)

Three pre-registered robustness swaps, each reported as stable/unstable per
(study, dimension), never generating new headline claims:

1. per-function statistic swap: mean → median final error (recompute §3.2/§3.3);
2. error-floor swap: raw errors vs the documented 1e-8 display floor;
3. leave-one-function-out influence on the Friedman rank ordering (direction
   stability of the reference-vs-cell ordering).

Parameter sensitivity (n = 3 exploratory grid) is a **separate study** (Phase 5
task 10) and is not mixed with the ablation.

---

## 5. Execution gate and promotion (Section 2.4) — **PHASE_12_ONLY**

1. **No ablation objective evaluation may be launched, resumed, or analyzed
   before Phase 12**, entered only through the signed Phase 11 gate and an
   all-green `phase12_entry_certificate.md` (Gate 11). Design-level activity
   permitted earlier is limited to PAPER_BUILD_PROMPT §6.10 (audits, `--dry-run`
   with config restore, this pre-registration).
2. **Authoritative dry-run after Gate 11** (§12.7): regenerate configs, verify
   per cell — exact intended toggles only; frozen non-toggled parameters; SGSM
   scope (§1.1 off-everywhere; §2.1 hand-authored cells); suite/dims/functions/
   runs/seeds/MaxFES per §1.2/§2.2; `generation_logs: true` (§4.1); output-path
   isolation; no parameter retuning; no evidence overwrite — and render the
   configuration-difference matrix. Any unexpected difference blocks execution.
3. **Execution:** staging only, under `results/_ablation/<cell>/dt-gsk/<suite>/...`;
   seed 20240620 and run counts never reduced; failed/corrupt cells re-run via
   `--only <cell>` without protocol change; retries and hardware events logged.
4. **Validation before analysis** (§12.9): completeness (functions × dims × runs),
   seed-schedule match, per-run key uniqueness, MaxFES/objective-call equality,
   environment + FP sentinel, frozen code/config hashes, failure policy,
   checkpoint presence per §4.1, `runtime_seconds` instrumentation, no NaN/Inf or
   schema corruption, no cross-cell contamination. A partial matrix is never
   analyzed or reported as complete.
5. **Controlled promotion (Section 2.4):** validated staging is promoted via
   `scripts/promote_evidence.py` to a **new immutable ablation release**
   `benchmarks/cec_reference_results/ablation/<ablation_release_id>/`, mirroring
   the cell-first staging layout byte-for-byte, with
   `ablation_release_manifest.json`, checksums, and read-only status. From that
   point every ablation analysis reads exclusively from the promoted release
   (strict-source guard; outputs under `papers/analysis/<ablation_release_id>/<suite>/`);
   staging ceases to be an analytical input.
6. **Disposition of the currently running staging campaign:** the
   `results/_ablation/` campaign in progress at freeze time is **quarantined
   evidence**. No outcome, rank, p-value, mean, curve, or file content from it
   may be inspected before the Phase 11 freeze (development-leakage rule). In
   Phase 12 it MAY be promoted **iff** it passes item 4 validation **and**
   matches this pre-registration exactly (cells, suite, dimensions, runs, seed,
   SGSM-off scope); otherwise the affected cells are re-run under this protocol.
   Known pre-registered caveat: if that campaign was produced with
   `generation_logs: false`, the §4.1 convergence disposition applies. Staging
   `overwrite: true` semantics mean the promotion snapshot — not staging — is the
   immutable record.
7. **Amendments:** any post-freeze change to this design is logged and classified
   as confirmatory amendment or exploratory deviation (Phase 5 exit rule); silent
   deviation invalidates the affected analysis.

---

## 6. Secondary pre-registered designs (conditional on compute budget) — **PHASE_12_ONLY**

Priority order (drop-last-first when budget-constrained; every drop recorded in
`evidence_gap_register.md`, never silent): X-ABL-01 > X-ABL-02 > 6.1 > 6.2 > 6.3.
All use §1.2 constants at the dimensions stated; all inherit §3 statistics
(within their own Holm families), §4 requirements, and §5 gating.

### 6.1 Isolated add-one panel (§12.5.1) — estimand 2

`scripts/run_ablation.py --mode add-one`: `base` (all six scaffold flags off,
SGSM off) + one `only_<m>` cell per mechanism = 7 cells. Suite CEC2017, **D50
only** (lowest tier at which all six mechanisms are expected active in the frozen
profile; confirmed at the dry-run per §1.4 — if any mechanism is inactive at D50,
the lowest dimension where all are active is used, fixed before execution).
Identifiability screen: a component whose in-isolation consumers are disabled in
`base` (e.g. `only_arch` with BSE off removes the archive's injection consumer)
is marked **not identifiable in isolation** and reported as design-limited, not
as a null contribution. 7 × 29 × 25 = 5,075 runs.

### 6.2 Cumulative incremental chain (§12.5.2) — estimand 3

Dependency-respecting order fixed now (code dependencies, not expected
performance): `base` → `+ace` → `+psr` → `+bse` → `+arch` → `+linkage` →
`+localsearch`. Endpoints reuse existing configs (`base` = 6.1 base;
`+ace` = `only_ace`; final chain cell ≡ X-ABL-01 `baseline`), so 4 new cells.
CEC2017, D50 only. Every delta reported as **order-conditional**. 4 × 29 × 25 =
2,900 new runs.

### 6.3 Targeted interactions (§12.6) — estimand 5

Two pre-registered non-additivity contrasts at CEC2017 D50 via joint remove-two
cells (new configs `no_ace_psr`, `no_arch_bse`): compare
Δ(no_a) + Δ(no_b) vs Δ(no_a, no_b) against `baseline`, with the §3.4 effect/CI
machinery on per-function means. SGSM × linkage interaction requires SGSM-on
cells and is admissible only as a hand-authored extension of the §2 overlay
design, pre-registered before execution. Untested interactions are never claimed
absent. 2 × 29 × 25 = 1,450 runs.

---

## Cell inventory summary — **PHASE_12_ONLY**

| Study | Cells | Suite | Dimensions | Runs/cell/func | Functions | Total runs |
|---|---|---|---|---|---|---|
| X-ABL-01 scaffold remove-one (required) | 7 (`baseline`, `no_ace`, `no_psr`, `no_bse`, `no_linkage`, `no_localsearch`, `no_arch`) | CEC2017 | 10, 30, 50, 100 | 25 | 29 | 20,300 |
| X-ABL-02 SGSM overlay (required) | 4 (`full`, `no_adaptive`, `no_sgsm`, `no_finalpolish`) | CEC2013 | 50, 100 | 25 | 28 | 5,600 |
| 6.1 add-one (secondary) | 7 (`base`, `only_<m>` × 6) | CEC2017 | 50 | 25 | 29 | 5,075 |
| 6.2 cumulative chain (secondary) | 4 new (`+psr`…`+linkage` interiors) | CEC2017 | 50 | 25 | 29 | 2,900 |
| 6.3 interactions (secondary) | 2 (`no_ace_psr`, `no_arch_bse`) | CEC2017 | 50 | 25 | 29 | 1,450 |
| **Required core total** | **11 cells / 36 cell-dimension combinations** | | | | | **25,900** |
| **Full pre-registered total** | **24 cells / 49 cell-dimension combinations** | | | | | **35,325** |

Seed 20240620 unified/threefry everywhere; SGSM off in every X-ABL-01/6.1/6.2/6.3
cell; α = 0.05; Holm primary; supplement-phase12 only.

*End of pre-registration. PHASE_12_ONLY.*
