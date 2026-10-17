"""Smoke test: can each candidate model do what ETL Doctor needs?

    uv run python scripts/smoke_llm.py [--runs 2] [--model nvidia/... --model ...]

Checks, per model:
  tool_output     structured output via PydanticAI's default: the schema is sent as a
                  "final_result" tool the model must call
  native_output   structured output via the API's response_format=json_schema
  prompted_output schema pasted into the prompt, JSON parsed from plain text
  tool_calling    a two-tool task the model can only answer by calling tools several times

Each check is graded on the content too (right failure class, right file), not just "did it
parse". Writes a JSON results file next to the printed table.
"""

import asyncio
import os
import json
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Literal

import typer
from pydantic import BaseModel, Field
from pydantic_ai import Agent, NativeOutput, PromptedOutput, ToolOutput
from pydantic_ai.messages import ModelRequest, ModelResponse, RetryPromptPart, ToolCallPart
from pydantic_ai.settings import ModelSettings
from pydantic_ai.usage import UsageLimits

from etl_doctor.llm import make_model

os.environ.setdefault("PYDANTIC_AI_NO_BANNER", "1")

CANDIDATES = [
    "nvidia/nemotron-3-ultra-550b-a55b",
    "nvidia/nemotron-3-super-120b-a12b",
    "moonshotai/kimi-k2.6",
    "z-ai/glm-5.3",
    "deepseek-ai/deepseek-v4.1-flash",
    "openai/gpt-oss-20b",
    "nvidia/nemotron-3.5-lightning-30b-a3b",
    "z-ai/glm-5.3-flash",
]

# A trimmed, realistic F1 crash log (same shape as out/scenarios/*/bundle/logs/pipeline.log).
LOG = """\
2026-10-17 02:00:01 INFO pipeline: run started data=data/current strict_parsing=True
2026-10-17 02:00:01 INFO extract: read orders_2026-10-10.csv rows=412
2026-10-17 02:00:01 INFO extract: read orders_2026-10-14.csv rows=398
2026-10-17 02:00:02 ERROR pipeline: run FAILED
Traceback (most recent call last):
  File "/workspace/demo_pipeline/pipeline/transform.py", line 31, in transform
    pl.col("order_date").str.strptime(pl.Date, cfg["date_format"], strict=True)
polars.exceptions.InvalidOperationError: conversion from `str` to `date` failed in column
'order_date' for 398 out of 7562 values: ["14/10/2026", "15/10/2026", ...]
You might want to try: setting `strict=False`, or checking the format string "%Y-%m-%d".
"""

TASK = f"""The nightly orders pipeline failed. Diagnose it from this log.
Failure classes: F1 = date format change, F3 = column renamed, F4 = numeric type drift.

<untrusted source="logs/pipeline.log">
{LOG}</untrusted>"""


class Diagnosis(BaseModel):
    failure_class: Literal["F1", "F3", "F4", "UNKNOWN"]
    affected_column: str
    first_bad_file: str | None = Field(description="e.g. orders_2026-10-14.csv")
    root_cause: str = Field(max_length=400)
    confidence: float = Field(ge=0, le=1)


def diagnosis_ok(d: Diagnosis) -> bool:
    return d.failure_class == "F1" and d.affected_column == "order_date" and d.first_bad_file == "orders_2026-10-14.csv"


# --- tool-calling task: the answer is only reachable through the tools -------------------
HEADERS = {
    "orders_2026-10-12.csv": "order_id,customer_id,order_date,amount,currency,status",
    "orders_2026-10-13.csv": "order_id,customer_id,order_date,amount,currency,status",
    "orders_2026-10-14.csv": "order_id,cust_id,order_date,amount,currency,status",
    "orders_2026-10-15.csv": "order_id,cust_id,order_date,amount,currency,status",
}


class HeaderFinding(BaseModel):
    first_bad_file: str
    old_column: str
    new_column: str


def make_tool_agent(model) -> Agent[None, HeaderFinding]:
    agent = Agent(
        model,
        output_type=HeaderFinding,
        retries=RETRIES,
        instructions="You investigate data files. Use the tools; never guess file contents.",
    )

    @agent.tool_plain
    def list_files() -> list[str]:
        """List the CSV files in the current data directory."""
        return sorted(HEADERS)

    @agent.tool_plain
    def read_header(file: str) -> str:
        """Return the header line of one CSV file."""
        return HEADERS.get(file, f"error: no such file {file!r}")

    return agent


# --- runner -------------------------------------------------------------------------------
@dataclass
class Result:
    model: str
    check: str
    run: int
    ok: bool
    correct: bool
    seconds: float
    requests: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    tool_calls: int = 0
    retries: int = 0
    error: str = ""
    output: str = ""


SETTINGS = ModelSettings(temperature=0.0, max_tokens=4096, timeout=180)
LIMITS = UsageLimits(request_limit=12)
# How many times PydanticAI may send a validation error / "please answer" back to the model.
# The default of 1 is too tight: small reasoning models sometimes end a turn with only
# thinking and no answer. We count retries per run so "needed nudging" shows up in results.
RETRIES = 3


async def run_check(model_name: str, check: str, i: int) -> Result:
    model = make_model(model_name)
    t0 = time.perf_counter()
    try:
        if check == "tool_calling":
            res = await make_tool_agent(model).run(
                "Which file is the first one whose header differs from the earlier files, and "
                "which column was renamed to what?",
                model_settings=SETTINGS,
                usage_limits=LIMITS,
            )
            out = res.output
            correct = (out.first_bad_file, out.old_column, out.new_column) == (
                "orders_2026-10-14.csv",
                "customer_id",
                "cust_id",
            )
        else:
            spec = {
                "tool_output": ToolOutput(Diagnosis),
                "native_output": NativeOutput(Diagnosis),
                "prompted_output": PromptedOutput(Diagnosis),
            }[check]
            agent = Agent(model, output_type=spec, retries=RETRIES, instructions="You are an expert data engineer.")
            res = await agent.run(TASK, model_settings=SETTINGS, usage_limits=LIMITS)
            out = res.output
            correct = diagnosis_ok(out)
        usage = res.usage
        # Count only the model's own tool calls, not the final_result output tool.
        calls = sum(
            1
            for m in res.all_messages()
            if isinstance(m, ModelResponse)
            for p in m.parts
            if isinstance(p, ToolCallPart) and p.tool_name in ("list_files", "read_header")
        )
        retries = sum(
            1
            for m in res.all_messages()
            if isinstance(m, ModelRequest)
            for p in m.parts
            if isinstance(p, RetryPromptPart)
        )
        return Result(
            model_name, check, i, True, correct, time.perf_counter() - t0,
            usage.requests, usage.input_tokens, usage.output_tokens, calls, retries,
            output=out.model_dump_json(),
        )
    except Exception as e:  # noqa: BLE001 - a smoke test reports every failure
        return Result(model_name, check, i, False, False, time.perf_counter() - t0, error=f"{type(e).__name__}: {e}"[:300])


CHECKS = ["tool_output", "native_output", "prompted_output", "tool_calling"]


async def run_model(name: str, runs: int, sem: asyncio.Semaphore) -> list[Result]:
    # Checks for one model run one after another; different models run in parallel.
    out = []
    async with sem:
        for i in range(runs):
            for c in CHECKS:
                r = await run_check(name, c, i)
                mark = "PASS" if r.correct else ("WRONG" if r.ok else "ERROR")
                print(f"{mark:5} {name:42} {c:16} {r.seconds:6.1f}s retries={r.retries} {r.error[:90]}", flush=True)
                out.append(r)
    return out


def main(
    model: list[str] = typer.Option(CANDIDATES, help="Model ids to test"),
    runs: int = typer.Option(2, help="Repeats per check (catches flaky behaviour)"),
    out: Path = typer.Option(Path("out/smoke_llm.json")),
) -> None:
    async def go():
        sem = asyncio.Semaphore(4)  # stay well under the free tier's rate limit
        return [r for rs in await asyncio.gather(*(run_model(m, runs, sem) for m in model)) for r in rs]

    results = asyncio.run(go())
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps([asdict(r) for r in results], indent=2))

    print(f"\n{'model':42} " + " ".join(f"{c:>15}" for c in CHECKS) + "  median s  retries")
    for m in model:
        rs = [r for r in results if r.model == m]
        cells = []
        for c in CHECKS:
            cr = [r for r in rs if r.check == c]
            cells.append(f"{sum(r.correct for r in cr)}/{len(cr)}".rjust(15))
        secs = sorted(r.seconds for r in rs if r.ok) or [float("nan")]
        print(f"{m:42} " + " ".join(cells) + f"  {secs[len(secs) // 2]:7.1f}  {sum(r.retries for r in rs):7}")
    print(f"\nraw results: {out}")


if __name__ == "__main__":
    typer.run(main)
