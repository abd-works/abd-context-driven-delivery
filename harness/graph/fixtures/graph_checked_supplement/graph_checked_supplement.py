"""A practice supplement for graph specs: it supplements BDD development and Clean Engineering code, and checks graph
rules on them, read from its own ``rules`` package as a pattern's are."""
from __future__ import annotations

import functools

from harness.graph.pattern_overlays import GraphOverlay
from harness.guidance.practice_supplement import PracticeSupplement


class GraphCheckedSupplement(PracticeSupplement):
    """# Instructions"""

    @functools.cached_property
    def graph_overlay(self) -> GraphOverlay:
        """Its graph rules on the practices it supplements, read from its own folder, as a pattern's are."""
        return GraphOverlay(self)
