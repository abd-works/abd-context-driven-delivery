"""CddClaudeMod generator - implementation fidelity for a Claude Code mod that is a view of the CDD domain.
The domain stays in Python. Each component runs one straight line: view, client, MCP tool, domain.
See space/kanban for the worked example."""

from __future__ import annotations

from harness.agent_tools.agent_tools import agent_toolset

from cdd_guidance.patterns.pattern import Pattern


@agent_toolset
class CddClaudeMod(Pattern):
    """A Claude Code mod that is a view of the CDD domain: each component runs view, client, MCP tool, domain."""

    default_workspace_folder = "harness"
