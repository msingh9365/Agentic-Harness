"""A scripted stand-in for the LLM that plays every graph role, for offline tests.

It recognises the role from the output schema it is asked to fill, makes one sensible tool
call where the role has tools, and answers using the evidence IDs the tools returned.
"""

import json

from pydantic_ai.messages import ModelMessage, ModelResponse, TextPart, ToolCallPart, ToolReturnPart
from pydantic_ai.models.function import AgentInfo, FunctionModel


def _evidence_ids(messages: list[ModelMessage]) -> list[str]:
    return [p.content["evidence_id"] for m in messages for p in m.parts
            if isinstance(p, ToolReturnPart) and isinstance(p.content, dict) and "evidence_id" in p.content]


# Fixes the fixer role can propose. "good" handles both date formats; "regress" switches the
# config to the new format only (breaks the old files); "forbidden" edits a test file.
STRPTIME = '        pl.col("order_date").str.strptime(pl.Date, cfg["date_format"], strict=strict),'
FIXES = {
    "good": [{"path": "demo_pipeline/pipeline/transform.py", "old_text": STRPTIME, "new_text":
              '        pl.coalesce(pl.col("order_date").str.strptime(pl.Date, "%Y-%m-%d", strict=False), '
              'pl.col("order_date").str.strptime(pl.Date, "%d/%m/%Y", strict=False)).alias("order_date"),'}],
    "regress": [{"path": "demo_pipeline/pipeline/config.yaml", "old_text": 'date_format: "%Y-%m-%d"',
                 "new_text": 'date_format: "%d/%m/%Y"'}],
    "forbidden": [{"path": "demo_pipeline/tests/test_quality.py", "old_text": "def test_every_source_file_loaded",
                   "new_text": "def _skip_every_source_file_loaded"}],
}


def make_brain(confidence: float = 0.9, verdict: str = "confirmed", fixes: list[str] | None = None,
               stubborn_verifier: bool = False) -> FunctionModel:
    """`fixes`: what the fixer proposes on each call, in order (the last one repeats).
    `stubborn_verifier`: the verifier never stops calling tools, so its budget runs out."""
    fix_plan = list(fixes or ["good"])
    fixer_calls = {"n": 0}

    def respond(messages: list[ModelMessage], info: AgentInfo) -> ModelResponse:
        # Tool output: the answer is a call to an output tool. Native output (the fixer): the
        # answer is JSON text matching a schema, the way response_format=json_schema works.
        native = info.model_request_parameters.output_object
        out = None if native else info.output_tools[0]
        schema = native.json_schema if native else out.parameters_json_schema
        fields = set(schema.get("properties", {}))
        ids = _evidence_ids(messages)

        def answer(data: dict) -> ModelResponse:
            if native:
                return ModelResponse(parts=[TextPart(json.dumps(data))])
            return ModelResponse(parts=[ToolCallPart(out.name, json.dumps(data))])

        def call(tool: str, args: dict) -> ModelResponse:
            return ModelResponse(parts=[ToolCallPart(tool, json.dumps(args))])

        if "symptom" in fields:
            return answer({"symptom": "rows lost", "run_outcome": "succeeded_with_bad_data",
                           "candidate_classes": ["F1"], "suspect_columns": ["order_date"],
                           "first_checks": ["column_by_file order_date"]})
        if "findings" in fields:
            if not ids:
                return call("column_by_file", {"column": "order_date"})
            return answer({"findings": [f"{ids[0]} shows order_date changes format at orders_2026-10-14.csv"]})
        if "hypotheses" in fields:
            # The prompt lists the evidence; cite the first ID it mentions.
            text = " ".join(str(p.content) for m in messages for p in m.parts if hasattr(p, "content"))
            first = next(w for w in text.replace("\n", " ").split() if w.startswith("ev-"))
            return answer({"hypotheses": [{
                "id": "h1", "failure_class": "F1", "statement": "order_date became DD/MM/YYYY from orders_2026-10-14.csv",
                "affected_columns": ["order_date"], "first_bad_partition": "orders_2026-10-14.csv",
                "evidence_ids": [first], "confidence": confidence,
                "falsification_check": "count rows per file with '/' in order_date", "suggested_fix": "accept both formats",
            }], "next_checks": ["profile orders_2026-10-14.csv"]})
        if "outcome" in fields:
            if stubborn_verifier:
                if info.function_tools:
                    return call("run_sql", {"query": f"SELECT count(*) FROM current_orders -- {len(ids)}"})
                # The verdict agent (no tools) sees the checks in its prompt: cite the last one.
                text = " ".join(str(p.content) for m in messages for p in m.parts if hasattr(p, "content"))
                ids = [w.strip("[]():,") for w in text.split() if w.startswith("ev-")]
            if not ids:
                return call("run_sql", {"query": "SELECT source_file, count(*) FROM current_orders WHERE order_date LIKE '%/%' GROUP BY 1"})
            return answer({"hypothesis_id": "h1", "outcome": verdict, "observations": "as predicted", "evidence_ids": [ids[-1]]})
        if "edits" in fields:
            kind = fix_plan[min(fixer_calls["n"], len(fix_plan) - 1)]
            fixer_calls["n"] += 1
            return answer({"hypothesis_id": "h1", "edits": FIXES[kind], "rationale": f"{kind} fix",
                           "blast_radius": "order_date parsing only", "expected_effects": ["all files load"],
                           "rollback": "revert the edit", "confidence": 0.8})
        raise AssertionError(f"unexpected output schema {fields}")

    return FunctionModel(respond)
