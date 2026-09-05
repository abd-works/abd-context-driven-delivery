"""DiagramStoryMap — positioning layer shared by every diagram backend.

Grid model:

- Y row layout (top -> bottom):
    Epic row               y = 0
    SubEpic row depth d    y = (d + 1) * ROW_HEIGHT   for d in 0..max_depth
    Actor row              y = (max_depth + 2) * ROW_HEIGHT
    Story row              y = (max_depth + 3) * ROW_HEIGHT
- X layout: Epic X is the cumulative width of previous Epics; a SubEpic's X is
  its parent's X plus the cumulative width of its preceding siblings. Each leaf
  SubEpic contributes `BASE_WIDTH`; parent widths are the sum of child widths.
"""

from __future__ import annotations

from typing import Iterable, List, Optional

from src.core.stories.nodes import Epic, Story, SubEpic
from src.core.stories.story_map import StoryMap

BASE_WIDTH = 200
ROW_HEIGHT = 100


class PlacementError(Exception):
    """Raised when a placement would violate the Epic > SubEpic > Story hierarchy."""


class DiagramStoryMap:
    """Wraps a canonical StoryMap and exposes positions/dimensions per node."""

    def __init__(self, story_map: Optional[StoryMap] = None):
        self._story_map = story_map if story_map is not None else StoryMap()

    @property
    def story_map(self) -> StoryMap:
        return self._story_map

    @property
    def epics(self) -> List[Epic]:
        return self._story_map.epics

    def append_epic(self, epic: Epic) -> None:
        self._story_map.append_epic(epic)

    def remove_epic(self, name: str) -> Epic:
        return self._story_map.remove_epic(name)

    def max_sub_epic_depth(self) -> int:
        deepest = 0
        for epic in self._story_map.epics:
            for sub in epic.sub_epics:
                deepest = max(deepest, self._depth_from(sub, current=0))
        return deepest

    def epic_row_y(self) -> int:
        return 0

    def sub_epic_row_y(self, depth: int) -> int:
        return (depth + 1) * ROW_HEIGHT

    def actor_row_y(self) -> int:
        return (self.max_sub_epic_depth() + 2) * ROW_HEIGHT

    def story_row_y(self) -> int:
        return (self.max_sub_epic_depth() + 3) * ROW_HEIGHT

    def epic_width(self, epic: Epic) -> int:
        if not epic.sub_epics:
            return BASE_WIDTH
        return sum(self.sub_epic_width(s) for s in epic.sub_epics)

    def sub_epic_width(self, sub_epic: SubEpic) -> int:
        if not sub_epic.sub_epics:
            return BASE_WIDTH
        return sum(self.sub_epic_width(s) for s in sub_epic.sub_epics)

    def epic_x(self, epic: Epic) -> int:
        offset = 0
        for candidate in self._story_map.epics:
            if candidate is epic:
                return offset
            offset += self.epic_width(candidate)
        raise KeyError(f"Epic {epic.name!r} not part of this diagram")

    def sub_epic_x(self, sub_epic: SubEpic) -> int:
        for epic in self._story_map.epics:
            x = self._find_sub_epic_x(sub_epic, self.epic_x(epic), epic.sub_epics)
            if x is not None:
                return x
        raise KeyError(f"SubEpic {sub_epic.name!r} not part of this diagram")

    def sub_epic_y(self, sub_epic: SubEpic) -> int:
        return self.sub_epic_row_y(self.sub_epic_depth(sub_epic))

    def sub_epic_depth(self, sub_epic: SubEpic) -> int:
        for epic in self._story_map.epics:
            depth = self._depth_of(sub_epic, epic.sub_epics, current=0)
            if depth is not None:
                return depth
        raise KeyError(f"SubEpic {sub_epic.name!r} not part of this diagram")

    def story_x(self, story: Story) -> int:
        parent = self._parent_sub_epic_of_story(story)
        return self.sub_epic_x(parent)

    def story_y(self, story: Story) -> int:
        return self.story_row_y()

    def actor_y(self) -> int:
        return self.actor_row_y()

    def place_child_under_parent(self, child, parent) -> None:
        # WHY: single guard on all invalid placements — every rejection leaf
        # collapses to a check on the type pair (parent, child).
        if isinstance(parent, Story):
            raise PlacementError("Stories cannot have child nodes")
        if isinstance(parent, SubEpic) and isinstance(child, Epic):
            raise PlacementError("An Epic cannot live under a SubEpic")
        if isinstance(parent, Story) and isinstance(child, SubEpic):
            raise PlacementError("A SubEpic cannot live under a Story")
        if child is None or parent is None:
            raise PlacementError("Both child and parent are required")
        if isinstance(child, Epic) and parent is not None and not isinstance(
            parent, StoryMap
        ):
            raise PlacementError("An Epic can only sit under the Story Map itself")

    def _depth_from(self, sub_epic: SubEpic, current: int) -> int:
        if not sub_epic.sub_epics:
            return current
        return max(self._depth_from(s, current + 1) for s in sub_epic.sub_epics)

    def _find_sub_epic_x(
        self, target: SubEpic, base_x: int, siblings: List[SubEpic]
    ) -> Optional[int]:
        offset = base_x
        for sibling in siblings:
            if sibling is target:
                return offset
            inner = self._find_sub_epic_x(target, offset, sibling.sub_epics)
            if inner is not None:
                return inner
            offset += self.sub_epic_width(sibling)
        return None

    def _depth_of(
        self, target: SubEpic, siblings: List[SubEpic], current: int
    ) -> Optional[int]:
        for sibling in siblings:
            if sibling is target:
                return current
            inner = self._depth_of(target, sibling.sub_epics, current + 1)
            if inner is not None:
                return inner
        return None

    def _all_sub_epics_recursive(
        self, siblings: Iterable[SubEpic]
    ) -> Iterable[SubEpic]:
        for sibling in siblings:
            yield sibling
            yield from self._all_sub_epics_recursive(sibling.sub_epics)

    def _parent_sub_epic_of_story(self, story: Story) -> SubEpic:
        for epic in self._story_map.epics:
            for sub in self._all_sub_epics_recursive(epic.sub_epics):
                if story in sub.stories:
                    return sub
        raise KeyError(f"Story {story.name!r} not part of this diagram")
