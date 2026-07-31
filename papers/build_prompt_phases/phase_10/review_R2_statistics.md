# Review R2 — Statistics

**Manuscript:** An Interaction-Structure Memory for High-Dimensional Gaining-Sharing Knowledge Optimization (DT-GSK)
**Target:** MDPI *Algorithms* (submit mode)
**Reviewer role:** R2 — statistical methodology (adversarial, Q1 standard)
**Artifacts read:** `papers/DT-GSK.pdf` (34 pp), `papers/supplementary.pdf` (32 pp), `papers/sections/performance.tex`, `papers/sections/proposed_algorithm.tex`, `papers/scripts/phase6_run_analysis.py`, `papers/governance/claims_evidence_matrix.csv`, `papers/build_prompt_phases/phase_06/negative_findings.md`, evidence release `rel-2026-07-10-262fc16c9`.

---

## Summary judgment

This is an unusually disciplined statistical treatment. The framework is textbook-Demšar (per-dimension Friedman + Iman–Davenport, omnibus-gated Nemenyi, pairwise Wilcoxon + Holm, VD A12, BCa CIs), the overall across-dimension rank is scrupulously presented as a **descriptive mean with no test attached** (and the governance matrix explicitly *blocks* calling it Iman–Davenport-corrected), the r01/r04/r05 robustness DIVERGE verdicts are disclosed in the body and supplement, the APGSK run-level gap is handled by disclosed-unavailable/never-imputed rows with a clean function-level fallback, and no per-component causal claim is made anywhere in the main text. The CD value reproduces exactly (q₀.₀₅=2.949, CD=2.949·√(7·8/(6·29))=1.673).

The defects are **not** errors in the numbers and **not** wrong tests — every frozen fact I was asked to hold the paper to checks out. They are **method-description / disclosure gaps** that a Q1 statistics referee will demand closed before acceptance, all fixable in prose without touching any number or the frozen algorithm:

1. The paper never states how zero-differences are handled in the Wilcoxon signed-rank test, nor whether p-values are exact or normal-approximation-with-continuity — material on a suite where many low-D functions are solved to 0 by both algorithms (MAJOR).
2. The A12 reported in the headline Table 8 is computed on the **29 per-function means** (the same unit as the across-function Wilcoxon), not on run-level distributions; this is a *different object* from the run-level A12/Cliff/BCa effect-size workbook, and the VD 0.56/0.64/0.71 magnitude thresholds are being applied to a function-mean summary. The basis is not disclosed (MAJOR).
3. Two minor framing items: the "17 of 24 significant wins" tally spans four independent Holm families with no joint FWER control; and the BCa CI resamples pre-computed midranks (unusual, though disclosed).
4. The deferred-ablation sentence and one interpretation sentence soft-attribute the D≥50 gains to "the interaction-structure memory," which is one of several mechanisms co-gated at D≥50 — a confound worth a hedge (minor; motivates Phase 12).

Recommendation: **minor revision.** No fatal statistical flaw; the required fixes are all prose/method-description and do not disturb the frozen evidence.

---

## Category-by-category findings

### 1. Endpoint / units / pairing / independence — SCORE 4
- Endpoints are unambiguous and per-suite: CEC2017/CEC2013 = error `f−f*` with `<1e-8→0`; CEC2011 = raw best objective (NaN error column disclosed on problems without published optima). Units consistent across prose/tables (p. 18, Table 6).
- Pairing is strong and auditable: one optimizer-independent seed formula `s(D,f,r)`, shared runner-generated `X0`, counter-based Threefry, full-schedule recomputation audit (70,813 rows, 0 mismatches). The single DT-GSK self-init exception to shared-`X0` is **disclosed**, not hidden (p. 18–19).
- Independence: functions are treated as the sample unit for the rank tests (standard Demšar convention); the paper does not over-claim function independence, and runs within a cell are independently seeded.
- One residual (disclosed) quibble keeps this at 4 rather than 5: the per-function *representative* is the **mean** over 51 runs, which is outlier-sensitive on heavy-tailed error distributions; the r01 median-re-ranking DIVERGE verdict shows the ordering is sensitive to this choice. It is pre-registered and disclosed, so no mandatory ticket, but a median-based primary is defensible and a referee may ask.

### 2. Multiplicity families (Holm primary; BH exploratory) — SCORE 4
- Clean separation: Holm step-down is the confirmatory correction at **family size 6 per dimension**; Benjamini–Hochberg is explicitly **exploratory**, run-level, released in the workbooks only (p. 19, 24; pipeline `wilcoxon_run_*_exploratory_bh.csv`). This matches the pre-registration and the review mandate exactly.
- Gap (minor): the headline "of the 24 Holm-corrected cells … 17 significant wins … none a significant loss" (p. 21, repeated in Discussion p. 29 and Conclusions p. 30) aggregates **four independent Holm families** (6 comparators × 4 dimensions). FWER is controlled only *within* each dimension; the 24-cell tally is a descriptive count, not a jointly FWER-controlled result. The paper does say "dimensions are never pooled," but the aggregate sentence should say so at the point of the tally.

### 3. Friedman + Iman–Davenport & Nemenyi validity — SCORE 5
- Friedman per dimension over per-function mean errors, k=7, N=29; Iman–Davenport F used for the decision; Nemenyi CD diagrams emitted **only where the omnibus is significant** (p ≤ 2.6×10⁻⁸ at every CEC2017 dimension). Explicit evidence of validity.
- CD reproduces exactly: k=7, N=29, α=0.05 ⇒ CD=1.673 (q₀.₀₅=2.949). The "DT-GSK and eGSK never Nemenyi-separable" statement is correct and conservatively framed (all four gaps 1.36/0.21/0.41/0.34 inside the band).
- Internal validation is strong: the pipeline cross-checks its Friedman ranks against `scipy.stats.friedmanchisquare` with an exact-agreement guard (`ranks_agree_exact`).
- Nemenyi (all-pairs) is more conservative than a Bonferroni–Dunn/Holm control-vs-rest post-hoc; since the pairwise Wilcoxon+Holm already answers control-vs-rest, the extra conservativeness only strengthens the honesty of the "not separable from eGSK" claim. No defect.

### 4. Wilcoxon validity (incl. APGSK function-level-only disposition) — SCORE 3 → MAJOR TICKET
- **APGSK disposition: exemplary.** Run-level records for CEC2017 D10/30/50 are absent (sidecar-overwrite anomaly A2-004); all run-level Wilcoxon/A12/BCa vs APGSK there are emitted as disclosed-unavailable rows, **never imputed**, and the across-function Wilcoxon on per-function means is stated as the *sole* inferential basis (p. 19; Supp. S1; pipeline lines 556, 1955). This is the right call, consistently applied and cross-referenced.
- **Undisclosed zero-handling and approximation (the defect).** The protocol states only "two-sided Wilcoxon signed-rank test … win/tie/loss counts use the tie rule |Δ|<1e-8" (performance.tex 149–159). It does **not** state that zero-differences (|Δ|<1e-8) are **discarded** from the signed-rank statistic (`zero_method='wilcox'`) nor that p-values use the **normal approximation with continuity correction** rather than the exact null distribution — both confirmed in the pipeline (`method="normal_approx_continuity"`, phase6_run_analysis.py 333/359/1879/1946). On CEC2017 low-D, unimodal/simple functions are routinely driven to 0 by multiple panel members, so a non-trivial fraction of the 29 paired differences can be exact zeros; discarding them shrinks the effective n and makes the asymptotic approximation (vs. exact) a consequential, currently-undisclosed choice that directly affects every reported p and its reproducibility. A Q1 stats referee will require this stated and, ideally, the effective post-zero n reported per cell (already in the released R⁺/R⁻ workbooks). Method-description gap, not a numerical error.

### 5. A12 + BCa design — SCORE 3 → MAJOR TICKET (A12) + minor (BCa)
- **A12 basis mismatch / undisclosed unit.** The paper carries two distinct A12 objects that it does not disambiguate:
  - the **effect-size workbook (T03 / RS-08)** computes A12 at `unit_of_analysis="run"` — the conventional Vargha–Delaney stochastic-dominance estimate over 51×51 run pairs per function (pipeline 1052–1096);
  - the **headline Table 8 (`tab:wilcoxon-holm`)** A12 is computed **across the 29 per-function means** (pipeline 2233–2241: "across-function A12 on per-function means"), i.e. the same unit as the across-function Wilcoxon, giving a *single* A12 per (comparator, dimension).
  The Table 8 caption labels the *Wilcoxon* "across-function" but does not state that the accompanying A12 is also over per-function means, and the protocol paragraph presents A12 generically with the VD 0.56/0.64/0.71 small/medium/large thresholds (performance.tex 157–159; Table 8 caption 287–294). Those thresholds were calibrated for sample-level stochastic dominance, not for a 29-value function-mean summary. A referee will read "A12=0.712 vs APGSK at D=100" and reasonably assume run-level dominance; the basis must be disclosed and the two A12 objects kept distinct (or the run-level A12 cited for the effect-magnitude claims).
- **BCa on midranks (minor).** Table A14 resamples the **29 pre-computed function-level midranks** (Supp. S2.4, p. 8–9), i.e. it bootstraps a mean-of-fixed-midranks rather than recomputing ranks within each resample; bias-correction/acceleration on a bounded discrete rank statistic is unusual and the intervals can behave oddly near the rank boundaries. It is disclosed and the point estimates reproduce exactly, and the CIs are used only descriptively ("consistent with the pairwise ties," not as a formal overlap test), so this is a labeling/one-line-justification item, not an error.

### 6. Robustness disclosure (r01 / r04 / r05 divergences) — SCORE 5
- Both mandated divergences are disclosed in the body (Sec. 4.2.3, p. 24) and Supp. S2.4, and itemized in `negative_findings.md` (items 7–8) with explicit **DIVERGE** verdicts: r01 median re-ranking (W/T/L shifts + two comparator swaps), r04 disputed-cell exclusion (D30 GSK/FDB-AGSK swap), r05 unpaired Mann–Whitney companion (8 significant→non-significant transitions, 0 sign reversals, and the 18 emergent unpaired significances noted for completeness). Crucially, the paper states what is *stable* (DT-GSK's own ordinals 1/2/1/1) and what is *not* (comparator orderings). Explicit evidence; no over-claim.

### 7. No causal component claim precedes the Phase-12 ablation — SCORE 4
- The main text makes **no** per-component causal claim: "per-component causal attribution is deliberately not claimed in this paper" (Discussion, p. 29); IN-02's governance record *blocks* "ISM causes/drives/explains the gain"; proposed_algorithm.tex carries the guard comment "NO ablation content; component causality deferred to the Supplementary Materials." The interpretation uses permitted "consistent with the design intent" wording. This is the correct discipline and I confirm the deferral holds.
- Two minor items keep it at 4:
  - **Forward-reference accuracy.** "The individual contribution of each subsystem is evaluated in the Supplementary Materials after the final freeze" (proposed_algorithm.tex 186–187; main p. 12) reads in the present tense as if the ablation is *in* the shipped supplement — but the current `supplementary.pdf` (S1 panel tables, S2 head-to-head, S3 convergence, S4 diagnostics, S5 reproducibility) contains **no** component-ablation section. A reader chasing that pointer will not find it. Reword to make the deferral explicitly prospective (e.g. "will be evaluated in a follow-up supplement").
  - **Soft-attribution confound.** "The high-dimension behavior … is consistent with the intended role of the interaction-structure memory, which is active at D≥50" (Discussion p. 29; IN-02). The D≥50 gate co-activates *several* mechanisms (ISM graph, subspace LS, eigenframe polish, Nmin 12→25, p-split, block size 5→10 — Fig. 3), so associating the D≥50 improvement with "the interaction-structure memory" singles out one bundled change. It is hedged ("consistent with," permitted wording) and is exactly why the Phase-12 ablation is needed, but a one-clause acknowledgement that D≥50 bundles multiple changes would forestall the obvious referee objection.

### 8. Overall rank = descriptive mean, not a pooled test — SCORE 5
- Verified in four independent places: "the unweighted mean of the four per-dimension Friedman mean ranks — a descriptive aggregation with no cross-dimension test attached; the Iman–Davenport correction applies to each per-dimension omnibus, not to the overall row" (p. 20); Fig. 6 caption ("descriptive aggregate, no omnibus test attaches to the aggregate itself"); and the governance matrix RS-01 *blocked wording* = "describing the overall row itself as Iman-Davenport corrected/tested." Arithmetic checks: (2.88+2.50+2.21+2.34)/4 = 2.48; eGSK (4.24+2.29+2.62+2.69)/4 = 2.96. Explicit evidence; exactly the discipline the mandate asks for. Pooled Iman–Davenport is computed only as an internal guard (pipeline ~1670), never presented as a headline.

---

## Frozen-fact conformance check
| Frozen fact | Verdict |
|---|---|
| CEC2017 overall #1 (2.48/7), descriptive mean, not a pooled test | ✔ confirmed, explicitly descriptive |
| D30 #2 behind eGSK (2.50 vs 2.29) | ✔ |
| CEC2011 #2 with Holm-significant loss vs eGSK (pHolm=4.2×10⁻²) | ✔ single Holm-significant unfavorable headline cell, disclosed everywhere |
| ISM–eGSK never Nemenyi-separable (CD=1.673) | ✔ CD reproduces; all four gaps inside band |
| CEC2013 overall #1 (2.80), per-dim 1st/3rd/1st | ✔ |
| APGSK CEC2017 D10/30/50 function-level tests only | ✔ disclosed-unavailable, never imputed |
| Component causality deferred to Phase 12 | ✔ no causal claim in main text |
| Superiority scoped "within the GSK family panel" | ✔ pervasive |

All frozen facts hold. No number, test result, or scope statement contradicts the mandate.
