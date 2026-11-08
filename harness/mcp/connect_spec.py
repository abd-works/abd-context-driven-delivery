"""How the connect script names the project a chat's cdd calls are for."""

import importlib.util
import os
from pathlib import Path

from expects import equal, expect
from mamba import description, it, context

_SCRIPT = Path(__file__).resolve().parent / "scripts" / "connect.py"
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


with description("what a chat's connect script prints"):
    with context("for an IDE's headers helper, with the chat's folder passed"):
        with it("should be the headers alone, naming that folder"):
            expect(connect.answer([r"C:\dev\pets"], "http://127.0.0.1:8790/mcp", "x-cdd-project")).to(equal({"x-cdd-project": r"C:\dev\pets"}))

    with context("for a language adapter, asked for the server's address in the project's folder"):
        with it("should be the server's address with the headers naming the folder it runs in"):
            expect(connect.answer(["--address"], "http://127.0.0.1:8790/mcp", "x-cdd-project")).to(equal({"url": "http://127.0.0.1:8790/mcp", "headers": {"x-cdd-project": os.getcwd()}}))
