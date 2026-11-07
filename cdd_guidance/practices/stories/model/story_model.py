"""Story map nodes: StoryNode, StoryModel, Epic, Story, Scenario, Step, Background, Example, Increment.

A nested epic is an epic whose parent is an epic. Each node type implements clone.
"""

from __future__ import annotations

import re
from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Dict, Iterable, List, Optional

from harness.graph.model_node import ModelChildren
from harness.graph.model_node import ModelNode
from harness.graph.graph import Graph
from harness.name.name import Name

from cdd_guidance.practices.clean_engineering.model.call_graph import CallGraphEntry
from cdd_guidance.practices.clean_engineering.model.code_body import CodeBody, WrittenBlock

from .source_location import SourceLocation, path_from

# Pairs the schema names with belongsTo. The facade does not grow a method for them.
_BELONGS = {
    ("Epic", "Epic"),
    ("Story", "Epic"),
    ("Background", "Story"),
    ("Step", "Scenario"),
}


class StoryNode(ModelNode, ABC):
    """A story-model object and the graph node for that object.

    Subclasses declare `_semantic_type_name` so cross-format nodes
    (e.g. MarkdownEpic vs JsonEpic) share one semantic axis.
    Pass a graph the same way you pass another model. Omit it and this node
    keeps a graph of its own until a parent adopts it.
    """

    _practice_key = "stories"
    _semantic_type_name: str = "StoryNode"
    graph_facts = (
        "opening_token",
        "opening_class",
        "child_count",
        "child_label",
        "child_band",
        "near_duplicate",
        "generic_handler",
        "shared_verb",
        "one_time_task",
        "artifact_name",
        "camel_case_path",
        "evidence",
        "scenario_count",
    )
    _belongs = _BELONGS

    _GENERIC_VERBS = frozenset({"handle", "process", "manage", "perform", "do", "execute", "run"})
    _ACTOR_NOUNS = frozenset({
        "customer", "user", "system", "admin", "operator", "treasurer", "approver",
        "auditor", "merchant", "partner", "service", "api", "backend", "frontend",
        "database", "browser", "client", "server",
    })
    _VERBS = frozenset({
        "access", "activate", "add", "allow", "apply", "approve", "assign",
        "attach", "authenticate", "authorize", "block", "browse", "build", "cancel",
        "capture", "change", "check", "choose", "clear", "close", "collect",
        "compare", "complete", "compose", "confirm", "connect", "convert", "create",
        "delete", "deliver", "deny", "deploy", "detect", "determine", "disable",
        "display", "download", "draft", "drop", "edit", "email", "enable", "enter",
        "expire", "export", "extend", "extract", "fetch", "filter", "fix", "flag",
        "generate", "get", "grant", "group", "hide", "hold", "import", "index",
        "initiate", "invite", "issue", "join", "know", "leave", "list", "load", "lock",
        "log", "map", "match", "merge", "move", "notify", "onboard", "open",
        "order", "pause", "pay", "pick", "place", "post", "print", "provide",
        "publish", "purchase", "query", "queue", "read", "record", "redeem", "refresh",
        "refund", "register", "reject", "release", "remove", "rename", "render",
        "reply", "report", "request", "reset", "resolve", "retry", "return",
        "revert", "review", "revoke", "route", "save", "scan", "schedule", "search",
        "select", "send", "serve", "set", "settle", "share", "show", "sign",
        "split", "start", "stop", "store", "submit", "subscribe", "sync", "toggle",
        "track", "translate", "trigger", "unlock", "update", "upload", "use",
        "validate", "verify", "view", "vote", "wait",
    })
    _GERUND = re.compile(r"^[a-z]+ing$")
    _NOMINALISATION = re.compile(r"^[a-z]+(?:tion|sion|ment|ance|ence|ity|ness)$")
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
        self.written: Optional[WrittenBlock] = None
        self.setup = CodeBody()

    def load_map_facts(self) -> None:
        """Fill the name, evidence, and child-count facts this node already owns."""
        self._load_opening()
        self._load_path_case()
        self.generic_handler = self._names_generic_handler()
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
        # One word ("CartStuff") has no object to follow a verb, whatever the word is.
        single_word = bool(stripped) and len(stripped.split()) == 1
        self.opening_class = "single-word" if single_word else self._classify_opening(self.opening_token)

    def opens_with_verb(self) -> bool:
        """The name's first word is a verb the story map knows, generic or not."""
        words = (self.name or "").split()
        token = words[0].lower() if words else ""
        return token in self._VERBS or token in self._GENERIC_VERBS

    def _names_generic_handler(self) -> bool:
        """A generic verb such as Handle or Process followed by its object: the name hides what happens."""
        words = (self.name or "").split()
        return len(words) > 1 and words[0].lower() in self._GENERIC_VERBS and words[1][:1].isalpha()

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
        # A word the verb list lacks is not evidence of a noun ("Carry Plan ..."); only the classes above are flagged.
        return "unlisted"

    def load_child_band(self, count: int, label: str) -> None:
        self.child_count = count
        self.child_label = label
        self.child_band = "" if count == 0 or 4 <= count <= 9 else "error"

    def take_code_from(self, source: "StoryNode") -> None:
        """Keep the code the source was read with, so a copy in another channel can still write it back."""
        self.written = getattr(source, "written", None)
        self.setup = getattr(source, "setup", CodeBody())
        if hasattr(self, "body"):
            self.body = getattr(source, "body", CodeBody())

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
        self._stories = ModelChildren(self, "stories")
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
    graph_facts = ("keyword", "text", "phase", "concepts", "values", "actor", "continuation", "callees")

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
        self._ands = ModelChildren(self, "ands")
        self.concepts: List[str] = list(concepts) if concepts is not None else []
        self.values: List[str] = list(values) if values is not None else []
        self.actor = actor
        self.source = source
        self.call_graph: List[CallGraphEntry] = (
            list(origin.call_graph) if origin is not None and getattr(origin, "call_graph", None) else []
        )
        self.body = CodeBody()
        if origin is not None:
            self.take_code_from(origin)
            for extra in origin.ands:
                self._ands.append(type(self)(extra))

    @property
    def code_key(self) -> tuple:
        """What this step says in code: while it still says it, the lines it was read with stand."""
        return (self.keyword, self.text, self.body.text)

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

    @property
    def continuation(self) -> bool:
        """The fact name rules read for ``is_continuation``."""
        return self.is_continuation

    @property
    def phase(self) -> str:
        """given, when, or then from the step type; empty when the step has none."""
        return self.step_type.value if self.step_type is not None else ""

    @property
    def callees(self) -> List[str]:
        """The capitalized concepts the step names: the domain classes it reaches."""
        found: List[str] = []
        for concept in self.concepts or []:
            token = concept.strip()
            if token and token[0].isupper() and token not in found:
                found.append(token)
        return found

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
        cloned.call_graph = list(self.call_graph)
        cloned.take_code_from(self)
        return cloned


def _steps_key(steps: List["Step"]) -> tuple:
    return tuple(line.code_key for step in steps for line in (step, *step.ands))


class Background(StoryNode):
    _semantic_type_name = "Background"

    def __init__(self, name: "str | Background" = "background", sequential_order: int = 1) -> None:
        source = name if isinstance(name, Background) else None
        super().__init__(
            name=source.name if source is not None else name,
            sequential_order=source.sequential_order if source is not None else sequential_order,
        )
        self._steps = ModelChildren(self, "steps")
        self.examples = source.examples.clone(self) if source is not None else Examples(self)
        if source is not None:
            self.take_code_from(source)
            for step in source.steps:
                self._steps.append(Step(step))

    @property
    def steps(self) -> List["Step"]:
        return sorted(self._steps, key=lambda step: step.sequential_order)

    @steps.setter
    def steps(self, steps: List["Step"]) -> None:
        self._refill(self._steps, steps)

    @property
    def code_key(self) -> tuple:
        return (self.name, _steps_key(self.steps))

    def clone(self) -> "Background":
        cloned = type(self)(self.name, self.sequential_order)
        cloned.steps = [step.clone() for step in self.steps]
        cloned.examples = self.examples.clone(cloned)
        cloned.take_code_from(self)
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
        self._backgrounds = ModelChildren(self, "background")
        self._steps = ModelChildren(self, "steps")
        self.examples = source.examples.clone(self) if source is not None else Examples(self)
        self.is_outline: bool = source.is_outline if source is not None else False
        self.evidence: List[str] = list(source.evidence) if source is not None else []
        self.source: Optional[SourceLocation] = source.source if source is not None else None
        if source is not None:
            self.take_code_from(source)
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
        self.child_count = len(self.steps)
        self.child_label = "steps"
        self.child_band = ""

    @property
    def code_key(self) -> tuple:
        """What this scenario says in code: its name, examples, backgrounds, and every step with its body."""
        backgrounds = tuple(background.code_key for background in self.backgrounds)
        return (self.name, tuple(self.examples), backgrounds, _steps_key(self.steps))

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
        cloned.take_code_from(self)
        return cloned


class StoryType(str, Enum):
    """What kind of story it is. The outline notations (story-map.md, the sketch) mark a story ``(S)`` and add the
    kind only when it is not a user story, ``(S:system)`` or ``(S:technical)``, so a map of user stories reads as it
    always has and the kind survives every format."""

    USER = "user"
    SYSTEM = "system"
    TECHNICAL = "technical"

    @property
    def outline_mark(self) -> str:
        return "(S)" if self is StoryType.USER else f"(S:{self.value})"

    @classmethod
    def from_mark(cls, kind: Optional[str]) -> "StoryType":
        """The kind an outline mark names; no kind is a user story."""
        return cls((kind or cls.USER.value).strip().lower())


class Epic(StoryNode):
    """An epic. A nested epic is an epic whose parent is an epic."""

    _semantic_type_name = "Epic"

    def __init__(self, name: "str | Epic", sequential_order: int = 0, *, story_class: Optional[type] = None):
        source = name if isinstance(name, Epic) else None
        super().__init__(
            source.name if source is not None else name,
            source.sequential_order if source is not None else sequential_order,
        )
        self._epics = ModelChildren(self, "decomposedInto")
        self._stories = ModelChildren(self, "decomposedInto")
        self.examples = source.examples.clone(self) if source is not None else Examples(self)
        if source is None:
            return
        self.estimate = source.estimate or ""
        self.take_code_from(source)
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
        cloned.take_code_from(self)
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

    def every_epic(self) -> List["Epic"]:
        """This epic and every epic nested under it, each before its own children."""
        return [self, *(found for child in self.epics for found in child.every_epic())]

    def every_story(self) -> List["Story"]:
        """Every Story this epic and its nested epics hold, in map order."""
        return [story for epic in self.every_epic() for story in epic.stories]

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

    def place_in(self, file: str) -> None:
        """Name *file* on this epic and everything under it that names no file yet; the line stays unknown."""
        if not self.has_source_file:
            self.source = SourceLocation(file)
        for child in self.epics:
            child.place_in(file)
        for story in self.stories:
            if not story.has_source_file:
                story.source = SourceLocation(file)

    def _stamp_epic(self, name: str, loc) -> bool:
        for child in self.epics:
            if child.name == name and not child.has_source_file:
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
            if story.name == name and not story.has_source_file:
                story.source = loc
                return True
        return False

    def _has_estimate(self) -> bool:
        if (self.estimate or "").strip():
            return True
        return any(child._has_estimate() for child in self.epics)

    def span_columns(self) -> int:
        """Story-grid columns a top-level epic occupies: its own stories, then each nested epic. An empty epic is one
        column."""
        nested = sum(max(child.diagram_span_columns(), 1) for child in self.epics)
        return max(len(self.stories) + nested, 1)

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
        self._backgrounds = ModelChildren(self, "background")
        self._scenarios = ModelChildren(self, "scenarios")
        if source is None:
            return
        self.take_code_from(source)
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
        self.generic_handler = self._names_generic_handler()
        self.one_time_task = bool(self._ONE_OFF.search(self.name or ""))
        self.shared_verb = ""
        self.scenario_count = len(self.scenarios)
        self.child_count = self.scenario_count
        self.child_label = "scenarios"
        self.child_band = ""
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

    @property
    def code_key(self) -> tuple:
        """What this story says in code apart from its scenarios, which keep their own keys."""
        backgrounds = tuple(background.code_key for background in self.backgrounds)
        return (self.name, tuple(self.actors), tuple(self.evidence), backgrounds)

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
        cloned.take_code_from(self)
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
        self._epics = ModelChildren(self, "decomposedInto")
        self._increments = ModelChildren(self, "increments")
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
        self.examples = source.examples.clone(self)
        for epic in source.epics:
            self.append_epic(self.epic_type(epic, story_class=self.story_type))
        increment_type = getattr(type(self), "increment_type", Increment)
        for increment in source.increments:
            self.append_increment(increment_type(increment, story_class=self.story_type))

    def _copy_map_on_graph(self) -> None:
        maps = [
            node
            for node in self.graph.nodes_of(self.practice, "StoryModel")
            if node is not self and isinstance(node, StoryModel) and node.epics
        ]
        if maps:
            self._copy_map(maps[0])

    @classmethod
    def load(cls, root, *, on_file=None) -> "StoryModel":
        """Read the story map, scenarios, and increments from a folder."""
        from pathlib import Path

        from cdd_guidance.practices.stories.model.json.nodes import JsonStoryModel
        from cdd_guidance.practices.stories.model.markdown.nodes import MarkdownStoryModel

        root = Path(root).resolve()
        story_map_root = root.parent if root.is_file() else root
        story_map = cls._story_map_at(story_map_root, JsonStoryModel, MarkdownStoryModel, on_file)
        if story_map.epics:
            return story_map
        for name in ("story_map.md", "story-map.md"):
            candidate = root / name
            if not candidate.is_file():
                continue
            parsed = MarkdownStoryModel.from_workspace(candidate, on_file=on_file)
            if parsed and parsed.epics:
                return parsed
        parsed = MarkdownStoryModel.from_workspace(root, on_file=on_file)
        if parsed and parsed.epics:
            return parsed
        return story_map

    @classmethod
    def load_files(cls, files, project, *, on_file=None) -> "StoryModel":
        """Read the story maps and story tests among *files*; each node names its file as a path from *project*.

        A story test holds one Story's scenarios in its own language, and the story map says which epic that Story
        sits under. So a story test's scenarios go on the map's Story of the same name, and a story test with no map
        listed reads the map in its own folder."""
        from pathlib import Path

        project = Path(project).resolve()
        paths = [Path(item).resolve() for item in files]
        tests = [path for path in paths if story_test_type(path) is not None]
        maps = [path for path in paths if is_story_map_file(path)]
        maps += [found for found in cls._maps_beside(tests) if found not in maps]
        merged = cls()
        for path in maps:
            for epic in list(cls._story_map_file(path, project, on_file).epics):
                merged.append_epic(epic)
        for path in tests:
            merged._take_scenarios_from(path, project, on_file)
        return merged

    @classmethod
    def _maps_beside(cls, tests) -> list:
        """The story map each story test belongs to: in its own folder, or the nearest folder above it, since story
        tests sit in epic folders below their map."""
        return list(dict.fromkeys(found for path in tests for found in [cls._nearest_map(path.parent)] if found))

    @staticmethod
    def _nearest_map(folder):
        """The story map in *folder* or the nearest folder above it, or in that folder's ``.context``, where documents
        go while code sits straight in the folder: its markdown when it has one, since a drawio of the same map would
        add every Story twice."""
        for candidate in (folder, *folder.parents):
            context = candidate / ".context"
            beside = list(context.iterdir()) if context.is_dir() else []
            maps = sorted(path.resolve() for path in [*candidate.iterdir(), *beside] if is_story_map_file(path))
            if maps:
                markdown = [path for path in maps if path.suffix.lower() == ".md"]
                return (markdown or maps)[0]
        return None

    def _take_scenarios_from(self, path, project, on_file=None) -> None:
        """Give the scenarios of each Story in the story test at *path* to every Story of the same name in this model,
        each keeping the story test as its source. The markdown and the drawio of one story map each hold that Story,
        so both take its scenarios. A Story the map does not have adds nothing."""
        file = path_from(project, path)
        if on_file is not None:
            on_file(file)
        for read in story_test_type(path).load_all(path.read_text(encoding="utf-8")):
            for scenario in read.scenarios:
                scenario.source = SourceLocation(file)
            for story in self.every_story():
                if story.name == read.name:
                    story.backgrounds = list(read.backgrounds)
                    story.scenarios = list(read.scenarios)

    def every_epic(self) -> List[Epic]:
        """Every epic and nested epic, each before its own children."""
        return [found for epic in self.epics for found in epic.every_epic()]

    def every_story(self) -> List["Story"]:
        """Every Story under every epic and sub-epic, in map order."""
        return [story for epic in self.every_epic() for story in epic.stories]

    @classmethod
    def _story_map_file(cls, path, project, on_file=None) -> "StoryModel":
        from cdd_guidance.practices.stories.model.drawio.nodes import DrawIOStoryModel
        from cdd_guidance.practices.stories.model.markdown.nodes import MarkdownStoryModel

        if path.suffix.lower() == ".md":
            return MarkdownStoryModel.from_workspace(path, on_file=on_file, project=project) or cls()
        file = path_from(project, path)
        if on_file is not None:
            on_file(file)
        loaded = DrawIOStoryModel().load(path.read_text(encoding="utf-8"))
        for epic in loaded.epics:
            epic.place_in(file)
        return loaded

    @staticmethod
    def _story_map_at(story_map_root, json_story_map, markdown_story_map, on_file=None) -> "StoryModel":
        story_map_dir = story_map_root
        while story_map_dir and story_map_dir != story_map_dir.parent:
            candidate = story_map_dir / "story-map.md"
            if candidate.exists():
                loaded = markdown_story_map.from_workspace(candidate, on_file=on_file)
                if loaded:
                    return loaded
            story_map_dir = story_map_dir.parent
        return (
            json_story_map.from_workspace(story_map_root)
            or markdown_story_map.from_workspace(story_map_root, on_file=on_file)
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


STORY_MAP_SUFFIXES = (".md", ".drawio")


def story_test_type(path):
    """The Story type that reads a story test in its own language, by the file's ending; none for any other file."""
    from pathlib import Path

    name = Path(path).name
    if name.endswith("_story.test.py"):
        from cdd_guidance.practices.stories.model.python.nodes import PythonStory

        return PythonStory
    if name.endswith("_story.test.ts"):
        from cdd_guidance.practices.stories.model.typescript.nodes import TypeScriptStory

        return TypeScriptStory
    if name.endswith("_story.test.js"):
        from cdd_guidance.practices.stories.model.javascript.nodes import JavaScriptStory

        return JavaScriptStory
    return None


def is_story_map_file(path) -> bool:
    """A story map is a markdown or drawio file named story-map (or story_map), alone or after a prefix."""
    from pathlib import Path

    path = Path(path)
    stem = Name(path.stem).title_slug
    return path.suffix.lower() in STORY_MAP_SUFFIXES and (stem == "story-map" or stem.endswith("-story-map"))
