# Evidence card — fialho2010adaptive

## Verified bibliographic identity
- Title: Adaptive Operator Selection with Dynamic Multi-Armed Bandits
- Authors AS PRINTED (source order): Luis Da Costa, Alvaro Fialho, Marc
  Schoenauer, Michele Sebag (p. 913). NOTE: the BibTeX entry lists Fialho
  first — wrong order; adopt source order if the entry is corrected.
- Venue: GECCO 2008 (Proceedings of the 10th Annual Conference on Genetic and
  Evolutionary Computation), Atlanta, July 12-16, 2008, pp. 913-920.
  ACM 978-1-60558-130-9/08/07. DOI 10.1145/1389095.1389272 (from BibTeX; not
  printed in the file).
- Identity status (reference_inventory.csv): `minor_metadata_mismatch` —
  identity certain; bib is typed @article with the proceedings name in the
  journal field, author order wrong, and the citation key says 2010 while
  the work is 2008. All resolved from the source; no external metadata used.
- Local file: `reference_papers/fialho2010adaptive.pdf`, 8 pages, fully
  readable.
- Page-locator convention: **printed proceedings pages 913-920**; PDF page =
  printed page - 912.

## Research question and context
How should the "adaptation rule" (decision making) component of Adaptive
Operator Selection (AOS) in evolutionary algorithms be designed, given that
operator quality changes during the run? Proposes a Dynamic Multi-Armed
Bandit (D-MAB) combining UCB1 with the Page-Hinkley change-detection test
(Abstract, p. 913; Sect. 1, pp. 913-914).

## Method and scope
- AOS decomposition: credit assignment (reward computation per operator) +
  adaptation/selection rule; this paper addresses only the latter (Abstract
  p. 913; Sect. 2, p. 914).
- AOS framed as exploration-vs-exploitation; the best operator changes along
  the run, so the formal problem is a DYNAMIC multi-armed bandit (Sect. 1,
  p. 914).
- Baselines defined: Probability Matching (PM) — selection probability
  proportional to relaxed reward estimate with floor p_min (Eqs. (2)-(3),
  p. 915); Adaptive Pursuit (AP) — winner-take-all update with learning rate
  beta (Eq. (4), p. 916); static MAB = UCB1 with the index
  p_hat_j + sqrt(2 log(sum_k n_k) / n_j) plus variants UCB-Tuned, KUCBT,
  cUCB (Eq. (1) and Table 1, p. 915).
- D-MAB: run UCB1 and restart it from scratch whenever the Page-Hinkley test
  (parameters lambda, delta) detects a change in the reward series
  (Sect. 4.1-4.2, p. 916). Reward scaling (multiplicative or affine) added
  to handle continuous rewards (Sect. 4.3, p. 917).
- Experimental protocol: ARTIFICIAL scenarios (no actual EA), following
  Thierens' protocol: K = 5 operators, 10 epochs, rewards permuted every
  Delta_T in {50, 200} steps; Uniform, Boolean, and Outlier reward scenarios;
  100 independent runs per setting; performance = total cumulative reward
  (TCR) and probability of picking the best operator (p_best); factorial
  design-of-experiments with 1-way ANOVA (95%) + Scheffe tests for parameter
  selection (Sect. 5, pp. 917-918; Sect. 6.1, p. 918).

## Conservative findings (with exact locators)
1. MAB-family algorithms outperform PM and AP on the tested scenarios:
   Uniform scenario Delta_T = 50 — MAB-M and D-MAB-M best; Delta_T = 200 —
   D-MAB-M and D-MAB-A statistically best; Boolean scenario — the STATIC
   MAB-M best for both epoch lengths (Sect. 6.3, p. 919; Tables 2-3, p. 919;
   Fig. 3, p. 920).
2. D-MAB is comparatively more robust to its parameter settings than PM and
   AP (response surfaces, Figs. 1-2, p. 918; Conclusion, p. 919).
3. Optimal p_min for PM/AP was ~0 or .01 — much lower than the 0.1 used in
   the original Thierens work; "greediness is a valid option" in these
   scenarios (Sect. 6.2, p. 919; Conclusion, p. 920).
4. The Outlier scenario (rare large rewards) was "poorly handled by all
   methods"; best p_best close to random guessing (Sect. 6.2, p. 918;
   Conclusion, p. 920).
5. Authors' own scope caveat: the artificial scenarios are "though probably
   far from reality" — validation is independent of any actual evolutionary
   algorithm (Conclusion, p. 920; also Sect. 3.2, p. 915: "it is doubtful
   that the reward of variation operators ... obeys such simple
   distributions").

## Limitations relevant to citation
- No evolutionary algorithm was run: rewards are synthetic distributions with
  scheduled permutations. No function optimization, no benchmark suite, no
  dimensions.
- Results depend on scenario type (static MAB beat D-MAB on Boolean); no
  universal winner.
- Credit assignment — the other half of AOS — is explicitly out of scope
  (footnote 1 and Sect. 2, p. 914).

## Supported uses in the DT-GSK manuscript
- Citing that adaptive operator selection is formally a dynamic bandit
  problem with an exploration/exploitation dilemma (Sect. 1, p. 914).
- Citing the standard AOS decomposition into credit assignment + operator
  selection rule (Abstract p. 913; Sect. 2 p. 914) when describing where an
  DT-GSK adaptive controller (e.g., ACE) sits conceptually.
- Citing bandit-based operator selection (UCB variants, restart-on-change)
  as established prior art for adaptive control in evolutionary computation
  (Sects. 3-4, pp. 915-917).
- Citing that operator quality varies along the run, motivating dynamic
  rather than static adaptation (Sect. 1, p. 914).

## Unsupported / prohibited overextensions
- Appendix B.7 (binding): grounding only — "not proof that the exact ACE
  mechanism is inherited". Do NOT describe DT-GSK's controller as D-MAB/PM/
  AP unless mechanism-level verification against the frozen code shows it.
- Do NOT cite as evidence that bandit-based AOS improves optimization
  performance on any real benchmark; validation is on artificial reward
  scenarios only (p. 920).
- Do NOT generalize the PM/AP-vs-MAB ranking beyond the tested scenarios
  (the Boolean scenario reversed the dynamic-vs-static ordering, p. 919).
- Do NOT cite with journal-style metadata or year 2010 in prose; the work is
  the GECCO 2008 paper (key remains `fialho2010adaptive` as frozen).

## Role in DT-GSK framing (Appendix B.7)
Adaptive-operator-selection grounding: canonical evidence that the EC
community formalizes on-line operator/strategy selection as a (dynamic)
multi-armed bandit, supporting the design rationale of DT-GSK's adaptive
knowledge control at the positioning level.

## Verification quotation (identity)
"a specific Dynamic Multi-Armed Bandit algorithm is proposed, that hybridizes
an optimal Multi-Armed Bandit algorithm with the statistical Page-Hinkley
test" (Abstract, p. 913).
