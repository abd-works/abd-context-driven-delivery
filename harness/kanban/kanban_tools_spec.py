"""The session board as tools an agent calls (cdd MCP)."""
import json
import tempfile
from pathlib import Path

from expects import contain, equal, expect
from mamba import before, context, description, it

from harness.installation.installer import Installer

Installer(repo=Path(__file__).resolve().parents[2]).ensure_import_path()

from harness.kanban.kanban import Kanban  # noqa: E402

DISCOVERY_DONE = [
    line
    for practice, practice_class, fidelity in (
        ("stories", "Stories", "story_map"), ("ddd", "Ddd", "bounded_context"), ("ux", "Ux", "ia"),
        ("clean_engineering", "CleanEngineering", "modules"), ("bdd", "Bdd", "behavior"),
    )
    for line in (
        f"2026-10-31T01:00:00Z generate /work {practice} {fidelity} markdown {practice} no-chat",
        f"2026-10-31T01:00:01Z validate {practice_class} {fidelity} no-chat",
        f"2026-10-31T01:00:02Z review /work {practice} {fidelity} markdown {practice} no-chat",
    )
]

with description("the board tools") as self:
    with context("with a project whose sessions folder holds a ticket and a backlog item"):
        with before.each:
            self.project = Path(tempfile.mkdtemp(prefix="kanban-tools-"))
            sessions = self.project / ".sessions"
            (sessions / "pet-visits").mkdir(parents=True)
            (sessions / "pet-visits" / "session.json").write_text(json.dumps({"title": "Pet visits"}), encoding="utf-8")
            (sessions / "pet-visits" / "session.log").write_text("\n".join(DISCOVERY_DONE) + "\n", encoding="utf-8")
            (sessions / "_backlog").mkdir()
            (sessions / "_backlog" / "returns.md").write_text("# Returns and refunds\n", encoding="utf-8")
            self.tools = Kanban(str(self.project))

        with it("should return every column of the board"):
            columns = [column["name"] for column in self.tools.board()["columns"]]
            expect(columns).to(equal(["Backlog", "Discovery", "Specification", "Implementation", "Complete"]))

        with context("that pulls a done ticket"):
            with before.each:
                self.pulled = self.tools.pull("pet-visits")

            with it("should return the ticket in its next stage"):
                expect(self.pulled["column"]).to(equal("Specification"))

        with context("that starts a backlog item"):
            with before.each:
                self.started = self.tools.start("Returns and refunds", "feature")

            with it("should return the new ticket in Discovery"):
                expect((self.started["name"], self.started["column"])).to(equal(("returns-and-refunds", "Discovery")))

        with context("that closes a ticket"):
            with before.each:
                self.tools.close("pet-visits")

            with it("should show the ticket in Complete"):
                complete = next(column for column in self.tools.board()["columns"] if column["name"] == "Complete")
                expect([ticket["name"] for ticket in complete["tickets"]]).to(contain("pet-visits"))

        with context("that archives a ticket"):
            with before.each:
                self.tools.archive("pet-visits")

            with it("should leave the ticket off the board"):
                expect(json.dumps(self.tools.board())).not_to(contain("pet-visits"))
