"""CreateAgentToolset — scaffold @agent_toolset classes with @agent_tool and @agent_instructions."""

from __future__ import annotations

from practices.base.base_context_tool import BaseContextTool
from harness.agent_tools.agent_tools import agent_instructions


class CreateAgentToolset(BaseContextTool):
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
        super().__init__(format=format, path=path, session=session, workspace=workspace)

    @agent_instructions
    def guidance(recipe) -> str:
        """Provide guidance for scaffolding a decorated AgentToolSet."""
        return super().guidance()
