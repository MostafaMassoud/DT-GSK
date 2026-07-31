"""External SOTA baselines, vendored for first-party benchmarking.

These exist so comparisons against the state of the art can be RUN under this
project's own harness -- identical objective code, seed schedule, budget and
protocol as the GSK family -- instead of quoting published tables measured on
other hardware, other implementations and (for CEC2013LSGO's Ackley functions)
a different objective variant.

All are vendored byte-faithfully from ``05-Human-Inspired-Family_Python_v0.1``,
where they carry parity records under ``docs/development/matlab_parity/``; only
the import namespace was rewritten. The single exception is ``decc_g``, which is
first-party code written here against Yang, Tang & Yao (2008) and has NO
author-code oracle -- see ``docs/development/DECC_G_port_record.md``.

**None of these belongs to the seven-method GSK-family statistical panel.**
``gsk_family.optimizers.EXTERNAL_OPTIMIZER_IDS`` keeps that boundary explicit.

Suite applicability
-------------------
``mos-cec2013lsgo`` and ``shade-ils`` are large-scale specialists built for
CEC2013LSGO. ``decc-g`` is a cooperative-coevolution method for the same regime.
``cmaes``, ``ebowithcmar``, ``jso``, ``lshade`` and ``lshade-spacma`` target the
bound-constrained suites (CEC2017 lineage) and also run on CEC2011/CEC2013.
CMA-ES carries an O(D^2)-O(D^3) covariance update, so it is impractical at
D = 1000 and should not be launched on CEC2013LSGO without a cost check first.
"""

from gsk_family.optimizers.external.cmaes import optimize as optimize_cmaes
from gsk_family.optimizers.external.decc_g import optimize as optimize_decc_g
from gsk_family.optimizers.external.ebowithcmar import optimize as optimize_ebowithcmar
from gsk_family.optimizers.external.jso import optimize as optimize_jso
from gsk_family.optimizers.external.lshade import optimize as optimize_lshade
from gsk_family.optimizers.external.lshade_spacma import optimize as optimize_lshade_spacma
from gsk_family.optimizers.external.mos_cec2013lsgo import optimize as optimize_mos
from gsk_family.optimizers.external.shade_ils import optimize as optimize_shade_ils

__all__ = [
    "optimize_cmaes",
    "optimize_decc_g",
    "optimize_ebowithcmar",
    "optimize_jso",
    "optimize_lshade",
    "optimize_lshade_spacma",
    "optimize_mos",
    "optimize_shade_ils",
]
