"""Claude Whiteboard story nodes: the diagram epic and story drawn as board elements, and the story map that saves them
as a ``.whiteboard`` file and reads one back.

A whiteboard reads at a zoom like a Miro board's, so its cards and columns are the Miro sizes. Each element's id names
the node it draws (``epic.<key>``, ``subepic.<depth>.<key>``, ``story.<kind>.<key>``, ``actor.<key>``), where the key is
a hash of the node's path, so the same node keeps its id from one render to the next. A board is read back by where
its elements sit, as a drawio map is (``DiagramStoryModel.place_cells``), because people move and restack elements on
a shared board.
"""

from __future__ import annotations

import hashlib
from typing import List

from harness.whiteboard import BoardElement, Box, Shape, UnreadableBoard, Whiteboard, WhiteboardNode

from cdd_guidance.practices.stories.model.diagram_story_model import (
    DiagramEpic,
    DiagramIncrement,
    DiagramStory,
    DiagramStoryCell,
    DiagramStoryModel,
)
from cdd_guidance.practices.stories.model.story_model import Epic, StoryModel

KEY_LENGTH = 10
"""Hex digits of a node's path hash in its element id: enough that two nodes of one map never share one."""


class _BoardStoryNode(WhiteboardNode):
    """A story-map node drawn on a board, keyed by its path from the map's root."""

    @property
    def board_key(self) -> str:
        names: List[str] = []
        node = self
        while node is not None and not isinstance(node, StoryModel):
            names.append(f"{'epic' if isinstance(node, Epic) else 'story'}:{node.name}")
            node = node.parent
        return hashlib.sha1("/".join(reversed(names)).encode("utf-8")).hexdigest()[:KEY_LENGTH]


class WhiteboardStory(DiagramStory, _BoardStoryNode):
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

    def board_box(self) -> Box:
        return Box(self.x, self.y, self.size, self.size)

    def board_elements(self) -> List[BoardElement]:
        drawn: List[BoardElement] = []
        actor = self.actors[0].strip() if self.actors else ""
        if actor:
            drawn.append(Shape(
                f"actor.{self.board_key}", box=Box(self.x, self.y - self.actor_height - self.actor_gap, self.size, self.actor_height),
                kind="rect", color="blue", size="small", text=actor,
            ))
        drawn.append(self.board_shape(f"story.{self.story_type.value}.{self.board_key}", kind="rect", color="yellow", size="small", text=self.name))
        return drawn


class WhiteboardEpic(DiagramEpic, _BoardStoryNode):
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

    def board_box(self) -> Box:
        return Box(self.x, self.y, self.width, self.height)

    def board_elements(self) -> List[BoardElement]:
        nested = isinstance(self.parent, Epic)
        element_id = f"subepic.{self.depth}.{self.board_key}" if nested else f"epic.{self.board_key}"
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
    increment_type = DiagramIncrement

    def render(self, canonical: StoryModel | None = None, previous: str | None = None) -> str:
        """Draw canonical, or this map, as a board; the elements a previous board held stay where people put them."""
        board = self.copy_of(canonical if canonical is not None else self).board()
        if previous:
            board.keep_places(Whiteboard.from_text(previous))
        return board.save()

    def board(self) -> Whiteboard:
        board = Whiteboard("Story Map")
        for epic in self.epics:
            board.draw(epic)
        return board

    def save(self) -> str:
        return self.board().save()

    def parse(self, text: str) -> "WhiteboardStoryModel":
        """The format-adapter entry point Stories renders through: the story map a board's text holds."""
        return self.take_board(Whiteboard.from_text(text))

    def load(self, text: str) -> "WhiteboardStoryModel":
        """The story map a saved board holds, as every story-map format loads its file."""
        return self.take_board(Whiteboard.from_text(text))

    def take_board(self, board: Whiteboard) -> "WhiteboardStoryModel":
        """The story map board draws, read by where its elements sit."""
        cells = [cell for cell in (_BoardCell(element) for element in board.elements) if cell.role]
        if not any(cell.role == "epic" for cell in cells):
            raise UnreadableBoard("The board holds no story-map epic")
        story_map = WhiteboardStoryModel()
        story_map.place_cells(cells)
        return story_map


class _BoardCell(DiagramStoryCell):
    """A board element as a story-map cell: its role, bar depth and story kind from its id, its text, and its box. An
    element no story map draws, such as a note a person added, has no role."""

    ROLES = ("epic", "subepic", "story", "actor")

    def __init__(self, element: BoardElement) -> None:
        super().__init__()
        parts = element.id.split(".")
        if not isinstance(element, Shape) or element.role not in self.ROLES:
            return
        self.role = element.role
        self.depth = int(parts[1]) if self.role == "subepic" else -1
        self.kind = parts[1] if self.role == "story" else ""
        self.text = element.text.strip()
        self.x, self.y, self.width, self.height = element.box.x, element.box.y, element.box.w, element.box.h
