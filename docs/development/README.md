# Development Docs

> **What this folder is.** The living guides for people working *on* this package —
> reading, changing, extending, and maintaining the code — plus the reference for the
> proposed method's locked core and its evidence re-run runbook, the EGSK port decision
> record, and the performance-acceleration campaign docs. Start with the guide that matches
> your task; the user-facing pages for *running* experiments are under
> [`docs/getting-started/`](../getting-started/user_guide.md). The folder also holds
> thirteen **historical records** — executed campaign plans, closed bug and adjudication
> records, and review records — indexed in their own section at the bottom; they are dated
> evidence, not current guidance.

## Guides

| Page | One-line purpose |
| --- | --- |
| [Code Reading Guide](code_reading_guide.md) | Guided tour of the source tree, in dependency order. |
| [Developer Guide](developer_guide.md) | Day-to-day reference: setup, layout, test tiers, workers, analysis suite. |
| [Extension Guide](extension_guide.md) | Recipes for adding an optimizer, suite, artifact, or CLI command. |
| [Contributor Guide](contributor_guide.md) | The submission checklist: gates, docs expectations, evidence policy. |
| [Maintenance Guide](maintenance_guide.md) | Recurring health checks, dependency bumps, reference-evidence care. |

## The proposed method (DT-GSK)

| Page | One-line purpose |
| --- | --- |
| [DT-GSK Core Reference](dt_gsk_core_reference.md) | **Read before touching `optimizers/_dt_*`.** The vendored core, the byte-identity lock, the six tests that hold it, the dimension tiers, determinism at `D >= 50`, and the facts that are routinely got wrong. |
| [Evidence Re-run Runbook](evidence_rerun_runbook.md) | Regenerating the `D >= 50` evidence after a core behavior change: affected-cell inventory, exact commands, and the manuscript edits that must follow. |

## Decision records

| Page | One-line purpose |
| --- | --- |
| [EGSK Port Spec](egsk_port_spec.md) | Why the EGSK comparator is a Python port whose `fmincon` refinement is substituted by SciPy SLSQP, and why byte-identity with the original was infeasible. Reviewers ask about this; the algorithm guide is [algorithms/egsk.md](../algorithms/egsk.md). |

## Acceleration campaign

| Page | One-line purpose |
| --- | --- |
| [Acceleration Campaign Prompt](ACCELERATION_CAMPAIGN_PROMPT.md) | Method and governance for the GSK-family speed campaign — the R1/R2/R3 risk ladder, the evidence-freeze constraint, and the priced options. Paused behind manuscript remediation; RT-001 comparator re-timing is CLOSED (executed, failed its determinism gate, not adopted), so the campaign has no live evidence item. |
| [Sibling-Campaign Transfer](SIBLING_CAMPAIGN_TRANSFER.md) | Which accelerations proven in the human-inspired sibling project transfer here, ranked by expected value and paired with their governance cost. |

## Historical records and executed campaign plans (retained as dated evidence, not current guidance)

**Read nothing below as a description of the project's current state.** These
thirteen pages are dated evidence: campaign plans that were executed and closed,
bug and adjudication records whose fixes have shipped, port and incident
records, and the review records. Their status lines were true on the dates they
carry. For the current state read
[`REVISION_STATUS.md`](../../REVISION_STATUS.md), the `phase` field of
`papers/governance/main_manuscript_freeze_manifest.json`, and the newest entry
in `papers/governance/decision_log.md`. Nothing here is deleted or "fixed
forward" — the dates are the point.

| Page | Status |
| --- | --- |
| [Paper Completion Plan](PAPER_COMPLETION_PLAN.md) | Executed and superseded. Drove the five-suite manuscript to its v2.0 freeze; the manuscript has since advanced through several further freeze passes. |
| [Final Publication Plan](FINAL_PUBLICATION_PLAN.md) | Executed, partially superseded. The nine-phase four/five-suite publication programme of 2026-07-28; its inter-lens rulings (R1-R7) remain in force unless a later governance record supersedes them. |
| [Reference Promotion Plan](REFERENCE_PROMOTION_PLAN.md) | Executed 2026-07-28/29. Produced releases `lsgo-rel-2026-07-28-ff1a046ef` and `cec2020-rel-2026-07-29-5867abe1e`; every target it lists now exists. |
| [CEC2013LSGO Integration Campaign](LSGO_INTEGRATION_CAMPAIGN.md) | Executed. The work-sequencing plan for bringing CEC2013LSGO into the manuscript, including the external-baseline comparison. An internal quality-assurance instrument, not the journal's peer review. |
| [Family Acceleration Plan](FAMILY_ACCELERATION_PLAN.md) | CLOSED 2026-07-25 under CR-0013..CR-0017. The bit-identical family-wide speed campaign, 7 algorithms x 5 suites; supersedes the campaign-state sections of the LSGO plan below. |
| [LSGO Acceleration Plan](LSGO_ACCELERATION_PLAN.md) | CLOSED 2026-07-25, superseded by the Family Acceleration Plan. Its resume table and "next action" work order are historical; its measured lessons (T1 rejection, budget scaling, the worker knee, the probe traps) remain authoritative. |
| [Port-05 Tuning Triage](PORT_05_TUNING_TRIAGE.md) | Read-only audit, 2026-07-26. Verdict: nothing to port — this project's own acceleration campaign had already closed that ground. No code changed. |
| [BUG-RESUME-01: resume summary truncation](BUG_resume_summary_truncation.md) | FIXED 2026-07-25 under CR-0012. Resume mode truncated and mis-computed the per-dimension summary CSV for all 7 algorithms and all 5 suites; `per_run.csv` was never affected and stays authoritative. |
| [CEC2017-PREC adjudication](CEC2017_PREC_adjudication.md) | CLOSED 2026-07-25. Adjudicates the frozen CEC2017 summary-precision flag: 340 mismatched fields across all 28 files, every one falling into one of three explained signatures; none unexplained. |
| [DECC-G Port Record](DECC_G_port_record.md) | Standing fidelity record. `decc-g` is implemented and paper-faithful but has **no author-code oracle**, unlike the vendored MOS and SHADE-ILS. Read before any DECC-G number goes into the manuscript. |
| [Round-One Review Record](round_one_review_record.md) | The public record of the round-one review of `algorithms-4507562`: what was asked, what was done, and where the evidence went against the manuscript. Deliberately carries no reviewer sentence, report detail, or attribution (D-0049). |
| [Acceptance-Readiness Review 2026-08-28](acceptance_readiness_review_2026_08_28.md) | Executed output of [`prompt/change-register-acceptance-review.md`](../prompt/change-register-acceptance-review.md) at pass-50 / v2.23; its five surviving findings were fixed and tagged as pass-51 / v2.24. |
| [GitHub Exposure and Traffic Record](github_exposure_traffic_record.md) | Incident record. How long seven copyrighted third-party PDFs were served from the public remote, and what GitHub's rolling 14-day traffic counters saw before they expired. The incident itself is `papers/governance/decision_log.md` D-0049. |

## Where the evidence lives

It is **not** in this folder — no documentation page holds run data. Every paper number
resolves from the promoted, read-only evidence tree `benchmarks/cec_reference_results/`,
navigated through its `_index/BENCHMARK_EVIDENCE_INDEX.md`; each suite cell is bound by a
self-verifying manifest (release id, per-file SHA-256, seed schedule, and generating
command). Derived statistics live under `papers/analysis/<release-id>/`.
