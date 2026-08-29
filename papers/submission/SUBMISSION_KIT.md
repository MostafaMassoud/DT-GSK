# SuSy submission kit — everything pasteable, in portal order

Regenerated 2026-08-29 from the pass-52 / v2.25 REVISION-1 sources (the
round-one response to algorithms-4507562). Every value below is copied from
the shipped manuscript; do not retype from memory — copy from here so the
form matches the paper exactly (D16.5).

---

## 1. Journal / type

- Journal: **Algorithms**
- Article type: **Article**
- Section / Special Issue: none (regular submission) unless you have an invite

## 2. Title (paste exactly)

DT-GSK: Dimension-Tiered Adaptive Configuration Selection and Deterministic Refinement for Gaining-Sharing Knowledge Optimization

## 3. Abstract (plain-text version of the shipped abstract)

Published gaining-sharing knowledge (GSK) variants adapt scalar control
and donor/selection policy to a single operating point. Dimension-Tiered
GSK (DT-GSK) resolves control by dimension: an adaptive scaffold serves
every tier, a deterministic, budget-exact final refinement runs once at
D >= 50, with the GSK vector-update equations retained; an exploratory
interaction-structure memory, learned from accepted moves, supplies its
basis. Against six GSK-family baselines re-executed on five CEC suites
under one budget-fair paired protocol, DT-GSK attains the best
descriptive family-rank aggregate on CEC2017 (2.48) and CEC2013 (2.80),
though the Holm-corrected tests separate it from eGSK only at CEC2017's
D = 10; it is second behind eGSK at D = 30 and on CEC2011 (a
Holm-significant loss). On AGSK's strongest suite—the CEC2020
competition in which it was the runner-up—DT-GSK places fourth; the
family panel corroborates AGSK's published strength in this regime,
consistent with the tiering thesis: every dimension-gated DT-GSK
subsystem is inactive at D <= 20. On CEC2013LSGO the comparison is
family-internal: tied-first descriptive rank; paired tests do not
separate DT-GSK from AGSK. Suite roles: CEC2017 selection-exposed;
CEC2011 and CEC2013 corroborative; CEC2020 pre-registered confirmatory;
CEC2013LSGO post-hoc. Direct isolations find no standalone benefit from
that memory; its basis is outperformed by coordinate axes—controlled
negative results. All findings are scoped to the GSK-family panel.

(If the abstract above ever disagrees with papers/DT-GSK.pdf, the PDF wins —
re-copy from it.)

## 4. Keywords (paste as-is; semicolon-separated)

metaheuristic optimization; gaining-sharing knowledge; dimension-tiered
adaptive configuration selection; deterministic final refinement; adaptive
operator selection; population-size reduction; CEC benchmark suites;
nonparametric statistical comparison; reproducibility

## 5. Authors (enter in this order; affiliation identical for all three)

Affiliation (all): Operations Research Department, Faculty of Graduate Studies
for Statistical Research, Cairo University, Giza 12613, Egypt

| # | Name | Email | ORCID | Role |
|---|---|---|---|---|
| 1 | Mostafa Elsayed Masoud | moustafa.masoud@gmail.com | 0009-0003-8415-2158 | **Corresponding** |
| 2 | Heba Sayed Mohamed Roshdy | hmhmdss@yahoo.com | 0000-0003-0387-5876 | Co-author |
| 3 | Ali Wagdy Mohamed | aliwagdy@gmail.com | 0000-0002-5895-2632 | Co-author |

## 6. Files to upload (this order)

This is a **LaTeX submission** (author decision, 2026-08-01): the PDF is the
canonical rendering and the source ZIP recompiles byte-identical to it. The
DOCX files are NOT uploaded — they are pandoc-built companions whose layout
legitimately differs from the PDF (the parity gate proves semantic equality,
not visual identity). If the editorial office requests an editable file later
in production, `papers/DT-GSK.docx` exists and validates.

| Upload slot | File |
|---|---|
| Manuscript (LaTeX source) | `papers/submission/DT-GSK-latex-source.zip` |
| Manuscript PDF | `papers/DT-GSK.pdf` |
| Figures | `papers/submission/DT-GSK-figures-600dpi.zip` |
| Supplementary Materials | `papers/supplementary.pdf` |
| Cover letter | paste text from `papers/cover_letter.md`, or upload `papers/cover_letter.pdf` |
| **Response to reviewers** | `papers/submission/response_to_reviewers.pdf` — staged beside the other upload artifacts, pinned untracked like them because it quotes both reports (D-0049) — rendered from `papers/review_2026_08_24/response_to_reviewers.md`, which is on disk but withheld from the repository because it quotes both reports (D-0049). Upload the PDF, or paste the Markdown point-by-point into the form. **A current render exists: 15 pages, revised 2026-08-29 from the pass-52 / v2.25 source, with the seven-lens panel-review fixes applied** (per-point template with Status outcomes, calmer wording per the external letter review, closure table with Status column, E4/E5 summary table, A12 and W/T/L defined, dagger contrasts unadjusted, reproducibility section compressed to DAS-anchored form with no internal release identifiers or repository filenames (companion-PDF names and latexdiff kept deliberately), 93-passage count included), via `SOURCE_DATE_EPOCH=1788220800 pandoc papers/review_2026_08_24/response_to_reviewers.md -o papers/submission/response_to_reviewers.pdf --pdf-engine=xelatex --include-in-header=papers/review_2026_08_24/response_letter_style.tex -V mainfont=Cambria -V "mainfontoptions=Ligatures=NoCommon" -V monofont=Consolas -V "monofontoptions=HyphenChar=None" -V fontsize=11pt -V geometry:margin=2.4cm -V colorlinks=true` (`HyphenChar=None` keeps hyphens out of code identifiers) (the style header, beside the source and likewise withheld, uses tcolorbox for the reviewer-quote boxes; mdframed is NOT installed here). `Ligatures=NoCommon` is load-bearing: with Cambria ligatures on, xelatex emits a ToUnicode map that copy-pastes every fi/fl word as broken text ("signi icant"). If any later pass edits the source, re-render with the same command. |
| **Revised manuscript, changes marked** | `DT-GSK-changes-marked.pdf` — a **latexdiff marked-up manuscript**: additions underlined, deletions struck through, in place, which is literally what item (II) asks for. Build it at resubmission with `python papers/scripts/build_change_marked_pdf.py` (diffs `v2.13` against the tag being submitted; derived, gitignored, do not commit). **The note previously here — that `latexdiff` is unusable because MiKTeX ships only a Perl shim — was half right and is superseded.** Plain `latexdiff` does fail, on a missing `Algorithm::Diff`; the standalone variant **`latexdiff-so` bundles it and works**. `ulem` is also required. Two caveats to state, not to hide: **preamble changes do not render** — the retitle is emitted as a `%DIF` comment, so the title change is invisible in the PDF and must be pointed out in the cover letter — and the main diff covers `main.tex` and its sections — a marked-up Supplementary (`DT-GSK-supplementary-changes-marked.pdf`, 80 pp) is available from the same script with `--doc supplementary` if the editors want the S-changes in place too. `DT-GSK-change-register.pdf`, the tabulated passage-by-passage register, is the companion: build it with `python papers/scripts/build_change_register.py` (93 passages over the same 7 files at v2.25 — but read the live count off the register's own front page; each given as submitted and as revised, with the reviewer point it answers). Its attribution column is keyword-derived and says so on its own front page; a passage answering two points is listed under both, so the column sums to more than the passage count. Do not quote a fixed passage or page count for it — the count has grown at every pass (54 at pass-41, 75 at v2.21, 93 at v2.25); read it off the register's front page at build time. |
| ~~Word files~~ | skip — LaTeX submission |

## 7. Cover letter (textbox)

Paste the body of `papers/cover_letter.md` (it is the plain-text twin of the
PDF and already carries the correct GenAI sentence naming both tools).

## 8. Generative-AI declaration (paste exactly; names BOTH tools, no ChatGPT version)

During the preparation and revision of this manuscript, the authors used two
generative-AI assistants: Claude (Opus 4.6, 4.8 and 5.0; Anthropic) and
ChatGPT (OpenAI). They assisted with language editing and rephrasing; the
drafting of expository prose that restates and explains findings the authors
had already established; structural review, consistency checking, and review
of the statistical and methodological descriptions; and software-engineering
support during implementation and tooling work. The algorithm design and the
experimental protocol are the authors' own, and every reported number was
produced by the authors' deterministic analysis pipeline: no AI system
designed an experiment, produced data, computed a statistic, or generated a
scientific claim, result, or conclusion, and no AI system is an author of this
work. The authors reviewed, verified and edited all AI-assisted content and
take full responsibility for the content of this publication.

Do NOT add "5.5/5.6" here: the manuscript deliberately states no ChatGPT
version (D-0036), and the form must match the manuscript.

## 8b. Code/data availability field (if the form asks for a URL)

Paste: https://github.com/MostafaMassoud/DT-GSK
The originally submitted version corresponds to repository tag v2.13 and
this revised version to tag v2.25 — matching the manuscript's own Data
Availability Statement exactly. No Zenodo/DOI for the repository; the
article DOI is assigned by the journal (D-0044).

## 9. Conflicts of interest (if the form asks separately)

State what the manuscript states: A.W.M. is the originator of the baseline GSK
algorithm and a co-author of several comparator variants; one comparator
(eGSK) is also co-authored by H.S.M.R. These relationships are declared in the
manuscript's Conflicts of Interest statement.

## 10. Suggested reviewers — THREE, author-selected (DO NOT auto-generate)

Rules (from the live Instructions, retrieved 2026-08-01): no collaborator or
co-publisher with any author within the last three years; no one at any
author's institution; three different institutions; institutional email
addresses. Your COI structure additionally rules out every GSK-family
comparator author.

| # | Name | Institution | Institutional email | Why qualified |
|---|---|---|---|---|
| 1 | (author to fill) | | | |
| 2 | (author to fill) | | | |
| 3 | (author to fill) | | | |

Candidate pools to draw from, per the cover-letter comment: authors in
evolutionary computation / metaheuristics benchmarking who are NOT in the GSK
lineage — e.g., researchers publishing on CEC benchmark methodology,
nonparametric comparison of metaheuristics, or adjacent DE/PSO families.

## 11. Form checkboxes you will meet

- APC acknowledgment: the current APC is shown on the journal page; the form
  asks you to acknowledge it (invoiced only on acceptance).
- Originality / not under consideration elsewhere: TRUE (state as the cover
  letter does).
- All authors approved submission: confirm with your co-authors BEFORE
  pressing submit.
- English editing: optional; decline or accept at your discretion.

## 12. After pressing Submit

1. The manuscript ID is already known: **algorithms-4507562**. A revision keeps
   it; there is no new ID to record.
2. Do NOT rebuild anything in the repo afterwards. The five uploaded files are
   hash-recorded in `submission_package_manifest.json` at **v2.25**, and that
   record is what makes the submitted bytes checkable. Freeze pass-52 and tag
   v2.25 are the frozen state of this resubmission, exactly as pass-38 / v2.13
   is the frozen state of the original.
3. If a SECOND revision is requested, it becomes pass-53 through change
   control: a new freeze pass and a new superseding tag, never an edit to
   v2.25 in place (D-0045).
4. Two of the uploaded artifacts — the response letter and the change register —
   are deliberately not in the repository (D-0049). They are regenerable: the
   response letter from its Markdown source on disk, the register from
   `git diff v2.13 v2.25` over the manuscript sources.
