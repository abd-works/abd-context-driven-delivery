"""Find duplicate CDD runtime processes and stop every one but the keeper."""
from __future__ import annotations

import json
import os
import signal
import socket
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Callable, NamedTuple, TypedDict

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from harness.graph.graph_app import GRAPH_APP_PORTS  # noqa: E402
from harness.process.process import RunningProcess  # noqa: E402

PingAnswer = dict[str, Any]
"""The JSON a service's ``/ping`` answered, or the report a ping script prints."""

PING_TIMEOUT_SECONDS = 2
"""How long one ping or connection attempt waits; a local service that is up answers in milliseconds."""

PROCESS_LIST_TIMEOUT_SECONDS = {"win32": 60, "posix": 30}
"""How long listing processes may take: PowerShell's CIM query starts slowly on Windows, ``ps`` is quick."""


class ProcessEntry(TypedDict, total=False):
    """One process as the system's process listing reports it in JSON."""

    CommandLine: str
    ProcessId: int
    ParentProcessId: int


class Process(NamedTuple):
    pid: int
    ppid: int
    command: str


class HttpService(NamedTuple):
    """An HTTP service a script pings: which command lines run it, the ports it listens on, and the service name its
    ``/ping`` answers with."""

    include: Callable[[str], bool]
    preferred_ports: tuple[int, ...] = ()
    expect_service: str | None = None

    def answered_by(self, origin: str, body: PingAnswer) -> bool:
        """Whether the pong at ``origin`` came from this service: by the name it gives, or, for a graph server that
        gives none, by the port it answers on."""
        if self.expect_service is None:
            return True
        tagged = body.get("service")
        if tagged is not None:
            return tagged == self.expect_service
        port_text = origin.rsplit(":", 1)[-1]
        untagged_ports = {"graph_web": GRAPH_APP_PORTS.of("web"), "graph_app": GRAPH_APP_PORTS.of("app")}
        ports = untagged_ports.get(self.expect_service, ())
        return port_text in {str(item) for item in ports}


class PingAnswers:
    """Ask local ports for a ``/ping`` pong, or at least an open connection."""

    def first_pong(self, service: HttpService, ports: list[int]) -> PingAnswer | None:
        candidates = list(service.preferred_ports) if service.preferred_ports else sorted(ports)
        for port in candidates:
            body = self.ping(port, service)
            if body is not None:
                return body
        return None

    def ping(self, port: int, service: HttpService) -> PingAnswer | None:
        heard = self._read_ping(port, service)
        if heard is not None:
            return heard
        if service.expect_service is not None:
            return None
        origin = self._open_origin(port)
        if origin is None:
            return None
        return {"ok": True, "ping": "pong", "url": origin, "port": port}

    def _read_ping(self, port: int, service: HttpService) -> PingAnswer | None:
        for origin in self._origins(port):
            body = self._fetch_ping(origin)
            if body is not None and service.answered_by(origin, body):
                return self._located(body, origin)
        return None

    def _fetch_ping(self, origin: str) -> PingAnswer | None:
        try:
            with urllib.request.urlopen(origin + "/ping", timeout=PING_TIMEOUT_SECONDS) as response:
                body = json.loads(response.read().decode("utf-8"))
        except (OSError, urllib.error.URLError, json.JSONDecodeError, ValueError, TimeoutError):
            return None
        if not isinstance(body, dict) or body.get("ping") != "pong":
            return None
        return body

    def _located(self, body: PingAnswer, origin: str) -> PingAnswer:
        """The pong with the origin it was heard on, which a server behind a proxy may report differently."""
        reported = str(body.get("url") or "").rstrip("/")
        body["url"] = reported if reported == origin else origin
        port_text = origin.rsplit(":", 1)[-1]
        if port_text.isdigit():
            body.setdefault("port", int(port_text))
        return body

    def _open_origin(self, port: int) -> str | None:
        for host, origin in (("127.0.0.1", f"http://127.0.0.1:{port}"), ("::1", f"http://localhost:{port}")):
            try:
                with socket.create_connection((host, port), timeout=PING_TIMEOUT_SECONDS):
                    return origin
            except OSError:
                continue
        return None

    def _origins(self, port: int) -> tuple[str, ...]:
        return (f"http://127.0.0.1:{port}", f"http://localhost:{port}")


class RepoProcesses:
    """Command lines and listening ports for processes started from this checkout."""

    def __init__(self, repo: Path | str | None = None) -> None:
        self.repo = Path(repo or Path(__file__).resolve().parents[1]).resolve()
        self._process_cache: list[Process] | None = None

    def refresh(self) -> None:
        """Forget the processes read so far, so the next question reads them again."""
        self._process_cache = None

    def matching(self, include: Callable[[str], bool]) -> list[Process]:
        return [item for item in self.processes() if include(item.command)]

    def roots(self, found: list[Process]) -> list[Process]:
        """Drop a worker whose parent is already one of these processes."""
        pids = {item.pid for item in found}
        return [item for item in found if item.ppid not in pids]

    def processes(self) -> list[Process]:
        if self._process_cache is None:
            if sys.platform == "win32":
                self._process_cache = self._windows_processes()
            else:
                self._process_cache = self._posix_processes()
        return self._process_cache

    def tree_ports(self, pid: int) -> list[int]:
        heard: set[int] = set()
        for item in self._descendants(pid):
            heard.update(RunningProcess(item).listening_ports)
        return sorted(heard)

    def stop(self, pid: int) -> None:
        if pid <= 0 or pid == os.getpid() or not RunningProcess(pid).alive:
            return
        if sys.platform == "win32":
            subprocess.run(
                ["taskkill", "/F", "/T", "/PID", str(pid)],
                capture_output=True,
                text=True,
                check=False,
            )
            return
        os.kill(pid, signal.SIGTERM)

    def collapse(self, pids: list[int], prefer: int | None = None) -> tuple[int | None, list[int]]:
        unique = sorted({pid for pid in pids if pid > 0})
        if not unique:
            return None, []
        keeper = prefer if prefer in unique else unique[0]
        stopped = [pid for pid in unique if pid != keeper]
        for pid in stopped:
            self.stop(pid)
        return keeper, stopped

    def in_repo(self, command: str) -> bool:
        folded = command.casefold().replace("\\", "/")
        root = str(self.repo).casefold().replace("\\", "/")
        return root in folded

    def root_pids(self, include: Callable[[str], bool]) -> list[int]:
        """The top process of each copy of a service started from this checkout."""

        def scoped(command: str) -> bool:
            return self.in_repo(command) and include(command)

        return [item.pid for item in self.roots(self.matching(scoped))]

    def _descendants(self, pid: int) -> list[int]:
        by_parent: dict[int, list[int]] = {}
        for item in self.processes():
            by_parent.setdefault(item.ppid, []).append(item.pid)
        found = [pid]
        pending = [pid]
        while pending:
            current = pending.pop()
            for child in by_parent.get(current, []):
                found.append(child)
                pending.append(child)
        return found

    def _windows_processes(self) -> list[Process]:
        script = (
            "Get-CimInstance Win32_Process | "
            "Where-Object { $_.Name -match '^(python|pythonw|node)(\\.exe)?$' } | "
            "Select-Object ProcessId, ParentProcessId, CommandLine | ConvertTo-Json -Compress"
        )
        completed = subprocess.run(
            ["powershell", "-NoProfile", "-Command", script],
            capture_output=True,
            text=True,
            timeout=PROCESS_LIST_TIMEOUT_SECONDS["win32"],
            check=False,
        )
        return self._processes_from_json(completed.stdout)

    def _posix_processes(self) -> list[Process]:
        completed = subprocess.run(
            ["ps", "-ax", "-o", "pid=,ppid=,command="],
            capture_output=True,
            text=True,
            timeout=PROCESS_LIST_TIMEOUT_SECONDS["posix"],
            check=False,
        )
        found: list[Process] = []
        for line in (completed.stdout or "").splitlines():
            text = line.strip()
            if not text:
                continue
            pid_text, _, rest = text.partition(" ")
            ppid_text, _, command = rest.strip().partition(" ")
            if not pid_text.isdigit() or not ppid_text.isdigit() or not command:
                continue
            found.append(Process(int(pid_text), int(ppid_text), command.strip()))
        return found

    def _processes_from_json(self, raw: str) -> list[Process]:
        text = (raw or "").lstrip("﻿").strip()
        if not text:
            return []
        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            return []
        entries = data if isinstance(data, list) else [data]
        return [process for process in map(self._process_from_entry, entries) if process is not None]

    def _process_from_entry(self, entry: ProcessEntry) -> Process | None:
        if not isinstance(entry, dict):
            return None
        command = str(entry.get("CommandLine") or "").strip()
        pid = entry.get("ProcessId")
        ppid = entry.get("ParentProcessId")
        if not command or not isinstance(pid, int):
            return None
        return Process(pid, ppid if isinstance(ppid, int) and ppid > 0 else 0, command)


class PingReport:
    """Print one JSON ping result and return a process exit code."""

    def emit(self, report: PingAnswer) -> int:
        json.dump(report, sys.stdout, indent=2)
        sys.stdout.write("\n")
        return 0 if report.get("ok") else 1


class HookPing:
    """Ping the hook daemon. Keep the published process; stop the rest."""

    def __init__(self, repo: Path | str | None = None) -> None:
        self.processes = RepoProcesses(repo)

    def run(self) -> int:
        from harness.hooks.hook_daemon import HookDaemon

        found = self._daemons()
        daemon = HookDaemon(self.processes.repo)
        published = daemon.address_file.server()
        keeper, stopped = self.processes.collapse(found, published.pid if published is not None and published.pid > 0 else None)
        running = daemon.running()
        ok = running is not None
        return PingReport().emit(
            {
                "ok": ok,
                "ping": "pong" if ok else "down",
                "host": daemon.address.host if ok else None,
                "port": daemon.address.port if ok else None,
                "pid": running.pid if ok and running.pid > 0 else keeper,
                "instances": len(found),
                "stopped": stopped,
            }
        )

    def _daemons(self) -> list[int]:
        return [item.pid for item in self.processes.roots(self.processes.matching(self._is_daemon))]

    def _is_daemon(self, command: str) -> bool:
        folded = command.casefold()
        return self.processes.in_repo(command) and "harness.hooks.hook_daemon" in folded


class HttpPing:
    """Ping one HTTP listener. Keep the process that answers; stop the rest."""

    def __init__(self, repo: Path | str | None = None) -> None:
        self.processes = RepoProcesses(repo)
        self.answers = PingAnswers()

    def run(self, service: HttpService) -> int:
        found = self.processes.root_pids(service.include)
        ports = {pid: self.processes.tree_ports(pid) for pid in found}
        keeper, stopped, body = self._collapse_to_keeper(service, found, ports)
        port = self._port(service, body, (ports.get(keeper) or []) if keeper is not None else None)
        url = body.get("url") if body is not None else None
        ok = body is not None and body.get("ping") == "pong"
        return PingReport().emit(
            {
                "ok": ok,
                "ping": "pong" if ok else "down",
                "url": url if url is not None or port is None else f"http://127.0.0.1:{port}",
                "port": port,
                "pid": keeper,
                "instances": len(found),
                "stopped": stopped,
            }
        )

    def _collapse_to_keeper(
        self, service: HttpService, found: list[int], ports: dict[int, list[int]]
    ) -> tuple[int | None, list[int], PingAnswer | None]:
        """Keep the lowest process that answers a ping, stop the rest, and answer the keeper, what was stopped, and what
        the keeper answered."""
        answered = {pid: self.answers.first_pong(service, ports.get(pid, [])) for pid in found}
        healthy = [pid for pid, body in answered.items() if body is not None]
        keeper, stopped = self.processes.collapse(found, min(healthy) if healthy else None)
        return keeper, stopped, self._keeper_answer(service, keeper, answered)

    def _keeper_answer(
        self, service: HttpService, keeper: int | None, answered: dict[int, PingAnswer | None]
    ) -> PingAnswer | None:
        if keeper is None:
            return None
        body = answered.get(keeper)
        return body if body is not None else self.answers.first_pong(service, self.processes.tree_ports(keeper))

    def _port(self, service: HttpService, body: PingAnswer | None, heard: list[int] | None) -> int | None:
        """The port the keeper answered on, else the one it should listen on, else the first it was heard on; heard
        is none when no process was kept."""
        if body is not None and body.get("port") is not None:
            return body["port"]
        if heard is None:
            return None
        if service.preferred_ports:
            return service.preferred_ports[0]
        return heard[0] if heard else None


_GRAPH_APP = "harness/graph/app/"


def graph_web(command: str) -> bool:
    folded = command.casefold().replace("\\", "/")
    if "preflight.cjs" in folded or "vitest" in folded:
        return False
    return _GRAPH_APP in folded and "server.ts" in folded


def graph_app(command: str) -> bool:
    folded = command.casefold().replace("\\", "/")
    if _GRAPH_APP not in folded or "vitest" in folded or "preflight.cjs" in folded:
        return False
    return "/vite/bin/vite.js" in folded or folded.rstrip().endswith(" vite")


GRAPH_WEB = HttpService(graph_web, GRAPH_APP_PORTS.of("web"), "graph_web")
GRAPH_APP = HttpService(graph_app, GRAPH_APP_PORTS.of("app"), "graph_app")
