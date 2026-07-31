# Evidence card — omidvar2014dg

## Verified bibliographic identity
- Title: Cooperative Co-evolution with Differential Grouping for Large Scale Optimization
- Authors: Mohammad Nabi Omidvar; Xiaodong Li; Yi Mei; Xin Yao
- Venue: IEEE Transactions on Evolutionary Computation. Bib cites the final 2014 publication (TEVC 18(3):378–393); DOI 10.1109/TEVC.2013.2281543.
- Local file: `reference_papers/omidvar2014dg.pdf` (16 pp.) — AUTHOR-ACCEPTED MANUSCRIPT: header reads "This article has been accepted for publication ... has not been fully edited", "(c) 2013 IEEE", "VOL. X, NO. X". Final 2014 pagination (378–393) is NOT shown.
- Inventory status: identity `verified`, readable, admissible, with the explicit condition that locators use the local manuscript pagination (pp. 1–16). SHA-256 `efb15b9bf91d257aa09e856946abc98c8a3a8eac89d87d9aa13756474e93686d`.
- Locator convention in this card: manuscript pages 1–16 as printed in the running header of the local file.

## Research question and context
Can the interaction structure of decision variables be uncovered automatically — with a theoretically grounded test — so a cooperative co-evolution (CC) framework can decompose a large-scale problem into subcomponents with minimal interdependence, and does near-optimal decomposition improve large-scale optimization and enable contribution-based budget allocation? (Abstract and Sec. I, pp. 1–2.)

Context: Sec. II (pp. 2–4) surveys separability/epistasis definitions (Definition 1, separable iff dimension-wise argmin works, p. 2), CC decomposition strategies (Potter & De Jong 1-D decomposition; CPSO; random grouping; delta grouping; MLCC), and the four-way classification of linkage-learning methods (random / perturbation / interaction adaptation / model building; differential grouping is a perturbation method, p. 3).

## Method
- Definition 2 (p. 4): partially additively separable functions f(x) = sum_i f_i(x_i) with mutually exclusive decision vectors.
- Theorem 1 (p. 4): for additively separable f, if the forward difference Delta_{delta,x_p}[f] evaluated at two different values of x_q differs, then x_p and x_q are non-separable (interact). Proof via Lemma 1 (partial derivative belongs only to the containing component), pp. 4–5; worked quadratic example with interaction strength lambda, p. 5.
- Algorithm 1 "differential grouping" (p. 5): pairwise interaction check per Theorem 1 using points built from the lower bound, upper bound, and middle of the domain; threshold epsilon on |Delta1 − Delta2|; interacting variables are extracted into a subcomponent; all separable variables pooled into one group. Choice of the probe points is arbitrary (p. 5).
- Shows LINC-R's heuristic is derivable from Theorem 1 (pp. 5–6).
- Complexity (Sec. III-B, p. 6): total FEs ~ 2(S + n/m) with S = n(n+m−2)/(2m); O(n^2/m). Examples at n = 1000: m = 50 → 21,000 FEs; fully separable (m = 1) → 1,001,000 FEs.
- CC framework (Algorithm 2, p. 6): off-line grouping stage then round-robin subcomponent optimization; also combined with Contribution-Based CC (CBCC1/CBCC2, ref. [15]) which allocates budget by subcomponent contribution (Sec. III-C, p. 6; Sec. V-E, pp. 12–13).

## Experimental scope
- CEC'2010 large-scale global optimization suite: 20 functions in 5 classes (fully separable f1–f3; single-group 50-nonseparable f4–f8; 10-group f9–f13; 20-group f14–f18; fully non-separable f19–f20); n = 1000, m = 50 (Sec. IV, pp. 6–7).
- Subcomponent optimizer SaNSDE, population 50; 25 independent runs; MaxFES = 3 x 10^6; epsilon = 10^-3 (also 10^-1, 10^-6 in sensitivity study) (Sec. IV-A, p. 7).
- Comparisons: grouping accuracy and FE cost vs CCVIL (Table I, p. 8; Sec. V-B, pp. 10–11); epsilon sensitivity (Table III, p. 8); optimization as DECC-DG vs MLCC, DECC-D, DECC-DML, DECC-I (ideal manual grouping) (Table V, p. 11; algorithm roster Table IV, p. 12); CBCC1/CBCC2-DG vs DECC-DG and vs MA-SW-Chains, the CEC'2010 competition winner (Tables VI, p. 12; VII–VIII, p. 13); imbalanced-function variants f'9–f'18 defined p. 13. Wilcoxon test at alpha = 0.05 throughout.

## Conservative findings (with locators)
1. Grouping accuracy: 100% on 13 of 20 CEC'2010 functions with epsilon = 10^-3; near-perfect on several others (f11 99.2%, f16 99.6%); poor on Rosenbrock-based instances (f8 92%, f13 25.2%, f18 17.3%, f20 8.2%) and f7 (69%) (Table I, p. 8; Sec. V-A, pp. 7–9). Grouping-matrix detail: Table II, p. 9.
2. Cost pattern: FE cost of grouping is lowest for fully non-separable f19 (2,000 FEs) and highest for fully separable f1–f3 (~1,001,000 FEs, ~n(n+1)), matching the O(n^2/m) analysis (Table I, p. 8; Sec. V-A, pp. 8–10; Sec. III-B, p. 6).
3. vs CCVIL: differential grouping is more accurate with considerably fewer FEs on most functions (exceptions f1, f2, f7); CCVIL classified all Rosenbrock variants as fully separable (0%) (Table I, p. 8; Sec. V-B, pp. 10–11). Mechanism: DG compares fitness differences (gradient-like), CCVIL needs an existential search for fitness-order flips (Fig. 1, p. 11).
4. Epsilon sensitivity (Sec. V-C, pp. 10–11; Table III, p. 8): performance is not very sensitive as long as epsilon is small; larger epsilon (10^-1) classifies separable variables better, smaller (10^-3) detects interactions better; too small (10^-6) misclassifies separable variables as interacting (e.g., f9 accuracy drops 100% → 25.6%).
5. Optimization: DECC-DG outperformed MLCC, DECC-D, DECC-DML overall on CEC'2010 (Table V, p. 11; Sec. V-D, pp. 11–12); grouping cost is compensated during optimization (convergence plots Fig. 2, p. 14). DECC-DML remains better on fully separable functions.
6. CBCC: both CBCC1-DG and CBCC2-DG outperform round-robin DECC-DG on the imbalanced class f4–f8, and by a wider margin on the artificially imbalanced f'9–f'18 (Tables VI, p. 12; VII, p. 13; Secs. V-E–V-F, pp. 12–13).
7. vs MA-SW-Chains (CEC'2010 winner): MA-SW-Chains better on 15/20 standard functions, but on 9 imbalanced multimodal functions CBCC-DG won 6, tied 2, lost 1; the authors argue memetic local search wins short-term while CC+DG improves steadily (Table VI, p. 12; Table VIII, pp. 13–14; Fig. 3 discussion, p. 14).
8. Known failure mode: DG may miss interactions when the sampled region of the space is separable although other regions are not (p. 11); Rosenbrock's overlapping-chain structure defeats the grouping (pp. 8–9, behavior noted "beyond the scope of the current study").

## Limitations
- Accepted-manuscript copy: final journal pagination/edits not verifiable locally; cite content by manuscript page + section/table/theorem number.
- Requires additively separable structure for the theory; interactions detected pointwise can miss region-dependent separability (p. 11).
- Grouping cost is heavy for (nearly) fully separable problems (~n^2 FEs) and epsilon needs a scale-appropriate choice (Sec. V-C).
- Evidence is n = 1000, m = 50 CEC'2010-specific; subcomponent optimizer fixed (SaNSDE); 25 runs.

## Exact usable locators (claim → locator)
- Separability definition: Definition 1, p. 2. Partial additive separability: Definition 2, p. 4.
- Interaction criterion: Theorem 1 + Eq. (4), p. 4; proof pp. 4–5.
- Differential grouping algorithm and epsilon: Algorithm 1, p. 5.
- LINC-R equivalence: pp. 5–6.
- FE complexity O(n^2/m) with worked examples: Sec. III-B, p. 6, Eq. (15).
- CC framework and CBCC linkage: Algorithm 2 and Sec. III-C, p. 6.
- Benchmark classes and settings (n=1000, m=50, 25 runs, 3e6 FES, SaNSDE): Secs. IV–IV-A, pp. 6–7.
- Grouping accuracy table incl. CCVIL comparison: Table I, p. 8. Epsilon study: Table III, p. 8.
- DECC-DG vs other decompositions: Table V, p. 11; Table IV roster, p. 12.
- CBCC vs DECC-DG vs MA-SW-Chains: Table VI, p. 12; imbalanced results Table VII and wins/losses Table VIII, p. 13.
- Conclusion: Sec. VI, p. 14.

## Supported uses in the DT-GSK manuscript
- Citing differential grouping as the theoretically grounded automatic decomposition method for large-scale optimization (per Appendix B.3: decomposition comparison / future-work citation).
- Supporting statements that (a) variable-interaction structure can be discovered from forward-difference tests at O(n^2/m) evaluation cost, (b) near-optimal decomposition materially improves CC optimization, and (c) contribution-based budget allocation across subcomponents beats round-robin under imbalance.
- Future-work framing for DT-GSK: decomposition/grouping as a potential extension direction for high-dimensional GSK-family scaling — cite with its stated failure modes (Rosenbrock-type overlap; region-dependent separability).

## Unsupported / prohibited overextensions
- Do NOT cite final-journal page numbers (378–393) as verified — the local copy is the accepted manuscript without them.
- Do NOT claim DG achieves perfect decomposition generally — it fails on Rosenbrock-structured and locally separable landscapes (Table I; p. 11).
- Do NOT claim DECC-DG beats memetic state of the art overall — MA-SW-Chains won 15/20 standard CEC'2010 functions (Table VI).
- Not evidence about CEC2017/CEC2011 suites, about DE parameter adaptation, or about GSK operators.
- Later improvements (DG2, RDG, etc.) are outside this source; do not attribute them here.

## Role in DT-GSK framing (Appendix B.3)
`omidvar2014dg` — differential grouping and decomposition comparison / future work: anchors the structure-aware decomposition line (cooperative co-evolution) against which DT-GSK's non-decompositional design is positioned, and supplies the standard citation for automatic variable-interaction detection in future-work text.

## Verification quotation (identity)
"Cooperative Co-evolution with Differential Grouping for Large Scale Optimization — Mohammad Nabi Omidvar, Student Member, IEEE, Xiaodong Li, Senior Member, IEEE, Yi Mei, Member, IEEE, and Xin Yao, Fellow, IEEE" (manuscript p. 1, with IEEE accepted-for-publication header).
