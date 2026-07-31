# Stage 18 — Predicted reviewer-question bank

**Seat:** `s18_reviewers` · **Cycle:** 2026-07-22 · **Target journal:** *Algorithms* (MDPI) · **Package:** HEAD `45248eb31`, release `rel-2026-07-20-67d9345f9`, 39 pp main / 61 pp supplement / 2 pp cover letter.

**How to read this file.** Each entry gives the question a referee is likely to ask, **whether the manuscript can already answer it** (`ANSWERABLE` = the answer is in the shipped package and the referee just needs pointing; `PARTIAL` = the answer exists but the manuscript's wording is weaker or broader than the evidence; `NOT ANSWERABLE` = no admissible evidence exists in the package), and the **author response required**. Every "author response required" line is written so it can be pasted into a response letter after verification. Ticket ids cross-reference `independent_reviewer_reports.md`.

Questions 1–25 are the mandated defaults (§Stage 18, L2760–2787) instantiated on this manuscript. Questions 26–41 are manuscript-specific and are the ones I judge most likely to decide the review.

---

## A. The 25 mandated questions, instantiated

### 1. What exactly is new relative to the closest method?
**Status:** ANSWERABLE, but the framing invites the wrong answer (S18-R1-01).
**Likely phrasing:** "eGSK already adds dual adaptive knowledge factors and a late local polish. What does DT-GSK add that eGSK does not, given the two are never Nemenyi-separable on CEC2017?"
**Response required:** Point to the per-mechanism labelling in `introduction.tex:101–112` and `related_work.tex:275–299`. State plainly: relative to eGSK the additions are (i) operator-level rather than parameter-level adaptation (ACE over five complete `(KF,KR,K_exp)` settings, with ARGP arm-freezing, which the authors did not find in the surveyed family), (ii) a *deterministic, RNG-free, solver-free* endgame in place of eGSK's SQP escape, and (iii) resolution of all control by dimension tier from one hash-frozen configuration. Concede the non-separability from eGSK explicitly — the manuscript already does, at `performance.tex:449–456` and `conclusions.tex:41–50`.

### 2. Why is the identified gap scientifically important?
**Status:** ANSWERABLE.
**Response required:** The gap is "no surveyed GSK variant learns or exploits the interaction structure of its own accepted moves" (`related_work.tex:257–270`). Importance: if such a signal were usable it would be free — it costs no objective evaluations — so a negative result is itself a boundary on a design idea the family would otherwise keep re-attempting. Note that the paper answers the question **negatively** and reports it as a controlled negative result (`conclusions.tex:96–102`).

### 3. Which components are inherited, adapted, or original?
**Status:** ANSWERABLE — this is a strength; make the referee see it early.
**Response required:** Cite the architecture table (`proposed_algorithm.tex:122–150`, categories inherited/scaffold/gated) and the equation registry, where every equation carries an `inherited / modified / original` label and a code anchor. Inherited: junior/senior indices, `K_exp` schedule, gaining–sharing update, midpoint repair, greedy selection. Modified: crossover mask, NLPSR (explicitly "a variant of the APGSK NLPSR schedule, explicitly not claimed as new"), ACE, BSE, archive, restart. Original as claimed: ARGP's acceptance-rate-gated arm freezing, the ISM graph, the eigenframe polish, the 13-substream RNG rail.

### 4. Does the method add computational or objective-evaluation cost?
**Status:** PARTIAL — objective-evaluation cost is fully answered; comparator-relative compute cost is not (S18-R6-01).
**Response required:** Objective evaluations: no — a single budget controller, no second counter, no direct objective path, all polish/escape/local-search/restart probes charged (`proposed_algorithm.tex:774–787`), and all seven optimizers charged exactly `MaxFES`. Compute: DT-GSK's own per-run wall-clock is 4.93 → 41.59 s over `D = 10 → 100` (`tab:runtime`). **Then answer the question the table does not:** state the comparator order of magnitude from `cost_cec2017.csv` with its `NOT-COMPARABLE-ACROSS-ALGORITHMS` qualifier, or state explicitly why it is withheld.

### 5. Were the evaluation benchmarks used during development?
**Status:** ANSWERABLE for *which*, NOT ANSWERABLE for *how much* (S18-R3-01).
**Response required:** CEC2017 is declared the development suite and is selection-exposed; CEC2011 and CEC2013 were not consulted during configuration selection and are corroborative (`performance.tex:103–111`, `supplementary.tex:1148–1169`). Anticipate the follow-up in Q6.

### 6. How were hyperparameters selected and what was the tuning budget?
**Status:** NOT ANSWERABLE as written — **the most dangerous question in the bank** (S18-R3-01).
**Likely phrasing:** "'Several full-panel candidate configurations were compared' — how many is several, on what statistic, and where is the record?"
**Response required:** Supply the count, the selection statistic, and whether comparison used the full 29 × 4 grid or a subset. If the count was not recorded, say so in exactly those words. Do **not** answer with "several" a second time. Note in mitigation that the two held-out suites place DT-GSK second (CEC2011) and third at `D = 30` (CEC2013), i.e. the held-out evidence is mixed rather than uniformly favourable — which is the paper's own honest framing.

### 7. Why were these comparators selected, and which strong alternatives are missing?
**Status:** ANSWERABLE.
**Response required:** The panel is the complete published GSK lineage (GSK, AGSK, APGSK, FDB-AGSK, eGSK, ATMALS-GSK). Missing by design: all non-GSK families. Cite the seventh limitation (`supplementary.tex:1224–1237`), which names L-SHADE-class, CMA-ES and differential grouping as the absent calibrations and states the consequence ("interpretable only within this panel"). Also restate the conflict disclosure here rather than waiting to be asked (Q31).

### 8. Are comparator implementations and budgets genuinely fair?
**Status:** PARTIAL (S18-R2-02).
**Response required:** Budgets: identical `MaxFES`, identical optimizer-independent seed schedule, byte-identical problem instances, identical infeasibility penalty on CEC2011. Two disclosed asymmetries: (i) DT-GSK self-initializes its own `5·D` population from the same seed-paired stream, so pairing is by seed/problem/run not by identical `X0`; (ii) the eGSK port substitutes SciPy-SLSQP for the published `fmincon` SQP. On budget-crossing, state the *verified* scope precisely: DT-GSK truncates before evaluating; the six MATLAB-faithful ports evaluate the terminal batch and count only the in-budget prefix; a regression probe shows the uncounted rows are inert — and say on what configuration the probe runs.

### 9. What is the experimental unit?
**Status:** ANSWERABLE.
**Response required:** For the primary inference the unit is the **function** (29 paired per-function mean errors per dimension for the across-function Wilcoxon; 29 blocks for Friedman). Run-level analyses are companions. Dimensions are never pooled. Runs are paired by `(seed, problem, run index)`.

### 10. Why is the chosen statistical test valid?
**Status:** ANSWERABLE.
**Response required:** Two-sided Wilcoxon signed-rank on paired per-function means (no normality assumption, valid under symmetry of paired differences), zeros discarded under `zero_method='wilcox'` with the tie band `|Δ| < 1e-8`, normal approximation with continuity correction, effective post-zero `n` recorded in the released `R+/R−` workbooks. Friedman with Iman–Davenport for the multi-algorithm view, Nemenyi only where the omnibus is significant.

### 11. How is multiplicity controlled?
**Status:** ANSWERABLE — a strength.
**Response required:** Holm within each dimension, family size 6, `α = 0.05`. The 24-cell 17/7/0 tally is explicitly labelled a descriptive aggregation of four independent within-dimension families, not a jointly FWER-controlled result, and a global-Holm sensitivity is supplied (15 of 24 survive; the two that fall are ATMALS-GSK at `D = 10` and GSK at `D = 30`; zero significant losses under either correction). Benjamini–Hochberg appears only as a labelled exploratory companion.

### 12. What is the practical effect size and uncertainty?
**Status:** PARTIAL — **the table/prose mismatch will be caught here** (S18-R4-01, S18-R4-02).
**Response required:** Fix the text before submission. The tabulated effect size is the matched-pairs rank-biserial `r = (R⁺−R⁻)/(R⁺+R⁻)`, aligned with the paired test; `A12` is a descriptive unpaired companion. Uncertainty on ranks is a seeded BCa *rank-stability* interval, explicitly descriptive because it resamples fixed midranks. Be ready to state that no inferential interval is claimed for the mean ranks.

### 13. Do conclusions change under alternative reasonable analyses?
**Status:** ANSWERABLE — a strength; lead with it.
**Response required:** A prespecified robustness battery is reported *with its divergences*: median re-ranking shifts W/T/L materially (21–4–4 → 17–10–2 vs eGSK at `D = 10`) and swaps two comparator pairs; excluding the disputed APGSK cells swaps GSK and FDB-AGSK at `D = 30`; under the median endpoint DT-GSK's `D = 100` first place becomes an exact tie with eGSK at 2.59. DT-GSK's own ordinals (1/2/1/1) are invariant across every reported variant; comparator orderings are not.

### 14. How are failed runs or missing observations treated?
**Status:** ANSWERABLE.
**Response required:** No run is dropped. CEC2011 infeasible evaluations take the suite's `1e30` penalty identically for all seven. The one evidence gap — APGSK per-run records on CEC2017 available only at `D = 100` at analysis freeze — was declared disclosed-unavailable and never imputed; the function-level across-function test still applies. The records were later recovered deterministically post-freeze and reproduce the frozen summaries exactly; the manuscript conservatively retains the function-level basis and says so in a footnote.

### 15. Why is the reported convergence behavior representative?
**Status:** ANSWERABLE.
**Response required:** The four-function panels were selected by a fixed rule prespecified and frozen before rendering (stratified by function category, difficulty tercile and DT-GSK standing) and the rule *mandates* an unfavourable case. Every curve is the per-checkpoint mean error over all 51 runs — one aggregation basis for all seven curves, no smoothing, no interpolation; the `1e-14` axis floor is display-only. Complete per-function grids for all three suites are in Supplement S3.

### 16. What failure cases or dimensions weaken the method?
**Status:** ANSWERABLE — a strength.
**Response required:** `D = 30` on both CEC2017 and CEC2013 (second and third respectively); CEC2011 overall (second, with the study's only Holm-significant unfavourable headline cell, `p_Holm = 4.2e-2` vs eGSK); the composition class at `D = 10` (class mean rank 3.70, behind three comparators); F26 at `D = 30`, where DT-GSK's best run never reaches the low attractor every comparator reaches; and the non-monotone rank trend (2.88, 2.50, 2.21, 2.34).

### 17. Does ablation isolate components or only show conditional differences?
**Status:** ANSWERABLE — the supplement says so itself.
**Response required:** The scaffold remove-one study is explicitly **conditional** (ISM held off in every cell) and has a dedicated "What This Study Does Not Establish" subsection. The ISM overlay isolation is a separate, directly isolating design (four cells, one shared seed schedule, 51 paired repetitions at `D ∈ {50,100}` plus CEC2013 `D = 50`). Do not let the two be conflated in the response.

### 18. Are component interactions tested?
**Status:** PARTIAL.
**Response required:** Single-toggle contrasts are tested (ISM, adaptive confidence gate, ISM-dependent final polish). Higher-order interactions are not, and the paper does not claim them. Note the one contrast that *is* informative about interaction: the `no_sgsm` cell, in which the polish runs on coordinate axes, is itself null — which is why the significant effect is attributed to the compass endgame as a whole and not to the learned basis.

### 19. Is the method reproducible from the paper and package?
**Status:** PARTIAL — reproducible from the *package*; C1's printed equation is thin (S18-R2-01) and the comparator cross-commit caveat is undisclosed (S18-R5-02).
**Response required:** From the package: yes, and machine-checked (`check_manifest` 15/15, four green validators, 579 cross-format parity rows at 0 FAIL). From the paper alone: the GSK core, ACE, NLPSR, BSE, ISM and the crossover mask are fully specified; the compass polish's step schedule lives in the supplement's operator specification. Disclose that comparator evidence is deterministic within its producing commit but is not bit-reproducible across commits.

### 20. Are source code, data, seeds, and exact commands available?
**Status:** ANSWERABLE (pending the author-side archival DOI, which is out of scope for this cycle).
**Response required:** Implementation, harness, per-run raw CSVs, seed schedules, per-cell environment manifests, the checksummed analysis bundle and the runbook are all released; the seed formula is printed in the protocol table with a 70,813-row recomputation audit at 0 mismatches; MIT for code, CC BY 4.0 for derived data.

### 21. How sensitive are results to parameter values?
**Status:** PARTIAL — **expect pushback.**
**Response required:** There is no parameter-sensitivity sweep, by design: one hash-frozen dimension-aware configuration is shipped and no per-suite tuning exists, so sensitivity would have to be generated outside the frozen protocol. What *is* available: the tie-band sensitivity analysis (Supplement S5), the endpoint (mean vs median) robustness variants, and the component toggles of S6. State this positively — the paper trades sensitivity curves for a single locked configuration evaluated identically on three suites — and do not generate a sweep from unpromoted staging data (§10.11 forbids it).

### 22. Does the method generalize beyond the chosen benchmark?
**Status:** ANSWERABLE (in the negative, honestly).
**Response required:** No generalization claim is made. CEC2013 is "a second comparison suite … [that] carries no independence claim of any kind"; CEC2011 supplies real-world *formulations*, explicitly "not evidence of deployment performance"; the evidence ceiling is `D = 100`.

### 23. What are the time and memory trade-offs?
**Status:** PARTIAL on time (S18-R6-01), ANSWERABLE on memory.
**Response required:** Memory: `O(NP·D)` dominates at every tier (a few MB at `D = 100` with `NP_init = 5D`); the gated interaction state adds three `O(D²)` matrices ≈ half a megabyte at `D = 100`. Time: give DT-GSK's measured per-run cost, the explicit "no complexity improvement over GSK" statement, and then address the comparator-relative gap head-on rather than leaving it to the referee.

### 24. Which conclusion would change if one comparison cell were removed?
**Status:** ANSWERABLE.
**Response required:** Removing the eGSK column: DT-GSK's first places become uncontested and the Nemenyi non-separability caveat disappears — i.e. **eGSK is the cell that carries every qualification in the paper**. Removing APGSK at `D ≤ 50` (the disputed cells): swaps GSK and FDB-AGSK at `D = 30`, DT-GSK's ordinals unchanged. Removing CEC2011: deletes the study's only Holm-significant unfavourable headline. Say all three.

### 25. Why this journal rather than a narrower venue?
**Status:** ANSWERABLE.
**Response required:** The deliverable is not only a ranking: it is a fully specified mechanism, a reproducible within-family evaluation protocol, and a controlled negative result — an algorithms-and-evidence contribution rather than a benchmark-competition entry.

---

## B. Manuscript-specific questions (the ones most likely to decide the review)

### 26. "Table 6 has no `A12` column. What is the reader supposed to look at?"
**Status:** NOT ANSWERABLE as shipped — **fix before submission** (S18-R4-01).
**Evidence:** `papers/tables/T15.tex` header is `p, p_Holm, +, ≈, −, r, Dec.`; `performance.tex:362` and `:365` describe "`A12` effect sizes" and "The `A12` column"; `:409` and `:426` quote `A12` values (0.490, 0.505, 0.472, 0.712) that appear in no exhibit. The values are numerically correct (independently recomputed from `descriptive_stats_cec2017_D*.csv`) but untraceable from the paper.
**Response required:** Correct the four passages to name `r`, and either drop the `A12` quotations or add the across-function `A12` as a released column plus a `statistical_results.csv` row. Do not answer this one in a response letter — answer it in the manuscript.

### 27. "Your CEC2013 omnibus p-values do not match your own released CSVs."
**Status:** NOT ANSWERABLE as shipped (S18-R4-03).
**Evidence:** printed 3.3e-7 / 2.2e-3 / 9.2e-6 at `D = 10/30/50` are the tie-**un**corrected values; the corrected (declared primary) values are 5.32e-8 / 1.09e-3 / 2.91e-6. The CEC2017 caption bound `p ≤ 2.6e-8` is likewise the uncorrected D10 value (corrected max 1.16e-9), while CEC2011 prints the corrected pair.
**Response required:** Choose one convention, apply it to all three suites, and state which is printed. No decision changes under either.

### 28. "Your abstract's 2.48 — best rank on which suite?"
**Status:** PARTIAL.
**Evidence:** `main.tex:138–142` names three suites in one clause and then reports 2.48 without attribution; 2.48 is CEC2017-only (CEC2013 overall is 2.80, CEC2011 is 3.36 = second).
**Response required:** Insert "on CEC2017" and, if space allows, add the CEC2013 overall so the two favourable suites and the one unfavourable suite are all visible in the abstract.

### 29. "You ship a mechanism your own experiment shows costs 30–57 % wall-time for nothing. Why is it in the algorithm?"
**Status:** ANSWERABLE, but the answer must be prepared — this is R6's sharpest question.
**Evidence:** Supplement S6.5: ISM `Δrank` +0.05 / +0.16 / +0.20, Holm `p` 0.983 / 0.897 / 0.647, `A12` ≈ 0.50, overhead +57.3 % / +36.3 % / +30.3 %.
**Response required:** Three parts. (i) The ISM is not removable without changing the frozen algorithm and destroying C1's basis — the polish consumes the ISM eigenbasis, and the `no_sgsm` cell runs the polish on coordinate axes. (ii) The overhead is *bookkeeping*, not objective evaluations, so it does not affect any comparison at matched `MaxFES`. (iii) Reporting the null is the contribution: the paper's stated deliverable includes a boundary result on cheap accepted-move structure learning. Do **not** answer by re-asserting a benefit.

### 30. "Is the eigenframe polish actually better than coordinate axes, or than a random orthonormal basis?"
**Status:** NOT ANSWERABLE — and the manuscript already concedes it in four places.
**Response required:** Concede immediately and cite the concessions (`introduction.tex:94–100`, `proposed_algorithm.tex:599–604`, `supplementary.tex` S6.5 closing, the eighth limitation). State the exact contrast that would settle it (learned eigenbasis vs coordinate axes vs matched random orthonormal basis at `D ∈ {50,100}`, same seeds, same budget) and offer it as future work. Under the standing no-rerun constraint this cannot be added in this cycle; say so honestly rather than promising it in revision.

### 31. "Five of six comparators were written by two of the authors. How is this not a self-referential evaluation?"
**Status:** ANSWERABLE.
**Response required:** Do not minimize. State: the relationship is disclosed in the Conflicts of Interest, in the seventh limitation and in the authorship line; every comparator runs from its original publication's configuration inside one harness; the frozen protocol charges an identical `MaxFES` and an identical seed schedule to all seven; and the strongest comparator (eGSK, co-authored by two of the present authors) is the one that beats DT-GSK at `D = 30` and on CEC2011 — an outcome the paper reports rather than suppresses. That last point is the strongest available answer and should be given explicitly.

### 32. "You are second on CEC2011 with a Holm-significant loss, and never separable from eGSK on CEC2017. What exactly is the claim?"
**Status:** ANSWERABLE — the manuscript's calibrated sentence already answers it.
**Response required:** Quote `performance.tex:857–864`: within the GSK-family panel and under the frozen protocol, DT-GSK holds the best descriptive across-dimension family-rank aggregate on two of three suites, while eGSK holds the better ordinal rank at the mid-dimension tier on both CEC2017 and CEC2013 (where the paired tests do not establish a separation) and a Holm-significant advantage on CEC2011. That is the whole claim.

### 33. "Your win/tie/loss tie band is a fixed `1e-8` across functions spanning many orders of magnitude."
**Status:** ANSWERABLE.
**Response required:** The tally is explicitly descriptive; the inferential Wilcoxon and Friedman are rank-based and invariant to per-function scale, so the band affects no significance decision (`performance.tex:203–209`). A tie-band sensitivity analysis is in Supplement S5.

### 34. "The BCa intervals are called rank-stability intervals. Why not confidence intervals on the ranks?"
**Status:** ANSWERABLE — a point of statistical credit.
**Response required:** They resample each algorithm's *fixed* per-function midranks rather than re-ranking within each bootstrap sample, so they describe spread on the mean rank and do not support an overlap test. The paper says so and refuses the stronger reading; this is deliberate, and ticket N-004 records the renaming.

### 35. "Why does DT-GSK not start from the shared initial population?"
**Status:** PARTIAL — disclosed, not bounded.
**Evidence:** `performance.tex:117–125`; `supplementary.tex:1231–1236` ("a disclosed fairness asymmetry that is not separately bounded and is most consequential at low dimension").
**Response required:** Explain the mechanism (DT-GSK self-initializes `5·D` points from the same seed-paired stream, so the seed pairing holds but the starting matrix does not), restate that it applies at every dimension, and — recommended — bound it descriptively from data already in the release (distribution of initial-population best fitness, DT-GSK vs shared `X0`, across seeds). No rerun required.

### 36. "Table A19 in the supplement runs off the page."
**Status:** NOT ANSWERABLE — **must be fixed before submission** (S18-R5-01).
**Evidence:** `supplementary.log:1647` "Overfull \hbox (218.9852pt too wide)"; measured on supplementary.pdf p.48, 17 words past the right text margin and 7 past the paper edge, with cells truncated to `interaction_grap` and `final_polish_sta`.
**Response required:** Re-lay the table (wrapping `p{}` columns or a sidewaystable), re-render, and re-measure. No parameter value may change; the artefact is hash-frozen, so the freeze manifest must be re-hashed.

### 37. "You claim runs are repeat-identical. Does that include the comparators?"
**Status:** PARTIAL and, as written, over-broad (S18-R5-02).
**Evidence:** `proposed_algorithm.tex:727–728` correctly says byte-stability covers DT-GSK and the analysis pipeline only; `performance.tex:179–186` says "Runs are budget-exact and repeat-identical" immediately after a sentence quantified over all seven optimizers. The RT-001 closure record measures 3,772 scientific-column diffs when the comparators are re-run under current code (ATMALS-GSK ≈ 31 %, eGSK ≈ 29 %), deterministic within-commit only.
**Response required:** Narrow the §4 sentence to DT-GSK and add one limitation sentence stating that comparator evidence is deterministic within its producing commit but is not bit-reproducible across commits, with the measured scope. This converts a discoverable surprise into a disclosed limitation.

### 38. "Which commit reproduces the submitted PDF?"
**Status:** NOT ANSWERABLE as shipped (S18-EIC-02).
**Evidence:** the freeze manifest records `anchor_commit: abd2fa2f25c8…`, but HEAD `45248eb31` itself changed `performance.tex` (+11 lines), rebuilt the PDF/DOCX and re-hashed those rows in the same manifest without re-stamping the anchor.
**Response required:** Re-stamp the anchor to the commit containing the hashed bytes and extend `check_manifest.py` to assert `git show <anchor>:<path>` matches every recorded hash.

### 39. "The scaffold ablation held ISM off in every cell. Does it tell us anything about the shipped algorithm at `D ≥ 50`?"
**Status:** ANSWERABLE.
**Response required:** No, and the supplement says so in its own subsection. The remove-one results are conditional on ISM-off and therefore speak to the scaffold in the tiers where the memory is inactive; the `D ≥ 50` question is addressed by the separate overlay isolation. Use cautious identifiability language and do not extrapolate.

### 40. "Your ISM update rule is an EMA. Which operand carries the decay, and is the learning rate independent?"
**Status:** ANSWERABLE — and it is worth volunteering, because this is where comparable manuscripts fail.
**Response required:** `G ← λG + η Σ_i w_i φ(δ̂_i)φ(δ̂_i)ᵀ`: retention `λ` multiplies the **old** graph and `η` is an independent learning rate; the two are not collapsed. This matches the frozen source, and the printed equation states that the display is the *update* rule only — consumption is separately gated on `conf(G_abs) ≥ κ_min`.

### 41. "Why is F2 excluded from CEC2017?"
**Status:** ANSWERABLE.
**Response required:** It is excluded under the adopted CEC2017 protocol for documented instability and difficult-to-reproduce behaviour, and — the part that matters — **uniformly in every panel cell**, so no algorithm gains or loses from the exclusion. Give the uniformity clause in the same sentence.

---

## C. Questions the authors should be ready for but that need no manuscript change

| # | Question | One-line answer from the shipped package |
|---|---|---|
| 42 | "Is the 'Overall' column a test?" | No — an unweighted mean of per-dimension Friedman mean ranks, with the Iman–Davenport correction applying per dimension only (`performance.tex:325–330`). |
| 43 | "Did the two corrected code defects change any reported number?" | The polish-incumbent defect never corrupted results (best-ever shadow); the numba import defect changed wall-clock only, with bit-identical optimization results. All primary, scaffold and overlay evidence was regenerated at 51 runs with the corrected binary. |
| 44 | "Are the compiled kernels numerically identical to the NumPy path?" | For the interaction graph, yes by construction — `fastmath=False`, no `parallel=True` on the accumulation kernels (verified in `_numba_accel.py:1127–1259`), with a backend-parity regression test. |
| 45 | "Does the deep-stall restart lose the best solution?" | No — subsystems are elitist except the restart, which resamples the working population; the global best is held separately, never re-initialized, and is what the run returns. |
| 46 | "Why is the Nemenyi diagram a mean-rank plot with a CD span rather than a clique diagram?" | A presentation choice, stated in the protocol; non-separable groups are identified in the text and the within-one-CD cohorts are given per dimension in the figure caption. |
| 47 | "Was any generative-AI system involved in the results?" | No — declared at methods level and in the back matter; the tool and version are pinned, and all scientific content came from the deterministic analysis pipeline. |
| 48 | "Why is the CEC2011 runtime a bare mean when CEC2017 gets ± SD?" | `cost_cec2017.csv` gives CEC2011 `mean = 80.64 s, sd = 119.34 s, n = 550` — the SD exceeds the mean because 22 problems of different native dimension are pooled. Give the SD and say the pool is heterogeneous, or drop the figure. |

---

## D. Response-letter priority

1. **Fix before submission, do not defend in a letter:** Q26 (A12 column), Q27 (omnibus p-values), Q36 (Table A19 overflow), Q38 (freeze anchor), Q37 (determinism scope + comparator caveat).
2. **Prepare a written answer, no manuscript change strictly required:** Q6/Q5 (tuning budget — but a number in the supplement is strongly preferred), Q4/Q23 (compute cost — a supplement table is preferred), Q29 (why ship the ISM), Q31 (comparator authorship), Q30 (basis contrast — concede and defer).
3. **Lead with these; they are the manuscript's strongest ground:** Q13 (disclosed robustness reversals), Q11 (multiplicity discipline), Q16 (adverse cases stated), Q3 (per-mechanism attribution), Q24 (which cell carries the qualifications).
