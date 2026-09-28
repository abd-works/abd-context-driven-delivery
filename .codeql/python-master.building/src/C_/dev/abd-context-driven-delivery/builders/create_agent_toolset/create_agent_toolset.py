"""CreateAgentToolset — scaffold @agent_toolset classes with @agent_tool and @agent_instructions."""

from __future__ import annotations

from harness.agent_tools.agent_tools import agent_toolset
from harness.guidance.guidance import PracticeGuidance


@agent_toolset
class CreateAgentToolset(PracticeGuidance):
    """# Instructions"""

    default_workspace_folder: str = "."
    context_index_key: str = "create_agent_toolset"

    def __init__(
        self,
        format: str | None = None,
        path: str | None = None,
        session: str | None = None,
        workspace: str | None = None,
    ) -> None:
        super().__init__(format=format)
        self._attach_workspace(path=path, session=session, workspace=workspace)
