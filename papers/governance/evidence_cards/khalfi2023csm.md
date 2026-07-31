# Evidence card — khalfi2023csm

## Verified bibliographic identity
- Title: A Single-Solution–Compact Hybrid Algorithm for Continuous Optimization
- Authors: Souheila Khalfi, Giovanni Iacca, Amer Draa
- Venue (bib): Memetic Computing, vol. 15, 2023, pp. 155–204; DOI 10.1007/s12293-023-00392-1
- Local source: `reference_papers/khalfi2023csm.pdf` (36 pp., Springer AUTHOR-MANUSCRIPT version, dated Oct 2022). Published pagination (155–204) is NOT visible in the local file; ALL locators below use the manuscript's own pagination 1–36 (identity_status = verified; see reference_inventory.csv note).
- Bib first-author given name "Said" vs source "Souheila": inventory records exact-title and all-author confirmation; use source names.

## Research question and context
Can a memetic hybrid of a single-solution metaheuristic and a compact (probabilistic-model, population-less) algorithm overcome the known weaknesses of compact algorithms — premature convergence and poor handling of non-separable problems — while keeping a tiny memory footprint suitable for constrained hardware? (Abstract, p. 1; Sec. 1, pp. 1–3.)

## Method (Sec. 3, pp. 6–9)
- Operator: Non-Uniform Mutation (NUM), x'_k = x_k ± Δ(t, ·) with Δ(t, y) = y(1 − ρ^{(1−t/T)^B}) — long jumps early, shrinking neighborhood later; "neither a Gaussian mutation, which searches only locally (around its mean value), nor a Cauchy mutation, which takes long steps" (Sec. 3.2, pp. 6–7, Eqs. (1)–(2), Fig. 1).
- cSM = two sequential modules sharing one structure (Sec. 3.3, pp. 7–9, Algorithm 1):
  - Module-1 (SNUM): single-solution search perturbing ONE randomly chosen variable at a time (treats the problem as separable); budget1 = 20% of total FE budget T.
  - Module-2 (cMNUM): compact scheme — sample from probability vector PV = [μ, σ], apply Multi-NUM (all variables; handles non-separability), greedy elite/lbest update, PV update with virtual population NP; μ initialized to −elite from Module-1 (information exchange; opposite initialization chosen after preliminary BBOB comparison, footnote 1, pp. 8–9).
- Parameters: B = 6 (empirical analysis Sec. 4.1.2, p. 24), NP = 1 for cSM (better than the conventional 300 in preliminary tests, p. 11), λ = σ-init = 10; only two tunable parameters (B and budget1) (pp. 10–11, Table 3).
- Toroidal bound handling for all algorithms (p. 11).

## Experimental scope (Sec. 4, pp. 8–23)
- Testbeds: BBOB (24 functions; D = 20, 40; 15 runs; COCO platform), CEC-2014 (30 functions) and CEC-2017 (30 functions) at D = 10/30/50/100 with 51 runs each, and 7 highest-dimensional CEC-2011 real-world problems (T09, T11.1, T11.2, T11.7–T11.10; D = 126, 120, 216, 140, 96, 96, 96) with 25 runs (pp. 9–10).
- Budgets: T = 5000 × D FEs (BBOB, CEC-2014, CEC-2017); T = 150000 FEs (CEC-2011) (p. 10).
- Comparators: 12 lightweight algorithms — rcGA, cDE-Exp, DEcDE, McDE, CScDE, cSNUM, cPSO, cTLBO, cFA, nuSA, ISPO, 3SOME (pp. 10–11); plus population-based winners L-SHADE (CEC-2014) and jSO (CEC-2017) using competition raw data (Sec. 4.3, p. 21, Tables 27–28 pp. 30–35), and CEC-2011 top-two GA-MPC and DE-ACr (mean values only) (Sec. 4.2.3, p. 20).
- Statistics: Wilcoxon rank-sum at α = 0.05 plus Holm–Bonferroni procedure (p. 17 ff., Tables 4–7).

## Conservative findings
1. Vs lightweights on CEC-2014 (120 cases = 30 func × 4 dims): cSM significantly better than cDE-Exp/McDE/DEcDE/CScDE/cSNUM/cFA/cPSO/cTLBO/ISPO/nuSA/3SOME in 91/115/90/73/62/114/117/118/95/79/71 of 120 cases; best Holm–Bonferroni rank, all null hypotheses rejected (pp. 18–19, Tables 4–5).
2. Vs lightweights on CEC-2017: same pattern — 91/116/83/63/64/116/116/118/95/70/81 of 120; best rank, all rejected (p. 19, Tables 6–7).
3. CEC-2011 (7 problems, 25 runs): cSM statistically better/worse than cDE-Exp, nuSA, 3SOME, CScDE, DEcDE in 6/0, 7/0, 4/1, 3/1, 3/1 of 7 cases; Holm–Bonferroni rejects only cDE-Exp and nuSA. Vs the competition's top two (means only): DE-ACr best on mean fitness; cSM close when beaten and best among lightweights on several problems; "cSM, as well as the other lightweight approaches, are not particularly tailored for the larger-scale problems" (pp. 20–21, Tables 8–9).
4. Vs L-SHADE/jSO: competition winners clearly better overall; but cSM's relative performance "surprisingly improves for mid-scale dimensionalities (i.e., 50 to 100 dimensions)", winning only isolated cases at 10–30D (Sec. 4.3, p. 21; Tables 27–28).
5. Complexity: cSM (and nuSA) have higher CPU time than other compact methods (MNUM perturbs all variables); memory footprint remains small/constant in D-independent solution count, unlike population methods whose memory grows (L-SHADE example, Sec. 4.4, pp. 21–23, incl. footnote 3).
6. Ablation: both modules contribute; budget1 variations have limited effect for tested values (Sec. 4.1.1–4.1.2, pp. 23–24).
7. Explicit research limitation (Conclusions, p. 23): "the substantial performance difference is still in favor of the population-based approaches ... the absence of a population unquestionably impedes the attainment of better performances."

## Limitations
- Author-manuscript pagination only (cannot cite published pages 155–204 from the local copy).
- CEC-2011 comparison with GA-MPC/DE-ACr is mean-only (no raw data, no statistics; p. 20, Table 9 note).
- Winners' comparison relies on competition raw data, not re-runs (p. 21).
- cSM is a lightweight-hardware proposition; its results do not claim state-of-the-art status against population algorithms.

## Exact usable locators (bibkey, manuscript page)
- Compact-optimization definition, weaknesses (premature convergence, no population variance info, separability bias): (khalfi2023csm, Sec. 1 pp. 1–2; Sec. 2.2 pp. 4–5; Table 1 p. 5).
- NUM operator definition and Gaussian/Cauchy contrast: (khalfi2023csm, Sec. 3.2, pp. 6–7, Eqs. (1)–(2)).
- cSM two-module design, 20% budget split, μ ← −elite information exchange: (khalfi2023csm, Sec. 3.3, pp. 7–9, Algorithm 1 p. 9).
- Experimental protocol (91 problems; 15/51/25 runs; T = 5000·D or 150000 FEs; 12 lightweight comparators; NP = 1; B = 6; toroidal bounds): (khalfi2023csm, Sec. 4, pp. 9–11, Table 3).
- CEC-2014 win/tie/loss and Holm–Bonferroni: (khalfi2023csm, pp. 18–19, Tables 4–5).
- CEC-2017 win/tie/loss and Holm–Bonferroni: (khalfi2023csm, p. 19, Tables 6–7).
- CEC-2011 results incl. GA-MPC/DE-ACr context: (khalfi2023csm, pp. 20–21, Tables 8–9).
- L-SHADE/jSO comparison and the mid-scale (50–100D) observation: (khalfi2023csm, Sec. 4.3, p. 21; Tables 27–28, pp. 30–35).
- Time/memory complexity analysis: (khalfi2023csm, Sec. 4.4, pp. 21–23).
- Research limitations paragraph: (khalfi2023csm, Sec. 5, p. 23).

## Supported uses in the DT-GSK manuscript
- Taxonomy/positioning: exemplar of memetic/lightweight (single-solution + compact) hybridization evaluated across BBOB + CEC-2014 + CEC-2017 + CEC-2011 with Wilcoxon + Holm–Bonferroni methodology.
- Supporting the general statement that modular budget-split designs with complementary operators (separable-oriented + non-separability-oriented) are an established design pattern.
- Supporting the observation that population-based winners (L-SHADE, jSO) dominate lightweight/compact approaches on CEC suites — useful context when positioning DT-GSK against strong population baselines.
- Its use of the 5000·D and 150000-FE budgets and 51/25-run conventions may be cited as an example of common practice (NOT as the protocol authority).

## Unsupported / prohibited overextensions
- Do NOT cite cSM as evidence that lightweight algorithms match population-based state of the art — the paper says the opposite (p. 23).
- Do NOT cite the GA-MPC/DE-ACr comparison as statistically validated (means only).
- Do NOT use as the defining source for CEC-2011/2014/2017 protocols (definition keys hold that role).
- Do NOT cite published pagination (155–204) for specific claims; only manuscript pages are verifiable locally.

## Role in DT-GSK framing (Appendix B.5)
"Taxonomy/positioning only." Sanctioned for related-work breadth on hybrid/memetic and lightweight metaheuristics and for context on how non-family methods fare against CEC winners; not part of the GSK lineage, benchmark authority, or statistics toolkit.
