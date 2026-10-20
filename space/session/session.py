"""Session — work paths, logging, and practice graphs for the active process session."""

from __future__ import annotations

import json
import os
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


class Loop:
    """One span of context, generation, and evaluation inside a session."""

    def __init__(self, number: int) -> None:
        self.number = number
        self.entries: list[str] = []

    def inject(self, chat_file: Path) -> None:
        path = Path(chat_file)
        self.entries.append(str(path))
        if not path.is_file():
            return
        response = path.read_text(encoding="utf-8").strip()
        if response:
            self.entries.append(response.splitlines()[0])


class Practice:
    """One practice guideline and the graph of that same practice."""

    def __init__(self, name: str, guideline: PracticeGuidance, graph: Graph, folder_sets: list) -> None:
        self.name = name
        self.guideline = guideline
        self.graph = graph
        self.folder_sets = folder_sets


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
        self._injected: list[tuple[str, str, str]] = []
        self._chat: tuple[str, Path, str] | None = None

    @property
    def name(self) -> str:
        """Named work session (not the toolset slug)."""
        return self._session_name

    @name.setter
    def name(self, value: str) -> None:
        self._session_name = (value or "").strip()

    @classmethod
    def _slot(cls) -> Session:
        if cls._current is None:
            cls._current = cls()
        return cls._current

    @classmethod
    @mcp
    @command
    @agent_tool
    def current(cls, repo_path: Path | str | None = None) -> Session | None:
        """Named session already in memory, or the one saved on the repo."""
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
        if repo_path is not None:
            return Path(repo_path).resolve()
        if self.repo_path is not None:
            return self.repo_path
        named = os.environ.get("CDD_REPO")
        if named:
            return Path(named).resolve()
        return None

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
    @command
    @agent_instructions
    def new(cls, name: str, workpath: Path, repo_path: Path) -> str:
        """Open a session. Returns keep_log."""
        session = cls._slot()
        session._bind_new(name, Path(workpath), Path(repo_path))
        return session.keep_log()

    @classmethod
    @mcp
    @command
    @agent_instructions
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
    def open_or_switch(cls, name: str, workpath: Path, repo_path: Path) -> str:
        """Select a session folder when it exists, otherwise create it."""
        cleaned = (name or "").strip()
        if not cleaned:
            raise ValueError("session name is required")
        primary = Path(repo_path).resolve()
        work = Path(workpath).resolve()
        session_json = primary / "sessions" / cleaned / "session.json"
        if session_json.is_file():
            return cls.switch(cleaned, workpath=work, repo_path=primary)
        return cls.new(cleaned, work, primary)

    @property
    def saved_current_session(self) -> str:
        """``current`` in repo/sessions/session.json."""
        if self.repo_path is None:
            return _DEFAULT_SESSION_NAME
        path = self.repo_path / "sessions" / "session.json"
        if not path.is_file():
            return _DEFAULT_SESSION_NAME
        state = json.loads(path.read_text(encoding="utf-8"))
        cleaned = str(state.get("current") or _DEFAULT_SESSION_NAME).strip()
        return cleaned or _DEFAULT_SESSION_NAME

    @saved_current_session.setter
    def saved_current_session(self, name: str) -> None:
        if self.repo_path is None:
            return
        path = self.repo_path / "sessions" / "session.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        state = json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}
        state["current"] = (name or "").strip() or _DEFAULT_SESSION_NAME
        path.write_text(json.dumps(state), encoding="utf-8")

    def practice(self, name: str) -> Practice:
        found = self._opened_named(name)
        if found is not None:
            return found
        guidance = self._guidance_for(name)
        sets = self._stored_folders().get(name) or self._default_folder_sets(guidance)
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
        if normalized == self._default_folder_sets(self._guidance_for(practice)):
            stored.pop(practice, None)
        else:
            stored[practice] = normalized
        self._write_practices_json(stored)
        self._parent_folders = stored

    def note_injected_rule(self, practice: str, fidelity: str, rule: str) -> None:
        self._injected.append((practice, fidelity, rule))

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
            self.workpath = Path(stored["workpath"]) if stored.get("workpath") else workpath
            self.repo_path = self._git_root(self.session_path)
        elif repo_path is not None:
            self.repo_path = Path(repo_path).resolve()
            self.session_path = self.repo_path / "sessions" / name
            stored = self._read_session_folder_json(self.session_path)
            self.workpath = Path(stored["workpath"]) if stored.get("workpath") else workpath
        elif workpath is not None:
            self.workpath = Path(workpath).resolve()
            self.repo_path = self._git_root(self.workpath)
            self.session_path = self.repo_path / "sessions" / name
        else:
            self.repo_path = self._env_repo()
            self.session_path = self.repo_path / "sessions" / name
            stored = self._read_session_folder_json(self.session_path)
            if stored.get("workpath"):
                self.workpath = Path(stored["workpath"])
            else:
                self.workpath = self._env_workpath()
        self._read_practices_json()
        self.saved_current_session = name
        self._write_session_folder_json()
        return self

    def loop(self) -> Loop:
        number = self._loops[-1].number + 1 if self._loops else 1
        opened = Loop(number)
        self._loops.append(opened)
        self._append_log(f"--- {number}")
        return opened

    def log_action(self, action: str, paths: list[Path]) -> None:
        self._append_log(self._action_line(action, paths))

    def log_validation(self, guidance: PracticeGuidance, violations: list[str]) -> None:
        practice = type(guidance).__name__
        fidelity = self._fidelity_name(guidance)
        detail = " ".join(violations)
        self._append_log(f"validate {practice} {fidelity} {detail}".rstrip())

    def log_error(self, failure: BaseException) -> None:
        trace = "".join(traceback.format_exception(type(failure), failure, failure.__traceback__))
        if self.session_path is not None:
            err = self.session_path / "session.err"
            err.write_text(trace, encoding="utf-8")
            self._append_log(f"error {err}")
        raise failure

    def append_chat(self, action: str, chat_file: Path) -> None:
        pointer = self._chat_pointer(chat_file)
        self._append_to_action_line(action, pointer)
        self._append_log(f"{action} chat {pointer}")

    def keep_log(self) -> str:
        return (
            "log_action, log_validation, and log_error already run. "
            "Reuse those operations, and append_chat, when a log line misses the chat or a detail."
        )

    def _bind_new(self, name: str, workpath: Path, repo_path: Path) -> None:
        self.name = name
        self.workpath = workpath.resolve()
        self.repo_path = repo_path.resolve()
        self.session_path = self.repo_path / "sessions" / name
        self.session_path.mkdir(parents=True, exist_ok=True)
        self._read_practices_json()
        self._write_session_folder_json()
        self.saved_current_session = name

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

    def _git_root(self, start: Path) -> Path:
        from space.repo.repo import Repo

        found = Repo(start).find_root()
        return found if found is not None else Path(start).resolve()

    def _env_repo(self) -> Path:
        named = os.environ.get("CDD_REPO")
        if named:
            return Path(named).resolve()
        return self._git_root(Path.cwd())

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
        import inspect

        folder = Path(inspect.getfile(type(guidance))).resolve().parent
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
        return self._fidelity_name(self._opened[0].guideline)

    def _active_format(self) -> str:
        if not self._opened:
            return ""
        return str(getattr(self._opened[0].guideline, "format", "") or "")

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
        ordered = sorted(self._injected, key=lambda item: (item[0], item[1], item[2]))
        return " ".join(f"{practice} {fidelity} {rule}" for practice, fidelity, rule in ordered)

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
