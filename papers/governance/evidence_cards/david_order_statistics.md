# Evidence card — david_order_statistics

## Verified bibliographic identity
- Title: Order Statistics, Third Edition
- Authors: H. A. David; H. N. Nagaraja
- Venue/year: John Wiley & Sons, 2003 (© 2003; ISBN 0-471-38926-9 printed in the running text layer)
- DOI (bib): 10.1002/0471722162
- Local file: `reference_papers/david_order_statistics.pdf` — **PARTIAL EXCERPT, 12 pages**: Chapter 7, "Order Statistics in Nonparametric Inference", book pp. 159–170 (PDF p. 1 = book p. 159, ..., PDF p. 12 = book p. 170).
- Readability: **image-only scan.** Only PDF p. 1 carries an extractable text layer, and it is just the Wiley running copyright line ("Order Statistics, Third Edition. By H. A. David and H. N. Nagaraja, Copyright 2003 John Wiley & Sons, Inc. ISBN: 0-471-38926-9") — identity confirmation. All content below was read VISUALLY from the page scans; no machine-searchable quotes exist.
- Inventory status: identity `verified`, readability `partial_text_title_page_only`, admissible with citation use limited to the excerpted material. SHA-256 `fc190cb81f54fddc8e6729eb477ab250cafc0762bcc63da461a7d11d6029bb36`.
- Locator convention: book page numbers 159–170 (printed on the scans), equal to PDF page + 158.

## Research question and context
Chapter 7 treats three kinds of distribution-free intervals built from order statistics: confidence intervals for population quantiles (7.1), tolerance intervals (7.2), and prediction intervals (7.3) (chapter opening, p. 159).

## Method / content of the excerpt (visually read)
- Quantile definition: ξp solves F(x) = p for continuous strictly increasing F; general definition ξp = F^{-1}(p) = inf{x : F(x) ≥ p} (Eqs. 7.1.1–7.1.2, p. 159).
- Central distribution-free coverage result: for continuous X, the random interval (X(r), X(s)) covers ξp with probability
  π(r, s, n, p) = I_p(r, n−r+1) − I_p(s, n−s+1) = Σ_{i=r}^{s−1} C(n,i) p^i (1−p)^{n−i}
  (Eq. 7.1.4, p. 160) — depending on r, s, n, p but NOT on F; "essentially due to Thompson (1936)". Discrete-case one-sided bounds in Eqs. 7.1.5–7.1.7 (p. 160); lower/upper distribution-free bounds first obtained by Scheffé and Tukey (1945) (p. 160).
- Median intervals: with p = 1/2 and s = n−r+1, π reduces to 2·I_{1/2}(r, n−r+1) − 1 = 2^{−n} Σ_{i=r}^{n−r} C(n,i) (Eq. 7.1.8, p. 160); "Confidence intervals for the median are closely related to the sign test" (p. 160). Normal-approximation rule of thumb for n > 10: count off (1/2)·n^{1/2}·u_α observations either side of the sample median, rounding out (p. 161); Example 7.1.1: n = 100, α = 0.05 gives interval (x(40), x(61)) (p. 161).
- Refinements: Hettmansperger–Sheather interpolation between adjacent order statistics (p. 161, Example 7.1.2 p. 161); Beran–Hall linear interpolation (pp. 161–162); Papadatos fractional order statistics; Hutson's approximately distribution-free quantile intervals (p. 162); symmetric-case intervals from averages (Walsh averages) linked to the signed-rank test (p. 162); Guilbaud's bound for quasi-midranges (p. 162).
- Quantile differences: distribution-free lower/upper confidence bounds for ξq − ξp (Chu 1957), Eqs. 7.1.9–7.1.13 with an elementary proof (p. 163); choice of integers achieving level ≥ 1 − α (p. 163); outer/inner intervals for quantile intervals [ξp, ξq] (Wilks 1962) (p. 164); Breth's simultaneous intervals; Hettmansperger's two-sample shift intervals (p. 164).
- Tolerance intervals (Section 7.2, pp. 164–167): definition Pr{∫_{L1}^{L2} f(x)dx ≥ γ} = β (Eq. 7.2.1, p. 165); the LHS is distribution-free if and ONLY if L1, L2 are order statistics (Wilks 1942; Robbins 1944) (p. 165); coverage W_rs with Pr{W_rs ≥ γ} = 1 − I_γ(s−r, n−s+r+1) (p. 165); Example 7.2: for γ = 0.95, β = 0.90 one needs n = 77 (p. 165); statistically equivalent blocks (Tukey 1947) (p. 167).
- Prediction intervals (Section 7.3, pp. 167–168): two-sample setting; probability that (X(r), X(s)) contains Y(t); exceedance probabilities η_i(r, m, n) in closed binomial-coefficient form (Eqs. 7.3.1a/7.3.1b, p. 167).
- Exercises 7.1.1–7.2.3 (pp. 169–170), including Ex. 7.1.7 (outlier-robust median coverage; Kelleher and Walsh 1972) and Ex. 7.1.8 (finite-population versions; Meyer 1987).

## Experimental scope
Not applicable (monograph chapter; analytical results with small numerical examples).

## Conservative findings (with locators)
1. The coverage probability of an order-statistic interval (X(r), X(s)) for any quantile ξp of a continuous distribution is an exact binomial-sum expression independent of F — the foundational distribution-free interval result (Eq. 7.1.4, p. 160).
2. For the median this yields exact, sign-test-equivalent confidence intervals and a simple normal-approximation counting rule for n > 10 (Eq. 7.1.8, pp. 160–161).
3. Distribution-free tolerance intervals exist iff their endpoints are order statistics (p. 165), with Beta-based coverage probabilities and explicit sample-size computations (p. 165).
4. Distribution-free prediction intervals for a future order statistic have closed-form exceedance probabilities (Eqs. 7.3.1a/b, p. 167).

## Limitations
- **Excerpt-only**: citation use is limited to Chapter 7, pp. 159–170. Nothing else in the book (moments of order statistics, extreme-value theory, estimation chapters, the distribution theory of Ch. 2 that eq. 7.1.4 cross-references as (2.1.5)/(2.1.3)) is locally verifiable.
- **Image-only**: no text quotes can be machine-verified; locators are page/equation numbers from visual reading. An OCR or text-native copy is recommended before heavy citation use (inventory note).
- The results assume i.i.d. sampling; continuous-F results are exact, discrete-F results are one-sided bounds (p. 160).

## Exact usable locators (claim → locator)
- Quantile definition ξp: Eqs. 7.1.1–7.1.2, p. 159 (PDF p. 1).
- Distribution-free coverage π(r,s,n,p) as binomial sum: Eq. 7.1.4, p. 160 (PDF p. 2).
- Discrete-case bounds: Eqs. 7.1.5–7.1.7, p. 160 (PDF p. 2).
- Median CI formula and sign-test connection: Eq. 7.1.8 and following text, p. 160 (PDF p. 2).
- n > 10 counting rule and Example 7.1.1 (n = 100 → (x(40), x(61))): p. 161 (PDF p. 3).
- Quantile-difference confidence bounds: Eqs. 7.1.9–7.1.13, p. 163 (PDF p. 5).
- Tolerance-interval definition and Wilks/Robbins iff-order-statistics result: Eq. 7.2.1 and text, p. 165 (PDF p. 7).
- Tolerance sample-size example (γ=.95, β=.90 → n=77): Example 7.2, p. 165 (PDF p. 7).
- Prediction-interval exceedance probabilities: Eqs. 7.3.1a/7.3.1b, p. 167 (PDF p. 9).

## Supported uses in the DT-GSK manuscript
- Supporting an order-statistics argument (per the inventory note, proof-sketch support for the manuscript's Theorem 1): specifically, that intervals/events defined by order statistics of i.i.d. continuous samples have exact, distribution-free binomial coverage probabilities (Eq. 7.1.4), and the derived median/tolerance/prediction interval machinery of Ch. 7.
- Citing the book as the standard reference for order-statistics theory ONLY insofar as the cited content lies within pp. 159–170.

## Unsupported / prohibited overextensions
- Do NOT cite this key for any order-statistics result outside Ch. 7 pp. 159–170 (e.g., moments/distributions of order statistics from Ch. 2–3, asymptotics, extreme-value results, record values) — those pages are not in the corpus.
- Do NOT quote verbatim text as if machine-verified; the scan has no usable text layer (visual locators only).
- Appendix B gates this key to "order-statistics argument only if actually used": if the manuscript's final proofs do not invoke an order-statistics argument, the key remains uncited; do not add a decorative citation.

## Role in DT-GSK framing (Appendix B.8)
`david_order_statistics` — order-statistics support (Appendix B.8: "order-statistics argument only if actually used"). Backs the distribution-free coverage identities used in the manuscript's theoretical argument (Theorem 1 proof sketch), nothing more.

## Verification quotation (identity)
Running text layer, PDF p. 1: "Order Statistics, Third Edition. By H. A. David and H. N. Nagaraja. Copyright 2003 John Wiley & Sons, Inc. ISBN: 0-471-38926-9". Visual: chapter heading "7 — Order Statistics in Nonparametric Inference", p. 159.
