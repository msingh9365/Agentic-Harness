"""Graph state: everything a run knows, saved to SQLite after every node.

Rules:
- Nodes return partial updates (dicts); they never mutate state in place.
- `evidence` has an append-only reducer: once recorded, evidence can't be rewritten.
- `usage` has a summing reducer: each node reports only what it spent.
- Nothing non-serializable lives here (no sandbox handles, no callbacks). The sandbox is
  referenced by `sandbox_id` and reconnected on resume.
"""

import operator
from typing import Annotated, Literal

from pydantic import BaseModel, Field

from etl_doctor.domain import Diagnosis, FailureClass
from etl_doctor.evidence import Evidence

STATE_VERSION = 1


class Usage(BaseModel):
    requests: int = 0
    tool_calls: int = 0
    input_tokens: int = 0
    output_tokens: int = 0

    def __add__(self, other: "Usage") -> "Usage":
        return Usage(**{k: getattr(self, k) + getattr(other, k) for k in Usage.model_fields})

    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens


class Budget(BaseModel):
    max_total_tokens: int = 400_000
    max_investigations: int = 3  # investigate <-> hypothesize loops
    max_verifications: int = 2
    tool_calls_per_investigation: int = 8
    confidence_threshold: float = 0.8


class TriageResult(BaseModel):
    symptom: str = Field(max_length=300, description="What is observably wrong, in one or two sentences.")
    run_outcome: Literal["crashed", "succeeded_with_bad_data", "unclear"]
    candidate_classes: list[FailureClass] = Field(min_length=1, max_length=3)
    suspect_columns: list[str] = Field(default_factory=list, max_length=4)
    first_checks: list[str] = Field(min_length=1, max_length=4, description="Concrete checks to run first.")


class InvestigationStep(BaseModel):
    findings: list[str] = Field(min_length=1, max_length=8, description="What the tool results showed, each citing ev-IDs.")
    open_questions: list[str] = Field(default_factory=list, max_length=4)


class Hypothesis(BaseModel):
    id: str = Field(description='"h1", "h2", ...')
    failure_class: FailureClass
    statement: str = Field(max_length=400, description="What changed upstream, from which file on, and the effect.")
    affected_columns: list[str] = Field(min_length=1)
    first_bad_partition: str | None
    evidence_ids: list[str] = Field(min_length=1, description="ev-IDs that support this hypothesis.")
    confidence: float = Field(ge=0, le=1)
    falsification_check: str = Field(
        max_length=400, description="A concrete tool check whose result would DISPROVE this hypothesis."
    )
    suggested_fix: str = Field(max_length=500)


class HypothesisSet(BaseModel):
    hypotheses: list[Hypothesis] = Field(min_length=1, max_length=3)
    next_checks: list[str] = Field(default_factory=list, max_length=4, description="What to investigate if not confident.")

    def top(self) -> Hypothesis:
        return max(self.hypotheses, key=lambda h: h.confidence)


class Verification(BaseModel):
    hypothesis_id: str
    outcome: Literal["confirmed", "falsified", "inconclusive"]
    observations: str = Field(max_length=600)
    evidence_ids: list[str] = Field(min_length=1)


class Report(BaseModel):
    status: Literal["diagnosed", "escalated"]
    diagnosis: Diagnosis | None
    verification: Verification | None
    terminal_reason: str
    usage: Usage


class RunState(BaseModel):
    state_version: int = STATE_VERSION
    run_id: str
    bundle: str  # local path; the bundle is uploaded to the sandbox
    sandbox_mode: Literal["e2b", "local"] = "e2b"
    budget: Budget = Budget()

    manifest: str = ""
    current_files: list[str] = []
    sandbox_id: str | None = None

    triage: TriageResult | None = None
    evidence: Annotated[list[Evidence], operator.add] = []
    findings: Annotated[list[str], operator.add] = []
    hypotheses: HypothesisSet | None = None
    verification: Verification | None = None
    feedback: Annotated[list[str], operator.add] = []  # why a hypothesis was rejected, for the next round

    investigations: int = 0
    verifications: int = 0
    usage: Annotated[Usage, operator.add] = Usage()
    terminal_reason: str | None = None
    report: Report | None = None
