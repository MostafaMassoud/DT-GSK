# Evidence card: nabahat2024hybrid

## Verified bibliographic identity
- Title: "Hybrid Noise Reduction Filter Using the Gaining–Sharing Knowledge-Based Optimization and the Whale Optimization Algorithms"
- Source authors (bib given names corrected from source): Mehrdad Nabahat, Farzin Modarres Khiyabani, Nima Jafari Navmipour
- Venue: SN Computer Science (2024) 5:417; **source DOI 10.1007/s42979-024-02674-y** (printed p. 1) — the bib's DOI 10.1007/s42979-024-02705-8 is wrong.
- Identity status (reference_inventory.csv): **minor_metadata_mismatch, admissible** — identity certain by exact title and journal header; bib given names and DOI wrong (corrections recorded in the inventory notes).
- 42-page PDF; article pagination "Page N of 41"; local PDF page k = article page k. Locators use article pages.

## Research question and context
Classical image de-noising filters remove noise but blur edges; parameter-based filters (generalized-Cauchy mask filter, bilateral filter) need proper parameter selection. Can WOA and GSK optimize (i) the generalized Cauchy (GC) mask parameters **including the mask size** and (ii) bilateral-filter parameters with GC kernels **including the neighboring radius**, to beat classical and PSO-optimized filters? (Abstract, p. 1; motivation and gap Table 1, p. 6).

## Method
Two proposed filters, each instantiated with WOA and with GSK (four variants: P1_WOA, P1_GSK, P2_WOA, P2_GSK):
1. **Filter 1 (GC mask)**: bivariate GC function (Eq. (21), p. 9) discretized into a convolution mask; optimized parameters beta, mu, theta and mask size w (odd, in [3,11], Eq. (26), p. 13), maximizing PSNR (Eq. (24), p. 13) as fitness (Sect. "Mask Design Using the GC Function", pp. 8–10; diagram Fig. 1, p. 9; pseudocode Algorithms 1–2, pp. 10–11). Extends Karami & Tafakori's PSO-based GC filter (their mask size was fixed at 3).
2. **Filter 2 (BL-GC bilateral)**: bilateral filter with GC kernels replacing Gaussian in both spatial and range domains (weight Eq. (22), p. 11; output Eq. (23), p. 12); optimized parameters beta_d, mu_d, theta_d, beta_r, mu_r, theta_r and neighboring radius r in [1,5] (Eq. (27), p. 13), window = 2r+1; PSNR fitness (Sect. "Bilateral Filter Using the GC Function", pp. 11–12; diagram Fig. 2, p. 11; Algorithms 3–4, pp. 12–13).
- GSK role: standard GSK (their ref. [45] = Mohamed et al. 2020) used as the optimizer; junior/senior update restated (Eq. (16) senior scheme and dimension Eqs. (17)–(18), p. 8); GSK parameters M = 20, umax = 50, k = 10, n(=p) = 0.1, kf = 0.5, kr = 0.9 (p. 16); filter-1 optimizer budget: 300 iterations, population 50; filter-2/PSO filters: 50 iterations, population 20 (pp. 13–16). Reported results average 20 executions (p. 16).

## Experimental scope
- Data: six standard grayscale test images (Barbara, Boats, Hill, Couple 512x512; Peppers, House 256x256; Kaggle standard-test-images) plus a Brain MRI (454x448) medical image (pp. 13–14, 29 [Table 11 context]).
- Noise: Gaussian noise at sigma = 20, 30, 50, 70; salt-and-pepper (SAP) noise at densities 0.02/0.03/0.05 (Tables 2–10).
- Comparators: Mean, Gaussian, Median, Wiener, Non-Local Means; GC_PSO (Karami & Tafakori), BW_PSO (Wang), BA_PSO (Asokan) (pp. 5–6; Table 1, p. 6).
- Metrics: PSNR, SSIM, FOM, EPF + execution time (pp. 6, 13–14).
- Statistics: Friedman test and multi-problem Wilcoxon signed-rank test, alpha = 0.05 (Sect. "Statistical Analysis", p. 21; Friedman Tables 12–14, pp. 29–30; Wilcoxon Tables 15–18, pp. 31 ff.).
- Environment: MATLAB R2012b, Core i5-2410M, 4 GB RAM, Win7 (p. 37).

## Conservative findings
- Gaussian noise (Friedman, Table 12, p. 29): P2_GSK ranks 1st on SSIM (1.13), PSNR (1.13), FOM (1.25), and ties 1st on EPF (1.75 with P2_WOA); P2_WOA 2nd; overall filter order P2_GSK > P2_WOA > BW_PSO > P1_GSK ~ P1_WOA > ... > Gaussian last (pp. 22, 29). Friedman p-value < 0.05 (p. 22).
- GSK-based variants edge out the WOA-based ones: "the GSK-based proposed filters are better than WOA-based filters" per the non-parametric tests (Conclusion, p. 39); Brain-MRI Friedman total: P2_GSK 1st (12.0), P2_WOA/BW_PSO tied 2nd (Table 14, p. 30).
- Representative PSNR numbers (Gaussian sigma = 20, Barbara, Table 3, p. 15): P2_GSK 27.1968 vs noisy 22.17, NLM 26.86, BW_PSO 26.90, GC_PSO 27.46 (GC_PSO occasionally best at low sigma; P2_GSK dominates at higher sigma, e.g., sigma = 70 Barbara: 22.133 vs GC_PSO 14.5886).
- SAP noise: the proposed filters are NOT suitable — the median filter ranks 1st (Table 13, p. 30); "the proposed filters are not suitable for SAP noise reduction" (Conclusion, p. 38). Note the SAP Friedman table includes only P1_WOA/P2_WOA among the proposals (10 filters, Table 13, p. 30).
- Execution time (Table 19, p. 36): GSK-based filters are faster than WOA-based counterparts (e.g., Barbara sigma=20: P1_GSK 153.0 s vs P1_WOA 433.7 s; P2_GSK 7082.7 s vs P2_WOA 8448.9 s); "the GSK algorithm is faster than WOA" (p. 37) — but P2 variants are by far the slowest filters overall (7 parameters to optimize; complexity Eqs. (33)–(35), pp. 36–37). CAUTION: the sentence on p. 37 ("execution time of P2_GSK and P1_GSK filters is longer than P2_WOA and P1_WOA") contradicts Table 19 and its own next sentence; cite Table 19, not that sentence.
- GSK-based filter convergence is faster in early iterations (Fig. 7 discussion, p. 37).

## Limitations (author-stated and observed)
- Author-stated: the original noiseless image must be available for the PSNR fitness (p. 5, "Disadvantages"); second filter has long execution time; no precise upper/lower bounds known for GC parameters (Conclusion, p. 39).
- Proposed filters fail on salt-and-pepper noise relative to the median filter (Conclusion, p. 38).
- Only grayscale test images + one MRI; 20 executions; small optimizer budgets for filter 2 (50 iterations, pop 20).
- GSK is used off-the-shelf as an optimizer; the paper contributes nothing to GSK's mechanism.
- Typographic inconsistency on p. 37 regarding GSK vs WOA execution time (see above).

## Exact usable locators (claim -> locator)
| Claim the DT-GSK manuscript may need | Locator (article pages) |
|---|---|
| GSK applied as parameter optimizer in image de-noising | Abstract, p. 1; Table 1, p. 6 |
| Rationale for choosing GSK (novelty, scalability, exploration/exploitation balance) | p. 5, paragraph "Due to the novelty of the GSK algorithm..." |
| GSK senior-scheme restatement + dimension split | Eqs. (16)–(18), p. 8 |
| GSK parameter settings used | p. 16 ("M = 20, umax = 50, k = 10, n = 0.1, kf = 0.5, kr = 0.9") |
| Filter-1 design (GC mask; mask size optimized) | pp. 8–10, Eq. (21), Eq. (26); Algorithms 1–2 |
| Filter-2 design (bilateral with GC kernels; radius optimized) | pp. 11–12, Eqs. (22)–(23), Eq. (27); Algorithms 3–4 |
| PSNR fitness definition | Eq. (24)–(25), p. 13 |
| Friedman results, Gaussian noise (P2_GSK 1st on all criteria) | Table 12, p. 29; discussion p. 22 |
| SAP noise: median filter best; proposals unsuitable | Table 13, p. 30; Conclusion, p. 38 |
| Brain-MRI Friedman (P2_GSK 1st) | Table 14, p. 30 |
| Wilcoxon per-filter comparisons | Tables 15–18, pp. 31 ff. |
| Execution times; GSK faster than WOA; P2 slowest overall | Table 19, p. 36; complexity Eqs. (33)–(35), pp. 36–37 |
| GSK-based filters better than WOA-based (statistical statement) | Conclusion, p. 39 |

## Supported uses in the DT-GSK manuscript
- Related-work breadth: an application of standard GSK (vs WOA) as the optimizer inside image de-noising filters, with Friedman/Wilcoxon evidence that the GSK-driven variants ranked first on Gaussian-noise removal and ran faster than the WOA-driven ones.
- Evidence of GSK's application spread beyond benchmark optimization (image processing), complementing the applications listed in other family papers.

## Unsupported / prohibited overextensions
- Do NOT cite as evidence about GSK's benchmark performance or mechanisms — GSK is used unmodified as a black-box optimizer.
- Do NOT generalize the "GSK faster than WOA" statement beyond this filter-fitness setting; and do not quote the contradictory p. 37 sentence (cite Table 19).
- Do NOT claim the proposed filters handle impulse (SAP) noise well — the paper states the opposite.
- Do NOT copy the bib's given names or DOI — both are wrong; use the source-corrected metadata above (inventory notes).
- Does not discuss DT-GSK.

## Role in DT-GSK framing (Appendix B)
Appendix B.2: related-work breadth only. Suitable at most for a clause on GSK's application to image de-noising / filter-parameter optimization.

## Verification quotations
- "Due to the novelty of the GSK algorithm, and the lack of wide applications in image processing, the GSK algorithm is used for noise removal purposes." (p. 5)
- "The results of the used non-parametric tests show that the GSK-based proposed filters are better than WOA-based filters." (Conclusion, p. 39)
- "the proposed filters are not suitable for SAP noise reduction." (Conclusion, p. 38)
