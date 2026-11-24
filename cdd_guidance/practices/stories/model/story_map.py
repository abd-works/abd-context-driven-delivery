"""Story map nodes: StoryNode, StoryMap, Epic, Story, Scenario, Step, Background, Example, Increment.

A nested epic is an epic whose parent is an epic. Each node keeps its fields in one list (`_copy_fields`), which `copy_of` and `clone` share.
"""

from __future__ import annotations

import os
import zlib
from dataclasses import dataclass
from pathlib import Path
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

from .name_facts import NameFacts
from .opened_story_map import OpenedStoryMap, StoryMapEditRefused, UnopenedStoryMap
from .story_copies import StoryCopies
from .story_map_files import source_at
from .story_recording import StoryRecording, StorySources, file_of
from harness.guidance.practice_formats import FormatAdapter

if TYPE_CHECKING:
    from pathlib import Path

    from harness.graph.graph import Node, Source

    from .story_file import StoryBlock
    from harness.guidance.guidance import PracticeGuidance

    from space.session.practices.practice_session_output import FidelitySessionOutput

# A step goes by its text, cut to this many characters, so a long step still reads as one name.
_STEP_NAME_LENGTH = 80
# A step's graph id ends in a 24-bit checksum of its name: short enough to read in an id, long enough that two steps
# on one line of one file do not share it.
_STEP_CHECKSUM_MASK = 0xFFFFFF

# What an example stands for: a field map, a class, an object whose fields are its cells, or its own name.
ExampleValue = Any

# Pairs the schema names with belongsTo. The facade does not grow a method for them.
_BELONGS = {
    ("Epic", "Epic"),
    ("Story", "Epic"),
    ("Background", "Story"),
    ("Step", "Scenario"),
}


# How a copy makes one part of the node it copies: from the part and the class the copying node holds that part as.
CopyPart = Callable[["StoryNode", type], "StoryNode"]


def _as_part_class(part: "StoryNode", part_class: type) -> "StoryNode":
    """part made as part_class: a copy into another format makes each part in that format."""
    return part_class.copy_of(part)


def _as_own_class(part: "StoryNode", part_class: type) -> "StoryNode":
    """part cloned as the class it has: a clone keeps each part's own class."""
    return part.clone()


@dataclass(frozen=True)
class ChildBand:
    """How many children a node of one layer of a story map holds: what its children are counted as, and the fewest
    and the most that read well."""

    label: str
    fewest: int
    most: int

    @property
    def written(self) -> str:
        """The band as a rule's text and a finding write it: ``3-9``."""
        return f"{self.fewest}-{self.most}"

    def holds(self, count: int) -> bool:
        """Whether count fits the band; a node with no children yet fits, since they are simply not written."""
        return count == 0 or self.fewest <= count <= self.most


@dataclass(frozen=True)
class LayerBands:
    """The band of each layer of a story map (`child-count-fits-layer`): a node holding sub-epics groups outcomes; a
    sub-epic holding only stories may hold few, since its sibling sub-epics carry the breadth; a top epic holding only
    stories needs more, since an epic of two or three stories is usually a sub-epic of a neighbouring epic."""

    holding_sub_epics: ChildBand
    sub_epic: ChildBand
    flat_epic: ChildBand


# The one place the numbers of the story map's rules are written. The checks read them here, and the practice's
# document and templates carry a marker for each (``{{child_band.sub_epic}}``), filled when the guidance is read.
LAYER_BANDS = LayerBands(ChildBand("children", 2, 9), ChildBand("stories", 2, 9), ChildBand("stories", 4, 9))
# The most code scenarios a story holds before it is too big to be one interaction (`story-scenarios-at-most-seven`).
MOST_SCENARIOS = 7


class StoryNodeNotFound(LookupError):
    """A tool call named a node its story map does not hold, or a node of another kind than the tool acts on."""

    def __init__(self, node: str, kind: type) -> None:
        super().__init__(f"no {kind.__name__} {node!r} on its story map")
        self.node = node
        self.kind = kind


@hosted_only
@identity("node")
class StoryNode(ModelNode, ABC):
    """A story-map object and the graph node for that object.

    Subclasses declare `_semantic_type_name` so cross-format nodes
    (e.g. MarkdownEpic vs JsonEpic) share one semantic axis.
    Pass a graph the same way you pass another model. Omit it and this node
    keeps a graph of its own until a parent adopts it.
    """

    _semantic_type_name: str = "StoryNode"
    graph_facts = ("evidence", "scenario_count")
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

    def load_map_facts(self) -> None:
        """Keep the facts the story map's rules read about this node (*NameFacts*): a node of no layer holds no children
        it is sized by, and names a generic handler when its name opens with one."""
        facts = self._name_facts()
        facts.judge(generic_handler=facts.opens_with_generic_handler)
        self.set_facts(facts.facts)

    def _name_facts(self) -> NameFacts:
        """What the node's name and file say, before it counts its children and judges its place in the map."""
        return NameFacts(self.name, self.source.file or "")

    @property
    def recorded_name(self) -> str:
        """The name this object's graph node is called by."""
        return self.name

    # The node type this object's graph node takes: its semantic type, unless a kind of node records itself as another
    # (a step as Given, When or Then; an epic under another as SubEpic).
    recorded_type = property(ModelNode.semantic_type)

    @classmethod
    def copy_of(cls, source: "StoryNode") -> "StoryNode":
        """source made as this class, each of its parts made as the class this class holds that part as: how a story
        map is copied into another format, so a markdown epic copied from a plain one holds markdown stories."""
        copy = cls(source.name)
        copy._copy_fields(source, _as_part_class)
        return copy

    def clone(self) -> "StoryNode":
        """A copy of this node as its own class, each of its parts a clone keeping the class it has, so a markdown
        story under a plain epic stays a markdown story."""
        copy = type(self)(self.name)
        copy._copy_fields(self, _as_own_class)
        return copy

    @abstractmethod
    def _copy_fields(self, original: "StoryNode", copy_part: "CopyPart") -> None:
        """Take what original says, and each of its parts as copy_part copies it: the one list of a node's fields that
        a copy into another format and a clone share."""

    # -- edits a person or an agent makes through the story map's tools ---------------------------------------------
    # Every edit saves through its story map before it answers, and answers the story map, so the page shows the map as
    # its files now hold it. A tool names a node `{file}#{path}`: the file its map was opened from, and the slugs from
    # its top epic down (`checkout.pay.pay-by-card`), a step by its place under its scenario (`step-2`).

    @classmethod
    @tool_subject
    def load(cls, node: str, *, call: ToolCall) -> "StoryNode":
        """The node the call names, `{file}#{path}`, on the story map read from that file now."""
        file, _, path = node.partition("#")
        found = StoryMap.load(file, call=call).descendants.node_at(path)
        if not isinstance(found, cls):
            raise StoryNodeNotFound(node, cls)
        return found

    @property
    def story_map(self) -> "StoryMap":
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
    def rename(self, name: str) -> "StoryMap":
        """Rename this node of its story map, save the map, and return it."""
        self.name = name
        return self.story_map.opened.save()

    @mcp
    @agent_tool
    def edit_description(self, description: str) -> "StoryMap":
        """Change what the story map says about this node under its heading, save the map, and return it."""
        self.description_text = description.strip()
        return self.story_map.opened.save()

    @mcp
    @agent_tool
    def move_before(self, other: "StoryNode") -> "StoryMap":
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
    def remove(self) -> "StoryMap":
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


class CodeHeld(StoryNode):
    """The code a node of the story map was read with in a language: the block it was written as (``written``), the
    story file a story was read with (``file_written``, its path and its own code around its stories, which the stories
    read from one file share), and the code its scenarios or steps share (``setup``). An epic, a story, a background, a
    scenario, and a step hold it; an example and an increment are written with no code of their own."""

    def __init__(self, name: str, sequential_order: int, graph: Optional[Graph] = None):
        super().__init__(name, sequential_order, graph)
        self.written: Optional[WrittenBlock] = None
        self.file_written: Optional[WrittenBlock] = None
        self.setup = CodeBody()

    def take_code_from(self, source: "CodeHeld") -> None:
        """Keep the code the source was read with, so a copy in another channel can still write it back."""
        self.written = source.written
        self.file_written = source.file_written
        self.setup = source.setup
        if hasattr(self, "body"):
            self.body = getattr(source, "body", CodeBody())


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

    def _copy_fields(self, original: "Example", copy_part: CopyPart) -> None:
        self.value = dict(original.value) if isinstance(original.value, dict) else original.value
        self.sequential_order, self.scope = original.sequential_order, original.scope

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
    def edit_field(self, field: str, text: str) -> "StoryMap":
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
    def rename(self, name: str) -> "StoryMap":
        """Rename this example, and the column of its row that names it; save its story map and return it."""
        named = [column for column in self.naming_columns if self._names_it(column) and isinstance(self.value, dict)]
        if isinstance(self.value, str):
            self.value = name
        for column in named:
            self.value[column] = name
        self.scope.examples.rename(self, name)
        return self.story_map.opened.save()

    def edit_description(self, description: str) -> "StoryMap":
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

    def __init__(self, name: str, sequential_order: int = 0, stories: Optional[List["Story"]] = None) -> None:
        super().__init__(name=name, sequential_order=sequential_order)
        self.parent: Optional["StoryMap"] = None
        self.outcome: str = ""
        self.slicing_notes: str = ""
        self.decision_prompt: str = ""
        self.source: Optional["Source"] = None
        self._stories = ModelReferences(self, "stories")
        self.stories = stories or []

    def _copy_fields(self, original: "Increment", copy_part: CopyPart) -> None:
        """Its fields, delivering the same stories; a map that copies its stories as well hands the copy those."""
        self.sequential_order, self.description_text, self.source = original.sequential_order, original.description_text, original.source
        self.outcome, self.slicing_notes, self.decision_prompt = original.outcome, original.slicing_notes, original.decision_prompt
        self.stories = list(original.stories)

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
    def add_story(self, story: "Story") -> "StoryMap":
        """Deliver story, a story of the same story map, in this increment, taking it off the increment that delivered
        it before; save the map and return it."""
        found = self.story_map.descendants.node_at(story.path)
        for increment in self.story_map.increments:
            increment.stories = [each for each in increment.stories if each is not found]
        self.stories = [*self.stories, found]
        return self.story_map.opened.save()

    @mcp
    @agent_tool
    def remove_story(self, story: "Story") -> "StoryMap":
        """Stop delivering story in this increment; the story stays on its story map. Save the map and return it."""
        found = self.story_map.descendants.node_at(story.path)
        self.stories = [each for each in self.stories if each is not found]
        return self.story_map.opened.save()


@language_adapter(language="typescript")
@agent_toolset
class Step(CodeHeld):
    _semantic_type_name = "Step"
    graph_facts = ("keyword", "text", "phase", "concepts", "values", "linked_terms", "actor", "continuation", "callees", "body_text", "realization_calls")

    def __init__(self, text: str, step_type: "StepType | None" = None, sequential_order: int = 0) -> None:
        """A step saying text, of step_type, at sequential_order. What a format reads about the step beyond that, its
        keyword, the concepts, values and actor its line names, and where it sits, is set on the step afterwards."""
        label = text.strip()[:_STEP_NAME_LENGTH] if text.strip() else f"step-{sequential_order}"
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

    def _copy_fields(self, original: "Step", copy_part: CopyPart) -> None:
        """Take what original says and was read with, its code, and each step chained onto it."""
        self.name, self.text, self.step_type = original.name, original.text, original.step_type
        self.sequential_order, self._keyword = original.sequential_order, original._keyword
        self.concepts, self.values = list(original.concepts), list(original.values)
        self.linked_terms = list(original.linked_terms)
        self.actor, self.source = original.actor, original.source
        self.call_graph = CallGraph(getattr(original, "call_graph", None) or [])
        self.take_code_from(original)
        self.ands = [copy_part(extra, type(self)) for extra in original.ands]

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
    def edit_text(self, text: str) -> "StoryMap":
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

    def read_code(self, block: "StoryBlock") -> None:
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
    def realization_calls(self) -> List[str]:
        """The calls its realization's call graph names, at every depth, each once and as written (``Cart.addBook(book,
        1)``); a return line (``<- CartLine``) is no call. It saves with the graph, so the step is linked to the model
        operations its realization names whichever process holds the graph."""
        found: List[str] = []
        for entry in self.call_graph:
            if entry.kind in ("call", "out") and entry.text not in found:
                found.append(entry.text)
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


def _steps_key(steps: List["Step"]) -> tuple:
    return tuple(line.code_key for step in steps for line in (step, *step.ands))


class Background(CodeHeld):
    _semantic_type_name = "Background"
    step_class = Step
    """The step class this format's backgrounds are made of; a background copied into this format makes its steps of
    it."""

    def __init__(self, name: str = "background", sequential_order: int = 1) -> None:
        super().__init__(name=name, sequential_order=sequential_order)
        self._steps = ModelChildren(self, "steps")
        self.examples = Examples(self)

    def _copy_fields(self, original: "Background", copy_part: CopyPart) -> None:
        self.sequential_order = original.sequential_order
        self.steps = [copy_part(step, type(self).step_class) for step in original.steps]
        self.examples = original.examples.clone(self)
        self.take_code_from(original)

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


class StepType(str, Enum):
    """Given, When, or Then. A step's list is this type."""

    GIVEN = "given"
    WHEN = "when"
    THEN = "then"


@language_adapter(language="typescript")
@agent_toolset
class Scenario(CodeHeld):
    """Behaviour walk-through under a story.

    Tree children: Background, Step, Example.
    """

    _semantic_type_name = "Scenario"
    step_class = Step
    background_class = Background
    """The step and background classes this format's scenarios are made of; a scenario copied into this format makes
    its parts of them."""

    def __init__(self, name: str = "", sequential_order: int = 0) -> None:
        super().__init__(name=name, sequential_order=sequential_order)
        self._backgrounds = ModelChildren(self, "background")
        self._steps = ModelChildren(self, "steps")
        self.examples = Examples(self)
        self.is_outline: bool = False
        self.evidence: List[str] = []
        self.source: Optional["Source"] = None

    def _copy_fields(self, original: "Scenario", copy_part: CopyPart) -> None:
        self.sequential_order, self.is_outline = original.sequential_order, original.is_outline
        self.evidence, self.source = list(original.evidence), original.source
        self.backgrounds = [copy_part(background, type(self).background_class) for background in original.backgrounds]
        self.steps = [copy_part(step, type(self).step_class) for step in original.steps]
        self.examples = original.examples.clone(self)
        self.take_code_from(original)

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
    def new_step(self, step_type: str, text: str) -> "StoryMap":
        """Add a step saying text, of step_type (given, when or then), after this scenario's steps; save its story map
        and return it."""
        self.steps.append(type(self).step_class(text, StepType(step_type), len(self.steps) + 1))
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
        """A scenario is sized by its steps, against no band."""
        facts = self._name_facts()
        facts.count(len(self.steps), label="steps")
        self.set_facts(facts.facts)

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


# The fact a story's graph node carries when a scenarios file specifies it and the story map does not hold it.
NOT_ON_STORY_MAP = "not_on_story_map"


@language_adapter(language="typescript")
@agent_toolset
class Story(CodeHeld):
    _semantic_type_name = "Story"
    scenario_class = Scenario
    background_class = Background
    """The scenario and background classes this format's stories are made of; a story copied into this format makes
    its parts of them."""

    def __init__(self, name: str, sequential_order: int = 0, story_type: StoryType = StoryType.USER):
        super().__init__(name, sequential_order)
        self.story_type = story_type
        self.actors: List[str] = []
        self.domain_terms: List[str] = []
        self.evidence: List[str] = []
        self._backgrounds = ModelChildren(self, "background")
        self._scenarios = ModelChildren(self, "scenarios")

    def _copy_fields(self, original: "Story", copy_part: CopyPart) -> None:
        self.sequential_order, self.story_type = original.sequential_order, original.story_type
        self.actors, self.domain_terms, self.evidence = list(original.actors), list(original.domain_terms), list(original.evidence)
        self.description_text = original.description_text
        self.backgrounds = [copy_part(background, type(self).background_class) for background in original.backgrounds]
        self.scenarios = [copy_part(scenario, type(self).scenario_class) for scenario in original.scenarios]
        self.take_code_from(original)

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
    def new_scenario(self, name: str) -> "StoryMap":
        """Add a scenario called name after this story's scenarios; save its story map and return it."""
        self.scenarios.append(type(self).scenario_class(name, len(self.scenarios) + 1))
        return self.story_map.opened.save()

    def load_map_facts(self) -> None:
        """A story is sized by its scenarios, against no band; its name may hide a generic handler or repeat a later
        sibling's."""
        self.scenario_count = len(self.scenarios)
        facts = self._name_facts()
        facts.count(self.scenario_count, label="scenarios")
        facts.judge(facts.opens_with_generic_handler, self._repeats_later_sibling())
        self.set_facts(facts.facts)

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


@language_adapter(language="typescript")
@agent_toolset
class Epic(CodeHeld):
    """An epic. A nested epic is an epic whose parent is an epic."""

    _semantic_type_name = "Epic"
    story_class = Story
    """The story class this format's epics hold; an epic copied into this format makes its stories of it, and its
    story map makes a new story of it."""

    def __init__(self, name: str, sequential_order: int = 0):
        super().__init__(name, sequential_order)
        self._epics = ModelChildren(self, "decomposedInto")
        self._stories = ModelChildren(self, "decomposedInto")
        self.examples = Examples(self)
        self.descendants = Descendants(self)

    def _copy_fields(self, original: "Epic", copy_part: CopyPart) -> None:
        self.sequential_order, self.estimate = original.sequential_order, original.estimate or ""
        self.description_text = original.description_text
        self.epics = [copy_part(child, type(self)) for child in original.epics]
        self.stories = [copy_part(story, type(self).story_class) for story in original.stories]
        self.examples = original.examples.clone(self)
        self.take_code_from(original)

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
    def new_epic(self, name: str) -> "StoryMap":
        """Add a sub-epic called name after this epic's sub-epics; save its story map and return it."""
        self.epics.append(type(self)(name, len(self.epics) + 1))
        return self.story_map.opened.save()

    @mcp
    @agent_tool
    def new_story(self, name: str) -> "StoryMap":
        """Add a story called name after this epic's stories; save its story map and return it."""
        self.stories.append(self.story_map.story_class(name, len(self.stories) + 1))
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

    def load_map_facts(self) -> None:
        """An epic is sized by its sub-epics and stories, against the band of its layer, and may name the verb all its
        stories open with."""
        facts = self._name_facts()
        facts.count(len(self.epics) + len(self.stories), self._child_band_for_layer())
        facts.judge(shared_verb=self._shared_opening())
        self.set_facts(facts.facts)

    def _child_band_for_layer(self) -> ChildBand:
        """The band this node's children fit, by the layer it is (`child-count-fits-layer`, ``LAYER_BANDS``)."""
        if self.epics:
            return LAYER_BANDS.holding_sub_epics
        return LAYER_BANDS.sub_epic if self.is_sub_epic else LAYER_BANDS.flat_epic

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

    def leaf_epics(self) -> List["Epic"]:
        """The epics whose stories sit in columns under this epic: its innermost sub-epics, or itself when it has none."""
        if not self.epics:
            return [self]
        return [leaf for child in self.epics for leaf in child.leaf_epics()]


@identity("file")
@language_adapter(language="typescript")
@agent_toolset
class StoryMap(StoryNode, FormatAdapter):
    """A story map: its epics, and the increments that deliver its stories. One opened in a session through its tools
    (``load``) holds the file it was read from (an *OpenedStoryMap*) and saves itself there after every edit."""

    # A story map opened in a session writes only its own file and the formats chosen beside it, under the session's
    # roots.

    _semantic_type_name = "StoryMap"
    epic_class = Epic
    """The epic class this format's maps are made of; a map copied into this format makes its epics of it."""
    increment_class = Increment
    """The increment class this format's maps are sliced by."""

    def __init__(self, graph: Optional[Graph] = None) -> None:
        super().__init__(name="StoryMap", sequential_order=0, graph=graph)
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

    @property
    def story_class(self) -> type:
        """The story class this format's maps hold: the one its epics hold."""
        return self.epic_class.story_class

    def blank(self) -> "StoryMap":
        """A map of this format holding nothing, made with this map's settings, such as a code map's tests root."""
        return type(self)()

    def copy_of(self, source: "StoryMap") -> "StoryMap":
        """source copied into this format's node classes, with this map's settings, so this format's nodes write it. It
        is asked of a map, not its class, because a code format copies with its own settings."""
        copy = self.blank()
        copy._copy_fields(source, _as_part_class)
        return copy

    def clone(self) -> "StoryMap":
        """A copy of this map with its settings, each epic and increment a clone keeping the class it has."""
        copy = self.blank()
        copy._copy_fields(self, _as_own_class)
        return copy

    def _copy_fields(self, original: "StoryMap", copy_part: CopyPart) -> None:
        """Take original's description and examples, its epics as copy_part copies them, and its increments, each
        delivering the copies of the stories it delivered."""
        self.description_text = original.description_text
        self.examples = original.examples.clone(self)
        for epic in original.epics:
            self.epics.append(copy_part(epic, self.epic_class))
        StoryCopies(original, self).copy_increments(lambda increment: copy_part(increment, self.increment_class))

    def placed_in(self, file: str, text: str) -> "StoryMap":
        """This map, read from text, the file called file: it keeps the text as one of its sources, and each epic and
        everything under it names the file."""
        self.sources.add(file, text)
        self.descendants.place_in(file)
        return self

    def opened_from(self, path: Path, project: Path) -> "StoryMap":
        """The story map an edit to the file at path writes back, each node naming the file from project: the file
        read by this format."""
        return self.read_file(path, project)
    @classmethod
    @tool_subject
    def load(cls, file: str, *, call: ToolCall) -> "StoryMap":
        """The story map in file, a Stories file named from the project: a story map, a scenario file, or a story test
        merged onto its story map, read by the Stories practice of the session the call works in. A file outside the
        session's roots is refused (PathOutsideRootsError)."""
        session = call.session
        path = session.paths.path_named(file)
        files = session.session_files.file_manager
        files.read(os.path.relpath(path, files.workpath))
        stories = session.graph.practices.of(cls.practice_class)
        model = stories.story_files(session.checkout.root).opened(path)
        model.opened = OpenedStoryMap(model, path, session)
        return model

    @classmethod
    @mcp
    @agent_tool
    def open_in_session(cls, *, call: ToolCall) -> "StoryMap":
        """Return the story map of the session open in the project: the first story map file its Stories practice
        declares there, so a page that follows the open session shows the ticket activated last."""
        stories = call.session.graph.practices.of(cls.practice_class)
        story_map = next(iter(stories.fidelities))
        made = [entry.path for entries in story_map.session_output.written.files().values() for entry in entries if entry.exists]
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
    def show(self) -> "StoryMap":
        """Return the story map as its file holds it now, with the formats chosen for its fidelity and, when an edit
        would not be saved, why."""
        return self

    @mcp
    @agent_tool
    def new_epic(self, name: str) -> "StoryMap":
        """Add an epic called name after the map's epics; save the map and return it."""
        self.epics.append(self.epic_class(name, len(self.epics) + 1))
        return self.opened.save()

    @mcp
    @agent_tool
    def new_increment(self, name: str) -> "StoryMap":
        """Add an increment called name after the map's increments, delivering no story yet; save the map and return
        it. A map that keeps no increments, such as a scenario file, refuses it with StoryMapEditRefused."""
        if self.slicing is None:
            raise StoryMapEditRefused(self, "new_increment", f"{self.file} keeps no increments")
        self.increments.append(self.increment_class(name, len(self.increments) + 1))
        return self.opened.save()

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


class NumberedChildren(ModelChildren):
    """The epics or increments of a story map, numbered in the order they stand: one appended takes the next number."""

    def append(self, held: StoryNode) -> None:
        super().append(held)
        _renumber(self)


class Descendants:
    """The epics and stories under an epic or a story map, at any depth, in map order, and the node a path names
    among them: what a story map is searched and placed by."""

    def __init__(self, holder: "Epic | StoryMap") -> None:
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


class StoryTestScenarios:
    """The scenarios a story map's stories take from the story tests that specify them. A story test names the Story
    it specifies, and the markdown and the drawio of one story map each hold that Story, so every Story of that name
    takes its scenarios. A Story the map does not have takes nothing."""

    def __init__(self, story_map: "StoryMap") -> None:
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
