"""How Clean Engineering reads code into its graph: each class's properties and operations, and the edges that say which
class a property's value is and which parameters an operation takes."""

from expects import be_true, contain, equal, expect, have_key
from mamba import before, context, description, it

from cdd_guidance.practices.clean_engineering.model.python.python_class_model import PythonCleanEngineeringModel
from cdd_guidance.practices.clean_engineering.reading.production_classes import ProductionClasses
from cdd_guidance.practices.clean_engineering.rules.rule_examples import practice_from_files
from cdd_guidance.practices.stories.model.fixtures.round_trip_story_map import round_trip_story_map
from cdd_guidance.practices.stories.model.whiteboard.nodes import WhiteboardStoryMap
from cdd_guidance.practices.clean_engineering.model.whiteboard.whiteboard_class_model import WhiteboardCleanEngineeringModel
from cdd_guidance.practices.clean_engineering.model.base_class_model import CleanEngineeringModel, Module
from cdd_guidance.practices.clean_engineering.measures.read_facts import DESCRIBED_FACT

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
            board = WhiteboardStoryMap().copy_of(round_trip_story_map()).save()
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

    # Hardening regression run (graph_incremental_heavy_spec): a refresh kept a folder's node as the build before left
    # it, so a file added or deleted was not counted among its public files and a deleted file's imports stayed on it.
    with context("with a file of its folder deleted and refreshed"):
        with before.all:
            self.fixture = practice_from_files({"shop/cart.py": _CART, "shop/till.py": "from pathlib import Path\n\n\nclass Till:\n    pass\n"})
            (self.fixture.root / "shop/till.py").unlink()
            self.fixture.practice.reading.graph.refresh([str(self.fixture.root / "shop/till.py")])
            self.shop = next(node for node in self.fixture.practice.reading.in_graph.nodes("Package") if node.name == "shop")

        with it("should count only the public files still in the folder"):
            expect(self.shop.get_fact("public_source_files")).to(equal(1))

        with it("should keep no import of the file deleted"):
            expect(sorted(self.shop.get_fact("imported_classes_by_file") or {})).to(equal(["shop/cart.py"]))

    # Hardening regression run (graph_incremental_heavy_spec): a refresh after a deleted file kept it among the files of
    # its folder that another file imports, which a fresh build, reading only files still there, never lists.
    with context("with a file another file of its folder imports deleted and refreshed"):
        with before.all:
            self.fixture = practice_from_files({"shop/till.py": "class Till:\n    pass\n", "shop/counter.py": "from shop.till import Till\n\n\nclass Counter:\n    pass\n"})
            (self.fixture.root / "shop/till.py").unlink()
            self.fixture.practice.reading.graph.refresh([str(self.fixture.root / "shop/till.py")])
            self.shop = next(node for node in self.fixture.practice.reading.in_graph.nodes("Package") if node.name == "shop")

        with it("should list no sibling the file still there imported from the file deleted"):
            expect(self.shop.get_fact("sibling_imports")).to(equal({"counter.py": []}))

    # Hardening regression run (graph_build_heavy_spec): OoadClass's property named properties took the place of the
    # group its class's properties sit under, so it was its own parent and a save walking up from it never ended.
    with context("with a class whose property is named as the group its properties sit under"):
        with before.all:
            ledger = "from shop.entry import Entry\n\n\nclass Ledger:\n    def __init__(self) -> None:\n        self.properties: list[Entry] = []\n        self.total: int = 0\n\n    def add(self, entry: Entry) -> None:\n        self.properties.append(entry)\n        self.total += 1\n"
            self.fixture = practice_from_files({"shop/entry.py": "class Entry:\n    pass\n", "shop/ledger.py": ledger})
            self.members = [node for node in self.fixture.practice.reading.in_graph.nodes("Property") if node.name in ("properties", "total")]

        with it("should hang no property under a property, itself included"):
            expect([(member.name, member.parent is not None and member.parent.type == "Property") for member in sorted(self.members, key=lambda member: member.name)]).to(equal([("properties", False), ("total", False)]))

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
                    "shop/.context/shop-model.md": _SHOP_MODEL + "+ close(): None\n",
                    "shop/ledger.py": "class Ledger:\n    def record(self, entry: str) -> str:\n        return entry\n",
                }
            )
            self.ledger = next(iter(_classes(self.fixture)), None)

        with it("should hold one node for the class, read from the code"):
            expect([(node.name, node.source.file) for node in _classes(self.fixture)]).to(equal([("Ledger", "shop/ledger.py")]))

        with it("should keep the document's place on the class, beside the code's"):
            places = {name: (place.file, place.line) for name, place in self.ledger.places.items()} if self.ledger else {}
            expect(places).to(equal({"python": ("shop/ledger.py", 1), "markdown": ("shop/.context/shop-model.md", 3)}))

        with it("should keep the code's measures and the document's stereotypes on the one class"):
            expect(self.ledger and (self.ledger.has_fact("method_count"), self.ledger.get_fact("stereotypes"))).to(equal((True, ["Entity"])))

        with it("should keep the document's place on an operation the code declares too"):
            record = next(node for node in self.fixture.practice.reading.in_graph.nodes("Operation") if node.name == "record")
            expect(sorted(record.places)).to(equal(["markdown", "python"]))

        with it("should hold an operation only the document declares under the code's class, at the document's line"):
            expect(sorted((node.name, node.source.file) for node in _members_of(self.fixture, self.ledger))).to(
                equal([("balance", "shop/.context/shop-model.md"), ("close", "shop/.context/shop-model.md"), ("record", "shop/ledger.py")])
            )

        with it("should read an operation only the document declares at the model fidelity"):
            close = next(node for node in self.fixture.practice.reading.in_graph.nodes("Operation") if node.name == "close")
            expect(close.fidelity_read_at).to(equal("model"))

        with it("should join no format to another with an edge"):
            expect(list(self.fixture.practice.reading.in_graph.edge_index.of("implements"))).to(equal([]))

        with it("should take the class as a production class the compared facts measure, once"):
            expect([each.file for each in ProductionClasses(self.fixture.practice.reading)]).to(equal(["shop/ledger.py"]))

    # Hardening regression run (graph_incremental_heavy_spec): a refresh of another file of the folder read the document
    # again and gave each member only the document writes its own file as a second place, which a fresh build never does.
    with context("with code that declares the class the model document describes, refreshed with another file of its folder"):
        with before.all:
            self.fixture = practice_from_files(
                {
                    "shop/.context/shop-model.md": _SHOP_MODEL + "+ close(): None\n",
                    "shop/ledger.py": "class Ledger:\n    def record(self, entry: str) -> str:\n        return entry\n",
                    "shop/till.py": "class Till:\n    pass\n",
                }
            )
            self.fixture.practice.reading.graph.refresh([str(self.fixture.root / "shop/till.py")])

        with it("should keep no second place on an operation only the document declares"):
            close = next(node for node in self.fixture.practice.reading.in_graph.nodes("Operation") if node.name == "close")
            expect(close.has_fact("written_in")).to(equal(False))

    # Hardening regression run (graph_incremental_heavy_spec): a document that no longer describes a class left the
    # class its code declares holding the document's place and stereotypes until a full load.
    with context("with code that declares the class the model document describes, whose document is changed to describe another class"):
        with before.all:
            self.fixture = practice_from_files(
                {
                    "shop/.context/shop-model.md": _SHOP_MODEL,
                    "shop/ledger.py": "class Ledger:\n    def record(self, entry: str) -> str:\n        return entry\n",
                }
            )
            document = self.fixture.root / "shop/.context/shop-model.md"
            document.write_text(_SHOP_MODEL.replace("## Ledger", "## Journal"), encoding="utf-8")
            self.fixture.practice.reading.graph.refresh([str(document)])
            self.ledger = next(node for node in _classes(self.fixture) if node.name == "Ledger")

        with it("should keep only the code's place on the class the code declares"):
            expect(sorted(self.ledger.places)).to(equal(["python"]))

        with it("should keep none of the document's stereotypes on it"):
            expect(self.ledger.get_fact("stereotypes") or []).to(equal([]))

    with context("with code that declares the class in two files of the module the document describes"):
        with before.all:
            self.fixture = practice_from_files(
                {
                    "shop/.context/shop-model.md": _SHOP_MODEL,
                    "shop/ledger.py": "class Ledger:\n    def record(self, entry: str) -> str:\n        return entry\n",
                    "shop/old/ledger.py": "class Ledger:\n    def record(self, entry: str) -> str:\n        return entry\n",
                }
            )

        with it("should keep the document's class a node of its own, since the document names no file to tell them by"):
            expect(sorted(node.source.file for node in _classes(self.fixture))).to(
                equal(["shop/.context/shop-model.md", "shop/ledger.py", "shop/old/ledger.py"])
            )

    with context("with only a spec's support in the module declaring the class the document describes"):
        with before.all:
            self.fixture = practice_from_files(
                {
                    "shop/.context/shop-model.md": _SHOP_MODEL,
                    "shop/ledger_fixture.py": "class Ledger:\n    def record(self, entry: str) -> str:\n        return entry\n",
                }
            )

        with it("should hold the class once, read from the code that declares it"):
            expect([node.source.file for node in _classes(self.fixture)]).to(equal(["shop/ledger_fixture.py"]))

    with context("with a document of another module describing the class the code declares"):
        with before.all:
            self.fixture = practice_from_files(
                {
                    "till/.context/till-model.md": _SHOP_MODEL.replace("# shop", "# till"),
                    "shop/ledger.py": "class Ledger:\n    def record(self, entry: str) -> str:\n        return entry\n",
                }
            )

        with it("should keep the two classes apart, since the module decides which class a document means"):
            expect(sorted(node.source.file for node in _classes(self.fixture))).to(equal(["shop/ledger.py", "till/.context/till-model.md"]))

    with context("with a folder whose only file is a DDD domain model"):
        with before.all:
            self.fixture = practice_from_files({"shop/.context/domain-model.md": _SHOP_DOMAIN_MODEL})

        with it("should leave the domain model to DDD and read no class from it"):
            expect([node.name for node in _classes(self.fixture)]).to(equal([]))


def _members_of(fixture, cls) -> list:
    """The operations and properties cls holds, as its edges in the graph say."""
    edges = fixture.practice.reading.graph.edges
    return [edge.child for kind in ("owns", "properties") for edge in edges.from_parent(kind, cls)]


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


with description("Clean Engineering naming the class a member belongs to"):
    with before.all:
        self.fixture = practice_from_files({"shop/cart.py": _CART + "\n\ndef total(lines: list) -> int:\n    return 0\n"})
        self.reading = self.fixture.practice.reading
        self.nodes = {node.name: node for node in self.reading.in_graph.nodes() if node.type == "Operation"}

    with it("should name the class an operation belongs to"):
        expect(self.reading.owner_of(self.nodes["__init__"])).to(equal("Cart"))

    with it("should name none for a module's function"):
        expect(self.reading.owner_of(self.nodes["total"])).to(equal(""))
