"""JSON format story nodes - all seven StoryNode subtypes plus I/O.

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
              "stories": [...],
              "subEpics": []
            }
          ]
        }
      ],
      "increments": [
        {
          "name": "...",
          "sequentialOrder": 1,
          "outcome": "...",
          "stories": ["Story name", ...],
          "decisionPrompt": "...",
          "slicingNotes": "..."
        }
      ]
    }
"""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

from context_tools.stories.story_model.nodes import Epic, Story, StoryType, SubEpic
from context_tools.stories.story_model.scenario import Scenario
from context_tools.stories.story_model.source_location import SourceLocation
from context_tools.stories.story_model.story_map import StoryMap
from context_tools.stories.story_model.thin_slice import Increment
from context_tools.stories.story_model.update_report import UpdateReport


# -- Leaf node types -----------------------------------------------------------

class JsonIncrement(Increment):
    pass


class JsonScenario(Scenario):
    def create_child_scenario(self, source: Scenario) -> "JsonScenario":
        return JsonScenario(source.name, source.sequential_order, source.story_name)


class JsonStory(Story):
    def create_child_scenario(self, source: Scenario) -> JsonScenario:
        return JsonScenario(source.name, source.sequential_order, source.story_name)


class JsonSubEpic(SubEpic):
    def create_child_sub_epic(self, source: SubEpic) -> "JsonSubEpic":
        return JsonSubEpic(source.name, source.sequential_order)

    def create_child_story(self, source: Story) -> JsonStory:
        return JsonStory(source.name, source.sequential_order, source.story_type)


class JsonEpic(Epic):
    def create_child_sub_epic(self, source: SubEpic) -> JsonSubEpic:
        return JsonSubEpic(source.name, source.sequential_order)


# -- Root node + I/O -----------------------------------------------------------

class JsonParseError(Exception):
    """Raised when a document does not conform to the story-graph.json schema."""


class JsonStoryMap(StoryMap):
    """JSON story-map I/O. IS the format-typed tree root.

    parse / render / sync implement the Uniform Callable Surface.
    Factory overrides ensure every child is Json-typed throughout the tree.
    """

    def create_child_epic(self, source: JsonEpic) -> JsonEpic:
        return JsonEpic(source.name, source.sequential_order)

    def create_child_increment(self, source: Increment) -> JsonIncrement:
        return JsonIncrement(source.name, source.sequential_order)

    # -- Uniform Callable Surface ----------------------------------------------

    def render(self, story_map: "JsonStoryMap", previous: Optional[str] = None) -> str:
        payload: Dict[str, Any] = {
            "epics": [self._epic_to_dict(e) for e in story_map.epics],
        }
        if story_map.increments:
            payload["increments"] = [
                self._increment_to_dict(i) for i in story_map.increments
            ]
        return json.dumps(payload, indent=2)

    def parse(self, text: str) -> "JsonStoryMap":
        try:
            payload = json.loads(text)
        except json.JSONDecodeError as err:
            raise JsonParseError(f"Not valid JSON: {err}") from err
        self._guard_schema(payload)
        story_map = JsonStoryMap()
        for epic_dict in payload.get("epics", []):
            story_map.epics.append(self._epic_from_dict(epic_dict))
        for inc_dict in payload.get("increments", []):
            story_map.increments.append(self._increment_from_dict(inc_dict))
        return story_map

    def sync(self, text: str, canonical: "JsonStoryMap") -> UpdateReport:
        return canonical.translate_from(self.parse(text))

    def attach_source_locations(self, file_name: str) -> None:
        """Stamp a single SourceLocation (the JSON file) onto every node."""
        loc = SourceLocation(file_name, 0)
        for epic in self.epics:
            epic.source = loc
        for sub in self.all_sub_epics():
            sub.source = loc
        for story in self.all_stories():
            story.source = loc

    @classmethod
    def from_workspace(cls, root: "Path") -> Optional["JsonStoryMap"]:
        """Find story-graph.json in *root* and parse it; return None if absent."""
        from pathlib import Path as _Path
        root = _Path(root).resolve()
        json_path = root / "story-graph.json"
        if not json_path.exists():
            return None
        try:
            text = json_path.read_text(encoding="utf-8")
            sm = cls().parse(text)
            sm.attach_source_locations(json_path.name)
            sm.source = SourceLocation(json_path.name, 1)
            return sm
        except Exception:
            return None

    # -- render helpers --------------------------------------------------------

    def _epic_to_dict(self, epic: JsonEpic) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "name": epic.name,
            "sequentialOrder": epic.sequential_order,
            "subEpics": [self._sub_epic_to_dict(s) for s in epic.sub_epics],
        }
        if epic.estimate:
            payload["estimate"] = epic.estimate
        factories = list(getattr(epic, "example_factories", None) or [])
        if factories:
            payload["exampleFactories"] = factories
        return payload

    def _sub_epic_to_dict(self, sub_epic: JsonSubEpic) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "name": sub_epic.name,
            "sequentialOrder": sub_epic.sequential_order,
            "subEpics": [self._sub_epic_to_dict(s) for s in sub_epic.sub_epics],
            "stories": [self._story_to_dict(s) for s in sub_epic.stories],
        }
        if sub_epic.estimate:
            payload["estimate"] = sub_epic.estimate
        factories = list(getattr(sub_epic, "example_factories", None) or [])
        if factories:
            payload["exampleFactories"] = factories
        return payload

    def _story_to_dict(self, story: JsonStory) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "name": story.name,
            "sequentialOrder": story.sequential_order,
            "storyType": story.story_type.value,
            "scenarios": [self._scenario_to_dict(s) for s in story.scenarios],
        }
        if story.users:
            payload["users"] = list(story.users)
        if getattr(story, "domain_terms", None):
            payload["domainTerms"] = list(story.domain_terms)
        if getattr(story, "evidence", None):
            payload["evidence"] = list(story.evidence)
        return payload

    def _scenario_to_dict(self, scenario: JsonScenario) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "name": scenario.name,
            "sequentialOrder": scenario.sequential_order,
        }
        rows = list(getattr(scenario, "example_rows", None) or [])
        if rows:
            payload["exampleRows"] = rows
        return payload

    def _increment_to_dict(self, inc: JsonIncrement) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "name": inc.name,
            "sequentialOrder": inc.sequential_order,
            "stories": list(inc.stories),
        }
        if inc.outcome:
            payload["outcome"] = inc.outcome
        if inc.decision_prompt:
            payload["decisionPrompt"] = inc.decision_prompt
        if inc.slicing_notes:
            payload["slicingNotes"] = inc.slicing_notes
        return payload

    # -- parse helpers ---------------------------------------------------------

    def _guard_schema(self, payload: Any) -> None:
        if not isinstance(payload, dict):
            raise JsonParseError("Root must be an object")
        if "epics" not in payload:
            raise JsonParseError("Missing required 'epics' key")
        if not isinstance(payload["epics"], list):
            raise JsonParseError("'epics' must be a list")

    def _epic_from_dict(self, data: Dict[str, Any]) -> JsonEpic:
        epic = JsonEpic(data["name"], int(data.get("sequentialOrder", 0)))
        epic.estimate = str(data.get("estimate", "") or "")
        factories = data.get("exampleFactories") or []
        if factories:
            epic.example_factories = list(factories)
        for sub in data.get("subEpics", []):
            epic.sub_epics.append(self._sub_epic_from_dict(sub))
        return epic

    def _sub_epic_from_dict(self, data: Dict[str, Any]) -> JsonSubEpic:
        sub_epic = JsonSubEpic(data["name"], int(data.get("sequentialOrder", 0)))
        sub_epic.estimate = str(data.get("estimate", "") or "")
        factories = data.get("exampleFactories") or []
        if factories:
            sub_epic.example_factories = list(factories)
        for nested in data.get("subEpics", []):
            sub_epic.sub_epics.append(self._sub_epic_from_dict(nested))
        for story in data.get("stories", []):
            sub_epic.stories.append(self._story_from_dict(story))
        return sub_epic

    def _story_from_dict(self, data: Dict[str, Any]) -> JsonStory:
        story = JsonStory(
            data["name"],
            int(data.get("sequentialOrder", 0)),
            StoryType(data.get("storyType", "user")),
        )
        users = data.get("users")
        if users is None and data.get("actor"):
            users = [data["actor"]]
        if users:
            story.users = list(users) if isinstance(users, list) else [str(users)]
        if data.get("domainTerms"):
            story.domain_terms = list(data["domainTerms"])
        if data.get("evidence"):
            story.evidence = list(data["evidence"])
        for sc in data.get("scenarios", []):
            story.scenarios.append(self._scenario_from_dict(sc))
        return story

    def _scenario_from_dict(self, data: Dict[str, Any]) -> JsonScenario:
        scenario = JsonScenario(
            name=data.get("name", "Scenario"),
            sequential_order=int(data.get("sequentialOrder", 0)),
        )
        rows = data.get("exampleRows") or []
        if rows:
            scenario.example_rows = list(rows)
        return scenario

    def _increment_from_dict(self, data: Dict[str, Any]) -> JsonIncrement:
        inc = JsonIncrement(
            name=data["name"],
            sequential_order=int(data.get("sequentialOrder", 0)),
        )
        inc.stories = list(data.get("stories", []))
        inc.outcome = str(data.get("outcome", "") or "")
        inc.decision_prompt = str(data.get("decisionPrompt", "") or "")
        inc.slicing_notes = str(data.get("slicingNotes", "") or "")
        return inc
