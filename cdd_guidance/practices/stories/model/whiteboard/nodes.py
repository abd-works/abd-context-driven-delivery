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
import re
from typing import List

from harness.whiteboard import BoardElement, Box, Section, Shape, UnreadableBoard, Whiteboard, WhiteboardNode

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
    """A story card on the story line under its epic: its actor in italics on the first line, then its name. A board
    grows a block too small for its words over its neighbours, so the card is sized for a story name of three lines
    at the board's small text, and cards stand the board's 24 units apart."""

    card_width = 160
    size = 112
    pitch = card_width + 24
    column_pad = 12
    row_y = 280
    actor_height = 0
    actor_gap = 0

    @property
    def x(self) -> int:
        parent = self.parent
        if not isinstance(parent, Epic):
            return 0
        return parent.x + self.column_pad + parent.stories.index(self) * self.pitch

    @property
    def y(self) -> int:
        return self._story_line_y()

    def board_box(self) -> Box:
        return Box(self.x, self.y, self.card_width, self.size)

    @property
    def card_text(self) -> str:
        """The card's words: its actor in italics on the first line, when it has one, then its name."""
        actor = self.actors[0].strip() if self.actors else ""
        return f"*{actor}*\n{self.name}" if actor else self.name

    def board_elements(self) -> List[BoardElement]:
        return [self.board_shape(f"story.{self.story_type.value}.{self.board_key}", kind="rounded", color="yellow", size="small", text=self.card_text)]

    def lane_card(self, lane_key: str, left: float, top: float) -> Shape:
        """This story's card in a thin-slice lane: keyed by the lane too, since the board holds the lanes beside the map."""
        key = hashlib.sha1(f"{lane_key}/{self.board_key}".encode("utf-8")).hexdigest()[:KEY_LENGTH]
        return Shape(f"story.{self.story_type.value}.{key}", box=Box(left, top, self.card_width, self.size),
                     kind="rounded", color="yellow", size="small", text=self.card_text)


class WhiteboardEpic(DiagramEpic, _BoardStoryNode):
    """An epic bar; a sub-epic's bar sits one row lower for each level it is nested, under the epic that holds it."""

    tighten = 0
    bar_gap = 8
    """The space left between two bars side by side, so each sub-epic reads as its own."""
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
        return Box(self.x, self.y, self.width - self.bar_gap, self.height)

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
        cells = [cell for cell in (_BoardCell(element) for element in board.whole_elements) if cell.role]
        if not any(cell.role == "epic" for cell in cells):
            raise UnreadableBoard("The board holds no story-map epic")
        story_map = WhiteboardStoryModel()
        story_map.place_cells(cells)
        return story_map

    def save_thin_slice(self) -> str:
        """This map's increments as a board: one lane per increment, the lanes stacked below each other, each holding
        its stories in story-map order, wrapped into rows of ``_ThinSliceBoard.CARDS_PER_ROW``. A board shows a whole
        map at a glance only when it is small, so a lane is as wide as one row of cards, not as the whole map."""
        return _ThinSliceBoard(self).board().save()

    def load_thin_slice(self, text: str) -> "WhiteboardStoryModel":
        """Read a thin-slice board into this map's increments, top lane first, each delivering the map's own stories
        its lane holds, row by row, and return this map."""
        board = Whiteboard.from_text(text)
        lanes = sorted((element for element in board.whole_elements if isinstance(element, Section) and element.role == "lane"),
                       key=lambda lane: lane.box.y)
        cards = [element for element in board.whole_elements if isinstance(element, Shape) and element.role == "story"]
        increments = []
        for lane in lanes:
            held = sorted((card for card in cards if lane.holds(card)), key=lambda card: (card.box.y, card.box.x))
            names = [_BoardCell(card).text for card in held]
            increments.append(self.increment_type(lane.text.strip(), len(increments) + 1, self.stories_named(names)))
        self.increments.refill(increments)
        return self


class _ThinSliceBoard:
    """A story map's increments drawn as lanes stacked below each other, each a grid of its stories in map order."""

    CARDS_PER_ROW = 12
    LANE_TITLE_ROOM = 52
    LANE_INSET = 24
    LANE_GAP = 24

    def __init__(self, story_map: WhiteboardStoryModel) -> None:
        self.story_map = story_map
        order = {story.name: index for index, story in enumerate(story_map.every_story())}
        self.lanes = [
            (increment, sorted((self._map_story(story) for story in increment.stories), key=lambda story: order.get(story.name, len(order))))
            for increment in story_map.increments
        ]
        self.width = self.CARDS_PER_ROW * WhiteboardStory.pitch - WhiteboardStory.pitch + WhiteboardStory.card_width + 2 * self.LANE_INSET

    def board(self) -> Whiteboard:
        board = Whiteboard("Thin Slice")
        top = DiagramEpic.row_y
        for increment, stories in self.lanes:
            top = self._draw_lane(board, increment, stories, top)
        return board

    def _draw_lane(self, board: Whiteboard, increment, stories, top: float) -> float:
        lane_key = hashlib.sha1(f"lane:{increment.name}".encode("utf-8")).hexdigest()[:KEY_LENGTH]
        rows = max(1, -(-len(stories) // self.CARDS_PER_ROW))
        height = rows * (WhiteboardStory.size + self.LANE_GAP) - self.LANE_GAP + 2 * self.LANE_INSET
        board.add(Section(f"lane.{lane_key}", box=Box(WhiteboardEpic.first_x, top, self.width, height), color="white", text=increment.name))
        for place, story in enumerate(stories):
            row, column = divmod(place, self.CARDS_PER_ROW)
            left = WhiteboardEpic.first_x + self.LANE_INSET + column * WhiteboardStory.pitch
            board.add(story.lane_card(lane_key, left, top + self.LANE_INSET + row * (WhiteboardStory.size + self.LANE_GAP)))
        return top + height + self.LANE_GAP + self.LANE_TITLE_ROOM

    def _map_story(self, story):
        """The map's own whiteboard story of this name, which carries the card's actor and size."""
        return next((held for held in self.story_map.every_story() if held.name == story.name), story)


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
        lines = [line.strip() for line in element.text.strip().splitlines() if line.strip()]
        actor = re.match(r"^\*([^*].*)\*$", lines[0]) if self.role == "story" and len(lines) > 1 else None
        self.actor = actor.group(1).strip() if actor else ""
        self.text = " ".join(lines[1:] if actor else lines)
        self.x, self.y, self.width, self.height = element.box.x, element.box.y, element.box.w, element.box.h
