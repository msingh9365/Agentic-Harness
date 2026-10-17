"""etl-doctor diagnose <bundle>"""

import asyncio
from pathlib import Path

import typer

from etl_doctor.diagnose import diagnose as run_diagnose
from etl_doctor.llm import STRONG_MODEL

app = typer.Typer(no_args_is_help=True, add_completion=False)


@app.callback()
def _main() -> None:
    """ETL Doctor: diagnose broken ETL pipelines."""


@app.command()
def diagnose(
    bundle: Path = typer.Argument(..., exists=True, file_okay=False, help="Bundle directory"),
    model: str = typer.Option(STRONG_MODEL, help="Model id on the NVIDIA API"),
    show_prompt: bool = typer.Option(False, help="Print the exact context sent to the model, then exit"),
) -> None:
    """Read a bundle's logs, code and data samples; print a validated Diagnosis as JSON."""
    if show_prompt:
        from etl_doctor.context import build_context
        from etl_doctor.diagnose import PROMPT

        typer.echo(f"=== system instructions ===\n{PROMPT}\n=== user prompt ===\n{build_context(bundle).render()}")
        raise typer.Exit()
    r = asyncio.run(run_diagnose(bundle, model))
    typer.echo(r.diagnosis.model_dump_json(indent=2))
    u = r.usage
    typer.echo(
        f"\nmodel={r.model} requests={u.requests} retries={r.retries} "
        f"input_tokens={u.input_tokens} output_tokens={u.output_tokens} prompt_chars={r.prompt_chars}",
        err=True,
    )


if __name__ == "__main__":
    app()
