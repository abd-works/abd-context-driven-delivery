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
from harness.graph.graph import Source  # noqa: E402
from cdd_guidance.practices.stories.model.story_model import Epic, Scenario, Step, StepType, Story, StoryModel  # noqa: E402


with description("a story map recorded on a graph"):
    with before.each:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        story = Story("Submit Order")
        scenario = Scenario("Happy path")
        scenario.steps = [
            Step("cart has items", step_type=StepType.GIVEN, sequential_order=1),
            Step("customer checks out", step_type=StepType.WHEN, sequential_order=2),
            Step("order is placed", step_type=StepType.THEN, sequential_order=3),
        ]
        scenario.steps[1].concepts = ["Cart"]
        story.scenarios = [scenario]
        model = StoryModel()
        epic = Epic("Place Orders", 1)
        epic.stories.append(story)
        model.epics.append(epic)
        graph = Graph()
        graph.reads.open(Path(str(self.root)))
        practice = graph.practices.named("stories")
        model.record(practice)
        self.practice = practice

    with it("should emit Given, When, and Then node types"):
        expect(self.practice.reading.in_graph.node_types).to(contain("Given", "When", "Then"))

    with it("should attach step payload with phase and concepts"):
        when_nodes = self.practice.reading.in_graph.nodes("When")
        expect(len(when_nodes)).to(equal(1))
        expect(when_nodes[0].get_fact("phase")).to(equal("when"))
        expect(when_nodes[0].get_fact("concepts")).to(contain("Cart"))

    with it("should wire scenario steps edges"):
        scenario = self.practice.reading.in_graph.nodes("Scenario")[0]
        steps = [
            edge.child
            for edge in self.practice.reading.in_graph.edge_index.of("steps")
            if edge.parent is scenario
        ]
        expect(len(steps)).to(equal(3))


with description("a merged story map whose two maps each hold a story a story test specifies"):
    with before.each:
        self.tmp = tempfile.TemporaryDirectory()
        model = StoryModel()
        for order, file in enumerate(["story-map.md", "story-map.drawio"], start=1):
            story = Story("Submit Order")
            story.source = Source(file, 1, 1)
            epic = Epic(f"Place Orders {order}", order)
            epic.stories.append(story)
            model.epics.append(epic)
        read = Story("Submit Order")
        read.scenarios = [Scenario("Happy path")]
        model.test_scenarios.take([read], "tests/submit_order_story.test.ts")
        graph = Graph()
        graph.reads.open(Path(self.tmp.name))
        self.practice = graph.practices.named("stories")
        model.record(self.practice)

    with after.each:
        self.tmp.cleanup()

    with it("should record the story test's scenario under both stories"):
        scenario = self.practice.reading.in_graph.nodes("Scenario")[0]
        stories = [edge.parent for edge in self.practice.reading.in_graph.edge_index.of("scenarios") if edge.child is scenario]
        expect(len(stories)).to(equal(2))


def _imports_of(root: Path, file: str, text: str) -> dict:
    """The imported modules the Story node records for a story read from file, a story test holding text."""
    story = Story("Onboard Customer")
    story.source = Source(file, 1, 1)
    epic = Epic("Onboard", 1)
    epic.stories.append(story)
    model = StoryModel()
    model.epics.append(epic)
    model.sources.add(file, text)
    graph = Graph()
    graph.reads.open(Path(str(root)))
    practice = graph.practices.named("stories")
    model.record(practice)
    return practice.reading.in_graph.nodes("Story")[0].get_fact("imported_modules")


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

