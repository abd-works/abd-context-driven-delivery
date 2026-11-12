"""The named examples of Integrate Practice Content Editor Apps In Chat Bar, one fixture per example.

**Seed** examples are the state an app's folder and ports own: whether its packages and built page are in its folder,
and whether something answers on its port. *App* reads its status from exactly these, so `ThrowawayApp` writes them in a
throwaway folder on a free port, and registers an app of the example's label there in place of the real one, which it
puts back when the scenario ends, so no scenario installs, launches, or stops the person's own apps.

**Interaction** examples are what the status row shows and what a press opens: the app's label, its status, and its url.
"""

from __future__ import annotations

import json
import shutil
import socket
import tempfile
from dataclasses import dataclass
from pathlib import Path

from harness.diagnostics.app import App, AppStatus
from harness.process.process import ListeningPorts
import space.kanban  # noqa: F401 - registers the Kanban and Story UI apps, as the cdd server does when it loads every toolset

STOP_SECONDS = 5


@dataclass(frozen=True)
class AppExample:
    """Interaction: one app of the apps table, as the status row names it and the page it opens on."""

    label: str
    page: str


# The apps table of the scenarios: the status row's label and the page each opens on. The ports are the throwaway
# app's own, a free port each, never the person's 8778 or 5173.
STORY_UI_EDITOR = AppExample("Story UI", "/story-map")
GRAPH_APP = AppExample("Graph", "/")
CDD_KANBAN = AppExample("Kanban", "/")

# Seed: the throwaway app's code. Its one dependency sits beside it, so npm install works offline; its build writes
# the page, and its server answers on the port its ports file names.
SERVE = "require('http').createServer((q, a) => a.end('app')).listen(require('./ports.json').app[0], '127.0.0.1');\n"
BUILD = "require('fs').mkdirSync('dist', {recursive: true}); require('fs').writeFileSync('dist/index.html', 'built');\n"
STOPS_AT_ONCE = "process.exit(0);\n"
# Seed: a dependency npm cannot find, so its install fails with npm's own ENOENT.
MISSING_DEPENDENCY = "file:./missing.tgz"
FOUND_DEPENDENCY = "file:./part"


def free_port() -> int:
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        return probe.getsockname()[1]


class ThrowawayApp:
    """An app of the example's label in a throwaway folder on a free port, registered in place of the real one."""

    def __init__(self, example: AppExample) -> None:
        self.example = example
        self.folder = Path(tempfile.mkdtemp(prefix="cdd-app-"))
        self.port = free_port()
        self._replaced = App.load(example.label, project=self.folder)
        self._listener: socket.socket | None = None
        self.app = App(example.label, self.folder, (self.port,), example.page).register()
        self.write_code(FOUND_DEPENDENCY, SERVE)

    def write_code(self, dependency: str, server: str) -> None:
        """Seed: its package, with dependency as its one dependency and server as what npm start runs."""
        package = {"name": "throwaway-app", "private": True, "scripts": {"build": "node build.js", "start": "node serve.js"}, "dependencies": {"part": dependency}}
        (self.folder / "package.json").write_text(json.dumps(package), encoding="utf-8")
        (self.folder / "ports.json").write_text(json.dumps({"app": [self.port]}), encoding="utf-8")
        (self.folder / "build.js").write_text(BUILD, encoding="utf-8")
        (self.folder / "serve.js").write_text(server, encoding="utf-8")
        (self.folder / "part").mkdir(exist_ok=True)
        (self.folder / "part" / "package.json").write_text(json.dumps({"name": "part", "version": "1.0.0"}), encoding="utf-8")

    def seed(self, status: AppStatus) -> None:
        """Seed: the folder and port as an app of status has them."""
        if status is AppStatus.NOT_INSTALLED:
            return
        (self.folder / "node_modules").mkdir()
        (self.folder / "dist").mkdir()
        if status is AppStatus.RUNNING:
            self._listener = socket.socket()
            self._listener.bind(("127.0.0.1", self.port))
            self._listener.listen()

    @property
    def url(self) -> str:
        """Interaction: the url the side panel shows the app at."""
        return f"http://127.0.0.1:{self.port}{self.example.page}"

    def close(self) -> None:
        """Stop what answers on its port, put the real app back, and remove the folder."""
        if self._listener is not None:
            self._listener.close()
        server = ListeningPorts().holder(self.port)
        if server is not None:
            server.stop(STOP_SECONDS)
        self._replaced.register()
        shutil.rmtree(self.folder, ignore_errors=True)


def app_in(report: dict, label: str) -> dict:
    """The app labelled label as the server health report lists it, which the status row reads."""
    return next(app for app in report["apps"] if app["label"] == label)

