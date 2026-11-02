"""Apply a proposed fix to a COPY of the workspace and check it. Harness-only.

This is not a model tool: the model can only propose edits (as data). The harness runs
this after a human approved them. It executes model-written code (the patched pipeline),
which is why it runs inside the sandbox.

Idempotent: the work directory is keyed by a hash of the edits and the workspace, and a
finished result is cached there. Running it twice (a retried node, a resumed run) applies the patch once and
returns the same answer.
"""

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from fnmatch import fnmatch
from pathlib import Path

import duckdb

from edtools.commands import UserError

# Policy: what a fix may change. Pipeline code and config only; never data, tests or logs
# (a "fix" that edits the test or deletes the bad file would make the checks pass).
EDITABLE = ["demo_pipeline/pipeline/*.py", "demo_pipeline/pipeline/config.yaml"]


def fix_id(edits: list[dict], workspace: Path) -> str:
    """Same edits on the same workspace -> same ID. Both parts matter: identical edits on a
    different bundle must not reuse a cached result."""
    h = hashlib.sha256(json.dumps(edits, sort_keys=True).encode())
    for f in sorted(workspace.rglob("*")):
        if f.is_file() and f.parts[len(workspace.parts)] in ("demo_pipeline", "data") and "__pycache__" not in f.parts:
            h.update(f.relative_to(workspace).as_posix().encode())
            h.update(hashlib.sha256(f.read_bytes()).digest())
    return h.hexdigest()[:16]


def check_edit_policy(edits: list[dict]) -> None:
    for e in edits:
        p = e["path"]
        if ".." in Path(p).parts or Path(p).is_absolute() or not any(fnmatch(p, g) for g in EDITABLE):
            raise UserError(f"edit to {p!r} is not allowed; editable: {EDITABLE}")


def apply_edits(root: Path, edits: list[dict]) -> None:
    for e in edits:
        f = root / e["path"]
        text = f.read_text()
        if text.count(e["old_text"]) != 1:
            raise UserError(f"old_text must occur exactly once in {e['path']}; found {text.count(e['old_text'])}")
        f.write_text(text.replace(e["old_text"], e["new_text"]))


def _run(cmd: list[str], cwd: Path, env: dict | None = None, timeout: int = 60) -> tuple[int, str]:
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout,
                       env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1", **(env or {})})
    return p.returncode, (p.stdout + p.stderr)[-1500:]


def _csv_rows(d: Path) -> dict[str, int]:
    return {f.name: sum(1 for _ in f.open()) - 1 for f in sorted(d.glob("*.csv"))}


def validate_fix(edits: list[dict]) -> dict:
    check_edit_policy(edits)
    fid = fix_id(edits, Path.cwd())
    work = Path(tempfile.gettempdir()) / f"etl-fix-{fid}"
    cached = work / ".fix_result.json"
    if cached.exists():
        return {**json.loads(cached.read_text()), "cached": True}

    if work.exists():
        shutil.rmtree(work)  # a half-finished earlier attempt: start clean
    shutil.copytree(Path.cwd(), work, ignore=shutil.ignore_patterns("warehouse", "__pycache__", ".*"))
    apply_edits(work, edits)

    checks = []

    def check(name: str, ok: bool, detail: str) -> bool:
        checks.append({"name": name, "ok": bool(ok), "detail": detail[-600:]})  # tail: errors come last
        return ok

    run = [sys.executable, "-m", "demo_pipeline.pipeline.run"]
    for label, data in [("current", "data/current"), ("last_good", "data/last_good")]:
        db = f"warehouse/fix_{label}.duckdb"
        code, out = _run(run + ["--data", data, "--db", db], work)
        # Regression check included: the fix must still load the data that used to work.
        if not check(f"pipeline_runs_{label}", code == 0, f"exit {code}: {out}"):
            continue
        code, out = _run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "demo_pipeline/tests"],
                         work, env={"WAREHOUSE": db, "DATA_DIR": data})
        check(f"quality_tests_{label}", code == 0, out)

    ran = {c["name"]: c["ok"] for c in checks}
    if ran.get("pipeline_runs_current"):
        try:
            _data_checks(work, check)
        except duckdb.Error as e:
            check("warehouse_readable", False, f"{type(e).__name__}: {e}")

    result = {"fix_id": fid, "passed": all(c["ok"] for c in checks) and len(checks) >= 7, "checks": checks}
    cached.write_text(json.dumps(result))
    return result


def _data_checks(work: Path, check) -> None:
    """Checks on the loaded data, beyond "the tests pass"."""
    cur_db = work / "warehouse/fix_current.duckdb"
    with duckdb.connect(str(cur_db), read_only=True) as con:
        loaded = dict(con.execute("SELECT source_file, count(*) FROM orders GROUP BY 1").fetchall())
        expected = _csv_rows(work / "data/current")
        lost = {f: (n, loaded.get(f, 0)) for f, n in expected.items() if loaded.get(f, 0) != n}
        check("no_rows_lost", not lost, f"file: (in csv, loaded) {lost}" if lost else f"{sum(expected.values())} rows, all loaded")

        # Every order is dated on its file's day. Catches e.g. DD/MM parsed as MM/DD.
        wrong = con.execute(
            "SELECT source_file, count(*) FROM orders "
            "WHERE strftime(order_date, '%Y-%m-%d') != regexp_extract(source_file, '(\\d{4}-\\d{2}-\\d{2})', 1) "
            "GROUP BY 1 ORDER BY 1"
        ).fetchall()
        check("order_date_matches_partition", not wrong, f"mismatched rows per file: {wrong}" if wrong else "all rows match")

        # Amounts keep their scale (catches "12,50" -> 1250).
        med_cur = con.execute("SELECT median(amount) FROM orders").fetchone()[0]
    last_db = work / "warehouse/fix_last_good.duckdb"
    if last_db.exists():
        with duckdb.connect(str(last_db), read_only=True) as con:
            med_old = con.execute("SELECT median(amount) FROM orders").fetchone()[0]
        # Either side can be empty (NULL median) when the fix drops every row.
        ratio = med_cur / med_old if med_cur and med_old else 0.0
        check("amount_scale_unchanged", 0.5 <= ratio <= 2, f"median amount {med_cur} vs last good {med_old} (ratio {ratio:.2f})")


# Not exposed to the model: tools.py maps model tools to edtools.commands.COMMANDS only.
HARNESS_COMMANDS = {"validate_fix": validate_fix}
