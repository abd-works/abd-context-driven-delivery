"""Claude Whiteboard story nodes: the diagram epic, story and increment drawn as board elements, and the story map that
saves them as a ``.whiteboard`` file and reads one back.

A whiteboard reads at a zoom like a Miro board's, so its cards and columns are the Miro sizes. Each element's id names
the node it draws (``epic.<key>``, ``subepic.<depth>.<key>``, ``story.<kind>.<key>``, ``actor.<key>``), where the key is
a hash of the node's path, so the same node keeps its id from one render to the next. A board is read back by where
its elements sit, as a drawio map is, because people move and restack elements on a shared board.
"""

from __future__ import annotations

import hashlib
from typing import List, Optional

from harness.whiteboard import BoardElement, Shape, UnreadableBoard, Whiteboard, WhiteboardNode

from cdd_guidance.practices.stories.model.diagram_story_model import (
    DiagramEpic,
    DiagramIncrement,
    DiagramStory,
    DiagramStoryModel,
)
from cdd_guidance.practices.stories.model.story_model import Epic, StoryModel, StoryType


def _key(node) -> str:
    """A short key of the node's path from the map's root, the same on every render of the same map."""
    names: List[str] = []
    while node is not None and not isinstance(node, StoryModel):
        names.append(f"{'epic' if isinstance(node, Epic) else 'story'}:{node.name}")
        node = node.parent
    return hashlib.sha1("/".join(reversed(names)).encode("utf-8")).hexdigest()[:10]


class WhiteboardIncrement(DiagramIncrement):
    pass


class WhiteboardStory(DiagramStory, WhiteboardNode):
    """A story card on the story line under its epic, with its actor drawn above it. Every story's actor is drawn, even
    one the story before it shares, because a board element carries no field of a practice's own to hold it."""

    pitch = 72
    size = 60
    actor_height = size
    column_pad = 5

    @property
    def x(self) -> int:
        parent = self.parent
        if not isinstance(parent, Epic):
            return 0
        return parent.x + WhiteboardEpic.tighten + self.column_pad + parent.stories.index(self) * self.pitch

    @property
    def y(self) -> int:
        return self._story_line_y()

    def board_box(self):
        return (self.x, self.y, self.size, self.size)

    def board_elements(self) -> List[BoardElement]:
        key = _key(self)
        drawn: List[BoardElement] = []
        actor = self._actor
        if actor:
            drawn.append(Shape(
                f"actor.{key}", x=self.x, y=self.y - self.actor_height - self.actor_gap, w=self.size,
                h=self.actor_height, kind="rect", color="blue", size="small", text=actor,
            ))
        drawn.append(self.board_shape(f"story.{self.story_type.value}.{key}", kind="rect", color="yellow", size="small", text=self.name))
        return drawn

    @property
    def _actor(self) -> str:
        return self.actors[0].strip() if self.actors else ""


class WhiteboardEpic(DiagramEpic, WhiteboardNode):
    """An epic bar; a sub-epic's bar sits one row lower for each level it is nested, under the epic that holds it."""

    tighten = 10
    first_x = DiagramEpic.left_margin
    epic_spacing = DiagramEpic.gap
    story_pitch = WhiteboardStory.pitch

    @property
    def width(self) -> int:
        if isinstance(self.parent, Epic):
            return max(self.diagram_span_columns(), 1) * WhiteboardStory.pitch
        return self.span_columns() * WhiteboardStory.pitch

    @property
    def height(self) -> int:
        return self.bar_height

    @property
    def y(self) -> int:
        if isinstance(self.parent, Epic):
            return self._sub_epic_bar_y(self.depth)
        return self.row_y

    def board_box(self):
        return (self.x, self.y, self.width, self.height)

    def board_elements(self) -> List[BoardElement]:
        nested = isinstance(self.parent, Epic)
        element_id = f"subepic.{self.depth}.{_key(self)}" if nested else f"epic.{_key(self)}"
        drawn: List[BoardElement] = [self.board_shape(
            element_id, kind="rounded", color="green" if nested else "purple", size="body", text=self.name,
        )]
        for story in self.stories:
            drawn.extend(story.board_elements())
        for child in self.epics:
            drawn.extend(child.board_elements())
        return drawn


class WhiteboardStoryModel(DiagramStoryModel):
    """Whiteboard story-map I/O. IS the format-typed tree root: render draws it on a board, parse reads one back."""

    suffixes = (Whiteboard.SUFFIX,)
    epic_type = WhiteboardEpic
    story_type = WhiteboardStory
    increment_type = WhiteboardIncrement

    def render(self, canonical: StoryModel | None = None, previous: str | None = None) -> str:
        """Draw canonical, or this map, as a board; the elements a previous board held stay where people put them."""
        board = self.copy_of(canonical if canonical is not None else self).board()
        if previous:
            board.keep_places(Whiteboard.load(previous))
        return board.save()

    def board(self) -> Whiteboard:
        board = Whiteboard("Story Map")
        for epic in self.epics:
            board.draw(epic)
        return board

    def save(self) -> str:
        return self.board().save()

    def parse(self, text: str) -> "WhiteboardStoryModel":
        """The format-adapter entry point Stories renders through; the same as load."""
        return self.load(text)

    def load(self, text: str) -> "WhiteboardStoryModel":
        """Read the story map by where its elements sit, not their order on the board: epics left to right, each
        sub-epic under the shallower bar above it, each story under the deepest bar over it, and the actor just above a
        story as that story's actor."""
        placed = [_Placed(element) for element in Whiteboard.load(text).elements if _Placed.draws(element)]
        if not any(cell.role == "epic" for cell in placed):
            raise UnreadableBoard("The board holds no story-map epic")
        story_map = WhiteboardStoryModel()
        owners = self._place_epics(story_map, placed)
        self._place_stories(placed, owners)
        return story_map

    def _place_epics(self, story_map: "WhiteboardStoryModel", placed: List["_Placed"]) -> List["_Placed"]:
        owners: List[_Placed] = []
        for cell in sorted((c for c in placed if c.role == "epic"), key=lambda c: c.x):
            cell.node = WhiteboardEpic(cell.text, len(story_map.epics) + 1)
            story_map.append_epic(cell.node)
            owners.append(cell)
        for cell in sorted((c for c in placed if c.role == "subepic"), key=lambda c: (c.depth, c.x)):
            owner = _Placed.beneath(cell.center, [o for o in owners if o.depth < cell.depth])
            if owner is None:
                continue
            cell.node = WhiteboardEpic(cell.text, len(owner.node.epics) + 1)
            owner.node.append_epic(cell.node)
            owners.append(cell)
        return owners

    def _place_stories(self, placed: List["_Placed"], owners: List["_Placed"]) -> None:
        stories = sorted((c for c in placed if c.role == "story"), key=lambda c: (c.x, c.y))
        actor_of = {}
        for actor in (c for c in placed if c.role == "actor"):
            below = actor.story_below(stories)
            if below is not None:
                actor_of[id(below)] = actor.text
        for cell in stories:
            owner = _Placed.beneath(cell.center, owners)
            if owner is None:
                continue
            story = WhiteboardStory(cell.text, len(owner.node.stories) + 1, cell.story_type)
            if id(cell) in actor_of:
                story.actors = [actor_of[id(cell)]]
            owner.node.append_story(story)


class _Placed:
    """One story-map element as it sits on the board: its role and depth from its id, its text, and its box."""

    ROLES = ("epic", "subepic", "story", "actor")

    def __init__(self, element: Shape) -> None:
        parts = element.id.split(".")
        self.role = parts[0]
        self.depth = int(parts[1]) if self.role == "subepic" else -1
        self.kind = parts[1] if self.role == "story" else ""
        self.text = element.text.strip()
        self.x, self.y, self.width, self.height = element.place
        self.node: Optional[Epic] = None

    @classmethod
    def draws(cls, element: BoardElement) -> bool:
        return isinstance(element, Shape) and element.id.split(".")[0] in cls.ROLES

    @property
    def center(self) -> float:
        return self.x + self.width / 2

    @property
    def story_type(self) -> StoryType:
        return StoryType.from_mark(self.kind or None)

    def spans(self, x: float) -> bool:
        return self.x <= x < self.x + self.width

    def story_below(self, stories: List["_Placed"]) -> Optional["_Placed"]:
        column = [story for story in stories if story.spans(self.center) and story.y > self.y]
        return min(column, key=lambda story: story.y, default=None)

    @staticmethod
    def beneath(x: float, bars: List["_Placed"]) -> Optional["_Placed"]:
        spanning = [bar for bar in bars if bar.spans(x)]
        if spanning:
            return max(spanning, key=lambda bar: bar.depth)
        return min(bars, key=lambda bar: abs(bar.center - x), default=None)
