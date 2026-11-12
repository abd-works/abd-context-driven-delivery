"""*App*, one CDD web app a person opens beside the chat, the one registry of them, and how far each has got."""
from __future__ import annotations

import os
import shutil
import socket
import subprocess
import tempfile
import time
from enum import Enum
from pathlib import Path
from typing import ClassVar

from harness.agent_tools import agent_toolset
from harness.agent_tools.agent_tools import agent_tool, tool_subject
from harness.agent_tools.progress import report_progress
from harness.annotations.name import Name
from harness.graph.graph_app import GRAPH_APP_PORTS
from harness.installation.data_class import data_field, identity, language_adapter
from harness.installation.json_file import JsonFile
from harness.mcp.mcp_server import mcp
from harness.process.process import BackgroundStart

_HOST = "127.0.0.1"
# A server listening on this machine takes a connection at once: the system completes it, not the server.
PROBE_SECONDS = 0.05
# npm install fetches packages, so it gets most of the ten minutes a call may take; a build takes the same.
NPM_SECONDS = 270
LAUNCH_SECONDS = 30
LAUNCH_CHECK_SECONDS = 0.5
# How many lines of a failed step's output the status row shows.
REASON_LINES = 3
INSTALL, LAUNCH = "install", "launch"
# What the status row says of a step that failed, and what a person runs by hand in the app's folder to fix it.
FAILED_OF = {INSTALL: "install failed", LAUNCH: "did not start"}
FIX_OF = {INSTALL: "npm install", LAUNCH: "npm start"}


class AppStatus(str, Enum):
    """How far an app has got on this machine."""

    NOT_INSTALLED = "not installed"
    DOWN = "not running"
    RUNNING = "running"


class AppNotRegistered(KeyError):
    """A call named an app no module registered."""

    def __init__(self, label: str) -> None:
        super().__init__(f"no app is registered as {label}; the apps are {', '.join(app.label for app in App.registered())}")
        self.label = label


class AppNotStarted(Exception):
    """An app could not be installed or launched: which app, which step, the output that says why, and the fix."""

    def __init__(self, app: App, step: str, reason: str) -> None:
        super().__init__(f"The {app.label} {FAILED_OF[step]}: {reason}. Run {FIX_OF[step]} in {app.folder}.")
        self.app = app
        self.step = step
        self.reason = reason


@identity("label")
@language_adapter(language="typescript")
@agent_toolset
class App:
    """*App* is one CDD web app a person opens beside the chat: the Story UI editor, the Graph app, or the CDD Kanban.
    The module that owns each app makes it once, keeps it, and registers it; *App* keeps the one registry of them."""

    # open never launches an app that is not installed, and never answers a url before one of its ports answers.
    # status is read from the folder and the ports each time it is asked; the app keeps no copy of it.

    _registered: ClassVar[list[App]] = []

    def __init__(self, label: str, folder: Path, ports: tuple[int, ...], page: str = "/") -> None:
        self._label = label
        self.folder = Path(folder)
        self.ports = tuple(ports)
        self.page = page
        self._package = JsonFile(self.folder / "package.json")

    def register(self) -> App:
        """Register this app; registering a label again replaces the earlier app rather than listing it twice."""
        held = App._registered
        place = next((index for index, app in enumerate(held) if app.label == self.label), len(held))
        held[place : place + 1] = [self]
        return self

    @classmethod
    def registered(cls) -> list[App]:
        """Every app registered, in the order registered."""
        return list(cls._registered)

    @classmethod
    @tool_subject
    def load(cls, app: str, *, project: Path | str) -> App:
        """The registered app whose label is app, such as Kanban; one no module registered is refused."""
        found = next((registered for registered in cls._registered if registered.label == app), None)
        if found is None:
            raise AppNotRegistered(app)
        return found

    @property
    @data_field
    def label(self) -> str:
        return self._label

    @property
    @data_field
    def status(self) -> AppStatus:
        if not self.is_installed:
            return AppStatus.NOT_INSTALLED
        return AppStatus.DOWN if self.port is None else AppStatus.RUNNING

    @property
    @data_field
    def port(self) -> int | None:
        """The first of its ports that answers; none while it is not running."""
        return next((port for port in self.ports if self._answers(port)), None)

    @property
    @data_field
    def url(self) -> str:
        """Where its page answers: on the port that answers, else on the first port its server starts on."""
        return f"http://{_HOST}:{self.port or self.ports[0]}{self.page}"

    @property
    def is_installed(self) -> bool:
        """Its packages are in its folder, and so is its built page when its package builds one."""
        if not self._package.exists() or not (self.folder / "node_modules").is_dir():
            return False
        return not self._builds_a_page or (self.folder / "dist").is_dir()

    @mcp
    @agent_tool
    def open(self) -> App:
        """Ready the app to open beside the chat: install it while it is not installed, launch it while it is not
        running, then answer it with its url."""
        if self.status is AppStatus.NOT_INSTALLED:
            self.install()
        if self.status is not AppStatus.RUNNING:
            self.launch()
        return self

    def install(self) -> App:
        """Install its packages, then build its page when its package builds one."""
        if not self._package.exists():
            raise AppNotStarted(self, INSTALL, f"{self.folder} holds no package.json, so the {self.label} app is not there yet")
        report_progress(f"{self.label}: npm install in {self.folder}")
        self._npm("install")
        if self._builds_a_page:
            report_progress(f"{self.label}: npm run build in {self.folder}")
            self._npm("run", "build")
        # open launches only an installed app, so an install that leaves it not installed is a failed one.
        if not self.is_installed:
            raise AppNotStarted(self, INSTALL, f"npm left {self.folder} without its packages or its built page")
        return self

    def launch(self) -> App:
        """Start its server from its folder in the background and wait until one of its ports answers."""
        report_progress(f"{self.label}: npm start in {self.folder}")
        with self._launch_log.open("a", encoding="utf-8") as log:
            server = BackgroundStart().run([self._npm_command, "start"], cwd=self.folder, env=dict(os.environ), log=log)
        deadline = time.monotonic() + LAUNCH_SECONDS
        # A server that has stopped will never answer, so the wait ends with it.
        while self.port is None:
            if time.monotonic() > deadline or server.poll() is not None:
                raise AppNotStarted(self, LAUNCH, f"nothing answered on port {self.ports[0]}")
            time.sleep(LAUNCH_CHECK_SECONDS)
        return self

    @property
    def _builds_a_page(self) -> bool:
        return "build" in self._package.read().get("scripts", {})

    @property
    def _launch_log(self) -> Path:
        """Where its server writes what it says while it runs, outside its folder so a launch changes no checked-in file."""
        folder = Path(tempfile.gettempdir()) / "cdd-apps"
        folder.mkdir(parents=True, exist_ok=True)
        return folder / f"{Name(self.label).title_slug}.log"

    @property
    def _npm_command(self) -> str:
        npm = shutil.which("npm")
        if npm is None:
            raise AppNotStarted(self, INSTALL, "npm is not on the PATH: install Node.js")
        return npm

    def _npm(self, *arguments: str) -> None:
        try:
            ran = subprocess.run(
                [self._npm_command, *arguments], cwd=self.folder, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=NPM_SECONDS, stdin=subprocess.DEVNULL
            )
        except subprocess.TimeoutExpired as slow:
            raise AppNotStarted(self, INSTALL, f"npm {' '.join(arguments)} took longer than {NPM_SECONDS} s") from slow
        if ran.returncode != 0:
            raise AppNotStarted(self, INSTALL, _reason_of(ran.stderr or ran.stdout) or f"npm {' '.join(arguments)} exited with {ran.returncode}")

    def _answers(self, port: int) -> bool:
        with socket.socket() as probe:
            probe.settimeout(PROBE_SECONDS)
            return probe.connect_ex((_HOST, port)) == 0


def _reason_of(output: str) -> str:
    """The lines of a failed step's output that say why: the first error lines npm and node print, such as
    ``npm error code ENOENT``, else its last lines."""
    lines = output.strip().splitlines()
    errors = [line for line in lines if "err" in line.lower()]
    return "\n".join(errors[:REASON_LINES] if errors else lines[-REASON_LINES:])


# harness/graph sits below this module and imports nothing of it, so the Graph app is made and registered here, from
# the ports file its servers read; space/kanban registers the CDD Kanban and the Story UI editor the same way.
GRAPH_APP = App("Graph", GRAPH_APP_PORTS.file.path.parent, GRAPH_APP_PORTS.of("app")).register()
