"""GraphStoryModel supplies rule-ready step and scenario fields."""

import sys
import tempfile
from pathlib import Path

from expects import contain, equal, expect
from mamba import before, description, it

_REPO = Path(__file__).resolve().parents[3]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from graph import Graph  # noqa: E402
from practices.stories.model.graph_story_model import GraphStoryModel  # noqa: E402
from practices.stories.model.story_model import Scenario, Step, StepType, Story, StoryModel  # noqa: E402


with description("GraphStoryModel rule data"):
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
        model = StoryModel("map")
        model.epics[0].stories = [story]
        graph = Graph()
        practice = graph.practice("stories")
        practice.source_root = str(self.root)
        GraphStoryModel(model).record(practice)
        self.practice = practice

    with it("should emit Given, When, and Then node types"):
        expect(set(self.practice.nodes.keys())).to(contain("Given", "When", "Then"))

    with it("should attach step payload with phase and concepts"):
        when_nodes = self.practice.nodes.get("When", [])
        expect(len(when_nodes)).to(equal(1))
        expect(when_nodes[0].data.get("phase")).to(equal("when"))
        expect(when_nodes[0].data.get("concepts")).to(contain("Cart"))

    with it("should wire scenario steps edges"):
        scenario = self.practice.nodes["Scenario"][0]
        steps = [
            edge.child
            for edge in self.practice.edges.get("steps", [])
            if edge.parent is scenario
        ]
        expect(len(steps)).to(equal(3))
