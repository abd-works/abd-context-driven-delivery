"""A story map recorded on a graph supplies rule-ready step and scenario fields."""

import sys
import tempfile
from pathlib import Path

from expects import contain, equal, expect
from mamba import after, before, context, description, it

_REPO = Path(__file__).resolve().parents[4]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from harness.graph.graph import Graph  # noqa: E402
from cdd_guidance.practices.stories.model.source_location import SourceLocation  # noqa: E402
from cdd_guidance.practices.stories.model.story_model import Epic, Scenario, Step, StepType, Story, StoryModel  # noqa: E402


with description("a story map recorded on a graph"):
    with before.each:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        story = Story("Submit Order")
        scenario = Scenario("Happy path", story_name="Submit Order")
        scenario.steps = [
            Step("cart has items", step_type=StepType.GIVEN, sequential_order=1, keyword="Given"),
            Step(
                "customer checks out",
                step_type=StepType.WHEN,
                sequential_order=2,
                keyword="When",
                concepts=["Cart"],
            ),
            Step(
                "order is placed",
                step_type=StepType.THEN,
                sequential_order=3,
                keyword="Then",
            ),
        ]
        story.scenarios = [scenario]
        model = StoryModel()
        epic = Epic("Place Orders", 1)
        epic.append_story(story)
        model.append_epic(epic)
        graph = Graph()
        graph.open(Path(str(self.root)))
        practice = graph.practice("stories")
        model.record(practice)
        self.practice = practice

    with it("should emit Given, When, and Then node types"):
        expect(self.practice.in_graph.node_types).to(contain("Given", "When", "Then"))

    with it("should attach step payload with phase and concepts"):
        when_nodes = self.practice.in_graph.nodes("When")
        expect(len(when_nodes)).to(equal(1))
        expect(when_nodes[0].get_fact("phase")).to(equal("when"))
        expect(when_nodes[0].get_fact("concepts")).to(contain("Cart"))

    with it("should wire scenario steps edges"):
        scenario = self.practice.in_graph.nodes("Scenario")[0]
        steps = [
            edge.child
            for edge in self.practice.in_graph.edges("steps")
            if edge.parent is scenario
        ]
        expect(len(steps)).to(equal(3))


def _imports_of(root: Path, file: str, text: str) -> dict:
    """The imported modules the Story node records for a story read from file, a story test holding text."""
    story = Story("Onboard Customer")
    story.source = SourceLocation(file, 1, 1)
    epic = Epic("Onboard", 1)
    epic.append_story(story)
    model = StoryModel()
    model.append_epic(epic)
    model.source_texts[file] = text
    graph = Graph()
    graph.open(Path(str(root)))
    practice = graph.practice("stories")
    model.record(practice)
    return practice.in_graph.nodes("Story")[0].get_fact("imported_modules")


with description("a story read from a story test that imports its examples"):
    with before.each:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    with after.each:
        self.tmp.cleanup()

    with context("that is TypeScript"):
        with it("should map each imported name to the module the import names"):
            text = 'import { validCustomer, lapsed as lapsedCustomer } from "./examples/customers.examples";\n'
            expect(_imports_of(self.root, "tests/onboard.story.shared.ts", text)).to(equal(
                {"validCustomer": "./examples/customers.examples", "lapsedCustomer": "./examples/customers.examples"}
            ))

    with context("that is Python"):
        with it("should map each imported name to its module as a folder path"):
            text = "from .examples.customers_examples import (\n    valid_customer,\n    lapsed as lapsed_customer,\n)\n"
            expect(_imports_of(self.root, "tests/onboard_story_test.py", text)).to(equal(
                {"valid_customer": "./examples/customers_examples", "lapsed_customer": "./examples/customers_examples"}
            ))

    with context("that is Java"):
        with it("should map a static import to its class file and a class import to itself"):
            text = (
                "import static shop.onboard.examples.CustomersExamples.validCustomer;\n"
                "import shop.onboard.examples.LapsedExamples;\n"
            )
            expect(_imports_of(self.root, "tests/OnboardStoryTest.java", text)).to(equal(
                {
                    "validCustomer": "shop/onboard/examples/CustomersExamples",
                    "LapsedExamples": "shop/onboard/examples/LapsedExamples",
                }
            ))
