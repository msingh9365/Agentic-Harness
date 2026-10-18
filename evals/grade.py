"""Diagnose one injected case and score it against its answer key.

    python -m evals.grade out/scenarios/f1_date_format__silent [--model ...]

Lives in evals/, not in the agent package: only the grader may read ground_truth.json.
"""

import asyncio
import json
import time
from pathlib import Path

import typer
from pydantic_ai.exceptions import UnexpectedModelBehavior, UsageLimitExceeded

from etl_doctor.diagnose import diagnose
from etl_doctor.investigate import investigate, investigate_in_sandbox
from etl_doctor.domain import DiagnosisCore
from etl_doctor.llm import STRONG_MODEL
from evals.models import GroundTruth


def grade(d: DiagnosisCore, truth: GroundTruth) -> dict[str, bool]:
    return {
        "failure_class": d.failure_class.value == truth.failure_class,
        # Extra columns are tolerated (e.g. naming both customer_id and cust_id for a rename).
        "affected_columns": set(truth.affected_columns) <= set(d.affected_columns),
        "first_bad_partition": d.first_bad_partition == truth.first_bad_partition,
    }


def main(
    case_dir: Path = typer.Argument(..., exists=True, file_okay=False),
    model: str = typer.Option(STRONG_MODEL),
    no_tools: bool = typer.Option(False, "--no-tools", help="Grade the Step 1 baseline instead"),
    graph: bool = typer.Option(False, "--graph", help="Grade the Step 4 graph (checkpointed, with verification)"),
    sandbox: str = typer.Option("e2b", help="e2b or local"),
) -> None:
    truth = GroundTruth.model_validate_json((case_dir / "ground_truth.json").read_text())
    t0 = time.perf_counter()
    if graph:
        return grade_graph(case_dir, truth, sandbox, t0)
    run = diagnose if no_tools else investigate_in_sandbox if sandbox == "e2b" else investigate
    agent = "no_tools" if no_tools else f"tools/{sandbox}"
    try:
        r = asyncio.run(run(case_dir / "bundle", model))
    except (UsageLimitExceeded, UnexpectedModelBehavior) as e:
        # Out of budget or retries: a failed case, not a crashed eval. Step 4 turns this
        # into an explicit "escalate to a human" outcome.
        typer.echo(json.dumps({"case": case_dir.name, "model": model, "agent": agent, "correct": False,
                               "error": f"{type(e).__name__}: {str(e)[:200]}",
                               "seconds": round(time.perf_counter() - t0, 1)}))
        raise typer.Exit(1)
    scores = grade(r.diagnosis, truth)
    typer.echo(r.diagnosis.model_dump_json(indent=2))
    typer.echo(json.dumps({
        "case": case_dir.name,
        "model": model,
        "agent": agent,
        "correct": all(scores.values()),
        **scores,
        "retries": r.retries,
        "tool_calls": r.usage.tool_calls,
        "sandbox_seconds": getattr(r, "sandbox_seconds", None),
        "input_tokens": r.usage.input_tokens,
        "output_tokens": r.usage.output_tokens,
        "seconds": round(time.perf_counter() - t0, 1),
    }))


def grade_graph(case_dir: Path, truth: GroundTruth, sandbox: str, t0: float) -> None:
    from etl_doctor.graph.build import start_run

    s = asyncio.run(start_run(case_dir / "bundle", sandbox))
    r = s.report
    scores = grade(r.diagnosis, truth) if r.diagnosis else {k: False for k in ("failure_class", "affected_columns", "first_bad_partition")}
    if r.diagnosis:
        typer.echo(r.diagnosis.model_dump_json(indent=2))
    typer.echo(json.dumps({
        "case": case_dir.name,
        "agent": f"graph/{sandbox}",
        "run_id": s.run_id,
        "status": r.status,
        # An escalation is not a wrong answer, but it is not a diagnosis either.
        "correct": r.status == "diagnosed" and all(scores.values()),
        **scores,
        "investigations": s.investigations,
        "verifications": s.verifications,
        "tool_calls": r.usage.tool_calls,
        "input_tokens": r.usage.input_tokens,
        "output_tokens": r.usage.output_tokens,
        "seconds": round(time.perf_counter() - t0, 1),
        "terminal_reason": r.terminal_reason,
    }))


if __name__ == "__main__":
    typer.run(main)
