# Evidence card — auer2002finite

## Verified bibliographic identity
- Title: Finite-time Analysis of the Multiarmed Bandit Problem
- Authors: Peter Auer, Nicolo Cesa-Bianchi, Paul Fischer
- Venue: Machine Learning 47, pp. 235-256, 2002 (Kluwer). DOI in BibTeX:
  10.1023/A:1013689704352 (not printed in file; identity verified by
  title/authors/venue/pagination on p. 235).
- Identity status (reference_inventory.csv): `verified`.
- Local file: `reference_papers/auer2002finite.pdf`, 22 pages, fully readable.
- Page-locator convention: **printed journal pages 235-256**; PDF page =
  printed page - 234.

## Research question and context
Can simple, efficient bandit policies achieve the optimal logarithmic regret
UNIFORMLY over time (finite-time bounds), rather than only asymptotically as
in Lai and Robbins (1985)? (Abstract and Sect. 1, pp. 235-236.)

## Method and scope
- Setting: K-armed bandit; arm i yields i.i.d. rewards with unknown mean
  mu_i; regret after n plays is mu* n - sum_j mu_j E[T_j(n)] (Sect. 1,
  pp. 235-236). Delta_i := mu* - mu_i (p. 237).
- UCB1 policy: after playing each machine once, at each step play the machine
  j maximizing x_bar_j + sqrt(2 ln n / n_j), where x_bar_j is the average
  reward of machine j and n_j the number of times j has been played
  (Figure 1, p. 237).
- UCB2: epoch-based refinement with parameter alpha; index
  x_bar_i + a_{n,r_i} with a_{n,r} = sqrt((1+alpha) ln(e n / tau(r)) /
  (2 tau(r))), tau(r) = ceil((1+alpha)^r) (Figure 2 and Eq. (3), p. 238).
- epsilon_n-GREEDY: play the empirical best arm with probability 1-eps_n,
  a random arm otherwise, with eps_n decreasing as c K/(d^2 n) (Figure 3,
  p. 239).
- UCB1-NORMAL for normal rewards (Figure 4, p. 240).
- UCB1-TUNED (experimental variant): replaces the exploration term by
  sqrt((ln n / n_j) min{1/4, V_j(n_j)}) where V_j is an upper confidence
  bound on the variance; no proven regret bound (Sect. 4, p. 245).
- Experiments: Bernoulli reward distributions, 2-armed and 10-armed setups
  (distributions 1-3, 11-14), 100,000 plays averaged over 100 runs; measures
  are percentage of optimal-machine plays and actual regret (Sect. 4,
  pp. 245-246; comparison Figs. 6-12, pp. 247-250).

## Conservative findings (with exact locators)
1. Theorem 1 (p. 237): UCB1 on any reward distributions with support in
   [0,1] has expected regret at most
   [8 sum_{i: mu_i < mu*} (ln n / Delta_i)] + (1 + pi^2/3)(sum_j Delta_j) —
   logarithmic regret uniformly over time, no prior knowledge needed.
2. Theorem 2 (pp. 238-239): UCB2 brings the leading constant arbitrarily
   close to the optimal 1/(2 Delta_i^2) rate.
3. Theorem 3 (pp. 239-240): epsilon_n-GREEDY with tuned input d achieves
   instantaneous regret of order c/(d^2 n), but requires knowing a lower
   bound d on the gap between best and second-best arm (Remark, p. 240).
4. Empirical summary (Sect. 4.1, p. 247): an optimally TUNED epsilon-greedy
   performs almost always best, but degrades rapidly if mis-tuned;
   UCB1-TUNED is comparable to well-tuned epsilon-greedy, is "not very
   sensitive to the variance of the machines", and UCB2 is slightly worse
   than UCB1-TUNED.
5. Theorems 1-3 hold even for rewards dependent across arms and merely
   mean-stationary per arm (remark, p. 241).
6. Assumption structure: the core setting is STATIC — reward distributions
   do not change over time (Sect. 1, pp. 235-236).

## Limitations relevant to citation
- Rewards assumed bounded in [0,1] (Theorems 1-3) or normal (Theorem 4);
  regret optimality is with respect to stationary distributions.
- No treatment of non-stationary/dynamic bandits — directly relevant because
  operator quality in an evolutionary run drifts (that gap is the subject of
  `fialho2010adaptive`).
- UCB1-TUNED, often used in practice, has NO proven regret bound (p. 245).
- Empirical scope: Bernoulli distributions, K = 2 or 10 arms only.

## Supported uses in the DT-GSK manuscript
- Citing UCB1's index formula x_bar_j + sqrt(2 ln n / n_j) and its
  finite-time logarithmic regret guarantee (Figure 1 + Theorem 1, p. 237) as
  the canonical exploration-exploitation allocation rule.
- Grounding, at the conceptual level, any bandit-style or
  confidence-bound-style adaptive control in DT-GSK (e.g., ACE knowledge
  control), i.e., "adaptive allocation among discrete options with
  logarithmic-regret credentials in the stationary case".
- Citing the exploration/exploitation dilemma framing (Abstract, p. 235).
- Citing that epsilon-greedy-style rules work well only when well tuned
  (Sect. 4.1, p. 247) as bounded motivation for confidence-based rather than
  fixed-epsilon control.

## Unsupported / prohibited overextensions
- Appendix B.7 (binding): bandit sources ground adaptive operator selection
  but are "not proof that the exact ACE mechanism is inherited". Do NOT
  claim DT-GSK's controller IS UCB1 or inherits its regret bound unless the
  frozen code provably implements the exact policy under its assumptions.
- Do NOT transfer regret guarantees to the non-stationary rewards of an
  evolutionary run; the theorems assume time-invariant distributions.
- Do NOT claim UCB-style control guarantees optimization performance on any
  benchmark; regret is defined w.r.t. arm means, not objective optima.
- Do NOT cite UCB1-TUNED as having a proven bound (explicitly unproven,
  p. 245).

## Role in DT-GSK framing (Appendix B.7)
Bandit/adaptive-control grounding for the design rationale of ACE-style
adaptive knowledge control: establishes that principled adaptive allocation
between discrete alternatives exists with finite-time guarantees, motivating
(not proving) adaptive bias in DT-GSK.

## Verification quotation (identity)
"In this work we show that the optimal logarithmic regret is also achievable
uniformly over time, with simple and efficient policies, and for all reward
distributions with bounded support" (Abstract, p. 235).
