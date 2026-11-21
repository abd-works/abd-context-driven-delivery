"""TermLinks. The domain terms the steps of the Stories graph link to the domain model, as edges to the model's nodes."""

from __future__ import annotations

import posixpath
import re
from functools import cached_property
from pathlib import Path
from typing import TYPE_CHECKING

from harness.guidance.practice_reading import PracticeReading
from harness.markdown.markdown import MarkdownText

if TYPE_CHECKING:
    from harness.graph.graph import Node

    from cdd_guidance.practices.stories.model.graph_reading import StoryTree

# A term linked to a heading of a model document, `[Cart](../.context/domain-model.md#cart-aggregate-root-entity)`, and
# the words written after it up to the next link, where the example of that term is named (`++Tiny Tales++`).
_TERM_LINK = re.compile(r"\[(?P<term>[^\]\n]+)\]\((?P<file>[^)\s#]+\.md)#(?P<anchor>[^)\s]+)\)(?P<after>[^\[\n]*)")
# What stands between a linked term and the example named after it: the underline marks around each, and spaces.
_BEFORE_EXAMPLE = "+ "


class TermLinks:
    """The edges from the steps of the Stories practice to the domain model: a step ``names`` the class each of its
    links names, which is ``namedBy`` the step, and an example written straight after a linked term ``demonstrates``
    that class, of the examples its own story file holds. A link is followed to the node its target names: the model document at the link's path, taken from the
    step's own file, and the node read from the heading with the link's anchor. A term is never matched to a class by
    its name, so a class of the same name in another document, or in code, gets no edge. Each link is read from the
    step's name and the lines of its file, which any process holding the graph can read."""

    def __init__(self, stories: PracticeReading, model: PracticeReading, tree: "StoryTree") -> None:
        self.stories = stories
        self.model = model
        self.tree = tree
        self.graph = stories.graph
        self._heading_lines: dict[Path, MarkdownText | None] = {}

    def link(self) -> None:
        for step in self.tree.all_steps():
            self._link_step(step)

    def _link_step(self, step: "Node") -> None:
        examples = self._examples_by_file.get(step.source.file, [])
        for found in _TERM_LINK.finditer(f"{step.name}\n{step.source.text}"):
            for named in self._nodes_at(self._target(step, found.group("file")), found.group("anchor")):
                self.graph.edges.relate("names", step, named)
                self.graph.edges.relate("namedBy", named, step)
                for example in self._named_after(found.group("after"), examples):
                    self.graph.edges.group("demonstrates", example, named)
                    self.graph.edges.relate("demonstratedThrough", named, example)

    def _target(self, step: "Node", linked_file: str) -> Path:
        """The file a link in step's file names, the link's path taken from the folder of that file."""
        folder = posixpath.dirname(step.source.file or "")
        return (self._stories_root / posixpath.normpath(posixpath.join(folder, linked_file))).resolve()

    def _nodes_at(self, document: Path, anchor: str) -> list["Node"]:
        """The model's nodes read from the heading of document that anchor names; none when the document has no such
        heading, or the model read no node from it."""
        text = self._document(document)
        lines = text.anchored_lines(anchor) if text is not None else None
        if lines is None:
            return []
        return [node for node in self._nodes_by_file.get(document, []) if node.source.start_line == lines[0]]

    def _document(self, document: Path) -> MarkdownText | None:
        """The model document at document, read once; none when it is not there."""
        if document not in self._heading_lines:
            self._heading_lines[document] = MarkdownText(document.read_text(encoding="utf-8")) if document.is_file() else None
        return self._heading_lines[document]

    def _named_after(self, after: str, examples: list["Node"]) -> list["Node"]:
        """The examples among examples whose name is written straight after a linked term, as words or as the name
        code gives it (``paid order`` for ``paid_order``)."""
        words = after.lstrip(_BEFORE_EXAMPLE).casefold()
        return [example for example in examples if words.startswith(example.name.replace("_", " ").casefold())]

    @cached_property
    def _examples_by_file(self) -> dict[str, list["Node"]]:
        """The examples of the Stories graph by the story file each is recorded for: a step means its own file's."""
        by_file: dict[str, list["Node"]] = {}
        for example in self.stories.in_graph.nodes("Example"):
            by_file.setdefault(example.source.file, []).append(example)
        return by_file

    @cached_property
    def _nodes_by_file(self) -> dict[Path, list["Node"]]:
        """The model's nodes by the file each was read from."""
        root = Path(self.model.in_graph.source_root).resolve()
        by_file: dict[Path, list["Node"]] = {}
        for node in self.model.in_graph.nodes():
            if node.source is not None and node.source.file:
                by_file.setdefault((root / node.source.file).resolve(), []).append(node)
        return by_file

    @cached_property
    def _stories_root(self) -> Path:
        return Path(self.stories.in_graph.source_root).resolve()
