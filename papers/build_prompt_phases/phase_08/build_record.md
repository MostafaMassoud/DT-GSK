# Phase 8 — Assembly, Compile & Page-Count Record

Date: 2026-07-11. Agent: Phase 8 assembly/compile agent.
Binding budget: `papers/build_prompt_phases/phase_04/page_budget.md`
(B1 target 28–34 typeset pages main text INCLUDING exhibits, EXCLUDING
references and back matter; hard cap 34).

## 1. Commands

All commands run in `D:/AI/PhD-Projects/00-GSK-Family/02-GSK_Family_Python_v1.1/papers/`
with MiKTeX (`latexmk`, `pdflatex`, `bibtex` from
`C:/Program Files/MiKTeX/miktex/bin/x64/`):

```
latexmk -C main.tex                                        # clean
latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
latexmk -C supplementary.tex                               # clean
latexmk -pdf -interaction=nonstopmode -halt-on-error supplementary.tex
```

latexmk drove pdflatex + bibtex to fixpoint for the main document. For
the supplement's final verification rebuild, a transient Windows file
lock on `supplementary.pdf` crashed one pdflatex pass mid-run
("I can't write on file"), which left a truncated .aux and hence an
EMPTY regenerated .bbl ("Something's wrong--perhaps a missing \item"
on the next pass). Recovery: delete `supplementary.{bbl,aux,out}` and
run the manual chain `pdflatex; bibtex supplementary; pdflatex x2` —
reproduced the identical 32-page/889,611-byte PDF. Not a source
defect; noted in case a future CI build hits the same lock. No missing packages: every package
used (`amssymb`, `algorithm`/`algpseudocode`, `algorithm2e` [supplement],
`bm`, `longtable`, `siunitx`, `subcaption`, `pgfplots`, `rotating`) was
already present in the MiKTeX installation; no packages were added to
either preamble by this phase.

## 2. Assembly state verified (no main.tex restructuring required)

`main.tex` already carried the Phase 8 title/abstract/back-matter rewrite
and inputs the five rewritten sections in outline order
(introduction, related_work, proposed_algorithm, performance,
conclusions); `\bibliography{references}` confirmed. Verified against
`papers/governance/artifact_binding.csv` (scope column):

- All 21 main-scope artifacts are included exactly once in the main
  document tree: T01/T15/T16 table includes; the four phase_03 method
  artifacts (`notation_table.tex`, `equations.tex`,
  `algorithm_pseudocode.tex`, `parameter_table.tex`) input from
  `build_prompt_phases/phase_03/` at their Section 3 positions; the 14
  main-scope figures via `\includegraphics` of `papers/figures/*.pdf`.
- All supplement-scope artifacts (T02–T14, T16_bca, 19 convergence
  grids, FIG-NLPSR) are included in `supplementary.tex` only (after fix
  2 below).
- Stale `papers/tables/T21.tex` / `T22.tex` are not referenced anywhere
  (per phase_07/table_dispositions.md they must not be).
- Supplement S6 remains an internal comment placeholder only
  (`% PHASE_12_PLACEHOLDER - DO NOT RELEASE`); no ablation content in
  either document.

## 3. Fixes applied

1. **Multiply-defined label `tab:panel`** (compile warning). Two panel
   roster floats existed: `sections/proposed_algorithm.tex` (§3.7) and
   `sections/performance.tex` (§4.1). The outline
   (`phase_04/outline.md`, Section 3 exhibit list, X5 = `T-PANEL`)
   binds the roster to Section 3; §4.1's exhibit is T07 only. Removed
   the §4.1 duplicate float; §4.1 prose reference
   `Table~\ref{tab:panel}` now resolves to the §3.7 float. Information
   audit of the removed copy: the APGSK per-run-gap note is retained in
   §4.1 prose (mandated disclosure, negative_findings item 8); the
   FDB-AGSK "(Case-1)" mechanism detail is retained in §2
   (`related_work.tex`, EC:fdbagsk2023-bound). Not re-added to the kept
   table because the kept table's evidence bind
   (comparability_audit.md) does not carry "Case-1".
2. **TAB-T16-BCA scope conflict** (registry conflict, resolved to the
   binding CSV). `artifact_binding.csv` and `exhibit_plan.csv` (row
   T-BCA) both mark `tab:bca-ci` supplement-scope, but
   `performance.tex` typeset the float in §4.2.3 (and the supplement
   carried a second, richer copy). Action: removed the main-text float;
   §4.2.3 keeps the numeric BCa-CI summary prose (values verified
   against `papers/tables/T16_bca.tex`) now pointing to Supplementary
   Material Section S2, where the full table with the registered
   caption and the r01/r04 + Nemenyi disclosures is typeset. This has
   the same shape as page-budget valve step 4 ("BCa summary replaced by
   a 3–4-line summary") but was motivated by scope compliance, not by
   the budget (B1 was already ≤ 34 before the change). NOTE for
   Phase 9: page_budget.md §4 lists a BCa/effect-size summary as a main
   exhibit (plan T03) while both machine registries say supplement for
   T-BCA; reconcile the registries (see also the binding CSV's own
   word_sources/T16_bca.json identity note).
3. **Egregious overfull hbox, 125.85pt** in the frozen
   `phase_03/parameter_table.tex` rendering (natural tabular width
   ~570pt vs 443.86pt text width). The phase_03 artifact is frozen and
   was NOT edited. Presentation-only fix at the inclusion site
   (`proposed_algorithm.tex`): a scoped group re-wraps the artifact's
   single `tabular` in an `lrbox` and emits it through
   `\resizebox{\textwidth}{!}` (graphicx is loaded by the MDPI class;
   no new package). Content bytes of the artifact unchanged. Effective
   font scale ≈ 0.78 of `\small` — flagged for Phase 9 to re-flow the
   table properly (e.g. via a change request to the frozen rendering or
   the MDPI fullwidth environment).
4. **APGSK citation-key error** (consequence-check of fix 1). The kept
   §3.7 panel table and one §3.3.1 sentence cited APGSK as
   `mohamed2021novel`, which per `governance/citation_role_map.csv` is
   a SHADE/LSHADE mutation paper (role B.2), not APGSK; the APGSK
   origin key is `apgsk2021` (role B.1, "exact settings for
   reproduction"). Both occurrences corrected to `\cite{apgsk2021}`.
   `mohamed2021novel` is now uncited in the main document (allowed;
   only ~40 of 57 admissible keys are cited).
5. **24 overfull vboxes in the supplement** (27.0–66.2pt too high,
   pages 10–21): the S3 full-page convergence grids at
   `width=\textwidth` plus captions exceeded `\textheight`,
   overprinting the bottom margin. Mechanical presentation fix in
   `supplementary.tex`: all 19 convergence `\includegraphics` calls now
   use `[width=\textwidth,height=0.87\textheight,keepaspectratio]`
   (no-op for grids that already fit). Zero overfull boxes of any kind
   remain in the supplement log.
6. **Four `[t]` table floats deferred past the references** (latent
   defect present in every earlier build of this manuscript, discovered
   by post-compile exhibit-placement audit): the notation table
   (frozen phase_03 rendering), the worked-example table, the parameter
   table (frozen phase_03 rendering), and the panel table — the only
   four `[t]`-spec tables in the build — could not satisfy top
   placement (the near-full-page notation table can never fit
   `\topfraction`, and it blocked the `[t]` queue behind it), so LaTeX
   flushed all four onto float pages AFTER the reference list
   (pp. 32–34), outside the running text. Fix, consistent with the
   build's own convention (every other table and figure in both
   documents uses `[H]`): the two floats owned by
   `proposed_algorithm.tex` were changed `[t]` → `[H]` directly; the
   two frozen phase_03 artifacts get a scoped
   `\renewenvironment{table}[1][t]{...[H]}{...}` override at their
   `\input` sites (artifact bytes untouched). After the fix the four
   tables typeset inline at their Section 3 positions
   (tab:notation p. 8, tab:worked-example p. 13, tab:parameters p. 16,
   tab:panel p. 17) and the document ends with the references.
   The supplement was audited for the same defect: all of its 14
   tables and 20 figures already use `[H]`; none deferred.

## 4. Final page counts (log lines verbatim)

```
main.log:          Output written on main.pdf (34 pages, 921155 bytes).
supplementary.log: Output written on supplementary.pdf (32 pages, 889611 bytes).
```

Page-budget measurement (B1 scope = main text incl. exhibits, excl.
references and back matter), measured from the compiled PDF AFTER the
deferred-float fix (fix 6) — i.e., with every main-text exhibit
actually inside the main text:

| Boundary | Page |
|---|---|
| Section 5 (Conclusions) starts | p. 30 |
| Conclusions final paragraph ends / back matter begins | p. 31 |
| References begin | p. 32 |
| Document ends (references) | p. 34 |

- **B1 = 31 pages** (pp. 1–31; p. 31 shared with back-matter start) →
  inside the 28–34 target band, **≤ 34 hard cap. PASS.**
- Total typeset main document: **34 pages** (back matter +
  abbreviations pp. 31–32, references pp. 32–34 — excluded from B1).
- Supplement: **32 pages** (separate document; no cap recorded).
- Measurement honesty note: before fix 6 the build *appeared* to have
  B1 = 28 only because four Section 3 tables (~3 pages of exhibits)
  had been silently flushed after the references; B1 = 31 is the true
  figure with all exhibits in place. Total page count is 34 in both
  states.
- B2/B3 word-level measurement is the Phase 9 cross-format check per
  page_budget.md §7–8; outline word budgets were enforced at drafting.

## 5. Overflow-valve steps applied

**None required by the budget.** B1 never exceeded 34 at any point in
this phase (final, true measurement: B1 = 31 within a 34-page total).
The Section-6 valve order of page_budget.md was therefore not invoked.
(Fix 2 above coincides in shape with valve step 4 but was a
scope-compliance action, recorded as such.)

## 6. Remaining warnings (accepted for Phase 8)

main.log:
- 5x `hyperref Warning: Token not allowed in a PDF string` — math
  (`$D \ge 100$`-style) in section headings reduced to plain text in
  PDF bookmarks; cosmetic.
- 3 overfull hboxes, all inside the §2 T-FAMREV table cells,
  max 17.5pt (unhyphenatable algorithm names "ATMALS-GSK [ref]",
  "FDB-AGSK [ref]" protruding within their p-columns) — below the
  "egregious" bar; left for Phase 9 polish (column-width retune).
- Assorted underfull hboxes in narrow table columns and the frozen
  pseudocode (badness warnings only); no action.
- `Label(s) may have changed` never appeared in the final run; aux
  stable.

supplementary.log:
- 2x hyperref PDF-string warnings (as above); zero overfull h/v boxes;
  zero undefined or multiply-defined references.

Citations: bibtex resolved every `\cite` in both documents (40 keys in
main, 8 in supplement; all from allowed_citation_keys.txt); no missing
citation warnings in either .blg.

## 7. Items handed to Phase 9

1. Reconcile T-BCA scope across page_budget.md §4 vs
   exhibit_plan.csv/artifact_binding.csv (fix 2), and the
   word_sources/T16_bca.json identity note (already flagged in the
   binding CSV).
2. Re-flow the frozen parameter-table rendering at readable font size
   (fix 3's `\resizebox` is a Phase 8 presentation stopgap).
3. T-FAMREV column widths (17.5pt protrusion).
4. `latex_location` column of artifact_binding.csv still says
   `pending-phase8-rewire` for rows now wired via the section files;
   update the register to the actual locations.
5. Citation-consistency sweep: `apgsk2021` vs `mohamed2021novel` usage
   was corrected in `proposed_algorithm.tex` only; the non-included
   legacy files (`literature_review.tex`, `supplementary_content.tex`)
   still carry old keys (they are not part of either compiled
   document).
6. The frozen phase_03 renderings (`notation_table.tex`,
   `parameter_table.tex`) still declare `[t]` internally; the scoped
   `[H]` overrides (fix 6) live at the `\input` sites in
   `proposed_algorithm.tex`. If Phase 9 re-issues the frozen renderings
   via change request, set `[H]` at the source and drop the overrides.

## 8. Compile log tails

### main.log (final run)

```
Output written on main.pdf (34 pages, 921155 bytes).
```
(final fixpoint confirmed: repeat `latexmk` reports
"All targets (main.pdf) are up-to-date"; exhibit placements verified
from main.aux: tab:notation p8, alg:dt-gsk p10, tab:worked-example
p13, tab:parameters p16, tab:panel p17.)

latexmk summary: "Found bibliography file(s): ./references.bib";
final run reported no problematic refs/citations and
"All targets (main.pdf) are up-to-date".

### supplementary.log (final run)

```
Output written on supplementary.pdf (32 pages, 889611 bytes).
PDF statistics:
 1608 PDF objects out of 1728 (max. 8388607)
 91 named destinations out of 1000 (max. 500000)
 104694 words of extra memory for PDF output out of 106986 (max. 10000000)
```

latexmk summary: "Found bibliography file(s): ./references.bib"; no
problematic refs/citations; "All targets (supplementary.pdf) are
up-to-date".

## 9. Gate 8 adversarial QA addendum (2026-07-11)

1. **Fixed (title mismatch):** `supplementary.tex` `\Title` still carried
   the stale pre-Phase-8 title "An **Adaptive** Interaction-Structure
   Memory ..." while `main.tex` froze "An Interaction-Structure Memory
   ...". Supplement title aligned to the main title and the supplement
   recompiled to fixpoint: `Output written on supplementary.pdf
   (32 pages, 889552 bytes)` — page count unchanged (byte size differs
   from Section 4's verbatim log because of the rebuild). The same stale
   title also survives in non-compiled legacy files
   (`cover_letter.md/.tex`, `build_prompt_phases/PHASE_9_submission.md`)
   — cover-letter handling stays under R-0004 (Phase 9/11).
2. **Finding (MAJOR, not fixed here — substance):** the `main.tex`
   abstract measures **222 words** against the Phase-8 hard constraint
   of <= 200 (comment in `main.tex` says "~200 words"). Content is
   otherwise compliant (one bound number 2.48-of-7; D30 #2, CEC2011
   Holm-significant loss to eGSK, and Nemenyi non-separability all
   disclosed; panel scoping present; no citations; no ablation). Needs a
   ~25-word trim by the drafting owner; do NOT drop the bound number or
   the three disclosures.
3. **Finding (minor):** `sections/related_work.tex` (§2.1, "Hybrid and
   operator-export lines...") attributes "junior/senior operators"
   transplantation to both `zhong2021gskhho` (correct) and
   `liang2024gskwoa` (card sanctions the **junior-phase operator only**
   for the WOA host). Suggested wording: "...transplant the
   junior/senior operators into DE~\cite{zhong2021gskhho}, and the
   junior-phase operator into a whale-optimization
   host~\cite{liang2024gskwoa}".
4. **Note (AG-0007):** the methods-level GenAI-use description is
   implemented as a dedicated back-matter block plus the Acknowledgments
   tool/version statement (per the register's Phase-8 plan); the paper
   has no "Materials and Methods"-titled section. Phase 9 should confirm
   MDPI accepts the back-matter placement or fold one sentence into
   Section 4.1.
5. QA verification summary: 20+ scientific paragraphs traced to claim
   rows/analysis ids; 20+ citation sites checked against evidence-card
   sanctioned uses (one minor issue, item 3); 40+ typed numbers
   re-verified against `papers/analysis/rel-2026-07-10-262fc16c9/` CSVs
   and `papers/tables/T*.tex` (0 mismatches); all 7 mandated negative
   disclosures present in prose alongside the favorable cells; 0
   ablation content in released text (S6 comment placeholder intact);
   page budget B1 = 31 <= 34 re-confirmed from the compiled PDFs.
