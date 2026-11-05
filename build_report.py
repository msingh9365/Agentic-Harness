#!/usr/bin/env python
"""Build REPORT.md from REPORT.src.md by replacing each
    <!-- include: <heading> -->
line with the block under that heading in results/tables.md
(everything up to the next markdown heading). This keeps the tables in the
report identical to what analyze.py produced."""
import re
import sys

SOURCES = {"": "results/tables.md", "avast": "results/avast/tables.md", "hier": "results/hier/summary.md"}
TABLES = {k: open(v).read().splitlines() for k, v in SOURCES.items() if __import__("os").path.exists(v)}


def block(heading):
    # "<!-- include: avast: Heading -->" reads results/avast/tables.md
    src = ""
    if ":" in heading and heading.split(":", 1)[0].strip() in SOURCES:
        src, heading = heading.split(":", 1)[0].strip(), heading.split(":", 1)[1].strip()
    tables = TABLES[src]
    for i, line in enumerate(tables):
        if line.startswith("#") and line.lstrip("#").strip() == heading:
            out = []
            for l in tables[i + 1:]:
                if l.startswith("#"):
                    break
                out.append(l)
            return "\n".join(out).strip("\n")
    sys.exit(f"heading not found in results/tables.md: {heading!r}")


src = open("REPORT.src.md").read()
out = re.sub(r"<!-- include: (.+?) -->", lambda m: block(m.group(1).strip()), src)
open("REPORT.md", "w").write(out)
print("wrote REPORT.md")
