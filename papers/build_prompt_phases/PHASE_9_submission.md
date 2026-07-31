# PHASE 9 — Submission Package

> **Objective (one sentence).** Assemble the complete, upload-ready submission
> folder for MDPI *Algorithms* — a finalised cover letter, correct front-matter
> and metadata, a reproducibility / data-and-code-availability statement anchored
> to the exact commit SHA, every source and PDF and figure the manuscript
> references, and a response-to-reviewers template seeded from the Phase-7
> revision log — then hold it behind a single human (PI) sign-off gate before it
> leaves the repository.

This file **expands Phase 9** of `papers/PAPER_BUILD_PROMPT.md` (the master
prompt; Part 5 › "PHASE 9 — Submission package", and Appendix E for the
reviewer-response template). It **follows `PHASE_8_compliance.md`** — the last
gate before this one, which certifies both PDFs compile clean and every Part-2
constraint is verified. **Phase 9 is the final phase**: it produces no new
science and edits no manuscript prose. It only packages what Phases 0–8 already
made true, and it hands nowhere — except back to Phase 7 if a revise-and-resubmit
decision ever arrives (see Hand-off).

Method under submission: **DT-GSK** — an adaptive Interaction-Structure Memory
(SGSM) overlay for high-dimensional Gaining–Sharing Knowledge optimization.
Authors: Mostafa Elsayed Masoud (corresponding, `moustafa.masoud@gmail.com`) and
Ali Wagdy Mohamed. Target journal: **MDPI *Algorithms*** (Q1/Q2), whose class
(`Definitions/mdpi.cls`, invoked as `\documentclass[algorithms,article,submit,
moreauthors,pdftex]{Definitions/mdpi}` at the top of `main.tex`) is already
wired into the manuscript.

Nothing here changes a number, a claim, or a figure. If Phase 9 uncovers a
substantive problem (a referenced exhibit that does not exist, a stale statistic,
a broken cross-reference), that is not a Phase-9 fix — it is a defect that sends
the work **back to the phase that owns it** (Phase 8 for compile/constraint
issues, Phase 2 for a statistic, Phase 5 for a figure). Phase 9 assembles; it
does not repair.

---

## Prerequisites

Phase 9 may not begin until the **Phase 8 exit gate is green**. Confirm each
before proceeding; if any is red, return to Phase 8 (or the phase it points to).

- [ ] **Both PDFs compile clean.** `main.tex` → `main.pdf` and
  `supplementary.tex` → `supplementary.pdf` build with **no undefined
  references**, **no missing figures**, and **no overfull-hbox errors that hurt
  legibility** (master prompt Phase 8.5). The two committed PDFs
  (`papers/main.pdf`, `papers/supplementary.pdf`) are the current build, not a
  stale one — rebuild and diff if in doubt.
- [ ] **Every Part-2 constraint verified with evidence.** The Phase-8 compliance
  checklist is complete: one concrete quantified abstract number with honest
  scope; the D30 second-place result stated openly, not hidden; no citation
  outside the **57 admissible keys**; every table/figure sourced from committed
  results. (Master prompt Phase 8.1–8.4.)
- [ ] **Repo green gates pass.** `pytest`, `ruff`, the **profile lock**, and the
  **docs build** are all green (master prompt Phase 8.6) — so every sentence the
  paper writes *about the software* remains true at submission time. The
  profile-lock witness `tests/test_d49_scaffold_byte_identity.py` (the
  below-threshold byte-identity guarantee the cover letter and Method both rely
  on) is passing.
- [ ] **The anchor commit SHA is chosen and recorded.** The single commit that
  every "reproducible from" claim cites (fixed in Phase 0, carried through
  Phase 1's claim table CL3) is written down and points at a commit that is (a)
  on the public repository, (b) contains the committed `results/**`,
  `environment.json`, and `results/CHECKSUMS.txt`, and (c) is the state the two
  PDFs were built from.
- [ ] **The Phase-7 revision log exists.** The gracious, evidence-led revision
  log produced during internal red-team review (Phase 7) is on disk — it is the
  seed for the response-to-reviewers template built in task 9.4. If Phase 7 left
  no log, there is nothing to seed; produce the empty-but-structured template and
  note it will be filled at the first real review round.

If Phase 8 left any item "assumed clean but not re-verified," treat it as red
here: **you cannot package a PDF you have not seen build clean.**

---

## Inputs

Phase 9 consumes finished artifacts only — it does not re-open raw data:

1. **The two clean PDFs and their sources** — `main.tex`/`main.pdf`,
   `supplementary.tex`/`supplementary.pdf` (Phase 8 output).
2. **The figures and tables** — everything under `papers/figures/`
   (`convergence/`, `diagrams/`, `flowchart/`, `ranks/`, `taxonomy/`, `traces/`)
   and `papers/tables/` (`T01..T22.tex`, `T16_bca.tex`) that the manuscript
   `\includegraphics` / `\input`s.
3. **The bibliography** — `papers/references.bib` (**57 keys**), confirmed to
   parse in the Phase-8 build.
4. **The cover-letter draft** — `papers/cover_letter.tex` (+ `cover_letter.pdf`),
   to be finalised in task 9.1. NOTE: the committed draft currently addresses
   *Swarm and Evolutionary Computation*; the target is **MDPI *Algorithms***, so
   the venue line must be corrected (see task 9.1 and Pitfalls).
5. **The reproducibility anchors** — `environment.json` (FP-regime sentinel),
   the seed formula `get_cec_seed(20240620, dim, func, run)`, the integrity
   manifest `results/CHECKSUMS.txt`, and the tuning-protocol disclosure
   `docs/TUNING_PROTOCOL.md`, all referenced by task 9.3.
6. **The Phase-7 revision log** — the seed for the response-to-reviewers template
   (master prompt Appendix E).

You do **not** recompute a statistic, regenerate a figure, or rewrite a section
in Phase 9. If an input is wrong, it goes back to its owning phase.

---

## Tasks

Work the five sub-tasks in order. Adopt the **P1 (PI / lead author)** hat for the
letter and the sign-off, and a meticulous **submissions-editor** hat for the
packaging: the failure mode here is not intellectual, it is clerical — a missing
file, a wrong ORCID, a supplement reference to a file not uploaded.

### 9.1 — Finalise `cover_letter.tex`

The cover letter is the editor's first read. It must, in four tight paragraphs,
do exactly five jobs — and it must address **MDPI *Algorithms***, not the venue
in the current draft.

**Required content (each is load-bearing; none optional).**
1. **Statement of the contribution.** What is genuinely new — the
   interaction-structure memory (ISM), instantiated as SGSM, as a *categorical
   addition* to the metaheuristic-memory taxonomy (it records co-improvement
   *topology*, not hyperparameters like SHADE/JADE success-history, not
   populations like external archives, not schedules like restart controllers).
   State it in the scope the evidence supports.
2. **Fit-to-journal argument.** Why *Algorithms* specifically: an algorithmic
   contribution with a controlled, reproducible empirical validation and released
   code — squarely in the journal's remit; the `algorithms` document class is
   already the manuscript's class.
3. **Originality + no-concurrent-submission statement.** The manuscript is
   original, not published elsewhere, and not under consideration by any other
   journal; all authors have read and approved.
4. **Reproducibility statement (one sentence pointing forward).** Code, per-run
   CSVs, the seed formula, the FP-regime sentinel, and a SHA-256 manifest are
   committed at a pinned public commit — the full paragraph lives in task 9.3 and
   in the manuscript's data-availability statement; the letter only signposts it.
5. **Conflict-of-interest disclosure, declared up front.** Prof. A. W. Mohamed
   is the originator of baseline GSK and a co-author of the AGSK / APGSK /
   FDB-AGSK / eGSK / ATMALS-GSK variants in the comparison panel. This is already
   disclosed in the draft; keep it in the letter, the authorship line, and the
   manuscript's conflicts statement, consistently.

**Suggested / excluded reviewers — conditional.** Provide these **only if the
journal's submission form asks for them.** MDPI *Algorithms* typically requests
suggested reviewers at the portal step, not in the letter. If asked:
- **Suggested:** name specialists with no co-authorship, no shared-institution,
  and no recent-collaboration tie to either author. The current draft offers
  *expertise areas* (SHADE-family self-adaptive DE; large-scale / structure-aware
  EC; benchmark-and-statistics methodology) rather than named individuals — that
  is a defensible, conflict-safe default; convert to named individuals only if
  the portal requires names.
- **Excluded:** anyone with a genuine conflict. Given the co-author's central
  role in the GSK lineage, **exclude close GSK-family collaborators** to preempt
  the "cosy review" objection.

**Micro-steps.**
1. Change the addressee block from *Swarm and Evolutionary Computation* to
   *Algorithms* (MDPI); verify the Editor-in-Chief / editorial-office salutation
   matches the journal.
2. Confirm the manuscript title in the letter is byte-identical to `main.tex`'s
   `\Title{...}`.
3. Confirm the author list and corresponding-author email match `main.tex`
   front-matter exactly (task 9.2 cross-check).
4. Compile `cover_letter.tex` → `cover_letter.pdf` clean; the letter is a
   standalone `article`-class document and must build independently of `main.tex`.
5. Keep it to **one page** if at all possible; editors skim.

*(A ready-to-fill skeleton is in Worked examples below.)*

### 9.2 — Front-matter & metadata

Every metadata field the portal will ask for must already be correct in
`main.tex`, so the portal entry is transcription, not authorship. Verify against
the MDPI template.

**Metadata checklist (verify each in `main.tex` front-matter, then transcribe).**
- [ ] **Title** — `\Title{...}`; matches cover letter and portal.
- [ ] **Authors** — `\Author{...}` in submission order; spelling and diacritics
  exactly as each author publishes them (Mostafa Elsayed Masoud; Ali Wagdy
  Mohamed).
- [ ] **Affiliations** — `\address{...}` / `\affiliation`, numbered, each author
  mapped to the right superscript; no placeholder "Department of X."
- [ ] **ORCIDs** — one per author via the MDPI `\orcidauthor` / `\orcidA` macro;
  a real 16-digit ORCID, not a stub. Missing ORCID is a common MDPI desk-return.
- [ ] **Corresponding author** — `\corres{...}` marks Mostafa Elsayed Masoud;
  `\corresemail{moustafa.masoud@gmail.com}` matches the cover letter.
- [ ] **Keywords** — `\keyword{...}`: **5–7**, lowercase, comma-separated, no
  trailing period. Draw from the paper's own vocabulary, e.g. *gaining–sharing
  knowledge; interaction-structure memory; high-dimensional optimization;
  metaheuristics; self-adaptive; CEC benchmarks*. Avoid keywords the abstract
  never earns.
- [ ] **Abstract** — `\abstract{...}`; ≤250 words (master prompt §6.1); one
  concrete quantified result with its honest scope (the D30 second place stated,
  not hidden); no citations inside the abstract.
- [ ] **Highlights / graphical abstract** — *Algorithms* does **not** mandate
  a graphical abstract, but accepts one. If supplied, it must be an original
  figure (not a lift of an in-paper figure verbatim) at the portal's resolution
  spec. If the journal's current author instructions do not request highlights,
  do not invent them.
- [ ] **MDPI-specific items** — Author Contributions statement (CRediT roles);
  Funding statement ("This research received no external funding" if true);
  Institutional Review Board / Informed Consent statements ("Not applicable" for
  an algorithms paper); Data Availability Statement (task 9.3); Conflicts of
  Interest statement (the GSK-lineage disclosure from 9.1). MDPI desk-returns
  submissions missing any of these back-matter blocks.

**Micro-steps.**
1. Open `main.tex`; walk the checklist top to bottom; fix any placeholder or
   mismatch **in the front-matter only** (this is metadata, not prose — it is in
   Phase-9 scope).
2. Rebuild `main.pdf`; confirm the title page renders authors, affiliations,
   ORCIDs, corresponding mark, keywords, and all back-matter blocks.
3. Produce a one-page **`metadata.txt`** in the submission folder holding the
   exact strings to paste into the portal (title, each author + affiliation +
   ORCID + email, keywords, abstract) so the human transcribes rather than
   retypes.

### 9.3 — Reproducibility & data/code availability statement

This is the claim the adversarial reviewer (R1) will test hardest (Phase-1 claim
CL3: *"Reproducibility asserted but not demonstrated"*). The statement must be
**demonstrable**, not aspirational, and it must cite the **exact commit SHA**.

**It must point at, by name:**
- **The committed benchmarks/results** — the reference panel under
  `benchmarks/cec_reference_results/**` (with local reproductions under
  `results/**`) that every reported table and figure is rendered from (CEC2017
  and CEC2013 at 51 runs; CEC2011 at 25 runs — the CEC conventions).
- **The seed policy** — the deterministic formula
  `get_cec_seed(20240620, dim, func, run)`, so any run regenerates bit-for-bit.
- **The FP-regime sentinel** — the floating-point-regime check recorded in
  `environment.json` that guards against a platform producing subtly different
  arithmetic (the reproducibility anchor confirmed in Phase 0).
- **The integrity manifest** — `results/CHECKSUMS.txt`, the SHA-256 digest over
  every reported run, so a reviewer can verify the committed CSVs are the ones
  the paper reports.
- **The tuning-protocol disclosure** — `docs/TUNING_PROTOCOL.md`, so the "how was
  this tuned" question is answered before it is asked.
- **The exact commit SHA** — the anchor from the Prerequisites; the statement is
  worthless without it (a reviewer cannot check "the repository" if the
  repository has moved since).

**Benchmark provenance citations (within the 57).** When the statement or Setup
names the suites, cite them from the admissible set only: `awad2016problem`
(CEC2017 definitions), `das2011cec2011` (CEC2011 real-world), `liang2013cec2013`
(CEC2013). The statistics the reproducibility claim underwrites are cited where
they are used (Setup / Results), from: `friedman1937use`, `demsar2006statistical`,
`wilcoxon1945individual`, `holm1979simple`, `benjamini1995controlling`,
`vargha2000critique`, `efron1993introduction`. Do not introduce a "reproducibility"
or "software" citation outside the 57 — if one seems needed, name the artifact by
path instead.

**Micro-steps.**
1. Draft the Data Availability paragraph (template in Worked examples) into the
   manuscript's `\dataavailability{...}` back-matter block **if and only if** the
   number/paths already exist as committed artifacts — this is transcription of
   verified facts, not a new claim.
2. Fill the `<COMMIT-SHA>` slot with the actual full 40-char hash (or the pinned
   short SHA the repo uses consistently); never leave the placeholder.
3. Verify every path in the paragraph resolves in the repo at that SHA
   (`results/**`, `environment.json`, `results/CHECKSUMS.txt`,
   `docs/TUNING_PROTOCOL.md`).
4. Cross-check the manuscript's Setup section already states the seed formula and
   FP-regime once (Phase 4 prose); the availability statement points to it, it
   does not re-derive it.

### 9.4 — Package assembly

Build one flat, named submission folder holding **exactly** what the portal
uploads — nothing referenced that is not present, nothing present that is not
referenced. Recommended location: a `papers/submission/` staging folder (do not
commit it if it duplicates tracked artifacts; it is an upload bundle).

**Upload manifest (every item; check off as staged).**
- [ ] `main.tex` — manuscript source (with corrected front-matter, 9.2).
- [ ] `main.pdf` — the clean compiled manuscript (Phase 8).
- [ ] `supplementary.tex` — supplement source.
- [ ] `supplementary.pdf` — the clean compiled supplement.
- [ ] `references.bib` — the 57-key bibliography (and/or the `.bbl` if the portal
  requires a pre-built bibliography for the LaTeX compile).
- [ ] `Definitions/mdpi.cls` **and its companions** (`mdpi.bst`, logos, any
  `Definitions/*` the class `\input`s) — MDPI's server compiles the source, so
  the class files must ship or the build fails at their end.
- [ ] **Figures at required resolution** — every file under `papers/figures/**`
  that the manuscript or supplement includes. The figures are **vector PDFs**,
  which satisfy MDPI's raster spec (≥300 dpi photos / ≥1000 dpi line art) because
  vector art is resolution-independent; keep them vector. Do not down-convert a
  vector figure to a low-dpi raster.
- [ ] `cover_letter.pdf` — the finalised letter (9.1).
- [ ] `metadata.txt` — the portal-paste strings (9.2).
- [ ] Highlights / graphical-abstract file — **only if** the journal requested it
  (9.2).
- [ ] `RESPONSE_TO_REVIEWERS.md` (template) — see below; staged now, filled at
  review time.

**The response-to-reviewers template (built from the Phase-7 revision log).**
Seed it from the master prompt's Appendix E convention. For **each** point in the
Phase-7 revision log, emit one entry with four fields, in this order:
1. **Quote** the reviewer comment verbatim.
2. **Change** — what was actually altered in the manuscript.
3. **Where** — the exact section / table / figure now addressing it (so the
   reviewer can verify in one click).
4. **Principled reason if declined** — if a request was not adopted, the
   evidence-led, gracious reason (never dismissive).

Because there is no real review yet, the template is populated from Phase-7's
*internal* red-team points — this pre-stages the structure and proves the paper
already anticipated the likely objections (e.g. the "same-family scope is
convenient" objection, the "for-free is a design claim, where is the accounting"
objection, the "ranks can flip under a different post-hoc" objection from the
Phase-1 claim table). Keep tone gracious and evidence-led throughout.

**Micro-steps.**
1. Create `papers/submission/`; copy each manifest item in.
2. **Reference-closure check (mechanical, mandatory).** Grep `main.tex` and
   `supplementary.tex` for every `\includegraphics`, `\input`, `\ref`,
   `\cref`, and cross-document reference; confirm each target file is present in
   the folder. Grep the supplement for any "see the repository / see file X"
   pointer; confirm X is either in the package or is a public-repo path reachable
   at the anchor SHA. **A supplement that references a file not in the package is
   the single most common submission defect** (see Pitfalls).
3. Confirm the folder contains **no** stray build artifacts (`*.aux`, `*.log`,
   `*.out`, `*.synctex.gz`) — they are not uploaded.
4. Write `RESPONSE_TO_REVIEWERS.md` from the Phase-7 log using the four-field
   entry format (example in Worked examples).
5. Produce a one-line `MANIFEST.txt` listing every file in the folder with its
   role, for the PI sign-off in 9.5.

### 9.5 — Final human (PI) sign-off gate

The package does not leave the repository on the agent's authority. This is a
**hard human gate** (master prompt Phase 9 exit; P1 owns submission).

**What the PI confirms (single closed checklist).**
- [ ] The manuscript, supplement, cover letter, figures, bib, class files, and
  response template are all present in `papers/submission/` (per `MANIFEST.txt`).
- [ ] **Nothing the two PDFs reference is missing from the package** — the
  reference-closure check (9.4 step 2) is green.
- [ ] The reproducibility statement cites the correct, current commit SHA and
  every path resolves.
- [ ] Author metadata (names, affiliations, ORCIDs, corresponding email) is
  correct and consistent across `main.tex`, the cover letter, and `metadata.txt`.
- [ ] The venue in the cover letter reads *Algorithms* (MDPI), not a leftover
  journal name.

Record the sign-off as a dated line in the project's decision log
(`decisions.md`, carried from Phase 1) — e.g. *"2026-07-08 — P1 (M. Masoud)
confirms submission package complete; nothing referenced is missing; cleared for
upload to MDPI Algorithms. Anchor SHA <...>."* No sign-off line → not submitted.

---

## Worked examples

**A cover-letter skeleton (MDPI *Algorithms*; fill the slots).**
```
To the Editor-in-Chief, Algorithms (MDPI)

Manuscript: An Adaptive Interaction-Structure Memory for High-Dimensional
Gaining–Sharing Knowledge Optimization
Authors: Mostafa Elsayed Masoud, Ali Wagdy Mohamed
Corresponding author: Mostafa Elsayed Masoud (moustafa.masoud@gmail.com)

Dear Editor,

[Para 1 — CONTRIBUTION] We submit our manuscript for consideration in
Algorithms. It introduces <the interaction-structure memory (ISM): an online,
O(D^2), acceptance-driven record of pairwise co-improvement that biases the
subspace subsequent operators act on — a categorical addition to the
metaheuristic-memory taxonomy, distinct from hyperparameter memories
(SHADE/JADE), population archives, and restart schedules>. We instantiate it as
SGSM and bind it to linkage-aware crossover and a Nelder–Mead endgame at D≥50;
below that threshold the algorithm is byte-identical to its scaffold, which
isolates the ISM's contribution to the high-dimensional regime.

[Para 2 — FIT + RESULT WITH SCOPE] The contribution suits Algorithms as an
algorithmic advance with a controlled, reproducible empirical validation.
Within a same-family GSK panel evaluated identically on CEC 2017 (n=51), DT-GSK
attains <the best mean Friedman rank overall and at D∈{10,50,100}>, with
<D30 the honest exception — second, behind eGSK>; the CEC 2011 real-world suite
and the CEC 2013 second comparison suite preserve the pattern without retuning.

[Para 3 — REPRODUCIBILITY + CONFLICT] All code, per-run CSVs, the seed formula,
the FP-regime sentinel, and a SHA-256 integrity manifest are committed at a
pinned public commit (see the Data Availability statement). We declare one
relationship up front: Prof. A. W. Mohamed originated baseline GSK and co-authored
the family variants we compare against; this is reflected in the authorship line,
the literature review, and the conflicts-of-interest statement. No funding body
influenced the design, statistics, or interpretation.

[Para 4 — ORIGINALITY] The manuscript is original, has not been published
elsewhere, and is not under consideration by any other journal; all authors have
read and approved this submission.

Sincerely,
Mostafa Elsayed Masoud (corresponding author); Ali Wagdy Mohamed
```

**A data/code availability paragraph (cites a commit SHA).**
```
Data Availability Statement. All code, benchmark run data, and analysis
scripts that reproduce every reported table and figure are openly available in
the project repository at commit <a1b2c3d4e5f6...> (full 40-character SHA).
The per-run objective traces are committed in the reference panel under
benchmarks/cec_reference_results/ (CEC 2017 and CEC 2013 at 51 runs; CEC 2011
at 25 runs); each reported value regenerates bit-for-bit
from the deterministic seed formula get_cec_seed(20240620, dim, func, run) under
the floating-point regime recorded in environment.json. A SHA-256 digest over
every reported run is provided in results/CHECKSUMS.txt, and the complete tuning
protocol is disclosed in docs/TUNING_PROTOCOL.md. Benchmark definitions follow
the CEC technical reports [awad2016problem, das2011cec2011, liang2013cec2013].
```

**A response-to-reviewers entry (four fields; seeded from the Phase-7 log).**
```
### Reviewer 1, Comment 3
> "The comparison is restricted to the GSK family; a same-family scope is
> convenient rather than fair. Why not include L-SHADE-class baselines?"

Change made. We added an explicit scope justification to the Experimental Setup
and expanded the Limitations discussion of external generality.

Where addressed. Section 4.2 (panel scope and why same-family isolation is the
correct control for an *overlay* contribution) and Section 5.6 (limitations,
including the D30 second-place result stated openly).

Reason (where partially declined). We do not add a cross-family L-SHADE panel as
a co-headline: doing so would confound the overlay's effect with a different base
algorithm, defeating the controlled isolation the paper is designed around. We
instead cite the L-SHADE frontier as positioning (Section 2.3) and report the
CEC 2011 real-world suite and the CEC 2013 second comparison suite as the
external-generality evidence.
```

---

## Pitfalls & anti-patterns

- **Referencing a supplement file not included.** The most common submission
  defect: `supplementary.tex` (or `main.tex`) says "see file X / see the
  repository for Y" and the portal upload does not contain X. The 9.4 step-2
  reference-closure grep exists precisely to catch this — run it, do not eyeball
  it. Every `\includegraphics`/`\input`/`\ref` target and every prose pointer
  must resolve to a packaged file or a public-repo path live at the anchor SHA.
- **Figure resolution below journal spec.** Down-converting the vector PDF
  figures to low-dpi raster (or exporting a screenshot) fails MDPI's
  ≥300-dpi/≥1000-dpi requirement. Ship the figures as the vector PDFs they
  already are; vector art is resolution-independent and passes by construction.
- **Mismatched author metadata.** Name spelling, affiliation numbering, ORCID, or
  corresponding email differing between `main.tex`, `cover_letter.tex`, and the
  portal entry causes desk-return or an incorrect published record. Make one
  canonical source (the `main.tex` front-matter) and copy from it — never retype.
  A missing or stub ORCID is a frequent MDPI desk-return.
- **A reproducibility statement without a commit SHA.** "Available in the
  repository" with no pinned hash is not reproducible — the repository moves.
  Every availability claim names the exact SHA and every path resolves at it.
  This is the R1 objection CL3 was written to defeat; do not hand it back.
- **Suggested reviewers with conflicts.** Given the co-author's central role in
  the GSK lineage, nominating a close GSK-family collaborator invites the "cosy
  review" objection and can trigger editor distrust of the whole submission.
  Prefer conflict-free specialists (or the expertise-areas default in the draft);
  actively **exclude** near collaborators; provide names only if the portal asks.
- **Leftover venue name.** The committed `cover_letter.tex` addresses *Swarm and
  Evolutionary Computation*; the target is MDPI *Algorithms*. Shipping the letter
  with the wrong journal name is an instant credibility hit — verify the addressee
  block, salutation, and any in-body "for consideration at ..." line.
- **Packaging stale PDFs.** Uploading a `main.pdf`/`supplementary.pdf` built
  before the final Phase-8 fixes. Rebuild from the anchor-SHA source and confirm
  the PDF in the package is that build.
- **Treating a real defect as a Phase-9 edit.** If closure fails because an
  exhibit genuinely does not exist or a number is stale, that is not a
  package-it-anyway situation and not a Phase-9 prose fix — it returns to the
  owning phase (8 / 5 / 2). Phase 9 assembles verified artifacts; it does not
  manufacture missing ones.
- **Skipping the human gate.** The agent does not submit. Assembling the folder
  is Phase 9's job; releasing it is the PI's, recorded as a dated sign-off line.

---

## Exit gate

Phase 9 — and the build — is complete only when **all** hold, each with evidence:

- [ ] **Submission folder complete.** `papers/submission/` contains every
  manifest item from 9.4 (main source + PDF, supplement source + PDF, figures,
  `references.bib` and needed `Definitions/*` class files, finalised cover
  letter, `metadata.txt`, highlights if requested, response-to-reviewers
  template), and no stray build artifacts. `MANIFEST.txt` lists them.
- [ ] **Every referenced file is included.** The 9.4 reference-closure check is
  green: no `\includegraphics`/`\input`/`\ref`/prose pointer in either PDF
  targets a file absent from the package or unreachable at the anchor SHA.
- [ ] **Metadata correct and consistent.** Title, authors, affiliations, ORCIDs,
  corresponding email, keywords (5–7), and abstract match across `main.tex`, the
  cover letter, and `metadata.txt`; the cover letter names MDPI *Algorithms*.
- [ ] **Reproducibility statement anchored.** The Data Availability paragraph
  cites the exact commit SHA, names `results/**`, the seed formula, the
  FP-regime sentinel (`environment.json`), the SHA-256 manifest
  (`results/CHECKSUMS.txt`), and `docs/TUNING_PROTOCOL.md`; every path resolves.
- [ ] **Response template ready.** `RESPONSE_TO_REVIEWERS.md` exists in the
  four-field format, seeded from the Phase-7 revision log, ready for the eventual
  review round.
- [ ] **PI sign-off recorded.** A dated P1 sign-off line in `decisions.md`
  confirms nothing referenced is missing and clears the package for upload.

**Evidence artifacts produced by this phase:**
- `papers/submission/` — the flat, upload-ready folder with `MANIFEST.txt`.
- `papers/submission/metadata.txt` — the portal-paste metadata strings.
- `papers/submission/RESPONSE_TO_REVIEWERS.md` — the seeded response template.
- The finalised `papers/cover_letter.tex` / `cover_letter.pdf`.
- The Data Availability paragraph in `main.tex` back-matter (with the SHA).
- The dated PI sign-off line in `decisions.md`.

---

## Hand-off

**None — Phase 9 is the final phase.** The build plan ends when the PI-signed
package is cleared for upload.

**The one loop back.** If the journal returns a **revise-and-resubmit**, the work
does *not* re-enter at Phase 9. It loops to **Phase 7** (the red-team / revision
phase): the real reviewer comments replace the internal red-team points as the
seed for the revision log, each is worked to a change + section pointer +
principled-reason-if-declined, and the manuscript then re-flows Phase 7 → Phase 8
(recompile clean, re-verify constraints, re-run green gates) → Phase 9 (re-package
with the *filled* `RESPONSE_TO_REVIEWERS.md`, a new anchor SHA for the revised
commit, and a fresh PI sign-off). The response template built here in 9.4 is what
makes that loop fast: its structure and its pre-staged answers to the likely
objections are already in place.
