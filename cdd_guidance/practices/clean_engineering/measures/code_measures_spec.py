"""The code measures the reader keeps as facts: the tool and limit a project chooses for each measure, the facts a read
of named files leaves on each function, class and module, and the limit rules that read them. The outside tool, lizard,
is stood in for here, at the one place the practice asks a tool; code_measures_heavy_spec.py runs the real ones."""
import tempfile
from pathlib import Path

from expects import be_false, be_none, be_true, contain, equal, expect, have_len, raise_error
from mamba import before, context, description, it

from cdd_guidance.practices.clean_engineering.measures.code_measures import (
    AVERAGE_CLASS_COMPLEXITY,
    CODE_LINES,
    COPIED_CODE_BLOCKS,
    IMPORT_LOOPS,
    CLASSES_DEPENDED_ON,
    LEAST_MAINTAINABILITY,
    LONGEST_FILE_LINES,
    METHODS_SET_OFF,
    MODULES_IMPORTED,
    MODULES_IMPORTING,
    NOT_MEASURED,
    SHIPPED_TOOLS,
    PARAMETERS_TAKEN,
    PATHS_THROUGH,
    READABILITY_SCORE,
    TOTAL_COMPLEXITY,
    UNSHARED_METHOD_GROUPS,
    ChosenTools,
    MeasureNotTaken,
    NoToolChosen,
)
from cdd_guidance.practices.clean_engineering.measures.measuring_tools import TOOLS, MeasuringTool, MeasuringToolNotInstalled, ToolDoesNotTakeMeasure
from cdd_guidance.practices.clean_engineering.rules import BY_SLUG
from cdd_guidance.practices.clean_engineering.rules.code_measure_limits import MEASURE_LIMIT_RULES
from cdd_guidance.practices.clean_engineering.rules.rule_examples import MEASURES_CHOSEN, measured, measured_example_pair, measured_module_example_pair, practice_from_files
from harness.graph.saved_graph import SavedGraph

_CART = '''class Cart:
    """A customer's cart."""

    def __init__(self, lines: list[int], owner: str) -> None:
        self._lines = lines
        self._owner = owner

    def total(self, discount: int) -> int:
        return sum(self._lines) - discount

    def is_empty(self) -> bool:
        return not self._lines

    def greeting(self) -> str:
        return f"Hello {self._owner}"
'''
# Cart's methods and one more, label, which uses no field of the cart.
_CART_WITH_A_HELPER = _CART + "\n    def label(self, sku: str) -> str:\n        return sku.upper()\n"
_ONE_GROUP_AND_A_HELPER = (
    "class Basket:\n    def __init__(self, lines: list[int]) -> None:\n        self._lines = lines\n\n"
    "    def total(self) -> int:\n        return sum(self._lines)\n\n"
    "    def is_empty(self) -> bool:\n        return not self._lines\n\n"
    "    def label(self, sku: str) -> str:\n        return sku.upper()\n"
)
# Invoice's total calls its own subtotal twice and the methods of two other classes, one of them twice.
_INVOICE = (
    "class Tax:\n    def rate(self) -> int:\n        return 2\n\n    def round(self, cents: int) -> int:\n        return cents\n\n\n"
    "class Discount:\n    def off(self) -> int:\n        return 1\n\n\n"
    "class Invoice:\n    def __init__(self, tax: Tax, discount: Discount) -> None:\n        self._tax = tax\n        self._discount = discount\n\n"
    "    def subtotal(self) -> int:\n        return 10\n\n"
    "    def total(self) -> int:\n        cents = self.subtotal() + self.subtotal() - self._discount.off()\n"
    "        return self._tax.round(cents * self._tax.rate())\n"
)
_CART_IN_JAVASCRIPT = "export class Cart {\n  total(discount) {\n    return discount;\n  }\n}\n"
_CART_SPEC = "class CartExample:\n    def total(self, discount: int) -> int:\n        return discount\n"
_SIX_PARAMETERS = "class Parcel:\n    def send(self, street: str, town: str, postcode: str, country: str, carrier: str, insured: bool) -> str:\n        return street\n"
_FUNCTION_MEASURES = ["paths_through", "readability_score"]
# A module is a folder that owns a module card; any other folder with source is a package inside the module above it.
_CARD = "# {name}\n*{title}* is what {name} keeps.\n\n- **Seam (terms):** {title}\n\n## Constraint\n\nUse {title} only.\n"
_SHOP_CARD = {"shop/.context/module-context.md": _CARD.format(name="shop", title="Cart")}
_CATALOGUE = "class Book:\n    def price(self) -> int:\n        return 0\n"
_PRICE = "from catalogue.book import Book\n\n\nclass Price:\n    def of(self, book: Book) -> int:\n        return book.price()\n"
_ORDER = (
    "from shop.cart import Cart\nfrom shop.pricing.price import Price\n\n\n"
    "class Order:\n    def of(self, cart: Cart, price: Price) -> int:\n        return 0\n"
)
# Three modules: orders imports shop and a package inside it; shop imports catalogue only through its package pricing.
_MODULES_AND_A_PACKAGE = {
    **MEASURES_CHOSEN,
    **_SHOP_CARD,
    "shop/cart.py": _CART,
    "shop/pricing/price.py": _PRICE,
    "catalogue/.context/module-context.md": _CARD.format(name="catalogue", title="Book"),
    "catalogue/book.py": _CATALOGUE,
    "orders/.context/module-context.md": _CARD.format(name="orders", title="Order"),
    "orders/order.py": _ORDER,
}
# shop's cart imports its own package pricing, which is no import of another module, and the child module payments,
# a folder inside shop with a module card of its own, which is.
_A_CHILD_MODULE = {
    **MEASURES_CHOSEN,
    **_SHOP_CARD,
    "shop/cart.py": "from shop.pricing.price import Price\nfrom shop.payments.payment import Payment\n\n\nclass Cart:\n    def total(self, price: Price, payment: Payment) -> int:\n        return 0\n",
    "shop/pricing/price.py": "class Price:\n    def of(self) -> int:\n        return 0\n",
    "shop/payments/.context/module-context.md": _CARD.format(name="payments", title="Payment"),
    "shop/payments/payment.py": "class Payment:\n    def amount(self) -> int:\n        return 0\n",
}
# catalogue imports shop's cart, and shop's package pricing imports catalogue: no folder imports one that imports it,
# yet the module shop and the module catalogue import each other.
_LOOP_THROUGH_A_PACKAGE = {
    **_MODULES_AND_A_PACKAGE,
    "catalogue/book.py": "from shop.cart import Cart\n\n\nclass Book:\n    def price(self, cart: Cart) -> int:\n        return 0\n",
}


# A block of six lines, over fifty tokens, that the shop's cart and the catalogue's book both write.
_COPIED_BLOCK = (
    "        subtotal = sum(line.price * line.quantity for line in lines)\n"
    "        if subtotal > 100:\n"
    "            subtotal = subtotal - subtotal * discount // 100\n"
    "        taxed = subtotal + subtotal * tax_rate // 100\n"
    "        rounded = round(taxed / 5) * 5\n"
    "        return max(rounded, minimum_charge)\n"
)
_TOTAL_SIGNATURE = "    def total(self, lines: list, discount: int, tax_rate: int, minimum_charge: int) -> int:\n"
_COPIED_ACROSS_MODULES = {
    **MEASURES_CHOSEN,
    **_SHOP_CARD,
    "shop/cart.py": "class Cart:\n" + _TOTAL_SIGNATURE + _COPIED_BLOCK,
    "catalogue/.context/module-context.md": _CARD.format(name="catalogue", title="Book"),
    "catalogue/book.py": "class Book:\n    def price(self) -> int:\n        return 0\n\n" + _TOTAL_SIGNATURE + _COPIED_BLOCK,
}


class StandInLizard(MeasuringTool):
    """Lizard, stood in for: every function has 14 paths and a readability score of 3, every class a total complexity
    of 40, and every module's longest file 120 lines of code."""

    name = "lizard"

    def __init__(self) -> None:
        super().__init__()
        self._takes = {
            PATHS_THROUGH.name: lambda measured: 14,
            READABILITY_SCORE.name: lambda measured: 3,
            TOTAL_COMPLEXITY.name: lambda measured: 40,
            LONGEST_FILE_LINES.name: self._longest,
        }

    def _longest(self, measured) -> int:
        measured.keep_file(LONGEST_FILE_LINES, measured.files[0])
        return 120


class StandInRadon(MeasuringTool):
    """Radon, stood in for: every module's least maintainable file has a maintainability index of 65."""

    name = "radon"

    def __init__(self) -> None:
        super().__init__()
        self._takes = {LEAST_MAINTAINABILITY.name: lambda measured: 65}


class MeasuresNothing(MeasuringTool):
    """An outside tool that finds nothing to measure, so only the practice's own reader answers."""

    def value(self, measure, measured):
        return None


class CountingLizard(MeasuringTool):
    """Lizard, stood in for where a class's total complexity is read: one path for each line of the class's own."""

    name = "lizard"

    def __init__(self) -> None:
        super().__init__()
        self._takes = {TOTAL_COMPLEXITY.name: lambda measured: measured.lines[1] - measured.lines[0] + 1}

    def value(self, measure, measured):
        return super().value(measure, measured) if measure.name in self._takes else None


class NotInstalled(MeasuringTool):
    """Lizard as it is on a machine that never installed it."""

    name = "lizard"

    def value(self, measure, measured):
        return self._imported("a_measuring_tool_nobody_installed", measure)


_STAND_INS = {"lizard": StandInLizard, "radon": StandInRadon}
_READER_ALONE = {"lizard": MeasuresNothing, "radon": MeasuresNothing}


def _node(fixture, kind: str, name: str):
    return next(found for found in fixture.practice.reading.in_graph.nodes(kind) if found.name == name)


def _kept(fixture, kind: str, name: str, measures: list[str]) -> dict:
    node = _node(fixture, kind, name)
    return {measure: node.get_fact(measure) for measure in measures if node.has_fact(measure)}


def _module_hits_with(slug: str, facts: dict) -> list[str]:
    """What the rule finds on the module shop once it holds facts, as a read that measured its files leaves them."""
    fixture = practice_from_files({**MEASURES_CHOSEN, **_SHOP_CARD, "shop/cart.py": _CART})
    shop = _node(fixture, "Module", "shop")
    for fact, value in facts.items():
        shop.set_fact(fact, value)
    return fixture.hits(BY_SLUG[slug])


def _hits_with(slug: str, kind: str, value) -> list[str]:
    """What the rule finds on Cart's total, or on Cart, once the fact the rule's measure is read from holds value."""
    fixture = practice_from_files({**MEASURES_CHOSEN, "shop/cart.py": _CART})
    node = _node(fixture, kind, "total" if kind == "Operation" else "Cart")
    fact = BY_SLUG[slug].measure.existing or BY_SLUG[slug].measure.name
    if fact in node.graph_facts:
        setattr(node, fact, value)
    else:
        node.set_fact(fact, value)
    return fixture.hits(BY_SLUG[slug])


with description("the tools a project chooses for its code measures") as self:
    with context("with a code measures section in its config that names nothing"):
        with before.all:
            self.chosen = ChosenTools({})

        with it("should measure the project's code"):
            expect(self.chosen.measures_code).to(be_true)

        with it("should take a Python function's paths with lizard, as shipped"):
            expect(self.chosen.tool_name(PATHS_THROUGH, "python")).to(equal("lizard"))

        with it("should take a class's total complexity with lizard in both languages"):
            chosen = [self.chosen.tool_name(TOTAL_COMPLEXITY, language) for language in ("typescript", "python")]
            expect(chosen).to(equal(["lizard", "lizard"]))

        with it("should offer lizard, radon and the practice's own reader, and no other tool"):
            expect(sorted(TOOLS)).to(equal(["lizard", "radon", "reader"]))

        with it("should take a module's longest file with lizard, and the maintainability index of its files with radon in Python alone"):
            chosen = [self.chosen.tool_name(LONGEST_FILE_LINES, "typescript"), *(self.chosen.tool_name(LEAST_MAINTAINABILITY, language) for language in ("python", "typescript"))]
            expect(chosen).to(equal(["lizard", "radon", None]))

        with it("should count with the practice's own reader the classes a class depends on, the methods one call into it can set off, and a module's average class complexity"):
            chosen = [self.chosen.tool_name(measure, "python") for measure in (CLASSES_DEPENDED_ON, METHODS_SET_OFF, AVERAGE_CLASS_COMPLEXITY)]
            expect(chosen).to(equal(["reader", "reader", "reader"]))

        with it("should ask no tool for a measure a fact on the node already gives"):
            asked = [self.chosen.supplied_by_a_tool(measure) for measure in (CODE_LINES, PARAMETERS_TAKEN, IMPORT_LOOPS, MODULES_IMPORTED)]
            expect(asked).to(equal([False, False, False, False]))

        with it("should take no measure the shipped table says is not measured in a language"):
            expect(self.chosen.tool_name(UNSHARED_METHOD_GROUPS, "typescript")).to(be_none)

        with it("should hold each measure to its shipped limit"):
            limits = [self.chosen.limit(measure) for measure in (PATHS_THROUGH, READABILITY_SCORE, CODE_LINES, PARAMETERS_TAKEN, TOTAL_COMPLEXITY)]
            expect(limits).to(equal([10, 15, 50, 3, 100]))

        with it("should hold a measure kept for information to no limit"):
            expect(self.chosen.limit(MODULES_IMPORTED)).to(be_none)

        with it("should hold a class to the shipped limits on its coupling and on the methods one call into it can set off"):
            expect([self.chosen.limit(measure) for measure in (CLASSES_DEPENDED_ON, METHODS_SET_OFF)]).to(equal([14, 50]))

        with it("should hold a module to the shipped limits on its importers, its longest file, its least maintainable file and its average class complexity"):
            limits = [self.chosen.limit(measure) for measure in (MODULES_IMPORTING, LONGEST_FILE_LINES, LEAST_MAINTAINABILITY, AVERAGE_CLASS_COMPLEXITY)]
            expect(limits).to(equal([40, 800, 20, 15]))

        with it("should count the blocks of code a module repeats from another file with the practice's own reader, in every language, and hold a module to none"):
            chosen = [self.chosen.tool_name(COPIED_CODE_BLOCKS, language) for language in ("python", "typescript", "javascript")]
            expect([*chosen, self.chosen.limit(COPIED_CODE_BLOCKS)]).to(equal(["reader", "reader", "reader", 0]))

        with it("should take in JavaScript each measure lizard gives, as it does in TypeScript"):
            chosen = [self.chosen.tool_name(measure, "javascript") for measure in (PATHS_THROUGH, READABILITY_SCORE, TOTAL_COMPLEXITY)]
            expect(chosen).to(equal(["lizard", "lizard", "lizard"]))

        with it("should choose for JavaScript, for every other measure, what it chooses for TypeScript"):
            differing = [name for name, languages in SHIPPED_TOOLS.items() if languages["javascript"] != languages["typescript"]]
            expect(differing).to(equal([]))

        with it("should refuse code in a language nobody chose a tool for, naming the measure, the language and the config"):
            choose = lambda: self.chosen.tool_name(PATHS_THROUGH, "go")
            expect(choose).to(raise_error(NoToolChosen, contain("'paths_through'", "paths through a function (cyclomatic complexity)", "in go", "config.json")))

        with it("should say, in that refusal, to choose a tool for the measure and the language, record it in the config's code measures, and install it"):
            choose = lambda: self.chosen.tool_name(PATHS_THROUGH, "go")
            expect(choose).to(raise_error(NoToolChosen, contain(
                "Fix: choose a tool that takes 'paths_through' in go",
                '"code_measures": "tools": "paths_through": "go"',
                "and install it",
            )))

    with context("with a section that chooses a tool and a limit of its own"):
        with before.all:
            self.chosen = ChosenTools({"tools": {"paths_through": {"go": "lizard", "python": NOT_MEASURED}}, "limits": {"paths_through": 6}})

        with it("should take the measure in the language it adds"):
            expect(self.chosen.tool_name(PATHS_THROUGH, "go")).to(equal("lizard"))

        with it("should leave out the measure it says is not measured"):
            expect(self.chosen.tool_name(PATHS_THROUGH, "python")).to(be_none)

        with it("should keep the shipped choice it does not name"):
            expect(self.chosen.tool_name(PATHS_THROUGH, "typescript")).to(equal("lizard"))

        with it("should hold the measure to the project's limit"):
            expect(self.chosen.limit(PATHS_THROUGH)).to(equal(6))

    with context("with no code measures section in its config"):
        with it("should not measure the project's code"):
            expect(ChosenTools(None).measures_code).to(be_false)

        with it("should hold no measure to a limit"):
            expect(ChosenTools(None).limit(PATHS_THROUGH)).to(be_none)

    with context("read from a project's top folder"):
        with before.all:
            self.project = Path(tempfile.mkdtemp(prefix="cdd-chosen-tools-"))
            (self.project / ".context").mkdir()
            (self.project / ".context" / "config.json").write_text('{"code_measures": {"limits": {"code_lines": 80}}}', encoding="utf-8")
            (self.project / "src" / "shop").mkdir(parents=True)

        with it("should be the choices of that folder's config"):
            expect(ChosenTools.of_project(self.project).limit(CODE_LINES)).to(equal(80))

        with it("should be no choice for a folder kept inside the project, such as a sample, which is not measured by the project's choices"):
            expect(ChosenTools.of_project(self.project / "src" / "shop").measures_code).to(be_false)


with description("the code measures the reader keeps of the files a read names") as self:
    with context("in a project that chose the shipped tools"):
        with before.all:
            self.fixture = measured(practice_from_files({**MEASURES_CHOSEN, **_SHOP_CARD, "shop/cart.py": _CART, "shop/cart_spec.py": _CART_SPEC}), _STAND_INS)

        with it("should keep on a function each measure its tool took"):
            expect(_kept(self.fixture, "Operation", "total", _FUNCTION_MEASURES)).to(equal({"paths_through": 14, "readability_score": 3}))

        with it("should read a function's lines and parameters from the facts every read keeps, and keep no second fact for them"):
            total = _node(self.fixture, "Operation", "total")
            read = [CODE_LINES.value_on(total), PARAMETERS_TAKEN.value_on(total), total.has_fact("code_lines"), total.has_fact("parameters_taken")]
            expect(read).to(equal([total.get_fact("line_count"), 1, False, False]))

        with it("should keep on a class its total complexity, its methods, the classes it depends on, and its groups of methods sharing no data"):
            kept = _kept(self.fixture, "OoadClass", "Cart", ["total_complexity", "method_count", "classes_depended_on", "unshared_method_groups"])
            expect(kept).to(equal({"total_complexity": 40, "method_count": 4, "classes_depended_on": 0, "unshared_method_groups": 2}))

        with it("should keep on a module the modules that import it"):
            expect(_kept(self.fixture, "Module", "shop", ["modules_importing"])).to(equal({"modules_importing": 0}))

        with it("should keep on a module its longest file's lines and the file, its least maintainable file's index, and its classes' average total complexity"):
            kept = _kept(self.fixture, "Module", "shop", ["longest_file_lines", "longest_file_lines_file", "least_maintainability", "average_class_complexity"])
            expect(kept).to(equal({"longest_file_lines": 120, "longest_file_lines_file": "shop/cart.py", "least_maintainability": 65, "average_class_complexity": 40}))

        with it("should keep on a class the methods one call into it can set off: its own four"):
            expect(_kept(self.fixture, "OoadClass", "Cart", ["methods_set_off"])).to(equal({"methods_set_off": 4}))

        with it("should read a module's import loops and the modules it imports from the facts every read keeps"):
            shop = _node(self.fixture, "Module", "shop")
            expect([IMPORT_LOOPS.value_on(shop), MODULES_IMPORTED.value_on(shop)]).to(equal([0, 0]))

        with it("should keep no measure the project says is not measured"):
            fixture = measured(practice_from_files({
                ".context/config.json": '{"code_measures": {"tools": {"copied_code_blocks": {"python": "not measured"}}}}',
                **_SHOP_CARD, "shop/cart.py": _CART,
            }), _STAND_INS)
            expect(_node(fixture, "Module", "shop").has_fact("copied_code_blocks")).to(be_false)

        with it("should measure no spec"):
            spec_functions = [node for node in self.fixture.practice.reading.in_graph.nodes("Operation") if node.source.file == "shop/cart_spec.py"]
            expect([node.has_fact("paths_through") for node in spec_functions]).to(equal([False]))

    with context("with modules, each a folder with its module card, and a package inside one of them"):
        with before.all:
            self.fixture = measured(practice_from_files(_MODULES_AND_A_PACKAGE), _READER_ALONE)

        with it("should count as the modules a module imports those its packages import"):
            expect(MODULES_IMPORTED.value_on(_node(self.fixture, "Module", "shop"))).to(equal(1))

        with it("should count a module imported through a package inside it once, as that module"):
            expect(_kept(self.fixture, "Module", "shop", ["modules_importing"])).to(equal({"modules_importing": 1}))

        with it("should count as the modules importing a module the module that holds the package importing it"):
            expect(_kept(self.fixture, "Module", "catalogue", ["modules_importing"])).to(equal({"modules_importing": 1}))

        with it("should take no module measure on a package, which is part of its module"):
            pricing = _node(self.fixture, "Package", "pricing")
            taken = [pricing.has_fact("modules_importing"), MODULES_IMPORTED.value_on(pricing), IMPORT_LOOPS.value_on(pricing)]
            expect(taken).to(equal([False, None, None]))

    with context("with a child module, a folder with a module card of its own inside another module"):
        with before.all:
            self.fixture = measured(practice_from_files(_A_CHILD_MODULE), _READER_ALONE)

        with it("should count the child module among the modules its parent imports, and not the parent's own package"):
            expect(_node(self.fixture, "Module", "shop").get_fact("imported_modules")).to(equal(["shop/payments"]))

        with it("should count the parent among the modules that import the child module"):
            expect(_kept(self.fixture, "Module", "payments", ["modules_importing"])).to(equal({"modules_importing": 1}))

    with context("with two modules that import each other only through a package inside one of them"):
        with it("should count the loop on each module"):
            fixture = measured(practice_from_files(_LOOP_THROUGH_A_PACKAGE), _READER_ALONE)
            expect([IMPORT_LOOPS.value_on(_node(fixture, "Module", name)) for name in ("shop", "catalogue")]).to(equal([1, 1]))

    with context("in a project whose config chooses no tools"):
        with it("should keep no measure"):
            fixture = measured(practice_from_files({"shop/cart.py": _CART}), _STAND_INS)
            expect(_kept(fixture, "Operation", "total", _FUNCTION_MEASURES)).to(equal({}))

    with context("in a read of the whole working copy, which names no file"):
        with it("should keep no measure, so no load of the graph waits on a measuring tool"):
            fixture = practice_from_files({**MEASURES_CHOSEN, "shop/cart.py": _CART})
            fixture.practice.reading.measuring_tools.update(_STAND_INS)
            expect(_kept(fixture, "Operation", "total", _FUNCTION_MEASURES)).to(equal({}))

    with context("with a chosen tool that is not installed"):
        with before.all:
            self.fixture = measured(practice_from_files({**MEASURES_CHOSEN, "shop/cart.py": _CART}), {"lizard": NotInstalled})
            self.hits = self.fixture.hits(BY_SLUG["limit-paths-through-a-function"])

        with it("should have the measure's rule report which tool, which measure, and how to install it"):
            expect(self.hits).to(contain(contain("'lizard'", "'paths_through'", "is not installed", 'pip install -e ".[measures]"')))

        with it("should say, as the fix, to install the tool the config names, with the command"):
            expect(self.hits).to(contain(contain("Fix: install lizard, the tool .context/config.json names for this measure, with: pip install")))

        with it("should report it once for the file, not for each of its functions"):
            expect(self.hits).to(have_len(1))

        with it("should keep no measure the tool would have taken"):
            expect(_kept(self.fixture, "Operation", "total", ["paths_through"])).to(equal({}))

    with context("with code in JavaScript"):
        with before.all:
            self.fixture = measured(practice_from_files({**MEASURES_CHOSEN, "shop/cart.js": _CART_IN_JAVASCRIPT}), _STAND_INS)

        with it("should keep on a function each measure lizard took"):
            expect(_kept(self.fixture, "Operation", "total", _FUNCTION_MEASURES)).to(equal({"paths_through": 14, "readability_score": 3}))

        with it("should report no measure as one no tool is chosen for"):
            reported = [hit for rule in MEASURE_LIMIT_RULES for hit in self.fixture.hits(rule) if "No tool is chosen" in hit]
            expect(reported).to(equal([]))

    with context("with a class one of whose methods uses no field of the class"):
        with before.all:
            self.fixture = measured(practice_from_files({**MEASURES_CHOSEN, "shop/cart.py": _CART_WITH_A_HELPER, "shop/basket.py": _ONE_GROUP_AND_A_HELPER}), _READER_ALONE)

        with it("should leave that method out of the groups of methods sharing no data"):
            expect(_kept(self.fixture, "OoadClass", "Cart", ["unshared_method_groups"])).to(equal({"unshared_method_groups": 2}))

        with it("should not report a class whose other methods share their data"):
            expect([hit for hit in self.fixture.hits(BY_SLUG["keep-class-methods-sharing-data"]) if "'Basket'" in hit]).to(equal([]))

    with context("with a tool chosen for a measure it does not take"):
        with it("should have the measure's rule report what the tool does take"):
            fixture = practice_from_files({".context/config.json": '{"code_measures": {"tools": {"readability_score": {"python": "reader"}}}}', "shop/cart.py": _CART})
            hits = measured(fixture, _STAND_INS).hits(BY_SLUG["keep-functions-readable"])
            expect(hits).to(contain(contain("'reader'", "'readability_score'", "modules_importing")))

    with context("with a tool chosen that nobody has written"):
        with it("should have the measure's rule report the tools there are"):
            fixture = practice_from_files({".context/config.json": '{"code_measures": {"tools": {"readability_score": {"python": "sonar"}}}}', "shop/cart.py": _CART})
            hits = measured(fixture, _STAND_INS).hits(BY_SLUG["keep-functions-readable"])
            expect(hits).to(contain(contain("'sonar'", "lizard, radon, reader")))

    with context("by the refresh of the files a validate names"):
        with before.all:
            self.fixture = practice_from_files({**MEASURES_CHOSEN, "shop/cart.py": _CART})
            reading = self.fixture.practice.reading
            reading.measuring_tools.update(_STAND_INS)
            self.checked = Path(tempfile.mkdtemp(prefix="cdd-checked-")) / "checked.json"
            reading.graph.reads.refreshed(["shop/cart.py"], self.checked)

        with it("should keep each function's measures on the node the refresh read"):
            expect(_kept(self.fixture, "Operation", "total", ["paths_through"])).to(equal({"paths_through": 14}))

        with it("should have the limit rule report the function in the same check as every other rule"):
            violations = [violation.rule for violation in SavedGraph.from_file(self.checked).violations(["clean_engineering"])]
            expect(violations).to(contain("limit-paths-through-a-function"))

        with it("should save each measure with the nodes the validate reads back"):
            saved = SavedGraph.from_file(self.checked).practices["clean_engineering"]
            total = next(node for node in saved.nodes if node.name == "total")
            expect(total.facts["paths_through"]).to(equal(14))


with description("the methods one call into a class can set off") as self:
    with context("with a class whose method calls the methods of other classes"):
        with before.all:
            self.fixture = measured(practice_from_files({**MEASURES_CHOSEN, "shop/invoice.py": _INVOICE}), _READER_ALONE)

        with it("should count the class's own three methods and the three methods of other classes they call, once each"):
            expect(_kept(self.fixture, "OoadClass", "Invoice", ["methods_set_off"])).to(equal({"methods_set_off": 6}))

        with it("should count the class's coupling: the other classes it depends on"):
            expect(_kept(self.fixture, "OoadClass", "Invoice", ["classes_depended_on"])).to(equal({"classes_depended_on": 2}))


with description("a module's average class complexity") as self:
    with context("with two classes the tool measured and a package inside the module"):
        with it("should average the total complexity of the classes of its files and packages"):
            fixture = measured(practice_from_files(_MODULES_AND_A_PACKAGE), {"lizard": CountingLizard, "radon": MeasuresNothing})
            totals = [_node(fixture, "OoadClass", name).get_fact("total_complexity") for name in ("Cart", "Price")]
            expect(_kept(fixture, "Module", "shop", ["average_class_complexity"])).to(equal({"average_class_complexity": round(sum(totals) / 2, 2)}))


with description("the blocks of code a module repeats from another file") as self:
    with context("with a block of six lines, over fifty tokens, written in a file of each of two modules"):
        with before.all:
            self.fixture = measured(practice_from_files(_COPIED_ACROSS_MODULES), _READER_ALONE)

        with it("should count the block once on each module"):
            counted = [_kept(self.fixture, "Module", name, ["copied_code_blocks"]) for name in ("shop", "catalogue")]
            expect(counted).to(equal([{"copied_code_blocks": 1}, {"copied_code_blocks": 1}]))

        with it("should keep on the module where the block is and where its copy is"):
            expect(_node(self.fixture, "Module", "shop").get_fact("copied_code_blocks_file")).to(equal("shop/cart.py lines 2-8, also in catalogue/book.py lines 5-11"))

    with context("with the block written once, and called from the other module"):
        with it("should count no block"):
            fixture = measured(practice_from_files({**_COPIED_ACROSS_MODULES, "catalogue/book.py": "class Book:\n    def price(self) -> int:\n        return 0\n"}), _READER_ALONE)
            expect(_kept(fixture, "Module", "shop", ["copied_code_blocks"])).to(equal({"copied_code_blocks": 0}))

    with context("with a copy shorter than five lines"):
        with it("should count no block"):
            short = {**_COPIED_ACROSS_MODULES, "catalogue/book.py": "class Book:\n" + _TOTAL_SIGNATURE + "".join(_COPIED_BLOCK.splitlines(keepends=True)[:3]) + "        return 0\n"}
            expect(_kept(measured(practice_from_files(short), _READER_ALONE), "Module", "catalogue", ["copied_code_blocks"])).to(equal({"copied_code_blocks": 0}))


with description("a measuring tool asked for a measure") as self:
    with context("that it does not take"):
        with it("should refuse, naming the tool, the measure and the measures it takes"):
            expect(lambda: StandInLizard().value(CODE_LINES, None)).to(
                raise_error(ToolDoesNotTakeMeasure, contain("'lizard'", "'code_lines'", "it takes longest_file_lines, paths_through, readability_score, total_complexity"))
            )

        with it("should be a measure not taken, which the read keeps on the node instead of stopping"):
            expect(lambda: StandInLizard().value(CODE_LINES, None)).to(raise_error(MeasureNotTaken))

    with context("that is not installed"):
        with it("should refuse, naming the tool, the measure and how to install it"):
            expect(lambda: NotInstalled().value(PATHS_THROUGH, None)).to(
                raise_error(MeasuringToolNotInstalled, contain("'lizard'", "'paths_through'", "pip install"))
            )


with description("a limit on a code measure") as self:
    with context("on a function whose measure is past its limit"):
        with it("should report more paths through it than the limit, naming the measure in plain words"):
            expect(_hits_with("limit-paths-through-a-function", "Operation", 11)).to(contain(contain("Function 'total' has 11 paths through it (cyclomatic complexity), over the limit of 10.")))

        with it("should report a readability score over the limit"):
            expect(_hits_with("keep-functions-readable", "Operation", 16)).to(contain(contain("a readability score of 16 (cognitive complexity; higher is harder to read), over the limit of 15.")))

        with it("should report more lines than the limit, read from the lines every read keeps, with no tool asked"):
            expect(_hits_with("limit-function-lines", "Operation", 51)).to(contain(contain("has 51 lines, over the limit of 50.")))

        with it("should report more parameters than the limit, counted from its parameter nodes, with no tool asked"):
            fixture = practice_from_files({**MEASURES_CHOSEN, "parcels/parcel.py": _SIX_PARAMETERS})
            expect(fixture.hits(BY_SLUG["limit-operation-parameters"])).to(equal(["Operation 'send' takes 6 parameters (maximum 3, excluding self)."]))

        with it("should hold its parameters to the limit the project sets"):
            fixture = practice_from_files({".context/config.json": '{"code_measures": {"limits": {"parameters_taken": 6}}}', "parcels/parcel.py": _SIX_PARAMETERS})
            expect(fixture.hits(BY_SLUG["limit-operation-parameters"])).to(equal([]))

    with context("on a function whose measure is at its limit"):
        with it("should report nothing"):
            expect(_hits_with("limit-paths-through-a-function", "Operation", 10)).to(equal([]))

    with context("on a function no read measured"):
        with it("should report nothing"):
            fixture = practice_from_files({**MEASURES_CHOSEN, "shop/cart.py": _CART})
            expect(fixture.hits(BY_SLUG["limit-paths-through-a-function"])).to(equal([]))

    with context("in a project whose config has no code measures section"):
        with it("should still hold an operation's parameters to the shipped limit, as it did before code was measured"):
            fixture = practice_from_files({"parcels/parcel.py": _SIX_PARAMETERS})
            expect(fixture.hits(BY_SLUG["limit-operation-parameters"])).to(equal(["Operation 'send' takes 6 parameters (maximum 3, excluding self)."]))

        with it("should report no class for its methods, which the reader counts in every project"):
            fixture = practice_from_files({"shop/cart.py": _CART})
            _node(fixture, "OoadClass", "Cart").method_count = 31
            expect(fixture.hits(BY_SLUG["limit-class-methods"])).to(equal([]))

    with context("on a class whose measure is past its limit"):
        with it("should report a total complexity over the limit"):
            expect(_hits_with("limit-class-complexity", "OoadClass", 101)).to(contain(contain("Class 'Cart' has a total complexity of 101 (the paths through all its methods, added up), over the limit of 100.")))

        with it("should report more methods than the limit"):
            expect(_hits_with("limit-class-methods", "OoadClass", 31)).to(contain(contain("Class 'Cart' has 31 methods, over the limit of 30.")))

        with it("should report more classes it depends on than the limit"):
            expect(_hits_with("limit-class-coupling", "OoadClass", 15)).to(contain(contain("Class 'Cart' has 15 classes it depends on (coupling between objects), over the limit of 14.")))

        with it("should report more methods one call into it can set off than the limit"):
            expect(_hits_with("limit-class-response", "OoadClass", 51)).to(contain(contain("Class 'Cart' has 51 methods one call into it can set off (response for a class), over the limit of 50.")))

    with context("on a class whose measure is at its limit"):
        with it("should report neither its coupling nor the methods one call into it can set off"):
            expect([_hits_with("limit-class-coupling", "OoadClass", 14), _hits_with("limit-class-response", "OoadClass", 50)]).to(equal([[], []]))

    with context("on a module whose measure is past its limit"):
        with it("should report a longest file over the limit, naming the file"):
            hits = _module_hits_with("limit-module-file-lines", {"longest_file_lines": 801, "longest_file_lines_file": "shop/cart.py"})
            expect(hits).to(contain(contain("Module 'shop' has a file of 801 lines of code, in shop/cart.py, over the limit of 800.")))

        with it("should report a file whose maintainability index is under the limit, which is the least it may be"):
            hits = _module_hits_with("keep-module-files-maintainable", {"least_maintainability": 19.5, "least_maintainability_file": "shop/cart.py"})
            expect(hits).to(contain(contain("Module 'shop' has a file with a maintainability index of 19.5 (0 to 100; higher is easier to change), in shop/cart.py, under the limit of 20.")))

        with it("should report an average class complexity over the limit"):
            hits = _module_hits_with("limit-average-class-complexity", {"average_class_complexity": 15.5})
            expect(hits).to(contain(contain("Module 'shop' has classes whose total complexity averages 15.5 (the paths through all a class's methods, added up), over the limit of 15.")))

        with it("should report a copied block over the limit, naming where it is and where its copy is"):
            hits = _module_hits_with("limit-copied-code-blocks", {"copied_code_blocks": 1, "copied_code_blocks_file": "shop/cart.py lines 2-8, also in catalogue/book.py lines 5-11"})
            expect(hits).to(contain(contain("Module 'shop' has 1 blocks of code repeated from another file, in shop/cart.py lines 2-8, also in catalogue/book.py lines 5-11, over the limit of 0.")))

        with it("should report more modules importing it than the limit"):
            expect(_module_hits_with("limit-modules-importing", {"modules_importing": 41})).to(contain(contain("Module 'shop' has 41 modules that import it, over the limit of 40.")))

    with context("on a module whose measure is at its limit"):
        with it("should report no file at its longest lines"):
            expect(_module_hits_with("limit-module-file-lines", {"longest_file_lines": 800})).to(equal([]))

        with it("should report no file at its least maintainability"):
            expect(_module_hits_with("keep-module-files-maintainable", {"least_maintainability": 20})).to(equal([]))

        with it("should report no module at its average class complexity"):
            expect(_module_hits_with("limit-average-class-complexity", {"average_class_complexity": 15})).to(equal([]))

        with it("should report no module at the modules importing it"):
            expect(_module_hits_with("limit-modules-importing", {"modules_importing": 40})).to(equal([]))

    with context("in a project that sets a limit of its own"):
        with it("should hold the measure to the project's limit"):
            fixture = practice_from_files({".context/config.json": '{"code_measures": {"limits": {"paths_through": 20}}}', "shop/cart.py": _CART})
            _node(fixture, "Operation", "total").paths_through = 14
            expect(fixture.hits(BY_SLUG["limit-paths-through-a-function"])).to(equal([]))

    with context("on the measures the practice's own reader takes, with its failing and its repaired example"):
        # Each pair reads and measures two projects, so they are read once, before the examples, which only check them.
        with before.all:
            self.method_count_pair = measured_example_pair("limit-class-methods", _READER_ALONE)
            self.sharing_data_pair = measured_example_pair("keep-class-methods-sharing-data", _READER_ALONE)
            self.coupling_pair = measured_example_pair("limit-class-coupling", _READER_ALONE)
            self.response_pair = measured_example_pair("limit-class-response", _READER_ALONE)
            self.importing_pair = measured_module_example_pair("limit-modules-importing", _READER_ALONE)
            self.copied_blocks_pair = measured_module_example_pair("limit-copied-code-blocks", _READER_ALONE)

        with it("should report a class with more methods than the limit, and pass the repaired one"):
            self.method_count_pair.check()

        with it("should report a class with a group of methods that share no data with the rest, and pass the repaired one"):
            self.sharing_data_pair.check()

        with it("should report a class that depends on more classes than the limit, and pass the repaired one"):
            self.coupling_pair.check()

        with it("should report a class one call into which can set off more methods than the limit, and pass the repaired one"):
            self.response_pair.check()

        with it("should report a module more modules import than its project's limit, and pass the repaired one"):
            self.importing_pair.check()

        with it("should report a module that repeats a block of code from another module's file, and pass the repaired one"):
            self.copied_blocks_pair.check()
