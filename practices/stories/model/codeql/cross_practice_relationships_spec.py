"""Cross-practice edges on the CodeQL story types."""

import mcp.types  # SDK, before harness/mcp is on PYTHONPATH
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[4]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("practices", "tools"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from expects import contain, equal, expect, have_length
from mamba import description, it

from harness.knowledge_graph.model.graph_node import Kind
from harness.knowledge_graph.model.practice_graph import PracticeGraph
from practices.clean_engineering.model.codeql.codeql_model import Module, OoadClass, Operation, Property
from practices.stories.model.codeql.codeql_model import (
    Background,
    Epic,
    Scenario,
    Step,
    Story,
    StoryMap,
)

_FILE = "stories/load_customer_story.test.ts"


def _names(nodes) -> list:
    return [node.name for node in nodes]


with description("Stories CodeQL cross-practice relationships"):
    with it("should wire step phase edges and roll invokes and observes up to the story"):
        graph = PracticeGraph(_REPO_ROOT)
        module = Module("Customer", 1)
        graph.register(module)
        customer = OoadClass("Customer", 1)
        graph.register(customer)
        module.relate(Kind.OWNS, customer)
        customer.relate(Kind.BELONGS_TO, module)
        load = Operation("load", 1)
        identity = Property("identity", 1)
        graph.register(load)
        graph.register(identity)
        customer.relate(Kind.OWNS, load)
        load.relate(Kind.BELONGS_TO, customer)
        customer.relate(Kind.OWNS, identity)
        identity.relate(Kind.BELONGS_TO, customer)

        StoryMap().ensure(
            graph,
            {
                "stories": [
                    {
                        "name": "Load customer",
                        "file": _FILE,
                        "line": 1,
                        "epic": "Onboard",
                        "sub_epic": "Create customer",
                    }
                ],
                "backgrounds": [
                    {"name": "background", "story": "Load customer", "file": _FILE, "line": 4}
                ],
                "scenarios": [
                    {
                        "name": "customer exists",
                        "story": "Load customer",
                        "file": _FILE,
                        "line": 10,
                    }
                ],
                "steps": [
                    {
                        "keyword": "given",
                        "text": "a stored customer",
                        "story": "Load customer",
                        "file": _FILE,
                        "line": 5,
                        "background": "background",
                        "uses_examples": ["storedCustomer"],
                    },
                    {
                        "keyword": "given",
                        "text": "a stored customer",
                        "story": "Load customer",
                        "file": _FILE,
                        "line": 12,
                        "scenario": "customer exists",
                        "uses_examples": ["storedCustomer"],
                    },
                    {
                        "keyword": "when",
                        "text": "My Paradise loads the customer",
                        "story": "Load customer",
                        "file": _FILE,
                        "line": 14,
                        "scenario": "customer exists",
                    },
                    {
                        "keyword": "then",
                        "text": "the identity is stored",
                        "story": "Load customer",
                        "file": _FILE,
                        "line": 16,
                        "scenario": "customer exists",
                        "uses_examples": ["storedCustomer", "otherExample"],
                    },
                ],
                "example_exports": [
                    {
                        "export_name": "storedCustomer",
                        "file": "customer.examples.ts",
                        "line": 3,
                        "demonstrates": ["Customer"],
                    },
                    {
                        "export_name": "otherExample",
                        "file": "customer.examples.ts",
                        "line": 8,
                        "demonstrates": ["Customer"],
                    },
                ],
                "story_calls": [
                    {
                        "story_file": _FILE,
                        "line": 14,
                        "callee_class": "Customer",
                        "callee_operation": "load",
                        "step_text": "My Paradise loads the customer",
                    }
                ],
                "story_observations": [
                    {
                        "story_file": _FILE,
                        "line": 16,
                        "target_class": "Customer",
                        "target_member": "identity",
                        "member_kind": "property",
                    }
                ],
            },
        )

        steps = graph.nodes_of_type(Step)
        given_steps = [step for step in steps if step.text == "a stored customer"]
        when = next(step for step in steps if step.text == "My Paradise loads the customer")
        then = next(step for step in steps if step.text == "the identity is stored")
        expect(given_steps).to(have_length(2))
        for given in given_steps:
            expect(_names(given.related(Kind.LOADS))).to(contain("storedCustomer"))
        expect(when.related(Kind.INVOKES)).to(equal([load]))
        expect(_names(then.related(Kind.OBSERVES))).to(equal(["storedCustomer"]))
        expect(then.related(Kind.OBSERVES)[0].related(Kind.RETRIEVED_USING)).to(equal([identity]))
        expect(then.related(Kind.OBSERVES)[0].related(Kind.DEMONSTRATES)).to(equal([customer]))

        scenario = graph.nodes_of_type(Scenario)[0]
        expect(scenario.related(Kind.INVOKES)).to(equal([load]))
        expect(_names(scenario.related(Kind.OBSERVES))).to(equal(["storedCustomer"]))

        story = graph.nodes_of_type(Story)[0]
        expect(story.related(Kind.INVOKES)).to(equal([load]))
        expect(_names(story.related(Kind.OBSERVES))).to(equal(["storedCustomer"]))

        background = graph.nodes_of_type(Background)[0]
        expect(_names(background.related(Kind.LOADS))).to(equal(["storedCustomer"]))

        epics = graph.nodes_of_type(Epic)
        for epic in epics:
            expect(epic.related(Kind.USES)).to(have_length(1))
            expect(epic.related(Kind.USES)[0]).to(equal(module))
