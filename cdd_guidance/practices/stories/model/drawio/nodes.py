"""DrawIO format story nodes - all seven StoryNode subtypes plus I/O.

Two views:
- story-map  render(canonical)            - Epic -> Epic -> Story grid
- thin-slice DrawIOStoryMap.save_thin_slice / load_thin_slice - increment rows across epic columns
"""

from __future__ import annotations

import itertools
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

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
from cdd_guidance.practices.stories.model.markdown.links import StoryMapLinks
from cdd_guidance.practices.stories.model.story_map import Epic, Story, StoryMap, StoryType
from harness.drawio import DrawioCell, DrawioFile, DrawioPage, KeepsDocumentInDrawing, UnreadableDrawio
from harness.guidance.practice_formats import Written
from harness.whiteboard import Box

# A sub-epic's estimate is never drawn narrower than this, however little room its bar leaves.
_ESTIMATE_MIN_WIDTH = 80
# An epic's estimate is never drawn wider than this, however wide the epic.
_EPIC_ESTIMATE_MAX_WIDTH = 160
# A thin slice's header and lane label stop this far short of the next column, so neighbours do not touch.
_HEADER_INSET = 4


class DrawIOIncrement(DiagramIncrement):
    width = 480
    lane_style = (
        "inc-lane;whiteSpace=wrap;html=1;overflow=hidden;"
        f"fillColor={DiagramIncrement.fill};strokeColor={DiagramIncrement.stroke};"
        "fontColor=#000000;fontSize=11;fontStyle=1;"
    )
    label_style = (
        "inc-lane-label;whiteSpace=wrap;html=1;overflow=hidden;"
        "fillColor=#e8e8e8;strokeColor=#666666;fontColor=#000000;fontSize=10;fontStyle=1;"
        "align=right;spacingRight=8;verticalAlign=middle;"
    )
    story_style = (
        "increment-story;whiteSpace=wrap;html=1;overflow=hidden;"
        f"fillColor={DiagramStory.fill};strokeColor={DiagramStory.stroke};"
        "fontColor=#000000;fontSize=8;"
    )

    # The first lane starts this far below the lowest epic or sub-epic header drawn above it.
    header_gap = 10
    # The gap between story cards in a thin slice's lane, and around them.
    card_gap = 6


class DrawIOStory(LaidOutStory):
    shaping_row_y = 275
    inset = 10
    actor_style = (
        "actor;whiteSpace=wrap;html=1;overflow=hidden;"
        f"fillColor={DiagramStory.actor_fill};strokeColor={DiagramStory.actor_stroke};"
        "fontColor=#000000;fontSize=7;"
    )
    style = (
        "story:{role};whiteSpace=wrap;html=1;overflow=hidden;aspect=fixed;"
        f"fillColor={DiagramStory.fill};strokeColor={DiagramStory.stroke};"
        "fontColor=#000000;fontSize=8;"
    )

    @property
    def cell_slug(self) -> str:
        parent = self.parent
        if not isinstance(parent, Epic):
            return self.slug
        seen = 0
        for story in parent.stories:
            if story is self:
                break
            if story.slug == self.slug:
                seen += 1
        return self.slug if seen == 0 else f"{self.slug}-{seen + 1}"

    def cells(self, parent_id: str) -> List["DrawIOStoryMap.Vertex"]:
        actor = self.actors[0].strip() if self.actors else ""
        cell_id = f"{parent_id}/{self.cell_slug}"
        drawn: List[DrawIOStoryMap.Vertex] = []
        if actor:
            drawn.append(DrawIOStoryMap.Vertex.make(
                f"{cell_id}/actor", actor, self.x,
                self.y - self.actor_height - self.actor_gap,
                self.size, self.actor_height, self.actor_style,
            ))
        drawn.append(DrawIOStoryMap.Vertex.make(
            cell_id, self.name, self.x, self.y, self.size, self.size,
            self.style.format(role=self.story_type.value),
        ).linked(self))
        return drawn


class DrawIOEpic(LaidOutEpic):
    story_class = DrawIOStory
    # A draw.io epic starts at the map's margin, its sub-epics after the stories it holds itself.
    first_x = DiagramEpic.left_margin
    epic_spacing = DiagramEpic.gap
    story_pitch = DrawIOStory.pitch
    shaping_row_y = 200
    estimate_gap = 15
    estimate_row_y = DiagramEpic.row_y - 20
    estimate_height = 40
    epic_estimate_style = "text;whiteSpace=wrap;html=1;"
    estimate_style = (
        "estimate;whiteSpace=wrap;html=1;overflow=hidden;"
        "fillColor=none;strokeColor=none;fontColor=#333333;fontSize=8;"
        "align=left;spacingLeft=4;"
    )

    @property
    def cell_id(self) -> str:
        parent = self.parent
        if isinstance(parent, DrawIOEpic):
            return f"{parent.cell_id}/{self.slug}"
        return self.slug

    @property
    def bar_width(self) -> int:
        return self.width - self.tighten * 2

    @property
    def style(self) -> str:
        if isinstance(self.parent, Epic):
            return (
                f"subepic:{self.depth};rounded=1;whiteSpace=wrap;html=1;overflow=hidden;"
                f"fillColor={self.nested_fill};strokeColor={self.nested_stroke};"
                "fontColor=#000000;fontSize=10;"
            )
        return (
            "epic;rounded=1;whiteSpace=wrap;html=1;overflow=hidden;"
            f"fillColor={DiagramEpic.fill};strokeColor={DiagramEpic.stroke};"
            "fontColor=#000000;fontSize=11;"
        )

    def cells(self) -> List["DrawIOStoryMap.Vertex"]:
        if not isinstance(self.parent, Epic):
            return self._epic_cells()
        drawn = [DrawIOStoryMap.Vertex.make(
            self.cell_id, self.name, self.x, self.y, self.bar_width, self.bar_height, self.style,
        ).linked(self)]
        for story in self.stories:
            drawn.extend(story.cells(self.cell_id))
        for child in self.epics:
            drawn.extend(child.cells())
        if (self.estimate or "").strip():
            drawn.append(self._estimate_cell())
        return drawn

    def _estimate_cell(self) -> "DrawIOStoryMap.Vertex":
        """A sub-epic's estimate, written on its story line after its last story."""
        estimate = self.estimate.strip()
        label = estimate if estimate.startswith("*") else f"* {estimate}"
        if self.stories:
            last_story_x = self.x + self.tighten + (len(self.stories) - 1) * DiagramStory.pitch
            estimate_x = last_story_x + DiagramStory.size + self.estimate_gap
        else:
            estimate_x = self.x + self.tighten
        return DrawIOStoryMap.Vertex.make(
            f"{self.cell_id}/estimate", label, estimate_x, self._story_line_y(),
            max(self.bar_width - (estimate_x - self.x) - self.tighten, _ESTIMATE_MIN_WIDTH),
            DiagramStory.size, self.estimate_style,
        )

    def _epic_cells(self) -> List["DrawIOStoryMap.Vertex"]:
        drawn = [DrawIOStoryMap.Vertex.make(
            self.cell_id, self.name, self.x, self.y, self.width, self.height, self.style,
        ).linked(self)]
        for story in self.stories:
            drawn.extend(story.cells(self.cell_id))
        estimate = (self.estimate or "").strip()
        if estimate:
            label = self.columns.estimate_label()
            drawn.append(DrawIOStoryMap.Vertex.make(
                f"{self.cell_id}/epic-estimate", label, self.x, self.estimate_row_y,
                min(_EPIC_ESTIMATE_MAX_WIDTH, self.width), self.estimate_height, self.epic_estimate_style,
            ))
        for child in self.epics:
            drawn.extend(child.cells())
        return drawn


# -- Root node + I/O -----------------------------------------------------------

class _PlacedCell(DiagramStoryCell):
    """One vertex of a story map diagram as it sits on screen: its role from the style, its bar depth, and its box."""

    def __init__(self, cell: DrawioCell) -> None:
        super().__init__()
        style = cell.style
        self.style = style.text
        self.text = cell.label
        self.cell_id = cell.id
        self.role = style.role
        self.depth = int(style.role_detail) if self.role == "subepic" and style.role_detail else -1
        self.kind = style.role_detail if self.role == "story" else ""
        box = cell.box or Box(0, 0, 0, 0)
        self.x, self.y, self.width, self.height = box.x, box.y, box.w, box.h

    @property
    def is_epic_estimate(self) -> bool:
        return self.cell_id.endswith("/epic-estimate") or (self.cell_id.endswith("/estimate") and self.cell_id.count("/") == 1)

    @property
    def estimate(self) -> str:
        """The estimate the cell's text says, without its markup and the `*` it is written after."""
        plain = re.sub(r"<[^>]+>", "", self.text)
        return plain.strip().removeprefix("*").strip()

    @property
    def is_outline_estimate(self) -> bool:
        """A text cell a shaping outline writes an epic's estimate in: one that says approx, or starts with `*`."""
        return self.role == "text" and bool(self.estimate) and ("approx" in self.estimate.lower() or self.text.strip().startswith("*"))

    def estimate_owner(self, owners: List["_PlacedCell"]) -> Optional["_PlacedCell"]:
        """The epic or sub-epic among owners whose estimate this cell is; none for a cell that is no estimate."""
        epics = [owner for owner in owners if owner.depth < 0]
        if self.is_outline_estimate:
            return self.beneath(epics)
        if self.role == "estimate":
            return self.beneath(epics if self.is_epic_estimate else owners, across=self.x)
        return None


def _is_thin_slice_card(cell_id: str) -> bool:
    """Whether cell_id names a story card in a thin slice's lane, `inc-lane/{increment}/{story}`, rather than a lane's
    background or label."""
    return cell_id.startswith("inc-lane/") and cell_id.count("/") == 2 and not cell_id.endswith("/bg")


def _measure(written: object) -> float | int:
    """A geometry value as the drawing wrote it, read as a number: whole numbers stay whole, so a cell drawn again is
    written as it was, `928` and not `928.0`."""
    value = float(written or 0)
    return int(value) if value.is_integer() else value


class _KeptPlaces:
    """Where each cell of a story map drawn before stands, by its cell id: the drawing a person may have moved cards on,
    which the next render keeps them where they put them."""

    def __init__(self) -> None:
        self._places: Dict[str, Dict[str, str]] = {}

    @classmethod
    def from_text(cls, drawio: Optional[str]) -> "_KeptPlaces":
        """The places a draw.io file holds; none for no file, or text that is no draw.io file."""
        kept = cls()
        if not drawio:
            return kept
        try:
            drawn = DrawioFile.from_text(drawio).whole
        except UnreadableDrawio:
            return kept
        kept._places = {cell.id: cell.geometry for cell in drawn.cells if cell.id and cell.geometry}
        return kept

    def box_of(self, cell_id: str) -> Optional[Box]:
        """The box the cell named cell_id stood in; none for a cell the drawing did not hold."""
        kept = self._places.get(cell_id)
        if kept is None:
            return None
        return Box(*(_measure(kept.get(side, 0)) for side in ("x", "y", "width", "height")))

    def thin_slice_cards(self) -> Dict[str, Box]:
        """The box of every story card a thin slice drawing held, in any lane, by its cell id."""
        return {name: self.box_of(name) for name in self._places if _is_thin_slice_card(name)}

    def place(self, vertex: "DrawIOStoryMap.Vertex") -> None:
        """Put vertex where its cell stood before, at the size it had; a cell new to the map stays where it was laid out.
        An epic or sub-epic that has grown since is drawn as wide as it is laid out now, so it still covers every story
        it holds."""
        kept = self._places.get(str(vertex.cell_id))
        if kept is None:
            return
        vertex.x = kept.get("x", vertex.x)
        vertex.y = kept.get("y", vertex.y)
        vertex.height = kept.get("height", vertex.height)
        kept_width = kept.get("width", vertex.width)
        if not (isinstance(vertex.node, Epic) and float(kept_width) < float(vertex.width)):
            vertex.width = kept_width


class DrawIOStoryMap(KeepsDocumentInDrawing, DiagramStoryMap):
    # Its thin slice places the cells of the drawing it is drawn over itself (*_ThinSlicePlaces*).
    keeps_thin_slice_layout = True
    suffixes = (".drawio",)
    epic_class = DrawIOEpic
    increment_class = DrawIOIncrement
    """DrawIO story-map I/O. IS the format-typed tree root.

    parse reads a file into these nodes. save writes the nodes you edited.
    The thin-slice view is save_thin_slice and load_thin_slice, over this map's own increments.
    """

    class Vertex:
        def __init__(self) -> None:
            self.cell_id = ""
            self.label = ""
            self.x = 0
            self.y = 0
            self.width = 0
            self.height = 0
            self.style = ""
            self.link = ""
            self.entry = ""
            self.code_link: dict = {}
            self.node = None

        @classmethod
        def make(cls, cell_id, label, x, y, width, height, style) -> "DrawIOStoryMap.Vertex":
            vertex = cls()
            vertex.cell_id = cell_id
            vertex.label = label
            vertex.x = x
            vertex.y = y
            vertex.width = width
            vertex.height = height
            vertex.style = style
            return vertex

        def linked(self, node) -> "DrawIOStoryMap.Vertex":
            """Draw this cell for *node*, so it can carry that node's links."""
            self.node = node
            return self

        def take_links(self, links: StoryMapLinks) -> None:
            """``link`` opens the story's own file when it has one, otherwise its ``story-map.md`` entry;
            ``entry`` keeps the story-map entry; ``code_link`` opens ``link`` in the draw.io editor of VS Code and
            Cursor, which does not follow ``link`` to a file."""
            if self.node is None:
                return
            self.entry = links.entry_for(self.node)
            story_file = links.story_file(self.node) if isinstance(self.node, Story) else ""
            self.link = story_file or self.entry
            self.code_link = links.code_link(self.link)

        def draw_on(self, page: DrawioPage) -> None:
            """This vertex as a cell of page; a linked one inside the UserObject that carries its links."""
            link = None
            if self.link:
                link = {"link": self.link, **({"entry": self.entry} if self.entry and self.entry != self.link else {}), **self.code_link}
            page.add(str(self.cell_id), self.label, self.style, Box(self.x, self.y, self.width, self.height), link)

    # -- Uniform Callable Surface ----------------------------------------------

    @property
    def has_outline_estimates(self) -> bool:
        return any(epic.columns.has_estimate() for epic in self.epics)

    @property
    def sub_epic_top(self) -> int:
        """A shaping outline drops its sub-epics lower, leaving room for the epic estimate above them."""
        return DrawIOEpic.shaping_row_y if self.has_outline_estimates else DrawIOEpic.nested_row_y

    @property
    def story_floor(self) -> int:
        return DrawIOStory.shaping_row_y if self.has_outline_estimates else DrawIOStory.row_y

    def render(self, canonical: StoryMap, written: Written = Written()) -> str:
        """Draw the story map. Written in a folder, each epic, sub-epic, and story cell links to its ``story-map.md``
        entry there, and a story to its own file when one exists. With no target file, the cell has no link. Each cell
        the previous drawing held stays where it stood there, so the cards a person moved stay put."""
        drawn = self.copy_of(canonical)
        if written.folder is not None:
            drawn.links = StoryMapLinks(drawn, str(written.folder))
        drawn.kept_places = _KeptPlaces.from_text(written.previous or None)
        return drawn.save()

    # Where the cells of the drawing this one replaces stood; none while the map is drawn afresh.
    kept_places: Optional[_KeptPlaces] = None

    def save(self) -> str:
        """Draw this story map; each cell links where the links of the folder it was placed in say, and stands where
        the drawing it replaces had it."""
        vertices = [vertex for epic in self.epics for vertex in epic.cells()]
        drawing = DrawioFile()
        page = drawing.add_page("Story Map", "story-map")
        for vertex in vertices:
            if self.links is not None:
                vertex.take_links(self.links)
            if self.kept_places is not None:
                self.kept_places.place(vertex)
            vertex.draw_on(page)
        return drawing.save()

    def parse(self, text: str, file: str = "") -> "DrawIOStoryMap":
        """Read the story map by where its cells sit, not their order in the file: draw.io saves cells back to
        front, so bringing a cell forward or sending it back moves it in the file but not on screen."""
        cells = self._placed_cells(text)
        story_map = DrawIOStoryMap()
        owners = story_map.place_cells(cells)
        for cell in cells:
            owner = cell.estimate_owner(owners)
            if owner is not None and (cell.role == "estimate" or cell.estimate):
                owner.node.estimate = cell.estimate
        return story_map

    def _placed_cells(self, text: str) -> List[_PlacedCell]:
        """Each vertex a draw.io story map draws, as it sits on screen; a linked one read with its UserObject's id and
        words."""
        return [_PlacedCell(cell) for cell in DrawioFile.from_text(text).whole.cells if cell.is_vertex]

    # -- Thin-slice view -------------------------------------------------------

    def save_thin_slice(self) -> str:
        """This map's increments as a swim-lane grid: epic/sub-epic columns x increment rows.

        Row 1: Epic headers (same positions as story-map view).
        Row 2: Sub-epic headers.
        Rows 3+: One horizontal lane per increment; story cells placed in their
                 epic-column position within the lane.
        """
        return _ThinSliceDrawing(self, DrawioFile(), self.kept_places or _KeptPlaces()).text()

    def render_thin_slice(self, written: Written = Written()) -> str:
        """This map's increments drawn as its thin slice over the drawing written holds: each lane, card and bar stands
        where that drawing had it, so the layout a person gave the thin slice stays."""
        self.kept_places = _KeptPlaces.from_text(written.previous or None)
        return self.save_thin_slice()

    def load_thin_slice(self, text: str) -> "DrawIOStoryMap":
        """Read a thin-slicing.drawio document into this map's increments, each delivering the map's own stories
        that its lane names, and return this map."""
        names, lanes = self._lanes_in(DrawioFile.from_text(text).whole)
        self.increments.refill([
            DrawIOIncrement(names[slug], order, lanes[slug]) for order, slug in enumerate((slug for slug in lanes if slug in names), start=1)
        ])
        return self

    def _lanes_in(self, page: DrawioPage) -> Tuple[Dict[str, str], Dict[str, List[Story]]]:
        """Each lane's name and the map's stories it holds, by the increment slug its cells are named with. Cells are
        read in document order, so a lane's stories may come before its label."""
        lanes: Dict[str, List[Story]] = {}
        names: Dict[str, str] = {}
        for cell in (cell for cell in page.cells if cell.is_vertex and not cell.link):
            style = cell.style.text
            parts = cell.id.split("/", 2)
            if len(parts) < 2:
                continue
            if style.startswith("inc-lane-label;"):
                names[parts[1]] = cell.label.strip()
                lanes.setdefault(parts[1], [])
            elif style.startswith("increment-story;") and len(parts) >= 3:
                lanes.setdefault(parts[1], []).extend(self.descendants.stories_named([cell.label.strip()]))
        return names, lanes


class _ThinSlicePlaces:
    """Where each lane, story card and bar of a thin slice is drawn, over the thin slice drawing it replaces. A lane,
    card or bar that drawing held stands where it stood, since a person may have laid it out by hand, moved right only
    as far as a column added or widened to its left needs; a card new to a lane takes the first free place in its
    sub-epic's column there, beside or below the cards already in it; and each column is as wide as the cards it holds,
    so every card stays under the bar of the sub-epic that holds it and no bar is drawn over another. With no drawing
    before it, this is the layout's own: one row of cards in each lane, each column as wide as its fullest lane."""

    def __init__(self, layout: ThinSliceLayout, kept: _KeptPlaces, lane_top: float) -> None:
        self._layout = layout
        self._kept = kept
        self._pitch = DiagramStory.size + DrawIOIncrement.card_gap
        self._counted: Dict[str, Dict[str, int]] = {}
        self.lanes: List[Box] = self._laid_lanes(lane_top)
        self._named = [self._named_cards(column) for column in range(len(layout.columns))]
        drawn = {cell_id for named in self._named for _, cell_id, _ in named}
        # Every place a card stands in: the drawing's cards that are not drawn again, which the save puts back where
        # they stood, and each card placed since.
        self._taken: List[Box] = [box for name, box in kept.thin_slice_cards().items() if name not in drawn]
        self.cards: List[List[Tuple[str, Story, Box]]] = [[] for _ in layout.lanes]
        # How far each column moved right of where the drawing had it, to make room for what was added to its left.
        self._moved: List[float] = []
        self.columns: List[Box] = self._laid_columns()

    @property
    def right(self) -> float:
        """Where the last column ends."""
        return max((column.x + column.w for column in self.columns), default=DiagramEpic.left_margin)

    def epic_bar(self, epic: Epic) -> Box:
        """The epic's bar over every column it holds: where the drawing had it, moved with its first column, and at
        least as wide as those columns."""
        held = [(box, moved) for column, box, moved in zip(self._layout.columns, self.columns, self._moved) if column.epic is epic]
        start, end = held[0][0].x, held[-1][0].x + held[-1][0].w - _HEADER_INSET
        kept = self._kept.box_of(epic.slug)
        if kept is None:
            return Box(start, DiagramEpic.row_y, end - start, DiagramEpic.bar_height)
        x = kept.x + held[0][1]
        return Box(x, kept.y, max(kept.w, end - x), kept.h)

    def _laid_lanes(self, top: float) -> List[Box]:
        """Each lane's box: where the drawing had its background, else below the lane before it."""
        lanes: List[Box] = []
        left = DiagramEpic.left_margin - DrawIOIncrement.label_width
        for lane in self._layout.lanes:
            kept = self._kept.box_of(f"inc-lane/{lane.increment.slug}/bg")
            box = Box(left, kept.y, kept.w, kept.h) if kept else Box(left, top, 0, DrawIOIncrement.lane_height)
            lanes.append(box)
            top = box.y + box.h + DrawIOIncrement.lane_gap
        return lanes

    def _named_cards(self, column: int) -> List[Tuple[int, str, Story]]:
        """Each card the lanes put in the column: its lane's index, its cell id, and its story."""
        return [(index, self._card_id(lane.increment.slug, story.slug), story)
                for index, lane in enumerate(self._layout.lanes) for story in lane.stories.get(column, [])]

    def _laid_columns(self) -> List[Box]:
        """Each column's box, left to right, with its cards placed: a column the drawing held where it stood, moved
        right past the column before it when that one ends further right; a new one straight after the column before."""
        columns: List[Box] = []
        start, moved = DiagramEpic.left_margin, 0
        for index, column in enumerate(self._layout.columns):
            kept = self._kept.box_of(self._column_cell(column))
            x, width = (max(kept.x + moved, start), kept.w + _HEADER_INSET) if kept else (start, self._pitch + DrawIOIncrement.card_gap)
            moved = x - kept.x if kept else moved
            width = max(width, self._placed_cards(index, x, width, moved) - x)
            columns.append(Box(x, DiagramEpic.nested_row_y, width, DiagramEpic.bar_height))
            self._moved.append(moved)
            start = x + width
        return columns

    def _column_cell(self, column: ThinSliceColumn) -> str:
        """The cell that heads column: its sub-epic's bar, or its epic's when the epic has no sub-epics."""
        return column.sub.cell_id if column.sub is not column.epic else column.epic.slug

    def _placed_cards(self, column: int, x: float, width: float, moved: float) -> float:
        """Place the cards the lanes put in the column at x, width wide, which moved right by moved: the drawing's own
        cards first, moved with it, then each new card in a free place; answer where the column must end to hold
        them."""
        named = self._named[column]
        placed = [(lane, cell_id, story, self._moved_by(self._kept.box_of(cell_id), moved))
                  for lane, cell_id, story in named if self._kept.box_of(cell_id) is not None]
        self._taken.extend(box for *_, box in placed)
        for lane, cell_id, story in named:
            if self._kept.box_of(cell_id) is None:
                placed.append((lane, cell_id, story, self._free_place(x, width, self.lanes[lane])))
                self._taken.append(placed[-1][3])
        for lane, cell_id, story, box in placed:
            self.cards[lane].append((cell_id, story, box))
        return max([x + width] + [box.x + box.w + DrawIOIncrement.card_gap for *_, box in placed])

    def _moved_by(self, box: Box, moved: float) -> Box:
        return Box(box.x + moved, box.y, box.w, box.h)

    def _card_id(self, increment: str, story: str) -> str:
        """The id of a story's card in an increment's lane; a story the lane holds again takes the next number."""
        counted = self._counted.setdefault(increment, {})
        count = counted[story] = counted.get(story, 0) + 1
        return f"inc-lane/{increment}/{story}" + (f"-{count}" if count > 1 else "")

    def _free_place(self, x: float, width: float, lane: Box) -> Box:
        """The first place in the column at x, width wide, within lane, that no card stands in: along each row the lane
        is tall enough for, then on along its first row past the column's right edge, which the column then grows to."""
        top = lane.y + (DrawIOIncrement.lane_height - DiagramStory.size) // 2
        rows = max(1, int((lane.y + lane.h - top - DiagramStory.size) // self._pitch) + 1)
        across = max(1, int((width - DrawIOIncrement.card_gap - DiagramStory.size) // self._pitch) + 1)
        inside = (self._place(x, top, row, slot) for row in range(rows) for slot in range(across))
        beyond = (self._place(x, top, 0, slot) for slot in itertools.count(across))
        return next(place for place in itertools.chain(inside, beyond) if not self._is_taken(place))

    def _place(self, x: float, top: float, row: int, slot: int) -> Box:
        """The card place slot steps along row of the column at x, its first row at top."""
        return Box(x + DrawIOIncrement.card_gap + slot * self._pitch, top + row * self._pitch, DiagramStory.size, DiagramStory.size)

    def _is_taken(self, place: Box) -> bool:
        return any(place.x < card.x + card.w and card.x < place.x + place.w and place.y < card.y + card.h and card.y < place.y + place.h
                   for card in self._taken)


class _ThinSliceDrawing(ThinSliceSurface):
    """The draw.io page a story map's thin slice is drawn on: its epics and sub-epics as column headers, and one lane
    per increment holding its stories under their sub-epics' columns, each where *_ThinSlicePlaces* puts it."""

    def __init__(self, story_map: DrawIOStoryMap, drawing: DrawioFile, kept: _KeptPlaces) -> None:
        self.drawing = drawing
        self.page = drawing.add_page("Thin Slicing", "thin-slicing")
        self.layout = ThinSliceLayout(story_map, DiagramStory.size + DrawIOIncrement.card_gap, DrawIOIncrement.card_gap, DiagramEpic.left_margin)
        lane_top = DiagramEpic.nested_row_y + DiagramEpic.bar_height + DrawIOIncrement.header_gap
        self.places = _ThinSlicePlaces(self.layout, kept, lane_top)
        self.width = DrawIOIncrement.label_width + self.places.right - DiagramEpic.left_margin
        self._lanes_drawn = 0

    def _draw(self, vertex: "DrawIOStoryMap.Vertex") -> None:
        vertex.draw_on(self.page)

    def text(self) -> str:
        self.layout.draw_on(self)
        return self.drawing.save()

    def epic_header(self, epic: Epic, x: float, width: float) -> None:
        """The epic's bar over every column it holds, where the places put those columns."""
        bar = self.places.epic_bar(epic)
        self._draw(DrawIOStoryMap.Vertex.make(epic.slug, epic.name, bar.x, bar.y, bar.w, bar.h, epic.style))

    def sub_epic_header(self, column: ThinSliceColumn) -> None:
        sub = column.sub
        box = self.places.columns[self.layout.columns.index(column)]
        self._draw(DrawIOStoryMap.Vertex.make(sub.cell_id, sub.name, box.x, DiagramEpic.nested_row_y, box.w - _HEADER_INSET, DiagramEpic.bar_height, sub.style))

    def lane(self, lane: ThinSliceLane, layout: ThinSliceLayout) -> None:
        """One increment's lane: its label at the left and its stories where the places put them."""
        index = self._lanes_drawn
        self._lanes_drawn += 1
        increment, box = lane.increment, self.places.lanes[index]
        self._draw(DrawIOStoryMap.Vertex.make(f"inc-lane/{increment.slug}/bg", "", box.x, box.y, max(box.w, self.width), box.h, DrawIOIncrement.lane_style))
        self._draw(DrawIOStoryMap.Vertex.make(f"inc-lane/{increment.slug}", increment.name, box.x, box.y, DrawIOIncrement.label_width - _HEADER_INSET, box.h, DrawIOIncrement.label_style))
        for cell_id, story, card in self.places.cards[index]:
            self._draw(DrawIOStoryMap.Vertex.make(cell_id, story.name, card.x, card.y, card.w, card.h, DrawIOIncrement.story_style))
