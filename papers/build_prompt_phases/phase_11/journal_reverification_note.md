# Phase 11 — Target-Journal Reverification Note

- **Date:** 2026-07-11
- **Task:** Phase 11 task 1 — confirm the target journal is unchanged since Phase 4; record access note.
- **Scope note:** No **new** online venue verification is required at Phase 11 — the venue is
  author-ratified (user decision 2026-07-10, "use the current plan's target"). This note records the
  unchanged status and the outstanding author-side live-page re-verification.

## 1. Verdict

**UNCHANGED.** The target journal remains **MDPI *Algorithms*** (article type Article), exactly as
frozen at Phase 4 (decision **D-0010**, `papers/governance/decision_log.md`;
`papers/governance/project_configuration.md` Section 4; `phase_04/journal_decision.md`). No change
request in `papers/governance/change_request_register.csv` has re-opened the venue since Phase 4.

## 2. Repository wiring re-checked (2026-07-11)

| Check | Result |
|---|---|
| MDPI class vendored | `papers/Definitions/mdpi.cls` present |
| Documentclass / journal option | `\documentclass[algorithms,article,submit,moreauthors,pdftex]{Definitions/mdpi}` — main.tex **line 9** |
| Line-number note | Config Section 4 cites "line 5"; the documentclass is now line 9, shifted only by the Phase-8 header comment block. Content is identical — journal option `algorithms` and class `Definitions/mdpi` unchanged. |
| Built title banner | Both PDFs render "submitted to *Algorithms*" (page header). |

## 3. Access note (recorded per task)

- **Phase-4 access:** 2026-07-10. The official Instructions-for-Authors page
  (`https://www.mdpi.com/journal/algorithms/instructions`) returned **HTTP 403 Forbidden** to the
  automated fetcher (`verified_online = false`, `phase_04/journal_requirements.md`).
- **Phase-11 access:** no new fetch attempted (author-ratified; MDPI blocks non-browser clients, so a
  retry adds no evidence). The Phase-4 requirements record remains the authoritative venue-rules
  snapshot.
- **Enforceable page limit:** MDPI publishes no fixed length cap for *Algorithms* (contact-the-office
  band ~3,000–12,000 words); under framework Section 1.5 the limit therefore binds to the self-imposed
  `page_budget.md` budget — **B1 ≤ 34 pp**, re-measured PASS this phase (B1 = 32; see
  `final_primary_integrity_audit.md` §10).

## 4. Outstanding author-side item (non-blocking)

`verified_online = false` carries forward as an **author pre-submission step**: re-verify the live
official Instructions page (length cap, peer-review model, template currency, APC, declaration blocks,
figure resolution/format) in a browser and reconcile any discrepancy via change request — not via
silent edit. This does not block the Phase-11 content freeze.

## 5. Related deferral (already dispositioned)

**R-0004** (cover-letter venue mismatch) was **resolved-pending-author** at Phase 9: `cover_letter.*`
was rewritten for MDPI *Algorithms* (CL-01 → READY, `phase_09/PHASE_9_gate_report.md`); the stale
Swarm-and-Evolutionary-Computation copy is retained only as `cover_letter_STALE_swevo.pdf`.
