# Documentation Review Prompt

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
> the `CLAUDE.md` "Right now" block. As of this refresh: **pass-56 / tag v2.29**
> (decision log through **D-0061**, register through **CR-0036**,
> next free **CR-0037 / D-0062** — verify free at apply time); the round-one revision at *Algorithms* (MDPI) is
> complete and agent-side work is finished; resubmission is due **2026-09-01**
> (deadline = planned date, zero slack).
>
> Four things this refresh adds, because they change what a reviewer of this repository sees:
> (1) the repository is **PRIVATE until upload day** and must be flipped public before the
> SuSy upload — the Data Availability Statement names its URL and tags `v2.13`/`v2.29`;
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


> **Two parts.** Part I (below) is the prose/consistency-and-staleness gate for
> `docs/` and Markdown. Part II (appended) is the inline docstring & comment
> review for code, tests, scripts, and configs.

> **What this page is.** A reusable, paste-in prompt for auditing whether the
> docs are *complete, internally consistent, and accurate to the current code*.
> **Who it is for.** Maintainers running a documentation consistency-and-drift
> review (not a depth/pedagogy pass). **What it produces.** A severity-ordered
> findings report with `file:line` citations, evidence, and suggested fixes.
> **See also.** The deeper enhancement prompt
> [documentation-deep-upgrade.md](documentation-deep-upgrade.md) (depth, worked
> examples, diagrams) and the whole-project audit prompt
> [project-review.md](project-review.md); the inline docstring/comment review
> is **Part II of this file** (merged from the former standalone prompt).
> All siblings live in this same `docs/prompt/`
> folder. Run *this* consistency prompt **last**, as the final gate, after any
> depth or inline-documentation pass has landed.

Use this prompt when you need to confirm that the Python project documentation is
complete, readable, internally consistent, and faithful to the code as it exists
*today* — not to an older revision. This prompt is deliberately mechanical: it
favors copy-pasteable checks, explicit pass/fail criteria, and reproducible
evidence over open-ended judgement. The companion `documentation-deep-upgrade.md`
handles depth, numerical worked examples, and diagrams; keep the two concerns
separate.

## Current project status (2026-07-20)

> **Read this first — it dates the facts below.** This prompt is *process-generic*
> and stays valid across releases; the project it audits is not. As of
> **2026-07-20** the **DT-GSK** manuscript is **built** and in **final
> pre-submission remediation** (not from-scratch construction). Re-verify against
> the repo if this date has moved.
>
> - **Remediation ledger — 80/80 terminal** (70 `closed_verified` + 10
>   `superseded_with_evidence`; no ticket is open)
>   (`papers/governance/remediation_2026_07_18/ticket_status.csv`, column
>   `lifecycle_status`). All quality
>   gates are **green** (build hygiene, cross-format PDF/DOCX/JSON parity,
>   provenance-claim, citation-usage, environment attestation).
> - **RT-001 is CLOSED — do not re-run it.** The six-comparator re-timing was
>   executed, **failed** its determinism gate (3,772 differing rows), and was not
>   adopted; the runtime table (`tab:runtime`) was narrowed to **DT-GSK-only,
>   single-session** instead, and no cross-algorithm wall-clock claim is made.
>   No evidence task is open. The two **terminal** tickets **C-008** (mint a fresh
>   manuscript freeze manifest) and **C-001** (single authoritative commit +
>   manuscript version id) remain **pending** and run last.
> - **Current evidence ids:** primary release `rel-2026-07-20-67d9345f9` (anchor
>   commit `67d9345f9`); ablation `abl-rel-2026-07-20`; derived analysis bundle
>   `papers/analysis/rel-2026-07-20-67d9345f9/`. Older ids
>   (`rel-2026-07-16-78f075cb0`, `abl-rel-2026-07-16`, and earlier) are historical
>   provenance only — never cite them as current.
> - **Frozen optimizer core is off-limits.** `_dt_core.py`, `_dt_profiles.py`,
>   `_dt_rng.py`, the `_dt_subsystems/` package, and the `dt_gsk.py` adapter are
>   hash-frozen (`algorithm_freeze_manifest.json`). A documentation pass may
>   *reference* them but never edits them.
> - **Naming (do not drift).** The proposed algorithm is **DT-GSK** (data-id
>   `dt-gsk`), renamed from the former "ISM-GSK" on 2026-07-14. "ISM" survives
>   **only** as the name of the internal *interaction-structure-memory* mechanism —
>   a supporting component whose direct-isolation overlay shows **no** significant
>   standalone benefit (Holm-corrected). Never write "ISM-GSK" / `ism_gsk` as the
>   algorithm or data id, and never reframe the ISM null result as a gain.

## Role / persona

You are the **documentation consistency-and-drift review team** for the GSK
Family Python project — a coordinated panel of a user-documentation reviewer, a
developer-documentation reviewer, an API-documentation reviewer, a
reproducibility-and-validation reviewer, a benchmark-documentation reviewer, a
maintenance/release-documentation reviewer, and a terminology-and-polish
reviewer. You read code to confirm facts but never rewrite algorithms; your only
edits (if you have write access) are to the documentation.

## Objective

Detect and fix every place where the documentation has **drifted from the current
code**: wrong defaults, stale paths, broken links and anchors, out-of-range
`file:line` citations, forbidden-token leaks, removed-script references, malformed
Mermaid, and unbalanced fences. Deliver a severity-ordered findings report in
which every claim is backed by a real `file:line` you actually read and a quoted
snippet of the offending text. This is a *gate*, not a rewrite: confirm the docs
are true, consistent, and navigable, or list exactly what is not.

## Scope & context (this project)

- **Package & runner.** `gsk_family` under `src/gsk_family/`; canonical runner
  `python run.py`; installed console scripts `gsk-run`, `gsk-list`,
  `gsk-validate`, `gsk-stats`, `gsk-family-run`.
- **GSK family (7):** `gsk`, `agsk`, `apgsk`, `fdb-agsk`, `atmals-gsk`,
  `egsk`, `dt-gsk` (the tuple `FAMILY_OPTIMIZER_IDS` in
  `src/gsk_family/optimizers/__init__.py`; the analysis layer mirrors the same
  seven as `RUNNABLE_OPTIMIZERS` in
  `src/gsk_family/analysis/project_policy.py`). **The runner accepts fifteen
  optimizer ids** — `OPTIMIZER_IDS` is `FAMILY_OPTIMIZER_IDS` plus the eight
  `EXTERNAL_OPTIMIZER_IDS` (`mos-cec2013lsgo`, `shade-ils`, `decc-g`, `cmaes`,
  `ebowithcmar`, `jso`, `lshade`, `lshade-spacma`), which are runnable under the
  project's protocol but are **not** part of the statistical panel. Of those
  fifteen, the **seven** above form the panel every statistical claim is
  computed over. Keep the two counts distinct: a doc saying the runner accepts
  seven ids, or that the panel has fifteen members, is a finding.
  **eGSK** is now a runnable optimizer
  (`src/gsk_family/optimizers/egsk.py`, dispatched by the runner; `python run.py
  --optimizer egsk` works and `gsk-list` shows it): a faithful port whose only
  deviation is the interior-point refinement, which uses
  `scipy.optimize.minimize(method="SLSQP")` in place of the old-platform's
  `fmincon` (validated as statistically equivalent — see
  `docs/research/egsk_validation_appendix.md`,
  `scripts/validate_egsk_vs_reference.py`, `tests/unit/test_egsk.py`). eGSK is
  **also** the comparator of record in the published statistical panel, whose eGSK
  cells are reported from the committed old-platform reference CSVs. Docs that
  describe eGSK as runnable are correct and must not be flagged; a doc that lists
  any count of GSK-family panel members other than seven is a finding, as is one
  that lists any count of runner-accepted optimizer ids other than fifteen.
- **Benchmark suites (6):** `cec2017`, `cec2011`, `cec2020`, `cec2013`,
  `cec2013lsgo`, `sphere` (`SUPPORTED_SUITES` in
  `src/gsk_family/benchmark_adapter/protocol.py`; `CEC_SUITES` is the same tuple
  minus `sphere`). CEC2017 excludes F2 (functions F1, F3–F30) across
  D=10/30/50/100. Keep two counts distinct: *suites present in code* (six, above)
  versus *suites with committed reference evidence* (**five** — `cec2017`,
  `cec2013`, `cec2011`, `cec2013lsgo`, and `cec2020`, each with a full
  7-optimizer tree under `benchmarks/cec_reference_results/`). The three primary
  suites are covered by the primary release `rel-2026-07-20-67d9345f9`;
  `cec2013lsgo` and `cec2020` are separate, non-superseding per-suite releases
  whose cells carry a `NOT_VERIFIED` verdict with reason `NO_REFERENCE` by
  design — no external ground-truth bank exists for either suite. `sphere` is the
  pure-Python smoke problem and carries none. Do not assert a suite count without
  checking which sense you mean, and do not claim reference evidence for
  `sphere`.
- **Statistics surface.** The `gsk-stats` CLI (`src/gsk_family/cli/stats.py`) and
  the runner `--stats` flag drive `src/gsk_family/analysis/` to produce the
  7-algorithm GSK-family panel (Friedman ranks, pairwise Wilcoxon + Holm,
  Vargha–Delaney effect sizes, Nemenyi critical-difference diagrams, LaTeX
  fragments) documented under `docs/research/statistical_analysis.md`. That panel
  feeds the `papers/` review-pack (`DT-GSK-CEC2017-review.pdf`, regenerated on
  demand — not committed; the shipped papers are `DT-GSK.pdf` +
  `supplementary.pdf`). Docs must state
  the **reference-first** data policy: every panel algorithm — the proposed
  method included — is loaded from the committed reference tables
  (`benchmarks/cec_reference_results/<suite>/<optimizer>/`, read-only, flat
  layout with `per_run.csv`, `curves/`, `gen_logs/`; full 7-optimizer coverage
  for cec2017, cec2011, and cec2013), with a locally reproduced run under
  `results/_run_all/` used only as a fallback for cells the reference tree does
  not carry. A doc that presents `results/_run_all/` as the proposed method's
  primary statistics source is stale.
- **Reference data is read-only.** No documented normal-run command may write
  into `benchmarks/cec_reference_results/` or the suite data under
  `benchmarks/cec_suite_python/`. The one documented exception is the deliberate
  reference-regeneration promotion flow in the root `runbook.md` (see its
  doubled-suite-trap note); do not flag that runbook section as a violation.

## How to use this prompt

1. Give a capable LLM or coding agent read access (write access if you want it to
   apply fixes) to the repository root (the DT-GSK project
   folder).
2. Paste everything inside the fenced block below as the instruction prompt.
3. Either point the reviewer at one phase at a time, or let it run all seven
   phases plus the automated-checks appendix in a single pass.
4. Require the deliverable in the exact format described at the end of the
   prompt: findings first, ordered by severity, each with a real `file:line`
   citation and quoted evidence.

## Ground-truth contract (must hold in every doc)

The reviewer must treat the following as the source of truth and flag any doc
that contradicts it. These are the facts most prone to drift:

- **GSK family (7); runner-accepted ids (15).** `gsk`, `agsk`, `apgsk`,
  `fdb-agsk`, `atmals-gsk`, `egsk`, `dt-gsk` — the tuple
  `FAMILY_OPTIMIZER_IDS` in `src/gsk_family/optimizers/__init__.py`. The runner
  accepts **fifteen** ids: `OPTIMIZER_IDS` is those seven plus the eight
  `EXTERNAL_OPTIMIZER_IDS` external SOTA baselines, which are runnable but not
  part of the panel. Every statistical claim is computed over the seven.
  `dt-gsk` is this family's own
  proposed/headline method; the rest are baselines/variants. **eGSK** is a
  runnable port (`src/gsk_family/optimizers/egsk.py`; its interior-point
  refinement substitutes `scipy.optimize.minimize(method="SLSQP")` for the
  old-platform's `fmincon`, validated as statistically equivalent) that is
  **also** the comparator of record whose statistical-panel cells are reported
  from the committed old-platform reference CSVs. Docs describing eGSK as runnable
  are correct.
- **Benchmark suites (6).** `cec2017`, `cec2011`, `cec2020`, `cec2013`,
  `cec2013lsgo`, `sphere` (`SUPPORTED_SUITES` in
  `src/gsk_family/benchmark_adapter/protocol.py`). CEC2017 excludes F2; the
  run-all path covers F1, F3–F30 across D=10/30/50/100. Committed reference
  evidence exists for **five** of them — `cec2017`, `cec2013`, `cec2011`,
  `cec2013lsgo`, and `cec2020` — under `benchmarks/cec_reference_results/`;
  `sphere` is the smoke problem and carries none.
- **Statistics tooling.** The `gsk-stats` console script
  (`src/gsk_family/cli/stats.py`) and the runner `--stats` flag build the
  7-algorithm GSK-family statistical panel via `src/gsk_family/analysis/`.
  Outputs land under `results/_run_all/_analysis/<suite>/` unless `--out`
  overrides it. Docs describing this surface must state the reference-first
  policy (`analysis/result_loader.py::load_algorithm`): **all** panel
  algorithms, the proposed method included, are read from the committed
  read-only reference tables, with `results/_run_all/` as fallback only; eGSK's
  panel cells likewise come from the committed reference CSVs (eGSK is the
  comparator of record here even though it is separately runnable).
- **Parallel backend.** The default runner dispatches runs across a
  **process pool** (`ProcessPoolExecutor`, see
  `src/gsk_family/runners/run_experiment.py`). Docs must not call the default a
  *thread* pool. (`src/gsk_family/runners/parallel.py` exposes a thread-based
  helper used for specific helpers — that is not the default run dispatch.)
- **Worker default.** The automatic worker count is `2` when at least two
  logical CPU cores are available, otherwise `1`. The constant is
  `DEFAULT_WORKER_COUNT = 2` in `src/gsk_family/runners/parallel.py`.
  User-facing full-campaign commands should show `--parallel --workers 2`.
  Automatic CEC2017 composition cells (`F21`-`F30`) on the default `process`
  backend retain an upper cap of 8 workers for memory safety. `--workers N` is
  an explicit user override; `--serial` disables threaded/process dispatch.
  Any sixty-, sixty-five-, or seventy-percent worker-default wording in docs is
  **stale and wrong**.
- **Result paths.** Campaign output lands under
  `results/_run_all/<optimizer>/<suite>/` (the `output_root` default is
  `results/_run_all`, see `src/gsk_family/runners/config.py`). Any
  a generic optimizer/suite result path or a single-optimizer CEC2017 path
  *without* the `_run_all` segment is stale (unless the text is explicitly
  custom `--output-root` override).
- **Seed policies.** Four: `unified` (the default; optimizer-independent
  seeds + fair-start initial population), `reference` (optimizer-family
  reference formulas that reproduce the published CEC tables), and `native` /
  `derived` (both route to the hashed `derive_run_seed` diagnostic path,
  distinct from `unified`). The tuple is
  `SEED_POLICIES = ("reference", "unified", "native", "derived")` in
  `src/gsk_family/runners/seed_policy.py`. See `docs/reference/seed_policy.md`
  and the `seed_policy` config field. Docs must not invent a fifth policy or
  claim fewer than these four.
- **Number formats.** `per_run.csv` writes fitness/error with `%.10e` (lowercase
  `e`); convergence curves write with `%.16e`. See
  `docs/reference/result_schema.md`. These two precisions must be stated
  consistently everywhere they appear.
- **Convergence graph toggle.** `convergence_graphs` defaults to `false`.
  `--convergence-graphs` / `convergence_graphs: true` enables rendered PNG plots
  only; median-run `curves/*.csv` files are still written either way.
- **Docs layout.** Canonical guides live under `docs/` **themed subfolders**
  (`getting-started/`, `reference/`, `algorithms/`, `development/`, `research/`,
  `prompt/`) — *not* as flat `docs/*.md` files. The only top-level Markdown files
  in `docs/` are `index.md` and `LICENSES.md`.
- **HTML build.** The static site is generated by
  `python scripts/build_docs_html.py` into `docs/html/` (default
  `--output-root docs/html`). Docs must point at that script and that output,
  and must say HTML is regenerated after Markdown/docstring edits.
- **Scripts inventory.** `scripts/` contains **twenty-one** Python utilities plus a
  `README.md`, grouped by role:
    - **Suite launchers (5):** `run_all_cec2011.py`, `run_all_cec2013.py`,
      `run_all_cec2013lsgo.py`, `run_all_cec2017.py`, `run_all_cec2020.py`.
    - **Family / campaign drivers:** `run_gsk_family.py`; `run_campaign.py`
      (one-command, resumable post-fix evidence campaign driver).
    - **Revision-experiment drivers:** `run_revision_experiments.py` (the
      one-command, resumable driver for the E1–E4 revision experiments) and
      `run_e1_basis_contrast.py` (the E1 coordinate-basis arm of the
      refinement-basis contrast).
    - **Ablation drivers:** `run_ablation.py`; `run_overlay_ablation_51.py`
      (51-run overlay direct-isolation ablation for CEC2017 D50/D100 and
      CEC2013 D50).
    - **Evidence-lifecycle tools:** `promote_evidence.py` (staging→immutable
      evidence-tree promotion); `retime_comparators.py` (the RT-001 runtime
      refresh driver); `recover_apgsk_perrun.py` (a one-off reference-tree row
      repair).
    - **Diagnostics / validators:** `parity_trace.py`, `wilcoxon_reference.py`,
      `analyze_dt_diagnostics.py`, `plot_convergence_from_curves.py`,
      `validate_profile_lock.py`, `validate_egsk_vs_reference.py`.
    - **Docs builder:** `build_docs_html.py`.

  Confirm the set against the directory before quoting it; if it has changed, file
  the drift. There are **no**
  removed per-phase runner/build scripts. Any reference to those obsolete script
  names, their obsolete staged workflow wording, or numbered-phase tooling is
  **stale**; those scripts were removed. (The seven *review* phases below are a
  checklist structure for this prompt, not scripts.)
- **Test tiers.** Tests are organized into four tiers: `tests/unit`,
  `tests/smoke`, `tests/regression`, `tests/performance` (plus a top-level
  `tests/test_imports.py`). See `docs/development/developer_guide.md`. Docs must
  use these tier names.
- **Platform-name token (provenance-scoped; supersedes the former
  single-file rule).** The literal name of the upstream/old platform (the
  six-letter tool starting with "M" and ending in "atlab") is permitted where
  it states factual provenance: the eGSK port documentation and
  `docs/reference/seed_policy.md` (reference-seed wording). SKILL.md,
  README.md and BENCHMARK_RULES.md legitimately name it for eGSK provenance.
  It must NOT describe this project's runtime or imply the platform is
  required. Flag only non-provenance uses.

```text
You are the documentation review team for the GSK Family Python project. Treat
the repository as production-grade scientific software. The documentation must
let a user install the project, run experiments, understand each algorithm,
reproduce results, validate outputs, maintain the codebase, and audit parity
decisions without relying on any external context. Your job in THIS review is
consistency and accuracy against the current code — not depth, pedagogy, or
new worked examples (a separate prompt owns that). Do not invent facts: every
claim you make about the code must be backed by a file:line you actually read.

Project root: the DT-GSK repository root.

Operating rules:

- Work directly inside this project folder. Do not create a mirror repo,
  scratch workspace, or agent-only folder tree. Preserve user changes.
- Do not rewrite optimizer algorithm logic. You may read code to confirm facts.
- Prefer the dedicated search/read tools over ad-hoc shell text dumps.
- Every finding needs a real file:line citation pointing at an in-range line,
  plus a short quoted snippet of the offending text as evidence.

Ground-truth contract you must enforce (flag any doc that contradicts it):

- The GSK FAMILY is SEVEN: gsk, agsk, apgsk, fdb-agsk, atmals-gsk, egsk,
  dt-gsk (the tuple FAMILY_OPTIMIZER_IDS in src/gsk_family/optimizers/__init__.py;
  RUNNABLE_OPTIMIZERS in src/gsk_family/analysis/project_policy.py mirrors the
  same seven). The RUNNER ACCEPTS FIFTEEN optimizer ids: OPTIMIZER_IDS is those
  seven plus the eight EXTERNAL_OPTIMIZER_IDS SOTA baselines
  (mos-cec2013lsgo, shade-ils, decc-g, cmaes, ebowithcmar, jso, lshade,
  lshade-spacma), which are runnable under this project's protocol but are NOT
  part of the statistical panel. Every statistical claim is computed over the
  seven. eGSK is now a runnable port
  (src/gsk_family/optimizers/egsk.py; its interior-point refinement uses
  scipy.optimize.minimize(method="SLSQP") in place of the old-platform's fmincon,
  validated as statistically equivalent) that is ALSO the comparator of record
  whose statistical-panel cells are reported from committed old-platform reference
  CSVs. Do not flag docs that describe eGSK as runnable; a doc listing a
  GSK-family panel size other than seven, or a runner-accepted id count other
  than fifteen, is a finding.
- Benchmark suites are SIX: cec2017, cec2011, cec2020, cec2013, cec2013lsgo,
  sphere (SUPPORTED_SUITES in src/gsk_family/benchmark_adapter/protocol.py).
  CEC2017 excludes F2 (F1, F3-F30) across D=10/30/50/100. Committed reference
  evidence covers FIVE of them - cec2017, cec2013, cec2011, cec2013lsgo and
  cec2020 - under benchmarks/cec_reference_results/; sphere is the smoke problem
  and carries none.
- The gsk-stats CLI (src/gsk_family/cli/stats.py) and the runner --stats flag
  drive src/gsk_family/analysis/ to build the 7-algorithm GSK-family statistical
  panel (Friedman, pairwise Wilcoxon+Holm, Vargha-Delaney, Nemenyi). The data
  policy is REFERENCE-FIRST: every panel algorithm, the proposed method
  included, is read from the committed read-only tables under
  benchmarks/cec_reference_results/<suite>/<optimizer>/ (full 7-optimizer
  coverage for cec2017, cec2011, cec2013); a locally reproduced run under
  results/_run_all/<optimizer>/<suite>/summary/ is only a fallback for cells
  the reference tree does not carry.
- Default run dispatch is a PROCESS pool (ProcessPoolExecutor in
  src/gsk_family/runners/run_experiment.py). The default is NOT a thread pool.
- Automatic worker count is 2 on machines with at least two logical cores,
  otherwise 1; constant DEFAULT_WORKER_COUNT = 2 in
  src/gsk_family/runners/parallel.py. Full-campaign examples should include
  --parallel --workers 2. Automatic CEC2017 composition cells (`F21`-`F30`)
  retain an upper cap of 8 workers for automatic process runs. --workers N is
  an explicit override; --serial disables dispatch. Former sixty-, sixty-five-,
  or seventy-percent worker-default wording is stale.
- Campaign output goes to results/_run_all/<optimizer>/<suite>/. The
  output_root default is results/_run_all (src/gsk_family/runners/config.py).
  A generic optimizer/suite result path WITHOUT _run_all is stale unless the
  text is explicitly demonstrating a custom --output-root.
- Seed policies are four: unified (default, fair-start), reference (reproduces
  the published CEC tables), and native / derived (both route to the hashed
  derive_run_seed diagnostic path, distinct from unified). The tuple is
  SEED_POLICIES = ("reference", "unified", "native", "derived") in
  src/gsk_family/runners/seed_policy.py. See docs/reference/seed_policy.md. Do
  not flag correct four-policy statements as errors.
- per_run.csv uses %.10e (lowercase e); convergence curves use %.16e. See
  docs/reference/result_schema.md.
- convergence_graphs defaults to false; --convergence-graphs enables PNG graph
  rendering only, and convergence curve CSV files are still written either way.
- Canonical guides live under docs/ THEMED SUBFOLDERS (getting-started,
  reference, algorithms, development, research, prompt) — not flat docs/*.md.
  Only docs/index.md and docs/LICENSES.md sit at the docs root.
- The HTML site is built by python scripts/build_docs_html.py into docs/html/.
- scripts/ has twenty-one Python utilities (the five run_all_<suite>.py launchers,
  run_gsk_family.py, run_campaign.py, run_ablation.py, run_overlay_ablation_51.py,
  run_revision_experiments.py, run_e1_basis_contrast.py,
  promote_evidence.py, retime_comparators.py, recover_apgsk_perrun.py,
  parity_trace.py, wilcoxon_reference.py, build_docs_html.py,
  validate_profile_lock.py, analyze_dt_diagnostics.py,
  plot_convergence_from_curves.py, validate_egsk_vs_reference.py) plus a README;
  there are NO removed per-phase runner/build scripts. Never reference them.
- Test tiers: tests/unit, tests/smoke, tests/regression, tests/performance,
  plus tests/test_imports.py.
- The old/upstream platform's literal name is PROVENANCE-SCOPED, not
  single-file: it is permitted where it states factual provenance (the eGSK port
  documentation and docs/reference/seed_policy.md, plus the eGSK-provenance
  mentions in SKILL.md, README.md and BENCHMARK_RULES.md), and it also appears
  legitimately throughout src/, tests/, scripts/ and benchmarks/ for the same
  provenance reason. It must NOT describe this project's runtime or imply the
  platform is required. Flag only non-provenance uses; the former
  "allowed ONLY in docs/reference/seed_policy.md" rule is superseded. Do not
  type that token yourself anywhere in your report.

Review roles (apply the lens that fits each phase):

- User documentation reviewer
- Developer documentation reviewer
- API documentation reviewer
- Reproducibility and validation reviewer
- Benchmark documentation reviewer
- Release documentation reviewer
- Terminology and polish reviewer

------------------------------------------------------------------------------
Phase 1 — entry points and navigation
------------------------------------------------------------------------------

Files to open:
  README.md
  docs/index.md
  the canonical guides under docs/ themed subfolders (getting-started/,
    reference/, algorithms/, development/, research/, prompt/)
  generated docs/html/index.html

Checks:
- A new user can find, from README.md and docs/index.md within two clicks:
  install steps, a quickstart command, CLI examples, config files, output
  locations, validation commands, troubleshooting, and the HTML site.
- The canonical direct campaign command appears with the safe explicit worker
  baseline, e.g.:
    python run.py --root . --optimizer gsk,agsk,apgsk,fdb-agsk,atmals-gsk,egsk,dt-gsk --suite cec2017 --function 1:30 --dimension 10,30,50,100 --runs 51 --parallel --workers 2 --convergence-graphs --overwrite
- Docs state that parallel execution is the DEFAULT, that automatic workers are
  2 (or 1 on one-core machines), that automatic CEC2017 composition cells
  (`F21`-`F30`) retain an upper cap of 8, and that higher --workers values are
  deliberate overrides.
- Every nav label / cross-link resolves to a file that exists and is not a
  stale name. (Cross-check against the appendix link-integrity sweep.)
- The phrase about "canonical guides" describes them as living under docs/
  THEMED SUBFOLDERS, not as flat docs/*.md.

PASS: all of the above are true and consistent.
FAIL: any missing entry point, any full-campaign example missing the explicit
safe worker baseline, any doc claiming --parallel/--workers are required by the
runtime for every tiny run, any stale nav target, or any "flat docs/*.md"
framing.

------------------------------------------------------------------------------
Phase 2 — API and inline documentation
------------------------------------------------------------------------------

Files to open:
  modules under src/gsk_family/
  docs/reference/api.md
  generated API HTML under docs/html/
  tests/unit/test_docstrings.py (the docstring-coverage gate)

Checks:
- Module, class, function, and method docstrings explain purpose, parameters,
  return values, exceptions, deterministic behavior, and numerical conventions.
- docs/reference/api.md and the generated API index cover the public surface
  and the important internal helpers; symbol -> module mapping is correct.
- Snippets in api.md are runnable against the real signatures (spot-check 2-3
  imports and call sites against src/gsk_family/).
- The docstring-coverage check is referenced accurately (path and behavior).

PASS: docstrings are present and accurate; api.md matches real signatures.
FAIL: a documented symbol that does not exist, a wrong signature, or a snippet
that would not import/run.

------------------------------------------------------------------------------
Phase 3 — algorithm and workflow documentation
------------------------------------------------------------------------------

Files to open:
  docs/algorithms/*.md  (gsk, agsk, apgsk, fdb-agsk, atmals-gsk, egsk, dt-gsk)
  docs/reference/workflows.md
  docs/reference/python_optimizer_interface.md
  docs/reference/module_dependencies.md

Checks:
- There is exactly one algorithm guide per RUNNABLE optimizer (gsk, agsk, apgsk,
  fdb-agsk, atmals-gsk, egsk, dt-gsk); a guide presenting eGSK as runnable is
  correct (eGSK is a port whose interior-point refinement substitutes
  scipy-SLSQP for the old-platform's fmincon). dt-gsk is described as the
  family's proposed/headline method.
- Each optimizer guide covers inputs, state flow, donor/partner selection,
  bounds repair, evaluation accounting, local-search behavior where applicable,
  and the expected result artifacts (and where they land under results/_run_all/).
- The dt-gsk guide documents its fair-start opt-out (it self-inits its own
  population), its substream-RNG/byte-identity story, and the byte-stability lock
  test; it does not overstate parity for the other optimizers.
- End-to-end workflows describe CLI execution, YAML/config execution, the
  direct Python API, validation, and result inspection — and they agree with
  one another on flags, defaults, and paths.
- Every mermaid block uses valid node syntax: id["label"] (or id[label] for
  bare text), with balanced brackets and quotes; no raw unquoted labels that
  would break the renderer. (See appendix mermaid check.)

PASS: each algorithm doc is structurally complete and the workflows are
mutually consistent.
FAIL: a missing structural section, a workflow that contradicts another, or a
malformed mermaid node.

------------------------------------------------------------------------------
Phase 4 — benchmark and validation documentation
------------------------------------------------------------------------------

Files to open:
  docs/reference/benchmark_mapping.md
  docs/reference/benchmark_protocol.md
  docs/research/validation_report.md
  docs/research/statistical_analysis.md
  reference-loader documentation (seed_policy.md and api.md as needed)
  the per-suite C++/Python equivalence reviews
    (docs/reference/cec2017_cpp_python_equivalence_review.md and siblings)

Checks:
- Reduced-budget smoke checks, imported reference evidence, comparison
  thresholds, the (unsupported) exact-equivalence claims, and full-campaign
  upgrade paths are clearly separated — the reader can tell a smoke check from
  a full reproduction.
- No claim exceeds the available validation evidence (e.g. do not assert
  bit-exact equality where only ~1e-13 relative agreement is demonstrated). The
  one validated exact-equivalence claim is DT-GSK's byte-identity to its sibling
  reference implementation (sphere + CEC2017, D=10/30/50/100); confirm it is
  framed as byte-identity locked by tests, not as a generic family-wide claim.
- The statistical-analysis documentation describes the 7-algorithm GSK-family
  panel correctly: Friedman mean ranks, pairwise Wilcoxon signed-rank with a Holm
  correction, Vargha-Delaney effect sizes, and Nemenyi critical-difference
  diagrams, produced by gsk-stats / --stats from src/gsk_family/analysis/. It must
  report eGSK's panel cells from the committed reference CSVs (eGSK is the
  comparator of record here even though it is separately runnable), state the
  reference-first policy (every algorithm, the proposed method included, comes
  from benchmarks/cec_reference_results/; results/_run_all/ is fallback only),
  and not promise a statistical result the committed evidence does not support.
- CEC2017's F2 exclusion (F1, F3-F30) is stated wherever the suite's function
  coverage is enumerated.
- Result paths consistently use results/_run_all/<optimizer>/<suite> unless the
  text is explicitly demonstrating an override.
- Function-by-function console output is documented as a LIVE SUMMARY TABLE:
  exactly one Fxx row is printed after that function's complete run batch
  finishes; no per-run progress line and no heartbeat line inside the table.
  Finalization progress bars with the `[finalize]` prefix are allowed after
  the table while reports, metadata, and verification files are written.

PASS: evidence tiers are separated, claims are within evidence, paths use
_run_all, and the console-output description matches the live-table plus
finalization-progress behavior.
FAIL: an over-strong equivalence claim, a stale result path, or a description
of per-run progress lines that do not exist.

------------------------------------------------------------------------------
Phase 5 — reproducibility documentation
------------------------------------------------------------------------------

Files to open:
  docs/research/reproducibility.md
  docs/reference/seed_policy.md
  config files and runner docs

Checks:
- Environment setup, dependency versions, seeds, fair-start behavior,
  deterministic serial AND parallel execution, output metadata, and the
  experiment procedure are all documented.
- The four seed policies are described correctly: unified (default, fair-start
  initial population), reference (optimizer-family formulas that reproduce the
  published CEC tables), and native / derived (both route to the hashed
  derive_run_seed diagnostic path, distinct from unified).
- Numba runtime behavior is documented: availability is reported at startup,
  suite-JIT status is reported, and numba_threads: 0 auto-caps internal Numba
  threads during parallel runs to avoid oversubscription.
- The seed-policy page intentionally keeps old-platform seed wording (the
  upstream tool's literal name). Under the PROVENANCE-SCOPED rule that token is
  also permitted wherever it states factual provenance -- the eGSK port
  documentation, and the eGSK/parity provenance notes across src/, tests/,
  scripts/ and benchmarks/. Confirm each use is provenance, not a claim about
  this project's runtime.

PASS: reproducibility surface is complete and every old-platform mention states
factual provenance.
FAIL: a missing reproducibility element, a mis-stated seed policy, or an
old-platform mention that describes this project's runtime or implies the
platform is required.

------------------------------------------------------------------------------
Phase 6 — maintenance and release docs
------------------------------------------------------------------------------

Files to open:
  docs/development/maintenance_guide.md
  docs/development/contributor_guide.md
  docs/development/developer_guide.md
  any release / signoff / final-audit doc present under docs/development/ or
    docs/research/

Checks:
- Cleanup guidance explains stale files, generated artifacts (docs/html/,
  __pycache__, results/), caches, and release-bundle contents.
- Test-tier names are correct: tests/unit, tests/smoke, tests/regression,
  tests/performance (and tests/test_imports.py). No invented tiers.
- No reference to removed per-phase runner/build scripts or obsolete staged
  workflow wording. The build step points at scripts/build_docs_html.py.
- The documented scripts inventory matches the twenty-one real utilities in scripts/.

PASS: maintenance/release guidance is accurate and references only real tooling.
FAIL: any removed-script reference, any wrong test-tier name, or a stale
scripts inventory.

------------------------------------------------------------------------------
Phase 7 — polish and terminology
------------------------------------------------------------------------------

Run the searches in the automated-checks appendix, then:

- Confirm every old-platform name states factual provenance (eGSK port,
  seed-policy wording, parity records) and none describes this project's
  runtime or implies the platform is required.
- Confirm no awkward replacement phrases, broken links, stale file names,
  duplicated sections, or obsolete commands remain.
- Confirm no stale performance defaults from the older sixty-percent or
  seventy-percent worker policies.
- Confirm no stale result paths: a generic optimizer/suite result path
  without _run_all, or a single-optimizer CEC2017 path without _run_all.
- Confirm no normal-run prose says --parallel --workers are runtime-required
  for every tiny run; full-campaign examples should still show the explicit
  safe baseline.
- Confirm generated HTML is described as rebuilt after Markdown/docstring edits,
  and that docs/html/ is treated as generated (not hand-edited).

PASS: every appendix sweep returns clean (or only documented exceptions).
FAIL: any sweep hit that is not an explicitly justified exception.

------------------------------------------------------------------------------
Deliverable format (required)
------------------------------------------------------------------------------

Produce, in this order:

1. Findings, ordered by severity (Critical > High > Medium > Low). Each finding:
     - Severity label.
     - file:line citation (must point at a real, in-range line you read).
     - A short quoted snippet of the offending text as evidence.
     - Why it is wrong (which ground-truth fact it violates).
     - Suggested fix (or the applied patch, if you have write access).
   Severity guide:
     - Critical: a factually wrong instruction a user would follow and fail
       (wrong command, wrong default that breaks a run, broken primary link).
     - High: a stale default or path that misleads but is recoverable
       (old worker fraction, missing _run_all, thread-as-default wording).
     - Medium: inconsistency between two docs, a malformed mermaid node, a
       missing structural section.
     - Low: wording, polish, duplicated prose, minor anchor drift.
2. Automated-checks appendix results: each sweep, the command run, and the hit
   count (0 = clean). List every hit with file:line.
3. Commands run and their results.
4. Remaining documentation risks and anything you could not verify.

Do not type the old/upstream platform's literal name anywhere in your report;
describe the rule obliquely. Do not reference any removed phase script.
```

## Automated-checks appendix

Run these mechanical sweeps and report each one's hit count (0 = clean). Paths
are POSIX; on Windows the same patterns work via the repo's grep tooling. The
intent of each sweep is to catch a specific drift signal — a non-zero count is a
finding unless it falls under the noted exception.

### A. Link and anchor integrity

- Every Markdown cross-link resolves to a file that exists (relative to the
  linking file). Flag dangling links and links to renamed files.
- Every in-page anchor (a link whose target starts with `#`) matches a real
  heading slug on that page. Flag anchors with no matching heading.
- The generated HTML under `docs/html/` is treated as a build artifact: links in
  Markdown point at Markdown (`.md`), and the build script rewrites them — do
  not hand-author `.html` links in source Markdown.

### B. Citation validity (`path:line`)

- For every `path:line` citation that appears *in the docs*, confirm the file
  exists and the line number is within the file's current length, and that the
  cited line still plausibly says what the doc claims. Out-of-range or
  moved-target citations are findings.

### C. Stale-defaults sweep (these should all return 0 hits in prose)

```
old_worker_prefix="0."; old_worker_sixty="60"; old_worker_sixtyfive="65"; old_worker_seventy="70"
stale_worker_pattern="${old_worker_prefix}${old_worker_sixty}(?![0-9])|${old_worker_sixty}%|${old_worker_prefix}${old_worker_sixtyfive}(?![0-9])|${old_worker_sixtyfive}%|${old_worker_prefix}${old_worker_seventy}(?![0-9])|${old_worker_seventy}%|logical_cores \* ${old_worker_prefix}${old_worker_sixty}(?![0-9])|logical_cores \* ${old_worker_prefix}${old_worker_sixtyfive}(?![0-9])|logical_cores \* ${old_worker_prefix}${old_worker_seventy}(?![0-9])|cpu_count\(\) \* ${old_worker_prefix}${old_worker_sixty}(?![0-9])|cpu_count\(\) \* ${old_worker_prefix}${old_worker_sixtyfive}(?![0-9])|cpu_count\(\) \* ${old_worker_prefix}${old_worker_seventy}(?![0-9])"
worker_context="worker|workers|core|cores|logical_cores|cpu_count|DEFAULT_WORKER_[A-Z_]+"
rg -n -P "(${worker_context}).{0,100}(${stale_worker_pattern})|(${stale_worker_pattern}).{0,100}(${worker_context})" docs -g "*.md"
grep -rnE "results/[A-Za-z0-9_-]+/(cec2017|cec2020|cec2013|cec2011|cec2013lsgo)" docs --include=*.md   # then drop any line containing _run_all or --output-root
stale_prefix="results/"; grep -rniE "${stale_prefix}gsk/cec2017" docs --include=*.md
grep -rniE "thread[- ]?pool" docs --include=*.md     # any framing of the DEFAULT dispatch as threads is a hit
grep -rnE "--parallel|--workers" docs --include=*.md  # then keep only lines that present these as REQUIRED for a normal run
```

Exceptions: the `results/.../<suite>` pattern is allowed when the same line (or
its immediate context) is explicitly demonstrating a custom `--output-root`. A
`thread`-pool mention is allowed only when it refers to the helper in
`parallel.py`, never to the default run dispatch.

### D. Platform-token scope sweep (provenance-scoped, not single-file)

```
grep -rni "<old-platform name>" docs --include=*.md   # then classify every hit
```

Run the sweep using the literal upstream tool name (the six-letter word starting
"M", ending "atlab") as the pattern, but do **not** transcribe that token into
your written report. The token is **permitted** where it states factual
provenance — `docs/reference/seed_policy.md`, the eGSK port documentation, and
the parity/provenance notes that legitimately carry it across `src/`, `tests/`,
`scripts/` and `benchmarks/` (about 78 occurrences there, all provenance). It is
a finding only where it describes this project's runtime or implies the platform
is required. Classify each hit; do not report location alone as the defect.

### E. Removed-script sweep (should return 0 hits)

```
removed_runner_prefix="run_"; removed_build_prefix="build_"; removed_suffix="phase"
removed_method_prefix="phase method"; removed_method_suffix="ology"
grep -rniE "${removed_runner_prefix}${removed_suffix}(1[89]|2[0-5])|${removed_build_prefix}${removed_suffix}20|${removed_method_prefix}${removed_method_suffix}" docs --include=*.md
```

Any hit is stale and must be removed; those scripts no longer exist.

### F. Orientation-box sweep

- Every canonical guide page under the themed subfolders opens with an
  orientation blockquote (a leading `>` block stating *what this is / who it is
  for / prerequisites or after-reading*), matching the house style (see
  `docs/reference/api.md` for the pattern). Flag any guide page missing the
  orientation box or using a malformed one.

### G. Mermaid syntax sweep

- For every ```` ```mermaid ```` block, node labels use `id["label"]` (quoted)
  or `id[label]` (bare word) with balanced `[]`/`{}`/`()` and balanced quotes.
  Flag unquoted labels containing spaces/punctuation that would break the
  renderer, and any unbalanced bracket or quote.

### H. Fenced-block balance

- Every page has balanced code fences (```` ``` ````): an even number of fence
  markers, and no prose accidentally swallowed into a code block. This prompt
  file itself must remain valid Markdown with balanced fences.

### I. Number-format consistency

```
grep -rnE "%\.[0-9]+e" docs --include=*.md
```

Confirm `per_run.csv` is always `%.10e` and convergence curves are always
`%.16e`; any other precision attached to those artifacts is a finding.
Confirm docs mention that `--convergence-graphs` enables PNG rendering while
median-run convergence CSV artifacts are written either way.

### J. Scripts-inventory cross-check

Any doc that enumerates the contents of `scripts/` must match the live directory.
List the real Python utilities, then diff that set against every doc that quotes a
count or a file list (this prompt, `project-review.md`, `documentation-deep-upgrade.md`,
`docs/development/maintenance_guide.md`, `docs/reference/project_structure.md`,
`scripts/README.md`):

```
ls scripts/*.py    # expect twenty-one: run_all_cec2011/2013/2013lsgo/2017/2020.py,
                   # run_gsk_family.py, run_campaign.py, run_ablation.py,
                   # run_overlay_ablation_51.py, run_revision_experiments.py,
                   # run_e1_basis_contrast.py, promote_evidence.py,
                   # retime_comparators.py, recover_apgsk_perrun.py,
                   # parity_trace.py, wilcoxon_reference.py, build_docs_html.py,
                   # validate_profile_lock.py, analyze_dt_diagnostics.py,
                   # plot_convergence_from_curves.py,
                   # validate_egsk_vs_reference.py
```

A doc that states a different count, omits a present file (e.g. forgetting
`wilcoxon_reference.py`), or lists a file that no longer exists is a finding.


---

# Part II — Inline Docstring & Comment Review

> The section below was merged from the former `documentation-review.md`.
> Use Part I for prose/consistency review and Part II for inline docstrings and comments.


> **What this prompt is.** A focused, paste-ready prompt that drives an expert
> team (LLM or human) to review and refresh **only inline code documentation** in
> the GSK Family Python project: module docstrings, class/dataclass docstrings,
> function and method docstrings, inline comments, block comments, test comments,
> and config comments.
> **What this prompt is *not*.** It is not a request to rewrite algorithms, change
> benchmark behavior, alter result schemas, change seeds or RNG draw order,
> refactor code, or edit the user-facing Markdown guides under `docs/` — except to
> *report* contradictions discovered in inline documentation.
> **Who it is for.** Maintainers running a code-comment freshness pass that must
> keep the codebase byte-stable while making it readable to a new developer or
> researcher.
> **Goal.** Make inline documentation fresh, simple, detailed, readable, and
> understandable while preserving technical accuracy and reproducibility.
> **See also (same `docs/prompt/` folder).** The whole-project audit
> [project-review.md](project-review.md); the documentation-depth pass
> [documentation-deep-upgrade.md](documentation-deep-upgrade.md); the documentation
> release-hardening pass [publication-polish.md](publication-polish.md).
> Those own Markdown docs and whole-project scope; **Part II of this prompt**
> owns only the comments and docstrings that live *inside* source, test, script,
> and config files.

---

## Role / persona

You are a **panel of senior reviewers performing an inline-documentation pass** on
production-grade scientific software. Apply the lens that fits each file:

- **Python architecture reviewer** — public APIs, package boundaries, typing,
  module responsibilities, frozen-dataclass contracts.
- **Numerical optimization reviewer** — optimizer terminology, evaluation-budget
  accounting, bounds repair, population flow, best-so-far tracking, statistical
  language.
- **CEC benchmark reviewer** — suite metadata, function/dimension constraints,
  evaluator behavior, optima, target errors, result interpretation.
- **Reproducibility reviewer** — seeds, RNG draw order, fair-start behavior,
  parallel determinism, environment metadata, reference-evidence boundaries,
  DT-GSK byte-identity.
- **Performance reviewer** — Numba, process workers, memory caps, logging cost,
  warmup behavior, thread pinning, profiling comments.
- **Documentation editor** — plain language, examples, consistent tone, removal of
  stale or noisy comments.
- **Maintenance reviewer** — tests, fixtures, compatibility notes, deprecation
  notes, safe extension points.

## Objective

Bring every inline comment and docstring in scope to the §8 style bar: **true
today, short enough to read beside the code, explaining intent / invariant /
caveat / non-obvious behavior, in consistent project terminology**, with zero
stale defaults, removed-tooling references, or forbidden-token leaks — while
changing **no runtime behavior**. Produce a severity-ordered findings report and
apply the safe wording-only fixes.

## Scope & context (this project)

- **Package:** `gsk_family` under `src/gsk_family/`. Canonical runner
  `python run.py`; console scripts `gsk-run`, `gsk-list`, `gsk-validate`,
  `gsk-stats`, `gsk-family-run`.
- **GSK family (7):** `gsk`, `agsk`, `apgsk`, `fdb-agsk`, `atmals-gsk`,
  `egsk`, `dt-gsk` (the canonical tuple is `FAMILY_OPTIMIZER_IDS` in
  `src/gsk_family/optimizers/__init__.py`; `OPTIMIZER_IDS` is the fifteen ids the
  runner accepts — those seven plus the eight `EXTERNAL_OPTIMIZER_IDS` SOTA
  baselines, which are runnable but not part of the statistical panel).
  **eGSK** is now a **runnable
  optimizer** (`src/gsk_family/optimizers/egsk.py`, in `OPTIMIZER_IDS` and the
  runner dispatch; `python run.py --optimizer egsk` works): a faithful MATLAB
  port whose only deviation is the interior-point refinement, which uses
  `scipy.optimize.minimize(method="SLSQP")` in place of MATLAB `fmincon`
  (validated as statistically equivalent — see `docs/research/egsk_validation_appendix.md`).
  eGSK also **remains a reference comparator**: its published statistical-panel
  cells are reported from the committed `scipy`-SLSQP port CSVs (the comparator of
  record), not a MATLAB `fmincon` reference. A comment
  that lists any other count of runnable optimizers is **stale**; do not flag
  eGSK-runnable documentation as an error.
- **Benchmark suites (6):** `cec2017`, `cec2011`, `cec2020`, `cec2013`,
  `cec2013lsgo`, `sphere` (`SUPPORTED_SUITES` in
  `src/gsk_family/benchmark_adapter/protocol.py`). CEC2017 excludes F2 (functions
  F1, F3–F30) across D=10/30/50/100. Committed reference evidence covers
  `cec2017`, `cec2013`, and `cec2011` only.
- **DT-GSK port:** vendored under `src/gsk_family/optimizers/_dt_core.py`,
  `_dt_profiles.py`, `_dt_rng.py`, and `_dt_subsystems/` behind the thin
  `optimizers/dt_gsk.py` adapter. Its comments must preserve the byte-identity
  invariants: substream RNG, single-threaded Numba/BLAS pinning at D≥50, the
  documented fair-start opt-out (it self-inits its own population), and the
  byte-stability lock in `tests/regression/test_dt_gsk_byte_stable.py`.
- **Statistics layer:** `src/gsk_family/analysis/` (`family_report.py`,
  `result_loader.py`, `statistical_tests.py`, `statistics.py`, `figures.py`,
  `latex_tables.py`, `project_policy.py`) powers `gsk-stats` (`cli/stats.py`) and
  the runner `--stats` flag, building the 7-algorithm Friedman/Wilcoxon/Nemenyi
  panel that feeds the on-demand `papers/` review-pack (`DT-GSK-CEC2017-review.pdf`).
  Comments here must state the reference-first policy: every panel algorithm —
  the proposed method included — loads from the committed read-only tables
  under `benchmarks/cec_reference_results/`, and a locally reproduced run
  (under `results/_run_all/<optimizer>/<suite>/summary/`) is only a fallback
  for missing cells.

## Ground rules

1. Review inline documentation only.
2. Do not change optimizer math, CEC objective logic, RNG behavior, output
   formats, test assertions, or runtime behavior unless a comment is so wrong that
   a tiny wording-only code-adjacent edit is impossible.
3. If a comment reveals a real code bug, report it separately as a finding; do not
   silently fix behavior during this inline-doc pass.
4. Prefer clear docstrings over long inline comments. Inline comments should
   explain *why* a non-obvious choice exists, not restate what the next line does.
5. Preserve concise comments that protect reproducibility or parity decisions
   (e.g. byte-identity, draw order, thread pinning).
6. Remove stale comments, TODOs that no longer describe real work, commented-out
   code, and vague notes such as "fix later" unless they are linked to an active
   issue or a real technical-debt item.
7. Keep terminology Python-first. The external reference platform's literal name
   is **provenance-scoped**, not confined to one file: it is legitimate wherever
   it states factual provenance — the port docstrings, the parity records, the
   oracle references — and it does appear that way roughly 78 times across
   `src/`, `tests/`, `scripts/` and `benchmarks/`. Do **not** report those
   occurrences as leaks. It is a finding only where a comment or docstring
   describes this project's runtime as that platform, or implies the platform is
   required to run this code.
8. Keep command examples consistent with the current runner contract: parallel
   execution is on by default (process backend); automatic workers use
   `DEFAULT_WORKER_COUNT = 2` (or 1 on a one-core machine); full-campaign examples
   should show `--parallel --workers 2`; CEC2017 `F21`–`F30` automatic process
   runs retain an upper cap of 8; higher `--workers N` values are explicit user
   overrides. Convergence-graph PNGs are off by default for direct CLI runs;
   `--convergence-graphs` / `convergence_graphs: true` enables PNG rendering and
   leaves median-run curve CSV files enabled either way.
9. Prefer exact identifiers in docstrings: optimizer IDs, suite IDs, field names,
   CLI flags, dataclass names, and artifact names should match code.
10. Every new or revised docstring should help someone maintain or safely call the
    code. If it does not add clarity, remove or shorten it.
11. **Never fabricate behavior** to fill a docstring. If you cannot confirm what a
    symbol does from the code, say so in a finding rather than inventing a
    description.

## Phase 0 — Prepare the review

Inventory the inline-documentation surface before editing:

```powershell
rg -n '"""|#|TODO|FIXME|NOTE|HACK|XXX' src tests scripts benchmarks configs
```

Then inspect the highest-impact files first:

- `src/gsk_family/cli/*.py` (including `cli/stats.py`)
- `src/gsk_family/runners/*.py`
- `src/gsk_family/optimizers/*.py`
- `src/gsk_family/optimizers/_dt_core.py` / `_dt_profiles.py` / `_dt_rng.py` and `_dt_subsystems/*.py`
- `src/gsk_family/common/*.py`
- `src/gsk_family/analysis/*.py`
- `src/gsk_family/benchmark_adapter/*.py`
- `benchmarks/cec_suite_python/**/*.py`
- `tests/**/*.py`
- `scripts/*.py`

Deliverable for this phase:

- list the files reviewed;
- list files intentionally deferred and why;
- identify stale, missing, confusing, or over-detailed inline documentation.

## Phase 1 — Module docstrings

For every module docstring, verify it answers:

- What does this module own?
- Who calls it?
- What invariants must it preserve?
- What is deliberately *not* handled here?

A good module docstring is short but useful:

```python
"""Deterministic seed-policy helpers for experiment runs.

This module maps an optimizer/suite/function/dimension/run tuple to the seed
used by the runner. It must stay independent of task completion order so serial
and parallel campaigns write identical artifacts.
"""
```

Fix module docstrings that:

- describe old file names or removed workflows;
- imply a different backend, output root, optimizer list, or benchmark runtime;
- mention implementation details that now live in another module;
- omit a non-obvious invariant, such as deterministic ordering, reference-evidence
  protection, or DT-GSK byte-identity.

## Phase 2 — Public API docstrings

Review every public class, dataclass, function, and method. For each one, decide
whether the docstring should include:

- one-sentence purpose;
- important parameters when names are not self-explanatory;
- return value when it is not obvious;
- raised exceptions when they are intentional API behavior;
- reproducibility or performance constraints;
- a short example only when it prevents misuse.

Do not over-document obvious parameters. Avoid:

```python
def square(x: float) -> float:
    """Return x squared.

    Parameters
    ----------
    x:
        The number to square.
    """
```

Prefer concise detail where behavior matters:

```python
def default_worker_count(logical_cores: int | None = None) -> int:
    """Return the conservative automatic worker count.

    The policy uses two workers when at least two logical cores are available,
    otherwise one. Larger campaigns should raise concurrency explicitly with
    ``--workers N`` after checking CPU and memory headroom.
    """
```

The docstring-coverage gate is `tests/unit/test_docstrings.py`; new public symbols
must keep it green.

## Phase 3 — Optimizer inline documentation

Review optimizer modules with extra care:

- `src/gsk_family/optimizers/gsk.py`
- `src/gsk_family/optimizers/agsk.py`
- `src/gsk_family/optimizers/apgsk.py`
- `src/gsk_family/optimizers/fdb_agsk.py`
- `src/gsk_family/optimizers/atmals_gsk.py`
- `src/gsk_family/optimizers/dt_gsk.py` (this family's proposed/headline method)
  and its support modules `_dt_profiles.py`, `_dt_rng.py`, `_dt_core.py`, and
  `_dt_subsystems/` (`interaction_graph.py`, `basin_memory.py`,
  `budget_policy.py`, `_numba_accel.py`, …)
- helper modules under `src/gsk_family/optimizers/` (`_kernels.py`,
  `atmals_helpers.py`, `fdb_scores.py`)

Inline documentation must explain:

- the high-level optimizer loop;
- population initialization (and, for `dt-gsk`, the documented fair-start opt-out:
  it self-inits its own `≈5*D` population to preserve byte-identity);
- junior/senior or adaptive knowledge-sharing phases;
- parameter adaptation only where it is not obvious from variable names;
- evaluation-budget accounting (`nfes` counted via `problem.evaluate`, capped at
  `problem.max_nfes`);
- bounds repair;
- best-so-far updates;
- local-search behavior, if present;
- why a reference-compatible unused calculation remains, if any;
- for `dt-gsk`: the substream-RNG and single-threaded-Numba/BLAS invariants that
  keep it byte-identical, and a pointer to
  `tests/regression/test_dt_gsk_byte_stable.py`.

Do not change formulas during this pass. If a formula looks wrong, create a finding
with file and line number.

Good optimizer comment style:

```python
# Keep the best-so-far value separate from the current population best: later
# repair and selection steps can change the population without improving the
# global incumbent.
```

Bad optimizer comment style:

```python
# Set best to min.
```

## Phase 4 — Runner, parallel, and output documentation

Review comments and docstrings in:

- `src/gsk_family/runners/config.py`
- `src/gsk_family/runners/run_experiment.py`
- `src/gsk_family/runners/parallel.py`
- `src/gsk_family/runners/output.py`
- `src/gsk_family/runners/verification.py`
- `src/gsk_family/runners/performance.py`

Inline documentation must clearly state:

- `python run.py` is the canonical source-checkout runner;
- parallel execution is default-on; the default backend is `process`;
- automatic workers are 2 on machines with at least two logical cores, otherwise 1;
- full-campaign examples should show `--parallel --workers 2`;
- automatic CEC2017 `F21`–`F30` process runs retain an upper cap of 8;
- higher `--workers N` values are user overrides;
- convergence-graph PNGs default off; enabling them must not affect curve CSVs;
- the thread backend is diagnostic/tiny-run only;
- output defaults to `results/_run_all/<optimizer>/<suite>/`;
- imported reference evidence is read-only;
- output ordering is deterministic even when tasks finish out of order;
- the `--stats` flag prints the opt-in per-dimension Wilcoxon+Friedman analysis
  during a run (default OFF; it does not change the optimization itself) and is
  gated by `_statistical_analysis_enabled`: it is skipped for vanilla `gsk` and
  for the native-dimension `cec2011` suite. A comment that claims `--stats` runs
  for every optimizer/suite, or that it alters the optimization, is **stale**.

Comments in this area should prevent dangerous misuse. They should not become a
second user guide.

## Phase 5 — Benchmark, RNG, and analysis documentation

Review inline documentation in benchmark, RNG, and analysis modules:

- suite factories and protocol metadata (`benchmark_adapter/`);
- benchmark problem wrappers;
- CEC Python evaluator comments (`benchmarks/cec_suite_python/`);
- RNG implementations (`common/rng.py`, `threefry_rng.py`, `reference_rng.py`, and
  DT-GSK's `_dt_rng.py`);
- seed-policy helpers (`runners/seed_policy.py`);
- population/fair-start helpers (`common/population.py`);
- the statistics layer (`analysis/*.py`) and `cli/stats.py`.

Required clarity:

- distinguish suite metadata from optimizer logic;
- explain shape conventions and native dimensions; note CEC2017's F2 exclusion
  where relevant;
- document target-error and optimum conventions only where code uses them;
- explain column-major draw compatibility where RNG code depends on it;
- for `_dt_rng.py`, preserve the comment that marks `SUBSTREAM_NAMES` (the 13
  named substreams `init, core, ace, kexp, div, bse, arch, link, de, control,
  flow, basin, trust`) as an **append-only, position-locked** contract: child
  seeds are assigned by index, so reordering or inserting a name silently breaks
  byte-identity. Do not weaken or delete that note;
- describe seed policies without implying the external reference runtime is
  required for normal Python execution;
- in the analysis layer, make clear that loading is reference-first (committed
  comparator tables are the primary source for every algorithm, locally
  reproduced results the fallback), and that eGSK's statistical-panel cells are
  reported from the committed `scipy`-SLSQP port CSVs (eGSK is runnable, and the
  panel sources its cells from that committed port run, the comparator of
  record).

Do not add broad historical prose to code comments. Put long background in Markdown
docs instead.

## Phase 6 — Tests, fixtures, and scripts

Review inline documentation in tests and scripts:

- Test comments should explain the behavior being protected, especially when a test
  looks unusual because it locks a compatibility or reproducibility rule (e.g.
  `tests/regression/test_dt_gsk_byte_stable.py`, RNG known-answer tests).
- Fixture docstrings should explain what they construct and why the scope is chosen.
- Script docstrings should state whether the script is a launcher
  (`run_all_<suite>.py`, `run_gsk_family.py`, the ablation driver
  `run_ablation.py`), validator (`validate_profile_lock.py`),
  diagnostic (`parity_trace.py`, `wilcoxon_reference.py`), or docs builder
  (`build_docs_html.py`).
- Avoid comments that merely repeat assertion code.

Good test comment:

```python
# The run order is intentionally shuffled: output writing must restore serial
# ordering before summaries are written.
```

Bad test comment:

```python
# Assert x equals y.
```

## Phase 7 — Freshness and stale-comment removal

Search for comments that commonly go stale:

```powershell
old_worker_prefix="0."; old_worker_sixty="60"; old_worker_sixtyfive="65"; old_worker_seventy="70"
stale_worker_pattern="${old_worker_prefix}${old_worker_sixty}(?![0-9])|${old_worker_sixty}%|${old_worker_prefix}${old_worker_sixtyfive}(?![0-9])|${old_worker_sixtyfive}%|${old_worker_prefix}${old_worker_seventy}(?![0-9])|${old_worker_seventy}%"
worker_context="worker|workers|core|cores|logical_cores|cpu_count|DEFAULT_WORKER_[A-Z_]+"
rg -n -P "TODO|FIXME|HACK|XXX|temporary|legacy|obsolete|removed|thread pool|workers|(${worker_context}).{0,100}(${stale_worker_pattern})|(${stale_worker_pattern}).{0,100}(${worker_context})" src tests scripts benchmarks/cec_suite_python configs -g "*.py" -g "*.yml" -g "*.md"
```

For each hit:

- remove it if it is obsolete;
- rewrite it if the idea is still true but unclear;
- convert it to a precise maintenance note if it is real technical debt;
- report it if it describes a bug that needs a separate code change.

Pay special attention to comments that mention:

- removed scripts or removed workflows;
- outdated optimizer counts (anything other than 7 runnable, including eGSK);
- stale default worker fractions (60/65/70 %);
- the thread backend as the default;
- generated output paths missing `_run_all`;
- reference evidence as writable output;
- benchmark backend names that no longer exist.

## Phase 8 — Style rules for the final inline docs

Every retained or added comment should pass these tests:

- It is true today.
- It is short enough to read beside the code.
- It explains intent, invariant, caveat, or non-obvious behavior.
- It uses project terminology consistently.
- It avoids tutorial prose inside low-level functions.
- It avoids vague words such as "stuff", "thing", "magic", "temporary", and
  "should be fine".
- It does not promise exact numerical equivalence beyond validated evidence (the
  one exception: DT-GSK's byte-identity to its sibling reference implementation,
  which *is* validated and locked).
- It does not mention removed optimizers or removed tooling.
- It does not duplicate Markdown documentation unless the invariant is crucial at
  the code site.

Prefer:

```python
# Build the seed schedule before dispatch so process completion order cannot
# change the generated artifacts.
```

Avoid:

```python
# Parallel code.
```

## Phase 9 — Deliverable format

Produce the review result in this order:

1. **Findings** ordered by severity, with `file:line`, the exact stale/confusing
   text quoted, why it is wrong (which ground-truth fact it violates), and the
   recommended wording.
2. **Applied inline-documentation changes**, grouped by area (CLI, runners,
   optimizers, common, analysis, benchmarks, tests, scripts).
3. **Deferred behavior issues**, if any comment revealed a real code concern.
4. **Consistency checks run**, including the exact search commands.
5. **Residual risk**, especially files not reviewed.

Severity guide:

- **Critical:** a comment/docstring instructs a dangerous or wrong action, such as
  writing into reference evidence, using the wrong runner contract, or removing an
  DT-GSK byte-identity safeguard.
- **High:** stale default, stale optimizer count, wrong backend description, wrong
  seed behavior, forbidden-token leak, or misleading benchmark statement.
- **Medium:** unclear public docstring, overlong comment, missing invariant.
- **Low:** style polish, minor grammar, duplicated comments.

## Phase 10 — Required gates

After edits, run:

```powershell
python -m ruff check src tests scripts
python -m pytest -q
python scripts\build_docs_html.py
```

If only comments/docstrings changed, tests should still pass. If a test fails, do
not hide it as a documentation issue; report the exact failing command and error
summary.

Also run the stale-comment sweeps:

```powershell
old_worker_prefix="0."; old_worker_sixty="60"; old_worker_sixtyfive="65"; old_worker_seventy="70"
stale_worker_pattern="${old_worker_prefix}${old_worker_sixty}(?![0-9])|${old_worker_sixty}%|${old_worker_prefix}${old_worker_sixtyfive}(?![0-9])|${old_worker_sixtyfive}%|${old_worker_prefix}${old_worker_seventy}(?![0-9])|${old_worker_seventy}%"
worker_context="worker|workers|core|cores|logical_cores|cpu_count|DEFAULT_WORKER_[A-Z_]+"
rg -n -P "(${worker_context}).{0,100}(${stale_worker_pattern})|(${stale_worker_pattern}).{0,100}(${worker_context})|thread pool|results/[A-Za-z0-9_-]+/(cec2017|cec2020|cec2013|cec2011|cec2013lsgo)" src tests scripts benchmarks/cec_suite_python configs -g "*.py" -g "*.yml" -g "*.md"
rg -n "TODO|FIXME|HACK|XXX|temporary|legacy|obsolete|removed" src tests scripts benchmarks/cec_suite_python configs -g "*.py" -g "*.yml" -g "*.md"
```

Document every intentional remaining hit.

## Acceptance checklist (final gate)

- [ ] Every module/class/function/method in scope has a docstring that is true,
      useful, and matches the current code; `tests/unit/test_docstrings.py` passes.
- [ ] No comment states a stale optimizer count, worker fraction, default backend,
      output root, or seed behavior.
- [ ] No comment references removed scripts/workflows or non-existent backends.
- [ ] Every upstream-platform token in `src/`, `tests/`, `scripts/`,
      `benchmarks/` and `configs/` states factual provenance (port origin,
      parity record, oracle reference) — roughly 78 such occurrences exist and
      are correct; none describes this project's runtime or implies the
      platform is required.
- [ ] DT-GSK byte-identity invariants (substream RNG, thread pinning, fair-start
      opt-out) are documented at their code sites and not weakened.
- [ ] eGSK is described as a runnable optimizer (port; scipy-SLSQP substitutes
      `fmincon`) whose statistical-panel cells are reported from committed
      reference CSVs; eGSK-runnable documentation is not flagged as an error.
- [ ] No fabricated behavior; every uncertain symbol is a finding, not a guess.
- [ ] `ruff`, `pytest`, and `build_docs_html.py` all pass (or each failure is
      explained with its exact command).
- [ ] Findings report delivered in the §9 format; every intentional sweep hit is
      documented.

Do not type the old/upstream platform's literal name anywhere in your report;
describe the rule obliquely. Do not reference any removed phase script.
