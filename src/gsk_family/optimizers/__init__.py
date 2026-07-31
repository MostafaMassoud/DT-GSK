"""Optimizer registry for the GSK family and the external SOTA baselines."""

from __future__ import annotations

#: The seven-method GSK family. This is the panel every statistical claim in the
#: manuscript is computed over; do not add external baselines here.
FAMILY_OPTIMIZER_IDS = (
    "gsk",
    "agsk",
    "apgsk",
    "atmals-gsk",
    "egsk",
    "fdb-agsk",
    "dt-gsk",
)

#: External SOTA baselines, runnable but NOT part of the family panel. Vendored /
#: implemented so the CEC2013LSGO comparison can be run first-party under this
#: project's protocol instead of citing published means. See
#: ``gsk_family.optimizers.external``.
EXTERNAL_OPTIMIZER_IDS = (
    # large-scale specialists (CEC2013LSGO regime)
    "mos-cec2013lsgo",
    "shade-ils",
    "decc-g",
    # bound-constrained SOTA (CEC2017 lineage; also runnable on CEC2011/CEC2013)
    "cmaes",
    "ebowithcmar",
    "jso",
    "lshade",
    "lshade-spacma",
)

#: Everything the runner will accept. Kept in sync with
#: ``run_experiment.OPTIMIZER_FUNCTIONS`` by ``tests/test_registry_consistency.py``
#: -- these two lists having drifted apart is exactly what made a registered
#: optimizer fail at the CLI with "Unsupported optimizer(s)".
OPTIMIZER_IDS = FAMILY_OPTIMIZER_IDS + EXTERNAL_OPTIMIZER_IDS
