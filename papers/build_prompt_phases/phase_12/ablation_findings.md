# Phase 12 - Scaffold Ablation Findings (X-ABL-01)

**Study id:** `abl-rel-2026-07-16` · **Suite:** CEC2017 · **Dims:** D10/D30/D50/D100 · **Runs:** 51 · **Functions:** 29 (F2 excluded)
**Immutable release:** `benchmarks/cec_reference_results/_ablation/scaffold/`
**Machine-readable:** `papers/build_prompt_phases/phase_12/ablation_results/`

> **51-run regeneration (2026-07-16).** This revision supersedes the 25-run findings of
> `abl-rel-2026-07-11` (recoverable via git history). The cells were fully rerun with the
> post-fix binary (C006 final-polish incumbent + M038 graph-backend corrections) at 51 runs,
> matching the primary panel's power. Membership of the Holm-significant set changed:
> `no_localsearch@D50` dropped out; `no_bse@D30` entered.

> This document reports **descriptive** and **within-dimension inferential** findings only. It is
> supplement-S6 material and does **not** enter the frozen main text, abstract, highlights,
> conclusion, or cover letter.

## Scope caveats (read first)

1. **SGSM is OFF in every cell** (`interaction_graph_enabled=false`, including the `baseline`).
   This study **cannot** establish the effect of the SGSM/ISM interaction-structure memory - that
   is the **separate** X-ABL-02 overlay campaign, completed at 51 runs and reported in
   Supplement S6.5 (see `_ablation/overlay/analysis/overlay_findings.md`).
2. **Remove-one deltas are CONDITIONAL contributions** - each number is the effect of removing one
   component *given all other components enabled and SGSM off*. They are **not** independent causal
   effects and do not decompose additively.
3. **No cross-dimension averaging where signs differ.** Several mechanisms flip sign across
   dimensions (ACE, linkage); a pooled mean would be meaningless.
4. **Multiple-comparison correction is within-dimension** (Holm across the 6 disabled cells at each
   D; alpha = 0.05). Only 4 of 24 (cell, dimension) contrasts survive Holm.
5. **`geomean_error_ratio` can be inflated** by a few near-optimum functions; always read it
   alongside the win/tie/loss counts, the median relative change, and the rank delta.

Freeze reconfirmed at analysis time: the frozen optimizer core is byte-locked
(profile-lock and byte-stability regressions PASS); the manuscript freeze manifest is in its
documented pending-refreeze state following the evidence regeneration
(`papers/governance/_pending_refreeze.json`).

## Headline: largest conditional degradation when a component is removed

`delta_rank` = cell mean-Friedman-rank minus baseline (larger positive = removing that component
degrades performance more, conditionally). `[SIG]` = Holm-significant within that dimension.

| Dim | Friedman p | 1st (largest degradation) | 2nd | 3rd | rank-neutral / removal-helps |
|----|----|----|----|----|----|
| **D10**  | 1.8e-06 | **no_ace +2.84 [SIG]** (Holm 1.1e-3) | no_psr +1.05 | no_bse +0.86 | no_linkage +0.02 |
| **D30**  | 2.5e-08 | **no_psr +2.90 [SIG]** (Holm 4.4e-3) | **no_localsearch +2.03 [SIG]** (Holm 1.4e-3) | **no_bse +1.31 [SIG]** (Holm 3.4e-2) | no_arch +0.14 |
| **D50**  | 5.8e-03 | no_localsearch +1.69 (Holm 0.12, ns) | no_psr +1.40 (ns) | no_ace +1.19 (ns) | no_linkage +0.02 |
| **D100** | 3.5e-02 | no_localsearch +1.38 (ns) | no_psr +0.95 (ns) | no_bse +0.48 (ns) | no_ace **-0.12** · no_linkage **-0.22** |

Only four (cell, dimension) contrasts are Holm-significant: **no_ace@D10, no_psr@D30,
no_localsearch@D30, no_bse@D30**. At **D50 and D100 nothing survives Holm** (Friedman signal
weakest at D100, p = 0.035); those orderings are descriptive only.

## Per-mechanism conditional findings (across dimensions)

- **ACE bandit control (`no_ace`) - the low-dimensional backbone.** Dominant and the *only*
  Holm-significant effect at D10 (delta_rank **+2.84**, geometric-mean error **3.24x** worse,
  median +85.9%, 24/29 functions worse). Its conditional value fades at mid dimension (D30 +0.28
  ns, D50 +1.19 ns) and is mildly **negative at D100** (delta_rank -0.12 ns, geomean 0.70x, 16/29
  functions *improve* when ACE is removed, best_count 15/29). Reads as a low-D exploration
  controller.

- **NLPSR population reduction (`no_psr`) - the mid/high-D population backbone.** The largest and
  a Holm-significant degradation at D30 (delta_rank **+2.90**, geomean 1.62x, median +30.6%,
  24/29 worse). Remains the second-largest degradation at D50 (+1.40, Holm 0.12, ns) and
  D100 (+0.95 ns), i.e. a positive contributor at scale though not Holm-significant beyond D30.

- **Eigenframe local-search polish (`no_localsearch`) - the most consistent mid/high-D
  contributor.** Holm-significant at **D30** (+2.03) and the single largest degradation at both
  **D50** (+1.69, Holm 0.12, ns) and **D100** (+1.38, ns). **Negligible at D10** (+0.28, geomean
  1.01x, engaged on only 21/29 functions), consistent with the local search being far more
  consequential once dimension rises.

- **BSE budget-safe escape (`no_bse`) - consistently positive, significant at D30.** Positive
  delta_rank at *all* four dimensions (+0.48 to +1.31) and Holm-significant at D30 (+1.31,
  Holm 3.4e-2; median +0.97%, 19/29 worse); central effects elsewhere are small (median <= 0.6%).
  Engages progressively fewer functions at high D (identifiability 23->21->20 across
  D30/D50/D100), consistent with a safety mechanism that fires on a subset of runs.

- **Linkage-aware block crossover (`no_linkage`) - aggregate-neutral, sign-mixed per function.**
  Rank-neutral or better at every dimension (|delta_rank| <= 0.34; **negative at D100** -
  removing it slightly *improves* rank; best_count 8/29 at D10, 7/29 at D50). The D50
  geometric-mean ratio (2.09x) is driven by a **handful** of functions while the median change is
  +0.4% and 14/29 functions improve - a specialist mechanism, large on specific composition
  classes but neutral in aggregate. A textbook "do not average across dimensions" case.

- **Distance-thresholded elite archive (`no_arch`) - minor at every dimension.** Small magnitude
  throughout (+0.07 to +0.38), never Holm-significant, medians ~0%. (The 25-run release's
  "removal improves rank at D30" reading did not persist at 51 runs: D30 is +0.14, mildly
  harmful.) Engages fewer functions at high D (20/29 at D100).

## Synthesis (conditional, SGSM-off)

- The mid/high-D backbone is **NLPSR + the local-search polish** - together with BSE, the only
  mechanisms that reach Holm significance beyond D10, all at D30. **ACE** is the low-D backbone
  (dominant, significant at D10 only).
- **BSE** is a consistently-positive safety contributor at every dimension, Holm-significant at
  D30.
- **Linkage** and **archive** are aggregate rank-neutral or sign-mixed across dimensions; their
  conditional contribution does not have a stable sign, so per-dimension reporting is mandatory.
- The dimension-structured picture (ACE at low D; NLPSR/local-search at mid/high D) is coherent
  with the frozen dimension-gating design, but this study attributes contributions **only**
  conditional on SGSM off.

## Identifiability

All 6 disabled-component cells changed >=1 function's per-run trajectory vs baseline at **every**
dimension (n_active ranges 20-29 of 29). There are **no null-contrast cells** - every toggle was
engaged - so every contrast is identifiable. (BSE and archive engage the fewest functions at high
D; ACE/NLPSR/linkage/polish the most.)

## Correction-exception (G0) disposition - NOT TRIGGERED

Every Holm-significant scaffold delta is **favorable** (removing a component degrades performance).
Under the one-directional G0 guard, favorable results are **supplement-only and may never upgrade a
frozen claim**; only an **unfavorable** pre-registered contradiction can force a text-only
narrowing. None of the pre-registered contradiction conditions is met:

- **T-2 (LM-02, low-D gating):** no component is shown to *cause* the low-D weakness; the low-D
  significant effect (ACE) shows ACE *helps* at low D. No narrowing.
- **T-3 (MT-03, NLPSR D100 floor):** at D100 NLPSR is **not** dominated by its removal (removing it
  is non-significantly *harmful*, delta_rank +0.95). Floor rationale stands; not upgraded.
- **T-4 (MT-06/07, BSE):** BSE is never harmful (positive delta_rank at all D; Holm-significant
  favorable at D30). A positive result is supplement-only.
- **T-5 (MT-09/C2, polish):** the dedicated polish toggle is AB-03 (separate); the AB-01
  `no_localsearch` favorable result is supplement-only and does **not** upgrade C2 in the frozen
  paper. (Naming note for supplement authoring: disambiguate the AB-01 `local_search` cell from the
  C2 eigenframe *final* polish that AB-03 isolates.)

No claim is upgraded (G0). The manuscript's post-regeneration number re-verification and freeze
refreeze are tracked in `results/_finalize/finalize_report.md`.
