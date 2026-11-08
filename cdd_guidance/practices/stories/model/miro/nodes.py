"""Miro format story nodes - all seven StoryNode subtypes plus I/O.

load reads a canvas-composer SVG. save writes the nodes you edited.
The thin-slice table is MiroStoryModel.save_thin_slice and load_thin_slice.
"""

from __future__ import annotations

import html
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional

from cdd_guidance.practices.stories.model.diagram_story_model import (
    DiagramEpic,
    DiagramIncrement,
    DiagramStory,
    DiagramStoryModel,
)
from cdd_guidance.practices.stories.model.story_model import Epic, StoryModel, StoryType


class MiroIncrement(DiagramIncrement):
    def table_row(self, column_count: int, story_column: Dict[str, int]) -> str:
        cells = [""] * column_count
        cells[0] = self.name
        for story in self.stories:
            column = story_column.get(story.name)
            if column is not None and column < column_count:
                cells[column] = story.name
        return "<tr>" + "".join(
            f"<td>{html.escape(cell, quote=True)}</td>" for cell in cells
        ) + "</tr>"

class MiroStory(DiagramStory):
    """A Miro board reads at a coarser zoom than a DrawIO page, so story cards and
    their columns are larger here than the shared diagram geometry."""

    pitch = 72
    size = 60
    actor_height = size
    column_pad = 5

    @property
    def x(self) -> int:
        parent = self.parent
        if not isinstance(parent, Epic):
            return 0
        index = parent.stories.index(self)
        return parent.x + MiroEpic.tighten + self.column_pad + index * self.pitch

    @property
    def y(self) -> int:
        return self._story_line_y()

    def shapes(self, parent_id: str) -> List[dict]:
        parent = self.parent
        index = parent.stories.index(self) + 1 if isinstance(parent, Epic) else 1
        actor = self.actors[0].strip() if self.actors else ""
        previous = ""
        if isinstance(parent, Epic) and index > 1:
            prior = parent.stories[index - 2]
            previous = prior.actors[0].strip() if prior.actors else ""
        story_id = f"{parent_id}/story-{index}-{self.slug}"
        shapes: List[dict] = []
        if actor and actor != previous:
            shapes.append({
                "id": f"{story_id}/actor",
                "x": self.x,
                "y": self.y - self.actor_height - self.actor_gap,
                "w": self.size, "h": self.actor_height, "rx": 0,
                "fill": self.actor_fill, "stroke": self.actor_stroke, "stroke_width": 1,
                "content": actor, "role": "actor", "font_size": 7,
            })
        shapes.append({
            "id": story_id,
            "x": self.x, "y": self.y,
            "w": self.size, "h": self.size, "rx": 0,
            "fill": self.fill, "stroke": self.stroke, "stroke_width": 1,
            "content": self.name,
            "role": f"story:{self.story_type.value}",
            "font_size": 8,
            "actor": actor,
        })
        return shapes


class MiroEpic(DiagramEpic):
    """A nested epic is inset from its parent's left edge and sits flush with its
    right edge, so the nesting reads as a bar under the epic that owns it."""

    tighten = 10

    @property
    def width(self) -> int:
        if isinstance(self.parent, Epic):
            return max(self.diagram_span_columns(), 1) * MiroStory.pitch
        return self.span_columns() * MiroStory.pitch

    @property
    def height(self) -> int:
        return self.bar_height

    @property
    def y(self) -> int:
        if isinstance(self.parent, Epic):
            return self._sub_epic_bar_y(self.depth)
        return self.row_y

    @property
    def x(self) -> int:
        parent = self.parent
        if isinstance(parent, Epic):
            origin = parent.x + len(parent.stories) * MiroStory.pitch
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
    def fill(self) -> str:
        darken = min(self.depth * 12, 40)
        red = int(DiagramEpic.nested_fill[1:3], 16)
        green = int(DiagramEpic.nested_fill[3:5], 16)
        blue = int(DiagramEpic.nested_fill[5:7], 16)
        if not isinstance(self.parent, Epic):
            return DiagramEpic.fill
        return f"#{max(red - darken, 0xa0):02x}{max(green - darken, 0xc0):02x}{max(blue - darken, 0xa0):02x}"

    def leaves(self) -> List["MiroEpic"]:
        if not self.epics:
            return [self]
        found: List[MiroEpic] = []
        for child in self.epics:
            found.extend(child.leaves())
        return found

    def shapes(self, parent_id: str = "") -> List[dict]:
        if not isinstance(self.parent, Epic):
            return self._top_shapes()
        siblings = self.parent.epics if self.parent is not None else [self]
        index = siblings.index(self) + 1
        sid = f"{parent_id}/sub-{index}-{self.slug}-d{self.depth}"
        shapes: List[dict] = [{
            "id": sid, "x": self.x + self.tighten, "y": self.y,
            "w": self.width - self.tighten, "h": self.height, "rx": 4,
            "fill": self.fill, "stroke": self.stroke, "stroke_width": 1,
            "content": self.name, "role": f"subepic:{self.depth}", "font_size": 10,
        }]
        for story in self.stories:
            shapes.extend(story.shapes(sid))
        for child in self.epics:
            shapes.extend(child.shapes(sid))
        return shapes

    def _top_shapes(self) -> List[dict]:
        index = self.parent.epics.index(self) + 1 if self.parent is not None else 1
        eid = f"epic-{index}-{self.slug}"
        shapes: List[dict] = [{
            "id": eid, "x": self.x, "y": self.y,
            "w": self.width, "h": self.height, "rx": 6,
            "fill": self.fill, "stroke": self.stroke, "stroke_width": 2,
            "content": self.name, "role": "epic", "font_size": 11,
        }]
        for story in self.stories:
            shapes.extend(story.shapes(eid))
        for child in self.epics:
            shapes.extend(child.shapes(eid))
        return shapes


# -- Root node + I/O -----------------------------------------------------------

class MiroParseError(Exception):
    """Raised when the payload is not a valid Miro story map SVG."""


class MiroStoryModel(DiagramStoryModel):
    epic_type = MiroEpic
    story_type = MiroStory
    increment_type = MiroIncrement
    """Miro story-map I/O. IS the format-typed tree root.

    load reads a file into these nodes. save writes the nodes you edited.
    The thin-slice table is save_thin_slice and load_thin_slice, over this map's own increments.
    """

    def render(self, canonical: StoryModel | None = None, previous: str | None = None) -> str:
        """Draw canonical, or this story map when none is given, as a Miro canvas-composer SVG."""
        return type(self)(canonical if canonical is not None else self).save()

    def parse(self, text: str) -> "MiroStoryModel":
        """Read a canvas-composer SVG into a Miro story map; the format-adapter entry point Stories renders through."""
        return self.load(text)

    def save_thin_slice(self) -> str:
        """This map's increments as a thin-slice table: one column per epic or sub-epic, one row per increment."""
        headers = ["Increment"]
        story_column: Dict[str, int] = {}
        column = 1
        for epic in self.epics:
            if epic.stories:
                headers.append(epic.name)
                for story in epic.stories:
                    story_column[story.name] = column
                column += 1
            for sub_epic in epic.epics:
                leaves = sub_epic.leaves()
                if not sub_epic.epics:
                    headers.append(f"{epic.name} / {sub_epic.name}")
                else:
                    for leaf in leaves:
                        headers.append(f"{epic.name} / … / {leaf.name}")
                for leaf in leaves:
                    for story in leaf.stories:
                        story_column[story.name] = column
                    column += 1
        return self._thin_slice_svg(headers, story_column)

    def _thin_slice_svg(self, headers: List[str], story_column: Dict[str, int]) -> str:
        header_cells = "".join(f"<th>{html.escape(header, quote=True)}</th>" for header in headers)
        rows = "\n        ".join(increment.table_row(len(headers), story_column) for increment in self.increments)
        table_width = MiroIncrement.label_width + (len(headers) - 1) * (MiroStory.pitch + 20)
        table_height = 60 + len(self.increments) * 40
        table = (
            f'<foreignObject id="thin-slice-table" x="0" y="0" '
            f'width="{table_width}" height="{table_height}" '
            f'data-type="table" data-title="Thin Slicing">'
            f"<table><thead><tr>{header_cells}</tr></thead>"
            f"<tbody>\n        {rows}\n      </tbody></table>"
            f"</foreignObject>"
        )
        return "<?xml version='1.0' encoding='utf-8'?>\n" '<svg xmlns="http://www.w3.org/2000/svg">\n' f"  {table}\n" "</svg>"

    def load_thin_slice(self, text: str) -> "MiroStoryModel":
        """Read a thin-slice table into this map's increments, each delivering the map's own stories its row names,
        and return this map."""
        try:
            root_el = ET.fromstring(text.split("\n", 1)[1] if text.startswith("<?") else text)
        except ET.ParseError as err:
            raise MiroParseError(f"Not valid SVG: {err}") from err
        foreign = _foreign_object(root_el, "table")
        if foreign is None:
            raise MiroParseError("No table foreignObject found in thin-slice SVG")
        body = next((element for element in foreign.iter() if _local_name(element) == "tbody"), None)
        rows = [] if body is None else [row for row in body if _local_name(row) == "tr"]
        stories = {story.name: story for story in self.every_story()}
        increments: List[MiroIncrement] = []
        for row in rows:
            cells = [(cell.text or "").strip() for cell in row if _local_name(cell) == "td"]
            if cells and cells[0]:
                delivered = [stories[name] for name in cells[1:] if name in stories]
                increments.append(MiroIncrement(cells[0], len(increments) + 1, delivered))
        self.increments = increments
        return self

    def save(self) -> str:
        """Write this story map's nodes as a Miro canvas-composer SVG."""
        lines = self._build_rect_lines()
        body = "\n".join(lines)
        return (
            "<?xml version='1.0' encoding='utf-8'?>\n"
            '<svg xmlns="http://www.w3.org/2000/svg">\n'
            + body
            + "\n</svg>"
        )

    def _build_rect_lines(self) -> List[str]:
        """One SVG rect line per epic, sub-epic, story, and actor. Each node places itself."""
        return [self._shape_to_svg_line(shape) for epic in self.epics for shape in epic.shapes()]

    def _shape_to_svg_line(self, s: dict) -> str:
        actor = s.get("actor", "")
        actor_attr = f' data-actor="{self._xe(actor)}"' if actor else ""
        return (
            f'  <rect id="{s["id"]}" x="{s["x"]}" y="{s["y"]}" '
            f'width="{s["w"]}" height="{s["h"]}" rx="{s["rx"]}" '
            f'fill="{s["fill"]}" stroke="{s["stroke"]}" stroke-width="{s["stroke_width"]}" '
            f'data-content="{self._xe(s["content"])}" data-role="{s["role"]}" '
            f'data-font-size="{s["font_size"]}"{actor_attr} />'
        )

    def load(self, text: str) -> "MiroStoryModel":
        """Read a canvas-composer SVG into a Miro story map."""
        try:
            root_el = ET.fromstring(
                text.split("\n", 1)[1] if text.startswith("<?") else text
            )
        except ET.ParseError as err:
            raise MiroParseError(f"Not valid SVG: {err}") from err

        def _all_rects_in_order(el: ET.Element):
            """Yield rect elements with data-role in document (DFS) order."""
            for child in el:
                tag = child.tag.split("}")[-1] if "}" in child.tag else child.tag
                if tag == "rect" and child.get("data-role"):
                    yield child
                yield from _all_rects_in_order(child)

        tagged = list(_all_rects_in_order(root_el))

        if not tagged:
            raise MiroParseError("No story-map nodes found in SVG (missing data-role attributes)")

        story_map = MiroStoryModel()
        current_epic: MiroEpic | None = None
        current_sub_epic_stack: List[MiroEpic] = []

        for el in tagged:
            role = el.get("data-role", "")
            label = el.get("data-content", "")
            if role == "epic":
                current_epic = MiroEpic(label, len(story_map.epics) + 1)
                story_map.append_epic(current_epic)
                current_sub_epic_stack = []
            elif role.startswith("subepic:") and current_epic is not None:
                depth = int(role.split(":", 1)[1])
                while len(current_sub_epic_stack) > depth:
                    current_sub_epic_stack.pop()
                owner = current_sub_epic_stack[-1] if current_sub_epic_stack else current_epic
                sub_epic = MiroEpic(label, len(owner.epics) + 1)
                owner.append_epic(sub_epic)
                current_sub_epic_stack.append(sub_epic)
            elif role.startswith("story:") and current_epic is not None:
                parent = current_sub_epic_stack[-1] if current_sub_epic_stack else current_epic
                story = MiroStory(label, len(parent.stories) + 1, StoryType.from_mark(role.split(":", 1)[1]))
                actor = el.get("data-actor", "").strip()
                if actor:
                    story.actors = [actor]
                parent.append_story(story)

        return story_map

    # -- Thin-slice view -------------------------------------------------------

    # -- Private helpers -------------------------------------------------------

    def _xe(self, value: str) -> str:
        """XML-escape a string for use in SVG attributes and text."""
        return html.escape(value, quote=True)


def _local_name(element: ET.Element) -> str:
    tag = element.tag
    return tag.split("}")[-1] if "}" in tag else tag


def _foreign_object(root_el: ET.Element, data_type: str) -> Optional[ET.Element]:
    for element in root_el.iter():
        if _local_name(element) == "foreignObject" and element.get("data-type") == data_type:
            return element
    return None
