"""How the connect script names the project a chat's cdd calls are for."""

import importlib.util
import os
from pathlib import Path

from expects import equal, expect
from mamba import after, before, context, description, it

_SCRIPT = Path(__file__).resolve().parent / "scripts" / "connect.py"
_URL = "http://127.0.0.1:8790/mcp"
_spec = importlib.util.spec_from_file_location("cdd_connect", _SCRIPT)
connect = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(connect)


with description("the project a chat's connect script names"):
    with context("with the chat's folder passed by the cdd plugin"):
        with it("should be that folder"):
            expect(connect.project_folder([r"C:\dev\pets"])).to(equal(r"C:\dev\pets"))

    with context("with a folder Claude Code never filled in"):
        with it("should be the folder the script runs in"):
            expect(connect.project_folder(["${CLAUDE_PROJECT_DIR}"])).to(equal(os.getcwd()))

    with context("with no folder passed"):
        with it("should be the folder the script runs in"):
            expect(connect.project_folder([])).to(equal(os.getcwd()))


with description("what a chat's connect script prints") as self:
    with before.each:
        self.prior_chat = os.environ.pop(connect.CHAT_ID_VARIABLE, None)

    with after.each:
        os.environ.pop(connect.CHAT_ID_VARIABLE, None)
        if self.prior_chat is not None:
            os.environ[connect.CHAT_ID_VARIABLE] = self.prior_chat

    with context("for an IDE's headers helper, with the chat's folder passed"):
        with it("should be the headers alone, naming that folder and an unnamed chat"):
            expect(connect.answer([r"C:\dev\pets"], _URL, "x-cdd-project", "x-cdd-chat")).to(equal({"x-cdd-project": r"C:\dev\pets", "x-cdd-chat": connect.UNNAMED_CHAT}))

    with context("for a Claude Code chat's headers helper"):
        with it("should name the chat, so the server can follow it to the folder it works in now"):
            os.environ[connect.CHAT_ID_VARIABLE] = "chat-7"
            expect(connect.answer([r"C:\dev\pets"], _URL, "x-cdd-project", "x-cdd-chat")).to(equal({"x-cdd-project": r"C:\dev\pets", "x-cdd-chat": "chat-7"}))

    with context("for a headers helper run by a Claude Code chat process"):
        with it("should name that process, so the server can read the folder its session works in now"):
            headers = connect.answer([r"C:\dev\pets"], _URL, "x-cdd-project", "x-cdd-chat", {"x-cdd-chat-process": "40364"})
            expect(headers["x-cdd-chat-process"]).to(equal("40364"))

    with context("for a language adapter, asked for the server's address in the project's folder"):
        with it("should be the server's address with the headers naming the folder it runs in"):
            expect(connect.answer(["--address"], _URL, "x-cdd-project", "x-cdd-chat")).to(equal({"url": _URL, "headers": {"x-cdd-project": os.getcwd(), "x-cdd-chat": connect.UNNAMED_CHAT}}))

        # A board or graph server started from a chat serves every chat, so it never takes on the chat that started it:
        # the server would otherwise follow that chat to its folder and show that repository to everyone.
        with context("that a Claude Code chat started"):
            with it("should name only the project, never the chat or its process"):
                os.environ[connect.CHAT_ID_VARIABLE] = "chat-7"
                answer = connect.answer(["--address"], _URL, "x-cdd-project", "x-cdd-chat", {"x-cdd-chat-process": "40364"})
                expect(answer["headers"]).to(equal({"x-cdd-project": os.getcwd(), "x-cdd-chat": connect.UNNAMED_CHAT}))
