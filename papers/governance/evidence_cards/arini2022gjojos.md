# Evidence card — arini2022gjojos

## Verified bibliographic identity
- Title: Golden Jackal Optimization With Joint Opposite Selection: An Enhanced Nature-Inspired Optimization Algorithm for Solving Optimization Problems
- Authors (source): Florentina Yuni Arini, Khamron Sunat, Chitsutha Soomlek
- Venue: IEEE Access, vol. 10, 2022, pp. 128800–128823
- DOI (source page 1): 10.1109/ACCESS.2022.3227510 — NOTE: the BibTeX record carries 10.1109/ACCESS.2022.3225010 and first-author name "Fatma Y. Arini"; both are bib metadata errors resolved from the local source (see reference_inventory.csv, identity_status = minor_metadata_mismatch).
- Local source: `reference_papers/arini2022gjojos.pdf` (24 pp., published IEEE Access layout; journal pagination 128800–128823 printed on pages)

## Research question and context
Can Golden Jackal Optimization (GJO), which underperforms other nature-inspired algorithms on CEC 2017, be improved by embedding Joint Opposite Selection (JOS) — a combination of two opposition-based-learning (OBL) strategies, Dynamic Opposite (DO, exploration) and Selective Leading Opposition (SLO, exploitation) — framed through Aristotle's square of opposition? (Abstract, p. 128800; Sec. I, pp. 128800–128801; motivation explicitly stated p. 128801: "there is no supporting evidence that GJO can conquer other benchmark problems such as CEC 2017. We conducted an experiment on CEC 2017 and found that GJO did not perform sufficiently".)

## Method
- GJO-JOS = GJO + JOS, where JOS jointly applies DO (jumping-rate-driven dynamic opposition, enriching diversification/exploration) and SLO (selective opposition of leading dimensions using GJO's existing linear decrement operator as threshold, accelerating exploitation) (Sec. I contributions list, p. 128801; Sec. II-A philosophy, pp. 128802–128803; Sec. III proposed method, pp. 128806–128807).
- Memory size of GJO-JOS is k × (NP × D) (p. 128807).

## Experimental scope
- Suite: CEC 2017 single-objective real-parameter suite, 29 functions (f1, f3–f30; f2 omitted as unstable), categories unimodal (f1, f3), simple multimodal (f4–f10), hybrid (f11–f20), composition (f21–f30); search space [−100, 100]^D (Sec. IV, p. 128807, Table 1 p. 128808).
- Dimensions: 10, 30, 50, 100. Runs: 51 per algorithm per function. Population NP = 30; jumping rate Jr = 0.25; maxFE = 10^4 × D; max iterations T = maxFE / NP (p. 128808).
- Evaluation: CEC-style scoring metric (Score = ScoreSE + ScoreSR, max 100, dimension weights 0.1/0.2/0.3/0.4 for 10/30/50/100D; Eqs. (7)–(11), pp. 128807–128808), plus mean/std tables and convergence curves. Wilcoxon signed-rank test is listed among evaluation instruments in the contributions (p. 128801).
- Comparators: (a) seven single OBL strategies embedded in GJO (DO, SLO, SO, Quasi, Generalized, Reflection; plus original GJO); (b) eight nature-inspired algorithms: WHO, AO, ABC, HHO, AOS, AOA, RLNNA, and original GJO (pp. 128801, 128810–128814). Hardware/software: MATLAB, i9-7980XE, 64 GB RAM, Windows 10 (p. 128807).

## Conservative findings
1. Against six OBL variants + GJO: GJO-JOS obtained the best (lowest) summed errors at all four dimensions and the maximum scoring-metric totals — SE total score 50 and SR total score 50 (Tables 2–3, pp. 128810–128811; discussion pp. 128810–128811, e.g., GJO-JOS SE sums 7.20E+05 / 1.54E+07 / 7.10E+07 / 2.96E+08 at 10/30/50/100D).
2. Against the eight nature-inspired algorithms: GJO-JOS total score 97.69 (SE 47.69, second to ABC's 50; SR 50, the highest) (Figs. 9–10 and text, pp. 128813–128814).
3. Per-function statistics (mean/std, Tables 4–7 and 10–13): GJO-JOS dominant or tied on most functions; losses are isolated and are enumerated in the text (e.g., loses to GJO-SLO on f9 at 100D, p. 128811; some 10D hybrid ties/losses to RLNNA and others, pp. 128815–128816).
4. Improvement over original GJO is largest on hybrid and composition functions and grows with dimension (e.g., f30 mean best fitness GJO 6.50E+09 vs GJO-JOS 2.10E+07 at 100D; pp. 128808–128809).
5. Conclusion: GJO-JOS "exhibited a strong performance in improving the original version of GJO ... especially in higher dimensions"; also acknowledges (citing reviews) that metaheuristics carry no guarantee of global optimality (pp. 128819–128820).

## Limitations
- Comparators do not include modern DE/GSK-family or CEC competition winners; the pool is GJO-variants plus general nature-inspired algorithms.
- Wilcoxon results are claimed in the contribution list but the visible analysis relies mainly on the scoring metric, means/stds, and convergence curves; treat significance-test claims cautiously.
- Population size fixed at 30 with a single Jr value; no parameter sensitivity study for JOS parameters is presented in the main text.
- No real-world problems; CEC 2017 only.

## Exact usable locators (bibkey, journal page)
- Motivation: GJO insufficient on CEC 2017 vs other nature-inspired algorithms: (arini2022gjojos, p. 128801).
- JOS = DO (exploration) + SLO (exploitation) design and Aristotle square framing: (arini2022gjojos, pp. 128801–128803).
- Experimental protocol (29 CEC2017 functions, f2 omitted; D = 10/30/50/100; 51 runs; NP = 30; maxFE = 10^4·D; Jr = 0.25): (arini2022gjojos, pp. 128807–128808, Table 1).
- Scoring-metric definition (SE/SR, weights, Eqs. (7)–(11)): (arini2022gjojos, pp. 128807–128808).
- GJO-JOS best among OBL-embedded GJO variants (both SE and SR total = 50): (arini2022gjojos, Tables 2–3, pp. 128810–128811).
- GJO-JOS total score 97.69 vs eight nature-inspired algorithms: (arini2022gjojos, pp. 128813–128814, Figs. 9–10).
- Conclusion and no-guarantee caveat: (arini2022gjojos, pp. 128819–128820).

## Supported uses in the DT-GSK manuscript
- Taxonomy/positioning sentence(s): as an example of recent (2022) opposition-based-learning enhancement of a nature-inspired metaheuristic evaluated on CEC 2017 at D = 10–100 with 51 runs and CEC scoring.
- Supporting the general observation that OBL-style mechanisms are used to rebalance exploration/exploitation in swarm algorithms.
- Noting that improvement claims are relative to the original GJO and a nature-inspired comparator pool (not against DE/GSK-family state of the art).

## Unsupported / prohibited overextensions
- Do NOT cite as evidence that GJO-JOS is state-of-the-art versus DE-family, GSK-family, or CEC competition winners — those comparisons were never run.
- Do NOT cite specific Wilcoxon significance outcomes (not verifiably reported in extracted tables).
- Do NOT use as a benchmark-protocol authority for CEC 2017 (that role belongs to the suite-definition key, which is currently blocked; see reference_inventory.csv on awad2016problem).
- Do NOT reuse the bib's DOI/first-author metadata without correction (bib carries a wrong DOI and given name).

## Role in DT-GSK framing (Appendix B.5)
"Taxonomy/positioning only." Sanctioned use is in related-work/positioning text situating DT-GSK among recent metaheuristic enhancement papers; not for method inheritance, not for benchmark definitions, not for statistical practice. Do not insert a citation merely to force bibliography usage (Appendix B.2 wording applies to breadth citations generally).
