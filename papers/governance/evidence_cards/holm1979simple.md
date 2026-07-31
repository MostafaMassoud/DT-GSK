# Evidence card — holm1979simple

## Verified bibliographic identity
- Title: A Simple Sequentially Rejective Multiple Test Procedure
- Author: Sture Holm (Chalmers University of Technology, Göteborg)
- Venue/year: Scandinavian Journal of Statistics, Vol. 6, No. 2 (1979), pp. 65–70
- DOI: none in bib; none printed in file (JSTOR stable URL 4615733 on cover)
- Local file: `reference_papers/holm1979simple.pdf` (7 pp.; JSTOR scan)
- Inventory status: identity `verified`, readable, admissible. SHA-256 `2918f8b5a994a1c149104d61502d1d94fcfc9e5e9a34f4d9ceabb751bbf7cd2a`.
- Locator convention: printed journal pages 65–70 map to PDF pages 2–7 (PDF p. 1 is the JSTOR cover sheet). Locators give printed page (PDF page).

## Research question and context
Can a simple, widely applicable multiple test procedure of the "sequentially rejective" type — hypotheses rejected one at a time until no further rejections — retain a prescribed protection against any type-I error (multiple level of significance α) for any combination of true hypotheses, while gaining power over the classical Bonferroni procedure? (Abstract, p. 65 / PDF p. 2.)

Context: multiple inference per Miller (1966); the definition of a multiple level of significance α "for free combinations" — for any non-empty index set I of true hypotheses, the supremum of P(∪_{i∈I} C_i) is ≤ α (Definition, p. 65 / PDF p. 2). Related prior work: Naik (1975) and the closed procedures of Marcus, Peritz & Gabriel (1976), which are equivalent to sequentially rejective tests but were not stated in this simple, general form (p. 66 / PDF p. 3). Sequentially rejective tests are coherent and consonant by construction (p. 66 / PDF p. 3).

## Method
- Setup: hypotheses H1..Hn with test statistics Y1..Yn; obtained (observed) levels R_k = the p-values of the separate tests; order them R(1) ≤ R(2) ≤ ... ≤ R(n) with corresponding H(1)..H(n) (p. 66 / PDF p. 3).
- Sequentially rejective Bonferroni test (Scheme 1, p. 67 / PDF p. 4): compare R(1) with α/n; if R(1) ≤ α/n reject H(1) and compare R(2) with α/(n−1); continue, comparing R(k) with α/(n−k+1); stop at the first failure and accept all remaining hypotheses.
- Theorem 1 (p. 67 / PDF p. 4): the sequentially rejective Bonferroni test has multiple level of significance α for free combinations. Proof is a short Boole-inequality argument: with m true hypotheses, P(R_i > α/m for all true i) ≥ 1 − α, and on that event the procedure stops at step n+1−m or earlier, accepting all true hypotheses.
- The procedure is derived solely from the Boole inequality, hence "can be applied to any parametric or non-parametric model" — the only requirement is that an obtained level (p-value) can be computed for each separate test (p. 66 / PDF p. 3; p. 68 / PDF p. 5).
- Generalization to weighted (importance) constants c1..cn with statistics S_k = R_k/c_k and adjusted thresholds; Theorem 2 (Scheme 2) proves multiple level α for the generalized version (pp. 69–70 / PDF pp. 6–7).
- Variant for independent test statistics: replace α/n, α/(n−1), ..., α/1 by 1−(1−α)^{1/n}, 1−(1−α)^{1/(n−1)}, ..., 1−(1−α); slightly more powerful (p. 68 / PDF p. 5).

## Experimental scope
Analytical paper; no simulation suite. Numerical illustrations:
- Power example: Y_k ~ N(μ_k, 1), k = 1..10, one-sided tests at multiple level 0.05, with four μ = 0, four μ = 6, two μ = 3: classical Bonferroni rejects both μ = 3 hypotheses with probability 0.439, the sequentially rejective test with 0.565 (pp. 67–68 / PDF pp. 4–5).
- Comparison against the refined Dunnett closed test (9 treatments vs control, 4 observations each): successive critical t constants 1.70, 2.04, 2.23, ..., 2.71 for the sequential Bonferroni vs 1.70, 1.99, ..., 2.54 for the refined Dunnett — small power loss for far greater computational simplicity (p. 69 / PDF p. 6).

## Conservative findings (with locators)
1. The Holm procedure controls the familywise error rate (multiple level of significance α, free combinations) for arbitrary dependence among the test statistics, by the Boole inequality (Theorem 1, p. 67 / PDF p. 4).
2. It is uniformly at least as rejective as classical Bonferroni: obtained levels are compared with α/n, α/(n−1), ..., α/1 instead of always α/n; "Except in trivial non-interesting cases the sequentially rejective Bonferroni test has strictly larger probability of rejecting false hypotheses and thus it ought to replace the classical Bonferroni test at all instants where the latter usually is applied" (p. 67 / PDF p. 4).
3. The power gain depends on the alternative: small if all hypotheses are "almost true", considerable if a number of hypotheses are "completely wrong" (p. 67 / PDF p. 4).
4. The procedure cannot be used to construct smaller confidence sets than classical Bonferroni; used that way it degenerates to classical Bonferroni (p. 68 / PDF p. 5).
5. Two-sided/one-sided logical implications are handled: with paired one-sided hypotheses using opposite-signed statistics and α ≤ 1/2, contradictory double rejections cannot occur (p. 68 / PDF p. 5).
6. A weighted generalization directs power toward more important hypotheses (Theorem 2, pp. 69–70 / PDF pp. 6–7).

## Limitations
- Provides familywise error control only; no claims about false discovery proportion (that is benjamini1995controlling).
- Power comparisons are illustrative examples, not a systematic study.
- Confidence-set construction gains nothing over classical Bonferroni (p. 68 / PDF p. 5).
- Specialized closed procedures (e.g., refined Dunnett) remain somewhat more powerful in their parametric settings (p. 69 / PDF p. 6).
- OCR artifacts in extracted text (e.g., "R('1 <", "ac" for α); quote from page images, not raw extraction.

## Exact usable locators (claim → locator)
- Definition of multiple level of significance for free combinations: p. 65 (PDF p. 2).
- Coherence/consonance of sequentially rejective tests: p. 66 (PDF p. 3).
- Procedure definition (ordered p-values vs α/n, α/(n−1), ..., α/1; stop at first failure): Scheme 1 and surrounding text, pp. 66–67 (PDF pp. 3–4).
- FWER control theorem and Boole-inequality proof: Theorem 1, p. 67 (PDF p. 4).
- Uniform dominance over classical Bonferroni + "ought to replace" statement: p. 67 (PDF p. 4).
- Numerical power gain 0.439 → 0.565: pp. 67–68 (PDF pp. 4–5).
- Applicability to any parametric or non-parametric model / only p-values needed: p. 66 (PDF p. 3); p. 68 (PDF p. 5).
- Independent-statistics variant with (1−(1−α)^{1/k}) constants: p. 68 (PDF p. 5).
- Weighted generalization: Theorem 2 and Scheme 2, pp. 69–70 (PDF pp. 6–7).
- Confidence-set caveat: p. 68 (PDF p. 5).

## Supported uses in the DT-GSK manuscript
- Citing Holm's step-down (sequentially rejective Bonferroni) procedure as the family-wise multiplicity correction applied after per-function Wilcoxon tests or after a Friedman omnibus test.
- Supporting the statements that (a) Holm controls FWER under arbitrary dependence, (b) it is uniformly more powerful than the single-step Bonferroni correction, and (c) it requires only the individual p-values (works with non-parametric tests).

## Unsupported / prohibited overextensions
- Do NOT call it "Holm–Bonferroni step-down" with attributes not in the source (the paper's own name is "sequentially rejective Bonferroni test"; describing it as step-down is fine as a modern gloss but any formal property cited must be one proven here).
- Do NOT cite this paper for FDR control, Hochberg's or Hommel's step-up procedures, Šidák correction as such (only the independent-statistics variant above appears here), or adjusted-p-value formulations (later formalizations).
- Do NOT claim it yields shorter simultaneous confidence intervals (explicitly false per p. 68).
- Do NOT cite for power superiority over closed/parametric procedures — the paper concedes those are more powerful in their settings (p. 69).

## Role in DT-GSK framing (Appendix B.8)
`holm1979simple` — family-wise multiplicity control. Cited wherever the manuscript reports Holm-corrected p-values for multiple pairwise algorithm comparisons.

## Verification quotation (identity)
"Scand J Statist 6: 65-70, 1979 — A Simple Sequentially Rejective Multiple Test Procedure — STURE HOLM, Chalmers University of Technology, Göteborg. Received December 1977, revised September 1978" (p. 65 / PDF p. 2).
