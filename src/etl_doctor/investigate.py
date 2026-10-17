"""Step 2: an agent with read-only tools. It decides which checks to run and cites evidence IDs.

This is the agent loop (ReAct: reason -> act -> observe, repeated):
model picks a tool -> harness runs it -> result goes back into the conversation -> model
picks the next tool ... until it returns a Diagnosis. PydanticAI runs this loop for us;
the harness's job is to bound it (UsageLimits) and to check the final answer.
"""

from dataclasses import dataclass
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

    def cited(self) -> list[Evidence]:
        ids = set(self.diagnosis.evidence_ids)
        return [e for e in self.evidence if e.id in ids]


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
    user_prompt = f'<untrusted source="problem.md">\n{escape(problem)}\n</untrusted>\n\nInvestigate and diagnose.'
    llm = make_model(model) if isinstance(model, str) else model
    result = await agent.run(user_prompt, deps=deps, model=llm, model_settings=SETTINGS, usage_limits=LIMITS)
    retries = sum(1 for m in result.all_messages() for p in m.parts if p.part_kind == "retry-prompt")
    return InvestigateResult(result.output, deps.evidence.all(), result.usage, retries, llm.model_name)
