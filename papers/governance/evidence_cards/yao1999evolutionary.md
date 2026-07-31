# Evidence card — yao1999evolutionary

## Verified bibliographic identity
- Title: Evolutionary Programming Made Faster
- Authors: Xin Yao, Yong Liu, Guangming Lin
- Venue: IEEE Transactions on Evolutionary Computation, vol. 3, no. 2, July 1999, pp. 82–102
- DOI (bib): 10.1109/4235.771163
- Local source: `reference_papers/yao1999evolutionary.pdf` (21 pp., published journal layout; PDF page n = journal page 81+n)
- Identity status: verified; readable. Note: inline mathematical symbols (function names f1–f23, parameter values) are partially lost in text extraction; all claims below were verified against surrounding running text.

## Research question and context
Why does classical evolutionary programming (CEP) with self-adaptive Gaussian mutation converge slowly on some multimodal function-optimization problems, and can replacing Gaussian mutation with a heavier-tailed Cauchy mutation ("fast EP", FEP) improve it? When exactly do longer mutation jumps help or hurt? (Abstract, p. 82; Sec. I, p. 82.)

## Method
- CEP: self-adaptive Gaussian-mutation EP following Bäck & Schwefel; each individual is a pair of real vectors (objective variables + self-adaptive standard deviations); offspring via Eqs. (1)–(2); pairwise tournament selection over parents+offspring (Sec. II, pp. 82–83).
- FEP: identical to CEP except Eq. (1) is replaced by Eq. (4), which uses a Cauchy random variate with scale parameter t = 1; the Cauchy density is Eq. (3); its variance is infinite and its long flat tails give a higher probability of long jumps (Sec. III, p. 83, and Fig. 1, p. 84).
- Analytical part: probability that Cauchy mutation generates a longer jump than Gaussian is estimated at 0.68; expected jump length of Gaussian is finite while the Cauchy expectation "does not exist" (Sec. VII, pp. 89–90). Derivations (Eqs. (5)–(9), pp. 90–91) show a large step size increases the probability of reaching a near-optimum only when the distance to the optimum exceeds the step size; otherwise it decreases it.
- IFEP (improved FEP): each parent generates two offspring, one by Cauchy and one by Gaussian mutation, and the better one is kept — mixing (not switching) search biases, no new parameters (Sec. VIII, p. 95).

## Experimental scope
- 23 benchmark functions (Table I, p. 84): f1–f7 unimodal (incl. step and noisy quartic), f8–f13 multimodal with many local minima (dimension set to 30), f14–f23 low-dimensional multimodal with few local minima (Sec. IV, p. 84).
- 50 independent runs per function for all comparisons (Tables II–V, pp. 85–89). Population size 100 (stated explicitly on p. 91 in the search-space-scaling experiment). Same self-adaptation, population size, tournament size, initial parameters for CEP and FEP (Sec. V-A, p. 84).
- Scale-parameter study of Cauchy t on 7 functions (Sec. VI, p. 89, Table VI); initialization-range/search-space-scaling experiments on f21 (Sec. VII-B, pp. 91–92, Tables VII–VIII); IFEP tested on representative functions f1, f2, f10, f11, f21–f23 (Table X, p. 95).

## Conservative findings
1. FEP (Cauchy) performs significantly better than CEP (Gaussian) on multimodal functions with many local minima (f8–f13, D=30), and comparably on unimodal and few-minima multimodal functions; CEP retains an edge in fine-grained local search (e.g., final results on f1, f2) (Abstract, p. 82; Sec. V-B, pp. 84–85; Sec. V-C1, p. 87, Table III).
2. Largest FEP advantage occurs on the step function f6 (plateaus/discontinuity), attributed to long jumps moving across plateaus (Sec. V-B, pp. 85–87).
3. Low dimensionality is not the deciding factor; function shape / number of local minima drives the FEP-vs-CEP difference (Sec. V-C2, pp. 88–89, Table V).
4. Analytically, Cauchy mutation's benefit comes from a higher long-jump probability (P ≈ 0.68 of exceeding a Gaussian jump); long jumps help only when the current point is far from the optimum and hurt when it is close (Sec. VII, pp. 89–91, Eqs. (6)–(9)).
5. Empirically, shrinking the initialization range near the optimum favors CEP; expanding the search space 10x/100x/1000x removes CEP's advantage and eventually reverses it (Sec. VII-B, pp. 91–92, Tables VII–VIII).
6. The optimal Cauchy scale parameter t is problem-dependent (t = 1 not optimal everywhere); self-adaptation or mixing operators is suggested (Sec. VI, p. 89, Table VI).
7. IFEP (mixing Cauchy + Gaussian offspring, choosing the better) performs as well as or better than the better of FEP/CEP on most tested functions, with half the population size and no added parameters (Sec. VIII, pp. 95–97, Table X; Conclusion, p. 99). The number of successful Cauchy mutations decreases over generations as the population nears the optimum (Figs. 12–14, pp. 98–99).

## Limitations
- 1999-era EP setting: fixed benchmark suite of 23 classical functions (not CEC-style shifted/rotated suites); population 100; 50 runs; results are means without modern nonparametric multiple-comparison corrections (t-tests are used where significance is claimed).
- FEP parameters copied from CEP without tuning (Sec. I, p. 82); scale-parameter study limited to 7 functions.
- Analytical results are for idealized one-dimensional neighborhood models (Sec. VII, pp. 89–91), not convergence proofs for the full algorithm.

## Exact usable locators (bibkey, page-or-section)
- Cauchy density definition, infinite variance, FEP update rule: (yao1999evolutionary, Sec. III, p. 83, Eqs. (3)–(4)).
- Long flat tails → higher escape probability from local optima/plateaus; weaker fine-tuning: (yao1999evolutionary, Sec. III, p. 83; Fig. 1, p. 84).
- 23-function suite composition and rationale (incl. NFL-motivated breadth): (yao1999evolutionary, Sec. IV, p. 84, Table I).
- FEP >> CEP on many-minima multimodal f8–f13 (D=30), 50 runs: (yao1999evolutionary, Sec. V-C1, p. 87, Table III).
- P(Cauchy jump > Gaussian jump) ≈ 0.68; expected Cauchy jump length does not exist: (yao1999evolutionary, Sec. VII, p. 90).
- Large steps help only when distance-to-optimum > step size: (yao1999evolutionary, Sec. VII-A, pp. 90–91, Eqs. (6)–(9)).
- Empirical reversal with initialization/search-space scaling on f21: (yao1999evolutionary, Sec. VII-B, pp. 91–92, Tables VII–VIII).
- IFEP mixing design and results: (yao1999evolutionary, Sec. VIII, p. 95, Table X; discussion pp. 95–97).
- Conclusion summary: (yao1999evolutionary, Sec. IX, p. 99).

## Supported uses in the DT-GSK manuscript
- Citing the established principle that heavy-tailed (Cauchy) mutation increases long-jump probability and helps escape local optima/plateaus when the search point is far from the optimum — as design grounding for any Cauchy/heavy-tailed exploration component (e.g., BSE) in DT-GSK.
- Citing the counterpart caveat: large mutation steps reduce the probability of improvement near the optimum (supports staged/gated use of heavy-tailed moves).
- Citing operator mixing (Cauchy + Gaussian) as a precedent for combining complementary search biases without switching logic or extra parameters.
- Historical/taxonomic positioning of FEP/IFEP in the EP lineage.

## Unsupported / prohibited overextensions
- Do NOT claim FEP/IFEP superiority on CEC2011/CEC2013/CEC2017 suites — the paper predates them and used 23 classical functions.
- Do NOT claim Cauchy mutation is universally better than Gaussian; the paper explicitly shows the reverse near optima and on some few-minima functions (f21–f23, Table IV, p. 87).
- Do NOT cite the 0.68 probability or the step-size analysis as a proof about DT-GSK's specific operator; it is an idealized one-dimensional argument for EP mutations.
- Do NOT attribute self-adaptive scale control of the Cauchy parameter to this paper as an implemented result — it is only suggested as future direction (Sec. VI, p. 89).

## Role in DT-GSK framing (Appendix B.5)
"Cauchy-mutation basis when relevant to BSE" — the sanctioned citation role is as the literature basis for Cauchy/heavy-tailed mutation behavior (long-jump probability, escape from local optima, far-vs-near optimum trade-off) where the manuscript discusses the BSE (heavy-tailed exploration) subsystem. Not a family baseline, not a benchmark-protocol source, not a statistics source.
