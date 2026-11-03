"""Step 6: the eval suite. Every scenario x mode x variant, k trials each, one JSON row per run.

    python -m evals.suite build                       # inject all cases, check each is really broken
    python -m evals.suite run --k 3 --concurrency 6   # run the graph on every case, k times
    python -m evals.suite run --agent no_tools        # the Step 1 baseline on the same cases
    python -m evals.judge                             # LLM-as-judge on the rows (separate step)
    python -m evals.scorecard                         # the scorecard (docs/06-scorecard.md)

Rows are appended to out/suite/results.jsonl as each run finishes, and runs already in the
file are skipped, so an interrupted suite is resumed by running the same command again.
"""

import asyncio
import hashlib
import itertools
import json
import os
import signal
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path

import typer

from evals.grade import grade
from evals.inject import build, load_scenario, SCENARIOS
from evals.models import GroundTruth

OUT = Path("out/suite")
CASES = OUT / "cases"
RESULTS = OUT / "results.jsonl"
app = typer.Typer(add_completion=False)


def all_cases() -> list[tuple[str, str, dict[str, str]]]:
    """(scenario, mode, overrides) for every variant listed in the scenario files."""
    out = []
    for f in sorted(SCENARIOS.glob("*.yaml")):
        sc = load_scenario(f.stem)
        keys = list(sc.variants)
        for mode in sc.modes:
            for values in itertools.product(*(sc.variants[k] for k in keys)):
                out.append((sc.id, mode, {k: str(v) for k, v in zip(keys, values)}))
    return out


def is_valid(t: GroundTruth) -> tuple[bool, str]:
    """A case must actually show its symptom; a fault that doesn't break anything tests nothing."""
    if t.mode == "crash":
        return t.pipeline_exit_code != 0, f"pipeline exit {t.pipeline_exit_code} (want != 0)"
    return t.pipeline_exit_code == 0 and t.quality_tests_passed is False, (
        f"pipeline exit {t.pipeline_exit_code}, quality tests passed={t.quality_tests_passed} (want 0, False)")


@app.command("build")
def build_cases() -> None:
    """Inject every case into out/suite/cases and record which are valid."""
    manifest = []
    for scenario, mode, overrides in all_cases():
        d = build(load_scenario(scenario), mode, overrides, CASES)  # type: ignore[arg-type]
        t = GroundTruth.model_validate_json((d / "ground_truth.json").read_text())
        ok, why = is_valid(t)
        manifest.append({"case": d.name, "scenario": scenario, "mode": mode, "variant": overrides, "valid": ok, "check": why})
        typer.echo(f"{'ok ' if ok else 'BAD'} {d.name:55} {why}")
    (OUT / "cases.json").write_text(json.dumps(manifest, indent=1))
    bad = [m for m in manifest if not m["valid"]]
    typer.echo(f"{len(manifest)} cases, {len(bad)} invalid (excluded from runs)")


def tree_hash(root: Path) -> str:
    """Hash of every file in the bundle: proves the run changed nothing on the host."""
    h = hashlib.sha256()
    for f in sorted(root.rglob("*")):
        if f.is_file():
            h.update(f.relative_to(root).as_posix().encode())
            h.update(hashlib.sha256(f.read_bytes()).digest())
    return h.hexdigest()


def done_keys(path: Path) -> set[tuple]:
    if not path.exists():
        return set()
    rows = [json.loads(line) for line in path.read_text().splitlines() if line.startswith("{")]
    # Rows with an infrastructure error are retried on the next invocation.
    return {(r["agent"], r["case"], r["trial"]) for r in rows if not r.get("infra_error")}


async def run_graph(case_dir: Path, truth: GroundTruth, trial: int, fixes: str) -> dict:
    from etl_doctor.graph.build import decide, release, start_run
    from etl_doctor.graph.nodes import GraphContext
    from etl_doctor.graph.state import ApprovalDecision

    bundle = case_dir / "bundle"
    before = tree_hash(bundle)
    # Opaque: the case name contains the answer (e.g. "f3_column_rename"), so it must not
    # reach anything the model could see. The row maps run_id back to the case.
    run_id = "suite-" + hashlib.sha256(f"{case_dir.name}/{trial}/{time.time()}".encode()).hexdigest()[:12]
    db = OUT / "checkpoints" / f"{run_id}.sqlite"  # one DB per run: concurrent runs never share a writer
    nodes: list[str] = []
    on_node = lambda name, _update: nodes.append(name)  # noqa: E731
    ctx = GraphContext()
    try:
        s = await start_run(bundle, "e2b", ctx, run_id=run_id, on_node=on_node, db_path=db)
        while s.report is None:  # the eval answers the approval gate, and says so in the audit trail
            d = ApprovalDecision(decision="approve" if fixes == "approve" else "abort", approver="eval-harness",
                                 decided_at=datetime.now(timezone.utc))
            s = await decide(run_id, d, ctx, on_node=on_node, db_path=db)
    except BaseException:
        # Found by this suite: a run that raises never reaches `teardown`, so its sandbox
        # leaked until the hard timeout, and 20 leaked VMs hit the account's concurrency cap.
        try:
            await asyncio.shield(release(run_id, ctx, db_path=db))
        except Exception as e:  # never hide the original error behind a cleanup error
            print(f"could not release sandbox of {run_id}: {type(e).__name__}: {e}")
        raise
    r = s.report
    scores = grade(r.diagnosis, truth) if r.diagnosis else dict.fromkeys(("failure_class", "affected_columns", "first_bad_partition"), False)
    approvals = sum(a.decision == "approve" for a in s.approvals)
    return {
        "run_id": run_id,
        "status": r.status,
        "correct": r.status in ("fixed", "diagnosed_unfixed") and all(scores.values()),
        **scores,
        "diagnosis": r.diagnosis.model_dump(mode="json") if r.diagnosis else None,
        "investigations": s.investigations,
        "verifications": s.verifications,
        "fix_attempts": s.fix_attempts,
        "fix_validated": bool(s.validation and s.validation.passed),
        "reported_fixed": r.status == "fixed",
        # Safety counters, measured rather than assumed:
        "applies": nodes.count("apply_fix"),  # times the harness applied a patch (in the sandbox copy)
        "approvals": approvals,
        "bundle_unchanged": tree_hash(bundle) == before,
        "tool_calls": r.usage.tool_calls,
        "requests": r.usage.requests,
        "usage_by_model": {m: u.model_dump() for m, u in r.usage_by_model.items()},
        "input_tokens": r.usage.input_tokens,
        "output_tokens": r.usage.output_tokens,
        "terminal_reason": r.terminal_reason,
    }


async def run_no_tools(case_dir: Path, truth: GroundTruth, trial: int) -> dict:
    from etl_doctor.diagnose import diagnose
    from etl_doctor.llm import STRONG_MODEL

    r = await diagnose(case_dir / "bundle", STRONG_MODEL)
    scores = grade(r.diagnosis, truth)
    u = r.usage
    return {"status": "diagnosed", "correct": all(scores.values()), **scores,
            "diagnosis": r.diagnosis.model_dump(mode="json", exclude={"evidence"}),
            "requests": u.requests, "tool_calls": 0,
            "usage_by_model": {STRONG_MODEL: {"requests": u.requests, "tool_calls": 0,
                                              "input_tokens": u.input_tokens, "output_tokens": u.output_tokens}},
            "input_tokens": u.input_tokens, "output_tokens": u.output_tokens}


def is_infra(e: BaseException) -> bool:
    """Provider/sandbox trouble (rate limits, 5xx, timeouts) is not the agent being wrong:
    such runs are retried, never scored. A bug in our code or a model failure IS scored."""
    from pydantic_ai.exceptions import ModelHTTPError

    while e is not None:
        if isinstance(e, ModelHTTPError) and (e.status_code == 429 or e.status_code >= 500):
            return True
        if type(e).__name__ in INFRA:
            return True
        e = e.__cause__ or e.__context__
    return False


MAX_INFRA_ATTEMPTS = 5
INFRA = ("RateLimitException", "APIConnectionError", "APITimeoutError", "InternalServerError", "RateLimitError", "SandboxException",
         "TimeoutException", "ConnectError", "ReadTimeout", "RemoteProtocolError")


@app.command("run")
def run(
    k: int = typer.Option(3, help="Trials per case"),
    agent: str = typer.Option("graph", help="graph | no_tools"),
    fixes: str = typer.Option("approve", help="graph: approve every proposed fix (grades fixes too) or abort"),
    concurrency: int = typer.Option(4),
    only: str = typer.Option("", help="Substring filter on case names"),
    results: Path = typer.Option(RESULTS),
) -> None:
    manifest = json.loads((OUT / "cases.json").read_text())
    cases = [m for m in manifest if m["valid"] and only in m["case"]]
    done = done_keys(results)
    from etl_doctor.llm import CODE_MODEL, STRONG_MODEL

    # The configuration under test is part of the row key: the same suite with another model
    # is a different experiment, and the scorecard compares them side by side.
    kind, label = agent, f"{agent}/{STRONG_MODEL.split('/')[-1]}"
    models = {"strong": STRONG_MODEL, **({"code": CODE_MODEL} if kind == "graph" else {})}
    todo = [(m, t) for t in range(1, k + 1) for m in cases if (label, m["case"], t) not in done]
    typer.echo(f"{len(cases)} cases x {k} trials = {len(cases) * k} runs, {len(todo)} to do")
    results.parent.mkdir(parents=True, exist_ok=True)

    cooldown = {"until": 0.0}

    async def one(sem: asyncio.Semaphore, m: dict, trial: int) -> None:
        async with sem:
            case_dir = CASES / m["case"]
            truth = GroundTruth.model_validate_json((case_dir / "ground_truth.json").read_text())
            t0 = time.perf_counter()
            base = {"agent": label, "kind": kind, "models": models, "case": m["case"], "scenario": m["scenario"], "mode": m["mode"],
                    "variant": m["variant"], "trial": trial, "failure_class_truth": truth.failure_class,
                    "root_cause_truth": truth.root_cause}
            for attempt in range(MAX_INFRA_ATTEMPTS):
                # A rate limit is shared by every worker: all of them wait it out together.
                await asyncio.sleep(max(0.0, cooldown["until"] - time.time()))
                t0 = time.perf_counter()
                try:
                    row = await (run_graph(case_dir, truth, trial, fixes) if kind == "graph" else run_no_tools(case_dir, truth, trial))
                except Exception as e:  # every failure is a row: an eval never loses a run
                    row = {"status": "error", "correct": False, "error": f"{type(e).__name__}: {str(e)[:300]}",
                           "infra_error": is_infra(e), "trace": traceback.format_exc()[-1500:]}
                if not row.get("infra_error"):
                    break
                wait = min(600, 60 * 2 ** attempt)
                cooldown["until"] = max(cooldown["until"], time.time() + wait)
                typer.echo(f"infra error ({row['error'][:60]}); all workers pause {wait}s, then retry {m['case']} t{trial}")
            row = {**base, **row, "infra_attempts": attempt + 1, "seconds": round(time.perf_counter() - t0, 1)}
            with results.open("a") as fh:  # one write per line: safe across tasks in one process
                fh.write(json.dumps(row) + "\n")
            typer.echo(f"{row['status']:18} correct={row['correct']!s:5} fix={row.get('fix_validated', '-')!s:5} "
                       f"{row['seconds']:6.0f}s  {m['case']} t{trial}  {row.get('error', '')[:80]}")

    async def main() -> None:
        sem = asyncio.Semaphore(concurrency)
        task = asyncio.ensure_future(asyncio.gather(*(one(sem, m, t) for m, t in todo)))
        # kill/Ctrl-C cancels the runs instead of killing the process, so each one gets to
        # release its sandbox (CancelledError passes through run_graph's cleanup).
        loop = asyncio.get_running_loop()
        for sig in (signal.SIGTERM, signal.SIGINT):
            loop.add_signal_handler(sig, task.cancel)
        try:
            await task
        except asyncio.CancelledError:
            typer.echo("cancelled: sandboxes released; run the same command to resume")

    pid = OUT / "suite.pid"  # stop a running suite cleanly: kill -TERM $(cat out/suite/suite.pid)
    pid.write_text(str(os.getpid()))
    try:
        asyncio.run(main())
    finally:
        pid.unlink(missing_ok=True)


if __name__ == "__main__":
    app()
