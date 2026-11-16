"""Mamba spec: a Clean Engineering model drawn on a Claude Whiteboard as its drawio is drawn, and read back as the same
model."""

from expects import be_above, be_true, contain, equal, expect, raise_error
from mamba import before, context, description, it

from harness.whiteboard import Arrow, Label, Section, Shape, Whiteboard
from cdd_guidance.practices.clean_engineering.model.base_class_model import CleanEngineeringModel, Module, OoadClass, UnreadableSource
from cdd_guidance.practices.clean_engineering.model.diagram.class_view import CLASSES_ON_ONE_PAGE
from cdd_guidance.practices.clean_engineering.model.operation import Operation
from cdd_guidance.practices.clean_engineering.model.property import Property
from cdd_guidance.practices.clean_engineering.model.whiteboard.whiteboard_class_model import WhiteboardCleanEngineeringModel


def _class_with(name: str, sequential_order: int, properties: list) -> OoadClass:
    """A class holding the properties given."""
    made = OoadClass(name, sequential_order)
    made.properties = properties
    return made


def _module_card(name: str, sequential_order: int, description: str, seam_terms: list, dependencies: list) -> Module:
    """A module whose card says its purpose, its seam terms, and the modules it depends on."""
    made = Module(name, sequential_order)
    made.description = description
    made.seam_terms = seam_terms
    made.dependencies = dependencies
    return made


def orders_class_model() -> CleanEngineeringModel:
    model = CleanEngineeringModel("orders")
    module = Module("orders", 1)
    cart = _class_with("Cart", 1, [Property(name="lines", type_hint="List[Line]")])
    cart.operations = [Operation.from_signature("checkout(payment: Payment): Order")]
    cart.stereotypes = ["Aggregate Root"]
    line = _class_with("Line", 2, [Property(name="quantity", type_hint="int")])
    priced = _class_with("PricedLine", 3, [Property(name="price", type_hint="Money")])
    priced.bases = ["Line"]
    module.classes.extend([cart, line, priced])
    model.modules.append(module)
    for prop in cart.properties:
        prop.take_drawn_kind("composition")
    return model


def two_module_model(classes_each: int) -> CleanEngineeringModel:
    """Two modules of classes_each classes, the first module's first class holding the second module's first."""
    model = CleanEngineeringModel("big")
    for module_number, name in enumerate(("billing", "catalog"), start=1):
        module = Module(name, module_number)
        module.classes.extend(
            _class_with(f"{name.title()}{index}", index, [Property(name="id", type_hint="str")])
            for index in range(1, classes_each + 1)
        )
        model.modules.append(module)
    product = Property(name="product", type_hint="Catalog1")
    model.modules[0].classes[0].properties.append(product)
    product.take_drawn_kind("association")
    return model


def shop_modules_view() -> CleanEngineeringModel:
    model = CleanEngineeringModel("shop")
    model.modules.append(_module_card("orders", 1, "Take and pay orders.", ["Cart", "Order"], ["catalog"]))
    model.modules.append(_module_card("orders/returns", 2, "Take goods back.", ["Return"], ["orders"]))
    model.modules.append(_module_card("catalog", 3, "Keep what is for sale.", ["Product"], []))
    return model


def summary(model: CleanEngineeringModel) -> list:
    return [
        (module.name, [
            (oclass.name, list(oclass.stereotypes), [(item.name, item.type_hint) for item in oclass.properties],
             [item.name for item in oclass.operations], list(oclass.bases))
            for oclass in module.classes
        ])
        for module in model.modules
    ]


def cards_of(board: Whiteboard, role: str = "class") -> dict:
    return {element.text.split("**")[1]: element for element in board.elements if isinstance(element, Shape) and element.role == role}


with description("a class model drawn on a Claude whiteboard") as self:
    with before.each:
        self.source = orders_class_model()
        self.text = WhiteboardCleanEngineeringModel().render(self.source)
        self.board = Whiteboard.from_text(self.text)
        self.cards = cards_of(self.board)

    with it("should draw each class with its module, stereotypes, properties and operations"):
        expect(self.cards["Cart"].text.splitlines()).to(equal([
            "`orders`", "*«Aggregate Root»*", "**Cart**", "---", "+ lines: List[Line]", "---", "+ checkout(payment: Payment): Order",
        ]))

    with it("should place a base above the classes that derive from it, as the drawio class view does"):
        expect(self.cards["PricedLine"].box.y).to(be_above(self.cards["Line"].box.y))

    with it("should draw each relationship as an arrow named by its kind"):
        arrows = {(element.role, element.from_id, element.to_id) for element in self.board.elements if isinstance(element, Arrow)}
        expect(arrows).to(contain(("inheritance", self.cards["PricedLine"].id, self.cards["Line"].id)))

    with it("should give each arrow the sides it leaves and reaches its cards by"):
        sides = [(element.from_side, element.to_side) for element in self.board.elements if isinstance(element, Arrow)]
        expect(all(start and end for start, end in sides)).to(be_true)

    with it("should read back every module, class, property, operation and base"):
        expect(summary(WhiteboardCleanEngineeringModel().parse(self.text))).to(equal(summary(self.source)))

    with context("that is too big for one page"):
        with before.each:
            self.source = two_module_model(CLASSES_ON_ONE_PAGE // 2 + 1)
            self.text = WhiteboardCleanEngineeringModel().render(self.source)
            self.board = Whiteboard.from_text(self.text)

        with it("should draw each module's page as a section of its own, side by side"):
            pages = [element for element in self.board.elements if isinstance(element, Section)]
            expect([(page.text, page.box.x < pages[-1].box.x) for page in pages]).to(equal([("billing", True), ("catalog", False)]))

        with it("should show the class of another module a page reaches on a card of its own"):
            expect(list(cards_of(self.board, "imported"))).to(equal(["Catalog1"]))

        with it("should read back each module with only its own classes"):
            expect(summary(WhiteboardCleanEngineeringModel().parse(self.text))).to(equal(summary(self.source)))


with description("a modules view drawn on a Claude whiteboard") as self:
    with before.each:
        self.source = shop_modules_view()
        self.text = WhiteboardCleanEngineeringModel().render(self.source)
        self.board = Whiteboard.from_text(self.text)
        self.boxes = {element.text.split("**")[1]: element for element in self.board.elements if isinstance(element, Shape)}
        self.sections = {element.text: element for element in self.board.elements if isinstance(element, Section)}

    with it("should draw each module with its purpose and seam terms"):
        expect(self.boxes["catalog"].text.splitlines()).to(equal(["**catalog**", "*Keep what is for sale.*", "- Product"]))

    with it("should draw a module that holds others as a section around them"):
        expect(self.sections["orders"].holds(self.boxes["orders/returns"])).to(be_true)

    with it("should write the purpose and seam terms of a section under its title"):
        about = next(element for element in self.board.elements if isinstance(element, Label) and element.role == "about")
        expect(about.text.splitlines()).to(equal(["*Take and pay orders.*", "- Cart", "- Order"]))

    with it("should stand a module left of the modules that depend on it, as the drawio modules view does"):
        expect(self.boxes["catalog"].box.x < self.sections["orders"].box.x).to(be_true)

    with it("should draw each dependency but the one on the module it sits in as an arrow"):
        arrows = [(element.from_id, element.to_id) for element in self.board.elements if isinstance(element, Arrow)]
        expect(arrows).to(equal([(self.sections["orders"].id, self.boxes["catalog"].id)]))

    with it("should read back every module with its purpose, seam terms and dependencies"):
        read = WhiteboardCleanEngineeringModel().parse(self.text)
        expect([(module.name, module.description, module.seam_terms, module.dependencies) for module in read.modules]).to(equal([
            ("orders", "Take and pay orders.", ["Cart", "Order"], ["catalog"]),
            ("orders/returns", "Take goods back.", ["Return"], ["orders"]),
            ("catalog", "Keep what is for sale.", ["Product"], []),
        ]))

    with context("that is read from a board with no modules or classes"):
        with it("should refuse the board as an unreadable source"):
            expect(lambda: WhiteboardCleanEngineeringModel().parse(Whiteboard("Empty").save())).to(raise_error(UnreadableSource, "The board holds no module and no class"))
