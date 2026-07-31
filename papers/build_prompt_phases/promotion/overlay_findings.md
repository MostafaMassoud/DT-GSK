# X-ABL-02 SGSM-overlay — findings (CEC2013 D50, 25 runs, 28 functions)

**What this is.** The direct SGSM isolation reviewers R1/R6 requested. Reference cell `full`
(SGSM on) is compared against three single-toggle cells on **per-function mean final error**
(28 functions, D50). Test = paired Wilcoxon signed-rank across functions (the frozen
GSK-family method in `gsk_family.analysis.statistics.wilcoxon_paired`, used by
`papers/scripts/generate_ablation_matrix.py`); **Holm** correction over the pre-registered
3-comparison X-ABL-02 family; Friedman ranks over all 4 cells; Vargha–Delaney A12 on raw runs.
Every repo Wilcoxon p-value reproduced **exactly** under `scipy.stats.wilcoxon(zero_method=
"wilcox")` (independent cross-check).

## Results

**Friedman omnibus (4 cells × 28 functions):** χ² = 16.60, **p = 8.55e-04** — the cells differ.
**Mean-rank ordering, best→worst (lower = better):**
`no_sgsm (1.946)  <  full (2.179)  <  no_adaptive (2.625)  <  no_finalpolish (3.250)`.

| Contrast (isolates) | W/T/L (full better / tie / full worse) | Wilcoxon p_raw | **Holm p** | sig. | Δrank vs full | mean A12 (full vs cell) | direction |
|---|---|---|---|---|---|---|---|
| `full` vs `no_sgsm` — **direct SGSM** | **10 / 3 / 15** | 0.1389 | **0.2345** | **no** | −0.232 | 0.429 | point estimate mildly favours **SGSM-OFF** |
| `full` vs `no_adaptive` — adaptive gate | 15 / 5 / 8 | 0.1173 | 0.2345 | no | +0.446 | 0.532 | gate helps **directionally**, not sig. |
| `full` vs `no_finalpolish` — **final polish** | **20 / 4 / 4** | 7.1e-04 | **0.00213** | **yes** | +1.071 | 0.637 (medium) | polish **significantly helps** |

(W/T/L uses the scale-aware tie band in `win_tie_loss`; Wilcoxon `n_pairs` = 25/23/24 after the
standard zero-difference drop, e.g. F1/F5/F28 where cells tie exactly.)

## Headline findings — reported honestly

1. **SGSM (full vs no_sgsm): NO significant standalone D50 benefit — a null, mildly net-negative.**
   Holm p = **0.235** (raw 0.139); W/T/L **10/3/15**; `no_sgsm` actually holds the *best* mean
   rank (1.95 vs 2.18) and mean A12 = 0.429 (<0.5). Turning the SGSM/ISM interaction-structure
   memory **off** at its own active tier neither helps nor hurts significantly, and the point
   estimate leans slightly toward off. This **replicates the quarantined 4-cell pilot** (pilot:
   p≈0.056, W/T/L 5/10/13 — same "more losses than wins for SGSM-on" direction, same null verdict;
   the fresh 25-run result is, if anything, *less* significant). The per-function matrix shows the
   loss direction is driven by hybrids/compositions where SGSM-on is markedly worse — F11 (34.0 vs
   10.9), F14 (4055 vs 465), F17 (103 vs 55), F19 (8.3 vs 3.6), F22 (4104 vs 294).

2. **Adaptive confidence gate (full vs no_adaptive): directional but NOT significant.**
   Full beats `no_adaptive` on 15/28 functions (W/T/L 15/5/8, Δrank +0.45, A12 0.53), but Holm
   p = **0.235**. The gate contributes in the expected direction within the SGSM subsystem; the
   evidence does not reach significance at D50.

3. **Eigenframe final polish (full vs no_finalpolish): SIGNIFICANT benefit.**
   The only contrast that survives Holm — p = **0.00213** (raw 7.1e-04), W/T/L **20/4/4**, Δrank
   +1.07, medium effect (A12 0.64). At CEC2013 D50 the bundled algorithm's edge is carried by the
   final polish, not by SGSM itself.

**One-line answer to the three pre-registered questions.** Does SGSM show a significant D50
benefit? **No (null; p_holm 0.235; mildly net-negative).** Does the adaptive gate? **No
(directional only; p_holm 0.235).** Does the final polish? **Yes (p_holm 0.0021; W/T/L 20/4/4).**

## Interpretation guard (conditional, remove-one; do not over-read)

These are **remove-one contributions conditional on all other components present** — not
independent causal effects; signs need not add across dimensions or suites (see the X-ABL-01
release README and the preregistration §1). The single significant effect (polish) and the SGSM
null are both **CEC2013-D50-only** statements.

## Mapping to `phase_10/ablation_correction_triggers.md` (one-directional: narrow only)

- **T-1 · IN-02 / LM-02 / MT-05·C1 — TRIGGERED (narrow).** The contradiction condition ("SGSM
  isolation shows no significant D≥50 benefit … or a net-negative SGSM effect") is met on both
  counts. Correction owed **in the Phase-12 supplement**: state plainly that the direct SGSM
  isolation did **not** confirm a standalone D50 benefit; keep high-D behavior described as a
  property of the **bundled** D≥50 tier, and narrow the C1 framing accordingly. Per **G0** this
  can only *narrow* — it must **not** be back-ported to upgrade any shipped main-text claim, and
  a favorable component (the polish) may **not** be used to upgrade C1/IN-02/C2 to causal wording
  in the frozen paper.
- **T-5 · MT-09 / C2 (polish) — NOT triggered.** The "no measurable effect at any tier"
  contradiction does **not** hold: the polish is significant at D50. No editorial demotion of C2
  is forced. But **G0** confines this positive result to the supplement (X-ABL-02 / AB-03); it does
  not convert C2 into a validated-efficacy headline in the shipped manuscript.
- **Net effect on claims:** the overlay **narrows** the SGSM/C1 story and **leaves C2 intact**
  (supplement-only support). It inflates nothing.

## Machine-readable outputs (`promotion/overlay_analysis/`)

- `ablation_overlay_rank_summary_cec2013_D50.csv` — frozen-schema rank matrix from
  `papers/scripts/generate_ablation_matrix.py --suite cec2013 --dimension 50 --full-cell full`
  (`cell, mean_rank, delta_rank_vs_full, best_count, n_funcs, wilcoxon_p, holm_p, significant`).
- `overlay_contrasts_cec2013_D50.json` — full per-contrast record: repo Wilcoxon + scipy
  (`wilcox` and `zsplit`) cross-checks, Holm family, W/T/L, direction, Friedman, per-function A12.
- `overlay_per_function_means_cec2013_D50.csv` — the 28×4 per-function mean-error matrix with
  per-function W/T/L labels (transparent basis for every number above).
