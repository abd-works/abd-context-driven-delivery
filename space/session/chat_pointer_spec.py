"""Specs for the chat pointer that ends each session.log line."""
import json
import os
import sys
import tempfile
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from expects import be_none, equal, expect
from mamba import after, before, context, description, it

from space.session.chat_pointer import ChatPointer
from space.session.sessions import Sessions
from space.session.throwaway_project import ProjectCall

CHAT_ID = "4f1c2b3a-1111-2222-3333-444455556666"


# (E) Record Session Log
with description("a chat pointer"):
    with before.each:
        self.config = Path(tempfile.mkdtemp())
        self.prior_config = os.environ.get("CLAUDE_CONFIG_DIR")
        os.environ["CLAUDE_CONFIG_DIR"] = str(self.config)

    with after.each:
        if self.prior_config is None:
            os.environ.pop("CLAUDE_CONFIG_DIR", None)
        else:
            os.environ["CLAUDE_CONFIG_DIR"] = self.prior_config

    with context("taken from a tool call that names only its Claude Code chat"):
        with context("with the chat's transcript in the Claude projects folder"):
            with before.each:
                self.transcript = self.config / "projects" / "C--dev-shop" / f"{CHAT_ID}.jsonl"
                self.transcript.parent.mkdir(parents=True)
                self.transcript.write_text('{"type": "user"}\n{"type": "assistant"}\n', encoding="utf-8")
                self.chat, self.arguments = ChatPointer.taken_from({"conversation_id": CHAT_ID, "path": "cart.py"})

            with it("should name the chat's transcript"):
                expect(self.chat.transcript).to(equal(self.transcript))

            with it("should point at every line of the transcript so far"):
                expect(self.chat.lines).to(equal("1-2"))

            with it("should hand the tool only its own arguments"):
                expect(self.arguments).to(equal({"path": "cart.py"}))

        with context("with no transcript by that name"):
            with it("should name no transcript"):
                chat, _ = ChatPointer.taken_from({"conversation_id": CHAT_ID})
                expect(chat.transcript).to(equal(Path("unknown")))

    with context("taken from a tool call that names no chat"):
        with it("should be none"):
            chat, _ = ChatPointer.taken_from({"path": "cart.py"})
            expect(chat).to(be_none)

    with context("that a tool call is served with"):
        with before.each:
            self.chat = ChatPointer("chat-a", Path("a.jsonl"), "1-3")

        with it("should be the current chat while the call runs"):
            with ChatPointer.serving(self.chat):
                expect(ChatPointer.current()).to(equal(self.chat))

        with it("should not be the current chat once the call ends"):
            with ChatPointer.serving(self.chat):
                pass
            expect(ChatPointer.current() == self.chat).to(equal(False))

    with context("at the end of a session.log line"):
        with it("should read the chat id, the transcript, and the line range"):
            line = (
                "2026-10-20T15:35:21Z satisfy C:\\work "
                "b4c2a422-7199-47ce-9656-c0429af8adb8 "
                "C:\\chats\\one.jsonl 10-12"
            )
            chat = ChatPointer.in_log_line(line)
            expect((chat.id, chat.transcript.name, chat.lines)).to(
                equal(("b4c2a422-7199-47ce-9656-c0429af8adb8", "one.jsonl", "10-12"))
            )

        with it("should be none on a no-chat line"):
            expect(ChatPointer.in_log_line("2026-10-20T12:00:00Z sketch no-chat err 1")).to(be_none)

    with context("over a JSONL transcript"):
        with it("should give each event's role and text in its range"):
            path = self.config / "chat.jsonl"
            path.write_text(
                "\n".join(
                    json.dumps({"role": role, "message": {"content": [{"type": "text", "text": text}]}})
                    for role, text in (("user", "hi"), ("assistant", "hello"))
                ),
                encoding="utf-8",
            )
            lines = ChatPointer("chat-a", path, "1-2").transcript_text()
            expect((any("hi" in line for line in lines), any("hello" in line for line in lines))).to(
                equal((True, True))
            )


# (E) Record Session Log
with description("a session loop"):
    with after.each:
        ProjectCall.close_all()

    with context("whose log line points at a chat"):
        with it("should place the transcript text under that line"):
            repo = Path(tempfile.mkdtemp())
            ProjectCall(repo)
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
