"""DrawIO format story nodes — all seven StoryNode subtypes plus I/O.

Three views:
- story-map  render(canonical)            — Epic → SubEpic → Story grid
- thin-slice render_thin_slice(canonical) — Epic/sub-epic column headers × increment swim-lane rows
- scenario   render_scenario(canonical)   — Story + Scenario + Clause cells
"""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional

from stories.story_model.nodes import Epic, Story, StoryType, SubEpic
from stories.story_model.scenario import Scenario
from stories.story_model.story_map import StoryMap
from stories.story_model.thin_slice import Increment
from stories.story_model.update_report import UpdateReport
from stories.diagram.diagram_story_map import (
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
EPIC_CONTENT_INSET = 10
EPIC_ESTIMATE_ROW_Y = EPIC_ROW_Y - 20
EPIC_ESTIMATE_HEIGHT = 40
SUBEPIC_ROW_Y = 195
SHAPING_SUBEPIC_ROW_Y = 200
SUBEPIC_HEIGHT = 60
STORY_ROW_Y = 345
SHAPING_DETAIL_ROW_Y = 275
STORY_SIZE = 50
STORY_PITCH_X = 60
ESTIMATE_STORY_GAP = 15
FIRST_STORY_INSET = 10
SUBEPIC_TIGHTEN = 5
EPIC_TIGHTEN = 5
EPIC_GAP = 10

_STYLE_EPIC = (
    "epic;rounded=1;whiteSpace=wrap;html=1;overflow=hidden;"
    "fillColor=#e1d5e7;strokeColor=#9673a6;fontColor=#000000;fontSize=11;"
)
_STYLE_EPIC_ESTIMATE_TEXT = "text;whiteSpace=wrap;html=1;"
_STYLE_STORY_TMPL = (
    "story:{role};whiteSpace=wrap;html=1;overflow=hidden;aspect=fixed;"
    "fillColor=#fff2cc;strokeColor=#d6b656;fontColor=#000000;fontSize=8;"
)
_STYLE_ESTIMATE = (
    "estimate;whiteSpace=wrap;html=1;overflow=hidden;"
    "fillColor=none;strokeColor=none;fontColor=#333333;fontSize=8;"
    "align=left;spacingLeft=4;"
)
_STYLE_INC_LANE_BG = (
    "inc-lane;whiteSpace=wrap;html=1;overflow=hidden;"
    "fillColor=#f5f5f5;strokeColor=#666666;fontColor=#000000;fontSize=11;fontStyle=1;"
)
_STYLE_INC_LANE_LABEL = (
    "inc-lane-label;whiteSpace=wrap;html=1;overflow=hidden;"
    "fillColor=#e8e8e8;strokeColor=#666666;fontColor=#000000;fontSize=10;fontStyle=1;"
    "align=right;spacingRight=8;verticalAlign=middle;"
)
_STYLE_INCREMENT_STORY = (
    "increment-story;whiteSpace=wrap;html=1;overflow=hidden;"
    "fillColor=#fff2cc;strokeColor=#d6b656;fontColor=#000000;fontSize=8;"
)
_STYLE_ACTOR = (
    "actor;whiteSpace=wrap;html=1;overflow=hidden;"
    "fillColor=#dae8fc;strokeColor=#6c8ebf;fontColor=#000000;fontSize=7;"
)

INC_LANE_LABEL_WIDTH = 160                              # left label column width
INC_LANE_TOP_Y = SUBEPIC_ROW_Y + SUBEPIC_HEIGHT + 10   # below sub-epic headers
INC_LANE_HEIGHT = STORY_SIZE + 20                       # 70 px per lane
INC_LANE_GAP = 5
INC_STORY_Y_OFFSET = (INC_LANE_HEIGHT - STORY_SIZE) // 2  # vertically centre story in lane

ACTOR_LABEL_HEIGHT = STORY_SIZE   # square, same size as story cells
ACTOR_LABEL_GAP = 4               # gap between actor label bottom and story top


def _slugify(name: str) -> str:
    s = name.lower()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s or "node"


def _subepic_style(depth: int) -> str:
    return (
        f"subepic:{depth};rounded=1;whiteSpace=wrap;html=1;overflow=hidden;"
        "fillColor=#d5e8d4;strokeColor=#82b366;fontColor=#000000;fontSize=10;"
    )


def _layout_columns(sub_epic: SubEpic) -> int:
    return sub_epic.diagram_span_columns()


def _estimate_label(estimate: str) -> str:
    text = estimate.strip()
    if not text:
        return ""
    return text if text.startswith("*") else f"* {text}"


def _parse_estimate_value(value: str) -> str:
    plain = re.sub(r"<[^>]+>", "", value)
    return plain.strip().removeprefix("*").strip()


def _map_has_outline_estimates(story_map: StoryMap) -> bool:
    if any(ep.estimate.strip() for ep in story_map.epics):
        return True
    return any(sub.estimate.strip() for sub in story_map.all_sub_epics())


def _layout_rows(story_map: StoryMap) -> tuple[int, int]:
    """Return (subepic_row_y, detail_row_y) for story-map layout."""
    if _map_has_outline_estimates(story_map):
        return SHAPING_SUBEPIC_ROW_Y, SHAPING_DETAIL_ROW_Y
    return SUBEPIC_ROW_Y, STORY_ROW_Y


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

        subepic_y, detail_y = _layout_rows(canonical)
        epic_x_cursor = LEFT_MARGIN_X
        for epic in canonical.epics:
            first_story_col = self._next_story_col(canonical, epic)
            self._emit_epic(
                graph_root, epic, epic_x_cursor, first_story_col,
                subepic_y=subepic_y, detail_y=detail_y,
            )
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
                current_epic = DrawIOEpic(value.strip(), len(story_map.epics) + 1)
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
            elif style.startswith("text") and current_epic is not None and not current_sub_epic_stack:
                estimate = _parse_estimate_value(value)
                if estimate and ("approx" in estimate.lower() or value.strip().startswith("*")):
                    current_epic.estimate = estimate
            elif style.startswith("estimate") and current_epic is not None:
                estimate = _parse_estimate_value(value)
                cell_id = cell.attrib.get("id", "")
                if cell_id.endswith("/epic-estimate") or (
                    cell_id.endswith("/estimate") and cell_id.count("/") == 1
                ):
                    current_epic.estimate = estimate
                elif current_sub_epic_stack:
                    current_sub_epic_stack[-1].estimate = estimate

        return story_map

    def sync(self, text: str, canonical: "DrawIOStoryMap") -> UpdateReport:
        return canonical.translate_from(self.parse(text))

    # ── Thin-slice view ───────────────────────────────────────────────────────

    def render_thin_slice(self, canonical: StoryMap) -> str:
        """Render a swim-lane grid: epic/sub-epic columns × increment rows.

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

        # Build story → x-position map (same column positions as the story-map view).
        story_x: Dict[str, int] = {}
        self._collect_story_x(canonical, story_x)

        # Compute total grid width so lanes span the full column area.
        grid_width = (
            sum(self._epic_width(ep) + EPIC_GAP for ep in canonical.epics) - EPIC_GAP
            if canonical.epics else 200
        )

        # Epic + sub-epic column headers (identical to story-map render).
        epic_x_cursor = LEFT_MARGIN_X
        for epic in canonical.epics:
            epic_width = self._epic_width(epic)
            self._add_cell(
                graph_root, _slugify(epic.name), epic.name,
                epic_x_cursor, EPIC_ROW_Y, epic_width, EPIC_HEIGHT,
                style=_STYLE_EPIC,
            )
            sub_x_cursor = epic_x_cursor + EPIC_CONTENT_INSET
            for sub in epic.sub_epics:
                span = _layout_columns(sub)
                width = span * STORY_PITCH_X - SUBEPIC_TIGHTEN * 2
                self._add_cell(
                    graph_root,
                    f"{_slugify(epic.name)}/{_slugify(sub.name)}",
                    sub.name,
                    sub_x_cursor, SUBEPIC_ROW_Y, width, SUBEPIC_HEIGHT,
                    style=_subepic_style(0),
                )
                sub_x_cursor += width + SUBEPIC_TIGHTEN * 2
            epic_x_cursor += epic_width + EPIC_GAP

        # Increment swim lanes.
        # Each lane = a grey background strip (left label area + story grid)
        # + a right-aligned text label cell in the left column.
        lane_start_x = LEFT_MARGIN_X - INC_LANE_LABEL_WIDTH
        lane_total_width = INC_LANE_LABEL_WIDTH + grid_width
        lane_y = INC_LANE_TOP_Y
        for inc in canonical.increments:
            inc_slug = _slugify(inc.name)
            # Background strip (no text).
            self._add_cell(
                graph_root, f"inc-lane/{inc_slug}/bg", "",
                lane_start_x, lane_y, lane_total_width, INC_LANE_HEIGHT,
                style=_STYLE_INC_LANE_BG,
            )
            # Right-aligned label in the left column.
            self._add_cell(
                graph_root, f"inc-lane/{inc_slug}", inc.name,
                lane_start_x, lane_y, INC_LANE_LABEL_WIDTH - 4, INC_LANE_HEIGHT,
                style=_STYLE_INC_LANE_LABEL,
            )
            for story_name in inc.stories:
                x = story_x.get(story_name)
                if x is None:
                    continue
                self._add_cell(
                    graph_root,
                    f"inc-lane/{inc_slug}/{_slugify(story_name)}",
                    story_name,
                    x, lane_y + INC_STORY_Y_OFFSET, STORY_SIZE, STORY_SIZE,
                    style=_STYLE_INCREMENT_STORY,
                )
            lane_y += INC_LANE_HEIGHT + INC_LANE_GAP

        body = ET.tostring(mxfile, encoding="unicode")
        return "<?xml version='1.0' encoding='utf-8'?>\n" + body

    def parse_thin_slice(self, text: str) -> List[DrawIOIncrement]:
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
                        inc.stories.append(value.strip())
        return increments

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

    def _emit_epic(
        self,
        graph_root: ET.Element,
        epic: Epic,
        epic_x: int,
        first_story_col: int,
        *,
        subepic_y: int = SUBEPIC_ROW_Y,
        detail_y: int = STORY_ROW_Y,
    ) -> None:
        epic_slug = _slugify(epic.name)
        self._add_cell(
            graph_root, epic_slug, epic.name,
            epic_x, EPIC_ROW_Y, self._epic_width(epic), EPIC_HEIGHT,
            style=_STYLE_EPIC,
        )
        if (epic.estimate or "").strip():
            self._add_cell(
                graph_root, f"{epic_slug}/epic-estimate", _estimate_label(epic.estimate),
                epic_x, EPIC_ESTIMATE_ROW_Y, min(160, self._epic_width(epic)), EPIC_ESTIMATE_HEIGHT,
                style=_STYLE_EPIC_ESTIMATE_TEXT,
            )
        sub_x_cursor = epic_x + EPIC_CONTENT_INSET
        col_cursor = first_story_col
        for sub in epic.sub_epics:
            span = _layout_columns(sub)
            width = span * STORY_PITCH_X - SUBEPIC_TIGHTEN * 2
            self._emit_sub_epic(
                graph_root, sub, epic_slug, depth=0,
                sub_x=sub_x_cursor, width=width, first_story_col=col_cursor,
                subepic_y=subepic_y, detail_y=detail_y,
            )
            sub_x_cursor += width + SUBEPIC_TIGHTEN * 2
            col_cursor += span

    def _emit_sub_epic(
        self,
        graph_root: ET.Element,
        sub_epic: SubEpic,
        parent_slug: str,
        depth: int,
        sub_x: int,
        width: int,
        first_story_col: int,
        *,
        subepic_y: int = SUBEPIC_ROW_Y,
        detail_y: int = STORY_ROW_Y,
    ) -> None:
        sub_slug = f"{parent_slug}/{_slugify(sub_epic.name)}"
        self._add_cell(
            graph_root, sub_slug, sub_epic.name,
            sub_x, subepic_y, width, SUBEPIC_HEIGHT,
            style=_subepic_style(depth),
        )
        col_cursor = first_story_col
        for nested in sub_epic.sub_epics:
            span = _layout_columns(nested)
            nested_width = span * STORY_PITCH_X - SUBEPIC_TIGHTEN * 2
            self._emit_sub_epic(
                graph_root, nested, sub_slug, depth=depth + 1,
                sub_x=sub_x + (col_cursor - first_story_col) * STORY_PITCH_X,
                width=nested_width, first_story_col=col_cursor,
                subepic_y=subepic_y, detail_y=detail_y,
            )
            col_cursor += span
        current_actor: str = ""
        for i, story in enumerate(sub_epic.stories):
            story_x = sub_x + SUBEPIC_TIGHTEN + i * STORY_PITCH_X
            actor = story.users[0] if story.users else ""
            # Emit actor label above the first story in this sub-epic and
            # whenever the actor changes.  Only when there is enough vertical
            # room (non-shaping fidelity where detail_y == STORY_ROW_Y).
            if detail_y == STORY_ROW_Y and actor and (i == 0 or actor != current_actor):
                actor_y = detail_y - ACTOR_LABEL_HEIGHT - ACTOR_LABEL_GAP
                self._add_cell(
                    graph_root,
                    f"{sub_slug}/{_slugify(story.name)}/actor",
                    actor,
                    story_x, actor_y, STORY_SIZE, ACTOR_LABEL_HEIGHT,
                    style=_STYLE_ACTOR,
                )
                current_actor = actor
            self._add_cell(
                graph_root, f"{sub_slug}/{_slugify(story.name)}", story.name,
                story_x, detail_y, STORY_SIZE, STORY_SIZE,
                style=_STYLE_STORY_TMPL.format(role=story.story_type.value),
            )
        estimate = (sub_epic.estimate or "").strip()
        if estimate:
            if sub_epic.stories:
                last_story_x = (
                    sub_x + SUBEPIC_TIGHTEN + (len(sub_epic.stories) - 1) * STORY_PITCH_X
                )
                est_x = last_story_x + STORY_SIZE + ESTIMATE_STORY_GAP
            else:
                est_x = sub_x + SUBEPIC_TIGHTEN
            est_width = max(width - (est_x - sub_x) - SUBEPIC_TIGHTEN, 80)
            self._add_cell(
                graph_root, f"{sub_slug}/estimate", _estimate_label(estimate),
                est_x, detail_y, est_width, STORY_SIZE,
                style=_STYLE_ESTIMATE,
            )

    def _epic_width(self, epic: Epic) -> int:
        if not epic.sub_epics:
            return STORY_PITCH_X
        return sum(_layout_columns(sub) * STORY_PITCH_X for sub in epic.sub_epics)

    def _next_story_col(self, story_map: StoryMap, epic: Epic) -> int:
        col = 0
        for candidate in story_map.epics:
            if candidate is epic:
                return col
            for sub in candidate.sub_epics:
                col += _layout_columns(sub)
        return col

    def _collect_story_x(self, canonical: StoryMap, out: Dict[str, int]) -> None:
        epic_x_cursor = LEFT_MARGIN_X
        for epic in canonical.epics:
            sub_x_cursor = epic_x_cursor + EPIC_CONTENT_INSET
            for sub in epic.sub_epics:
                self._collect_sub_epic_x(sub, sub_x_cursor, out)
                sub_x_cursor += _layout_columns(sub) * STORY_PITCH_X
            epic_x_cursor += self._epic_width(epic) + EPIC_GAP

    def _collect_sub_epic_x(self, sub_epic: SubEpic, sub_x: int, out: Dict[str, int]) -> None:
        if sub_epic.sub_epics:
            col_cursor = sub_x
            for nested in sub_epic.sub_epics:
                self._collect_sub_epic_x(nested, col_cursor, out)
                col_cursor += _layout_columns(nested) * STORY_PITCH_X
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
