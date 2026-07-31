# Evidence card — tanabe2014improving

## Verified bibliographic identity
- Title: Improving the Search Performance of SHADE Using Linear Population Size Reduction
- Authors: Ryoji Tanabe; Alex S. Fukunaga (The University of Tokyo)
- Venue/year: Proceedings of the 2014 IEEE Congress on Evolutionary Computation (CEC 2014)
- DOI (bib): 10.1109/CEC.2014.6900380
- Local file: `reference_papers/tanabe2014improving.pdf` (8 pp.)
- Inventory status: identity `verified`, readable, admissible. SHA-256 `1c25d8c374300936947b05e27bd55444e1692b185d5f6ff141ad16eeab530e04`.
- Locator convention: the local file carries NO printed proceedings page numbers (official pp. 1658–1665 not shown); locators use local PDF pages 1–8 plus section/equation/table numbers.

## Research question and context
Does adding a simple deterministic Linear Population Size Reduction (LPSR) to SHADE 1.1 improve performance enough to compete not only with state-of-the-art adaptive DE but with restart CMA-ES variants (the CEC2013 competition co-winners)? (Abstract and Sec. I, PDF p. 1.)

Context: positions deterministic population resizing (IPOP-CMA-ES, GL-25, IPSO, DPSR, SVPS) against adaptive resizing (e.g., GAVaPS), arguing deterministic rules are simpler and effective (Sec. I, PDF p. 1). LPSR is a special case of SVPS (τ=1, ρ=0; footnote 1, PDF p. 3) with a single extra user parameter (initial population size).

## Method
- SHADE 1.1 recap (Secs. II-A–II-E, PDF pp. 2–3): historical memories M_CR, M_F; CR_i = randn(M_CR,ri, 0.1) but CR_i = 0 if the slot holds the terminal value ⊥; F_i = randc(M_F,ri, 0.1) (Eqs. 1–2, PDF p. 2); current-to-pbest/1 mutation (Eq. 3) with midpoint boundary repair (Eq. 4); binomial crossover (Eq. 5); external archive; memory update per Algorithm 1 (PDF p. 3) using weighted Lehmer means for BOTH CR and F (Eqs. 7–9) with fitness-improvement weights; if M_CR,k = ⊥ or max(S_CR) = 0 the slot is locked at ⊥, forcing CR = 0 ("change-one-parameter-at-a-time" behavior, effective on multimodal problems; Sec. II-E, PDF p. 3).
- LPSR (Sec. II-F, PDF p. 3): after each generation, N_{G+1} = round[((N_min − N_init)/MAX_NFE)·NFE + N_init] (Eq. 10), N_min = 4 (minimum for current-to-pbest); the (N_G − N_{G+1}) worst-ranked individuals are deleted and the archive size is resized proportionally (Algorithm 2 lines 21–24, PDF p. 3). Without LPSR, Algorithm 2 reduces to SHADE 1.1.
- Parameter tuning by ParamILS with training set = CEC2013 composition functions F21–F25 at D = 10, 30 (deliberately disjoint from the CEC2014 test set to avoid overfitting; Sec. III-A, PDF p. 5). Tuned settings: r_Ninit = 18 (N_init = round(18·D)), r_arc = 2.6, p = 0.11, H = 6 (Table II, PDF p. 5).

## Experimental scope
- CEC2014 suite: 30 functions (F1–F3 unimodal; F4–F16 simple multimodal; F17–F22 hybrid; F23–F30 composition), search space [−100,100]^D; D = 10, 30, 50, 100; MaxFES = D × 10,000; 51 runs; errors < 10^-8 zeroed (Sec. III, PDF p. 4).
- Full L-SHADE result tables (best/worst/median/mean/std per dimension): Table I, PDF p. 4.
- Comparators (authors' suggested settings): SHADE 1.1, CoDE, EPSDE, SaDE, JADE, dynNP-jDE (Sec. III-C, PDF pp. 5–6, Table IV, PDF p. 6); restart CMA-ES variants NBIPOP-ACMA-ES and iCMAES-ILS, CEC2013 competition co-winners (Sec. III-D, PDF pp. 6–7, Table V, PDF p. 7); D-SHADE (DPSR-based reduction) (Sec. III-E, Tables VI–VII, PDF p. 7).
- Statistics: Wilcoxon rank-sum, p < 0.05, aggregate +/−/≈ counts.
- Algorithm complexity timings: Table III, PDF p. 5 (C++, Ubuntu 12.04, i7 2.20 GHz).

## Conservative findings (with locators)
1. L-SHADE clearly has the best overall performance vs all six DE comparators for D ∈ {10, 30, 50} and outperforms them at D = 100 as well (e.g., SHADE 1.1 vs L-SHADE: better/worse/≈ = 0/16/14 at D=10 and 3/18/9 at D=30); "the search performance of L-SHADE is significantly better than SHADE 1.1, showing that LPSR successfully contributed" (Table IV and Sec. III-C, PDF p. 6).
2. Against restart CMA-ES variants, L-SHADE is "quite competitive": on the 6 hybrid functions F17–F22 it clearly outperforms both NBIPOP-ACMA-ES and iCMAES-ILS at ALL dimensions (e.g., 6/6 worse for NBIPOP at D=10–50); on unimodal functions the CMA-ES variants win on F1 at D=50,100; overall counts favor L-SHADE at D=10–50 vs NBIPOP and D=10,30 vs iCMAES-ILS (Table V and Sec. III-D, PDF pp. 6–7).
3. The paper explicitly frames this as contradicting the conventional wisdom that DE performs significantly worse than restart CMA-ES (Sec. III-D, PDF p. 7: "contrary to current conventional wisdom (c.f. [2]) ... a DE approach can be quite competitive with state-of-the-art restart CMA-ES variants").
4. LPSR vs DPSR: L-SHADE beats D-SHADE at D = 10, 30, is similar at D = 50, and is outperformed at D = 100; the best reduction schedule appears dimension-dependent, but LPSR has fewer control parameters (Table VII and Sec. III-E, PDF p. 7).
5. Caveats stated by the authors: deterministic resizing assumes a known MaxFES budget; in anytime-optimization settings SHADE 1.1 may outperform L-SHADE (Sec. IV, PDF p. 8). On hybrid functions whose components differ strongly (unimodal–multimodal, separable–nonseparable mixes), adaptive DE including SHADE/JADE/jDE "tended to degrade dramatically" per their ref. [33] (Sec. IV, PDF p. 8).

## Limitations
- Single benchmark suite (CEC2014) for the headline claims; parameter set tuned by ParamILS (though on a disjoint CEC2013 training set).
- Comparator DEs used untuned author-suggested parameters (acknowledged in tanabe2013shade for the analogous setup).
- The local file does not print the proceedings pagination; page-precise citations to the published 1658–1665 range cannot be verified locally.
- The paper does not itself state L-SHADE's CEC2014 competition rank (the "winner of the 2014 competition (LSHADE)" statement appears in mohamed2017lshadespacma, Sec. III-E).

## Exact usable locators (claim → locator)
- LPSR formula and N_min = 4: Eq. (10) and surrounding text, Sec. II-F, PDF p. 3.
- Worst-individual deletion + archive resizing: Algorithm 2 lines 21–24 and Sec. II-F text, PDF pp. 3–4.
- SHADE 1.1 memory update with ⊥ terminal value: Algorithm 1 and Sec. II-E, PDF p. 3.
- Weighted Lehmer mean with improvement weights: Eqs. (7)–(9), PDF p. 3.
- Tuned parameters (r_Ninit=18, r_arc=2.6, p=0.11, H=6) and ParamILS protocol: Table II and Sec. III-A, PDF p. 5.
- CEC2014 protocol (51 runs, D×10^4 FES, 1e-8 zeroing): Sec. III, PDF p. 4.
- L-SHADE vs DE state of the art: Table IV, PDF p. 6.
- L-SHADE vs NBIPOP-ACMA-ES / iCMAES-ILS incl. hybrid-function dominance: Table V, PDF p. 7.
- LPSR vs DPSR dimension dependence: Table VII, PDF p. 7.
- Anytime-optimization caveat and hybrid-function pathology: Sec. IV, PDF p. 8.

## Supported uses in the DT-GSK manuscript
- Citing L-SHADE as the origin of linear population size reduction and as the SHADE-lineage baseline that many later CEC winners (including LSHADE-SPACMA) build on.
- Supporting claims that (a) deterministic population reduction can substantially improve an adaptive DE, and (b) a DE-family method can be competitive with restart CMA-ES, with particular strength on hybrid (partially separable) functions.
- Population-size-reduction lineage context for any GSK-family variant that adopts linear reduction (e.g., AGSK-style NP reduction).

## Unsupported / prohibited overextensions
- Do NOT cite this paper as evidence that L-SHADE won CEC2014 (rank not stated here; use mohamed2017lshadespacma for the "winner of the 2014 competition" wording).
- Do NOT extend the CMA-ES-competitive claim beyond CEC2014 and the two specific restart variants tested.
- Do NOT claim LPSR is universally the best reduction schedule — D-SHADE (DPSR) won at D = 100 (Table VII, PDF p. 7).
- Do NOT use it for CEC2017 results or for GSK mechanisms.

## Role in DT-GSK framing (Appendix B.3)
`tanabe2014improving` — L-SHADE and population-size-reduction lineage (paired with tanabe2013shade). Method-lineage and competitive-context citation for the DE side of the DT-GSK comparison narrative.

## Verification quotation (identity)
"Improving the Search Performance of SHADE Using Linear Population Size Reduction — Ryoji Tanabe and Alex S. Fukunaga, Graduate School of Arts and Sciences, The University of Tokyo" (PDF p. 1).
