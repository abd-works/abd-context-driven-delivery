"""Session — work paths, logging, and practice graphs for the active process session."""

from __future__ import annotations

import json
import os
import re
import shutil
import traceback
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import TYPE_CHECKING

from harness.agent_tools import agent_instructions, agent_tool, agent_toolset
from harness.installation.destination import language_adapter
from harness.installation.files import command
from harness.mcp.mcp_server import mcp
from space.work_state import (
    SESSIONS_FOLDER,
    WorkState,
    checkout_holding,
    main_checkout_of,
    project_checkout,
    project_folder,
)

if TYPE_CHECKING:
    from harness.graph.graph import Graph
    from harness.guidance.guidance import FidelityGuidance, PracticeGuidance
    from space.repo.repo import Repo
    from tools.file_manager.file_manager import FileManager


_SOURCE_SUFFIXES = {".py", ".ts", ".tsx", ".js", ".jsx"}
_LOAD_FILE_BUDGET = 40
_OUTPUT_PATTERN_MARKS = {"*", "{"}
CONTEXT_FOLDER = ".context"
_MAIN_SESSION_NAME = "main"
_LEGACY_REPO_SESSIONS_DIR = "sessions"
_COMPLETE_FOLDER = "_complete"
_ARCHIVE_FOLDER = "_archive"
_BACKLOG_FOLDER = "_backlog"
_BOARD_FILE = "_board.json"
# A log line from a chat the server cannot name ends with "no-chat" in place of the chat's id, transcript, and lines.
NO_CHAT: tuple[str, Path, str] = ("no-chat", Path(), "")
_TIMESTAMP_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
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


def name_of(text: str) -> str:
    """The name a session, its folder, and its branch get: `Pet visits` is `pet-visits`, since git refuses a space in a branch name."""
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


class PracticeRootInContextError(ValueError):
    """A practice root was chosen inside a ``.context`` folder, which would put the practice's code among its documents
    and its documents in a ``.context`` within a ``.context``. It names the practice and the folder it refused."""

    def __init__(self, practice: str, root: Path) -> None:
        self.practice = practice
        self.root = root
        super().__init__(
            f"{root} is inside a .context folder: choose the folder for {practice}'s code, "
            "and its documents and diagrams go in that folder's .context"
        )
        self.practice = practice
        self.root = root


class SessionNameRequiredError(ValueError):
    """Raised when switch-session has no name and ``.sessions/session.json`` has no session or branch."""

    def __init__(self) -> None:
        super().__init__(
            "session name is required: pass name, or switch to a branch first so "
            "the session can take its name"
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


class PracticeSessionOutput:
    """What one practice has in one session: its guideline, the paths it reads, its graph, and whether it is on."""

    # The guideline, folders, and graph load on first use: the board asks every ticket's session
    # which practices are enabled after every cdd call, and that question needs none of them.

    def __init__(self, name: str, session: Session) -> None:
        self.name = name
        self._session = session
        self._guideline: PracticeGuidance | None = None
        self._output_paths: list | None = None
        self._graph: Graph | None = None

    @property
    def guideline(self) -> PracticeGuidance:
        if self._guideline is None:
            self._guideline = self._session._guidance_for(self.name)
        return self._guideline

    @guideline.setter
    def guideline(self, guidance: PracticeGuidance) -> None:
        self._guideline = guidance

    @property
    def _folders(self) -> list:
        """The folders this practice reads in the session, saved or its defaults. Callers ask for its graph or its
        result instead, so how the folders are kept stays this class's own."""
        if self._output_paths is None:
            stored = self._session._stored_folders().get(self.name)
            self._output_paths = stored or self._session._default_output_paths(self.guideline, self.name)
        return self._output_paths

    @property
    def graph(self) -> Graph:
        if self._graph is None:
            folders = [[Path(item) for item in group] for group in self._folders]
            self._graph = self._session._graph_for(self.name, folders)
        return self._graph

    @property
    def enabled(self) -> bool:
        """Whether the session works on this practice: true until a person turns it off."""
        return self._session._fields.get("practices", {}).get(self.name, {}).get("enabled", True)

    @enabled.setter
    def enabled(self, is_enabled: bool) -> None:
        saved = self._session._fields.get("practices", {})
        self._session._save_fields(practices={**saved, self.name: {"enabled": is_enabled}})

    def to_mcp_result(self) -> dict:
        """JSON-safe snapshot for MCP tool results."""
        return {
            "name": self.name,
            "output_paths": [[str(Path(item)) for item in group] for group in self._folders],
        }


_PRACTICE_TYPES = {
    "stories": "cdd_guidance.practices.stories.stories:Stories",
    "clean_engineering": "cdd_guidance.practices.clean_engineering.clean_engineering:CleanEngineering",
    "ddd": "cdd_guidance.practices.ddd.ddd:Ddd",
    "bdd": "cdd_guidance.practices.bdd.bdd:Bdd",
    "ux": "cdd_guidance.practices.ux.ux:Ux",
}


@language_adapter(language="typescript")
@agent_toolset
class Session:
    """Work session — one in-memory current for each project; new and switch open named sessions."""

    main_session = _MAIN_SESSION_NAME
    default_wip = 3

    # One cdd server works on every chat's project, so each project keeps its own current session.
    _current_by_project: dict[Path, Session] = {}

    def __init__(self, repo_root: Path | str | None = None) -> None:
        self._session_name = ""
        self.workpath: Path | None = None
        self.repo_path: Path | None = Path(repo_root).resolve() if repo_root else None
        self.session_path: Path | None = None
        self._loops: list[Loop] = []
        self._parent_folders: dict = {}
        self._known: dict[str, PracticeSessionOutput] = {}
        self._opened: list[PracticeSessionOutput] = []
        self._injected: list[tuple[str, str, str, str]] = []
        self._chat: tuple[str, Path, str] | None = None
        self._file_manager: FileManager | None = None

    @property
    def name(self) -> str:
        """Named work session (not the toolset slug)."""
        return self._session_name

    @name.setter
    def name(self, value: str) -> None:
        self._session_name = (value or "").strip()

    @property
    def file_manager(self) -> FileManager:
        """The session's file manager, held in memory, reading under the session's roots: the folder each practice works
        in, as ``session.json`` records it or by the practice's default. A new one when those roots change."""
        from tools.file_manager.file_manager import FileManager

        workpath = Path(self.workpath or self.repo_from_session()).resolve()
        roots = tuple(sorted({self.practice_root(self._guidance_for(name), name).resolve() for name in _PRACTICE_TYPES}))
        if self._file_manager is None or self._file_manager.roots != roots:
            self._file_manager = FileManager(workpath, roots)
        return self._file_manager

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
            roots[name] = stored.get(name) or self._default_output_paths(
                self._guidance_for(name), name
            )
        return roots

    @classmethod
    def _slot(cls, repo_path: Path | str | None = None) -> Session:
        """The in-memory current session of ``repo_path``'s checkout, else of the project being worked on."""
        repo = checkout_holding(repo_path) if repo_path is not None else project_checkout()
        return cls._current_by_project.setdefault(repo, cls())

    @classmethod
    def forget_current(cls, repo_path: Path | str | None = None) -> None:
        """Drop the in-memory current session of ``repo_path``'s checkout, or of every project when none is named, so
        the next call reads ``.sessions/`` again. Naming the project leaves other chats' sessions as they are."""
        if repo_path is None:
            cls._current_by_project.clear()
            return
        cls._current_by_project.pop(checkout_holding(repo_path), None)

    @classmethod
    def refresh_current_from_repo(cls, repo_path: Path | str | None = None) -> None:
        """Reload in-memory session when repo ``.sessions/session.json`` current changed."""
        repo = checkout_holding(repo_path) if repo_path is not None else project_checkout()
        slot = cls._slot(repo)
        saved = cls.active_name(repo)
        if slot.name == saved and slot.session_path is not None and slot.repo_path == repo:
            return
        cls._current_by_project.pop(repo, None)
        session = cls._slot(repo)
        session.repo_path = repo
        session.resolve(saved, repo if saved == _MAIN_SESSION_NAME else None, repo)

    @classmethod
    def active_name(cls, repo_path: Path) -> str:
        """The session saved as open on ``repo_path``; main, which works on the whole repository, when none is named."""
        return WorkState(repo_path).session or _MAIN_SESSION_NAME

    @classmethod
    def current_folder(cls, repo_path: Path | str | None = None) -> Path:
        """``.sessions/{current}/`` on the project's checkout; ``.sessions/main/`` when none is named.

        Reads the project (``repo_path``, else the project being worked on), not a session held in memory."""
        repo = checkout_holding(repo_path) if repo_path is not None else project_checkout()
        return cls._session_folder(repo, cls.active_name(repo))

    @classmethod
    @mcp
    @command(name="current-session")
    @agent_tool
    def current(cls, repo_path: Path | str | None = None) -> Session:
        """The session saved on the repo; the main session, which works on the whole repository, when none is named."""
        cls.refresh_current_from_repo(repo_path)
        return cls._slot(repo_path)

    def repo_from_session(self, repo_path: Path | str | None = None) -> Path:
        """Repo that holds ``.sessions`` — the path already in hand, or the repo it sits in."""
        if repo_path is not None:
            return checkout_holding(repo_path)
        if self.repo_path is not None:
            return Path(self.repo_path).resolve()
        return project_checkout()

    @mcp
    @command(name="close-session")
    @agent_tool
    def close(self) -> None:
        """Close this work session and remove ``session`` from ``.sessions/session.json``."""
        self.repo_path = self.repo_from_session()
        if self.name and self.name != self.saved_current_session:
            return
        self.saved_current_session = _MAIN_SESSION_NAME
        opened = type(self)._current_by_project.get(self.repo_path)
        if opened is not None and opened is not self:
            opened._forget()
        if opened is self or not self.name:
            self._forget()

    def _forget(self) -> None:
        self.name = ""
        self.workpath = None
        self.session_path = None
        self.reset()

    @classmethod
    def new(
        cls,
        name: str,
        workpath: Path,
        repo_path: Path,
        is_current: bool = True,
        *,
        title: str = "",
        scope: str = "",
        parent: str = "",
    ) -> str:
        """Open a new session folder, with the title, scope, and parent a board ticket shows saved in its
        ``session.json``. Returns keep_log.

        ``is_current`` False leaves the current session as it is, because a session a person opens for
        later, such as a board ticket, is not the one being worked on."""
        session = cls._slot(repo_path) if is_current else cls(repo_path)
        described = {key: value for key, value in (("title", title), ("scope", scope), ("parent", parent)) if value}
        session._bind_new(name, Path(workpath), Path(repo_path), described, is_current)
        return session.keep_log()

    @classmethod
    def load(cls, session_path: Path, repo_path: Path) -> Session:
        """The session kept in ``session_path``, read without becoming the current session."""
        session = cls(repo_path)
        session.session_path = Path(session_path)
        session.name = session.session_path.name
        stored = session._fields.get("workpath", "")
        session.workpath = Path(stored) if stored else session.repo_path
        return session

    @classmethod
    def all_in(cls, repo_path: Path | str) -> list[Session]:
        """The repo's work sessions, open ones first then closed: not main, and not the folders the sessions share."""
        return [cls.load(folder, Path(repo_path)) for folder in cls._work_folders(Path(repo_path))]

    @classmethod
    def backlog_folder(cls, repo_path: Path | str) -> Path:
        """Where sessions wait before work starts, and where a session moved back is held."""
        return cls.sessions_dir(Path(repo_path)) / _BACKLOG_FOLDER

    @classmethod
    def board_file(cls, repo_path: Path | str) -> Path:
        """The file that holds what the repo's sessions share on the board."""
        return cls.sessions_dir(Path(repo_path)) / _BOARD_FILE

    @staticmethod
    def timestamp(moment: datetime) -> str:
        """A moment as session logs write it."""
        return moment.astimezone(timezone.utc).strftime(_TIMESTAMP_FORMAT)

    @classmethod
    def _work_folders(cls, repo_path: Path) -> list[Path]:
        sessions = cls.sessions_dir(repo_path)
        if not sessions.is_dir():
            return []
        skipped = {_COMPLETE_FOLDER, _MAIN_SESSION_NAME}
        open_folders = [
            folder for folder in sorted(sessions.iterdir())
            if folder.is_dir() and folder.name not in skipped and not folder.name.startswith("_")
        ]
        closed = sessions / _COMPLETE_FOLDER
        closed_folders = sorted(folder for folder in closed.iterdir() if folder.is_dir()) if closed.is_dir() else []
        return open_folders + closed_folders

    @property
    def is_closed(self) -> bool:
        return self.session_path is not None and self.session_path.parent.name == _COMPLETE_FOLDER

    @property
    def session_file(self) -> Path:
        """The ``session.json`` in this session's folder, which holds its title, workpath, practice roots, and practices."""
        return self.session_path / "session.json"

    @property
    def title(self) -> str:
        """The title a person gave the session's ticket; empty when it has none."""
        return self._fields.get("title", "")

    @property
    def scope(self) -> str:
        """feature, story, or slice; empty when no one said."""
        return self._fields.get("scope", "")

    @property
    def parent(self) -> str:
        """The name of the session this one was split from; empty when it was not split from one."""
        return self._fields.get("parent", "")

    @property
    def _fields(self) -> dict:
        """What ``session.json`` in this session's folder holds, read each time. Callers ask for a named value, so
        the file's layout stays the session's own."""
        return self._read_session_folder_json(self.session_path) if self.session_path else {}

    def _save_fields(self, **values: object) -> None:
        """Merge ``values`` into ``session.json``, keeping what others store there."""
        merged = {**self._fields, **values}
        self.session_file.write_text(json.dumps(merged), encoding="utf-8")

    def enable_practice(self, practice: str, is_enabled: bool) -> None:
        """Turn ``practice`` on or off for this session, saved in its ``session.json``."""
        self.practices[practice].enabled = is_enabled

    def keep_file(self, file: Path) -> Path:
        """Move ``file`` into this session's folder, where it stays with the session's work until it becomes lasting
        context, such as part of a story map. A started backlog item's text is the only copy of the idea."""
        kept = self.session_path / file.name
        file.replace(kept)
        return kept

    def choose_workpath(self, workpath: Path) -> None:
        """Work in ``workpath`` from now on: the folder this session's practices write under and its graph loads from.
        A practice root a person chose is kept relative to the workpath, so each is saved again against the new one and
        still names the same folder."""
        base = Path(self.workpath or self.repo_path).resolve()
        chosen = {practice: (base / output["root"]).resolve() for practice, output in self._output_overrides().items() if output.get("root")}
        self.workpath = Path(workpath).resolve()
        self._write_session_folder_json()
        for practice, root in chosen.items():
            self.choose_practice_root(practice, root)

    def choose_practice_root(self, practice: str, root: Path) -> Path:
        """Write ``practice``'s files under ``root``, kept in ``session.json`` relative to the workpath like any output
        override, and return the practice root now in use."""
        # A practice root holds the practice's code; its documents and diagrams go in the root's own .context.
        if CONTEXT_FOLDER in Path(root).parts:
            raise PracticeRootInContextError(practice, Path(root))
        outputs = dict(self._fields.get("outputs", {}))
        relative = os.path.relpath(Path(root).resolve(), Path(self.workpath or self.repo_path).resolve())
        outputs[practice] = {**outputs.get(practice, {}), "root": Path(relative).as_posix()}
        self._save_fields(outputs=outputs)
        return Path(root).resolve()

    def use_default_practice_root(self, practice: str) -> None:
        """Write ``practice``'s files under its default practice root again."""
        outputs = dict(self._fields.get("outputs", {}))
        kept = {key: value for key, value in outputs.get(practice, {}).items() if key != "root"}
        self._save_fields(outputs={**outputs, practice: kept})

    def has_chosen_practice_root(self, practice: str) -> bool:
        return bool(self._output_overrides().get(practice, {}).get("root"))

    def practice_root(self, guidance: PracticeGuidance, practice: str = "") -> Path:
        """The folder ``practice`` writes under: the root a person chose, or the workpath plus the practice's default
        folder from ``.context/config.json`` or the practice itself. With no practice key, the guidance's own."""
        practice = practice or self._practice_key_for_instance(guidance) or ""
        chosen = self._output_overrides().get(practice, {}).get("root")
        if chosen:
            return (Path(self.workpath or self.repo_path).resolve() / chosen).resolve()
        return Path(self._default_output_paths(guidance, practice)[0][0])

    def move_folder_to(self, parent: Path) -> Session:
        """Move this session's folder under ``parent``, such as ``.sessions/_complete/``."""
        parent.mkdir(parents=True, exist_ok=True)
        destination = parent / self.name
        shutil.move(str(self.session_path), str(destination))
        return type(self).load(destination, self.repo_path)

    def move_to_closed(self) -> Session:
        return self.move_folder_to(self.sessions_dir(self.repo_path) / _COMPLETE_FOLDER)

    def move_to_archive(self) -> Session:
        return self.move_folder_to(self.sessions_dir(self.repo_path) / _ARCHIVE_FOLDER)

    def move_to_backlog(self) -> Session:
        return self.move_folder_to(self.backlog_folder(self.repo_path))

    def reopen(self) -> Session:
        """Back among the open sessions, from closed or the backlog."""
        return self.move_folder_to(self.sessions_dir(self.repo_path))

    @classmethod
    @mcp
    @command(name="switch-session")
    @agent_tool
    def switch(
        cls,
        name: str = "",
        workpath: Path | None = None,
        repo_path: Path | None = None,
        session_path: Path | None = None,
    ) -> str:
        """Switch to session ``name``, creating its folder when missing. Returns keep_log.

        ``name`` defaults to ``session`` in ``.sessions/session.json``, then to the saved ``branch``.
        Saves ``name`` as ``session`` there. Does not touch branches or worktrees."""
        if repo_path is not None:
            repo = checkout_holding(repo_path)
        elif workpath is not None:
            repo = checkout_holding(workpath)
        else:
            repo = project_checkout()
        slot = cls._slot(repo)
        wanted = cls._session_name(name, repo)
        folder = Path(session_path) if session_path is not None else cls._session_folder(repo, wanted)
        if not (folder / "session.json").is_file():
            work = Path(workpath) if workpath is not None else slot._env_workpath()
            return cls.new(wanted, work, repo)
        slot.resolve(wanted, workpath, repo_path, session_path)
        return slot.keep_log()

    @classmethod
    def _session_name(cls, name: str, repo: Path) -> str:
        state = WorkState(repo)
        cleaned = name_of(name or state.session or state.branch)
        if not cleaned:
            raise SessionNameRequiredError()
        return cleaned

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
        """``session`` in repo/.sessions/session.json."""
        if self.repo_path is None:
            return _MAIN_SESSION_NAME
        return type(self).active_name(self.repo_path)

    @saved_current_session.setter
    def saved_current_session(self, name: str) -> None:
        if self.repo_path is None:
            return
        cleaned = (name or "").strip()
        if cleaned == _MAIN_SESSION_NAME:
            cleaned = ""
        WorkState(self.repo_path).session = cleaned
        if cleaned:
            from harness.hooks.session_logs import SessionLogs

            SessionLogs(self.repo_path).write_active_session(cleaned)

    def practice(self, name: str) -> PracticeSessionOutput:
        found = self._opened_named(name)
        if found is not None:
            return found
        if name not in _PRACTICE_TYPES:
            raise ValueError(f"Unknown practice {name}")
        opened = self.practices[name]
        self._opened.append(opened)
        return opened

    @property
    def practices(self) -> dict[str, PracticeSessionOutput]:
        """Every practice CDD has, by practice key, opened or not."""
        for name in _PRACTICE_TYPES:
            self._known.setdefault(name, PracticeSessionOutput(name, self))
        return dict(self._known)

    @property
    def active_practices(self) -> list[PracticeSessionOutput]:
        return [practice for practice in self.practices.values() if practice.enabled]

    @property
    def opened_practices(self) -> list[PracticeSessionOutput]:
        """The practices this session has asked for, which its log lines name."""
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

    def remember_parent_folders(self, practice: str, output_paths: list[list[Path]]) -> None:
        stored = self._stored_folders()
        normalized = self._normalize_output_paths(output_paths)
        if normalized == self._default_output_paths(self._guidance_for(practice), practice):
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
        self._known = {}
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
            self.repo_path = checkout_holding(self.workpath)
            self.session_path = self._session_folder(self.repo_path, name)
        else:
            self.repo_path = project_checkout()
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
        from space.session.chat_context import apply_chat_context

        if apply_chat_context(self):
            return
        self._chat = NO_CHAT

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
        """Open listed practices and log this guidance action (after session.switch)."""
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
            for group in opened._folders:
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
        stamp = self.timestamp(datetime.now(timezone.utc))
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
            "Session owns logging once session.switch has run. "
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
            "log_action(action, paths) records an action with the paths it touched; "
            "log_agent_tool(mcp_name, tool_input) records an @agent_tool call. "
            "Failures: record_failure and log_error also re-raises. "
            "Do not duplicate unless a line lacks detail. "
            "session.switch seeds --- 1 in a new session (chat on that marker when bound at open). "
            "When the user corrects ai behavior or output, session.append_log with note, optional loop, "
            "paths, and chat fields. "
            "SESSION ARTIFACTS: with session_path set, write every large/temporary agent output "
            "(graph JSON, MCP dumps, probes) under session_path—not only under Cursor agent-tools. "
            "List artifact paths on append_log. "
            "PERMANENT ARTIFACTS: fidelity outputs belong to the folder the session was opened on, its "
            "workpath, and sit at the repository root only when the session names no folder. Markdown and "
            "drawio go in that folder's .context/; code goes straight in that folder. "
            f"Log file: {log_file}. Errors: {err_file}."
        )

    def _bind_new(self, name: str, workpath: Path, repo_path: Path, fields: dict[str, str], is_current: bool) -> None:
        name = name_of(name)
        self.name = name
        self.workpath = workpath.resolve()
        self.repo_path = repo_path.resolve()
        self.session_path = self.sessions_dir(self.repo_path) / name
        self.session_path.mkdir(parents=True, exist_ok=True)
        self._read_practices_json()
        self._write_session_folder_json()
        self._save_fields(**fields)
        if is_current:
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
        return WorkState(repo_path).sessions_folder

    @classmethod
    def _session_folder(cls, repo_path: Path, name: str) -> Path:
        """A ticket on the board lives in the main checkout's ``.sessions``, so a chat in the ticket's linked worktree
        logs there too and the board shows its work. Each checkout keeps its own main session."""
        root = Path(repo_path).resolve()
        preferred = cls.sessions_dir(root) / name
        legacy = root / _LEGACY_REPO_SESSIONS_DIR / name
        candidates = [preferred, legacy]
        if name != _MAIN_SESSION_NAME:
            candidates.insert(0, cls.sessions_dir(main_checkout_of(root)) / name)
        for folder in candidates:
            if (folder / "session.json").is_file():
                return folder
        return preferred

    def _write_session_folder_json(self) -> None:
        if self.session_path is None:
            return
        # Keep fields others store here, such as a board ticket's title, scope, and parent.
        payload = {
            **self._read_session_folder_json(self.session_path),
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
        if folder.name in {SESSIONS_FOLDER, _LEGACY_REPO_SESSIONS_DIR}:
            return folder.parent
        return folder

    def _env_workpath(self) -> Path:
        return project_folder()

    def _opened_named(self, name: str) -> PracticeSessionOutput | None:
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

    def _graph_for(self, name: str, output_paths: list[list[Path]]) -> Graph:
        from harness.graph.graph import Graph

        primary = output_paths[0][0]
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

    def _default_output_paths(
        self, guidance: PracticeGuidance, practice: str | None = None
    ) -> list[list[str]]:
        """Content roots under the workpath.

        Project ``.context/config.json`` ``practice_folders`` overrides the practice's
        ``default_workspace_folder`` (tests, src, …) with a workpath-relative path.
        """
        base = self.workpath or self.repo_path or project_folder()
        key = (practice or self._practice_key_for_instance(guidance) or "").strip()
        relative = self._project_default_folder(key)
        if relative is None:
            relative = getattr(guidance, "default_workspace_folder", None) or "."
        folder = (Path(base) / relative).resolve()
        return [[str(folder)]]

    def fidelity_outputs(self, guidance: PracticeGuidance, fidelity: FidelityGuidance | None = None) -> dict[str, list[str]]:
        """Where fidelity writes each format, the practice's active fidelity when none is named: its declared paths
        under the session's workpath. Naming the fidelity leaves the practice as it is, since practices are shared.

        The workpath is the folder the session was opened on, and the repository when it names none.
        The session's ``outputs`` field overrides by practice: ``root`` for the practice, and under a
        fidelity's name its own ``root`` and a file name per format for a single-file output. An override
        root is a folder under the workpath: the first of the fidelity's override, the practice's override,
        and ``practice_folders`` in ``.context/config.json``.
        """
        current = fidelity or getattr(getattr(guidance, "fidelities", None), "current", None)
        if current is None:
            return {}
        key = self._practice_key_for_instance(guidance) or ""
        practice = self._output_overrides().get(key, {})
        overrides = practice.get(str(getattr(current, "fidelity", "") or getattr(current, "name", "")), {})
        chosen_root = overrides.get("root") or practice.get("root") or self._project_default_folder(key)
        root = (Path(self.workpath or self.repo_path or project_folder()) / (chosen_root or ".")).resolve()
        return {
            label: [self._output_path(root, name) for name in self._output_names(declared, overrides.get(label))]
            for label, declared in current.outputs.items()
        }

    def _output_overrides(self) -> dict:
        if self.session_path is None:
            return {}
        return self._read_session_folder_json(self.session_path).get("outputs", {})

    def _output_names(self, declared: str | list[str], override: str | None) -> list[str]:
        names = [declared] if isinstance(declared, str) else list(declared)
        is_single_file = len(names) == 1 and not set(names[0]) & _OUTPUT_PATTERN_MARKS
        return [PurePosixPath(names[0]).with_name(override).as_posix()] if override and is_single_file else names

    def _output_path(self, root: Path, name: str) -> str:
        folder_mark = "/" if name.endswith("/") else ""
        return f"{(root / name).as_posix()}{folder_mark}"

    def _project_default_folder(self, practice: str) -> str | None:
        """Workpath-relative folder from ``.context/config.json`` practice_folders."""
        if not practice:
            return None
        from space.context_config import ContextConfig

        root = self.repo_path or self.workpath
        if root is None:
            return None
        return ContextConfig(root).practice_folder(practice)

    def _normalize_output_paths(self, output_paths: list[list[Path]]) -> list[list[str]]:
        return [[str(Path(item).resolve()) for item in group] for group in output_paths]

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

    def last_generated_format(self, guidance: PracticeGuidance) -> str:
        """The format the latest generate of guidance's fidelity wrote, read from its line in session.log, which lists the
        practices, then their fidelities, then their formats; empty when no generate line names that fidelity."""
        practice = self._practice_key_for_instance(guidance)
        fidelity = self._fidelity_name(guidance)
        log = self.session_path / "session.log" if self.session_path else None
        if not practice or not fidelity or log is None or not log.is_file():
            return ""
        for line in reversed(log.read_text(encoding="utf-8").splitlines()):
            words = line.replace(", ", ",").split(" ")
            if len(words) > 1 and words[1] == "generate":
                written = self._written_format(words[2:], practice, fidelity)
                if written:
                    return written
        return ""

    @staticmethod
    def _written_format(words: list[str], practice: str, fidelity: str) -> str:
        for practices, fidelities, formats in zip(words, words[1:], words[2:]):
            named = list(zip(practices.split(","), fidelities.split(","), formats.split(",")))
            if (practice, fidelity) in [(name, opened) for name, opened, _ in named]:
                return next(written for name, opened, written in named if (name, opened) == (practice, fidelity))
        return ""

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
        if self._chat is NO_CHAT:
            return NO_CHAT[0]
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
        stamp = self.timestamp(datetime.now(timezone.utc))
        written = f"{stamp} {line}"
        log = self.session_path / "session.log"
        with log.open("a", encoding="utf-8") as handle:
            handle.write(written + "\n")
        if self._loops and not line.startswith("--- "):
            self._loops[-1].entries.append(written)
