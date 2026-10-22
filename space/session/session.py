"""Session — work paths, logging, and practice graphs for the active process session."""

from __future__ import annotations

import json
import os
import re
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING

from harness.agent_tools import agent_instructions, agent_tool, agent_toolset
from harness.installation.files import command
from harness.mcp.mcp_server import mcp

if TYPE_CHECKING:
    from harness.graph.graph import Graph
    from harness.guidance.guidance import PracticeGuidance
    from space.repo.repo import Repo


_SOURCE_SUFFIXES = {".py", ".ts", ".tsx", ".js", ".jsx"}
_LOAD_FILE_BUDGET = 40
_DEFAULT_SESSION_NAME = "default"
_REPO_SESSIONS_DIR = ".sessions"
_LEGACY_REPO_SESSIONS_DIR = "sessions"
_LOOP_MARKER = re.compile(r"---\s+(\d+)(?:\s|$)")
_KNOWN_ACTIONS = (
    "generate",
    "validate",
    "sketch",
    "document",
    "satisfy",
    "iterate",
    "createRule",
)
_TOOL_INPUT_PATH_KEYS = (
    "path",
    "file_path",
    "target_directory",
    "working_directory",
    "transcript_path",
    "agent_transcript_path",
)


def _parse_chat_file(path: Path) -> tuple[str, str, str]:
    if not path.is_file():
        return path.stem, "", ""
    lines = path.read_text(encoding="utf-8").splitlines()
    chat_id = ""
    line_numbers = ""
    body_start = 0
    for index, line in enumerate(lines):
        if not line.strip():
            body_start = index + 1
            break
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        token = key.strip().lower().replace("_", "-")
        text = value.strip()
        if token in {"chat-id", "conversation-id"}:
            chat_id = text
        elif token == "lines":
            line_numbers = text
    else:
        body_start = len(lines)
    body = "\n".join(lines[body_start:]).strip()
    if not chat_id:
        chat_id = path.stem
    if not line_numbers:
        count = len(body.splitlines()) if body else 1
        line_numbers = f"1-{count}" if count > 1 else "1"
    return chat_id, line_numbers, body


class Loop:
    """One span of context, generation, and evaluation inside a session."""

    def __init__(self, number: int) -> None:
        self.number = number
        self.entries: list[str] = []
        self._session: Session | None = None

    def text(self) -> str:
        """Log lines for this loop plus any chat injected under them."""
        return "\n".join(self.entries)

    def expanded_text(self) -> str:
        """Log lines for this loop with referenced chat transcript slices inlined."""
        from space.session.chat_transcript import expand_log_lines

        return expand_log_lines(self.entries)

    def inject(self, chat_file: Path, *, action: str | None = None) -> None:
        path = Path(chat_file)
        chat_id, line_numbers, body = _parse_chat_file(path)
        pointer = f"{chat_id} {path} {line_numbers}".strip()
        session = self._session
        action_name = action or self._action_from_entries()
        if session is not None and action_name:
            session.note_chat(chat_id, path, line_numbers)
            session.append_chat(action_name, path)
        self.entries.append(pointer)
        if body:
            self.entries.extend(body.splitlines())

    def _action_from_entries(self) -> str:
        for line in reversed(self.entries):
            for name in _KNOWN_ACTIONS:
                if f" {name} " in f" {line} " or line.endswith(f" {name}"):
                    return name
        return ""


class Practice:
    """One practice guideline and the graph of that same practice."""

    def __init__(self, name: str, guideline: PracticeGuidance, graph: Graph, folder_sets: list) -> None:
        self.name = name
        self.guideline = guideline
        self.graph = graph
        self.folder_sets = folder_sets

    def to_mcp_result(self) -> dict:
        """JSON-safe snapshot for MCP tool results."""
        return {
            "name": self.name,
            "folder_sets": [[str(Path(item)) for item in group] for group in self.folder_sets],
        }


_PRACTICE_TYPES = {
    "stories": "cdd_guidance.practices.stories.stories:Stories",
    "clean_engineering": "cdd_guidance.practices.clean_engineering.clean_engineering:CleanEngineering",
    "ddd": "cdd_guidance.practices.ddd.ddd:Ddd",
    "bdd": "cdd_guidance.practices.bdd.bdd:Bdd",
    "ux": "cdd_guidance.practices.ux.ux:Ux",
}


@agent_toolset
class Session:
    """Process session — one in-memory current; new and switch open named sessions."""

    _current: Session | None = None

    def __init__(self, repo_root: Path | str | None = None) -> None:
        self._session_name = ""
        self.workpath: Path | None = None
        self.repo_path: Path | None = Path(repo_root).resolve() if repo_root else None
        self.session_path: Path | None = None
        self._loops: list[Loop] = []
        self._parent_folders: dict = {}
        self._opened: list[Practice] = []
        self._injected: list[tuple[str, str, str, str]] = []
        self._chat: tuple[str, Path, str] | None = None

    @property
    def name(self) -> str:
        """Named work session (not the toolset slug)."""
        return self._session_name

    @name.setter
    def name(self, value: str) -> None:
        self._session_name = (value or "").strip()

    def to_mcp_result(self) -> dict:
        """JSON-safe snapshot for MCP tool results — name, paths, practice roots."""
        return {
            "name": self.name,
            "workpath": None if self.workpath is None else str(self.workpath),
            "repo_path": None if self.repo_path is None else str(self.repo_path),
            "session_path": None if self.session_path is None else str(self.session_path),
            "practices": [entry.to_mcp_result() for entry in self._opened],
            "parent_folders": self._stored_folders(),
            "practice_roots": self._practice_roots_snapshot(),
        }

    def _practice_roots_snapshot(self) -> dict[str, list[list[str]]]:
        stored = self._stored_folders()
        roots: dict[str, list[list[str]]] = {}
        for name in _PRACTICE_TYPES:
            roots[name] = stored.get(name) or self._default_folder_sets(
                self._guidance_for(name), name
            )
        return roots

    @classmethod
    def _slot(cls) -> Session:
        if cls._current is None:
            cls._current = cls()
        return cls._current

    @classmethod
    def refresh_current_from_repo(cls, repo_path: Path | str | None = None) -> None:
        """Reload in-memory session when repo ``.sessions/session.json`` current changed."""
        slot = cls._slot()
        repo = slot.repo_from_session(repo_path)
        if repo is None:
            return
        slot.repo_path = repo
        saved = cls._read_repo_current_name(repo)
        if saved == _DEFAULT_SESSION_NAME:
            return
        current = cls._current
        if (
            current is not None
            and current.name == saved
            and current.session_path is not None
            and current.repo_path == repo
        ):
            return
        cls._current = None
        session = cls._slot()
        session.repo_path = repo
        session.resolve(saved, repo_path=repo)

    @classmethod
    def _read_repo_current_name(cls, repo_path: Path) -> str:
        path = cls.sessions_dir(repo_path) / "session.json"
        if not path.is_file():
            return _DEFAULT_SESSION_NAME
        state = json.loads(path.read_text(encoding="utf-8"))
        cleaned = str(state.get("current") or _DEFAULT_SESSION_NAME).strip()
        return cleaned or _DEFAULT_SESSION_NAME

    @classmethod
    @mcp
    @command(name="current-session")
    @agent_tool
    def current(cls, repo_path: Path | str | None = None) -> Session | None:
        """Named session already in memory, or the one saved on the repo."""
        cls.refresh_current_from_repo(repo_path)
        if cls._current is not None and cls._current.name:
            return cls._current
        session = cls._slot()
        repo = session.repo_from_session(repo_path)
        if repo is None:
            return None
        session.repo_path = repo
        name = session.saved_current_session
        if name == _DEFAULT_SESSION_NAME:
            return None
        session.resolve(name, repo_path=repo)
        return session if session.name else None

    def repo_from_session(self, repo_path: Path | str | None = None) -> Path | None:
        """Repo that holds ``.sessions`` — the path already in hand, not a git lookup."""
        if repo_path is not None:
            return Path(repo_path).resolve()
        if self.repo_path is not None:
            return Path(self.repo_path).resolve()
        named = os.environ.get("CDD_REPO")
        if named:
            return Path(named).resolve()
        project = os.environ.get("CDD_PROJECT")
        if project:
            return Path(project).resolve()
        return Path.cwd().resolve()

    @mcp
    @command(name="close-session")
    @agent_tool
    def close(self) -> None:
        """Close this work session and clear the saved current session on the repo."""
        if self.repo_path is not None:
            self.saved_current_session = _DEFAULT_SESSION_NAME
        self.name = ""
        self.workpath = None
        self.session_path = None
        self.reset()

    @classmethod
    @mcp
    @agent_tool
    def new(cls, name: str, workpath: Path, repo_path: Path) -> str:
        """Open a session. Returns keep_log."""
        session = cls._slot()
        session._bind_new(name, Path(workpath), Path(repo_path))
        return session.keep_log()

    @classmethod
    @mcp
    @agent_tool
    def switch(
        cls,
        name: str,
        workpath: Path | None = None,
        repo_path: Path | None = None,
        session_path: Path | None = None,
    ) -> str:
        """Open an existing session. Returns keep_log."""
        session = cls._slot()
        session.resolve(name, workpath, repo_path, session_path)
        return session.keep_log()

    @classmethod
    @mcp
    @command(name="session")
    @agent_tool
    def session(
        cls,
        name: str,
        workpath: Path | None = None,
        repo_path: Path | None = None,
    ) -> str:
        """Chaining: create session ``name`` when missing; switch and set repo current when it exists."""
        return cls.open_or_switch(name, workpath=workpath, repo_path=repo_path)

    @classmethod
    @mcp
    def open_named(
        cls,
        name: str,
        workpath: Path | None = None,
        repo_path: Path | None = None,
    ) -> str:
        """MCP alias for :meth:`session` (older clients call ``session.open_named``)."""
        return cls.session(name, workpath=workpath, repo_path=repo_path)

    @classmethod
    def open_or_switch(
        cls,
        name: str,
        workpath: Path | None = None,
        repo_path: Path | None = None,
    ) -> str:
        """Select a session folder when it exists, otherwise create it."""
        cleaned = (name or "").strip()
        if not cleaned:
            raise ValueError("session name is required")
        slot = cls._slot()
        primary = Path(repo_path).resolve() if repo_path is not None else slot.repo_from_session() or slot._env_repo()
        work = Path(workpath).resolve() if workpath is not None else slot._env_workpath()
        session_json = cls._session_folder(primary, cleaned) / "session.json"
        if session_json.is_file():
            return cls.switch(cleaned, workpath=work, repo_path=primary)
        return cls.new(cleaned, work, primary)

    @classmethod
    @command(name="new-session")
    @agent_instructions
    def new_session_command(cls) -> str:
        """Open a new CDD session folder under the repo.

        Ask the user for the session name when it is not already clear from the chat.
        Resolve workpath from CDD_PROJECT or the current working directory and repo from CDD_REPO or the current directory.
        Call MCP ``session.new`` with name, workpath, and repo_path. Do not call ``session.open_named``."""
        return ""

    @classmethod
    @command(name="switch-session")
    @agent_instructions
    def switch_session_command(cls) -> str:
        """Switch to an existing CDD session and set it current on disk.

        Ask the user for the session name when it is not already clear from the chat.
        Call MCP ``session.switch`` with that name (paths optional — loaded from the session folder).
        Do not call ``session.open_named``."""
        return ""

    @classmethod
    @mcp
    @command(name="mark-loop")
    @agent_tool
    def mark_loop(
        cls,
        conversation_id: str = "",
        transcript_path: str = "",
        transcript_lines: str = "",
    ) -> str:
        """Mark the next loop in the open session log (slash ``/mark-loop``).

        Pass ``conversation_id``, ``transcript_path``, and ``transcript_lines`` (cumulative JSONL
        range for this chat). Dispatch logs ``session.mark_loop``; the ``--- N`` marker carries the
        same pointer when chat is bound."""
        session = cls.current()
        if session is None or not session.name:
            raise ValueError("no current session; open one with session.new or session.switch")
        session._bind_chat_for_append(conversation_id, transcript_path, transcript_lines)
        opened = session.loop()
        return str(opened.number)

    @classmethod
    @mcp
    @command(name="read-loop")
    @agent_tool
    def read_loop(cls, number: int | None = None) -> str:
        """Read one loop from the current session log with chat transcript lines inlined.

        ``number`` defaults to the highest ``--- N`` marker in session.log.
        Run via MCP ``session.read_loop`` or slash ``/read-loop``."""
        session = cls.current()
        if session is None or not session.name:
            raise ValueError("no current session; open one with session.new or session.switch")
        if number is None:
            loop_number = session._latest_loop_with_entries()
        else:
            loop_number = number
        if loop_number < 1:
            raise ValueError("no loops in session.log; run mark-loop first")
        opened = session.loop_at(loop_number)
        if not opened.entries:
            raise ValueError(f"loop {loop_number} not found (missing --- {loop_number} in session.log?)")
        header = f"# Loop {loop_number} ({session.name})\n\n"
        return header + opened.expanded_text()

    @classmethod
    @mcp
    @command(name="append-log")
    @agent_tool
    def append_log(
        cls,
        note: str,
        loop: int | None = None,
        paths: list[str] | None = None,
        conversation_id: str = "",
        transcript_path: str = "",
        transcript_lines: str = "",
    ) -> str:
        """Append a correction or audit note to the open session log (slash ``/append-log``).

        **Agent steps:** confirm the open session; resolve ``loop`` (argument or latest loop with
        entries — use ``read_loop`` to inspect); capture conversation id, transcript JSONL path,
        and line range for this turn; write a short ``note`` (what changed, ``paths``, cross-refs to
        earlier ``session.log`` lines); call MCP ``session.append_log`` with those fields.

        Omit ``loop`` to target the latest loop with log lines. Pass ``conversation_id``,
        ``transcript_path``, and ``transcript_lines`` when hook metadata is missing.
        Do not edit ``session.log`` by hand.

        **Session artifacts:** whenever an open session exists, write large or temporary
        outputs (MCP ``graph_return_nodes`` JSON, diagnostics dumps, probe results) under
        ``session_path`` on that repo (e.g. ``repo/.sessions/{name}/``). Do not leave the
        only copy under Cursor ``.cursor/projects/.../agent-tools``. Reference those files
        in ``paths`` on this call."""
        session = cls.current()
        if session is None or not session.name:
            raise ValueError("no current session; open one with session.new or session.switch")
        text = (note or "").strip()
        if not text:
            raise ValueError("note is required")
        session._bind_chat_for_append(conversation_id, transcript_path, transcript_lines)
        loop_number = session._resolve_append_loop(loop)
        path_objs = [Path(item) for item in (paths or []) if str(item).strip()]
        body = text if text.lower().startswith(f"loop {loop_number}") else f"loop {loop_number}: {text}"
        session.log_note(body, path_objs or None)
        log_path = session.session_path / "session.log" if session.session_path else "session.log"
        return f"appended note to {log_path} (loop {loop_number})"

    @property
    def saved_current_session(self) -> str:
        """``current`` in repo/.sessions/session.json."""
        if self.repo_path is None:
            return _DEFAULT_SESSION_NAME
        path = self.sessions_dir(self.repo_path) / "session.json"
        if not path.is_file():
            return _DEFAULT_SESSION_NAME
        state = json.loads(path.read_text(encoding="utf-8"))
        cleaned = str(state.get("current") or _DEFAULT_SESSION_NAME).strip()
        return cleaned or _DEFAULT_SESSION_NAME

    @saved_current_session.setter
    def saved_current_session(self, name: str) -> None:
        if self.repo_path is None:
            return
        path = self.sessions_dir(self.repo_path) / "session.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        state = json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}
        cleaned = (name or "").strip() or _DEFAULT_SESSION_NAME
        state["current"] = cleaned
        path.write_text(json.dumps(state), encoding="utf-8")
        if cleaned != _DEFAULT_SESSION_NAME:
            from harness.hooks.session_logs import SessionLogs

            SessionLogs(self.repo_path).write_active_session(cleaned)

    def practice(self, name: str) -> Practice:
        found = self._opened_named(name)
        if found is not None:
            return found
        guidance = self._guidance_for(name)
        sets = self._stored_folders().get(name) or self._default_folder_sets(guidance, name)
        folders = [[Path(item) for item in group] for group in sets]
        opened = Practice(name, guidance, self._graph_for(name, folders), sets)
        self._opened.append(opened)
        return opened

    @property
    def practices(self) -> list[Practice]:
        return list(self._opened)

    @property
    def loops(self) -> list[Loop]:
        return list(self._loops)

    @property
    def repo(self) -> Repo | None:
        if self.repo_path is None:
            return None
        from space.repo.repo import Repo

        return Repo(self.repo_path)

    def remember_parent_folders(self, practice: str, folder_sets: list[list[Path]]) -> None:
        stored = self._stored_folders()
        normalized = self._normalize_sets(folder_sets)
        if normalized == self._default_folder_sets(self._guidance_for(practice), practice):
            stored.pop(practice, None)
        else:
            stored[practice] = normalized
        self._write_practices_json(stored)
        self._parent_folders = stored

    def note_injected_rule(
        self, practice: str, fidelity: str, rule: str, matched_path: str = ""
    ) -> None:
        entry = (practice, fidelity, rule, matched_path)
        if entry not in self._injected:
            self._injected.append(entry)

    def note_chat(self, chat_id: str, chat_file: Path, line_numbers: str) -> None:
        self._chat = (chat_id, Path(chat_file), line_numbers)

    def reset(self) -> None:
        self._opened = []

    def resolve(
        self,
        name: str,
        workpath: Path | None = None,
        repo_path: Path | None = None,
        session_path: Path | None = None,
    ) -> Session:
        self.name = name
        if session_path is not None:
            self.session_path = Path(session_path).resolve()
            stored = self._read_session_folder_json(self.session_path)
            if workpath is not None:
                self.workpath = Path(workpath).resolve()
            elif stored.get("workpath"):
                self.workpath = Path(stored["workpath"])
            if stored.get("repo_path"):
                self.repo_path = Path(stored["repo_path"])
            else:
                self.repo_path = self._repo_holding(self.session_path)
        elif repo_path is not None:
            self.repo_path = Path(repo_path).resolve()
            self.session_path = self._session_folder(self.repo_path, name)
            stored = self._read_session_folder_json(self.session_path)
            if workpath is not None:
                self.workpath = Path(workpath).resolve()
            elif stored.get("workpath"):
                self.workpath = Path(stored["workpath"])
            else:
                self.workpath = self._env_workpath()
        elif workpath is not None:
            self.workpath = Path(workpath).resolve()
            self.repo_path = self._env_repo()
            self.session_path = self._session_folder(self.repo_path, name)
        else:
            self.repo_path = self._env_repo()
            self.session_path = self._session_folder(self.repo_path, name)
            stored = self._read_session_folder_json(self.session_path)
            if stored.get("workpath"):
                self.workpath = Path(stored["workpath"])
            else:
                self.workpath = self._env_workpath()
        self._read_practices_json()
        self.saved_current_session = name
        self._write_session_folder_json()
        return self

    def __getitem__(self, number: int) -> Loop:
        return self.loop_at(number)

    def loop_at(self, number: int) -> Loop:
        """Return loop ``number`` with log lines read from session.log (and chat via inject)."""
        opened = Loop(number)
        opened._session = self
        opened.entries = self._lines_for_loop(number)
        return opened

    def _max_loop_number_from_log(self) -> int:
        if self.session_path is None:
            return 0
        log = self.session_path / "session.log"
        if not log.is_file():
            return 0
        highest = 0
        for line in log.read_text(encoding="utf-8").splitlines():
            match = _LOOP_MARKER.search(line)
            if match:
                highest = max(highest, int(match.group(1)))
        return highest

    def _latest_loop_with_entries(self) -> int:
        highest = self._max_loop_number_from_log()
        for candidate in range(highest, 0, -1):
            if self._lines_for_loop(candidate):
                return candidate
        return 0

    def _resolve_append_loop(self, loop: int | None) -> int:
        if loop is not None:
            if loop < 1:
                raise ValueError("loop must be >= 1")
            if self._max_loop_number_from_log() < loop:
                raise ValueError(f"loop {loop} not found in session.log (no --- {loop} marker)")
            return loop
        chosen = self._latest_loop_with_entries()
        if chosen < 1:
            chosen = self._max_loop_number_from_log()
        if chosen < 1:
            raise ValueError("no loop in session.log; run mark-loop first")
        return chosen

    def _bind_chat_for_append(
        self,
        conversation_id: str,
        transcript_path: str,
        transcript_lines: str,
    ) -> None:
        from space.session.chat_context import apply_chat_context, set_chat_context

        chat_id = (conversation_id or "").strip()
        transcript = (transcript_path or "").strip()
        lines = (transcript_lines or "").strip()
        if chat_id and transcript:
            set_chat_context(chat_id, transcript, lines)
        apply_chat_context(self)

    def loop(self) -> Loop:
        from_memory = self._loops[-1].number if self._loops else 0
        from_log = self._max_loop_number_from_log()
        number = max(from_memory, from_log) + 1
        opened = Loop(number)
        opened._session = self
        self._loops.append(opened)
        self.require_chat_noted()
        marker = f"--- {number}"
        chat = self._noted_chat()
        self._append_log(f"{marker} {chat}".strip() if chat else marker)
        self._chat = None
        return opened

    @staticmethod
    def _loop_marker_number(line: str) -> int | None:
        match = _LOOP_MARKER.search(line)
        if not match:
            return None
        return int(match.group(1))

    def _lines_for_loop(self, number: int) -> list[str]:
        if self.session_path is None:
            return []
        log = self.session_path / "session.log"
        if not log.is_file():
            return []
        raw = log.read_text(encoding="utf-8").splitlines()
        marker_index: int | None = None
        for index, line in enumerate(raw):
            if self._loop_marker_number(line) == number:
                marker_index = index
                break
        if marker_index is None:
            return []
        collected: list[str] = [raw[marker_index]]
        for line in raw[marker_index + 1 :]:
            other = self._loop_marker_number(line)
            if other is not None and other != number:
                break
            collected.append(line)
        return collected

    def require_chat_noted(self) -> None:
        if self._chat is not None:
            return
        from space.session.chat_context import MISSING_CHAT_DETAIL, apply_chat_context

        if apply_chat_context(self):
            return
        self._record_missing_chat_for_log(MISSING_CHAT_DETAIL)

    def _record_missing_chat_for_log(self, message: str) -> None:
        if self.session_path is None:
            return
        err = self.session_path / "session.err"
        err.parent.mkdir(parents=True, exist_ok=True)
        prior = err.read_text(encoding="utf-8") if err.is_file() else ""
        line_number = len(prior.splitlines()) + 1
        stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        with err.open("a", encoding="utf-8") as handle:
            handle.write(f"{stamp} {message}\n")
        self.note_chat("no-chat", err, str(line_number))

    def log_action(self, action: str, paths: list[Path]) -> None:
        if self.session_path is None:
            return
        self.require_chat_noted()
        self._append_log(self._action_line(action, paths))
        self._injected.clear()
        self._chat = None

    def log_agent_tool(self, mcp_name: str, tool_input: dict | None = None) -> None:
        """Append a ``tool …`` line for an enrolled ``@mcp`` ``@agent_tool`` (or prompt) invocation."""
        name = (mcp_name or "").strip()
        if not name:
            return
        self.log_tool(name, tool_input)

    def log_tool(self, tool_name: str, tool_input: dict | None = None) -> None:
        """Append a timestamped ``tool …`` line for a host or MCP tool invocation."""
        if self.session_path is None:
            return
        name = (tool_name or "").strip()
        if not name:
            return
        paths = self._paths_from_tool_input(tool_input or {})
        from space.session.chat_context import apply_chat_context

        apply_chat_context(self)
        parts = ["tool", name]
        if paths:
            parts.append(", ".join(str(path) for path in paths))
        rules = self._rule_text()
        chat = self._noted_chat()
        if rules:
            parts.append(rules)
        if chat:
            parts.append(chat)
        self._append_log(" ".join(parts))
        self._injected.clear()
        self._chat = None

    def log_note(self, message: str, paths: list[Path] | None = None) -> None:
        """Record a correction or decision in the current loop (use after user steers logging or close behavior)."""
        if self.session_path is None:
            return
        text = (message or "").strip()
        if not text:
            return
        self.require_chat_noted()
        parts = ["note", text]
        if paths:
            parts.append(", ".join(str(path) for path in paths))
        chat = self._noted_chat()
        if chat:
            parts.append(chat)
        self._append_log(" ".join(parts))
        self._chat = None

    @staticmethod
    def _paths_from_tool_input(tool_input: dict) -> list[Path]:
        paths: list[Path] = []
        seen: set[str] = set()
        for key in _TOOL_INPUT_PATH_KEYS:
            value = tool_input.get(key)
            if not value:
                continue
            token = str(value).strip()
            if token and token not in seen:
                seen.add(token)
                paths.append(Path(token))
        raw_paths = tool_input.get("paths")
        if isinstance(raw_paths, list):
            for item in raw_paths:
                token = str(item).strip()
                if token and token not in seen:
                    seen.add(token)
                    paths.append(Path(token))
        return paths

    def note_chat_from_hook(
        self,
        action: str,
        *,
        chat_id: str = "",
        chat_file: Path | str | None = None,
        line_numbers: str = "",
    ) -> None:
        """Record chat metadata so the next log_action line can point at the transcript."""
        if not chat_id and not chat_file:
            return
        path = Path(chat_file) if chat_file else Path(f"chat-{chat_id or 'unknown'}")
        self.note_chat(chat_id or path.stem, path, line_numbers or "1")

    def log_guidance_action(self, action: str, guidance_items: list) -> None:
        """Open listed practices and log this guidance action (after session.new or session.switch)."""
        paths: list[Path] = []
        seen: set[str] = set()
        if self.workpath is not None:
            work = Path(self.workpath).resolve()
            paths.append(work)
            seen.add(str(work))
        for item in guidance_items:
            key = self._practice_key_for_instance(item)
            if key is None:
                continue
            opened = self.practice(key)
            opened.guideline = item
            for group in opened.folder_sets:
                for folder in group:
                    resolved = Path(folder).resolve()
                    token = str(resolved)
                    if token in seen:
                        continue
                    seen.add(token)
                    paths.append(resolved)
        self.log_action(action, paths)

    def note_injected_rules_for_edit(self, guidance: PracticeGuidance, payload: dict) -> None:
        """Note rule slugs from inject_rules hooks for the next log_action line."""
        if self.session_path is None:
            return
        rules = getattr(guidance, "rules", None)
        if rules is None:
            return
        path = rules._payload_path(payload)
        if not path or not rules._just_edited(payload):
            return
        bags = rules._bags_for_path(path)
        if not bags:
            return
        self.note_injected_rules_from_bags(guidance, path, bags)

    def note_injected_rules_from_bags(self, guidance: PracticeGuidance, matched_path: str, bags: list) -> None:
        if self.session_path is None or not matched_path or not bags:
            return
        practice = self._practice_key_for_instance(guidance) or type(guidance).__name__.casefold()
        for bag in bags:
            fidelity = self._fidelity_for_rules_bag(guidance, bag)
            for rule in bag:
                self.note_injected_rule(practice, fidelity, rule.slug, matched_path)

    def log_validation(self, guidance: PracticeGuidance, violations: list[str]) -> None:
        if self.session_path is None:
            return
        self.require_chat_noted()
        practice = type(guidance).__name__
        fidelity = self._fidelity_name(guidance)
        detail = " ".join(violations)
        pointer = self._noted_chat()
        line = f"validate {practice} {fidelity} {detail}".rstrip()
        if pointer:
            line = f"{line} {pointer}"
        self._append_log(line)
        self._injected.clear()
        self._chat = None

    def record_failure(self, failure: BaseException, *, tool: str = "") -> None:
        """Append a full trace to session.err and a pointer line on session.log (does not raise)."""
        if self.session_path is None:
            return
        trace = "".join(traceback.format_exception(type(failure), failure, failure.__traceback__))
        err = self.session_path / "session.err"
        err.parent.mkdir(parents=True, exist_ok=True)
        prior = err.read_text(encoding="utf-8") if err.is_file() else ""
        line_number = len(prior.splitlines()) + 1
        stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        header = f"{stamp} {tool} {type(failure).__name__}: {failure}".strip()
        with err.open("a", encoding="utf-8") as handle:
            handle.write(f"{header}\n")
            handle.write(trace)
            if not trace.endswith("\n"):
                handle.write("\n")
        self.require_chat_noted()
        parts = ["error", str(err), str(line_number)]
        name = (tool or "").strip()
        if name:
            parts.insert(1, name)
        chat = self._noted_chat()
        if chat:
            parts.append(chat)
        self._append_log(" ".join(parts))
        self._chat = None

    def log_error(self, failure: BaseException) -> None:
        self.record_failure(failure)
        raise failure

    def append_chat(self, action: str, chat_file: Path) -> None:
        pointer = self._chat_pointer(chat_file)
        self._append_to_action_line(action, pointer)
        self._append_log(f"{action} chat {pointer}")

    def keep_log(self) -> str:
        log_file = "session.log"
        err_file = "session.err"
        if self.session_path is not None:
            log_file = str(self.session_path / "session.log")
            err_file = str(self.session_path / "session.err")
        return (
            "Session owns logging once session.new or session.switch has run. "
            "CHAT POINTERS — required for continued conversations: you must attach chat id, agent "
            "transcript JSONL path, and line range on every log line when metadata exists. "
            "Hooks: CDD_CONVERSATION_ID, CDD_TRANSCRIPT_PATH, CDD_TRANSCRIPT_LINES. "
            "MCP: pass conversation_id, transcript_path, transcript_lines on the same tool call. "
            "Long threads: use an accurate slice for this turn or a cumulative range (e.g. 1-1152, "
            "then 1-1450) so read_loop can inline the full dialogue for that loop. "
            "Missing chat on an earlier line: append_chat(action, chat_file) or session.append_log "
            "(/append-log); never hand-edit session.log. "
            "MARK-LOOP — link the entire conversation span: call session.mark_loop (/mark-loop) only "
            "with chat fields on that MCP invoke. Dispatch writes tool session.mark_loop with a pointer; "
            "the --- N marker line records the same pointer when bound—both tie the loop to the transcript. "
            "After marking, log actions in that loop with the same thread id and growing line ranges so "
            "read_loop(number) expands every line in the loop with matching transcript slices. "
            "WHERE LINES COME FROM: @agent_tool invocations (AgentOperation.invoke / MCP → "
            "log_session_invocation; guidance kits use GuidanceAgentOperation override). run logs "
            "via log_guidance_action (Validate overrides to log_validation). record_failure on run "
            "and MCP dispatch errors. Cursor hooks do not write session.log. "
            "Failures: record_failure and log_error also re-raises. "
            "Do not duplicate unless a line lacks detail. "
            "session.new seeds --- 1 (chat on that marker when bound at open). "
            "When the user corrects ai behavior or output, session.append_log with note, optional loop, "
            "paths, and chat fields. "
            "SESSION ARTIFACTS: with session_path set, write every large/temporary agent output "
            "(graph JSON, MCP dumps, probes) under session_path—not only under Cursor agent-tools. "
            "List artifact paths on append_log. "
            f"Log file: {log_file}. Errors: {err_file}."
        )

    def _bind_new(self, name: str, workpath: Path, repo_path: Path) -> None:
        self.name = name
        self.workpath = workpath.resolve()
        self.repo_path = repo_path.resolve()
        self.session_path = self.sessions_dir(self.repo_path) / name
        self.session_path.mkdir(parents=True, exist_ok=True)
        self._read_practices_json()
        self._write_session_folder_json()
        self.saved_current_session = name
        self._ensure_initial_loop()

    def _ensure_initial_loop(self) -> None:
        """New sessions start session.log with ``--- 1`` before any actions."""
        if self.session_path is None:
            return
        if self._max_loop_number_from_log() >= 1:
            return
        opened = Loop(1)
        opened._session = self
        self._loops = [opened]
        self._append_log("--- 1")

    @staticmethod
    def sessions_dir(repo_path: Path) -> Path:
        return Path(repo_path).resolve() / _REPO_SESSIONS_DIR

    @classmethod
    def _session_folder(cls, repo_path: Path, name: str) -> Path:
        root = Path(repo_path).resolve()
        preferred = cls.sessions_dir(root) / name
        legacy = root / _LEGACY_REPO_SESSIONS_DIR / name
        if (preferred / "session.json").is_file():
            return preferred
        if (legacy / "session.json").is_file():
            return legacy
        return preferred

    def _write_session_folder_json(self) -> None:
        if self.session_path is None:
            return
        payload = {
            "name": self.name,
            "workpath": str(self.workpath),
            "repo_path": str(self.repo_path),
        }
        self.session_path.mkdir(parents=True, exist_ok=True)
        (self.session_path / "session.json").write_text(json.dumps(payload), encoding="utf-8")

    def _read_session_folder_json(self, session_path: Path) -> dict:
        path = Path(session_path) / "session.json"
        if not path.is_file():
            return {}
        return json.loads(path.read_text(encoding="utf-8"))

    def _read_practices_json(self) -> None:
        if self.repo_path is None:
            self._parent_folders = {}
            return
        path = self.repo_path / ".context" / "practices.json"
        if not path.is_file():
            self._parent_folders = {}
            return
        self._parent_folders = json.loads(path.read_text(encoding="utf-8"))

    def _repo_holding(self, session_path: Path) -> Path:
        folder = Path(session_path).resolve().parent
        if folder.name in {".sessions", "sessions"}:
            return folder.parent
        return folder

    def _env_repo(self) -> Path:
        named = os.environ.get("CDD_REPO")
        if named:
            return Path(named).resolve()
        if self.repo_path is not None:
            return Path(self.repo_path).resolve()
        return Path.cwd().resolve()

    def _env_workpath(self) -> Path:
        named = os.environ.get("CDD_PROJECT")
        if named:
            return Path(named).resolve()
        return Path.cwd().resolve()

    def _opened_named(self, name: str) -> Practice | None:
        for opened in self._opened:
            if opened.name == name:
                return opened
        return None

    @staticmethod
    def _practice_key_for_instance(guidance: PracticeGuidance) -> str | None:
        cls_name = type(guidance).__name__
        for key, ref in _PRACTICE_TYPES.items():
            if ref.rsplit(":", 1)[-1] == cls_name:
                return key
        return None

    @staticmethod
    def _fidelity_for_rules_bag(guidance: PracticeGuidance, bag) -> str:
        parent = getattr(bag, "parent", None)
        if parent is guidance or parent is None:
            current = getattr(getattr(guidance, "fidelities", None), "current", None)
            return str(getattr(current, "name", "") or getattr(current, "fidelity", "") or "")
        return str(getattr(parent, "name", "") or getattr(parent, "fidelity", "") or "")

    def _guidance_for(self, name: str) -> PracticeGuidance:
        ref = _PRACTICE_TYPES.get(name)
        if ref is None:
            raise ValueError(f"Unknown practice {name}")
        module_name, class_name = ref.split(":")
        import importlib

        module = importlib.import_module(module_name)
        return getattr(module, class_name)()

    def _graph_for(self, name: str, folder_sets: list[list[Path]]) -> Graph:
        from harness.graph.graph import Graph

        primary = folder_sets[0][0]
        graph = Graph()
        if self._within_load_budget(primary):
            root = str(self.repo_path or primary)
            graph.load_working_copy(root, {name: str(primary)})
            return graph
        graph._folder = Path(self.repo_path or primary)
        graph._practice_roots = {name: primary}
        practice = graph.practice(name)
        practice.source_root = str(primary)
        return graph

    def _within_load_budget(self, folder: Path) -> bool:
        if not folder.is_dir():
            return True
        count = 0
        for item in folder.rglob("*"):
            if item.suffix.lower() not in _SOURCE_SUFFIXES:
                continue
            count += 1
            if count > _LOAD_FILE_BUDGET:
                return False
        return True

    def _default_folder_sets(self, guidance: PracticeGuidance) -> list[list[str]]:
        """Content roots under the workpath — practice ``default_workspace_folder`` (tests, src, …)."""
        base = self.workpath or self.repo_path or Path.cwd()
        relative = getattr(guidance, "default_workspace_folder", None) or "."
        folder = (Path(base) / relative).resolve()
        return [[str(folder)]]

    def _normalize_sets(self, folder_sets: list[list[Path]]) -> list[list[str]]:
        return [[str(Path(item).resolve()) for item in group] for group in folder_sets]

    def _stored_folders(self) -> dict:
        return dict(self._parent_folders)

    def _write_practices_json(self, stored: dict) -> None:
        if self.repo_path is None:
            return
        path = self.repo_path / ".context" / "practices.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        if not stored:
            if path.is_file():
                path.unlink()
            return
        path.write_text(json.dumps(stored), encoding="utf-8")

    def _action_line(self, action: str, paths: list[Path]) -> str:
        names = ", ".join(str(path) for path in paths)
        guidelines = ", ".join(entry.name for entry in self._opened)
        fidelity = self._active_fidelity()
        layout = self._active_format()
        nodes = self._node_names()
        rules = self._rule_text()
        chat = self._noted_chat()
        return " ".join(
            part
            for part in (
                action,
                names,
                guidelines,
                fidelity,
                layout,
                nodes,
                rules,
                chat,
            )
            if part
        )

    def _fidelity_name(self, guidance: PracticeGuidance) -> str:
        current = getattr(getattr(guidance, "fidelities", None), "current", None)
        if current is None:
            return ""
        return str(getattr(current, "fidelity", "") or getattr(current, "name", ""))

    def _active_fidelity(self) -> str:
        if not self._opened:
            return ""
        parts = [self._fidelity_name(entry.guideline) for entry in self._opened]
        return ", ".join(part for part in parts if part)

    def _active_format(self) -> str:
        if not self._opened:
            return ""
        parts = [str(getattr(entry.guideline, "format", "") or "") for entry in self._opened]
        return ", ".join(part for part in parts if part)

    def _node_names(self) -> str:
        names: list[str] = []
        for entry in self._opened:
            practice = entry.graph.practices.get(entry.name)
            if practice is None:
                continue
            names.append(practice.root_node.name)
        return " ".join(names)

    def _rule_text(self) -> str:
        if not self._injected:
            return ""
        ordered = sorted(self._injected, key=lambda item: (item[0], item[1], item[2], item[3]))
        return " ".join(
            " ".join(part for part in (practice, fidelity, rule, path) if part)
            for practice, fidelity, rule, path in ordered
        )

    def _noted_chat(self) -> str:
        if self._chat is None:
            return ""
        chat_id, chat_file, line_numbers = self._chat
        return f"{chat_id} {chat_file} {line_numbers}".strip()

    def _chat_pointer(self, chat_file: Path) -> str:
        if self._chat is None:
            return str(chat_file)
        chat_id, _path, line_numbers = self._chat
        return f"{chat_id} {chat_file} {line_numbers}".strip()

    def _append_to_action_line(self, action: str, pointer: str) -> None:
        if self.session_path is None:
            return
        log = self.session_path / "session.log"
        if not log.is_file():
            return
        lines = log.read_text(encoding="utf-8").splitlines()
        for index, line in enumerate(lines):
            if f" {action} " in f" {line} " or line.endswith(f" {action}"):
                lines[index] = f"{line} {pointer}"
        log.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")

    def _append_log(self, line: str) -> None:
        if self.session_path is None:
            return
        stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        written = f"{stamp} {line}"
        log = self.session_path / "session.log"
        with log.open("a", encoding="utf-8") as handle:
            handle.write(written + "\n")
        if self._loops and not line.startswith("--- "):
            self._loops[-1].entries.append(written)
