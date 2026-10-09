"""Long-lived CodeQL query-server2 owned by the MCP host process."""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import threading
import time
from pathlib import Path


class CodeQLRunError(RuntimeError):
    """CodeQL could not be started or a query-server call failed."""


class QueryServerDown(CodeQLRunError):
    """The long-lived query server process is gone or its stream closed."""


class CodeQL:
    """Locates the codeql executable and the repo that owns the query server."""

    def __init__(self, root: Path | str) -> None:
        self.root = Path(root)

    def executable(self) -> str:
        path = shutil.which("codeql")
        if path is None:
            raise CodeQLRunError("codeql is not on PATH")
        return path

    def repo_root(self) -> Path:
        resolved = self.root.resolve()
        for candidate in (resolved, *resolved.parents):
            if (candidate / ".git").exists() and (candidate / "practices").is_dir():
                return candidate
        return resolved

_PHASES = {"Compiling", "Running", "Writing", "Shutting"}
_STDERR_LIMIT = 400
_CRASH_LOG_CHARS = 12000


def pid_alive(pid: int) -> bool:
    if pid <= 0:
        return False
    if sys.platform == "win32":
        import ctypes

        handle = ctypes.windll.kernel32.OpenProcess(0x1000, False, pid)
        if handle:
            ctypes.windll.kernel32.CloseHandle(handle)
            return True
        return False
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    return True


def process_command(pid: int) -> str:
    if pid <= 0:
        return ""
    if sys.platform != "win32":
        try:
            raw = Path(f"/proc/{pid}/cmdline").read_bytes()
        except OSError:
            return ""
        return raw.replace(b"\x00", b" ").decode("utf-8", errors="replace").strip()
    result = subprocess.run(
        [
            "powershell",
            "-NoProfile",
            "-Command",
            f"(Get-CimInstance Win32_Process -Filter 'ProcessId={int(pid)}').CommandLine",
        ],
        capture_output=True,
        text=True,
        timeout=20,
        check=False,
    )
    return (result.stdout or "").strip()


_CODEQL_HOLDER_PATTERN = (
    "query-server2|database run-queries|database create|codeql_query_daemon|execute queries"
)


def codeql_holder_pids() -> list[int]:
    """PIDs for processes that can keep a CodeQL database directory open on Windows."""
    if sys.platform != "win32":
        return []
    script = (
        "Get-CimInstance Win32_Process | "
        f"Where-Object {{ $_.CommandLine -match '{_CODEQL_HOLDER_PATTERN}' }} | "
        "ForEach-Object { $_.ProcessId }"
    )
    result = subprocess.run(
        ["powershell", "-NoProfile", "-Command", script],
        capture_output=True,
        text=True,
        timeout=20,
        check=False,
    )
    pids: list[int] = []
    for line in (result.stdout or "").splitlines():
        text = line.strip()
        if text.isdigit():
            pids.append(int(text))
    return pids


def terminate_process_tree(pid: int) -> None:
    if pid <= 0:
        return
    if sys.platform == "win32":
        subprocess.run(
            ["taskkill", "/F", "/T", "/PID", str(pid)],
            check=False,
            capture_output=True,
        )
        return
    try:
        os.kill(pid, 9)
    except OSError:
        return


def stop_query_daemon(repo: Path | str) -> None:
    """Stop the persistent query daemon registered for this repo, if any."""
    root = CodeQL(repo).repo_root()
    path = root / ".codeql" / "query-server.json"
    if not path.is_file():
        return
    pid = 0
    try:
        state = json.loads(path.read_text(encoding="utf-8"))
        pid = int(state.get("pid") or 0)
    except (json.JSONDecodeError, OSError, TypeError, ValueError):
        pass
    if pid_alive(pid):
        terminate_process_tree(pid)
    try:
        path.unlink()
    except OSError:
        pass


def release_codeql_database_locks(*repos: Path | str, settle_seconds: float | None = None) -> None:
    """Drop query daemons and CodeQL JVMs so database directories can be deleted."""
    seen: set[Path] = set()
    touched = False
    for repo in repos:
        root = CodeQL(repo).repo_root()
        if root in seen:
            continue
        seen.add(root)
        marker = root / ".codeql" / "query-server.json"
        if marker.is_file():
            touched = True
        stop_query_daemon(root)
    for pid in codeql_holder_pids():
        touched = True
        terminate_process_tree(pid)
    if touched:
        delay = settle_seconds if settle_seconds is not None else (1.0 if sys.platform == "win32" else 0.35)
        time.sleep(delay)


def codeql_process_report() -> str:
    """Name every CodeQL process that can hold the query server or a database."""
    if sys.platform != "win32":
        return ""
    script = (
        "Get-CimInstance Win32_Process | "
        f"Where-Object {{ $_.CommandLine -match '{_CODEQL_HOLDER_PATTERN}' }} | "
        "ForEach-Object { '{0}`t{1}' -f $_.ProcessId, $_.CommandLine }"
    )
    result = subprocess.run(
        ["powershell", "-NoProfile", "-Command", script],
        capture_output=True,
        text=True,
        timeout=20,
        check=False,
    )
    rows = []
    for line in (result.stdout or "").splitlines():
        pid_text, separator, command = line.partition("\t")
        if separator and pid_text.strip():
            rows.append(f"pid {pid_text.strip()}: {command.strip()}")
    if not rows:
        return ""
    return "CodeQL processes still running:\n" + "\n".join(rows)


def held_process_error(pid: int, command: str) -> str:
    text = (
        "Another process is holding the query server and it did not answer.\n"
        f"pid: {pid}\n"
        f"command: {command or '(command line unavailable)'}"
    )
    others = codeql_process_report()
    if others:
        text = f"{text}\n{others}"
    return text


def crash_logs(folders: list[Path], since: float) -> str:
    parts: list[str] = []
    seen: set[Path] = set()
    for folder in folders:
        if not folder.is_dir():
            continue
        for path in folder.glob("hs_err_pid*.log"):
            resolved = path.resolve()
            if resolved in seen:
                continue
            try:
                modified = path.stat().st_mtime
            except OSError:
                continue
            if modified < since:
                continue
            seen.add(resolved)
            text = path.read_text(encoding="utf-8", errors="replace")[:_CRASH_LOG_CHARS]
            parts.append(f"--- {path} ---\n{text}")
    return "\n".join(parts)


class CodeQLQueryServer:
    """One `codeql execute query-server2` process for the life of the host."""

    def __init__(self, repo: Path | str, codeql: CodeQL) -> None:
        self.repo = Path(repo)
        self._codeql = codeql
        self._process: subprocess.Popen | None = None
        self._next_id = 1
        self._registered: set[str] = set()
        self._lock = threading.Lock()
        self._last_progress = ""
        self._on_line = None
        self._stderr_lines: list[str] = []
        self._stderr_thread: threading.Thread | None = None
        self._started_at = 0.0

    @classmethod
    def from_repo(cls, repo: Path | str) -> CodeQLQueryServer:
        root = Path(repo)
        return cls(root, CodeQL(root))

    @property
    def alive(self) -> bool:
        return self._process is not None and self._process.poll() is None

    @property
    def pid(self) -> int | None:
        if self._process is None:
            return None
        return self._process.pid

    def start(self) -> None:
        if self.alive:
            return
        executable = self._codeql.executable()
        ram = subprocess.run(
            [executable, "resolve", "ram", "--"],
            check=False,
            capture_output=True,
            text=True,
        )
        ram_args = [line.strip() for line in (ram.stdout or "").splitlines() if line.strip()]
        command = [
            executable,
            "execute",
            "query-server2",
            "--threads=0",
            "-q",
            *ram_args,
        ]
        flags = getattr(subprocess, "CREATE_NO_WINDOW", 0) if sys.platform == "win32" else 0
        self._process = subprocess.Popen(
            command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=str(self._codeql.repo_root()),
            creationflags=flags,
        )
        if self._process.stdout is None or self._process.stdin is None:
            raise CodeQLRunError("codeql query server produced no stdio streams")
        self._started_at = time.time()
        self._stderr_lines.clear()
        self._stderr_thread = threading.Thread(target=self._drain_stderr, daemon=True)
        self._stderr_thread.start()
        self._registered.clear()

    def stop(self) -> None:
        process = self._process
        self._process = None
        self._registered.clear()
        if process is None:
            return
        if process.stdin is not None:
            try:
                process.stdin.close()
            except OSError:
                pass
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self._kill_tree(process.pid)
                process.wait(timeout=5)
        elif process.pid:
            self._kill_tree(process.pid)

    def run_queries(self, queries, database: Path, on_line) -> dict[str, Path]:
        """Evaluate one batch on the warm server. Returns resolved query path to bqrs."""
        with self._lock:
            if not self.alive:
                raise QueryServerDown("codeql query server is not running")
            self._on_line = on_line
            self._last_progress = ""
            db = str(Path(database).resolve())
            self._register(db)
            folder = Path(database) / "results" / "query-server"
            folder.mkdir(parents=True, exist_ok=True)
            inputs = []
            outputs: dict[str, Path] = {}
            for query in queries:
                resolved = str(Path(query).resolve())
                bqrs = folder / f"{Path(query).stem}.bqrs"
                dil = bqrs.with_suffix(".dil")
                inputs.append(
                    {
                        "queryPath": resolved,
                        "outputPath": str(bqrs),
                        "dilPath": str(dil),
                    }
                )
                outputs[resolved] = bqrs
            result = self._request(
                "evaluation/runQueries",
                {
                    "inputOutputPaths": inputs,
                    "db": db,
                    "additionalPacks": [],
                    "externalInputs": {},
                    "singletonExternalInputs": {},
                },
            )
            failures: list[str] = []
            produced: dict[str, Path] = {}
            by_path = {
                str(Path(path).resolve()): value
                for path, value in (result or {}).items()
                if isinstance(value, dict)
            }
            for resolved, bqrs in outputs.items():
                entry = by_path.get(resolved) or {}
                result_type = entry.get("resultType", 1)
                if result_type != 0 or not bqrs.is_file():
                    message = entry.get("message") or f"resultType={result_type}"
                    failures.append(f"{Path(resolved).stem}: {message}")
                else:
                    produced[resolved] = bqrs
                dil = bqrs.with_suffix(".dil")
                if dil.is_file():
                    dil.unlink()
            if failures and not produced:
                raise CodeQLRunError("codeql query server failed: " + "; ".join(failures))
            if failures and on_line is not None:
                on_line("query-server partial: " + "; ".join(failures))
            return produced

    def _register(self, database: str) -> None:
        if database in self._registered:
            return
        self._request("evaluation/registerDatabases", {"databases": [database]})
        self._registered.add(database)

    def _request(self, method: str, body: dict) -> dict:
        request_id = self._next_id
        self._next_id += 1
        progress_id = self._next_id
        self._next_id += 1
        payload = {
            "jsonrpc": "2.0",
            "id": request_id,
            "method": method,
            "params": {"progressId": progress_id, "body": body},
        }
        raw = json.dumps(payload).encode("utf-8")
        process = self._process
        if process is None or process.stdin is None or process.stdout is None:
            raise QueryServerDown(self._failure("codeql query server is not running"))
        try:
            process.stdin.write(f"Content-Length: {len(raw)}\r\n\r\n".encode("ascii") + raw)
            process.stdin.flush()
        except OSError as error:
            raise QueryServerDown(self._failure(f"codeql query server stdin closed: {error}")) from error
        while True:
            try:
                message = self.read_message(process.stdout)
            except QueryServerDown as error:
                raise QueryServerDown(self._failure(str(error))) from error
            if message.get("id") != request_id:
                if message.get("method") == "ql/progressUpdated":
                    self._note_progress(message.get("params") or {})
                continue
            if "error" in message:
                err = message["error"]
                detail = err.get("message", err) if isinstance(err, dict) else err
                raise CodeQLRunError(self._failure(f"{method} failed: {detail}"))
            result = message.get("result")
            return result if isinstance(result, dict) else {}

    def _note_progress(self, params: dict) -> None:
        raw = str(params.get("message") or "").strip()
        step = params.get("step")
        maximum = params.get("maxStep")
        message = raw
        if raw.startswith("(") and isinstance(step, int) and isinstance(maximum, int) and maximum:
            message = f"{raw} {step}/{maximum}"
        if not message or message == self._last_progress:
            return
        self._last_progress = message
        phase = message.split(" ", 1)[0]
        if not raw.startswith("(") and ".ql" not in message and phase not in _PHASES:
            return
        if self._on_line is not None:
            self._on_line(message)

    def _failure(self, message: str) -> str:
        dump = self.crash_dump()
        text = message if not dump or dump in message else f"{message}\n{dump}"
        others = codeql_process_report()
        if others and others not in text:
            text = f"{text}\n{others}"
        return text

    def crash_dump(self) -> str:
        """Stderr plus any Java crash log written since this server started."""
        thread = self._stderr_thread
        if thread is not None:
            thread.join(timeout=1)
        process = self._process
        pid = process.pid if process is not None else None
        code = process.poll() if process is not None else None
        stderr = "\n".join(self._stderr_lines).strip()
        logs = crash_logs([self._codeql.repo_root(), Path.cwd()], self._started_at)
        parts = [f"query server pid {pid} exit {code}"]
        if stderr:
            parts.append(stderr)
        if logs:
            parts.append(logs)
        return "\n".join(parts)

    def _drain_stderr(self) -> None:
        process = self._process
        if process is None or process.stderr is None:
            return
        for line in process.stderr:
            text = line.decode("utf-8", errors="replace").rstrip("\r\n")
            if not text:
                continue
            self._stderr_lines.append(text)
            if len(self._stderr_lines) > _STDERR_LIMIT:
                del self._stderr_lines[: len(self._stderr_lines) - _STDERR_LIMIT]
            if self._on_line is not None:
                self._on_line(text)

    @staticmethod
    def read_message(stream) -> dict:
        headers: dict[str, str] = {}
        while True:
            line = stream.readline()
            if not line:
                raise QueryServerDown("codeql query server closed the stream")
            if line in (b"\r\n", b"\n"):
                break
            key, value = line.decode("ascii").split(":", 1)
            headers[key.strip().lower()] = value.strip()
        length = int(headers["content-length"])
        chunks: list[bytes] = []
        remaining = length
        while remaining:
            chunk = stream.read(remaining)
            if not chunk:
                raise QueryServerDown("codeql query server closed the stream")
            chunks.append(chunk)
            remaining -= len(chunk)
        return json.loads(b"".join(chunks))

    def _kill_tree(self, pid: int) -> None:
        terminate_process_tree(pid)
