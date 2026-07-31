# Evidence card — tang2024fowfo

## Verified bibliographic identity
- Title: Fractional-Order Water Flow Optimizer
- Authors: Zhentao Tang, Kaiyu Wang, Yan Zang, Qianyu Zhu, Yuki Todo, Shangce Gao (source shows "Qianyu Zhu"; bib has "Zhu, Qian" — minor given-name truncation in bib)
- Venue: International Journal of Computational Intelligence Systems, (2024) 17:84; DOI 10.1007/s44196-024-00445-4; received 11 Dec 2023, accepted 3 Mar 2024
- Local source: `reference_papers/tang2024fowfo.pdf` (27 pp., published Springer layout; pages printed as "Page X of 27"). Locators below use "p. X of 27". Identity status: verified.

## Research question and context
Can the water flow optimizer (WFO) — a recent swarm-intelligence algorithm with laminar (exploitation) and turbulent (exploration) operators — be improved by injecting fractional-order (FO) calculus, whose Grünwald–Letnikov formulation adds memory of previous positions, and by replacing the constant laminar probability with a linearly increasing schedule? (Abstract, p. 1 of 27; Sec. 1, pp. 1–3 of 27.)

## Method (Sec. 3, pp. 5–6 of 27)
- FO laminar operator: the laminar position update is rewritten as a GL fractional difference of order ε; truncating the memory to the first e terms yields update rules that blend the current move s·d⃗ with weighted contributions of the last e positions (Eqs. (11)–(18); e = 2, 4, 8 shown explicitly; weights (1/g!)·ε(1−ε)...((g−1)−ε)).
- Memory of the last e iterations kept first-in-first-out (Sec. 3.2, p. 6 of 27).
- Laminar probability p_l (constant in WFO) is replaced by Coef = t/T_max: rand < Coef → laminar (exploitation), else turbulent (exploration); exploration-heavy early, exploitation-heavy late (Sec. 3.2, p. 6 of 27).
- Claimed advantages: rigorous mathematical derivation; FO long-term memory, non-locality, weak singularity (Sec. 3.3, p. 6 of 27).

## Experimental scope (Sec. 4, pp. 7–8 of 27)
- Suite: IEEE CEC2017, 29 functions (F2 excluded as unstable), classes: F1–F3 unimodal, F4–F10 multimodal, F11–F20 hybrid, F21–F30 composition (p. 7 of 27).
- Protocol: N = 100; bounds [−100, 100]; maxFE = 10000 × D; 51 independent runs; D = 10, 30, 50, 100; MATLAB R2021b, i7-9750H, 16 GB RAM (pp. 7–8 of 27).
- Comparators (9): WFO, FCMRFO, FOFPA, SS, SE, CSA, XPSO, TLABC, AHA — parameter settings in Table 2 (p. 8 of 27). FOWFO parameters: e = 12, ε = 0.9999999, p_e = 0.7 (Table 2).
- Statistics: Wilcoxon rank-sum (α = 0.05, W/T/L convention) and Friedman ranks on mean errors (Sec. 4.2, p. 8 of 27); box-and-whisker plots and convergence curves (Figs. 3–6).
- Real-world: four large-dimension problems — HSP (D = 96), DED (D = 120), LSTPP (D = 126), ELD (D = 140); N = 100, 51 runs (Sec. 4.4, p. 21 of 27).
- Parameter sensitivity: 18 combinations of e and ε on CEC2017 30D (Sec. 5.1, p. 21 of 27, Tables 12–13); exploration/exploitation visualization (Sec. 5.2); CPU-time comparison (Sec. 5.3, Tables 14–15, Figs. 8–9).

## Conservative findings
1. Friedman ranks (Table 3, p. 8 of 27): FOWFO ranks first at every dimension — 2.5862 (10D), 2.0345 (30D), 2.3448 (50D), 2.3103 (100D); WFO is second throughout.
2. Wilcoxon W/T/L: 10D — FOWFO beats WFO/FCMRFO/FOFPA/SS/SE/CSA/XPSO/TLABC/AHA on 15/22/29/14/24/24/21/16/18 of 29 functions (best mean count second to SS, which wins 11 vs FOWFO's 10) (p. 8 of 27, Table 4). 30D — wins on 14/27/29/22/27/23/22/17/26; best mean on 15 functions (p. 17 of 27, Table 5). 50D — wins on 8/28/29/22/25/21/20/18/28; best-mean count ranks first with 9 (pp. 17–18 of 27, Table 6). 100D — wins on 11/29/28/20/26/22/22/24/28 (p. 17 of 27, Table 7).
3. Real-world large-dimension problems: FOWFO attains the smallest Mean, Best, and Worst on all four problems (HSP, DED, LSTPP, ELD) among the ten algorithms (Sec. 4.4, p. 21 of 27, Tables 8–11).
4. Best parameter combination: e = 12, ε = 0.9999999 (Sec. 5.1, p. 21 of 27).
5. CPU time: WFO fastest; FOWFO costs more than WFO but the increase is modest; authors conclude "fractional order has little effect on algorithm complexity" (Sec. 5.3, pp. 21–22 of 27; Sec. 1 contributions, p. 3 of 27; Conclusion, p. 24 of 27).
6. Conclusion: FO technology is effective for improving WFO; FOWFO suits high-dimensional practical problems (Sec. 6, p. 24 of 27).

## Limitations
- Comparator pool is swarm/FO variants plus SS/SE/TLABC/AHA; no DE/GSK-family or CEC competition winners.
- Gains over the base WFO at 10D and 50D are modest by Wilcoxon counts (15/29 and 8/29 wins over WFO); the Friedman margin over WFO is small at all dims.
- ε = 0.9999999 is extremely close to 1 (integer order), suggesting the effective fractional deviation is small; parameter study is on 30D only.
- Real-world set limited to four power/energy problems taken from one source ([63]).

## Exact usable locators (bibkey, page)
- FO laminar update derivation (GL definition, memory-truncated updates): (tang2024fowfo, Sec. 3.1, p. 5 of 27, Eqs. (11)–(18)).
- Linear laminar-probability schedule Coef = t/T_max and its exploration→exploitation rationale: (tang2024fowfo, Sec. 3.2, p. 6 of 27).
- CEC2017 protocol (29 functions, F2 excluded; N = 100; maxFE = 10^4·D; 51 runs; D = 10/30/50/100): (tang2024fowfo, Sec. 4.1, pp. 7–8 of 27).
- Wilcoxon/Friedman evaluation criteria: (tang2024fowfo, Sec. 4.2, p. 8 of 27).
- Friedman ranks — FOWFO first at all four dimensions: (tang2024fowfo, Table 3, p. 8 of 27).
- Per-dimension W/T/L summaries: 10D (Table 4, pp. 9 ff. of 27, summary p. 8 of 27); 30D/50D/100D summaries (p. 17 of 27).
- Real-world problems (HSP/DED/LSTPP/ELD; D = 96–140; FOWFO best Mean/Best/Worst on all four): (tang2024fowfo, Sec. 4.4, p. 21 of 27, Tables 8–11 pp. 18–21 of 27).
- Parameter sensitivity (best e = 12, ε = 0.9999999): (tang2024fowfo, Sec. 5.1, p. 21 of 27, Tables 12–13).
- CPU-time analysis: (tang2024fowfo, Sec. 5.3, pp. 21–22 of 27, Tables 14–15).
- Conclusion: (tang2024fowfo, Sec. 6, p. 24 of 27).

## Supported uses in the DT-GSK manuscript
- Taxonomy/positioning: exemplar of a 2024 memory-augmented (fractional-order) enhancement of a recent swarm optimizer, evaluated on CEC2017 (D = 10–100, 51 runs, Wilcoxon + Friedman) plus large-dimension real-world power problems.
- Supporting the general statement that incorporating memory of past states/positions is a recognized route to improving metaheuristic search behavior.
- Supporting the observation that time-varying operator-selection probabilities (exploration early, exploitation late) are common design practice.

## Unsupported / prohibited overextensions
- Do NOT cite as evidence of superiority over DE/GSK-family algorithms or CEC winners — never compared.
- Do NOT present FOWFO's Friedman first place as "state of the art" for CEC2017; the pool is nine swarm/FO methods.
- Do NOT use as CEC2017 protocol authority (suite-definition key holds that role; awad2016problem currently blocked).
- Do NOT claim fractional-order calculus is required for the reported gains; the paper's own ε ≈ 1 setting is close to integer order and no such causal claim is made beyond the ablation shown.

## Role in DT-GSK framing (Appendix B.5)
"Taxonomy/positioning only." Sanctioned for related-work breadth (recent metaheuristic enhancement trends: memory mechanisms, adaptive operator scheduling); not for method inheritance, benchmark protocol, or statistics.
