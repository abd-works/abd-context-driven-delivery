"""Specs for session log chat pointer expansion."""
import json
import sys
import tempfile
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from expects import equal, expect
from mamba import context, description, it

from space.session.chat_transcript import parse_line_chat_pointer, read_transcript_slice
from space.session.session import Session


with description("chat transcript helpers"):
    with context("that parse a chat pointer on a log line"):
        with it("should read uuid, path, and line numbers from the suffix"):
            line = (
                "2026-10-20T15:35:21Z satisfy C:\\work "
                "b4c2a422-7199-47ce-9656-c0429af8adb8 "
                "C:\\chats\\one.jsonl 10-12"
            )
            parsed = parse_line_chat_pointer(line)
            expect(parsed is not None).to(equal(True))
            chat_id, path, lines = parsed
            expect(chat_id).to(equal("b4c2a422-7199-47ce-9656-c0429af8adb8"))
            expect(path.name).to(equal("one.jsonl"))
            expect(lines).to(equal("10-12"))

        with it("should ignore no-chat lines"):
            expect(parse_line_chat_pointer("2026-10-20T12:00:00Z sketch no-chat err 1")).to(equal(None))

    with context("that read a jsonl slice"):
        with it("should format role and text for each line in range"):
            with tempfile.TemporaryDirectory() as tmp:
                path = Path(tmp) / "chat.jsonl"
                path.write_text(
                    "\n".join(
                        [
                            json.dumps({"role": "user", "message": {"content": [{"type": "text", "text": "hi"}]}}),
                            json.dumps(
                                {"role": "assistant", "message": {"content": [{"type": "text", "text": "hello"}]}}
                            ),
                        ]
                    ),
                    encoding="utf-8",
                )
                lines = read_transcript_slice(path, "1-2")
                expect(any("hi" in line for line in lines)).to(equal(True))
                expect(any("hello" in line for line in lines)).to(equal(True))

    with context("that expand loop log lines"):
        with it("should place transcript text under the log line that references it"):
            with tempfile.TemporaryDirectory() as tmp:
                repo = Path(tmp)
                work = repo / "work"
                work.mkdir()
                transcript = work / "chat.jsonl"
                transcript.write_text(
                    json.dumps({"role": "user", "message": {"content": [{"type": "text", "text": "question"}]}}),
                    encoding="utf-8",
                )
                Session._current = None
                Session.new("alpha", work, repo)
                session = Session.current()
                session._append_log("--- 1")
                chat_id = "b4c2a422-7199-47ce-9656-c0429af8adb8"
                log_line = f"2026-10-20T12:00:00Z sketch {work / 'a.py'} {chat_id} {transcript} 1"
                session._append_log(log_line)
                expanded = session.loop_at(1).expanded_text()
                expect("question" in expanded and "sketch" in expanded).to(equal(True))
