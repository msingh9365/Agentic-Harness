"""A scripted stand-in for the LLM that plays every graph role, for offline tests.

It recognises the role from the output schema it is asked to fill, makes one sensible tool
call where the role has tools, and answers using the evidence IDs the tools returned.
"""

import json

from pydantic_ai.messages import ModelMessage, ModelResponse, ToolCallPart, ToolReturnPart
from pydantic_ai.models.function import AgentInfo, FunctionModel


def _evidence_ids(messages: list[ModelMessage]) -> list[str]:
    return [p.content["evidence_id"] for m in messages for p in m.parts
            if isinstance(p, ToolReturnPart) and isinstance(p.content, dict) and "evidence_id" in p.content]


def make_brain(confidence: float = 0.9, verdict: str = "confirmed") -> FunctionModel:
    def respond(messages: list[ModelMessage], info: AgentInfo) -> ModelResponse:
        out = info.output_tools[0]
        fields = set(out.parameters_json_schema.get("properties", {}))
        ids = _evidence_ids(messages)

        def answer(data: dict) -> ModelResponse:
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
            if not ids:
                return call("run_sql", {"query": "SELECT source_file, count(*) FROM current_orders WHERE order_date LIKE '%/%' GROUP BY 1"})
            return answer({"hypothesis_id": "h1", "outcome": verdict, "observations": "as predicted", "evidence_ids": [ids[-1]]})
        raise AssertionError(f"unexpected output schema {fields}")

    return FunctionModel(respond)
