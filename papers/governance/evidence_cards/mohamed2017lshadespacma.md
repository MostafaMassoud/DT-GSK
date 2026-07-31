# Evidence card — mohamed2017lshadespacma

## Verified bibliographic identity
- Title: LSHADE with Semi-Parameter Adaptation Hybrid with CMA-ES for Solving CEC 2017 Benchmark Problems
- Authors: Ali W. Mohamed (Cairo University); Anas A. Hadi, Anas M. Fattouh, Kamal M. Jambi (King Abdulaziz University)
- Venue/year: Proceedings of the 2017 IEEE Congress on Evolutionary Computation (CEC 2017)
- DOI (bib): 10.1109/CEC.2017.7969307; page footer "978-1-5090-4601-0/17/$31.00 (c)2017 IEEE"
- Local file: `reference_papers/mohamed2017lshadespacma.pdf` (8 pp.)
- Inventory status: identity `verified`, readable, admissible. SHA-256 `a15cd9421f3be6904ded1f8becd2c8d2a2913c51fa4586d45830c6365367f118`.
- Locator convention: no printed proceedings page numbers in the local file; locators use local PDF pages 1–8 plus section/table numbers.
- Note: the file's author line prints "Anas M. Fattouh"; the bib records "Ali M. Fattouh" — flagged in reading, does not affect identity (title, venue, DOI, other authors match). Inventory carries the entry as verified.

## Research question and context
Can LSHADE be improved by (a) a semi-parameter adaptation (SPA) scheme that adapts only Cr during the first half of the budget (with F drawn uniformly) and only then switches to full adaptation of F, and (b) a hybridization framework in which LSHADE-SPA and a crossover-modified CMA-ES work simultaneously on one population with an adaptive budget split? (Abstract, PDF p. 1.)

Context: motivated by JADE (ref. [15]) and SHADE/LSHADE (refs. [16], [18]); notes SHADE ranked 3rd of 21 algorithms in the CEC2013 competition with the top two ranks taken by non-DE algorithms (Sec. I, PDF pp. 1–2), and calls LSHADE "the winner of the 2014 competition" (Sec. III-E, PDF p. 5). Design premise: "the semi-adaptive algorithm is better than pure random algorithm or fully adaptive or self-adaptive algorithm" (Sec. I, PDF p. 2) — an empirical principle, argued from exploration/exploitation trade-offs of F and Cr.

## Method
- LSHADE base: current-to-pbest/1 mutation with archive, binomial crossover, greedy selection, LPSR (Sec. II-A, PDF pp. 2–3; LPSR formula with Nmin = 4 at PDF p. 3).
- CMA-ES component: standard sampling x_i = N(m, sigma^2 C) with weighted-mean update and step-size/covariance adaptation (Sec. II-B, PDF p. 3); modified by applying the DE crossover operation (Eq. 3) to CMA-ES offspring to improve exploration (Secs. I and II-D, PDF pp. 1, 4).
- SPA (Sec. II-C, PDF pp. 3–4):
  - First half (nfes < max_nfes/2): Cr_i = randn(Mcr_i, 0.1) with LSHADE memory adaptation (arithmetic mean of successful Cr); F_i = 0.45 + 0.1·rand (uniform in (0.45, 0.55)) — "change one parameter at a time".
  - Second half: F_i = randc(MF_i, 0.1) (Cauchy, memory updated with Lehmer mean of successful F); MF slots initialized from the last 5 generations of part 1; Cr adaptation continues but freezes to terminal values per LSHADE's rule.
- Hybridization (Sec. II-D, PDF p. 4): per-individual algorithm assignment by class probability FCP drawn from memory M_FCP; memory updated by M_FCP,g+1 = (1−c)·M_FCP,g + c·Delta_Alg1, where Delta_Alg1 = min(0.8, max(0.2, w_Alg1/(w_Alg1+w_Alg2))) and w is the sum of fitness improvements of successful offspring per algorithm; probabilities clamped to (0.2, 0.8) so both algorithms always run. Pseudocode: Fig. 1, PDF p. 4.
- Parameters (Sec. III-B, PDF p. 4): NP_init = 18·D; Pbest rate 0.11, arc rate 1.4, memory size H = 5 (as LSHADE); FCP init 0.5; learning rate c = 0.8; SPA switch at max_nfes/2.

## Experimental scope
- CEC2017 single-objective real-parameter suite: 30 functions (F1–F3 unimodal, F4–F10 multimodal, F11–F20 hybrid, F21–F30 composition), D = 10, 30, 50, 100; 51 independent runs; MaxFES = 10,000 × D; error values < 10^-8 treated as zero (Secs. III-A, III-D, PDF pp. 4–5).
- Full descriptive statistics (best/worst/median/mean/std) for LSHADE-SPACMA: Tables II–V, PDF pp. 5–6.
- Comparison vs LSHADE (original suggested parameters) and LSHADE-SPA: multi-problem Wilcoxon signed-rank test at 0.05 significance (SPSS 20.00), R+/R−, and better/equal/worse counts (Sec. III-E and Table VI, PDF pp. 5, 7).
- Complexity timings: Table I, PDF p. 5 (MATLAB R2014a, i7-4790, 12 GB RAM).

## Conservative findings (with locators)
1. LSHADE-SPACMA vs LSHADE (Table VI, PDF p. 7): significantly better at D = 100 (R+ = 378.5, R− = 56.5, p = 0.000; 24 better / 1 equal / 5 worse); NOT significantly different at D = 10, 30, 50 (p = 0.242, 0.372, 0.119), though with favorable R+ at all dimensions.
2. LSHADE-SPA vs LSHADE (Table VI): significantly better at D = 30 (p = 0.031), D = 50 (p = 0.037), and D = 100 (p = 0.007); not significant at D = 10 (p = 0.821). The authors read this as semi-adaptive > fully adaptive for LSHADE (Sec. III-E, PDF p. 5).
3. LSHADE-SPACMA vs LSHADE-SPA: no significant difference at any dimension (Table VI); the CMA-ES hybridization's clearest added value is at D = 100 (Sec. III-E, PDF p. 5; conclusion PDF pp. 7–8).
4. Qualitative pattern: at D = 10 all three algorithms are comparable; superiority of the proposed methods grows with dimension (Sec. III-E, PDF p. 5).
5. Historical/context statements usable from this source: SHADE ranked 3rd of 21 in the CEC2013 competition, top two ranks non-DE (Sec. I, PDF p. 2); LSHADE is "the winner of the 2014 competition" (Sec. III-E, PDF p. 5).

## Limitations
- Comparison set is only LSHADE and its own SPA variant — no external CEC2017 competitors are compared in this paper.
- No effect sizes; only Wilcoxon signed-rank R+/R− and p-values.
- The "semi-adaptive better than fully adaptive or pure random" principle is an empirical claim on this suite/configuration, not a theorem (Sec. I, PDF p. 2).
- 8-page conference paper: no ablation isolating the modified-CMA-ES crossover, no parameter sensitivity study.

## Exact usable locators (claim → locator)
- SPA two-phase definition (F uniform(0.45,0.55) then Cauchy/Lehmer; Cr memory adaptation then freezing): Sec. II-C, PDF pp. 3–4.
- Hybridization framework, FCP memory update, (0.2, 0.8) clamping: Sec. II-D and equations, PDF p. 4; pseudocode Fig. 1, PDF p. 4.
- Modified CMA-ES = CMA-ES + crossover for exploration: Abstract PDF p. 1; Sec. II-D, PDF p. 4.
- Parameter settings (NP=18D, H=5, p=0.11, arc=1.4, FCP=0.5, c=0.8): Sec. III-B, PDF p. 4.
- CEC2017 protocol (51 runs, 10^4·D FES, 1e-8 zeroing): Secs. III-A, III-D, PDF pp. 4–5.
- Headline significance results incl. D=100 (R+ 378.5, p=0.000, 24/1/5): Table VI, PDF p. 7.
- Descriptive results per dimension: Tables II–V, PDF pp. 5–6.
- SHADE CEC2013 3rd-rank statement: Sec. I, PDF p. 2. LSHADE 2014-winner statement: Sec. III-E, PDF p. 5.

## Supported uses in the DT-GSK manuscript
- Citing LSHADE-SPACMA as the hybrid DE–CMA-ES competitive context (Appendix B.3 role) — an example of the winner-lineage LSHADE family hybridized with covariance adaptation, relevant when positioning DT-GSK against modern CEC-2017-era competitors.
- Supporting narrow claims that (a) its gains over LSHADE concentrate at higher dimensions and are statistically significant only at D=100 for the full hybrid, and (b) semi-adaptation of F/Cr outperformed LSHADE's full adaptation at D ≥ 30 on CEC2017.
- Sourcing the competition-context facts listed above (SHADE 3rd in 2013; LSHADE won 2014) if needed in related work.

## Unsupported / prohibited overextensions
- Do NOT cite this paper for LSHADE-SPACMA's own CEC2017 competition ranking (not stated in the file).
- Do NOT claim LSHADE-SPACMA dominates LSHADE at all dimensions — Table VI shows ≈ at D = 10–50.
- Do NOT present the semi-adaptation principle as established theory; it is empirically argued for this algorithm/suite.
- Do NOT use as evidence about GSK mechanisms or about CMA-ES itself (cite hansen2001cmaes for CMA-ES).

## Role in DT-GSK framing (Appendix B.3)
`mohamed2017lshadespacma` — hybrid competitive context: the LSHADE-lineage/CMA-ES hybrid representing the strongest DE-era competition baselines against which family-level positioning is made. Also connects the DE lineage to the GSK-family authors (A. W. Mohamed).

## Verification quotation (identity)
"LSHADE with Semi-Parameter Adaptation Hybrid with CMA-ES for Solving CEC 2017 Benchmark Problems — Ali W. Mohamed ... Anas A. Hadi, Anas M. Fattouh, Kamal M. Jambi" (PDF p. 1).
