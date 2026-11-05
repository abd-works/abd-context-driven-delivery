"""Specs for the chat a cdd tool call names, which session.log writes on each action line."""
import os
import sys
import tempfile
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from expects import be_none, equal, expect
from mamba import after, before, description, context, it

from space.session.chat_context import chat_from_environ, clear_chat_context, pop_chat_fields

CHAT_ID = "4f1c2b3a-1111-2222-3333-444455556666"


with description("a cdd tool call from a Claude Code chat"):
    with before.each:
        self.config = Path(tempfile.mkdtemp())
        self.prior_config = os.environ.get("CLAUDE_CONFIG_DIR")
        os.environ["CLAUDE_CONFIG_DIR"] = str(self.config)
        clear_chat_context()

    with after.each:
        clear_chat_context()
        if self.prior_config is None:
            os.environ.pop("CLAUDE_CONFIG_DIR", None)
        else:
            os.environ["CLAUDE_CONFIG_DIR"] = self.prior_config

    with context("that names only its chat"):
        with context("with the chat's transcript in the Claude projects folder"):
            with before.each:
                self.transcript = self.config / "projects" / "C--dev-shop" / f"{CHAT_ID}.jsonl"
                self.transcript.parent.mkdir(parents=True)
                self.transcript.write_text('{"type": "user"}\n{"type": "assistant"}\n', encoding="utf-8")
                self.arguments = pop_chat_fields({"conversation_id": CHAT_ID, "path": "cart.py"})

            with it("should name the chat's transcript"):
                expect(chat_from_environ()[1]).to(equal(self.transcript))

            with it("should point at every line of the transcript so far"):
                expect(chat_from_environ()[2]).to(equal("1-2"))

            with it("should hand the tool only its own arguments"):
                expect(self.arguments).to(equal({"path": "cart.py"}))

        with context("with no transcript by that name"):
            with it("should name no transcript"):
                pop_chat_fields({"conversation_id": CHAT_ID})
                expect(chat_from_environ()[1]).to(equal(Path("unknown")))

    with context("that names no chat"):
        with it("should leave the action without a chat"):
            pop_chat_fields({"path": "cart.py"})
            expect(chat_from_environ()).to(be_none)
