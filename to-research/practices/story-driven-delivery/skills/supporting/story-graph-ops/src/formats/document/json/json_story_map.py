"""JsonStoryMap — story-graph.json I/O.

Schema (camelCase, mirrors the legacy `story-graph.json` conventions):

    {
      "epics": [
        {
          "name": "...",
          "sequentialOrder": 1,
          "subEpics": [
            {
              "name": "...",
              "sequentialOrder": 1,
              "stories": [
                {
                  "name": "...",
                  "sequentialOrder": 1,
                  "storyType": "user",
                  "acceptanceCriteria": [
                    {"name": "AC 1", "sequentialOrder": 1, "text": "..."}
                  ]
                }
              ],
              "subEpics": []
            }
          ]
        }
      ]
    }
"""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

from src.core.stories.nodes import AcceptanceCriteria, Epic, Story, StoryType, SubEpic
from src.core.stories.story_map import StoryMap
from src.core.stories.update_report import UpdateReport


class JsonParseError(Exception):
    """Raised when a document does not conform to the story-graph.json schema."""


class JsonStoryMap:
    """Adapter between a canonical StoryMap and story-graph.json text.

    Implements the Uniform Callable Surface declared in the Multi-Format Story
    Rendering mechanism: parse(external) -> StoryMap,
    render(canonical, previous=None) -> external, sync(external, canonical) ->
    UpdateReport. `previous` is accepted for signature parity across backends and
    ignored here — JSON documents have no hand-written regions to preserve.
    """

    def render(self, story_map: StoryMap, previous: Optional[str] = None) -> str:
        payload = {"epics": [self._epic_to_dict(e) for e in story_map.epics]}
        return json.dumps(payload, indent=2)

    def parse(self, text: str) -> StoryMap:
        try:
            payload = json.loads(text)
        except json.JSONDecodeError as err:
            raise JsonParseError(f"Not valid JSON: {err}") from err

        self._guard_schema(payload)

        story_map = StoryMap()
        for epic_dict in payload.get("epics", []):
            story_map.epics.append(self._epic_from_dict(epic_dict))
        return story_map

    def sync(self, text: str, canonical: StoryMap) -> UpdateReport:
        parsed = self.parse(text)
        return canonical.translate_from(parsed)

    def _epic_to_dict(self, epic: Epic) -> Dict[str, Any]:
        return {
            "name": epic.name,
            "sequentialOrder": epic.sequential_order,
            "subEpics": [self._sub_epic_to_dict(s) for s in epic.sub_epics],
        }

    def _sub_epic_to_dict(self, sub_epic: SubEpic) -> Dict[str, Any]:
        return {
            "name": sub_epic.name,
            "sequentialOrder": sub_epic.sequential_order,
            "subEpics": [self._sub_epic_to_dict(s) for s in sub_epic.sub_epics],
            "stories": [self._story_to_dict(s) for s in sub_epic.stories],
        }

    def _story_to_dict(self, story: Story) -> Dict[str, Any]:
        return {
            "name": story.name,
            "sequentialOrder": story.sequential_order,
            "storyType": story.story_type.value,
            "acceptanceCriteria": [self._ac_to_dict(a) for a in story.acceptance_criteria],
        }

    def _ac_to_dict(self, ac: AcceptanceCriteria) -> Dict[str, Any]:
        return {
            "name": ac.name,
            "sequentialOrder": ac.sequential_order,
            "text": ac.text,
        }

    def _guard_schema(self, payload: Any) -> None:
        if not isinstance(payload, dict):
            raise JsonParseError("Root must be an object")
        if "epics" not in payload:
            raise JsonParseError("Missing required 'epics' key")
        if not isinstance(payload["epics"], list):
            raise JsonParseError("'epics' must be a list")

    def _epic_from_dict(self, data: Dict[str, Any]) -> Epic:
        epic = Epic(data["name"], int(data.get("sequentialOrder", 0)))
        for sub in data.get("subEpics", []):
            epic.sub_epics.append(self._sub_epic_from_dict(sub))
        return epic

    def _sub_epic_from_dict(self, data: Dict[str, Any]) -> SubEpic:
        sub_epic = SubEpic(data["name"], int(data.get("sequentialOrder", 0)))
        for nested in data.get("subEpics", []):
            sub_epic.sub_epics.append(self._sub_epic_from_dict(nested))
        for story in data.get("stories", []):
            sub_epic.stories.append(self._story_from_dict(story))
        return sub_epic

    def _story_from_dict(self, data: Dict[str, Any]) -> Story:
        story = Story(
            data["name"],
            int(data.get("sequentialOrder", 0)),
            StoryType(data.get("storyType", "user")),
        )
        for ac in data.get("acceptanceCriteria", []):
            story.acceptance_criteria.append(self._ac_from_dict(ac))
        return story

    def _ac_from_dict(self, data: Dict[str, Any]) -> AcceptanceCriteria:
        return AcceptanceCriteria(
            name=data.get("name", "AC"),
            sequential_order=int(data.get("sequentialOrder", 0)),
            text=data.get("text", ""),
        )
