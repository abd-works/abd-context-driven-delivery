"""SkillFile — one file inside a skill package, addressed by its top-level directory
(``rules``, ``templates``, ``concepts``, …) and its path relative to the skill root."""

from __future__ import annotations

from dataclasses import dataclass

from .fidelity import Fidelity
from .front_matter import FrontMatter


@dataclass(frozen=True)
class SkillFile:
    path: str
    directory: str
    front_matter: FrontMatter

    def matches(self, fidelities: frozenset[Fidelity], format: str) -> bool:
        return self.front_matter.matches(fidelities, format)
