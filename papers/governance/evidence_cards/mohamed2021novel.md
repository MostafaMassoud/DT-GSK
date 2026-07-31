# Evidence card — mohamed2021novel

Group: family-panel task grouping; Appendix B role: **B.2 — GSK variants and hybrids, related-work breadth only** (this is a DE/SHADE-lineage paper cited in the family panel context, e.g., EBLSHADE appears as a comparator in mohamed2020agsk and apgsk2021).
Prepared: 2026-07-10, Phase 1 tasks 4–5. Read: mutation strategies (Sect. 4, pp. 5–7), setup (Sect. 5.1, p. 7), proposed-algorithm comparisons (Sect. 5.2, pp. 7–9), state-of-the-art comparisons (Sect. 5.3, pp. 9–12), conclusion (Sect. 6, pp. 12–13).

## 1. Verified bibliographic identity

- **Identity status: minor_metadata_mismatch, resolved; admissible.** Exact title match: "Novel mutation strategy for enhancing SHADE and LSHADE algorithms for global numerical optimization". Source-of-truth metadata from the local file: **Ali W. Mohamed, Anas A. Hadi, Kamal M. Jambi; Swarm and Evolutionary Computation 50 (2019) 100455; DOI 10.1016/j.swevo.2018.10.006** (printed p. 1). Bib errors recorded in the inventory: bib year 2021 (actual 2019), bib DOI 10.1016/j.swevo.2019.100455 (actual 10.1016/j.swevo.2018.10.006), bib third author "Mohamed, Ali K." (actual Kamal M. Jambi).
- Local file: `reference_papers/mohamed2021novel.pdf`, 14 PDF pages.
- **Locator convention: printed article pages 1–14 (equal to PDF pages) plus section/equation/table numbers.**

## 2. Research question and context

Can DE be improved by **ordered** mutation strategies that sort the vectors participating in the difference terms by fitness — a less greedy exploratory variant (ord_best) and a greedier exploitative variant (ord_pbest) — and can these mutations enhance SHADE and LSHADE via a hybridization framework? (Abstract p. 1; Sect. 1, pp. 1–2.)

## 3. Method

- **DE/current-to-ord_best/1 (ord_best)** (Sect. 4.1, Eq. (10), p. 5): for each target, three randomly selected vectors are ordered by fitness into ord_best / ord_median / ord_worst; v = x_i + F·(x_ord_best − x_i) + F·(x_ord_median − x_ord_worst). The directed differences (worst → better) "resemble the concept of the gradient" (p. 5).
- **DE/current-to-ord_pbest/1 (ord_pbest)** (Sect. 4.2, Eq. (11), p. 5): one vector drawn from the global top-p best, two random; the three are ordered as above. Designed for large populations (e.g., LSHADE's NP_init = 18×D) where plain ord_best degenerates toward DE/rand/1 (p. 5).
- **EDE / EBDE** (Sect. 4.3, pp. 5–6): the new mutations + SHADE's success-history parameter adaptation (memory H; Cauchy/normal sampling Eqs. (12)–(13); weighted Lehmer/arithmetic means Eqs. (14)–(17)).
- **ESHADE / EBSHADE / ELSHADE / EBLSHADE hybridization framework** (Sect. 4.4, Fig. 2, pp. 6–7): pbest mutation and ord_best (or ord_pbest) coexist in one population; a class-probability memory M_FCP assigns individuals to mutations; improvement ω (Eq. 19), improvement rate Δ clipped to (0.2, 0.8) (Eq. 20), memory update with learning rate c (Eq. 21). ELSHADE/EBLSHADE add LPSR (Eq. (18), Nmin = 4). Table 1 (p. 7) lists the six proposed algorithms; EBLSHADE = ELSHADE with ord_pbest.

## 4. Experimental scope

- **CEC2013**: 28 functions; setup text says D = 10, 30, 50 (Sect. 5.1, p. 7) though rank Table 2 also reports a 100D column (paper-internal inconsistency; see Limitations). 10,000×D FEs; 51 runs.
- **CEC2017**: 29 functions; D = 10, 30, 50, 100; 10,000×D FEs; 51 runs; error < 10⁻⁸ zeroed (Sect. 5.1, p. 7).
- **CEC2010 LSGO**: 20 functions; D = 1000; 3000×D FEs; 25 runs (Sect. 5.1, p. 7).
- Settings: without population reduction NP = 100 and memory size 100 (per SHADE); with reduction NP_init = 18×D, memory size 5 (per LSHADE) (p. 7).
- Statistics: Friedman + multi-problem Wilcoxon signed-rank at 0.05 (p. 7).

## 5. Conservative findings

- **CEC2013 Friedman (Table 2, p. 8): EBLSHADE first by mean rank (3.48) just ahead of LSHADE (3.50)**; ELSHADE third; LSHADE-family > SHADE-family throughout; LSHADE itself best at the 100D column.
- **CEC2017 Friedman (Table 3, p. 8): EBLSHADE first (mean rank 2.86), EBDE second (2.97), LSHADE third (3.39)**.
- Wilcoxon: EBLSHADE R+ > R− vs LSHADE in all dims except 100D (CEC2013) and except 10D (CEC2017) (Tables 5–6, narrative pp. 8–9); significance vs LSHADE is dimension-dependent, not universal.
- ord_best deteriorates under population-size reduction (large NP); ord_pbest is the suitable alternative (p. 8).
- **Vs state-of-the-art on CEC2013 (Table 8, p. 11): NBIPOPaCMAES first (2.48), EBLSHADE second (2.67), iCMAESILS third (2.93)**; Wilcoxon (Table 9, pp. 12–13): EBLSHADE ≈ NBIPOPaCMAES and iCMAESILS, significantly better than SMADE/MDE-pBX/CMAES/CCPSO2.
- ord_pbest plugged into LSHADE-cnEpSin and LSHADE-SPACMA (Tables 12–13, pp. 10–11): competitive but **no significant differences** (all p > 0.05).
- CEC2010 (D = 1000): ESHADE best among {EDE, SHADE, ESHADE} (Table 4, p. 8); vs literature (Table 14, pp. 11–12): jDElsgo best mean rank, ESHADE second; ESHADE ≈ jDElsgo by Wilcoxon (Table 15).
- Authors' scope statement (p. 12): "the main contribution of this study is to propose a new mutation strategy that could be integrated with other DE-based algorithms, and not to propose a 'Best' algorithm or competitor to defeat other state-of-the-art algorithms."

## 6. Limitations

- Bib metadata was wrong (year/DOI/third author) — resolved in the inventory; cite with the corrected 2019 metadata once the change request lands.
- CEC2013 dimension listing inconsistency: setup text says D = 10/30/50 (p. 7) while Table 2 reports a 100D column (p. 8) — when citing CEC2013 scope, prefer "10, 30, 50 (with an additional 100D column reported in Table 2)".
- EBLSHADE's edge over LSHADE is small (Friedman 3.48 vs 3.50 on CEC2013) and not uniformly significant; NBIPOPaCMAES outranks it on CEC2013.
- ord_pbest inside LSHADE-cnEpSin/SPACMA shows no significant improvement.
- This is a DE-lineage paper: it contains **no GSK content**; its relevance to the GSK family is only as (a) the EBLSHADE comparator used by AGSK/APGSK papers and (b) mutation-design lineage.

## 7. Exact usable locators (claim → locator)

| Claim | Locator |
|---|---|
| Published identity (SwEvo 50 (2019) 100455; DOI; Jambi) | p. 1 (title/footer) |
| ord_best definition + gradient-mimicking rationale | Sect. 4.1, Eq. (10), p. 5 |
| ord_pbest definition + large-population motivation | Sect. 4.2, Eq. (11), p. 5 |
| SHADE parameter-adaptation recap (memory, Lehmer mean) | Sect. 4.3, Eqs. (12)–(17), pp. 5–6 |
| Hybridization framework (M_FCP, Δ clipped to (0.2,0.8)) | Sect. 4.4, Eqs. (19)–(21), Fig. 2, pp. 6–7 |
| LPSR (Eq. 18, Nmin = 4); NP_init = 18×D, memory 5 | Sect. 4.4/5.1, p. 7 |
| Naming of six proposed algorithms; EBLSHADE = ELSHADE + ord_pbest | Table 1 + text, p. 7 |
| Protocols (CEC2013/2017 10,000×D 51 runs; CEC2010 3000×D 25 runs D=1000) | Sect. 5.1, p. 7 |
| CEC2013 Friedman (EBLSHADE 3.48 vs LSHADE 3.50) | Table 2, p. 8 |
| CEC2017 Friedman (EBLSHADE 2.86 first) | Table 3, p. 8 |
| ord_best degradation under population reduction | p. 8 |
| CEC2013 SOTA ranks (NBIPOPaCMAES > EBLSHADE) | Table 8, p. 11 |
| ord_pbest in cnEpSin/SPACMA: no significant difference | Tables 12–13 + narrative, pp. 10–11 |
| CEC2010 LSGO results (ESHADE 2nd to jDElsgo) | Tables 4, 14, 15, pp. 8, 11–12 |
| Authors' "not a Best-algorithm" scope statement | p. 12 |

## 8. Supported uses

- Related-work breadth: describing the ordered/directed-difference mutation idea (fitness-sorted difference vectors mimicking descent directions) as DE-lineage design relevant to DT-GSK's discussion of directed perturbations.
- Identifying EBLSHADE — the comparator used in mohamed2020agsk (Table XIV) and apgsk2021 (Table 14) — as "LSHADE + ord_pbest via an adaptive hybridization framework" from this source.
- Citing the empirical caveat that greedy ordered mutation needs p-best injection under large/reducing populations.

## 9. Unsupported / prohibited overextensions

- Do NOT cite as evidence about GSK — the paper contains no GSK mechanism or experiment.
- Do NOT claim EBLSHADE is state-of-the-art-best on CEC2013 — NBIPOPaCMAES ranks first (Table 8); the authors explicitly disclaim best-algorithm intent (p. 12).
- Do NOT claim uniform significant superiority of EBLSHADE over LSHADE — dimension-dependent, with reversals at CEC2013-100D and CEC2017-10D.
- Do NOT use the bib's 2021/DOI metadata in prose; the work is 2019 (metadata correction pending via change request).
- Per Appendix B.2: use only where the verified mechanism (ord_best/ord_pbest, hybridization framework) is actually discussed; no decorative citation.

## 10. Role in DT-GSK framing (Appendix B.2)

`mohamed2021novel` — related-work breadth only: DE/SHADE-lineage ordered-mutation design and the definition of EBLSHADE, which the GSK-family papers use as a competition-grade comparator. Not a GSK-family baseline itself.

## 11. Verification quotations (minimal)

- "the directed perturbations in the proposed mutation resemble the concept of the gradient as the difference vectors are directed from the worst to the better vectors" (Sect. 4.1, p. 5).
- "the main contribution of this study is to propose a new mutation strategy that could be integrated with other DE-based algorithms, and not to propose a 'Best' algorithm or competitor to defeat other state-of-the-art algorithms." (p. 12)
- Footer identity: "Swarm and Evolutionary Computation 50 (2019) 100455" (pp. 1–14 running footer).
