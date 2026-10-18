"""etl-doctor diagnose <bundle> [--no-tools]"""

import asyncio
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


NODE_LABEL = {
    "intake": "read bundle manifest",
    "provision_sandbox": "sandbox ready",
    "triage": "triage",
    "investigate": "investigation round",
    "hypothesize": "hypotheses",
    "verify": "verification",
    "escalate": "ESCALATE to a human",
    "report": "report",
    "teardown": "sandbox destroyed",
}


def print_node(name: str, update: dict) -> None:
    detail = ""
    if name == "provision_sandbox" and update.get("sandbox_id"):
        detail = update["sandbox_id"]
    elif name == "triage" and update.get("triage"):
        t = update["triage"]
        detail = f"{t.run_outcome}; candidates {[c.value for c in t.candidate_classes]}; suspects {t.suspect_columns}"
    elif name == "hypothesize" and update.get("hypotheses"):
        detail = "; ".join(f"{h.id} {h.failure_class.value} conf={h.confidence:.2f} {h.statement[:70]}" for h in update["hypotheses"].hypotheses)
    elif name == "verify" and update.get("verification"):
        v = update["verification"]
        detail = f"{v.hypothesis_id} {v.outcome.upper()}: {v.observations[:100]}"
    elif name == "escalate":
        detail = update.get("terminal_reason", "")
    typer.secho(f"[{name}] {NODE_LABEL.get(name, name)} {detail}", err=True, fg="green" if name != "escalate" else "red")


def print_report(s) -> None:
    r = s.report
    if r is None:
        return
    typer.echo(r.model_dump_json(indent=2, exclude={"usage"}))
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
    """Step 4: the full graph (triage -> investigate <-> hypothesize -> verify -> report), checkpointed."""
    from etl_doctor.graph.build import new_run_id, start_run
    from etl_doctor.graph.nodes import GraphContext

    run_id = run_id or new_run_id()
    typer.secho(f"run {run_id} (checkpoints: .etl_doctor/checkpoints.sqlite)", err=True, bold=True)
    ctx = GraphContext(on_evidence=print_evidence, crash_before=crash_before)
    print_report(asyncio.run(start_run(bundle, sandbox, ctx, run_id=run_id, on_node=print_node)))


@app.command()
def resume(run_id: str = typer.Argument(...)) -> None:
    """Continue a run from its last checkpoint (after a crash, Ctrl-C or error)."""
    from etl_doctor.graph.build import resume_run
    from etl_doctor.graph.nodes import GraphContext

    typer.secho(f"resuming {run_id}", err=True, bold=True)
    print_report(asyncio.run(resume_run(run_id, GraphContext(on_evidence=print_evidence), on_node=print_node)))


@app.command("history")
def history_cmd(run_id: str = typer.Argument(...)) -> None:
    """List a run's checkpoints, newest first (time travel)."""
    from etl_doctor.graph.build import history

    async def go():
        async for h in history(run_id):
            typer.echo(f"step {h['step']:>3}  next={','.join(h['next']) or '(done)':<18} evidence={h['evidence']:<3} "
                       f"investigations={h['investigations']} tokens={h['tokens']:<7} {h['checkpoint_id']}")

    asyncio.run(go())


if __name__ == "__main__":
    app()
