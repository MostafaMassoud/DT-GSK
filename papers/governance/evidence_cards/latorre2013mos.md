# Evidence card: latorre2013mos

## 1. Verified bibliographic identity

- LaTorre, Antonio; Muelas, Santiago; Pena, Jose-Maria. "Large Scale Global Optimization:
  Experimental Results with MOS-based Hybrid Algorithms." **Proceedings of the 2013 IEEE
  Congress on Evolutionary Computation**, pp. **2742-2749**, 2013.
  DOI **10.1109/CEC.2013.6557901**.
- Title-page casing is preserved exactly as printed ("MOS-based", lower-case "based");
  author names are printed with diacritics as "Jose-Maria Pena" (accented on the title page)
  and are carried in the bib with LaTeX accent macros.
- Affiliations on the title page (PDF p. 1): all three authors -- DATSI, Facultad de
  Informatica, Universidad Politecnica de Madrid; LaTorre additionally -- Instituto Cajal,
  Centro Superior de Investigaciones Cientificas (CSIC).
- The PDF carries **no printed DOI, venue line or page folios**. The venue string follows the
  house precedent already established for this exact venue by `tanabe2013shade`
  ("Proceedings of the 2013 IEEE Congress on Evolutionary Computation"). The DOI and page
  range were verified against the CrossRef API on 2026-07-28 (see the provenance comment in
  `references.bib`). The page range is **independently corroborated inside this corpus**:
  reference [7] of `molina2018shadeils` (PDF p. 6) cites this paper as
  "in 2013 IEEE Congress on Evolutionary Computation (CEC 2013), Cancun, Mexico, 2013,
  pp. 2742-2749".
- Local file: `reference_papers/latorre2013mos.pdf`, 8 pp., sha256
  e71952bd40cd9eb519970458edc00a20e33843b02420d9d975cfcfdaf4817257.
- Page convention in this card: **PDF page index**.
- Disambiguation: this is NOT `latorre2012mos` (the earlier MOS paper, present in
  `reference_papers/` as lineage context but not an admitted citation key).

## 2. Research question and context

The paper describes "the whole process of creating a competitive hybrid algorithm, from the
experimental design to the final statistical validation of the results" on the benchmark of
the "Special Session on Large Scale Global Optimization" held at IEEE CEC 2013 (Abstract and
Sec. I, p. 1). Its two claims are that a disciplined experimental design "is able to find a
combination of algorithms that outperforms any of its composing algorithms by automatically
selecting the most appropriate heuristic for each function and search phase", and that the
resulting algorithm "obtains statistically better results than the reference algorithm
DECC-G" (Abstract, p. 1). The suite reference is the paper's [4], i.e. `li2013lsgo`.

## 3. Method (Section III, pp. 2-3; Section IV, pp. 2-4)

**Eight candidate algorithms** were tuned individually (Sec. III-A, p. 2): a Genetic
Algorithm (BLX-alpha crossover, alpha = 0.5, Gaussian mutation); Differential Evolution with
exponential crossover; Self-Adaptive DE; Generalized Opposition-Based DE (GODE);
Self-Adaptive GODE (proposed for this work); the Solis and Wets direct-search method;
MTS-LS1; and **MTS-LS1-Reduced**, a new local search proposed in this paper that spends most
of its evaluations on the dimensions with the largest recorded score improvements,
controlled by `improvePerc` and `minPerc`.

**MOS** (Sec. III-B, p. 2) is "a framework for the development of Dynamic Hybrid Evolutionary
Algorithms". The participation of each member -- "the number of new candidate solutions that
each algorithm is allowed to create" -- is adjusted dynamically by a quality measure, here
"the average fitness increment of the newly created individuals". The hybrid follows an
**HRH (High-level Relay Hybrid)** scheme: members run in sequence, each reusing the previous
member's output population, with the search divided into steps of a fixed number of FEs and
the participation for step `i+1` set from performance at step `i`.

**Tuning** (Sec. IV, pp. 2-3): a fractional design on orthogonal matrices following the
Taguchi method, with the "smaller is better" signal-to-noise ratio of Eq. 1; "a maximum of 27
different configurations were tested for each algorithm on the whole set of functions"
(p. 3). Table I (p. 3) lists every parameter grid; Fig. 1 (p. 4) is the GA main-effects plot.

**Member selection** (Table II, p. 4) ranks the eight tuned algorithms by average Friedman
rank and by the nWins procedure (pairwise Wilcoxon signed-rank at alpha = 0.05, +1 for a
significant win, -1 for a significant loss):

| Algorithm | Ranking | nWins |
|---|---|---|
| MTS-LS1-Reduced | 2.63 | 7 |
| MTS-LS1 | 3.70 | 3 |
| Solis and Wets | 4.13 | 2 |
| GA | 4.47 | 1 |
| Self-Adaptive DE | 4.20 | 0 |
| Self-Adaptive GODE | 4.47 | -1 |
| GODE | 6.13 | -6 |
| DE | 6.27 | -6 |

Three members were selected for the hybrid: **MTS-LS1-Reduced, Solis and Wets, and the GA**
(p. 4). MTS-LS1 was excluded as a simplified version of MTS-LS1-Reduced; Self-Adaptive DE
lost to the GA on nWins despite a marginally better rank; the remaining population-based
methods were dropped because their required population sizes were too far from the GA's.
**The final MOS configuration therefore contains no DE component.** Hybrid-level parameters
(`minPart`, `stepFactor`) were tuned by the same fractional design (Table III, p. 4).

**Protocol** (Sec. IV, p. 4): "In order to make the results comparable with other algorithms,
we have strictly followed the conditions imposed by the benchmark. Therefore, for each
combination, **25 independent executions** were carried out. The stopping criterion, as
defined in the benchmark, was a fixed number of fitness evaluations (**3M FEs**)." The
response variable is the error between the best individual found and the global optimum.

## 4. Results (Section V, pp. 4-7)

**Convergence** (Sec. V-A, pp. 4-5): average curves over 25 runs for the six functions
selected by the organizers -- F2, F7, F11, F12, F13, F14 (Figs. 2-7) -- plus participation
plots for F12 and F13 (Figs. 8-9) showing which member dominates at each search phase. The
authors observe that "the hybrid algorithm does not seem to completely converge in none of
the analyzed functions" (p. 6).

**MOS results** (Table IV, p. 7): best / median / worst / mean / std at FEs = 1.2e+5, 6.0e+5
and 3.0e+6 for all 15 functions. Terminal-budget (3.0e+6) **mean** errors:

| f | MOS mean | f | MOS mean |
|---|---|---|---|
| F1 | 0.00e+00 | F9 | 3.83e+08 |
| F2 | 8.32e+02 | F10 | 9.02e+05 |
| F3 | 9.17e-13 | F11 | 5.22e+07 |
| F4 | 1.74e+08 | F12 | 2.47e+02 |
| F5 | 6.94e+06 | F13 | 3.40e+06 |
| F6 | 1.48e+05 | F14 | 2.56e+07 |
| F7 | 1.62e+04 | F15 | 2.35e+06 |
| F8 | 8.00e+12 | | |

The authors' own reading (Sec. V-B, p. 6): the algorithm "is able to solve one function to
the maximum precision (F1) and another one to a very low error value (F3)", and "for all the
functions the differences between the mean and the median are very low".

**Versus its own members** (Table V, p. 6), MOS as the control algorithm, Wilcoxon
signed-rank on the 15 per-function average errors, with the Good (1992) sample-size
standardization `p_stan = min(1/2, p * sqrt(N)/10)` (Eq. 2):

| MOS vs. | Wilcoxon p | standardized p |
|---|---|---|
| MTS-LS1-Reduced | 6.03e-02 | 2.44e-02 (significant) |
| GA | 9.03e-03 (significant) | 3.50e-03 (significant) |
| Solis and Wets | 3.05e-05 (significant) | 1.18e-05 (significant) |
| all three, FWER-adjusted | 9.06e-02 | 3.51e-02 (significant) |

MOS is significantly better than the GA and Solis and Wets on the raw p-value; against
MTS-LS1-Reduced it is significant only after the standardization.

**Versus the reference algorithm** (Sec. V-D, Table VI, pp. 6-7): MOS "obtains the best
performance in **14 out of 15 functions**", losing only F6 by one order of magnitude, with a
Wilcoxon p-value of **3.05e-04** (standardized 1.18e-04).

## 5. Conservative findings

- MOS as configured here is a **GA + Solis-and-Wets + MTS-LS1-Reduced** HRH hybrid, tuned by
  a Taguchi fractional design, run under the suite's own 25-run / 3e6-FE protocol.
- It is statistically better than each of its three composing algorithms (raw p for two of
  three; all three after standardization and under FWER) and than the cooperative-
  coevolution reference algorithm (14 of 15 functions, p = 3.05e-04).
- Table IV is the **primary published source** for MOS's per-function CEC2013-LSGO results;
  the MOS column of Table VI in `molina2018shadeils` reproduces its 3.0e+06 mean row exactly.

## 6. Limitations

- **The paper never claims a competition win.** It reports a special-session entry and a
  comparison against three internal members and one reference algorithm. The
  "winner of LSGO competitions since 2013" framing exists only in `molina2018shadeils`
  (Sec. I, p. 1) as those authors' characterization, and even there it is not an
  organizer-certified ranking.
- **The reference algorithm's name is printed inconsistently**: "DECC-G" in the Abstract and
  in the Sec. V-D text, "DECC-CG" as the Table VI row label, and "DECC-GG" in the
  Conclusions (pp. 1, 6, 7, 8). Its reference [25] is Yang, Tang and Yao (2008),
  *Large Scale Evolutionary Optimization Using Cooperative Coevolution*. Because CR-0020 did
  not admit a DECC-G key, this comparison may be described only in general terms
  ("the special session's reference cooperative-coevolution algorithm") and its numbers must
  not be quoted as DECC-G results.
- The robustness inference from "mean and median are very low [in difference]" (p. 6) is
  weaker than it reads: on **F6** the best run is 1.95e+01 against a median of 1.39e+05, and
  on **F10** the best is 5.92e+02 against a median of 1.18e+06 (Table IV). The run
  distribution on those two functions is strongly bimodal even though the mean tracks the
  median.
- Table II lists the eight algorithms **in nWins order, not rank order** (Self-Adaptive DE,
  rank 4.20, is printed below the GA, rank 4.47). Quote the numbers, not the row order.
- The comparison set is the three composing algorithms plus one reference algorithm. **No
  GSK-family algorithm and no modern DE competitor (SHADE, L-SHADE, jSO) is evaluated**, so
  no claim about MOS versus those families can be sourced here.
- No confidence intervals or effect sizes are reported; the evidence is win counts plus
  Wilcoxon p-values over a 15-value sample, which the authors themselves flag as small
  enough to need the Good standardization (Eq. 2, p. 6).
- The paper does not restate the suite's function definitions, dimensions or milestones; for
  those, cite `li2013lsgo`.

## 7. Exact usable locators

| Claim the DT-GSK manuscript may need | Locator |
|---|---|
| MOS identity, authors, affiliations | title page, p. 1 |
| Benchmark = CEC 2013 LSGO special-session suite, 15 functions | Abstract; Sec. IV, p. 2 |
| MOS is a framework for dynamic hybrid EAs; participation adjusted by average fitness increment | Sec. III-B, p. 2 |
| HRH (High-level Relay Hybrid) definition and taxonomy | Sec. II, p. 1; Sec. III-B, p. 2 |
| The eight tuned candidate algorithms | Sec. III-A, p. 2 |
| MTS-LS1-Reduced is new in this paper; `improvePerc` / `minPerc` | Sec. III-A.8, p. 2 |
| Taguchi fractional design, SN ratio "smaller is better" (Eq. 1), <= 27 configurations | Sec. IV, pp. 2-3 |
| Per-algorithm parameter grids | Table I, p. 3 |
| Friedman ranks and nWins for the eight candidates | Table II, p. 4 |
| **Final hybrid = GA + Solis and Wets + MTS-LS1-Reduced (no DE member)** | Sec. IV text, p. 4 |
| Hybrid parameters `minPart`, `stepFactor` | Table III, p. 4 |
| **Protocol: 25 independent executions, 3M FEs, benchmark conditions strictly followed** | Sec. IV, p. 4 |
| Convergence curves for the six organizer-selected functions (F2, F7, F11, F12, F13, F14) | Sec. V-A, Figs. 2-7, pp. 4-5 |
| Member-participation plots for F12 and F13 | Figs. 8-9, p. 6 |
| **Full MOS results: best/median/worst/mean/std at 1.2e5, 6.0e5, 3.0e6** | Table IV, p. 7 |
| F1 solved to maximum precision; F3 to a very low error | Sec. V-B, p. 6 |
| MOS vs each composing algorithm: Wilcoxon and standardized p-values; FWER row | Table V, p. 6 |
| Good (1992) sample-size standardization formula | Eq. 2, p. 6 |
| MOS best in 14 of 15 functions vs the reference algorithm; p = 3.05e-04 | Sec. V-D + Table VI, pp. 6-7 |

## 8. Supported uses

- Citing **published MOS results on CEC2013-LSGO** by name and value (Table IV), including
  the fact that they were produced under the suite's own 25-run / 3e6-FE protocol.
- Citing MOS as a **specialist large-scale optimizer**: an HRH hybrid that dynamically
  reallocates the evaluation budget between a GA, Solis and Wets, and MTS-LS1-Reduced.
- Grounding the large-scale limitation sentence (LM-06) that dedicated LSGO specialists such
  as MOS reach error levels the general-purpose family does not target, **provided the
  sentence quotes the published values and does not compare them to this project's own
  banks as if the protocols matched**.
- Supporting a methodological remark that MOS's members were selected by a documented
  design-of-experiments procedure (Taguchi SN ratio, Friedman ranks, nWins) rather than by
  ad-hoc choice.
- Supporting the statement that MOS is statistically better than each of its own composing
  algorithms and than the special session's reference cooperative-coevolution algorithm.

## 9. Unsupported / prohibited overextensions

- Do NOT cite this paper as proof that **MOS won the CEC2013 (or any) LSGO competition**. It
  contains no ranking, no score table and no organizer statement. "Winner" language is
  supported in this corpus only as `molina2018shadeils`'s own characterization.
- Do NOT quote the Table VI reference-algorithm numbers **as DECC-G results**; the name is
  printed three different ways and no DECC-G key was admitted by CR-0020.
- Do NOT claim MOS superiority over **GSK, AGSK, DT-GSK, SHADE, L-SHADE, jSO or any
  algorithm not in Tables II, V and VI**; none is evaluated here.
- Do NOT present these numbers as protocol-comparable with results produced under a
  different run count or budget without disclosure; this paper is 25 runs / 3e6 FEs.
- Do NOT infer per-run robustness from the mean-versus-median remark: F6 and F10 have
  best values several orders of magnitude below their medians (Table IV).
- Do NOT use it as the **CEC2013-LSGO suite definition**; that is `li2013lsgo`.
- Do NOT confuse this key with `latorre2012mos` (the earlier MOS paper, not an admitted key).

## 10. Role in DT-GSK framing (master Appendix B.4)

`latorre2013mos` -- **competition context: published LSGO-specialist results only where the
source supports the stated claim**. Like `awad2017ensemble` and `brest2017single`, it is a
CEC competition-track paper admitted to Appendix B.4 for what its own tables print. Its
single sanctioned function in this manuscript is to supply *published* MOS values for the
mandatory large-scale limitation sentence, paired with `molina2018shadeils` for SHADE-ILS and
`li2013lsgo` for the suite definition. It licenses no comparison against the GSK family, no
competition-rank claim, and no first-party result.
