"""Claude Whiteboard story nodes: the diagram epic and story drawn as board elements, and the story map that saves them
as a ``.whiteboard`` file and reads one back.

A whiteboard reads at a zoom like a Miro board's, so its cards and columns are the Miro sizes. Each element's id names
the node it draws (``epic.<key>``, ``subepic.<depth>.<key>``, ``story.<kind>.<key>``, ``actor.<key>``), where the key is
a hash of the node's path, so the same node keeps its id from one render to the next. A board is read back by where
its elements sit, as a drawio map is (``DiagramStoryMap.place_cells``), because people move and restack elements on
a shared board.
"""

from __future__ import annotations

import re
from typing import Dict, List, Optional

from harness.whiteboard import BoardElement, Box, ElementId, KeepsDocumentOnBoard, Section, Shape, Whiteboard, WhiteboardNode

from cdd_guidance.practices.stories.model.diagram_story_map import (
    DiagramEpic,
    DiagramIncrement,
    DiagramStory,
    DiagramStoryCell,
    DiagramStoryMap,
    LaidOutEpic,
    LaidOutStory,
    ThinSliceColumn,
    ThinSliceLane,
    ThinSliceLayout,
    ThinSliceSurface,
)
from cdd_guidance.practices.stories.model.story_map import Epic, Increment, Story, StoryMap
from harness.catalog_generator.git_citation import GitCitation
from harness.guidance.practice_formats import Written
from cdd_guidance.practices.stories.model.markdown.links import StoryMapLinks, unlink

class _BoardStoryNode(WhiteboardNode):
    """A story-map node drawn on a board, keyed by its path from the map's root."""

    @property
    def path_names(self) -> List[str]:
        """The node's names from the map's root down to it, each with the kind of node it names."""
        names: List[str] = []
        node = self
        while node is not None and not isinstance(node, StoryMap):
            names.append(f"{'epic' if isinstance(node, Epic) else 'story'}:{node.name}")
            node = node.parent
        return list(reversed(names))

    def element_id(self, role: str, *parts: str) -> ElementId:
        """This node's element id as role, then parts, then the key its path hashes to."""
        return ElementId.of(role, *self.path_names, length=self.KEY_LENGTH, parts=parts)


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
    file_link = ""
    """Where the board opens the story's own file, its scenarios or else its acceptance test: the web address its
    checkout's origin shows it at, since a board opens no other link; empty when the story has no file or none is known."""

    def board_box(self) -> Box:
        return Box(self.x, self.y, self.card_width, self.size)

    @property
    def card_text(self) -> str:
        """The card's words: its actor in italics on the first line, when it has one, then its name, linked to its own
        file when it has one."""
        actor = self.actors[0].strip() if self.actors else ""
        name = f"[{self.name}]({self.file_link})" if self.file_link else self.name
        return f"*{actor}*\n{name}" if actor else name

    def take_file_link(self, links: StoryMapLinks, citation: GitCitation) -> None:
        """Link the story's name to its own file, where citation's checkout shows it, when links find one."""
        path = links.story_path(self)
        self.file_link = citation.blob_url(path) if path is not None else ""

    def board_elements(self) -> List[BoardElement]:
        return [self.board_shape(self.element_id("story", self.story_type.value), kind="rounded", color="yellow", size="small", text=self.card_text)]

    def lane_card(self, lane: ElementId, left: float, top: float) -> BoardElement:
        """This story's card in a thin-slice lane: keyed by the lane too, since the board holds the lanes beside the map."""
        card = ElementId.of("story", lane.key, self.element_id("story").key, length=self.KEY_LENGTH, parts=(self.story_type.value,))
        return Shape(card, box=Box(left, top, self.card_width, self.size), kind="rounded", color="yellow", size="small", text=self.card_text)


class WhiteboardEpic(LaidOutEpic, _BoardStoryNode):
    """An epic bar; a sub-epic's bar sits one row lower for each level it is nested, under the epic that holds it."""

    story_class = WhiteboardStory

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
        element_id = self.element_id("subepic", str(self.depth)) if nested else self.element_id("epic")
        return self.board_shape(element_id, kind="rounded", color="green" if nested else "purple", size="body", text=self.name)


class WhiteboardStoryMap(KeepsDocumentOnBoard, DiagramStoryMap):
    """Whiteboard story-map I/O. IS the format-typed tree root: render draws it on a board, parse reads one back."""

    suffixes = (Whiteboard.SUFFIX,)
    epic_class = WhiteboardEpic
    increment_class = DiagramIncrement

    def render(self, canonical: StoryMap, written: Written = Written()) -> str:
        """Draw canonical as a board; the elements a previous board held stay where people put them. Written in a
        folder of a checkout with an origin, each story's name links to its own file there."""
        drawn = self.copy_of(canonical)
        citation = GitCitation.from_branch(written.folder) if written.folder is not None else None
        if citation is not None:
            links = StoryMapLinks(drawn, str(written.folder))
            for story in drawn.descendants.stories():
                story.take_file_link(links, citation)
        return drawn.board().drawn_over(str(written.previous))

    def board(self) -> Whiteboard:
        board = Whiteboard()
        for epic in self.epics:
            board.draw(epic)
        return board

    def save(self) -> str:
        return self.board().save()

    def parse(self, text: str, file: str = "") -> "WhiteboardStoryMap":
        """The format-adapter entry point Stories renders through: the story map a board's text holds."""
        return self.take_board(Whiteboard.from_text(text))

    def take_board(self, board: Whiteboard) -> "WhiteboardStoryMap":
        """The story map board draws, read by where its elements sit."""
        cells = [cell for cell in (_BoardCell(element) for element in board.holding({"epic"}, "story-map epic").shapes) if cell.role]
        story_map = WhiteboardStoryMap()
        story_map.place_cells(cells)
        return story_map

    def save_thin_slice(self) -> str:
        """This map's increments as a board, laid out as drawio lays out its thin slice: one column per sub-epic under
        the epic and sub-epic bars, each column as wide as the most stories any one increment puts in it, and one lane
        per increment stacked below each other, each a single row of its stories under the sub-epic that holds each."""
        return _ThinSliceBoard(self, Whiteboard()).board().save()

    def load_thin_slice(self, text: str) -> "WhiteboardStoryMap":
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
            increments.append(self.increment_class(name, len(increments) + 1, self.descendants.stories_named(names)))
        self.increments.refill(increments)
        return self


class _ThinSliceBoard(ThinSliceSurface):
    """The board a story map's thin slice is drawn on, in the layout every drawn format draws (``ThinSliceLayout``)."""

    LANE_INSET = 24
    LANE_GAP = 24
    LABEL_WIDTH = 200
    """The increment's name sits in a label at the left of its lane, as drawio draws it, and the columns start after it."""

    def __init__(self, story_map: WhiteboardStoryMap, drawing: Whiteboard) -> None:
        self.story_map = story_map
        self.drawing = drawing
        self.left = WhiteboardEpic.first_x + self.LABEL_WIDTH + self.LANE_GAP
        self.layout = ThinSliceLayout(story_map, WhiteboardStory.pitch, WhiteboardStory.column_pad, self.left)
        self._top = DiagramEpic.nested_row_y + DiagramEpic.bar_height + self.LANE_GAP

    def board(self) -> Whiteboard:
        self.layout.draw_on(self)
        return self.drawing

    def epic_header(self, epic: Epic, x: float, width: float) -> None:
        self.drawing.add(Shape(epic.element_id("epic"), box=Box(x, DiagramEpic.row_y, width - WhiteboardEpic.bar_gap, DiagramEpic.bar_height),
                               kind="rounded", color="purple", size="body", text=epic.name))

    def sub_epic_header(self, column: ThinSliceColumn) -> None:
        sub = column.sub
        self.drawing.add(Shape(sub.element_id("subepic", str(sub.depth)), box=Box(column.x, DiagramEpic.nested_row_y, column.width - WhiteboardEpic.bar_gap, DiagramEpic.bar_height),
                               kind="rounded", color="green", size="body", text=sub.name))

    def lane(self, lane: ThinSliceLane, layout: ThinSliceLayout) -> None:
        board, increment, top = self.drawing, lane.increment, self._top
        lane_id = ElementId.of("lane", f"lane:{increment.name}", length=WhiteboardNode.KEY_LENGTH)
        height = WhiteboardStory.size + 2 * self.LANE_INSET
        board.add(Section(lane_id, box=Box(WhiteboardEpic.first_x, top, self.left - WhiteboardEpic.first_x + layout.width, height), color="white"))
        board.add(Shape(ElementId("increment", lane_id.key), box=Box(WhiteboardEpic.first_x + self.LANE_INSET, top + self.LANE_INSET, self.LABEL_WIDTH - self.LANE_INSET, WhiteboardStory.size),
                        kind="rounded", color="white", size="body", text=increment.name))
        for column, stories in lane.stories.items():
            column_left = layout.columns[column].x + WhiteboardStory.column_pad
            for place, story in enumerate(self._map_story(story) for story in stories):
                if isinstance(story, WhiteboardStory):
                    board.add(story.lane_card(lane_id, column_left + place * WhiteboardStory.pitch, top + self.LANE_INSET))
        self._top = top + height + self.LANE_GAP

    def _map_story(self, story: Story) -> Story:
        """The map's own whiteboard story of this name, which carries the card's actor and size."""
        return next((held for held in self.story_map.descendants.stories() if held.name == story.name), story)


class _BoardCell(DiagramStoryCell):
    """A board shape as a story-map cell: its role, bar depth and story kind from its id, its text, and its box. A
    shape no story map draws has no role."""

    ROLES = ("epic", "subepic", "story", "actor")

    def __init__(self, element: BoardElement) -> None:
        super().__init__()
        if element.role not in self.ROLES:
            return
        self.role = element.role
        self.depth = int(element.id.parts[0]) if self.role == "subepic" else -1
        self.kind = element.id.parts[0] if self.role == "story" else ""
        lines = [line.strip() for line in element.text.strip().splitlines() if line.strip()]
        actor = re.match(r"^\*([^*].*)\*$", lines[0]) if self.role == "story" and len(lines) > 1 else None
        self.actor = actor.group(1).strip() if actor else ""
        self.text = unlink(" ".join(lines[1:] if actor else lines))
        self.x, self.y, self.width, self.height = element.box.x, element.box.y, element.box.w, element.box.h
