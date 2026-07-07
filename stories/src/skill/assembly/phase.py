"""Phase — the workflow step that determines which directories the manifest scopes to.

The three phases follow the read discipline in ``stories/behavior/skill-workflow.md``:

- INTERVIEW — ask the user; understand what already exists.
- GENERATE  — assemble the artifact.
- VALIDATE  — re-check the generated artifact against rules.
"""

from __future__ import annotations

from enum import Enum


class UnknownPhaseError(ValueError):
    def __init__(self, value: str):
        super().__init__(f"Unknown phase: {value!r}")
        self.value = value


class Phase(str, Enum):
    INTERVIEW = "interview"
    GENERATE = "generate"
    VALIDATE = "validate"

    @classmethod
    def parse(cls, value: str) -> "Phase":
        try:
            return cls(value)
        except ValueError as error:
            raise UnknownPhaseError(value) from error

    def directories(self) -> tuple[str, ...]:
        return _PHASE_SCOPE[self]


_PHASE_SCOPE: dict[Phase, tuple[str, ...]] = {
    Phase.INTERVIEW: ("concepts", "grill-me-questions"),
    Phase.GENERATE: (
        "concepts",
        "behavior",
        "generate-instructions",
        "templates",
        "rules",
        "examples",
    ),
    Phase.VALIDATE: ("rules",),
}
