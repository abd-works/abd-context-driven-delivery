"""Diagram epic and story. A nested epic is an epic whose parent is an epic."""

from __future__ import annotations

from typing import Optional

from practices.stories.model.story_model import Epic, Increment, Story, StoryMap, StoryType


class DiagramStoryNode:
    """Placement shared by a diagram epic, story, and increment."""

    def _owning_map(self) -> Optional[StoryMap]:
        node = self.parent
        while node is not None and not isinstance(node, StoryMap):
            node = node.parent
        return node

    @property
    def width(self) -> int:
        if isinstance(self, Story):
            return self.pitch
        if not isinstance(self, Epic):
            return 0
        if isinstance(self.parent, Epic):
            return DiagramStoryMap.base_width * max(self.diagram_span_columns(), 1)
        return DiagramStoryMap.base_width * self.span_columns()

    @property
    def height(self) -> int:
        if isinstance(self, Story):
            return self.size
        if isinstance(self, Epic):
            return DiagramStoryMap.row_height
        return 0

    @property
    def y(self) -> int:
        if isinstance(self, Story):
            story_map = self._owning_map()
            if story_map is None:
                return 0
            return story_map.actor_y + DiagramStoryMap.row_height
        if isinstance(self, Epic) and isinstance(self.parent, Epic):
            return (self.depth + 1) * DiagramStoryMap.row_height
        return 0

    @property
    def x(self) -> int:
        parent = self.parent
        if isinstance(self, Story):
            return parent.x if isinstance(parent, Epic) else 0
        if isinstance(parent, Epic):
            origin = parent.x
            siblings = parent.epics
        elif isinstance(parent, StoryMap):
            origin = 0
            siblings = parent.epics
        else:
            return 0
        offset = origin
        for sibling in siblings:
            if sibling is self:
                return offset
            offset += sibling.width
        return offset

    def place(self, side: str, destination: "DiagramStoryNode") -> None:
        self._place_side = side
        self._place_destination = destination

    def add(self, child: "DiagramStoryNode") -> None:
        children = self._placed_children()
        previous = children[-1] if children else None
        if isinstance(child, Epic):
            self.append_epic(child)
        elif isinstance(child, Story):
            self.append_story(child)
        child.place("below", self)
        if previous is not None:
            child.place("after", previous)
        self.stretch()

    def stretch(self) -> None:
        parent = getattr(self, "parent", None)
        if isinstance(parent, DiagramStoryNode):
            parent.stretch()

    def role(self) -> str:
        if isinstance(self, Story):
            story_type = getattr(self, "story_type", StoryType.USER)
            value = getattr(story_type, "value", story_type)
            return f"story:{value}"
        if isinstance(self, Epic):
            if isinstance(self.parent, Epic):
                return f"subepic:{self.depth}"
            return "epic"
        return ""

    def _placed_children(self) -> list:
        children = []
        children.extend(getattr(self, "epics", []))
        children.extend(getattr(self, "stories", []))
        return children


class DiagramEpic(Epic, DiagramStoryNode):
    row_y = 120
    nested_row_y = 195
    bar_height = 60
    content_inset = 10
    gap = 10
    left_margin = 20
    depth_gap = 8
    tighten = 5
    fill = "#e1d5e7"
    nested_fill = "#d5e8d4"
    stroke = "#9673a6"
    nested_stroke = "#82b366"


class DiagramStory(Story, DiagramStoryNode):
    pitch = 60
    size = 50
    row_y = 345
    actor_height = size
    actor_gap = 4
    pad_below_sub_epic = 16
    fill = "#fff2cc"
    stroke = "#d6b656"
    actor_fill = "#dae8fc"
    actor_stroke = "#6c8ebf"


class DiagramIncrement(Increment, DiagramStoryNode):
    label_width = 160
    lane_height = 70
    lane_gap = 5
    fill = "#f5f5f5"
    stroke = "#666666"


class DiagramStoryMap(StoryMap):
    """Story map whose epics and stories are the diagram types."""

    base_width = 200
    row_height = 100
    epic_type = DiagramEpic
    story_type = DiagramStory

    @property
    def max_sub_epic_depth(self) -> int:
        deepest = 0
        for epic in self.epics:
            deepest = max(deepest, epic.tree_depth())
        return deepest

    @property
    def actor_y(self) -> int:
        return (self.max_sub_epic_depth + 2) * self.row_height
