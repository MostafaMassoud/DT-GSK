# Evidence card: li2013lsgo

## 1. Verified bibliographic identity

- Li, Xiaodong; Tang, Ke; Omidvar, Mohammad N.; Yang, Zhenyu; Qin, Kai. "Benchmark
  Functions for the CEC'2013 Special Session and Competition on Large-Scale Global
  Optimization." Technical report, dated **December 24, 2013** (title page, p. 1).
- Affiliations printed on the title page: (1) Evolutionary Computing and Machine Learning
  (ECML), School of Computer Science and Information Technology, **RMIT University**,
  Melbourne, Australia (Li, Omidvar, Qin); (2) Nature Inspired Computation and Applications
  Laboratory (NICAL), School of Computer Science and Technology, **University of Science and
  Technology of China**, Hefei (Tang); (3) College of Information System and Management,
  **National University of Defense Technology**, Changsha (Yang). The bib `institution`
  field carries RMIT University; the other two affiliations are recorded here.
- **No DOI is printed anywhere in the document** and none was supplied; the bib entry
  therefore carries no `doi` field. The report is distributed from the RMIT competition
  page cited in footnote 1 (p. 2).
- Local file: `reference_papers/li2013lsgo.pdf`, 23 pp., sha256
  0f377901bc7e16e0a702a45a26315daf03ad89344b7b89b28121efc3bb07b169.
- Page convention in this card: PDF page = printed report page (they coincide; the printed
  folio on the last page is 23).
- **Identity warning.** This is NOT `liang2013cec2013`. That key is the *bound-constrained*
  CEC 2013 real-parameter suite (28 functions, D = 10/30/50, 51 runs, 10,000*D FEs). This
  key is the *large-scale* CEC'2013 suite (15 functions, D = 1000/905, 25 runs, 3e6 FEs).
  The two share a year and a competition series and nothing else.

## 2. Research question and context

The report proposes **15 large-scale benchmark problems as an extension to the existing
CEC'2010 large-scale global optimization benchmark suite** (Abstract, p. 1). Its stated aim
is "to better represent a wider range of real-world large-scale optimization problems and
provide convenience and flexibility for comparing various evolutionary algorithms
specifically designed for large-scale global optimization" (Abstract, p. 1). Section 1
(pp. 1-2) motivates the suite from three difficulty sources -- exponential growth of the
search space, change of landscape properties with dimension, and expensive evaluation --
plus variable interaction (non-separability), and argues that most real-world problems sit
between full separability and full non-separability, which is what makes decomposition and
cooperative co-evolution attractive (pp. 1-2).

## 3. Method -- what is new relative to CEC'2010 (Section 2, pp. 2-3)

Four families of changes are introduced over the CEC'2010 suite (Section 2, p. 2):

- **Nonuniform subcomponent sizes** (Sec. 2.1, p. 2): CEC'2010 used equal-sized
  non-separable subcomponents; this suite uses a range of different sizes.
- **Imbalance in the contribution of subcomponents** (Sec. 2.2, p. 3): each non-separable
  subcomponent is multiplied by a random weight `w_i = 10^(3*N(0,1))` (Sec. 4.2.1, p. 7).
- **Overlapping subcomponents** (Sec. 2.3, p. 3), in two kinds -- *conforming* (shared
  variables have the same optimum in both subcomponents) and *conflicting* (shared variables
  have different optima) (Section 4, p. 4).
- **New transformations of the base functions** (Sec. 2.4, pp. 3): ill-conditioning
  (`Lambda^alpha`, Sec. 4.2.1 p. 7), irregularities (`T_osz`, p. 7) and symmetry breaking
  (`T_asy^beta`, p. 7). The report states these "do not change the separability and modality
  properties of the functions" (p. 3).

Section 3 (p. 4) gives three formal definitions: partial separability with m independent
subcomponents (Def. 1), full non-separability (Def. 2), and partial additive separability
(Def. 3). Section 4 (pp. 4-5) organises the suite into four categories and names the 15
functions:

| Category | Functions |
|---|---|
| Fully separable | f1 Elliptic, f2 Rastrigin, f3 Ackley |
| Partially additively separable, **with** a separable subcomponent | f4 Elliptic, f5 Rastrigin, f6 Ackley, f7 Schwefel 1.2 |
| Partially additively separable, **no** separable subcomponent | f8 Elliptic, f9 Rastrigin, f10 Ackley, f11 Schwefel 1.2 |
| Overlapping | f12 Rosenbrock, f13 Schwefel *conforming*, f14 Schwefel *conflicting* |
| Fully non-separable | f15 Schwefel 1.2 |

The six base functions are Sphere, Elliptic, Rastrigin, Ackley, Schwefel's Problem 1.2 and
Rosenbrock (Sec. 4.1, p. 6).

Per-function structural facts taken from Section 4.3 (pp. 9-18):

- f1/f2/f3 bounds `[-100,100]^D`, `[-5,5]^D`, `[-32,32]^D` respectively (pp. 9-10).
- f4-f7 use `S = {50, 25, 25, 100, 50, 25, 25, 700}`, so `D = 1000` (pp. 11-13).
- f8-f11 use the 20-element multiset
  `S = {50,50,25,25,100,100,25,25,50,25,100,25,100,50,25,25,25,100,50,25}`, so `D = 1000`
  (pp. 14-16).
- f12 `D = 1000`, `[-100,100]^D`, global optimum at `f12(x_opt + 1) = 0` (p. 17).
- **f13 and f14 have `D = 905`**, not 1000: overlap size `m = 5` removes `m*(|S|-1) = 95`
  variables from the 1000-variable multiset (pp. 17-18).
- f15 `D = 1000`, `[-100,100]^D` (p. 18).
- Every base function in f2/f3, f5/f6, f9/f10 (the Rastrigin and Ackley members) is applied
  to `z = Lambda^10 * T_asy^0.2(T_osz(...))`, i.e. **the ill-conditioned, symmetry-broken,
  irregularised transform of the shifted (and, where applicable, rotated) argument**
  (pp. 9-10, 11-12, 14-15). The report defines no untransformed variant of these functions.

## 4. Evaluation protocol (Section 5, p. 19)

Section 5.1 "General Settings" states verbatim:

1. Problems: **15 minimization problems**;
2. Dimensions: **D = 1000**;
3. Number of runs: **25 runs per function**;
4. Maximum number of fitness evaluations: **Max FE = 3 x 10^6**;
5. Termination criteria: when Max FE is reached;
6. Boundary handling: "All problems have the global optimum within the given bounds, so
   there is no need to perform search outside of the given bounds for these problems. The
   provided codes returns NaN if an objective function is evaluated outside the specified
   bounds."

Section 5.2 "Data To Be Recorded and Evaluation Criteria" (p. 19) requires solution quality
at three FE milestones -- **FEs1 = 1.2e+5, FEs2 = 6.0e+5, FEs3 = 3.0e+6** -- reporting the
**best, median, worst, mean and standard deviation of the 25 runs** in the layout of Table 2
(p. 20). It states: "Competition entries will be mainly ranked based on the **median**
results achieved when FEs = 1.2e+5, 6.0e+5 and 3.0e+6." Convergence curves are additionally
requested for **six** functions -- f2, f7, f11, f12, f13, f14 -- each averaged over the 25
runs (p. 19).

Table 1 (p. 19) reports the runtime of 10,000 FEs per function in GNU Octave 3.2.3 on an
Intel Core2 Duo E8500 (4.69 s for f1 up to 24.40 s for f15), and the report estimates the
full 3e6-FE experiment at "about 207 hours" with the MATLAB/Octave version, recommending
parallel runs (p. 19).

## 5. Conservative findings

This is a benchmark-definition technical report. It defines problems, transformations and
an evaluation protocol; **it reports no algorithm results, no rankings and no winner**.
Section 6 "Conclusion" (p. 20) restates the four new features and the design goal, and the
Acknowledgments thank W. Chen (C++ version) and G. Iacca (Java version), confirming that
MATLAB/Octave, Java and C++ implementations accompany the report (p. 2 footnote 1; p. 20).

## 6. Limitations

- **The "D = 1000" line in Section 5.1 is not literally true for the whole suite**: f13 and
  f14 are defined with `D = 905` in Section 4.3.4 (pp. 17-18). Any statement that the suite
  is "1000-dimensional throughout" contradicts the function definitions and must be
  qualified.
- Several **typographic defects** survive in the definitions and must not be propagated:
  (i) f7's optimum line prints "Global optimum: f3(x_opt) = 0" where f7 is meant (p. 13);
  (ii) the Schwefel 1.2 base function (Sec. 4.1.5, p. 6) and f15 (p. 18) print `x_i` inside
  the inner summation where the running index `x_j` / the transformed `z` is meant;
  (iii) f12's property list says "Separable" (p. 17) although Section 4 classifies f12 under
  *Overlapping Functions* and its definition is the coupled Rosenbrock chain. Cite the
  category taxonomy of Section 4 (pp. 4-5), not these property bullets, for separability
  claims.
- The report certifies `f_i(x_opt) = 0` for every function but provides **no per-function
  difficulty ordering and no reference results**, so "hardest function" claims cannot be
  sourced here.
- The report defines the suite; the authoritative numerical behaviour of any particular
  implementation (MATLAB/Octave, Java, C++, or a third-party port) is a property of that
  code, not of this PDF. Where an implementation and this report disagree, the disagreement
  must be disclosed, not silently resolved.
- The rotation matrices, permutation `P`, shift vectors `x_opt` and weights `w_i` are
  *data files* shipped with the code (Sec. 4.2.1, p. 7 lists them as symbols); the report
  does not print their values, so no claim about a specific instance can be sourced here.

## 7. Exact usable locators

| Claim the DT-GSK manuscript may need | Locator |
|---|---|
| Suite identity: 15 large-scale benchmarks extending CEC'2010; Li, Tang, Omidvar, Yang, Qin | title page + Abstract, p. 1 |
| Report date December 24, 2013 | title page, p. 1 |
| Four new features (nonuniform sizes, imbalance, overlap, transformations) | Sec. 2, p. 2; Conclusion, p. 20 |
| Formal definitions of partial / additive separability and full non-separability | Sec. 3, Defs. 1-3, p. 4 |
| The four function categories and the f1-f15 assignment | Sec. 4, pp. 4-5 |
| Six base functions (Sphere, Elliptic, Rastrigin, Ackley, Schwefel 1.2, Rosenbrock) | Sec. 4.1, p. 6 |
| Imbalance weights `w_i = 10^(3*N(0,1))` | Sec. 4.2.1, p. 7 |
| Transformations `T_osz`, `T_asy^beta`, `Lambda^alpha`, rotation `R`, overlap `m` | Sec. 4.2.1, pp. 7-8 |
| f4-f7 multiset `S = {50,25,25,100,50,25,25,700}`, D = 1000 | pp. 11-13 |
| f8-f11 20-element multiset, D = 1000 | pp. 14-16 |
| **f13/f14: overlap m = 5, D = 905** | pp. 17-18 |
| Per-function search bounds ([-100,100] / [-5,5] / [-32,32]) | pp. 9-18, per-function bullet lists |
| Ackley members f3/f6/f10 are defined on the transformed argument `Lambda^10 T_asy^0.2(T_osz(.))` | pp. 10, 12, 15 |
| Protocol: 15 problems, D = 1000, **25 runs**, MaxFE = 3e6, terminate at MaxFE | Sec. 5.1, p. 19 |
| Out-of-bounds evaluation returns NaN | Sec. 5.1, item 6, p. 19 |
| Milestones 1.2e5 / 6.0e5 / 3.0e6; report best/median/worst/mean/std over 25 runs | Sec. 5.2, p. 19; Table 2, p. 20 |
| Competition ranking is **median**-based at the three milestones | Sec. 5.2, p. 19 |
| Convergence curves requested for f2, f7, f11, f12, f13, f14 | Sec. 5.2, p. 19 |
| Reference runtime of 10,000 FEs per function; ~207 h for a full experiment | Table 1 + text, p. 19 |

## 8. Supported uses

- Citing the **CEC2013-LSGO suite definition**: the 15 functions, their four separability
  categories, base functions, subcomponent multisets, bounds, and the overlap construction.
- Citing the **official CEC2013-LSGO evaluation protocol**: D = 1000 (with f13/f14 at 905),
  25 runs per function, MaxFE = 3e6, milestones at 1.2e5 / 6.0e5 / 3.0e6, and
  best/median/worst/mean/std reporting.
- Grounding the statement that the suite deliberately introduces subcomponent imbalance,
  nonuniform subcomponent sizes and conforming/conflicting overlap as challenges to
  decomposition-based algorithms.
- Grounding the statement that the competition's own ranking criterion is the **median**
  error at the three milestones, if the manuscript contrasts its own mean-based reporting.
- Supporting the disclosure that f13 and f14 are 905-dimensional while the remaining
  thirteen functions are 1000-dimensional.

## 9. Unsupported / prohibited overextensions

- Do NOT cite this report for **any algorithm's LSGO result, score or competition rank**
  (MOS, SHADE-ILS, DECC-G or otherwise). The report contains no results whatsoever; use
  `latorre2013mos` / `molina2018shadeils` for published specialist results.
- Do NOT interchange this key with `liang2013cec2013`. Using either as the other suite's
  definition is a suite-identity error, not a citation-style slip.
- Do NOT cite it for a **51-run** protocol or a `10,000*D` FE budget -- those are the
  bound-constrained CEC2013/CEC2017 conventions. This suite is 25 runs and a fixed 3e6 FEs.
- Do NOT state "all functions are 1000-dimensional" on the strength of Section 5.1 alone;
  f13/f14 are 905-D by their own definitions.
- Do NOT attribute an **untransformed / raw** Ackley (or Rastrigin) formulation to this
  report. f3, f6 and f10 are defined only on the `Lambda^10 T_asy^0.2(T_osz(.))` chain.
  If an implementation evaluates a different Ackley composition, the divergence is a
  property of that implementation and must be disclosed against these pages, never
  presented as the report's definition.
- Do NOT cite it for the CEC'2010 suite's own definitions; the CEC'2010 report (its
  reference [42]) is the authority for those and is not in this corpus.
- Do NOT claim the report certifies difficulty rankings, landscape statistics, or the
  optimum's basin structure beyond the property bullets, which contain the defects listed
  in Section 6.

## 10. Role in DT-GSK framing (master Appendix B.4)

`li2013lsgo` -- **verified CEC2013-LSGO definition role**: the citation anchor whenever the
manuscript names the CEC2013 *large-scale* suite, its 15 functions, its D = 1000 / 905
dimensions, or its 25-run / 3e6-FE protocol. It is the fourth suite-definition key in
Appendix B.4, alongside `awad2016problem` (CEC2017), `das2011cec2011` (CEC2011) and
`liang2013cec2013` (CEC2013 bound-constrained), and it is the only admissible source for
the large-scale suite. Any statement about how *algorithms* perform on this suite requires
a different, verified source.
