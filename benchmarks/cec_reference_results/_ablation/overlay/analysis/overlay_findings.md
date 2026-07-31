# X-ABL-02 SGSM-overlay — findings (CEC2013 D50, 51 runs, 28 functions)

> **Release note.** These findings describe the **51-run regeneration**
> (`abl-rel-2026-07-16`, post-fix binary: C006 final-polish incumbent + M038
> graph-backend corrections applied). They supersede the 25-run findings of
> `abl-rel-2026-07-13`, whose text is recoverable via git history. The verdicts
> are unchanged (SGSM null; polish significant); the point estimates moved.

**What this is.** The direct SGSM isolation reviewers R1/R6 requested. Reference cell `full`
(SGSM on) is compared against three single-toggle cells on **per-function mean final error**
(28 functions, D50). Test = paired Wilcoxon signed-rank across functions (the frozen
GSK-family method in `gsk_family.analysis.statistics.wilcoxon_paired`, used by
`papers/scripts/generate_ablation_matrix.py`); **Holm** correction over the pre-registered
3-comparison X-ABL-02 family; Friedman ranks over all 4 cells; Vargha–Delaney A12 on raw runs.
Every repo Wilcoxon p-value reproduces under `scipy.stats.wilcoxon(zero_method="wilcox")`
(cross-check recorded in `overlay_contrasts_cec2013_D50.json`).

## Results

**Friedman omnibus (4 cells × 28 functions):** χ² = 13.40, **p = 3.84e-03** — the cells differ.
**Mean-rank ordering, best→worst (lower = better):**
`full (2.036)  <  no_sgsm (2.232)  <  no_adaptive (2.518)  <  no_finalpolish (3.214)`.

| Contrast (isolates) | W/T/L (full better / tie / full worse) | Wilcoxon p_raw | **Holm p** | sig. | Δrank vs full | mean A12 (full vs cell) | direction |
|---|---|---|---|---|---|---|---|
| `full` vs `no_sgsm` — **direct SGSM** | **13 / 3 / 12** | 0.6474 | **0.6474** | **no** | +0.196 | 0.419 | rank leans mildly to SGSM-ON; raw-run effect size leans to SGSM-OFF — a null either way |
| `full` vs `no_adaptive` — adaptive gate | 15 / 5 / 8 | 0.1173 | 0.2345 | no | +0.482 | 0.518 | gate helps **directionally**, not sig. |
| `full` vs `no_finalpolish` — **final polish** | **21 / 4 / 3** | 5.8e-04 | **0.00173** | **yes** | +1.179 | 0.638 (medium) | polish **significantly helps** |

(W/T/L uses the exact per-function-mean comparison in the contrasts JSON; Wilcoxon `n_pairs`
= 25/23/24 after the standard zero-difference drop.)

## Headline findings — reported honestly

1. **SGSM (full vs no_sgsm): NO significant standalone D50 benefit — a clean null.**
   Holm p = **0.647** (raw 0.647); W/T/L **13/3/12** (as even as it can be at n = 28). At 51
   runs the mean-rank point estimate leans mildly to SGSM-ON (Δrank +0.20, and `full` holds the
   best mean rank of the four cells), while the raw-run effect size leans to SGSM-OFF
   (mean A12 = 0.419) — the two point estimates disagree in sign and neither approaches
   significance. The 25-run release's "mildly net-negative" reading does not persist; the
   defensible statement is the null itself. The loss direction remains concentrated in the
   same hybrid functions where SGSM-on is markedly worse (per-function A12 ≈ 0 on F22, F14,
   F17, F11, F19).

2. **Adaptive confidence gate (full vs no_adaptive): directional but NOT significant.**
   Full beats `no_adaptive` on 15/28 functions (W/T/L 15/5/8, Δrank +0.48, A12 0.52), but Holm
   p = **0.235**. The gate contributes in the expected direction within the SGSM subsystem; the
   evidence does not reach significance at D50.

3. **Eigenframe final polish (full vs no_finalpolish): SIGNIFICANT benefit.**
   The only contrast that survives Holm — p = **0.00173** (raw 5.8e-04), W/T/L **21/4/3**, Δrank
   +1.18, medium effect (A12 0.64). At CEC2013 D50 the bundled algorithm's edge is carried by the
   final polish, not by SGSM itself. Note the polish is measured here **un-handicapped** (the
   C006 stale-incumbent defect is fixed in this release's binary).

**One-line answer to the three pre-registered questions.** Does SGSM show a significant D50
benefit? **No (null; p_holm 0.647).** Does the adaptive gate? **No (directional only;
p_holm 0.235).** Does the final polish? **Yes (p_holm 0.0017; W/T/L 21/4/3).**

## Interpretation guard (conditional, remove-one; do not over-read)

These are **remove-one contributions conditional on all other components present** — not
independent causal effects; signs need not add across dimensions or suites (see the X-ABL-01
release README and the preregistration §1). The single significant effect (polish) and the SGSM
null are both **CEC2013-D50-only** statements.

## Mapping to `phase_10/ablation_correction_triggers.md` (one-directional: narrow only)

- **T-1 · IN-02 / LM-02 / MT-05·C1 — TRIGGERED (narrow), as in the 25-run release.** The
  contradiction condition ("SGSM isolation shows no significant D≥50 benefit") is met: no
  significant standalone benefit at 51 runs. (The 25-run release's additional "net-negative"
  arm no longer holds — the 51-run rank point estimate leans mildly positive — but the
  narrow-only correction stands on the null alone.) Correction owed **in the Phase-12
  supplement**: state plainly that the direct SGSM isolation did **not** confirm a standalone
  D50 benefit; keep high-D behavior described as a property of the **bundled** D≥50 tier, and
  narrow the C1 framing accordingly. Per **G0** this can only *narrow* — it must **not** be
  back-ported to upgrade any shipped main-text claim, and a favorable component (the polish)
  may **not** be used to upgrade C1/IN-02/C2 to causal wording in the frozen paper.
- **T-5 · MT-09 / C2 (polish) — NOT triggered.** The "no measurable effect at any tier"
  contradiction does **not** hold: the polish is significant at D50. No editorial demotion of C2
  is forced. But **G0** confines this positive result to the supplement (X-ABL-02 / AB-03); it does
  not convert C2 into a validated-efficacy headline in the shipped manuscript.
- **Net effect on claims:** the overlay **narrows** the SGSM/C1 story and **leaves C2 intact**
  (supplement-only support). It inflates nothing.

## Machine-readable outputs (`overlay/analysis/`)

- `ablation_overlay_rank_summary_cec2013_D50.csv` — frozen-schema rank matrix from
  `papers/scripts/generate_ablation_matrix.py --suite cec2013 --dimension 50 --full-cell full`
  (`cell, mean_rank, delta_rank_vs_full, best_count, n_funcs, wilcoxon_p, holm_p, significant`).
- `overlay_contrasts_cec2013_D50.json` — full per-contrast record: repo Wilcoxon + scipy
  (`wilcox` and `zsplit`) cross-checks, Holm family, W/T/L, direction, Friedman, per-function A12.
- `overlay_per_function_means_cec2013_D50.csv` — the 28×4 per-function mean-error matrix with
  per-function W/T/L labels (transparent basis for every number above).
