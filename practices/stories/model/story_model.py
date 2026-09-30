"""Story map nodes: StoryNode, StoryMap, Epic, Story, Scenario, Step, Background, Example, Increment.

A nested epic is an epic whose parent is an epic. Each node type implements clone.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Dict, List, Optional

from .source_location import SourceLocation


class StoryNode(ABC):
    """Abstract base. Subclasses declare `_semantic_type_name` so cross-format nodes
    (e.g. MarkdownEpic vs JsonEpic) share one semantic axis."""

    _semantic_type_name: str = "StoryNode"

    def __init__(self, name: str, sequential_order: int):
        self.name = name
        self.sequential_order = sequential_order
        self.parent: Optional[StoryNode] = None
        # Shaping outline sizing (e.g. "approx 2-3 more stories (...)").
        # Meaningful on Epic/Epic; empty on Story and below.
        self.estimate: str = ""

    def semantic_type(self) -> str:
        return self._semantic_type_name

    @abstractmethod
    def clone(self) -> "StoryNode":
        """Return a new copy of this node, including its children."""


class Example(StoryNode):
    """One named example. `value` is any object and defaults to a field map.

    `scope` is the story node that shares this example: a background, a scenario,
    a sub-epic, an epic, or the story map.
    """

    _semantic_type_name = "Example"

    def __init__(
        self,
        name: str,
        value: Any = None,
        sequential_order: int = 0,
        scope: Optional["StoryNode"] = None,
    ) -> None:
        super().__init__(name=name, sequential_order=sequential_order)
        self.value = {} if value is None else value
        self.scope = scope

    def clone(self) -> "Example":
        value = dict(self.value) if isinstance(self.value, dict) else self.value
        return type(self)(self.name, value, self.sequential_order, self.scope)

    def cells(self) -> Dict[str, Any]:
        """Columns for a table row, whether the value is a field map or an object."""
        value = self.value
        if isinstance(value, dict):
            return dict(value)
        if isinstance(value, type):
            return {name: "" for name in getattr(value, "__annotations__", {})}
        if isinstance(value, str):
            return {}
        try:
            items = vars(value).items()
        except TypeError:
            return {}
        return {
            name: item
            for name, item in items
            if not name.startswith("_")
        }

    def as_code(self) -> str:
        """A code literal for this value: a field map, a class, or a constructor call."""
        value = self.value
        if isinstance(value, dict):
            return repr(value)
        if isinstance(value, type):
            return f"{value.__name__}()"
        arguments = ", ".join(f"{name}={item!r}" for name, item in self.cells().items())
        return f"{type(value).__name__}({arguments})"


class Examples(dict):
    """Example name to value. Iterates as a table and each value can be written as code.

    `scope` is the story node these examples belong to. Putting an example in the
    map sets `example.scope` to that node.
    """

    def __init__(self, scope: Optional["StoryNode"] = None) -> None:
        super().__init__()
        self.scope = scope

    def __setitem__(self, name: str, value: Any) -> None:
        if not isinstance(value, Example):
            value = Example(str(name), value)
        value.scope = self.scope
        super().__setitem__(name, value)

    def clone(self, scope: Optional["StoryNode"] = None) -> "Examples":
        copied = type(self)(self.scope if scope is None else scope)
        for name, example in self.items():
            copied[name] = example.clone()
        return copied

    def table(self) -> List[Dict[str, str]]:
        records: List[Dict[str, Any]] = []
        columns: List[str] = []
        for name, example in self.items():
            cells: Dict[str, Any] = {"example": name}
            cells.update(example.cells())
            for key in cells:
                if key not in columns:
                    columns.append(key)
            records.append(cells)
        return [
            {column: "" if record.get(column) is None else str(record.get(column, "")) for column in columns}
            for record in records
        ]


class Increment(StoryNode):
    _semantic_type_name = "Increment"

    def __init__(
        self,
        name: "str | Increment",
        sequential_order: int = 0,
        stories: Optional[List["Story"]] = None,
        *,
        story_class: Optional[type] = None,
    ) -> None:
        source = name if isinstance(name, Increment) else None
        super().__init__(
            name=source.name if source is not None else name,
            sequential_order=source.sequential_order if source is not None else sequential_order,
        )
        self.parent: Optional["StoryMap"] = None
        self.outcome: str = source.outcome if source is not None else ""
        self.slicing_notes: str = source.slicing_notes if source is not None else ""
        self.decision_prompt: str = source.decision_prompt if source is not None else ""
        self.source: Optional[SourceLocation] = source.source if source is not None else None
        self.stories: List["Story"] = []
        if source is None:
            for story in stories or []:
                story.increment = self
                self.stories.append(story)
            return
        build = story_class or Story
        for story in source.stories:
            copied = build(story)
            copied.increment = self
            self.stories.append(copied)

    def clone(self) -> "Increment":
        cloned = type(self)(
            self.name,
            self.sequential_order,
            [story.clone() for story in self.stories],
        )
        cloned.outcome = self.outcome
        cloned.slicing_notes = self.slicing_notes
        cloned.decision_prompt = self.decision_prompt
        cloned.source = self.source
        return cloned


class Step(StoryNode):
    _semantic_type_name = "Step"

    def __init__(
        self,
        text: "str | Step",
        step_type: "StepType | None" = None,
        sequential_order: int = 0,
        *,
        keyword: str = "",
        concepts: Optional[List[str]] = None,
        values: Optional[List[str]] = None,
        actor: str = "",
        source: Optional[SourceLocation] = None,
        name: str = "",
    ) -> None:
        origin = text if isinstance(text, Step) else None
        if origin is not None:
            text = origin.text
            step_type = origin.step_type
            sequential_order = origin.sequential_order
            keyword = origin._keyword
            concepts = list(origin.concepts)
            values = list(origin.values)
            actor = origin.actor
            source = origin.source
            name = origin.name
        label = name or (text.strip()[:80] if text.strip() else f"step-{sequential_order}")
        super().__init__(name=label, sequential_order=sequential_order)
        self.text = text
        self.step_type = step_type
        self._keyword = (keyword or "").strip()
        self._ands: List["Step"] = []
        self.concepts: List[str] = list(concepts) if concepts is not None else []
        self.values: List[str] = list(values) if values is not None else []
        self.actor = actor
        self.source = source
        if origin is not None:
            for extra in origin.ands:
                self._ands.append(type(self)(extra))

    @property
    def ands(self) -> List["Step"]:
        """And and But lines on this step, in order."""
        return sorted(self._ands, key=lambda step: step.sequential_order)

    @ands.setter
    def ands(self, ands: List["Step"]) -> None:
        self._ands = list(ands)

    @property
    def keyword(self) -> str:
        """Gherkin keyword on the line: Given, When, Then, And, or But."""
        if self._keyword:
            return self._keyword[0].upper() + self._keyword[1:].lower()
        value = getattr(self.step_type, "value", self.step_type)
        return str(value).capitalize()

    def clone(self) -> "Step":
        cloned = type(self)(
            text=self.text,
            step_type=self.step_type,
            sequential_order=self.sequential_order,
            keyword=self._keyword,
            concepts=list(self.concepts),
            values=list(self.values),
            actor=self.actor,
            source=self.source,
            name=self.name,
        )
        cloned.ands = [step.clone() for step in self.ands]
        return cloned


class Background(StoryNode):
    _semantic_type_name = "Background"

    def __init__(self, name: "str | Background" = "background", sequential_order: int = 1) -> None:
        source = name if isinstance(name, Background) else None
        super().__init__(
            name=source.name if source is not None else name,
            sequential_order=source.sequential_order if source is not None else sequential_order,
        )
        self._steps: List["Step"] = []
        self.examples = source.examples.clone(self) if source is not None else Examples(self)
        if source is not None:
            for step in source.steps:
                self._steps.append(Step(step))

    @property
    def steps(self) -> List["Step"]:
        return sorted(self._steps, key=lambda step: step.sequential_order)

    @steps.setter
    def steps(self, steps: List["Step"]) -> None:
        self._steps = list(steps)

    def clone(self) -> "Background":
        cloned = type(self)(self.name, self.sequential_order)
        cloned.steps = [step.clone() for step in self.steps]
        cloned.examples = self.examples.clone(cloned)
        return cloned


class StepType(str, Enum):
    """Given, When, or Then. A step's list is this type."""

    GIVEN = "given"
    WHEN = "when"
    THEN = "then"


class Scenario(StoryNode):
    """Behaviour walk-through under a story.

    Tree children: Background, Step, Example.
    """

    _semantic_type_name = "Scenario"

    def __init__(
        self,
        name: "str | Scenario" = "",
        sequential_order: int = 0,
        story_name: str = "",
    ) -> None:
        source = name if isinstance(name, Scenario) else None
        super().__init__(
            name=source.name if source is not None else name,
            sequential_order=source.sequential_order if source is not None else sequential_order,
        )
        self.story_name: str = source.story_name if source is not None else story_name
        self.backgrounds: List[Background] = []
        self.steps: List[Step] = []
        self.examples = source.examples.clone(self) if source is not None else Examples(self)
        self.is_outline: bool = source.is_outline if source is not None else False
        self.evidence: List[str] = list(source.evidence) if source is not None else []
        self.source: Optional[SourceLocation] = source.source if source is not None else None
        if source is not None:
            for background in source.backgrounds:
                self.backgrounds.append(Background(background))
            for step in source.steps:
                self.steps.append(Step(step))

    def steps_in(self, step_type: StepType) -> List[Step]:
        return [step for step in self.steps if step.step_type == step_type]

    def when_then_runs(self) -> List[tuple]:
        """Walk steps. A When after a Then starts the next run."""
        runs: List[tuple] = []
        when_steps: List[Step] = []
        then_steps: List[Step] = []

        def close() -> None:
            nonlocal when_steps, then_steps
            if when_steps or then_steps:
                runs.append((when_steps, then_steps))
            when_steps, then_steps = [], []

        for step in self.steps:
            if step.step_type == StepType.WHEN:
                if then_steps:
                    close()
                when_steps.append(step)
            elif step.step_type == StepType.THEN:
                then_steps.append(step)
        close()
        return runs

    def clone(self) -> "Scenario":
        cloned = type(self)(self.name, self.sequential_order, self.story_name)
        cloned.is_outline = self.is_outline
        cloned.evidence = list(self.evidence)
        cloned.source = self.source
        for background in self.backgrounds:
            cloned.backgrounds.append(background.clone())
        for step in self.steps:
            cloned.steps.append(step.clone())
        cloned.examples = self.examples.clone(cloned)
        return cloned


class StoryType(str, Enum):
    USER = "user"
    SYSTEM = "system"
    TECHNICAL = "technical"


class Epic(StoryNode):
    """An epic. A nested epic is an epic whose parent is an epic."""

    _semantic_type_name = "Epic"

    def __init__(self, name: "str | Epic", sequential_order: int = 0, *, story_class: Optional[type] = None):
        source = name if isinstance(name, Epic) else None
        super().__init__(
            source.name if source is not None else name,
            source.sequential_order if source is not None else sequential_order,
        )
        self.epics: List[Epic] = []
        self.stories: List[Story] = []
        self.examples = Examples(self)
        if source is None:
            return
        self.estimate = source.estimate or ""
        build_story = story_class or Story
        for child in source.epics:
            self.append_epic(type(self)(child, story_class=build_story))
        for story in source.stories:
            self.append_story(build_story(story))

    @property
    def has_epics(self) -> bool:
        return len(self.epics) > 0

    def estimate_label(self) -> str:
        estimate = (self.estimate or "").strip()
        if not estimate:
            return ""
        if estimate.startswith("*"):
            return estimate
        return f"* {estimate}"

    def clone(self) -> "Epic":
        cloned = type(self)(self.name, self.sequential_order)
        cloned.estimate = self.estimate or ""
        for child in self.epics:
            cloned.epics.append(child.clone())
        for story in self.stories:
            cloned.stories.append(story.clone())
        cloned.examples = self.examples.clone(cloned)
        for child in cloned.epics:
            child.parent = cloned
        for story in cloned.stories:
            story.parent = cloned
        return cloned

    def append_epic(self, epic: "Epic") -> None:
        epic.parent = self
        self.epics.append(epic)

    def append_story(self, story: "Story") -> None:
        story.parent = self
        self.stories.append(story)

    def _stamp_source(self, loc) -> None:
        for child in self.epics:
            child.source = loc
            child._stamp_source(loc)
        for story in self.stories:
            story.source = loc

    def _stamp_epic(self, name: str, loc) -> bool:
        for child in self.epics:
            if child.name == name and not getattr(child, "source", None):
                child.source = loc
                return True
            if child._stamp_epic(name, loc):
                return True
        return False

    def _stamp_story(self, name: str, loc) -> bool:
        for child in self.epics:
            if child._stamp_story(name, loc):
                return True
        for story in self.stories:
            if story.name == name and not getattr(story, "source", None):
                story.source = loc
                return True
        return False

    def _has_estimate(self) -> bool:
        if (self.estimate or "").strip():
            return True
        return any(child._has_estimate() for child in self.epics)

    def span_columns(self) -> int:
        """Story-grid columns this epic occupies. An empty epic is one column."""
        if not self.epics:
            return 1
        return sum(max(child.diagram_span_columns(), 1) for child in self.epics)

    def layout_column_count(self) -> int:
        """Story grid columns. Named stories only. Estimates are not story cells."""
        nested = sum(child.layout_column_count() for child in self.epics)
        own = len(self.stories)
        if self.epics:
            return max(nested + own, 1)
        return own

    def diagram_span_columns(self) -> int:
        """Bar width in story-pitch columns. Stories and nested epics both consume columns.

        Estimates widen a leaf epic.
        """
        nested = sum(child.diagram_span_columns() for child in self.epics)
        story_cols = len(self.stories)
        if self.epics:
            return max(nested + story_cols, 1)
        estimate = self.estimate.strip()
        if not estimate:
            return max(story_cols, 1)
        if story_cols == 0:
            return max(2, min(8, (len(estimate) + 12) // 18))
        extra = max(1, min(5, (len(estimate) + 15) // 22))
        return story_cols + extra

    @property
    def depth(self) -> int:
        parent = self.parent
        if not isinstance(parent, Epic):
            return 0
        if not isinstance(parent.parent, Epic):
            return 0
        return parent.depth + 1

    def tree_depth(self) -> int:
        if not self.epics:
            return self.depth
        return max(child.tree_depth() for child in self.epics)


class Story(StoryNode):
    _semantic_type_name = "Story"
    scenario_type = Scenario

    def __init__(
        self,
        name: "str | Story",
        sequential_order: int = 0,
        story_type: StoryType = StoryType.USER,
    ):
        source = name if isinstance(name, Story) else None
        super().__init__(
            source.name if source is not None else name,
            source.sequential_order if source is not None else sequential_order,
        )
        self.story_type = source.story_type if source is not None else story_type
        self.increment: Optional["Increment"] = None
        self.actors: List[str] = list(source.actors) if source is not None else []
        self.domain_terms: List[str] = list(source.domain_terms) if source is not None else []
        self.evidence: List[str] = list(source.evidence) if source is not None else []
        self.backgrounds: List["Background"] = []
        self.scenarios: List["Scenario"] = []
        if source is None:
            return
        for background in source.backgrounds:
            self.backgrounds.append(Background(background))
        for scenario in source.scenarios:
            self.scenarios.append(type(self).scenario_type(scenario))

    def clone(self) -> "Story":
        cloned = type(self)(self.name, self.sequential_order, self.story_type)
        cloned.increment = self.increment
        cloned.actors = list(self.actors)
        cloned.domain_terms = list(self.domain_terms)
        cloned.evidence = list(self.evidence)
        for background in self.backgrounds:
            cloned.backgrounds.append(background.clone())
        for scenario in self.scenarios:
            cloned.scenarios.append(scenario.clone())
        return cloned


class StoryMap(StoryNode):
    _semantic_type_name = "StoryMap"
    epic_type = Epic
    story_type = Story

    def __init__(self, source: Optional["StoryMap"] = None) -> None:
        super().__init__(name="StoryMap", sequential_order=0)
        self.epics: List[Epic] = []
        self.increments: List[Increment] = []
        self.examples = Examples(self)
        if source is None:
            return
        for epic in source.epics:
            self.append_epic(self.epic_type(epic, story_class=self.story_type))
        increment_type = getattr(type(self), "increment_type", Increment)
        for increment in source.increments:
            self.append_increment(increment_type(increment, story_class=self.story_type))

    @classmethod
    def load(cls, root) -> "StoryMap":
        """Read the story map, scenarios, and increments from a folder."""
        from pathlib import Path

        from practices.stories.model.json.nodes import JsonStoryMap
        from practices.stories.model.markdown.nodes import MarkdownStoryMap

        root = Path(root).resolve()
        story_map_root = root.parent if root.is_file() else root
        story_map = cls._story_map_at(story_map_root, JsonStoryMap, MarkdownStoryMap)
        if story_map.epics:
            return story_map
        for name in ("story_map.md", "story-map.md"):
            candidate = root / name
            if not candidate.is_file():
                continue
            parsed = MarkdownStoryMap.from_workspace(candidate)
            if parsed and parsed.epics:
                return parsed
        parsed = MarkdownStoryMap.from_workspace(root)
        if parsed and parsed.epics:
            return parsed
        return story_map

    @staticmethod
    def _story_map_at(story_map_root, json_story_map, markdown_story_map) -> "StoryMap":
        story_map_dir = story_map_root
        while story_map_dir and story_map_dir != story_map_dir.parent:
            candidate = story_map_dir / "story-map.md"
            if candidate.exists():
                loaded = markdown_story_map.from_workspace(candidate)
                if loaded:
                    return loaded
            story_map_dir = story_map_dir.parent
        return (
            json_story_map.from_workspace(story_map_root)
            or markdown_story_map.from_workspace(story_map_root)
            or StoryMap()
        )

    # -- Epic mutations -------------------------------------------------------

    def append_epic(self, epic: Epic) -> None:
        epic.parent = self
        self.epics.append(epic)
        self._renumber(self.epics)

    # -- Increment mutations --------------------------------------------------

    def append_increment(self, increment: Increment) -> None:
        increment.parent = self
        self.increments.append(increment)
        self._renumber(self.increments)

    def clone(self) -> "StoryMap":
        cloned = type(self)()
        for epic in self.epics:
            cloned.append_epic(epic.clone())
        for increment in self.increments:
            cloned.append_increment(increment.clone())
        cloned.examples = self.examples.clone(cloned)
        return cloned

    # -- helpers --------------------------------------------------------------

    def _renumber(self, nodes: List[StoryNode]) -> None:
        for i, node in enumerate(nodes, start=1):
            node.sequential_order = i


class StoryModelFactory:
    """Pick the channel story map from a file or a folder and return a StoryMap."""

    @staticmethod
    def load(path: str) -> StoryMap:
        from pathlib import Path

        target = Path(path)
        if target.is_file() and target.suffix == ".drawio":
            from practices.stories.model.drawio.nodes import DrawIOStoryMap

            return DrawIOStoryMap().load(target.read_text(encoding="utf-8"))
        return StoryMap.load(path)
