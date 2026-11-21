"""StoryLink - a story, scenario, or step a screen shows."""

from __future__ import annotations

import re
from functools import cached_property
from pathlib import Path
from typing import Iterator, Optional, Sequence, Union

from harness.graph.graph import Graph, Node
from harness.markdown.markdown import MarkdownText

KEY_SEPARATOR = " › "
# An association written as a markdown link: its key as the link's text, and the file and heading it is written at.
_WRITTEN_LINK = re.compile(r"^\[(?P<key>[^\]]+)\]\((?P<target>[^)\s]+)\)$")
# What parts a link target's file from the heading it names in that file.
_ANCHOR_MARK = "#"

# The node types the Stories graph records a step as: it types each step by its phase.
STEP_TYPES = ("Step", "Given", "When", "Then")
# The Stories node types a link of each kind can hold; a background is a scenario a story runs first.
_NODE_TYPES = {
    "Story": ("Story",),
    "Scenario": ("Scenario", "Background"),
    "Step": STEP_TYPES,
}


class StoryLink:
    """A story, scenario, or step a screen or a control serves.

    Once that Stories node is on the graph of the screen or control the link holds the node itself, so a story renamed
    after it is linked keeps its screens and the formats write its new name. Until then the link holds what the
    formats store: the key (a story by its name, a scenario as ``Story › Scenario``, a step as
    ``Story › Scenario › Step``) and, when the association was written as a markdown link, its target: the file the
    story is written in, with the heading of the story or scenario after ``#`` when the file has one. A link with a
    target is followed to that file, never matched by its key alone.
    """

    def __init__(self, kind: str, key: str = "", node: Optional[Node] = None) -> None:
        self.kind = kind
        self._key = key
        self.node = node
        # The file and heading the association was written with as a markdown link; none for one written by its key.
        self.target = ""

    @classmethod
    def from_shown(cls, kind: str, shown: Union[Node, str]) -> "StoryLink":
        """A link to the Stories node a screen or control serves, or to what a format read for it: its key, or a
        markdown link whose text is the key."""
        if not isinstance(shown, str):
            return cls(kind, node=shown)
        written = _WRITTEN_LINK.match(shown.strip())
        if written is None:
            return cls(kind, key=shown)
        link = cls(kind, key=written.group("key").strip())
        link.target = written.group("target")
        return link

    @property
    def key(self) -> str:
        return key_of(self.node) if self.node is not None else self._key

    @property
    def written(self) -> str:
        """The link as the formats write it: a markdown link to its target when it has one, else its key."""
        return f"[{self.key}]({self.target})" if self.target else self.key

    def resolved_on(self, graph: Graph, written_in: Sequence[Path] = ()) -> Optional[Node]:
        """The node this link names on graph; the first node found is held from then on. A link with a target names
        the node read from that file, the target's path taken from each folder of written_in in turn, then from the
        folders the graph reads; a link with none names the node with its key."""
        if self.node is None and self.target:
            self.node = StoryTargets(graph).node_at(self, written_in)
        elif self.node is None:
            self.node = next((node for node in self._candidates(graph) if key_of(node) == self._key), None)
        return self.node

    def names(self, node: Node) -> bool:
        """True when this link holds node, or names a node with node's key, such as a copy drawn on another graph."""
        return node is self.node or (node.type in _NODE_TYPES[self.kind] and key_of(node) == self.key)

    def _candidates(self, graph: Graph) -> Iterator[Node]:
        """The Stories nodes of this link's kind on graph; none while graph reads no Stories."""
        from cdd_guidance.practices.stories.stories import Stories

        stories = graph.practices.loaded(Stories)
        if stories is None:
            return
        for node_type in _NODE_TYPES[self.kind]:
            yield from stories.reading.in_graph.nodes(node_type)


class StoryTargets:
    """The Stories nodes of one graph by the file each was read from, so a link's target leads to the node written at
    it: the node read from the heading the target names (for a story read from the story map, the heading of its story
    file names it too, through the scenarios read under that heading), or, for a target that names a file alone, the
    node of that file with the link's key. A graph that reads no Stories, a file Stories did not read, and a heading no node was
    read from all lead to no node; none of them is an error."""

    def __init__(self, graph: Graph) -> None:
        self._graph = graph
        self._documents: dict[Path, MarkdownText] = {}

    def node_at(self, link: StoryLink, written_in: Sequence[Path] = ()) -> Optional[Node]:
        """The one Stories node link's target names; none when the target names no node, or more than one."""
        path, _mark, anchor = link.target.partition(_ANCHOR_MARK)
        file = self._file_named(path, written_in)
        if file is None:
            return None
        nodes = self._nodes_by_file[file]
        if not anchor:
            found = self._with_key(link, nodes)
        else:
            lines = self._document(file).anchored_lines(anchor)
            found = self._under_heading(link, nodes, lines) if lines is not None else []
        return found[0] if len(found) == 1 else None

    def _file_named(self, path: str, written_in: Sequence[Path]) -> Optional[Path]:
        """The file Stories read that path names, taken from each folder in turn."""
        named = ((folder / path).resolve() for folder in [*written_in, *self._read_folders])
        return next((file for file in named if file in self._nodes_by_file), None)

    def _with_key(self, link: StoryLink, nodes: list[Node]) -> list[Node]:
        return [node for node in nodes if node.type in _NODE_TYPES[link.kind] and key_of(node) == link.key]

    def _under_heading(self, link: StoryLink, nodes: list[Node], lines: tuple[int, int]) -> list[Node]:
        """The nodes of link's kind read from the heading whose section is on lines: the story or scenario written at
        it, or, for a step, the step with the link's text under the story or scenario written at it."""
        headed = [node for node in nodes if node.source.start_line == lines[0]]
        if link.kind == "Story":
            return [node for node in headed if node.type == "Story"] or self._stories_written_in(nodes, lines)
        if link.kind != "Step":
            return [node for node in headed if node.type in _NODE_TYPES[link.kind]]
        text = link.key.split(KEY_SEPARATOR)[-1]
        steps = [node for node in nodes if node.type in _NODE_TYPES["Step"] and (node.get_fact("text") or node.name) == text]
        return [step for step in steps if any(self._is_under(step, heading) for heading in headed)]

    def _stories_written_in(self, nodes: list[Node], lines: tuple[int, int]) -> list[Node]:
        """The stories whose scenarios are read from the section on lines: a story is read from the story map, and the
        heading of its story file holds its scenarios, so a link to that heading names the story they belong to."""
        within = [node for node in nodes if lines[0] <= node.source.start_line <= lines[1]]
        stories = {id(story): story for story in (_ancestor(node, ("Story",)) for node in within) if story is not None}
        return list(stories.values())

    def _is_under(self, node: Node, heading: Node) -> bool:
        above = _parent(node)
        while above is not None and above is not heading:
            above = _parent(above)
        return above is heading

    def _document(self, file: Path) -> MarkdownText:
        if file not in self._documents:
            self._documents[file] = MarkdownText(file.read_text(encoding="utf-8"))
        return self._documents[file]

    @cached_property
    def _stories_read(self):
        """What the graph read for Stories; none while it reads no Stories."""
        from cdd_guidance.practices.stories.stories import Stories

        stories = self._graph.practices.loaded(Stories)
        return stories.reading.in_graph if stories is not None else None

    @cached_property
    def _read_folders(self) -> list[Path]:
        """The folders a target's path is taken from when the file it is written in gives none: the folder the graph
        reads, then the folder Stories reads."""
        folders = [self._graph.scope.folder, self._stories_read.source_root if self._stories_read is not None else None]
        return [Path(folder).resolve() for folder in folders if folder]

    @cached_property
    def _nodes_by_file(self) -> dict[Path, list[Node]]:
        """The Stories nodes by the file each was read from; none while the graph reads no Stories."""
        if self._stories_read is None:
            return {}
        root = Path(self._stories_read.source_root).resolve()
        by_file: dict[Path, list[Node]] = {}
        for node in self._stories_read.nodes():
            if node.source is not None and node.source.file:
                by_file.setdefault((root / node.source.file).resolve(), []).append(node)
        return by_file


def key_of(node: Node) -> str:
    """The key a screen lists a Stories node by: the story's name, then its scenario's, then the step's text. It reads
    the node's type, its saved facts, and the graph's edges, so a Stories node read back from a saved graph has the key
    the story object it was read from has."""
    kind = node.type
    if kind in _NODE_TYPES["Step"]:
        scenario = _ancestor(node, _NODE_TYPES["Scenario"])
        parts = [_story_name(scenario), scenario.name if scenario is not None else "", node.get_fact("text") or node.name]
    elif kind == "Story":
        return node.name
    else:
        parts = [_story_name(node), node.name]
    return KEY_SEPARATOR.join(part for part in parts if part)


def _story_name(node: Optional[Node]) -> str:
    story = _ancestor(node, ("Story",)) if node is not None else None
    return story.name if story is not None else ""


def _ancestor(node: Node, kinds: tuple) -> Optional[Node]:
    current = _parent(node)
    while current is not None and current.type not in kinds:
        current = _parent(current)
    return current


def _parent(node: Node) -> Optional[Node]:
    """The node above node: the parent its tree gives it, else the one a direct edge of its graph hangs it under."""
    if node.parent is not None:
        return node.parent
    return node.graph.edges.direct_parent(node) if node.practice is not None else None
