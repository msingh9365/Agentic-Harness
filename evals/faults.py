"""Fault implementations. Each takes the all-string orders frame and returns a broken copy."""

from collections.abc import Callable

import polars as pl

from evals.models import Fault

FaultFn = Callable[[pl.DataFrame, Fault], pl.DataFrame]


def date_format_change(df: pl.DataFrame, fault: Fault) -> pl.DataFrame:
    col, fmt = fault.column, fault.params["to_format"]
    parsed = pl.col(col).str.strptime(pl.Date, "%Y-%m-%d")
    if fmt == "epoch_ms":
        new = (parsed.cast(pl.Datetime("ms")).cast(pl.Int64)).cast(pl.String)
    else:
        new = parsed.dt.strftime(fmt)
    return df.with_columns(new.alias(col))


def column_rename(df: pl.DataFrame, fault: Fault) -> pl.DataFrame:
    return df.rename({fault.column: fault.params["to"]})


def type_drift(df: pl.DataFrame, fault: Fault) -> pl.DataFrame:
    col, style = fault.column, fault.params["style"]
    if style == "comma_decimal":  # European locale: 12.50 -> 12,50
        new = pl.col(col).str.replace(".", ",", literal=True)
    elif style == "currency_symbol":  # 12.50 -> $12.50
        new = pl.lit("$") + pl.col(col)
    else:
        raise ValueError(f"unknown type_drift style: {style}")
    return df.with_columns(new.alias(col))


FAULTS: dict[str, FaultFn] = {
    "date_format_change": date_format_change,
    "column_rename": column_rename,
    "type_drift": type_drift,
}


def describe(fault: Fault) -> dict[str, str]:
    """Human-readable fields used to render a scenario's root_cause template."""
    p = fault.params
    if fault.type == "date_format_change":
        fmt = p["to_format"]
        human = "epoch milliseconds" if fmt == "epoch_ms" else (
            fmt.replace("%Y", "YYYY").replace("%m", "MM").replace("%d", "DD")
        )
        return {"to_format_human": human}
    if fault.type == "type_drift":
        return {
            "comma_decimal": {"style_human": "a comma decimal separator", "example": "12,50"},
            "currency_symbol": {"style_human": "a leading currency symbol", "example": "$12.50"},
        }[p["style"]]
    return {}
