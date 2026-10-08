"""Find duplicate CDD runtime processes and stop every one but the keeper."""
from __future__ import annotations

import json
import os
import re
import signal
import socket
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Callable, NamedTuple


class Process(NamedTuple):
    pid: int
    ppid: int
    command: str


class RepoProcesses:
    """Command lines and listening ports for processes started from this checkout."""

    def __init__(self, repo: Path | str | None = None) -> None:
        self.repo = Path(repo or Path(__file__).resolve().parents[1]).resolve()
        self._process_cache: list[Process] | None = None
        self._port_cache: dict[int, list[int]] | None = None

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

    def listening_ports(self) -> dict[int, list[int]]:
        if self._port_cache is None:
            if sys.platform == "win32":
                self._port_cache = self._windows_ports()
            else:
                self._port_cache = self._posix_ports()
        return self._port_cache

    def descendants(self, pid: int) -> list[int]:
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

    def tree_ports(self, pid: int) -> list[int]:
        ports = self.listening_ports()
        heard: set[int] = set()
        for item in self.descendants(pid):
            heard.update(ports.get(item, []))
        return sorted(heard)

    def alive(self, pid: int) -> bool:
        if pid <= 0:
            return False
        if sys.platform == "win32":
            return self._windows_alive(pid)
        try:
            os.kill(pid, 0)
        except PermissionError:
            return True
        except OSError:
            return False
        return True

    def stop(self, pid: int) -> None:
        if pid <= 0 or pid == os.getpid() or not self.alive(pid):
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

    def http_ping(self, port: int) -> dict[str, Any] | None:
        heard = self._read_ping(port)
        if heard is not None:
            return heard
        origin = self._open_origin(port)
        if origin is None:
            return None
        return {
            "ok": True,
            "ping": "pong",
            "url": origin,
            "port": port,
        }

    def _read_ping(self, port: int) -> dict[str, Any] | None:
        for origin in self._origins(port):
            body = self._fetch_ping(origin)
            if body is not None:
                return body
        return None

    def _fetch_ping(self, origin: str) -> dict[str, Any] | None:
        try:
            with urllib.request.urlopen(origin + "/ping", timeout=2) as response:
                body = json.loads(response.read().decode("utf-8"))
        except (OSError, urllib.error.URLError, json.JSONDecodeError, ValueError, TimeoutError):
            return None
        if not isinstance(body, dict) or body.get("ping") != "pong":
            return None
        reported = str(body.get("url") or "").rstrip("/")
        body["url"] = reported if reported == origin else origin
        port_text = origin.rsplit(":", 1)[-1]
        if port_text.isdigit():
            body.setdefault("port", int(port_text))
        return body

    def _open_origin(self, port: int) -> str | None:
        for host, origin in (("127.0.0.1", f"http://127.0.0.1:{port}"), ("::1", f"http://localhost:{port}")):
            try:
                with socket.create_connection((host, port), timeout=2):
                    return origin
            except OSError:
                continue
        return None

    def _origins(self, port: int) -> tuple[str, ...]:
        return (f"http://127.0.0.1:{port}", f"http://localhost:{port}")

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
            timeout=60,
            check=False,
        )
        return self._rows_from_json(completed.stdout)

    def _posix_processes(self) -> list[Process]:
        completed = subprocess.run(
            ["ps", "-ax", "-o", "pid=,ppid=,command="],
            capture_output=True,
            text=True,
            timeout=30,
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

    def _rows_from_json(self, raw: str) -> list[Process]:
        text = (raw or "").lstrip("\ufeff").strip()
        if not text:
            return []
        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            return []
        rows = data if isinstance(data, list) else [data]
        found: list[Process] = []
        for row in rows:
            if not isinstance(row, dict):
                continue
            command = str(row.get("CommandLine") or "").strip()
            pid = row.get("ProcessId")
            ppid = row.get("ParentProcessId")
            if not command or not isinstance(pid, int):
                continue
            parent = ppid if isinstance(ppid, int) and ppid > 0 else 0
            found.append(Process(pid, parent, command))
        return found

    def _windows_ports(self) -> dict[int, list[int]]:
        completed = subprocess.run(
            ["netstat", "-ano"],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        ports: dict[int, set[int]] = {}
        for line in (completed.stdout or "").splitlines():
            parts = line.split()
            if len(parts) < 5 or parts[3].upper() != "LISTENING":
                continue
            port_text = parts[1].rsplit(":", 1)[-1]
            if not port_text.isdigit() or not parts[4].isdigit():
                continue
            ports.setdefault(int(parts[4]), set()).add(int(port_text))
        return {pid: sorted(values) for pid, values in ports.items()}

    def _posix_ports(self) -> dict[int, list[int]]:
        completed = subprocess.run(
            ["ss", "-ltnp"],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        ports: dict[int, set[int]] = {}
        for line in (completed.stdout or "").splitlines():
            pid_match = re.search(r"pid=(\d+)", line)
            port_match = re.search(r":(\d+)\s", line)
            if pid_match is None or port_match is None:
                continue
            ports.setdefault(int(pid_match.group(1)), set()).add(int(port_match.group(1)))
        return {pid: sorted(values) for pid, values in ports.items()}

    def _windows_alive(self, pid: int) -> bool:
        import ctypes

        handle = ctypes.windll.kernel32.OpenProcess(0x1000, False, pid)
        if not handle:
            return False
        ctypes.windll.kernel32.CloseHandle(handle)
        return True


class PingReport:
    """Print one JSON ping result and return a process exit code."""

    def emit(self, report: dict[str, Any]) -> int:
        json.dump(report, sys.stdout, indent=2)
        sys.stdout.write("\n")
        return 0 if report.get("ok") else 1


class McpPing:
    """Ping the CDD stdio host. Keep one process; stop the rest."""

    def __init__(self, repo: Path | str | None = None) -> None:
        self.processes = RepoProcesses(repo)

    def run(self) -> int:
        found = self._hosts()
        keeper, stopped = self.processes.collapse(found, self._recorded_pid())
        alive = keeper is not None and self.processes.alive(keeper)
        return PingReport().emit(
            {
                "ok": alive,
                "ping": "pong" if alive else "down",
                "pid": keeper,
                "instances": len(found),
                "stopped": stopped,
            }
        )

    def _hosts(self) -> list[int]:
        return [item.pid for item in self.processes.roots(self.processes.matching(self._is_host))]

    def _is_host(self, command: str) -> bool:
        folded = command.casefold().replace("\\", "/")
        if not self.processes.in_repo(command) or "discover_host.py" in folded:
            return False
        if "start_host.py" in folded:
            return True
        return re.search(r"(^|\s)-m\s+harness\.mcp(\s|$)", folded) is not None

    def _recorded_pid(self) -> int | None:
        path = self.processes.repo / ".cursor" / "mcp-host.pid"
        if not path.is_file():
            return None
        try:
            pid = int(path.read_text(encoding="utf-8").strip())
        except ValueError:
            return None
        return pid if pid > 0 else None


class HookPing:
    """Ping the hook daemon. Keep the published process; stop the rest."""

    def __init__(self, repo: Path | str | None = None) -> None:
        self.processes = RepoProcesses(repo)

    def run(self) -> int:
        from harness.hooks.hook_daemon import HookDaemon
        from harness.hooks.hook_server import HookServer

        found = self._daemons()
        state = HookServer.state_path(self.processes.repo)
        recorded = self._recorded_pid(state)
        keeper, stopped = self.processes.collapse(found, recorded)
        address = HookDaemon().live_address(state)
        ok = address is not None
        host, port, pid = address if address is not None else (None, None, keeper)
        return PingReport().emit(
            {
                "ok": ok,
                "ping": "pong" if ok else "down",
                "host": host,
                "port": port,
                "pid": pid if pid is not None else keeper,
                "instances": len(found),
                "stopped": stopped,
            }
        )

    def _daemons(self) -> list[int]:
        return [item.pid for item in self.processes.roots(self.processes.matching(self._is_daemon))]

    def _is_daemon(self, command: str) -> bool:
        folded = command.casefold()
        return self.processes.in_repo(command) and "harness.hooks.hook_daemon" in folded

    def _recorded_pid(self, path: Path) -> int | None:
        if not path.is_file():
            return None
        try:
            pid = json.loads(path.read_text(encoding="utf-8")).get("pid")
        except json.JSONDecodeError:
            return None
        return int(pid) if isinstance(pid, int) and pid > 0 else None


class HttpPing:
    """Ping one HTTP listener. Keep the process that answers; stop the rest."""

    def __init__(self, repo: Path | str | None = None) -> None:
        self.processes = RepoProcesses(repo)

    def run(self, include: Callable[[str], bool]) -> int:
        def scoped(command: str) -> bool:
            return self.processes.in_repo(command) and include(command)

        found = [item.pid for item in self.processes.roots(self.processes.matching(scoped))]
        ports = {pid: self.processes.tree_ports(pid) for pid in found}
        answered = {pid: self._first_pong(ports.get(pid, [])) for pid in found}
        healthy = [pid for pid, body in answered.items() if body is not None]
        prefer = min(healthy) if healthy else None
        keeper, stopped = self.processes.collapse(found, prefer)
        body = answered.get(keeper) if keeper is not None else None
        if keeper is not None and body is None:
            body = self._first_pong(self.processes.tree_ports(keeper))
        port = None if body is None else body.get("port")
        if port is None and keeper is not None:
            heard = ports.get(keeper) or []
            port = heard[0] if heard else None
        url = None if body is None else body.get("url")
        if url is None and port is not None:
            url = f"http://127.0.0.1:{port}"
        ok = body is not None and body.get("ping") == "pong"
        return PingReport().emit(
            {
                "ok": ok,
                "ping": "pong" if ok else "down",
                "url": url,
                "port": port,
                "pid": keeper,
                "instances": len(found),
                "stopped": stopped,
            }
        )

    def _first_pong(self, ports: list[int]) -> dict[str, Any] | None:
        for port in ports:
            body = self.processes.http_ping(port)
            if body is not None:
                return body
        return None


def codeql_web(command: str) -> bool:
    folded = command.casefold().replace("\\", "/")
    if "preflight.cjs" in folded or "vitest" in folded:
        return False
    return "codeql_graph/app/" in folded and "server.ts" in folded


def codeql_app(command: str) -> bool:
    folded = command.casefold().replace("\\", "/")
    if "codeql_graph/app/" not in folded or "vitest" in folded or "preflight.cjs" in folded:
        return False
    return "/vite/bin/vite.js" in folded or folded.rstrip().endswith(" vite")
