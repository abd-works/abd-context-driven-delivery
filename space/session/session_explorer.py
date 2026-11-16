"""SessionExplorer - what a page browsing a session's files asks of its knowledge graph."""

from __future__ import annotations

from typing import TYPE_CHECKING

from space.session.node_spans import NodeSpans

if TYPE_CHECKING:
    from harness.agent_tools.tool_call import ToolCall
    from harness.graph.explorer import ExplorerEntry, NodeSource
    from space.session.file_range import Range
    from space.session.session import Session


class SessionExplorer:
    """*SessionExplorer* answers a page browsing one session's files from the session's graph: the practice trees read
    from exactly the files the page lists, one node's entry, the lines a node covers, and every member the graph holds.
    The files the page lists are the one filter, named from the project."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def trees(self, paths: list[str], call: ToolCall | None) -> list[ExplorerEntry]:
        """The practice trees read from exactly the files at paths; none when no path is in the project."""
        session = self._session
        listed = session.paths.in_project(paths)
        if not listed:
            return []
        graph = session.graph
        graph.load_files(str(session.repo_path.resolve()), session.practice_outputs.working, listed, graph.overlays, call)
        return graph.explorer.explorer_trees({"paths": listed})

    def branch(self, node_id: str, paths: list[str]) -> ExplorerEntry | None:
        """The node's entry, kept to the nodes read from the files at paths."""
        return self._session.graph.explorer.explorer_branch(node_id, {"paths": self._session.paths.in_project(paths)})

    def node_ranges(self, node_id: str, paths: list[str]) -> list[Range]:
        """The lines the node covers, one range for each file among paths."""
        session = self._session
        spans = NodeSpans(session.graph, {"paths": session.paths.in_project(paths)}, session.work_root).collect(node_id).spans
        return [session.file(session.paths.from_project(path)).range(start, end) for path, (start, end) in spans.items()]

    def members(self) -> list[NodeSource]:
        """Every class, operation, and property the graph holds, each with its text and its class."""
        return self._session.graph.explorer.source_members()
