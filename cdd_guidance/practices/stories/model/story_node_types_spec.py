"""Stories' node types: the relationships a story node's evidence decides, and the types a session's stories scope."""

from expects import be_true, contain, equal, expect
from mamba import before, context, description, it

from cdd_guidance.practices.stories.model.story_node_types import StoryNodeTypes


class _Node:
    """A model object as the evidence reads it: its name, its type, its source text, and what it holds."""

    def __init__(self, name: str, kind: str, text: str = "", steps: list | None = None, phase: str = "") -> None:
        self.name = name
        self.kind = kind
        self.phase = phase
        self.steps = steps or []
        self.source = type("Source", (), {})()
        self.source.text = text

    def semantic_type(self) -> str:
        return self.kind

    def subtree(self) -> list:
        return [self, *self.steps]


with description("Stories' node types"):
    with before.each:
        self.types = StoryNodeTypes()

    with it("should scope the story map's ten node types by a session's stories"):
        expect(len(self.types.scope_types)).to(equal(10))
        expect(self.types.scope_types).to(contain("Example"))

    with context("with a step whose source calls an operation"):
        with it("should link the step to the operation it invokes"):
            step = _Node("place order", "Step", "cart.place_order(book)")
            expect(self.types.links(step, "invokes", _Node("place_order", "Operation"))).to(be_true)

        with it("should not link it to an operation it does not call"):
            step = _Node("place order", "Step", "cart.place_order(book)")
            expect(self.types.links(step, "invokes", _Node("cancel", "Operation"))).to(equal(False))

    with context("with a scenario and one of its Given steps"):
        with it("should link the scenario to that step as its given"):
            given = _Node("an empty cart", "Step", phase="given")
            scenario = _Node("Order one book", "Scenario", steps=[given])
            expect(self.types.links(scenario, "given", given)).to(be_true)

    with it("should link a story to what bears its name, in any case"):
        expect(self.types.links(_Node("Place Order", "Story"), "specifiedBy", _Node("place order", "Spec"))).to(be_true)
