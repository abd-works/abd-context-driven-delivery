"""MiroStoryMap — renders a canonical StoryMap as a payload of Miro API items.

Payload shape (matches Miro's REST `create_items` batch shape):

    {
      "items": [
        {
          "type": "shape",
          "data": {"content": "Epic 1"},
          "position": {"x": 0, "y": 0},
          "geometry": {"width": 200, "height": 100},
          "role": "epic"
        }, ...
      ]
    }

Public surface follows the Uniform Callable Surface (see
src/architecture-context.md). `DiagramStoryMap` is an internal positioning
collaborator built inside `render`; it does not leak through the seam.
"""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

from src.core.stories.nodes import AcceptanceCriteria, Epic, Story, StoryType, SubEpic
from src.core.stories.story_map import StoryMap
from src.core.stories.update_report import UpdateReport
from src.formats.diagram.diagram_story_map import BASE_WIDTH, ROW_HEIGHT, DiagramStoryMap


class MiroParseError(Exception):
    """Raised when the payload is not a valid Miro story map."""


class MiroStoryMap:
    def render(
        self, canonical: StoryMap, previous: Optional[str] = None
    ) -> str:
        layout = DiagramStoryMap(canonical)
        items: List[Dict[str, Any]] = []
        for epic in canonical.epics:
            items.append(
                self._item(
                    role="epic",
                    label=epic.name,
                    x=layout.epic_x(epic),
                    y=layout.epic_row_y(),
                    width=layout.epic_width(epic),
                )
            )
            for sub in epic.sub_epics:
                self._collect_sub_epic_items(sub, layout, items)
        return json.dumps({"items": items}, indent=2)

    def parse(self, text: str) -> StoryMap:
        try:
            payload = json.loads(text)
        except json.JSONDecodeError as err:
            raise MiroParseError(f"Not valid JSON: {err}") from err
        if not isinstance(payload, dict) or "items" not in payload:
            raise MiroParseError("Payload must contain an 'items' list")

        story_map = StoryMap()
        current_epic: Epic | None = None
        current_sub_epic_stack: List[SubEpic] = []

        for item in payload["items"]:
            role = item.get("role", "")
            label = item.get("data", {}).get("content", "")
            if role == "epic":
                current_epic = Epic(label, len(story_map.epics) + 1)
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
                sub_epic = SubEpic(label, len(parent_children) + 1)
                parent_children.append(sub_epic)
                current_sub_epic_stack.append(sub_epic)
            elif role.startswith("story:") and current_sub_epic_stack:
                parent = current_sub_epic_stack[-1]
                story = Story(label, len(parent.stories) + 1, StoryType.USER)
                ac_payload = item.get("acceptanceCriteria", [])
                if isinstance(ac_payload, list):
                    for i, entry in enumerate(ac_payload, start=1):
                        if not isinstance(entry, dict):
                            continue
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

    def _collect_sub_epic_items(
        self,
        sub_epic: SubEpic,
        layout: DiagramStoryMap,
        items: List[Dict[str, Any]],
    ) -> None:
        depth = layout.sub_epic_depth(sub_epic)
        items.append(
            self._item(
                role=f"subepic:{depth}",
                label=sub_epic.name,
                x=layout.sub_epic_x(sub_epic),
                y=layout.sub_epic_row_y(depth),
                width=layout.sub_epic_width(sub_epic),
            )
        )
        for nested in sub_epic.sub_epics:
            self._collect_sub_epic_items(nested, layout, items)
        for story in sub_epic.stories:
            items.append(
                self._item(
                    role=f"story:{story.story_type.value}",
                    label=story.name,
                    x=layout.story_x(story),
                    y=layout.story_row_y(),
                    width=BASE_WIDTH,
                    acceptance_criteria=[
                        {"name": ac.name, "text": ac.text}
                        for ac in story.acceptance_criteria
                    ],
                )
            )

    def _item(
        self,
        role: str,
        label: str,
        x: int,
        y: int,
        width: int,
        acceptance_criteria: Optional[List[Dict[str, str]]] = None,
    ) -> Dict[str, Any]:
        item = {
            "type": "shape",
            "role": role,
            "data": {"content": label},
            "position": {"x": x, "y": y},
            "geometry": {"width": width, "height": ROW_HEIGHT},
        }
        if acceptance_criteria is not None:
            item["acceptanceCriteria"] = acceptance_criteria
        return item
