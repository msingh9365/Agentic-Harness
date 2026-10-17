"""Step 2: an agent with read-only tools. It decides which checks to run and cites evidence IDs.

This is the agent loop (ReAct: reason -> act -> observe, repeated):
model picks a tool -> harness runs it -> result goes back into the conversation -> model
picks the next tool ... until it returns a Diagnosis. PydanticAI runs this loop for us;
the harness's job is to bound it (UsageLimits) and to check the final answer.
"""

from dataclasses import dataclass, field
from pathlib import Path

from pydantic_ai import Agent, ModelRetry, RunContext
from pydantic_ai.models import Model
from pydantic_ai.settings import ModelSettings
from pydantic_ai.usage import RunUsage, UsageLimits

from etl_doctor.context import escape, head
from etl_doctor.domain import Diagnosis
from etl_doctor.evidence import Evidence, EvidenceStore
from etl_doctor.executor import Executor, LocalExecutor
from etl_doctor.llm import STRONG_MODEL, make_model
from etl_doctor.tools import AgentDeps, readonly_tools

PROMPT = (Path(__file__).parent / "prompts" / "investigate.md").read_text()

SETTINGS = ModelSettings(temperature=0.0, max_tokens=8_192)
# Budgets for one investigation. Without them a confused model can loop on tools forever.
LIMITS = UsageLimits(request_limit=20, tool_calls_limit=15)

agent = Agent(
    deps_type=AgentDeps,
    output_type=Diagnosis,
    instructions=PROMPT,
    toolsets=[readonly_tools],
    retries=3,
)


@agent.output_validator
def check_citations(ctx: RunContext[AgentDeps], out: Diagnosis) -> Diagnosis:
    known = ctx.deps.evidence.ids()
    problems = []
    if missing := sorted(set(out.evidence_ids) - known):
        problems.append(
            f"evidence_ids {missing} were never returned by a tool. Cite only these: {sorted(known) or 'none yet: call tools first'}"
        )
    if out.first_bad_partition and out.first_bad_partition not in ctx.deps.current_files:
        problems.append(
            f"first_bad_partition {out.first_bad_partition!r} is not a file in data/current; files: {ctx.deps.current_files}"
        )
    if problems:
        raise ModelRetry("Fix these problems and answer again:\n- " + "\n- ".join(problems))
    return out


@dataclass
class InvestigateResult:
    diagnosis: Diagnosis
    evidence: list[Evidence]
    usage: RunUsage
    retries: int
    model: str
    sandbox_seconds: float | None = None  # set when tools ran in E2B (its cost driver)
    tool_call_parts: list = field(default_factory=list)  # every call the model asked for, even refused ones

    def cited(self) -> list[Evidence]:
        ids = set(self.diagnosis.evidence_ids)
        return [e for e in self.evidence if e.id in ids]


def manifest(bundle: Path) -> str:
    """Every file in the bundle with its size, and header + row count for CSVs.

    Computed by the harness for free. Without it the model spent 4-6 of its ~15 tool calls
    just listing directories, and runs hit the budget. Static facts go in the prompt;
    tools are for questions whose answer depends on what the model has seen so far.
    """
    lines = []
    for p in sorted(bundle.rglob("*")):
        if not p.is_file() or "__pycache__" in p.parts:
            continue
        rel = p.relative_to(bundle).as_posix()
        if p.suffix == ".csv":
            with p.open(errors="replace") as fh:
                header = fh.readline().strip()
                rows = sum(1 for _ in fh)
            lines.append(f"{rel}  rows={rows}  header={header}")
        else:
            lines.append(f"{rel}  bytes={p.stat().st_size}")
    return "\n".join(lines[:400])


async def investigate_in_sandbox(bundle: Path, model: str | Model = STRONG_MODEL, on_evidence=None, on_ready=None):
    """Step 3: same agent, tools run in a fresh E2B microVM that is destroyed afterwards."""
    from etl_doctor.sandbox import E2BExecutor

    async with E2BExecutor.start(bundle) as ex:
        if on_ready:
            on_ready(ex)
        r = await investigate(bundle, model, executor=ex, on_evidence=on_evidence)
        r.sandbox_seconds = round(ex.seconds(), 1)
        return r


async def investigate(
    bundle: Path,
    model: str | Model = STRONG_MODEL,
    executor: Executor | None = None,
    on_evidence=None,
) -> InvestigateResult:
    """`on_evidence` is called as each tool call is recorded (the CLI prints a live trace)."""
    deps = AgentDeps(
        executor=executor or LocalExecutor(bundle),
        evidence=EvidenceStore(on_add=on_evidence),
        current_files=sorted(p.name for p in (bundle / "data" / "current").glob("*.csv")),
    )
    problem = head(bundle / "problem.md", 2_000)
    user_prompt = (
        f'<untrusted source="problem.md">\n{escape(problem)}\n</untrusted>\n\n'
        # File names and CSV headers come from the bundle too, so they are untrusted as well.
        f'<untrusted source="bundle manifest">\n{escape(manifest(bundle))}\n</untrusted>\n\n'
        "Investigate and diagnose. The manifest above is already known: don't list directories to rediscover it."
    )
    llm = make_model(model) if isinstance(model, str) else model
    result = await agent.run(user_prompt, deps=deps, model=llm, model_settings=SETTINGS, usage_limits=LIMITS)
    retries = sum(1 for m in result.all_messages() for p in m.parts if p.part_kind == "retry-prompt")
    calls = [p for m in result.all_messages() for p in m.parts if p.part_kind == "tool-call" and p.tool_name in readonly_tools.tools]
    return InvestigateResult(result.output, deps.evidence.all(), result.usage, retries, llm.model_name, tool_call_parts=calls)
