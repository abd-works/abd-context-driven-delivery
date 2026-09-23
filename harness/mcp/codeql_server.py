"""Long-lived CodeQL query-server2 owned by the MCP host process."""
from __future__ import annotations

import json
import os
import subprocess
import sys
import threading
from pathlib import Path

from harness.knowledge_graph.model.codeql import CodeQL, CodeQLRunError, QueryServerDown

_PHASES = {"Compiling", "Running", "Writing", "Shutting"}


class CodeQLQueryServer:
    """One `codeql execute query-server2` process for the life of the host."""

    def __init__(self, repo: Path | str) -> None:
        self.repo = Path(repo)
        self._codeql = CodeQL(self.repo)
        self._process: subprocess.Popen | None = None
        self._next_id = 1
        self._registered: set[str] = set()
        self._lock = threading.Lock()
        self._last_progress = ""
        self._on_line = None

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
        threading.Thread(target=self._drain_stderr, daemon=True).start()
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
            raise QueryServerDown("codeql query server is not running")
        try:
            process.stdin.write(f"Content-Length: {len(raw)}\r\n\r\n".encode("ascii") + raw)
            process.stdin.flush()
        except OSError as error:
            raise QueryServerDown(f"codeql query server stdin closed: {error}") from error
        while True:
            message = self.read_message(process.stdout)
            if message.get("id") != request_id:
                if message.get("method") == "ql/progressUpdated":
                    self._note_progress(message.get("params") or {})
                continue
            if "error" in message:
                err = message["error"]
                detail = err.get("message", err) if isinstance(err, dict) else err
                raise CodeQLRunError(f"{method} failed: {detail}")
            result = message.get("result")
            return result if isinstance(result, dict) else {}

    def _note_progress(self, params: dict) -> None:
        message = str(params.get("message") or "").strip()
        if not message or message == self._last_progress or message.startswith("("):
            return
        self._last_progress = message
        phase = message.split(" ", 1)[0]
        if ".ql" not in message and phase not in _PHASES:
            return
        if self._on_line is not None:
            self._on_line(message)

    def _drain_stderr(self) -> None:
        process = self._process
        if process is None or process.stderr is None:
            return
        for line in process.stderr:
            text = line.decode("utf-8", errors="replace").rstrip("\r\n")
            if text and self._on_line is not None:
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

    @staticmethod
    def _kill_tree(pid: int) -> None:
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
