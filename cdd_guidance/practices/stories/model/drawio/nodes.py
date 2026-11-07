"""DrawIO format story nodes - all seven StoryNode subtypes plus I/O.

Two views:
- story-map  render(canonical)            - Epic -> Epic -> Story grid
- thin-slice DrawIOIncrement.save / DrawIOIncrement.load - increment rows across epic columns
"""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional

from harness.agent_tools.name import Name
from cdd_guidance.practices.stories.model.diagram_story_model import (
    DiagramEpic,
    DiagramIncrement,
    DiagramStory,
    DiagramStoryModel,
)
from cdd_guidance.practices.stories.model.markdown.links import StoryMapLinks
from cdd_guidance.practices.stories.model.story_model import Epic, Story, StoryModel, StoryType


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

    @classmethod
    def lane_top_y(cls) -> int:
        return DiagramEpic.row_y + DiagramEpic.bar_height + 10

    @classmethod
    def story_y_offset(cls) -> int:
        return (cls.lane_height - DiagramStory.size) // 2

    @classmethod
    def save(cls, story_map: StoryModel) -> str:
        return DrawIOStoryModel()._write_thin_slice(story_map)

    @classmethod
    def load(cls, text: str) -> List["DrawIOIncrement"]:
        return DrawIOStoryModel()._read_thin_slice(text)


class DrawIOStory(DiagramStory):
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
    def slug(self) -> str:
        return Name(self.name).title_slug or "node"

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

    @property
    def x(self) -> int:
        parent = self.parent
        if not isinstance(parent, Epic):
            return 0
        index = parent.stories.index(self)
        return parent.x + DrawIOEpic.tighten + index * self.pitch

    @property
    def y(self) -> int:
        story_map = self._owning_map()
        depth = story_map.max_sub_epic_depth if isinstance(story_map, DiagramStoryModel) else 0
        shaping = isinstance(story_map, DrawIOStoryModel) and story_map.has_outline_estimates
        base = DrawIOEpic.shaping_row_y if shaping else DrawIOEpic.row_y
        deepest_bottom = base + depth * (DrawIOEpic.bar_height + DrawIOEpic.depth_gap) + DrawIOEpic.bar_height
        if shaping:
            return max(self.shaping_row_y, deepest_bottom + self.pad_below_sub_epic)
        return max(
            self.row_y,
            deepest_bottom + self.actor_height + self.actor_gap + self.pad_below_sub_epic,
        )

    def cells(self, parent_id: str) -> List["DrawIOStoryModel.Vertex"]:
        parent = self.parent
        index = parent.stories.index(self) if isinstance(parent, Epic) else 0
        actor = self.actors[0].strip() if self.actors else ""
        previous = ""
        if isinstance(parent, Epic) and index > 0:
            prior = parent.stories[index - 1]
            previous = prior.actors[0].strip() if prior.actors else ""
        cell_id = f"{parent_id}/{self.cell_slug}"
        drawn: List[DrawIOStoryModel.Vertex] = []
        room = (
            self.y >= parent.y + DrawIOEpic.bar_height + self.actor_height + self.actor_gap
            if isinstance(parent, Epic) else False
        )
        if room and actor:
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


class DrawIOEpic(DiagramEpic):
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
    def slug(self) -> str:
        return Name(self.name).title_slug or "node"

    @property
    def cell_id(self) -> str:
        parent = self.parent
        if isinstance(parent, DrawIOEpic):
            return f"{parent.cell_id}/{self.slug}"
        return self.slug

    @property
    def width(self) -> int:
        if isinstance(self.parent, Epic):
            return max(self.diagram_span_columns(), 1) * DrawIOStory.pitch
        return self.span_columns() * DiagramStory.pitch

    @property
    def bar_width(self) -> int:
        return self.width - self.tighten * 2

    @property
    def height(self) -> int:
        return self.bar_height

    @property
    def y(self) -> int:
        if not isinstance(self.parent, Epic):
            return self.row_y
        story_map = self._owning_map()
        shaping = isinstance(story_map, DrawIOStoryModel) and story_map.has_outline_estimates
        base = self.shaping_row_y if shaping else self.nested_row_y
        return base + self.depth * (self.bar_height + self.depth_gap)

    @property
    def x(self) -> int:
        parent = self.parent
        if isinstance(parent, Epic):
            origin = parent.x + len(parent.stories) * DrawIOStory.pitch
            siblings = parent.epics
            offset = origin
            for sibling in siblings:
                if sibling is self:
                    return offset
                offset += sibling.width
            return offset
        offset = self.left_margin
        if parent is None:
            return offset
        for epic in parent.epics:
            if epic is self:
                return offset
            offset += epic.width + self.gap
        return offset

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

    def story_xs(self) -> Dict[str, int]:
        found = {story.name: story.x for story in self.stories}
        for child in self.epics:
            found.update(child.story_xs())
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
        estimate = (self.estimate or "").strip()
        if estimate:
            label = estimate if estimate.startswith("*") else f"* {estimate}"
            if self.stories:
                last_story_x = self.x + self.tighten + (len(self.stories) - 1) * DiagramStory.pitch
                estimate_x = last_story_x + DiagramStory.size + self.estimate_gap
            else:
                estimate_x = self.x + self.tighten
            drawn.append(DrawIOStoryModel.Vertex.make(
                f"{self.cell_id}/estimate", label, estimate_x, self.stories[0].y if self.stories else self._story_row(),
                max(self.bar_width - (estimate_x - self.x) - self.tighten, 80),
                DiagramStory.size, self.estimate_style,
            ))
        return drawn

    def _epic_cells(self) -> List["DrawIOStoryModel.Vertex"]:
        drawn = [DrawIOStoryModel.Vertex.make(
            self.cell_id, self.name, self.x, self.y, self.width, self.height, self.style,
        ).linked(self)]
        for story in self.stories:
            drawn.extend(story.cells(self.cell_id))
        estimate = (self.estimate or "").strip()
        if estimate:
            label = self.estimate_label()
            drawn.append(DrawIOStoryModel.Vertex.make(
                f"{self.cell_id}/epic-estimate", label, self.x, self.estimate_row_y,
                min(160, self.width), self.estimate_height, self.epic_estimate_style,
            ))
        for child in self.epics:
            drawn.extend(child.cells())
        return drawn

    def _story_row(self) -> int:
        story_map = self._owning_map()
        depth = story_map.max_sub_epic_depth if isinstance(story_map, DiagramStoryModel) else 0
        shaping = isinstance(story_map, DrawIOStoryModel) and story_map.has_outline_estimates
        base = self.shaping_row_y if shaping else self.row_y
        deepest_bottom = base + depth * (self.bar_height + self.depth_gap) + self.bar_height
        if shaping:
            return max(DrawIOStory.shaping_row_y, deepest_bottom + DiagramStory.pad_below_sub_epic)
        return max(
            DiagramStory.row_y,
            deepest_bottom + DiagramStory.actor_height + DiagramStory.actor_gap + DiagramStory.pad_below_sub_epic,
        )


# -- Root node + I/O -----------------------------------------------------------

class DrawIOParseError(Exception):
    """Raised when a document is not a valid Draw.io story map."""


class _PlacedCell:
    """One vertex of a story map diagram as it sits on screen: its role from the style, its bar depth, and its box."""

    def __init__(self, element: ET.Element) -> None:
        self.style = element.attrib.get("style", "")
        self.value = element.attrib.get("value", "")
        self.cell_id = element.attrib.get("id", "")
        head = self.style.split(";", 1)[0]
        self.role = head.split(":", 1)[0]
        self.depth = int(head.split(":", 1)[1]) if self.role == "subepic" and ":" in head else -1
        geometry = element.find("mxGeometry")
        box = geometry.attrib if geometry is not None else {}
        self.x, self.y = float(box.get("x", 0)), float(box.get("y", 0))
        self.width, self.height = float(box.get("width", 0)), float(box.get("height", 0))
        self.node = None

    @property
    def center(self) -> float:
        return self.x + self.width / 2

    @property
    def story_type(self) -> StoryType:
        """The kind a story cell's style names after ``story:``."""
        head = self.style.split(";", 1)[0]
        return StoryType.from_mark(head.split(":", 1)[1] if ":" in head else None)

    @property
    def is_epic_estimate(self) -> bool:
        return self.cell_id.endswith("/epic-estimate") or (self.cell_id.endswith("/estimate") and self.cell_id.count("/") == 1)

    def spans(self, x: float) -> bool:
        return self.x <= x < self.x + self.width

    def story_below(self, stories: List["_PlacedCell"]) -> Optional["_PlacedCell"]:
        """The story an actor names: the nearest one beneath it in the same column."""
        column = [story for story in stories if story.spans(self.center) and story.y > self.y]
        return min(column, key=lambda story: story.y, default=None)

    @staticmethod
    def beneath(x: float, bars: List["_PlacedCell"]) -> Optional["_PlacedCell"]:
        """The deepest bar spanning ``x``; the nearest bar when a cell was dragged past every bar's edge."""
        spanning = [bar for bar in bars if bar.spans(x)]
        if spanning:
            return max(spanning, key=lambda bar: bar.depth)
        return min(bars, key=lambda bar: abs(bar.center - x), default=None)


class DrawIOStoryModel(DiagramStoryModel):
    epic_type = DrawIOEpic
    story_type = DrawIOStory
    increment_type = DrawIOIncrement
    """DrawIO story-map I/O. IS the format-typed tree root.

    load reads a file into these nodes. save writes the nodes you edited.
    The thin-slice table is DrawIOIncrement.save and DrawIOIncrement.load.
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

        def take_links(self, entries: Dict[int, str], links: StoryMapLinks) -> None:
            """``link`` opens the story's own file when it has one, otherwise its ``story-map.md`` entry;
            ``entry`` keeps the story-map entry."""
            if self.node is None:
                return
            self.entry = entries.get(id(self.node), "")
            story_file = links.story_file(self.node) if isinstance(self.node, Story) else ""
            self.link = story_file or self.entry


    def _parse_estimate_value(self, value: str) -> str:
        plain = re.sub(r"<[^>]+>", "", value)
        return plain.strip().removeprefix("*").strip()



    # -- Uniform Callable Surface ----------------------------------------------

    @property
    def has_outline_estimates(self) -> bool:
        return any(epic._has_estimate() for epic in self.epics)

    def render(
        self,
        canonical: StoryModel | None = None,
        previous: str | None = None,
        links=None,
        workspace: str | None = None,
    ) -> str:
        """Draw the story map. With *links* (a ``StoryMapLinks``, or a *workspace* folder to find
        them in), each epic, sub-epic, and story cell links to its ``story-map.md`` entry, and a
        story to its own file when one exists. With no target file, the cell has no link."""
        if links is None and workspace:
            links = StoryMapLinks.from_workspace(workspace)
        drawn = type(self)(canonical if canonical is not None else self)
        return drawn._drawing(links)

    def save(self) -> str:
        return self._drawing(None)

    def _drawing(self, links: Optional[StoryMapLinks]) -> str:
        vertices = [vertex for epic in self.epics for vertex in epic.cells()]
        if links is not None:
            entries = links.entries(self)
            for vertex in vertices:
                vertex.take_links(entries, links)
        mxfile = ET.Element("mxfile", attrib={"host": "app.diagrams.net"})
        diagram = ET.SubElement(mxfile, "diagram", attrib={"name": "Story Map", "id": "story-map"})
        graph_model = ET.SubElement(diagram, "mxGraphModel")
        graph_root = ET.SubElement(graph_model, "root")
        ET.SubElement(graph_root, "mxCell", attrib={"id": "0"})
        ET.SubElement(graph_root, "mxCell", attrib={"id": "1", "parent": "0"})
        for vertex in vertices:
            self._add_cell(graph_root, vertex)
        body = ET.tostring(mxfile, encoding="unicode")
        return "<?xml version='1.0' encoding='utf-8'?>\n" + body

    def parse(self, text: str) -> "DrawIOStoryModel":
        """Format-adapter entry point used by PracticeGuidance.render; same as load."""
        return self.load(text)

    def load(self, text: str) -> "DrawIOStoryModel":
        """Read the story map by where its cells sit, not their order in the file: draw.io saves cells back to
        front, so bringing a cell forward or sending it back moves it in the file but not on screen."""
        cells = [_PlacedCell(element) for element in self._vertices(self._graph_model(text))]
        story_map = DrawIOStoryModel()
        owners = self._place_epics(story_map, cells)
        self._place_stories(cells, owners)
        self._place_estimates(cells, owners)
        return story_map

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

    def _place_epics(self, story_map: "DrawIOStoryModel", cells: List["_PlacedCell"]) -> List["_PlacedCell"]:
        """Epics left to right, then each sub-epic under the shallower bar it sits beneath."""
        owners: List[_PlacedCell] = []
        for cell in sorted((c for c in cells if c.role == "epic"), key=lambda c: c.x):
            cell.node = DrawIOEpic(cell.value.strip(), len(story_map.epics) + 1)
            story_map.append_epic(cell.node)
            owners.append(cell)
        for cell in sorted((c for c in cells if c.role == "subepic"), key=lambda c: (c.depth, c.x)):
            owner = _PlacedCell.beneath(cell.center, [o for o in owners if o.depth < cell.depth])
            if owner is None:
                continue
            cell.node = DrawIOEpic(cell.value, len(owner.node.epics) + 1)
            owner.node.append_epic(cell.node)
            owners.append(cell)
        return owners

    def _place_stories(self, cells: List["_PlacedCell"], owners: List["_PlacedCell"]) -> None:
        """Stories by column, then down, each under the deepest epic it sits beneath, with the actor drawn just
        above it."""
        stories = sorted((c for c in cells if c.role == "story"), key=lambda c: (c.x, c.y))
        actors = {id(story): actor for actor in cells if actor.role == "actor"
                  for story in [actor.story_below(stories)] if story is not None}
        for cell in stories:
            owner = _PlacedCell.beneath(cell.center, owners)
            if owner is None:
                continue
            story = DrawIOStory(cell.value, len(owner.node.stories) + 1, cell.story_type)
            if id(cell) in actors:
                story.actors = [actors[id(cell)].value.strip()]
            owner.node.append_story(story)

    def _place_estimates(self, cells: List["_PlacedCell"], owners: List["_PlacedCell"]) -> None:
        epics = [owner for owner in owners if owner.depth < 0]
        for cell in cells:
            if cell.role == "text":
                owner = _PlacedCell.beneath(cell.center, epics)
                estimate = self._parse_estimate_value(cell.value)
                if owner is not None and estimate and ("approx" in estimate.lower() or cell.value.strip().startswith("*")):
                    owner.node.estimate = estimate
            elif cell.role == "estimate":
                owner = _PlacedCell.beneath(cell.x, epics if cell.is_epic_estimate else owners)
                if owner is not None:
                    owner.node.estimate = self._parse_estimate_value(cell.value)

    def _vertices(self, tree) -> List[ET.Element]:
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

    def _write_thin_slice(self, canonical: StoryModel) -> str:
        """Render a swim-lane grid: epic/sub-epic columns x increment rows.

        Row 1: Epic headers (same positions as story-map view).
        Row 2: Sub-epic headers.
        Rows 3+: One horizontal lane per increment; story cells placed in their
                 epic-column position within the lane.
        """
        mxfile = ET.Element("mxfile", attrib={"host": "app.diagrams.net"})
        diagram = ET.SubElement(mxfile, "diagram", attrib={"name": "Thin Slicing", "id": "thin-slicing"})
        graph_model = ET.SubElement(diagram, "mxGraphModel")
        graph_root = ET.SubElement(graph_model, "root")
        ET.SubElement(graph_root, "mxCell", attrib={"id": "0"})
        ET.SubElement(graph_root, "mxCell", attrib={"id": "1", "parent": "0"})

        story_x: Dict[str, int] = {}
        for epic in canonical.epics:
            story_x.update(epic.story_xs())

        grid_width = (
            canonical.epics[-1].x + canonical.epics[-1].width - DiagramEpic.left_margin
            if canonical.epics else 200
        )

        for epic in canonical.epics:
            vertex = self._cell(epic.slug, epic.name)
            vertex.x = epic.x
            vertex.y = epic.y
            vertex.width = epic.width
            vertex.height = epic.height
            vertex.style = epic.style
            self._add_cell(graph_root, vertex)
            for sub_epic in epic.epics:
                sub_vertex = self._cell(sub_epic.cell_id, sub_epic.name)
                sub_vertex.x = sub_epic.x
                sub_vertex.y = sub_epic.y
                sub_vertex.width = sub_epic.bar_width
                sub_vertex.height = sub_epic.bar_height
                sub_vertex.style = sub_epic.style
                self._add_cell(graph_root, sub_vertex)

        lane_start_x = DiagramEpic.left_margin - DrawIOIncrement.label_width
        lane_total_width = DrawIOIncrement.label_width + grid_width
        lane_y = DrawIOIncrement.lane_top_y()
        for inc in canonical.increments:
            inc_slug = inc.slug if hasattr(inc, "slug") else Name(inc.name).title_slug or "node"
            # Background strip (no text).
            background = self._cell(f"inc-lane/{inc_slug}/bg", "")
            background.x = lane_start_x
            background.y = lane_y
            background.width = lane_total_width
            background.height = DrawIOIncrement.lane_height
            background.style = DrawIOIncrement.lane_style
            self._add_cell(graph_root, background)
            label = self._cell(f"inc-lane/{inc_slug}", inc.name)
            label.x = lane_start_x
            label.y = lane_y
            label.width = DrawIOIncrement.label_width - 4
            label.height = DrawIOIncrement.lane_height
            label.style = DrawIOIncrement.label_style
            self._add_cell(graph_root, label)
            for story in inc.stories:
                story_name = story.name
                x = story_x.get(story_name)
                if x is None:
                    continue
                story_vertex = self._cell(
                    f"inc-lane/{inc_slug}/{Name(story_name).title_slug or 'node'}",
                    story_name,
                )
                story_vertex.x = x
                story_vertex.y = lane_y + DrawIOIncrement.story_y_offset()
                story_vertex.width = DiagramStory.size
                story_vertex.height = DiagramStory.size
                story_vertex.style = DrawIOIncrement.story_style
                self._add_cell(graph_root, story_vertex)
            lane_y += DrawIOIncrement.lane_height + DrawIOIncrement.lane_gap

        body = ET.tostring(mxfile, encoding="unicode")
        return "<?xml version='1.0' encoding='utf-8'?>\n" + body

    def _read_thin_slice(self, text: str) -> List[DrawIOIncrement]:
        """Parse a thin-slicing.drawio document into increment nodes."""
        try:
            root_el = ET.fromstring(text)
        except ET.ParseError as err:
            raise DrawIOParseError(f"Not valid Draw.io XML: {err}") from err
        tree = root_el if root_el.tag == "mxGraphModel" else root_el.find(".//mxGraphModel")
        if tree is None:
            raise DrawIOParseError("No mxGraphModel found")

        # Build a map from inc_slug to increment so stories can be appended in
        # cell order regardless of document ordering.
        slug_to_inc: Dict[str, DrawIOIncrement] = {}
        increments: List[DrawIOIncrement] = []
        for cell in tree.findall(".//mxCell[@vertex='1']"):
            style = cell.attrib.get("style", "")
            value = cell.attrib.get("value", "")
            cell_id_attr = cell.attrib.get("id", "")
            if style.startswith("inc-lane-label;"):
                # Label cell carries the increment name; id = "inc-lane/{slug}"
                parts = cell_id_attr.split("/", 2)
                if len(parts) >= 2:
                    inc_slug = parts[1]
                    inc = DrawIOIncrement(value.strip(), len(increments) + 1)
                    slug_to_inc[inc_slug] = inc
                    increments.append(inc)
            elif style.startswith("increment-story;"):
                parts = cell_id_attr.split("/", 3)
                if len(parts) >= 3:
                    inc_slug = parts[1]
                    inc = slug_to_inc.get(inc_slug)
                    if inc is not None:
                        story = DrawIOStory(value.strip(), len(inc.stories) + 1)
                        story.increment = inc
                        inc.stories.append(story)
        return increments


    def _cell(self, cell_id, label) -> "DrawIOStoryModel.Vertex":
        vertex = self.Vertex()
        vertex.cell_id = cell_id
        vertex.label = label
        return vertex

    def _add_cell(self, graph_root, vertex):
        id_str = str(vertex.cell_id)
        attributes = {
            "id": id_str, "value": vertex.label, "style": vertex.style,
            "vertex": "1", "parent": "1",
        }
        if getattr(vertex, "link", ""):
            user = {"label": attributes.pop("value"), "link": vertex.link, "id": attributes.pop("id")}
            if vertex.entry and vertex.entry != vertex.link:
                user["entry"] = vertex.entry
            holder = ET.SubElement(graph_root, "UserObject", attrib=user)
            cell = ET.SubElement(holder, "mxCell", attrib=attributes)
        else:
            cell = ET.SubElement(graph_root, "mxCell", attrib=attributes)
        ET.SubElement(cell, "mxGeometry", attrib={
            "x": str(vertex.x), "y": str(vertex.y),
            "width": str(vertex.width), "height": str(vertex.height),
            "as": "geometry",
        })
        if isinstance(vertex.cell_id, int):
            return vertex.cell_id + 1
        return vertex.cell_id
