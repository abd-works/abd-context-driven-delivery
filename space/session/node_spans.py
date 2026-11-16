"""NodeSpans - the lines one node of a session's graph covers, in each file it was read from."""

from __future__ import annotations

from pathlib import Path

from harness.graph.explorer import ExplorerEntry
from harness.graph.graph import FilterRequest, Graph


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

    @property
    def spans(self) -> dict[Path, tuple[int, int]]:
        """Each file's first and last line the node covers."""
        return dict(self._spans)

    def collect(self, node_id: str) -> NodeSpans:
        """Widen the spans with the lines node_id covers in its file, or, read from no file's lines, with those of the
        nodes below it."""
        if node_id in self._seen:
            return self
        self._seen.add(node_id)
        node = self._graph.node(node_id)
        source = node.source if node is not None else None
        if source is None:
            return self
        path = (Path(source.root or self._root) / source.file).resolve() if source.file else None
        if path is not None and source.start_line >= 1 and path.is_file():
            start, end = self._spans.get(path, (source.start_line, source.end_line))
            self._spans[path] = (min(start, source.start_line), max(end, source.end_line, source.start_line))
            return self
        branch = self._graph.explorer.explorer_branch(node_id, self._request)
        for child in branch.children if branch is not None else []:
            if isinstance(child, ExplorerEntry):
                self.collect(child.node_id)
        return self
