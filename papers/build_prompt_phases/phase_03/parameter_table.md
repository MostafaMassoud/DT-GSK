# DT-GSK — Frozen Parameter Table (`pub` profile)

**Phase 3 deliverable** (Phase 3 task 4/14; canonical source for `parameter_table.tex`).
These are the **frozen** run parameters of the shipped `pub` profile
(`_dt_profiles.build_pub_config(dim)`). Values are the tier-resolved `pub` settings; where
a value varies by dimension tier the four tiers `D<20 / 20–49 / 50–99 / ≥100` are shown.
Dataclass defaults (`_dt_core.ISMGSKConfig`) are the bare fallback and are cited for
provenance. **No tuning is required or permitted at run time** beyond `options.values`
advanced overrides. Freeze recorded in `algorithm_freeze_manifest.json`.

## Run-level (reserved; from problem/options, never from `values`)
| Parameter | Value | Source |
|---|---|---|
| profile | `"pub"` (always) | `dt_gsk.py:157` |
| generator | `threefry`, unified shared seed `get_cec_seed` | `_dt_rng.py`, seed_policy |
| MaxFES | `10^4·D` | `resolved_max_nfes` |
| bounds | scalar `(ℓ,u)` or per-coordinate `(ℓ_j,u_j)` | `dt_gsk.py:79` |
| $NP_{\text{init}}$ | `5·D` | `np_init_mult=5` |

## Core GSK operator
| Parameter | `pub` value | Dataclass default | Notes |
|---|---|---|---|
| KF | 0.5 (ACE arm-controlled) | `KF=0.5` | ACE adapts per-individual |
| KR | 0.9 (ACE arm-controlled) | `KR=0.9` | block mask when linkage on |
| $K_{\exp}$ | 10 (ACE arm-controlled) | `Kexp=10.0` | junior-dim schedule |
| $p$ (senior) | 0.05 (0.15 split-bottom at D≥50) | `p_senior=0.05` | `p_senior_split_enabled` at D≥50 |

## NLPSR
| Parameter | `pub` value | Notes |
|---|---|---|
| schedule | `lpsr` / nonlinear `x^(1-x)` | `psr_schedule` |
| $N_{\min}$ | 25 at D≥50 (12 bare) | tier floor |
| $\alpha$ | 1.0 | `psr_alpha` |

## ACE / ARGP
| Parameter | `pub` value | Notes |
|---|---|---|
| arm pool | 5 arms `(KF,KR,Kexp)`; arm 2 = GSK-pure `(0.5,0.9,10)` | `ace_pool` |
| init probs | `(0.05,0.05,0.45,0.05,0.40)` | `ace_init_probs` |
| learning rate $c$ | 0.10 | `ace_learning_rate` |
| prob floor $\pi_{\min}$ | 0.05 | `ace_min_prob` |
| memory mode | `single` (D<20) → `top_bottom` (D≥20) | `ace_memory_mode` |
| DE arm | off (D<20) → on (D≥20) | `ace_de_entry` |
| ARGP window / threshold | 30 / 0.02 (0.010 at D≥50), warmup 0.15 | `argp_*` |

## Linkage crossover
| Parameter | `pub` value | Notes |
|---|---|---|
| block size | 5 (D<50) / 10 (D≥50) | `linkage_block_size_by_dim` |
| mix prob | 0.70 (D<20) / 0.40 (mid) / 0.70 (D≥50) | `linkage_block_mix_prob` |
| refresh period | 20 gens | `linkage_block_refresh_period` |

## BSE / archive / deep-stall
| Parameter | `pub` value | Notes |
|---|---|---|
| trigger mode | `stagnation` (D<20) / `triple` (D≥20) | `bse_trigger_mode` |
| window $W$ | 50; signal window 10 | `bse_window`, `bse_signal_window` |
| $\epsilon$ | 1e-8 | `bse_epsilon` |
| restart frac $r_{\text{rst}}$ | 0.10 (0.30 low-D / D30) | `bse_restart_frac` |
| max restarts $R_{\max}$ | 2 (4 at D<20, 2 at D≥100) | `bse_max_restarts` |
| acceptance / diversity floor | 0.10 / 0.35 | `bse_acceptance_floor`, `bse_diversity_floor_frac` |
| archive size / dist | 1.5·NPinit, L2 0.05, cap 200 | `arch_*` |
| deep-stall | on; frac 0.25; min-budget 20000; cooldown 0.15; stop 0.9 | `deep_stall_*` |

## SGSM / eigenframe polish (D≥50)
| Parameter | `pub` value | Notes |
|---|---|---|
| enabled | D≥50 (`interaction_graph_min_dim=50`) | `interaction_graph_enabled` |
| decay $\lambda$ | 0.95 | `interaction_graph_decay` |
| learning rate $\eta$ | 1.0 | `interaction_graph_lr` |
| refresh period / warmup | 5 gens / 0.10 | `interaction_graph_*` |
| confidence gate $\kappa_{\min}$ | 0.35 (linkage 0.35, LS 0.45; base 0.55 superseded by the adaptive triple at D≥50) | `interaction_confidence_min` |
| block size range | 2–10 | `interaction_block_{min,max}_size` |
| final polish start | 0.96 | `final_polish_start_frac` |

## D≥100 controllers
| Parameter | `pub` value |
|---|---|
| A1 late-accept clip / A2 frozen-broaden / FC4 link-random-mix | enabled (tier-tuned scalars) |
| basin memory / SP-NLPSR floor / TERRA budget policy | enabled |

> **Reproducibility:** the exact resolved config for any `D` is
> `build_pub_config(D, ...)`; this table summarises the `_dt_profiles.py` override blocks
> (`_PUB_COMMON`, `_PUB_D_LT_20`, `_PUB_D_20_TO_49`, `_PUB_D_GE_50` + SGSM/adaptive extras,
> `_PUB_D_GE_100_EXTRA`). The profile builder is locked against a source oracle by
> `tests/unit/test_dt_profiles.py`; any drift fails CI.
