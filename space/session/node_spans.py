"""NodeSpans - the lines one node of a session's graph covers, in each file it was read from."""

from __future__ import annotations

from pathlib import Path

from harness.graph.explorer import ExplorerEntry
from harness.graph.graph import MARKDOWN_SUFFIXES, FilterRequest, Graph, Node
from harness.markdown.markdown import MarkdownText
from space.session.session_files import NamedPathNotFoundError

# The kind of node a story's example is: a fixture a scenario uses, declared in the story test or in an examples module.
EXAMPLE_TYPE = "Example"


class NodeSpans:
    """The lines a node covers, one span for each file: a node read from lines of a file covers those; a node read from
    no file's lines, such as a module that is a folder, covers the lines of the nodes below it. Only the files the
    request keeps are covered."""

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

    def file_of(self, node_id: str) -> Path | None:
        """The file whose lines the node node_id was read from, while it is there; none for a node the graph does not
        hold or one read from no lines."""
        node = self._graph.node(node_id)
        return self._lines_file(node) if node is not None and node.source is not None else None

    def collect(self, node_id: str) -> NodeSpans:
        """Widen the spans with the lines node_id covers in its file and the lines of the nodes it is made of, wherever
        they sit, such as a story map's story and its scenarios in their own file, which its own line alone does not
        reach; or, read from no file's lines, with those of the nodes below it. Below a node read from lines, a
        relationship group, such as the invokes group a step's calls sit under or the invokedBy group of the steps that
        call an operation, is left closed, so a step opens no operation it calls and an operation no step that calls it.
        A node shown under another as a relationship covers its own lines alone. The walk keeps its own stack, so a deep
        tree never runs past Python's call stack. A node read from a file or a folder that is no longer there, such as
        one moved since the graph read it, is refused: it would open nothing, which reads as a node with no lines. A
        folder that is there, such as a package's, is read from no lines and opens the files below it."""
        self._refuse_gone(self._graph.node(node_id))
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
        """True for an example, which a scenario uses from where the story declares it, such as the examples module a
        story test imports its fixtures from or the Examples table of a markdown story: it is no part of the scenario,
        so the scenario's lines open alone."""
        return node.type == EXAMPLE_TYPE

    def _widen_with(self, node: Node) -> bool:
        """Widen the spans with the lines node was read from; whether it was read from any."""
        path = self._lines_file(node)
        if path is None:
            return False
        if not self._kept(path):
            # Read from lines, but of a file the request leaves out: nothing of it opens, and the nodes below it still do.
            return True
        source = node.source
        start, end = self._spans.get(path, (source.start_line, source.end_line))
        self._spans[path] = (min(start, source.start_line), max(end, source.end_line, source.start_line))
        return True

    def _kept(self, path: Path) -> bool:
        """Whether the request keeps the file at path: every file when it names no paths, else one it names or one
        under a folder it names. A story the graph placed on a story map the viewer does not list, because its story
        test names that map, opens its story test alone."""
        listed = [str(named).replace("\\", "/").strip("/") for named in self._request.get("paths") or []]
        folder = self._graph.folder
        if not listed or not folder or not path.is_relative_to(Path(folder).resolve()):
            return True
        named = path.relative_to(Path(folder).resolve()).as_posix()
        return any(named == kept or named.startswith(kept + "/") for kept in listed)

    def _refuse_gone(self, node: Node | None) -> None:
        named = self._named_file(node) if node is not None and node.source is not None else None
        if named is not None and not named.exists():
            raise NamedPathNotFoundError(node.source.file, Path(node.source.root or self._root))

    def _lines_file(self, node: Node) -> Path | None:
        """The file whose lines node was read from, while it is there; none for a node read from no lines."""
        path = self._named_file(node)
        return path if path is not None and path.is_file() else None

    def _named_file(self, node: Node) -> Path | None:
        """The file node's source names its lines in; none for a node read from no lines, such as a module that is a
        folder or a relationship group, which carries its holder's source but no lines of its own."""
        source = node.source
        if node.type == node.name or not source.file or source.start_line < 1:
            return None
        return (Path(source.root or self._root) / source.file).resolve()

    def _below(self, node: Node, below_lines: bool) -> list[tuple[str, bool]]:
        """The nodes the request keeps at their home below node, still to take. A node shown under node only as a
        relationship adds its own lines here, but nothing below it; an example node uses adds none."""
        branch = self._graph.explorer.explorer_branch(node.node_id, self._request)
        entries = [child for child in (branch.children if branch is not None else []) if isinstance(child, ExplorerEntry)]
        children = [child for entry in entries if (child := self._graph.node(entry.node_id)) is not None]
        for related in (child for child in children if not self._at_home_under(child, node) and not self._used_from_elsewhere(child)):
            self._widen_with(related)
        return [(child.node_id, below_lines) for child in children if self._at_home_under(child, node)]

    def _at_home_under(self, child: Node, holder: Node) -> bool:
        """True when child sits under holder as its own, or holder is a relationship group, which holds every node it
        shows."""
        return child.parent is holder or holder.type == holder.name
