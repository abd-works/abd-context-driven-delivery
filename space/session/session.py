"""Session — one named piece of work in a project: its folder, its workpath, its practices, its log, and its handoffs."""

from __future__ import annotations

import json
import shutil
import threading
from pathlib import Path
from typing import TYPE_CHECKING, ClassVar

from harness.agent_tools import agent_instructions, agent_tool, agent_toolset, tools
from harness.agent_tools.agent_tools import noSessionLog, tool_subject
from harness.agent_tools.chat_pointer import ChatPointer
from harness.graph.graph import Graph
from harness.guidance.practice_catalogue import PracticeCatalogue
from harness.guidance.documents import load_document
from harness.installation.destination import data_field, identity, language_adapter
from harness.installation.files import command, skill
from harness.mcp.mcp_server import mcp
from harness.installation.context_config import CONTEXT_FOLDER
from space.repo.repo import Repo
from space.session.decision_records import FORMAT_FILE, DecisionRecords
from space.session.handoffs import HANDOFF_FORMAT_FILE, Handoffs
from space.session.practice_session_output import PracticeSessionOutput
from space.session.session_files import SessionFiles
from space.session.session_log import SessionLog
from space.work_state import WorkState
from tools.file_manager.file_manager import FileEntry, FileText

if TYPE_CHECKING:
    from space.session.sessions import Sessions

MAIN_SESSION_NAME = "main"
COMPLETE_FOLDER = "_complete"
ARCHIVE_FOLDER = "_archive"
SESSION_FILE = "session.json"
_REPORT_FOLDER = "validation-reports"
_HOOK_LOGS_FOLDER = "logs"
_DECISION_RECORDS_FOLDER = "cdr"


class SessionNotFoundError(LookupError):
    """A tool named a session.json that is not there, such as a session closed or moved since the board read it."""

    def __init__(self, session: str) -> None:
        super().__init__(f"no session at {session!r}: name the session.json of the session to work on")
        self.session = session


class UnknownPracticeError(ValueError):
    """A session was asked for a practice it does not know, such as astrology. It names the practice, so a caller can
    say which request was refused."""

    def __init__(self, practice: str) -> None:
        self.practice = practice
        super().__init__(f"Unknown practice {practice}")


@identity("session_file")
@language_adapter(language="typescript")
@agent_toolset
class Session:
    """One named piece of work in a project, kept in ``.sessions/{name}/``. It holds where it works, the practices it
    uses, and its title; its log, files, handoffs, and decision records are objects of their own. Every tool on it acts
    on the session whose ``session.json`` its ``session`` argument names."""

    # The graph of each session the cdd server works in, by the session's folder, with the root it was opened on. The
    # graph holds the session's one instance of each practice, which its actions work with too. A Session is read from
    # its folder again on every call, so these are kept here for as long as the server runs.
    _held: ClassVar[dict[Path, tuple[Path, Graph]]] = {}
    _held_lock: ClassVar[threading.Lock] = threading.Lock()

    def __init__(self, repo_root: Path | str) -> None:
        self._session_name = ""
        self.workpath: Path | None = None
        self.repo_path: Path = Path(repo_root).resolve()
        self.session_path: Path | None = None
        # The chat of the tool call this session was opened for: its log lines point at it.
        self.chat: ChatPointer | None = None
        self._known: dict[str, PracticeSessionOutput] = {}
        self._opened: list[PracticeSessionOutput] = []
        self.log = SessionLog(self)
        self.session_files = SessionFiles(self)

    @classmethod
    def load(cls, session_path: Path, repo_path: Path) -> Session:
        """The session kept in ``session_path``, read without opening it."""
        session = cls(repo_path)
        session.session_path = Path(session_path)
        session.name = session.session_path.name
        stored = session.fields.get("workpath", "")
        session.workpath = Path(stored) if stored else session.repo_path
        return session

    @classmethod
    @tool_subject
    def from_file(cls, session: str, project: Path | str) -> Session:
        """The session whose session.json is session, a path from project's checkout or an absolute one, read without
        opening it. A board command names its ticket's session this way, because it runs in whichever chat it is sent
        to, and that chat's open session can be another. A tool call is handed the project the call names."""
        checkout = Repo(project).checkout_folder
        named = Path(session)
        found = named if named.is_absolute() else checkout / named
        if not session or not found.is_file():
            raise SessionNotFoundError(session)
        return cls.load(found.parent, checkout)

    @property
    @data_field
    def name(self) -> str:
        """Named work session (not the toolset slug)."""
        return self._session_name

    @name.setter
    def name(self, value: str) -> None:
        self._session_name = (value or "").strip()

    @property
    def repo(self) -> Repo:
        """The repository that holds this session's ``.sessions``."""
        return Repo(self.repo_path)

    @property
    def is_closed(self) -> bool:
        return self.session_path is not None and self.session_path.parent.name == COMPLETE_FOLDER

    @property
    def session_file(self) -> Path:
        """The ``session.json`` in this session's folder, which holds its title, workpath, practice roots, and practices."""
        return self.session_path / SESSION_FILE

    @property
    @data_field(key="session_file")
    def session_file_from_project(self) -> str:
        """Its session.json as a path from the project: the name every board command gives this session."""
        return self.from_project(self.session_file)

    @property
    def root(self) -> Path:
        """The folder the session works in: its workpath, or the whole repository when it chose none. Actions write
        their sketches, grill answers, and partitions under it, each practice's folder is kept relative to it, and the
        file manager reads under it."""
        return Path(self.workpath or self.repo_path).resolve()

    @property
    def graph(self) -> Graph:
        """The knowledge graph this session works with, opened on its root, holding the session's one instance of each
        practice. The cdd server holds it in memory from the session's first call on, so every call in the session works
        on the same graph and the same practices, and none rebuilds them; an action that writes files refreshes the graph
        with exactly those files. A session whose root has moved gets a new graph, with new practices, on the new root."""
        key = Path(self.session_path or self.root).resolve()
        root = self.root
        with Session._held_lock:
            held = Session._held.get(key)
            if held is None or held[0] != root:
                held = (root, self._new_graph())
                Session._held[key] = held
            return held[1]

    def _new_graph(self) -> Graph:
        """A graph on this session's root holding a new instance of every practice, each working in this session."""
        practices = PracticeCatalogue.create_all()
        kept = self._unopened()
        for practice in practices:
            practice.work_in(PracticeSessionOutput(practice, kept))
        graph = Graph(practices)
        graph.open(self.root)
        return graph

    def _unopened(self) -> Session:
        """This session as no call opened it, which the practices it keeps between calls work in, so they never point
        at the chat of the call that first asked for them."""
        kept = type(self)(self.repo_path)
        kept.session_path = self.session_path
        kept.name = self.name
        kept.workpath = self.workpath
        return kept

    def path_named(self, named: str | Path) -> Path:
        """named as a path in this session's project, the way its agent writes one: from the project's root, or
        absolute. The cdd server serves every project from its own working folder, so a relative path read as given
        would name a file in the server's checkout instead of this project's."""
        path = Path(named)
        return path.resolve() if path.is_absolute() else (self.repo_path / path).resolve()

    def document_named(self, content: str = "", paths: list[str] | str | None = None) -> str:
        """The document a call names: content, or the files at paths, read from this session's project."""
        if paths in ("", None, []):
            return load_document(content)
        entries = [paths] if isinstance(paths, (str, Path)) else list(paths)
        return load_document(content, [str(self.path_named(entry)) for entry in entries])

    @property
    @data_field(key="workpath")
    def workpath_from_project(self) -> str:
        """The folder the session works in, as a path from the project; empty for the whole repository."""
        return self.from_project(self.root)

    def from_project(self, path: Path | str) -> str:
        """path as written from the project's top, the way the board names every file and folder."""
        return self.repo.path_from_top(path)

    @property
    @data_field
    def title(self) -> str:
        """The title a person gave the session's ticket; empty when it has none."""
        return self.fields.get("title", "")

    @property
    @data_field
    def scope(self) -> str:
        """feature, story, or slice; empty when no one said."""
        return self.fields.get("scope", "")

    @property
    @data_field
    def parent(self) -> str:
        """The name of the session this one was split from; empty when it was not split from one."""
        return self.fields.get("parent", "")

    @property
    def fields(self) -> dict:
        """What ``session.json`` in this session's folder holds, read each time; nothing before it has a folder."""
        path = self.session_path / SESSION_FILE if self.session_path else None
        return json.loads(path.read_text(encoding="utf-8")) if path is not None and path.is_file() else {}

    def save_fields(self, **values: object) -> None:
        """Merge ``values`` into ``session.json``, keeping what others store there, and make the session's folder when
        it has none yet, as a project's main session has none until something is saved in it."""
        self.session_path.mkdir(parents=True, exist_ok=True)
        self.session_file.write_text(json.dumps({**self.fields, **values}), encoding="utf-8")

    def save(self) -> None:
        """Save this session's name, workpath, and repository in its ``session.json``, creating its folder, and keep
        the fields others store there, such as a board ticket's title, scope, and parent."""
        if self.session_path is None:
            return
        self.save_fields(name=self.name, workpath=str(self.root), repo_path=str(self.repo_path))

    @property
    def reports_folder(self) -> Path:
        """Where Validate saves its reports in this session, each with the graph it checked beside it."""
        return self.session_path / _REPORT_FOLDER

    def hook_log(self, filename: str) -> Path:
        """The log called filename that a hook appends to while this session is open, such as dispatch.debug, in the
        ``logs`` folder of the session's folder, which is made when missing."""
        folder = self.session_path / _HOOK_LOGS_FOLDER
        folder.mkdir(parents=True, exist_ok=True)
        return folder / filename

    def keep_file(self, file: Path) -> Path:
        """Move ``file`` into this session's folder, where it stays with the session's work until it becomes lasting
        context, such as part of a story map. A started backlog item's text is the only copy of the idea."""
        kept = self.session_path / file.name
        file.replace(kept)
        return kept

    def move_to_closed(self) -> Session:
        return self._move_folder_to(self._sessions_folder / COMPLETE_FOLDER)

    def move_to_archive(self) -> Session:
        return self._move_folder_to(self._sessions_folder / ARCHIVE_FOLDER)

    def move_to_backlog(self) -> Session:
        return self._move_folder_to(self._sessions.backlog_folder)

    def reopen(self) -> Session:
        """Back among the open sessions, from closed or the backlog."""
        return self._move_folder_to(self._sessions_folder)

    @property
    def _sessions(self) -> Sessions:
        """Every session of this session's repository, and which of them is open."""
        # WHY: Sessions makes and loads Session objects, so space.session.sessions imports this module.
        from space.session.sessions import Sessions

        return Sessions(self.repo_path)

    @property
    def _sessions_folder(self) -> Path:
        return WorkState(self.repo_path).sessions_folder

    def _move_folder_to(self, parent: Path) -> Session:
        """Move this session's folder under ``parent``, such as ``.sessions/_complete/``; the session as it is there."""
        parent.mkdir(parents=True, exist_ok=True)
        destination = parent / self.name
        shutil.move(str(self.session_path), str(destination))
        return type(self).load(destination, self.repo_path)

    def practice(self, name: str) -> PracticeSessionOutput:
        """The practice called name in this session, opened, so this session's log lines name it."""
        found = next((opened for opened in self._opened if opened.name == name), None)
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
        """Every practice CDD has, by practice key, opened or not, each the session's one instance of it."""
        if len(self._known) < len(PracticeCatalogue.keys()):
            for key, guidance in self.graph.every_practice.items():
                self._known.setdefault(key, PracticeSessionOutput(guidance, self))
        return dict(self._known)

    @property
    def active_practices(self) -> list[PracticeSessionOutput]:
        return [practice for practice in self.practices.values() if practice.enabled]

    @property
    def opened_practices(self) -> list[PracticeSessionOutput]:
        """The practices this session has asked for, which its log lines name."""
        return list(self._opened)

    def reset(self) -> None:
        """Forget the practices this session opened, so each opens again on the next ask."""
        self._known = {}
        self._opened = []

    @property
    def handoffs(self) -> Handoffs:
        """The handoffs this session keeps in its folder."""
        return Handoffs(self.session_path)

    @property
    @data_field(key="handoff")
    def latest_handoff(self) -> str:
        """The newest handoff file, as a path from the project; empty before one is written."""
        latest = self.handoffs.latest
        return self.from_project(latest) if latest is not None else ""

    @property
    def decision_records(self) -> DecisionRecords:
        """The Context Decision Records this session keeps, under its workpath's ``.context/cdr/``."""
        return DecisionRecords(self.root / CONTEXT_FOLDER / _DECISION_RECORDS_FOLDER)

    @mcp
    @command(name="close-session")
    @agent_tool
    def close(self) -> None:
        """Close this work session: when it is the open session of its project, main becomes the open one.

        ``session`` is the session's session.json; ask ``sessions.current`` for it when the user names no session."""
        self._sessions.close(self)

    @mcp
    @agent_tool
    @noSessionLog
    def choose_workpath(self, path: str = "") -> Session:
        """Make path, a folder in the repository, this session's workpath: the folder its practices write under and its graph loads from. An empty path is the whole repository."""
        # A practice root a person chose is kept relative to the workpath, so each is saved again against the new one
        # and still names the same folder.
        chosen = {practice: practice.folder for practice in self.practices.values() if practice.is_root_chosen}
        self.workpath = (self.repo_path / path).resolve()
        self.save()
        for practice, root in chosen.items():
            practice.keep_root(root)
        return self

    @mcp
    @agent_tool
    @noSessionLog
    def folder_files(self) -> list[FileEntry]:
        """List every file in this session's folder, each with its path from the project: its log, handoffs, kept notes, and validation reports."""
        return self.session_files.in_folder()

    @mcp
    @agent_tool
    @noSessionLog
    def read_file(self, path: str = "") -> FileText:
        """Return the text of path, a file in this repository or under a folder this session's practices write to, such as its ticket's worktree; no text when the file is gone, such as one deleted since the board listed it."""
        return self.session_files.read(path)

    @mcp
    @command(name="mark-loop")
    @agent_tool
    def mark_loop(self) -> str:
        """Mark the next loop in this session's log (slash ``/mark-loop``); returns its number.

        ``session`` is the session's session.json; ask ``sessions.current`` for it when the user names no session.
        Pass ``conversation_id``, ``transcript_path``, and ``transcript_lines`` (cumulative JSONL range for this chat)
        on the call; the ``--- N`` marker carries that chat's pointer."""
        return str(self.log.mark_loop())

    @mcp
    @command(name="read-loop")
    @agent_tool
    def read_loop(self, number: int | None = None) -> str:
        """Read one loop from this session's log with chat transcript lines inlined.

        ``session`` is the session's session.json; ask ``sessions.current`` for it when the user names no session.
        ``number`` defaults to the latest loop with log lines. Run via MCP ``session.read_loop`` or slash ``/read-loop``."""
        return self.log.read_loop(number)

    @mcp
    @command(name="append-log")
    @agent_tool
    def append_log(self, note: str = "", loop: int | None = None, paths: list[str] | None = None) -> str:
        """Append a correction or audit note to this session's log (slash ``/append-log``).

        **Agent steps:** name the session by its session.json in ``session`` (ask ``sessions.current`` when the user
        names none); resolve ``loop`` (argument or latest loop with entries — use ``read_loop`` to inspect); capture
        conversation id, transcript JSONL path, and line range for this turn; write a short ``note`` (what changed,
        ``paths``, cross-refs to earlier ``session.log`` lines); call MCP ``session.append_log`` with those fields.

        Omit ``loop`` to target the latest loop with log lines. Pass ``conversation_id``,
        ``transcript_path``, and ``transcript_lines`` on the call so the note points at this chat.
        Do not edit ``session.log`` by hand.

        **Session artifacts:** write large or temporary outputs (MCP ``graph_return_nodes`` JSON, diagnostics dumps,
        probe results) under the session's folder (``.sessions/{name}/``), not only under Cursor
        ``.cursor/projects/.../agent-tools``. Reference those files in ``paths`` on this call."""
        return self.log.append_note(note, loop, paths)

    @mcp
    @skill
    @agent_tool
    def write_handoff(self, content: str = "", paths: list[str] | str | None = None) -> str:
        """Write a handoff into this session's folder, .sessions/{session}/handoff-{timestamp}.md (.sessions/main/ for the main session).
        Returns the absolute path of the written file.
        paths: a file, a list of files, or a folder. Pass paths. This action reads them locally. Do not pass the handoff body in content.
        content: in-process text. Leave this empty on an MCP call."""
        document = self.document_named(content, paths)
        if not document.strip():
            return "Nothing written: draft the handoff to a file and pass its path in paths."
        return str(self.handoffs.write(document))

    @mcp
    @skill
    @agent_tool
    def read_handoff_format(self) -> str:
        """Return HANDOFF-FORMAT.md - the structure of a handoff, where to find the corrections document, and how to
        write the approach for the next agent. Read this before drafting a handoff."""
        return HANDOFF_FORMAT_FILE.read_text(encoding="utf-8")

    @mcp
    @skill
    @agent_instructions
    def handoff_session(self, next_focus: str = "") -> str:
        """Write a compact handoff for this session so the next agent can continue. Tailor it to {{next_focus}} when provided. Pass the same session argument to every session tool this calls."""
        """Step 1 - Read the handoff format once via read_handoff_format."""
        tools(self.read_handoff_format)
        """Step 2 - Draft the handoff markdown from this conversation in that format, tailored to {{next_focus}} when provided."""
        """Step 3 - Write the handoff markdown to a file and call write_handoff with paths set to that file. Do not pass the handoff body. Report the returned path to the user."""
        tools(self.write_handoff)
        return "Handoff written."

    @mcp
    @skill
    @agent_tool
    def read_cdr_format(self) -> str:
        """Return CDR-FORMAT.md - when to offer a CDR, template, numbering, and optional sections.
        Read this before offering or writing a CDR."""
        return FORMAT_FILE.read_text(encoding="utf-8")

    @mcp
    @skill
    @agent_tool
    def list_cdrs(self) -> str:
        """List CDR files under this session's workpath .context/cdr/.
        Returns newline-separated paths sorted by filename; empty string if missing or empty."""
        return "\n".join(str(path) for path in self.decision_records.paths)

    @mcp
    @skill
    @agent_tool
    def write_cdr(
        self,
        *,
        slug: str,
        content: str = "",
        paths: list[str] | str | None = None,
    ) -> str:
        """Write one Context Decision Record to this session's workpath .context/cdr/{NNNN}-{slug}.md.
        NNNN is the next sequential number under .context/cdr/. Creates the directory lazily.
        paths: a file, a list of files, or a folder. Pass paths. This action reads them locally. Do not pass the record body in content.
        content: in-process text. Leave this empty on an MCP call.
        slug: kebab-case short name (e.g. 'event-sourced-orders').
        Returns the resolved path. Call immediately when a qualifying decision crystallises - do not batch."""
        return str(self.decision_records.write(slug, self.document_named(content, paths)))

    @mcp
    @skill
    @agent_instructions
    def record_decisions_session(self) -> str:
        """Offer and write Context Decision Records (CDRs) for this session sparingly as decisions crystallise during the wrapped action - never batch; never invent decisions. Pass the same session argument to session.list_cdrs and session.write_cdr."""
        """Step 1 - Read the format once via read_cdr_format. Internalise the three-criteria gate and the minimal template."""
        tools(self.read_cdr_format)
        """Step 2 - Optionally call list_cdrs so you do not re-record an already-captured decision. Records live under the session workpath's .context/cdr/."""
        tools(self.list_cdrs)
        """Step 3 - During the session (grill, sketch, or generate), watch for decisions that meet ALL three: hard to reverse, surprising without context, and a real trade-off. If any criterion is missing, skip the CDR."""
        """Step 4 - When a qualifying decision crystallises, offer a CDR briefly (title + one-line gist). If the user accepts, write the record to a file and call write_cdr immediately with a kebab slug and paths set to that file. Do not pass the record body. Do not batch; do not wait until the end."""
        """Step 5 - Keep CDRs short. Prefer a single paragraph. Add Status / Considered Options / Consequences only when they add genuine value."""
        return "CDR session active."
