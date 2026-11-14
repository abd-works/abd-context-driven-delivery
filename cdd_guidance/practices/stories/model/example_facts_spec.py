"""An example's facts, read from the code that declares it in each language a story test is written in: the names it
shows, which link it to the classes it demonstrates, and the members read off it, which link it to the properties it is
retrieved through."""

import functools

from expects import contain, equal, expect
from mamba import before, description, it

from harness.graph.graph import Graph
from cdd_guidance.practices.stories.model.story_model import StoryModel
from cdd_guidance.practices.stories.model.story_recording import StoryRecording, imported_example_files

_DECLARED = {
    "tests/checkout.examples.ts": "export function validCart() { return new Cart(items.first) }\nexport const EMPTY_CART = new Cart()\n",
    "tests/checkout.examples.js": "export function validCart() { return new Cart(items.first) }\nexport const EMPTY_CART = new Cart()\n",
    "tests/checkout_examples.py": "VALID_CART = Cart(items.first)\n\n\ndef empty_cart():\n    return Cart()\n",
    "tests/CheckoutExamples.java": "public class CheckoutExamples {\n  public static final Cart VALID_CART = new Cart(items.first);\n  public static Cart emptyCart() { return new Cart(); }\n}\n",
}


@functools.cache
def _stories_practice():
    """The Stories practice of a graph, made once: every example reads facts through it and none changes it."""
    return Graph().practice("stories")


def _facts(name: str) -> dict:
    model = StoryModel()
    model.source_texts.update(_DECLARED)
    return StoryRecording(model, _stories_practice(), None).example_facts("tests/story.ts", name)


with description("the facts of an example"):
    with before.all:
        _stories_practice()

    with description("declared as a TypeScript or JavaScript function"):
        with it("should name the class it builds"):
            expect(_facts("validCart")["source_names"]).to(contain("Cart"))

    with description("declared as a TypeScript or JavaScript constant"):
        with it("should name the class it builds"):
            expect(_facts("EMPTY_CART")["source_names"]).to(contain("Cart"))

    with description("declared as a Python module constant"):
        with it("should name the class it builds"):
            expect(_facts("VALID_CART")["source_names"]).to(contain("Cart"))

        with it("should read the members read in its declaration"):
            expect(_facts("VALID_CART")["source_reads"]).to(contain("first"))

    with description("declared as a Python function"):
        with it("should name the class it builds"):
            expect(_facts("empty_cart")["source_names"]).to(contain("Cart"))

    with description("declared as a Java static method"):
        with it("should name the class it builds"):
            expect(_facts("emptyCart")["source_names"]).to(contain("Cart"))

    with description("of an examples module a Python story test imports from its package root"):
        with it("should be looked for under each folder above the story test"):
            files = imported_example_files("shop/tests/checkout_story.test.py", "from examples.checkout_examples import VALID_CART\n")
            expect(files).to(contain("shop/examples/checkout_examples.py"))

    with description("of an examples class a Java story test imports"):
        with it("should be looked for under each folder above the story test"):
            files = imported_example_files("src/test/java/shop/CheckoutStory.java", "import static shop.examples.CheckoutExamples.emptyCart;\n")
            expect(files).to(contain("src/test/java/shop/examples/CheckoutExamples.java"))
