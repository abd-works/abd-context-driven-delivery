"""SessionExplorer - what a page browsing a session's files asks of its knowledge graph."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Callable

from harness.agent_tools.agent_tools import agent_tool, noSessionLog
from harness.agent_tools.tool_call import ToolCall
from harness.annotations.annotation import hosted_only
from harness.graph.explorer import ExplorerEntry, NodeSource
from harness.mcp.mcp_annotations import long_call, mcp
from space.session.file_range import Range
from space.session.node_spans import NodeSpans

if TYPE_CHECKING:
    from harness.graph.graph import Graph
    from space.session.practice_outputs import PracticeOutputs
    from space.session.session_file import SessionFile
    from space.session.session_paths import SessionPaths


@hosted_only
class SessionExplorer:
    """*SessionExplorer* answers a page browsing one session's files from the session's graph, as the session's tools:
    the practice trees read from exactly the files the page lists, one node's entry, the lines a node covers, and every
    member the graph holds. The files the page lists are the one filter, named from the project. Mixed into *Session*,
    whose graph, paths, and files it reads."""

    paths: SessionPaths
    graph: Graph
    repo_path: Path
    work_root: Path
    practice_outputs: PracticeOutputs
    file: Callable[[str], SessionFile]

    @long_call
    @mcp
    @agent_tool
    @noSessionLog
    def graph_trees(self, paths: list[str], call: ToolCall | None = None) -> list[ExplorerEntry]:
        """Return the practice trees of this session's graph read from exactly the files at paths, each named from the project as the Files app lists them, and holding only the nodes read from them: each practice's root with the entries below it, closed, as graph.explorer_trees answers them. The files the page lists are the one filter: the graph reads them, its story tests in code and in markdown alike, and keeps what they hold. No paths, or none in the project, answer no tree."""
        listed = self.paths.in_project(paths)
        if not listed:
            return []
        graph = self.graph
        graph.load_files(str(self.repo_path.resolve()), self.practice_outputs.working, listed, graph.overlays, call)
        return graph.explorer.explorer_trees({"paths": listed})

    @mcp
    @agent_tool
    @noSessionLog
    def graph_branch(self, node_id: str, paths: list[str]) -> ExplorerEntry | None:
        """Return the node node_id's entry in this session's graph, kept to the nodes read from the files at paths as graph_trees keeps them, with the entries below it, closed; None for an id the graph no longer holds."""
        return self.graph.explorer.explorer_branch(node_id, {"paths": self.paths.in_project(paths)})

    @mcp
    @agent_tool
    @noSessionLog
    def graph_node_ranges(self, node_id: str, paths: list[str]) -> list[Range]:
        """Return the lines the node node_id covers, one range for each file, each named from the project, so a viewer opens every file there. A node read from lines of a file answers that one range; a node read from no file's lines, such as a module that is a folder, answers each file the nodes below it come from, among paths, spanning the lines they cover; none for an id the graph no longer holds."""
        spans = NodeSpans(self.graph, {"paths": self.paths.in_project(paths)}, self.work_root).collect(node_id).spans
        return [self.file(self.paths.from_project(path)).range(start, end) for path, (start, end) in spans.items()]

    @mcp
    @agent_tool
    @noSessionLog
    def graph_members(self) -> list[NodeSource]:
        """Return every class, operation, and property this session's graph holds, each with its text and the class it belongs to, so a viewer opens a call in place even when it reaches another file. Read after graph_trees, which reads the files the page lists."""
        return self.graph.explorer.source_members()
