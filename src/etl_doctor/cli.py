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


if __name__ == "__main__":
    app()
