"""DrawIO format story nodes — all seven StoryNode subtypes plus I/O.

Three views:
- story-map  render(canonical)            — Epic → SubEpic → Story grid
- thin-slice render_thin_slice(canonical) — increment lanes overlaid on map
- scenario   render_scenario(canonical)   — Story + Scenario + Clause cells
"""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional

from stories.src.stories.model.nodes import Epic, Story, StoryType, SubEpic
from stories.src.stories.model.scenario import Scenario
from stories.src.stories.model.story_map import StoryMap
from stories.src.stories.model.thin_slice import Increment
from stories.src.stories.model.update_report import UpdateReport
from stories.src.stories.diagram.diagram_story_map import (
    BASE_WIDTH, ROW_HEIGHT, DiagramStoryMap,
)

CLAUSE_HEIGHT = 40
CLAUSE_WIDTH = 480
SCENARIO_WIDTH = 400
STORY_WIDTH = 320
INCREMENT_WIDTH = 480
LANE_INDENT = 40
SCENARIO_INDENT = 40
CLAUSE_INDENT = 80
BLOCK_GAP = 20

LEFT_MARGIN_X = 20
EPIC_ROW_Y = 120
EPIC_HEIGHT = 60
SUBEPIC_ROW_Y = 195
SUBEPIC_HEIGHT = 60
STORY_ROW_Y = 345
STORY_SIZE = 50
STORY_PITCH_X = 60
FIRST_STORY_INSET = 10
SUBEPIC_TIGHTEN = 5
EPIC_TIGHTEN = 5
EPIC_GAP = 10

_STYLE_EPIC = (
    "epic;rounded=1;whiteSpace=wrap;html=1;overflow=hidden;"
    "fillColor=#e1d5e7;strokeColor=#9673a6;fontColor=#000000;fontSize=11;"
)
_STYLE_STORY_TMPL = (
    "story:{role};whiteSpace=wrap;html=1;overflow=hidden;aspect=fixed;"
    "fillColor=#fff2cc;strokeColor=#d6b656;fontColor=#000000;fontSize=8;"
)


def _slugify(name: str) -> str:
    s = name.lower()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s or "node"


def _subepic_style(depth: int) -> str:
    return (
        f"subepic:{depth};rounded=1;whiteSpace=wrap;html=1;overflow=hidden;"
        "fillColor=#d5e8d4;strokeColor=#82b366;fontColor=#000000;fontSize=10;"
    )


def _leaf_story_count(sub_epic: SubEpic) -> int:
    if not sub_epic.sub_epics:
        return max(1, len(sub_epic.stories))
    return sum(_leaf_story_count(s) for s in sub_epic.sub_epics)


# ── Leaf node types ───────────────────────────────────────────────────────────

class DrawIOIncrement(Increment):
    pass


class DrawIOScenario(Scenario):
    def create_child_scenario(self, source: Scenario) -> "DrawIOScenario":
        return DrawIOScenario(source.name, source.sequential_order, source.story_name)


class DrawIOStory(Story):
    def create_child_scenario(self, source: Scenario) -> DrawIOScenario:
        return DrawIOScenario(source.name, source.sequential_order, source.story_name)


class DrawIOSubEpic(SubEpic):
    def create_child_sub_epic(self, source: SubEpic) -> "DrawIOSubEpic":
        return DrawIOSubEpic(source.name, source.sequential_order)

    def create_child_story(self, source: Story) -> DrawIOStory:
        return DrawIOStory(source.name, source.sequential_order, source.story_type)


class DrawIOEpic(Epic):
    def create_child_sub_epic(self, source: SubEpic) -> DrawIOSubEpic:
        return DrawIOSubEpic(source.name, source.sequential_order)


# ── Root node + I/O ───────────────────────────────────────────────────────────

class DrawIOParseError(Exception):
    """Raised when a document is not a valid Draw.io story map."""


class DrawIOStoryMap(StoryMap):
    """DrawIO story-map I/O. IS the format-typed tree root.

    parse / render / sync implement the Uniform Callable Surface.
    render_thin_slice and render_scenario are render-only views.
    """

    def create_child_epic(self, source: DrawIOEpic) -> DrawIOEpic:
        return DrawIOEpic(source.name, source.sequential_order)

    def create_child_increment(self, source: Increment) -> DrawIOIncrement:
        return DrawIOIncrement(source.name, source.sequential_order)

    # ── Uniform Callable Surface ──────────────────────────────────────────────

    def render(self, canonical: "DrawIOStoryMap", previous: Optional[str] = None) -> str:
        mxfile = ET.Element("mxfile", attrib={"host": "app.diagrams.net"})
        diagram = ET.SubElement(mxfile, "diagram", attrib={"name": "Story Map", "id": "story-map"})
        graph_model = ET.SubElement(diagram, "mxGraphModel")
        graph_root = ET.SubElement(graph_model, "root")
        ET.SubElement(graph_root, "mxCell", attrib={"id": "0"})
        ET.SubElement(graph_root, "mxCell", attrib={"id": "1", "parent": "0"})

        epic_x_cursor = LEFT_MARGIN_X
        for epic in canonical.epics:
            first_story_col = self._next_story_col(canonical, epic)
            self._emit_epic(graph_root, epic, epic_x_cursor, first_story_col)
            epic_x_cursor += self._epic_width(epic) + EPIC_GAP

        body = ET.tostring(mxfile, encoding="unicode")
        return "<?xml version='1.0' encoding='utf-8'?>\n" + body

    def parse(self, text: str) -> "DrawIOStoryMap":
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
        current_sub_epic_stack: List[DrawIOSubEpic] = []

        for cell in cells:
            style = cell.attrib.get("style", "")
            value = cell.attrib.get("value", "")
            if style.startswith("epic"):
                current_epic = DrawIOEpic(value, len(story_map.epics) + 1)
                story_map.epics.append(current_epic)
                current_sub_epic_stack = []
            elif style.startswith("subepic") and current_epic is not None:
                depth = int(style.split(":", 1)[1].split(";", 1)[0]) if ":" in style else 0
                while len(current_sub_epic_stack) > depth:
                    current_sub_epic_stack.pop()
                parent_children = (
                    current_sub_epic_stack[-1].sub_epics
                    if current_sub_epic_stack
                    else current_epic.sub_epics
                )
                sub_epic = DrawIOSubEpic(value, len(parent_children) + 1)
                parent_children.append(sub_epic)
                current_sub_epic_stack.append(sub_epic)
            elif style.startswith("story") and current_sub_epic_stack:
                parent = current_sub_epic_stack[-1]
                story = DrawIOStory(value, len(parent.stories) + 1, StoryType.USER)
                parent.stories.append(story)

        return story_map

    def sync(self, text: str, canonical: "DrawIOStoryMap") -> UpdateReport:
        return canonical.translate_from(self.parse(text))

    # ── Thin-slice view ───────────────────────────────────────────────────────

    def render_thin_slice(self, canonical: StoryMap) -> str:
        mxfile = ET.Element("mxfile", attrib={"host": "app.diagrams.net"})
        diagram = ET.SubElement(mxfile, "diagram", attrib={"name": "Story Map", "id": "story-map"})
        graph_model = ET.SubElement(diagram, "mxGraphModel")
        graph_root = ET.SubElement(graph_model, "root")
        ET.SubElement(graph_root, "mxCell", attrib={"id": "0"})
        ET.SubElement(graph_root, "mxCell", attrib={"id": "1", "parent": "0"})

        epic_x_cursor = LEFT_MARGIN_X
        for epic in canonical.epics:
            first_story_col = self._next_story_col(canonical, epic)
            self._emit_epic(graph_root, epic, epic_x_cursor, first_story_col)
            epic_x_cursor += self._epic_width(epic) + EPIC_GAP

        total_map_width = epic_x_cursor - EPIC_GAP + LEFT_MARGIN_X
        lane_start_y = STORY_ROW_Y + STORY_SIZE + 15

        story_x: Dict[str, int] = {}
        self._collect_story_x(canonical, story_x)

        _LANE_HEIGHT = 70
        _LABEL_WIDTH = 150
        _LABEL_X = LEFT_MARGIN_X - _LABEL_WIDTH - 5
        _LANE_X = _LABEL_X
        _STYLE_LANE_BG = (
            "whiteSpace=wrap;html=1;overflow=hidden;"
            "fillColor=#f5f5f5;strokeColor=#666666;"
            "fontColor=#000000;fontSize=11;fontStyle=1;"
        )
        _STYLE_STORY_IN_LANE = (
            "whiteSpace=wrap;html=1;overflow=hidden;aspect=fixed;"
            "fillColor=#fff2cc;strokeColor=#d6b656;"
            "fontColor=#000000;fontSize=8;"
        )

        lane_y = lane_start_y
        for inc in canonical.increments:
            inc_slug = _slugify(inc.name)
            self._add_cell(
                graph_root, f"inc-lane/{inc_slug}", "",
                _LANE_X, lane_y,
                total_map_width - _LANE_X + LEFT_MARGIN_X + 20, _LANE_HEIGHT,
                style=_STYLE_LANE_BG,
            )
            self._add_cell(
                graph_root, f"inc-label/{inc_slug}", inc.name,
                _LABEL_X + 5, lane_y + 10,
                _LABEL_WIDTH - 10, _LANE_HEIGHT - 20,
                style=_STYLE_LANE_BG,
            )
            for story_name in inc.stories:
                sx = story_x.get(story_name)
                if sx is None:
                    continue
                self._add_cell(
                    graph_root, f"inc-lane/{inc_slug}/{_slugify(story_name)}", story_name,
                    sx, lane_y + (_LANE_HEIGHT - STORY_SIZE) // 2,
                    STORY_SIZE, STORY_SIZE,
                    style=_STYLE_STORY_IN_LANE,
                )
            lane_y += _LANE_HEIGHT

        body = ET.tostring(mxfile, encoding="unicode")
        return "<?xml version='1.0' encoding='utf-8'?>\n" + body

    # ── Scenario view ─────────────────────────────────────────────────────────

    def render_scenario(self, canonical: StoryMap) -> str:
        root, graph_root, cell_id = self._new_document()
        y = 0
        for story in self._walk_stories_with_scenarios(canonical):
            cell_id = self._add_cell(
                graph_root, cell_id, story.name, 0, y, STORY_WIDTH, ROW_HEIGHT,
                style="story:user",
            )
            y += ROW_HEIGHT
            for scenario in story.scenarios:
                cell_id = self._add_cell(
                    graph_root, cell_id, scenario.name,
                    SCENARIO_INDENT, y, SCENARIO_WIDTH, ROW_HEIGHT,
                    style="scenario",
                )
                y += ROW_HEIGHT
                for clause in scenario.given:
                    cell_id = self._render_clause(graph_root, cell_id, clause, "Given", y)
                    y += CLAUSE_HEIGHT
                for interaction in scenario.interactions:
                    for clause in interaction.when:
                        cell_id = self._render_clause(graph_root, cell_id, clause, "When", y)
                        y += CLAUSE_HEIGHT
                    for clause in interaction.then:
                        cell_id = self._render_clause(graph_root, cell_id, clause, "Then", y)
                        y += CLAUSE_HEIGHT
                y += BLOCK_GAP
            y += BLOCK_GAP
        return ET.tostring(root, encoding="unicode")

    # ── Private helpers ───────────────────────────────────────────────────────

    def _emit_epic(self, graph_root: ET.Element, epic: Epic, epic_x: int, first_story_col: int) -> None:
        epic_slug = _slugify(epic.name)
        self._add_cell(
            graph_root, epic_slug, epic.name,
            epic_x, EPIC_ROW_Y, self._epic_width(epic), EPIC_HEIGHT,
            style=_STYLE_EPIC,
        )
        sub_x_cursor = epic_x + EPIC_TIGHTEN
        col_cursor = first_story_col
        for sub in epic.sub_epics:
            leaves = _leaf_story_count(sub)
            width = leaves * STORY_PITCH_X - SUBEPIC_TIGHTEN * 2
            self._emit_sub_epic(graph_root, sub, epic_slug, depth=0,
                                sub_x=sub_x_cursor, width=width, first_story_col=col_cursor)
            sub_x_cursor += width + SUBEPIC_TIGHTEN * 2
            col_cursor += leaves

    def _emit_sub_epic(self, graph_root: ET.Element, sub_epic: SubEpic, parent_slug: str,
                       depth: int, sub_x: int, width: int, first_story_col: int) -> None:
        sub_slug = f"{parent_slug}/{_slugify(sub_epic.name)}"
        self._add_cell(
            graph_root, sub_slug, sub_epic.name,
            sub_x, SUBEPIC_ROW_Y, width, SUBEPIC_HEIGHT,
            style=_subepic_style(depth),
        )
        col_cursor = first_story_col
        for nested in sub_epic.sub_epics:
            leaves = _leaf_story_count(nested)
            nested_width = leaves * STORY_PITCH_X - SUBEPIC_TIGHTEN * 2
            self._emit_sub_epic(
                graph_root, nested, sub_slug, depth=depth + 1,
                sub_x=sub_x + (col_cursor - first_story_col) * STORY_PITCH_X,
                width=nested_width, first_story_col=col_cursor,
            )
            col_cursor += leaves
        for i, story in enumerate(sub_epic.stories):
            story_x = sub_x + SUBEPIC_TIGHTEN + i * STORY_PITCH_X
            self._add_cell(
                graph_root, f"{sub_slug}/{_slugify(story.name)}", story.name,
                story_x, STORY_ROW_Y, STORY_SIZE, STORY_SIZE,
                style=_STYLE_STORY_TMPL.format(role=story.story_type.value),
            )

    def _epic_width(self, epic: Epic) -> int:
        if not epic.sub_epics:
            return STORY_PITCH_X
        return sum(_leaf_story_count(sub) * STORY_PITCH_X for sub in epic.sub_epics)

    def _next_story_col(self, story_map: StoryMap, epic: Epic) -> int:
        col = 0
        for candidate in story_map.epics:
            if candidate is epic:
                return col
            for sub in candidate.sub_epics:
                col += _leaf_story_count(sub)
        return col

    def _collect_story_x(self, canonical: StoryMap, out: Dict[str, int]) -> None:
        epic_x_cursor = LEFT_MARGIN_X
        for epic in canonical.epics:
            sub_x_cursor = epic_x_cursor + EPIC_TIGHTEN
            for sub in epic.sub_epics:
                self._collect_sub_epic_x(sub, sub_x_cursor, out)
                sub_x_cursor += _leaf_story_count(sub) * STORY_PITCH_X
            epic_x_cursor += self._epic_width(epic) + EPIC_GAP

    def _collect_sub_epic_x(self, sub_epic: SubEpic, sub_x: int, out: Dict[str, int]) -> None:
        if sub_epic.sub_epics:
            col_cursor = sub_x
            for nested in sub_epic.sub_epics:
                self._collect_sub_epic_x(nested, col_cursor, out)
                col_cursor += _leaf_story_count(nested) * STORY_PITCH_X
        else:
            for i, story in enumerate(sub_epic.stories):
                out[story.name] = sub_x + SUBEPIC_TIGHTEN + i * STORY_PITCH_X

    def _new_document(self):
        root = ET.Element("mxGraphModel")
        graph_root = ET.SubElement(root, "root")
        ET.SubElement(graph_root, "mxCell", attrib={"id": "0"})
        ET.SubElement(graph_root, "mxCell", attrib={"id": "1", "parent": "0"})
        return root, graph_root, 2

    def _render_clause(self, graph_root, cell_id, clause, phase_keyword, y):
        label = clause.text if clause.is_continuation else f"{phase_keyword} {clause.text}"
        return self._add_cell(
            graph_root, cell_id, label,
            CLAUSE_INDENT, y, CLAUSE_WIDTH, CLAUSE_HEIGHT,
            style=f"clause:{phase_keyword.lower()}",
        )

    def _walk_stories_with_scenarios(self, canonical: StoryMap) -> List[Story]:
        result: List[Story] = []
        for epic in canonical.epics:
            for sub in epic.sub_epics:
                self._collect_stories_with_scenarios(sub, result)
        return result

    def _collect_stories_with_scenarios(self, sub_epic: SubEpic, out: List[Story]) -> None:
        for story in sub_epic.stories:
            if getattr(story, "scenarios", None):
                out.append(story)
        for nested in sub_epic.sub_epics:
            self._collect_stories_with_scenarios(nested, out)

    def _add_cell(self, graph_root, cell_id, label, x, y, width, height, style,
                  extra_attributes=None):
        id_str = str(cell_id)
        attributes = {
            "id": id_str, "value": label, "style": style,
            "vertex": "1", "parent": "1",
        }
        if extra_attributes:
            attributes.update(extra_attributes)
        cell = ET.SubElement(graph_root, "mxCell", attrib=attributes)
        ET.SubElement(cell, "mxGeometry", attrib={
            "x": str(x), "y": str(y), "width": str(width), "height": str(height),
            "as": "geometry",
        })
        if isinstance(cell_id, int):
            return cell_id + 1
        return cell_id
