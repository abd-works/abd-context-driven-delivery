"""Story tests are written in Python, TypeScript, or JavaScript: a fidelity that offers TypeScript offers JavaScript, and
a JavaScript story test is written, read back, and read into the knowledge graph as a TypeScript one is."""

import tempfile
from pathlib import Path

from expects import equal, expect
from mamba import before, context, description, it

import cdd_guidance.practices  # noqa: F401 - registers the practices a graph holds
from cdd_guidance.practices.stories.stories import Stories
from harness.graph.graph import Graph

_CODE_LANGUAGES = ["javascript", "python", "typescript"]
# The formats a fidelity writes that are no programming language.
_OTHER_FORMATS = {"markdown", "drawio", "whiteboard", "thin_slice", "realization", "json", "miro", "sketch", "desktop"}

_STORY_MAP = """\
# Story Map — Shop

# (E) Check Out

## (E) Pay

### (S) Shopper --> Pay For Order
### (S) Shopper --> Refund Order
"""

_STORY_TEST = """\
import { scenario, story } from "../../story-test.js";

story("Pay For Order", () => {
  scenario("Pay by card", ({ given, when, then }) => {
    given("a cart with a book", () => {
      // domain state only
    });
    when("the Shopper pays by card", () => {
      // test code goes here
    });
    then("the order is paid", () => {
      // test code goes here
    });
  });
});
"""


def _shop_with_story_test(extension: str) -> tempfile.TemporaryDirectory:
    """A project with a story map and one story test written with extension."""
    folder = tempfile.TemporaryDirectory()
    root = Path(folder.name)
    (root / ".context").mkdir()
    (root / ".context" / "story-map.md").write_text(_STORY_MAP, encoding="utf-8")
    story_folder = root / "story_tests" / "check-out" / "pay"
    story_folder.mkdir(parents=True)
    (story_folder / f"pay_for_order_story.test.{extension}").write_text(_STORY_TEST, encoding="utf-8")
    return folder


def _steps_read(folder: tempfile.TemporaryDirectory) -> list[str]:
    """The steps the graph holds after loading the whole working copy in folder."""
    graph = Graph()
    graph.load_working_copy(folder.name, {"stories": folder.name}, force=True)
    part = graph.practices.named("stories").reading.in_graph
    return [f"{node.type}: {node.name}" for node in part.nodes() if node.type in ("Given", "When", "Then")]


with description("the languages Stories writes story tests in") as self:
    with context("that its fidelities offer"):
        with before.all:
            self.fidelities = list(Stories().fidelities)

        with it("should be Python, TypeScript and JavaScript, and no other"):
            offered = {label for fidelity in self.fidelities for label in fidelity.outputs}
            expect(sorted(offered - _OTHER_FORMATS)).to(equal(_CODE_LANGUAGES))

        with it("should have JavaScript in every fidelity that has TypeScript"):
            without = [fidelity.name for fidelity in self.fidelities if "typescript" in fidelity.outputs and "javascript" not in fidelity.outputs]
            expect(without).to(equal([]))

    with context("that the practice holds a format for"):
        with it("should be Python, TypeScript and JavaScript, and no other"):
            code = sorted(name for name in Stories().formats if name not in _OTHER_FORMATS)
            expect(code).to(equal(_CODE_LANGUAGES))

    with context("with a JavaScript story test in a working copy"):
        with before.all:
            self.javascript = _shop_with_story_test("js")
            self.typescript = _shop_with_story_test("ts")

        with it("should read its steps into the knowledge graph"):
            expect(_steps_read(self.javascript)).to(equal(
                ["Given: given a cart with a book", "When: when the Shopper pays by card", "Then: then the order is paid"]
            ))

        with it("should read the same steps a TypeScript story test gives"):
            expect(_steps_read(self.javascript)).to(equal(_steps_read(self.typescript)))
