"""Web UI: the API drives the same checkpointed graph as the CLI (scripted model, local tools)."""

import base64
import time

import pytest
from fastapi.testclient import TestClient
from pydantic_ai.models.function import FunctionModel

from etl_doctor.graph.nodes import GraphContext
from etl_doctor.web.app import Settings, create_app
from tests.fake_brain import make_brain

CASE = "f1_date_format__silent__to_format-dmY"
POST = {"x-etldoc": "1"}


def scripted(on_evidence) -> GraphContext:
    brain = make_brain()
    return GraphContext(strong=brain, fast=brain, on_evidence=on_evidence)


def broken(on_evidence) -> GraphContext:
    def boom(messages, info):
        raise RuntimeError("model endpoint down")

    return GraphContext(strong=FunctionModel(boom), fast=FunctionModel(boom), on_evidence=on_evidence)


def basic(user: str, pw: str) -> dict:
    return {"authorization": "Basic " + base64.b64encode(f"{user}:{pw}".encode()).decode()}


@pytest.fixture(scope="module")
def data_dir(tmp_path_factory):
    return tmp_path_factory.mktemp("web")  # shared: the broken bundle is built once


def wait_for(client, run_id, statuses, headers=None, timeout=90) -> dict:
    t0 = time.time()
    while time.time() - t0 < timeout:
        r = client.get(f"/api/runs/{run_id}", headers=headers).json()
        if r["status"] in statuses:
            return r
        time.sleep(0.2)
    raise AssertionError(f"{run_id} still {r['status']}")


def test_run_approve_and_report_through_the_api(data_dir):
    alice = basic("alice", "pw")
    s = Settings(data_dir=data_dir, users={"alice": "pw"}, allow_local_sandbox=True, make_context=scripted)
    with TestClient(create_app(s)) as c:
        assert c.get("/").status_code == 401  # login first
        page = c.get("/", headers=alice)
        assert page.status_code == 200 and "script-src 'self'" in page.headers["content-security-policy"]
        assert c.get("/api/config", headers=alice).json()["user"] == "alice"

        # CSRF: a POST without the custom header is refused even when logged in.
        assert c.post("/api/runs", json={"case": CASE, "sandbox": "local"}, headers=alice).status_code == 403
        r = c.post("/api/runs", json={"case": CASE, "sandbox": "local"}, headers={**alice, **POST})
        assert r.status_code == 201, r.text
        run_id = r.json()["run_id"]

        run = wait_for(c, run_id, {"awaiting_approval", "stopped"}, alice)
        assert run["status"] == "awaiting_approval", run
        assert "+++ b/demo_pipeline/pipeline/transform.py" in run["approval"]["patch"]
        assert run["state"]["evidence"] and "data" not in run["state"]["evidence"][0]  # summaries only
        assert run["meta"]["started_by"] == "alice"

        events = c.app.state.runs.events(run_id, -1)
        kinds = [e.get("node") or e["type"] for e in events]
        assert "triage" in kinds and "evidence" in kinds and kinds[-2:] == ["__interrupt__", "status"]

        bad = c.post(f"/api/runs/{run_id}/decision", json={"decision": "reject"}, headers={**alice, **POST})
        assert bad.status_code == 422 and "feedback" in bad.text  # a rejection must say why

        ok = c.post(f"/api/runs/{run_id}/decision", json={"decision": "approve", "approver": "mallory"},
                    headers={**alice, **POST})
        assert ok.status_code == 200
        again = c.post(f"/api/runs/{run_id}/decision", json={"decision": "approve"}, headers={**alice, **POST})
        assert again.status_code == 409  # double click / second reviewer

        run = wait_for(c, run_id, {"fixed", "diagnosed_unfixed", "escalated", "stopped"}, alice)
        assert run["status"] == "fixed"
        report = run["state"]["report"]
        assert report["approvals"][0]["approver"] == "alice"  # the login, not the claimed name
        assert run["answer_key"]["grade"] == {"failure_class": True, "affected_columns": True, "first_bad_partition": True}
        p = c.get(f"/api/runs/{run_id}/patch", headers=alice)
        assert p.status_code == 200 and "coalesce" in p.text and "attachment" in p.headers["content-disposition"]
        assert [r["run_id"] for r in c.get("/api/runs", headers=alice).json()] == [run_id]
        assert c.get(f"/api/runs/{run_id}/history", headers=alice).json()[0]["next"] == []


def test_failed_run_is_stopped_then_resumable(data_dir):
    s = Settings(data_dir=data_dir, allow_local_sandbox=True, make_context=broken)
    with TestClient(create_app(s)) as c:
        assert c.post("/api/runs", json={"case": CASE, "sandbox": "local"}, headers=POST).status_code == 422  # name needed
        run_id = c.post("/api/runs", json={"case": CASE, "sandbox": "local", "approver": "bob"}, headers=POST).json()["run_id"]
        run = wait_for(c, run_id, {"stopped"})
        assert run["state"] is not None  # checkpointed up to the failing step
        errors = [e for e in c.app.state.runs.events(run_id, -1) if e["type"] == "error"]
        assert "model endpoint down" in errors[0]["message"]

        s.make_context = scripted  # the endpoint is back
        assert c.post(f"/api/runs/{run_id}/resume", headers=POST).status_code == 200
        assert wait_for(c, run_id, {"awaiting_approval", "stopped"})["status"] == "awaiting_approval"
        assert c.post(f"/api/runs/{run_id}/resume", headers=POST).status_code == 409  # not stopped any more


def test_guards(data_dir, monkeypatch):
    s = Settings(data_dir=data_dir, make_context=scripted, max_runs_per_day=0)
    with TestClient(create_app(s)) as c:
        assert c.post("/api/runs", json={"case": CASE, "sandbox": "local", "approver": "x"}, headers=POST).status_code == 422
        assert c.post("/api/runs", json={"case": "nope", "approver": "x"}, headers=POST).status_code == 422
        assert c.post("/api/runs", json={"case": CASE, "approver": "x"}, headers=POST).status_code == 429  # daily cap
        assert c.get("/api/runs/..%2F..%2Fetc").status_code == 404
        assert c.get("/api/runs/run-20990101-000000-abcd").status_code == 404
        assert c.get("/healthz").json() == {"ok": True}
