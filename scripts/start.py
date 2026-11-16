"""Stop the current process for a service, then start one new one."""
from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Callable, NamedTuple

_REPO = Path(__file__).resolve().parents[1]
_SCRIPTS = Path(__file__).resolve().parent
for _entry in (str(_REPO), str(_SCRIPTS)):
    if _entry not in sys.path:
        sys.path.insert(0, _entry)

from instances import (
    GRAPH_APP,
    GRAPH_WEB,
    HttpService,
    PingAnswer,
    PingAnswers,
    PingReport,
    RepoProcesses,
)

START_WAIT_SECONDS = 30
"""How long a started service has to answer its ping before the start is reported down."""

STOP_WAIT_SECONDS = 10
"""How long the stopped copies have to disappear from the process list before the new one starts anyway."""

POLL_SECONDS = 0.25
"""How often a wait asks again; short enough that a fast start is reported at once."""


class ServiceLaunch(NamedTuple):
    """The command that starts a service, the folder it runs in, its log, and its environment."""

    command: str
    cwd: Path
    log: Path
    env: dict[str, str]


class ServiceStart:
    """Kill every running copy, start one, and wait until it answers."""

    def __init__(self, processes: RepoProcesses | None = None) -> None:
        self.processes = processes or RepoProcesses()
        self.answers = PingAnswers()
        self.repo = self.processes.repo
        self.app = self.repo / "harness" / "graph" / "app"
        self.logs = _SCRIPTS / ".run"

    def graph_app(self) -> int:
        return self._http(GRAPH_APP, ServiceLaunch("npm run dev", self.app, self.logs / "graph-app.log", os.environ.copy()))

    def graph_web(self) -> int:
        env = os.environ.copy()
        # The explorer's server names the project it explores on every cdd call; by default this checkout.
        env.setdefault("GRAPH_PROJECT", str(self.repo))
        python = self.repo / ".venv" / "Scripts" / "python.exe"
        if python.is_file():
            env["PYTHON"] = str(python)
        return self._http(GRAPH_WEB, ServiceLaunch("npm run server", self.app, self.logs / "graph-web.log", env))

    def hook(self) -> int:
        from harness.hooks.hook_daemon import HookDaemon

        stopped = self._stop(self._hook_command)
        daemon = HookDaemon(self.repo)
        daemon.spawn()
        address = self._waited(daemon.live_address)
        ok = address is not None
        return PingReport().emit(
            {
                "ok": ok,
                "ping": "pong" if ok else "down",
                "host": address.host if ok else None,
                "port": address.port if ok else None,
                "pid": address.pid if ok else None,
                "stopped": stopped,
                "log": "" if ok else str(daemon.log_path),
            }
        )

    def _waited(self, answer: Callable[[], Any]) -> Any:
        """The first answer that is not None within the start wait, or None when none came."""
        deadline = time.time() + START_WAIT_SECONDS
        while time.time() < deadline:
            found = answer()
            if found is not None:
                return found
            time.sleep(POLL_SECONDS)
        return None

    def _http(self, service: HttpService, launch: ServiceLaunch) -> int:
        stopped = self._stop(service.include)
        self._spawn(launch)
        pid, body = self._waited(lambda: self._pong(service)) or (None, None)
        ok = body is not None
        report: PingAnswer = {
            "ok": ok,
            "ping": "pong" if ok else "down",
            "url": None if body is None else body.get("url"),
            "port": None if body is None else body.get("port"),
            "pid": pid,
            "stopped": stopped,
        }
        if not ok:
            report["log"] = str(launch.log)
        return PingReport().emit(report)

    def _stop(self, include: Callable[[str], bool]) -> list[int]:
        found = self._roots(include)
        for pid in found:
            self.processes.stop(pid)
        deadline = time.time() + STOP_WAIT_SECONDS
        while time.time() < deadline and self._roots(include):
            time.sleep(POLL_SECONDS)
        return found

    def _pong(self, service: HttpService) -> tuple[int, PingAnswer] | None:
        for pid in self._roots(service.include):
            body = self.answers.first_pong(service, self.processes.tree_ports(pid))
            if body is not None:
                return pid, body
        return None

    def _roots(self, include: Callable[[str], bool]) -> list[int]:
        self.processes.refresh()
        return self.processes.root_pids(include)

    def _hook_command(self, command: str) -> bool:
        return "harness.hooks.hook_daemon" in command.casefold()

    def _spawn(self, launch: ServiceLaunch) -> None:
        launch.log.parent.mkdir(parents=True, exist_ok=True)
        stream = open(launch.log, "a", encoding="utf-8")
        stream.write(f"\n--- {launch.command} ---\n")
        stream.flush()
        subprocess.Popen(
            args=launch.command,
            cwd=str(launch.cwd),
            env=launch.env,
            stdin=subprocess.DEVNULL,
            stdout=stream,
            stderr=subprocess.STDOUT,
            shell=True,
            close_fds=True,
            **self._detached(),
        )

    def _detached(self) -> dict[str, Any]:
        """The options that keep the started service running after this script exits, without a console window."""
        if sys.platform != "win32":
            return {"start_new_session": True}
        from harness.process.process import BackgroundStart

        background = BackgroundStart()
        return {"creationflags": background.creationflags, "startupinfo": background.startupinfo}
