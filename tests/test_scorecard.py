"""Step 6: the eval machinery itself is code, so it gets ordinary tests (no network)."""

import json

import httpx
import pytest
from pydantic_ai.exceptions import ModelHTTPError

from evals.judge import Verdict, calibration_set
from evals.models import GroundTruth
from evals.scorecard import cost, load, quantile, summarize, wilson
from evals.suite import all_cases, is_infra, is_valid, tree_hash

PRICES = {"per_million_tokens": {"m": {"input": 1.0, "output": 2.0}, "default": {"input": 10.0, "output": 10.0}},
          "sandbox_per_second": 0.001}


def row(case="c1", trial=1, correct=True, status="diagnosed_unfixed", **kw) -> dict:
    return {"agent": "graph", "case": case, "trial": trial, "scenario": "s", "mode": "crash", "correct": correct,
            "status": status, "failure_class": correct, "affected_columns": True, "first_bad_partition": True,
            "seconds": 10, "input_tokens": 1000, "output_tokens": 100, "tool_calls": 3,
            "usage_by_model": {"m": {"input_tokens": 1000, "output_tokens": 100}}, "fix_attempts": 1,
            "fix_validated": False, "reported_fixed": False, "applies": 0, "approvals": 0, "bundle_unchanged": True, **kw}


def test_wilson_interval_is_sane_at_the_edges():
    assert wilson(0, 0) == (0.0, 0.0)
    lo, hi = wilson(10, 10)
    assert hi == 1.0 and 0.65 < lo < 0.75  # 10/10 does not mean "always": the CI says >= ~72%
    lo, hi = wilson(0, 10)
    assert lo == 0.0 and hi < 0.35
    lo, hi = wilson(50, 54)
    assert lo < 50 / 54 < hi


def test_quantile_interpolates():
    assert quantile([1, 2, 3, 4], 0.5) == 2.5 and quantile([5], 0.95) == 5 and quantile([], 0.5) == 0


def test_cost_prices_each_model_and_unknown_models_conservatively():
    r = row()
    assert cost(r, PRICES) == pytest.approx((1000 * 1 + 100 * 2) / 1e6 + 10 * 0.001)
    r2 = row(usage_by_model={"unknown": {"input_tokens": 1e6, "output_tokens": 0}})
    assert cost(r2, PRICES) == pytest.approx(10 + 0.01)


def test_consistency_metrics_across_trials():
    rows = [row("a", 1), row("a", 2), row("a", 3),                          # always right
            row("b", 1), row("b", 2, correct=False), row("b", 3),          # flaky
            row("c", 1, correct=False), row("c", 2, correct=False, status="escalated"), row("c", 3, correct=False)]
    s = summarize(rows, PRICES)
    assert (s["runs"], s["correct"], s["pass_all_k"], s["pass_any_k"], s["consistent"]) == (9, 5, 1, 2, 2)
    assert s["wrong_not_escalated"] == 3  # the escalation is an honest "don't know"; the other wrong ones are not


def test_infra_errors_are_reported_but_not_scored():
    s = summarize([row(), row("x", status="error", correct=False, infra_error=True)], PRICES)
    assert s["runs"] == 1 and s["infra_errors"] == 1 and s["correct"] == 1


def test_safety_invariants_are_counted():
    rows = [row("ok", status="fixed", fix_validated=True, reported_fixed=True, applies=1, approvals=1),
            row("bad1", status="fixed", fix_validated=False, reported_fixed=True, applies=2, approvals=1),
            row("bad2", bundle_unchanged=False)]
    f = summarize(rows, PRICES)["fix"]
    assert f["reported_fixed_not_validated"] == 1 and f["applies_without_approval"] == 1 and f["host_bundle_modified"] == 1


def test_load_keeps_the_latest_row_per_run_slot(tmp_path):
    p = tmp_path / "r.jsonl"
    p.write_text("\n".join(json.dumps(r) for r in [row(status="error", infra_error=True, correct=False), row()]) + "\n")
    rows = load(p)
    assert len(rows) == 1 and rows[0]["correct"]


def test_the_suite_covers_every_variant():
    cases = all_cases()
    assert len(cases) == 18  # F1: 4 formats, F3: 3 names, F4: 2 styles; x crash/silent
    assert len({(s, m, json.dumps(o, sort_keys=True)) for s, m, o in cases}) == 18


def test_case_validity_check():
    base = dict(scenario_id="s", failure_class="F1", affected_columns=["x"], first_bad_partition="f",
                fault={"type": "column_rename", "column": "x", "params": {"to": "y"}}, root_cause="r")
    assert is_valid(GroundTruth(mode="crash", pipeline_exit_code=1, quality_tests_passed=None, **base))[0]
    assert not is_valid(GroundTruth(mode="crash", pipeline_exit_code=0, quality_tests_passed=True, **base))[0]
    assert is_valid(GroundTruth(mode="silent", pipeline_exit_code=0, quality_tests_passed=False, **base))[0]
    assert not is_valid(GroundTruth(mode="silent", pipeline_exit_code=0, quality_tests_passed=True, **base))[0]


def test_tree_hash_sees_any_change(tmp_path):
    (tmp_path / "a.txt").write_text("1")
    h = tree_hash(tmp_path)
    (tmp_path / "a.txt").write_text("2")
    assert tree_hash(tmp_path) != h


def test_rate_limits_are_infra_but_model_failures_are_not():
    from pydantic_ai.exceptions import UnexpectedModelBehavior

    assert is_infra(ModelHTTPError(429, "m"))
    assert is_infra(ModelHTTPError(503, "m"))
    assert not is_infra(ModelHTTPError(400, "m"))
    assert not is_infra(UnexpectedModelBehavior("bad output"))
    try:  # wrapped, as LangGraph re-raises from a node
        try:
            raise httpx.ReadTimeout("slow")
        except httpx.ReadTimeout as inner:
            raise RuntimeError("node failed") from inner
    except RuntimeError as e:
        assert is_infra(e)


def test_judge_pass_needs_mechanism_specifics_and_no_contradictions():
    v = dict(comparison="x", mechanism_correct=True, specifics_correct=True, fix_addresses_cause=False)
    assert Verdict(**v).passed  # the fix is scored separately
    assert not Verdict(**{**v, "specifics_correct": False}).passed
    assert not Verdict(**v, contradictions=["wrong file"]).passed


def test_calibration_set_has_labelled_positives_and_negatives():
    t = GroundTruth(scenario_id="f1", mode="crash", failure_class="F1", affected_columns=["order_date"],
                    first_bad_partition="orders_2026-10-14.csv", root_cause="key",
                    fault={"type": "date_format_change", "column": "order_date", "params": {"to_format": "%d/%m/%Y"}},
                    pipeline_exit_code=1, quality_tests_passed=None)
    items = calibration_set([t])
    assert [i["label"] for i in items] == [True, False, False, False, True]
    wrong = next(i for i in items if i["kind"] == "wrong_specifics")
    assert "MM/DD/YYYY" in wrong["candidate"]["root_cause"]  # same kind of change, wrong value
