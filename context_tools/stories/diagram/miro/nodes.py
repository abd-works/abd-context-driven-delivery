"""Miro format story nodes - all seven StoryNode subtypes plus I/O.

Three views (mirroring the DrawIO backend):
- story-map   render(canonical)            - Epic -> SubEpic -> Story grid
- thin-slice  render_thin_slice(canonical) - Increment swim-lane rows x Epic/SubEpic columns
- scenario    render_scenario(canonical)   - Story + Scenario + Clause markdown document

All render methods return an SVG string in the Miro canvas-composer DSL that can
be posted directly to a Miro board via canvas_create_from_svg.
parse() reads the same SVG format back into a StoryMap.
"""

from __future__ import annotations

import html
import re
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional

from context_tools.stories.story_model.nodes import Epic, Story, StoryType, SubEpic
from context_tools.stories.story_model.scenario import Clause, Phase, Scenario
from context_tools.stories.story_model.story_map import StoryMap
from context_tools.stories.story_model.thin_slice import Increment
from context_tools.stories.story_model.update_report import UpdateReport


# ---------------------------------------------------------------------------
# Style constants (match draw.io colours for visual parity)
# ---------------------------------------------------------------------------
_FILL_EPIC = "#e1d5e7"
_STROKE_EPIC = "#9673a6"
_FILL_SUBEPIC_BASE = "#d5e8d4"
_STROKE_SUBEPIC = "#82b366"
_FILL_STORY = "#fff2cc"
_STROKE_STORY = "#d6b656"
_FILL_INC_LANE = "#f5f5f5"
_STROKE_INC_LANE = "#666666"
_FILL_SCENARIO = "#dae8fc"
_STROKE_SCENARIO = "#6c8ebf"
_FILL_CLAUSE = "#f8f8f8"
_STROKE_CLAUSE = "#999999"

INC_LANE_LABEL_WIDTH = 160
INC_LANE_HEIGHT = 70
INC_LANE_GAP = 5
INC_STORY_SIZE = 50
SUBEPIC_TIGHTEN = 5
STORY_PITCH_X = 60
EPIC_GAP = 10
EPIC_HEIGHT = 60
EPIC_CONTENT_INSET = 10
LEFT_MARGIN_X = 20
EPIC_ROW_Y = 120
SUBEPIC_ROW_Y = 195
SUBEPIC_HEIGHT = 60
SUBEPIC_DEPTH_GAP = 8
STORY_ROW_Y = 345
STORY_SIZE = 50
ACTOR_LABEL_HEIGHT = STORY_SIZE
ACTOR_LABEL_GAP = 4
DETAIL_BELOW_SUBEPIC_PAD = 16

SCENARIO_WIDTH = 400
SCENARIO_HEIGHT = 40
STORY_DOC_WIDTH = 320
CLAUSE_HEIGHT = 40
CLAUSE_WIDTH = 480
BLOCK_GAP = 20
SCENARIO_INDENT = 40
CLAUSE_INDENT = 80


def _slugify(name: str) -> str:
    s = name.lower()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s or "node"


def _xe(value: str) -> str:
    """XML-escape a string for use in SVG attributes and text."""
    return html.escape(value, quote=True)


def _subepic_style(depth: int) -> str:
    """Slightly darker fill for each nesting depth."""
    darken = min(depth * 12, 40)
    return f"#{max(0xd5 - darken, 0xa0):02x}{max(0xe8 - darken, 0xc0):02x}{max(0xd4 - darken, 0xa0):02x}"


def _subepic_y_for_depth(depth: int) -> int:
    return SUBEPIC_ROW_Y + depth * (SUBEPIC_HEIGHT + SUBEPIC_DEPTH_GAP)


def _max_sub_epic_depth(story_map: StoryMap) -> int:
    def depth_of(sub_epic: SubEpic, depth: int) -> int:
        if not sub_epic.sub_epics:
            return depth
        return max(depth_of(child, depth + 1) for child in sub_epic.sub_epics)

    return max(
        (
            depth_of(sub_epic, 0)
            for epic in story_map.epics
            for sub_epic in epic.sub_epics
        ),
        default=0,
    )


def _story_row_y(story_map: StoryMap) -> int:
    deepest_bottom = _subepic_y_for_depth(_max_sub_epic_depth(story_map)) + SUBEPIC_HEIGHT
    return max(
        STORY_ROW_Y,
        deepest_bottom + ACTOR_LABEL_HEIGHT + ACTOR_LABEL_GAP + DETAIL_BELOW_SUBEPIC_PAD,
    )


# -- Leaf node types -----------------------------------------------------------

class MiroIncrement(Increment):
    pass


class MiroScenario(Scenario):
    def create_child_scenario(self, source: Scenario) -> "MiroScenario":
        return MiroScenario(source.name, source.sequential_order, source.story_name)


class MiroStory(Story):
    def create_child_scenario(self, source: Scenario) -> MiroScenario:
        return MiroScenario(source.name, source.sequential_order, source.story_name)


class MiroSubEpic(SubEpic):
    def create_child_sub_epic(self, source: SubEpic) -> "MiroSubEpic":
        return MiroSubEpic(source.name, source.sequential_order)

    def create_child_story(self, source: Story) -> MiroStory:
        return MiroStory(source.name, source.sequential_order, source.story_type)


class MiroEpic(Epic):
    def create_child_sub_epic(self, source: SubEpic) -> MiroSubEpic:
        return MiroSubEpic(source.name, source.sequential_order)


# -- Root node + I/O -----------------------------------------------------------

class MiroParseError(Exception):
    """Raised when the payload is not a valid Miro story map SVG."""


class MiroStoryMap(StoryMap):
    """Miro story-map I/O. IS the format-typed tree root.

    parse / render / sync implement the Uniform Callable Surface.
    render_thin_slice and render_scenario are render-only views.
    """

    def create_child_epic(self, source: MiroEpic) -> MiroEpic:
        return MiroEpic(source.name, source.sequential_order)

    def create_child_increment(self, source: Increment) -> MiroIncrement:
        return MiroIncrement(source.name, source.sequential_order)

    # -- Uniform Callable Surface ----------------------------------------------

    def render(self, canonical: "MiroStoryMap", previous: Optional[str] = None) -> str:
        """Render a story-map SVG in the Miro canvas-composer DSL.

        Returns an SVG string with one rect per Epic/SubEpic/Story, each carrying
        a data-role attribute encoding its type and depth. Post with
        canvas_create_from_svg to create on an actual Miro board.

        Elements are emitted in depth-first tree order so that parse() can
        reconstruct the hierarchy by processing in document order.
        """
        lines = self._build_rect_lines(canonical)
        body = "\n".join(lines)
        return (
            "<?xml version='1.0' encoding='utf-8'?>\n"
            '<svg xmlns="http://www.w3.org/2000/svg">\n'
            + body
            + "\n</svg>"
        )

    def render_chunks(self, canonical: "MiroStoryMap", chunk_size: int = 80) -> List[str]:
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

    def _build_rect_lines(self, canonical: "MiroStoryMap") -> List[str]:
        """Build the flat list of SVG rect lines for the full story map."""
        lines: List[str] = []
        epic_x = LEFT_MARGIN_X
        story_y = _story_row_y(canonical)
        for epic_index, epic in enumerate(canonical.epics, start=1):
            epic_width = self._epic_width(epic)
            eid = f"epic-{epic_index}-{_slugify(epic.name)}"
            lines.append(
                f'  <rect id="{eid}" x="{epic_x}" y="{EPIC_ROW_Y}" '
                f'width="{epic_width}" height="{EPIC_HEIGHT}" rx="6" '
                f'fill="{_FILL_EPIC}" stroke="{_STROKE_EPIC}" stroke-width="2" '
                f'data-content="{_xe(epic.name)}" data-role="epic" data-font-size="11" />'
            )
            self._collect_sub_epic_lines(
                epic.sub_epics,
                lines,
                depth=0,
                parent_id=eid,
                start_x=epic_x + EPIC_CONTENT_INSET,
                story_y=story_y,
            )
            epic_x += epic_width + EPIC_GAP
        return lines

    def parse(self, text: str) -> "MiroStoryMap":
        """Parse a canvas-composer SVG back into a MiroStoryMap.

        Processes rect elements in document order (depth-first tree order as
        emitted by render). The stack-based algorithm mirrors DrawIO's parse:
        the depth encoded in data-role="subepic:{depth}" drives stack management.
        """
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

        story_map = MiroStoryMap()
        current_epic: MiroEpic | None = None
        current_sub_epic_stack: List[MiroSubEpic] = []

        for el in tagged:
            role = el.get("data-role", "")
            label = el.get("data-content", "")
            if role == "epic":
                current_epic = MiroEpic(label, len(story_map.epics) + 1)
                story_map.epics.append(current_epic)
                current_sub_epic_stack = []
            elif role.startswith("subepic:") and current_epic is not None:
                depth = int(role.split(":", 1)[1])
                while len(current_sub_epic_stack) > depth:
                    current_sub_epic_stack.pop()
                parent_children = (
                    current_sub_epic_stack[-1].sub_epics
                    if current_sub_epic_stack
                    else current_epic.sub_epics
                )
                sub_epic = MiroSubEpic(label, len(parent_children) + 1)
                parent_children.append(sub_epic)
                current_sub_epic_stack.append(sub_epic)
            elif role.startswith("story:") and current_sub_epic_stack:
                parent = current_sub_epic_stack[-1]
                story = MiroStory(label, len(parent.stories) + 1, StoryType.USER)
                actor = el.get("data-actor", "").strip()
                if actor:
                    story.users = [actor]
                parent.stories.append(story)

        return story_map

    def sync(self, text: str, canonical: "MiroStoryMap") -> UpdateReport:
        return canonical.translate_from(self.parse(text))

    # -- Thin-slice view -------------------------------------------------------

    def render_thin_slice(self, canonical: StoryMap) -> str:
        """Render a swim-lane grid: increment rows x epic/subepic columns.

        Returns an SVG with a Miro table widget (foreignObject data-type="table").
        Each row = one increment; columns show the epic/subepic breakdown and which
        stories belong to that increment.
        """
        # Build column headers (one per leaf sub-epic)
        headers: List[str] = ["Increment"]
        sub_epic_cols: List[SubEpic] = []
        for epic in canonical.epics:
            for sub in epic.sub_epics:
                self._collect_leaf_sub_epics(sub, sub_epic_cols)
                if not sub.sub_epics:
                    headers.append(f"{epic.name} / {sub.name}")
                else:
                    for leaf in self._leaf_sub_epics(sub):
                        headers.append(f"{epic.name} / … / {leaf.name}")

        # Build story -> column index map
        story_col: Dict[str, int] = {}
        col_idx = 1
        for epic in canonical.epics:
            for sub in epic.sub_epics:
                for leaf in self._leaf_sub_epics(sub):
                    for story in leaf.stories:
                        story_col[story.name] = col_idx
                    col_idx += 1

        # Generate table header row
        th_cells = "".join(f"<th>{_xe(h)}</th>" for h in headers)
        # Generate increment rows
        tbody_rows: List[str] = []
        for inc in canonical.increments:
            cells = [""] * len(headers)
            cells[0] = inc.name
            for story_name in inc.stories:
                ci = story_col.get(story_name)
                if ci is not None and ci < len(cells):
                    cells[ci] = story_name
            row_html = "".join(f"<td>{_xe(c)}</td>" for c in cells)
            tbody_rows.append(f"<tr>{row_html}</tr>")

        tbody = "\n        ".join(tbody_rows)
        col_count = len(headers)
        table_width = INC_LANE_LABEL_WIDTH + (col_count - 1) * (STORY_PITCH_X + 20)
        table_height = 60 + len(canonical.increments) * 40

        table_xml = (
            f'<foreignObject id="thin-slice-table" x="0" y="0" '
            f'width="{table_width}" height="{table_height}" '
            f'data-type="table" data-title="Thin Slicing">'
            f"<table><thead><tr>{th_cells}</tr></thead>"
            f"<tbody>\n        {tbody}\n      </tbody></table>"
            f"</foreignObject>"
        )
        return (
            "<?xml version='1.0' encoding='utf-8'?>\n"
            '<svg xmlns="http://www.w3.org/2000/svg">\n'
            f"  {table_xml}\n"
            "</svg>"
        )

    def parse_thin_slice(self, text: str) -> List[MiroIncrement]:
        """Parse a thin-slice SVG back into increment nodes.

        The foreignObject body contains an HTML table; ET parses it with the SVG
        namespace inherited from the root, so all lookups use namespace-agnostic
        tag matching (split on "}" to get local name).
        """
        try:
            root_el = ET.fromstring(
                text.split("\n", 1)[1] if text.startswith("<?") else text
            )
        except ET.ParseError as err:
            raise MiroParseError(f"Not valid SVG: {err}") from err

        fo = self._find_foreign_object(root_el, "table")
        if fo is None:
            raise MiroParseError("No table foreignObject found in thin-slice SVG")

        def _local(el: ET.Element) -> str:
            tag = el.tag
            return tag.split("}")[-1] if "}" in tag else tag

        # Find tbody using namespace-agnostic iteration
        tbody_el: ET.Element | None = None
        for el in fo.iter():
            if _local(el) == "tbody":
                tbody_el = el
                break
        if tbody_el is None:
            return []

        increments: List[MiroIncrement] = []
        order = 1
        for tr_el in tbody_el:
            if _local(tr_el) != "tr":
                continue
            cells = [td_el.text or "" for td_el in tr_el if _local(td_el) == "td"]
            if not cells:
                continue
            inc_name = cells[0].strip()
            if not inc_name:
                continue
            inc = MiroIncrement(inc_name, order)
            for story_name in cells[1:]:
                story_name = story_name.strip()
                if story_name:
                    inc.stories.append(story_name)
            increments.append(inc)
            order += 1
        return increments

    # -- Scenario view ---------------------------------------------------------

    def render_scenario(self, canonical: StoryMap) -> str:
        """Render scenario view as a Miro doc widget.

        Returns an SVG with a foreignObject data-type="doc" containing Markdown
        that lists every story with its scenarios and clauses.
        """
        md_lines: List[str] = []
        for story in self._walk_stories_with_scenarios(canonical):
            md_lines.append(f"# {story.name}")
            for scenario in story.scenarios:
                md_lines.append(f"\n## {scenario.name}\n")
                if scenario.given:
                    for clause in scenario.given:
                        prefix = "" if clause.is_continuation else "**Given** "
                        md_lines.append(f"{prefix}{clause.text}  ")
                for interaction in scenario.interactions:
                    for clause in interaction.when:
                        prefix = "" if clause.is_continuation else "**When** "
                        md_lines.append(f"{prefix}{clause.text}  ")
                    for clause in interaction.then:
                        prefix = "" if clause.is_continuation else "**Then** "
                        md_lines.append(f"{prefix}{clause.text}  ")
            md_lines.append("")

        markdown = "\n".join(md_lines).strip()
        if not markdown:
            markdown = "# (no scenarios)"

        escaped_md = _xe(markdown)
        doc_xml = (
            f'<foreignObject id="scenario-doc" x="0" y="0" '
            f'width="784" height="1105" data-type="doc">'
            f"{escaped_md}"
            f"</foreignObject>"
        )
        return (
            "<?xml version='1.0' encoding='utf-8'?>\n"
            '<svg xmlns="http://www.w3.org/2000/svg">\n'
            f"  {doc_xml}\n"
            "</svg>"
        )

    # -- Private helpers -------------------------------------------------------

    def _collect_sub_epic_lines(
        self,
        sub_epics: List[SubEpic],
        lines: List[str],
        depth: int,
        parent_id: str,
        start_x: int,
        story_y: int,
    ) -> None:
        sub_x = start_x
        for sub_index, sub in enumerate(sub_epics, start=1):
            span = max(sub.diagram_span_columns(), 1)
            width = span * STORY_PITCH_X - SUBEPIC_TIGHTEN * 2
            sub_y = _subepic_y_for_depth(depth)
            sid = (
                f"{parent_id}/sub-{sub_index}-{_slugify(sub.name)}-d{depth}"
            )
            fill = _subepic_style(depth)
            lines.append(
                f'  <rect id="{sid}" x="{sub_x}" y="{sub_y}" '
                f'width="{width}" height="{SUBEPIC_HEIGHT}" rx="4" '
                f'fill="{fill}" stroke="{_STROKE_SUBEPIC}" stroke-width="1" '
                f'data-content="{_xe(sub.name)}" data-role="subepic:{depth}" data-font-size="10" />'
            )
            # Own stories come before nested children (left columns)
            current_actor = ""
            for index, story in enumerate(sub.stories):
                story_x = sub_x + SUBEPIC_TIGHTEN + index * STORY_PITCH_X
                actor = story.users[0].strip() if story.users else ""
                story_id = f"{sid}/story-{index + 1}-{_slugify(story.name)}"
                if actor and actor != current_actor:
                    lines.append(
                        f'  <rect id="{story_id}/actor" '
                        f'x="{story_x}" y="{story_y - ACTOR_LABEL_HEIGHT - ACTOR_LABEL_GAP}" '
                        f'width="{STORY_SIZE}" height="{ACTOR_LABEL_HEIGHT}" rx="0" '
                        f'fill="{_FILL_SCENARIO}" stroke="{_STROKE_SCENARIO}" stroke-width="1" '
                        f'data-content="{_xe(actor)}" data-role="actor" data-font-size="7" />'
                    )
                    current_actor = actor
                lines.append(
                    f'  <rect id="{story_id}" '
                    f'x="{story_x}" y="{story_y}" '
                    f'width="{STORY_SIZE}" height="{STORY_SIZE}" rx="0" '
                    f'fill="{_FILL_STORY}" stroke="{_STROKE_STORY}" stroke-width="1" '
                    f'data-content="{_xe(story.name)}" '
                    f'data-role="story:{story.story_type.value}" '
                    f'data-actor="{_xe(actor)}" data-font-size="8" />'
                )
            # Recurse into nested sub-epics
            nested_x = sub_x + len(sub.stories) * STORY_PITCH_X
            self._collect_sub_epic_lines(
                sub.sub_epics,
                lines,
                depth + 1,
                sid,
                nested_x,
                story_y,
            )
            sub_x += span * STORY_PITCH_X

    def _epic_width(self, epic: Epic) -> int:
        if not epic.sub_epics:
            return STORY_PITCH_X
        return sum(
            max(sub_epic.diagram_span_columns(), 1) * STORY_PITCH_X
            for sub_epic in epic.sub_epics
        )

    def _leaf_sub_epics(self, sub: SubEpic) -> List[SubEpic]:
        if not sub.sub_epics:
            return [sub]
        result: List[SubEpic] = []
        for child in sub.sub_epics:
            result.extend(self._leaf_sub_epics(child))
        return result

    def _collect_leaf_sub_epics(
        self, sub: SubEpic, out: List[SubEpic]
    ) -> None:
        if not sub.sub_epics:
            out.append(sub)
        else:
            for child in sub.sub_epics:
                self._collect_leaf_sub_epics(child, out)

    def _find_foreign_object(
        self, root_el: ET.Element, data_type: str
    ) -> Optional[ET.Element]:
        for el in root_el.iter():
            tag = el.tag.split("}")[-1] if "}" in el.tag else el.tag
            if tag == "foreignObject" and el.get("data-type") == data_type:
                return el
        return None

    def _walk_stories_with_scenarios(self, canonical: StoryMap) -> List[Story]:
        result: List[Story] = []
        for epic in canonical.epics:
            for sub in epic.sub_epics:
                self._collect_stories_with_scenarios(sub, result)
        return result

    def _collect_stories_with_scenarios(
        self, sub_epic: SubEpic, out: List[Story]
    ) -> None:
        for story in sub_epic.stories:
            if getattr(story, "scenarios", None):
                out.append(story)
        for nested in sub_epic.sub_epics:
            self._collect_stories_with_scenarios(nested, out)
