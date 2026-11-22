"""FileViewFilter - which callouts of a file a file view shows, for the filters its page sends with the read."""

from __future__ import annotations

from functools import cached_property
from pathlib import Path
from typing import TYPE_CHECKING

from harness.graph.node_filter import Filter, FilterRequest

if TYPE_CHECKING:
    from harness.graph.graph import Node
    from space.session.session import Session

# What a node filter chooses that narrows a file's callouts: the practices, the node types and the connectors. Its
# rules and its Violations switch choose which broken rules the graph view lists, never what a line opens in place.
_NODE_CHOICES = ("practices", "practice", "types", "type")
_CONNECTOR_CHOICES = ("relationships",)


class FileViewFilter:
    """The filters of a file view, as its page sends them with the read of a file: the files its stages, practices and
    formats list, and the graph view's node filter. They decide which callouts of the file show, by a
    *Filter* made for both, as the session's graph trees are (``session.graph_trees``): a callout into a file of a
    stage, practice or format turned off is left out, and so is what a step invokes or observes while the node filter
    leaves out that connector or the node type of what it reaches. A file no fidelity declares, such as a note, belongs
    to no practice, so no practice turned off hides a callout into it. A read that sends no list of files and no node
    filter, as an agent's does, shows every callout."""

    def __init__(self, session: Session, listed: list[str] | None = None, node_filter: FilterRequest | None = None) -> None:
        self._session = session
        self._listed = listed
        self._node_filter = dict(node_filter or {})
        self._of_a_practice: dict[str, bool] = {}

    def shows_file(self, path: str) -> bool:
        """Whether a callout into the file at path, named from the project, shows: every file while the page sent no
        list; else a file the list holds, or one no fidelity declares."""
        if self._listed is None:
            return True
        return self._by_files.lists(path) or not self._is_of_a_practice(path)

    def shows(self, connector: str, reached: Node) -> bool:
        """Whether what a step reaches by connector, such as invokes or observes, shows: the connector is one the node
        filter chooses, or it chooses none; the node filter matches the node reached; and the file it sits in shows."""
        connectors = self._by_files.relationships
        if connectors and connector not in connectors:
            return False
        if self._chooses_nodes and not self._by_nodes.matches(reached):
            return False
        return self.shows_file(self._file_of(reached))

    @property
    def _chooses_nodes(self) -> bool:
        return any(self._node_filter.get(choice) for choice in _NODE_CHOICES)

    @cached_property
    def _by_files(self) -> Filter:
        """The filter of the files listed and the connectors chosen."""
        chosen = {choice: self._node_filter[choice] for choice in _CONNECTOR_CHOICES if choice in self._node_filter}
        return Filter(self._session.graph, {**chosen, "paths": self._session.paths.in_project(self._listed or [])})

    @cached_property
    def _by_nodes(self) -> Filter:
        """The filter of the practices and node types chosen. A node is matched apart from the files
        listed, which shows_file answers, since a node in a file of no practice is in no list and still shows."""
        return Filter(self._session.graph, {choice: self._node_filter[choice] for choice in _NODE_CHOICES if choice in self._node_filter})

    def _file_of(self, node: Node) -> str:
        """The file node was read from, named from the project."""
        source = node.source
        return self._session.paths.from_project(Path(source.root or self._session.work_root, source.file).resolve())

    def _is_of_a_practice(self, path: str) -> bool:
        """Whether a fidelity of any practice, turned on for the session or not, declares the file at path; asked once
        for each file, since several callouts of one file reach the same one."""
        if path not in self._of_a_practice:
            file = self._session.paths.path_named(path)
            outputs = self._session.practice_outputs.every.values()
            self._of_a_practice[path] = any(fidelity.session_output.written.holds(file) for output in outputs for fidelity in output.fidelities)
        return self._of_a_practice[path]
