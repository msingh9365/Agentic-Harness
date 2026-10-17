"""Scenario specs (inputs to the fault injector) and ground truth (the answer key)."""

from typing import Any, Literal

from pydantic import BaseModel

Mode = Literal["crash", "silent"]


class Fault(BaseModel):
    type: Literal["date_format_change", "column_rename", "type_drift"]
    column: str
    params: dict[str, Any] = {}


class Scenario(BaseModel):
    id: str
    failure_class: str
    description: str
    fault: Fault
    start_partition: str  # ISO date of the first broken file
    modes: list[Mode]
    variants: dict[str, list[Any]] = {}
    root_cause: str  # template, formatted with fault params + derived fields


class GroundTruth(BaseModel):
    """What a correct diagnosis must say. Never placed inside the bundle the agent sees."""

    scenario_id: str
    mode: Mode
    failure_class: str
    affected_columns: list[str]
    first_bad_partition: str
    fault: Fault
    root_cause: str
    pipeline_exit_code: int
    quality_tests_passed: bool | None  # None when the pipeline crashed before tests ran
