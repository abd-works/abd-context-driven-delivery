"""CddAccess generator - how anything outside Python reaches the CDD domain.
The domain stays in Python. Skills, actions, and commands reach it through MCP tools, and a TypeScript server reaches
those same tools through the language adapter the installer deploys. See harness/kanban/app for the worked example."""

from __future__ import annotations

from harness.agent_tools.agent_tools import agent_toolset
from harness.guidance.guidance import PracticeGuidance


@agent_toolset
class CddAccess(PracticeGuidance):
    """# Instructions"""

    pattern = "cdd_access"

    def __init__(self) -> None:
        super().__init__(
            format="typescript",
            default_workspace_folder="harness",
        )
