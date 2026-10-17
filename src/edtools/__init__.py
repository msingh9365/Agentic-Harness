"""Read-only investigation commands. Runs where the data is (locally now, in the sandbox
from Step 3), takes JSON args, prints JSON. Depends only on polars + duckdb, never on
etl_doctor, so it can be copied into a sandbox image on its own."""
