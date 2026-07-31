# Evidence card — demsar2006statistical

## Verified bibliographic identity
- Title: Statistical Comparisons of Classifiers over Multiple Data Sets
- Author: Janez Demsar
- Venue: Journal of Machine Learning Research 7 (2006), pp. 1-30
  (Submitted 8/04; Revised 4/05; Published 1/06) — printed on p. 1.
- Identity status (reference_inventory.csv): `verified`.
- Local file: `reference_papers/demsar2006statistical.pdf`, 30 pages, fully
  readable.
- Page-locator convention: **printed JMLR pages 1-30** (equal to PDF pages).

## Research question and context
Which statistical tests are theoretically safe and empirically sound for
comparing two or more algorithms over MULTIPLE data sets (as opposed to a
single data set)? (Abstract and Sect. 1, p. 1; problem formalization Sect. 2,
p. 2.)

## Method and scope
- Setting: k algorithms x N data sets; one reliable performance score per
  algorithm per data set; no variance recorded; sample size = number of data
  sets, "can therefore be as small as five and is usually well below 30"
  (Sect. 3, p. 5).
- Reviews and critiques: averaging across data sets (Sect. 3.1.1, pp. 5-6),
  paired t-test (commensurability, normality on small samples, outliers;
  Sect. 3.1.2, p. 6), sign test (Sect. 3.1.4, pp. 8-9), ANOVA (normality +
  sphericity assumptions likely violated; Sect. 3.2.1, p. 10).
- Presents in detail: Wilcoxon signed-ranks test with worked example
  (Sect. 3.1.3, pp. 7-8); Friedman test with average ranks R_j, the
  chi^2_F statistic (k-1 df) and the Iman-Davenport F_F refinement
  ("Friedman's chi^2_F is undesirably conservative"; Sect. 3.2.2, p. 11);
  post-hoc tests: Nemenyi critical difference
  CD = q_alpha sqrt(k(k+1)/(6N)) for all-pairs comparison, Bonferroni-Dunn,
  and step-wise Holm / Hochberg / Hommel procedures for comparison with a
  control (Sect. 3.2.2, pp. 11-13; critical-value tables Table 5, p. 12;
  worked example pp. 13-15).
- Introduces CD (critical difference) diagrams for visualizing post-hoc
  results (Sect. 3.2.4, pp. 15-16; Fig. 1, p. 16).
- Empirical part (Sect. 4): behavior of the tests on real classifiers/data
  sets with biased data-set selection, measuring rejection likelihood and
  replicability.

## Conservative findings (with exact locators)
1. Recommendation (Abstract, p. 1; Conclusion, p. 27): use non-parametric
   tests — Wilcoxon signed-ranks for TWO algorithms; Friedman test with
   corresponding post-hoc tests for MORE algorithms over multiple data sets.
2. The t-test over multiple data sets suffers commensurability, normality
   (N < 30), and outlier problems (Sect. 3.1.2, p. 6).
3. Wilcoxon is safer than t (no normality assumption, less outlier-driven);
   less powerful than t only when t's assumptions actually hold
   (Sect. 3.1.3, p. 8). Zero-difference handling: split ranks of d_i = 0
   evenly, drop one if odd count (p. 7).
4. Friedman statistic chi^2_F = 12N/(k(k+1)) [sum_j R_j^2 - k(k+1)^2/4] with
   k-1 df; chi-square approximation is for N and k "big enough (as a rule of
   a thumb, N > 10 and k > 5)", exact tables otherwise (Sect. 3.2.2, p. 11).
5. Iman-Davenport correction F_F = (N-1) chi^2_F / (N(k-1) - chi^2_F),
   F-distributed with (k-1, (k-1)(N-1)) df, less conservative than chi^2_F
   (Sect. 3.2.2, p. 11).
6. Nemenyi CD formula and critical values (p. 11 bottom - p. 12, Table 5a);
   use Nemenyi only for all-pairs comparisons.
7. When comparing against a control (one new method vs. others), use
   Bonferroni-Dunn or preferably step procedures: "Holm's procedure is more
   powerful than the Bonferroni-Dunn's and makes no additional assumptions"
   (p. 13); comparing all pairs when the question is new-vs-existing wastes
   power (p. 12).
8. FDR procedures are noted but deemed "less suitable" for algorithm
   evaluation because the acceptable false discovery rate must be chosen
   (p. 13).
9. The omnibus Friedman test can be significant while the post-hoc detects
   nothing (lower power) — only "some algorithms differ" may then be claimed
   (p. 13).
10. CD diagrams neatly present rank order, magnitude, and significance
    (Sect. 3.2.4, pp. 15-16; Conclusion, p. 27).
11. Non-parametric tests are "appropriate since they assume some, but limited
    commensurability", safer, and applicable to any evaluation measure
    including computation times (Conclusion, p. 27).
12. Replicability of the tests can be a problem: "the actual experiments
    should be conducted on as many data sets as possible" (Conclusion,
    p. 27).

## Limitations relevant to citation
- Written for classifier comparison over data sets; transfer to optimizer
  comparison over benchmark functions is a community convention built ON this
  paper, not something this paper itself validates.
- Requires independent "tasks" (data sets / here benchmark functions) and one
  reliable aggregated score per task; multiple runs feed the score, not the
  test (Sect. 3, p. 5; Sect. 3.2.3, p. 15: no test available for dependent
  multiple observations per cell).
- The empirical study deliberately avoids Type 1/Type 2 error quantification
  (Conclusion, p. 27).
- Sign test has low power (pp. 8-9); counting only "significant wins" is an
  invalid practice (p. 9).

## Supported uses in the DT-GSK manuscript
This is the PRIMARY methodology citation for the statistical protocol
(master Sect. 7.5-7.6; Appendix B.8):
- Friedman omnibus test on per-task ranks (Sect. 3.2.2, p. 11).
- Iman-Davenport F correction, pre-registered per CR-0003 (p. 11).
- Nemenyi critical-difference diagram for all-pairs display, incl. the CD
  formula used by `papers/scripts/generate_nemenyi_cd.py` (pp. 11-12,
  Table 5a; diagrams Sect. 3.2.4, pp. 15-16).
- Holm-adjusted comparisons of DT-GSK vs. each comparator as the
  control-based family (pp. 12-13).
- Wilcoxon signed-rank for paired two-algorithm comparisons, including the
  tie/zero-handling rule the master requires to be reported (Sect. 3.1.3,
  pp. 7-8).
- Justifying WHY non-parametric tests are used instead of t-test/ANOVA
  (Sects. 3.1.2, 3.2.1; Conclusion p. 27).
- Statistical-reporting presentation conventions for the Phase 4 register
  (master Sect. 8.7 explicitly names this source).

## Unsupported / prohibited overextensions
- Do NOT use Nemenyi when the manuscript's question is DT-GSK vs. each
  comparator (control structure) — the paper itself says all-pairs post-hoc
  wastes power there (p. 12); Nemenyi display only when design matches
  (master Sect. 7.5).
- Do NOT run both Friedman post-hoc families and mix conclusions, and do not
  claim an algorithm "belongs to two groups" in a CD diagram (explicitly
  called "a statistical nonsense", p. 14).
- Do NOT feed per-run (paired, dependent) observations into the Friedman
  test as if they were independent tasks (Sect. 3.2.3, p. 15).
- Do NOT cite this paper for effect sizes (A12), bootstrap CIs, or FDR
  methodology — it does not develop them (FDR only mentioned p. 13);
  use vargha2000critique, efron1993introduction, benjamini1995controlling.
- Do NOT claim the recommended tests control Type 1/2 error at exact rates
  for optimizer comparisons; the paper provides no such quantification
  (p. 27).

## Role in DT-GSK framing (Appendix B.8)
Friedman/rank/post-hoc practice anchor: justifies the choice, order
(omnibus -> post-hoc), display (CD diagram), and multiplicity handling (Holm
as primary control-family adjustment) of the manuscript's comparison
statistics.

## Verification quotation (identity)
"we recommend a set of simple, yet safe and robust non-parametric tests ...
the Wilcoxon signed ranks test for comparison of two classifiers and the
Friedman test with the corresponding post-hoc tests for comparison of more
classifiers over multiple data sets" (Abstract, p. 1).
