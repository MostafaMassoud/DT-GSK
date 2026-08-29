# Deep Expert Review Prompt For GSK Family Python

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
> the `CLAUDE.md` "Right now" block. As of this refresh: **pass-59 / tag v2.32**
> (decision log through **D-0064**, register through **CR-0039**,
> next free **CR-0040 / D-0065** — verify free at apply time); the round-one revision at *Algorithms* (MDPI) is
> complete and agent-side work is finished; resubmission is due **2026-09-01**
> (deadline = planned date, zero slack).
>
> Four things this refresh adds, because they change what a reviewer of this repository sees:
> (1) the repository is **PRIVATE until upload day** and must be flipped public before the
> SuSy upload — the Data Availability Statement names its URL and tags `v2.13`/`v2.32`;
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


> **What this page is.** A paste-ready, full-project audit prompt for the GSK
> Family Python project. It coordinates an expert review team across code, docs,
> tests, benchmarks, and reproducibility, and produces a severity-ranked report
> with applied fixes. **Who it is for.** Maintainers and reviewers (human teams
> or capable LLM/coding agents) running a complete production-grade review.
> **How to use it.** Open the repository, then paste everything below the first
> horizontal rule as the instruction prompt. Work the phases in order (Phase 0
> first, always read-only), running the embedded commands and recording evidence.
> **See also.** The four sibling prompts in this folder:
> [documentation-deep-upgrade.md](documentation-deep-upgrade.md) (deep documentation
> depth/pedagogy pass), [documentation-review.md](documentation-review.md)
> (documentation consistency/staleness gate in Part I, inline docstrings/comments in
> Part II), and [publication-polish.md](publication-polish.md) (the pre-publication
> release-hardening pass). This prompt is the broadest: it audits the whole
> project, not just docs.

---

```text
You are a coordinated review team of senior experts auditing the GSK Family
Python scientific optimization project. Review the repository as production
research software, not as a partial prototype. The finished project must be
runnable, documented, reproducible, maintainable, performant, and traceable to
the imported reference evidence.

================================================================================
0. CONTEXT THE REVIEWER MUST INTERNALIZE BEFORE STARTING
================================================================================

Project root: the DT-GSK repository root. All paths in this
prompt are relative to it.

--------------------------------------------------------------------------------
CURRENT PROJECT STATUS (snapshot 2026-07-20 -- a point-in-time anchor, NOT a
standing invariant; re-verify each item against the repo before acting):

- Phase: the manuscript is BUILT and in FINAL PRE-SUBMISSION REMEDIATION -- a
  hardening/consistency pass over a finished project, not from-scratch
  construction. The 80-ticket remediation ledger
  (papers/governance/remediation_2026_07_18/ticket_status.csv) stands at 80/80
  terminal -- 70 closed_verified plus 10 superseded_with_evidence; no ticket is
  open.
- Quality gates: all GREEN as of 2026-07-20 -- build hygiene, cross-format
  parity (PDF/DOCX/JSON), provenance-claims, citation-usage map, and environment
  attestation. Document-consistency exits nonzero ONLY on author-pending fields
  (e.g. suggested reviewer names), which are author-supplied and must NOT be
  auto-generated.
- RT-001 is CLOSED -- do NOT re-run it and do NOT request a re-timing. The
  six-comparator re-timing was executed, FAILED its determinism gate (3,772
  differing rows), and was not adopted. Under Decision 7 Option 3 the runtime
  table (tab:runtime) was narrowed to DT-GSK-only, single-session, and the
  manuscript makes no cross-algorithm wall-clock claim. tab:runtime and
  cost_cec2017.csv are frozen in that narrowed form; no evidence task is open.
- Terminal steps (only after any author edits land): C-008 mints a
  FRESH papers/governance/main_manuscript_freeze_manifest.json (CRLF + 2-space,
  edited in place -- never read_text()/sed, which normalize to LF and break the
  hashes), then C-001 records the single authoritative commit + manuscript
  version id.
- Current evidence releases: rel-2026-07-20-67d9345f9 (anchor commit 67d9345f9)
  and abl-rel-2026-07-20; derived bundle
  papers/analysis/rel-2026-07-20-67d9345f9/. Do NOT cite the superseded ids
  (rel-2026-07-16-78f075cb0, rel-2026-07-10-262fc16c9, abl-rel-2026-07-16,
  abl-rel-2026-07-13) as current -- they are historical provenance only.
- Off-limits: the optimizer core is byte-locked/hash-frozen (the algorithm
  freeze manifest, algorithm_freeze_manifest.json): _dt_core.py,
  _dt_profiles.py, _dt_rng.py, the _dt_subsystems/ package (incl.
  interaction_graph.py and _numba_accel.py), and the dt_gsk.py adapter.
  Reference them; never direct edits to them.
- Naming (do not drift): the proposed algorithm is DT-GSK (data-id dt-gsk).
  "ISM" (interaction-structure memory) is only a SUPPORTING internal mechanism
  -- not the algorithm name and not a contribution; its direct-isolation overlay
  shows no significant standalone benefit (Holm-corrected). Never write
  "ISM-GSK" or ism_gsk as the algorithm or data id.
--------------------------------------------------------------------------------

This prompt lives at docs/prompt/project-review.md and renders as a page in the
generated documentation site. Sibling prompts sit beside it in the same folder:
documentation-deep-upgrade.md (documentation depth/pedagogy),
documentation-review.md (documentation consistency/staleness in Part I, inline
docstrings/comments in Part II), and publication-polish.md (release hardening).
This prompt
supersets them for whole-project scope.

Primary rule:

Work directly inside this project folder. Do not create a separate workspace,
mirror repository, or generated agent-only folder structure. Preserve user
changes. Do not rewrite optimizer algorithm logic unless the task explicitly
requests algorithmic work. You may review algorithm behavior, interfaces,
outputs, tests, performance, and documentation.

Ground-truth inventory (verify against the repo; do not assume it is stale, and
do not invent items not present):

- Family panel optimizers (7): gsk, agsk, apgsk, fdb-agsk, atmals-gsk, egsk,
  dt-gsk (dt-gsk is this family's own proposed/headline method; the rest are
  baselines/variants). Source: src/gsk_family/optimizers/ (gsk.py, agsk.py,
  apgsk.py, fdb_agsk.py, atmals_gsk.py, egsk.py, dt_gsk.py, plus helpers
  _kernels.py, atmals_helpers.py, fdb_scores.py, and the dt-gsk support modules
  _dt_profiles.py, _dt_rng.py, _dt_core.py, _dt_subsystems/). These 7 are
  FAMILY_OPTIMIZER_IDS; the runner ALSO accepts 8 external SOTA baselines
  (EXTERNAL_OPTIMIZER_IDS — outside the statistical panel), so the canonical
  OPTIMIZER_IDS tuple in src/gsk_family/optimizers/__init__.py holds 15 ids and
  `gsk-list` prints 15. RUNNABLE_OPTIMIZERS (the 7 family ids) lives in
  src/gsk_family/analysis/project_policy.py. Do NOT file the 15-id surface as
  drift against the 7-id panel.
  eGSK is a runnable optimizer (a faithful port; its interior-point refinement
  substitutes scipy.optimize.minimize(method="SLSQP") for the reference fmincon,
  validated as statistically equivalent -- see
  docs/research/egsk_validation_appendix.md,
  scripts/validate_egsk_vs_reference.py, tests/unit/test_egsk.py): it is in
  OPTIMIZER_IDS, RUNNABLE_OPTIMIZERS, and the runner dispatch, and
  "python run.py --optimizer egsk" works. eGSK ALSO remains the comparator of
  record for the statistical panel: the panel reports eGSK's cells from the
  committed Python (scipy-SLSQP) port CSVs under benchmarks/cec_reference_results/
  (the comparator of record), not a MATLAB-fmincon reference.
  Do NOT flag egsk-runnable documentation as an error. The 7-algorithm panel =
  the 7 runnable optimizers (with eGSK's panel cells sourced from the reference
  CSVs).
- Benchmark suites (6): cec2017, cec2011, cec2020, cec2013, cec2013lsgo, sphere.
  Suite tokens are normalized in src/gsk_family/benchmark_adapter/protocol.py;
  Python suite data lives under benchmarks/cec_suite_python/<suite>/. CEC2017
  excludes F2: the run-all path covers F1, F3-F30 across D=10/30/50/100.
- Statistical-comparison surface: the gsk-stats console script
  (src/gsk_family/cli/stats.py) and the runner --stats flag drive
  src/gsk_family/analysis/ to build the 7-algorithm GSK-family panel (Friedman
  mean ranks, pairwise Wilcoxon signed-rank with Holm correction, Vargha-Delaney
  effect sizes, Nemenyi critical-difference diagrams, rank charts, LaTeX
  fragments). The data policy is REFERENCE-FIRST
  (src/gsk_family/analysis/result_loader.py::load_algorithm): every panel
  algorithm — the proposed optimizer included — is read from the committed
  tables under benchmarks/cec_reference_results/<suite>/<optimizer>/ (flat
  layout: <opt>_<suite>_D<dim>.csv summaries, per_run.csv, curves/, gen_logs/;
  full 7-optimizer coverage for all five suites), and a locally
  reproduced run under results/_run_all/<optimizer>/<suite>/summary/ is only a
  fallback for cells the reference tree lacks. Default analysis output root is
  results/_run_all/_analysis/<suite>/ (override with --out). These LaTeX/figure
  fragments feed the papers/ review-pack (papers/DT-GSK-CEC2017-review.pdf,
  regenerated on demand by papers/scripts/generate_review_pack.py — not a
  committed artifact; the shipped papers are DT-GSK.pdf and supplementary.pdf,
  with papers/cover_letter.pdf alongside);
  papers/ is author material — review it for consistency, do not regenerate or
  edit it unless explicitly asked.
- Default execution backend is "process": a ProcessPoolExecutor created with the
  "spawn" start method (constructed in src/gsk_family/runners/run_experiment.py).
  The automatic worker count defaults to 2 when at least two logical CPU cores
  are available, otherwise 1 (src/gsk_family/runners/parallel.py:
  default_worker_count, DEFAULT_WORKER_COUNT = 2). User-facing campaign
  commands should spell out --parallel --workers 2. Automatic CEC2017
  composition cells F21-F30 retain an upper cap of 8 workers for memory safety
  if the automatic policy is raised in the future. --workers N is the explicit
  speed/memory override.
- Default results path: results/_run_all/<optimizer>/<suite>/ (the join is
  Path(output_root)/optimizer/suite in src/gsk_family/runners/output.py, with
  output_root defaulting to "results/_run_all"). Per-run subtrees: summary/,
  curves/, curves/graphs/, gen_logs/.
- Convergence graph PNGs are off by default for direct CLI runs
  (convergence_graphs = False). --convergence-graphs or
  convergence_graphs: true enables PNG rendering, while median-run curve CSV
  files under curves/ are always required.
- Seed policies: the supported set is ("reference", "unified", "native",
  "derived") (src/gsk_family/runners/seed_policy.py: SEED_POLICIES). The default
  is "unified" (fair cross-family statistical match). "reference" reproduces the
  imported reference tables bit-for-bit. "native" and "derived" are diagnostic
  labels that both map to the hashed derive_run_seed path.
- Byte-format parity (preserve exactly; do NOT "normalize"): per_run.csv writes
  best_fitness/error with %.10e and runtime_seconds with %.6f; convergence
  curves write BestError/Log10Error with %.16e; environment.json preserves its
  documented key order. These mirror the upstream reference implementation by
  intent.
- FP-regime sentinel: src/gsk_family/runners/fp_regime.py is a fail-closed guard
  that keeps a campaign in a single numba-JIT floating-point regime (documented in
  docs/reference/fp_regime.md, tested by tests/regression/test_fp_regime.py). Do
  not weaken or bypass it.
- DT-GSK ships a SINGLE `pub` profile. The earlier strong_candidate tuning
  experiment was rejected by full validation and fully removed; there is no
  strong-candidate config, script, test, or doc, and no analyze_ism_strong_baseline.py
  or analyze_ism_candidate_results.py in scripts/. Treat any such reference as stale.
- Docs live under docs/ in SIX themed subfolders: getting-started/, reference/,
  algorithms/, development/, research/, prompt/ -- plus the top-level entry
  points docs/index.md and docs/LICENSES.md. The HTML site is built by
  scripts/build_docs_html.py into docs/html/ and uses folder-prefixed page
  names (docs/reference/seed_policy.md -> docs/html/reference_seed_policy.html).
  docs/html/ is generated; never hand-edit it.
- scripts/ contains exactly twenty-one Python files (plus a README.md) and no others:
  run_all_cec2011.py, run_all_cec2013.py, run_all_cec2013lsgo.py,
  run_all_cec2017.py, run_all_cec2020.py, run_gsk_family.py, run_campaign.py,
  run_ablation.py, run_overlay_ablation_51.py, run_revision_experiments.py,
  run_e1_basis_contrast.py, build_docs_html.py,
  validate_profile_lock.py, parity_trace.py, wilcoxon_reference.py,
  analyze_dt_diagnostics.py, plot_convergence_from_curves.py,
  validate_egsk_vs_reference.py, promote_evidence.py, recover_apgsk_perrun.py,
  retime_comparators.py.
  (Re-check the count against the directory before flagging anything — the set
  grows with tooling work; a mismatch here means THIS list is stale, not that
  the extra script is a defect.)
  (run_ablation.py is the DT-GSK scaffold-ablation driver; its cells are
  aggregated by papers/scripts/generate_ablation_matrix.py and rendered by
  papers/scripts/generate_latex_tables.py.)
  (run_campaign.py is the one-command, resumable post-fix evidence-campaign
  driver -- primary cec2017/cec2013/cec2011, then the scaffold and overlay
  ablations, then finalization -- and never overwrites completed work.
  retime_comparators.py is the RT-001 driver: a single-environment runtime
  refresh that re-times the six comparators on CEC2017; it is a PURE TIMING
  refresh whose verify stage asserts every scientific column reproduces
  byte-for-byte, so neither script is "phase"/staged-release tooling.)
  (Confirm the set against the directory before quoting it;
  if it has changed, file the drift.) There is NO release/phase tooling in this
  project; do not look for, reference, or expect any "phase" runner script or any
  staged release-build methodology. If you find a reference to such tooling
  anywhere, treat it as a stale-documentation defect.
- Test tiers: tests/unit/, tests/smoke/, tests/regression/, tests/performance/,
  plus the top-level tests/test_imports.py. Documentation-command tests live in
  tests/smoke/test_documentation_commands.py; docstring-coverage tests live in
  tests/unit/test_docstrings.py.
- The standing quality gates are: python -m pytest -q ;
  python -m ruff check src tests scripts ; python scripts/build_docs_html.py .

Terminology rule (provenance-scoped; supersedes the former single-file rule):
the name of the upstream numerical-computing platform (a six-letter tool whose
name starts with "M" and ends with "atlab") is PERMITTED where it states factual
provenance — the eGSK port (a faithful port of a published implementation on
that platform, with `scipy`-SLSQP substituting its `fmincon` solver) and the
RNG seed-compatibility documentation (docs/reference/seed_policy.md). It MUST
NOT be used to describe THIS project's runtime, to imply that platform is
required to run anything here, or as a casual synonym for "the reference". The
former "exactly one file" rule predates the runnable eGSK port and is
superseded: SKILL.md, README.md and BENCHMARK_RULES.md now legitimately name
the platform for eGSK provenance. Flag only NON-provenance uses as defects.

Runtime contract to verify (each item is a check, not an assumption):

- Canonical source-checkout runner: python run.py (run.py prepends src/ to
  sys.path and calls gsk_family.cli.run:main).
- Representative full campaign command (explicit safe worker baseline):
  python run.py --root . --optimizer gsk,agsk,apgsk,fdb-agsk,atmals-gsk,egsk,dt-gsk
  --suite cec2017 --function 1:30 --dimension 10,30,50,100 --runs 51
  --parallel --workers 2 --convergence-graphs --overwrite
  (confirm the exact accepted syntax for multi-value --optimizer / --function /
  --dimension against src/gsk_family/cli/run.py before quoting it in docs).
- Parallel (process backend) is the default; --serial selects serial dispatch;
  --parallel forces parallel on; --parallel and --serial are mutually exclusive.
- --parallel-backend chooses between "process" (default) and "thread"; there is
  no "serial" backend token -- serial is the separate --serial flag. Confirm the
  flag is named --parallel-backend, not --backend.
- --workers N is an explicit user-selected concurrency override. The automatic
  default is 2 workers on machines with at least two logical cores, otherwise 1;
  documented campaign commands should still show --parallel --workers 2.
- Console output is on by default (console_log = True). --quiet turns it off;
  --console-log forces it on; the two are mutually exclusive.
- Numba availability, suite JIT status, active Numba thread count, and the
  thread mode are reported at startup when relevant. numba_threads: 0 auto-caps
  internal Numba threads during parallel runs to avoid nested oversubscription.
- Console progress is function-by-function: exactly one Fxx summary row prints
  only after that function's complete run batch finishes. The summary table must
  contain no per-run heartbeat/progress lines. Finalization progress bars with
  the `[finalize]` prefix are expected after the function table while reports,
  metadata, and verification files are written.
- Imported reference/evaluator evidence (benchmarks/cec_reference_results/ and
  benchmarks/cec_suite_python/ data files) is read-only during normal runs.
- The seed-policy reference page is the only place legacy seed-label wording for
  the upstream platform is intentionally retained.

================================================================================
1. REVIEW TEAM ROLES
================================================================================

1. Principal scientific-computing architect
2. Numerical optimization and metaheuristics expert
3. CEC benchmark and experimental-protocol expert
4. Reproducibility and deterministic-computation expert
5. Python packaging and release engineer
6. Performance, parallelism, and Numba specialist
7. Test strategy and quality-gate engineer
8. Documentation, API, and developer-experience reviewer
9. Security, path-safety, and generated-artifact reviewer
10. Research-user workflow reviewer
11. Statistical-analysis and publication-reporting expert (Friedman/Wilcoxon/
    Nemenyi panel, effect sizes, the gsk-stats CLI and --stats flag, and the
    papers/ review-pack consistency)

================================================================================
2. GLOBAL REVIEW RULES
================================================================================

- Findings first, ordered by severity, then by file path.
- Cite exact file paths and line numbers (path:line) wherever possible.
- Distinguish defects, risks, missing evidence, stale documentation, and
  improvement opportunities. Never relabel a missing check as a pass.
- Do not claim full-budget parity unless full-budget evidence is present.
- Treat reduced smoke results as smoke evidence only; keep them separate from
  full-campaign claims.
- Preserve RNG draw order, seed schedules, evaluation counts, result schema,
  output naming, and deterministic serial/parallel behavior.
- Prefer narrow patches over broad rewrites; justify any broad refactor in
  writing before doing it.
- Keep source docs and generated HTML synchronized: edit the source Markdown or
  docstring, then rebuild HTML; never hand-edit docs/html/.
- Root Markdown policy: the root holds three operating Markdown files --
  README.md (detailed landing page), SKILL.md (project agent file), and
  runbook.md (concise copy-paste build-and-run command reference) -- plus the six
  governance docs (PROJECT_RULES.md, DESIGN_GUIDE.md, ARCHITECTURE.md,
  BENCHMARK_RULES.md, CODING_STANDARD.md, PERFORMANCE_RULES.md), the release
  record FINAL_RELEASE_REPORT.md, and the top-level REPO_MAP.md navigation index.
  All review and documentation prompts now live under docs/prompt/ (this file is
  docs/prompt/project-review.md), and every other prose guide lives under docs/.
  Flag any root-level Markdown file outside that intentional set as a candidate
  for relocation under docs/ or removal.

================================================================================
3. AUDIT OPERATING PROTOCOL
================================================================================

1. Start read-only. Do not edit until baseline state, root location, git
   status, generated-output policy, and protected paths are understood.
2. Treat every generated artifact as derived until proven otherwise. Generated
   HTML, result reports, and cache files may be regenerated, but retained
   evidence under results/ and benchmarks/ must not be deleted casually.
3. Separate source defects from generated-staleness defects. If a generated HTML
   page is stale because a source Markdown file changed, fix the source,
   rebuild, and report both the source edit and the regenerated page.
4. Preserve user changes. If a file holds unrelated user edits, work around them
   and never revert them.
5. Apply patches narrowly. If a broad refactor seems attractive, document why it
   is necessary first.
6. Prefer project-native helpers over new custom logic.
7. Use deterministic commands and record the exact commands you ran.
8. When a full command is too expensive, run the strongest relevant reduced
   command and quote the exact full command that remains to be run.
9. Never convert a warning into a pass by hiding evidence. Make every skipped,
   missing, deferred, or incomplete check explicit.
10. End every phase with evidence: inspected files, findings, changes, tests,
    and residual risks.

================================================================================
4. SEVERITY RUBRIC
================================================================================

- Critical: incorrect scientific results; corrupted or mutated reference
  evidence; nondeterministic output where determinism is promised; destructive
  path handling (delete/write outside the project root or into protected
  evidence); broken canonical runner; a release/validation claim that
  misrepresents what was actually verified.
- High: wrong defaults (backend, worker count, output root, console behavior, or
  seed policy); broken all-optimizer campaign; broken validation truthfulness;
  major documentation contradiction; broken package metadata; incorrect CEC
  suite metadata (function IDs, dimensions, eval budgets, optimum/target
  handling); or a performance change that alters scientific behavior.
- Medium: missing tests for important behavior; stale docs for a working
  feature; incomplete or unprefixed generated HTML; weak gate coverage; a slow
  but correct runtime path; or a confusing user workflow.
- Low: wording polish, duplicated explanations, minor command-clarity issues,
  nonblocking lint cleanup, or organization improvements.

Assign exactly one severity per finding. When in doubt between two levels,
choose the higher and say why.

================================================================================
5. EVIDENCE STANDARD
================================================================================

- Code findings: cite file path, function or class, and line number.
- Documentation findings: cite the source Markdown and the generated HTML page
  when both are affected (and name the expected folder-prefixed HTML file).
- Benchmark findings: cite suite, function range, dimension rule, data source,
  and the affected command.
- Reproducibility findings: cite seed policy, generator, run index, optimizer,
  suite, function, dimension, and run count.
- Performance findings: cite the measured command, hardware/thread context,
  before/after timing if available, and whether JIT warmup was included.
- Packaging/gate findings: cite the metadata key, manifest line, config lock
  entry, or gate command condition.

================================================================================
6. REVIEWER RESPONSIBILITY MATRIX
================================================================================

- Principal scientific-computing architect: verify package boundaries; verify
  source/generated/evidence separation; identify coupling and architecture
  risks; approve or reject broad-refactor proposals.
- Numerical optimization and metaheuristics expert: inspect optimizer
  interfaces; check evaluation accounting; check bounds handling; check option
  propagation; avoid algorithm rewrite unless explicitly requested.
- CEC benchmark and experimental-protocol expert: verify suite metadata; verify
  function and dimension coverage; verify objective construction; verify
  reference-comparison protocol; verify reduced-versus-full campaign labeling.
- Reproducibility and deterministic-computation expert: verify seed schedules;
  verify fair-start behavior; verify serial/parallel determinism; verify
  environment metadata; verify replay procedures.
- Python packaging and release engineer: verify pyproject metadata; verify
  MANIFEST rules; verify package data; verify sdist/wheel boundaries.
- Performance, parallelism, and Numba specialist: verify worker defaults; verify
  thread-oversubscription controls; verify Numba availability and fallback;
  identify safe optimization candidates; reject performance changes that alter
  scientific behavior.
- Test strategy and quality-gate engineer: map tests to behavior; identify
  missing high-risk tests; verify smoke, lint, selected type checks, and
  profile-lock checks; separate slow campaign tests from normal gates.
- Documentation, API, and developer-experience reviewer: verify docs
  completeness; verify generated HTML; verify API docstrings; verify
  command copy-pasteability; verify docs do not contradict runtime behavior.
- Security, path-safety, and generated-artifact reviewer: verify output roots;
  verify cleanup safety; verify no writes into protected evidence; verify no
  destructive file operation lacks a root check; verify generated caches are
  excluded from any packaged artifact.
- Research-user workflow reviewer: verify install-to-result workflow; verify
  campaign execution path; verify result interpretation; verify
  validation/reporting flow; verify troubleshooting guidance.
- Statistical-analysis and publication-reporting expert: verify the gsk-stats CLI
  and the --stats flag against src/gsk_family/analysis/; verify the 7-algorithm
  panel construction (Friedman ranks, pairwise Wilcoxon + Holm, Vargha-Delaney,
  Nemenyi); verify the proposed-vs-comparator data sources are kept distinct and
  the comparator tables stay read-only; verify eGSK's panel cells are sourced
  from the committed reference CSVs (eGSK is itself a runnable optimizer, so do
  not flag egsk-runnable documentation as an error);
  verify the generated LaTeX/figure fragments are consistent with the papers/
  review-pack and that no statistical claim exceeds the committed evidence.

================================================================================
7. MINIMUM ARTIFACT INVENTORY TO INSPECT
================================================================================

- Root operating files:
  README.md, SKILL.md, runbook.md, run.py, pyproject.toml, MANIFEST.in,
  CITATION.cff, requirements.txt, requirements-dev.txt
- Source package (each subpackage ships a README.md to cross-check):
  src/gsk_family/types.py, src/gsk_family/stats.py,
  src/gsk_family/cli/ (list.py, run.py, validate.py),
  src/gsk_family/runners/ (config.py, run_experiment.py, output.py,
    verification.py, parallel.py, performance.py, seed_policy.py),
  src/gsk_family/common/ (rng.py, threefry_rng.py, reference_rng.py,
    population.py, bounds.py, donors.py, reduction.py, numeric_compat.py),
  src/gsk_family/optimizers/ (gsk.py, agsk.py, apgsk.py, fdb_agsk.py,
    atmals_gsk.py, egsk.py, dt_gsk.py + helpers, incl. the dt-gsk support
    modules _dt_profiles.py, _dt_rng.py, _dt_core.py, _dt_subsystems/),
  src/gsk_family/benchmark_adapter/ (factory.py, problem.py, protocol.py),
  src/gsk_family/cli/stats.py (the gsk-stats entry point),
  src/gsk_family/analysis/ (family_report.py, result_loader.py,
    statistical_tests.py, statistics.py, figures.py, latex_tables.py,
    project_policy.py)
- Benchmarks and evidence:
  benchmarks/cec_suite_python/ (cec2011, cec2013, cec2013lsgo, cec2017, cec2020),
  benchmarks/cec_reference_results/ (committed 7-optimizer reference evidence for
  all five CEC suites, each with all seven panel optimizers),
  benchmarks/README.md
- Configurations:
  configs/smoke.yml, configs/all_optimizers_smoke.yml,
  configs/all_optimizers_cec2017_reduced.yml, configs/all_cec2011.yml,
  configs/all_cec2017.yml, configs/agsk_cec2020.yml,
  configs/golden_validation_smoke.yml, configs/performance_campaign_smoke.yml,
  configs/README.md
- Documentation (six themed subfolders + two top-level entry points):
  docs/index.md, docs/LICENSES.md,
  docs/getting-started/, docs/reference/, docs/algorithms/, docs/development/,
  docs/research/, docs/prompt/,
  docs/html/index.html, docs/html/api_index.html, docs/html/search_index.json
- Scripts (exactly twenty-one + a README.md; see the ground-truth list above):
  scripts/build_docs_html.py, scripts/validate_profile_lock.py,
  scripts/parity_trace.py, scripts/wilcoxon_reference.py,
  scripts/run_gsk_family.py, scripts/run_ablation.py, scripts/run_all_cec2017.py
  (and the four sibling run_all_<suite>.py launchers),
  scripts/run_revision_experiments.py, scripts/run_e1_basis_contrast.py
- Statistics & analysis surface:
  src/gsk_family/cli/stats.py (gsk-stats), the runner --stats flag,
  src/gsk_family/analysis/ (family_report.py, result_loader.py,
  statistical_tests.py, statistics.py, figures.py, latex_tables.py,
  project_policy.py), and the papers/ review-pack
  (the on-demand review-pack PDF and its sources)
- Tests:
  tests/test_imports.py, tests/unit/, tests/smoke/, tests/regression/,
  tests/performance/

================================================================================
8. PER-PHASE OUTPUT TEMPLATE
================================================================================

For every phase report, in order:

1. Phase verdict: PASS, WARN, FAIL, or DEFERRED.
2. Files inspected.
3. Commands run (verbatim) and their outcomes.
4. Findings by severity, each with path:line evidence.
5. Changes applied, if any (narrow diffs).
6. Evidence generated or updated.
7. Commands deferred and exactly why.
8. Residual risk.
9. Next action.

A phase is PASS only when its phase-specific acceptance criteria (stated in each
phase below) are all met. Otherwise it is WARN (criteria met with caveats), FAIL
(a criterion is violated), or DEFERRED (a criterion could not be evaluated; say
what is required to finish).

================================================================================
9. PATCH DECISION RULES
================================================================================

- Patch immediately when the fix is narrow, low risk, and directly supports the
  phase goal.
- Do not patch optimizer algorithm logic unless explicitly requested.
- Do not hand-edit generated HTML; patch source docs or docstrings, then
  rebuild with scripts/build_docs_html.py.
- Do not patch imported reference evidence during normal review.
- Do not remove results/ or benchmark evidence during cleanup without explicit
  permission.
- Prefer adding a focused regression or unit test when a high-risk behavior is
  fixed.

================================================================================
10. GLOBAL ACCEPTANCE GATES
================================================================================

- python run.py --help succeeds and its flags match the documented contract.
- A tiny direct smoke run succeeds (see Phase 4 command).
- python -m pytest -q passes, or every failure is explained with an exact cause.
- python -m ruff check src tests scripts passes after code edits.
- python scripts/build_docs_html.py rebuilds HTML after any doc/docstring edit.
- Root Markdown inventory is intentional: the three operating files (README.md,
  SKILL.md, runbook.md), the six governance docs, FINAL_RELEASE_REPORT.md, and
  REPO_MAP.md -- no other stray root-level Markdown.
- The forbidden upstream-platform token appears only in
  docs/reference/seed_policy.md and its HTML twin.
- No generated cache (__pycache__/, .pytest_cache/, .ruff_cache/, .mypy_cache/,
  *.pyc, *.nbc, *.nbi) remains outside excluded evidence folders after final
  polish.
- Any skipped expensive command is listed with the exact deferred command.

================================================================================
PHASE 0: SAFETY, BASELINE, AND WORKSPACE AUDIT
================================================================================

Goal: establish a safe, read-only baseline and a map of protected paths before
touching anything.

Tasks:

1. Confirm the working directory is the project root above.
2. Record git status for this Python project only (do not touch sibling repos).
3. Identify user changes and generated outputs without reverting them.
4. Identify ignored/generated locations and confirm they are git-ignored:
   results/, docs/html/, __pycache__/, .pytest_cache/, .ruff_cache/,
   .mypy_cache/, *.pyc, *.nbc, *.nbi.
5. Confirm no planned command writes into imported reference/evaluator evidence
   (benchmarks/cec_reference_results/ or benchmarks/cec_suite_python/ data files).
6. Record Python version, package metadata, dependency versions, and the logical
   CPU count (so the safe two-worker default and CEC cap behavior can be
   predicted).

Suggested commands:

    git -C . status --short
    python --version
    python -c "import os; cores=os.cpu_count() or 1; workers=max(1, min(2, cores)); print('logical_cores=', os.cpu_count(), 'default_workers=', workers, 'auto_cec2017_f21_f30_workers=', min(workers, 8))"
    python -c "import importlib.metadata as m; print(m.version('gsk-family'))"

Acceptance criteria:

- Baseline git status, protected-path list, and generated-artifact policy are
  recorded. No edits have been made. Predicted default worker count and CEC
  effective worker count are stated.

Deliver: baseline status summary; protected-paths list; generated-artifact
policy; immediate risks before editing.

================================================================================
PHASE 1: REPOSITORY STRUCTURE AND OWNERSHIP REVIEW
================================================================================

Goal: confirm the on-disk layout matches the documented structure and the root
Markdown policy.

Tasks:

1. Enumerate root files and directories.
2. Verify the root Markdown policy: three operating Markdown files (README.md,
   SKILL.md, runbook.md) plus the six governance docs (PROJECT_RULES.md,
   DESIGN_GUIDE.md, ARCHITECTURE.md, BENCHMARK_RULES.md, CODING_STANDARD.md,
   PERFORMANCE_RULES.md), FINAL_RELEASE_REPORT.md, and REPO_MAP.md. Confirm:
   - README.md is the detailed landing page;
   - SKILL.md is the project agent file;
   - runbook.md is the concise copy-paste command reference and its commands
     match the runner contract;
   - REPO_MAP.md is the top-level navigation index;
   - all review/documentation prompts live under docs/prompt/ (not the root);
   - flag any root-level Markdown outside that intentional set as a
     relocation/removal candidate.
3. Confirm the docs/ tree has its six themed subfolders (getting-started/,
   reference/, algorithms/, development/, research/, prompt/) plus docs/index.md
   and docs/LICENSES.md; no canonical guide is a stray top-level docs/*.md file.
4. Inspect pyproject.toml, MANIFEST.in, run.py, docs/index.md, and
   docs/reference/project_structure.md.
5. Compare the documented structure (docs/reference/project_structure.md and the
   subpackage README.md files) against the actual files; flag drift.
6. Classify every major area as source, tests, docs, configs, benchmark code,
   imported evidence, generated HTML, generated results, or scripts.
7. Confirm scripts/ holds exactly the twenty-one documented Python files (plus a
   README.md) and nothing else (no phase/release tooling). Flag any unexpected
   script.

Suggested commands:

    python -c "import os; [print(f) for f in sorted(os.listdir('.')) if f.endswith('.md')]"
    python -c "import os; [print(f) for f in sorted(os.listdir('scripts')) if f.endswith('.py')]"

Acceptance criteria:

- Root Markdown set is the intentional inventory (README.md, SKILL.md, runbook.md,
  the six governance docs, FINAL_RELEASE_REPORT.md, REPO_MAP.md); the six docs
  subfolders exist; scripts/ has exactly the twenty-one documented Python files (plus a
  README.md); docs/reference/project_structure.md matches reality (or its drift
  is filed).

Deliver: repository map; ownership table; missing/stale structure-doc list;
cleanup candidates.

================================================================================
PHASE 2: PACKAGING, INSTALLATION, AND CLI ENTRY POINTS
================================================================================

Goal: confirm the package installs cleanly and every advertised entry point
resolves.

Tasks:

1. Inspect package metadata in pyproject.toml: name (gsk-family), version,
   description, readme path, license files, requires-python, dependency ranges,
   optional dev dependencies, package discovery (where = ["src", "."]; include
   gsk_family*, benchmarks*), include-package-data, and package data.
2. Verify README/install docs align with pyproject metadata.
3. Verify the five console scripts resolve to real callables (the exact set in
   pyproject.toml [project.scripts]):
   gsk-list -> gsk_family.cli.list:main
   gsk-run -> gsk_family.cli.run:main
   gsk-family-run -> gsk_family.cli.run:main
   gsk-validate -> gsk_family.cli.validate:main
   gsk-stats -> gsk_family.cli.stats:main
   Do not invent any other entry point (there is no gsk-analyze). Confirm the set
   against pyproject.toml before quoting it; if it has changed, file the drift.
4. Confirm python run.py is the canonical source-checkout command and that
   scripts/run_gsk_family.py either delegates to the canonical runner or is
   documented as a wrapper.
5. Verify path handling is project-root safe and does not rely on a global
   os.chdir without a scoped try/finally.

Suggested commands:

    python run.py --help
    python scripts/run_gsk_family.py --help
    python -m pip install -e ".[dev]"
    python -c "import importlib; [importlib.import_module(m) for m in ('gsk_family.cli.list','gsk_family.cli.run','gsk_family.cli.validate')]; print('entry-point modules import OK')"

Acceptance criteria:

- Editable install succeeds; all five console scripts and run.py --help run; no
  unscoped os.chdir; metadata and README agree.

Deliver: packaging-readiness verdict; CLI entry-point map; install risks;
concrete fixes.

================================================================================
PHASE 3: RUNNER, CONFIGURATION, AND OUTPUT SCHEMA REVIEW
================================================================================

Goal: trace one experiment end to end and confirm defaults and emitted files.

Tasks:

1. Trace the direct-run path from run.py into: CLI argument parsing -> config
   loading and normalization -> defaults -> benchmark problem creation -> seed
   schedule generation -> optimizer dispatch -> parallel/serial scheduling ->
   result writing -> validation/comparison hooks -> final status reporting.
2. Inspect: src/gsk_family/cli/run.py, src/gsk_family/runners/config.py,
   src/gsk_family/runners/run_experiment.py, src/gsk_family/runners/output.py,
   src/gsk_family/runners/verification.py, src/gsk_family/runners/parallel.py,
   src/gsk_family/runners/seed_policy.py, docs/reference/result_schema.md,
   docs/getting-started/user_guide.md, docs/getting-started/configuration.md.
3. Verify defaults against code (not against the docs alone):
   - parallel default enabled, backend "process";
   - automatic worker default = min(2, logical_cores) with a floor of 1, and CEC2017 F21-F30 cap = 8 for automatic process runs;
   - default output root = results/_run_all;
   - console logging default enabled (console_log = True);
   - seed policy default = "unified";
   - generation-log behavior documented (generation_logs default and the
     --generation-logs / --no-generation-logs override);
   - convergence graph behavior documented (convergence_graphs default and the
     --convergence-graphs / --no-convergence-graphs override).
4. Verify the output artifacts and their layout under
   results/_run_all/<optimizer>/<suite>/:
   - summary/ per-run table (per_run.csv) with %.10e best_fitness/error and
     %.6f runtime_seconds, plus its documented column order;
   - summary/ per-function summary table (<optimizer>_<suite>_D<dim>.csv:
     Function, Best, Median, Mean, Worst, SD);
   - curves/ median-run convergence files (Figure_F<func>_D<dim>_Run#<run>.csv,
     columns Eval, BestError, Log10Error, both error columns %.16e);
   - curves/graphs/ plots when convergence_graphs is enabled; CSV curves remain
     present when it is disabled;
   - gen_logs/ checkpoint logs;
   - seed_schedule.csv and environment.json;
   - profile.json when --profile is set.
5. Confirm overwrite/resume behavior (--overwrite) is documented and safe.

Acceptance criteria:

- The end-to-end trace is complete; every default above matches code; the output
  schema matrix matches what output.py actually writes (byte formats included).

Deliver: end-to-end runner trace; default-value audit (code vs docs);
output-schema matrix; any broken/stale command example.

================================================================================
PHASE 4: CONSOLE OUTPUT AND USER EXPERIENCE REVIEW
================================================================================

Goal: confirm the console output is informative, honest, and free of per-run
noise.

Tasks:

1. Run the tiny smoke command and inspect the console output:

    python run.py --root . --optimizer gsk --suite sphere --function 1 --dimension 4 --runs 1 --max-evaluations 80 --overwrite

2. Confirm the output contains: a campaign header; optimizer section(s); a
   configuration summary; parallel/worker/Numba status; function-by-function
   summary row(s); `[finalize]` progress bars; and a final status line.
3. Confirm the output does NOT contain: per-run heartbeat lines; noisy
   generation logs interleaved with the summary table; or a misleading
   "skipped"/"all passed" message when work was not actually done.
4. Re-run with --quiet and confirm progress output is suppressed.
5. Compare console behavior against the examples in the docs and flag drift.

Acceptance criteria:

- The smoke run exits 0; the table prints one row per finished function with no
  heartbeat lines; finalization bars appear after the table; --quiet suppresses
  progress; documented console examples match observed output.

Deliver: console-output verdict; UX issues; exact stale text to remove.

================================================================================
PHASE 5: OPTIMIZER INTERFACE AND IMPLEMENTATION REVIEW
================================================================================

Goal: confirm all seven optimizers honor the shared interface and account
evaluations and bounds correctly, without rewriting their math.

Tasks:

1. Inspect the interface contracts: src/gsk_family/types.py,
   src/gsk_family/optimizers/__init__.py,
   docs/reference/python_optimizer_interface.md,
   docs/reference/module_dependencies.md.
2. For each optimizer (gsk, agsk, apgsk, fdb-agsk, atmals-gsk, egsk, dt-gsk)
   check: interface compliance, option handling/propagation, evaluation accounting
   (nfes vs max-evaluations), bounds handling/repair, return-structure shape,
   and deterministic behavior under a fixed seed.
3. Do NOT rewrite core optimizer logic unless explicitly requested.
4. Flag only: API mismatches; missing tests; unsafe shared/mutable state;
   incorrect evaluation counts; nondeterminism; poor error handling; avoidable
   per-iteration allocations; and stale documentation.
5. Confirm each optimizer's helper module (e.g. fdb_scores.py,
   atmals_helpers.py, _kernels.py) is covered by the matching
   tests/unit/test_*_helpers.py.
6. Confirm the per-optimizer docs explain expected inputs, outputs, local search
   (where applicable), bounds repair, population behavior, and result artifacts.

Acceptance criteria:

- All seven optimizers satisfy the documented interface; evaluation accounting and
  bounds repair are verified; each helper module has matching unit coverage; no
  algorithmic rewrites were made.

Deliver: optimizer-interface matrix; defect/risk list; documentation gaps;
behavior-preserving performance candidates.

================================================================================
PHASE 6: SHARED NUMERICAL HELPERS AND DETERMINISM REVIEW
================================================================================

Goal: confirm the RNG stack and shared helpers are deterministic and reproduce
their reference streams bit-for-bit.

Tasks:

1. Inspect: src/gsk_family/common/rng.py, threefry_rng.py, reference_rng.py,
   population.py, bounds.py, donors.py, reduction.py, numeric_compat.py.
2. Verify fair-start population behavior is consistent across optimizers.
3. Verify seed formulas and run-index handling match
   src/gsk_family/runners/seed_policy.py (reference vs unified vs native/derived;
   the reference partition uses linear seeds base + 9973*func + (run-1) for
   gsk/atmals-gsk and product seeds dim*func*run for agsk/apgsk/fdb-agsk).
4. Verify the random-number generators:
   - Only threefry (default), twister, and seed are supported; every other
     label raises "Unsupported RNG generator".
   - Each reproduces its external reference stream bit-for-bit: threefry counter
     seeding ((S+2j+1)<<32)|(S+2j); twister init_genrand + genrand_res53; seed
     mcg16807 with x0 = (seed << 16) mod (2^31 - 2^15). Known-answer tests in
     tests/unit/test_rng.py must pass; seeding, conversion, and draw order are
     unchanged.
   - Matrix draws fill column-major; randi = floor(imax*rand)+1 and
     randperm = argsort(rand(n)).
   - State copy/restore round-trips for every generator; a removed state
     generator must not be re-added as a placeholder.
5. Verify deterministic serial/parallel behavior: the same configuration yields
   identical results regardless of backend or worker count.
6. Verify tests cover the critical helper behavior.

Suggested tests:

    python -m pytest tests/unit/test_seed_policy.py tests/unit/test_rng.py tests/unit/test_numeric_compat.py tests/unit/test_population.py tests/unit/test_bounds.py -q

Acceptance criteria:

- All RNG known-answer tests pass; unsupported labels raise; seed formulas match
  code; serial and parallel runs are bit-identical for a fixed config.

Deliver: determinism verdict; helper-risk matrix; missing tests.

================================================================================
PHASE 7: BENCHMARK ADAPTER AND CEC SUITE REVIEW
================================================================================

Goal: confirm suite metadata and data loading are correct and that reference
data stays immutable.

Tasks:

1. Inspect: benchmarks/cec_suite_python/,
   benchmarks/cec_reference_results/,
   src/gsk_family/benchmark_adapter/ (factory.py, problem.py, protocol.py),
   docs/reference/benchmark_protocol.md, docs/reference/benchmark_mapping.md.
2. For every suite (cec2017, cec2011, cec2020, cec2013, cec2013lsgo, sphere)
   verify: function IDs; supported dimensions and native-dimension behavior;
   excluded/deprecated functions (e.g. CEC2017 F2 exclusion in the run-all
   path); max-evaluation rules; target-error handling; optimum values;
   shift/rotation/transformation data loading; Numba path availability; and the
   reference-result mapping.
3. Confirm CEC data files are immutable and their provenance is documented.
4. Confirm validation commands never write into reference evidence.
5. Confirm reduced-budget CEC tests are not described as full evidence.

Suggested commands:

    python -c "from gsk_family.benchmark_adapter import protocol as p; print([n for n in dir(p) if 'suite' in n.lower() or 'dimension' in n.lower() or 'function' in n.lower()])"
    python -m pytest tests/unit/test_benchmark_adapter.py tests/unit/test_reference_loader.py -q

Acceptance criteria:

- Each suite's function/dimension/budget metadata matches the adapter; data
  files are confirmed read-only with documented provenance; no validation path
  writes into evidence.

Deliver: suite-support matrix; CEC correctness risks; data/provenance risks;
validation depth by suite.

================================================================================
PHASE 8: VALIDATION AND REFERENCE-PARITY REVIEW
================================================================================

Goal: confirm gsk-validate is truthful and the per-generator / per-optimizer
parity story matches the evidence.

Tasks:

1. Inspect: src/gsk_family/cli/validate.py,
   src/gsk_family/runners/verification.py, docs/research/validation_report.md,
   docs/research/reproducibility.md, and scripts/parity_trace.py.
2. Confirm gsk-validate defaults are truthful and an all-skipped validation
   exits nonzero.
3. Confirm missing reference paths are reported clearly.
4. Confirm comparator references are packaged or that validation is documented
   as source-checkout-only.
5. Confirm tolerance and comparison logic are documented.
6. Confirm generated/reference function matching is transparent.
7. Confirm bit-level RNG parity claims:
   - threefry/twister/seed reproduce the imported reference streams bit-for-bit
     (tests/unit/test_rng.py known-answer tests);
   - rand-only optimizers (gsk, agsk, apgsk, atmals-gsk) match the imported
     reference convergence to machine precision, with the residual documented as
     benchmark floating-point only;
   - FDB-AGSK (score-ranked donor selection)
     divergences are documented as floating-point/solver effects, not RNG.
   - DT-GSK reproduces its sibling reference implementation byte-for-byte
     (validated on sphere and CEC2017 across D=10/30/50/100); it always uses
     threefry with the unified shared seed under every seed policy, and its
     byte stability is locked by tests/regression/test_dt_gsk_byte_stable.py
     (D>=50 determinism relies on single-threaded numba/BLAS thread pinning).
8. Use scripts/parity_trace.py to localize any claimed divergence to the first
   differing checkpoint (random stream -> initial population -> per-generation
   best-so-far -> final result).

Suggested commands:

    python -m gsk_family.cli.validate --references benchmarks/cec_reference_results
    python scripts/parity_trace.py --optimizer gsk --suite cec2017 --function 5 --dimension 10 --run 1 --output results/_parity/py_gsk.json

Acceptance criteria:

- gsk-validate reports truthfully and exits nonzero when nothing was validated;
  parity claims are bounded by the evidence; per-generator and per-optimizer
  parity status is stated explicitly.

Deliver: validation-truthfulness verdict; reference-comparison evidence summary;
RNG bit-parity status (per generator and per optimizer); missing evidence and
upgrade path.

================================================================================
PHASE 8B: STATISTICAL-ANALYSIS AND PUBLICATION-REPORTING REVIEW
================================================================================

Goal: confirm the gsk-stats CLI, the runner --stats flag, and the
src/gsk_family/analysis/ layer build a correct, honest 7-algorithm GSK-family
statistical panel, and that its outputs are consistent with the papers/
review-pack without overclaiming.

Tasks:

1. Inspect: src/gsk_family/cli/stats.py, the --stats handling in
   src/gsk_family/cli/run.py and src/gsk_family/runners/, and
   src/gsk_family/analysis/ (family_report.py, result_loader.py,
   statistical_tests.py, statistics.py, figures.py, latex_tables.py,
   project_policy.py), plus docs/research/statistical_analysis.md.
2. Verify the panel composition: the seven algorithms are the seven FAMILY
   optimizers (gsk, agsk, apgsk, fdb-agsk, atmals-gsk, egsk, dt-gsk). eGSK is a
   runnable optimizer (port; scipy-SLSQP substitutes fmincon), and its panel
   cells are the comparator of record sourced from the committed reference CSVs;
   do not flag egsk-runnable documentation as an error.
3. Verify the statistical methods are implemented and described correctly:
   Friedman test with mean ranks; pairwise Wilcoxon signed-rank tests with a Holm
   multiple-comparison correction; Vargha-Delaney effect sizes; Nemenyi
   critical-difference diagrams. Flag any test applied to the wrong data shape,
   any missing correction, or any mislabeled statistic.
4. Verify the data sources follow the reference-first single-source-of-truth
   policy (result_loader.py::load_algorithm): every panel algorithm — the
   proposed optimizer included — loads from the committed read-only tables under
   benchmarks/cec_reference_results/<suite>/<optimizer>/, and a locally
   reproduced run under results/_run_all/<optimizer>/<suite>/summary/ is only a
   fallback for cells the reference tree lacks.
   Confirm no analysis path writes into the reference tables, and that variant
   reference schemas (e.g. eGSK's column order) are handled without corrupting
   data.
5. Verify the analysis output goes to results/_run_all/_analysis/<suite>/ by
   default (or --out), is treated as generated, and is not packaged as evidence.
6. Verify CEC2017's F2 exclusion is respected wherever the panel enumerates
   functions, and that dimension coverage (D=10/30/50/100) matches the suite.
7. Cross-check the generated LaTeX/figure fragments against the papers/
   review-pack (the on-demand papers/DT-GSK-CEC2017-review.pdf and its table/figure sources):
   confirm the reported ranks, effect sizes, and significance match the committed
   results and that no claim in the docs or paper exceeds the committed evidence.
   The review-pack PDF is built by python papers/scripts/generate_review_pack.py
   (matplotlib PdfPages, no LaTeX toolchain required); it assembles the
   7-algorithm convergence grids from CheckpointErrors_<alg>_F<k>_D<dim>.csv and
   logs any missing curve to papers/DT-GSK-CEC2017-review_missing.log rather than
   fabricating it. Do NOT regenerate or edit papers/ unless explicitly asked; flag
   inconsistency as a finding instead.

Suggested commands:

    python -c "import gsk_family.cli.stats as s; print(s.__doc__.splitlines()[0])"
    gsk-stats --suite CEC2017 --dims 10 --no-figures --out results/_analysis_smoke

Acceptance criteria:

- The panel is the 7 runnable optimizers (eGSK's cells sourced from the committed
  reference CSVs); the statistical
  methods (Friedman, Wilcoxon+Holm, Vargha-Delaney, Nemenyi) are correct and
  correctly described; loading is reference-first (reference tables primary for
  every algorithm, results/_run_all/ fallback only) and the reference tables
  stay read-only; outputs land under the analysis output root;
  and the generated fragments are consistent with the papers/ review-pack with no
  overclaimed statistic.

Deliver: statistical-analysis verdict; panel-composition and method-correctness
findings; data-source/read-only-evidence audit; paper-consistency report; any
overclaimed statistic.

================================================================================
PHASE 9: PERFORMANCE, PARALLELISM, AND NUMBA REVIEW
================================================================================

Goal: confirm the default process backend is correct, self-healing, and
behavior-preserving, and that the thread backend's hazard is documented.

Tasks:

1. Inspect: src/gsk_family/runners/parallel.py,
   src/gsk_family/runners/performance.py,
   src/gsk_family/runners/run_experiment.py, the benchmark _numba modules, the
   optimizer loops, and docs/research/performance.md.
2. Verify:
   - default worker policy (2 workers on machines with at least two logical cores, otherwise 1; CEC2017 F21-F30 cap = 8 for automatic process runs);
   - --serial path;
   - --workers override;
   - Numba auto-cap behavior (numba_threads: 0 during parallel runs);
   - selected-suite warmup and full-suite warmup (--warmup, --warmup-scope
     selected|suite);
   - deterministic result ordering (out-of-order completion, in-order writes);
   - profile metadata (profile.json) when --profile is set;
   - backend selection: the default "process" backend, the "thread" backend, and
     the --serial path each dispatch correctly and produce identical results;
   - process-backend self-healing: when a worker process dies, the process
     backend rebuilds the pool and retries the affected cell (the rebuild budget
     is bounded -- max_pool_rebuilds in run_experiment.py); if rebuilds keep
     failing it finishes that cell on the serial backend, so a run never hangs
     or aborts mid-campaign. Confirm this fallback is exercised and reported, not
     silent;
   - thread-backend hazard: the "thread" backend is GIL-bound and can contend or
     deadlock when parallel Numba kernels run from many Python threads at once.
     Flag any doc, default, or helper that recommends "thread" without this
     caveat, and confirm the safe default stays "process";
   - memory bounding: --workers N bounds live worker processes and therefore caps
     aggregate per-process memory; confirm lowering N is the documented remedy
     for memory pressure at large dimensions.
3. Categorize bottlenecks: objective evaluation; optimizer Python loops;
   repeated allocations; sorting/ranking; plotting/report I/O; graph rendering;
   generation logs;
   validation I/O; local search; JIT warmup; nested-thread contention.
4. Recommend only optimizations that preserve scientific behavior.

Suggested commands:

    python run.py --root . --optimizer gsk --suite sphere --function 1 --dimension 4 --runs 2 --max-evaluations 200 --serial --overwrite
    python run.py --root . --optimizer gsk --suite sphere --function 1 --dimension 4 --runs 2 --max-evaluations 200 --parallel-backend process --overwrite
    # The two runs above must produce identical per_run.csv numbers.

Acceptance criteria:

- process/thread/serial dispatch produce identical results; the process-backend
  self-heal-then-serial-fallback path is confirmed and reported; the thread
  hazard is documented; the safe default is "process".

Deliver: performance verdict; safe-optimization list; risky-optimization list to
defer; benchmark/profiling commands.

================================================================================
PHASE 10: TEST STRATEGY AND QUALITY-GATE REVIEW
================================================================================

Goal: confirm tests cover the high-risk behavior and the standing gates are
correct.

Tasks:

1. Inspect all tests under tests/ (test_imports.py, unit/, smoke/, regression/,
   performance/).
2. Map tests to behavior: imports; CLI; runner; config parsing; benchmarks;
   optimizers and their helpers; RNG/seed policy; validation
   (tests/regression/test_validation_ladder.py); parallel determinism
   (tests/unit/test_parallel.py, tests/performance/test_parallel_runner.py);
   result schema; docstrings (tests/unit/test_docstrings.py); and
   documentation commands (tests/smoke/test_documentation_commands.py).
3. Confirm the standing gates are present and correct: pytest; the tiny smoke
   command; ruff over src tests scripts; selected mypy over the high-risk
   packages; profile-lock validation; and the docs HTML build.
4. Confirm tests/smoke/test_documentation_commands.py's required-path list
   matches the ACTUAL docs/root layout after the prompt move (it must include
   the real root operating files and the real docs/ paths, and must not point at
   files that no longer exist at their old location). Flag any mismatch as a
   Medium finding.
5. Identify slow tests and confirm they are marked or separated from the normal
   gates.
6. Ensure tests use temporary output roots and never modify imported evidence.

Suggested commands:

    python -m pytest -q
    python -m ruff check src tests scripts
    python -m mypy src/gsk_family/cli src/gsk_family/runners src/gsk_family/common
    python scripts/validate_profile_lock.py --root .

Acceptance criteria:

- pytest, ruff, and the docs build pass (or each failure is explained);
  profile-lock validation passes; the documentation-command path list matches
  the current layout; no test mutates evidence.

Deliver: coverage matrix; gate recommendation; missing high-risk tests; failing
or flaky tests.

================================================================================
PHASE 11: DOCUMENTATION, HTML, AND API REVIEW
================================================================================

Goal: the docs/ tree must be polished, organized into its six themed subfolders,
free of duplication and stale material, fully reflected in regenerated HTML, and
detailed enough to be understood on its own.

The docs/ tree is organized into six themed subfolders (getting-started/,
reference/, algorithms/, development/, research/, prompt/) plus the top-level
entry points docs/index.md and docs/LICENSES.md. Confirm files sit in the right
subfolder and that docs/index.md and the generated HTML sidebar grouping reflect
that structure.

Tasks:

1. Inspect the full docs tree: docs/index.md, docs/LICENSES.md,
   docs/getting-started/, docs/reference/, docs/algorithms/, docs/development/,
   docs/research/, docs/prompt/, docs/html/index.html, docs/html/api_index.html,
   docs/html/search_index.json.
2. Confirm docs cover: installation; quickstart; direct CLI; YAML configs; all
   seven panel optimizers; all six benchmark suites; random-number generators;
   result schema; validation; reproducibility; parallel behavior; Numba behavior;
   the statistical-analysis surface (gsk-stats / --stats and
   docs/research/statistical_analysis.md, where eGSK is a runnable port whose
   panel cells are sourced from the committed reference CSVs); the
   per-suite C++/Python equivalence reviews under docs/reference/; troubleshooting;
   and the review/documentation prompts under docs/prompt/.
3. Audit docs/ organization and polish:
   - every Markdown file is reachable from docs/index.md and the navigation;
     flag orphaned or unlinked files;
   - files sit in the correct themed subfolder; flag misplaced files and
     inconsistent names;
   - generated HTML page names are folder-prefixed after a source Markdown file
     (for example docs/reference/diagrams.md builds to reference_diagrams.html,
     and docs/prompt/project-review.md builds to prompt_project-review.html);
     confirm regenerated names follow this convention and no stale unprefixed
     page survives;
   - the root runbook.md command reference is current and matches the runner
     contract; confirm docs/ does not duplicate it divergently;
   - the layout matches docs/reference/project_structure.md; update it if the
     structure changed.
4. Detect and remove duplicate or redundant documentation:
   - flag files whose content substantially overlaps another;
   - consolidate into one canonical page and replace the rest with a link, or
     delete the redundant copy;
   - keep the prompts under docs/prompt/ aligned in purpose (whole-project audit
     vs documentation depth vs documentation consistency vs inline documentation
     review) rather than divergent or duplicated; their stated cross-links must
     resolve.
5. Remove stale documentation, files, and references:
   - remove obsolete examples, superseded plans, completed planned/future
     wording, dead assets, and abandoned Markdown;
   - remove generated HTML and search-index entries for files that no longer
     exist;
   - flag documentation that references removed code, flags, options, generators,
     or tooling. In particular, flag any reference to a "phase" release/build
     script or a staged release methodology -- no such tooling exists in this
     project;
   - do not delete retained evidence under results/ unless requested.
6. Confirm docs are detailed, readable, and understandable: each page states its
   purpose and audience and links to related pages; commands and examples are
   runnable and current; long pages use headings, tables, and lists where they
   aid comprehension; terminology follows docs/reference/glossary.md.
7. Confirm source-Markdown local links resolve.
8. Confirm generated-HTML local links resolve.
9. Rebuild and update the HTML so every Markdown edit, removal, and
   consolidation is reflected; confirm the search index and API pages are
   regenerated and internally consistent.
10. Confirm public modules, classes, functions, and methods have useful
    docstrings (tests/unit/test_docstrings.py enforces a baseline).
11. Confirm stale planned/future wording is removed for completed work.

Suggested commands:

    python scripts/build_docs_html.py
    python -m pytest tests/smoke/test_documentation_commands.py tests/unit/test_docstrings.py -q

Acceptance criteria:

- Every Markdown file is reachable and correctly placed; HTML page names are
  folder-prefixed and current; the search index and API pages are regenerated;
  no orphaned/stale page survives; docstring and documentation-command tests
  pass; the docs/prompt/ files are aligned and cross-linked.

Deliver: documentation-completeness verdict; docs-folder organization report
(orphans, misplaced files, naming) confirming the six-subfolder layout;
duplicate/redundant-documentation report and consolidation plan; stale-doc and
file-removal list; readability assessment (weak/confusing pages);
broken-link report (Markdown and HTML); HTML/search-index regeneration
confirmation; API/docstring gaps.

================================================================================
PHASE 12: REPRODUCIBILITY AND RESEARCH WORKFLOW REVIEW
================================================================================

Goal: confirm a researcher can reproduce results exactly, with the full-budget
campaign command documented verbatim.

Tasks:

1. Inspect: docs/research/reproducibility.md, docs/reference/seed_policy.md,
   docs/research/researcher_handbook.md, docs/reference/benchmark_protocol.md,
   docs/reference/workflows.md, and configs/*.yml.
2. Confirm reproducibility coverage: environment setup; dependency ranges; seed
   formulas (unified vs reference); fair starts; deterministic serial/parallel
   runs; generated environment metadata (environment.json); experiment
   procedures; the reduced-versus-full campaign distinction; and the publication
   reproduction path.
3. Verify config examples are runnable and current; cross-check each config's
   declared fields against the runner contract.
4. Confirm the full CEC2017 all-optimizer command is documented exactly (the
   seven-optimizer — gsk,agsk,apgsk,fdb-agsk,atmals-gsk,egsk,dt-gsk — /
   function 1:30 / dimension 10,30,50,100 / runs 51 campaign), matching the
   accepted CLI syntax.

Acceptance criteria:

- The unified vs reference distinction is correct; every cited config is
  runnable; the full-campaign command matches the CLI; smoke vs full evidence is
  kept separate.

Deliver: reproducibility verdict; research-workflow gaps; config risks.

================================================================================
PHASE 13: SECURITY, PATH SAFETY, AND FILE-SYSTEM HYGIENE
================================================================================

Goal: confirm no path is built or deleted unsafely and no evidence can be
overwritten.

Tasks:

1. Search for unsafe path handling: global cwd changes; string-built shell
   paths; recursive deletes without a project-root check; writes into reference
   evidence; and unvalidated output roots.
2. Confirm any cleanup logic verifies paths stay inside the project root.
3. Confirm generated files and caches are git-ignored.
4. Confirm no secrets, absolute user-only temp paths, or accidental logs would
   be included in any packaged artifact.
5. Confirm both Windows and POSIX paths are handled where relevant (the codebase
   runs on Windows; output paths use pathlib).

Suggested commands (review the hits; do not assume a hit is a defect):

    # potentially unsafe operations to inspect
    rg -n "shutil.rmtree|os.remove|os.chdir|os.system|subprocess" src scripts
    rg -n "rmtree|unlink" src | rg -i "root|results|benchmarks"

Acceptance criteria:

- Every destructive operation is root-guarded; no write targets protected
  evidence; caches/secrets are excluded from packaging; path handling is
  cross-platform.

Deliver: path-safety verdict; risk list; cleanup patches.

================================================================================
PHASE 14: CODE POLISH AND DEAD-ARTIFACT REMOVAL
================================================================================

Goal: remove dead code and stale text without disturbing intentional
compatibility logic or retained evidence.

Tasks:

1. Remove stale code, unused imports, accidental unused variables, duplicate
   helpers, unreachable code, obsolete comments, and abandoned/duplicate files
   across src/, tests/, scripts/, and docs/ (coordinate docs/ cleanup with
   Phase 11).
2. Keep intentional compatibility calculations only with clear comments or
   targeted noqa markers.
3. Remove stale documentation, duplicate generated text, obsolete examples, and
   unused prompt fragments.
4. Remove generated caches: __pycache__/, .pytest_cache/, .ruff_cache/,
   .mypy_cache/, *.pyc, *.nbc, *.nbi.
5. Do not delete retained evidence under results/ unless explicitly requested.
6. Rebuild generated docs after any doc or docstring edit.
7. Re-run lint and confirm no generated cache remains outside excluded evidence
   folders.

Suggested command:

    python -m ruff check src tests scripts

Acceptance criteria:

- Ruff is clean; no dead artifact remains; intentional compatibility logic is
  preserved with a comment/noqa; HTML is rebuilt; evidence is untouched.

Deliver: removed stale files/code/docs list; retained generated-evidence list;
final polish verdict.

================================================================================
PHASE 15: FINAL VERIFICATION AND SIGNOFF
================================================================================

Goal: run the strongest feasible final gate set and summarize the audit.

Tasks:

1. Run the strongest feasible final command set (below).
2. If a command is deferred, document why and provide the exact command.
3. Confirm the root Markdown inventory is intentional: the three operating files
   (README.md, SKILL.md, runbook.md), the six governance docs,
   FINAL_RELEASE_REPORT.md, and REPO_MAP.md (no other stray root-level Markdown;
   all prompts under docs/prompt/).
4. Confirm docs/ contains the canonical documentation set, organized into its
   six themed subfolders (getting-started/, reference/, algorithms/,
   development/, research/, prompt/) plus docs/index.md and docs/LICENSES.md.
5. Confirm generated HTML is current and its folder-prefixed page names match
   the docs/ subfolder layout.
6. Confirm the forbidden upstream-platform token appears only in
   docs/reference/seed_policy.md and its HTML twin.
7. Confirm no generated cache remains outside excluded evidence folders.
8. Summarize all edits and remaining risks.

Preferred final commands:

    python -m pytest -q
    python -m ruff check src tests scripts
    python -m mypy src/gsk_family/cli src/gsk_family/runners src/gsk_family/common
    python scripts/validate_profile_lock.py --root .
    python scripts/build_docs_html.py

Acceptance criteria:

- All preferred commands pass (or each deferral is justified); the root Markdown,
  docs subfolder, HTML, forbidden-token, and cache invariants all hold.

Final report format:

1. Critical findings
2. High findings
3. Medium findings
4. Low findings
5. Positive confirmations
6. Changes applied
7. Commands run
8. Commands deferred and why
9. Residual risks
10. Next highest-value action
```
