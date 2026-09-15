"""CreateContextTool - scaffold new BaseContextTool domains under context_tools/."""

from __future__ import annotations

from context_tools.base.base_context_tool import BaseContextTool
from primitives.actions.action import agent_instructions


class CreateContextTool(BaseContextTool):
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
        super().__init__(format=format, path=path, session=session, workspace=workspace)

    @agent_instructions
    def guidance(self) -> str:
        """Provide guidance for scaffolding new context-tool domains."""
        return super().guidance()
