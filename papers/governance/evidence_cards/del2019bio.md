# Evidence card — del2019bio

## Verified bibliographic identity
- Title: Bio-inspired Computation: Where We Stand and What's Next
- Authors: Javier Del Ser; Eneko Osaba; Daniel Molina; Xin-She Yang; Sancho Salcedo-Sanz; David Camacho; Swagatam Das; Ponnuthurai N. Suganthan; Carlos A. Coello Coello; Francisco Herrera
- Venue/year: Swarm and Evolutionary Computation, Vol. 48, pp. 220–250 (2019); DOI 10.1016/j.swevo.2019.04.008 (both printed on the local title page footer)
- Local file: `reference_papers/del2019bio.pdf` (85 pp.) — author-preprint layout ("Preprint submitted to Swarm and Evolutionary Computation, April 16, 2019", p. 1) with its own pagination 1–85. Published pagination 220–250 differs; locators below use LOCAL preprint pages, which are what resolves in the corpus.
- Inventory status: identity `verified`, readable, admissible. SHA-256 `bc757e03728955e1bf448037b3c45df619560783369ec1fd052077556761ef99`.

## Research question and context
Position survey by senior figures of the field: "to outline the state of the art and to identify open challenges concerning the most relevant areas within bio-inspired optimization", plus a critical analysis of the community's trajectory and the need for consensus (Abstract, p. 1). Motivated by the "gold rush" of metaphor-based algorithm proposals and the controversy about their relevance and novelty (Introduction, p. 2, citing Sörensen's "Metaheuristics — the metaphor exposed" as ref. [2]).

## Method
Narrative expert review, structured as: recent history of bio-inspired computation (Section 2, pp. 3–7); fourteen technical areas (Sections 3.1–3.14, pp. 7–47): theoretical foundations; dynamic/stochastic; multi/many-objective; multimodal; topologies; surrogate-assisted; distributed EAs; ensembles & hyper-heuristics; memetic algorithms; large-scale global optimization; parameter tuning; parameter adaptation; benchmarks and comparison methodologies; applications — each with a learned-lessons + challenges format (area map in Fig. 3, p. 8); then cross-cutting challenges (Section 4, pp. 47–50) and conclusions (Section 5, p. 50). Not a systematic review protocol; no experiments.

## Experimental scope
None (survey). Benchmark practice is summarized descriptively: standard suites define function sets, error measures, dimensions, "no less than 25" runs per function/dimension, stopping criteria (fixed max FES or required accuracy), and ranking criteria (p. 40); Table 1 (p. 41) catalogs benchmarks including CEC'2005, CEC'2011 (real-world problems, small dimensions), CEC'2013, CEC'2014, CEC'2015, CEC'2017 and BBOB for continuous optimization, plus multi-/many-objective, dynamic, multimodal and LSGO suites; CEC = fixed-cost vs BBOB = fixed-target comparison regimes (p. 41).

## Conservative findings (with locators)
1. NFL framing as community consensus: the lack of a universally outperforming metaheuristic "yields from the well-known No Free Lunch Theorem", which "states that no optimization algorithm can perform better than any other under any metric over all possible problems" (Section 3.1, p. 8; NFL refs [47]–[52]).
2. Benchmark methodology: ad-hoc, per-paper function sets make results incomparable; standard suites with common experimental conditions are the accepted remedy; drawbacks of informal comparisons include structural bias exploitation (optimum centered in the domain), unclear state-of-the-art baselines, and unfair non-retuned reference configurations (Section 3.13, p. 39).
3. Persistent malpractice: "more than ten years after the first benchmarks too many proposals are still published without a right comparison methodology", often compared only against classic algorithms rather than the state of the art (pp. 39–40); new metaphor-driven proposals frequently fail to acknowledge similarities to existing algorithms (p. 40, citing [2] and [319]).
4. Statistical-testing guidance: "it is mandatory to apply statistical tests to clarify the statistical significance of the performance gaps"; parametric-test assumptions are often unmet on benchmarks, so non-parametric tests are used, "the most popular is arguably the Wilcoxon test" for pairwise comparison, with post-hoc corrections "such as Holm/Hochberg/Hommel" for multiple comparisons; Bayesian tests are flagged as a promising newer trend and the p-value misinterpretation problem is noted (Section 3.13, p. 42; good-practice refs [345, 346]).
5. Parameter adaptation lineage: SaDE/JADE adapt distribution means of F and CR; "alternative versions like SHADE use a memory of several F and CR mean values"; current-to-pbest-style p-adaptation trends (Section 3.12, p. 38).
6. Field-level challenges: "More is not Always Better" — literature outbreak of allegedly novel bio-inspired methods without agreed theoretical/empirical evaluation standards makes it "absolutely unfeasible to separate the wheat from the chaff" (Section 4.1, p. 47); call for a unified, metaphor-free notation and description of algorithms (Section 4.2, pp. 47–48).
7. The paper endorses runs ≥ 25 and rank-based, multi-dimension weighted comparison criteria as the benchmark norm (p. 40, p. 42).

## Limitations
- Opinionated expert survey: positions (e.g., Bayesian tests as preferable, criticisms of metaphor-based work) are the authors' assessments, not empirical results.
- Preprint pagination; published article pages 220–250 not usable as locators from this file.
- Coverage is broad but shallow per area; for any specific algorithm's mechanics the primary sources must be cited instead.

## Exact usable locators (claim → locator)
- Purpose/scope of the survey: Abstract, p. 1.
- Metaphor controversy and "gold rush": Introduction, p. 2.
- NFL statement and role: Section 3.1, p. 8.
- Structural bias of algorithms/benchmarks: p. 10 and p. 39.
- SHADE/JADE parameter-adaptation summary: Section 3.12, p. 38.
- Drawbacks of ad-hoc comparisons: Section 3.13, p. 39.
- Benchmark design elements incl. ≥ 25 runs: p. 40.
- Table 1 benchmark catalog (CEC'2005–CEC'2017, CEC'2011 real-world, BBOB, LSGO): p. 41.
- Fixed-cost (CEC) vs fixed-target (BBOB): p. 41.
- Mandatory statistical testing; Wilcoxon; Holm/Hochberg/Hommel post-hoc; Bayesian trend: Section 3.13, p. 42.
- "More is not Always Better" challenge: Section 4.1, p. 47.
- Unified metaphor-free notation: Section 4.2, pp. 47–48.
- Conclusions: Section 5, p. 50.

## Supported uses in the DT-GSK manuscript
- Field-framing sentences: the proliferation of bio-inspired metaheuristics, the novelty controversy, and the community's demand for rigorous, benchmark-based, statistically tested comparisons.
- Supporting the manuscript's experimental-design choices as community-endorsed practice: standard CEC suites, ≥ 25 (DT-GSK uses more) independent runs, non-parametric pairwise tests (Wilcoxon) with FWER post-hoc corrections (Holm), and rank-based multi-algorithm summaries.
- Positioning statements that improving/analyzing existing algorithm families (rather than inventing new metaphors) aligns with the survey's recommendations (Sections 3.13, 4.1).

## Unsupported / prohibited overextensions
- Appendix B.9 rule: "field framing and taxonomy only as supported." Do NOT use this survey as evidence of any specific algorithm's performance, of GSK-family results, or of DT-GSK's positioning relative to named competitors.
- Do NOT cite it as the definition source of any CEC suite (suite-definition citations belong to the respective technical reports; note `awad2016problem` is currently BLOCKED).
- Do NOT cite it for the mathematical content of NFL (cite wolpert1997nfl) or of statistical tests (cite the primary statistics keys).
- Do NOT attribute the Bayesian-testing recommendation to the manuscript's own methodology unless the manuscript actually uses Bayesian tests.

## Role in DT-GSK framing (Appendix B.9)
`del2019bio` — field framing and taxonomy: used in the introduction/related-work to characterize the state and norms of bio-inspired optimization research and to justify the rigor of the experimental/statistical protocol.

## Verification quotation (identity)
"Bio-inspired Computation: Where We Stand and What's Next — Javier Del Ser ... Francisco Herrera. Preprint submitted to Swarm and Evolutionary Computation, April 16, 2019. Swarm and Evolutionary Computation, vol. 48, pp. 220-250 (2019). https://doi.org/10.1016/j.swevo.2019.04.008" (p. 1).
