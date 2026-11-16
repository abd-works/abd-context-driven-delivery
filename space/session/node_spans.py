"""NodeSpans - the lines one node of a session's graph covers, in each file it was read from."""

from __future__ import annotations

from pathlib import Path

from harness.graph.explorer import ExplorerEntry
from harness.graph.graph import MARKDOWN_SUFFIXES, FilterRequest, Graph
from harness.markdown.markdown import MarkdownText


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

    def collect(self, node_id: str, below_lines: bool = False) -> NodeSpans:
        """Widen the spans with the lines node_id covers in its file and the lines of the nodes it is made of, wherever
        they sit, such as a story map's story and its scenarios in their own file, which its own line alone does not
        reach; or, read from no file's lines, with those of the nodes below it. Below a node read from lines, a node read
        from none, such as the invokes group a step's calls sit under, is left closed, so a step opens no operation it
        calls."""
        if node_id in self._seen:
            return self
        node = self._graph.node(node_id)
        if not self._seen and node is not None:
            self._name = node.name
        self._seen.add(node_id)
        source = node.source if node is not None else None
        if source is None:
            return self
        path = (Path(source.root or self._root) / source.file).resolve() if source.file else None
        if path is None or source.start_line < 1 or not path.is_file():
            return self if below_lines else self._collect_below(node_id, below_lines=False)
        start, end = self._spans.get(path, (source.start_line, source.end_line))
        self._spans[path] = (min(start, source.start_line), max(end, source.end_line, source.start_line))
        return self._collect_below(node_id, below_lines=True)

    def _collect_below(self, node_id: str, below_lines: bool) -> NodeSpans:
        branch = self._graph.explorer.explorer_branch(node_id, self._request)
        for child in branch.children if branch is not None else []:
            if isinstance(child, ExplorerEntry):
                self.collect(child.node_id, below_lines)
        return self
