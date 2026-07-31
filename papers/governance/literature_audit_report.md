# Literature audit report — Phase 1 (closed corpus)

> **SUPERSEDED IN PART — do not read this report as current on `awad2016problem`.**
> Every finding below that declares `awad2016problem` inadmissible, blocked, or
> intentionally absent from the role map was **superseded by CR-0005 / decision
> D-0009 (2026-07-10)**, which admitted the correct 34-page Awad et al. (2016) NTU
> CEC2017 definitions report. The key is now `verified` and `admissible`, carries a
> full evidence card, holds a B.4 row in `citation_role_map.csv` (added under SE-025,
> 2026-07-22), and is un-blocked for Word source generation via
> `build_docx.py CITATION_BLOCK_OVERRIDES`. This report is retained unedited below as
> the dated Phase-1 record; `decision_log.md` D-0009 and `evidence_gap_register.md`
> are authoritative for the current state.

Date: 2026-07-10. Anchor commit `262fc16c91fbe5608a1a0b0c5df3cbcd009edc21` (Gate 0 FROZEN).
Scope: master framework Phase 1 tasks 1-9; this report closes tasks 6-9 on top of the
task 1-5 outputs (`reference_inventory.csv`, `evidence_cards/`).
Authority: closed corpus only — `reference_papers/*.pdf` + `papers/references.bib`.

## 1. Counts

| Quantity | Count |
|---|---|
| BibTeX entries in `papers/references.bib` | **57** (expected 57; no forcing needed) |
| Duplicate BibTeX keys | 0 |
| Appendix A expected keys | 57 |
| Appendix A keys missing from bib | 0 |
| Bib keys not in Appendix A | 0 |
| `reference_inventory.csv` rows | 57 (every key exactly once) |
| Evidence cards in `evidence_cards/` | 57 (56 full + 1 inadmissible stub) |
| **Runtime admissible set (`allowed_citation_keys.txt`)** | **56** |
| Inadmissible keys | 1 (`awad2016problem`) |
| `citation_role_map.csv` rows | 56 (admissible keys only) |
| `word_citation_tag_map.csv` rows | 57 (56 ready + 1 marked BLOCKED) |
| Evidence gaps seeded (`evidence_gap_register.md`) | 13 (EG-001 ... EG-013) |

## 2. Identity and readability statuses (from `reference_inventory.csv`)

| Status | Count | Keys |
|---|---|---|
| `verified` | 40 | (all remaining keys) |
| `minor_metadata_mismatch` | 16 | jawad2024egsk, mohamed2021novel, jalali2021opposition, apgsk_imode2024, nabahat2024hybrid, zhong2021gskhho, navaneetha2022gskde, liang2024gskwoa, zhou2021iade, arini2022gjojos, hu2022qcsca, awad2017ensemble, kaveh2021pgo, kolda2003directsearch, fialho2010adaptive, jones1995fitness |
| `major_mismatch` | 1 | **awad2016problem — WRONG DOCUMENT, inadmissible, blocked** |

Readability: 55 `readable`; `nelder1965simplex` is `image_only_no_text_layer`
(identity verified visually; no verbatim quotes permitted); `david_order_statistics` is
`partial_text_title_page_only` (12-page excerpt; visual locators, Ch. 7 content only).
All 16 minor mismatches are identity-certain; the mismatch is bib metadata error
(wrong DOI, garbled given names, wrong year, or version/venue difference), each resolved
from the local source in the inventory notes. Every admissible key has exactly one
readable local source and one evidence card; every card locator scheme is pinned to the
local copy's pagination.

## 3. Runtime admissible set vs Appendix A (task 6)

- `allowed_citation_keys.txt` written with the **56 verified keys** (sorted, one per line).
- **Missing expected:** `awad2016problem` — Appendix A expects it in the runtime
  intersection, but the local PDF is the CEC2017 *constrained* competition report
  (Wu/Mallipeddi/Suganthan), not the cited single-objective bound-constrained report
  (Awad/Ali/Liang/Qu/Suganthan, NTU 2016). Excluded; see EG-001 and the stub card.
- **Unexpected extras:** none. The bib, Appendix A, the inventory, and the card set are
  in exact one-to-one correspondence.

## 4. Notable identity resolutions

- **awad2016problem** — the single blocking finding of the audit. Suite-definition
  citations for CEC2017 are blocked (EG-001); interim narrow path documented
  (participant protocol descriptions via `awad2017ensemble` / `brest2017single`).
- **jawad2024egsk** — bib is a @misc preprint placeholder (2024); the local file is the
  PUBLISHED article (Results in Control and Optimization 19 (2025) 100542,
  10.1016/j.rico.2025.100542). Identity confirmed; camera-ready metadata recorded for the
  change-request pipeline (references.bib is a scientific artifact — no Phase 1 edit).
- **mohamed2021novel** — actual publication year 2019 (Swarm Evol. Comput. 50:100455),
  DOI 10.1016/j.swevo.2018.10.006, third author Kamal M. Jambi; bib year/DOI/author wrong.
- **fialho2010adaptive** — GECCO 2008 paper typed as @article, key says 2010, and the
  bib's author order is wrong (source: Da Costa, Fialho, Schoenauer, Sebag). Key frozen.
- **awad2017ensemble** — bib title says "with L-SHADE"; source title is "with Euclidean
  Neighborhood" (LSHADE-cnEpSin). Source title adopted in inventory.
- **apgsk_imode2024, nabahat2024hybrid, arini2022gjojos, hu2022qcsca** — wrong DOIs in
  bib (and multiple wrong given names); corrected from the printed pages.
- **kolda2003directsearch** — bib DOI truncated (missing final digit).
- **Version differences (published identity certain, locators local):**
  `omidvar2014dg` (accepted manuscript), `khalfi2023csm` (author manuscript),
  `wolpert1997nfl` (1996 preprint), `zhou2021iade` (preprint), `nomer2021gskrl` (author
  version), `jones1995fitness` (SFI working paper vs cited ICGA-6),
  `mohamed2020gaining` (online-first without journal pagination). Consolidated as EG-009.

No metadata was completed from memory or the web; all resolutions come from the printed
pages of the local files, and none required editing `papers/references.bib` (bib fixes
are queued for the change-request pipeline).

## 5. Citation role map (task 7)

`citation_role_map.csv` — one row per admissible key with columns:
`citation_key, appendix_b_group, appendix_b_role, sanctioned_uses,
prohibited_overextensions, usage_condition, evidence_card, identity_status, notes`.

- `appendix_b_role` carries the Appendix B sanctioned role verbatim-condensed;
  `sanctioned_uses` / `prohibited_overextensions` carry the evidence-card
  supported/unsupported sections (pipe-separated bullets, traceable to the card).
- **No key is required to appear in final prose** (master Phase 1 task 7). Conditional
  keys are gated in `usage_condition`: `benjamini1995controlling` (only if FDR analyses
  are reported), `david_order_statistics` (only if an order-statistics argument is used),
  `jones1995fitness` (only where fitness-distance reasoning is discussed),
  `efron1993introduction` (BCa as attribution-only), `yao1999evolutionary` (only where
  BSE/heavy-tailed exploration is discussed), all 13 B.2 variant keys and the 7 B.5
  taxonomy keys (verified-mechanism discussion only; no decorative citations).
- `awad2016problem` is intentionally absent from the role map (inadmissible); its
  Word-tag row is marked BLOCKED so no downstream generator can consume it silently.

## 6. Evidence gap register seed (task 8)

13 gaps seeded in `evidence_gap_register.md` under the Section 3.6 schema:

| Gap | Topic | Disposition |
|---|---|---|
| EG-001 | CEC2017 suite-definition citation (wrong local document) | **blocked** (interim narrow) |
| EG-002 | Official CEC competition rankings | narrow |
| EG-003 | BCa bootstrap mechanics (excerpt lacks Ch. 14) | narrow |
| EG-004 | Measured peak-memory cost (no harness/cost record) | additional experiment, else narrow |
| EG-005 | GenLog diagnostic release (0 GenLog files anywhere) | additional experiment, else omit |
| EG-006 | Parametric-sweep release for T21/T22 (staging absent, no tooling) | additional experiment, else omit |
| EG-007 | ACE-as-bandit inheritance claims | narrow (analysis to upgrade) |
| EG-008 | Superiority beyond the family panel / "state of the art" | narrow |
| EG-009 | Locator/version fidelity (10 preprint/excerpt/scan copies) | narrow |
| EG-010 | NFL refinements beyond 1997 | omit |
| EG-011 | EGSK fmincon-vs-SLSQP port equivalence | narrow (provenance check Phase 2) |
| EG-012 | FDB-AGSK 1000·D vs 10,000·D budget comparability | narrow |
| EG-013 | Universal novelty claims from a closed corpus | narrow |

The empirical known gaps (EG-004/005/006) were artifact-verified on 2026-07-10:
no memory harness in `scripts/`, zero `GenLog_*` files in the release or staging, and
`results/dt-gsk/sweeps/` absent with no `parametric/` release subtree.

## 7. Citation-system readiness (task 9)

**LaTeX/BibTeX:** `papers/references.bib` parsed with a strict entry tokenizer
(balanced-brace scan, per-type required-field check, \cite-key safety, LaTeX-hostile
character scan): 57/57 entries parse; **0 problems, 0 warnings** — no duplicate keys, no
missing required fields (article/inproceedings/techreport/book/misc), all keys
\cite-safe, fully ASCII, no unescaped `% & _` or unbalanced `$` in text fields. The file
is safe for LaTeX/BibTeX consumption as-is. (pybtex/bibtexparser are not installed in
this environment; the check is the scripted minimal parse per the execution context.)

**Word:** `word_citation_tag_map.csv` assigns each key a stable Word citation tag under
the deterministic **bibkey-identity scheme** (tag = citation key; all 57 tags match
`^[A-Za-z][A-Za-z0-9_]*$` and are unique, so they are valid, collision-free Word source
tags). Mapping columns cover the Word source store: `bibtex_entry_type` →
`word_source_type` (article→JournalArticle, inproceedings→ConferenceProceedings,
techreport→Report, book→Book, misc→Misc) and the target store
(customXml `b:Sources`/sources.xml, generated in the Word build phase).
**No citations were generated** — the map is inert until the Word-manuscript phase.
The `awad2016problem` row is status `BLOCKED_do_not_generate_word_source`.

## 8. Task 6-9 output inventory

| Artifact | Status |
|---|---|
| `papers/governance/allowed_citation_keys.txt` | written — 56 keys |
| `papers/governance/citation_role_map.csv` | written — 56 rows, 9 columns |
| `papers/governance/evidence_gap_register.md` | seeded — 13 gaps |
| `papers/governance/word_citation_tag_map.csv` | written — 57 rows, 9 columns |
| BibTeX parse validation | pass (0 problems / 0 warnings) |
| `papers/governance/literature_audit_report.md` | this report |

Open item carried forward: resolution of EG-001 (supply the correct Awad et al. 2016
NTU report, re-inventory, replace the stub card, extend the role map and allowed set to
57). Bib metadata corrections (Section 4) remain queued for the change-request pipeline;
no scientific artifact was modified by Phase 1.
