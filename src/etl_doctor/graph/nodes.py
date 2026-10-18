"""Graph nodes and routing. Each node: read state -> do one job -> return a partial update.

Context engineering: the graph passes each agent a compact view of the state (triage notes,
findings, evidence summaries), not the whole transcript of earlier agent calls. So input
tokens per call stay roughly flat as the investigation goes on, unlike Step 2's single
growing conversation.
"""

import json
import os
import sys
from collections.abc import Callable
from dataclasses import dataclass, field
from functools import wraps
from pathlib import Path
from typing import Any

from langgraph.runtime import Runtime
from pydantic_ai.exceptions import UsageLimitExceeded
from pydantic_ai.models import Model
from pydantic_ai.settings import ModelSettings
from pydantic_ai.usage import RunUsage, UsageLimits

from etl_doctor.context import escape, tail
from etl_doctor.domain import Diagnosis
from etl_doctor.evidence import Evidence, EvidenceStore
from etl_doctor.executor import Executor, LocalExecutor
from etl_doctor.graph.agents import (
    KnownFacts,
    hypothesis_agent,
    investigator_agent,
    triage_agent,
    verifier_agent,
)
from etl_doctor.graph.state import Report, RunState, Usage, Verification
from etl_doctor.investigate import manifest
from etl_doctor.llm import FAST_MODEL, STRONG_MODEL, make_model
from etl_doctor.tools import AgentDeps

SETTINGS = ModelSettings(temperature=0.0, max_tokens=8_192)


@dataclass
class GraphContext:
    """Per-process runtime context: NOT checkpointed. Rebuilt on resume."""

    strong: str | Model = STRONG_MODEL
    fast: str | Model = FAST_MODEL
    on_evidence: Callable[[Evidence], None] | None = None
    crash_before: str | None = None  # demo/testing: hard-kill the process before this node
    executors: dict[str, Executor] = field(default_factory=dict)  # run_id -> live executor

    def model(self, which: str) -> Model:
        m = self.strong if which == "strong" else self.fast
        return make_model(m) if isinstance(m, str) else m


def node(fn):
    """Common wrapper: the crash hook for the resume demo."""

    @wraps(fn)
    async def wrapper(state: RunState, runtime: Runtime[GraphContext]):
        if runtime.context.crash_before == fn.__name__:
            # os._exit, not an exception: like kill -9, no cleanup, no finally blocks.
            print(f"\n*** simulated crash before '{fn.__name__}' (run {state.run_id}) ***", file=sys.stderr, flush=True)
            os._exit(137)
        return await fn(state, runtime)

    return wrapper


def usage_of(u: RunUsage) -> Usage:
    return Usage(requests=u.requests, tool_calls=u.tool_calls, input_tokens=u.input_tokens, output_tokens=u.output_tokens)


async def executor_for(state: RunState, ctx: GraphContext) -> tuple[Executor, dict[str, Any]]:
    """The live executor for this run, plus a state update if the sandbox had to change.

    After a crash, the in-process cache is empty but state still has the sandbox_id: we
    reconnect to the same VM (its workspace is intact). If it has expired, we make a new one.
    """
    if state.sandbox_mode == "local":
        return LocalExecutor(Path(state.bundle)), {}
    if ex := ctx.executors.get(state.run_id):
        return ex, {}
    from etl_doctor.sandbox import E2BExecutor

    if state.sandbox_id:
        try:
            ex = await E2BExecutor.connect(state.sandbox_id)
            ctx.executors[state.run_id] = ex
            return ex, {}
        except Exception as e:  # expired or killed
            print(f"sandbox {state.sandbox_id} is gone ({type(e).__name__}); creating a new one", file=sys.stderr)
    ex = await E2BExecutor.create(Path(state.bundle))
    ctx.executors[state.run_id] = ex
    return ex, {"sandbox_id": ex.sandbox_id}


def render_evidence(evidence: list[Evidence], with_data: bool, max_chars: int = 1_500) -> str:
    if not evidence:
        return "(none yet)"
    lines = []
    for e in evidence:
        lines.append(f"{e.id} {e.tool}({json.dumps(e.args)}): {e.summary}")
        if with_data:
            data = json.dumps(e.data, default=str)
            lines.append("   data: " + (data if len(data) <= max_chars else data[:max_chars] + " ...[truncated]"))
    return escape("\n".join(lines))


def untrusted(source: str, text: str) -> str:
    return f'<untrusted source="{source}">\n{escape(text)}\n</untrusted>'


# --- nodes ---------------------------------------------------------------------------------


@node
async def intake(state: RunState, runtime: Runtime[GraphContext]) -> dict:
    bundle = Path(state.bundle)
    return {
        "manifest": manifest(bundle),
        "current_files": sorted(p.name for p in (bundle / "data" / "current").glob("*.csv")),
    }


@node
async def provision_sandbox(state: RunState, runtime: Runtime[GraphContext]) -> dict:
    _, update = await executor_for(state, runtime.context)
    return update


@node
async def triage(state: RunState, runtime: Runtime[GraphContext]) -> dict:
    bundle = Path(state.bundle)
    parts = [untrusted("problem.md", (bundle / "problem.md").read_text()), untrusted("bundle manifest", state.manifest)]
    for log in ["pipeline.log", "quality_tests.log"]:
        if (p := bundle / "logs" / log).exists():
            parts.append(untrusted(f"logs/{log}", tail(p, 2_500)))
    # Strong model on purpose. Measured on the 6 cases: the fast model ranked the right class
    # first 4/6 times vs 5/6, and named the right column 4/6 vs 6/6, for the same ~5k tokens.
    # A wrong triage cost two extra investigation rounds, far more than it saved.
    r = await triage_agent.run("\n\n".join(parts), model=runtime.context.model("strong"), model_settings=SETTINGS,
                               usage_limits=UsageLimits(request_limit=4))
    return {"triage": r.output, "usage": usage_of(r.usage)}


@node
async def investigate(state: RunState, runtime: Runtime[GraphContext]) -> dict:
    ctx = runtime.context
    ex, update = await executor_for(state, ctx)
    store = EvidenceStore(on_add=ctx.on_evidence, existing=state.evidence)
    deps = AgentDeps(executor=ex, evidence=store, current_files=state.current_files)
    questions = (state.hypotheses.next_checks if state.hypotheses else []) or (state.triage.first_checks if state.triage else [])
    prompt = "\n\n".join([
        f"Triage notes:\n{state.triage.model_dump_json(indent=1) if state.triage else '(none)'}",
        untrusted("bundle manifest", state.manifest),
        "Findings so far:\n" + ("\n".join(f"- {f}" for f in state.findings) or "(none)"),
        "Evidence so far (re-run a check only if you need its full result):\n" + render_evidence(state.evidence, with_data=False),
        "Rejected hypotheses / feedback:\n" + ("\n".join(f"- {f}" for f in state.feedback) or "(none)"),
        "Open questions for this round:\n" + "\n".join(f"- {q}" for q in questions),
    ])
    usage = RunUsage()  # passed in so we can still read it if the budget runs out mid-run
    limits = UsageLimits(request_limit=state.budget.tool_calls_per_investigation + 4,
                         tool_calls_limit=state.budget.tool_calls_per_investigation)
    try:
        r = await investigator_agent.run(prompt, deps=deps, model=ctx.model("strong"), model_settings=SETTINGS,
                                         usage_limits=limits, usage=usage)
        findings = r.output.findings
    except UsageLimitExceeded:
        # Out of budget for this round is not a failure of the run: keep the evidence the
        # tools recorded and let the hypothesis step work with it.
        findings = [f"(round {state.investigations + 1} ran out of tool budget; see its evidence)"]
    return {**update, "evidence": store.new(), "findings": findings,
            "investigations": state.investigations + 1, "usage": usage_of(usage)}


@node
async def hypothesize(state: RunState, runtime: Runtime[GraphContext]) -> dict:
    prompt = "\n\n".join([
        f"Triage notes:\n{state.triage.model_dump_json(indent=1) if state.triage else '(none)'}",
        "Findings:\n" + ("\n".join(f"- {f}" for f in state.findings) or "(none)"),
        "Evidence (ID, tool call, summary, result):\n" + render_evidence(state.evidence, with_data=True),
        "Feedback on earlier hypotheses:\n" + ("\n".join(f"- {f}" for f in state.feedback) or "(none)"),
        f"Valid files for first_bad_partition: {state.current_files}",
    ])
    current = Path(state.bundle) / "data" / "current"
    headers = {f: (current / f).open().readline().strip().split(",") for f in state.current_files}
    deps = KnownFacts({e.id for e in state.evidence}, state.current_files, headers)
    r = await hypothesis_agent.run(prompt, deps=deps, model=runtime.context.model("strong"), model_settings=SETTINGS,
                                   usage_limits=UsageLimits(request_limit=5))
    return {"hypotheses": r.output, "usage": usage_of(r.usage)}


@node
async def verify(state: RunState, runtime: Runtime[GraphContext]) -> dict:
    ctx = runtime.context
    ex, update = await executor_for(state, ctx)
    h = state.hypotheses.top()
    store = EvidenceStore(on_add=ctx.on_evidence, existing=state.evidence)
    deps = AgentDeps(executor=ex, evidence=store, current_files=state.current_files)
    prompt = f"Hypothesis to test:\n{h.model_dump_json(indent=1)}"
    usage = RunUsage()
    try:
        r = await verifier_agent.run(prompt, deps=deps, model=ctx.model("strong"), model_settings=SETTINGS,
                                     usage_limits=UsageLimits(request_limit=8, tool_calls_limit=4), usage=usage)
        v = r.output.model_copy(update={"hypothesis_id": h.id})
    except UsageLimitExceeded:
        # A verifier that can't decide within budget hasn't confirmed anything.
        cited = [e.id for e in store.new()] or h.evidence_ids
        v = Verification(hypothesis_id=h.id, outcome="inconclusive", evidence_ids=cited,
                         observations="verification ran out of tool budget before reaching a verdict")
    out = {**update, "verification": v, "evidence": store.new(), "verifications": state.verifications + 1,
           "usage": usage_of(usage)}
    if v.outcome != "confirmed":
        out["feedback"] = [f"{h.id} ({h.failure_class}, {h.statement[:120]}) was {v.outcome}: {v.observations[:300]}"]
    return out


@node
async def escalate(state: RunState, runtime: Runtime[GraphContext]) -> dict:
    return {"terminal_reason": escalation_reason(state)}


@node
async def report(state: RunState, runtime: Runtime[GraphContext]) -> dict:
    confirmed = state.verification is not None and state.verification.outcome == "confirmed"
    diagnosis = None
    if state.hypotheses:
        h = state.hypotheses.top()
        cited = list(dict.fromkeys(h.evidence_ids + (state.verification.evidence_ids if confirmed else [])))[:8]
        diagnosis = Diagnosis(
            failure_class=h.failure_class, summary=h.statement[:200], root_cause=h.statement[:600],
            affected_columns=h.affected_columns, first_bad_partition=h.first_bad_partition,
            suggested_fix=h.suggested_fix[:600], confidence=h.confidence, evidence_ids=cited,
        )
    return {"report": Report(
        status="diagnosed" if confirmed and not state.terminal_reason else "escalated",
        diagnosis=diagnosis, verification=state.verification,
        terminal_reason=state.terminal_reason or "hypothesis confirmed by verification",
        usage=state.usage,
    )}


@node
async def teardown(state: RunState, runtime: Runtime[GraphContext]) -> dict:
    if state.sandbox_mode == "e2b" and state.sandbox_id:
        ex = runtime.context.executors.pop(state.run_id, None)
        if ex is None:
            from etl_doctor.sandbox import E2BExecutor

            try:
                ex = await E2BExecutor.connect(state.sandbox_id)
            except Exception:
                ex = None  # already gone: nothing to clean up
        if ex is not None:
            await ex.kill()
    return {"sandbox_id": None}


# --- routing: pure functions of state, so they are trivial to unit-test ----------------------


def over_token_budget(s: RunState) -> bool:
    return s.usage.total_tokens >= s.budget.max_total_tokens


def route_after_hypothesize(s: RunState) -> str:
    if over_token_budget(s):
        return "escalate"
    if s.hypotheses.top().confidence >= s.budget.confidence_threshold and s.verifications < s.budget.max_verifications:
        return "verify"
    if s.investigations < s.budget.max_investigations:
        return "investigate"
    return "escalate"


def route_after_verify(s: RunState) -> str:
    if s.verification.outcome == "confirmed":
        return "report"
    if over_token_budget(s) or s.verifications >= s.budget.max_verifications or s.investigations >= s.budget.max_investigations:
        return "escalate"
    return "investigate"


def escalation_reason(s: RunState) -> str:
    if over_token_budget(s):
        return f"token budget exhausted ({s.usage.total_tokens} >= {s.budget.max_total_tokens})"
    if s.verification and s.verification.outcome != "confirmed":
        return f"top hypothesis {s.verification.outcome} after {s.verifications} verification(s)"
    if s.hypotheses and s.hypotheses.top().confidence < s.budget.confidence_threshold:
        return f"no hypothesis reached confidence {s.budget.confidence_threshold} after {s.investigations} investigation round(s)"
    return "verification budget exhausted"
