"""etl-doctor diagnose <bundle> [--no-tools]"""

import asyncio
import getpass
import sys
from datetime import datetime, timezone
from pathlib import Path

import typer

from etl_doctor.llm import STRONG_MODEL

app = typer.Typer(no_args_is_help=True, add_completion=False)


@app.callback()
def _main() -> None:
    """ETL Doctor: diagnose broken ETL pipelines."""


def print_evidence(ev) -> None:
    typer.secho(f"  {ev.id}  {ev.tool:<15} {ev.summary[:150]}", fg="cyan", err=True)


@app.command()
def diagnose(
    bundle: Path = typer.Argument(..., exists=True, file_okay=False, help="Bundle directory"),
    model: str = typer.Option(STRONG_MODEL, help="Model id on the NVIDIA API"),
    no_tools: bool = typer.Option(False, "--no-tools", help="Step 1 baseline: everything in the prompt, no tools"),
    sandbox: str = typer.Option("e2b", help="Where tools run: e2b (isolated microVM) or local (subprocess, dev only)"),
    show_prompt: bool = typer.Option(False, help="--no-tools only: print the exact context sent to the model, then exit"),
) -> None:
    """Diagnose a bundle and print a validated diagnosis as JSON."""
    if no_tools:
        from etl_doctor.context import build_context
        from etl_doctor.diagnose import PROMPT, diagnose as run_diagnose

        if show_prompt:
            typer.echo(f"=== system instructions ===\n{PROMPT}\n=== user prompt ===\n{build_context(bundle).render()}")
            raise typer.Exit()
        r = asyncio.run(run_diagnose(bundle, model))
        typer.echo(r.diagnosis.model_dump_json(indent=2))
    else:
        from etl_doctor.investigate import investigate, investigate_in_sandbox

        if sandbox == "e2b":
            ready = lambda ex: typer.secho(f"sandbox {ex.sandbox_id} ready (no internet)", err=True, bold=True)
            run = investigate_in_sandbox(bundle, model, on_evidence=print_evidence, on_ready=ready)
        elif sandbox == "local":
            typer.secho("WARNING: tools run on this machine, not isolated", err=True, fg="yellow")
            run = investigate(bundle, model, on_evidence=print_evidence)
        else:
            raise typer.BadParameter("--sandbox must be e2b or local")
        typer.secho("tool calls (evidence recorded by the harness):", err=True, bold=True)
        r = asyncio.run(run)
        typer.echo(r.diagnosis.model_dump_json(indent=2))
        typer.secho("\ncited evidence:", err=True, bold=True)
        for ev in r.cited():
            print_evidence(ev)
        if r.sandbox_seconds is not None:
            typer.echo(f"sandbox_seconds={r.sandbox_seconds}", err=True)
    u = r.usage
    typer.echo(
        f"\nmodel={r.model} requests={u.requests} tool_calls={u.tool_calls} retries={r.retries} "
        f"input_tokens={u.input_tokens} output_tokens={u.output_tokens}",
        err=True,
    )


def print_node(name: str, update: dict) -> None:
    from etl_doctor.progress import NODE_LABEL, node_detail

    if name == "__interrupt__":
        typer.secho("[approval_gate] waiting for a human decision (run is checkpointed)", err=True, fg="yellow", bold=True)
        return
    typer.secho(f"[{name}] {NODE_LABEL.get(name, name)} {node_detail(name, update)}", err=True,
                fg="green" if name != "escalate" else "red")


def print_approval_card(req: dict) -> None:
    h, p, v = req["hypothesis"], req["proposal"], req["verification"]
    line = "=" * 78
    typer.secho(f"\n{line}\nAPPROVAL NEEDED  run {req['run_id']}  (proposal {req['attempt']})\n{line}", bold=True)
    typer.echo(f"Diagnosis   {h['failure_class']} {h['statement']}")
    typer.echo(f"            columns {h['affected_columns']}, first bad file {h['first_bad_partition']}, confidence {h['confidence']}")
    typer.echo(f"Verified    {v['outcome']}: {v['observations'][:200]}")
    typer.echo("Evidence")
    for e in req["evidence"]:
        typer.echo(f"  {e['id']}  {e['tool']:<15} {e['summary'][:110]}")
    typer.secho("\nProposed change (not applied yet):", bold=True)
    for ln in req["patch"].splitlines():
        color = "green" if ln.startswith("+") and not ln.startswith("+++") else "red" if ln.startswith("-") and not ln.startswith("---") else None
        typer.secho("  " + ln, fg=color)
    typer.echo(f"\nRationale   {p['rationale']}")
    typer.echo(f"Blast radius {p['blast_radius']}")
    typer.echo("Expected    " + "; ".join(p["expected_effects"]))
    typer.echo(f"Rollback    {p['rollback']}")
    u = req["usage"]
    typer.echo(f"Fixer confidence {p['confidence']}   cost so far: {u['input_tokens'] + u['output_tokens']} tokens, {u['tool_calls']} tool calls")
    typer.echo("If approved, the harness applies this to a COPY in a fresh sandbox and re-runs the pipeline on")
    typer.echo("current and last-good data. Nothing outside the sandbox is changed.")
    typer.secho(line, bold=True)


async def ask_and_decide(run_id: str) -> None:
    """Show the pending request; ask on a terminal, or explain how to answer later."""
    from etl_doctor.graph.build import pending_approval

    req = await pending_approval(run_id)
    if req is None:
        return
    print_approval_card(req)
    if not sys.stdin.isatty():
        typer.secho(f"\nNo terminal attached. Answer later (from any process):\n"
                    f"  etl-doctor approve {run_id}                    # apply + validate\n"
                    f"  etl-doctor approve {run_id} --reject 'why'     # ask for a different fix\n"
                    f"  etl-doctor approve {run_id} --abort            # keep the diagnosis, no fix", fg="yellow")
        return
    choice = typer.prompt("[a]pprove / [r]eject with feedback / a[b]ort / [l]ater", default="l").strip().lower()
    if choice.startswith("l"):
        typer.echo(f"Left pending. Later: etl-doctor approve {run_id} [--reject 'why' | --abort]")
        return
    decision = {"a": "approve", "r": "reject", "b": "abort"}.get(choice[:1])
    if decision is None:
        typer.echo("Unrecognised answer; left pending.")
        return
    feedback = typer.prompt("What should change?") if decision == "reject" else None
    await _decide(run_id, decision, feedback, getpass.getuser())


async def _decide(run_id: str, decision: str, feedback: str | None, approver: str) -> None:
    from etl_doctor.graph.build import decide
    from etl_doctor.graph.nodes import GraphContext
    from etl_doctor.graph.state import ApprovalDecision

    d = ApprovalDecision(decision=decision, approver=approver, feedback=feedback, decided_at=datetime.now(timezone.utc))
    s = await decide(run_id, d, GraphContext(on_evidence=print_evidence), on_node=print_node)
    if s.report is None:
        await ask_and_decide(run_id)  # a rejection produced a new proposal: ask again
    else:
        print_report(s)


async def _finish(s) -> None:
    """After run/resume: print the report, or the approval card if the run is waiting."""
    if s.report:
        print_report(s)
    else:
        await ask_and_decide(s.run_id)


@app.command()
def approve(
    run_id: str = typer.Argument(...),
    reject: str | None = typer.Option(None, help="Reject, with feedback for the next proposal"),
    abort: bool = typer.Option(False, help="Stop: keep the diagnosis, apply nothing"),
    approver: str = typer.Option(getpass.getuser(), "--as", help="Recorded in the audit trail"),
) -> None:
    """Answer a run's pending approval (works from any process, at any later time)."""
    if reject and abort:
        raise typer.BadParameter("use either --reject or --abort")
    # One event loop per command: HTTP clients must close in the loop that opened them.
    asyncio.run(_decide(run_id, "abort" if abort else "reject" if reject else "approve", reject, approver))


@app.command()
def show(run_id: str = typer.Argument(...)) -> None:
    """Show the approval a run is waiting on, without answering it."""
    from etl_doctor.graph.build import pending_approval

    req = asyncio.run(pending_approval(run_id))
    if req is None:
        typer.echo(f"{run_id} is not waiting for approval")
    else:
        print_approval_card(req)


def print_report(s) -> None:
    r = s.report
    if r is None:
        return
    typer.echo(r.model_dump_json(indent=2, exclude={"usage", "patch"}))
    if r.patch:
        typer.secho(f"\nvalidated patch: .etl_doctor/fixes/{s.run_id}.patch  (apply it yourself: git apply ...)", fg="green", bold=True)
    u = r.usage
    typer.secho(f"\nrun={s.run_id} status={r.status} investigations={s.investigations} verifications={s.verifications} "
                f"requests={u.requests} tool_calls={u.tool_calls} input_tokens={u.input_tokens} output_tokens={u.output_tokens}",
                err=True, bold=True)


@app.command()
def run(
    bundle: Path = typer.Argument(..., exists=True, file_okay=False, help="Bundle directory"),
    sandbox: str = typer.Option("e2b", help="e2b or local"),
    run_id: str | None = typer.Option(None, help="Defaults to a new timestamped ID"),
    crash_before: str | None = typer.Option(None, help="Demo: hard-kill the process before this node, then use `resume`"),
) -> None:
    """The full graph: diagnose, verify, propose a fix, wait for approval, validate. Checkpointed."""
    from etl_doctor.graph.build import new_run_id, start_run
    from etl_doctor.graph.nodes import GraphContext

    run_id = run_id or new_run_id()
    typer.secho(f"run {run_id} (checkpoints: .etl_doctor/checkpoints.sqlite)", err=True, bold=True)
    ctx = GraphContext(on_evidence=print_evidence, crash_before=crash_before)

    async def go():
        await _finish(await start_run(bundle, sandbox, ctx, run_id=run_id, on_node=print_node))

    asyncio.run(go())


@app.command()
def resume(run_id: str = typer.Argument(...)) -> None:
    """Continue a run from its last checkpoint (after a crash, Ctrl-C or error)."""
    from etl_doctor.graph.build import resume_run
    from etl_doctor.graph.nodes import GraphContext

    typer.secho(f"resuming {run_id}", err=True, bold=True)

    async def go():
        await _finish(await resume_run(run_id, GraphContext(on_evidence=print_evidence), on_node=print_node))

    asyncio.run(go())


@app.command("history")
def history_cmd(run_id: str = typer.Argument(...)) -> None:
    """List a run's checkpoints, newest first (time travel)."""
    from etl_doctor.graph.build import history

    async def go():
        async for h in history(run_id):
            typer.echo(f"step {h['step']:>3}  next={','.join(h['next']) or '(done)':<18} evidence={h['evidence']:<3} "
                       f"investigations={h['investigations']} tokens={h['tokens']:<7} {h['checkpoint_id']}")

    asyncio.run(go())



@app.command()
def serve(
    host: str = typer.Option("127.0.0.1", help="Interface to bind; 0.0.0.0 to expose it (needs ETLDOC_UI_USERS)"),
    port: int = typer.Option(8000),
    data_dir: Path | None = typer.Option(None, help="Runs and cases (default: $ETLDOC_DATA_DIR or .etl_doctor/web)"),
    insecure: bool = typer.Option(False, help="Allow a non-local bind without login (e.g. behind an authenticating proxy)"),
) -> None:
    """Web UI: start runs, watch them live, approve or reject fixes, read reports."""
    import uvicorn

    from etl_doctor.web.app import Settings, create_app

    settings = Settings.from_env(**({"data_dir": data_dir} if data_dir else {}))
    if host not in ("127.0.0.1", "localhost", "::1") and not settings.users and not insecure:
        raise typer.BadParameter(
            "refusing to expose the UI without a login: every run spends API and sandbox credit, and "
            "approvals are recorded under a name. Set ETLDOC_UI_USERS=name:password[,...] or pass --insecure.",
            param_hint="--host")
    typer.secho(f"ETL Doctor UI on http://{host}:{port}  (data: {settings.data_dir}, "
                f"login: {'on' if settings.users else 'off'}, local sandbox: {'on' if settings.allow_local_sandbox else 'off'})",
                err=True, bold=True)
    uvicorn.run(create_app(settings), host=host, port=port, proxy_headers=True, timeout_graceful_shutdown=20)


if __name__ == "__main__":
    app()
