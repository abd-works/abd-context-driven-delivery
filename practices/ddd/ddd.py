"""DDD generator - domain emphasis, contexts, building blocks over clean_engineering."""

from __future__ import annotations

from harness.agent_tools.agent_tools import agent_toolset
from harness.guidance.guidance import PracticeGuidance


@agent_toolset
class Ddd(PracticeGuidance):
    """# Instructions

    Depends on CleanEngineering (lazy import to avoid circular imports at
    module load time).
    """

    def __init__(
        self,
        fidelity: str = "bounded_context",
        format: str | None = None,
        stage: str | None = None,
    ) -> None:
        super().__init__(
            format=format,
            fidelity=None if stage is not None else fidelity,
            default_workspace_folder="src",
        )
        if stage is not None:
            self._activate(stage=stage)

    def _skip_inactive_fidelity(self, current_name: str | None, name: str) -> bool:
        del current_name, name
        return False
