"""Where tool code runs. The agent's tools only know this interface.

Step 2: LocalExecutor runs `python -m edtools` as a subprocess with the bundle as its
working directory. That gives a JSON-only boundary, a timeout and an output cap, but it
is NOT isolation: the subprocess can read the whole machine. Step 3 adds an executor that
runs the same command inside an E2B microVM, and nothing above this file changes.
"""

import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Any, Protocol


class Executor(Protocol):
    async def edtools(self, command: str, args: dict[str, Any]) -> dict[str, Any]:
        """Returns {"result": ...} or {"error": "..."}; raises only on infrastructure failure."""
        ...


class LocalExecutor:
    def __init__(self, bundle: Path, timeout_s: float = 30, max_output_bytes: int = 64_000):
        self.bundle = bundle.resolve()
        self.timeout_s = timeout_s
        self.max_output_bytes = max_output_bytes

    async def edtools(self, command: str, args: dict[str, Any]) -> dict[str, Any]:
        proc = await asyncio.create_subprocess_exec(
            sys.executable, "-m", "edtools", command, json.dumps(args),
            cwd=self.bundle,
            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        try:
            out, err = await asyncio.wait_for(proc.communicate(), self.timeout_s)
        except TimeoutError:
            proc.kill()
            return {"error": f"{command} timed out after {self.timeout_s}s; narrow the request"}
        if proc.returncode not in (0, 2):
            # A crash in our own tool code is a harness bug, not something the model can fix.
            raise RuntimeError(f"edtools {command} crashed (exit {proc.returncode}): {err.decode()[-2000:]}")
        if len(out) > self.max_output_bytes:
            return {"error": f"{command} output too large ({len(out)} bytes); narrow the request"}
        return json.loads(out)
