"""Specs for the session log reading a loop back with the chat each line came from."""
import json
import shutil
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
from harness.agent_tools.chat_pointer import ChatPointer
from harness.process.log_timestamp import LogTimestamp
from space.session.session_log import LogLine
from space.session.sessions import SERVED_SESSIONS, Sessions
from space.session.spec_support.throwaway_project import ExampleHome
from harness.guidance.practice_catalogue import PRACTICE_CATALOGUE
import cdd_guidance.practices  # noqa: F401 - registers the practices with the practice catalogue

# The first practices a process makes read and parse their guidance for every later one; made once here, before any
# example, so no example pays for that first read.
PRACTICE_CATALOGUE.create_all()


def _call_from(repo: Path, chat: str, project: Path | None) -> ToolCall:
    """A call from chat, naming its transcript in repo, so the call never searches the Claude projects folder for it."""
    return ToolCall.sent({"conversation_id": chat, "transcript_path": str(repo / f"{chat}.jsonl")}, project)


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
            Sessions(repo).switch("alpha", work, create=True)
            session = Sessions(repo).current()
            session.log.record(LogLine("---", subject="1"))
            chat_id = "b4c2a422-7199-47ce-9656-c0429af8adb8"
            session.log.record(LogLine("sketch", paths=[work / "a.py"], chat=ChatPointer(chat_id, transcript, "1")))
            expanded = session.log.loop_at(1).expanded_text()
            expect("question" in expanded and "sketch" in expanded).to(equal(True))

    # A worktree removed while the cdd server still holds its session, as a reset of a ticket's sessions removes it: a
    # folder made again under the worktree's name would stop the next ticket.activate from adding the worktree there.
    with context("whose ticket's worktree was removed"):
        with before.each:
            repo = Path(tempfile.mkdtemp())
            Sessions(repo).switch("alpha", repo, create=True)
            self.session = Sessions(repo).current()
            self.worktree = Path(tempfile.mkdtemp()) / "cdd-alpha"
            self.session.work_folder = self.worktree / ".sessions" / "alpha"
            self.session.log.record(LogLine("move", subject="alpha Discovery"))

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
            Sessions(repo).switch("alpha", repo, create=True, call=ToolCall.sent({"conversation_id": "chat-2"}, repo))
            first = ToolCall.sent({"conversation_id": "chat-1"}, repo).session_named(".sessions/alpha/session.json")
            second = ToolCall.sent({"conversation_id": "chat-2"}, repo).session
            expect(first is second).to(equal(True))

    # One Session per folder holds only when every name of one checkout reaches one Sessions, as one Repo does.
    with context("read by a call that names a folder inside the checkout"):
        # Both chats open the session once, and every example reads what the calls after them were answered.
        with before.all:
            self.naming_home = ExampleHome()
            self.repo = Path(tempfile.mkdtemp()).resolve()
            (self.repo / ".git").mkdir()
            (self.repo / "docs").mkdir()
            for chat in ("chat-1", "chat-2"):
                Sessions.of_project(self.repo).switch("alpha", self.repo, call=_call_from(self.repo, chat, self.repo), create=True)
            self.session = _call_from(self.repo, "chat-1", self.repo).session
            self.inside = _call_from(self.repo, "chat-2", self.repo / "docs").session
            self.named = _call_from(self.repo, "chat-3", None).session_named(str(self.repo / ".sessions" / "alpha" / "session.json"))
            self.sessions_inside = Sessions.of_project(self.repo / "docs")
            self.sessions_at_top = Sessions.of_project(self.repo)

        # The process lets go of the checkout's sessions, so a run of many examples does not keep each one's.
        with after.all:
            SERVED_SESSIONS.forget_under(self.repo)
            shutil.rmtree(self.repo, ignore_errors=True)
            self.naming_home.close()

        with it("should be the session object a call naming the checkout's top reads"):
            expect(self.inside is self.session).to(equal(True))

        with it("should be the session object a board command naming its session.json with no project reads"):
            expect(self.named is self.session).to(equal(True))

        with it("should be held by one sessions object for the checkout"):
            expect(self.sessions_inside is self.sessions_at_top).to(equal(True))

    with context("whose practice a call reaches"):
        with it("should be the practice's own session, the one the call opened"):
            repo = Path(tempfile.mkdtemp())
            (repo / ".git").mkdir()
            Sessions(repo).switch("alpha", repo, create=True)
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
            Sessions(self.repo).switch("alpha", self.repo, create=True)
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
            Sessions(repo).switch("alpha", repo, create=True)
            self.session = Sessions(repo).current()
            self.session.log.record(LogLine("---", subject="3", chat=ChatPointer("chat-a")))
            self.session.log.record(LogLine("x" * LOG_SIZE_LIMIT_BYTES))
            self.session.log.record(LogLine("tool", subject="board.show"))
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
            Sessions(repo).switch("alpha", repo, create=True)
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
            Sessions(repo).switch("alpha", repo, create=True)
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
            Sessions(repo).switch("alpha", repo, create=True)
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
            Sessions(repo).switch("alpha", repo, create=True)
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
            answer = Sessions(self.repo).switch("alpha", self.repo, create=True)
            expect(answer).to(contain("practice-session-output.choose_root"))

        with it("should tell the chat to give a fidelity kept apart, such as the story tests, a root of its own, as local as it can"):
            answer = Sessions(self.repo).switch("alpha", self.repo, create=True)
            expect(answer).to(contain("fidelity-session-output.choose_root", "most local folder"))

        with it("should tell the chat to set up its roots from the ticket and its branch and confirm them with the person"):
            answer = Sessions(self.repo).switch("alpha", self.repo, create=True)
            expect(answer).to(contain("session.set_up_roots", "fidelity-session-output.propose_roots", "confirm"))

        with it("should tell the chat to add each further folder beside a fidelity's root"):
            answer = Sessions(self.repo).switch("alpha", self.repo, create=True)
            expect(answer).to(contain("fidelity-session-output.add_root"))

    with context("whose every practice has a chosen root"):
        with it("should not ask about roots"):
            Sessions(self.repo).switch("alpha", self.repo, create=True)
            session = Sessions(self.repo).current()
            for practice in session.own_practices.values():
                practice.choose_root("work")
            answer = Sessions(self.repo).switch("alpha", self.repo, create=True)
            expect("Output roots" in answer).to(equal(False))

    with context("that is main"):
        with it("should not ask about roots"):
            answer = Sessions(self.repo).switch("main")
            expect("Output roots" in answer).to(equal(False))


with description("a log line"):
    with it("should write its verb, subject, paths, practices, fidelities, formats, detail and chat in that order"):
        line = LogLine("generate", paths=["src/a.py", "src/b.py"], practices=["stories"], fidelities=["scenarios"], formats=["markdown"], chat=ChatPointer("chat-a"))
        expect(line.written).to(equal("generate src/a.py, src/b.py stories scenarios markdown chat-a"))

    with it("should read its time, verb and words back from the line the log holds"):
        read = LogLine.read("2026-10-31T01:00:01Z validate stories scenarios graph-rule map.md:12 no-chat")
        expect([read.time, read.verb, read.words[:2]]).to(equal(["2026-10-31T01:00:01Z", "validate", ["stories", "scenarios"]]))

    # Older logs named a validated practice by its class, which a ticket still reads its progress from.
    with it("should name a fidelity an older validate line names by its practice's class"):
        class Stories:
            key = "stories"

        fidelity = type("Fidelity", (), {"name": "story_map", "practice_guidance": Stories()})()
        expect(LogLine.read("2026-10-31T01:00:01Z validate Stories story_map no-chat").names(fidelity)).to(equal(True))
