"""What a graph reads, and when: the reads a call asks of a graph, each run alone. The graph makes its reads once and
keeps them (``graph.reads``); its MCP operations choose what to read and hand the read to them. Whether a build runs
apart, in a worker process, is said by the graph's toolset from the call it answers, so no read takes the call."""

from __future__ import annotations

import threading
from pathlib import Path
from typing import TYPE_CHECKING

from harness.agent_tools.progress import report_progress
from harness.graph.explorer import GraphLoaded
from harness.graph.graph_build import BuildStep, BuildTask, CheckedFiles
from harness.graph.load_scope import LoadScope

if TYPE_CHECKING:
    from harness.graph.graph import Graph


class GraphReads:
    """The reads a call asks of one graph, which the graph makes once and keeps (``graph.reads``): open it on a folder,
    with or without its saved graph; load the practices chosen, from the saved graph when it holds them; read only the
    files being edited; load its practices' session roots; refresh the files an action wrote; make sure it holds the
    whole working copy; and apply pattern overlays. A load, a refresh, and a write each run alone: calls in one session
    can arrive at once, so a caller that chooses what to read first holds ``changing`` while it chooses and reads."""

    def __init__(self, graph: Graph) -> None:
        self._graph = graph
        self.changing = threading.RLock()

    def open(self, folder: Path) -> None:
        """Open the graph on folder with every practice it holds rooted there, holding no node yet."""
        graph = self._graph
        with self.changing:
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
        with self.changing:
            saved = graph.saved_file.read()
            if saved is None:
                return
            graph.overlays = list(saved.overlays)
            graph.practices.reopen(saved)
            if saved.holds(graph.practices.roots_by_key, graph.overlays):
                graph.scope = LoadScope(folder)

    def load(self, force: bool, apart: bool) -> GraphLoaded:
        """Read each chosen practice from its root, with the graph's overlays: from the saved graph when it holds every
        one of them on the same root with the same overlays and the load is not forced, else from the working copy,
        which is then saved; in a worker process when apart."""
        graph = self._graph
        with self.changing:
            report_progress("Checking the saved graph")
            saved = None if force else graph.saved_file.holding(graph.practices.roots_by_key, graph.overlays)
            if saved is not None:
                report_progress("Loading the saved graph")
                graph.build.run(BuildTask(BuildStep.CHECK, apart=apart), state=saved.of_practices(list(graph.practices.roots_by_key)))
                return GraphLoaded("Loaded the saved graph.")
            report_progress("Scanning the folder")
            graph.practices.open_chosen()
            graph.build.run(BuildTask(BuildStep.READ, saves=True, apart=apart))
            return GraphLoaded("Loaded the working copies.")

    def edited_files(self, apart: bool) -> GraphLoaded:
        """Build each chosen practice from only the files the graph's scope names, as they are now, and run its rules
        on them; the saved graph is never touched."""
        graph = self._graph
        with self.changing:
            report_progress("Reading the edited files")
            graph.practices.open_chosen()
            graph.build.run(BuildTask(BuildStep.READ, apart=apart))
            return GraphLoaded(f"Loaded {len(graph.scope.edited_files or [])} edited files.")

    def practice_roots(self, apart: bool) -> GraphLoaded:
        """Open each practice the graph holds on the folder its session names for it, and build; a practice with no
        root, or whose folder is not written yet, is left out."""
        graph = self._graph
        with self.changing:
            roots = {practice: root for practice in graph.practices.held.values() if (root := practice.session_root) is not None and root.is_dir()}
            if not roots:
                return GraphLoaded("No practice root of a session is there to read, so nothing was loaded.")
            graph.scope = LoadScope(graph.scope.folder)
            graph.practices.choose(roots)
            return self.load(False, apart)

    def refresh(self, paths: list[str], apart: bool) -> GraphLoaded:
        """Read again exactly the files at paths into the graph held in memory."""
        with self.changing:
            return self._refresh(paths, BuildTask(BuildStep.REFRESH, apart=apart))

    def hold_whole(self, apart: bool = False) -> None:
        """Make sure the graph holds the whole working copy across every practice it holds, reading it, or the saved
        graph when that holds it, when it does not yet: a validate judges links across practices, which a graph holding
        only some files cannot."""
        graph = self._graph
        with self.changing:
            if graph.scope.over_whole or graph.scope.folder is None:
                return
            graph.scope = LoadScope(graph.scope.folder)
            self.load(False, apart)

    def refreshed(self, paths: list[str], checked: Path, apart: bool = False) -> None:
        """Refresh the graph with exactly the files at paths and write the nodes read from them, as they save, at
        checked, as one change: no other call's load or refresh comes between the two, so a call that checks the files
        it names sees the graph its own refresh left, whatever other calls in the session do at the same time. The build
        writes them, in its worker when apart, so the server answering chats never serialises them."""
        with self.changing:
            self._refresh(paths, BuildTask(BuildStep.REFRESH, checked=CheckedFiles(paths, checked), apart=apart))

    def apply_overlays(self, overlays: list[str], apart: bool) -> Graph:
        """Apply pattern overlays and, when a folder is open with practices chosen, load it again with them; answer the
        graph, which now applies them."""
        graph = self._graph
        with self.changing:
            graph.overlays = list(overlays or [])
            if graph.scope.folder is not None and graph.practices.chosen:
                graph.scope = LoadScope(graph.scope.folder)
                self.load(False, apart)
        return graph

    def _refresh(self, paths: list[str], task: BuildTask) -> GraphLoaded:
        """Read again the files at paths in the graph's folder, and the files a practice reads together with them; when
        task checks files, write the nodes read from the files it names, whether or not anything was refreshed."""
        graph = self._graph
        scope = graph.scope.refreshing(paths)
        if scope.named and graph.practices.chosen:
            report_progress(f"Refreshing {len(scope.named)} files")
            graph.scope = scope.also_naming(self._read_with(scope.named))
            graph.build.run(task)
            return GraphLoaded(f"Refreshed {len(scope.named)} files.")
        if task.checked is not None:
            task.checked.write(graph)
        if scope.folder is None or not graph.practices.chosen:
            return GraphLoaded("No graph is open, so nothing was refreshed.")
        return GraphLoaded("None of those files is in the graph's folder, so nothing was refreshed.")

    def _read_with(self, files: list[Path]) -> list[Path]:
        """The files each chosen practice reads together with files, which a refresh of files then reads again too: a
        practice that builds one tree from several files, read from only some of them, would leave a different graph
        than the load that read them all."""
        return [path for practice in self._graph.practices.chosen for path in practice.reading.read_with(files)]
