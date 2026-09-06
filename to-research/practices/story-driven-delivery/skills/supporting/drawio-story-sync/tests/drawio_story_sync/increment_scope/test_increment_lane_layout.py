"""Drawio Story Sync → Increment Lane Layout

Story Path: Drawio Story Sync → Increment Lane Layout (compact single-row height).

Behavior: increment swim lanes render at a height that comfortably fits exactly
one row of story sticky notes — less than half the unconstrained height.  The
compact height must hold for both render (fresh generation) and update/sync
(extraction reads back from file) so that dimension constants are the single
source of truth for both directions.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from ..drawio_story_sync_helper import (
    requires_story_graph_ops,
    STORY_GRAPH_WITH_ONE_INCREMENT,
    when_increments_diagram_is_rendered,
    then_increment_lane_height_is_compact,
    then_story_copies_are_within_lane_bounds,
)

# Increment graph that includes a story with an assigned user so actor
# rendering inside lanes can be tested.
_STORY_GRAPH_WITH_USER: dict = {
    "epics": [
        {
            "name": "Epic A",
            "sequential_order": 1.0,
            "sub_epics": [
                {
                    "name": "Sub A",
                    "sequential_order": 1.0,
                    "sub_epics": [],
                    "story_groups": [
                        {
                            "name": None,
                            "type": "and",
                            "connector": None,
                            "stories": [
                                {
                                    "name": "Story One",
                                    "sequential_order": 1.0,
                                    "story_type": "user",
                                    "users": ["Pet Owner"],
                                    "acceptance_criteria": [],
                                }
                            ],
                        }
                    ],
                }
            ],
        }
    ],
    "increments": [
        {
            "name": "Slice A",
            "priority": 1,
            "stories": [{"name": "Story One", "sequential_order": 1.0}],
            "description": "",
            "goal": "",
        }
    ],
}

pytestmark = requires_story_graph_ops


# ---------------------------------------------------------------------------
# Helpers local to this story
# ---------------------------------------------------------------------------

def _lane_height() -> int:
    from drawio_story_sync.drawio_story_node import DrawIOIncrementLane
    return DrawIOIncrementLane.LANE_HEIGHT


def _story_y_offset() -> int:
    from drawio_story_sync.drawio_story_node import DrawIOIncrementLane
    return DrawIOIncrementLane.STORY_Y_OFFSET


def _cell_size() -> int:
    from diagram_story_sync.layout_constants import CELL_SIZE
    return CELL_SIZE


# =============================================================================
# STORY: Increment Lane Renders Compact Single-Row Height
# =============================================================================


class TestIncrementLaneRendersCompactSingleRowHeight:
    """Increment swim lanes are short: one sticky note row, less than half the old height."""

    def test_lane_height_constant_fits_one_story_row(self) -> None:
        """LANE_HEIGHT must accommodate exactly one sticky note row (< 2 × CELL_SIZE)."""
        assert _lane_height() < _cell_size() * 2, (
            f"LANE_HEIGHT {_lane_height()} must be less than 2×CELL_SIZE "
            f"({_cell_size() * 2}) — lane must fit only one row of story squares"
        )

    def test_story_y_offset_leaves_room_for_bottom_padding(self) -> None:
        """STORY_Y_OFFSET + CELL_SIZE must be strictly less than LANE_HEIGHT (room for padding)."""
        story_bottom = _story_y_offset() + _cell_size()
        assert story_bottom < _lane_height(), (
            f"STORY_Y_OFFSET ({_story_y_offset()}) + CELL_SIZE ({_cell_size()}) = "
            f"{story_bottom} must be < LANE_HEIGHT ({_lane_height()}) for bottom padding"
        )

    def test_rendered_lane_element_height_matches_constant(self) -> None:
        """The rendered lane background element height equals LANE_HEIGHT."""
        from drawio_story_sync.drawio_story_node import DrawIOIncrementLane

        dm = when_increments_diagram_is_rendered(STORY_GRAPH_WITH_ONE_INCREMENT)
        assert dm._increment_lanes, "No increment lanes rendered"
        lane = dm._increment_lanes[0]
        assert lane._lane_element is not None
        assert lane._lane_element.boundary.height == DrawIOIncrementLane.LANE_HEIGHT, (
            f"Rendered height {lane._lane_element.boundary.height} "
            f"!= LANE_HEIGHT {DrawIOIncrementLane.LANE_HEIGHT}"
        )

    def test_rendered_lane_is_compact(self) -> None:
        """Rendered lane height is less than twice the sticky note size."""
        dm = when_increments_diagram_is_rendered(STORY_GRAPH_WITH_ONE_INCREMENT)
        max_height = _cell_size() * 2  # strict upper bound for single-row lanes
        then_increment_lane_height_is_compact(dm, max_height_px=max_height)

    def test_story_copies_are_inside_lane_bounds(self) -> None:
        """Story sticky note copies rendered inside the lane stay within its vertical bounds."""
        dm = when_increments_diagram_is_rendered(STORY_GRAPH_WITH_ONE_INCREMENT)
        then_story_copies_are_within_lane_bounds(dm)

    def test_label_fits_within_lane_height(self) -> None:
        """Lane label bottom edge does not exceed lane bottom."""
        from drawio_story_sync.drawio_story_node import DrawIOIncrementLane

        label_bottom = DrawIOIncrementLane.LABEL_Y_OFFSET + DrawIOIncrementLane.LABEL_HEIGHT
        assert label_bottom <= DrawIOIncrementLane.LANE_HEIGHT, (
            f"Label bottom {label_bottom} exceeds LANE_HEIGHT {DrawIOIncrementLane.LANE_HEIGHT}"
        )

    def test_no_actor_elements_rendered_inside_lanes_without_users(self) -> None:
        """Increment lanes do not render actor elements when stories have no users."""
        dm = when_increments_diagram_is_rendered(STORY_GRAPH_WITH_ONE_INCREMENT)
        for lane in dm._increment_lanes:
            assert lane._actor_elements == [], (
                f"Lane '{lane.name}' rendered {len(lane._actor_elements)} actor elements; "
                f"actors belong in the outline, not the lane"
            )

    def test_no_actor_elements_rendered_inside_lanes_with_users(self) -> None:
        """Increment lanes do not render actor elements even when stories have assigned users."""
        dm = when_increments_diagram_is_rendered(_STORY_GRAPH_WITH_USER)
        for lane in dm._increment_lanes:
            assert lane._actor_elements == [], (
                f"Lane '{lane.name}' rendered {len(lane._actor_elements)} actor elements "
                f"for a story with users; actors belong in the outline above, not in lanes"
            )


# =============================================================================
# STORY: Increment Lane Extraction Reads Back Compact Dimensions
# =============================================================================


class TestIncrementLaneExtractionReadsBackCompactDimensions:
    """After render → save → load, lane Y bounds still assign stories correctly."""

    def test_extraction_assigns_story_to_lane_after_compact_render(
        self, tmp_path: Path
    ) -> None:
        """Round-trip: render compact lanes, save, load, extract — story is in correct lane."""
        from drawio_story_sync.drawio_story_map import DrawIOIncrementsMap, DrawIOStoryMap
        from story_graph_ops.nodes import StoryMap

        sm = StoryMap(STORY_GRAPH_WITH_ONE_INCREMENT)
        dm = DrawIOIncrementsMap()
        dm.render(sm, sm.story_graph.get("increments", []))

        out = tmp_path / "increments.drawio"
        dm.save(out)

        loaded = DrawIOStoryMap.load(out, diagram_type="increments")
        extracted = loaded.extract_increment_assignments()

        assert extracted, "No increments extracted after compact render + reload"
        lane_names = [inc["name"] for inc in extracted]
        assert "Slice A" in lane_names, f"Expected 'Slice A' in {lane_names}"

        slice_a = next(inc for inc in extracted if inc["name"] == "Slice A")
        assert "Story One" in slice_a["stories"], (
            f"'Story One' not found in extracted lane stories: {slice_a['stories']}"
        )
