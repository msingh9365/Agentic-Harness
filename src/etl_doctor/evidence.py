"""Evidence is recorded by the tools as they run, not reported by the model.

The model only ever sees an evidence ID next to a tool result. When it cites "ev-004" in
its diagnosis, we can check that ev-004 exists and show a human exactly which tool call,
with which arguments, produced it. The model can't invent evidence, and it can't edit it.
"""

from collections.abc import Callable, Iterable
from typing import Any

from pydantic import BaseModel, ConfigDict


class Evidence(BaseModel):
    # A Pydantic model (not a dataclass) so it can live in checkpointed graph state.
    model_config = ConfigDict(frozen=True)

    id: str
    tool: str
    args: dict[str, Any]
    summary: str  # one line for humans and for the final report
    data: Any  # the tool result, as the model saw it


class EvidenceStore:
    def __init__(self, on_add: Callable[[Evidence], None] | None = None, existing: Iterable[Evidence] = ()):
        """`existing`: evidence from earlier steps, so new IDs continue the sequence."""
        self.on_add = on_add
        self._items: dict[str, Evidence] = {e.id: e for e in existing}
        self._new: list[Evidence] = []

    def add(self, tool: str, args: dict[str, Any], summary: str, data: Any) -> Evidence:
        ev = Evidence(id=f"ev-{len(self._items) + 1:03d}", tool=tool, args=args, summary=summary, data=data)
        self._items[ev.id] = ev
        self._new.append(ev)
        if self.on_add:
            self.on_add(ev)
        return ev

    def ids(self) -> set[str]:
        return set(self._items)

    def get(self, ev_id: str) -> Evidence:
        return self._items[ev_id]

    def all(self) -> list[Evidence]:
        return list(self._items.values())

    def new(self) -> list[Evidence]:
        """Evidence added through this store (not the `existing` it was seeded with)."""
        return list(self._new)
