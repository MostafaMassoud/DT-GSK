# Evidence card: kaveh2021pgo

## 1. Verified bibliographic identity

- Kaveh, Ali; Akbari, Hossein; Hosseini, Seyed Milad. "Plasma generation optimization:
  a new physically-based metaheuristic algorithm for solving constrained optimization
  problems." Engineering Computations (Emerald). DOI 10.1108/EC-05-2020-0235.
  Received 1 May 2020; accepted 5 Aug 2020; bib cites the 2021 issue — consistent.
- identity_status: **minor_metadata_mismatch** (reference_inventory.csv): bib given
  names are wrong ("Hamza Akbari", "Saeed Mahmoudi Hosseini"). **Resolution: adopt the
  source author names — Ali Kaveh, Hossein Akbari, Seyed Milad Hosseini** — in any
  rendered bibliography.
- Local file: `reference_papers/kaveh2021pgo.pdf`, 53 pp. (Emerald layout without
  printed issue pagination in extraction), sha256
  fb5c9da596798e7b75a60b0419954017b6b20a10a872d5a095662a71286f3720.
- Page convention: **PDF page numbers**.

## 2. Research question and context

Proposes Plasma Generation Optimization (PGO), a physically inspired population-based
metaheuristic in which each agent is an electron and movement/energy-level changes
simulate excitation, de-excitation, and ionization during plasma generation; the global
optimum corresponds to plasma with the highest degree of ionization (Abstract, PDF p. 1).
Positioned within the physics-based metaheuristic line of the first author (CSS, CBO,
ECBO, WEO, TEO, CPA, SSOA listed as prior art, PDF p. 2), targeting **constrained**
optimization (benchmark g-functions and truss sizing).

## 3. Method (Section 2, PDF pp. 3–22)

- Physics background (plasma, generation via fields/beams, chemical reactions, electron
  movement): Section 2.1, PDF pp. 3–5.
- Algorithm presentation (Section 2.2, PDF pp. 5–22), steps:
  1. random initialization of electrons and their energies (energy vector Eq. 4, PDF p. 10);
  2. simulation of d-orbitals via pear-shaped curves; orbital-length coefficient
     a_ij ~ U(0.6 + 0.1 t, 1.4 - 0.1 t), t = iteration/max_iteration (Eq. 5, PDF p. 10);
     transverse characteristic dy (Eqs. 6–7, PDF p. 10) shrinks the search domain around
     better electrons as iterations increase;
  3. step-size determination: with rand < EDR do excitation/de-excitation, otherwise
     ionization (Eq. 8, PDF p. 10); a second threshold DR selects de-excitation within
     the first branch (Eq. 18, PDF p. 22);
  4. position update by Eq. 18 (PDF p. 22); out-of-bounds variables are **clipped to the
     closer bound** (worked example, PDF p. 22);
  5. termination by max iterations; best electron reported (Step 5, PDF p. 22).
- Control parameters: **EDR** (excitation/de-excitation rate), **DR** (de-excitation
  rate), **DRS** (de-excitation step parameter).
- Sensitivity analysis (Section 3, PDF pp. 22–26): EDR in 0.6–0.8 balances
  intensification/diversification (values < 0.6 over-diversify, PDF p. 26); performance
  "not considerably sensitive" to DR, with DR = 0.2 converging fastest on the truss
  cases (PDF p. 26); DRS in 0.1–0.2 has the best convergence rate (PDF p. 26).

## 4. Experimental scope (Section 4, PDF pp. 26–43)

- **13 constrained benchmark functions g01–g13** (definitions in Appendix 1, PDF
  pp. 50 ff.): population 100, 2,400 iterations, stated maximum of 240,000 objective
  function evaluations; **30 independent runs**; PGO parameters EDR = 0.6, DR = 0.3,
  DRS = 0.15 (Section 4.1, PDF p. 26 and Section 4.1.1, PDF p. 29).
- Comparators for g01–g13 (results **taken from Patel & Savsani 2015**, not re-run):
  homomorphous mapping, adaptive segregational constraint-handling EA, simple
  multi-membered evolution strategy, GA, PSO, DE, ABC, biogeography-based optimization,
  TLBO, heat transfer search (Section 4.1.1, PDF pp. 29–30; Table 2, PDF pp. 15–16).
- **6 truss sizing problems** (weight minimization, cross-sectional areas as variables,
  Eq. 19, PDF p. 30): 10-bar planar, 25-bar spatial, 72-bar spatial, 120-bar dome,
  272-bar transmission tower, 582-bar tower (Sections 4.2.1–4.2.6, PDF pp. 35–43;
  comparison tables e.g. Table 5 for the 25-bar truss, PDF p. 23).

## 5. Conservative findings

- On g01–g13, PGO "obtains the optima for g01, g03, g04, g05, g06, g08, g09, g11, g12
  and g13 ... and also finds solutions very close to the optimum ones for g02, g07 and
  g10" (Section 4.1.1, PDF p. 30); authors add PGO often needs fewer evaluations to
  reach the same optima (PDF p. 30).
- On trusses, PGO's best weights are competitive with BB-BC, SAHS, TLBO, MSPSO, HPSSO,
  WEO, CPA (e.g. 25-bar truss best 545.17 lb vs 545.09–545.38 lb; Table 5, PDF p. 23).
- Authors' overall claim is deliberately modest: performance "is competitive with other
  considered state-of-the-art optimization methods" (Abstract, PDF p. 1; Conclusions,
  PDF p. 44).

## 6. Limitations

- Comparator results for g01–g13 are copied from the literature (Patel & Savsani 2015),
  so run counts/budgets across algorithms are only as comparable as that secondary
  source made them.
- **Internal FEs inconsistency**: Section 4.1 states 240,000 max evaluations
  (pop 100 x 2,400 iterations, PDF p. 26) while Section 4.2's discussion says "identical
  function evaluations (i.e. 24,000)" (PDF p. 30) — one figure is presumably a typo; do
  not quote either budget without noting the discrepancy.
- No CEC-suite experiments at all (no CEC2011/2013/2017); no nonparametric significance
  testing reported for the g-function comparisons.
- Physics narrative (orbitals, ionization) is metaphorical; the operative mechanism is
  the Eq. 5–18 sampling/step-size scheme.

## 7. Exact usable locators

| Claim the DT-GSK manuscript may need | Locator (PDF page) |
|---|---|
| PGO identity: physically based metaheuristic; agents = electrons; excitation/de-excitation/ionization; optimum = highest ionization | Abstract, p. 1 |
| Position in the physics-inspired algorithm lineage (CSS, CBO, ECBO, WEO, TEO, CPA, SSOA) | Section 1, p. 2 |
| Orbital-coefficient sampling and shrinking neighborhood (Eqs. 5–7) | p. 10 |
| EDR-gated choice of excitation/de-excitation vs ionization (Eq. 8) | p. 10 |
| Update rule and boundary clipping to closer bound (Eq. 18 + example) | p. 22 |
| Termination by max iterations | Step 5, p. 22 |
| Parameter sensitivity: EDR 0.6–0.8; DR insensitive (0.2 fastest); DRS 0.1–0.2 | Section 3, pp. 22–26 |
| g01–g13 setup: pop 100, 2,400 iterations, 240,000 FEs, 30 runs, EDR=0.6/DR=0.3/DRS=0.15 | pp. 26, 29 |
| Comparator list and provenance (Patel & Savsani 2015) | pp. 29–30 |
| g-function outcome (optima on 10 of 13; near-optima g02/g07/g10) | p. 30 |
| Truss formulation (weight minimization, grouped areas, Eq. 19) | p. 30 |
| Six truss case studies | Sections 4.2.1–4.2.6, pp. 35–43 |
| 25-bar truss comparison table (weights, std, NSAs) | Table 5, p. 23 |
| Conclusions (scope recap; competitive-performance claim) | p. 44 |

## 8. Supported uses

- Taxonomy/positioning: PGO as a recent physics-inspired metaheuristic exemplar
  (2020/2021 generation), with a correctly described mechanism and parameter set.
- Related-work sentences on physics-based algorithm proliferation and on
  engineering/structural (truss) application domains for metaheuristics.
- Example of author-tuned three-parameter control (EDR/DR/DRS) with published
  sensitivity analysis — usable when contrasting with adaptive/knowledge-based control
  in GSK-family methods.

## 9. Unsupported / prohibited overextensions

- Do NOT cite PGO results as evidence on any CEC suite; the paper contains none.
- Do NOT claim PGO is "state-of-the-art" beyond the authors' own "competitive" wording.
- Do NOT quote a single FEs budget for the g-function study without the 240,000 vs
  24,000 discrepancy caveat (Section 6).
- Do NOT use the g-function comparison as a like-for-like empirical baseline for
  DT-GSK (comparator numbers are secondhand from Patel & Savsani 2015).
- Do NOT attribute the bib's wrong author given names; use the source names.
- Per master Appendix B.5 discipline: no one-sentence token citation solely to consume
  the key.

## 10. Role in DT-GSK framing (master Appendix B.5)

`kaveh2021pgo` — **taxonomy/positioning only**: an "other metaheuristics" breadth
exemplar (physics-inspired, constrained/structural focus) for the related-work
landscape. Cite only where its verified mechanism, sensitivity findings, or
constrained/truss scope is genuinely discussed; never for CEC-benchmark performance
context.
