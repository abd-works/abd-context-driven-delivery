"""DrawIO format story nodes - all seven StoryNode subtypes plus I/O.

Two views:
- story-map  render(canonical)            - Epic -> Epic -> Story grid
- thin-slice DrawIOIncrement.save / DrawIOIncrement.load - increment rows across epic columns
"""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional

from practices.stories.model.diagram_story_model import (
    DiagramEpic,
    DiagramIncrement,
    DiagramStory,
    DiagramStoryMap,
    DiagramEpic,
)
from practices.stories.model.story_model import Epic, Increment, StoryMap, StoryType, Epic


class DrawIOIncrement(DiagramIncrement):
    width = 480
    lane_indent = 40
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
    def save(cls, story_map: StoryMap) -> str:
        return DrawIOStoryMap()._write_thin_slice(story_map)

    @classmethod
    def load(cls, text: str) -> List["DrawIOIncrement"]:
        return DrawIOStoryMap()._read_thin_slice(text)


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
        slug = re.sub(r"[^a-z0-9]+", "-", self.name.lower()).strip("-")
        return slug or "node"

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
        depth = story_map.max_sub_epic_depth if isinstance(story_map, DiagramStoryMap) else 0
        shaping = isinstance(story_map, DrawIOStoryMap) and story_map.has_outline_estimates
        base = DrawIOEpic.shaping_row_y if shaping else DrawIOEpic.row_y
        deepest_bottom = base + depth * (DrawIOEpic.bar_height + DrawIOEpic.depth_gap) + DrawIOEpic.bar_height
        if shaping:
            return max(self.shaping_row_y, deepest_bottom + self.pad_below_sub_epic)
        return max(
            self.row_y,
            deepest_bottom + self.actor_height + self.actor_gap + self.pad_below_sub_epic,
        )

    def cells(self, parent_id: str) -> List["DrawIOStoryMap.Vertex"]:
        parent = self.parent
        index = parent.stories.index(self) if isinstance(parent, Epic) else 0
        actor = self.actors[0].strip() if self.actors else ""
        previous = ""
        if isinstance(parent, Epic) and index > 0:
            prior = parent.stories[index - 1]
            previous = prior.actors[0].strip() if prior.actors else ""
        cell_id = f"{parent_id}/{self.cell_slug}"
        drawn: List[DrawIOStoryMap.Vertex] = []
        room = (
            self.y >= parent.y + DrawIOEpic.bar_height + self.actor_height + self.actor_gap
            if isinstance(parent, Epic) else False
        )
        if room and actor and actor != previous:
            drawn.append(DrawIOStoryMap.Vertex.make(
                f"{cell_id}/actor", actor, self.x,
                self.y - self.actor_height - self.actor_gap,
                self.size, self.actor_height, self.actor_style,
            ))
        drawn.append(DrawIOStoryMap.Vertex.make(
            cell_id, self.name, self.x, self.y, self.size, self.size,
            self.style.format(role=self.story_type.value),
        ))
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
        slug = re.sub(r"[^a-z0-9]+", "-", self.name.lower()).strip("-")
        return slug or "node"

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
        shaping = isinstance(story_map, DrawIOStoryMap) and story_map.has_outline_estimates
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

    def cells(self) -> List["DrawIOStoryMap.Vertex"]:
        if not isinstance(self.parent, Epic):
            return self._epic_cells()
        drawn = [DrawIOStoryMap.Vertex.make(
            self.cell_id, self.name, self.x, self.y, self.bar_width, self.bar_height, self.style,
        )]
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
            drawn.append(DrawIOStoryMap.Vertex.make(
                f"{self.cell_id}/estimate", label, estimate_x, self.stories[0].y if self.stories else self._story_row(),
                max(self.bar_width - (estimate_x - self.x) - self.tighten, 80),
                DiagramStory.size, self.estimate_style,
            ))
        return drawn

    def _epic_cells(self) -> List["DrawIOStoryMap.Vertex"]:
        drawn = [DrawIOStoryMap.Vertex.make(
            self.cell_id, self.name, self.x, self.y, self.width, self.height, self.style,
        )]
        estimate = (self.estimate or "").strip()
        if estimate:
            label = self.estimate_label()
            drawn.append(DrawIOStoryMap.Vertex.make(
                f"{self.cell_id}/epic-estimate", label, self.x, self.estimate_row_y,
                min(160, self.width), self.estimate_height, self.epic_estimate_style,
            ))
        for child in self.epics:
            drawn.extend(child.cells())
        return drawn

    def _story_row(self) -> int:
        story_map = self._owning_map()
        depth = story_map.max_sub_epic_depth if isinstance(story_map, DiagramStoryMap) else 0
        shaping = isinstance(story_map, DrawIOStoryMap) and story_map.has_outline_estimates
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


class DrawIOStoryMap(DiagramStoryMap):
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
            self.extra_attributes = None

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


    def _parse_estimate_value(self, value: str) -> str:
        plain = re.sub(r"<[^>]+>", "", value)
        return plain.strip().removeprefix("*").strip()



    # -- Uniform Callable Surface ----------------------------------------------

    @property
    def has_outline_estimates(self) -> bool:
        return any(epic._has_estimate() for epic in self.epics)

    def clone(self):
        return super().clone().save()

    def save(self) -> str:
        mxfile = ET.Element("mxfile", attrib={"host": "app.diagrams.net"})
        diagram = ET.SubElement(mxfile, "diagram", attrib={"name": "Story Map", "id": "story-map"})
        graph_model = ET.SubElement(diagram, "mxGraphModel")
        graph_root = ET.SubElement(graph_model, "root")
        ET.SubElement(graph_root, "mxCell", attrib={"id": "0"})
        ET.SubElement(graph_root, "mxCell", attrib={"id": "1", "parent": "0"})
        for epic in self.epics:
            for vertex in epic.cells():
                self._add_cell(graph_root, vertex)
        body = ET.tostring(mxfile, encoding="unicode")
        return "<?xml version='1.0' encoding='utf-8'?>\n" + body

    def load(self, text: str) -> "DrawIOStoryMap":
        try:
            root_el = ET.fromstring(text)
        except ET.ParseError as err:
            raise DrawIOParseError(f"Not valid Draw.io XML: {err}") from err
        if root_el.tag == "mxfile":
            tree = root_el.find(".//mxGraphModel")
            if tree is None:
                raise DrawIOParseError("mxfile has no mxGraphModel child")
        elif root_el.tag == "mxGraphModel":
            tree = root_el
        else:
            raise DrawIOParseError("Root element must be <mxGraphModel>")

        cells = tree.findall(".//mxCell[@vertex='1']")
        story_map = DrawIOStoryMap()
        current_epic: DrawIOEpic | None = None
        current_sub_epic_stack: List[DrawIOEpic] = []
        current_actor = ""

        for cell in cells:
            style = cell.attrib.get("style", "")
            value = cell.attrib.get("value", "")
            role = style.split(";", 1)[0]
            if role == "epic":
                current_epic = DrawIOEpic(value.strip(), len(story_map.epics) + 1)
                story_map.append_epic(current_epic)
                current_sub_epic_stack = []
                current_actor = ""
            elif style.startswith("subepic") and current_epic is not None:
                depth = int(style.split(":", 1)[1].split(";", 1)[0]) if ":" in style else 0
                while len(current_sub_epic_stack) > depth:
                    current_sub_epic_stack.pop()
                owner = current_sub_epic_stack[-1] if current_sub_epic_stack else current_epic
                sub_epic = DrawIOEpic(value, len(owner.epics) + 1)
                owner.append_epic(sub_epic)
                current_sub_epic_stack.append(sub_epic)
                current_actor = ""
            elif style.startswith("actor") and current_sub_epic_stack:
                current_actor = value.strip()
            elif style.startswith("story") and current_sub_epic_stack:
                parent = current_sub_epic_stack[-1]
                story = DrawIOStory(value, len(parent.stories) + 1, StoryType.USER)
                if current_actor:
                    story.actors = [current_actor]
                parent.append_story(story)
            elif style.startswith("text") and current_epic is not None and not current_sub_epic_stack:
                estimate = self._parse_estimate_value(value)
                if estimate and ("approx" in estimate.lower() or value.strip().startswith("*")):
                    current_epic.estimate = estimate
            elif style.startswith("estimate") and current_epic is not None:
                estimate = self._parse_estimate_value(value)
                cell_id = cell.attrib.get("id", "")
                if cell_id.endswith("/epic-estimate") or (
                    cell_id.endswith("/estimate") and cell_id.count("/") == 1
                ):
                    current_epic.estimate = estimate
                elif current_sub_epic_stack:
                    current_sub_epic_stack[-1].estimate = estimate

        return story_map

    # -- Thin-slice view -------------------------------------------------------

    def _write_thin_slice(self, canonical: StoryMap) -> str:
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
            for sub_epic in epic.epics:
                story_x.update(sub_epic.story_xs())

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
            inc_slug = inc.slug if hasattr(inc, "slug") else re.sub(r"[^a-z0-9]+", "-", inc.name.lower()).strip("-") or "node"
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
                    f"inc-lane/{inc_slug}/{re.sub(r'[^a-z0-9]+', '-', story_name.lower()).strip('-') or 'node'}",
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


    def _new_document(self):
        root = ET.Element("mxGraphModel")
        graph_root = ET.SubElement(root, "root")
        ET.SubElement(graph_root, "mxCell", attrib={"id": "0"})
        ET.SubElement(graph_root, "mxCell", attrib={"id": "1", "parent": "0"})
        return root, graph_root, 2

    def _cell(self, cell_id, label) -> "DrawIOStoryMap.Vertex":
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
        if vertex.extra_attributes:
            attributes.update(vertex.extra_attributes)
        cell = ET.SubElement(graph_root, "mxCell", attrib=attributes)
        ET.SubElement(cell, "mxGeometry", attrib={
            "x": str(vertex.x), "y": str(vertex.y),
            "width": str(vertex.width), "height": str(vertex.height),
            "as": "geometry",
        })
        if isinstance(vertex.cell_id, int):
            return vertex.cell_id + 1
        return vertex.cell_id
