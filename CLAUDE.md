# CLAUDE.md

Auto-loaded every session. It holds what a new session needs to continue
without re-reading the repository, so keep it short. The full pass-by-pass
chronicle that used to live here is REVISION_STATUS.md, Appendix A. **Do not
read the large root documents speculatively** (REVISION_STATUS.md about 186 KB,
README.md about 51 KB, SKILL.md about 48 KB): open only the file a task needs,
using the table at the end. Injected claude-mem observations can be stale; git,
this file and the memory files win. If the copy of this file in your context
has no "Open items" section, it is stale: read CLAUDE.md from disk.

## What this repo is

DT-GSK (Dimension-Tiered Gaining-Sharing Knowledge): the code and evidence
behind one paper. The paper's panel is seven GSK-family optimizers (`gsk`,
`agsk`, `apgsk`, `fdb-agsk`, `atmals-gsk`, `egsk`, and the proposed `dt-gsk`)
on five CEC suites (`cec2011`, `cec2013`, `cec2013lsgo`, `cec2017`, `cec2020`)
under one locked, budget-fair paired protocol; eight external comparators are
also registered. Python package `gsk_family` under `src/`; runner
`python run.py`; console scripts `gsk-*`. Public repository
https://github.com/MostafaMassoud/DT-GSK, branch `main` only. Most files are
frozen or hash-bound: assume nothing is casually editable.

**Claim wording (README, docs, emails):** the learned ISM eigenbasis was shown
harmful (plain coordinate axes beat it at D = 50), so contribution C1 is "a
deterministic final polish", claimed basis-neutrally; C2 (tiering) is claimed
only at D = 10 and D = 50 (the 20 <= D < 50 tier is mis-specified). Saying the
mechanism computes an eigenbasis is fine; calling the eigenbasis a contribution
or a benefit is not (REVISION_STATUS.md section 3, Phase 7). Do not
over-correct: the polish itself still beats no refinement at both active
dimensions, C3 is not narrowed, and the E1 D = 100 eigenframe-vs-coordinate
contrast is SEPARATED (Holm 0.0489; "not separated" is a stale claim that has
recurred five times). There is no hosted CI; never claim one.

## Right now (2026-10-16)

- **The paper is published:** *Algorithms* 2026, 19(9), 769, https://doi.org/10.3390/a19090769
  (online 2026-09-07, CC BY 4.0; manuscript `algorithms-4507562`, accepted
  2026-09-02). README and CITATION.cff record it. Its Data Availability
  Statement prints tag **v2.37**, so `papers/main.tex` stays at v2.37 (D-0070).
  Never rebuild, move or retag a published tag (v2.13 =
  submission, v2.36 = resubmission, v2.37 = the printed article).
- **Last freeze: pass-73 / tag v2.46** (2026-09-03, commit `64c70bb`). **Next
  free governance ids: CR-0054 / D-0079.** Before use, check that
  `grep -c '^CR-0054,' papers/governance/change_request_register.csv` and
  `grep -c '^## D-0079' papers/governance/decision_log.md` both print 0 (a bare
  grep also finds D-0078's own "NEXT free ids" line). One line per pass from
  pass-49 on: `git log --oneline --grep="^Close pass"`.
- **Since v2.46: ordinary commits only** (`git log --oneline v2.46..main`; no
  freeze pass, no ids, no published number changed), pushed 2026-10-16:
  `bc13511` gsk-stats keeps F2 on CEC2020 and CEC2013LSGO (only CEC2017 drops
  it), adds suite default dims and `scripts/build_stats_panel.py` (rank your
  own runs); `4bb1974` runbook.md Part 1 "Run and test DT-GSK" for anyone, with
  `runbook.html` and `docs/getting-started/runbook.md` generated from it, and
  stale run docs fixed repo-wide.
- Never hard-code the test count (PROJECT_RULES 8.2; re-collect with
  `python -m pytest --collect-only -q`). The environment attestation
  (`papers/governance/environment_attestation/attestation.json`, script
  `papers/scripts/make_environment_attestation.py`) and the supplement keep the
  published 618; a re-mint is freeze-pass work (rule 3) and the author's call.

## Open items (next steps)

1. **Runner fixes, proposed as a separate session, not started; covers all of
   this item. Ask the author whether to do it here or start that session.**
   (a) `run.py --stats` drops F2 on CEC2013, CEC2020 and CEC2013LSGO:
   `src/gsk_family/runners/run_experiment.py` (CRLF) about line 509,
   `or (2,)`. Use
   `tuple(sorted(SUITE_EXCLUDED_FUNCS.get(config.suite.upper(), set())))` from
   `src/gsk_family/analysis/result_loader.py` (keys upper case; a bare set
   fails mypy). An empty tuple is passed through by the vendored code (no
   fallback to `(2,)`). The emitter swallows exceptions and prints only
   `[stats] skipped`, so tests must assert that the panel printed (extend
   `tests/smoke/test_stats_flag_smoke.py`). (b) When a summary folder has no
   `<opt>_<suite>_D*.csv` (every run of a cell failed) or, on CEC2011, after
   any skipped run, `src/gsk_family/runners/verification.py`
   `load_generated_tables` (about lines 202-208) reads
   `summary/skipped_runs.csv` and raises "missing a Function column"; test on
   a tmp `summary/` holding only `environment.json` + `skipped_runs.csv`.
   (c) Stale docs: PERFORMANCE_RULES.md about 203-205 (removed tiny-run
   heuristic), README.md about 783 ("separate process pool" per cell). Then
   remove the "known gap" note in docs/research/statistical_analysis.md and the
   `skipped_runs.csv` wording in the runbook Troubleshooting row. Rebuild
   docs/html (code line numbers move the API pages).
2. **Declined by the author 2026-10-15; do not redo without asking:** a pooled
   15-function CEC2013LSGO panel in gsk-stats (needs the vendored
   `analysis/statistical_tests.py`, rule 11).
3. **Author-only, status unknown:** the GitHub Support purge request for the
   two exposed commits was REOPENED 2026-08-28, to be filed after the public
   flip (decision_log.md, "GitHub purge"); nothing records that it was filed.
   Ask the author.
4. Optional, needs author sign-off: README.md line 954 says "Two such commits
   touch other files under" `src/gsk_family/optimizers/`; there are three
   (3539977, 290854d, 86411e6).
5. Optional: the "State snapshot" block (lines 13-19) of four
   `docs/prompt/*.md` files (all but change-register-acceptance-review.md) is
   stale: it calls REVISION_STATUS.md the place to start and gives next free
   CR-0044 / D-0069 beside pass-73. Point it at CLAUDE.md "Right now", refresh
   the ids, then rebuild docs/html.

## Never break these

1. **Four DT-GSK modules are hash-gated:** `dt_gsk.py`, `_dt_core.py`,
   `_dt_profiles.py`, `_dt_rng.py` under `src/gsk_family/optimizers/`
   (`papers/scripts/validate_provenance_claims.py`). Even a comment edit fails.
   `_dt_subsystems/` is not hash-gated but is equally locked (PROJECT_RULES 5.3).
2. **`benchmarks/cec_reference_results/` is READ-ONLY** frozen evidence; never
   regenerate it. `run.py` and gsk-stats both default to `results/_run_all/`,
   which holds tracked CEC2020/CEC2013LSGO staging, so always pass
   `--output-root` to run.py and `--out` to gsk-stats (only
   `scripts/run_campaign.py` should write there). `results/_revision/` is
   untracked by design (D-0049). Evidence releases are additive and
   non-superseding: frozen analysis outputs are never re-minted; a new finding
   gets a new release id.
3. **`papers/` is a frozen manuscript under change control.** Any edit there
   needs a new freeze pass (D-0045). Never edit a submitted state in place. A
   change "to the manuscript" reaches only the file edited: the letters, the
   supplement and the DOCX channel (`build_docx.py`) each need their own edit
   and render check.
4. **Never author LaTeX, regex or code through a bash heredoc** (backslash
   collapse has shipped corrupted macros). Use exact-match file editing; the
   project skill `dtgsk-maintain` has an EOL-safe applier.
5. **Line endings are per file and can change under you.** `core.autocrlf` is
   true here: tracked text is stored LF, but many working copies are CRLF
   (README.md +BOM, REVISION_STATUS.md, PROJECT_RULES.md, about half of
   `src/**/*.py` incl. run_experiment.py and result_loader.py); SKILL.md is
   LF +BOM. The papers/ freeze files are `-text` in .gitattributes and must stay
   byte-exact. Check the bytes, lone CR included, before a multi-line edit.
6. **Append-only trees:** `papers/build_prompt_phases/`,
   `papers/review_2026_07_22/`, `papers/governance/remediation_2026_07_18/`.
   Stale content there is correct: do not fix it (carve-out:
   `phase_09/evidence_binding_verification.csv` is refreshed each pass).
7. **Never run `papers/scripts/finalize_evidence.py`** (nor
   `scripts/run_campaign.py` without `--skip-finalize`, which chains it).
8. **Work only in this checkout.** Other copies exist (paths in memory): a
   sibling checkout of the same remote only ever gets `git pull --ff-only`; the
   PhD-Projects monorepo copy is a separate, divergent repository, never worked
   in. Each freeze manifest hashes only its own tree.
9. **The repository is PUBLIC; some files are deliberately untracked** (D-0049):
   reviewers' reports, the response letter, the co-author handoff, seven
   copyrighted PDFs, `papers/review_2026_08_24/PRIVATE_OPS.md`. Never re-add
   them or push history that contains them; never fetch, merge or copy the
   author's private history bundle into this repo or any public place. Tracked
   files never quote the reviewers verbatim and never carry the bundle's
   location or the purge SHAs (those live only in PRIVATE_OPS.md). The
   pre-registration (`papers/review_2026_08_24/revision_experiments_preregistration.md`)
   is public on purpose: keep it tracked.
10. **A `.gitignore` glob that does not cross `/` is not an exclusion.** Check
    with `git check-ignore -v <path>`.
11. **The vendored analysis modules `analysis/statistical_tests.py` and
    `analysis/statistics.py` stay untouched** (PROJECT_RULES 5.3; phase6b reads
    `friedman_rank_test`'s `excluded=(2,)` default).
12. **Generated files are never hand-edited:** `runbook.html`,
    `docs/getting-started/runbook.md`, `docs/html/`. Edit the source and
    regenerate; commit the generated files with it.
13. **Gate side effects:** `validate_cross_format_parity.py` and
    `validate_evidence_bindings.py` rewrite tracked CSVs unless given
    `--csv <scratch path>`; `phase6b_run_analysis_newsuites.py` rewrites
    `papers/analysis/` unless given `--out-root`.
14. **Author style:** no em-dashes (U+2014) in new prose; plain, simple
    sentences in anything readers or editors see.
15. **Scratch stays outside the repo.** Temporary files go in the session
    scratchpad; never create scratch trees, plan folders or agent scaffolding
    under this root.

## Fast paths

- **Python:** the machine's global interpreter may import a foreign editable
  `gsk-family` from another checkout. `run.py` and pytest find `src/` by
  themselves; bare `gsk-*` and `python -m gsk_family...` need
  `PYTHONPATH=src` (plus `PYTHONDONTWRITEBYTECODE=1`), or a venv made with
  `py -3.10 -m venv .venv` and `pip install -e ".[dev]"`. Python 3.10.11 is the
  attested version.
- **Reproducing archived numbers:** pass `--numba-threads 1`; at D >= 50 also
  set the six thread variables (OMP, MKL, OPENBLAS, VECLIB_MAXIMUM, NUMEXPR,
  NUMBA) to 1 before Python starts (runbook.md Part 1 Step 5). `run.py` pins no
  threads itself; `scripts/run_campaign.py` pins all six and
  `scripts/run_revision_experiments.py` five.
- **Tests and lint:** `python -m pytest -q -p no:cacheprovider` (about 2 min on
  an idle machine, 7-10 min under load), `python -m ruff check . --no-cache`,
  `python scripts/validate_profile_lock.py --root .`.
- **Prove the paper is unaffected:** runbook.md Part 2, stage 8b: 13
  papers/scripts gates plus `scripts/check_package_contents.py` (builds from
  `git archive HEAD`, so run it after committing); all exit 0 (check_manifest
  15/15 and sources 2/2, frozen analysis 115/115, parity 755 rows 0 FAIL).
  Mind rule 13.
- **Docs:** edit runbook.md, then `python scripts/build_runbook_html.py`, then
  `python scripts/build_docs_html.py`. Any `docs/**/*.md` or `src/**/*.py`
  change needs `build_docs_html.py` too: the API pages anchor every function by
  its line number, and no test catches a stale docs/html.
  `tests/smoke/test_runbook_html.py` fails when the runbook twins are stale or
  a runbook anchor breaks.
- **gsk-stats byte-identity proof:** `PYTHONHASHSEED=0`, non-strict, compare
  against `git archive HEAD src` extracted to scratch.
- **Ordinary commit vs freeze pass:** files outside papers/, the freeze
  manifests and the four hash-gated modules take ordinary commits on `main`
  (imperative subject, prose body with evidence, `Co-Authored-By` trailer, no
  em-dashes). A freeze pass follows runbook.md Part 2 "Freeze-Pass Cycle";
  first read REVISION_STATUS.md section 7 and all of Appendix A: its "Right
  now" entries hold the per-pass traps (`\hl` cannot wrap `\ref`; audit for
  lone CR; CITATION.cff carries no leading v, so a v2.x sweep misses it; run
  check_reproducibility_manifest.py after every rebuild, not with the mint),
  and "Conventions" holds the id and SHA rules (SHAs from `git rev-parse`,
  never typed; CITATION.cff, SUBMISSION_KIT.md and
  submission_package_manifest.json move with every tag; `published_commit`
  names the previous close). Commit and push only when the author asks.
- **Outside researchers asking how to run the code:** point them to
  runbook.md Part 1 (or runbook.html in their clone).
- The local project skill **`dtgsk-maintain`** (`.claude/skills/`, not in git)
  holds these checklists, the EOL-safe edit applier and `verify.sh` (the whole
  ladder). It exists only on the author's machine; elsewhere use the Edit tool
  and runbook.md Part 2 stage 8b with the rule 13 redirects.

## Lessons that generalise

- Diagnoses from review instruments are usually right; their prescribed fixes
  often are not (10 of 11 unsafe in one audit). Challenge the fix, not just the
  finding, and verify against bytes or the render.
- Read the built PDF or rendered page: source greps miss line-wrapped phrases
  and table cells.
- State the gap, never the causation. Closed, do not revive: the D-0051
  diagnostic re-execution stays diagnostic (author, 2026-08-28); the CR-0015
  "larger disclosure" (rejected on challenge); the C4 "fix" (refuted).
- Publication was a squash through 2026-08-28: governance SHAs recorded before
  then may not resolve. Since then ordinary commits are published as they are.

## Where detail lives

| Need | File |
|---|---|
| Run and test the code (for anyone) | runbook.md Part 1, or runbook.html |
| Pipeline, gates, freeze cycle (maintainers) | runbook.md Part 2 |
| Settled decisions, trap table | REVISION_STATUS.md sections 4 and 7 |
| Pass-by-pass history | REVISION_STATUS.md Appendix A (about line 1680; bold `**Pass-NN` entries from pass-49 on) |
| Orientation, directory tree | REPO_MAP.md |
| Agent operating contract | SKILL.md |
| Module structure, data flow | ARCHITECTURE.md |
| Design principles, how to extend | DESIGN_GUIDE.md |
| Style, determinism, KATs, vendored exemptions | CODING_STANDARD.md |
| Governance rules | PROJECT_RULES.md |
| Suite protocols, budgets, seeds | BENCHMARK_RULES.md |
| Threading and speed | PERFORMANCE_RULES.md |
| Runtime-acceleration method | docs/development/ACCELERATION_CAMPAIGN_PROMPT.md (Appendix A) |
| Decisions; what is public vs withheld | `papers/governance/decision_log.md` (D-0049) |
| Claim to evidence bindings | `papers/governance/claims_evidence_matrix.csv` |

FINAL_RELEASE_REPORT.md is historical (CEC2017 only, pre-submission); do not
read it for current status.
