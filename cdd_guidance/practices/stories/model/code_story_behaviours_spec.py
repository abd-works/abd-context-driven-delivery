"""A story map written as story tests in one language and read back, then one common set of examples on the model.

Each language's part is only the setup: the model type that writes and reads its story tests, and, for a step's code,
one story file in that language. Every example after that is shared and names no language. What one language alone
does stays in that language's own spec (`python/`, `typescript/`, `javascript/`)."""

from expects import be_false, be_true, contain, equal, expect, have_len, raise_error
from mamba import before, context, description, included_context, it, shared_context

from cdd_guidance.practices.stories.model.code_story_model import CodeStoryModelError
from cdd_guidance.practices.stories.model.fixtures.round_trip_story_map import outline, round_trip_story_map
from cdd_guidance.practices.stories.model.javascript.javascript_story_model import JavaScriptStoryModel
from cdd_guidance.practices.stories.model.python.python_story_model import PythonStoryModel
from cdd_guidance.practices.stories.model.story_model import Epic, Scenario, Step, StepType, Story, StoryModel, StoryType
from cdd_guidance.practices.stories.stories import Stories
from cdd_guidance.practices.stories.model.typescript.typescript_story_model import TypeScriptStoryModel

_SCRIPT_TEST = """\
story('Pay For Order', () => {
  scenario('Pay by card', ({ given, when, then }) => {
    given('a cart', () => {
      cart = Cart.holding(book);
    });
    when('the Shopper pays', () => {
      order = cart.checkout();
    });
    then('the order is paid', () => {
      expect(order.paid).toBe(true);
    });
  });
});
"""

_PYTHON_TEST = """\
from story_test import given, scenario, story, then, when

with story("Pay For Order"):
    with scenario("Pay by card"):
        with given("a cart"):
            cart = Cart.holding(book)
        with when("the Shopper pays"):
            order = cart.checkout()
        with then("the order is paid"):
            assert order.paid
"""

_PYTHON_SHARED = """\
shared_stories = SharedStories("Check Out")


@shared_stories.scenario("Pay For Order", "Pay by card")
def _(s):
    @s.when("the Shopper pays")
    def _(world):
        world.order = world.cart.checkout()
"""


def _scenario(name: str, order: int) -> Scenario:
    scenario = Scenario(name=name, sequential_order=order)
    scenario.steps = [
        Step("a context", StepType.GIVEN, 1),
        Step("the action occurs", StepType.WHEN, 2),
        Step("the outcome is observed", StepType.THEN, 3),
    ]
    return scenario


def _voucher_map() -> StoryModel:
    """Four epics, the first holding three sub-epics, each with the story Redeem a voucher and its two scenarios."""
    story_map = StoryModel()
    for number in range(1, 5):
        story_map.epics.append(Epic(f"Epic {number}", number))
    for number in range(1, 4):
        sub_epic = Epic(f"Epic 1.{number}", number)
        story = Story("Redeem a voucher", 1, StoryType.USER)
        story.actors = ["shopper"]
        story.scenarios = [_scenario("Voucher is active", 1), _scenario("Paid order is placed", 2)]
        sub_epic.stories.append(story)
        story_map.epics[0].epics.append(sub_epic)
    return story_map


def _epics_each_with_a_story(count: int) -> StoryModel:
    story_map = StoryModel()
    for number in range(1, count + 1):
        epic = Epic(f"Epic {number}", number)
        epic.stories.append(Story(f"Story {number}", 1))
        story_map.epics.append(epic)
    return story_map


def _name_read_back(model_type, name: str) -> str:
    """The name a story called name has after its language writes it and reads it back."""
    story = Story(name, 1)
    story.actors = ["Customer"]
    model = model_type()
    return model.story_type.load_all(model.writing.story_text(model.story_type(story)))[0].name


with shared_context("a story map written as story tests and read back"):
    with before.all:
        model = self.model_type()
        self.tree = model.render(_voucher_map())
        self.leaf_paths = sorted(path for path in self.tree if model.is_story_file(path))
        self.read_back = model.parse(self.tree)

    with it("should write one story test for each story, in the story's own folder under its sub-epic's"):
        suffix = self.model_type.story_file_suffixes[0]
        expected = [f"tests/epic-1/epic-1-{number}/redeem-a-voucher/redeem_a_voucher{suffix}" for number in (1, 2, 3)]
        expect(self.leaf_paths).to(equal(expected))

    with it("should write a story its epic holds itself in the story's own folder under the epic's"):
        model = self.model_type()
        written = [path for path in model.render(_epics_each_with_a_story(2)) if model.is_story_file(path)]
        suffix = self.model_type.story_file_suffixes[0]
        expect(sorted(written)).to(equal([f"tests/epic-1/story-1/story_1{suffix}", f"tests/epic-2/story-2/story_2{suffix}"]))

    with it("should read a story its epic holds itself back onto that epic, with no sub-epic between"):
        model = self.model_type()
        read = model.parse(model.render(_epics_each_with_a_story(2)))
        expect([(epic.name, [story.name for story in epic.stories], len(epic.epics)) for epic in read.epics]).to(
            equal([("Epic 1", ["Story 1"], 0), ("Epic 2", ["Story 2"], 0)])
        )

    with it("should read an epic's stories back in the map's order, whatever their names"):
        model = self.model_type()
        story_map = StoryModel()
        epic = Epic("Sell Books", 1)
        epic.stories = [Story(name, order) for order, name in enumerate(("Take Order", "Pack Order", "Bill Order"), start=1)]
        story_map.epics.append(epic)
        expect([story.name for story in model.parse(model.render(story_map)).epics[0].stories]).to(equal(["Take Order", "Pack Order", "Bill Order"]))

    with it("should write every file at a path the acceptance tests fidelity declares, when the practice renders"):
        practice = Stories()
        declared = practice.fidelities.entries["acceptance_tests"].declared
        written = practice.formats.adapter(self.format_name).render(_voucher_map())
        expect([path for path in written if not declared.includes(path, self.format_name)]).to(equal([]))

    with it("should write every file at a path the scenarios fidelity declares, when the practice renders"):
        practice = Stories()
        declared = practice.fidelities.entries["scenarios"].declared
        written = practice.formats.adapter(self.format_name).render(_voucher_map())
        expect([path for path in written if not declared.includes(path, self.format_name)]).to(equal([]))

    with it("should write under the tests folder when no root is named"):
        expect([path for path in self.leaf_paths if not path.startswith("tests/")]).to(equal([]))

    with it("should write no examples file, whose data no story names"):
        expect([path for path in self.tree if "/examples/" in path]).to(equal([]))

    with it("should read back each sub-epic's story"):
        expect(self.read_back.epics[0].epics[0].stories).to(have_len(1))

    with it("should read back each story's scenarios"):
        expect(self.read_back.epics[0].epics[0].stories[0].scenarios).to(have_len(2))

    with it("should read back the story's name"):
        expect(self.read_back.epics[0].epics[0].stories[0].name).to(equal("Redeem a voucher"))

    with it("should read back the story's actor"):
        expect(self.read_back.epics[0].epics[0].stories[0].actors).to(equal(["shopper"]))

    with it("should read back every epic, story, kind, actor, background, and scenario of a map that uses them all"):
        files = self.model_type().render(round_trip_story_map())
        expect(outline(self.model_type().load(files), with_scenarios=True)).to(equal(outline(round_trip_story_map(), with_scenarios=True)))

    with it("should read back a story name that ends in a parenthetical"):
        expect(_name_read_back(self.model_type, "Pay Bill (By Card)")).to(equal("Pay Bill (By Card)"))

    with it("should read back a story name without the tier-neutral marker"):
        expect(_name_read_back(self.model_type, "Pay Bill (tier-neutral)")).to(equal("Pay Bill"))

    with it("should read each epic from the folder below a tests root two folders deep"):
        model = self.model_type("stories/tests")
        names = [epic.name for epic in model.parse(model.render(_epics_each_with_a_story(4))).epics]
        expect(names).to(equal(["Epic 1", "Epic 2", "Epic 3", "Epic 4"]))

    with it("should refuse to read a value that is not a tree of story files"):
        expect(lambda: self.model_type().parse("not a tree")).to(raise_error(CodeStoryModelError))


with shared_context("a step read from a story file in code"):
    with it("should hold the code that calls the operation"):
        path, text = self.story_file
        story = next(found for epic in self.model_type().parse({path: text}).descendants.epics() for found in epic.stories)
        when = next(step for step in story.scenarios[0].steps if step.keyword == "When")
        expect(when.body_text).to(contain("cart.checkout()"))


with shared_context("a script story map and its step library"):
    with before.all:
        self.extension = self.model_type.LEAF_EXTENSION
        self.at_default = self.model_type().render(_voucher_map())
        self.in_stories_workspace = self.model_type(tests_root="stories/create-customer").render(_voucher_map())
        self.in_named_folder = self.model_type(tests_root="tests", story_test_folder="test-utils/story-test").render(_voucher_map())

    with it("should seed a new tree with the step library at the tests root"):
        expect(f"tests/story-test{self.extension}" in self.at_default).to(be_true)

    with it("should place the step library at the stories workspace root when the tests root lies under it"):
        expect(f"stories/story-test{self.extension}" in self.in_stories_workspace).to(be_true)

    with it("should write story tests under a tests root the caller names"):
        leaves = [path for path in self.in_stories_workspace if path.endswith(self.model_type.story_file_suffixes[0])]
        expect([path for path in leaves if not path.startswith("stories/create-customer/")]).to(equal([]))

    with it("should place the step library in the folder a pattern names"):
        expect(f"test-utils/story-test/story-test{self.extension}" in self.in_named_folder).to(be_true)

    with it("should leave the tests root without a step library when a pattern names its folder"):
        expect(f"tests/story-test{self.extension}" in self.in_named_folder).to(be_false)

    with it("should keep story tests under the tests root when a pattern names the step library's folder"):
        leaf = next(path for path in self.in_named_folder if path.endswith(self.model_type.story_file_suffixes[0]))
        expect(leaf.startswith("tests/")).to(be_true)

    with it("should read the stories back from a tree that holds the step library"):
        parsed = self.model_type("tests").parse(self.in_named_folder)
        expect(parsed.epics[0].epics[0].stories[0].name).to(equal("Redeem a voucher"))

    with it("should not take the step library for a story file"):
        expect(self.model_type("tests").is_story_file(f"test-utils/story-test/story-test{self.extension}")).to(be_false)

    with it("should take the step library folder its practice names, when the practice makes it"):
        practice = Stories(story_test_folder="test-utils/story-test")
        expect(practice.formats.adapter(self.format_name).story_test_folder).to(equal("test-utils/story-test"))

    with it("should take a shared story file and a screen spec for story files"):
        names = [f"tests/checkout/checkout.story.shared{self.extension}", f"tests/checkout/checkout.story.ui.spec{self.extension}"]
        expect([name for name in names if not self.model_type().is_story_file(name)]).to(equal([]))

    with it("should leave out a story file under an examples folder"):
        expect(self.model_type().is_story_file(f"tests/checkout/examples/card_story.test{self.extension}")).to(be_false)

    with it("should write balanced braces and brackets"):
        leaves = [text for path, text in self.at_default.items() if path.endswith(self.model_type.story_file_suffixes[0])]
        expect([text for text in leaves if text.count("{") != text.count("}") or text.count("[") != text.count("]")]).to(equal([]))

    with it("should register each story and scenario by a call"):
        leaf = next(text for path, text in self.at_default.items() if path.endswith(self.model_type.story_file_suffixes[0]))
        expect(["story('Redeem a voucher', () => {" in leaf, "scenario('Voucher is active'" in leaf, "scenario('Paid order is placed'" in leaf]).to(equal([True, True, True]))


with description("a story map created as story tests") as self:
    with context("in Python"):
        with before.all:
            self.model_type = PythonStoryModel
            self.format_name = "python"
            self.story_file = ("tests/place-orders/check_out_story.test.py", _PYTHON_TEST)

        with included_context("a story map written as story tests and read back"):
            pass

        with included_context("a step read from a story file in code"):
            pass

        with context("with a shared story file"):
            with before.all:
                self.story_file = ("tests/place-orders/check-out.story.shared.py", _PYTHON_SHARED)

            with included_context("a step read from a story file in code"):
                pass

    with context("in TypeScript"):
        with before.all:
            self.model_type = TypeScriptStoryModel
            self.format_name = "typescript"
            self.story_file = ("tests/place-orders/check_out_story.test.ts", _SCRIPT_TEST)

        with included_context("a story map written as story tests and read back"):
            pass

        with included_context("a step read from a story file in code"):
            pass

        with included_context("a script story map and its step library"):
            pass

    with context("in JavaScript"):
        with before.all:
            self.model_type = JavaScriptStoryModel
            self.format_name = "javascript"
            self.story_file = ("tests/place-orders/check_out_story.test.js", _SCRIPT_TEST)

        with included_context("a story map written as story tests and read back"):
            pass

        with included_context("a step read from a story file in code"):
            pass

        with included_context("a script story map and its step library"):
            pass
