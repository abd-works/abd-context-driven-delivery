"""How Clean Engineering reads code into its graph: each class's properties and operations, and the edges that say which
class a property's value is and which parameters an operation takes."""

from expects import be_true, equal, expect, have_key
from mamba import before, context, description, it

from cdd_guidance.practices.clean_engineering.model.python.python_class_model import PythonCleanEngineeringModel
from cdd_guidance.practices.clean_engineering.rules.class_graph import ClassGraph
from cdd_guidance.practices.clean_engineering.rules.rule_examples import practice_from_files

_CART = (
    "class Cart:\n"
    "    def __init__(self) -> None:\n"
    "        self.lines = []\n"
)


def _targets(fixture, kind: str, source_name: str) -> list[str]:
    """The names of the nodes an edge of kind leads to from the node called source_name."""
    return sorted(edge.child.name for edge in fixture.practice.reading.in_graph.edges(kind) if edge.parent.name == source_name)


with description("Clean Engineering reading code into its graph"):
    with context("with a getter whose return type is another class"):
        with before.all:
            self.fixture = practice_from_files(
                {
                    "shop/cart.py": _CART,
                    "shop/checkout.py": (
                        "from shop.cart import Cart\n\n\n"
                        "class Checkout:\n"
                        "    @property\n"
                        "    def basket(self) -> Cart:\n"
                        "        return Cart()\n"
                    ),
                }
            )

        with it("should give the getter's property node a hasType edge to the class it returns"):
            expect(_targets(self.fixture, "hasType", "basket")).to(equal(["Cart"]))

        with it("should make the owning class depend on the class the getter returns"):
            expect(_targets(self.fixture, "dependsOn", "Checkout")).to(equal(["Cart"]))

    with context("with a getter named like a class that returns text"):
        with before.all:
            self.fixture = practice_from_files(
                {
                    "shop/cart.py": _CART,
                    "shop/label.py": (
                        "class Label:\n"
                        "    @property\n"
                        "    def cart(self) -> str:\n"
                        "        return 'cart'\n"
                    ),
                }
            )

        with it("should give the getter's property node no hasType edge"):
            expect(_targets(self.fixture, "hasType", "cart")).to(equal([]))

    with context("with an operation that takes parameters"):
        with before.all:
            self.fixture = practice_from_files(
                {"shop/till.py": "class Till:\n    def charge(self, amount: int, note: str) -> None:\n        pass\n"}
            )
            self.charge = next(node for node in self.fixture.practice.reading.in_graph.nodes("Operation") if node.name == "charge")

        with it("should link each parameter through hasParameter, in the order the operation declares them"):
            expect([edge.child.name for edge in self.fixture.practice.reading.graph.edges_from("hasParameter", self.charge)]).to(
                equal(["amount", "note"])
            )

        with it("should keep no copy of the parameters as a fact beside the parameter nodes"):
            expect(self.charge.facts).not_to(have_key("parameters"))

    with context("with a getter parsed and not yet read into a graph"):
        with before.all:
            parsed = PythonCleanEngineeringModel().parse("class Till:\n    @property\n    def total(self) -> int:\n        return 0\n")
            self.getter = parsed.file_module().classes[0].operations[0]

        with it("should already say it is read as a property"):
            expect(self.getter.type).to(equal("Property"))

        with it("should still be an operation that is a property"):
            expect(self.getter.is_property).to(be_true)

    with context("with a module whose public file documents its internal design under a heading"):
        with before.all:
            self.fixture = practice_from_files(
                {
                    "shop/.context/module-context.md": "# Shop\n",
                    "shop/cart.py": '"""The cart.\n\n## Internal\n\nHow lines are kept."""\n\n\nclass Cart:\n    pass\n',
                    "shop/_helpers.py": "# _ holds nothing public\n",
                }
            )
            self.shop = next(node for node in self.fixture.practice.reading.in_graph.nodes("Module") if node.name == "shop")

        with it("should read the documentation from the module the file was parsed into"):
            expect(self.shop.get_fact("public_source_internal")).to(equal("heading"))

        with it("should count only its public files"):
            expect(self.shop.get_fact("public_source_files")).to(equal(1))

    with context("with a module whose other public file does not parse, read by a load of one edited file"):
        with before.all:
            self.fixture = practice_from_files(
                {
                    "shop/.context/module-context.md": "# Shop\n",
                    "shop/cart.py": _CART,
                    "shop/broken.py": "class Broken(:\n    pass\n",
                }
            )
            self.fixture.read_only(["shop/cart.py"])
            self.shop = next(node for node in self.fixture.practice.reading.in_graph.nodes("Module") if node.name == "shop")

        with it("should keep the file that does not parse on its module, as a load of the whole folder does"):
            expect([kept.split(":")[0] for kept in self.shop.get_fact("unreadable_sources") or []]).to(equal(["shop/broken.py"]))

    with context("with a class read again by a refresh"):
        with before.all:
            self.fixture = practice_from_files({"shop/cart.py": _CART, "shop/till.py": "class Till:\n    pass\n"})
            self.index = self.fixture.practice.reading.code_index
            self.index.classes_named("Cart")
            self.fixture.practice.reading.graph.refresh([str(self.fixture.root / "shop/cart.py")])
            self.cart = next(node for node in self.fixture.practice.reading.in_graph.nodes("OoadClass") if node.name == "Cart")

        with it("should name the class the refresh read, not the one it replaced"):
            expect(self.index.classes_named("Cart")).to(equal([self.cart]))

        with it("should be the index the class rules ask"):
            expect(ClassGraph(self.fixture.context).named("Till")).to(equal(self.index.classes_named("Till")))

    with context("with members that call and read another object's members"):
        with before.all:
            self.fixture = practice_from_files(
                {
                    "app/board.ts": (
                        "export class Board {\n"
                        "  get shown(): string[] { return [] }\n"
                        "  select(name: string): void { this.picked = name }\n"
                        "}\n\n"
                        "export class BoardClient {\n"
                        "  constructor(private board: Board) {}\n"
                        "  select(): void {\n"
                        "    this.board.select('x')\n"
                        "  }\n"
                        "  opensLeft(): boolean {\n"
                        "    return this.board.shown.length > 2\n"
                        "  }\n"
                        "}\n"
                    ),
                }
            )

        with it("should record that an operation invokes the member of its name it calls on another object"):
            expect(_targets(self.fixture, "invokes", "select")).to(equal(["select"]))

        with it("should record that an operation invokes the property it reads"):
            expect(_targets(self.fixture, "invokes", "opensLeft")).to(equal(["shown"]))

    with context("with a class whose heritage clause holds braced type arguments"):
        with before.all:
            self.fixture = practice_from_files(
                {
                    "app/page.tsx": (
                        "export class PageFailureView extends Component<{ children: ReactNode }, { failure: string }> {\n"
                        "  render() {\n"
                        "    return this.props.children\n"
                        "  }\n"
                        "}\n"
                    ),
                }
            )

        with it("should read the members of the class body, not of the type arguments"):
            expect(_targets(self.fixture, "owns", "PageFailureView")).to(equal(["render"]))

    with context("with a folder holding only story tests"):
        with before.all:
            self.fixture = practice_from_files(
                {
                    "shop/cart.py": _CART,
                    "shop/pay/pay_story.test.py": "with story('Pay'):\n    pass\n",
                }
            )

        with it("should hold no package for the folder"):
            packages = [node.name for node in self.fixture.practice.reading.in_graph.nodes("Package")]
            expect(packages).to(equal(["shop"]))
