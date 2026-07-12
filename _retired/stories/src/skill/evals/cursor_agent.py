"""cursor-agent subprocess helpers — persistent session + streamed output."""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

_CHAT_ID_PATTERN = re.compile(
    r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}",
    re.IGNORECASE,
)
_PYTHON_CMD = re.compile(r"\bpython(?:\.exe)?\b", re.IGNORECASE)
_SKIP_READ_NAMES = frozenset({".stories-skill-trace", "run.txt", "agent-session.json"})
_DELIVERABLE_HINTS = ("story-map", "story-graph", "thin-slice", ".drawio")

# Per-run deduplication: prevent the same python tool-call command from being
# logged more than once.  --stream-partial-output can fire multiple "completed"
# events for the same tool invocation; tracking the hash here suppresses those
# duplicates.  reset() is called at the start of each run_agent call.
_seen_command_hashes: set[int] = set()


def _reset_run_state() -> None:
    _seen_command_hashes.clear()


class NotAuthenticatedError(RuntimeError):
    """Raised when cursor-agent has no valid session."""


def resolve_launcher() -> str | None:
    return shutil.which("cursor-agent")


def assert_authenticated() -> str:
    launcher = resolve_launcher()
    if launcher is None:
        raise NotAuthenticatedError("cursor-agent not on PATH")
    completed = subprocess.run(
        [launcher, "status"],
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    if completed.returncode != 0:
        raise NotAuthenticatedError(
            "cursor-agent is not authenticated.\n"
            "Run `cursor-agent login` first, then re-run.\n\n"
            f"stderr:\n{completed.stderr.strip()}"
        )
    return completed.stdout.strip()


def create_chat(workspace: Path) -> str:
    launcher = resolve_launcher()
    if launcher is None:
        raise FileNotFoundError("cursor-agent not on PATH")
    completed = subprocess.run(
        [launcher, "create-chat", "--workspace", str(workspace.resolve())],
        capture_output=True,
        text=True,
        timeout=60,
        check=True,
    )
    for token in completed.stdout.split():
        if _CHAT_ID_PATTERN.fullmatch(token):
            return token
    match = _CHAT_ID_PATTERN.search(completed.stdout)
    if match:
        return match.group(0)
    raise RuntimeError(
        f"cursor-agent create-chat did not return a chat id.\n"
        f"stdout:\n{completed.stdout}\nstderr:\n{completed.stderr}"
    )


@dataclass
class AgentSession:
    chat_id: str
    session_file: Path

    @classmethod
    def load(cls, session_file: Path) -> "AgentSession | None":
        if not session_file.is_file():
            return None
        try:
            data = json.loads(session_file.read_text(encoding="utf-8"))
            chat_id = str(data.get("chat_id", "")).strip()
        except (OSError, json.JSONDecodeError, TypeError):
            return None
        if not chat_id:
            return None
        return cls(chat_id=chat_id, session_file=session_file)

    def save(self) -> None:
        self.session_file.parent.mkdir(parents=True, exist_ok=True)
        self.session_file.write_text(
            json.dumps({"chat_id": self.chat_id}, indent=2),
            encoding="utf-8",
        )


def get_or_create_session(session_file: Path, workspace: Path, *, fresh: bool) -> AgentSession:
    if not fresh:
        existing = AgentSession.load(session_file)
        if existing is not None:
            return existing
    session = AgentSession(chat_id=create_chat(workspace), session_file=session_file)
    session.save()
    return session


@dataclass(frozen=True)
class AgentResult:
    exit_code: int
    stdout: str
    stderr: str
    elapsed_seconds: float

    def ok(self) -> bool:
        return self.exit_code == 0


def _tool_args(tool_call: dict) -> dict:
    if not tool_call:
        return {}
    args = tool_call.get("args")
    if isinstance(args, dict):
        return args
    return tool_call if isinstance(tool_call, dict) else {}


def _is_noise_tool(tool_call: dict) -> bool:
    args = _tool_args(tool_call)
    if "globPattern" in args:
        return True
    if "pattern" in args and "path" in args:
        return True
    for key in tool_call:
        lower = key.lower()
        if "glob" in lower or "grep" in lower or "search" in lower:
            return True
    return False


def _read_path_from_tool_call(tool_call: dict) -> str | None:
    for key in ("readToolCall", "ReadToolCall", "read"):
        if key in tool_call and isinstance(tool_call[key], dict):
            inner = tool_call[key]
            args = inner.get("args") if isinstance(inner.get("args"), dict) else inner
            path = args.get("path")
            if path:
                return str(path)
    args = _tool_args(tool_call)
    path = args.get("path")
    if path and "pattern" not in args and "globPattern" not in args:
        return str(path)
    return None


def _write_path_from_tool_call(tool_call: dict) -> str | None:
    for key in ("writeToolCall", "WriteToolCall", "editToolCall", "EditToolCall"):
        if key in tool_call and isinstance(tool_call[key], dict):
            inner = tool_call[key]
            args = inner.get("args") if isinstance(inner.get("args"), dict) else inner
            path = args.get("path")
            if path:
                return str(path)
    args = _tool_args(tool_call)
    if args.get("path") and ("streamContent" in args or "contents" in args):
        return str(args["path"])
    return None


def _shell_command_from_tool_call(tool_call: dict) -> str | None:
    if not tool_call:
        return None
    for key in (
        "shellToolCall",
        "ShellToolCall",
        "runTerminalCommandToolCall",
        "terminalToolCall",
    ):
        if key in tool_call and isinstance(tool_call[key], dict):
            inner = tool_call[key]
            args = inner.get("args") if isinstance(inner.get("args"), dict) else inner
            command = args.get("command") or args.get("cmd")
            if command:
                return str(command)
    command = tool_call.get("command") or tool_call.get("cmd")
    return str(command) if command else None


def _is_python_command(command: str) -> bool:
    return bool(_PYTHON_CMD.search(command))


def _should_skip_read_log(path: str) -> bool:
    name = Path(path).name
    if name in _SKIP_READ_NAMES:
        return True
    normalized = path.replace("/", "\\").lower()
    if "\\evals\\.last-run\\" in normalized and name == "run.txt":
        return True
    return False


def _extract_shell_output(tool_call: dict, event: dict | None = None) -> str | None:
    def _walk(node: object) -> str | None:
        if isinstance(node, str):
            stripped = node.strip()
            return stripped or None
        if not isinstance(node, dict):
            return None
        for key in ("stdout", "stderr", "output", "text", "content"):
            value = node.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
        for value in node.values():
            found = _walk(value)
            if found:
                return found
        return None

    for root in (tool_call, event or {}):
        found = _walk(root)
        if found:
            return found
    return None


def _shell_output_is_echo(command: str, output: str) -> bool:
    out = output.strip()
    cmd = command.strip()
    if not out or out == cmd or out in cmd or cmd in out:
        return True
    return out.startswith("$") and "python" in out.lower()


def _parse_manifest(stdout: str) -> dict | None:
    try:
        payload = json.loads(stdout)
    except json.JSONDecodeError:
        return None
    if isinstance(payload, dict) and "files_by_directory" in payload:
        return payload
    return None


def _handle_tool_event(subtype: str, tool_call: dict, event: dict) -> None:
    """Append structured trace blocks to run.txt + console."""
    try:
        from stories.src.skill import skill_trace as trace  # noqa: WPS433
    except ImportError:
        return

    if _is_noise_tool(tool_call):
        return

    is_done = subtype in ("completed", "complete", "succeeded", "success", "finished")
    is_start = subtype in ("started", "start", "running", "pending")

    command = _shell_command_from_tool_call(tool_call)
    if command and _is_python_command(command):
        lower = command.lower()
        if is_start:
            if "assemble_components" in lower:
                phase = trace.extract_flag(command, "phase") or "?"
                trace.emit_progress(f"  → ASSEMBLE --phase {phase} …")
            elif "cli/main.py" in lower:
                trace.emit_progress("  → STORIES CLI …")
            elif "scanner" in lower or "run_scanners" in lower:
                trace.emit_progress("  → SCANNER …")
        if not is_done:
            return

    if not is_done:
        return

    read_path = _read_path_from_tool_call(tool_call)
    if read_path and not _should_skip_read_log(read_path) and trace.should_log_read(read_path):
        trace.log_read(read_path)
        return

    write_path = _write_path_from_tool_call(tool_call)
    if write_path and any(h in write_path.lower() for h in _DELIVERABLE_HINTS):
        trace.log_write_deliverable(write_path)
        return

    if not command or not _is_python_command(command):
        return

    cmd_hash = hash(command.strip())
    if cmd_hash in _seen_command_hashes:
        return
    _seen_command_hashes.add(cmd_hash)

    output = _extract_shell_output(tool_call, event)
    if output and _shell_output_is_echo(command, output):
        output = None

    lower = command.lower()
    if "assemble_components" in lower:
        manifest = _parse_manifest(output) if output else None
        if manifest is None:
            manifest = trace.replay_assemble_manifest(command)
        trace.log_assemble_call(
            params=trace.parse_assemble_params(command),
            manifest=manifest,
            command=command,
        )
    elif "stories/cli/main.py" in lower or "cli/main.py" in lower:
        written: list[str] = []
        if output:
            try:
                payload = json.loads(output)
                written = list(payload.get("written") or [])
            except json.JSONDecodeError:
                pass
        params: dict[str, str] = {}
        for flag in ("format", "workspace", "view", "command", "output", "tests-root"):
            match = re.search(rf"--{re.escape(flag)}(?:=|\s+)(\"[^\"]+\"|\S+)", command)
            if match:
                params[flag] = match.group(1).strip('"')
        trace.log_stories_cli_call(
            command=command,
            params=params,
            written=written or None,
            output=output if output and not written else None,
        )
    elif "run_scanners" in lower or "-scanner.py" in lower or "run_scanners.py" in lower:
        pass  # Scanner results are logged authoritatively by the eval runner after agent completes.


_SCAN_LINE_RE = re.compile(
    r"^#\s*(?:scan|rule)\s+([\w-]+):\s*(PASS|FAIL|SKIP|NO_SCANNER)(.*)?$",
    re.IGNORECASE,
)


def _parse_run_scanners_output(output: str) -> list[tuple[str, str, str]]:
    """Parse `# scan/rule <name>: PASS/FAIL/SKIP/NO_SCANNER` lines from run_scanners.py."""
    results: list[tuple[str, str, str]] = []
    for line in output.splitlines():
        m = _SCAN_LINE_RE.match(line.strip())
        if m:
            name = m.group(1)
            tag = m.group(2).upper()
            reason = (m.group(3) or "").strip().lstrip("—").strip()
            results.append((name, tag, reason))
    return results


def _parse_foreach_scanner_output(
    output: str,
) -> list[tuple[str, str, str]]:
    """Parse a foreach-loop scanner run's mixed stdout/stderr into per-scanner tuples.

    Each scanner emits:
      - JSON violation lines to stdout (one per violation)
      - A summary comment "# ScannerName: N violation(s) …" to stderr (captured via 2>&1)
    """
    results: list[tuple[str, str, str]] = []
    current: str | None = None
    viols: list[str] = []

    for raw in output.splitlines():
        line = raw.strip()
        # Section header written by the foreach: "=== rules/foo/foo-scanner.py ==="
        if line.startswith("===") and "-scanner" in line.lower():
            if current is not None:
                tag = "FAIL" if viols else "PASS"
                results.append((current, tag, "; ".join(viols[:2])))
            m = re.search(r"([^/\\\s\"']+)-scanner", line, re.IGNORECASE)
            current = m.group(1) if m else line.strip("= ")
            viols = []
        elif line.startswith("{"):
            try:
                obj = json.loads(line)
                msg = obj.get("message", "")
                if msg:
                    viols.append(msg)
            except json.JSONDecodeError:
                pass

    if current is not None:
        tag = "FAIL" if viols else "PASS"
        results.append((current, tag, "; ".join(viols[:2])))

    return results


def _parse_stream_line(
    line: str,
    on_narrative: Callable[[str], None],
    on_tool: Callable[[str], None] | None = None,
) -> None:
    line = line.strip()
    if not line:
        return
    try:
        event = json.loads(line)
    except json.JSONDecodeError:
        return
    if not isinstance(event, dict):
        return
    kind = event.get("type")
    if kind == "assistant":
        message = event.get("message") or {}
        for block in message.get("content") or []:
            if isinstance(block, dict) and block.get("type") == "text":
                text = block.get("text")
                if isinstance(text, str) and text:
                    on_narrative(text)
    elif kind == "result":
        # cursor-agent emits a {"type":"result","result":"..."} event when the
        # agent completes without using any tools (e.g. the coarse judge prompt).
        text = event.get("result")
        if isinstance(text, str) and text.strip():
            on_narrative(text)
    if kind == "tool_call":
        subtype = str(event.get("subtype") or event.get("state") or "event")
        tool_call = event.get("tool_call") or {}
        if not isinstance(tool_call, dict):
            tool_call = {}
        _handle_tool_event(subtype, tool_call, event)


def run_agent(
    session: AgentSession,
    prompt: str,
    workspace: Path,
    *,
    timeout_seconds: int = 900,
    model: str | None = None,
    on_stdout: Callable[[str], None] | None = None,
    on_stderr: Callable[[str], None] | None = None,
    on_narrative: Callable[[str], None] | None = None,
    on_tool: Callable[[str], None] | None = None,
    echo: bool = False,
    extra_env: dict[str, str] | None = None,
) -> AgentResult:
    launcher = resolve_launcher()
    if launcher is None:
        raise FileNotFoundError("cursor-agent not on PATH")

    args = [
        launcher,
        "-p",
        "--force",
        "--trust",
        "--resume",
        session.chat_id,
        "--workspace",
        str(workspace.resolve()),
        "--output-format",
        "stream-json",
        "--stream-partial-output",
    ]
    if model:
        args.extend(["--model", model])

    # Write long prompts to a file in the workspace to avoid Windows
    # command-line length limits (~32 KB).  The agent reads the file itself.
    import tempfile as _tempfile
    _prompt_file: "_tempfile._TemporaryFileWrapper[str] | None" = None  # type: ignore[assignment]
    _CMDLINE_SAFE = 4096
    if len(prompt) > _CMDLINE_SAFE:
        _prompt_file = _tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".txt",
            dir=str(workspace.resolve()),
            delete=False,
            encoding="utf-8",
            prefix="_prompt_",
        )
        _prompt_file.write(prompt)
        _prompt_file.flush()
        _prompt_file.close()
        short = f"Read the file `{Path(_prompt_file.name).name}` in the workspace and follow its instructions exactly."
        args.append(short)
    else:
        args.append(prompt)

    _reset_run_state()

    narrative_cb = on_narrative or on_stdout or (lambda _t: None)
    narrative_parts: list[str] = []
    raw_lines: list[str] = []  # every raw stdout line — fallback for verdict parsing
    stderr_parts: list[str] = []

    def emit_narrative(text: str) -> None:
        narrative_parts.append(text)

    def emit_stderr(text: str) -> None:
        stderr_parts.append(text)
        if on_stderr is not None:
            on_stderr(text)
        if echo:
            sys.stderr.write(text)
            sys.stderr.flush()

    started = time.perf_counter()
    env = os.environ.copy()
    if extra_env:
        env.update({k: v for k, v in extra_env.items() if v is not None})
    proc = subprocess.Popen(
        args,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
        env=env,
    )

    def _read_stdout() -> None:
        assert proc.stdout is not None
        for line in proc.stdout:
            raw_lines.append(line)
            _parse_stream_line(line, emit_narrative, None)

    def _read_stderr() -> None:
        assert proc.stderr is not None
        for chunk in iter(lambda: proc.stderr.read(4096), ""):
            emit_stderr(chunk)

    threads = [
        threading.Thread(target=_read_stdout, daemon=True),
        threading.Thread(target=_read_stderr, daemon=True),
    ]
    for thread in threads:
        thread.start()

    heartbeat_stop = threading.Event()

    def _heartbeat() -> None:
        try:
            from stories.src.skill.skill_trace import emit_progress  # noqa: WPS433
        except ImportError:
            return
        while not heartbeat_stop.wait(20):
            emit_progress("  … agent still working …")

    heartbeat = threading.Thread(target=_heartbeat, daemon=True)
    heartbeat.start()

    try:
        exit_code = proc.wait(timeout=timeout_seconds)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait()
        for thread in threads:
            thread.join()
        raise
    finally:
        heartbeat_stop.set()
        heartbeat.join(timeout=1)

    for thread in threads:
        thread.join()

    if _prompt_file is not None:
        try:
            os.unlink(_prompt_file.name)
        except OSError:
            pass

    # If the event-based parser captured narrative, use it.  Otherwise fall
    # back to the raw stream lines so verdict patterns can be found even when
    # cursor-agent uses an event format we don't recognise.
    stdout = "".join(narrative_parts) or "".join(raw_lines)
    return AgentResult(
        exit_code=exit_code,
        stdout=stdout,
        stderr="".join(stderr_parts),
        elapsed_seconds=time.perf_counter() - started,
    )
