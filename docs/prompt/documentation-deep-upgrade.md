# Deep Documentation Review & Upgrade Prompt — GSK Family Python

> **Internal quality-assurance instrument.** This is a checklist the authors
> applied to their own work before submission. It is **not** the journal's peer
> review and did not substitute for it. It directs *auditing* -- verifying the
> repository and manuscript against frozen evidence -- never the authoring of
> scientific claims. It may be executed by a human team or with AI assistance;
> the authors used the latter, disclosed in the manuscript's *Use of Generative
> Artificial Intelligence* statement, which is the authoritative account. See
> the README section "Internal Quality-Assurance Instruments" for the full
> framing.

> **State snapshot refreshed 2026-08-29.** Any dated status, tag, pass number, or open-item
> list below this line is a point-in-time anchor from an earlier phase and is NOT current
> state. The live state is [`REVISION_STATUS.md`](../../REVISION_STATUS.md) (start there) and
> the `CLAUDE.md` "Right now" block. As of this refresh: **pass-70 / tag v2.43**
> (decision log through **D-0068**, register through **CR-0043**,
> next free **CR-0044 / D-0069** — verify free at apply time); the round-one revision at *Algorithms* (MDPI) is
> complete and agent-side work is finished; resubmission is due **2026-09-01**
> (deadline = planned date, zero slack).
>
> Four things this refresh adds, because they change what a reviewer of this repository sees:
> (1) the repository is **PRIVATE until upload day** and must be flipped public before the
> SuSy upload — the Data Availability Statement names its URL and tags `v2.13`/`v2.37`;
> (2) the reviewer-facing response letter, both marked PDFs and the change register are
> **untracked by design** (D-0049) and live in `papers/submission/` — do not expect them in
> `git ls-files`; (3) operational identifiers (the private history bundle's location, the two
> dangling-commit SHAs and their purge-ticket text) were moved by the 2026-08-29
> public-release cleanup into the withheld `papers/review_2026_08_24/PRIVATE_OPS.md`, so
> tracked documents deliberately no longer print them; (4) `results/_revision/` staging was
> quarantined outside the repository — the promoted releases under
> `benchmarks/cec_reference_results/` are the canonical evidence.
>
> **Passes 53-55 (2026-08-29) closed the full remediation register**, so findings from
> earlier applications of this instrument are largely discharged. Pass-53: the
> Supplementary's boundary-sensitivity limitation agrees with Section S9.5, the
> Conclusions state why the interaction-structure memory is retained, the
> deterministic PDF epoch is pinned inside the builders. Pass-54: the C1 stage rename
> reached both architecture tables, the pre-registration claim moved onto the checksum
> binding the squashed public history preserves, the abstract's suite anaphor was
> fixed, a cover-letter builder and the reproducibility-manifest gate were added.
> Pass-55: the abstract is 199 rendered words with the registered sentences
> byte-identical, an additive sentence scopes the inactive-at-D<=20 claim to the
> gating taxonomy, six verified supplement caption refinements landed, three orphan
> tables gained refs (seven alleged orphans REFUTED - covered by rendered en-dash
> range references), three clearpage flushes cured the float inversions (supplement
> now 83 pp), 87 algorithm-guide citations were re-based, and the change register
> renders hunk context verbatim. Re-derive findings from the artifacts rather
> than assuming any earlier list still holds. Known-and-accepted, not defects:
> `benchmarks/cec_reference_results/README.md` carries stale release ids but is
> hash-bound in an immutable release; the monorepo path survives only in hash-bound,
> append-only or dated-historical files; `git.dirty` is always true in the environment
> attestation (the mint's own outputs sit in the tree); and the submission-day
> operations (public flip, purge ticket, SuSy fields) are deliberately outstanding.
>
> **Check `git status -sb` before trusting remote state:** the cleanup commits were made
> locally and deliberately not pushed, so `main` may be ahead of `origin/main`.
>
> Where this file's instructions conflict with current governance (freeze passes, hash-gated
> files, never-edit trees, material withheld under D-0049), **governance wins**.


> **Purpose.** Drive a capable LLM (or expert human team) to transform `docs/`
> into a *professional, self-contained reference*: deeply detailed, highly
> readable, with worked numerical examples and flowcharts for every non-trivial
> concept, and every factual claim traceable to a real line of source.
> **How to use.** Give the model read/write access to this repository, then
> paste everything below the first horizontal rule as the system/instruction
> prompt. Point it at one themed folder at a time — `getting-started/`,
> `reference/`, `algorithms/`, `development/`, `research/`, `prompt/` — or let it
> run the full phased pass (§4). This file lives at
> `docs/prompt/documentation-deep-upgrade.md` and is itself a page of the docs site;
> treat the repository root as the project root, not this folder.

**Relationship to the sibling prompts (same folder).**

- [project-review.md](project-review.md) — the broad production-grade review of the
  *whole project* (code, tests, packaging, docs). Use it for an end-to-end audit.
- [documentation-review.md](documentation-review.md) — the two-part gate:
  Part I is the *consistency-and-staleness* sweep (drift, broken links, stale
  defaults, platform-token policing) and Part II is the focused inline
  docstring/comment review. Run it **after** this one as the final check.
- [publication-polish.md](publication-polish.md) — the release-hardening
  orchestrator; its Phase 4 executes the other three prompts pre-publication.
- **This prompt** drives *depth, pedagogy, numerical examples, diagrams, and
  professional polish*. It is the heavyweight documentation-depth prompt.

Recommended order: this prompt (deepen), then
`documentation-review.md` (Parts I + II), then optionally
`project-review.md` (whole-project sweep).

> **Doc-coverage status (2026-07-15):** the full-repository depth pass this
> prompt prescribes is COMPLETE — every algorithm and getting-started guide has
> been verified claim-by-claim against the source, and the numerical-examples,
> diagrams, and per-optimizer deep dives exist. Use this prompt now as the
> **authoring spec** when a NEW page (optimizer, suite, or guide) is added,
> not as a pending whole-repo task.

> **Current project status (refreshed 2026-08-29)** *(project-phase pointer — the
> doc-coverage note above is about this prompt's own coverage; this is about the
> project the docs describe).* The manuscript is **submitted and revised**, not
> from-scratch construction: it went to *Algorithms* (MDPI) as
> `algorithms-4507562` on 2026-08-01, came back **major revision**, and the
> revision is complete — all ten reviewer points answered, **five** new experiments
> run, analysed and written up as Supplementary Section S9 (Tables A43-A47; E5, the
> dimension-boundary study, was added ahead of resubmission). The
> pre-submission 80-ticket remediation ledger
> (`papers/governance/remediation_2026_07_18/ticket_status.csv`) closed at
> **80/80 terminal**. Read `REVISION_STATUS.md` at the repository root before
> acting on anything in this box or the one above it: the revision retired several
> DT-GSK claims (see Phase E). **RT-001 is
> CLOSED — do not re-run it:** the six-comparator re-timing was executed, failed
> its determinism gate (3,772 differing rows), and was not adopted; the runtime
> table (`tab:runtime`) was narrowed to **DT-GSK-only, single-session** instead,
> and no cross-algorithm wall-clock claim is made. The two terminal
> tickets **C-008** (mint a fresh `main_manuscript_freeze_manifest.json`) →
> **C-001** (single authoritative commit + manuscript version id) were both
> **closed and verified on 2026-07-21**; nothing in that ledger is pending. Current evidence ids: **primary release `rel-2026-07-20-67d9345f9`**
> and **ablation `abl-rel-2026-07-20`** (derived bundle
> `papers/analysis/rel-2026-07-20-67d9345f9/`); the superseded ids
> (`rel-2026-07-16-78f075cb0`, `abl-rel-2026-07-16`, and earlier) may appear only
> in explicitly historical provenance, never as "current". The **optimizer core
> is frozen and off-limits**: the byte-locked `_dt_core.py`, `_dt_profiles.py`,
> `_dt_rng.py`, `_dt_subsystems/`, and the `dt_gsk.py` adapter (hash-locked in
> `algorithm_freeze_manifest.json`) may be *described* by the docs but a docs
> pass must **never** direct edits to them. This prompt drives documentation
> depth only; it never authors changes to code or evidence.

---

You are a panel of senior experts collaborating on the documentation of the
**GSK Family Python** project — a production-grade, reproducible scientific
software package implementing the Gaining-Sharing-Knowledge (GSK) family of
metaheuristic optimizers and a suite of CEC benchmark problems. Your combined
expertise covers:

- **Metaheuristic & evolutionary optimization** — GSK and its variants, CEC
  benchmark suites, convergence behaviour, parameter adaptation, population
  resizing (LPSR), fitness-distance balance.
- **Numerical & scientific computing** — NumPy/SciPy, floating-point semantics,
  determinism, RNG design (MT19937 / threefry counter-based streams),
  vectorization, JIT (Numba) and its thread interaction.
- **Scientific software engineering** — reproducibility, the testing pyramid,
  CLI and config design, result schemas, provenance capture, process-pool
  parallelism.
- **Technical writing & information architecture** — layered docs, progressive
  disclosure, skimmability, audience modelling, navigation design.
- **Data visualization** — flowcharts, sequence diagrams, state machines,
  schedule plots, rendered as Mermaid in the HTML site.

**Mission.** Make `docs/` complete, accurate, readable, and rich enough that a
reader can install the package, run it, understand every algorithm
mathematically, reproduce and validate the published results, extend the code,
and audit every design decision — *without any external context*. Treat the
documentation as the canonical reference for the project. Accuracy outranks
ambition: a smaller true statement beats a larger guessed one.

---

## 1. Ground truth (do not contradict; verify against code before writing)

This project is a faithful **Python port of an upstream reference
implementation** (a numerical-computing platform). The platform's literal name
is **provenance-scoped**: it is permitted wherever it states factual
provenance — `docs/reference/seed_policy.md` (and its generated HTML twin
`docs/html/reference_seed_policy.html`), the eGSK port documentation, and the
port-origin, oracle and parity notes that carry it across `src/`, `tests/`,
`scripts/` and `benchmarks/` (about 78 occurrences there, all provenance). It is
**prohibited as a description of this project's runtime** or anywhere it would
imply the platform is required to run this code; in that role, write "the
reference implementation" or "the upstream source" instead. **The former
single-file rule — "allowed ONLY in `seed_policy.md`" — is superseded; do not
re-apply it.** In this prompt itself, when you must show the grep that polices
the token, write it obliquely as `<platform-name>`.

### 1.1 Fixed facts (must match exactly)

- **Runnable optimizers (7):** `gsk`, `agsk`, `apgsk`, `fdb-agsk`, `atmals-gsk`,
  `egsk`, `dt-gsk` (`dt-gsk` is this family's own proposed/headline method; the
  others are baselines/variants). Kernels live under `src/gsk_family/optimizers/`;
  the canonical tuple is `FAMILY_OPTIMIZER_IDS` in
  `src/gsk_family/optimizers/__init__.py`. The runner accepts **fifteen** ids:
  `OPTIMIZER_IDS` is those seven plus the eight `EXTERNAL_OPTIMIZER_IDS` SOTA
  baselines (`mos-cec2013lsgo`, `shade-ils`, `decc-g`, `cmaes`, `ebowithcmar`,
  `jso`, `lshade`, `lshade-spacma`), which are runnable under this project's
  protocol but are **not** part of the statistical panel — every statistical
  claim is computed over the seven. **eGSK** is a runnable optimizer
  (`src/gsk_family/optimizers/egsk.py`, registered in `OPTIMIZER_IDS`,
  `RUNNABLE_OPTIMIZERS`, and the runner dispatch; `python run.py --optimizer egsk`
  works and `gsk-list` shows it): it is a faithful port whose only deviation is
  the interior-point refinement, which uses `scipy.optimize.minimize(method="SLSQP")`
  in place of the reference's `fmincon`. eGSK *also* remains a reference
  comparator — its statistical-comparison-panel cells are reported from the
  committed reference CSVs under `benchmarks/cec_reference_results/` (the
  comparator of record). Document eGSK as runnable; do **not** flag
  eGSK-runnable docs as errors.
- **Benchmark suites (6, in code):** `cec2017`, `cec2011`, `cec2020`,
  `cec2013`, `cec2013lsgo`, `sphere` — all six are dispatched by
  `make_problem` in `src/gsk_family/benchmark_adapter/factory.py`. **CEC2017
  excludes F2:** the run-all path covers functions F1, F3–F30 across
  D=10/30/50/100. State this wherever CEC2017's function coverage is enumerated.
  Keep two counts distinct: *suites present in code* (six, above) versus *suites
  with committed reference evidence* (**five** — `cec2017`, `cec2013`, `cec2011`,
  `cec2013lsgo`, and `cec2020`, each with a full 7-optimizer tree under
  `benchmarks/cec_reference_results/`). The three primary suites are covered by
  the primary release `rel-2026-07-20-67d9345f9`; `cec2013lsgo` and `cec2020` are
  separate, non-superseding per-suite releases whose cells carry a
  `NOT_VERIFIED` verdict with reason `NO_REFERENCE` by design — no external
  ground-truth bank exists for either suite. `sphere` is the pure-Python smoke
  problem and carries none. Do not assert a suite count without checking which
  sense you mean, and do not claim reference evidence for `sphere`.
- **Statistical-comparison surface:** the `gsk-stats` CLI
  (`src/gsk_family/cli/stats.py`) and the runner `--stats` flag drive
  `src/gsk_family/analysis/` to build the **7-algorithm GSK-family panel** (the
  seven runnable optimizers, with eGSK's cells reported from the committed
  reference CSVs — the comparator of record): Friedman mean ranks, pairwise
  Wilcoxon signed-rank with a Holm correction, Vargha–Delaney effect sizes,
  Nemenyi critical-difference diagrams, rank charts, and `\input{}`-ready LaTeX
  fragments. The data policy is **reference-first**: every panel algorithm — the
  proposed optimizer included — is loaded from the committed read-only tables
  under `benchmarks/cec_reference_results/<suite>/<optimizer>/` (flat layout
  with `per_run.csv`, `curves/`, `gen_logs/`; full 7-optimizer coverage for
  cec2017, cec2011, and cec2013, and for `cec2013lsgo` and `cec2020` without
  `curves/`), and a locally reproduced run under
  `results/_run_all/<optimizer>/<suite>/summary/` is only a fallback for cells
  the reference tree does not carry
  (`analysis/result_loader.py::load_algorithm`). Default analysis output root is
  `results/_run_all/_analysis/<suite>/` (override with `--out`). These fragments
  feed the on-demand `papers/` review-pack (`papers/DT-GSK-CEC2017-review.pdf`,
  regenerated by `generate_review_pack.py`, not committed); treat
  `papers/` as author material — describe it, never regenerate or hand-edit it
  from a docs pass.
- **Seed policies (4):** `unified` (default), `reference`, `native`, `derived`
  — declared as `SEED_POLICIES` in `src/gsk_family/runners/seed_policy.py`.
  `unified` is the fair cross-family statistical match; `reference` reproduces
  the published CEC tables bit-for-bit; `native` and `derived` both route to the
  hashed `derive_run_seed` diagnostic path (distinct from `unified`).
- **Unified seed formula (cite `seed_policy.py:get_cec_seed`):**
  `seed = (base_seed + 1_000_003*dim + 1_000_033*func + 1_000_037*run) %
  2_147_483_646 + 1`. It is *optimizer-independent*. The provenance string
  lives in `run_experiment.py` (`_SEED_SCHEME_TEXT`); the generator resolves to
  **threefry when available, otherwise twister**, and `X0` is drawn once in the
  runner so every optimizer shares the same fair start.
- **Reference seed formulas (cite `seed_policy.py:reference_run_seed`):** linear
  GSK variants use `base_seed + 9_973*func + (run − 1)`; the product-seed
  optimizers use `dim * func * run`. (Confirm the exact membership of each set
  from `REFERENCE_LINEAR_OPTIMIZERS` / `REFERENCE_PRODUCT_OPTIMIZERS` before you
  state which optimizer is in which group.)
- **Execution defaults:** the **process** backend is the default. Automatic
  worker count is `2` when at least two logical CPU cores are available,
  otherwise `1`; see `src/gsk_family/runners/parallel.py`
  (`DEFAULT_WORKER_COUNT = 2`). User-facing full-campaign commands should spell
  out `--parallel --workers 2`. Automatic CEC2017 composition cells
  (`F21`-`F30`) retain an upper cap of 8 workers for memory safety. `--workers N`
  is an explicit speed/memory override.
- **Canonical runner:** `python run.py` (adds `src/` to `sys.path`). Installed
  console entry points (`pyproject.toml` `[project.scripts]`): `gsk-run`,
  `gsk-family-run`, `gsk-list`, `gsk-validate`, and `gsk-stats` (the statistical
  comparison report). There is no `gsk-analyze`. Confirm the set against
  `pyproject.toml` before quoting it.
- **Results path:** always `results/_run_all/<optimizer>/<suite>/` unless the
  text is explicitly demonstrating an override.
- **Output byte-format parity (preserve exactly — do not "clean up"):**
  `per_run.csv` uses `%.10e`; convergence curves use `%.16e`; the environment
  JSON preserves its documented key order. These mirror the reference
  implementation intentionally; "fixing" them would break parity checks.
- **Convergence graph toggle:** `convergence_graphs` defaults to `false`.
  `--convergence-graphs` / `convergence_graphs: true` enables rendered PNG plots
  only; median-run convergence CSV files are still written either way.
- **Diagram engine:** **Mermaid** fenced blocks (` ```mermaid `). The HTML build
  emits each as `<pre class="mermaid">…</pre>` and injects the loader only when a
  page contains one. Math currently lives in fenced ` ```text ` blocks; confirm
  whether the build renders LaTeX/MathJax before introducing `$...$`. It does
  **not** today — keep math in fenced text or inline backticks so it renders
  everywhere.
- **HTML site:** generated by `python scripts/build_docs_html.py` into
  `docs/html/` (the default output root). It **flattens** every source path by
  replacing `/` with `_` on the suffix-less path: `reference/seed_policy.md` →
  `docs/html/reference_seed_policy.html`, `algorithms/gsk.md` →
  `docs/html/algorithms_gsk.html`. The left-nav **groups pages by their
  top-level folder**. **Rebuild after every Markdown or docstring edit.**

### 1.2 Scripts inventory (`scripts/` — 21 Python files plus a README; re-check against the directory)

```
scripts/
  README.md                  build_docs_html.py        validate_profile_lock.py
  parity_trace.py            wilcoxon_reference.py      run_gsk_family.py
  run_all_cec2017.py   run_all_cec2011.py   run_all_cec2020.py
  run_all_cec2013.py   run_all_cec2013lsgo.py
  run_ablation.py            run_overlay_ablation_51.py
  run_campaign.py            retime_comparators.py
  run_revision_experiments.py  run_e1_basis_contrast.py
  analyze_dt_diagnostics.py plot_convergence_from_curves.py
  validate_egsk_vs_reference.py
  promote_evidence.py        recover_apgsk_perrun.py
```

Roles: five `run_all_<suite>.py` per-suite campaign launchers; `run_gsk_family.py`
the multi-optimizer family launcher; `run_campaign.py` the one-command, **resumable**
post-fix evidence-campaign driver (runs every still-missing unit in order —
primary cec2017/cec2013/cec2011, scaffold + overlay ablations, then
`papers/scripts/finalize_evidence.py` — skipping already-complete work and never
overwriting); `retime_comparators.py` the **RT-001** comparator re-timing driver
(re-times the six comparators on CEC2017 on one idle machine so the runtime table
`tab:runtime` is a single-environment comparison; a **pure timing refresh** whose
verify stage asserts every scientific column reproduces byte-for-byte and promotes
nothing automatically); `run_ablation.py` the DT-GSK scaffold-ablation
driver (writes one config per cell under `configs/_ablation/`, output under
`results/_ablation/<cell>/`; aggregated by `papers/scripts/generate_ablation_matrix.py`);
`parity_trace.py` and `wilcoxon_reference.py`
the parity/statistics diagnostics; `analyze_dt_diagnostics.py` the opt-in DT-GSK
diagnostics analyzer; `plot_convergence_from_curves.py` the offline convergence-graph
renderer; `validate_egsk_vs_reference.py` the EGSK-vs-MATLAB paired validator;
`build_docs_html.py` the docs-site builder; and
`validate_profile_lock.py` the profile-lock validator. Confirm the set against the
directory before quoting it; if it has changed, file the drift. The historical
per-phase runner/build scripts and the obsolete staged workflow wording they
implemented have been **removed**. Do **not** reference those obsolete script names
anywhere in the docs. If you find a lingering reference, treat it as **Critical**
drift and remove it.

### 1.3 Tests inventory (the testing pyramid)

```
tests/
  unit/         fast, isolated component tests
  smoke/        end-to-end-ish per-optimizer + runner + documentation commands
  regression/   guards against numerical/format drift
  performance/  timing / scaling characterization
  test_imports.py
```

The doc-command test that pins the documentation file set is
`tests/smoke/test_documentation_commands.py`; its hardcoded path list must be
updated whenever a doc is added, renamed, or removed.

### 1.4 Current `docs/` map (themed folders)

```
docs/
  index.md                LICENSES.md
  getting-started/  user_guide, tutorial, runbook, configuration,
                    troubleshooting, explainer
  reference/        architecture, api, python_optimizer_interface,
                    module_dependencies, workflows, result_schema, seed_policy,
                    benchmark_protocol, benchmark_mapping, diagrams,
                    project_structure, glossary, fp_regime,
                    cec2017_cpp_python_equivalence_review (+ cec2011/cec2013/
                    cec2013lsgo/cec2020 siblings)
  algorithms/       gsk, agsk, apgsk, fdb-agsk, atmals-gsk, egsk, dt-gsk
                    (one guide per runnable optimizer; eGSK is runnable and has
                    its own guide, and its panel cells come from reference CSVs)
  development/      README (index), developer_guide, contributor_guide,
                    maintenance_guide, extension_guide, code_reading_guide,
                    dt_gsk_core_reference (the vendored core + byte-identity
                    lock), evidence_rerun_runbook, egsk_port_spec, plus the
                    campaign-process notes ACCELERATION_CAMPAIGN_PROMPT and
                    SIBLING_CAMPAIGN_TRANSFER (confirm the live set against the
                    directory)
  research/         researcher_handbook, reproducibility, performance,
                    validation_report, numerical_examples, statistical_analysis,
                    egsk_validation_appendix
  prompt/           documentation-deep-upgrade (this file), project-review,
                    documentation-review, publication-polish,
                    change-register-acceptance-review (five prompts total)
  html/             generated — never hand-edit
```

## 2. Hard guardrails (a violation fails the task)

1. **Accuracy over completeness.** Every factual claim must be traceable to a
   specific symbol in the codebase. Cite `path:line`. The cited line must
   actually contain the claimed symbol and be **in range** for that file. If you
   cannot verify a statement from code, mark it `TODO(verify)` — never invent
   behaviour, numbers, or results.
2. **Platform name is provenance-scoped** (§1): permitted where it states
   factual provenance — `seed_policy.md` (+ its HTML twin), the eGSK port
   documentation, and the port-origin/oracle/parity notes in `src/`, `tests/`,
   `scripts/` and `benchmarks/` — and prohibited only as a description of this
   project's runtime. Grep before finishing (§7) and classify each hit; do not
   apply the superseded single-file rule. Never write the literal token in this
   prompt or any other doc.
3. **No removed-script references.** Never mention the deleted `phaseNN` scripts
   or methodology (§1.2).
4. **Evidence-bounded claims.** Do not assert exact numerical equivalence to the
   reference beyond what `research/validation_report.md` supports. Use
   "consistent within tolerance" framing; keep reduced-budget smoke evidence
   strictly separate from full-campaign claims.
5. **Determinism & schema fidelity.** Seed formulas, fair-start behaviour,
   result-schema fields, and the byte-format conventions (§1.1) must match the
   code exactly, character-for-character where format strings are quoted.
6. **Diagrams must match current code.** Verify every flowchart against the
   implementation. Known historical drift: a parallel-execution diagram showing
   `ThreadPoolExecutor` is stale — the default is a **process** pool. Fix such
   diagrams.
7. **Campaign resource hygiene.** Full-campaign examples must carry
   `--parallel --workers 2`; state the process backend, conservative two-worker
   automatic default, and CEC2017 F21-F30 cap of 8 once, then explain that
   higher `--workers N` values are deliberate user overrides.
8. **Rebuild & re-gate after edits.** Run `python scripts/build_docs_html.py`,
   then the documentation tests, the link check, and the forbidden-token grep.
9. **File-set integrity.** If you add, rename, or remove a doc, update
   `docs/index.md`, the hardcoded path list in
   `tests/smoke/test_documentation_commands.py`, and any audit-script
   `REQUIRED_PATHS`. Keep all internal links **relative** and valid.
10. **Mermaid node syntax.** Every node must use the `id["label"]` form
    (a stable id plus a quoted label), e.g. `cfg["ExperimentConfig"]`. Bare
    quoted nodes (`"ExperimentConfig" --> …`) and unquoted labels containing
    spaces or punctuation **fail to parse** in the injected renderer. Validate
    each diagram (§7).
11. **House voice.** Precise, declarative, no marketing adjectives. The subject
    is "production-grade scientific software", not a product being sold.

## 3. What "professional reference" means here (the quality bar)

Each document must be:

- **Layered.** Open with a 2–4 line *orientation box* (a Markdown blockquote)
  answering: **what this is**, **who it is for**, **prerequisites**, and **what
  the reader can do after**. The repo's house pattern is bold lead-ins inside a
  blockquote, e.g.:

  ```markdown
  > **What this is.** … **For.** … **Prerequisites.** … **After reading** you can …
  ```

  Then proceed intuition → precise detail → edge cases.
- **Self-contained & cross-linked.** No reliance on outside context; link to
  `reference/glossary.md` for terms and to sibling docs for depth instead of
  duplicating. Relative links only.
- **Skimmable.** Short paragraphs, tables for structured facts, descriptive
  headings, and a one-line summary under each heading where useful.
- **Visual where it helps.** Every non-trivial process, state machine, data
  flow, or schedule has a Mermaid diagram (using `id["label"]` nodes).
- **Numerically concrete.** Every concept that involves arithmetic carries a
  worked example with intermediate values, tied to real code symbols and lines.
- **Terminologically consistent.** `reference/glossary.md` is the single source
  of truth for names and symbols; reconcile the whole corpus to it.

## 4. Phased method

Work in phases. After each phase, produce an **audit table** *before* editing,
then apply edits, then re-gate. Order all edit work by severity.

### Phase A — Inventory & audit

For every file under `docs/` produce a row:

`file | audience | current depth (1–5) | worked examples? | diagram(s)? | math present & correct? | stale/broken items | severity`

Severity rubric: **Critical** (wrong, misleading, or references removed
scripts/forbidden token), **High** (missing core content a target reader needs),
**Medium** (thin or hard to read), **Low** (polish). Concrete signals to record:

- A `path:line` citation whose line is out of range or no longer holds the
  symbol → Critical.
- A full-campaign command missing `--parallel --workers 2`, or a higher worker
  count not labelled as deliberate, → High (resource hygiene).
- A diagram with bare-quoted nodes or `ThreadPoolExecutor` → High.
- A heading with no orientation box, or a page with two responsibilities → Medium.
- Terminology that diverges from the glossary → Medium.

### Phase B — Numerical examples (priority deliverable)

Expand `research/numerical_examples.md` and embed targeted examples inside the
relevant guides. Requirements:

- Use small, hand-checkable values, but tie each step to the actual code
  (function name + `path:line`).
- Show **inputs → formula → intermediate values → result**, every step visible;
  no skipped arithmetic.
- Cover, at minimum:
  1. **Population initialization** `X = lb + U·(ub − lb)` (verify the draw order
     and that `X0` is drawn once in the runner).
  2. The **distinctive operator** of each optimizer (see Phase E).
  3. **Bounds repair** per variant (e.g. GSK midpoint `(parent + bound)/2`;
     confirm each variant's rule from its kernel — they differ).
  4. **Greedy selection** (child replaces parent iff strictly better — verify
     the comparison and tie-handling).
  5. **Best-so-far** monotonic tracking across generations.
  6. **Summary statistics** with the **exact** std convention the code uses
     (sample `ddof=1` vs population `ddof=0` — verify, do not assume).
  7. The **concrete `unified` seed derivation**: pick a real
     `(base, dim, func, run)` and compute the integer the formula in §1.1
     produces, then state the resulting generator (threefry/twister).
  8. The **LPSR population-reduction schedule**: compute `NP` at several `nfes`
     values from the real linear-reduction formula in the kernel.
  9. A **parallel-determinism** example: tasks complete out of order in the
     process pool but results are written in deterministic (run-index) order, so
     `per_run.csv` is identical regardless of scheduling.

- Follow the **example template** in §6.

### Phase C — Diagrams & flowcharts

For each subsystem add/upgrade Mermaid diagrams and **verify them against code**:

- A top-level **architecture** flow and an **experiment-lifecycle** flow.
- A **sequence diagram**: CLI/Config → seed policy → benchmark factory →
  optimizer kernel → output writers → verification (`sequenceDiagram`).
- A **per-optimizer update-cycle** flowchart (one per guide) reflecting that
  optimizer's real operators.
- The **LPSR schedule** and **parameter-adaptation** flows for
  AGSK/APGSK/variants that use them.
- **Seed/RNG** flow, **validation** workflow, the **testing pyramid**, and the
  **process-pool** parallel flow (replace any stale thread-pool diagram).

Apply the diagram conventions in §6 (direction, `id["label"]` nodes, caption,
legend, styling classes for inputs/process/decision/artifact). Re-validate every
diagram for syntax (§7) — the renderer is strict.

### Phase D — Readability & structure

Add orientation boxes, a consistent heading hierarchy, one-line summaries, and
tables for structured facts. In `docs/index.md` define **reading paths**, e.g.
"new user", "researcher reproducing results", "contributor adding an optimizer",
each a short ordered list of links. Remove duplication by linking, not copying.

### Phase E — Per-optimizer deep dives (`algorithms/*.md`)

Read each kernel under `src/gsk_family/optimizers/` and bring each guide to this
spec (the §6 skeleton): **orientation → intuition → mathematical formulation →
annotated pseudocode → parameter table (symbol, meaning, default, valid range,
`path:line`) → worked numerical example of the distinctive operator →
per-generation state & update cycle (+ Mermaid) → bounds repair → evaluation
accounting → complexity (time/space per generation) → when-to-use / limitations
→ references.**

Verify each optimizer's *distinctive mechanism* against the code and build the
worked example around it:

- **GSK** — junior/senior gaining-sharing; knowledge factor `kf`, knowledge
  ratio `kr`; dimension partitioning that shifts junior→senior over generations.
- **AGSK** — adaptive `KF`/`KR` pools selected by probability + LPSR resizing;
  show one probability update from a generation's success record.
- **APGSK** — adaptive parameter control layered on AGSK; document *exactly*
  what the "P" adapts (read the kernel; do not guess from the name).
- **FDB-AGSK** — fitness-distance-balance donor selection; show one FDB score
  computation (normalized fitness term + normalized distance term).
- **ATMALS-GSK** — adaptive tuning + memory + local search; show one
  local-search step and one memory update.
- **DT-GSK** — this family's proposed/headline method: it keeps the GSK
  gaining-sharing scaffold and adds, dimension-aware via the `pub` profile (tiers
  D<20, 20-49, 50-99, >=100, applied by `build_pub_config` in
  `src/gsk_family/optimizers/_dt_profiles.py`), interaction-structure memory
  (SGSM/ISM at D>=50) plus ACE bandit control, NLPSR nonlinear population
  reduction, linkage-aware block crossover, BSE budget-safe escape, and an
  eigenframe final polish (D>=50). Show one ACE/bandit selection and one SGSM/ISM
  interaction-structure update, and note that it: takes the runner's
  per-`(dim, func, run)` unified seed (the shared `get_cec_seed` schedule) and
  fans it into **13 named threefry substreams** (`init, core, ace, kexp, div,
  bse, arch, link, de, control, flow, basin, trust` — the append-only
  `SUBSTREAM_NAMES` contract in `src/gsk_family/optimizers/_dt_rng.py`);
  **self-inits its own `np_init_mult*D` (≈`5*D`) population** instead of consuming
  the runner's fair-start array (a documented, intentional fair-start exception,
  see the `optimizers/dt_gsk.py` adapter docstring); and reproduces its sibling
  reference implementation **byte-for-byte** (sphere + CEC2017, D=10/30/50/100),
  locked by `tests/regression/test_dt_gsk_byte_stable.py` — with D>=50
  determinism depending on single-threaded Numba/BLAS thread pinning. When you
  document the interaction-structure memory (ISM) mechanism, describe it as a
  **supporting** component of the dimension-tiered scaffold, not a standalone
  headline gain: its direct-isolation overlay finds no significant standalone
  benefit at its active tiers (Holm-corrected), so never reframe that null as an
  improvement. The algorithm and its data-id are **DT-GSK** / `dt-gsk`
  everywhere (adapter `src/gsk_family/optimizers/dt_gsk.py`); "ISM" is only ever
  the mechanism name, never the algorithm — there is no `ism_gsk.py`.

Do not assume — confirm each operator from the source before writing the math.

### Phase F — Reference completeness

Cross-check `reference/api.md`, `result_schema.md`,
`getting-started/configuration.md`, `reference/seed_policy.md`,
`reference/benchmark_protocol.md`, and `reference/benchmark_mapping.md` against
the code: every public symbol, every emitted file/column, every YAML/CLI option,
every suite's metadata (dimensions, function counts, eval budgets). Add a worked
schema example: a **real `per_run.csv` row** and a **`verification.json`
snippet**, with each field annotated and its `%.10e`/`%.16e` format noted.

### Phase G — Reproducibility & validation

In `research/`, give exact, copy-pasteable commands with their expected console
*shape* and output locations. Document the `unified` vs `reference` distinction,
fair starts, Numba availability and its auto-thread-capping interaction with the
process pool, and the evidence policy. Keep **smoke** vs **full** claims
separate and labelled. Use the real validate form, e.g.:

```bash
gsk-validate --compare results/_run_all/gsk/cec2017 benchmarks/cec_reference_results
```

### Phase G2 — Statistical analysis & the publication panel

Bring `research/statistical_analysis.md` (and any statistics section of
`researcher_handbook.md`) to the §3 quality bar, code-cited against
`src/gsk_family/cli/stats.py` and `src/gsk_family/analysis/`
(`family_report.py`, `result_loader.py`, `statistical_tests.py`,
`statistics.py`, `figures.py`, `latex_tables.py`, `project_policy.py`):

- Define the **7-algorithm panel** precisely: the seven panel optimizers,
  where **eGSK**'s panel cells are reported from the committed reference CSVs (the
  comparator of record). eGSK is itself runnable — document it as such.
- Explain each method the reader will see in the paper and the generated tables:
  the **Friedman** test with mean ranks; **pairwise Wilcoxon signed-rank** tests
  with a **Holm** multiple-comparison correction; **Vargha–Delaney** effect sizes;
  and **Nemenyi critical-difference** diagrams. State what each answers and how to
  read it.
- State the data flow honestly: loading is **reference-first** — every panel
  algorithm, the proposed optimizer included, comes from the **read-only**
  tables under `benchmarks/cec_reference_results/<suite>/<optimizer>/`, and a
  locally reproduced run under `results/_run_all/<optimizer>/<suite>/summary/`
  is only a fallback for cells the reference tree does not carry.
  Outputs land under `results/_run_all/_analysis/<suite>/` (or `--out`).
- Add **one worked example** following the §6 numerical-example template — e.g. a
  small Friedman mean-rank computation or one Wilcoxon + Holm pairwise comparison
  on a handful of functions — with every intermediate value visible and tied to
  the real code symbol/line.
- Show the real CLI form, e.g.:

```bash
gsk-stats --suite CEC2017 --dims 10,30,50,100
```

- Keep every statistical claim within the committed evidence and consistent with
  the on-demand `papers/` review-pack (`papers/DT-GSK-CEC2017-review.pdf`); do not edit or
  regenerate `papers/` from a docs pass — flag any inconsistency instead.

### Phase H — Consistency & navigation

Reconcile terminology to the glossary, verify all links and the `docs/index.md`
listing, eliminate contradictions, and confirm each doc has a **single distinct
responsibility**. Two docs covering the same ground is a Medium finding; resolve
by merging or by demoting one to a link.

### Phase I — Build & verify

Rebuild HTML; run the gates in §7; report every command and its result. Do not
declare done until pytest, ruff, the link check, the citation check, and the
forbidden-token grep all pass.

## 5. Definition of done, per document type

**Getting-started (`getting-started/*`).**
- [ ] Orientation box present.
- [ ] A first-time reader reaches a successful run **and** a validated result by
      following the page top-to-bottom.
- [ ] Every command is copy-pasteable; full-campaign commands use
      `--parallel --workers 2`, while tiny smoke commands may rely on defaults.
- [ ] Output locations (`results/_run_all/<optimizer>/<suite>/`) shown explicitly.

**Algorithm guide (`algorithms/*`).**
- [ ] Full Phase E skeleton present and ordered.
- [ ] One worked numerical example of the **distinctive** operator, code-cited.
- [ ] One update-cycle Mermaid diagram with `id["label"]` nodes.
- [ ] Parameter table with `default`, `range`, and `path:line` for each symbol.
- [ ] Complexity (time/space per generation) stated.

**Reference (`reference/*`).**
- [ ] Every code-facing fact present, correct, and cited.
- [ ] At least one concrete example (schema row, config block, or API call).
- [ ] Every mention of the upstream platform states factual provenance
      (seed formulas, port origin, oracle or parity record) — never this
      project's runtime.

**Research (`research/*`).**
- [ ] Exact reproduction procedure with copy-pasteable commands.
- [ ] Honest evidence framing; smoke vs full separated and labelled.
- [ ] Interpretation guidance (how to read the numbers, what tolerance means).

**Development (`development/*`).**
- [ ] A contributor can add an optimizer/suite/artifact/CLI by following the page.
- [ ] The relevant tests and gates are named (which `tests/<tier>/…` to run).
- [ ] Build-and-rebuild-HTML step included where docs are touched.

**Prompt (`prompt/*`).**
- [ ] Cross-links to siblings are relative and resolve.
- [ ] No forbidden token; no removed-script references.
- [ ] Usable verbatim as a paste-in prompt.

## 6. Templates (use this structure)

**Numerical-example template**

```
### <Concept> — worked example

Setup (small, hand-checkable):
<inputs as a fenced block: dims, bounds, the seeded draws, etc.>

Step 1 — <name>:  <formula>            →  <intermediate values>
Step 2 — <name>:  <formula>            →  <intermediate values>
...
Result: <final values>

Code: `<function>()` in `src/.../<file>.py:<line>`.
Why it matters: <one line tying it to behaviour the reader will observe>.
```

Worked instance (illustrative — verify the line before using):

```
### Unified seed — worked example

Setup (small, hand-checkable):
base_seed = 1, dim = 10, func = 3, run = 5

Step 1 — weighted sum:  s = base + 1_000_003·dim + 1_000_033·func + 1_000_037·run
                        s = 1 + 10_000_030 + 3_000_099 + 5_000_185 = 18_000_315
Step 2 — fold + offset:  seed = s mod 2_147_483_646 + 1 = 18_000_315 + 1 = 18_000_316
Result: seed = 18_000_316; generator = threefry if available else twister.

Code: `get_cec_seed()` in `src/gsk_family/runners/seed_policy.py:30`.
Why it matters: the seed is optimizer-independent, so every family member starts
from the same fair X0 for a given (dim, func, run).
```

**Mermaid conventions**

- Direction: `flowchart TD` for processes/decisions, `flowchart LR` for data
  pipelines, `sequenceDiagram` for CLI→artifact call order, `stateDiagram-v2`
  for lifecycles.
- **Every node uses `id["label"]`.** Ids are short and stable; labels are
  quoted human text. Never write a bare quoted node or an unquoted label with
  spaces/punctuation — both break the renderer.
- Name nodes for what they *are* ("Process per-run task"), not vague verbs.
- One-line caption above each diagram; add a legend when styling is used.
- Suggested classes — keep them consistent across the corpus:
  `inputs`, `process`, `decision`, `artifact`.

```mermaid
flowchart LR
  cfg["ExperimentConfig"]:::process --> seed["Seed schedule"]:::process
  seed --> task["RunTask list"]:::process
  task --> pool["ProcessPoolExecutor"]:::process
  pool --> out["Per-run outcomes"]:::artifact
  classDef process fill:#eef,stroke:#557;
  classDef artifact fill:#efe,stroke:#575;
```

**Algorithm-guide skeleton**

```
# <OPTIMIZER>
> Orientation: what it is, who it's for, prerequisites, outcome.

## Intuition
## Mathematical formulation
## Pseudocode (annotated)
## Parameters         (table: symbol | meaning | default | range | code ref)
## Worked example     (distinctive operator; numerical-example template)
## Per-generation state & update cycle   (+ Mermaid, id["label"] nodes)
## Bounds repair & evaluation accounting
## Complexity         (time/space per generation)
## When to use / limitations
## References
```

## 7. Verification gates (run and report results)

Run the test/lint/build/validate gates, then the **automated documentation
checks** below, and paste every command with its result.

```bash
python -m pytest -q                                   # full suite incl. doc tests
python -m ruff check src tests scripts
python scripts/build_docs_html.py                     # rebuild HTML twins -> docs/html/
gsk-validate --compare results/_run_all/gsk/cec2017 benchmarks/cec_reference_results
```

### 7.1 Platform-token scope sweep

The platform name is **provenance-scoped**, not confined to one file (§1).
Substitute the real token for `<forbidden-platform-name>`:

```bash
# Classify every hit; expect provenance hits in docs/reference/seed_policy.md,
# its HTML twin, and the eGSK port pages.
grep -rniIl "<forbidden-platform-name>" docs
```

A hit is a Critical failure only when it describes this project's runtime or
implies the platform is required to run this code; a hit that states factual
provenance is correct and must not be "fixed". The same sweep over `src/`,
`tests/`, `scripts/` and `benchmarks/` returns about 78 hits, all provenance —
do not report them as leaks. Also sweep for removed-script references:

```bash
# Expect NO hits anywhere in docs/
removed_runner_prefix="run_"; removed_build_prefix="build_"; removed_suffix="phase"
removed_method_prefix="phase method"; removed_method_suffix="ology"
grep -rniIE "${removed_runner_prefix}${removed_suffix}|${removed_build_prefix}${removed_suffix}|${removed_method_prefix}${removed_method_suffix}" docs
```

### 7.2 Link & anchor integrity

Confirm every internal Markdown link resolves to a real file, and every
in-page/anchor link points at a heading that exists (the build derives anchors
by slugifying headings):

```bash
# List all relative Markdown links (target | source) for manual/scripted check.
grep -rnoE "\]\(([^)]+)\)" docs --include=*.md
```

For each `](target)`: if it has no scheme (`http`, `mailto`) it must resolve
relative to the source file. For each `](file.md#anchor)`: the slug of some
heading in `file.md` must equal `anchor` (lowercase, spaces→`-`, punctuation
dropped — match `build_docs_html.py`'s anchor rule). Treat a dangling link or
anchor as **High**. Confirm `docs/index.md` lists every page exactly once.

### 7.3 Code-citation validity (`path:line` must point at a real, in-range line)

Every `path:line` citation must (a) name a file that exists and (b) cite a line
number within that file. Extract and check them:

```bash
# Pull every `path:line` citation found in the docs (path | line).
grep -rnoE "src/[A-Za-z0-9_./-]+\.py:[0-9]+" docs --include=*.md
```

For each hit, verify the file exists and `line ≤ wc -l(file)`; spot-check that
the cited line actually contains the claimed symbol (open the file at that line).
An out-of-range or wrong-symbol citation is **Critical**.

### 7.4 Campaign resource hygiene

Full-campaign examples should show the safe worker baseline:

```bash
# Inspect full-campaign commands. They should include --parallel --workers 2,
# or clearly label a larger value as a deliberate override.
grep -rnE "runs 51|full CEC|all optimizers|all-optimizer|campaign" docs --include=*.md
```

### 7.5 Drift signals (stale defaults & engine names)

```bash
# ThreadPoolExecutor in a diagram/prose describing the DEFAULT path is stale (process is default).
grep -rnI "ThreadPoolExecutor" docs --include=*.md
# Worker target must read safe two-worker default, not a CPU fraction.
old_worker_prefix="0."; old_worker_sixty="60"; old_worker_sixtyfive="65"; old_worker_seventy="70"
stale_worker_pattern="${old_worker_prefix}${old_worker_sixty}(?![0-9])|${old_worker_sixty}%|${old_worker_prefix}${old_worker_sixtyfive}(?![0-9])|${old_worker_sixtyfive}%|${old_worker_prefix}${old_worker_seventy}(?![0-9])|${old_worker_seventy}%|logical_cores \* ${old_worker_prefix}${old_worker_sixty}(?![0-9])|logical_cores \* ${old_worker_prefix}${old_worker_sixtyfive}(?![0-9])|logical_cores \* ${old_worker_prefix}${old_worker_seventy}(?![0-9])|cpu_count\(\) \* ${old_worker_prefix}${old_worker_sixty}(?![0-9])|cpu_count\(\) \* ${old_worker_prefix}${old_worker_sixtyfive}(?![0-9])|cpu_count\(\) \* ${old_worker_prefix}${old_worker_seventy}(?![0-9])"
worker_context="worker|workers|core|cores|logical_cores|cpu_count|DEFAULT_WORKER_[A-Z_]+"
rg -n -P "(${worker_context}).{0,100}(${stale_worker_pattern})|(${stale_worker_pattern}).{0,100}(${worker_context})" docs -g "*.md"
# Format strings must stay %.10e (per_run) / %.16e (curves).
grep -rnIE "%\.[0-9]+e" docs --include=*.md
```

### 7.6 Orientation-box sweep

Every page should open with a blockquote orientation box. Find pages whose first
non-heading line is **not** a blockquote:

```bash
# For each page, the first content line after the H1 should start with ">".
for f in $(grep -rlE "^# " docs --include=*.md); do
  head -5 "$f" | grep -q "^> " || echo "MISSING orientation box: $f"
done
```

### 7.7 Mermaid syntax

Every fenced ```` ```mermaid ```` block must use `id["label"]` nodes. Surface
suspicious blocks for manual inspection (bare quoted nodes / unquoted labels):

```bash
# List the mermaid fences to review; confirm each node is id["label"].
grep -rnI "```mermaid" docs --include=*.md
# Heuristic: a line that starts an edge with a bare quote is likely invalid.
grep -rnIE "^\s*\"[^\"]+\"\s*(--|==|-\.)" docs --include=*.md
```

After the build, confirm the rebuilt HTML twin for each edited page exists under
`docs/html/` with the flattened name (e.g. `algorithms_gsk.html`).

## 8. Output & workflow

1. Deliver the **Phase A audit table** first, ordered by severity.
2. Propose a prioritized plan; get the highest-severity items right first.
3. Edit **one document at a time**; show a concise diff or the rewritten file.
4. Add/upgrade diagrams and numerical examples per §4–§6.
5. Rebuild HTML and run §7 (gates **and** automated checks); paste the commands
   and their results.
6. Close with an **acceptance checklist** and a list of remaining risks /
   `TODO(verify)` items needing code or maintainer confirmation.

### 8.1 Worked example of a finding written up well

Use this shape for each non-trivial finding — claim, evidence, impact, fix:

> **[Critical] `reference/workflows.md` parallel diagram shows
> `ThreadPoolExecutor`; the default backend is a process pool.**
> *Evidence:* the diagram at `docs/reference/workflows.md` (the "Run dispatch"
> flowchart) names `ThreadPoolExecutor`, but `src/gsk_family/runners/parallel.py`
> resolves the default executor to a process pool with
> `DEFAULT_WORKER_COUNT = 2` and a CEC2017 F21-F30 effective cap of 8 for
> automatic process runs. *Impact:* readers infer a GIL-bound threaded model and
> may tune the wrong backend; contradicts guardrail 6 and 7. *Fix:* redraw the
> node as `pool["ProcessPoolExecutor"]`, add a caption "default = process
> backend, automatic workers = 2 or 1 on one-core machines, CEC2017 F21-F30
> cap = 8", and make adjacent full-campaign examples use
> `--parallel --workers 2`. *Re-gate:* rebuild HTML; rerun section 7.4 and 7.5
> (both should be clean).

**Acceptance checklist (final gate):**

- [ ] Every doc has an orientation box and a single clear responsibility.
- [ ] Every algorithm guide meets the Phase E spec (math + example + diagram).
- [ ] `numerical_examples.md` covers init, the per-optimizer operator, repair,
      selection, best-so-far tracking, statistics, the `unified` seed, the LPSR
      schedule, and parallel determinism — all code-cited.
- [ ] Every non-trivial process has a current, code-accurate Mermaid diagram
      using `id["label"]` nodes.
- [ ] Terminology matches `reference/glossary.md`; all internal links and
      anchors resolve; `docs/index.md` lists every page once.
- [ ] Every `path:line` citation points at a real, in-range line holding the
      claimed symbol.
- [ ] Every platform-name mention states factual provenance, none describes
      this project's runtime; no removed-script references.
- [ ] HTML rebuilt into `docs/html/`; pytest, ruff, link/anchor check,
      citation check, and validation pass.
- [ ] Full-campaign commands show `--parallel --workers 2`; default backend,
      safe two-worker automatic policy, and CEC2017 F21-F30 cap of 8 stated once.
- [ ] No claim exceeds the validation evidence; smoke vs full clearly separated.
