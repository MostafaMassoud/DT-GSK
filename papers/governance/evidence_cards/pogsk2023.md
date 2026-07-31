# Evidence card: pogsk2023

## Verified bibliographic identity
- Title: "A New Gaining-Sharing Knowledge Based Algorithm with Parallel Opposition-Based Learning for Internet of Vehicles"
- Authors: Jeng-Shyang Pan, Li-Fa Liu, Shu-Chuan Chu, Pei-Cheng Song, Geng-Geng Liu
- Venue: Mathematics 2023, 11, 2953 (MDPI); DOI 10.3390/math11132953 (printed p. 1)
- Identity status (reference_inventory.csv): **verified**; 25-page PDF, local PDF page = printed page 1–25.

## Research question and context
GSK converges well but "there is room for improvement in avoiding locally optimal solutions and convergence speed" (Sect. 1, p. 2). Can a multi-population (parallel) scheme with Taguchi-orthogonal-array inter-group communication plus opposition-based learning (OBL) improve GSK, and does the improved algorithm solve a resource-scheduling model for the Internet of Vehicles (IoV)? (Abstract, p. 1; contributions, pp. 3–4).

## Method
POGSK = GSK + parallel groups + two communication strategies + OBL (Sect. 3, pp. 8–11; overview Fig. 1, p. 10; flowchart Fig. 2, p. 12; pseudocode Algorithm 4, p. 11):
1. **Parallel/multi-population**: initial population split into G = 4 groups searching independently (Sect. 3.1, p. 9; Algorithm 4, p. 11).
2. **Taguchi communication** (probability controlled by factor R): pairs of groups take their two best solutions as a 2-level orthogonal-array experiment (L8(2^7) example Eq. (3), p. 6; worked example Tables 1–2, p. 9; L12(2^11) used for 10D, L32(2^31) for 30D, p. 6); per-dimension level with better cumulative fitness is combined into a new individual (Sect. 3.1 steps 1–2, p. 8).
3. **Population-merger communication**: because subpopulations weaken GSK ("the search performance of the original GSK algorithm was significantly reduced when the algorithm was divided into several subpopulations", Sect. 3.1, p. 9), groups merge 4 -> 2 -> 1 at staged evaluation-count conditions (Sect. 3.1, p. 9; Algorithm 4, p. 11).
4. **OBL**: opposite population at initialization (Eq. (10), p. 10, keep fittest of {x, x_op}) and jump-rate-r-triggered dynamic opposite population during the run using current per-dimension min/max bounds (Eq. (11), p. 10; Definitions 1–2 and dynamic form Eqs. (4)–(8), p. 7).
- GSK restated with junior/senior pseudocode (Algorithms 1–3, pp. 5–6; dimension equations Eqs. (1)–(2), p. 4).
- POGSK parameters: G = 4, R = 0.5, L = 1 (communication every generation), r = 0.1, kf = 0.5, kr = 0.9, K = 1 (Table 3, p. 15).
- **IoV resource-scheduling model** (Sect. 3.3, pp. 11–14): n tasks to m processing nodes; fitness = a·FT + b/FU + c·FN + d/FS combining total service delay FT (Eqs. (14)–(17)), resource utilization FU (Eq. (18)), load-balance variance FN (Eqs. (20)–(23)), and on-time-completion security rate FS (Eqs. (24)–(26)); capacity constraints Eq. (28) with repair procedure (Sect. 4.2, p. 20).

## Experimental scope
- **CEC2017** (29 functions, F2 dropped), 10D and 30D; NFES = 10,000·D (fairness note: Taguchi adds fitness calls, so termination is by evaluations, Sect. 4.1, p. 14); population 100; 31 independent runs; comparators GSK, DE, PSO, GWO (parameters Table 3, p. 15). Additional budget-sensitivity experiments at 0.1/0.3/0.5·Max NFES (Tables 8–9, pp. 19–20).
- **IoV simulation**: 10 processing units, 30 tasks, 11 random scenarios, 300,000 evaluations, population 100, 20 runs each; comparators GSK, PSO, GWO (Sect. 4.2, pp. 20–21; scenario parameters Table 10, p. 22).
- Win/lose counts reported; **no significance tests** (no Wilcoxon/Friedman) anywhere.

## Conservative findings
- CEC2017 10D (31 runs, mean error): POGSK better than GSK on 26 of 29 functions (5 at optimum), better than DE on 23, GWO on 25, PSO on 25 (Sect. 4.1, p. 15; Tables 4–5, pp. 15–16, win/lose rows).
- CEC2017 30D: better than GSK on 20 of 29, DE on 26, GWO on 28, PSO on 25 (Sect. 4.1, p. 17; Tables 6–7, pp. 17–18).
- Notably strong on composition functions F21–F30 (9 of 10 better at 10D, 7 at 30D; pp. 15, 17).
- Reduced-budget behavior: POGSK still leads GSK at 0.1/0.3/0.5·Max NFES (25/24/23 wins) but beats PSO on only 18 functions at 0.1·Max NFES — authors attribute this to POGSK's capability not being fully utilized at small budgets (Sect. 4.1, p. 18; Tables 8–9, pp. 19–20).
- IoV scheduling (20 runs, 11 scenarios): POGSK best mean fitness in 9 of 11 scenarios vs GSK, 9 vs PSO, 11 vs GWO (Sect. 4.2, pp. 20–21; Table 11, pp. 23; win/lose rows).
- Convergence curves (Figs. 4–5, pp. 21–22) show mid/late-run escape from local optima credited to OBL + parallel strategy (p. 18).

## Limitations (author-stated and observed)
- No statistical hypothesis testing; only mean/std and win-loss counts over 31 runs (CEC2017) and 20 runs (IoV).
- Only 10D and 30D; only 4 comparators, all classical (GSK, DE, PSO, GWO) — no CEC-winner baselines, no other GSK variants.
- Author-acknowledged: subpopulation splitting degrades plain GSK, requiring the merger strategy as a fix (p. 9); performance advantage shrinks at low evaluation budgets vs PSO (p. 18).
- Taguchi communication consumes extra fitness evaluations (acknowledged and controlled by evaluation-count termination, p. 14).
- IoV model is a simulation with randomly generated scenarios; weights a,b,c,d of the fitness function are not sensitivity-analyzed.

## Exact usable locators (claim -> locator)
| Claim the DT-GSK manuscript may need | Locator |
|---|---|
| GSK junior/senior schemes restated (pseudocode) | Algorithms 1–2, p. 5; parameters K, kf, kr, p. 5 |
| Motivation: GSK needs better local-optimum avoidance / convergence speed | Sect. 1, p. 2 |
| Parallel/multi-population + Taguchi orthogonal-array communication mechanism | Sect. 3.1, pp. 8–9; Eq. (3), p. 6; Tables 1–2, p. 9 |
| Population-merger strategy and the observation that splitting hurts GSK | Sect. 3.1, p. 9 |
| OBL initialization and jump-rate dynamic opposition | Sect. 3.2, Eqs. (10)–(11), p. 10; Defs. 1–2, p. 7 |
| POGSK full pseudocode and parameters | Algorithm 4, p. 11; Table 3, p. 15 |
| CEC2017 protocol (31 runs, NFES = 10,000·D, F2 dropped) | Sect. 4.1, pp. 14–15 |
| POGSK vs GSK win counts, 10D (26/29) and 30D (20/29) | Tables 4 and 6 win/lose rows, pp. 15, 17 |
| Composition-function strength claim | Sect. 4.1, pp. 15, 17 |
| Budget-sensitivity results | Tables 8–9, pp. 19–20; discussion p. 18 |
| IoV model fitness function and constraints | Sect. 3.3, Eqs. (12)–(28), pp. 11–14 |
| IoV results (9/11 scenarios best vs GSK/PSO; 11/11 vs GWO) | Table 11, p. 23; Sect. 4.2, pp. 20–21 |

## Supported uses in the DT-GSK manuscript
- Related-work breadth: a 2023 GSK variant combining multi-population parallelism, Taguchi-orthogonal communication, and OBL, tested on CEC2017 (10/30D) and an IoV scheduling application.
- Evidence that opposition-based learning and multi-population devices have been grafted onto GSK (mechanism locators above).
- Evidence of the observed fragility of GSK under subpopulation splitting (p. 9) — relevant if DT-GSK discusses population-structure design choices.

## Unsupported / prohibited overextensions
- Do NOT describe POGSK's wins as statistically significant — no significance tests were run.
- Do NOT generalize beyond 10D/30D CEC2017 or beyond the four classical comparators; no evidence vs modern CEC winners or other GSK variants.
- Do NOT cite the IoV study as real-world deployment evidence; it is a randomized simulation model.
- Does not discuss DT-GSK or any of its mechanisms.

## Verification quotations
- "The main idea used to improve the GSK algorithm is to divide the initial population into different groups, each searching independently and communicating according to two main strategies. Opposite-based learning is introduced to correct the direction of convergence and improve the speed of convergence." (Abstract, p. 1)
- "After testing, the search performance of the original GSK algorithm was significantly reduced when the algorithm was divided into several subpopulations." (Sect. 3.1, p. 9)
