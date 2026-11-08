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
from mamba import before, description, context, it

from harness.agent_tools.tool_call import ToolCall
from harness.mcp.mcp_server import McpServer
from space.session.session import Session
from space.session.session_log import LogTimestamp
from space.session.sessions import Sessions
import cdd_guidance.practices  # noqa: F401 - registers the practices with the practice catalogue


# (E) Record Session Log
with description("a session loop"):
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

    with context("marked by a tool call a chat sent"):
        with it("should point its next loop marker at that chat"):
            repo = Path(tempfile.mkdtemp())
            transcript = repo / "chat.jsonl"
            transcript.write_text("{}\n", encoding="utf-8")
            call = ToolCall.sent({"conversation_id": "chat-b", "transcript_path": str(transcript)}, repo)
            call.session.log.by(call.chat).next_loop()
            expect(call.session.log.path.read_text(encoding="utf-8")).to(contain(f"--- 1 chat-b {transcript} 1"))

    with context("read by two calls from two chats"):
        with it("should be one session object, which holds no chat of either"):
            repo = Path(tempfile.mkdtemp())
            (repo / ".git").mkdir()
            Sessions(repo).switch("alpha", repo)
            first = ToolCall.sent({"conversation_id": "chat-1"}, repo).session_named(".sessions/alpha/session.json")
            second = ToolCall.sent({"conversation_id": "chat-2"}, repo).session
            expect(first is second).to(equal(True))

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
        with before.each:
            self.repo = Path(tempfile.mkdtemp())
            (self.repo / ".git").mkdir()
            Sessions(self.repo).switch("alpha", self.repo)
            Sessions(self.repo).switch("main")
            self.transcript = self.repo / "chat.jsonl"
            self.transcript.write_text("{}\n", encoding="utf-8")
            chat = {"conversation_id": "chat-m", "transcript_path": str(self.transcript), "transcript_lines": "3"}
            self.server = McpServer(project=self.repo)
            self.server.start((Session, Sessions))
            call = ToolCall.sent({"session": ".sessions/alpha/session.json", **chat}, self.repo, tool="session.mark_loop")
            self.number = self.server.answer_tool("session.mark_loop", call)
            self.log = (self.repo / ".sessions" / "alpha" / "session.log").read_text(encoding="utf-8")

        with it("should answer the number of the loop it marked"):
            expect(self.number).to(equal("2"))

        with it("should point the loop marker at the chat that called it"):
            expect(self.log).to(contain(f"--- 2 chat-m {self.transcript} 3"))

    with context("noted through the session tool a chat calls with the session named"):
        with it("should point the note at the chat that called it"):
            repo = Path(tempfile.mkdtemp())
            (repo / ".git").mkdir()
            Sessions(repo).switch("alpha", repo)
            transcript = repo / "chat.jsonl"
            transcript.write_text("{}\n", encoding="utf-8")
            chat = {"conversation_id": "chat-n", "transcript_path": str(transcript), "transcript_lines": "4"}
            server = McpServer(project=repo)
            server.start((Session, Sessions))
            server.answer_tool("session.append_log", ToolCall.sent({"session": ".sessions/alpha/session.json", "note": "fixed", **chat}, repo, tool="session.append_log"))
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
    with context("of a session that two hooks append to"):
        with before.each:
            repo = Path(tempfile.mkdtemp())
            (repo / ".git").mkdir()
            Sessions(repo).switch("alpha", repo)
            session = Sessions(repo).current()
            session.hook_log("prompt-log.txt").append("== entry under its own stamped header")
            session.hook_log("prompt-log.txt").stamped("dispatch line")
            self.text = (repo / ".sessions" / "alpha" / "logs" / "prompt-log.txt").read_text(encoding="utf-8")

        with it("should keep an entry as it was given"):
            expect(self.text.splitlines()[0]).to(equal("== entry under its own stamped header"))

        with it("should stamp a line with the time it was written"):
            expect(self.text.splitlines()[1]).to(contain("Z dispatch line"))
