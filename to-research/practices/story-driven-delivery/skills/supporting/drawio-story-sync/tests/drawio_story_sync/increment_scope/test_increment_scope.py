"""Drawio Story Sync → Increment Scope

Story Path: Drawio Story Sync → Increment Scope (synchronizer increment: filter).

Folder ``increment_scope`` = lowest sub-epic (ATDD). File ``test_*.py`` for pytest.

Behavior: increment-scoped render skips cleanly when that increment is not on the graph.
"""
from __future__ import annotations

from pathlib import Path


from ..drawio_story_sync_helper import (
    requires_story_graph_ops,
    given_empty_story_graph_file,
    when_synchronizer_renders_with_increment_scope,
    then_render_was_skipped_for_missing_increment,
)

pytestmark = requires_story_graph_ops


# =============================================================================
# STORY: Drawio Synchronizer Skips Missing Increment Scope
# =============================================================================


class TestDrawioSynchronizerSkipsMissingIncrementScope:
    """Increment-scoped render does not write output when the lane is absent."""

    def test_skips_when_increment_not_on_graph(self, tmp_path: Path) -> None:
        graph = given_empty_story_graph_file(tmp_path)
        out = tmp_path / "out.drawio"
        label = "Bring Heroes to the Table"
        result = when_synchronizer_renders_with_increment_scope(graph, out, label)
        then_render_was_skipped_for_missing_increment(result, "Bring Heroes", out)
