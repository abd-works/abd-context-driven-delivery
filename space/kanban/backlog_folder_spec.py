"""The Backlog's folder and where each idea's file lies (model: space/kanban/.context/kanban-model.md, BacklogFolder)."""
import shutil
import tempfile
from pathlib import Path

from expects import equal, expect
from mamba import after, before, context, description, it

from space.kanban.backlog_folder import BacklogFolder


def write(path: Path, text: str = "# Idea\n") -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


with description("a Backlog folder") as self:
    with before.each:
        self.folder = Path(tempfile.mkdtemp()) / "_backlog"
        write(self.folder / "returns.md")
        write(self.folder / "checkout" / "checkout.md")
        write(self.folder / "checkout" / "gift-cards.md")
        write(self.folder / "pet-visits" / "pet-visits.md")
        write(self.folder / "pet-visits" / "session.json", "{}")
        write(self.folder / "pet-visits" / "notes.md")
        self.backlog = BacklogFolder(self.folder)

    with after.each:
        shutil.rmtree(self.folder.parent, ignore_errors=True)

    def names(self) -> list[str]:
        return [path.relative_to(self.folder).as_posix() for path in self.backlog.idea_files()]

    with it("should hold each file of its own, each parent and its children, and a ticket moved back by its own file alone"):
        expect(self.names()).to(equal(["checkout/checkout.md", "checkout/gift-cards.md", "pet-visits/pet-visits.md", "returns.md"]))

    with it("should say a child's parent is the file of its folder's name"):
        expect(self.backlog.place_of(self.folder / "checkout" / "gift-cards.md").parent_file).to(equal(self.folder / "checkout" / "checkout.md"))

    with it("should say a ticket moved back holds its ticket's work"):
        expect(self.backlog.place_of(self.folder / "pet-visits" / "pet-visits.md").holds_ticket).to(equal(True))

    with context("whose idea of its own is moved under another kept as one file"):
        with before.each:
            write(self.folder / "refunds.md")
            self.backlog.place_of(self.folder / "returns.md").move_under(self.backlog.place_of(self.folder / "refunds.md"))

        with it("should keep both files in a folder of the parent's name"):
            expect(self.names()).to(equal(["checkout/checkout.md", "checkout/gift-cards.md", "pet-visits/pet-visits.md", "refunds/refunds.md", "refunds/returns.md"]))

    with context("whose only child is moved out"):
        with before.each:
            self.backlog.place_of(self.folder / "checkout" / "gift-cards.md").move_out()

        with it("should keep the child's file in the Backlog's own folder, and the parent's in its folder"):
            expect(self.names()).to(equal(["checkout/checkout.md", "gift-cards.md", "pet-visits/pet-visits.md", "returns.md"]))
