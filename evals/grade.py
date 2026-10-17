"""Diagnose one injected case and score it against its answer key.

    python -m evals.grade out/scenarios/f1_date_format__silent [--model ...]

Lives in evals/, not in the agent package: only the grader may read ground_truth.json.
"""

import asyncio
import json
import time
from pathlib import Path

import typer

from etl_doctor.diagnose import diagnose
from etl_doctor.domain import Diagnosis
from etl_doctor.llm import STRONG_MODEL
from evals.models import GroundTruth


def grade(d: Diagnosis, truth: GroundTruth) -> dict[str, bool]:
    return {
        "failure_class": d.failure_class.value == truth.failure_class,
        # Extra columns are tolerated (e.g. naming both customer_id and cust_id for a rename).
        "affected_columns": set(truth.affected_columns) <= set(d.affected_columns),
        "first_bad_partition": d.first_bad_partition == truth.first_bad_partition,
    }


def main(
    case_dir: Path = typer.Argument(..., exists=True, file_okay=False),
    model: str = typer.Option(STRONG_MODEL),
) -> None:
    truth = GroundTruth.model_validate_json((case_dir / "ground_truth.json").read_text())
    t0 = time.perf_counter()
    r = asyncio.run(diagnose(case_dir / "bundle", model))
    scores = grade(r.diagnosis, truth)
    typer.echo(r.diagnosis.model_dump_json(indent=2))
    typer.echo(json.dumps({
        "case": case_dir.name,
        "model": model,
        "correct": all(scores.values()),
        **scores,
        "retries": r.retries,
        "input_tokens": r.usage.input_tokens,
        "output_tokens": r.usage.output_tokens,
        "seconds": round(time.perf_counter() - t0, 1),
    }))


if __name__ == "__main__":
    typer.run(main)
