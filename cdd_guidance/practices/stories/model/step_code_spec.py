"""A step read from a story test in code holds the code its story test gives it, in each language whose story tests hold
code, so the graph links the step to the operations that code calls. A Java story test is a doc comment of steps with no
code, so a Java step holds none."""

from expects import be_empty, contain, expect
from mamba import description, it

from cdd_guidance.practices.stories.model.java.java_story_model import JavaStoryModel
from cdd_guidance.practices.stories.model.javascript.javascript_story_model import JavaScriptStoryModel
from cdd_guidance.practices.stories.model.python.python_story_model import PythonStoryModel
from cdd_guidance.practices.stories.model.typescript.typescript_story_model import TypeScriptStoryModel

_BRACE_TEST = """\
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

_JAVA_TEST = """\
/** Story: Pay For Order
 * SCENARIO: Pay by card
 * WHEN: the Shopper pays
 */
"""


def _when_code(model, path: str, text: str) -> str:
    """The code the When step of the one scenario read from text at path holds."""
    story = next(found for epic in model.parse({path: text}).every_epic() for found in epic.stories)
    return next(step for step in story.scenarios[0].steps if step.keyword == "When").body_text


with description("a step read from a story test in code"):
    with description("written in TypeScript"):
        with it("should hold the code that calls the operation"):
            expect(_when_code(TypeScriptStoryModel(), "tests/place-orders/check_out_story.test.ts", _BRACE_TEST)).to(contain("cart.checkout()"))

    with description("written in JavaScript"):
        with it("should hold the code that calls the operation"):
            expect(_when_code(JavaScriptStoryModel(), "tests/place-orders/check_out_story.test.js", _BRACE_TEST)).to(contain("cart.checkout()"))

    with description("written in a Python story test"):
        with it("should hold the code that calls the operation"):
            expect(_when_code(PythonStoryModel(), "tests/place-orders/check_out_story.test.py", _PYTHON_TEST)).to(contain("cart.checkout()"))

    with description("written in a Python shared story file"):
        with it("should hold the code that calls the operation"):
            expect(_when_code(PythonStoryModel(), "tests/place-orders/check-out.story.shared.py", _PYTHON_SHARED)).to(contain("world.cart.checkout()"))

    with description("written in Java"):
        with it("should hold no code, since a Java story test writes none"):
            expect(_when_code(JavaStoryModel(), "tests/place-orders/CheckOutStory.java", _JAVA_TEST)).to(be_empty)
