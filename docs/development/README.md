# Development Docs

> **What this folder is.** The living guides for people working *on* this package —
> reading, changing, extending, and maintaining the code — plus the reference for the
> proposed method's locked core and its evidence re-run runbook, the EGSK port decision
> record, and the performance-acceleration campaign docs. Start with the guide that matches
> your task; the user-facing pages for *running* experiments are under
> [`docs/getting-started/`](../getting-started/user_guide.md).

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

## Where the evidence lives

It is **not** in this folder — no documentation page holds run data. Every paper number
resolves from the promoted, read-only evidence tree `benchmarks/cec_reference_results/`,
navigated through its `_index/BENCHMARK_EVIDENCE_INDEX.md`; each suite cell is bound by a
self-verifying manifest (release id, per-file SHA-256, seed schedule, and generating
command). Derived statistics live under `papers/analysis/<release-id>/`.
