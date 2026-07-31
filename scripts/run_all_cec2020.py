"""Run the CEC2020 campaign: the seven-method family panel, unified seeds.

Extra arguments are forwarded to the runner, so the documented campaign line

    python scripts/run_all_cec2020.py --workers 14

behaves exactly like

    python run.py --config configs/family_cec2020.yml --workers 14

Until 2026-07-28 this wrapper pointed at ``configs/agsk_cec2020.yml``, which
then carried ``seed_policy: reference``. Invoking it would have written
AGSK rows seeded off the reference schedule into the shared output tree, where
they would have looked valid while being unpairable with every other optimizer.
Repointed under CR-0019; the AGSK config is now a unified-seed subset of this
one.

``--workers`` is worth passing explicitly: the runner's default worker count is
2 (``gsk_family.runners.parallel.default_worker_count``).
"""

from __future__ import annotations

import sys

from gsk_family.cli.run import main

CONFIG = "configs/family_cec2020.yml"


if __name__ == "__main__":
    raise SystemExit(main(["--config", CONFIG, "--root", ".", *sys.argv[1:]]))
