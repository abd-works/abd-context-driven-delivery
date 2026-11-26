"""StoryLink - a story, scenario, or step a screen shows."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Optional, Sequence, Union

from harness.graph.graph import Node

from cdd_guidance.practices.stories.model.story_tree import LINKED_TYPES, StoryTree, WrittenStoryNodes

# An association written as a markdown link: its key as the link's text, and the file and heading it is written at.
_WRITTEN_LINK = re.compile(r"^\[(?P<key>[^\]]+)\]\((?P<target>[^)\s]+)\)$")


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
        return StoryTree.key_of(self.node) if self.node is not None else self._key

    @property
    def written(self) -> str:
        """The link as the formats write it: a markdown link to its target when it has one, else its key."""
        return f"[{self.key}]({self.target})" if self.target else self.key

    def resolved_in(self, story_tree: Optional[StoryTree], written_in: Sequence[Path] = ()) -> Optional[Node]:
        """The node this link names in story_tree; the first node found is held from then on. A link with a target names
        the node read from that file, the target's path taken from each folder of written_in in turn, then from the
        folders the graph reads; a link with none names the node with its key. A graph that reads no Stories (no
        story_tree) names none."""
        if self.node is None and story_tree is not None:
            self.node = self.found_in(story_tree.written_nodes(), story_tree, written_in)
        return self.node

    def found_in(self, written: WrittenStoryNodes, story_tree: StoryTree, written_in: Sequence[Path] = ()) -> Optional[Node]:
        """The node this link names, its target followed through written, the Stories nodes by the file each was read
        from, which a run of links shares; its key looked up in story_tree when it has no target."""
        if self.target:
            return written.node_written_at(self.kind, self.target, self.key, written_in)
        return next(iter(story_tree.nodes_keyed(self.kind, self._key)), None)

    def names(self, node: Node) -> bool:
        """True when this link holds node, or names a node with node's key, such as a copy drawn on another graph."""
        return node is self.node or (node.type in LINKED_TYPES[self.kind] and StoryTree.key_of(node) == self.key)
