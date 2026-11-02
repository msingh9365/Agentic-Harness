"""Step 4: the graph end to end with a scripted model and local tools (no network)."""

import asyncio
import subprocess
import sys
from pathlib import Path

import pytest

from datetime import datetime, timezone

from etl_doctor.graph.build import decide, history, pending_approval, resume_run, start_run
from etl_doctor.graph.nodes import GraphContext, route_after_hypothesize, route_after_verify
from etl_doctor.graph.state import ApprovalDecision, Budget, Hypothesis, HypothesisSet, RunState, Usage, Verification
from evals.inject import build, load_scenario
from tests.fake_brain import make_brain


@pytest.fixture(scope="module")
def bundle(tmp_path_factory) -> Path:
    return build(load_scenario("f1_date_format"), "silent", {}, tmp_path_factory.mktemp("cases")) / "bundle"


def ctx(**kw) -> GraphContext:
    brain = make_brain(**kw)
    return GraphContext(strong=brain, fast=brain)


def approve(**kw) -> ApprovalDecision:
    return ApprovalDecision(**{"decision": "approve", "approver": "tester", "decided_at": datetime.now(timezone.utc), **kw})


def test_happy_path_pauses_for_approval_then_fixes(bundle, tmp_path):
    db, nodes = tmp_path / "cp.db", []
    s = asyncio.run(start_run(bundle, "local", ctx(), run_id="r1", db_path=db, on_node=lambda n, u: nodes.append(n)))
    assert nodes[-3:] == ["propose_fix", "release_sandbox", "__interrupt__"]
    assert s.report is None and [e.id for e in s.evidence] == ["ev-001", "ev-002"]  # IDs continue across nodes

    req = asyncio.run(pending_approval("r1", db_path=db))  # e.g. from another process, later
    assert "+++ b/demo_pipeline/pipeline/transform.py" in req["patch"] and "coalesce" in req["patch"]

    nodes.clear()
    s = asyncio.run(decide("r1", approve(), ctx(), db_path=db, on_node=lambda n, u: nodes.append(n)))
    assert nodes == ["approval_gate", "apply_fix", "report", "teardown"]
    assert s.report.status == "fixed" and s.validation.passed
    assert {c.name for c in s.validation.checks} >= {"no_rows_lost", "quality_tests_last_good", "order_date_matches_partition"}
    assert s.report.approvals[0].approver == "tester"  # audit trail
    assert "coalesce" in s.report.patch


def test_rejection_feedback_reaches_the_next_proposal(bundle, tmp_path):
    db = tmp_path / "cp.db"
    c = ctx(fixes=["regress", "good"])
    asyncio.run(start_run(bundle, "local", c, run_id="r2", db_path=db))
    assert "config.yaml" in asyncio.run(pending_approval("r2", db_path=db))["patch"]
    asyncio.run(decide("r2", approve(decision="reject", feedback="breaks the old files"), c, db_path=db))
    req = asyncio.run(pending_approval("r2", db_path=db))
    assert req["attempt"] == 2 and "transform.py" in req["patch"]
    s = asyncio.run(decide("r2", approve(), c, db_path=db))
    assert s.report.status == "fixed" and "breaks the old files" in s.fix_feedback[0]


def test_regressing_fix_fails_validation_and_run_ends_unfixed(bundle, tmp_path):
    db = tmp_path / "cp.db"
    c = ctx(fixes=["regress"])
    asyncio.run(start_run(bundle, "local", c, run_id="r3", db_path=db))
    s = asyncio.run(decide("r3", approve(), c, db_path=db))   # human approves a bad fix...
    assert not s.validation.passed                              # ...the sandbox check catches it
    failed = {ch.name for ch in s.validation.checks if not ch.ok}
    assert "quality_tests_last_good" in failed and "no_rows_lost" in failed
    while s.report is None:                                    # every retry is the same bad fix, approved again
        s = asyncio.run(decide("r3", approve(), c, db_path=db))
    assert s.fix_attempts == s.budget.max_fix_attempts
    assert s.report.status == "diagnosed_unfixed" and s.report.patch is None
    assert "failed validation" in s.report.terminal_reason


def test_forbidden_edit_never_reaches_a_human(bundle, tmp_path):
    db = tmp_path / "cp.db"
    asyncio.run(start_run(bundle, "local", ctx(fixes=["forbidden", "good"]), run_id="r4", db_path=db))
    req = asyncio.run(pending_approval("r4", db_path=db))
    assert "test_quality.py" not in req["patch"] and "transform.py" in req["patch"]


def test_abort_keeps_the_diagnosis(bundle, tmp_path):
    db = tmp_path / "cp.db"
    asyncio.run(start_run(bundle, "local", ctx(), run_id="r5", db_path=db))
    s = asyncio.run(decide("r5", approve(decision="abort"), ctx(), db_path=db))
    assert s.report.status == "diagnosed_unfixed" and s.report.diagnosis.failure_class == "F1"
    assert s.validation is None  # nothing was applied


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
    assert nodes[-1] == "__interrupt__" and s.proposal is not None  # now waiting for a human


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
    ({"outcome": "confirmed"}, "propose_fix"),
    ({"outcome": "falsified", "verifications": 1}, "investigate"),
    ({"outcome": "falsified", "verifications": 2}, "escalate"),
    ({"outcome": "inconclusive", "verifications": 1, "tokens": 10**6}, "escalate"),
])
def test_route_after_verify(kw, expected):
    assert route_after_verify(_state(**kw)) == expected


def test_validation_cache_is_per_workspace(tmp_path_factory):
    """Same edits on two different bundles must be validated separately."""
    from edtools.validate import fix_id
    from tests.fake_brain import FIXES

    out = tmp_path_factory.mktemp("two")
    a = build(load_scenario("f1_date_format"), "silent", {}, out / "a") / "bundle"
    b = build(load_scenario("f4_type_drift"), "silent", {}, out / "b") / "bundle"
    assert fix_id(FIXES["good"], a) != fix_id(FIXES["good"], b)
    assert fix_id(FIXES["good"], a) == fix_id(FIXES["good"], a)


def test_requoted_old_text_snaps_to_the_real_file(bundle):
    from etl_doctor.fixes import edit_problems, repair_edits
    from etl_doctor.graph.state import FileEdit

    # What Nemotron Ultra actually sent: single quotes where the file has double quotes.
    e = FileEdit(path="demo_pipeline/pipeline/config.yaml", old_text="date_format: '%Y-%m-%d'", new_text="date_formats: ['%Y-%m-%d']")
    assert edit_problems(bundle, [e])  # exact match fails
    fixed = repair_edits(bundle, [e])
    assert fixed[0].old_text == 'date_format: "%Y-%m-%d"' and not edit_problems(bundle, fixed)
    # An ambiguous loose match is left alone, so the model is asked again.
    amb = FileEdit(path="demo_pipeline/pipeline/transform.py", old_text="pl.col(", new_text="x")
    assert repair_edits(bundle, [amb])[0].old_text == "pl.col("


def test_flattened_multiline_text_is_not_snapped(bundle):
    """What Ultra sent once: a whole multi-line config, flattened onto one line."""
    from etl_doctor.fixes import repair_edits
    from etl_doctor.graph.state import FileEdit

    cfg = (bundle / "demo_pipeline/pipeline/config.yaml").read_text()
    flat = "  ".join(cfg.splitlines())
    e = FileEdit(path="demo_pipeline/pipeline/config.yaml", old_text=flat, new_text="x")
    assert repair_edits(bundle, [e])[0].old_text == flat  # untouched -> validator asks again


def test_truncated_fragment_and_broken_syntax_are_rejected(bundle):
    from etl_doctor.fixes import edit_problems, syntax_problems
    from etl_doctor.graph.state import FileEdit

    # What Ultra sent: old_text cut off at a quote. Unique, but mid-line.
    frag = FileEdit(path="demo_pipeline/pipeline/transform.py", old_text="    strict = cfg[", new_text="    strict = cfg[")
    assert any("complete lines" in p for p in edit_problems(bundle, [frag]))
    broken = FileEdit(path="demo_pipeline/pipeline/transform.py", old_text='    strict = cfg["strict_parsing"]',
                      new_text='    strict = cfg["strict_parsing"]\n    )')
    assert not edit_problems(bundle, [broken]) and syntax_problems(bundle, [broken])


def test_quote_only_edit_is_a_no_op(bundle):
    """What MiniMax once sent: the same line with ' instead of "."""
    from etl_doctor.fixes import edit_problems
    from etl_doctor.graph.state import FileEdit

    line = '        pl.col("order_date").str.strptime(pl.Date, cfg["date_format"], strict=strict),'
    e = FileEdit(path="demo_pipeline/pipeline/transform.py", old_text=line, new_text=line.replace('"', "'"))
    assert any("changes nothing" in p for p in edit_problems(bundle, [e]))
