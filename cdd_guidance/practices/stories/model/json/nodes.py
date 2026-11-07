"""JSON format story nodes - all seven StoryNode subtypes plus I/O.

Schema of ``story-graph.json`` (camelCase). Every epic, top-level or nested, has the same shape; nested epics sit
under ``subEpics``:

    {
      "examples": [{"exampleName": "...", "<cell>": "...", ...}],
      "epics": [
        {
          "name": "...",
          "sequentialOrder": 1,
          "estimate": "...",
          "examples": [...],
          "stories": [
            {
              "name": "...", "sequentialOrder": 1, "storyType": "user", "actors": ["..."],
              "backgrounds": [{"name": "background", "steps": [...], "examples": [...]}],
              "scenarios": [
                {"name": "...", "sequentialOrder": 1, "isOutline": false, "steps": [...], "examples": [...]}
              ]
            }
          ],
          "subEpics": [...]
        }
      ],
      "increments": [
        {"name": "...", "sequentialOrder": 1, "outcome": "...", "stories": ["Story name", ...],
         "decisionPrompt": "...", "slicingNotes": "..."}
      ]
    }

A step is ``{"keyword": "Given", "text": "...", "stepType": "given", "ands": [...]}``.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from cdd_guidance.practices.stories.model.source_location import SourceLocation
from cdd_guidance.practices.stories.model.story_model import (
    Background,
    Epic,
    Examples,
    Increment,
    Scenario,
    Step,
    StepType,
    Story,
    StoryModel,
    StoryType,
)

# -- Leaf node types -----------------------------------------------------------

class JsonIncrement(Increment):
    pass


class JsonScenario(Scenario):
    pass


class JsonStory(Story):
    scenario_type = JsonScenario


class JsonEpic(Epic):
    pass


# -- Root node + I/O -----------------------------------------------------------

class JsonParseError(Exception):
    """Raised when a document does not conform to the story-graph.json schema."""


class JsonStoryModel(StoryModel):
    """JSON story-map I/O. render writes a story map as story-graph.json text; parse reads that text into a new map."""

    epic_type = JsonEpic
    story_type = JsonStory
    increment_type = JsonIncrement

    def render(self, story_map: StoryModel, previous: Optional[str] = None) -> str:
        payload: Dict[str, Any] = {
            "epics": [self._epic_to_dict(epic) for epic in story_map.epics],
        }
        records = self._example_records(story_map.examples)
        if records:
            payload["examples"] = records
        if story_map.increments:
            payload["increments"] = [
                self._increment_to_dict(increment) for increment in story_map.increments
            ]
        return json.dumps(payload, indent=2)

    def parse(self, text: str) -> "JsonStoryModel":
        try:
            payload = json.loads(text)
        except json.JSONDecodeError as err:
            raise JsonParseError(f"Not valid JSON: {err}") from err
        self._guard_schema(payload)
        story_map = JsonStoryModel()
        for epic_record in payload.get("epics", []):
            story_map.epics.append(self._epic_from_dict(epic_record))
        self._take_examples(story_map.examples, payload)
        for increment_record in payload.get("increments", []):
            story_map.increments.append(self._increment_from_dict(increment_record))
        return story_map

    def attach_source_locations(self, file_name: str) -> None:
        """Stamp a single SourceLocation (the JSON file) onto every node."""
        loc = SourceLocation(file_name, 0)
        for epic in self.epics:
            epic.source = loc
            epic._stamp_source(loc)

    @classmethod
    def from_workspace(cls, root: Path) -> Optional["JsonStoryModel"]:
        """Find story-graph.json in *root* and parse it; None when the folder has none. A file that is there but does
        not read is a JsonParseError naming the file, not a missing story map."""
        json_path = Path(root).resolve() / "story-graph.json"
        if not json_path.exists():
            return None
        try:
            story_map = cls().parse(json_path.read_text(encoding="utf-8"))
        except JsonParseError as err:
            raise JsonParseError(f"{json_path}: {err}") from err
        story_map.attach_source_locations(json_path.name)
        story_map.source = SourceLocation(json_path.name, 1)
        return story_map

    # -- render helpers --------------------------------------------------------

    def _epic_to_dict(self, epic: Epic) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "name": epic.name,
            "sequentialOrder": epic.sequential_order,
            "subEpics": [self._epic_to_dict(child) for child in epic.epics],
            "stories": [self._story_to_dict(story) for story in epic.stories],
        }
        if epic.estimate:
            payload["estimate"] = epic.estimate
        records = self._example_records(epic.examples)
        if records:
            payload["examples"] = records
        return payload

    def _story_to_dict(self, story: Story) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "name": story.name,
            "sequentialOrder": story.sequential_order,
            "storyType": story.story_type.value,
            "scenarios": [self._scenario_to_dict(scenario) for scenario in story.scenarios],
        }
        if story.backgrounds:
            payload["backgrounds"] = [self._background_to_dict(background) for background in story.backgrounds]
        if story.actors:
            payload["actors"] = list(story.actors)
        if story.domain_terms:
            payload["domainTerms"] = list(story.domain_terms)
        if story.evidence:
            payload["evidence"] = list(story.evidence)
        return payload

    def _scenario_to_dict(self, scenario: Scenario) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "name": scenario.name,
            "sequentialOrder": scenario.sequential_order,
            "steps": [self._step_to_dict(step) for step in scenario.steps],
        }
        if scenario.is_outline:
            payload["isOutline"] = True
        records = self._example_records(scenario.examples)
        if records:
            payload["examples"] = records
        if scenario.backgrounds:
            payload["backgrounds"] = [self._background_to_dict(background) for background in scenario.backgrounds]
        return payload

    def _background_to_dict(self, background: Background) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "name": background.name,
            "steps": [self._step_to_dict(step) for step in background.steps],
        }
        records = self._example_records(background.examples)
        if records:
            payload["examples"] = records
        return payload

    def _step_to_dict(self, step: Step) -> Dict[str, Any]:
        payload: Dict[str, Any] = {"keyword": step.keyword, "text": step.text}
        if step.phase:
            payload["stepType"] = step.phase
        if step.ands:
            payload["ands"] = [self._step_to_dict(extra) for extra in step.ands]
        for key, value in (("concepts", step.concepts), ("values", step.values)):
            if value:
                payload[key] = list(value)
        if step.actor:
            payload["actor"] = step.actor
        return payload

    def _increment_to_dict(self, increment: Increment) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "name": increment.name,
            "sequentialOrder": increment.sequential_order,
            "stories": [story.name for story in increment.stories],
        }
        if increment.outcome:
            payload["outcome"] = increment.outcome
        if increment.decision_prompt:
            payload["decisionPrompt"] = increment.decision_prompt
        if increment.slicing_notes:
            payload["slicingNotes"] = increment.slicing_notes
        return payload

    def _example_records(self, examples: Examples) -> List[Dict[str, str]]:
        """Each example as its name under ``exampleName`` beside its own cells, so a cell named ``example`` stays a
        cell."""
        records = []
        for name, example in examples.items():
            cells = {key: "" if value is None else str(value) for key, value in example.cells().items()}
            records.append({"exampleName": name, **cells})
        return records

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
        for child in epic_record.get("subEpics", []):
            epic.epics.append(self._epic_from_dict(child))
        for story in epic_record.get("stories", []):
            epic.stories.append(self._story_from_dict(story))
        self._take_examples(epic.examples, epic_record)
        return epic

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
        for background in story_record.get("backgrounds") or []:
            story.backgrounds.append(self._background_from_dict(background, len(story.backgrounds) + 1))
        for scenario in story_record.get("scenarios", []):
            story.scenarios.append(self._scenario_from_dict(scenario, story.name))
        return story

    def _scenario_from_dict(self, scenario_record: Dict[str, Any], story_name: str) -> JsonScenario:
        scenario = JsonScenario(
            name=scenario_record.get("name", "Scenario"),
            sequential_order=int(scenario_record.get("sequentialOrder", 0)),
            story_name=story_name,
        )
        scenario.is_outline = bool(scenario_record.get("isOutline", False))
        scenario.steps = self._steps_from(scenario_record)
        self._take_examples(scenario.examples, scenario_record)
        for background in scenario_record.get("backgrounds") or []:
            scenario.backgrounds.append(self._background_from_dict(background, len(scenario.backgrounds) + 1))
        return scenario

    def _background_from_dict(self, record: Dict[str, Any], order: int) -> Background:
        background = Background(record.get("name") or "background", order)
        background.steps = self._steps_from(record)
        self._take_examples(background.examples, record)
        return background

    def _steps_from(self, record: Dict[str, Any]) -> List[Step]:
        return [self._step_from_dict(step, order) for order, step in enumerate(record.get("steps") or [], start=1)]

    def _step_from_dict(self, record: Dict[str, Any], order: int) -> Step:
        phase = record.get("stepType")
        step = Step(
            str(record.get("text", "")),
            StepType(phase) if phase else None,
            order,
            keyword=str(record.get("keyword", "")),
            concepts=list(record.get("concepts") or []),
            values=list(record.get("values") or []),
            actor=str(record.get("actor", "") or ""),
        )
        step.ands = [self._step_from_dict(extra, index) for index, extra in enumerate(record.get("ands") or [], start=1)]
        return step

    def _take_examples(self, examples: Examples, record: Dict[str, Any]) -> None:
        for index, record_cells in enumerate(record.get("examples") or [], start=1):
            label = str(record_cells.get("exampleName") or record_cells.get("example") or record_cells.get("name") or f"example-{index}")
            cells = {key: value for key, value in record_cells.items() if key != "exampleName"}
            examples[label] = cells if set(cells) - {"example"} else label

    def _increment_from_dict(self, increment_record: Dict[str, Any]) -> JsonIncrement:
        stories = []
        for index, name in enumerate(increment_record.get("stories", []), start=1):
            story_name = name.get("name") if isinstance(name, dict) else str(name)
            stories.append(Story(story_name, index))
        increment = JsonIncrement(
            name=increment_record["name"],
            sequential_order=int(increment_record.get("sequentialOrder", 0)),
            stories=stories,
        )
        increment.outcome = str(increment_record.get("outcome", "") or "")
        increment.decision_prompt = str(increment_record.get("decisionPrompt", "") or "")
        increment.slicing_notes = str(increment_record.get("slicingNotes", "") or "")
        return increment
