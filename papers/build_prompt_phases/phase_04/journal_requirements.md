# Phase 4 Task 1 — Target-Journal Requirements Record: MDPI *Algorithms*

- **Frozen target journal**: MDPI *Algorithms* (decision D-0010, `papers/governance/decision_log.md`; see `phase_04/journal_decision.md`).
- **Access date**: 2026-07-10.
- **Primary source URL (official)**: https://www.mdpi.com/journal/algorithms/instructions
- **Secondary source URLs (official MDPI, reached via search snippets only)**:
  - https://www.mdpi.com/journal/algorithms
  - https://www.mdpi.com/journal/algorithms/apc
  - https://www.mdpi.com/about/apc-2026-2 (APC list as of July 2026)
  - https://www.mdpi.com/authors/references (MDPI reference style guide)
  - https://www.mdpi.com/editorial_process (MDPI editorial/peer-review process)
- **verified_online = FALSE.** Direct retrieval of the official Instructions-for-Authors page FAILED on 2026-07-10: `https://www.mdpi.com/journal/algorithms/instructions` and `https://www.mdpi.com/journal/algorithms` both returned **HTTP 403 Forbidden** to the automated fetcher (mdpi.com blocks non-browser clients). Everything below is therefore graded by evidence class and **MUST be re-verified against the live official page in a browser before submission** (owner: Phase 8 draft gate re-check; hard gate at Phase 9 build / Phase 11 packaging).

## Evidence classes used below

| Class | Meaning |
|---|---|
| REPO-PROVEN | Proven by files inside this repository (byte-inspectable). |
| SEARCH-DERIVED | Returned by web search on 2026-07-10 quoting official MDPI pages; the page itself was NOT directly fetched. Treat as provisional. |
| UNKNOWN | Not established by either source. Do NOT assume; resolve at re-verification. |

## 1. Article type

- **"Article" (full research article)** — REPO-PROVEN as the wired type: `papers/main.tex` line 5 is `\documentclass[algorithms,article,submit,moreauthors,pdftex]{Definitions/mdpi}` — class options `algorithms` (journal) and `article` (type).
- SEARCH-DERIVED: *Algorithms* is a peer-reviewed, open-access journal published monthly by MDPI; manuscripts must contain the required sections: Author Information, Abstract, Keywords, Introduction, Materials & Methods, Results, Conclusions, Figures and Tables with Captions, Funding Information, Author Contributions, Conflict of Interest and other Ethics Statements.
- UNKNOWN: the current full list of accepted article types on the live page (e.g., Review, Communication) — not needed for this project; the wired type is `article`.

## 2. Length / page guidance

- SEARCH-DERIVED (general MDPI guidance, applied to *Algorithms*): **no fixed maximum length**; authors are advised to contact the Editorial Office in advance if the paper is **shorter than 3,000 words or longer than 12,000 words**.
- No hard typeset-page limit was found. **Consequence (binding)**: under the framework Section 1.5 hard page-limit rule ("or the typical accepted article length, when no hard limit is published"), the limit binds to the **SELF-IMPOSED budget in `page_budget.md`** (main total approximately 16–22 typeset pages excluding references, per the Section 1.5 budget table). See `journal_decision.md`.
- VERIFY-BEFORE-SUBMISSION: confirm on the live page that *Algorithms* publishes no journal-specific length cap.

## 3. Template

- REPO-PROVEN: MDPI LaTeX class present at `papers/Definitions/mdpi.cls` (header: "LaTeX support: latex@mdpi.com"); manuscript wired to it via `papers/main.tex` line 5 (options `algorithms,article,submit,moreauthors,pdftex`).
- SEARCH-DERIVED: MDPI requires manuscripts prepared with the **Microsoft Word template or LaTeX template**; the MDPI LaTeX template is also available through the Overleaf (writeLaTeX) template gallery with direct submission support. MDPI additionally operates a **free-format initial submission** policy (references may be in any style provided formatting is consistent); MDPI-format compliance is enforced at revision/production.
- VERIFY-BEFORE-SUBMISSION: confirm the vendored `mdpi.cls` matches the CURRENT template version distributed by MDPI (template drift is a known risk; do not silently swap class files — raise a change request if outdated).

## 4. Reference / citation style

- SEARCH-DERIVED: citations are **Arabic numerals in square brackets** — "[1]", "[1,2]", "[2–4]" — cited in **ascending order of appearance** in the text. MDPI's reference list styles are based on **ACS** (used by most MDPI journals, including engineering/CS titles), with Chicago- and APA-based variants for some journals. Free-format submission tolerates any consistent style at initial submission.
- Project constraint (governance, not journal): reference entries come ONLY from the 57-key locked corpus `papers/governance/allowed_citation_keys.txt` / `papers/references.bib`.
- VERIFY-BEFORE-SUBMISSION: confirm which of the three MDPI style variants *Algorithms* mandates at production.

## 5. Figures and tables

- SEARCH-DERIVED (MDPI-level): figures and tables must be inserted in the main text near first citation, each with a caption; "Figures and Tables with Captions" is a required manuscript component.
- UNKNOWN (journal-specific specifics not retrievable through the 403 block): exact minimum resolution (MDPI commonly asks approximately 1000 px width / 300 dpi at production) and accepted image file formats for *Algorithms*. Do NOT rely on the parenthetical common values — VERIFY-BEFORE-SUBMISSION on the live instructions page.

## 6. Supplementary materials

- SEARCH-DERIVED: authors are **encouraged to publish all observations related to the submitted manuscript as Supplementary Material**; *Algorithms* requires that authors **publish all experimental controls and make full datasets available where possible**.
- Project binding: the supplement carries extended tables, full per-function results, full convergence curves, reproducibility detail, and the **ablation study (Phase-12, supplement-only; DEFERRED_TO_PHASE_12_SUPPLEMENT_ONLY)** — no ablation content in the main manuscript.
- UNKNOWN: accepted supplementary file types/size limits and whether deposition in an external repository (e.g., Zenodo) is preferred over journal-hosted files. VERIFY-BEFORE-SUBMISSION.

## 7. Data availability and required declarations

- SEARCH-DERIVED: MDPI back matter requires the declaration blocks: **Author Contributions; Funding; Data Availability Statement; Conflicts of Interest;** plus, where applicable, Institutional Review Board Statement and Informed Consent Statement (not applicable to this computational study — state "Not applicable" if the template requires the block).
- SEARCH-DERIVED (journal-specific): *Algorithms* requires publishing all experimental controls and making full datasets available where possible — consistent with this project's release-anchored evidence plan (release rel-2026-07-10-262fc16c9, to be cited in the Data Availability Statement in later phases).
- VERIFY-BEFORE-SUBMISSION: exact current wording/ordering of mandatory declaration sections for *Algorithms*.

## 8. Peer-review model / anonymization

- SEARCH-DERIVED: MDPI's process is **single-blind for most journals**, with **optional open peer review** (authors may opt to publish review reports and their responses alongside the paper; reviewers may optionally sign). No manuscript anonymization requirement was found for *Algorithms*.
- VERIFY-BEFORE-SUBMISSION: confirm *Algorithms*' current model on the live page (MDPI has piloted double-blind on some titles); if double-blind, an anonymized build would be required — treat as a change request if so.

## 9. APC (factual note only)

- SEARCH-DERIVED (MDPI APC listing referenced as "as of July 2026" and the journal APC page): APC for *Algorithms* is **CHF 1800** per accepted paper; payable in CHF, EUR, USD, GBP, JPY, or CAD. Open access: free for readers; APC paid by authors/institutions.
- VERIFY-BEFORE-SUBMISSION: confirm the current APC and any waiver/discount status at submission time.

## 10. Other factual notes (SEARCH-DERIVED)

- Journal operating stats quoted for H1 2026: median first decision approximately 17.6 days; acceptance-to-publication approximately 3.9 days. Informational only; not a requirement.
- MDPI originality/preprint policy (general): submissions must be original and not under consideration elsewhere; posting to preprint servers is permitted. VERIFY the journal-specific wording before submission.

## 11. Re-verification checklist (blocking before submission)

1. Fetch https://www.mdpi.com/journal/algorithms/instructions in a browser; confirm sections 1–10 above and flip this record to verified_online=true (new access date).
2. Confirm no journal-specific page cap (Section 2) — else re-bind the Section 1.5 rule to the published cap and update `page_budget.md`.
3. Confirm peer-review model (Section 8) and template currency (Section 3).
4. Confirm APC (Section 9) and declaration block list (Section 7).
