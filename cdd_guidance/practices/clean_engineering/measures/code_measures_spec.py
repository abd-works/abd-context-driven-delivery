"""The code measures the reader keeps as facts: the tool and limit a project chooses for each measure, the facts a read
of named files leaves on each function, class and module, and the limit rules that read them. The outside tool, lizard,
is stood in for here, at the one place the practice asks a tool; code_measures_heavy_spec.py runs the real ones."""
import tempfile
from pathlib import Path

from expects import be_false, be_none, be_true, contain, equal, expect, have_len, raise_error
from mamba import before, context, description, it

from cdd_guidance.practices.clean_engineering.measures.code_measures import (
    CODE_LINES,
    IMPORT_LOOPS,
    CLASSES_DEPENDED_ON,
    MEASURE_NAMED,
    MODULES_IMPORTED,
    NOT_MEASURED,
    SHIPPED_TOOLS,
    PARAMETERS_TAKEN,
    PATHS_THROUGH,
    READABILITY_SCORE,
    TOTAL_COMPLEXITY,
    UNSHARED_METHOD_GROUPS,
    ChosenTools,
    NoToolChosen,
)
from cdd_guidance.practices.clean_engineering.measures.measuring_tools import TOOLS, MeasuringTool
from cdd_guidance.practices.clean_engineering.rules import BY_SLUG
from cdd_guidance.practices.clean_engineering.rules.code_measure_limits import MEASURE_LIMIT_RULES
from cdd_guidance.practices.clean_engineering.rules.rule_examples import MEASURES_CHOSEN, measured, measured_example_pair, practice_from_files
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
# catalogue imports shop's cart, and shop's package pricing imports catalogue: no folder imports one that imports it,
# yet the module shop and the module catalogue import each other.
_LOOP_THROUGH_A_PACKAGE = {
    **_MODULES_AND_A_PACKAGE,
    "catalogue/book.py": "from shop.cart import Cart\n\n\nclass Book:\n    def price(self, cart: Cart) -> int:\n        return 0\n",
}


class StandInLizard(MeasuringTool):
    """Lizard, stood in for: every function has 14 paths and a readability score of 3, and every class a total
    complexity of 40."""

    name = "lizard"

    def __init__(self) -> None:
        super().__init__()
        self._takes = {
            PATHS_THROUGH.name: lambda measured: 14,
            READABILITY_SCORE.name: lambda measured: 3,
            TOTAL_COMPLEXITY.name: lambda measured: 40,
        }


class MeasuresNothing(MeasuringTool):
    """An outside tool that finds nothing to measure, so only the practice's own reader answers."""

    def value(self, measure, measured):
        return None


class NotInstalled(MeasuringTool):
    """Lizard as it is on a machine that never installed it."""

    name = "lizard"

    def value(self, measure, measured):
        return self._imported("a_measuring_tool_nobody_installed", measure)


_STAND_INS = {"lizard": StandInLizard}
_READER_ALONE = {"lizard": MeasuresNothing}


def _node(fixture, kind: str, name: str):
    return next(found for found in fixture.practice.reading.in_graph.nodes(kind) if found.name == name)


def _kept(fixture, kind: str, name: str, measures: list[str]) -> dict:
    node = _node(fixture, kind, name)
    return {measure: node.get_fact(measure) for measure in measures if node.has_fact(measure)}


def _hits_with(slug: str, kind: str, value) -> list[str]:
    """What the rule finds on Cart's total, or on Cart, once the fact the rule's measure is read from holds value."""
    fixture = practice_from_files({**MEASURES_CHOSEN, "shop/cart.py": _CART})
    node = _node(fixture, kind, "total" if kind == "Operation" else "Cart")
    measure = BY_SLUG[slug].measure
    setattr(node, measure.existing or measure.name, value)
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

        with it("should offer lizard and the practice's own reader, and no other tool"):
            expect(sorted(TOOLS)).to(equal(["lizard", "reader"]))

        with it("should hold no measure of a module's maintainability, which only radon took"):
            expect("maintainability_score" in MEASURE_NAMED).to(be_false)

        with it("should ask no tool for a measure a fact on the node already gives"):
            asked = [self.chosen.supplied_by_a_tool(measure) for measure in (CODE_LINES, PARAMETERS_TAKEN, IMPORT_LOOPS, MODULES_IMPORTED)]
            expect(asked).to(equal([False, False, False, False]))

        with it("should take no measure the shipped table says is not measured in a language"):
            expect(self.chosen.tool_name(UNSHARED_METHOD_GROUPS, "typescript")).to(be_none)

        with it("should hold each measure to its shipped limit"):
            limits = [self.chosen.limit(measure) for measure in (PATHS_THROUGH, READABILITY_SCORE, CODE_LINES, PARAMETERS_TAKEN, TOTAL_COMPLEXITY)]
            expect(limits).to(equal([10, 15, 50, 3, 100]))

        with it("should hold a measure kept for information to no limit"):
            expect(self.chosen.limit(CLASSES_DEPENDED_ON)).to(be_none)

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

        with it("should read a module's import loops and the modules it imports from the facts every read keeps"):
            shop = _node(self.fixture, "Module", "shop")
            expect([IMPORT_LOOPS.value_on(shop), MODULES_IMPORTED.value_on(shop)]).to(equal([0, 0]))

        with it("should keep no measure the project says is not measured"):
            expect(_node(self.fixture, "Module", "shop").has_fact("copied_code_blocks")).to(be_false)

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
            expect(hits).to(contain(contain("'sonar'", "lizard, reader")))

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

    with context("in a project that sets a limit of its own"):
        with it("should hold the measure to the project's limit"):
            fixture = practice_from_files({".context/config.json": '{"code_measures": {"limits": {"paths_through": 20}}}', "shop/cart.py": _CART})
            _node(fixture, "Operation", "total").paths_through = 14
            expect(fixture.hits(BY_SLUG["limit-paths-through-a-function"])).to(equal([]))

    with context("on the measures the practice's own reader takes, with its failing and its repaired example"):
        with it("should report a class with more methods than the limit, and pass the repaired one"):
            measured_example_pair("limit-class-methods", _READER_ALONE).check()

        with it("should report a class with a group of methods that share no data with the rest, and pass the repaired one"):
            measured_example_pair("keep-class-methods-sharing-data", _READER_ALONE).check()
