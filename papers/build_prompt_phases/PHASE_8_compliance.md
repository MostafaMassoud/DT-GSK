# PHASE 8 — Compliance & Final Build

**Objective:** Prove — with a machine-checkable artifact per clause — that every Part 2 constraint holds, that both `papers/main.tex` and `papers/supplementary.tex` compile clean, and that the repo's green gates still pass, so the manuscript can be handed to submission with nothing left to trust on faith.

> This file expands **Phase 8** of `papers/PAPER_BUILD_PROMPT.md` (and **Part 10**, the acceptance gates / definition of done) into concrete, grounded checks. It **follows** `papers/build_prompt_phases/PHASE_7_review.md` (adversarial review, which must have closed every major/must-fix) and **hands off** to `papers/build_prompt_phases/PHASE_9_submission.md` (submission package). Phase 8 changes nothing scientific: it recompiles, counts, cross-checks, and — only where a check fails — migrates content main↔supplement or fixes a build defect. It never invents a number, a citation, or a result.

All commands assume the current directory is the repo root:

```
D:\AI\PhD-Projects\00-GSK-Family\02-GSK_Family_Python_v1.1
```

Windows is primary (PowerShell), with Bash equivalents where useful. Use `python` (not `python3`). The manuscript's bibliography driver is **BibTeX** — `papers/main.tex` ends with `\bibliography{references}` and loads the class via `\documentclass[algorithms,article,submit,moreauthors,pdftex]{Definitions/mdpi}`. Compile with `latexmk` if available, else run explicit `pdflatex`/`bibtex` passes (both spelled out in 8.5).

---

## Prerequisites

- [ ] **Phase 7 is done.** `papers/build_prompt_phases/PHASE_7_review.md` exit gate is green: `review_R1.md` has **zero open majors**, `review_R2.md` has **zero open must-fixes**, and `revision_log.md` records the resolution of each. Phase 8 audits a frozen draft — do not run it against a manuscript still under revision.

- [ ] **Clean tree at a known commit.** The compliance evidence is only as trustworthy as the tree it is produced on.

  ```powershell
  git status --porcelain
  git rev-parse HEAD
  ```

  ```bash
  git status --porcelain
  git rev-parse HEAD
  ```

  If `git status --porcelain` prints anything under `results/`, `benchmarks/`, `optimizers/`, `src/`, or `papers/{tables,figures,sections}`, **stop and reconcile** — a dirty tree makes the number-binding (8.3) and reproducibility (8.4) checks meaningless. Record this HEAD as the **compliance SHA**; it is what the checks below cite, and it should equal the Phase 0 anchor SHA unless Phase 2/3 legitimately advanced it.

- [ ] **Phase 0/2 provenance artifacts present.** 8.3 and 8.4 consume them directly:
  - `papers/build_prompt_phases/data_ledger.csv` (the (optimizer × suite × dim) → source_path + commit_sha ledger from Phase 0, extended by Phase 2 with the `table_or_figure` binding column of Appendix D.1).
  - `papers/build_prompt_phases/asset_map.md` (table/figure → generator + backing CSV).
  - `papers/build_prompt_phases/_bibkeys.txt` (the frozen 57-key citation universe dumped in Phase 0.4).
  If any is missing, Phase 8 cannot certify C2 — return to the phase that owns it.

- [ ] **A LaTeX toolchain is on PATH.** Confirm before you start so 8.1/8.5 do not fail for a trivial reason:

  ```powershell
  (Get-Command pdflatex).Source; (Get-Command bibtex).Source
  try { (Get-Command latexmk -ErrorAction Stop).Source } catch { "latexmk: not found (use explicit passes in 8.5)" }
  ```

  ```bash
  command -v pdflatex; command -v bibtex; command -v latexmk || echo "latexmk: not found (use explicit passes in 8.5)"
  ```

---

## Tasks

Each task is a **verifiable check**: exact commands, then an explicit **pass criterion**. A task is not "done" because it ran — it is done when its pass criterion is met and its evidence artifact exists. Do 8.5 (build) before 8.1–8.4, because 8.1/8.2/8.4 all read the freshly produced `main.pdf` / `.log` / `.aux`; the numbering below follows Part 10's clause order, not execution order. Recommended execution order: **8.5 → 8.1 → 8.2 → 8.3 → 8.4 → 8.6**.

---

### 8.1 — Page-budget check (C3)

**Goal.** Confirm the typeset **main text** is within the budget for the chosen journal, and — if it is over — migrate content to the supplement rather than shrink figures or crush margins.

**Budget (from Part 3 §3.4 + C3):**
- **Primary — MDPI *Algorithms* (single-column):** no hard cap; self-discipline ceiling **≈ 16–22 typeset pp** excluding references, per the block table in §3.4.
- **Fallback — IEEE TEC (double-column):** **hard 14 pp** for a regular paper; over-length is penalized. If the PI retargeted to TEC in Phase 1, this is the binding limit.

**Step 8.1.a — Read the typeset page count from the build.** The most reliable count is the one LaTeX itself reports in the log (produced by 8.5); no extra tool needed:

```powershell
Select-String -Path papers\main.log -Pattern 'Output written on .*\((\d+) page' `
  | ForEach-Object { $_.Matches.Groups[1].Value } | Select-Object -Last 1
```

```bash
grep -oE 'Output written on [^(]*\(([0-9]+) page' papers/main.log | tail -1
```

If `pdfinfo` (poppler) is on PATH, cross-check:

```bash
pdfinfo papers/main.pdf | grep -i '^Pages'
```

**Step 8.1.b — Subtract the references pages** (the budget excludes them). The bibliography starts at `\bibliography{references}`; note the page it lands on from the PDF and subtract the reference pages from the total to get the **main-text page count**. Record both numbers.

**Step 8.1.c — If over budget, migrate — do not shrink.** Overflow is a design smell (C3), not a licence to shrink figures below legibility or drop `\clearpage`s. Legitimate moves, in order of preference:
1. Move a **full per-function table** from `papers/tables/*.tex` out of `main.tex`'s `\input` spine into `sections/supplementary_content.tex` (it almost certainly already has a summary counterpart in the main text — C4 keeps *one* summary table per dimension in main, the full grids in supplement).
2. Move all but one convergence figure (`papers/figures/convergence/*`) to the supplement, keeping the 2–3 that show both a win and an honest hard case (C4 / Part 6.6).
3. Tighten prose flagged as padding by the Phase 6/7 A1 pass — never by deleting a reported loss or limitation (C7).
   After any migration, **recompile (8.5) and re-count (8.1.a).** Do not hand-edit the PDF.

**Pass criterion.** Main-text page count (excl. references) ≤ the chosen journal's ceiling (≤ 22 pp MDPI; ≤ 14 pp TEC), achieved without reducing any figure below print legibility (verified visually) and without exiling a conclusion-critical result to the supplement (that is 8.x's C4 concern, cross-checked here). **Evidence:** the recorded page count + the migration diff (if any).

---

### 8.2 — Citation check (C1)

**Goal.** Prove the cite-set is a subset of the 57 locked keys, that **every** bib key is used at least once, and that the build produced **zero** undefined-citation warnings.

**Step 8.2.a — Static set check (source-of-truth: the `.tex` + `.bib`).** Run the cross-check script (full listing in *Worked examples → A*). It parses entry keys from `papers/references.bib`, scans every `\cite`-family command across `papers/main.tex`, `papers/supplementary.tex`, and `papers/sections/*.tex`, and prints three sets: **undefined** (cited but not in bib), **unused** (in bib but never cited), and **out-of-universe** (cited but not in `_bibkeys.txt`).

```powershell
python papers\build_prompt_phases\_cite_check.py
```

```bash
python papers/build_prompt_phases/_cite_check.py
```

**Step 8.2.b — Confirm the universe is exactly 57 and mirrors the master.** Re-assert the Phase 0.4 invariant so a stray entry added mid-build is caught:

```powershell
"bib entries = " + (Select-String papers\references.bib -Pattern '^@\w+\{[^,]+,').Count
Compare-Object `
  (Select-String papers\references.bib -Pattern '^@\w+\{([^,]+),' | ForEach-Object { $_.Matches.Groups[1].Value } | Sort-Object) `
  (Select-String reference_papers\references.bib -Pattern '^@\w+\{([^,]+),' | ForEach-Object { $_.Matches.Groups[1].Value } | Sort-Object)
```

```bash
grep -cE '^@[A-Za-z]+\{' papers/references.bib   # expect 57
diff <(grep -oE '^@[A-Za-z]+\{[^,]+' papers/references.bib | sed -E 's/^@[A-Za-z]+\{//' | sort) \
     <(grep -oE '^@[A-Za-z]+\{[^,]+' reference_papers/references.bib | sed -E 's/^@[A-Za-z]+\{//' | sort)
```

**Step 8.2.c — Dynamic check from the build (authoritative for "undefined").** After 8.5, BibTeX and LaTeX record the real resolution. Grep the logs:

```powershell
Select-String -Path papers\main.log,papers\supplementary.log -Pattern "Citation .* undefined|There were undefined references"
Select-String -Path papers\main.blg,papers\supplementary.blg -Pattern "Warning--I didn't find a database entry|Warning--empty"
```

```bash
grep -nE "Citation .* undefined|There were undefined references" papers/main.log papers/supplementary.log
grep -nE "Warning--I didn't find a database entry|Warning--empty" papers/main.blg papers/supplementary.blg
```

**Pass criterion.** 8.2.a prints **empty** undefined, **empty** out-of-universe, and **empty** unused sets; 8.2.b reports **57** entries and an empty `Compare-Object`/`diff`; 8.2.c matches **nothing**. If "unused" is non-empty, either cite the key semantically-correctly (Part 8 gives the sanctioned role of each key) or, only with P1 sign-off, remove it and re-mirror `reference_papers/references.bib` — never leave a dangling entry. **Evidence:** the `_cite_check.py` stdout (all-empty), the entry count, and the empty log greps.

---

### 8.3 — Number-binding check (C2)

**Goal.** For every reported number — each table cell, each plotted figure point, each in-prose statistic — assert it equals what the **named generator produces from the committed CSV**, and that the binding is logged with a commit SHA. This is the anti-fabrication gate.

**Step 8.3.a — Confirm the binding ledger is complete.** `papers/build_prompt_phases/data_ledger.csv` carries Appendix D.1's schema `optimizer, suite, dimension, n_runs, seed_policy, source_path, commit_sha, table_or_figure`. Every `papers/tables/T*.tex` and every `papers/figures/**` referenced by `main.tex`/`supplementary.tex` must appear in the `table_or_figure` column with a non-empty `source_path` and `commit_sha`:

```powershell
$ledger = Import-Csv papers\build_prompt_phases\data_ledger.csv
$bound   = $ledger | Where-Object { $_.table_or_figure } | ForEach-Object { $_.table_or_figure } | Sort-Object -Unique
$tables  = Get-ChildItem papers\tables\T*.tex | ForEach-Object { $_.BaseName }
$tables | Where-Object { $bound -notcontains $_ } | ForEach-Object { "UNBOUND TABLE: $_" }
$ledger | Where-Object { $_.table_or_figure -and (-not $_.source_path -or -not $_.commit_sha) } |
  ForEach-Object { "MISSING PROVENANCE: $($_.table_or_figure)" }
```

```bash
python - <<'PY'
import csv, glob, os
rows = list(csv.DictReader(open("papers/build_prompt_phases/data_ledger.csv", encoding="utf-8")))
bound = {r["table_or_figure"] for r in rows if r.get("table_or_figure")}
for t in glob.glob("papers/tables/T*.tex"):
    b = os.path.splitext(os.path.basename(t))[0]
    if b not in bound: print("UNBOUND TABLE:", b)
for r in rows:
    if r.get("table_or_figure") and (not r.get("source_path") or not r.get("commit_sha")):
        print("MISSING PROVENANCE:", r["table_or_figure"])
PY
```

Present tables to expect at binding time: `T01`–`T16`, `T16_bca`, `T21`, `T22`. **`T17`–`T20` do not exist** (Phase 0 finding) — do not invent bindings for them. Ablation fragments, if present, are named `papers/tables/ablation_<tag>.tex` (emitted by `gen_ablation_table()` in `papers/scripts/generate_latex_tables.py` from `results/ablation/ablation_matrix_rank_summary_<suite>[_D<dim>].csv`) — they are not matched by the `T*.tex` glob, so bind them explicitly.

**Step 8.3.b — Spot-audit table cells against the generator.** The LaTeX table bodies are frozen `tabular` fragments (numbers baked in; no CSV hook), emitted upstream by `src/gsk_family/analysis/latex_tables.py`. Re-emit each audited table from committed data and diff against the checked-in `.tex`. For a spot audit, pick at least: one per-dimension summary table, `T16_bca` (BCa CIs), and one rank/p-value table. Compare the re-emitted body to the committed one:

```powershell
# Re-emit into a scratch dir, then diff. Adjust the invocation to latex_tables.py's real CLI/API.
python -c "import src.gsk_family.analysis.latex_tables as L; print(hasattr(L,'main'))"
git diff --no-index --stat papers\tables\T16_bca.tex $env:TEMP\T16_bca.regenerated.tex
```

```bash
git diff --no-index papers/tables/T16_bca.tex /tmp/T16_bca.regenerated.tex
```

If the emitter has no re-emit entry point, fall back to a **numeric** audit: parse the numbers out of the `.tex` cell and assert equality (to the reported precision) against the value read from the `source_path` CSV named in the ledger for that cell. A mismatch means the table is **stale** — regenerate it via the Phase 2/3 pipeline; never hand-patch the cell.

**Step 8.3.c — Spot-audit figure points.** Convergence figures come from `scripts/plot_convergence_from_curves.py` reading `results/_run_all/<optimizer>/<suite>/curves/*.csv`; rank/CD figures come from `src/gsk_family/analysis/figures.py` over `results/_analysis/`. For one audited convergence figure, confirm the plotted endpoint equals the final value in the backing curve CSV named in the ledger. Never hand-edit a plotted number — re-run the generator.

**Step 8.3.d — Prose numbers.** Every quantified claim in `sections/*.tex` (e.g. a Friedman-rank lead, an A12 value, a "1.69× gap") must trace to the same committed source as the table/figure it summarizes. Grep the prose for numerals near claim verbs and confirm each has a ledger row or a `\ref` to a bound exhibit:

```bash
grep -nE '[0-9]+\.[0-9]+(×|x| ?%)?' papers/sections/*.tex | head -60
```

**Pass criterion.** 8.3.a prints **no** `UNBOUND TABLE` / `MISSING PROVENANCE` lines; every spot-audited cell/point matches its generator output exactly (empty `git diff`); every audited prose number resolves to a ledger row or a bound exhibit; the ledger's `commit_sha` equals the compliance SHA (or an earlier SHA that still touches the same, unchanged CSV). **Evidence:** the ledger with a full `table_or_figure` column, the empty spot-audit diffs, and the recorded compliance SHA.

---

### 8.4 — Reproducibility-appendix check (C2 provenance / Part 9.5)

**Goal.** Confirm the supplement's reproducibility appendix states the three things every "reproducible from" claim rests on — the **FP-regime sentinel**, the **seed formula**, and the **commit SHA** — and that each matches the committed evidence.

**Step 8.4.a — FP-regime sentinel present in `environment.json` and quoted in the supplement.** The canonical CEC2017 sentinel lives at `fp_regime.sentinel` in each `environment.json` and begins `8bda40d8`. Confirm it across the runs and read the exact value:

```powershell
Get-ChildItem -Recurse -File -Filter environment.json benchmarks\cec_reference_results, results\_run_all | ForEach-Object {
  $j = Get-Content $_.FullName -Raw | ConvertFrom-Json
  [pscustomobject]@{ path = Resolve-Path -Relative $_.FullName; sentinel = $j.fp_regime.sentinel }
} | Format-Table -AutoSize
```

```bash
find benchmarks/cec_reference_results results/_run_all -name environment.json | while read f; do
  echo "$f -> $(python -c "import json,sys;print(json.load(open(sys.argv[1]))['fp_regime']['sentinel'])" "$f")"
done
```

(The reference panel `benchmarks/cec_reference_results/` is the primary evidence tree — sweep it first; `results/_run_all` covers the local reproductions.)

Then confirm that same sentinel string is quoted verbatim in the supplement's reproducibility appendix:

```powershell
Select-String -Path papers\sections\supplementary_content.tex -Pattern '8bda40d8[0-9a-f]+'
```

```bash
grep -noE '8bda40d8[0-9a-f]+' papers/sections/supplementary_content.tex
```

Any CEC2017 `environment.json` whose sentinel does **not** begin `8bda40d8` is a hard stop (a different FP regime; runs cannot be pooled) — surface it, do not paper over it.

**Step 8.4.b — Seed formula stated.** The appendix must state the seed policy exactly as implemented in `src/gsk_family/runners/seed_policy.py`: **`get_cec_seed(20240620, dim, func, run) % 2147483646 + 1`**, with base seed `20240620`. Confirm the prose matches the source and the run counts (CEC2017 = 51, F2 excluded; CEC2011 = 25; CEC2013 = 51, D ∈ {10,30,50}):

```powershell
Select-String -Path runners\seed_policy.py -Pattern 'def get_cec_seed|2147483646'
Select-String -Path papers\sections\supplementary_content.tex -Pattern 'get_cec_seed|2147483646|20240620'
```

```bash
grep -nE 'def get_cec_seed|2147483646' src/gsk_family/runners/seed_policy.py
grep -nE 'get_cec_seed|2147483646|20240620' papers/sections/supplementary_content.tex
```

**Step 8.4.c — Commit SHA cited.** The appendix must cite the compliance SHA (from Prerequisites) as the "reproducible from" anchor, and it should match `git_commit` recorded in the `environment.json`s used for the reported cells:

```bash
git rev-parse HEAD
grep -noE '[0-9a-f]{7,40}' papers/sections/supplementary_content.tex | head
```

**Pass criterion.** The sentinel appears in every CEC2017 `environment.json` (prefix `8bda40d8`) **and** is quoted verbatim in the supplement; the seed formula in the supplement is character-for-character the `seed_policy.py` formula; the commit SHA cited in the supplement equals the compliance SHA. **Evidence:** the sentinel table, the matched grep lines, and the SHA equality.

---

### 8.5 — Build check (Phase 8 build gate / Appendix D.4)

**Goal.** Compile both documents to clean PDFs with **no** undefined references, **no** missing figures, and no overfull boxes bad enough to hurt legibility.

**Step 8.5.a — Compile with `latexmk` (preferred).** `latexmk` sequences the pdflatex/bibtex passes automatically:

```powershell
cd papers
latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
latexmk -pdf -interaction=nonstopmode -halt-on-error supplementary.tex
cd ..
```

```bash
( cd papers && latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex && \
                latexmk -pdf -interaction=nonstopmode -halt-on-error supplementary.tex )
```

**Step 8.5.b — Explicit passes (fallback if `latexmk` is absent).** The MDPI class + BibTeX bibliography needs the classic four-pass dance (pdflatex → bibtex → pdflatex → pdflatex) so labels, citations, and cross-refs all settle:

```powershell
cd papers
foreach ($doc in 'main','supplementary') {
  pdflatex -interaction=nonstopmode -halt-on-error "$doc.tex"
  bibtex   $doc
  pdflatex -interaction=nonstopmode -halt-on-error "$doc.tex"
  pdflatex -interaction=nonstopmode -halt-on-error "$doc.tex"
}
cd ..
```

```bash
( cd papers && for doc in main supplementary; do
    pdflatex -interaction=nonstopmode -halt-on-error "$doc.tex"
    bibtex   "$doc"
    pdflatex -interaction=nonstopmode -halt-on-error "$doc.tex"
    pdflatex -interaction=nonstopmode -halt-on-error "$doc.tex"
  done )
```

**Step 8.5.c — Grep the logs for the four defect classes.** (See *Worked examples → B* for the combined clean-log grep.)

```powershell
foreach ($log in 'papers\main.log','papers\supplementary.log') {
  "=== $log ==="
  Select-String -Path $log -Pattern 'undefined|Overfull|Underfull|LaTeX Warning: Reference|File .* not found|No file .*\.(pdf|png)'
}
```

```bash
for log in papers/main.log papers/supplementary.log; do
  echo "=== $log ==="
  grep -nE 'undefined|Overfull|Underfull|LaTeX Warning: Reference|File .* not found|No file .*\.(pdf|png)' "$log"
done
```

**Resolution steps by class:**
- **Undefined reference/citation** (`LaTeX Warning: Reference ... undefined`, `Citation ... undefined`): a missing `\label`, a typo'd `\ref`/`\cite`, or a not-yet-run bibtex pass. Fix the label/key; re-run the full pass sequence (a single pdflatex run will not clear a citation that needs bibtex + two more passes).
- **Missing figure** (`File ... not found`, `No file ...pdf`): a figure moved between `papers/figures/{convergence,diagrams,flowchart,ranks,taxonomy,traces}/` or was renamed. Fix the `\includegraphics` path; regenerate the figure from its Phase-3 generator if it is genuinely absent — do not comment out the `\includegraphics`.
- **Overfull `\hbox`**: acceptable if small (a few pt) and it does not push content into the margin; a large one that visibly runs into the margin must be fixed by rewording the line, adding a `\-` hyphenation hint, or resizing an oversized table with `\resizebox`/`\small` — never by disabling `\overfullrule` or ignoring it.
- **Underfull `\hbox`/`\vbox`**: cosmetic; log it, fix only if it produces a visibly ugly gap.

**Pass criterion.** Both `papers/main.pdf` and `papers/supplementary.pdf` are produced; the grep in 8.5.c returns **no** `undefined`, **no** missing-figure lines, and **no** margin-breaking overfull box; the last pdflatex pass reports no "There were undefined references." / "Rerun to get cross-references right." **Evidence:** the two PDFs + the clean-log grep output.

---

### 8.6 — Repo green gates (Part 10 "Repo" clause)

**Goal.** Re-run the four repo gates so the paper's claims *about the software* (byte-identity-locked ISM core, passing test suite, lint-clean, docs build) remain true at the compliance SHA.

```powershell
python -m pytest -q
python -m ruff check .
python scripts\validate_profile_lock.py --root .
python scripts\build_docs_html.py
```

```bash
python -m pytest -q
python -m ruff check .
python scripts/validate_profile_lock.py --root .
python scripts/build_docs_html.py
```

**Pass criterion.** All four exit **0**: `pytest` reports no failures, `ruff check .` reports "All checks passed!", `validate_profile_lock.py --root .` confirms the frozen ISM profile is byte-identical, and `build_docs_html.py` completes. A red gate here blocks the exit gate — a paper that claims a green, reproducible codebase must actually have one. **Evidence:** the four commands' pass output + exit codes recorded in the compliance checklist.

---

## Worked examples

### A — Citation cross-check script (`papers/build_prompt_phases/_cite_check.py`)

Parses bib keys, scans every `\cite`-family macro across the manuscript `.tex`, does the set algebra, and prints the three violation sets. Exits non-zero on any violation so it can gate a script/CI. (Consistent with Appendix D.2; reuses the Phase 0.4 `_bibkeys.txt` universe when present.)

```python
#!/usr/bin/env python
"""Phase 8.2 citation cross-check. Run from repo root: python papers/build_prompt_phases/_cite_check.py"""
import glob, re, sys, os

BIB      = "papers/references.bib"
UNIVERSE = "papers/build_prompt_phases/_bibkeys.txt"   # frozen 57 from Phase 0.4
TEX      = ["papers/main.tex", "papers/supplementary.tex", *glob.glob("papers/sections/*.tex")]

# 1) bib keys actually defined in references.bib
bibkeys = set(re.findall(r'^@[A-Za-z]+\{([^,]+),', open(BIB, encoding="utf-8").read(), re.M))

# 2) the frozen 57-key universe (fall back to bibkeys if the dump is absent)
universe = set(l.strip() for l in open(UNIVERSE, encoding="utf-8")) if os.path.exists(UNIVERSE) else set(bibkeys)

# 3) every \cite{a,b}, \citep, \citet, \citeauthor, \citeyear ... -> individual keys
cite_cmd = re.compile(r'\\(?:cite|citep|citet|citeauthor|citeyear|autocite|textcite)\*?(?:\[[^\]]*\])*\{([^}]+)\}')
cited = set()
for f in TEX:
    for m in cite_cmd.finditer(open(f, encoding="utf-8").read()):
        cited.update(k.strip() for k in m.group(1).split(",") if k.strip())

undefined      = sorted(cited - bibkeys)      # cited but no bib entry  -> C1 violation
unused         = sorted(bibkeys - cited)      # bib entry never cited   -> C1 violation
out_of_universe = sorted(cited - universe)    # cited outside the 57    -> C1 violation

print(f"bib entries      : {len(bibkeys)}  (expect 57)")
print(f"distinct cites   : {len(cited)}")
print(f"undefined        : {undefined or 'NONE'}")
print(f"unused           : {unused or 'NONE'}")
print(f"out_of_universe  : {out_of_universe or 'NONE'}")

sys.exit(1 if (undefined or unused or out_of_universe or len(bibkeys) != 57) else 0)
```

Expected clean run:

```
bib entries      : 57  (expect 57)
distinct cites   : 57
undefined        : NONE
unused           : NONE
out_of_universe  : NONE
```

### B — `latexmk` invocation + a clean-log grep

```bash
( cd papers && latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex )

# One grep, four defect classes. A clean build prints only the two headers.
for log in papers/main.log papers/supplementary.log; do
  echo "=== $log ==="
  grep -nE 'undefined|Overfull|LaTeX Warning: Reference|File .* not found|No file .*\.(pdf|png)' "$log" || echo "  (clean)"
done
```

A clean result looks like:

```
=== papers/main.log ===
  (clean)
=== papers/supplementary.log ===
  (clean)
```

### C — Page-count check (main text, references excluded)

```bash
# total typeset pages, straight from the log LaTeX wrote
total=$(grep -oE 'Output written on [^(]*\(([0-9]+) page' papers/main.log | grep -oE '[0-9]+' | tail -1)
echo "main.pdf total pages   : ${total:-<not found; recompile 8.5>}"
echo "MDPI ceiling (excl refs): 22   |   IEEE-TEC hard cap: 14"
# subtract the references pages by reading where \bibliography lands in the PDF (pdfinfo/manual),
# then: main_text_pages = total - reference_pages   ->   compare to the ceiling above.
```

PowerShell equivalent for the total:

```powershell
$total = Select-String -Path papers\main.log -Pattern 'Output written on .*\((\d+) page' |
  ForEach-Object { $_.Matches.Groups[1].Value } | Select-Object -Last 1
"main.pdf total pages   : $total"
"MDPI ceiling (excl refs): 22 | IEEE-TEC hard cap: 14"
```

---

## Pitfalls & anti-patterns

- **Shrinking figures (or margins) to fit the budget.** C3 is explicit: overflow means content belongs in the supplement (8.1.c), not that a figure should be `\resizebox`-ed below print legibility or the geometry hacked. A reviewer who cannot read an axis label rejects the figure; migrate a full table or extra convergence curves instead.
- **Declaring the build clean with unresolved undefined refs.** A single pdflatex pass hides citation/label problems that only surface after bibtex + two more passes. Always run the full sequence (8.5.a/b) and grep the *final* log (8.5.c). "Rerun to get cross-references right." in the last pass means you are not done.
- **A bib key added but never cited — or a `\cite` with no entry.** Both are C1 violations. Do not "fix" an unused key by deleting it casually: it must stay mirrored with `reference_papers/references.bib` (Phase 0.4), so removal needs P1 sign-off and a re-mirror. Do not "fix" an undefined cite by inventing an entry — the universe is frozen at 57 (Appendix A); rewrite the sentence to rest on evidence you have (Part 0.3).
- **Citing a key outside its sanctioned role to make "unused" go to zero.** Part 8 assigns each of the 57 keys a specific use. Padding a sentence with a decorative citation to clear the "unused" set is malpractice — R1 catches semantic mis-citation. If a key genuinely has no honest home, that is a scope question for P1, not a compliance hack.
- **Claiming reproducibility without the sentinel or commit.** An appendix that says "runs are reproducible" but omits the `8bda40d8…` FP sentinel, the exact `get_cec_seed(20240620, dim, func, run) % 2147483646 + 1` formula, or the commit SHA fails 8.4. Worse: quoting a sentinel that does not match the `environment.json` used for the reported cells is a fabrication. The three must agree with the committed evidence.
- **Trusting a table because it compiled.** LaTeX will happily typeset a stale number. 8.3 exists precisely because `T*.tex` bodies are frozen fragments with numbers baked in — a clean build says nothing about whether a cell still matches its CSV. Always run the binding audit.
- **Skipping the ruff/pytest/profile-lock gates because "the paper is done".** The manuscript makes claims about the software (a byte-identity-locked ISM core, a green suite). If 8.6 is red, those claims are false at the compliance SHA. The green gates are part of the definition of done, not a separate concern.
- **Running Phase 8 on a dirty tree.** Uncommitted changes under `results/`/`benchmarks/`/`optimizers/`/`src/`/`papers/` void the number-binding and reproducibility evidence. Reconcile first (Prerequisites).
- **Editing anything under `benchmarks/cec_reference_results/`.** These comparator CSVs are READ-ONLY and SHA-256-auditable. 8.3 reads them; it never writes them.
- **Inventing paths, scripts, or tables `T17`–`T20`.** Only the scripts and files enumerated here exist (`scripts/validate_profile_lock.py`, `scripts/build_docs_html.py`, `scripts/plot_convergence_from_curves.py`, `scripts/run_ablation.py`, `papers/scripts/generate_ablation_matrix.py`, `papers/scripts/generate_latex_tables.py`, the `papers/scripts/generate_*_convergence.py` generators, `src/gsk_family/analysis/{latex_tables,figures}.py`, tables `T01`–`T16`, `T16_bca`, `T21`, `T22`, plus any `ablation_<tag>.tex` fragments). Do not reference a runner, table, or path not on this list.

---

## Exit gate

Do not hand off to Phase 9 until **every** box is checked and the named evidence artifact exists. This mirrors Part 10; each item maps to a task above.

- [ ] **C1 — Citations closed.** `_cite_check.py` prints empty undefined / unused / out-of-universe; bib count = 57; mirrors `reference_papers/references.bib`; build logs show zero undefined citations. — *evidence:* 8.2 cross-check stdout + empty `.blg`/`.log` greps.
- [ ] **C2 — Numbers bound.** Every `papers/tables/T*.tex` and every referenced figure appears in `data_ledger.csv` with `source_path` + `commit_sha`; spot-audited cells/points/prose numbers match their generator output; ledger SHA = compliance SHA. — *evidence:* 8.3 completed `data_ledger.csv` + empty spot-audit diffs.
- [ ] **C3 — Within page budget.** Main-text page count (excl. references) ≤ ceiling (22 pp MDPI / 14 pp TEC), with no illegibly shrunk figure. — *evidence:* 8.1 recorded page count (+ migration diff if any).
- [ ] **C4 — Split honoured.** No conclusion-critical result lives only in the supplement; main carries the headline summary tables, the Nemenyi CD figure, the key ablation, and the honest limitations. — *evidence:* 8.1.c review note against C4/Part 6.6.
- [ ] **Reproducibility appendix complete.** FP sentinel (`8bda40d8…`) present in every CEC2017 `environment.json` and quoted verbatim in the supplement; seed formula stated exactly; commit SHA cited = compliance SHA. — *evidence:* 8.4 sentinel table + matched greps.
- [ ] **Build clean.** `papers/main.pdf` and `papers/supplementary.pdf` compile with no undefined refs, no missing figures, no margin-breaking overfull boxes. — *evidence:* 8.5 clean-log grep + the two PDFs.
- [ ] **Repo green.** `pytest -q`, `ruff check .`, `validate_profile_lock.py --root .`, `build_docs_html.py` all exit 0. — *evidence:* 8.6 pass output + exit codes.

Write the compliance evidence to `papers/build_prompt_phases/PHASE_8_compliance_report.md`: the page count, the `_cite_check.py` output, the number-binding ledger reference + spot-audit diffs, the sentinel/seed/SHA confirmations, the clean build-log greps, and the four green-gate results — one row per Part 10 clause with its evidence artifact. Confirm `papers/main.pdf` and `papers/supplementary.pdf` are the freshly built, clean PDFs.

---

## Hand-off

Phase 8 passes the following to **`papers/build_prompt_phases/PHASE_9_submission.md`**:

1. **`papers/main.pdf` + `papers/supplementary.pdf`** — the clean, compliant compiled artifacts (the exact files Phase 9 packages for upload).
2. **`PHASE_8_compliance_report.md`** — the Part 10 checklist with an evidence artifact per clause (page count, citation cross-check, binding ledger, sentinel/seed/SHA, clean logs, green gates). Phase 9 draws on this for the data/code-availability and reproducibility statements.
3. **The compliance SHA** — the commit every "reproducible from" claim, the cover letter's originality/reproducibility statement, and the availability statement will cite.
4. **`data_ledger.csv` (binding-complete)** — the provenance backbone for Phase 9's reproducibility statement pointing at committed artifacts.

Phase 9 consumes these to finalize `papers/cover_letter.tex`, assemble author/affiliation/ORCID/keywords/highlights, write the reproducibility + data/code-availability statements against the compliance SHA, and package the submission folder — asserting that nothing referenced in the package is absent from it.
