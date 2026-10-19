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


def parse_call_graph_block(text: str) -> List[CallGraphEntry]:
    """Parse a fenced or plain call-graph block into entries."""
    entries: List[CallGraphEntry] = []
    for raw in text.splitlines():
        if not raw.strip():
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        depth = indent // 2
        stripped = raw.strip()
        arrow = parse_arrow_line(stripped)
        if arrow is not None:
            kind, payload = arrow
            entries.append(CallGraphEntry(depth=depth, kind=kind, text=payload))
            continue
        entries.append(CallGraphEntry(depth=depth, kind="call", text=stripped))
    return entries


def render_call_graph_block(entries: Iterable[CallGraphEntry]) -> str:
    """Render entries as an indented call-graph text block (no fences)."""
    lines: List[str] = []
    for entry in entries:
        pad = "  " * entry.depth
        if entry.kind == "out":
            lines.append(f"{pad}-> {entry.text}")
        elif entry.kind == "in":
            lines.append(f"{pad}<- {entry.text}")
        else:
            lines.append(f"{pad}{entry.text}")
    return "\n".join(lines)


def call_graph_to_callees(entries: Iterable[CallGraphEntry]) -> List[str]:
    """Flat outbound interaction list (clean-engineering ``callees`` shape)."""
    callees: List[str] = []
    for entry in entries:
        if entry.kind == "out" and entry.text and entry.text not in callees:
            callees.append(entry.text)
    return callees


def callees_to_call_graph(callees: Iterable[str]) -> List[CallGraphEntry]:
    """Lift flat ``->`` callees from a model operation into graph entries."""
    return [CallGraphEntry(depth=index + 1, kind="out", text=text) for index, text in enumerate(callees)]
