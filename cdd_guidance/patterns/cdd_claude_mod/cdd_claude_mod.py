"""CddClaudeMod generator - implementation fidelity for a Claude Code mod that is a view of the CDD domain.
The domain stays in Python. Each component runs one straight line: view, client, MCP tool, domain.
See space/kanban for the worked example."""

from __future__ import annotations

from functools import cached_property

from harness.agent_tools.agent_tools import agent_toolset
from harness.graph.pattern_overlays import GraphOverlay
from harness.guidance.guidance import PracticeGuidance


@agent_toolset
class CddClaudeMod(PracticeGuidance):
    """A Claude Code mod that is a view of the CDD domain: each component runs view, client, MCP tool, domain."""

    pattern = "cdd_claude_mod"

    def __init__(self) -> None:
        super().__init__(
            format="typescript",
            default_workspace_folder="harness",
        )

    @cached_property
    def graph_overlay(self) -> GraphOverlay:
        """What this pattern gives the knowledge graph on top of the practices: no nodes, only the rules it adds to each practice. Made once and kept."""
        return GraphOverlay(self)
