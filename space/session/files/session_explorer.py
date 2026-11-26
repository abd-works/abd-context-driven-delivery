"""SessionExplorer - what a page browsing a session's files asks of its knowledge graph."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Callable

from harness.agent_tools.agent_tools import agent_tool, noSessionLog
from harness.agent_tools.tool_call import ToolCall
from harness.annotations.annotation import hosted_only
from harness.graph.explorer import ExplorerEntry, NodeSource
from harness.graph.node_filter import FilterChoices, FilterRequest
from harness.mcp.mcp_annotations import long_call, mcp
from space.session.files.file_range import Range
from space.session.files.node_spans import NodeSpans

if TYPE_CHECKING:
    from harness.graph.graph import Graph
    from space.session.session_graph import SessionGraph
    from space.session.practices.session_practices import SessionPractices
    from space.session.files.session_file import SessionFile
    from space.session.session_checkout import SessionCheckout
    from space.session.session_paths import SessionPaths


@hosted_only
class SessionExplorer:
    """*SessionExplorer* answers a page browsing one session's files from the session's graph, as the session's tools:
    the practice trees read from exactly the files the page lists, one node's entry, the lines a node covers, and every
    member the graph holds. The files the page lists are the one filter, named from the project. Mixed into *Session*,
    whose graph, paths, and files it reads."""

    paths: SessionPaths
    graph: Graph
    checkout: SessionCheckout
    work_root: Path
    session_practices: SessionPractices
    session_graph: SessionGraph
    file: Callable[[str], SessionFile]

    @long_call
    @mcp
    @agent_tool
    @noSessionLog
    def graph_trees(self, paths: list[str], node_filter: FilterRequest | None = None, call: ToolCall | None = None) -> list[ExplorerEntry]:
        """Return the practice trees of this session's graph read from exactly the files at paths, each named from the project as the Files app lists them, and holding only the nodes read from them: each practice's root with the entries below it, closed, as graph.explorer_trees answers them. The files the page lists are the one filter: the graph reads them, its story tests in code and in markdown alike, and keeps what they hold. node_filter is a node filter as graph.explorer_trees takes it (types, relationships, violations, rules): it applies with the file list, narrowing the nodes of the files listed, and never widens the list, so any paths it names are the list's. No paths, or none in the project, answer no tree, and so does a session with every practice turned off, since no practice reads the files."""
        listed = self.paths.in_project(paths)
        if not self._read_listed(listed, call):
            return []
        return self.graph.explorer_trees(self._narrowed_to(listed, node_filter))

    def _read_listed(self, listed: list[str], call: ToolCall | None = None) -> bool:
        """Read the files listed into the session's graph, as they are now; answers whether anything was read, which
        nothing is when none is listed or every practice is turned off."""
        if not listed or not self.session_practices.working:
            return False
        graph = self.graph
        graph.load_files(str(self.checkout.root.resolve()), self.session_practices.working, listed, graph.overlays, call)
        self.session_graph.listed([self.paths.path_named(path) for path in listed])
        return True

    @mcp
    @agent_tool
    @noSessionLog
    def graph_branch(self, node_id: str, paths: list[str], node_filter: FilterRequest | None = None) -> ExplorerEntry | None:
        """Return the node node_id's entry in this session's graph, kept to the nodes read from the files at paths and matched by node_filter as graph_trees keeps them, with the entries below it, closed; None for an id the graph no longer holds."""
        return self.graph.explorer_branch(node_id, self._narrowed_to(self.paths.in_project(paths), node_filter))

    @mcp
    @agent_tool
    @noSessionLog
    def graph_filter_choices(self, practices: list[str], node_types: list[str], practices_before: list[str] | None = None) -> FilterChoices:
        """Return the node types the graph view's node filter offers and those it chooses, with the connectors and rules of the chosen ones, as graph.filter_choices answers them on this session's graph."""
        return self.graph.filter_choices(practices, node_types, practices_before)

    @long_call
    @mcp
    @agent_tool
    @noSessionLog
    def graph_fix_prompt(self, paths: list[str], node_filter: FilterRequest | None = None, rule: str = "", node_id: str = "", call: ToolCall | None = None) -> str:
        """Return what the graph view's Fix buttons send the chat, read from the session's graph as graph_trees reads it for paths and node_filter, each file as it is now: Fix all, with no rule and no node_id, every rule broken on every node the view shows; Fix rule, with rule, every node the view shows breaking that rule; Fix this one, with rule and node_id, that rule on that node. Each names its node, file and lines, rule, code and what is wrong, asking for the fix test first. Empty when the view shows no such broken rule, such as one fixed since and read again."""
        listed = self.paths.in_project(paths)
        if not self._read_listed(listed, call):
            return ""
        narrowed = self._narrowed_to(listed, node_filter)
        chosen: FilterRequest = {**narrowed, "rules": [rule]} if rule else narrowed
        return self.graph.fix_prompt(chosen, node_id)

    def _narrowed_to(self, listed: list[str], node_filter: FilterRequest | None) -> FilterRequest:
        """The graph's filter request for a node filter applied with the file list: the node filter's choices, kept to
        the files listed, in place of any paths it names."""
        return {**(node_filter or {}), "paths": listed}

    @mcp
    @agent_tool
    @noSessionLog
    def graph_node_ranges(self, node_id: str, paths: list[str]) -> list[Range]:
        """Return the lines the node node_id covers, one range for each file, each named from the project, so a viewer opens every file there. A node read from lines of a file answers that one range; a node read from no file's lines, such as a module that is a folder, answers each file the nodes below it come from, among paths, spanning the lines they cover; none for an id the graph no longer holds. A node the graph read from the lines of a file that is no longer there, such as one moved since, is refused, naming that file. A file changed since graph_trees read it is read again first, so the lines are the file's as it is now."""
        node_spans = NodeSpans(self.graph, {"paths": self.paths.in_project(paths)}, self.work_root)
        read_from = node_spans.file_of(node_id)
        if read_from is not None:
            self.session_graph.as_it_is_now(read_from)
        spans = node_spans.collect(node_id).spans
        return [self.file(self.paths.from_project(path)).range(start, end) for path, (start, end) in spans.items()]

    @mcp
    @agent_tool
    @noSessionLog
    def graph_members(self) -> list[NodeSource]:
        """Return every class, operation, and property this session's graph holds, each with its text and the class it belongs to, so a viewer opens a call in place even when it reaches another file. Read after graph_trees, which reads the files the page lists."""
        return self.graph.source_members()
