"""CreateContextTool - scaffold new PracticeGuidance domains under practices/."""

from __future__ import annotations

from harness.agent_tools.agent_tools import agent_instructions, agent_toolset
from harness.guidance.guidance import PracticeGuidance


@agent_toolset
class CreateContextTool(PracticeGuidance):
    """# Instructions"""

    default_workspace_folder: str = "."
    context_index_key: str = "create_context_tool"

    def __init__(
        self,
        format: str | None = None,
        path: str | None = None,
        session: str | None = None,
        workspace: str | None = None,
    ) -> None:
        super().__init__(
            format=format,
            path=path,
            session=session,
            workspace=workspace,
        )

    @agent_instructions
    def guidance(recipe) -> str:
        """Provide guidance for scaffolding new context-tool domains."""
        return super().guidance()
