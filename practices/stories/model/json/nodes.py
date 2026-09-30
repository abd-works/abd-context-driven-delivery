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

from practices.stories.model.story_model import Epic, Story, StoryType, Epic
from practices.stories.model.story_model import Scenario
from practices.stories.model.source_location import SourceLocation
from practices.stories.model.story_model import StoryMap
from practices.stories.model.story_model import Increment

# -- Leaf node types -----------------------------------------------------------

class JsonIncrement(Increment):
    pass


class JsonScenario(Scenario):
    def load_scenario(self, source: Scenario) -> "JsonScenario":
        return JsonScenario(source.name, source.sequential_order, source.story_name)


class JsonStory(Story):
    def load_scenario(self, source: Scenario) -> JsonScenario:
        return JsonScenario(source.name, source.sequential_order, source.story_name)


class JsonEpic(Epic):
    def load_epic(self, source: Epic) -> "JsonEpic":
        return JsonEpic(source.name, source.sequential_order)

    def load_story(self, source: Story) -> JsonStory:
        return JsonStory(source.name, source.sequential_order, source.story_type)


# -- Root node + I/O -----------------------------------------------------------

class JsonParseError(Exception):
    """Raised when a document does not conform to the story-graph.json schema."""


class JsonStoryMap(StoryMap):
    epic_type = JsonEpic
    story_type = JsonStory
    increment_type = JsonIncrement
    """JSON story-map I/O. IS the format-typed tree root.

    parse / render / sync implement the Uniform Callable Surface.
    Factory overrides ensure every child is Json-typed throughout the tree.
    """

    def load_epic(self, source: JsonEpic) -> JsonEpic:
        return JsonEpic(source.name, source.sequential_order)

    def load_increment(self, source: Increment) -> JsonIncrement:
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

    def attach_source_locations(self, file_name: str) -> None:
        """Stamp a single SourceLocation (the JSON file) onto every node."""
        loc = SourceLocation(file_name, 0)
        for epic in self.epics:
            epic.source = loc
            epic._stamp_source(loc)

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
            "subEpics": [self._sub_epic_to_dict(s) for s in epic.epics],
        }
        if epic.estimate:
            payload["estimate"] = epic.estimate
        return payload

    def _sub_epic_to_dict(self, sub_epic: JsonEpic) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "name": sub_epic.name,
            "sequentialOrder": sub_epic.sequential_order,
            "subEpics": [self._sub_epic_to_dict(s) for s in sub_epic.epics],
            "stories": [self._story_to_dict(s) for s in sub_epic.stories],
        }
        if sub_epic.estimate:
            payload["estimate"] = sub_epic.estimate
        return payload

    def _story_to_dict(self, story: JsonStory) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "name": story.name,
            "sequentialOrder": story.sequential_order,
            "storyType": story.story_type.value,
            "scenarios": [self._scenario_to_dict(s) for s in story.scenarios],
        }
        if story.actors:
            payload["actors"] = list(story.actors)
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
        rows = scenario.examples.table()
        if rows:
            payload["exampleRows"] = rows
        return payload

    def _increment_to_dict(self, inc: JsonIncrement) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "name": inc.name,
            "sequentialOrder": inc.sequential_order,
            "stories": [story.name for story in inc.stories],
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

    def _epic_from_dict(self, epic_record: Dict[str, Any]) -> JsonEpic:
        epic = JsonEpic(epic_record["name"], int(epic_record.get("sequentialOrder", 0)))
        epic.estimate = str(epic_record.get("estimate", "") or "")
        for sub in epic_record.get("subEpics", []):
            epic.epics.append(self._sub_epic_from_dict(sub))
        return epic

    def _sub_epic_from_dict(self, sub_epic_record: Dict[str, Any]) -> JsonEpic:
        sub_epic = JsonEpic(sub_epic_record["name"], int(sub_epic_record.get("sequentialOrder", 0)))
        sub_epic.estimate = str(sub_epic_record.get("estimate", "") or "")
        for nested in sub_epic_record.get("subEpics", []):
            sub_epic.epics.append(self._sub_epic_from_dict(nested))
        for story in sub_epic_record.get("stories", []):
            sub_epic.stories.append(self._story_from_dict(story))
        return sub_epic

    def _story_from_dict(self, story_record: Dict[str, Any]) -> JsonStory:
        story = JsonStory(
            story_record["name"],
            int(story_record.get("sequentialOrder", 0)),
            StoryType(story_record.get("storyType", "user")),
        )
        actors = story_record.get("actors")
        if actors is None and story_record.get("actor"):
            actors = [story_record["actor"]]
        if actors:
            story.actors = list(actors) if isinstance(actors, list) else [str(actors)]
        if story_record.get("domainTerms"):
            story.domain_terms = list(story_record["domainTerms"])
        if story_record.get("evidence"):
            story.evidence = list(story_record["evidence"])
        for sc in story_record.get("scenarios", []):
            story.scenarios.append(self._scenario_from_dict(sc))
        return story

    def _scenario_from_dict(self, scenario_record: Dict[str, Any]) -> JsonScenario:
        scenario = JsonScenario(
            name=scenario_record.get("name", "Scenario"),
            sequential_order=int(scenario_record.get("sequentialOrder", 0)),
        )
        for index, row in enumerate(scenario_record.get("exampleRows") or [], start=1):
            label = str(row.get("example") or row.get("name") or f"example-{index}")
            scenario.examples[label] = dict(row)
        return scenario

    def _increment_from_dict(self, increment_record: Dict[str, Any]) -> JsonIncrement:
        stories = []
        for index, name in enumerate(increment_record.get("stories", []), start=1):
            story_name = name.get("name") if isinstance(name, dict) else str(name)
            stories.append(Story(story_name, index))
        inc = JsonIncrement(
            name=increment_record["name"],
            sequential_order=int(increment_record.get("sequentialOrder", 0)),
            stories=stories,
        )
        inc.outcome = str(increment_record.get("outcome", "") or "")
        inc.decision_prompt = str(increment_record.get("decisionPrompt", "") or "")
        inc.slicing_notes = str(increment_record.get("slicingNotes", "") or "")
        return inc
