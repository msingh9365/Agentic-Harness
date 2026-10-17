"""Entry point: python -m demo_pipeline.pipeline.run --data <dir> --db <file> [--log <file>]"""

import logging
import sys
from pathlib import Path

import typer
import yaml

from demo_pipeline.pipeline.extract import extract
from demo_pipeline.pipeline.load import load
from demo_pipeline.pipeline.transform import transform

CONFIG = Path(__file__).with_name("config.yaml")


def main(
    data: Path = typer.Option(..., help="Directory of orders_*.csv files"),
    db: Path = typer.Option(..., help="DuckDB warehouse file to write"),
    log_file: Path | None = typer.Option(None, "--log", help="Also append logs here"),
    config: Path = typer.Option(CONFIG, help="Pipeline config YAML"),
) -> None:
    handlers: list[logging.Handler] = [logging.StreamHandler(sys.stderr)]
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        handlers.append(logging.FileHandler(log_file))
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        handlers=handlers,
        force=True,
    )
    log = logging.getLogger("pipeline")

    cfg = yaml.safe_load(config.read_text())
    log.info("run started data=%s strict_parsing=%s", data, cfg["strict_parsing"])
    try:
        load(transform(extract(data, cfg["strict_parsing"]), cfg), db)
    except Exception:
        log.exception("run FAILED")
        raise typer.Exit(code=1)
    log.info("run SUCCEEDED")


if __name__ == "__main__":
    typer.run(main)
