# Evidence card — jawad2024egsk

Group: family-panel (Appendix B.1 — Foundation and GSK family)
Prepared: 2026-07-10, Phase 1 tasks 4–5. Read: method (Sect. 3, pp. 3–6), setup (Sect. 4.1, pp. 7–9), results (Sects. 4.2, pp. 9–14), parametric study (Sect. 5, pp. 15–17), conclusions (Sect. 6, pp. 17–18).

## 1. Verified bibliographic identity

- **Identity status: minor_metadata_mismatch, resolved; admissible.** The bib entry is a @misc preprint/in-press placeholder ("2024", title with "for Global Optimization"). The local file is the **published article**: "Enhanced Gaining-Sharing Knowledge-based algorithm", Mohammed Adnan Jawad, Heba Sayed Mohamed Roshdy, Ali Wagdy Mohamed, **Results in Control and Optimization 19 (2025) 100542, DOI 10.1016/j.rico.2025.100542** (printed pp. 1, 2); received 29 Dec 2024, accepted 5 Mar 2025 (p. 1). Authors match the bib exactly. The camera-ready metadata above should be used when the bib is updated (per the inventory note).
- Local file: `reference_papers/jawad2024egsk.pdf`, 19 PDF pages.
- **Locator convention: printed article pages 1–18 (equal to PDF pages) plus section/equation/table numbers.**

## 2. Research question and context

Can GSK's premature convergence be mitigated by three modifications — Adjust Selection Criteria, Modify Parameters Setup, and Escaping from Local Minimum Solutions — producing eGSK, evaluated on CEC 2017 against GSK variants and recent metaheuristics? (Abstract p. 1; Sect. 3.2, p. 5.)

## 3. Method (eGSK = GSK + three modifications)

- GSK recap (Sect. 3.1, pp. 3–5): experience equations Eqs. (4)–(5); worked example Table 1 (D = 100, K = 3, p. 4); junior rule Eq. (6) (p. 4); senior rule Eq. (7) with p-best/middle/p-worst partition (p. 5).
- **eGSK_1 — Adjust Selection Criteria** (Sect. 3.2.1, p. 5): after generating the new population, compare the **sum of fitness of the old population vs the new population**; the population-level winner drives the per-individual greedy update direction (Eqs. (8)–(9)) — a diversity-preserving population-update criterion.
- **eGSK_2 — Modify Parameters Setup** (Sect. 3.2.2, pp. 5–6): initial setup **K = 10, Kf1 = 0.5, Kf2 = 0.5, Kr = 1**; separate knowledge factors for the junior (Kf1) and senior (Kf2) phases become **self-adaptive after 75% of MAXNFEs** via fitness-interpolation formulas: ΔKf1 from the relative position of f(x_i) among f(x_{i−1}), f(x_r), f(x_{i+1}) (Eqs. (10)–(11)); ΔKf2 from the relative position of f(x_i) among min f(x_p-best), min f(x_m), min f(x_p-worst) (Eqs. (12)–(13)); accepted only if in (0,1).
- **eGSK_3 — Escaping from Local Minimum Solutions** (Sect. 3.2.3, p. 6): at 75% of MAXNFEs, compute a scaled standard deviation over {min f(x_p-best), min f(x_m), min f(x_p-worst)} (Eq. (14)); if the stagnation condition holds, apply **Sequential Quadratic Programming (SQP)** as a local search to escape/refine the local minimum. Pseudo-code Fig. 1 (p. 6); flow chart Fig. 2 (p. 7).

## 4. Experimental scope

- Suite: **CEC 2017**, 29 functions (f1, f3–f30; listed with optima in Table 2, p. 8); search space [−100, 100]^D; **D = 10, 30, 50, 100**; **MaxFEs = 10,000×D**; **51 runs**; error < 10⁻⁸ zeroed (Sect. 4.1, pp. 7–8). MATLAB R2023a, Intel 3.40 GHz, 12 GB RAM (Sect. 4, p. 6).
- **eGSK parameters (Table 3, p. 9): P = 0.1, Kf1 = Kf2 = 0.5, Kr = 1, K = 10, NP = 100.** Family comparators with settings in Table 3: AGSK, APGSK, and **FDBAGSK (Case-1, chosen because "Case-1 variant was stronger than its competitors in the original literature")**, all NP = 100, NPmin = 12.
- State-of-the-art comparators (Sect. 4.1, pp. 8–9): cSM, FOWFO, GGA, GJO-JOS, IADE, QCSCA, DEPSO — **results taken from the original literature** (p. 12: "The results of all other state-of-the-art algorithms taken from the original literature").
- Statistics: Wilcoxon signed-rank (0.05) + Friedman; SPSS v20 (Sect. 4.1, p. 8).

## 5. Conservative findings

- eGSK raw statistics: Tables 4–7 (pp. 9–11; 100D = Table 7, p. 11). Optimum or near-optimum reached at least once for 8 problems at 10D, 5 at 30D, 5 at 50D (Sect. 4.2.1, p. 9).
- **Vs GSK variants — Wilcoxon (Table 8, p. 12)**: at **D = 10 eGSK is significantly WORSE than AGSK (R+ 79 / R− 246, p = 0.025, decision "−") and worse than FDBAGSK (p = 0.076, "−"), ≈ APGSK**; at D = 30/50/100 eGSK significantly better than AGSK, APGSK, FDBAGSK in every case; total (all dims pooled) significantly better than all three.
- **Vs GSK variants — Friedman (Table 9, p. 13): overall eGSK 1.89 (1st), FDBAGSK 2.24 (2nd), AGSK 2.71 (3rd), APGSK 3.16 (4th)**; per-dimension mean ranks: D = 10 — AGSK 2.22 best, eGSK 2.78 last (p = 0.14, not significant); D = 30 — eGSK 1.38; D = 50 — 1.66; D = 100 — 1.76 (p = 0.00).
- **Vs state-of-the-art — Friedman (Table 11, narrative p. 13–14)**: eGSK first at D = 10 (1.91), 30 (1.98), 50 (2.28); **second at D = 100 (2.55) behind DEPSO (2.52)**; overall ranking: eGSK, FOWFO, DEPSO, cSM, QCSCA, GGA, GJO-JOS, IADE. Wilcoxon (Table 10, p. 14): FOWFO statistically comparable at all dims (p = 0.094–0.973); QCSCA and DEPSO ≈ at D = 100; others significantly worse.
- **Component study** (Sect. 5, pp. 15–17): eGSK beats GSK, eGSK_1, eGSK_2, eGSK_3 (Wilcoxon Table 12, p. 17 — significant except eGSK_3 at D = 100 ≈; Friedman Table 13, p. 17: eGSK 2.20 first, eGSK_3 2.49 second, GSK 3.67 last).
- **Conclusion success ratios** (Sect. 6, pp. 17–18): vs AGSK 68%, APGSK 71%, FDBAGSK 64%; vs cSM 85%, FOWFO 55%, GGA 84%, GJO-JOS 97%, IADE 97%, QCSCA 89%, DEPSO 75%; vs GSK/eGSK_1/eGSK_2/eGSK_3 71/67/66/59%.
- Authors' summary: eGSK "performs exceptionally well at solving optimization problems with 30, 50, and 100 dimensions and is competitive in 10 dimensions" (Abstract, p. 1).

## 6. Limitations

- **Explicit D = 10 weakness**: significantly worse than AGSK at D = 10 (Table 8) and last among the four variants by D = 10 Friedman rank (Table 9); the abstract's "competitive in 10 dimensions" is the honest framing.
- SQP local search introduces a gradient-based solver dependency (relevant to reproduction; the DT-GSK repo's Python port substitutes scipy-SLSQP for MATLAB fmincon — port-side note, not from this paper).
- State-of-the-art comparator numbers are transcribed from original papers, not re-run under a common environment.
- eGSK's own setup fixes **Kr = 1** (Table 3), i.e., every dimension is always updated pre-adaptation — a departure from GSK's kr = 0.9 that is part of the "Modify Parameters Setup" design, not a typo, but worth noting when comparing parameterizations.
- No CEC2011/CEC2020 evidence; no runtime/complexity analysis.

## 7. Exact usable locators (claim → locator)

| Claim | Locator |
|---|---|
| Published identity (journal, year, DOI, article no.) | pp. 1–2 (title page + footer "Results in Control and Optimization 19 (2025) 100542") |
| Three modifications named | Abstract p. 1; Sect. 3.2, p. 5 |
| eGSK_1 population-sum selection criterion | Sect. 3.2.1, Eqs. (8)–(9), p. 5 |
| eGSK_2 parameters: K=10, Kf1=Kf2=0.5, Kr=1; self-adaptive Kf after 75% MAXNFEs | Sect. 3.2.2, Eqs. (10)–(13), pp. 5–6 |
| eGSK_3 SQP local search at 75% MAXNFEs + stagnation std trigger | Sect. 3.2.3, Eq. (14), p. 6 |
| CEC2017 protocol (29 fns, D = 10/30/50/100, 10,000×D, 51 runs) | Sect. 4.1, pp. 7–8; Table 2, p. 8 |
| eGSK and family parameter settings (incl. FDBAGSK Case-1 choice) | Table 3, p. 9 |
| eGSK worse than AGSK at D = 10; better at 30/50/100 | Table 8, p. 12 |
| Family Friedman: eGSK 1.89 overall 1st; D = 10 p = 0.14 ns | Table 9, p. 13 |
| SOTA Friedman: eGSK 1st at 10/30/50, 2nd at 100 (DEPSO 1st) | Table 11 + narrative, pp. 13–14 |
| FOWFO statistically comparable | Table 10 + narrative, p. 14 |
| Component ablation (eGSK > eGSK_1/2/3 > GSK) | Tables 12–13, p. 17 |
| Success-ratio summary | Sect. 6, pp. 17–18 |
| 100D raw eGSK statistics | Table 7, p. 11 |

## 8. Supported uses

- Citing eGSK as the enhanced-GSK family baseline with its three verified mechanisms (population-sum selection, phase-specific self-adaptive Kf after 75% budget, SQP escape at 75% budget).
- Supporting the claim that eGSK dominates the GSK family at D = 30/50/100 on CEC2017 but is weak/competitive-only at D = 10 (a family-wide mid/high-D vs low-D pattern relevant to DT-GSK's positioning).
- Documenting that eGSK's reference implementation relies on SQP — the mechanism-scope anchor for DT-GSK's EGSK port discussion.
- Stating that FDBAGSK Case-1 is the variant adopted by follow-on family papers.

## 9. Unsupported / prohibited overextensions

- Do NOT cite this as a 2024 preprint fact-source; the local, admissible source is the 2025 published article (metadata above). Keep bib-update handling in the change-request pipeline, not in prose.
- Do NOT claim eGSK is best at D = 10 (it is significantly worse than AGSK there) or best at D = 100 vs all metaheuristics (DEPSO ranks first at D = 100).
- Do NOT claim eGSK beats FOWFO significantly — all Wilcoxon vs FOWFO are non-significant.
- Do NOT present the SOTA comparison as a common-environment rerun — numbers were taken from original papers.
- Do NOT attribute LPSR or parameter pools to eGSK — its NP is fixed at 100 with Kr = 1 and phase-specific Kf adaptation.

## 10. Role in DT-GSK framing (Appendix B.1)

`jawad2024egsk` — eGSK family baseline and verified mechanism scope: defines exactly which mechanisms eGSK contains (and does not contain), anchoring DT-GSK's family panel and the discussion of the runnable EGSK port (scipy-SLSQP substituting for MATLAB's SQP/fmincon).

## 11. Verification quotations (minimal)

- "the eGSK algorithm performs exceptionally well at solving optimization problems with 30, 50, and 100 dimensions and is competitive in 10 dimensions." (Abstract, p. 1)
- "the Kf1, Kf2 Parameters will be Self-adaptive after 75 % of MAXNFEs." (Sect. 3.2.2, p. 5)
- "Sequential quadratic programming (SQP) as a local search at 75 % of MAXNFEs helps the algorithm to escape from the local minimum solution" (Sect. 3.2.3, p. 6)
- "Select Case-1, Case-1 variant was stronger than its competitors in the original literature." (FDBAGSK row, Table 3, p. 9)
