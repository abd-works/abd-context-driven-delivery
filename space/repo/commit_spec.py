"""BDD spec — a commit as an MCP tool answers with it."""
from pathlib import Path

from expects import equal, expect
from mamba import description, it

from harness.installation.repository_toolsets import RepositoryToolsets

RepositoryToolsets(Path(__file__).resolve().parents[2]).ensure_import_path()

from harness.installation.destination import data_of  # noqa: E402
from space.repo.repo import Commit  # noqa: E402


with description("a commit returned by an MCP tool"):
    with it("should reach the caller as its sha, subject, message, and trailer data"):
        commit = Commit("abc123", "Fix it\nTicket: pet-visits")
        expect(data_of(commit)).to(equal({
            "sha": "abc123",
            "subject": "Fix it",
            "message": "Fix it\nTicket: pet-visits",
            "data": {"Ticket": "pet-visits"},
        }))
