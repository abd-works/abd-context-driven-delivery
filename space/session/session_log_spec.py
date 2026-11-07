"""Specs for the session log reading a loop back with the chat each line came from."""
import json
import sys
import tempfile
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from expects import contain, equal, expect
from mamba import description, context, it

from harness.agent_tools.tool_call import ToolCall
from space.session.sessions import Sessions


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

    with context("opened for a tool call a chat sent"):
        with it("should point its next loop marker at that chat"):
            repo = Path(tempfile.mkdtemp())
            transcript = repo / "chat.jsonl"
            transcript.write_text("{}\n", encoding="utf-8")
            session = ToolCall.sent({"conversation_id": "chat-b", "transcript_path": str(transcript)}, repo).session
            session.log.next_loop()
            expect(session.log.path.read_text(encoding="utf-8")).to(contain(f"--- 1 chat-b {transcript} 1"))
