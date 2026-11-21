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
from typing import Dict, List

from harness.whiteboard import BoardElement, Box, Whiteboard, WhiteboardNode

from cdd_guidance.practices.stories.model.diagram_story_model import (
    DiagramEpic,
    DiagramIncrement,
    DiagramStory,
    DiagramStoryCell,
    DiagramStoryModel,
    LaidOutEpic,
    LaidOutStory,
)
from cdd_guidance.practices.stories.model.story_model import Epic, Increment, Story, StoryModel

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


class WhiteboardStory(LaidOutStory, _BoardStoryNode):
    """A story card on the story line under its epic: its actor in italics on the first line, then its name. A board
    grows a block too small for its words over its neighbours, so the card is sized for a story name of three lines
    at the board's small text, and cards stand the board's 24 units apart."""

    size = 152
    card_width = size
    """A story card is square, as drawio draws it, and big enough for its actor and a name of three lines."""
    pitch = card_width + 24
    column_pad = 12
    row_y = 280
    actor_height = 0
    actor_gap = 0

    def board_box(self) -> Box:
        return Box(self.x, self.y, self.card_width, self.size)

    @property
    def card_text(self) -> str:
        """The card's words: its actor in italics on the first line, when it has one, then its name."""
        actor = self.actors[0].strip() if self.actors else ""
        return f"*{actor}*\n{self.name}" if actor else self.name

    def board_elements(self) -> List[BoardElement]:
        return [self.board_shape(f"story.{self.story_type.value}.{self.board_key}", kind="rounded", color="yellow", size="small", text=self.card_text)]

    def lane_card(self, lane_key: str, left: float, top: float) -> BoardElement:
        """This story's card in a thin-slice lane: keyed by the lane too, since the board holds the lanes beside the map."""
        key = hashlib.sha1(f"{lane_key}/{self.board_key}".encode("utf-8")).hexdigest()[:KEY_LENGTH]
        return BoardElement.shape(f"story.{self.story_type.value}.{key}", Box(left, top, self.card_width, self.size),
                                  kind="rounded", color="yellow", size="small", text=self.card_text)


class WhiteboardEpic(LaidOutEpic, _BoardStoryNode):
    """An epic bar; a sub-epic's bar sits one row lower for each level it is nested, under the epic that holds it."""

    tighten = 0
    bar_gap = 8
    """The space left between two bars side by side, so each sub-epic reads as its own."""
    first_x = DiagramEpic.left_margin
    epic_spacing = DiagramEpic.gap
    story_pitch = WhiteboardStory.pitch

    def board_box(self) -> Box:
        return Box(self.x, self.y, self.width - self.bar_gap, self.height)

    def board_elements(self) -> List[BoardElement]:
        drawn: List[BoardElement] = [self.bar()]
        for story in self.stories:
            drawn.extend(story.board_elements())
        for child in self.epics:
            drawn.extend(child.board_elements())
        return drawn

    def bar(self) -> BoardElement:
        """This epic's bar, or a sub-epic's, over the stories it holds."""
        nested = isinstance(self.parent, Epic)
        element_id = f"subepic.{self.depth}.{self.board_key}" if nested else f"epic.{self.board_key}"
        return self.board_shape(element_id, kind="rounded", color="green" if nested else "purple", size="body", text=self.name)


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

    def take_board(self, board: Whiteboard) -> "WhiteboardStoryModel":
        """The story map board draws, read by where its elements sit."""
        cells = [cell for cell in (_BoardCell(element) for element in board.holding({"epic"}, "story-map epic").shapes) if cell.role]
        story_map = WhiteboardStoryModel()
        story_map.place_cells(cells)
        return story_map

    def save_thin_slice(self) -> str:
        """This map's increments as a board, laid out as drawio lays out its thin slice: one column per sub-epic under
        the epic and sub-epic bars, each column as wide as the most stories any one increment puts in it, and one lane
        per increment stacked below each other, each a single row of its stories under the sub-epic that holds each."""
        return _ThinSliceBoard(self, Whiteboard("Thin Slice")).board().save()

    def load_thin_slice(self, text: str) -> "WhiteboardStoryModel":
        """Read a thin-slice board into this map's increments, top lane first, each delivering the map's own stories
        its lane holds, row by row, and return this map."""
        board = Whiteboard.from_text(text)
        lanes = sorted((element for element in board.sections if element.role == "lane"), key=lambda lane: lane.box.y)
        cards = [element for element in board.shapes if element.role == "story"]
        labels = [element for element in board.shapes if element.role == "increment"]
        increments = []
        for lane in lanes:
            held = sorted((card for card in cards if lane.holds(card)), key=lambda card: (card.box.y, card.box.x))
            names = [_BoardCell(card).text for card in held]
            label = next((found for found in labels if lane.holds(found)), None)
            name = label.text.strip() if label is not None else lane.text.strip()
            increments.append(self.increment_type(name, len(increments) + 1, self.descendants.stories_named(names)))
        self.increments.refill(increments)
        return self


class _ThinSliceBoard:
    """A story map's thin slice drawn as board elements, in the layout the diagram model gives every format."""

    LANE_INSET = 24
    LANE_GAP = 24
    LABEL_WIDTH = 200
    """The increment's name sits in a label at the left of its lane, as drawio draws it, and the columns start after it."""

    def __init__(self, story_map: WhiteboardStoryModel, drawing: Whiteboard) -> None:
        self.story_map = story_map
        self.drawing = drawing
        self.left = WhiteboardEpic.first_x + self.LABEL_WIDTH + self.LANE_GAP
        self.columns = story_map.thin_slice_columns()
        self.lanes = story_map.thin_slice_lanes(self.columns)
        self.widths = story_map.thin_slice_widths(self.lanes, WhiteboardStory.pitch, WhiteboardStory.column_pad)

    def board(self) -> Whiteboard:
        board = self.drawing
        left = self.left
        for index, (epic, sub) in enumerate(self.columns):
            if index == 0 or self.columns[index - 1][0] is not epic:
                span = sum(width for (top, _), width in zip(self.columns, self.widths) if top is epic)
                board.add(BoardElement.shape(f"epic.{epic.board_key}", Box(left, DiagramEpic.row_y, span - WhiteboardEpic.bar_gap, DiagramEpic.bar_height),
                                             kind="rounded", color="purple", size="body", text=epic.name))
            if sub is not epic:
                board.add(BoardElement.shape(f"subepic.{sub.depth}.{sub.board_key}", Box(left, DiagramEpic.nested_row_y, self.widths[index] - WhiteboardEpic.bar_gap, DiagramEpic.bar_height),
                                             kind="rounded", color="green", size="body", text=sub.name))
            left += self.widths[index]
        top = DiagramEpic.nested_row_y + DiagramEpic.bar_height + self.LANE_GAP
        for increment, held in self.lanes:
            top = self._draw_lane(increment, held, top)
        return board

    def _draw_lane(self, increment: "Increment", held: Dict[int, List[Story]], top: float) -> float:
        board = self.drawing
        lane_key = hashlib.sha1(f"lane:{increment.name}".encode("utf-8")).hexdigest()[:KEY_LENGTH]
        height = WhiteboardStory.size + 2 * self.LANE_INSET
        board.add(BoardElement.section(f"lane.{lane_key}", Box(WhiteboardEpic.first_x, top, self.left - WhiteboardEpic.first_x + sum(self.widths), height), color="white"))
        board.add(BoardElement.shape(f"increment.{lane_key}", Box(WhiteboardEpic.first_x + self.LANE_INSET, top + self.LANE_INSET, self.LABEL_WIDTH - self.LANE_INSET, WhiteboardStory.size),
                                     kind="rounded", color="white", size="body", text=increment.name))
        for column, stories in held.items():
            column_left = self.left + sum(self.widths[:column]) + WhiteboardStory.column_pad
            for place, story in enumerate(self._map_story(story) for story in stories):
                if isinstance(story, WhiteboardStory):
                    board.add(story.lane_card(lane_key, column_left + place * WhiteboardStory.pitch, top + self.LANE_INSET))
        return top + height + self.LANE_GAP

    def _map_story(self, story: Story) -> Story:
        """The map's own whiteboard story of this name, which carries the card's actor and size."""
        return next((held for held in self.story_map.descendants.stories() if held.name == story.name), story)


class _BoardCell(DiagramStoryCell):
    """A board shape as a story-map cell: its role, bar depth and story kind from its id, its text, and its box. A
    shape no story map draws has no role."""

    ROLES = ("epic", "subepic", "story", "actor")

    def __init__(self, element: BoardElement) -> None:
        super().__init__()
        parts = element.id.split(".")
        if element.role not in self.ROLES:
            return
        self.role = element.role
        self.depth = int(parts[1]) if self.role == "subepic" else -1
        self.kind = parts[1] if self.role == "story" else ""
        lines = [line.strip() for line in element.text.strip().splitlines() if line.strip()]
        actor = re.match(r"^\*([^*].*)\*$", lines[0]) if self.role == "story" and len(lines) > 1 else None
        self.actor = actor.group(1).strip() if actor else ""
        self.text = " ".join(lines[1:] if actor else lines)
        self.x, self.y, self.width, self.height = element.box.x, element.box.y, element.box.w, element.box.h
