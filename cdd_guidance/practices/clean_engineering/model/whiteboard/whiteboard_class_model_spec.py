"""Mamba spec: a Clean Engineering model drawn on a Claude Whiteboard reads back as the same model, as its drawio does."""

from expects import contain, equal, expect, raise_error
from mamba import before, context, description, it

from harness.whiteboard import Arrow, Section, Shape, UnreadableBoard, Whiteboard
from cdd_guidance.practices.clean_engineering.model.base_class_model import CleanEngineeringModel, Module, OoadClass
from cdd_guidance.practices.clean_engineering.model.operation import Operation
from cdd_guidance.practices.clean_engineering.model.property import Property
from cdd_guidance.practices.clean_engineering.model.whiteboard.whiteboard_class_model import WhiteboardCleanEngineeringModel


def orders_class_model() -> CleanEngineeringModel:
    model = CleanEngineeringModel("orders")
    module = Module("orders", 1)
    cart = OoadClass("Cart", 1, properties=[Property(name="lines", type_hint="List[Line]")],
                     operations=[Operation.from_signature("checkout(payment: Payment): Order")])
    cart.stereotypes = ["Aggregate Root"]
    line = OoadClass("Line", 2, properties=[Property(name="quantity", type_hint="int")])
    priced = OoadClass("PricedLine", 3, properties=[Property(name="price", type_hint="Money")])
    priced.bases = ["Line"]
    module.classes.extend([cart, line, priced])
    model.modules.append(module)
    for prop in cart.properties:
        prop.take_drawn_kind("composition")
    return model


def shop_modules_view() -> CleanEngineeringModel:
    model = CleanEngineeringModel("shop")
    model.modules.append(Module("orders", 1, description="Take and pay orders.", seam_terms=["Cart", "Order"], dependencies=["catalog"]))
    model.modules.append(Module("catalog", 2, description="Keep what is for sale.", seam_terms=["Product"]))
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


with description("a class model drawn on a Claude whiteboard") as self:
    with before.each:
        self.source = orders_class_model()
        self.text = WhiteboardCleanEngineeringModel().render(self.source)
        self.board = Whiteboard.load(self.text)
        self.cards = {element.text.split("**")[1]: element for element in self.board.elements
                      if isinstance(element, Shape) and element.id.startswith("class.")}

    with it("should draw each module as a section holding its classes"):
        section = next(element for element in self.board.elements if isinstance(element, Section))
        inside = all(section.x <= card.x and card.x + card.w <= section.x + section.w
                     and section.y <= card.y and card.y + card.h <= section.y + section.h for card in self.cards.values())
        expect((section.text, inside)).to(equal(("orders", True)))

    with it("should draw each class with its stereotypes, properties and operations"):
        expect(self.cards["Cart"].text.splitlines()).to(equal([
            "*«Aggregate Root»*", "**Cart**", "---", "+ lines: List[Line]", "---", "+ checkout(payment: Payment): Order",
        ]))

    with it("should draw each class's base as an arrow to the base"):
        arrows = [(element.from_id, element.to_id, element.label) for element in self.board.elements if isinstance(element, Arrow)]
        expect(arrows).to(contain((self.cards["PricedLine"].id, self.cards["Line"].id, "extends")))

    with it("should read back every module, class, property, operation and base"):
        expect(summary(WhiteboardCleanEngineeringModel().parse(self.text))).to(equal(summary(self.source)))


with description("a modules view drawn on a Claude whiteboard") as self:
    with before.each:
        self.source = shop_modules_view()
        self.text = WhiteboardCleanEngineeringModel().render(self.source)
        self.board = Whiteboard.load(self.text)
        self.boxes = {element.text.split("**")[1]: element for element in self.board.elements if isinstance(element, Shape)}

    with it("should draw each module with its purpose and seam terms"):
        expect(self.boxes["orders"].text.splitlines()).to(equal(["**orders**", "*Take and pay orders.*", "- Cart", "- Order"]))

    with it("should draw each dependency as an arrow to the module it depends on"):
        arrows = [(element.from_id, element.to_id) for element in self.board.elements if isinstance(element, Arrow)]
        expect(arrows).to(equal([(self.boxes["orders"].id, self.boxes["catalog"].id)]))

    with it("should read back every module with its purpose, seam terms and dependencies"):
        read = WhiteboardCleanEngineeringModel().parse(self.text)
        expect([(module.name, module.description, module.seam_terms, module.dependencies) for module in read.modules]).to(equal([
            ("orders", "Take and pay orders.", ["Cart", "Order"], ["catalog"]),
            ("catalog", "Keep what is for sale.", ["Product"], []),
        ]))

    with context("that is read from a board with no modules or classes"):
        with it("should refuse the board as an unreadable source"):
            expect(lambda: WhiteboardCleanEngineeringModel().parse(Whiteboard("Empty").save())).to(raise_error(UnreadableBoard))
