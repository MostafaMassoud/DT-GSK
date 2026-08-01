# SuSy submission kit — everything pasteable, in portal order

Generated 2026-08-01 from the frozen pass-37 / v2.12 sources. Every value below
is copied from the shipped manuscript; do not retype from memory — copy from
here so the form matches the paper exactly (D16.5).

---

## 1. Journal / type

- Journal: **Algorithms**
- Article type: **Article**
- Section / Special Issue: none (regular submission) unless you have an invite

## 2. Title (paste exactly)

DT-GSK: Dimension-Tiered Adaptive Control and Deterministic Refinement for Gaining-Sharing Knowledge Optimization

## 3. Abstract (plain-text version of the shipped abstract)

Published gaining-sharing knowledge (GSK) variants adapt scalar control and
donor/selection policy at one operating point. Dimension-Tiered Gaining-Sharing
Knowledge (DT-GSK) instead resolves control by dimension: an adaptive scaffold
serves every tier, a deterministic, budget-exact eigenframe refinement runs
once from D = 50 upward, and the GSK vector-update equations are retained; an
exploratory interaction-structure memory, learned from strictly improving
accepted moves at no extra evaluations, supplies the refinement basis. Against
six GSK-family baselines re-executed in-repository on CEC2017 (primary),
CEC2011, CEC2013, CEC2020, and CEC2013LSGO under one budget-fair paired
protocol, DT-GSK attains the best descriptive family-rank aggregate on CEC2017
(2.48) and CEC2013 (2.80); it is second behind eGSK at CEC2017's D = 30 and on
CEC2011; the CEC2011 loss is Holm-significant. On AGSK's strongest suite — the
CEC2020 competition in which it was the runner-up — DT-GSK places fourth; the
family panel corroborates AGSK's published strength in this regime, consistent
with the tiering thesis: every dimension-gated DT-GSK subsystem is inactive at
D <= 20. On CEC2013LSGO the comparison is family-internal: tied-first
descriptive rank; paired tests do not separate DT-GSK from AGSK. Suite roles:
CEC2017 selection-exposed; CEC2011 and CEC2013 corroborative; CEC2020
pre-registered confirmatory; CEC2013LSGO post-hoc. A direct isolation finds no
detectable standalone benefit from that memory — a controlled negative result.
All findings are scoped to the GSK-family panel.

(If the abstract above ever disagrees with papers/DT-GSK.pdf, the PDF wins —
re-copy from it.)

## 4. Keywords (paste as-is; semicolon-separated)

metaheuristic optimization; gaining-sharing knowledge; dimension-tiered
adaptive control; deterministic final refinement; adaptive operator selection;
population-size reduction; interaction-structure memory; CEC benchmark suites;
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

1. Save the manuscript ID from the confirmation page/email (algorithms-XXXXXXX).
2. Tell Claude the ID — it gets recorded in the governance log (AG-0006 row).
3. Do NOT rebuild anything in the repo afterwards: the submitted five files
   are hash-recorded in submission_package_manifest.json at v2.12. If a
   revision is ever requested, that becomes pass-38 through change control.
