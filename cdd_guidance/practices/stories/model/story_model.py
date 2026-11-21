"""Story map nodes: StoryNode, StoryModel, Epic, Story, Scenario, Step, Background, Example, Increment.

A nested epic is an epic whose parent is an epic. Each node type implements clone.
"""

from __future__ import annotations

import os
import zlib
from abc import ABC, abstractmethod
from enum import Enum
from typing import TYPE_CHECKING, Annotated, Any, Callable, Dict, List, Optional

from harness.agent_tools import agent_tool, agent_toolset
from harness.agent_tools.agent_tools import tool_subject
from harness.agent_tools.tool_call import ToolCall
from harness.annotations.annotation import hosted_only
from harness.graph.model_node import ModelChildren, ModelReferences
from harness.graph.model_node import ModelNode
from harness.graph.graph import Graph
from harness.annotations.name import Name
from harness.installation.data_class import SourceFile, data_field, identity, language_adapter
from harness.mcp.mcp_annotations import mcp

from cdd_guidance.practices.source_code import CallGraph
from cdd_guidance.practices.source_code import CodeBody, WrittenBlock

from . import name_facts
from .opened_story_map import OpenedStoryMap, StoryMapEditRefused, UnopenedStoryMap
from .story_copies import StoryCopies
from .story_map_files import source_at
from .story_recording import StoryRecording, StorySources, file_of

if TYPE_CHECKING:
    from pathlib import Path

    from harness.graph.graph import Node, Source

    from .story_file import CodeBlock
    from harness.guidance.guidance import PracticeGuidance

    from space.session.practice_session_output import FidelitySessionOutput

# A step goes by its text, cut to this many characters, so a long step still reads as one name.
_STEP_NAME_LENGTH = 80
# A step's graph id ends in a 24-bit checksum of its name: short enough to read in an id, long enough that two steps
# on one line of one file do not share it.
_STEP_CHECKSUM_MASK = 0xFFFFFF
# A leaf epic with an estimate widens by a column for about this many characters of the estimate: wider for an epic
# that has stories beside it, as its estimate shares their columns.
_ESTIMATE_CHARACTERS_PER_COLUMN = 18
_ESTIMATE_CHARACTERS_PER_EXTRA_COLUMN = 22
_ESTIMATE_LEAD_CHARACTERS = 12
_ESTIMATE_EXTRA_LEAD_CHARACTERS = 15
_EMPTY_EPIC_COLUMNS = (2, 8)
_EXTRA_EPIC_COLUMNS = (1, 5)

# What an example stands for: a field map, a class, an object whose fields are its cells, or its own name.
ExampleValue = Any

# Pairs the schema names with belongsTo. The facade does not grow a method for them.
_BELONGS = {
    ("Epic", "Epic"),
    ("Story", "Epic"),
    ("Background", "Story"),
    ("Step", "Scenario"),
}


class StoryNodeNotFound(LookupError):
    """A tool call named a node its story map does not hold, or a node of another kind than the tool acts on."""

    def __init__(self, node: str, kind: type) -> None:
        super().__init__(f"no {kind.__name__} {node!r} on its story map")
        self.node = node
        self.kind = kind


@hosted_only
@identity("node")
class StoryNode(ModelNode, ABC):
    """A story-model object and the graph node for that object.

    Subclasses declare `_semantic_type_name` so cross-format nodes
    (e.g. MarkdownEpic vs JsonEpic) share one semantic axis.
    Pass a graph the same way you pass another model. Omit it and this node
    keeps a graph of its own until a parent adopts it.
    """

    _semantic_type_name: str = "StoryNode"
    graph_facts = (
        "opening_token",
        "opening_class",
        "child_count",
        "child_label",
        "child_band",
        "child_target",
        "near_duplicate",
        "generic_handler",
        "shared_verb",
        "artifact_name",
        "camel_case_path",
        "evidence",
        "scenario_count",
    )
    _belongs = _BELONGS

    @property
    def slug(self) -> str:
        """The node's name as a cell id or a folder spells it, `place-order`; `node` for a node whose name has no
        letters."""
        return Name(self.name).title_slug or "node"

    def __init__(self, name: str, sequential_order: int, graph: Optional[Graph] = None):
        super().__init__(name, sequential_order, graph)
        # Shaping outline sizing (e.g. "approx 2-3 more stories (...)").
        # Meaningful on Epic; empty on Story and below.
        self.estimate: str = ""
        # What the story map says about this node in prose: the paragraphs under its heading in a story map. A save
        # writes it back unchanged.
        self.description_text: str = ""
        self.evidence: List[str] = []
        self.written: Optional[WrittenBlock] = None
        # The story file a story was read with, in code: its path and its own code around its stories, which the
        # stories read from one file share.
        self.file_written: Optional[WrittenBlock] = None
        self.setup = CodeBody()
        self._start_map_facts()

    def _start_map_facts(self) -> None:
        """The name and child-count facts a node holds before its map loads them (``load_map_facts``)."""
        self.opening_token = ""
        self.opening_class = ""
        self.child_count = 0
        self.child_label = "children"
        self.child_band = ""
        self.child_target = ""
        self.near_duplicate = False
        self.generic_handler = False
        self.shared_verb = ""
        self.artifact_name = ""
        self.camel_case_path = False

    def load_map_facts(self) -> None:
        """Fill the name, evidence, and child-count facts this node already owns."""
        self._load_opening()
        self._load_path_case()
        self.generic_handler = name_facts.names_generic_handler(self.name)
        self.near_duplicate = False
        self.shared_verb = ""
        self._load_child_band(0, "children")

    def _load_opening(self) -> None:
        self.opening_token, self.opening_class = name_facts.opening_of(self.name)

    def _load_path_case(self) -> None:
        self.artifact_name, self.camel_case_path = name_facts.file_name_facts(getattr(self, "source", None))

    def _load_child_band(self, count: int, label: str, fewest: int = 4, most: int = 9) -> None:
        """Record how many children the node holds and whether that count is outside fewest..most; a node with no
        children yet passes, since its children are simply not written."""
        self.child_count = count
        self.child_label = label
        self.child_target = f"{fewest}-{most}"
        self.child_band = "" if count == 0 or fewest <= count <= most else "error"

    def take_code_from(self, source: "StoryNode") -> None:
        """Keep the code the source was read with, so a copy in another channel can still write it back."""
        self.written = getattr(source, "written", None)
        self.file_written = getattr(source, "file_written", None)
        self.setup = getattr(source, "setup", CodeBody())
        if hasattr(self, "body"):
            self.body = getattr(source, "body", CodeBody())

    @property
    def recorded_name(self) -> str:
        """The name this object's graph node is called by."""
        return self.name

    # The node type this object's graph node takes: its semantic type, unless a kind of node records itself as another
    # (a step as Given, When or Then; an epic under another as SubEpic).
    recorded_type = property(ModelNode.semantic_type)

    @abstractmethod
    def clone(self) -> "StoryNode":
        """Return a new copy of this node, including its children."""

    # -- edits a person or an agent makes through the story map's tools ---------------------------------------------
    # Every edit saves through its story map before it answers, and answers the story map, so the page shows the map as
    # its files now hold it. A tool names a node `{file}#{path}`: the file its map was opened from, and the slugs from
    # its top epic down (`checkout.pay.pay-by-card`), a step by its place under its scenario (`step-2`).

    @classmethod
    @tool_subject
    def load(cls, node: str, *, call: ToolCall) -> "StoryNode":
        """The node the call names, `{file}#{path}`, on the story map read from that file now."""
        file, _, path = node.partition("#")
        found = StoryModel.load(file, call=call).descendants.node_at(path)
        if not isinstance(found, cls):
            raise StoryNodeNotFound(node, cls)
        return found

    @property
    def story_map(self) -> "StoryModel":
        """The story map at the top of its parent chain."""
        parent = getattr(self, "parent", None)
        return parent.story_map if parent is not None else self

    @property
    def parts(self) -> List["StoryNode"]:
        """The nodes a path goes through below this one; none for a node that holds no named parts."""
        return []

    def holding(self, part: "StoryNode") -> List["StoryNode"]:
        """The list of its own that holds part, which an edit inserts into and takes from."""
        raise StoryMapEditRefused(part, "move", f"{self.name} holds no {type(part).__name__}")

    segment_prefix = ""

    @property
    def segment(self) -> str:
        """Its step on a path: its slug, after the prefix its kind of node goes by."""
        return f"{self.segment_prefix}{self.slug}"

    @property
    def path(self) -> str:
        """The segments from its top epic down to it, joined by dots; empty for the story map itself."""
        parent = getattr(self, "parent", None)
        if parent is None:
            return ""
        return f"{parent.path}.{self.segment}" if parent.path else self.segment

    @property
    @data_field(key="node")
    def address(self) -> str:
        """`{file}#{path}`: what a tool call names this node by, sent as its `node`."""
        return f"{self.story_map.file}#{self.path}"

    @property
    @data_field(key="name")
    def shown_name(self) -> str:
        return self.name

    @property
    @data_field(key="description")
    def written_description(self) -> str:
        return self.description_text

    @mcp
    @agent_tool
    def rename(self, name: str) -> "StoryModel":
        """Rename this node of its story map, save the map, and return it."""
        self.name = name
        return self.story_map.opened.save()

    @mcp
    @agent_tool
    def edit_description(self, description: str) -> "StoryModel":
        """Change what the story map says about this node under its heading, save the map, and return it."""
        self.description_text = description.strip()
        return self.story_map.opened.save()

    @mcp
    @agent_tool
    def move_before(self, other: "StoryNode") -> "StoryModel":
        """Move this node to just before other, a node of its own kind on the same story map, under other's parent; save
        the map and return it. A node of another kind is refused with StoryMapEditRefused."""
        target = self.story_map.descendants.node_at(other.path)
        if target.semantic_type() != self.semantic_type():
            raise StoryMapEditRefused(self, "move_before", f"{target.name} is a {target.semantic_type()}, not a {self.semantic_type()}")
        self._leave()
        siblings = target.parent.holding(target)
        siblings.insert(siblings.index(target), self)
        _renumber(siblings)
        return self.story_map.opened.save()

    @mcp
    @agent_tool
    def remove(self) -> "StoryModel":
        """Take this node, and everything under it, off its story map; save the map and return it."""
        story_map = self.story_map
        self._leave()
        return story_map.opened.save()

    def _leave(self) -> None:
        parent = getattr(self, "parent", None)
        if parent is None:
            raise StoryMapEditRefused(self, "move", "the story map itself sits under nothing")
        siblings = parent.holding(self)
        siblings.pop(siblings.index(self))
        _renumber(siblings)


@language_adapter(language="typescript")
@agent_toolset
class Example(StoryNode):
    """One named example. `value` is any object and defaults to a field map.

    `scope` is the story node that shares this example: a background, a scenario,
    a sub-epic, an epic, or the story map.
    """

    _semantic_type_name = "Example"
    # An example goes by its slug after `example:`, so it never shares a path with a step of its scenario.
    segment_prefix = "example:"
    # The columns an example's row may name it by, in the order a table is read for its name.
    naming_columns = ("example", "name", "scenario")

    def __init__(self, name: str, example_value: ExampleValue = None) -> None:
        super().__init__(name=name, sequential_order=0)
        self.value = {} if example_value is None else example_value
        self.scope: Optional["StoryNode"] = None

    def record(self, recording: StoryRecording, scenario: "Node", lines: "Source") -> None:
        """Add this example to the graph under scenario, the node of the scenario that uses it, at that scenario's
        lines; an example two scenarios of one file share is one node. Its graph parent is the scenario that uses it,
        not its scope, so the scenario is handed in."""
        node = recording.add(self, f"stories:Example:{lines.file}:{self.name}", lines)
        for fact, held in self.recorded_facts(recording, lines.file).items():
            node.set_fact(fact, held)
        recording.graph.edges.link("examples", scenario, node)

    def recorded_facts(self, recording: StoryRecording, file: str) -> dict:
        """The facts this example records with: those the story file at file gives the example of its name."""
        return recording.example_facts(file, self.name)

    @property
    def declaration(self) -> Optional[tuple]:
        """Where this example is defined apart from the story file that uses it, as (file, first line, last line); none
        for an example its story file writes or whose definition is found by name (``align_to_example_export``)."""
        return None

    def clone(self) -> "Example":
        cloned = type(self)(self.name, dict(self.value) if isinstance(self.value, dict) else self.value)
        cloned.sequential_order, cloned.scope = self.sequential_order, self.scope
        return cloned

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

    @property
    @data_field(key="fields")
    def row(self) -> Dict[str, str]:
        """Its row of its table: its name under `example`, then its fields, each as text."""
        cells: Dict[str, Any] = {"example": self.name, **self.cells()}
        return {column: "" if value is None else str(value) for column, value in cells.items()}

    @mcp
    @agent_tool
    def edit_field(self, field: str, text: str) -> "StoryModel":
        """Change what this example says under field, a column of its row, to text; the column it is named by renames
        it. Save its story map and return it. A column its row does not have is refused with StoryMapEditRefused."""
        if field not in self.row:
            raise StoryMapEditRefused(self, "edit_field", f"{self.name} has no {field} column")
        if self._names_it(field):
            return self.rename(text)
        if not isinstance(self.value, dict):
            raise StoryMapEditRefused(self, "edit_field", f"{self.name} keeps its fields in a {type(self.value).__name__}, not a table row")
        self.value[field] = text
        return self.story_map.opened.save()

    @mcp
    @agent_tool
    def rename(self, name: str) -> "StoryModel":
        """Rename this example, and the column of its row that names it; save its story map and return it."""
        named = [column for column in self.naming_columns if self._names_it(column) and isinstance(self.value, dict)]
        if isinstance(self.value, str):
            self.value = name
        for column in named:
            self.value[column] = name
        self.scope.examples.rename(self, name)
        return self.story_map.opened.save()

    def edit_description(self, description: str) -> "StoryModel":
        """An example's row holds no description, so none is kept: refused with StoryMapEditRefused, and no tool offers
        it."""
        raise StoryMapEditRefused(self, "edit_description", f"{self.name} is a row of its table, which holds no description")

    @property
    def is_named_by_its_row(self) -> bool:
        """Whether a column of its own row holds its name, so a table of it needs no example column added."""
        cells = self.cells()
        return any(str(cells.get(column, "")) == self.name for column in self.naming_columns)

    def _names_it(self, field: str) -> bool:
        """Whether its row names it by field: `example` always does, `name` while it says its name."""
        return field == "example" or (field in self.naming_columns and self.row.get(field) == self.name)

    def _leave(self) -> None:
        """An example leaves the examples of its scope; nothing holds its place."""
        self.scope.examples.drop(self)
        self.parent = None


class Examples(dict):
    """Example name to value. Iterates as a table and each value can be written as code.

    `scope` is the story node these examples belong to. Putting an example in the
    map sets `example.scope` to that node.
    """

    def __init__(self, scope: Optional["StoryNode"] = None) -> None:
        super().__init__()
        self.scope = scope

    def __setitem__(self, name: str, example: "Example | ExampleValue") -> None:
        if not isinstance(example, Example):
            example = Example(str(name), example)
        example.scope = self.scope
        super().__setitem__(name, example)
        if isinstance(self.scope, StoryNode):
            self.scope.attach(example, "examples")

    def rename(self, example: Example, name: str) -> None:
        """Keep example under name, in the place it stood."""
        held = [(name if each is example else key, each) for key, each in self.items()]
        example.name = name
        dict.clear(self)
        dict.update(self, held)

    def drop(self, example: Example) -> None:
        """Hold example no longer."""
        for key in [key for key, each in self.items() if each is example]:
            del self[key]

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


@language_adapter(language="typescript")
@agent_toolset
class Increment(StoryNode):
    """A thin slice of the story map: the stories one release delivers. The increment refers to the map's own Story
    objects, which stay under their epics; a story is delivered by one increment at most."""

    _semantic_type_name = "Increment"
    # An increment goes by its slug after `increment:`, so it never shares a path with an epic of the same name.
    segment_prefix = "increment:"

    def __init__(
        self,
        name: "str | Increment",
        sequential_order: int = 0,
        stories: Optional[List["Story"]] = None,
    ) -> None:
        source = name if isinstance(name, Increment) else None
        if source is not None:
            name, sequential_order = source.name, source.sequential_order
        super().__init__(name=name, sequential_order=sequential_order)
        self.parent: Optional["StoryModel"] = None
        self.outcome: str = ""
        self.slicing_notes: str = ""
        self.decision_prompt: str = ""
        self.source: Optional["Source"] = None
        if source is not None:
            self.outcome, self.slicing_notes, self.decision_prompt = source.outcome, source.slicing_notes, source.decision_prompt
            self.description_text, self.source = source.description_text, source.source
        self._stories = ModelReferences(self, "stories")
        self.stories = stories or []

    @property
    def stories(self) -> List["Story"]:
        return self._stories

    @stories.setter
    def stories(self, stories: List["Story"]) -> None:
        self._stories.refill(stories)

    @property
    @data_field(key="stories")
    def delivered(self) -> List[str]:
        """The stories it delivers, by the address each one's tools take."""
        return [story.address for story in self.stories]

    @mcp
    @agent_tool
    def add_story(self, story: "Story") -> "StoryModel":
        """Deliver story, a story of the same story map, in this increment, taking it off the increment that delivered
        it before; save the map and return it."""
        found = self.story_map.descendants.node_at(story.path)
        for increment in self.story_map.increments:
            increment.stories = [each for each in increment.stories if each is not found]
        self.stories = [*self.stories, found]
        return self.story_map.opened.save()

    @mcp
    @agent_tool
    def remove_story(self, story: "Story") -> "StoryModel":
        """Stop delivering story in this increment; the story stays on its story map. Save the map and return it."""
        found = self.story_map.descendants.node_at(story.path)
        self.stories = [each for each in self.stories if each is not found]
        return self.story_map.opened.save()

    def clone(self) -> "Increment":
        """A copy delivering the same stories; a map that copies its stories as well hands the copy those."""
        return type(self)(self, stories=list(self.stories))


@language_adapter(language="typescript")
@agent_toolset
class Step(StoryNode):
    _semantic_type_name = "Step"
    graph_facts = ("keyword", "text", "phase", "concepts", "values", "linked_terms", "actor", "continuation", "callees", "body_text")

    def __init__(self, text: "str | Step", step_type: "StepType | None" = None, sequential_order: int = 0) -> None:
        """A step saying text, of step_type, at sequential_order; given a step, a copy of it. What a format reads about
        the step beyond that, its keyword, the concepts, values and actor its line names, and where it sits, is set on
        the step afterwards."""
        origin = text if isinstance(text, Step) else None
        name = ""
        if origin is not None:
            text, step_type, sequential_order, name = origin.text, origin.step_type, origin.sequential_order, origin.name
        label = name or (text.strip()[:_STEP_NAME_LENGTH] if text.strip() else f"step-{sequential_order}")
        super().__init__(name=label, sequential_order=sequential_order)
        self.text = text
        self.step_type = step_type
        self._keyword = ""
        self._ands = ModelChildren(self, "ands")
        self.concepts: List[str] = []
        self.values: List[str] = []
        self.linked_terms: List[str] = []
        self.actor = ""
        self.source: Optional["Source"] = None
        self.call_graph = CallGraph([])
        self.body = CodeBody()
        if origin is not None:
            self._copy_from(origin)

    def _copy_from(self, origin: "Step") -> None:
        """Take what origin was read with, its code, and a copy of each step chained onto it."""
        self._keyword = origin._keyword
        self.concepts, self.values = list(origin.concepts), list(origin.values)
        self.linked_terms = list(origin.linked_terms)
        self.actor, self.source = origin.actor, origin.source
        self.call_graph = CallGraph(getattr(origin, "call_graph", None) or [])
        self.take_code_from(origin)
        for extra in origin.ands:
            self._ands.append(type(self)(extra))

    @property
    def segment(self) -> str:
        """A step goes by its place: `step-2` is the second step of its scenario, or of the step it continues."""
        return f"step-{self.parent.holding(self).index(self) + 1}"

    @property
    def parts(self) -> List["StoryNode"]:
        return self.ands

    def holding(self, part: "StoryNode") -> List["StoryNode"]:
        return self._ands

    @property
    @data_field(key="text")
    def written_text(self) -> str:
        return self.text

    @mcp
    @agent_tool
    def edit_text(self, text: str) -> "StoryModel":
        """Change what this step says, save its story map, and return it."""
        self.text = text
        self.name = text.strip()[:_STEP_NAME_LENGTH] or self.name
        return self.story_map.opened.save()

    @property
    def body_text(self) -> str:
        """The code its story test gives the step; it saves with the graph, so the step is linked to the operations it
        calls whichever process holds the graph."""
        return self.body.text

    @property
    def code_key(self) -> tuple:
        """What this step says in code: while it still says it, the lines it was read with stand."""
        return (self.keyword, self.text, self.body.text)

    def read_code(self, block: "CodeBlock") -> None:
        """The body of the step block found where this step sits in its file, when that block is this step's call; a
        step whose text differs keeps no body."""
        if self.text == block.name:
            self.body = block.body

    @property
    @data_field
    def ands(self) -> List["Step"]:
        """And and But lines on this step, in order."""
        return sorted(self._ands, key=lambda step: step.sequential_order)

    @ands.setter
    def ands(self, ands: List["Step"]) -> None:
        self._ands.refill(ands)

    @property
    @data_field
    def keyword(self) -> str:
        """Gherkin keyword on the line: Given, When, Then, And, or But."""
        if self._keyword:
            return self._keyword[0].upper() + self._keyword[1:].lower()
        value = getattr(self.step_type, "value", self.step_type)
        return str(value).capitalize()

    @keyword.setter
    def keyword(self, word: str) -> None:
        self._keyword = (word or "").strip()

    def continue_with(self, keyword: str, text: str) -> "Step":
        """Chain an And or But line saying text onto this step, of this step's type, after the lines chained onto it
        already, and answer it."""
        continued = type(self)(text, self.step_type, len(self.ands) + 1)
        continued.keyword = keyword
        self.ands = [*self.ands, continued]
        return continued

    @property
    def continuation(self) -> bool:
        """An And or But line continues the clause before it."""
        if self._keyword:
            return self._keyword.casefold() in ("and", "but")
        return self.text.strip().startswith(("And ", "But "))

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

    @property
    def recorded_name(self) -> str:
        """`given a cart`: the keyword and the text, which is what a screen and a rule read a step by."""
        return f"{self.keyword.lower()} {self.text}".strip()

    @property
    def recorded_type(self) -> str:
        """Given, When, or Then from the step's phase, else from its keyword; a step with neither is a Step."""
        phase = self.phase or (self.keyword or "").casefold()
        return phase.capitalize() if phase in ("given", "when", "then") else "Step"

    def record(self, recording: StoryRecording, file: str, parent: "Node") -> None:
        """Add this step under parent, its scenario's or background's node (``steps``) or the step it continues
        (``ands``), then the steps chained onto it."""
        lines = recording.span_of(self, file, fallback_text=self.text)
        continuations = list(self.ands)
        node = recording.add(self, self._node_id(lines), lines)
        recording.graph.edges.link("ands" if isinstance(self.parent, Step) else "steps", parent, node)
        for continuation in continuations:
            continuation.record(recording, file, node)

    def _node_id(self, lines: "Source") -> str:
        """Its graph id: its kind, file, line, and a checksum of its name, so it keeps the same id in every process."""
        return f"stories:{self.recorded_type}:{lines.file}:{lines.start_line}:{self._name_checksum}"

    @property
    def _name_checksum(self) -> int:
        """A checksum of the step's recorded name for its graph id. A checksum, never ``hash``: Python salts ``hash``
        per process, and a step must keep its id in the worker that refreshes the graph and in the server."""
        return zlib.crc32(self.recorded_name.encode("utf-8")) & _STEP_CHECKSUM_MASK

    def clone(self) -> "Step":
        """A copy of this step, its code, and a copy of each step chained onto it."""
        return type(self)(self)


def _steps_key(steps: List["Step"]) -> tuple:
    return tuple(line.code_key for step in steps for line in (step, *step.ands))


class Background(StoryNode):
    _semantic_type_name = "Background"
    step_type = Step
    """The step type this format's backgrounds are made of; a copy of a background makes its steps through it."""

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
                self._steps.append(type(self).step_type(step))

    @property
    def steps(self) -> List["Step"]:
        return sorted(self._steps, key=lambda step: step.sequential_order)

    @steps.setter
    def steps(self, steps: List["Step"]) -> None:
        self._steps.refill(steps)

    @property
    def code_key(self) -> tuple:
        return (self.name, _steps_key(self.steps))

    @property
    def recorded_name(self) -> str:
        return self.name or "background"

    def record(self, recording: StoryRecording, file: str, parent: "Node") -> None:
        """Add this background under parent, its story's node, then its steps."""
        lines = recording.background_span(self, file)
        recording.place(self, lines)
        self.load_map_facts()
        node = recording.add(self, f"stories:Background:{file}:{self.recorded_name}", lines)
        recording.graph.edges.link("background", parent, node)
        for step in self.steps:
            step.record(recording, file, node)

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


@language_adapter(language="typescript")
@agent_toolset
class Scenario(StoryNode):
    """Behaviour walk-through under a story.

    Tree children: Background, Step, Example.
    """

    _semantic_type_name = "Scenario"
    step_type = Step
    background_type = Background
    """The step and background types this format's scenarios are made of; a copy of a scenario makes its parts
    through them."""

    def __init__(self, name: "str | Scenario" = "", sequential_order: int = 0) -> None:
        source = name if isinstance(name, Scenario) else None
        super().__init__(
            name=source.name if source is not None else name,
            sequential_order=source.sequential_order if source is not None else sequential_order,
        )
        self._backgrounds = ModelChildren(self, "background")
        self._steps = ModelChildren(self, "steps")
        self.examples = source.examples.clone(self) if source is not None else Examples(self)
        self.is_outline: bool = source.is_outline if source is not None else False
        self.evidence: List[str] = list(source.evidence) if source is not None else []
        self.source: Optional["Source"] = source.source if source is not None else None
        if source is not None:
            self.take_code_from(source)
            for background in source.backgrounds:
                self.backgrounds.append(type(self).background_type(background))
            for step in source.steps:
                self.steps.append(type(self).step_type(step))

    @property
    def backgrounds(self) -> List[Background]:
        return self._backgrounds

    @backgrounds.setter
    def backgrounds(self, backgrounds: List[Background]) -> None:
        self._backgrounds.refill(backgrounds)

    @property
    @data_field
    def steps(self) -> List[Step]:
        return self._steps

    @steps.setter
    def steps(self, steps: List[Step]) -> None:
        self._steps.refill(steps)

    @property
    @data_field(key="examples")
    def example_rows(self) -> List[Example]:
        """Its examples, a row each, in the order its table gives them; each is edited through its own tools."""
        return list(self.examples.values())

    @property
    def parts(self) -> List["StoryNode"]:
        return [*self.steps, *self.examples.values()]

    def holding(self, part: "StoryNode") -> List["StoryNode"]:
        if isinstance(part, Example):
            raise StoryMapEditRefused(part, "move", "an example keeps the place its table gives it")
        return self._steps

    @mcp
    @agent_tool
    def new_step(self, step_type: str, text: str) -> "StoryModel":
        """Add a step saying text, of step_type (given, when or then), after this scenario's steps; save its story map
        and return it."""
        self.steps.append(type(self).step_type(text, StepType(step_type), len(self.steps) + 1))
        return self.story_map.opened.save()

    def steps_in(self, step_type: StepType) -> List[Step]:
        return [step for step in self.steps if step.step_type == step_type]

    def when_then_runs(self) -> List[tuple]:
        """Walk steps. A When after a Then starts the next run."""
        runs: List[tuple] = []
        run: tuple = ([], [])
        for step in self.steps:
            if step.step_type == StepType.WHEN and run[1]:
                runs.append(run)
                run = ([], [])
            if step.step_type == StepType.WHEN:
                run[0].append(step)
            elif step.step_type == StepType.THEN:
                run[1].append(step)
        return runs + [run] if run[0] or run[1] else runs

    def load_map_facts(self) -> None:
        self._load_opening()
        self._load_path_case()
        self.generic_handler = False
        self.near_duplicate = False
        self.shared_verb = ""
        self.child_count = len(self.steps)
        self.child_label = "steps"
        self.child_band = ""

    @property
    def code_key(self) -> tuple:
        """What this scenario says in code: its name, examples, backgrounds, and every step with its body."""
        backgrounds = tuple(background.code_key for background in self.backgrounds)
        return (self.name, tuple(self.examples), backgrounds, _steps_key(self.steps))

    def record(self, recording: StoryRecording, story: "Story", parent: "Node") -> None:
        """Add this scenario under parent, the node of story, the Story walking it, with its steps and the examples it
        uses: its own, those its own Background holds, and those story's Background holds. A scenario read from a story
        test sits in that file, not in the story map its Story came from, and is shared by every Story of that name, so
        the story walking it is handed in rather than read from its parent."""
        file = file_of(self) or file_of(story)
        scoped = [example for background in story.backgrounds for example in background.examples.values()]
        lines = recording.span_of(self, file)
        recording.place(self, lines)
        self.load_map_facts()
        node = recording.add(self, f"stories:Scenario:{file}:{self.name}", lines)
        node.set_fact("is_outline", bool(self.is_outline))
        if file != file_of(story):
            # Its steps and examples read the facts of the file that writes them, not of the story map its Story is in.
            node.set_facts(recording.source_of(file).facts)
        recording.graph.edges.link("scenarios", parent, node)
        for step in self.steps:
            step.record(recording, file, node)
        own_background = [example for background in self.backgrounds for example in background.examples.values()]
        used = {example.name: example for example in [*self.examples.values(), *own_background, *scoped]}
        for example in used.values():
            example.record(recording, node, lines)

    def clone(self) -> "Scenario":
        cloned = type(self)(self.name, self.sequential_order)
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


@language_adapter(language="typescript")
@agent_toolset
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
        self.columns = EpicColumns(self)
        self.descendants = Descendants(self)
        if source is None:
            return
        self.estimate = source.estimate or ""
        self.description_text = source.description_text
        self.take_code_from(source)
        build_story = story_class or Story
        for child in source.epics:
            self.epics.append(type(self)(child, story_class=build_story))
        for story in source.stories:
            self.stories.append(build_story(story))

    @property
    @data_field
    def epics(self) -> List["Epic"]:
        return self._epics

    @epics.setter
    def epics(self, epics: List["Epic"]) -> None:
        self._epics.refill(epics)

    @property
    @data_field
    def stories(self) -> List["Story"]:
        return self._stories

    @stories.setter
    def stories(self, stories: List["Story"]) -> None:
        self._stories.refill(stories)

    @property
    def parts(self) -> List["StoryNode"]:
        return [*self.epics, *self.stories]

    def holding(self, part: "StoryNode") -> List["StoryNode"]:
        return self._epics if isinstance(part, Epic) else self._stories

    @mcp
    @agent_tool
    def new_epic(self, name: str) -> "StoryModel":
        """Add a sub-epic called name after this epic's sub-epics; save its story map and return it."""
        self.epics.append(type(self)(name, len(self.epics) + 1))
        return self.story_map.opened.save()

    @mcp
    @agent_tool
    def new_story(self, name: str) -> "StoryModel":
        """Add a story called name after this epic's stories; save its story map and return it."""
        self.stories.append(self.story_map.story_type(name, len(self.stories) + 1))
        return self.story_map.opened.save()

    @property
    def is_sub_epic(self) -> bool:
        """An epic nested under another epic."""
        return isinstance(self.parent, Epic)

    @property
    def recorded_type(self) -> str:
        return "SubEpic" if self.is_sub_epic else "Epic"

    @property
    def top_epic(self) -> "Epic":
        """The epic of the story map this epic sits under: itself when it is one."""
        return self.parent.top_epic if self.is_sub_epic else self

    def record(self, recording: StoryRecording, parent: "Node") -> None:
        """Add this epic or sub-epic under parent, the practice's root or its epic's node, then its sub-epics and its
        stories. An epic sits on the line that names it in the first file any story under it was read from."""
        story_file = self._first_story_file() or file_of(self)
        folder = self._folder_above(story_file)
        self.source = recording.name_span(story_file, self.name, folder)
        self.load_map_facts()
        self.evidence = self._evidence_in(recording, story_file)
        node = recording.add(self, f"stories:{self.recorded_type}:{folder}:{self.name}", self.source)
        recording.graph.edges.link("decomposedInto", parent, node)
        for child in self.epics:
            child.record(recording, node)
        for story in self.stories:
            story.record(recording, node)

    def _folder_above(self, story_file: str) -> str:
        """The folder this epic is recorded in: the one story_file sits in, and for a top epic that holds sub-epics the
        folder above that, since its first story file sits in a sub-epic's folder."""
        parts = [part for part in story_file.split("/") if part][:-1]
        if not self.is_sub_epic and self.epics and parts:
            parts = parts[:-1]
        return "/".join(parts) or "."

    def _first_story_file(self) -> str:
        """The first file any story under this epic was read from; empty when none names a file."""
        return next((file for story in self.descendants.stories() for file in [file_of(story)] if file), "")

    def _evidence_in(self, recording: StoryRecording, story_file: str) -> List[str]:
        """What this epic declares, else its sub-epic file's opening docblock, else the labels its children carry."""
        if self.evidence:
            return list(self.evidence)
        declared = recording.source_of(story_file).evidence if self.is_sub_epic else []
        if declared:
            return declared
        labels: List[str] = []
        for child in self.epics:
            labels.extend(child._evidence_in(recording, child._first_story_file()))
        for story in self.stories:
            labels.extend(story.evidence)
        return list(dict.fromkeys(labels))

    def clone(self) -> "Epic":
        cloned = type(self)(self.name, self.sequential_order)
        cloned.estimate = self.estimate or ""
        cloned.description_text = self.description_text
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
        self._load_child_band(len(self.epics) + len(self.stories), *self._child_band_for_layer())
        self.shared_verb = self._shared_opening()

    def _child_band_for_layer(self) -> tuple[str, int, int]:
        """The children this node is counted by and the band they fit (`child-count-fits-layer`). A node holding
        sub-epics groups 3-9 outcomes; a sub-epic holding only stories holds 2-9, since its sibling sub-epics carry the
        breadth; a top epic holding only stories holds 4-9, since an epic of two or three stories is usually a sub-epic
        of a neighbouring epic."""
        if self.epics:
            return "children", 3, 9
        if self.is_sub_epic:
            return "stories", 2, 9
        return "stories", 4, 9

    def _shared_opening(self) -> str:
        names = [story.name.strip().casefold() for story in self.stories if story.name.strip()]
        verbs = [name.split()[0] for name in names if name.split()]
        if len(verbs) < 2 or len(set(verbs)) != 1 or len(set(names)) < 2:
            return ""
        return verbs[0]

    @property
    def depth(self) -> int:
        parent = self.parent
        if not isinstance(parent, Epic):
            return 0
        if not isinstance(parent.parent, Epic):
            return 0
        return parent.depth + 1



# The fact a story's graph node carries when a scenarios file specifies it and the story map does not hold it.
NOT_ON_STORY_MAP = "not_on_story_map"


@language_adapter(language="typescript")
@agent_toolset
class Story(StoryNode):
    _semantic_type_name = "Story"
    scenario_type = Scenario
    background_type = Background

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
        self.story_type = story_type
        self.actors: List[str] = []
        self.domain_terms: List[str] = []
        self.evidence: List[str] = []
        self._backgrounds = ModelChildren(self, "background")
        self._scenarios = ModelChildren(self, "scenarios")
        if source is not None:
            self._copy_from(source)

    def _copy_from(self, source: "Story") -> None:
        """Take what source says, its code, and a copy of each of its backgrounds and scenarios in this story's types."""
        self.story_type = source.story_type
        self.actors, self.domain_terms, self.evidence = list(source.actors), list(source.domain_terms), list(source.evidence)
        self.description_text = source.description_text
        self.take_code_from(source)
        for background in source.backgrounds:
            self.backgrounds.append(type(self).background_type(background))
        for scenario in source.scenarios:
            self.scenarios.append(type(self).scenario_type(scenario))

    @property
    def backgrounds(self) -> List["Background"]:
        return self._backgrounds

    @backgrounds.setter
    def backgrounds(self, backgrounds: List["Background"]) -> None:
        self._backgrounds.refill(backgrounds)

    @property
    @data_field
    def scenarios(self) -> List["Scenario"]:
        return self._scenarios

    @scenarios.setter
    def scenarios(self, scenarios: List["Scenario"]) -> None:
        self._scenarios.refill(scenarios)

    @property
    @data_field(key="story_type")
    def kind(self) -> str:
        """user, system or technical."""
        return StoryType(self.story_type).value

    @property
    @data_field
    def acceptance_tests(self) -> List[str]:
        """The acceptance-test files of its story map's session that hold this story, as paths from the project: they
        are read, not edited, through the story map; none for a map opened in no session."""
        return self.story_map.opened.acceptance_tests_of(self)

    @property
    def parts(self) -> List["StoryNode"]:
        return list(self.scenarios)

    def holding(self, part: "StoryNode") -> List["StoryNode"]:
        return self._scenarios

    @mcp
    @agent_tool
    def new_scenario(self, name: str) -> "StoryModel":
        """Add a scenario called name after this story's scenarios; save its story map and return it."""
        self.scenarios.append(type(self).scenario_type(name, len(self.scenarios) + 1))
        return self.story_map.opened.save()

    def load_map_facts(self) -> None:
        self._load_opening()
        self._load_path_case()
        self.generic_handler = name_facts.names_generic_handler(self.name)
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

    @property
    def top_epic(self) -> Optional[Epic]:
        """The epic of the story map this story sits under; none for a story under no epic."""
        return self.parent.top_epic if isinstance(self.parent, Epic) else None

    def record(self, recording: StoryRecording, parent: "Node | None") -> None:
        """Add this story under parent, its epic's node, with the facts of the file it was read from, then its
        backgrounds and its scenarios. A story the map does not hold has no parent: it is added under no epic and
        marked as not on the story map."""
        recording.announce(self)
        file = file_of(self)
        lines = recording.span_of(self, file)
        self.load_map_facts()
        node = recording.add(self, f"stories:Story:{file}:{self.name}", lines)
        for fact, held in recording.source_of(file).facts.items():
            node.set_fact(fact, held)
        if parent is None:
            node.set_fact(NOT_ON_STORY_MAP, True)
        else:
            recording.graph.edges.link("decomposedInto", parent, node)
        # A Background with no step is the place a reader keeps for one, not a Background anybody wrote.
        own = [background for background in self.backgrounds if background.steps]
        for background in own:
            background.record(recording, file, node)
        if not own:
            # The shared Background is read from the scenarios file, which may not be the story map the story is in.
            for background in self._shared_backgrounds():
                background.record(recording, file_of(self.scenarios[0]) or file, node)
        for scenario in self.scenarios:
            scenario.record(recording, self, node)

    def _shared_backgrounds(self) -> List["Background"]:
        """The Background every one of this story's scenarios holds a copy of: a Background above the scenarios is the
        state they share, which the reader gives each scenario. It belongs to the story, so it is recorded once there,
        and its steps are in the graph with the scenarios'. A Background under one scenario's heading is that
        scenario's alone and is not one of them."""
        held = [scenario.backgrounds for scenario in self.scenarios]
        if not held or not all(held):
            return []
        keys = [{background.code_key for background in backgrounds} for backgrounds in held]
        return [background for background in held[0] if background.steps and all(background.code_key in each for each in keys)]

    def clone(self) -> "Story":
        cloned = type(self)(self.name, self.sequential_order, self.story_type)
        cloned.description_text = self.description_text
        cloned.actors = list(self.actors)
        cloned.domain_terms = list(self.domain_terms)
        cloned.evidence = list(self.evidence)
        for background in self.backgrounds:
            cloned.backgrounds.append(background.clone())
        for scenario in self.scenarios:
            cloned.scenarios.append(scenario.clone())
        cloned.take_code_from(self)
        return cloned


@identity("file")
@language_adapter(language="typescript")
@agent_toolset
class StoryModel(StoryNode):
    """A story map: its epics, and the increments that deliver its stories. One opened in a session through its tools
    (``load``) holds the file it was read from (an *OpenedStoryMap*) and saves itself there after every edit."""

    # A story map opened in a session writes only its own file and the formats chosen beside it, under the session's
    # roots.

    _semantic_type_name = "StoryModel"
    epic_type = Epic
    story_type = Story

    def __init__(self, source: Optional["StoryModel | Graph"] = None, graph: Optional[Graph] = None) -> None:
        if isinstance(source, Graph):
            graph = source
            source = None
        super().__init__(name="StoryModel", sequential_order=0, graph=graph)
        self._epics = NumberedChildren(self, "decomposedInto")
        self._increments = NumberedChildren(self, "increments")
        self.examples = Examples(self)
        self.descendants = Descendants(self)
        self.test_scenarios = StoryTestScenarios(self)
        # The stories a scenarios file specifies that this map does not hold. Each is recorded on a graph with its
        # scenarios, under no epic and marked ``not_on_story_map``, so a file that names a story the map lacks is seen
        # rather than left out.
        self.unplaced_stories: List[Story] = []
        # The files this map was read from, so recording the map on a graph finds each node's lines without reading a
        # file again.
        self.sources = StorySources()
        # Where each node links in the folder this map was placed in to be drawn; none until a render places it.
        self.links = None
        # The file it was opened from in a session, which saves it after every edit; nowhere for a map read any other
        # way, which saves no edit.
        self.opened: "OpenedStoryMap | UnopenedStoryMap" = UnopenedStoryMap(self)
        # The file that keeps its increments and writes them on a save (``write(increments)``), such as the thin slice
        # beside a markdown story map; None for a map that keeps none.
        self.slicing = None
        if isinstance(source, StoryModel):
            self._copy_from(source)

    def _copy_from(self, source: "StoryModel") -> None:
        """Take source's description and examples, and a copy of its epics and increments in this map's types."""
        self.description_text = source.description_text
        self.examples = source.examples.clone(self)
        for epic in source.epics:
            self.epics.append(self.epic_type(epic, story_class=self.story_type))
        StoryCopies(source, self).copy_increments(self.increment_type)

    @classmethod
    @tool_subject
    def load(cls, file: str, *, call: ToolCall) -> "StoryModel":
        """The story map in file, a Stories file named from the project: a story map, a scenario file, or a story test
        merged onto its story map, read by the Stories practice of the session the call works in. A file outside the
        session's roots is refused (PathOutsideRootsError)."""
        session = call.session
        path = session.paths.path_named(file)
        files = session.session_files.file_manager
        files.read(os.path.relpath(path, files.workpath))
        stories = session.graph.practices.of(cls.practice_class)
        model = stories.open_file(path, session.repo_path)
        model.opened = OpenedStoryMap(model, path, session)
        return model

    @classmethod
    @mcp
    @agent_tool
    def open_in_session(cls, *, call: ToolCall) -> "StoryModel":
        """Return the story map of the session open in the project: the first story map file its Stories practice
        declares there, so a page that follows the open session shows the ticket activated last."""
        stories = call.session.graph.practices.of(cls.practice_class)
        story_map = next(iter(stories.fidelities))
        made = [entry.path for entries in story_map.declared.files().values() for entry in entries if entry.exists]
        if not made:
            raise StoryNodeNotFound(f"{call.session.name}: no story map", cls)
        return cls.load(made[0], call=call)

    @property
    @data_field
    def file(self) -> Annotated[str, SourceFile]:
        """The file it was opened from, as a path from the project; empty for a map read any other way."""
        return self.opened.file

    @property
    @data_field
    def formats(self) -> "FidelitySessionOutput":
        """What the fidelity declaring its file keeps in the session: the formats it offers, and the ones chosen, which
        a save renders beside its file."""
        return self.opened.fidelity.session_output

    @property
    @data_field
    def refusal(self) -> str:
        """Why an edit to it is not saved, such as a scenario file opened to be read; empty when edits are saved."""
        return self.opened.refusal

    @mcp
    @agent_tool
    def show(self) -> "StoryModel":
        """Return the story map as its file holds it now, with the formats chosen for its fidelity and, when an edit
        would not be saved, why."""
        return self

    @mcp
    @agent_tool
    def new_epic(self, name: str) -> "StoryModel":
        """Add an epic called name after the map's epics; save the map and return it."""
        self.epics.append(self.epic_type(name, len(self.epics) + 1))
        return self.opened.save()

    @mcp
    @agent_tool
    def new_increment(self, name: str) -> "StoryModel":
        """Add an increment called name after the map's increments, delivering no story yet; save the map and return
        it. A map that keeps no increments, such as a scenario file, refuses it with StoryMapEditRefused."""
        if self.slicing is None:
            raise StoryMapEditRefused(self, "new_increment", f"{self.file} keeps no increments")
        self.increments.append(self.increment_type(name, len(self.increments) + 1))
        return self.opened.save()

    increment_type = Increment
    """The increment type this format's maps are sliced by."""

    @property
    @data_field
    def scope(self) -> List[str]:
        """The stories of this map the session it was opened in names, by address: the part of the map that session's
        ticket covers. None when the session names no story, or the map was opened in no session."""
        return [story.address for story in self.descendants.stories_named(self.opened.session_stories)]

    @property
    def parts(self) -> List["StoryNode"]:
        return [*self.epics, *self.increments]

    def holding(self, part: "StoryNode") -> List["StoryNode"]:
        return self._increments if isinstance(part, Increment) else self._epics

    def copy_of(self, source: "StoryModel") -> "StoryModel":
        """source copied into this format's node types, with this model's settings, so this format's nodes write it.
        It is asked of a model, not its class, because a code format copies with its own settings."""
        return type(self)(source)

    @property
    @data_field
    def epics(self) -> List[Epic]:
        return self._epics

    @property
    @data_field
    def increments(self) -> List[Increment]:
        return self._increments

    def record(self, practice: "PracticeGuidance", *, on_node: Optional[Callable[[str], None]] = None) -> None:
        """Write this map's epics, stories, backgrounds, scenarios, steps, and examples onto practice, the practice
        that holds Stories in a graph; on_node hears each story as it is written."""
        with self.batch_schema_sync():
            StoryRecording(self, practice, on_node).write()

    def clone(self) -> "StoryModel":
        cloned = type(self)()
        for epic in self.epics:
            cloned.epics.append(epic.clone())
        StoryCopies(self, cloned).copy_increments(lambda increment, stories: type(increment)(increment, stories=stories))
        cloned.examples = self.examples.clone(cloned)
        cloned.description_text = self.description_text
        return cloned


class NumberedChildren(ModelChildren):
    """The epics or increments of a story map, numbered in the order they stand: one appended takes the next number."""

    def append(self, held: StoryNode) -> None:
        super().append(held)
        _renumber(self)


class Descendants:
    """The epics and stories under an epic or a story map, at any depth, in map order, and the node a path names
    among them: what a story map is searched and placed by."""

    def __init__(self, holder: "Epic | StoryModel") -> None:
        self._holder = holder

    def epics(self) -> List[Epic]:
        """Every epic nested under its holder, each before its own children."""
        return [found for epic in self._holder.epics for found in (epic, *epic.descendants.epics())]

    def stories(self) -> List["Story"]:
        """Every Story its holder and its nested epics hold, in map order."""
        return [story for epic in self._holding_stories() for story in epic.stories]

    def stories_named(self, names: List[str]) -> List["Story"]:
        """Its stories that names name, in the order names gives them; a name no story has adds nothing. A thin slice
        names the stories it delivers, so an increment read from one takes the map's stories through this."""
        first = self.stories_by_name()
        return [first[name] for name in names if name in first]

    def stories_by_name(self) -> Dict[str, "Story"]:
        """Each name one of its stories has, mapped to the first story in map order that has it."""
        first: Dict[str, "Story"] = {}
        for story in self.stories():
            first.setdefault(story.name, story)
        return first

    def place_in(self, file: str) -> None:
        """Name file on every epic and story under its holder, and on an epic holder itself, that names no file yet;
        the line stays unknown."""
        for node in [*self._holding_stories(), *self.stories()]:
            if not node.has_source_file:
                node.source = source_at(file)

    def node_at(self, path: str) -> StoryNode:
        """The node path names below its holder; the holder itself for an empty path. StoryNodeNotFound for one it does
        not hold."""
        node: StoryNode = self._holder
        for segment in filter(None, path.split(".")):
            node = next((part for part in node.parts if part.segment == segment), None)
            if node is None:
                raise StoryNodeNotFound(path, StoryNode)
        return node

    def _holding_stories(self) -> List[Epic]:
        """The epics whose own stories are its stories: an epic holder itself, then every epic under it."""
        own = [self._holder] if isinstance(self._holder, Epic) else []
        return [*own, *self.epics()]


class EpicColumns:
    """How many story columns an epic spans on a drawn map, and how deep its sub-epics nest: what a diagram format
    lays its bars out by."""

    def __init__(self, epic: Epic) -> None:
        self._epic = epic

    def leaf_epics(self) -> List[Epic]:
        """The epics whose stories sit in columns under the epic: its innermost sub-epics, or itself when it has none."""
        if not self._epic.epics:
            return [self._epic]
        return [leaf for child in self._epic.epics for leaf in child.columns.leaf_epics()]

    def estimate_label(self) -> str:
        """The epic's estimate as a bar writes it, `* {estimate}`; empty for an epic with none."""
        estimate = (self._epic.estimate or "").strip()
        if not estimate:
            return ""
        if estimate.startswith("*"):
            return estimate
        return f"* {estimate}"

    def has_estimate(self) -> bool:
        """The epic or a sub-epic under it gives an estimate."""
        if (self._epic.estimate or "").strip():
            return True
        return any(child.columns.has_estimate() for child in self._epic.epics)

    def span(self) -> int:
        """Story-grid columns a top-level epic occupies: its own stories, then each nested epic. An empty epic is one
        column."""
        nested = sum(max(child.columns.diagram_span(), 1) for child in self._epic.epics)
        return max(len(self._epic.stories) + nested, 1)

    def diagram_span(self) -> int:
        """Bar width in story-pitch columns. Stories and nested epics both take columns; an estimate widens a leaf
        epic."""
        nested = sum(child.columns.diagram_span() for child in self._epic.epics)
        story_columns = len(self._epic.stories)
        if self._epic.epics:
            return max(nested + story_columns, 1)
        estimate = self._epic.estimate.strip()
        if not estimate:
            return max(story_columns, 1)
        if story_columns == 0:
            fewest, most = _EMPTY_EPIC_COLUMNS
            return max(fewest, min(most, (len(estimate) + _ESTIMATE_LEAD_CHARACTERS) // _ESTIMATE_CHARACTERS_PER_COLUMN))
        fewest, most = _EXTRA_EPIC_COLUMNS
        return story_columns + max(fewest, min(most, (len(estimate) + _ESTIMATE_EXTRA_LEAD_CHARACTERS) // _ESTIMATE_CHARACTERS_PER_EXTRA_COLUMN))

    def tree_depth(self) -> int:
        """The depth of the deepest sub-epic under the epic; its own depth when it has none."""
        if not self._epic.epics:
            return self._epic.depth
        return max(child.columns.tree_depth() for child in self._epic.epics)


class StoryTestScenarios:
    """The scenarios a story map's stories take from the story tests that specify them. A story test names the Story
    it specifies, and the markdown and the drawio of one story map each hold that Story, so every Story of that name
    takes its scenarios. A Story the map does not have takes nothing."""

    def __init__(self, story_map: "StoryModel") -> None:
        self._story_map = story_map
        # The stories that already took a story test's scenarios, which the next story test of the same story adds to.
        self._specified: set[int] = set()

    def take(self, stories: List["Story"], file: str) -> None:
        """Give the scenarios and backgrounds of each of stories, read from the story test file, to every Story of the
        same name, each scenario keeping the story test as its source. The first story test a Story takes replaces the
        scenarios the map itself gave it; each later one adds its own after them, so a story written in a shared story
        file and a screen spec holds the scenarios of both."""
        for read, story in self._same_named(stories, file):
            if id(story) in self._specified:
                story.scenarios = [*story.scenarios, *read.scenarios]
                continue
            self._specified.add(id(story))
            story.backgrounds = list(read.backgrounds)
            story.scenarios = list(read.scenarios)

    def drop(self) -> None:
        """Take every story's scenarios and backgrounds away, leaving the map: at a fidelity whose scenarios come from
        other files, the ones the map's own story tests hold are not read."""
        for story in self._story_map.descendants.stories():
            story.scenarios = []
            story.backgrounds = []

    def _same_named(self, stories: List["Story"], file: str) -> List[tuple]:
        """Each read story beside each Story of the map with its name, its scenarios placed in file."""
        for read in stories:
            for scenario in read.scenarios:
                scenario.source = source_at(file)
        held = self._story_map.descendants.stories()
        return [(read, story) for read in stories for story in held if story.name == read.name]


def _renumber(nodes: List[StoryNode]) -> None:
    """Number nodes in the order they stand, from 1."""
    for i, node in enumerate(nodes, start=1):
        node.sequential_order = i
