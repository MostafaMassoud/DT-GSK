# Evidence card — kolda2003directsearch

## Verified bibliographic identity
- Title: Optimization by Direct Search: New Perspectives on Some Classical
  and Modern Methods
- Authors: Tamara G. Kolda, Robert Michael Lewis, Virginia Torczon
- Venue: SIAM Review 45(3), pp. 385-482, 2003.
- DOI: source prints 10.1137/S0036144502428893; the BibTeX DOI is truncated
  (missing final "3"). Inventory disposition: adopt the source DOI.
- Identity status (reference_inventory.csv): `minor_metadata_mismatch`
  (identity certain; DOI truncation only).
- Local file: `reference_papers/kolda2003directsearch.pdf`, 98 pages, fully
  readable.
- Page-locator convention: **printed SIAM Review pages 385-482** (printed on
  every page of the local copy); PDF page = printed page - 384.

## Research question and context
A survey/synthesis: which direct search methods (derivative-free methods that
use only function comparisons) have rigorous convergence guarantees, and what
algorithmic features produce reliability? Introduces the unifying class
"generating set search" (GSS) (Sect. 1, pp. 387-388; Sect. 3, p. 400).

## Method and scope (survey + theory; no new benchmark experiments)
- Compass search defined: from the current iterate try steps of length
  Delta_k along the 2n signed coordinate directions
  D_plus = {e_1,...,e_n, -e_1,...,-e_n}; accept an improving trial point,
  otherwise halve the step (Sect. 1.1, p. 389; formalized Algorithm 3.1 and
  Sect. 3.1, p. 401). Historical root: Fermi and Metropolis on the Los
  Alamos Maniac, "slow but sure" (Sect. 1.1, p. 389).
- Applicability niche: direct search is recommended when gradients are
  unavailable/untrustworthy (e.g., simulation-based objectives); when
  accurate derivatives exist, gradient/Newton methods are the first
  recommendation, including the authors' own (Sect. 1.2, pp. 390-391).
- GSS defined: search directions must contain a generating set (positive
  spanning set) of R^n; includes compass search, Hooke-Jeeves pattern search,
  multidirectional search, EVOP variants, and sufficient-decrease variants
  (Sect. 3, pp. 400-401; Definition 3.1 in Sect. 3.4, pp. 406ff).
- Core convergence mechanics: for compass search the cosine measure of the
  coordinate set is bounded below by 1/sqrt(n), giving at unsuccessful
  iterations the implicit gradient bound
  ||grad f(x_k)|| <= sqrt(n) M Delta_k (Eq. (3.3), Sect. 3.2, pp. 402-403).
  General GSS version: Theorem 3.3, pp. 409-410 — at unsuccessful iterations
  ||grad f(x_k)|| <= kappa(G_k)^{-1} [M Delta_k beta_max + rho(Delta_k)/(Delta_k beta_min)].
- Global convergence: Theorem 3.11, pp. 421-422 — under Lipschitz-continuous
  gradient, bounded level set, and one of three globalization strategies
  (sufficient decrease; rational lattice; moving grids),
  liminf_{k->inf} ||grad f(x_k)|| = 0. Stronger "every limit point is
  stationary" version under Assumption 3.12 (Sect. 3.8.2, p. 422).
- Step-length-based stopping criterion is validated by the theory linking
  Delta_k to stationarity (Sect. 3.6 and 3.10; summary bullet, p. 470).
- Nelder-Mead assessment: NM and Spendley-Hext-Himsworth simplex methods are
  NOT GSS methods (single search direction, different decrease acceptance)
  (Sect. 4.1, p. 429); McKinnon's family shows NM can converge to a
  non-stationary point even on strictly convex C^2-parameterized functions
  via simplex collapse (Sect. 4.1, pp. 429-430); long-standing anecdotal and
  experimental evidence of NM failure, common fix is restarting (p. 430).
- Summary insights: geometry of search directions + globalization explains
  reliability; the cosine measure's dependence on dimension "help[s] explain
  the observation that performance deteriorates for problems with large
  numbers of variables"; local analysis explains slow asymptotic convergence
  (Sect. 9, pp. 470-471).

## Conservative findings (with exact locators)
1. Direct search methods "remain an effective option, and sometimes the only
   option, for several varieties of difficult optimization problems" and many
   have rigorous convergence guarantees (Sect. 1, p. 388, numbered points
   1-2).
2. Compass search definition and 2n coordinate-direction structure
   (Sect. 1.1 p. 389; Sect. 3.1 p. 401).
3. GSS methods converge globally to stationary points on smooth problems
   (Theorem 3.11, pp. 421-422; Summary, p. 470).
4. At unsuccessful iterations the step-length parameter bounds the gradient
   norm — the theoretical basis for step-size-based termination (Eq. (3.3)
   p. 403; Theorem 3.3 pp. 409-410; Sect. 3.10, p. 424 region; Summary
   bullet, p. 470).
5. Nelder-Mead lacks such guarantees and can fail by simplex degeneration
   (Sect. 4.1, pp. 429-430); this motivates restarts and convergent variants.
6. Direct search performance deteriorates with dimension; asymptotic
   convergence can be slow because no curvature information is used
   (Sect. 1.1, p. 390; Summary, p. 470).

## Limitations relevant to citation
- A survey with convergence theory for smooth (continuously differentiable,
  often Lipschitz-gradient) unconstrained/linearly constrained problems; no
  claims for multimodal global optimization and no benchmark competition
  results.
- Guarantees are for stationary points (local, first-order), not global
  optima.
- GSS theory does not cover Nelder-Mead (explicitly outside the framework,
  Sect. 4.1 p. 429; Summary p. 471).

## Supported uses in the DT-GSK manuscript
- Sanctioned basis for describing compass/coordinate/direct search and its
  properties wherever DT-GSK's final search / polish stage is compared
  conceptually with direct search (Appendix B.6; master Sect. 5.3 allows
  eigenframe-polish vs. direct-search comparison "only at the conceptual
  level supported by approved sources").
- Citing that direct search is appropriate when derivatives are unavailable
  (Sect. 1.2, pp. 390-391).
- Citing dimension-dependence and slow asymptotic convergence of direct
  search (p. 390; p. 470).
- Citing step-length-based stopping rationale (Theorem 3.3 pp. 409-410;
  Sect. 3.10; p. 470).
- Citing Nelder-Mead's known failure modes and its exclusion from the
  provably convergent class (pp. 429-430) as bounded motivation for
  safeguards (restarts, budget caps) around any NM endgame.

## Unsupported / prohibited overextensions
- Do NOT cite as evidence that direct search (or any DT-GSK polish stage)
  finds global optima or wins benchmark comparisons.
- Do NOT transfer GSS convergence guarantees to DT-GSK's composite
  algorithm, to its eigenframe polish, or to Nelder-Mead; the theory applies
  to GSS methods on smooth problems under stated assumptions.
- Do NOT imply equivalence between an eigenbasis/eigenframe search and
  generating-set search; master Sect. 5.3 forbids implying equivalence among
  support graph, covariance matrix, decomposition, and eigenbasis.

## Role in DT-GSK framing (Appendix B.6)
"Compass/direct-search basis" — the reference anchor for direct-search
concepts, terminology, and conceptual-level comparison with DT-GSK's final
search/polish machinery.

## Verification quotation (identity)
"Because there is no name for the particular class of direct search methods
that is our focus, we introduce the name generating set search (GSS)"
(Sect. 3, p. 400).
