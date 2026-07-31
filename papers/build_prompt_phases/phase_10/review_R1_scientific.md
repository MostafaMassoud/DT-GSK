# Review R1 — Scientific (adversarial, Q1 standard)

**Manuscript:** *An Interaction-Structure Memory for High-Dimensional Gaining-Sharing Knowledge Optimization* (DT-GSK), MDPI *Algorithms*, submit mode, 34 pp.
**Reviewer role:** R1 — scientific merit. Charge: importance/problem-specificity, contribution novelty boundary (C1–C4), same-family scope discipline, mechanism distinction, baseline strength, external validity, honesty of losses/limitations.
**Artifacts read:** `papers/main.tex` (title/abstract/back matter), `sections/{introduction,related_work,proposed_algorithm,performance,conclusions}.tex`, `governance/claims_evidence_matrix.csv` (50 rows), `governance/comparability_audit.md`, `build_prompt_phases/phase_06/negative_findings.md`, plus typeset `papers/DT-GSK.pdf` p.1 (source/typeset parity confirmed).

**Overall recommendation: MAJOR REVISION.**

---

## Summary judgment

This is an unusually disciplined and honest manuscript. Its scope-control, evidence provenance, and disclosure of unfavorable cells are exemplary and materially above the norm for this literature: every superiority sentence carries the "within the GSK family panel" qualifier; the headline overall rank is explicitly labeled a descriptive across-dimension mean with *no cross-dimension test attached*; the significant CEC2011 loss to eGSK, the losing head-to-head records at D≥30, the never-Nemenyi-separable relationship with eGSK, the non-monotone dimension trend, the APGSK evidence gap, and the eGSK solver-substitution are all surfaced rather than buried. On honesty the paper is close to a model.

The scientific weaknesses are structural rather than presentational, and they are what block acceptance at a Q1 bar:

1. **No external baseline of any kind.** The 7-member panel is entirely within the GSK family, and every one of the six comparators is authored or co-authored by the paper's second author. There is no L-SHADE-class / CMA-ES / jSO / SOTA-DE anchor. A reader cannot tell whether "best of 7 GSK variants" locates DT-GSK anywhere near the broader state of the art.
2. **The only strong in-family baseline is never beaten in a separable way — and it is a port.** Against eGSK, DT-GSK loses the head-to-head at D30/D50/D100 (11-2-16, 13-0-16, 12-0-17), significantly loses on CEC2011, and is never Nemenyi-separable at any CEC2017 dimension. The "best overall rank" is therefore carried by beating the weak family members. Moreover eGSK here is a SciPy-SLSQP re-port whose polish solver differs from the published fmincon implementation and whose numbers differ from the published tables, so even this one real comparison is against a reimplementation.
3. **The paper's own central mechanism is not shown to help.** ISM (C1) and the eigenframe polish (C2) — the named scientific core — are gated to D≥50 and per-component causal attribution is *deferred to a Phase-12 supplement*. The main text can only say results are "consistent with" the design intent. So the paper asserts a gap and a mechanism but demonstrates no causal payoff for the mechanism it is named after.

None of these is fatal in isolation, and the work is rigorous enough that the fixes are achievable (add an external anchor; either promote the ablation or further soften the importance framing; sharpen the mechanistic distinction from covariance learning). Hence major revision rather than reject.

---

## Category-by-category

### Importance / problem-specificity — 3/5
The problem ("learn and exploit accepted-move interaction structure inside GSK, at no extra objective evaluations, at high dimension") is crisply specified and genuinely under-served *within the family*. But importance is undercut from two sides: (a) the payoff mechanism's contribution is deferred (Phase 12), so the paper cannot show the specific problem it targets is worth solving in performance terms; and (b) the strongest family member (eGSK) already matches or beats DT-GSK wherever the headline mechanisms are active (D≥50), so the practical importance of closing this specific gap is not established. The paper is important as a *methodology/reproducibility* exemplar more than as an algorithmic advance. Ticket R1-1.

### Contribution novelty boundary (C1–C4) — 3/5
The boundary discipline is excellent and honest: C1 (ISM) is the novel primitive; C2 is a modest recombination (direct search on a learned basis); C3 is explicitly labeled mostly MOD with only ARGP claimed original at specificity; C4 is engineering/reproducibility. Credit for the honest MOD/ORI labeling. The *substance* of the novelty is thin, however, and the mechanistic distance from CMA-ES is smaller than the prose implies (see mechanism distinction). The genuinely new content reduces to (i) ISM as a decaying signed accepted-move interaction matrix and its discrete exploitation channels, and (ii) ARGP. Ticket R1-2.

### Same-family scope discipline — 4/5
Best dimension of the paper. The "within the GSK family panel" qualifier is applied consistently across abstract, results, discussion, and conclusions; NFL is invoked to bound scope; CEC2013 is called a "second comparison suite," never "independent/holdout/validation." Two blemishes keep this from a 5: the **title** claims "High-Dimensional" optimization while the evidence ceiling is D=100 and the paper explicitly disclaims LSGO — "high-dimensional" is used in the field for n≈1000, so the title over-reaches relative to the paper's own bounds; and the **abstract** presents "best overall CEC2017 Friedman mean rank … (2.48 of 7)" without the "descriptive aggregate, no cross-dimension test" qualifier that the body is careful to attach. Tickets R1-3, R1-4.

### Baseline adequacy — 2/5
The central scientific weakness. (a) **No external comparator.** An L-SHADE-class or CMA-ES anchor is standard practice and is absent; without it the panel is self-referential and the reader cannot calibrate the family against the field. (b) **The one strong baseline is unbeaten.** DT-GSK does not statistically separate from eGSK anywhere it matters and loses the head-to-heads and CEC2011. (c) **Self-authored panel.** Per the COI statement, the second author originated GSK and co-authored all five variants — the entire baseline set is the authors' own prior work, which makes an independent external anchor not optional but necessary. (d) **The strong baseline is a port** (SLSQP≠fmincon; numbers differ from published), disclosed as LM-04 but material. Transparency about these does not remedy them. Ticket R1-5 (major; missing evidence — flag, do not silently alter numbers/algorithm).

### External validity — 3/5
Findings are bounded to one family, three CEC suites, D≤100, and a **single host/environment** (the comparability audit records "No independently-verified (second-environment) cell exists" as a disclosed limitation, but this threat is not surfaced in the manuscript's main-text limitations). The one strong baseline being a re-port further limits transfer of the comparison to the actual published eGSK. The generalization claim is honestly disclaimed, but as scored, external validity is genuinely low: essentially everything lives inside one lab's ecosystem and one machine. Tickets R1-5 (shared), R1-6.

### Limitations completeness — 4/5
Among the most complete limitations sections I have reviewed: five numbered limitations plus statistical-scope bounds, APGSK gap, runtime-cost admission, eGSK-port comparability, D=100 ceiling, non-monotone trend, and robustness divergences. Two disclosed threats do not make it from the governance audits into the main-text limitations: (i) the **single-environment** reproducibility threat, and (ii) the **self-authored-baseline** issue is confined to the COI statement and not framed as a scientific threat to the comparison. Ticket R1-7 (minor).

---

## Mechanism distinction (specific technical concern feeding R1-2)

ISM accumulates a signed D×D matrix from accepted-move deltas with EMA decay (λ=0.95), and the eigenframe polish **eigendecomposes that matrix and searches along its eigenvectors**. That is operationally very close to CMA-ES, which learns a covariance C from selected steps at no extra objective evaluations and samples along the eigenbasis of C. On the paper's own four axes (update trigger, evaluation cost, what is learned, how exploited), ISM and CMA-ES **coincide on two** (online trigger; zero extra evaluations — the paper says so itself in BG-04) and differ on the other two (soft signed pair graph vs full sampling covariance; discrete block/subspace/one-polish exploitation vs reshaping every sample). The prose ("not a sampling covariance") risks reading as a distinction-without-much-difference precisely because the terminal polish performs the covariance-eigenbasis operation CMA-ES is built on. The novelty is real but rests mainly on the *discrete, decaying, signed, accepted-move-only* framing and the exploitation channels — not on the learning being fundamentally new. The manuscript should say this outright rather than leaning on the four-axis table to imply a larger gap.

---

## Tickets (structured JSON mirrors this list)

- **R1-1 (major, analysis):** Importance rests on a mechanism whose contribution is deferred. Either promote a minimal ISM/polish ablation into the main text or reframe the contribution explicitly as methodological/reproducibility-first.
- **R1-2 (major, method_description):** Sharpen the mechanistic distinction of ISM (and the eigenframe polish) from CMA-ES/covariance learning; acknowledge the accepted-move second-moment matrix is covariance-like and locate novelty in the discrete exploitation + signed/decaying/accepted-move framing.
- **R1-3 (minor, editorial):** Title "High-Dimensional" overstates relative to the D=100 ceiling and the explicit no-LSGO disclaimer; qualify or soften.
- **R1-4 (minor, prose):** Abstract's "2.48 of 7" lacks the "descriptive across-dimension aggregate, no cross-dimension test" qualifier the body uses; add it.
- **R1-5 (major, missing_evidence):** Add at least one external, non-GSK, L-SHADE-class (or CMA-ES) anchor under the same locked protocol so the family — and thus DT-GSK — can be calibrated against the field; the self-authored, within-family-only panel is not an adequate baseline for a superiority-flavored claim. Flag; do not silently alter the frozen numbers/algorithm.
- **R1-6 (major, method_description):** State plainly that the only strong baseline (eGSK) is a SLSQP re-port differing from published fmincon eGSK, and that DT-GSK does not statistically separate from it; ensure no headline framing implies otherwise.
- **R1-7 (minor, prose):** Surface the single-environment reproducibility threat and the self-authored-baseline caveat as explicit main-text limitations (both are in the governance audits/COI but not in the limitations paragraph).
