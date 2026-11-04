"""Export a finished run for the static replay site.

    etl-doctor export out/web/runs/<run_id> [--cases out/web/cases] [--out site/runs]

A run directory already has everything a replay needs: the live event log and the
checkpoint history (the state after every step, including each approval request the run
paused on). The export turns that into one JSON file the page can play back with no server:

    {"meta": ..., "events": [...], "frames": [{"t": ..., "run": <GET /api/runs/{id} shape>}],
     "history": [...]}

What is left out, because the file is published: sandbox IDs, local paths, the bundle
manifest, and full tool results (only the one-line evidence summaries are kept, as the live
page shows them). The CLI then checks the output for the API keys in the environment.
"""

import json
import re
from datetime import datetime
from pathlib import Path

from etl_doctor.graph.build import _config, open_graph
from etl_doctor.graph.state import RunState
from etl_doctor.web.app import answer_key

SANDBOX_ID = re.compile(r"\b[a-z0-9]{20}\b")  # E2B sandbox IDs in free text


def public_state(state: RunState) -> dict:
    d = state.model_dump(mode="json", exclude={"evidence": {"__all__": {"data"}}, "manifest": True,
                                               "bundle": True, "sandbox_id": True})
    return d


def _status(state: RunState, interrupted: bool) -> str:
    if interrupted:
        return "awaiting_approval"
    return state.report.status if state.report else "running"


def _scrub_event(e: dict) -> dict:
    e = dict(e)
    if e.get("node") == "provision_sandbox":
        e["detail"] = ""
    for k in ("detail", "message", "summary"):
        if isinstance(e.get(k), str):
            e[k] = SANDBOX_ID.sub("<sandbox>", e[k])
    return e


async def export_run(run_dir: Path, cases: Path | None = None) -> dict:
    run_id = run_dir.name
    meta = json.loads((run_dir / "meta.json").read_text())
    meta.pop("description", None)
    events = [_scrub_event(json.loads(line)) for line in (run_dir / "events.jsonl").read_text().splitlines()]

    frames, history = [], []
    async with open_graph(run_dir / "checkpoints.sqlite") as app:
        snaps = [s async for s in app.aget_state_history(_config(run_id))]
    for snap in reversed(snaps):  # oldest first
        if not snap.values or "run_id" not in snap.values:
            continue
        state = RunState.model_validate(snap.values)
        req = snap.interrupts[0].value if snap.interrupts else None
        run = {"meta": meta, "status": _status(state, req is not None), "next": list(snap.next),
               "approval": req, "state": public_state(state)}
        if state.report is not None and cases is not None:
            run["answer_key"] = answer_key(cases / meta["case"], state)
        t = datetime.fromisoformat(snap.created_at).timestamp()
        frames.append({"t": t, "run": run})
        history.append({"step": snap.metadata.get("step"), "next": list(snap.next),
                        "evidence": len(state.evidence), "tokens": state.usage.total_tokens,
                        "checkpoint_id": snap.config["configurable"]["checkpoint_id"]})
    if not frames or frames[-1]["run"]["state"]["report"] is None:
        raise ValueError(f"{run_id} has not finished: only finished runs are exported")
    history.reverse()  # newest first, like the live endpoint
    return {"meta": meta, "events": events, "frames": frames, "history": history}
