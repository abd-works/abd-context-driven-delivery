"""GraphBuild, BuildOrder and WorkerBuild. A graph's build, run in a worker process of its own for a graph held by the
cdd server.

Every chat shares the cdd server's one interpreter. A graph build is minutes of CPU-bound Python, and run in that
interpreter it slows the event loop until the server stops accepting connections, so a build a chat's call asks for
runs in a worker process: the graph writes what it holds now and what to do as a *BuildOrder*, the worker reads the
working copy into a graph of its own and runs the rules, and the graph then holds what the worker saved. The order and
the answer are both *SavedGraph* documents, the shape ``graph.json`` keeps, so the worker's answer is what the server
would have read back from a saved graph.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import threading
import weakref
from collections.abc import Callable
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING

from harness.agent_tools.progress import report_progress
from harness.graph.explorer import GraphLoaded
from harness.graph.load_scope import LoadScope
from harness.graph.saved_graph import GraphChanges, SavedGraph

if TYPE_CHECKING:
    from harness.agent_tools.tool_call import ToolCall
    from harness.graph.graph import Graph

# The module a worker process runs, which carries out one order.
WORKER_MODULE = "harness.graph.graph_worker"
# How much of a failed worker's error output the failure names.
_ERROR_TAIL_CHARACTERS = 4000
# Windows' CREATE_NO_WINDOW: the worker opens no console window beside a windowless server.
_CREATE_NO_WINDOW = 0x08000000
# The part of a worker build the server does itself, writing what its graph holds into the order and reading the
# worker's answer back into its graph, is CPU-bound Python in the interpreter every chat shares. Builds take turns at
# it, so the event loop waits for one build's turn at most, never for several builds' at once.
_SERVER_TURN = threading.Lock()


class BuildStep(str, Enum):
    """What a build does with the graph it is given: read the working copy into it and run the rules (``read``); drop
    the nodes of the files in scope, read those files again, and run the rules (``refresh``); or only run the rules on
    what it holds (``check``), as a graph read back from ``graph.json`` does."""

    READ = "read"
    REFRESH = "refresh"
    CHECK = "check"


class GraphBuildFailed(RuntimeError):
    """The worker process building a graph exited with an error."""

    def __init__(self, exit_code: int, errors: str) -> None:
        super().__init__(f"the graph build's worker process exited with {exit_code}:\n{errors[-_ERROR_TAIL_CHARACTERS:]}")
        self.exit_code = exit_code
        self.errors = errors


class CheckedFiles:
    """The files a validate checks after a refresh, each a file or folder from a practice's source root, and the file
    the nodes read from them are written to, as they save: the build that refreshes the graph writes it, in the worker
    for a chat's call, so the server answering chats never serialises those nodes."""

    def __init__(self, paths: list[str], file: Path) -> None:
        self.paths = list(paths)
        self.file = Path(file)

    @property
    def document(self) -> dict:
        return {"paths": self.paths, "file": str(self.file)}

    def write(self, graph: Graph) -> None:
        """Write the nodes graph read from these files, the edges between them, and their violations."""
        self.file.parent.mkdir(parents=True, exist_ok=True)
        self.file.write_text(SavedGraph.from_graph(graph, self.paths).text, encoding="utf-8")


class BuildOrder:
    """One build as a worker process carries it out: the step, the scope it reads (the folder the graph loads, and the
    edited files a load is limited to), each chosen practice's source root, the pattern overlays, the graph as it is
    before the step, the modules that register the practices and patterns the graph holds, which the worker imports so
    its catalogues hold the same classes, whether the worker saves the graph it built in the folder's ``graph.json``,
    and the files a validate checks, whose nodes the worker writes for it.

    The graph before the step is written into the order (a *SavedGraph*), or named by the file of the worker's last
    answer when the graph holds exactly what that answer says (its path): the server then writes no graph of its own,
    and the worker answers a refresh with what it changed (``GraphChanges``), which is all the server reads back."""

    def __init__(
        self,
        step: BuildStep,
        scope: LoadScope,
        roots: dict[str, Path],
        overlays: list[str],
        before: SavedGraph | Path,
        modules: list[str],
        saves: bool = False,
        checked: CheckedFiles | None = None,
    ) -> None:
        self.step = BuildStep(step)
        self.scope = scope
        self.roots = dict(roots)
        self.overlays = list(overlays)
        self._before = before
        self.modules = list(modules)
        self.saves = saves
        self.checked = checked

    @classmethod
    def from_text(cls, text: str) -> BuildOrder:
        document = json.loads(text)
        named = document.get("scope")
        scope = LoadScope(Path(document["folder"]) if document.get("folder") else None, None if named is None else [Path(path) for path in named])
        embedded = document.get("state")
        before = SavedGraph.from_document(embedded) if embedded is not None else Path(document["state_file"])
        roots = {key: Path(root) for key, root in (document.get("roots") or {}).items()}
        return cls(
            BuildStep(document["step"]), scope, roots, list(document.get("overlays") or []), before, list(document.get("modules") or []),
            bool(document.get("saves")), cls._checked_in(document.get("checked")),
        )

    @staticmethod
    def _checked_in(document: dict | None) -> CheckedFiles | None:
        return None if document is None else CheckedFiles(list(document["paths"]), Path(document["file"]))

    @property
    def state(self) -> SavedGraph:
        """The graph before the step: the one written into the order, else the one its state file holds, read anew
        each time it is asked for, so a build that changes the graph it read leaves this one as it was."""
        if isinstance(self._before, SavedGraph):
            return self._before
        return SavedGraph.from_file(self._before)

    @property
    def answers_changes(self) -> bool:
        """Whether the worker answers what the step changed: for a refresh of a graph the server holds as the worker's
        last answer said, whose nodes are all plain nodes the changes can be made to."""
        return self.step is BuildStep.REFRESH and isinstance(self._before, Path)

    def changes(self, built: SavedGraph) -> GraphChanges | None:
        """What the step changed in the graph it was given, when the order asks for it and the step kept the graph's
        practices, roots, and overlays."""
        return GraphChanges.between(self.state, built) if self.answers_changes else None

    @property
    def text(self) -> str:
        before = self._before
        return json.dumps(
            {
                "step": self.step.value,
                "folder": "" if self.scope.folder is None else str(self.scope.folder),
                "roots": {key: str(root) for key, root in self.roots.items()},
                "overlays": self.overlays,
                "scope": None if self.scope.named is None else [str(path) for path in self.scope.named],
                "state": before.document if isinstance(before, SavedGraph) else None,
                "state_file": str(before) if isinstance(before, Path) else "",
                "modules": self.modules,
                "saves": self.saves,
                "checked": None if self.checked is None else self.checked.document,
            },
            separators=(",", ":"),
        )


class HeldAnswer:
    """The file of the last answer a worker gave one graph, while the graph holds exactly what it says. It counts every
    change to what the graph holds: the count when the graph took the answer names the graph as it was then, and any
    change since makes the file stale. The files live in a folder of the graph's own, removed with it."""

    def __init__(self) -> None:
        self._folder: Path | None = None
        self._file: Path | None = None
        self._revision = 0
        self._taken_at = -1
        self._count = 0

    def changed(self) -> None:
        """Count a change to what the graph holds."""
        self._revision += 1

    def next_file(self) -> Path:
        """A file of this graph's for the next worker's answer."""
        if self._folder is None:
            self._folder = Path(tempfile.mkdtemp(prefix="cdd-graph-answers-"))
            weakref.finalize(self, shutil.rmtree, str(self._folder), True)
        self._count += 1
        return self._folder / f"answer-{self._count}.json"

    def keep(self, file: Path) -> None:
        """The graph now holds what file says; the answer it held before is no longer needed."""
        if self._file is not None and self._file != file:
            self._file.unlink(missing_ok=True)
        self._file = file
        self._taken_at = self._revision

    @property
    def file(self) -> Path | None:
        """The answer the graph holds, when it has not changed since it took it."""
        if self._file is None or self._taken_at != self._revision or not self._file.is_file():
            return None
        return self._file


class WorkerBuild:
    """One order carried out by a worker process: started with this interpreter and this import path, it reports its
    progress one line at a time, which goes on to report_progress, writes the graph it built to the answer file it is
    given, and, for a refresh the order asks it of, what it changed to a file of its own."""

    def __init__(self, report_progress: Callable[[str], None]) -> None:
        self._report_progress = report_progress

    def carry_out(
        self,
        ordered: Callable[[], BuildOrder],
        answer: Path,
        hold: Callable[[SavedGraph], None],
        take: Callable[[GraphChanges], None],
    ) -> None:
        """Make the order and write it, run the worker on it, which writes the graph it built to answer, then hold that
        graph, or take only the changes the worker answers when it answers them; ``GraphBuildFailed`` when the worker
        exits with an error, and then nothing is held and answer is gone. Making the order and holding the answer each
        take the server's turn; the worker runs while other builds take theirs."""
        with tempfile.TemporaryDirectory(prefix="cdd-graph-build-") as folder:
            order_file = Path(folder) / "order.json"
            changes_file = Path(folder) / "changes.json"
            errors_file = Path(folder) / "errors.txt"
            with _SERVER_TURN:
                order_file.write_text(ordered().text, encoding="utf-8")
            with open(errors_file, "w", encoding="utf-8") as errors:
                exit_code = self._run([str(order_file), str(answer), str(changes_file)], errors)
            if exit_code != 0:
                answer.unlink(missing_ok=True)
                raise GraphBuildFailed(exit_code, errors_file.read_text(encoding="utf-8", errors="replace"))
            with _SERVER_TURN:
                if changes_file.is_file():
                    take(GraphChanges.from_text(changes_file.read_text(encoding="utf-8")))
                else:
                    hold(SavedGraph.from_file(answer))

    def _run(self, arguments: list[str], errors) -> int:
        process = subprocess.Popen(
            [sys.executable, "-m", WORKER_MODULE, *arguments],
            cwd=os.getcwd(),
            env={**os.environ, "PYTHONPATH": os.pathsep.join(path for path in sys.path if path), "PYTHONIOENCODING": "utf-8"},
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=errors,
            encoding="utf-8",
            errors="replace",
            creationflags=_CREATE_NO_WINDOW if sys.platform == "win32" else 0,
        )
        assert process.stdout is not None
        for line in process.stdout:
            message = line.rstrip("\n")
            if message:
                self._report_progress(message)
        return process.wait()


class GraphBuild:
    """The build of one graph, which the graph makes once and keeps (``graph.build``): a load of a working copy, or of
    the saved graph that holds it, a load of the files being edited, a refresh of the files an action wrote, or a run of
    the rules on what the graph holds. For a call the cdd server answers for a chat (``call.answers_a_chat``) a worker
    process carries the build out, and the graph then holds what the worker built: a build is minutes of CPU-bound
    Python, and in the server's interpreter it would keep the server from answering every other chat. The graph changes
    only once the worker answers, so a build that fails leaves it holding what it held. Any other call, or none, builds
    in its own process. The build keeps the file of the worker's last answer and counts every change to what the graph
    holds, so the next order names that file while the graph has not changed since."""

    def __init__(self, graph: Graph) -> None:
        self.graph = graph
        self._answer = HeldAnswer()

    def changed(self) -> None:
        """Count a change to what the graph holds, so the file of a worker's answer stops standing for it."""
        self._answer.changed()

    def load(self, force: bool, call: ToolCall | None) -> GraphLoaded:
        """Read each chosen practice from its root, with the graph's overlays: from the saved graph when it holds every
        one of them on the same root with the same overlays and the load is not forced, else from the working copy,
        which is then saved."""
        graph = self.graph
        report_progress("Checking the saved graph")
        saved = None if force else graph.saved_file.holding(graph.practices.roots_by_key, graph.overlays)
        if saved is not None:
            report_progress("Loading the saved graph")
            self.run(BuildStep.CHECK, call, state=saved.of_practices(list(graph.practices.roots_by_key)))
            return GraphLoaded("Loaded the saved graph.")
        report_progress("Scanning the folder")
        graph.practices.open_chosen()
        self.run(BuildStep.READ, call, saves=True)
        return GraphLoaded("Loaded the working copies.")

    def refresh(self, paths: list[str], call: ToolCall | None, checked: CheckedFiles | None = None) -> GraphLoaded:
        """Read again exactly the files at paths in the graph's folder; with checked, write the nodes read from the files
        it names, whether or not anything was refreshed."""
        graph = self.graph
        scope = graph.scope.refreshing(paths)
        if scope.named and graph.practices.chosen:
            report_progress(f"Refreshing {len(scope.named)} files")
            graph.scope = scope
            self.run(BuildStep.REFRESH, call, checked=checked)
            return GraphLoaded(f"Refreshed {len(scope.named)} files.")
        if checked is not None:
            checked.write(graph)
        if scope.folder is None or not graph.practices.chosen:
            return GraphLoaded("No graph is open, so nothing was refreshed.")
        return GraphLoaded("None of those files is in the graph's folder, so nothing was refreshed.")

    def run(self, step: BuildStep, call: ToolCall | None, state: SavedGraph | None = None, saves: bool = False, checked: CheckedFiles | None = None) -> None:
        """Carry step out on the graph's scope, from state when one is given, else from what the graph holds now; save
        the graph after when saves is set, and write the checked files' nodes when checked names them. A call that
        answers a chat has a worker process carry it out."""
        if call is not None and call.answers_a_chat:
            answer = self._answer.next_file()
            WorkerBuild(report_progress).carry_out(lambda: self._order(step, state, saves, checked), answer, self._hold, self.graph.practices.take)
            self._answer.keep(answer)
            return
        if state is not None:
            self._hold(state)
        self._carry_out(step)
        self._finish(saves, checked)

    def carry_out(self, order: BuildOrder) -> SavedGraph:
        """Carry order out on the graph, as a worker process does for a graph the cdd server holds, save it and write
        the checked files' nodes when the order says, and answer the graph as it is then. The worker writes both, so
        the server never serialises the graph it built a second time."""
        graph = self.graph
        graph.scope = order.scope
        held = graph.practices.held
        graph.practices.choose({held[key]: root for key, root in order.roots.items()})
        graph.overlays = order.overlays
        graph.schema_edges.syncs = False
        self._hold(order.state)
        self._carry_out(order.step)
        self._finish(order.saves, order.checked)
        return SavedGraph.from_graph(graph)

    def _hold(self, saved: SavedGraph) -> None:
        self.graph.practices.hold(saved, self.graph.scope.folder)

    def _finish(self, saves: bool, checked: CheckedFiles | None) -> None:
        if saves:
            report_progress("Saving the graph")
            self.graph.save_json()
        if checked is not None:
            checked.write(self.graph)

    def _order(self, step: BuildStep, state: SavedGraph | None, saves: bool, checked: CheckedFiles | None) -> BuildOrder:
        """step as a worker carries it out: from state when one is given, else from what the graph holds now, which
        is the file of the worker's last answer while the graph has not changed since it took it, so the server writes
        no graph of its own."""
        graph = self.graph
        before = state if state is not None else self._answer.file or SavedGraph.from_graph(graph)
        return BuildOrder(step, graph.scope, graph.practices.roots_by_key, graph.overlays, before, self._registering_modules(), saves, checked)

    def _carry_out(self, step: BuildStep) -> None:
        """Run step on what the graph holds, in this process. A read fills the open practices from the working copy;
        a refresh first drops the nodes read from the files in scope, and every rule's findings, since a rule over a
        whole practice can change its finding on a node no file in scope holds. Both run every rule and rebuild each
        practice's tree. A working copy's edges are the ones its practices read; its parsed objects never add schema
        edges of their own. A check only runs the rules on what the graph holds."""
        self.changed()
        practices = self.graph.practices
        if step is BuildStep.CHECK:
            practices.check()
            return
        self.graph.schema_edges.syncs = False
        if step is BuildStep.REFRESH:
            practices.forget(self.graph.scope.named or [])
        self._read_working_copy()
        practices.rebuild_trees()

    def _read_working_copy(self) -> None:
        """Read every open practice from the loaded folder, each after the practices it reads while it reads its own;
        link them once all are read; add the applied overlays' nodes; then run every practice's rules."""
        graph = self.graph
        if graph.scope.folder is None:
            return
        practices = graph.practices.in_reading_order()
        for practice in practices:
            practice.reading.read()
        for overlay in graph.applied_patterns.graph_overlays:
            overlay.read(graph)
        self._offer_overlay_types()
        graph.practices.check()

    def _offer_overlay_types(self) -> None:
        """Offer the overlay schemas' node and relationship types in the filter lists before rules run."""
        overlays = self.graph.applied_patterns.graph_overlays
        if overlays:
            for practice in self.graph.practices.opened.values():
                practice.reading.in_graph.rule_run.offer_overlay_types(overlays)

    def _registering_modules(self) -> list[str]:
        """The modules that define the practices the graph holds and the patterns it applies; importing them registers
        them with their catalogues, so a worker process holds the same classes."""
        held = [*self.graph.practices.held.values(), *self.graph.applied_patterns.patterns]
        return sorted({type(item).__module__ for item in held})
