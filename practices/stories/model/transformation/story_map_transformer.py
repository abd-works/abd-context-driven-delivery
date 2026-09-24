"""Stories transformation channel — wrap live story-map types with Transformer."""

from __future__ import annotations

from jinja2 import Environment

from harness.transformers.transformer import Transformer
from practices.stories.model.background import Background as SourceBackground
from practices.stories.model.code_story_map import to_kebab, to_pascal, to_snake
from practices.stories.model.example import Example as SourceExample
from practices.stories.model.markdown.nodes import MarkdownStoryMap
from practices.stories.model.nodes import (
    Epic as SourceEpic,
    Story as SourceStory,
    SubEpic as SourceSubEpic,
)
from practices.stories.model.python.story_file import render_story_file
from practices.stories.model.python.tree import PythonTree
from practices.stories.model.scenario import Scenario as SourceScenario
from practices.stories.model.step import Step as SourceStep
from practices.stories.model.story_map import StoryMap as SourceStoryMap

_LENS = "stories:"
_NEXT_LENSES = ("ce:", "bdd:", "ddd:", "ux:")
_SKIP_PREFIXES = ("given ", "when ", "then ", "and ", "but ")


class StoryMapTransformer(SourceStoryMap, Transformer):
    @classmethod
    def load(cls, sketch: str) -> "StoryMapTransformer":
        parsed = MarkdownStoryMap().parse(_stories_outline(sketch))
        root = cls()
        for epic in parsed.epics:
            root.append_epic(root.load_epic(epic))
        _attach_scenarios(root, sketch)
        return root

    def load_epic(self, source: SourceEpic) -> "EpicTransformer":
        epic = EpicTransformer(source.name, source.sequential_order)
        for sub in source.sub_epics:
            epic.sub_epics.append(epic.load_sub_epic(sub))
        return epic

    def children(self) -> list:
        return list(self.epics)

    def attach_environment(self, environment: Environment, root: Transformer | None = None) -> None:
        _bind_python_filters(environment)
        super().attach_environment(environment, root)


class EpicTransformer(SourceEpic, Transformer):
    _logical_template = "epic"

    def load_sub_epic(self, source: SourceSubEpic) -> "SubEpicTransformer":
        sub = SubEpicTransformer(source.name, source.sequential_order)
        for nested in source.sub_epics:
            sub.sub_epics.append(sub.load_sub_epic(nested))
        for story in source.stories:
            sub.stories.append(sub.load_story(story))
        return sub

    def children(self) -> list:
        return list(self.sub_epics)

    def _output_path(self) -> str:
        folder = f"{self._tests_folder}/{to_kebab(self.name)}"
        return f"{folder}/{to_snake(self.name)}_helper.py"

    def _child_folder(self) -> str:
        return f"{self._tests_folder}/{to_kebab(self.name)}"


class SubEpicTransformer(SourceSubEpic, Transformer):
    def load_sub_epic(self, source: SourceSubEpic) -> "SubEpicTransformer":
        nested = SubEpicTransformer(source.name, source.sequential_order)
        for child in source.sub_epics:
            nested.sub_epics.append(nested.load_sub_epic(child))
        for story in source.stories:
            nested.stories.append(nested.load_story(story))
        return nested

    def load_story(self, source: SourceStory) -> "StoryTransformer":
        story = StoryTransformer(source.name, source.sequential_order, source.story_type)
        story.users = list(source.users)
        return story

    def children(self) -> list:
        return list(self.sub_epics) + list(self.stories)

    def _child_folder(self) -> str:
        return f"{self._tests_folder}/{to_kebab(self.name)}"


class StoryTransformer(SourceStory, Transformer):
    _logical_template = "story"

    def children(self) -> list:
        return list(self.scenarios)

    def _output_path(self) -> str:
        folder = f"{self._tests_folder}/{to_kebab(self.name)}"
        return f"{folder}/{to_snake(self.name)}_story.test.py"


class ScenarioTransformer(SourceScenario, Transformer):
    def children(self) -> list:
        return list(getattr(self, "steps", []) or [])


class BackgroundTransformer(SourceBackground, Transformer):
    pass


class StepTransformer(SourceStep, Transformer):
    pass


class ExampleTransformer(SourceExample, Transformer):
    pass


def _bind_python_filters(environment: Environment) -> None:
    environment.filters["snake"] = to_snake
    environment.filters["kebab"] = to_kebab
    environment.filters["pascal"] = to_pascal
    environment.filters["story_python"] = render_story_file
    environment.filters["epic_python"] = PythonTree()._render_epic_helper


def _stories_outline(sketch: str) -> str:
    lines: list[str] = []
    for raw in _lens_body(sketch).splitlines():
        stripped = raw.strip()
        if _skip_line(stripped):
            continue
        indent = (len(raw) - len(raw.lstrip(" "))) // 4
        if indent >= 3:
            continue
        if "-->" in stripped:
            actor, name = [part.strip() for part in stripped.split("-->", 1)]
            lines.append(f"{'    ' * indent}(S) {actor} --> {name}")
            continue
        lines.append(f"{'    ' * indent}(E) {stripped}")
    return "\n".join(lines)


def _attach_scenarios(root: StoryMapTransformer, sketch: str) -> None:
    remaining = list(_all_stories(root))
    current: StoryTransformer | None = None
    for raw in _lens_body(sketch).splitlines():
        stripped = raw.strip()
        indent = (len(raw) - len(raw.lstrip(" "))) // 4
        if "-->" in stripped and not stripped.startswith("//"):
            name = stripped.split("-->", 1)[1].strip()
            current = _take_story(remaining, name)
            continue
        if current is None or indent != 3 or _skip_line(stripped):
            continue
        current.scenarios.append(
            ScenarioTransformer(stripped, len(current.scenarios) + 1, current.name)
        )


def _take_story(remaining: list[StoryTransformer], name: str) -> StoryTransformer | None:
    for index, story in enumerate(remaining):
        if story.name == name:
            return remaining.pop(index)
    return None


def _all_stories(root: StoryMapTransformer) -> list[StoryTransformer]:
    stories: list[StoryTransformer] = []
    for epic in root.epics:
        for sub in epic.sub_epics:
            stories.extend(_stories_under(sub))
    return stories


def _stories_under(sub: SubEpicTransformer) -> list[StoryTransformer]:
    stories: list[StoryTransformer] = []
    for nested in sub.sub_epics:
        stories.extend(_stories_under(nested))
    stories.extend(sub.stories)
    return stories


def _skip_line(stripped: str) -> bool:
    if not stripped or stripped.startswith("//") or stripped.startswith("*"):
        return True
    if stripped.startswith("~>"):
        return True
    lower = stripped.lower()
    return lower.startswith(_SKIP_PREFIXES)


def _lens_body(sketch: str) -> str:
    lines = sketch.splitlines()
    start = next((i for i, line in enumerate(lines) if line.startswith(_LENS)), None)
    if start is None:
        return sketch
    end = len(lines)
    for i in range(start + 1, len(lines)):
        if any(lines[i].startswith(marker) for marker in _NEXT_LENSES):
            end = i
            break
    return "\n".join(lines[start + 1 : end])
