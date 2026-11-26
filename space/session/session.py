"""Session — one named piece of work in a project: its folder, its workpath, its practices, its log, and its handoffs."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from harness.agent_tools import agent_instructions, agent_tool, agent_toolset, tools
from harness.agent_tools.agent_tools import noSessionLog, subAgent, tool_subject
from harness.agent_tools.tool_call import ToolCall
from harness.annotations.annotation import hosted_only
from harness.chat.chat import Chat
from harness.graph.graph import Graph
from harness.graph.pattern_overlays import PatternOverlays
from harness.installation.data_class import data_field, identity, language_adapter
from harness.installation.files import command, skill
from harness.mcp.mcp_annotations import long_call, mcp
from harness.installation.context_config import CONTEXT_FOLDER, ContextConfig
from space.repo.repo import Repo
from space.session.chat_injections import ChatInjections
from space.session.decision_records import FORMAT_FILE, DecisionRecords
from space.session.files.file_manager import FileEntry, FileText
from space.session.files.file_view_filter import FileViewFilter
from space.session.files.session_explorer import SessionExplorer
from space.session.files.session_file import RuleReads, SessionFile
from space.session.files.session_files import SessionFiles
from space.session.handoffs import HANDOFF_FORMAT_FILE, Handoffs
from space.session.idea_file import IdeaFile
from space.session.practices.guidance_selection import GuidanceSelection, SelectionPart
from space.session.practices.practice_session_output import PracticeSessionOutput
from space.session.practices.session_practices import SessionPractices
from space.session.session_checkout import SessionCheckout
from space.session.session_folder import SessionFolder
from space.session.session_graph import SessionGraph
from space.session.session_hierarchy import SessionHierarchy
from space.session.session_log import SessionLog
from space.session.session_paths import SessionPaths
from space.session.session_record import SESSION_FILE, SessionFields, SessionRecord
from space.session.test_tiers import TestTiers
from space.session.validation.accepted_violations import ACCEPTED_VIOLATIONS_FILE, AcceptedViolations
from space.session.validation.changed_artifact import ChangedArtifact
from space.work_state import COMPLETE_FOLDER, SESSIONS_FOLDER

if TYPE_CHECKING:
    # Named only for typing: a toolset the module holds at run time would be published again as this toolset's tools.
    from space.session.files.file_comments import FileComments
    from space.session.sessions import Sessions

MAIN_SESSION_NAME = "main"
_REPORT_FOLDER = "validation-reports"
_DECISION_RECORDS_FOLDER = "cdr"


class SessionNotFoundError(LookupError):
    """A tool named a session.json that is not there, such as a session closed or moved since the board read it."""

    def __init__(self, session: str) -> None:
        super().__init__(f"no session at {session!r}: name the session.json of the session to work on")
        self.session = session


class MainStaysOpenError(ValueError):
    """Raised when a tool would close main, the default session, which stays open on the board, or a board tool would
    archive, delete, or shelve it, or edit its text or tags, which the board keeps for no ticket's work. It names what
    was asked of main."""

    def __init__(self, action: str) -> None:
        self.action = action
        super().__init__(f"main is the default session and stays open; it cannot {action}")


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


@hosted_only
class SessionFileTools:
    """The tools that list, read, and write a session's files, and put a file into a chat's context: each asks the
    session's *SessionFiles*, the part that owns its files."""

    session_files: SessionFiles

    @mcp
    @agent_tool
    @noSessionLog
    def folder_files(self) -> list[FileEntry]:
        """List every file in this session's record folder and work folder, each with its path from the project: its session.json, log, handoffs, kept notes, and validation reports; each listed, and the session's own work when the branch changed it."""
        listing = self.guidance.listing([])
        return [listing.of_folder(entry) for entry in self.session_files.in_folder()]

    @mcp
    @agent_tool
    @noSessionLog
    def workpath_files(self) -> list[FileEntry]:
        """List every file directly in the folder this session works in, each with its path from the project, as the board's details open it from the workpath; each listed, and the session's own work when the branch changed it."""
        listing = self.guidance.listing([])
        return [listing.of_folder(entry) for entry in self.session_files.in_workpath()]

    @mcp
    @agent_tool
    @noSessionLog
    def read_file(self, path: str = "") -> FileText:
        """Return the text of path, a file in this repository or under a folder this session's practices write to, such as its ticket's worktree, with its version, which write_file takes back; no text and no version when the file is gone, such as one deleted since the board listed it. A path inside a .git folder is refused."""
        return self.session_files.read(path)

    @mcp
    @agent_tool
    @noSessionLog
    def write_file(self, path: str, text: str, version: str = "") -> FileText:
        """Save text as the whole of path, a file in this repository or under a folder this session's practices write to, named as read_file names it; the file as saved, with its new version. version is the one read_file, or the last write_file of the file, answered; none for a file not there yet. A file changed on disk since that read is refused and left as it is: read it again and write from what it holds. A path inside a .git folder is refused."""
        return self.session_files.write(path, text, version)

    @mcp
    @agent_tool
    def delete_file(self, path: str) -> str:
        """Delete path, a file, or a folder with every file in it, named from the project or absolute, as the Files app's file menu asks once the person confirmed; answer the path deleted, from the project. Only what lies under the session's roots is deleted: a path outside them is refused (PathOutsideRootsError), as is a root itself (RootDeleteRefused), a path not there (NamedPathNotFoundError), the session's own session.json or a folder holding it (SessionRecordWriteRefused), and a path inside a .git folder (VersionControlPathRefused). Nothing is kept to undo it."""
        return self.session_files.delete(path)

    @long_call
    @mcp
    @agent_tool
    @noSessionLog
    def check_changed_artifact(self, path: str) -> ChangedArtifact:
        """Run the graph rules on path, a file just edited or a file or folder the Files app's file menu validates, named as read_file names it, with no explicit validate: Validate runs on that path alone for each fidelity the session's guidance selection shows, of a practice the session works on, that declares it (for a folder, any file in it), saving a report and logging its validate line, so the chat bar's violation count follows the edit. Returns the file and the slug of each fidelity checked; none for a file no such fidelity declares, or one outside the session's roots. The chat bar calls it after each edit the agent makes."""
        return ChangedArtifact(self, path).check()

    @long_call
    @mcp
    @agent_tool
    @noSessionLog
    def file(self, path: str, rules: bool = False, cross_file: bool = False, folds: bool = False, paths: list[str] | None = None, node_filter: dict | None = None) -> SessionFile:
        """Return path, a file named as read_file names it, as the viewer shows it, refused when the file is not there, such as one deleted or moved since a page listed it, or is longer than the viewer shows: its text and language, the comments on it, and with any of folds, rules or cross_file the folds of its classes, operations, and properties. With folds alone, the folds and no broken rule. With rules, the rules it breaks read on its own, under a second; with cross_file, the rules only the whole working copy finds broken in it, linking files and practices, which takes far longer. Each on its range of lines. All off, browsing never reads a graph. paths and node_filter are the file view's filters, as graph_trees takes them: the files the page lists for the stages, practices and formats chosen, and the graph view's node filter (practices, types, relationships). They decide which callouts the answer holds, by the graph's own filter: a link into a file of a stage, practice or format turned off is left out, a file no fidelity declares always shows, and what a step invokes or observes is left out while the node filter leaves out that connector or the node type it reaches. Neither sent, the answer holds every callout."""
        return SessionFile(self, path, RuleReads(rules, cross_file, folds), FileViewFilter(self, paths, node_filter))

    @mcp
    @agent_tool
    @noSessionLog
    def add_to_chat_context(self, chat: str, path: str, start_line: int = 0, end_line: int = 0) -> Chat:
        """Add path, a file named from the project, or its lines start_line to end_line, to the context of chat, a chat's id: a fill in its prompt box that goes with the person's next prompt, as Claude's own file viewer adds a file. The whole file goes as an @ mention of its path; lines go as the path and range with each line quoted. A chat that is not connected refuses it."""
        text = self.file(path).range(start_line, end_line).context if start_line else f"@{path} "
        added_to = Chat.load(chat)
        added_to.mailbox.queue("fill", text)
        return added_to


@hosted_only
class SessionGuidanceTools:
    """The tools that read and change a session's guidance selection, which the session holds (*GuidanceSelection*)."""

    guidance: GuidanceSelection

    @mcp
    @agent_tool
    @noSessionLog
    def guidance_selection(self) -> GuidanceSelection:
        """Return the session's guidance selection: each stage and practice selected or not, the formats the selected stages' fidelities of the selected practices offer, each selected or not, those fidelities by slug, and the version every change raises. The chat bar's stage buttons, practice dots and format chips and the Files app's toggles all show it."""
        return self.guidance

    @mcp
    @agent_tool
    @noSessionLog
    def toggle_guidance(self, part: SelectionPart, name: str) -> GuidanceSelection:
        """Select the stage (such as discovery), practice (such as stories), or format group (such as markdown) called name beside those selected, or no longer, as a press on the chat bar or the Files app asks; part is stage, practice, or format. Save it in session.json, raise the version once, and return the selection. Before anyone chose stages, a stage toggles beside the one the session's ticket stands in. A practice selected is one the session works on; a format group selected is chosen for every selected fidelity offering it."""
        return self.guidance.toggle(part, name)

    @mcp
    @skill
    @agent_instructions
    def set_up_roots(self, ticket: str = "") -> str:
        """Set up this session's roots so they cover exactly the pieces its ticket {{ticket}} works on, in every practice the session has on: for each practice and fidelity, the narrowest folders that hold those pieces (an aggregate's folder, the package that implements it, the sub-epics whose stories cover it), and no folder beside them. Run it when a session is created, switched to with roots nobody set, or found to miss files it works on. Pass the same session argument to every session tool this calls."""
        """Step 1 - Read what the ticket works on: its text (session.show, and the title and description its session.json keeps), the story map nodes it names (epics, sub-epics, stories), and the domain names it uses (bounded contexts, aggregates, modules, screens). Write them down as the names to look for."""
        """Step 2 - Read what the branch changed: `git diff --name-only <default branch>...HEAD` plus the uncommitted files in the session's worktree. Each changed file is evidence of a piece the ticket works on."""
        """Step 3 - For each practice the session has on (session.guidance_selection), and each of its fidelities, read where it writes: the `outputs` each fidelity declares in the practice's guidance (its `{practice}.md`), such as a path through a context and an aggregate, a folder per module, or a path through an epic and a sub-epic. Practices keep their pieces in different areas of the project, so look in every area each one declares, not only beside the others."""
        """Step 4 - Ask each fidelity for the folders it proposes: fidelity-session-output.propose_roots with the names from Step 1. It answers the narrowest folder holding each piece the branch changed and each piece a name names, as its declared outputs place them."""
        """Step 5 - Dig further where the proposals miss or overreach. Scan each declared location across the project (Glob, Grep) for the names from Step 1: the domain folder of each aggregate, the module and package that implement it, the epic and sub-epic folders whose stories cover it, its screens and its specs. Go down to the narrowest folder that holds the piece; never propose a parent that also holds siblings the ticket does not touch."""
        """Step 6 - Propose the roots to the person: a short table of practice, fidelity, and folders, each with its evidence (the name it matches, or the changed file it holds), and the folders left out on purpose. Ask the person to confirm or correct it; set nothing before they answer."""
        """Step 7 - Set what the person confirmed: practice-session-output.choose_root for a practice's own root (where its documents go when no fidelity keeps its own); fidelity-session-output.choose_root for a fidelity's first folder, and fidelity-session-output.add_root for each further folder beside it. Leave a default root that already holds the pieces."""
        """Step 8 - Check: session.show and ticket.root_files list the files under the new roots; every file Step 2 found that a practice writes must be among them. Whenever a later step finds another piece of the ticket outside the roots, such as a story test in another sub-epic, add its folder with fidelity-session-output.add_root, telling the person."""
        return "Session roots set up and confirmed."

    @long_call
    @mcp
    @agent_tool
    @noSessionLog
    def guidance_selection_after(self, version: int) -> GuidanceSelection:
        """Return the session's guidance selection once its version is past version: at once when it already is, else as soon as a change raises it, else after GUIDANCE_WAIT_SECONDS with it unchanged. A page holds one such call open, so a selection made anywhere reaches it in a fraction of a second."""
        self.guidance.wait_past(version)
        return self.guidance


@hosted_only
class SessionTestTierTools:
    """The tool that records a test tier a module uses, which the session holds (*TestTiers*)."""

    test_tiers: TestTiers

    @mcp
    @agent_tool
    def record_test_tier(self, module: str, tier: str, tool: str) -> dict[str, dict[str, str]]:
        """Record in session.json that the tests of module use tier, written with the test tool named, beside the tiers the module already holds, and return the module's tiers. module: the module's folder, named from the project's root, such as space/kanban. tier: unit, which every module uses; server, for a module that publishes operations through the cdd server or another server; or web, for a module that shows a page. tool: the test tool of that tier, such as mamba, vitest, or playwright. A generate or a render that writes tests records the tiers it can tell; call this for a tier it asks you to decide. A story of a module whose record names the server or web tier needs a test at that tier. Another tier, or an empty tool, is refused and nothing is recorded."""
        tiers = self.test_tiers.record(module, {tier: tool})
        return {self.test_tiers.path_of(module): tiers}


@hosted_only
class SessionLogTools:
    """The tools that mark and read a session's log loops, add notes to it, and hand its work on: each asks the
    session's *SessionLog* or its *Handoffs*."""

    log: SessionLog
    paths: SessionPaths
    handoffs: Handoffs | None

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
        probe results) under the session's work folder (``.sessions/{name}/``, in its ticket's worktree when it has one),
        not only under Cursor
        ``.cursor/projects/.../agent-tools``. Reference those files in ``paths`` on this call."""
        return self.log.by(call.request.chat).append_note(note, loop, paths)

    @mcp
    @skill
    @agent_tool
    def write_handoff(self, content: str = "", paths: list[str] | str | None = None) -> str:
        """Write a handoff into this session's work folder, .sessions/{session}/handoff-{timestamp}.md in its ticket's worktree when it has one, else in the main checkout (.sessions/main/ for the main session).
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
        """Debug what went wrong in this session: capture as much context as can be found, always log it as a defect on GitHub, then fix it or leave it logged for a person or an agent to fix. The chat bar's debug button starts this with no choice; its Fix buttons start it with {{choice}} set to fix and {{details}} naming the failure. Pass the same session argument to every session tool this calls."""
        """Step 1 - Capture the context. Gather, as fully as can be found: {{details}} when given; every failure and stack trace this chat met (tool errors, tracebacks, failed commands with their output), quoted whole; the failures the CDD chat bar shows; the latest lines of this session's session.log; server-health.report; the diagnostics.json of the install folder; the session's name, branch, and git status; cdd-version.read; and the operating system. Say what could not be read rather than leaving it out."""
        """Step 2 - Write it as markdown with session.write_file to debug/debug-{time}.md in this session's work folder (time as YYYYMMDDTHHMMSS): a one-line summary first, then each part under its own heading, stack traces in fences. End it with "Suggested fix", where the cause most likely lies and what change would mend it, and "Status: raised". Tell the person its path."""
        """Step 3 - Always log the defect, whatever happens next, so it is never lost: open an issue on the CDD repository on GitHub with `gh issue create --repo <owner>/<repo>`, the repository read from `git -C ~/.cdd/runtime remote get-url origin`, its title "CDD defect: " and the summary, its body the summary, {{details}}, the steps that led to it, the first stack trace in a fence, the suggested fix, "Status: raised", and the report's path, written so a person or an agent can fix it from the issue alone. Tell the person the issue's link. When gh cannot create it, say why and how to fix gh (gh auth login), and keep the report as the log."""
        """Step 4 - Unless {{choice}} is fix, log, later, or fix on a named branch, ask the person with AskUserQuestion, one question: what to do, with the options "Fix the bug" (a sub-agent fixes it on this branch and serves it on the dev lane; on main, it pushes to main and serves it on the stable lane; with no permission to push, it opens a pull request; it links the fix in the issue), "Fix on another branch" (the fix goes to the chat that works that branch, such as a release branch's chat, on its prompt queue; the person names the branch in Other or its notes), "Log a defect" (the issue stays open, raised, for a person or an agent to fix), and "Fix later" (the issue stays open with the status to come later). Its notes and Other take more detail: add what the person writes to the report with session.write_file and to the issue with `gh issue comment` before going on."""
        """Step 5 - Log a defect: the issue is the log, its status raised; tell the person its link and stop. Fix later: set the status to come later in the report with session.write_file and in the issue with `gh issue comment` ("Status: to come later"); tell the person its link and stop."""
        """Step 5b - Fix on another branch: find the chat that works that branch with chats.list (its worktree's branch), and put the fix on its prompt queue with prompt-queue.add, chat set to that chat: the report's path, the issue's link, the suggested fix, and Step 6's steps (b) to (f) to follow in its own worktree on its own branch, ending with "Status: resolved" in the report and the issue and `gh issue close`. Comment on the issue that the fix is queued on that branch, its status still raised. When no chat works that branch, say so and treat it as Fix the bug in that branch's worktree. Tell the person where it was queued and stop."""
        """Step 6 - Fix the bug: start a background sub-agent with the Agent tool and run_in_background, so this chat stays free, and tell the person it is running. Hand it the report's path, the issue's link, and these steps: (a) Find where to work: when this project is the CDD checkout and the chat works in a ticket's worktree (any branch but main), work in that worktree on that branch; when it is the CDD checkout's main, work in the main checkout on main; else CDD is installed in another project, so work on a new branch in a worktree of the clone at the origin of `git -C ~/.cdd/runtime remote get-url origin`. (b) Fix the cause with the diagnose action's discipline: a failing spec first, then the fix, then the unit tier. (c) Check whether the person may push to the CDD repository: `gh repo view <owner>/<repo> --json viewerPermission` answers WRITE, MAINTAIN or ADMIN. (d) With permission, send it where it goes live. On a ticket's branch: commit and push to that branch with repo.push_commit, then repin the dev lane with `python scripts/install.py --ide Claude --pin-runtime` from the worktree, and run `app.open` for each app the fix changed (Files, Kanban, Story UI) so it rebuilds on the dev lane; never merge it to main unless the person asked for that in their own words. On main: commit and push to main with repo.push_commit, message the chats that use the stable lane, then repin the stable lane with the same command from the main checkout. (e) With no permission to push, or with CDD installed in another project: never push to its main; fork with `gh repo fork --remote`, push the branch, and open a pull request with `gh pr create --repo <owner>/<repo>`, its body the report's summary, what was changed, and "Fixes #<issue>". (f) Link the fix in the issue with `gh issue comment`: the commit pushed and the lane it was served on, or the pull request's link. Once pushed and served, set the status to resolved: "Status: resolved" in the report with session.write_file and in the comment, then `gh issue close`; a pull request leaves it raised until merged, and a fix that could not be finished leaves it raised with what is left. (g) Report the cause, the change, where it went, and the status."""
        """Step 7 - When the sub-agent reports, pass its result on to the person: the cause, the change, where it went, the status (raised, resolved, or to come later), and the issue's link."""
        return "Debug report written and logged as an issue; fix under way or left logged."


@hosted_only
class SessionDecisionTools:
    """The tools that list and write a session's Context Decision Records, which its *DecisionRecords* keep."""

    decision_records: DecisionRecords
    paths: SessionPaths

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


@identity("session_file")
@language_adapter(language="typescript")
@agent_toolset
class Session(SessionFileTools, SessionExplorer, SessionGuidanceTools, SessionTestTierTools, SessionLogTools, SessionDecisionTools):
    """One named piece of work in a project. Its record, the session.json the board reads, is kept on main in
    ``.sessions/{name}/`` (``record_folder``); everything else it writes goes to its work folder, the same folder in its
    ticket's worktree when it has one (``work_folder``). It holds where it works, the practices it
    uses, and its title; its log, files, handoffs, decision records, and chat injections are objects of their own, made
    with it. It holds the *Sessions* that loaded it and their repository, which keep one Session for each session
    folder, so every call made in the session, from any chat, works on this one object: its graph and its one instance
    of each practice. Every tool on it acts on the session whose ``session.json`` its ``session`` argument names; a
    line a call logs points at that call's chat, which the call holds, never the session.

    A session is made for its record folder, named by it, and is whole from then on; ``placed()`` derives where it works
    now, in one order: its checkout, then its work folder, then its workpath."""

    def __init__(self, sessions: Sessions, record_folder: Path) -> None:
        # The sessions of the checkout that loaded this one, and their repository, which holds this session's ``.sessions``.
        self._sessions = sessions
        self.repo: Repo = sessions.repo
        # The root of the checkout it was last placed in, whose ``.context/config.json`` names the folder each practice
        # writes in and the formats each fidelity is chosen in by default, read again when the session moves to another.
        self._checkout_root: Path = sessions.root
        self.context_config = ContextConfig(self._checkout_root)
        self._workpath: Path | None = None
        self._record_folder = record_folder
        self._work_folder: Path | None = None
        self._make_parts()
        self.record.kept_in(record_folder)
        self.work_folder = record_folder

    def _make_parts(self) -> None:
        """The parts the session holds, each made once with it: what it reads and writes is theirs to keep."""
        self.paths = SessionPaths(self)
        self.record = SessionRecord(self)
        self.checkout = SessionCheckout(self)
        self.folder = SessionFolder(self)
        self.hierarchy = SessionHierarchy(self)
        self.guidance = GuidanceSelection(self)
        self.test_tiers = TestTiers(self)
        self.decision_records = DecisionRecords(self.work_root / CONTEXT_FOLDER / _DECISION_RECORDS_FOLDER)
        self.handoffs: Handoffs | None = None
        self.log = SessionLog(self)
        self.session_files = SessionFiles(self)
        self.chat_injections = ChatInjections(self)
        # The practices and graph this session keeps between calls, made when first asked for.
        self.session_practices = SessionPractices(self)
        self.session_graph = SessionGraph(self, self.session_practices)

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
        """Named work session (not the toolset slug): the name of its record folder."""
        return self._record_folder.name

    @property
    def is_main(self) -> bool:
        """Whether this is main, the default session, which works on the whole repository and never closes."""
        return self.name == MAIN_SESSION_NAME

    def refuse_if_main(self, action: str) -> None:
        """Refuse action, such as a close, with ``MainStaysOpenError`` when this is main, which stays open."""
        if self.is_main:
            raise MainStaysOpenError(action)

    def placed(self) -> Session:
        """This session working where it derives now, never saved on a switch: in its checkout (its own worktree, else
        the checkout whose sessions hold it), writing its work in its work folder (its worktree's ``.sessions``, else its
        record folder), at its workpath (a folder a person chose in that checkout, else the checkout). The work folder is
        set before the workpath, so a graph made again for a new workpath is kept in the new work folder."""
        worktree = self.checkout.own_worktree
        root = worktree.root if worktree is not None else self._sessions.root
        if root != self._checkout_root:
            self._checkout_root = root
            self.context_config = ContextConfig(root)
        is_own = worktree is not None and worktree.root.resolve() != self.repo.main_clone.root.resolve()
        self.work_folder = worktree.root / SESSIONS_FOLDER / self.name if is_own else self.record_folder
        workpath = self._chosen_workpath(root)
        if self.workpath is None or self.work_root != workpath:
            self.workpath = workpath
        return self

    def _chosen_workpath(self, checkout: Path) -> Path:
        """A workpath a person chose by hand in its session.json, in checkout, while that folder is there; else checkout.
        A chosen workpath that lies in another checkout of the repository names the same folder in this one."""
        stored = str(self.record.fields.workpath or "").strip()
        chosen = self._sessions.worktrees.in_checkout(checkout, checkout / stored) if stored else None
        # WHY: older switches saved the checkout itself, or a worktree since removed, as the workpath; neither was chosen.
        if chosen is not None and chosen.is_dir() and chosen not in (self._sessions.root, self.repo.main_clone.root, checkout):
            return chosen
        return checkout

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
        self._forget_practices()

    @property
    def record_folder(self) -> Path:
        """The folder of the session's record on main, ``<main clone>/.sessions/{name}/`` (``_complete``, ``_archive``
        or ``_backlog`` once it moves there): its session.json, from which the board lists its ticket and tracks where it
        stands, and its idea file. Every checkout of the repository reads the same record. None for a session not yet
        kept in one."""
        return self._record_folder

    @record_folder.setter
    def record_folder(self, folder: Path) -> None:
        """Keep the session's record in folder from now on, the folder it moved to, such as ``.sessions/_complete``."""
        self._record_folder = folder
        self.record.kept_in(folder)

    @property
    def work_folder(self) -> Path | None:
        """The folder everything else the session writes goes to: its log, hook logs, handoffs, validation reports,
        graph, progress cache, violation history, comments, and chat injections. For a ticket with its own worktree it
        is ``<worktree>/.sessions/{name}/``, so the work stays on the ticket's branch; for a session with none, such as
        main, it is the record folder. None for a session not yet kept in one."""
        return self._work_folder

    @work_folder.setter
    def work_folder(self, folder: Path | None) -> None:
        """Write the session's work in folder from now on. Its handoffs and graph were kept in the old one, so they are
        made again in the new one."""
        if folder == self._work_folder:
            return
        self._work_folder = folder
        self.handoffs = Handoffs(folder) if folder is not None else None
        self._forget_practices()

    def _forget_practices(self) -> None:
        """The practices and graph were made on the session's old root or work folder, so both are made again when next
        asked for."""
        self.session_practices.forget()
        self.session_graph.forget()

    @property
    def is_closed(self) -> bool:
        return self.record_folder is not None and self.record_folder.parent.name == COMPLETE_FOLDER

    @property
    def session_file(self) -> Path:
        """The ``session.json`` in this session's record folder, which holds its title, workpath, practice roots, and
        practices."""
        return self.record_folder / SESSION_FILE

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
        return self.paths.resolved(Path(self.workpath or self.checkout.root))

    @property
    def graph(self) -> Graph:
        """The knowledge graph this session works with, opened on its root, holding the session's one instance of each
        practice, made once on its root, so every call in the session works on the same graph and the same practices
        and none rebuilds them; an action that writes files refreshes the graph with exactly those files. It reads back
        the graph saved on its root, so a session opened again, such as a ticket just activated, shows what was loaded
        in it before. A session whose root has moved gets a new graph, with new practices, on the new root. It holds only
        the practices the session works on, so turning one on or off makes it again with those."""
        return self.session_graph.graph

    @property
    @data_field
    def title(self) -> str:
        """The title a person gave the session's ticket; empty when it has none."""
        return self.record.fields.title

    @property
    @data_field
    def repo_name(self) -> str:
        """The repository the session works in, by its folder's name, as a page heads it."""
        return self.repo.root.name

    @property
    @data_field
    def branch(self) -> str:
        """The branch the session works on: its checkout's branch, as its session.json records it, else named as the
        session, else the one branch holding its name."""
        return self.checkout.branch.name

    @property
    @data_field
    def is_repository(self) -> bool:
        """Whether the session works in a git repository, whose branch says which files the session changed; in a plain
        folder there is no branch, so no file is ever changed and a page lists the session's own files instead."""
        return self.repo.is_clone

    @property
    @data_field
    def root(self) -> str:
        """The whole path of the folder the session works in, as a page heads it."""
        return str(self.work_root)

    @property
    @data_field
    def scope(self) -> str:
        """feature, story, or slice; empty when no one said."""
        return self.record.fields.scope

    @property
    @data_field
    def parent(self) -> str:
        """The name of the session this one was split from; empty when it was not split from one."""
        return self.hierarchy.parent

    @property
    def tags(self) -> list[str]:
        """The words a person tagged this session with, in the order they were added."""
        return list(self.record.fields.tags)

    def add_tag(self, word: str) -> None:
        """Tag this session with word, once however often it is added."""
        if word in self.tags:
            return

        def tagged(fields: SessionFields) -> None:
            # Added to the tags the file holds inside the change, so a tag another chat adds at the same moment stays.
            if word not in fields.tags:
                fields.tags = [*fields.tags, word]

        self.record.update(tagged, f"tags {word}")

    @property
    def idea_file(self) -> IdeaFile:
        """``<name>.md`` in this session's record folder: what its work is about, the backlog item's file when it was
        started from one. The board shows its text on the ticket's card, so it stays with the record on main."""
        return IdeaFile(self.record_folder / f"{self.name}.md")

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
        return list(self.record.fields.overlays)

    def choose_overlays(self, overlays: list[str]) -> None:
        """Overlay the patterns named on this session's graph from now on, in place of those chosen before: kept in its
        session.json, and applied to its graph at once when it has one. A name that is no registered pattern is refused
        with NotAPatternError, and nothing changes."""
        patterns = PatternOverlays().names
        unknown = [name for name in overlays if name not in patterns]
        if unknown:
            raise NotAPatternError(unknown, patterns)
        self.record.update(lambda fields: setattr(fields, "overlays", list(overlays)), f"overlays {', '.join(overlays)}")
        self.session_graph.overlay(overlays)

    def log_tool(self, call: ToolCall, tool: str) -> None:
        """Log that call ran tool, with the paths it named, pointing at the call's chat (*CallSession*)."""
        self.log.by(call.request.chat).tool(tool, call.named_paths)

    def log_failure(self, call: ToolCall, failure: BaseException) -> None:
        """Log that call failed with failure, its trace in session.err (*CallSession*)."""
        self.log.by(call.request.chat).failure(failure, tool=call.request.tool)

    def log_hook_dispatch(self, text: str) -> None:
        """Stamp text in the hook dispatch log of the session's work folder (*HookSession*)."""
        self.folder.hook_log("dispatch.debug").stamped(text)

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
        checkout = self.paths.resolved(self.checkout.root)
        if not root.is_relative_to(checkout):
            return root.as_posix()
        relative = root.relative_to(checkout).as_posix()
        return "" if relative == "." else relative

    @property
    def accepted_violations(self) -> AcceptedViolations:
        """The violations a person accepted as they are, kept for the whole project in
        ``.context/violations-accepted.json`` under the folder the session works in, where its decision records are, so
        the file is committed with the work and every session on that folder leaves the same violations out. Made from
        wherever the session works now, since its workpath can change."""
        root = self.work_root
        return AcceptedViolations(root / CONTEXT_FOLDER / ACCEPTED_VIOLATIONS_FILE, [root, self.paths.resolved(self.checkout.root)])

    @property
    def reports_folder(self) -> Path:
        """Where Validate saves its reports in this session, each with the graph it checked beside it."""
        return self.work_folder / _REPORT_FOLDER

    def practice(self, name: str) -> PracticeSessionOutput:
        """The practice called name in this session, on or off for it: the session's one instance of it, so a practice
        turned off can be turned on again. One the session works on is opened in its graph first."""
        found = self.practices.get(name) or self.session_practices.every.get(name)
        if found is None:
            raise UnknownPracticeError(name)
        return found

    @property
    def practices(self) -> dict[str, PracticeSessionOutput]:
        """The practices the session works on, by practice key, each the session's one instance of it: the ones its
        graph holds, kept between calls with the graph, which opening here gives each practice to work in. A practice
        switched off for the session is in ``own_practices`` and ``practice(name)``, and here only once an action works
        on it (``take_up``)."""
        outputs = self.session_practices.every
        return {key: outputs[key] for key in self.graph.practices.held}

    def take_up(self, name: str) -> PracticeSessionOutput:
        """The practice called name, held in the session's graph from now on, switched on or off: an action sent to
        work on it works on it, since switching a practice off changes only what the board and chat show."""
        self.session_practices.take_up(name)
        return self.practice(name)

    @property
    @data_field(key="practices")
    def own_practices(self) -> dict[str, PracticeSessionOutput]:
        """The same practices, without opening the graph, for reading what each one declares, its folder and fidelities:
        a board listing every session would otherwise read every session's saved graph. A practice that runs is reached
        through ``practices``, so it works in the graph."""
        return dict(self.session_practices.every)

    @property
    @data_field(key="handoff")
    def latest_handoff(self) -> str:
        """The newest handoff file, as a path from the project; empty before one is written."""
        latest = self.handoffs.latest
        return self.paths.from_project(latest.path) if latest is not None else ""

    @mcp
    @command(name="close-session")
    @agent_tool
    def close(self, call: ToolCall) -> None:
        """Close this work session: when it is the open session of the calling chat, main becomes the open one.

        ``session`` is the session's session.json; ask ``sessions.current`` for it when the user names no session.
        Main, the default session, stays open, so closing it is refused with MainStaysOpenError."""
        self.refuse_if_main("close")
        self.sessions.opened.close(self, call.chat_id)

    @mcp
    @agent_tool
    @noSessionLog
    def choose_workpath(self, path: str = "") -> Session:
        """Make path, a folder in the repository, this session's workpath: the folder its practices write under and its graph loads from. An empty path is the whole repository."""
        # A practice root a person chose is kept relative to the workpath, so each is saved again against the new one
        # and still names the same folder.
        # The practices on the new workpath are kept again with it, so each root is kept by the practice that works there.
        chosen = {key: practice.folder for key, practice in self.practices.items() if practice.is_root_chosen}
        checkout = self.checkout.root
        self.workpath = self._sessions.worktrees.in_checkout(checkout, checkout / path)
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

    @property
    def file_comments(self) -> FileComments:
        """The comments a person wrote on this session's files, kept in its folder."""
        from space.session.files.file_comments import FileComments

        return FileComments(self)
