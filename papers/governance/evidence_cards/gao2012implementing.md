# Evidence card — gao2012implementing

## Verified bibliographic identity
- Title: Implementing the Nelder-Mead simplex algorithm with adaptive parameters
- Authors: Fuchang Gao, Lixing Han
- Venue: Computational Optimization and Applications (Springer)
- DOI (printed on page 1 of local PDF): 10.1007/s10589-010-9329-3
- Identity status (reference_inventory.csv): `verified`. Local file is the
  online-first version (received 13 Jan 2010, (c) 2010 header); the BibTeX entry
  cites the 2012 issue 51(1), pp. 259-277 — consistent (recorded in inventory).
- Local file: `reference_papers/gao2012implementing.pdf`, 19 pages, fully readable.
- Page-locator convention for this card: **PDF page numbers (1-19)** of the
  online-first copy plus stable section/equation/table numbers. The published
  pagination (259-277) is NOT present in the local file; do not cite printed
  page numbers from memory.

## Research question and context
Why does the standard Nelder-Mead (NM) simplex method become inefficient as the
problem dimension grows, and can dimension-dependent (adaptive) choices of its
expansion/contraction/shrink parameters repair this? (Abstract, PDF p. 1;
Introduction, Sect. 1, PDF pp. 1-3.)

## Method and experimental scope
- Restates the standard NM iteration (Lagarias et al. version) with operations
  reflection/expansion/outside contraction/inside contraction/shrink and the
  standard parameters {alpha, beta, gamma, delta} = {1, 2, 1/2, 1/2}
  (Eq. (1.3), Sect. 1, PDF p. 2; iteration outline PDF pp. 2-3).
- Theory: proves that for uniformly convex objectives the expansion and
  contraction steps have a sufficient-descent property whose per-step reduction
  factor is (n-1)/(2 n^2), which decreases with dimension n and tends to 0 as
  n -> infinity (Theorem 2.1, Sect. 2, PDF p. 4; interpretation Sect. 3,
  PDF p. 9).
- Diagnosis: on the quadratic f(x) = x^T x with MATLAB FMINSEARCH, the fraction
  of NM steps that are reflections grows toward 1 as n rises through
  2,4,...,100, i.e., standard NM in high dimension degenerates to mostly
  reflections (Sect. 3 and Fig. 1, PDF pp. 10-11).
- Proposal: the Adaptive Nelder-Mead Simplex (ANMS) parameters
  alpha = 1, beta = 1 + 2/n, gamma = 0.75 - 1/(2n), delta = 1 - 1/n
  (Eq. (4.1), Sect. 4.1, PDF p. 11). For n = 2 ANMS is identical to standard
  NM (SNMS) (Sect. 4.1, PDF p. 11). Rationale: reduce reflection use and slow
  the collapse of the simplex diameter in high dimension (Sect. 4.1, PDF p. 11;
  Fig. 2, PDF p. 12).
- Experiments (Sect. 4.2, PDF pp. 12-17): comparison of ANMS vs. SNMS via
  FMINSEARCH with termination tolerances TolFun = TolX = 1e-4 and
  MaxIter = MaxFunEvals = 1e6 (Eq. (4.2), PDF p. 12), on
  (i) a uniformly convex quartic family (Eq. (4.3)) with n = 10..60 (Table 1,
  PDF p. 13); (ii) 18 More-Garbow-Hillstrom problems with 2 <= n <= 6
  (Table 2, PDF p. 14); (iii) 11 variable-dimension More-Garbow-Hillstrom
  problems up to n = 60 (Tables 3-4, PDF pp. 15-16); and (iv) an SNMS
  stagnation check with tighter tolerances (Table 5, PDF p. 17).
  Scope note: deterministic single-start runs; no CEC-style suites, no
  multi-run statistics, no stochastic baselines.

## Conservative findings (with exact locators)
1. Expansion/contraction steps of standard NM possess a descent property on
   uniformly convex functions; the guaranteed decrease scales as
   (n-1)/(2 n^2) * rho(D/2), vanishing with dimension — a theoretical account
   of NM's "effect of dimensionality" (Theorem 2.1, PDF p. 4; Sect. 3, PDF
   p. 9).
2. Standard NM uses an "overwhelmingly large number of reflections in high
   dimensions" on the quadratic test (Sect. 3, Fig. 1, PDF pp. 10-11).
3. ANMS (dimension-adaptive parameters, Eq. (4.1)) "substantially outperforms"
   SNMS on the uniformly convex family for n >= 20-ish and always attains a
   good approximation there, while SNMS can terminate prematurely (Table 1
   and following commentary, PDF p. 13).
4. On small dimensions (2 <= n <= 6) ANMS is comparable to SNMS in many
   cases (Table 2 and commentary, PDF pp. 13-14).
5. On the higher-dimensional test set, ANMS "clearly outperforms" SNMS
   overall; SNMS can stagnate at non-minimizers (e.g., lin, pen1, pen2)
   even with 1e6 evaluations and tighter tolerances (Tables 3-5 and
   commentary, PDF pp. 15-17).
6. Limitations acknowledged by the authors: no convergence theory for ANMS
   (it may fail like standard NM); initial-simplex choice matters and the
   FMINSEARCH default edges are short; ANMS still uses many reflections on
   hard problems (pen1, rosenbrock, vardim) in high dimension (Sect. 5,
   PDF pp. 17-18; Fig. 3, PDF p. 18).

## Limitations relevant to citation
- The descent theory assumes uniform convexity; conclusions for general
  nonconvex landscapes are heuristic extrapolation (explicitly flagged,
  Sect. 3 end, PDF p. 10).
- Benchmarks are classical smooth test problems up to n = 60; no evidence
  about CEC2017/CEC2011-style multimodal or hybrid functions and no evidence
  above n = 100 (reflection-fraction plots go to n = 100, optimization tables
  stop at n = 60).
- Single deterministic runs from fixed starting points; no statistical
  comparison methodology.
- NM (standard or adaptive) can converge to non-stationary points (McKinnon
  counterexamples cited, Sect. 1, PDF p. 3; Sect. 5, PDF p. 18).

## Supported uses in the DT-GSK manuscript
- Citing the standard NM operation set and standard parameters
  {1, 2, 1/2, 1/2} (Sect. 1, Eq. (1.3), PDF p. 2).
- Citing the dimension-adaptive parameter schedule
  beta = 1 + 2/n, gamma = 0.75 - 1/(2n), delta = 1 - 1/n as the established
  adaptive-NM (ANMS) choice if DT-GSK's Nelder-Mead endgame uses it
  (Eq. (4.1), Sect. 4.1, PDF p. 11) — cite only after verifying the frozen
  code actually implements these formulas.
- Supporting the qualitative statement that standard NM degrades with
  dimension and that dimension-dependent parameters mitigate this on smooth
  test problems (Theorem 2.1 PDF p. 4; Tables 1, 3, 4 PDF pp. 13-16).
- Motivating a bounded design rationale for using an NM-based local polish
  primarily as an endgame/refinement device rather than a global search.

## Unsupported / prohibited overextensions
- Do NOT claim ANMS guarantees convergence (authors state no convergence
  theory; Sect. 5, PDF pp. 17-18).
- Do NOT claim ANMS superiority on multimodal, noisy, constrained, or
  CEC-suite problems; the evidence is smooth classical test functions,
  n <= 60.
- Do NOT use this paper as evidence that an NM endgame improves a
  metaheuristic; it compares NM variants against each other only.
- Do NOT cite printed page numbers 259-277; the local copy lacks them.

## Role in DT-GSK framing (Appendix B.6)
Nelder-Mead basis, together with `nelder1965simplex`. This is the sanctioned
source for the adaptive-parameter NM implementation underlying DT-GSK's
"Nelder-Mead endgame" component (master Sect. 5.1). Any mechanism-level
comparison must first verify the frozen code against Eq. (4.1) and the
iteration outline (PDF pp. 2-3, 11).

## Verification quotation (identity)
"we propose an implementation of the Nelder-Mead method in which the
expansion, contraction, and shrink parameters depend on the dimension of the
optimization problem" (Abstract, PDF p. 1).
