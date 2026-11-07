"""How the CDD Claude mod pattern takes part in the graph: it adds no nodes, and its guidance gives its rules their prose."""

from __future__ import annotations

from harness.graph.graph_practice import GraphOverlay, GraphPractices


class ClaudeModOverlay(GraphOverlay):
    def guidance(self):
        from cdd_guidance.patterns.cdd_claude_mod.cdd_claude_mod import CddClaudeMod

        return CddClaudeMod()


GraphPractices.register_overlay(ClaudeModOverlay("cdd_claude_mod"))
