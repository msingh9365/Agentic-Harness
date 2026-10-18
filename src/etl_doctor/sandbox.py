"""Step 3: run the tools inside an E2B sandbox (a Firecracker microVM) instead of on the host.

Same Executor interface as LocalExecutor, so the agent and the tools don't change.
What changes is the blast radius of a mistake. If the model, a poisoned log line, or a
bug in our path checks makes a tool do something unintended, it happens inside a
disposable VM that:
- has its own kernel (a microVM, not a container sharing the host kernel);
- has no internet access (allow_internet_access=False), so nothing can be exfiltrated;
- holds only a copy of the bundle, not the host's files, env vars or API keys;
- is destroyed when the run ends, and has a hard timeout in case we never get there.
"""

import io
import json
import shlex
import tarfile
import time
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, AsyncIterator

from e2b import AsyncSandbox, CommandExitException, TimeoutException

import edtools

TEMPLATE = "etl-doctor-v1"  # built by sandbox/build_template.py
WORKSPACE = "/workspace"
EDTOOLS_ROOT = "/opt/edtools"  # the package goes to /opt/edtools/edtools, on PYTHONPATH


def _tarball(files: dict[str, Path]) -> bytes:
    """tar.gz of {archive name: local path}, skipping caches. One upload instead of hundreds."""
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as tar:
        for name, path in files.items():
            tar.add(path, arcname=name, filter=lambda t: None if "__pycache__" in t.name else t)
    return buf.getvalue()


class E2BExecutor:
    def __init__(self, sandbox: AsyncSandbox, cmd_timeout_s: float = 60, max_output_bytes: int = 64_000):
        self.sandbox = sandbox
        self.cmd_timeout_s = cmd_timeout_s
        self.max_output_bytes = max_output_bytes
        self.started = time.monotonic()

    @property
    def sandbox_id(self) -> str:
        return self.sandbox.sandbox_id

    @classmethod
    async def create(cls, bundle: Path, template: str = TEMPLATE, timeout_s: int = 900) -> "E2BExecutor":
        """Create a sandbox and copy the bundle and the tool code in. Caller must kill() it."""
        sandbox = await AsyncSandbox.create(
            template=template,
            timeout=timeout_s,  # E2B kills the VM after this even if we crash before kill()
            allow_internet_access=False,
            metadata={"app": "etl-doctor"},
        )
        try:
            archive = _tarball({"bundle": bundle.resolve(), "edtools": Path(edtools.__file__).parent})
            await sandbox.files.write("/tmp/upload.tgz", archive)
            await sandbox.commands.run(
                f"tar xzf /tmp/upload.tgz -C /tmp && cp -r /tmp/bundle/. {WORKSPACE}/ "
                f"&& cp -r /tmp/edtools {EDTOOLS_ROOT}/ && rm -rf /tmp/upload.tgz /tmp/bundle /tmp/edtools",
                timeout=60,
            )
        except BaseException:
            await sandbox.kill()
            raise
        return cls(sandbox)

    @classmethod
    async def connect(cls, sandbox_id: str, timeout_s: int = 900) -> "E2BExecutor":
        """Reattach to a running sandbox (e.g. after the host process crashed and resumed).
        Its workspace is exactly as we left it, so nothing is re-uploaded."""
        return cls(await AsyncSandbox.connect(sandbox_id, timeout=timeout_s))

    async def kill(self) -> None:
        await self.sandbox.kill()

    @classmethod
    @asynccontextmanager
    async def start(cls, bundle: Path, template: str = TEMPLATE, timeout_s: int = 900) -> AsyncIterator["E2BExecutor"]:
        """create() + kill() as a context manager: the sandbox never outlives the block."""
        ex = await cls.create(bundle, template, timeout_s)
        try:
            yield ex
        finally:
            await ex.kill()

    async def run(self, cmd: str, timeout_s: float | None = None) -> tuple[int, str, str]:
        """Run a shell command in the sandbox. Used by tests and by later steps (validation)."""
        try:
            r = await self.sandbox.commands.run(cmd, cwd=WORKSPACE, timeout=timeout_s or self.cmd_timeout_s)
            return r.exit_code, r.stdout, r.stderr
        except CommandExitException as e:  # the SDK raises on non-zero exit
            return e.exit_code, e.stdout, e.stderr

    async def edtools(self, command: str, args: dict[str, Any]) -> dict[str, Any]:
        cmd = f"PYTHONPATH={EDTOOLS_ROOT} PYTHONDONTWRITEBYTECODE=1 python -m edtools {command} {shlex.quote(json.dumps(args))}"
        try:
            code, out, err = await self.run(cmd)
        except TimeoutException:
            return {"error": f"{command} timed out after {self.cmd_timeout_s}s; narrow the request"}
        if code not in (0, 2):
            raise RuntimeError(f"edtools {command} crashed in sandbox (exit {code}): {err[-2000:]}")
        if len(out) > self.max_output_bytes:
            return {"error": f"{command} output too large ({len(out)} bytes); narrow the request"}
        return json.loads(out)

    def seconds(self) -> float:
        return time.monotonic() - self.started
