# Evidence card — efron1993introduction

## Verified bibliographic identity
- Title: An Introduction to the Bootstrap
- Authors: Bradley Efron (Stanford); Robert J. Tibshirani (Toronto)
- Venue/year: Chapman & Hall, 1993 (Monographs on Statistics and Applied Probability 57). Local printing is the Chapman & Hall/CRC (Taylor & Francis, © 1994 imprint) reprint; ISBN 978-0-412-04231-7 on the copyright page.
- DOI (bib): 10.1201/9780429246593
- Local file: `reference_papers/efron1993introduction.pdf` — **PARTIAL EXCERPT, 60 PDF pages only**: series list, title/copyright pages, full table of contents (book pp. vii–xiii), Preface (pp. xiv–xvi), and body Chapters 1–5 complete (book pp. 1–43). Nothing beyond book p. 43 is present.
- Inventory status: identity `verified`, readable, admissible with the excerpt restriction. SHA-256 `d2519d082976641c28dd8141d0a27d8e7ed56109c6eb9882efdc271aa78f9d82`.
- Locator convention: book page numbers (printed in the excerpt). PDF↔book mapping: PDF p. 4 = title page; PDF p. 5 = copyright; PDF pp. 8–14 = Contents; PDF pp. 15–17 = Preface; PDF p. 18 = book p. 1; PDF p. 27 = book p. 10; PDF p. 34 = book p. 17; PDF p. 48 = book p. 31; PDF p. 56 = book p. 39; PDF p. 60 = book p. 43 (last page present).

## Research question and context
Textbook monograph: explains "when and why bootstrap methods work, and how they can be applied in a wide variety of real data-analytic situations" (book p. 2), starting from the accuracy of a sample mean and building to bootstrap standard errors, bias, confidence intervals, and beyond (overview, book pp. 6–8).

## Method (content actually present in the local excerpt)
- Ch. 1 (pp. 1–9): statistical inference framing (aspirin study example); overview of the book; notation.
- Ch. 2 (pp. 10–16): the bootstrap previewed on the mouse data. "The bootstrap is a computer-based method for assigning measures of accuracy to statistical estimates" (p. 10). A bootstrap sample x* = (x*1, ..., x*n) is obtained by randomly sampling n times WITH replacement from the original data (p. 12; "invented by Efron in 1979", p. 12). Algorithm: generate B independent bootstrap samples, evaluate the statistic on each, and take the standard deviation of the B replications as se_boot (Fig. 2.1 schematic, p. 13; formula (2.3), p. 13). As B → ∞ for the mean, (2.3) approaches the plug-in standard error (2.4) (p. 14; Table 2.2 numerical illustration, p. 14).
- B guidance (standard errors): "Typical values for B, the number of bootstrap samples, range from 50 to 200 for standard error estimation" (p. 13); "B in the range 50 to 200 usually makes se_boot a good standard error estimator, even for estimators like the median" (pp. 14–15, pointing to Chs. 6 and 19). "Bootstrap confidence intervals add another factor of 10 to the computational burden" (p. 15).
- Ch. 3 (pp. 17–30): random samples, probability background; empirical distribution motivation.
- Ch. 4 (pp. 31–37): the empirical distribution function and the PLUG-IN PRINCIPLE — estimate a parameter θ = t(F) by θ̂ = t(F̂) (Sections 4.2–4.3, pp. 31–37).
- Ch. 5 (pp. 39–43): standard errors and estimated standard errors; se of a mean; plug-in estimate.
- Table of contents (book pp. vii–xiii; PDF pp. 8–14) — documents the existence and page locations of the NOT-INCLUDED chapters, notably: Ch. 12 bootstrap-t intervals (p. 153); Ch. 13 percentile intervals (p. 168); **Ch. 14 "Better bootstrap confidence intervals", Section 14.3 "The BCa method", p. 184, and Section 14.4 "The ABC method", p. 188**; Ch. 22 "Further topics in bootstrap confidence intervals" incl. 22.4 "The BCa interval" (p. 325).

## Experimental scope
Not applicable (textbook). Worked data examples in the excerpt: aspirin study (pp. 2–5), mouse survival data (Tables 2.1–2.2, pp. 11–14), law school data (pp. 19 ff.), rainfall data (p. 33).

## Conservative findings (with locators)
1. Definition and mechanics of the nonparametric bootstrap estimate of standard error (sampling with replacement; B replications; sd of replications): pp. 12–13, Eq. (2.3), Fig. 2.1.
2. B ≈ 50–200 suffices for standard-error estimation; confidence intervals need roughly an order of magnitude more (pp. 13–15).
3. The bootstrap generalizes accuracy assessment to statistics with no closed-form standard-error formula (e.g., the median), at the price of computation (pp. 12–15).
4. The plug-in principle underlies the bootstrap: θ̂ = t(F̂) (Ch. 4, pp. 35–37).
5. The book contains a chapter presenting the BCa confidence-interval method (ToC: Section 14.3, p. 184; Ch. 22.4, p. 325) — but ONLY its existence and page location are verifiable from the local excerpt.

## Limitations
- **The local excerpt ends at book p. 43. Chapters 6–26 — including everything on bootstrap confidence intervals (bootstrap-t, percentile, and the BCa/ABC methods) — are NOT locally readable.** Only the table of contents attests to them.
- Consequently no technical property of BCa (bias-correction constant z0, acceleration a, second-order accuracy, transformation-respecting behavior, coverage) can be supported by a locator from this corpus.
- Front-matter chapters present only elementary background; no asymptotic theory is in the excerpt.
- Local printing is the 1994 Taylor & Francis reprint of the 1993 edition (copyright page, PDF p. 5); bib cites the 1993 Chapman & Hall edition with the CRC DOI — treated as a minor metadata note in the inventory, identity verified.

## Exact usable locators (claim → locator)
- "The bootstrap is a computer-based method for assigning measures of accuracy to statistical estimates": book p. 10 (Ch. 2 opening; PDF p. 27).
- Bootstrap sample = n draws with replacement; invented by Efron 1979: book p. 12 (PDF p. 29).
- se_boot algorithm and formula: book p. 13, Eq. (2.3), Fig. 2.1 (PDF p. 30).
- B = 50–200 for SE estimation: book p. 13 (PDF p. 30) and pp. 14–15 (PDF pp. 31–32).
- CIs add ~10× computation: book p. 15 (PDF p. 32).
- Limit of se_boot for the mean = plug-in SE: book p. 14, Eq. (2.4) (PDF p. 31).
- Plug-in principle: book pp. 35–37, Sections 4.3 (PDF pp. 52–54).
- Standard error definitions: book pp. 39–43, Ch. 5 (PDF pp. 56–60).
- Existence of the BCa chapter: Contents entries "14 Better bootstrap confidence intervals 178 ... 14.3 The BCa method 184" (PDF p. 11) and "22.4 The BCa interval 325" (PDF p. 13).

## Supported uses in the DT-GSK manuscript
- Citing the book for the general bootstrap methodology: resampling with replacement, bootstrap replications, bootstrap standard errors, plug-in principle, and B-size guidance for SE estimation.
- A bare attribution of the form "the BCa method of Efron and Tibshirani (1993, Ch. 14)" is supportable ONLY as an attribution of the method to this book (via the ToC locator); any sentence characterizing what BCa does or why must be reworded, dropped, or supported elsewhere.

## Unsupported / prohibited overextensions
- Do NOT support any technical claim about BCa intervals (definition, z0/acceleration, second-order accuracy, coverage superiority, recommended B for intervals beyond the "factor of 10" remark on p. 15) from this key — the pages are absent locally. If the manuscript's methods section explains BCa mechanics, that is an EVIDENCE GAP to be registered (narrow the sentence to the supported attribution, or supply the missing pages).
- Do NOT cite for permutation tests, jackknife, cross-validation, prediction error, or bootstrap hypothesis testing — those chapters are outside the excerpt.
- Do NOT quote page numbers above 43 as if verified; only ToC-level locators exist for them.

## Role in DT-GSK framing (Appendix B.8)
`efron1993introduction` — BCa bootstrap (Appendix B.8). Given the partial excerpt, the key can fully support general bootstrap-resampling methodology, and supports the BCa citation only as a book/chapter attribution; BCa-specific technical support is blocked pending a fuller copy (register in evidence_gap_register if the manuscript needs it).

## Verification quotation (identity)
"An Introduction to the Bootstrap — Bradley Efron, Department of Statistics, Stanford University; and Robert J. Tibshirani, ... University of Toronto — CHAPMAN & HALL/CRC" (title page, PDF p. 4); "ISBN-13: 978-0-412-04231-7" (copyright page, PDF p. 5); series list entry "57 An Introduction to the Bootstrap B. Efron and R. Tibshirani (1993)" (PDF p. 3).
