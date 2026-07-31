# Evidence card — benjamini1995controlling

## Verified bibliographic identity
- Title: Controlling the False Discovery Rate: a Practical and Powerful Approach to Multiple Testing
- Authors: Yoav Benjamini; Yosef Hochberg (Tel Aviv University, Israel)
- Venue/year: Journal of the Royal Statistical Society, Series B (Methodological), Vol. 57, No. 1 (1995), pp. 289–300. [Received January 1993, revised March 1994.]
- DOI (bib): 10.1111/j.2517-6161.1995.tb02031.x
- Local file: `reference_papers/benjamini1995controlling.pdf` (12 pp.)
- Inventory status: identity `verified`, readable, admissible. SHA-256 `d155815b607568d852ca2aac08db35fd1d37d27436b40e7b10dec586480b31b1`.
- Locator convention: printed journal pages 289–300 map one-to-one to PDF pages 1–12. Locators give printed page (PDF page).

## Research question and context
Is familywise error rate (FWER) control the right criterion for all multiple-testing problems, and can a less stringent but still meaningful error rate — the expected proportion of falsely rejected hypotheses among the rejected, the false discovery rate (FDR) — be controlled by a simple Bonferroni-type procedure with a substantial gain in power? (Summary, p. 289 / PDF p. 1.)

Context: difficulties with classical FWER-controlling multiple-comparison procedures — low power and frequent inapplicability — are laid out in Section 1 (pp. 289–290 / PDF pp. 1–2); the FDR concept builds on Soriç's (1989) notion of a rejected hypothesis as a "statistical discovery" (p. 290 / PDF p. 2).

## Method
- Framework: of m tested null hypotheses, m0 are true; R = number rejected; V = number of true nulls rejected; Q = V/(V+S) with Q = 0 when no rejections; FDR Qe = E(Q) = E(V/R) (Section 2.1, p. 291 / PDF p. 3).
- Two elementary properties (p. 291 / PDF p. 3):
  (a) if all nulls are true (m0 = m), FDR = FWER, so FDR control implies weak FWER control;
  (b) if m0 < m, FDR ≤ FWER; hence FDR-controlling procedures are potentially more powerful than FWER-controlling ones, and the potential gain grows with the number of false nulls.
- The BH procedure (Section 3.1, p. 293 / PDF p. 5): with ordered p-values p(1) ≤ ... ≤ p(m) and desired level q*: "let k be the largest i for which P(i) ≤ (i/m) q*; then reject all H(i), i = 1, 2, ..., k" (procedure (1)).
- Theorem 1 (p. 293 / PDF p. 5): for independent test statistics and any configuration of false null hypotheses, the procedure controls the FDR at q* (the proof's lemma gives the sharper bound E(Q) ≤ (m0/m) q* ≤ q*). Remark (p. 293): independence is only needed for the statistics corresponding to the TRUE null hypotheses; independence among the false-null statistics is not required.
- Alternative characterization: Theorem 2 (p. 295 / PDF p. 7) — the procedure solves the post hoc maximization "choose α maximizing the number of rejections r(α) subject to αm/r(α) ≤ q*".
- Lineage: the procedure was mentioned by Simes (1986) as an exploratory extension of his intersection test; Hommel (1988) showed it does not control FWER in the strong sense; Hochberg (1988) built a different, FWER-controlling use of Simes's inequality (p. 293 / PDF p. 5). Constant-by-constant comparison with Hochberg's procedure and the conclusion that BH rejects at least as many hypotheses, "and therefore has also greater power than other FWER controlling methods such as Holm's (1979)" (p. 294 / PDF p. 6).

## Experimental scope
- Worked example (Section 3.2, pp. 294–295 / PDF pp. 6–7): 15 p-values from a multicentre myocardial-infarction trial (Neuhaus et al. 1992); at 0.05, Bonferroni and Hochberg reject 3 hypotheses (not including mortality, p = 0.0095); the FDR procedure with q* = 0.05 rejects 4, including mortality (p(4) = 0.0095 ≤ (4/15)·0.05 = 0.013).
- Simulation study (Section 4, pp. 296–298 / PDF pp. 8–10): m independent normal test statistics, z-tests, q* = α = 0.05; m ∈ {4, 8, 16, 32, 64}; m0/m ∈ {3/4, 1/2, 1/4, 0}; non-zero means placed in 4 clusters at L/4..L with L ∈ {5, 10}; three configurations (D/E/I); 20,000 repetitions; SE of power estimates ≈ 0.0008–0.0016.

## Conservative findings (with locators)
1. FDR is a distinct, well-defined error rate; controlling it implies weak (but not strong) FWER control (property (a), p. 291 / PDF p. 3).
2. The linear step procedure (1) controls FDR at q* for independent test statistics, for any configuration of false nulls (Theorem 1, p. 293 / PDF p. 5).
3. Power of the FDR procedure is uniformly larger than Bonferroni's and Hochberg's in the simulation; the advantage increases with the number of non-null hypotheses and with m (observations (c)–(e), p. 297 / PDF p. 9).
4. Example magnitudes: testing 32 hypotheses, all false, equally spread — Bonferroni power 0.42 vs 0.65 for the FDR procedure; 4 hypotheses, half true — 0.62 vs 0.70 (observation (f), p. 298 / PDF p. 10).
5. The gain from FDR control over FWER control is much larger than the gain of Hochberg's method over Bonferroni (observation (g), p. 298 / PDF p. 10).
6. FDR control is argued to be the appropriate criterion when the overall conclusion tolerates a small proportion of erroneous rejections (multiple endpoints, subgroups, screening; Section 2.2, p. 292 / PDF p. 4).

## Limitations
- Theorem 1 is proved for INDEPENDENT test statistics (of the true nulls). The positive-dependence (PRDS) extension is Benjamini–Yekutieli 2001, NOT in this paper — do not cite this key for dependent-case validity.
- FDR control is weaker than strong FWER control; individual rejections carry less protection (Section 5 discussion, p. 298 / PDF p. 10).
- Simulations cover independent normal means only, m ≤ 64.
- Terminology caution: the paper describes both Hochberg's procedure and its own as "step-down" (p. 294 / PDF p. 6); modern literature calls the BH procedure "step-up". Quote carefully.

## Exact usable locators (claim → locator)
- FDR definition Qe = E(V/R): Section 2.1, p. 291 (PDF p. 3).
- FDR = FWER when all nulls true (weak control); FDR ≤ FWER otherwise: p. 291 (PDF p. 3).
- Procedure (1) definition (largest i with p(i) ≤ (i/m)q*): Section 3.1, p. 293 (PDF p. 5).
- Theorem 1 (independent statistics; FDR ≤ (m0/m)q*): p. 293 (PDF p. 5); Lemma and inequality (2), p. 293; full proof Appendix A, pp. 299–300 (PDF pp. 11–12).
- Independence of false-null statistics not needed (Remark): p. 293 (PDF p. 5).
- Relation to Simes/Hommel/Hochberg: p. 293 (PDF p. 5).
- Greater power than Holm's and other FWER methods (analytical constants argument): p. 294 (PDF p. 6).
- Worked 15-endpoint example: Section 3.2, pp. 294–295 (PDF pp. 6–7).
- Post hoc maximization view: Theorem 2, p. 295 (PDF p. 7).
- Simulation design: Section 4.1, p. 296 (PDF p. 8); power results and observations (a)–(g): pp. 296–298 (PDF pp. 8–10), Fig. 1, p. 297 (PDF p. 9).

## Supported uses in the DT-GSK manuscript
- Citing the Benjamini–Hochberg procedure when the manuscript reports FDR-adjusted results for exploratory, many-comparison analyses (Appendix B.8 gates this to "exploratory FDR only when used").
- Supporting statements that (a) FDR is the expected proportion of false rejections among rejections, (b) BH controls FDR at q* for independent statistics, and (c) FDR control trades strong FWER protection for power in large exploratory families.

## Unsupported / prohibited overextensions
- Do NOT cite for FDR control under dependence (PRDS) — that is Benjamini & Yekutieli (2001), outside this corpus.
- Do NOT present BH-adjusted results as FWER-controlled conclusions; the paper itself distinguishes these (p. 291, p. 298).
- Do NOT use this key for adaptive FDR (m0 estimation), q-values, or resampling-based FDR — later literature.
- Do NOT cite it as recommending FDR for confirmatory headline comparisons; its motivation is problems that tolerate a proportion of errors (Section 2.2).

## Role in DT-GSK framing (Appendix B.8)
`benjamini1995controlling` — exploratory FDR control, cited only if the manuscript actually reports BH/FDR-adjusted analyses; otherwise the key remains unused (Appendix B: "exploratory FDR only when used").

## Verification quotation (identity)
"J. R. Statist. Soc. B (1995) 57, No. 1, pp. 289-300 — Controlling the False Discovery Rate: a Practical and Powerful Approach to Multiple Testing — By YOAV BENJAMINI and YOSEF HOCHBERG, Tel Aviv University, Israel" (p. 289 / PDF p. 1).
