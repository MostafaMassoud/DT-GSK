# CODING_STANDARD.md

**Purpose.** This is the code-level standard for the GSK-family Python project
(`gsk_family`, src layout, CPython 3.10). It codifies the conventions that the
project's automated **gates** enforce — linting, type hints, docstrings, the
vendored byte-identity lock, console-output discipline, determinism, tests,
docs-as-code, and commit hygiene — so that any change you make stays green and
keeps the research software reproducible. **Audience:** anyone who edits Python
under `src/`, `tests/`, or `scripts/`, or adds documentation. It is the
authoritative answer to "how do I write code here so the gates pass."

This file stays in its lane: it governs *how the code is written*. For the
project-wide operating rules (workspace contract, what is immutable, the seed
and result-schema policies) see [PROJECT_RULES.md](PROJECT_RULES.md); for module
boundaries and the `optimize()` contract see [ARCHITECTURE.md](ARCHITECTURE.md)
and [DESIGN_GUIDE.md](DESIGN_GUIDE.md); for benchmark/suite conventions see
[BENCHMARK_RULES.md](BENCHMARK_RULES.md); for Numba/thread/determinism-under-load
rules see [PERFORMANCE_RULES.md](PERFORMANCE_RULES.md). The agent operating
contract is [SKILL.md](SKILL.md); the landing page is [README.md](README.md);
copy-paste commands live in [runbook.md](runbook.md).

---

## 1. Language and Tooling

- **Interpreter / target.** Code runs on **CPython 3.10**. `pyproject.toml`
  declares `requires-python = ">=3.10,<3.14"`; Ruff and mypy both target
  `py310` / `python_version = "3.10"`. You MUST NOT use syntax newer than 3.10
  (no `match`-only constructs that assume 3.11+, no PEP 695 `type` aliases, no
  exception groups).
- **Layout.** This is a **src layout**: the importable package is
  `src/gsk_family/`, and tests run with `pythonpath = ["src", "."]`
  (`[tool.pytest.ini_options]`). The canonical source-checkout runner is
  `python run.py`, which prepends `src/` to `sys.path`. You MUST keep all package
  code under `src/gsk_family/` and never import it via a relative path that
  assumes a flat (non-src) layout.
- **Ruff is the lint/format authority.** The gate is Ruff over exactly
  `src tests scripts`. It MUST be clean:

  ```powershell
  python -m ruff check src tests scripts
  ```

  Ruff config (`pyproject.toml`): `target-version = "py310"`,
  `line-length = 120`, lint `select = ["E9", "F"]` (syntax errors + Pyflakes:
  undefined names, unused imports, unused variables, f-string and redefinition
  issues). Keep lines within **120 columns**. Do NOT silence a finding with a
  blanket ignore; use a targeted `# noqa: <code>` only for an intentional
  compatibility shim or a justified unused calculation, and keep the noqa
  specific.
- **mypy is an optional, scoped gate.** The type check is deliberately narrowed
  (`follow_imports = "skip"`, `ignore_missing_imports = true`) to keep it green
  under NumPy 2.x shape-typing churn. Run it on the first-party packages only:

  ```powershell
  python -m mypy src/gsk_family/cli src/gsk_family/runners src/gsk_family/common
  ```

  Do not "fix" mypy noise by widening its scope to vendored or benchmark
  kernels.
- **Dependencies.** Runtime deps are pinned in `pyproject.toml`
  (`numpy`, `scipy`, `pandas`, `matplotlib`, `PyYAML`, `numba`); dev tooling is
  the `dev` extra (`build`, `mypy`, `pytest`, `ruff`, `types-PyYAML`). You MUST
  NOT add a new third-party runtime dependency without an explicit request — the
  reproducibility and packaging story depends on the pinned set.

---

## 2. Imports and Module Layout

- **`from __future__ import annotations` first.** Every new `.py` module SHOULD
  begin with the module docstring, then `from __future__ import annotations`,
  before any other import. This defers annotation evaluation (PEP 563) so you can
  reference types without runtime import cost or circular-import pain. This is
  the established pattern across `src/gsk_family/` and every test module.
- **Import grouping.** Order imports stdlib -> third-party -> first-party
  (`gsk_family.*`), separated by blank lines, as in
  `src/gsk_family/optimizers/gsk.py`. Prefer **absolute** first-party imports
  (`from gsk_family.common.rng import RandomContext`), not deep relative chains.
- **No unused imports / names.** Pyflakes (`F`) fails the lint gate on any unused
  import or unused local. If a symbol exists only for re-export, expose it via
  `__all__` rather than leaving it apparently unused.
- **Respect the module boundaries.** Optimizers call the benchmark *through* the
  adapter (`benchmark_adapter`), RNG *through* `common.rng.RandomContext`, and
  write results *through* `runners.output`. Do not reach across these layers ad
  hoc; the layering rationale belongs to [ARCHITECTURE.md](ARCHITECTURE.md).
- **One `main()` per CLI module.** Each `cli/*.py` (`run`, `list`, `validate`,
  `stats`) exposes a single `main()` that backs a console script declared in
  `[project.scripts]`. Keep that contract: console scripts MUST resolve to
  `gsk_family.cli.<name>:main`.

---

## 3. Type Hints

- **Annotate public APIs.** Every public function, method, and dataclass field
  MUST carry type annotations. The `optimize()` contract is annotated end to end
  (`optimize(problem: BenchmarkProblem, options: OptimizerOptions | dict) ->
  OptimizerResult`); follow that standard for any new public surface.
- **Use 3.10 + future-annotations syntax.** With
  `from __future__ import annotations` you write modern union syntax as strings:
  `int | None`, `list[str]`, `dict[str, Any]`, `np.ndarray | None`,
  `tuple[float, np.ndarray]` (see `src/gsk_family/types.py` and
  `optimizers/gsk.py`). Prefer these over `typing.Optional` / `typing.List`.
- **`Any` is a deliberate escape hatch**, not a default — used where the option
  bag is genuinely heterogeneous (e.g. `_option_value(options: Any, ...)` in
  `gsk.py`, or `values: dict[str, Any]` in `OptimizerOptions`). Narrow the type
  when you can.
- **Return types are required** on public functions, including `-> None`. Helper
  signatures in the codebase already do this (e.g.
  `def _log_console(enabled: bool, message: str) -> None:`).
- Numeric arrays are `np.ndarray`; do not invent custom shape-typed aliases that
  the scoped mypy gate cannot follow.

---

## 4. Docstrings — the Gate

The docstring gate is **non-negotiable** and the single most common reason a new
function fails CI. It lives in `tests/unit/test_docstrings.py`
(`test_all_source_modules_classes_functions_and_methods_have_docstrings`).

### 4.1 What is required

The test parses every `src/gsk_family/**/*.py` with `ast` and asserts a docstring
on:

- **every module** (`ast.get_docstring(tree)`),
- **every `ClassDef`**,
- **every `FunctionDef` and `AsyncFunctionDef`** — and because it uses
  `ast.walk`, that includes **methods and nested/inner functions**.

So a closure or a private `_helper` defined inside another function still needs a
docstring. There is no "it's just a one-liner" exemption.

A compliant module + class + function looks like this:

```python
"""Best-so-far convergence tracking utilities."""

from __future__ import annotations

import numpy as np


class ConvergenceTracker:
    """Accumulate best-so-far fitness across evaluations for one run."""

    def __init__(self, capacity: int) -> None:
        """Pre-allocate buffers for ``capacity`` checkpoints."""
        self._values = np.empty(capacity, dtype=np.float64)

    def record(self, nfes: int, best: float) -> None:
        """Store ``best`` fitness observed at evaluation count ``nfes``."""

        def _clamp(value: float) -> float:
            """Floor the recorded value at the known optimum (nested helper)."""
            return max(value, 0.0)

        self._values[nfes] = _clamp(best)
```

Docstrings SHOULD be imperative, one short summary line, expanding only where the
behavior is non-obvious (units, draw order, side effects, determinism caveats).

### 4.2 The only exemptions

`test_docstrings.py` exempts exactly the **vendored** modules via
`_is_vendored_ism(path)`. These are byte-identical copies of upstream code and
are intentionally not re-styled:

| Exempt path | Why |
| --- | --- |
| `src/gsk_family/optimizers/_dt_core.py` | vendored DT-GSK core (~4983 lines), byte-identity-locked |
| `src/gsk_family/optimizers/_dt_subsystems/*` | vendored DT-GSK subsystems (`bound_constraint`, `budget`, `budget_policy`, `basin_memory`, `gained_shared_junior`, `gained_shared_senior`, `interaction_graph`, `_numba_accel`, `_dt_provenance`, `__init__`) |
| `src/gsk_family/analysis/statistics.py` | vendored statistical-analysis core |
| `src/gsk_family/analysis/statistical_tests.py` | vendored statistical-analysis core |

The exemption is encoded as:

```python
_VENDORED_ANALYSIS = {"statistics.py", "statistical_tests.py"}

def _is_vendored_ism(path: Path) -> bool:
    if path.name == "_dt_core.py" or "_dt_subsystems" in path.parts:
        return True
    return "analysis" in path.parts and path.name in _VENDORED_ANALYSIS
```

Note what is **NOT** exempt and DOES need full docstrings: the ISM adapter
`optimizers/dt_gsk.py`, the profile builder `optimizers/_dt_profiles.py`, the
RNG layer `optimizers/_dt_rng.py`, and the rest of `analysis/` (e.g.
`family_report.py`, `result_loader.py`, `figures.py`, `latex_tables.py`,
`project_policy.py`). Do not add new files to the exempt set unless they are a
genuine byte-identical vendored import (see §5).

---

## 5. The Vendored-Code Rule (Byte-Identity Lock)

`dt-gsk` is this project's **proposed method**, migrated byte-identically from
the source DT-GSK v2.1 tree. Its core is **reference-locked**:

- **NEVER edit for behavior:** `optimizers/_dt_core.py`,
  `optimizers/_dt_subsystems/*`, `analysis/statistics.py`,
  `analysis/statistical_tests.py`. These are the same files exempted from the
  docstring gate (§4.2). Casual refactors, reformatting, renaming, or
  "cleanups" are forbidden — they break byte parity.
- **Where adaptation belongs.** If `dt-gsk` must be adapted to the family
  (option mapping, batch objective, dim-aware config, per-dimension bounds), do
  it in the **adapter** `optimizers/dt_gsk.py` or a thin **wrapper**, NOT in the
  vendored core. The adapter already builds the `pub` config via
  `_dt_profiles.build_pub_config`, drives the 13-substream RNG via
  `_dt_rng`, and self-initializes its `5*D` (`np_init_mult*D`) population — that
  is the right place for project-specific glue.
- **What proves the lock (must stay green):**
  - config KAT — `tests/unit/test_dt_profiles.py` (`build_pub_config` field-for-field vs the source `_build_ism_gsk_config` fixture),
  - RNG KAT — `tests/unit/test_dt_rng.py` (13-substream layer),
  - byte-stable regression — `tests/regression/test_dt_gsk_byte_stable.py`
    (golden `best_fitness` values validated byte-identical at `seed=12345`,
    `max_nfes=3000`).

  Any change that alters the vendored core, the RNG substream layer, or the
  `pub`-profile config will fail these. If one breaks, do not "update the
  golden" to make it pass — investigate, because the lock just caught a parity
  regression.
- These determinism/lock rules intersect with thread pinning at D>=50/100; that
  side belongs to [PERFORMANCE_RULES.md](PERFORMANCE_RULES.md). The immutability
  policy belongs to [PROJECT_RULES.md](PROJECT_RULES.md).

---

## 6. Console Output

The project's console output and `results/` byte format are **load-bearing** —
they are deliberately mirrored so they can be diffed against a reference project
(see `runners/output.py`). Do not casually `print()` from inside package code.

- **In package/library code (`optimizers/`, `common/`, `runners/`,
  `benchmark_adapter/`, `analysis/`):** route diagnostics through the standard
  library logger, exactly as `runners/output.py` does:

  ```python
  import logging

  logger = logging.getLogger(__name__)
  ```

  Use `logger.info(...)` / `logger.warning(...)`, not bare `print()`.
- **Campaign progress / human-facing console lines** go through the runner's
  centralized helper `_log_console(enabled, message)` in
  `runners/run_experiment.py` (it is the single gated `print(..., flush=True)`
  site, honoring the `enabled` toggle and producing PowerShell-friendly ASCII
  progress bars via `_progress_bar`). Reuse these helpers rather than scattering
  `print` calls.
- **`print()` is appropriate only in the CLI entry layer** (`cli/run.py`,
  `cli/list.py`, `cli/validate.py`, `cli/stats.py`), which exists to talk to the
  terminal. Even there, you MUST preserve the exact documented format strings
  (banners like `==================== run_all (SPHERE) ====================`,
  `PASS  GSK`, the `DETAILED CONFIGURATION` block) — these are asserted by
  `tests/smoke/test_documentation_commands.py`. Changing whitespace or wording
  silently breaks the smoke gate and reference diffability.
- **NEVER** change the result byte formats in `runners/output.py`
  (`per_run.csv` `%.10e`; convergence `%.16e` + `log10` column;
  `environment.json` key order). That schema is governed by
  [PROJECT_RULES.md](PROJECT_RULES.md) / [BENCHMARK_RULES.md](BENCHMARK_RULES.md).

---

## 7. Determinism Rules in Code

Reproducibility is the whole point of this research software. Code MUST be
deterministic given a seed.

- **No unseeded randomness.** NEVER call `random.*`, `np.random.*` free
  functions, `time.time()`, `datetime.now()`, `uuid`, or `os.urandom` to drive
  any value that affects optimizer trajectory, RNG draws, seed derivation, or
  result ordering. All randomness flows through `RandomContext`
  (`common/rng.py`) and the unified seed schedule
  `get_cec_seed(base_seed=20240620, dim, func, run)`
  (`runners/seed_policy.py`). `dt-gsk` additionally uses its 13-substream layer
  (`_dt_rng.py`) on top of the same threefry generator.
- **Timing is for measurement only.** `time.*` may be used for performance
  metadata (e.g. wall-clock in a profile) but MUST NOT feed any computed result,
  filename of a tracked artifact, or branch that changes numerics.
- **Preserve draw order.** RNG draw order, matrix fill order (column-major),
  integer-draw and permutation conventions are byte-significant. Do not reorder
  draws or vectorize in a way that changes the sequence consumed. The full RNG
  contract is in [PROJECT_RULES.md](PROJECT_RULES.md) and
  `docs/reference/seed_policy.md`.
- **Stable ordering everywhere.** Use deterministic sorts (the codebase uses
  `stable_argsort` / `argsort` for selection and permutations). Do not rely on
  set iteration order or dict insertion order for numeric outcomes.
- **Thread-safe Numba.** The parallel Numba / SGSM / TERRA paths require
  single-thread BLAS/Numba pinning to stay byte-stable, and the process backend
  must never fall back to threads. Those rules — and the
  `NUMBA/OMP/MKL/OPENBLAS_NUM_THREADS=1` pins — are owned by
  [PERFORMANCE_RULES.md](PERFORMANCE_RULES.md); honor them in any code you add to
  a JIT path.

---

## 8. Tests

Tests live under `tests/` in tiers; the suite currently collects 324 tests.
Re-check the live count with `python -m pytest --collect-only -q` rather than
hard-coding a number.

| Tier | Path | What it covers |
| --- | --- | --- |
| Unit | `tests/unit/` | RNG known-answer tests (`test_rng.py`, `test_dt_rng.py`), config/profile KATs (`test_dt_profiles.py`), statistical primitives, docstring gate (`test_docstrings.py`), figures, loaders, helpers |
| Smoke | `tests/smoke/` | per-optimizer smoke runs, CLI smoke, the documentation-command smoke (`test_documentation_commands.py`), stats CLI / `--stats` flag |
| Regression | `tests/regression/` | the validation ladder and the dt-gsk byte-stable golden (`test_dt_gsk_byte_stable.py`) |
| Performance | `tests/performance/` | optional parallel/scalability checks (the `slow` marker) |
| Imports | `tests/test_imports.py` | package import surface |

Rules:

- **Add tests for new behavior.** New public behavior MUST land with a test in
  the appropriate tier. Bug fixes SHOULD include a regression test.
- **Run the gate.** `python -m pytest -q` for broad changes; a targeted file for
  narrow ones (e.g. `python -m pytest tests/unit/test_docstrings.py -q`). Use
  `-m "not slow"` to skip the optional performance tier, `-m slow` to include it.
- **Do not weaken the byte-identity KATs** (§5). If you genuinely changed
  intended behavior of a non-vendored path, update the test deliberately and say
  so; never edit a golden just to silence a red bar.
- Keep tests deterministic and seeded — the same determinism rules in §7 apply
  to test code.

---

## 9. Docs-as-Code

Documentation is gated like code by
`tests/smoke/test_documentation_commands.py`.

- **Required-doc list.** `test_documented_docs_exist()` asserts a fixed list of
  doc and config paths exists. If you **add or move** a documented file, you MUST
  update that list in `tests/smoke/test_documentation_commands.py` in the same
  change, or the smoke gate fails.
- **HTML twins must rebuild and resolve.** `test_html_documentation_generator_rebuilds_site()`
  reruns the builder, and `test_generated_html_local_links_resolve()` walks every
  generated `docs/html/**/*.html` and asserts **every relative `href`/`src`
  resolves to a real file**. After any change to `docs/**/*.md`, docstrings,
  README commands, or navigation, regenerate the static site and commit the
  twins:

  ```powershell
  python scripts\build_docs_html.py
  ```

  Page names flatten to `<subfolder>_<page>.html` (e.g.
  `docs/reference/seed_policy.md` -> `docs/html/reference_seed_policy.html`),
  preserving literal hyphens.
- **UTF-8 clean, no mojibake.** All Markdown and source MUST be ASCII/UTF-8 clean
  — no smart-quote/em-dash corruption, no double-encoded characters. The HTML
  builder reads with `encoding="utf-8"`; broken bytes surface as garbled output.
- **Keep the two runbooks in sync.** The root [runbook.md](runbook.md) and the
  in-site `docs/getting-started/runbook.md` must agree when run commands change.
- **Respect the platform-name rule.** The upstream numeric-platform product
  name is permitted for factual provenance (the vendored eGSK port lineage and
  `docs/reference/seed_policy.md`), but must never describe this project's own
  runtime, which is pure Python (see
  [PROJECT_RULES.md](PROJECT_RULES.md) / [SKILL.md](SKILL.md)).

---

## 10. Commit Hygiene

- **Commit only when asked.** Do NOT commit or push as a side effect of an edit.
  Make the change, run the relevant gates, report — then wait for the explicit
  request to commit. NEVER push without being asked. (Workspace and
  commit-consent rules are in [PROJECT_RULES.md](PROJECT_RULES.md) /
  [SKILL.md](SKILL.md).)
- **Branch off the default branch** if you are on it before committing requested
  work.
- **Co-author trailer.** When you do commit, end the message with the trailer:

  ```text
  Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>
  ```

- **Atomic, in-place changes.** Keep a commit scoped to one coherent change;
  include regenerated `docs/html/` twins in the same commit as the doc/docstring
  change that produced them. Work in-place in this repo root — never create a
  nested or mirror folder.
- **Never bypass hooks.** Do not use `--no-verify` or skip signing unless the
  user explicitly asks; if a hook fails, fix the cause.

---

## 11. Pre-Commit / Pre-Review Checklist

Before you call an edit done, confirm:

1. `python -m ruff check src tests scripts` is clean.
2. The relevant `python -m pytest` tier passes (docstring gate included for any
   new function/class/module).
3. You did **not** edit a vendored byte-identity-locked file for behavior (§5);
   the dt-gsk KATs/regression still pass if you were near that area.
4. New package-code diagnostics go through `logging` / the runner console helper,
   not bare `print` (§6); documented console/byte formats are unchanged.
5. No unseeded randomness or wall-clock leaked into a numeric/result path (§7).
6. New docs are in the required-doc list, `docs/html/` is regenerated and links
   resolve, and everything is UTF-8 clean (§9).
7. You commit only if asked, with the `Co-Authored-By` trailer (§10).

---

*Sibling governance files:* [PROJECT_RULES.md](PROJECT_RULES.md) -
[DESIGN_GUIDE.md](DESIGN_GUIDE.md) - [ARCHITECTURE.md](ARCHITECTURE.md) -
[BENCHMARK_RULES.md](BENCHMARK_RULES.md) -
[PERFORMANCE_RULES.md](PERFORMANCE_RULES.md). Operating contract:
[SKILL.md](SKILL.md). Landing: [README.md](README.md). Commands:
[runbook.md](runbook.md).
