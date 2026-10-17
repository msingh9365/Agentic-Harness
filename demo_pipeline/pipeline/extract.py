import logging
from pathlib import Path

import polars as pl

log = logging.getLogger("pipeline.extract")


def extract(input_dir: Path, strict: bool = True) -> pl.DataFrame:
    """Read every orders_*.csv as all-string columns, tagging rows with their source file.

    strict: every file must have the same header as the first one. Otherwise files are
    unioned by column name and columns missing from a file are filled with nulls.
    """
    files = sorted(input_dir.glob("orders_*.csv"))
    if not files:
        raise FileNotFoundError(f"no orders_*.csv files in {input_dir}")
    frames = []
    for f in files:
        df = pl.read_csv(f, infer_schema=False).with_columns(source_file=pl.lit(f.name))
        log.info("extracted %d rows from %s", df.height, f.name)
        if strict and frames and df.columns != frames[0].columns:
            raise ValueError(
                f"header mismatch in {f.name}: {df.columns[:-1]} != {frames[0].columns[:-1]}"
            )
        frames.append(df)
    return pl.concat(frames, how="diagonal")
