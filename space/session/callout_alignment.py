"""Callout alignment - whether the callouts a session's files show match the edges of its knowledge graph."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, NamedTuple

from harness.graph.saved_graph import SavedGraph, SavedNode
from harness.markdown.format import Format
from space.session.session_file import FileTooLongToShowError
from space.session.session_files import NamedPathNotFoundError

if TYPE_CHECKING:
    from harness.agent_tools.tool_call import ToolCall
    from space.session.session import Session
    from space.session.session_file import FileCallout

# The kinds of gap between a file's callouts and the graph's edges.
CALLOUT_TARGET_MISSING = "callout_target_missing"
CALLOUT_WITHOUT_EDGE = "callout_without_edge"
EDGE_WITHOUT_CALLOUT = "edge_without_callout"
# The back-edge of every child list, which no file writes as a link of its own.
_BACK_EDGE = "belongsTo"
_MARKDOWN = "markdown"
# A page is written in a code format, yet its text holds no link a callout is read from; a drawing holds none either.
_PAGE_FORMATS = frozenset({"html"})


class _CalloutGap(NamedTuple):
    """One gap between a file's callouts and the graph's edges: its kind, the file, and what is wrong in plain words."""

    kind: str
    file: str
    message: str


class PlacedNode(NamedTuple):
    """A node of the graph with its file named from the project, so it is matched against a callout's files."""

    node: SavedNode
    file: str

    def covers(self, line: int) -> bool:
        return self.node.line <= line <= self.node.end_line

    def holds(self, other: PlacedNode) -> bool:
        """Whether other sits within this node's lines, as a scenario sits within its story."""
        return self.node.line <= other.node.line and other.node.end_line <= self.node.end_line

    @property
    def named(self) -> str:
        return f"{self.node.type} '{self.node.name}'"


class _CrossingEdge(NamedTuple):
    """An edge of the graph whose two nodes sit in different files."""

    parent: PlacedNode
    child: PlacedNode
    kind: str

    @property
    def ends(self) -> tuple[tuple[PlacedNode, PlacedNode], tuple[PlacedNode, PlacedNode]]:
        """The edge's two nodes, each first in turn, since a callout on either shows it."""
        return ((self.parent, self.child), (self.child, self.parent))


class CalloutAlignment:
    """The callouts of a session's files against the edges of its knowledge graph, read from exactly the files it is
    given, as the Files app's graph view reads them. A callout is what a link to a heading of another file opens in
    place (``session.file`` callouts), in a markdown file or in a story test's steps; an edge matches it when it joins a
    node on the callout's line, or one within a node on that line, with a node in the file the callout opens, in
    either direction: a story test's ``# Map:`` header sits on its story, so the edge to one of the story's scenarios
    matches it. A callout on a line no node of its file sits on speaks for the whole file, so any node of the file
    matches it. A link to a whole file, with no heading, is a reference a sentence makes, which no edge is
    expected for."""

    def __init__(self, session: Session, files: list[str], call: ToolCall | None = None) -> None:
        self._session = session
        self._files = list(files)
        self._call = call
        self._crossing: list[_CrossingEdge] = []
        self._nodes_in: dict[str, list[PlacedNode]] = {}
        self._callouts: dict[str, list[FileCallout]] = {}

    def gaps(self) -> list[_CalloutGap]:
        """Each link whose target is not there, each callout no edge matches, and each edge between a markdown file and
        another document or code file that no callout shows from either end. No files, or a session working on no
        practice, answer none, since no practice reads the files."""
        if not self._files or not self._session.session_practices.working:
            return []
        self._read_graph()
        self._callouts = {file: self._callouts_of(file) for file in self._files if self._holds_links(file)}
        by_file = [self._missing_targets(file) + self._unmatched(file) for file in self._callouts]
        return [gap for gaps in by_file for gap in gaps] + self._unshown()

    def _read_graph(self) -> None:
        """Read the files into the session's graph and keep each edge whose nodes sit in two files, each node with its
        file named from the project."""
        session = self._session
        graph = session.graph
        graph.load_files(str(session.checkout.root.resolve()), session.session_practices.working, self._files, graph.overlays, self._call)
        practices = list(SavedGraph.from_graph(graph).practices.values())
        nodes: dict[str, PlacedNode] = {}
        for practice in practices:
            root = Path(practice.source_root) if practice.source_root else session.checkout.root
            nodes.update({node.node_id: PlacedNode(node, session.paths.from_project(root / node.file)) for node in practice.nodes if node.file})
        for placed in nodes.values():
            self._nodes_in.setdefault(placed.file, []).append(placed)
        edges = (edge for practice in practices for edge in practice.edges if edge.kind != _BACK_EDGE and edge.parent in nodes and edge.child in nodes)
        joined = (_CrossingEdge(nodes[edge.parent], nodes[edge.child], edge.kind) for edge in edges)
        self._crossing = [edge for edge in joined if edge.parent.file != edge.child.file]

    def _holds_links(self, file: str) -> bool:
        """Whether a callout is read from the text of file: a markdown document, or code, such as a story test."""
        format = Format.from_extension(Path(file).suffix)
        return format.group == _MARKDOWN or (format.is_code and format.name not in _PAGE_FORMATS)

    def _callouts_of(self, file: str) -> list[FileCallout]:
        """The callouts of file; none for a file gone since it was listed or too long for the viewer, which shows none."""
        try:
            return self._session.file(file).callouts
        except (NamedPathNotFoundError, FileTooLongToShowError):
            return []

    def _missing_targets(self, file: str) -> list[_CalloutGap]:
        missing = (callout for callout in self._callouts[file] if callout.missing)
        return [_CalloutGap(CALLOUT_TARGET_MISSING, file, f"{file} line {callout.line}: the link '{callout.title}' opens nothing: {callout.missing}.") for callout in missing]

    def _unmatched(self, file: str) -> list[_CalloutGap]:
        """The callouts of file that name a heading which is there, and that no edge matches."""
        to_headings = (callout for callout in self._callouts[file] if not callout.missing and "#" in callout.link)
        unmatched = (callout for callout in to_headings if not any(self._shows(callout, file, edge) for edge in self._crossing))
        return [self._without_edge(file, callout) for callout in unmatched]

    def _unshown(self) -> list[_CalloutGap]:
        """The edges between a markdown file and another file a callout is read from that no callout shows."""
        checked = (edge for edge in self._crossing if edge.parent.file in self._callouts and edge.child.file in self._callouts)
        from_documents = (edge for edge in checked if self._is_document(edge.parent.file) or self._is_document(edge.child.file))
        return list(dict.fromkeys(self._without_callout(edge) for edge in from_documents if not self._is_shown(edge)))

    def _is_document(self, file: str) -> bool:
        return Format.from_extension(Path(file).suffix).group == _MARKDOWN

    def _is_shown(self, edge: _CrossingEdge) -> bool:
        """Whether a callout on the lines of either node of edge opens the file of the other."""
        return any(self._shows(callout, file, edge) for file in (edge.parent.file, edge.child.file) for callout in self._callouts[file])

    def _shows(self, callout: FileCallout, file: str, edge: _CrossingEdge) -> bool:
        """Whether callout, on a line of file, shows edge: the edge joins a node of file on that line or within a node
        on it, or any node of file when no node sits on that line, with a node in the file the callout opens."""
        on_line = [node for node in self._nodes_in.get(file, []) if node.covers(callout.line)]
        joined = (here for here, there in edge.ends if here.file == file and there.file == callout.section.path)
        return any(not on_line or any(node.holds(here) for node in on_line) for here in joined)

    def _without_edge(self, file: str, callout: FileCallout) -> _CalloutGap:
        message = f"{file} line {callout.line}: the callout '{callout.title}' opens {callout.section.path}, but no edge of the graph joins that line to a node in {callout.section.path}."
        return _CalloutGap(CALLOUT_WITHOUT_EDGE, file, message)

    def _without_callout(self, edge: _CrossingEdge) -> _CalloutGap:
        """The gap of an edge no callout shows, reported in its markdown file, the parent's when both are markdown."""
        here, there = (edge.parent, edge.child) if self._is_document(edge.parent.file) else (edge.child, edge.parent)
        message = f"{here.file}: the graph joins {here.named} to {there.named} in {there.file} ({edge.kind}), but no callout on either opens the other's file."
        return _CalloutGap(EDGE_WITHOUT_CALLOUT, here.file, message)
