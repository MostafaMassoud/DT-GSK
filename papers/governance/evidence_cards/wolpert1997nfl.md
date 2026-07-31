# Evidence card — wolpert1997nfl

## Verified bibliographic identity
- Title: No Free Lunch Theorems for Optimization
- Authors: David H. Wolpert (IBM Almaden Research Center); William G. Macready (Santa Fe Institute)
- Bib venue/year: IEEE Transactions on Evolutionary Computation 1(1):67–82, 1997; DOI 10.1109/4235.585893
- Local file: `reference_papers/wolpert1997nfl.pdf` (32 pp.) — **PREPRINT dated December 31, 1996** (affiliation block, p. 1). The IEEE TEVC venue, volume, and 67–82 pagination are NOT printed in the file; identity of the work (title, authors, content) is verified.
- Inventory status: identity `verified`, readable, admissible; "Locators must use preprint pagination." SHA-256 `cba4647681eb73d5511a126e0c547e711c26b7db5be76f1ebf6116c03ff92340`.
- Locator convention: preprint page numbers 1–32 (printed at page bottoms; equal to PDF page numbers). Section numbers also given — they survive into the published version, page numbers do not.
- Text-extraction caution: old DVI-derived scan; extraction is noisy (digits and ligatures garbled). Verify any verbatim quote against the page image.

## Research question and context
What can be said a priori — "without any assumptions and from mathematical principles alone" — about the relationship between the performance of black-box optimization algorithms and the problems they are run on? In particular, how does the set of problems on which algorithm a1 beats a2 compare with the set where the reverse holds? (Abstract p. 1; Introduction pp. 1–3; explicit disclaimer that "no claims whatsoever are being made ... concerning how well various search algorithms work in practice", p. 3.)

## Method
- Formal model (Section 2, pp. 3–6): finite search space X, finite cost-value space Y; problems f : X → Y, F = Y^X; a "sample" d_m is the time-ordered set of m DISTINCT visited points; algorithms are (deterministic; extension to stochastic given later) mappings from samples to a new, previously unvisited point. Performance after m iterations is any function Φ(d^y_m) of the sample's cost values; comparison is by number of distinct oracle calls (pp. 4–5). Wall-clock measures are outside scope (p. 5).
- Static NFL — Theorem 1 (Section 3, p. 6; proof Appendix A): for any pair of algorithms a1, a2,
  Σ_f P(d^y_m | f, m, a1) = Σ_f P(d^y_m | f, m, a2).
  Corollary: for ANY performance measure Φ(d^y_m), the f-averaged distribution of performance is independent of the algorithm (p. 6).
- Time-dependent NFL — Theorem 2 (p. 7; proof Appendix B): same equality when averaging over all bijective evolution operators T, for both sampling schemes d^y_m and D^y_m.
- Stochastic algorithms: NFL extends to stochastic non-revisiting algorithms (Section 3.2, pp. 9–10).
- Geometric interpretation (Section 4, pp. 10–13): P(d^y_m | m, a) = Σ_f P(d^y_m | f, m, a) P(f) is an inner product; an algorithm's average performance is determined by how "aligned" it is with the prior P(f) over problems (Eq. 1, p. 8; Section 4).
- Information-theoretic/benchmark results (Section 5, pp. 13–15): Theorems 3–4 (fractions of problems giving a specified histogram); Theorems 5–7 (benchmark measures; behavior of the random algorithm).
- Minimax distinctions (Section 6, pp. 16–19): despite NFL, head-to-head minimax distinctions between pairs of algorithms can exist (Theorem 8, p. 17, and the constructive example).
- Fixed-f, algorithm-averaged results (Section 7, pp. 19–21): Theorems 9–10 (p. 20) — averaged over all algorithms, one cannot use an algorithm's observed behavior on f to justify predictions of its future behavior; choosing between algorithms based on observed performance embeds assumptions about how the algorithms relate to the cost function (p. 20 discussion).
- Conclusions and open problems (Section 8, p. 21).

## Experimental scope
None — purely theoretical (finite spaces, combinatorial arguments; proofs in Appendices A–F, pp. 22–32).

## Conservative findings (with locators)
1. Averaged uniformly over all cost functions on finite X, Y, all algorithms have identical performance distributions for any performance measure (Theorem 1, p. 6).
2. Consequently, "if an algorithm performs better than random search on some class of problems then it must perform worse than random search on the remaining problems" — elevated performance on one class is exactly paid for on the complement (Section 3.1, p. 8; Abstract, p. 1).
3. Comparisons reporting an algorithm's performance "on a few sample problems are of limited utility"; generalization beyond the tested problem range is unwarranted a priori (Section 3.1, p. 8).
4. The mere EXISTENCE of structure in a problem class does not justify a particular algorithm choice; "that structure must be known and reflected directly in the choice of algorithm" (Section 3.1, pp. 8–9).
5. Uniform P(f) is not essential: NFL also holds for a range of non-uniform priors (factorizable priors; permutation-closed rank-ordered sums), so non-uniformity of the practitioner's P(f) does not by itself restore distinctions (Section 3.1, p. 9).
6. NFL is compatible with a priori head-to-head minimax distinctions between algorithms (Section 6, pp. 16–19, Theorem 8, p. 17) and with alignment-based explanations of why structure-exploiting algorithms work in practice (Section 4, pp. 10–13).
7. Scope conditions built into the theorems: finite X and Y; performance a function of the sample of distinct evaluations only; algorithms compared by distinct oracle calls; deterministic or stochastic non-revisiting algorithms (Section 2, pp. 3–5; Section 3.2, pp. 9–10).

## Limitations
- Preprint copy: published TEVC page numbers (67–82) cannot be cited from this file; section/theorem numbers are the portable locators.
- Results are set in finite search/cost spaces with the oracle model; they say nothing about revisiting-cost, wall-clock time, or implementation efficiency (pp. 4–5).
- The paper itself stresses it makes no claims about practical performance (p. 3) — it constrains what may be claimed a priori.
- Noisy text extraction (see identity block).

## Exact usable locators (claim → locator)
- NFL Theorem 1 (static): Section 3, p. 6; proof Appendix A, pp. 22–23.
- Corollary for any performance measure: p. 6, immediately after Theorem 1.
- NFL Theorem 2 (time-dependent): p. 7; proof Appendix B.
- "Better than random somewhere ⇒ worse than random elsewhere": Section 3.1, p. 8.
- Limited utility of few-problem comparisons: Section 3.1, p. 8.
- Structure must be known and incorporated: Section 3.1, pp. 8–9.
- NFL under non-uniform priors: Section 3.1, p. 9.
- Stochastic algorithms covered: Section 3.2, pp. 9–10.
- Geometric "alignment" interpretation: Section 4, pp. 10–13 (P(f)-inner-product framing; Eq. (1) on p. 8).
- Benchmark-measure theorems: Section 5, pp. 13–15 (Theorems 3–7).
- Minimax distinctions: Section 6, pp. 16–19 (Theorem 8, p. 17).
- No a priori justification from observed behavior on the same f: Section 7, pp. 19–21 (Theorems 9–10, p. 20).
- Disclaimer (no practical-performance claims): Introduction, p. 3.

## Supported uses in the DT-GSK manuscript
- Citing NFL as the bounded premise that no optimizer is expected to dominate over ALL problems, hence (a) algorithm design must encode known problem structure, and (b) empirical claims must be scoped to the benchmarked problem classes (CEC2017/CEC2011 suites) rather than "all problems".
- Supporting careful wording of contribution claims: superiority statements are per-suite/per-dimension empirical findings, not universal expectations.

## Unsupported / prohibited overextensions
- Appendix B.9 rule: "bounded NFL premise, never proof of expected superiority." Do NOT use NFL to argue that DT-GSK (or any method) is expected to be superior, or that observed benchmark wins imply general superiority.
- Do NOT invert NFL into "all algorithms are equal in practice" — the paper explicitly disclaims practical-performance statements (p. 3) and shows practice depends on alignment with P(f) (Section 4).
- Do NOT cite this key for NFL refinements/limitations from later literature (sharpened NFL, focused NFL, non-closed function classes, continuous-domain caveats) — outside this corpus.
- Do NOT cite published TEVC page numbers from this preprint copy.

## Role in DT-GSK framing (Appendix B.9)
`wolpert1997nfl` — foundations: the NFL premise used once, in the framing/discussion, to motivate structure-exploiting design and bounded claims. Never used as evidence of expected superiority.

## Verification quotation (identity)
"No Free Lunch Theorems for Optimization — David H. Wolpert, IBM Almaden Research Center ... William G. Macready, Santa Fe Institute ... December 31, 1996" (p. 1; extraction-noise cleaned, verified against page image).
