# Evidence card — hu2022qcsca

## Verified bibliographic identity
- Title: Horizontal and Vertical Crossover of Sine Cosine Algorithm with Quick Moves for Optimization and Feature Selection
- Authors (source): Hanyu Hu, Weifeng Shan, Yixiang Tang, Ali Asghar Heidari, Huiling Chen, Haijun Liu, Maofa Wang, José Escorcia-Gutierrez, Romany F. Mansour, Jun Chen
- Venue: Journal of Computational Design and Engineering, 2022, vol. 9 (no. 6), pp. 2524–2555
- DOI (source page 1): 10.1093/jcde/qwac119 — NOTE: the BibTeX record carries 10.1093/jcde/qwac110 and five wrong author given names (Hui/Yang/Huaguang/Miao/Jie instead of Hanyu/Yixiang/Haijun/Maofa/Jun); resolved from the local source (reference_inventory.csv, identity_status = minor_metadata_mismatch).
- Local source: `reference_papers/hu2022qcsca.pdf` (32 pp., published OUP layout; journal pagination printed; PDF page n = journal page 2523+n)

## Research question and context
Can the sine cosine algorithm (SCA) — simple, few-parameter, but prone to premature convergence due to a poorly balanced exploration/exploitation phase — be improved by (i) an adaptive control parameter, (ii) a crisscross (CC) crossover mechanism, and (iii) a quick-move (QM) mechanism, yielding QCSCA effective for global optimization and wrapper feature selection (FS)? (Abstract, p. 2524; contributions, Sec. 1.3, p. 2527.)

## Method (Sec. 3, pp. 2529–2531)
- Base SCA: population update by sine/cosine oscillation around the best solution, parameter r1 decreasing linearly (Sec. 2, pp. 2528–2529, Eqs. (1)–(2)).
- Adaptive parameter: r1 = 4(1 − t/T)^2 replaces the linear decrease — larger early steps for exploration, smoother late decay for exploitation (Sec. 3.1, pp. 2529–2530, Eq. (3), Fig. 1).
- CC selection mechanism (from crisscross optimizer, Meng et al. 2014): horizontal crossover search (HCS) between pairs of individuals (Eqs. (4)–(5)) and vertical crossover search (VCS) across dimensions of one individual (Eq. (6)), each with greedy selection — increases population diversity and helps escape local optima (Sec. 3.2, pp. 2529–2530, Algorithms 2–3).
- QM mechanism (inspired by the crow search algorithm): before the exploration stage (while stage = t/T < TH, TH constant in (0,1); TH = 0.6 in experiments, Table 8), individuals move quickly toward the current best: X_{i,t+1} = X_{i,t} + r_i · fl · (X_best − X_{i,t}) (Sec. 3.3, p. 2530, Eqs. (7)–(8)).
- QCSCA combines all three (Sec. 3.4, pp. 2530–2531, Algorithm 4, Fig. 2); time complexity driven by T, dimension d, population n, threshold TH (p. 2530).

## Experimental scope
- Suites: IEEE CEC2017 (29 functions, F2 removed as unstable) and IEEE CEC2013 (28 functions) (Sec. 4.1, pp. 2531–2532, Tables 2–3).
- Basic parameters (Table 1, p. 2526): population N = 100; D = 10, 30, 50, 100; M = D × 10000 (per the paper's notation M is "the maximum number of iterations"); F = 51 comparison experiments (i.e., 51 runs).
- Mechanism ablation: 8 variants (SCA, QM_SCA, A_SCA, CC_SCA, QM_A_SCA, QM_CC_SCA, A_CC_SCA, QCSCA) on CEC2017 30D (Sec. 4.2, Table 5, pp. 2531–2534; full data on the authors' GitHub).
- SCA-variant comparison: vs ASCA_PSO, CGSCA, m_SCA, OBSCA, CESCA, CLSCA, SCADE on CEC2013 30D (Sec. 4.3, Table 6, pp. 2533–2534).
- Conventional/advanced comparison: vs SMA, WOA, PSO, GWO, MFO, BMWOA, RCBA, SCADE, OBSCA on CEC2017 at 10/30/50/100D (Sec. 4.4, Tables 9–12, pp. 2538–2544; parameters Table 8, p. 2537).
- Statistics: Wilcoxon signed-rank test at p < 0.05 (Tables 7 and 13, pp. 2535 and 2546); ranks and average ranks per table; convergence curves (Figs. 3–4).
- FS application: binary QCSCA (BQCSCA) on 14 UCI datasets vs binary metaheuristics (Sec. 4.5, pp. 2537 ff.).
- Environment: MATLAB R2018, Windows Server 2016, 2× Xeon Silver 4110, 128 GB RAM (p. 2531).

## Conservative findings
1. Ablation: QCSCA ranks first among the 8 mechanism variants on CEC2017 30D; CC-related variants beat original SCA while QM-only and adaptive-only variants do not — the three mechanisms are complementary, with CC the main contributor (pp. 2534–2535).
2. Vs SCA variants (CEC2013 30D): QCSCA ranks first on 17 of 28 functions, average rank 1.8214; most Wilcoxon p-values < 0.05 (Tables 6–7, pp. 2533–2535).
3. Vs conventional/advanced algorithms (CEC2017, 10–100D): QCSCA ranked first overall at every tested dimension; performance remains comparatively stable as D grows to 100, which the authors read as good scalability (pp. 2537–2538; Tables 9–12; Table 13 p-values mostly < 0.05).
4. FS: BQCSCA tends to find feature subsets with higher classification accuracy than comparable binary algorithms on 14 UCI datasets, "but suffers from excessive time costs" (Abstract, p. 2524; Conclusions, p. 2549).
5. NFL theorem is used as motivation for developing new optimizers (Sec. 1.1, p. 2526).

## Limitations
- Comparator pool excludes DE/GSK-family state of the art and CEC competition winners; strongest comparators are PSO/GWO and SCA variants.
- QCSCA's own unimodal performance is described as "mediocre"; its strength is on multimodal/hybrid/composition functions (p. 2537).
- FS experiments limited to 14 UCI datasets; time cost acknowledged as excessive (p. 2549).
- The parameter table's "M = D × 10000" is labeled "maximum number of iterations" while CEC protocols define D × 10^4 as max function evaluations; the paper's notation should be quoted as-is, not silently converted.

## Exact usable locators (bibkey, journal page)
- SCA weaknesses (local optima, unbalanced exploration/exploitation): (hu2022qcsca, Abstract p. 2524; Sec. 3 intro p. 2529).
- Adaptive r1 = 4(1 − t/T)^2: (hu2022qcsca, Sec. 3.1, pp. 2529–2530, Eq. (3)).
- HCS/VCS crisscross definitions with greedy selection: (hu2022qcsca, Sec. 3.2, pp. 2529–2530, Eqs. (4)–(6), Algorithms 2–3).
- QM mechanism and stage threshold TH: (hu2022qcsca, Sec. 3.3–3.4, pp. 2530–2531, Eqs. (8)–(9); TH = 0.6 in Table 8, p. 2537).
- Experimental protocol (N = 100; D = 10/30/50/100; M = D × 10000; 51 runs; F2 removed): (hu2022qcsca, Table 1 p. 2526; Sec. 4.1 pp. 2531–2532).
- Ablation ranking of mechanism combinations: (hu2022qcsca, pp. 2534–2535, Table 5).
- QCSCA first-ranked vs SCA variants on CEC2013 30D (avg rank 1.8214) with Wilcoxon support: (hu2022qcsca, pp. 2533–2535, Tables 6–7).
- QCSCA first-ranked vs 9 conventional/advanced algorithms on CEC2017 at all four dimensions; stability at 100D: (hu2022qcsca, pp. 2537–2538, Tables 9–13).
- FS competitiveness + excessive time cost: (hu2022qcsca, Abstract p. 2524; Conclusions p. 2549).

## Supported uses in the DT-GSK manuscript
- Taxonomy/positioning: example of a 2022 SCA hybrid using crossover-style information exchange (crisscross) and staged move mechanisms, evaluated on CEC2013+CEC2017 (D up to 100, 51 runs, Wilcoxon at 0.05).
- Supporting the generic observation that population information exchange (crossover between individuals/dimensions) is a common remedy for premature convergence in swarm algorithms.
- Example of NFL-motivated justification for new optimizer design (with wolpert1997nfl as the primary NFL source).

## Unsupported / prohibited overextensions
- Do NOT cite as evidence of superiority over DE/GSK-family algorithms or CEC winners — never compared.
- Do NOT use as CEC2017/CEC2013 protocol authority (suite-definition keys hold that role; awad2016problem is currently blocked).
- Do NOT convert the paper's "M = D × 10000 iterations" into FE budgets or vice versa when quoting its protocol.
- Do NOT reuse the bib DOI (qwac110) or the wrong given names; the source shows qwac119.

## Role in DT-GSK framing (Appendix B.5)
"Taxonomy/positioning only." Use where DT-GSK's related-work text surveys recent hybrid metaheuristics; not for method lineage, benchmark protocol, or statistical methodology.
