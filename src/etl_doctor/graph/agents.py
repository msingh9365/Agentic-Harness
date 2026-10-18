"""The four LLM roles of the graph. Each is small, typed and has one job.

Splitting one big agent into roles lets each step use the right model (cheap triage,
strong reasoning), the right tools (none, all read-only, or a narrow subset) and a
budget of its own, and lets the graph decide what happens next instead of the model.
"""

from dataclasses import dataclass
from pathlib import Path

from pydantic_ai import Agent, ModelRetry, RunContext

from etl_doctor.graph.state import HypothesisSet, InvestigationStep, TriageResult, Verification
from etl_doctor.tools import AgentDeps, readonly_tools

PROMPTS = Path(__file__).resolve().parent.parent / "prompts"


def prompt(name: str) -> str:
    return (PROMPTS / f"{name}.md").read_text()


@dataclass
class KnownFacts:
    """Deps for the no-tool agents: what their answers may refer to."""

    evidence_ids: set[str]
    current_files: list[str]
    headers: dict[str, list[str]]  # current file -> its CSV columns, read by the harness


def _check_refs(evidence_ids: list[str], first_bad: str | None, known: set[str], files: list[str]) -> list[str]:
    problems = []
    if missing := sorted(set(evidence_ids) - known):
        problems.append(f"evidence IDs {missing} don't exist; valid IDs: {sorted(known)}")
    if first_bad and first_bad not in files:
        problems.append(f"first_bad_partition {first_bad!r} is not a file in data/current: {files}")
    return problems


triage_agent = Agent(output_type=TriageResult, instructions=prompt("triage"), retries=3)

investigator_agent = Agent(
    deps_type=AgentDeps,
    output_type=InvestigationStep,
    instructions=prompt("investigate_step"),
    toolsets=[readonly_tools],
    retries=3,
)

hypothesis_agent = Agent(deps_type=KnownFacts, output_type=HypothesisSet, instructions=prompt("hypothesize"), retries=3)


@hypothesis_agent.output_validator
def _hypotheses_cite_real_evidence(ctx: RunContext[KnownFacts], out: HypothesisSet) -> HypothesisSet:
    problems = []
    cols = [set(c) for c in ctx.deps.headers.values()]
    changing = (set.union(*cols) - set.intersection(*cols)) if cols else set()
    for h in out.hypotheses:
        problems += [f"{h.id}: {p}" for p in _check_refs(h.evidence_ids, h.first_bad_partition, ctx.deps.evidence_ids, ctx.deps.current_files)]
        # Cheap deterministic guardrail on an LLM claim: a rename/drop must show in the headers.
        if h.failure_class == "F3" and not changing & set(h.affected_columns):
            problems.append(
                f"{h.id}: F3 means a column was renamed or dropped, but the headers of data/current files "
                f"differ only in {sorted(changing) or 'nothing (all headers are identical)'}. "
                "Use the class that matches the statement."
            )
    if problems:
        raise ModelRetry("Fix and answer again:\n- " + "\n- ".join(problems))
    return out


# Least privilege per role: the verifier only needs to query and compare data.
VERIFY_TOOLS = {"run_sql", "column_by_file", "profile_dataset", "diff_schema"}
verifier_agent = Agent(
    deps_type=AgentDeps,
    output_type=Verification,
    instructions=prompt("verify"),
    toolsets=[readonly_tools.filtered(lambda ctx, tool: tool.name in VERIFY_TOOLS)],
    retries=3,
)


@verifier_agent.output_validator
def _verification_cites_real_evidence(ctx: RunContext[AgentDeps], out: Verification) -> Verification:
    if problems := _check_refs(out.evidence_ids, None, ctx.deps.evidence.ids(), ctx.deps.current_files):
        raise ModelRetry("Fix and answer again:\n- " + "\n- ".join(problems))
    return out
