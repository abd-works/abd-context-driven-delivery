import tempfile
from pathlib import Path

from expects import equal, expect
from mamba import before, context, description, it

from space.session.idea_file import IdeaFile

_TICKET = """# Maintain Tickets On Board

## Epic: Move Work Forward On Session Board

### Feature: Maintain Tickets

#### Story: Edit Ticket Text

*Person*. A double click edits the card's text.

#### Story: Tag Ticket Session

*Person*. Tags show on the card.
Overlays: none

### Feature: Organize Ticket Hierarchy

#### Story: Add Child Ticket
"""


with description("an idea file") as self:
    with context("that names the stories its work is about"):
        with before.each:
            self.file = Path(tempfile.mkdtemp()) / "ticket.md"
            self.file.write_text(_TICKET, encoding="utf-8")
            self.idea = IdeaFile(self.file)

        with it("should list its stories in order"):
            expect(self.idea.stories).to(equal(["Edit Ticket Text", "Tag Ticket Session", "Add Child Ticket"]))

        with it("should name the stories that leave out the session's overlays"):
            expect(self.idea.stories_without_overlays).to(equal(["Tag Ticket Session"]))

    with context("that is not there"):
        with it("should name no stories"):
            expect(IdeaFile(Path(tempfile.mkdtemp()) / "missing.md").stories).to(equal([]))
