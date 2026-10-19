"""Miro format story nodes - all seven StoryNode subtypes plus I/O.

load reads a canvas-composer SVG. save writes the nodes you edited.
The thin-slice table is MiroIncrement.save and MiroIncrement.load.
upload posts each node's shapes to a Miro board.
"""

from __future__ import annotations

import html
import re
import time
import xml.etree.ElementTree as ET
from typing import Callable, Dict, List, Optional

from practices.stories.model.diagram_story_model import (
    DiagramEpic,
    DiagramIncrement,
    DiagramStory,
    DiagramStoryModel,
    DiagramEpic,
)
from practices.stories.model.story_model import Epic, StoryModel, StoryType, Epic


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

    @classmethod
    def from_cells(cls, cells: List[str], order: int) -> Optional["MiroIncrement"]:
        if not cells:
            return None
        name = cells[0].strip()
        if not name:
            return None
        increment = cls(name, order)
        for story_name in cells[1:]:
            story_name = story_name.strip()
            if not story_name:
                continue
            story = MiroStory(story_name, len(increment.stories) + 1)
            story.increment = increment
            increment.stories.append(story)
        return increment

    @classmethod
    def save(cls, story_map: StoryModel) -> str:
        headers = ["Increment"]
        story_column: Dict[str, int] = {}
        column = 1
        for epic in story_map.epics:
            for sub_epic in epic.epics:
                leaves = sub_epic.leaves()
                if not sub_epic.epics:
                    headers.append(f"{epic.name} / {sub_epic.name}")
                else:
                    for leaf in leaves:
                        headers.append(f"{epic.name} / â€¦ / {leaf.name}")
                for leaf in leaves:
                    for story in leaf.stories:
                        story_column[story.name] = column
                    column += 1
        header_cells = "".join(f"<th>{html.escape(header, quote=True)}</th>" for header in headers)
        rows = "\n        ".join(
            increment.table_row(len(headers), story_column) for increment in story_map.increments
        )
        column_count = len(headers)
        table_width = cls.label_width + (column_count - 1) * (MiroStory.pitch + 20)
        table_height = 60 + len(story_map.increments) * 40
        table = (
            f'<foreignObject id="thin-slice-table" x="0" y="0" '
            f'width="{table_width}" height="{table_height}" '
            f'data-type="table" data-title="Thin Slicing">'
            f"<table><thead><tr>{header_cells}</tr></thead>"
            f"<tbody>\n        {rows}\n      </tbody></table>"
            f"</foreignObject>"
        )
        return (
            "<?xml version='1.0' encoding='utf-8'?>\n"
            '<svg xmlns="http://www.w3.org/2000/svg">\n'
            f"  {table}\n"
            "</svg>"
        )

    @classmethod
    def load(cls, text: str) -> List["MiroIncrement"]:
        try:
            root_el = ET.fromstring(text.split("\n", 1)[1] if text.startswith("<?") else text)
        except ET.ParseError as err:
            raise MiroParseError(f"Not valid SVG: {err}") from err
        foreign = cls._foreign_object(root_el, "table")
        if foreign is None:
            raise MiroParseError("No table foreignObject found in thin-slice SVG")
        body = None
        for element in foreign.iter():
            if cls._local_name(element) == "tbody":
                body = element
                break
        if body is None:
            return []
        increments: List[MiroIncrement] = []
        for row in body:
            if cls._local_name(row) != "tr":
                continue
            cells = [
                cell.text or "" for cell in row if cls._local_name(cell) == "td"
            ]
            increment = cls.from_cells(cells, len(increments) + 1)
            if increment is not None:
                increments.append(increment)
        return increments

    @staticmethod
    def _local_name(element: ET.Element) -> str:
        tag = element.tag
        return tag.split("}")[-1] if "}" in tag else tag

    @classmethod
    def _foreign_object(cls, root_el: ET.Element, data_type: str) -> Optional[ET.Element]:
        for element in root_el.iter():
            if cls._local_name(element) == "foreignObject" and element.get("data-type") == data_type:
                return element
        return None


class MiroStory(DiagramStory):
    """A Miro board reads at a coarser zoom than a DrawIO page, so story cards and
    their columns are larger here than the shared diagram geometry."""

    pitch = 72
    size = 60
    actor_height = size
    column_pad = 5

    @property
    def slug(self) -> str:
        slug = re.sub(r"[^a-z0-9]+", "-", self.name.lower()).strip("-")
        return slug or "node"

    @property
    def x(self) -> int:
        parent = self.parent
        if not isinstance(parent, Epic):
            return 0
        index = parent.stories.index(self)
        return parent.x + MiroEpic.tighten + self.column_pad + index * self.pitch

    @property
    def y(self) -> int:
        story_map = self._owning_map()
        depth = story_map.max_sub_epic_depth if isinstance(story_map, DiagramStoryModel) else 0
        deepest_bottom = (
            DiagramEpic.row_y
            + depth * (DiagramEpic.bar_height + DiagramEpic.depth_gap)
            + DiagramEpic.bar_height
        )
        return max(
            self.row_y,
            deepest_bottom + self.actor_height + self.actor_gap + self.pad_below_sub_epic,
        )

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

    @classmethod
    def fills(cls) -> set:
        return {DiagramStory.fill, DiagramStory.actor_fill}


class MiroEpic(DiagramEpic):
    """A nested epic is inset from its parent's left edge and sits flush with its
    right edge, so the nesting reads as a bar under the epic that owns it."""

    tighten = 10

    @property
    def slug(self) -> str:
        slug = re.sub(r"[^a-z0-9]+", "-", self.name.lower()).strip("-")
        return slug or "node"

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
            return self.nested_row_y + self.depth * (self.bar_height + self.depth_gap)
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

    @classmethod
    def fills(cls) -> set:
        painted = set()
        red = int(DiagramEpic.nested_fill[1:3], 16)
        green = int(DiagramEpic.nested_fill[3:5], 16)
        blue = int(DiagramEpic.nested_fill[5:7], 16)
        for depth in range(8):
            darken = min(depth * 12, 40)
            painted.add(
                f"#{max(red - darken, 0xa0):02x}{max(green - darken, 0xc0):02x}{max(blue - darken, 0xa0):02x}"
            )
        painted.add(DiagramEpic.fill)
        return painted

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
    The thin-slice table is MiroIncrement.save and MiroIncrement.load.
    """

    # -- Uniform Callable Surface ----------------------------------------------

    def clone(self):
        return super().clone().save()

    def save(self) -> str:
        """Write this story map's nodes as a Miro canvas-composer SVG."""
        lines = self._build_rect_lines(self)
        body = "\n".join(lines)
        return (
            "<?xml version='1.0' encoding='utf-8'?>\n"
            '<svg xmlns="http://www.w3.org/2000/svg">\n'
            + body
            + "\n</svg>"
        )

    def render_chunks(self, canonical: "MiroStoryModel", chunk_size: int = 80) -> List[str]:
        """Render story-map SVG as a list of valid SVG chunks for incremental Miro upload.

        Each chunk is self-contained and has at most chunk_size rect elements.
        Attribute values use single quotes to avoid JSON escaping issues when
        passing SVG strings to canvas_create_from_svg via MCP tool calls.

        Usage: call canvas_create_from_svg(is_repository=True, svg=chunk) for
        each returned chunk in sequence.
        """
        lines = self._build_rect_lines(canonical)
        lines_sq = [re.sub(r'="([^"]*)"', r"='\1'", line) for line in lines]
        header = "<?xml version='1.0' encoding='utf-8'?>\n<svg xmlns='http://www.w3.org/2000/svg'>"
        footer = "</svg>"
        chunks = []
        for i in range(0, len(lines_sq), chunk_size):
            body = "\n".join(lines_sq[i:i + chunk_size])
            chunks.append(f"{header}\n{body}\n{footer}")
        return chunks

    def render_api_shapes(self, canonical: "MiroStoryModel") -> List[dict]:
        """Return a flat list of shape descriptors for direct Miro REST API upload.

        Each dict has: id, x, y, w, h, rx, fill, stroke, stroke_width,
        content, role, font_size â€” all in SVG-coordinate space.
        upload converts those top-left boxes to Miro centre coordinates.
        """
        return self._build_shape_dicts(canonical)

    def upload(
        self,
        board_id: str,
        client,
        scale: float = 1.5,
        origin_x: float = 0.0,
        origin_y: float = 6000.0,
        delay_ms: int = 350,
        on_progress: Optional[Callable] = None,
    ) -> Dict[str, object]:
        """Post this map's shapes to a Miro board.

        SVG layout uses a top-left origin. Miro places a shape by its centre.
        ``delay_ms`` pauses between calls so the board stays under 200 requests a minute.
        """
        shapes = self.render_api_shapes(self)
        total = len(shapes)
        id_map: Dict[str, str] = {}
        for index, shape in enumerate(shapes):
            centre_x, centre_y, width, height, font_size = self._board_box(shape, scale, origin_x, origin_y)
            result = client.create_shape(
                board_id=board_id,
                x=centre_x, y=centre_y, w=width, h=height,
                fill=shape["fill"],
                stroke=shape["stroke"],
                stroke_width=shape["stroke_width"],
                content=shape["content"],
                rx=shape.get("rx", 0),
                font_size=font_size,
            )
            id_map[shape["id"]] = result["id"]
            if on_progress is not None:
                on_progress(index + 1, total)
            if delay_ms > 0 and index < total - 1:
                time.sleep(delay_ms / 1000)
        return {
            "board_id": board_id,
            "shape_count": len(id_map),
            "scale": scale,
            "origin": {"x": origin_x, "y": origin_y},
            "ids": id_map,
        }

    def clear(self, board_id: str, client, miro_ids: List[str], delay_ms: int = 350) -> int:
        """Delete shapes by Miro id. Returns the count deleted."""
        count = 0
        for miro_id in miro_ids:
            client.delete_shape(board_id, miro_id)
            count += 1
            if delay_ms > 0 and count < len(miro_ids):
                time.sleep(delay_ms / 1000)
        return count

    def clear_story_map(self, board_id: str, client, delay_ms: int = 350) -> int:
        """Delete story-map shapes on the board, matched by the fills these nodes paint."""
        paints = {fill.lower() for fill in MiroEpic.fills() | MiroEpic.fills() | MiroStory.fills()}
        to_delete: List[str] = []
        for shape in client.list_shapes(board_id):
            fill = shape.get("style", {}).get("fillColor", "").lower()
            if fill in paints:
                to_delete.append(shape["id"])
        return self.clear(board_id, client, to_delete, delay_ms)

    def _board_box(self, shape: dict, scale: float, origin_x: float, origin_y: float):
        centre_x = (shape["x"] + shape["w"] / 2) * scale + origin_x
        centre_y = (shape["y"] + shape["h"] / 2) * scale + origin_y
        width = shape["w"] * scale
        height = shape["h"] * scale
        font_size = max(8, round(shape.get("font_size", 12) * scale * 0.5))
        return centre_x, centre_y, width, height, font_size

    def _build_shape_dicts(self, canonical: "MiroStoryModel") -> List[dict]:
        """One shape dict per epic, sub-epic, and story. Each node places itself."""
        shapes: List[dict] = []
        for epic in canonical.epics:
            shapes.extend(epic.shapes())
        return shapes

    def _build_rect_lines(self, canonical: "MiroStoryModel") -> List[str]:
        """Build the flat list of SVG rect lines for the full story map."""
        return [self._shape_to_svg_line(s) for s in self._build_shape_dicts(canonical)]

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
            elif role.startswith("story:") and current_sub_epic_stack:
                parent = current_sub_epic_stack[-1]
                story = MiroStory(label, len(parent.stories) + 1, StoryType.USER)
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
