"""StoryTree. The story map as the graph holds it, which every reader of Stories' nodes asks, in this practice or another:
the one definition of which node types are steps and epics, how a node is keyed, and which node a file's heading names."""

from __future__ import annotations

from functools import cached_property
from pathlib import Path
from typing import TYPE_CHECKING, Optional, Sequence

from harness.markdown.markdown import MarkdownText

if TYPE_CHECKING:
    from harness.graph.graph import Graph, Node
    from harness.graph.practice_reading import PracticeReading

STEP_TYPES = ("Step", "Given", "When", "Then")
"""The node types the Stories graph records a step as: it types each step by its phase."""
EPIC_TYPES = ("Epic", "SubEpic")
"""The node types of the story map's epics: an Epic, and a SubEpic under another epic."""
KEY_SEPARATOR = " › "
"""What parts a story's name from its scenario's, and a scenario's from its step's, in a key."""
EXAMPLE_TYPE = "Example"
"""The node type of a story's example: a fixture a scenario uses, declared in the story test or in an examples module."""
LINKED_TYPES = {"Story": ("Story",), "Scenario": ("Scenario", "Background"), "Step": STEP_TYPES}
"""The Stories node types a link of each kind can name; a background is a scenario a story runs first."""
STORY_MAP_TYPES = frozenset({*EPIC_TYPES, "Story", "Scenario", "Background", EXAMPLE_TYPE, *STEP_TYPES})
"""Every node type of the story map itself, as opposed to the test files a pattern reads into the practice."""
_ANCHOR_MARK = "#"


class StoryTree:
    """The story map as the graph holds it: each epic's sub-epics and stories, each story's scenarios, each scenario's
    steps, and the epic, story, scenario, or area above any of them, read through the edges Stories records and the facts
    each node saves. It answers the same for the objects a read parsed and for the plain nodes of a graph opened from its
    save, so every reader of Stories' nodes, in this practice or another, asks it rather than a parsed object's
    attributes."""

    def __init__(self, stories: PracticeReading) -> None:
        self.stories = stories

    @staticmethod
    def of_graph(graph: Graph) -> Optional["StoryTree"]:
        """The story tree of the Stories practice graph reads; none while it reads no Stories."""
        from cdd_guidance.practices.stories.model.story_map import StoryNode

        # The practice names itself on its model when its module is imported, so the model never imports it back.
        stories = graph.practices.loaded(StoryNode.practice_class)
        return stories.reading.story_tree if stories is not None else None

    @property
    def _edges(self):
        return self.stories.graph.edges

    ## the map, top down

    def epic_of(self, node: Node) -> Optional[Node]:
        """The epic of the story map whose tree holds node, the outermost found up the graph's own edges; none for a
        node under no epic."""
        epic = None
        above = self._edges.direct_parent(node)
        while above is not None:
            epic = above if self.is_epic(above) else epic
            above = self._edges.direct_parent(above)
        return epic

    def sub_epics(self, epic: Node) -> list[Node]:
        """The sub-epics directly under epic, in the order the map lists them."""
        return self._below(epic, "decomposedInto", EPIC_TYPES)

    def stories_under(self, epic: Node) -> list[Node]:
        """The stories directly under epic or a sub-epic, in the order the map lists them."""
        return self._below(epic, "decomposedInto", ("Story",))

    def scenarios(self, story: Node) -> list[Node]:
        """The story's scenarios, in the order its story test or map lists them."""
        return self._below(story, "scenarios", ("Scenario",))

    def steps(self, scenario: Node) -> list[Node]:
        """The scenario's own steps, without the steps chained onto them, in order."""
        return [edge.child for edge in self._edges.from_parent("steps", scenario)]

    def every_step(self) -> list[Node]:
        """Every step the Stories graph holds, a Given, When, Then, or plain Step, with the steps chained onto them."""
        return [node for node in self.stories.in_graph.nodes() if self.is_step(node)]

    def examples(self) -> list[Node]:
        """Every example the Stories graph holds."""
        return self.stories.in_graph.nodes("Example")

    def examples_by_file(self) -> dict[str, list[Node]]:
        """The examples by the story file each is recorded for: a step means its own file's."""
        by_file: dict[str, list[Node]] = {}
        for example in self.examples():
            by_file.setdefault(example.source.file, []).append(example)
        return by_file

    ## the map, bottom up

    def scenario_of(self, step: Node) -> Optional[Node]:
        """The scenario step sits in, found up the graph's own edges; none for a step outside one."""
        return self._above(step, ("Scenario",))

    def story_of(self, node: Node) -> Optional[Node]:
        """The story node sits under, found up the graph's own edges; none for a node under no story."""
        return self._above(node, ("Story",))

    def background_steps(self, story: Optional[Node]) -> list[Node]:
        """The steps of story's Background; none for a story that writes none."""
        if story is None:
            return []
        return [step for background in self._below(story, "background", ("Background",)) for step in self.steps(background)]

    def area_of(self, node: Node) -> Node:
        """The nearest sub-epic or epic above node; for a node under none, the topmost node above it, its story."""
        above = node
        while not self.is_epic(above):
            parent = self._edges.direct_parent(above)
            if parent is None:
                return above
            above = parent
        return above

    ## a step

    def is_step(self, node: Node) -> bool:
        """Whether node is a step, recorded as the Given, When, or Then it is, or as a Step with none of them."""
        return node.type in STEP_TYPES

    def is_epic(self, node: Node) -> bool:
        """Whether node is an epic of the story map, recorded as an Epic, or as a SubEpic under another epic."""
        return node.type in EPIC_TYPES

    def step_text(self, step: Node) -> str:
        """The step's words after its keyword."""
        return str(step.get_fact("text") or step.name)

    def step_phase(self, step: Node) -> str:
        """given, when, or then; an And or But line carries the phase of the line it continues."""
        return str(step.get_fact("phase") or "")

    def step_body(self, step: Node) -> str:
        """The step's own text and the body its story test gives it."""
        return f"{step.name}\n{step.get_fact('body_text') or ''}"

    def steps_saying(self, text: str) -> list[Node]:
        """Every step whose words are text."""
        return [step for step in self.every_step() if self.step_text(step) == text]

    ## how a node is named elsewhere

    @staticmethod
    def key_of(node: Node) -> str:
        """The key another practice lists a Stories node by: the story's name, then its scenario's, then the step's
        text. It reads the node's type, its saved facts, and the edges of the node's own graph, so a Stories node read
        back from a saved graph, or drawn on another graph, has the key the story object it was read from has."""
        if node.type == "Story":
            return node.name
        if node.type in STEP_TYPES:
            scenario = _ancestor(node, LINKED_TYPES["Scenario"])
            parts = [_story_name(scenario), scenario.name if scenario is not None else "", node.get_fact("text") or node.name]
        else:
            parts = [_story_name(node), node.name]
        return KEY_SEPARATOR.join(part for part in parts if part)

    def nodes_keyed(self, kind: str, key: str) -> list[Node]:
        """The Stories nodes of a link of kind whose key is key."""
        return [node for node_type in LINKED_TYPES[kind] for node in self.stories.in_graph.nodes(node_type) if self.key_of(node) == key]

    def written_nodes(self) -> "WrittenStoryNodes":
        """The Stories nodes by the file each was read from, read now, for a run of links that each name a file and a
        heading: keep it for the run, since the map does not change during it."""
        return WrittenStoryNodes(self)

    def _below(self, parent: Node, kind: str, node_types: Sequence[str]) -> list[Node]:
        return [edge.child for edge in self._edges.from_parent(kind, parent) if edge.child.type in node_types]

    def _above(self, node: Node, node_types: Sequence[str]) -> Optional[Node]:
        above = self._edges.direct_parent(node)
        while above is not None and above.type not in node_types:
            above = self._edges.direct_parent(above)
        return above


class WrittenStoryNodes:
    """The Stories nodes of one graph by the file each was read from, so a link written as a file and a heading leads to
    the node written there: the node read from the heading the link names (for a story read from the story map, the
    heading of its story file names it too, through the scenarios read under that heading), or, for a link that names a
    file alone, the node of that file with the link's key. A file Stories did not read and a heading no node was read
    from lead to no node; neither is an error."""

    def __init__(self, tree: StoryTree) -> None:
        self._tree = tree
        self._documents: dict[Path, MarkdownText] = {}

    def node_written_at(self, kind: str, target: str, key: str, written_in: Sequence[Path] = ()) -> Optional[Node]:
        """The one Stories node of kind that target, a file and an optional ``#heading``, names, its path taken from
        each folder of written_in in turn, then from the folders the graph reads; none when it names no node, or more
        than one."""
        path, _mark, heading = target.partition(_ANCHOR_MARK)
        file = self._file_named(path, written_in)
        if file is None:
            return None
        nodes = self._nodes_by_file[file]
        if not heading:
            found = [node for node in nodes if node.type in LINKED_TYPES[kind] and StoryTree.key_of(node) == key]
        else:
            lines = self._document(file).anchored_lines(heading)
            found = self._under_heading(kind, key, nodes, lines) if lines is not None else []
        return found[0] if len(found) == 1 else None

    def _file_named(self, path: str, written_in: Sequence[Path]) -> Optional[Path]:
        named = ((folder / path).resolve() for folder in [*written_in, *self._read_folders])
        return next((file for file in named if file in self._nodes_by_file), None)

    def _under_heading(self, kind: str, key: str, nodes: list[Node], lines: tuple[int, int]) -> list[Node]:
        """The nodes of kind read from the heading whose section is on lines: the story or scenario written at it, or,
        for a step, the step with the key's text under the story or scenario written at it."""
        headed = [node for node in nodes if node.source.start_line == lines[0]]
        if kind == "Story":
            return [node for node in headed if node.type == "Story"] or self._stories_written_in(nodes, lines)
        if kind != "Step":
            return [node for node in headed if node.type in LINKED_TYPES[kind]]
        text = key.split(KEY_SEPARATOR)[-1]
        steps = [node for node in nodes if node.type in STEP_TYPES and (node.get_fact("text") or node.name) == text]
        return [step for step in steps if any(_is_under(step, heading) for heading in headed)]

    def _stories_written_in(self, nodes: list[Node], lines: tuple[int, int]) -> list[Node]:
        """The stories whose scenarios are read from the section on lines: a story is read from the story map, and the
        heading of its story file holds its scenarios, so a link to that heading names the story they belong to."""
        within = [node for node in nodes if lines[0] <= node.source.start_line <= lines[1]]
        stories = {id(story): story for story in (_ancestor(node, ("Story",)) for node in within) if story is not None}
        return list(stories.values())

    def _document(self, file: Path) -> MarkdownText:
        if file not in self._documents:
            self._documents[file] = MarkdownText(file.read_text(encoding="utf-8"))
        return self._documents[file]

    @cached_property
    def _read_folders(self) -> list[Path]:
        """The folders a link's path is taken from when the file it is written in gives none: the folder the graph
        reads, then the folder Stories reads."""
        folders = [self._tree.stories.graph.scope.folder, self._tree.stories.in_graph.source_root]
        return [Path(folder).resolve() for folder in folders if folder]

    @cached_property
    def _nodes_by_file(self) -> dict[Path, list[Node]]:
        root = Path(self._tree.stories.in_graph.source_root).resolve()
        by_file: dict[Path, list[Node]] = {}
        for node in self._tree.stories.in_graph.nodes():
            if node.source is not None and node.source.file:
                by_file.setdefault((root / node.source.file).resolve(), []).append(node)
        return by_file


def _story_name(node: Optional[Node]) -> str:
    story = _ancestor(node, ("Story",)) if node is not None else None
    return story.name if story is not None else ""


def _ancestor(node: Node, kinds: Sequence[str]) -> Optional[Node]:
    current = _parent(node)
    while current is not None and current.type not in kinds:
        current = _parent(current)
    return current


def _is_under(node: Node, heading: Node) -> bool:
    above = _parent(node)
    while above is not None and above is not heading:
        above = _parent(above)
    return above is heading


def _parent(node: Node) -> Optional[Node]:
    """The node above node: the parent its tree gives it, else the one a direct edge of its graph hangs it under."""
    if node.parent is not None:
        return node.parent
    return node.graph.edges.direct_parent(node) if node.practice is not None else None
