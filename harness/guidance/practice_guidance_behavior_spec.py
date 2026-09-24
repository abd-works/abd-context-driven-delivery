"""BDD development — practice format, companion, and render.

Hierarchy 1:1 with harness/guidance/.context/practice-guidance-sketch.md
theme: behaviors.
"""
import sys
import tempfile
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("practices", "tools", "actions"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from expects import contain, equal, expect
from mamba import before, context, description, it

from actions.render.render import Render
from practices.bdd.bdd import Bdd
from practices.clean_engineering.clean_engineering import CleanEngineering
from practices.ddd.ddd import Ddd
from practices.examples.car.car import Car
from practices.stories.model.markdown.nodes import MarkdownStoryMap
from practices.stories.stories import Stories

_CLASS_MARKDOWN = """\
# Shop

*Shop* is the cart module.

## Cart

*Cart* holds line items and places orders.

Cart(owner: str)
------
owner: str
----
place_order(): Order
"""

_CLASS_PYTHON = """\
class Cart:
    \"\"\"Cart holds line items and places orders.\"\"\"

    def __init__(self, owner: str) -> None:
        self.owner = owner

    def place_order(self) -> "Order": ...
"""

_STORY_MAP = """\
(E) Manage Customer Orders
    (E) Place New Order
        (S) Customer --> Browse Product Catalog
"""

_SCENARIOS = """\
# Browse Product Catalog

### Default

*Given* a customer
*When* the customer browses the catalog
*Then* products are listed
"""


with description("a practice"):
    with context("that has been loaded from its markdown"):
        with before.each:
            self.practice = CleanEngineering()

        with it("should take each fidelity's default format from that fidelity's Default format"):
            expect(
                {
                    name: child.default_format
                    for name, child in self.practice.fidelities.entries.items()
                }
            ).to(equal({"modules": "markdown", "model": "python", "code": "python"}))

        with it("should keep Default format off the fidelity overview"):
            expect(self.practice.fidelities["model"].overview).not_to(contain("Default format"))
            expect(self.practice.fidelities["model"].overview).to(contain("Design the object model"))

        with it("should take each fidelity's stage from that fidelity's Stage"):
            expect(
                {name: child.stage for name, child in self.practice.fidelities.entries.items()}
            ).to(
                equal(
                    {
                        "modules": "discovery",
                        "model": "specification",
                        "code": "implementation",
                    }
                )
            )

        with context("with a format passed at construction"):
            with before.each:
                self.practice = CleanEngineering(fidelity="model", format="markdown")

            with it("should use the passed format"):
                expect(self.practice.format).to(equal("markdown"))

        with context("with no format passed at construction"):
            with before.each:
                self.practice = CleanEngineering(fidelity="model")

            with it("should use the current fidelity's default format"):
                expect(self.practice.format).to(equal("python"))

        with context("with a Clean Engineering name on a fidelity"):
            with before.each:
                self.practice = Bdd(fidelity="behavior")
                self.child = self.practice.fidelities["behavior"]

            with it("should treat that Clean Engineering fidelity as the companion"):
                expect(self.practice.fidelities.current.clean_engineering.fidelity).to(
                    equal("model")
                )

            with it("should take Default format and Stage from the lines under the fidelity heading"):
                expect(self.child.default_format).to(equal("python"))
                expect(self.child.stage).to(equal("specification"))

            with it("should use that Default format on the practice"):
                expect(self.practice.format).to(equal("python"))

        with context("with no Clean Engineering name on a fidelity"):
            with it("should leave that fidelity without a companion"):
                expect(self.practice.fidelities["modules"].clean_engineering).to(equal(None))

    with context("that has been asked for guidance"):
        with context("with a Clean Engineering companion on the current fidelity"):
            with before.each:
                self.practice = Bdd(fidelity="behavior")

            with it("should include that companion's instructions"):
                expect(self.practice.guidance).to(contain("Design the object model"))

            with it("should include that companion's instructions on the fidelity"):
                expect(self.practice.fidelities["behavior"].instructions).to(
                    contain("Design the object model")
                )

        with context("with no Clean Engineering companion on the current fidelity"):
            with before.each:
                self.practice = CleanEngineering(fidelity="model")

            with it("should not include Clean Engineering instructions"):
                expect(self.practice.guidance).not_to(contain("Behavior-driven development"))

    with context("that has been asked to render"):
        with context("with no format folders"):
            with context("with no Clean Engineering companion on the current fidelity"):
                with before.each:
                    self.practice = Car()
                    self.source = "keep this text"
                    self.result = self.practice.render("python", self.source)

                with it("should skip conversion"):
                    expect(self.result["content"]).to(equal(self.source))

        with context("with an object model"):
            with before.each:
                self.model = MarkdownStoryMap().parse(_STORY_MAP)
                self.result = Stories(fidelity="story_map").render(
                    "drawio", self.model
                )

            with it("should render that model into the requested format"):
                expect(self.result["content"]).to(contain("mxGraphModel"))

        with context("with a tool whose context lives in the code layer"):
            with before.each:
                self.root = Path(tempfile.mkdtemp(prefix="story-code-"))
                leaf = (
                    self.root
                    / "tests"
                    / "manage-customer-orders"
                    / "place-new-order"
                    / "browse-product-catalog"
                    / "browse_product_catalog_story.test.py"
                )
                leaf.parent.mkdir(parents=True)
                leaf.write_text(
                    "Story: Browse Product Catalog\nActor: Customer\n",
                    encoding="utf-8",
                )
                self.tool = Stories(fidelity="story_map", format="python")
                self.tool.path = str(self.root)
                self.tool.workspace = type("WorkspacePath", (), {"path": str(self.root)})()
                self.result = self.tool.render("markdown", self.tool)

            with it("should instantiate the object model from that code"):
                expect(str(self.result["content"])).to(contain("Browse Product Catalog"))

            with it("should render that object model into the requested format"):
                expect(str(self.result["content"])).to(contain("Manage Customer Orders"))


with description("a class model"):
    with context("that has been generated by the model fidelity"):
        with context("that has been generated in markdown"):
            with context("that has been re-rendered in python"):
                with it("should be python of that class model"):
                    result = CleanEngineering(fidelity="model").render(
                        "python", _CLASS_MARKDOWN, source="markdown"
                    )
                    expect(result["content"]).to(contain("class Cart"))

        with context("that has been generated in python"):
            with context("that has been re-rendered in markdown"):
                with it("should be markdown of that class model"):
                    result = CleanEngineering(fidelity="model").render(
                        "markdown", _CLASS_PYTHON, source="python"
                    )
                    expect(result["content"]).to(contain("Cart"))


with description("a story map"):
    with context("that has been generated by the story-map fidelity"):
        with context("that has been generated in markdown"):
            with context("that has been re-rendered in drawio"):
                with it("should be drawio of that story map"):
                    result = Stories(fidelity="story_map").render(
                        "drawio", _STORY_MAP, source="markdown"
                    )
                    expect(result["content"]).to(contain("mxGraphModel"))

        with context("that has been generated in drawio"):
            with context("that has been re-rendered in markdown"):
                with it("should be markdown of that story map"):
                    drawio = Stories(fidelity="story_map").render(
                        "drawio", _STORY_MAP, source="markdown"
                    )["content"]
                    result = Stories(fidelity="story_map").render(
                        "markdown", drawio, source="drawio"
                    )
                    expect(result["content"]).to(contain("Manage Customer Orders"))


with description("story scenarios"):
    with context("that have been generated by the scenarios fidelity"):
        with context("that have been generated in markdown"):
            with context("that have been re-rendered in python"):
                with it("should be python of those scenarios"):
                    result = Stories(fidelity="scenarios").render(
                        "python", _SCENARIOS, source="markdown"
                    )
                    expect(str(result["content"])).to(contain("Browse Product Catalog"))

        with context("that have been generated in python"):
            with context("that have been re-rendered in markdown"):
                with it("should be markdown of those scenarios"):
                    python_tree = {
                        "tests/stories/scenarios/browse-product-catalog/browse_product_catalog_story.test.py": (
                            "Story: Browse Product Catalog\n"
                            "SCENARIO: Default\n"
                        )
                    }
                    result = Stories(fidelity="scenarios").render(
                        "markdown", python_tree, source="python"
                    )
                    expect(str(result["content"])).to(contain("Browse Product Catalog"))


with description("building blocks"):
    with context("that have been generated by the building-blocks fidelity"):
        with context("that have been generated in markdown"):
            with context("that have been re-rendered in python"):
                with it("should be python of those building blocks"):
                    result = Ddd(fidelity="building_blocks").render(
                        "python", _CLASS_MARKDOWN, source="markdown"
                    )
                    expect(result["content"]).to(contain("class Cart"))

        with context("that have been generated in python"):
            with context("that have been re-rendered in markdown"):
                with it("should be markdown of those building blocks"):
                    result = Ddd(fidelity="building_blocks").render(
                        "markdown", _CLASS_PYTHON, source="python"
                    )
                    expect(result["content"]).to(contain("Cart"))


with description("a behavior tree"):
    with context("that has been generated by the behavior fidelity"):
        with context("that has been generated in python"):
            with context("that has been re-rendered in markdown"):
                with it("should be markdown of that behavior tree"):
                    result = Bdd(fidelity="behavior").render(
                        "markdown", _CLASS_PYTHON, source="python"
                    )
                    expect(result["content"]).to(contain("Cart"))

        with context("that has been generated in markdown"):
            with context("that has been re-rendered in python"):
                with it("should be python of that behavior tree"):
                    result = Bdd(fidelity="behavior").render(
                        "python", _CLASS_MARKDOWN, source="markdown"
                    )
                    expect(result["content"]).to(contain("class Cart"))


with description("a render"):
    with context("that has been invoked with listed practices"):
        with it("should return one conversion per practice"):
            results = Render().render(
                [
                    CleanEngineering(fidelity="model"),
                    CleanEngineering(fidelity="model"),
                ],
                format="markdown",
                content=_CLASS_PYTHON,
            )
            expect(len(results)).to(equal(2))
