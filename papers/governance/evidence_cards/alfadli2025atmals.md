# Evidence card — alfadli2025atmals

Group: family-panel (Appendix B.1 — Foundation and GSK family)
Prepared: 2026-07-10, Phase 1 tasks 4–5. Read: contributions (Sect. 2.3), method (Sect. 3, pp. 7–19), settings (Sect. 4.1, p. 20), CEC2011/CEC2017 results (Sects. 4.2–4.4), statistics (Sect. 4.5, pp. 55–58), parametric study (Sect. 4.6, pp. 58–60), conclusions (Sect. 5, pp. 60–61).

## 1. Verified bibliographic identity

- Title: "Auto-Tuning Memory-Based Adaptive Local Search Gaining–Sharing Knowledge-Based Algorithm for Solving Optimization Problems"
- Authors: Nawaf Mijbel Alfadli, Eman Mostafa Oun, Ali Wagdy Mohamed
- Venue: Algorithms 2025, 18, 398 (MDPI); DOI 10.3390/a18070398 (printed on p. 1); published 28 June 2025.
- Identity status in `reference_inventory.csv`: **verified / readable / admissible**.
- Local file: `reference_papers/alfadli2025atmals.pdf`, 64 pages.
- **Locator convention: printed page numbers 1–64 (identical to PDF pages) plus section/equation/table/figure numbers.**

## 2. Research question and context

Can GSK's fixed control parameters (K = 10, Kf = 0.5, Kr = 0.9, P = 0.1) — blamed for premature convergence — be replaced by a **memory-based, Gaussian-driven auto-tuning** of five parameters (K, Kf, Kr, P, PLS) plus an **adaptive local search**, yielding better robustness and solution quality on CEC 2011 and CEC 2017? (Abstract p. 1; Sects. 2.3 and 3.2, pp. 6–11.)

## 3. Method (ATMALS-GSK)

- GSK recap (Sect. 3.1, pp. 7–10): Eqs. (1)–(2) junior/senior dimension split; junior phase Algorithm 2 (p. 9); senior phase Algorithm 3 (p. 10); overall GSK Algorithm 1 (p. 8). Original fixed values quoted: K = 10, Kf = 0.5, Kr = 0.9, P = 0.1 (Sect. 3.2, p. 10).
- **Adaptive parameter ranges** (Table 1, p. 11): K ∈ [5, 30] step 1 (initial 10); Kf ∈ [0.2, 0.8] step 0.1 (initial 0.5); Kr ∈ [0.85, 1] step 0.01 (initial 0.9); P ∈ [0.05, 0.15] step 0.01 (initial 0.1); PLS ∈ [1, 2]/ProbSize step 0.1 (initial 1); NLS = 0.05×PopSize; RPG ∈ [3, 5].
- **Gaussian enhancement rate** (Eq. (3), p. 15): per generation, each candidate parameter value gets an enhancement rate from a Gaussian centered at the currently selected value (GF, Eq. (4), σ = δ·(range), δ = 0.05·range per Algorithm 4), scaled by exp(−(Fnew−Fold)/Fold), where Fnew/Fold are the average fitness of the **top 50%** of the population in consecutive generations.
- **Exponentially weighted moving-average memory** (Eq. (5), p. 16): probabilities from historical enhancement rates with decay α = 0.97 (recent generations weighted more).
- **Powered roulette-wheel selection (RWS)** (Eqs. (6)–(7), pp. 16–17): selection probability ∝ Prob^RPG; RPG grows over generations (elitism sharpens from exploration to exploitation). Note: RWS selects **parameter values**, not individuals (p. 11).
- The same machinery tunes Kr (Sect. 3.2.2, p. 17), Kf (Sect. 3.2.3, p. 17), P (Sect. 3.2.4, p. 18), and PLS (Sect. 3.2.5, p. 18).
- **Adaptive local search** (Sect. 3.2.5, p. 18): each iteration, NLS = 0.05×PopSize randomly chosen solutions get per-dimension mutation with probability PLS/ProbSize; local-search range RangeLS shrinks linearly (Eq. (8), p. 18). Overall pseudo-code Algorithm 4 (p. 19); flowchart Fig. 3 (p. 12).

## 4. Experimental scope

- **CEC 2011**: 22 real-world functions; MaxFEs = 150,000; population 100 (⇒ 1500 iterations); **25 runs** (Sect. 4.1, p. 20).
- **CEC 2017**: 30 functions listed (29 used in statistics: "29 × 4 = 116 cases", p. 55); D = 10, 30, 50, 100; **FEs = 10,000×D**; **51 runs**; error < 10⁻⁸ zeroed (Sect. 4.1, p. 20).
- Comparators: family — GSK, AGSK, APGSK, FDBAGSK, eGSK; recent metaheuristics — IADE, GJO-JOS, QCSCA, cSM, FOWFO (Sect. 4 intro, p. 20).
- Statistics: Wilcoxon signed-rank + Friedman (Sect. 4.5).

## 5. Conservative findings

- **CEC 2011 vs GSK** (Table 3, p. 21; Table 4, p. 22): Wilcoxon R+ = 127, R− = 26, p = 0.0168; +12 / =5 / −5 → significant overall win; largest gains on hybrid/composition-like F17–F20 (narrative p. 22).
- **CEC 2017 vs GSK family** (Tables 9–12, pp. 42–54; Wilcoxon Table 17, p. 55): vs GSK significant "+" at every dimension; **at D = 10 not significant vs AGSK, APGSK, FDBAGSK, eGSK (and numerically behind FDBAGSK: 8/5/16)**; at D = 30 significant vs AGSK/APGSK/FDBAGSK (eGSK ≈, p = 0.0818); at D = 50 and 100 significant vs all five.
- **Friedman family ranking (Table 18, p. 56): overall — ATMALS-GSK 2.24 (1st), eGSK 2.84 (2nd), FDBAGSK 3.34 (3rd), AGSK 3.89 (4th), GSK 4.22 (5th), APGSK 4.44 (6th).** Per-dimension: at **D = 10 FDBAGSK ranks best (2.81) and ATMALS-GSK 3.37**; ATMALS-GSK ranks first at D = 30 (1.84), 50 (1.93), 100 (1.82).
- **Success ratios** (Sect. 4.5, p. 55; Conclusions p. 61): vs GSK 75%, AGSK 74.1%, APGSK 78.4%, FDBAGSK 66.4%, eGSK 65.5% (of 116 cases); vs IADE 96.6%, GJO-JOS 96.6%, QCSCA 87.1%, cSM 91.4%, FOWFO 54.3%.
- **Vs other metaheuristics** (Wilcoxon Table 19, p. 56; Friedman Table 20, p. 57): overall ranking ATMALS-GSK 1.72 (1st) vs FOWFO 1.75 (2nd) — FOWFO statistically ≈ at every dimension; IADE/GJO-JOS/cSM significantly worse nearly everywhere; QCSCA ≈ at D = 100.
- **Component ablation** (Sect. 4.6, Tables 21–22, pp. 59–60; Fig. 15, p. 60): full ATMALS-GSK significantly better than each single-adaptive-parameter variant (success ratios 75.9%, 82.7%, 79.3%, 82.7%, 65.5% vs ATMALS-GSK-1..5); Friedman p = 4.11×10⁻¹⁰.
- Adaptive-parameter trajectories: Figs. 7–8 (CEC2011, pp. 23–24), Figs. 10–11 (CEC2017, pp. 36–37).

## 6. Limitations (largely author-acknowledged, Conclusions p. 61)

- **Computational overhead** from memory mechanisms and local search — "might become significant in high-dimensional or real-time applications"; no complexity table is provided.
- Gaussian tuning "might need recalibration" for irregular landscapes; performance can vary by problem class.
- **D = 10 weakness**: only competitive, not superior (Wilcoxon ≈ vs all improved variants; Friedman D = 10 first place goes to FDBAGSK).
- Comparator results for eGSK/FDBAGSK etc. rely on the authors' reruns/collection; the paper does not detail per-competitor reimplementation provenance.
- Table 1 vs Algorithm 4 have small range inconsistencies (e.g., KVALUES "[5,30]" in Table 1 but "[1,...,30]" in Algorithm 4; Kr "[0.85,1]" vs "[0.8,...,1.0]"; P "[0.05,0.15]" vs "[0.05,...,0.2]") — cite Table 1 as the parameter specification and note the discrepancy if exact ranges matter.

## 7. Exact usable locators (claim → locator)

| Claim | Locator |
|---|---|
| Motivation: fixed GSK parameters → premature convergence | Abstract p. 1; Sect. 3.2, pp. 10–11 |
| Original GSK fixed values K=10, Kf=0.5, Kr=0.9, P=0.1 | Sect. 3.2, p. 10; Table 1, p. 11 |
| Adaptive ranges/discretization for K, Kf, Kr, P, PLS; NLS; RPG | Table 1, p. 11 |
| Gaussian enhancement rate; top-50% average fitness signal | Eqs. (3)–(4), p. 15 |
| Exponential weighted moving average, α = 0.97 | Eq. (5), p. 16; Algorithm 4, p. 19 |
| Powered RWS with growing power RPG | Eqs. (6)–(7), pp. 16–17 |
| Adaptive local search, NLS = 0.05×PopSize, shrinking RangeLS | Sect. 3.2.5 + Eq. (8), p. 18 |
| Full pseudo-code | Algorithm 4, p. 19 |
| Protocols: CEC2011 (150k FEs, 25 runs, NP=100); CEC2017 (10,000×D, 51 runs, D=10–100) | Sect. 4.1, p. 20 |
| CEC2011 Wilcoxon vs GSK (R+127/R−26, p=0.0168) | Table 4, p. 22 |
| CEC2017 family Wilcoxon per dimension | Table 17, p. 55 |
| Family Friedman ranks (ATMALS 1st overall; FDBAGSK 1st at D=10) | Table 18, p. 56 |
| Success ratios vs family and vs metaheuristics | Sect. 4.5, p. 55; Conclusions p. 61 |
| Metaheuristic Friedman (ATMALS 1.72 vs FOWFO 1.75) | Table 20, p. 57 |
| Component ablation results | Tables 21–22, pp. 59–60; Fig. 15, p. 60 |
| Acknowledged limitations (overhead, recalibration, variability) | Conclusions, p. 61 |
| Family mean±SD tables D = 10/30/50/100 (incl. eGSK, FDBAGSK columns) | Tables 9–12, pp. 42–54 |

## 8. Supported uses

- Citing ATMALS-GSK as the memory/local-search family baseline, with its exact adaptation machinery (Gaussian + EWMA + powered RWS + shrinking local search).
- Supporting statements that within the GSK family (as measured here), ATMALS-GSK ranks first overall on CEC2017 with eGSK second, and that its advantage grows with dimension while D = 10 is only competitive.
- Family-panel cross-checks: this paper provides an independent 51-run CEC2017 family table including GSK, AGSK, APGSK, FDBAGSK, eGSK at the standard 10,000×D budget.
- Citing the acknowledged computational-overhead limitation of memory-based adaptation + local search.

## 9. Unsupported / prohibited overextensions

- Do NOT claim ATMALS-GSK is significantly better than FOWFO — every Wilcoxon vs FOWFO is ≈ (Table 19), and Friedman margins are 1.72 vs 1.75.
- Do NOT claim superiority over the improved family variants at D = 10 — Wilcoxon ≈ (and 8/5/16 vs FDBAGSK); FDBAGSK ranks first at D = 10 in Table 18.
- Do NOT cite a runtime/complexity comparison — none is reported; only a qualitative overhead admission (p. 61).
- Do NOT treat CEC2020 or engineering applications as covered — only CEC2011 and CEC2017 are tested.
- Avoid quoting exact adaptive ranges without noting the Table 1 / Algorithm 4 inconsistency (Sect. 6 of this card).

## 10. Role in DT-GSK framing (Appendix B.1)

`alfadli2025atmals` — ATMALS-GSK and memory/local-search family baseline: the family's most recent adaptive/local-search member; its results table is a key external reference for DT-GSK's family-panel comparisons, and its D = 10 weakness parallels the low-dimension discussion in DT-GSK.

## 11. Verification quotations (minimal)

- "ATMALS-GSK surpasses GSK, AGSK, APGSK, FDBAGSK, and eGSK algorithms in 87, 86, 91, 77, and 76 cases out of all 29 × 4 = 116 cases" (Sect. 4.5, p. 55).
- "Although ATMALS-GSK performs similarly to improved variants like AGSK and APGSK at lower dimensions (e.g., for D = 10), it becomes noticeably superior as the problem size increases." (Sect. 4.5, p. 58)
- "The introduction of memory-based mechanisms and local search strategies inevitably adds computational overhead" (Conclusions, p. 61).
