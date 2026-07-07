"""Append-only JSONL log for stories CLI invocations.

When ``STORIES_CLI_LOG`` points at a file path, each CLI run appends one
record so eval runs (and humans) can reconstruct call order alongside
``cursor-agent`` logs under ``evals/.last-run/<case>/agent/``.
"""

from __future__ import annotations

import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _log_path() -> Path | None:
    raw = os.environ.get("STORIES_CLI_LOG", "").strip()
    return Path(raw) if raw else None


def log_cli_invocation(
    *,
    argv: list[str],
    started_at: str,
    elapsed_seconds: float,
    exit_code: int,
    command: str | None = None,
    fmt: str | None = None,
    workspace: str | None = None,
    output: str | None = None,
    tests_root: str | None = None,
    view: str | None = None,
    dry_run: bool = False,
    written: list[str] | None = None,
    stderr_tail: str | None = None,
) -> None:
    path = _log_path()
    if path is None:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    record: dict[str, Any] = {
        "kind": "stories-cli",
        "started_at": started_at,
        "finished_at": datetime.now(timezone.utc).isoformat(),
        "elapsed_seconds": round(elapsed_seconds, 3),
        "exit_code": exit_code,
        "argv": argv,
        "command": command,
        "format": fmt,
        "workspace": workspace,
        "output": output,
        "tests_root": tests_root,
        "view": view,
        "dry_run": dry_run,
        "written": written or [],
    }
    if stderr_tail:
        record["stderr_tail"] = stderr_tail
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, sort_keys=True) + "\n")


class CliInvocationTimer:
    """Context manager: log one stories CLI invocation on exit."""

    def __init__(self, args: Any) -> None:
        self._args = args
        self._started_at = datetime.now(timezone.utc).isoformat()
        self._t0 = time.perf_counter()
        self._exit_code = 0
        self._written: list[str] = []
        self._stderr_tail = ""

    def set_result(self, exit_code: int, written: list[str] | None = None) -> None:
        self._exit_code = exit_code
        if written is not None:
            self._written = written

    def capture_stderr_tail(self) -> None:
        # Best-effort: nothing buffered today; callers may set explicitly.
        pass

    def __enter__(self) -> "CliInvocationTimer":
        return self

    def __exit__(self, exc_type, exc, tb) -> bool:
        elapsed = time.perf_counter() - self._t0
        exit_code = self._exit_code if exc is None else 1
        if exc is not None:
            self._stderr_tail = str(exc)[-500:]
        args = self._args
        log_cli_invocation(
            argv=sys.argv,
            started_at=self._started_at,
            elapsed_seconds=elapsed,
            exit_code=exit_code,
            command=getattr(args, "command", None),
            fmt=getattr(args, "format", None),
            workspace=getattr(args, "workspace", None),
            output=getattr(args, "output", None),
            tests_root=getattr(args, "tests_root", None),
            view=getattr(args, "view", None),
            dry_run=bool(getattr(args, "dry_run", False)),
            written=self._written,
            stderr_tail=self._stderr_tail or None,
        )
        return False
