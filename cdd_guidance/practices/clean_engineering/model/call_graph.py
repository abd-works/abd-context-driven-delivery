"""Call-graph lines for model sketch fidelity and story/BDD realizations.

Uses the same ``->`` / ``<-`` interaction arrows as clean-engineering model
operations (Unicode ``→`` / ``←`` accepted on read).
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable, List, Optional

_ARROW_OUT = re.compile(r"^(?:->|→)\s*(.+)$")
_ARROW_IN = re.compile(r"^(?:<-|←)\s*(.+)$")


@dataclass(frozen=True)
class CallGraphEntry:
    """One line in an indented call graph."""

    depth: int
    kind: str  # "call" | "out" | "in"
    text: str


def parse_arrow_line(stripped: str) -> Optional[tuple[str, str]]:
    """Parse a single interaction arrow line. Returns (kind, payload) or None."""
    if match := _ARROW_OUT.match(stripped):
        return ("out", match.group(1).strip())
    if match := _ARROW_IN.match(stripped):
        return ("in", match.group(1).strip())
    return None


class CallGraph(list):
    """An indented call graph: the operations a step or an observation reaches, one CallGraphEntry per line. It reads
    itself from a text block and writes itself as one."""

    @classmethod
    def parse(cls, text: str) -> "CallGraph":
        """The call graph a fenced or plain call-graph block holds."""
        graph = cls()
        for raw in text.splitlines():
            if not raw.strip():
                continue
            depth = (len(raw) - len(raw.lstrip(" "))) // 2
            stripped = raw.strip()
            arrow = parse_arrow_line(stripped)
            kind, payload = arrow if arrow is not None else ("call", stripped)
            graph.append(CallGraphEntry(depth=depth, kind=kind, text=payload))
        return graph

    @classmethod
    def of_callees(cls, callees: Iterable[str]) -> "CallGraph":
        """Flat ``->`` callees from a model operation, each one level deeper than the one before."""
        return cls(CallGraphEntry(depth=index + 1, kind="out", text=text) for index, text in enumerate(callees))

    def block(self) -> str:
        """This call graph as an indented text block, without fences."""
        lines: List[str] = []
        for entry in self:
            pad = "  " * entry.depth
            arrow = {"out": "-> ", "in": "<- "}.get(entry.kind, "")
            lines.append(f"{pad}{arrow}{entry.text}")
        return "\n".join(lines)

    def callees(self) -> List[str]:
        """The outbound calls, each once: the clean-engineering ``callees`` shape."""
        found: List[str] = []
        for entry in self:
            if entry.kind == "out" and entry.text and entry.text not in found:
                found.append(entry.text)
        return found
