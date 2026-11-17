"""PracticeOutputs - a session's one instance of each practice, and the knowledge graph of the practices it works on."""

from __future__ import annotations

import threading
from typing import TYPE_CHECKING

from harness.graph.graph import Graph
from harness.guidance.practice_catalogue import PRACTICE_CATALOGUE
from space.session.practice_session_output import PracticeSessionOutput

if TYPE_CHECKING:
    from space.session.session import Session


class PracticeOutputs:
    """*PracticeOutputs* are one session's instances of every practice, each working in that session, made once on its
    root, and the knowledge graph of the practices it works on, made again only when that set changes or the root moves.
    Calls from several chats reach the one session at once; the first to ask makes them and the others wait, so a
    session never holds two."""

    def __init__(self, session: Session) -> None:
        self._session = session
        self._outputs: dict[str, PracticeSessionOutput] | None = None
        self._graph: Graph | None = None
        self._graph_practices: frozenset[str] = frozenset()
        # Reentrant, because the graph asks for the practices while it is being made.
        self._lock = threading.RLock()

    @property
    def every(self) -> dict[str, PracticeSessionOutput]:
        """A new instance of every practice, by key, each working in the session: made once on its root."""
        with self._lock:
            if self._outputs is None:
                self._outputs = {practice.key: PracticeSessionOutput(practice, self._session) for practice in PRACTICE_CATALOGUE.create_all()}
                for output in self._outputs.values():
                    output.guidance.work_in(output)
            return self._outputs

    @property
    def working(self) -> list[str]:
        """The keys of the practices the session works on."""
        return [key for key, output in self.every.items() if output.enabled]

    @property
    def graph(self) -> Graph:
        """The graph of the practices the session works on, opened on its root and made again when that set changes."""
        with self._lock:
            working = frozenset(self.working)
            if self._graph is None or working != self._graph_practices:
                self._graph = self._graph_of(working)
                self._graph_practices = working
                self._session.file_graphs.opened()
            return self._graph

    def _graph_of(self, working: frozenset[str]) -> Graph:
        """A graph of only the practices the session works on, created for it and saved in its work folder: a practice
        turned off for it is never read into it, and a graph saved anywhere else is not the session's."""
        session = self._session
        graph = Graph(self.every[key].guidance for key in self.every if key in working)
        graph.kept_in = session.work_folder
        graph.reads.open_saved(session.work_root)
        if session.overlays:
            graph.overlays = session.overlays
        return graph

    def overlay(self, overlays: list[str]) -> None:
        """Lay overlays on the graph at once when it has been made; a graph made later reads them from the session."""
        with self._lock:
            if self._graph is not None:
                self._graph.overlays = list(overlays)

    def forget(self) -> None:
        """The practices and graph were made on the session's old root, so they are made again when next asked for."""
        with self._lock:
            self._outputs = None
            self._graph = None
