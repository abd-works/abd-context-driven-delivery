"""How the connect script names the project a chat's cdd calls are for."""

import importlib.util
import json
import os
import shutil
import sys
import tempfile
import threading
from pathlib import Path

from expects import be_true, equal, expect, raise_error
from mamba import after, before, context, description, it

_SCRIPT = Path(__file__).resolve().parent / "scripts" / "connect.py"
_URL = "http://127.0.0.1:8790/mcp"
_REPOSITORY = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location("cdd_connect", _SCRIPT)
connect = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(connect)

# What the pinned runtime's modules build on, loaded with the spec, so an example that imports the runtime times the wait
# for its record and the runtime's own modules rather than the standard library's HTTP client and the toolset framework.
import http.client  # noqa: E402,F401
import harness.agent_tools.claude_chat_process  # noqa: E402,F401


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


# An install swaps the pinned runtime in place; a headers helper that exits then prints nothing, and its chat is cut
# off from cdd until a reload, so the script waits out the swap.
with description("the pinned runtime a chat's connect script imports") as self:
    with before.each:
        self.prior = (connect.HOME, connect.RUNTIME_SWAP_SECONDS, connect.RUNTIME_RETRY_SECONDS)
        self.home = Path(tempfile.mkdtemp())
        connect.HOME = self.home
        connect.RUNTIME_RETRY_SECONDS = 0.005

    with after.each:
        connect.HOME, connect.RUNTIME_SWAP_SECONDS, connect.RUNTIME_RETRY_SECONDS = self.prior
        shutil.rmtree(self.home, ignore_errors=True)

    with context("that an install is swapping, its record written a moment later"):
        with it("should import it once the record is there"):
            connect.RUNTIME_SWAP_SECONDS = 5
            record = json.dumps({"source": str(_REPOSITORY)})
            threading.Timer(0.02, lambda: (self.home / "runtime.json").write_text(record, encoding="utf-8")).start()
            connect.import_runtime()
            expect("harness.mcp.mcp_daemon" in sys.modules).to(be_true)

    with context("whose record stays missing longer than an install swaps it"):
        with it("should fail, naming the missing record"):
            connect.RUNTIME_SWAP_SECONDS = 0.02
            expect(connect.import_runtime).to(raise_error(FileNotFoundError))
