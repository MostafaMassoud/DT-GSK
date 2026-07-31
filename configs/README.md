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

## Subfolders

| Folder | Purpose |
|---|---|
| `_ablation/` | Generated per-cell ablation configs (`baseline.yml`, `no_<mechanism>.yml`, `only_<mechanism>.yml`, ...) written by `scripts/run_ablation.py`. Regenerated on each ablation launch — do not hand-edit; change `scripts/run_ablation.py` instead. |
| `experimental/` | Opt-in diagnostics campaigns: `dt_diag.yml` / `dt_diag_15run.yml` (per-generation DT-GSK JSONL traces, analyzed by `scripts/analyze_dt_diagnostics.py`) and `dt_d10_scored.yml` (canonical D10 scored reproducer). |
| `publish/` | Publication campaign configs; `dt_gsk_cec2017_final.yml` is the canonical DT-GSK CEC2017 paper run. |

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
