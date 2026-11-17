"""BDD development — a session opens each practice with its graph."""
import json
import os
import shutil
import sys
import tempfile
import threading
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("cdd_guidance/practices", "tools", "cdd_guidance/actions"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

import time

from expects import be, be_a, contain, equal, expect, raise_error
from mamba import after, before, context, description, it

from harness.graph.graph_reads import GraphReads
from harness.guidance.guidance import PracticeGuidance
from harness.installation.data_class import data_of
from harness.guidance_actions import GuidanceAction
from harness.hooks.hook_server import HookPayload
from harness.agent_tools.tool_call import SESSION_OPENING, ToolCall, ToolRequest
from harness.mcp.mcp_server import McpServer
from harness.whiteboard import BoardLinks
from space.repo.mock_repo import MockGit
from tools.prompt_queue.prompt_queue import PromptQueue
from space.repo.repo import Repo
from space.session import Session, Sessions
from harness.agent_tools.chat_pointer import ChatPointer
from space.session.session_log import LoopNotFoundError
from space.session.open_sessions import SessionNameRequiredError
from space.work_state import WorkState
import cdd_guidance.practices  # noqa: F401 - registers the practices with the practice catalogue
import cdd_guidance.actions  # noqa: F401 - registers the actions with the action catalogue
from space.session.throwaway_project import ExampleHome, SPEC_RUN_HOME
from harness.guidance.practice_catalogue import PRACTICE_CATALOGUE

# The first practices a process makes read and parse their guidance for every later one; made once here, before any
# example, so no example pays for that first read.
PRACTICE_CATALOGUE.create_all()


_HANDOFF_WITH_STEPS = """# Handoff

## Approach for Next Agent

1. Read the handoff
2. Run the unit tier
"""


def _chat_in(session: Session, chat_id: str = "spec-chat") -> ChatPointer:
    """A chat called chat_id whose transcript sits in session's folder: the chat a call from it names."""
    chats = session.work_folder / "chats"
    chats.mkdir(parents=True, exist_ok=True)
    transcript = chats / f"{chat_id}.md"
    transcript.write_text("spec transcript\n", encoding="utf-8")
    return ChatPointer.of(chat_id, transcript, "1")


def _chat_arguments(chat_id: str, transcript: Path) -> dict[str, str]:
    """The chat fields an MCP call from chat_id sends with its own arguments."""
    return {"conversation_id": chat_id, "transcript_path": str(transcript), "transcript_lines": "1"}


# (E) Open Work Session
# (E) Hold Process Session
with description("a session"):
    with before.each:
        self.home = ExampleHome()

    with after.each:
        self.home.close()

    # (S) Session --> Persist Hook Session
    with context("that a hook event reads"):
        with before.each:
            self.root = Path(tempfile.mkdtemp())
            self.event = lambda: HookPayload({"hook_event_name": "stop"}, self.root)

        with it("should be the main session until another is open on the repo"):
            expect(self.event().session.name).to(equal("main"))

        with context("with a named session opened after the hook server started"):
            with before.each:
                self.work = self.root / "work"
                self.work.mkdir()
                Sessions(self.root).switch("alpha", self.work)

            with it("should be that session"):
                expect(self.event().session.name).to(equal("alpha"))

            with it("should open that practice's guidance"):
                expect(self.event().session.practice("stories").guidance).to(be_a(PracticeGuidance))

            with it("should open the session's graph, which holds that practice"):
                expect(self.event().session.graph.practices.held["stories"]).to(be(self.event().session.practice("stories").guidance))

            with it("should open the same graph on the next call in that session"):
                expect(self.event().session.graph).to(be(self.event().session.graph))

            with context("that has closed"):
                with it("should be the main session again"):
                    Sessions(self.root).current().close()
                    expect(self.event().session.name).to(equal("main"))

    # (S) Session --> Read Call Session
    with context("that a tool call reads"):
        with before.each:
            self.repo = Path(tempfile.mkdtemp())
            (self.repo / ".git").mkdir()

        with it("should be the main session until another is open on the repo"):
            expect(ToolCall({}, self.repo).session.name).to(equal("main"))

        with it("should agree with a hook event on the same repo"):
            expect(ToolCall({}, self.repo).session.record_folder).to(equal(HookPayload({"cwd": str(self.repo)}).session.record_folder))

        with it("should agree with the session opened for the project without a call"):
            expect(ToolCall({}, self.repo).session.record_folder).to(equal(SESSION_OPENING.saved_in(self.repo).record_folder))

        with context("with a named session open"):
            with before.each:
                self.work = self.repo / "work"
                self.work.mkdir()
                Sessions(self.repo).switch("alpha", self.work)

            with it("should be that session"):
                expect(ToolCall({}, self.repo).session.record_folder).to(equal(self.repo.resolve() / ".sessions" / "alpha"))

            with it("should be that session when the call's project is the workpath folder"):
                expect(ToolCall({}, self.work).session.name).to(equal("alpha"))

            with it("should be the one session its sessions hold, whichever call reads it"):
                expect(ToolCall({}, self.repo).session is ToolCall({}, self.repo).session).to(equal(True))

    # (S:system) Cdd Server --> Queue Handoff Steps On Session Start
    with context("that a chat switches to it with a handoff written"):
        with before.each:
            self.repo = Path(tempfile.mkdtemp())
            work = self.repo / "work"
            work.mkdir()
            Sessions(self.repo).switch("alpha", work)
            Sessions(self.repo).current().handoffs.write(_HANDOFF_WITH_STEPS)
            self.chat = f"queue-chat-{time.time_ns()}"
            self.call = ToolCall.sent({}, self.repo, ToolRequest(ChatPointer.from_request(self.chat)))
            self.instructions = Sessions(self.repo).switch("alpha", call=self.call)

        with it("should queue the handoff's steps on the chat's prompt queue, in order"):
            expect([prompt["text"] for prompt in PromptQueue.of_chat(self.chat).prompts]).to(equal(["Read the handoff", "Run the unit tier"]))

        with it("should tell the agent to work through them, marking each one done"):
            expect(self.instructions).to(contain("prompt-queue.done"))

        with it("should queue them once, however often the chat switches to it again"):
            Sessions(self.repo).switch("alpha", call=self.call)
            expect(len(PromptQueue.of_chat(self.chat).prompts)).to(equal(2))

    # (E) Open Named Session
    # (S) Session --> Open New Session
    with context("that is new"):
        with before.each:
            self.repo = Path(tempfile.mkdtemp())
            self.called = self.repo
            self.work = self.repo / "work"
            self.work.mkdir()
            self.instructions = Sessions(self.repo).switch("alpha", self.work)

        with it("should return how to keep its log to the agent"):
            expect(self.instructions).to(contain("Keeping the session log"))

        with it("should keep the name, the workpath, and the repo path"):
            session = Sessions(self.called).current()
            expect(session.name).to(equal("alpha"))
            expect(session.workpath).to(equal(self.work))
            expect(session.repo_path).to(equal(self.repo.resolve()))
            expect(session.record_folder).to(equal(self.repo.resolve() / ".sessions" / "alpha"))

        with it("should write --- 1 as the first line of a new session.log"):
            first = (Sessions(self.called).current().work_folder / "session.log").read_text(encoding="utf-8").splitlines()[0]
            expect("--- 1" in first).to(equal(True))

        with it("should keep the name as the open session under the cdd home"):
            expect(WorkState(self.repo).session).to(equal("alpha"))

        with it("should write no open-session pointer in the checkout"):
            expect((self.repo / ".sessions" / "session.json").exists()).to(equal(False))

    with context("whose session.json holds a board ticket's title, scope, and parent"):
        with before.each:
            self.repo = Path(tempfile.mkdtemp())
            self.called = self.repo
            self.work = self.repo / "work"
            self.work.mkdir()
            folder = self.repo / ".sessions" / "alpha"
            folder.mkdir(parents=True)
            (folder / "session.json").write_text(
                json.dumps({"name": "alpha", "title": "Pet visits", "scope": "feature", "parent": "pawplace"}),
                encoding="utf-8",
            )
            Sessions(self.repo).switch("alpha", self.work)

        with it("should keep the ticket's title, scope, and parent after it is switched to"):
            stored = json.loads((self.repo / ".sessions" / "alpha" / "session.json").read_text(encoding="utf-8"))
            expect((stored.get("title"), stored.get("scope"), stored.get("parent"))).to(equal(("Pet visits", "feature", "pawplace")))

    with context("that is closed"):
        with before.each:
            self.repo = Path(tempfile.mkdtemp())
            self.called = self.repo
            self.work = self.repo / "work"
            self.work.mkdir()
            Sessions(self.repo).switch("alpha", self.work)
            Sessions(self.called).current().close()

        with it("should clear the open session kept under the cdd home"):
            expect(WorkState(self.repo).session).to(equal(""))

        with it("should go back to the main session"):
            expect(Sessions(self.called).current().name).to(equal("main"))

    # (S) Session --> Select Existing Session
    with context("that is selected"):
        with before.each:
            self.repo = Path(tempfile.mkdtemp())
            self.called = self.repo
            self.work = self.repo / "work"
            self.work.mkdir()
            Sessions(self.repo).switch("alpha", self.work)

        with context("with only a name"):
            with before.each:
                self._prior_repo = os.environ.get("CDD_REPO")
                self._prior_project = os.environ.get("CDD_PROJECT")
                (self.repo / ".git").mkdir()
                os.environ["CDD_REPO"] = str(Path(tempfile.mkdtemp()))
                os.environ["CDD_PROJECT"] = str(self.repo / "other")
                self.instructions = Sessions(self.called).switch("alpha")

            with it("should bind the existing session from the environment"):
                session = Sessions(self.called).current()
                expect(session.name).to(equal("alpha"))
                expect(session.repo_path).to(equal(self.repo.resolve()))
                expect(session.record_folder).to(equal(self.repo.resolve() / ".sessions" / "alpha"))

            with it("should use the workpath stored on that session"):
                expect(Sessions(self.called).current().workpath).to(equal(self.work.resolve()))

            with it("should return how to keep its log to the agent"):
                expect(self.instructions).to(contain("Keeping the session log"))

            with after.each:
                if self._prior_repo is None:
                    os.environ.pop("CDD_REPO", None)
                else:
                    os.environ["CDD_REPO"] = self._prior_repo
                if self._prior_project is None:
                    os.environ.pop("CDD_PROJECT", None)
                else:
                    os.environ["CDD_PROJECT"] = self._prior_project

        # A session's name is its folder and its branch, and git refuses a space in a branch name.
        with context("with a name that has spaces and capitals"):
            with before.each:
                Sessions(self.repo).switch("Chat UI", self.work)

            with it("should name the session by its slug"):
                expect(Sessions(self.called).current().name).to(equal("chat-ui"))

            with it("should keep the session in a folder named by its slug"):
                expect((self.repo / ".sessions" / "chat-ui" / "session.json").is_file()).to(equal(True))

        # A chat in a ticket's own worktree works on that ticket; every ticket's record stays in the repository's own
        # .sessions, and the ticket's worktree carries only its work.
        with context("from the linked worktree of a ticket"):
            with before.each:
                # The repository and its worktree held in memory: what is checked out where is all these examples ask git.
                held = MockGit(self.repo.resolve())
                held.make_clone()
                Sessions(self.repo).create("alpha")
                self.worktree = Path(tempfile.mkdtemp()).resolve() / "alpha"
                held.add_worktree("alpha", self.worktree)
                self.called = self.worktree

            with after.each:
                shutil.rmtree(self.worktree.parent, ignore_errors=True)

            with it("should work on that ticket's session"):
                expect(Sessions(self.called).current().name).to(equal("alpha"))

            # The board lists the ticket and tracks where it stands from its record, which stays on main; everything
            # else the session writes goes with its work, in the ticket's worktree.
            with it("should keep its record in the ticket's folder in the repository's own .sessions"):
                expect(Sessions(self.called).current().record_folder).to(equal(self.repo.resolve() / ".sessions" / "alpha"))

            with it("should keep its work in the ticket's folder in its worktree's .sessions"):
                expect(Sessions(self.called).current().work_folder).to(equal(self.worktree / ".sessions" / "alpha"))

            with context("that works"):
                with before.each:
                    self.session = Sessions(self.called).current()
                    self.session.mark_loop(ToolCall())
                    self.handoff = Path(self.session.write_handoff("Next steps"))
                    self.session.record.save_fields(stage="Specification")

                with it("should log into its work folder"):
                    expect((self.worktree / ".sessions" / "alpha" / "session.log").read_text(encoding="utf-8")).to(contain("--- 1"))

                with it("should write its handoffs into its work folder"):
                    expect(self.handoff.parent).to(equal(self.worktree / ".sessions" / "alpha"))

                with it("should keep its validation reports in its work folder"):
                    expect(self.session.reports_folder).to(equal(self.worktree / ".sessions" / "alpha" / "validation-reports"))

                with it("should save its session.json in its record folder"):
                    saved = json.loads((self.repo / ".sessions" / "alpha" / "session.json").read_text(encoding="utf-8"))
                    expect(saved["stage"]).to(equal("Specification"))

                with it("should write no session.json into its work folder"):
                    expect((self.worktree / ".sessions" / "alpha" / "session.json").exists()).to(equal(False))

            with context("that closes"):
                with before.each:
                    self.session = Sessions(self.called).current()
                    self.session.folder.move_to_closed()

                with it("should move its record among the closed sessions"):
                    expect(self.session.record_folder).to(equal(self.repo.resolve() / ".sessions" / "_complete" / "alpha"))

                with it("should leave its work in its worktree"):
                    expect(self.session.work_folder).to(equal(self.worktree / ".sessions" / "alpha"))

            # The board and the chat bar name the active ticket by the open session's name, so it follows the worktree
            # as current does: the ticket's own chat shows the ticket, not main.
            with it("should name that ticket as the session open"):
                expect(Sessions(self.called).opened.name_for()).to(equal("alpha"))

            with context("that a chat in the repository's own folder switches to"):
                with before.each:
                    self.instructions = Sessions(self.repo).switch("alpha", call=ToolCall({}, self.repo))

                with it("should say the chat works outside the ticket's worktree"):
                    expect(self.instructions).to(contain(f"This chat works in {self.repo.resolve()}, but alpha's worktree is {self.worktree.resolve()}"))

                with it("should say to start a chat in the worktree"):
                    expect(self.instructions).to(contain(f"start_session with cwd {self.worktree.resolve()}"))

            with context("that a chat in the ticket's worktree switches to"):
                with it("should give no warning"):
                    instructions = Sessions(self.worktree).switch("alpha", call=ToolCall({}, self.worktree))
                    expect(instructions).not_to(contain("This chat works in"))

            # A session's root has to be in its own worktree: a workpath saved into the repository's own folder, as
            # older saves wrote it, names the same folder in the ticket's worktree.
            with context("with a workpath stored in the repository's own folder"):
                with before.each:
                    (self.repo / "harness").mkdir()
                    (self.worktree / "harness").mkdir()
                    stored = self.repo / ".sessions" / "alpha" / "session.json"
                    fields = json.loads(stored.read_text(encoding="utf-8"))
                    fields.update(workpath=str(self.repo.resolve() / "harness"), repo_path=str(self.repo.resolve()))
                    stored.write_text(json.dumps(fields), encoding="utf-8")
                    self.session = Sessions(self.repo).named("alpha")

                with it("should work in that folder in the ticket's worktree"):
                    expect(self.session.work_root).to(equal(self.worktree.resolve() / "harness"))

                with it("should take the ticket's worktree as its repository"):
                    expect(self.session.repo_path).to(equal(self.worktree.resolve()))

                with context("that is saved"):
                    with before.each:
                        self.session.record.save()

                    with it("should keep its workpath from the repository's top"):
                        expect(self.session.record.fields["workpath"]).to(equal("harness"))

                    with it("should keep working in that folder in the ticket's worktree"):
                        expect(Sessions(self.repo).named("alpha").work_root).to(equal(self.worktree.resolve() / "harness"))

            # The worktree holds only its ticket's work, so a chat there always opens the ticket's session.
            with context("that a chat in the ticket's worktree switches naming no session"):
                with before.each:
                    self.instructions = Sessions(self.worktree).switch(call=ToolCall({}, self.worktree))

                with it("should open the ticket's session"):
                    expect(Sessions(self.worktree).current().name).to(equal("alpha"))

                with it("should return how to keep its log"):
                    expect(self.instructions).to(contain("Keeping the session log"))

            with context("that a chat in the ticket's worktree switches to main"):
                with before.each:
                    self.instructions = Sessions(self.worktree).switch("main", call=ToolCall({}, self.worktree))

                with it("should open the ticket's session"):
                    expect(Sessions(self.worktree).current().name).to(equal("alpha"))

                with it("should say the worktree belongs to the ticket"):
                    expect(self.instructions).to(contain("This chat works in alpha's own worktree, so its session is alpha, not main"))

            with context("that a chat in the ticket's worktree switches to another ticket"):
                with before.each:
                    Sessions(self.repo).create("beta")
                    self.instructions = Sessions(self.worktree).switch("beta", call=ToolCall({}, self.worktree))

                with it("should open the worktree's ticket"):
                    expect(Sessions(self.worktree).current().name).to(equal("alpha"))

                with it("should say the worktree belongs to the ticket"):
                    expect(self.instructions).to(contain("so its session is alpha, not beta"))

        with context("with a repo path"):
            with before.each:
                self.instructions = Sessions(self.repo).switch("alpha")

            with it("should keep its record under that repo at sessions and the name"):
                expect(Sessions(self.called).current().record_folder).to(equal(self.repo.resolve() / ".sessions" / "alpha"))

            # A session with no worktree of its own keeps its work beside its record.
            with it("should keep its work in its record folder"):
                expect(Sessions(self.called).current().work_folder).to(equal(self.repo.resolve() / ".sessions" / "alpha"))

            with it("should read the workpath from that session"):
                expect(Sessions(self.called).current().workpath).to(equal(self.work.resolve()))

        with context("that another client of the same chat switches"):
            with it("should reload the named session instead of keeping stale memory"):
                Sessions(self.repo).switch("alpha", self.work)
                Sessions(self.repo).switch("beta", self.work)
                expect(Sessions(self.called).current().name).to(equal("beta"))
                WorkState(self.repo).session = "alpha"
                expect(Sessions(self.called).current().name).to(equal("alpha"))

    # (S) Session --> Open Session Loop
    with context("that opens a loop"):
        with before.each:
            self.repo = Path(tempfile.mkdtemp())
            self.called = self.repo
            self.work = self.repo / "work"
            self.work.mkdir()
            Sessions(self.repo).switch("alpha", self.work)

        with it("should seed loop 1 in session.log when the session is new"):
            log = (Sessions(self.called).current().work_folder / "session.log").read_text(encoding="utf-8")
            expect("--- 1" in log).to(equal(True))

        with it("should mark loops via mark_loop when a session is current"):
            expect(Sessions(self.called).current().mark_loop(ToolCall())).to(equal("2"))

    with context("that resumes loop numbering from session.log"):
        with before.each:
            self.repo = Path(tempfile.mkdtemp())
            self.called = self.repo
            self.work = self.repo / "work"
            self.work.mkdir()
            Sessions(self.repo).switch("alpha", self.work)
            Sessions(self.called).current().log.record("--- 2")

        with it("should append the next loop after switch without in-memory loops"):
            Sessions(self.repo).switch("alpha", self.work)
            expect(Sessions(self.called).current().mark_loop(ToolCall())).to(equal("3"))

    # A ticket's moves and marks are lines of its session's log, which the log answers rather than its readers scanning it.
    with context("whose log records moves and marks on the board's stages"):
        with before.each:
            self.repo = Path(tempfile.mkdtemp())
            Sessions(self.repo).switch("alpha", self.repo)
            self.log = Sessions(self.repo).current().log
            for line in ("move Discovery", "done Discovery", "move Specification", "in-progress Specification"):
                self.log.record(line)

        with it("should answer the latest line of a verb"):
            expect(self.log.latest("move").stage).to(equal("Specification"))

        with it("should answer the latest line of several verbs that names a stage"):
            expect(self.log.latest("move", "done", "in-progress", stage="Discovery").verb).to(equal("done"))

        with it("should answer none for a verb the log has no line of"):
            expect(self.log.latest("review")).to(equal(None))

    # (E) Record Session Log
    # (S) Session --> Record Session Error
    with context("that logs an error"):
        with before.each:
            self.repo = Path(tempfile.mkdtemp())
            self.called = self.repo
            self.work = self.repo / "work"
            self.work.mkdir()
            Sessions(self.repo).switch("alpha", self.work)
            self.failure = RuntimeError("boom")

        with it("should write the trace to session.err"):
            Sessions(self.called).current().log.by(None).failure(self.failure)
            err = (Sessions(self.called).current().work_folder / "session.err").read_text(encoding="utf-8")
            expect("boom" in err).to(equal(True))

        with it("should point the session.log line at that session.err file"):
            Sessions(self.called).current().log.by(None).failure(self.failure)
            log = (Sessions(self.called).current().work_folder / "session.log").read_text(encoding="utf-8")
            expect("session.err" in log).to(equal(True))

        with it("should append a second failure without overwriting session.err"):
            session = Sessions(self.called).current()
            session.log.by(None).failure(RuntimeError("first"))
            session.log.by(None).failure(RuntimeError("second"))
            err = (session.work_folder / "session.err").read_text(encoding="utf-8")
            expect("first" in err and "second" in err).to(equal(True))

    with context("that records MCP tool failures on dispatch"):
        with before.each:
            self.repo = Path(tempfile.mkdtemp())
            self.called = self.repo
            self.work = self.repo / "work"
            self.work.mkdir()
            Sessions(self.repo).switch("alpha", self.work)
            self.session = Sessions(self.called).current()

        with it("should append session.err and session.log when an agent tool raises"):
            from harness.mcp.mcp_server import McpHost

            host = McpHost.from_refs(
                ("space.session.session:Session",),
                repo=str(self.repo),
                project=str(self.repo),
            )
            try:
                host.dispatch("session.append_log", {"session": self.session.session_file_from_project, "note": "late", "loop": 99}, self.called)
            except LookupError:
                pass
            log = (self.session.work_folder / "session.log").read_text(encoding="utf-8")
            err = (self.session.work_folder / "session.err").read_text(encoding="utf-8")
            expect(
                "error" in log
                and "session.append_log" in log
                and "session.err" in log
                and "loop 99 not found" in err
            ).to(equal(True))

    with context("that logs enrolled MCP tools on dispatch"):
        with before.each:
            self.repo = Path(tempfile.mkdtemp())
            self.called = self.repo
            self.work = self.repo / "work"
            self.work.mkdir()
            Sessions(self.repo).switch("alpha", self.work)
            self.session = Sessions(self.called).current()
            self.transcript = _chat_in(self.session, "mcp-dispatch-chat").transcript

        with it("should append a tool line when the MCP host invokes an agent tool"):
            from harness.mcp.mcp_server import McpHost

            host = McpHost.from_refs(
                ("space.session.session:Session",),
                repo=str(self.repo),
                project=str(self.repo),
            )
            host.dispatch("session.mark_loop", {"session": self.session.session_file_from_project, **_chat_arguments("mcp-dispatch-chat", self.transcript)}, self.called)
            log = (self.session.work_folder / "session.log").read_text(encoding="utf-8")
            expect("tool session.mark_loop" in log and "mcp-dispatch-chat" in log).to(equal(True))

    with context("that records a loop correction note"):
        with before.each:
            self.repo = Path(tempfile.mkdtemp())
            self.called = self.repo
            self.work = self.repo / "work"
            self.work.mkdir()
            Sessions(self.repo).switch("alpha", self.work)
            self.session = Sessions(self.called).current()
            self.chat_log = self.session.log.by(_chat_in(self.session, "note-chat"))

        with it("should append a note line with message paths and chat pointer"):
            touched = self.work / "repo.py"
            self.chat_log.note("close_branch must push merge checkout main", [touched])
            log = (self.session.work_folder / "session.log").read_text(encoding="utf-8")
            expect(
                "note close_branch must push merge checkout main" in log
                and str(touched) in log
                and "note-chat" in log
            ).to(equal(True))

        with it("should append via append_log with loop number and chat fields"):
            call = ToolCall(request=ToolRequest(_chat_in(self.session, "append-chat")))
            result = self.session.append_log(call, "correction recorded", loop=1, paths=[str(self.work / "session.py")])
            log = (self.session.work_folder / "session.log").read_text(encoding="utf-8")
            expect(
                "appended note" in result
                and "loop 1: correction recorded" in log
                and "append-chat" in log
            ).to(equal(True))

    # (S) Session --> Record Session Action
    with context("that logs an action"):
        with before.each:
            self.repo = Path(tempfile.mkdtemp())
            self.called = self.repo
            self.work = self.repo / "work"
            self.work.mkdir()
            Sessions(self.repo).switch("alpha", self.work)
            self.session = Sessions(self.called).current()
            self.chat_log = self.session.log.by(_chat_in(self.session))
            self.edited = self.work / "cart.py"
            self.edited.write_text("class Cart:\n    pass\n", encoding="utf-8")

        # Every tool call from a chat the server cannot name logs this way, so a note per line in session.err grew it without end.
        with context("with no chat known"):
            with before.each:
                bare = Path(tempfile.mkdtemp())
                work = bare / "work"
                work.mkdir()
                Sessions(bare).switch("alpha", work)
                self.bare_session = Sessions(self.called).current()
                self.bare_session.log.by(None).action("sketch", [work / "x.py"])

            with it("should log the action as from no chat"):
                log = (self.bare_session.work_folder / "session.log").read_text(encoding="utf-8")
                expect(log.rstrip().endswith("x.py no-chat")).to(equal(True))

            with it("should write nothing to session.err"):
                expect((self.bare_session.work_folder / "session.err").exists()).to(equal(False))

            with context("with the server's environment naming a chat"):
                with before.each:
                    transcript = Path(tempfile.mkdtemp()) / "other.jsonl"
                    transcript.write_text("{}\n", encoding="utf-8")
                    os.environ.update(CDD_CONVERSATION_ID="other-chat", CDD_TRANSCRIPT_PATH=str(transcript))
                    self.bare_session.log.by(None).action("generate", [Path("y.py")])

                with after.each:
                    os.environ.pop("CDD_CONVERSATION_ID", None)
                    os.environ.pop("CDD_TRANSCRIPT_PATH", None)

                with it("should still log the action as from no chat, not the chat the environment names"):
                    log = (self.bare_session.work_folder / "session.log").read_text(encoding="utf-8")
                    expect(log.rstrip().endswith("y.py no-chat")).to(equal(True))

        with context("with paths passed in"):
            with it("should append a timestamped line that names the action and the path"):
                self.chat_log.action("sketch", [self.edited])
                log = (self.session.work_folder / "session.log").read_text(encoding="utf-8")
                expect("sketch" in log and str(self.edited) in log and "T" in log).to(equal(True))

        with context("with the practice it worked on"):
            with it("should name the practice graph root"):
                self.chat_log.action("sketch", [self.edited], [self.session.practice("bdd").fidelities["behavior"].session_output])
                log = (self.session.work_folder / "session.log").read_text(encoding="utf-8")
                expect("bdd" in log).to(equal(True))

        with context("with rules injected from a inject rules hook"):
            with before.each:
                rules = self.session.practice("bdd").fidelities["development"].rules
                self.session.log.injected_rules.note(rules, str(self.edited))

            with it("should log that practice, fidelity, rule, and matched file"):
                self.chat_log.action("sketch", [self.edited])
                log = (self.session.work_folder / "session.log").read_text(encoding="utf-8")
                expect(
                    "bdd development hierarchy-preservation" in log and str(self.edited) in log
                ).to(equal(True))

            with it("should omit a rule that was not injected"):
                self.chat_log.action("sketch", [self.edited])
                log = (self.session.work_folder / "session.log").read_text(encoding="utf-8")
                expect("stories-story-map" in log).to(equal(False))

        with context("with a chat transcript"):
            with it("should point at the chat id, the transcript file, and the line numbers"):
                transcript = self.work / "chat.md"
                transcript.write_text("hello\n", encoding="utf-8")
                self.session.log.by(ChatPointer("chat-1", transcript, "1-2")).action("sketch", [self.edited])
                log = (self.session.work_folder / "session.log").read_text(encoding="utf-8")
                expect("chat-1" in log and str(transcript) in log and "1-2" in log).to(equal(True))

    # (S) Session --> Select Existing Session
    with context("that is loaded from its folder"):
        with before.each:
            self.repo = Path(tempfile.mkdtemp())
            self.called = self.repo
            (self.repo / ".git").mkdir()
            self.work = self.repo / "work"
            self.work.mkdir()
            Sessions(self.repo).switch("alpha", self.work)
            self.record_folder = Sessions(self.called).current().record_folder

        with it("should read the repo path and the workpath from that session"):
            session = Sessions(self.repo).held.load(self.record_folder)
            expect(session.repo_path).to(equal(self.repo.resolve()))
            expect(session.workpath).to(equal(self.work.resolve()))

    # (S) Session --> Select Existing Session
    with context("with a workpath"):
        with before.each:
            self.repo = Path(tempfile.mkdtemp())
            self.called = self.repo
            (self.repo / ".git").mkdir()
            self.work = self.repo / "work"
            self.work.mkdir()
            Sessions(self.repo).switch("alpha", self.work)

        with it("should keep the given workpath and take the repo root from it"):
            Sessions(self.work).switch("alpha", self.work)
            session = Sessions(self.called).current()
            expect(session.workpath).to(equal(self.work.resolve()))
            expect(session.repo_path).to(equal(self.repo.resolve()))


# (E) Open Work Session
# (E) Open Named Session
# (S) Session --> Open Session Loop
with description("a loop"):
    with before.each:
        self.home = ExampleHome()

    with after.each:
        self.home.close()

    with context("that is opened"):
        with before.each:
            self.repo = Path(tempfile.mkdtemp())
            self.called = self.repo
            self.work = self.repo / "work"
            self.work.mkdir()
            Sessions(self.repo).switch("alpha", self.work)
            self.first = Sessions(self.called).current().log.by(None).next_loop()
            self.second = Sessions(self.called).current().log.by(None).next_loop()

        with it("should take the next loop number"):
            expect(self.second.number).to(equal(self.first.number + 1))

        with it("should append the loop marker to session.log"):
            log = (Sessions(self.called).current().work_folder / "session.log").read_text(encoding="utf-8")
            expect(f"--- {self.second.number}" in log).to(equal(True))

    with context("that has log entries"):
        with before.each:
            self.repo = Path(tempfile.mkdtemp())
            self.called = self.repo
            self.work = self.repo / "work"
            self.work.mkdir()
            Sessions(self.repo).switch("alpha", self.work)
            self.session = Sessions(self.called).current()
            chat_log = self.session.log.by(_chat_in(self.session, "loop-chat"))
            self.opened = chat_log.next_loop()
            chat_log.action("sketch", [self.work / "cart.py"])

        with it("should return the log lines for that loop number"):
            expect(any("sketch" in line for line in self.session.log.loop_at(self.opened.number).entries)).to(equal(True))

        with it("should put the loop marker line first when loaded from session.log"):
            reloaded = self.session.log.loop_at(self.opened.number)
            expect(reloaded.entries[0]).to(contain(f"--- {reloaded.number}"))

        with it("should reload log lines from session.log when accessed by loop number"):
            Sessions(self.repo).switch("alpha")
            reloaded = Sessions(self.called).current().log.loop_at(self.opened.number)
            expect(any("sketch" in line for line in reloaded.entries)).to(equal(True))

        with it("should read a loop with transcripts via read_loop"):
            chat = self.work / "chat.jsonl"
            chat.write_text(
                '{"role": "user", "message": {"content": [{"type": "text", "text": "loop read"}]}}\n',
                encoding="utf-8",
            )
            chat_id = "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"
            self.session.log.by(ChatPointer(chat_id, chat, "1")).action("validate", [self.work / "cart.py"])
            body = Sessions(self.called).current().read_loop(self.opened.number)
            expect("loop read" in body and "validate" in body).to(equal(True))


# (E) Open Work Session
# (E) Record Session Log
with description("an action"):
    with after.each:
        self.home.close()

    with before.each:
        self.home = ExampleHome()
        self.repo = Path(tempfile.mkdtemp())
        self.called = self.repo
        self.work = self.repo / "work"
        self.work.mkdir()
        Sessions(self.repo).switch("alpha", self.work)
        self.session = Sessions(self.called).current()
        self.chat_log = self.session.log.by(_chat_in(self.session, "action-chat"))

    # (S) Session --> Record Validation Run
    with context("that calls validate"):
        with before.each:
            self.practice = self.session.practice("bdd").fidelities["behavior"].session_output

        with context("with a practice and a fidelity"):
            with it("should log that practice and that fidelity"):
                self.chat_log.validation(self.practice, [])
                log = (self.session.work_folder / "session.log").read_text(encoding="utf-8")
                expect("Bdd" in log and "behavior" in log).to(equal(True))

        with context("with a violation"):
            with it("should log the rule, the synopsis, and the correction"):
                self.chat_log.validation(self.practice, 
                    ["hierarchy-preservation synopsis: flattened tree correction: keep the nesting"],
                )
                log = (self.session.work_folder / "session.log").read_text(encoding="utf-8")
                expect("hierarchy-preservation" in log and "synopsis" in log and "correction" in log).to(
                    equal(True)
                )

    # (S) Session --> Record Session Action
    with context("that names an action"):
        with it("should log that action"):
            action = GuidanceAction(self.session)
            action._work_on("a note")
            action.run(lambda item: None, action="sketch")
            log = (self.session.work_folder / "session.log").read_text(encoding="utf-8")
            expect("sketch" in log).to(equal(True))

        with it("should log workpath and practice context for listed guidance"):
            from harness.guidance_actions import GuidanceAction

            action = GuidanceAction(self.session)
            action._work_on(["bdd"])
            action.run(lambda item: None, action="generate")
            log = (self.session.work_folder / "session.log").read_text(encoding="utf-8")
            expect("generate" in log and str(self.work) in log and "bdd" in log).to(equal(True))

        with context("with MCP host session binding like session.switch"):
            with it("should log generate and validate with practice context"):
                import os

                from harness.mcp.mcp_server import McpServer
                from cdd_guidance.actions.validate.validate import Validate

                (self.repo / ".git").mkdir(exist_ok=True)
                os.environ["CDD_REPO"] = str(self.repo.resolve())
                os.environ["CDD_PROJECT"] = str(self.work.resolve())
                McpServer(repo=self.repo, project=self.work)
                action = GuidanceAction(self.session)
                action._work_on(["bdd"])
                action.run(lambda _item: None, action="generate")
                Validate(self.session).validate(["bdd"])
                log = (self.session.work_folder / "session.log").read_text(encoding="utf-8")
                expect(
                    "generate" in log
                    and "bdd" in log
                    and "validate" in log
                    and "Bdd" in log
                ).to(equal(True))

        with context("after inject_rules records rules on the session"):
            with it("should name those rules on the next log_action line"):
                from harness.guidance.fixtures.sample_tool.sample_tool_host import (
                    SamplePracticeGuidance,
                )

                guidance = SamplePracticeGuidance(format="markdown")
                edited = self.work / "pkg" / "foo_sample_bar.py"
                edited.parent.mkdir(parents=True, exist_ok=True)
                edited.write_text("x = 1\n", encoding="utf-8")
                guidance.rules.inject_rules(
                    HookPayload({
                        "hook_event_name": "afterFileEdit",
                        "file_path": edited.as_posix(),
                        "cwd": str(self.repo),
                    })
                )
                self.chat_log.action("sketch", [edited])
                log = (self.session.work_folder / "session.log").read_text(encoding="utf-8")
                expect("sample-rule-one" in log and str(edited) in log).to(equal(True))

    with context("that names no action"):
        with it("should leave session.log unchanged"):
            log_path = self.session.work_folder / "session.log"
            before = log_path.read_text(encoding="utf-8") if log_path.is_file() else ""
            action = GuidanceAction(self.session)
            action._work_on("a note")
            action.run(lambda item: None)
            after_log = log_path.read_text(encoding="utf-8") if log_path.is_file() else ""
            expect(after_log).to(equal(before))


# (E) Open Work Session
# (E) Hold Process Session
# (S) Session --> Load Practice Guideline
with description("a practice"):
    with before.each:
        self.home = ExampleHome()

    with after.each:
        self.home.close()

    with context("that a practice has been invoked"):
        with before.each:
            self.repo = Path(tempfile.mkdtemp())
            self.called = self.repo
            self.work = self.repo / "work"
            self.work.mkdir()
            Sessions(self.repo).switch("alpha", self.work)
            self.session = Sessions.of_project(self.called).current()
            self.opened = self.session.practice("bdd")

        with it("should hold that practice's guidance in memory"):
            expect(isinstance(self.opened.guidance, PracticeGuidance)).to(equal(True))

        with it("should be the one practice the session's graph holds"):
            expect(self.session.graph.practices.held["bdd"]).to(be(self.opened.guidance))

        with it("should know the session's graph"):
            expect(self.opened.guidance.reading.graph).to(be(self.session.graph))

        with it("should be the same practice the next call in the session works with"):
            expect(Sessions.of_project(self.called).current().practice("bdd").guidance).to(be(self.opened.guidance))

        with it("should hold the practice it extends from the same session"):
            expect(self.session.practice("ddd").guidance.working_set.extended).to(be(self.session.practice("clean_engineering").guidance))

        with it("should open its graph on its workpath"):
            expect(self.opened.guidance.reading.in_graph.source_root).to(equal(str(self.work.resolve())))

        with it("should be the same graph on the next call in the session"):
            expect(Sessions.of_project(self.called).current().graph).to(be(self.session.graph))

        with it("should have one output for that practice, whichever call asks"):
            expect(Sessions.of_project(self.called).current().practices["bdd"]).to(be(self.opened))

        # (S) Session --> Read Saved Graph When First Opened
        with context("with a graph loaded and saved in its workpath"):
            with before.each:
                (self.work / "order.py").write_text("class Order:\n    def place(self) -> None:\n        pass\n", encoding="utf-8")
                self.session.graph.load_working_copy(str(self.work), {"clean_engineering": str(self.work)})

            with it("should hold the saved nodes when another process first opens the session"):
                reopened = Sessions(self.repo).current().graph
                practice = reopened.practices.held["clean_engineering"]
                expect([node.name for node in practice.reading.in_graph.nodes()]).to(contain("Order"))

        with it("should return that same practice on the next ask"):
            expect(self.session.practice("bdd") is self.opened).to(equal(True))

        with it("should list every practice CDD has, opened or not"):
            expect(sorted(self.session.practices)).to(equal(["bdd", "clean_engineering", "ddd", "stories", "ux"]))

        with it("should start with the practice enabled"):
            expect(self.opened.enabled).to(equal(True))

        with context("with a practice turned off"):
            with before.each:
                self.session.practice("ddd").enable(False)

            with it("should save it in the session's session.json"):
                saved = json.loads((self.session.record_folder / "session.json").read_text(encoding="utf-8"))
                expect(saved["practices"]["ddd"]["enabled"]).to(equal(False))

            with it("should read as turned off from the same folder later"):
                later = Sessions(self.repo).held.load(self.session.record_folder)
                expect(later.practice("ddd").enabled).to(equal(False))

            with it("should be left out of the practices the session works on"):
                expect(sorted(self.session.practices)).to(equal(["bdd", "clean_engineering", "stories", "ux"]))

            with it("should still be shown, turned off, so a toggle can turn it on again"):
                expect(data_of(self.session.show())["practices"]["ddd"]["enabled"]).to(equal(False))

            with it("should name its own fidelities, so a page can hide their files"):
                expect(data_of(self.session.show())["practices"]["ddd"]["fidelity_slugs"]).to(equal(["ddd-bounded-context", "ddd-model", "ddd-tactics"]))

            with it("should be shown in its practice's colour"):
                expect(data_of(self.session.show())["practices"]["ddd"]["colour"]).to(equal(self.session.practice("ddd").guidance.colour))

            with context("that is turned on again"):
                with before.each:
                    self.session.practice("ddd").enable(True)

                with it("should be among the practices the session works on"):
                    expect(sorted(self.session.practices)).to(equal(["bdd", "clean_engineering", "ddd", "stories", "ux"]))

        with context("with the practice default folders"):
            with it("should point that practice's folder at its default workspace folder under workpath"):
                expect(Path(self.opened.folder).resolve()).to(equal((self.work / "src").resolve()))

        with context("with a fidelity's outputs resolved for the session"):
            with before.each:
                self.stories = self.session.practice("stories")
                self.fidelity = self.stories.fidelities["story_map"]
                # Written by hand, as another process would, and read by the next call, which begins an answer of its own.
                self.write_overrides = lambda overrides: (
                    (self.session.record_folder / "session.json").write_text(
                        json.dumps({"name": "alpha", "outputs": overrides}), encoding="utf-8"
                    ),
                    Sessions.of_project(self.called),
                )

            with it("should put each format's file under the practice's root folder"):
                outputs = self.fidelity.declared.output_paths()
                expect(outputs["markdown"]).to(equal([(self.work / ".context" / "story-map.md").resolve().as_posix()]))

            with context("whose validation reports its session output keeps"):
                with it("should save a new report in the session's reports folder"):
                    expect(self.fidelity.session_output.validation_reports.new_path().parent).to(equal(self.session.reports_folder))

                with it("should name a new report by the fidelity's slug"):
                    expect(self.fidelity.session_output.validation_reports.new_path().name).to(contain("stories-story-map-"))

                with it("should list the reports saved there"):
                    saved = self.fidelity.session_output.validation_reports.new_path()
                    saved.write_text("# report\n", encoding="utf-8")
                    expect(self.fidelity.session_output.validation_reports.listed()).to(equal([saved]))

            with context("whose file is written"):
                with it("should be read by the session's file manager, though the practice's own folder is elsewhere"):
                    (self.work / ".context").mkdir()
                    (self.work / ".context" / "story-map.md").write_text("# Map\n", encoding="utf-8")
                    expect(self.session.session_files.file_manager.read(".context/story-map.md").text).to(equal("# Map\n"))

            with context("with session.json naming a root folder for the practice"):
                with before.each:
                    self.write_overrides({"stories": {"root": "docs/stories"}})

                with it("should use that root"):
                    outputs = self.fidelity.declared.output_paths()
                    expect(outputs["markdown"]).to(equal([(self.work / "docs/stories/.context/story-map.md").resolve().as_posix()]))

            with context("that a person chooses a folder as the practice's root"):
                with it("should write the practice's files under that folder"):
                    self.stories.keep_root(self.work / "docs")
                    expect(self.stories.folder).to(equal((self.work / "docs").resolve()))

                with it("should say the practice root is chosen"):
                    self.stories.keep_root(self.work / "docs")
                    expect(self.stories.is_root_chosen).to(equal(True))

                with context("that is then put back to the default"):
                    with it("should say the practice root is not chosen"):
                        self.stories.keep_root(self.work / "docs")
                        self.stories.use_default_root()
                        expect(self.stories.is_root_chosen).to(equal(False))

                with context("that then moves the session's workpath"):
                    with it("should still write the practice's files under that folder"):
                        self.stories.keep_root(self.work / "docs")
                        self.session.choose_workpath("work/inner")
                        expect(self.stories.folder).to(equal((self.work / "docs").resolve()))

            with context("that a person chooses a folder inside .context as the practice's root"):
                with before.each:
                    self.stories.keep_root(self.work / ".context" / "stories")

                with it("should write the practice's documents in that folder itself"):
                    outputs = self.fidelity.declared.output_paths()
                    expect(outputs["markdown"]).to(equal([(self.work / ".context" / "stories" / "story-map.md").resolve().as_posix()]))

                with it("should say the practice root is chosen"):
                    expect(self.stories.is_root_chosen).to(equal(True))

                with it("should write the scenarios in the story_tests beside that .context"):
                    outputs = self.stories.fidelities["scenarios"].declared.output_paths()
                    expect(outputs["markdown"]).to(equal([(self.work / "story_tests" / "{epic}/{sub-epic}/{story_snake}_story.test.md").resolve().as_posix()]))

                with context("and the scenarios' own root one epic's folder in story_tests"):
                    with it("should write the scenarios under that epic's folder only"):
                        self.write_overrides({"stories": {"root": ".context/stories", "scenarios": {"root": "story_tests/manage-orders"}}})
                        outputs = self.stories.fidelities["scenarios"].declared.output_paths()
                        expect(outputs["markdown"]).to(equal([(self.work / "story_tests" / "manage-orders" / "{sub-epic}/{story_snake}_story.test.md").resolve().as_posix()]))

                with context("and a person chooses one epic's folder for the scenarios"):
                    with it("should write the scenarios there and keep the story map in the practice's root"):
                        self.stories.of_fidelity(self.stories.fidelities.entries["scenarios"]).choose_root("work/story_tests/manage-orders")
                        scenarios = self.stories.fidelities["scenarios"].declared.output_paths()["markdown"]
                        story_map = self.fidelity.declared.output_paths()["markdown"]
                        expect((scenarios, story_map)).to(equal((
                            [(self.work / "story_tests" / "manage-orders" / "{sub-epic}/{story_snake}_story.test.md").resolve().as_posix()],
                            [(self.work / ".context" / "stories" / "story-map.md").resolve().as_posix()],
                        )))

                with context("and the scenarios' roots the folders of the sub-epics the session works on"):
                    with before.each:
                        self.write_overrides({"stories": {"root": ".context/stories", "scenarios": {"roots": ["story_tests/manage-orders/place-order", "story_tests/ship-orders/track-parcel"]}}})

                    with it("should write the scenarios under each sub-epic's folder, and nowhere else in story_tests"):
                        outputs = self.stories.fidelities["scenarios"].declared.output_paths()
                        expect(outputs["markdown"]).to(equal([
                            (self.work / "story_tests" / "manage-orders" / "place-order" / "{story_snake}_story.test.md").resolve().as_posix(),
                            (self.work / "story_tests" / "ship-orders" / "track-parcel" / "{story_snake}_story.test.md").resolve().as_posix(),
                        ]))

                    with it("should let the session's file manager read a story test in the second sub-epic"):
                        story_test = self.work / "story_tests" / "ship-orders" / "track-parcel" / "track-parcel.story.shared.py"
                        story_test.parent.mkdir(parents=True)
                        story_test.write_text("shared_stories = None\n", encoding="utf-8")
                        expect(self.session.session_files.in_root(story_test.resolve())).to(equal(True))

                with context("and a person adds a second sub-epic's folder to the scenarios' roots"):
                    with it("should write the scenarios under both folders"):
                        scenarios = self.stories.of_fidelity(self.stories.fidelities.entries["scenarios"])
                        scenarios.choose_root("work/story_tests/manage-orders/place-order")
                        scenarios.add_root("work/story_tests/ship-orders/track-parcel")
                        expect(self.stories.fidelities["scenarios"].declared.output_paths()["markdown"]).to(equal([
                            (self.work / "story_tests" / "manage-orders" / "place-order" / "{story_snake}_story.test.md").resolve().as_posix(),
                            (self.work / "story_tests" / "ship-orders" / "track-parcel" / "{story_snake}_story.test.md").resolve().as_posix(),
                        ]))

                with it("should let the session's file manager read the story tests in that story_tests"):
                    story_test = self.work / "story_tests" / "manage-orders" / "place-order" / "place-order.story.shared.py"
                    story_test.parent.mkdir(parents=True)
                    story_test.write_text("shared_stories = None\n", encoding="utf-8")
                    expect(self.session.session_files.file_manager.read("story_tests/manage-orders/place-order/place-order.story.shared.py").text).to(equal("shared_stories = None\n"))

            with context("with session.json naming a root folder for the fidelity too"):
                with before.each:
                    self.write_overrides({"stories": {"root": "docs/stories", "story_map": {"root": "docs/map"}}})

                with it("should prefer the fidelity's root"):
                    outputs = self.fidelity.declared.output_paths()
                    expect(outputs["drawio"]).to(equal([(self.work / "docs/map/.context/story-map.drawio").resolve().as_posix()]))

            with context("with session.json naming a file for a single-file output"):
                with before.each:
                    self.write_overrides({"stories": {"story_map": {"markdown": "our-map.md"}}})

                with it("should use that file name"):
                    outputs = self.fidelity.declared.output_paths()
                    expect(outputs["markdown"]).to(equal([(self.work / ".context" / "our-map.md").resolve().as_posix()]))

                with it("should keep the declared name for the other formats"):
                    outputs = self.fidelity.declared.output_paths()
                    expect(outputs["drawio"]).to(equal([(self.work / ".context" / "story-map.drawio").resolve().as_posix()]))

            with context("with session.json naming a file for a patterned output"):
                with before.each:
                    self.fidelity = self.stories.fidelities["scenarios"]
                    self.write_overrides({"stories": {"scenarios": {"python": "one-file.py"}}})

                with it("should keep the declared pattern"):
                    outputs = self.fidelity.declared.output_paths()
                    expect(outputs["python"][0]).to(contain("{story_snake}_story.test.py"))

        with context("with config.json practice_folders pointing a practice at the workpath"):
            with before.each:
                from harness.installation.context_config import ContextConfig

                ContextConfig(self.repo).update(practice_folders={"bdd": "."})
                Sessions(self.repo).switch("alpha")
                self.session = Sessions(self.called).current()
                self.opened = self.session.practice("bdd")

            with it("should point that practice's folder at the workpath"):
                expect(Path(self.opened.folder).resolve()).to(equal(self.work.resolve()))

        with context("with config.json default_formats naming diagram formats for every fidelity"):
            with before.each:
                from harness.installation.context_config import ContextConfig

                ContextConfig(self.repo).update(default_formats={"*": ["default", "drawio", "whiteboard"], "stories.scenarios": ["python"]})
                Sessions(self.repo).switch("alpha")
                self.stories = Sessions(self.called).current().practice("stories")

            with it("should choose a fidelity's own default and the diagram formats it writes until the session chooses"):
                expect(self.stories.fidelities["story_map"].session_output.chosen_formats).to(equal(["markdown", "drawio", "whiteboard"]))

            with it("should choose what the project names for that one fidelity over its defaults for every fidelity"):
                expect(self.stories.fidelities["scenarios"].session_output.chosen_formats).to(equal(["python"]))

            with it("should keep what the session chooses over the project's defaults"):
                chosen = self.stories.fidelities["story_map"].session_output.choose_format("whiteboard", False)
                expect(chosen.chosen_formats).to(equal(["markdown", "drawio"]))

        with context("with a root a person chose for the practice"):
            with before.each:
                self.custom = self.repo / "custom-bdd"
                self.custom.mkdir()
                self.session.practice("bdd").keep_root(self.custom)
                Sessions(self.repo).switch("alpha")
                self.session = Sessions(self.called).current()
                self.opened = self.session.practice("bdd")

            with it("should point that practice's folder at that folder"):
                expect(Path(self.opened.folder).resolve()).to(equal(self.custom.resolve()))

            with it("should keep that folder in the session's session.json and nowhere else"):
                expect((self.repo / ".context" / "practices.json").exists()).to(equal(False))


    with context("with harness/guidance as the tree for clean engineering, stories, and bdd"):
        with before.each:
            self.repo = Path(tempfile.mkdtemp())
            self.called = self.repo
            self.work = self.repo / "work"
            self.work.mkdir()
            self.tree = _REPO_ROOT / "harness" / "guidance"
            Sessions(self.repo).switch("alpha", self.work)
            self.session = Sessions(self.called).current()
            for practice in ("clean_engineering", "stories", "bdd"):
                self.session.practice(practice).keep_root(self.tree)
            Sessions(self.repo).switch("alpha")
            self.session = Sessions(self.called).current()
            started = time.perf_counter()
            self.opened = [self.session.practice(name) for name in ("clean_engineering", "stories", "bdd")]
            self.elapsed = time.perf_counter() - started

        with it("should point those practices' folders at harness/guidance"):
            roots = [Path(item.folder).resolve() for item in self.opened]
            expect(all(root == self.tree.resolve() for root in roots)).to(equal(True))

        with it("should open them within 5 seconds"):
            expect(self.elapsed < 5).to(equal(True))


with description("a session with no folder of its own, on a project inside its checkout") as self:
    with before.each:
        self.home = ExampleHome()
        self.repo = Path(tempfile.mkdtemp(prefix="session-root-")).resolve()
        (self.repo / ".git").mkdir()
        self.project = self.repo / "app"
        self.project.mkdir()
        self.session = ToolCall({}, self.project).session

    with after.each:
        shutil.rmtree(self.repo, ignore_errors=True)
        self.home.close()

    with it("should work in the whole repository"):
        expect(self.session.work_root).to(equal(self.repo))

    with it("should keep each practice's folder under its root"):
        stories = self.session.practice("stories")
        expect(stories.folder).to(equal(self.session.work_root / stories.guidance.default_workspace_folder))


with description("a session working in a folder of its own, holding an aggregate's files") as self:
    with before.each:
        self.home = ExampleHome()
        self.repo = Path(tempfile.mkdtemp(prefix="session-declared-")).resolve()
        (self.repo / ".git").mkdir()
        self.work = self.repo / "work"
        for name in ("client.ts", "helpers.ts"):
            (self.work / "sales" / "client").mkdir(parents=True, exist_ok=True)
            (self.work / "sales" / "client" / name).write_text("export class Client {}\n", encoding="utf-8")
        Sessions(self.repo).switch("alpha", self.work)
        self.model = Sessions(self.repo).current().practice("ddd").fidelities["model"]

    with after.each:
        shutil.rmtree(self.repo, ignore_errors=True)
        self.home.close()

    with it("should list the file named for its aggregate's folder"):
        expect([entry.path for entry in self.model.declared.files()["typescript"]]).to(equal(["work/sales/client/client.ts"]))

    with it("should find the declared file there"):
        expect(self.model.declared.has_output()).to(equal(True))


# Main works on the whole repository, so a practice nobody gave a folder lists its documents from every .context folder,
# as its patterns already find its tests anywhere.
with description("a session working on the whole repository, whose story map is in a module's .context folder") as self:
    with before.each:
        self.home = ExampleHome()
        self.repo = Path(tempfile.mkdtemp(prefix="session-whole-")).resolve()
        (self.repo / ".git").mkdir()
        story_map = self.repo / "harness" / ".context" / "stories" / "story-map.md"
        story_map.parent.mkdir(parents=True)
        story_map.write_text("# (E) Review Work\n", encoding="utf-8")
        session = ToolCall({}, self.repo).session
        session.session_files.branch_changes.files = lambda: set()
        self.story_map = session.practice("stories").fidelities["story_map"]

    with after.each:
        shutil.rmtree(self.repo, ignore_errors=True)
        self.home.close()

    with it("should list that story map as the story map's markdown"):
        expect([entry.path for entry in self.story_map.declared.files()["markdown"]]).to(equal(["harness/.context/stories/story-map.md"]))

    with context("with a thin slice beside it"):
        with before.each:
            (self.repo / "harness" / ".context" / "stories" / "thin-slice.md").write_text("# Thin Slice\n", encoding="utf-8")

        with it("should list the thin slice as the story map's thin slice"):
            expect([entry.path for entry in self.story_map.declared.files()["thin_slice"]]).to(contain("harness/.context/stories/thin-slice.md"))

    with context("with the project's config naming the repository's own folder for stories"):
        with before.each:
            (self.repo / ".context" / "config.json").parent.mkdir(exist_ok=True)
            (self.repo / ".context" / "config.json").write_text('{"practice_folders": {"stories": "."}}', encoding="utf-8")
            session = ToolCall({}, self.repo).session
            session.session_files.branch_changes.files = lambda: set()
            self.story_map = session.practice("stories").fidelities["story_map"]

        with it("should still list that story map as the story map's markdown"):
            expect([entry.path for entry in self.story_map.declared.files()["markdown"]]).to(equal(["harness/.context/stories/story-map.md"]))


# A fidelity that declares a folder per module, as Clean Engineering's code does with ``{module}/``, lists the code the
# session's branch changed; git is the boundary, so the branch's changes are given, not read.
with description("a session whose branch changed code in the folder it works in") as self:
    with before.each:
        self.home = ExampleHome()
        self.repo = Path(tempfile.mkdtemp(prefix="session-code-")).resolve()
        (self.repo / ".git").mkdir()
        self.work = self.repo / "work"
        changed = [
            self.work / "orders" / "order.py",
            self.work / "orders" / "order_view.tsx",
            self.work / "orders" / "notes.md",
            self.work / "orders" / "order_spec.py",
            self.work / "orders" / "order-view.spec.tsx",
            self.repo / "elsewhere.py",
        ]
        for file in changed:
            file.parent.mkdir(parents=True, exist_ok=True)
            file.write_text("x\n", encoding="utf-8")
        Sessions(self.repo).switch("alpha", self.work)
        session = Sessions(self.repo).current()
        session.session_files.branch_changes.files = lambda: {file.resolve() for file in changed}
        self.code = session.practice("clean_engineering").fidelities["code"]

    with after.each:
        shutil.rmtree(self.repo, ignore_errors=True)
        self.home.close()

    with it("should list the changed Python under its folder as the code's Python"):
        expect([entry.path for entry in self.code.declared.files()["python"]]).to(equal(["work/orders/order.py"]))

    with it("should list the changed TypeScript, components included, as the code's TypeScript"):
        expect([entry.path for entry in self.code.declared.files()["typescript"]]).to(equal(["work/orders/order_view.tsx"]))

    # Specs and tests are the acceptance tests' and the development specs' files, not production code.
    with it("should leave the changed specs out of the code"):
        listed = [entry.path for entries in self.code.declared.files().values() for entry in entries]
        expect(listed).not_to(contain("work/orders/order_spec.py"))


# UX's front-end code is reviewed against the screens it was built from: its view code is Clean Engineering's code to
# review, so the files a person reviews for it are the IA's and the mockup's, the design canvas opening at its link.
with description("a session whose UX work has an information architecture, a published design canvas, and view code") as self:
    with before.each:
        self.home = ExampleHome()
        self.repo = Path(tempfile.mkdtemp(prefix="session-ux-")).resolve()
        (self.repo / ".git").mkdir()
        self.work = self.repo / "work"
        canvas = self.work / "design-canvas"
        written = {
            self.work / "checkout" / ".context" / "information-architecture.drawio": "<mxfile/>",
            canvas / "version-1" / "project" / "canvas.json": "{}",
            canvas / "versions.json": json.dumps({"version-1": "https://claude.ai/artifact/checkout-canvas"}),
            self.work / "checkout" / "OrderView.tsx": "export function OrderView() {}",
        }
        for file, text in written.items():
            file.parent.mkdir(parents=True, exist_ok=True)
            file.write_text(text, encoding="utf-8")
        Sessions(self.repo).switch("alpha", self.work)
        self.front_end_code = Sessions(self.repo).current().practice("ux").fidelities["front_end_code"]

    with after.each:
        shutil.rmtree(self.repo, ignore_errors=True)
        self.home.close()

    with it("should review the information architecture's diagram"):
        expect([entry.path for entry in self.front_end_code.declared.files_to_review()["drawio"]]).to(contain("work/checkout/.context/information-architecture.drawio"))

    with it("should review the design canvas at the link it is published at"):
        expect([(entry.path, entry.link) for entry in self.front_end_code.declared.files_to_review()["claude_design"]]).to(
            equal([("work/design-canvas/version-1/project/canvas.json", "https://claude.ai/artifact/checkout-canvas")])
        )

    with it("should leave its view code to Clean Engineering's review"):
        reviewed = [entry.path for entries in self.front_end_code.declared.files_to_review().values() for entry in entries]
        expect(reviewed).not_to(contain("work/checkout/OrderView.tsx"))


# A whiteboard file opens the board in Claude it was published to, whose address is kept beside it (whiteboards.json);
# requested 2026-11-16: "whiteboard file entries don't open those files, they open the actual whiteboard".
with description("a session whose story map is drawn on a whiteboard") as self:
    with before.each:
        self.home = ExampleHome()
        self.repo = Path(tempfile.mkdtemp(prefix="session-whiteboard-")).resolve()
        (self.repo / ".git").mkdir()
        self.work = self.repo / "work"
        (self.work / ".context").mkdir(parents=True)
        (self.work / ".context" / "story-map.whiteboard").write_text("{}", encoding="utf-8")
        Sessions(self.repo).switch("alpha", self.work)
        self.story_map = Sessions(self.repo).current().practice("stories").fidelities["story_map"]

    with after.each:
        shutil.rmtree(self.repo, ignore_errors=True)
        self.home.close()

    with context("that was published to a board"):
        with before.each:
            BoardLinks.beside(self.work / ".context" / "story-map.whiteboard").record(self.work / ".context" / "story-map.whiteboard", "https://claude.ai/artifact/story-board")

        with it("should list the whiteboard file at its board's address"):
            expect([(entry.path, entry.link) for entry in self.story_map.declared.files()["whiteboard"]]).to(
                equal([("work/.context/story-map.whiteboard", "https://claude.ai/artifact/story-board")])
            )

    with context("that was never published"):
        with it("should list the whiteboard file at no address"):
            expect([entry.link for entry in self.story_map.declared.files()["whiteboard"]]).to(equal([""]))


# The chat bar's stage buttons, practice dots, and format chips, and the Files app's toggles, are one selection the
# session holds; every change raises its version, which a page waits on.
with description("a session's guidance selection") as self:
    with before.each:
        self.home = ExampleHome()
        self.repo = Path(tempfile.mkdtemp(prefix="session-guidance-")).resolve()
        (self.repo / ".git").mkdir()
        (self.repo / "work").mkdir()
        Sessions(self.repo).switch("alpha", self.repo / "work")
        self.session = Sessions(self.repo).current()

    with after.each:
        shutil.rmtree(self.repo, ignore_errors=True)
        self.home.close()

    with it("should name its repository, branch, and root, as a page heads them"):
        expect([self.session.repo_name, self.session.branch, self.session.root]).to(equal([self.repo.name, "alpha", str((self.repo / "work").resolve())]))

    with context("that nothing has selected yet"):
        with it("should have no stage chosen"):
            expect(self.session.guidance_selection().is_stage_chosen).to(equal(False))

        with it("should have every practice selected, as the session works on each until one is turned off"):
            expect(all(practice.is_selected for practice in self.session.guidance_selection().practices)).to(equal(True))

    # Requested 2026-11-16: "make sure design canvas is a filter option for UX".
    with context("that has Specification and UX selected"):
        with it("should offer the canvas format, the design canvas the UX mockup writes"):
            selected = self.session.update_guidance_selection(stages=["specification"], practices=["ux"])
            expect([(format.label, format.formats) for format in selected.formats if format.label == "canvas"]).to(equal([("canvas", ["claude_design"])]))

    with context("that has Discovery and Stories selected"):
        with before.each:
            self.selected = self.session.update_guidance_selection(stages=["discovery"], practices=["stories"])

        with it("should cover Stories' Discovery fidelity alone"):
            expect(self.selected.fidelities).to(equal(["stories-story-map"]))

        with it("should turn every other practice off for the session"):
            expect(self.session.practice("ddd").enabled).to(equal(False))

        with it("should raise the version once"):
            expect(self.selected.version).to(equal(1))

        with it("should keep the stages for the next read"):
            expect([stage.name for stage in Sessions(self.repo).current().guidance_selection().stages if stage.is_selected]).to(equal(["discovery"]))

        with context("that has every stage turned off"):
            with before.each:
                self.selected = self.session.update_guidance_selection(stages=[])

            with it("should keep the stages chosen"):
                expect(self.selected.is_stage_chosen).to(equal(True))

            with it("should cover Stories' fidelities of every stage, as no stage filter"):
                expect(self.selected.fidelities).to(equal(["stories-story-map", "stories-scenarios", "stories-acceptance-tests"]))

        with context("that has every practice turned off"):
            with before.each:
                self.selected = self.session.update_guidance_selection(practices=[])

            with it("should cover every practice's Discovery fidelity, as no practice filter"):
                expect(self.selected.fidelities).to(equal(["stories-story-map", "ddd-bounded-context", "ux-ia", "clean-engineering-modules", "bdd-behavior"]))

    with context("that a page waits on at version 0"):
        with it("should answer at once once the selection is past it"):
            self.session.update_guidance_selection(stages=["discovery"])
            expect(self.session.guidance_selection_after(0).version).to(equal(1))

        with it("should answer as soon as another call changes the selection"):
            changer = threading.Timer(0.01, lambda: Sessions(self.repo).current().update_guidance_selection(stages=["specification"]))
            changer.start()
            answered = self.session.guidance_selection_after(0)
            changer.join()
            expect([stage.name for stage in answered.stages if stage.is_selected]).to(equal(["specification"]))


# (E) Open Work Session
# (S) Session --> Switch Session
with description("a session on an MCP host whose CDD_REPO is the CDD checkout, not the project"):
    with before.each:
        self.home = ExampleHome()
        self._prior_repo = os.environ.get("CDD_REPO")
        self._prior_project = os.environ.get("CDD_PROJECT")
        self.cdd = Path(tempfile.mkdtemp(prefix="cdd-checkout-"))
        (self.cdd / ".git").mkdir()
        Sessions(self.cdd).switch("overlay", Path.home())
        self.project = Path(tempfile.mkdtemp(prefix="cdd-project-"))
        (self.project / ".git").mkdir()
        os.environ["CDD_REPO"] = str(self.cdd)
        os.environ["CDD_PROJECT"] = str(self.project)

    with after.each:
        for key, prior in (("CDD_REPO", self._prior_repo), ("CDD_PROJECT", self._prior_project)):
            if prior is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = prior
        self.home.close()

    with context("with a session named on the project"):
        with before.each:
            Sessions(self.project).switch("beta", self.project)

        with it("should bind the project's session, not the CDD checkout's"):
            session = Sessions(self.project).current()
            expect(session.name).to(equal("beta"))
            expect(session.record_folder).to(equal(self.project.resolve() / ".sessions" / "beta"))
            expect(session.workpath).to(equal(self.project.resolve()))

        with it("should give the project's session folder"):
            expect(Sessions(self.project).current().record_folder).to(equal(self.project.resolve() / ".sessions" / "beta"))

        with it("should append log notes to the project's session log"):
            session = Sessions(self.project).current()
            session.append_log(ToolCall(request=ToolRequest(_chat_in(session, "project-chat"))), "project note", loop=1)
            log = (self.project / ".sessions" / "beta" / "session.log").read_text(encoding="utf-8")
            cdd_log = self.cdd / ".sessions" / "overlay" / "session.log"
            cdd_text = cdd_log.read_text(encoding="utf-8") if cdd_log.is_file() else ""
            expect("project note" in log and "project note" not in cdd_text).to(equal(True))

        with it("should mark loops on the project's session log"):
            session = Sessions(self.project).current()
            session.mark_loop(ToolCall(request=ToolRequest(_chat_in(session, "project-loop-chat"))))
            log = (self.project / ".sessions" / "beta" / "session.log").read_text(encoding="utf-8")
            expect("--- " in log).to(equal(True))

        with it("should close the project's session and leave the CDD checkout's current"):
            Sessions(self.project).current().close()
            expect(WorkState(self.project).session).to(equal(""))
            expect(WorkState(self.cdd).session).to(equal("overlay"))

        with it("should bind the project's session when the MCP host dispatches"):
            from harness.mcp.mcp_server import McpHost

            host = McpHost.from_refs(
                ("space.session.session:Session",),
                repo=str(self.cdd),
                project=str(self.project),
            )
            session = Sessions(self.project).current()
            transcript = _chat_in(session, "project-dispatch-chat").transcript
            host.dispatch("session.mark_loop", {"session": session.session_file_from_project, **_chat_arguments("project-dispatch-chat", transcript)})
            log = (self.project / ".sessions" / "beta" / "session.log").read_text(encoding="utf-8")
            expect("tool session.mark_loop" in log).to(equal(True))

    with context("with no session named on the project"):
        with it("should be in the main session"):
            expect(Sessions(self.project).current().name).to(equal("main"))

        with it("should keep the main session in the project's main session folder"):
            expect(Sessions(self.project).current().record_folder).to(equal(self.project.resolve() / ".sessions" / "main"))

        with it("should work on the whole repository"):
            expect(Sessions(self.project).current().workpath).to(equal(self.project.resolve()))

        with it("should give the project's main session folder"):
            expect(Sessions(self.project).current().record_folder).to(equal(self.project.resolve() / ".sessions" / "main"))

        with it("should leave the session unnamed in .sessions/session.json"):
            Sessions(self.project).current()
            expect(WorkState(self.project).session).to(equal(""))


with description("a session switched to without a name"):
    with before.each:
        self.home = ExampleHome()

    with after.each:
        self.home.close()

    with context("with nothing saved in .sessions/session.json"):
        with before.each:
            self.repo = Path(tempfile.mkdtemp())
            self.called = self.repo

        with after.each:
            shutil.rmtree(self.repo, ignore_errors=True)

        with it("should refuse to switch"):
            expect(lambda: Sessions(self.repo).switch()).to(raise_error(SessionNameRequiredError))




with description("a session read for a board") as self:
    with after.each:
        self.home.close()

    with before.each:
        self.home = ExampleHome()
        self.repo = Path(tempfile.mkdtemp(prefix="session-board-"))
        (self.repo / ".git").mkdir()
        Sessions(self.repo).switch("alpha", self.repo)
        Sessions(self.repo).create("beta", self.repo, title="Beta")
        self.beta = Sessions(self.repo).held.load(self.repo / ".sessions" / "beta")

    with context("that was opened without becoming current"):
        with it("should leave the current session as it was"):
            expect(Sessions(self.repo).current().name).to(equal("alpha"))

        with it("should keep the title it was opened with"):
            expect(self.beta.title).to(equal("Beta"))

    with context("that is not the current session and marks a loop"):
        with before.each:
            self.beta.mark_loop(ToolCall())

        with it("should mark the loop in its own log"):
            expect((self.repo / ".sessions" / "beta" / "session.log").read_text(encoding="utf-8")).to(contain("--- 2"))

        with it("should leave the current session's log as it was"):
            expect((self.repo / ".sessions" / "alpha" / "session.log").read_text(encoding="utf-8")).not_to(contain("--- 2"))

    with context("that is not the current session and has closed"):
        with before.each:
            self.beta.close()

        with it("should leave the current session as it was"):
            expect(Sessions(self.repo).current().name).to(equal("alpha"))

    with context("that has moved to the closed sessions"):
        with before.each:
            self.moved = self.beta.folder.move_to_closed()

        with it("should keep its log and title in the new folder"):
            expect(self.moved.title).to(equal("Beta"))

        with it("should stay the same session"):
            expect(self.moved).to(be(self.beta))

        with it("should be kept in the closed sessions' folder"):
            expect(self.beta.record_folder).to(equal(self.repo.resolve() / ".sessions" / "_complete" / "beta"))

        with it("should write its handoffs into that folder"):
            expect(Path(self.beta.write_handoff("moved")).parent).to(equal(self.beta.work_folder))

        # A cache written for it before the move, or a folder Windows would not let go of, can leave its old folder behind.
        with context("with its old folder left among the open sessions"):
            with before.each:
                left = self.repo / ".sessions" / "beta"
                left.mkdir()
                (left / "progress-cache.json").write_text("{}", encoding="utf-8")

            with it("should be listed once, among the closed sessions"):
                listed = [session.record_folder for session in Sessions(self.repo).all() if session.name == "beta"]
                expect(listed).to(equal([self.repo.resolve() / ".sessions" / "_complete" / "beta"]))

    with context("that its sessions loaded"):
        with before.each:
            self.sessions = Sessions(self.repo)
            self.loaded = self.sessions.named("beta")

        with it("should hold those sessions"):
            expect(self.loaded.sessions).to(be(self.sessions))

        with it("should hold their repository"):
            expect(self.loaded.repo).to(be(self.sessions.repo))

        with it("should make each practice once"):
            expect(self.loaded.practices["stories"]).to(be(self.loaded.practices["stories"]))

        with it("should keep its decision records under the workpath it moves to"):
            (self.repo / "billing").mkdir()
            self.loaded.choose_workpath("billing")
            written = Path(self.loaded.write_cdr(slug="moved", content="# Moved"))
            expect(written.parent).to(equal(self.repo.resolve() / "billing" / ".context" / "cdr"))

    with context("whose checkout's files are listed"):
        with it("should list them through one file manager"):
            sessions = Sessions(self.repo)
            expect(sessions.file_manager).to(be(sessions.file_manager))

    with context("that keeps a file a person wrote, such as a started backlog item's idea"):
        with before.each:
            self.idea = self.repo / "gift-cards.md"
            self.idea.write_text("# Gift cards\n", encoding="utf-8")
            self.kept = self.beta.folder.keep_file(self.idea)

        with it("should hold the file in its session folder"):
            expect(self.kept).to(equal(self.beta.record_folder / "gift-cards.md"))

        with it("should leave nothing where the file was"):
            expect(self.idea.exists()).to(equal(False))


# One graph per session: two calls that first ask for it at once must not each make their own.
with description("a session whose graph two calls first ask for at once"):
    # The two calls race once, made slow on purpose, and every example reads what that one race left.
    with before.all:
        SPEC_RUN_HOME.ensure()
        self.repo = Path(tempfile.mkdtemp())
        session = Sessions(self.repo).current()
        self.original = GraphReads.open_saved
        self.made: list[object] = []
        opened = self.original

        def slow_open(reads, folder):
            # A slow read of the saved graph, so both calls are inside their first ask together.
            self.made.append(reads)
            time.sleep(0.2)
            return opened(reads, folder)

        GraphReads.open_saved = slow_open
        gate = threading.Barrier(2)
        self.graphs: list[object] = []

        def ask() -> None:
            gate.wait()
            self.graphs.append(session.graph)

        callers = [threading.Thread(target=ask) for _ in range(2)]
        for caller in callers:
            caller.start()
        for caller in callers:
            caller.join()

        GraphReads.open_saved = self.original

    with after.all:
        shutil.rmtree(self.repo, ignore_errors=True)

    with it("should give both calls the one graph"):
        expect(self.graphs[0]).to(be(self.graphs[1]))

    with it("should make the graph once"):
        expect(len(self.made)).to(equal(1))
