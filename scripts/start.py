"""Stop the current process for a service, then start one new one."""
from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Callable

_REPO = Path(__file__).resolve().parents[1]
_SCRIPTS = Path(__file__).resolve().parent
for _entry in (str(_REPO), str(_SCRIPTS)):
    if _entry not in sys.path:
        sys.path.insert(0, _entry)

from instances import PingReport, RepoProcesses, codeql_app, codeql_web


class ServiceStart:
    """Kill every running copy, start one, and wait until it answers."""

    def __init__(self, processes: RepoProcesses | None = None) -> None:
        self.processes = processes or RepoProcesses()
        self.repo = self.processes.repo
        self.app = self.repo / "harness" / "codeQl_graph" / "app"
        self.logs = _SCRIPTS / ".run"

    def codeql_app(self) -> int:
        return self._http(codeql_app, "npm run dev", self.app, self.logs / "codeql-app.log", os.environ.copy())

    def codeql_web(self) -> int:
        env = os.environ.copy()
        python = self.repo / ".venv" / "Scripts" / "python.exe"
        if python.is_file():
            env["PYTHON"] = str(python)
        return self._http(codeql_web, "npm run server", self.app, self.logs / "codeql-web.log", env)

    def hook(self) -> int:
        from harness.hooks.hook_daemon import HookDaemon
        from harness.hooks.hook_server import HookServer

        stopped = self._stop(self._hook_command)
        daemon = HookDaemon()
        state = HookServer.state_path(self.repo)
        daemon.spawn(self.repo, state)
        deadline = time.time() + 30
        address = None
        while time.time() < deadline:
            address = daemon.live_address(state)
            if address is not None:
                break
            time.sleep(0.25)
        host, port, pid = address if address is not None else (None, None, None)
        ok = address is not None
        return PingReport().emit(
            {
                "ok": ok,
                "ping": "pong" if ok else "down",
                "host": host,
                "port": port,
                "pid": pid,
                "stopped": stopped,
                "log": "" if ok else str(self.repo / ".cursor" / "hook-server.log"),
            }
        )

    def _http(self, include: Callable[[str], bool], command: str, cwd: Path, log: Path, env: dict[str, str]) -> int:
        stopped = self._stop(include)
        self._spawn(command, cwd, log, env)
        pid, body = self._wait_pong(include)
        ok = body is not None
        report: dict[str, Any] = {
            "ok": ok,
            "ping": "pong" if ok else "down",
            "url": None if body is None else body.get("url"),
            "port": None if body is None else body.get("port"),
            "pid": pid,
            "stopped": stopped,
        }
        if not ok:
            report["log"] = str(log)
        return PingReport().emit(report)

    def _stop(self, include: Callable[[str], bool]) -> list[int]:
        found = self._roots(include)
        for pid in found:
            self.processes.stop(pid)
        deadline = time.time() + 10
        while time.time() < deadline and self._roots(include):
            time.sleep(0.2)
        return found

    def _wait_pong(self, include: Callable[[str], bool]) -> tuple[int | None, dict[str, Any] | None]:
        deadline = time.time() + 30
        while time.time() < deadline:
            for pid in self._roots(include):
                body = self._first_pong(self.processes.tree_ports(pid))
                if body is not None:
                    return pid, body
            time.sleep(0.25)
        return None, None

    def _first_pong(self, ports: list[int]) -> dict[str, Any] | None:
        for port in ports:
            body = self.processes.http_ping(port)
            if body is not None:
                return body
        return None

    def _roots(self, include: Callable[[str], bool]) -> list[int]:
        self.processes._process_cache = None
        self.processes._port_cache = None

        def scoped(command: str) -> bool:
            return self.processes.in_repo(command) and include(command)

        return [item.pid for item in self.processes.roots(self.processes.matching(scoped))]

    def _hook_command(self, command: str) -> bool:
        return "harness.hooks.hook_daemon" in command.casefold()

    def _spawn(self, command: str, cwd: Path, log: Path, env: dict[str, str]) -> None:
        log.parent.mkdir(parents=True, exist_ok=True)
        stream = open(log, "a", encoding="utf-8")
        stream.write(f"\n--- {command} ---\n")
        stream.flush()
        kwargs: dict[str, Any] = {
            "args": command,
            "cwd": str(cwd),
            "env": env,
            "stdin": subprocess.DEVNULL,
            "stdout": stream,
            "stderr": subprocess.STDOUT,
            "shell": True,
            "close_fds": True,
        }
        if sys.platform == "win32":
            from harness.hooks.process import detached_creationflags, hidden_process_startupinfo

            kwargs["creationflags"] = detached_creationflags()
            kwargs["startupinfo"] = hidden_process_startupinfo()
        else:
            kwargs["start_new_session"] = True
        subprocess.Popen(**kwargs)
