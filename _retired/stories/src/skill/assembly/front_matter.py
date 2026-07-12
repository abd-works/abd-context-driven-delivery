"""FrontMatter — the metadata block at the top of every skill file."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .fidelity import Fidelity


@dataclass(frozen=True)
class FrontMatter:
    fidelities: frozenset[Fidelity] = field(default_factory=frozenset)
    format: str | None = None
    section: str | None = None
    artifact: frozenset[str] = field(default_factory=frozenset)
    scanner: str | None = None
    raw: dict[str, Any] = field(default_factory=dict)

    def matches(self, fidelities: frozenset[Fidelity], format: str) -> bool:
        """A file matches when:

        - its fidelity set intersects the requested set, **and**
        - its format equals the requested format **or** is absent (universal).
        """
        if not self.fidelities.intersection(fidelities):
            return False
        if self.format is not None and self.format != format:
            return False
        return True
