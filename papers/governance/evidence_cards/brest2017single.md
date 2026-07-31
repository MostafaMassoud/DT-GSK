# Evidence card: brest2017single

## 1. Verified bibliographic identity

- Brest, Janez; Maucec, Mirjam Sepesy; Boskovic, Borko. "Single Objective Real-Parameter
  Optimization: Algorithm jSO." Proc. 2017 IEEE Congress on Evolutionary Computation
  (CEC), 2017, pp. 1311–1318. DOI 10.1109/CEC.2017.7969456.
- identity_status: **verified** (reference_inventory.csv). Diacritics in "Maucec" /
  "Boskovic" split in text extraction — artifact only.
- Local file: `reference_papers/brest2017single.pdf`, 8 pp., sha256
  943d52360c969d5105277a3aa2f0c228024768df890af34054074c1709b7de89.
- Page convention: proceedings pages 1311–1318 = PDF pp. 1–8; both given below.

## 2. Research question and context

Presents jSO, an improved variant of iL-SHADE (itself an improved L-SHADE), whose main
change is a weighted mutation strategy, and evaluates it on the CEC 2017 benchmark. The
authors state iL-SHADE "was on the third/fourth place on CEC 2016 competition"
(Section I, p. 1311 / PDF p. 1) and that "L-SHADE has been the best ranked DE-based
algorithm on CEC 2014 Competition" (Section II.B, p. 1313 / PDF p. 3). They also note
CEC 2016 and CEC 2017 benchmark functions differ, so results across those years are not
directly comparable (Section I, pp. 1311–1312 / PDF pp. 1–2).

## 3. Method (Sections II–III, pp. 1312–1315 / PDF pp. 2–5)

- Framework: success-history parameter adaptation (SHADE) + linear population size
  reduction (L-SHADE) + iL-SHADE's memory-initialization/clamping refinements.
  Full pseudo-code: Algorithm 1, p. 1313 / PDF p. 3 (jSO-specific lines flagged).
- **New mutation, DE/current-to-pBest-w/1** (Eq. 3, p. 1315 / PDF p. 5):
  v = x_i + Fw (x_pBest - x_i) + F (x_r1 - x_r2), with the weighted factor
  Fw = 0.7 F for nfes < 0.2 max_nfes; 0.8 F for nfes < 0.4 max_nfes; 1.2 F otherwise
  (Eq. 4, p. 1315 / PDF p. 5) — smaller pBest influence early, larger late.
- jSO-specific settings vs L-SHADE / iL-SHADE (Section IV.B, p. 1317 / PDF p. 7):
  p linearly decreases from pmax = 0.25 to pmin = pmax/2 (Eq. 1); initial population
  N_init = 25 log(D) sqrt(D) (vs 18D in L-SHADE, 12D in iL-SHADE); historical memory
  size H = 5 (vs 6); M_F initialized to 0.3 (vs 0.5); M_CR initialized to 0.8;
  CR clamped >= 0.7 for g < 0.25 G_MAX and >= 0.6 for g < 0.5 G_MAX; F capped at 0.7
  before 0.6 G_MAX (Algorithm 1 lines 19–27, p. 1313 / PDF p. 3).
- Authors' candor: parameter values "are set based on some additional experiments, but
  without fine tuning" (p. 1315 / PDF p. 5); changes from iL-SHADE to jSO "are minors"
  (p. 1315 / PDF p. 5).

## 4. Experimental scope (Section IV, pp. 1315–1318 / PDF pp. 5–8)

- Suite: CEC 2017 special-session benchmark (their ref. [23] = Awad et al., NTU Tech.
  Rep., Nov. 2016); **D = 10, 30, 50, 100; 51 runs; max_nfes = D x 10,000**; functions
  used as black boxes; optima known in advance (Section IV.B, p. 1317 / PDF p. 7).
- Own error statistics: Tables I–IV (D = 10/30/50/100), best/worst/median/mean/std
  (pp. 1313–1315 / PDF pp. 3–5).
- jSO vs L-SHADE per dimension with **Wilcoxon rank-sum, alpha = 0.05**: Tables V–VIII
  (pp. 1315–1317 / PDF pp. 5–7).
- **CEC 2017 evaluation method documented**: score = score1 + score2, where score1 uses
  the sum of errors and score2 the sum of ranks, each weighted 0.1/0.2/0.3/0.4 over
  D = 10/30/50/100 (Eqs. 5–7, Section IV-A, p. 1316 / PDF p. 6) — "higher weights are
  given for higher dimensions".
- Run-time complexity: Table XI (p. 1318 / PDF p. 8).

## 5. Conservative findings

- Summary statistics (Table IX, p. 1317 / PDF p. 7), jSO +/~/- (better/no difference/
  worse): vs L-SHADE — D10: 8/17/5; D30: 11/15/4; D50: 15/9/6; D100: 19/4/7.
  vs iL-SHADE — D10: 7/19/4; D30: 7/13/10; D50: 13/7/10; D100: 13/8/9.
  jSO better on all dimensions with one exception: iL-SHADE beats jSO at D = 30
  (Section IV.B and Conclusions, pp. 1317–1318 / PDF pp. 7–8).
- Applying the CEC 2017 scoring to the three algorithms only: jSO 100.0,
  iL-SHADE 93.30, L-SHADE 63.64 (Table X, p. 1318 / PDF p. 8) — "the best final score
  **among these three algorithms**" (Abstract, p. 1311 / PDF p. 1).
- jSO's advantage grows with dimension; "Superior performance of jSO is seen especially
  on D = 100" (p. 1317 / PDF p. 7).

## 6. Limitations

- Compares only within its own lineage (jSO vs L-SHADE vs iL-SHADE); no external
  algorithms.
- Improvements over iL-SHADE are explicitly minor and not fine-tuned (p. 1315 / PDF p. 5).
- Score-of-100 is relative to the two in-house baselines, not a competition-wide result.
- Complexity numbers "should be considered with some care, since the measured values of
  run-time are very small" (p. 1318 / PDF p. 8).

## 7. Exact usable locators

| Claim the DT-GSK manuscript may need | Locator |
|---|---|
| jSO = improved iL-SHADE; main novelty is weighted current-to-pBest-w/1 mutation | Abstract, p. 1311 / PDF p. 1; Section III, p. 1315 / PDF p. 5 |
| Weighted mutation equation and Fw schedule (0.7/0.8/1.2 x F) | Eqs. 3–4, p. 1315 / PDF p. 5 |
| Linearly decreasing p for pBest selection (Eq. 1) | p. 1314 / PDF p. 4 |
| Full pseudo-code with jSO-changed lines marked | Algorithm 1, p. 1313 / PDF p. 3 |
| jSO parameter settings (pmax=0.25, Ninit=25 log(D) sqrt(D), H=5, MF=0.3, MCR=0.8) | Section IV.B, p. 1317 / PDF p. 7; Alg. 1 lines 3–4 |
| L-SHADE = SHADE + linear population size reduction; best-ranked DE-based at CEC2014 | Section II.B, p. 1313 / PDF p. 3 |
| iL-SHADE placed third/fourth at CEC 2016 (authors' claim) | Section I, p. 1311 / PDF p. 1 |
| CEC2016 vs CEC2017 benchmarks differ; cross-year comparison invalid | Section I, pp. 1311–1312 / PDF pp. 1–2 |
| CEC2017 protocol: D=10/30/50/100, 51 runs, 10,000 x D FEs, black-box | Section IV.B, p. 1317 / PDF p. 7 |
| CEC2017 official scoring formula (error+rank scores, 0.1/0.2/0.3/0.4 weights) | Section IV-A, Eqs. 5–7, p. 1316 / PDF p. 6 |
| jSO error statistics at each dimension | Tables I–IV, pp. 1313–1315 / PDF pp. 3–5 |
| Wilcoxon (alpha=0.05) jSO vs L-SHADE per dimension | Tables V–VIII, pp. 1315–1317 / PDF pp. 5–7 |
| Summary w/t/l vs L-SHADE and iL-SHADE | Table IX, p. 1317 / PDF p. 7 |
| Scores 100.0 / 93.30 / 63.64 (jSO / iL-SHADE / L-SHADE) | Table X, p. 1318 / PDF p. 8 |

## 8. Supported uses

- Competition-context sentence: jSO as a winner-class, L-SHADE-lineage DE presented at
  CEC 2017, with its weighted-mutation mechanism accurately described.
- Citing the CEC 2017 **evaluation/scoring method** (weighted error + rank scores) —
  this paper reproduces the formula explicitly.
- Secondary (context-only) description of the CEC2017 protocol used by entrants
  (51 runs, 10,000·D, D=10–100, black-box) — flagged as participant description, NOT as
  the suite definition (definition key awad2016problem is blocked; see stub card).
- Lineage and design-philosophy framing: staged parameter schedules (CR/F clamps, Fw
  schedule) as competition practice for balancing exploration/exploitation over time —
  relevant when contrasting with DT-GSK's phase-structured control.
- The methodological caution that different CEC suites are not cross-comparable
  (pp. 1311–1312) — useful when the manuscript separates CEC2013/2017/2011 result sets.

## 9. Unsupported / prohibited overextensions

- Do NOT cite this paper as proof that **jSO placed second (or any official rank) in the
  CEC 2017 competition** — no official ranking appears in the paper; Table X's 100.0
  score is only among jSO/iL-SHADE/L-SHADE.
- Do NOT use it as the CEC2017 suite-definition citation.
- Do NOT claim jSO dominance over algorithms outside its lineage (none compared), nor
  over GSK-family algorithms.
- Do NOT cite iL-SHADE's "third/fourth place at CEC 2016" as an organizer-certified
  ranking; it is the authors' own characterization.

## 10. Role in DT-GSK framing (master Appendix B.4)

`brest2017single` — **competition context only where the source supports the stated
claim**: winner-lineage DE context for CEC2017, the official scoring formula, and
staged-parameter-control practice. Every use must match a locator above; no
suite-definition or official-ranking roles.
