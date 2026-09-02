# Final Publication Prompt — Production-Ready Q1 Release of GSK Family Python v1.1

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
> the `CLAUDE.md` "Right now" block. As of this refresh: **pass-68 / tag v2.41**
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


> **When to use this prompt:** for the final pre-publication hardening pass — after all
> algorithm work, tuning, and campaign runs are complete. It drives repository-wide
> cleanup, documentation modernization, and release preparation. It does **not**
> authorize algorithm changes, new experiments, or another development iteration.

> **Current project status (2026-07-20) — read before executing.** This prompt is
> reusable and process-generic; the dated snapshot below fixes the phase you are
> polishing *into*, so an executor does not re-open settled work. The manuscript is
> **built** and in **final pre-submission remediation** (not from-scratch
> construction): the 80-ticket remediation ledger
> (`papers/governance/remediation_2026_07_18/ticket_status.csv`) stands at **80/80
> terminal** (70 `closed_verified` + 10 `superseded_with_evidence`; no ticket is
> open), and every quality gate is **green** as of 2026-07-20 (build hygiene,
> cross-format PDF/DOCX/JSON parity, provenance-claims, citation-usage map, and
> environment attestation). **Do not** re-open algorithm work, re-tune, or regenerate
> the frozen runtime table. **RT-001 is CLOSED — do not re-run it or request a re-timing:**
> the six-comparator re-timing was executed, failed its determinism gate (3,772 differing
> rows), and was not adopted; `tab:runtime` was instead narrowed to DT-GSK-only,
> single-session, and no cross-algorithm wall-clock claim is made. One item remains live:
> the terminal pair **C-008** (mint a fresh
> `papers/governance/main_manuscript_freeze_manifest.json`, CRLF + 2-space, edited in
> place) → **C-001** (one authoritative commit + manuscript version id) is pending and
> must run last, after any author edits land. Current evidence ids: primary
> release **`rel-2026-07-20-67d9345f9`**, ablation release **`abl-rel-2026-07-20`**
> (derived bundle `papers/analysis/rel-2026-07-20-67d9345f9/`). Suggested reviewer
> names and JCR/quartile figures are **author-supplied** — never auto-generate them.

You are acting as a multidisciplinary team of world-class experts in evolutionary
computation, numerical optimization, CEC benchmarking, scientific software engineering,
Python architecture, research reproducibility, documentation engineering, technical
writing, release engineering, performance engineering, quality assurance, open-source
maintenance, and Q1 journal publication standards.

Your objective is **not** to add features, tune algorithms, or open another development
iteration. Your objective is to transform this repository —
the DT-GSK repository, the Python implementation of the GSK optimizer family
(seven panel optimizers: `gsk`, `agsk`, `apgsk`, `fdb-agsk`, `atmals-gsk`, `egsk`,
and the proposed `dt-gsk`) spanning five CEC benchmark suites in code (`cec2011`,
`cec2013`, `cec2013lsgo`, `cec2017`, `cec2020`) — three of which (`cec2011`,
`cec2013`, `cec2017`) carry committed reference evidence under
`benchmarks/cec_reference_results/` — plus a pure-Python `sphere` smoke test, the
`gsk-stats` statistical panel, and the `papers/` manuscript pipeline — into the
**final production-quality release**,
ready for:

- Q1 journal publication (supplementary software for the DT-GSK paper)
- Public GitHub release
- Zenodo archival (`CITATION.cff` already present)
- Long-term maintenance
- Fully reproducible research by external users with zero internal knowledge

Assume this is the final release before publication.

---

## Non-Negotiable Invariants (apply to every phase)

These are the project's standing rules from `PROJECT_RULES.md` and its sibling
governance docs. No phase may violate them:

1. **Byte-identity lock.** `src/gsk_family/optimizers/_dt_core.py`,
   `_dt_subsystems/`, `_dt_profiles.py`, and `_dt_rng.py` are vendored and locked.
   Never edit them for behavior; never "improve" their style or docstrings (they are
   exempt from the docstring gate). The same exemption covers the vendored
   `analysis/statistics.py` and `analysis/statistical_tests.py`.
2. **No behavior changes.** Optimizer logic, seed schedules (`get_cec_seed`, the
   unified policy, `UNIFIED_ONLY_OPTIMIZERS`), RNG draw order, evaluation counts,
   bounds repair, the CEC2017 F2 exclusion, result byte formats
   (`runners/output.py`), and file naming must be preserved exactly. All cleanup is
   behavior-preserving.
3. **Evidence integrity.** The evidence flows through three tiers:
   `benchmarks/cec_reference_results/` (promoted, read-only imported reference
   evidence — never edit, regenerate, or delete it) → `papers/analysis/<rel-id>/`
   (the derived analysis bundle for a release) → `results/` (transient staging).
   Paper statistics are generated in strict-source mode (`gsk-stats --strict-source`
   / `GSK_STRICT_SOURCE`), which pins the promoted evidence as the citation source.
   Canonical reproduced results under `results/_run_all/` (including `_analysis/`)
   are kept for reproduction. Never fabricate numbers; missing data is logged, not
   invented.
4. **Generated HTML is generated.** Never hand-edit `docs/html/`; change the
   Markdown/docstrings and rebuild with `python scripts/build_docs_html.py`,
   committing source and HTML twins together.
5. **Green gates after every phase:**

   ```powershell
   python -m pytest -q
   python -m ruff check .
   python scripts/validate_profile_lock.py --root .
   python scripts/build_docs_html.py
   ```

   The DT-GSK KATs (`tests/unit/test_dt_profiles.py`, `tests/unit/test_dt_rng.py`,
   `tests/regression/test_dt_gsk_byte_stable.py`) must stay green untouched — never
   weaken them.
6. **Version control.** Work on the current tree; commit only when the user asks;
   never push without asking.
7. **Forbidden-token rule.** The upstream numeric-platform product name may appear
   only in `docs/reference/seed_policy.md` and its HTML twin.

---

## Phase 1 — Repository Audit

Audit every folder, source file, script, config, doc page, HTML page, test, benchmark
asset, and root report. Build a single findings ledger (path, verdict
KEEP/ARCHIVE/DELETE/REWRITE, reason). The earlier one-time `cleanup_candidates.csv`
inventory has already been fully actioned and removed — do **not** expect it as a live
file; treat this phase as a fresh re-audit that must reach the same clean end state.
Known audit targets to confirm or close:

- Stale experiment output (`results/_experimental`, `results/_staging_*`,
  `results/_tmp_baseline_analysis`) and any rejected/superseded configs under
  `configs/experimental/` (keep the diagnostic configs actually referenced by
  tests/tooling, e.g. `dt_diag.yml`).
- Dead analysis modules: any empty stub or uncalled thin wrapper under
  `src/gsk_family/analysis/`.
- Duplicated optimizer helpers: `_option_value` (multiple copies), `_scan_best`,
  `_append_convergence`, the `_MISSING` sentinel — consolidate only if provably
  draw-order-neutral and the byte-stable regression stays green; otherwise document
  the duplication as accepted.
- Unused `parent_pop` copy in `atmals_gsk.py`; APGSK's RNG-fidelity-only K draw
  (keep, but ensure the inline comment explains it).
- Historical root/development reports: keep the ones that are part of the official
  record (e.g. `FINAL_RELEASE_REPORT.md`); archive or delete superseded one-off
  investigation notes.
- Possible overlap between `papers/scripts/generate_rank_charts.py` /
  `generate_nemenyi_cd.py` and the figures `gsk-stats` already renders — keep one
  canonical path per figure.
- `.pytest_cache/`, `.ruff_cache/`, and `__pycache__/` — keep off the release
  surface (caches are already gitignored).

---

## Phase 2 — Update Every Prompt

Review every prompt in `docs/prompt/` — `project-review.md`,
`documentation-deep-upgrade.md`, `documentation-review.md`,
and this file — plus the agent contract in
`SKILL.md`. (The `docs/prompt/` suite is now exactly these five files; the
one-time DT-GSK migration/publish/doc-polish prompts were completed and
removed.)

Update each to describe only the current production implementation: seven runnable
optimizers (`egsk` runnable *and* reference comparator); the completed DT-GSK
migration (drop any "phase N pending" language — the migration and the statistical
suite are done); DT-GSK shipping a **single `pub` profile** (the earlier
`strong_candidate_a/b/c` tuning experiment was completed, rejected by full validation,
and fully removed — no prompt may reference strong-candidate configs, scripts, tests,
or docs as if they exist); the fail-closed FP-regime sentinel
(`runners/fp_regime.py` + `docs/reference/fp_regime.md` +
`tests/regression/test_fp_regime.py`); the current test count (618 tests — always re-collect before citing) and gate
list; and the current directory layout. Remove references
to finished phases, removed modules, the old PCG64/base-123456 seed era, superseded
workflows, and any removed prompt/report (there is no `EGSK_IMPLEMENTATION_PROMPT.md`
or `EGSK_IMPLEMENTATION_REPORT.md`; the `docs/prompt/` suite is now exactly the four
files listed above). Prompts that documented one-time completed work (for example
the migration prompt) should either be rewritten as maintenance prompts or archived
as historical records — not left implying open work. Keep every prompt technically
accurate, concise, deterministic, and consistent with the governance docs. Remember:
adding, renaming, or removing any doc file requires updating the required-doc list in
`tests/smoke/test_documentation_commands.py` and rebuilding HTML.

---

## Phase 3 — Simplify All Runbooks

Review the execution documentation: `README.md`, the root `runbook.md`,
`docs/getting-started/` (runbook, tutorial, user_guide, configuration,
troubleshooting, explainer), and the benchmark/developer guides. The root
`runbook.md` and `docs/getting-started/runbook.md` must stay synchronized.

Rewrite run instructions to be minimal, beginner-friendly, copy-paste ready, and
deterministic, with PowerShell (primary) and Linux shell variants where syntax
differs. The single canonical path is: install (`pip install -e ".[dev]"`) → smoke
run (`python run.py --root . --optimizer gsk --suite sphere ...`) → full campaign
(`python run.py ... --parallel --workers 2 --convergence-graphs --overwrite`, or the
`configs/*.yml` launchers; the panel suites are CEC2017, CEC2011, and CEC2013) →
ablation (`python scripts/run_ablation.py ...` →
`python papers/scripts/generate_ablation_matrix.py`) → validation (`gsk-validate`)
→ statistics (`gsk-stats --suite CEC2017 --dims 10,30,50,100`, plus
`--suite CEC2013 --dims 10,30,50`) → review pack
(`python papers/scripts/generate_review_pack.py`). Keep it consistent with the
root `runbook.md` "Full Paper Pipeline (in order)" section (eight stages) — the
runbook is current; do not contradict it. Remove duplicated, historical, and
experimental command paths; keep the documented safe defaults
(`--parallel --workers 2`, process backend, never the thread backend) and the
slow/crashing-machine recovery commands.

---

## Phase 4 — Execute Every Updated Prompt

After updating the prompts, execute each applicable maintenance prompt against the
repository: the full-project review (`project-review.md`), the deep docs upgrade
(`documentation-deep-upgrade.md`), and the two-part docs gate
(`documentation-review.md`, Part I consistency + Part II inline documentation).
The repository must reflect the output of
its own updated prompts. Log any prompt intentionally not executed and why.

---

## Phase 5 — Update Inline Documentation

Review every **non-vendored** source file under `src/gsk_family/`, `scripts/`,
`benchmarks/cec_suite_python/`, and `papers/scripts/`. Rewrite module, class,
function, and method docstrings to be accurate, concise, scientifically rigorous, and
synchronized with the implementation — parameters, returns, exceptions, algorithm and
mathematical notes included. The docstring gate (`tests/unit/test_docstrings.py`)
already requires full coverage; this phase raises quality, not just presence. Remove
obsolete comments, fix misleading ones, and make sure the load-bearing quirks stay
documented in place: the DT-GSK fair-start exception, the C++-fidelity emulations in
the CEC kernels, the composition-kernel `fastmath` exception, the reference
seed-formula rationale in `seed_policy.py`, and the F2 exclusion. Do not touch
vendored modules.

---

## Phase 6 — Regenerate and Verify HTML Documentation

Never hand-edit `docs/html/`. Instead: fix the Markdown sources and docstrings,
improve `scripts/build_docs_html.py` templates/styling/navigation only if needed,
rebuild, and commit the twins. Then verify via the existing gates that every page
renders, every relative link resolves (`test_generated_html_local_links_resolve`),
the API pages match current docstrings, version/date references are current, and no
stale pages remain for deleted docs (removals require pruning both the source and the
required-doc list).

---

## Phase 7 — Repository Cleanup

Execute the Phase 1 ledger. Delete or archive: stale staging/experimental results,
rejected experimental configs, dead modules, orphaned assets, duplicate reports,
temporary outputs, and debug utilities. Keep only what development, testing,
reproduction, publication, and user documentation require. Hard protections:
`benchmarks/cec_reference_results/` (read-only evidence), `results/_run_all/`
canonical results and `_analysis/`, all tests, all governance docs, `papers/`
sources, and the committed reference-parity fixtures under `tests/`. Every deletion
must leave the green gates passing; update `MANIFEST.in`, `.gitignore`, and the
required-doc list wherever cleanup changes the file set. (The one-time
`cleanup_candidates.csv` ledger from the original cleanup pass has already been
actioned and removed — do not re-create it as a shipped artifact; if you keep a
fresh ledger, keep it out of the release surface.)

---

## Phase 8 — Documentation Consistency Review

Verify identical terminology, naming, and facts across README, the six governance
docs, all `docs/` themes, HTML, prompts, runbooks, inline docs, and `papers/`.
Specific consistency anchors for this project: optimizer IDs and their hyphenation
(`dt-gsk`, `fdb-agsk`, `atmals-gsk`), suite IDs and protocols (F2 excluded from
CEC2017 scoring; CEC2011 and CEC2013LSGO are raw-objective, native-dimension suites),
the seed formula and the three RNG labels (`threefry`, `twister`, `seed` — no
others), the seven-runnable / six-comparator panel wording (the `egsk` dual role
stated identically everywhere), the reference-first data policy (all paper
statistics — the proposed `dt-gsk` included — read from the committed panel
under `benchmarks/cec_reference_results/<suite>/<optimizer>/`, with
`results/_run_all/` as fallback only), test and doc counts, version numbers
(`pyproject.toml` ↔ `CITATION.cff` ↔ docs), and the two-runbook sync.

---

## Phase 9 — Publication Quality Audit

Review the project against Q1 journal and archival expectations: reproducibility
(unified seeds, bit-exact RNG streams, environment metadata, deterministic parallel
execution), organization, architecture (the downward-only layering), documentation
quality, coding standards (ruff clean, scoped mypy clean), maintainability, portability
(the declared Python 3.10–3.13 support range, which no CI verifies), scientific transparency (evidence provenance,
no-fabrication rules, missing-data logs), and release readiness. Close every fixable
weakness within the invariants; for the known accepted trade-offs (scoped mypy, the
`slow`-marked performance tier, D≤30-only byte-identity golden cells, the silent
Numba fallback if left unchanged), either fix behavior-neutrally or document them
explicitly as limitations — nothing may remain both known and undocumented.

---

## Phase 10 — Final Release Preparation

Prepare the official release: confirm `pyproject.toml` metadata, version,
classifiers, and console scripts; validate `CITATION.cff`; verify a clean source
distribution builds from `MANIFEST.in`; confirm the CI workflow passes on all
supported Python versions; refresh `FINAL_RELEASE_REPORT.md` (or a successor release
notes file) to describe the shipped state; and run the complete gate sequence one
final time from a clean checkout. The end state: zero stale files, zero obsolete
documentation, zero dead code, zero duplicated assets, zero unfinished TODOs, zero
placeholder docs — suitable for GitHub release, Zenodo archive, Q1 supplementary
material, and long-term maintenance.

---

## Expected Final Deliverables

A single publication-ready repository containing only the final production version:

- All `docs/prompt/` prompts and `SKILL.md` updated to the current implementation,
  with completed-work prompts rewritten or archived.
- Simplified, verified, synchronized runbooks with one canonical execution path
  (install → smoke → campaign → validate → stats → paper pack).
- Publication-quality inline documentation across all non-vendored code; vendored
  modules untouched.
- Regenerated, link-clean HTML documentation matching the sources.
- The Phase 1 cleanup ledger fully executed; reference evidence and canonical
  results preserved intact.
- Consistent naming, terminology, versions, and counts across every artifact.
- All gates green from a clean checkout: pytest (all tiers), ruff, profile lock,
  docs build + link resolution, and the untouched DT-GSK byte-identity KATs.
- A refreshed release report documenting the shipped state.

No experimental, deprecated, temporary, duplicated, historical, or obsolete artifacts
remain — and every published number stays byte-identical to the evidence that
produced it.
