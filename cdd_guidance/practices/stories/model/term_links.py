"""TermLinks. The domain terms the steps of the Stories graph link to the domain model, as edges to the model's nodes;
and ModelHeadings, which follows a step's links to the nodes a model practice read from the headings they name."""

from __future__ import annotations

import posixpath
import re
from functools import cached_property
from pathlib import Path
from typing import TYPE_CHECKING, Iterator, NamedTuple

from harness.markdown.markdown import MarkdownText

if TYPE_CHECKING:
    from harness.graph.graph import Node
    from harness.graph.practice_reading import PracticeReading

    from cdd_guidance.practices.stories.model.story_tree import StoryTree

# A term linked to a heading of a model document, `[Cart](../.context/domain-model.md#cart-aggregate-root-entity)`, and
# the words written after it up to the next link, where the example of that term is named (`++Tiny Tales++`).
_TERM_LINK = re.compile(r"\[(?P<term>[^\]\n]+)\]\((?P<file>[^)\s#]+\.md)#(?P<anchor>[^)\s]+)\)(?P<after>[^\[\n]*)")
# What stands between a linked term and the example named after it: the underline marks around each, and spaces.
_BEFORE_EXAMPLE = "+ "


class TermLink(NamedTuple):
    """One domain term a step links to a heading of a model document: the document, the heading's anchor, and the words
    written after the link."""

    document: Path
    anchor: str
    after: str


class ModelHeadings:
    """The nodes one model practice read from its documents, found by the links a step writes to their headings. A link
    is followed to the node its target names: the model document at the link's path, taken from the step's own file,
    and the node read from the heading with the link's anchor. A term is never matched to a class by its name, so a
    class of the same name in another document, or in code, is not found. Each link is read from the step's name and
    the lines of its file, which any process holding the graph can read."""

    def __init__(self, stories_root: Path, model: PracticeReading) -> None:
        self._stories_root = stories_root.resolve()
        self._model = model
        self._heading_lines: dict[Path, MarkdownText | None] = {}

    def links_of(self, step: "Node") -> Iterator[TermLink]:
        """Each domain term step links to a heading of a model document, in the order it writes them."""
        for found in _TERM_LINK.finditer(f"{step.name}\n{step.source.text}"):
            yield TermLink(self._target(step, found.group("file")), found.group("anchor"), found.group("after"))

    def nodes_at(self, link: TermLink) -> list["Node"]:
        """The model's nodes read from the heading the link names; none when its document has no such heading, or the
        model read no node from it."""
        text = self._document(link.document)
        lines = text.anchored_lines(link.anchor) if text is not None else None
        if lines is None:
            return []
        return [node for node in self.nodes_in(link.document) if node.source.start_line == lines[0]]

    def nodes_in(self, document: Path) -> list["Node"]:
        """Every node the model read from document."""
        return self._nodes_by_file.get(document, [])

    def _target(self, step: "Node", linked_file: str) -> Path:
        """The file a link in step's file names, the link's path taken from the folder of that file."""
        folder = posixpath.dirname(step.source.file or "")
        return (self._stories_root / posixpath.normpath(posixpath.join(folder, linked_file))).resolve()

    def _document(self, document: Path) -> MarkdownText | None:
        """The model document at document, read once; none when it is not there."""
        if document not in self._heading_lines:
            self._heading_lines[document] = MarkdownText(document.read_text(encoding="utf-8")) if document.is_file() else None
        return self._heading_lines[document]

    @cached_property
    def _nodes_by_file(self) -> dict[Path, list["Node"]]:
        """The model's nodes by the file each was read from."""
        root = Path(self._model.in_graph.source_root).resolve()
        by_file: dict[Path, list["Node"]] = {}
        for node in self._model.in_graph.nodes():
            if node.source is not None and node.source.file:
                by_file.setdefault((root / node.source.file).resolve(), []).append(node)
        return by_file


class TermLinks:
    """The edges from the steps of the Stories practice to the domain model: a step ``names`` the class each of its
    links names (*ModelHeadings*), which is ``namedBy`` the step, and an example written straight after a linked term
    ``demonstrates`` that class, of the examples its own story file holds."""

    def __init__(self, tree: StoryTree, model: PracticeReading) -> None:
        self.tree = tree
        self.graph = tree.stories.graph
        self.headings = ModelHeadings(Path(tree.stories.in_graph.source_root), model)

    def link(self) -> None:
        for step in self.tree.every_step():
            self._link_step(step)

    def _link_step(self, step: "Node") -> None:
        examples = self._examples_by_file.get(step.source.file, [])
        for link in self.headings.links_of(step):
            for named in self.headings.nodes_at(link):
                self.graph.edges.relate("names", step, named)
                self.graph.edges.relate("namedBy", named, step)
                for example in self._named_after(link.after, examples):
                    self.graph.edges.group("demonstrates", example, named)
                    self.graph.edges.relate("demonstratedThrough", named, example)

    def _named_after(self, after: str, examples: list["Node"]) -> list["Node"]:
        """The examples among examples whose name is written straight after a linked term, as words or as the name
        code gives it (``paid order`` for ``paid_order``)."""
        words = after.lstrip(_BEFORE_EXAMPLE).casefold()
        return [example for example in examples if words.startswith(example.name.replace("_", " ").casefold())]

    @cached_property
    def _examples_by_file(self) -> dict[str, list["Node"]]:
        """The examples of the Stories graph by the story file each is recorded for, read once."""
        return self.tree.examples_by_file()
