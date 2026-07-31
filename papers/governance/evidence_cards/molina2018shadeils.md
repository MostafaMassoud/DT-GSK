# Evidence card: molina2018shadeils

## 1. Verified bibliographic identity

- Molina, Daniel; LaTorre, Antonio; Herrera, Francisco. "SHADE with Iterative Local Search
  for Large-Scale Global Optimization." **2018 IEEE Congress on Evolutionary Computation
  (CEC)**, pp. 1-8, 2018. DOI **10.1109/CEC.2018.8477755**.
- Affiliations on the title page (PDF p. 1): Molina and Herrera -- Department of Computer
  Science, University of Granada, Spain; LaTorre -- DATSI, ETSIINF, Center for Computational
  Simulation, Universidad Politecnica de Madrid, Spain.
- **ISBN 978-1-5090-6017-7** is printed in the page-1 footer
  ("978-1-5090-6017-7/18/$31.00 (c)2018 IEEE"); the running footer on PDF pp. 2-8 reads
  "2018 IEEE Congress on Evolutionary Computation (CEC)", which is the venue string used in
  the bib `booktitle`.
- The DOI and the `pages = {1--8}` range were verified against the CrossRef API on
  2026-07-28 (recorded in the provenance comment above the entry in `references.bib`); the
  title, authors and venue string were read off the PDF. No field was reconstructed from
  recollection.
- Local file: `reference_papers/molina2018shadeils.pdf`, 8 pp., sha256
  b87c53bf23092d64c1fc7c421d681afa6d5028963e710de6e66ddc2290c56bc5.
- Page convention in this card: **PDF page index** (the article carries no printed folios).

## 2. Research question and context

The paper proposes SHADE-ILS, "a new hybrid algorithm especially designed to tackle" large-
scale global optimization, defined as optimization whose "problem size reaches (or exceeds)
one thousand of variables" (Abstract and Sec. I, p. 1). It positions itself against the
incumbent: "the current state-of-art and winner of LSGO competitions since 2013, Multiple
Offspring Sampling, MOS", which "as far as the authors are concerned, had not been improved
since its proposal back in 2013" (Sec. I, p. 1). SHADE-ILS is a direct successor of the
authors' earlier IHDELS (2015), with three named changes (Sec. II, p. 2).

## 3. Method (Section II, pp. 2-3)

Algorithm 1 (p. 2) alternates, inside one budget loop, a DE phase and a local-search phase
on the current best solution, exploring all variables simultaneously -- "an important
difference compared to algorithms using variable grouping techniques" (p. 2). The population
is carried across DE calls and the LS parameters persist across LS calls except at restart.

Three differences from IHDELS, each stated explicitly (p. 2):

1. **Exploratory component is SHADE**, not SaDE (Sec. II-A, p. 2). The authors chose SHADE
   over L-SHADE because "the population size adjustment would reduce too quickly the
   exploration", and report having tested both, "obtaining the best results with SHADE".
2. **LS selection rule** (Sec. II-B, p. 2): the relative improvement
   `I_LS = (fitness(BeforeLS) - fitness(AfterLS)) / BeforeLS` (Eq. 1) is computed as in
   IHDELS, but the method with the **largest `I_LS` in its last application** is chosen
   rather than the largest average. This removes the `FreqLS` parameter.
3. **Restart mechanism** (Sec. II-C, p. 3): triggered when, over **three consecutive
   iterations**, the improvement ratio is **below 5%**. On restart a random population member
   `sol` is perturbed as `current_best = sol + rand_i * 0.1 * (b - a)`, the DE population is
   randomly re-initialised, and the LS adaptive parameters are reset to defaults.

Two local searches are used (Sec. II, p. 2): **MTS LS-1**, "very fast and appropriated for
separable problems, but ... very sensitive to rotations", and **L-BFGS-B**, "less powerful
[but] less sensitive to rotations".

Parameter values (Table I, p. 3): DE population size **100**; `FE_DE = 25000` and
`FE_LS = 25000` per iteration (so one iteration consumes 50,000 evaluations); MTS initial
step size 20; `RestartN = 3`; improvement threshold 5%.

## 4. Experimental scope (Section III, pp. 3-8)

- Benchmark: "the benchmark and the experimental conditions used in the **CEC2013 LSGO
  competition**" -- 15 functions, 1000 dimensions, the separability groups f1-f3 (fully
  separable), f4-f7 / f8-f11 (partially separable with / without a separable subcomponent),
  f12-f14 (overlapping), f15 (non-separable) (p. 3). The suite report is the paper's
  reference [12], i.e. `li2013lsgo`.
- **Run count: 51.** "Each algorithm is run for each function **51 times**, and each run
  finishes when a maximum number of evaluations ... is reached (**3 x 10^6** in this case)"
  (p. 3). This is the paper's own choice; the suite report specifies 25 runs.
- Eleven milestones are recorded, `{1.2, 3.0, 6.0, 9.0, 12, 15, 18, 21, 24, 27, 30} x 10^5`,
  but "in previous competitions only a subset of the milestones was considered: 1.2e5, 6.0e5,
  3.0e6, so we are going to use only these last milestones to allow a straightforward
  comparison with state-of-the-art algorithms" (p. 3).
- Table II (p. 4) is a four-way component study at 3e6 FEs; the "Better" row is
  12 / 1 / 0 / 2, and the text concludes the full proposal "obtains the best results in 12 of
  the 15 functions" (pp. 4-5).
- Table III (p. 5) reports wall-clock time per function for SHADE-ILS and IHDELS
  (SHADE-ILS "on average a 15% slower").
- Tables IV, V, VI (pp. 5-6) compare SHADE-ILS with MOS at 1.2e5, 6e5 and 3e6 FEs.
- **Table VII (p. 8)** is the full competition-format result table for SHADE-ILS: best,
  median, worst, mean and std for f1-f15 at each of the three milestones.

Head-to-head at the terminal budget (**Table VI, 3e6 FEs**, mean error):

| f | SHADE-ILS | MOS | better |
|---|---|---|---|
| F1 | 2.69e-24 | 0.00e+00 | MOS |
| F2 | 1.00e+03 | 8.32e+02 | MOS |
| F3 | 2.01e+01 | 9.17e-13 | MOS |
| F4 | 1.48e+08 | 1.74e+08 | SHADE-ILS |
| F5 | 1.39e+06 | 6.94e+06 | SHADE-ILS |
| F6 | 1.02e+06 | 1.48e+05 | MOS |
| F7 | 7.41e+01 | 1.62e+04 | SHADE-ILS |
| F8 | 3.17e+11 | 8.00e+12 | SHADE-ILS |
| F9 | 1.64e+08 | 3.83e+08 | SHADE-ILS |
| F10 | 9.18e+07 | 9.02e+05 | MOS |
| F11 | 5.11e+05 | 5.22e+07 | SHADE-ILS |
| F12 | 6.18e+01 | 2.47e+02 | SHADE-ILS |
| F13 | 1.00e+05 | 3.40e+06 | SHADE-ILS |
| F14 | 5.76e+06 | 2.56e+07 | SHADE-ILS |
| F15 | 6.25e+05 | 2.35e+06 | SHADE-ILS |

The paper's own summary of this table: "for the maximum number of FEs, 3 x 10^6, SHADE-ILS
gets the best results in **10 of the 15 functions**" and "While MOS continues to be better in
separable functions (f1-f3) SHADE-ILS is better for more complex ones: with the exception of
functions f6, f10, SHADE-ILS is clearly better in all the other functions" (p. 5). At the
**earliest** milestone the ordering is reversed -- "While MOS obtains better results at
1.2 x 10^5 FEs, both algorithms are very similar at 6 x 10^5 FEs" (p. 5).

**Independently verifiable cross-check.** The MOS column of Table VI reproduces, value for
value across all 15 functions, the `FEs = 3.0e+06 / Mean` row of Table IV in
`latorre2013mos` (that card, Sec. 4). The two published tables are therefore consistent, and
either may be cited for the MOS terminal-budget means -- but `latorre2013mos` is the primary
source.

Section III-D (pp. 5-6) describes the competition aggregation used since CEC'2013: sort
algorithms per function by average mean error, award F-1-style points (25 to the best, 18 to
the runner-up, 15 to the third, and so on), sum across functions. Figure 2 (p. 7) shows
SHADE-ILS with the highest point total at 6e5 and 3e6 FEs among IHDELS_2015, MOS, SHADE-ILS
and VMODE.

## 5. Conservative findings

- SHADE-ILS obtains a lower mean error than MOS on 10 of the 15 CEC2013-LSGO functions at
  3e6 FEs, and a higher one on 5 (F1, F2, F3, F6, F10) -- the paper's own Table VI.
- The advantage is milestone-dependent: MOS is better at 1.2e5 FEs (Table IV), the two are
  comparable at 6e5 (Table V), and SHADE-ILS leads at 3e6 (Table VI).
- The paper's stated headline is that SHADE-ILS beats "MOS for the first time since
  CEC'2013" (Conclusions, p. 6).
- Ablation (Table II): the restart change matters more than the DE change -- "The change in
  the restart mechanism has a more important effect than that on the DE component" (p. 4).

## 6. Limitations

- **Run count deviates from the suite report**: 51 runs here versus the 25 runs specified in
  `li2013lsgo` Sec. 5.1. Any comparison that pools this paper's numbers with 25-run banks
  must disclose the difference; it cannot be presented as protocol-identical.
- The comparison is **against MOS and IHDELS/VMODE only**. No GSK-family algorithm appears
  anywhere in the paper, and no claim about GSK, AGSK or any of their variants can be
  sourced here.
- No official CEC ranking is reproduced. Figure 2 is the authors' own application of the
  competition point scheme to a four-algorithm field they selected; it is not an
  organizer-certified competition result.
- Tables IV-VI give **mean** error only (Table VII adds best/median/worst/std for SHADE-ILS
  but not for MOS), so median-based comparisons -- which is what `li2013lsgo` Sec. 5.2 says
  the competition actually ranks on -- cannot be reconstructed for MOS from this paper.
- No dispersion or significance test accompanies the SHADE-ILS-versus-MOS comparison; the
  "10 of 15" statement is a win count, not a hypothesis test.
- Typographic defect: the SHADE-ILS column in **Table IV is headed "IHSHADELS"** (p. 5)
  although the surrounding text and Tables V-VI call it SHADE-ILS. Cite the caption and the
  body text, not the column header.
- The paper does not restate the suite's function definitions; for those, cite `li2013lsgo`.

## 7. Exact usable locators

| Claim the DT-GSK manuscript may need | Locator |
|---|---|
| SHADE-ILS identity, authors, venue, ISBN | title page + footer, p. 1 |
| Definition of LSGO as >= ~1000 variables | Sec. I, p. 1 |
| MOS described as the LSGO competition winner since 2013 and previously unbeaten | Sec. I, p. 1; Sec. III-C, p. 5 |
| Algorithm skeleton: alternating SHADE and a selected LS, all variables at once | Algorithm 1 + text, p. 2 |
| SHADE chosen over L-SHADE (population reduction too fast) | Sec. II-A, p. 2 |
| LS pool = MTS LS-1 and L-BFGS-B, with their complementary sensitivities | Sec. II, p. 2 |
| LS selection by largest last-application improvement (Eq. 1) | Sec. II-B, p. 2 |
| Restart after 3 iterations with < 5% improvement; perturbation and reset rules | Sec. II-C, p. 3 |
| Parameters: popsize 100; 25000 FEs to DE and 25000 to LS per iteration | Table I, p. 3 |
| Benchmark = CEC2013 LSGO, 15 functions, 1000 D, separability groups | Sec. III, p. 3 |
| **51 runs, 3e6 FEs, milestones 1.2e5 / 6e5 / 3e6 used for comparison** | Sec. III, p. 3 |
| Component ablation; restart matters more than the DE swap; best in 12 of 15 | Table II + text, pp. 4-5 |
| Runtime penalty of ~15% versus IHDELS | Table III + text, p. 5 |
| SHADE-ILS vs MOS at 1.2e5 (MOS ahead) | Table IV, p. 5 |
| SHADE-ILS vs MOS at 6e5 (comparable) | Table V, p. 5 |
| **SHADE-ILS vs MOS at 3e6: SHADE-ILS best on 10 of 15; MOS on F1, F2, F3, F6, F10** | Table VI + text, pp. 5-6 |
| Full competition-format SHADE-ILS table (best/median/worst/mean/std, 3 milestones) | Table VII, p. 8 |
| Competition point scheme (25 / 18 / 15 ...) and the four-algorithm comparison | Sec. III-D, pp. 5-6; Fig. 2, p. 7 |
| "beating MOS for the first time since CEC'2013" | Conclusions, p. 6 |

## 8. Supported uses

- Citing **published SHADE-ILS results on CEC2013-LSGO** by name and value, at the 1.2e5,
  6e5 and 3e6 milestones, taken from Tables VI and VII.
- Citing SHADE-ILS as a **specialist large-scale optimizer** whose design is explicitly
  LSGO-targeted (DE plus alternating MTS-LS1 / L-BFGS-B intensification with restarts).
- Grounding the large-scale limitation sentence (LM-06) that dedicated LSGO specialists such
  as SHADE-ILS attain error levels the general-purpose family does not target, **provided
  the sentence quotes the published values and never compares them to this project's own
  banks as if the protocols matched**.
- Supporting the historical statement that MOS was the unbeaten LSGO competition winner from
  2013 until this paper (the authors' own framing, Sec. I and Conclusions).
- Supporting the observation that the SHADE-ILS advantage is budget-dependent and that MOS
  remains ahead on the fully separable functions f1-f3.

## 9. Unsupported / prohibited overextensions

- Do NOT present the numbers in this paper as **protocol-comparable** with any 25-run
  CEC2013-LSGO bank without disclosing that this paper used 51 runs (Sec. III, p. 3).
- Do NOT cite it for an **official CEC competition rank or award**; Figure 2 is the authors'
  own point aggregation over a field they chose.
- Do NOT claim SHADE-ILS superiority over **GSK, AGSK, DT-GSK or any GSK-family member**;
  none is evaluated, mentioned or cited anywhere in the paper.
- Do NOT claim SHADE-ILS dominates MOS outright. It loses on F1, F2, F3, F6 and F10 at 3e6
  FEs and loses overall at 1.2e5 FEs, by the paper's own tables.
- Do NOT use it as the **CEC2013-LSGO suite definition**; that is `li2013lsgo`.
- Do NOT attribute the MOS numbers to this paper as primary evidence; they are reproduced
  from `latorre2013mos`, which is the primary source.
- Do NOT derive a statistical claim (significance, effect size, rank test) from this paper;
  it reports win counts and point totals only.

## 10. Role in DT-GSK framing (master Appendix B.4)

`molina2018shadeils` -- **competition context: published LSGO-specialist results only where
the source supports the stated claim**. It sits in Appendix B.4 for the same reason as
`awad2017ensemble` and `brest2017single`: it is a CEC competition-track paper cited for what
its own tables print, not for a lineage or taxonomy role. Its single sanctioned function in
this manuscript is to supply *published* SHADE-ILS values for the mandatory large-scale
limitation sentence, alongside `latorre2013mos` for MOS and `li2013lsgo` for the suite
itself. It licenses no comparison against the GSK family and no first-party result.
