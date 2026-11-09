"""StoryLink - a story, scenario, or step a screen shows."""

from __future__ import annotations

from typing import Iterator, Optional, Union

from harness.graph.graph import Graph, Node

KEY_SEPARATOR = " › "

# The Stories node types a link of each kind can hold; a background is a scenario a story runs first, and the Stories
# graph types each step by its phase.
_NODE_TYPES = {
    "Story": ("Story",),
    "Scenario": ("Scenario", "Background"),
    "Step": ("Step", "Given", "When", "Then"),
}


class StoryLink:
    """A story, scenario, or step a screen shows.

    Once that Stories node is on the screen's graph the link holds the node itself, so a story renamed after it is
    linked keeps its screens and the formats write its new name. Until then the link holds the key the formats
    store: a story by its name, a scenario as ``Story › Scenario``, a step as ``Story › Scenario › Step``.
    """

    def __init__(self, kind: str, key: str = "", node: Optional[Node] = None) -> None:
        self.kind = kind
        self._key = key
        self.node = node

    @classmethod
    def from_item(cls, kind: str, item: Union[Node, str]) -> "StoryLink":
        """A link to a Stories node, or to the key a format read."""
        if isinstance(item, str):
            return cls(kind, key=item)
        return cls(kind, node=item)

    @property
    def key(self) -> str:
        return key_of(self.node) if self.node is not None else self._key

    def resolved_on(self, graph: Graph) -> Optional[Node]:
        """The node this link names on graph; the first node found is held from then on."""
        if self.node is None:
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
    return node.graph.direct_parent(node) if node.practice is not None else None
