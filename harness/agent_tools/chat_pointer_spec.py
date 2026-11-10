"""Specs for the chat a tool call came from, which ends each session.log line."""
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

from harness.agent_tools.chat_pointer import ChatPointer
from harness.agent_tools.tool_call import ToolCall

CHAT_ID = "4f1c2b3a-1111-2222-3333-444455556666"


def record_folders(transcript: Path, *folders: Path) -> None:
    """Write a Claude Code transcript whose events record the chat working in each folder in turn."""
    transcript.write_text("".join(json.dumps({"type": "user", "cwd": str(folder)}) + "\n" for folder in folders), encoding="utf-8")


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

    with context("found for a Claude Code session"):
        with before.each:
            self.transcript = self.config / "projects" / "C--spare" / f"{CHAT_ID}.jsonl"
            self.transcript.parent.mkdir(parents=True)
            self.spare = self.config / "spare"
            self.spare.mkdir()
            self.checkout = self.config / "shop"
            (self.checkout / ".git").mkdir(parents=True)
            (self.checkout / "src").mkdir()

        with context("that moved from the folder it started in to a checkout"):
            with it("should work in the checkout it moved to"):
                record_folders(self.transcript, self.spare, self.checkout)
                expect(ChatPointer.from_claude_session(CHAT_ID).working_folder).to(equal(self.checkout.resolve()))

        with context("that moved into a subfolder of a checkout"):
            with it("should work in the checkout holding the subfolder"):
                record_folders(self.transcript, self.checkout, self.checkout / "src")
                expect(ChatPointer.from_claude_session(CHAT_ID).working_folder).to(equal(self.checkout.resolve()))

        with context("whose last recorded folder is gone"):
            with it("should work in the last folder that is still there"):
                record_folders(self.transcript, self.checkout, self.config / "deleted")
                expect(ChatPointer.from_claude_session(CHAT_ID).working_folder).to(equal(self.checkout.resolve()))

        with context("whose transcript records no folder"):
            with it("should work in no folder"):
                self.transcript.write_text('{"type": "user"}\n', encoding="utf-8")
                expect(ChatPointer.from_claude_session(CHAT_ID).working_folder).to(be_none)

        with context("with no transcript by its id"):
            with it("should be none"):
                expect(ChatPointer.from_claude_session("9f1c2b3a-1111-2222-3333-444455556666")).to(be_none)

    with context("taken from a tool call that names no chat"):
        with it("should be none"):
            chat, _ = ChatPointer.taken_from({"path": "cart.py"})
            expect(chat).to(be_none)

    with context("of a tool call a chat sent"):
        with before.each:
            self.transcript = self.config / "chat.jsonl"
            self.transcript.write_text('{"type": "user"}\n', encoding="utf-8")
            self.call = ToolCall.sent({"conversation_id": "chat-a", "transcript_path": str(self.transcript), "path": "cart.py"}, self.config)

        with it("should be the call's chat"):
            expect(self.call.chat).to(equal(ChatPointer("chat-a", self.transcript, "1")))

        with it("should leave the tool only its own arguments"):
            expect(self.call.arguments).to(equal({"path": "cart.py"}))

        with it("should not be the chat of another call"):
            expect(ToolCall.sent({"path": "cart.py"}, self.config).chat).to(be_none)

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
