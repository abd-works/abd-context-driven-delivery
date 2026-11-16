"""What a graph reads, and when: the reads a call asks of a graph, each run alone. The graph makes its reads once and
keeps them (``graph.reads``); its MCP operations hand each call to them in one line."""

from __future__ import annotations

import threading
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING

from harness.agent_tools.progress import report_progress
from harness.graph.explorer import GraphLoaded
from harness.graph.graph_build import BuildStep, BuildTask, CheckedFiles
from harness.graph.load_scope import LoadScope

if TYPE_CHECKING:
    from harness.agent_tools.tool_call import ToolCall
    from harness.graph.graph import Graph


@dataclass(frozen=True)
class WorkingCopyRead:
    """A read of a working copy a call asks for: its folder, the source root of each practice under it, the folder the
    graph is saved in when it is not the working copy, the pattern overlays to apply, and whether to rebuild even when
    the saved graph holds what is asked."""

    folder: str
    practices: dict[str, str]
    database: str | None = None
    overlays: list[str] = field(default_factory=list)
    force: bool = False


@dataclass(frozen=True)
class FilesRead:
    """A read of only some files a call asks for: the folder they sit in, the practices that read them, the files or
    folders themselves, and the pattern overlays to apply."""

    folder: str
    practices: list[str]
    files: list[str]
    overlays: list[str] = field(default_factory=list)


class GraphReads:
    """The reads a call asks of one graph, which the graph makes once and keeps (``graph.reads``): open it on a folder,
    with or without its saved graph; load a working copy, its practices' session roots, or some files; refresh the
    files an action wrote; make sure it holds the whole working copy; and apply pattern overlays. A load, a refresh,
    and a write each run alone: calls in one session can arrive at once."""

    def __init__(self, graph: Graph) -> None:
        self._graph = graph
        self._changing = threading.RLock()

    def open(self, folder: Path) -> None:
        """Open the graph on folder with every practice it holds rooted there, holding no node yet."""
        graph = self._graph
        with self._changing:
            # Holding no node yet, the graph stands on none of the working copy until a load reads it.
            graph.scope = LoadScope(folder, [])
            graph.practices.choose({practice: folder for practice in graph.practices.held.values()})
            graph.practices.open_chosen()

    def open_saved(self, folder: Path) -> None:
        """Open the graph on folder, then read back the graph saved in its ``.context`` when there is one, each saved
        practice on the source root it was read from, with the violations it was saved with: a session opened again
        shows what was loaded in it before. Its rules run again on the next load or refresh, which a call makes and
        which builds where that call says; opening a session runs no build. A folder with nothing saved opens holding
        no node until a load reads it."""
        self.open(folder)
        graph = self._graph
        with self._changing:
            saved = graph.saved_file.read()
            if saved is None:
                return
            graph.overlays = list(saved.overlays)
            graph.practices.reopen(saved, folder)
            if saved.holds(graph.practices.roots_by_key, graph.overlays):
                graph.scope = LoadScope(folder)

    def working_copy(self, read: WorkingCopyRead, call: ToolCall | None) -> GraphLoaded:
        """Open each practice read names on its source root and build, from the saved graph when it holds them."""
        graph = self._graph
        with self._changing:
            graph.scope = LoadScope(Path(read.database or read.folder).resolve())
            graph.practices.choose({graph.practices.named(key): (Path(read.folder) / root).resolve() for key, root in read.practices.items()})
            graph.overlays = list(read.overlays)
            return graph.build.load(read.force, call)

    def practice_roots(self, call: ToolCall | None) -> GraphLoaded:
        """Open each practice the graph holds on the folder its session names for it, and build; a practice with no
        root, or whose folder is not written yet, is left out."""
        graph = self._graph
        with self._changing:
            roots = {practice: root for practice in graph.practices.held.values() if (root := practice.session_root) is not None and root.is_dir()}
            if not roots:
                return GraphLoaded("No practice root of a session is there to read, so nothing was loaded.")
            graph.scope = LoadScope(graph.scope.folder)
            graph.practices.choose(roots)
            return graph.build.load(False, call)

    def files(self, read: FilesRead, call: ToolCall | None) -> GraphLoaded:
        """Build each practice read names from only its files, as they are now, and run its rules on them."""
        graph = self._graph
        with self._changing:
            root = Path(read.folder).resolve()
            graph.scope = LoadScope.of_paths(root, read.files)
            graph.practices.choose({graph.practices.named(key): root for key in read.practices})
            graph.overlays = list(read.overlays)
            report_progress("Reading the edited files")
            graph.practices.open_chosen()
            graph.build.run(BuildTask(BuildStep.READ), call)
            return GraphLoaded(f"Loaded {len(graph.scope.edited_files or [])} edited files.")

    def refresh(self, paths: list[str], call: ToolCall | None) -> GraphLoaded:
        """Read again exactly the files at paths into the graph held in memory."""
        with self._changing:
            return self._graph.build.refresh(paths, call)

    def hold_whole(self, call: ToolCall | None = None) -> None:
        """Make sure the graph holds the whole working copy across every practice it holds, reading it, or the saved
        graph when that holds it, when it does not yet: a validate judges links across practices, which a graph holding
        only some files cannot."""
        graph = self._graph
        with self._changing:
            if graph.scope.over_whole or graph.scope.folder is None:
                return
            graph.scope = LoadScope(graph.scope.folder)
            graph.build.load(False, call)

    def refreshed(self, paths: list[str], checked: Path, call: ToolCall | None = None) -> None:
        """Refresh the graph with exactly the files at paths and write the nodes read from them, as they save, at
        checked, as one change: no other call's load or refresh comes between the two, so a call that checks the files
        it names sees the graph its own refresh left, whatever other calls in the session do at the same time. The build
        writes them, in its worker for a chat's call, so the server answering chats never serialises them."""
        with self._changing:
            self._graph.build.refresh(paths, call, CheckedFiles(paths, checked))

    def apply_overlays(self, overlays: list[str], call: ToolCall | None) -> Graph:
        """Apply pattern overlays and, when a folder is open with practices chosen, load it again with them; answer the
        graph, which now applies them."""
        graph = self._graph
        with self._changing:
            graph.overlays = list(overlays or [])
            if graph.scope.folder is not None and graph.practices.chosen:
                graph.scope = LoadScope(graph.scope.folder)
                graph.build.load(False, call)
        return graph
