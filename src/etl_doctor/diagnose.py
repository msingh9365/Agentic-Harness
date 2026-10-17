"""Step 1: one agent, no tools. Context in, validated QuotedDiagnosis out.

Kept after Step 2 as the `--no-tools` baseline, so evals can compare with and without tools."""

from dataclasses import dataclass
from pathlib import Path

from pydantic_ai import Agent, ModelRetry, RunContext
from pydantic_ai.models import Model
from pydantic_ai.settings import ModelSettings
from pydantic_ai.usage import RunUsage, UsageLimits

from etl_doctor.context import BundleContext, build_context, normalize
from etl_doctor.domain import QuotedDiagnosis
from etl_doctor.llm import STRONG_MODEL, make_model

PROMPT = (Path(__file__).parent / "prompts" / "diagnose.md").read_text()

# temperature 0: we want the most likely answer, not a creative one, and runs that are
# as repeatable as the provider allows.
SETTINGS = ModelSettings(temperature=0.0, max_tokens=8_192)
# Hard ceiling on model calls for one diagnosis, retries included. Stops a model that
# keeps failing validation from looping (and spending) forever.
LIMITS = UsageLimits(request_limit=6)

agent = Agent(
    deps_type=BundleContext,
    output_type=QuotedDiagnosis,
    instructions=PROMPT,
    # Each failed validation is sent back to the model as feedback, up to this many times.
    retries=3,
)


@agent.output_validator
def check_against_context(ctx: RunContext[BundleContext], out: QuotedDiagnosis) -> QuotedDiagnosis:
    """Reject answers that cite things not in the context.

    Pydantic already checked the shape (types, enums, lengths). This checks the facts that
    we can verify cheaply. ModelRetry sends the message back to the model, which tries
    again: this is the "validation + retry" loop.
    """
    sources = ctx.deps.by_source()
    problems = []
    for q in out.evidence:
        if q.source not in sources:
            problems.append(f"source {q.source!r} does not exist; valid sources: {sorted(sources)}")
        elif normalize(q.text) not in normalize(sources[q.source]):
            problems.append(f"quote {q.text!r} does not appear verbatim in {q.source}")
    if out.first_bad_partition and out.first_bad_partition not in ctx.deps.current_files:
        problems.append(
            f"first_bad_partition {out.first_bad_partition!r} is not a file in data/current; "
            f"files: {ctx.deps.current_files}"
        )
    if problems:
        raise ModelRetry("Fix these problems and answer again:\n- " + "\n- ".join(problems))
    return out


@dataclass
class DiagnoseResult:
    diagnosis: QuotedDiagnosis
    usage: RunUsage
    retries: int
    model: str
    prompt_chars: int


async def diagnose(bundle: Path, model: str | Model = STRONG_MODEL) -> DiagnoseResult:
    """`model` is a model id on the NVIDIA API, or a Model object (tests pass a fake one)."""
    ctx = build_context(bundle)
    user_prompt = ctx.render()
    llm = make_model(model) if isinstance(model, str) else model
    result = await agent.run(user_prompt, deps=ctx, model=llm, model_settings=SETTINGS, usage_limits=LIMITS)
    retries = sum(
        1 for m in result.all_messages() for p in m.parts if p.part_kind == "retry-prompt"
    )
    return DiagnoseResult(result.output, result.usage, retries, llm.model_name, len(PROMPT) + len(user_prompt))
