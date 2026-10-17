"""Every scenario x mode x variant must produce the intended symptom, and must not leak the answer."""

import subprocess
import sys
from pathlib import Path

import pytest

from demo_pipeline.generate import generate
from evals.inject import SCENARIOS, build, load_scenario
from evals.models import GroundTruth


def cases():
    for path in sorted(SCENARIOS.glob("*.yaml")):
        sc = load_scenario(path.stem)
        for mode in sc.modes:
            for key, values in sc.variants.items():
                for value in values:
                    yield pytest.param(sc.id, mode, {key: str(value)}, id=f"{sc.id}-{mode}-{value}")


@pytest.mark.parametrize(("scenario_id", "mode", "overrides"), list(cases()))
def test_scenario_produces_symptom(tmp_path: Path, scenario_id, mode, overrides):
    sc = load_scenario(scenario_id)
    case_dir = build(sc, mode, overrides, tmp_path)
    bundle = case_dir / "bundle"
    truth = GroundTruth.model_validate_json((case_dir / "ground_truth.json").read_text())

    assert "run SUCCEEDED" in (bundle / "logs" / "last_good_run.log").read_text()
    if mode == "crash":
        assert truth.pipeline_exit_code != 0
        assert truth.quality_tests_passed is None
    else:
        assert truth.pipeline_exit_code == 0
        assert truth.quality_tests_passed is False
    assert truth.first_bad_partition == f"orders_{sc.start_partition}.csv"

    # The agent only ever sees `bundle/`; nothing in it may reveal the scenario.
    assert not (bundle / "ground_truth.json").exists()
    needles = [sc.id, sc.fault.type, "ground_truth", str(tmp_path)]
    for f in bundle.rglob("*"):
        if f.is_file() and f.suffix != ".duckdb":
            text = f.read_text(errors="ignore")
            assert not any(n in text for n in needles), f"{f.relative_to(bundle)} leaks scenario info"
    assert not list(bundle.rglob("__pycache__"))


def test_clean_data_passes_quality_checks(tmp_path: Path):
    repo = Path(__file__).resolve().parent.parent
    data, db = tmp_path / "data", tmp_path / "w.duckdb"
    generate(data)
    run = [sys.executable, "-m", "demo_pipeline.pipeline.run", "--data", str(data), "--db", str(db)]
    assert subprocess.run(run, cwd=repo).returncode == 0
    tests = [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "demo_pipeline/tests"]
    env = {"WAREHOUSE": str(db), "DATA_DIR": str(data), "PYTHONDONTWRITEBYTECODE": "1"}
    assert subprocess.run(tests, cwd=repo, env=env).returncode == 0
