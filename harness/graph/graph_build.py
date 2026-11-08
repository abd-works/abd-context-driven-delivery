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
import subprocess
import sys
import tempfile
from collections.abc import Callable
from enum import Enum
from pathlib import Path

from harness.graph.saved_graph import SavedGraph

# The module a worker process runs, which carries out one order.
WORKER_MODULE = "harness.graph.graph_worker"
# How much of a failed worker's error output the failure names.
_ERROR_TAIL_CHARACTERS = 4000
# Windows' CREATE_NO_WINDOW: the worker opens no console window beside a windowless server.
_CREATE_NO_WINDOW = 0x08000000


class BuildStep(str, Enum):
    """What a build does with the graph it is given: read the working copy into it and run the rules (``read``), or
    only run the rules on what it holds (``check``), as a graph read back from ``graph.json`` does."""

    READ = "read"
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
    it is before the step, and the modules that register the practices and patterns the graph holds, which the worker
    imports so its catalogues hold the same classes."""

    def __init__(
        self,
        step: BuildStep,
        folder: str,
        roots: dict[str, str],
        overlays: list[str],
        scope: list[str] | None,
        state: SavedGraph,
        modules: list[str],
    ) -> None:
        self.step = BuildStep(step)
        self.folder = folder
        self.roots = dict(roots)
        self.overlays = list(overlays)
        self.scope = None if scope is None else list(scope)
        self.state = state
        self.modules = list(modules)

    @classmethod
    def from_text(cls, text: str) -> BuildOrder:
        document = json.loads(text)
        return cls(
            BuildStep(document["step"]),
            str(document.get("folder") or ""),
            dict(document.get("roots") or {}),
            list(document.get("overlays") or []),
            document.get("scope"),
            SavedGraph.from_document(document["state"]),
            list(document.get("modules") or []),
        )

    @property
    def text(self) -> str:
        return json.dumps(
            {
                "step": self.step.value,
                "folder": self.folder,
                "roots": self.roots,
                "overlays": self.overlays,
                "scope": self.scope,
                "state": self.state.document,
                "modules": self.modules,
            },
            separators=(",", ":"),
        )


class WorkerBuild:
    """One order carried out by a worker process: started with this interpreter and this import path, it reports its
    progress one line at a time, which goes on to report_progress, and writes the graph it built to a file of its
    own."""

    def __init__(self, order: BuildOrder, report_progress: Callable[[str], None]) -> None:
        self.order = order
        self._report_progress = report_progress

    def result(self) -> SavedGraph:
        """The graph the worker built; ``GraphBuildFailed`` when the worker exits with an error."""
        with tempfile.TemporaryDirectory(prefix="cdd-graph-build-") as folder:
            order_file = Path(folder) / "order.json"
            result_file = Path(folder) / "graph.json"
            errors_file = Path(folder) / "errors.txt"
            order_file.write_text(self.order.text, encoding="utf-8")
            with open(errors_file, "w", encoding="utf-8") as errors:
                exit_code = self._run([str(order_file), str(result_file)], errors)
            if exit_code != 0:
                raise GraphBuildFailed(exit_code, errors_file.read_text(encoding="utf-8", errors="replace"))
            return SavedGraph.from_text(result_file.read_text(encoding="utf-8"))

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
