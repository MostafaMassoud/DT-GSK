# Scripts

Command-line entry points for the project: convenience launchers that mirror the
reference `run_all_*.m` entry points (delegating to `gsk-run`), the documentation
builder, and a few developer utilities.

## Files

| File | Purpose |
|---|---|
| `run_all_cec2011.py` | Launch CEC2011 experiments. |
| `run_all_cec2013.py` | Launch CEC2013 experiments. |
| `run_all_cec2013lsgo.py` | Launch CEC2013LSGO native-dimension experiments. |
| `run_all_cec2017.py` | Launch CEC2017 experiments. |
| `run_all_cec2020.py` | Launch CEC2020 experiments. |
| `run_gsk_family.py` | Source-checkout run wrapper: adds `src/` to the import path, then calls `gsk-run`. |
| `run_revision_experiments.py` | Driver for the five reviewer-requested revision experiments E1-E5 (round-1 E1-E4 under D-0047/CR-0023; E5 added in round two under pre-registration Amendment A4). Writes staging under `results/_revision/`, never into `benchmarks/`; promote with `papers/scripts/promote_revision_experiments.py` / `promote_revision2_experiments.py`. Flags: `--only {E1,E2,E3,E4,E5}`, `--smoke`, `--dry-run`, `--workers`. |
| `run_e1_basis_contrast.py` | Standalone launcher for E1's coordinate-axes arm (the refinement-basis contrast at D = 50 and D = 100), kept separate because that arm drives the research hook from outside the shipped package. |
| `run_ablation.py` | DT-GSK scaffold ablation driver: full-scaffold baseline plus one cell per mechanism (ACE, NLPSR, BSE, linkage crossover, Nelder-Mead local search, elite archive) = 7 cells, with SGSM (`interaction_graph_enabled`) off in every cell. Writes one YAML per cell under `configs/_ablation/`, runs each via `gsk-run`, and outputs to `results/_ablation/<cell>/dt-gsk/<suite>/`. Flags: `--suite {cec2017,cec2011,cec2013}`, `--mode {remove-one,add-one}`, `--dimension`, `--runs` (default 25), `--workers`, `--only`, `--dry-run`. Aggregate cells afterwards with `papers/scripts/generate_ablation_matrix.py`. |
| `build_docs_html.py` | Generate the browsable HTML documentation package from Markdown and Python docstrings. |
| `validate_profile_lock.py` | Gate check that the pinned settings (parallel, backend, warmup, profile, seed policy, RNG, workers) in the smoke and validation configs have not drifted. |
| `parity_trace.py` | Developer diagnostic: dump deterministic checkpoints (raw RNG stream, initial population, per-generation best-so-far, final result) for one cell to localize any divergence from the reference. |
| `validate_egsk_vs_reference.py` | Reproducibility check: re-runs the Python EGSK port (`scipy`-SLSQP) at the committed cell's recorded seeds and verifies it byte-faithfully reproduces the promoted EGSK evidence. The committed cell **is** the SLSQP port (not a MATLAB-`fmincon` table), so this validates port/environment reproducibility, not port-vs-fmincon; reports per-cell mean/median, max abs paired difference, exact-match count, and a paired Wilcoxon p as a secondary drift signal. The one-time fmincon comparison is archived in `docs/research/egsk_validation_appendix.md` (§5). |
| `plot_convergence_from_curves.py` | Render convergence-graph PNGs from already-committed median-run curve CSVs, without re-running the optimizer (for runs done without `--convergence-graphs`). Writes `curves/graphs/Figure_F<f>_D<d>.png` under each `<results>/<optimizer>/<suite>` root. |
| `analyze_dt_diagnostics.py` | Aggregate the opt-in DT-GSK per-generation JSONL diagnostics traces (`DTTrace_*.jsonl`) into per-cell summary statistics; used with the `configs/experimental/dt_diag*.yml` campaigns. |
| `wilcoxon_reference.py` | Suite-level Wilcoxon signed-rank test pairing the Python port's per-function summary statistic against an imported reference table; reports win/tie/loss, signed rank sums, p-value, and a verdict at the chosen alpha. |
| `run_campaign.py` | Full-campaign driver: runs the seven-optimizer panel across a suite and dimension set, pinning thread counts as the published campaign pinned them. `run.py` does NOT pin threads, and D = 100 is thread-sensitive, so an unpinned re-run is not comparable to the archive. |
| `run_overlay_ablation_51.py` | Re-runs the component-isolation overlay cells at 51 repetitions, for the promoted CEC2017 D50/D100 overlay in the frozen ablation release. |
| `promote_evidence.py` | Promote a staging result tree under `results/` into an immutable, checksummed evidence release under `benchmarks/`. Releases are additive and non-superseding; this script never rewrites one. |
| `retime_comparators.py` | Re-measure comparator wall-clock under the published thread pinning, for the runtime-overhead figures, without re-running the optimizers' scored cells. |
| `recover_apgsk_perrun.py` | Reconstruct APGSK per-run records from archived summaries where the per-run file was not retained; used once, kept for provenance. |

The `run_all_*.py` scripts are thin wrappers; prefer editing the YAML files in
`configs/` for campaign changes. `validate_profile_lock.py` runs in the standard gate ladder;
`parity_trace.py` is a manual diagnostic used when investigating reference parity.
For CEC2017 F1/F12/F13 floating-point trace checks, run it with
`--benchmark-fp-mode strict` so the traced Python cell uses the fixed-order
strict evaluator.
