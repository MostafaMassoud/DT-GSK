# DT-GSK — Accepted Contributions (Phase 4, tasks 2–3)

**Phase 4 deliverable (claim-freeze input to Gate 4).** Date: 2026-07-10.
Source of record: `papers/build_prompt_phases/phase_03/contribution_matrix.md` (FROZEN;
16 mechanisms, INH/MOD/ORI, code anchors) and its novelty statement + prohibited
wordings, inherited verbatim. This file applies the Phase 4 **contribution acceptance
test** (keep 3–5 load-bearing contributions; remove duplicates, implementation trivia,
and unsupported novelty; claim no component contribution before the Phase-12 ablation).

**Result: 4 accepted contributions (C1–C4).**

**Numeric discipline.** No empirical value is stated as fact. Evidence slots are
exhibit-bound placeholders `<TXX:field>` / `<FXX:field>` (provisional IDs; to be
reconciled with the Phase 4 task-8 exhibit plan and bound in Phase 6 from release
`rel-2026-07-10-262fc16c9`). Every component-causality slot is marked
`DEFERRED_TO_PHASE_12_SUPPLEMENT_ONLY`.

## Provisional exhibit-placeholder registry (used below)

| ID | Planned exhibit |
|---|---|
| T01 | CEC2017 per-function descriptive statistics, 7-algorithm panel, per dimension |
| T02 | Wilcoxon signed-rank + Holm pairwise outcomes, DT-GSK vs each comparator |
| T03 | Vargha–Delaney A12 / Cliff's delta + BCa CIs + win/tie/loss |
| T04 | CEC2011 panel results (descriptive + ranks) |
| T05 | CEC2017 Friedman mean ranks (per dimension + overall, Iman–Davenport) |
| T06 | CEC2013 second-comparison-suite panel results |
| T07 | Experimental-protocol / reproducibility summary (budgets, seeds, release id) |
| F01 | Nemenyi critical-difference diagrams per dimension |
| F02 | Family-overlay convergence grids (CR-0001 pre-registered design) |
| F03 | Rank-vs-dimension scalability trend |
| SA01–SA03 | RESERVED, ablation exhibits — `DEFERRED_TO_PHASE_12_SUPPLEMENT_ONLY` (scaffold ablation matrix; SGSM-overlay `full`/`no-adaptive`/`no-sgsm` cells; full-vs-cell Wilcoxon/Holm) |

---

## C1 — Interaction-structure memory (ISM; code alias SGSM): zero-extra-objective-evaluation structure learning from accepted moves

- **Category:** ORIGINAL (phase_03 row 11), absorbing row 8 (linkage-aware block
  crossover, MOD) as its exploitation channel.
- **Exact difference vs closest work:** ISM learns a decaying (λ = 0.95),
  confidence- and evidence-gated coordinate-pair interaction graph **from the moves the
  run already accepted**, at **no extra objective evaluations** (compute cost stated in
  `phase_03/complexity_analysis.md` — never worded as "free"). Differential grouping
  [omidvar2014dg] learns interaction structure by *dedicated offline probing* that
  spends O(n²/m) objective evaluations before optimization begins and feeds a
  decomposition; ISM probes nothing, decomposes nothing, and feeds linkage blocks into
  the GSK crossover (replacing the per-coordinate KR mask of [mohamed2020gaining] for
  ~70% of the population; graph-supplied blocks at D ≥ 50) plus a top-k-block subspace
  to local search. Unlike covariance-eigenbasis methods [guo2015eig], it maintains a
  sparse signed pair graph rather than a per-generation population covariance, and
  leaves the base operator numerics unchanged.
- **Code location:**
  `src/gsk_family/optimizers/_dt_subsystems/interaction_graph.py:1` (862 lines);
  exploitation path `_dt_core.py` — `_make_linkage_groups:908`,
  `_build_phase4_masks:926`, `_resolve_linkage_block_size:839`.
- **Primary evidence:** `<T05:friedman_rank_D50>`, `<T05:friedman_rank_D100>`,
  `<F03:rank_vs_dimension_trend>`, `<F02:convergence_grids_D50_D100>` (ISM is
  D ≥ 50-gated under the `pub` profile, so its footprint is the high-D panel behavior).
- **Final-phase ablation need:** YES — any statement that ISM *causes* performance is
  `DEFERRED_TO_PHASE_12_SUPPLEMENT_ONLY` (SGSM-overlay cells `SA02`). Main text presents
  ISM as a proposed, fully specified mechanism only.
- **Scope bound:** active at D ≥ 50 (`pub` profile); learns from accepted moves only —
  no claim that it recovers the true separability structure of the objective; no LSGO
  claim (evidence tops out at D = 100).
- **Reviewer risk + mitigation:** risk — "this is differential grouping / covariance
  learning re-badged." Mitigation: the four-dimension comparison table in
  `phase_04/novelty_scope.md` (update trigger, evaluation cost, what is learned, how
  exploited), each cell backed by evidence cards; plus the prohibited-wording guard
  (never "free"; always "no extra objective evaluations", with compute cost cited).

## C2 — Eigenframe final polish: deterministic, RNG-free endgame on the learned interaction eigenbasis

- **Category:** ORIGINAL (phase_03 row 12).
- **Exact difference vs closest work:** a one-shot **deterministic compass search
  executed on the eigenbasis of the ISM signed interaction matrix** in the final budget
  slice (coordinate axes when no graph signal). Classical compass/pattern search
  [kolda2003directsearch] and Nelder–Mead [nelder1965simplex] search in the coordinate
  frame (or a simplex) throughout the run and carry no learned basis; the polish
  inherits its basis from C1's accepted-move memory, fires once, consumes budget via the
  strict accounting path, and draws no RNG — byte-identical trajectories whether it
  fires or not. No convergence guarantee is claimed, and no equivalence to
  generating-set search is implied.
- **Code location:** `src/gsk_family/optimizers/_dt_core.py` —
  `_final_polish_basis:1882`, `_final_polish_compass:1907`.
- **Primary evidence:** `<T01:cec2017_endpoint_stats_D50_D100>`,
  `<F02:convergence_grids_final_slice>` (endgame behavior at high D).
- **Final-phase ablation need:** YES — component causality (`final_polish_enabled`
  toggle) is `DEFERRED_TO_PHASE_12_SUPPLEMENT_ONLY` (`SA01`).
- **Scope bound:** D ≥ 50 tier; final budget slice only; conceptual-level comparison to
  direct search per the kolda2003directsearch card (no GSS theory transfer).
- **Reviewer risk + mitigation:** risk — "a local-search bolt-on; why not standard NM?"
  Mitigation: the differentiator is *where the basis comes from* (learned signed
  interaction matrix) and the determinism/byte-stability property; NM's known failure
  modes and lack of guarantees [kolda2003directsearch, nelder1965simplex] are cited as
  bounded motivation for a capped, one-shot, deterministic design.

## C3 — Dimension-tiered adaptive scaffold: ACE bandit + ARGP pruning + NLPSR floor + budget-safe BSE + deep-stall restart with global-best invariant

- **Category:** MODIFIED/ORIGINAL composite — honestly labeled (phase_03 rows 5, 6, 7,
  9, 13, with row 10 elite archive as BSE's seeding sub-component). ACE, NLPSR, BSE,
  elite archive, deep-stall are MOD; ARGP is ORI.
- **Exact difference vs closest work:** AGSK adapts KF/KR from a fixed pool by success
  history [mohamed2020agsk], APGSK extends the parameter pools [mohamed2021novel];
  **ACE** instead runs an EMA-credit multi-armed bandit over a 5-arm (KF, KR, Kexp)
  *operator* pool (arm 2 = GSK-pure) with a min-probability floor — operator-level, not
  parameter-level, adaptation, with credit memory in the spirit of SHADE's success
  history [tanabe2013shade]. **ARGP** (original; no direct GSK-family antecedent)
  freezes arms whose windowed acceptance falls below a tier threshold after warm-up.
  **NLPSR** keeps the x^(1−x) reduction shape of APGSK NLPSR [mohamed2020agsk,
  tanabe2014improving] but starts from dimension-scaled NP = 5·D and bottoms at a
  tier-specific floor — explicitly *not* claimed as new. **BSE** is a triple-trigger
  stagnation escape (Cauchy rescue + archive-seeded partial restart in the
  JADE/SHADE-archive lineage [zhang2009jade, tanabe2013shade, storn1997differential])
  that is **hard-capped** (`bse_max_restarts`, `bse_stop_frac`) so it can never overshoot
  MaxFES. The **deep-stall restart** fully re-initializes the working population on a
  deep stall while **preserving the global best** — the restart-never-loses-ground
  invariant.
- **Code location:** `src/gsk_family/optimizers/_dt_core.py` — ACE
  `_ace_update_probs:1193`, `_ace_sample_indices:1163`, `ace_pool:202`; ARGP
  `_argp_update_memory_probs:1261`, `_argp_update_memory_probs_guarded:1304`; NLPSR
  `_psr_target_size:790` (+ `_numba_accel._psr_target_nb:909`); BSE
  `StagnationDetector:1813`, `cauchy_like:1412`, `EliteArchive:1640`; deep-stall fields
  `:444` + restart block in `dt_gsk_optimize`.
- **Primary evidence:** `<T05:friedman_rank_D10>`, `<T05:friedman_rank_D30>`,
  `<T01:cec2017_descriptive_low_mid_D>`, `<T04:cec2011_panel_results>` (the scaffold is
  what runs at every tier; low/mid-D behavior is its footprint).
- **Final-phase ablation need:** YES — per-component causality (ACE, NLPSR, BSE,
  linkage, archive toggles) is `DEFERRED_TO_PHASE_12_SUPPLEMENT_ONLY` (`SA01`, `SA03`).
- **Scope bound:** tier-resolved `pub` profile values only (`phase_03/
  parameter_table.md`); the D ≥ 100 controllers (row 14) are documented method detail
  under this scaffold, not an elevated claim; contribution language is "control, budget,
  structure-memory, and polish layered on the GSK scaffold" — never a new base operator.
- **Reviewer risk + mitigation:** risk — "a grab-bag of tricks with unclear individual
  value." Mitigation: honest MOD/ORI labeling per sub-mechanism with citations to the
  exact antecedents; single frozen composite configuration (no per-suite tuning);
  individual value explicitly deferred to the Phase-12 supplement rather than asserted.

## C4 — Controlled, reproducible family evaluation + byte-stable ablation infrastructure

- **Category:** ORIGINAL infrastructure contribution (phase_03 row 15 + the evaluation
  protocol; row 16 self-init documented as the protocol exception).
- **Exact difference vs closest work:** GSK-family papers report suite results but do
  not ship a determinism layer that makes *component-level* re-evaluation byte-stable.
  DT-GSK's **13-substream, append-only, prefix-locked RNG layer** (counter-based,
  child-seeded from one run seed) guarantees that toggling any subsystem cannot disturb
  any other subsystem's draw order — the property that makes byte-stable ablation and
  exact reproduction possible. Around it: the paired optimizer-independent seed schedule
  keyed (dim, func, run) with shared X0; the hash-frozen `pub` profile
  (`algorithm_freeze_manifest.json`, `validate_profile_lock.py`); and the promoted,
  read-only evidence release `rel-2026-07-10-262fc16c9` with per-cell checksums and
  environment records (`papers/governance/data_ledger.csv`).
- **Code location:** `src/gsk_family/optimizers/_dt_rng.py:1`;
  `src/gsk_family/optimizers/_dt_profiles.py`; `scripts/promote_evidence.py`;
  `tests/regression/test_dt_gsk_byte_stable.py`; `tests/unit/test_dt_profiles.py`;
  ledger `papers/governance/data_ledger.csv`.
- **Primary evidence:** `<T07:protocol_reproducibility_summary>`; the Phase 3
  deterministic trace (`phase_03/deterministic_trace/` — budget-exact, monotone,
  repeat-identical) and the Phase 6 dynamic high-D witnesses; the release manifest
  itself. This contribution is defended by verifiable artifacts, not by performance
  numbers.
- **Final-phase ablation need:** NO causality claim to defer — the infrastructure is
  the *enabler* of the Phase-12 ablation, and that role is stated as design fact
  (byte-stability is test-enforced), not as a performance claim. Ablation *results*
  remain `DEFERRED_TO_PHASE_12_SUPPLEMENT_ONLY`.
- **Scope bound:** reproducibility claims cover this repository's runner, suites, and
  release pipeline; no claim that comparator reimplementations are byte-stable (eGSK
  panel data comes from committed reference CSVs; solver-provenance note in the ledger).
- **Reviewer risk + mitigation:** risk — "engineering, not science." Mitigation: framed
  as the evaluation-integrity contribution that makes every other claim checkable
  (paired seeds, frozen profile, promoted evidence, byte-stable toggles); MDPI
  Algorithms readership values reproducible algorithmic artifacts; kept as one
  contribution, not inflated into several.

---

## Phase_03 rows NOT elevated (acceptance test rejections), and why

| Phase_03 row | Mechanism | Class | Why not elevated |
|---|---|---|---|
| 1–3 | GSK junior/senior operator, Kexp schedule, greedy selection | INH | Inherited unchanged from [mohamed2020gaining] — definitionally not contributions; prohibited wording guard: never describe the gaining-sharing operator as novel. |
| 4 | Midpoint bound repair | INH | Inherited from L-SHADE [tanabe2014improving]; implementation detail. |
| 5 | NLPSR | MOD | Not standalone — tier-floored variant of the APGSK NLPSR schedule (prohibited to claim as new); folded into C3. |
| 8 | Linkage-aware block crossover | MOD | Not standalone — it is C1's exploitation channel (graph-supplied blocks at D ≥ 50); below D50 it is a fixed contiguous-block variant of the KR mask, which alone would be unsupported novelty. Folded into C1. |
| 10 | Elite archive | MOD | JADE/SHADE-lineage archive [zhang2009jade, tanabe2013shade] with a distance threshold — supporting component of BSE; folded into C3. |
| 14 | D≥100 controllers (A1/A2/FC4, basin memory, SP-NLPSR, TERRA) | ORI | Original but not load-bearing as a headline: high-D protective engineering with no isolated main-text evidence plan; elevating it would dilute C1–C3 and invite causality questions that are `DEFERRED_TO_PHASE_12_SUPPLEMENT_ONLY`. Documented as method detail under C3's dimension-tier scope. |
| 16 | Self-init (fair-start exception) | MOD | Protocol documentation, not a contribution; recorded in the protocol exhibit `<T07>` as the documented exception. |

Duplicate-elimination note: rows 6+7 merge into C3 (control), rows 9+10+13 merge into C3
(budget/escape), rows 8+11 merge into C1 (structure memory + exploitation), row 12
stands alone as C2, row 15 anchors C4. This yields exactly four load-bearing
contributions — within the framework's three-to-five band.

## Acceptance-test attestation

- 3–5 load-bearing contributions: **4** ✅
- Duplicates removed (mechanism-level rows merged into claim-level contributions) ✅
- Implementation trivia removed (rows 4, 16; row 14 demoted to method detail) ✅
- Unsupported novelty removed (rows 5, 8, 10 not claimed standalone) ✅
- No component-contribution claim ahead of the final ablation — all such slots marked
  `DEFERRED_TO_PHASE_12_SUPPLEMENT_ONLY`; main text frames mechanisms as proposed ✅
- Prohibited wordings honored (no "free" without the no-extra-objective-evaluations
  qualifier; no new-operator claim; NLPSR never claimed new) ✅
