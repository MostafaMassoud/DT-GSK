# DT-GSK — author & submission data handoff

**Purpose.** A self-contained briefing for a *fresh* session with no prior
context. Everything below is transcribed from the frozen manuscript sources and
the governance record, not from recollection. Where a value is unverified or
author-owned it is marked so explicitly — do not silently promote a marked value
to a fact.

**Generated** 2026-08-07 from tag `v2.13` (freeze pass-38).

---

## 0. Hard constraints — read before doing anything

1. **The manuscript is under peer review and FROZEN.** Do NOT rebuild, re-mint,
   or edit any manuscript artifact. `v2.13` is the exact record of what the
   editor and reviewers are reading, and the public repository must keep
   matching it (the Data Availability Statement points reviewers at it).
2. **A revision, if one comes, is a NEW freeze pass through change control** —
   never an edit to the submitted state. Standing instruction, D-0045.
3. **Fifteen files are hash-frozen** in
   `papers/governance/main_manuscript_freeze_manifest.json`; `check_manifest`
   must stay 15/15. Files under `papers/submission/` (including this one) are
   NOT in the manifest and may be edited freely.
4. **Never invent author data.** Degrees, ranks, editorial roles, and versions
   are author-owned. The project rule is: an unsupported specific claim is worse
   than an acknowledged gap.

---

## 1. Manuscript identity

| Field | Value |
|---|---|
| Title | DT-GSK: Dimension-Tiered Adaptive Control and Deterministic Refinement for Gaining-Sharing Knowledge Optimization |
| Journal | *Algorithms* (MDPI) |
| Section | Evolutionary Algorithms and Machine Learning |
| Article type | Article |
| Manuscript ID | **algorithms-4507562** |
| Submitted | 2026-08-01 via SuSy |
| Status | **Under review** (cleared the editorial desk gate 2026-08-01) |
| Peer-review model | **Open Review — elected by the author and retained** (confirmed by the editorial office, 2026-08) |
| Special Issue | none (regular submission) |
| Frozen basis | freeze pass-38, tag **`v2.13`** (tag commit `33bc50305`; repository anchor at submission `b51590790`) |
| Submitted files | LaTeX source ZIP, `DT-GSK.pdf` (47 pp), `supplementary.pdf` (75 pp), `cover_letter.pdf` (2 pp), 600 dpi figures ZIP — hashes in `papers/governance/submission_package_manifest.json` |
| Word/DOCX | deliberately NOT uploaded (LaTeX submission; DOCX is a pandoc companion whose layout legitimately differs) |

---

## 2. Author roster — master table

**Author order is fixed and must never be reordered.** All three carry
affiliation 1 only (affiliations 2 and 3 were removed at the author's direction
on 2026-07-29).

| # | Full name | Initials | Role | ORCID iD |
|---|---|---|---|---|
| 1 | **Mostafa Elsayed Masoud** | M.E.M. | **Corresponding author** | `0009-0003-8415-2158` |
| 2 | **Heba Sayed Mohamed Roshdy** | H.S.M.R. | Co-author | `0000-0003-0387-5876` |
| 3 | **Ali Wagdy Mohamed** | A.W.M. | Co-author | `0000-0002-5895-2632` |

All three ORCID iDs pass the ISO 7064 MOD 11-2 checksum and are distinct
(verified 2026-07-25, AG-0002 closed). An earlier author message mistakenly
repeated M.E.M.'s iD for A.W.M.; that duplicate was rejected, not applied.

**Name splitting for portal forms** (matters — a wrong split displays a name
that does not match the paper):

| Author | First | Middle | Last |
|---|---|---|---|
| 1 | Mostafa | Elsayed | Masoud |
| 2 | Heba | Sayed Mohamed | Roshdy |
| 3 | Ali | Wagdy | Mohamed |

**Courtesy titles** (as used in correspondence): Mr. Masoud (PhD candidate),
Dr. Roshdy, Prof. Dr. Ali Wagdy Mohamed.

---

## 3. Affiliation (identical for all three authors)

```
Operations Research Department, Faculty of Graduate Studies for Statistical
Research, Cairo University, Giza 12613, Egypt
```

Components for forms: Department = `Operations Research Department`;
Faculty/Institute = `Faculty of Graduate Studies for Statistical Research`;
University = `Cairo University`; City = `Giza`; Zip = `12613`;
Country = `Egypt`; Time zone = `(GMT+02:00) Cairo`.

---

## 4. Email addresses — TWO SETS, both live

### 4a. Personal addresses — these are what the SUBMITTED MANUSCRIPT prints

Printed in the affiliation block of `papers/main.tex` and therefore in the
frozen PDF/DOCX:

| Author | Email in the manuscript |
|---|---|
| M.E.M. (corresponding) | `moustafa.masoud@gmail.com` |
| H.S.M.R. | `hmhmdss@yahoo.com` |
| A.W.M. | `aliwagdy@gmail.com` |

Correspondence line in the paper: `Correspondence: moustafa.masoud@gmail.com`

### 4b. Institutional addresses — supplied to the editorial office 2026-08

Requested by the *Algorithms* editorial office and sent by the corresponding
author; the office said it would update SuSy accordingly.

| Author | Institutional email |
|---|---|
| M.E.M. (corresponding) | `12422024551622@pg.cu.edu.eg` |
| H.S.M.R. | `HebaSayed@cu.edu.eg` |
| A.W.M. | `aliwagdy@cu.edu.eg` |

### 4c. OPEN QUESTION arising from the above

All three manuscript addresses are personal; all three institutional ones are
`cu.edu.eg`. **The submitted byline and the SuSy record will therefore
disagree.** The corresponding author has asked the editorial office which they
want displayed. Two outcomes:

- *System only* → nothing changes in the paper. No action.
- *Update the manuscript too* → this is a genuine manuscript text change and
  must run as a **new freeze pass (`v2.14`)**, editing the `\address{}` and
  `\corres{}` blocks in `papers/main.tex`, never as an ad-hoc edit.

Until the office answers, **change nothing**. Also note SuSy notifications
currently route to the Gmail address — keep monitoring it even after any update.

---

## 5. CRediT author contributions

**Author-stated allocation** (re-confirmed 2026-07-25, AG-0001 closed):

| Author | Roles |
|---|---|
| M.E.M. | Conceptualization; Methodology; Software; Formal analysis; Investigation; Data curation; Writing – original draft |
| H.S.M.R. | Writing – review & editing; Supervision |
| A.W.M. | Methodology; Formal analysis; Investigation; Data curation; Writing – original draft; Supervision; Project administration |

**As rendered in the manuscript** (MDPI role-first convention — this is the
authoritative published form; it is equivalent to the table above):

> Conceptualization, M.E.M.; methodology, M.E.M. and A.W.M.; software, M.E.M.;
> formal analysis, M.E.M. and A.W.M.; investigation, M.E.M. and A.W.M.; data
> curation, M.E.M. and A.W.M.; writing—original draft preparation, M.E.M. and
> A.W.M.; writing—review and editing, H.S.M.R.; supervision, H.S.M.R. and
> A.W.M.; project administration, A.W.M. All authors have read and agreed to
> the published version of the manuscript.

---

## 6. Author biographies

MDPI requires these **before acceptance**, not before review. Each publishes on
the paper's webpage only if the author's toggle is on.

### 6a. Mostafa Elsayed Masoud — APPROVED AND ENTERED IN SuSy

> Mostafa Elsayed Masoud is a PhD candidate in the Operations Research
> Department, Faculty of Graduate Studies for Statistical Research, Cairo
> University, Egypt. He holds a master's degree in Operations Research, a
> two-year postgraduate diploma in Operations Research and Statistics, and a
> two-year postgraduate diploma in Computer Science.
>
> He has over 20 years of professional experience in information technology,
> enterprise resource planning (ERP) systems, and Java- and Python-based
> automation solutions, contributing to technology and digital-transformation
> initiatives across government, public-sector, and private-sector
> organizations.
>
> His research interests include metaheuristic optimization, evolutionary
> computation, artificial intelligence, and supply chain optimization, with
> particular focus on Gaining-Sharing Knowledge (GSK) optimization algorithms,
> adaptive operator control, and rigorous, reproducible performance evaluation
> on the IEEE CEC benchmark suites.

(~1,070 characters; SuSy's limit is 1,500.)

### 6b. Heba Sayed Mohamed Roshdy — DRAFT, AWAITING HER APPROVAL

> Heba Sayed Mohamed Roshdy is a faculty member at the Operations Research
> Department, Faculty of Graduate Studies for Statistical Research, Cairo
> University, Giza, Egypt [PhD in Operations Research, Cairo University]. She
> is a co-author of the enhanced Gaining-Sharing Knowledge (eGSK) algorithm,
> and her research interests include operations research, metaheuristic
> optimization, and evolutionary computation.

Bracketed = **inferred, not verified**; hers to confirm or correct. If she holds
a specific rank (Lecturer / Assistant Professor / Associate Professor), use it
in place of "faculty member". The eGSK co-authorship is safe — the manuscript's
own COI statement declares it.

### 6c. Ali Wagdy Mohamed — DRAFT, AWAITING HIS APPROVAL

> Ali Wagdy Mohamed is a Professor at the Operations Research Department,
> Faculty of Graduate Studies for Statistical Research, Cairo University, Giza,
> Egypt. He is the originator of the Gaining-Sharing Knowledge (GSK)
> optimization algorithm and a co-author of several of its published variants,
> and his algorithms have ranked among the top performers in IEEE CEC
> optimization competitions [including AGSK, runner-up in the CEC 2020
> bound-constrained competition].
>
> His research interests include evolutionary computation, differential
> evolution, metaheuristic optimization, global and engineering optimization,
> and machine learning applications. He has authored numerous highly cited
> publications in these areas [and serves on the editorial boards of several
> journals in evolutionary computation and optimization].
>
> [Degrees: to be confirmed — e.g., PhD in Statistics, Cairo University.]

Bracketed = **placeholders, not verified facts**. Current editorial roles,
degree details, and CEC phrasing are his to state; drop anything he does not
confirm. Google Scholar: `https://scholar.google.com/citations?user=PFy3kvIAAAAJ`

**Rule for both co-author bios: ask, do not draft-and-paste.** A biography is a
personal professional statement published under that person's name. Preferred
route is to request their standard institutional bio. Do not enter either bio
without that author's explicit approval.

---

## 7. Conflicts of interest — as declared in the manuscript

The relationships (paraphrase; the verbatim block is in `papers/main.tex`
`\conflictsofinterest{}`):

- **A.W.M.** is the originator of the baseline GSK algorithm and a co-author of
  the AGSK, APGSK, eGSK, and ATMALS-GSK comparators used in this paper.
  FDB-AGSK, a further comparator, is an independent third-party variant.
- **H.S.M.R.** is a co-author of the eGSK comparator.
- **A.W.M. is the doctoral supervisor of M.E.M.**
- **Specific adjacency disclosed:** AGSK was the runner-up of the CEC2020
  competition whose suite serves as this paper's pre-registered confirmatory
  benchmark, and the AGSK paper is A.W.M.'s. This accompanies every
  interpretation of the CEC2020 results in the text.
- Mitigation stated: every comparator was re-executed from its
  reference-implementation configuration under an optimizer-independent seed
  schedule; the released evidence permits third-party re-derivation.
- No other conflicts; no funding body influenced anything.

**Consequence for reviewer suggestions:** this COI structure rules out every
GSK-family comparator author, anyone at Cairo University, and any collaborator
of any author within three years.

---

## 8. Funding, ethics, consent

| Statement | Value |
|---|---|
| Funding | **This research received no external funding.** (AG-0003, confirmed 2026-07-13, re-confirmed 2026-07-25) |
| Institutional Review Board | Not applicable. |
| Informed Consent | Not applicable. |

---

## 9. Data availability & repository

| Field | Value |
|---|---|
| Repository | `https://github.com/MostafaMassoud/DT-GSK` — **public** |
| Submitted version | tag **`v2.13`** |
| Zenodo deposit | **none** — deliberate author decision (D-0044) |
| Repository DOI | **none, and none is to be reserved** |
| Article DOI | assigned by *Algorithms* after acceptance |
| Code licence | MIT |
| Data/analysis licence | CC BY 4.0 |
| Benchmark definitions | remain under their respective upstream terms |

Evidence releases cited in the statement: `rel-2026-07-20-67d9345f9` (primary:
CEC2017/2011/2013), `lsgo-rel-2026-07-28-ff1a046ef` (CEC2013LSGO),
`cec2020-rel-2026-07-29-5867abe1e` (CEC2020), plus a separate immutable
component-isolation release for Section S6.

Preprint: **none published.** A Preprints.org submission (ID 226790) was posted
and withdrawn the same day, 2026-08-04, inside the pre-announcement screening
window; no DOI was issued (D-0046, CLOSED).

---

## 10. Generative-AI disclosure — use this wording, unchanged

Named in all three required loci (declaration, methods-level description,
acknowledgments). **Claude versions are stated; ChatGPT's deliberately is NOT** —
the author-recalled version strings were never verified, and this project does
not publish a model number on inference (D-0036). Do not add "5.5" or "5.6".

Manuscript block, verbatim:

> **Use of Generative Artificial Intelligence:** During the preparation and
> revision of this manuscript (2026), the authors used two generative-AI
> assistants: Claude (Opus 4.6, 4.8 and 5.0; Anthropic) and ChatGPT (OpenAI).
> They assisted with language editing and rephrasing; the drafting of expository
> prose that restates and explains findings the authors had already established
> from the frozen evidence; structural review, consistency checking, and review
> of the statistical and methodological descriptions; and software-engineering
> support during implementation and tooling work. The algorithm design and the
> experimental protocol are the authors' own, and every reported number was
> produced by the authors' deterministic analysis pipeline from a version-locked
> evidence archive: no AI system designed an experiment, produced data, computed
> a statistic, or generated a scientific claim, result, or conclusion, and no AI
> system is an author of this work. Every suggestion was critically evaluated
> and, where adopted, revised and verified by the authors, who take full
> responsibility for the content of this publication.

---

## 11. Corresponding-author SuSy profile (as configured)

| Field | Value |
|---|---|
| Workplace | Academic |
| Job type | PhD Student |
| Title | Mr. |
| Name split | Mostafa / Elsayed / Masoud |
| Affiliation | Operations Research Department, Faculty of Graduate Studies for Statistical Research, Cairo University |
| Address | institutional — Faculty of Graduate Studies for Statistical Research, Cairo University |
| Zip / City / Country | 12613 / Giza / Egypt |
| Time zone | (GMT+02:00) Cairo |
| ORCID | 0009-0003-8415-2158 |
| Social media | left blank |

**Invoicing note:** the author asked for invoices at his home address. The
*profile* address stays institutional (AG-0006 keeps the residential address out
of every project artifact); the home address belongs only in SuSy's separate
billing/invoice fields, and must not be written into any repository file.

---

## 12. Editorial correspondence to date

| Date | Event |
|---|---|
| 2026-08-01 | Submitted; status *Pending editor decision* → **Under review** the same day (desk gate cleared). D-0045. |
| 2026-08-04 | Preprints.org ID 226790 posted, then withdrawn the same day. D-0046, CLOSED. |
| 2026-08 | Editorial office queried the **Open Review** election; author replied confirming he wished to retain it. Office confirmed retention. |
| 2026-08 | Office requested **institutional email addresses for all authors**; author supplied M.E.M. and A.W.M. first, then H.S.M.R. Office to update SuSy. |

Expected: reviewer reports around mid-to-late August 2026 (journal median ~17.8
days to first decision). Because Open Review was elected, reports publish
alongside the paper.

---

## 13. Open items

| # | Item | Owner | Due |
|---|---|---|---|
| 1 | H.S.M.R. biography — approval of §6b | Dr. Roshdy | before acceptance |
| 2 | A.W.M. biography — approval of §6c | Prof. Mohamed | before acceptance |
| 3 | Editorial-office answer on the byline-email question (§4c) | office | before proofs |
| 4 | Reviewer reports → point-by-point response | on arrival | — |

Nothing else is outstanding. Repository is clean, pushed, gates 15/15.

---

## 14. Authoritative sources — verify against these, not against this file

| What | Where |
|---|---|
| Byline, ORCIDs, CRediT, COI, funding, DAS, GenAI blocks | `papers/main.tex` |
| Every SuSy form value in portal order | `papers/submission/SUBMISSION_KIT.md` |
| Decision history (D-0001 … D-0046) | `papers/governance/decision_log.md` |
| Author-side administrative gaps (AG-0001 … AG-0007) | `papers/governance/administrative_gap_register.md` |
| Hashes of the 15 frozen files | `papers/governance/main_manuscript_freeze_manifest.json` |
| Hashes of the 5 uploaded files | `papers/governance/submission_package_manifest.json` |
| Anticipated reviewer objections | `papers/build_prompt_phases/phase_10/response_to_reviewers_seed.md` |

If this file ever disagrees with `papers/main.tex`, **the manuscript wins** —
re-transcribe from it.
