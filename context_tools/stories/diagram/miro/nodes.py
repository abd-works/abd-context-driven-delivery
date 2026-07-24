"""Miro format story nodes — all seven StoryNode subtypes plus I/O."""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

from context_tools.stories.story_model.nodes import Epic, Story, StoryType, SubEpic
from context_tools.stories.story_model.scenario import Scenario
from context_tools.stories.story_model.story_map import StoryMap
from context_tools.stories.story_model.thin_slice import Increment
from context_tools.stories.story_model.update_report import UpdateReport
from context_tools.stories.diagram.diagram_story_map import BASE_WIDTH, ROW_HEIGHT, DiagramStoryMap


# ── Leaf node types ───────────────────────────────────────────────────────────

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


# ── Root node + I/O ───────────────────────────────────────────────────────────

class MiroParseError(Exception):
    """Raised when the payload is not a valid Miro story map."""


class MiroStoryMap(StoryMap):
    """Miro story-map I/O. IS the format-typed tree root.

    parse / render / sync implement the Uniform Callable Surface.
    """

    def create_child_epic(self, source: MiroEpic) -> MiroEpic:
        return MiroEpic(source.name, source.sequential_order)

    def create_child_increment(self, source: Increment) -> MiroIncrement:
        return MiroIncrement(source.name, source.sequential_order)

    # ── Uniform Callable Surface ──────────────────────────────────────────────

    def render(self, canonical: "MiroStoryMap", previous: Optional[str] = None) -> str:
        layout = DiagramStoryMap(canonical)
        items: List[Dict[str, Any]] = []
        for epic in canonical.epics:
            items.append(self._item(
                role="epic", label=epic.name,
                x=layout.epic_x(epic), y=layout.epic_row_y(), width=layout.epic_width(epic),
            ))
            for sub in epic.sub_epics:
                self._collect_sub_epic_items(sub, layout, items)
        return json.dumps({"items": items}, indent=2)

    def parse(self, text: str) -> "MiroStoryMap":
        try:
            payload = json.loads(text)
        except json.JSONDecodeError as err:
            raise MiroParseError(f"Not valid JSON: {err}") from err
        if not isinstance(payload, dict) or "items" not in payload:
            raise MiroParseError("Payload must contain an 'items' list")

        story_map = MiroStoryMap()
        current_epic: MiroEpic | None = None
        current_sub_epic_stack: List[MiroSubEpic] = []

        for item in payload["items"]:
            role = item.get("role", "")
            label = item.get("data", {}).get("content", "")
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
                parent.stories.append(story)

        return story_map

    def sync(self, text: str, canonical: "MiroStoryMap") -> UpdateReport:
        return canonical.translate_from(self.parse(text))

    # ── Private helpers ───────────────────────────────────────────────────────

    def _collect_sub_epic_items(self, sub_epic: SubEpic, layout: DiagramStoryMap,
                                items: List[Dict[str, Any]]) -> None:
        depth = layout.sub_epic_depth(sub_epic)
        items.append(self._item(
            role=f"subepic:{depth}", label=sub_epic.name,
            x=layout.sub_epic_x(sub_epic), y=layout.sub_epic_row_y(depth),
            width=layout.sub_epic_width(sub_epic),
        ))
        for nested in sub_epic.sub_epics:
            self._collect_sub_epic_items(nested, layout, items)
        for story in sub_epic.stories:
            items.append(self._item(
                role=f"story:{story.story_type.value}", label=story.name,
                x=layout.story_x(story), y=layout.story_row_y(), width=BASE_WIDTH,
            ))

    def _item(self, role: str, label: str, x: int, y: int, width: int) -> Dict[str, Any]:
        return {
            "type": "shape", "role": role,
            "data": {"content": label},
            "position": {"x": x, "y": y},
            "geometry": {"width": width, "height": ROW_HEIGHT},
        }
