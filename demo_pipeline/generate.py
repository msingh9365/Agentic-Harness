"""Generate the clean, deterministic "orders" source data the demo pipeline ingests.

One CSV per day, as an upstream system would drop them. Everything is a string on
disk; typing happens in the pipeline's transform step, which is where format drift bites.
"""

import random
from datetime import date, timedelta
from pathlib import Path

import polars as pl
import typer

START = date(2026, 10, 8)
DAYS = 9  # 2026-10-08 .. 2026-10-16
ROWS_PER_DAY = 200
STATUSES = ["completed"] * 8 + ["refunded", "cancelled"]


def generate(out_dir: Path, seed: int = 42) -> list[Path]:
    rng = random.Random(seed)
    out_dir.mkdir(parents=True, exist_ok=True)
    paths, order_id = [], 100_000
    for d in range(DAYS):
        day = START + timedelta(days=d)
        rows = []
        for _ in range(ROWS_PER_DAY):
            order_id += 1
            rows.append(
                {
                    "order_id": str(order_id),
                    "customer_id": str(rng.randint(1, 5_000)),
                    "order_date": day.isoformat(),
                    "amount": f"{rng.uniform(5, 250):.2f}",
                    "currency": "USD",
                    "status": rng.choice(STATUSES),
                }
            )
        path = out_dir / f"orders_{day.isoformat()}.csv"
        pl.DataFrame(rows).write_csv(path)
        paths.append(path)
    return paths


def main(out_dir: Path = Path("demo_pipeline/data/clean"), seed: int = 42) -> None:
    paths = generate(out_dir, seed)
    typer.echo(f"wrote {len(paths)} files to {out_dir}")


if __name__ == "__main__":
    typer.run(main)
