# Glossary

> **What this page is.** Short definitions of the terms and abbreviations used
> across the documentation and code. **Who it is for.** Anyone who hits an
> unfamiliar term. **Tip.** Other pages link here on first use.

| Term | Meaning |
|---|---|
| ACE | Adaptive Configuration Engine: DT-GSK's multi-armed bandit over a 5-arm (+DE) pool of `(KF, KR, Kexp)` operator settings; EMA credit-tracking concentrates draws on the arms with the higher realised improvement (credit = the positive fitness delta). Part of contribution C2. |
| AGSK | Adaptive Gaining-Sharing Knowledge optimizer with adaptive parameter pools and population reduction. |
| APGSK | Adaptive-parameters GSK variant with a mixed positive/negative `KF` pool and stochastic junior schedule. |
| ARGP | Acceptance-Rate Gated Pruning: prunes ACE pool entries whose windowed acceptance falls below a dimension-tier threshold after a warm-up fraction of the budget. Part of C2. |
| ATMALS-GSK | GSK variant with adaptive memory and local search mechanisms. |
| BCa bootstrap | Bias-corrected-and-accelerated bootstrap confidence interval (Efron 1987); implemented in `analysis.statistics.bootstrap_bca_ci`. |
| BenchmarkProblem | Python object that wraps suite metadata, bounds, budget, known optimum, and evaluator. |
| BSE | Budget-Safe Escape: a triple-trigger (acceptance / diversity / signal) stagnation detector that fires a Cauchy rescue and an archive-seeded restart, capped so it can never overshoot the budget. Part of C2. |
| C1 | DT-GSK contribution 1 — a deterministic final polish: a one-shot, RNG-free compass search fired in the final budget slice, active at the `D>=50` tiers. The mechanism searches the eigenbasis of the signed interaction graph (falling back to the coordinate axes when the graph carries no signal), but C1 is claimed *basis-neutrally*: the three-arm basis isolation (Supplementary Materials, Section S9.1) shows the polish beating no refinement at both active dimensions, while the learned eigenbasis is beaten by the plain coordinate axes at `D=50` (Holm 1.4e-4, 25 of 29 functions) and, under the canonical 1e-8 tie rule, at `D=100` as well (Holm 0.0489). The contribution is the deterministic endgame, not the basis it searches along. |
| C2 | DT-GSK contribution 2 — dimension-tiered adaptive scaffold: the `pub` profile's ACE/ARGP operator control, the NLPSR population schedule, and BSE + the diversity archive + the deep-stall restart, each gated and tuned by dimension tier. |
| C3 | DT-GSK contribution 3 — controlled family evaluation: the seven-algorithm GSK-family panel run under one frozen protocol. |
| CEC | Congress on Evolutionary Computation benchmark family. |
| Cliff's delta | Non-parametric `(wins - losses) / n` effect size in `[-1, 1]` reported alongside paired Wilcoxon results. |
| Convergence trace | Best-so-far objective values recorded against evaluation counts. |
| Critical difference (CD) | Nemenyi post-hoc threshold; two mean ranks differ significantly when they are farther apart than the CD. Drawn as a Demsar-style CD diagram. |
| Dimension tier | The dimension band (`D<20`, `20<=D<50`, `D>=50`, plus a `D>=100` controller bundle) at which DT-GSK's `pub` profile gates and tunes each subsystem. |
| DT-GSK | Dimension-Tiered Gaining-Sharing Knowledge: this project's proposed optimizer, byte-identically migrated from the source DT-GSK v2.1 project; renamed from ISM-GSK (2026-07-14). |
| eGSK | Enhanced GSK-family optimizer, a faithful MATLAB port (`optimizers/egsk.py`; the only deviation is `scipy.optimize.minimize(method="SLSQP")` for the interior-point refinement in place of MATLAB `fmincon`). Runnable via `--optimizer egsk` and validated as statistically equivalent to the reference; it also remains a reference comparator, contributing committed reference statistics to the analysis panel. |
| Fair start | Shared initial population and post-initialization RNG state used to compare optimizers fairly. |
| FDB | Fitness-Distance Balance selection signal (normalized fitness plus normalized distance to the best). |
| FDB-AGSK | AGSK variant that injects FDB-selected candidates into junior and senior donor sets. |
| Friedman test | Non-parametric rank test across the algorithm panel; produces the mean ranks shown in the CD diagram and rank chart. |
| Function id | Benchmark function number inside a suite. |
| `get_cec_seed` | The unified deterministic seed function (`runners.seed_policy`) that derives one seed per `(base, dim, function, run)` cell. |
| GSK | Baseline Gaining-Sharing Knowledge optimizer. |
| GSK-family panel | The 7-algorithm statistical comparison set: the six reference comparators (`gsk`, `agsk`, `apgsk`, `fdb-agsk`, `egsk`, `atmals-gsk`) plus the proposed `dt-gsk`. |
| Holm correction | Step-down multiple-comparison adjustment applied to the pairwise Wilcoxon p-values in the family report. |
| ISM | Interaction-structure memory (a.k.a. SGSM): a confidence-gated success graph that records the co-movement of strictly improving accepted moves without additional objective evaluations (active at `D>=50`), supplying linkage evidence to the block crossover and an eigenbasis to C1's polish. A *specified negative result, not a contribution*, and dropped from the paper's keywords — the direct-isolation overlay shows no significant standalone benefit at its active tiers once Holm-corrected, and the three-arm basis isolation (Supplementary Section S9.1) goes further: in the memory's terminal exploitation channel, the polish basis, the learned eigenframe is *outperformed* by the plain coordinate axes at `D=50` (Holm 1.4e-4, 25 of 29 functions) and, under the canonical 1e-8 tie rule, at `D=100` as well (Holm 0.0489). Nor is it free in compute: enabling it costs +57.3% wall-clock on CEC2017 at `D=50`, +36.3% at `D=100`, and +30.3% on CEC2013 at `D=50`. The algorithm is named DT-GSK, never "ISM-GSK". |
| Junior phase | Early-stage gaining-sharing where an individual learns from its fitness-rank neighbours and a random peer (exploration). |
| Knowledge factor (`kf`) | Step scale applied to a gained vector in the GSK update. |
| Knowledge ratio (`kr`) | Per-dimension probability that a gained value replaces the parent value. |
| Known optimum | Suite-provided objective optimum used to compute error. |
| LPSR | Linear Population-Size Reduction: shrinking the population from an initial size toward a floor as the evaluation budget is spent. |
| Midpoint repair | Bound repair that pulls an out-of-range coordinate to the midpoint between the parent value and the breached bound. |
| Native-dimension suite | Suite where each function owns its natural dimension instead of accepting arbitrary dimensions. |
| NFEs | Number of function evaluations. |
| NLPSR / `n_min` | Nonlinear Population-Size Reduction (`psr_schedule = "nlpsr"` in the `pub` profile): shrinks the population along a nonlinear schedule toward the floor `n_min` (the `DTGSKConfig` default is 12; the `pub` profile raises it to 25 at `D>=50`). Part of C2. |
| numeric compatibility helper | Python helper that preserves a reference rounding, sorting, indexing, RNG, or bounds behavior. |
| Parallel backend | Execution backend for independent run tasks: `process` (default, multi-core process pool) or `thread` (GIL-bound). Serial execution is selected by disabling parallel (`parallel: false` / `--serial`), not by a `parallel_backend` value. |
| Proposed optimizer | The optimizer a statistical report is anchored on; defaults to `dt-gsk` (`analysis.family_report.DEFAULT_PROPOSED`). |
| Reduced budget | Experiment with `max_evaluations` lower than the suite's full protocol budget. |
| Reference comparator | A GSK-family optimizer with committed reference statistics used in the comparison panel (`analysis.project_policy.REFERENCE_COMPARATORS`). |
| Reference seed policy | Seed policy that reproduces published reference tables bit-for-bit using per-optimizer seeding. |
| Reference table | Imported reference summary table under `benchmarks/cec_reference_results/`; the validation baseline and the analysis layer's primary (reference-first) data source. |
| Review pack | The matplotlib-only reviewer PDF (`papers/DT-GSK-CEC2017-review.pdf`) of 7-algorithm convergence grids, built by `papers/scripts/generate_review_pack.py`. |
| Senior phase | Late-stage gaining-sharing where an individual learns from the elite and worst blocks via a middle performer (exploitation). |
| Suite | Benchmark collection such as `cec2017` or `cec2020`. |
| threefry | Counter-based RNG generator; the default `rand_generator` for campaigns (the runner config default). |
| twister | Mersenne Twister RNG generator; the `OptimizerOptions` dataclass default and the reference-compatible generator. |
| Unified seed policy | Default seed policy that makes matching cells comparable across optimizers via a shared fair start. |
| Vargha-Delaney A12 | Probability-of-superiority effect size; `A12 > 0.5` favours the proposed optimizer (`analysis.statistics.vargha_delaney`). |
| Win/tie/loss | Per-function tally of whether the proposed optimizer beats, ties, or loses to a comparator. |
