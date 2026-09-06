"""DrawIOStoryMap — renders a canonical StoryMap as a Draw.io XML document.

Every Epic, SubEpic, and Story appears as an `<mxCell>` with `vertex="1"` and an
`<mxGeometry>` carrying the position/size computed by `DiagramStoryMap`
internally. The public surface follows the Uniform Callable Surface declared in
the Multi-Format Story Rendering mechanism (see src/architecture-context.md):
parse(text) -> StoryMap, render(canonical, previous=None) -> str,
sync(text, canonical) -> UpdateReport. `DiagramStoryMap` is an internal
positioning collaborator and does not appear on the public seam.
"""

from __future__ import annotations

import json
import xml.etree.ElementTree as ET
from typing import List, Optional

from src.core.stories.nodes import AcceptanceCriteria, Epic, Story, StoryType, SubEpic
from src.core.stories.story_map import StoryMap
from src.core.stories.update_report import UpdateReport
from src.formats.diagram.diagram_story_map import BASE_WIDTH, ROW_HEIGHT, DiagramStoryMap


class DrawIOParseError(Exception):
    """Raised when a document is not a valid Draw.io story map."""


class DrawIOStoryMap:
    def render(
        self, canonical: StoryMap, previous: Optional[str] = None
    ) -> str:
        # WHY: DiagramStoryMap owns geometry math — built fresh here so the
        # positions always reflect the caller's current canonical.
        layout = DiagramStoryMap(canonical)

        root = ET.Element("mxGraphModel")
        graph_root = ET.SubElement(root, "root")
        ET.SubElement(graph_root, "mxCell", attrib={"id": "0"})
        ET.SubElement(graph_root, "mxCell", attrib={"id": "1", "parent": "0"})

        cell_id = 2
        for epic in canonical.epics:
            cell_id = self._add_cell(
                graph_root,
                cell_id,
                epic.name,
                layout.epic_x(epic),
                layout.epic_row_y(),
                layout.epic_width(epic),
                ROW_HEIGHT,
                style="epic",
            )
            for sub in epic.sub_epics:
                cell_id = self._render_sub_epic(sub, layout, graph_root, cell_id)

        return ET.tostring(root, encoding="unicode")

    def parse(self, text: str) -> StoryMap:
        try:
            tree = ET.fromstring(text)
        except ET.ParseError as err:
            raise DrawIOParseError(f"Not valid Draw.io XML: {err}") from err
        if tree.tag != "mxGraphModel":
            raise DrawIOParseError("Root element must be <mxGraphModel>")

        cells = tree.findall(".//mxCell[@vertex='1']")
        story_map = StoryMap()
        current_epic: Epic | None = None
        current_sub_epic_stack: List[SubEpic] = []

        # WHY: cells are emitted in tree order, so we can walk them in one pass and
        # reconstruct the hierarchy from each cell's style tag.
        for cell in cells:
            style = cell.attrib.get("style", "")
            value = cell.attrib.get("value", "")
            if style.startswith("epic"):
                current_epic = Epic(value, len(story_map.epics) + 1)
                story_map.epics.append(current_epic)
                current_sub_epic_stack = []
            elif style.startswith("subepic") and current_epic is not None:
                depth = int(style.split(":", 1)[1]) if ":" in style else 0
                while len(current_sub_epic_stack) > depth:
                    current_sub_epic_stack.pop()
                parent_children = (
                    current_sub_epic_stack[-1].sub_epics
                    if current_sub_epic_stack
                    else current_epic.sub_epics
                )
                sub_epic = SubEpic(value, len(parent_children) + 1)
                parent_children.append(sub_epic)
                current_sub_epic_stack.append(sub_epic)
            elif style.startswith("story") and current_sub_epic_stack:
                parent = current_sub_epic_stack[-1]
                story = Story(value, len(parent.stories) + 1, StoryType.USER)
                ac_payload = cell.attrib.get("ac", "")
                if ac_payload:
                    for i, entry in enumerate(self._parse_acceptance_payload(ac_payload), start=1):
                        story.acceptance_criteria.append(
                            AcceptanceCriteria(
                                name=entry.get("name") or f"AC {i}",
                                sequential_order=i,
                                text=entry.get("text") or "",
                            )
                        )
                parent.stories.append(story)

        return story_map

    def sync(self, text: str, canonical: StoryMap) -> UpdateReport:
        parsed = self.parse(text)
        return canonical.translate_from(parsed)

    def _render_sub_epic(
        self,
        sub_epic: SubEpic,
        layout: DiagramStoryMap,
        graph_root: ET.Element,
        cell_id: int,
    ) -> int:
        depth = layout.sub_epic_depth(sub_epic)
        cell_id = self._add_cell(
            graph_root,
            cell_id,
            sub_epic.name,
            layout.sub_epic_x(sub_epic),
            layout.sub_epic_row_y(depth),
            layout.sub_epic_width(sub_epic),
            ROW_HEIGHT,
            style=f"subepic:{depth}",
        )
        for nested in sub_epic.sub_epics:
            cell_id = self._render_sub_epic(nested, layout, graph_root, cell_id)
        for story in sub_epic.stories:
            cell_id = self._add_cell(
                graph_root,
                cell_id,
                story.name,
                layout.story_x(story),
                layout.story_row_y(),
                BASE_WIDTH,
                ROW_HEIGHT,
                style=f"story:{story.story_type.value}",
                extra_attributes={
                    "ac": json.dumps(
                        [
                            {"name": ac.name, "text": ac.text}
                            for ac in story.acceptance_criteria
                        ],
                        separators=(",", ":"),
                    )
                },
            )
        return cell_id

    def _add_cell(
        self,
        graph_root: ET.Element,
        cell_id: int,
        label: str,
        x: int,
        y: int,
        width: int,
        height: int,
        style: str,
        extra_attributes: Optional[dict] = None,
    ) -> int:
        attributes = {
            "id": str(cell_id),
            "value": label,
            "style": style,
            "vertex": "1",
            "parent": "1",
        }
        if extra_attributes:
            for key, value in extra_attributes.items():
                attributes[key] = value
        cell = ET.SubElement(
            graph_root,
            "mxCell",
            attrib=attributes,
        )
        ET.SubElement(
            cell,
            "mxGeometry",
            attrib={
                "x": str(x),
                "y": str(y),
                "width": str(width),
                "height": str(height),
                "as": "geometry",
            },
        )
        return cell_id + 1

    def _parse_acceptance_payload(self, payload: str) -> List[dict]:
        try:
            parsed = json.loads(payload)
        except json.JSONDecodeError:
            return []
        if not isinstance(parsed, list):
            return []
        result: List[dict] = []
        for item in parsed:
            if isinstance(item, dict):
                result.append(item)
        return result
