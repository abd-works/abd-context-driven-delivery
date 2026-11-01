"""CddClaudeMod generator - implementation fidelity for a Claude Code mod that is a view of the CDD domain.
The domain stays in Python. Each component runs one straight line: view, client, MCP tool, domain.
See harness/kanban for the worked example."""

from __future__ import annotations

from harness.agent_tools.agent_tools import agent_toolset
from harness.guidance.guidance import PracticeGuidance


@agent_toolset
class CddClaudeMod(PracticeGuidance):
    """# Instructions"""

    pattern = "cdd_claude_mod"

    def __init__(self) -> None:
        super().__init__(
            format="typescript",
            default_workspace_folder="harness",
        )
