# Evidence card: ma2023mgskdpmo

## Verified bibliographic identity
- Title: "A Modified Gaining-Sharing Knowledge Algorithm Based on Dual-Population and Multi-operators for Unconstrained Optimization"
- Authors: Haoran Ma, Jiahao Zhang, Wenhong Wei, Wanyou Cheng, Qunfeng Liu
- Venue: Advances in Swarm Intelligence (ICSI 2023), LNCS 13968, pp. 309–319; chapter DOI 10.1007/978-3-031-36622-2_25 (printed p. 309)
- Identity status (reference_inventory.csv): **verified**; 11-page PDF; **printed page N = local PDF page N−308** (PDF p. 1 = printed p. 309). Locators use printed pages 309–319.

## Research question and context
Multi-operator and multi-population mechanisms are known to strengthen EAs; GSK uses a single population with one gaining-sharing scheme per phase, which "may own more probability to be trapped in the local optima in difficult tasks" (Sect. 3.1, p. 311). Can a dual-population, multi-operator GSK with hybrid parameter adaptation compete with CEC2020 winners on the CEC2020 suite? (Abstract, p. 309; Sect. 1, pp. 309–310).

## Method
mGSK-DPMO (Sect. 3, pp. 311–314):
1. **Dual-population multi-operator scheme** (n_pop = 2, Sect. 3.1, pp. 311–312): each subpopulation has its own junior/senior gaining-sharing operators —
   - pop1 junior: x_new = x_old + kf_jun·[(x_r1 − x_r2) + (x_r3 − x_old)] (Eq. 1); pop1 senior: x_new = x_old + kf_sen·[(x_phi_best − x_m-worst) + (x_m − x_r3)] (Eq. 2);
   - pop2 junior: mirrored random scheme x_new = x_old + kf_jun·[(x_r2 − x_r1) + (x_old − x_r3)] (Eq. 3); pop2 senior: x_new = x_old + kf_sen·(x_phi_worst − x_phi_best) (Eq. 4) — learning also from worse individuals to escape local optima (p. 312).
2. **Hybrid parameter adaptation** (Sect. 3.2, pp. 312–313): kf_jun and kr_sen adapt via a modified success-history memory (H elements) with weighted Lehmer mean (Eqs. 5–6, p. 312, weight w_k = log((|S|+0.5)/k)); kf_sen and kr_jun adapt via the AGSK pool + probability KwP scheme (fixed probabilities for the first 10% of FEs; p. 313). kf_sen is additionally staged: ×0.7 (<0.2 MaxFES), ×0.8 (0.2–0.4 MaxFES), ×1.1 (after) (Eq. 7, p. 313).
3. **Knowledge-rate adaptation**: K = K_init if rand < Nfes/MaxFES else 4·K_init (Eq. 8, p. 313).
4. **NLPSR** population reduction, as in AGSK (p. 313).
5. **New ranking scheme** (pp. 313–314): from generation 2, rank = convex combination score = ω·rank_fitness + (1−ω)·rank_improvement (Eq. 9), with ω rising linearly 0.1→0.9 over evaluations (Eq. 10).
- Parameters (Sect. 4.1, p. 314): Nmin = 4 + floor(3·log(D)); Ninit = 250 for 5D, 240·D for 10/15/20D; H = 20·D; kf_sen pools [0.1 1.0 0.5 1.0] and [−0.15 −0.05 −0.05 −0.15]; kr_jun pool [0.2 0.1 0.9 0.9]; KwP_init = [0.85 0.05 0.05 0.05]; K_init = 10; c = 0.05.

## Experimental scope
- CEC2020 bound-constrained benchmark, D = 5, 10, 15, 20, search range [−100,100]^D (Sect. 4, p. 314). MATLAB R2021b, Ryzen 5 3400GE (p. 314).
- 30 independent runs (implied by "through 30 runs independently", p. 315; the CEC2020 protocol).
- Comparators: ELSHADE-SPACMA (3rd CEC2018), EBOwithCMAR (1st CEC2017), HSES (1st CEC2018) in Table 1; IMODE, AGSK, j2020 (top-3 CEC2020) in Table 2; competitor parameters taken from their articles (Sect. 4.2, p. 314).
- Evaluation: CEC2020 competition score metric (Score1 SE + Score2 RS) and Dolan–Moré performance profiles (tau = 1e-2, Fig. 1, p. 315). **No Wilcoxon/Friedman tests.**

## Conservative findings
- Against EBOwithCMAR/ELSHADE-SPACMA/HSES: mGSK-DPMO better on 6/8 (5D), 7/10 (10D), 6/10 (15D), 7/10 (20D) problems (Sect. 4.2, p. 315; Table 1, p. 316); CEC2020 total score 100.00 vs 64.25 / 58.35 / 41.25 (Table 3, p. 318).
- Against CEC2020 top-3: total score 97.01 vs IMODE 91.46, AGSK 83.67, j2020 80.46 (Table 4, p. 318); "very competitive" with IMODE at 5D and better at 10/15/20D (p. 315).
- On F10 the algorithm attains best mean among the top-3 comparison despite missing the global optimum; on F9 20D it reaches the optimum in some of the 30 runs while comparators do not (p. 315; Table 2, p. 317).
- Performance profiles: solves ~90% of problems at 5D and ~100% at 10/15/20D at tau = 1e-2, occupying the top curve (Sect. 4.2, p. 318; Fig. 1, p. 315).
- Author-stated motivation result: performance of GSK is "very sensitive to its four control parameters" kf, kr, K, NP (Sect. 3.2, p. 312).

## Limitations (author-stated and observed)
- CEC2020 suite only; dimensions 5–20; 8–10 functions per dimension (F6, F7 not defined at 5D — dashes in Tables 1–2).
- No statistical significance tests; ranking rests on the CEC2020 score metric and performance profiles.
- No ablation isolating dual-population vs hybrid adaptation vs new ranking contributions.
- Conference-length paper (11 pages): no runtime/complexity analysis, no code link.
- Future work (Sect. 5, p. 318): more complicated problems, multi-objective extension — confirming current scope is narrow.

## Exact usable locators (claim -> locator)
| Claim the DT-GSK manuscript may need | Locator (printed pages) |
|---|---|
| GSK sensitivity to its four control parameters | Sect. 3.2, p. 312 |
| Single-population GSK topology may increase local-optimum trapping | Sect. 3.1, p. 311 |
| Dual-population multi-operator junior/senior equations | Eqs. (1)–(4), p. 311 |
| Learning from worse individuals to escape local optima | Sect. 3.1, p. 312 |
| Hybrid success-history (Lehmer-mean) + AGSK-pool adaptation | Sect. 3.2, Eqs. (5)–(7), pp. 312–313 |
| Knowledge-rate adaptation Eq. and NLPSR reuse | Eq. (8) and "Population Size Reduction", p. 313 |
| Fitness+improvement convex-combination ranking scheme | Eqs. (9)–(10), pp. 313–314 |
| Parameter settings | Sect. 4.1, p. 314 |
| CEC2020 score: 100.00 vs EBOwithCMAR/ELSHADE-SPACMA/HSES | Table 3, p. 318 |
| CEC2020 score: 97.01 vs IMODE/AGSK/j2020 (CEC2020 top-3) | Table 4, p. 318 |
| Performance-profile claim (~90%/100% solved, tau=1e-2) | Fig. 1, p. 315; text p. 318 |
| Per-function mean/std tables | Tables 1–2, pp. 316–317 |

## Supported uses in the DT-GSK manuscript
- Related-work breadth: a 2023 dual-population, multi-operator GSK with hybrid (success-history + pool) parameter adaptation that outscored the CEC2020 top-3 under the CEC2020 metric at 5–20D.
- Evidence that multi-population/multi-operator designs and success-history adaptation (SHADE-style Lehmer memory) have been imported into the GSK family (mechanism locators above).
- Evidence, from within the GSK literature, of GSK's strong sensitivity to kf, kr, K, NP (p. 312) — usable when motivating parameter-adaptive design.

## Unsupported / prohibited overextensions
- Do NOT describe results as statistically significant or as covering CEC2017/CEC2011 — CEC2020 only, D <= 20.
- Do NOT attribute the gains to any single component (no ablation).
- Do NOT cite the CEC2020 score comparison as head-to-head with re-tuned comparators; competitor parameters were taken from their original articles (p. 314).
- Does not discuss DT-GSK.

## Role in DT-GSK framing (Appendix B)
Appendix B.2: related-work breadth only; cite only where its verified mechanisms (dual-population multi-operator scheme, hybrid adaptation, improvement-aware ranking) are actually discussed.

## Verification quotations
- "the performance of GSK algorithm is very sensitive to its four control parameters, i.e., knowledge factor kf, knowledge ratio kr, knowledge rate K and population size NP." (Sect. 3.2, p. 312)
- "mGSK-DPMO is significantly better than IMODE, AGSK and j2020 ... which are the top 3 algorithms in CEC2020 competition." (Sect. 4.2, p. 315 — note: "significantly" here refers to the score metric, not a statistical test)
