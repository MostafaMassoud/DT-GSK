"""Run a default CEC2013LSGO GSK experiment."""

from __future__ import annotations

from gsk_family.cli.run import main


if __name__ == "__main__":
    raise SystemExit(
        main(
            [
                "--optimizer",
                "gsk",
                "--suite",
                "cec2013lsgo",
                "--functions",
                "1",
                "--dimensions",
                "1000",
                "--runs",
                "1",
                "--max-evaluations",
                "1000",
                "--root",
                ".",
                "--output-root",
                "results",
                "--overwrite",
            ]
        )
    )

