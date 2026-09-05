"""Tests for ``story_graph_ops.story_graph_scope`` (vendored scope filters).

Behaviors covered:
- StoryGraphFilter with increment scope trims epics and increments
- StoryGraphScope filters an on-disk story graph by story name
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Sequence

from story_graph_ops.story_graph_scope import (
    ScopeType,
    StoryGraphFilter,
    StoryGraphScope,
)

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================


def given_sample_graph_with_two_increment_lanes() -> Dict[str, Any]:
    """Given: graph with one story and two increment lanes."""
    return {
        "epics": [
            {
                "name": "E1",
                "sub_epics": [
                    {
                        "name": "SE1",
                        "story_groups": [
                            {"name": None, "stories": [{"name": "S1"}]},
                        ],
                    }
                ],
            }
        ],
        "increments": [
            {"name": "Lane A", "priority": 1, "stories": [{"name": "S1"}]},
            {"name": "Lane B", "priority": 2, "stories": [{"name": "Other"}]},
        ],
    }


def when_filter_by_increments(
    graph: Dict[str, Any], increment_names: List[str]
) -> Dict[str, Any]:
    """When: StoryGraphFilter restricts to named increments."""
    flt = StoryGraphFilter(increments=increment_names)
    return flt.filter_story_graph(graph)


def given_story_graph_on_disk(workspace: Path, story_name: str) -> Path:
    """Given: docs/story/story-graph.json containing one story."""
    sg = workspace / "docs" / "story" / "story-graph.json"
    sg.parent.mkdir(parents=True)
    sg.write_text(
        '{"epics":[{"name":"Epic","sub_epics":[{"name":"Sub","story_groups":'
        '[{"name":null,"stories":[{"name":"'
        + story_name
        + '"}]}]}]}],"increments":[]}',
        encoding="utf-8",
    )
    return sg


def when_scope_filters_stories(
    scope: StoryGraphScope, story_names: Sequence[str]
) -> None:
    """When: StoryGraphScope applies STORY filter."""
    scope.filter(ScopeType.STORY, list(story_names))


def then_single_named_increment_and_epics_remain(
    out: Dict[str, Any], increment_name: str
) -> None:
    """Then: one increment remains with expected name; epics non-empty."""
    assert len(out["increments"]) == 1
    assert out["increments"][0]["name"] == increment_name
    assert out["epics"] and out["epics"][0]["sub_epics"]


def then_scope_filtered_graph_keeps_epic_name(
    scope: StoryGraphScope, epic_name: str
) -> None:
    """Then: filtered_story_graph retains the epic name."""
    data = scope.filtered_story_graph
    assert data is not None
    assert data["epics"][0]["name"] == epic_name


# =============================================================================
# STORY: increment-scoped filter
# =============================================================================


class TestStoryGraphFilterByIncrements:
    """Filtering by increment name keeps only matching lanes and related epics."""

    def test_limits_epics_and_increments_to_lane(self) -> None:
        # Given
        graph = given_sample_graph_with_two_increment_lanes()
        # When
        out = when_filter_by_increments(graph, ["Lane A"])
        # Then
        then_single_named_increment_and_epics_remain(out, "Lane A")


# =============================================================================
# STORY: scope filters on-disk graph
# =============================================================================


class TestStoryGraphScopeFiltersStoryGraphDict:
    """StoryGraphScope reads a file tree and exposes filtered_story_graph."""

    def test_filters_to_requested_story(self, tmp_path: Path) -> None:
        # Given
        given_story_graph_on_disk(tmp_path, "KeepMe")
        scope = StoryGraphScope(tmp_path)
        # When
        when_scope_filters_stories(scope, ["KeepMe"])
        # Then
        then_scope_filtered_graph_keeps_epic_name(scope, "Epic")
