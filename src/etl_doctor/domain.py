"""Typed contracts between the LLM and the rest of the harness. Pure Pydantic, no I/O.

Field descriptions are not just docs: PydanticAI sends them to the model as part of the
JSON schema, so they work as instructions for each field.
"""

from enum import StrEnum

from pydantic import BaseModel, Field


class FailureClass(StrEnum):
    DATE_FORMAT_CHANGE = "F1"
    COLUMN_RENAMED = "F3"
    TYPE_DRIFT = "F4"
    UNKNOWN = "UNKNOWN"


class Quote(BaseModel):
    """A verbatim excerpt from the context. Checked against the context after the model
    answers, so the model cannot invent evidence."""

    source: str = Field(description='The source attribute of the <untrusted> block, e.g. "logs/pipeline.log".')
    text: str = Field(
        min_length=8,
        max_length=300,
        description="Copied exactly, character for character, from that block. One line or part of a line.",
    )


class DiagnosisCore(BaseModel):
    """Fields every diagnosis has, whichever agent produced it. The grader reads only these."""

    failure_class: FailureClass = Field(
        description="F1 date/time format changed, F3 column renamed or dropped, "
        "F4 numeric value format changed, UNKNOWN if the evidence does not support one."
    )
    summary: str = Field(max_length=200, description="One sentence a manager can read.")
    root_cause: str = Field(
        max_length=600,
        description="What changed upstream, from which file on, and why the pipeline fails or loses rows.",
    )
    affected_columns: list[str] = Field(
        min_length=1,
        description="Pipeline column names (as in config.yaml required_columns) that are affected.",
    )
    first_bad_partition: str | None = Field(
        description="File name of the first broken data file, e.g. orders_2026-10-14.csv. null if unknown."
    )
    suggested_fix: str = Field(max_length=600, description="Concrete change to code or config. Do not apply it.")
    confidence: float = Field(ge=0, le=1)


class QuotedDiagnosis(DiagnosisCore):
    """Step 1 (no tools): evidence is quoted from the prompt and checked verbatim."""

    evidence: list[Quote] = Field(min_length=1, max_length=6)


class Diagnosis(DiagnosisCore):
    """Step 2+ (tools): evidence is cited by ID. IDs are created by the tools when they
    run, never by the model, so a cited ID proves the check really happened."""

    evidence_ids: list[str] = Field(
        min_length=1,
        max_length=8,
        description='IDs returned by your tool calls, e.g. ["ev-002", "ev-005"], that support the root cause.',
    )
