# Evidence card — zhong2021gskhho

## 1. Verified bibliographic identity
- **Citation key:** `zhong2021gskhho`
- **Title (on source):** "A hybrid differential evolution based on gaining-sharing knowledge algorithm and harris hawks optimization"
- **Authors (on source):** Xuxu Zhong; Meijun Duan; Xiao Zhang; Peng Cheng
- **Venue/year (on source):** PLoS ONE 16(4): e0250951, published April 30, 2021; DOI 10.1371/journal.pone.0250951 (printed on every page)
- **Identity status (inventory):** `minor_metadata_mismatch` — identity certain; bib given-name errors: first author is **Xuxu** Zhong (bib "Xu"), third author is **Xiao** Zhang (bib "Xingxing"). Bib `number` field carries the article number e0250951.
- **Source file:** `reference_papers/zhong2021gskhho.pdf`, 24 pages, sha256 `d27e91637f79a1cdcf574389aa22ee7e6f1776bce7171161d531b7b8c33db62f`
- **Locator convention:** local PDF page N = printed page "N / 24"; cite as "p. N".

## 2. Research question and context
Can DE's exploration–exploitation balance be improved by (a) hybridizing its mutation stage with GSK's two-phase operators plus HHO's soft-besiege rule, and (b) tightening the internal coupling of mutation/crossover/selection through crossover-probability self-adaptation? (Abstract p. 1; motivations Sec. 3.1, p. 7.) Proposed algorithm: **DEGH**.

## 3. Method
- **Hybrid mutation operator, a "dual-insurance" mechanism of four strategies** (Sec. 3.2, pp. 7–8), selected per individual by two random numbers R1_i,g, R2_i,g compared against F and CR_i,g after GSK-style sorting/grouping of the population (Fig 1, p. 8):
  - **GSK/J-mutation** (R1≥F, R2<CR): streamlined GSK junior-phase rule with scaling factor F substituted for kf: V = X_i + F·(X_{i−1}−X_{i+1}) + F·(X_r−X_i) (Eq 21, p. 8).
  - **GSK/S-mutation** (R1<F, R2≥CR): GSK senior-phase rule, F for kf: V = X_i + F·(X_rpb−X_rpw) + F·(X_i−X_rm) (Eq 22, p. 8).
  - **DE/rand/1-mutation** (R1≥F, R2≥CR): classic Eq 2 (p. 4).
  - **HHO/SB-mutation** (R1<F, R2<CR): soft-besiege-derived V = ΔX + F·(X_best−X_i), ΔX = X_best−X_i (Eqs 23–24, p. 8).
- **Crossover-probability self-adaptation** (Sec. 3.3, Eq 25, pp. 8–9): per-generation usage frequencies of the four strategies (anum..dnum)/NP become CR values for individuals flagged by strategy, gated by a binary evolution-success variable h (failed trial ⇒ CR randomized in [0,1]).
- **GSK/HHO preliminaries** reproduced: GSK junior/senior equations and D_junior schedule (Eqs 5–7, pp. 4–5); HHO phases (Eqs 8–20, pp. 5–7).
- **Complexity:** DEGH adds only sorting O(NP) to DE; overall complexity stays O(NP·D·G) (Sec. 3.5, p. 9).

## 4. Experimental scope
- **Benchmarks:** 32 classical benchmark functions (Table 1, p. 11): f1–f14 unimodal, f15–f32 multimodal. NOT a CEC competition suite.
- **Dimensions:** D = 30, 50, 100 (Sec. 4.3, p. 13). (Abstract p. 1 and Conclusions p. 15 mention "D = 30,100" — the body includes D = 50 as well.)
- **Protocol:** G = 1000 generations, NP = 100, 30 independent runs (Sec. 4.1, p. 9); DEGH uses fixed F = 0.3 (Table 2, p. 12).
- **Comparators:** eight DE variants — IMMSADE, CIPDE, EBDE, EDE, EJADE, LSHADE-SPACMA, DEPSO, ATLDE (Sec. 4, p. 9; settings Table 2, p. 12).

## 5. Findings (conservative)
- **Wilcoxon signed-rank (+/−/≈), DEGH better on:** D=30: 26, 19, 24, 21, 24, 21, 26, 25 of 32 functions vs IMMSADE, CIPDE, EBDE, EDE, EJADE, LSHADE-SPACMA, DEPSO, ATLDE respectively (p. 13, citing Table 9). D=50: "27,24,26,26, 24,25 and 25" (p. 14 — the sentence lists only seven counts for eight comparators; a typographical omission in the source). D=100: 29, 27, 29, 27, 29, 27, 24, 24 (p. 14).
- **Friedman and Kruskal–Wallis tests:** DEGH best in all dimensions (Fig 6, referenced p. 14); Wilcoxon rank-sum R+ ≫ R− vs every comparator (Table 10, referenced p. 14).
- **D=30 detail:** DEGH reaches the global optimum on f1–f12, f16–f24, f27, f28, f30 (p. 13; Table 6, pp. 16 ff.).
- **Parameter studies (D=30):** insensitive to NP (Fig 3/Table 3, pp. 12–13); insensitive to F except F=0.1 (Table 4, p. 14; F=0.3 chosen); CR self-adaptation effective but DEGH not very CR-sensitive except CR=0.2 (Table 5, p. 15).
- **Authors' attribution of gains:** GSK's two-phase operators + DE/rand/1 + HHO soft besiege form a dual safeguard for exploration/exploitation; CR self-adaptation tightens the DE framework (Sec. 4.4, p. 15).

## 6. Limitations
- Classical benchmark functions, not CEC suites; budget in generations (G=1000), not FES-based; no runtime/FES accounting.
- Fixed scaling factor F = 0.3; findings tied to that setting.
- D=50 Wilcoxon summary sentence is incomplete in the source (7 counts for 8 algorithms).
- Uses GSK operators inside a DE framework — it is a DE variant borrowing GSK structure, not a GSK-family algorithm evaluated under GSK protocols.

## 7. Usable locators (claim → locator)
| Claim | Locator |
|---|---|
| DEGH hybridizes DE with GSK junior/senior operators and HHO soft besiege | Abstract p. 1; Sec. 3.2, pp. 7–8 |
| GSK junior/senior equations and D_junior schedule (as restated) | Eqs 5–7, pp. 4–5 |
| Four mutation strategies and their selection rules (Eqs 21–24) | pp. 8 |
| CR self-adaptation rule (Eq 25) | pp. 8–9 |
| Complexity O(NP·D·G) unchanged vs DE | Sec. 3.5, p. 9 |
| 32 functions, D=30/50/100, NP=100, G=1000, 30 runs, 8 DE-variant comparators | Sec. 4.1 p. 9; Table 1 p. 11; Sec. 4.3 p. 13 |
| Wilcoxon win counts at D=30 / D=50 / D=100 | pp. 13–14 (Table 9 referenced) |
| Friedman/Kruskal–Wallis: DEGH best in all dimensions | p. 14 (Fig 6) |
| GSK two-stage model balances exploration and exploitation (authors' premise) | Sec. 3.1, p. 7 |

## 8. Supported uses in the DT-GSK manuscript
- Related-work sentence: GSK's junior/senior operators have been extracted into a DE hybrid (DEGH, with HHO soft besiege and self-adaptive CR) and reported significantly better than eight DE variants on 32 classical functions at D=30–100 under a fixed-generation protocol.
- Evidence that the GSK two-phase structure is treated in the literature as an exploration/exploitation-balancing mechanism worth transplanting.

## 9. Unsupported / prohibited overextensions
- Do NOT present DEGH results as CEC-suite evidence or compare its numbers with CEC-protocol results (different functions, budget in generations).
- Do NOT claim DEGH outperforms GSK itself — GSK was not a comparator.
- Do NOT cite as evidence about GSK parameter settings (kf replaced by F=0.3 here).
- Do NOT quote a complete D=50 win-count list vs all eight comparators; the source sentence is defective.

## 10. Role in DT-GSK framing (Appendix B)
Appendix B.2 — "GSK variants and hybrids — related-work breadth only." Cite only where the verified mechanism (GSK operators hybridized into DE alongside HHO) is actually discussed.
