# Evidence card — mohamed2020agsk

Group: family-panel (Appendix B.1 — Foundation and GSK family)
Prepared: 2026-07-10, Phase 1 tasks 4–5. Source read in full (8 pages).

## 1. Verified bibliographic identity

- Title: "Evaluating the Performance of Adaptive Gaining-Sharing Knowledge Based Algorithm on CEC 2020 Benchmark Problems"
- Authors: Ali Wagdy Mohamed, Anas A. Hadi, Ali Khater Mohamed, Noor H. Awad
- Venue: Proceedings of the 2020 IEEE Congress on Evolutionary Computation (CEC); DOI 10.1109/CEC48606.2020.9185901; IEEE copyright line "978-1-7281-6929-3/20" on p. 1.
- Identity status in `reference_inventory.csv`: **verified / readable / admissible**.
- Local file: `reference_papers/mohamed2020agsk.pdf`, 8 pages, IEEE Xplore proceedings layout.
- **Locator convention: PDF page numbers p. 1–8 (no other pagination printed) plus section/table/figure numbers.**

## 2. Research question and context

Does replacing GSK's fixed knowledge factor (kf) and knowledge ratio (kr) with an adaptive, probability-pool mechanism (plus linear population size reduction) improve performance on the CEC 2020 bound-constrained suite? AGSK is the proposed extension of the original GSK [their ref. 7].

## 3. Method (AGSK = GSK + parameter adaptation + LPSR + dual-regime K)

- Basic GSK recap (Sect. II.A, pp. 2–3): initialization Eq. (1); experience equations Eqs. (2)–(3); junior pseudo-code Fig. 1 (p. 2); senior pseudo-code Fig. 2 (p. 3); GSK pseudo-code Fig. 3 (p. 3). Identical mechanics to mohamed2020gaining.
- **Adaptive (Kf, Kr) settings** (Sect. II.B, Fig. 4, p. 3): a parameter-setting pool of four (Kf, Kr) pairs **[(0.1, 0.2), (1.0, 0.1), (0.5, 0.9), (1.0, 0.9)]** with probability vector Kw_P; one setting assigned per individual by its probability; adaptation of Kw_P starts **after the first 10% of evaluations**; per-setting improvement ω_ps = Σ f(x_new) − f(x_old) (Eq. 4); improvement rate Δ_ps = max(0.05, ω_ps / sum(ω_ps)) (Eq. 5, 0.05 = minimum selection probability); update Kw_P(g+1) = (1 − c)·Kw_P(g) + c·Δ_ps (Eq. 6, c = learning rate).
- **Linear Population Size Reduction (LPSR)** (Sect. II.C, Eq. 7, pp. 3–4): N decreases linearly from N_init to **N_min = 12**.
- **Knowledge rate K** (Sect. II.D, p. 4): to mimic heterogeneous populations, K is assigned k ∈ (0,1) or k ≥ 1 each with probability 0.5; "k ∈ [1,20] is enough".

## 4. Experimental scope

- Suite: **CEC 2020** bound-constrained, 10 functions f1–f10 (f1 unimodal, f2–f4 basic, f5–f7 hybrid, f8–f10 composition) (Sect. III.A, p. 4).
- Dimensions/budgets: D = 5, 10, 15, 20 with MaxFEs = 50,000 / 1,000,000 / 3,000,000 / 10,000,000 respectively; **30 independent runs**; errors and SDs < 10⁻⁸ zeroed (Sect. III.D, p. 4).
- AGSK parameters (Sect. III.B, p. 4): initial **NP = 20×D**; p = 0.05; Kw_P initial = [0.85, 0.05, 0.05, 0.05]; **c = 0.05**.
- Baselines (Sect. III.E, pp. 5–6): GSK (kf = 0.5, kr = 0.9, NP = 20D, K and P as AGSK) and GSK_LPSR (GSK + LPSR); state-of-the-art LSHADE-family: LSHADE, EBLSHADE, ELSHADE-SPACMA, LSHADE-cnEpSin.
- Statistics: CEC2020 score metric (Score1 normalized errors + Score2 rank sums, 50/50; p. 5); multi-problem Wilcoxon signed-rank at α = 0.05, SPSS v20 (pp. 5–6). Complexity measured per CEC protocol on MATLAB R2014a, i7-4790, 12 GB RAM, Win10 (Sect. III.C, Table I, p. 4).

## 5. Conservative findings

- AGSK raw statistics per dimension: Tables II–V (pp. 4–5). F1 solved consistently at all dims; F2 traps AGSK in local optima; composition functions hardest (narrative p. 4).
- **Ablation vs GSK and GSK_LPSR** (Tables VI–IX, p. 5; narrative p. 6): AGSK and GSK_LPSR outperform GSK on everything except F1; superiority grows with dimension; LPSR alone "considerably improve[s]" GSK; AGSK better than GSK_LPSR at D = 10–20.
- **Score metric (Table X, p. 6): AGSK 100, GSK_LPSR 52.60, GSK 34.56.**
- **Wilcoxon vs GSK/GSK_LPSR (Table XI, p. 6)**: AGSK significantly better than both in all dimensions (borderline p = 0.050 ≈ decisions for GSK_LPSR at D = 15 and 20); overall AGSK inferior/equal/superior in 2/11/63 of 76 cases (≈83% better; p. 6).
- **Vs LSHADE-family (Table XIV, p. 8; Table XII, p. 7): AGSK score 100 vs ELSHADE-SPACMA 65.83, EBLSHADE 65.36, LSHADE 64.87, LSHADE-cnEpSin 55.04.** Wilcoxon (Table XIII, p. 7): significant only in 4 of 16 cases (vs LSHADE-cnEpSin at D = 10, 15, 20; vs EBLSHADE at D = 10); remaining 12 cases not significant; overall inferior/equal/superior 28/22/102 of 152 (≈67% better, 18.4% worse; p. 6).
- Conclusion (Sect. IV, p. 7): AGSK first by CEC2020 score metric; "statistically superior to and competitive with" previous CEC winners.

## 6. Limitations

- Only 10 functions and small dimensions (5–20); very large FE budgets relative to dimension — regime differs sharply from CEC2017 10,000×D.
- No Friedman test; score metric + Wilcoxon only.
- Most Wilcoxon comparisons vs LSHADE-family are not significant (12/16 ≈); the "beats the winners" narrative rests mainly on the score metric.
- Conference-length paper; no convergence/diversity analysis, no complexity comparison vs baselines beyond Table I.
- The claim that AGSK was the **runner-up of the CEC2020 competition is NOT in this paper** — it is stated in apgsk2021 (p. 65936). Cite apgsk2021 for that fact.

## 7. Exact usable locators (claim → locator)

| Claim | Locator |
|---|---|
| AGSK motivation: fixed kf/kr → adaptive | Abstract + Sect. I, pp. 1–2 |
| (Kf,Kr) pool [(0.1,0.2),(1.0,0.1),(0.5,0.9),(1.0,0.9)], Kw_P mechanism | Sect. II.B, Fig. 4, p. 3 |
| Adaptation starts after 10% of FEs; min prob 0.05; learning-rate update | Eqs. (4)–(6), p. 3 |
| LPSR with N_min = 12 | Sect. II.C, Eq. (7), pp. 3–4 |
| Dual-regime knowledge rate K (k∈(0,1) vs k≥1, prob 0.5; k∈[1,20]) | Sect. II.D, p. 4 |
| CEC2020 protocol: 10 fns, D = 5/10/15/20, FEs 5e4/1e6/3e6/1e7, 30 runs | Sect. III.A, III.D, p. 4 |
| AGSK settings NP = 20D, p = 0.05, Kw_P init, c = 0.05 | Sect. III.B, p. 4 |
| GSK baseline setting inside this paper (kf 0.5, kr 0.9, NP 20D) | p. 6 |
| AGSK/GSK_LPSR/GSK score 100/52.60/34.56 | Table X, p. 6 |
| Wilcoxon AGSK vs GSK & GSK_LPSR | Table XI, p. 6 |
| AGSK vs LSHADE-family scores (Table XII) and Wilcoxon (Table XIII) | p. 7 |
| Full mean±SD comparison vs LSHADE-family | Table XIV, p. 8 |
| Competition pedigree of comparators (LSHADE CEC2014 winner etc.) | p. 6 |

## 8. Supported uses

- Citing AGSK as the family's first adaptive-parameter variant: pool-based (Kf,Kr) adaptation, dual-regime K, LPSR with N_min = 12.
- Family-baseline description of AGSK's exact mechanism and parameter values for reproduction.
- Stating AGSK outperformed GSK and GSK_LPSR significantly on CEC2020, and topped the CEC2020 score metric against four LSHADE-family algorithms (with the caveat that most pairwise Wilcoxon tests vs those were not significant).

## 9. Unsupported / prohibited overextensions

- Do NOT cite this paper for "AGSK was runner-up of the CEC2020 competition" — that statement is in apgsk2021, p. 65936.
- Do NOT generalize AGSK's superiority to CEC2017/CEC2011 or to D ≥ 30 — evidence covers CEC2020, D ≤ 20 only.
- Do NOT claim statistically significant superiority over LSHADE/ELSHADE-SPACMA in general — 12/16 Wilcoxon cases were non-significant (Table XIII).
- Do NOT attribute negative-kf pools or non-linear population reduction to AGSK — those are APGSK features (apgsk2021).

## 10. Role in DT-GSK framing (Appendix B.1)

`mohamed2020agsk` — AGSK method and family baseline: source of the adaptive-pool parameter control that later variants (APGSK, FDBAGSK) inherit, and a panel baseline in DT-GSK's family comparison.

## 11. Verification quotations (minimal)

- "The parameter setting pool contains the following (Kf, Kr) pairs: [(0.1, 0.2), (1.0, 0.1), (0.5, 0.9), and (1.0, 0.9)]" (Sect. II.B, p. 3).
- "AGSK was the best algorithm according to CEC2020 metric with 100 score. GSK_LPSR and GSK ranked second and third" (p. 6).
- "the significance difference can be observed in four cases ... However, there is no significant difference in the remaining 12 cases." (p. 6, vs LSHADE-family)
