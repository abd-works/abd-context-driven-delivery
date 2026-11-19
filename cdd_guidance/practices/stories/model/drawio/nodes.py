"""DrawIO format story nodes - all seven StoryNode subtypes plus I/O.

Two views:
- story-map  render(canonical)            - Epic -> Epic -> Story grid
- thin-slice DrawIOStoryModel.save_thin_slice / load_thin_slice - increment rows across epic columns
"""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Callable, Dict, Iterator, List, Optional, Tuple

from cdd_guidance.practices.stories.model.diagram_story_model import (
    DiagramStoryCell,
    LaidOutEpic,
    LaidOutStory,
    DiagramEpic,
    DiagramIncrement,
    DiagramStory,
    DiagramStoryModel,
)
from cdd_guidance.practices.stories.model.markdown.links import StoryMapLinks
from cdd_guidance.practices.stories.model.story_map_files import path_from
from cdd_guidance.practices.stories.model.story_model import Epic, Story, StoryModel, StoryType

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

    def cells(self, parent_id: str) -> List["DrawIOStoryModel.Vertex"]:
        actor = self.actors[0].strip() if self.actors else ""
        cell_id = f"{parent_id}/{self.cell_slug}"
        drawn: List[DrawIOStoryModel.Vertex] = []
        if actor:
            drawn.append(DrawIOStoryModel.Vertex.make(
                f"{cell_id}/actor", actor, self.x,
                self.y - self.actor_height - self.actor_gap,
                self.size, self.actor_height, self.actor_style,
            ))
        drawn.append(DrawIOStoryModel.Vertex.make(
            cell_id, self.name, self.x, self.y, self.size, self.size,
            self.style.format(role=self.story_type.value),
        ).linked(self))
        return drawn


class DrawIOEpic(LaidOutEpic):
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

    def story_xs(self) -> Dict[str, List[int]]:
        """Each story name's columns, left to right; one name can sit under several sub-epics."""
        found: Dict[str, List[int]] = {}
        for story in self.stories:
            found.setdefault(story.name, []).append(story.x)
        for child in self.epics:
            for name, xs in child.story_xs().items():
                found.setdefault(name, []).extend(xs)
        return found

    def cells(self) -> List["DrawIOStoryModel.Vertex"]:
        if not isinstance(self.parent, Epic):
            return self._epic_cells()
        drawn = [DrawIOStoryModel.Vertex.make(
            self.cell_id, self.name, self.x, self.y, self.bar_width, self.bar_height, self.style,
        ).linked(self)]
        for story in self.stories:
            drawn.extend(story.cells(self.cell_id))
        for child in self.epics:
            drawn.extend(child.cells())
        if (self.estimate or "").strip():
            drawn.append(self._estimate_cell())
        return drawn

    def _estimate_cell(self) -> "DrawIOStoryModel.Vertex":
        """A sub-epic's estimate, written on its story line after its last story."""
        estimate = self.estimate.strip()
        label = estimate if estimate.startswith("*") else f"* {estimate}"
        if self.stories:
            last_story_x = self.x + self.tighten + (len(self.stories) - 1) * DiagramStory.pitch
            estimate_x = last_story_x + DiagramStory.size + self.estimate_gap
        else:
            estimate_x = self.x + self.tighten
        return DrawIOStoryModel.Vertex.make(
            f"{self.cell_id}/estimate", label, estimate_x, self._story_line_y(),
            max(self.bar_width - (estimate_x - self.x) - self.tighten, _ESTIMATE_MIN_WIDTH),
            DiagramStory.size, self.estimate_style,
        )

    def _epic_cells(self) -> List["DrawIOStoryModel.Vertex"]:
        drawn = [DrawIOStoryModel.Vertex.make(
            self.cell_id, self.name, self.x, self.y, self.width, self.height, self.style,
        ).linked(self)]
        for story in self.stories:
            drawn.extend(story.cells(self.cell_id))
        estimate = (self.estimate or "").strip()
        if estimate:
            label = self.columns.estimate_label()
            drawn.append(DrawIOStoryModel.Vertex.make(
                f"{self.cell_id}/epic-estimate", label, self.x, self.estimate_row_y,
                min(_EPIC_ESTIMATE_MAX_WIDTH, self.width), self.estimate_height, self.epic_estimate_style,
            ))
        for child in self.epics:
            drawn.extend(child.cells())
        return drawn


# -- Root node + I/O -----------------------------------------------------------

class DrawIOParseError(Exception):
    """Raised when a document is not a valid Draw.io story map."""


class _PlacedCell(DiagramStoryCell):
    """One vertex of a story map diagram as it sits on screen: its role from the style, its bar depth, and its box."""

    def __init__(self, element: ET.Element) -> None:
        super().__init__()
        self.style = element.attrib.get("style", "")
        self.text = element.attrib.get("value", "")
        self.cell_id = element.attrib.get("id", "")
        head = self.style.split(";", 1)[0]
        self.role = head.split(":", 1)[0]
        self.depth = int(head.split(":", 1)[1]) if self.role == "subepic" and ":" in head else -1
        self.kind = head.split(":", 1)[1] if self.role == "story" and ":" in head else ""
        geometry = element.find("mxGeometry")
        box = geometry.attrib if geometry is not None else {}
        self.x, self.y = float(box.get("x", 0)), float(box.get("y", 0))
        self.width, self.height = float(box.get("width", 0)), float(box.get("height", 0))

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


class _DrawIOPage:
    """One page of a draw.io file being written: its root, which each vertex is added under."""

    def __init__(self, name: str, page_id: str) -> None:
        self.mxfile = ET.Element("mxfile", attrib={"host": "app.diagrams.net"})
        diagram = ET.SubElement(self.mxfile, "diagram", attrib={"name": name, "id": page_id})
        self.root = ET.SubElement(ET.SubElement(diagram, "mxGraphModel"), "root")
        ET.SubElement(self.root, "mxCell", attrib={"id": "0"})
        ET.SubElement(self.root, "mxCell", attrib={"id": "1", "parent": "0"})

    def add(self, vertex: "DrawIOStoryModel.Vertex") -> None:
        """The vertex as a cell of this page; a linked one inside the ``UserObject`` that carries its links."""
        attributes = {"id": str(vertex.cell_id), "value": vertex.label, "style": vertex.style, "vertex": "1", "parent": "1"}
        holder = self.root
        if vertex.link:
            user = {"label": attributes.pop("value"), "link": vertex.link, "id": attributes.pop("id")}
            if vertex.entry and vertex.entry != vertex.link:
                user["entry"] = vertex.entry
            user.update(vertex.code_link)
            holder = ET.SubElement(self.root, "UserObject", attrib=user)
        cell = ET.SubElement(holder, "mxCell", attrib=attributes)
        ET.SubElement(cell, "mxGeometry", attrib={
            "x": str(vertex.x), "y": str(vertex.y),
            "width": str(vertex.width), "height": str(vertex.height),
            "as": "geometry",
        })

    def text(self) -> str:
        return "<?xml version='1.0' encoding='utf-8'?>\n" + ET.tostring(self.mxfile, encoding="unicode")


class _KeptPlaces:
    """Where each cell of a story map drawn before stands, by its cell id: the drawing a person may have moved cards on,
    which the next render keeps them where they put them."""

    def __init__(self, places: Dict[str, Dict[str, str]]) -> None:
        self._places = places

    @classmethod
    def from_text(cls, drawio: Optional[str]) -> "_KeptPlaces":
        """The places a draw.io file holds; none for no file, or text that is no draw.io file."""
        if not drawio:
            return cls({})
        try:
            root = ET.fromstring(drawio)
        except ET.ParseError:
            return cls({})
        return cls({cell_id: geometry.attrib for cell_id, geometry in _drawn_geometries(root)})

    def place(self, vertex: "DrawIOStoryModel.Vertex") -> None:
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


def _drawn_geometries(root: ET.Element) -> Iterator[Tuple[str, ET.Element]]:
    """Each drawn cell's id and geometry in a draw.io file; a linked cell's id is on the ``UserObject`` round it."""
    for holder in root.iter():
        cell = holder.find("mxCell") if holder.tag == "UserObject" else holder if holder.tag == "mxCell" else None
        geometry = cell.find("mxGeometry") if cell is not None else None
        if geometry is not None and holder.get("id"):
            yield holder.get("id"), geometry


class DrawIOStoryModel(DiagramStoryModel):
    suffixes = (".drawio",)
    epic_type = DrawIOEpic
    story_type = DrawIOStory
    increment_type = DrawIOIncrement
    """DrawIO story-map I/O. IS the format-typed tree root.

    load reads a file into these nodes. save writes the nodes you edited.
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
        def make(cls, cell_id, label, x, y, width, height, style) -> "DrawIOStoryModel.Vertex":
            vertex = cls()
            vertex.cell_id = cell_id
            vertex.label = label
            vertex.x = x
            vertex.y = y
            vertex.width = width
            vertex.height = height
            vertex.style = style
            return vertex

        def linked(self, node) -> "DrawIOStoryModel.Vertex":
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

    def render(
        self,
        canonical: StoryModel | None = None,
        previous: str | None = None,
        workspace: str | None = None,
    ) -> str:
        """Draw the story map. In a *workspace* folder, each epic, sub-epic, and story cell links to its
        ``story-map.md`` entry there, and a story to its own file when one exists. With no target file,
        the cell has no link. Each cell a *previous* drawing held stays where it stood there, so the cards a person
        moved stay put."""
        drawn = self.copy_of(canonical if canonical is not None else self)
        if workspace:
            drawn.links = StoryMapLinks(drawn, workspace)
        drawn.kept_places = _KeptPlaces.from_text(previous)
        return drawn.save()

    # Where the cells of the drawing this one replaces stood; none while the map is drawn afresh.
    kept_places: Optional[_KeptPlaces] = None

    def save(self) -> str:
        """Draw this story map; each cell links where the links of the folder it was placed in say, and stands where
        the drawing it replaces had it."""
        vertices = [vertex for epic in self.epics for vertex in epic.cells()]
        page = _DrawIOPage("Story Map", "story-map")
        for vertex in vertices:
            if self.links is not None:
                vertex.take_links(self.links)
            if self.kept_places is not None:
                self.kept_places.place(vertex)
            page.add(vertex)
        return page.text()

    def parse(self, text: str) -> "DrawIOStoryModel":
        """Format-adapter entry point used by PracticeGuidance.render; same as load."""
        return self.load(text)

    @classmethod
    def from_workspace(cls, path: Path, *, on_file: Optional[Callable[[str], None]] = None, project: Optional[Path] = None) -> "DrawIOStoryModel":
        """The story map drawn in the .drawio file at path, each epic and everything under it naming that file as a
        path from project (from the file's own folder without one)."""
        path = Path(path).resolve()
        file = path_from(Path(project).resolve() if project is not None else path.parent, path)
        if on_file is not None:
            on_file(file)
        text = path.read_text(encoding="utf-8")
        loaded = cls().load(text)
        loaded.sources.add(file, text)
        loaded.descendants.place_in(file)
        return loaded

    def load(self, text: str) -> "DrawIOStoryModel":
        """Read the story map by where its cells sit, not their order in the file: draw.io saves cells back to
        front, so bringing a cell forward or sending it back moves it in the file but not on screen."""
        cells = self.placed_cells(text)
        story_map = DrawIOStoryModel()
        owners = story_map.place_cells(cells)
        for cell in cells:
            owner = cell.estimate_owner(owners)
            if owner is not None and (cell.role == "estimate" or cell.estimate):
                owner.node.estimate = cell.estimate
        return story_map

    def placed_cells(self, text: str) -> List[_PlacedCell]:
        """Each vertex a draw.io story map draws, as it sits on screen."""
        return [_PlacedCell(element) for element in self._vertices(self._graph_model(text))]

    def _graph_model(self, text: str) -> ET.Element:
        try:
            root_el = ET.fromstring(text)
        except ET.ParseError as err:
            raise DrawIOParseError(f"Not valid Draw.io XML: {err}") from err
        if root_el.tag == "mxGraphModel":
            return root_el
        if root_el.tag != "mxfile":
            raise DrawIOParseError("Root element must be <mxGraphModel>")
        tree = root_el.find(".//mxGraphModel")
        if tree is None:
            raise DrawIOParseError("mxfile has no mxGraphModel child")
        return tree

    def _vertices(self, tree: ET.Element) -> List[ET.Element]:
        """Vertex cells in document order. A linked cell sits in a ``UserObject`` that holds
        its ``label`` and ``id``; it is read as if they were on the cell, with the cell's geometry."""
        vertices: List[ET.Element] = []
        wrapped: set = set()
        for element in tree.iter():
            if element.tag == "UserObject":
                cell = element.find("mxCell")
                if cell is not None and cell.attrib.get("vertex") == "1":
                    wrapped.add(id(cell))
                    merged = ET.Element("mxCell", attrib=dict(
                        cell.attrib, id=element.attrib.get("id", ""), value=element.attrib.get("label", ""),
                    ))
                    merged.extend(cell.findall("mxGeometry"))
                    vertices.append(merged)
            elif element.tag == "mxCell" and element.attrib.get("vertex") == "1" and id(element) not in wrapped:
                vertices.append(element)
        return vertices

    # -- Thin-slice view -------------------------------------------------------

    def save_thin_slice(self) -> str:
        """This map's increments as a swim-lane grid: epic/sub-epic columns x increment rows.

        Row 1: Epic headers (same positions as story-map view).
        Row 2: Sub-epic headers.
        Rows 3+: One horizontal lane per increment; story cells placed in their
                 epic-column position within the lane.
        """
        return _ThinSliceDrawing(self, _DrawIOPage("Thin Slicing", "thin-slicing")).text()

    def load_thin_slice(self, text: str) -> "DrawIOStoryModel":
        """Read a thin-slicing.drawio document into this map's increments, each delivering the map's own stories
        that its lane names, and return this map."""
        try:
            root_el = ET.fromstring(text)
        except ET.ParseError as err:
            raise DrawIOParseError(f"Not valid Draw.io XML: {err}") from err
        tree = root_el if root_el.tag == "mxGraphModel" else root_el.find(".//mxGraphModel")
        if tree is None:
            raise DrawIOParseError("No mxGraphModel found")
        names, lanes = self._lanes_in(tree)
        self.increments.refill([
            DrawIOIncrement(names[slug], order, lanes[slug]) for order, slug in enumerate((slug for slug in lanes if slug in names), start=1)
        ])
        return self

    def _lanes_in(self, tree: ET.Element) -> Tuple[Dict[str, str], Dict[str, List[Story]]]:
        """Each lane's name and the map's stories it holds, by the increment slug its cells are named with. Cells are
        read in document order, so a lane's stories may come before its label."""
        lanes: Dict[str, List[Story]] = {}
        names: Dict[str, str] = {}
        for cell in tree.findall(".//mxCell[@vertex='1']"):
            style = cell.attrib.get("style", "")
            parts = cell.attrib.get("id", "").split("/", 2)
            if len(parts) < 2:
                continue
            if style.startswith("inc-lane-label;"):
                names[parts[1]] = cell.attrib.get("value", "").strip()
                lanes.setdefault(parts[1], [])
            elif style.startswith("increment-story;") and len(parts) >= 3:
                lanes.setdefault(parts[1], []).extend(self.descendants.stories_named([cell.attrib.get("value", "").strip()]))
        return names, lanes


class _ThinSliceDrawing:
    """A story map's increments drawn as a swim-lane grid on one draw.io page: its epics and sub-epics as column
    headers, and one lane per increment holding its stories under their sub-epics' columns."""

    def __init__(self, story_map: DrawIOStoryModel, page: _DrawIOPage) -> None:
        self.page = page
        self.columns = story_map.thin_slice_columns()
        self.lanes = story_map.thin_slice_lanes(self.columns)
        self.widths = story_map.thin_slice_widths(self.lanes, DiagramStory.size + DrawIOIncrement.card_gap, DrawIOIncrement.card_gap)
        self.width = DrawIOIncrement.label_width + sum(self.widths)

    def text(self) -> str:
        lane_y = self._headers() + DrawIOIncrement.header_gap
        for increment, held in self.lanes:
            self._lane(increment, held, lane_y)
            lane_y += DrawIOIncrement.lane_height + DrawIOIncrement.lane_gap
        return self.page.text()

    def _headers(self) -> int:
        """Each epic over the columns it spans, and each column's sub-epic under it; answers the headers' bottom."""
        x = DiagramEpic.left_margin
        for index, (epic, sub) in enumerate(self.columns):
            if index == 0 or self.columns[index - 1][0] is not epic:
                span = sum(width for (top, _), width in zip(self.columns, self.widths) if top is epic)
                self.page.add(DrawIOStoryModel.Vertex.make(epic.slug, epic.name, x, DiagramEpic.row_y, span - _HEADER_INSET, DiagramEpic.bar_height, epic.style))
            if sub is not epic:
                self.page.add(DrawIOStoryModel.Vertex.make(sub.cell_id, sub.name, x, DiagramEpic.nested_row_y, self.widths[index] - _HEADER_INSET, DiagramEpic.bar_height, sub.style))
            x += self.widths[index]
        return DiagramEpic.nested_row_y + DiagramEpic.bar_height

    def _lane(self, increment: DiagramIncrement, held: Dict[int, List[Story]], lane_y: int) -> None:
        """One increment's lane: its label at the left and its stories in one row under their sub-epics."""
        left = DiagramEpic.left_margin - DrawIOIncrement.label_width
        height = DrawIOIncrement.lane_height
        self.page.add(DrawIOStoryModel.Vertex.make(f"inc-lane/{increment.slug}/bg", "", left, lane_y, self.width, height, DrawIOIncrement.lane_style))
        self.page.add(DrawIOStoryModel.Vertex.make(f"inc-lane/{increment.slug}", increment.name, left, lane_y, DrawIOIncrement.label_width - _HEADER_INSET, height, DrawIOIncrement.label_style))
        story_y = lane_y + (DrawIOIncrement.lane_height - DiagramStory.size) // 2
        pitch = DiagramStory.size + DrawIOIncrement.card_gap
        seen: Dict[str, int] = {}
        for column, stories in held.items():
            column_x = DiagramEpic.left_margin + sum(self.widths[:column])
            for place, story in enumerate(stories):
                count = seen[story.slug] = seen.get(story.slug, 0) + 1
                cell_id = f"inc-lane/{increment.slug}/{story.slug}" + (f"-{count}" if count > 1 else "")
                story_x = column_x + DrawIOIncrement.card_gap + place * pitch
                self.page.add(DrawIOStoryModel.Vertex.make(cell_id, story.name, story_x, story_y, DiagramStory.size, DiagramStory.size, DrawIOIncrement.story_style))
