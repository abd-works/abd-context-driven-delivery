"""NodeSpans - the lines one node of a session's graph covers, in each file it was read from."""

from __future__ import annotations

from pathlib import Path

from harness.graph.explorer import ExplorerEntry
from harness.graph.graph import MARKDOWN_SUFFIXES, FilterRequest, Graph, Node
from harness.markdown.markdown import MarkdownText

# The kind of node a story's example is: a fixture a scenario uses, declared in the story test or in an examples module.
EXAMPLE_TYPE = "Example"


class NodeSpans:
    """The lines a node covers, one span for each file: a node read from lines of a file covers those; a node read from
    no file's lines, such as a module that is a folder, covers the lines of the nodes below it, among the files the
    request keeps."""

    def __init__(self, graph: Graph, request: FilterRequest, root: Path) -> None:
        self._graph = graph
        self._request = request
        # The folder a node's file is named from when its source names no root of its own.
        self._root = root
        self._seen: set[str] = set()
        self._spans: dict[Path, tuple[int, int]] = {}
        # The name of the node collected first, the one the spans are for.
        self._name = ""

    @property
    def spans(self) -> dict[Path, tuple[int, int]]:
        """Each file's first and last line the node covers. In a markdown file that heads the node's part with a heading
        of its own, such as a story map's story or sub-epic in its scenarios file (``## Story: Delete Ticket``), the
        span starts at that heading, not at the first scenario below it."""
        return {path: (self._heading_above(path, start), end) for path, (start, end) in self._spans.items()}

    def _heading_above(self, path: Path, start: int) -> int:
        """The line of the last heading at or above start that names the node, after its kind (``Sub-epic: Remove
        Tickets``); start itself when none does or the file is not markdown."""
        if not self._name or path.suffix.lower() not in MARKDOWN_SUFFIXES:
            return start
        text = MarkdownText(path.read_text(encoding="utf-8"))
        named = [text.text.count("\n", 0, offset) + 1 for offset, _end, _level, title in text.headings() if title.split(":", 1)[-1].strip() == self._name]
        return max((line for line in named if line <= start), default=start)

    def collect(self, node_id: str) -> NodeSpans:
        """Widen the spans with the lines node_id covers in its file and the lines of the nodes it is made of, wherever
        they sit, such as a story map's story and its scenarios in their own file, which its own line alone does not
        reach; or, read from no file's lines, with those of the nodes below it. Below a node read from lines, a
        relationship group, such as the invokes group a step's calls sit under or the invokedBy group of the steps that
        call an operation, is left closed, so a step opens no operation it calls and an operation no step that calls it.
        A node shown under another as a relationship covers its own lines alone. The walk keeps its own stack, so a deep
        tree never runs past Python's call stack."""
        pending: list[tuple[str, bool]] = [(node_id, False)]
        while pending:
            current, below_lines = pending.pop()
            pending.extend(self._take(current, below_lines))
        return self

    def _take(self, node_id: str, below_lines: bool) -> list[tuple[str, bool]]:
        """Widen the spans with node_id's own lines; the nodes below it still to take, each with whether a node read
        from lines lies above it."""
        node = self._graph.node(node_id)
        if node_id in self._seen or node is None or node.source is None:
            return []
        if not self._seen:
            self._name = node.name
        self._seen.add(node_id)
        if below_lines and self._used_from_elsewhere(node):
            return []
        if not self._widen_with(node):
            return [] if below_lines else self._below(node, below_lines=False)
        return self._below(node, below_lines=True)

    def _used_from_elsewhere(self, node: Node) -> bool:
        """True for an example declared in a file none of the spans covers yet, such as the examples module a story
        test imports its fixtures from: the scenario uses it, but it is no part of the scenario, so the scenario's
        lines open alone."""
        return node.type == EXAMPLE_TYPE and self._lines_file(node) not in self._spans

    def _widen_with(self, node: Node) -> bool:
        """Widen the spans with the lines node was read from; whether it was read from any."""
        path = self._lines_file(node)
        if path is None:
            return False
        source = node.source
        start, end = self._spans.get(path, (source.start_line, source.end_line))
        self._spans[path] = (min(start, source.start_line), max(end, source.end_line, source.start_line))
        return True

    def _lines_file(self, node: Node) -> Path | None:
        """The file whose lines node was read from; none for a node read from no lines, such as a module that is a
        folder or a relationship group, which carries its holder's source but no lines of its own."""
        source = node.source
        if node.type == node.name or not source.file or source.start_line < 1:
            return None
        path = (Path(source.root or self._root) / source.file).resolve()
        return path if path.is_file() else None

    def _below(self, node: Node, below_lines: bool) -> list[tuple[str, bool]]:
        """The nodes the request keeps at their home below node, still to take. A node shown under node only as a
        relationship adds its own lines here, but nothing below it."""
        branch = self._graph.explorer.explorer_branch(node.node_id, self._request)
        entries = [child for child in (branch.children if branch is not None else []) if isinstance(child, ExplorerEntry)]
        children = [child for entry in entries if (child := self._graph.node(entry.node_id)) is not None]
        for related in (child for child in children if not self._at_home_under(child, node)):
            self._widen_with(related)
        return [(child.node_id, below_lines) for child in children if self._at_home_under(child, node)]

    def _at_home_under(self, child: Node, holder: Node) -> bool:
        """True when child sits under holder as its own, or holder is a relationship group, which holds every node it
        shows."""
        return child.parent is holder or holder.type == holder.name
