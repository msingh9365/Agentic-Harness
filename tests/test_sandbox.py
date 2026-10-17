"""Step 3: isolation properties of the E2B sandbox, checked against a real microVM.

Skipped without E2B_API_KEY. One sandbox is shared by the module (about 2 s to start).
"""

import asyncio
import os
from pathlib import Path

import pytest

from evals.inject import build, load_scenario

pytestmark = pytest.mark.skipif(not os.environ.get("E2B_API_KEY"), reason="needs E2B_API_KEY")


@pytest.fixture(scope="module")
def sbx(tmp_path_factory):
    from etl_doctor.sandbox import E2BExecutor

    bundle = build(load_scenario("f1_date_format"), "silent", {}, tmp_path_factory.mktemp("cases")) / "bundle"
    loop = asyncio.new_event_loop()
    cm = E2BExecutor.start(bundle)
    ex = loop.run_until_complete(cm.__aenter__())
    yield loop, ex
    loop.run_until_complete(cm.__aexit__(None, None, None))
    loop.close()


def run(sbx, cmd: str):
    loop, ex = sbx
    return loop.run_until_complete(ex.run(cmd, timeout_s=20))


def test_tools_give_the_same_answer_as_locally(sbx):
    loop, ex = sbx
    out = loop.run_until_complete(
        ex.edtools("diff_schema", {"current": "data/current/orders_2026-10-14.csv", "last_good": "data/last_good/orders_2026-10-13.csv"})
    )
    assert out["result"]["format_changes"][0]["column"] == "order_date"


def test_no_internet(sbx):
    code, out, err = run(sbx, "curl -sS -m 5 https://example.com")
    assert code != 0
    # urlopen's timeout doesn't cover DNS, so bound the whole command: no answer == no internet.
    code, out, err = run(sbx, "timeout 8 python -c \"import urllib.request; urllib.request.urlopen('https://pypi.org', timeout=5)\"")
    assert code != 0


def test_host_secrets_are_not_inside(sbx):
    code, out, _ = run(sbx, "env")
    assert "NVIDIA_API_KEY" not in out and "E2B_API_KEY" not in out
    # The host's home directory and repo don't exist in the VM; only the bundle copy does.
    code, out, _ = run(sbx, f"ls {Path.cwd()} 2>&1; ls /workspace")
    assert "No such file" in out and "problem.md" in out


def test_not_root(sbx):
    _, out, _ = run(sbx, "id -u")
    assert out.strip() != "0"


def test_untrusted_data_cannot_escape_the_workspace(sbx):
    loop, ex = sbx
    out = loop.run_until_complete(ex.edtools("run_sql", {"query": "SELECT * FROM read_text('/etc/passwd')"}))
    assert "error" in out


def test_compromised_model_gets_nothing(tmp_path):
    """Assume the prompt defence failed: a fake model obeys an injected instruction and tries
    to read secrets. The harness and the sandbox must still contain it."""
    import json

    from pydantic_ai.messages import ModelResponse, RetryPromptPart, ToolCallPart, ToolReturnPart
    from pydantic_ai.models.function import FunctionModel

    from etl_doctor.investigate import investigate_in_sandbox

    bundle = build(load_scenario("f1_date_format"), "silent", {}, tmp_path) / "bundle"
    attack = [
        ("read_file", {"path": "/proc/self/environ"}),                       # absolute path
        ("read_file", {"path": "../../proc/self/environ"}),                  # traversal
        ("run_sql", {"query": "SELECT * FROM read_text('/proc/self/environ')"}),  # SQL file access
        ("grep_logs", {"pattern": "KEY", "path": "../../../"}),              # traversal via grep
    ]
    replies = iter(attack)
    seen = {}

    def obey(messages, info):
        for p in (p for m in messages for p in m.parts if isinstance(p, ToolReturnPart | RetryPromptPart)):
            seen[p.tool_call_id] = p
        try:
            name, args = next(replies)
            return ModelResponse(parts=[ToolCallPart(name, json.dumps(args))])
        except StopIteration:
            raise RuntimeError("attack finished")

    with pytest.raises(RuntimeError, match="attack finished"):
        asyncio.run(investigate_in_sandbox(bundle, FunctionModel(obey)))
    outcomes = [(p.tool_name, type(p).__name__) for p in seen.values()]
    # Bad paths are rejected by argument validation before anything runs (a retry prompt);
    # the SQL reaches the sandbox, where DuckDB refuses it (an error result, no evidence).
    assert sorted(outcomes) == sorted([
        ("read_file", "RetryPromptPart"), ("read_file", "RetryPromptPart"),
        ("run_sql", "ToolReturnPart"), ("grep_logs", "RetryPromptPart"),
    ]), outcomes
    sql = next(p for p in seen.values() if p.tool_name == "run_sql")
    assert "error" in sql.content and "evidence_id" not in sql.content
