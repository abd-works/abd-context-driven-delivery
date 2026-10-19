"""A BDD spec model is its graph node."""

import sys
from pathlib import Path

from expects import be, contain, equal, expect
from mamba import before, description, it

_REPO = Path(__file__).resolve().parents[4]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from harness.graph.graph import Graph

from cdd_guidance.practices.bdd.model.bdd_model import BddModel, _parse_sketch
from cdd_guidance.practices.bdd.model.nodes import Context, Description, Observation


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


with description("a bdd sketch with realization fences"):
    with it("should attach call graphs to observations"):
        sketch = """
a cart
  that has items
```
cart.checkout()
  -> payment.charge()
it should complete payment
```
"""
        descriptions = _parse_sketch(sketch)
        observation = descriptions[0].contexts[0].observations[0]
        expect(observation.name).to(equal("should complete payment"))
        expect(observation.call_graph[0].text).to(equal("cart.checkout()"))
        expect(observation.call_graph[1].text).to(equal("payment.charge()"))


_HEADED = """
## clean engineering:

### **Session**

+ new(name: str): str

## behavior driven development:

### a session

#### that is new

```
it should return keep_log to the agent
  -> expect(instructions).to contain "log_action"
```

#### that is selected

##### with only a name

```
-> session.select(name)
it should bind the existing session from the environment
  -> expect(session.name).to equal name
```
"""


with description("a sketch that carries behavior under headings"):
    with it("should build the fenced tree under the behavior section"):
        from cdd_guidance.practices.bdd.model.sketch.sketch_bdd_model import SketchBddModel

        spec = SketchBddModel().parse(_HEADED)
        session = spec.descriptions[0]
        expect(session.name).to(equal("a session"))
        expect(session.contexts[0].name).to(equal("that is new"))
        expect(session.contexts[0].observations[0].name).to(equal("should return keep_log to the agent"))
        expect(session.contexts[0].observations[0].surface_lines).to(
            contain('expect(instructions).to contain "log_action"')
        )
        selected = session.contexts[1]
        expect(selected.name).to(equal("that is selected"))
        named = selected.contexts[0]
        expect(named.name).to(equal("with only a name"))
        expect(named.observations[0].name).to(equal("should bind the existing session from the environment"))
        expect(named.observations[0].surface_lines[0]).to(equal("session.select(name)"))
