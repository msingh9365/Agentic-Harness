import logging

import polars as pl

log = logging.getLogger("pipeline.transform")


def transform(df: pl.DataFrame, cfg: dict) -> pl.DataFrame:
    """Validate the columns, cast to typed columns, and drop rows that failed to parse."""
    missing = [c for c in cfg["required_columns"] if c not in df.columns]
    if missing:
        raise KeyError(f"missing required columns: {missing}; got {df.columns}")

    strict = cfg["strict_parsing"]
    typed = df.select(
        pl.col("order_id").cast(pl.Int64, strict=strict),
        pl.col("customer_id").cast(pl.Int64, strict=strict),
        pl.col("order_date").str.strptime(pl.Date, cfg["date_format"], strict=strict),
        pl.col("amount").cast(pl.Float64, strict=strict),
        pl.col("currency"),
        pl.col("status"),
        pl.col("source_file"),
    )

    # Only reachable when strict_parsing is false: unparseable values became nulls.
    valid = typed.drop_nulls(["order_id", "order_date", "amount"])
    dropped = typed.height - valid.height
    if dropped:
        log.debug("dropped %d rows with unparseable values", dropped)
    log.info("transformed %d rows", valid.height)
    return valid
