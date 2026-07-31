# Evidence card: epd_gsk2024

## Verified bibliographic identity
- Title: "Enhancing population diversity based gaining-sharing knowledge based algorithm for global optimization and engineering design problems"
- Authors: Ziyuan Liang, Zhenlei Wang
- Venue: Expert Systems With Applications 252 (2024) 123958; DOI 10.1016/j.eswa.2024.123958 (printed p. 1)
- Identity status (reference_inventory.csv): **verified**; 20-page PDF, local PDF page = printed page 1–20.

## Research question and context
GSK loses population diversity rapidly (random initialization; diminished inter-phase information transfer; homogenizing senior updates), causing local-optimum trapping and exploration/exploitation imbalance. Can a plug-in "framework" of three diversity components improve GSK and its adaptive variants (AGSK, APGSK) without extra asymptotic cost? (Abstract, p. 1; deficiency analysis and contributions, Sect. 1, p. 2).

## Method
EPD-GSK framework = three components applied to any GSK-family base (Sect. 3, pp. 3–5):
1. **Sobol-sequence initialization** (low-discrepancy) replacing uniform random init (Sect. 3.1, Eqs. (7)–(9), p. 4; uniformity illustration Fig. 1, p. 4).
2. **Cauchy mutation in the junior phase**: the sharing difference term is multiplied elementwise by standard Cauchy(0,1) samples: x_new = x_i + kf·[(x_{i-1} - x_{i+1}) + cauchy(0,1) ⊗ (x_r - x_i)] (and mirrored branch) (Sect. 3.2, Eq. (11), p. 5; Cauchy-vs-Gaussian density Fig. 2, p. 5).
3. **Reverse learning update in the senior phase**: the sign of the senior increment is inverted, x_new = x_i - kf·[(x_pbest - x_pworst) + (x_m - x_i)] (and mirrored branch), OBL-inspired (Sect. 3.3, Eq. (12), p. 5).
- Baseline GSK restated with junior/senior equations and pseudocode (Sect. 2.2, Eqs. (2)–(6), Algorithms 1–2, p. 3).
- Complexity: claimed unchanged overall, O(N·D·T) (Sect. 3.4, p. 5) — but see Limitations (measured runtime of the Cauchy component increases).
- Instantiations: EPD-GSK, EPD-AGSK, EPD-APGSK; single-component variants EPDa (Sobol only), EPDb (Cauchy only), EPDc (reverse learning only) for ablation (Sects. 3.5, 4.3, pp. 5, 7).
- Parameters (Table 2, p. 6): GSK/EPD-GSK N=100, P=0.1, kf=0.5, kr=0.9, k=10; AGSK/EPD-AGSK N=20·D, P=0.05, c=0.05, k in [1,20], Kwp=[0.85,0.05,0.05,0.05]; APGSK/EPD-APGSK N=250 (5D), N=200·D (D>5). AGSK/APGSK (kf,kr) pools spelled out in Sect. 4.2, pp. 6–7.

## Experimental scope
- Suites (Table 1, p. 6): CEC2017 (29 functions, F2 excluded, 10D/30D, Max_FEs 1e5/3e5) for EPD-GSK ablation; CEC2020 (10 functions; 5/10/15/20D) for EPD-AGSK and EPD-APGSK; CEC2022 (12 functions, 10D/20D, Max_FEs 2e5/1e6) for the external comparison. Search range [-100,100]^D; error values < 1e-8 zeroed.
- 30 independent runs everywhere (Sect. 4.1, p. 6); Wilcoxon signed-rank (alpha = 0.05) per function and Friedman test on means (Sects. 4.1, 4.3.3, pp. 6–7).
- External comparators on CEC2022: RSA, SHO, FOX, MSMA, HFPSO, MELGWO, FDB-TLABC, all N = 100 (Sect. 4.4, p. 11; parameters Table 3, p. 6).
- Engineering problems (Sect. 5, pp. 12–17): pressure vessel, three-bar truss, tension/compression spring, welded beam; static penalty method (Eq. (14), p. 12; penalty factors 10,000 / 10,000 / 100 / 100,000); N = 100, 100,000 FEs, 30 runs; 11 comparators (CLPSO, ABC, KH, WOA, HHO, HGSO, RUN, DO, SO, FLA, COA; Table 20, p. 15).
- Environment: MATLAB 2021a, 3.10 GHz Intel Core, 32 GB (Sect. 4, p. 6).

## Conservative findings
- CEC2017 ablation vs plain GSK (Wilcoxon +/-/= from GSK's perspective; "-" = variant better): EPD-GSK is better on 17 of 29 at 10D (2/17/10) and 16 of 29 at 30D (0/16/13) with 0 losses at 30D (Tables 4–5, pp. 8–9). Single components help less: e.g., EPDa-GSK 10D 2/7/20 (Table 4, p. 8).
- CEC2020: EPD-AGSK better than AGSK on 6/8/6/5 functions at 5/10/15/20D; EPD-APGSK better than APGSK on 2/4/7/3 functions (Sect. 4.3.2, p. 7; Tables 6–13, pp. 9–10). Single-component variants sometimes degrade performance (Sect. 4.3.2 point (2), p. 7).
- Friedman: complete-framework algorithms rank 1st in every dimension block (EPD-GSK 2.34 overall vs GSK 3.41, Table 14, p. 11; EPD-AGSK 1.95 vs AGSK 3.80, Table 15, p. 12; EPD-APGSK 2.62 vs APGSK 3.41, Table 16, p. 12 — note EPD-APGSK ranks only 3.10 at 20D, tied-worst among its variants, Table 16 last column).
- CEC2022 vs 7 external metaheuristics: EPD-APGSK Friedman rank 1.40 overall (1.50 at 10D, 1.29 at 20D), FDB-TLABC 2nd (Table 19, p. 14); wins 12/12, 12/12, 12/11... per-algorithm Wilcoxon counts in Tables 17–18 (pp. 12–13); loses only to HFPSO/FDB-TLABC on isolated functions.
- Population diversity metric PD (Eq. (13), p. 7) shows higher initial diversity from Sobol and sustained diversity fluctuations from Cauchy/reverse learning (Figs. 5–6, pp. 14–15; discussion pp. 7–9).
- Execution time: Sobol and reverse-learning components add negligible time; Cauchy mutation measurably increases runtime of EPDb-GSK and EPD-GSK (Fig. 7, p. 15; Sect. 4.3.6, p. 10). On CEC2022, EPD-APGSK had the lowest average execution time among the 8 compared algorithms (Fig. 9, p. 16; Sect. 4.4, p. 11).
- Engineering: EPD-APGSK best costs — PVD 5879.5241 (Table 21, p. 16), TBTD 263.8958435 tied with SO (Table 22, p. 16), T/CSD 0.01264522 (Table 23, p. 17), WBD 1.723485 (Table 24, p. 18).

## Limitations (author-stated and observed)
- Author-stated (Sect. 6, pp. 17–18): scalability to higher-dimensional problems may pose computational-efficiency challenges; adaptability to a wider array of problems unexplored; future work = component sensitivity and adaptive combination.
- Max dimension tested is 30 (CEC2017); CEC2020/2022 runs are 5–20D. No 50D/100D evidence.
- Improvements over already-adaptive bases are thinner than over plain GSK (EPD-APGSK beats APGSK on only 2–7 functions of 10 per dimension; ranks worse than single components at 20D, Table 16).
- Complexity claim of "no additional CC" (Sect. 3.4, p. 5) is contradicted in measured time by the Cauchy component (Sect. 4.3.6, p. 10) — cite the measured statement, not the claim, for runtime.
- Engineering comparison uses penalty-function constraint handling with hand-picked penalty factors (p. 12).

## Exact usable locators (claim -> locator)
| Claim the DT-GSK manuscript may need | Locator |
|---|---|
| GSK diversity-loss deficiency analysis (random init; phase homogenization) | Sect. 1, p. 2 (paragraph "GSK showed promising performance, but...") |
| GSK junior/senior equations + pseudocode (restated) | Sect. 2.2, Eqs. (2)–(6), Algorithms 1–2, p. 3 |
| Sobol initialization mechanism | Sect. 3.1, Eqs. (7)–(9), p. 4, Fig. 1 |
| Cauchy mutation in junior phase | Sect. 3.2, Eq. (11), p. 5 |
| Reverse-learning (sign-inverted) senior update | Sect. 3.3, Eq. (12), p. 5 |
| Framework claimed O(N·D·T), same as GSK | Sect. 3.4, p. 5 |
| 30 runs, Wilcoxon + Friedman protocol | Sect. 4.1, pp. 6–7 |
| Full framework needed; single components insufficient/degrading | Sect. 4.3.1 point (3), p. 7; Sect. 4.3.2 point (2), p. 7 |
| EPD-GSK vs GSK Wilcoxon counts (10D/30D) | Tables 4–5, pp. 8–9 (R rows) |
| EPD-AGSK / EPD-APGSK vs bases | Tables 6–13, pp. 9–10; Friedman Tables 14–16, pp. 11–12 |
| EPD-APGSK 1st on CEC2022 vs 7 metaheuristics | Tables 17–19, pp. 12–14 |
| Population-diversity metric definition | Eq. (13), p. 7 |
| Cauchy component increases measured runtime | Sect. 4.3.6, p. 10, Fig. 7 |
| Engineering design results (PVD/TBTD/T-CSD/WBD) | Tables 21–24, pp. 16–18 |
| Author-stated limitations | Sect. 6, pp. 17–18 |

## Supported uses in the DT-GSK manuscript
- Related-work breadth: a 2024 diversity-enhancement framework for GSK/AGSK/APGSK (Sobol init + junior Cauchy mutation + senior reverse learning), validated on CEC2017/2020/2022 with Wilcoxon/Friedman, 30 runs.
- Evidence that the GSK literature itself diagnoses diversity loss / local-optimum trapping as GSK's core weakness (Sect. 1, p. 2; Abstract).
- Evidence that Cauchy-type heavy-tailed perturbation and opposition/reverse-learning devices have precedent inside the GSK family (Eqs. (11)–(12), p. 5) — relevant when positioning any DT-GSK mechanism that uses heavy-tailed moves (e.g., BSE Cauchy basis discussed via yao1999evolutionary per Appendix B.5).
- Evidence of component-ablation methodology in GSK variants (EPDa/b/c design, Sect. 4.3).

## Unsupported / prohibited overextensions
- Do NOT claim EPD-GSK is state-of-the-art beyond the tested suites/dimensions (max 30D; CEC2022 comparison uses mostly recent nature-inspired algorithms, not CEC winners such as LSHADE lineage).
- Do NOT cite the "no additional computational complexity" claim as if runtime-neutral — measured time increases for the Cauchy component (p. 10).
- Do NOT infer that the framework reliably improves APGSK: gains are small and non-uniform (Tables 10–13, 16).
- Not usable for CEC2011 real-world evidence or any D >= 50 claim; does not discuss DT-GSK.

## Role in DT-GSK framing (Appendix B)
Appendix B.2: related-work breadth only; cite only where its verified mechanisms (Sobol init, junior Cauchy mutation, senior reverse learning, diversity diagnosis) are actually discussed.

## Verification quotations
- "GSK tends to get trapped in local optimum due to the rapid loss of population diversity during the optimization process, resulting in an imbalance between exploration and exploitation." (Abstract, p. 1)
- "the introduction of a single component may not significantly enhance the performance ... the combination of the complete framework is required" (Sect. 4.3.1, p. 7)
