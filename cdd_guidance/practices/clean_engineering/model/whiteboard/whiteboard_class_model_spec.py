"""Mamba spec: a Clean Engineering model drawn on a Claude Whiteboard as its drawio is drawn, and read back as the same
model."""

from pathlib import Path
from expects import be_above, be_true, contain, equal, expect, raise_error
from mamba import before, context, description, it

from harness.whiteboard.whiteboard import Arrow, Label, Section, Shape, UnreadableBoard, Whiteboard
from cdd_guidance.practices.clean_engineering.model.base_class_model import CleanEngineeringModel, Module, OoadClass, UnreadableSource
from cdd_guidance.practices.clean_engineering.model.diagram.class_layout import DiagramArrow
from cdd_guidance.practices.clean_engineering.model.diagram.class_view import CLASSES_ON_ONE_PAGE
from cdd_guidance.practices.clean_engineering.model.diagram.diagram_node import DiagramClass
from harness.whiteboard import Box
from cdd_guidance.practices.clean_engineering.model.field_types import Relationship
from cdd_guidance.practices.clean_engineering.model.operation import Operation
from cdd_guidance.practices.clean_engineering.model.property import Property
from cdd_guidance.practices.clean_engineering.model.whiteboard.whiteboard_class_model import BoardArrowRouter, WhiteboardCleanEngineeringModel


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
        prop.arrow.take_kind("composition")
    return model


def credentials_class_model() -> CleanEngineeringModel:
    """Credentials holding a token, a validation and a password reset, each its own card below it, and the password
    reset holding the temporary password it sent, on a card of its own below that; the cards are as wide as their
    words, so none is as wide as the card above it."""
    model = CleanEngineeringModel("customer")
    module = Module("credentials", 1)
    held = {
        "Credentials": [("token", "Token"), ("validation", "Validation"), ("passwordReset", "PasswordReset")],
        "PasswordReset": [("sent", "TemporaryPassword"), ("requestedAtTheMomentTheCustomerAsked", "Instant")],
    }
    for order, name in enumerate(("Credentials", "Token", "Validation", "PasswordReset", "TemporaryPassword"), start=1):
        oclass = _class_with(name, order, [Property(name=field, type_hint=kind) for field, kind in held.get(name, [("value", "str")])])
        module.classes.append(oclass)
        for prop in oclass.properties:
            if prop.type_hint != "Instant":
                prop.arrow.take_kind("composition")
    model.modules.append(module)
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
    product.arrow.take_kind("association")
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

    with it("should draw each class with its module, stereotypes, properties and operations, a few dashes between them"):
        expect(self.cards["Cart"].text.splitlines()).to(equal([
            "`orders`", "*«Aggregate Root»*", "**Cart**", "+ lines: List[Line]", "– – –", "+ checkout(payment: Payment): Order",
        ]))

    with context("with a class folded into another's card"):
        with before.each:
            self.source = orders_class_model()
            cart = self.source.modules[0].classes[0]
            repository = _class_with("CartRepository", 4, [Property(name="carts", type_hint="List[Cart]")])
            repository.operations = [Operation.from_signature("load(id: str): Cart")]
            repository.stereotypes = ["Repository"]
            cart.fold(repository)
            self.text = WhiteboardCleanEngineeringModel().render(self.source)

        with it("should leave a blank line between the classes on the card"):
            expect(cards_of(Whiteboard.from_text(self.text))["Cart"].text.splitlines()).to(equal([
                "`orders`", "*«Aggregate Root»*", "**Cart**", "+ lines: List[Line]", "– – –", "+ checkout(payment: Payment): Order",
                "", "*«Repository»*", "**CartRepository**", "+ carts: List[Cart]", "– – –", "+ load(id: str): Cart",
            ]))

        with it("should read back each class on the card with its own properties and operations"):
            cart = WhiteboardCleanEngineeringModel().parse(self.text).modules[0].classes[0]
            expect([(item.name, [prop.name for prop in item.properties], [op.name for op in item.operations]) for item in [cart, *cart.folded]]).to(equal([
                ("Cart", ["lines"], ["checkout"]), ("CartRepository", ["carts"], ["load"]),
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

    with context("where a class depends on the class that holds it"):
        with before.each:
            line = self.source.modules[0].classes[1]
            line.dependencies.append(Relationship(target="Cart", kind="dependency", label="totals"))
            self.board = Whiteboard.from_text(WhiteboardCleanEngineeringModel().render(self.source))
            self.cards = cards_of(self.board)

        # A solid line already joins the two cards; a dotted one beside it says nothing more and tangles the page.
        with it("should draw only the solid relationship between the two classes"):
            pair = {self.cards["Cart"].id, self.cards["Line"].id}
            joining = [element.role for element in self.board.elements if isinstance(element, Arrow) and {element.from_id, element.to_id} == pair]
            expect(joining).to(equal(["composition"]))

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


def level_leg(cards: dict, arrow: Arrow) -> tuple:
    """The level leg of an arrow a board draws down from a card and across to the card below it: its height, and where
    it runs from and to, from the middle of the card it leaves to the middle of the card it reaches."""
    by_id = {card.id: card.box for card in cards.values()}
    start, end = by_id[arrow.from_id], by_id[arrow.to_id]
    height = start.y + start.h / 2 + arrow.bends[1]
    ends = sorted((start.x + start.w / 2, end.x + end.w / 2))
    return (height, ends[0], ends[1])


with description("a class model whose cards hang one under another on a Claude whiteboard") as self:
    with before.all:
        self.board = Whiteboard.from_text(WhiteboardCleanEngineeringModel().render(credentials_class_model()))
        self.cards = cards_of(self.board)
        self.arrows = {(element.from_id, element.to_id): element for element in self.board.elements if isinstance(element, Arrow)}

    # A board ends an arrow at the middle of a card's side, so a straight line needs the two middles in line.
    with it("should stand a card in line under the one card above it that holds it"):
        reset, sent = self.cards["PasswordReset"].box, self.cards["TemporaryPassword"].box
        expect(sent.x + sent.w / 2).to(equal(reset.x + reset.w / 2))

    with it("should draw the arrow between them straight, with no bends"):
        arrow = self.arrows[(self.cards["PasswordReset"].id, self.cards["TemporaryPassword"].id)]
        expect((arrow.from_side, arrow.to_side, arrow.bends)).to(equal(("bottom", "top", None)))

    # Arrows leaving one side of a card start by its middle, so two whose level legs ran at one height the same way
    # would be drawn one over the other.
    with it("should give each arrow leaving one side of a card a level leg no other runs along"):
        legs = [level_leg(self.cards, arrow) for (start, _end), arrow in self.arrows.items() if start == self.cards["Credentials"].id and arrow.bends]
        overlapping = [(first, second) for index, first in enumerate(legs) for second in legs[index + 1:] if first[0] == second[0] and min(first[2], second[2]) > max(first[1], second[1])]
        expect(overlapping).to(equal([]))


def placed_card(name: str, box: tuple) -> DiagramClass:
    """A card a person left at box."""
    card = DiagramClass(name=name)
    card.cell_id = name
    card.geometry = Box(*box)
    return card


def drawn_leg(arrow: DiagramArrow, start: Box, end: Box) -> tuple:
    """The level leg a board draws for an arrow that goes down from one card, across, and down into the next: a board
    starts it at the middle of the card it leaves and ends it over the middle of the card it reaches, at the height
    its bends give."""
    bends = arrow.bends_from_middles(start, end)
    ends = sorted((start.center[0], end.center[0]))
    return (start.center[1] + bends[1], ends[0], ends[1])


with description("arrows routed for a board from one side of a card a person placed") as self:
    with before.all:
        self.cards = {card.cell_id: card for card in (
            placed_card("Credentials", (430, 140, 580, 860)),
            placed_card("Token", (50, 1150, 220, 170)),
            placed_card("Validation", (410, 1150, 500, 400)),
            placed_card("PasswordReset", (1070, 1150, 320, 280)),
        )}
        self.arrows = [DiagramArrow("Credentials", name, "composition") for name in ("Token", "Validation", "PasswordReset")]
        BoardArrowRouter(list(self.cards.values()), self.arrows).route()
        self.legs = [drawn_leg(arrow, self.cards[arrow.source].geometry, self.cards[arrow.target].geometry) for arrow in self.arrows]

    # A board starts every arrow leaving one side near its middle, so two level legs at one height, both running from
    # the middle the same way, are drawn one over the other.
    with it("should give each arrow a level leg no other runs along as the board draws it"):
        overlapping = [(first, second) for index, first in enumerate(self.legs) for second in self.legs[index + 1:] if first[0] == second[0] and min(first[2], second[2]) > max(first[1], second[1])]
        expect(overlapping).to(equal([]))

    with it("should leave the card at a point of its own for each arrow"):
        expect(len({arrow.exit_point for arrow in self.arrows})).to(equal(3))


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
        with it("should refuse the board as another practice's drawing, which a read of code skips"):
            expect(lambda: WhiteboardCleanEngineeringModel().parse(Whiteboard("Empty").save())).to(raise_error(UnreadableBoard, "The board holds no module and no class"))

    with context("that is read from text that is no saved board"):
        with it("should refuse the text as an unreadable source"):
            expect(lambda: WhiteboardCleanEngineeringModel().parse("not a board")).to(raise_error(UnreadableSource))


def _saved_as(name: str, text: str) -> Whiteboard:
    """text saved by a render as the whiteboard file called name, read back."""
    import tempfile
    from cdd_guidance.actions.render.rendered_file import RenderedFile
    from harness.guidance.practice_formats import Rendered
    from harness.markdown.format import Format

    file = Path(tempfile.mkdtemp(prefix="board-title-")) / name
    RenderedFile(file, Format("whiteboard")).save(Rendered(Format("whiteboard"), text))
    return Whiteboard.from_text(file.read_text(encoding="utf-8"))


with description("a Clean Engineering board saved as its file") as self:
    with it("should title a module's class model with its file's name, {module}-model"):
        expect(_saved_as("ordering-model.whiteboard", WhiteboardCleanEngineeringModel().render(orders_class_model())).title).to(equal("ordering-model"))

    with it("should title the modules view with its file's name, modules"):
        modules = CleanEngineeringModel("Shop")
        modules.modules = [_module_card("orders", 1, "Takes orders.", ["Order"], []), _module_card("billing", 2, "Bills orders.", ["Invoice"], ["orders"])]
        expect(_saved_as("modules.whiteboard", WhiteboardCleanEngineeringModel().render(modules)).title).to(equal("modules"))

    with it("should still draw the system's name over the modules view"):
        modules = CleanEngineeringModel("Shop")
        modules.modules = [_module_card("orders", 1, "Takes orders.", ["Order"], [])]
        board = _saved_as("modules.whiteboard", WhiteboardCleanEngineeringModel().render(modules))
        expect([label.text for label in board.labels if label.id == "title"]).to(equal(["Shop - Modules Context"]))
