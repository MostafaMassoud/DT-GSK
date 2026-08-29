# Configs

This directory contains YAML experiment configurations for `gsk-run`.

## Files

| File | Purpose |
|---|---|
| `smoke.yml` | Fast smoke run for local verification. |
| `all_optimizers_smoke.yml` | Fast all-optimizer sphere smoke run with warmup and profiling metadata. Pins the `thread` backend (see [Parallel backend](#parallel-backend)). |
| `all_optimizers_cec2017_reduced.yml` | Reduced CEC2017 all-optimizer parity run for quick cross-kernel checks. |
| `golden_validation_smoke.yml` | Reduced CEC2017 golden-validation smoke campaign against imported reference summaries. |
| `performance_campaign_smoke.yml` | Serial-versus-parallel performance smoke campaign with deterministic artifact comparison. |
| `all_cec2011.yml` | CEC2011 campaign template. |
| `all_cec2017.yml` | CEC2017 campaign template. |
| `agsk_cec2020.yml` | AGSK-focused CEC2020 campaign template. |
| `family_cec2011.yml` | Seven-optimizer family panel on CEC2011. |
| `family_cec2013.yml` | Seven-optimizer family panel on CEC2013. |
| `family_cec2013lsgo.yml` | Seven-optimizer family panel on CEC2013LSGO (native dimensions). |
| `family_cec2017.yml` | Seven-optimizer family panel on CEC2017, the primary suite. |
| `family_cec2020.yml` | Seven-optimizer family panel on CEC2020. |
| `baselines_cec2011.yml` | External SOTA baselines on CEC2011. |
| `baselines_cec2013.yml` | External SOTA baselines on CEC2013. |
| `baselines_cec2013lsgo.yml` | External SOTA baselines on CEC2013LSGO (SHADE-ILS, MOS, DECC-G). |
| `baselines_cec2017.yml` | External SOTA baselines on CEC2017. |
| `baselines_cec2020.yml` | External SOTA baselines on CEC2020. |
| `dtgsk_cec2013lsgo.yml` | DT-GSK alone on CEC2013LSGO at native dimensions. |
| `dtgsk_lsgo_smoke.yml` | Reduced CEC2013LSGO smoke run for the LSGO path. |

## Subfolders

| Folder | Purpose |
|---|---|
| `_ablation/` | Generated per-cell ablation configs (`baseline.yml`, `no_<mechanism>.yml`, `only_<mechanism>.yml`, ...) written by `scripts/run_ablation.py`. Regenerated on each ablation launch — do not hand-edit; change `scripts/run_ablation.py` instead. |
| `experimental/` | Opt-in diagnostics campaigns: `dt_diag.yml` / `dt_diag_15run.yml` (per-generation DT-GSK JSONL traces, analyzed by `scripts/analyze_dt_diagnostics.py`) and `dt_d10_scored.yml` (canonical D10 scored reproducer). |
| `publish/` | Publication campaign configs; `dt_gsk_cec2017_final.yml` is the canonical DT-GSK CEC2017 paper run. |
| `_recover/` | One-off recovery configs for regenerating lost reference cells (`apgsk_cec2017_recover.yml`, used with `scripts/recover_apgsk_perrun.py`); kept for provenance. |

Run a config from the project root with:

```powershell
gsk-run --config configs/smoke.yml --root .
```

Use `--root .` so relative paths inside the config resolve inside this project
folder.

Convergence graph PNGs are off by default for direct CLI runs. The shipped
campaign configs set `convergence_graphs: true` explicitly where rendered PNG
plots are wanted. Omit `--convergence-graphs` for direct CLI CSV-only output,
or set `convergence_graphs: false` in a copied config.

## Parallel backend

The campaign templates — `all_cec2017.yml`, `all_cec2011.yml`, `agsk_cec2020.yml`,
and `all_optimizers_cec2017_reduced.yml` — use the default **process** backend,
the right choice for real runs: true multi-core, and self-healing if a worker
crashes.

The three smoke and validation profiles — `all_optimizers_smoke.yml`,
`golden_validation_smoke.yml`, and `performance_campaign_smoke.yml` — deliberately
pin the **thread** backend with `workers: 2`, which keeps their tiny CI artifacts
byte-for-byte deterministic. Avoid the thread backend for full campaigns; it does
not scale past a few workers.
