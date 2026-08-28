# Pre-Registration Addendum — Round-1 Revision Experiments (E1–E4)

**Signed and frozen: 2026-08-25, BEFORE any result from these experiments existed.**

- **Governs:** the four experiments requested by the *Algorithms* round-1 reviewers of
  `algorithms-4507562`, executed under CR-0023 and D-0047.
- **Relationship to the existing registration:** an **addendum** to
  `papers/build_prompt_phases/phase_05/ablation_preregistration.md` (frozen 2026-07-10). That
  document is append-only and is **not edited** by this one. Where a rule there does not fit an
  experiment here, the mismatch is named in §2 and a replacement rule is registered rather than the
  original being reinterpreted.
- **Primary evidence release in force:** `rel-2026-07-20-67d9345f9`, read-only and untouched. These
  experiments produce **new, separate** releases; no primary result is re-minted.
- **Attestation (no-inspection).** At the moment of signing, no rank, p-value, mean, effect size or
  curve from E1, E2, E3 or E4 had been computed, read or viewed. E1 was in flight and its output
  directory was not opened. The only executions preceding this document were the smoke rehearsal
  (`--smoke`, 2 functions × 2 runs × 3,000 evaluations, written to the gitignored
  `results/_revision_smoke/` and deleted) and two single-cell mechanism checks used to confirm the
  basis override alters the trajectory at all. Those are feasibility checks on machinery, not
  outcomes, and none of them entered any analysis.

---

## 1. What is registered

| Id | Reviewer point | Estimand |
|---|---|---|
| **E1** | R2.3 | Effect of the **refinement basis**, holding enablement constant: eigenframe vs coordinate axes vs no refinement, at equal evaluation budget |
| **E2** | R1.3 / R2.2 | Effect of **initial population size** on DT-GSK's standing: NP = 5D vs NP = 100 |
| **E3** | R2.1 | Effect of **dimension-tiering itself**: the tiered configuration vs an otherwise identical tier-constant one |
| **E4** | R2.7 | **Sensitivity** of the reported standing to the frozen thresholds and constants |

All four are **CEC2017**, the unified Threefry seed schedule at base seed 20240620, `seed_policy:
unified`, the suite's own protocol budget (`MaxFES = 10^4 · D`), and the 29 scored functions
(F1, F3–F30). E1–E3 use 51 runs, matching the panel. E4 uses 15 runs, declared below.

## 2. Where the 2026-07-10 registration does not fit, and what replaces it

**§1.4 (per-dimension baseline-ON check) does not govern E1 or E3, and must not be stretched to.**
That rule binds *disable deltas*: before claiming that removing a mechanism changed something at
dimension *d*, the mechanism must be verified ON in the baseline at *d*, else the contrast is a null
contrast and is excluded. Neither E1 nor E3 is a disable delta.

- **E1** holds enablement constant and substitutes the *basis* the refinement searches along. The
  mechanism is ON in both arms by construction; §1.4's premise is satisfied trivially and carries no
  information here.
- **E3** deliberately **inverts** §1.4's premise. Applying the D=10 parameter set at D=100 turns
  mechanisms off that the baseline has on, and applying the D=100 set at D=10 turns mechanisms on
  that the baseline has off. Under §1.4 read literally, every E3 cell would be a "null contrast" and
  the experiment could report nothing. That reading is wrong for this design: the *point* of E3 is to
  measure what the dimension-dependence buys, so the change in enablement **is the treatment**, not a
  confound to be excluded.

**Replacement rule for E3 (binding).** Each E3 arm is a *configuration transplant*, not a component
removal. For every (arm, dimension) cell the report must state which mechanisms the transplanted
parameter set turns on or off relative to the tiered baseline at that dimension, taken from the
resolved `run_config.json`, and no E3 result may be described as the contribution of any individual
mechanism. E3 licenses exactly one class of claim: *the tiered configuration does / does not
outperform a tier-constant one at dimension d*. Attributing an E3 difference to ISM, to the polish,
to NLPSR, or to any other single subsystem is **prohibited** — that is what E1 and the existing
scaffold ablation are for.

**Disclosure for E1 (binding).** E1 reaches `research_oracle_basis`, a keyword-only hook that
`tests/regression/test_dormant_mechanisms_unreachable.py` asserts is unreachable from every config,
profile, CLI and adapter path. That test's own docstring records that making the hooks reachable
"requires a new evidence release", which is what E1 produces. E1 is therefore driven from
`scripts/run_e1_basis_contrast.py`, outside the shipped surface; nothing under `src/` is modified and
the tripwire remains green. **Any report of E1 must disclose this**, state that the shipped
configuration is otherwise unchanged, and state that the identity basis reproduces the axes fallback
the polish already uses when no graph signal exists.

## 3. Designs

### 3.1 E1 — refinement-basis contrast

Three arms, identical in every other respect (shipped `pub` profile, ISM live, linkage live, same
seeds, same budget), D ∈ {50, 100}, 51 runs:

| Arm | Source | Status at signing |
|---|---|---|
| no refinement | `configs/_ablation/_51run/overlay_no_finalpolish_cec2017_51.yml` | already in the frozen ablation release |
| **coordinate axes** | `research_oracle_basis = I(D)` | **the only new cell** |
| eigenframe | `configs/_ablation/_51run/overlay_full_cec2017_51.yml` | already in the frozen ablation release |

### 3.2 E2 — matched population size

DT-GSK at `pop_size: 100`, all four dimensions, 51 runs. The six frozen comparator columns are reused
unchanged; no comparator is re-run.

**Declared single-factor scope (binding).** Only `NP_init` changes. The NLPSR floor `n_min` stays at
its tier value (12 / 12 / 25 / 25), the D≥100 SP-NLPSR floor is untouched, and the archive size
remains `arch_size_mult × NP_init` and therefore moves with NP by construction. The report must state
this, because it means E2 is **not** a full "DT-GSK with the comparators' population regime" — it is
the initial size alone.

**Framing, pre-committed.** NP = 5D is a *declared component of the dimension-tiered method*, not an
incidental setting. E2 is therefore reported as an **ablation of that component**, labelled
"DT-GSK with its population rule replaced by the panel constant", and not as a corrected baseline.

### 3.3 E3 — uniform versus tiered

Three arms at all four dimensions, 51 runs. The tiered arm is the frozen primary leg, reused
read-only; only the two transplant arms are new.

| Arm | Definition |
|---|---|
| T (tiered) | the shipped profile — frozen leg, not re-run |
| U-low | `pub_overrides(10)` applied unchanged at every dimension |
| U-high | `pub_overrides(100)` applied unchanged at every dimension |

Both override dictionaries are generated programmatically from
`gsk_family.optimizers._dt_profiles.pub_overrides` and never transcribed; 88 keys differ between the
two tiers.

**Reading registered (binding).** The **same-constants** reading is primary: the tier dictionary is
copied verbatim, so dimension-keyed gates inside it — `interaction_graph_min_dim`, `linkage_min_dim`,
the `kr_min_dims/D` floor, `linkage_block_size_by_dim` — are carried as constants. No arm may be
described as "dimension-independent"; the permitted term is **tier-constant**. Some scaling is
irreducible (NP = 5D, the junior/senior split, the 1/√D scaling) and the report must say so.

### 3.4 E4 — parameter sensitivity

One factor at a time, D ∈ {30, 100}, all 29 functions, **15 runs per cell**, 27 cells. Seven
constants at two levels each, ±20 % for real-valued parameters and the nearest different integer for
integer-valued ones — the integer convention must be stated in the caption, not silently rounded.
One cell is skipped automatically because its perturbation lands on the frozen value
(`interaction_update_period` is already 1 at D=30).

**Run-count justification.** The reviewer asked for a *limited* study. Runs are reduced rather than
functions, so every cell still spans the full scored set and no function-selection effect is
introduced.

**Reporting constraints (binding, carried from `robustness_plan.md`).** E4 is **exploratory**. The
label must appear in both the section title and the table caption; the analysis is **descriptive
only**; **no hypothesis tests and no corrected p-values** may be computed on it; it belongs in the
supplement and must not be mixed with the S6 ablation material. The single permitted headline form is
an ordinal statement — "DT-GSK's position within the family panel is / is not unchanged under the
perturbations tested".

**Known-sensitive parameter, registered in advance.** The repository already records a measured
perturbation showing `interaction_update_period > 1` was slower *and* worse
(`configs/dtgsk_cec2013lsgo.yml`). It is included in the sweep deliberately. Omitting the one
constant the project already knows is sensitive would itself be a finding a reviewer could make.

## 4. Analysis, fixed before results

- **Pairing.** Every new cell pairs with the frozen bank at matched (dimension, function, run) through
  the unified seed schedule, which contains no optimizer or cell term.
- **E1, E2, E3:** paired Wilcoxon signed-rank across functions, Holm-corrected **within dimension**,
  α = 0.05, with Vargha–Delaney A₁₂ on the raw runs. Friedman mean ranks are **descriptive**. Any
  omnibus reported uses the tie-corrected statistic with the Iman–Davenport F — the convention now
  used everywhere in this paper after R1.4.
- **E4:** descriptive only, per §3.4.
- **Method citations** stay within `papers/governance/allowed_citation_keys.txt`.
- **No algorithm changes.** Modifying DT-GSK in response to any of these results is prohibited. If a
  result is unfavourable it is reported, not engineered away.

## 5. Pre-committed outcome wording

Registered **before** the results exist, so that an unfavourable outcome cannot be re-narrated after
the fact. The wording below is what will be used, adjusted only for numbers.

**E1 — if the eigenframe does not beat coordinate axes.** "The refinement's benefit is carried by the
budget-exact compass endgame rather than by the learned basis: at equal budget, an eigenframe basis
is not distinguishable from the coordinate axes. Contribution C1 is accordingly stated
basis-neutrally as a deterministic final refinement. The polish itself remains Holm-significant
against no refinement." This outcome is **anticipated**: the repository's own configuration note
records the learned basis matching the coordinate axes to 5 × 10⁻⁵.

**E1 — if coordinate axes beat the eigenframe.** Reported as such, plainly, and ISM's fitness-affecting
channel is then described as harmful at the tested tiers rather than merely inert.

**E2 — if DT-GSK's standing falls at matched NP.** "DT-GSK's family-rank standing is sensitive to its
population rule: with NP fixed at the panel constant, its ordinal position changes at [dimensions].
NP = 5D is a declared component of the dimension-tiered design, so this is an ablation of that
component rather than a correction; the affected rank statements are qualified as
configuration-dependent." The headline rank claims will be qualified accordingly. They will **not** be
quietly restricted to the dimensions that survive.

**E3 — if a tier-constant arm matches or beats the tiered one.** "At [dimensions], a tier-constant
configuration is not distinguishable from the tiered one; the tiering is therefore not shown to be
necessary there, and contribution C2 is narrowed to the tiers where it is demonstrated." If the D≥50
set is the load-bearing one, that is what will be said. The measured overhead of the high-dimension
constants will be reported alongside, since tiering may buy cost even where it does not buy accuracy.

**E4 — if a constant proves knife-edge.** Reported descriptively and added to the limitations. The
study is exploratory by registration, so a sensitive parameter is a disclosure, not a refutation.

**Universal.** If any experiment fails to run to completion, the shortfall is reported with the cells
missing. Partial results are never presented as complete.

## 6. Promotion

Results stage under `results/_revision/` and are **not** evidence until promoted. Promotion is a
separate, deliberate step producing new, non-superseding, checksummed releases; the primary release
`rel-2026-07-20-67d9345f9` and the frozen ablation release are never re-minted. `check_frozen_analysis`
must still report 115/115 byte-identical after promotion.

---

*Signed 2026-08-25 under CR-0023 / D-0047. Append-only: if any design element changes, a dated
amendment is appended below rather than the text above being edited.*

---

## Amendment A1 (2026-08-26) — E4 perturbation-level deviation at D=100, found post-hoc

Discovered during adversarial QC of the results, after the campaign completed and before any
E4 result was reported anywhere. Recorded here rather than corrected silently.

**The deviation.** Section 3.4 registered one-factor perturbations of "+/-20 % for real-valued
parameters ... around the frozen value". The driver
(`scripts/run_revision_experiments.py`, SENSITIVITY block) hard-coded one lo/hi pair per
real-valued parameter, derived from the D=30-tier frozen values, and applied that same pair at
both dimensions. For three parameters whose frozen value differs at D=100, the executed D=100
perturbations are therefore NOT +/-20 % of the frozen D=100 value:

| Parameter | Frozen at D=100 | Executed levels | Actual perturbation |
|---|---|---|---|
| `argp_threshold` | 0.010 | 0.016 / 0.024 | +60 % / +140 % (one-sided, above) |
| `bse_restart_frac` | 0.10 | 0.24 / 0.36 | +140 % / +260 % (one-sided, above) |
| `local_search_eval_budget_frac` | 0.02 | 0.008 / 0.012 | -60 % / -40 % (one-sided, below) |

All D=30 cells, all integer-valued parameters at both dimensions, and the remaining real-valued
parameters at D=100 conform to the registered rule.

**Consequences for reporting (binding).**
1. The blanket claim "no frozen constant is knife-edge at +/-20 %" is licensed only for the
   conforming cells. For the three parameters above at D=100 the licensed claim is: ordinal
   position and per-function means were stable under perturbations LARGER than registered
   (up to +260 %), but coverage is one-sided -- no evidence exists below the frozen value for
   `argp_threshold`/`bse_restart_frac`, nor above it for `local_search_eval_budget_frac`, at
   D=100. Robustness in magnitude holds a fortiori; symmetry does not.
2. Any table reporting E4 must state the executed levels per cell (they are recorded in each
   cell's promoted `run_config.json`), not the registered formula.
3. The observed outcomes are unaffected as data: all three parameters' D=100 cells kept ordinal
   position 1 with median ratios within ~2 % -- under perturbations several times larger than
   registered.

**No re-run is performed.** The deviation widens rather than narrows the tested range and E4 is
registered exploratory/descriptive; a symmetric +/-20 % D=100 screen for the three parameters is
noted as optional follow-up work, not owed to the current revision.

---

## Amendment A2 (2026-08-26) — E2 scope statement corrected: the archive does NOT scale with NP

Section 3.2 declared "the archive size remains `arch_size_mult x NP_init` and therefore moves
with NP by construction". Post-hoc source verification shows that formula is dead code in every
shipped configuration: `_dt_core.py` uses it only when `arch_max_size` is None, but the default
is `arch_max_size = 200` and no shipped tier overrides either field (the `EliteArchive` docstring
claiming otherwise is itself wrong). The archive capacity is therefore a flat 200 in BOTH E2 arms.

Consequence: E2 is a CLEANER single-factor experiment than registered — initial population size
is the only difference between the arms; the archive is identical. No result changes; the
declared-scope sentence in any report must describe the flat cap, not the formula.

---

## Amendment A3 (2026-08-27) — the executed Holm family for E2 and E3

The analysis plan above specifies Holm correction **within dimension**. What was
executed differs, and differs *differently* for the two experiments, so they are
recorded separately rather than under one clause.

- **E2** admits one comparison per dimension (tiered against the matched-population
  arm), so a within-dimension family has m = 1 and applies no correction at all.
  The executed family instead corrects **across the four dimensions**, m = 4.
- **E3** admits **two** comparisons per dimension (the two tier-constant transplant
  arms), so a within-dimension family has m = 2. The executed family is a
  **transpose** of the registered one — correcting across dimensions within each
  arm — not an expansion of it.

**Direction and effect.** For E2 the executed family is strictly more
conservative than the registered one. For E3 neither family dominates the other
in general. Conservatism is therefore claimed here only as **verified over the
executed values**, not as a theorem: recomputing both experiments under the
registered within-dimension family leaves every reported decision unchanged in
all twelve cells.

Recorded as an amendment rather than silently, because the value of this
pre-registration is that its analysis plan was fixed in advance and any departure
is visible. The S9 preamble's deviation wording is adjusted to carry no count.

## Amendment A4 (2026-08-28) — E5: dimension-boundary sensitivity, registered before execution

Round-two addition, filed before any E5 run executes. The round-one reviewer point R2.7 names
"dimension thresholds and several algorithmic constants"; E4 varied seven constants and explicitly
left the tier boundaries (20, 50, 100) unvaried, which the manuscript concedes. E5 closes that half.
It is diagnostic and additive: the shipped profiles, the frozen evidence, and every reported number
of the round-one revision are unchanged.

**Design.** Each cell shifts one tier boundary just far enough to change the profile assigned to the
nearest official CEC2017 dimension, and runs DT-GSK at that dimension under the transplanted
profile. Mechanically each cell is a single-dimension profile transplant, identical in kind to E3:
`pub_overrides(source_tier_dimension)` applied as optimizer options, with every dimension-derived
quantity (NP = 5D, junior/senior split, 1/sqrt(D) terms) resolving from the actual run dimension,
exactly as E3's arms did.

| Cell | Boundary shift | Runs at | Transplanted profile | Execution |
|---|---|---|---|---|
| b20_lo  | 20 -> 10  | D = 10  | the middle-tier set, `pub_overrides(30)` | 15 new runs |
| b20_hi  | 20 -> 31  | D = 30  | the low-tier set, `pub_overrides(10)`    | REUSED: identical by construction to E3's U-low arm at D = 30 (51 runs already promoted); not re-executed |
| b50_lo  | 50 -> 30  | D = 30  | the structure-tier set, `pub_overrides(50)` | 15 new runs |
| b50_hi  | 50 -> 51  | D = 50  | the middle-tier set, `pub_overrides(30)` | 15 new runs |
| b100_hi | 100 -> 101| D = 100 | the T2 set, `pub_overrides(50)`          | 15 new runs |

**Coverage disclosure, fixed now.** The T2/T3 boundary is tested one-sided (101 only): a lower-side
perturbation large enough to move D = 100 out of its tier would collapse adjacent boundaries, and no
official CEC2017 dimension sits between 50 and 100. This is disclosed rather than patched with a
non-official benchmark dimension.

**Protocol.** CEC2017, the 29 scored functions, MaxFES = 10^4 D, the unified seed schedule
(`seed 20240620`), 15 runs per function for the new cells — the FIRST 15 runs of the schedule, so
every run pairs with the frozen tiered leg. Threads pinned single as the campaign driver pins them.
Staging under `results/_revision/e5_*`; promotion to an additive evidence release is a separate,
deliberate step, as for E1–E4.

**Analysis, fixed before results.** Per-function means over the runs each cell has. Pairing against
the frozen tiered leg restricted to the SAME first 15 runs per function (the reused b20_hi cell
pairs on its full 51). Paired two-sided Wilcoxon on the 29 per-function mean differences under the
canonical near-zero rule of Amendment A5 (|d| < 1e-8 zeroed, zero_method='wilcox'); **Holm over the
five prespecified boundary contrasts (m = 5)**; W/T/L at tolerance 1e-8; rank-biserial and A12 as
descriptive companions; panel ordinal re-ranked with only the DT-GSK column substituted, per
dimension. No other comparison belongs to the confirmatory family.

**Pre-committed outcome wording.**
- Not separated: "the reported standing at D = <d> is insensitive to the tested boundary shift."
- Transplant significantly better: "the tested boundary shift improves DT-GSK at D = <d>; this
  identifies boundary-level sensitivity at that dimension and does not identify a responsible
  mechanism, because the shift changes the complete resolved profile."
- Transplant significantly worse: "the tested boundary shift degrades DT-GSK at D = <d>; the shipped
  boundary is supported at that dimension in the tested direction."
Whatever the split, all five cells are reported, and interpretation is limited to boundary
sensitivity — no cell licenses a claim about any individual constant or mechanism.

**Outputs.** Raw staging per cell; on promotion: an additive release with checksums, an
`e5_threshold_sensitivity.json` analysis bundle, Supplementary Section S9.5 with Table A47, a
limitations update replacing "thresholds unvaried" with the executed coverage, and the revised
R2.7 response.

## Amendment A5 (2026-08-28) — canonical near-zero rule; a revision-analyzer deviation corrected

**This is a correction record, not an outcome-blind registration, and it says so.** The direction of
its main consequence was already known when it was filed.

**The defect.** The manuscript states one tie rule for across-function Wilcoxon tests: differences
with |d| < 1e-8 are discarded before ranking (performance.tex, statistics protocol). The primary
analysis pipeline implements exactly that (phase6_run_analysis.py applies the 1e-8 band before
calling `wilcoxon_paired`). The round-one revision analyzer (`analyze_revision_experiments.py`)
did NOT: it passed per-function means to `wilcoxon_paired` directly, which excludes exact zeros
only. E1–E3 statistics were therefore computed under a different convention than the paper states
and the primary tables use.

**The rule, fixed here for everything.** |d| < 1e-8 is zeroed and excluded before ranking
(zero_method='wilcox'), two-sided, for every across-function Wilcoxon in the paper, the supplement,
and the revision experiments. W/T/L keeps its stated absolute tolerance of 1e-8. Regression tests
pin both (a 5e-9 pair must be excluded; a large-magnitude pair must not be).

**Known consequence, stated rather than discovered.** Recomputing E1 under the stated rule moves
eigenframe-versus-coordinate at D = 100 from p = 0.054296 (n = 29) to p = 0.048869 (n = 28, one
within-band function excluded), which crosses alpha = 0.05; the D = 50 contrasts are unchanged to
the printed precision. The manuscript's current "not separated at D = 100" wording is therefore
convention-dependent and will be regenerated under the canonical rule, together with every E1–E3
value, Tables A43–A45, and the dependent prose and response text. Any decision that changes in that
regeneration beyond the one named here will be recorded in this file by a further amendment.
