# Evidence card — liang2024gskwoa

## 1. Verified bibliographic identity
- **Citation key:** `liang2024gskwoa`
- **Title (on source):** "A Novel Improved Whale Optimization Algorithm for Global Optimization and Engineering Applications"
- **Authors (on source):** Ziying Liang; Ting Shu; Zuohua Ding (Zhejiang Sci-Tech University)
- **Venue/year (on source):** Mathematics 2024, 12, 636; DOI 10.3390/math12050636; published 21 February 2024 (p. 1)
- **Identity status (inventory):** `minor_metadata_mismatch` — identity certain; ALL THREE bib given names are wrong: source authors are **Ziying** Liang, **Ting** Shu, **Zuohua** Ding (bib: "Ziting Liang", "Tao Shu", "Zijian Ding").
- **Source file:** `reference_papers/liang2024gskwoa.pdf`, 43 pages, sha256 `fa0af91dfa0485420a0fab7560cec4ce086fb286ac2d0238c953349712af5dd0`
- **Locator convention:** local PDF page N = printed page "N of 43"; cite as "p. N".

## 2. Research question and context
Can WOA's limited global-search efficiency and slow convergence be improved by combining three strategies — chaotic (Sine–Tent–Cosine) initialization, the GSK junior gaining–sharing phase as the exploration operator, and Dynamic Opposition-Based Learning (DOBL) population updating? Proposed algorithm: **DGSWOA** ("Dynamic Gain-Sharing Whale Optimization Algorithm") (Abstract p. 1; Sec. 1, pp. 1–2).

## 3. Method
- **STC map initialization** (Sec. 3.1, Eq 11, p. 4): Sine–Tent–Cosine chaotic map (from a cosine-transform-based chaotic system) for a more uniform initial population.
- **GSK junior phase as WOA exploration** (Sec. 3.2, Eq 12, p. 5): the junior gaining–sharing rule (nearest-better X_{i,j−1}, nearest-worse X_{i,j+1}, random X_rand) replaces WOA's random "search for prey"; knowledge factor kf set to 0.5. The paper describes GSK (Mohamed et al., ref [25]) as having "excellent performance in solving optimization problems, especially high-dimensional problems" and its junior phase as balancing exploration and exploitation (p. 5). Only the **junior** phase is used; the senior phase is not adopted.
- **DOBL** (Sec. 3.3, Eqs 13–15, pp. 5–6; Algorithm 1, p. 6): opposition-based learning with a dynamic factor δ decreasing over iterations and depending on fitness rank; keeps top third of {X, X_opposite, X_dynamic-opposite}.
- **Overall algorithm:** Fig 3 flowchart (p. 7); Algorithm 2 pseudo-code (p. 8); behavior selection among encircling prey (Eq 1), bubble-net attack (Eq 6), and GSK-based exploration (Eq 12).
- **Complexity** (Sec. 3.5, p. 8): space O(N·D); time ≈ O(T·(N·D + N·F + N·logN)).

## 4. Experimental scope
- **Suite:** BBOB (Blackbox Optimization Benchmarking) test suite, 24 noise-free single-objective functions F1–F24 (Table 2, p. 9), dimensions 2, 3, 5, 10, 20, 40; search range [−5, 5].
- **Protocol:** population 30, 500 iterations, 30 independent runs per function/dimension; Python 3.9, Windows 10 (Sec. 4.1, p. 8). Fixed-iteration budget — NOT the standard COCO/BBOB runtime-based protocol.
- **Comparators:** PSO, GA, GWO, BOA, SOA, WOA, LWOA, MSWOA (Table 1, p. 9). DGSWOA settings: kf = 0.5, δMAX = 1, b = 1 (Table 1, p. 9).
- **Ablation** (Sec. 4.3, Table 3, pp. 10–12): SWOA (STC only), GWOA (GSK only), DWOA (DOBL only) vs WOA and DGSWOA at dimension 10.
- **Engineering problems** (Sec. 5, pp. 39–41): three-bar truss design (Table 11, p. 40) and pressure vessel design (Table 12, p. 41), same comparators/settings.

## 5. Findings (conservative)
- **Ablation (D=10, Table 3, pp. 10–12):** average ranks — WOA 3.38, SWOA 3.29, GWOA 3.21, DWOA 3.04, DGSWOA 2.08; all three single strategies beat original WOA; DOBL gives the largest single improvement, then GSK, then STC (p. 12). "GWOA is obviously better at solving multi-peak problems and can effectively avoid falling into local optima" (p. 12).
- **Main comparison (Tables 4–9, pp. 13–37; Table 10, p. 38):** DGSWOA holds combined rank 1 in all six dimensions (average rank 1.96 / 1.63 / 1.75 / 1.83 / 2.17 / 2.04 at D = 2/3/5/10/20/40).
- **Wilcoxon signed-rank (Sec. 4.4.2, p. 39):** State +/−/≈ per function in Tables 4–9; most marks are "+" at dimensions 2, 3, 5, 10; some "−" at 20 and 40 but overall still improved.
- **Convergence:** faster convergence in most cases (Figs 4–5, pp. 38–39).
- **Engineering:** best mean on three-bar truss (263.94, Table 11, p. 40); second on pressure vessel behind LWOA (mean 8949.7 vs 8484.0, Table 12, p. 41).

## 6. Limitations
- WOA-lineage study: GSK contributes one operator (junior phase only); no GSK-family algorithm is among the comparators, and no CEC suite is used.
- Fixed 500-iteration budget on BBOB functions instead of the COCO expected-runtime protocol; results are means/ranks over 30 runs.
- Comparators are general swarm algorithms plus two WOA variants; no state-of-the-art DE/CMA-ES class baselines.
- Some table values carry rounding artifacts acknowledged by the authors (note under Table 3, p. 12).

## 7. Usable locators (claim → locator)
| Claim | Locator |
|---|---|
| DGSWOA = STC init + GSK junior phase + DOBL on WOA | Abstract p. 1; Sec. 3, pp. 4–8 |
| GSK junior-phase update rule used for WOA exploration, kf = 0.5 | Eq 12, p. 5 |
| Authors' characterization of GSK (strong on high-dimensional problems; junior phase balances exploration/exploitation) | Sec. 3.2, p. 5 |
| DOBL equations and dynamic factor | Eqs 13–15, pp. 5–6 |
| Complexity O(T·(N·D + N·F + NlogN)) | Sec. 3.5, p. 8 |
| BBOB suite, 24 functions, dims 2–40, pop 30, 500 iterations, 30 runs | Sec. 4.1–4.2, pp. 8–9; Table 2, p. 9 |
| Ablation ranks (GSK-only variant GWOA better than WOA; DOBL strongest single strategy) | Table 3 + discussion, pp. 10–12 |
| DGSWOA combined rank 1 in all six dimensions | Table 10, p. 38 |
| Wilcoxon signed-rank convention and summary | Sec. 4.4.2, p. 39 |
| Three-bar truss best / pressure vessel second | Tables 11–12, pp. 40–41 |

## 8. Supported uses in the DT-GSK manuscript
- Related-work sentence: the GSK junior-phase operator has been exported into WOA (DGSWOA) as its exploration mechanism, where an ablation showed the GSK-equipped variant outperformed original WOA at dimension 10 on BBOB, and the full three-strategy hybrid ranked first among nine algorithms across dimensions 2–40.
- Evidence that GSK operators are being adopted outside the GSK/DE lineage (cross-family operator transplantation).

## 9. Unsupported / prohibited overextensions
- Do NOT cite as evidence that GSK (the full algorithm) outperforms WOA or others — only the junior-phase operator was transplanted.
- Do NOT treat the BBOB numbers as CEC-protocol evidence or compare them with FES-budgeted results.
- Do NOT claim DGSWOA is state-of-the-art beyond its compared set (no DE/CMA-ES-class baselines).
- Do NOT reuse the paper's "GSK excels on high-dimensional problems" line as an independent finding — in this source it is a citation-backed characterization, not a result.

## 10. Role in DT-GSK framing (Appendix B)
Appendix B.2 — "GSK variants and hybrids — related-work breadth only." Cite only where the verified mechanism (GSK junior phase inside WOA) is actually discussed.
