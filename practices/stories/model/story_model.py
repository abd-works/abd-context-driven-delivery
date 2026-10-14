"""Story map nodes: StoryNode, StoryModel, Epic, Story, Scenario, Step, Background, Example, Increment.

A nested epic is an epic whose parent is an epic. Each node type implements clone.
"""

from __future__ import annotations

import re
from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Dict, Iterable, List, Optional

from harness.graph.bound_node import BoundChildren as _BoundChildren
from harness.graph.bound_node import BoundNode
from harness.graph.graph import Graph

from .source_location import SourceLocation

# Pairs the schema names with belongsTo. The facade does not grow a method for them.
_BELONGS = {
    ("Epic", "Epic"),
    ("Story", "Epic"),
    ("Background", "Story"),
    ("Step", "Scenario"),
}


class StoryNode(BoundNode, ABC):
    """A story-model object and the graph node for that object.

    Subclasses declare `_semantic_type_name` so cross-format nodes
    (e.g. MarkdownEpic vs JsonEpic) share one semantic axis.
    Pass a graph the same way you pass another model. Omit it and this node
    keeps a graph of its own until a parent adopts it.
    """

    _graph_practice = "stories"
    _semantic_type_name: str = "StoryNode"
    _belongs = _BELONGS
    _edge_order = {
        "decomposedInto": 1,
        "background": 2,
        "scenarios": 3,
        "steps": 4,
        "examples": 5,
        "increments": 6,
        "stories": 7,
        "belongsTo": 8,
        "ands": 9,
    }

    _GENERIC_VERBS = frozenset({"handle", "process", "manage", "perform", "do", "execute", "run"})
    _ACTOR_NOUNS = frozenset({
        "customer", "user", "system", "admin", "operator", "treasurer", "approver",
        "auditor", "merchant", "partner", "service", "api", "backend", "frontend",
        "database", "browser", "client", "server",
    })
    _VERBS = frozenset({
        "add", "allow", "approve", "assign", "attach", "block", "build", "cancel",
        "capture", "check", "clear", "close", "collect", "compare", "complete",
        "compose", "confirm", "connect", "convert", "create", "delete", "deliver",
        "deny", "deploy", "detect", "disable", "display", "download", "draft",
        "drop", "edit", "email", "enable", "enter", "expire", "export", "extend",
        "extract", "fetch", "filter", "fix", "flag", "generate", "grant", "group",
        "hide", "hold", "import", "index", "initiate", "invite", "issue",
        "join", "leave", "list", "load", "lock", "log", "map", "match", "merge",
        "move", "notify", "onboard", "open", "order", "pause", "pay", "post",
        "print", "publish", "queue", "read", "record", "refresh",
        "refund", "register", "reject", "release", "remove", "rename", "render",
        "reply", "report", "reset", "resolve", "retry", "return", "revert",
        "review", "revoke", "route", "save", "scan", "schedule", "search",
        "select", "send", "settle", "share", "show", "sign", "split", "start",
        "stop", "store", "submit", "subscribe", "sync", "toggle", "track",
        "translate", "trigger", "unlock", "update", "upload", "validate", "verify",
        "view", "vote", "wait", "browse", "request", "place",
    })
    _GERUND = re.compile(r"^[a-z]+ing$")
    _NOMINALISATION = re.compile(r"^[a-z]+(?:tion|sion|ment|ance|ence|ity|ness)$")
    _GENERIC_HANDLER = re.compile(
        r"^(Handle|Process|Manage|Perform|Do|Execute|Run)\s+[A-Z]",
        re.IGNORECASE,
    )
    _KEBAB_FILE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*\.(md|ts|tsx|js|jsx)$")
    _CAMEL_FILE = re.compile(r"[A-Z][a-zA-Z0-9]*(?:Story|Test|Spec)")
    _ONE_OFF = re.compile(
        r"\b(once|one[- ]time|initial setup|bootstrap only|migrate legacy)\b",
        re.IGNORECASE,
    )

    def __init__(self, name: str, sequential_order: int, graph: Optional[Graph] = None):
        super().__init__(name, sequential_order, graph)
        # Shaping outline sizing (e.g. "approx 2-3 more stories (...)").
        # Meaningful on Epic; empty on Story and below.
        self.estimate: str = ""
        self.opening_token = ""
        self.opening_class = ""
        self.child_count = 0
        self.child_label = "children"
        self.child_band = ""
        self.near_duplicate = False
        self.generic_handler = False
        self.shared_verb = ""
        self.one_time_task = False
        self.artifact_name = ""
        self.camel_case_path = False
        self.evidence: List[str] = []

    def load_map_facts(self) -> None:
        """Fill the name, evidence, and child-count facts this node already owns."""
        self._load_opening()
        self._load_path_case()
        self.generic_handler = bool(self._GENERIC_HANDLER.match((self.name or "").strip()))
        self.near_duplicate = False
        self.shared_verb = ""
        self.one_time_task = bool(self._ONE_OFF.search(self.name or ""))
        self.load_child_band(0, "children")

    def _load_path_case(self) -> None:
        source = getattr(self, "source", None)
        relative = str(getattr(source, "file", "") or "") if source is not None else ""
        name = relative.replace("\\", "/").rsplit("/", 1)[-1]
        self.artifact_name = name
        self.camel_case_path = self._camel_case_file(name)

    def _camel_case_file(self, name: str) -> bool:
        if not name or name in {"."}:
            return False
        if self._KEBAB_FILE.match(name):
            return False
        stem = name.split(".")[0]
        return bool(self._CAMEL_FILE.search(name) or re.search(r"[A-Z]", stem))

    def _load_opening(self) -> None:
        stripped = (self.name or "").strip().strip("`").strip("*").strip()
        match = re.match(r"[A-Za-z][A-Za-z\-']*", stripped)
        self.opening_token = match.group(0).lower() if match else ""
        self.opening_class = self._classify_opening(self.opening_token)

    def _classify_opening(self, token: str) -> str:
        if not token:
            return "unknown-noun"
        if token in self._GENERIC_VERBS:
            return "generic-verb"
        if token in self._VERBS:
            return "verb"
        if token in self._ACTOR_NOUNS:
            return "actor-noun"
        if self._GERUND.match(token):
            return "gerund"
        if self._NOMINALISATION.match(token):
            return "nominalisation"
        return "unknown-noun"

    def load_child_band(self, count: int, label: str) -> None:
        self.child_count = count
        self.child_label = label
        if count == 0 or 4 <= count <= 9:
            self.child_band = ""
        elif count in (3, 10):
            self.child_band = "warning"
        else:
            self.child_band = "error"

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
        if isinstance(self.scope, StoryNode):
            self.scope._link(value, "examples")

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
        self.parent: Optional["StoryModel"] = None
        self.outcome: str = source.outcome if source is not None else ""
        self.slicing_notes: str = source.slicing_notes if source is not None else ""
        self.decision_prompt: str = source.decision_prompt if source is not None else ""
        self.source: Optional[SourceLocation] = source.source if source is not None else None
        self._stories = _BoundChildren(self, "stories")
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

    @property
    def stories(self) -> List["Story"]:
        return self._stories

    @stories.setter
    def stories(self, stories: List["Story"]) -> None:
        self._refill(self._stories, stories)

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
        self._ands = _BoundChildren(self, "ands")
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
        self._refill(self._ands, ands)

    @property
    def keyword(self) -> str:
        """Gherkin keyword on the line: Given, When, Then, And, or But."""
        if self._keyword:
            return self._keyword[0].upper() + self._keyword[1:].lower()
        value = getattr(self.step_type, "value", self.step_type)
        return str(value).capitalize()

    @property
    def is_continuation(self) -> bool:
        """An And or But line continues the clause before it."""
        if self._keyword:
            return self._keyword.casefold() in ("and", "but")
        return self.text.strip().startswith(("And ", "But "))

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
        self._steps = _BoundChildren(self, "steps")
        self.examples = source.examples.clone(self) if source is not None else Examples(self)
        if source is not None:
            for step in source.steps:
                self._steps.append(Step(step))

    @property
    def steps(self) -> List["Step"]:
        return sorted(self._steps, key=lambda step: step.sequential_order)

    @steps.setter
    def steps(self, steps: List["Step"]) -> None:
        self._refill(self._steps, steps)

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
        self._backgrounds = _BoundChildren(self, "background")
        self._steps = _BoundChildren(self, "steps")
        self.examples = source.examples.clone(self) if source is not None else Examples(self)
        self.is_outline: bool = source.is_outline if source is not None else False
        self.evidence: List[str] = list(source.evidence) if source is not None else []
        self.source: Optional[SourceLocation] = source.source if source is not None else None
        if source is not None:
            for background in source.backgrounds:
                self.backgrounds.append(Background(background))
            for step in source.steps:
                self.steps.append(Step(step))

    @property
    def backgrounds(self) -> List[Background]:
        return self._backgrounds

    @backgrounds.setter
    def backgrounds(self, backgrounds: List[Background]) -> None:
        self._refill(self._backgrounds, backgrounds)

    @property
    def steps(self) -> List[Step]:
        return self._steps

    @steps.setter
    def steps(self, steps: List[Step]) -> None:
        self._refill(self._steps, steps)

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

    def load_map_facts(self) -> None:
        self._load_opening()
        self._load_path_case()
        self.generic_handler = False
        self.near_duplicate = False
        self.shared_verb = ""
        self.one_time_task = False
        self.load_child_band(len(self.steps), "steps")

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
        self._epics = _BoundChildren(self, "decomposedInto")
        self._stories = _BoundChildren(self, "decomposedInto")
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
    def epics(self) -> List["Epic"]:
        return self._epics

    @epics.setter
    def epics(self, epics: List["Epic"]) -> None:
        self._refill(self._epics, epics)

    @property
    def stories(self) -> List["Story"]:
        return self._stories

    @stories.setter
    def stories(self, stories: List["Story"]) -> None:
        self._refill(self._stories, stories)

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

    def load_map_facts(self) -> None:
        self._load_opening()
        self._load_path_case()
        self.generic_handler = False
        self.near_duplicate = False
        self.one_time_task = False
        self.load_child_band(len(self.epics) + len(self.stories), "children")
        self.shared_verb = self._shared_opening()

    def _shared_opening(self) -> str:
        names = [story.name.strip().casefold() for story in self.stories if story.name.strip()]
        verbs = [name.split()[0] for name in names if name.split()]
        if len(verbs) < 2 or len(set(verbs)) != 1 or len(set(names)) < 2:
            return ""
        return verbs[0]

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
        self._backgrounds = _BoundChildren(self, "background")
        self._scenarios = _BoundChildren(self, "scenarios")
        if source is None:
            return
        for background in source.backgrounds:
            self.backgrounds.append(Background(background))
        for scenario in source.scenarios:
            self.scenarios.append(type(self).scenario_type(scenario))

    @property
    def backgrounds(self) -> List["Background"]:
        return self._backgrounds

    @backgrounds.setter
    def backgrounds(self, backgrounds: List["Background"]) -> None:
        self._refill(self._backgrounds, backgrounds)

    @property
    def scenarios(self) -> List["Scenario"]:
        return self._scenarios

    @scenarios.setter
    def scenarios(self, scenarios: List["Scenario"]) -> None:
        self._refill(self._scenarios, scenarios)

    def load_map_facts(self) -> None:
        self._load_opening()
        self._load_path_case()
        self.generic_handler = bool(self._GENERIC_HANDLER.match((self.name or "").strip()))
        self.one_time_task = bool(self._ONE_OFF.search(self.name or ""))
        self.shared_verb = ""
        backgrounds = len(self.backgrounds)
        total = len(self.scenarios) + backgrounds
        label = "scenarios" if backgrounds == 0 else "children"
        self.load_child_band(total, label)
        self.near_duplicate = self._repeats_later_sibling()

    def _repeats_later_sibling(self) -> bool:
        siblings = list(getattr(self.parent, "stories", []) or [])
        if len(siblings) < 2 or self not in siblings:
            return False
        names = [story.name.strip().lower() for story in siblings]
        index = siblings.index(self)
        left = names[index]
        return any(self._near_name(left, right) for right in names[index + 1 :])

    def _near_name(self, left: str, right: str) -> bool:
        if left == right:
            return True
        if left.split()[:1] != right.split()[:1]:
            return False
        if abs(len(left) - len(right)) > 2:
            return False
        shorter, longer = (left, right) if len(left) <= len(right) else (right, left)
        return longer.startswith(shorter[: max(3, len(shorter) - 1)])

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


class StoryModel(StoryNode):
    _semantic_type_name = "StoryModel"
    epic_type = Epic
    story_type = Story

    def __init__(self, source: Optional["StoryModel | Graph"] = None, graph: Optional[Graph] = None) -> None:
        if isinstance(source, Graph):
            graph = source
            source = None
        super().__init__(name="StoryModel", sequential_order=0, graph=graph)
        self._epics = _BoundChildren(self, "decomposedInto")
        self._increments = _BoundChildren(self, "increments")
        self.examples = Examples(self)
        if isinstance(source, StoryModel):
            self._copy_map(source)
            return
        if graph is not None:
            self._copy_map_on_graph()

    @property
    def epics(self) -> List[Epic]:
        return self._epics

    @epics.setter
    def epics(self, epics: List[Epic]) -> None:
        self._refill(self._epics, epics)

    @property
    def increments(self) -> List[Increment]:
        return self._increments

    @increments.setter
    def increments(self, increments: List[Increment]) -> None:
        self._refill(self._increments, increments)

    def _copy_map(self, source: "StoryModel") -> None:
        for epic in source.epics:
            self.append_epic(self.epic_type(epic, story_class=self.story_type))
        increment_type = getattr(type(self), "increment_type", Increment)
        for increment in source.increments:
            self.append_increment(increment_type(increment, story_class=self.story_type))

    def _copy_map_on_graph(self) -> None:
        maps = [
            node
            for node in self.practice.nodes.get("StoryModel", [])
            if node is not self and isinstance(node, StoryModel) and node.epics
        ]
        if maps:
            self._copy_map(maps[0])

    @classmethod
    def load(cls, root) -> "StoryModel":
        """Read the story map, scenarios, and increments from a folder."""
        from pathlib import Path

        from practices.stories.model.json.nodes import JsonStoryModel
        from practices.stories.model.markdown.nodes import MarkdownStoryModel

        root = Path(root).resolve()
        story_map_root = root.parent if root.is_file() else root
        story_map = cls._story_map_at(story_map_root, JsonStoryModel, MarkdownStoryModel)
        if story_map.epics:
            return story_map
        for name in ("story_map.md", "story-map.md"):
            candidate = root / name
            if not candidate.is_file():
                continue
            parsed = MarkdownStoryModel.from_workspace(candidate)
            if parsed and parsed.epics:
                return parsed
        parsed = MarkdownStoryModel.from_workspace(root)
        if parsed and parsed.epics:
            return parsed
        return story_map

    @staticmethod
    def _story_map_at(story_map_root, json_story_map, markdown_story_map) -> "StoryModel":
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
            or StoryModel()
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

    def clone(self) -> "StoryModel":
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
    """Pick the channel story map from a file or a folder and return a StoryModel."""

    @staticmethod
    def load(path: str) -> StoryModel:
        from pathlib import Path

        target = Path(path)
        if target.is_file() and target.suffix == ".drawio":
            from practices.stories.model.drawio.nodes import DrawIOStoryModel

            return DrawIOStoryModel().load(target.read_text(encoding="utf-8"))
        return StoryModel.load(path)
