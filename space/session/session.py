"""Session — one named piece of work in a project: its folder, its workpath, its practices, its log, and its handoffs."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from harness.agent_tools import agent_instructions, agent_tool, agent_toolset, tools
from harness.agent_tools.agent_tools import noSessionLog, subAgent, tool_subject
from harness.agent_tools.tool_call import ToolCall
from harness.chat.chat import Chat
from harness.graph.explorer import ExplorerEntry, NodeSource
from harness.graph.graph import Graph
from harness.graph.pattern_overlays import PatternOverlays
from harness.installation.data_class import data_field, identity, language_adapter
from harness.installation.files import command, skill
from harness.mcp.mcp_annotations import long_call, mcp
from harness.installation.context_config import CONTEXT_FOLDER, ContextConfig
from space.repo.repo import Repo
from space.session.chat_injections import ChatInjections
from space.session.decision_records import FORMAT_FILE, DecisionRecords
from space.session.file_manager import FileEntry, FileText
from space.session.file_range import Range
from space.session.handoffs import HANDOFF_FORMAT_FILE, Handoffs
from space.session.idea_file import IdeaFile
from space.session.practice_session_output import PracticeSessionOutput
from space.session.practice_outputs import PracticeOutputs
from space.session.progress_cache import ProgressCache
from space.session.file_graphs import FileGraphs
from space.session.guidance_selection import GuidanceSelection
from space.session.guidance_version import GuidanceVersion
from space.session.session_file import RuleReads, SessionFile
from space.session.session_explorer import SessionExplorer
from space.session.session_files import SessionFiles
from space.session.session_folder import COMPLETE_FOLDER, SessionFolder
from space.session.session_hierarchy import SessionHierarchy
from space.session.session_log import SessionLog
from space.session.session_paths import SessionPaths
from space.session.session_record import SESSION_FILE, SessionRecord

if TYPE_CHECKING:
    # Named only for typing: a toolset the module holds at run time would be published again as this toolset's tools.
    from space.session.file_comments import FileComments
    from space.session.sessions import Sessions

MAIN_SESSION_NAME = "main"
_REPORT_FOLDER = "validation-reports"
_DECISION_RECORDS_FOLDER = "cdr"
_TAGS_FIELD = "tags"


class SessionNotFoundError(LookupError):
    """A tool named a session.json that is not there, such as a session closed or moved since the board read it."""

    def __init__(self, session: str) -> None:
        super().__init__(f"no session at {session!r}: name the session.json of the session to work on")
        self.session = session


class NotAPatternError(ValueError):
    """An overlay was asked for by a name that is no registered pattern."""

    def __init__(self, names: list[str], patterns: list[str]) -> None:
        self.names = names
        super().__init__(f"{', '.join(names)} is no pattern; the patterns are {', '.join(patterns)}")


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
    uses, and its title; its log, files, handoffs, decision records, and chat injections are objects of their own, made
    with it. It holds the *Sessions* that loaded it and their repository, which keep one Session for each session
    folder, so every call made in the session, from any chat, works on this one object: its graph and its one instance
    of each practice. Every tool on it acts on the session whose ``session.json`` its ``session`` argument names; a
    line a call logs points at that call's chat, which the call holds, never the session."""

    def __init__(self, sessions: Sessions) -> None:
        self._session_name = ""
        # The sessions of the checkout that loaded this one, and their repository, which holds this session's ``.sessions``.
        self._sessions = sessions
        self.repo: Repo = sessions.repo
        self.repo_path: Path = sessions.root
        # The project's ``.context/config.json``, which names the folder each practice writes in.
        self.context_config = ContextConfig(self.repo_path)
        self._workpath: Path | None = None
        self._session_path: Path | None = None
        self._make_parts()

    def _make_parts(self) -> None:
        """The parts the session holds, each made once with it: what it reads and writes is theirs to keep."""
        self.paths = SessionPaths(self)
        self.record = SessionRecord(self)
        self.folder = SessionFolder(self)
        self.hierarchy = SessionHierarchy(self)
        self.file_graphs = FileGraphs(self)
        self.guidance_version = GuidanceVersion(self)
        self.decision_records = DecisionRecords(self.work_root / CONTEXT_FOLDER / _DECISION_RECORDS_FOLDER)
        self.handoffs: Handoffs | None = None
        # What a board read costs most to work out for each of its fidelities, kept in its folder between reads.
        self.progress_cache = ProgressCache(None)
        self.log = SessionLog(self)
        self.session_files = SessionFiles(self)
        self.chat_injections = ChatInjections(self)
        # The practices and graph this session keeps between calls, made when first asked for.
        self.practice_outputs = PracticeOutputs(self)
        self.explorer = SessionExplorer(self)

    @classmethod
    @tool_subject
    def from_file(cls, session: str, *, call: ToolCall) -> Session:
        """The session whose session.json is session, a path from the call's project or an absolute one, read without
        opening it, from the sessions this process holds for that project. A board command names its ticket's session
        this way, because it runs in whichever chat it is sent to, and that chat's open session can be another. A tool
        is handed the call it answers."""
        return call.session_named(session)

    @property
    @data_field
    def name(self) -> str:
        """Named work session (not the toolset slug)."""
        return self._session_name

    @name.setter
    def name(self, value: str) -> None:
        self._session_name = (value or "").strip()

    @property
    def sessions(self) -> Sessions:
        """The sessions of this session's checkout, which loaded it."""
        return self._sessions

    @property
    def workpath(self) -> Path | None:
        """The folder the session works in; none for the whole repository."""
        return self._workpath

    @workpath.setter
    def workpath(self, folder: Path | None) -> None:
        """Work in folder from now on. The practices and graph this session keeps were made on its old root, so they
        are made again on the new one when next asked for."""
        self._workpath = folder
        self.decision_records = DecisionRecords(self.work_root / CONTEXT_FOLDER / _DECISION_RECORDS_FOLDER)
        self.practice_outputs.forget()

    @property
    def session_path(self) -> Path | None:
        """The session's folder, such as ``.sessions/alpha``; none for a session not yet kept in one."""
        return self._session_path

    @session_path.setter
    def session_path(self, folder: Path | None) -> None:
        self._session_path = folder
        self.record.kept_in(folder)
        self.handoffs = Handoffs(folder) if folder is not None else None
        self.progress_cache = ProgressCache(folder)

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
        return self.paths.from_project(self.session_file)

    @property
    def work_root(self) -> Path:
        """The folder the session works in: its workpath, or the whole repository when it chose none. Actions write
        their sketches, grill answers, and partitions under it, each practice's folder is kept relative to it, and the
        file manager reads under it."""
        return self.paths.resolved(Path(self.workpath or self.repo_path))

    @property
    def graph(self) -> Graph:
        """The knowledge graph this session works with, opened on its root, holding the session's one instance of each
        practice, made once on its root, so every call in the session works on the same graph and the same practices
        and none rebuilds them; an action that writes files refreshes the graph with exactly those files. It reads back
        the graph saved on its root, so a session opened again, such as a ticket just activated, shows what was loaded
        in it before. A session whose root has moved gets a new graph, with new practices, on the new root. It holds only
        the practices the session works on, so turning one on or off makes it again with those."""
        return self.practice_outputs.graph

    @property
    @data_field
    def title(self) -> str:
        """The title a person gave the session's ticket; empty when it has none."""
        return self.record.fields.get("title", "")

    @property
    @data_field
    def repo_name(self) -> str:
        """The repository the session works in, by its folder's name, as a page heads it."""
        return self.repo.root.name

    @property
    @data_field
    def branch(self) -> str:
        """The branch the session works on, as its session.json names it, else the session's own name."""
        return self.record.fields.get("branch") or self.name

    @property
    @data_field
    def root(self) -> str:
        """The whole path of the folder the session works in, as a page heads it."""
        return str(self.work_root)

    @property
    @data_field
    def scope(self) -> str:
        """feature, story, or slice; empty when no one said."""
        return self.record.fields.get("scope", "")

    @property
    @data_field
    def parent(self) -> str:
        """The name of the session this one was split from; empty when it was not split from one."""
        return self.hierarchy.parent

    @property
    def tags(self) -> list[str]:
        """The words a person tagged this session with, in the order they were added."""
        return list(self.record.fields.get(_TAGS_FIELD, []))

    def add_tag(self, word: str) -> None:
        """Tag this session with word, once however often it is added."""
        tags = self.tags
        if word not in tags:
            self.record.save_fields(**{_TAGS_FIELD: [*tags, word]})

    @property
    def idea_file(self) -> IdeaFile:
        """``<name>.md`` in this session's folder: what its work is about, the backlog item's file when it was started from one."""
        return IdeaFile(self.session_path / f"{self.name}.md")

    @property
    def text(self) -> str:
        """The text of its idea file; empty while it has none."""
        return self.idea_file.text

    @property
    def stories(self) -> list[str]:
        """The stories its idea file names: this session's increment, which generate and validate work on."""
        return self.idea_file.stories

    def keep_text(self, text: str) -> None:
        """Write text under its idea file's heading, making the file, headed with its title, when it has none."""
        idea = self.idea_file
        idea.write(idea.heading or self.title or self.name, text)
        self.record.saved("text")

    @property
    def overlays(self) -> list[str]:
        """The patterns this session overlays on its graph, by name, as its session.json keeps them; none until a
        person chooses some."""
        return list(self.record.fields.get("overlays", []))

    def choose_overlays(self, overlays: list[str]) -> None:
        """Overlay the patterns named on this session's graph from now on, in place of those chosen before: kept in its
        session.json, and applied to its graph at once when it has one. A name that is no registered pattern is refused
        with NotAPatternError, and nothing changes."""
        patterns = PatternOverlays().names
        unknown = [name for name in overlays if name not in patterns]
        if unknown:
            raise NotAPatternError(unknown, patterns)
        self.record.save_fields(overlays=list(overlays))
        self.practice_outputs.overlay(overlays)

    @property
    def answer(self) -> int | None:
        """The answer this session's sessions are giving, which what it reads from its files is held for; none when
        they serve no answer, and it reads them on every ask."""
        return self._sessions.answers.current

    @property
    @data_field(key="workpath")
    def workpath_from_checkout(self) -> str:
        """The folder the session works in, as its session.json saves it and the board shows it: from its checkout's
        top, so a ticket working in its own worktree shows the folder it chose there, and it can never name a folder in
        another checkout of the repository; empty for the whole checkout, and absolute when it lies outside it."""
        root = self.work_root
        checkout = self.paths.resolved(self.repo_path)
        if not root.is_relative_to(checkout):
            return root.as_posix()
        relative = root.relative_to(checkout).as_posix()
        return "" if relative == "." else relative

    @property
    def reports_folder(self) -> Path:
        """Where Validate saves its reports in this session, each with the graph it checked beside it."""
        return self.session_path / _REPORT_FOLDER

    def practice(self, name: str) -> PracticeSessionOutput:
        """The practice called name in this session, on or off for it: the session's one instance of it, so a practice
        turned off can be turned on again. One the session works on is opened in its graph first."""
        found = self.practices.get(name) or self.practice_outputs.every.get(name)
        if found is None:
            raise UnknownPracticeError(name)
        return found

    @property
    def practices(self) -> dict[str, PracticeSessionOutput]:
        """The practices the session works on, by practice key, each the session's one instance of it: the ones its
        graph holds, kept between calls with the graph, which opening here gives each practice to work in. A practice
        turned off for the session is in ``own_practices`` and ``practice(name)``, not here."""
        outputs = self.practice_outputs.every
        return {key: outputs[key] for key in self.graph.practices.held}

    @property
    @data_field(key="practices")
    def own_practices(self) -> dict[str, PracticeSessionOutput]:
        """The same practices, without opening the graph, for reading what each one declares, its folder and fidelities:
        a board listing every session would otherwise read every session's saved graph. A practice that runs is reached
        through ``practices``, so it works in the graph."""
        return dict(self.practice_outputs.every)

    @property
    @data_field(key="handoff")
    def latest_handoff(self) -> str:
        """The newest handoff file, as a path from the project; empty before one is written."""
        latest = self.handoffs.latest
        return self.paths.from_project(latest) if latest is not None else ""

    @mcp
    @command(name="close-session")
    @agent_tool
    def close(self) -> None:
        """Close this work session: when it is the open session of its project, main becomes the open one.

        ``session`` is the session's session.json; ask ``sessions.current`` for it when the user names no session."""
        self.sessions.opened.close(self)

    @mcp
    @agent_tool
    @noSessionLog
    def choose_workpath(self, path: str = "") -> Session:
        """Make path, a folder in the repository, this session's workpath: the folder its practices write under and its graph loads from. An empty path is the whole repository."""
        # A practice root a person chose is kept relative to the workpath, so each is saved again against the new one
        # and still names the same folder.
        # The practices on the new workpath are kept again with it, so each root is kept by the practice that works there.
        chosen = {key: practice.folder for key, practice in self.practices.items() if practice.is_root_chosen}
        self.workpath = self._sessions.roots.in_checkout(self.repo_path, self.repo_path / path)
        self.record.save()
        moved = self.practices
        for key, root in chosen.items():
            moved[key].keep_root(root)
        return self

    @mcp
    @agent_tool
    @noSessionLog
    def show(self) -> Session:
        """This session as it stands, changing nothing: its title, workpath, and each practice with whether it is on and its colour."""
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
    def workpath_files(self) -> list[FileEntry]:
        """List every file directly in the folder this session works in, each with its path from the project, as the board's details open it from the workpath."""
        return self.session_files.in_workpath()

    @mcp
    @agent_tool
    @noSessionLog
    def read_file(self, path: str = "") -> FileText:
        """Return the text of path, a file in this repository or under a folder this session's practices write to, such as its ticket's worktree; no text when the file is gone, such as one deleted since the board listed it."""
        return self.session_files.read(path)

    @mcp
    @agent_tool
    @noSessionLog
    def write_file(self, path: str, text: str) -> FileText:
        """Save text as the whole of path, a file in this repository or under a folder this session's practices write to, named as read_file names it; the file as saved."""
        return self.session_files.write(path, text)

    @mcp
    @agent_tool
    @noSessionLog
    def guidance_selection(self) -> GuidanceSelection:
        """Return the session's guidance selection: each stage and practice selected or not, the formats the selected stages' fidelities of the selected practices offer, each selected or not, those fidelities by slug, and the version every change raises. The chat bar's stage buttons, practice dots and format chips and the Files app's toggles all show it."""
        return GuidanceSelection(self)

    @mcp
    @agent_tool
    @noSessionLog
    def update_guidance_selection(self, stages: list[str] | None = None, practices: list[str] | None = None, formats: list[str] | None = None) -> GuidanceSelection:
        """Select exactly these stages (such as discovery), practices (such as stories), and format groups (such as markdown), each list in place of what was selected, a list left out unchanged; save it in session.json, raise the version once, and return the selection. A practice selected is one the session works on; a format group selected is chosen for every selected fidelity offering it."""
        self.guidance_version.select(stages, practices, formats)
        return GuidanceSelection(self)

    @long_call
    @mcp
    @agent_tool
    @noSessionLog
    def guidance_selection_after(self, version: int) -> GuidanceSelection:
        """Return the session's guidance selection once its version is past version: at once when it already is, else as soon as a change raises it, else after GUIDANCE_WAIT_SECONDS with it unchanged. A page holds one such call open, so a selection made anywhere reaches it in a fraction of a second."""
        self.guidance_version.wait_past(version)
        return GuidanceSelection(self)

    @long_call
    @mcp
    @agent_tool
    @noSessionLog
    def file(self, path: str, rules: bool = False, cross_file: bool = False) -> SessionFile:
        """Return path, a file named as read_file names it, as the viewer shows it: its text and language, the comments on it, and with either of rules or cross_file the folds of its classes, operations, and properties. With rules, the rules it breaks read on its own, under a second; with cross_file, the rules only the whole working copy finds broken in it, linking files and practices, which takes far longer. Each on its range of lines. Both off, browsing never reads a graph."""
        return SessionFile(self, path, RuleReads(rules, cross_file))

    @long_call
    @mcp
    @agent_tool
    @noSessionLog
    def graph_trees(self, paths: list[str], call: ToolCall | None = None) -> list[ExplorerEntry]:
        """Return the practice trees of this session's graph read from exactly the files at paths, each named from the project as the Files app lists them, and holding only the nodes read from them: each practice's root with the entries below it, closed, as graph.explorer_trees answers them. The files the page lists are the one filter: the graph reads them, its story tests in code and in markdown alike, and keeps what they hold. No paths, or none in the project, answer no tree."""
        return self.explorer.trees(paths, call)

    @mcp
    @agent_tool
    @noSessionLog
    def graph_branch(self, node_id: str, paths: list[str]) -> ExplorerEntry | None:
        """Return the node node_id's entry in this session's graph, kept to the nodes read from the files at paths as graph_trees keeps them, with the entries below it, closed; None for an id the graph no longer holds."""
        return self.explorer.branch(node_id, paths)

    @mcp
    @agent_tool
    @noSessionLog
    def graph_node_ranges(self, node_id: str, paths: list[str]) -> list[Range]:
        """Return the lines the node node_id covers, one range for each file, each named from the project, so a viewer opens every file there. A node read from lines of a file answers that one range; a node read from no file's lines, such as a module that is a folder, answers each file the nodes below it come from, among paths, spanning the lines they cover; none for an id the graph no longer holds."""
        return self.explorer.node_ranges(node_id, paths)

    @mcp
    @agent_tool
    @noSessionLog
    def graph_members(self) -> list[NodeSource]:
        """Return every class, operation, and property this session's graph holds, each with its text and the class it belongs to, so a viewer opens a call in place even when it reaches another file. Read after graph_trees, which reads the files the page lists."""
        return self.explorer.members()

    @mcp
    @agent_tool
    @noSessionLog
    def add_to_chat_context(self, chat: str, path: str, start_line: int = 0, end_line: int = 0) -> Chat:
        """Add path, a file named from the project, or its lines start_line to end_line, to the context of chat, a chat's id: a fill in its prompt box that goes with the person's next prompt, as Claude's own file viewer adds a file. The whole file goes as an @ mention of its path; lines go as the path and range with each line quoted. A chat that is not connected refuses it."""
        text = self.file(path).range(start_line, end_line).context if start_line else f"@{path} "
        added_to = Chat.load(chat)
        added_to.mailbox.queue("fill", text)
        return added_to

    @property
    def file_comments(self) -> FileComments:
        """The comments a person wrote on this session's files, kept in its folder."""
        from space.session.file_comments import FileComments

        return FileComments(self)

    @mcp
    @command(name="mark-loop")
    @agent_tool
    def mark_loop(self, call: ToolCall) -> str:
        """Mark the next loop in this session's log (slash ``/mark-loop``); returns its number.

        ``session`` is the session's session.json; ask ``sessions.current`` for it when the user names no session.
        Pass ``conversation_id``, ``transcript_path``, and ``transcript_lines`` (cumulative JSONL range for this chat)
        on the call; the ``--- N`` marker carries that chat's pointer."""
        return str(self.log.by(call.request.chat).next_loop().number)

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
    def append_log(self, call: ToolCall, note: str = "", loop: int | None = None, paths: list[str] | None = None) -> str:
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
        return self.log.by(call.request.chat).append_note(note, loop, paths)

    @mcp
    @skill
    @agent_tool
    def write_handoff(self, content: str = "", paths: list[str] | str | None = None) -> str:
        """Write a handoff into this session's folder, .sessions/{session}/handoff-{timestamp}.md (.sessions/main/ for the main session).
        Returns the absolute path of the written file.
        paths: a file, a list of files, or a folder. Pass paths. This action reads them locally. Do not pass the handoff body in content.
        content: in-process text. Leave this empty on an MCP call."""
        document = self.paths.document_named(content, paths)
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

    @subAgent
    @mcp
    @skill
    @agent_instructions
    def handoff_session(self, next_focus: str = "") -> str:
        """Write a compact handoff for this session so the next agent can continue, then commit and push it. Tailor it to {{next_focus}} when provided. Pass the same session argument to every session tool this calls. The caller hands the sub-agent the conversation's outcome, open work, corrections and decisions in the prompt, since the sub-agent cannot read this chat."""
        """Step 1 - Read the handoff format once via read_handoff_format."""
        tools(self.read_handoff_format)
        """Step 2 - Draft the handoff markdown from what the caller passed in that format, tailored to {{next_focus}} when provided."""
        """Step 3 - Write the handoff markdown to a file and call write_handoff with paths set to that file. Do not pass the handoff body."""
        tools(self.write_handoff)
        """Step 4 - Commit and push the handoff on the current branch with repo.push_commit (message: "Handoff: {session}"). Report the handoff path and the pushed commit."""
        return "Handoff written, committed and pushed."

    @mcp
    @skill
    @agent_instructions
    def debug_session(self, choice: str = "", details: str = "") -> str:
        """Debug what went wrong in this session: capture as much context as can be found, ask the person for more, then fix the bug or request help. The chat bar's debug button starts this with no choice; its Fix buttons start it with {{choice}} set to fix and {{details}} naming the failure. Pass the same session argument to every session tool this calls."""
        """Step 1 - Capture the context. Gather, as fully as can be found: {{details}} when given; every failure and stack trace this chat met (tool errors, tracebacks, failed commands with their output), quoted whole; the failures the CDD chat bar shows; the latest lines of this session's session.log; server-health.report; the diagnostics.json of the install folder; the session's name, branch, and git status; cdd-version.read; and the operating system. Say what could not be read rather than leaving it out."""
        """Step 2 - Write it as markdown with session.write_file to debug/debug-{time}.md in this session's folder (time as YYYYMMDDTHHMMSS): a one-line summary first, then each part under its own heading, stack traces in fences. Tell the person its path."""
        """Step 3 - Unless {{choice}} is fix or help, ask the person with AskUserQuestion, one question: what to do, with the options "Fix the bug" (a sub-agent fixes it and takes the fix to main) and "Request help" (an email to the CDD maintainer). Its notes and Other take more detail: add what the person writes to the report with session.write_file before going on."""
        """Step 4 - Request help: draft an email to the CDD maintainer for the person to send; never send it yourself. Build a mailto:jeff.anderson@abdworks.com link, subject "CDD debug: " and the summary, body the summary, the person's details, the report's path, and the first stack trace, URL-encoded and kept under 1800 characters, and open it with the system's opener: `start "" "<link>"` on Windows, `open "<link>"` on a Mac, `xdg-open "<link>"` elsewhere. Ask the person to attach the report and send it."""
        """Step 5 - Fix the bug: start a background sub-agent with the Agent tool and run_in_background, so this chat stays free, and tell the person it is running. Hand it the report's path and these steps: (a) Find the CDD repository: this project when it is the CDD checkout, else the clone at the origin of `git -C ~/.cdd/runtime remote get-url origin`; work on a new branch in a worktree of it. (b) Fix the cause with the diagnose action's discipline: a failing spec first, then the fix, then the unit tier. (c) Take it to main: when `gh api repos/<owner>/<repo> --jq .permissions.push` answers true, merge to main and push (repo.push_to_main in the CDD checkout); otherwise, or when gh is missing or not signed in, fork with `gh repo fork --remote`, push the branch, and open a pull request with `gh pr create --repo <owner>/<repo>`, its body the report's summary and what was changed. (d) Report the cause, the change, and the commit pushed or the pull request's link."""
        """Step 6 - When the sub-agent reports, pass its result on to the person: the cause, the change, and where it went."""
        return "Debug report written; fix or help request under way."

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
        return str(self.decision_records.write(slug, self.paths.document_named(content, paths)))

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
