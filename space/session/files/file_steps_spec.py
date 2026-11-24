"""Specs for a story test's steps as the Files app shows them: each thing a step invokes or observes opens in place on
the line of the step that names it, titled as the class it belongs to names it. Python decides both, and the page draws
what it is sent (release-1-2-fixes report, section 7, item 13; scenario Follow Story Steps To Code)."""

from types import SimpleNamespace

from expects import equal, expect
from mamba import before, context, description, it

from space.session.files.file_steps import StepCallout, StoryTestCode

# A Python story test: its Given on line 3 calls its seed ticket_on_board on line 6, below a comment naming it; its When on
# line 8 calls delete on line 10; its Then on line 12, whose words name delete, observes CHECKOUT_TICKET on line 14.
PYTHON_STORY = "\n".join(
    [
        '"""Delete Ticket: delete takes a ticket off the board."""',
        "",
        '@s.given("a ticket on the board")',
        "def _(world):",
        "    # ticket_on_board seeds it",
        "    world.ticket = ticket_on_board(world)",
        "",
        '@s.when("the Person deletes it")',
        "def _(world):",
        "    world.ticket.delete(world.board)",
        "",
        '@s.then("delete leaves no ticket")',
        "def _(world):",
        "    assert ticket_left(world) == CHECKOUT_TICKET",
    ]
)
PYTHON_STEPS = [3, 8, 12]

# A TypeScript story test: its When on line 1 calls delete on line 3, below a comment naming it.
TYPESCRIPT_STORY = "\n".join(["when('the Person deletes it', () => {", "  // delete takes it off the board", "  ticket.delete(board)", "})"])


with description("a story test's code") as self:
    with context("in Python"):
        with before.each:
            self.code = StoryTestCode(PYTHON_STORY, "python", PYTHON_STEPS)

        with it("should find what the Given calls on the line that calls it, not on the comment above"):
            expect(self.code.line_naming(3, "ticket_on_board")).to(equal(6))

        with it("should find what the When calls on the line that calls it"):
            expect(self.code.line_naming(8, "delete")).to(equal(10))

        with it("should find what the Then observes on the line that compares it"):
            expect(self.code.line_naming(12, "CHECKOUT_TICKET")).to(equal(14))

        with it("should keep a name only the step's words hold on the step's own line"):
            expect(self.code.line_naming(12, "delete")).to(equal(12))

        with it("should keep a name only a later step calls on the step's own line"):
            expect(self.code.line_naming(3, "delete")).to(equal(3))

    with context("in TypeScript"):
        with it("should find what the step calls on the line that calls it, not on the comment above"):
            expect(StoryTestCode(TYPESCRIPT_STORY, "typescript", [1]).line_naming(1, "delete")).to(equal(3))


with description("a callout of a step") as self:
    with context("to an operation of a class"):
        with it("should be titled by the class and the operation"):
            expect(StepCallout("call", 10, SimpleNamespace(owner="Ticket", name="delete")).title).to(equal("Ticket.delete"))

    with context("to a function of its module, which no class holds"):
        with it("should be titled by the function alone"):
            expect(StepCallout("call", 6, SimpleNamespace(owner="", name="ticket_on_board")).title).to(equal("ticket_on_board"))
