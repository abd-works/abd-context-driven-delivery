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

from harness.guidance.guidance import PracticeGuidance
from harness.guidance_actions import GuidanceAction
from harness.hooks.hook_server import HookPayload
from harness.agent_tools.tool_call import ToolCall
from harness.mcp.mcp_server import McpServer
from space.repo.repo import Repo
from space.session import Session, Sessions
from harness.agent_tools.chat_pointer import ChatPointer
from space.session.practice_session_output import PracticeRootInContextError
from space.session.session_log import LoopNotFoundError
from space.session.sessions import SessionNameRequiredError
from space.work_state import WorkState


def _attach_mandatory_chat(session: Session, work: Path, chat_id: str = "spec-chat") -> Path:
    chats = session.session_path / "chats"
    chats.mkdir(parents=True, exist_ok=True)
    transcript = chats / f"{chat_id}.md"
    transcript.write_text("spec transcript\n", encoding="utf-8")
    session.chat = ChatPointer.of(chat_id, transcript, "1")
    return transcript


def _chat_arguments(chat_id: str, transcript: Path) -> dict[str, str]:
    """The chat fields an MCP call from chat_id sends with its own arguments."""
    return {"conversation_id": chat_id, "transcript_path": str(transcript), "transcript_lines": "1"}


# (E) Open Work Session
# (E) Hold Process Session
with description("a session"):
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
                expect(self.event().session.graph.every_practice["stories"]).to(be(self.event().session.practice("stories").guidance))

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
            expect(ToolCall({}, self.repo).session.session_path).to(equal(HookPayload({"cwd": str(self.repo)}).session.session_path))

        with it("should agree with the session opened for the project without a call"):
            expect(ToolCall({}, self.repo).session.session_path).to(equal(ToolCall.session_in(self.repo).session_path))

        with context("with a named session open"):
            with before.each:
                self.work = self.repo / "work"
                self.work.mkdir()
                Sessions(self.repo).switch("alpha", self.work)

            with it("should be that session"):
                expect(ToolCall({}, self.repo).session.session_path).to(equal(self.repo.resolve() / ".sessions" / "alpha"))

            with it("should be that session when the call's project is the workpath folder"):
                expect(ToolCall({}, self.work).session.name).to(equal("alpha"))

            with it("should give each call its own copy, so one call's practices never reach another"):
                expect(ToolCall({}, self.repo).session is ToolCall({}, self.repo).session).to(equal(False))

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
            expect(session.session_path).to(equal(self.repo.resolve() / ".sessions" / "alpha"))

        with it("should write --- 1 as the first line of a new session.log"):
            first = (Sessions(self.called).current().session_path / "session.log").read_text(encoding="utf-8").splitlines()[0]
            expect("--- 1" in first).to(equal(True))

        with it("should leave practices empty until a practice is asked for"):
            expect(Sessions(self.called).current().opened_practices).to(equal([]))

        with it("should record the name in repo sessions session.json"):
            state = json.loads((self.repo / ".sessions" / "session.json").read_text(encoding="utf-8"))
            expect(state.get("session")).to(equal("alpha"))

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

        with it("should remove the session from repo sessions session.json"):
            state = json.loads((self.repo / ".sessions" / "session.json").read_text(encoding="utf-8"))
            expect("session" in state).to(equal(False))

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
                expect(session.session_path).to(equal(self.repo.resolve() / ".sessions" / "alpha"))

            with it("should use the workpath stored on that session"):
                expect(Sessions(self.called).current().workpath).to(equal(self.work.resolve()))

            with it("should leave practices empty until a practice is asked for"):
                expect(Sessions(self.called).current().opened_practices).to(equal([]))

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

        # The board reads the main checkout's .sessions, so a ticket's log written in its worktree never showed there.
        with context("from a linked worktree of the checkout whose board holds it"):
            with before.each:
                self.worktree = Path(tempfile.mkdtemp())
                worktree_git = self.repo / ".git" / "worktrees" / "alpha"
                worktree_git.mkdir(parents=True)
                (worktree_git / "commondir").write_text("../..\n", encoding="utf-8")
                (self.worktree / ".git").write_text(f"gitdir: {worktree_git}\n", encoding="utf-8")
                self.called = self.worktree
                Sessions(self.worktree).switch("alpha")

            with after.each:
                shutil.rmtree(self.worktree, ignore_errors=True)

            with it("should log into the ticket's folder on the board"):
                expect(Sessions(self.called).current().session_path).to(equal(self.repo.resolve() / ".sessions" / "alpha"))

            with it("should keep the worktree's own choice of session in the worktree"):
                expect(WorkState(self.worktree).session).to(equal("alpha"))

            with context("that switches to the main session"):
                with before.each:
                    Sessions(self.worktree).switch("main")

                with it("should log into the worktree's own main session"):
                    expect(Sessions(self.called).current().session_path).to(equal(self.worktree.resolve() / ".sessions" / "main"))

        with context("with a repo path"):
            with before.each:
                self.instructions = Sessions(self.repo).switch("alpha")

            with it("should keep logging under that repo at sessions and the name"):
                expect(Sessions(self.called).current().session_path).to(
                    equal(self.repo.resolve() / ".sessions" / "alpha")
                )

            with it("should read the workpath from that session"):
                expect(Sessions(self.called).current().workpath).to(equal(self.work.resolve()))

        with context("when repo session.json current changes on disk"):
            with it("should reload the named session instead of keeping stale memory"):
                Sessions(self.repo).switch("alpha", self.work)
                Sessions(self.repo).switch("beta", self.work)
                expect(Sessions(self.called).current().name).to(equal("beta"))
                pointer = self.repo / ".sessions" / "session.json"
                pointer.write_text('{"session": "alpha"}', encoding="utf-8")
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
            log = (Sessions(self.called).current().session_path / "session.log").read_text(encoding="utf-8")
            expect("--- 1" in log).to(equal(True))

        with it("should mark loops via mark_loop when a session is current"):
            expect(Sessions(self.called).current().mark_loop()).to(equal("2"))

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
            expect(Sessions(self.called).current().mark_loop()).to(equal("3"))

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
            Sessions(self.called).current().log.failure(self.failure)
            err = (Sessions(self.called).current().session_path / "session.err").read_text(encoding="utf-8")
            expect("boom" in err).to(equal(True))

        with it("should point the session.log line at that session.err file"):
            Sessions(self.called).current().log.failure(self.failure)
            log = (Sessions(self.called).current().session_path / "session.log").read_text(encoding="utf-8")
            expect("session.err" in log).to(equal(True))

        with it("should append a second failure without overwriting session.err"):
            session = Sessions(self.called).current()
            session.log.failure(RuntimeError("first"))
            session.log.failure(RuntimeError("second"))
            err = (session.session_path / "session.err").read_text(encoding="utf-8")
            expect("first" in err and "second" in err).to(equal(True))

    with context("that records MCP tool failures on dispatch"):
        with before.each:
            self.repo = Path(tempfile.mkdtemp())
            self.called = self.repo
            self.work = self.repo / "work"
            self.work.mkdir()
            Sessions(self.repo).switch("alpha", self.work)
            self.session = Sessions(self.called).current()
            _attach_mandatory_chat(self.session, self.work, "mcp-fail-chat")

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
            log = (self.session.session_path / "session.log").read_text(encoding="utf-8")
            err = (self.session.session_path / "session.err").read_text(encoding="utf-8")
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
            self.transcript = _attach_mandatory_chat(self.session, self.work, "mcp-dispatch-chat")

        with it("should append a tool line when the MCP host invokes an agent tool"):
            from harness.mcp.mcp_server import McpHost

            host = McpHost.from_refs(
                ("space.session.session:Session",),
                repo=str(self.repo),
                project=str(self.repo),
            )
            host.dispatch("session.mark_loop", {"session": self.session.session_file_from_project, **_chat_arguments("mcp-dispatch-chat", self.transcript)}, self.called)
            log = (self.session.session_path / "session.log").read_text(encoding="utf-8")
            expect("tool session.mark_loop" in log and "mcp-dispatch-chat" in log).to(equal(True))

    with context("that records a loop correction note"):
        with before.each:
            self.repo = Path(tempfile.mkdtemp())
            self.called = self.repo
            self.work = self.repo / "work"
            self.work.mkdir()
            Sessions(self.repo).switch("alpha", self.work)
            self.session = Sessions(self.called).current()
            _attach_mandatory_chat(self.session, self.work, "note-chat")

        with it("should append a note line with message paths and chat pointer"):
            touched = self.work / "repo.py"
            self.session.log.note("close_branch must push merge checkout main", [touched])
            log = (self.session.session_path / "session.log").read_text(encoding="utf-8")
            expect(
                "note close_branch must push merge checkout main" in log
                and str(touched) in log
                and "note-chat" in log
            ).to(equal(True))

        with it("should append via append_log with loop number and chat fields"):
            _attach_mandatory_chat(self.session, self.work, "append-chat")
            result = self.session.append_log("correction recorded", loop=1, paths=[str(self.work / "session.py")])
            log = (self.session.session_path / "session.log").read_text(encoding="utf-8")
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
            _attach_mandatory_chat(self.session, self.work)
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
                self.bare_session.log.action("sketch", [work / "x.py"])

            with it("should log the action as from no chat"):
                log = (self.bare_session.session_path / "session.log").read_text(encoding="utf-8")
                expect(log.rstrip().endswith("x.py no-chat")).to(equal(True))

            with it("should write nothing to session.err"):
                expect((self.bare_session.session_path / "session.err").exists()).to(equal(False))

            with context("with the server's environment naming a chat"):
                with before.each:
                    transcript = Path(tempfile.mkdtemp()) / "other.jsonl"
                    transcript.write_text("{}\n", encoding="utf-8")
                    os.environ.update(CDD_CONVERSATION_ID="other-chat", CDD_TRANSCRIPT_PATH=str(transcript))
                    self.bare_session.log.action("generate", [Path("y.py")])

                with after.each:
                    os.environ.pop("CDD_CONVERSATION_ID", None)
                    os.environ.pop("CDD_TRANSCRIPT_PATH", None)

                with it("should still log the action as from no chat, not the chat the environment names"):
                    log = (self.bare_session.session_path / "session.log").read_text(encoding="utf-8")
                    expect(log.rstrip().endswith("y.py no-chat")).to(equal(True))

        with context("with paths passed in"):
            with it("should append a timestamped line that names the action and the path"):
                self.session.log.action("sketch", [self.edited])
                log = (self.session.session_path / "session.log").read_text(encoding="utf-8")
                expect("sketch" in log and str(self.edited) in log and "T" in log).to(equal(True))

        with context("with a graph node known for the practice"):
            with before.each:
                self.session.practice("bdd")

            with it("should name the practice graph root"):
                self.session.log.action("sketch", [self.edited])
                log = (self.session.session_path / "session.log").read_text(encoding="utf-8")
                expect("bdd" in log).to(equal(True))

        with context("with rules injected from a inject rules hook"):
            with before.each:
                rules = self.session.practice("bdd").fidelities["development"].rules
                self.session.log.injected_rules.note(rules, str(self.edited))

            with it("should log that practice, fidelity, rule, and matched file"):
                self.session.log.action("sketch", [self.edited])
                log = (self.session.session_path / "session.log").read_text(encoding="utf-8")
                expect(
                    "bdd development hierarchy-preservation" in log and str(self.edited) in log
                ).to(equal(True))

            with it("should omit a rule that was not injected"):
                self.session.log.action("sketch", [self.edited])
                log = (self.session.session_path / "session.log").read_text(encoding="utf-8")
                expect("stories-story-map" in log).to(equal(False))

        with context("with a chat transcript"):
            with it("should point at the chat id, the transcript file, and the line numbers"):
                transcript = self.work / "chat.md"
                transcript.write_text("hello\n", encoding="utf-8")
                self.session.log.note_chat(ChatPointer("chat-1", transcript, "1-2"))
                self.session.log.action("sketch", [self.edited])
                log = (self.session.session_path / "session.log").read_text(encoding="utf-8")
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
            self.session_path = Sessions(self.called).current().session_path

        with it("should read the repo path and the workpath from that session"):
            session = Sessions(self.repo).load(self.session_path)
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
    with context("that is opened"):
        with before.each:
            self.repo = Path(tempfile.mkdtemp())
            self.called = self.repo
            self.work = self.repo / "work"
            self.work.mkdir()
            Sessions(self.repo).switch("alpha", self.work)
            self.first = Sessions(self.called).current().log.next_loop()
            self.second = Sessions(self.called).current().log.next_loop()

        with it("should take the next loop number"):
            expect(self.second.number).to(equal(self.first.number + 1))

        with it("should append the loop marker to session.log"):
            log = (Sessions(self.called).current().session_path / "session.log").read_text(encoding="utf-8")
            expect(f"--- {self.second.number}" in log).to(equal(True))

    with context("that has log entries"):
        with before.each:
            self.repo = Path(tempfile.mkdtemp())
            self.called = self.repo
            self.work = self.repo / "work"
            self.work.mkdir()
            Sessions(self.repo).switch("alpha", self.work)
            self.session = Sessions(self.called).current()
            _attach_mandatory_chat(self.session, self.work, "loop-chat")
            self.opened = self.session.log.next_loop()
            self.session.log.action("sketch", [self.work / "cart.py"])

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
            self.session.log.note_chat(ChatPointer(chat_id, chat, "1"))
            self.session.log.action("validate", [self.work / "cart.py"])
            body = Sessions(self.called).current().read_loop(self.opened.number)
            expect("loop read" in body and "validate" in body).to(equal(True))


# (E) Open Work Session
# (E) Record Session Log
with description("an action"):
    with before.each:
        self.repo = Path(tempfile.mkdtemp())
        self.called = self.repo
        self.work = self.repo / "work"
        self.work.mkdir()
        Sessions(self.repo).switch("alpha", self.work)
        self.session = Sessions(self.called).current()
        _attach_mandatory_chat(self.session, self.work, "action-chat")

    # (S) Session --> Record Validation Run
    with context("that calls validate"):
        with before.each:
            self.practice = self.session.practice("bdd")

        with context("with a practice and a fidelity"):
            with it("should log that practice and that fidelity"):
                self.session.log.validation(self.practice, [])
                log = (self.session.session_path / "session.log").read_text(encoding="utf-8")
                expect("Bdd" in log and "behavior" in log).to(equal(True))

        with context("with a violation"):
            with it("should log the rule, the synopsis, and the correction"):
                self.session.log.validation(self.practice, 
                    ["hierarchy-preservation synopsis: flattened tree correction: keep the nesting"],
                )
                log = (self.session.session_path / "session.log").read_text(encoding="utf-8")
                expect("hierarchy-preservation" in log and "synopsis" in log and "correction" in log).to(
                    equal(True)
                )

    # (S) Session --> Record Session Action
    with context("that names an action"):
        with it("should log that action"):
            action = GuidanceAction(self.session)
            action._work_on("a note")
            action.run(lambda item: None, action="sketch")
            log = (self.session.session_path / "session.log").read_text(encoding="utf-8")
            expect("sketch" in log).to(equal(True))

        with it("should log workpath and practice context for listed guidance"):
            from harness.guidance_actions import GuidanceAction

            action = GuidanceAction(self.session)
            action._work_on(["bdd"])
            action.run(lambda item: None, action="generate")
            log = (self.session.session_path / "session.log").read_text(encoding="utf-8")
            expect("generate" in log and str(self.work) in log and "bdd" in log).to(equal(True))

        with context("with MCP host session binding like session.switch"):
            with it("should log generate and validate with practice context"):
                import os

                from harness.mcp.mcp_server import McpServer
                from cdd_guidance.actions.validate.validate import Validate

                (self.repo / ".git").mkdir(exist_ok=True)
                os.environ["CDD_REPO"] = str(self.repo.resolve())
                os.environ["CDD_PROJECT"] = str(self.work.resolve())
                _attach_mandatory_chat(self.session, self.work, "mcp-host-chat")
                McpServer(repo=self.repo, project=self.work)
                action = GuidanceAction(self.session)
                action._work_on(["bdd"])
                action.run(lambda _item: None, action="generate")
                Validate(self.session).validate(["bdd"])
                log = (self.session.session_path / "session.log").read_text(encoding="utf-8")
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
                self.session.log.action("sketch", [edited])
                log = (self.session.session_path / "session.log").read_text(encoding="utf-8")
                expect("sample-rule-one" in log and str(edited) in log).to(equal(True))

    with context("that names no action"):
        with it("should leave session.log unchanged"):
            log_path = self.session.session_path / "session.log"
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
            expect(self.session.graph.every_practice["bdd"]).to(be(self.opened.guidance))

        with it("should know the session's graph"):
            expect(self.opened.guidance.graph).to(be(self.session.graph))

        with it("should be the same practice the next call in the session works with"):
            expect(Sessions.of_project(self.called).current().practice("bdd").guidance).to(be(self.opened.guidance))

        with it("should hold the practice it extends from the same session"):
            expect(self.session.practice("ddd").guidance.extended).to(be(self.session.practice("clean_engineering").guidance))

        with it("should open its graph on its workpath"):
            expect(self.session.graph.source_root_of(self.opened.guidance)).to(equal(str(self.work.resolve())))

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
                practice = reopened.every_practice["clean_engineering"]
                expect([node.name for node in reopened.nodes_of(practice)]).to(contain("Order"))

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
                saved = json.loads((self.session.session_path / "session.json").read_text(encoding="utf-8"))
                expect(saved["practices"]["ddd"]["enabled"]).to(equal(False))

            with it("should read as turned off from the same folder later"):
                later = Sessions(self.repo).load(self.session.session_path)
                expect(later.practices["ddd"].enabled).to(equal(False))

        with it("should leave the other practices unopened"):
            expect([item.name for item in self.session.opened_practices]).to(equal(["bdd"]))

        with context("with the practice default folders"):
            with it("should point that practice's folder at its default workspace folder under workpath"):
                expect(Path(self.opened.folder).resolve()).to(equal((self.work / "src").resolve()))

        with context("with a fidelity's outputs resolved for the session"):
            with before.each:
                self.stories = self.session.practice("stories")
                self.fidelity = self.stories.fidelities["story_map"]
                self.write_overrides = lambda overrides: (self.session.session_path / "session.json").write_text(
                    json.dumps({"name": "alpha", "outputs": overrides}), encoding="utf-8"
                )

            with it("should put each format's file under the practice's root folder"):
                outputs = self.fidelity.output_paths()
                expect(outputs["markdown"]).to(equal([(self.work / ".context" / "story-map.md").resolve().as_posix()]))

            with context("whose file is written"):
                with it("should be read by the session's file manager, though the practice's own folder is elsewhere"):
                    (self.work / ".context").mkdir()
                    (self.work / ".context" / "story-map.md").write_text("# Map\n", encoding="utf-8")
                    expect(self.session.session_files.file_manager.read(".context/story-map.md").text).to(equal("# Map\n"))

            with context("with session.json naming a root folder for the practice"):
                with before.each:
                    self.write_overrides({"stories": {"root": "docs/stories"}})

                with it("should use that root"):
                    outputs = self.fidelity.output_paths()
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

            with context("that a person chooses a .context folder as the practice's root"):
                with it("should refuse it, since the practice's documents already go in its root's .context"):
                    expect(lambda: self.stories.keep_root(self.work / ".context")).to(
                        raise_error(PracticeRootInContextError)
                    )

                with it("should name the practice and the folder it refused"):
                    try:
                        self.stories.keep_root(self.work / ".context")
                    except PracticeRootInContextError as refused:
                        expect((refused.practice, refused.root)).to(equal(("stories", self.work / ".context")))

            with context("with session.json naming a root folder for the fidelity too"):
                with before.each:
                    self.write_overrides({"stories": {"root": "docs/stories", "story_map": {"root": "docs/map"}}})

                with it("should prefer the fidelity's root"):
                    outputs = self.fidelity.output_paths()
                    expect(outputs["drawio"]).to(equal([(self.work / "docs/map/.context/story-map.drawio").resolve().as_posix()]))

            with context("with session.json naming a file for a single-file output"):
                with before.each:
                    self.write_overrides({"stories": {"story_map": {"markdown": "our-map.md"}}})

                with it("should use that file name"):
                    outputs = self.fidelity.output_paths()
                    expect(outputs["markdown"]).to(equal([(self.work / ".context" / "our-map.md").resolve().as_posix()]))

                with it("should keep the declared name for the other formats"):
                    outputs = self.fidelity.output_paths()
                    expect(outputs["drawio"]).to(equal([(self.work / ".context" / "story-map.drawio").resolve().as_posix()]))

            with context("with session.json naming a file for a patterned output"):
                with before.each:
                    self.fidelity = self.stories.fidelities["scenarios"]
                    self.write_overrides({"stories": {"scenarios": {"python": "one-file.py"}}})

                with it("should keep the declared pattern"):
                    outputs = self.fidelity.output_paths()
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

    with context("that a practice has not been invoked"):
        with before.each:
            self.session = Session(Sessions(Path(tempfile.mkdtemp())))

        with it("should omit that practice's entry"):
            expect(self.session.opened_practices).to(equal([]))

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
        self.repo = Path(tempfile.mkdtemp(prefix="session-root-")).resolve()
        (self.repo / ".git").mkdir()
        self.project = self.repo / "app"
        self.project.mkdir()
        self.session = ToolCall({}, self.project).session

    with after.each:
        shutil.rmtree(self.repo, ignore_errors=True)

    with it("should work in the whole repository"):
        expect(self.session.work_root).to(equal(self.repo))

    with it("should keep each practice's folder under its root"):
        stories = self.session.practice("stories")
        expect(stories.folder).to(equal(self.session.work_root / stories.guidance.default_workspace_folder))


with description("a session working in a folder of its own, holding an aggregate's files") as self:
    with before.each:
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

    with it("should list the file named for its aggregate's folder"):
        expect([entry.path for entry in self.model.files()["typescript"]]).to(equal(["work/sales/client/client.ts"]))

    with it("should find the declared file there"):
        expect(self.model.has_declared_output()).to(equal(True))


# (E) Open Work Session
# (S) Session --> Switch Session
with description("a session on an MCP host whose CDD_REPO is the CDD checkout, not the project"):
    with before.each:
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

    with context("with a session named on the project"):
        with before.each:
            Sessions(self.project).switch("beta", self.project)

        with it("should bind the project's session, not the CDD checkout's"):
            session = Sessions(self.project).current()
            expect(session.name).to(equal("beta"))
            expect(session.session_path).to(equal(self.project.resolve() / ".sessions" / "beta"))
            expect(session.workpath).to(equal(self.project.resolve()))

        with it("should give the project's session folder"):
            expect(Sessions(self.project).current().session_path).to(equal(self.project.resolve() / ".sessions" / "beta"))

        with it("should append log notes to the project's session log"):
            session = Sessions(self.project).current()
            _attach_mandatory_chat(session, self.project, "project-chat")
            session.append_log("project note", loop=1)
            log = (self.project / ".sessions" / "beta" / "session.log").read_text(encoding="utf-8")
            cdd_log = self.cdd / ".sessions" / "overlay" / "session.log"
            cdd_text = cdd_log.read_text(encoding="utf-8") if cdd_log.is_file() else ""
            expect("project note" in log and "project note" not in cdd_text).to(equal(True))

        with it("should mark loops on the project's session log"):
            session = Sessions(self.project).current()
            _attach_mandatory_chat(session, self.project, "project-loop-chat")
            session.mark_loop()
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
            transcript = _attach_mandatory_chat(session, self.project, "project-dispatch-chat")
            host.dispatch("session.mark_loop", {"session": session.session_file_from_project, **_chat_arguments("project-dispatch-chat", transcript)})
            log = (self.project / ".sessions" / "beta" / "session.log").read_text(encoding="utf-8")
            expect("tool session.mark_loop" in log).to(equal(True))

    with context("with no session named on the project"):
        with it("should be in the main session"):
            expect(Sessions(self.project).current().name).to(equal("main"))

        with it("should keep the main session in the project's main session folder"):
            expect(Sessions(self.project).current().session_path).to(equal(self.project.resolve() / ".sessions" / "main"))

        with it("should work on the whole repository"):
            expect(Sessions(self.project).current().workpath).to(equal(self.project.resolve()))

        with it("should give the project's main session folder"):
            expect(Sessions(self.project).current().session_path).to(equal(self.project.resolve() / ".sessions" / "main"))

        with it("should leave the session unnamed in .sessions/session.json"):
            Sessions(self.project).current()
            expect(WorkState(self.project).session).to(equal(""))


with description("a session switched to without a name"):
    with context("with a branch saved in .sessions/session.json"):
        with before.each:
            self.repo = Path(tempfile.mkdtemp())
            self.called = self.repo
            WorkState(self.repo).branch_name = "feature/space-battle"
            Sessions(self.repo).switch(workpath=self.repo)

        with after.each:
            shutil.rmtree(self.repo, ignore_errors=True)

        with it("should take its name from the branch"):
            expect(Sessions(self.repo).current().name).to(equal("feature-space-battle"))

        with it("should create the session folder"):
            expect((self.repo / ".sessions" / "feature-space-battle" / "session.json").is_file()).to(equal(True))

        with it("should save the session in .sessions/session.json"):
            expect(WorkState(self.repo).session).to(equal("feature-space-battle"))

        with it("should keep the saved branch"):
            expect(WorkState(self.repo).branch_name).to(equal("feature/space-battle"))

    with context("with nothing saved in .sessions/session.json"):
        with before.each:
            self.repo = Path(tempfile.mkdtemp())
            self.called = self.repo

        with after.each:
            shutil.rmtree(self.repo, ignore_errors=True)

        with it("should refuse to switch"):
            expect(lambda: Sessions(self.repo).switch()).to(raise_error(SessionNameRequiredError))




with description("a session read for a board") as self:
    with before.each:
        self.repo = Path(tempfile.mkdtemp(prefix="session-board-"))
        (self.repo / ".git").mkdir()
        Sessions(self.repo).switch("alpha", self.repo)
        Sessions(self.repo).create("beta", self.repo, title="Beta")
        self.beta = Sessions(self.repo).load(self.repo / ".sessions" / "beta")

    with context("that was opened without becoming current"):
        with it("should leave the current session as it was"):
            expect(Sessions(self.repo).current().name).to(equal("alpha"))

        with it("should keep the title it was opened with"):
            expect(self.beta.title).to(equal("Beta"))

    with context("that is not the current session and marks a loop"):
        with before.each:
            self.beta.mark_loop()

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
            self.moved = self.beta.move_to_closed()

        with it("should keep its log and title in the new folder"):
            expect(self.moved.title).to(equal("Beta"))

        with it("should stay the same session"):
            expect(self.moved).to(be(self.beta))

        with it("should be kept in the closed sessions' folder"):
            expect(self.beta.session_path).to(equal(self.repo.resolve() / ".sessions" / "_complete" / "beta"))

        with it("should write its handoffs into that folder"):
            expect(Path(self.beta.write_handoff("moved")).parent).to(equal(self.beta.session_path))

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
            self.kept = self.beta.keep_file(self.idea)

        with it("should hold the file in its session folder"):
            expect(self.kept).to(equal(self.beta.session_path / "gift-cards.md"))

        with it("should leave nothing where the file was"):
            expect(self.idea.exists()).to(equal(False))
