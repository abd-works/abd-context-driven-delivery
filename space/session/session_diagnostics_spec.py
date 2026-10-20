"""Session diagnostics — writes the session section in diagnostics.json."""
import json
import shutil
import sys
import tempfile
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from harness.installation.bootstrap import ensure_import_path
from harness.installation.installer import Installer

ensure_import_path(_REPO_ROOT)

from expects import contain, equal, expect
from mamba import description, it

from space.session.session_diagnostics import SessionDiagnostics, write_session_diagnostics
from space.session.session_probe import probe_session_log


with description("session diagnostics"):
    with it("should probe session.log for generate and validate in a temp session"):
        result = probe_session_log()
        expect(result.get("color")).to(equal("green"))
        expect(result.get("checks", {}).get("generate_line")).to(equal(True))
        expect(result.get("checks", {}).get("validate_line")).to(equal(True))
        expect(result.get("checks", {}).get("chat_pointer")).to(equal(True))

    with it("should install session-diagnostics as a slash command with MCP invoke"):
        tree = Path(tempfile.mkdtemp())
        try:
            mcp = Installer(ide="Cursor", path=tree, repo=_REPO_ROOT).install([SessionDiagnostics()])
            command_path = tree / "commands" / "space" / "session" / "session-diagnostics.md"
            expect(command_path.is_file()).to(equal(True))
            text = command_path.read_text(encoding="utf-8")
            expect(text).to(contain("session-diagnostics.session_diagnostics"))
            expect(text).to(contain("diagnostics.json"))
            names = [op.mcp_name for op in mcp.mcp_operations]
            expect(names).to(contain("session-diagnostics.session_diagnostics"))
        finally:
            shutil.rmtree(tree, ignore_errors=True)

    with it("should write the session section to diagnostics.json"):
        tree = Path(tempfile.mkdtemp())
        try:
            installer = Installer(ide="Cursor", path=tree, repo=_REPO_ROOT)
            report = write_session_diagnostics(installer)
            expect(report.startswith("green\n")).to(equal(True))
            data = json.loads((tree / "diagnostics.json").read_text(encoding="utf-8"))
            expect("session" in data).to(equal(True))
            expect(data["session"].get("color")).to(equal("green"))
        finally:
            shutil.rmtree(tree, ignore_errors=True)
