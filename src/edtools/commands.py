"""One function per command. Paths are relative to the working directory (the bundle
root, mounted at /workspace in the sandbox). Every output is bounded in size."""

import difflib
import re
from pathlib import Path

import duckdb
import polars as pl

from edtools.formats import format_matches, top_shapes


class UserError(Exception):
    """Bad arguments from the caller (the model). Reported back as {"error": ...}."""


def safe_path(p: str, must_exist: bool = True) -> Path:
    # Defence in depth: the host validates paths too, but this is the code that touches
    # the filesystem, so it must not trust its caller.
    root = Path.cwd().resolve()
    full = (root / p).resolve()
    if not full.is_relative_to(root):
        raise UserError(f"path {p!r} is outside the workspace")
    if must_exist and not full.exists():
        raise UserError(f"path {p!r} does not exist")
    return full


def read_strings(path: Path) -> pl.DataFrame:
    # All strings: we want to see the raw values, not whatever the CSV reader guessed.
    return pl.read_csv(path, infer_schema=False)


def list_files(directory: str = ".") -> dict:
    d = safe_path(directory)
    if not d.is_dir():
        raise UserError(f"{directory!r} is not a directory")
    entries = []
    for p in sorted(d.iterdir())[:200]:
        if p.name.startswith(".") or p.name == "__pycache__":
            continue
        e = {"name": p.name + ("/" if p.is_dir() else ""), "bytes": p.stat().st_size if p.is_file() else None}
        if p.suffix == ".csv":
            with p.open() as fh:
                e["header"] = fh.readline().strip()
                e["rows"] = sum(1 for _ in fh)
        entries.append(e)
    return {"directory": directory, "entries": entries}


def profile_column(s: pl.Series) -> dict:
    values = s.drop_nulls().to_list()
    distinct = s.n_unique()
    return {
        "name": s.name,
        "nulls": s.null_count(),
        "distinct": distinct,
        "examples": s.drop_nulls().unique(maintain_order=True).head(5).to_list(),
        "shapes": top_shapes(values),
        "formats": format_matches(values) if distinct > 1 or values else [],
    }


def profile(path: str, columns: list[str] | None = None) -> dict:
    df = read_strings(safe_path(path))
    if columns:
        unknown = [c for c in columns if c not in df.columns]
        if unknown:
            raise UserError(f"unknown columns {unknown}; file has {df.columns}")
        df = df.select(columns)
    return {"path": path, "rows": df.height, "columns": [profile_column(df[c]) for c in df.columns]}


def dominant(col: dict) -> str | None:
    return col["shapes"][0]["shape"] if col["shapes"] else None


def column_by_file(column: str, directory: str = "data/current") -> dict:
    """One row per CSV file: is the column there, and what do its values look like?"""
    d = safe_path(directory)
    files = sorted(d.glob("*.csv"))
    if not files:
        raise UserError(f"no CSV files in {directory!r}")
    rows = []
    for f in files[:100]:
        df = read_strings(f)
        if column not in df.columns:
            rows.append({"file": f.name, "rows": df.height, "present": False, "columns": df.columns})
            continue
        col = profile_column(df[column])
        top = col["formats"][0] if col["formats"] else None
        rows.append({
            "file": f.name,
            "rows": df.height,
            "present": True,
            "nulls": col["nulls"],
            "shape": col["shapes"][0] if col["shapes"] else None,
            "best_format": top,
            "example": col["examples"][0] if col["examples"] else None,
        })
    return {"column": column, "directory": directory, "files": rows}


def diff_schema(current: str, last_good: str) -> dict:
    cur, old = profile(current), profile(last_good)
    cur_cols = {c["name"]: c for c in cur["columns"]}
    old_cols = {c["name"]: c for c in old["columns"]}
    added = [c for c in cur_cols if c not in old_cols]
    dropped = [c for c in old_cols if c not in cur_cols]

    # A rename looks like "one column dropped, one added, similar values".
    renames = []
    for d in dropped:
        for a in added:
            name_sim = difflib.SequenceMatcher(None, d.lower(), a.lower()).ratio()
            shape_sim = 1.0 if dominant(old_cols[d]) == dominant(cur_cols[a]) else 0.0
            score = round(0.5 * name_sim + 0.5 * shape_sim, 2)
            if score >= 0.5:
                renames.append({"from": d, "to": a, "score": score})

    changes = []
    for name in cur_cols.keys() & old_cols.keys():
        before, after = dominant(old_cols[name]), dominant(cur_cols[name])
        if before != after:
            changes.append({
                "column": name,
                "before": {"shape": before, "formats": old_cols[name]["formats"][:2]},
                "after": {"shape": after, "formats": cur_cols[name]["formats"][:2]},
            })
    return {
        "current": current,
        "last_good": last_good,
        "added": added,
        "dropped": dropped,
        "rename_candidates": sorted(renames, key=lambda r: -r["score"]),
        "format_changes": sorted(changes, key=lambda c: c["column"]),
    }


def grep_logs(pattern: str, path: str = "logs", max_matches: int = 30) -> dict:
    try:
        rx = re.compile(pattern, re.IGNORECASE)
    except re.error as e:
        raise UserError(f"bad regex: {e}") from e
    root = safe_path(path)
    files = sorted(root.rglob("*.log")) if root.is_dir() else [root]
    matches, total = [], 0
    for f in files:
        for i, line in enumerate(f.read_text(errors="replace").splitlines(), 1):
            if rx.search(line):
                total += 1
                if len(matches) < max_matches:
                    rel = str(f.relative_to(Path.cwd().resolve()))
                    matches.append({"file": rel, "line": i, "text": line[:300]})
    return {"pattern": pattern, "total_matches": total, "matches": matches}


SQL_START = re.compile(r"^\s*(select|with|describe|summarize|show)\b", re.IGNORECASE)


def run_sql(query: str, max_rows: int = 50) -> dict:
    if not SQL_START.match(query) or ";" in query.strip().rstrip(";"):
        raise UserError("only a single SELECT / WITH / DESCRIBE / SUMMARIZE / SHOW statement is allowed")
    con = duckdb.connect()
    # Load the data first, then lock the connection down: no file or network access and
    # no way to undo that setting. Queries can only see the tables created here.
    tables = []
    for name, glob in [("current_orders", "data/current"), ("last_good_orders", "data/last_good")]:
        if any(safe_path(glob).glob("*.csv")):
            con.execute(
                f"CREATE TABLE {name} AS SELECT * FROM read_csv('{glob}/*.csv', all_varchar=true, "
                "union_by_name=true, filename='source_path')"
            )
            con.execute(f"UPDATE {name} SET source_path = regexp_extract(source_path, '[^/]+$')")
            con.execute(f"ALTER TABLE {name} RENAME source_path TO source_file")
            tables.append(name)
    for name, db in [("warehouse_current", "warehouse/current.duckdb"), ("warehouse_last_good", "warehouse/last_good.duckdb")]:
        if (Path.cwd() / db).exists():
            con.execute(f"ATTACH '{db}' AS {name}_db (READ_ONLY)")
            con.execute(f"CREATE TABLE {name} AS SELECT * FROM {name}_db.orders")
            con.execute(f"DETACH {name}_db")
            tables.append(name)
    con.execute("SET enable_external_access = false")
    con.execute("SET lock_configuration = true")
    try:
        rel = con.sql(query)
        rows = rel.fetchmany(max_rows + 1)
    except duckdb.Error as e:
        raise UserError(f"{type(e).__name__}: {str(e)[:500]}; tables: {tables}") from e
    return {
        "columns": rel.columns,
        "rows": [[str(v) for v in r] for r in rows[:max_rows]],
        "truncated": len(rows) > max_rows,
        "tables": tables,
    }


TEXT_SUFFIXES = {".py", ".yaml", ".yml", ".md", ".log", ".csv", ".txt", ".toml", ".json", ".sql"}


def read_file(path: str, start_line: int = 1, max_lines: int = 120) -> dict:
    f = safe_path(path)
    if not f.is_file() or f.suffix not in TEXT_SUFFIXES:
        raise UserError(f"{path!r} is not a readable text file ({sorted(TEXT_SUFFIXES)})")
    lines = f.read_text(errors="replace").splitlines()
    start = max(start_line, 1)
    chunk = lines[start - 1 : start - 1 + min(max_lines, 300)]
    return {
        "path": path,
        "total_lines": len(lines),
        "text": "\n".join(f"{i:4}| {line[:300]}" for i, line in enumerate(chunk, start)),
    }


COMMANDS = {
    "read_file": read_file,
    "list_files": list_files,
    "profile": profile,
    "column_by_file": column_by_file,
    "diff_schema": diff_schema,
    "grep_logs": grep_logs,
    "run_sql": run_sql,
}
