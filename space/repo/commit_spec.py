"""BDD spec — a commit as an MCP tool answers with it."""
from pathlib import Path

from expects import equal, expect
from mamba import description, it

from harness.installation.installer import Installer

Installer(repo=Path(__file__).resolve().parents[2]).ensure_import_path()

from space.repo.repo import Commit  # noqa: E402


with description("a commit returned by an MCP tool"):
    with it("should reach the caller as its sha and message"):
        expect(Commit("abc123", "Fix it").to_mcp_result()).to(equal({"sha": "abc123", "message": "Fix it"}))
