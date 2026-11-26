"""SessionGraph - a session's knowledge graph, the one owner of the graph file saved in its work folder; and
DocumentGraph, the one reader of a single document into a graph of its own."""

from __future__ import annotations

import shutil
import tempfile
import threading
import time
from pathlib import Path
from typing import TYPE_CHECKING

from harness.graph.graph import Graph
from harness.graph.saved_graph import GRAPH_FILE_NAME, SavedGraph, SavedPractice
from harness.guidance.guidance import PracticeGuidance
from harness.guidance.practice_catalogue import PRACTICE_CATALOGUE

if TYPE_CHECKING:
    from space.session.session import Session
    from space.session.practices.session_practices import SessionPractices


class DocumentGraph:
    """*DocumentGraph* reads one document at a time into a graph of its own, apart from a session's knowledge graph, with
    its own instance of each practice it was made with: a file a viewer shows, read on its own so only its own rules
    run, or a document's text a diagnosis compares across formats, written into a folder of its own. Reading a file
    takes a second or two, so a file is read again only once it changed."""

    def __init__(self, practices: list[PracticeGuidance]) -> None:
        self._graph = Graph(practices)
        self._keys = [practice.key for practice in practices]
        # The file the graph last read with its modification time, so the same file unchanged is not read again.
        self._read: tuple[Path, float] | None = None
        # The folder a document's text is written into to be read, made the first time one is.
        self._folder: Path | None = None
        self._lock = threading.Lock()

    @classmethod
    def of_practices(cls, keys: list[str]) -> DocumentGraph:
        """A document graph with a new instance of each practice whose key is in keys."""
        return cls([practice for practice in PRACTICE_CATALOGUE.create_all() if practice.key in keys])

    def read(self, folder: Path, path: Path) -> SavedGraph:
        """The file at path read on its own as it is now, its nodes named from folder, with only its own rules run: no
        other file is read or linked to it."""
        modified = path.stat().st_mtime if path.is_file() else -1.0
        with self._lock:
            if self._read != (path, modified):
                self._graph.load_files(str(folder), self._keys, [str(path)])
                self._read = (path, modified)
            return SavedGraph.from_graph(self._graph)

    def read_text(self, practice: PracticeGuidance, text: str, placed_at: str) -> SavedPractice:
        """What practice reads from text, a document placed at placed_at, its path from the project: written into the
        graph's own folder, read, and removed again."""
        with self._lock:
            if self._folder is None:
                self._folder = Path(tempfile.mkdtemp(prefix="cdd-document-graph-"))
            document = self._folder / placed_at
            document.parent.mkdir(parents=True, exist_ok=True)
            document.write_text(text, encoding="utf-8")
            try:
                self._graph.load_files(str(self._folder), [practice.key], [placed_at])
                self._read = None
                return SavedGraph.from_graph(self._graph).practices.get(practice.key) or SavedPractice(practice.key)
            finally:
                document.unlink()

    def close(self) -> None:
        """Remove the folder documents' text was read from."""
        with self._lock:
            if self._folder is not None:
                shutil.rmtree(self._folder, ignore_errors=True)
                self._folder = None


class SessionGraph:
    """*SessionGraph* is a session's knowledge graph of the practices it works on, opened on its root, made again only
    when that set changes or the root moves, and saved in the session's work folder (``saved_file``), whose one owner it
    is. It says when it read each file a viewer or a page showed, so a file changed since is read again before it is
    answered, and it holds the *DocumentGraph* a viewer reads one file into on its own. Calls from several chats reach
    the one session at once; it is made under the reentrant lock its *SessionPractices* make the practices under, so a
    session never holds two."""

    def __init__(self, session: Session, practices: SessionPractices) -> None:
        self._session = session
        self._practices = practices
        self._graph: Graph | None = None
        self._graph_practices: frozenset[str] = frozenset()
        self._opened_at = 0.0
        # The graph a viewer reads one file into on its own, and the practices it was made with.
        self._alone: tuple[list[str], DocumentGraph] | None = None
        self._alone_lock = threading.Lock()
        # When the knowledge graph last read each file a viewer showed, by its modification time, and the graph it read
        # them into.
        self._held_reads: tuple[Graph | None, dict[Path, float]] = (None, {})
        self._held_lock = threading.Lock()
        # When the graph last read each file a page lists, for the graph view.
        self._listed_reads: dict[Path, float] = {}
        self._listed_lock = threading.Lock()

    @property
    def graph(self) -> Graph:
        """The graph of the practices the session holds (``SessionPractices.held``), opened on its root and made again
        when that set changes."""
        with self._practices.lock:
            held = frozenset(self._practices.held)
            if self._graph is None or held != self._graph_practices:
                self._graph = self._graph_of(held)
                self._graph_practices = held
                self._opened_at = time.time()
            return self._graph

    def _graph_of(self, held: frozenset[str]) -> Graph:
        """A graph of only the practices the session holds, created for it and saved in its work folder: a practice
        switched off for it is read into it only once an action works on it, and a graph saved anywhere else is not the
        session's."""
        session = self._session
        every = self._practices.every
        graph = Graph(every[key].guidance for key in every if key in held)
        graph.kept_in = session.work_folder
        graph.reads.open_saved(session.work_root)
        if session.overlays:
            graph.overlays = session.overlays
        return graph

    def overlay(self, overlays: list[str]) -> None:
        """Lay overlays on the graph at once when it has been made; a graph made later reads them from the session."""
        with self._practices.lock:
            if self._graph is not None:
                self._graph.overlays = list(overlays)

    def forget(self) -> None:
        """The graph was made on the session's old root or in its old work folder, so it is made again when next asked
        for."""
        with self._practices.lock:
            self._graph = None

    @property
    def saved_file(self) -> Path:
        """The graph file saved in the session's work folder."""
        return Path(self._session.work_folder) / GRAPH_FILE_NAME

    @property
    def last_read(self) -> float:
        """When the graph read the files it holds, for one no viewer has shown since: when it was opened, or when the
        graph it opened was saved, whichever is earlier."""
        saved = self.saved_file
        return min(self._opened_at, saved.stat().st_mtime) if saved.is_file() else self._opened_at

    @property
    def alone(self) -> DocumentGraph:
        """The graph a viewer reads one file into on its own, with its own instance of each practice the session works
        on, made again when that set changes."""
        working = sorted(self._practices.working)
        with self._alone_lock:
            if self._alone is None or self._alone[0] != working:
                self._alone = (working, DocumentGraph.of_practices(working))
            return self._alone[1]

    def holding(self, path: Path, is_held: bool) -> SavedGraph:
        """The file at path in the knowledge graph holding the whole working copy, so the rules that link files and
        practices hold. The file is read into the graph when the graph holds nothing of it (is_held false) or it changed
        since the graph last read it: since a viewer last showed it, or, before that, since the graph was opened or
        saved."""
        graph = self.graph
        graph.reads.hold_whole()
        modified = path.stat().st_mtime if path.is_file() else -1.0
        with self._held_lock:
            held, reads = self._held_reads
            if held is not graph:
                reads = {}
                self._held_reads = (graph, reads)
            is_current = is_held and modified <= reads.get(path, self.last_read)
            reads[path] = max(modified, time.time())
        if not is_current:
            graph.refresh([str(path)])
        return SavedGraph.from_graph(graph)

    def listed(self, paths: list[Path]) -> None:
        """The graph read the files at paths now, the files a page lists for its graph view."""
        read_at = time.time()
        with self._listed_lock:
            self._listed_reads = {path: read_at for path in paths}

    def as_it_is_now(self, path: Path) -> None:
        """Read the listed file at path into the graph again when it changed since the graph read it, so the lines a
        node covers are the file's lines as it is now. A file the graph view never listed, or one that has gone, is left
        as the graph holds it."""
        modified = path.stat().st_mtime if path.is_file() else -1.0
        with self._listed_lock:
            read_at = self._listed_reads.get(path)
            is_current = read_at is None or modified <= read_at
            if not is_current:
                self._listed_reads[path] = max(modified, time.time())
        if not is_current:
            self.graph.refresh([str(path)])
