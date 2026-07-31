# Evidence card: awad2017ensemble

## 1. Verified bibliographic identity

- Awad, Noor H.; Ali, Mostafa Z.; Suganthan, Ponnuthurai N. "Ensemble Sinusoidal
  Differential Covariance Matrix Adaptation with **Euclidean Neighborhood** for Solving
  CEC2017 Benchmark Problems." Proc. 2017 IEEE Congress on Evolutionary Computation
  (CEC), 2017, pp. 372–379. DOI 10.1109/CEC.2017.7969336.
- identity_status: **minor_metadata_mismatch** (reference_inventory.csv): the bib title
  says "...with L-SHADE..."; the source title says "...with Euclidean Neighborhood...".
  Identity certain (same authors, venue, DOI, subject). **Resolution: adopt the source
  title** in any rendered bibliography.
- Algorithm name: **LSHADE-cnEpSin**.
- Local file: `reference_papers/awad2017ensemble.pdf`, 8 pp., sha256
  9fb369d7a34a8a9fd84b4f680c96e0feac517d25e94be61d67017116e6be64ee.
- Page convention: proceedings pages 372–379 = PDF pp. 1–8; both given below.

## 2. Research question and context

Can LSHADE-EpSin — described by the authors as "ranked as the joint winner in the
real-parameter single objective optimization competition, CEC 2016" (Abstract, p. 372 /
PDF p. 1; joint with UMOEAsII, p. 373 / PDF p. 2) — be improved by (i) performance-based
selection between its two sinusoidal scaling-factor adaptation schemes and (ii) a
covariance-matrix-learning crossover restricted to a Euclidean neighborhood of the best
individual, and how does the result perform on the CEC2017 bound-constrained suite?

## 3. Method (Section II, pp. 372–375 / PDF pp. 1–4)

Base framework inherited from L-SHADE lineage:
- JADE current-to-pbest/1 mutation with external archive (Eq. 2, p. 373 / PDF p. 2);
  success-history memories for F and CR (Eqs. 9–15, p. 374 / PDF p. 3);
  linear population size reduction (Eq. 3), NPmin = 4.

Contribution 1 — ensemble sinusoidal adaptation with performance adaptation
(Section II.A, pp. 373–374 / PDF pp. 2–3):
- First half of generations: choose between (a) non-adaptive sinusoidal decreasing
  adjustment (Eq. 4) and (b) adaptive sinusoidal increasing adjustment with
  Cauchy-perturbed frequency memory (Eqs. 5–6). Selection is by success-rate
  probabilities over a learning period LP (Eqs. 7–8; epsilon = 0.01), instead of the
  random choice used in LSHADE-EpSin.
- Second half: F from Cauchy around memory means (Eq. 9); CR always Normal around
  memory means (Eq. 10); weighted Lehmer mean updates (Eqs. 11–15).

Contribution 2 — covariance matrix learning with Euclidean neighborhood
(Section II.B, pp. 374–375 / PDF pp. 3–4):
- With probability pc, sort population by distance to the best individual, take the
  nearest NP x ps individuals, eigendecompose their covariance C = B D B^T (Eq. 16),
  apply binomial crossover in the eigen coordinate system, transform back
  (Eqs. 17–20).

Pseudo-code: Fig. 1, p. 375 / PDF p. 4. Parameters (Section III.B, pp. 375–376 /
PDF pp. 4–5): initial muF = muCR = 0.5; H = 5; freq = 0.5 (non-adaptive scheme);
ps = 0.5; pc = 0.4; NPmax = 18 x D; NPmin = 4.

## 4. Experimental scope (Section III, pp. 375–377 / PDF pp. 4–6)

- Suite: "CEC2017 competition on single objective bound constrained real-parameter
  optimization ... 30 test functions": F1–F3 unimodal, F4–F10 multimodal, F11–F20
  hybrid, F21–F30 composition (Section III.A, p. 375 / PDF p. 4; citing its ref. [18],
  the Awad et al. 2016 NTU/JUST/ZZU technical report).
- Dimensions D = 10, 30, 50, 100; **51 runs**; budget **10,000 x D** FEs; error treated
  as 0 below 1e-8 (Section III.D, p. 376 / PDF p. 5).
- Own results: Tables II–V (D = 10/30/50/100), best/worst/median/mean/std of error
  values (pp. 376–377 / PDF pp. 5–6).
- Complexity: Table I (Matlab 2015b, T0/T1/T2-hat per the suite's protocol; f18 used),
  p. 376 / PDF p. 5.
- Comparison at 50D vs SaDE, JADE, SHADE, L-SHADE, UMOEAsII, MVMO with original
  parameter settings, 51 runs, 10,000·D FEs; Wilcoxon rank-sum at alpha = 0.05
  (Section III.E and Table VI, pp. 377–378 / PDF pp. 6–7).

## 5. Conservative findings

- On 50D CEC2017, per the w/t/l row of Table VI (p. 378 / PDF p. 7): SaDE 0/0/30,
  JADE 0/3/27, SHADE 0/2/28, L-SHADE 7/9/14, UMOEAsII 8/4/18, MVMO 3/1/26 — each entry
  counts the contestant's wins/ties/losses against LSHADE-cnEpSin (text, p. 377 /
  PDF p. 6: "LSHADE performs better than LSHADE-cnEpSin in 7 functions ... inferior
  performance in 14 functions"; UMOEAsII 8/4/18 likewise).
- Authors' conclusion: best overall performance among the compared variants; improves on
  L-SHADE (CEC2014 winner, their citation) and UMOEAsII (CEC2016 joint winner)
  (Section III.E, p. 377 / PDF p. 6).
- Unimodal F1–F3 solved to optimum at all tested D except F2 at 50D/100D; composition
  functions remain hardest (Section III.D, pp. 376–377 / PDF pp. 5–6).

## 6. Limitations

- Cross-algorithm comparison reported only at D = 50 ("For space limitation", p. 377 /
  PDF p. 6); no head-to-head statistics at 10/30/100D.
- Sensitivity analysis for ps and pc omitted for space (Section III.B, p. 376 / PDF p. 5).
- Comparators are all DE-family or DE-adjacent; no non-DE metaheuristics.
- The internal w/t/l sign convention is described ambiguously in the text (the "+"
  definition sentence conflicts with the worked examples); rely on the worked-example
  sentences and the Table VI row quoted above.

## 7. Exact usable locators

| Claim the DT-GSK manuscript may need | Locator |
|---|---|
| LSHADE-cnEpSin = LSHADE-EpSin + performance-adaptive sinusoidal ensemble + covariance-matrix crossover with Euclidean neighborhood | Abstract, p. 372 / PDF p. 1 |
| LSHADE-EpSin was joint winner of CEC 2016 competition (with UMOEAsII) | Abstract p. 372; Section I, p. 373 / PDF pp. 1–2 |
| L-SHADE won CEC2014; SHADE ranked 3rd at CEC2013 (authors' historical framing) | Section I, p. 372 / PDF p. 1 |
| current-to-pbest mutation + archive; LPSR; memory-based F/CR | Section II, Eqs. 2–3, 9–15, pp. 373–374 / PDF pp. 2–3 |
| Ensemble sinusoidal F-adaptation, success-probability selection | Section II.A, Eqs. 4–8, pp. 373–374 / PDF pp. 2–3 |
| Eigen/covariance crossover in best-neighborhood (ps, pc) | Section II.B, Eqs. 16–20, pp. 374–375 / PDF pp. 3–4 |
| Parameter values (H=5, ps=0.5, pc=0.4, NPmax=18D, NPmin=4) | Section III.B, pp. 375–376 / PDF pp. 4–5 |
| CEC2017 suite structure: 30 functions; F1–F3 unimodal, F4–F10 multimodal, F11–F20 hybrid, F21–F30 composition | Section III.A, p. 375 / PDF p. 4 |
| Protocol: 51 runs, 10,000 x D FEs, error<1e-8 => 0, D=10/30/50/100 | Section III.D, p. 376 / PDF p. 5 |
| Own error statistics per dimension | Tables II–V, pp. 376–377 / PDF pp. 5–6 |
| 50D comparison + Wilcoxon w/t/l vs 6 algorithms | Table VI + Section III.E, pp. 377–378 / PDF pp. 6–7 |

## 8. Supported uses

- Competition-context sentence: LSHADE-cnEpSin as a winner-class L-SHADE-lineage
  algorithm presented at the CEC2017 session, with its mechanism accurately described.
- Secondary (context-only) description of the CEC2017 protocol actually used by
  competition entrants (30 functions, categories, 51 runs, 10,000·D) — flagged as the
  participant's description, NOT as the suite definition (that key, awad2016problem, is
  blocked; see its stub card).
- Lineage claims: JADE -> SHADE -> L-SHADE -> LSHADE-EpSin -> LSHADE-cnEpSin, and the
  CEC2016 joint-winner status of LSHADE-EpSin/UMOEAsII, as claimed by these authors.
- Positioning covariance/eigen-coordinate crossover as an established
  structure-exploiting operator in competition DE (with guo2015eig, hansen2001cmaes per
  Appendix B.3).

## 9. Unsupported / prohibited overextensions

- Do NOT cite this paper as proof that **LSHADE-cnEpSin won or placed N-th in the CEC
  2017 competition** — the paper contains no official CEC2017 ranking (rankings were
  announced by organizers outside this corpus). "Winner" language in this corpus is
  supported only for LSHADE-EpSin at CEC2016 (authors' own claim) and L-SHADE at CEC2014
  (authors' historical framing).
- Do NOT use it as the CEC2017 suite-definition citation (blocked key awad2016problem is
  the definition anchor; currently unavailable).
- Do NOT generalize the 50D-only comparison to all dimensions.
- Do NOT claim superiority over non-DE families or over GSK-family algorithms; no such
  comparison exists here.

## 10. Role in DT-GSK framing (master Appendix B.4)

`awad2017ensemble` — **competition context only where the source supports the stated
claim**: use for winner-lineage framing of CEC2017-era DE, description of its mechanism,
and participant-side protocol description. Every use must match a locator above; no
suite-definition or official-ranking roles.
