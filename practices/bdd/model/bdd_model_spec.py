"""A BDD spec model is its graph node."""

import sys
from pathlib import Path

from expects import be, contain, equal, expect
from mamba import before, description, it

_REPO = Path(__file__).resolve().parents[3]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from harness.graph.graph import Graph

from practices.bdd.model.bdd_model import BddModel
from practices.bdd.model.nodes import Context, Description, Observation


with description("a bdd spec on a graph"):
    with before.each:
        self.graph = Graph()
        self.spec = BddModel(self.graph)
        self.description = Description("a cart")
        self.context = Context("that has a line")
        self.observation = Observation("should show the line")
        self.context.observations.append(self.observation)
        self.description.contexts.append(self.context)
        self.spec.descriptions.append(self.description)

    with it("should be the graph node for the description"):
        expect(self.description.node).to(be(self.description))

    with it("should keep the description on the spec graph"):
        expect(self.context.graph).to(be(self.graph))
        expect(self.observation.graph).to(be(self.graph))

    with it("should record contexts, observations, and belongsTo"):
        practice = self.graph.practice("bdd")
        contexts = [(edge.parent.name, edge.child.name) for edge in practice.edges.get("contexts", [])]
        observations = [(edge.parent.name, edge.child.name) for edge in practice.edges.get("observations", [])]
        belongs = [(edge.parent.name, edge.child.name) for edge in practice.edges.get("belongsTo", [])]
        expect(contexts).to(contain(("a cart", "that has a line")))
        expect(observations).to(contain(("that has a line", "should show the line")))
        expect(belongs).to(contain(("that has a line", "a cart"), ("should show the line", "that has a line")))

    with it("should open the same spec from the graph"):
        restored = BddModel(self.graph)
        expect(restored.descriptions[0].name).to(equal("a cart"))
        expect(restored.descriptions[0].contexts[0].name).to(equal("that has a line"))
        expect(restored.descriptions[0].contexts[0].observations[0].name).to(equal("should show the line"))
