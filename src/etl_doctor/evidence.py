"""Evidence is recorded by the tools as they run, not reported by the model.

The model only ever sees an evidence ID next to a tool result. When it cites "ev-004" in
its diagnosis, we can check that ev-004 exists and show a human exactly which tool call,
with which arguments, produced it. The model can't invent evidence, and it can't edit it.
"""

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class Evidence:
    id: str
    tool: str
    args: dict[str, Any]
    summary: str  # one line for humans and for the final report
    data: Any  # the tool result, as the model saw it


@dataclass
class EvidenceStore:
    on_add: Callable[[Evidence], None] | None = None
    _items: dict[str, Evidence] = field(default_factory=dict)

    def add(self, tool: str, args: dict[str, Any], summary: str, data: Any) -> Evidence:
        ev = Evidence(f"ev-{len(self._items) + 1:03d}", tool, args, summary, data)
        self._items[ev.id] = ev
        if self.on_add:
            self.on_add(ev)
        return ev

    def ids(self) -> set[str]:
        return set(self._items)

    def get(self, ev_id: str) -> Evidence:
        return self._items[ev_id]

    def all(self) -> list[Evidence]:
        return list(self._items.values())
