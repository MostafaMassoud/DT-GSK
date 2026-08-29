# PROJECT_RULES.md — The GSK-Family Python Constitution

**Purpose.** This is the top-level, non-negotiable rule set for the
DT-GSK repository — the PhD research software backing the GSK
(Gaining-Sharing Knowledge) optimizer family and its proposed method `dt-gsk`
(Dimension-Tiered Gaining-Sharing Knowledge). Every contributor, reviewer, and AI agent
**MUST** follow these rules before any other guidance. They exist to protect the
three things a research codebase cannot recover once broken: **evidence
integrity** (no fabricated numbers), **reproducibility** (deterministic seeds
and schedules), and the **byte-identity** of the vendored `dt-gsk` core.

**Audience.** Humans contributing code, docs, or experiments; AI agents running,
reviewing, documenting, or refactoring this repository; reviewers gating merges.

**Authority.** When this file conflicts with a habit, a memory, or a convenient
shortcut, this file wins. When it conflicts with the operating contract in
[SKILL.md](SKILL.md), treat the two as one body of law: SKILL.md is the detailed
agent operating contract, this file is the short constitution that points to it.
The specialized governance siblings (linked in §10) own their domains; this hub
defers to them rather than duplicating their detail.

---

## 1. Purpose and Scope

1.1 This project is a pure-Python implementation of the GSK optimizer family
plus self-contained Python ports of six CEC benchmark suites. It exists to run
**reproducible** optimizer campaigns, to reproduce published reference tables
bit-for-bit, and to produce the paper-grade statistical comparison that backs
the proposed method `dt-gsk`.

1.2 **Runnable optimizers (7):** `gsk`, `agsk`, `apgsk`, `fdb-agsk`,
`atmals-gsk`, `egsk`, `dt-gsk`. The canonical list is enforced in code by
`RUNNABLE_OPTIMIZERS` in `src/gsk_family/analysis/project_policy.py`.

1.3 **`egsk` is both runnable and a reference comparator.** `egsk` now ships a
real optimizer kernel (`src/gsk_family/optimizers/egsk.py`, a faithful MATLAB
port whose interior-point refinement uses `scipy`-SLSQP in place of `fmincon`,
validated as statistically equivalent), so `gsk-run --optimizer egsk` works and
`egsk` is in `RUNNABLE_OPTIMIZERS`. It **also** remains in
`REFERENCE_COMPARATORS`: the published statistical panel continues to source
`egsk`'s cells from the committed **Python (`scipy`-SLSQP) port** CSVs (the
comparator of record), not from a MATLAB `fmincon` reference. See §6.

1.4 **Suites (6):** `sphere`, `cec2011`, `cec2013`, `cec2013lsgo`, `cec2017`,
`cec2020`. Suite-specific conventions (CEC2017 excludes F2; CEC2011 uses native
per-problem heterogeneous bounds) are owned by
[BENCHMARK_RULES.md](BENCHMARK_RULES.md).

1.5 These rules apply to **everything in this repository**: source, tests,
scripts, configs, docs, generated results, and any agent automation. Scope
exclusions and per-domain depth live in the sibling docs of §10.

---

## 2. Workspace Rules

2.1 **MUST work in-place.** Work **directly inside** the repository root (the
DT-GSK repository, the folder containing `run.py` and `src/gsk_family/`). This
root is the shared working folder for humans and agents alike.

2.2 **NEVER nest, mirror, or fork the tree.** Do **not** create a nested copy, a
mirror tree, a generated agent-only workspace, a worktree clone of this repo
inside this repo, or a separate `.claude/` project folder for it. The
repository root is its own git root; nothing licenses creating sub-projects
here.

2.3 **`benchmarks/cec_reference_results/` is READ-ONLY.** This directory is
imported, immutable reference evidence. NEVER write generated experiment output
into it, NEVER overwrite it, and NEVER "regenerate" it. Generated results go
under `results/` only (see §3 and [BENCHMARK_RULES.md](BENCHMARK_RULES.md)). The
only exception is an explicit, user-requested provenance/data-maintenance task.

2.4 **NEVER destroy user work.** Do not revert user changes unless explicitly
asked. Do not delete retained evidence under `results/` without explicit
consent. Transient caches (`docs/html/`, `.pytest_cache/`, `.ruff_cache/`,
`.mypy_cache/`, `__pycache__/`, `*.pyc`, `*.nbc`, `*.nbi`) may be cleared only
when cleanup is in scope.

2.5 **Use absolute paths in agent automation.** Agent (subagent) Bash calls
reset the working directory between calls; always use absolute paths or `cd`
into the root first.

2.6 **Root-file discipline.** The project root holds a fixed inventory of thirteen
Markdown documents: the session entry point [CLAUDE.md](CLAUDE.md), the current-state
record [REVISION_STATUS.md](REVISION_STATUS.md), the three operating files —
[README.md](README.md), [SKILL.md](SKILL.md), [runbook.md](runbook.md) — the
newcomer orientation map [REPO_MAP.md](REPO_MAP.md), the six governance files
listed in §10, and the release report
[FINAL_RELEASE_REPORT.md](FINAL_RELEASE_REPORT.md). These are the only root
Markdown files. Do not add ad-hoc root guides or collapse existing ones without
an explicit request. Note the documentation smoke gate (§8) asserts a fixed
required-doc list, but among root Markdown files that list names only
[README.md](README.md) and [SKILL.md](SKILL.md); the other eleven — this file
included — are governed by this section alone. No root document has an HTML
twin, so the link gate never reaches them either. Adding, moving, or renaming a
root document therefore means updating both inventories in
[SKILL.md](SKILL.md) (§3.1 and §15) and the tree in [README.md](README.md) by
hand; no gate will catch it for you.

CLAUDE.md and REVISION_STATUS.md were added 2026-08-25 at the author's explicit
request, to give a resuming session a cheap entry point during the journal
revision. CLAUDE.md is a pointer file and must stay short; REVISION_STATUS.md is
the single place current state is recorded, so status must not be duplicated into
the other eleven. Resist growth: a new root guide is almost always a section in an
existing file.

---

## 3. Source-of-Truth and Evidence Integrity

3.1 **NEVER fabricate numerical or convergence results.** This is the cardinal
rule of the project. No invented best/median/mean/worst/SD values, no synthetic
convergence curves, no hand-edited reference tables, no "plausible" placeholders
in a results file or a paper figure. A gap is reported as a gap.

3.2 **Missing data is logged, never invented.** Tooling that encounters absent
data must surface it, not paper over it:

- The paper review pack (`papers/scripts/generate_review_pack.py`) logs absent
  convergence curves to `papers/DT-GSK-CEC2017-review_missing.log` and leaves
  the grid cell empty — it NEVER fabricates a curve.
- `gsk-stats` exits non-zero when no usable data is found, so absence of
  evidence is never silently reported as a pass.
- `gsk-validate` reports missing references clearly and exits **non-zero** when
  all functions were skipped (see §8.4 and [BENCHMARK_RULES.md](BENCHMARK_RULES.md)).

3.3 **Reference data is the source of truth and is immutable.**
`benchmarks/cec_reference_results/` is imported external evidence. It is the
ground truth that reproduced results are diffed against; it is never the place
reproduced results are written. See §2.3.

3.4 **Record the RNG + seed regime with every result.** A numerical result is
only evidence if it is reproducible. Every campaign writes its determinism
provenance alongside its numbers — `seed_schedule.csv` (the per-(dim, func, run)
seeds), `environment.json` (runtime/thread metadata), and an optional
`profile.json` — under `results/_run_all/<optimizer>/<suite>/`. Do not strip,
reorder, or "normalize" this provenance. The seed regime itself is governed by
§4.

3.5 **Byte-format parity is load-bearing.** The console output and `results/`
file formats are deliberately mirrored to a sibling reference project so the two
can be diffed (per-run best/error fields `%.10e`; convergence values `%.16e`
with a matching `log10` column; fixed `environment.json` key order). The exact
format is owned by `src/gsk_family/runners/output.py` and
[BENCHMARK_RULES.md](BENCHMARK_RULES.md). Do not "clean up" these formats.

3.6 **Truthful reporting (terminology).** Do not imply that reduced smoke checks
prove full-budget equivalence, that generated results are reference evidence, or
that validation passed when functions were skipped. Terminology rules
(including the upstream-platform name, which is permitted for factual
provenance -- the eGSK port lineage and the `docs/reference/seed_policy.md`
exception -- but never to describe this project's own runtime) are detailed in
[SKILL.md](SKILL.md) §13.

---

## 4. Reproducibility and Determinism Rules

4.1 **One unified seed schedule across the family.** The default and canonical
seed regime is the **unified** policy. The seed is the optimizer-independent
linear modular formula `get_cec_seed(base_seed, dim, func, run)` in
`src/gsk_family/runners/seed_policy.py`:

```python
seed = (base_seed
        + 1_000_003 * dim
        + 1_000_033 * func
        + 1_000_037 * run) % 2_147_483_646 + 1
```

with the project base seed `DEFAULT_BASE_SEED = 20_240_620`. It is **not**
hashed and **not** optimizer-specific. Do not change these constants, the
strides, the modulus, or the `+1` without re-verifying every reproducibility
gate (§8.5) — they are pinned by known-answer tests.

4.2 **Seed policies are a closed set.** `--seed-policy` accepts exactly
`SEED_POLICIES = ("reference", "unified", "native", "derived")`. `unified` is
the default; `reference` reproduces published tables bit-for-bit for the
rand-only optimizers; `native`/`derived` are diagnostic. Full derivation lives
in `docs/reference/seed_policy.md`; the operational summary is in
[SKILL.md](SKILL.md) §10.

4.3 **`dt-gsk` is forced onto the unified regime under ALL policies.**
`UNIFIED_ONLY_OPTIMIZERS = {"dt-gsk"}` (`seed_policy.py`) pins `dt-gsk` to the
shared threefry generator and the `get_cec_seed` schedule regardless of the
selected `--seed-policy`. Do not exempt it, special-case it out, or add another
id to this set without explicit instruction.

4.4 **Deterministic generators only.** `RandomContext`
(`src/gsk_family/common/rng.py`) supports exactly three reference-matching
labels — `threefry` (Threefry-4x64-20, the default), `twister` (MT19937), and
`seed` (mcg16807/Park-Miller). Any label outside `{threefry, twister, seed}`
must raise. Do NOT add NumPy bit generators (Philox, PCG64, plain MT19937) as
labels, and do NOT re-add the absent v5 `state` generator. Draw order, matrix
fill (column-major), integer and permutation conventions are fixed; changing any
of them requires re-verifying against reference draws (`tests/unit/test_rng.py`).

4.5 **Fair-start exception is documented and intentional.** `dt-gsk`
self-initializes a `5*D` (`np_init_mult*D`) population and therefore ignores any
injected fair-start `X0`/`initial_population`, while still using the unified
seed. This is a deliberate, documented exception — see
`src/gsk_family/optimizers/dt_gsk.py` and `docs/algorithms/dt-gsk.md`. Do not
"fix" it to consume the runner's injected population. `NP = 5D` is also a
**declared component of the method**, not merely a default: the round-one
journal review challenged the asymmetry against the comparators' `NP = 100`
(R1.3/R2.2), and the matched-population experiment answered it — `dt-gsk` at
`NP = 100` is first at `D = 10` and second at `D = 30`, `50` and `100`, with
the paired difference null at `D = 10` and `D = 30` and significant at
`D = 50` and `D = 100`. The published `D = 50` and `D = 100` rank claims are
therefore qualified as resting in part on the population rule. Changing
`np_init_mult` changes what the paper claims; the experiment, its evidence
release and the decision that closed it are owned by
[REVISION_STATUS.md](REVISION_STATUS.md) and
`papers/governance/decision_log.md` (D-0048).

4.6 **Thread pinning preserves determinism at scale.** `dt-gsk` at `D>=50`
(SGSM / `prange`) and `D>=100` (TERRA controllers) requires single-thread
Numba/BLAS (`NUMBA`/`OMP`/`MKL`/`OPENBLAS_NUM_THREADS=1`) for byte-stable
determinism. The full performance/threading contract — worker defaults, the
self-healing process backend, the no-thread-fallback rule — is owned by
[PERFORMANCE_RULES.md](PERFORMANCE_RULES.md). Do not weaken thread pinning to
chase speed.

4.7 **Determinism is sacred during any refactor.** When changing anything that
could touch behavior, preserve seed schedules, RNG draw order, evaluation
counts, deterministic result ordering, and output schema. Prefer profiling
evidence over intuition; defer the why to [PERFORMANCE_RULES.md](PERFORMANCE_RULES.md).

---

## 5. The `dt-gsk` Byte-Identity Rule

5.1 `dt-gsk` is **this project's proposed method**, byte-identically migrated
from the source DT-GSK v2.1 tree. Its core is **VENDORED and
BYTE-IDENTITY-LOCKED**.

5.2 **The locked surface (do NOT edit — the lock is on the bytes, not on behavior):**

| Locked module / package | Path |
| --- | --- |
| DT-GSK core (5186 lines) | `src/gsk_family/optimizers/_dt_core.py` |
| DT-GSK subsystems package | `src/gsk_family/optimizers/_dt_subsystems/` |
| — bound constraint | `_dt_subsystems/bound_constraint.py` |
| — budget / budget policy | `_dt_subsystems/budget.py`, `budget_policy.py` |
| — basin memory | `_dt_subsystems/basin_memory.py` |
| — gained/shared junior + senior | `_dt_subsystems/gained_shared_junior.py`, `gained_shared_senior.py` |
| — interaction graph | `_dt_subsystems/interaction_graph.py` |
| — numba acceleration | `_dt_subsystems/_numba_accel.py` |
| — provenance | `_dt_subsystems/_dt_provenance.py` |

The closely-coupled `_dt_profiles.py` (`build_pub_config`), `_dt_rng.py`
(13-substream RNG layer), and the family-facing `dt_gsk.py` adapter are part of
the `dt-gsk` machinery; treat the core/subsystems as reference-locked and touch
the profiles/RNG/adapter only with the same byte-identity caution.

5.3 **Rules for the locked core:**

- **NEVER** edit `_dt_core.py` or anything under `_dt_subsystems/`. For
  `_dt_core.py` the lock is on the BYTES, not on behavior: it is one of the four
  `SHIPPED` modules that `papers/scripts/validate_provenance_claims.py` SHA-256s,
  and that gate requires the manuscript to print each module's *live* hash — so a
  comment or whitespace edit that changes nothing at runtime still fails the gate
  and falsifies a value the manuscript prints. `_dt_subsystems/` is not covered by
  that hash gate, but a byte change there is still an explicitly-requested,
  change-registered action (next bullet). No "casual" refactors, no renames, no
  reformatting, no "improvements".
- Any permitted change (e.g. a re-verified migration step under
  `docs/development/dt_gsk_core_reference.md`) MUST keep every byte-identity gate
  green (§8.5) and MUST be explicitly requested.
- The docstring gate **intentionally exempts** the vendored modules
  (`_dt_core.py`, `_dt_subsystems/*`, and the vendored stats modules
  `analysis/statistics.py`, `analysis/statistical_tests.py`) — see
  `tests/unit/test_docstrings.py`. Do not add docstrings to vendored code to
  "satisfy" the gate; that would perturb the vendored bytes.

5.4 **Verification is mandatory.** The byte identity of `dt-gsk` is protected by
the KATs in §8.5. If you cannot keep them green, the change does not ship.

---

## 6. `egsk`: Runnable Port + Reference-Comparator Data

6.1 `egsk` is now a first-class runnable optimizer
(`src/gsk_family/optimizers/egsk.py`) **and** a reference comparator. The kernel
is a faithful port of the MATLAB `egsk_optimize` reference; the only deviation is
the interior-point refinement, which uses `scipy.optimize.minimize(method="SLSQP")`
in place of MATLAB `fmincon` (no byte-identical Python equivalent exists). It is
validated as **statistically equivalent** to the reference (`tests/unit/test_egsk.py`).

6.2 The committed comparator data under `benchmarks/cec_reference_results/.../egsk/`
is the **comparator of record** the statistical panel reports, and it is the
**Python (`scipy`-SLSQP) port run**, not a MATLAB `fmincon` reference (the
committed `egsk` CSVs were produced by the runnable port; e.g. CEC2017 F5 D10
mean 4.816, the SLSQP value, not the `fmincon` 4.994). The seven-algorithm panel
= the seven panel optimizers (Section 1.2), all evaluated by `gsk-stats`. The panel
reads these committed CSVs rather than a fresh live run so the numbers are fixed
and reproducible.

---

## 7. Version-Control Policy

7.1 **Commit ONLY when explicitly asked.** Do not commit as a courtesy, do not
auto-commit after a task, do not "save progress" without being told.

7.2 **NEVER push without asking.** Pushing is an outward, hard-to-reverse action;
it requires explicit consent every time.

7.3 **Branch off `main`.** The default branch is `main`. If asked to commit while
on `main` (or a detached HEAD), branch first; do not commit research changes
directly onto the default branch unless explicitly told to.

7.4 **Honor hooks and signing.** Never skip hooks (`--no-verify`) or bypass
signing unless explicitly requested. If a hook fails, fix the underlying issue.

7.5 **Keep the working tree truthful.** Do not stage or commit generated
caches, do not commit `benchmarks/cec_reference_results/` changes (it is
read-only, §2.3), and when docs change, commit the regenerated `docs/html/`
twins alongside the source change (§8.4).

---

## 8. The Green-Gates Rule

A change is **not done** until the gates it touches are green. Run targeted
checks for narrow edits; run the full sequence for broad changes. If a gate is
too expensive to run, state exactly which command was deferred and why — never
imply a deferred gate passed.

### 8.1 Lint — Ruff (matches CI; scoped to source/tests/scripts)

```powershell
python -m ruff check src tests scripts
```

MUST be clean.

### 8.2 Tests — pytest tiers

```powershell
python -m pytest -q
```

Tiers: `tests/unit/`, `tests/smoke/`, `tests/regression/` (plus
`tests/performance/` and the top-level `tests/test_imports.py`). Do not
hard-code the collected test count into new docs; re-check with
`python -m pytest --collect-only -q`.

### 8.3 Docstring gate

`tests/unit/test_docstrings.py` requires a docstring on every module, class,
function, and method **EXCEPT** the vendored modules exempted in §5.3
(`_dt_core.py`, `_dt_subsystems/*`, `analysis/statistics.py`,
`analysis/statistical_tests.py`).

### 8.4 Documentation / link gate + HTML twins

`tests/smoke/test_documentation_commands.py` resolves a fixed required-doc list,
rebuilds the HTML, and asserts every generated HTML relative link resolves.
After any change to docs, docstrings, README commands, navigation, or the review
prompts, rebuild and commit the twins:

```powershell
python -m pytest tests\smoke\test_documentation_commands.py -q
python scripts\build_docs_html.py
```

### 8.5 `dt-gsk` byte-identity KATs (the lock's enforcement)

| Gate | Test |
| --- | --- |
| Config known-answer test (`build_pub_config`) | `tests/unit/test_dt_profiles.py` |
| RNG known-answer test (13-substream layer) | `tests/unit/test_dt_rng.py` |
| Byte-stable regression | `tests/regression/test_dt_gsk_byte_stable.py` |

These MUST stay green for any change that could touch `dt-gsk` (§5).

### 8.6 Profile lock + preferred broad sequence

```powershell
python -m pytest -q
python -m ruff check src tests scripts
python scripts\validate_profile_lock.py --root .
python scripts\build_docs_html.py
```

Validation/comparison truthfulness (`gsk-validate`, all-skipped exits non-zero)
is part of the integrity contract in §3.2 and detailed in
[BENCHMARK_RULES.md](BENCHMARK_RULES.md).

---

## 9. Change-Safety and Reporting

9.1 **Confirm hard-to-reverse and outward actions.** Pushing, deleting retained
evidence, force operations, touching `benchmarks/cec_reference_results/`,
editing the vendored `dt-gsk` core, or changing seed/RNG constants are all
high-consequence. Confirm before doing them; prefer the narrowest safe change.

9.2 **Report failures faithfully.** If a gate fails, a run crashes, or data is
missing, say so plainly with exact paths and commands. Never present a partial,
skipped, or fabricated result as a success. "It didn't run" is an acceptable
answer; a fabricated number is not.

9.3 **Stay in lane during edits.** Reuse existing helper APIs, avoid unrelated
refactors, keep abstractions conservative, and update the matching
`docs/algorithms/<id>.md` when optimizer behavior/options/artifacts change.

9.4 **Lead reviews with severity-ordered findings**, exact file paths and line
numbers, bugs separated from risks/missing-tests/stale-docs, and a short
summary. State clearly when nothing is wrong.

---

## 10. Where the Other Governance Docs Live

This file is the rules **hub**. Each sibling owns its domain in depth; defer to
it rather than duplicating its content. All six governance files sit at the
project root.

| Doc | Owns |
| --- | --- |
| [PROJECT_RULES.md](PROJECT_RULES.md) | **This file** — the constitution: workspace, evidence integrity, determinism, the `dt-gsk` lock, version control, gates, change-safety. |
| [DESIGN_GUIDE.md](DESIGN_GUIDE.md) | Design principles and the `optimize(problem, options) -> OptimizerResult` contract; how adapters, the seed policy, and subsystems fit together. |
| [ARCHITECTURE.md](ARCHITECTURE.md) | The package map (`cli/`, `runners/`, `optimizers/`, `common/`, `benchmark_adapter/`, `analysis/`) and module dependencies. |
| [BENCHMARK_RULES.md](BENCHMARK_RULES.md) | Suite definitions, CEC2017-excludes-F2, CEC2011 native dims/heterogeneous bounds, budgets/run counts, result schema, reference-evidence immutability, validation. |
| [CODING_STANDARD.md](CODING_STANDARD.md) | Style, docstrings (and the vendored exemptions), Ruff rules, typing, naming, and the editing protocol. |
| [PERFORMANCE_RULES.md](PERFORMANCE_RULES.md) | Numba JIT, worker defaults, the self-healing process backend, the no-thread-fallback rule, and thread pinning for `dt-gsk` at `D>=50`/`D>=100`. |

**Operating docs (also at root):** [README.md](README.md) (landing),
[SKILL.md](SKILL.md) (the full agent operating contract — the detailed companion
to this constitution), [runbook.md](runbook.md) (copy-paste commands).
In-depth reference material lives under `docs/` (getting-started, reference,
algorithms, development, research, prompt) and the generated `docs/html/`.

---

*If a rule here ever conflicts with expediency, the rule wins. Evidence
integrity, reproducibility, and the `dt-gsk` byte-identity lock are
non-negotiable.*
