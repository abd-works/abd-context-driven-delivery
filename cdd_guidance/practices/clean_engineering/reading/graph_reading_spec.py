"""How Clean Engineering reads code into its graph: each class's properties and operations, and the edges that say which
class a property's value is and which parameters an operation takes."""

from expects import be_true, contain, equal, expect, have_key
from mamba import before, context, description, it

from cdd_guidance.practices.clean_engineering.model.python.python_class_model import PythonCleanEngineeringModel
from cdd_guidance.practices.clean_engineering.reading.production_classes import ProductionClasses
from cdd_guidance.practices.clean_engineering.rules.rule_examples import practice_from_files
from cdd_guidance.practices.stories.model.fixtures.round_trip_story_map import round_trip_story_map
from cdd_guidance.practices.stories.model.whiteboard.nodes import WhiteboardStoryModel
from cdd_guidance.practices.clean_engineering.model.whiteboard.whiteboard_class_model import WhiteboardCleanEngineeringModel
from cdd_guidance.practices.clean_engineering.model.base_class_model import CleanEngineeringModel, Module
from cdd_guidance.practices.clean_engineering.reading.code_read import DESCRIBED_FACT

_CART = (
    "class Cart:\n"
    "    def __init__(self) -> None:\n"
    "        self.lines = []\n"
)


# A Clean Engineering class model of the shop folder, describing a ledger no code declares yet.
_SHOP_MODEL = (
    "# shop\n"
    "\n"
    "## Ledger <<Entity>>\n"
    "\n"
    "------\n"
    "+ balance: int\n"
    "----\n"
    "+ record(entry: str): str\n"
)

# A DDD domain model of the shop folder, which DDD reads in its own format and Clean Engineering leaves to it.
_SHOP_DOMAIN_MODEL = (
    "# Domain Model — Shop\n"
    "\n"
    "## Sales | custom\n"
    "\n"
    "### Cart\n"
    "\n"
    "#### Cart <<Aggregate Root>> <<Entity>>\n"
    "\n"
    "------\n"
    "+ total: int\n"
    "----\n"
    "+ add(item: str): Cart\n"
)


def _classes(fixture) -> list:
    """The classes Clean Engineering's graph holds, by node id."""
    return sorted(fixture.practice.reading.in_graph.nodes("OoadClass"), key=lambda node: node.node_id)


def _modules_board() -> str:
    """A Clean Engineering modules view saved as a whiteboard: one module, shop, drawn as its card."""
    model = CleanEngineeringModel("shop")
    shop = Module("shop", 1)
    shop.description = "Sell what is in the cart."
    model.modules.append(shop)
    return WhiteboardCleanEngineeringModel().render(model)


def _targets(fixture, kind: str, source_name: str) -> list[str]:
    """The names of the nodes an edge of kind leads to from the node called source_name."""
    return sorted(edge.child.name for edge in fixture.practice.reading.in_graph.edge_index.of(kind) if edge.parent.name == source_name)


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
            expect([edge.child.name for edge in self.fixture.practice.reading.graph.edges.from_parent("hasParameter", self.charge)]).to(
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

    with context("with a Python file that starts with a byte-order mark"):
        with before.all:
            self.fixture = practice_from_files(
                {"shop/.context/module-context.md": "# Shop\n", "shop/bom.py": "﻿class BomOnly:\n    pass\n"}
            )

        with it("should read the byte-order mark as the file's start, and the class the file declares"):
            expect([node.name for node in self.fixture.practice.reading.in_graph.nodes("OoadClass")]).to(equal(["BomOnly"]))

    with context("with a Stories story-map board among the edited files"):
        with before.all:
            board = WhiteboardStoryModel(round_trip_story_map()).save()
            self.fixture = practice_from_files(
                {
                    ".context/story-map.whiteboard": board,
                    "shop/.context/module-context.md": "# Shop\n",
                    "shop/story-map.whiteboard": board,
                    "shop/cart.py": _CART,
                }
            )
            self.fixture.read_only([".context/story-map.whiteboard", "shop/story-map.whiteboard", "shop/cart.py"])
            self.in_graph = self.fixture.practice.reading.in_graph
            self.shop = next(node for node in self.in_graph.nodes("Module") if node.name == "shop")

        with it("should read the code, and no class from the board"):
            expect([node.name for node in self.in_graph.nodes("OoadClass")]).to(equal(["Cart"]))

        with it("should not keep the board as a source that does not parse"):
            expect(self.shop.get_fact("unreadable_sources") or []).to(equal([]))

    with context("with a Clean Engineering modules board beside the code"):
        with before.all:
            board = _modules_board()
            self.fixture = practice_from_files(
                {
                    ".context/modules.whiteboard": board,
                    "shop/.context/module-context.md": "# Shop\n",
                    "shop/modules.whiteboard": board,
                    "shop/cart.py": _CART,
                }
            )
            self.fixture.read_only([".context/modules.whiteboard", "shop/cart.py"])
            self.in_graph = self.fixture.practice.reading.in_graph
            self.shop = next(node for node in self.in_graph.nodes("Module") if node.name == "shop")

        with it("should read the code, and no class from the board, as the board draws the design and is not source"):
            expect([node.name for node in self.in_graph.nodes("OoadClass")]).to(equal(["Cart"]))

        with it("should not keep the board as a source that does not parse"):
            expect(self.shop.get_fact("unreadable_sources") or []).to(equal([]))

    with context("with a whiteboard file that is not a saved board"):
        with before.all:
            self.fixture = practice_from_files(
                {
                    "shop/.context/module-context.md": "# Shop\n",
                    "shop/cart.py": _CART,
                    "shop/broken.whiteboard": "{not a board",
                }
            )
            self.shop = next(node for node in self.fixture.practice.reading.in_graph.nodes("Module") if node.name == "shop")

        with it("should keep the file on its module as a source that does not parse"):
            expect([kept.split(":")[0] for kept in self.shop.get_fact("unreadable_sources") or []]).to(equal(["shop/broken.whiteboard"]))

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
            expect([each.node for each in ProductionClasses(self.fixture.practice.reading).named("Till")]).to(equal(self.index.classes_named("Till")))

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

        # `private board: Board` in the constructor is a field the client holds, so each operation also reads it.
        with it("should record that an operation invokes the member of its name it calls on another object"):
            expect(_targets(self.fixture, "invokes", "select")).to(equal(["board", "select"]))

        with it("should record that an operation invokes the property it reads"):
            expect(_targets(self.fixture, "invokes", "opensLeft")).to(equal(["board", "shown"]))

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

    with context("with members declared with no body"):
        with before.all:
            self.fixture = practice_from_files(
                {
                    "ts/shape.ts": "export abstract class Shape {\n  abstract area(width: number): number;\n}\n",
                    "ts/drawable.ts": "export interface Drawable {\n  draw(scale: number): void;\n}\n",
                }
            )

        def _exempt(self, name: str) -> list:
            member = next(node for node in self.fixture.practice.reading.in_graph.nodes("Operation") if node.name == name)
            return member.get_fact("exempt_relationships") or []

        with it("should not hold a TypeScript abstract member to invokes"):
            expect(self._exempt("area")).to(equal(["invokes"]))

        with it("should read no TypeScript interface's method, so none is held to invokes"):
            names = [node.name for node in self.fixture.practice.reading.in_graph.nodes("Operation")]
            expect(names).not_to(contain("draw"))

    with context("with a spec beside the code"):
        with before.all:
            self.fixture = practice_from_files(
                {
                    "shop/cart.py": _CART,
                    "shop/cart_spec.py": "class CartSpec:\n    def check(self, cart) -> None:\n        assert cart\n",
                }
            )

        with it("should hold none of the spec's members to the relationships the schema requires"):
            in_graph = self.fixture.practice.reading.in_graph
            check = next(node for node in in_graph.nodes("Operation") if node.name == "check")
            required = {requirement.field for requirement in in_graph.rule_run.schema.requirements if "Operation" in requirement.owner.node_types}
            expect(required - set(check.get_fact("exempt_relationships") or [])).to(equal(set()))

    with context("with a folder holding only story tests"):
        with before.all:
            self.fixture = practice_from_files(
                {
                    "shop/cart.py": _CART,
                    "shop/pay/pay_story.test.py": "with story('Pay'):\n    pass\n",
                }
            )

        with it("should not hold the folder's package to the participants a package of production code needs"):
            package = next(node for node in self.fixture.practice.reading.in_graph.nodes("Package") if node.name == "pay")
            expect(package.get_fact("exempt_relationships")).to(equal(["participants"]))


with description("Clean Engineering reading the classes its model documents describe"):
    with context("with a folder whose only file is a class model describing a class"):
        with before.all:
            self.fixture = practice_from_files({"shop/.context/module-context.md": "# Shop\n", "shop/.context/shop-model.md": _SHOP_MODEL})
            self.ledger = next(iter(_classes(self.fixture)), None)
            self.graph = self.fixture.practice.reading.graph

        with it("should hold the class the document describes"):
            expect([node.name for node in _classes(self.fixture)]).to(equal(["Ledger"]))

        with it("should hold the operation the document gives the class"):
            expect(_targets(self.fixture, "owns", "Ledger")).to(equal(["record"]))

        with it("should keep the stereotypes the document gives the class"):
            expect(self.ledger and self.ledger.get_fact("stereotypes")).to(equal(["Entity"]))

        with it("should place the class at the document's line that names it"):
            expect(self.ledger and (self.ledger.source.file, self.ledger.source.start_line)).to(equal(("shop/.context/shop-model.md", 3)))

        with it("should place the operation at the document's line that declares it"):
            lines = [node.source.start_line for node in self.fixture.practice.reading.in_graph.nodes("Operation") if node.name == "record"]
            expect(lines).to(equal([8]))

        with it("should have the class owned by the folder the document describes"):
            expect(self.ledger and self.graph.edges.direct_parent(self.ledger).name).to(equal("shop"))

        with it("should mark the class as one a model document describes, not one code declares"):
            expect(self.ledger and self.ledger.get_fact(DESCRIBED_FACT)).to(be_true)

    with context("with code that declares the class the model document describes"):
        with before.all:
            self.fixture = practice_from_files(
                {
                    "shop/.context/shop-model.md": _SHOP_MODEL,
                    "shop/ledger.py": "class Ledger:\n    def record(self, entry: str) -> str:\n        return entry\n",
                }
            )

        with it("should hold a node for the class the document describes and a node for the class the code declares"):
            expect([(node.name, node.source.file) for node in _classes(self.fixture)]).to(
                equal([("Ledger", "shop/.context/shop-model.md"), ("Ledger", "shop/ledger.py")])
            )

        with it("should join the code's class to the document's class it implements"):
            expect([(edge.parent.source.file, edge.child.source.file) for edge in self.fixture.practice.reading.in_graph.edge_index.of("implements")]).to(
                equal([("shop/ledger.py", "shop/.context/shop-model.md")])
            )

        with it("should answer the code's class first for the class's name"):
            expect(self.fixture.practice.reading.code_index.classes_named("Ledger")[0].source.file).to(equal("shop/ledger.py"))

    with context("with a folder whose only file is a DDD domain model"):
        with before.all:
            self.fixture = practice_from_files({"shop/.context/domain-model.md": _SHOP_DOMAIN_MODEL})

        with it("should leave the domain model to DDD and read no class from it"):
            expect([node.name for node in _classes(self.fixture)]).to(equal([]))


def _exempt(fixture, name: str) -> list[str]:
    """The relationships the member called name is not held to."""
    member = next(node for node in fixture.practice.reading.in_graph.nodes("Operation") if node.name == name)
    return member.get_fact("exempt_relationships") or []


with description("Clean Engineering marking members that call nothing by design"):
    with before.all:
        self.fixture = practice_from_files(
            {
                "app/kinds.py": (
                    "from abc import ABC, abstractmethod\n\n\n"
                    "class Kind(ABC):\n"
                    "    @abstractmethod\n"
                    "    def move_next(self, steps: int) -> None:\n"
                    '        """Move on."""\n\n'
                    "    def limit(self) -> int:\n"
                    "        return 3\n\n"
                    "    def keep(self, value: int) -> None:\n"
                    "        self.value = value\n"
                ),
            }
        )

    with it("should not hold an abstract member to invoking anything"):
        expect(_exempt(self.fixture, "move_next")).to(equal(["invokes"]))

    with it("should not hold a member that takes nothing and answers a value to invoking anything"):
        expect(_exempt(self.fixture, "limit")).to(equal(["invokes"]))

    with it("should still hold a member that takes a value and calls nothing to invoking something"):
        expect(_exempt(self.fixture, "keep")).to(equal([]))


# The shape of the Files app's own example project: Ticket.delete takes a board its annotation names, and ticket.py
# imports no Board, which sits in board.py of the same package.
_KANBAN = {
    "space/kanban/ticket.py": (
        "class Ticket:\n"
        "    def delete(self, board: Board) -> None:\n"
        "        board.reread()\n\n"
        "    def close(self, lane) -> None:\n"
        "        lane.reread()\n\n"
        "    def move(self, lane) -> None:\n"
        "        lane.clear()\n"
    ),
    "space/kanban/board.py": "class Board:\n    def reread(self) -> None:\n        return None\n\n    def clear(self) -> None:\n        return None\n",
    "space/kanban/lane.py": "class Lane:\n    def clear(self) -> None:\n        return None\n",
    "space/archive/board.py": "class Board:\n    def reread(self) -> None:\n        return None\n",
}


def _invoked_by(fixture, operation: str) -> list[str]:
    """What the operation called operation invokes, each as its file and its class's member."""
    graph = fixture.practice.reading.graph
    caller = next(node for node in fixture.practice.reading.in_graph.nodes("Operation") if node.name == operation and node.source.file == "space/kanban/ticket.py")
    return [f"{edge.child.source.file}:{edge.child.get_fact('owner')}.{edge.child.name}" for edge in graph.edges.from_parent("invokes", caller)]


with description("Clean Engineering linking a call on a receiver whose class its file does not import"):
    with before.all:
        self.fixture = practice_from_files(_KANBAN)

    with context("with a parameter whose annotation names a class of the file's own package"):
        with it("should invoke the operation of that package's class, not a class of the same name in another package"):
            expect(_invoked_by(self.fixture, "delete")).to(equal(["space/kanban/board.py:Board.reread"]))

    with context("with a parameter that has no annotation, and one class of the file's package that declares the operation"):
        with it("should invoke that class's operation"):
            expect(_invoked_by(self.fixture, "close")).to(equal(["space/kanban/board.py:Board.reread"]))

    with context("with a parameter that has no annotation, and two classes of the file's package that declare the operation"):
        with it("should invoke neither"):
            expect(_invoked_by(self.fixture, "move")).to(equal([]))
