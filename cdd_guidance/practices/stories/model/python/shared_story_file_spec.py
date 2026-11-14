"""A Python shared story file read as the code of its stories' scenarios: each step's code from its function, and each
example from the fixture its examples module builds; and a render of it to markdown, with its steps and its examples."""

import tempfile
from pathlib import Path

from expects import contain, equal, expect
from mamba import after, before, description, it

import cdd_guidance.practices  # noqa: F401 - registers the practices with the practice catalogue
from cdd_guidance.practices.stories.model.python.nodes import PythonStory
from cdd_guidance.practices.stories.model.python.shared_story_file import SharedStoryFile
from harness.guidance.practice_catalogue import PracticeCatalogue

_EXAMPLES = '''\
from dataclasses import dataclass


@dataclass(frozen=True)
class SessionSeed:
    name: str
    title: str


CHECKOUT_FLOW = SessionSeed("checkout-flow", "Checkout flow")
CHECKOUT_FLOW_TEXT = "Pay for the basket."
'''

_SHARED = '''\
"""Edit Ticket Text. Map: story-map.md."""

from shop.shop_examples import CHECKOUT_FLOW, CHECKOUT_FLOW_TEXT

shared_stories = SharedStories("Maintain Tickets")


def board_of(world):
    return world.Board.load().show()


@shared_stories.scenario("Edit Ticket Text", "Show a ticket's text")
def _(s):
    @s.given("the ticket checkout-flow holds Pay for the basket.")
    def _(world):
        world.project.seed_session(CHECKOUT_FLOW)

    @s.when("the Person opens the board")
    def _(world):
        world.board = board_of(world)

    @s.then("checkout-flow's card shows Pay for the basket.")
    def _(world):
        expect(world.Ticket.card(CHECKOUT_FLOW.name)).to(equal(CHECKOUT_FLOW_TEXT))

    @s.and_("its card is open")
    def _(world):
        pass
'''

_MAP = """\
# Story Map

(E) Move Work Forward
    (E) Maintain Tickets
        (S) Person --> Edit Ticket Text
"""


def _project() -> tempfile.TemporaryDirectory:
    """A folder holding the shared story file, its examples module, and its story map."""
    folder = tempfile.TemporaryDirectory()
    root = Path(folder.name)
    (root / "shop").mkdir()
    (root / "shop" / "shop_examples.py").write_text(_EXAMPLES, encoding="utf-8")
    (root / "shop" / "edit-ticket-text.story.shared.py").write_text(_SHARED, encoding="utf-8")
    (root / "story-map.md").write_text(_MAP, encoding="utf-8")
    return folder


with description("a Python shared story file"):
    with before.each:
        self.folder = _project()
        self.root = Path(self.folder.name)
        story = SharedStoryFile(_SHARED, [self.root]).stories(PythonStory)[0]
        self.scenario = story.scenarios[0]

    with after.each:
        self.folder.cleanup()

    with description("read as the code of its scenarios"):
        with it("should hold each step in its words, by the kind its function is"):
            expect([(step.keyword, step.text) for step in self.scenario.steps]).to(equal([
                ("Given", "the ticket checkout-flow holds Pay for the basket."),
                ("When", "the Person opens the board"),
                ("Then", "checkout-flow's card shows Pay for the basket."),
            ]))

        with it("should continue the step before an And"):
            expect([step.text for step in self.scenario.steps[2].ands]).to(equal(["its card is open"]))

        with it("should give a step the code of the helpers it calls"):
            expect(self.scenario.steps[1].body_text).to(contain("world.Board.load().show()"))

        with it("should take each fixture the scenario names as an example with its fields"):
            expect(self.scenario.examples["CHECKOUT_FLOW"].cells()).to(equal({"group": "SessionSeed", "name": "checkout-flow", "title": "Checkout flow"}))

        with it("should give an example the names of the statements that use it"):
            expect(self.scenario.examples["CHECKOUT_FLOW"].fixture_facts["source_names"]).to(contain("Ticket"))

        with it("should give an example the members read off it"):
            expect(self.scenario.examples["CHECKOUT_FLOW"].fixture_facts["source_reads"]).to(equal(["name"]))

    with description("rendered to markdown"):
        # Rendered once; the examples only read the markdown.
        with before.all:
            folder = _project()
            root = Path(folder.name)
            practice = PracticeCatalogue.create("stories", fidelity="scenarios")
            paths = [str(root / "shop" / "edit-ticket-text.story.shared.py"), str(root / "story-map.md")]
            self.markdown = str(practice.fidelities.current.render_files("markdown", paths, "python")["content"])
            folder.cleanup()

        with it("should write the scenario's steps"):
            expect(self.markdown).to(contain("*When* the Person opens the board"))

        with it("should write the examples its fixtures give"):
            expect(self.markdown).to(contain("| CHECKOUT_FLOW | SessionSeed | checkout-flow | Checkout flow |"))
