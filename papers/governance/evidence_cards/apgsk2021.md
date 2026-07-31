# Evidence card — apgsk2021

Group: family-panel (Appendix B.1 — Foundation and GSK family)
Prepared: 2026-07-10, Phase 1 tasks 4–5. Source read in full (article pages 65934–65944; local PDF 13 pages incl. references/bios).

## 1. Verified bibliographic identity

- Title: "Gaining-Sharing Knowledge Based Algorithm With Adaptive Parameters for Engineering Optimization"
- Authors: Ali Wagdy Mohamed, Hattan F. Abutarboush, Anas A. Hadi, Ali Khater Mohamed
- Venue: IEEE Access, vol. 9, 2021, pp. 65934–65946; DOI 10.1109/ACCESS.2021.3076091 (printed on p. 65934).
- Identity status in `reference_inventory.csv`: **verified / readable / admissible** ("bib DOI found on page").
- Local file: `reference_papers/apgsk2021.pdf`, 13 PDF pages.
- **Locator convention: printed IEEE Access page numbers 65934–65944 (PDF page 1 = p. 65934) plus section/equation/table numbers.**

## 2. Research question and context

Can AGSK be further improved by (i) allowing small **negative** knowledge-factor values late in the search, (ii) an adaptive knowledge-rate scheme, (iii) **non-linear** population size reduction (NLPSR), and (iv) a much larger initial population? The paper is explicitly "an extended version of work published in [19]" (= AGSK, mohamed2020agsk) and states "AGSK [19] is the runner up in CEC2020 competition" (Sect. I, p. 65936).

## 3. Method (APGSK)

- GSK recap (Sect. II.A, pp. 65935–65937): initialization Eq. (1); junior/senior dimension split Eqs. (2)–(3) (DimJ = Dim·((Genmax−G)/Genmax)^k); junior/senior pseudo-codes Figs. 1–2 (p. 65936); GSK pseudo-code Fig. 3 and flow chart Fig. 5 (pp. 65936–65937); senior partition best/middle/worst = 100p% / NP−2·100p% / 100p%.
- **Adaptive (kf, kr) with negative-kf pool** (Sect. II.B.1, p. 65937): first 50% of MAXNFE uses the AGSK pool [(0.1, 0.2), (1.0, 0.1), (0.5, 0.9), (1.0, 0.9)]; **after 50% of MAXNFE the pool [(−0.15, 0.2), (−0.05, 0.1), (−0.05, 0.9), (−0.15, 0.9)] is activated with probability less than 0.3** "for enhancing the diversity of the population to ensure escaping from local optima and to reduce possibility of stagnation". Kw_P adaptation starts after 10% of FEs; improvement rate Eqs. (4)–(6) with minimum probability 0.05 and learning rate c (same machinery as AGSK).
- **Non-Linear Population Size Reduction (NLPSR)** (Sect. II.B.2, Eq. (7), pp. 65937–65938): N(G+1) = round[(Nmin − Ninit)·(NFE/MAXNFE)^(1−NFE/MAXNFE) + Ninit], **Nmin = 12** (keeps best/worst partitions ≥ 2 individuals, p. 65938).
- **Adaptive knowledge rate K** (Sect. II.B.3, p. 65938): per individual, "if rand > (NFE/MAXNFE), k = 0.5 else k = 2".
- Rationale for negative kf: improves diversity/escape early-middle and local-search tendency middle-end (Sect. I, p. 65935).

## 4. Experimental scope

- Suite: **CEC2020**, 10 functions (f1 unimodal; f2–f4 basic; f5–f7 hybrid; f8–f10 composition) (Sect. III.A, p. 65938).
- D = 5, 10, 15, 20; MaxFEs = 50,000 / 1,000,000 / 3,000,000 / 10,000,000; **30 independent runs**; errors < 10⁻⁸ zeroed (Sect. III.D, p. 65938).
- APGSK parameters (Sect. III.B, p. 65938): **NP = 200×D for D = 10, 15, 20; NP = 250 for D = 5**; p = 0.05 (best 5%, worst 5%, middle 90%); Kw_P init [0.85, 0.05, 0.05, 0.05]; c = 0.05.
- Baselines: GSK (kf = 0.5, kr = 0.9; K, P, NP as APGSK) and GSK_NLPSR (Sect. IV.A, p. 65939); LSHADE-family (LSHADE, EBLSHADE, ELSHADE-SPACMA, LSHADE-cnEpSin; Sect. IV.B); CEC2020 winners (IMODE = winner, AGSK = runner-up, J2020 = third; Sect. IV.C, pp. 65942–65943).
- Statistics: Friedman + multi-problem Wilcoxon signed-rank at 0.05, SPSS (Sect. IV, p. 65939). Complexity per CEC protocol, MATLAB R2014a (Sect. III.C, Table 1, p. 65938).

## 5. Conservative findings

- APGSK raw results: Tables 2–5 (pp. 65938–65939). Same qualitative pattern as AGSK (F1 solved everywhere; F2 traps; composition functions hardest; f5 degrades with dimension) (pp. 65938–65939).
- **Vs GSK / GSK_NLPSR** (Tables 6–9, pp. 65940; narrative pp. 65939–65941): both APGSK and GSK_NLPSR beat GSK on all functions except f1, gap grows with dimension; **Friedman (Table 10, p. 65941): APGSK first in all dims, GSK_NLPSR second, GSK third**; Wilcoxon (Table 11, p. 65941): APGSK significantly better in all cases except GSK_NLPSR at D = 20; overall inferior/equal/superior 3/5/68 of 76 (≈89.5% better, p. 65941).
- **Vs LSHADE-family** (Table 14 mean values, p. 65942; Friedman Table 12, p. 65941: **APGSK first overall, LSHADE second, EBLSHADE third, ELSHADE-SPACMA fourth, LSHADE-cnEpSin fifth**; Wilcoxon Table 13, p. 65941: significant in only 4 of 16 cases — vs LSHADE_cnEpSin at D = 10/15/20 and ELSHADE-SPACMA at D = 10); overall better/equal/worse 74.34% / 11.84% / 13.82% (p. 65943).
- **Vs CEC2020 winners** (Table 15 means, p. 65943; Friedman Table 16, p. 65944: APGSK first at D = 5/10/15, IMODE first at D = 20; **overall: APGSK 1st, IMODE 2nd, AGSK 3rd, J2020 4th**; Wilcoxon Table 17, p. 65944: **no significant difference in any case**; better/equal/worse 47.54% / 22.13% / 30.33%, p. 65944).
- Authors' diagnosis (pp. 65942–65943): LSHADE-based algorithms deteriorate on CEC2020's small dimensions with large budgets (stagnation/premature convergence), attributed to LSHADE's adaptation scheme and mutation.
- Source code link: https://sites.google.com/view/optimization-project/files (Sect. V, p. 65944).

## 6. Limitations

- Same scope limits as AGSK: CEC2020 only, D ≤ 20, 10 functions; no CEC2017/CEC2011 evidence.
- Winner comparisons show **no statistically significant differences** (Table 17); superiority over IMODE/J2020/AGSK is by rank counts and Friedman means only, and IMODE wins D = 20.
- Despite the title, **no engineering application is actually solved in the paper** — evidence is benchmark-only.
- The "LSHADE-family deteriorates at low dimensions" inference is the authors' interpretation of one suite/regime.
- GSK-family baselines here use APGSK's own K/P/NP settings for GSK, not the original GSK reference setting (comparability nuance, p. 65939).

## 7. Exact usable locators (claim → locator)

| Claim | Locator |
|---|---|
| APGSK = 4 modifications over AGSK; AGSK = CEC2020 runner-up | Sect. I, p. 65936 |
| Negative-kf pool after 50% MAXNFE, activation prob < 0.3 | Sect. II.B.1, p. 65937 |
| Kw_P adaptation machinery (Eqs. 4–6), min prob 0.05, learning rate c | Sect. II.B.1, p. 65937 |
| NLPSR formula, Nmin = 12 and partition rationale | Sect. II.B.2, Eq. (7), pp. 65937–65938 |
| Adaptive K rule (k = 0.5 or 2 by NFE/MAXNFE test) | Sect. II.B.3, p. 65938 |
| NP = 200×D (250 at D=5), p = 0.05, c = 0.05 | Sect. III.B, p. 65938 |
| CEC2020 protocol (10 fns, D = 5–20, budgets, 30 runs) | Sect. III.A/III.D, p. 65938 |
| Friedman: APGSK > GSK_NLPSR > GSK all dims | Table 10, p. 65941 |
| Wilcoxon vs GSK/GSK_NLPSR; 89.5% better | Table 11 + narrative, p. 65941 |
| Friedman vs LSHADE-family: APGSK 1st, LSHADE 2nd | Table 12, p. 65941 |
| Wilcoxon vs LSHADE-family: 4/16 significant | Table 13, p. 65941; narrative p. 65943 |
| Winners comparison: APGSK 1st overall, IMODE 2nd; no significant Wilcoxon differences | Table 15, p. 65943; Tables 16–17 + narrative, p. 65944 |
| LSHADE low-dimension deterioration claim (authors' inference) | pp. 65942–65943 |
| MATLAB source code availability | p. 65944 |

## 8. Supported uses

- Citing APGSK as the adaptive-parameter family baseline: negative-kf pool, NLPSR, adaptive K, enlarged NP — with exact settings for reproduction.
- Stating APGSK's Friedman-first results on CEC2020 vs GSK/GSK_NLPSR (significant) and vs LSHADE-family/CEC2020 winners (mostly non-significant; rank-based).
- Citing the documented fact that AGSK was the CEC2020 runner-up (p. 65936).
- Family-lineage narrative: GSK → AGSK → APGSK.

## 9. Unsupported / prohibited overextensions

- Do NOT claim APGSK significantly beats IMODE, J2020, or AGSK — Wilcoxon shows no significant differences (Table 17), and IMODE leads at D = 20.
- Do NOT claim APGSK was validated on engineering problems from this paper — the title notwithstanding, experiments are CEC2020 benchmarks only.
- Do NOT extrapolate the LSHADE-deterioration diagnosis beyond CEC2020's low-dimension/large-budget regime.
- Do NOT use this paper for CEC2017 protocol or results.

## 10. Role in DT-GSK framing (Appendix B.1)

`apgsk2021` — APGSK/adaptive-parameter family baseline: defines the APGSK mechanism DT-GSK's family panel includes, and documents the family's competition pedigree (AGSK runner-up CEC2020).

## 11. Verification quotations (minimal)

- "Actually, AGSK [19] is the runner up in CEC2020 competition." (Sect. I, p. 65936)
- "the another pairs: [(−0.15, 0.2), (−0.05, 0.1), (−0.05, 0.9), and (−0.15, 0.9)] will be activated after 50% of MAXNFE with probability less than 0.3" (Sect. II.B.1, p. 65937)
- "From the Wilcoxon's test at 0.05 level of significance, it could be observed that there is no significant difference between all the algorithms." (winners comparison, p. 65944)
