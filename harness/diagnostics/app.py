"""*App*, one CDD web app a person opens beside the chat, the one registry of them, and how far each has got."""
from __future__ import annotations

import os
import re
import shutil
import signal
import socket
import subprocess
import sys
import time
from enum import Enum
from pathlib import Path
from typing import ClassVar

from harness.agent_tools import agent_toolset
from harness.agent_tools.agent_tools import agent_tool, tool_subject
from harness.agent_tools.progress import report_progress
from harness.graph.graph_app import GRAPH_APP_PORTS
from harness.installation.data_class import data_field, identity, language_adapter
from harness.installation.json_file import JsonFile
from harness.mcp.mcp_annotations import long_call, mcp

_HOST = "127.0.0.1"
# A server listening on this machine takes a connection at once: the system completes it, not the server.
PROBE_SECONDS = 0.05
# npm install fetches packages, so it gets most of the ten minutes a call may take; a build takes the same.
NPM_SECONDS = 270
# How many lines of a failed install's output the status row shows.
REASON_LINES = 3
# The loader node runs a TypeScript server with, from the server's own packages.
TYPESCRIPT_LOADER = ("--import", "tsx")
# How long a restarted server has to answer on one of its ports, and how often it is asked.
RESTART_SECONDS = 30
RESTART_CHECK_SECONDS = 0.25
# A Windows process started on its own, so it outlives the install that started it and opens no console window.
_DETACHED = getattr(subprocess, "DETACHED_PROCESS", 0) | getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0) | getattr(subprocess, "CREATE_NO_WINDOW", 0)


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
    """An app could not be installed: which app, the output that says why, and the fix."""

    def __init__(self, app: App, reason: str) -> None:
        super().__init__(f"The {app.label} install failed: {reason}. Run npm install in {app.folder}.")
        self.app = app
        self.reason = reason


class AppServer:
    """The server an app answers from: the script node runs, the folder it runs in, and the ports it tries in turn. The
    chat that opens an app starts it, as long as that chat lasts, so this says how; two apps the same server serves,
    as the board's server serves the Story UI editor, share one."""

    def __init__(self, folder: Path, script: str, ports: tuple[int, ...]) -> None:
        self._folder = Path(folder)
        self.script = script
        self.ports = tuple(ports)

    @property
    @data_field
    def folder(self) -> str:
        """The folder it runs in, written with forward slashes, as a chat starts it there."""
        return self._folder.as_posix()

    @property
    @data_field
    def command(self) -> list[str]:
        """What starts it, run in its folder: node on its script, through tsx for a TypeScript one."""
        loader = list(TYPESCRIPT_LOADER) if self.script.endswith(".ts") else []
        return ["node", *loader, self.script]

    @property
    def port(self) -> int | None:
        """The first of its ports that answers; none while it is not running."""
        return next((port for port in self.ports if self._answers(port)), None)

    def _answers(self, port: int) -> bool:
        with socket.socket() as probe:
            probe.settimeout(PROBE_SECONDS)
            return probe.connect_ex((_HOST, port)) == 0

    def restart(self) -> bool:
        """Stop the server while it runs and start it again in its folder, so it serves the code an install just
        wrote: a server keeps the routes and the built page it started with, and answers a path it does not know with
        another app's page. The server started again runs on its own, past the install. A server that is not running
        is left for the chat that opens its app to start; answers whether it restarted."""
        port = self.port
        if port is None:
            return False
        listening = _process_listening_on(port)
        if listening is None:
            raise AppServerNotRestarted(self, f"nothing this machine lists is listening on port {port}")
        _stop_process(listening)
        self._wait_until(lambda: self.port is None, f"it still answers on port {port} after it was stopped")
        try:
            subprocess.Popen(self.command, cwd=self._folder, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=_DETACHED, start_new_session=sys.platform != "win32")
        except OSError as failed:
            raise AppServerNotRestarted(self, f"{' '.join(self.command)} did not start: {failed}") from failed
        self._wait_until(lambda: self.port is not None, f"nothing answered on {', '.join(map(str, self.ports))} within {RESTART_SECONDS} s")
        return True

    def _wait_until(self, done, reason: str) -> None:
        deadline = time.monotonic() + RESTART_SECONDS
        while not done():
            if time.monotonic() > deadline:
                raise AppServerNotRestarted(self, reason)
            time.sleep(RESTART_CHECK_SECONDS)


class AppServerNotRestarted(Exception):
    """A running app server could not be restarted: which server, why, and how to start it by hand."""

    def __init__(self, server: AppServer, reason: str) -> None:
        super().__init__(f"{' '.join(server.command)} was not restarted: {reason}. Stop it and run that command in {server.folder}.")
        self.server = server


def _process_listening_on(port: int) -> int | None:
    """The process listening on port on this machine, as the system lists its connections: netstat on Windows, lsof
    elsewhere. Windows may list a listening socket under process 0, but names the process on its end of a connection,
    so a connection is held open while its server's end is looked up."""
    if sys.platform == "win32":
        try:
            with socket.create_connection((_HOST, port), timeout=PROBE_SECONDS * 20) as held:
                ours = held.getsockname()[1]
                listed = subprocess.run(["netstat", "-ano", "-p", "TCP"], capture_output=True, text=True, errors="replace").stdout
        except (ConnectionRefusedError, TimeoutError):
            return None
        found = re.search(rf"^[ \t]*TCP[ \t]+\S+:{port}[ \t]+\S+:{ours}[ \t]+ESTABLISHED[ \t]+(\d+)[ \t]*$", listed, re.MULTILINE)
        return int(found.group(1)) if found else None
    listed = subprocess.run(["lsof", "-t", f"-iTCP:{port}", "-sTCP:LISTEN"], capture_output=True, text=True).stdout.split()
    return int(listed[0]) if listed else None


def _stop_process(process: int) -> None:
    """Stop the process, and on Windows the ones it started. Elsewhere only the process itself: a server a chat started
    shares the chat's process group, so stopping the group would stop the chat too."""
    if sys.platform == "win32":
        subprocess.run(["taskkill", "/PID", str(process), "/T", "/F"], capture_output=True)
        return
    os.kill(process, signal.SIGTERM)


class NpmRun:
    """What one npm command did: its exit code and what it printed."""

    def __init__(self, code: int, stdout: str = "", stderr: str = "") -> None:
        self.code = code
        self.stdout = stdout
        self.stderr = stderr


class NpmNotFound(Exception):
    """npm is not on the PATH."""


class NpmTooSlow(Exception):
    """An npm command outlasted its time limit and was stopped."""

    def __init__(self, seconds: float) -> None:
        super().__init__(f"took longer than {seconds:g} s")


class Npm:
    """npm, the one system an app's install calls: one command run in an app's folder, within a time limit. On Windows
    npm is a launcher that starts node, so a command over its limit is stopped with every process it started; stopping
    only the launcher would leave node holding its output open, and the wait for that output would not end."""

    def __init__(self, seconds: float = NPM_SECONDS) -> None:
        self.seconds = seconds

    def run(self, folder: Path, *arguments: str) -> NpmRun:
        """Run npm with arguments in folder and answer what it did."""
        npm = shutil.which("npm")
        if npm is None:
            raise NpmNotFound()
        process = subprocess.Popen(
            [npm, *arguments], cwd=folder, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8", errors="replace"
        )
        try:
            stdout, stderr = process.communicate(timeout=self.seconds)
        except subprocess.TimeoutExpired as slow:
            _stop_process(process.pid)
            process.communicate()
            raise NpmTooSlow(self.seconds) from slow
        return NpmRun(process.returncode, stdout, stderr)


@identity("label")
@language_adapter(language="typescript")
@agent_toolset
class App:
    """*App* is one CDD web app a person opens beside the chat: the Story UI editor, the Graph app, or the CDD Kanban.
    The module that owns each app makes it once, keeps it, and registers it; *App* keeps the one registry of them."""

    # open answers an app installed, or refuses; the chat that opens it starts its server for as long as it lasts.
    # status is read from the folder and the ports each time it is asked; the app keeps no copy of it.

    _registered: ClassVar[list[App]] = []

    def __init__(self, label: str, folder: Path, server: AppServer, page: str = "/", npm: Npm | None = None) -> None:
        self._label = label
        self.folder = Path(folder)
        self._server = server
        self.page = page
        self._npm_system = npm or Npm()
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
        """The port its server answers on; none while it is not running."""
        return self._server.port

    @property
    @data_field
    def url(self) -> str:
        """Where its page answers: on the port that answers, else on the first port its server starts on."""
        return f"http://{_HOST}:{self.port or self._server.ports[0]}{self.page}"

    @property
    @data_field
    def server(self) -> AppServer:
        return self._server

    @property
    def is_installed(self) -> bool:
        """Its packages are in its folder, and so is its built page when its package builds one."""
        if not self._package.exists() or not (self.folder / "node_modules").is_dir():
            return False
        return not self._builds_a_page or (self.folder / "dist").is_dir()

    @mcp
    @agent_tool
    def open(self) -> App:
        """Ready the app to open beside the chat: install it while it is not installed, then answer it with its url and
        its server, which the chat starts while it is not running and stops when the chat ends."""
        if self.status is AppStatus.NOT_INSTALLED:
            self.install()
        return self

    @long_call
    @mcp
    @agent_tool
    def install(self) -> App:
        """Install the app's packages, then build its page when its package builds one; a page open on it loads the new build."""
        if not self._package.exists():
            raise AppNotStarted(self, f"{self.folder} holds no package.json, so the {self.label} app is not there yet")
        report_progress(f"{self.label}: npm install in {self.folder}")
        self._npm("install")
        if self._builds_a_page:
            report_progress(f"{self.label}: npm run build in {self.folder}")
            self._npm("run", "build")
        # a chat starts only an installed app, so an install that leaves it not installed is a failed one.
        if not self.is_installed:
            raise AppNotStarted(self, f"npm left {self.folder} without its packages or its built page")
        return self

    @property
    def _builds_a_page(self) -> bool:
        return "build" in self._package.read().get("scripts", {})

    def _npm(self, *arguments: str) -> None:
        try:
            ran = self._npm_system.run(self.folder, *arguments)
        except NpmNotFound as missing:
            raise AppNotStarted(self, "npm is not on the PATH: install Node.js") from missing
        except NpmTooSlow as slow:
            raise AppNotStarted(self, f"npm {' '.join(arguments)} {slow}") from slow
        if ran.code != 0:
            raise AppNotStarted(self, _reason_of(ran.stderr or ran.stdout) or f"npm {' '.join(arguments)} exited with {ran.code}")


def _reason_of(output: str) -> str:
    """The lines of a failed step's output that say why: the first error lines npm and node print, such as
    ``npm error code ENOENT``, else its last lines."""
    lines = output.strip().splitlines()
    errors = [line for line in lines if "err" in line.lower()]
    return "\n".join(errors[:REASON_LINES] if errors else lines[-REASON_LINES:])


# harness/graph sits below this module and imports nothing of it, so the Graph app is made and registered here, from
# the ports file its servers read; space/kanban registers the CDD Kanban and the Story UI editor the same way.
_GRAPH_FOLDER = GRAPH_APP_PORTS.file.path.parent
GRAPH_APP = App("Graph", _GRAPH_FOLDER, AppServer(_GRAPH_FOLDER, "start.ts", GRAPH_APP_PORTS.of("app"))).register()
