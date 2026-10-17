"""Build a broken pipeline bundle from a scenario spec.

    python -m evals.inject f1_date_format --mode silent [-p to_format=%m/%d/%Y] [--out out/scenarios]

Writes:
    <out>/<case>/bundle/        what the agent gets: code, data, logs, problem statement
    <out>/<case>/ground_truth.json   the answer key, kept OUTSIDE the bundle
"""

import os
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path

import polars as pl
import typer
import yaml

from demo_pipeline.generate import generate
from evals.faults import FAULTS, describe
from evals.models import GroundTruth, Mode, Scenario

REPO = Path(__file__).resolve().parent.parent
SCENARIOS = REPO / "evals" / "scenarios"

PROBLEMS = {
    "crash": "The nightly orders pipeline failed on its latest run. It had been running "
    "fine before. Find the root cause and propose a fix.",
    "silent": "The nightly orders pipeline reports success, but the post-load data-quality "
    "checks are failing and the daily revenue numbers look wrong. Find the root cause "
    "and propose a fix.",
}


def load_scenario(scenario_id: str) -> Scenario:
    return Scenario.model_validate(yaml.safe_load((SCENARIOS / f"{scenario_id}.yaml").read_text()))


def case_name(scenario: Scenario, mode: Mode, overrides: dict[str, str]) -> str:
    parts = [scenario.id, mode] + [f"{k}-{v}" for k, v in sorted(overrides.items())]
    return "__".join("".join(c if c.isalnum() or c in "-_" else "" for c in p) for p in parts)


def run(cmd: list[str], cwd: Path, log: Path, env: dict[str, str] | None = None) -> int:
    # No .pyc files: they embed absolute paths, which would leak the case name.
    env = {**os.environ, **(env or {}), "PYTHONDONTWRITEBYTECODE": "1"}
    with log.open("w") as fh:
        return subprocess.run(cmd, cwd=cwd, env=env, stdout=fh, stderr=subprocess.STDOUT).returncode


def build(scenario: Scenario, mode: Mode, overrides: dict[str, str], out: Path) -> Path:
    if mode not in scenario.modes:
        raise typer.BadParameter(f"{scenario.id} supports modes {scenario.modes}, not {mode}")
    fault = scenario.fault.model_copy(update={"params": {**scenario.fault.params, **overrides}})
    start = date.fromisoformat(scenario.start_partition)

    case_dir = out / case_name(scenario, mode, overrides)
    if case_dir.exists():
        shutil.rmtree(case_dir)
    bundle = case_dir / "bundle"

    # Code: a copy of the demo pipeline, with strict_parsing set by the mode.
    shutil.copytree(
        REPO / "demo_pipeline",
        bundle / "demo_pipeline",
        ignore=shutil.ignore_patterns("data", "__pycache__", "generate.py"),
    )
    cfg_path = bundle / "demo_pipeline" / "pipeline" / "config.yaml"
    cfg_path.write_text(
        cfg_path.read_text().replace("strict_parsing: true", f"strict_parsing: {str(mode == 'crash').lower()}")
    )

    # Data: last_good = clean files before the fault; current = all files, broken from `start`.
    clean = generate(case_dir / "_clean")
    current, last_good = bundle / "data" / "current", bundle / "data" / "last_good"
    current.mkdir(parents=True)
    last_good.mkdir(parents=True)
    first_bad = None
    for src in clean:
        day = date.fromisoformat(src.stem.removeprefix("orders_"))
        if day < start:
            shutil.copy(src, last_good / src.name)
            shutil.copy(src, current / src.name)
        else:
            first_bad = first_bad or src.name
            df = pl.read_csv(src, infer_schema=False)
            FAULTS[fault.type](df, fault).write_csv(current / src.name)
    shutil.rmtree(case_dir / "_clean")

    # Logs: run the pipeline on last_good and current, then the quality checks.
    logs = bundle / "logs"
    logs.mkdir()
    py = [sys.executable, "-m", "demo_pipeline.pipeline.run"]
    run(py + ["--data", "data/last_good", "--db", "warehouse/last_good.duckdb"], bundle, logs / "last_good_run.log")
    exit_code = run(py + ["--data", "data/current", "--db", "warehouse/current.duckdb"], bundle, logs / "pipeline.log")
    tests_passed = None
    if exit_code == 0:
        test_rc = run(
            [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "demo_pipeline/tests"],
            bundle,
            logs / "quality_tests.log",
            env={"WAREHOUSE": "warehouse/current.duckdb", "DATA_DIR": "data/current"},
        )
        tests_passed = test_rc == 0

    # Tracebacks contain the absolute bundle path, which includes the case name and would
    # leak the answer. Rewrite it to /workspace, where the sandbox mounts the bundle.
    for cache in bundle.rglob("__pycache__"):
        shutil.rmtree(cache)
    for log_file in logs.iterdir():
        log_file.write_text(log_file.read_text().replace(str(bundle.resolve()), "/workspace"))

    (bundle / "problem.md").write_text(PROBLEMS[mode] + "\n")

    truth = GroundTruth(
        scenario_id=scenario.id,
        mode=mode,
        failure_class=scenario.failure_class,
        affected_columns=[fault.column],
        first_bad_partition=first_bad,
        fault=fault,
        root_cause=" ".join(
            scenario.root_cause.format(**fault.params, **describe(fault), first_bad_partition=first_bad).split()
        ),
        pipeline_exit_code=exit_code,
        quality_tests_passed=tests_passed,
    )
    (case_dir / "ground_truth.json").write_text(truth.model_dump_json(indent=2) + "\n")
    return case_dir


def main(
    scenario_id: str = typer.Argument(..., help="Scenario file name without .yaml"),
    mode: str = typer.Option("crash", help="crash | silent"),
    param: list[str] = typer.Option([], "-p", help="Override a fault param: key=value"),
    out: Path = typer.Option(Path("out/scenarios"), help="Output root"),
) -> None:
    overrides = dict(p.split("=", 1) for p in param)
    case_dir = build(load_scenario(scenario_id), mode, overrides, out)  # type: ignore[arg-type]
    truth = GroundTruth.model_validate_json((case_dir / "ground_truth.json").read_text())
    typer.echo(f"bundle:       {case_dir / 'bundle'}")
    typer.echo(f"ground truth: {case_dir / 'ground_truth.json'}")
    typer.echo(f"pipeline exit={truth.pipeline_exit_code} quality_tests_passed={truth.quality_tests_passed}")


if __name__ == "__main__":
    typer.run(main)
