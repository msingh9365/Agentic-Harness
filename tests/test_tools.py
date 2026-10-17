"""Step 2 tools and agent loop, offline: real edtools on a real bundle, scripted fake model."""

import asyncio
import json
from pathlib import Path

import pytest
from pydantic_ai.messages import ModelMessage, ModelResponse, ToolCallPart, ToolReturnPart
from pydantic_ai.models.function import AgentInfo, FunctionModel

from etl_doctor.executor import LocalExecutor
from etl_doctor.investigate import investigate
from evals.inject import build, load_scenario


@pytest.fixture(scope="module")
def cases(tmp_path_factory) -> dict[str, Path]:
    out = tmp_path_factory.mktemp("cases")
    return {
        sid: build(load_scenario(sid), "silent", {}, out) / "bundle"
        for sid in ["f1_date_format", "f3_column_rename", "f4_type_drift"]
    }


def edtools(bundle: Path, cmd: str, **args):
    return asyncio.run(LocalExecutor(bundle).edtools(cmd, args))


def test_diff_schema_detects_each_fault(cases):
    args = {"current": "data/current/orders_2026-10-14.csv", "last_good": "data/last_good/orders_2026-10-13.csv"}
    f1 = edtools(cases["f1_date_format"], "diff_schema", **args)["result"]
    assert [c["column"] for c in f1["format_changes"]] == ["order_date"]
    assert f1["format_changes"][0]["after"]["formats"][0]["format"] == "%d/%m/%Y"

    f3 = edtools(cases["f3_column_rename"], "diff_schema", **args)["result"]
    assert f3["rename_candidates"][0] == {"from": "customer_id", "to": "cust_id", "score": f3["rename_candidates"][0]["score"]}

    f4 = edtools(cases["f4_type_drift"], "diff_schema", **args)["result"]
    assert f4["format_changes"][0]["column"] == "amount"
    assert f4["format_changes"][0]["after"]["formats"][0]["format"] == "comma_decimal"


def test_sql_shows_rows_lost_per_file(cases):
    q = "SELECT source_file, count(*) FROM warehouse_current GROUP BY 1 ORDER BY 1"
    rows = edtools(cases["f1_date_format"], "run_sql", query=q)["result"]["rows"]
    assert [r[0] for r in rows][-1] == "orders_2026-10-13.csv"  # nothing loaded from the 14th on


@pytest.mark.parametrize(
    ("cmd", "args"),
    [
        ("read_file", {"path": "../../../../etc/passwd"}),
        ("profile", {"path": "/etc/passwd"}),
        ("run_sql", {"query": "SELECT * FROM read_csv('/etc/passwd')"}),
        ("run_sql", {"query": "SELECT 1; COPY current_orders TO 'x.csv'"}),
        ("run_sql", {"query": "WITH x AS (SELECT 1) SELECT * FROM read_text('/etc/hostname')"}),
    ],
)
def test_tools_stay_inside_the_bundle(cases, cmd, args):
    assert "error" in edtools(cases["f1_date_format"], cmd, **args)


def test_agent_loop_records_evidence_and_rejects_invented_ids(cases):
    """Fake model: calls diff_schema, then cites an ID that doesn't exist, then the real one."""
    bundle = cases["f1_date_format"]
    step = iter(range(10))

    def respond(messages: list[ModelMessage], info: AgentInfo) -> ModelResponse:
        n = next(step)
        if n == 0:
            args = {"current": "data/current/orders_2026-10-14.csv", "last_good": "data/last_good/orders_2026-10-13.csv"}
            return ModelResponse(parts=[ToolCallPart("diff_schema", json.dumps(args))])
        returned = [p for m in messages for p in m.parts if isinstance(p, ToolReturnPart) and p.tool_name == "diff_schema"]
        real_id = returned[0].content["evidence_id"]
        answer = {
            "failure_class": "F1",
            "summary": "order_date format changed.",
            "root_cause": "order_date became DD/MM/YYYY from orders_2026-10-14.csv.",
            "affected_columns": ["order_date"],
            "first_bad_partition": "orders_2026-10-14.csv",
            "suggested_fix": "Accept both formats.",
            "confidence": 0.9,
            "evidence_ids": ["ev-999"] if n == 1 else [real_id],
        }
        return ModelResponse(parts=[ToolCallPart(info.output_tools[0].name, json.dumps(answer))])

    seen = []
    r = asyncio.run(investigate(bundle, FunctionModel(respond), on_evidence=seen.append))

    assert [e.tool for e in seen] == ["diff_schema"]
    assert r.diagnosis.evidence_ids == ["ev-001"]
    assert r.retries == 1
    assert "order_date" in r.cited()[0].summary


def test_bad_path_is_rejected_before_anything_runs(cases):
    calls = iter([("read_file", {"path": "/etc/passwd"})])

    def respond(messages: list[ModelMessage], info: AgentInfo) -> ModelResponse:
        try:
            name, args = next(calls)
            return ModelResponse(parts=[ToolCallPart(name, json.dumps(args))])
        except StopIteration:
            raise RuntimeError("stop")  # end the run; we only care about the first call

    seen = []
    with pytest.raises(RuntimeError, match="stop"):
        asyncio.run(investigate(cases["f1_date_format"], FunctionModel(respond), on_evidence=seen.append))
    assert seen == []
