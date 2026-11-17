"""Mamba spec for a Python runnable-story Story Map."""

import ast
import sys
from pathlib import Path

_HERE = Path(__file__).resolve()
for _candidate in _HERE.parents:
    if (_candidate / "practices" / "stories").is_dir() and (
        _candidate / "contexts"
    ).is_dir():
        if str(_candidate) not in sys.path:
            sys.path.insert(0, str(_candidate))
        break

from mamba import description, context, it, before
from expects import equal, have_len, be_true, contain, expect, raise_error

from cdd_guidance.practices.stories.model.story_model import Epic, Step, StepType, Story, StoryType
from cdd_guidance.practices.stories.model.story_model import Scenario
from cdd_guidance.practices.stories.model.story_model import StoryModel
from cdd_guidance.practices.stories.model.code_story_model import CodeStoryModelError
from cdd_guidance.practices.stories.model.python.python_story_model import PythonStoryModel


def _story_map_with_stories() -> StoryModel:
    story_map = StoryModel()
    for i in range(1, 5):
        story_map.epics.append(Epic(f"Epic {i}", i))
    first = story_map.epics[0]
    for j in range(1, 4):
        sub = Epic(f"Epic 1.{j}", j)
        story = Story("Book a room", 1, StoryType.USER)
        story.actors = ["guest"]
        story.domain_terms = ["Room", "Reservation"]
        story.scenarios.append(
            Scenario(name="a room is available", sequential_order=1)
        )
        sub.stories.append(story)
        first.epics.append(sub)
    return story_map


def _story_map_with_a_but_step() -> StoryModel:
    """One epic, one story, one scenario whose last step is a But, as markdown scenarios often end."""
    story_map = StoryModel()
    epic = Epic("Remove Tickets", 1)
    story = Story("Delete Ticket", 1, StoryType.USER)
    scenario = Scenario(name="a ticket is deleted", sequential_order=1)
    for order, (keyword, text, step_type) in enumerate(
        [("Given", "a ticket on the board", StepType.GIVEN), ("When", "the Person deletes it", StepType.WHEN), ("Then", "the board no longer shows it", StepType.THEN), ("But", "the ticket's work is kept", StepType.THEN)], 1
    ):
        step = Step(text, step_type, order)
        step.keyword = keyword
        scenario.steps.append(step)
    story.scenarios.append(scenario)
    epic.stories.append(story)
    story_map.epics.append(epic)
    return story_map


def _imported_from_story_test(content: str) -> set:
    return {alias.name for node in ast.walk(ast.parse(content)) if isinstance(node, ast.ImportFrom) and node.module == "story_test" for alias in node.names}


def _step_verbs_used(content: str) -> set:
    return {item.context_expr.func.id for node in ast.walk(ast.parse(content)) if isinstance(node, ast.With) for item in node.items if isinstance(item.context_expr, ast.Call) and isinstance(item.context_expr.func, ast.Name)}


# Seen 2026-11-17: scenarios rendered from markdown to Python used but_ without importing it, so the file failed to run.
with description("a Python story test rendered from scenarios whose last step is a But"):
    with before.each:
        py = PythonStoryModel()
        tree = py.render(_story_map_with_a_but_step())
        self.content = next(text for path, text in tree.items() if py.is_story_file(path))

    with it("should import every step verb it uses"):
        expect(_step_verbs_used(self.content) - _imported_from_story_test(self.content)).to(equal(set()))

    with it("should open each scenario one indent inside its story, as the repository's story tests are written"):
        expect(self.content).to(contain('\nwith story("Delete Ticket"):\n    with scenario("a ticket is deleted"):\n        with given("a ticket on the board"):'))


with description("a Python runnable-story Story Map") as self:
    with context(
        "that holds a rendered code Story Map with 4 Epics and 3 Epics under the first Epic"
    ):
        with before.each:
            self.py = PythonStoryModel()
            self.canonical = _story_map_with_stories()
            self.tree = self.py.render(self.canonical)
            self.leaf_paths = sorted(path for path in self.tree if self.py.is_story_file(path))
            self.leaf_contents = [self.tree[p] for p in self.leaf_paths]

        with context("every leaf file"):
            with it("should be named `<sub_epic_snake>_story.test.py` in the parent epic folder"):
                for path in self.leaf_paths:
                    expect(path.endswith("_story.test.py")).to(be_true)
                    expect("/epic-1/epic_1_" in path).to(be_true)
                    expect("/book-a-room/" in path).to(equal(False))

            with it("should parse as a valid Python module"):
                for content in self.leaf_contents:
                    ast.parse(content)

            with it("should open the story"):
                for content in self.leaf_contents:
                    expect(content).to(contain('with story("Book a room")'))

            with it("should carry domain terms for markdown round-trip"):
                for content in self.leaf_contents:
                    expect(content).to(contain("Domain terms: Room, Reservation"))

        with context("every Scenario"):
            with it("should name the scenario"):
                for content in self.leaf_contents:
                    expect(content).to(contain('with scenario("a room is available")'))

    with context("that has been rendered and parsed back without edits"):
        with before.each:
            self.canonical = _story_map_with_stories()
            self.parsed = PythonStoryModel().parse(PythonStoryModel().render(self.canonical))

        with it("should preserve Story and Scenario counts under each Epic"):
            first_sub = self.parsed.epics[0].epics[0]
            expect(first_sub.stories).to(have_len(1))
            expect(first_sub.stories[0].scenarios).to(have_len(1))

        with it("should restore the Story name and actor"):
            story = self.parsed.epics[0].epics[0].stories[0]
            expect(story.name).to(equal("Book a room"))
            expect(story.actors).to(equal(["guest"]))

    with context("that is not a valid Python story-spec tree"):
        with it("should reject parse"):
            expect(lambda: PythonStoryModel().parse("not a tree")).to(
                raise_error(CodeStoryModelError)
            )

    with context("that holds a story file whose story keeps code between its scenarios"):
        with before.each:
            self.parsed = PythonStoryModel().parse({
                "tests/checkout/checkout_story.test.py": (
                    "from story_test import given, scenario, story\n"
                    "\n"
                    "# Epic: Checkout\n"
                    "\n"
                    "# Story: Pay by card\n"
                    'with story("Pay by card"):\n'
                    "    card = Card()\n"
                    '    with scenario("the card is charged"):\n'
                    '        with given("a basket"):\n'
                    "            pass\n"
                )
            })

        with context("with the story renamed and the map written again"):
            with before.each:
                self.parsed.epics[0].stories[0].name = "Pay with a card"
                self.written = PythonStoryModel().render(self.parsed)

            with it("should keep the code the story shares between its scenarios"):
                expect(self.written["tests/checkout/checkout_story.test.py"]).to(contain("    card = Card()"))
