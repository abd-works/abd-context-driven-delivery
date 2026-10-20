"""BDD development — a session opens each practice with its graph."""
import json
import os
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

from expects import be_a, contain, equal, expect
from mamba import after, before, context, description, it

from harness.guidance.guidance import PracticeGuidance
from harness.guidance_actions import GuidanceAction
from harness.hooks.hook_server import HandlerCatalog, HookPayload, HookServer
from harness.mcp.mcp_server import McpServer
from space.session import Session


def _bind_mandatory_chat(session: Session, work: Path, chat_id: str = "spec-chat") -> Path:
    chats = session.session_path / "chats"
    chats.mkdir(parents=True, exist_ok=True)
    transcript = chats / f"{chat_id}.md"
    transcript.write_text("spec transcript\n", encoding="utf-8")
    os.environ["CDD_CONVERSATION_ID"] = chat_id
    os.environ["CDD_TRANSCRIPT_PATH"] = str(transcript)
    os.environ["CDD_TRANSCRIPT_LINES"] = "1"
    return transcript


# (E) Open Work Session
# (E) Hold Process Session
with description("a session"):
    # (S) Session --> Reset Process Session
    with context("that has been reset"):
        with before.each:
            self.session = Session()
            self.prior = self.session.practice("stories")
            self.session.reset()

        with it("should open that practice again on the next ask"):
            expect(self.session.practice("stories") is self.prior).to(equal(False))

    # (S) Session --> Persist Hook Session
    with context("that the hook server holds"):
        with before.each:
            Session._current = None
            self.root = Path(tempfile.mkdtemp())
            self.server = HookServer(self.root, HandlerCatalog([], self.root))  # pyright: ignore[reportUndefinedVariable]

        with it("should return no named session until one is open on the repo"):
            expect(self.server.session).to(equal(None))

        with it("should keep one in-memory session object for new and switch"):
            expect(Session._slot()).to(be_a(Session))

        with it("should be the same object across hook runs"):
            from harness.hooks.hook_daemon import HookDaemon

            marker = self.root / ".cursor" / "hook-server.json"
            original = HookServer.state_path
            HookServer.state_path = classmethod(lambda cls, repo: marker)
            try:
                thread = threading.Thread(
                    target=HookDaemon().serve,
                    args=(self.root,),
                    kwargs={"inner": self.server},
                    daemon=True,
                )
                thread.start()
                client = HookServer(self.root)._wait_until_connected(marker)
                first = self.server.session
                client.handle_stdin(b'{"hook_event_name":"stop"}')
                client.handle_stdin(b'{"hook_event_name":"stop"}')
                expect(self.server.session is first).to(equal(True))
            finally:
                HookServer.state_path = original

        with context("with a named session open on that repo"):
            with before.each:
                self.work = self.root / "work"
                self.work.mkdir()
                Session.new("alpha", self.work, self.root)
                self.server.session = Session.current(self.root)
                self.session = self.server.session

            with it("should open that practice's guideline"):
                expect(self.session.practice("stories").guideline).to(be_a(PracticeGuidance))

            with it("should open that practice's graph with the guideline"):
                opened = self.session.practice("stories")
                expect(opened.graph.practices["stories"].name).to(equal("stories"))

            with it("should return the same practice across hook runs"):
                first = self.session.practice("stories")
                self.server.dispatch(HookPayload({"hook_event_name": "stop"}))
                self.server.dispatch(HookPayload({"hook_event_name": "stop"}))
                expect(self.server.session.practice("stories") is first).to(equal(True))

    # (S) Session --> Hold Mcp Session
    with context("that the mcp server holds"):
        with before.each:
            Session._current = None
            self.repo = Path(tempfile.mkdtemp())
            self.hooks = HookServer(self.repo, HandlerCatalog([], self.repo))
            self.mcp = McpServer(repo=self.repo, project=self.repo)

        with it("should return no named session until one is open on the repo"):
            expect(self.mcp.session).to(equal(None))

        with it("should agree with the hook server on the same repo"):
            expect(self.mcp.session is self.hooks.session).to(equal(True))
            expect(self.mcp.session is Session.current(self.repo)).to(equal(True))

        with context("that opened a named session"):
            with before.each:
                Session._current = None
                self.repo = Path(tempfile.mkdtemp())
                (self.repo / ".git").mkdir()
                self.work = self.repo / "work"
                self.work.mkdir()
                Session.new("alpha", self.work, self.repo)
                self.hooks = HookServer(self.repo, HandlerCatalog([], self.repo))
                self.mcp = McpServer(repo=self.repo, project=self.repo)

            with it("should bind that session on the mcp host"):
                expect(self.mcp.session.name).to(equal("alpha"))
                expect(self.mcp.session.session_path).to(
                    equal(self.repo.resolve() / ".sessions" / "alpha")
                )

            with it("should load that session when another host syncs from the repo"):
                Session._current = None
                hooks = HookServer(self.repo, HandlerCatalog([], self.repo))
                expect(hooks.session.name).to(equal("alpha"))

            with it("should resolve current session when mcp project is the workpath subfolder"):
                Session._current = None
                work = self.repo / "space"
                work.mkdir()
                host = McpServer(repo=self.repo, project=work)
                expect(host.session.name).to(equal("alpha"))

            with it("should open that practice's guideline"):
                expect(self.mcp.session.practice("stories").guideline).to(be_a(PracticeGuidance))

            with it("should open that practice's graph with the guideline"):
                opened = self.mcp.session.practice("stories")
                expect(opened.graph.practices["stories"].name).to(equal("stories"))

            with it("should return the same practice across mcp calls"):
                first = self.mcp.session.practice("stories")
                expect(self.mcp.session.practice("stories") is first).to(equal(True))

    # (E) Open Named Session
    # (S) Session --> Open New Session
    with context("that is new"):
        with before.each:
            Session._current = None
            self.repo = Path(tempfile.mkdtemp())
            self.work = self.repo / "work"
            self.work.mkdir()
            self.instructions = Session.new("alpha", self.work, self.repo)

        with it("should return keep_log to the agent"):
            expect("log_action" in self.instructions).to(equal(True))
            expect("log_validation" in self.instructions).to(equal(True))
            expect("log_error" in self.instructions).to(equal(True))
            expect("append_chat" in self.instructions).to(equal(True))
            expect("log_guidance_action" in self.instructions).to(equal(True))
            expect("session.new" in self.instructions).to(equal(True))

        with it("should keep the name, the workpath, and the repo path"):
            session = Session.current()
            expect(session.name).to(equal("alpha"))
            expect(session.workpath).to(equal(self.work))
            expect(session.repo_path).to(equal(self.repo.resolve()))
            expect(session.session_path).to(equal(self.repo.resolve() / ".sessions" / "alpha"))

        with it("should write --- 1 as the first line of a new session.log"):
            first = (Session.current().session_path / "session.log").read_text(encoding="utf-8").splitlines()[0]
            expect("--- 1" in first).to(equal(True))

        with it("should leave practices empty until a practice is asked for"):
            expect(Session.current().practices).to(equal([]))

        with it("should record the name in repo sessions session.json"):
            state = json.loads((self.repo / ".sessions" / "session.json").read_text(encoding="utf-8"))
            expect(state.get("current")).to(equal("alpha"))

    with context("that is closed"):
        with before.each:
            Session._current = None
            self.repo = Path(tempfile.mkdtemp())
            self.work = self.repo / "work"
            self.work.mkdir()
            Session.new("alpha", self.work, self.repo)
            Session.current().close()

        with it("should record the default session in repo sessions session.json"):
            state = json.loads((self.repo / ".sessions" / "session.json").read_text(encoding="utf-8"))
            expect(state.get("current")).to(equal("default"))

        with it("should clear the in-process name"):
            expect(Session._slot().name).to(equal(""))

        with it("should return no current session without a repo path when nothing is open"):
            expect(Session.current()).to(equal(None))

    # (S) Session --> Select Existing Session
    with context("that is selected"):
        with before.each:
            Session._current = None
            self.repo = Path(tempfile.mkdtemp())
            self.work = self.repo / "work"
            self.work.mkdir()
            Session.new("alpha", self.work, self.repo)
            Session._current = None

        with context("with only a name"):
            with before.each:
                self._prior_repo = os.environ.get("CDD_REPO")
                self._prior_project = os.environ.get("CDD_PROJECT")
                os.environ["CDD_REPO"] = str(self.repo)
                os.environ["CDD_PROJECT"] = str(self.repo / "other")
                self.instructions = Session.switch("alpha")

            with it("should bind the existing session from the environment"):
                session = Session.current()
                expect(session.name).to(equal("alpha"))
                expect(session.repo_path).to(equal(self.repo.resolve()))
                expect(session.session_path).to(equal(self.repo.resolve() / ".sessions" / "alpha"))

            with it("should use the workpath stored on that session"):
                expect(Session.current().workpath).to(equal(self.work.resolve()))

            with it("should leave practices empty until a practice is asked for"):
                expect(Session.current().practices).to(equal([]))

            with it("should return keep_log to the agent"):
                expect("log_action" in self.instructions).to(equal(True))
                expect("session.switch" in self.instructions).to(equal(True))

            with after.each:
                if self._prior_repo is None:
                    os.environ.pop("CDD_REPO", None)
                else:
                    os.environ["CDD_REPO"] = self._prior_repo
                if self._prior_project is None:
                    os.environ.pop("CDD_PROJECT", None)
                else:
                    os.environ["CDD_PROJECT"] = self._prior_project

        with context("with a repo path"):
            with before.each:
                self.instructions = Session.switch("alpha", repo_path=self.repo)

            with it("should keep logging under that repo at sessions and the name"):
                expect(Session.current().session_path).to(
                    equal(self.repo.resolve() / ".sessions" / "alpha")
                )

            with it("should read the workpath from that session"):
                expect(Session.current().workpath).to(equal(self.work.resolve()))

        with context("when repo session.json current changes on disk"):
            with it("should reload the named session instead of keeping stale memory"):
                Session._current = None
                Session.new("alpha", self.work, self.repo)
                Session.new("beta", self.work, self.repo)
                expect(Session.current().name).to(equal("beta"))
                pointer = self.repo / ".sessions" / "session.json"
                pointer.write_text('{"current": "alpha"}', encoding="utf-8")
                Session.refresh_current_from_repo(self.repo)
                expect(Session.current().name).to(equal("alpha"))

    # (S) Session --> Open Session Loop
    with context("that opens a loop"):
        with before.each:
            Session._current = None
            self.repo = Path(tempfile.mkdtemp())
            self.work = self.repo / "work"
            self.work.mkdir()
            Session.new("alpha", self.work, self.repo)

        with it("should seed loop 1 in session.log when the session is new"):
            log = (Session.current().session_path / "session.log").read_text(encoding="utf-8")
            expect("--- 1" in log).to(equal(True))

        with it("should mark loops via mark_loop when a session is current"):
            expect(Session.mark_loop()).to(equal("2"))

    with context("that resumes loop numbering from session.log"):
        with before.each:
            Session._current = None
            self.repo = Path(tempfile.mkdtemp())
            self.work = self.repo / "work"
            self.work.mkdir()
            Session.new("alpha", self.work, self.repo)
            session = Session.current()
            session._append_log("--- 2")
            Session._current = None

        with it("should append the next loop after switch without in-memory loops"):
            Session.switch("alpha", self.work, self.repo)
            expect(Session.mark_loop()).to(equal("3"))

    # (E) Record Session Log
    # (S) Session --> Record Session Error
    with context("that logs an error"):
        with before.each:
            Session._current = None
            self.repo = Path(tempfile.mkdtemp())
            self.work = self.repo / "work"
            self.work.mkdir()
            Session.new("alpha", self.work, self.repo)
            self.failure = RuntimeError("boom")

        with it("should write the trace and still raise the failure"):
            caught = None
            try:
                Session.current().log_error(self.failure)
            except RuntimeError as error:
                caught = error
            err = (Session.current().session_path / "session.err").read_text(encoding="utf-8")
            expect(caught).to(equal(self.failure))
            expect("boom" in err).to(equal(True))

        with it("should point the session.log line at that session.err file"):
            try:
                Session.current().log_error(self.failure)
            except RuntimeError:
                pass
            log = (Session.current().session_path / "session.log").read_text(encoding="utf-8")
            expect("session.err" in log).to(equal(True))

    # (S) Session --> Record Session Action
    with context("that logs an action"):
        with before.each:
            Session._current = None
            self.repo = Path(tempfile.mkdtemp())
            self.work = self.repo / "work"
            self.work.mkdir()
            Session.new("alpha", self.work, self.repo)
            self.session = Session.current()
            _bind_mandatory_chat(self.session, self.work)
            self.edited = self.work / "cart.py"
            self.edited.write_text("class Cart:\n    pass\n", encoding="utf-8")

        with context("with paths passed in"):
            with it("should still log the action and record no-chat on session.err when chat is missing"):
                Session._current = None
                bare = Path(tempfile.mkdtemp())
                work = bare / "work"
                work.mkdir()
                Session.new("alpha", work, bare)
                session = Session.current()
                os.environ.pop("CDD_CONVERSATION_ID", None)
                os.environ.pop("CDD_TRANSCRIPT_PATH", None)
                session.log_action("sketch", [work / "x.py"])
                log = (session.session_path / "session.log").read_text(encoding="utf-8")
                err = (session.session_path / "session.err").read_text(encoding="utf-8")
                expect("sketch" in log and "no-chat" in log and "session.err" in log).to(equal(True))
                expect("missing chat" in err).to(equal(True))

            with it("should append a timestamped line that names the action and the path"):
                self.session.log_action("sketch", [self.edited])
                log = (self.session.session_path / "session.log").read_text(encoding="utf-8")
                expect("sketch" in log and str(self.edited) in log and "T" in log).to(equal(True))

        with context("with a graph node known for the practice"):
            with before.each:
                self.session.practice("bdd")

            with it("should name the practice graph root"):
                self.session.log_action("sketch", [self.edited])
                log = (self.session.session_path / "session.log").read_text(encoding="utf-8")
                expect("bdd" in log).to(equal(True))

        with context("with rules injected from a inject rules hook"):
            with before.each:
                self.session.note_injected_rule(
                    "bdd", "development", "hierarchy-preservation", str(self.edited)
                )

            with it("should log that practice, fidelity, rule, and matched file"):
                self.session.log_action("sketch", [self.edited])
                log = (self.session.session_path / "session.log").read_text(encoding="utf-8")
                expect(
                    "bdd development hierarchy-preservation" in log and str(self.edited) in log
                ).to(equal(True))

            with it("should omit a rule that was not injected"):
                self.session.log_action("sketch", [self.edited])
                log = (self.session.session_path / "session.log").read_text(encoding="utf-8")
                expect("stories-story-map" in log).to(equal(False))

        with context("with a chat transcript"):
            with it("should point at the chat id, the transcript file, and the line numbers"):
                transcript = self.work / "chat.md"
                transcript.write_text("hello\n", encoding="utf-8")
                self.session.note_chat("chat-1", transcript, "1-2")
                self.session.log_action("sketch", [self.edited])
                log = (self.session.session_path / "session.log").read_text(encoding="utf-8")
                expect("chat-1" in log and str(transcript) in log and "1-2" in log).to(equal(True))

    # (S) Session --> Select Existing Session
    with context("with a session path"):
        with before.each:
            Session._current = None
            self.repo = Path(tempfile.mkdtemp())
            (self.repo / ".git").mkdir()
            self.work = self.repo / "work"
            self.work.mkdir()
            Session.new("alpha", self.work, self.repo)
            self.session_path = Session.current().session_path
            Session._current = None

        with it("should read the repo path and the workpath from that session"):
            Session.switch("alpha", session_path=self.session_path)
            session = Session.current()
            expect(session.repo_path).to(equal(self.repo.resolve()))
            expect(session.workpath).to(equal(self.work.resolve()))

    # (S) Session --> Select Existing Session
    with context("with a workpath"):
        with before.each:
            Session._current = None
            self.repo = Path(tempfile.mkdtemp())
            (self.repo / ".git").mkdir()
            self.work = self.repo / "work"
            self.work.mkdir()
            Session.new("alpha", self.work, self.repo)
            Session._current = None

        with it("should keep the given workpath and take the repo root from it"):
            Session.switch("alpha", workpath=self.work)
            session = Session.current()
            expect(session.workpath).to(equal(self.work.resolve()))
            expect(session.repo_path).to(equal(self.repo.resolve()))


# (E) Open Work Session
# (E) Open Named Session
# (S) Session --> Open Session Loop
with description("a loop"):
    with context("that is opened"):
        with before.each:
            Session._current = None
            self.repo = Path(tempfile.mkdtemp())
            self.work = self.repo / "work"
            self.work.mkdir()
            Session.new("alpha", self.work, self.repo)
            self.first = Session.current().loop()
            self.second = Session.current().loop()

        with it("should take the next loop number"):
            expect(self.second.number).to(equal(self.first.number + 1))

        with it("should append the loop marker to session.log"):
            log = (Session.current().session_path / "session.log").read_text(encoding="utf-8")
            expect(f"--- {self.second.number}" in log).to(equal(True))

    with context("that has log entries"):
        with before.each:
            Session._current = None
            self.repo = Path(tempfile.mkdtemp())
            self.work = self.repo / "work"
            self.work.mkdir()
            Session.new("alpha", self.work, self.repo)
            self.session = Session.current()
            _bind_mandatory_chat(self.session, self.work, "loop-chat")
            self.opened = self.session.loop()
            self.session.log_action("sketch", [self.work / "cart.py"])

        with it("should return the log lines for that loop number"):
            expect(any("sketch" in line for line in self.opened.entries)).to(equal(True))

        with it("should put the loop marker line first when loaded from session.log"):
            reloaded = self.session.loop_at(self.opened.number)
            expect(reloaded.entries[0]).to(contain(f"--- {reloaded.number}"))

        with context("with a chat to place under the lines"):
            with it("should show the chat and the response under the lines they belong to"):
                chat = self.work / "chat.md"
                chat.write_text(
                    "chat-id: chat-loop-1\nlines: 1-1\n\nthe response\n",
                    encoding="utf-8",
                )
                self.opened.inject(chat)
                text = self.opened.text()
                expect(
                    "chat-loop-1" in text
                    and str(chat) in text
                    and "1-1" in text
                    and "the response" in text
                ).to(equal(True))

        with it("should reload log lines from session.log when accessed by loop number"):
            Session._current = None
            Session.switch("alpha", repo_path=self.repo)
            reloaded = Session.current()[self.opened.number]
            expect(any("sketch" in line for line in reloaded.entries)).to(equal(True))

        with it("should read a loop with transcripts via read_loop"):
            chat = self.work / "chat.jsonl"
            chat.write_text(
                '{"role": "user", "message": {"content": [{"type": "text", "text": "loop read"}]}}\n',
                encoding="utf-8",
            )
            chat_id = "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"
            self.session.note_chat(chat_id, chat, "1")
            self.session.log_action("validate", [self.work / "cart.py"])
            body = Session.read_loop(self.opened.number)
            expect("loop read" in body and "validate" in body).to(equal(True))


# (E) Open Work Session
# (E) Record Session Log
with description("an action"):
    with before.each:
        Session._current = None
        self.repo = Path(tempfile.mkdtemp())
        self.work = self.repo / "work"
        self.work.mkdir()
        Session.new("alpha", self.work, self.repo)
        self.session = Session.current()
        _bind_mandatory_chat(self.session, self.work, "action-chat")

    # (S) Session --> Record Validation Run
    with context("that calls validate"):
        with before.each:
            self.guidance = self.session.practice("bdd").guideline

        with context("with a practice and a fidelity"):
            with it("should log that practice and that fidelity"):
                self.session.log_validation(self.guidance, [])
                log = (self.session.session_path / "session.log").read_text(encoding="utf-8")
                expect("Bdd" in log and "behavior" in log).to(equal(True))

        with context("with a violation"):
            with it("should log the rule, the synopsis, and the correction"):
                self.session.log_validation(
                    self.guidance,
                    ["hierarchy-preservation synopsis: flattened tree correction: keep the nesting"],
                )
                log = (self.session.session_path / "session.log").read_text(encoding="utf-8")
                expect("hierarchy-preservation" in log and "synopsis" in log and "correction" in log).to(
                    equal(True)
                )

    # (S) Session --> Attach Action Chat
    with context("that appends a chat to a logged action"):
        with before.each:
            self.session.log_action("sketch", [self.work / "cart.py"])
            self.chat = self.work / "chat.md"
            self.chat.write_text("chat body\n", encoding="utf-8")
            self.session.note_chat("chat-9", self.chat, "4")

        with it("should add that chat onto that action's log line"):
            self.session.append_chat("sketch", self.chat)
            log = (self.session.session_path / "session.log").read_text(encoding="utf-8")
            expect("chat-9" in log and "4" in log).to(equal(True))

    # (S) Session --> Record Session Action
    with context("that names an action"):
        with it("should log that action"):
            GuidanceAction().run("a note", lambda item: None, action="sketch")
            log = (self.session.session_path / "session.log").read_text(encoding="utf-8")
            expect("sketch" in log).to(equal(True))

        with it("should log workpath and practice context for listed guidance"):
            from harness.guidance_actions import GuidanceAction

            GuidanceAction().run(["bdd"], lambda item: None, action="generate")
            log = (self.session.session_path / "session.log").read_text(encoding="utf-8")
            expect("generate" in log and str(self.work) in log and "bdd" in log).to(equal(True))

        with context("with MCP host session binding like session.switch"):
            with it("should log generate and validate with practice context"):
                import os

                from harness.mcp.mcp_server import McpServer
                from validate.validate import Validate

                Session._current = None
                (self.repo / ".git").mkdir(exist_ok=True)
                os.environ["CDD_REPO"] = str(self.repo.resolve())
                os.environ["CDD_PROJECT"] = str(self.work.resolve())
                _bind_mandatory_chat(self.session, self.work, "mcp-host-chat")
                McpServer(repo=self.repo, project=self.work)
                Session._current = None
                GuidanceAction().run(["bdd"], lambda _item: None, action="generate")
                Validate().validate(["bdd"])
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
                    {
                        "hook_event_name": "afterFileEdit",
                        "file_path": edited.as_posix(),
                    }
                )
                self.session.log_action("sketch", [edited])
                log = (self.session.session_path / "session.log").read_text(encoding="utf-8")
                expect("sample-rule-one" in log and str(edited) in log).to(equal(True))

    with context("that names no action"):
        with it("should leave session.log unchanged"):
            log_path = self.session.session_path / "session.log"
            before = log_path.read_text(encoding="utf-8") if log_path.is_file() else ""
            GuidanceAction().run("a note", lambda item: None)
            after_log = log_path.read_text(encoding="utf-8") if log_path.is_file() else ""
            expect(after_log).to(equal(before))


# (E) Open Work Session
# (E) Hold Process Session
# (S) Session --> Load Practice Guideline
with description("a practice"):
    with context("that a practice has been invoked"):
        with before.each:
            Session._current = None
            self.repo = Path(tempfile.mkdtemp())
            self.work = self.repo / "work"
            self.work.mkdir()
            Session.new("alpha", self.work, self.repo)
            self.session = Session.current()
            self.opened = self.session.practice("bdd")

        with it("should hold that practice's guideline and graph in memory"):
            expect(isinstance(self.opened.guideline, PracticeGuidance)).to(equal(True))

        with it("should hold that practice's graph with the guideline"):
            expect(self.opened.graph.practices["bdd"].name).to(equal("bdd"))

        with it("should return that same practice on the next ask"):
            expect(self.session.practice("bdd") is self.opened).to(equal(True))

        with it("should leave the other practices unopened"):
            expect([item.name for item in self.session.practices]).to(equal(["bdd"]))

        with context("with the practice default folders"):
            with it("should point that practice's graph root at the practice's own folder"):
                expect(self.opened.graph.practices["bdd"].source_root.endswith("bdd")).to(equal(True))

            # (E) Open Named Session
            # (S) Session --> Remember Practice Folders
            with it("should leave that practice out of practices.json"):
                path = self.repo / ".context" / "practices.json"
                text = path.read_text(encoding="utf-8") if path.is_file() else ""
                expect("bdd" in text).to(equal(False))

        with context("with parent folders that are not the default"):
            with before.each:
                self.custom = self.repo / "custom-bdd"
                self.custom.mkdir()
                self.session.remember_parent_folders("bdd", [[self.custom]])
                Session._current = None
                Session.switch("alpha", repo_path=self.repo)
                self.session = Session.current()
                self.opened = self.session.practice("bdd")

            with it("should point that practice's graph root at those parent folders"):
                expect(self.opened.graph.practices["bdd"].source_root).to(equal(str(self.custom.resolve())))

            # (S) Session --> Remember Practice Folders
            with it("should save those folders in practices.json"):
                text = (self.repo / ".context" / "practices.json").read_text(encoding="utf-8")
                expect("bdd" in text and "custom-bdd" in text).to(equal(True))

        # (S) Session --> Remember Practice Folders
        with context("with more than one set of peer folders"):
            with before.each:
                self.first_set = self.repo / "one"
                self.second_set = self.repo / "two"
                self.first_set.mkdir()
                self.second_set.mkdir()
                self.session.remember_parent_folders("bdd", [[self.first_set], [self.second_set]])
                Session._current = None
                Session.switch("alpha", repo_path=self.repo)
                self.session = Session.current()
                self.opened = self.session.practice("bdd")

            with it("should keep each set on that practice"):
                expect(len(self.opened.folder_sets)).to(equal(2))

    with context("that a practice has not been invoked"):
        with before.each:
            Session._current = None
            self.session = Session()

        with it("should omit that practice's entry"):
            expect(self.session.practices).to(equal([]))

    with context("with harness/guidance as the tree for clean engineering, stories, and bdd"):
        with before.each:
            Session._current = None
            self.repo = Path(tempfile.mkdtemp())
            self.work = self.repo / "work"
            self.work.mkdir()
            self.tree = _REPO_ROOT / "harness" / "guidance"
            Session.new("alpha", self.work, self.repo)
            self.session = Session.current()
            for practice in ("clean_engineering", "stories", "bdd"):
                self.session.remember_parent_folders(practice, [[self.tree]])
            Session._current = None
            Session.switch("alpha", repo_path=self.repo)
            self.session = Session.current()
            started = time.perf_counter()
            self.opened = [self.session.practice(name) for name in ("clean_engineering", "stories", "bdd")]
            self.elapsed = time.perf_counter() - started

        with it("should load those graphs from harness/guidance"):
            roots = [item.graph.practices[item.name].source_root for item in self.opened]
            expect(all(root == str(self.tree.resolve()) for root in roots)).to(equal(True))

        with it("should finish that load within 5 seconds"):
            expect(self.elapsed < 5).to(equal(True))
