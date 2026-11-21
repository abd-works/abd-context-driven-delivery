"""Specs for the session log reading a loop back with the chat each line came from."""
import json
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from expects import contain, equal, expect
from mamba import after, before, description, context, it

from harness.agent_tools.agent_tools import ToolsetReference
from harness.agent_tools.tool_call import ToolCall, ToolRequest
from harness.mcp.mcp_server import ProjectToolsets
from space.session.session import Session
from harness.process.capped_log_file import LOG_SIZE_LIMIT_BYTES
from space.session.session_log import LogTimestamp
from space.session.sessions import Sessions
from space.session.throwaway_project import ExampleHome
from harness.guidance.practice_catalogue import PRACTICE_CATALOGUE
import cdd_guidance.practices  # noqa: F401 - registers the practices with the practice catalogue

# The first practices a process makes read and parse their guidance for every later one; made once here, before any
# example, so no example pays for that first read.
PRACTICE_CATALOGUE.create_all()


# (E) Record Session Log
with description("a session loop"):
    with before.each:
        self.home = ExampleHome()

    with after.each:
        self.home.close()

    with context("whose log line points at a chat"):
        with it("should place the transcript text under that line"):
            repo = Path(tempfile.mkdtemp())
            work = repo / "work"
            work.mkdir()
            transcript = work / "chat.jsonl"
            transcript.write_text(
                json.dumps({"role": "user", "message": {"content": [{"type": "text", "text": "question"}]}}),
                encoding="utf-8",
            )
            Sessions(repo).switch("alpha", work)
            session = Sessions(repo).current()
            session.log.record("--- 1")
            chat_id = "b4c2a422-7199-47ce-9656-c0429af8adb8"
            session.log.record(f"2026-10-20T12:00:00Z sketch {work / 'a.py'} {chat_id} {transcript} 1")
            expanded = session.log.loop_at(1).expanded_text()
            expect("question" in expanded and "sketch" in expanded).to(equal(True))

    # A worktree removed while the cdd server still holds its session, as a reset of a ticket's sessions removes it: a
    # folder made again under the worktree's name would stop the next ticket.activate from adding the worktree there.
    with context("whose ticket's worktree was removed"):
        with before.each:
            repo = Path(tempfile.mkdtemp())
            Sessions(repo).switch("alpha", repo)
            self.session = Sessions(repo).current()
            self.worktree = Path(tempfile.mkdtemp()) / "cdd-alpha"
            self.session.work_folder = self.worktree / ".sessions" / "alpha"
            self.session.log.record("move alpha Discovery")

        with it("should write nothing, leaving no folder where the worktree was"):
            expect(self.worktree.exists()).to(equal(False))

    with context("marked by a tool call a chat sent"):
        with it("should point its next loop marker at that chat"):
            repo = Path(tempfile.mkdtemp())
            transcript = repo / "chat.jsonl"
            transcript.write_text("{}\n", encoding="utf-8")
            call = ToolCall.sent({"conversation_id": "chat-b", "transcript_path": str(transcript)}, repo)
            call.session.log.by(call.request.chat).next_loop()
            expect(call.session.log.path.read_text(encoding="utf-8")).to(contain(f"--- 1 chat-b {transcript} 1"))

    with context("read by two calls from two chats"):
        with it("should be one session object, which holds no chat of either"):
            repo = Path(tempfile.mkdtemp())
            (repo / ".git").mkdir()
            Sessions(repo).switch("alpha", repo, ToolCall.sent({"conversation_id": "chat-2"}, repo))
            first = ToolCall.sent({"conversation_id": "chat-1"}, repo).session_named(".sessions/alpha/session.json")
            second = ToolCall.sent({"conversation_id": "chat-2"}, repo).session
            expect(first is second).to(equal(True))

    # One Session per folder holds only when every name of one checkout reaches one Sessions, as one Repo does.
    with context("read by a call that names a folder inside the checkout"):
        with before.each:
            self.repo = Path(tempfile.mkdtemp()).resolve()
            (self.repo / ".git").mkdir()
            (self.repo / "docs").mkdir()
            for chat in ("chat-1", "chat-2"):
                Sessions(self.repo).switch("alpha", self.repo, ToolCall.sent({"conversation_id": chat}, self.repo))
            self.session = ToolCall.sent({"conversation_id": "chat-1"}, self.repo).session

        with it("should be the session object a call naming the checkout's top reads"):
            inside = ToolCall.sent({"conversation_id": "chat-2"}, self.repo / "docs").session
            expect(inside is self.session).to(equal(True))

        with it("should be the session object a board command naming its session.json with no project reads"):
            named = ToolCall.sent({"conversation_id": "chat-3"}, None).session_named(str(self.repo / ".sessions" / "alpha" / "session.json"))
            expect(named is self.session).to(equal(True))

        with it("should be held by one sessions object for the checkout"):
            expect(Sessions.of_project(self.repo / "docs") is Sessions.of_project(self.repo)).to(equal(True))

    with context("whose practice a call reaches"):
        with it("should be the practice's own session, the one the call opened"):
            repo = Path(tempfile.mkdtemp())
            (repo / ".git").mkdir()
            Sessions(repo).switch("alpha", repo)
            call = ToolCall.sent({"conversation_id": "chat-v"}, repo)
            expect(call.session.practice("stories").session is call.session).to(equal(True))

    # A session tool names its session by its session.json, so the session it acts on is found from that argument,
    # not from the session open in the project; the chat that sent the call is still the one its lines point at.
    with context("marked through the session tool a chat calls with the session named"):
        # The server marks the loop once, and every example reads what that one call answered and wrote.
        with before.all:
            self.marking_home = ExampleHome()
            self.repo = Path(tempfile.mkdtemp())
            (self.repo / ".git").mkdir()
            Sessions(self.repo).switch("alpha", self.repo)
            Sessions(self.repo).switch("main")
            self.transcript = self.repo / "chat.jsonl"
            self.transcript.write_text("{}\n", encoding="utf-8")
            chat = {"conversation_id": "chat-m", "transcript_path": str(self.transcript), "transcript_lines": "3"}
            self.server = ProjectToolsets(project=self.repo)
            self.server.start((ToolsetReference.of(Session), ToolsetReference.of(Sessions)))
            call = ToolCall.sent({"session": ".sessions/alpha/session.json", **chat}, self.repo, ToolRequest(tool="session.mark_loop"))
            self.number = self.server.answer("session.mark_loop", call)
            self.log = (self.repo / ".sessions" / "alpha" / "session.log").read_text(encoding="utf-8")

        with after.all:
            self.marking_home.close()

        with it("should answer the number of the loop it marked"):
            expect(self.number).to(equal("2"))

        with it("should point the loop marker at the chat that called it"):
            expect(self.log).to(contain(f"--- 2 chat-m {self.transcript} 3"))

    # A session's log is written on every tool call; capped, it cannot grow until it fills the disk.
    with context("whose log reached its size limit"):
        with before.each:
            repo = Path(tempfile.mkdtemp())
            Sessions(repo).switch("alpha", repo)
            self.session = Sessions(repo).current()
            self.session.log.record("--- 3 chat-a")
            self.session.log.record("x" * LOG_SIZE_LIMIT_BYTES)
            self.session.log.record("tool board.show")
            self.folder = repo / ".sessions" / "alpha"

        with it("should keep the earlier lines in session.log.1"):
            expect((self.folder / "session.log.1").read_text(encoding="utf-8")).to(contain("--- 3 chat-a"))

        with it("should start the new session.log in the loop it was in"):
            expect(self.session.log.loop_at(3).entries[-1]).to(contain("tool board.show"))

        with it("should number the next loop on from it"):
            expect(self.session.log.by(None).next_loop().number).to(equal(4))

    with context("whose error file reached its size limit"):
        with before.each:
            repo = Path(tempfile.mkdtemp())
            Sessions(repo).switch("alpha", repo)
            self.session = Sessions(repo).current()
            self.folder = repo / ".sessions" / "alpha"
            (self.folder / "session.err").write_text("x" * LOG_SIZE_LIMIT_BYTES, encoding="utf-8")
            self.session.log.by(None).failure(RuntimeError("the call failed"), tool="board.show")

        with it("should keep the earlier traces in session.err.1"):
            expect((self.folder / "session.err.1").stat().st_size).to(equal(LOG_SIZE_LIMIT_BYTES))

        with it("should point the error line at the first line of the new session.err"):
            expect(self.session.log.entries[-1].text).to(contain(f"{self.folder / 'session.err'} 1 "))

    with context("noted through the session tool a chat calls with the session named"):
        with it("should point the note at the chat that called it"):
            repo = Path(tempfile.mkdtemp())
            (repo / ".git").mkdir()
            Sessions(repo).switch("alpha", repo)
            transcript = repo / "chat.jsonl"
            transcript.write_text("{}\n", encoding="utf-8")
            chat = {"conversation_id": "chat-n", "transcript_path": str(transcript), "transcript_lines": "4"}
            server = ProjectToolsets(project=repo)
            server.start((ToolsetReference.of(Session), ToolsetReference.of(Sessions)))
            server.answer("session.append_log", ToolCall.sent({"session": ".sessions/alpha/session.json", "note": "fixed", **chat}, repo, ToolRequest(tool="session.append_log")))
            log = (repo / ".sessions" / "alpha" / "session.log").read_text(encoding="utf-8")
            expect(log).to(contain(f"note loop 1: fixed chat-n {transcript} 4"))


with description("a log timestamp"):
    with context("of a moment in another time zone"):
        with it("should write the moment in UTC to the second, as session logs do"):
            moment = datetime(2026, 11, 7, 18, 30, 5, 900, tzinfo=timezone(timedelta(hours=1)))
            expect(str(LogTimestamp(moment))).to(equal("2026-11-07T17:30:05Z"))

    with context("read back from the text a log wrote"):
        with it("should be the same moment"):
            expect(LogTimestamp.read("2026-11-07T17:30:05Z").moment).to(equal(datetime(2026, 11, 7, 17, 30, 5, tzinfo=timezone.utc)))

    with context("made for now"):
        with it("should be the current moment"):
            before_now = datetime.now(timezone.utc).replace(microsecond=0)
            expect(LogTimestamp.now().moment >= before_now).to(equal(True))


# (E) Record Session Log
with description("a hook log"):
    with before.each:
        self.home = ExampleHome()

    with after.each:
        self.home.close()

    with context("of a session that two hooks append to"):
        with before.each:
            repo = Path(tempfile.mkdtemp())
            (repo / ".git").mkdir()
            Sessions(repo).switch("alpha", repo)
            session = Sessions(repo).current()
            session.folder.hook_log("prompt-log.txt").append("== entry under its own stamped header")
            session.folder.hook_log("prompt-log.txt").stamped("dispatch line")
            self.text = (repo / ".sessions" / "alpha" / "logs" / "prompt-log.txt").read_text(encoding="utf-8")

        with it("should keep an entry as it was given"):
            expect(self.text.splitlines()[0]).to(equal("== entry under its own stamped header"))

        with it("should stamp a line with the time it was written"):
            expect(self.text.splitlines()[1]).to(contain("Z dispatch line"))

    with context("that reached its size limit"):
        with before.each:
            repo = Path(tempfile.mkdtemp())
            (repo / ".git").mkdir()
            Sessions(repo).switch("alpha", repo)
            logs = repo / ".sessions" / "alpha" / "logs"
            logs.mkdir(parents=True)
            (logs / "dispatch.debug").write_text("x" * LOG_SIZE_LIMIT_BYTES, encoding="utf-8")
            Sessions(repo).current().folder.hook_log("dispatch.debug").stamped("dispatch line")
            self.logs = logs

        with it("should start a new log with the next line"):
            expect((self.logs / "dispatch.debug").read_text(encoding="utf-8")).to(contain("Z dispatch line"))

        with it("should keep the earlier entries in the previous file"):
            expect((self.logs / "dispatch.debug.1").stat().st_size).to(equal(LOG_SIZE_LIMIT_BYTES))


# (E) Record Session Log
with description("a session a chat switches to"):
    with before.each:
        self.home = ExampleHome()
        self.repo = Path(tempfile.mkdtemp())
        (self.repo / ".git").mkdir()

    with after.each:
        self.home.close()

    with context("whose practices write under their default folders"):
        with it("should tell the chat to point each practice at where its artifacts already are"):
            answer = Sessions(self.repo).switch("alpha", self.repo)
            expect(answer).to(contain("practice-session-output.choose_root"))

        with it("should tell the chat to give a fidelity kept apart, such as the story tests, a root of its own, as local as it can"):
            answer = Sessions(self.repo).switch("alpha", self.repo)
            expect(answer).to(contain("fidelity-session-output.choose_root", "most local folder"))

        with it("should tell the chat to set up its roots from the ticket and its branch and confirm them with the person"):
            answer = Sessions(self.repo).switch("alpha", self.repo)
            expect(answer).to(contain("session.set_up_roots", "fidelity-session-output.propose_roots", "confirm"))

        with it("should tell the chat to add each further folder beside a fidelity's root"):
            answer = Sessions(self.repo).switch("alpha", self.repo)
            expect(answer).to(contain("fidelity-session-output.add_root"))

    with context("whose every practice has a chosen root"):
        with it("should not ask about roots"):
            Sessions(self.repo).switch("alpha", self.repo)
            session = Sessions(self.repo).current()
            for practice in session.own_practices.values():
                practice.choose_root("work")
            answer = Sessions(self.repo).switch("alpha", self.repo)
            expect("Output roots" in answer).to(equal(False))

    with context("that is main"):
        with it("should not ask about roots"):
            answer = Sessions(self.repo).switch("main")
            expect("Output roots" in answer).to(equal(False))
