# Evidence card — hansen2001cmaes

## Verified bibliographic identity
- Title: Completely Derandomized Self-Adaptation in Evolution Strategies
- Authors: Nikolaus Hansen; Andreas Ostermeier (Technische Universitaet Berlin, Fachgebiet fuer Bionik)
- Venue/year: Evolutionary Computation 9(2):159–195, 2001 (MIT Press; printed on p. 159)
- DOI (bib): 10.1162/106365601750190398
- Local file: `reference_papers/hansen2001cmaes.pdf` (37 pp.; PDF p. 1 = printed p. 159; printed page = PDF page + 158)
- Inventory status: identity `verified`, readable, admissible. SHA-256 `6c5b3c544c781c59cff9de300c9782c73afd42b4b521930327d37a84187dff5e`.
- Locator convention: printed journal pages (159–195).
- Extraction caveat: mathematical symbols inside equations extract poorly from this PDF (prose is fully legible); equation-level claims below are cited by equation number and page, verified from surrounding prose.

## Research question and context
How can the self-adaptation of arbitrary (zero-mean) normal mutation distributions in evolution strategies be made reliable and fast? The paper proposes two concepts — complete derandomization and cumulation (evolution paths) — leading to covariance matrix adaptation (CMA), and formalizes the (mu/mu_W, lambda)-CMA-ES (Abstract, p. 159; Sec. 1, pp. 159–161).

Context: reviews the three levels of mutation-distribution adaptation (isotropic step size, individual step sizes, arbitrary normal distributions; Sec. 1, pp. 160–161), the shortcomings of mutative strategy parameter control (MSC) (Sec. 2, pp. 162–164), and Schwefel's rotation-angle "correlated mutations" as the mutative alternative (Sec. 3.1, pp. 167–168).

## Method
- Four fundamental demands on any adaptation of a general linear encoding (Sec. 3, p. 166): Adaptation (progress on any convex-quadratic function should, after adaptation, match the sphere — even for condition numbers up to ~10^6 with non-axis-parallel principal axes), Performance (near-optimal-step-size sphere performance, loss factor up to ~10 acceptable), Invariance (translation/rotation/reflection of search space and strictly monotone transformations of f must not change strategy behavior), Stationarity (strategy parameters stationary under random selection).
- CMA principle (Sec. 3.2, pp. 168–170): the covariance matrix is changed to increase the probability of reproducing previously selected mutation steps; "the CMA implements a principle component analysis of the previously selected mutation steps to determine the new mutation distribution" (p. 169). Construction from weighted selected steps (Eq. 11, p. 169; Fig. 3, p. 170). Overall variance (global step size) is adapted separately and on a faster time scale (~n) than the shape (~n^2) (p. 169).
- Cumulation (Sec. 4, pp. 171–173): evolution path p_c built by weighted summation of successive selected steps (Eq. 12, p. 172); exploits sign/correlation information between successive steps that single-step statistics cannot see (Figs. 4–5, pp. 172–173); life span of accumulated information ~1/c_c generations (p. 172).
- Algorithm (Sec. 5, pp. 174–176): the (mu/mu_W, lambda)-CMA-ES fully defined by transitions Eqs. (13)–(17): sampling x = m + sigma·B·D·z (Eq. 13); evolution path p_c and rank-one covariance update with change rate c_cov (Eqs. 14–15); "conjugate" evolution path p_sigma and cumulative path-length control of sigma with damping d_sigma (Eqs. 16–17). Weighted recombination of the mu best of lambda individuals.
- Default parameters: Table 1, p. 177; lambda = 4 + floor(3·ln n) (Appendix A MATLAB code, p. 191: `lambda = 4 + floor(3*log(N))`); selection parameters relatively uncritical; small lambda default suits unimodal non-noisy problems, larger lambda for robustness/multimodality (Sec. 5.1, p. 177).
- Practical limitations (Sec. 5.2, pp. 178–179): failure modes = shortage of valid selection information and numerical precision (unbounded growth of cond(C); recommended cap ~10^14); too-small initial sigma can force unlearning; O(n^2) storage; eigendecomposition update every ~n/10 generations reduces cost.

## Experimental scope
- Test suite: 12 scalable functions (Table 3, p. 180) — convex-quadratic (sphere, Schwefel, cigar, tablet, ellipsoid with axis ratio up to 10^3, i.e., condition 10^6), ridge-type (parabolic ridge, sharp ridge), Rosenbrock, sum of different powers, and multimodal (generalized Rastrigin plus two mis-scaled Rastrigin variants with axis ratios 10 and 100). Non-separability enforced by evaluating in a randomly drawn orthonormal basis (pp. 179–181; basis generator Fig. 6, p. 181).
- Strategies compared: (mu/mu_I, lambda)-CMA-ES; (mu/mu_I, lambda)-CORR-ES (Schwefel rotation angles); PATH-ES (cumulative path-length control only, c_cov = 0); MUT-ES (mutative global step size) (Sec. 7, pp. 181–182).
- Dimensions n up to 320 for scaling studies (Fig. 10, p. 187); multimodal runs at n = 20 with 100 runs (Figs. 11–13, pp. 189–190). Performance measured in objective function evaluations to reach target f values.

## Conservative findings (with locators)
1. Adaptation demand met: after an adaptation phase the CMA-ES achieves progress rates on cigar/tablet/ellipsoid (condition 10^6, randomly oriented) identical to the sphere; behavior is identical on axis-parallel and rotated versions (Sec. 7.2, pp. 183–186; Figs. 8–9). In contrast, CORR-ES depends strongly on coordinate-system orientation, exploits separability, and misses the adaptation demand by factors up to ~10^3 vs sphere progress (pp. 183–185).
2. Invariance: CMA-ES results are independent of the chosen orthonormal basis — invariant to translation, rotation, reflection, and order-preserving transformations of f (Sec. 7, p. 182; demands p. 166; conclusion pp. 190–191).
3. Speed-ups: on badly scaled, non-separable functions, CMA-ES vs step-size-only ES gains are typically several orders of magnitude (Abstract, p. 159); vs PATH-ES a factor between ~10^2 and ~10^4 on condition-10^6 quadratics for n ∈ [5, 320] (Sec. 7.3, p. 186; Fig. 10, p. 187).
4. Scaling: CMA-ES scales between linear and quadratic with n — linear where long axes are learned (cigar, parabolic ridge; credit given to cumulation) or no adaptation is needed (sphere), close to quadratic where continuous re-adaptation is demanded (ellipsoid, tablet, Rosenbrock, sharp ridge, different powers) (Sec. 7.3, pp. 186–188).
5. Global search: on the mis-scaled Rastrigin functions (axis ratio 10 and 100, n = 20), CMA-ES reaches final function values better by factors ~10^2–10^3 than a mutative step-size ES and roughly 10x faster; the mechanism is that shape adaptation permits larger step sizes, which improves the global search of a local strategy (Sec. 7.4, pp. 188–190; Figs. 12–13). On the perfectly scaled Rastrigin both behave similarly (Fig. 11, p. 189).
6. Budget guidance: reliable adaptation of a significant distribution-shape change needs at least ~n^2 function evaluations; complete adaptation can take ~10·n^2; "to get always the most out of adaptation, CPU resources should allow roughly between 100·n and 300·n^2 function evaluations" (Sec. 8, p. 190).
7. Conceptual positioning: the step from isotropic ES to CMA-ES is compared to the step from gradient descent to quasi-Newton; "In simulations, the CMA-ES reliably approximates the inverse Hessian matrix" (Sec. 8, pp. 190–191).

## Limitations
- Test suite is mostly unimodal/local-convergence oriented; only functions 10–12 are multimodal (Sec. 6, p. 179); no CEC-style suite, no statistical hypothesis testing (single/median-of-runs presentation).
- 2001-era defaults; later CMA-ES refinements (rank-mu update, restarts such as IPOP/BIPOP) are NOT in this paper — do not cite them from here.
- Adaptation is limited by selection-information shortage and numerics (Sec. 5.2, pp. 178–179); premature end possible when cond(C) explodes.
- Performance claims are counted in function evaluations; internal cost is O(n^2) storage and eigendecomposition work (Sec. 5.2, p. 179; CPU times Sec. 7.1, p. 182).

## Exact usable locators (claim → locator)
- Derandomization concept + MSC shortcomings: Sec. 2, pp. 162–165.
- Four demands (adaptation/performance/invariance/stationarity): Sec. 3, p. 166.
- Equivalence of adapting arbitrary normal distributions and adaptive general linear encoding/decoding: Sec. 3, p. 165.
- CMA = PCA of selected steps; rank-one construction: Sec. 3.2, pp. 168–169 (Eq. 11; Fig. 3, p. 170).
- Cumulation/evolution path definition and benefit: Sec. 4, Eq. (12), pp. 171–173; Figs. 4–5.
- Full algorithm Eqs. (13)–(17): Sec. 5, pp. 174–176.
- Default parameter table: Table 1, p. 177; lambda default: p. 191 (Appendix A).
- Separate time scales for sigma (~n) vs shape (~n^2): Sec. 3.2, p. 169; Sec. 5.1 c_cov discussion, p. 178.
- Practical hints/limits (initial sigma, cond cap 10^14, O(n^2)): Sec. 5.2, pp. 178–179.
- Test functions: Table 3, p. 180; random orthonormal basis: Fig. 6, p. 181.
- Adaptation-demand verification runs: Sec. 7.2, pp. 183–186 (Figs. 8–9).
- Speed-up factors and scaling: Abstract p. 159; Sec. 7.3, pp. 186–188 (Fig. 10, p. 187).
- Global-search improvement on mis-scaled Rastrigin: Sec. 7.4, pp. 188–190 (Figs. 11–13).
- n^2 budget rule and quasi-Newton analogy: Sec. 8, pp. 190–191.

## Supported uses in the DT-GSK manuscript
- Conceptual-comparison citation for covariance adaptation: what CMA-ES adapts (full mutation covariance via selected-step statistics and evolution paths), its invariance properties, and why that matters on ill-conditioned non-separable landscapes — as a contrast to the GSK/DT-GSK operator style.
- Supporting precise claims about CMA-ES's adaptation time scales (~n^2 evaluations for shape) and its strength on high-conditioning problems, e.g., when discussing where covariance-adaptation-based competitors (LSHADE-SPACMA's CMA component, eGSK's fmincon-like local models) derive their advantage.
- Sourcing invariance as an evaluation principle (translation/rotation/monotone-transform invariance; Sec. 3 p. 166, Sec. 6 p. 181).

## Unsupported / prohibited overextensions
- Do NOT cite this paper for restart CMA-ES variants (IPOP/BIPOP/NBIPOP, iCMAES-ILS), rank-mu updates, or any CEC competition result — none appear here.
- Do NOT claim CMA-ES is a global optimizer in general; the authors explicitly frame ESs as local search strategies whose global performance on multimodal functions is initialization- and step-size-dependent (Sec. 7.4, p. 188).
- Do NOT source benchmark comparisons against DE or other EAs from here (only ES-internal comparators are tested).
- Avoid attributing exact modern default formulas (beyond lambda = 4 + floor(3 ln n) and Table 1) to this paper.

## Role in DT-GSK framing (Appendix B.3)
`hansen2001cmaes` — covariance-adaptation conceptual comparison: the canonical reference for full covariance-matrix adaptation, cumulative step-size control, and invariance, used to position structure-aware adaptation against the GSK-family knowledge-sharing operators and to explain the CMA component of hybrid baselines.

## Verification quotation (identity)
"Completely Derandomized Self-Adaptation in Evolution Strategies — Nikolaus Hansen ... Andreas Ostermeier ... (c) 2001 by the Massachusetts Institute of Technology, Evolutionary Computation 9(2): 159-195" (p. 159).
