# DT-GSK — Primary Thesis (Phase 4, task 4)

**Phase 4 deliverable (claim-freeze input to Gate 4).** Date: 2026-07-10.
Sources of record: `papers/build_prompt_phases/phase_03/contribution_matrix.md` (frozen),
`phase_03/PHASE_3_gate_report.md`, `phase_03/parameter_table.md`, `phase_03/complexity_analysis.md`,
`docs/algorithms/dt-gsk.md` (byte-stability-locked spec), `papers/governance/data_ledger.csv`,
`papers/build_prompt_phases/phase_04/terminology_glossary.md` (frozen names),
evidence release `rel-2026-07-10-262fc16c9` (read-only, `benchmarks/cec_reference_results/`).

**Numeric discipline (binding).** No empirical value (mean, rank, p-value, effect size,
CI bound, overhead ratio) is stated as fact in this document. All numeric slots are
exhibit-bound placeholders `<TXX:field>` / `<FXX:field>` to be bound in Phase 6 from
release `rel-2026-07-10-262fc16c9`. The only rank statements permitted are the
already-verified family-panel ranks in Section 5.1, and they are marked for Phase 6
re-derivation. This document mentions **no ablation results**; all component-contribution
claims are `DEFERRED_TO_PHASE_12_SUPPLEMENT_ONLY`.

---

## Thesis statement

Within the 7-algorithm GSK-family panel, DT-GSK — the unchanged gaining-sharing
operator core [mohamed2020gaining] augmented with (i) an interaction-structure memory
(ISM) that learns a decaying coordinate-pair interaction graph from *accepted* moves at
**no extra objective evaluations**, (ii) a deterministic eigenframe final polish on the
eigenbasis of that learned graph, and (iii) a dimension-tiered adaptive scaffold (ACE
bandit control, ARGP pruning, NLPSR floor, budget-safe BSE, global-best-preserving
deep-stall restart) — is expected to attain the leading family-panel rank position under
a budget-fair, reference-locked, byte-stable evaluation protocol, with a separation that
strengthens as dimension grows; every headline number is derived in Phase 6 exclusively
from evidence release `rel-2026-07-10-262fc16c9`, and no claim extends beyond the GSK
family panel.

## 1. Problem

Budget-fair, bound-constrained continuous minimization across dimension tiers, evaluated
**within the GSK family**: given a fixed evaluation budget MaxFES (CEC2017: 10^4·D at
D ∈ {10, 30, 50, 100} [awad2016problem]; CEC2011: 150,000 per problem at native
dimensions [das2011cec2011]), which GSK-family algorithm delivers the best error/fitness
under a paired, optimizer-independent seed schedule and shared initial populations
(DT-GSK self-init is the single documented exception, drawn from the same fair-start
stream)? The base operator family is the gaining-sharing knowledge algorithm
[mohamed2020gaining]; the comparators are its published adaptive descendants (AGSK
[mohamed2020agsk], APGSK [mohamed2021novel], FDB-AGSK [fdbagsk2023], eGSK
[jawad2024egsk], ATMALS-GSK [alfadli2025atmals]).

## 2. Bounded gap

GSK-family variants adapt **scalar control parameters and donor/selection policy** —
KF/KR pools by success history [mohamed2020agsk], extended parameter-adaptation pools
[mohamed2021novel], fitness-distance-balance donor selection [fdbagsk2023], dual
adaptive knowledge factors plus a late local polish [jawad2024egsk], memory-based pool
tuning with adaptive local search [alfadli2025atmals] — but **none learns or exploits
the interaction structure of the moves the run has already accepted**. Outside the
family, structure learning exists but at a different cost or mechanism: differential
grouping spends a dedicated, offline budget of objective evaluations (O(n²/m)) on
pairwise probing before optimization starts [omidvar2014dg]; covariance matrix
adaptation learns a full sampling covariance from selected steps and needs on the order
of n² evaluations of adaptation time for a significant shape change [hansen2001cmaes];
eigenvector-based crossover recomputes the population covariance eigenbasis every
generation at O(D³) compute cost to gain rotational invariance in DE [guo2015eig]. The
bounded gap DT-GSK addresses: **within the GSK operator style, exploit accepted-move
interaction structure at high dimension without spending any additional objective
evaluations and without replacing the base operator** — the structure signal is a
byproduct of moves the run already made.

## 3. Central mechanism

Primary pair (frozen contribution matrix rows 11–12, both original):

1. **Interaction-structure memory (ISM; code alias SGSM, `interaction_graph.py`).** A
   decaying (λ = 0.95) coordinate-pair interaction graph updated from accepted moves
   only; confidence- and evidence-gated; active at D ≥ 50 under the `pub` profile. It
   costs **no extra objective evaluations** (its compute cost is stated in
   `phase_03/complexity_analysis.md`). Exploited twice: it supplies the linkage blocks
   of the block crossover, and a top-k-block subspace to local search.
2. **Eigenframe final polish.** A one-shot, RNG-free deterministic compass search on the
   eigenbasis of the ISM signed interaction matrix in the final budget slice (coordinate
   axes when no graph signal); consumes budget through the strict accounting path and
   draws no RNG (byte-identical whether it fires or not).

Both ride on a **dimension-tiered adaptive scaffold** (secondary contribution, honestly
labeled modified/original composite): ACE — an EMA-credit multi-armed bandit over a
5-arm (KF, KR, Kexp) operator pool with a probability floor; ARGP — acceptance-rate
gated arm pruning; NLPSR — the tier-floored nonlinear population-size schedule (a
variant of the APGSK NLPSR schedule [apgsk2021], never
claimed as new); BSE — a triple-trigger, hard-capped budget-safe escape with an elite
archive [zhang2009jade, tanabe2013shade lineage]; and the deep-stall full restart with a
preserved global best (a restart can never lose ground). D ≥ 100 controllers (A1/A2/FC4,
basin memory, SP-NLPSR subspace floor, TERRA) are method-level protections, not headline
contributions. The gaining-sharing operator core, junior→senior schedule, greedy
selection, and midpoint bound repair are inherited unchanged [mohamed2020gaining,
tanabe2014improving] — **no new base operator is claimed**.

## 4. Primary evaluation design

- **Panel:** the 7-algorithm GSK-family panel — GSK, AGSK, APGSK, FDB-AGSK, eGSK,
  ATMALS-GSK, DT-GSK. All comparisons and superiority wording are scoped "within the
  GSK family panel"; never field-wide.
- **Primary suite:** CEC2017 [awad2016problem] — 29 functions (F1, F3–F30; F2 excluded
  per protocol), D ∈ {10, 30, 50, 100}, **51 runs**, MaxFES = 10^4·D, paired
  optimizer-independent seed schedule keyed (dim, func, run), shared runner-generated X0
  (DT-GSK self-init documented exception).
- **Secondary real-world suite:** CEC2011 [das2011cec2011] — **25 runs**, MaxFES
  150,000, problems at native dimensions.
- **Second comparison suite:** CEC2013 [liang2013cec2013] — never called "independent",
  "holdout", or "validation" in the main text (no development-history evidence of
  independence is on record).
- **Evidence lock:** every empirical number is derived in Phase 6 exclusively from the
  frozen, read-only evidence release `rel-2026-07-10-262fc16c9`
  (`benchmarks/cec_reference_results/`; provenance in `papers/governance/data_ledger.csv`).
  Staging data under `results/` is never citable.
- **Statistics (names frozen; parameters bound in the Phase 5 pre-registration):**
  Friedman mean ranks [friedman1937use] with Iman–Davenport correction; Nemenyi critical
  difference diagrams [demsar2006statistical]; per-function Wilcoxon signed-rank tests
  [wilcoxon1945individual] with Holm correction [holm1979simple]; Vargha–Delaney A12
  effect sizes [vargha2000critique]; BCa bootstrap confidence intervals
  [efron1993introduction]; win/tie/loss tallies.

## 5. Strongest expected claim TYPE

The strongest claim the manuscript will defend is a **family-panel rank-superiority
claim plus a scalability-trend claim** — never a field-wide superiority claim
[wolpert1997nfl bounds the honest scope of any such claim]:

- **Rank type:** "Within the 7-algorithm GSK-family panel on CEC2017, DT-GSK attains
  Friedman mean rank `<T05:friedman_rank_overall>` overall and
  `<T05:friedman_rank_D10>` / `<T05:friedman_rank_D30>` / `<T05:friedman_rank_D50>` /
  `<T05:friedman_rank_D100>` per dimension, with Nemenyi CD structure
  `<F01:cd_diagram_per_dim>`, Holm-corrected Wilcoxon outcomes
  `<T02:wilcoxon_holm_pairwise>`, and effect sizes `<T03:a12_cliffs_bca>`."
- **Scalability-trend type:** "DT-GSK's separation from the panel comparators changes
  with dimension as `<F03:rank_vs_dimension_trend>`" — a trend statement over the four
  CEC2017 tiers, plus real-world corroboration `<T04:cec2011_panel_results>` and second
  comparison suite behavior `<T06:cec2013_panel_results>`.

### 5.1 Permitted pre-Phase-6 rank statements (verified; to be re-derived)

The following already-verified family-panel rank statements from
`docs/algorithms/dt-gsk.md` are the ONLY ranks that may be repeated in planning
artifacts, and each is marked **to be re-derived in Phase 6 from release
rel-2026-07-10-262fc16c9**:

- CEC2017: DT-GSK is #1 in the family overall by both mean and median; #1 at D10, D50,
  and D100; #2 at D30 behind eGSK.
- CEC2011: DT-GSK places #2 in the family.

No other rank, mean, p-value, or effect size may be stated before Phase 6 binding.

## 6. Reproducibility

The claim set is defensible because the evidence pipeline is deterministic end-to-end:

- **Byte-stable determinism:** the 13-substream, append-only, prefix-locked RNG layer
  (`src/gsk_family/optimizers/_dt_rng.py`) child-seeds all subsystems from one run
  seed; toggling any subsystem cannot disturb the others' draw order. Locked by
  `tests/regression/test_dt_gsk_byte_stable.py`.
- **Profile lock:** the single paper-facing `pub` configuration is tier-resolved by
  `_dt_profiles.build_pub_config(dim)` and enforced by `validate_profile_lock.py` and
  `tests/unit/test_dt_profiles.py`; the algorithm and parameters are hash-frozen in
  `phase_03/algorithm_freeze_manifest.json` (Gate 3 APPROVED).
- **Seeded release:** every panel cell records its seed schedule, run config,
  environment, and SHA-256 checksums in the data ledger; runs are paired via the unified
  optimizer-independent seed schedule.
- **Promoted evidence:** staging results enter evidence only through the controlled
  promotion pipeline (`scripts/promote_evidence.py`), which mints a new release id; the
  manuscript binds exclusively to `rel-2026-07-10-262fc16c9`.
- **Verification path:** Phase 6 re-derives all headline statistics from the release and
  produces the dynamic high-D witnesses scheduled in the Phase 3 gate report (SGSM/
  polish D ≥ 50 trace; deep-stall D ≤ 30 trace).

## 7. Exclusions (binding)

- **No ablation content in the main manuscript.** Component-contribution evidence is
  `DEFERRED_TO_PHASE_12_SUPPLEMENT_ONLY`; the main-text outline contains no ablation
  subsection. Mechanisms are presented as *proposed* and *specified*, with causal
  attribution deferred to the Phase-12 supplement.
- **No field-wide claims, no theoretical convergence claims, no LSGO claims** — see
  `phase_04/novelty_scope.md` (non-claims register).
- **Venue context:** frozen target MDPI Algorithms; cover-letter venue conflict is risk
  R-0004, DEFERRED by user decision 2026-07-10 (referenced, not resolved).
