# Evidence card — nelder1965simplex

## Verified bibliographic identity
- Title: A Simplex Method for Function Minimization
- Authors: J. A. Nelder and R. Mead (National Vegetable Research Station, Wellesbourne, Warwick)
- Venue: The Computer Journal, vol. 7, no. 4, 1965, pp. 308–313
- DOI (bib): 10.1093/comjnl/7.4.308
- Local source: `reference_papers/nelder1965simplex.pdf` (6 pp., image-only scan, NO text layer)
- Identity status: verified (visually); readability: image_only_no_text_layer. All content below was read visually from the page scans. IMPORTANT: the scan's page order is shuffled — PDF page 4 contains journal page 312 and PDF page 5 contains journal page 311; PDF pages 1,2,3,6 = journal pages 308,309,310,313. Locators below use JOURNAL page numbers.

## Research question and context
How to minimize a function of n variables using only function-value comparisons (no derivatives), by adapting Spendley, Hext & Himsworth's (1962) simplex design so the simplex deforms to the local landscape instead of using rigid steps? Motivated by statistical likelihood maximization with non-linear parameters (p. 308, opening paragraphs and abstract).

## Method
- Maintain (n+1) points P0..Pn of a general (not necessarily regular) simplex; yh/yl are the highest/lowest function values; P̄ is the centroid of points excluding Ph (p. 308).
- Three operations replace the worst point Ph each iteration (p. 308):
  - Reflection: P* = (1+α)P̄ − αPh, reflection coefficient α > 0.
  - Expansion (when reflection produced a new minimum): P** = γP* + (1−γ)P̄, expansion coefficient γ > 1.
  - Contraction (when reflection fails, y* > yi for all i ≠ h): P** = βPh + (1−β)P̄, contraction coefficient 0 < β < 1; on failed contraction, shrink all points: Pi ← (Pi + Pl)/2.
- α, β, γ give the factor by which the simplex volume changes under each operation (p. 308). Complete method as flow diagram, Fig. 1 (p. 309).
- Stopping criterion: standard error of the y-values over the simplex, sqrt(Σ(yi − ȳ)²/n), falls below a preset value — chosen for statistical estimation contexts, and differing from Powell's (1964) criterion (pp. 308–309).
- Constraints: handled by variable transformation (e.g., logarithm) or by assigning a large positive value outside the permitted region; linear constraints by reducing dimensionality of the initial simplex (p. 309).
- Appendix: estimating the Hessian (information) matrix at the minimum by fitting a quadratic surface to the simplex points plus "half-way" points; xmin = −B⁻¹a; variance–covariance matrix QB⁻¹Q′ (pp. 312–313).

## Experimental scope
- Three classical test functions, all with minimum 0 (pp. 309–310): (1) Rosenbrock's parabolic valley, start (−1.2, 1); (2) Powell's quartic, start (3, −1, 0, 1); (3) Fletcher & Powell's helical valley, start (−1, 0, 0).
- Stopping threshold sqrt(Σ(yi − ȳ)²/n) < 10⁻⁸; final centroid value typically within 10⁻⁸ of the true minimum (geometric-mean deviation 2.5 × 10⁻⁹) (p. 310).
- Strategy (α, β, γ) trials over several initial step-lengths and eight initial-simplex arrangements; Tables 1–2 report mean/minimum numbers of evaluations (pp. 310–311).
- Variable-count scaling: sum of fourth powers, k = 2..10 variables (p. 311).

## Conservative findings
1. The strategy α = 1, β = 1/2, γ = 2 was clearly the best of those tried; lower α, β gave slower convergence, and the extra strategies converged to false minima on some occasions with function (3) (p. 310).
2. Mean evaluations to converge (over unasterisked step-lengths): 144 for function (1), 216 for (2), 228 for (3); Powell (1964)'s method needed about 150 and 235 evaluations to reach the same 2.5 × 10⁻⁹ level on functions (1) and (2) — i.e., little difference at this accuracy (p. 310, Table 2 on p. 311).
3. On three typical runs (Table 3, p. 312), the simplex method establishes an initial advantage over Powell's method; for functions (1) and (3) the advantage grows until Powell's method rapidly closes the gap at the final stage.
4. Effect of number of variables: mean evaluations N ≈ 3.16 (k+1)^2.11 for k = 2..10 on the quartic-sum test (p. 311).
5. The method uses no gradients and no quadratic-form assumptions; it converges even when the initial simplex straddles two or more valleys, unlike Powell's method (Discussion, p. 311).
6. Expected weakness: near a minimum where the Hessian is stable, quadratic-form methods may do better; false convergence can occur on surfaces with long curved valleys with steep sides (Discussion, p. 311).
7. Computationally compact: fewer than 350 instructions on the Orion computer, mostly additions/subtractions and logical orders (p. 312).

## Limitations
- 1965 study: three (plus one scaling) low-dimensional test functions; no statistical replication framework; step-length/orientation sensitivity is acknowledged and tabulated rather than removed.
- No convergence theory is given; the paper itself notes false-convergence hazards (p. 311).
- Local source is an image-only scan: text-quote verification is not possible; all locators are from visual reading, and the PDF page order is shuffled (PDF p4 = journal p312, PDF p5 = journal p311). An OCR or text-native copy is recommended before heavy citation use (also noted in reference_inventory.csv).

## Exact usable locators (bibkey, journal page)
- Method definition; reflection/expansion/contraction formulas and coefficients α, β, γ: (nelder1965simplex, p. 308).
- Flow diagram of the complete method: (nelder1965simplex, Fig. 1, p. 309).
- Stopping criterion based on function-value standard error: (nelder1965simplex, pp. 308–309).
- Standard strategy α=1, β=1/2, γ=2 identified as best: (nelder1965simplex, p. 310).
- Evaluation counts and comparison with Powell (1964): (nelder1965simplex, pp. 310–311, Tables 1–3 on pp. 310–312).
- N ≈ 3.16(k+1)^2.11 scaling with number of variables: (nelder1965simplex, p. 311).
- Derivative-free character; opportunist method, no surface assumptions except continuity; valley-straddling robustness: (nelder1965simplex, Discussion, p. 311).
- Hessian/variance–covariance estimation at the minimum: (nelder1965simplex, Appendix, pp. 312–313).

## Supported uses in the DT-GSK manuscript
- Citing the original definition of the Nelder–Mead downhill simplex method (reflection/expansion/contraction/shrink and the standard coefficients) wherever DT-GSK's local-search component derives from or is compared to Nelder–Mead.
- Citing it as a derivative-free direct-search local method that adapts to the local landscape, with known weaknesses (possible false convergence; no convergence guarantees).
- Pair with gao2012implementing (per Appendix B.6) for modern implementation details; do not use nelder1965simplex alone for implementation-level parameter claims of modern NM variants.

## Unsupported / prohibited overextensions
- Do NOT cite this paper for convergence guarantees of Nelder–Mead (none are given; later literature documents failure cases).
- Do NOT cite it for performance claims on modern benchmark suites or in high dimensions (tests are 2–10 variables, three classical functions).
- Do NOT attribute adaptive/restart variants of NM to this paper.
- Avoid verbatim quotations: the local copy is an image-only scan, so quotes cannot be checksum-verified against extractable text.

## Role in DT-GSK framing (Appendix B.6)
"Nelder–Mead" origin citation (together with gao2012implementing) in the local-search and landscape subsection — sanctioned as the primary-source definition of the simplex local search used/discussed in DT-GSK. Not a benchmark or statistics source; not a metaheuristic-taxonomy source.
