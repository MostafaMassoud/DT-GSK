# Evidence card — storn1997differential

## 1. Verified bibliographic identity
- **Citation key:** `storn1997differential`
- **Title (on source):** "Differential Evolution — A Simple and Efficient Heuristic for Global Optimization over Continuous Spaces"
- **Authors (on source):** Rainer Storn (Siemens AG); Kenneth Price
- **Venue/year (on source):** Journal of Global Optimization 11: 341–359, 1997 (header, journal p. 341); received 20 March 1996, accepted 19 November 1996
- **Identity status (inventory):** `verified` (title match degraded only by ligature extraction artifacts).
- **Source file:** `reference_papers/storn1997differential.pdf`, 19 pages, sha256 `d8bd6c0f8030790d9d172076b57119bc94fd861bbca79c94ae6b680363239f12`
- **Locator convention:** local PDF page N = journal page 340+N (local p. 1 = journal p. 341). Cite journal pages.

## 2. Research question and context
Introduce a new stochastic direct-search heuristic — Differential Evolution (DE) — for minimizing nonlinear, non-differentiable continuous-space functions, satisfying four practical requirements: handling non-differentiable/multimodal costs, parallelizability, ease of use (few, robust control variables), and consistent convergence (pp. 342). Foundational paper of the DE lineage.

## 3. Method
- **Population and mutation** (Sec. 2, pp. 343–344): NP D-dimensional vectors per generation (NP fixed); mutant vector v_{i,G+1} = x_{r1,G} + F·(x_{r2,G} − x_{r3,G}) with mutually different random indices ≠ i, so NP ≥ 4; F ∈ [0, 2] real constant (Eq 2, p. 344).
- **Crossover** (pp. 344–345): binomial ("bin") crossover forming the trial vector, u_{ji,G+1} = v if randb(j) ≤ CR or j = rnbr(i), else x (Eqs 3–4, p. 345); CR ∈ [0,1]; rnbr(i) guarantees at least one mutant component.
- **Selection** (p. 345): greedy one-to-one replacement — trial replaces target iff it has lower cost.
- **Notation DE/x/y/z** (pp. 345–346): x ∈ {rand, best} base vector, y = number of difference vectors, z = crossover scheme; the paper's standard variant is **DE/rand/1/bin**; DE/best/2/bin (Eq 5, p. 346) noted as highly beneficial with two difference vectors.
- **Pseudocode:** 19-line C-style pseudocode, Fig 3 (p. 346).
- **Self-organizing key idea** (p. 343): DE perturbs vectors with the difference of two randomly chosen population vectors, in contrast to ESs' predetermined distributions; idea of using population information borrowed from Nelder–Mead.

## 4. Experimental scope
- **Testbed 1** (Sec. 3.1, pp. 347–351): 9 problems — modified De Jong f1–f5 plus Corana's parabola, Griewangk (D=10), Zimmermann, Chebyshev polynomial fitting (T8, T16); vs Annealed Nelder–Mead (ANM) and Adaptive Simulated Annealing (ASA); 20 runs each; success = reaching a value-to-reach (VTR) from random starts in an initial parameter range (IPR).
- **Testbed 2** (Sec. 3.2, pp. 351–353): 5 scalable functions (hyper-ellipsoid, Katsuura, Rastrigin, Griewangk, Ackley) at D up to 100; vs Breeder GA (BGA) and EASY evolution strategy using their reported results; 20 runs.
- **Testbed 3** (Sec. 3.3, pp. 353–357): 15 problems from the Stochastic Differential Equations (SDE) method literature; 1000 trial runs per function for DE.

## 5. Findings (conservative)
- **Testbed 1** (Table 1, p. 351): "DE was the only strategy that could find all global minima of the test suite"; except f1–f3, DE also needed the fewest function evaluations; for the polynomial-fitting problem DE found the optimum even though final parameters lie outside the IPR.
- **Testbed 2** (Table 2, p. 353): DE needed the least nfe in 8 of 10 cases vs BGA and EASY.
- **Testbed 3** (Table 3, p. 357): DE superior to SDE's reported best results in all test cases; none of DE's 1000 runs per function failed; settings mostly constant (NP=20, F=0.5, CR=0), indicating robustness.
- **Competition context** (p. 347): at the 1st ICEO (1996), DE "proved to be the fastest evolutionary algorithm, although it did place third in speed behind two deterministic methods of limited application."
- **Control-variable guidance** (Sec. 4, pp. 356–357): NP reasonable in [5D, 10D], NP ≥ 4; F = 0.5 a good initial choice, F < 0.4 or > 1 only occasionally effective; CR = 0.1 good first choice, CR = 0.9/1.0 to try for fast convergence.
- **Divergence property** (Conclusion, p. 358): DE's vector-difference perturbation grows population spread on flat surfaces and shrinks near a minimum via selection — the authors' explanation for its convergence behavior; a convergence proof is posed as open.

## 6. Limitations
- 1997-era testbeds and protocols (20 runs; VTR-based success; no CEC-style FES budgets or rank statistics); comparator results for BGA/EASY/SDE taken from the literature, not re-run.
- Constant F and CR (no parameter adaptation); scaling behavior explicitly declared unknown ("Little is known about DE's scaling property", p. 358).
- No theoretical convergence analysis (acknowledged, p. 358).

## 7. Usable locators (claim → locator)
| Claim | Locator |
|---|---|
| DE introduced as simple, parallel, few-control-variable direct-search heuristic | Abstract + Sec. 1, pp. 341–343 |
| Mutation v = x_r1 + F(x_r2 − x_r3); NP ≥ 4; F ∈ [0,2] | Eq 2, p. 344 |
| Binomial crossover and CR | Eqs 3–4, pp. 344–345 |
| Greedy one-to-one selection | p. 345 |
| DE/x/y/z notation; DE/rand/1/bin canonical; DE/best/2/bin (Eq 5) | pp. 345–346 |
| DE only method to solve all Testbed-1 problems; fastest on most | Table 1 + text, p. 351 |
| DE beats BGA/EASY in 8/10 cases (up to D=100) | Table 2, p. 353 |
| DE beats SDE on all 15 problems; 1000 runs, no failures | Table 3 + text, pp. 356–357 |
| Control-variable rules of thumb (NP∈[5D,10D], F=0.5, CR=0.1/0.9) | Sec. 4, pp. 356–357 |
| Divergence/self-organization property; open convergence question | Conclusion, pp. 357–358 |
| 1st ICEO: fastest evolutionary algorithm | Sec. 3, p. 347 |

## 8. Supported uses in the DT-GSK manuscript
- DE-origin citation: definition of the canonical DE population/mutation/crossover/selection cycle, the DE/x/y/z taxonomy, and the F/CR/NP control-parameter roles — the operator vocabulary GSK-style junior/senior rules and the wider variant literature build on.
- Historical anchor for statements like "difference-vector-based mutation originates with DE (Storn & Price, 1997)."
- Source for DE's classic control-parameter heuristics when contrasting fixed-parameter vs adaptive schemes.

## 9. Unsupported / prohibited overextensions
- Do NOT use its 1997 benchmark wins as evidence of DE's standing against modern algorithms or on CEC suites.
- Do NOT cite it for convergence guarantees (none proved) or for large-scale behavior (explicitly unknown per the source).
- Do NOT attribute parameter-adaptation ideas to this paper (F, CR are constants here).
- Do NOT claim GSK "is a DE variant" on this citation alone; it supports DE's definition, not GSK's genealogy.

## 10. Role in DT-GSK framing (Appendix B)
Appendix B.3 — "DE origin." Use for DE lineage/positioning of GSK-style difference-based operators and as the canonical DE reference in related work and method-lineage discussion.
