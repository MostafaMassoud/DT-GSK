# Evidence card — tanabe2013shade

## Verified bibliographic identity
- Title: Success-History Based Parameter Adaptation for Differential Evolution
- Authors: Ryoji Tanabe; Alex Fukunaga (Graduate School of Arts and Sciences, The University of Tokyo)
- Venue/year: Proceedings of the 2013 IEEE Congress on Evolutionary Computation (CEC 2013)
- DOI (bib): 10.1109/CEC.2013.6557555
- Local file: `reference_papers/tanabe2013shade.pdf` (8 pp.)
- Inventory status: identity `verified`, readable, admissible. SHA-256 `bd41e3b637ce83f08f26f741797f42869ee26d37f865defe7fb5c8a62b320af3`.
- Locator convention: the local file carries NO printed proceedings page numbers (official pp. 71–78 are not shown); all locators below use local PDF pages 1–8 plus section/table numbers, which resolve unambiguously in the file.

## Research question and context
Does replacing JADE's single adaptive pair (μCR, μF) with a historical memory of several successful parameter means make DE parameter adaptation more robust, and does the resulting algorithm (SHADE) outperform state-of-the-art adaptive DE? (Abstract and Sec. I, PDF p. 1.)

Context: reviews DE basics (Sec. II, PDF pp. 1–2), related adaptive DE — jDE, SaDE, EPSDE, CoDE (Sec. III, PDF p. 2) — and JADE in detail (Sec. IV, PDF pp. 2–3), including current-to-pbest/1 (Eq. 7), the external archive with |A| = |P|, JADE's CR/F sampling (Eqs. 8–9) and updates (Eqs. 10–12), and Peng et al.'s weighted mean and restart extensions (Eqs. 13–14, PDF p. 3).

## Method
- Motivation: JADE's μCR, μF can be dragged toward poor values by a single unlucky generation; SHADE stores the per-generation means in historical memories M_CR, M_F with H entries so past good settings cannot be directly corrupted (Sec. V opening, PDF p. 3).
- Sampling: for each individual, a random memory index r_i ∈ [1,H]; CR_i = randn(M_CR,ri, 0.1), F_i = randc(M_F,ri, 0.1) (Eqs. 15–16, PDF p. 4; out-of-range handling as in JADE).
- Memory update: position k (cycling 1..H) is overwritten with weighted means — meanWA(S_CR) (Peng et al.'s Eq. 13, weights from fitness improvement) and the weighted Lehmer mean meanWL(S_F) (Eq. 19) — only when the generation produced successes; otherwise no update (Eqs. 17–18 and surrounding text, PDF p. 4).
- Greediness parameter p is randomized per individual: p_i = rand[p_min, 0.2], p_min = 2/N (Eq. 20, Sec. V-B, PDF p. 4), so no manual p tuning as in JADE.
- Full pseudocode: Algorithm 1, PDF p. 4; parameters recorded to S_CR, S_F only when strictly better (f(u) < f(x)), because zero-improvement weights would corrupt the weighted means (Sec. V-C, PDF p. 4).
- Relationship to SaDE's memory clarified in Sec. V-D (PDF pp. 4–5): SHADE stores generation means of successful sets, not raw values, and samples around a randomly chosen stored element.

## Experimental scope
- Primary: 28 CEC2013 benchmark functions, D = 30, MaxFES = D × 10,000 = 300,000, 51 runs, Wilcoxon rank-sum test at p < 0.05 (Sec. VI-A, PDF pp. 5–6; Table I, PDF p. 5).
- Comparators: JADE, dynNP-jDE, CoDE, EPSDE, using original authors' suggested parameters; CoDE/EPSDE/JADE Matlab code from Q. Zhang's site (Sec. VI, PDF pp. 5–6). SHADE used N = 100, H = 100.
- Secondary: CEC2005 vs CoDE (Table II, PDF p. 6); 13 classical functions vs JADE (Table III, PDF p. 7) and vs dynNP-jDE (Table IV, PDF p. 7), replicating original-paper conditions.
- Boundary repair: midpoint rule as JADE (Eq. 21, PDF p. 6).
- Memory-size study H ∈ {5,…,500} (Table V, Sec. VI-C, PDF pp. 7–8) and infinite-memory variants (Table VI, Sec. VI-D, PDF p. 8).

## Conservative findings (with locators)
1. On CEC2013 (D=30), SHADE had the best overall performance among the five DEs: vs SHADE, CoDE was significantly better/worse/equal on 4/15/9 functions, EPSDE 0/23/5, JADE 2/10/16, dynNP-jDE 5/13/10 (Table I bottom rows, PDF p. 5; Sec. VI-A, PDF p. 6).
2. SHADE and JADE were the best group on unimodal F1–F5; dynNP-jDE led composites, with SHADE next (Sec. VI-A, PDF p. 6).
3. SHADE beat CoDE on CEC2005 (8 better / 12 worse for CoDE, 5 equal — read as CoDE + on 8; Table II caption/rows, PDF p. 6) and outperformed JADE and dynNP-jDE under their original classical-function conditions (Tables III–IV, PDF p. 7; "in each case, SHADE performs better", Sec. VI-B, PDF p. 7) — with the caveat that some final-generation differences may reflect implementation precision, not algorithmic difference (Sec. VI-B, PDF p. 7).
4. Performance depends on memory size H: H = 30, 50 slightly better than H = 100; H > 100 degrades monotonically; H = 100 is "a fairly good setting" (Table V, Sec. VI-C, PDF pp. 7–8).
5. All three infinite-memory (H = ∞) variants performed clearly worse than H = 100, so a finite tuned memory contributes significantly (Table VI, Sec. VI-D, PDF p. 8).

## Limitations
- D = 30 only for the main CEC2013 comparison; no higher-dimension evidence here.
- Population size fixed at N = 100; population-size reduction is not part of SHADE 1.0 (see tanabe2014improving).
- Cross-implementation precision issues acknowledged for CEC2005/classical comparisons (Sec. VI-A and VI-B, PDF pp. 6–7).
- This paper does not report the CEC2013 competition ranking of SHADE; competition-rank statements need another source (e.g., mohamed2017lshadespacma states SHADE ranked 3rd).

## Exact usable locators (claim → locator)
- Historical memory structure M_CR, M_F: Fig. 1 and Sec. V-A, PDF pp. 3–4.
- Parameter sampling from random memory slot: Eqs. (15)–(16), PDF p. 4.
- Weighted-mean/weighted-Lehmer memory update, update-only-on-success: Eqs. (13), (17)–(19), PDF p. 4.
- Randomized p_i ∈ [2/N, 0.2]: Eq. (20), PDF p. 4.
- Full algorithm: Algorithm 1, PDF p. 4.
- H as implicit learning rate replacing JADE's c: Sec. V-D, PDF pp. 4–5.
- Headline CEC2013 result and per-function table: Table I, PDF p. 5; summary counts at table bottom.
- Experimental protocol (51 runs, 300k FES, Wilcoxon p<0.05, error<1e-8 zeroed): Sec. VI-A, PDF p. 6.
- Memory-size sensitivity: Table V, PDF p. 8; infinite-memory result: Table VI, PDF p. 8.

## Supported uses in the DT-GSK manuscript
- Citing SHADE as the success-history parameter-adaptation mechanism extending JADE (memory of successful means, weighted Lehmer update, randomized p) — the adaptation style inherited by L-SHADE and by several adaptive GSK-family baselines.
- Supporting the design principle that a diversified memory of past successful settings is more robust than a single adapted pair (Sec. V, PDF p. 3).
- Protocol precedent: 51 runs / MaxFES = 10^4·D / Wilcoxon rank-sum for CEC-style comparisons.

## Unsupported / prohibited overextensions
- Do NOT cite this paper for L-SHADE, linear population-size reduction, or CEC2014 results.
- Do NOT cite it for SHADE's official CEC2013 competition rank (not stated here).
- Do NOT generalize the H-sensitivity findings beyond D = 30 CEC2013 (the authors flag higher-D as future work, Sec. VI-C, PDF p. 8).
- No claims about GSK operators; DE lineage only.

## Role in DT-GSK framing (Appendix B.3)
`tanabe2013shade` — SHADE lineage: success-history based parameter adaptation. Cited with tanabe2014improving for the SHADE/L-SHADE method lineage that forms the competitive DE context for the GSK family.

## Verification quotation (identity)
"Success-History Based Parameter Adaptation for Differential Evolution — Ryoji Tanabe and Alex Fukunaga, Graduate School of Arts and Sciences, The University of Tokyo" (PDF p. 1).
