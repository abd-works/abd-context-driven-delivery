"""Miro format story nodes - all seven StoryNode subtypes plus I/O.

load reads a canvas-composer SVG. save writes the nodes you edited.
The thin-slice table is MiroStoryModel.save_thin_slice and load_thin_slice.
"""

from __future__ import annotations

import html
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from typing import Dict, Iterator, List, Optional, Tuple

from harness.whiteboard import Box

from cdd_guidance.practices.stories.model.diagram_story_model import (
    DiagramEpic,
    DiagramIncrement,
    DiagramStory,
    DiagramStoryModel,
    LaidOutEpic,
    LaidOutStory,
)
from cdd_guidance.practices.stories.model.story_model import Epic, Story, StoryModel, StoryType
from harness.guidance.practice_formats import Written

# Font sizes, corner radii, and stroke widths a Miro board draws each kind of card with.
_ACTOR_FONT_SIZE = 7
_STORY_FONT_SIZE = 8
_SUB_EPIC_FONT_SIZE = 10
_EPIC_FONT_SIZE = 11
_SUB_EPIC_CORNER = 4
_EPIC_CORNER = 6
_EPIC_STROKE_WIDTH = 2
# How much darker each level of sub-epic is drawn, and the most it darkens.
_DARKEN_PER_LEVEL = 12
_DARKEST = 40
# A thin-slice table's header row and each increment's row, and the room each column takes beyond a story card.
_TABLE_HEADER_HEIGHT = 60
_TABLE_ROW_HEIGHT = 40
_TABLE_COLUMN_PAD = 20


@dataclass
class _MiroShape:
    """One card a Miro story map draws: its box, colours, text, and the role its kind of node reads it back by."""

    id: str
    box: Box
    rx: int
    fill: str
    stroke: str
    stroke_width: int
    content: str
    role: str
    font_size: int
    actor: str = ""

    def svg_line(self) -> str:
        """The card as the SVG rect line a canvas-composer SVG holds it on, its words and actor escaped."""
        actor_attr = f' data-actor="{html.escape(self.actor, quote=True)}"' if self.actor else ""
        return (
            f'  <rect id="{self.id}" x="{self.box.x}" y="{self.box.y}" '
            f'width="{self.box.w}" height="{self.box.h}" rx="{self.rx}" '
            f'fill="{self.fill}" stroke="{self.stroke}" stroke-width="{self.stroke_width}" '
            f'data-content="{html.escape(self.content, quote=True)}" data-role="{self.role}" '
            f'data-font-size="{self.font_size}"{actor_attr} />'
        )



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


class MiroStory(LaidOutStory):
    """A Miro board reads at a coarser zoom than a DrawIO page, so story cards and
    their columns are larger here than the shared diagram geometry."""

    pitch = 72
    size = 60
    actor_height = size
    column_pad = 5

    def shapes(self, parent_id: str) -> List[_MiroShape]:
        parent = self.parent
        index = parent.stories.index(self) + 1 if isinstance(parent, Epic) else 1
        actor = self.actors[0].strip() if self.actors else ""
        story_id = f"{parent_id}/story-{index}-{self.slug}"
        shapes: List[_MiroShape] = []
        if actor and actor != self._previous_actor(index):
            shapes.append(self._actor_shape(story_id, actor))
        shapes.append(_MiroShape(
            id=story_id, box=Box(self.x, self.y, self.size, self.size), rx=0,
            fill=self.fill, stroke=self.stroke, stroke_width=1,
            content=self.name, role=f"story:{self.story_type.value}", font_size=_STORY_FONT_SIZE, actor=actor,
        ))
        return shapes

    def _previous_actor(self, index: int) -> str:
        """The actor of the story before this one under the same epic, whose card already names it; empty for none."""
        if not isinstance(self.parent, Epic) or index <= 1:
            return ""
        prior = self.parent.stories[index - 2]
        return prior.actors[0].strip() if prior.actors else ""

    def _actor_shape(self, story_id: str, actor: str) -> _MiroShape:
        return _MiroShape(
            id=f"{story_id}/actor", box=Box(self.x, self.y - self.actor_height - self.actor_gap, self.size, self.actor_height),
            rx=0, fill=self.actor_fill, stroke=self.actor_stroke, stroke_width=1,
            content=actor, role="actor", font_size=_ACTOR_FONT_SIZE,
        )


class MiroEpic(LaidOutEpic):
    """A nested epic is inset from its parent's left edge and sits flush with its
    right edge, so the nesting reads as a bar under the epic that owns it."""

    tighten = 10
    # A Miro epic starts at the map's margin, its sub-epics after the stories it holds itself.
    first_x = DiagramEpic.left_margin
    epic_spacing = DiagramEpic.gap
    story_pitch = MiroStory.pitch

    @property
    def fill(self) -> str:
        darken = min(self.depth * _DARKEN_PER_LEVEL, _DARKEST)
        red = int(DiagramEpic.nested_fill[1:3], 16)
        green = int(DiagramEpic.nested_fill[3:5], 16)
        blue = int(DiagramEpic.nested_fill[5:7], 16)
        if not isinstance(self.parent, Epic):
            return DiagramEpic.fill
        return f"#{max(red - darken, 0xa0):02x}{max(green - darken, 0xc0):02x}{max(blue - darken, 0xa0):02x}"

    def shapes(self, parent_id: str = "") -> List[_MiroShape]:
        if not isinstance(self.parent, Epic):
            return self._top_shapes()
        siblings = self.parent.epics if self.parent is not None else [self]
        index = siblings.index(self) + 1
        sub_epic_id = f"{parent_id}/sub-{index}-{self.slug}-d{self.depth}"
        shapes: List[_MiroShape] = [_MiroShape(
            id=sub_epic_id, box=Box(self.x + self.tighten, self.y, self.width - self.tighten, self.height),
            rx=_SUB_EPIC_CORNER, fill=self.fill, stroke=self.stroke, stroke_width=1,
            content=self.name, role=f"subepic:{self.depth}", font_size=_SUB_EPIC_FONT_SIZE,
        )]
        return shapes + self._children_shapes(sub_epic_id)

    def _top_shapes(self) -> List[_MiroShape]:
        index = self.parent.epics.index(self) + 1 if self.parent is not None else 1
        epic_id = f"epic-{index}-{self.slug}"
        shapes: List[_MiroShape] = [_MiroShape(
            id=epic_id, box=Box(self.x, self.y, self.width, self.height), rx=_EPIC_CORNER,
            fill=self.fill, stroke=self.stroke, stroke_width=_EPIC_STROKE_WIDTH,
            content=self.name, role="epic", font_size=_EPIC_FONT_SIZE,
        )]
        return shapes + self._children_shapes(epic_id)

    def _children_shapes(self, own_id: str) -> List[_MiroShape]:
        """The cards of its stories, then of its sub-epics, drawn under the card called own_id."""
        stories = [shape for story in self.stories for shape in story.shapes(own_id)]
        return stories + [shape for child in self.epics for shape in child.shapes(own_id)]


# -- Root node + I/O -----------------------------------------------------------

class MiroParseError(Exception):
    """Raised when the payload is not a valid Miro story map SVG."""


class _MiroReading:
    """One read of a canvas-composer SVG's cards into a new story map: the epic being read and the sub-epics open under
    it, so each card lands under the one above it."""

    def __init__(self, story_map: "MiroStoryModel") -> None:
        self.story_map = story_map
        self.epic: Optional[MiroEpic] = None
        self.sub_epics: List[MiroEpic] = []

    def read(self, element: ET.Element) -> None:
        role = element.get("data-role", "")
        label = element.get("data-content", "")
        if role == "epic":
            self.epic = MiroEpic(label, len(self.story_map.epics) + 1)
            self.story_map.epics.append(self.epic)
            self.sub_epics = []
            return
        if self.epic is None:
            return
        if role.startswith("subepic:"):
            self._sub_epic(label, int(role.split(":", 1)[1]))
            return
        if role.startswith("story:"):
            self._story(label, role, element.get("data-actor", "").strip())

    def _sub_epic(self, label: str, depth: int) -> None:
        while len(self.sub_epics) > depth:
            self.sub_epics.pop()
        owner = self.sub_epics[-1] if self.sub_epics else self.epic
        sub_epic = MiroEpic(label, len(owner.epics) + 1)
        owner.epics.append(sub_epic)
        self.sub_epics.append(sub_epic)

    def _story(self, label: str, role: str, actor: str) -> None:
        parent = self.sub_epics[-1] if self.sub_epics else self.epic
        story = MiroStory(label, len(parent.stories) + 1, StoryType.from_mark(role.split(":", 1)[1]))
        if actor:
            story.actors = [actor]
        parent.stories.append(story)


class MiroStoryModel(DiagramStoryModel):
    epic_type = MiroEpic
    story_type = MiroStory
    increment_type = MiroIncrement
    """Miro story-map I/O. IS the format-typed tree root.

    parse reads a file into these nodes. save writes the nodes you edited.
    The thin-slice table is save_thin_slice and load_thin_slice, over this map's own increments.
    """

    def render(self, canonical: StoryModel, written: Written = Written()) -> str:
        """Draw canonical as a Miro canvas-composer SVG."""
        return self.copy_of(canonical).save()

    def save_thin_slice(self) -> str:
        """This map's increments as a thin-slice table: one column per epic or sub-epic, one row per increment."""
        headers = ["Increment"]
        story_column: Dict[str, int] = {}
        for epic in self.epics:
            for header, stories in self._thin_slice_columns(epic):
                headers.append(header)
                story_column.update({story.name: len(headers) - 1 for story in stories})
        return self._thin_slice_svg(headers, story_column)

    def _thin_slice_columns(self, epic: Epic) -> List[Tuple[str, List[Story]]]:
        """The columns epic takes in a thin-slice table, each with the stories under it: one for its own stories, then
        one per sub-epic, or per innermost sub-epic of a sub-epic that has its own."""
        columns = [(epic.name, list(epic.stories))] if epic.stories else []
        for sub_epic in epic.epics:
            leaves = sub_epic.columns.leaf_epics()
            names = [f"{epic.name} / {sub_epic.name}"] if not sub_epic.epics else [f"{epic.name} / … / {leaf.name}" for leaf in leaves]
            columns.extend((name, list(leaf.stories)) for name, leaf in zip(names, leaves))
        return columns

    def _thin_slice_svg(self, headers: List[str], story_column: Dict[str, int]) -> str:
        header_cells = "".join(f"<th>{html.escape(header, quote=True)}</th>" for header in headers)
        rows = "\n        ".join(increment.table_row(len(headers), story_column) for increment in self.increments)
        table_width = MiroIncrement.label_width + (len(headers) - 1) * (MiroStory.pitch + _TABLE_COLUMN_PAD)
        table_height = _TABLE_HEADER_HEIGHT + len(self.increments) * _TABLE_ROW_HEIGHT
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
        foreign = self._foreign_object(self._svg_root(text), "table")
        if foreign is None:
            raise MiroParseError("No table foreignObject found in thin-slice SVG")
        body = next((element for element in foreign.iter() if self._local_name(element) == "tbody"), None)
        rows = [] if body is None else [row for row in body if self._local_name(row) == "tr"]
        increments: List[MiroIncrement] = []
        for row in rows:
            cells = [(cell.text or "").strip() for cell in row if self._local_name(cell) == "td"]
            if cells and cells[0]:
                increments.append(MiroIncrement(cells[0], len(increments) + 1, self.descendants.stories_named(cells[1:])))
        self.increments.refill(increments)
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
        return [shape.svg_line() for epic in self.epics for shape in epic.shapes()]

    def parse(self, text: str, file: str = "") -> "MiroStoryModel":
        """Read a canvas-composer SVG into a Miro story map; the format-adapter entry point Stories renders through."""
        tagged = list(self._cards_in_order(self._svg_root(text)))
        if not tagged:
            raise MiroParseError("No story-map nodes found in SVG (missing data-role attributes)")
        reading = _MiroReading(MiroStoryModel())
        for element in tagged:
            reading.read(element)
        return reading.story_map

    def _svg_root(self, text: str) -> ET.Element:
        try:
            return ET.fromstring(text.split("\n", 1)[1] if text.startswith("<?") else text)
        except ET.ParseError as err:
            raise MiroParseError(f"Not valid SVG: {err}") from err

    def _cards_in_order(self, element: ET.Element) -> Iterator[ET.Element]:
        """Each rect with a data-role under element, in document (depth-first) order."""
        for child in element:
            if self._local_name(child) == "rect" and child.get("data-role"):
                yield child
            yield from self._cards_in_order(child)

    def _local_name(self, element: ET.Element) -> str:
        tag = element.tag
        return tag.split("}")[-1] if "}" in tag else tag

    def _foreign_object(self, root_el: ET.Element, data_type: str) -> Optional[ET.Element]:
        for element in root_el.iter():
            if self._local_name(element) == "foreignObject" and element.get("data-type") == data_type:
                return element
        return None
