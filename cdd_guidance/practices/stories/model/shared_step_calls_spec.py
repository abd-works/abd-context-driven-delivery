"""What each step of a shared story file calls, found by the story, scenario, and words a story test writes the step in."""

import tempfile
from pathlib import Path

from expects import contain, equal, expect
from mamba import after, before, description, it

from cdd_guidance.practices.stories.model.shared_step_calls import SharedStepCalls, step_words

_SHARED = '''\
shared_stories = SharedStories("Maintain Tickets")


@shared_stories.scenario("Edit Ticket Text", "Show a ticket's text")
def _(s):
    @s.when("the Person opens the board")
    def _(world):
        # Board.show()
        #   -> checkout-flow.text
        world.board = world.Board.load()
'''


with description("the calls of a shared story file's steps"):
    with before.each:
        self.folder = tempfile.TemporaryDirectory()
        root = Path(self.folder.name)
        (root / "maintain-tickets.story.shared.py").write_text(_SHARED, encoding="utf-8")
        self.calls = SharedStepCalls(root).called_by("Edit Ticket Text", "Show a ticket's text", "when the Person opens the board.")

    with after.each:
        self.folder.cleanup()

    with it("should hold what the step's body calls"):
        expect(self.calls).to(contain("load"))

    with it("should hold what its realization comments call"):
        expect(self.calls).to(contain("show"))

    with it("should hold the properties its realization comments read"):
        expect(self.calls).to(contain("text"))

    with description("a step a story test writes with marks and a link"):
        with it("should read as the shared file writes it"):
            expect(step_words("*When* the Person opens the [board](model.md#board).")).to(equal("the person opens the board"))
