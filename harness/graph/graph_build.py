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
import shutil
import tempfile
import threading
import weakref
from collections.abc import Callable
from enum import Enum
from pathlib import Path
from typing import IO, TYPE_CHECKING, TypedDict

from harness.agent_tools.progress import report_progress
from harness.agent_tools.worker_process import WorkerProcess
from harness.graph.explorer import GraphLoaded
from harness.graph.file_lines import BuildReads
from harness.graph.load_scope import LoadScope
from harness.graph.saved_graph import GraphChanges, GraphDocument, SavedGraph

if TYPE_CHECKING:
    from harness.agent_tools.tool_call import ToolCall
    from harness.graph.graph import Graph
    from harness.guidance.guidance import PracticeGuidance

# The module a worker process runs, which carries out one order.
WORKER_MODULE = "harness.graph.graph_worker"
# How much of a failed worker's error output the failure names.
_ERROR_TAIL_CHARACTERS = 4000
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


class CheckedFilesDocument(TypedDict):
    """The checked files as an order writes them for the worker."""

    paths: list[str]
    file: str


class CheckedFiles:
    """The files a validate checks after a refresh, each a file or folder from a practice's source root, and the file
    the nodes read from them are written to, as they save: the build that refreshes the graph writes it, in the worker
    for a chat's call, so the server answering chats never serialises those nodes."""

    def __init__(self, paths: list[str], file: Path) -> None:
        self.paths = list(paths)
        self.file = Path(file)

    @classmethod
    def from_document(cls, document: CheckedFilesDocument | None) -> CheckedFiles | None:
        """The checked files an order names; none when it names none."""
        return None if document is None else cls(list(document["paths"]), Path(document["file"]))

    @property
    def document(self) -> CheckedFilesDocument:
        return {"paths": self.paths, "file": str(self.file)}

    def write(self, graph: Graph) -> None:
        """Write the nodes graph read from these files, the edges between them, and their violations."""
        self.file.parent.mkdir(parents=True, exist_ok=True)
        self.file.write_text(SavedGraph.from_graph(graph, self.paths).text, encoding="utf-8")


class BuildTaskDocument(TypedDict):
    """A build's task as an order writes it for the worker."""

    step: str
    saves: bool
    checked: CheckedFilesDocument | None


class BuildTask:
    """What one build does: its step, then whether it saves the graph it built in its folder's ``graph.json`` (saves)
    and the files a validate checks, whose nodes it writes for it (checked)."""

    def __init__(self, step: BuildStep, saves: bool = False, checked: CheckedFiles | None = None) -> None:
        self.step = BuildStep(step)
        self.saves = saves
        self.checked = checked

    @classmethod
    def from_document(cls, document: BuildTaskDocument) -> BuildTask:
        return cls(BuildStep(document["step"]), bool(document.get("saves")), CheckedFiles.from_document(document.get("checked")))

    @property
    def document(self) -> BuildTaskDocument:
        return {"step": self.step.value, "saves": self.saves, "checked": None if self.checked is None else self.checked.document}


class BuildOrderDocument(TypedDict):
    """A build order as the server writes it for the worker: the task, the scope the worker reads (its folder, the files
    it is limited to, and whether it stands on the whole working copy), each chosen practice's source root, the pattern
    overlays, the graph before the step (written in, or named by the file of the worker's last answer), and the
    modules that register the practices and patterns the graph holds."""

    task: BuildTaskDocument
    folder: str
    named: list[str] | None
    over_whole: bool
    roots: dict[str, str]
    overlays: list[str]
    state: GraphDocument | None
    state_file: str
    modules: list[str]


class BuildOrder:
    """One build as a worker process carries it out, read from the document the server writes for it: the task, the
    scope it reads (the folder the graph loads, and the edited files a load is limited to), each chosen practice's
    source root, the pattern overlays, the graph as it is before the step, and the modules that register the practices
    and patterns the graph holds, which the worker imports so its catalogues hold the same classes.

    The graph before the step is written into the order (a *SavedGraph*), or named by the file of the worker's last
    answer when the graph holds exactly what that answer says (its path): the server then writes no graph of its own,
    and the worker answers a refresh with what it changed (``GraphChanges``), which is all the server reads back."""

    def __init__(self, document: BuildOrderDocument) -> None:
        self._document = document

    @classmethod
    def from_graph(cls, graph: Graph, task: BuildTask, before: SavedGraph | Path) -> BuildOrder:
        """task as a worker carries it out on what graph is set to now, from before: the graph written in, or the file
        that holds it."""
        scope = graph.scope
        return cls({
            "task": task.document,
            "folder": "" if scope.folder is None else str(scope.folder),
            "named": None if scope.named is None else [str(path) for path in scope.named],
            "over_whole": scope.over_whole,
            "roots": {key: str(root) for key, root in graph.practices.roots_by_key.items()},
            "overlays": list(graph.overlays),
            "state": before.document if isinstance(before, SavedGraph) else None,
            "state_file": str(before) if isinstance(before, Path) else "",
            "modules": sorted({type(item).__module__ for item in [*graph.practices.held.values(), *graph.applied_patterns.patterns]}),
        })

    @classmethod
    def from_text(cls, text: str) -> BuildOrder:
        return cls(json.loads(text))

    @property
    def task(self) -> BuildTask:
        return BuildTask.from_document(self._document["task"])

    @property
    def scope(self) -> LoadScope:
        document = self._document
        named = document.get("named")
        folder = Path(document["folder"]) if document.get("folder") else None
        return LoadScope(folder, None if named is None else [Path(path) for path in named], over_whole=bool(document.get("over_whole")))

    @property
    def roots(self) -> dict[str, Path]:
        """Each chosen practice's source root, by the practice's key."""
        return {key: Path(root) for key, root in (self._document.get("roots") or {}).items()}

    @property
    def overlays(self) -> list[str]:
        return list(self._document.get("overlays") or [])

    @property
    def modules(self) -> list[str]:
        return list(self._document.get("modules") or [])

    @property
    def state(self) -> SavedGraph:
        """The graph before the step: the one written into the order, else the one its state file holds, read anew
        each time it is asked for, so a build that changes the graph it read leaves this one as it was."""
        embedded = self._document.get("state")
        if embedded is not None:
            return SavedGraph.from_document(embedded)
        return SavedGraph.from_file(Path(self._document["state_file"]))

    @property
    def answers_changes(self) -> bool:
        """Whether the worker answers what the step changed: for a refresh of a graph the server holds as the worker's
        last answer said, whose nodes are all plain nodes the changes can be made to."""
        return self.task.step is BuildStep.REFRESH and self._document.get("state") is None

    def changes(self, built: SavedGraph) -> GraphChanges | None:
        """What the step changed in the graph it was given, when the order asks for it and the step kept the graph's
        practices, roots, and overlays."""
        return GraphChanges.between(self.state, built) if self.answers_changes else None

    @property
    def text(self) -> str:
        return json.dumps(self._document, separators=(",", ":"))


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
    """One order carried out by a worker process (*WorkerProcess*), which reports its progress as it goes, writes the graph it built to the answer file it is
    given, and, for a refresh the order asks it of, what it changed to a file of its own. The graph the order was made
    for holds what the worker answers."""

    def __init__(self, graph: Graph) -> None:
        self._graph = graph

    def carry_out(self, ordered: Callable[[], BuildOrder], answer: Path) -> None:
        """Make the order and write it, run the worker on it, which writes the graph it built to answer, then have the
        graph hold that graph, or take only the changes the worker answers when it answers them; ``GraphBuildFailed``
        when the worker exits with an error, and then nothing is held and answer is gone. Making the order and holding
        the answer each take the server's turn; the worker runs while other builds take theirs."""
        with tempfile.TemporaryDirectory(prefix="cdd-graph-build-") as folder:
            order_file, changes_file, errors_file = (Path(folder) / name for name in ("order.json", "changes.json", "errors.txt"))
            with _SERVER_TURN:
                order_file.write_text(ordered().text, encoding="utf-8")
            with open(errors_file, "w", encoding="utf-8") as errors:
                exit_code = self._run([str(order_file), str(answer), str(changes_file)], errors)
            if exit_code != 0:
                answer.unlink(missing_ok=True)
                raise GraphBuildFailed(exit_code, errors_file.read_text(encoding="utf-8", errors="replace"))
            with _SERVER_TURN:
                self._take_answer(answer, changes_file)

    def _take_answer(self, answer: Path, changes_file: Path) -> None:
        """Have the graph take the changes the worker answered, when it answered them, else hold the graph it built."""
        if changes_file.is_file():
            self._take(GraphChanges.from_text(changes_file.read_text(encoding="utf-8")))
        else:
            self._graph.practices.hold(SavedGraph.from_file(answer), self._graph.scope.folder)

    def _take(self, changes: GraphChanges) -> None:
        """Change what the open practices hold as a worker's changes say: every practice's nodes first, then the edges,
        which may cross practices, and the violations; then each changed practice's tree. The graph then holds what the
        worker's whole answer says, without reading it back."""
        held = self._graph.practices.held
        changed = {held[key]: record for key, record in changes.practices.items() if key in held and not record.is_empty}
        for practice, record in changed.items():
            practice.reading.in_graph.restore.changes(record)
        for practice, record in changed.items():
            practice.reading.in_graph.restore.links(record)
        for practice in changed:
            practice.reading.in_graph.loading.put_in_source_order()
            practice.reading.in_graph.root.tree.rebuild()

    def _run(self, arguments: list[str], errors: IO[str]) -> int:
        return WorkerProcess(WORKER_MODULE).run(arguments, errors)


class GraphBuild:
    """The build of one graph, which the graph makes once and keeps (``graph.build``): a load of a working copy, or of
    the saved graph that holds it, a load of the files being edited, a refresh of the files an action wrote, or a run of
    the rules on what the graph holds. For a call the cdd server answers for a chat (``call.request.answers_a_chat``) a worker
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
            self.run(BuildTask(BuildStep.CHECK), call, state=saved.of_practices(list(graph.practices.roots_by_key)))
            return GraphLoaded("Loaded the saved graph.")
        report_progress("Scanning the folder")
        graph.practices.open_chosen()
        self.run(BuildTask(BuildStep.READ, saves=True), call)
        return GraphLoaded("Loaded the working copies.")

    def refresh(self, paths: list[str], call: ToolCall | None, checked: CheckedFiles | None = None) -> GraphLoaded:
        """Read again exactly the files at paths in the graph's folder; with checked, write the nodes read from the files
        it names, whether or not anything was refreshed."""
        graph = self.graph
        scope = graph.scope.refreshing(paths)
        if scope.named and graph.practices.chosen:
            report_progress(f"Refreshing {len(scope.named)} files")
            graph.scope = scope
            self.run(BuildTask(BuildStep.REFRESH, checked=checked), call)
            return GraphLoaded(f"Refreshed {len(scope.named)} files.")
        if checked is not None:
            checked.write(graph)
        if scope.folder is None or not graph.practices.chosen:
            return GraphLoaded("No graph is open, so nothing was refreshed.")
        return GraphLoaded("None of those files is in the graph's folder, so nothing was refreshed.")

    def run(self, task: BuildTask, call: ToolCall | None, state: SavedGraph | None = None) -> None:
        """Carry task out on the graph's scope, from state when one is given, else from what the graph holds now. A call
        that answers a chat has a worker process carry it out."""
        if call is not None and call.request.answers_a_chat:
            answer = self._answer.next_file()
            WorkerBuild(self.graph).carry_out(lambda: self._order(task, state), answer)
            self._answer.keep(answer)
            return
        with BuildReads():
            if state is not None:
                self._hold(state)
            self._carry_out(task.step)
            self._finish(task)

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
        task = order.task
        with BuildReads():
            self._hold(order.state)
            self._carry_out(task.step)
            self._finish(task)
            return SavedGraph.from_graph(graph)

    def _hold(self, saved: SavedGraph) -> None:
        self.graph.practices.hold(saved, self.graph.scope.folder)

    def _finish(self, task: BuildTask) -> None:
        if task.saves:
            report_progress("Saving the graph")
            self.graph.save_json()
        if task.checked is not None:
            task.checked.write(self.graph)

    def _order(self, task: BuildTask, state: SavedGraph | None) -> BuildOrder:
        """task as a worker carries it out: from state when one is given, else from what the graph holds now, which
        is the file of the worker's last answer while the graph has not changed since it took it, so the server writes
        no graph of its own."""
        graph = self.graph
        return BuildOrder.from_graph(graph, task, state if state is not None else self._answer.file or SavedGraph.from_graph(graph))

    def _carry_out(self, step: BuildStep) -> None:
        """Run step on what the graph holds, in this process. A read fills the open practices from the working copy;
        a refresh first drops the nodes read from the files in scope, and every rule's findings, since a rule over a
        whole practice can change its finding on a node no file in scope holds. Both run every rule and rebuild each
        practice's tree. A working copy's edges are the ones its practices read; its parsed objects never add schema
        edges of their own. A check only runs the rules on what the graph holds."""
        self.changed()
        if step is BuildStep.CHECK:
            self._check()
            return
        self.graph.schema_edges.syncs = False
        if step is BuildStep.REFRESH:
            self._forget(self.graph.scope.named or [])
        self._read_working_copy()
        self.graph.practices.rebuild_trees()

    def _forget(self, files: list[Path]) -> None:
        """Drop the nodes read from files in every open practice, every edge that joins one of them, and every rule's
        findings, so a refresh reads those files again from nothing."""
        opened = self.graph.practices.opened.values()
        dropped: set[int] = set()
        for practice in opened:
            dropped |= practice.reading.in_graph.loading.forget_files(files)
        for practice in opened:
            practice.reading.in_graph.edge_index.drop(lambda edge: id(edge.parent) in dropped or id(edge.child) in dropped)
            practice.reading.in_graph.rule_run.renew()

    def _in_reading_order(self) -> list[PracticeGuidance]:
        """The open practices, each after the practices it reads while it reads its own."""
        opened = self.graph.practices.opened
        ordered: list[PracticeGuidance] = []

        def place(practice: PracticeGuidance) -> None:
            if practice in ordered:
                return
            for earlier in practice.reading.reads_after:
                if earlier in opened:
                    place(opened[earlier])
            ordered.append(practice)

        for practice in list(opened.values()):
            place(practice)
        return ordered

    def _check(self) -> None:
        """Put every open practice's nodes in source order, as a fresh build reads them, and run its graph rules: a rule
        that reports the first of two nodes then reports the same node whichever build read them."""
        opened = self.graph.practices.opened.values()
        for practice in opened:
            practice.reading.in_graph.loading.put_in_source_order()
        for practice in opened:
            practice.reading.in_graph.rule_run.check()

    def _read_working_copy(self) -> None:
        """Read every open practice from the loaded folder, each after the practices it reads while it reads its own;
        link them once all are read; add the applied overlays' nodes; then run every practice's rules."""
        graph = self.graph
        if graph.scope.folder is None:
            return
        practices = self._in_reading_order()
        for practice in practices:
            practice.reading.read()
        for overlay in [*graph.applied_patterns.graph_overlays, *graph.applied_patterns.supplement_overlays_of(practices)]:
            overlay.read(graph)
        self._offer_overlay_types()
        self._check()

    def _offer_overlay_types(self) -> None:
        """Offer the overlay schemas' node and relationship types in the filter lists before rules run."""
        for practice in self.graph.practices.opened.values():
            overlays = list(self.graph.applied_patterns.overlays_for(practice))
            if overlays:
                practice.reading.in_graph.rule_run.offer_overlay_types(overlays)
