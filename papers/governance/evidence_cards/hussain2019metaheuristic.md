# Evidence card — hussain2019metaheuristic

## Verified bibliographic identity
- Title: Metaheuristic research: a comprehensive survey
- Authors: Kashif Hussain; Mohd Najib Mohd Salleh (Universiti Tun Hussein Onn Malaysia); Shi Cheng (Shaanxi Normal University); Yuhui Shi (SUSTech)
- Venue/year: Artificial Intelligence Review; DOI 10.1007/s10462-017-9605-z printed on p. 1; © Springer 2018 online-first; bib cites the 2019 issue 52(4) — consistent (inventory note).
- Local file: `reference_papers/hussain2019metaheuristic.pdf` (43 pp., Springer online-first layout paginated 1–43 with "123" footers). Published issue pagination (2191–2233) is not printed; locators use LOCAL pages 1–43.
- Inventory status: identity `verified`, readable, admissible. SHA-256 `83512295350e91a5839acb0a46ae8de70ea40a9a652248c7019605102511e31a`.

## Research question and context
What is the volume, structure, and direction of metaheuristic research, and what open questions and critical issues does the literature raise? The survey observes that "little has been evidenced on insightful analysis of metaheuristic performance issues, and it is still a 'black box' that why certain metaheuristics perform better on specific optimization problems and not as good on others" (Abstract, p. 1).

## Method
Systematic mapping study (guidelines of Keele 2007 with the mapping process of Petersen et al. 2008): preliminary study, research questions, keyword search across publication databases, two-iteration screening with inclusion/exclusion criteria (excluding papers under 5 pages and off-topic items), and data extraction (Section 2, pp. 2–6; process figure Fig. 1). Corpus: **1222 publications from 1983 to mid-2016 (33 years)** (Abstract, p. 1; Section 2.4, p. 5). Analysis is organized around research questions covering: definitions/foundations (optimization, metaheuristics, exploration vs exploitation; Section 3.1, pp. 6–9), publication intensity (RQ2, p. 9, Fig. 2), venues and publication types (p. 10, Fig. 3), algorithm popularity (Fig. 5, p. 25), related surveys (Section 4, pp. 28–31), research gaps (Section 5, pp. 31–33), and conclusions (Section 6, p. 33). Four dimensions of the field are addressed: "introduction of new algorithms, modifications and hybrids, comparisons and analysis, and research gaps and future directions" (Abstract, p. 1).

## Experimental scope
Bibliometric only; no algorithm experiments. Corpus counts: category totals per publication years shown in the table on p. 4 (e.g., Swarm Intelligence 157 of 1222); total 1222 across venue types (p. 10); year-wise intensity Fig. 2 (p. 9) with a post-2011 surge; algorithms with ≥ 10 publications charted in Fig. 5 (p. 25). Appendix Table 4 (pp. 34–37) lists acronyms for the metaheuristics encountered — a breadth indicator of the "novel metaphor" flood.

## Conservative findings (with locators)
1. Metaheuristic research grew massively over 1983–2016 (1222 publications; sharp surge after 2011), spanning new algorithms, hybrids, comparisons, and applications (Abstract p. 1; p. 9).
2. Performance analysis practice is criticized as ad hoc: "performance analysis of metaheuristic methods have been mostly performed based on simple mean of objective function values, standard deviation, and some basic statistical tests on certain test functions; which is an ad-hoc approach. More well-established and commonly agreed performance validation criteria are required" (Section 6 gap list, p. 33; also Boussaïd et al. paraphrase "More statistical analysis is required for authentic comparisons", p. 31).
3. Theoretical foundations lag: gaps include formal definitions and measures of exploration/exploitation, understanding which algorithm components contribute to each, convergence analysis, and mathematical explanations of efficiency (pp. 31–32, drawing on Črepinšek 2013 and Yang 2011; summary bullets p. 33).
4. Benchmark representativeness is questioned: "how these common benchmark test set and evaluation criteria reflect the characteristics of real-world problems?" (p. 31, after Mahdavi et al. 2015); scalability beyond ~1000 dimensions flagged (p. 31).
5. The metaphor flood is acknowledged critically: past twenty years "flooded with 'novel' metaheuristics", which per Koziel & Yang "has harmed research in its true sense of scientific findings" (Section 6, p. 33).
6. Future directions: agreed validation criteria; theoretical/mathematical foundations for exploration–exploitation and convergence; scalable, self-adaptive/self-tuning metaheuristics for large, imbalanced problems (Section 6 bullets, pp. 33–34).

## Limitations
- Corpus ends mid-2016; counts and trends do not cover the GSK era (GSK itself, 2020, is absent) or any recent algorithm.
- Systematic-mapping breadth, not depth: no algorithm mechanics, no benchmarking data, no statistical methodology of its own.
- Some historical statements carry typos in the source (e.g., "1680s" for the 1980s introduction of Tabu Search/Simulated Annealing, p. 33) — do not quote uncritically.
- Local pagination differs from the published issue pagination.

## Exact usable locators (claim → locator)
- Survey scope: 1222 publications, 1983–2016, four dimensions: Abstract, p. 1.
- "Black box" performance-understanding gap: Abstract, p. 1.
- Systematic mapping process and screening: Section 2, pp. 2–6.
- Definitions of optimization/metaheuristic; exploration vs exploitation (diversification/intensification): Section 3.1, pp. 6–9.
- Publication intensity and post-2011 surge: Section 3.2, p. 9 (Fig. 2).
- Venue/type distribution (total 1222): p. 10 (Fig. 3).
- Category totals (e.g., Swarm Intelligence 157): table, p. 4.
- Algorithm popularity chart (≥ 10 publications): Fig. 5, p. 25.
- Related surveys: Section 4, pp. 28–31.
- Research gaps (statistical rigor, theory, scalability, benchmark realism): Section 5, pp. 31–33.
- Concluding gap bullets (ad-hoc validation criticism; theory; self-adaptive scalability): Section 6, pp. 33–34.

## Supported uses in the DT-GSK manuscript
- Field-framing/taxonomy sentences: the scale and growth of metaheuristic research; the recognized split of the literature into new algorithms, modifications/hybrids, and comparative analyses.
- Motivating rigor: the documented criticism that mean/SD-only reporting is ad hoc supports the manuscript's use of formal non-parametric testing, effect sizes, and agreed validation protocols.
- Motivating analysis-driven improvement of an existing family (DT-GSK) over inventing new metaphors, via the survey's critical stance on the "novel metaheuristic" flood (p. 33).

## Unsupported / prohibited overextensions
- Appendix B.9 rule: "field framing and taxonomy only as supported." Do NOT use this survey for any algorithm-specific performance claim, for GSK-family facts (GSK postdates the corpus), or as evidence about CEC benchmark protocols.
- Do NOT extrapolate its 1983–2016 bibliometrics to the present ("research has continued to grow" needs no citation or a different one).
- Do NOT cite it as prescribing any specific statistical test — it calls for agreed criteria but prescribes none (that support comes from demsar2006statistical / the statistics keys / del2019bio).

## Role in DT-GSK framing (Appendix B.9)
`hussain2019metaheuristic` — field framing and taxonomy: introduction/related-work support for the state, growth, and methodological criticisms of metaheuristic research.

## Verification quotation (identity)
"Artif Intell Rev — https://doi.org/10.1007/s10462-017-9605-z — Metaheuristic research: a comprehensive survey — Kashif Hussain · Mohd Najib Mohd Salleh · Shi Cheng · Yuhui Shi — © Springer Science+Business Media B.V., part of Springer Nature 2018" (p. 1).
