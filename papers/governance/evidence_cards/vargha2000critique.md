# Evidence card — vargha2000critique

## Verified bibliographic identity
- Title: A Critique and Improvement of the CL Common Language Effect Size Statistics of McGraw and Wong
- Authors: András Vargha (Dept. of Experimental Psychology, ELTE, Hungary); Harold D. Delaney (Dept. of Psychology, UNM, USA). [Accented first name renders as "Andrfis" in text extraction — artifact only.]
- Venue/year: Journal of Educational and Behavioral Statistics, Summer 2000, Vol. 25, No. 2, pp. 101–132
- DOI (bib): 10.3102/10769986025002101
- Local file: `reference_papers/vargha2000critique.pdf` (32 pp.)
- Inventory status: identity `verified`, readable, admissible. SHA-256 `85996798e0263ec930a007fa048be094bcc3f807382900f9460229c9e909b60e`.
- Locator convention: printed journal pages 101–132 map one-to-one to PDF pages 1–32. Locators give printed page (PDF page).

## Research question and context
McGraw and Wong (1992) proposed the "common language effect size" CL = P(X1 > X2) for continuous, normal distributions. Can CL be generalized correctly to any (discrete or continuous) at least ordinally scaled variable, with exact point/interval estimation and significance tests, and are McGraw–Wong's own multi-group / discrete / correlated-samples generalizations sound? (Abstract, p. 101 / PDF p. 1; overview, pp. 102–103 / PDF pp. 2–3.)

## Method
- Core proposal — the measure of stochastic superiority: A12 = P(X1 > X2) + 0.5·P(X1 = X2) (Eq. (2), p. 102 / PDF p. 2). A applies to any ordinal-or-better variable and equals CL in the continuous case (p. 102).
- Identities: A12 = 1 − A21 (Eq. (3)); stochastic equality defined by A12 = A21 = 0.5 (Eq. (4)); equivalently P(X1 > X2) = P(X1 < X2) (Eq. (5)) (pp. 102–103 / PDF pp. 2–3).
- Relation to Cliff's stochastic difference δ = p+ − p−: A12 = (δ + 1)/2, δ = 2·A12 − 1 (Eqs. (8)–(10), p. 104 / PDF p. 4).
- Interpretation guidelines (Table 1, p. 106 / PDF p. 6): values corresponding to Cohen's small/medium/large standardized differences for normal distributions — A12 ≈ .56 (small), .64 (medium), .71 (large); δ ≈ .11, .28, .43.
- Point estimation (Section 2, p. 107 / PDF p. 7): Â12 = [#(Xi > Yj) + 0.5·#(Xi = Yj)]/(mn) (Eq. (12)), unbiased; rank-sum computing formula Â12 = (R1/m − (m+1)/2)/n (Eq. (14)) using the Mann–Whitney–Wilcoxon rank sum R1.
- Tests of A = .5 (stochastic equality; Section 3, pp. 108–117 / PDF pp. 8–17): the MWW test is consistent against alternatives iff the populations are stochastically unequal, but is not robust to variance heterogeneity; three robust alternatives are examined — the Fligner–Policello (FP) test, Cliff's modified FP (FPC), and Welch's t on ranks (rank Welch, rW).
- Confidence intervals for A12 via FP/FPC (CI for δ transformed by (δ+1)/2) and via rank Welch with t(dfw) quantiles (Section 4, pp. 118–120 / PDF pp. 18–20; Eqs. (24), (31)).
- Critique of McGraw–Wong generalizations: their discrete CLg is not a proper generalization and can be uninterpretable (pp. 105–106 / PDF pp. 5–6); their multi-group CLg lacks a constant no-effect baseline (estimated CLg ≈ .33/.26/.23 for 3/4/5 identical groups; pp. 120–121 / PDF pp. 20–21). Correct multi-group alternatives: stochastic homogeneity (all Aiu = .5) tested by rank ANOVA / Kruskal–Wallis, and effect measures AAD/AAPD (Section 5, pp. 121–127 / PDF pp. 21–27); correlated-samples generalization Axy with sign test and Friedman-test connection (Section 6, pp. 127–129 / PDF pp. 27–29).

## Experimental scope
Monte Carlo study (pp. 111–117 / PDF pp. 11–17): generalized lambda distributions; skewness α3 ∈ {0, 2}, three kurtosis levels each; variance ratios 1:1 and 1:9 (σ ratio 1:3); average sample sizes 9 and 18; balanced and unbalanced (n = 2m) designs with direct and inverse variance–size pairing; null of stochastic equality enforced by empirically determined shifts (Table 2, p. 113); 100,000 iterations per condition; two-tailed α = .05 (results in Tables 3–4, pp. 115–116 / PDF pp. 15–16).

## Conservative findings (with locators)
1. A12 is the unique linear transformation of Cliff's δ that reduces to CL in the continuous case, and is meaningful for any ordinal variable (p. 104 / PDF p. 4).
2. Â12 from Eq. (14) is unbiased and computable from MWW rank sums available in standard packages (p. 107 / PDF p. 7).
3. Benchmarks for interpreting A12 (.56/.64/.71) derive from Cohen's small/medium/large under normality and are offered as guidelines, not universal cutoffs (Table 1 and note, p. 106 / PDF p. 6).
4. Under equal variances the rank t test holds its nominal level; under unequal variances paired with unequal sample sizes it degrades badly (up to ~.13 at nominal .05), while rank Welch stays only slightly inflated (~.06–.07); small-sample exact FP/FPC behave best in the direct-pairing case (Tables 3–4, pp. 115–116; discussion points 1–6, pp. 114–117 / PDF pp. 14–17).
5. Large-sample (normal-approximation) versions of FP and FPC are consistently inflated; the authors recommend exact critical values for n, m ≤ 30 (point 3, p. 117 / PDF p. 17).
6. McGraw–Wong's multi-group and discrete generalizations of CL are formally defective (no constant null baseline; k-tuple output) — the stated motivation for A (pp. 105–106, 120–121 / PDF pp. 5–6, 20–21).
7. Worked example (admissions data, m = 16, n = 78): Â12 = .762 with .95 CI ≈ (.63, .90) via rank Welch — "substantial dominance" per Table 1 (Example 2, pp. 119–120 / PDF pp. 19–20).

## Limitations
- The Monte Carlo study is small (six lambda distribution types, two variance ratios, two average sizes) and the authors call the multi-group methods "sometimes tentative", needing further validation (p. 130 / PDF p. 30).
- Robust-test recommendations are for testing stochastic equality, not location equality; under asymmetry these hypotheses differ (pp. 111–112 / PDF pp. 11–12).
- Guideline thresholds are derived under normal-shift assumptions; the paper does not validate them for arbitrary distributions (p. 106).
- Not a source for algorithm benchmarking practice; all examples are behavioral-science data.

## Exact usable locators (claim → locator)
- Definition A12 = P(X1 > X2) + .5·P(X1 = X2): Eq. (2), p. 102 (PDF p. 2).
- CL definition and McGraw–Wong context: Eq. (1), p. 102 (PDF p. 2).
- A12 = 1 − A21; stochastic equality A = .5: Eqs. (3)–(5), pp. 102–103 (PDF pp. 2–3).
- Relation to Cliff's δ: Eqs. (8)–(10), p. 104 (PDF p. 4).
- Interpretation thresholds A12 = .56/.64/.71 (δ = .11/.28/.43): Table 1, p. 106 (PDF p. 6).
- Unbiased sample estimator and rank-sum formula: Eqs. (12) and (14), p. 107 (PDF p. 7).
- MWW consistency iff stochastic inequality: pp. 108–109 (PDF pp. 8–9).
- MWW non-robustness to variance heterogeneity: p. 109 (PDF p. 9).
- Robust tests (FP, FPC, rank Welch) definitions: pp. 109–111 (PDF pp. 9–11), Eqs. (15)–(18).
- Monte Carlo design and Type-I error tables: pp. 113–116 (PDF pp. 13–16), Tables 2–4.
- CI construction for A12: Section 4, pp. 118–119 (PDF pp. 18–19), Eqs. (24), (31).
- Multi-group critique and AAD/AAPD: pp. 120–127 (PDF pp. 20–27), Eqs. (36)–(37), (44).
- Correlated-samples Axy and sign-test connection: Eqs. (50)–(52), p. 127 (PDF p. 27).

## Supported uses in the DT-GSK manuscript
- Citing the A12 (Vargha–Delaney) effect size used to complement Wilcoxon tests in pairwise algorithm comparisons: definition, unbiased rank-sum estimator, and the .56/.64/.71 interpretation guidelines (with their normal-theory provenance stated or implied as "conventional thresholds").
- Supporting the statement that A12 is a probability-based, scale-free effect size valid for ordinal data and robust to non-normality, equal to CL for continuous variables.
- If the manuscript reports A12 confidence intervals, the rank-Welch/FP-based constructions here support that methodology.

## Unsupported / prohibited overextensions
- Do NOT attribute A12 to McGraw & Wong, nor cite this paper as merely "the CL statistic" — the paper's contribution is the corrected generalization A.
- Do NOT present .56/.64/.71 as distribution-free universal cutoffs; they are normal-based guidelines (Table 1 note, p. 106).
- Do NOT cite this paper for the Mann–Whitney U test itself (Mann & Whitney 1947; Wilcoxon 1945) or for Cliff's δ inference theory beyond what is reproduced here.
- Do NOT claim the paper validates A12-based comparisons of optimization algorithms or any benchmarking protocol.
- Do NOT use the multi-group AAD/AAPD machinery as if it were established practice; the authors themselves call it tentative (p. 130).

## Role in DT-GSK framing (Appendix B.8)
`vargha2000critique` — A12 effect size. Primary citation for the stochastic-superiority effect size reported alongside signed-rank/rank-sum p-values in the DT-GSK statistical suite.

## Verification quotation (identity)
"Journal of Educational and Behavioral Statistics, Summer 2000, Vol. 25, No. 2, pp. 101-132 — A Critique and Improvement of the CL Common Language Effect Size Statistics of McGraw and Wong — Andrfis [András] Vargha ... Harold D. Delaney" (p. 101 / PDF p. 1).
