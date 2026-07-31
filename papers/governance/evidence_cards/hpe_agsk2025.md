# Evidence card: hpe_agsk2025

## Verified bibliographic identity
- Title: "Adaptive gaining-sharing knowledge-based variant algorithm with historical probability expansion and its application in escape maneuver decision making"
- Authors: Lei Xie, Yuan Wang, Shangqin Tang, Yintong Li, Zhuoran Zhang, Changqiang Huang
- Venue: Artificial Intelligence Review (2025) 58:161; DOI 10.1007/s10462-024-11096-4 (printed on p. 1)
- Identity status (reference_inventory.csv): **verified**; local PDF is the 44-page Springer-Nature version, article pagination "Page N of 43"; local PDF page k = article page k. Locators below use article page numbers.

## Research question and context
Can AGSK's single-objective optimization performance be further improved by modifying its junior/senior search strategies (rather than only its parameter adaptation), and does the resulting variant work on a real decision-making problem (beyond-visual-range escape maneuver)? (Abstract, p. 1; Sect. 1 contributions, p. 5).

## Method
HPE-AGSK = AGSK + three strategy modifications (Sect. 3, pp. 9–13):
1. **Expansion Sharing Strategy (ESS)** in the junior phase: instead of always using the two nearest ranked neighbors x_{i-1}, x_{i+1}, the gaining sources are drawn from a dynamically expanding rank window sigma = max(round(R_J·(1 + nfe/Max_nfe)), 1) (Eqs. 20–22, pp. 9–10). Claimed purpose: better local search.
2. **Historical Probability Expansion Strategy (HPES)** in the senior phase: a historical store H of size round(theta·N) keeps individuals eliminated by crossover; senior donors are drawn from the merged {current pop + H} split into best/middle/worst with rank-proportional selection probability (Eqs. 23–25, pp. 10–11); the partition fraction p decays linearly from 0.15 to 0.05 with evaluations (Eq. 26, p. 11). Claimed purpose: stronger global search.
3. **Reverse Gaining Strategy (RGS)**: for the first ~50% of evaluations (and with probability 0.9 thereafter inverted per Eq. 27), the (kf, kr) pool uses negative kf values [(-0.1, 0.2), (-0.1, 0.1), (-0.1, 0.9), (-0.1, 0.9)] to push individuals away from the best and expand the population distribution early (Eq. 27 and Algorithm 1, p. 11; movement-trend illustration Fig. 13, p. 31).
- Knowledge rate k is dimension-dependent (Eq. 28, p. 12): AGSK-style random k for D < 30, APGSK-style two fixed values (4 or 20) for D >= 30.
- Inherits NLPSR population reduction from APGSK (Sect. 3.4, p. 12; APGSK background Eqs. 17–19, pp. 8–9).
- Parameters (tuned via Friedman tests + grid search on CEC 2021, Sect. 5.1, pp. 16–18): N = 40·D, Nmin = 12, delta = 0.05, R_J = 5, theta = 0.05, fs = 9 (Table 1, p. 15).
- Section 2 (pp. 5–9) gives a compact, faithful restatement of GSK (Eqs. 1–8), AGSK (Eqs. 9–16: pool-based kf/kr adaptation, LPSR, random knowledge rate), and APGSK (Eqs. 17–19: negative-kf pool switch after 50% evaluations, fixed two-value k, NLPSR) — usable as a secondary locator for those mechanisms.

## Experimental scope
- **CEC 2021** test suite (10 functions, 5 transformation configurations 000/010/110/011/111), D = 10 and 20, Max_nfe = 200,000 (10D) and 1,000,000 (20D), search range [-100,100]^D (Sect. 4.2, p. 14). 30 runs per algorithm for the main comparison (Sect. 5.3, p. 19); 10 runs for parameter tuning and ablation (Sects. 5.1–5.2, pp. 16, 19). 13 comparators incl. AGSK, APGSK, APGSK-IMODE, GLAGSK, EDA2, AAVS-EDA, EBOwithCMAR, LSHADE-SPACMA, HSES, IMODE, MadDE, CJADE, iLSHADE-RSP (Sect. 4.3, pp. 14–15; parameter settings Table 1, p. 15).
- **CEC 2018** suite (29 functions), D = 10/30/50/100, Max_nfe = 10,000·D, 51 runs, vs AGSK, APGSK, GLAGSK, APGSK-IMODE, IMODE, MadDE (Sect. 5.4, p. 26).
- **BVR escape maneuver decision making**: 10 repeated experiments, metrics = success rate, average calculation time, average fitness evaluations (Sect. 6, pp. 31–35).
- Statistics: Friedman test (alpha = 0.05) and Wilcoxon signed-rank test (alpha = 0.05) (Sect. 4.2, p. 14). Environment: MATLAB R2021b, Xeon Gold 6248R (Sect. 4.1, p. 14).

## Conservative findings
- Ablation (CEC 2021, 10 runs, Friedman ranks): full HPE-AGSK ranks 1st in all configurations; AGSK-HPES 2nd, AGSK-RGS 3rd, AGSK-ESS 4th, plain AGSK last; ESS alone is slightly worse than AGSK in 10D-000 and 10D-111 (Table 5, p. 19).
- CEC 2021 Friedman mean rank across configurations: HPE-AGSK 4.44 (1st), MadDE 4.73 (2nd), APGSK-IMODE 4.82 (3rd); HPE-AGSK ranks only 4th in the untransformed 000 configuration behind MadDE, APGSK-IMODE, IMODE (Table 6, p. 21; Fig. 7, p. 20).
- CEC 2021 Wilcoxon: HPE-AGSK beats AGSK 34/13/3 (10D) and 36/14/0 (20D); beats APGSK-IMODE 27/13/0 (10D) but loses 0/6/4 to it in 10D-000 (Table 7, p. 22).
- CEC 2018 Friedman by function class (mean rank): unimodal 2.87 (behind IMODE 2.62 and APGSK 2.75); multimodal 2.85 (behind APGSK-IMODE 2.19); hybrid+composition 1.78 (best) (Tables 10–12, p. 27). Note: the running text on p. 27 swaps the words "exploration"/"exploitation" relative to its own definitions on pp. 26–27 (unimodal = exploitation test, multimodal = exploration test); cite the tables, not the prose labels.
- CEC 2018 by dimension: 2nd at 10D (behind MadDE), 1st at 30D/50D/100D and overall (Fig. 10, p. 28). Wilcoxon: significant vs all six comparators at 30D; not significant vs IMODE at 50D/100D, and at 10D not significant vs APGSK, APGSK-IMODE, IMODE, MadDE (Tables 13–16, pp. 28–29).
- Time complexity (CEC 2021 metric): HPE-AGSK (T2-T1)/T0 = 213.11 (10D) / 242.58 (20D) — roughly 1.8x AGSK's cost and below EBOwithCMAR and APGSK-IMODE-10D (Table 9, p. 26).
- BVR escape: HPE-AGSK success rate 100% (10/10), mean maneuver time 9.10 s, mean 622.2 fitness evaluations; APGSK 90%, APGSK-IMODE 80%, GLAGSK/IMODE/MadDE 60%, AGSK 50% (Table 18, p. 35).
- Population diversity (Euclidean-distance index, Eqs. 29–30, p. 31): HPE-AGSK diversity similar to AGSK/APGSK/MadDE, below IMODE and APGSK-IMODE; high early, low late (Fig. 14 discussion, p. 31).

## Limitations (author-stated and observed)
- Author-stated (Sect. 7, p. 38): (kf, kr) pool too limited; population diversity in later iterations needs expansion; time complexity should be improved.
- Weakest on untransformed (000) low-dimensional problems (Table 6, p. 21; Table 7, p. 22).
- Only D <= 20 for CEC 2021 and D <= 100 for CEC 2018; no CEC2011/CEC2017-2017-report real-world suite; BVR study is a single scenario with 10 repeats.
- Ablation and parameter tuning used only 10 runs per configuration.

## Exact usable locators (claim -> locator)
| Claim the DT-GSK manuscript may need | Locator |
|---|---|
| GSK junior/senior update equations (restated) | Sect. 2.1, Eqs. (4)–(5), pp. 6–7 |
| AGSK (kf,kr) pool + probabilities + LPSR + random knowledge rate | Sect. 2.2, Eqs. (9)–(16), pp. 7–8 |
| APGSK negative-kf pool switch, fixed k in {0.5(->4),2(->20)}, NLPSR | Sect. 2.3, Eqs. (17)–(19), pp. 8–9 |
| ESS mechanism (rank-window expansion in junior phase) | Sect. 3.1, Eqs. (20)–(22), pp. 9–10, Fig. 2 |
| HPES mechanism (historical archive + rank-probability senior donors) | Sect. 3.2, Eqs. (23)–(26), pp. 10–11, Fig. 3 |
| RGS mechanism (negative-kf pool early) | Sect. 3.3, Eq. (27), Algorithm 1, p. 11 |
| HPE-AGSK ranks 1st overall on CEC 2021 (Friedman 4.44) | Table 6, p. 21 |
| HPE-AGSK beats AGSK/APGSK by Wilcoxon on CEC 2021 | Table 7, p. 22 |
| CEC 2018: best mean rank at 30/50/100D; 2nd at 10D | Fig. 10, p. 28; Tables 13–16, pp. 28–29 |
| Runtime overhead vs AGSK | Table 9, p. 26 |
| BVR escape results (100% SR, 9.10 s, 622.2 evals) | Table 18, p. 35 |
| Author-stated limitations | Sect. 7, p. 38 |
| GSK-variant literature mini-taxonomy (population/hybrid/strategy/composite improvements) | Sects. 1.1–1.4, pp. 4–5 |

## Supported uses in the DT-GSK manuscript
- Related-work breadth: cite as a 2025 strategy-improvement AGSK variant (ESS/HPES/RGS) evaluated on CEC 2021/2018 with Friedman + Wilcoxon statistics.
- Evidence that the GSK-variant literature itself groups improvements into population / hybrid / strategy / composite categories (pp. 4–5) — useful for positioning DT-GSK's mechanism class.
- Evidence that archive-of-eliminated-individuals and negative-kf (reverse/repulsion) devices exist in the GSK family (pp. 10–11).
- Secondary (non-primary) locator for AGSK/APGSK mechanics; primary citations remain mohamed2020agsk and apgsk2021.

## Unsupported / prohibited overextensions
- Do NOT cite as evidence that HPE-AGSK beats all comparators everywhere: it loses the 000 configuration at both dimensions and is not significantly different from IMODE at 50D/100D (Tables 6, 15, 16).
- Do NOT cite for performance at D > 100, on CEC2011/CEC2017-style real-world problems, or on any suite DT-GSK uses unless the suite matches.
- Do NOT use the p. 27 prose "outstanding exploration ability" wording without noting the exploration/exploitation label swap; rely on Tables 10–12 semantics.
- Do NOT present the BVR result as general engineering evidence — one scenario, 10 repeats.
- No claim of relevance to DT-GSK's specific mechanisms may be sourced here; this paper does not discuss DT-GSK.

## Role in DT-GSK framing (Appendix B)
Appendix B.2: "GSK variants and hybrids — related-work breadth only. Use each only where its verified mechanism is actually discussed. Do not insert one sentence per source solely to force bibliography usage."

## Verification quotations
- "expansion sharing strategy is proposed and added in junior gaining-sharing phase to boost local search ability... historical probability expansion strategy is proposed and added in senior gaining-sharing phase to strengthen global search ability... reverse gaining strategy is proposed and utilized to expand population distribution at the beginning of iterations" (Abstract, p. 1).
- "Mean ranking of HPE-AGSK is 4.44 which is the first in the test algorithms" (Sect. 5.3.1, p. 19; Table 6, p. 21).
