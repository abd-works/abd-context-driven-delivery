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


# -- Records of the plain parts every story node holds -------------------------

def _example_records(examples: Examples) -> List[Dict[str, str]]:
    """Each example as its name under ``exampleName`` beside its own cells, so a cell named ``example`` stays a
    cell."""
    records = []
    for name, example in examples.items():
        cells = {key: "" if value is None else str(value) for key, value in example.cells().items()}
        records.append({"exampleName": name, **cells})
    return records


def _take_examples(examples: Examples, record: Dict[str, Any]) -> None:
    for index, record_cells in enumerate(record.get("examples") or [], start=1):
        label = str(record_cells.get("exampleName") or record_cells.get("example") or record_cells.get("name") or f"example-{index}")
        cells = {key: value for key, value in record_cells.items() if key != "exampleName"}
        examples[label] = cells if set(cells) - {"example"} else label


def _step_record(step: Step) -> Dict[str, Any]:
    payload: Dict[str, Any] = {"keyword": step.keyword, "text": step.text}
    if step.phase:
        payload["stepType"] = step.phase
    if step.ands:
        payload["ands"] = [_step_record(extra) for extra in step.ands]
    for key, value in (("concepts", step.concepts), ("values", step.values)):
        if value:
            payload[key] = list(value)
    if step.actor:
        payload["actor"] = step.actor
    return payload


def _step_from_record(record: Dict[str, Any], order: int) -> Step:
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
    step.ands = [_step_from_record(extra, index) for index, extra in enumerate(record.get("ands") or [], start=1)]
    return step


def _steps_from(record: Dict[str, Any]) -> List[Step]:
    return [_step_from_record(step, order) for order, step in enumerate(record.get("steps") or [], start=1)]


def _background_record(background: Background) -> Dict[str, Any]:
    payload: Dict[str, Any] = {
        "name": background.name,
        "steps": [_step_record(step) for step in background.steps],
    }
    records = _example_records(background.examples)
    if records:
        payload["examples"] = records
    return payload


def _background_from_record(record: Dict[str, Any], order: int) -> Background:
    background = Background(record.get("name") or "background", order)
    background.steps = _steps_from(record)
    _take_examples(background.examples, record)
    return background


# -- Leaf node types: each reads and writes its own record ----------------------

class JsonIncrement(Increment):
    def as_record(self) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "name": self.name,
            "sequentialOrder": self.sequential_order,
            "stories": [story.name for story in self.stories],
        }
        if self.outcome:
            payload["outcome"] = self.outcome
        if self.decision_prompt:
            payload["decisionPrompt"] = self.decision_prompt
        if self.slicing_notes:
            payload["slicingNotes"] = self.slicing_notes
        return payload

    @classmethod
    def from_record(cls, record: Dict[str, Any]) -> "JsonIncrement":
        """The increment a record lists, with a story for each name it gives."""
        named = [item.get("name") if isinstance(item, dict) else str(item) for item in record.get("stories", [])]
        increment = cls(
            name=record["name"],
            sequential_order=int(record.get("sequentialOrder", 0)),
            stories=[Story(name, index) for index, name in enumerate(named, start=1)],
        )
        increment.outcome = str(record.get("outcome", "") or "")
        increment.decision_prompt = str(record.get("decisionPrompt", "") or "")
        increment.slicing_notes = str(record.get("slicingNotes", "") or "")
        return increment


class JsonScenario(Scenario):
    def as_record(self) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "name": self.name,
            "sequentialOrder": self.sequential_order,
            "steps": [_step_record(step) for step in self.steps],
        }
        if self.is_outline:
            payload["isOutline"] = True
        records = _example_records(self.examples)
        if records:
            payload["examples"] = records
        if self.backgrounds:
            payload["backgrounds"] = [_background_record(background) for background in self.backgrounds]
        return payload

    @classmethod
    def from_record(cls, record: Dict[str, Any], story_name: str) -> "JsonScenario":
        scenario = cls(
            name=record.get("name", "Scenario"),
            sequential_order=int(record.get("sequentialOrder", 0)),
            story_name=story_name,
        )
        scenario.is_outline = bool(record.get("isOutline", False))
        scenario.steps = _steps_from(record)
        _take_examples(scenario.examples, record)
        for background in record.get("backgrounds") or []:
            scenario.backgrounds.append(_background_from_record(background, len(scenario.backgrounds) + 1))
        return scenario


class JsonStory(Story):
    scenario_type = JsonScenario

    def as_record(self) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "name": self.name,
            "sequentialOrder": self.sequential_order,
            "storyType": self.story_type.value,
            "scenarios": [scenario.as_record() for scenario in self.scenarios],
        }
        if self.backgrounds:
            payload["backgrounds"] = [_background_record(background) for background in self.backgrounds]
        if self.actors:
            payload["actors"] = list(self.actors)
        if self.domain_terms:
            payload["domainTerms"] = list(self.domain_terms)
        if self.evidence:
            payload["evidence"] = list(self.evidence)
        return payload

    @classmethod
    def from_record(cls, record: Dict[str, Any]) -> "JsonStory":
        story = cls(
            record["name"],
            int(record.get("sequentialOrder", 0)),
            StoryType(record.get("storyType", "user")),
        )
        actors = record.get("actors")
        if actors is None and record.get("actor"):
            actors = [record["actor"]]
        if actors:
            story.actors = list(actors) if isinstance(actors, list) else [str(actors)]
        if record.get("domainTerms"):
            story.domain_terms = list(record["domainTerms"])
        if record.get("evidence"):
            story.evidence = list(record["evidence"])
        for background in record.get("backgrounds") or []:
            story.backgrounds.append(_background_from_record(background, len(story.backgrounds) + 1))
        for scenario in record.get("scenarios", []):
            story.scenarios.append(JsonScenario.from_record(scenario, story.name))
        return story


class JsonEpic(Epic):
    def as_record(self) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "name": self.name,
            "sequentialOrder": self.sequential_order,
            "subEpics": [child.as_record() for child in self.epics],
            "stories": [story.as_record() for story in self.stories],
        }
        if self.estimate:
            payload["estimate"] = self.estimate
        records = _example_records(self.examples)
        if records:
            payload["examples"] = records
        return payload

    @classmethod
    def from_record(cls, record: Dict[str, Any]) -> "JsonEpic":
        epic = cls(record["name"], int(record.get("sequentialOrder", 0)))
        epic.estimate = str(record.get("estimate", "") or "")
        for child in record.get("subEpics", []):
            epic.epics.append(cls.from_record(child))
        for story in record.get("stories", []):
            epic.stories.append(JsonStory.from_record(story))
        _take_examples(epic.examples, record)
        return epic


# -- Root node + I/O -----------------------------------------------------------

class JsonParseError(Exception):
    """Raised when a document does not conform to the story-graph.json schema."""


class JsonStoryModel(StoryModel):
    """The story map as story-graph.json. render copies a story map into this format and writes it; parse reads the
    text into this map."""

    epic_type = JsonEpic
    story_type = JsonStory
    increment_type = JsonIncrement

    def render(self, story_map: StoryModel, previous: Optional[str] = None) -> str:
        """The story map as story-graph.json text: copied into a JSON map, which writes itself."""
        return (story_map if isinstance(story_map, JsonStoryModel) else type(self)(story_map)).save()

    def save(self) -> str:
        payload: Dict[str, Any] = {"epics": [epic.as_record() for epic in self.epics]}
        records = _example_records(self.examples)
        if records:
            payload["examples"] = records
        if self.increments:
            payload["increments"] = [increment.as_record() for increment in self.increments]
        return json.dumps(payload, indent=2)

    def parse(self, text: str) -> "JsonStoryModel":
        """Read story-graph.json text into this map, and return it."""
        try:
            payload = json.loads(text)
        except json.JSONDecodeError as err:
            raise JsonParseError(f"Not valid JSON: {err}") from err
        self._guard_schema(payload)
        self.epics = [JsonEpic.from_record(record) for record in payload.get("epics", [])]
        _take_examples(self.examples, payload)
        self.increments = [JsonIncrement.from_record(record) for record in payload.get("increments", [])]
        return self

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

    def _guard_schema(self, payload: Any) -> None:
        if not isinstance(payload, dict):
            raise JsonParseError("Root must be an object")
        if "epics" not in payload:
            raise JsonParseError("Missing required 'epics' key")
        if not isinstance(payload["epics"], list):
            raise JsonParseError("'epics' must be a list")
