"""BDD generator - multi-fidelity behavior skeletons and development."""

from __future__ import annotations

from harness.agent_tools.agent_tools import agent_tool, agent_toolset
from harness.guidance.guidance import PracticeGuidance


@agent_toolset
class Bdd(PracticeGuidance):
    """# Instructions

    Depends on CleanEngineering (lazy import to avoid circular imports at
    module load time).
    """

    def __init__(
        self,
        fidelity: str = "behavior",
        format: str | None = None,
        path: str | None = None,
        session: str | None = None,
    ) -> None:
        super().__init__(
            format=format,
            fidelity=fidelity,
            default_workspace_folder="src",
        )
        if path is not None or session is not None:
            self._attach_workspace(path=path, session=session)
