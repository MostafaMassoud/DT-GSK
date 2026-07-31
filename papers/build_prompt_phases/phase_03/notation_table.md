# DT-GSK — Notation Table (canonical, Word-ready source)

**Phase 3 deliverable** (Phase 3 task 3 & outputs `notation_table.tex` /
`notation_table_word.omml.xml`). This Markdown is the **canonical** notation source;
`notation_table.tex` is its LaTeX rendering and the Word OMML rendering is generated in
Phase 9 from this table (do not hand-author OMML in Phase 3). Every symbol used in
`algorithm_pseudocode.md` and `equation_registry.csv` appears here (QA: no undefined symbol).

> **N-015 rendering split (presentation only; this canonical content is unchanged).**
> The single LaTeX key was split for legibility into four placed tables, each rendered
> from the corresponding block below:
> - `notation_table.tex` (label `tab:notation`) — *Problem and population* + *GSK operator*, kept in main-text §3.1.
> - `notation_table_scaffold.tex` (label `tab:notation-scaffold`) — *ACE / ARGP* + *NLPSR* + *BSE / archive / restart*, placed with §3.3.
> - `notation_table_ism.tex` (label `tab:notation-ism`) — *ISM / eigenframe polish*, placed with §3.4–3.5.
> - `notation_table_rng.tex` equivalent (label `tab:notation-rng`) — *RNG* substream key, authored inline in the supplement's reproducibility section.

## Problem and population
| Symbol | Meaning | Source |
|---|---|---|
| $f:\mathbb{R}^D\to\mathbb{R}$ | objective (minimised) | problem |
| $D$ | dimension | `ISMGSKConfig.dim` |
| $[\ell,u]^D$ | box bounds ($\ell,u$ scalar, or per-coordinate $\ell_j,u_j$) | `ISMGSKConfig.bounds`, `bounds_matrix()` |
| $\text{MaxFES}=10^4 D$ | evaluation budget | `resolved_max_nfes()` |
| $t$ | evaluations used so far ($\text{nfes\_used}$) | `BudgetController.nfes_used` |
| $x = t/\text{MaxFES}\in[0,1]$ | budget fraction | NLPSR / schedules |
| $g$ | generation index | main loop |
| $NP_{\text{init}} = 5D$ | initial population size | `np_init_mult=5` |
| $N_{\min}$ | NLPSR floor (12 bare; **25** at $D\ge50$) | `n_min` |
| $NP(x)$ | current population size | NLPSR schedule |
| $P=\{x_i\}_{i=1}^{NP}$ | population (rows $x_i\in\mathbb{R}^D$) | `pop` array |
| $x^\*, f^\*$ | working incumbent + value | main loop |
| $x^{g\!b}, f^{g\!b}$ | **global-best** (preserved across restarts) | `global_best_x/_f` |

## GSK operator
| Symbol | Meaning | Source |
|---|---|---|
| $R_1,R_2,R_3$ | knowledge-source indices (junior: rank-neighbours; senior: top/mid/worst) | `gained_shared_junior/senior.py` |
| $s_J,s_S$ | junior/senior comparison sign: $+1$ when the compared source ($x_{R_3}$ junior, $x_{R_2}$ senior) is fitter than $x_i$, else $-1$ | `_numba_accel.py` (gsk kernel) |
| $KF$ | knowledge factor (step scale) | `KF=0.5` |
| $KR$ | knowledge ratio (per-dim update prob) | `KR=0.9` |
| $K_{\exp}$ | junior→senior dimension-schedule exponent | `Kexp=10` |
| $D_{\text{jun}}(x)=D(1-x)^{K_{\exp}}$ | # dimensions in junior phase | Kexp schedule |
| $p$ | senior partition fraction (best/worst group $=\text{round}(pNP)$) | `p_senior=0.05` |

## ACE / ARGP
| Symbol | Meaning | Source |
|---|---|---|
| $\mathcal{A}=\{a_m=(KF_m,KR_m,K_{\exp,m})\}_{m=1}^{5}$ | ACE arm pool (arm 2 = GSK-pure) | `ace_pool` |
| $\pi_m$ | ACE selection probability of arm $m$ | `ace_init_probs`, `_ace_update_probs` |
| $\omega_m$ | arm $m$ acceptance credit (EMA) | `_ace_update_probs:1193` |
| $c=0.10$ | ACE learning rate | `ace_learning_rate` |
| $\pi_{\min}=0.05$ | ACE probability floor | `ace_min_prob` |
| $W_{\text{argp}}=30$ | ARGP acceptance window | `argp_window` |
| $\tau_{\text{argp}}$ | ARGP prune threshold (0.02 / 0.010 tier) | `argp_threshold` |

## NLPSR
| Symbol | Meaning |
|---|---|
| $NP(x)=NP_{\text{init}}+(N_{\min}-NP_{\text{init}})\,x^{(1-x)}$ | tier-floored nonlinear reduction (rounded half-up) |

## BSE / archive / restart
| Symbol | Meaning | Source |
|---|---|---|
| $W$ | BSE stagnation window | `bse_window=50` |
| $\epsilon=10^{-8}$ | scale-aware stagnation tolerance | `bse_epsilon` |
| $r_{\text{rst}}=0.10$ | BSE restart fraction | `bse_restart_frac` |
| $R_{\max}$ | max BSE restarts (2, or 4 at low-D) | `bse_max_restarts` |
| $\mathcal{C}(0,\gamma)$ | Cauchy rescue draws | `cauchy_like:1412` |
| $A$ | distance-filtered diversity archive ($|A|\approx1.5\,NP_{\text{init}}$, cap 200, L2 thresh 0.05; no fitness admission) | `EliteArchive:1640` |
| $\rho_{\text{ds}}=0.25$ | deep-stall frozen-fraction trigger | `deep_stall_frac` |

## SGSM / eigenframe polish
| Symbol | Meaning | Source |
|---|---|---|
| $G\in\mathbb{R}^{D\times D}$ | signed interaction graph (decaying, $\lambda=0.95$) | `interaction_graph.py` |
| $\lambda=0.95$ | interaction decay (EMA) | `interaction_graph_decay` |
| $\kappa_{\min}=0.55$ | interaction confidence gate | `interaction_confidence_min` |
| $V$ | eigenbasis of the SGSM signed matrix (polish directions) | `_final_polish_basis:1882` |
| $s_{\text{fp}}$ | polish start fraction (~0.985) | `final_polish_start_frac` |

## RNG
| Symbol | Meaning | Source |
|---|---|---|
| 13 substreams | `init, core, ace, kexp, div, bse, arch, link, de, control, flow, basin, trust` (append-only, prefix-locked) | `_dt_rng.py` |
| $\text{init}=\text{threefry}(\text{seed})$ | stream 0 = run seed verbatim (self-init) | `_dt_rng.py`, `dt_gsk.py:166` |
