# Evidence card — friedman1937use

## Verified bibliographic identity
- Title: The Use of Ranks to Avoid the Assumption of Normality Implicit in
  the Analysis of Variance
- Author: Milton Friedman (National Resources Committee)
- Venue: Journal of the American Statistical Association, Vol. 32, No. 200
  (Dec. 1937), pp. 675-701. JSTOR stable URL printed on cover page.
  DOI in BibTeX: 10.1080/01621459.1937.10503522.
- Identity status (reference_inventory.csv): `verified`.
- Local file: `reference_papers/friedman1937use.pdf`, 28 PDF pages.
  READABILITY NOTE: the file is a JSTOR image scan with NO text layer beyond
  the cover; content was read visually from rendered page images (PDF p. 1 =
  JSTOR cover; PDF pages 2-28 = printed pages 675-701; PDF page = printed
  page - 673). All locators below are **printed page numbers 675-701**.

## Research question and context
Can ranked data replace raw measurements in two-way (row x column) analyses
so that significance testing needs "no assumption whatsoever ... as to the
distribution of the original variate", i.e., avoid the normality assumption
implicit in the analysis of variance? (p. 675.)

## Method and scope
- "Method of ranks": rank the data within each ROW of a two-way table, then
  test whether the COLUMNS of ranks can be supposed to come from the same
  universe, via a statistic chi_r^2 computed from the column mean ranks
  (p. 676).
- Statistic (p = number of columns/treatments, n = number of rows/blocks):
  chi_r^2 = (12n / (p(p+1))) * sum_j { r_bar_j - (p+1)/2 }^2, with the
  integer-only computational form
  chi_r^2 = 12/(n p (p+1)) * sum_j (sum_i r_ij)^2 - 3 n (p+1)
  (definition and derivation p. 678; computational formula p. 679).
- Distribution: "So long as the number of rows and columns is not too small,
  chi_r^2 computed in this way will be distributed according to the usual
  chi^2 distribution with p-1 degrees of freedom" (p. 679).
- Worked example: standard deviations of expenditures for 14 expenditure
  categories across 7 income levels (Tables I-II, pp. 676-677); chi_r^2 =
  40.1076 with 6 df, P ~ .000001 (p. 679).
- Handling of ties: assign each tied value the average of the ranks tied for
  (e.g., two values tied for ranks 2 and 3 each get 2.5); this is the
  preferred procedure and "does not affect the validity of the chi_r^2 test"
  (p. 681).
- Exact distributions of chi_r^2 tabulated for small cases (p = 3, n up to 9;
  p = 4, n up to 4; Tables V-VI region, pp. 688-693) and accuracy of the
  chi^2 approximation assessed: for p = 3 the chi^2 approximation is likely
  sufficiently accurate for n > 9; for p = 4, for n >= 6; "fairly accurate"
  more generally for n >= 6 (p. 693-694).
- Efficiency: for p = 2 the method reduces to the binomial/sign test of a
  mean difference with efficiency 63.7 per cent relative to normal-theory
  tests (p. 682); relation to rank correlation: for n = 2,
  chi_r^2 = (p-1)(1+r') where r' is the rank-difference correlation
  (p. 694).
- Empirical comparison with ANOVA: on 56 analyses of the expenditure data,
  the two methods "lead to similar conclusions" in 45 of 56; "In no case
  does one of the methods indicate a probability of less than .01 while the
  other indicates a probability greater than .05" (Table IV, p. 686).
- Mathematical appendix deriving moments of chi_r^2 (pp. 695-701; variance
  sigma^2 = 2 (n-1)(p-1)/n at p. 700, Eq. (26)).

## Conservative findings (with exact locators)
1. The Friedman test statistic definition and its chi^2(p-1) null
   approximation (pp. 678-679).
2. The test requires no assumption about the distribution of the original
   variate, and rows need not even share a distribution: "no assumption
   whatsoever needs to be made as to the similarity of the distribution of
   the original variate for the different rows" (pp. 680-681).
3. The method tests randomness of ranking; a significant chi_r^2 means the
   column mean ranks differ beyond chance (pp. 679, 681).
4. Caveats stated by Friedman: the method provides no test of interaction
   (p. 681); it may fail to detect an influence whose direction differs
   across rows (p. 681); "non-significant results do not establish the
   validity of the null hypothesis in the same way that significant results
   tend to contradict it" (p. 681).
5. Average-rank tie handling is valid (p. 681).
6. Loss of information relative to ANOVA is modest when ANOVA is valid
   (efficiency discussion pp. 681-682; agreement study Table IV, p. 686).
7. chi^2 approximation quality for small designs: adequate for p = 3 when
   n > 9 and for p = 4 when n >= 6; exact tables provided for smaller cases
   (pp. 688-694).

## Limitations relevant to citation
- The chi^2 approximation is asymptotic; with few tasks or few algorithms
  exact critical values (or the Iman-Davenport correction per
  demsar2006statistical and CR-0003) are the safer practice (pp. 679,
  688-694).
- The 1937 paper contains NO post-hoc procedure (no Nemenyi, no Holm) — those
  must be cited to demsar2006statistical / holm1979simple.
- The scan has no searchable text; quotations above were transcribed from
  page images and should be verified against the images if quoted verbatim
  in the manuscript.

## Supported uses in the DT-GSK manuscript
- Primary/origin citation for the Friedman test whenever the manuscript
  applies the omnibus rank test over benchmark tasks (master Sect. 7.5):
  statistic definition (pp. 678-679), df = k-1, chi^2 approximation
  (p. 679), tie handling by average ranks (p. 681).
- Citing that the test is distribution-free with respect to the underlying
  variate (pp. 675, 680-681) — the justification for using it on
  non-normal benchmark error distributions.
- Citing the small-sample accuracy boundary of the chi^2 approximation when
  defending the pre-registered Iman-Davenport refinement (pp. 688-694).

## Unsupported / prohibited overextensions
- Do NOT attribute post-hoc tests, critical-difference diagrams, or the
  Iman-Davenport correction to this paper.
- Do NOT cite it for the claim that Friedman is preferable to ANOVA in
  machine-learning/optimizer comparisons — that argument belongs to
  demsar2006statistical; Friedman 1937 only shows modest information loss on
  one 1935-36 expenditure data set (p. 686).
- Do NOT interpret a non-significant Friedman result as evidence of
  equivalence (explicitly warned against, p. 681).
- Do NOT use the p = 2 special case as a substitute for Wilcoxon signed-rank
  (efficiency only 63.7%, p. 682; Wilcoxon is the sanctioned pairwise test).

## Role in DT-GSK framing (Appendix B.8)
Origin citation for the Friedman rank test used in the suite-level omnibus
comparison; paired with demsar2006statistical for modern practice (post-hoc,
CD diagrams) and with the CR-0003 Iman-Davenport option.

## Verification quotation (identity)
"This test is made by computing from the mean ranks for the several columns a
statistic, chi_r^2, which tends to be distributed according to the usual chi^2
distribution when the ranking is, in fact, random" (p. 676; transcribed from
page image).
