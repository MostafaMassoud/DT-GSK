"""Run the CEC2011 configured experiment."""

from __future__ import annotations

from gsk_family.cli.run import main


if __name__ == "__main__":
    raise SystemExit(main(["--config", "configs/all_cec2011.yml", "--root", "."]))

