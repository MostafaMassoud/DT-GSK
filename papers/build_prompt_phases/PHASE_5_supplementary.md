# PHASE 5 — Supplementary Assembly

> **⚑ Revision 2 addendum applies to this phase.** Before executing, read [ADDENDUM_R2_cec2013_and_ablation.md](ADDENDUM_R2_cec2013_and_ablation.md) §R2.C — a CEC2013 family panel and the CEC2017 scaffold ablation add tasks to this phase, and the addendum overrides this file where they disagree.

**Objective:** Assemble `papers/sections/supplementary_content.tex` into a complete,
standalone-compiling supplement that carries every full-detail exhibit and the
reproducibility appendix, cross-linked to the main text, with *no*
conclusion-critical result living only here.

> This file expands **Phase 5** of `papers/PAPER_BUILD_PROMPT.md`. It **follows**
> `PHASE_4_drafting.md` (the main-text draft must exist first) and **hands off to**
> `PHASE_6_prose_quality.md`. Do **not** edit the main manuscript in this phase;
> the only manuscript-adjacent files you touch are `papers/supplementary.tex` and
> `papers/sections/supplementary_content.tex`.

---

## Prerequisites

Before starting Phase 5, all of the following must be true:

1. **Main-text draft complete.** `PHASE_4_drafting.md` has produced a compiling
   `papers/main.tex` (or equivalent) whose Results/Discussion prose is stable
   enough that its "see Table S-x / Fig S-x" pointers are final. If the main text
   still churns, cross-links will drift — do not start 5.2 until pointers freeze.
2. **Phase 3 supplement-bound exhibits ready.** Every full table
   (`papers/tables/T01`–`T22`, plus `T16_bca`) and every figure under
   `papers/figures/{convergence,diagrams,flowchart,ranks,taxonomy,traces}/`
   that Phase 3 tagged as *supplement-bound* has been generated and committed.
3. **Stats bundle frozen (Phase 2).** The Friedman/Wilcoxon–Holm matrices, per-run
   summaries, and BCa intervals (`T16_bca`) are final; no re-tuning is in flight.
4. **Bib freeze respected.** The 57 locked keys (Appendix A of
   `papers/PAPER_BUILD_PROMPT.md`) are the *only* citations permitted. The single
   supplement-only exception is `david_order_statistics`, available **only** if you
   include the optional order-statistics proof sketch (Task 5.1.7).
5. **Repo is at a known commit.** Record the current commit SHA now; it anchors
   every headline number and is quoted verbatim in the Reproducibility Appendix.

---

## Inputs

| Input | Location / value | Used by |
|-------|------------------|---------|
| Full per-function tables (all `D`) | `papers/tables/T01`–`T22`, `papers/tables/T16_bca` | 5.1.1 |
| Pairwise Wilcoxon (Holm) matrices | Phase 2 stats bundle → `tables/…` (e.g. `tab:cec2011_wilcoxon`, `tab:cec2013_wilcoxon`) | 5.1.2 |
| All convergence curves | `papers/figures/convergence/` | 5.1.3 |
| Adaptive-parameter traces | `papers/figures/traces/` | 5.1.5 |
| Rank/diagram/taxonomy/flowchart figures | `papers/figures/{ranks,diagrams,taxonomy,flowchart}/` | 5.1.x |
| Full hyperparameter sweep grids | Phase 2/3 sweep exhibits (`T21`, `T22` parametric probe) | 5.1.4 |
| Extended ablations | Phase 2 ablation tables (`tab:substrate_ablation`, `tab:category_breakdown`, `tab:fdc_attribution`) | 5.1.6 |
| Reproducibility facts | see below | 5.1.8 |
| Assembly targets | `papers/supplementary.tex`, `papers/sections/supplementary_content.tex` | all |

**Reproducibility facts (verbatim — do not paraphrase the values):**

- **ISM core byte-identity locked.** Files:
  `src/gsk_family/optimizers/_dt_core.py`,
  `src/gsk_family/optimizers/_dt_subsystems/`,
  `src/gsk_family/optimizers/_dt_rng.py`,
  `src/gsk_family/optimizers/_dt_profiles.py`.
- **FP-regime sentinel** recorded in `environment.json`
  (per suite/optimizer, e.g.
  `benchmarks/cec_reference_results/cec2017/dt-gsk/environment.json`);
  the CEC2017 canonical prefix is **`8bda40d8…`**.
- **Seed formula:** `get_cec_seed(20240620, dim, func, run) % 2147483646 + 1`,
  defined in `src/gsk_family/runners/seed_policy.py` (function `get_cec_seed`,
  base seed `20240620`).
- **Run counts:** CEC2017 = **51**, CEC2011 = **25**, CEC2013 = **51**.
- **Dimensions:** `D ∈ {10, 30, 50, 100}` (CEC2017); `D ∈ {10, 30, 50}`
  (CEC2013, 28 functions); CEC2011 is problem-defined.
- **Commit SHA** anchors every headline number (record it in the appendix).
- **Four green gates:**
  1. `python -m pytest -q`
  2. `python -m ruff check .`
  3. `python scripts\validate_profile_lock.py --root .`
  4. `python scripts\build_docs_html.py`

---

## Tasks

Work top-to-bottom. Each micro-step lists the *edit target*, the *snippet*, and
the *verification command*. All commands run from the repo root
`D:\AI\PhD-Projects\00-GSK-Family\02-GSK_Family_Python_v1.1` unless noted.

### 5.1 Assemble `sections/supplementary_content.tex`

The file is `\input{}`-ed by `papers/supplementary.tex` at its line ~170
(`\input{sections/supplementary_content}`). It is a sequence of top-level
`\section{…}` blocks, each `\label`-ed. Preserve the existing section order; you
are *filling in / completing* content, not rewriting the scaffold.

Existing top-level sections already present (extend, do not duplicate):

- `\section{Complete Per-Function Result Tables}\label{ssec:tables}`
- `\section{Tuning Protocol Disclosure}\label{ssec:tuning}`
- `\section{Adaptive-Parameter Traces}\label{ssec:traces}`
- `\section{Ablations, Attribution, and Sensitivity}\label{ssec:ablation}`

You will add two new sections in this phase:

- `\section{Complete Pairwise Significance Matrices}\label{ssec:wilcoxon}`
  (if not already merged into `ssec:tables`)
- `\section{Reproducibility Appendix}\label{ssec:repro}`
- (optional) `\section{Proof Sketch: Order-Statistic Bound}\label{ssec:proof}`

#### 5.1.1 Full per-function result tables (all `D`)

For each suite × dimension, emit a `\begin{table}[H] … \input{tables/Txx} …`
block inside `ssec:tables`. Each table reports, per function, the five error
summaries over the run budget: **Best, Median, Worst, Mean, SD** (error =
`f(x) − f*`), with the better Mean in **bold** via `\bestval{…}`.

```latex
\begin{table}[H]
\caption{CEC~2017 $D = 50$: \ismgsk{} vs.\ GSK.  Best Mean per function in
bold; error $= f(x)-f^{*}$ over 51 runs.}\label{tab:h2h_d50}
\centering
\tablesize{\scriptsize}
\resizebox{\textwidth}{!}{\input{tables/T04}}
\end{table}
```

Checklist for this micro-step:

- CEC2017 head-to-head at `D ∈ {10,30,50,100}` → four tables
  (`tab:h2h_d10 … tab:h2h_d100`), 51-run stats.
- CEC2011 real-world table (`tab:cec2011`), 25-run stats.
- GSK-family comparison at all four `D` (`tab:gsk_d10 … tab:gsk_d100`).
- CEC2013 second comparison suite at `D ∈ {10,30,50}` (`tab:cec2013_d10 …
  tab:cec2013_d50`), 51-run stats, 28 functions, full 7-optimizer panel.
- Every table caption states the **run count** and that values are **error**, not
  raw fitness. Do not restate a headline number here — the table *is* the source;
  the main text references it (see 5.2 / pitfalls).

For a table too tall for one page, use `longtable` (already loaded in
`supplementary.tex`); see the Worked Example. Use `\tablesize{\scriptsize}` +
`\resizebox` for wide tables so the body never overflows `\textwidth`.

#### 5.1.2 Full pairwise Wilcoxon (Holm) matrices

Emit the *complete* symmetric win/tie/loss matrices (all algorithm pairs), with
Holm-corrected `p`-values, per suite. Encode outcomes with the existing macros:
`\wmark` (`+`, row beats column), `\lmark` (`−`, row loses), `\emark` (`≈`, tie).

```latex
\begin{table}[H]
\caption{CEC~2017 pairwise Wilcoxon signed-rank outcomes (Holm-corrected,
$\alpha = 0.05$).  Cell $(i,j)$: \wmark{}/\lmark{}/\emark{} = row $i$
beats/loses to/ties column $j$.}\label{tab:cec2017_wilcoxon_full}
\centering
\tablesize{\footnotesize}
\resizebox{\textwidth}{!}{\input{tables/T14}}
\end{table}
```

Include the matrices already scaffolded (`tab:cec2011_wilcoxon`,
`tab:cec2013_wilcoxon`) plus the full CEC2017 family matrix. State in each caption
the correction method (Holm) and `α`.

#### 5.1.3 All convergence curves

Include every convergence figure from `papers/figures/convergence/`. Group by
suite/dimension; use `subcaption` (loaded) for multi-panel plates.

```latex
\begin{figure}[H]
\centering
\includegraphics[width=\textwidth]{figures/convergence/cec2017_d50_grid.pdf}
\caption{CEC~2017 $D = 50$ median convergence, all 30 functions
(log-scale error vs.\ FEs).}\label{fig:conv_cec2017_d50}
\end{figure}
```

Cover CEC2017 all `D`, CEC2011 (the existing `fig:conv_cec2011{,_b,_c}` plates),
and CEC2013 at `D ∈ {10,30,50}` (grids via
`papers/scripts/generate_cec2013_convergence.py` — 28 functions, 4 subfigures
a–d). Do not omit any function; the *full* set is the whole point
of putting them here rather than in the main text.

#### 5.1.4 Full hyperparameter sweep grids

Emit the complete sweep grids (the parametric probe / layout-parallel pilot,
`T21`/`T22`, labels `tab:parametric_t21`, `tab:parametric_t22`) inside
`ssec:tuning`. State the swept ranges, the fixed budget, and that these are a
*pilot* (per the existing captions), not the headline configuration.

#### 5.1.5 Adaptive-parameter traces

Populate `ssec:traces` with the full trace figures from
`papers/figures/traces/`: junior/senior probability trace (`fig:ace_trace`),
accuracy–diversity trace (`fig:acc_div_trace`), and the all-parameters plate
mirroring the ATMALS-GSK layout (`fig:adaptive_params_all`).

#### 5.1.6 Extended ablations

Populate `ssec:ablation` with the full ablation set:

- Scaffold ablation, remove-one design — 6 mechanisms + baseline = 7 cells,
  n = 25, SGSM off in every cell — CEC2017 (`tab:substrate_ablation`; matrix
  `results/ablation/ablation_matrix_rank_summary_<suite>[_D<dim>].csv`, fragment
  `papers/tables/ablation_<tag>.tex`).
- SGSM-overlay ablation, CEC2013 hold-out design (`sec:exp:ablation:sgsm`).
- Per-category breakdown, CEC2017 `D=50` (`tab:category_breakdown`).
- Landscape attribution / FDC probe (`tab:fdc_attribution`).

Each ablation must state its design (cells), the suite/dimension, and the run
count so a reader can reproduce it. If an ablation's *direction* (which component
helps) is load-bearing for a main-text claim, the main text must state the
direction itself and merely reference the full grid here (see pitfalls).

#### 5.1.7 (Optional) Order-statistics proof sketch

If — and only if — the main text makes a claim that rests on an order-statistic
argument (e.g. a bound on the expected best-of-`n` error), add
`\section{Proof Sketch: Order-Statistic Bound}\label{ssec:proof}` and cite
`david_order_statistics` (the single supplement-only key). Keep it a *sketch*:
state the assumption, the lemma, and the one-paragraph derivation; do not import
new notation the main text never defined. If no such claim exists, **skip this
section entirely** and do not cite `david_order_statistics`.

#### 5.1.8 Reproducibility Appendix

Add `\section{Reproducibility Appendix}\label{ssec:repro}`. It must document, in
this order, each fact with the *exact* value/path:

1. **FP regime & sentinel.** The floating-point regime is pinned; the CEC2017
   canonical benchmark prefix is `8bda40d8…`, recorded per run in
   `environment.json` (e.g.
   `benchmarks/cec_reference_results/cec2017/dt-gsk/environment.json`). State
   that a mismatched sentinel invalidates the run and is caught at load time.
2. **Seed formula.** `get_cec_seed(20240620, dim, func, run) % 2147483646 + 1`,
   defined in `src/gsk_family/runners/seed_policy.py`. Give the base seed
   (`20240620`) and note the schedule is deterministic and per-`(dim,func,run)`.
3. **Run counts.** CEC2017 = 51, CEC2011 = 25, CEC2013 = 51;
   `D ∈ {10,30,50,100}` (CEC2017) and `D ∈ {10,30,50}` (CEC2013).
4. **Commit SHA.** Quote the SHA recorded in Prerequisites; state that it anchors
   every headline number.
5. **`environment.json`.** Describe what it captures (interpreter, key package
   versions, FP sentinel) and where it lives.
6. **ISM core byte-identity.** List the four locked artifacts
   (`_dt_core.py`, `_dt_subsystems/`, `_dt_rng.py`, `_dt_profiles.py`) and
   state that `validate_profile_lock.py` enforces byte-identity.
7. **Four green gates.** List the four commands verbatim (5.1.8 table below) and
   state that all four must pass on the anchored SHA.

```latex
\begin{table}[H]
\caption{Verification gates.  All four must pass on the anchoring commit.}
\label{tab:green_gates}
\centering
\begin{tabular}{ll}
\toprule
Gate & Command \\
\midrule
Unit + integration tests & \texttt{python -m pytest -q} \\
Lint & \texttt{python -m ruff check .} \\
Profile-lock (byte-identity) & \texttt{python scripts\textbackslash validate\_profile\_lock.py -{}-root .} \\
Docs build & \texttt{python scripts\textbackslash build\_docs\_html.py} \\
\bottomrule
\end{tabular}
\end{table}
```

Before writing the appendix, actually run the four gates and confirm green:

```powershell
python -m pytest -q
python -m ruff check .
python scripts\validate_profile_lock.py --root .
python scripts\build_docs_html.py
```

Capture the current SHA:

```powershell
git rev-parse HEAD
```

### 5.2 Cross-link main ↔ supplement

Every main-text pointer of the form "see Table S-x" / "Fig. S-x" must resolve to a
labelled float in the supplement, and every supplement float that the main text
references must carry the matching label.

**Labeling scheme.** The supplement uses an **`S`-numbered display** for its
floats so that main-text prose can say "Table S3" unambiguously. In
`papers/supplementary.tex` preamble (once, before `\begin{document}`), redefine
the counters:

```latex
\renewcommand{\thetable}{S\arabic{table}}
\renewcommand{\thefigure}{S\arabic{figure}}
\renewcommand{\theequation}{S\arabic{equation}}
```

Keep the existing *internal* `\label` keys (`tab:h2h_d50`, `fig:conv_cec2017_d50`,
`ssec:repro`, …) — they are stable identifiers. The `S`-prefix is a *display*
concern (what the reader sees), the `\label` key is the *internal* handle. Do not
rename existing keys; renaming breaks any `\cref`/`\ref` already written.

**How the main text points in.** Because the supplement compiles separately, the
main text cannot `\ref{}` a supplement label directly. Use one of:

- **Hard-coded display names** in main-text prose: "full per-function results
  appear in Table S3 (Supplementary Material)". This is the MDPI-idiomatic
  approach for separately-compiled supplements and is the default here.
- Maintain a **pointer manifest**: a short list (kept in the Phase 4 hand-off
  notes) mapping each main-text "Table S-x" to the supplement `\label` key, so the
  display number and the target stay in sync.

**How to check pointers resolve:**

1. Build the supplement (5.3) and read the log for `undefined references` /
   `multiply-defined labels`. Zero of each is required.

   ```powershell
   Select-String -Path papers\supplementary.log -Pattern "undefined|multiply.defined|LaTeX Warning: Reference"
   ```

2. Enumerate every "S-x" mention in the main text and confirm a matching numbered
   float exists in `supplementary.pdf`:

   ```powershell
   Select-String -Path papers\sections\*.tex,papers\main.tex -Pattern "(Table|Fig(ure|\.)?)~?\s*S-?\d+"
   ```

   For each hit, confirm the number exists in the compiled supplement. If the main
   text says "Table S7" but the supplement only reaches S6, the pointer is broken.

3. Confirm no *internal* supplement `\ref` is dangling by grepping the `.tex` for
   `\ref{`/`\cref{` keys and matching each to a `\label{`.

### 5.3 Ensure `supplementary.tex` compiles independently

`papers/supplementary.tex` is standalone: it declares its own MDPI class
(`\documentclass[algorithms,article,submit,moreauthors,pdftex]{Definitions/mdpi}`),
its own preamble (amssymb, algorithm2e, bm, longtable, siunitx, subcaption,
pgfplots, rotating, custom macros `\ismgsk`, `\bestval`, `\wmark`, …), `\input`s
`sections/supplementary_content`, then pulls its **own** bibliography via
`\input{supplementary.bbl}` before `\end{document}`.

**Build command (from `papers/`):**

```powershell
cd papers
pdflatex -interaction=nonstopmode supplementary.tex
bibtex supplementary
pdflatex -interaction=nonstopmode supplementary.tex
pdflatex -interaction=nonstopmode supplementary.tex
```

(If the project uses `latexmk`: `latexmk -pdf supplementary.tex`. If the `.bbl`
is generated by the main build and shared, regenerate it so supplement-only keys
resolve.)

**What a clean build looks like:**

- `supplementary.pdf` is produced.
- `supplementary.log` contains **no** `Undefined control sequence`, **no**
  `Undefined reference`, **no** `Citation … undefined`, **no**
  `multiply-defined`.
- Every `\input{tables/Txx}` and `\includegraphics{figures/…}` resolves (no
  "File not found").
- No `Overfull \hbox` wide enough to push a table past the page margin (use
  `\resizebox`/`longtable` to fix).
- Bibliography lists only keys from the 57-key lock (+ `david_order_statistics`
  iff the proof sketch is included).

Verify the citation set does not leak keys outside the lock:

```powershell
Select-String -Path papers\supplementary.tex,papers\sections\supplementary_content.tex -Pattern "\\cite[tp]?\{" -AllMatches
```

Cross-check each cited key against Appendix A of `papers/PAPER_BUILD_PROMPT.md`.

---

## Worked examples

### A. `longtable` skeleton for a full per-function table

Use when a per-function table is taller than one page (e.g. CEC2017's 30
functions with five statistics each). `longtable` is already loaded in
`supplementary.tex`.

```latex
\begin{footnotesize}
\begin{longtable}{@{}l S S S S S@{}}
\caption{CEC~2017 $D = 30$: \ismgsk{} per-function error statistics over 51
runs (error $= f(x)-f^{*}$).  Best Mean vs.\ GSK in bold.}\label{tab:h2h_d30}\\
\toprule
Func. & {Best} & {Median} & {Worst} & {Mean} & {SD} \\
\midrule
\endfirsthead
\multicolumn{6}{@{}l}{\itshape Table~\ref{tab:h2h_d30} continued}\\
\toprule
Func. & {Best} & {Median} & {Worst} & {Mean} & {SD} \\
\midrule
\endhead
\midrule
\multicolumn{6}{r@{}}{\itshape continued on next page}\\
\endfoot
\bottomrule
\endlastfoot
F1  & 0.00e+00 & 0.00e+00 & 0.00e+00 & \bestval{0.00e+00} & 0.00e+00 \\
F3  & 0.00e+00 & 1.13e-07 & 4.52e-05 & \bestval{2.10e-06} & 6.84e-06 \\
% … one row per function F1..F30 (F2 omitted per CEC2017 convention) …
F30 & 3.95e+02 & 5.94e+02 & 8.10e+02 & 5.88e+02 & 1.02e+02 \\
\end{longtable}
\end{footnotesize}
```

Notes: the `S` column type (siunitx) aligns on the exponent; declare it in the
preamble if not already present. Keep the caption's run count (`51`) truthful for
the suite. Prefer `\input{tables/Txx}` when the row body is machine-generated;
inline the skeleton only when hand-editing.

### B. Reproducibility-Appendix subsection skeleton

```latex
\section{Reproducibility Appendix}\label{ssec:repro}

\subsection{Numerical regime and benchmark sentinel}\label{repro:fp}
All CEC~2017 runs execute under a pinned floating-point regime.  Each run records
a benchmark-data sentinel in \texttt{environment.json}; the CEC~2017 canonical
prefix is \texttt{8bda40d8\ldots}.  A run whose sentinel does not match this
prefix is rejected at load time and excluded from every reported statistic.

\subsection{Seed schedule}\label{repro:seed}
Run seeds are fully determined by
\[
\texttt{seed}(d,f,r) \;=\; \texttt{get\_cec\_seed}(20240620,\,d,\,f,\,r)
\bmod 2147483646 \;+\; 1,
\]
implemented in \texttt{src/gsk\_family/runners/seed\_policy.py} (base seed
\texttt{20240620}).  Run counts are 51 (CEC~2017), 25 (CEC~2011), and 51
(CEC~2013), over $D \in \{10,30,50,100\}$ for CEC~2017 and
$D \in \{10,30,50\}$ for CEC~2013.

\subsection{Provenance anchor}\label{repro:sha}
Every headline number in the main text and this supplement was produced at
commit \texttt{<INSERT-40-CHAR-SHA>}.  The ISM core is byte-identity locked
(\texttt{\_ism\_core.py}, \texttt{\_ism\_subsystems/}, \texttt{\_ism\_rng.py},
\texttt{\_ism\_profiles.py}); \texttt{scripts\textbackslash validate\_profile\_lock.py}
enforces the lock.  The four verification gates
(Table~\ref{tab:green_gates}) all pass on this commit.
```

Replace `<INSERT-40-CHAR-SHA>` with the output of `git rev-parse HEAD` recorded in
Prerequisites — never a placeholder in the committed file.

### C. Cross-link pair (main `\ref` → supplement `\label`)

Main text (in a `papers/sections/*.tex` file — *authored in Phase 4, referenced,
not edited, here*):

```latex
% MAIN TEXT — display-name pointer into the separately-compiled supplement
Complete per-function error statistics for every dimension are reported in
Table~S3 of the Supplementary Material.
```

Supplement (`sections/supplementary_content.tex`), with `S`-numbered display via
the counter redefinition in 5.2:

```latex
% SUPPLEMENT — the target float; internal key stays `tab:h2h_d50`
\begin{table}[H]
\caption{CEC~2017 $D = 50$: \ismgsk{} vs.\ GSK per-function statistics
(51 runs).}\label{tab:h2h_d50}
\centering\tablesize{\scriptsize}
\resizebox{\textwidth}{!}{\input{tables/T04}}
\end{table}
```

The manifest entry recording this pair (kept with the Phase 4 hand-off notes):
`Table S3  →  tab:h2h_d50  (papers/tables/T04)`. If the supplement is later
reordered and this becomes the fourth table, update the main text to "Table S4"
and the manifest — the `\label` key does not change.

---

## Pitfalls & anti-patterns

- **Burying a conclusion-critical result in the supplement — FORBIDDEN.** The C4
  split rule (`papers/PAPER_BUILD_PROMPT.md`) is absolute: *nothing critical to the
  paper's conclusion may live only in the supplement.* If the abstract/conclusion
  claims "DT-GSK is family-best at D10/D50/D100," the *statistic that establishes
  that* must appear in the main text; the supplement may carry the full per-run
  detail, but not the load-bearing summary. Audit: for each conclusion sentence,
  confirm its supporting number is in the main text, not only in an `S-`table.
- **Broken cross-links.** "See Table S7" pointing at a supplement that stops at S6;
  a `\ref` to a `\label` that was renamed; a figure moved between plates so its
  display number shifts. Run the 5.2 checks after *every* reorder. Because the
  supplement compiles separately, a broken pointer will **not** raise a LaTeX error
  in the main build — it silently misdirects the reader. Only the manual "S-x"
  enumeration catches it.
- **Supplement that won't compile standalone.** Relying on a macro, package, or
  `.bbl` defined only in `main.tex`. `supplementary.tex` has its **own** preamble
  and its **own** `\input{supplementary.bbl}` — any macro the content needs
  (`\ismgsk`, `\bestval`, `\wmark`, `S` column type, pgfplots) must be declared in
  *its* preamble. Test by building `supplementary.tex` in isolation (5.3), not as
  part of the main build.
- **Duplicating (not referencing) main-text numbers.** Never retype a headline
  Mean/rank into supplement prose. Reference the main-text claim and let the
  supplement carry the *full source table*. Duplicated numbers drift the moment one
  side is re-run; a single source of truth per number is mandatory.
- **Citing outside the lock.** Any key not in the 57-key set (Appendix A) — except
  `david_order_statistics` used *solely* for the optional proof sketch — is a hard
  failure. A `Citation undefined` in `supplementary.log` usually means a key leaked
  in or the `.bbl` wasn't regenerated.
- **Wide tables overflowing the margin.** A per-function table without
  `\resizebox`/`longtable` produces an `Overfull \hbox` and clipped columns in the
  PDF. Always wrap wide tabulars.
- **Stale reproducibility facts.** A placeholder SHA, an old sentinel prefix, or a
  run count that doesn't match the suite (e.g. writing 51 for CEC2011, which is 25).
  Copy the values from this document / live commands, not from memory.

---

## Exit gate

Phase 5 is complete only when **all** hold:

1. `papers/supplementary.pdf` compiles clean — `supplementary.log` shows no
   undefined control sequence, undefined reference, undefined citation, or
   multiply-defined label; no missing file; no margin-breaking overfull box.
2. **All cross-links resolve** — every main-text "Table S-x / Fig. S-x" maps to an
   existing numbered float in the compiled supplement, and every internal
   `\ref`/`\cref` resolves (5.2 checks pass).
3. **No conclusion-critical result is supplement-only** — the C4 audit passes:
   each conclusion/abstract claim's supporting number lives in the main text.
4. **Reproducibility Appendix complete** — FP sentinel (`8bda40d8…`), seed formula
   (`get_cec_seed(20240620,dim,func,run)%2147483646+1`), run counts (51/25/51 for
   CEC2017/CEC2011/CEC2013), dimensions (`{10,30,50,100}` CEC2017; `{10,30,50}`
   CEC2013), commit SHA, `environment.json`, ISM byte-identity
   lock, and the four green gates are all documented with exact values.
5. Citations are within the 57-key lock (+ `david_order_statistics` iff the proof
   sketch is included).
6. The four green gates were re-run and passed on the anchoring commit:
   `python -m pytest -q`, `python -m ruff check .`,
   `python scripts\validate_profile_lock.py --root .`,
   `python scripts\build_docs_html.py`.

---

## Hand-off

Deliverables handed to **`PHASE_6_prose_quality.md`**:

- `papers/sections/supplementary_content.tex` — fully assembled, all sections
  populated, S-numbered.
- `papers/supplementary.pdf` — clean standalone build.
- The cross-link **pointer manifest** (Table/Fig S-x → `\label` key → source
  artifact), for Phase 6 to preserve while it edits prose.
- The recorded **commit SHA** and confirmation that the four gates are green.

Phase 6 is a prose-quality pass over both the main text and supplement. It must not
alter any `\label` key, table/figure number, or reproducibility value; if it
reorders content, it re-runs the 5.2 cross-link checks and updates the manifest.
