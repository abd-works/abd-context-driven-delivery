"""FileGraphs - the graphs a session reads one file into for a viewer: alone, or in its whole knowledge graph."""

from __future__ import annotations

import threading
import time
from pathlib import Path
from typing import TYPE_CHECKING

from harness.graph.graph import Graph
from harness.graph.saved_graph import GRAPH_FILE_NAME, SavedGraph
from harness.guidance.practice_catalogue import PRACTICE_CATALOGUE

if TYPE_CHECKING:
    from space.session.session import Session


class FileGraphs:
    """The graphs one session reads a single file into, so a viewer shows its folds and the rules it breaks. Reading a
    file into a graph takes a second or two, so each file is read again only once it changed."""

    def __init__(self, session: Session) -> None:
        self._session = session
        # The small graph a viewer reads one file into, apart from the knowledge graph: the practices it was made with,
        # the graph, and the file it last read with that file's modification time.
        self._alone: tuple[list[str], Graph, tuple[Path, float] | None] | None = None
        self._alone_lock = threading.Lock()
        # When the session's knowledge graph last read each file a viewer showed, by its modification time, and the
        # graph it read them into.
        self._whole_reads: tuple[Graph | None, dict[Path, float]] = (None, {})
        self._whole_lock = threading.Lock()
        self._opened_at = 0.0

    def opened(self) -> None:
        """The session opened a new knowledge graph now: every file it holds was read at this moment or before."""
        self._opened_at = time.time()

    def file_alone(self, path: Path) -> SavedGraph:
        """The file at path read on its own, as it is now, with only its own rules run: no other file is read or linked
        to it, so a viewer shows its folds and the rules it breaks in under a second. The graph is made with its own
        instance of each practice the session works on."""
        working = self._working()
        modified = path.stat().st_mtime if path.is_file() else -1.0
        with self._alone_lock:
            if self._alone is None or self._alone[0] != working:
                practices = [practice for practice in PRACTICE_CATALOGUE.create_all() if practice.key in working]
                self._alone = (working, Graph(practices), None)
            _working, graph, read = self._alone
            if read != (path, modified):
                graph.load_files(str(self._session.work_root), working, [str(path)])
                self._alone = (working, graph, (path, modified))
            return SavedGraph.from_graph(graph)

    def file_in_whole(self, path: Path, is_held: bool) -> SavedGraph:
        """The file at path in the session's knowledge graph holding the whole working copy, so the rules that link files
        and practices hold, which takes far longer than reading the file alone. The file is read into the graph when the
        graph holds nothing of it (is_held false) or it changed since the graph last read it: since a viewer last showed
        it, or, before that, since the graph was opened or saved."""
        graph = self._session.graph
        graph.reads.hold_whole()
        modified = path.stat().st_mtime if path.is_file() else -1.0
        with self._whole_lock:
            held, reads = self._whole_reads
            if held is not graph:
                reads = {}
                self._whole_reads = (graph, reads)
            is_current = is_held and modified <= reads.get(path, self._read_at())
            reads[path] = max(modified, time.time())
        if not is_current:
            graph.refresh([str(path)])
        return SavedGraph.from_graph(graph)

    def _working(self) -> list[str]:
        return sorted(key for key, output in self._session.own_practices.items() if output.enabled)

    def _read_at(self) -> float:
        """When the session's graph read the files it holds, for one no viewer has shown since: when it was opened, or
        when the graph it opened was saved, whichever is earlier."""
        saved = Path(self._session.session_path) / GRAPH_FILE_NAME
        return min(self._opened_at, saved.stat().st_mtime) if saved.is_file() else self._opened_at
