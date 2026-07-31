# Evidence card: chen2020cbo

## 1. Verified bibliographic identity

- Chen, Debao; Lu, Renquan; Li, Suwen; Zou, Feng; Liu, Yajun. "An enhanced colliding
  bodies optimization and its application." Artificial Intelligence Review, vol. 53,
  no. 2 (2020). DOI 10.1007/s10462-019-09691-x (on-page DOI; (c) Springer Nature 2019
  online-first; bib cites the 2020 issue — consistent).
- identity_status: **verified** (reference_inventory.csv).
- Local file: `reference_papers/chen2020cbo.pdf`, 60 pp. (online-first layout, no issue
  pagination), sha256 2a5304a90dfa1bbb1923437af386b9075f241a91fc498cf861cdf732bc4c0ccb.
- Page convention: **PDF page numbers** (printed journal pages absent).
- **Naming caution:** the algorithm proposed here is **LSCBO** (learning-strategy-based
  colliding bodies optimization). It is NOT Kaveh & Ilchi Ghazaan's "ECBO"; ECBO appears
  in this paper only as one of the compared algorithms (Table 2, PDF p. 14). Never
  conflate the two under this key.

## 2. Research question and context

Colliding Bodies Optimization (CBO) is parameter-free in its body-updating equations and
structurally simple, but "suffers from low convergence speed and premature convergence"
(Abstract, PDF p. 1). Can hybridizing CBO's collision operator with the
teaching/learning operator of TLBO, best-individual guidance, a history-based random
mutation, and a safer mass computation produce a CBO variant competitive with well-known
metaheuristics?

## 3. Method (Sections 2–3, PDF pp. 3–10)

- Background: TLBO (teacher + learner phases) Section 2.1, PDF pp. 3–4; original CBO
  (mass by inverse fitness, colliding pairs, coefficient of restitution
  epsilon = 1 - iter/itermax, Eqs. 5–10) Sections 2.2 and 3.4–3.5, PDF pp. 4–8.
- LSCBO components (Section 3, PDF pp. 5–10):
  - new mass computation to avoid computation overflow (Section 3.3, PDF p. 6);
  - hybrid position generation: one candidate from the CBO collision operation
    (Eqs. 21–22) and one from the TLBO teaching operation toward the teacher with
    teaching factor TF = round(1 + rand) (Eqs. 23–25); the two are recombined by a
    random convex mix x_new = r8 x_new1 + (1 - r8) x_new2 (Eq. 26) (Section 3.6,
    PDF p. 8);
  - mutation using a permuted historical population (Oldpop) with mutation ratio Pc,
    combining backtracking-search-style history and DE-style difference of individuals
    (Eqs. 27–29, Section 3.7, PDF pp. 8–9);
  - greedy acceptance of better positions; pseudo-code on PDF p. 10.

## 4. Experimental scope (Section 4, PDF pp. 10–58)

- **22 classical benchmark functions** (Table 1, PDF pp. 12–13): F1–F9 unimodal,
  F10–F14 multimodal, F15–F22 rotated; D = 30, 50, 100 (Section 4.1.1, PDF p. 11).
- Settings (Section 4.1.2, PDF p. 11): population 50 (trial-and-error); **maxFEs =
  5000 x D for all algorithms**; **30 independent runs**; MATLAB 2012 / Windows 7;
  LSCBO's own parameters set by trial and error (velocity scale c = 0.1 simple /
  0.3 complex problems; alpha = 0.1; Pc = 0.1 simple / 0.4 complex).
- **15 algorithms compared** (14 baselines + LSCBO; Table 2, PDF p. 14): jDE, SaDE,
  JADE, PSOFIPS, PSOFDR, CLPSO, TLBO, ETLBO, BSA, LBSA, DGSTLBO, CBO, ECBO, CBOPSO.
- Statistics: means/std over 30 runs (Tables 3, 6, 7); mean FEs to acceptable solution
  (mFEs, Table 4); **t-tests** with B/S/W (better/same/worse) aggregation (Table 5,
  PDF pp. 26–29).
- **CEC2005 subset**: 25 functions F23–F47 at D = 30 (Table 8, PDF p. 42), fitness =
  |f - f*|; rank-based aggregation (Table 9, PDF pp. 43–50).
- **3 engineering design problems** with penalty-based constraint handling (Eqs. 30–31,
  PDF p. 50): welded beam (Section 4.5, PDF p. 51), pressure vessel (Section 4.5.1,
  PDF p. 52), tubular column (Section 4.5.2, PDF p. 54).

## 5. Conservative findings

- On the 22 classical functions, LSCBO's means/stds are best or tied for most unimodal
  and several rotated functions at D = 30/50/100; average excellent-and-good rate vs the
  other 14 algorithms is 86.04% by t-test at 30D (Section 4.1.3 and p. 29's rate
  computation; Section 4.6, PDF p. 58: 68.2% at 30D and 86.4% at 50D/100D by
  means-of-solutions criterion).
- On CEC2005 (D = 30): **LSCBO's average rank is 4.60, worse than jDE and JADE but
  better than the other 12 algorithms** (Section 4.3 discussion, PDF p. 50; Section 4.6,
  PDF p. 58).
- On the three engineering problems, LSCBO "is not always the best for all performance
  metrics" but finds satisfactory solutions (Section 4.6, PDF p. 58).
- Overall: the designed operators clearly improve original CBO (Tables 3–7; Section 5,
  PDF p. 58).

## 6. Limitations (author-acknowledged, Section 4.6, PDF p. 58)

- The random convex-mix proportion (Eq. 26) cannot adapt to what benefits the current
  iteration.
- Parameters are trial-and-error, not adaptive; LSCBO adds parameters relative to the
  parameter-free CBO.
- LSCBO is not uniformly best (explicitly framed via the "No free lunch" theorem,
  Wolpert & Macready reference, PDF p. 58).
- Protocol differs from CEC conventions: 30 runs and 5000·D FEs (not 51 runs /
  10,000·D); t-tests rather than nonparametric tests on the classical set.

## 7. Exact usable locators

| Claim the DT-GSK manuscript may need | Locator (PDF page) |
|---|---|
| CBO is a recent metaheuristic with no algorithm-specific parameters in its updating equations | Abstract, p. 1 |
| CBO suffers from low convergence speed and premature convergence | Abstract, p. 1 |
| LSCBO = CBO collision + TLBO learning + best-individual guidance + history-based mutation | Abstract, p. 1; Section 3, pp. 5–10 |
| Original CBO update equations and restitution coefficient | Section 2.2 / Eqs. 5–10, pp. 4–5 |
| Hybrid position generation (Eqs. 21–26) | Section 3.6, p. 8 |
| History-based mutation (Eqs. 27–29) | Section 3.7, pp. 8–9 |
| Scope: 47 benchmark functions + 3 structural design problems | Abstract, p. 1 |
| 22 classical functions, categories, D = 30/50/100 | Section 4.1.1 + Table 1, pp. 11–13 |
| Protocol: pop 50, maxFEs 5000 x D, 30 runs | Section 4.1.2, p. 11 |
| 14 comparison algorithms and their parameters | Table 2, p. 14 |
| t-test aggregation, 86.04% excellent-and-good rate at 30D | Table 5 + text, pp. 26–29 |
| 50D/100D results; mFEs advantage | Section 4.2 + Tables 6–7, pp. 29–42 |
| CEC2005 subset F23–F47 definitions | Table 8, p. 42 |
| CEC2005 ranking: LSCBO avg rank 4.60; behind jDE and JADE, ahead of other 12 | pp. 50, 58 |
| Penalty-function constraint handling for engineering problems | Eqs. 30–31, p. 50 |
| Author-stated limitations; NFL framing | Section 4.6, p. 58 |
| Conclusions | Section 5, pp. 58–59 |

## 8. Supported uses

- Taxonomy/positioning: an example of the physics-inspired CBO line and of
  learning-strategy hybridization (TLBO operator injection) in recent metaheuristics.
- Related-work sentences on hybrid strategies: best-guided updates, historical-population
  mutation, and random recombination of operator outputs, with the verified mechanism
  described above.
- Evidence that adaptive-DE baselines (jDE, JADE) still outrank a tuned CBO hybrid on
  CEC2005 composition-heavy problems (PDF pp. 50, 58) — useful for motivating
  knowledge-based/adaptive designs.
- Honest-limitation framing (trial-and-error parameters, added parameters, NFL).

## 9. Unsupported / prohibited overextensions

- Do NOT cite as Kaveh's ECBO or as the original CBO paper (original CBO = Kaveh &
  Mahdavi 2014, cited within but not in our corpus under this key).
- Do NOT use its results as CEC2013/CEC2017-comparable evidence: protocol is 30 runs,
  5000·D FEs, t-tests, and a CEC2005 subset only.
- Do NOT claim LSCBO is state-of-the-art overall — the paper itself shows jDE and JADE
  rank higher on CEC2005 (PDF p. 50).
- Do NOT extract GSK-relevant performance comparisons: no GSK-family algorithm appears.
- Per master Appendix B.2/B.5 discipline: do not insert a one-sentence citation merely
  to consume the key.

## 10. Role in DT-GSK framing (master Appendix B.5)

`chen2020cbo` — **taxonomy/positioning only**: one of the "other metaheuristics"
exemplars for breadth in related work (physics-inspired + learning-hybrid line). Cite
only where its verified mechanism or its documented CEC2005/classical-function results
are actually discussed; never as a performance benchmark for DT-GSK claims.
