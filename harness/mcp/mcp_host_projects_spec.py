"""BDD spec — one cdd server answering calls that name different projects."""
import shutil
import sys
import tempfile
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from expects import contain, equal, expect
from mamba import after, before, context, description, it

from harness.mcp.mcp_server import McpHost
from space.session import Sessions

_FILE_MANAGER = "space.session.file_manager:FileManager"
_GENERATE = "cdd_guidance.actions.generate.generate:Generate"


def _project(file_name: str) -> Path:
    folder = Path(tempfile.mkdtemp(prefix="cdd-host-project-")).resolve()
    (folder / ".git").mkdir()
    (folder / file_name).write_text("kept\n", encoding="utf-8")
    return folder


def _names(listing) -> list[str]:
    return [entry.name for entry in listing.entries]


with description("a cdd server answering every chat"):
    with before.each:
        self.orders = _project("order.md")
        self.billing = _project("invoice.md")
        self.host = McpHost.from_refs((_FILE_MANAGER, _GENERATE), repo=str(_REPO_ROOT), project=str(self.orders))

    with after.each:
        shutil.rmtree(self.orders, ignore_errors=True)
        shutil.rmtree(self.billing, ignore_errors=True)

    with context("with calls that name different projects"):
        with it("should answer each call from the project it names"):
            self.host.dispatch("file-manager.list", {}, self.orders)
            expect(_names(self.host.dispatch("file-manager.list", {}, self.billing))).to(contain("invoice.md"))

        with it("should leave the other project's files out of each answer"):
            self.host.dispatch("file-manager.list", {}, self.billing)
            expect(_names(self.host.dispatch("file-manager.list", {}, self.orders))).not_to(contain("invoice.md"))

        with context("with a session open in each project"):
            with before.each:
                for project, name in ((self.orders, "orders"), (self.billing, "billing")):
                    sessions = Sessions(project)
                    sessions.open(sessions.create(name, project))

            with it("should log each call in the session of the project it names"):
                self.host.dispatch("generate.generate", {"guidance": "stories-story-map"}, self.orders)
                self.host.dispatch("generate.generate", {"guidance": "stories-story-map"}, self.billing)
                logged = (self.billing / ".sessions" / "billing" / "session.log").read_text(encoding="utf-8")
                expect(logged.count("tool generate.generate")).to(equal(1))

            with it("should work each action in the session of the project it names"):
                reply = self.host.dispatch("generate.generate", {"guidance": "stories-story-map"}, self.billing)
                expect(reply).to(contain("Session billing"))
