"""Drawio Story Sync → Outline Story Graph Sync

Story Path: Drawio Story Sync → Outline Story Graph Sync (personas, update report).

Folder ``outline_story_graph_sync`` = lowest sub-epic (ATDD). File ``test_*.py`` for pytest.

Behaviors: canonical users survive round-trip diff; outline row personas (column + forward fill).
"""
from __future__ import annotations

from pathlib import Path


from ..drawio_story_sync_helper import (
    requires_story_graph_ops,
    given_minimal_epic_graph_with_story_users,
    given_two_story_columns_and_actor_chip_over_story_b_column,
    given_three_story_row_with_actor_chip_above_first_column,
    when_outline_is_rendered_loaded_and_diffed_against_canonical,
    when_outline_row_personas_are_applied,
    then_story_users_changes_list_is_empty,
    then_chip_over_second_column_assigns_persona_to_b_only,
    then_story_row_users_match_forward_fill_from_chip,
)

pytestmark = requires_story_graph_ops


# =============================================================================
# STORY: Preserve Canonical Story Users On Sync When Diagram Omits Deduped Actor Cells
# =============================================================================


class TestPreserveCanonicalStoryUsersOnSyncWhenDiagramOmitsDedupedActorCells:
    """Round-trip outline render and diff emits no story users changes when graph matches."""

    def test_outline_reload_and_diff_emits_no_story_users_changes(
        self, tmp_path: Path
    ) -> None:
        _graph_path, drawio_path, graph = given_minimal_epic_graph_with_story_users(
            tmp_path, story_users=["Game Master"]
        )
        report = when_outline_is_rendered_loaded_and_diffed_against_canonical(
            graph, drawio_path
        )
        then_story_users_changes_list_is_empty(report)


# =============================================================================
# STORY: Outline Row Personas Column And Forward Fill
# =============================================================================


class TestOutlineRowPersonasColumnAndForwardFill:
    """Explicit chip above a column; following stories inherit until the next explicit."""

    def test_chip_column_assigns_persona_not_id_path(self) -> None:
        ordered, persona_nodes, st_a, st_b = (
            given_two_story_columns_and_actor_chip_over_story_b_column()
        )
        when_outline_row_personas_are_applied(ordered, persona_nodes)
        then_chip_over_second_column_assigns_persona_to_b_only(st_a, st_b)

    def test_forward_fill_carries_explicit_to_stories_without_chip(self) -> None:
        ordered, chip = given_three_story_row_with_actor_chip_above_first_column()
        when_outline_row_personas_are_applied(ordered, chip)
        then_story_row_users_match_forward_fill_from_chip(ordered, "Game Master")
