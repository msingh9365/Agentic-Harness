"""ETL Doctor web UI: start runs, watch them live, answer approvals, read reports.

    etl-doctor serve                      # http://127.0.0.1:8000

The server is one more client of the checkpointed graph (`graph/build.py`), next to the CLI:
- A run executes as a background task in this process. It is not tied to an HTTP request
  or a browser tab: close the tab and the run carries on, or stops at the approval gate.
- Every run has its own directory: `meta.json`, `events.jsonl` (the live log, replayed to
  late or reconnecting viewers) and `checkpoints.sqlite` (the graph state). One SQLite file
  per run means concurrent runs never contend for one database.
- Status comes from the checkpoint, not from memory, so it survives a restart. A run that
  was mid-flight when the process died shows as `stopped` and can be resumed; with
  `resume_on_start` the server resumes such runs itself at startup.

Security (see docs/07-ui-and-hosting.md):
- Everything shown comes from a broken system or a model, so it is untrusted: the page
  renders text only (no innerHTML) and the CSP forbids inline script.
- Optional HTTP Basic auth; the approver recorded in the audit trail is the logged-in user.
- POSTs need a custom header, which a cross-site form cannot send (CSRF).
- Limits on concurrent runs and runs per day, because each run spends real API and
  sandbox credit. The local (unsandboxed) executor is off unless explicitly allowed.
"""

import asyncio
import base64
import json
import os
import re
import secrets
import time
from collections.abc import Callable
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse, PlainTextResponse, Response, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ValidationError

from etl_doctor.evidence import Evidence
from etl_doctor.graph import build as gb
from etl_doctor.graph.nodes import GraphContext
from etl_doctor.graph.state import ApprovalDecision, RunState
from etl_doctor.progress import NODE_LABEL, node_detail

STATIC = Path(__file__).parent / "static"
RUN_ID = re.compile(r"^run-[0-9]{8}-[0-9]{6}-[0-9a-f]{4}$")
CSRF_HEADER = "x-etldoc"
TERMINAL = {"fixed", "diagnosed_unfixed", "escalated"}


@dataclass
class Settings:
    data_dir: Path = Path(".etl_doctor/web")
    users: dict[str, str] = field(default_factory=dict)  # name -> password; empty = no auth
    allow_local_sandbox: bool = False  # the local executor runs pipeline and fix code on THIS host
    max_active_runs: int = 2
    max_runs_per_day: int = 50
    resume_on_start: bool = False
    # Builds the per-operation runtime context. Tests pass one with a scripted model.
    make_context: Callable[[Callable[[Evidence], None]], GraphContext] = field(
        default=lambda on_evidence: GraphContext(on_evidence=on_evidence))

    @classmethod
    def from_env(cls, **overrides) -> "Settings":
        env = os.environ
        users = dict(u.split(":", 1) for u in env.get("ETLDOC_UI_USERS", "").split(",") if ":" in u)
        s = cls(
            data_dir=Path(env.get("ETLDOC_DATA_DIR", ".etl_doctor/web")),
            users=users,
            allow_local_sandbox=env.get("ETLDOC_ALLOW_LOCAL_SANDBOX") == "1",
            max_active_runs=int(env.get("ETLDOC_MAX_ACTIVE_RUNS", 2)),
            max_runs_per_day=int(env.get("ETLDOC_MAX_RUNS_PER_DAY", 50)),
            resume_on_start=env.get("ETLDOC_RESUME_ON_START") == "1",
        )
        for k, v in overrides.items():
            setattr(s, k, v)
        return s


# --- the case catalog: the scenarios the fault injector can build --------------------------

def catalog() -> dict[str, dict]:
    from evals.inject import case_name, load_scenario
    from evals.suite import all_cases

    out = {}
    for scenario, mode, variant in all_cases():
        sc = load_scenario(scenario)
        name = case_name(sc, mode, variant)  # type: ignore[arg-type]
        out[name] = {"case": name, "scenario": scenario, "failure_class": sc.failure_class,
                     "description": sc.description, "mode": mode, "variant": variant}
    return out


class StartRun(BaseModel):
    case: str
    sandbox: str = "e2b"
    approver: str | None = None  # who started it (no-auth mode); the logged-in user otherwise


class Decision(BaseModel):
    decision: str
    feedback: str | None = None
    approver: str | None = None


@dataclass
class Live:
    """In-process state of one run: its task (if running) and a wake-up for event streams."""

    task: asyncio.Task | None = None
    changed: asyncio.Event = field(default_factory=asyncio.Event)
    seq: int = -1  # number of the last event written to events.jsonl


class Runs:
    def __init__(self, settings: Settings):
        self.s = settings
        self.root = settings.data_dir / "runs"
        self.cases = settings.data_dir / "cases"
        self.root.mkdir(parents=True, exist_ok=True)
        self.cases.mkdir(parents=True, exist_ok=True)
        self.live: dict[str, Live] = {}
        self.case_locks: dict[str, asyncio.Lock] = {}
        self.catalog = catalog()

    # --- storage ---------------------------------------------------------------------------
    def dir(self, run_id: str) -> Path:
        if not RUN_ID.match(run_id):  # also stops path traversal
            raise HTTPException(404, "no such run")
        d = self.root / run_id
        if not (d / "meta.json").exists():
            raise HTTPException(404, "no such run")
        return d

    def db(self, run_id: str) -> Path:
        return self.root / run_id / "checkpoints.sqlite"

    def meta(self, run_id: str) -> dict:
        return json.loads((self.dir(run_id) / "meta.json").read_text())

    def _live(self, run_id: str) -> Live:
        if run_id not in self.live:
            f = self.root / run_id / "events.jsonl"
            self.live[run_id] = Live(seq=(sum(1 for _ in f.open()) - 1) if f.exists() else -1)
        return self.live[run_id]

    def emit(self, run_id: str, event: dict) -> None:
        lv = self._live(run_id)
        lv.seq += 1
        line = {"seq": lv.seq, "t": round(time.time(), 3), **event}
        with (self.root / run_id / "events.jsonl").open("a") as fh:
            fh.write(json.dumps(line, default=str) + "\n")
        old, lv.changed = lv.changed, asyncio.Event()
        old.set()  # wake every stream waiting on this run

    def events(self, run_id: str, after: int) -> list[dict]:
        f = self.root / run_id / "events.jsonl"
        if not f.exists():
            return []
        return [e for line in f.read_text().splitlines() if (e := json.loads(line))["seq"] > after]

    # --- state, from the checkpoint ---------------------------------------------------------
    async def snapshot(self, run_id: str) -> tuple[RunState | None, list[str], dict | None]:
        db = self.db(run_id)
        if not db.exists():
            return None, [], None
        async with gb.open_graph(db) as app:
            snap = await app.aget_state(gb._config(run_id))
        if not snap.values:
            return None, [], None
        req = snap.interrupts[0].value if snap.interrupts else None
        return RunState.model_validate(snap.values), list(snap.next), req

    def running(self, run_id: str) -> bool:
        lv = self.live.get(run_id)
        return bool(lv and lv.task and not lv.task.done())

    async def status(self, run_id: str) -> str:
        if self.running(run_id):
            return "running"
        state, nxt, req = await self.snapshot(run_id)
        if req is not None:
            return "awaiting_approval"
        if state is not None and state.report is not None:
            return state.report.status
        return "stopped"  # never started, or died mid-run: resumable

    def active_count(self) -> int:
        return sum(self.running(r) for r in self.live)

    # --- operations -------------------------------------------------------------------------
    async def ensure_case(self, case: str) -> Path:
        """Build the broken bundle once (the injector runs the pipeline, a few seconds)."""
        from evals.inject import build, load_scenario

        info = self.catalog[case]
        async with self.case_locks.setdefault(case, asyncio.Lock()):
            d = self.cases / case
            if not (d / "ground_truth.json").exists():
                await asyncio.to_thread(build, load_scenario(info["scenario"]), info["mode"], info["variant"], self.cases)
        return d

    def launch(self, run_id: str, what: str, op: Callable[[GraphContext, Callable], Any]) -> None:
        """Run a graph operation in the background; record its progress as events."""
        if self.running(run_id):
            raise HTTPException(409, "this run is already running")
        if self.active_count() >= self.s.max_active_runs:
            raise HTTPException(429, f"{self.s.max_active_runs} runs are already active; try again when one finishes")

        def on_node(name: str, update: Any) -> None:
            upd = update if isinstance(update, dict) else {}
            label = "waiting for a human decision (run is checkpointed)" if name == "__interrupt__" else NODE_LABEL.get(name, name)
            self.emit(run_id, {"type": "node", "node": name, "label": label, "detail": node_detail(name, upd)})

        def on_evidence(ev: Evidence) -> None:
            self.emit(run_id, {"type": "evidence", "id": ev.id, "tool": ev.tool, "summary": ev.summary})

        async def go():
            self.emit(run_id, {"type": "status", "status": "running", "detail": what})
            ctx = self.s.make_context(on_evidence)
            try:
                await op(ctx, on_node)
            except asyncio.CancelledError:
                await asyncio.shield(self._release(run_id))
                self.emit(run_id, {"type": "error", "message": "server shutting down; the run is checkpointed and can be resumed"})
                raise
            except Exception as e:  # recorded for the viewer; the run stays resumable
                await self._release(run_id)
                self.emit(run_id, {"type": "error", "message": f"{type(e).__name__}: {str(e)[:400]}"})
            finally:
                lv = self._live(run_id)
                lv.task = None
                self.emit(run_id, {"type": "status", "status": await self.status(run_id)})

        self._live(run_id).task = asyncio.create_task(go(), name=f"etl-doctor {run_id}")

    async def _release(self, run_id: str) -> None:
        try:  # don't leave a VM billing until its timeout
            await gb.release(run_id, db_path=self.db(run_id))
        except Exception:
            pass

    def runs_today(self) -> int:
        today = datetime.now(timezone.utc).strftime("%Y%m%d")
        return sum(1 for d in self.root.iterdir() if d.name.startswith(f"run-{today}"))

    async def recover(self) -> list[str]:
        """At startup: resume runs that were mid-flight when the process stopped."""
        resumed = []
        for d in sorted(self.root.iterdir()):
            if not (d / "meta.json").exists() or self.active_count() >= self.s.max_active_runs:
                continue
            state, nxt, req = await self.snapshot(d.name)
            if state is not None and nxt and req is None and state.report is None:
                self.launch(d.name, "resumed after restart",
                            lambda ctx, on_node, r=d.name: gb.resume_run(r, ctx, on_node=on_node, db_path=self.db(r)))
                resumed.append(d.name)
        return resumed

    async def shutdown(self) -> None:
        tasks = [lv.task for lv in self.live.values() if lv.task and not lv.task.done()]
        for t in tasks:
            t.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)


SECURITY_HEADERS = [(k.encode(), v.encode()) for k, v in {
    "content-security-policy": "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; "
                               "connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'none'",
    "x-content-type-options": "nosniff",
    "referrer-policy": "no-referrer",
}.items()]


class Guard:
    """ASGI middleware: Basic auth (if users are configured), CSRF header on POST, security
    headers. Plain ASGI rather than @app.middleware, which buffers and breaks event streams."""

    def __init__(self, app, users: dict[str, str]):
        self.app, self.users = app, users

    def _user(self, headers: dict[str, str]) -> str | None:
        auth = headers.get("authorization", "")
        if not auth.lower().startswith("basic "):
            return None
        try:
            name, _, pw = base64.b64decode(auth[6:]).decode().partition(":")
        except ValueError:
            return None
        want = self.users.get(name)
        return name if want is not None and secrets.compare_digest(pw.encode(), want.encode()) else None

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
        headers = {k.decode().lower(): v.decode() for k, v in scope["headers"]}
        if self.users and scope["path"] != "/healthz":
            user = self._user(headers)
            if user is None:
                return await Response("login required", 401, {"WWW-Authenticate": 'Basic realm="etl-doctor"'})(scope, receive, send)
            scope.setdefault("state", {})["user"] = user
        if scope["method"] == "POST" and headers.get(CSRF_HEADER) != "1":
            return await JSONResponse({"detail": f"missing {CSRF_HEADER} header"}, 403)(scope, receive, send)

        async def send_with_headers(msg):
            if msg["type"] == "http.response.start":
                msg["headers"] = list(msg.get("headers", [])) + SECURITY_HEADERS
            await send(msg)

        await self.app(scope, receive, send_with_headers)


def _public_state(state: RunState) -> dict:
    # Tool results can be large; the page shows each evidence item's one-line summary.
    return state.model_dump(mode="json", exclude={"evidence": {"__all__": {"data"}}, "manifest": True})


def create_app(settings: Settings | None = None) -> FastAPI:
    s = settings or Settings.from_env()
    runs = Runs(s)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        if s.resume_on_start:
            await runs.recover()
        yield
        await runs.shutdown()

    app = FastAPI(title="ETL Doctor", lifespan=lifespan, docs_url=None, redoc_url=None, openapi_url=None)
    app.state.runs = runs
    app.add_middleware(Guard, users=s.users)

    def user_of(request: Request) -> str | None:
        return getattr(request.state, "user", None)

    def who(request: Request, claimed: str | None) -> str:
        user = user_of(request)
        if user:
            return user  # authenticated: the claim in the body is ignored
        name = (claimed or "").strip()
        if not name:
            raise HTTPException(422, "enter your name: it is recorded in the audit trail")
        return name[:60]

    @app.api_route("/healthz", methods=["GET", "HEAD"])
    async def healthz():
        return {"ok": True}

    @app.api_route("/", methods=["GET", "HEAD"])
    async def index():
        return FileResponse(STATIC / "index.html")

    @app.get("/api/config")
    async def config(request: Request):
        return {"user": user_of(request), "auth": bool(s.users), "allow_local_sandbox": s.allow_local_sandbox,
                "max_active_runs": s.max_active_runs, "max_runs_per_day": s.max_runs_per_day,
                "runs_today": runs.runs_today(), "active_runs": runs.active_count()}

    @app.get("/api/cases")
    async def cases():
        return list(runs.catalog.values())

    @app.get("/api/runs")
    async def list_runs():
        out = []
        for d in sorted(runs.root.iterdir(), reverse=True):
            if (d / "meta.json").exists():
                out.append({**json.loads((d / "meta.json").read_text()), "status": await runs.status(d.name)})
        return out

    @app.post("/api/runs", status_code=201)
    async def start(body: StartRun, request: Request):
        if body.case not in runs.catalog:
            raise HTTPException(422, "unknown case")
        if body.sandbox not in ("e2b", "local") or (body.sandbox == "local" and not s.allow_local_sandbox):
            raise HTTPException(422, "sandbox must be e2b" + (" or local" if s.allow_local_sandbox else ""))
        if runs.runs_today() >= s.max_runs_per_day:
            raise HTTPException(429, f"daily limit of {s.max_runs_per_day} runs reached")
        if runs.active_count() >= s.max_active_runs:
            raise HTTPException(429, f"{s.max_active_runs} runs are already active; try again when one finishes")
        started_by = who(request, body.approver)
        case_dir = await runs.ensure_case(body.case)
        run_id = gb.new_run_id()
        d = runs.root / run_id
        d.mkdir()
        info = runs.catalog[body.case]
        (d / "meta.json").write_text(json.dumps({
            "run_id": run_id, **info, "sandbox": body.sandbox, "started_by": started_by,
            "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds")}))
        runs.launch(run_id, f"started by {started_by}", lambda ctx, on_node: gb.start_run(
            case_dir / "bundle", body.sandbox, ctx, run_id=run_id, on_node=on_node, db_path=runs.db(run_id)))
        return {"run_id": run_id}

    @app.get("/api/runs/{run_id}")
    async def get_run(run_id: str):
        meta = runs.meta(run_id)
        state, nxt, req = await runs.snapshot(run_id)
        status = await runs.status(run_id)
        out: dict[str, Any] = {"meta": meta, "status": status, "next": nxt, "approval": req,
                               "state": _public_state(state) if state else None}
        if state is not None and state.report is not None:
            out["answer_key"] = answer_key(runs.cases / meta["case"], state)
        return out

    @app.get("/api/runs/{run_id}/events")
    async def events(run_id: str, request: Request, after: int = -1):
        runs.dir(run_id)
        last = request.headers.get("last-event-id")
        if last and last.lstrip("-").isdigit():
            after = int(last)

        async def stream():
            nonlocal after
            yield "retry: 3000\n\n"
            while not await request.is_disconnected():
                wake = runs._live(run_id).changed  # take it BEFORE reading, or a write in between is missed
                for e in runs.events(run_id, after):
                    after = e["seq"]
                    yield f"id: {e['seq']}\ndata: {json.dumps(e, default=str)}\n\n"
                try:
                    await asyncio.wait_for(wake.wait(), timeout=15)
                except TimeoutError:
                    yield ": keep-alive\n\n"  # proxies close idle connections

        return StreamingResponse(stream(), media_type="text/event-stream",
                                 headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})

    @app.post("/api/runs/{run_id}/decision")
    async def decision(run_id: str, body: Decision, request: Request):
        runs.dir(run_id)
        if runs.running(run_id) or await runs.status(run_id) != "awaiting_approval":
            raise HTTPException(409, "this run is not waiting for a decision")  # double click, second reviewer
        try:
            d = ApprovalDecision(decision=body.decision, feedback=(body.feedback or "").strip() or None,
                                 approver=who(request, body.approver), decided_at=datetime.now(timezone.utc))
        except ValidationError as e:
            raise HTTPException(422, e.errors()[0]["msg"])
        runs.emit(run_id, {"type": "decision", "decision": d.decision, "approver": d.approver, "feedback": d.feedback})
        runs.launch(run_id, f"{d.decision} by {d.approver}",
                    lambda ctx, on_node: gb.decide(run_id, d, ctx, on_node=on_node, db_path=runs.db(run_id)))
        return {"ok": True}

    @app.post("/api/runs/{run_id}/resume")
    async def resume(run_id: str):
        runs.dir(run_id)
        if await runs.status(run_id) != "stopped":
            raise HTTPException(409, "only a stopped run can be resumed")
        state, _, _ = await runs.snapshot(run_id)
        meta = runs.meta(run_id)
        if state is None:  # died before the first checkpoint: start it again under the same ID
            case_dir = await runs.ensure_case(meta["case"])
            runs.launch(run_id, "restarted", lambda ctx, on_node: gb.start_run(
                case_dir / "bundle", meta["sandbox"], ctx, run_id=run_id, on_node=on_node, db_path=runs.db(run_id)))
        else:
            runs.launch(run_id, "resumed", lambda ctx, on_node: gb.resume_run(
                run_id, ctx, on_node=on_node, db_path=runs.db(run_id)))
        return {"ok": True}

    @app.get("/api/runs/{run_id}/history")
    async def history(run_id: str):
        runs.dir(run_id)
        if not runs.db(run_id).exists():
            return []
        return [h async for h in gb.history(run_id, db_path=runs.db(run_id))]

    @app.get("/api/runs/{run_id}/patch")
    async def patch(run_id: str):
        runs.dir(run_id)
        state, _, _ = await runs.snapshot(run_id)
        if state is None or state.report is None or not state.report.patch:
            raise HTTPException(404, "no validated patch for this run")
        return PlainTextResponse(state.report.patch, media_type="text/x-diff",
                                 headers={"Content-Disposition": f'attachment; filename="{run_id}.patch"'})

    app.mount("/static", StaticFiles(directory=STATIC), name="static")
    return app


def answer_key(case_dir: Path, state: RunState) -> dict | None:
    """After a run finishes: the injector's ground truth, and how the diagnosis scored."""
    from evals.grade import grade
    from evals.models import GroundTruth

    f = case_dir / "ground_truth.json"
    if not f.exists():
        return None
    t = GroundTruth.model_validate_json(f.read_text())
    d = state.report.diagnosis if state.report else None
    return {"failure_class": t.failure_class, "affected_columns": t.affected_columns,
            "first_bad_partition": t.first_bad_partition, "root_cause": t.root_cause,
            "grade": grade(d, t) if d else None}
