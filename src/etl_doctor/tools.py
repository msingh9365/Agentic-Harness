"""The read-only tools the investigating agent can call.

Tool design rules (each one is here because of something that broke or could break):
- Docstrings and Args sections are the tool's documentation *for the model*; PydanticAI
  sends them as the tool description and parameter descriptions.
- No zero-argument tools: the smoke test showed Nemotron Super's endpoint sends the wrong
  arguments to them. Every tool has at least one (defaulted) parameter.
- Paths are validated before anything runs; bad args come back as a validation error the
  model can correct.
- Errors from bad arguments are returned as data ({"error": ...}) so the model can adapt,
  instead of raising and spending the retry budget.
- Every successful call becomes Evidence with an ID the model must cite.
- Results are size-capped, so one call can't flood the context window.
"""

import json
from dataclasses import dataclass
from pathlib import PurePosixPath
from typing import Annotated, Any

from pydantic import AfterValidator, Field
from pydantic_ai import RunContext
from pydantic_ai.toolsets import FunctionToolset

from etl_doctor.evidence import EvidenceStore
from etl_doctor.executor import Executor

MAX_RESULT_CHARS = 8_000


def _relative(p: str) -> str:
    pp = PurePosixPath(p)
    if pp.is_absolute() or ".." in pp.parts:
        raise ValueError("use a path relative to the bundle root, without '..', e.g. data/current")
    return p


RelPath = Annotated[str, AfterValidator(_relative)]


@dataclass
class AgentDeps:
    executor: Executor
    evidence: EvidenceStore
    current_files: list[str]


def _bounded(data: Any) -> Any:
    text = json.dumps(data, default=str)
    if len(text) <= MAX_RESULT_CHARS:
        return data
    return {"truncated": True, "chars": len(text), "preview": text[:MAX_RESULT_CHARS]}


async def _call(ctx: RunContext[AgentDeps], command: str, args: dict[str, Any], summarize) -> dict[str, Any]:
    out = await ctx.deps.executor.edtools(command, args)
    if "error" in out:
        return {"error": out["error"]}
    data = _bounded(out["result"])
    ev = ctx.deps.evidence.add(command, args, summarize(out["result"]), data)
    return {"evidence_id": ev.id, "result": data}


readonly_tools = FunctionToolset[AgentDeps]()


@readonly_tools.tool
async def list_files(ctx: RunContext[AgentDeps], directory: RelPath = ".") -> dict[str, Any]:
    """List a directory in the bundle. For CSV files also shows the header line and row count.

    Args:
        directory: e.g. "." (bundle root), "logs", "data/current", "data/last_good".
    """

    def summary(r):
        headers = {e.get("header") for e in r["entries"] if "header" in e}
        return f"{len(r['entries'])} entries in {r['directory']}; {len(headers)} distinct CSV header(s)"

    return await _call(ctx, "list_files", {"directory": directory}, summary)


@readonly_tools.tool
async def read_file(
    ctx: RunContext[AgentDeps], path: RelPath, start_line: int = 1, max_lines: Annotated[int, Field(le=300)] = 120
) -> dict[str, Any]:
    """Read lines of a text file (code, config, logs, CSV) with line numbers.

    Args:
        path: e.g. "demo_pipeline/pipeline/config.yaml", "logs/pipeline.log".
        start_line: first line to return (1-based).
        max_lines: how many lines to return, at most 300.
    """
    args = {"path": path, "start_line": start_line, "max_lines": max_lines}
    return await _call(ctx, "read_file", args, lambda r: f"{r['path']} from line {start_line} ({r['total_lines']} lines total)")


@readonly_tools.tool
async def grep_logs(ctx: RunContext[AgentDeps], pattern: str, path: RelPath = "logs") -> dict[str, Any]:
    """Search log files for a case-insensitive regex. Returns matching lines with file and line number.

    Args:
        pattern: Python regex, e.g. "error|fail|traceback".
        path: a .log file or a directory searched recursively for *.log files.
    """
    return await _call(ctx, "grep_logs", {"pattern": pattern, "path": path}, lambda r: f"{r['total_matches']} log lines match /{pattern}/")


@readonly_tools.tool
async def profile_dataset(ctx: RunContext[AgentDeps], path: RelPath, columns: list[str] | None = None) -> dict[str, Any]:
    """Profile one CSV file, reading every value as a string. Per column: null count, distinct
    count, example values, the most common value shapes (digits as 9, letters as A/a, e.g.
    "99/99/9999") and which known date/number formats match, with match percentages.

    Args:
        path: one CSV file, e.g. "data/current/orders_2026-10-14.csv".
        columns: only these columns; all columns if omitted.
    """

    def summary(r):
        shapes = ", ".join(f"{c['name']}={c['shapes'][0]['shape'] if c['shapes'] else 'empty'}" for c in r["columns"])
        return f"{r['path']}: {r['rows']} rows; dominant shapes: {shapes}"

    return await _call(ctx, "profile", {"path": path, "columns": columns}, summary)


@readonly_tools.tool
async def column_by_file(ctx: RunContext[AgentDeps], column: str, directory: RelPath = "data/current") -> dict[str, Any]:
    """For ONE column, one row per CSV file in a directory: whether the column exists, its
    dominant value shape, the best-matching date/number format and an example value.
    The fastest way to find the FIRST file where a column changes: one call covers every file.

    Args:
        column: e.g. "order_date".
        directory: e.g. "data/current".
    """

    def summary(r):
        def cell(f):
            # Format name, not shape: amounts like 99.99 and 999.99 differ in shape, not format.
            if not f["present"]:
                return f"{f['file']}: missing"
            if f["best_format"]:
                return f"{f['file']}: {f['best_format']['format']}"
            return f"{f['file']}: {f['shape']['shape'] if f['shape'] else 'empty'}"

        # Collapse runs of identical shapes so the summary shows where it changes.
        parts, prev = [], None
        for f in r["files"]:
            key = cell(f).split(": ", 1)[1]
            if key != prev:
                parts.append(cell(f))
                prev = key
        return f"{r['column']} by file: " + "; ".join(parts)

    return await _call(ctx, "column_by_file", {"column": column, "directory": directory}, summary)


@readonly_tools.tool
async def diff_schema(ctx: RunContext[AgentDeps], current: RelPath, last_good: RelPath) -> dict[str, Any]:
    """Compare two CSV files: added and dropped columns, likely renames (with a score), and
    columns whose value format changed (dominant shape and matching formats, before and after).

    Args:
        current: the suspect file, e.g. "data/current/orders_2026-10-14.csv".
        last_good: a known good file, e.g. "data/last_good/orders_2026-10-13.csv".
    """

    def summary(r):
        parts = [f"added={r['added']}", f"dropped={r['dropped']}"]
        parts += [f"rename {x['from']}->{x['to']} ({x['score']})" for x in r["rename_candidates"][:2]]
        parts += [f"{c['column']}: {c['before']['shape']} -> {c['after']['shape']}" for c in r["format_changes"]]
        return f"{r['current']} vs {r['last_good']}: " + "; ".join(parts)

    return await _call(ctx, "diff_schema", {"current": current, "last_good": last_good}, summary)


@readonly_tools.tool
async def run_sql(ctx: RunContext[AgentDeps], query: str) -> dict[str, Any]:
    """Run one read-only DuckDB SELECT over these tables (at most 50 rows returned):
    current_orders, last_good_orders: every CSV row as raw strings plus source_file;
    warehouse_current, warehouse_last_good: rows the pipeline actually loaded (typed), plus source_file.
    Comparing raw rows with loaded rows per source_file shows where rows were lost.

    Args:
        query: e.g. "SELECT source_file, count(*) FROM warehouse_current GROUP BY 1 ORDER BY 1".
    """
    return await _call(ctx, "run_sql", {"query": query}, lambda r: f"{len(r['rows'])} row(s), columns {r['columns']}: {query[:120]}")
