"""TDD: the testing guidance and rules that supplement Clean Engineering code, Stories acceptance tests, BDD development,
and DDD tactics, on in every session."""

from __future__ import annotations

import functools

from harness.agent_tools.agent_tools import agent_toolset
from harness.graph.pattern_overlays import GraphOverlay
from harness.guidance.practice_supplement import PracticeSupplement


@agent_toolset
class Tdd(PracticeSupplement):
    """# Instructions"""

    SHORT_NAME = "TDD"

    @functools.cached_property
    def graph_overlay(self) -> GraphOverlay:
        """Its graph rules on the practices it supplements, read from its own folder, as a pattern's are."""
        return GraphOverlay(self)
