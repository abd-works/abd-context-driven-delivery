"""Mamba spec: the story tests of a working copy, read into the graph beside its Clean Engineering model.

A step invokes the operations it calls, the operation records the step that invokes it once, and the top-level
epic whose tree holds the step uses the module the operation sits in."""

from pathlib import Path

from expects import be_empty, be_true, equal, expect
from mamba import before, description, it

from cdd_guidance.practices.stories.model.story_model import Epic
from harness.graph.graph import Graph

_SAMPLE = Path(__file__).resolve().parents[3] / "harness" / "graph" / "_examples" / "input"


def _top_epic_of(node):
    while node is not None and not (isinstance(node, Epic) and not isinstance(node.parent, Epic)):
        node = node.parent
    return node


with description("story tests read into the graph beside the Clean Engineering model") as self:
    with before.all:
        self.graph = Graph()
        self.graph.load_files(str(_SAMPLE), ["clean_engineering", "stories"], ["."])
        self.stories = self.graph.practice("stories")
        self.clean = self.graph.practice("clean_engineering")

    with it("should record each step an operation is invoked by under invokedBy"):
        expect(len(self.clean.edges.get("invokedBy", [])) > 0).to(be_true)

    with it("should record the invoking step on the operation only once, as invokedBy"):
        expect(self.clean.edges.get("invokes", [])).to(be_empty)

    with it("should have the top-level epic use the module whose operation its step invokes"):
        uses = {(edge.parent.name, edge.child.name) for edge in self.stories.edges.get("uses", [])}
        expect(("Onboard A Customer", "account-credentials") in uses).to(be_true)

    with it("should have each epic use a module only when a step in that epic's own tree invokes an operation there"):
        owners = {
            (_top_epic_of(edge.parent).name, Path(edge.child.source.file).parent.name)
            for edge in self.stories.edges.get("invokes", [])
        }
        uses = {(edge.parent.name, edge.child.name) for edge in self.stories.edges.get("uses", [])}
        expect(uses - owners).to(equal(set()))
