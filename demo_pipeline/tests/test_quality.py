"""Data-quality checks on the warehouse, run after the pipeline (dbt-test style).

    WAREHOUSE=out/x.duckdb DATA_DIR=<input dir> pytest demo_pipeline/tests
"""

import os
from pathlib import Path

import duckdb
import pytest


@pytest.fixture(scope="module")
def con():
    with duckdb.connect(os.environ["WAREHOUSE"], read_only=True) as c:
        yield c


def scalar(con, sql):
    return con.execute(sql).fetchone()[0]


def test_orders_not_empty(con):
    assert scalar(con, "SELECT count(*) FROM orders") > 0


def test_every_source_file_loaded(con):
    expected = {p.name for p in Path(os.environ["DATA_DIR"]).glob("orders_*.csv")}
    loaded = {r[0] for r in con.execute("SELECT DISTINCT source_file FROM orders").fetchall()}
    assert loaded == expected, f"files with no loaded rows: {sorted(expected - loaded)}"


def test_no_null_keys(con):
    assert scalar(con, "SELECT count(*) FROM orders WHERE order_id IS NULL OR customer_id IS NULL") == 0


def test_amount_positive(con):
    assert scalar(con, "SELECT count(*) FROM orders WHERE amount <= 0") == 0


def test_daily_orders_not_anomalous(con):
    rows = con.execute(
        """
        SELECT order_date, orders FROM daily_revenue
        WHERE orders < 0.5 * (SELECT median(orders) FROM daily_revenue)
        """
    ).fetchall()
    assert not rows, f"days with abnormally few orders: {rows}"
