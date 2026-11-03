"""Why did fixes fail? Reads each failed run's final checkpoint and tallies its feedback.

    python -m evals.fix_failures [--agent graph/nemotron-3-ultra-550b-a55b]

The suite rows say *that* a fix failed; the checkpoints say *why* (every rejected proposal
and failed validation is in `fix_feedback`). This is error analysis: before improving the
fixer, find out which failure dominates.
"""

import asyncio
import json
from collections import Counter, defaultdict
from pathlib import Path

import typer

from etl_doctor.graph.build import _config, open_graph

OUT = Path("out/suite")
CATEGORIES = {  # first match wins, checked in this order
    "edit did not apply (old_text not copied exactly / not whole lines)": ["occurs 0 times", "must be complete lines"],
    "edit broke the file (does not parse)": ["does not parse", "SyntaxError"],
    "wrong file: header check in extract.py still rejects the renamed column": ["header mismatch"],
    "polars API misuse (crashes on the new data)": ["polars", "strptime", "to_date"],
    "old data broken (regression on last_good)": ["pipeline_runs_last_good", "quality_tests_last_good"],
    "loads, but values wrong (quality tests fail)": ["quality_tests_current"],
    "rows lost": ["no_rows_lost"],
    "other": [""],
}


def categorize(feedback: str) -> str:
    return next(c for c, keys in CATEGORIES.items() if any(k in feedback for k in keys))


async def collect(agent: str) -> list[tuple[str, list[str]]]:
    out = []
    for line in (OUT / "results.jsonl").read_text().splitlines():
        r = json.loads(line)
        if r["agent"] != agent or r.get("fix_validated") or not r.get("fix_attempts") or not r.get("run_id"):
            continue
        db = OUT / "checkpoints" / f"{r['run_id']}.sqlite"
        if not db.exists():
            continue
        async with open_graph(db) as app:
            v = (await app.aget_state(_config(r["run_id"]))).values
        out.append((r["case"], v.get("fix_feedback", [])))
    return out


def main(agent: str = typer.Option("graph/nemotron-3-ultra-550b-a55b")) -> None:
    runs = asyncio.run(collect(agent))
    per_attempt, per_scenario = Counter(), defaultdict(Counter)
    for case, feedback in runs:
        for f in feedback:
            c = categorize(f)
            per_attempt[c] += 1
            per_scenario[case.split("__")[0]][c] += 1
    typer.echo(f"{len(runs)} runs whose fix never validated; {sum(per_attempt.values())} failed attempts\n")
    typer.echo("| Why the attempt failed | Attempts |\n|---|---|")
    for c, n in per_attempt.most_common():
        typer.echo(f"| {c} | {n} |")
    typer.echo("")
    for sc, cnt in sorted(per_scenario.items()):
        typer.echo(f"{sc}: " + ", ".join(f"{c.split(' (')[0]} {n}" for c, n in cnt.most_common()))


if __name__ == "__main__":
    typer.run(main)
