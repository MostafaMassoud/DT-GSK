# Evidence card — guo2015eig

## Verified bibliographic identity
- Title: Enhancing Differential Evolution Utilizing Eigenvector-Based Crossover Operator
- Authors: Shu-Mei Guo; Chin-Chang Yang (National Cheng Kung University, Tainan)
- Venue/year: IEEE Transactions on Evolutionary Computation, 19(1):31–49, February 2015
- DOI: 10.1109/TEVC.2013.2297160 (printed on p. 31)
- Local file: `reference_papers/guo2015eig.pdf` (19 pp.; PDF p. 1 = printed p. 31; printed page = PDF page + 30)
- Inventory status: identity `verified`, readable, admissible. SHA-256 `30a1d86f1b3fee3bdb95f9a6b7be412132ce13f44316a42dd4ca144eab541489`.
- Locator convention: printed journal pages (31–49).
- Extraction caveat: the numeric cell contents of results Tables I–VI did not extract as text from the local PDF (captions extract; the paper itself notes the tables "can be accessed in IEEE Xplore", p. 37). All quantitative claims below are taken from the running prose, which reports the aggregate counts; claims requiring per-function numeric error values should not be made from this local copy.

## Research question and context
Can DE's binomial crossover be made rotationally invariant — without losing its diversity-preserving, dimension-wise behavior — by executing the crossover in the eigenvector basis of the population covariance matrix, and does this improve DE and state-of-the-art DE variants on rotated, ill-conditioned landscapes? (Abstract, p. 31.)

Context: binomial and exponential crossover are not rotationally invariant; DE performance with them is sensitive to coordinate rotation, especially on functions with high conditioning; pure arithmetic (rotationally invariant) recombination such as DE/rand/1/Either-Or can lose diversity and converge prematurely (Sec. I, p. 31). Sec. III (pp. 33–34) demonstrates both effects empirically (Figs. 1–5): with CR = 1 binomial crossover is rotationally invariant; with CR < 1 it is not; the rotationally invariant Either-Or follows valley lines but can stall on the attractive sector function.

## Method
- Compute the population covariance matrix C_G (Eqs. 12–13, p. 35) and its eigendecomposition C_G = Q_G Lambda_G Q_G^-1 (Eq. 14, p. 35), solved with the Jacobi eigenvalue method.
- Eigenvector-based crossover: express target and donor vectors in the eigenvector basis, apply any existing crossover there, then rotate back: u = Q* · xover(Q·x, Q·v) (Eq. 15, p. 36). This makes the crossover behavior rotationally invariant in the natural basis; the landscape becomes "pseudo-separable" in the rotated frame (Secs. III–IV, pp. 34–36; Fig. 6, p. 37; Fig. 7 shows the learned basis matching the 45-degree rotation, p. 37).
- Eigenvector ratio P: to preserve diversity, each trial vector is generated with the eigenvector-based crossover with probability P, otherwise with the original crossover (Eq. 16, p. 36). P near 0 = original operator; P near 1 = pure rotationally invariant behavior with premature-convergence risk (Sec. V-C, pp. 43–44).
- The operator is generic: applied to DE/rand/1, DE/best/1 and to six state-of-the-art variants — DCMA-EA, drift-free DE (DFDE, with a binomial crossover inserted), DEGL, rank-based RBDE, SaDE, JADE (with archive) (Sec. V-B, p. 38).
- Explicit debt to CMA-ES: the adaptation concept is taken from CMA-ES's covariance-based landscape adaptation (Sec. IV, p. 35, citing Hansen et al.).

## Experimental scope
- Suites: BBOB 2012 (24 noise-free functions, 5 classes; instance number fixed to 1) and CEC 2013 (28 functions, 3 classes) at D = 30 and D = 50; plus two CEC 2011 real-world problems (rf1 = FM sound-wave parameter estimation, CEC2011 Problem 1; rf2 = spread-spectrum radar polyphase code design, CEC2011 Problem 7) — 54 functions total at 50-D (Sec. V, pp. 36–38; abstract p. 31).
- Protocol: solution error f(x') − f(x*) after 10^4·D FEs; 50 independent runs; Wilcoxon rank-sum at 5% with +/−/= marking (Sec. V-A, pp. 37–38). Baseline DE settings: F = 0.7, CR = 0.5, P = 50%, NP = 5·D.
- P-ratio study over P ∈ {10%,…,90%} using a positive-minus-negative (P-N) count (Sec. V-C, pp. 43–45; Figs. 9–10).
- Overhead measurement and complexity (Sec. V-D, pp. 45–47); overall ECDF-of-normalized-mean-error comparison (Sec. V-E, p. 47; Fig. 11).
- Source code released at github.com/DE-EIG/DE-EIG (p. 37).

## Conservative findings (with locators)
1. For basic DE (30-D): the eigenvector-based crossover significantly improves both DE/best/1 and DE/rand/1, with substantial gains on unimodal functions of low/moderate (bf6–bf9) and high conditioning (bf10–bf14); DE/best/1/eig is significantly better or equal on 46 of 52 functions; degradations concentrate on a few separable multimodal functions (bf3, bf4, cf11, cf14, cf17) and cf22 (Sec. V-A, pp. 38–39; Table I, p. 39).
2. At 50-D the pattern persists and the number of significant improvements increases (e.g., DE/best/1: 25 of 54 functions significantly improved vs 18 of 52 at 30-D); improvements on the two CEC 2011 real-world problems are NOT statistically significant (Sec. V-A, p. 38; Table II, p. 40).
3. For state-of-the-art variants (30-D; Tables III–IV, pp. 41–42): DCMA-EA/eig significantly better on 15/52, never significantly worse; DFDE/eig similar-or-better on 45/52; DEGL/eig significantly better on 14, worse on 6; RBDE/eig similar-or-better on 45/52; SaDE/eig similar-or-better on 44/52; JADE/eig similar-or-better on 46/52 with JADE better on 6 (mostly separable multimodal). "The proposed eigenvector-based crossover barely decreases the performance of the efficient self-adaptive algorithms, such as SaDE and JADE" (p. 42).
4. Eigenvector ratio: the best overall value is P = 50% (overall P-N value 112, marginally above 111 at P = 70%); any P in 30%–80% gives overall P-N > 100; the optimal P is algorithm-dependent (e.g., 70% for JADE, 20% for SaDE/DEGL) (Sec. V-C, pp. 44–45; Figs. 9–10).
5. Overhead: time complexity O(D^2·NP·Gmax + D^3·Gmax), i.e., O(D^3·Gmax) with NP = 5D; measured mean overhead ratios ~5.30e-02 (BBOB 2012) and ~7.58e-04 (CEC 2013) of function-call time — at most ~5.3% (Sec. V-D, pp. 45–47).
6. Overall: the ECDF of normalized mean errors of the Eigen variants is almost always above the original DEs across BBOB 2012 + CEC 2013 + the two real-world problems (Sec. V-E, p. 47; Fig. 11).
7. Conclusions (pp. 47–48): significant improvement especially on non-separable unimodal functions with high conditioning; performance rarely worsened on multimodal functions; self-adaptive parameter mechanism for P left to future work.

## Limitations
- Per-function numeric tables not extractable from the local PDF (see caveat above) — quantitative citations must stay at the prose/count level.
- Fixed baseline parameters (F = 0.7, CR = 0.5, NP = 5D); single BBOB instance (instance 1); D = 30, 50 only.
- Gains are landscape-dependent: separable multimodal functions can be significantly degraded (e.g., bf3, bf4, cf14, cf17, cf22 recur as losses across variants).
- Real-world CEC 2011 problems (rf1, rf2): no significant differences (p. 38, p. 41).
- P must be chosen; the paper offers only empirical guidance (best overall 50%).

## Exact usable locators (claim → locator)
- Non-invariance of binomial/exponential crossover; CR = 1 invariance: Sec. I p. 31 and Sec. III p. 33.
- Covariance matrix and eigendecomposition of the population: Eqs. (12)–(14), p. 35.
- Eigen crossover definition (rotate, crossover, rotate back): Eq. (15), p. 36.
- Stochastic mixing with eigenvector ratio P: Eq. (16), p. 36.
- CMA-ES-inspired adaptation concept: Sec. IV, p. 35.
- Benchmarks/protocol (BBOB 2012 + CEC 2013 + 2 CEC 2011 problems, 50 runs, 10^4·D FEs, Wilcoxon 5%): Secs. V and V-A, pp. 36–38.
- Basic-DE results (30-D / 50-D): pp. 38–39 / p. 38 with Tables I–II (pp. 39–40).
- Six-variant results incl. JADE/eig and SaDE/eig counts: pp. 38–43; Tables III–VI (pp. 41–44).
- P = 50% recommendation and P-N analysis: pp. 44–45; Figs. 9–10 (pp. 46–47).
- O(D^3) complexity and <=5.3% overhead: Sec. V-D, pp. 45–47.
- ECDF overall superiority: Sec. V-E, p. 47, Fig. 11.

## Supported uses in the DT-GSK manuscript
- Citing eigenvector-based crossover as the representative structure-aware (rotationally invariant) crossover line in DE — the comparison point named in Appendix B.3 for DT-GSK's operator design discussion.
- Supporting claims that coordinate-wise (binomial-style) recombination is rotation-sensitive and that covariance-eigenbasis rotation restores invariance at modest (<~5%) runtime overhead, with the largest gains on non-separable, high-conditioning unimodal landscapes and occasional losses on separable multimodal ones.
- Precedent that a structural operator can be grafted onto adaptive DE variants (JADE, SaDE) without harming them on average.

## Unsupported / prohibited overextensions
- Do NOT cite per-function numeric error values from this local copy (tables did not extract; use prose counts only).
- Do NOT claim universal improvement — separable multimodal functions show significant degradation in several cases, and CEC 2011 real-world gains were not significant.
- Do NOT present this as a full CEC 2011 evaluation: only two CEC 2011 problems (rf1, rf2) are used.
- Do NOT attribute covariance *matrix adaptation* to this paper — it computes the covariance of the current population per generation (no cumulative adaptation); CMA-ES claims belong to hansen2001cmaes.
- Not evidence about GSK operators, population-size reduction, or competition rankings.

## Role in DT-GSK framing (Appendix B.3)
`guo2015eig` — eigenvector crossover comparison: the structure-aware DE operator against which DT-GSK's (non-rotational, knowledge-sharing) operator choices are contrasted; also a bridge citation between the DE lineage and covariance-based structure exploitation.

## Verification quotation (identity)
"Enhancing Differential Evolution Utilizing Eigenvector-Based Crossover Operator — Shu-Mei Guo, Member, IEEE, and Chin-Chang Yang" with header "IEEE TRANSACTIONS ON EVOLUTIONARY COMPUTATION, VOL. 19, NO. 1, FEBRUARY 2015 31" and "Digital Object Identifier 10.1109/TEVC.2013.2297160" (p. 31).
