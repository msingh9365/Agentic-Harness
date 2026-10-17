import logging
from pathlib import Path

import duckdb
import polars as pl

log = logging.getLogger("pipeline.load")


def load(df: pl.DataFrame, db_path: Path) -> None:
    """Replace the orders table and rebuild the daily_revenue mart."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with duckdb.connect(str(db_path)) as con:
        con.register("staged", df.to_arrow())
        con.execute("CREATE OR REPLACE TABLE orders AS SELECT * FROM staged")
        con.execute(
            """
            CREATE OR REPLACE TABLE daily_revenue AS
            SELECT order_date, count(*) AS orders, round(sum(amount), 2) AS revenue
            FROM orders
            WHERE status = 'completed'
            GROUP BY order_date
            ORDER BY order_date
            """
        )
        n = con.execute("SELECT count(*) FROM orders").fetchone()[0]
    log.info("loaded %d rows into %s", n, db_path)
