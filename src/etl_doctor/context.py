"""Turn a bundle directory into the text the model sees.

Step 1 has no tools, so this file decides everything the model can know. Two rules:

1. Bounded. Every block has a character cap, so a 2 GB log cannot blow the context
   window (or the bill). Logs keep their tail, because that is where tracebacks are.
2. Marked as untrusted. Bundle content comes from the broken system, not from us. It
   goes inside <untrusted source="..."> tags, and the system prompt says text in those
   tags is data, never instructions. This is the first defence against prompt injection
   (a log line saying "ignore previous instructions...").
"""

import re
from dataclasses import dataclass
from pathlib import Path

LOG_CHARS = 6_000
CODE_CHARS = 4_000
SAMPLE_ROWS = 3

CODE_FILES = [
    "demo_pipeline/pipeline/config.yaml",
    "demo_pipeline/pipeline/extract.py",
    "demo_pipeline/pipeline/transform.py",
]


@dataclass(frozen=True)
class Block:
    source: str  # path relative to the bundle root; the model cites this in Quote.source
    text: str


@dataclass(frozen=True)
class BundleContext:
    blocks: list[Block]
    current_files: list[str]

    def render(self) -> str:
        return "\n\n".join(
            f'<untrusted source="{b.source}">\n{escape(b.text)}\n</untrusted>' for b in self.blocks
        )

    def by_source(self) -> dict[str, str]:
        return {b.source: b.text for b in self.blocks}


def escape(text: str) -> str:
    # A log line containing "</untrusted>" must not be able to close the block early.
    return text.replace("</untrusted", "&lt;/untrusted")


def head(path: Path, max_chars: int) -> str:
    text = path.read_text(errors="replace")
    return text if len(text) <= max_chars else text[:max_chars] + f"\n... [truncated, {len(text)} chars total]"


def tail(path: Path, max_chars: int) -> str:
    text = path.read_text(errors="replace")
    return text if len(text) <= max_chars else f"[truncated, {len(text)} chars total] ...\n" + text[-max_chars:]


def first_lines(path: Path, n: int) -> str:
    with path.open(errors="replace") as fh:
        return "".join(line for _, line in zip(range(n), fh)).rstrip("\n")


def build_context(bundle: Path) -> BundleContext:
    blocks = [Block("problem.md", head(bundle / "problem.md", 2_000))]

    for name in ["pipeline.log", "quality_tests.log", "last_good_run.log"]:
        if (p := bundle / "logs" / name).exists():
            blocks.append(Block(f"logs/{name}", tail(p, LOG_CHARS)))

    for rel in CODE_FILES:
        if (p := bundle / rel).exists():
            blocks.append(Block(rel, head(p, CODE_CHARS)))

    # Data: the header and a few rows of every current file are cheap (about 100 tokens
    # each) and are often the only place a silent failure is visible.
    current = sorted((bundle / "data" / "current").glob("*.csv"))
    for p in current:
        blocks.append(Block(f"data/current/{p.name}", first_lines(p, SAMPLE_ROWS + 1)))
    last_good = sorted((bundle / "data" / "last_good").glob("*.csv"))
    if last_good:
        listing = "files: " + ", ".join(p.name for p in last_good)
        blocks.append(Block("data/last_good/", listing))
        blocks.append(Block(f"data/last_good/{last_good[-1].name}", first_lines(last_good[-1], SAMPLE_ROWS + 1)))

    return BundleContext(blocks, [p.name for p in current])


def normalize(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()
