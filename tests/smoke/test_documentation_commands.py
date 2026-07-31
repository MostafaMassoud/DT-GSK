from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _pythonpath_env() -> dict[str, str]:
    env = os.environ.copy()
    entries = [str(PROJECT_ROOT / "src"), str(PROJECT_ROOT)]
    existing = env.get("PYTHONPATH")
    if existing:
        entries.append(existing)
    env["PYTHONPATH"] = os.pathsep.join(entries)
    return env


def _run_module(*args: str, timeout: int = 60) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", *args],
        cwd=PROJECT_ROOT,
        env=_pythonpath_env(),
        text=True,
        capture_output=True,
        timeout=timeout,
        check=False,
    )


def test_documented_docs_exist() -> None:
    docs = [
        "README.md",
        "SKILL.md",
        "MANIFEST.in",
        "docs/prompt/project-review.md",
        "docs/prompt/documentation-review.md",
        "docs/prompt/documentation-deep-upgrade.md",
        "docs/prompt/publication-polish.md",
        "docs/index.md",
        "docs/LICENSES.md",
        "docs/getting-started/user_guide.md",
        "docs/getting-started/tutorial.md",
        "docs/getting-started/runbook.md",
        "docs/getting-started/configuration.md",
        "docs/reference/api.md",
        "docs/reference/architecture.md",
        "docs/reference/module_dependencies.md",
        "docs/reference/python_optimizer_interface.md",
        "docs/reference/benchmark_protocol.md",
        "docs/reference/benchmark_mapping.md",
        "docs/reference/diagrams.md",
        "docs/reference/result_schema.md",
        "docs/reference/seed_policy.md",
        "docs/reference/fp_regime.md",
        "docs/research/numerical_examples.md",
        "docs/research/statistical_analysis.md",
        "docs/research/performance.md",
        "docs/research/validation_report.md",
        "docs/research/reproducibility.md",
        "docs/development/developer_guide.md",
        "docs/algorithms/gsk.md",
        "docs/algorithms/agsk.md",
        "docs/algorithms/apgsk.md",
        "docs/algorithms/fdb-agsk.md",
        "docs/algorithms/atmals-gsk.md",
        "docs/html/index.html",
        "docs/html/api_index.html",
        "docs/html/prompt_documentation-review.html",
        "docs/html/api/gsk_family.optimizers.gsk.html",
        "docs/html/reference_diagrams.html",
        "docs/html/research_numerical_examples.html",
        "docs/html/assets/site.css",
        "docs/html/assets/search.js",
        "docs/html/search_index.json",
        "configs/README.md",
        "configs/smoke.yml",
        "configs/all_optimizers_smoke.yml",
        "configs/all_optimizers_cec2017_reduced.yml",
        "configs/golden_validation_smoke.yml",
        "configs/performance_campaign_smoke.yml",
        "scripts/README.md",
        "src/README.md",
        "src/gsk_family/README.md",
        "src/gsk_family/common/README.md",
        "src/gsk_family/optimizers/README.md",
        "src/gsk_family/runners/README.md",
        "scripts/build_docs_html.py",
    ]

    for relative_path in docs:
        assert (PROJECT_ROOT / relative_path).exists(), relative_path


def test_documented_list_and_validate_commands_are_callable() -> None:
    listed = _run_module(
        "gsk_family.cli.list",
        "--optimizers",
        "--benchmarks",
        "--references",
        "benchmarks/cec_reference_results",
    )
    assert listed.returncode == 0, listed.stderr
    assert "gsk" in listed.stdout
    assert "cec2017" in listed.stdout

    validated = _run_module(
        "gsk_family.cli.validate",
        "--references",
        "benchmarks/cec_reference_results",
    )
    assert validated.returncode == 0, validated.stderr
    assert "reference root:" in validated.stdout


def test_canonical_runner_wrappers_show_cli_help() -> None:
    for relative_path in ("run.py", "scripts/run_gsk_family.py"):
        command = subprocess.run(
            [sys.executable, str(PROJECT_ROOT / relative_path), "--help"],
            cwd=PROJECT_ROOT,
            env=_pythonpath_env(),
            text=True,
            capture_output=True,
            timeout=30,
            check=False,
        )

        assert command.returncode == 0, command.stderr
        assert "Run GSK-family Python experiments." in command.stdout


def test_documented_direct_run_command_writes_result_schema(tmp_path: Path) -> None:
    output_root = tmp_path / "results"
    command = _run_module(
        "gsk_family.cli.run",
        "--optimizer",
        "gsk",
        "--suite",
        "sphere",
        "--dimension",
        "4",
        "--function",
        "1",
        "--runs",
        "1",
        "--seed",
        "20240620",
        "--seed-policy",
        "unified",
        "--rand-generator",
        "threefry",
        "--max-evaluations",
        "80",
        "--output-root",
        str(output_root),
        "--reference-root",
        str(tmp_path / "references"),
        "--data-root",
        str(tmp_path / "cec_suite_python"),
        "--convergence-graphs",
        "--overwrite",
    )

    assert command.returncode == 0, command.stderr
    root = output_root / "gsk" / "sphere"
    assert "==================== run_all (SPHERE) ====================" in command.stdout
    assert "DETAILED CONFIGURATION" in command.stdout
    assert f"Saved 1 convergence graph(s) to {root / 'curves' / 'graphs'}" in command.stdout
    assert "PASS  GSK" in command.stdout
    assert "==================== done ====================" in command.stdout

    summary = root / "summary"
    assert (summary / "per_run.csv").exists()
    assert (summary / "seed_schedule.csv").exists()
    assert (summary / "environment.json").exists()
    assert (summary / "run_config.json").exists()
    assert (summary / "phase0_protocol.json").exists()
    assert (summary / "verification.json").exists()
    assert list(summary.glob("gsk_D4_log_*.txt"))
    assert list(summary.glob("gsk_D4_runs_log_*.txt"))
    assert (root / "gen_logs" / "CheckpointErrors_gsk_F1_D4.csv").exists()
    assert list((root / "curves" / "graphs").glob("Figure_F1_D4.png"))


def test_direct_run_omits_convergence_graphs_without_flag(tmp_path: Path) -> None:
    output_root = tmp_path / "results"
    command = _run_module(
        "gsk_family.cli.run",
        "--optimizer",
        "gsk",
        "--suite",
        "sphere",
        "--dimension",
        "4",
        "--function",
        "1",
        "--runs",
        "1",
        "--seed",
        "20240620",
        "--max-evaluations",
        "80",
        "--output-root",
        str(output_root),
        "--reference-root",
        str(tmp_path / "references"),
        "--data-root",
        str(tmp_path / "cec_suite_python"),
        "--overwrite",
    )

    assert command.returncode == 0, command.stderr
    root = output_root / "gsk" / "sphere"
    assert "Saved 1 convergence graph(s)" not in command.stdout
    assert not list((root / "curves" / "graphs").glob("Figure_F1_D4.png"))
    assert list((root / "curves").glob("Figure_F1_D4_Run#*.csv"))


def test_html_documentation_generator_rebuilds_site(tmp_path: Path) -> None:
    output_root = tmp_path / "docs" / "html"
    command = subprocess.run(
        [
            sys.executable,
            str(PROJECT_ROOT / "scripts" / "build_docs_html.py"),
            "--docs-root",
            str(PROJECT_ROOT / "docs"),
            "--source-root",
            str(PROJECT_ROOT / "src" / "gsk_family"),
            "--output-root",
            str(output_root),
        ],
        cwd=PROJECT_ROOT,
        env=_pythonpath_env(),
        text=True,
        capture_output=True,
        timeout=60,
        check=False,
    )

    assert command.returncode == 0, command.stderr
    assert "Markdown pages:" in command.stdout
    assert "API modules:" in command.stdout
    assert (output_root / "index.html").exists()
    assert (output_root / "api_index.html").exists()
    assert (output_root / "reference_diagrams.html").exists()
    assert (output_root / "api" / "gsk_family.optimizers.gsk.html").exists()


def test_generated_html_local_links_resolve() -> None:
    html_root = PROJECT_ROOT / "docs" / "html"
    pattern = re.compile(r"""(?:href|src)=["']([^"']+)["']""")
    missing: list[str] = []

    for page in sorted(html_root.rglob("*.html")):
        for target in pattern.findall(page.read_text(encoding="utf-8")):
            if (
                not target
                or target.startswith("#")
                or re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", target)
            ):
                continue
            path_part = target.split("#", 1)[0]
            if not path_part:
                continue
            resolved = (page.parent / path_part).resolve()
            if not resolved.exists():
                missing.append(f"{page.relative_to(PROJECT_ROOT)} -> {target}")

    assert not missing, "Broken generated HTML links:\n" + "\n".join(missing)
