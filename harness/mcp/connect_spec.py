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
