# Maintenance Guide

> **Orientation.** This page is for the maintainer keeping a healthy checkout
> over time: periodic health checks, dependency bumps, and care of the reference
> evidence. It is not about writing features — for that see the
> [Developer Guide](developer_guide.md) and
> [Extension Guide](extension_guide.md). After reading it you will know which
> commands to run on a schedule, what to verify when a dependency changes, and
> how to record new reference evidence. The three console commands below
> (`gsk-list`, `gsk-run`, `gsk-validate`) are three of the five installed entry
> points — `pyproject.toml` `[project.scripts]` also defines `gsk-family-run`
> (an alias of `gsk-run`) and `gsk-stats`; the
> [glossary](../reference/glossary.md) defines the terms.

## Regular Checks

A quick recurring pass to catch breakage early. The first command runs the test
suite; the second lists the registered optimizers and suites and confirms the
reference data is reachable; the third runs a tiny end-to-end experiment.

```powershell
python -m pytest
gsk-list --optimizers --benchmarks --references benchmarks/cec_reference_results
gsk-run --config configs/smoke.yml --root .
```

`python -m pytest` also runs the three documentation gates
(docstring coverage, doc-list resolution, and HTML link resolution); a green run
therefore confirms both code and docs are healthy. `gsk-list` should report
**fifteen** optimizer ids: the seven-method GSK-family panel (`gsk`, `agsk`,
`apgsk`, `fdb-agsk`, `atmals-gsk`, `egsk`, `dt-gsk`) — the panel every
statistical claim in the manuscript is computed over — plus eight external SOTA
baselines (`mos-cec2013lsgo`, `shade-ils`, `decc-g`, `cmaes`, `ebowithcmar`,
`jso`, `lshade`, `lshade-spacma`) that are runnable under the project's protocol
but are **not** part of that panel. Under `benchmarks:` it lists the five CEC
suites (`cec2011`, `cec2013`, `cec2013lsgo`, `cec2017`, `cec2020`), with
`sphere` reported separately under `smoke problems:`.
Add the ruff correctness lint and the scoped mypy gate to
the recurring pass as well (nothing else runs them — there is no hosted CI):

```powershell
python -m ruff check src tests scripts
python -m mypy src/gsk_family/cli src/gsk_family/runners src/gsk_family/common `
  --ignore-missing-imports --follow-imports=skip
```

Use `gsk-validate` after generating benchmark evidence to compare a results
directory against the imported reference tables:

```powershell
gsk-validate --compare results/_run_all/gsk/cec2017 benchmarks/cec_reference_results
```

`gsk-validate` is read-only: it reads both trees and reports parity, never
writing into `benchmarks/cec_reference_results/`. To re-confirm the proposed
method's migration parity on its own, run the byte-stability golden directly:

```powershell
python -m pytest tests/regression/test_dt_gsk_byte_stable.py -q
```

A failure there means a vendored `dt-gsk` module, its RNG substream layer, or
the `pub`-profile config drifted from the source project — investigate before
shipping, and never "fix" the golden by editing the pinned values. The golden
stays valid even though the **deep-stall full restart** (multi-start) is
default-on (`deep_stall_restart_enabled=True`): its `deep_stall_min_budget`
guard (default `20000`) keeps the mechanism inert at the golden's `max_nfes=3000`,
so non-stalling and tiny-budget runs are byte-identical whether the restart fires
or not — all real CEC runs (`>= 10000*D`) clear the guard.

## Dependency Updates

Numeric libraries can shift floating-point results, so treat every bump as a
parity event. When updating NumPy, SciPy, pandas, matplotlib, PyYAML, or numba:

1. Run all tests (`python -m pytest`). The regression tier is the parity
   tripwire: `tests/regression/test_validation_ladder.py` checks exact
   Python-replay and tiny reference-comparison behavior, and
   `tests/regression/test_dt_gsk_byte_stable.py` locks the `dt-gsk` migration
   golden. A library bump that changes either is a parity event.
2. Run at least one smoke experiment per optimizer — the bundled
   `configs/all_optimizers_smoke.yml` covers the full runnable set in one pass.
3. Inspect convergence traces for non-finite values.
4. Record any solver or floating-point behavior changes in
   [`docs/research/validation_report.md`](../research/validation_report.md).

Pay special attention to **SciPy** and **numba**: the statistical-analysis suite
calls `scipy.stats.wilcoxon` and `scipy.stats.friedmanchisquare` (so a SciPy
change can move p-values in the `gsk-stats` panel), and numba's LLVM JIT drives
the CEC2017 composition kernels (so a numba change can shift both timing and the
worker-memory pressure that the [worker cap](developer_guide.md#parallel-and-worker-model)
guards against).

## Reference Evidence

The imported reference tables are the ground truth for parity, so their
provenance must be traceable. Keep `benchmarks/cec_reference_results/`
read-only. The tree is laid out flat per suite and optimizer
(`benchmarks/cec_reference_results/<suite>/<optimizer>/`): summary CSVs
(`<opt>_<suite>_D<dim>.csv` plus a rollup for native-dimension suites),
`per_run.csv`, provenance files (`environment.json`, `run_config.json`,
`seed_schedule.csv`, `verification.json`, `phase0_protocol.json`), per-run
convergence curves under `curves/`, and generation logs under `gen_logs/`. Committed reference evidence exists for
exactly **three** suites: the full 7-optimizer family panel is committed for
`cec2017`, `cec2011`, and `cec2013` (each has a per-optimizer subtree under
`benchmarks/cec_reference_results/`). The other two registered suites,
`cec2020` and `cec2013lsgo`, are runnable in code (they are in
`SUPPORTED_SUITES`) but carry **no committed reference tables yet** — there is
no `benchmarks/cec_reference_results/cec2020` or `.../cec2013lsgo` tree. The
analysis suite loads the committed reference tree **first** and treats locally
reproduced `results/_run_all/` only as a fallback
(`analysis/result_loader.py::load_algorithm`). If new external evidence is
added, document:

- source project or run;
- date generated or imported;
- optimizer, suite, dimensions, and functions;
- budget and run count;
- format conversion steps.

## Documentation Upkeep

Keep the docs and their generated HTML in step. When a new document is added,
link it from [`docs/index.md`](../index.md) and from the path list in
`tests/smoke/test_documentation_commands.py` (the `test_documented_docs_exist`
gate); after any Markdown or docstring change, rebuild the HTML twins with
`python scripts/build_docs_html.py`. The HTML generator is also covered by a
smoke test, and `test_generated_html_local_links_resolve` will fail the suite if
any regenerated page links to a missing file — so always rebuild and commit the
HTML in the same change as the Markdown edit. Prefer editing existing docs over
adding new ones; renaming or deleting a listed doc breaks the doc-list gate.

## Long-Term Maintenance

Slower-moving upkeep that keeps the evidence base broad and current.

- Keep the reference parity matrix current.
- Rebuild the HTML docs after documentation changes.
- Keep generated outputs separate from imported references.
- Add deeper statistical-equivalence reports as full campaigns complete, using
  the `gsk-stats` CLI (`cli/stats.py`); its output lands under
  `results/_run_all/_analysis/<suite>/`. The panel compares the seven-algorithm
  GSK family (the six reference comparators plus `dt-gsk`).
- Regenerate the papers review pack with
  `python papers/scripts/generate_review_pack.py` after schema or curve-naming
  changes, and check `papers/DT-GSK-CEC2017-review_missing.log` for gaps; the
  pack needs no LaTeX (MiKTeX is only for the full `papers/main.tex` paper).
- Expand imported reference-comparison tables for `cec2013lsgo` and `cec2020`
  (registered in `SUPPORTED_SUITES` but carrying no committed reference tables
  yet — `cec2013` now carries the full 7-optimizer panel alongside `cec2011` and
  `cec2017`, so the committed evidence covers three suites). Recall the CEC2017
  scored set excludes `F2` (it covers `F1`, `F3`-`F30`) across D=10/30/50/100.
- When triaging DT-GSK behaviour with the diagnostics analyzer
  (`scripts/analyze_dt_diagnostics.py`), read **`ls_hit_rate`** — the fraction of
  local-search triggers that produced any improvement — as the honest measure of
  local-search usefulness. The older per-trigger **`ls_waste_frac`** overstates
  uselessness at low D (most individual triggers find nothing, yet the rare hits
  still net-help), so prefer `ls_hit_rate` when deciding whether LS is worth
  gating; a config-only ablation that cut LS ~5x at D10 left `ls_waste_frac` high
  but did **not** improve error because `ls_hit_rate` stayed `> 0`.
