"""A practice supplement for specs: it supplements BDD development and Clean Engineering code."""
from __future__ import annotations

import functools
from typing import Any

from harness.guidance.practice_supplement import PracticeSupplement


class SampleSupplement(PracticeSupplement):
    """# Instructions"""

    @functools.cached_property
    def graph_overlay(self) -> Any:
        """Its graph rules on the practices it supplements, read from its own folder, as a pattern's are."""
        from harness.graph.pattern_overlays import GraphOverlay

        return GraphOverlay(self)
