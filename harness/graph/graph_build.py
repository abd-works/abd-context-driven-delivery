"""BuildOrder and WorkerBuild. A graph build run in a worker process of its own, for a graph held by the cdd server.

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

from harness.graph.saved_graph import GraphChanges, SavedGraph

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


class BuildOrder:
    """One build as a worker process carries it out: the step, the folder the graph loads, each chosen practice's
    source root, the pattern overlays, the edited files a load is limited to (none for the whole folder), the graph as
    it is before the step, the modules that register the practices and patterns the graph holds, which the worker
    imports so its catalogues hold the same classes, and whether the worker saves the graph it built in the folder's
    ``graph.json``.

    The graph before the step is written into the order (``state``), or named by the file of the worker's last answer
    when the graph holds exactly what that answer says (``state_file``): the server then writes no graph of its own,
    and the worker answers a refresh with what it changed (``GraphChanges``), which is all the server reads back."""

    def __init__(
        self,
        step: BuildStep,
        folder: str,
        roots: dict[str, str],
        overlays: list[str],
        scope: list[str] | None,
        state: SavedGraph | None,
        modules: list[str],
        saves: bool = False,
        state_file: str = "",
    ) -> None:
        self.step = BuildStep(step)
        self.folder = folder
        self.roots = dict(roots)
        self.overlays = list(overlays)
        self.scope = None if scope is None else list(scope)
        self._state = state
        self.modules = list(modules)
        self.saves = saves
        self.state_file = state_file

    @classmethod
    def from_text(cls, text: str) -> BuildOrder:
        document = json.loads(text)
        embedded = document.get("state")
        return cls(
            BuildStep(document["step"]),
            str(document.get("folder") or ""),
            dict(document.get("roots") or {}),
            list(document.get("overlays") or []),
            document.get("scope"),
            SavedGraph.from_document(embedded) if embedded is not None else None,
            list(document.get("modules") or []),
            bool(document.get("saves")),
            str(document.get("state_file") or ""),
        )

    @property
    def state(self) -> SavedGraph:
        """The graph before the step: the one written into the order, else the one its state file holds, read anew
        each time it is asked for, so a build that changes the graph it read leaves this one as it was."""
        if self._state is not None:
            return self._state
        return SavedGraph.from_text(Path(self.state_file).read_text(encoding="utf-8"), self.state_file)

    @property
    def answers_changes(self) -> bool:
        """Whether the worker answers what the step changed: for a refresh of a graph the server holds as the worker's
        last answer said, whose nodes are all plain nodes the changes can be made to."""
        return self.step is BuildStep.REFRESH and bool(self.state_file)

    def changes(self, built: SavedGraph) -> GraphChanges | None:
        """What the step changed in the graph it was given, when the order asks for it and the step kept the graph's
        practices, roots, and overlays."""
        return GraphChanges.between(self.state, built) if self.answers_changes else None

    @property
    def text(self) -> str:
        return json.dumps(
            {
                "step": self.step.value,
                "folder": self.folder,
                "roots": self.roots,
                "overlays": self.overlays,
                "scope": self.scope,
                "state": self._state.document if self._state is not None else None,
                "state_file": self.state_file,
                "modules": self.modules,
                "saves": self.saves,
            },
            separators=(",", ":"),
        )


class HeldAnswer:
    """The file of the last answer a worker gave one graph, while the graph holds exactly what it says: the graph's
    revision when it took the answer names the graph as it was then, and any change since makes the file stale. The
    files live in a folder of the graph's own, removed with it."""

    def __init__(self) -> None:
        self._folder: Path | None = None
        self._file: Path | None = None
        self._revision = -1
        self._count = 0

    def next_file(self) -> Path:
        """A file of this graph's for the next worker's answer."""
        if self._folder is None:
            self._folder = Path(tempfile.mkdtemp(prefix="cdd-graph-answers-"))
            weakref.finalize(self, shutil.rmtree, str(self._folder), True)
        self._count += 1
        return self._folder / f"answer-{self._count}.json"

    def keep(self, file: Path, revision: int) -> None:
        """The graph now holds what file says, at revision; the answer it held before is no longer needed."""
        if self._file is not None and self._file != file:
            self._file.unlink(missing_ok=True)
        self._file = file
        self._revision = revision

    def file_at(self, revision: int) -> Path | None:
        """The answer the graph holds, when it has not changed since it took it."""
        if self._file is None or revision != self._revision or not self._file.is_file():
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
                    hold(SavedGraph.from_text(answer.read_text(encoding="utf-8")))

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
