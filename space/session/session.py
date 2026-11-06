"""Session — work paths, logging, and practice graphs for the active process session."""

from __future__ import annotations

import json
import os
import re
import shutil
import traceback
from datetime import datetime, timezone
from functools import cache
from pathlib import Path, PurePosixPath
from typing import TYPE_CHECKING, Callable

from harness.agent_tools import agent_instructions, agent_tool, agent_toolset
from harness.agent_tools.agent_tools import noSessionLog, tool_subject
from harness.installation.destination import data_field, language_adapter
from harness.guidance.practice_catalogue import PracticeCatalogue
from harness.installation.files import command
from harness.mcp.mcp_server import mcp
from tools.file_manager.file_manager import FileEntry, FileManager, FileText
from space.repo.repo import Repo
from space.session.chat_pointer import NO_CHAT, ChatPointer
from space.work_state import (
    LEGACY_SESSIONS_FOLDER,
    SESSIONS_FOLDER,
    WorkState,
    project_checkout,
    project_folder,
)

if TYPE_CHECKING:
    from harness.graph.graph import Graph
    from harness.guidance.guidance import FidelityGuidance, GuidanceCollection, PracticeGuidance


_SOURCE_SUFFIXES = {".py", ".ts", ".tsx", ".js", ".jsx"}
_LOAD_FILE_BUDGET = 40
_OUTPUT_PATTERN_MARKS = {"*", "{"}
CONTEXT_FOLDER = ".context"
_HANDOFF_FILES = "handoff-*.md"
# Verbs older session logs wrote, by the verb that now records the same thing.
_FORMER_VERBS = {"pull": "move"}
_REPORT_FOLDER = "validation-reports"
MAIN_SESSION_NAME = "main"
COMPLETE_FOLDER = "_complete"
_ARCHIVE_FOLDER = "_archive"
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
        """Log lines for this loop, each followed by the transcript lines its chat pointer covers. A transcript range
        that an earlier line already showed is named, not repeated."""
        parts: list[str] = []
        seen: set[tuple[str, str]] = set()
        for line in self.entries:
            parts.append(line)
            chat = ChatPointer.in_log_line(line)
            if chat is None:
                continue
            transcript = chat.transcript
            key = (str(transcript.resolve()) if transcript.exists() else str(transcript), chat.lines)
            if key in seen:
                parts.append(f"    (chat {chat.id} {chat.lines} — see above)")
                continue
            seen.add(key)
            parts.append(f"--- chat {chat} ---")
            parts.extend(chat.transcript_text())
        return "\n".join(parts)

    def inject(self, chat_file: Path, *, action: str | None = None) -> None:
        chat, body = ChatPointer.in_chat_file(Path(chat_file))
        session = self._session
        action_name = action or self._action_from_entries()
        if session is not None and action_name:
            session.append_chat(action_name, chat)
        self.entries.append(str(chat))
        if body:
            self.entries.extend(body.splitlines())

    def _action_from_entries(self) -> str:
        for line in reversed(self.entries):
            for name in _KNOWN_ACTIONS:
                if f" {name} " in f" {line} " or line.endswith(f" {name}"):
                    return name
        return ""


class SessionNotFoundError(LookupError):
    """A tool named a session.json that is not there, such as a session closed or moved since the board read it."""

    def __init__(self, session: str) -> None:
        super().__init__(f"no session at {session!r}")
        self.session = session


class UnknownPracticeError(ValueError):
    """A session was asked for a practice it does not know, such as astrology. It names the practice, so a caller can
    say which request was refused."""

    def __init__(self, practice: str) -> None:
        self.practice = practice
        super().__init__(f"Unknown practice {practice}")


class LogEntry:
    """One line of a session log: ``<time> <verb> <words...>``, the words being the subject the verb acted on."""

    # Action lines name a practice by its folder (`clean_engineering`) and validate lines by its class
    # (`CleanEngineering`).

    def __init__(self, line: str) -> None:
        self._parts = line.split()

    @property
    def time(self) -> str:
        return self._parts[0] if self._parts else ""

    @property
    def verb(self) -> str:
        """What the line records, such as move or generate; a log written before moves were named move says pull."""
        written = self._parts[1] if len(self._parts) > 1 else ""
        return _FORMER_VERBS.get(written, written)

    @property
    def words(self) -> list[str]:
        """The words after the verb, without the commas that join the paths and names an action lists."""
        return [word.rstrip(",") for word in self._parts[2:]]

    @property
    def stage(self) -> str:
        """The stage a move or a mark names: the first word after its verb."""
        words = self.words
        return words[0] if words else ""

    def names(self, fidelity: FidelityGuidance) -> bool:
        """Whether this line names fidelity and its practice."""
        practice = fidelity.practice_guidance
        words = set(self.words)
        return fidelity.name in words and bool({practice.key, type(practice).__name__} & words)


@language_adapter(language="typescript", identity=("session_file", "name"))
@agent_toolset
class PracticeSessionOutput:
    """What one practice has in one session: its guideline, the paths it reads, its graph, whether it is on, the folder
    it writes under, and the files each of its fidelities declares."""

    # The guideline, folders, and graph load on first use: the board asks every ticket's session
    # which practices are enabled after every cdd call, and that question needs none of them.

    def __init__(self, name: str, session: Session) -> None:
        self._name = name
        self._session = session
        self._guideline: PracticeGuidance | None = None
        self._output_paths: list | None = None
        self._graph: Graph | None = None

    @classmethod
    @tool_subject
    def load(cls, session: str, practice: str) -> PracticeSessionOutput:
        """The practice named practice in the session whose session.json is session, a path from the project."""
        return Session.from_file(session).practice(practice)

    @property
    @data_field
    def name(self) -> str:
        return self._name

    @property
    @data_field
    def session_file(self) -> str:
        """Its session's session.json as a path from the project, which names the session this practice is in."""
        return self._session.session_file_from_project

    @property
    def guideline(self) -> PracticeGuidance:
        """This session's own copy of the practice's guidance, which knows the session, so each of its fidelities can
        find the files it declares in this session."""
        if self._guideline is None:
            self.guideline = PracticeCatalogue.create(self.name)
        return self._guideline

    @guideline.setter
    def guideline(self, guidance: PracticeGuidance) -> None:
        """Work with guidance, the practice an action was given, at its fidelity; it now works in this session, and
        each of its fidelities answers its outputs and files from this practice."""
        guidance._attach_workspace(session=self._session.name, workspace=self._session)
        guidance.session_output = self
        self._guideline = guidance

    @property
    def fidelities(self) -> GuidanceCollection:
        """The practice's fidelities, such as story_map, by name, each able to list its files in this session."""
        return self.guideline.fidelities

    @property
    def _folders(self) -> list:
        """The sets of peer folders this practice reads in the session: the ones remembered for the repository, else
        its default folder. Callers ask for its graph or its log line instead, so how the folders are kept stays this
        class's own."""
        if self._output_paths is None:
            stored = self._session._stored_folders().get(self.name)
            self._output_paths = stored or [[str(self._default_folder)]]
        return self._output_paths

    @property
    def folders(self) -> list[Path]:
        """Every folder this practice reads in the session, in order: what an action's log line names it worked on."""
        return [Path(folder).resolve() for group in self._folders for folder in group]

    def remember_folders(self, folders: list[list[Path]]) -> None:
        """Read this practice from folders, sets of peer folders, in every session of the repository, kept in its
        ``.context/practices.json``. Folders that are the default are not kept, so a later default still applies."""
        stored = self._session._stored_folders()
        normalized = [[str(Path(item).resolve()) for item in group] for group in folders]
        if normalized == [[str(self._default_folder)]]:
            stored.pop(self.name, None)
        else:
            stored[self.name] = normalized
        self._session._write_practices_json(stored)
        self._output_paths = None
        self._graph = None

    @property
    def graph(self) -> Graph:
        if self._graph is None:
            folders = [[Path(item) for item in group] for group in self._folders]
            self._graph = self._session._graph_for(self.name, folders)
        return self._graph

    @property
    def root_node_name(self) -> str:
        """The name of the root node of this practice's graph, which an action's log line names; empty when its graph
        holds no such practice."""
        practice = self.graph.practices.get(self.name)
        return practice.root_node.name if practice is not None else ""

    @property
    def _saved(self) -> dict:
        """What session.json keeps for this practice: whether it is on, and the format each fidelity was last given."""
        return dict(self._session._fields.get("practices", {}).get(self.name, {}))

    def _save(self, **values: object) -> None:
        saved = self._session._fields.get("practices", {})
        self._session._save_fields(practices={**saved, self.name: {**self._saved, **values}})

    @property
    @data_field
    def enabled(self) -> bool:
        """Whether the session works on this practice: true until a person turns it off."""
        return self._saved.get("enabled", True)

    @mcp
    @agent_tool
    @noSessionLog
    def enable(self, is_enabled: bool) -> PracticeSessionOutput:
        """Turn this practice on or off for its session, saved in its session.json."""
        self._save(enabled=is_enabled)
        return self

    @property
    def working_fidelity(self) -> str:
        """The name of the fidelity this practice works at in the session, such as story_map; empty when it has none."""
        current = getattr(self.guideline.fidelities, "current", None)
        return str(current.name) if current is not None else ""

    @property
    def working_format(self) -> str:
        """The format this practice works in, such as drawio; empty when it has none."""
        return str(getattr(self.guideline, "format", "") or "")

    def keep_format(self) -> None:
        """Save the format this practice works in as its current fidelity's, so the next action on that fidelity in
        this session works in it without being told."""
        fidelity = self.working_fidelity
        if fidelity and self.guideline.format:
            self._save(formats={**self._saved.get("formats", {}), fidelity: self.guideline.format})

    def use_kept_format(self) -> None:
        """Work in the format last kept for the current fidelity; the fidelity's own format when none was kept."""
        kept = self._saved.get("formats", {}).get(self.working_fidelity, "")
        if kept:
            self.guideline.format = kept

    def log_validation(self, violations: list[str]) -> None:
        """Log a validate of this practice at its working fidelity in its session's log, with each violation's
        synopsis; no violations is a validate that passed."""
        detail = " ".join(violations)
        self._session.log_line(f"validate {type(self.guideline).__name__} {self.working_fidelity} {detail}".rstrip())

    @property
    def _overrides(self) -> dict:
        """What session.json's ``outputs`` keeps for this practice: the root a person chose, and under a fidelity's name
        that fidelity's own root and a file name per format for a single-file output."""
        return dict(self._session._fields.get("outputs", {}).get(self.name, {}))

    def _save_overrides(self, overrides: dict) -> None:
        outputs = dict(self._session._fields.get("outputs", {}))
        self._session._save_fields(outputs={**outputs, self.name: overrides})

    @property
    def _configured_folder(self) -> str | None:
        """The folder the project's ``.context/config.json`` names for this practice, relative to the workpath."""
        from space.context_config import ContextConfig

        project = self._session.repo_path or self._session.workpath
        return ContextConfig(project).practice_folder(self.name) if project is not None else None

    @property
    def _default_folder(self) -> Path:
        """The workpath plus the folder the project's config names for this practice, else the practice's own default
        folder, such as src for BDD."""
        relative = self._configured_folder or getattr(self.guideline, "default_workspace_folder", None) or "."
        return (self._session.work_folder / relative).resolve()

    @property
    def folder(self) -> Path:
        """The folder this practice writes under: the root a person chose, kept relative to the workpath, or its
        default folder."""
        chosen = self._overrides.get("root")
        return (self._session.work_folder / chosen).resolve() if chosen else self._default_folder

    @property
    @data_field
    def root(self) -> str:
        """The folder this practice writes under, as a path from the project: the one a person chose, or the
        workpath plus the practice's default folder."""
        return self._session.from_project(self.folder)

    @property
    @data_field
    def is_root_chosen(self) -> bool:
        """Whether a person chose this practice's root, rather than it being the default."""
        return bool(self._overrides.get("root"))

    @mcp
    @agent_tool
    @noSessionLog
    def choose_root(self, path: str) -> PracticeSessionOutput:
        """Write this practice's files under path, a folder in the repository."""
        self.keep_root(self._session.repo_from_session() / path)
        return self

    def keep_root(self, root: Path) -> None:
        """Write this practice's files under root, kept in session.json relative to the workpath, so the root still
        names the same folder after the workpath moves."""
        # A practice root holds the practice's code; its documents and diagrams go in the root's own .context.
        if CONTEXT_FOLDER in Path(root).parts:
            raise PracticeRootInContextError(self.name, Path(root))
        relative = os.path.relpath(Path(root).resolve(), self._session.work_folder)
        self._save_overrides({**self._overrides, "root": Path(relative).as_posix()})

    @mcp
    @agent_tool
    @noSessionLog
    def use_default_root(self) -> PracticeSessionOutput:
        """Write this practice's files under its default root again: the workpath plus the practice's own folder."""
        self._save_overrides({key: value for key, value in self._overrides.items() if key != "root"})
        return self

    def output_paths_of(self, fidelity: FidelityGuidance) -> dict[str, list[str]]:
        """Where fidelity, one of this practice's, writes each format in this session: its declared paths under the
        first of the fidelity's own root, the practice's chosen root, and the folder the project's config names, all
        under the workpath. session.json can also name a file per format for a single-file output."""
        overrides = self._overrides.get(str(fidelity.name), {})
        chosen = overrides.get("root") or self._overrides.get("root") or self._configured_folder
        root = (self._session.work_folder / (chosen or ".")).resolve()
        return {
            label: [_output_path(root, name) for name in _output_names(declared, overrides.get(label))]
            for label, declared in fidelity.outputs.items()
        }

    def files_of(self, fidelity: FidelityGuidance) -> dict[str, list[FileEntry]]:
        """The files fidelity declares in this session, by format, each with its path from the project and whether it
        exists. A pattern lists the files this session worked on, not every match in the repository."""
        # Asking git what the branch changed is slow, and a project that is no repository has no branch, so it is asked
        # only once a pattern finds files.
        worked_on = cache(self._session._worked_on_files)
        outputs = self.output_paths_of(fidelity)
        return {label: [entry for path in paths for entry in self._declared_files(path, worked_on)] for label, paths in outputs.items()}

    def has_output_of(self, fidelity: FidelityGuidance) -> bool:
        """Whether a file fidelity declares is already in this session, such as one a person wrote. Unlike
        ``files_of`` it never asks git: a pattern counts only in a session with a folder of its own, since on the whole
        repository a pattern also finds other sessions' files, and the board asks this of every fidelity."""
        repo = self._session._repo
        own_folder = self._session.work_folder != repo.root
        for paths in self.output_paths_of(fidelity).values():
            for declared in paths:
                pattern = _named_parts_as_wildcards(repo.path_from_top(declared))
                if "*" not in pattern and (repo.root / pattern).exists():
                    return True
                if "*" in pattern and own_folder and repo.file_manager.find(pattern):
                    return True
        return False

    def _declared_files(self, declared: str, worked_on: Callable[[], set[Path] | None]) -> list[FileEntry]:
        """A declared path, or each file of this session's that a pattern finds; a pattern that finds none stays as
        written, not yet there."""
        repo = self._session._repo
        relative = repo.path_from_top(declared)
        pattern = _named_parts_as_wildcards(relative)
        if "*" not in pattern:
            return [FileEntry(relative, (repo.root / relative).exists())]
        found = repo.file_manager.find(pattern)
        mine = worked_on() if found else None
        found = [path for path in found if mine is None or path.resolve() in mine]
        return [FileEntry(repo.path_from_top(path), True) for path in found] or [FileEntry(relative, False)]



@language_adapter(language="typescript", identity="session_file")
@agent_toolset
class Session:
    """Work session — one in-memory current for each project; new and switch open named sessions."""

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
        # A chat named for the next log line only, ahead of the chat of the tool call being served.
        self._chat: ChatPointer | None = None
        self._file_manager: FileManager | None = None

    @property
    @data_field
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
        workpath = Path(self.workpath or self.repo_from_session()).resolve()
        roots = tuple(sorted({practice.folder for practice in self.practices.values()}))
        if self._file_manager is None or self._file_manager.roots != roots:
            self._file_manager = FileManager(workpath, roots)
        return self._file_manager

    @classmethod
    def _slot(cls, repo_path: Path | str | None = None) -> Session:
        """The in-memory current session of ``repo_path``'s checkout, else of the project being worked on."""
        repo = Repo(repo_path).checkout_folder if repo_path is not None else project_checkout()
        return cls._current_by_project.setdefault(repo, cls())

    @classmethod
    def forget_current(cls, repo_path: Path | str | None = None) -> None:
        """Drop the in-memory current session of ``repo_path``'s checkout, or of every project when none is named, so
        the next call reads ``.sessions/`` again. Naming the project leaves other chats' sessions as they are."""
        if repo_path is None:
            cls._current_by_project.clear()
            return
        cls._current_by_project.pop(Repo(repo_path).checkout_folder, None)

    @classmethod
    def refresh_current_from_repo(cls, repo_path: Path | str | None = None) -> None:
        """Reload in-memory session when repo ``.sessions/session.json`` current changed."""
        repo = Repo(repo_path).checkout_folder if repo_path is not None else project_checkout()
        slot = cls._slot(repo)
        saved = Repo(repo).current_session.name
        if slot.name == saved and slot.session_path is not None and slot.repo_path == repo:
            return
        cls._current_by_project.pop(repo, None)
        session = cls._slot(repo)
        session._open(saved, repo, Repo(repo).session_folder(saved), repo if saved == MAIN_SESSION_NAME else None)

    def new_handoff_path(self) -> Path:
        """A new ``handoff-{timestamp}.md`` in this session's folder, which it creates; names sort by time, so
        ``latest_handoff`` finds the newest."""
        self.session_path.mkdir(parents=True, exist_ok=True)
        return self.session_path / f"handoff-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')}.md"

    @classmethod
    @mcp
    @command(name="current-session")
    @agent_tool
    def current(cls, repo_path: Path | str | None = None) -> Session:
        """The session saved on the repo; the main session, which works on the whole repository, when none is named."""
        cls.refresh_current_from_repo(repo_path)
        return cls._slot(repo_path)

    def repo_from_session(self) -> Path:
        """The repository that holds this session's ``.sessions``: the one it was opened in, else the project's."""
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
        self.saved_current_session = MAIN_SESSION_NAME
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
    @tool_subject
    def from_file(cls, session: str) -> Session:
        """The session whose session.json is session, a path from the project or an absolute one, read without becoming
        the current session; the current session when it names none. A board command names its ticket's session this
        way, because it runs in whichever chat it is sent to, and that chat's open session can be another."""
        if not session:
            return cls.current()
        project = project_checkout()
        named = Path(session)
        found = named if named.is_absolute() else project / named
        if not found.is_file():
            raise SessionNotFoundError(session)
        return cls.load(found.parent, project)

    @staticmethod
    def timestamp(moment: datetime) -> str:
        """A moment as session logs write it."""
        return moment.astimezone(timezone.utc).strftime(_TIMESTAMP_FORMAT)

    @property
    def is_closed(self) -> bool:
        return self.session_path is not None and self.session_path.parent.name == COMPLETE_FOLDER

    @property
    def session_file(self) -> Path:
        """The ``session.json`` in this session's folder, which holds its title, workpath, practice roots, and practices."""
        return self.session_path / "session.json"

    @property
    @data_field(key="session_file")
    def session_file_from_project(self) -> str:
        """Its session.json as a path from the project: the name every board command gives this session."""
        return self.from_project(self.session_file)

    @property
    @data_field(key="workpath")
    def workpath_from_project(self) -> str:
        """The folder the session works in, as a path from the project; empty for the whole repository."""
        return self.from_project(Path(self.workpath or self.repo_from_session()).resolve())

    @property
    @data_field(key="handoff")
    def latest_handoff(self) -> str:
        """The newest handoff file, as a path from the project; handoff names sort by their timestamp."""
        handoffs = sorted(self.session_path.glob(_HANDOFF_FILES))
        return self.from_project(handoffs[-1]) if handoffs else ""

    def from_project(self, path: Path | str) -> str:
        """path as written from the project's top, the way the board names every file and folder."""
        return Repo(self.repo_from_session()).path_from_top(path)

    @mcp
    @agent_tool
    @noSessionLog
    def files(self) -> dict[str, dict[str, dict[str, list[FileEntry]]]]:
        """List the files every practice this session works on declares, by practice, fidelity, and format, each with its path from the project and whether it exists."""
        return {name: practice.guideline.files() for name, practice in self.practices.items() if practice.enabled}

    @mcp
    @agent_tool
    @noSessionLog
    def folder_files(self) -> list[FileEntry]:
        """List every file in this session's folder, each with its path from the project: its log, handoffs, kept notes, and validation reports."""
        repo = self._repo
        files = sorted(path for path in self.session_path.rglob("*") if path.is_file())
        return [FileEntry(repo.path_from_top(path), True) for path in files]

    @mcp
    @agent_tool
    @noSessionLog
    def read_file(self, path: str) -> FileText:
        """Return the text of path, a file in this repository; no text when the file is gone, such as one deleted since the board listed it."""
        return self._repo.file_manager.read(path)

    @property
    def reports_folder(self) -> Path:
        """Where Validate saves its reports in this session, each with the graph it checked beside it."""
        return self.session_path / _REPORT_FOLDER

    @property
    def _repo(self) -> Repo:
        return Repo(self.repo_from_session())

    @property
    def work_folder(self) -> Path:
        """The folder the session works in: its workpath, else the whole repository. Each practice's root is kept
        relative to it."""
        return Path(self.workpath or self.repo_path or project_folder()).resolve()

    def _worked_on_files(self) -> set[Path] | None:
        """The files that are this session's work: every file when it works in a folder of its own, which holds only its
        work; on the whole repository, only the files its branch changed."""
        repo = self._repo
        if Path(self.workpath or repo.root).resolve() != repo.root:
            return None
        return {(repo.root / path).resolve() for path in repo.files_changed_on(self.name)}

    @property
    @data_field
    def title(self) -> str:
        """The title a person gave the session's ticket; empty when it has none."""
        return self._fields.get("title", "")

    @property
    @data_field
    def scope(self) -> str:
        """feature, story, or slice; empty when no one said."""
        return self._fields.get("scope", "")

    @property
    @data_field
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

    def keep_file(self, file: Path) -> Path:
        """Move ``file`` into this session's folder, where it stays with the session's work until it becomes lasting
        context, such as part of a story map. A started backlog item's text is the only copy of the idea."""
        kept = self.session_path / file.name
        file.replace(kept)
        return kept

    @mcp
    @agent_tool
    @noSessionLog
    def choose_workpath(self, path: str) -> Session:
        """Make path, a folder in the repository, this session's workpath: the folder its practices write under and its graph loads from. An empty path is the whole repository."""
        # A practice root a person chose is kept relative to the workpath, so each is saved again against the new one
        # and still names the same folder.
        chosen = {practice: practice.folder for practice in self.practices.values() if practice.is_root_chosen}
        self.workpath = (self.repo_from_session() / path).resolve()
        self._write_session_folder_json()
        for practice, root in chosen.items():
            practice.keep_root(root)
        return self

    def move_folder_to(self, parent: Path) -> Session:
        """Move this session's folder under ``parent``, such as ``.sessions/_complete/``."""
        parent.mkdir(parents=True, exist_ok=True)
        destination = parent / self.name
        shutil.move(str(self.session_path), str(destination))
        return type(self).load(destination, self.repo_path)

    def move_to_closed(self) -> Session:
        return self.move_folder_to(Repo(self.repo_path).sessions_folder / COMPLETE_FOLDER)

    def move_to_archive(self) -> Session:
        return self.move_folder_to(Repo(self.repo_path).sessions_folder / _ARCHIVE_FOLDER)

    def move_to_backlog(self) -> Session:
        return self.move_folder_to(Repo(self.repo_path).backlog_folder)

    def reopen(self) -> Session:
        """Back among the open sessions, from closed or the backlog."""
        return self.move_folder_to(Repo(self.repo_path).sessions_folder)

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
        repo = cls._repo_to_switch_in(workpath, repo_path, session_path)
        wanted = cls._session_name(name, repo)
        folder = Path(session_path).resolve() if session_path is not None else Repo(repo).session_folder(wanted)
        if not (folder / "session.json").is_file():
            return cls.new(wanted, Path(workpath) if workpath is not None else project_folder(), repo)
        slot = cls._slot(repo)
        slot._open(wanted, repo, folder, Path(workpath) if workpath is not None else None)
        return slot.keep_log()

    @classmethod
    def _repo_to_switch_in(cls, workpath: Path | None, repo_path: Path | None, session_path: Path | None) -> Path:
        """The checkout a switch works in: the one named, else the one holding the workpath, else the one a named
        session folder was saved in, else the project's."""
        if repo_path is not None:
            return Repo(repo_path).checkout_folder
        if workpath is not None:
            return Repo(workpath).checkout_folder
        if session_path is not None:
            saved = cls._read_session_folder_json(Path(session_path)).get("repo_path")
            return Path(saved) if saved else cls._repo_holding(Path(session_path))
        return project_checkout()

    @classmethod
    def _session_name(cls, name: str, repo: Path) -> str:
        state = WorkState(repo)
        branch = state.branch
        cleaned = name_of(name or state.session or (branch.name if branch is not None else ""))
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
        session._note_chat_given(conversation_id, transcript_path, transcript_lines)
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
        session._note_chat_given(conversation_id, transcript_path, transcript_lines)
        loop_number = session._resolve_append_loop(loop)
        path_objs = [Path(item) for item in (paths or []) if str(item).strip()]
        body = text if text.lower().startswith(f"loop {loop_number}") else f"loop {loop_number}: {text}"
        session.log_note(body, path_objs or None)
        log_path = session.log_path or "session.log"
        return f"appended note to {log_path} (loop {loop_number})"

    @property
    def saved_current_session(self) -> str:
        """``session`` in repo/.sessions/session.json."""
        if self.repo_path is None:
            return MAIN_SESSION_NAME
        return Repo(self.repo_path).current_session.name

    @saved_current_session.setter
    def saved_current_session(self, name: str) -> None:
        if self.repo_path is None:
            return
        cleaned = (name or "").strip()
        if cleaned == MAIN_SESSION_NAME:
            cleaned = ""
        WorkState(self.repo_path).session = cleaned
        if cleaned:
            from harness.hooks.session_logs import SessionLogs

            SessionLogs(self.repo_path).write_active_session(cleaned)

    def practice(self, name: str) -> PracticeSessionOutput:
        found = self._opened_named(name)
        if found is not None:
            return found
        if not PracticeCatalogue.has(name):
            raise UnknownPracticeError(name)
        opened = self.practices[name]
        self._opened.append(opened)
        return opened

    @property
    @data_field
    def practices(self) -> dict[str, PracticeSessionOutput]:
        """Every practice CDD has, by practice key, opened or not."""
        for name in PracticeCatalogue.keys():
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
        return Repo(self.repo_path)

    def note_injected_rule(
        self, practice: str, fidelity: str, rule: str, matched_path: str = ""
    ) -> None:
        entry = (practice, fidelity, rule, matched_path)
        if entry not in self._injected:
            self._injected.append(entry)

    def note_chat(self, chat: ChatPointer) -> None:
        """Point the next log line at chat, in place of the chat of the tool call being served."""
        self._chat = chat

    def reset(self) -> None:
        self._known = {}
        self._opened = []

    def _open(self, name: str, repo: Path, folder: Path, workpath: Path | None = None) -> Session:
        """Become the session called name, kept in folder, in the checkout repo, and make it the repo's saved current
        session. It works in workpath when one is given, else the workpath its session.json saved, else the project's
        folder."""
        self.name = name
        self.repo_path = Path(repo).resolve()
        self.session_path = Path(folder).resolve()
        saved = self._fields.get("workpath")
        if workpath is not None:
            self.workpath = Path(workpath).resolve()
        else:
            self.workpath = Path(saved) if saved else project_folder()
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
        log = self.log_path
        if log is None or not log.is_file():
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

    def _note_chat_given(self, conversation_id: str, transcript_path: str, transcript_lines: str) -> None:
        """A call made from Python names its chat in its own arguments; an MCP call's chat is already being served."""
        chat = ChatPointer.of(conversation_id, transcript_path, transcript_lines)
        if chat is not None:
            self.note_chat(chat)

    def loop(self) -> Loop:
        from_memory = self._loops[-1].number if self._loops else 0
        from_log = self._max_loop_number_from_log()
        number = max(from_memory, from_log) + 1
        opened = Loop(number)
        opened._session = self
        self._loops.append(opened)
        self.record(f"--- {number} {self._line_chat()}")
        return opened

    @staticmethod
    def _loop_marker_number(line: str) -> int | None:
        match = _LOOP_MARKER.search(line)
        if not match:
            return None
        return int(match.group(1))

    def _lines_for_loop(self, number: int) -> list[str]:
        log = self.log_path
        if log is None or not log.is_file():
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

    def _line_chat(self) -> ChatPointer:
        """The chat the next log line points at: one noted for it, else the chat of the call being served, else
        ``no-chat``. A noted chat is used once."""
        chat = self._chat or ChatPointer.current() or NO_CHAT
        self._chat = None
        return chat

    def log_action(self, action: str, paths: list[Path]) -> None:
        if self.session_path is None:
            return
        self.record(self._action_line(action, paths))
        self._injected.clear()

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
        parts = ["tool", name]
        if paths:
            parts.append(", ".join(str(path) for path in paths))
        rules = self._rule_text()
        if rules:
            parts.append(rules)
        # A tool line names its chat only when one is known; most tool calls come from a chat the server can name.
        chat = self._line_chat()
        if not chat.is_missing:
            parts.append(str(chat))
        self.record(" ".join(parts))
        self._injected.clear()

    def log_note(self, message: str, paths: list[Path] | None = None) -> None:
        """Record a correction or decision in the current loop (use after user steers logging or close behavior)."""
        if self.session_path is None:
            return
        text = (message or "").strip()
        if not text:
            return
        parts = ["note", text]
        if paths:
            parts.append(", ".join(str(path) for path in paths))
        parts.append(str(self._line_chat()))
        self.record(" ".join(parts))

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

    def log_guidance_action(self, action: str) -> None:
        """Log a guidance action on the practices this session has opened, with the workpath and each practice's
        folders as the paths it worked on."""
        work = [Path(self.workpath).resolve()] if self.workpath is not None else []
        folders = [folder for practice in self._opened for folder in practice.folders]
        self.log_action(action, list(dict.fromkeys([*work, *folders])))

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
        practice = PracticeCatalogue.key_of(guidance) or type(guidance).__name__.casefold()
        for bag in bags:
            fidelity = self._fidelity_for_rules_bag(guidance, bag)
            for rule in bag:
                self.note_injected_rule(practice, fidelity, rule.slug, matched_path)

    def log_line(self, line: str) -> None:
        """Append line to session.log with the noted chat's pointer, such as a practice's validate line."""
        if self.session_path is None:
            return
        self.record(f"{line} {self._line_chat()}")
        self._injected.clear()

    def record_failure(self, failure: BaseException, *, tool: str = "") -> None:
        """Append a full trace to session.err and a pointer line on session.log (does not raise)."""
        if self.session_path is None:
            return
        trace = "".join(traceback.format_exception(type(failure), failure, failure.__traceback__))
        err = self.error_path
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
        parts = ["error", str(err), str(line_number)]
        name = (tool or "").strip()
        if name:
            parts.insert(1, name)
        parts.append(str(self._line_chat()))
        self.record(" ".join(parts))

    def log_error(self, failure: BaseException) -> None:
        self.record_failure(failure)
        raise failure

    def append_chat(self, action: str, chat: ChatPointer) -> None:
        """Point action's earlier log lines at chat, and log that the chat was added."""
        self._append_to_action_line(action, str(chat))
        self.record(f"{action} chat {chat}")

    def keep_log(self) -> str:
        log_file = str(self.log_path or "session.log")
        err_file = str(self.error_path or "session.err")
        return (
            "Session owns logging once session.switch has run. "
            "CHAT POINTERS — required for continued conversations: every log line ends with a chat pointer, "
            "the chat id, the agent transcript JSONL path, and the transcript line range "
            "(`{id} {transcript} {lines}`), or `no-chat` when no chat can be named. "
            "MCP: pass conversation_id, transcript_path, transcript_lines on any tool call; the server takes "
            "them off the call and every line that call writes points at that chat. A Claude Code chat may "
            "pass conversation_id alone, and its transcript is found by that id. "
            "Without them the pointer comes from CDD_CONVERSATION_ID, CDD_TRANSCRIPT_PATH, CDD_TRANSCRIPT_LINES. "
            "Long threads: use an accurate slice for this turn or a cumulative range (e.g. 1-1152, "
            "then 1-1450) so read_loop can inline the full dialogue for that loop. "
            "Missing chat on an earlier line: append_chat(action, chat) or session.append_log "
            "(/append-log); never hand-edit session.log. "
            "MARK-LOOP — link the entire conversation span: call session.mark_loop (/mark-loop) only "
            "with chat fields on that MCP invoke. Dispatch writes tool session.mark_loop with a pointer; "
            "the --- N marker line records the same pointer when bound—both tie the loop to the transcript. "
            "After marking, log actions in that loop with the same thread id and growing line ranges so "
            "read_loop(number) expands every line in the loop with matching transcript slices. "
            "WHERE LINES COME FROM: @agent_tool invocations (AgentOperation.invoke / MCP → "
            "log_session_invocation; guidance kits use GuidanceAgentOperation override). run logs "
            "via log_guidance_action (Validate logs each practice's log_validation instead). record_failure on run "
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
        self.session_path = Repo(self.repo_path).sessions_folder / name
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
        self.record("--- 1")

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

    @staticmethod
    def _read_session_folder_json(session_path: Path) -> dict:
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

    @staticmethod
    def _repo_holding(session_path: Path) -> Path:
        folder = Path(session_path).resolve().parent
        if folder.name in {SESSIONS_FOLDER, LEGACY_SESSIONS_FOLDER}:
            return folder.parent
        return folder

    def _opened_named(self, name: str) -> PracticeSessionOutput | None:
        for opened in self._opened:
            if opened.name == name:
                return opened
        return None

    @staticmethod
    def _fidelity_for_rules_bag(guidance: PracticeGuidance, bag) -> str:
        parent = getattr(bag, "parent", None)
        if parent is guidance or parent is None:
            current = getattr(getattr(guidance, "fidelities", None), "current", None)
            return str(getattr(current, "name", "") or "")
        return str(getattr(parent, "name", "") or "")

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

    def _stored_folders(self) -> dict:
        return dict(self._parent_folders)

    def _write_practices_json(self, stored: dict) -> None:
        """Keep stored, each practice's remembered folders, in the repository's ``.context/practices.json``."""
        self._parent_folders = dict(stored)
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
        fidelity = ", ".join(entry.working_fidelity for entry in self._opened if entry.working_fidelity)
        layout = ", ".join(entry.working_format for entry in self._opened if entry.working_format)
        nodes = " ".join(entry.root_node_name for entry in self._opened if entry.root_node_name)
        rules = self._rule_text()
        chat = str(self._line_chat())
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

    @property
    def log_path(self) -> Path | None:
        """The session's session.log, where every action, note, and loop marker is written; none before the session has a folder."""
        return self.session_path / "session.log" if self.session_path is not None else None

    @property
    def error_path(self) -> Path | None:
        """The session's session.err, which keeps the full trace of each failure that session.log points at."""
        return self.session_path / "session.err" if self.session_path is not None else None

    @property
    def log_entries(self) -> list[LogEntry]:
        """Every line of session.log, oldest first; none before anything is logged."""
        log = self.log_path
        if log is None or not log.is_file():
            return []
        return [LogEntry(line) for line in log.read_text(encoding="utf-8").splitlines() if line.strip()]

    def _rule_text(self) -> str:
        if not self._injected:
            return ""
        ordered = sorted(self._injected, key=lambda item: (item[0], item[1], item[2], item[3]))
        return " ".join(
            " ".join(part for part in (practice, fidelity, rule, path) if part)
            for practice, fidelity, rule, path in ordered
        )

    def _append_to_action_line(self, action: str, pointer: str) -> None:
        log = self.log_path
        if log is None or not log.is_file():
            return
        lines = log.read_text(encoding="utf-8").splitlines()
        for index, line in enumerate(lines):
            if f" {action} " in f" {line} " or line.endswith(f" {action}"):
                lines[index] = f"{line} {pointer}"
        log.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")

    def record(self, line: str) -> None:
        """Append line to session.log, stamped with the time it was written."""
        if self.session_path is None:
            return
        stamp = self.timestamp(datetime.now(timezone.utc))
        written = f"{stamp} {line}"
        with self.log_path.open("a", encoding="utf-8") as handle:
            handle.write(written + "\n")
        if self._loops and not line.startswith("--- "):
            self._loops[-1].entries.append(written)


def _output_names(declared: str | list[str], override: str | None) -> list[str]:
    """The file names a declared output writes: override in place of the declared name for a single-file output."""
    names = [declared] if isinstance(declared, str) else list(declared)
    is_single_file = len(names) == 1 and not set(names[0]) & _OUTPUT_PATTERN_MARKS
    return [PurePosixPath(names[0]).with_name(override).as_posix()] if override and is_single_file else names


def _output_path(root: Path, name: str) -> str:
    folder_mark = "/" if name.endswith("/") else ""
    return f"{(root / name).as_posix()}{folder_mark}"


def _named_parts_as_wildcards(path: str) -> str:
    """A declared path with its named parts, such as `{module}/{module}-model.md`, as a pattern. A named folder can be
    a module several folders deep, so it matches folders at any depth; a named part of a file name matches within it."""
    folders = re.sub(r"\{[^{}/]+\}/", "**/", path)
    return re.sub(r"\{[^{}/]+\}", "*", folders)
