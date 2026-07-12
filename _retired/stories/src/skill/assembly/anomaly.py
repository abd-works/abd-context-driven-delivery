"""Anomaly — a soft-fail signal raised during assembly and reported alongside output.

The CLI never aborts on recoverable issues (typos, missing front matter, section
collisions). It emits the best-effort manifest **and** a structured list of anomalies
so the AI can surface them to the user before generation continues.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class Anomaly:
    kind: str
    file: str
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {"kind": self.kind, "file": self.file, "details": dict(self.details)}
