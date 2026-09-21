"""Parse bounded-context-map.md (BC → Aggregate tree)."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


@dataclass
class AggregateEntry:
    name: str
    concepts: List[str] = field(default_factory=list)


@dataclass
class BoundedContextEntry:
    name: str
    aggregates: List[AggregateEntry] = field(default_factory=list)


_BC_HEADING = re.compile(r"^##\s+(.+?)(?:\s*\||\s*$)")
_AGG_HEADING = re.compile(r"^###\s+(.+?)\s*$")
_CONCEPT_BULLET = re.compile(r"^-\s+(.+?)\s*$")


def parse_bounded_context_map(text: str) -> List[BoundedContextEntry]:
    contexts: List[BoundedContextEntry] = []
    current_bc: BoundedContextEntry | None = None
    current_agg: AggregateEntry | None = None

    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("<!--"):
            continue

        m_bc = _BC_HEADING.match(line)
        if m_bc:
            name = m_bc.group(1).strip()
            current_bc = BoundedContextEntry(name=name)
            contexts.append(current_bc)
            current_agg = None
            continue

        m_agg = _AGG_HEADING.match(line)
        if m_agg and current_bc is not None:
            current_agg = AggregateEntry(name=m_agg.group(1).strip())
            current_bc.aggregates.append(current_agg)
            continue

        m_concept = _CONCEPT_BULLET.match(line)
        if m_concept and current_agg is not None:
            concept = m_concept.group(1).split("→")[0].strip()
            if concept and not concept.startswith("→"):
                current_agg.concepts.append(concept)

    return contexts


def load_bounded_context_map(root: Path) -> List[BoundedContextEntry]:
    for name in ("bounded-context-map.md", "examples.md"):
        for path in sorted(root.glob(f"**/{name}")):
            text = path.read_text(encoding="utf-8", errors="ignore")
            if "Bounded Context Map" in text or _BC_HEADING.search(text):
                parsed = parse_bounded_context_map(text)
                if parsed:
                    return parsed
    return []
