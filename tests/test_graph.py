"""Step 4: the graph end to end with a scripted model and local tools (no network)."""

import asyncio
import subprocess
import sys
from pathlib import Path

import pytest

from etl_doctor.graph.build import history, resume_run, start_run
from etl_doctor.graph.nodes import GraphContext, route_after_hypothesize, route_after_verify
from etl_doctor.graph.state import Budget, Hypothesis, HypothesisSet, RunState, Usage, Verification
from evals.inject import build, load_scenario
from tests.fake_brain import make_brain


@pytest.fixture(scope="module")
def bundle(tmp_path_factory) -> Path:
    return build(load_scenario("f1_date_format"), "silent", {}, tmp_path_factory.mktemp("cases")) / "bundle"


def ctx(**kw) -> GraphContext:
    brain = make_brain(**kw)
    return GraphContext(strong=brain, fast=brain)


def test_happy_path_is_diagnosed(bundle, tmp_path):
    nodes = []
    s = asyncio.run(start_run(bundle, "local", ctx(), db_path=tmp_path / "cp.db", on_node=lambda n, u: nodes.append(n)))
    assert nodes == ["intake", "provision_sandbox", "triage", "investigate", "hypothesize", "verify", "report", "teardown"]
    assert s.report.status == "diagnosed"
    assert s.report.diagnosis.first_bad_partition == "orders_2026-10-14.csv"
    assert [e.id for e in s.evidence] == ["ev-001", "ev-002"]  # IDs continue across nodes


def test_low_confidence_loops_then_escalates(bundle, tmp_path):
    nodes = []
    s = asyncio.run(start_run(bundle, "local", ctx(confidence=0.5), budget=Budget(max_investigations=2),
                              db_path=tmp_path / "cp.db", on_node=lambda n, u: nodes.append(n)))
    assert nodes.count("investigate") == 2 and "verify" not in nodes
    assert s.report.status == "escalated" and "confidence" in s.report.terminal_reason


def test_falsified_hypothesis_goes_back_to_investigation(bundle, tmp_path):
    nodes = []
    s = asyncio.run(start_run(bundle, "local", ctx(verdict="falsified"), db_path=tmp_path / "cp.db",
                              on_node=lambda n, u: nodes.append(n)))
    assert nodes.count("verify") == 2  # max_verifications
    assert s.report.status == "escalated" and s.feedback  # the rejection reason is kept for later rounds


def test_crash_and_resume_from_checkpoint(bundle, tmp_path):
    db = tmp_path / "cp.db"
    # Run in a child process that hard-kills itself (os._exit) right before 'hypothesize'.
    script = (
        "import asyncio; from pathlib import Path; from etl_doctor.graph.build import start_run;"
        "from etl_doctor.graph.nodes import GraphContext; from tests.fake_brain import make_brain;"
        "b = make_brain(); asyncio.run(start_run(Path(r'%s'), 'local', GraphContext(strong=b, fast=b, crash_before='hypothesize'),"
        " run_id='crashy', db_path=Path(r'%s')))" % (bundle, db)
    )
    proc = subprocess.run([sys.executable, "-c", script], capture_output=True, text=True, cwd=Path(__file__).parent.parent)
    assert proc.returncode == 137, proc.stderr

    async def checkpoints():
        return [h async for h in history("crashy", db_path=db)]

    assert (asyncio.run(checkpoints()))[0]["next"] == ["hypothesize"]

    nodes, new_evidence = [], []
    c = ctx()
    c.on_evidence = new_evidence.append
    s = asyncio.run(resume_run("crashy", c, db_path=db, on_node=lambda n, u: nodes.append(n)))
    assert nodes[0] == "hypothesize"           # did not redo intake/triage/investigate
    assert [e.id for e in new_evidence] == ["ev-002"]  # only verify ran a tool; ev-001 came from the checkpoint
    assert s.report.status == "diagnosed"


# --- routing is pure, so test it directly ---------------------------------------------------

def _state(conf=0.9, investigations=1, verifications=0, outcome=None, tokens=0) -> RunState:
    h = Hypothesis(id="h1", failure_class="F1", statement="s", affected_columns=["c"], first_bad_partition=None,
                   evidence_ids=["ev-001"], confidence=conf, falsification_check="x", suggested_fix="y")
    v = Verification(hypothesis_id="h1", outcome=outcome, observations="o", evidence_ids=["ev-001"]) if outcome else None
    return RunState(run_id="r", bundle="b", hypotheses=HypothesisSet(hypotheses=[h]), verification=v,
                    investigations=investigations, verifications=verifications, usage=Usage(input_tokens=tokens))


@pytest.mark.parametrize(("kw", "expected"), [
    ({}, "verify"),
    ({"conf": 0.5}, "investigate"),
    ({"conf": 0.5, "investigations": 3}, "escalate"),
    ({"tokens": 10**6}, "escalate"),
    ({"verifications": 2}, "investigate"),  # confident, but no verification budget left
])
def test_route_after_hypothesize(kw, expected):
    assert route_after_hypothesize(_state(**kw)) == expected


@pytest.mark.parametrize(("kw", "expected"), [
    ({"outcome": "confirmed"}, "report"),
    ({"outcome": "falsified", "verifications": 1}, "investigate"),
    ({"outcome": "falsified", "verifications": 2}, "escalate"),
    ({"outcome": "inconclusive", "verifications": 1, "tokens": 10**6}, "escalate"),
])
def test_route_after_verify(kw, expected):
    assert route_after_verify(_state(**kw)) == expected
