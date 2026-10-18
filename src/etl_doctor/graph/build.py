"""Graph wiring, the SQLite checkpointer, and run / resume / history."""

import enum
import inspect
import secrets
import time
from collections.abc import AsyncIterator, Callable
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

from langgraph.checkpoint.serde.jsonplus import JsonPlusSerializer
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import RetryPolicy
from pydantic import BaseModel

from etl_doctor import domain, evidence
from etl_doctor.graph import nodes as n
from etl_doctor.graph import state as st
from etl_doctor.graph.nodes import GraphContext
from etl_doctor.graph.state import Budget, RunState

DB_PATH = Path(".etl_doctor/checkpoints.sqlite")

# Transient failures (provider 5xx/timeouts, sandbox hiccups) get retried by the graph.
# Node logic is idempotent enough for this: a retried node re-runs from the same input state.
LLM_RETRY = RetryPolicy(max_attempts=3, initial_interval=2.0)


def build_graph() -> StateGraph:
    g = StateGraph(RunState, context_schema=GraphContext)
    g.add_node("intake", n.intake)
    g.add_node("provision_sandbox", n.provision_sandbox, retry_policy=LLM_RETRY)
    g.add_node("triage", n.triage, retry_policy=LLM_RETRY)
    g.add_node("investigate", n.investigate, retry_policy=LLM_RETRY)
    g.add_node("hypothesize", n.hypothesize, retry_policy=LLM_RETRY)
    g.add_node("verify", n.verify, retry_policy=LLM_RETRY)
    g.add_node("escalate", n.escalate)
    g.add_node("report", n.report)
    g.add_node("teardown", n.teardown)

    g.add_edge(START, "intake")
    g.add_edge("intake", "provision_sandbox")
    g.add_edge("provision_sandbox", "triage")
    g.add_edge("triage", "investigate")
    g.add_edge("investigate", "hypothesize")
    g.add_conditional_edges("hypothesize", n.route_after_hypothesize, ["investigate", "verify", "escalate"])
    g.add_conditional_edges("verify", n.route_after_verify, ["investigate", "report", "escalate"])
    g.add_edge("escalate", "report")
    g.add_edge("report", "teardown")
    g.add_edge("teardown", END)
    return g


def _state_types() -> list[tuple[str, str]]:
    """Types allowed to be deserialized from checkpoints.

    A checkpoint DB is input to the program. Deserializing arbitrary types from it is a
    code-execution risk, so only our own state models are allowed back in.
    """
    allowed = []
    for mod in (st, domain, evidence):
        for name, obj in vars(mod).items():
            if inspect.isclass(obj) and obj.__module__ == mod.__name__ and issubclass(obj, BaseModel | enum.Enum):
                allowed.append((mod.__name__, name))
    return allowed


@asynccontextmanager
async def open_graph(db_path: Path = DB_PATH):
    db_path.parent.mkdir(parents=True, exist_ok=True)
    async with AsyncSqliteSaver.from_conn_string(str(db_path)) as saver:
        saver.serde = JsonPlusSerializer(allowed_msgpack_modules=_state_types())
        yield build_graph().compile(checkpointer=saver)


def new_run_id() -> str:
    return time.strftime("run-%Y%m%d-%H%M%S-") + secrets.token_hex(2)


def _config(run_id: str) -> dict[str, Any]:
    # recursion_limit caps the total number of node executions: a last-resort stop if the
    # routing budgets above had a bug and the graph looped.
    return {"configurable": {"thread_id": run_id}, "recursion_limit": 40}


async def _stream(app, inp, run_id: str, ctx: GraphContext, on_node: Callable[[str, dict], None] | None) -> RunState:
    # durability="sync": the checkpoint is written before the next node starts, so even a
    # kill -9 loses at most the node that was running. The default ("async") is faster but
    # can lose the last completed node on a hard crash.
    async for chunk in app.astream(inp, _config(run_id), context=ctx, stream_mode="updates", durability="sync"):
        for name, update in chunk.items():
            if on_node:
                on_node(name, update or {})
    snap = await app.aget_state(_config(run_id))
    return RunState.model_validate(snap.values)


async def start_run(bundle: Path, sandbox: str = "e2b", ctx: GraphContext | None = None, run_id: str | None = None,
                    budget: Budget | None = None, on_node=None, db_path: Path = DB_PATH) -> RunState:
    run_id = run_id or new_run_id()
    state = RunState(run_id=run_id, bundle=str(bundle.resolve()), sandbox_mode=sandbox, budget=budget or Budget())
    async with open_graph(db_path) as app:
        return await _stream(app, state, run_id, ctx or GraphContext(), on_node)


async def resume_run(run_id: str, ctx: GraphContext | None = None, on_node=None, db_path: Path = DB_PATH) -> RunState:
    async with open_graph(db_path) as app:
        snap = await app.aget_state(_config(run_id))
        if not snap.values:
            raise ValueError(f"no checkpoints for {run_id}")
        if snap.values.get("state_version") != st.STATE_VERSION:
            raise ValueError(f"{run_id} was saved with state version {snap.values.get('state_version')}, "
                             f"this code expects {st.STATE_VERSION}")
        if not snap.next:
            return RunState.model_validate(snap.values)  # already finished
        return await _stream(app, None, run_id, ctx or GraphContext(), on_node)


async def history(run_id: str, db_path: Path = DB_PATH) -> AsyncIterator[dict]:
    """Every checkpoint of a run, newest first: time travel for debugging."""
    async with open_graph(db_path) as app:
        async for snap in app.aget_state_history(_config(run_id)):
            v = snap.values or {}
            yield {
                "step": snap.metadata.get("step"),
                "next": list(snap.next),
                "checkpoint_id": snap.config["configurable"]["checkpoint_id"],
                "evidence": len(v.get("evidence", [])),
                "tokens": (v["usage"].total_tokens if v.get("usage") else 0),
                "investigations": v.get("investigations", 0),
            }
