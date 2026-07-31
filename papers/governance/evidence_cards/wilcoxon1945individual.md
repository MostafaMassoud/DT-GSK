# Evidence card — wilcoxon1945individual

## Verified bibliographic identity
- Title: Individual Comparisons by Ranking Methods
- Author: Frank Wilcoxon (American Cyanamid Co.)
- Venue/year: Biometrics Bulletin, Vol. 1, No. 6 (Dec. 1945), pp. 80–83
- DOI (bib): 10.2307/3001968 (JSTOR stable URL printed on cover page)
- Local file: `reference_papers/wilcoxon1945individual.pdf` (5 pp.; JSTOR scan)
- Inventory status: identity `verified`, readable, admissible. SHA-256 `34215448cbacd653211ba4282734d8ee0066f5902e6b062257a31f9984d01290`.
- Locator convention: printed journal pages 80–83 map to PDF pages 2–5 (PDF p. 1 is the JSTOR cover sheet). Locators below give printed page (PDF page).

## Research question and context
Can ranking methods — substituting rank scores 1, 2, ..., n for the actual numerical data — give "a rapid approximate idea of the significance of the differences" between two treatments, in both (a) unpaired replicated experiments and (b) paired-comparison experiments producing a series of signed differences? (p. 80 / PDF p. 2, opening paragraphs.)

Context: at the time, significance of mean differences was assessed with t/F tests; Friedman (1937) had proposed a rank test for several groups. Wilcoxon notes that Friedman's method for two groups reduces to the sign/binomial test (efficiency 63%), and proposes using the magnitudes of the differences as well as their signs, expecting higher efficiency (p. 80–81 / PDF pp. 2–3).

## Method
- Unpaired case (this is the origin of the two-sample rank-sum test): with q replicates per group, ranks 1..2q are assigned to all observations in order of magnitude; tied values receive the mean rank; the smaller rank sum is referred to Table I to obtain the probability of a total that small or smaller (p. 80 / PDF p. 2 and p. 81 / PDF p. 3).
- Paired case (this is the origin of the signed-rank test): rank numbers are assigned to the differences in order of magnitude neglecting signs; ranks of negative differences receive a negative sign; the test statistic is the sum of the rank numbers of one sign only (+ or −, whichever is less); referred to Table II (p. 81 / PDF p. 3 and p. 82 / PDF p. 4).
- Stated null hypothesis in the paired case: "we are dealing with a sample of positive and negative differences normally distributed about zero" (p. 81 / PDF p. 3).
- Exact null distributions are derived combinatorially by counting restricted partitions (unequal q-part partitions of the rank total; enumerated via Whitworth's partition tables and a partition correspondence attributed to MacMahon), with an explicit closed-form probability expression; tables can be prepared "for the 1 percent level or 5 percent level of significance or any other level desired" (pp. 81–83 / PDF pp. 3–5).

## Experimental scope
Illustrative worked examples only (no simulation study):
1. Fly-spray mortality, 8 replications per preparation (unpaired): rank sums 45 vs 91; P between 0.0104 and 0.021; parallel ANOVA gives F = 7.72 against 4.60 (5%) and 8.86 (1%) (p. 80 / PDF p. 2).
2. Fisher's cross- vs self-fertilized corn data, 15 paired differences: negative rank sum −24; P between 0.019 and 0.054; Fisher's t test gives 0.0497 (p. 80 / PDF p. 2).
3. Wheat seed-treatment, randomized blocks, 8 pairs: negative rank sum −3; P between 0.024 and 0.055; consistent with the ANOVA least-significant-difference conclusion (p. 80 / PDF p. 2).

## Conservative findings (with locators)
1. The paper introduces both the two-sample rank-sum procedure (unpaired) and the paired signed-rank procedure, with exact small-sample tables (Tables I and II) (pp. 80–82 / PDF pp. 2–4).
2. In the worked examples the rank tests give conclusions closely agreeing with the corresponding t/F analyses, "with only 8 pairs this method is capable of giving quite accurate information about the significance of differences of the means" (p. 80 / PDF p. 2).
3. Because it uses the magnitudes of the differences as well as their signs, the method "should have higher efficiency" than the sign/binomial test, "but its value is not known to me" — the author explicitly does not claim a proven efficiency (p. 81 / PDF p. 3).
4. Ties are handled by mean-rank assignment (p. 80 / PDF p. 2; p. 81 / PDF p. 3).

## Limitations
- Four-page note; no asymptotic theory, no power/efficiency results, no correction terms for ties or zeros — those were developed later by others (any such claim needs a different source).
- Tables I and II cover only the small numbers of replicates tabulated; the paper gives the partition-counting recipe for extending them.
- Text-extraction artifact: the numeric bodies of Tables I and II do not survive text extraction in the local scan (headers only); the tables are legible in the page images. Do not quote tabulated critical values from extracted text.
- The paired-case null is stated under a normality-centered-at-zero framing (p. 81 / PDF p. 3); the modern distribution-free symmetric-null formulation is a later reinterpretation, not this paper's wording.

## Exact usable locators (claim → locator)
- Purpose of ranking methods (rapid approximate significance): p. 80 (PDF p. 2), second paragraph.
- Two experiment categories (unpaired / paired): p. 80 (PDF p. 2), first paragraph.
- Unpaired ranking procedure and mean-rank ties rule: p. 80 (PDF p. 2); p. 81 (PDF p. 3).
- Paired signed-rank procedure (rank |differences|, sign attachment, min-sum statistic): p. 81 (PDF p. 3); p. 82 (PDF p. 4).
- Null hypothesis wording (paired case): p. 81 (PDF p. 3).
- Table I (unpaired significance): p. 81 (PDF p. 3). Table II (paired significance): p. 82 (PDF p. 4).
- Exact distribution via partition counting + probability formula: pp. 81–82 (PDF pp. 3–4).
- Efficiency remark (sign test 63%; higher expected, value unknown): p. 81 (PDF p. 3).
- Worked examples and agreement with t/F: p. 80 (PDF p. 2).

## Supported uses in the DT-GSK manuscript
- Citing the Wilcoxon signed-rank test (paired comparisons of two algorithms across runs or functions) to its original source.
- Citing the Wilcoxon rank-sum test (two independent samples) to the same paper if the manuscript uses the unpaired form.
- Supporting the statement that the test is based on ranks of the (absolute) differences with signs reattached and uses the smaller signed rank sum as statistic, with ties given mean ranks.

## Unsupported / prohibited overextensions
- Do NOT cite this paper for asymptotic normal approximations, ties/zeros corrections, continuity corrections, exact power or ARE values (e.g., 3/π vs t) — none of that is here.
- Do NOT cite it for the Mann–Whitney U formulation or its stochastic-superiority interpretation (that is Mann & Whitney 1947; and for A12 use vargha2000critique).
- Do NOT attribute distribution-free confidence intervals (Hodges–Lehmann etc.) to this paper.
- Do NOT cite it for multiple-comparison control (use holm1979simple / benjamini1995controlling) or for multi-algorithm rank tests (friedman1937use, demsar2006statistical).

## Role in DT-GSK framing (Appendix B.8)
`wilcoxon1945individual` — signed-rank test. Primary methodological citation for the per-function pairwise significance testing used in the DT-GSK statistical suite.

## Verification quotation (identity)
"INDIVIDUAL COMPARISONS BY RANKING METHODS — Frank Wilcoxon, American Cyanamid Co." (p. 80 / PDF p. 2); JSTOR cover: "Biometrics Bulletin, Vol. 1, No. 6 (Dec., 1945), pp. 80-83" (PDF p. 1).
