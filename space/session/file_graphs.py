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
        # When the session's graph last read each file a page lists, for the graph view: a file changed since is read
        # again before a node's lines in it are answered.
        self._listed_reads: dict[Path, float] = {}
        self._listed_lock = threading.Lock()

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
                graph.load_files(str(self.alone_folder), working, [str(path)])
                self._alone = (working, graph, (path, modified))
            return SavedGraph.from_graph(graph)

    @property
    def alone_folder(self) -> Path:
        """The folder a file read on its own is read from, and its nodes' files are named from: the project's root, so a
        file outside the session's own folder, such as a story test in the project's story_tests, is read too."""
        return Path(self._session.repo_path).resolve()

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

    def listed(self, paths: list[Path]) -> None:
        """The session's knowledge graph read the files at paths now, the files a page lists for its graph view."""
        read_at = time.time()
        with self._listed_lock:
            self._listed_reads = {path: read_at for path in paths}

    def listed_file_as_it_is_now(self, path: Path) -> None:
        """Read the listed file at path into the session's knowledge graph again when it changed since the graph read
        it, so the lines a node covers are the file's lines as it is now. A file the graph view never listed, or one
        that has gone, is left as the graph holds it."""
        modified = path.stat().st_mtime if path.is_file() else -1.0
        with self._listed_lock:
            read_at = self._listed_reads.get(path)
            is_current = read_at is None or modified <= read_at
            if not is_current:
                self._listed_reads[path] = max(modified, time.time())
        if not is_current:
            self._session.graph.refresh([str(path)])

    def _working(self) -> list[str]:
        return sorted(key for key, output in self._session.own_practices.items() if output.enabled)

    def _read_at(self) -> float:
        """When the session's graph read the files it holds, for one no viewer has shown since: when it was opened, or
        when the graph it opened was saved, whichever is earlier."""
        saved = Path(self._session.work_folder) / GRAPH_FILE_NAME
        return min(self._opened_at, saved.stat().st_mtime) if saved.is_file() else self._opened_at
