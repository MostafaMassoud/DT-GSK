# Stage 6 — Method, Theory, and Mathematical-Correctness Audit

**Seat:** `s6_method` (Stage 6; lead role R2; lead team T1-OPT, contributing T4-SOFT)
**Manuscript state audited:** git HEAD `45248eb31af7b01567c251f2a5da4f36e92d6030`; `papers/DT-GSK.pdf` (39 pp), `papers/supplementary.pdf` (61 pp), `papers/DT-GSK.docx`, `papers/supplementary.docx`
**Frozen code audited:** `src/gsk_family/optimizers/dt_gsk.py`, `_dt_core.py`, `_dt_profiles.py`, `_dt_rng.py`, `_dt_subsystems/*` — **byte-identity independently verified** against `papers/build_prompt_phases/phase_03/algorithm_freeze_manifest_2026-07-19.json` (SHA-256: `dt_gsk.py` 51b12194…, `_dt_core.py` dc2d59db…, `_dt_profiles.py` 7baadf22…, `_dt_rng.py` 8a0fc27d… — all four MATCH the working tree).
**Date:** 2026-07-22
**Governing sections applied:** §1.4 precedence (repo > prompt snapshot > prose), §5.1–5.4, §10.6, §10.11, §15, Stage 6 mandate (lines 1609–1686), Gate F.

---

## 0. Executive summary

Every printed equation E1a–E12 was recomputed symbolically against the byte-locked source, and the
main generation loop was walked line-by-line against Algorithm 1. **The equation registry itself is
now sound.** The R-01 correction (per-phase signs `s_J`/`s_S`) is faithful, complete, and rendered in
both the PDF and the DOCX; the R1-canonical SGSM EMA defect (`G←(1−λ)G+λΣ` vs. coded `G←λG+ηΣ`)
is genuinely fixed; and the R-04/R-05 budget and restart invariants hold exactly as stated.

The residual defects are **not in the equations** — they are in the *surrounding method
specification*, and they cluster on the one mechanism the manuscript is most exposed on: the
interaction-structure memory (ISM). Two are, in my judgement, blocking:

1. **A frozen, trajectory-determining parameter of the ISM's own exploitation channel is absent
   from the entire paper** (`interaction_linkage_mix_prob = 0.50`), and the prose that replaces it
   ("from `D≥50` the block structure is supplied by the ISM graph itself") **overstates the ISM's
   share of the crossover channel by 2×**. Measured at D=50: learned blocks drive **50.4 %** of
   blockwise rows in graph-ready generations and **14.1 %** of all population-rows over a run.
2. **The supplement asserts the coordinate local search is admitted by the ISM confidence gate
   κ=0.45.** It is not — that gate lives exclusively inside the *dormant* subspace branch. This both
   misstates an active mechanism and contradicts the main text's own "two active channels" claim.

Three further Moderate defects (ISM decay/refresh cadence bypass, Algorithm 1's misplacement of all
five upper-tier controllers, archive capacity) plus a set of Minor notation/traceability items are
listed below. None of them changes a reported number; all of them are correctable by text edit
alone, with **no rerun and no new evidence release**.

**Gate F recommendation: CONDITIONAL PASS — blocked on M6-01 and M6-02.**
Both are text-only fixes against the frozen code. Once corrected and re-verified, Gate F passes.

---

## 1. Verification of the 2026-07-21/22 remediation (R-01 … R-14)

I was asked to confirm these closed correctly and to report any that closed incompletely.

| Ticket | Verdict | Evidence |
|---|---|---|
| **R-01** Eq.(4) per-phase signs | **CLOSED, correct** | `equations.tex:47–61` prints `s_J` (junior, vs `x_R3`) and `s_S` (senior, vs `x_R2`) *inside the numbered display*, plus rendered explanatory text. Recomputed against `_numba_accel.py:403–415`: junior `f(x_i)>f(x_R3)` → `+(x_R3−x_i)`, else `+(x_i−x_R3)`; senior `f(x_i)>f(x_R2)` → `+(x_R2−x_i)`, else `+(x_i−x_R2)`. Exact-tie → `−1` (strict `>`), matching the paper's parenthetical. Notation row present (`notation_table.tex`, `s_J,s_S`). Rendered in PDF p.9 Eq.(4) and in `DT-GSK.docx` (OMML, tokens `sJ`/`sS` present). |
| **R-02** registry drift E3/E4/E8 | **CLOSED, INCOMPLETE** | E3/E4/E8 corrected in `equation_registry.csv`. **But E9 still names `r_rst` where code and rendered Eq.(10) use `r_c`** (0.30 vs 0.10 at D<50) — see M6-09. **And `implementation_correspondence.md` row E8 still says the greedy accept is "strictly `<`"** — see M6-06. |
| **R-03** DOCX OMML literal `&` | **CLOSED, correct** | `DT-GSK.docx`: 753 `<m:oMath>`, **0** `<m:t>` runs containing `&amp;`. `supplementary.docx`: 640 / **0**. |
| **R-04** restart invariant | **CLOSED, correct** | Deep-stall resamples all `min(NP, remaining)` rows uniformly (`_dt_core.py:4721–4726`), i.e. the working population *can* worsen; `global_best_(x,f)` is updated at `:4700–4703` and restored at return `:5141–5143`. All other subsystems verified elitist (`improved = child_fit <= fitness` :3362; Cauchy `kept iff ≤` :3944; LS `y_new <= f_old` :4551; polish `< f_best` :1950). |
| **R-05** budget-crossing semantics | **CLOSED, correct** | DT-GSK uses `eval_batch_strict`/`eval_batch_safe` (truncate *before* evaluating, `budget.py:193–239`); the MATLAB-faithful ports use `eval_batch_matlab` (`:241–279`, full batch, prefix charged). Disclosure at `performance.tex:165–175`. `tests/regression/test_budget_crossing_semantics.py` — **14 passed** (re-run 2026-07-22). |
| **R-06** supplement release identity | **CLOSED, correct** | `papers/scripts/validate_provenance_claims.py` → `[provenance] OK`, exit 0; supplement S5.2 cites `rel-2026-07-20-67d9345f9` / anchor `67d9345f9502…`. |
| **R-07** provenance validator hardening | **CLOSED, with a scope gap** | Validator is green and self-tests. **However `FREEZE` at `validate_provenance_claims.py:45` points only at the *superseded* `algorithm_freeze_manifest.json`; the current `algorithm_freeze_manifest_2026-07-19.json` is never read by this gate.** It passes because Rule B recomputes live hashes from the source files, so the result is correct — but the current freeze manifest is not itself machine-checked here. Recorded as M6-11 (advisory part). |
| **R-08** ISM not a fourth contribution | **CLOSED, correct** | `introduction.tex:84–135` — C1/C2/C3 only; ISM explicitly "a secondary exploratory mechanism". |
| **R-09** cover letter | **CLOSED** (out of my lane; no reviewer placeholder found in `cover_letter.tex`) | |
| **R-10 … R-13** | **CLOSED** in my lane: per-coordinate bounds notation is consistent (`proposed_algorithm.tex:51–56`; `tab:notation` row `[ℓ,u]^D`; Eq.(8) uses `ℓ_j,u_j`). | |
| **R-14** budget-crossing probe | **CLOSED, correct** | Test present, runs, and proves the uncounted terminal rows are inert (poisoning with 1e300 leaves `best_fitness`, `nfes`, `best_x` bit-identical). |

---

## 2. Equation and notation issue table

All twelve registry equations recomputed against source. `OK` = printed rule reproduces the frozen
operator exactly.

| Eq. | Printed as | Code anchor (verified) | Verdict |
|---|---|---|---|
| (1) E1a junior indices | `R1=rank(r_i−1), R2=rank(r_i+1), R3~U(P\{i,R1,R2})` | `gained_shared_junior.py:56–112` | **OK for the interior**; boundary rows unspecified (M6-15); `rank(·)` used as its own inverse and `r_i` undefined (M6-08) |
| (2) E1b senior indices | groups of `round(p·NP)` | `gained_shared_senior.py:59–129` | OK (round-away-from-zero + `n_grp≥1`, `2n_grp<NP` clamps unstated — Minor); split-senior (two `p` values at `D≥50`) not representable in (2), disclosed in Supp. S5 |
| (3) E2 junior-dim schedule | `D_jun=⌈D(1−x)^Kexp⌉` | `_dt_core.py:2941–2942` (`progress = 1−frac_used`, `:2750`) | **OK**, but applied as a per-coordinate Bernoulli (M6-14); `K_exp` is per-individual from the ACE arm (`:2919`), not the single scalar the display implies |
| (4) E3 gaining–sharing update | `s_J`/`s_S` per phase | `_numba_accel.py:403–415`, `:456–470` | **OK — R-01 verified faithful** |
| (5) E4 crossover mask | `Bernoulli(KR)` or block-shared | `_dt_core.py:918–933` (`_make_linkage_groups`), `:1017–1161` (`_build_phase4_masks`) | OK as far as it goes; the *two-stage* junior/senior + KR composition and the force-nonzero guarantee are main-text-silent (both in Supp. S5) |
| (6) E5 NLPSR | `round_½↑(NP_init+(N_min−NP_init)x^(1−x))` | `_dt_core.py:830–846`; `_numba_accel.py:930–937` | **OK.** Table 5 worked example independently recomputed: 250/222/170/91/41/27/25 and `D_jun` 50/18/3/1/1/1/0 — **all seven rows correct** |
| (7) E6 ACE update | three-branch τ; Euclidean simplex projection `P` | `_dt_core.py:1204–1266`; `_numba_accel.py:868–899` | **OK** under the stated `d=−ω, S=−s` convention, incl. the `S=0`/non-finite hold branch and the project-before-mix-then-project order. `ace_coverage_weighted=False` in the frozen profile, so `d_m` is the plain sum as printed |
| (8) E7 midpoint repair | `(x+bound)/2` | `bound_constraint.py` | OK (used by trials, DE, BSE, LS) — **but not by the polish**, which hard-clips (M6-12) |
| (9) E8 greedy accept | `≤`, ties accepted; `D≥100` clip note | `_dt_core.py:3362`, `:3373–3383` | **OK.** Note: the `D≥100` clip is correctly localized *here* by the equation, which is what makes Algorithm 1 step 19 wrong (M6-04) |
| (10) E9 BSE Cauchy | `γ=r_s(u−ℓ)/√D`, worst `round(r_c NP)` unfrozen rows, kept iff `≤` | `_dt_core.py:3928–3948` | **OK.** `max(1,·)` and the budget/pool clamps are unstated (Minor); "unfrozen" is undefined in the main text |
| (11) E10 ISM EMA | `G_• ← λG_• + η Σ_{i∈I⁺} w_i φ(δ̂)φ(δ̂)ᵀ` | `interaction_graph.py:201` (`matrix *= decay`), `:344` (`matrix += lr*agg`) | **OK — the R1 canonical defect is genuinely fixed.** Retention on the *old* graph, independent `η`, no parameter collapse. `w_i` and `I⁺` undefined in the main text (M6-08); the LS-path second call breaks the "each update" reading (M6-03) |
| (12) E11 eigenframe polish | `x*←CompassSearch(x*, V=eig(G_signed))` | `_dt_core.py:1889–1911`, `:1915–1974` | OK as a summary; ordering, step schedule, cap and clipping are supplement-only / undisclosed (M6-12) |
| (13) E12 RNG substreams | `s_k=(seed+1 000 003(k+1)) mod M + 1` | `_dt_rng.py:178–188` (`MAX_SAFE_SEED = 2 147 483 646`), `:193–207` | **OK.** `M` is defined only in Supp. S5 (M6-08) |

---

## 3. Method-completeness table (Stage 6 general audit)

| Required item | Status | Note |
|---|---|---|
| Problem, objective, applicability | **Complete** | `proposed_algorithm.tex:51–56`; per-coordinate bounds handled |
| Variables/symbols/domains | **Mostly complete** | 4 undefined symbols in printed equations — M6-08 |
| Inputs/outputs/initialization/update order/stopping | **Complete** | Algorithm 1 + §3.2 execution list; self-init exception disclosed (`:788–793`) |
| All parameters, defaults, ranges | **INCOMPLETE** | `interaction_linkage_mix_prob=0.50`, `interaction_restart_decay=0.50`, `interaction_post_restart_cooldown=5` appear nowhere — M6-01 |
| Boundary / tie / failure handling | **Mostly complete** | ties (`≤`) explicit; junior rank-boundary rule missing (M6-15) |
| Computational resources & complexity | **Complete and correct** | §3.8 — see §5 below |
| Numerical safeguards / degenerate cases | Complete | edge floors, `1e-10`/`1e-12` guards, `ig_ready` minimums |
| Reproducibility-relevant randomness | **Complete** | 13 substreams, prefix-locked, Eq.(13); polish RNG-free claim verified |
| External dependencies | Complete | SciPy only in the *dormant* NM branch and the eGSK port — correctly disclosed |
| Inherited vs. modified vs. original | **Complete and honest** | `tab:architecture` category column; §3.1 "only relaxation is `≤`" verified |

---

## 4. Pseudocode / code mismatch table

Loop order in `_dt_core.py` (`while not budget.exhausted():` at `:2708`) vs. Algorithm 1:

| Alg. 1 step | Code | Match |
|---|---|---|
| 6 NLPSR reduce | `:2752–2795` (cull worst surplus by fitness) | ✔ |
| 7 ACE arm assignment | `:2876–2926` | ✔ |
| 8 gained/shared dim count | `:2941–2945` | ✔ |
| 9/10 junior & senior phases | `:3098–3160` | ✔ |
| 11 crossover mask | `:3205–3236` | ✔ |
| 12 bound repair | fused into `:3098` | ✔ |
| 13 evaluate maximal fitting prefix | `:3356` + `improved[n_child:]=False` `:3363` | ✔ (exactly as the step's comment claims) |
| 14 greedy keep + archive | `:3362`, `:3459–3460` | ✔ |
| 15 `D≥50` ISM update | `:3502–3508` | ✔ position (after selection, before ACE credit) |
| 16 ACE credit + ARGP | `:3653–3716`, `:3720+` | ✔ |
| 17 BSE | `:3862–4084` | ✔ |
| 18 coordinate LS | `:4086–4585` | ✔ |
| **19 `D≥100` upper-tier controllers** | **scattered: `:3373–3383`, `:3641–3651`+`:2935`, `:3024–3038`, `:3465`+`:3993–4012`, `:2767`** | **✘ — M6-04** |
| 20 `D≥50` one-shot polish | `:4590–4644` | ✔ |
| 21 global-best update | `:4700–4703` | ✔ |
| 22 deep-stall restart | `:4704–4737` | ✔ |
| — (unlisted) LS-derived ISM update + block re-extraction | `:4646–4670` | **✘ — M6-03** (occurs *after* the polish, undecayed, off-cadence) |
| — (unlisted) ISM restart decay + block re-extraction | `:4070–4077` | **✘ — M6-01/M6-03** (undisclosed `interaction_restart_decay=0.50`, `post_restart_cooldown=5`) |
| 1 "Initialize `G_abs,G_signed ← 0`" | allocated only at `D≥50` | Minor: step 1 is unconditional in the listing |

---

## 5. Complexity and evaluation-accounting assessment

**Evaluation accounting — sound, and I could not break it.**
Every objective call in DT-GSK routes through one `BudgetController`: `_dt_core.py:1960` (polish),
`:2117`/`:2128` (init), `:3356` (trials), `:3940` (Cauchy), `:4018` (BSE reseed), `:4309`/`:4427`
(NM branch, dormant), `:4539` (coordinate LS), `:4723` (deep-stall). There is **no direct objective
call anywhere** in the DT-GSK path. `_consume` raises `BudgetExhausted` on any over-charge
(`budget.py:128–132`), so "MaxFES-exact by construction" is enforced, not asserted. The Section-3.8
claim, the Algorithm-1 step-13 wording, and the `performance.tex:165–175` comparator disclosure all
agree with the code and with the passing regression probe.

**Complexity — analytically correct and appropriately hedged.**
- ACE `O(NP+M)`, ARGP `O(M·W_argp)`: correct to within `log` factors from the `M≤6` simplex sort and the `searchsorted` — not worth a ticket.
- ISM `O(D²)` decay + `O(k·D²)` accumulation, `k≤NP`: verified; §3.8's tighter `O(|J|²)` per-move statement is the more accurate one and is present.
- Polish `O(D³)` once per run: `np.linalg.eigh` on `(D,D)`, `_dt_core.py:1907`. ✔
- Memory: population family `Θ(NP·D)` with `NP_init=5D` → ≈3.6 MB float64 at D=100 ("a few megabytes" ✔); ISM state 3×`D²` persistent + 3×`D²` scratch + `O(D)` ≈ 0.5 MB at D=100 ("about half a megabyte" ✔).
- "We claim no complexity improvement over GSK" — correctly stated; analytical complexity and measured wall-clock are kept separate.

---

## 6. Reimplementation blockers

Answering the Stage-6 question directly — *could a competent independent expert reimplement DT-GSK
from the paper alone?*

**Almost. Two hard blockers and one soft one remain.**

- **BLOCKER 1 (M6-01).** `interaction_linkage_mix_prob = 0.50` is unobtainable from the paper, and the prose actively misdirects (implies 1.0). A reimplementer builds a different algorithm at `D≥50` — the tier where C1 and the ISM both live.
- **BLOCKER 2 (M6-01).** `interaction_restart_decay = 0.50` and `interaction_post_restart_cooldown = 5` are unobtainable. They fire on every BSE restart at `D≥50`.
- **SOFT (M6-03/M6-12).** The LS-derived ISM update path (undecayed, unconditional block re-extraction) and the polish's hard-clip bounding and eval cap are either absent or contradicted.

Everything else *is* recoverable: the supplement's "Complete Operator Specification" (S5) is
genuinely thorough — the full 5-arm ACE table with initial probabilities, the two-stage mask, the
force-nonzero guarantee, the KR floor, the BSE stop fraction and module gate, the elite freeze, the
compass step schedule and eigenvector ordering, the confidence functional `κ(G)`, the block
extraction rule, the RNG modulus. Credit where due: this is a materially better method
specification than most papers in this literature. The blockers above are the exceptions that
falsify S5's own opening claim that "Every value is transcribed from the hash-frozen sources".

---

## 7. Tickets (§5.4 schema), ranked by severity

### M6-01 — ISM linkage share: undisclosed frozen parameters + 2× overstated ISM channel

```text
ticket_id: M6-01
review_stage: Stage 6 — Method and theory
reviewer_role: R2 (T1-OPT)
severity: Major
priority: P1
confidence: Confirmed
issue_type: method
manuscript_location: papers/sections/proposed_algorithm.tex:515-518 ("from D>=50 the block
  structure is supplied by the ISM graph itself"); :142 (tab:architecture row 3, "ISM-fed blocks at
  D>=50"); :243 (tab:dim-gating, "mix 0.70/0.40/0.70/0.70; ISM-fed blocks at D>=50");
  papers/build_prompt_phases/phase_03/parameter_table_detail.tex:36; papers/supplementary.tex:1370
  ("Complete Operator Specification ... Every value is transcribed from the hash-frozen sources")
claim_id_or_artifact_id: MT-08 / ART-PARAMS / tab:sgsm-mechanism
concise_issue: A frozen parameter that governs how much of the crossover channel the ISM actually
  drives (interaction_linkage_mix_prob = 0.50) appears nowhere in the main text, either parameter
  table, or the supplement's complete operator specification; the prose that stands in its place
  states or implies that the ISM supplies the block structure outright at D>=50.
exact_evidence_or_observation:
  - src/gsk_family/optimizers/_dt_profiles.py:131  interaction_linkage_mix_prob=0.50
  - src/gsk_family/optimizers/_dt_core.py:343       default 0.50
  - src/gsk_family/optimizers/_dt_core.py:3013-3018 when learned groups are admitted, the LEARNED
    groups become `linkage_groups` and the RANDOM permutation groups become
    `linkage_groups_secondary`, with `linkage_primary_row_prob = interaction_linkage_mix_prob`
    deciding, per row, which of the two is used.
  - Measured (instrumented D=50 run, seed 20240620, MaxFES=30000, pub profile, generation_callback
    reading linkage_learned_rows / linkage_random_rows):
        blockwise rows / all rows          = 0.701   (matches the published 0.70)
        learned rows / blockwise rows      = 0.504   (the UNPUBLISHED 0.50)
        learned rows / all rows (whole run)= 0.141
        graph-ready generations            = 100 of 438
  - Two further frozen ISM constants are equally absent from every reader-facing surface:
        interaction_restart_decay = 0.50           (_dt_profiles.py:140; applied at _dt_core.py:4070
                                                    — the graph is HALVED on every BSE restart)
        interaction_post_restart_cooldown = 5      (_dt_profiles.py:139; applied at :4071-4074,
                                                    :2964 — learned blocks suppressed for 5 gens)
    grep of papers/supplementary.tex and papers/sections/*.tex returns zero hits for either.
root_cause: The parameter-table split (N-013) moved per-subsystem constants to the supplement, and
  the ISM row of the supplement table lists decay / lr / refresh / gate / block-size but not the
  learned-vs-random row mix or the restart-decay pair. The main-text prose was written from the
  "ISM-fed blocks" architecture label rather than from the resolved profile.
scientific_or_editorial_justification: §10.6 requires that for every load-bearing mechanism the
  review verify "existence, status, exact behavior, parameters, purpose, cost". §10.11 and the
  supplement's own S5 opening promise a complete transcription. A missing parameter that halves the
  mechanism's realized exploitation share is exactly the "silently collapsed / mis-specified
  operator" failure mode Gate F is written to catch.
impact_on_validity_or_acceptance: (a) Non-reimplementable at D>=50 — the tier carrying C1 and the
  ISM. (b) It inflates the reader's estimate of the ISM's role by 2x at precisely the point where
  the paper is defending an honest ISM null (S6.5). A reviewer who reads "the block structure is
  supplied by the ISM graph itself" and then finds the null is entitled to ask why a channel that
  strong shows no effect; the true answer — it drives half of 70 % of rows, only in graph-ready
  generations — is materially more consistent with the null and *helps* the paper.
required_correction:
  1. Add `interaction_linkage_mix_prob` (0.50), `interaction_restart_decay` (0.50) and
     `interaction_post_restart_cooldown` (5) to tab:parameters-detail, ISM block.
  2. Rewrite proposed_algorithm.tex:515-518 to, e.g.: "from D>=50 the ISM graph supplies candidate
     blocks for about half of the blockwise rows (mix 0.50), the remainder keeping the random
     permutation-chunk blocks, with block size 10; learned blocks are used only while the graph
     passes the confidence gate."
  3. Amend tab:architecture row 3 and tab:dim-gating to read "ISM-fed blocks on ~50 % of blockwise
     rows at D>=50" rather than the unqualified "ISM-fed blocks at D>=50".
acceptable_alternatives: State the two mix probabilities as a single composite ("about 35 % of the
  population takes an ISM-derived block in graph-ready generations"), provided the underlying
  constants still appear in the parameter table.
additional_evidence_needed: None. Text-only; no rerun; the frozen code and release are unaffected.
dependencies: Cross-check with the Stage-13 exhibit seat (tab:sgsm-mechanism row 3 carries the same
  "magnitude-graph linkage blocks -> block crossover mask" phrasing) and with the Stage-9/10 seats
  that read the S6.5 ISM null.
expected_improvement: Restores reimplementability at D>=50 and aligns the ISM's advertised reach
  with the evidence; strengthens rather than weakens the null's interpretation.
post_revision_verification: (i) grep the rendered PDF + DOCX for the three constants; (ii) confirm
  no surviving sentence asserts unqualified ISM-supplied blocks; (iii) re-run the instrumented
  D=50 measurement and confirm the printed share matches.
status: open
```

### M6-02 — Supplement attributes an ISM confidence gate to the coordinate local search that does not gate it

```text
ticket_id: M6-02
review_stage: Stage 6 — Method and theory
reviewer_role: R2 (T1-OPT)
severity: Moderate
priority: P2
confidence: Confirmed
issue_type: method
manuscript_location: papers/supplementary.tex:1648-1652 ("Charged coordinate local search ... it is
  admitted by the joint of a time gate ..., an evaluation-budget cap ..., a call period, a
  post-search cooldown, and the local-search confidence gate kappa = 0.45")
claim_id_or_artifact_id: ART-PARAMS / MT-09
concise_issue: The kappa=0.45 ISM confidence gate is not part of the coordinate local search's
  admission. It is evaluated only inside the subspace-Nelder-Mead branch, which the paper itself
  states is implemented but not enabled.
exact_evidence_or_observation:
  - Admission gates for the LS actually are: _dt_core.py:4111-4129 (_ls_time_gate, _ls_budget_gate,
    _ls_period_gate, _ls_restart_gate, _ls_cooldown_gate, _ls_event_gate). No ISM term.
  - The kappa gate is at _dt_core.py:4205-4227 (`ig_adaptive_threshold` -> `ig_ready`), which sits
    INSIDE `if ls_budget_rem > 0 and _ls_code_gen == 0:  # subspace_nm` (:4181). The shipped path is
    the sibling `elif ls_budget_rem > 0 and local_search_step_scale > 0.0:` at :4495.
  - _ls_code_gen is -1 for the frozen config: `local_search_method="coordinate"` maps to -1 at
    :2475, and `local_search_auto_subspace=False` at every tier (verified via build_pub_config for
    D=10/30/50/100), so the :4181 branch is unreachable.
root_cause: The S5 paragraph was written from the config key `interaction_ls_confidence_min = 0.45`
  without tracing which branch consumes it — the same class of defect ISM-C001 fixed in the main
  text, left behind in the supplement.
scientific_or_editorial_justification: It misstates the admission condition of an ACTIVE mechanism,
  and it contradicts the main text, which states the ISM has exactly two active exploitation
  channels (proposed_algorithm.tex:501-505, 519-524) — if the coordinate LS were ISM-gated, the ISM
  would have a third consumer.
impact_on_validity_or_acceptance: No reported number changes, but a reviewer who checks the code
  finds a method/implementation contradiction in the section whose stated purpose is "so that
  DT-GSK is reproducible from the text" (supplementary.tex:1372-1374). It also re-opens the
  ISM-C001 wound the project already closed.
required_correction: Delete "and the local-search confidence gate kappa = 0.45" from the coordinate
  LS gate list; if the constant is worth listing, list it in tab:parameters-detail against the
  dormant subspace variant, as the eigen-polish/linkage gates are.
acceptable_alternatives: Reword to "(the 0.45 local-search confidence gate belongs to the
  implemented-but-disabled ISM-subspace variant and is inert in the shipped configuration)".
additional_evidence_needed: None.
dependencies: Consistency with proposed_algorithm.tex:144, :245, :519-524 and tab:sgsm-mechanism.
expected_improvement: Removes an internal contradiction and a code mismatch in the reproducibility
  section.
post_revision_verification: grep supplementary.tex for "0.45" and confirm every remaining occurrence
  is attributed to the dormant subspace path; re-read the LS paragraph against _dt_core.py:4111-4129.
status: open
```

### M6-03 — Local-search-derived ISM updates bypass both the decay and the block-refresh cadence

```text
ticket_id: M6-03
review_stage: Stage 6 — Method and theory
reviewer_role: R2 (T1-OPT)
severity: Moderate
priority: P2
confidence: Confirmed
issue_type: method
manuscript_location: papers/sections/proposed_algorithm.tex:455-460 ("updated only from
  strictly-improving accepted-move deltas at learning rate eta=1.0, with the retained graph decayed
  by lambda=0.95 at each update"); :474-477 ("The graph is updated every generation and its linkage
  blocks are re-extracted every 5 generations --- at D>=100, every 10 and 20 generations
  respectively"); papers/supplementary.tex:1476-1498 (S5 interaction-graph update)
claim_id_or_artifact_id: E10 / eq:sgsm-graph / MT-08
concise_issue: Local-search-derived accepted moves feed the ISM through a SECOND call made after the
  final polish with decay=1.0 (no decay at all) and an UNCONDITIONAL block re-extraction, so neither
  "decayed by lambda at each update" nor "blocks re-extracted every 5 generations" is true. A third
  off-cadence re-extraction fires on every BSE restart.
exact_evidence_or_observation:
  - src/gsk_family/optimizers/_dt_core.py:4646-4670 — `ig_update_from_accepted(..., decay=1.0, ...)`
    at :4658, followed by an unguarded `ig_extract_blocks(...)` at :4664 (guarded only by
    `interaction_state.updates > 0`, with no `gen % refresh_period` test).
  - src/gsk_family/optimizers/_dt_core.py:4070-4077 — `ig_apply_restart_decay(factor=0.50)` then a
    second unguarded `ig_extract_blocks` on a BSE restart.
  - The on-cadence path is :3502-3527 (`_do_sgsm_update = gen % interaction_update_period == 0`;
    refresh guarded by `gen % _v4_eff_refresh_period == 0`).
  - Measured (instrumented D=50 run, seed 20240620, MaxFES=30000, pub profile; counters wrapped
    around C.ig_update_from_accepted / C.ig_extract_blocks):
        ig_update_from_accepted calls: decay=0.95 -> 427 ; decay=1.00 -> 42
        ig_extract_blocks calls: 128; inter-call generation gaps observed = {0,1,2,3,4,5};
        77 of 127 gaps are < 5 generations; 8 gaps are 0 (two extractions in one generation).
root_cause: The LS-ISM feed was added as a tail-of-generation pass rather than folded into the
  single per-generation update, and the block-refresh guard was not replicated on the two secondary
  call sites.
scientific_or_editorial_justification: Stage 6 requires one-to-one correspondence among equation,
  pseudocode, prose and code, including cadence. Eq.(11) is presented as THE update rule; a second
  undecayed application of the same rule is a different operator.
impact_on_validity_or_acceptance: No reported number changes (the frozen runs used this code), but a
  reimplementation from the paper produces a differently-weighted graph and a differently-refreshed
  block set. The supplement's own D>=100 amortization argument ("evidence is injected only every
  tenth [generation] ... effective decay lambda^10") is falsified in the endgame, where the LS
  injects undecayed evidence every other generation.
required_correction: State it once, in S5: "local-search-derived accepted moves are folded in at the
  end of the generation as an additional, undecayed accumulation at source weight 0.25, and both
  that path and a BSE restart trigger an immediate block re-extraction outside the normal refresh
  period." Add `interaction_restart_decay` (0.50) at the same place (see M6-01).
acceptable_alternatives: Weaken the main-text sentences to "the graph is decayed once per generation
  and blocks are re-extracted at least every 5 generations (10/20 at D>=100), and immediately after a
  local-search improvement or a restart".
additional_evidence_needed: None; the measurement above is reproducible in ~60 s.
dependencies: M6-01 (same ISM parameter block).
expected_improvement: Makes the ISM update rule reimplementable exactly.
post_revision_verification: Re-run the instrumented counter and confirm the observed gap
  distribution matches the printed cadence description.
status: open
```

### M6-04 — Algorithm 1 places all five upper-tier controllers where none of them acts

```text
ticket_id: M6-04
review_stage: Stage 6 — Method and theory
reviewer_role: R2 (T1-OPT)
severity: Moderate
priority: P2
confidence: Confirmed
issue_type: method
manuscript_location: papers/build_prompt_phases/phase_03/algorithm_pseudocode.tex:59 (Algorithm 1
  step 19: "if D>=100: apply the upper-tier controllers", placed between the local search and the
  polish); papers/sections/proposed_algorithm.tex:198 (execution-order item 10)
claim_id_or_artifact_id: ART-PSEUDOCODE / alg:dt-gsk
concise_issue: The five D>=100 controllers are shown as one loop step at one position. In the frozen
  code they act at five different points of the generation, none of which is that position — and one
  of them (the late-acceptance clip) modifies the greedy-selection step that Algorithm 1 has already
  executed six lines earlier.
exact_evidence_or_observation:
  - late-acceptance clip: _dt_core.py:3373-3383 — replaces `improved` INSIDE the selection block
    (step 14), i.e. five steps before step 19.
  - frozen-streak broaden: decision at :3641-3651 (end-of-generation), applied to KR_i at :2935
    (next generation's ACE parameter block, before step 11).
  - late linkage random-mix (FC4): :3024-3038, inside the linkage-group dispatch that precedes the
    mask build (step 11).
  - basin memory: written at acceptance :3465, consumed in the BSE reseed :3993-4012 (step 17).
  - SP-NLPSR subspace-sampling floor: :2759-2767, inside the NLPSR block (step 6).
  The paper is also internally inconsistent: the note attached to Eq.(9) (equations.tex:132-136)
  correctly localizes the clip to the acceptance rule.
root_cause: The controllers were bundled under one §3.6 heading and the pseudocode mirrored the
  heading rather than the loop.
scientific_or_editorial_justification: §10.17.6 requires the listing to preserve "exact algorithmic
  behaviour, step order (faithful to the code, §10.6)". A reader reimplementing at D=100 from
  Algorithm 1 applies the acceptance clip after the local search and therefore accepts a different
  trial set.
impact_on_validity_or_acceptance: D=100 is one of four reported dimensions and the tier where the
  paper's rank advantage is largest; an incorrect loop position there is a fair reviewer objection.
required_correction: Replace step 19 with in-place annotations: mark step 14 "(at D>=100 the
  late-acceptance clip may tighten this to a strict relative decrease)"; mark step 6 "(at D>=100 the
  subspace-sampling floor may raise N_min)"; mark step 11 "(at D>=100 a late linkage random-mix may
  redirect learned-block rows)"; keep basin memory with the acceptance/archive step and the
  frozen-broaden with the end-of-generation bookkeeping. Delete the standalone step 19 and renumber
  the §3.2 execution list to match.
acceptable_alternatives: Retain step 19 but caption it explicitly as a grouping label, and add one
  sentence in §3.6 giving each controller's actual insertion point.
additional_evidence_needed: None.
dependencies: The flowchart fig:dtgsk-flowchart must be re-checked for the same placement; Stage 13
  exhibit seat.
expected_improvement: Algorithm 1 becomes a faithful loop specification at every tier.
post_revision_verification: Re-walk one generation of _dt_core.py against the revised listing at
  D=100 and confirm every annotated step matches its code line.
status: open
```

### M6-05 — Diversity-archive capacity misstated (flat 200, not 1.5·NP_init)

```text
ticket_id: M6-05
review_stage: Stage 6 — Method and theory
reviewer_role: R2 (T1-OPT)
severity: Moderate
priority: P2
confidence: Confirmed
issue_type: method
manuscript_location: papers/sections/proposed_algorithm.tex:396-401 ("once the store is full
  (|A| ~ 1.5 NP_init, hard-capped at 200)"); papers/build_prompt_phases/phase_03/
  parameter_table_detail.tex:47 ("archive size / distance | 1.5 NP_init, L2 0.05, cap 200");
  tab:notation-scaffold row A ("|A| ~ 1.5 NP_init")
claim_id_or_artifact_id: ART-PARAMS / MT-06
concise_issue: `arch_size_mult = 1.5` never takes effect. The construction short-circuits on
  `arch_max_size`, which is 200 and is never None, so the archive capacity is a flat 200 at every
  dimension.
exact_evidence_or_observation:
  - src/gsk_family/optimizers/_dt_core.py:2276-2286:
        if config.arch_max_size is not None:
            max_size = int(config.arch_max_size)
        else:
            max_size = int(_round_half_up(float(config.arch_size_mult) * float(NP_init)))
  - src/gsk_family/optimizers/_dt_core.py:306-308: arch_size_mult=1.5, arch_max_size=200 (not
    overridden in any tier of _dt_profiles.py).
  - Resolved via build_pub_config: D=10 -> NP_init 50, 1.5*NP_init = 75, effective cap = 200;
    D=30 -> 225 vs 200; D=50 -> 375 vs 200; D=100 -> 750 vs 200.
  - So the printed rule is wrong wherever 1.5*NP_init < 200, i.e. D < ~133: CEC2017/CEC2013 D=10
    (75 vs 200, a 2.7x understatement) and the majority of the CEC2011 problem dimensions.
  - The module docstring at :1675 compounds this with a third, also-wrong value ("arch_size_mult
    (default 5.0)").
root_cause: The parameter table was transcribed from the two config fields without tracing the
  precedence between them.
scientific_or_editorial_justification: §10.6 requires exact behaviour and parameters for the archive
  logic; §10.11 forbids parameter values that do not resolve to the frozen configuration.
impact_on_validity_or_acceptance: A reimplementer at D=10 builds an archive under half the true
  capacity, changing BSE reseed diversity. No reported number changes.
required_correction: State "|A| = 200 at every dimension (a size multiplier of 1.5*NP_init is
  configurable but is superseded by the hard cap in the shipped configuration)" in
  proposed_algorithm.tex:396-401, tab:parameters-detail:47 and tab:notation-scaffold.
acceptable_alternatives: "min(round(1.5 NP_init), 200), which resolves to 200 at every shipped
  dimension" is NOT acceptable — it is false at D=10.
additional_evidence_needed: None.
dependencies: None.
expected_improvement: Correct archive specification at every tier.
post_revision_verification: build_pub_config(D).arch_max_size for D in {10,30,50,100} against the
  printed value.
status: open
```

### M6-06 — Phase-3 correspondence artifact still says the greedy accept is "strictly <", and Gate 3's PASS row cites superseded hashes

```text
ticket_id: M6-06
review_stage: Stage 6 — Method and theory
reviewer_role: R2 (T1-OPT)
severity: Moderate
priority: P2
confidence: Confirmed
issue_type: reproducibility
manuscript_location: papers/build_prompt_phases/phase_03/implementation_correspondence.md, row E8
  ("| E8 | greedy accept | `dt_gsk_optimize:1974` accept block | strictly `<` |");
  papers/governance/phase_gate_register.csv row 5 (Gate 3)
claim_id_or_artifact_id: Gate 3 evidence / E8 / eq:greedy-accept
concise_issue: The governance artifact that Gate 3 cites as proof that "code/config/equations/
  pseudocode/trace agree" states the opposite of the frozen code and of the corrected Eq.(9): it
  records the acceptance rule as strict `<` when the code is `<=` with ties accepted. The same Gate 3
  row also pins the four superseded pre-rename source hashes.
exact_evidence_or_observation:
  - Code: _dt_core.py:3362 `improved = child_fit <= fitness`.
  - Paper: equations.tex:137-140 prints `iff f(v_i) <= f(x_i)`; proposed_algorithm.tex:79-87 says
    "a child replaces its parent if it is no worse (<=; ties accepted)".
  - implementation_correspondence.md E8 row: "strictly `<`". Its anchor `dt_gsk_optimize:1974` now
    resolves inside `_final_polish_compass`, not the accept block.
  - phase_gate_register.csv Gate 3 row records "dt_gsk.py a274e0f8, _dt_core.py 1ef815ce,
    _dt_profiles.py c3dcdce3, _dt_rng.py db1cc028" — the PRE-fix, PRE-rename hashes that
    algorithm_freeze_manifest.json itself marks SUPERSEDED ("do NOT cite it as the current method
    lock", registered CR-0007). The live hashes are 51b12194 / dc2d59db / 7baadf22 / 8a0fc27d.
root_cause: R-02's registry sweep covered equation_registry.csv but not the sibling correspondence
  artifact; the Gate 3 row was never re-signed after the C006/M038 fixes and the DT-GSK rename.
scientific_or_editorial_justification: §10.1 requires phase_gate_register.csv to carry a PASS row
  "with evidence" for every build gate, and forbids Gate A passing over an unevidenced row. Evidence
  that contradicts the frozen code is not evidence.
impact_on_validity_or_acceptance: Not reader-facing, but it is the artifact an editor or a
  reproducibility referee would pull first. It also means the freeze manifest's own PENDING item
  "P2 independent one-iteration code->pseudocode walk" was, on this evidence, never completed against
  the post-fix code.
required_correction: (i) Correct the E8 row to `<=` (ties accepted) and repoint its anchor to
  _dt_core.py:3362; (ii) re-sign the Gate 3 register row against
  algorithm_freeze_manifest_2026-07-19.json and its four live hashes, or add a supersession note
  pointing there; (iii) close or re-open the "P2 one-iteration walk" pending item explicitly.
acceptable_alternatives: A CR row in change_request_register.csv recording the correspondence-artifact
  correction, with the Gate 3 row annotated rather than re-signed.
additional_evidence_needed: None — this Stage-6 audit constitutes the one-iteration walk; its result
  is section 4 above.
dependencies: Stage 0/3 governance seat owns phase_gate_register.csv.
expected_improvement: Gate 3's evidence stops contradicting the shipped method.
post_revision_verification: Re-read implementation_correspondence.md against _dt_core.py:3362 and
  re-run the hash comparison against the 2026-07-19 manifest.
status: open
```

### M6-07 — S5.2's "cannot drift without failing the gate" claim is not supported by the two artifacts it names

```text
ticket_id: M6-07
review_stage: Stage 6 — Method and theory
reviewer_role: R2 (T1-OPT)
severity: Moderate
priority: P2
confidence: Confirmed
issue_type: reproducibility
manuscript_location: papers/supplementary.tex, S5.2 ("the repository's configuration-lock validator
  and the byte-stability regression test enforce byte-identity of the current sources on every run,
  so the code that produced the current release cannot drift without failing the gate")
claim_id_or_artifact_id: CN-02 / MT-11
concise_issue: Neither named artifact does what the sentence claims. The configuration-lock validator
  checks YAML experiment-config keys, not source bytes; the byte-stability regression test's golden
  cells are D<=30 only, by its own docstring, so the D>=50-gated ISM, eigenframe polish and upper-tier
  controllers are outside its coverage.
exact_evidence_or_observation:
  - scripts/validate_profile_lock.py:12-34 — REQUIRED_LOCKS is a dict of YAML keys (parallel,
    parallel_backend, warmup, profile, seed_policy, rand_generator) for three smoke configs. The file
    contains no hash, no sha256, no manifest read (grep "manifest|sha256|hash" -> no matches).
  - tests/regression/test_dt_gsk_byte_stable.py:10-31 — "Cells are D<=30 (below the D>=50
    SGSM/parallel-kernel tier)"; _GOLDEN = sphere D10, sphere D30, cec2017 F1 D10, cec2017 F3 D30.
  - The one D>=50 regression that exists, tests/regression/test_dt_graph_backend_parity.py, compares
    the numba and NumPy backends against EACH OTHER, not against a frozen golden value, so a
    semantic change to the ISM update rule would change both identically and still pass.
  - The same mis-description is inherited from algorithm_freeze_manifest.json change_control.locks
    ("scripts/validate_profile_lock.py (byte-identical ISM core)") and from
    implementation_correspondence.md finding 5.
root_cause: The lock names were carried forward from the migration-era manifest without re-checking
  what each script asserts today.
scientific_or_editorial_justification: §4 forbids "calls a method robust without adequate stress
  testing" and its analogue here — asserting a machine-enforced non-drift guarantee whose named
  enforcers do not cover the guaranteed surface. §10.3 requires the determinism contract to be
  recorded accurately per artifact class.
impact_on_validity_or_acceptance: The underlying reproducibility position is fine — the freeze
  manifest's SHA-256s DO pin the sources and I verified all four match. The defect is that the
  sentence attributes the guarantee to the wrong mechanisms and over-states the tier coverage.
required_correction: Rewrite to: "the current freeze manifest records a full SHA-256 for each shipped
  module and a Merkle digest over the subsystems; a low-dimensional byte-stability golden test
  (D<=30) and a D>=50 backend-parity test guard against trajectory and kernel drift, and any change to
  the frozen sources requires a recorded change request." Add a D>=50 golden-value cell if the
  stronger claim is wanted.
acceptable_alternatives: Drop the "cannot drift without failing the gate" clause and rely on the
  manifest + change-request statement, which is true as written.
additional_evidence_needed: Optional (non-blocking): one D=50 and one D=100 golden-value cell in
  test_dt_gsk_byte_stable.py, which would make the strong claim true.
dependencies: Stage 12 determinism-contract seat.
expected_improvement: The reproducibility claim becomes exactly as strong as the evidence.
post_revision_verification: Re-read the revised sentence against the two scripts' actual assertions.
status: open
```

### M6-08 — Four symbols used in printed equations are never defined in the main text

```text
ticket_id: M6-08
review_stage: Stage 6 — Method and theory
reviewer_role: R2 (T1-OPT)
severity: Minor
priority: P2
confidence: Confirmed
issue_type: writing
manuscript_location: Eq.(11) (equations.tex:164-171): w_i, I^+ ; Eq.(13) (:185-193): M ;
  Eq.(10) (:147-151): "unfrozen" ; Eq.(1) (:14-18): r_i and the inverse use of rank(.)
claim_id_or_artifact_id: ART-NOTATION / tab:notation, tab:notation-ism
concise_issue: Stage 6 requires every symbol to be defined before or at first use. Five are not, in
  the main text: the ISM per-move weight w_i, the strictly-improving index set I^+, the child-seed
  modulus M, the BSE "unfrozen" row set, and the rank variable r_i (whose operator rank(.) is used as
  its own inverse: rank(r_i - 1) means "the individual whose rank is r_i - 1").
exact_evidence_or_observation: tab:notation-ism lists G_abs, G_signed, g_act, C, lambda, eta,
  kappa_min, conf(.), V, s_fp -- but neither w_i nor I^+. tab:notation lists no r_i. M is defined only
  in Supplement S5 ("the RNG substream modulus of main-text Equation (13) is M = 2 147 483 646").
  "unfrozen" is explained only in the S5 BSE paragraph (elite freeze at round(0.05 NP)).
root_cause: The N-015 notation-table split moved the RNG key to the supplement and the ISM key was
  built from state components rather than from the equation's free symbols.
scientific_or_editorial_justification: Mandate line 1638 ("verify every symbol is defined before or
  at first use").
impact_on_validity_or_acceptance: Slows an expert reader; none of the five is ambiguous enough to
  block reimplementation given S5.
required_correction: Add three rows to tab:notation-ism (w_i = delta_i * s_i, the improvement x
  source weight; I^+ = strictly-improving accepted moves this generation) and one to tab:notation
  (M = 2 147 483 646, child-seed modulus). Add "(the top round(0.05 NP) elites are frozen and
  excluded)" to the Eq.(10) surrounding prose. Either define r_i or write Eq.(1) as
  R_1 = pi^{-1}(r_i - 1) with pi the index->rank map.
acceptable_alternatives: A single "symbols defined in Supplement S5" pointer at the equation block,
  provided w_i and I^+ are covered there (w_i is; I^+ is only implicit).
additional_evidence_needed: None.
dependencies: Word/OMML parity re-check after any notation-table edit.
expected_improvement: Self-contained main-text notation.
post_revision_verification: Re-extract the rendered notation tables and confirm every free symbol of
  Eqs.(1)-(13) resolves.
status: open
```

### M6-09 — Equation registry E9 names the wrong fraction

```text
ticket_id: M6-09
review_stage: Stage 6 — Method and theory
reviewer_role: R2 (T1-OPT)
severity: Minor
priority: P2
confidence: Confirmed
issue_type: reproducibility
manuscript_location: papers/build_prompt_phases/phase_03/equation_registry.csv, row E9
claim_id_or_artifact_id: ART-EQUATIONS / E9
concise_issue: The canonical registry row for the budget-safe escape says the Cauchy perturbation
  applies to "the worst r_rst*NP" rows. The code and the rendered Eq.(10) both use r_c
  (bse_cauchy_frac = 0.10), which differs from r_rst (bse_restart_frac = 0.30 at D<50).
exact_evidence_or_observation:
  - registry E9 equation field: "x_i <- x_i + gamma*C(0,1) for worst r_rst*NP; capped by R_max,
    x<bse_stop_frac"
  - rendered Eq.(10) (equations.tex:147-151): "worst round(r_c NP) unfrozen rows, kept iff <="
  - code _dt_core.py:3934 `n_cauchy = max(1, _round_half_up(_cfg_bse_cauchy_frac * float(NP)))`
    (bse_cauchy_frac=0.10) vs :3963 `n_restart = max(1, _round_half_up(_cfg_bse_restart_frac *
    float(NP)))` (bse_restart_frac = 0.30 at D<50, 0.10 at D>=50).
  - The registry row also omits the acceptance rule (kept iff <=) and the midpoint bound repair, both
    of which the rendered equation carries.
  - equations.tex:3 declares equation_registry.csv the canonical source and forbids editing the .tex
    without a matching registry change request; the .tex is correct and the registry is not.
root_cause: R-02's registry correction pass covered E3/E4/E8 only.
scientific_or_editorial_justification: §10.11 / Gate F traceability — the governed canonical artifact
  must match the rendered exhibit.
impact_on_validity_or_acceptance: Not reader-facing; a 3x parameter error in the governed registry.
required_correction: Update registry row E9 to "worst round(r_c NP) UNFROZEN rows (r_c =
  bse_cauchy_frac); gamma = r_s (u-l)/sqrt(D); bound-repaired; kept iff <=; capped by R_max and
  bse_stop_frac", and re-verify E1a-E12 against equations.tex as a set.
acceptable_alternatives: None.
additional_evidence_needed: None.
dependencies: M6-06 (same class).
expected_improvement: Registry and rendered equations agree everywhere.
post_revision_verification: Diff each registry row against its equations.tex block.
status: open
```

### M6-10 — Every `_dt_core.py` provenance anchor in the manuscript sources is stale

```text
ticket_id: M6-10
review_stage: Stage 6 — Method and theory
reviewer_role: R2 (T1-OPT)
severity: Minor
priority: P2
confidence: Confirmed
issue_type: reproducibility
manuscript_location: papers/build_prompt_phases/phase_03/equations.tex (BIND comments for E5, E8,
  E9, E11); papers/supplementary.tex (BIND comments at :1498, :1557, :1590, :1610, :1620, :1631,
  :1646, :1662, :1676, :1690)
claim_id_or_artifact_id: BIND traceability apparatus
concise_issue: All line anchors that point into _dt_core.py are off by ~7-65 lines against the
  byte-locked source, while anchors into every OTHER frozen module resolve exactly. They were
  recorded before the C006/M038 fixes shifted the file and never re-verified.
exact_evidence_or_observation (anchor -> what is actually at that line):
  - equations.tex E8 "_dt_core.py:3325" -> `mutants = pop[r1,:] + de_F*(pop[r2,:]-pop[r3,:])`
    (the accept step is :3362)
  - equations.tex E9 "_dt_core.py:3874" -> `_bse_acc_floor = _cfg_bse_acceptance_floor`
    (the Cauchy rescue is :3928-3948)
  - equations.tex E5 "_dt_core.py:790" -> a dict alias line ("nl": "nlpsr") (_psr_target_size is :800)
  - equations.tex E11 ":1882/:1907" -> off by 7/8 (_final_polish_basis :1889, _final_polish_compass
    :1915)
  - supplementary.tex "force-nonzero _dt_core.py:3204-3229" -> :3204 is a comment; the block is
    :3238-3266
  - supplementary.tex "D_jun/p_jun _dt_core.py:2909-2913" -> actual :2941-2945
  - supplementary.tex "kr floor _dt_core.py:2889-2892" -> actual :2921-2925
  - supplementary.tex "cauchy rescue :3868-3894" -> actual :3928-3948
  - supplementary.tex "A1 late-accept :3335-3346" -> actual :3373-3383
  - supplementary.tex "coordinate LS branch _dt_core.py:4431-4519" -> actual :4495-4580
  - supplementary.tex "d_m sum bincount :3641-3645" -> actual :3705-3711
  CONTROL (these all resolve exactly): interaction_graph.py:222 ig_update_from_accepted,
  :552 ig_extract_blocks, :678 ig_ready, :697 ig_adaptive_threshold; _numba_accel.py:407/414 gsk
  kernel, :505 mask kernel, :909 psr kernel; gained_shared_junior.py:56; gained_shared_senior.py:59.
root_cause: implementation_correspondence.md explicitly disclaims its own anchors ("Line numbers are
  at anchor 262fc16c9"); the .tex BIND comments inherited the same pre-fix numbers with no such
  disclaimer and were not re-derived after the rename/fix.
scientific_or_editorial_justification: These comments ARE the paper's code-correspondence apparatus.
  §10.6 requires code correspondence to be verifiable.
impact_on_validity_or_acceptance: Not reader-facing (LaTeX comments), but it defeats the audit trail
  a Stage-6 or reproducibility referee follows, and it is the mechanical signature of a
  correspondence walk that was not repeated after the code moved.
required_correction: Re-derive the _dt_core.py anchors mechanically (a 20-line script over the BIND
  comments), or convert them to symbol anchors (function/variable names), which are stable under
  line drift, as the other modules' anchors effectively already are.
acceptable_alternatives: Add the same "anchors at commit X" disclaimer the correspondence artifact
  carries, and pin X.
additional_evidence_needed: None.
dependencies: None.
expected_improvement: Restores a machine-followable audit trail.
post_revision_verification: Script every BIND anchor and assert the named symbol appears within +/-3
  lines.
status: open
```

### M6-11 — Reader-facing captions cite the superseded freeze manifest

```text
ticket_id: M6-11
review_stage: Stage 6 — Method and theory
reviewer_role: R2 (T1-OPT)
severity: Minor
priority: P2
confidence: Confirmed
issue_type: reproducibility
manuscript_location: papers/build_prompt_phases/phase_03/parameter_table.tex:14 ("Hash-frozen in
  \texttt{algorithm\_freeze\_manifest.json}", rendered on PDF p.14, Table 10 caption);
  parameter_table_detail.tex:14 (same string, supplement Table); papers/supplementary.tex S5.2
claim_id_or_artifact_id: ART-PARAMS
concise_issue: Both parameter-table captions name algorithm_freeze_manifest.json as the hash-freeze
  authority. That file marks ITSELF superseded and its recorded hashes match no shipped module; the
  live authority is algorithm_freeze_manifest_2026-07-19.json.
exact_evidence_or_observation:
  - algorithm_freeze_manifest.json, key "SUPERSEDED": {"by":
    "algorithm_freeze_manifest_2026-07-19.json", "why": "... none of them matches a shipped module
    ... do NOT cite it as the current method lock. Registered as CR-0007"}; and "gate.status":
    "DRAFT-PENDING-SIGNOFF" with three pending items.
  - I verified the 2026-07-19 manifest's four SHA-256s against the working tree: all four MATCH.
  - Supplement S5.2 does explain the whole chain and names the current manifest correctly, so the
    package is not misleading overall; the MAIN-TEXT caption carries no pointer to S5.2.
  - Related: papers/scripts/validate_provenance_claims.py:45 also reads only the superseded manifest
    (see R-07 note above); it passes only because Rule B recomputes live hashes from source.
root_cause: The caption predates the 2026-07-19 re-mint and was not swept.
scientific_or_editorial_justification: §10.3 (source release ID and checksums must be recorded
  correctly); §10.17.4 also flags raw internal filenames in reader-facing captions (cross-referred to
  the T5-WRITE seat).
impact_on_validity_or_acceptance: A referee resolving the caption lands on a file that disclaims
  itself.
required_correction: Point both captions at algorithm_freeze_manifest_2026-07-19.json, or replace the
  filename with a natural-language pointer ("hash-frozen; see the frozen-configuration record in
  Supplement S5.2"). Extend validate_provenance_claims.py to also read (and cross-check) the current
  manifest.
acceptable_alternatives: Keep the filename but add "(current manifest; see Supplement S5.2 for the
  provenance chain)".
additional_evidence_needed: None.
dependencies: T5-WRITE (§10.17.4) and Stage 12 (validator scope).
expected_improvement: Caption resolves to the artifact that actually pins the shipped code.
post_revision_verification: Rebuild and grep the rendered PDF/DOCX for the filename.
status: open
```

### M6-12 — Eigenframe-polish specification gaps (bounding, ordering, cap)

```text
ticket_id: M6-12
review_stage: Stage 6 — Method and theory
reviewer_role: R2 (T1-OPT)
severity: Minor
priority: P2
confidence: Confirmed
issue_type: method
manuscript_location: papers/sections/proposed_algorithm.tex:580-607 (§3.5); Eq.(12)
claim_id_or_artifact_id: E11 / MT-09 / C1
concise_issue: The polish is the paper's C1 contribution, yet three behaviours are absent from the
  main text and one is absent everywhere: (a) probes are bound-handled by HARD CLIPPING, not the
  midpoint repair of Eq.(8) that §3.1 presents as the algorithm's repair rule; (b) the direction
  ordering (descending |eigenvalue|) and (c) the step schedule / eval cap are supplement-only.
exact_evidence_or_observation:
  - (a) _dt_core.py:1958 `np.clip(cand, lower, upper, out=cand)` inside _final_polish_compass. Every
    other evaluation path uses bound_constraint (midpoint): trials (fused, :3098+), DE (:3346),
    BSE Cauchy (:3939), LS (:4538). The clip is stated NOWHERE in main text or supplement.
  - (b) _dt_core.py:1908 `order = np.argsort(-np.abs(eigvals), kind="stable")` -- disclosed in S5.
  - (c) step 0.05*span, growth 1.3 capped at 0.5*span, halving after a full sweep, min step 1e-12,
    cap 0.02*MaxFES -- disclosed in S5, absent from §3.5.
  The direction ordering is behaviourally load-bearing: with a 0.02*MaxFES cap the sweep is
  truncated, so which directions come first determines what is searched.
root_cause: §3.5 was written as a conceptual description with detail deferred to S5; the clip was
  never noticed because Eq.(8) is presented as universal.
scientific_or_editorial_justification: §10.6 requires exact behaviour for each mechanism; the repair
  rule is one of the four "inherited elements" the paper says are unchanged.
impact_on_validity_or_acceptance: Minor as reimplementation risk (S5 covers 2 of 3), but the
  bound-handling exception contradicts §3.1's blanket statement.
required_correction: Add one clause to §3.5 or S5: "polish probes are clipped to the box rather than
  midpoint-repaired, since the compass step is generated from the incumbent rather than from a
  parent-child pair"; and pull the eigenvector ordering into §3.5 (one clause) because it interacts
  with the cap.
acceptable_alternatives: A forward reference from §3.5 to S5 for all three, plus the clip clause
  (which must be added somewhere -- it currently exists nowhere).
additional_evidence_needed: None.
dependencies: None.
expected_improvement: C1 becomes fully specified from the paper.
post_revision_verification: Re-read §3.5 + S5 against _dt_core.py:1889-1974.
status: open
```

### M6-13 — Main-text BSE description: "perturbs AND reseeds" is an OR; stop fraction and module gate absent

```text
ticket_id: M6-13
review_stage: Stage 6 — Method and theory
reviewer_role: R2 (T1-OPT)
severity: Minor
priority: P2
confidence: Confirmed
issue_type: method
manuscript_location: papers/sections/proposed_algorithm.tex:389-406 (§3.3.4)
claim_id_or_artifact_id: MT-06 / E9
concise_issue: The main text says BSE "perturbs the worst r_c fraction ... and reseeds part of it
  from a diversity archive", implying both always happen; the code runs the reseed only if the
  Cauchy rescue failed to improve. The BSE stop fraction (0.95) and the ACE module gate are named as
  existing but never valued / never mentioned respectively.
exact_evidence_or_observation:
  - _dt_core.py:3956-3959: after an improving Cauchy rescue, `escape_triggered = False`; the reseed
    at :3961 is guarded by `if escape_triggered and restart_pool.size > 0`. Supplement S5 states it
    correctly ("a successful rescue cancels the restart for that generation").
  - bse_stop_frac = 0.95 (_dt_core.py:292; never overridden by any tier). §3.3.4 says "a stop
    fraction beyond which it is disabled" without the value; the value appears only in S5.
  - Module gate: BSE fires only when `pop_modules_active` (ACE mass on module-active arms >= 0.30;
    _dt_core.py:277-278, gate at :3907). Absent from the main text entirely; in S5.
root_cause: Main-text compression.
scientific_or_editorial_justification: §10.6 — a hard gate that can suppress the mechanism entirely
  is part of its "exact behavior".
impact_on_validity_or_acceptance: Low; S5 is correct. But the main text as written describes a
  strictly more aggressive escape than the one that runs.
required_correction: Change "and reseeds" to "or, if the perturbation fails to improve, reseeds";
  give the stop fraction its value (0.95); add a half-clause noting the escape is additionally gated
  on the operator pool retaining probability mass on module-active arms (S5).
acceptable_alternatives: Explicit forward reference to S5 for the gate.
additional_evidence_needed: None.
dependencies: None.
expected_improvement: Main-text BSE matches the code.
post_revision_verification: Re-read §3.3.4 against _dt_core.py:3907-4010.
status: open
```

### M6-14 — `D_jun` presented as an exact count; it is a Bernoulli rate

```text
ticket_id: M6-14
review_stage: Stage 6 — Method and theory
reviewer_role: R2 (T1-OPT)
severity: Minor
priority: P2
confidence: Confirmed
issue_type: method
manuscript_location: tab:notation row "D_jun = ceil(D(1-x)^Kexp) | number of dimensions in the
  junior phase"; Table 5 (tab:worked-example) column D_jun; Eq.(3)
claim_id_or_artifact_id: E2 / ART-NOTATION
concise_issue: The prose is correct ("The expected number of coordinates treated by the junior rule",
  proposed_algorithm.tex:65-68), but the notation row and the worked-example table present D_jun as
  the realized count. The realized count is Binomial(D, D_jun/D). Separately, Eq.(3) shows a single
  scalar K_exp while the code draws K_exp per individual from the ACE arm.
exact_evidence_or_observation: _dt_core.py:2941-2945 `D_junior_i = ceil(D * progress**kexp)`, clipped
  to [0,D], then `p_junior_i = D_junior_i / D`; the mask is `rands_j <= p_jun` (_dt_core.py:1013-1016
  / _numba_accel.py:505+). kexp is `pool[s_idx, 2]` (:2919), i.e. per-individual per-generation.
  Supplement S5 states both correctly ("applied as a per-coordinate probability ... equals D_jun only
  in expectation").
root_cause: Notation row and table caption written from the schedule formula.
scientific_or_editorial_justification: Mandate line 1640 (verify equality vs. sampling notation).
impact_on_validity_or_acceptance: Low; this is GSK-inherited behaviour and S5 corrects it.
required_correction: Change the tab:notation gloss to "expected number of junior-phase coordinates
  (applied as the per-coordinate rate D_jun/D)"; add "(expected)" to the Table 5 column header; add
  a subscript i to K_exp in Eq.(3) or one clause noting K_exp is arm-resolved per individual.
acceptable_alternatives: One sentence at Eq.(3) plus a Table 5 caption clause.
additional_evidence_needed: None.
dependencies: None.
expected_improvement: Removes a deterministic/stochastic notation conflict.
post_revision_verification: Re-read tab:notation and Table 5 against S5.
status: open
```

### M6-15 — Junior rank-neighbour boundary rule is unstated anywhere

```text
ticket_id: M6-15
review_stage: Stage 6 — Method and theory
reviewer_role: R2 (T1-OPT)
severity: Minor
priority: P3
confidence: Confirmed
issue_type: method
manuscript_location: Eq.(1) (equations.tex:14-18); no supplement coverage
claim_id_or_artifact_id: E1a
concise_issue: Eq.(1) indexes rank r_i - 1 for the best individual (rank 0) and r_i + 1 for the worst
  (rank NP-1), both out of range. The code's special cases are unstated in the paper.
exact_evidence_or_observation: gained_shared_junior.py:88-96 -- best: R1 = ind_best[1],
  R2 = ind_best[2]; worst: R1 = ind_best[NP-3], R2 = ind_best[NP-2]; interior: rank +/- 1. grep of
  supplementary.tex for the boundary rule returns nothing.
root_cause: Treated as an inherited GSK implementation detail.
scientific_or_editorial_justification: Mandate line 1642 (boundary cases) and line 1670
  (reimplementable without inferring hidden rules).
impact_on_validity_or_acceptance: Low -- the handling matches the reference GSK implementation and
  the paper cites mohamed2020gaining -- but a reimplementer hits an index error and must guess.
required_correction: One clause after Eq.(1) or in S5: "at the rank boundaries the pair is taken from
  the two nearest interior ranks (ranks 1 and 2 for the best individual, NP-3 and NP-2 for the
  worst), as in the reference implementation."
acceptable_alternatives: A footnote citing mohamed2020gaining for the boundary convention.
additional_evidence_needed: None.
dependencies: None.
expected_improvement: Removes the last hard-blocking ambiguity in the inherited operator.
post_revision_verification: Confirm the clause matches gained_shared_junior.py:88-96.
status: open
```

### M6-16 — Small precision defects in S5 and the notation tables

```text
ticket_id: M6-16
review_stage: Stage 6 — Method and theory
reviewer_role: R2 (T1-OPT)
severity: Editorial
priority: P3
confidence: Confirmed
issue_type: writing
manuscript_location: supplementary.tex S5 (ACE paragraph; coordinate-LS paragraph);
  tab:notation-scaffold (ACE arm pool row)
claim_id_or_artifact_id: E6 / ART-NOTATION
concise_issue: Three small imprecisions, none affecting a number:
  (a) S5: "when the generation is net-improving the full-pool target is used with worsened arms
      floored at pi_min" -- the code (and Eq.(7)) apply a EUCLIDEAN projection onto the floored
      simplex, which redistributes mass; it is not a floor-and-renormalize.
      (_dt_core.py:694-730; _numba_accel.py:868-899.)
  (b) S5: "When a generation yields no net improvement (its summed f_old - f_new is NON-POSITIVE) the
      credit target is restricted to the improving arms" -- at exactly zero the code HOLDS pi
      (projection only) rather than restricting (_dt_core.py:1236-1238). Eq.(7) states this
      correctly ("otherwise" branch); only the prose is loose.
  (c) S5 coordinate LS: "The minimum probe step is 1e-3 of each coordinate's population scale" --
      the code floors the population scale at 1e-3 of the BOX SPAN
      (_dt_core.py:2333 `local_search_min_step = min_step_frac * span`; :4499
      `coord_scale = np.maximum(coord_scale, local_search_min_step)`), which is a different quantity.
  (d) tab:notation-scaffold fixes the ACE arm pool at {a_m}_{m=1}^{5} while Eq.(7) sums over
      M in {5,6}.
exact_evidence_or_observation: as cited inline above.
root_cause: Prose paraphrase of exact operators.
scientific_or_editorial_justification: §10.6 exactness; Gate F consistency between prose and equation.
impact_on_validity_or_acceptance: None on results; small reimplementation friction.
required_correction: (a) "projected onto the floored simplex"; (b) "strictly negative"/"non-positive
  ... except an exactly zero aggregate, which leaves pi unchanged"; (c) "the coordinate scale is
  floored at 1e-3 of the box span"; (d) write the pool as {a_m}_{m=1}^{M}, M in {5,6}.
acceptable_alternatives: None needed.
additional_evidence_needed: None.
dependencies: None.
expected_improvement: Exact prose.
post_revision_verification: Re-read against the four cited code sites.
status: open
```

---

## 8. Prompt staleness (required report per the seat brief; §1.4 precedence)

The governing prompt's §1.5 snapshot ("current as of 2026-07-20") predates the 2026-07-21/22
remediation entirely and now contradicts the repository in at least three verifiable places. Per
§1.4 the repository governs; recorded here as instructed.

| Prompt statement | Repository state (verified) |
|---|---|
| §1.5 line 120: "the 80-ticket remediation ledger … stands at **73/80 fully closed** … **seven** … tickets remain open (RT-001 …; C-008 → C-001 …; N-009 / N-021 / M-007 / E-012 …)" | `papers/governance/remediation_2026_07_18/ticket_status.csv`: **80/80 closed** — 70 `closed_verified` + 10 `superseded_with_evidence`; **zero** rows in any other lifecycle state. RT-001 `closed_utc = 2026-07-21`. |
| §10.7 final bullet (line 3299): RT-001 "**IN PROGRESS**"; the runtime table "is being brought into single-environment comparability by **re-timing all six comparators** (`scripts/retime_comparators.py`)"; the review must "confirm … completion" of that refresh | RT-001 was **resolved by a different route**. Per its ledger row: the six-comparator re-timing *was* executed 2026-07-21 (~22 h) and **FAILED the determinism gate** (3,772 scientific-column diffs; the 2026-07-08 comparator evidence is not bit-reproducible under current code). `tab:runtime` was **re-scoped to DT-GSK-only** — `performance.tex:738` now reads "Table~\ref{tab:runtime} reports \dtgsk{}'s measured per-run wall-clock time". The remedy the prompt tells the review to confirm no longer exists. |
| §1.5 makes no mention of R-01 … R-14 | All fourteen are present in the repository and verified in §1 above (R-02 incompletely). A reviewer following §1.5 alone would re-raise R-01 (the Eq.(4) sign convention) and R-05 (budget crossing) as new Critical findings. |

Additionally, §10.6 (line 3270) and §5.5 (line 1139) both use the SGSM EMA mismatch
(`G←(1−λ)G+λΣ` vs `G←λG+ηΣ`) as a live calibration exemplar. **That defect is closed** — the rendered
Eq.(11) prints `G_• ← λG_• + η Σ …` and matches `interaction_graph.py:201`/`:344` exactly. The
exemplar is still useful as calibration, but it should be marked historical so a future seat does not
read it as an outstanding finding.

---

## 9. Gate F disposition

**Gate F — Method and Theory: CONDITIONAL PASS, blocked on M6-01 and M6-02.**

Gate F fails for "a material equation error, ambiguous central mechanism, uncounted budget,
unverified implementation-method mismatch, unsupported proof, or non-reimplementable core procedure."

- Material equation error: **none.** All thirteen displayed equations reproduce the frozen operator.
- Uncounted budget: **none.** Single controller, every path charged, MaxFES-exact, machine-proven.
- Unsupported proof: **not applicable** — the manuscript claims no convergence result and explicitly
  declines to transfer generating-set-search guarantees to the polish. Correct and commendable.
- Unverified implementation-method mismatch: **yes** — M6-02 (documented gate that does not gate),
  M6-03 (cadence/decay), M6-04 (pseudocode step placement), M6-05 (archive capacity).
- Non-reimplementable core procedure: **yes, narrowly** — M6-01. Three frozen constants of the ISM's
  own exploitation path are unobtainable from the paper, and the substitute prose is 2× wrong.

All blocking items are **text-only corrections against the byte-locked code**. No rerun, no new
evidence release, no change to any reported number. On correction and re-verification I would set
Gate F to PASS.

**Category score (Method & Theory): 4 — strong.** The equations are right, the accounting is right,
the complexity is right and honestly scoped, and the supplement's operator specification is well
above field norm. The score is held below 5 by M6-01/M6-02 and the cluster of ISM specification gaps.

---

## 10. Reproduction commands for this audit

```bash
# 1. Byte-identity of the audited code against the CURRENT freeze manifest
python - <<'PY'
import json,hashlib,os
m=json.load(open("papers/build_prompt_phases/phase_03/algorithm_freeze_manifest_2026-07-19.json"))
for n,h in m["frozen_core_sources"].items():
    p=os.path.join("src/gsk_family/optimizers",n)
    if os.path.exists(p):
        print(n, hashlib.sha256(open(p,'rb').read()).hexdigest()==h)
PY

# 2. M6-01 — measured ISM linkage share at D=50 (learned vs random blockwise rows)
#    (instrument dt_gsk_optimize with a generation_callback and read
#     log.linkage_rows / log.linkage_learned_rows / log.linkage_random_rows)

# 3. M6-03 — ISM decay/refresh cadence
#    (wrap _dt_core.ig_update_from_accepted and _dt_core.ig_extract_blocks with counters;
#     run build_pub_config(50, seed=20240620, max_nfes=30000))

# 4. R-05 / R-14
python -m pytest tests/regression/test_budget_crossing_semantics.py -q     # 14 passed

# 5. R-06 / R-07
python papers/scripts/validate_provenance_claims.py                        # [provenance] OK
python papers/scripts/check_manifest.py                                    # 15/15 match
```
